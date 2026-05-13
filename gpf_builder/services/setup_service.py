# -*- coding: utf-8 -*-
import frappe
from gpf_builder.gpf_builder.domain.constants import (
	TARGET_DOCTYPE, SETUP_STATUS_EDITING, SETUP_STATUS_FINALIZED,
	ERROR_SETUP_NOT_FOUND, ERROR_INVALID_TARGET_DOCTYPE, ERROR_SETUP_FINALIZED
)

class SetupService:
	@staticmethod
	def get_active_setup():
		"""
		Retrieve the single active MVP setup record.
		Throws SETUP_NOT_FOUND if no setup exists for the target DocType.
		"""
		setup_name = frappe.db.get_value("GPF Print Format Setup", {"target_doctype": TARGET_DOCTYPE}, "name")
		if not setup_name:
			frappe.throw(
				frappe._("Active setup for '{0}' not found.").format(TARGET_DOCTYPE), 
				frappe.DoesNotExistError, 
				ERROR_SETUP_NOT_FOUND
			)
		
		setup_doc = frappe.get_doc("GPF Print Format Setup", setup_name)
		
		# Hard restriction check
		if setup_doc.target_doctype != TARGET_DOCTYPE:
			frappe.throw(
				frappe._("Invalid target DocType: {0}").format(setup_doc.target_doctype),
				frappe.ValidationError,
				ERROR_INVALID_TARGET_DOCTYPE
			)
			
		return setup_doc

	@staticmethod
	def validate_editing_state(setup_doc):
		"""
		Enforce that the setup is in 'Editing' state for mutating actions.
		"""
		if setup_doc.status != SETUP_STATUS_EDITING:
			frappe.throw(
				frappe._("Action rejected: Setup is currently Finalized."), 
				frappe.ValidationError, 
				ERROR_SETUP_FINALIZED
			)

	@staticmethod
	def validate_finalized_state(setup_doc):
		"""
		Enforce that the setup is in 'Finalized' state for output actions.
		"""
		if setup_doc.status != SETUP_STATUS_FINALIZED:
			frappe.throw(
				frappe._("Action rejected: Setup must be Finalized first."), 
				frappe.ValidationError, 
				ERROR_SETUP_FINALIZED
			)
