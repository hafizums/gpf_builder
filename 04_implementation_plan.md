# Implementation Plan

Project: Frappe 14 PDF Reference to Print Format Builder for Warning Letters  
Stage: Waterfall Stage 4 — Implementation Planning  
Outputs: `04_implementation_plan.md`, `tasks.md`  
Implementation status: Planning only. No implementation code is included.

## Confirmed Information

- The system is a native Frappe 14 custom app.
- The backend is implemented as Python services inside Frappe.
- The frontend is a Frappe Desk page with JavaScript.
- The database layer uses MariaDB through Frappe ORM and custom DocTypes.
- The app is restricted to the built-in Frappe `Administrator` user only.
- The target DocType is hard-restricted to `Dunning Letter`.
- The MVP supports one active reusable Print Format setup.
- The MVP accepts one single-page warning letter PDF reference only.
- Uploaded PDF references must use private Frappe File storage.
- Branding assets are selected from existing Frappe File records only.
- Branding file types are limited to PNG, JPG, JPEG, and sanitized SVG.
- WEBP and PDF branding assets are rejected.
- Google Vision OCR is server-side only and assistive only.
- OCR text must be reviewed and confirmed before use in final output.
- The system must support English and Malay OCR expectations where Google Vision supports them.
- Preview similarity is Administrator-confirmed visual similarity, not automated similarity scoring.
- The system must clearly communicate that output is not pixel-perfect automatic PDF conversion.
- Save and Finalize are separate actions.
- Finalized setup is locked until explicitly returned to `Editing`.
- Return to editing invalidates final output, preview readiness, and similarity confirmation.
- Final copy-ready output is Frappe Print Format-compatible HTML/CSS/Jinja.
- Version history is required and rollback is out of scope.
- Security controls include Administrator-only access, no guest APIs, object-level setup scoping, rate limits, sanitization, audit logging, and redaction of sensitive data.

## Assumptions

- The Frappe app repository is named `gpf_builder`.
- Existing Frappe site configuration and deployment secret management are available for Google Vision credentials.
- The production `Dunning Letter` DocType exists before implementation starts.
- Any exact file-size constant not named in the design will be implemented as a configurable constant and documented in site configuration.
- Development will use Frappe's standard test framework and project conventions.

## Open Questions

- The exact maximum PDF upload size must be configured before production deployment if not already defined by the environment.
- The operational approval workflow for business deletion must be documented before deployment planning.
- The exact test fixture fields available on `Dunning Letter` must be confirmed in the development environment.

## 1. Approved Design Summary

The approved design is a Frappe 14 modular monolith. It uses Frappe Desk pages, whitelisted backend APIs, Python service classes, Frappe ORM DocTypes, private Frappe File storage, Google Vision OCR called only from the backend, and Frappe Print Format-compatible generated output.

Primary modules:

| Module | Implementation Responsibility | Trace |
| --- | --- | --- |
| `AccessControlService` | Enforce built-in `Administrator` user only at service layer. | FR-001–FR-005, PR-001–PR-008, DD-002 |
| `SetupService` | Manage one active MVP setup and setup state. | FR-044–FR-048, DR-012–DR-015, DD-006 |
| `PdfReferenceService` | Validate one-page private PDF references. | FR-006–FR-012, DR-001–DR-003 |
| `LayoutBlockService` | Manage block creation, updates, duplication, deletion, and locking. | FR-013–FR-019, DR-004 |
| `FieldMappingService` | Restrict metadata and mappings to `Dunning Letter`. | FR-020–FR-024, DR-005–DR-007, DD-003 |
| `BrandingAssetService` | Validate existing branding files and invoke SVG sanitization. | FR-034–FR-037, BR-014 |
| `SvgSanitizerService` | Reject unsafe SVG content before preview or output. | Security Design |
| `OcrService` | Run Google Vision OCR and store unconfirmed OCR text. | FR-028–FR-033, DR-008–DR-009 |
| `OcrConfirmationService` | Track Administrator review and confirmation. | FR-031–FR-032 |
| `PreviewService` | Generate sanitized preview HTML using sample data. | FR-038–FR-043, DR-010–DR-011 |
| `OutputGenerationService` | Generate safe copy-ready Print Format output. | FR-046, BR-019, IR-006 |
| `ValidationService` | Centralize save/finalization validation. | FR-024, Validation Design |
| `FinalizationService` | Enforce finalization and return-to-editing transitions. | FR-005, BR-018, DD-008 |
| `VersionHistoryService` | Store immutable version snapshots. | FR-049–FR-051, DR-014 |
| `AuditLogService` | Store sanitized security and workflow audit events. | Logging and Monitoring Design |
| `RateLimitService` | Apply configured limits to expensive and mutating actions. | Security Design, Performance Considerations |

