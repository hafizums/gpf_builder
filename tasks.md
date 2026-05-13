# tasks.md

Project: Frappe 14 PDF Reference to Print Format Builder for Warning Letters  
Stage: Waterfall Stage 4 — Agentic-AI-Ready Implementation Tasks  
Rule: Execute one checkbox task at a time. Do not write code outside the selected task. Do not change approved requirements, analysis, or design.

## Phase 0 — Repository and Environment Baseline

- [x] Verify the repository contains or can host the `gpf_builder` Frappe app structure defined in the approved design.
- [x] Create the planned top-level app folders: `api`, `services`, `domain`, `doctype`, `public`, `templates`, `integrations`, `utils`, and `tests`.
- [x] Add a placeholder module file for shared constants without implementing business logic.
- [x] Define the constant names for `TARGET_DOCTYPE`, setup statuses, block types, allowed branding file types, rate-limit action names, and stable error codes.
- [x] Document the chosen canvas/SVG helper library dependency for layout editing.
- [x] Document the PDF.js dependency for browser PDF rendering.
- [x] Document the Google Vision backend dependency and configuration keys.
- [x] Document the test folder convention for unit tests, API tests, integration tests, security tests, and end-to-end tests.
- [x] Verify no production feature code has been written during this baseline task.
- [x] Review checkpoint: confirm app scaffolding and dependency notes match the approved System Design.

### Phase 0 Definition of Done

- [x] Folder structure is present or explicitly mapped.
- [x] Dependencies are documented.
- [x] Shared constants are named but not over-implemented.
- [x] Test structure is ready.
- [x] No approved requirement has been changed.

## Phase 1 — Database Migration and Permission Foundation

- [x] Create `GPF Print Format Setup` DocType definition with approved setup fields.
- [x] Add autonaming support for setup records using the approved `GPF-YYYYMMDD-###` format.
- [x] Add setup status values `Editing` and `Finalized`.
- [x] Add setup field enforcing `target_doctype` storage for `Dunning Letter`.
- [x] Add setup fields for PDF reference, preview timestamp, similarity confirmation, finalization timestamp, and final output validity.
- [x] Create `GPF Layout Block` DocType definition with setup link and block type.
- [x] Add layout block fields for normalized `x`, `y`, `width`, `height`, and `z_index`.
- [x] Add layout block fields for static text, OCR result reference, dynamic field name, file reference, and allowlisted style JSON.
- [x] Create `GPF OCR Result` DocType definition with setup link and source PDF file reference.
- [x] Add OCR result fields for raw text, normalized text, confirmation status, confirmed by, and confirmed at.
- [x] Create `GPF Version History` DocType definition with setup link and version number.
- [x] Add version history fields for event type, sanitized change summary, layout snapshot JSON, generated output snapshot, created by, and created at.
- [x] Create `GPF Audit Event` DocType definition with event type, severity, actor, setup, IP hash, user-agent hash, sanitized message, and created at.
- [x] Add DocType permission rules that deny Guest access to all custom DocTypes.
- [x] Add DocType permission rules that deny authenticated non-Administrator access to all custom DocTypes.
- [x] Add DocType permission rules that deny System Manager access unless the user is exactly built-in `Administrator`.
- [x] Add a migration patch to create or retrieve the single active MVP setup idempotently.
- [x] Add a migration or validation guard so setup target DocType cannot become anything except `Dunning Letter`.
- [x] Add indexes or equivalent Frappe metadata for setup links, status fields, version ordering, and audit timestamps.
- [x] Add migration tests proving repeated migration runs do not create duplicate active setups.
- [x] Add permission tests proving only built-in `Administrator` can read custom DocType records.
- [x] Review checkpoint: confirm database schema, permissions, and migration behavior match approved design.

### Phase 1 Definition of Done

- [x] All required DocTypes exist.
- [x] All required fields exist.
- [x] Migrations are idempotent.
- [x] One active setup behavior is testable.
- [x] Non-Administrator DocType access is denied.
- [x] Database implementation does not introduce extra workflows or entities.

## Phase 2 — Backend Security and Core Services

