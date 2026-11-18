
frappe.pages["approver-inbox"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "Approver Inbox",
        single_column: true
    });

    const $body = $(page.body);

    $body.html(`
        <div class="frappe-card" style="padding:20px">
            <h3>Pending Timesheet Approvals</h3>
            <p class="text-muted">
                Submitted Timesheets waiting for approval.
            </p>
            <button class="btn btn-default" id="refresh-approvals">
                Refresh
            </button>
            <div style="overflow-x:auto;margin-top:15px">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Timesheet</th>
                            <th>Employee</th>
                            <th>Start Date</th>
                            <th>Total Hours</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="approval-list">
                        <tr><td colspan="6">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    `);

    function loadApprovals() {
        frappe.call({
            method: "arctic_timesheet.api.get_pending_approvals",
            callback(r) {
                if (r.exc) return;

                const records = r.message || [];
                const $list = $body.find("#approval-list");
                $list.empty();

                if (!records.length) {
                    $list.append(
                        $("<tr>").append(
                            $("<td>").attr("colspan", 6)
                                .text("No pending approvals.")
                        )
                    );
                    return;
                }

                records.forEach(item => {
                    const $tr = $("<tr>");

                    [
                        item.name,
                        item.employee_name,
                        item.start_date,
                        item.total_hours,
                        item.workflow_state
                    ].forEach(value => {
                        $tr.append($("<td>").text(value ?? ""));
                    });


                    const $actions = $("<td>");

                    ["Approve", "Reject"].forEach(action => {
                        const $button = $("<button>")
                            .addClass(action === "Approve"
                                ? "btn btn-primary btn-xs"
                                : "btn btn-default btn-xs")
                            .css("margin-right", "6px")
                            .text(action)
                            .on("click", () => {
                                frappe.confirm(
                                    `${action} Timesheet ${item.name}?`,
                                    () => {
                                        $button.prop("disabled", true);

                                        frappe.call({
                                            method: "arctic_timesheet.api.process_timesheet_approval",
                                            type: "POST",
                                            args: {
                                                timesheet_name: item.name,
                                                action: action
                                            },
                                            callback: function(r) {
                                                if (r.message) {
                                                    frappe.show_alert({
                                                        message: `${item.name}: ${action} successful`,
                                                        indicator: "green"
                                                    });
                                                    loadApprovals();
                                                }
                                            },
                                            always: function() {
                                                $button.prop("disabled", false);
                                            }
                                        });
                                    }
                                );
                            });

                        $actions.append($button);
                    });

                    $tr.append($actions);
                    $list.append($tr);
                });
            }
        });
    }

    $body.on("click", "#refresh-approvals", loadApprovals);
    loadApprovals();
};
