# -*- coding: utf-8 -*-
import frappe
import unittest
from unittest.mock import patch, MagicMock
from gpf_builder.services.field_mapping_service import FieldMappingService

class TestFieldMapping(unittest.TestCase):
	@patch("gpf_builder.services.field_mapping_service.frappe.get_meta")
	def test_get_allowed_fields_filtering(self, mock_get_meta):
		"""
		Proving that forbidden fields and non-data fieldtypes are filtered out.
		"""
		mock_meta = MagicMock()
		# Define a mix of allowed and forbidden fields
		mock_meta.fields = [
			MagicMock(fieldname="customer", label="Customer", fieldtype="Link"),
			MagicMock(fieldname="amount", label="Amount", fieldtype="Currency"),
			MagicMock(fieldname="creation", label="Creation", fieldtype="Datetime"), # Forbidden fieldname
			MagicMock(fieldname="section_break_1", label="Section", fieldtype="Section Break"), # Forbidden fieldtype
		]
		mock_get_meta.return_value = mock_meta
		
		allowed = FieldMappingService.get_allowed_fields()
		fieldnames = [f["fieldname"] for f in allowed]
		
		self.assertIn("customer", fieldnames)
		self.assertIn("amount", fieldnames)
		self.assertNotIn("creation", fieldnames)
		self.assertNotIn("section_break_1", fieldnames)

	@patch("gpf_builder.services.field_mapping_service.FieldMappingService.get_allowed_fields")
	def test_validate_fieldname(self, mock_get_allowed):
		"""
		Proving fieldname validation works against the allowed list.
		"""
		mock_get_allowed.return_value = [{"fieldname": "customer"}]
		
		self.assertTrue(FieldMappingService.validate_fieldname("customer"))
		self.assertFalse(FieldMappingService.validate_fieldname("forbidden_field"))

	def tearDown(self):
		frappe.db.rollback()
