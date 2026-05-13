# -*- coding: utf-8 -*-
import frappe
import unittest
import json
from gpf_builder.gpf_builder.api.api import (
	save_layout, 
	finalize_setup, 
	upload_pdf_reference,
	get_dunning_letter_fields,
	run_ocr
)
from gpf_builder.gpf_builder.domain.constants import (
	SETUP_STATUS_FINALIZED,
	ERROR_ACCESS_DENIED
)

class TestSecurityHardening(unittest.TestCase):
	def setUp(self):
		# Create a target setup
		self.setup = frappe.new_doc("GPF Print Format Setup")
		self.setup.target_doctype = "Dunning Letter"
		self.setup.insert(ignore_permissions=True)
		
		# Create an attacker setup
		self.attacker_setup = frappe.new_doc("GPF Print Format Setup")
		self.attacker_setup.target_doctype = "Dunning Letter"
		self.attacker_setup.insert(ignore_permissions=True)

	def test_unauthorized_access(self):
		"""
		Proving that Guest and Non-Administrator users are strictly denied.
		SEC-VAL-001
		"""
		users = ["Guest", "test@example.com"]
		# Create test user
		if not frappe.db.exists("User", "test@example.com"):
			user = frappe.new_doc("User")
			user.email = "test@example.com"
			user.first_name = "Test"
			user.insert(ignore_permissions=True)
			user.add_roles("System Manager") # Even System Managers should be blocked

		for user in users:
			frappe.set_user(user)
			with self.assertRaises(frappe.PermissionError):
				get_dunning_letter_fields()

	def test_object_level_scoping_bypass(self):
		"""
		Proving that cross-setup object usage is rejected.
		SEC-VAL-002
		"""
		frappe.set_user("Administrator")
		
		# Create OCR result for Setup A
		ocr_res = frappe.new_doc("GPF OCR Result")
		ocr_res.setup = self.setup.name
		ocr_res.insert(ignore_permissions=True)
		
		# Attempt to use OCR result from Setup A in Setup B layout save
		# We force the active setup to be Setup B
		frappe.db.set_value("GPF Print Format Setup", self.setup.name, "is_active", 0)
		frappe.db.set_value("GPF Print Format Setup", self.attacker_setup.name, "is_active", 1)
		
		blocks = [{
			"block_type": "OCR Text",
			"ocr_result": ocr_res.name,
			"x": 0, "y": 0, "width": 10, "height": 10
		}]
		
		with self.assertRaises(frappe.ValidationError):
			save_layout(json.dumps(blocks))

	def test_sanitizer_regression_xss(self):
		"""
		Proving that XSS payloads are sanitized in layout saving.
		SEC-VAL-003
		"""
		frappe.set_user("Administrator")
		payload = '<script>alert("XSS")</script><img src=x onerror=alert(1)>'
		
		# Test Static Text Sanitization
		blocks = [{
			"block_type": "Static Text",
			"static_text": payload,
			"x": 0, "y": 0, "width": 10, "height": 10
		}]
		save_layout(json.dumps(blocks))
		
		saved_text = frappe.db.get_value("GPF Layout Block", {"setup": self.attacker_setup.name}, "static_text")
		self.assertNotIn("<script>", saved_text)
		self.assertNotIn("onerror", saved_text)

	def test_finalized_state_bypass(self):
		"""
		Proving that finalized setups cannot be mutated via API.
		SEC-VAL-004
		"""
		frappe.set_user("Administrator")
		frappe.db.set_value("GPF Print Format Setup", self.attacker_setup.name, "status", SETUP_STATUS_FINALIZED)
		
		blocks = [{"block_type": "Static Text", "static_text": "Edit", "x": 0, "y": 0, "width": 10, "height": 10}]
		
		with self.assertRaises(frappe.ValidationError):
			save_layout(json.dumps(blocks))

	def tearDown(self):
		frappe.db.rollback()
