# -*- coding: utf-8 -*-
# Copyright (c) 2026, Antigravity and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GPFPrintFormatSetup(Document):
	def validate(self):
		self.validate_target_doctype()

	def validate_target_doctype(self):
		if not self.target_doctype or not frappe.db.exists("DocType", self.target_doctype):
			frappe.throw(frappe._("Target DocType is required and must exist."))
