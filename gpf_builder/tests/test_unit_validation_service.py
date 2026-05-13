# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.services.validation_service import ValidationService

class TestValidationService(unittest.TestCase):
	def setUp(self):
		# Create two setups
		self.setup1 = frappe.new_doc("GPF Print Format Setup")
		self.setup1.target_doctype = "Dunning Letter"
		self.setup1.insert(ignore_permissions=True)
		
		self.setup2 = frappe.new_doc("GPF Print Format Setup")
		self.setup2.target_doctype = "Dunning Letter"
		self.setup2.insert(ignore_permissions=True)
		
		# Create an OCR result for setup 1
		self.ocr1 = frappe.new_doc("GPF OCR Result")
		self.ocr1.setup = self.setup1.name
		self.ocr1.source_pdf_file = "test.pdf"
		self.ocr1.insert(ignore_permissions=True)

	def test_setup_scope_success(self):
		"""
		Proving valid setup scope is accepted.
		"""
		try:
			ValidationService.validate_setup_scope("GPF OCR Result", self.ocr1.name, self.setup1.name)
		except frappe.PermissionError:
			self.fail("ValidationService rejected a valid setup scope!")

	def test_setup_scope_failure(self):
		"""
		Proving cross-setup access is rejected.
		"""
		with self.assertRaises(frappe.PermissionError):
			ValidationService.validate_setup_scope("GPF OCR Result", self.ocr1.name, self.setup2.name)

	def test_file_scope_failure(self):
		"""
		Proving unrelated files are rejected.
		"""
		with self.assertRaises(frappe.PermissionError):
			ValidationService.validate_file_scope("random_file.png", self.setup1.name)

	def tearDown(self):
		frappe.db.rollback()
