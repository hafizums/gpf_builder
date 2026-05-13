# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.services.output_service import OutputService
from gpf_builder.services.layout_service import LayoutService
from gpf_builder.domain.constants import SETUP_STATUS_FINALIZED, SETUP_STATUS_EDITING

class TestOutputService(unittest.TestCase):
	def setUp(self):
		# Create setup and finalize it
		self.setup = frappe.new_doc("GPF Print Format Setup")
		self.setup.target_doctype = "Dunning Letter"
		self.setup.status = SETUP_STATUS_FINALIZED
		self.setup.insert(ignore_permissions=True)
		
		# Create a block
		LayoutService.create_block(self.setup.name, {
			"block_type": "Dynamic Field",
			"fieldname": "customer_name",
			"x": 10, "y": 10, "width": 50, "height": 5
		})
		
		# Mock Dunning Letter doc
		self.doc = frappe._dict({
			"customer_name": "REAL CUSTOMER NAME",
			"doctype": "Dunning Letter"
		})

	def test_output_requires_finalized_state(self):
		"""
		Proving that output generation fails if the setup is not finalized.
		"""
		frappe.db.set_value("GPF Print Format Setup", self.setup.name, "status", SETUP_STATUS_EDITING)
		with self.assertRaises(frappe.ValidationError):
			OutputService.generate_final_html(self.doc)

	def test_production_data_injection(self):
		"""
		Proving that real production data is injected into the HTML.
		"""
		html = OutputService.generate_final_html(self.doc)
		self.assertIn("REAL CUSTOMER NAME", html)
		self.assertNotIn("REDACTED", html)

	def tearDown(self):
		frappe.db.rollback()
