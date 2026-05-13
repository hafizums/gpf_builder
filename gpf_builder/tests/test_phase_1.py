import frappe
import unittest
from gpf_builder.patches.create_active_setup import execute as run_patch

class TestPhase1(unittest.TestCase):
	def setUp(self):
		# Ensure we are starting from a clean state for the test
		frappe.db.delete("GPF Print Format Setup", {"target_doctype": "Dunning Letter"})
		frappe.db.commit()

	def test_patch_idempotency(self):
		"""
		Proving repeated migration runs do not create duplicate active setups.
		"""
		# First run
		run_patch()
		count = frappe.db.count("GPF Print Format Setup", {"target_doctype": "Dunning Letter"})
		self.assertEqual(count, 1)

		# Second run
		run_patch()
		count = frappe.db.count("GPF Print Format Setup", {"target_doctype": "Dunning Letter"})
		self.assertEqual(count, 1)

	def test_administrator_only_access(self):
		"""
		Proving only built-in Administrator can read custom DocType records.
		Note: This test assumes standard Frappe permission enforcement is active.
		"""
		from frappe.utils.test_utils import WhiteListTest
		
		# Create a test setup
		run_patch()
		setup_name = frappe.db.get_value("GPF Print Format Setup", {"target_doctype": "Dunning Letter"}, "name")
		
		# Test Guest
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			frappe.get_doc("GPF Print Format Setup", setup_name)

		# Test Non-Administrator
		# Create a test user if not exists
		if not frappe.db.exists("User", "test_user@example.com"):
			user = frappe.new_doc("User")
			user.email = "test_user@example.com"
			user.first_name = "Test User"
			user.add_roles("System Manager") # Even System Manager should be denied
			user.insert(ignore_permissions=True)
		
		frappe.set_user("test_user@example.com")
		with self.assertRaises(frappe.PermissionError):
			frappe.get_doc("GPF Print Format Setup", setup_name)

		# Test Administrator
		frappe.set_user("Administrator")
		doc = frappe.get_doc("GPF Print Format Setup", setup_name)
		self.assertEqual(doc.target_doctype, "Dunning Letter")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()
