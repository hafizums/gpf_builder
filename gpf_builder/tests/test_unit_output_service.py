# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.services.output_service import OutputService
from gpf_builder.services.layout_service import LayoutService
from gpf_builder.services.setup_service import SetupService
from gpf_builder.services.field_mapping_service import FieldMappingService
from gpf_builder.domain.constants import SETUP_STATUS_FINALIZED, SETUP_STATUS_EDITING

class TestOutputService(unittest.TestCase):
	def setUp(self):
		# Reuse the singleton active setup expected by OutputService.
		self.setup = SetupService.get_active_setup()
		self.setup.target_doctype = "Dunning Letter"
		self.setup.status = SETUP_STATUS_FINALIZED
		self.setup.save(ignore_permissions=True)
		frappe.db.delete("GPF Layout Block", {"setup": self.setup.name})
		self.dynamic_field = FieldMappingService.get_allowed_fields("Dunning Letter")[0]["fieldname"]
		
		# Create a block
		LayoutService.create_block(self.setup.name, {
			"block_type": "Dynamic Field",
			"fieldname": self.dynamic_field,
			"x": 10, "y": 10, "width": 50, "height": 5
		})
		LayoutService.create_block(self.setup.name, {
			"block_type": "Static Text",
			"static_text": "<strong>HTML Header</strong>",
			"x": 10, "y": 20, "width": 50, "height": 5
		})
		
		# Mock Dunning Letter doc
		self.doc = frappe._dict({
			self.dynamic_field: "REAL CUSTOMER NAME",
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
		self.assertIn("font-size: 12px", html)
		self.assertIn("font-family: Arial", html)
		self.assertIn("line-height: 1.2", html)
		self.assertIn('"><span>REAL CUSTOMER NAME</span></div>', html)
		self.assertIn("<strong>HTML Header</strong>", html)

	def test_static_html_is_sanitized(self):
		"""
		Proving Static Text supports safe HTML without allowing script handlers.
		"""
		frappe.db.delete("GPF Layout Block", {"setup": self.setup.name})
		LayoutService.create_block(self.setup.name, {
			"block_type": "Static Text",
			"static_text": '<b>Safe</b><script>alert(1)</script><img src=x onerror="alert(1)">',
			"x": 0, "y": 0, "width": 50, "height": 5
		})
		html = OutputService.generate_final_html(self.doc)
		self.assertIn("<b>Safe</b>", html)
		self.assertNotIn("<script>", html)
		self.assertNotIn("onerror", html)

	def test_output_css_removes_print_margins(self):
		"""
		Proving final output is sized for wkhtmltopdf without Frappe wrapper gaps.
		"""
		html = OutputService.generate_final_html(self.doc)
		self.assertIn("@page", html)
		self.assertIn("margin: 0", html)
		self.assertIn("margin-left: 0mm", html)
		self.assertIn("margin-right: 0mm", html)
		self.assertIn(".print-format", html)
		self.assertIn("width: 210mm", html)
		self.assertIn("height: 297mm", html)

	def tearDown(self):
		frappe.db.rollback()