Clean Code Execution Standard:

- Use clear class, method, variable, DocType, and API names.
- Keep functions small and focused on one responsibility.
- Keep business logic out of UI components.
- Use repositories/Frappe ORM access through services, not scattered direct database logic.
- Use services for business rules.
- Use validators for request shape, data integrity, and finalization rules.
- Avoid duplicated business logic across API endpoints and UI.
- Validate security-sensitive rules server-side even when the UI already checks them.
- Add tests for critical rules before marking a phase complete.
- Use design patterns only where justified:
  - Facade pattern for API modules delegating to services.
  - Strategy pattern for finalization validation rules if rule count grows.
  - Adapter pattern for Google Vision OCR client.
  - Builder pattern or template model for output generation if output assembly becomes complex.

## 2. Development Phases

| Phase | Name | Goal | Review Checkpoint |
| --- | --- | --- | --- |
| 0 | Repository and Environment Baseline | Confirm app structure, dependencies, configuration placeholders, and development standards. | Review folder layout, hooks, dependency declarations, and no-code security checklist. |
| 1 | Database and Permissions Foundation | Create DocTypes, migrations, permissions, and setup defaults. | Review DocType schemas, permissions, patches, and migration reversibility. |
| 2 | Backend Security and Core Services | Implement access control, setup, rate limiting, audit logging, validation constants, and shared errors. | Review security tests before feature services proceed. |
| 3 | PDF, OCR, Field Mapping, Branding Services | Implement document ingestion, OCR, field selection, branding validation, and sanitization services. | Review service tests, object scoping tests, and unsafe file rejection tests. |
| 4 | Layout, Preview, Finalization, Output Services | Implement block persistence, preview generation, finalization locking, return-to-editing, and copy-ready output. | Review full backend workflow from upload to output. |
| 5 | Frontend Builder and Workflow Screens | Implement Frappe Desk UI screens using backend APIs without business-rule duplication. | Review UI behavior against approved screens and API contracts. |
| 6 | Integration, Security Hardening, and Testing | Complete end-to-end, security, validation, logging, and regression tests. | Review test evidence and security checklist. |
| 7 | Documentation and QA Handoff | Finalize developer documentation, operational notes, and QA handoff package. | Review documentation completeness and Stage Gate Checklist. |

## 3. Task Breakdown

### Phase 0 — Repository and Environment Baseline

| Task ID | Task | Trace | Verification |
| --- | --- | --- | --- |
| P0-T01 | Confirm `gpf_builder` Frappe app structure matches approved file/folder plan. | Design §16 | Folder tree exists with planned `api`, `services`, `doctype`, `public`, `templates`, `integrations`, `utils`, and tests folders. |
| P0-T02 | Add dependency declarations for PDF inspection, Google Vision client, PDF.js, and selected canvas helper library. | Design §3, §17 | Dependency list is documented and installable in a dev bench. |
| P0-T03 | Add configuration placeholders for Google Vision and rate limits. | IR-005, Security Design | Site config keys are documented and missing OCR config fails safely in later tests. |
| P0-T04 | Define shared constants for target DocType, statuses, file types, rate-limit keys, and error codes. | DD-003, Error Handling Design | Constants are centralized and imported by service plans/tests. |
| P0-T05 | Establish test folders and naming convention for unit, integration, API, and security tests. | NFR-005, Security Design | Test discovery runs with empty baseline. |
| P0-Review | Phase review checkpoint. | Waterfall Rules | Reviewer confirms no production code beyond scaffolding decisions and no requirement changes. |

### Phase 1 — Database and Permissions Foundation

| Task ID | Task | Trace | Verification |
| --- | --- | --- | --- |
| P1-T01 | Create `GPF Print Format Setup` DocType with status, target DocType, PDF reference, preview, similarity, finalization, and final output validity fields. | DR-012–DR-015, Design §5 | Migration creates DocType with approved fields and autonaming. |
| P1-T02 | Create `GPF Layout Block` DocType with setup link, block type, coordinates, z-index, content, field, file, and style fields. | DR-004–DR-007, Design §5 | Migration creates fields and setup relationship. |
| P1-T03 | Create `GPF OCR Result` DocType with setup, source PDF, raw text, normalized text, confirmation metadata, and status. | DR-008–DR-009, Design §5 | OCR result records can be created in tests. |
| P1-T04 | Create `GPF Version History` DocType with setup link, version number, event type, sanitized summary, layout snapshot, generated output snapshot, and metadata. | FR-049–FR-051, DR-014 | Version record structure supports immutable snapshots. |
| P1-T05 | Create `GPF Audit Event` DocType with event type, severity, actor, setup, IP hash, user-agent hash, sanitized message, and timestamp. | Logging Design | Audit event can store sanitized event data. |
| P1-T06 | Apply Frappe permission rules denying non-Administrator access to all custom DocTypes. | PR-001–PR-008, Security Design | Guest, non-Administrator, System Manager, and custom role users cannot read or write records. |
| P1-T07 | Add migration patch to create or retrieve the single active MVP setup safely. | FR-044, DD-006 | Patch is idempotent and creates no duplicate active setup. |
| P1-T08 | Add indexes for setup links, status, event timestamps, and version ordering. | Performance Considerations | Database metadata shows indexes or equivalent Frappe configuration. |
| P1-Review | Phase review checkpoint. | Waterfall Rules | Reviewer confirms schema and permission implementation matches design before service work continues. |

