import frappe


def calculate_expected_hours(employee, week_start, days=7):
    from datetime import timedelta
    from frappe.utils import getdate

    week_start = getdate(week_start)
    week_end = week_start + timedelta(days=days - 1)

    holiday_list = frappe.db.get_value(
        "Employee", employee, "holiday_list"
    )

    if not holiday_list:
        frappe.throw("Employee Holiday List is not configured")

    holidays = {
        getdate(d.holiday_date)
        for d in frappe.get_all(
            "Holiday",
            filters={
                "parent": holiday_list,
                "holiday_date": ["between", [week_start, week_end]]
            },
            fields=["holiday_date"]
        )
    }

    leaves = frappe.get_all(
        "Leave Application",
        filters={
            "employee": employee,
            "status": "Approved",
            "docstatus": 1,
            "from_date": ["<=", week_end],
            "to_date": [">=", week_start]
        },
        fields=["from_date", "to_date", "half_day", "half_day_date"]
    )

    expected = 0.0

    for i in range(days):
        day = week_start + timedelta(days=i)

        if day in holidays:
            continue

        hours = 8.0

        for leave in leaves:
            if getdate(leave.from_date) <= day <= getdate(leave.to_date):
                if leave.half_day and getdate(
                    leave.half_day_date or leave.from_date
                ) == day:
                    hours = 4.0
                else:
                    hours = 0.0
                break

        expected += hours

    return expected
