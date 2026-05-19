# -*- coding: utf-8 -*-
import json

import frappe

from gpf_builder.services.layout_service import LayoutService


class TemplateService:
	@staticmethod
	def parse_blocks(blocks_json):
		try:
			blocks = json.loads(blocks_json or "[]")
		except Exception:
			frappe.throw(frappe._("Invalid template layout payload."), frappe.ValidationError)

		if not isinstance(blocks, list):
			frappe.throw(frappe._("Invalid template layout payload: expected a list of blocks."), frappe.ValidationError)

		return blocks

	@staticmethod
	def normalize_blocks(blocks, target_doctype=None):
		normalized = []
		for index, block_data in enumerate(blocks):
			if not isinstance(block_data, dict):
				frappe.throw(frappe._("Invalid template block at row {0}.").format(index + 1), frappe.ValidationError)

			block_data = dict(block_data)
			block_data["z_index"] = block_data.get("z_index", index)
			block_data = LayoutService.normalize_file_reference(block_data)
			LayoutService.validate_block_data(block_data, target_doctype)
			normalized.append({
				"block_type": block_data.get("block_type") or block_data.get("type"),
				"x": block_data.get("x"),
				"y": block_data.get("y"),
				"width": block_data.get("width"),
				"height": block_data.get("height"),
				"z_index": block_data.get("z_index", index),
				"static_text": block_data.get("static_text"),
				"ocr_result": block_data.get("ocr_result"),
				"fieldname": block_data.get("fieldname"),
				"file_reference": block_data.get("file_reference"),
				"style_json": LayoutService.validate_style_json(block_data.get("style_json"))
			})

		return normalized

	@staticmethod
	def save_template(template_title, target_doctype, blocks):
		template_title = (template_title or "").strip()
		if not template_title:
			frappe.throw(frappe._("Template title is required."), frappe.ValidationError)

		if not target_doctype or not frappe.db.exists("DocType", target_doctype):
			frappe.throw(frappe._("Template target DocType is invalid."), frappe.ValidationError)

		normalized = TemplateService.normalize_blocks(blocks, target_doctype)
		if not normalized:
			frappe.throw(frappe._("Template must contain at least one block."), frappe.ValidationError)

		existing_name = frappe.db.get_value("GPF Layout Template", {
			"template_title": template_title,
			"target_doctype": target_doctype
		})

		if existing_name:
			template = frappe.get_doc("GPF Layout Template", existing_name)
			template.blocks_json = json.dumps(normalized)
			template.save(ignore_permissions=True)
		else:
			template = frappe.get_doc({
				"doctype": "GPF Layout Template",
				"template_title": template_title,
				"target_doctype": target_doctype,
				"blocks_json": json.dumps(normalized)
			})
			template.insert(ignore_permissions=True)

		return {
			"name": template.name,
			"template_title": template.template_title,
			"target_doctype": template.target_doctype,
			"block_count": len(normalized)
		}

	@staticmethod
	def list_templates(target_doctype):
		return frappe.get_all(
			"GPF Layout Template",
			filters={"target_doctype": target_doctype},
			fields=["name", "template_title", "target_doctype", "modified"],
			order_by="modified desc"
		)

	@staticmethod
	def get_template(template_name, target_doctype=None):
		if not template_name or not frappe.db.exists("GPF Layout Template", template_name):
			frappe.throw(frappe._("Layout template not found."), frappe.DoesNotExistError)

		template = frappe.get_doc("GPF Layout Template", template_name)
		if target_doctype and template.target_doctype != target_doctype:
			frappe.throw(
				frappe._("Template is for {0}, not {1}.").format(template.target_doctype, target_doctype),
				frappe.ValidationError
			)

		blocks = TemplateService.parse_blocks(template.blocks_json)
		return template, TemplateService.normalize_blocks(blocks, template.target_doctype)

	@staticmethod
	def delete_template(template_name, target_doctype=None):
		template, _blocks = TemplateService.get_template(template_name, target_doctype)
		frappe.delete_doc("GPF Layout Template", template.name, ignore_permissions=True)
		return template.name