### Phase 2 — Backend Security and Core Services

| Task ID | Task | Trace | Verification |
| --- | --- | --- | --- |
| P2-T01 | Implement `AccessControlService` with exact `frappe.session.user == "Administrator"` enforcement. | FR-001–FR-005, DD-002 | Tests reject Guest, non-Administrator, System Manager, and custom-role users. |
| P2-T02 | Implement API entrypoint guard that calls access control before every whitelisted method. | Security Design | Every `gpf_builder` API has no guest access and invokes guard. |
| P2-T03 | Implement `SetupService` for single active setup lookup, target DocType enforcement, and state checks. | DD-003, DD-006 | Tests reject missing setup, wrong target DocType, and duplicate active setup conditions. |
| P2-T04 | Implement shared error response handling with stable codes and sanitized messages. | Error Handling Design | API errors expose no stack traces, secrets, private paths, OCR payloads, or generated output. |
| P2-T05 | Implement `AuditLogService` with sanitized messages and hashed IP/user-agent fields. | Logging Design | Tests prove sensitive values are redacted and audit records are created for protected events. |
| P2-T06 | Implement `RateLimitService` with configured limits for upload, OCR, preview, save, finalize, output generation, and return-to-editing. | Performance/Security Design | Tests verify each configured limit blocks excess calls. |
| P2-T07 | Implement common object-level scoping helpers for setup, OCR result, and file references. | API Security Design | Tests reject cross-setup and unrelated object identifiers. |
| P2-T08 | Implement service-level finalized-state guard for mutating actions. | DD-008, State Management Design | Tests reject direct edits when setup is finalized. |
| P2-Review | Phase review checkpoint. | Security Design | Reviewer confirms core security controls are in place before feature services are added. |

### Phase 3 — PDF, OCR, Field Mapping, Branding Services

| Task ID | Task | Trace | Verification |
| --- | --- | --- | --- |
| P3-T01 | Implement `PdfReferenceService` extension, MIME, content-sniffing, readability, encryption/protection, page count, file size, and private storage validation. | FR-006–FR-012, DR-001–DR-003 | Tests accept valid one-page PDF and reject invalid, oversized, unreadable, protected, public, and multi-page PDFs. |
| P3-T02 | Implement `upload_pdf_reference` API orchestration with access control, rate limit, setup scoping, validation, audit logging, and stable errors. | FR-002, FR-006, API Design | API test returns expected response for valid upload and expected error codes for invalid cases. |
| P3-T03 | Implement `FieldMappingService` to fetch allowed fields from `Dunning Letter` only. | FR-020–FR-024, DD-003 | Tests reject arbitrary target DocType metadata access. |
| P3-T04 | Implement `get_dunning_letter_fields` API with no target DocType input accepted from clients. | IR-003, API Design | API always returns `Dunning Letter` metadata only. |
| P3-T05 | Implement `BrandingAssetService` to validate existing file reference, accessibility, extension, MIME, and allowed image type. | FR-034–FR-037, BR-014 | Tests accept PNG/JPG/JPEG and reject WEBP/PDF/unsupported/missing files. |
| P3-T06 | Implement `SvgSanitizerService` to reject scripts, event handlers, `foreignObject`, external references, `data:` URLs, `javascript:` URLs, embedded objects, and unsafe attributes. | Security Design | Unit tests reject unsafe SVG payload classes and accept safe SVG fixtures. |
| P3-T07 | Implement Google Vision client adapter with backend-only credential loading and timeout handling. | IR-005, External Integrations | Tests mock credentials, missing config, timeout, provider failure, and no credential leakage. |
| P3-T08 | Implement `OcrService` to run OCR explicitly, store raw OCR as unconfirmed, and avoid automatic layout use. | FR-028–FR-033, DR-008–DR-009 | Tests prove OCR result status is unconfirmed by default. |
| P3-T09 | Implement `OcrConfirmationService` and `confirm_ocr_text` API with setup ownership checks and Administrator metadata. | FR-031–FR-032 | Tests prove confirmed text is stored separately and traceable. |
| P3-Review | Phase review checkpoint. | Security/Validation Design | Reviewer confirms file, OCR, field, and branding services enforce server-side constraints. |

