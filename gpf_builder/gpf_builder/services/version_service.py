# -*- coding: utf-8 -*-
import frappe
import json
from frappe.utils import now_datetime

class VersionService:
	@staticmethod
	def create_snapshot(setup_name, event_type, change_summary=""):
		"""
		Creates an immutable snapshot of the current setup and layout blocks.
		Used for auditing and version control.
		"""
		# 1. Fetch current blocks
		blocks = frappe.get_all("GPF Layout Block", 
			filters={"setup": setup_name}, 
			fields=["block_type", "x", "y", "width", "height", "z_index", "static_text", "fieldname", "style_json"]
		)
		
		# 2. Calculate next version number
		current_max_version = frappe.db.get_value("GPF Version History", 
			{"setup": setup_name}, "max(version_number)") or 0
		next_version = current_max_version + 1
		
		# 3. Create version record
		version_doc = frappe.get_doc({
			"doctype": "GPF Version History",
			"setup": setup_name,
			"version_number": next_version,
			"event_type": event_type,
			"change_summary": change_summary,
			"layout_snapshot_json": json.dumps(blocks),
			"created_by": frappe.session.user,
			"created_at": now_datetime()
		})
		
		version_doc.insert(ignore_permissions=True)
		return version_doc.version_number

	@staticmethod
	def get_snapshot(setup_name, version_number):
		"""
		Retrieves a specific layout snapshot.
		"""
		snapshot_json = frappe.db.get_value("GPF Version History", 
			{"setup": setup_name, "version_number": version_number}, 
			"layout_snapshot_json"
		)
		if not snapshot_json:
			frappe.throw(frappe._("Version {0} not found for setup {1}").format(version_number, setup_name))
			
		return json.loads(snapshot_json)
