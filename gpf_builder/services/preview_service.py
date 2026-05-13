# -*- coding: utf-8 -*-
import frappe
import json
from gpf_builder.gpf_builder.services.layout_service import LayoutService
from gpf_builder.gpf_builder.domain.constants import (
	BLOCK_TYPE_STATIC_TEXT,
	BLOCK_TYPE_DYNAMIC_FIELD,
	BLOCK_TYPE_OCR_TEXT,
	BLOCK_TYPE_IMAGE,
	BLOCK_TYPE_BRANDING
)

class PreviewService:
	@staticmethod
	def generate_preview_html(setup_name):
		"""
		Generates a sanitized HTML preview of the current layout.
		Injects redacted sample data for Dunning Letter placeholders.
		"""
		blocks = LayoutService.get_layout(setup_name)
		sample_data = PreviewService.get_redacted_sample_data()
		
		# Base container mimics an A4 page aspect ratio (roughly 1:1.41)
		html = [
			'<style>.gpf-preview-root { position: relative; width: 100%; height: auto; aspect-ratio: 1 / 1.414; background: white; border: 1px solid #ccc; overflow: hidden; }</style>',
			'<div class="gpf-preview-root">'
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
				"overflow": "hidden"
			}
			base_styles.update(style_dict)
			
			style_str = "; ".join(["{0}: {1}".format(k, v) for k, v in base_styles.items()])
			
			html.append('<div class="gpf-block" style="{0}">{1}</div>'.format(style_str, content))
			
		html.append('</div>')
		return "".join(html)

	@staticmethod
	def _render_block_content(block, sample_data):
		"""
		Renders the inner content of a block based on its type.
		"""
		if block.block_type == BLOCK_TYPE_STATIC_TEXT:
			return block.static_text or ""
			
		elif block.block_type == BLOCK_TYPE_DYNAMIC_FIELD:
			val = sample_data.get(block.fieldname, "[{0}]".format(block.fieldname))
			return "<span>{0}</span>".format(val)
			
		elif block.block_type == BLOCK_TYPE_OCR_TEXT:
			# For preview, we show the normalized text if available
			normalized_text = frappe.db.get_value("GPF OCR Result", block.ocr_result, "normalized_text") if block.ocr_result else ""
			return "<span>{0}</span>".format(normalized_text or "[OCR Text]")
			
		elif block.block_type == BLOCK_TYPE_IMAGE or block.block_type == BLOCK_TYPE_BRANDING:
			if block.file_reference:
				file_url = frappe.db.get_value("File", block.file_reference, "file_url")
				return '<img src="{0}" style="width:100%; height:100%; object-fit:contain;" />'.format(file_url)
			return "[Image Placeholder]"
			
		return ""

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
