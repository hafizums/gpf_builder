# -*- coding: utf-8 -*-
import frappe
import traceback
import sys

class ErrorService:
	@staticmethod
	def throw(message, code, exc=frappe.ValidationError):
		"""
		Standardized error throwing for the application.
		Ensures that only the sanitized message and code are returned to the client.
		"""
		# In production, Frappe handles sanitization when a whitelisted method 
		# throws an exception. We ensure the code is passed as the title 
		# or as part of the message if needed.
		frappe.throw(
			msg=frappe._(message),
			exc=exc,
			title=code
		)

	@staticmethod
	def handle_api_exception(e):
		"""
		Ensures that unexpected exceptions do not leak stack traces or sensitive data.
		"""
		frappe.log_error(traceback.format_exc(), "GPF Builder API Error")
		
		# Mask the original error with a stable generic code if it's not a known ValidationError/PermissionError
		if isinstance(e, (frappe.ValidationError, frappe.PermissionError, frappe.DoesNotExistError)):
			raise e
		else:
			frappe.throw(
				msg=frappe._("An unexpected error occurred. Please contact the Administrator."),
				exc=frappe.ApplicationError,
				title="INTERNAL_SERVER_ERROR"
			)