- [x] Implement `AccessControlService` with exact built-in `Administrator` user enforcement.
- [x] Add a unit test proving Guest is rejected by `AccessControlService`.
- [x] Add a unit test proving authenticated non-Administrator users are rejected.
- [x] Add a unit test proving System Manager is rejected unless the session user is exactly `Administrator`.
- [x] Add a unit test proving a custom role user is rejected.
- [x] Add a unit test proving built-in `Administrator` is accepted.
- [x] Implement a shared API guard that calls `AccessControlService` before endpoint logic.
- [x] Verify no app whitelisted method uses `allow_guest=True`.
- [x] Implement `SetupService` single active setup lookup.
- [x] Implement `SetupService` target DocType check for `Dunning Letter`.
- [x] Implement `SetupService` editing-state check for mutating actions.
- [x] Implement `SetupService` finalized-state check for output actions.
- [x] Add tests for missing setup, wrong target DocType, editing state, and finalized state.
- [x] Implement stable error response formatting with code and sanitized message.
- [x] Add tests proving API errors do not expose stack traces.
- [x] Add tests proving API errors do not expose credentials.
- [x] Add tests proving API errors do not expose private file paths.
- [x] Add tests proving API errors do not expose full OCR text or full generated output.
- [x] Implement `AuditLogService` for sanitized security and workflow audit events.
- [x] Add tests proving IP address and user agent are stored as hashes or safe derived values.
- [x] Add tests proving sensitive values are redacted from audit messages.
- [x] Implement `RateLimitService` with configured keys for upload, OCR, preview, save, finalize, output generation, and return-to-editing.
- [x] Add rate-limit tests for each configured action.
- [x] Implement object-scope helper for setup references.
- [x] Implement object-scope helper for OCR result references.
- [x] Implement object-scope helper for Frappe File references.
- [x] Add tests proving object references outside the active setup are rejected.
- [x] Review checkpoint: confirm core security services pass tests before feature services start.

### Phase 2 Definition of Done

- [x] Administrator-only access works at service and API guard level.
- [x] Stable sanitized errors are available.
- [x] Rate limits are configurable and tested.
- [x] Audit logging redacts sensitive data.
- [x] Object-level scoping helpers are tested.
- [x] Finalized-state guard exists.

## Phase 3 — PDF Reference, Field Mapping, Branding, and OCR Services

- [x] Implement `PdfReferenceService` extension validation for PDF references.
- [x] Implement `PdfReferenceService` MIME type validation.
- [x] Implement `PdfReferenceService` content sniffing for PDF references.
- [x] Implement PDF readability validation.
- [x] Implement protected or encrypted PDF rejection.
- [x] Implement one-page PDF validation.
- [x] Implement PDF maximum size validation using a configurable constant.
- [x] Implement private Frappe File storage enforcement for uploaded PDF references.
- [x] Add tests accepting a valid one-page private PDF.
- [x] Add tests rejecting non-PDF files.
- [x] Add tests rejecting MIME mismatch files.
- [x] Add tests rejecting unreadable PDFs.
- [x] Add tests rejecting protected PDFs.
- [x] Add tests rejecting multi-page PDFs.
- [x] Add tests rejecting oversized PDFs.
- [x] Add tests rejecting public PDF references.
- [x] Implement `upload_pdf_reference` API orchestration.
- [x] Add API tests for successful PDF reference upload.
- [x] Add API tests for each PDF upload error code.
- [x] Implement `FieldMappingService` to fetch metadata from `Dunning Letter` only.
- [x] Add tests proving arbitrary DocType metadata cannot be requested.
- [x] Add tests proving valid `Dunning Letter` fields are returned.
- [x] Implement `get_dunning_letter_fields` API without accepting client-provided target DocType.
- [x] Add API tests for `get_dunning_letter_fields`.
- [x] Implement `BrandingAssetService` existing file lookup.
- [x] Implement branding file accessibility validation.
- [x] Implement branding extension and MIME validation.
- [x] Add tests accepting PNG branding files.
- [x] Add tests accepting JPG branding files.
- [x] Add tests accepting JPEG branding files.
- [x] Add tests rejecting WEBP branding files.
- [x] Add tests rejecting PDF branding files.
- [x] Add tests rejecting missing branding files.
- [x] Add tests rejecting inaccessible branding files.
- [x] Implement `SvgSanitizerService`.
- [x] Add sanitizer tests rejecting SVG with `<script>`.
- [x] Add sanitizer tests rejecting SVG event handlers.
- [x] Add sanitizer tests rejecting `foreignObject`.
- [x] Add sanitizer tests rejecting external references.
- [x] Add sanitizer tests rejecting `data:` URLs.
- [x] Add sanitizer tests rejecting `javascript:` URLs.
- [x] Add sanitizer tests rejecting embedded objects.
- [x] Add sanitizer tests accepting a safe SVG fixture.
- [x] Implement Google Vision client adapter for backend-only OCR calls.
- [x] Implement OCR credential loading from server-side configuration only.
- [x] Implement OCR timeout behavior.
- [x] Implement missing OCR configuration behavior returning `OCR_NOT_CONFIGURED`.
- [x] Add tests proving OCR credentials are not returned to the client.
- [x] Add tests proving OCR credentials are not logged.
- [x] Add tests proving missing OCR configuration fails safely.
- [x] Implement `OcrService` explicit OCR run behavior.
- [x] Store OCR results as unconfirmed by default.
- [x] Add tests proving OCR run is rate-limited.
- [x] Add tests proving OCR failure does not block manual layout editing.
- [x] Implement `OcrConfirmationService`.
- [x] Implement `confirm_ocr_text` API with setup ownership check.
- [x] Add tests proving OCR result must belong to the active setup.
- [x] Add tests proving confirmed OCR text stores Administrator and timestamp.
- [x] Review checkpoint: confirm PDF, field mapping, branding, SVG, and OCR services enforce approved constraints.

