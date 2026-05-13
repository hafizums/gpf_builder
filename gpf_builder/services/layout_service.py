# -*- coding: utf-8 -*-
import frappe
import json
from gpf_builder.gpf_builder.domain.constants import ERROR_ACCESS_DENIED

class LayoutService:
	# Allowlisted CSS properties for rendering blocks
	# Prevents CSS injection and ensures UI consistency
	ALLOWED_STYLE_PROPERTIES = [
		"font-size", "font-weight", "font-family", "font-style",
		"text-align", "text-decoration", "text-transform",
		"color", "background-color", "opacity",
		"line-height", "letter-spacing", "padding"
	]

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
	def validate_block_data(block_data):
		"""
		Validates block coordinates (0-100) and style JSON.
		"""
		for coord in ["x", "y", "width", "height"]:
			val = float(block_data.get(coord, 0))
			if val < 0 or val > 100:
				frappe.throw(frappe._("Invalid coordinates: {0} must be between 0 and 100.").format(coord), frappe.ValidationError)
		
		# Ensure width + x and height + y don't exceed 100
		if float(block_data.get("x", 0)) + float(block_data.get("width", 0)) > 100:
			frappe.throw(frappe._("Block exceeds horizontal boundary."), frappe.ValidationError)
		if float(block_data.get("y", 0)) + float(block_data.get("height", 0)) > 100:
			frappe.throw(frappe._("Block exceeds vertical boundary."), frappe.ValidationError)

		# 3. Block Type Specifics
		if block_data.get("block_type") == "Static Text":
			text = block_data.get("static_text")
			if not text or not text.strip():
				frappe.throw(frappe._("Static Text block cannot be empty or whitespace only."), frappe.ValidationError)

	@staticmethod
	def create_block(setup_name, block_data):
		"""
		Creates a single layout block.
		"""
		LayoutService.validate_block_data(block_data)
		
		block = frappe.get_doc({
			"doctype": "GPF Layout Block",
			"setup": setup_name,
			"block_type": block_data.get("block_type"),
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
	def update_block(block_name, block_data):
		"""
		Updates an existing layout block.
		"""
		LayoutService.validate_block_data(block_data)
		
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
	def save_layout_blocks(setup_name, blocks):
		"""
		Saves a list of layout blocks for a given setup.
		Overwrites existing blocks for that setup (Atomic Save).
		"""
		# 1. Delete existing blocks for this setup
		frappe.db.delete("GPF Layout Block", {"setup": setup_name})
		
		# 2. Insert new blocks
		created_blocks = []
		for block_data in blocks:
			LayoutService.validate_block_data(block_data)
			
			block = frappe.get_doc({
				"doctype": "GPF Layout Block",
				"setup": setup_name,
				"block_type": block_data.get("block_type"),
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
