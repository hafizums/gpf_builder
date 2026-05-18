# -*- coding: utf-8 -*-
import frappe
import json
from frappe.utils import escape_html
from gpf_builder.services.layout_service import LayoutService
from gpf_builder.services.setup_service import SetupService
from gpf_builder.services.preview_service import PreviewService
from gpf_builder.domain.constants import (
	BLOCK_TYPE_STATIC_TEXT,
	BLOCK_TYPE_DYNAMIC_FIELD,
	BLOCK_TYPE_OCR_TEXT,
	BLOCK_TYPE_IMAGE,
	BLOCK_TYPE_BRANDING
)

class OutputService:
	@staticmethod
	def generate_final_html(doc):
		"""
		Generates the production HTML for a Dunning Letter based on the finalized setup.
		Designed to be called within a custom Frappe Print Format.
		'doc' is the Dunning Letter document instance.
		"""
		setup = SetupService.get_active_setup()
		
		# SECURITY: Only allow output if setup is finalized
		SetupService.validate_finalized_state(setup)
		
		blocks = LayoutService.get_layout(setup.name)
		
		html = [
			PreviewService.get_shared_print_css(),
			'<div class="gpf-output-container gpf-print-root">'
		]
		
		for block in blocks:
			content = OutputService._render_production_content(block, doc)
			style_dict = json.loads(block.style_json or "{}")
			
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
			
			style_str = OutputService.format_inline_style(base_styles)
			
			html.append('<div class="gpf-block gpf-print-block" style="{0}">{1}</div>'.format(style_str, content))
			
		html.append('</div>')
		return "".join(html)

	@staticmethod
	def format_inline_style(styles):
		return "; ".join(["{0}: {1}".format(k, v) for k, v in styles.items()])

	@staticmethod
	def _render_production_content(block, doc):
		"""
		Renders content using real production data from the document.
		"""
		if block.block_type == BLOCK_TYPE_STATIC_TEXT:
			return PreviewService.render_static_html(block.static_text)
			
		elif block.block_type == BLOCK_TYPE_DYNAMIC_FIELD:
			try:
				val = doc.get_formatted(block.fieldname)
			except Exception:
				val = frappe.utils.cstr(doc.get(block.fieldname) if hasattr(doc, "get") else "")
			return "<span>{0}</span>".format(escape_html(val if val is not None else ""))
			
		elif block.block_type == BLOCK_TYPE_OCR_TEXT:
			# Only show if result is confirmed
			ocr_data = frappe.db.get_value("GPF OCR Result", block.ocr_result, ["normalized_text", "confirmed"], as_dict=True)
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
