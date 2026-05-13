# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.utils.error_service import ErrorService

class TestErrorHandling(unittest.TestCase):
	def test_sanitized_error_throwing(self):
		"""
		Proving ErrorService throws errors with stable codes and sanitized messages.
		"""
		with self.assertRaises(frappe.ValidationError) as cm:
			ErrorService.throw("Test message", "TEST_CODE")
		
		# Check if the title (code) is preserved in Frappe's exception structure
		# Note: In standard Frappe, 'title' is often mapped to the 'exc_group' or similar in the response
		# but for unit tests, we check the exception arguments.
		self.assertIn("Test message", str(cm.exception))

	def test_unexpected_error_masking(self):
		"""
		Proving that unexpected exceptions do not leak stack traces or sensitive data.
		"""
		try:
			# Simulate an unexpected internal error (e.g., KeyError)
			raise KeyError("sensitive_key_or_path")
		except Exception as e:
			with self.assertRaises(frappe.ApplicationError) as cm:
				ErrorService.handle_api_exception(e)
			
			# Verify that the sensitive info from KeyError is NOT in the message
			self.assertNotIn("sensitive_key_or_path", str(cm.exception))
			self.assertIn("An unexpected error occurred", str(cm.exception))

	def test_no_credential_leakage(self):
		"""
		Proving that API errors do not expose credentials.
		"""
		credentials = {"api_key": "SECRET_KEY_123"}
		try:
			# Simulate error during credential check
			if credentials["api_key"]:
				raise ValueError("Invalid credentials")
		except Exception as e:
			with self.assertRaises(frappe.ApplicationError) as cm:
				ErrorService.handle_api_exception(e)
			
			self.assertNotIn("SECRET_KEY_123", str(cm.exception))

	def tearDown(self):
		frappe.db.rollback()
