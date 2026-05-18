# -*- coding: utf-8 -*-
import frappe
from gpf_builder.domain.constants import (
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
	DEFAULT_WINDOW_SECONDS = 3600
	DEFAULT_LIMITS = {
		RATE_LIMIT_UPLOAD_PDF: 5,
		RATE_LIMIT_RUN_OCR: 3,
		RATE_LIMIT_GENERATE_PREVIEW: 30,
		RATE_LIMIT_SAVE_LAYOUT: 60,
		RATE_LIMIT_FINALIZE: 10,
		RATE_LIMIT_GENERATE_OUTPUT: 30,
		RATE_LIMIT_RETURN_TO_EDITING: 5
	}
	LIMITS = DEFAULT_LIMITS
	ACTION_SETTING_FIELDS = {
		RATE_LIMIT_UPLOAD_PDF: "upload_pdf_limit",
		RATE_LIMIT_RUN_OCR: "run_ocr_limit",
		RATE_LIMIT_GENERATE_PREVIEW: "generate_preview_limit",
		RATE_LIMIT_SAVE_LAYOUT: "save_layout_limit",
		RATE_LIMIT_FINALIZE: "finalize_limit",
		RATE_LIMIT_GENERATE_OUTPUT: "generate_output_limit",
		RATE_LIMIT_RETURN_TO_EDITING: "return_to_editing_limit"
	}

	@staticmethod
	def check_limit(action):
		"""
		Checks if the rate limit for a specific action has been exceeded for the current user.
		Throttles expensive or security-sensitive endpoints.
		"""
		if action not in RateLimitService.DEFAULT_LIMITS:
			return

		if not RateLimitService.is_enabled():
			return

		limit = RateLimitService.get_limit(action)
		if limit <= 0:
			return

		window_seconds = RateLimitService.get_window_seconds()
		# Use a cache key scoped by user and action
		key = "gpf_rate_limit:{0}:{1}".format(action, frappe.session.user)
		
		# Frappe cache is used for efficient per-user/per-action tracking
		current_count = frappe.cache().get_value(key) or 0
		
		if current_count >= limit:
			frappe.throw(
				frappe._("Rate limit exceeded for '{0}'. Please try again later.").format(action.replace('_', ' ')),
				frappe.PermissionError,
				ERROR_RATE_LIMITED
			)
		
		frappe.cache().set_value(key, current_count + 1, expires_in_sec=window_seconds)

	@staticmethod
	def get_settings_value(fieldname, default):
		try:
			value = frappe.db.get_single_value("GPF Rate Limit Settings", fieldname)
		except Exception:
			return default

		if value in [None, ""]:
			return default

		try:
			return int(value)
		except (TypeError, ValueError):
			return default

	@staticmethod
	def is_enabled():
		try:
			enabled = frappe.db.get_single_value("GPF Rate Limit Settings", "enabled")
		except Exception:
			return True

		return bool(enabled)

	@staticmethod
	def get_limit(action):
		fieldname = RateLimitService.ACTION_SETTING_FIELDS.get(action)
		default = RateLimitService.DEFAULT_LIMITS.get(action, 0)
		if not fieldname:
			return default
		return RateLimitService.get_settings_value(fieldname, default)

	@staticmethod
	def get_window_seconds():
		return max(1, RateLimitService.get_settings_value("window_seconds", RateLimitService.DEFAULT_WINDOW_SECONDS))

	@staticmethod
	def clear_limit(action):
		"""
		Utility to clear a rate limit for testing or administrative purposes.
		"""
		key = "gpf_rate_limit:{0}:{1}".format(action, frappe.session.user)
		frappe.cache().delete_value(key)
