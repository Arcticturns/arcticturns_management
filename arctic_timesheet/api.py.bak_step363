import frappe


@frappe.whitelist()
def get_my_employee():
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    employees = frappe.get_all(
        "Employee",
        filters={"user_id": frappe.session.user},
        fields=["name", "employee_name"],
        limit_page_length=2,
    )

    if len(employees) != 1:
        frappe.throw(
            "Exactly one Employee must be linked to your user account."
        )

    return employees[0]


@frappe.whitelist(methods=["POST"])
def save_weekly_draft(start_date, rows):
    import json
    from datetime import datetime, timedelta

    employee = get_my_employee()
    employee_doc = frappe.get_doc("Employee", employee["name"])

    if employee_doc.status != "Active":
        frappe.throw("Employee is not active")

    if isinstance(rows, str):
        rows = json.loads(rows)

    if not isinstance(rows, list) or not rows:
        frappe.throw("At least one work entry is required")

    week_start = datetime.strptime(start_date, "%Y-%m-%d").date()

    if week_start.weekday() != 0:
        frappe.throw("Week must start on Monday")


    week_end = week_start + timedelta(days=6)

    existing = frappe.get_all(
        "Timesheet",
        filters={
            "employee": employee_doc.name,
            "docstatus": ["<", 2],
            "start_date": ["<=", str(week_end)],
            "end_date": [">=", str(week_start)],
        },
        pluck="name",
        limit_page_length=1,
    )

    if existing:
        frappe.throw(
            f"Timesheet already exists for this week: {existing[0]}"
        )

    timesheet = frappe.new_doc("Timesheet")
    timesheet.employee = employee_doc.name
    timesheet.company = employee_doc.company
    timesheet.naming_series = "TS-.YYYY.-"

    for row in rows:
        activity = row.get("activity_type")
        description = row.get("description", "")
        hours = row.get("hours", [])

        if not activity:
            frappe.throw("Activity Type is required")

        if len(hours) != 7:
            frappe.throw("Seven daily hour values are required")

        for day_index, value in enumerate(hours):
            value = float(value or 0)

            if value < 0 or value > 16 or value * 4 != round(value * 4):
                frappe.throw("Hours must be 0–16 in 0.25 increments")

            if value == 0:
                continue

            day = week_start + timedelta(days=day_index)
            from_time = datetime.combine(
                day, datetime.min.time()
            )
            to_time = from_time + timedelta(hours=value)

            timesheet.append("time_logs", {
                "activity_type": activity,
                "project": row.get("project"),
                "task": row.get("task"),
                "description": description,
                "from_time": from_time,
                "to_time": to_time,
                "hours": value,
            })

    if not timesheet.time_logs:
        frappe.throw("Enter at least one hour")

    timesheet.insert()
    return {"name": timesheet.name, "status": "Draft"}


# --- MY WEEK BATCH 1 ---

@frappe.whitelist()
def get_weekly_draft(start_date):
    from datetime import datetime, timedelta

    employee = get_my_employee()
    week_start = datetime.strptime(start_date, "%Y-%m-%d").date()

    if week_start.weekday() != 0:
        frappe.throw("Week must start on Monday")

    week_end = week_start + timedelta(days=6)

    names = frappe.get_all(
        "Timesheet",
        filters={
            "employee": employee["name"],
            "docstatus": 0,
            "start_date": ["<=", str(week_end)],
            "end_date": [">=", str(week_start)]
        },
        pluck="name",
        limit_page_length=2
    )

    if len(names) > 1:
        frappe.throw("Multiple drafts overlap this week. Contact administrator.")

    if not names:
        return {"name": None, "rows": []}

    doc = frappe.get_doc("Timesheet", names[0])
    doc.check_permission("read")

    grouped = {}

    for log in doc.time_logs:
        day = log.from_time.date()
        index = (day - week_start).days

        if index < 0 or index > 6:
            frappe.throw("Draft contains entries outside the selected week")

        key = (
            log.activity_type or "",
            log.project or "",
            log.task or "",
            log.description or ""
        )

        if key not in grouped:
            grouped[key] = {
                "activity_type": key[0],
                "project": key[1],
                "task": key[2],
                "description": key[3],
                "hours": [0] * 7
            }

        grouped[key]["hours"][index] += float(log.hours or 0)

    return {"name": doc.name, "rows": list(grouped.values())}


