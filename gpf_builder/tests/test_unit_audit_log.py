# -*- coding: utf-8 -*-
import frappe
import unittest
import hashlib
from gpf_builder.gpf_builder.services.audit_log_service import AuditLogService

class TestAuditLog(unittest.TestCase):
	def test_audit_log_hashing(self):
		"""
		Proving IP address and user agent are stored as hashes, not raw values.
		"""
		# Mocking request info if needed, but the service handles missing info gracefully
		event_name = AuditLogService.log_event("TEST_EVENT", "Test audit message")
		
		audit_doc = frappe.get_doc("GPF Audit Event", event_name)
		
		# Check that hashes are 64 characters (SHA256)
		self.assertEqual(len(audit_doc.ip_address_hash), 64)
		self.assertEqual(len(audit_doc.user_agent_hash), 64)
		
		# Verify raw "unknown" (default in tests) is hashed correctly
		expected_unknown_hash = hashlib.sha256("unknown".encode("utf-8")).hexdigest()
		self.assertEqual(audit_doc.ip_address_hash, expected_unknown_hash)

	def test_audit_log_fields(self):
		"""
		Proving that all required fields are correctly populated in the audit log.
		"""
		frappe.set_user("Administrator")
		event_name = AuditLogService.log_event("LOGIN_ATTEMPT", "Admin login", severity="Warning")
		
		audit_doc = frappe.get_doc("GPF Audit Event", event_name)
		self.assertEqual(audit_doc.event_type, "LOGIN_ATTEMPT")
		self.assertEqual(audit_doc.severity, "Warning")
		self.assertEqual(audit_doc.actor, "Administrator")
		self.assertEqual(audit_doc.message, "Admin login")

	def tearDown(self):
		frappe.db.rollback()
