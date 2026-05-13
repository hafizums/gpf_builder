# -*- coding: utf-8 -*-
# Copyright (c) 2026, Antigravity and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GPFLayoutBlock(Document):
	def validate(self):
		self.validate_dimensions()

	def validate_dimensions(self):
		if self.width <= 0 or self.height <= 0:
			frappe.throw(frappe._("Width and height must be positive values"))
