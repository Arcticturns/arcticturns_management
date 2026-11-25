import frappe


def sales_target_permission_query(user=None):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    # CEO and System Manager can view all targets
    if "CEO" in roles or "System Manager" in roles:
        return ""

    # CRM Salesperson can view only their own Individual targets
    if "CRM Salesperson" in roles:
        return (
            "`tabSales Target`.`target_type` = 'Individual' "
            f"AND `tabSales Target`.`salesperson` = {frappe.db.escape(user)}"
        )

    # Everyone else gets no additional access
    return "1=0"
def sales_target_has_permission(doc, ptype, user=None):
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if "System Manager" in roles:
        return True

    if "CEO" in roles and ptype in ("read", "report"):
        return True

    if "CRM Salesperson" in roles:
        if ptype in ("read", "report"):
            return (
                doc.target_type == "Individual"
                and doc.salesperson == user
            )
        return False

    return None
