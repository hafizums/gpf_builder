# -*- coding: utf-8 -*-
import frappe
import json
import re
from frappe.utils import escape_html
from gpf_builder.services.layout_service import LayoutService
from gpf_builder.services.field_mapping_service import FieldMappingService
from gpf_builder.services.setup_service import SetupService
from gpf_builder.domain.constants import (
	BLOCK_TYPE_STATIC_TEXT,
	BLOCK_TYPE_DYNAMIC_FIELD,
	BLOCK_TYPE_OCR_TEXT,
	BLOCK_TYPE_IMAGE,
	BLOCK_TYPE_BRANDING
)

class PreviewService:
	HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

	@staticmethod
	def generate_preview_html(setup_name, docname=None):
		"""
		Generates a sanitized HTML preview of the current layout.
		Uses the selected Dunning Letter document when provided, otherwise
		injects redacted sample data for placeholders.
		"""
		blocks = LayoutService.get_layout(setup_name)
		target_doctype = SetupService.get_active_setup().target_doctype
		sample_data = PreviewService.get_document_data(target_doctype, docname) if docname else PreviewService.get_redacted_sample_data()
		
		html = [
			PreviewService.get_shared_print_css(),
			'<div class="gpf-preview-root gpf-print-root">'
		]
		
		for block in blocks:
			content = PreviewService._render_block_content(block, sample_data)
			style_dict = json.loads(block.style_json or "{}")
			
			# Combine positional styles with custom styles
			base_styles = {
				"position": "absolute",
				"left": "{0}%".format(block.x),
				"top": "{0}%".format(block.y),
				"width": "{0}%".format(block.width),
				"height": "{0}%".format(block.height),
				"z-index": block.z_index,
				"overflow": "hidden",
				"font-size": "12px",
				"font-family": "Arial",
				"line-height": "1.2",
				"color": "#1f2937",
				"text-align": "left"
			}
			base_styles.update(style_dict)
			
			style_str = "; ".join(["{0}: {1}".format(k, v) for k, v in base_styles.items()])
			
			html.append('<div class="gpf-block gpf-print-block" style="{0}">{1}</div>'.format(style_str, content))
			
		html.append('</div>')
		return "".join(html)

	@staticmethod
	def get_shared_print_css():
		return (
			"<style>\n"
			"  @page {\n"
			"    size: A4;\n"
			"    margin: 0;\n"
			"  }\n"
			"\n"
			"  html,\n"
			"  body {\n"
			"    margin: 0 !important;\n"
			"    padding: 0 !important;\n"
			"  }\n"
			"\n"
			"  .print-format,\n"
			"  .print-format-gutter,\n"
			"  .page-break {\n"
			"    margin: 0 !important;\n"
			"    margin-top: 0mm;\n"
			"    margin-bottom: 0mm;\n"
			"    margin-left: 0mm;\n"
			"    margin-right: 0mm;\n"
			"    padding: 0 !important;\n"
			"    width: 210mm !important;\n"
			"    max-width: none !important;\n"
			"  }\n"
			"\n"
			"  .gpf-print-root {\n"
			"    position: relative;\n"
			"    background: white;\n"
			"    overflow: hidden;\n"
			"  }\n"
			"\n"
			"  .gpf-preview-root {\n"
			"    width: 100%;\n"
			"    height: 0;\n"
			"    padding-bottom: 141.42%;\n"
			"  }\n"
			"\n"
			"  .gpf-output-container {\n"
			"    width: 210mm;\n"
			"    height: 297mm;\n"
			"    padding: 0;\n"
			"  }\n"
			"\n"
			"  .gpf-print-block {\n"
			"    box-sizing: border-box;\n"
			"    overflow: hidden;\n"
			"    vertical-align: top;\n"
			"    overflow-wrap: break-word;\n"
			"  }\n"
			"\n"
			"  .gpf-print-block span {\n"
			"    display: block;\n"
			"    width: 100%;\n"
			"    margin: 0;\n"
			"    padding: 0;\n"
			"    white-space: pre-wrap;\n"
			"    overflow-wrap: break-word;\n"
			"  }\n"
			"\n"
			"  .gpf-print-block img {\n"
			"    width: 100%;\n"
			"    height: 100%;\n"
			"    object-fit: contain;\n"
			"  }\n"
			"</style>"
		)

	@staticmethod
	def _render_block_content(block, sample_data):
		"""
		Renders the inner content of a block based on its type.
		"""
		if block.block_type == BLOCK_TYPE_STATIC_TEXT:
			return PreviewService.render_static_html(block.static_text)
			
		elif block.block_type == BLOCK_TYPE_DYNAMIC_FIELD:
			val = sample_data.get(block.fieldname, "[{0}]".format(block.fieldname))
			return "<span>{0}</span>".format(escape_html(val))
			
		elif block.block_type == BLOCK_TYPE_OCR_TEXT:
			ocr_data = frappe.db.get_value("GPF OCR Result", block.ocr_result, ["normalized_text", "confirmed"], as_dict=True) if block.ocr_result else None
			if ocr_data and ocr_data.confirmed:
				return "<span>{0}</span>".format(escape_html(ocr_data.normalized_text or ""))
			return ""
			
		elif block.block_type == BLOCK_TYPE_IMAGE or block.block_type == BLOCK_TYPE_BRANDING:
			if block.file_reference:
				file_url = frappe.db.get_value("File", block.file_reference, "file_url")
				if not file_url:
					file_url = block.file_reference
				return '<img src="{0}" />'.format(escape_html(file_url))
			return ""
			
		return ""

	@staticmethod
	def render_static_html(value):
		safe_html = LayoutService.sanitize_static_html(value)
		if PreviewService.HTML_TAG_PATTERN.search(safe_html or ""):
			return safe_html
		return "<span>{0}</span>".format(escape_html(safe_html or ""))

	@staticmethod
	def get_document_data(target_doctype, docname):
		if not frappe.db.exists(target_doctype, docname):
			frappe.throw(frappe._("{0} document not found.").format(target_doctype), frappe.DoesNotExistError)

		doc = frappe.get_doc(target_doctype, docname)
		data = {}
		for field in FieldMappingService.get_allowed_fields(target_doctype):
			fieldname = field["fieldname"]
			try:
				data[fieldname] = doc.get_formatted(fieldname)
			except Exception:
				data[fieldname] = frappe.utils.cstr(doc.get(fieldname) or "")
		return data

	@staticmethod
	def get_redacted_sample_data():
		"""
		Returns a set of sample data for Dunning Letter fields.
		Ensures sensitive information is redacted for preview purposes.
		"""
		return {
			"customer_name": "JOHN DOE (REDACTED)",
			"customer": "CUST-00001",
			"posting_date": "2026-05-13",
			"due_date": "2026-05-20",
			"outstanding_amount": "1,234.56",
			"currency": "USD",
			"company": "SAMPLE CORP",
			"contact_display": "REDACTED CONTACT",
			"customer_address": "123 REDACTED STREET, CITY, COUNTRY"
		}
