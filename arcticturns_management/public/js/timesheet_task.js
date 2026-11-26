frappe.ui.form.on("Timesheet", {
    refresh(frm) {
        frm.set_query("task", "time_logs", (doc, cdt, cdn) => {
            const row = locals[cdt][cdn];
            const assignment = frm._task_assignment;

            if (!row.project || assignment?.employee !== doc.employee || !assignment?.user) {
                return { filters: { name: ["in", ["__no_assigned_task__"]] } };
            }

            return {
                filters: {
                    project: row.project,
                    status: ["!=", "Cancelled"],
                    is_group: 0,
                    _assign: ["like", `%${JSON.stringify(assignment.user)}%`],
                },
            };
        });

        return load_task_assignee(frm);
    },

    employee(frm) {
        return load_task_assignee(frm);
    },
});

async function load_task_assignee(frm) {
    const assignment = { employee: frm.doc.employee, user: null };
    frm._task_assignment = assignment;

    if (!assignment.employee) {
        return;
    }

    const { message } = await frappe.db.get_value(
        "Employee", assignment.employee, "user_id"
    );
    assignment.user = message?.user_id || null;
}
