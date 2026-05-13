# -*- coding: utf-8 -*-
import frappe
import unittest
import json
from gpf_builder.gpf_builder.api.api import (
	save_layout, 
	finalize_setup, 
	upload_pdf_reference,
	get_preview
)
from gpf_builder.gpf_builder.services.output_service import OutputService

class TestIntegrationWorkflow(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		# Ensure clean state
		frappe.db.delete("GPF Print Format Setup")
		
		self.setup = frappe.new_doc("GPF Print Format Setup")
		self.setup.target_doctype = "Dunning Letter"
		self.setup.is_active = 1
		self.setup.insert(ignore_permissions=True)

	def test_happy_path_e2e(self):
		"""
		Verifying the complete workflow from PDF link to Final Output.
		"""
		# 1. Upload/Link PDF (mock file reference)
		upload_pdf_reference("test_file.pdf")
		self.assertEqual(frappe.db.get_value("GPF Print Format Setup", self.setup.name, "pdf_reference_file"), "test_file.pdf")
		
		# 2. Save Layout
		blocks = [
			{"block_type": "Static Text", "static_text": "Header", "x": 10, "y": 10, "width": 80, "height": 5},
			{"block_type": "Dynamic Field", "fieldname": "customer_name", "x": 10, "y": 20, "width": 40, "height": 5}
		]
		save_layout(json.dumps(blocks))
		self.assertEqual(frappe.db.count("GPF Layout Block", {"setup": self.setup.name}), 2)
		
		# 3. Get Preview
		preview_html = get_preview()
		self.assertIn("Header", preview_html)
		self.assertIn("REDACTED", preview_html)
		
		# 4. Finalize
		finalize_setup()
		self.assertEqual(frappe.db.get_value("GPF Print Format Setup", self.setup.name, "status"), "Finalized")
		
		# 5. Generate Production Output
		mock_doc = frappe._dict({"customer_name": "REAL CUSTOMER", "doctype": "Dunning Letter"})
		output_html = OutputService.generate_final_html(mock_doc)
		self.assertIn("REAL CUSTOMER", output_html)
		self.assertIn("Header", output_html)

	def tearDown(self):
		frappe.db.rollback()