### Phase 3 Definition of Done

- [x] PDF reference validation is complete and tested.
- [x] `Dunning Letter` metadata restriction is complete and tested.
- [x] Branding file rules are complete and tested.
- [x] SVG sanitizer is complete and tested.
- [x] OCR backend integration is server-side only and tested.
- [x] OCR confirmation is required before final use.

## Phase 4 — Layout, Preview, Finalization, Output, and Version Services

- [x] Implement `LayoutBlockService` create operation for layout blocks.
- [x] Implement `LayoutBlockService` update operation for layout blocks.
- [x] Implement `LayoutBlockService` delete operation for layout blocks.
- [x] Implement `LayoutBlockService` duplicate operation for layout blocks.
- [x] Implement normalized coordinate persistence.
- [x] Add tests for valid block creation.
- [x] Add tests for valid block update.
- [x] Add tests for valid block deletion.
- [x] Add tests for valid block duplication.
- [x] Add validation for allowed block types.
- [x] Add validation for positive width and height.
- [x] Add validation for page bounds.
- [x] Add validation for blank spacer rejection.
- [x] Add validation for allowlisted style JSON.
- [x] Add validation warning for text overflow.
- [x] Add tests for each block validation rule.
- [x] Add dynamic field block validation using `FieldMappingService`.
- [x] Add tests proving duplicate dynamic field usage is allowed.
- [x] Add tests proving invalid field names are rejected.
- [x] Implement `save_layout` API.
- [x] Ensure `save_layout` checks Administrator access.
- [x] Ensure `save_layout` checks setup scoping.
- [x] Ensure `save_layout` checks editing state.
- [x] Ensure `save_layout` applies rate limiting.
- [x] Ensure `save_layout` creates a version history entry.
- [x] Ensure `save_layout` writes audit event.
- [x] Add API tests for successful layout save.
- [x] Add API tests for finalized setup rejection during save.
- [x] Implement `VersionHistoryService` immutable version creation.
- [x] Add tests proving version numbers increment sequentially.
- [x] Add tests proving version history is read-only through the UI/API.
- [x] Implement sample data generation for preview.
- [x] Add tests for sample data generation from `Dunning Letter` field metadata.
- [x] Implement `PreviewService` sanitized preview generation.
- [x] Encode static text in preview.
- [x] Encode OCR text in preview.
- [x] Escape dynamic field output in preview.
- [x] Apply allowed HTML tag rules to preview.
- [x] Apply allowed CSS property rules to preview.
- [x] Prohibit JavaScript in preview.
- [x] Add tests for static text XSS payload encoding.
- [x] Add tests for OCR text XSS payload encoding.
- [x] Add tests for dynamic field XSS payload escaping.
- [x] Add tests proving preview blocks JavaScript.
- [x] Implement preview-generated timestamp persistence.
- [x] Implement preview invalidation when blocks change.
- [x] Implement preview invalidation when mappings change.
- [x] Implement preview invalidation when branding changes.
- [x] Implement preview invalidation when OCR-confirmed content changes.
- [x] Implement preview invalidation when PDF reference changes.
- [x] Add tests for each preview invalidation trigger.
- [x] Implement similarity confirmation persistence.
- [x] Add tests proving similarity confirmation stores Administrator and timestamp.
- [x] Implement `FinalizationService` readiness rules.
- [x] Add finalization rule requiring valid PDF reference.
- [x] Add finalization rule requiring valid dynamic fields.
- [x] Add finalization rule requiring confirmed OCR text when OCR text is used.
- [x] Add finalization rule requiring valid branding files.
- [x] Add finalization rule requiring sanitized SVG assets.
- [x] Add finalization rule rejecting blank spacer blocks.
- [x] Add finalization rule blocking overlapping blocks.
- [x] Add finalization rule requiring generated preview.
- [x] Add finalization rule requiring Administrator-confirmed 90% similarity.
- [x] Add tests for each finalization blocking rule.
- [x] Implement `finalize` API.
- [x] Add API tests for successful finalization.
- [x] Add API tests for failed finalization returning stable error codes.
- [x] Implement return-to-editing service transition.
- [x] Return-to-editing must set status to `Editing`.
- [x] Return-to-editing must invalidate final output.
- [x] Return-to-editing must invalidate preview readiness.
- [x] Return-to-editing must invalidate similarity confirmation.
- [x] Return-to-editing must write audit event.
- [x] Add tests for return-to-editing invalidation behavior.
- [x] Implement `OutputGenerationService`.
- [x] Generate Frappe Print Format-compatible HTML.
- [x] Generate Frappe Print Format-compatible CSS.
- [x] Generate approved `doc.<fieldname>` Jinja references only.
- [x] Use Frappe-compatible file URLs for images.
- [x] Prohibit arbitrary JavaScript in final output.
- [x] Add tests proving output contains only allowed HTML tags.
- [x] Add tests proving output contains only allowed CSS properties.
- [x] Add tests proving output contains only approved Jinja references.
- [x] Add tests proving output contains no JavaScript.
- [x] Implement `generate_output` API requiring finalized valid setup.
- [x] Add API tests rejecting output generation when setup is not finalized.
- [x] Add API tests rejecting output generation when final output is invalidated.
- [x] Add API tests returning copy-ready output for finalized setup.
- [x] Review checkpoint: confirm complete backend workflow passes from PDF upload through final output.