### Phase 4 — Layout, Preview, Finalization, Output Services

| Task ID | Task | Trace | Verification |
| --- | --- | --- | --- |
| P4-T01 | Implement `LayoutBlockService` create/update/delete/duplicate persistence with normalized coordinates. | FR-013–FR-019, DR-004 | Tests save blocks with valid coordinates and reject invalid block types. |
| P4-T02 | Implement layout validation for page bounds, positive width/height, blank spacer rejection, style allowlist, and text overflow warning. | FR-013–FR-019, BL-018, BL-020 | Tests distinguish hard failures from warnings. |
| P4-T03 | Implement dynamic field block validation using `FieldMappingService` and allow duplicate field usage. | FR-020–FR-024, DD-005 | Tests allow duplicate valid fields and reject invalid fields. |
| P4-T04 | Implement `save_layout` API with rate limit, setup scoping, finalized-state check, validation, version snapshot, and audit logging. | FR-044–FR-051 | API test proves save creates or updates the single setup and creates version history. |
| P4-T05 | Implement sample data generation for preview from `Dunning Letter` field metadata. | FR-038, DR-010 | Tests generate safe sample values for supported field types. |
| P4-T06 | Implement `PreviewService` with sanitized rendering, static/OCR text encoding, dynamic value escaping, and allowed HTML/CSS/Jinja rules. | FR-039–FR-043, Security Design | Tests block JavaScript and unsafe template content. |
| P4-T07 | Implement preview invalidation when blocks, mappings, branding, OCR text, or PDF reference changes. | Performance Considerations | Tests mark preview stale after each relevant change. |
| P4-T08 | Implement similarity confirmation persistence with Administrator identity and timestamp. | FR-042, BL-013 | Tests require Administrator identity and timestamp. |
| P4-T09 | Implement `FinalizationService` rules for PDF validity, valid fields, confirmed OCR, valid branding, sanitized SVG, no blank spacer, no overlaps, preview generated, and 90% similarity confirmed. | FR-024, FR-041–FR-043, DD-007 | Tests block finalization for each missing or invalid condition. |
| P4-T10 | Implement finalized-state transition from `Editing` to `Finalized` only through `FinalizationService`. | DD-008 | Tests reject direct status mutation through APIs. |
| P4-T11 | Implement return-to-editing flow that invalidates final output, preview readiness, and similarity confirmation. | State Management Design | Tests prove output cannot be generated after return to editing. |
| P4-T12 | Implement `OutputGenerationService` for copy-ready Frappe Print Format HTML/CSS/Jinja with output sanitizer and JavaScript prohibition. | FR-046, IR-006, BR-019 | Tests prove generated output uses only allowed tags, CSS properties, Jinja expressions, and file URLs. |
| P4-T13 | Implement final output generation API requiring finalized valid setup and rate limiting. | API Design | API rejects non-finalized or invalidated setup and returns output for finalized setup. |
| P4-Review | Phase review checkpoint. | Design §6–§14 | Reviewer confirms backend workflow from upload to final output is complete and secure. |

### Phase 5 — Frontend Builder and Workflow Screens

| Task ID | Task | Trace | Verification |
| --- | --- | --- | --- |
| P5-T01 | Implement Frappe Desk page registration and route guard messaging for non-Administrator users. | UI-001, PR-001 | Manual/UI test shows access denied without exposing app data. |
| P5-T02 | Implement Builder Home Screen with status badge, PDF upload panel, open builder action, version history action, finalize, return-to-editing, and output actions. | UI Screen Design | UI test verifies state-dependent actions show correct enabled/disabled behavior. |
| P5-T03 | Implement PDF reference viewer using PDF.js for single-page display. | UI-003, Design §3 | UI test displays a valid uploaded PDF reference. |
| P5-T04 | Implement layout canvas with selected helper library for draw, drag, resize, align, duplicate, delete, and z-order. | UI-004–UI-005 | UI test verifies each block manipulation action updates local state. |
| P5-T05 | Implement properties panel for block type, static text, multilingual text, dynamic field selection, OCR text selection, image/branding file reference, and allowed styles. | UI-006–UI-010 | UI test verifies each property maps to backend request fields. |
| P5-T06 | Implement OCR panel for run OCR, review OCR output, edit normalized text, and confirm OCR text. | UI-008–UI-009 | UI test verifies unconfirmed OCR is visibly distinct from confirmed OCR. |
| P5-T07 | Implement validation issue panel showing server validation errors and warnings without duplicating final business rules. | Validation Design | UI test renders stable error codes and sanitized messages. |
| P5-T08 | Implement Preview Comparison Screen with PDF reference on one side, generated preview on the other, similarity confirmation, and validation issue list. | UI-011–UI-013 | UI test verifies similarity confirmation persists only through backend API. |
| P5-T09 | Implement Final Output Screen with read-only output panel, copy action, metadata, and non-pixel-perfect warning. | UI-014, NFR-008, NFR-012 | UI test shows copy-ready output only after finalized setup. |
| P5-T10 | Implement Version History Screen with read-only list and snapshot viewer. | UI-015, FR-049–FR-051 | UI test confirms no rollback action is exposed. |
| P5-T11 | Implement loading, empty, and error states for all screens. | UI Screen Design | UI test covers no PDF, loading PDF, failed preview, invalid setup, and access denied states. |
| P5-Review | Phase review checkpoint. | UI/UX Requirements | Reviewer confirms UI aligns to approved design and does not implement unauthorized workflow changes. |

