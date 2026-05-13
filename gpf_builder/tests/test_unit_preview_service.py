# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.services.preview_service import PreviewService
from gpf_builder.services.layout_service import LayoutService

class TestPreviewService(unittest.TestCase):
	def setUp(self):
		# Create setup
		self.setup = frappe.new_doc("GPF Print Format Setup")
		self.setup.target_doctype = "Dunning Letter"
		self.setup.insert(ignore_permissions=True)
		
		# Create a few blocks
		LayoutService.create_block(self.setup.name, {
			"block_type": "Static Text",
			"static_text": "Hello World",
			"x": 10, "y": 10, "width": 20, "height": 5
		})
		
		LayoutService.create_block(self.setup.name, {
			"block_type": "Dynamic Field",
			"fieldname": "customer_name",
			"x": 10, "y": 20, "width": 30, "height": 5
		})

	def test_generate_preview_structure(self):
		"""
		Proving that PreviewService generates a valid HTML structure with blocks.
		"""
		html = PreviewService.generate_preview_html(self.setup.name)
		
		self.assertIn("gpf-preview-root", html)
		self.assertIn("Hello World", html)
		self.assertIn("position: absolute", html)
		self.assertIn("left: 10%", html)

	def test_sample_data_redaction(self):
		"""
		Proving that PreviewService uses redacted sample data.
		"""
		html = PreviewService.generate_preview_html(self.setup.name)
		self.assertIn("REDACTED", html)

	def tearDown(self):
		frappe.db.rollback()
