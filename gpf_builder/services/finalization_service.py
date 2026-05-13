# -*- coding: utf-8 -*-
import frappe
from frappe.utils import now_datetime
from gpf_builder.domain.constants import (
	SETUP_STATUS_EDITING, 
	SETUP_STATUS_FINALIZED,
	BLOCK_TYPE_OCR_TEXT
)
from gpf_builder.services.setup_service import SetupService
from gpf_builder.services.version_service import VersionService

class FinalizationService:
	@staticmethod
	def finalize_setup(setup_name):
		"""
		Transitions the setup to 'Finalized' state.
		Requires at least one block and confirmed OCR results if OCR blocks exist.
		Creates an immutable snapshot upon success.
		"""
		setup_doc = frappe.get_doc("GPF Print Format Setup", setup_name)
		
		# 1. Validation: Must be in Editing state
		SetupService.validate_editing_state(setup_doc)
		
		# 2. Validation: Block count
		block_count = frappe.db.count("GPF Layout Block", {"setup": setup_name})
		if block_count == 0:
			frappe.throw(frappe._("Finalization failed: At least one layout block is required."))
			
		# 3. Validation: OCR Confirmation
		ocr_blocks = frappe.db.get_all("GPF Layout Block", 
			filters={"setup": setup_name, "block_type": BLOCK_TYPE_OCR_TEXT},
			fields=["ocr_result"]
		)
		for b in ocr_blocks:
			if b.ocr_result:
				is_confirmed = frappe.db.get_value("GPF OCR Result", b.ocr_result, "confirmed")
				if not is_confirmed:
					frappe.throw(frappe._("Finalization failed: OCR Result {0} must be confirmed.").format(b.ocr_result))

		# 4. Validation: Overlapping Blocks
		FinalizationService.validate_no_overlaps(setup_name)

		# 5. State Transition
		setup_doc.status = SETUP_STATUS_FINALIZED
		setup_doc.finalized_at = now_datetime()
		setup_doc.save(ignore_permissions=True)
		
		# 6. Create Snapshot
		VersionService.create_snapshot(setup_name, "Finalize", "Setup finalized for production.")
		
		return True

	@staticmethod
	def validate_no_overlaps(setup_name):
		"""
		Prohibits finalization if any layout blocks intersect.
		UT-018 Compliance.
		"""
		blocks = frappe.db.get_all("GPF Layout Block", 
			filters={"setup": setup_name}, 
			fields=["name", "x", "y", "width", "height"]
		)
		
		for i in range(len(blocks)):
			for j in range(i + 1, len(blocks)):
				b1 = blocks[i]
				b2 = blocks[j]
				
				# Axis-Aligned Bounding Box (AABB) intersection check
				if (b1.x < b2.x + b2.width and
					b1.x + b1.width > b2.x and
					b1.y < b2.y + b2.height and
					b1.y + b1.height > b2.y):
					frappe.throw(frappe._("Finalization blocked: Blocks {0} and {1} overlap.").format(b1.name, b2.name))

	@staticmethod
	def return_to_editing(setup_name):
		"""
		Transitions a finalized setup back to 'Editing' state.
		Creates a snapshot to record the transition.
		"""
		setup_doc = frappe.get_doc("GPF Print Format Setup", setup_name)
		
		if setup_doc.status == SETUP_STATUS_EDITING:
			return True
			
		setup_doc.status = SETUP_STATUS_EDITING
		setup_doc.save(ignore_permissions=True)
		
		VersionService.create_snapshot(setup_name, "Return to Editing", "Setup returned to editing state.")
		
		return True
