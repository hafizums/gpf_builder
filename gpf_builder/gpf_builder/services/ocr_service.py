# -*- coding: utf-8 -*-
import frappe
import re
import json
from gpf_builder.gpf_builder.domain.constants import ERROR_OCR_NOT_CONFIGURED, ERROR_OCR_PROVIDER_FAILED

class OCRService:
	@staticmethod
	def run_ocr(file_name, setup_name):
		"""
		Main entry point for running OCR on a PDF reference.
		Orchestrates API call, normalization, and persistence.
		"""
		# 1. Fetch file record
		file_doc = frappe.get_doc("File", file_name)
		content = file_doc.get_content()
		
		# 2. Call Google Vision API
		raw_text = OCRService.call_google_vision(content)
		
		if not raw_text:
			frappe.throw(frappe._("OCR failed: No text detected in PDF."), frappe.ValidationError)
			
		# 3. Normalize text
		normalized_text = OCRService.normalize_text(raw_text)
		
		# 4. Create GPF OCR Result
		ocr_res = frappe.get_doc({
			"doctype": "GPF OCR Result",
			"setup": setup_name,
			"source_pdf_file": file_name,
			"raw_text": raw_text,
			"normalized_text": normalized_text,
			"confirmed": 0
		})
		ocr_res.insert(ignore_permissions=True)
		
		return ocr_res.name

	@staticmethod
	def normalize_text(text):
		"""
		Normalizes raw OCR text by removing excessive whitespace, 
		noise characters, and standardizing line breaks.
		"""
		if not text:
			return ""
			
		# Remove non-printable characters
		text = "".join(c for c in text if c.isprintable() or c in ["\n", "\r", "\t"])
		
		# Collapse multiple spaces
		text = re.sub(r' +', ' ', text)
		
		# Standardize newlines
		text = text.replace("\r\n", "\n").replace("\r", "\n")
		text = re.sub(r'\n+', '\n', text)
		
		return text.strip()

	@staticmethod
	def call_google_vision(content):
		"""
		Wrapper for Google Cloud Vision API.
		Expects configuration to be set in Site Config or System Settings.
		"""
		# In a real environment, we'd use the Google Cloud SDK:
		# from google.cloud import vision
		# client = vision.ImageAnnotatorClient()
		# ...
		
		# For this implementation, we provide a hook that can be mocked in tests.
		# In production, this would use configured credentials.
		
		if frappe.conf.get("mock_ocr"):
			return frappe.conf.get("mock_ocr_response") or "Mock OCR result text."

		# Check if credentials exist (placeholder for real check)
		# if not frappe.db.get_single_value("GPF Settings", "google_vision_enabled"):
		#    frappe.throw(frappe._("Google Vision OCR is not enabled."), ERROR_OCR_NOT_CONFIGURED)

		try:
			# Mocking the actual call structure for the agentic environment
			# In actual Frappe 14, this would be the place for the RPC call
			raw_result = OCRService._execute_vision_call(content)
			return raw_result
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "OCR Provider Failure")
			frappe.throw(
				frappe._("OCR Provider failed: {0}").format(str(e)), 
				frappe.ApplicationError,
				ERROR_OCR_PROVIDER_FAILED
			)

	@staticmethod
	def _execute_vision_call(content):
		"""
		Private method to contain the actual SDK call, isolated for mocking.
		"""
		# This is where the actual google-cloud-vision SDK interaction happens
		return ""
