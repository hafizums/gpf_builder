# -*- coding: utf-8 -*-
import frappe
from gpf_builder.domain.constants import TARGET_DOCTYPE

class FieldMappingService:
	# Fields to exclude from mapping (system/internal)
	FORBIDDEN_FIELDNAMES = [
		"name", "owner", "creation", "modified", "modified_by", 
		"docstatus", "idx", "lft", "rgt", "old_parent", "amended_from"
	]
	
	# Field types allowed for mapping in PDF layout
	ALLOWED_FIELD_TYPES = [
		"Data", "Text", "Long Text", "Small Text", "Select", 
		"Date", "Datetime", "Currency", "Int", "Float", "Link", "Check"
	]

	@staticmethod
	def get_allowed_fields():
		"""
		Retrieves the list of printable fields from the target DocType (Dunning Letter).
		Filters out system fields and non-data fieldtypes (e.g., Section Break, Column Break).
		"""
		meta = frappe.get_meta(TARGET_DOCTYPE)
		allowed_fields = []

		for df in meta.fields:
			if df.fieldtype in FieldMappingService.ALLOWED_FIELD_TYPES and \
			   df.fieldname not in FieldMappingService.FORBIDDEN_FIELDNAMES:
				allowed_fields.append({
					"fieldname": df.fieldname,
					"label": df.label,
					"fieldtype": df.fieldtype,
					"options": df.options if df.fieldtype in ["Select", "Link"] else None
				})

		# Add some standard fields that might be useful even if they are in forbidden list (optional)
		# For MVP, we stick to the strict allowed list.

		return allowed_fields

	@staticmethod
	def validate_fieldname(fieldname):
		"""
		Validates if a specific fieldname is allowed for use in the layout.
		"""
		allowed_fields = [f["fieldname"] for f in FieldMappingService.get_allowed_fields()]
		return fieldname in allowed_fields
