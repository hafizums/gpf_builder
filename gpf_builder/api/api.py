# -*- coding: utf-8 -*-
import frappe
import json
from gpf_builder.api.guard import api_guard
from gpf_builder.services.pdf_service import PDFService
from gpf_builder.services.field_mapping_service import FieldMappingService
from gpf_builder.services.branding_service import BrandingService
from gpf_builder.services.ocr_service import OCRService
from gpf_builder.services.layout_service import LayoutService
from gpf_builder.services.preview_service import PreviewService
from gpf_builder.services.finalization_service import FinalizationService
from gpf_builder.services.output_service import OutputService
from gpf_builder.services.setup_service import SetupService
from gpf_builder.services.template_service import TemplateService
from gpf_builder.services.rate_limit_service import RateLimitService
from gpf_builder.services.audit_log_service import AuditLogService
from gpf_builder.services.validation_service import ValidationService
from gpf_builder.domain.constants import (
	BLOCK_TYPE_IMAGE,
	BLOCK_TYPE_BRANDING,
	RATE_LIMIT_UPLOAD_PDF,
	RATE_LIMIT_RUN_OCR,
	RATE_LIMIT_GENERATE_PREVIEW,
	RATE_LIMIT_SAVE_LAYOUT,
	RATE_LIMIT_FINALIZE,
	RATE_LIMIT_GENERATE_OUTPUT,
	RATE_LIMIT_RETURN_TO_EDITING
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
	setup.pdf_reference_file = meta["name"]
	setup.save(ignore_permissions=True)
	
	AuditLogService.log_event("UPLOAD_PDF", "Uploaded PDF reference: {0}".format(file_name))
	
	return {"status": "success", "meta": meta}

@frappe.whitelist()
def get_target_fields():
	"""
	Returns allowed field mapping for the active setup target DocType.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	return FieldMappingService.get_allowed_fields(setup.target_doctype)

@frappe.whitelist()
def set_target_doctype(target_doctype):
	"""
	Sets the active builder target DocType and clears incompatible setup state.
	"""
	api_guard()
	if not target_doctype or not frappe.db.exists("DocType", target_doctype):
		frappe.throw(frappe._("Target DocType is required and must exist."), frappe.ValidationError)

	setup = SetupService.get_active_setup()
	SetupService.validate_editing_state(setup)

	if setup.target_doctype == target_doctype:
		return {"status": "success", "target_doctype": setup.target_doctype}

	frappe.db.delete("GPF Layout Block", {"setup": setup.name})
	frappe.db.delete("GPF OCR Result", {"setup": setup.name})
	setup.target_doctype = target_doctype
	setup.pdf_reference_file = None
	setup.save(ignore_permissions=True)

	AuditLogService.log_event("SET_TARGET_DOCTYPE", "Changed target DocType to {0}.".format(target_doctype))

	return {"status": "success", "target_doctype": setup.target_doctype}

@frappe.whitelist()
def get_dunning_letter_fields():
	"""
	Backward-compatible wrapper for older frontend/tests.
	"""
	return get_target_fields()

@frappe.whitelist()
def get_target_doc_values(docname):
	"""
	Returns printable values from a selected source document for the active
	setup target DocType.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	target_doctype = setup.target_doctype
	if not docname or not frappe.db.exists(target_doctype, docname):
		frappe.throw(frappe._("{0} document not found.").format(target_doctype), frappe.DoesNotExistError)

	doc = frappe.get_doc(target_doctype, docname)
	values = {}
	for field in FieldMappingService.get_allowed_fields(target_doctype):
		fieldname = field["fieldname"]
		try:
			values[fieldname] = doc.get_formatted(fieldname)
		except Exception:
			values[fieldname] = frappe.utils.cstr(doc.get(fieldname) or "")
	return values

@frappe.whitelist()
def get_dunning_letter_doc_values(docname):
	"""
	Backward-compatible wrapper for older frontend/tests.
	"""
	return get_target_doc_values(docname)

@frappe.whitelist()
def run_ocr(file_name, region_json=None):
	"""
	Runs OCR on the selected PDF region. Falls back to full-page OCR when no
	region is provided for backwards compatibility.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_RUN_OCR)
	
	setup = SetupService.get_active_setup()
	SetupService.validate_editing_state(setup)
	ValidationService.validate_file_scope(file_name, setup.name)
	
	if region_json:
		try:
			region = json.loads(region_json)
		except Exception:
			frappe.throw(frappe._("Invalid OCR region payload."), frappe.ValidationError)

		if not isinstance(region, dict):
			frappe.throw(frappe._("Invalid OCR region payload."), frappe.ValidationError)

		ocr_result_name = OCRService.run_ocr_region(file_name, setup.name, region)
		AuditLogService.log_event("RUN_OCR", "Ran region OCR for file: {0}".format(file_name))
	else:
		ocr_result_name = OCRService.run_ocr(file_name, setup.name)
		AuditLogService.log_event("RUN_OCR", "Ran full-page OCR for file: {0}".format(file_name))
	
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
def list_ocr_results():
	"""
	Returns OCR results for the active setup so the builder can display them.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	return frappe.get_all(
		"GPF OCR Result",
		filters={"setup": setup.name},
		fields=["name", "normalized_text", "confirmed", "creation"],
		order_by="creation desc"
	)

@frappe.whitelist()
def save_layout(blocks_json):
	"""
	Atomically saves all layout blocks for the active setup.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_SAVE_LAYOUT)
	
	setup = SetupService.get_active_setup()
	SetupService.validate_editing_state(setup)
	
	try:
		blocks = json.loads(blocks_json)
	except Exception:
		frappe.throw(frappe._("Invalid layout payload."), frappe.ValidationError)

	if not isinstance(blocks, list):
		frappe.throw(frappe._("Invalid layout payload: expected a list of blocks."), frappe.ValidationError)
	
	# Scoping checks for each block
	for b in blocks:
		if b.get("ocr_result"):
			ValidationService.validate_setup_scope("GPF OCR Result", b["ocr_result"], setup.name)
		if b.get("file_reference"):
			if b.get("block_type") in [BLOCK_TYPE_IMAGE, BLOCK_TYPE_BRANDING]:
				BrandingService.validate_image(b["file_reference"])
			else:
				ValidationService.validate_file_scope(b["file_reference"], setup.name)
			
	LayoutService.save_layout_blocks(setup.name, blocks, setup.target_doctype)
	
	AuditLogService.log_event("SAVE_LAYOUT", "Saved {0} blocks for setup {1}".format(len(blocks), setup.name))
	
	return {"status": "success"}

def validate_layout_block_scope(blocks, setup_name):
	for b in blocks:
		if b.get("ocr_result"):
			ValidationService.validate_setup_scope("GPF OCR Result", b["ocr_result"], setup_name)
		if b.get("file_reference"):
			if b.get("block_type") in [BLOCK_TYPE_IMAGE, BLOCK_TYPE_BRANDING]:
				BrandingService.validate_image(b["file_reference"])
			else:
				ValidationService.validate_file_scope(b["file_reference"], setup_name)

@frappe.whitelist()
def list_layout_templates():
	"""
	Returns saved layout templates for the active setup target DocType.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	return TemplateService.list_templates(setup.target_doctype)

@frappe.whitelist()
def save_layout_template(template_title, blocks_json):
	"""
	Saves the current builder canvas as a reusable template.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_SAVE_LAYOUT)

	setup = SetupService.get_active_setup()
	blocks = TemplateService.parse_blocks(blocks_json)
	blocks = TemplateService.normalize_blocks(blocks, setup.target_doctype)
	validate_layout_block_scope(blocks, setup.name)

	template = TemplateService.save_template(template_title, setup.target_doctype, blocks)
	AuditLogService.log_event(
		"SAVE_TEMPLATE",
		"Saved template {0} with {1} blocks.".format(template["name"], template["block_count"])
	)

	return {"status": "success", "template": template}

@frappe.whitelist()
def load_layout_template(template_name):
	"""
	Loads a saved template into the active setup, replacing current blocks.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_SAVE_LAYOUT)

	setup = SetupService.get_active_setup()
	SetupService.validate_editing_state(setup)

	template, blocks = TemplateService.get_template(template_name, setup.target_doctype)
	validate_layout_block_scope(blocks, setup.name)
	LayoutService.save_layout_blocks(setup.name, blocks, setup.target_doctype)

	AuditLogService.log_event("LOAD_TEMPLATE", "Loaded template {0} into setup {1}.".format(template.name, setup.name))

	return {"status": "success", "blocks": LayoutService.get_layout(setup.name)}

