import re
import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import cint


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=5, seconds=60, methods=["POST"])
def create_website_enquiry(name=None, phone=None, email=None, message=None):

    name = (name or "").strip()
    phone = (phone or "").strip()
    email = (email or "").strip().lower()
    message = (message or "").strip()

    # Basic input validation
    if not name or len(name) > 140:
        frappe.throw("Please enter a valid name.")

    if not email and not phone:
        frappe.throw("Email or phone number is required.")

    if email and (
        len(email) > 254
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        frappe.throw("Please enter a valid email address.")

    if phone and not re.fullmatch(r"[0-9+\-\s()]{7,20}", phone):
        frappe.throw("Please enter a valid phone number.")

    if len(message) > 5000:
        frappe.throw("Message is too long.")

    # Duplicate check
    if email:
        existing = frappe.db.exists("CRM Lead", {"email": email})
        if existing:
            return {
                "success": False,
                "duplicate": True,
                "message": "A lead with this email already exists."
            }

    if phone:
        existing = frappe.db.exists("CRM Lead", {"mobile_no": phone})
        if existing:
            return {
                "success": False,
                "duplicate": True,
                "message": "A lead with this phone number already exists."
            }

    # Create unassigned CRM Lead
    lead = frappe.get_doc({
        "doctype": "CRM Lead",
        "first_name": name,
        "email": email,
        "mobile_no": phone,
        "custom_website_enquiry_message": message,
        "status": "New"
    })

    lead.insert()

    return {
        "success": True,
        "message": "Website enquiry received successfully."
    }
