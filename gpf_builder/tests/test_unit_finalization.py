# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.services.finalization_service import FinalizationService
from gpf_builder.services.layout_service import LayoutService
from gpf_builder.domain.constants import SETUP_STATUS_FINALIZED, SETUP_STATUS_EDITING

class TestFinalization(unittest.TestCase):
	def setUp(self):
		# Create setup
		self.setup = frappe.new_doc("GPF Print Format Setup")
		self.setup.target_doctype = "Dunning Letter"
		self.setup.status = SETUP_STATUS_EDITING
		self.setup.insert(ignore_permissions=True)

	def test_finalize_no_blocks_fails(self):
		"""
		Proving that finalization fails if there are no blocks.
		"""
		with self.assertRaises(frappe.ValidationError):
			FinalizationService.finalize_setup(self.setup.name)

	def test_finalize_success(self):
		"""
		Proving successful finalization transition.
		"""
		# Add a block
		LayoutService.create_block(self.setup.name, {
			"block_type": "Static Text",
			"static_text": "Content",
			"x": 0, "y": 0, "width": 10, "height": 10
		})
		
		FinalizationService.finalize_setup(self.setup.name)
		
		status = frappe.db.get_value("GPF Print Format Setup", self.setup.name, "status")
		self.assertEqual(status, SETUP_STATUS_FINALIZED)
		
		# Verify snapshot created
		self.assertTrue(frappe.db.exists("GPF Version History", {"setup": self.setup.name, "event_type": "Finalize"}))

	def test_finalize_allows_punctuation_static_text_overlap(self):
		"""
		Punctuation labels such as ':' may overlap a field block slightly in
		real print layouts and should not block finalization.
		"""
		LayoutService.create_block(self.setup.name, {
			"block_type": "Static Text",
			"static_text": ":",
			"x": 0, "y": 0, "width": 5, "height": 5
		})
		LayoutService.create_block(self.setup.name, {
			"block_type": "Dynamic Field",
			"fieldname": "customer",
			"x": 2, "y": 0, "width": 10, "height": 5
		})

		FinalizationService.finalize_setup(self.setup.name)

		status = frappe.db.get_value("GPF Print Format Setup", self.setup.name, "status")
		self.assertEqual(status, SETUP_STATUS_FINALIZED)

	def test_finalize_allows_media_overlap(self):
		"""
		Image and Branding blocks may intentionally overlap other final print content.
		"""
		self.assertTrue(FinalizationService.is_allowed_overlap(
			frappe._dict({"block_type": "Image"}),
			frappe._dict({"block_type": "Static Text", "static_text": "Header"})
		))
		self.assertTrue(FinalizationService.is_allowed_overlap(
			frappe._dict({"block_type": "Dynamic Field", "fieldname": "customer"}),
			frappe._dict({"block_type": "Branding"})
		))

	def test_return_to_editing(self):
		"""
		Proving transition back to editing.
		"""
		# Force finalized
		frappe.db.set_value("GPF Print Format Setup", self.setup.name, "status", SETUP_STATUS_FINALIZED)
		
		FinalizationService.return_to_editing(self.setup.name)
		
		status = frappe.db.get_value("GPF Print Format Setup", self.setup.name, "status")
		self.assertEqual(status, SETUP_STATUS_EDITING)

	def tearDown(self):
		frappe.db.rollback()
