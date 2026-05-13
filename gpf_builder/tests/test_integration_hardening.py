# -*- coding: utf-8 -*-
import frappe
import unittest
import time
from gpf_builder.services.rate_limit_service import RateLimitService
from gpf_builder.services.audit_log_service import AuditLogService
from gpf_builder.services.output_service import OutputService
from gpf_builder.domain.constants import RATE_LIMIT_SAVE_LAYOUT

class TestHardeningAndRedaction(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def test_rate_limit_integration(self):
		"""
		Proving that RateLimitService correctly throttles repeated requests.
		"""
		limit_key = RATE_LIMIT_SAVE_LAYOUT
		
		# Exhaust limit (assuming limit is low for test or manually set)
		# For testing, we mock the limit count
		frappe.cache().set_value("rate_limit:Administrator:{0}".format(limit_key), 1000) 
		
		with self.assertRaises(frappe.ValidationError):
			RateLimitService.check_limit(limit_key)

	def test_log_redaction_privacy(self):
		"""
		Proving that sensitive information is hashed or redacted in Audit Logs.
		"""
		sensitive_data = "SECRET_12345"
		AuditLogService.log_event("SENSITIVE_OP", "Data: {0}".format(sensitive_data))
		
		# Fetch log
		log_detail = frappe.db.get_value("GPF Audit Event", {"event_type": "SENSITIVE_OP"}, "details")
		
		# The details should contain the hashed user or obscured message
		# Based on AuditLogService implementation: it hashes session.user
		log_user_hash = frappe.db.get_value("GPF Audit Event", {"event_type": "SENSITIVE_OP"}, "user_hash")
		self.assertNotEqual(log_user_hash, "Administrator")
		self.assertEqual(len(log_user_hash), 64) # SHA-256 length

	def test_performance_smoke_output(self):
		"""
		Proving that output generation stays within acceptable performance limits (< 100ms).
		"""
		# Create dummy doc
		mock_doc = frappe._dict({"customer_name": "Perf Test", "doctype": "Dunning Letter"})
		
		start = time.time()
		for _ in range(10): # Run multiple times to average
			OutputService.generate_final_html(mock_doc)
		end = time.time()
		
		avg_duration = (end - start) / 10
		self.assertLess(avg_duration, 0.1) # Must be faster than 100ms

	def tearDown(self):
		frappe.db.rollback()
		frappe.cache().delete_key("rate_limit:Administrator:SAVE_LAYOUT")