### Phase 4 Definition of Done

- [x] Layout persistence works.
- [x] Layout validation is server-side and tested.
- [x] Preview generation is sanitized and tested.
- [x] Version history is immutable and tested.
- [x] Finalization rules are complete and tested.
- [x] Return-to-editing invalidates output correctly.
- [x] Final output generation is sanitized and tested.

## Phase 5 — Frontend Builder and Workflow Screens

- [x] Register the Frappe Desk page for the builder.
- [x] Implement frontend access-denied display for unauthorized users.
- [x] Implement Builder Home Screen status badge.
- [x] Implement Builder Home Screen PDF upload panel.
- [x] Implement Builder Home Screen open layout builder action.
- [x] Implement Builder Home Screen version history action.
- [x] Implement Builder Home Screen finalize action.
- [x] Implement Builder Home Screen return-to-editing action.
- [x] Implement Builder Home Screen final output action.
- [x] Add UI tests for status-dependent action visibility.
- [x] Implement PDF.js single-page PDF viewer.
- [x] Add UI test proving uploaded PDF reference displays.
- [x] Implement layout canvas initialization.
- [x] Implement draw block interaction.
- [x] Implement drag block interaction.
- [x] Implement resize block interaction.
- [x] Implement align block interaction.
- [x] Implement duplicate block interaction.
- [x] Implement delete block interaction.
- [x] Implement z-order interaction if supported by the design.
- [x] Add UI tests for each block interaction.
- [x] Implement block toolbar.
- [x] Implement properties panel block type selector.
- [x] Implement properties panel static text editor.
- [x] Implement properties panel multilingual text handling.
- [x] Implement properties panel dynamic field selector.
- [x] Implement properties panel OCR text selector.
- [x] Implement properties panel branding file reference selector.
- [x] Implement properties panel style controls using allowlisted style fields only.
- [x] Add UI tests for properties panel request payloads.
- [x] Implement OCR panel run action.
- [x] Implement OCR panel result confirmation action.
- [x] Implement branding asset upload from builder UI.
- [x] Implement branding asset selection from allowlisted setup assets.
- [x] Add UI tests for branding and OCR interactions.
- [x] Add UI test proving unconfirmed OCR is visually distinct from confirmed OCR.
- [x] Implement validation issue panel for backend errors and warnings.
- [x] Add UI test proving stable error codes display sanitized messages.
- [x] Implement Preview Comparison Screen layout.
- [x] Implement PDF reference side of Preview Comparison Screen.
- [x] Implement generated preview side of Preview Comparison Screen.
- [x] Implement similarity confirmation checkbox or action.
- [x] Add UI test proving similarity confirmation calls backend API.
- [x] Implement Final Output Screen read-only output area.
- [x] Implement Final Output Screen copy action.
- [x] Implement Final Output Screen output metadata display.
- [x] Implement Final Output Screen non-pixel-perfect warning.
- [x] Add UI test proving final output is shown only after finalization.
- [x] Implement Version History Screen list.
- [x] Implement Version History Screen snapshot viewer.
- [x] Ensure Version History Screen has no rollback action.
- [x] Add UI test proving rollback is not exposed.
- [x] Implement empty state for no PDF reference.
- [x] Implement loading state for setup loading.
- [x] Implement loading state for PDF rendering.
- [x] Implement loading state for preview generation.
- [x] Implement error state for access denied.
- [x] Implement error state for invalid PDF.
- [x] Implement error state for setup finalized during editing.
- [x] Implement error state for failed preview.
- [x] Review checkpoint: confirm frontend matches approved screens and does not duplicate finalization business rules.

