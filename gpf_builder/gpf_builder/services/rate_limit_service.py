# -*- coding: utf-8 -*-
import frappe
from gpf_builder.gpf_builder.domain.constants import (
	ERROR_RATE_LIMITED,
	RATE_LIMIT_UPLOAD_PDF,
	RATE_LIMIT_RUN_OCR,
	RATE_LIMIT_GENERATE_PREVIEW,
	RATE_LIMIT_SAVE_LAYOUT,
	RATE_LIMIT_FINALIZE,
	RATE_LIMIT_GENERATE_OUTPUT,
	RATE_LIMIT_RETURN_TO_EDITING
)

class RateLimitService:
	# Design-specified limits (per hour)
	LIMITS = {
		RATE_LIMIT_UPLOAD_PDF: 5,
		RATE_LIMIT_RUN_OCR: 3,
		RATE_LIMIT_GENERATE_PREVIEW: 30,
		RATE_LIMIT_SAVE_LAYOUT: 60,
		RATE_LIMIT_FINALIZE: 10,
		RATE_LIMIT_GENERATE_OUTPUT: 30,
		RATE_LIMIT_RETURN_TO_EDITING: 5
	}

	@staticmethod
	def check_limit(action):
		"""
		Checks if the rate limit for a specific action has been exceeded for the current user.
		Throttles expensive or security-sensitive endpoints.
		"""
		if action not in RateLimitService.LIMITS:
			return

		limit = RateLimitService.LIMITS[action]
		# Use a cache key scoped by user and action
		key = "gpf_rate_limit:{0}:{1}".format(action, frappe.session.user)
		
		# Frappe cache is used for efficient per-user/per-action tracking
		current_count = frappe.cache().get_value(key) or 0
		
		if current_count >= limit:
			frappe.throw(
				frappe._("Rate limit exceeded for '{0}'. Please try again in an hour.").format(action.replace('_', ' ')),
				frappe.PermissionError,
				ERROR_RATE_LIMITED
			)
		
		# Increment and persist for 1 hour
		# In a real Frappe environment, this would use Redis via frappe.cache()
		frappe.cache().set_value(key, current_count + 1, expires_in_sec=3600)

	@staticmethod
	def clear_limit(action):
		"""
		Utility to clear a rate limit for testing or administrative purposes.
		"""
		key = "gpf_rate_limit:{0}:{1}".format(action, frappe.session.user)
		frappe.cache().delete_value(key)
