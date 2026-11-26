frappe.query_reports["AT Weekly Timesheet Compliance"] = {
    filters: [
        {
            fieldname: "week_start",
            label: __("Week Start"),
            fieldtype: "Date",
            reqd: 1,
        },
        {
            fieldname: "week_end",
            label: __("Week End"),
            fieldtype: "Date",
            reqd: 1,
        },
    ],
};
