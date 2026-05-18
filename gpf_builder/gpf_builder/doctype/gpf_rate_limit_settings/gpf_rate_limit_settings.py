# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document


class GPFRateLimitSettings(Document):
	def validate(self):
		for fieldname in self.get_rate_limit_fields():
			value = self.get(fieldname)
			if value is None:
				continue
			if int(value) < 0:
				frappe.throw(frappe._("{0} cannot be negative.").format(self.meta.get_label(fieldname)))

	@staticmethod
	def get_rate_limit_fields():
		return [
			"upload_pdf_limit",
			"run_ocr_limit",
			"generate_preview_limit",
			"save_layout_limit",
			"finalize_limit",
			"generate_output_limit",
			"return_to_editing_limit",
			"window_seconds"
		]
