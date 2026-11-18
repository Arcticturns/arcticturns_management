from datetime import datetime, timedelta

import frappe
from frappe.tests import IntegrationTestCase

from arctic_crm.tasks import (
    set_first_contact_deadline,
    validate_won_deal_value,
)


class TestLeadSLA(IntegrationTestCase):

    def test_deadline_four_working_days_from_monday(self):
        created = datetime(2026, 11, 9, 10, 0, 0)

        doc = frappe._dict({
            "doctype": "CRM Lead",
            "creation": created,
            "first_contact_by": None,
            "db_set": lambda field, value, **kwargs: setattr(
                doc, field, value
            ),
        })

        set_first_contact_deadline(doc)

        self.assertEqual(
            doc.first_contact_by.date(),
            datetime(2026, 11, 13).date()
        )

    def test_deadline_four_working_days_from_friday(self):
        created = datetime(2026, 11, 13, 10, 0, 0)

        doc = frappe._dict({
            "doctype": "CRM Lead",
            "creation": created,
            "first_contact_by": None,
            "db_set": lambda field, value, **kwargs: setattr(
                doc, field, value
            ),
        })

        set_first_contact_deadline(doc)

        self.assertEqual(
            doc.first_contact_by.date(),
            datetime(2026, 11, 19).date()
        )


class TestWonDealValidation(IntegrationTestCase):

    def test_won_deal_requires_deal_value(self):
        doc = frappe._dict({
            "status": "Won",
            "deal_value": 0,
            "closed_date": "2026-11-10",
        })

        with self.assertRaises(frappe.ValidationError):
            validate_won_deal_value(doc)

    def test_won_deal_requires_closed_date(self):
        doc = frappe._dict({
            "status": "Won",
            "deal_value": 50000,
            "closed_date": None,
        })

        with self.assertRaises(frappe.ValidationError):
            validate_won_deal_value(doc)

    def test_won_deal_with_required_values_passes(self):
        doc = frappe._dict({
            "status": "Won",
            "deal_value": 50000,
            "closed_date": "2026-11-10",
        })

        validate_won_deal_value(doc)
