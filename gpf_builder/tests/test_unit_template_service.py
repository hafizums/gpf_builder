# -*- coding: utf-8 -*-
import frappe
import json
import unittest

from gpf_builder.api.api import (
	delete_layout_template,
	list_layout_templates,
	load_layout_template,
	save_layout_template
)
from gpf_builder.domain.constants import SETUP_STATUS_EDITING
from gpf_builder.services.layout_service import LayoutService
from gpf_builder.services.setup_service import SetupService
from gpf_builder.services.template_service import TemplateService


class TestTemplateService(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.setup = SetupService.get_active_setup()
		self.setup.target_doctype = "Dunning Letter"
		self.setup.status = SETUP_STATUS_EDITING
		self.setup.save(ignore_permissions=True)
		frappe.db.delete("GPF Layout Block", {"setup": self.setup.name})
		frappe.db.delete("GPF Layout Template", {"target_doctype": self.setup.target_doctype})

	def test_save_and_load_template_snapshot(self):
		"""
		Proving templates persist normalized blocks and can restore a layout.
		"""
		blocks = [{
			"block_type": "Static Text",
			"static_text": "Template Body",
			"x": 5,
			"y": 6,
			"width": 40,
			"height": 8,
			"style_json": '{"font-size": "13px"}'
		}]

		result = TemplateService.save_template("Approval Table", self.setup.target_doctype, blocks)
		self.assertTrue(frappe.db.exists("GPF Layout Template", result["name"]))

		template, loaded_blocks = TemplateService.get_template(result["name"], self.setup.target_doctype)
		self.assertEqual(template.template_title, "Approval Table")
		self.assertEqual(len(loaded_blocks), 1)
		self.assertEqual(loaded_blocks[0]["static_text"], "Template Body")

		LayoutService.save_layout_blocks(self.setup.name, loaded_blocks, self.setup.target_doctype)
		self.assertTrue(frappe.db.exists("GPF Layout Block", {
			"setup": self.setup.name,
			"static_text": "Template Body"
		}))

	def test_template_target_doctype_is_enforced(self):
		"""
		Proving templates cannot be loaded into a different target DocType.
		"""
		result = TemplateService.save_template("Wrong Target", self.setup.target_doctype, [{
			"block_type": "Static Text",
			"static_text": "Body",
			"x": 0,
			"y": 0,
			"width": 10,
			"height": 10
		}])

		with self.assertRaises(frappe.ValidationError):
			TemplateService.get_template(result["name"], "Sales Invoice")

	def test_template_api_round_trip(self):
		"""
		Proving the whitelisted template API can save, list, load, and delete.
		"""
		blocks = [{
			"block_type": "Static Text",
			"static_text": "API Template Body",
			"x": 1,
			"y": 2,
			"width": 30,
			"height": 5
		}]

		result = save_layout_template("API Template", json.dumps(blocks))
		template_name = result["template"]["name"]

		templates = list_layout_templates()
		self.assertTrue(any(template.name == template_name for template in templates))

		load_layout_template(template_name)
		self.assertTrue(frappe.db.exists("GPF Layout Block", {
			"setup": self.setup.name,
			"static_text": "API Template Body"
		}))

		delete_layout_template(template_name)
		self.assertFalse(frappe.db.exists("GPF Layout Template", template_name))

	def tearDown(self):
		frappe.db.rollback()
