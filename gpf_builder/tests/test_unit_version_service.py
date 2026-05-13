# -*- coding: utf-8 -*-
import frappe
import unittest
import json
from gpf_builder.services.version_service import VersionService

class TestVersionService(unittest.TestCase):
	def setUp(self):
		# Create setup
		self.setup = frappe.new_doc("GPF Print Format Setup")
		self.setup.target_doctype = "Dunning Letter"
		self.setup.insert(ignore_permissions=True)
		
		# Create a block
		self.block = frappe.new_doc("GPF Layout Block")
		self.block.setup = self.setup.name
		self.block.block_type = "Static Text"
		self.block.x = 10
		self.block.y = 10
		self.block.width = 20
		self.block.height = 5
		self.block.insert(ignore_permissions=True)

	def test_create_snapshot_increment(self):
		"""
		Proving that version numbers increment correctly for each snapshot.
		"""
		v1 = VersionService.create_snapshot(self.setup.name, "Save", "First save")
		self.assertEqual(v1, 1)
		
		v2 = VersionService.create_snapshot(self.setup.name, "Save", "Second save")
		self.assertEqual(v2, 2)

	def test_snapshot_integrity(self):
		"""
		Proving that the snapshot contains the correct layout data.
		"""
		VersionService.create_snapshot(self.setup.name, "Finalize")
		
		snapshot = VersionService.get_snapshot(self.setup.name, 1)
		self.assertEqual(len(snapshot), 1)
		self.assertEqual(snapshot[0]["block_type"], "Static Text")
		self.assertEqual(float(snapshot[0]["x"]), 10.0)

	def tearDown(self):
		frappe.db.rollback()