### Phase 6 — Integration, Security Hardening, and Testing

| Task ID | Task | Trace | Verification |
| --- | --- | --- | --- |
| P6-T01 | Add end-to-end test for upload PDF, create blocks, map fields, run/confirm OCR, select branding, preview, confirm similarity, finalize, generate output, and view version history. | Core Features 1–16 | E2E test passes with a representative one-page PDF fixture. |
| P6-T02 | Add access-control tests for Guest, non-Administrator, System Manager, and custom-role users. | PR-001–PR-008, Security Design | All unauthorized users are denied at UI, API, service, and DocType levels. |
| P6-T03 | Add object-level authorization tests for setup, OCR result, PDF file, and branding file references. | API Security Design | Cross-object references are rejected. |
| P6-T04 | Add finalized-state bypass tests for direct API save, upload, OCR, branding, and layout mutations. | DD-008 | Finalized setup cannot be changed except through return-to-editing. |
| P6-T05 | Add sanitizer tests for SVG, preview HTML, generated output, static text XSS, OCR text XSS, and dynamic field escaping. | Security Design | Unsafe payloads are blocked or encoded. |
| P6-T06 | Add rate-limit tests for upload, OCR, preview, save, finalize, output, and return-to-editing. | Performance/Security Design | Excess requests return `RATE_LIMITED` or endpoint-specific code. |
| P6-T07 | Add log redaction tests for credentials, private file paths, OCR text, raw file data, warning-letter content, and full generated output outside approved snapshots. | Logging Design | Logs and API errors contain no sensitive raw data. |
| P6-T08 | Add Google Vision secret exposure tests for missing, invalid, and valid credential paths. | External Integrations | Credentials never appear in responses, logs, snapshots, or frontend data. |
| P6-T09 | Add private file access tests for uploaded PDF references and branding files. | File Security | Unauthorized users cannot retrieve private files through app paths. |
| P6-T10 | Add compatibility test proving generated output can be pasted into Frappe Print Format without prohibited constructs. | IR-002, IR-006, NFR-012 | Output passes allowlist validation and render smoke test. |
| P6-T11 | Add performance smoke tests for one-page PDF rendering, preview generation, and output generation under expected MVP payload size. | Performance Considerations | Tests complete within accepted local benchmark threshold. |
| P6-Review | Phase review checkpoint. | Security Test Cases | Reviewer confirms minimum security and workflow test matrix is complete. |

### Phase 7 — Documentation and QA Handoff

| Task ID | Task | Trace | Verification |
| --- | --- | --- | --- |
| P7-T01 | Write developer setup notes for app installation, migrations, test execution, and configuration keys. | Documentation Tasks | Documentation exists and a new developer can follow it. |
| P7-T02 | Write Administrator usage notes for upload, layout editing, OCR confirmation, preview, similarity confirmation, finalization, output copying, and return-to-editing. | UI/UX Requirements | Documentation covers every user workflow. |
| P7-T03 | Write security operations notes for credentials, private files, log retention, alert thresholds, and business deletion approval. | Security/Logging Design | Operations checklist has pass/fail items. |
| P7-T04 | Write known limitations: one-page PDF only, one saved format only, no rollback, no automated similarity, no pixel-perfect guarantee, no batch generation. | Out of Scope | Limitations match approved scope. |
| P7-T05 | Prepare QA handoff package referencing requirements, analysis, design, implementation plan, and tasks. | Waterfall Stage 5 Handoff | QA receives complete planning source set. |
| P7-Review | Phase review checkpoint. | Waterfall Rules | Reviewer confirms Stage 4 exit artifacts are complete. |

## 4. File-Level Change Plan

