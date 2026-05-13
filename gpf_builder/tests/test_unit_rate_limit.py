# -*- coding: utf-8 -*-
import frappe
import unittest
from gpf_builder.gpf_builder.services.rate_limit_service import RateLimitService
from gpf_builder.gpf_builder.domain.constants import RATE_LIMIT_RUN_OCR

class TestRateLimit(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		RateLimitService.clear_limit(RATE_LIMIT_RUN_OCR)

	def test_rate_limit_enforcement(self):
		"""
		Proving that the rate limit blocks excess calls for a specific action.
		"""
		limit = RateLimitService.LIMITS[RATE_LIMIT_RUN_OCR]
		
		# Exhaust the limit
		for _ in range(limit):
			RateLimitService.check_limit(RATE_LIMIT_RUN_OCR)
			
		# Next call should fail
		with self.assertRaises(frappe.PermissionError):
			RateLimitService.check_limit(RATE_LIMIT_RUN_OCR)

	def test_rate_limit_per_user(self):
		"""
		Proving that rate limits are tracked per user.
		"""
		limit = RateLimitService.LIMITS[RATE_LIMIT_RUN_OCR]
		
		# Exhaust limit for Admin
		for _ in range(limit):
			RateLimitService.check_limit(RATE_LIMIT_RUN_OCR)
		
		# Switch user
		frappe.set_user("Guest")
		RateLimitService.clear_limit(RATE_LIMIT_RUN_OCR)
		
		# Guest should still have their own limit
		try:
			RateLimitService.check_limit(RATE_LIMIT_RUN_OCR)
		except frappe.PermissionError:
			self.fail("Guest was rate limited by Administrator's activity!")

	def tearDown(self):
		frappe.set_user("Administrator")
		RateLimitService.clear_limit(RATE_LIMIT_RUN_OCR)
		frappe.db.rollback()
