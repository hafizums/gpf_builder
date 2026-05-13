# -*- coding: utf-8 -*-
import frappe
import unittest
from unittest.mock import patch, MagicMock
from gpf_builder.services.ocr_service import OCRService

class TestOCRService(unittest.TestCase):
	def test_normalize_text(self):
		"""
		Proving that OCR text normalization removes noise and collapses whitespace.
		"""
		raw = "  Hello   \n\n  World!  \r\n  Test.  "
		expected = "Hello\nWorld!\nTest."
		self.assertEqual(OCRService.normalize_text(raw), expected)
		
		# Test non-printable chars
		raw_with_noise = "Hello\x00World"
		self.assertEqual(OCRService.normalize_text(raw_with_noise), "HelloWorld")

	@patch("gpf_builder.services.ocr_service.OCRService.call_google_vision")
	@patch("gpf_builder.services.ocr_service.frappe.get_doc")
	def test_run_ocr_persistence(self, mock_get_doc, mock_call_vision):
		"""
		Proving that OCR results are correctly saved to the database.
		"""
		mock_call_vision.return_value = "Raw detected text"
		
		mock_file = MagicMock()
		mock_file.get_content.return_value = b"fake pdf data"
		mock_get_doc.return_value = mock_file
		
		setup_name = "GPF-20260513-001"
		ocr_name = OCRService.run_ocr("test.pdf", setup_name)
		
		ocr_doc = frappe.get_doc("GPF OCR Result", ocr_name)
		self.assertEqual(ocr_doc.raw_text, "Raw detected text")
		self.assertEqual(ocr_doc.normalized_text, "Raw detected text")
		self.assertEqual(ocr_doc.setup, setup_name)
		self.assertEqual(ocr_doc.confirmed, 0)

	def tearDown(self):
		frappe.db.rollback()