| Path | Planned Change | Trace |
| --- | --- | --- |
| `gpf_builder/hooks.py` | Register app resources, permissions, pages, fixtures, and patches. | IR-001 |
| `gpf_builder/modules.txt` | Register module metadata. | IR-001 |
| `gpf_builder/patches.txt` | Register migration patches. | Database Design |
| `gpf_builder/gpf_builder/api.py` | Expose whitelisted API methods or delegate to API package. | API Design |
| `gpf_builder/gpf_builder/api/*.py` | Implement endpoint-specific orchestration only. | API Design, Clean Code |
| `gpf_builder/gpf_builder/services/access_control_service.py` | Implement Administrator-only enforcement. | FR-001–FR-005 |
| `gpf_builder/gpf_builder/services/setup_service.py` | Manage single setup, state, and target DocType enforcement. | FR-044–FR-048 |
| `gpf_builder/gpf_builder/services/pdf_reference_service.py` | Validate and store PDF references. | FR-006–FR-012 |
| `gpf_builder/gpf_builder/services/layout_block_service.py` | Persist and validate layout blocks. | FR-013–FR-019 |
| `gpf_builder/gpf_builder/services/field_mapping_service.py` | Load and validate `Dunning Letter` field metadata. | FR-020–FR-024 |
| `gpf_builder/gpf_builder/services/branding_asset_service.py` | Validate existing branding files. | FR-034–FR-037 |
| `gpf_builder/gpf_builder/services/svg_sanitizer_service.py` | Sanitize or reject SVG assets. | Security Design |
| `gpf_builder/gpf_builder/services/ocr_service.py` | Run OCR via integration adapter and store results. | FR-028–FR-033 |
| `gpf_builder/gpf_builder/services/ocr_confirmation_service.py` | Confirm OCR text and metadata. | FR-031–FR-032 |
| `gpf_builder/gpf_builder/services/preview_service.py` | Generate sanitized preview. | FR-038–FR-043 |
| `gpf_builder/gpf_builder/services/output_generation_service.py` | Generate copy-ready Print Format output. | FR-046 |
| `gpf_builder/gpf_builder/services/validation_service.py` | Centralize reusable validations. | Validation Design |
| `gpf_builder/gpf_builder/services/finalization_service.py` | Enforce finalization and return-to-editing. | DD-008 |
| `gpf_builder/gpf_builder/services/version_history_service.py` | Create immutable version snapshots. | FR-049–FR-051 |
| `gpf_builder/gpf_builder/services/audit_log_service.py` | Write sanitized audit events. | Logging Design |
| `gpf_builder/gpf_builder/services/rate_limit_service.py` | Apply rate limits. | Security Design |
| `gpf_builder/gpf_builder/domain/*.py` | Store constants, validation codes, block types, and output model definitions. | Clean Code |
| `gpf_builder/gpf_builder/doctype/gpf_print_format_setup/*` | Define setup DocType and controller. | Database Design |
| `gpf_builder/gpf_builder/doctype/gpf_layout_block/*` | Define layout block DocType and controller. | Database Design |
| `gpf_builder/gpf_builder/doctype/gpf_ocr_result/*` | Define OCR result DocType and controller. | Database Design |
| `gpf_builder/gpf_builder/doctype/gpf_version_history/*` | Define version history DocType and controller. | Database Design |
| `gpf_builder/gpf_builder/doctype/gpf_audit_event/*` | Define audit event DocType and controller. | Logging Design |
| `gpf_builder/gpf_builder/public/js/builder_page.js` | Implement builder UI orchestration. | UI Screen Design |
| `gpf_builder/gpf_builder/public/js/preview_page.js` | Implement preview comparison UI. | UI Screen Design |
| `gpf_builder/gpf_builder/public/css/builder.css` | Implement approved builder layout styles. | UI Screen Design |
| `gpf_builder/gpf_builder/templates/pages/gpf_builder.html` | Render builder page shell. | UI Screen Design |
| `gpf_builder/gpf_builder/integrations/google_vision_client.py` | Encapsulate Google Vision API calls. | IR-005 |
| `gpf_builder/gpf_builder/utils/*.py` | Provide technical helpers only, no business rules. | Clean Code |
| `gpf_builder/tests/*` | Add unit, integration, API, security, and E2E tests. | Validation/Security Design |
| `docs/*` | Add developer, admin, and security operations documentation. | Documentation Tasks |

## 5. Database Migration Tasks

- Create DocType JSON and controller files for `GPF Print Format Setup`.
- Create DocType JSON and controller files for `GPF Layout Block`.
- Create DocType JSON and controller files for `GPF OCR Result`.
- Create DocType JSON and controller files for `GPF Version History`.
- Create DocType JSON and controller files for `GPF Audit Event`.
- Add permissions denying all non-Administrator access.
- Add migration patch for single active setup creation.
- Add migration patch or validation to enforce `target_doctype = Dunning Letter`.
- Add indexes for setup relationships, status filtering, version ordering, and audit timestamps.
- Add fixtures for custom DocType permissions if required by the Frappe project.
- Add migration tests verifying idempotent patch behavior.

