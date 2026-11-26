from datetime import datetime, time, timedelta

import frappe
from frappe.query_builder.functions import Max
from frappe.utils import get_datetime, getdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        "Employee:Link/Employee:155",
        "Employee Name:Data:200",
        "Timesheet:Link/Timesheet:155",
        "Timesheet Status:Data:170",
        "Last Submitted At:Datetime:170",
        "Submission Timing:Data:180",
    ]

    if not filters.week_start or not filters.week_end:
        return columns, []

    start = getdate(filters.week_start)
    end = getdate(filters.week_end)
    if end < start:
        frappe.throw("Week End must be on or after Week Start.")

    cutoff = datetime.combine(end + timedelta(days=1), time(11))
    employee = frappe.qb.DocType("Employee")
    timesheet = frappe.qb.DocType("Timesheet")
    comment = frappe.qb.DocType("Comment")

    records = (
        frappe.qb.from_(employee)
        .left_join(timesheet)
        .on(
            (timesheet.employee == employee.name)
            & (timesheet.company == employee.company)
            & (timesheet.docstatus < 2)
            & (timesheet.start_date <= end)
            & (timesheet.end_date >= start)
        )
        .left_join(comment)
        .on(
            (comment.reference_doctype == "Timesheet")
            & (comment.reference_name == timesheet.name)
            & (comment.comment_type == "Workflow")
            & (comment.content == "Submitted")
        )
        .select(
            employee.name.as_("employee_id"),
            employee.employee_name,
            timesheet.name.as_("timesheet_id"),
            timesheet.workflow_state,
            timesheet.docstatus,
            Max(comment.creation).as_("submitted_at"),
        )
        .where(employee.status == "Active")
        .where(employee.company == "Arctic Turns Solutions Pvt. Ltd.")
        .groupby(
            employee.name, employee.employee_name, timesheet.name,
            timesheet.workflow_state, timesheet.docstatus,
        )
        .orderby(employee.employee_name, timesheet.name)
    ).run(as_dict=True)

    status_labels = {
        "Submitted": "Pending Approval",
        "Approved": "Approved",
        "Rejected": "Rejected",
    }
    data = []
    for row in records:
        if not row.timesheet_id:
            status = "Missing Timesheet"
        else:
            fallback = "Not Submitted" if row.docstatus == 0 else "Check Workflow"
            status = status_labels.get(row.workflow_state, fallback)

        if not row.submitted_at:
            timing = "No Submission Recorded"
        elif get_datetime(row.submitted_at) > cutoff:
            timing = "Late Submission"
        else:
            timing = "On Time"

        data.append([
            row.employee_id, row.employee_name, row.timesheet_id,
            status, row.submitted_at, timing,
        ])

    return columns, data
