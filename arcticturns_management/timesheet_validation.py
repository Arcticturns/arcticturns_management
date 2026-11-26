from collections import defaultdict

import frappe
from frappe.utils import get_datetime

from arcticturns_management.expected_hours import calculate_expected_hours


def validate_timesheet(doc, method=None):
    if not doc.employee or not doc.time_logs:
        return
    validate_assigned_tasks(doc)
    holiday_list = frappe.db.get_value("Employee", doc.employee, "holiday_list")
    daily_hours = defaultdict(float)
    expected_by_day = {}

    for row in doc.time_logs:
        hours = float(row.hours or 0)

        if hours < 0.25:
            frappe.throw("Minimum time entry is 0.25 hours.")

        if round(hours * 4, 6) % 1 != 0:
            frappe.throw("Hours must be in multiples of 0.25.")

        if row.from_time:
            day = get_datetime(row.from_time).date()
            daily_hours[day] += hours
            if day not in expected_by_day:
                is_holiday = bool(
                    holiday_list and frappe.db.exists(
                        "Holiday", {"parent": holiday_list, "holiday_date": day}
                    )
                )
                is_non_working_day = day.weekday() >= 5 or is_holiday

                if is_non_working_day:
                    leave_holiday_reason = (
                        doc.get("custom_leave__holiday_work_reason")
                        or doc.get("custom_leave_holiday_work_reason")
                        or ""
                    ).strip()
                    if not leave_holiday_reason:
                        day_type = "Holiday" if is_holiday else "Weekend"
                        frappe.throw(f"{day}: {day_type} work reason is mandatory.")
                    expected_by_day[day] = 0.0
                else:
                    expected_by_day[day] = calculate_expected_hours(
                        doc.employee, day, days=1
                    )

    doc.custom_expected_hours = sum(expected_by_day.values())

    for day, total in daily_hours.items():
        if total > 16:
            frappe.throw(
                f"{day}: Maximum 16 working hours allowed per day."
            )

        if total > 10:
            frappe.msgprint(
                f"{day}: Working hours exceed 10 hours.",
                indicator="orange",
                alert=True
            )
    # Submission validation only
    if method != "before_submit":
        return
    for row in doc.time_logs:
        if not (row.description or "").strip():
            frappe.throw(
                f"Row {row.idx}: Description is mandatory."
            )

        if row.is_billable and len((row.description or "").strip()) < 10:
            frappe.throw(
                f"Row {row.idx}: Billable description must contain at least 10 characters."
            )

    if not (doc.get("custom_shortfall_reason") or "").strip():
        for day, expected in sorted(expected_by_day.items()):
            actual = daily_hours[day]
            if actual < expected:
                frappe.throw(
                    f"{day}: Expected {expected:g} hours, logged {actual:g} hours. "
                    "Shortfall Reason is mandatory."
                )


def validate_assigned_tasks(doc):
    employee_user = frappe.db.get_value("Employee", doc.employee, "user_id")
    if not employee_user:
        frappe.throw("The Timesheet employee must be linked to a User.")

    for row in doc.time_logs:
        if not row.task:
            frappe.throw(f"Row {row.idx}: Task is mandatory.")

        if not frappe.db.exists(
            "ToDo",
            {
                "reference_type": "Task",
                "reference_name": row.task,
                "allocated_to": employee_user,
                "status": "Open",
            },
        ):
            frappe.throw(
                f"Row {row.idx}: Task {row.task} is not assigned to this employee."
            )
