
import hmac
import json
from datetime import datetime, timedelta, timezone
from email.utils import formatdate

import frappe
from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response


# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------

SETTINGS = {
    # eSSL machine serial number
    "essl_allowed_serials": ["RAG8262800862"],

    # Empty = allow any source IP.
    # Add machine location's public IP only if it is stable.
    "essl_allowed_ips": [13.200.157.65],

    # Live Frappe Cloud domain
    "essl_allowed_hosts": ["arctic.m.frappe.cloud"],

    # Direct device connection: API authentication OFF
    # Do not put real API credentials in source code.
    "essl_api_key": "70aa0cc1a19de6d",
    "essl_api_secret": "654bfaf3ff4b364",
    "essl_require_api_auth": False,

    # Preserve old working IN/OUT logic
    "essl_use_device_status": False,

    # Debug logging
    "essl_debug": False,
}

LOGGER_NAME = "essl_adms"

IN_STATUS = {"0", "4"}
OUT_STATUS = {"1", "5"}

# IMPORTANT:
# Old local code's working 30-minute correction.
# Do not change this value.
DATE_HEADER_SHIFT_MINUTES = 30


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

def _cfg(key, default=None):
    value = frappe.conf.get(key)

    if value is None:
        value = SETTINGS.get(key, default)

    return value


def _log():
    return frappe.logger(LOGGER_NAME)


def _conf_set(key, upper=False):
    value = _cfg(key) or []

    if isinstance(value, str):
        value = value.split(",")

    result = {
        str(v).strip()
        for v in value
        if str(v).strip()
    }

    return {v.upper() for v in result} if upper else {
        v.lower() for v in result
    }


# ---------------------------------------------------------------------------
# DEVICE SECURITY
# ---------------------------------------------------------------------------

def _client_ip(request):
    forwarded = request.headers.get("X-Forwarded-For", "")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return (
        request.headers.get("X-Real-IP")
        or request.remote_addr
        or ""
    )


def _api_auth_ok(request):
    key = str(_cfg("essl_api_key") or "")
    secret = str(_cfg("essl_api_secret") or "")

    header = request.headers.get("Authorization", "")

    if not key or not secret:
        return False

    if not header.lower().startswith("token "):
        return False

    sent = header[6:].strip()
    expected = f"{key}:{secret}"

    return hmac.compare_digest(sent, expected)


def check_access(request, serial_number):
    """Return None if request is allowed, otherwise rejection reason."""

    serials = _conf_set(
        "essl_allowed_serials",
        upper=True,
    )

    if not serial_number or serial_number.upper() not in serials:
        return f"Unknown device ID: {serial_number}"

    ips = _conf_set("essl_allowed_ips")

    if ips and _client_ip(request).lower() not in ips:
        return f"IP not allowed: {_client_ip(request)}"

    hosts = _conf_set("essl_allowed_hosts")

    request_host = (request.host or "").split(":")[0].lower()

    if hosts and request_host not in hosts:
        return f"Host not allowed: {request.host}"

    if _cfg("essl_require_api_auth") and not _api_auth_ok(request):
        return "Invalid API authentication"

    return None


# ---------------------------------------------------------------------------
# IN / OUT LOGIC
# ---------------------------------------------------------------------------

def get_log_type(employee, punch_time, status):

    if _cfg("essl_use_device_status"):

        if status in OUT_STATUS:
            return "OUT"

        if status in IN_STATUS:
            return "IN"

    day_start = punch_time.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    last = frappe.get_all(
        "Employee Checkin",
        filters=[
            ["employee", "=", employee],
            ["time", ">=", day_start],
            ["time", "<", punch_time],
        ],
        fields=["log_type"],
        order_by="time desc",
        limit=1,
    )

    if last and last[0].log_type == "IN":
        return "OUT"

    return "IN"


# ---------------------------------------------------------------------------
# ATTLOG PARSING
# ---------------------------------------------------------------------------

def parse_attlog(body_data):

    rows = []

    for line in body_data.splitlines():

        if not line.strip():
            continue

        fields = line.strip().split()

        if len(fields) < 3:
            continue

        try:
            punch_time = datetime.strptime(
                fields[1] + " " + fields[2],
                "%Y-%m-%d %H:%M:%S",
            )

        except ValueError:

            _log().warning(
                f"Invalid attendance timestamp: {line}"
            )

            continue

        status = fields[3] if len(fields) > 3 else ""

        rows.append(
            (punch_time, fields[0], status)
        )

    rows.sort(key=lambda row: row[0])

    return rows


# ---------------------------------------------------------------------------
# SAVE ATTENDANCE
# ---------------------------------------------------------------------------

