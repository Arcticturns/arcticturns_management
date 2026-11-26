from datetime import timedelta

import frappe
from frappe.query_builder import Case
from frappe.query_builder.functions import Sum
from frappe.utils import flt, getdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        "Employee:Link/Employee:150",
        "Employee Name:Data:200",
        "Total Hours:Float:120",
        "Approved Hours:Float:130",
        "Pending Approval Hours:Float:170",
    ]

    if not filters.week_start or not filters.week_end:
        return columns, []

    start = getdate(filters.week_start)
    end = getdate(filters.week_end)
    if end < start:
        frappe.throw("Week End must be on or after Week Start.")

    # The scheduled Monday report must exclude the new week's Monday.
    stop = min(end + timedelta(days=1), start + timedelta(days=7))

    detail = frappe.qb.DocType("Timesheet Detail")
    timesheet = frappe.qb.DocType("Timesheet")
    employee = frappe.qb.DocType("Employee")

    rows = (
        frappe.qb.from_(detail)
        .join(timesheet).on(timesheet.name == detail.parent)
        .join(employee).on(employee.name == timesheet.employee)
        .select(
            employee.name,
            employee.employee_name,
            Sum(detail.hours).as_("total_hours"),
            Sum(Case().when(timesheet.workflow_state == "Approved", detail.hours).else_(0)).as_("approved_hours"),
            Sum(Case().when(timesheet.workflow_state == "Submitted", detail.hours).else_(0)).as_("pending_hours"),
        )
        .where(timesheet.company == "Arctic Turns Solutions Pvt. Ltd.")
        .where(timesheet.docstatus < 2)
        .where(timesheet.workflow_state.isin(["Submitted", "Approved"]))
        .where(detail.from_time >= start)
        .where(detail.from_time < stop)
        .groupby(employee.name, employee.employee_name)
        .orderby(employee.employee_name)
    ).run()

    return columns, [
        [employee_id, name, flt(total, 2), flt(approved, 2), flt(pending, 2)]
        for employee_id, name, total, approved, pending in rows
    ]
