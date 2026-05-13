# -*- coding: utf-8 -*-
import frappe
from gpf_builder.gpf_builder.domain.constants import ERROR_ACCESS_DENIED

class AccessControlService:
	@staticmethod
	def validate_administrator():
		"""
		Enforce that only the built-in 'Administrator' user is allowed.
		Rejects Guests, authenticated non-Administrators, and System Managers.
		"""
		if frappe.session.user == "Guest":
			frappe.throw(
				frappe._("Guest access is not allowed."), 
				frappe.PermissionError,
				ERROR_ACCESS_DENIED
			)
			
		if frappe.session.user != "Administrator":
			frappe.throw(
				frappe._("Only the built-in Administrator user is authorized to use this application."), 
				frappe.PermissionError,
				ERROR_ACCESS_DENIED
			)

	@staticmethod
	def is_administrator():
		"""
		Return True if the current user is exactly 'Administrator'.
		"""
		return frappe.session.user == "Administrator"