@frappe.whitelist(methods=["POST"])
def save_weekly_grid(start_date, rows):
    import json
    from datetime import datetime, timedelta

    employee = get_my_employee()
    employee_doc = frappe.get_doc("Employee", employee["name"])

    if employee_doc.status != "Active":
        frappe.throw("Employee is not active")

    if isinstance(rows, str):
        rows = json.loads(rows)

    if not isinstance(rows, list) or not 1 <= len(rows) <= 20:
        frappe.throw("Enter 1 to 20 activity rows")

    validate_weekly_entries(rows)

    week_start = datetime.strptime(start_date, "%Y-%m-%d").date()

    if week_start.weekday() != 0:
        frappe.throw("Week must start on Monday")

    week_end = week_start + timedelta(days=6)

    names = frappe.get_all(
        "Timesheet",
        filters={
            "employee": employee_doc.name,
            "docstatus": ["<", 2],
            "start_date": ["<=", str(week_end)],
            "end_date": [">=", str(week_start)]
        },
        pluck="name",
        limit_page_length=2
    )

    if any(
        frappe.db.get_value("Timesheet", name, "docstatus") == 1
        for name in names
    ):
        frappe.throw(
            "A submitted or approved Timesheet already exists for this week. "
            "You cannot create another draft."
        )

    if len(names) > 1:
        frappe.throw("Multiple Timesheets overlap this week")

    if names:
        doc = frappe.get_doc("Timesheet", names[0])
        doc.check_permission("write")

        if doc.docstatus != 0 or doc.workflow_state not in (None, "", "Draft"):
            frappe.throw("Only Draft Timesheets can be edited")
    else:
        doc = frappe.new_doc("Timesheet")
        doc.employee = employee_doc.name
        doc.company = employee_doc.company
        doc.naming_series = "TS-.YYYY.-"

    daily_totals = [0.0] * 7
    new_logs = []

    for row in rows:
        if not isinstance(row, dict):
            frappe.throw("Invalid activity row")

        activity = row.get("activity_type")
        hours = row.get("hours")

        if not activity or not isinstance(hours, list) or len(hours) != 7:
            frappe.throw("Activity Type and seven daily values are required")

        for index, raw in enumerate(hours):
            try:
                value = float(raw or 0)
            except (ValueError, TypeError):
                frappe.throw("Invalid hours value")

            if not 0 <= value <= 16 or value * 4 != round(value * 4):
                frappe.throw("Hours must be 0–16 in 0.25 increments")

            if not value:
                continue

            day = week_start + timedelta(days=index)
            start_hour = daily_totals[index]
            from_time = datetime.combine(day, datetime.min.time()) + timedelta(hours=start_hour)
            to_time = from_time + timedelta(hours=value)

            daily_totals[index] += value

            if daily_totals[index] > 16:
                frappe.throw("Daily total cannot exceed 16 hours")

            new_logs.append({
                "activity_type": activity,
                "project": row.get("project") or None,
                "task": row.get("task") or None,
                "description": row.get("description") or "",
                "from_time": from_time,
                "to_time": to_time,
                "hours": value
            })

    if not new_logs:
        frappe.throw("Enter at least one hour")

    doc.set("time_logs", [])

    for log in new_logs:
        doc.append("time_logs", log)

    if names:
        doc.save()
    else:
        doc.insert()

    return {
        "name": doc.name,
        "status": "Draft",
        "total_hours": sum(daily_totals)
    }



# --- MODULE 2: ADVANCED WEEKLY VALIDATION ---

def validate_weekly_entries(rows):
    from math import isfinite

    if not isinstance(rows, list) or not 1 <= len(rows) <= 20:
        frappe.throw("Enter 1 to 20 activity rows")

    daily_totals = [0.0] * 7
    seen = set()

    for row_number, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            frappe.throw(f"Invalid row {row_number}")

        activity = row.get("activity_type")
        project = row.get("project") or None
        task = row.get("task") or None
        description = (row.get("description") or "").strip()
        hours = row.get("hours")

        if not activity or not frappe.db.exists("Activity Type", activity):
            frappe.throw(f"Row {row_number}: Invalid Activity Type")

        if project and not frappe.db.exists("Project", project):
            frappe.throw(f"Row {row_number}: Invalid Project")

        if task:
            if not frappe.db.exists("Task", task):
                frappe.throw(f"Row {row_number}: Invalid Task")

            task_project = frappe.db.get_value("Task", task, "project")

            if project and task_project != project:
                frappe.throw(
                    f"Row {row_number}: Task does not belong to selected Project"
                )

            if task_project and not project:
                frappe.throw(
                    f"Row {row_number}: Select the Project linked to this Task"
                )

        if not isinstance(hours, list) or len(hours) != 7:
            frappe.throw(f"Row {row_number}: Seven daily hour values required")

        key = (activity, project, task, description.casefold())
        if key in seen:
            frappe.throw(
                f"Row {row_number}: Duplicate activity row. "
                "Combine hours into one row."
            )
        seen.add(key)

        for day_index, raw in enumerate(hours):
            try:
                value = float(raw or 0)
            except (ValueError, TypeError):
                frappe.throw(f"Row {row_number}: Invalid hours")

            if (
                not isfinite(value)
                or value < 0
                or value > 16
                or abs(value * 4 - round(value * 4)) > 1e-8
            ):
                frappe.throw(
                    f"Row {row_number}: Hours must be 0–16 "
                    "in 0.25 increments"
                )

            daily_totals[day_index] += value

            if daily_totals[day_index] > 16:
                frappe.throw(
                    f"Day {day_index + 1}: Total cannot exceed 16 hours"
                )

    if not any(daily_totals):
        frappe.throw("Enter at least one work hour")

    return daily_totals


