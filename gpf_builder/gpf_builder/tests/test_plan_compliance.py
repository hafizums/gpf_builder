# -*- coding: utf-8 -*-
import frappe
import unittest
import json
from gpf_builder.gpf_builder.services.layout_service import LayoutService
from gpf_builder.gpf_builder.services.finalization_service import FinalizationService
from gpf_builder.gpf_builder.services.branding_service import BrandingService
from gpf_builder.gpf_builder.services.ocr_service import OCRService
from gpf_builder.gpf_builder.services.output_service import OutputService

class TestPlanCompliance(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.setup = frappe.new_doc("GPF Print Format Setup")
		self.setup.target_doctype = "Dunning Letter"
		self.setup.insert(ignore_permissions=True)

	def test_ut_017_blank_spacer_rejection(self):
		"""
		Proving that blank spacer blocks are rejected.
		"""
		data = {"block_type": "Static Text", "static_text": "  ", "x": 0, "y": 0, "width": 10, "height": 10}
		with self.assertRaises(frappe.ValidationError):
			LayoutService.validate_block_data(data)

	def test_ut_021_duplicate_field_allowed(self):
		"""
		Proving that the same field can be used in multiple blocks.
		"""
		data = {"block_type": "Dynamic Field", "fieldname": "customer_name", "x": 0, "y": 0, "width": 10, "height": 10}
		# Should not raise error
		LayoutService.validate_block_data(data)
		LayoutService.validate_block_data(data)

	def test_ut_029_svg_strict_sanitization(self):
		"""
		Proving rejection of event handlers and foreignObject in SVG.
		"""
		unsafe_svg = '<svg><foreignObject>Unsafe</foreignObject></svg>'
		with self.assertRaises(frappe.ValidationError):
			BrandingService.validate_branding_asset("test.svg", unsafe_svg)
			
		onload_svg = '<svg onload="alert(1)"></svg>'
		with self.assertRaises(frappe.ValidationError):
			BrandingService.validate_branding_asset("test.svg", onload_svg)

	def test_it_013_ocr_not_configured_safe_failure(self):
		"""
		Proving OCR fails safely with OCR_NOT_CONFIGURED if credentials are missing.
		"""
		# Simulate missing config
		frappe.conf.google_vision_credentials = None
		with self.assertRaises(frappe.ValidationError) as cm:
			OCRService.run_ocr("test.pdf", self.setup.name)
		self.assertIn("OCR_NOT_CONFIGURED", str(cm.exception))

	def test_ut_018_overlapping_blocks_blocked(self):
		"""
		Proving that finalization is blocked if blocks overlap.
		Note: This requires a specialized validation in FinalizationService.
		"""
		# Add two overlapping blocks
		LayoutService.create_block(self.setup.name, {"block_type":"Static Text", "static_text":"A", "x":0, "y":0, "width":20, "height":20})
		LayoutService.create_block(self.setup.name, {"block_type":"Static Text", "static_text":"B", "x":10, "y":10, "width":20, "height":20})
		
		# I need to implement the overlap check in FinalizationService first
		# For now, this test identifies the missing requirement in the implementation
		# I will implement the overlap check in the next step.
		with self.assertRaises(frappe.ValidationError):
			FinalizationService.finalize_setup(self.setup.name)

	def tearDown(self):
		frappe.db.rollback()
