# -*- coding: utf-8 -*-
import frappe
from gpf_builder.gpf_builder.domain.constants import ERROR_ACCESS_DENIED

class ValidationService:
	@staticmethod
	def validate_setup_scope(doc_type, doc_name, setup_name):
		"""
		Ensure that a document (e.g., OCR Result, Layout Block) belongs to the specified setup.
		Prevents object-level authorization bypass and cross-setup access.
		"""
		if not doc_name:
			return

		actual_setup = frappe.db.get_value(doc_type, doc_name, "setup")
		if actual_setup != setup_name:
			frappe.throw(
				frappe._("Access denied: The requested {0} does not belong to setup {1}.").format(doc_type, setup_name),
				frappe.PermissionError,
				ERROR_ACCESS_DENIED
			)

	@staticmethod
	def validate_file_scope(file_name, setup_name):
		"""
		Ensure that a Frappe File is either the PDF reference of the setup 
		or is otherwise allowed (e.g., in a layout block belonging to the setup).
		"""
		if not file_name:
			return

		# Check if it is the primary PDF reference
		pdf_file = frappe.db.get_value("GPF Print Format Setup", setup_name, "pdf_reference_file")
		if file_name == pdf_file:
			return

		# Check if it is used in a layout block belonging to this setup
		if frappe.db.exists("GPF Layout Block", {"setup": setup_name, "file_reference": file_name}):
			return

		frappe.throw(
			frappe._("Access denied: The requested file is not associated with the active setup."),
			frappe.PermissionError,
			ERROR_ACCESS_DENIED
		)
