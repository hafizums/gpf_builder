# -*- coding: utf-8 -*-
import frappe
import re
from gpf_builder.gpf_builder.domain.constants import ALLOWED_BRANDING_EXTENSIONS, ERROR_INVALID_FILE_TYPE

class BrandingService:
	# MVP Constraint: 1MB limit for branding assets
	MAX_SIZE_BYTES = 1 * 1024 * 1024

	@staticmethod
	def validate_image(file_name):
		"""
		Validates a branding image asset (Logo, Signature, etc).
		Checks for allowed extensions, size limits, and sanitizes SVG content.
		"""
		if not frappe.db.exists("File", file_name):
			frappe.throw(frappe._("File record not found: {0}").format(file_name), frappe.DoesNotExistError)
			
		file_doc = frappe.get_doc("File", file_name)
		
		# 1. Extension Check
		ext = "." + file_doc.file_name.split(".")[-1].lower()
		if ext not in ALLOWED_BRANDING_EXTENSIONS:
			frappe.throw(
				frappe._("Invalid image type: {0}. Allowed: {1}").format(ext, ", ".join(ALLOWED_BRANDING_EXTENSIONS)), 
				frappe.ValidationError,
				ERROR_INVALID_FILE_TYPE
			)

		# 2. Size Check
		if file_doc.file_size > BrandingService.MAX_SIZE_BYTES:
			frappe.throw(
				frappe._("Branding asset too large: Images must be under 1MB."), 
				frappe.ValidationError
			)

		# 3. SVG Sanitization
		if ext == ".svg":
			BrandingService.sanitize_svg(file_doc)

		return True

	@staticmethod
	def sanitize_svg(file_doc):
		"""
		Strictly sanitizes SVG content to prevent XSS.
		Rejects any SVG containing <script> tags or 'on*' event handlers.
		"""
		content = file_doc.get_content()
		if isinstance(content, bytes):
			try:
				content = content.decode("utf-8")
			except UnicodeDecodeError:
				frappe.throw(frappe._("Invalid SVG encoding."))

		content_lower = content.lower()
		
		# Pattern 1: Script tags
		if "<script" in content_lower:
			frappe.throw(frappe._("Security Error: SVG contains forbidden <script> tags."), frappe.SecurityError)
			
		# Pattern 2: Event handlers (onclick, onload, etc)
		if re.search(r'\son\w+\s*=', content_lower):
			frappe.throw(frappe._("Security Error: SVG contains forbidden event handlers."), frappe.SecurityError)
			
		# Pattern 3: External references (optional but recommended for high security)
		# For MVP, we stick to the core script/event restrictions.
		
		return True
