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
		Supports Service Account JSON (via SDK) or API Key (via REST).
		"""
		if frappe.conf.get("mock_ocr"):
			return frappe.conf.get("mock_ocr_response") or "Mock OCR result text."

		api_key = frappe.conf.get("google_api_key")
		creds_json = frappe.conf.get("google_vision_credentials")

		if not api_key and not creds_json:
			frappe.throw(frappe._("Google Vision OCR is not configured. Add 'google_api_key' or 'google_vision_credentials' to site config."), ERROR_OCR_NOT_CONFIGURED)

		try:
			if api_key:
				return OCRService._execute_vision_rest_call(content, api_key)
			else:
				return OCRService._execute_vision_sdk_call(content, creds_json)
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "OCR Provider Failure")
			frappe.throw(
				frappe._("OCR Provider failed: {0}").format(str(e)), 
				frappe.ApplicationError,
				ERROR_OCR_PROVIDER_FAILED
			)

	@staticmethod
	def _execute_vision_rest_call(content, api_key):
		"""
		Uses a direct REST call to Google Vision API using an API Key.
		"""
		import requests
		import base64

		# Ensure content is base64 encoded if not already
		if isinstance(content, bytes):
			b64_content = base64.b64encode(content).decode("utf-8")
		else:
			b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

		url = "https://vision.googleapis.com/v1/images:annotate?key={0}".format(api_key)
		payload = {
			"requests": [{
				"image": {"content": b64_content},
				"features": [{"type": "DOCUMENT_TEXT_DETECTION"}]
			}]
		}
		
		response = requests.post(url, json=payload)
		if response.status_code != 200:
			raise Exception("Google Vision REST Error: {0}".format(response.text))
			
		res_json = response.json()
		try:
			return res_json["responses"][0]["fullTextAnnotation"]["text"]
		except (KeyError, IndexError):
			return ""

	@staticmethod
	def _execute_vision_sdk_call(content, creds_json):
		"""
		Uses the Google Cloud Vision SDK with Service Account credentials.
		"""
		from google.cloud import vision
		from google.oauth2 import service_account
		
		info = json.loads(creds_json)
		credentials = service_account.Credentials.from_service_account_info(info)
		client = vision.ImageAnnotatorClient(credentials=credentials)
		
		image = vision.Image(content=content)
		response = client.document_text_detection(image=image)
		
		if response.error.message:
			raise Exception(response.error.message)
			
		return response.full_text_annotation.text
