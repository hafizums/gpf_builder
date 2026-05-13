# -*- coding: utf-8 -*-
import frappe
import json
from gpf_builder.gpf_builder.services.layout_service import LayoutService
from gpf_builder.gpf_builder.services.setup_service import SetupService
from gpf_builder.gpf_builder.domain.constants import (
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
		
		# High-resolution A4 container (using normalized percentages)
		html = [
			'<div class="gpf-output-container" style="position: relative; width: 100%; height: 0; padding-bottom: 141.42%; background: white;">'
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
				"z-index": block.z_index
			}
			base_styles.update(style_dict)
			
			style_str = "; ".join(["{0}: {1}".format(k, v) for k, v in base_styles.items()])
			
			html.append('<div class="gpf-block" style="{0}">{1}</div>'.format(style_str, content))
			
		html.append('</div>')
		return "".join(html)

	@staticmethod
	def _render_production_content(block, doc):
		"""
		Renders content using real production data from the document.
		"""
		if block.block_type == BLOCK_TYPE_STATIC_TEXT:
			return block.static_text or ""
			
		elif block.block_type == BLOCK_TYPE_DYNAMIC_FIELD:
			# Get formatted value from Frappe if possible
			val = doc.get(block.fieldname)
			return "<span>{0}</span>".format(frappe.utils.cstr(val) if val is not None else "")
			
		elif block.block_type == BLOCK_TYPE_OCR_TEXT:
			# Only show if result is confirmed
			ocr_data = frappe.db.get_value("GPF OCR Result", block.ocr_result, ["normalized_text", "confirmed"], as_dict=True)
			if ocr_data and ocr_data.confirmed:
				return "<span>{0}</span>".format(ocr_data.normalized_text or "")
			return ""
			
		elif block.block_type == BLOCK_TYPE_IMAGE or block.block_type == BLOCK_TYPE_BRANDING:
			if block.file_reference:
				file_url = frappe.db.get_value("File", block.file_reference, "file_url")
				return '<img src="{0}" style="width:100%; height:100%; object-fit:contain;" />'.format(file_url)
			
		return ""
