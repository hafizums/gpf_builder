# -*- coding: utf-8 -*-
import frappe
import os
from gpf_builder.gpf_builder.domain.constants import ERROR_INVALID_FILE_TYPE, ERROR_PDF_TOO_LARGE, ERROR_PDF_PAGE_COUNT_INVALID

class PDFService:
	# MVP Constraint: 2MB limit for PDF references
	MAX_SIZE_BYTES = 2 * 1024 * 1024

	@staticmethod
	def validate_pdf(file_name):
		"""
		Validate that the provided file is a single-page PDF within size limits.
		Ensures file is private and correctly stored.
		"""
		# 1. Check if File record exists
		if not frappe.db.exists("File", file_name):
			frappe.throw(frappe._("File record not found: {0}").format(file_name), frappe.DoesNotExistError)
		
		file_doc = frappe.get_doc("File", file_name)

		# 2. Security Check: Must be private
		if not file_doc.is_private:
			frappe.throw(
				frappe._("Security Violation: PDF reference must be stored in private storage."), 
				frappe.PermissionError,
				ERROR_ACCESS_DENIED
			)

		# 3. Format Check: Must be PDF
		if not file_doc.file_name.lower().endswith(".pdf"):
			frappe.throw(
				frappe._("Invalid File Type: Only PDF files are allowed for reference."), 
				frappe.ValidationError,
				ERROR_INVALID_FILE_TYPE
			)

		# 4. Size Check
		if file_doc.file_size > PDFService.MAX_SIZE_BYTES:
			frappe.throw(
				frappe._("PDF too large: Reference files must be under 2MB."), 
				frappe.ValidationError,
				ERROR_PDF_TOO_LARGE
			)

		# 5. Page Count Check
		# We use pypdf (standard in Frappe 14) to check page count.
		# If pypdf is missing, we log an error and throw.
		try:
			from pypdf import PdfReader
		except ImportError:
			try:
				from PyPDF2 import PdfReader
			except ImportError:
				frappe.log_error("Missing PDF library (pypdf/PyPDF2)", "GPF Builder PDFService Error")
				frappe.throw(frappe._("Internal Error: PDF processing library not found."))

		file_path = frappe.get_site_path(file_doc.file_url.strip("/"))
		
		# For local development where the file might not be on disk in a mock environment
		if not os.path.exists(file_path):
			# Try absolute path if relative fails
			file_path = frappe.get_site_path("public", "files", file_doc.file_name) if not file_doc.is_private else frappe.get_site_path("private", "files", file_doc.file_name)

		try:
			reader = PdfReader(file_path)
			page_count = len(reader.pages)
		except Exception as e:
			frappe.log_error(str(e), "GPF Builder PDF Parsing Error")
			frappe.throw(frappe._("Failed to read PDF file. It may be corrupted or protected."))

		if page_count != 1:
			frappe.throw(
				frappe._("Invalid PDF: Reference must be exactly 1 page. Found {0} pages.").format(page_count), 
				frappe.ValidationError,
				ERROR_PDF_PAGE_COUNT_INVALID
			)

		return {
			"page_count": page_count,
			"file_size": file_doc.file_size,
			"file_name": file_doc.file_name
		}