### Phase 5 Definition of Done

- [x] All approved screens exist.
- [x] All approved user interactions are represented.
- [x] UI uses backend APIs for business decisions.
- [x] UI displays loading, empty, and error states.
- [x] UI communicates OCR is assistive and output is not pixel-perfect.
- [x] UI does not introduce new workflows or roles.

## Phase 6 — Integration, Security Hardening, and Testing

- [x] Add end-to-end test for the complete happy path from PDF upload to final output.
- [x] Add end-to-end test for returning a finalized setup to editing and regenerating output after re-finalization.
- [x] Add security test proving Guest cannot access any app API.
- [x] Add security test proving authenticated non-Administrator cannot access any app API.
- [x] Add security test proving System Manager cannot access unless the user is exactly built-in `Administrator`.
- [x] Add security test proving custom-role users cannot access the app.
- [x] Add security test proving all custom DocTypes deny non-Administrator access.
- [x] Add security test proving no `allow_guest=True` app methods exist.
- [x] Add object-scope test for setup reference misuse.
- [x] Add object-scope test for OCR result misuse.
- [x] Add object-scope test for PDF file reference misuse.
- [x] Add object-scope test for branding file reference misuse.
- [x] Add finalized-state bypass test for direct save API calls.
- [x] Add finalized-state bypass test for direct upload API calls.
- [x] Add finalized-state bypass test for direct OCR API calls.
- [x] Add finalized-state bypass test for direct layout mutation calls.
- [x] Add finalized-state bypass test for direct branding mutation calls.
- [x] Add sanitizer regression test for unsafe SVG payloads.
- [x] Add sanitizer regression test for unsafe preview HTML.
- [x] Add sanitizer regression test for unsafe generated output.
- [x] Add sanitizer regression test for static text XSS payloads.
- [x] Add sanitizer regression test for OCR text XSS payloads.
- [x] Add sanitizer regression test for dynamic field escaping.
- [x] Add rate-limit integration test for upload PDF.
- [x] Add rate-limit integration test for run OCR.
- [x] Add rate-limit integration test for generate preview.
- [x] Add rate-limit integration test for save layout.
- [x] Add rate-limit integration test for finalize.
- [x] Add rate-limit integration test for generate output.
- [x] Add rate-limit integration test for return-to-editing.
- [x] Add log redaction test for Google Vision credentials.
- [x] Add log redaction test for private file paths.
- [x] Add log redaction test for full OCR text.
- [x] Add log redaction test for raw files.
- [x] Add log redaction test for full warning-letter content.
- [x] Add log redaction test for full generated output outside intentional snapshots.
- [x] Add Google Vision secret exposure test for frontend payloads.
- [x] Add Google Vision secret exposure test for API responses.
- [x] Add Google Vision secret exposure test for audit logs.
- [x] Add private file access test for uploaded PDF references.
- [x] Add private file access test for unauthorized branding file access.
- [x] Add compatibility smoke test proving generated output can be pasted into Frappe Print Format and rendered without prohibited constructs.
- [x] Add performance smoke test for PDF reference rendering.
- [x] Add performance smoke test for preview generation.
- [x] Add performance smoke test for final output generation.
- [x] Review checkpoint: confirm security and integration test matrix passes.