## 6. Backend Implementation Tasks

- Implement API facades with no business logic beyond request parsing and service orchestration.
- Implement `AccessControlService` and enforce it in every API and service boundary.
- Implement `SetupService` for one active setup, status, and target DocType checks.
- Implement `PdfReferenceService` for PDF validation and private storage.
- Implement `LayoutBlockService` for normalized block persistence.
- Implement `FieldMappingService` for `Dunning Letter` metadata only.
- Implement `BrandingAssetService` and `SvgSanitizerService`.
- Implement `OcrService`, `OcrConfirmationService`, and Google Vision adapter.
- Implement `PreviewService` with sanitization and sample data.
- Implement `ValidationService` for common and finalization validations.
- Implement `FinalizationService` with state transitions and invalidation behavior.
- Implement `OutputGenerationService` with allowlisted HTML/CSS/Jinja.
- Implement `VersionHistoryService` for immutable snapshots.
- Implement `AuditLogService` with sensitive data redaction.
- Implement `RateLimitService` with design-defined limits.

## 7. Frontend Implementation Tasks

- Implement Frappe Desk page shell and route access feedback.
- Implement Builder Home Screen.
- Implement PDF upload panel and PDF.js viewer.
- Implement layout canvas using approved canvas/SVG helper library.
- Implement block toolbar and properties panel.
- Implement dynamic field selector from backend `Dunning Letter` metadata.
- Implement OCR review and confirmation panel.
- Implement branding file selection UI using existing file references.
- Implement validation issue panel.
- Implement Preview Comparison Screen.
- Implement similarity confirmation UI.
- Implement Final Output Screen with copy-ready display.
- Implement Version History Screen as read-only.
- Implement loading, empty, and error states.
- Ensure UI never contains finalization business logic.

## 8. Integration Tasks

- Integrate frontend screens with Frappe whitelisted APIs.
- Integrate PDF upload flow with private Frappe File records.
- Integrate PDF.js rendering with saved PDF reference.
- Integrate layout editor data model with `save_layout` API.
- Integrate field selector with `get_dunning_letter_fields`.
- Integrate OCR flow with Google Vision backend adapter.
- Integrate branding selector with existing Frappe File records.
- Integrate preview generation with server-side sanitizer.
- Integrate finalization flow with validation and state locking.
- Integrate output generation with finalized setup only.
- Integrate version history screen with immutable snapshot records.
- Integrate audit logging and rate limiting across all sensitive endpoints.

## 9. Validation Implementation Tasks

- Validate Administrator-only access at UI, API, service, and DocType levels.
- Validate target DocType is always `Dunning Letter`.
- Validate one active setup for MVP.
- Validate PDF extension, MIME, content, readability, protection state, page count, size, and private storage.
- Validate layout block type, coordinates, positive dimensions, page bounds, style allowlist, and non-blank content.
- Validate dynamic fields exist on `Dunning Letter`.
- Validate duplicate dynamic field use is allowed.
- Validate OCR text confirmation before finalization if OCR text is used.
- Validate branding files exist, are accessible, and are allowed types.
- Validate SVG safety before preview and output.
- Validate preview was generated before finalization.
- Validate 90% similarity was Administrator-confirmed before finalization.
- Validate overlapping blocks block finalization per resolved design.
- Validate final output against HTML/CSS/Jinja allowlists.

## 10. Error Handling Tasks

- Implement stable error codes from the approved error handling design.
- Return `ACCESS_DENIED` for unauthorized access.
- Return `GUEST_NOT_ALLOWED` for guest access where applicable.
- Return `INVALID_TARGET_DOCTYPE` for any non-`Dunning Letter` target request.
- Return `SETUP_NOT_FOUND` for missing active setup.
- Return `SETUP_FINALIZED` for invalid edit attempts.
- Return PDF-specific error codes for invalid, large, unreadable, protected, or multi-page PDFs.
- Return branding-specific error codes for invalid and unsafe files.
- Return OCR-specific error codes for missing config, rate limit, and provider failure.
- Return `OUTPUT_UNSAFE` when preview or final output sanitization blocks content.
- Sanitize all API error messages.
- Exclude stack traces, credentials, private paths, OCR text, raw files, and full generated output from errors.

## 11. Security Implementation Tasks