@frappe.whitelist()
def delete_layout_template(template_name):
	"""
	Deletes a saved layout template for the active target DocType.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_SAVE_LAYOUT)

	setup = SetupService.get_active_setup()
	deleted_name = TemplateService.delete_template(template_name, setup.target_doctype)
	AuditLogService.log_event("DELETE_TEMPLATE", "Deleted template {0}.".format(deleted_name))

	return {"status": "success"}

@frappe.whitelist()
def reset_setup():
	"""
	Resets the active setup to a clean editing state.
	This clears layout blocks and OCR results and unlinks the PDF reference.
	Uploaded File documents are not deleted.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_SAVE_LAYOUT)

	setup = SetupService.get_active_setup()
	SetupService.validate_editing_state(setup)

	frappe.db.delete("GPF Layout Block", {"setup": setup.name})
	frappe.db.delete("GPF OCR Result", {"setup": setup.name})

	setup.pdf_reference_file = None
	setup.save(ignore_permissions=True)

	AuditLogService.log_event("RESET_SETUP", "Reset setup {0}.".format(setup.name))

	return {"status": "success"}

@frappe.whitelist()
def get_layout():
	"""
	Returns all saved layout blocks for the active setup.
	"""
	api_guard()
	setup = SetupService.get_active_setup()
	return LayoutService.get_layout(setup.name)

