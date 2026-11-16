import frappe
import json
from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response
from datetime import datetime, timedelta, timezone
from email.utils import formatdate

# False = IN/OUT alternate aagum
# True = machine anupura status use pannum (0/4 = IN, 1/5 = OUT)
USE_DEVICE_STATUS = False
IN_STATUS = {"0", "4"}
OUT_STATUS = {"1", "5"}

# Machine timezone la 30 min kuraiya eduthukkudhu
DATE_HEADER_SHIFT_MINUTES = 30


def get_log_type(employee, punch_time, status):
    if USE_DEVICE_STATUS:
        if status in OUT_STATUS:
            return "OUT"
        if status in IN_STATUS:
            return "IN"

    day_start = punch_time.replace(
        hour=0, minute=0, second=0, microsecond=0
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


class ESSLADMSRenderer(BaseRenderer):

    def can_render(self):
        return self.path in (
            "iclock/cdata.aspx",
            "iclock/getrequest.aspx",
        )

    def render(self):
        request = frappe.local.request
        path = request.path.rstrip("/")
        body_data = request.get_data(as_text=True)

        details = {
            "method": request.method,
            "path": path,
            "args": request.args.to_dict(),
            "content_type": request.content_type,
            "body": body_data[:10000],
        }

        frappe.logger("essl_adms").info(
            json.dumps(details, ensure_ascii=False)
        )

        if (
            request.method == "POST"
            and path.endswith("cdata.aspx")
            and request.args.get("table", "").upper() == "ATTLOG"
        ):
            saved_count = 0
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
                    frappe.logger("essl_adms").warning(
                        f"Invalid attendance timestamp: {line}"
                    )
                    continue

                status = fields[3] if len(fields) > 3 else ""
                rows.append((punch_time, fields[0], status))

            rows.sort(key=lambda r: r[0])

            for punch_time, user_id, status in rows:
                employee = frappe.db.get_value(
                    "Employee",
                    {"attendance_device_id": user_id},
                    "name",
                )

                if not employee:
                    frappe.logger("essl_adms").warning(
                        f"No employee mapping for device ID {user_id}"
                    )
                    continue

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
                    checkin = frappe.get_doc({
                        "doctype": "Employee Checkin",
                        "employee": employee,
                        "time": punch_time,
                        "device_punch_time": punch_time,
                        "device_id": user_id,
                        "log_type": get_log_type(
                            employee, punch_time, status
                        ),
                    })

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

            frappe.logger("essl_adms").info(
                f"eSSL ATTLOG processed; saved={saved_count}"
            )

        if (
            request.method == "GET"
            and path.endswith("cdata.aspx")
            and request.args.get("options") == "all"
        ):
            serial_number = request.args.get("SN", "")

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

        shifted = datetime.now(timezone.utc) + timedelta(
            minutes=DATE_HEADER_SHIFT_MINUTES
        )

        return Response(
            body,
            status=200,
            content_type="text/plain",
            headers={
                "X-ESSL-Renderer": "active",
                "Date": formatdate(
                    shifted.timestamp(), usegmt=True
                ),
            },
        )
