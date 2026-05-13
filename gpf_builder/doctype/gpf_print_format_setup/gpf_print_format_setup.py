# -*- coding: utf-8 -*-
# Copyright (c) 2026, Antigravity and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GPFPrintFormatSetup(Document):
	def validate(self):
		self.validate_target_doctype()

	def validate_target_doctype(self):
		if self.target_doctype != "Dunning Letter":
			frappe.throw(frappe._("Target DocType must be 'Dunning Letter'"))