@frappe.whitelist()
def get_preview(docname=None):
	"""
	Returns the HTML preview for the active setup.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_GENERATE_PREVIEW)
	setup = SetupService.get_active_setup()
	return PreviewService.generate_preview_html(setup.name, docname=docname)

@frappe.whitelist()
def generate_output(docname=None):
	"""
	Returns copy-ready Print Format HTML for the active finalized setup.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_GENERATE_OUTPUT)
	setup = SetupService.get_active_setup()
	doc = frappe.get_doc(setup.target_doctype, docname) if docname else frappe._dict({})
	return OutputService.generate_final_html(doc)

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
	file_url = None
	file_name = None
	if setup.pdf_reference_file:
		try:
			file_doc = PDFService.get_file_doc(setup.pdf_reference_file)
			file_url = file_doc.file_url
			file_name = file_doc.file_name
		except Exception:
			file_url = setup.pdf_reference_file

	return {
		"name": setup.name,
		"pdf_reference_file": setup.pdf_reference_file,
		"pdf_file_url": file_url,
		"pdf_file_name": file_name,
		"status": setup.status,
		"target_doctype": setup.target_doctype
	}

@frappe.whitelist()
def return_to_editing():
	"""
	Returns a finalized setup to Editing state.
	"""
	api_guard()
	RateLimitService.check_limit(RATE_LIMIT_RETURN_TO_EDITING)
	setup = SetupService.get_active_setup()
	FinalizationService.return_to_editing(setup.name)
	
	AuditLogService.log_event("RETURN_TO_EDITING", "Setup {0} returned to editing.".format(setup.name))
	
	return {"status": "success"}