- Enforce exact built-in `Administrator` user only.
- Ensure no `allow_guest=True` whitelisted methods exist for this app.
- Enforce object-level setup scoping on every endpoint.
- Deny non-Administrator DocType access.
- Enforce private PDF storage.
- Enforce `Dunning Letter` hard restriction server-side.
- Enforce finalized-state locking server-side.
- Enforce CSRF/session protections for mutating APIs.
- Enforce rate limits for upload, OCR, preview, save, finalize, output generation, and return-to-editing.
- Store Google Vision credentials only in server-side site configuration or secret manager.
- Ensure credentials are not committed, logged, returned to client, or stored in snapshots.
- Sanitize SVG before preview/output use.
- Sanitize generated preview and output.
- Escape dynamic field output and encode static/OCR text.
- Prohibit arbitrary JavaScript.
- Redact sensitive data from logs and API errors.
- Restrict version history access to built-in `Administrator`.

## 12. Logging and Monitoring Tasks

- Log unauthorized access attempts.
- Log PDF upload success and failure.
- Log OCR start, failure, and confirmation.
- Log save completion and version snapshot creation.
- Log finalization failure and completion.
- Log return-to-editing.
- Log output generation failure and completion.
- Log rate-limit violations.
- Log unsafe SVG and unsafe output blocks.
- Store security audit events for at least 365 days.
- Retain error logs for at least 90 days.
- Retain version history with setup unless business deletion is approved.
- Add alert threshold checks for:
  - 5 unauthorized attempts in 10 minutes.
  - 3 OCR provider failures in 15 minutes.
  - 5 rate-limit hits in 10 minutes.
  - Any unsafe SVG or unsafe output block event.
- Ensure logs omit credentials, full private paths, full OCR text, raw files, full warning-letter content, and full generated output except intentional version snapshots.

## 13. Documentation Tasks

- Write developer setup documentation.
- Write configuration documentation for Google Vision and rate limits.
- Write database migration notes.
- Write API contract documentation with request/response/error codes.
- Write Administrator usage documentation.
- Write security operations documentation.
- Write logging and retention documentation.
- Write troubleshooting notes for PDF validation, OCR failure, preview failure, and output blocking.
- Write known limitations and out-of-scope documentation.
- Write QA handoff notes.

## 14. Developer Notes

- Do not change approved requirements during implementation.
- Do not introduce non-Administrator access.
- Do not introduce multiple saved formats.
- Do not introduce multi-page PDF support.
- Do not introduce batch generation or invoice attachment workflows.
- Do not treat OCR as authoritative.
- Do not place finalization rules in frontend JavaScript.
- Do not use arbitrary DocType metadata access.
- Do not add JavaScript to generated Print Format output.
- Do not store binary files in version snapshots.
- Do not log sensitive data.
- Use services for business logic and validators for validation.
- Use API modules as thin orchestration layers.
- Add tests for every security-sensitive rule before a task is marked complete.

## 15. Definition of Done

Implementation planning is done when:

- Development phases are clearly ordered.
- Every implementation task traces to a requirement, analysis decision, or design section.
- File-level changes are identified.
- Database migration tasks are identified.
- Backend and frontend tasks are separated.
- Validation, error handling, security, logging, monitoring, documentation, and testing tasks are included.
- Each task is verifiable.
- Review checkpoints exist after every phase.
- Clean Code Execution Standard is included.
- No production code is written in this stage.
- Scope remains unchanged from approved requirements, analysis, and design.

Product implementation is done when:

- All planned database migrations run successfully and idempotently.
- All custom DocType permissions deny non-Administrator access.
- All backend services pass unit and integration tests.
- All frontend workflows match approved UI screen design.
- All APIs enforce Administrator-only access, object scoping, rate limits, state locks, and stable errors.
- PDF, OCR, field mapping, branding, preview, finalization, output, version history, audit logging, and return-to-editing flows pass end-to-end tests.
- Generated output passes Print Format compatibility and sanitizer checks.
- Security tests pass for access control, sanitizer, rate limiting, log redaction, private files, secrets, and finalized-state bypass.
- Documentation is complete for developers, administrators, operations, and QA.

## 16. Stage Gate Checklist

| Checklist Item | Status |
| --- | --- |
| Development phases are clear | Complete |
| Tasks are traceable to design | Complete |
| File-level changes are identified | Complete |
| Database changes are planned | Complete |
| Backend and frontend tasks are separated | Complete |
| Validation tasks are included | Complete |
| Error handling tasks are included | Complete |
| Security tasks are included | Complete |
| Logging and monitoring tasks are included | Complete |
| Documentation tasks are included | Complete |
| Testing tasks are included | Complete |
| Definition of Done is clear | Complete |
| Review checkpoints are included after each phase | Complete |
| Clean Code Execution Standard is included | Complete |
| No code is produced | Complete |
| Approved requirements are unchanged | Complete |
| Approved system analysis is unchanged | Complete |
| Approved system design is unchanged | Complete |

## Handoff to QA Tester

Use this Implementation Plan, System Design Document, System Analysis Document, and Requirements Document as the source for Testing Planning.
