# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.services.setup_service import SetupService
from gpf_builder.domain.constants import TARGET_DOCTYPE, SETUP_STATUS_EDITING, SETUP_STATUS_FINALIZED

class TestSetupService(unittest.TestCase):
	def setUp(self):
		# Clean up any existing setups
		frappe.db.delete("GPF Print Format Setup")
		frappe.db.commit()

	def test_get_active_setup_success(self):
		"""
		Proving SetupService can retrieve the single active setup.
		"""
		setup = frappe.new_doc("GPF Print Format Setup")
		setup.target_doctype = TARGET_DOCTYPE
		setup.status = SETUP_STATUS_EDITING
		setup.insert(ignore_permissions=True)
		
		retrieved = SetupService.get_active_setup()
		self.assertEqual(retrieved.target_doctype, TARGET_DOCTYPE)

	def test_get_active_setup_not_found(self):
		"""
		Proving SetupService throws an error if no setup exists.
		"""
		with self.assertRaises(frappe.DoesNotExistError):
			SetupService.get_active_setup()

	def test_validate_editing_state(self):
		"""
		Proving SetupService correctly validates the Editing state.
		"""
		setup = frappe.new_doc("GPF Print Format Setup")
		setup.target_doctype = TARGET_DOCTYPE
		setup.status = SETUP_STATUS_EDITING
		
		# Should not throw
		SetupService.validate_editing_state(setup)
		
		# Switch to Finalized
		setup.status = SETUP_STATUS_FINALIZED
		with self.assertRaises(frappe.ValidationError):
			SetupService.validate_editing_state(setup)

	def test_validate_finalized_state(self):
		"""
		Proving SetupService correctly validates the Finalized state.
		"""
		setup = frappe.new_doc("GPF Print Format Setup")
		setup.target_doctype = TARGET_DOCTYPE
		setup.status = SETUP_STATUS_FINALIZED
		
		# Should not throw
		SetupService.validate_finalized_state(setup)
		
		# Switch to Editing
		setup.status = SETUP_STATUS_EDITING
		with self.assertRaises(frappe.ValidationError):
			SetupService.validate_finalized_state(setup)

	def tearDown(self):
		frappe.db.rollback()