def validate_timesheet_before_submit(doc, week_start):
    from datetime import timedelta

    week_end = week_start + timedelta(days=6)
    daily = [0.0] * 7

    if not doc.time_logs:
        frappe.throw("Cannot submit an empty Timesheet")

    for log in doc.time_logs:
        if not log.from_time or not log.to_time:
            frappe.throw("Timesheet entry must have start and end times")

        day = log.from_time.date()
        index = (day - week_start).days

        if index < 0 or index > 6 or log.to_time.date() != day:
            frappe.throw("Timesheet contains entries outside selected day")

        if not frappe.db.exists("Activity Type", log.activity_type):
            frappe.throw("Invalid Activity Type in Timesheet")

        if log.project and not frappe.db.exists("Project", log.project):
            frappe.throw("Invalid Project in Timesheet")

        if log.task:
            if not frappe.db.exists("Task", log.task):
                frappe.throw("Invalid Task in Timesheet")

            task_project = frappe.db.get_value(
                "Task", log.task, "project"
            )

            if log.project and task_project != log.project:
                frappe.throw("Task and Project mismatch")

            if task_project and not log.project:
                frappe.throw("Project required for selected Task")

        hours = float(log.hours or 0)

        if hours <= 0 or hours > 16 or hours * 4 != round(hours * 4):
            frappe.throw("Invalid hours in Timesheet")

        daily[index] += hours

        if daily[index] > 16:
            frappe.throw("Daily total exceeds 16 hours")

    return sum(daily)


# --- MY WEEK SUBMIT WORKFLOW ---

@frappe.whitelist(methods=["POST"])
def submit_my_week(start_date):
    from datetime import datetime, timedelta
    from frappe.model.workflow import apply_workflow

    employee = get_my_employee()
    week_start = datetime.strptime(start_date, "%Y-%m-%d").date()

    if week_start.weekday() != 0:
        frappe.throw("Week must start on Monday")

    week_end = week_start + timedelta(days=6)

    names = frappe.get_all(
        "Timesheet",
        filters={
            "employee": employee["name"],
            "docstatus": 0,
            "workflow_state": "Draft",
            "start_date": ["<=", str(week_end)],
            "end_date": [">=", str(week_start)]
        },
        pluck="name",
        limit_page_length=2
    )

    if len(names) != 1:
        frappe.throw("Exactly one Draft Timesheet is required for this week")

    doc = frappe.get_doc("Timesheet", names[0])
    doc.check_permission("write")

    if doc.docstatus != 0 or doc.workflow_state != "Draft":
        frappe.throw("Only Draft Timesheets can be submitted")

    if not doc.time_logs:
        frappe.throw("Cannot submit an empty Timesheet")

    for log in doc.time_logs:
        if not log.activity_type or not log.hours or log.hours <= 0:
            frappe.throw("Invalid activity entry")

    validate_timesheet_before_submit(doc, week_start)

    submitted = apply_workflow(doc, "Submit")

    return {
        "name": submitted.name,
        "workflow_state": submitted.workflow_state,
        "docstatus": submitted.docstatus
    }


# --- APPROVER INBOX API ---

