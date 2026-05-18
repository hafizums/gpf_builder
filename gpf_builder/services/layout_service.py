# -*- coding: utf-8 -*-
import frappe
import json
from frappe.utils import sanitize_html
from gpf_builder.domain.constants import (
	BLOCK_TYPE_BRANDING,
	BLOCK_TYPE_DYNAMIC_FIELD,
	BLOCK_TYPE_IMAGE,
	BLOCK_TYPE_OCR_TEXT,
	BLOCK_TYPE_STATIC_TEXT
)
from gpf_builder.services.branding_service import BrandingService
from gpf_builder.services.field_mapping_service import FieldMappingService

class LayoutService:
	# Allowlisted CSS properties for rendering blocks
	# Prevents CSS injection and ensures UI consistency
	ALLOWED_STYLE_PROPERTIES = [
		"font-size", "font-weight", "font-family", "font-style",
		"text-align", "text-align-last", "text-decoration", "text-transform",
		"color", "background-color", "opacity",
		"line-height", "letter-spacing", "padding"
	]

	@staticmethod
	def sanitize_static_html(value):
		return sanitize_html(value or "")

	@staticmethod
	def validate_style_json(style_json):
		"""
		Parses and sanitizes the style JSON.
		Removes any non-allowlisted CSS properties.
		"""
		if not style_json:
			return "{}"
			
		try:
			styles = json.loads(style_json)
			if not isinstance(styles, dict):
				raise ValueError("Style must be a dictionary")
		except (ValueError, TypeError):
			frappe.throw(frappe._("Invalid Style JSON: Must be a valid JSON object."), frappe.ValidationError)

		sanitized = {}
		for prop, value in styles.items():
			if prop.lower() in LayoutService.ALLOWED_STYLE_PROPERTIES:
				# Simple value sanitization: reject if it looks like a script or complex expression
				if isinstance(value, str) and ("javascript:" in value.lower() or "expression(" in value.lower()):
					continue
				sanitized[prop.lower()] = value

		return json.dumps(sanitized)

	@staticmethod
	def validate_block_data(block_data, target_doctype=None):
		"""
		Validates block coordinates (0-100) and style JSON.
		"""
		if "type" in block_data and not block_data.get("block_type"):
			block_data["block_type"] = block_data.get("type")

		block_type = block_data.get("block_type")
		if block_type not in [
			BLOCK_TYPE_STATIC_TEXT,
			BLOCK_TYPE_DYNAMIC_FIELD,
			BLOCK_TYPE_OCR_TEXT,
			BLOCK_TYPE_IMAGE,
			BLOCK_TYPE_BRANDING
		]:
			frappe.throw(frappe._("Invalid block type: {0}").format(block_type), frappe.ValidationError)

		for coord in ["x", "y", "width", "height"]:
			val = float(block_data.get(coord, 0))
			if val < 0 or val > 100:
				frappe.throw(frappe._("Invalid coordinates: {0} must be between 0 and 100.").format(coord), frappe.ValidationError)

		if float(block_data.get("width", 0)) <= 0 or float(block_data.get("height", 0)) <= 0:
			frappe.throw(frappe._("Block width and height must be greater than zero."), frappe.ValidationError)
		
		# Ensure width + x and height + y don't exceed 100
		if float(block_data.get("x", 0)) + float(block_data.get("width", 0)) > 100:
			frappe.throw(frappe._("Block exceeds horizontal boundary."), frappe.ValidationError)
		if float(block_data.get("y", 0)) + float(block_data.get("height", 0)) > 100:
			frappe.throw(frappe._("Block exceeds vertical boundary."), frappe.ValidationError)

		# 3. Block Type Specifics
		if block_type == BLOCK_TYPE_STATIC_TEXT:
			text = LayoutService.sanitize_static_html(block_data.get("static_text"))
			block_data["static_text"] = text
			if not text or not text.strip():
				frappe.throw(frappe._("Static Text block cannot be empty or whitespace only."), frappe.ValidationError)

		if block_type == BLOCK_TYPE_DYNAMIC_FIELD and not FieldMappingService.validate_fieldname(block_data.get("fieldname"), target_doctype):
			frappe.throw(frappe._("Dynamic Field block uses an invalid fieldname."), frappe.ValidationError)

		if block_type == BLOCK_TYPE_OCR_TEXT and block_data.get("ocr_result"):
			if not frappe.db.exists("GPF OCR Result", block_data.get("ocr_result")):
				frappe.throw(frappe._("OCR Result not found: {0}").format(block_data.get("ocr_result")), frappe.DoesNotExistError)

		if block_type in [BLOCK_TYPE_IMAGE, BLOCK_TYPE_BRANDING] and block_data.get("file_reference"):
			BrandingService.validate_image(block_data.get("file_reference"))

	@staticmethod
	def normalize_file_reference(block_data):
		if block_data.get("block_type") in [BLOCK_TYPE_IMAGE, BLOCK_TYPE_BRANDING] and block_data.get("file_reference"):
			block_data["file_reference"] = BrandingService.get_file_doc(block_data.get("file_reference")).name
		return block_data

	@staticmethod
	def create_block(setup_name, block_data, target_doctype=None):
		"""
		Creates a single layout block.
		"""
		block_data = LayoutService.normalize_file_reference(block_data)
		LayoutService.validate_block_data(block_data, target_doctype)
		
		block = frappe.get_doc({
			"doctype": "GPF Layout Block",
			"setup": setup_name,
			"block_type": block_data.get("block_type") or block_data.get("type"),
			"x": block_data.get("x"),
			"y": block_data.get("y"),
			"width": block_data.get("width"),
			"height": block_data.get("height"),
			"z_index": block_data.get("z_index", 0),
			"static_text": block_data.get("static_text"),
			"ocr_result": block_data.get("ocr_result"),
			"fieldname": block_data.get("fieldname"),
			"file_reference": block_data.get("file_reference"),
			"style_json": LayoutService.validate_style_json(block_data.get("style_json"))
		})
		block.insert(ignore_permissions=True)
		return block.name

	@staticmethod
	def update_block(block_name, block_data, target_doctype=None):
		"""
		Updates an existing layout block.
		"""
		block_data = LayoutService.normalize_file_reference(block_data)
		LayoutService.validate_block_data(block_data, target_doctype)
		
		block = frappe.get_doc("GPF Layout Block", block_name)
		block.update({
			"block_type": block_data.get("block_type", block.block_type),
			"x": block_data.get("x", block.x),
			"y": block_data.get("y", block.y),
			"width": block_data.get("width", block.width),
			"height": block_data.get("height", block.height),
			"z_index": block_data.get("z_index", block.z_index),
			"static_text": block_data.get("static_text", block.static_text),
			"ocr_result": block_data.get("ocr_result", block.ocr_result),
			"fieldname": block_data.get("fieldname", block.fieldname),
			"file_reference": block_data.get("file_reference", block.file_reference),
			"style_json": LayoutService.validate_style_json(block_data.get("style_json", block.style_json))
		})
		block.save(ignore_permissions=True)
		return block.name

	@staticmethod
	def delete_block(block_name):
		"""
		Deletes a layout block.
		"""
		frappe.delete_doc("GPF Layout Block", block_name, ignore_permissions=True)

	@staticmethod
	def duplicate_block(block_name):
		"""
		Duplicates a layout block with a slight offset.
		"""
		source = frappe.get_doc("GPF Layout Block", block_name)
		new_block = frappe.copy_doc(source)
		
		# Offset for visual clarity in UI
		new_block.x = min(100, float(new_block.x) + 2)
		new_block.y = min(100, float(new_block.y) + 2)
		
		new_block.insert(ignore_permissions=True)
		return new_block.name

	@staticmethod
	def save_layout_blocks(setup_name, blocks, target_doctype=None):
		"""
		Saves a list of layout blocks for a given setup.
		Overwrites existing blocks for that setup (Atomic Save).
		"""
		# 1. Delete existing blocks for this setup
		frappe.db.delete("GPF Layout Block", {"setup": setup_name})
		
		# 2. Insert new blocks
		created_blocks = []
		for block_data in blocks:
			block_data = LayoutService.normalize_file_reference(block_data)
			LayoutService.validate_block_data(block_data, target_doctype)
			
			block = frappe.get_doc({
				"doctype": "GPF Layout Block",
			"setup": setup_name,
			"block_type": block_data.get("block_type") or block_data.get("type"),
				"x": block_data.get("x"),
				"y": block_data.get("y"),
				"width": block_data.get("width"),
				"height": block_data.get("height"),
				"z_index": block_data.get("z_index", 0),
				"static_text": block_data.get("static_text"),
				"ocr_result": block_data.get("ocr_result"),
				"fieldname": block_data.get("fieldname"),
				"file_reference": block_data.get("file_reference"),
				"style_json": LayoutService.validate_style_json(block_data.get("style_json"))
			})
			block.insert(ignore_permissions=True)
			created_blocks.append(block.name)
			
		return created_blocks

	@staticmethod
	def get_layout(setup_name):
		"""
		Retrieves all layout blocks for a given setup, sorted by z-index.
		"""
		return frappe.get_all("GPF Layout Block", 
			filters={"setup": setup_name}, 
			fields=["*"],
			order_by="z_index asc"
		)
