import frappe
from datetime import timedelta
from frappe.utils import get_datetime, now_datetime


def set_first_contact_deadline(doc, method=None):
    if doc.doctype != "CRM Lead":
        return

    if doc.get("first_contact_by"):
        return

    created = get_datetime(doc.creation)
    deadline = created
    working_days = 0

    while working_days < 4:
        deadline += timedelta(days=1)
        if deadline.weekday() < 5:
            working_days += 1

    doc.db_set("first_contact_by", deadline, update_modified=False)


def check_overdue_lead_slas():
    now = now_datetime()

    overdue_leads = frappe.get_all(
        "CRM Lead",
        filters={
            "status": "New",
            "first_contact_by": ["<=", now],
            "lead_owner": ["is", "set"]
        },
        fields=["name", "lead_owner"]
    )

    for lead in overdue_leads:
        exists = frappe.db.exists(
            "Notification Log",
            {
                "for_user": lead.lead_owner,
                "document_type": "CRM Lead",
                "document_name": lead.name,
                "title": "Lead SLA overdue"
            }
        )

        if exists:
            continue

        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "type": "Alert",
            "title": "Lead SLA overdue",
            "description": (
                f"Lead {lead.name} is still in New status "
                "after its 4-working-day contact deadline."
            ),
            "document_type": "CRM Lead",
            "document_name": lead.name,
            "for_user": lead.lead_owner,
            "from_user": "Administrator"
        })

        notification.insert(ignore_permissions=True)

    frappe.db.commit()
def validate_won_deal_value(doc, method=None):
    if doc.status == "Won":
        if not doc.deal_value or doc.deal_value <= 0:
            frappe.throw("Please enter the Deal Value before marking this deal as Won.")

        if not doc.closed_date:
            frappe.throw("Please enter the Closed Date before marking this deal as Won.")

def update_sales_target_achievement():
    targets = frappe.get_all(
        "Sales Target",
        filters={"target_type": "Individual"},
        fields=[
            "name",
            "salesperson",
            "start_date",
            "end_date",
            "target_amount"
        ]
    )

    today = frappe.utils.getdate()

    for target in targets:
        achieved = frappe.db.sql("""
            SELECT COALESCE(SUM(deal_value), 0)
            FROM `tabCRM Deal`
            WHERE deal_owner = %s
            AND status = 'Won'
            AND closed_date BETWEEN %s AND %s
        """, (
            target.salesperson,
            target.start_date,
            target.end_date
        ))[0][0]

        percentage = (
            (achieved / target.target_amount) * 100
            if target.target_amount else 0
        )

        if percentage >= 100:
            status = "Achieved"
        elif today > target.end_date:
            status = "Missed"
        elif achieved > 0:
            status = "In Progress"
        else:
            status = "Not Started"

        frappe.db.set_value(
            "Sales Target",
            target.name,
            {
                "achieved_amount": achieved,
                "achievement_percentage": percentage,
                "target_status": status
            },
            update_modified=False
        )

    frappe.db.commit()
