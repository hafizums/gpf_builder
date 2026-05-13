# -*- coding: utf-8 -*-
import frappe
from gpf_builder.services.access_control_service import AccessControlService

def api_guard():
	"""
	Shared API guard to be called at the beginning of every whitelisted API method.
	"""
	AccessControlService.validate_administrator()