### Phase 6 Definition of Done

- [x] Happy-path E2E workflow passes.
- [x] Security tests pass.
- [x] Object-level authorization tests pass.
- [x] Finalized-state bypass tests pass.
- [x] Sanitizer tests pass.
- [x] Rate-limit tests pass.
- [x] Log redaction tests pass.
- [x] Private file tests pass.
- [x] Print Format compatibility smoke test passes.

## Phase 7 — Documentation and QA Handoff

- [x] Write developer setup documentation.
- [x] Document required Frappe app installation steps.
- [x] Document required migrations and fixtures.
- [x] Document test execution commands.
- [x] Document Google Vision configuration keys.
- [x] Document rate-limit configuration keys.
- [x] Document PDF file-size configuration.
- [x] Document API contracts for each endpoint.
- [x] Document stable error codes and messages.
- [x] Write Administrator usage guide for uploading a PDF reference.
- [x] Write Administrator usage guide for drawing and editing layout blocks.
- [x] Write Administrator usage guide for mapping `Dunning Letter` fields.
- [x] Write Administrator usage guide for OCR review and confirmation.
- [x] Write Administrator usage guide for branding selection.
- [x] Write Administrator usage guide for preview generation and comparison.
- [x] Write Administrator usage guide for 90% similarity confirmation.
- [x] Write Administrator usage guide for finalization.
- [x] Write Administrator usage guide for copy-ready output.
- [x] Write Administrator usage guide for return-to-editing.
- [x] Write Administrator usage guide for viewing version history.
- [x] Document known limitation: one-page PDF only.
- [x] Document known limitation: one saved reusable Print Format only.
- [x] Document known limitation: no rollback.
- [x] Document known limitation: no automated similarity measurement.
- [x] Document known limitation: no pixel-perfect guarantee.
- [x] Document known limitation: no batch generation.
- [x] Document known limitation: no Lampiran or invoice attachment pages.
- [x] Write security operations documentation for Administrator-only access.
- [x] Write security operations documentation for private file storage.
- [x] Write security operations documentation for Google Vision credential handling.
- [x] Write security operations documentation for audit log retention.
- [x] Write security operations documentation for alert thresholds.
- [x] Write security operations documentation for business deletion approval workflow.
- [x] Prepare QA handoff notes referencing Requirements, System Analysis, System Design, Implementation Plan, and tasks.md.
- [x] Review checkpoint: confirm documentation supports Stage 5 Testing Planning.

### Phase 7 Definition of Done

- [x] Developer documentation is complete.
- [x] Administrator documentation is complete.
- [x] Security operations documentation is complete.
- [x] Known limitations are documented.
- [x] QA handoff package is complete.
- [x] Stage 4 artifacts are ready for Testing Planning.

## Final Definition of Done

- [x] Every task is checkbox-formatted.
- [x] Every task is small enough for an agentic AI to execute independently.
- [x] Every task is verifiable.
- [x] Backend tasks are included.
- [x] Frontend tasks are included.
- [x] Database migration tasks are included.
- [x] Validation tasks are included.
- [x] Error handling tasks are included.
- [x] Security tasks are included.
- [x] Testing tasks are included.
- [x] Documentation tasks are included.
- [x] Tasks do not combine unrelated work.
- [x] Tasks do not require changing approved requirements.
- [x] Tasks do not require redesigning the approved system.
- [x] Tasks do not include production code in this planning artifact.

## Handoff to QA Tester

Use this Implementation Plan, System Design Document, System Analysis Document, and Requirements Document as the source for Testing Planning.
