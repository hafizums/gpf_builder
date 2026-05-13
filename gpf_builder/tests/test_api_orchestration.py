# -*- coding: utf-8 -*-
import frappe
import unittest
import json
from gpf_builder.api.api import save_layout, finalize_setup, upload_pdf_reference
from gpf_builder.domain.constants import SETUP_STATUS_FINALIZED

class TestAPIOrchestration(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		# Create setup
		self.setup = frappe.new_doc("GPF Print Format Setup")
		self.setup.target_doctype = "Dunning Letter"
		self.setup.insert(ignore_permissions=True)

	def test_api_guard_enforcement(self):
		"""
		Proving that API methods enforce Administrator access.
		"""
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			get_dunning_letter_fields()

	def test_save_layout_orchestration(self):
		"""
		Proving that save_layout calls services and updates database.
		"""
		frappe.set_user("Administrator")
		blocks = [{"block_type": "Static Text", "static_text": "API Test", "x": 0, "y": 0, "width": 10, "height": 10}]
		
		save_layout(json.dumps(blocks))
		
		self.assertTrue(frappe.db.exists("GPF Layout Block", {"setup": self.setup.name, "static_text": "API Test"}))
		self.assertTrue(frappe.db.exists("GPF Audit Event", {"event_type": "SAVE_LAYOUT"}))

	def test_finalize_api_locking(self):
		"""
		Proving that after finalize API call, the setup is locked.
		"""
		# Add a block so finalization passes
		blocks = [{"block_type": "Static Text", "static_text": "Block", "x": 0, "y": 0, "width": 10, "height": 10}]
		save_layout(json.dumps(blocks))
		
		finalize_setup()
		
		status = frappe.db.get_value("GPF Print Format Setup", self.setup.name, "status")
		self.assertEqual(status, SETUP_STATUS_FINALIZED)
		
		# Try saving again should fail
		with self.assertRaises(frappe.ValidationError):
			save_layout(json.dumps(blocks))

	def tearDown(self):
		frappe.db.rollback()