@frappe.whitelist()
def get_pending_approvals():
    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    if user != "Administrator" and "AT Timesheet Approver" not in frappe.get_roles(user):
        frappe.throw("AT Timesheet Approver role required", frappe.PermissionError)

    records = frappe.get_list(
        "Timesheet",
        filters={
            "workflow_state": "Submitted",
            "docstatus": 1
        },
        fields=[
            "name",
            "employee",
            "employee_name",
            "start_date",
            "total_hours",
            "workflow_state"
        ],
        order_by="modified desc",
        limit_page_length=100
    )

    if user == "Administrator":
        return records

    own_employees = frappe.get_all(
        "Employee",
        filters={"user_id": user},
        pluck="name"
    )

    return [
        record for record in records
        if record.employee not in own_employees
    ]


@frappe.whitelist(methods=["POST"])
def process_timesheet_approval(timesheet_name, action):
    from frappe.model.workflow import apply_workflow

    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    if user != "Administrator" and "AT Timesheet Approver" not in frappe.get_roles(user):
        frappe.throw("AT Timesheet Approver role required", frappe.PermissionError)

    if action not in ("Approve", "Reject"):
        frappe.throw("Invalid approval action")

    doc = frappe.get_doc("Timesheet", timesheet_name)

    if doc.workflow_state != "Submitted" or doc.docstatus != 1:
        frappe.throw("Timesheet is not pending approval")

    own_employees = frappe.get_all(
        "Employee",
        filters={"user_id": user},
        pluck="name"
    )

    if doc.employee in own_employees:
        frappe.throw("You cannot approve or reject your own Timesheet",
                     frappe.PermissionError)

    updated = apply_workflow(doc, action)

    return {
        "name": updated.name,
        "workflow_state": updated.workflow_state,
        "message": f"Timesheet {action.lower()}d successfully"
    }


@frappe.whitelist()
def get_my_week_status(start_date):
    from frappe.utils import getdate, add_days

    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    employees = frappe.get_all(
        "Employee",
        filters={"user_id": user},
        pluck="name"
    )

    if not employees:
        frappe.throw("Employee record not found")

    week_start = getdate(start_date)

    if week_start.weekday() != 0:
        frappe.throw("Week start must be Monday")

    week_end = add_days(week_start, 6)

    records = frappe.get_list(
        "Timesheet",
        filters={
            "employee": ["in", employees],
            "start_date": ["<=", week_end],
            "end_date": [">=", week_start],
            "docstatus": ["<", 2]
        },
        fields=[
            "name", "workflow_state", "docstatus",
            "total_hours", "start_date", "end_date"
        ],
        order_by="modified desc",
        limit_page_length=20
    )

    return records


@frappe.whitelist(methods=["POST"])
def request_timesheet_correction(timesheet_name):
    """Validate an employee's request to correct their rejected Timesheet."""
    employee = get_my_employee()

    doc = frappe.get_doc("Timesheet", timesheet_name)
    doc.check_permission("read")

    if doc.employee != employee["name"]:
        frappe.throw(
            "You can request correction only for your own Timesheet",
            frappe.PermissionError,
        )

    if doc.docstatus != 1 or doc.workflow_state != "Rejected":
        frappe.throw("Only Rejected Timesheets can be corrected")

    if doc.sales_invoice or float(doc.total_billed_hours or 0) > 0:
        frappe.throw("Billed Timesheets cannot be corrected")

    return {
        "name": doc.name,
        "workflow_state": doc.workflow_state,
        "message": "Correction eligible. Cancellation by approver is required.",
    }


@frappe.whitelist(methods=["POST"])
def cancel_rejected_timesheet(timesheet_name):
    """Allow the designated approver to cancel a rejected Timesheet."""
    from frappe.model.workflow import apply_workflow

    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    if user != "Administrator" and "AT Timesheet Approver" not in frappe.get_roles(user):
        frappe.throw("AT Timesheet Approver role required", frappe.PermissionError)

    doc = frappe.get_doc("Timesheet", timesheet_name)
    doc.check_permission("read")
    doc.check_permission("cancel")

    if doc.docstatus != 1 or doc.workflow_state != "Rejected":
        frappe.throw("Only Rejected Timesheets can be cancelled for correction")

    if (
        doc.sales_invoice
        or float(doc.total_billed_hours or 0) > 0
        or float(doc.total_billed_amount or 0) > 0
    ):
        frappe.throw("Billed Timesheets cannot be cancelled for correction")

    own_employees = frappe.get_all(
        "Employee",
        filters={"user_id": user},
        pluck="name",
    )

    if doc.employee in own_employees:
        frappe.throw(
            "You cannot cancel your own Timesheet",
            frappe.PermissionError,
        )

    updated = apply_workflow(doc, "Cancel")

    return {
        "name": updated.name,
        "workflow_state": updated.workflow_state,
        "docstatus": updated.docstatus,
    }
