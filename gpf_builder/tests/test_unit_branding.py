# -*- coding: utf-8 -*-
import frappe
import unittest
from unittest.mock import patch, MagicMock
from gpf_builder.services.branding_service import BrandingService

class TestBrandingService(unittest.TestCase):
	@patch("gpf_builder.services.branding_service.frappe.get_doc")
	@patch("gpf_builder.services.branding_service.frappe.db.exists")
	def test_validate_image_success(self, mock_db_exists, mock_get_doc):
		"""
		Proving valid PNG image is accepted.
		"""
		mock_db_exists.return_value = True
		mock_file = MagicMock()
		mock_file.file_name = "logo.png"
		mock_file.file_size = 500 * 1024 # 500KB
		mock_get_doc.return_value = mock_file
		
		self.assertTrue(BrandingService.validate_image("test_file"))

	@patch("gpf_builder.services.branding_service.frappe.get_doc")
	@patch("gpf_builder.services.branding_service.frappe.db.exists")
	def test_validate_image_invalid_type(self, mock_db_exists, mock_get_doc):
		"""
		Proving invalid type (e.g., .webp) is rejected.
		"""
		mock_db_exists.return_value = True
		mock_file = MagicMock()
		mock_file.file_name = "image.webp"
		mock_file.file_size = 100 * 1024
		mock_get_doc.return_value = mock_file
		
		with self.assertRaises(frappe.ValidationError):
			BrandingService.validate_image("test_file")

	@patch("gpf_builder.services.branding_service.frappe.get_doc")
	@patch("gpf_builder.services.branding_service.frappe.db.exists")
	def test_sanitize_svg_unsafe_script(self, mock_db_exists, mock_get_doc):
		"""
		Proving SVG with <script> is rejected.
		"""
		mock_db_exists.return_value = True
		mock_file = MagicMock()
		mock_file.file_name = "malicious.svg"
		mock_file.file_size = 10 * 1024
		mock_file.get_content.return_value = b'<svg><script>alert(1)</script></svg>'
		mock_get_doc.return_value = mock_file
		
		with self.assertRaises(frappe.SecurityError):
			BrandingService.validate_image("test_file")

	@patch("gpf_builder.services.branding_service.frappe.get_doc")
	@patch("gpf_builder.services.branding_service.frappe.db.exists")
	def test_sanitize_svg_unsafe_handler(self, mock_db_exists, mock_get_doc):
		"""
		Proving SVG with event handler is rejected.
		"""
		mock_db_exists.return_value = True
		mock_file = MagicMock()
		mock_file.file_name = "malicious.svg"
		mock_file.file_size = 10 * 1024
		mock_file.get_content.return_value = b'<svg onload="alert(1)"></svg>'
		mock_get_doc.return_value = mock_file
		
		with self.assertRaises(frappe.SecurityError):
			BrandingService.validate_image("test_file")

	def tearDown(self):
		frappe.db.rollback()
