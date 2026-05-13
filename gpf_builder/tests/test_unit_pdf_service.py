# -*- coding: utf-8 -*-
import frappe
import unittest
from unittest.mock import patch, MagicMock
from gpf_builder.services.pdf_service import PDFService

class TestPDFService(unittest.TestCase):
	def setUp(self):
		self.pdf_service = PDFService()

	@patch("gpf_builder.services.pdf_service.frappe.get_doc")
	@patch("gpf_builder.services.pdf_service.frappe.db.exists")
	@patch("gpf_builder.services.pdf_service.PdfReader")
	@patch("gpf_builder.services.pdf_service.os.path.exists")
	def test_validate_pdf_success(self, mock_os_exists, mock_pdf_reader, mock_db_exists, mock_get_doc):
		"""
		Proving valid PDF (private, <2MB, 1 page) is accepted.
		"""
		mock_db_exists.return_value = True
		mock_os_exists.return_value = True
		
		mock_file = MagicMock()
		mock_file.is_private = True
		mock_file.file_name = "test.pdf"
		mock_file.file_size = 1024 * 1024 # 1MB
		mock_file.file_url = "/private/files/test.pdf"
		mock_get_doc.return_value = mock_file
		
		mock_reader_instance = MagicMock()
		mock_reader_instance.pages = [MagicMock()] # 1 page
		mock_pdf_reader.return_value = mock_reader_instance
		
		result = PDFService.validate_pdf("test_file_name")
		self.assertEqual(result["page_count"], 1)

	@patch("gpf_builder.services.pdf_service.frappe.get_doc")
	@patch("gpf_builder.services.pdf_service.frappe.db.exists")
	def test_validate_pdf_public_rejected(self, mock_db_exists, mock_get_doc):
		"""
		Proving public PDF is rejected.
		"""
		mock_db_exists.return_value = True
		mock_file = MagicMock()
		mock_file.is_private = False
		mock_get_doc.return_value = mock_file
		
		with self.assertRaises(frappe.PermissionError):
			PDFService.validate_pdf("test_file_name")

	@patch("gpf_builder.services.pdf_service.frappe.get_doc")
	@patch("gpf_builder.services.pdf_service.frappe.db.exists")
	def test_validate_pdf_large_rejected(self, mock_db_exists, mock_get_doc):
		"""
		Proving large PDF (>2MB) is rejected.
		"""
		mock_db_exists.return_value = True
		mock_file = MagicMock()
		mock_file.is_private = True
		mock_file.file_name = "large.pdf"
		mock_file.file_size = 3 * 1024 * 1024 # 3MB
		mock_get_doc.return_value = mock_file
		
		with self.assertRaises(frappe.ValidationError):
			PDFService.validate_pdf("test_file_name")

	@patch("gpf_builder.services.pdf_service.frappe.get_doc")
	@patch("gpf_builder.services.pdf_service.frappe.db.exists")
	@patch("gpf_builder.services.pdf_service.PdfReader")
	@patch("gpf_builder.services.pdf_service.os.path.exists")
	def test_validate_pdf_multi_page_rejected(self, mock_os_exists, mock_pdf_reader, mock_db_exists, mock_get_doc):
		"""
		Proving multi-page PDF is rejected.
		"""
		mock_db_exists.return_value = True
		mock_os_exists.return_value = True
		
		mock_file = MagicMock()
		mock_file.is_private = True
		mock_file.file_name = "multi.pdf"
		mock_file.file_size = 500 * 1024
		mock_file.file_url = "/private/files/multi.pdf"
		mock_get_doc.return_value = mock_file
		
		mock_reader_instance = MagicMock()
		mock_reader_instance.pages = [MagicMock(), MagicMock()] # 2 pages
		mock_pdf_reader.return_value = mock_reader_instance
		
		with self.assertRaises(frappe.ValidationError):
			PDFService.validate_pdf("test_file_name")

	def tearDown(self):
		frappe.db.rollback()
