# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.services.access_control_service import AccessControlService

class TestAccessControl(unittest.TestCase):
	def setUp(self):
		# Create a test user for non-administrator tests
		if not frappe.db.exists("User", "staff@example.com"):
			user = frappe.new_doc("User")
			user.email = "staff@example.com"
			user.first_name = "Staff"
			user.insert(ignore_permissions=True)
		
		# Create a System Manager user
		if not frappe.db.exists("User", "manager@example.com"):
			user = frappe.new_doc("User")
			user.email = "manager@example.com"
			user.first_name = "Manager"
			user.add_roles("System Manager")
			user.insert(ignore_permissions=True)

	def test_guest_rejected(self):
		"""
		Proving Guest is rejected by AccessControlService.
		"""
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			AccessControlService.validate_administrator()

	def test_non_administrator_rejected(self):
		"""
		Proving authenticated non-Administrator users are rejected.
		"""
		frappe.set_user("staff@example.com")
		with self.assertRaises(frappe.PermissionError):
			AccessControlService.validate_administrator()

	def test_system_manager_rejected(self):
		"""
		Proving System Manager is rejected unless the session user is exactly Administrator.
		"""
		frappe.set_user("manager@example.com")
		with self.assertRaises(frappe.PermissionError):
			AccessControlService.validate_administrator()

	def test_administrator_accepted(self):
		"""
		Proving built-in Administrator is accepted.
		"""
		frappe.set_user("Administrator")
		try:
			AccessControlService.validate_administrator()
		except frappe.PermissionError:
			self.fail("AccessControlService.validate_administrator() raised PermissionError unexpectedly!")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()