def save_attlog(rows, serial_number):

    saved_count = 0

    employee_cache = {}

    for punch_time, user_id, status in rows:

        if user_id not in employee_cache:

            employee_cache[user_id] = frappe.db.get_value(
                "Employee",
                {
                    "attendance_device_id": user_id,
                    "status": "Active",
                },
                "name",
            )

        employee = employee_cache[user_id]

        if not employee:

            _log().warning(
                f"No active employee mapped for device ID {user_id}"
            )

            continue

        # Preserve old code's duplicate check.
        # This also preserves original device punch timestamp.
        duplicate = frappe.db.exists(
            "Employee Checkin",
            {
                "employee": employee,
                "device_punch_time": punch_time,
            },
        )

        if duplicate:
            continue

        try:

            checkin = frappe.get_doc(
                {
                    "doctype": "Employee Checkin",
                    "employee": employee,
                    "time": punch_time,
                    "device_punch_time": punch_time,

                    # Preserve old local code's device ID mapping.
                    "device_id": user_id,

                    "log_type": get_log_type(
                        employee,
                        punch_time,
                        status,
                    ),
                }
            )

            checkin.insert(ignore_permissions=True)

            frappe.db.commit()

            saved_count += 1

            frappe.publish_realtime(
                "list_update",
                {
                    "doctype": "Employee Checkin",
                    "name": checkin.name,
                },
                doctype="Employee Checkin",
            )

        except Exception:

            frappe.db.rollback()

            frappe.log_error(
                frappe.get_traceback(),
                "eSSL Employee Checkin Import Failed",
            )

    return saved_count


# ---------------------------------------------------------------------------
# ESSL ADMS RENDERER
# ---------------------------------------------------------------------------

class ESSLADMSRenderer(BaseRenderer):

    def can_render(self):

        return (self.path or "").lower() in (
            "iclock/cdata.aspx",
            "iclock/getrequest.aspx",
        )

    def render(self):

        request = frappe.local.request

        path = request.path.rstrip("/").lower()

        serial_number = (
            request.args.get("SN") or ""
        ).strip()

        # 1. DEVICE SECURITY

        reason = check_access(
            request,
            serial_number,
        )

        if reason:

            _log().warning(
                f"Rejected request SN='{serial_number}' "
                f"IP={_client_ip(request)}: {reason}"
            )

            return Response(
                "Forbidden",
                status=403,
                content_type="text/plain",
            )

        body_data = request.get_data(as_text=True)

        # 2. DEBUG LOGGING

        if _cfg("essl_debug"):

            _log().info(
                json.dumps(
                    {
                        "method": request.method,
                        "path": path,
                        "args": request.args.to_dict(),
                        "body": body_data[:10000],
                    },
                    ensure_ascii=False,
                )
            )

        # 3. ATTENDANCE UPLOAD

        if (
            request.method == "POST"
            and path.endswith("cdata.aspx")
            and request.args.get("table", "").upper() == "ATTLOG"
        ):

            rows = parse_attlog(body_data)

            saved = save_attlog(
                rows,
                serial_number,
            )

            _log().info(
                f"eSSL ATTLOG "
                f"SN={serial_number} "
                f"received={len(rows)} "
                f"saved={saved}"
            )

        # 4. DEVICE OPTION HANDSHAKE

        if (
            request.method == "GET"
            and path.endswith("cdata.aspx")
            and request.args.get("options") == "all"
        ):

            body = (
                f"GET OPTION FROM: {serial_number}\n"
                "ErrorDelay=60\n"
                "Delay=30\n"
                "TransTimes=00:00;14:05\n"
                "TransInterval=1\n"
                "TransFlag=AttLog\tOpLog\tEnrollUser\tChgUser\tEnrollFACE\tChgFACE\n"
                "Realtime=1\n"
                "Encrypt=None\n"
                "TimeZone=5\n"
                "Timeout=60\n"
                "SyncTime=0\n"
                "ServerVer=1.0\n"
                "ATTLOGStamp=0\n"
                "OPERLOGStamp=0\n"
                "OK\n"
            )

        else:

            body = "OK"

        # 5. PRESERVE OLD 30-MINUTE DATE HEADER CORRECTION
        #
        # This is intentionally fixed at +30 minutes.
        # Site Config cannot silently override it.

        shifted = (
            datetime.now(timezone.utc)
            + timedelta(minutes=DATE_HEADER_SHIFT_MINUTES)
        )

        return Response(
            body,
            status=200,
            content_type="text/plain",
            headers={
                "X-ESSL-Renderer": "active",
                "Date": formatdate(
                    shifted.timestamp(),
                    usegmt=True,
                ),
            },
        )
