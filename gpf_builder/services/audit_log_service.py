# -*- coding: utf-8 -*-
import frappe
import hashlib
from frappe.utils import now_datetime

class AuditLogService:
	@staticmethod
	def log_event(event_type, message, setup=None, severity="Info"):
		"""
		Records a security or workflow event in the GPF Audit Event log.
		Ensures that IP address and User Agent are hashed before storage.
		"""
		ip_address = frappe.local.request_ip if hasattr(frappe.local, "request_ip") else "unknown"
		user_agent = frappe.get_request_header("User-Agent") or "unknown"
		
		ip_hash = hashlib.sha256(ip_address.encode("utf-8")).hexdigest()
		ua_hash = hashlib.sha256(user_agent.encode("utf-8")).hexdigest()
		
		# Sanitize message: redact potential secrets or sensitive data pattern if needed
		# For MVP, we assume the caller provides a sanitized message.
		
		audit_doc = frappe.get_doc({
			"doctype": "GPF Audit Event",
			"event_type": event_type,
			"severity": severity,
			"actor": frappe.session.user,
			"setup": setup,
			"ip_address_hash": ip_hash,
			"user_agent_hash": ua_hash,
			"message": message,
			"created_at": now_datetime()
		})
		
		audit_doc.insert(ignore_permissions=True)
		return audit_doc.name
