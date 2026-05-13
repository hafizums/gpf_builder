# -*- coding: utf-8 -*-
import frappe
import json
from gpf_builder.gpf_builder.api.guard import api_guard
from gpf_builder.gpf_builder.services.pdf_service import PDFService
from gpf_builder.gpf_builder.services.field_mapping_service import FieldMappingService
from gpf_builder.gpf_builder.services.branding_service import BrandingService
from gpf_builder.gpf_builder.services.ocr_service import OCRService
from gpf_builder.gpf_builder.services.layout_service import LayoutService
from gpf_builder.gpf_builder.services.preview_service import PreviewService
from gpf_builder.gpf_builder.services.finalization_service import FinalizationService
from gpf_builder.gpf_builder.services.output_service import OutputService
from gpf_builder.gpf_builder.services.setup_service import SetupService
from gpf_builder.gpf_builder.services.rate_limit_service import RateLimitService
from gpf_builder.gpf_builder.services.audit_log_service import AuditLogService
from gpf_builder.gpf_builder.services.validation_service import ValidationService
from gpf_builder.gpf_builder.domain.constants import (
	RATE_LIMIT_UPLOAD_PDF,
	RATE_LIMIT_RUN_OCR,
	RATE_LIMIT_SAVE_LAYOUT,
	RATE_LIMIT_FINALIZE,
	RATE_LIMIT_GENERATE_OUTPUT
)

@frappe.whitelist()
def upload_pdf_reference(file_name):
	"""
	Validates and links a PDF reference to the active setup.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_UPLOAD_PDF)
	
	setup = SetupService.get_active_setup()
	SetupService.validate_editing_state(setup)
	
	# Validate PDF
	meta = PDFService.validate_pdf(file_name)
	
	# Update setup
	setup.pdf_reference_file = file_name
	setup.save(ignore_permissions=True)
	
	AuditLogService.log_event("UPLOAD_PDF", "Uploaded PDF reference: {0}".format(file_name))
	
	return {"status": "success", "meta": meta}

@frappe.whitelist()
def get_dunning_letter_fields():
	"""
	Returns allowed field mapping for Dunning Letter.
	"""
	api_guard()
	return FieldMappingService.get_allowed_fields()

@frappe.whitelist()
def run_ocr(file_name):
	"""
	Runs OCR on the provided file.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_RUN_OCR)
	
	setup = SetupService.get_active_setup()
	SetupService.validate_editing_state(setup)
	ValidationService.validate_file_scope(file_name, setup.name)
	
	ocr_result_name = OCRService.run_ocr(file_name, setup.name)
	
	AuditLogService.log_event("RUN_OCR", "Ran OCR for file: {0}".format(file_name))
	
	return {"ocr_result": ocr_result_name}

@frappe.whitelist()
def confirm_ocr_result(ocr_result_name):
	"""
	Marks an OCR result as confirmed by the Administrator.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	ValidationService.validate_setup_scope("GPF OCR Result", ocr_result_name, setup.name)
	
	frappe.db.set_value("GPF OCR Result", ocr_result_name, {
		"confirmed": 1,
		"confirmed_by": frappe.session.user,
		"confirmed_at": frappe.utils.now_datetime()
	})
	
	AuditLogService.log_event("CONFIRM_OCR", "Confirmed OCR result: {0}".format(ocr_result_name))
	
	return {"status": "success"}

@frappe.whitelist()
def save_layout(blocks_json):
	"""
	Atomically saves all layout blocks for the active setup.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_SAVE_LAYOUT)
	
	setup = SetupService.get_active_setup()
	SetupService.validate_editing_state(setup)
	
	blocks = json.loads(blocks_json)
	
	# Scoping checks for each block
	for b in blocks:
		if b.get("ocr_result"):
			ValidationService.validate_setup_scope("GPF OCR Result", b["ocr_result"], setup.name)
		if b.get("file_reference"):
			ValidationService.validate_file_scope(b["file_reference"], setup.name)
			
	LayoutService.save_layout_blocks(setup.name, blocks)
	
	AuditLogService.log_event("SAVE_LAYOUT", "Saved {0} blocks for setup {1}".format(len(blocks), setup.name))
	
	return {"status": "success"}

@frappe.whitelist()
def get_preview():
	"""
	Returns the HTML preview for the active setup.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	return PreviewService.generate_preview_html(setup.name)

@frappe.whitelist()
def finalize_setup():
	"""
	Transitions the setup to Finalized state.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_FINALIZE)
	
	setup = SetupService.get_active_setup()
	FinalizationService.finalize_setup(setup.name)
	
	AuditLogService.log_event("FINALIZE_SETUP", "Setup {0} finalized.".format(setup.name))
	
	return {"status": "success"}

@frappe.whitelist()
def get_active_setup_info():
	"""
	Returns basic info about the active setup for the frontend builder.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	return {
		"name": setup.name,
		"pdf_reference_file": setup.pdf_reference_file,
		"status": setup.status,
		"target_doctype": setup.target_doctype
	}

@frappe.whitelist()
def return_to_editing():
	"""
	Returns a finalized setup to Editing state.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	FinalizationService.return_to_editing(setup.name)
	
	AuditLogService.log_event("RETURN_TO_EDITING", "Setup {0} returned to editing.".format(setup.name))
	
	return {"status": "success"}
