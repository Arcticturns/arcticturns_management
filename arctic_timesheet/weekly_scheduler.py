
import frappe
from frappe.utils import getdate, add_days, nowdate


def get_week_start(reference_date=None):
    today = getdate(reference_date or nowdate())
    return add_days(today, -today.weekday())


def weekly_draft_preview(reference_date=None):
    """Read-only preview. Does not create Timesheets."""
    week_start = get_week_start(reference_date)
    week_end = add_days(week_start, 6)

    employees = frappe.get_all(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name", "user_id"],
        limit_page_length=0,
    )

    result = []

    for employee in employees:
        existing = frappe.get_all(
            "Timesheet",
            filters={
                "employee": employee.name,
                "docstatus": ["<", 2],
                "start_date": ["<=", week_end],
                "end_date": [">=", week_start],
            },
            pluck="name",
            limit_page_length=1,
        )

        result.append({
            "employee": employee.name,
            "employee_name": employee.employee_name,
            "week_start": str(week_start),
            "week_end": str(week_end),
            "status": "Existing Timesheet" if existing else "Ready for Entry",
        })

    return result


def weekly_reminder_preview(reference_date=None):
    """Read-only reminder preview. No emails sent."""
    from frappe.utils import getdate, nowdate

    today = getdate(reference_date or nowdate())
    employees = weekly_draft_preview(today)

    result = []

    for employee in employees:
        if employee["status"] != "Ready for Entry":
            continue

        user_id = frappe.db.get_value(
            "Employee", employee["employee"], "user_id"
        )

        if not user_id:
            continue

        if not frappe.db.exists(
            "User", {"name": user_id, "enabled": 1}
        ):
            continue

        result.append({
            "employee": employee["employee"],
            "email": user_id,
            "week_start": employee["week_start"],
            "reminder": "Pending weekly timesheet entry",
        })

    return result


def weekly_reminder_plan(reference_date=None):
    """Read-only reminder plan. No emails or database writes."""
    candidates = weekly_reminder_preview(reference_date)
    seen = set()
    reminders = []

    for item in candidates:
        key = (
            item["employee"],
            item["week_start"],
            "weekly_timesheet_reminder",
        )
        if key in seen:
            continue
        seen.add(key)

        reminders.append({
            **item,
            "reminder_key": ":".join(key),
            "action": "DRY_RUN_ONLY",
        })

    return {
        "week_start": str(get_week_start(reference_date)),
        "reminder_count": len(reminders),
        "reminders": reminders,
        "emails_sent": 0,
    }


def weekly_scheduler_dry_run(reference_date=None):
    """Scheduler-safe dry run. No emails or Timesheet creation."""
    plan = weekly_reminder_plan(reference_date)

    return {
        "status": "DRY_RUN",
        "week_start": plan["week_start"],
        "eligible_employees": plan["reminder_count"],
        "emails_sent": 0,
        "timesheets_created": 0,
    }
