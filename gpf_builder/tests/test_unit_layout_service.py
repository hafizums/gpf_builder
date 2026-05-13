# -*- coding: utf-8 -*-
import frappe
import unittest
import json
from gpf_builder.gpf_builder.services.layout_service import LayoutService

class TestLayoutService(unittest.TestCase):
	def test_validate_style_json_sanitization(self):
		"""
		Proving that only allowlisted CSS properties are preserved.
		"""
		unsafe_style = json.dumps({
			"font-size": "14px",
			"color": "red",
			"position": "absolute", # Not in allowlist
			"background-image": "url('javascript:alert(1)')" # Not in allowlist
		})
		
		sanitized_json = LayoutService.validate_style_json(unsafe_style)
		sanitized = json.loads(sanitized_json)
		
		self.assertIn("font-size", sanitized)
		self.assertIn("color", sanitized)
		self.assertNotIn("position", sanitized)
		self.assertNotIn("background-image", sanitized)

	def test_boundary_validation(self):
		"""
		Proving that blocks cannot exceed setup boundaries.
		"""
		data = {
			"x": 90,
			"y": 90,
			"width": 15, # 90 + 15 > 100
			"height": 5
		}
		with self.assertRaises(frappe.ValidationError):
			LayoutService.validate_block_data(data)

	def test_individual_operations(self):
		"""
		Proving individual block operations (create, update, delete, duplicate).
		"""
		setup_name = "GPF-20260513-001"
		data = {
			"block_type": "Static Text",
			"x": 10, "y": 10, "width": 20, "height": 10
		}
		
		# Create
		name = LayoutService.create_block(setup_name, data)
		self.assertTrue(frappe.db.exists("GPF Layout Block", name))
		
		# Update
		LayoutService.update_block(name, {"width": 30})
		self.assertEqual(frappe.db.get_value("GPF Layout Block", name, "width"), 30)
		
		# Duplicate
		dup_name = LayoutService.duplicate_block(name)
		dup_doc = frappe.get_doc("GPF Layout Block", dup_name)
		self.assertEqual(dup_doc.width, 30)
		self.assertEqual(dup_doc.x, 12) # 10 + 2 offset
		
		# Delete
		LayoutService.delete_block(name)
		self.assertFalse(frappe.db.exists("GPF Layout Block", name))

	def tearDown(self):
		frappe.db.rollback()
