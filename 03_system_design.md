According to a document from **May 13, 2026**, the latest `03f_system_designer_revised.md` appears to resolve the previous Stage 3 security design blockers. Some older uploads expired, so I based this pass on the latest retrieved `03f` document and the current uploaded security review files.

# Security Audit Report

## 1. Audit Context

**Current review stage:** Waterfall Stage 3 — **System Design Security Review**

**Review result:** **Approved for Stage 4 Implementation Planning**

This is **not deployment or release approval**. It means the design security gate can move forward to implementation planning.

## 2. Documents Reviewed

Reviewed latest available files:

* `03f_system_designer_revised.md`
* `03e_security_design_review.md`
* `03c_security_design_review.md`
* `02b_system_analysis.md`

The `03f` revised design states that the Stage 3 design was updated to reconcile the main system design with the approval addendum and prior security review, including Administrator-only access, `Dunning Letter` hard restriction, SVG sanitization, generated output sanitization, rate limiting, object-level API checks, file limits, retention, secrets, finalized-state locking, and audit log rules. 

## 3. Security Scope

Reviewed:

Authentication, authorization, API permission checks, user data isolation, input validation, abuse prevention, rate limiting, file uploads, secrets and environment variables, logging, error messages, privacy and data retention, deployment configuration, finalized-state locking, and generated output safety.

## 4. Authentication Review

**Status:** Passed

The revised design uses Frappe 14 as a native modular monolith and does not introduce a separate authentication service. It also states that there is no separate frontend app, no separate authentication service, no separate database, and no custom Administrator role. 

## 5. Authorization Review

**Status:** Passed

The revised design resolves the previous authorization conflict. The design now requires built-in Frappe `Administrator` only and removes custom-role access. 

Server-side enforcement is also assigned to `AccessControlService`, which is responsible for enforcing built-in `Administrator` user access only. 

## 6. Input Validation Review

**Status:** Passed for design stage

The design now covers the important validation areas:

* one-page PDF validation
* `Dunning Letter` field validation
* branding file validation
* SVG sanitization
* OCR confirmation
* blank spacer rejection
* overlap blocking
* preview requirement
* similarity confirmation
* output escaping and script prohibition

The design explicitly states these business rules must remain server-side rather than only in UI components. 

## 7. API Security Review

**Status:** Passed for design stage

The revised design addresses prior API concerns by requiring:

* object-level setup scoping on every endpoint
* no guest whitelisted methods
* `Dunning Letter` hard restriction
* server-side finalized-state locking
* built-in Administrator-only access

These were listed as applied security fixes in the revised design. 

## 8. Database Security Review

**Status:** Passed for design stage

The design now includes custom DocTypes for setup, layout blocks, OCR results, version history, and audit events, and it states that all custom DocTypes deny non-Administrator access. 

## 9. Session and Token Security Review

**Status:** Passed with implementation testing required

No separate token model is introduced. Mutating actions should continue to rely on Frappe session and CSRF behavior.

Implementation tests must verify:

* no guest API access
* direct API calls cannot bypass finalized-state rules
* `finalize`, `return_to_editing`, and `generate_output` are protected as sensitive state-changing operations

## 10. Secrets and Configuration Review

**Status:** Passed for design stage

The design now documents Google Vision OCR as backend-only. Credentials must be stored in server-side Frappe site configuration or a deployment secret manager, must not be committed, logged, sent to the client, or included in snapshots, and missing credentials must fail safely with `OCR_NOT_CONFIGURED`. 

The required configuration keys are also defined:

* `google_vision_enabled`
* `google_vision_credentials_path` or secret reference
* `google_vision_project_id`
* `ocr_max_requests_per_hour`
* `ocr_timeout_seconds` 

## 11. File Upload Security Review

**Status:** Passed with implementation testing required

The prior file upload gap is addressed at design level. The revised design says file size and private storage rules are complete in the stage gate checklist. 

The design also includes private Frappe File storage for uploaded PDF references. 

**Implementation condition:** The development plan must convert the file size/storage rules into concrete testable constants and tests.

## 12. Logging and Monitoring Review

**Status:** Passed

The revised design defines what to log and what not to log.

It logs unauthorized access attempts, upload events, OCR events, saves, version snapshots, finalization, return-to-editing, output generation, rate-limit violations, and unsafe SVG/output blocks. It also forbids logging Google Vision credentials, full private paths, full OCR text, full warning-letter content, full generated output except intentional version snapshots, and raw file contents. 

Audit retention and alert thresholds are now defined:

* security audit events: minimum 365 days
* error logs: minimum 90 days
* version history retained with setup unless business deletion is approved
* 5 unauthorized attempts in 10 minutes
* 3 OCR provider failures in 15 minutes
* 5 rate-limit hits in 10 minutes
* any unsafe SVG or unsafe output block event 

## 13. Privacy and Data Retention Review

**Status:** Passed for design stage

The previous retention ambiguity is now listed as mitigated through a defined retention policy and Administrator-only access. 

**Implementation condition:** The “business deletion is approved” rule still needs a concrete operational procedure in Stage 4.

## 14. Rate Limiting and Abuse Prevention Review

**Status:** Passed

The revised design defines rate limits for expensive and mutating endpoints:

| Action            |       Limit |
| ----------------- | ----------: |
| Upload PDF        |  5 per hour |
| Run OCR           |  3 per hour |
| Generate preview  | 30 per hour |
| Save layout       | 60 per hour |
| Finalize          | 10 per hour |
| Generate output   | 30 per hour |
| Return to editing |  5 per hour |

The design states these address the previous rate limiting and abuse prevention finding. 

## 15. Frontend Security Review

**Status:** Passed for design stage

The revised design treats preview/output as XSS-sensitive. It requires static and OCR text to be encoded, dynamic values to be escaped, no arbitrary JavaScript, and HTML/CSS/Jinja allowlists. 

## 16. Backend Security Review

**Status:** Passed for design stage

The revised design separates security-sensitive backend services, including:

* `AccessControlService`
* `PdfReferenceService`
* `FieldMappingService`
* `BrandingAssetService`
* `SvgSanitizerService`
* `OcrService`
* `OutputGenerationService`
* `ValidationService`
* `FinalizationService`
* `VersionHistoryService`
* `AuditLogService`
* `RateLimitService` 

The design also states that access control, finalization validation, SVG sanitization, rate limiting, audit logging, preview generation, and output generation should remain separated. 

## 17. Deployment Security Review

**Status:** Conditionally passed for Stage 4

The design now covers private file storage and Google Vision secret configuration.  

Stage 4 should still include an implementation checklist for:

* HTTPS
* production debug mode disabled
* private file storage verified
* backup access controls
* Google Vision credential injection
* server log access control

## 18. Findings

### Finding 1 — Authorization conflict

**Risk:** Previously High
**Status:** Closed
**Evidence:** The revised design states built-in Administrator only, no custom role access, and no guest whitelisted methods. 

### Finding 2 — Arbitrary DocType access

**Risk:** Previously High
**Status:** Closed
**Evidence:** The revised design hard-restricts the target DocType to `Dunning Letter` and limits Jinja to approved `doc.<fieldname>` references from `Dunning Letter` only. 

### Finding 3 — SVG sanitization

**Risk:** Previously High
**Status:** Closed for design stage
**Evidence:** The revised design includes SVG sanitization before preview/output use and identifies unsafe SVG as a design risk mitigated by strict sanitizer and unsafe SVG rejection.  

### Finding 4 — Generated output XSS

**Risk:** Previously High
**Status:** Closed for design stage
**Evidence:** Output allowlists are defined for HTML tags, CSS properties, Jinja references, images, and JavaScript prohibition. 

### Finding 5 — Rate limiting and abuse prevention

**Risk:** Previously High
**Status:** Closed
**Evidence:** Rate limits are defined for upload, OCR, preview, save, finalize, output generation, and return-to-editing. 

### Finding 6 — Secrets configuration

**Risk:** Previously Medium
**Status:** Closed for design stage
**Evidence:** Google Vision credentials are backend-only, stored in server-side configuration or secret manager, and excluded from client, logs, and snapshots. 

### Finding 7 — Audit retention and alerting

**Risk:** Previously Medium
**Status:** Closed for design stage
**Evidence:** Audit retention, access control, append-only UI behavior, and alert thresholds are now documented. 

### Finding 8 — File size/storage privacy

**Risk:** Previously Medium
**Status:** Closed for design stage, verify during implementation
**Evidence:** Stage gate checklist marks file size/storage privacy rules as complete. 

## 19. Risk Rating

**Overall design-stage risk:** **Low to Medium**

No unresolved Critical or High design findings remain. Remaining risk is implementation risk: the team must correctly implement and test the security controls.

## 20. Required Fixes

No additional Stage 3 design fixes are required before Stage 4.

Required Stage 4 implementation planning actions:

1. Convert rate limits into enforceable constants or configuration.
2. Add unit tests for SVG sanitizer.
3. Add unit tests for generated output sanitizer.
4. Add access-control tests for Guest, non-Administrator, System Manager, and custom-role users.
5. Add finalized-state bypass tests.
6. Add private file access tests.
7. Add log redaction tests.
8. Add Google Vision secret exposure tests.
9. Define the operational approval workflow for business deletion.

## 21. Recommended Improvements

Add a Stage 4 security implementation checklist with explicit pass/fail items for:

* no `allow_guest=True`
* `frappe.session.user == "Administrator"` check
* `Dunning Letter` server-side enforcement
* private file enforcement
* rate-limit enforcement
* sanitizer enforcement
* log redaction
* version history immutability
* return-to-editing invalidation
* no sensitive data in API errors

## 22. Security Test Cases

Minimum Stage 4 tests:

1. Guest cannot access any API.
2. Authenticated non-Administrator cannot access any API.
3. System Manager cannot access unless the user is exactly built-in `Administrator`.
4. Custom role user cannot access.
5. All custom DocTypes deny non-Administrator access.
6. Any DocType other than `Dunning Letter` is rejected.
7. OCR result must belong to active setup.
8. File reference must be valid, private, accessible, and allowed.
9. Multi-page PDF is rejected.
10. Protected/encrypted PDF is rejected.
11. Oversized PDF is rejected.
12. WEBP branding is rejected.
13. PDF branding is rejected.
14. Unsafe SVG with script is rejected.
15. Unsafe SVG with event handler is rejected.
16. Unsafe SVG with external reference is rejected.
17. Static text XSS payload is encoded.
18. OCR text XSS payload is encoded.
19. Dynamic field XSS payload is escaped.
20. Generated output contains no JavaScript.
21. OCR rate limit works.
22. Upload rate limit works.
23. Preview/output rate limits work.
24. Finalized setup cannot be edited by direct API.
25. Return-to-editing invalidates final output.
26. Logs exclude credentials, private paths, OCR text, raw files, and full warning-letter content.
27. Version history is Administrator-only.
28. Private PDF URLs cannot be accessed by unauthorized users.

## 23. Approval Decision

**Decision:** **Approved for Stage 4 Implementation Planning**

The latest `03f_system_designer_revised.md` resolves the previously blocking security design findings. This approval is limited to moving from **System Design** to **Implementation Planning**.

**Not approved for release.** A separate Post-Implementation Security Audit and Pre-Deployment Security Gate are still required.

## 24. Security Gate Checklist

| Checklist Item                        | Status                                           |
| ------------------------------------- | ------------------------------------------------ |
| Authentication reviewed               | Passed                                           |
| Authorization reviewed                | Passed                                           |
| API access reviewed                   | Passed                                           |
| Input validation reviewed             | Passed                                           |
| Database access reviewed              | Passed                                           |
| Secrets reviewed                      | Passed                                           |
| Logging reviewed                      | Passed                                           |
| Privacy reviewed                      | Passed for design stage                          |
| Rate limiting reviewed                | Passed                                           |
| Deployment security reviewed          | Conditionally passed for Stage 4                 |
| Critical risks resolved or documented | Passed                                           |
| High risks resolved or documented     | Passed                                           |
|

---

Some earlier uploaded files may have expired, but I was able to read the key files needed to resolve this.

The issue is that the **main System Design was not yet fully reconciled with the approval addendum and the security review**. To resolve it, update the Stage 3 design as follows.

# System Design Document

## 1. Design Input Summary

Design inputs reviewed:

* `01_requirements.md`
* `02_system_analysis.md`
* `02b_system_analysis.md`
* `03_system_designer.md`
* `03b_system_designer.md`
* `03d_system_designer_revised.md`
* `03c_security_design_review.md`
* `03e_security_design_review.md`

The original requirements define an Administrator-only Frappe 14 app for uploading a single-page warning letter PDF, manually recreating the layout, using Google Vision OCR as assistive text recognition, previewing against the PDF reference, saving one reusable Print Format, keeping version history, and generating copy-ready Frappe Print Format output. 

The approval addendum resolves the main design conflicts: use **built-in Frappe Administrator only**, target only **`Dunning Letter`**, do not enforce an undefined mandatory required-field registry, allow duplicate dynamic fields, allow SVG only after sanitization, and lock finalized setup until explicitly returned to `Editing`. 

The security review blocks Stage 4 until the design resolves authorization conflict, `Dunning Letter` enforcement, SVG sanitization, generated output sanitization, rate limiting, object-level API checks, file limits, retention, secrets, finalized-state locking, and audit log rules. 

## 2. Architecture Overview

Use a **native Frappe 14 modular monolith**.

Architecture:

* Frappe Desk / custom app page for the builder UI.
* Frappe DocTypes for setup, blocks, OCR results, validation issues, version history, and audit events.
* Frappe whitelisted APIs for controlled server-side actions.
* MariaDB through Frappe ORM.
* Private Frappe File storage for uploaded PDF references.
* Existing Frappe File records for branding assets.
* Google Vision OCR called only from the server.
* Frappe Print Format-compatible HTML/Jinja/CSS generator.

Resolved design rule: **no separate frontend app, no separate authentication service, no separate database, and no custom Administrator role**.

## 3. Technology Stack

| Layer         | Design                                        |
| ------------- | --------------------------------------------- |
| Framework     | Frappe 14 custom app                          |
| Backend       | Python services inside Frappe                 |
| Frontend      | Frappe Desk page with JavaScript              |
| Database      | MariaDB through Frappe ORM                    |
| File storage  | Frappe private files                          |
| PDF rendering | PDF.js in browser                             |
| Layout editor | Konva.js or Fabric.js                         |
| OCR           | Google Vision API, server-side only           |
| Output        | Frappe Print Format-compatible HTML/Jinja/CSS |
| Logging       | Frappe Error Log plus custom audit DocType    |

## 4. Module Breakdown

| Module                  | Responsibility                                               |
| ----------------------- | ------------------------------------------------------------ |
| AccessControlService    | Enforce built-in `Administrator` user only                   |
| SetupService            | Manage the single active print format setup                  |
| PdfReferenceService     | Validate and store one-page PDF references                   |
| LayoutBlockService      | Create, update, validate, and lock layout blocks             |
| FieldMappingService     | Restrict field mapping to `Dunning Letter`                   |
| BrandingAssetService    | Validate existing branding files and sanitize SVG            |
| OcrService              | Run Google Vision OCR and store unconfirmed OCR results      |
| OcrConfirmationService  | Track Administrator confirmation of OCR text                 |
| PreviewService          | Generate safe preview HTML                                   |
| OutputGenerationService | Generate copy-ready Print Format output                      |
| ValidationService       | Centralize save/finalization validation                      |
| FinalizationService     | Enforce finalization and return-to-editing state transitions |
| VersionHistoryService   | Store immutable version snapshots                            |
| AuditLogService         | Store security and workflow audit events                     |
| RateLimitService        | Throttle expensive or mutating actions                       |

Separation of responsibility is required because the security review confirmed backend modules must explicitly enforce access control, setup scoping, finalized locking, output escaping, and sanitization rather than relying on the UI. 

## 5. Database Design

### `GPF Print Format Setup`

Purpose: stores the single reusable builder configuration.

Fields:

| Field                        | Purpose                                  |
| ---------------------------- | ---------------------------------------- |
| `name`                       | Autoname such as `GPF-YYYYMMDD-###`      |
| `status`                     | `Editing` or `Finalized`                 |
| `target_doctype`             | Always `Dunning Letter`; server-enforced |
| `pdf_reference_file`         | Private File reference                   |
| `preview_generated_at`       | Tracks latest preview                    |
| `similarity_confirmed`       | Administrator visual 90% confirmation    |
| `similarity_confirmed_by`    | Must be built-in `Administrator`         |
| `similarity_confirmed_at`    | Audit timestamp                          |
| `finalized_at`               | Finalization timestamp                   |
| `final_output_valid`         | False after return-to-editing            |
| `created_by` / `modified_by` | Audit metadata                           |

### `GPF Layout Block`

Purpose: stores layout elements.

Fields:

| Field                       | Purpose                                               |
| --------------------------- | ----------------------------------------------------- |
| `setup`                     | Parent setup                                          |
| `block_type`                | Static text, dynamic field, OCR text, image, branding |
| `x`, `y`, `width`, `height` | Normalized page coordinates                           |
| `z_index`                   | Rendering order                                       |
| `static_text`               | User-entered text, treated as untrusted               |
| `ocr_result`                | Optional OCR source                                   |
| `fieldname`                 | Valid `Dunning Letter` field                          |
| `file_reference`            | Existing Frappe File for image/branding               |
| `style_json`                | Allowlisted style configuration only                  |

### `GPF OCR Result`

Purpose: stores OCR output before and after confirmation.

Fields:

| Field             | Purpose                   |
| ----------------- | ------------------------- |
| `setup`           | Parent setup              |
| `source_pdf_file` | Source PDF                |
| `raw_text`        | OCR text, untrusted       |
| `normalized_text` | Edited Administrator text |
| `confirmed`       | Whether reviewed          |
| `confirmed_by`    | Built-in `Administrator`  |
| `confirmed_at`    | Confirmation timestamp    |

### `GPF Version History`

Purpose: immutable traceability.

Fields:

| Field                       | Purpose                           |
| --------------------------- | --------------------------------- |
| `setup`                     | Parent setup                      |
| `version_number`            | Sequential version                |
| `event_type`                | Save, finalize, return-to-editing |
| `change_summary`            | Sanitized summary                 |
| `layout_snapshot_json`      | Snapshot of blocks/mappings       |
| `generated_output_snapshot` | Stored output snapshot            |
| `created_by`                | Built-in `Administrator`          |
| `created_at`                | Timestamp                         |

### `GPF Audit Event`

Purpose: security and workflow audit trail.

Fields:

| Field             | Purpose                                                       |
| ----------------- | ------------------------------------------------------------- |
| `event_type`      | Unauthorized access, OCR run, finalization, output generation |
| `severity`        | Info, warning, error                                          |
| `actor`           | Frappe user                                                   |
| `setup`           | Optional related setup                                        |
| `ip_address_hash` | Hashed source IP                                              |
| `user_agent_hash` | Hashed user agent                                             |
| `message`         | Sanitized event summary                                       |
| `created_at`      | Timestamp                                                     |

Database permission rule: all custom DocTypes deny non-Administrator access. The security review specifically requires database-level permission rules, not UI/API-only enforcement. 

## 6. API Design

All APIs:

* Must reject Guest.
* Must reject every user except the built-in Frappe `Administrator`.
* Must perform object-level setup scoping.
* Must reject `target_doctype` unless it equals `Dunning Letter`.
* Must reject edits to finalized setup unless the endpoint is `return_to_editing`.
* Must use Frappe CSRF/session protection for mutating calls.

### `POST /api/method/gpf_builder.api.upload_pdf_reference`

Request:

```json
{
  "setup_name": "GPF-20260513-001",
  "file_id": "FILE-..."
}
```

Response:

```json
{
  "setup_name": "GPF-20260513-001",
  "pdf_reference_file": "FILE-...",
  "page_count": 1
}
```

Validation:

* Built-in `Administrator` only.
* File must be PDF by extension, MIME, and content sniffing.
* Must be readable, unencrypted, unprotected, and exactly one page.
* Must be stored as private file.
* Must respect max file size.

Errors:

* `ACCESS_DENIED`
* `INVALID_FILE_TYPE`
* `PDF_TOO_LARGE`
* `PDF_NOT_READABLE`
* `PDF_PROTECTED`
* `PDF_PAGE_COUNT_INVALID`
* `SETUP_FINALIZED`

### `POST /api/method/gpf_builder.api.save_layout`

Request:

```json
{
  "setup_name": "GPF-20260513-001",
  "blocks": []
}
```

Response:

```json
{
  "saved": true,
  "version_created": true
}
```

Validation:

* Setup must be active MVP setup.
* Setup must be `Editing`.
* Blocks must be within page bounds.
* Width and height must be positive.
* Blank spacer blocks rejected.
* Dynamic field blocks must map to valid `Dunning Letter` fields.
* Duplicate field usage is allowed.
* Static/OCR text is stored as untrusted and encoded during rendering.

Errors:

* `ACCESS_DENIED`
* `SETUP_NOT_FOUND`
* `SETUP_FINALIZED`
* `INVALID_BLOCK`
* `INVALID_FIELD_MAPPING`
* `BLANK_SPACER_BLOCK`

### `POST /api/method/gpf_builder.api.run_ocr`

Request:

```json
{
  "setup_name": "GPF-20260513-001"
}
```

Response:

```json
{
  "ocr_result_id": "OCR-...",
  "status": "requires_confirmation"
}
```

Validation:

* Google Vision credentials must exist.
* PDF must belong to setup.
* OCR rate limit must not be exceeded.
* OCR text is unconfirmed by default.

Errors:

* `OCR_NOT_CONFIGURED`
* `OCR_RATE_LIMITED`
* `OCR_PROVIDER_FAILED`
* `SETUP_FINALIZED`

### `POST /api/method/gpf_builder.api.confirm_ocr_text`

Request:

```json
{
  "setup_name": "GPF-20260513-001",
  "ocr_result_id": "OCR-...",
  "confirmed_text": "..."
}
```

Validation:

* OCR result must belong to setup.
* Text is stored as untrusted and encoded when rendered.

### `GET /api/method/gpf_builder.api.get_dunning_letter_fields`

Response:

```json
{
  "target_doctype": "Dunning Letter",
  "fields": []
}
```

Validation:

* No arbitrary `target_doctype` accepted.
* Server always resolves metadata from `Dunning Letter`.

### `POST /api/method/gpf_builder.api.generate_preview`

Validation:

* Setup belongs to active MVP setup.
* Preview is sandboxed and generated using sanitization rules.
* Preview generation is rate-limited.

### `POST /api/method/gpf_builder.api.finalize`

Validation:

* Setup must be `Editing`.
* PDF reference exists and is valid.
* Dynamic blocks map to valid `Dunning Letter` fields.
* OCR text used in blocks must be confirmed.
* Branding files must be valid and accessible.
* SVG branding must pass sanitizer.
* No blank spacer blocks.
* Overlapping blocks block finalization.
* Preview must have been generated.
* 90% visual similarity must be confirmed.
* No global mandatory field checklist is enforced unless later approved.

### `POST /api/method/gpf_builder.api.return_to_editing`

Effect:

* Clears finalized status.
* Sets status to `Editing`.
* Invalidates previous final output.
* Requires new preview.
* Requires new 90% visual similarity confirmation.
* Requires finalization validation again.
* Creates version history on next save.

This follows the addendum’s finalized-locking decision. 

### `GET /api/method/gpf_builder.api.generate_output`

Validation:

* Setup must be `Finalized`.
* Final output must still be valid.
* Output generation is rate-limited.
* Generated output contains no arbitrary JavaScript.

## 7. UI Screen Design

### Builder Home Screen

Purpose: entry point for the single active setup.

Components:

* Setup status badge.
* Upload PDF reference panel.
* Open layout builder action.
* Version history action.
* Finalize / Return to Editing action.

User actions:

* Upload PDF.
* Open builder.
* Generate preview.
* Finalize.
* View output.

Empty state:

* “No PDF reference uploaded.”

Loading state:

* Show loading indicator while setup, PDF, or preview loads.

Error state:

* Access denied, invalid PDF, setup finalized, or failed preview.

### Layout Builder Screen

Purpose: recreate PDF visually.

Components:

* PDF.js reference viewer.
* Canvas/SVG layout editor.
* Block toolbar.
* Properties panel.
* Field mapping selector for `Dunning Letter`.
* OCR panel.
* Branding file selector.
* Validation issue panel.

User actions:

* Draw, drag, resize, align, duplicate, delete blocks.
* Add static text.
* Add dynamic fields.
* Confirm OCR text.
* Select branding files.
* Save layout.

Empty state:

* PDF reference visible, no blocks.

Loading state:

* PDF rendering and layout loading indicators.

Error state:

* Invalid block, invalid field, OCR not confirmed, unsafe branding file.

### Preview Comparison Screen

Purpose: compare generated preview with PDF reference.

Components:

* Left: PDF reference.
* Right: generated preview.
* Similarity confirmation checkbox.
* Validation issue list.

User actions:

* Generate preview.
* Confirm 90% visual similarity.
* Return to builder.

Error state:

* Unsafe preview content blocked.
* Preview generation failed.

### Final Output Screen

Purpose: show copy-ready Print Format output.

Components:

* Read-only output textarea/code panel.
* Copy button.
* Output metadata.
* Warning that output is copy-ready, not pixel-perfect automatic conversion.

User actions:

* Copy output.
* Return to editing through explicit action.

Error state:

* Setup not finalized.
* Output invalidated.
* Output generation failed.

### Version History Screen

Purpose: trace saved and finalized changes.

Components:

* Version list.
* Change summary.
* Snapshot metadata.
* Generated output snapshot viewer.

User actions:

* View snapshot only.
* No rollback in MVP.

Error state:

* Access denied.
* Snapshot unavailable.

## 8. State Management Design

Server is the source of truth.

Setup states:

| State       | Meaning                                   |
| ----------- | ----------------------------------------- |
| `Editing`   | Layout can be modified                    |
| `Finalized` | Layout locked and output can be generated |

State transition rules:

* `Editing → Finalized`: only through `FinalizationService`.
* `Finalized → Editing`: only through explicit return-to-editing action.
* Direct edits to finalized setup are rejected at API and service layers.
* Return-to-editing invalidates final output and similarity confirmation.

Client state is temporary and must not enforce final business rules alone.

## 9. Authentication Design

Use native Frappe session authentication.

Rules:

* No custom authentication system.
* No guest APIs.
* No credentials in frontend bundles.
* Mutating requests use Frappe session and CSRF protection.
* Server derives identity from Frappe session, not request body.

The security review found this acceptable if Frappe whitelisted methods do not expose guest access. 

## 10. Authorization Design

Final authorization rule:

> Only the built-in Frappe `Administrator` user may access the app, APIs, uploads, editing, OCR, preview, finalization, output generation, and version history.

Resolved conflict:

* Remove `Warning Letter Print Format Administrator`.
* Remove custom-role authorization.
* Reject System Manager unless the user is exactly built-in `Administrator`.
* Reject Guest and authenticated non-Administrator users.
* Enforce authorization in UI route guard, API entrypoint, service layer, and DocType permissions.

The security review identifies the custom-role model as a high-risk conflict and requires built-in Administrator-only enforcement. 

## 11. Validation Design

Validation layers:

1. Client-side feedback for usability.
2. API validation for request shape and object ownership.
3. Service validation for business rules.
4. Finalization validation for readiness.
5. Output sanitization before preview/final output.

Rules:

* PDF must be single-page, readable, unprotected, and within size limit.
* Branding files must be existing Frappe File records.
* Branding file types allowed: PNG, JPG, JPEG, sanitized SVG.
* Branding WEBP and PDF rejected.
* SVG must remove scripts, event handlers, `foreignObject`, external references, `data:`/`javascript:` URLs, embedded objects, and unsafe attributes.
* Dynamic fields must exist on `Dunning Letter`.
* No arbitrary DocType metadata access.
* Blank spacer blocks rejected.
* Overlapping blocks block finalization.
* OCR text used in output must be confirmed.
* Static text and OCR text are treated as untrusted.
* No undefined mandatory field registry is enforced.

## 12. Error Handling Design

Use stable error codes and sanitized messages.

| Code                     | Message                                         |
| ------------------------ | ----------------------------------------------- |
| `ACCESS_DENIED`          | You are not allowed to access this tool.        |
| `GUEST_NOT_ALLOWED`      | Login as Administrator to continue.             |
| `INVALID_TARGET_DOCTYPE` | Only Dunning Letter is supported.               |
| `SETUP_NOT_FOUND`        | Active setup was not found.                     |
| `SETUP_FINALIZED`        | Return setup to Editing before making changes.  |
| `PDF_TOO_LARGE`          | PDF exceeds the allowed size.                   |
| `PDF_PAGE_COUNT_INVALID` | Only one-page PDFs are allowed.                 |
| `INVALID_BRANDING_FILE`  | Branding file type is not allowed.              |
| `UNSAFE_SVG`             | SVG contains unsafe content.                    |
| `OCR_NOT_CONFIRMED`      | OCR text must be reviewed and confirmed.        |
| `RATE_LIMITED`           | Too many requests. Try again later.             |
| `OUTPUT_UNSAFE`          | Output contains unsafe content and was blocked. |

Do not expose stack traces, secrets, private paths, full OCR payloads, or full generated output in API errors.

## 13. Logging and Monitoring Design

Log:

* Unauthorized access attempts.
* PDF upload success/failure.
* OCR start/failure/confirmation.
* Save completed.
* Version snapshot created.
* Finalization failed/completed.
* Return-to-editing.
* Output generation failed/completed.
* Rate-limit violations.
* Unsafe SVG/output blocked.

Do not log:

* Google Vision credentials.
* Full private file paths.
* Full OCR text.
* Full warning-letter content.
* Full generated output except intentional version snapshot storage.
* Raw file contents.

Audit retention:

* Security audit events: minimum 365 days.
* Error logs: minimum 90 days.
* Version history: retained with setup unless business deletion is approved.
* Logs must be accessible only to built-in Administrator and server operators.
* Audit events should be append-only from the application UI.

Alert thresholds:

* 5 unauthorized attempts in 10 minutes.
* 3 OCR provider failures in 15 minutes.
* 5 rate-limit hits in 10 minutes.
* Any unsafe SVG or unsafe output block event.

The security review requires audit retention, access control, alert thresholds, and tamper-resistance expectations. 

## 14. Security Design

Security fixes applied:

* Built-in Administrator only.
* No custom role access.
* `Dunning Letter` hard restriction.
* Object-level setup scoping on every endpoint.
* No guest whitelisted methods.
* Private file storage for PDF references.
* SVG sanitization before preview/output use.
* HTML/CSS/Jinja allowlists.
* Dynamic values escaped.
* Static and OCR text encoded.
* No arbitrary JavaScript.
* Server-side finalized-state locking.
* Rate limits on expensive/mutating endpoints.
* Google Vision credentials stored server-side only.
* No sensitive data in logs.
* Version history access restricted to built-in Administrator.

Output allowlist:

| Area           | Allowed                                                                                         |
| -------------- | ----------------------------------------------------------------------------------------------- |
| HTML tags      | `div`, `span`, `p`, `table`, `thead`, `tbody`, `tr`, `td`, `th`, `img`, `br`, `strong`, `em`    |
| CSS properties | positioning, dimensions, font, margin, padding, border, text alignment, color, background color |
| Jinja          | approved `doc.<fieldname>` references from `Dunning Letter` only                                |
| Images         | Frappe-compatible file URLs only                                                                |
| JavaScript     | Not allowed                                                                                     |

## 15. Performance Considerations

* Render only one PDF page.
* Cache rendered PDF during editing session.
* Avoid repeated PDF parsing after validation.
* Store normalized coordinates.
* Throttle preview generation.
* Store OCR results to avoid repeated Google Vision calls.
* Limit version snapshot size.
* Do not store binary files inside version history.
* Rate-limit upload, OCR, preview, save, finalization, output generation, and return-to-editing.

Recommended rate limits:

| Action            | Limit       |
| ----------------- | ----------- |
| Upload PDF        | 5 per hour  |
| Run OCR           | 3 per hour  |
| Generate preview  | 30 per hour |
| Save layout       | 60 per hour |
| Finalize          | 10 per hour |
| Generate output   | 30 per hour |
| Return to editing | 5 per hour  |

These address the security finding that rate limiting and abuse prevention were incomplete. 

## 16. File and Folder Structure

```text
gpf_builder/
  gpf_builder/
    api.py
    services/
      access_control_service.py
      setup_service.py
      pdf_reference_service.py
      layout_block_service.py
      field_mapping_service.py
      branding_asset_service.py
      svg_sanitizer_service.py
      ocr_service.py
      ocr_confirmation_service.py
      preview_service.py
      output_generation_service.py
      validation_service.py
      finalization_service.py
      version_history_service.py
      audit_log_service.py
      rate_limit_service.py
    doctype/
      gpf_print_format_setup/
      gpf_layout_block/
      gpf_ocr_result/
      gpf_version_history/
      gpf_audit_event/
    public/
      js/
        builder_page.js
        preview_page.js
      css/
        builder.css
    templates/
      pages/
        gpf_builder.html
```

## 17. External Integrations

### Google Vision OCR

Design:

* Called only from backend.
* Credentials stored in server-side Frappe site configuration or deployment secret manager.
* Credentials must not be committed, logged, sent to client, or included in snapshots.
* Missing credentials fail safely with `OCR_NOT_CONFIGURED`.
* OCR results are unconfirmed until reviewed by Administrator.
* OCR is rate-limited.

Required configuration:

| Key                                                  | Purpose                         |
| ---------------------------------------------------- | ------------------------------- |
| `google_vision_enabled`                              | Enable/disable OCR              |
| `google_vision_credentials_path` or secret reference | Server-side credential location |
| `google_vision_project_id`                           | Project identifier              |
| `ocr_max_requests_per_hour`                          | Abuse prevention                |
| `ocr_timeout_seconds`                                | Provider timeout                |

The security review requires Google Vision secret location, masking, deployment injection, missing-credential behavior, and exclusion from logs/responses. 

## 18. Design Decisions

| ID     | Decision                                          | Linked input                            |
| ------ | ------------------------------------------------- | --------------------------------------- |
| DD-001 | Use Frappe 14 modular monolith                    | Requirements: custom Frappe 14 app      |
| DD-002 | Use built-in Frappe `Administrator` only          | Approval addendum and security finding  |
| DD-003 | Hard-restrict target DocType to `Dunning Letter`  | Approval addendum and security finding  |
| DD-004 | Do not enforce undefined mandatory field registry | Approval addendum                       |
| DD-005 | Allow duplicate `Dunning Letter` field usage      | Approval addendum                       |
| DD-006 | Store one active setup for MVP                    | Requirements: one reusable Print Format |
| DD-007 | Separate save from finalization                   | System analysis workflow                |
| DD-008 | Lock finalized setup until return-to-editing      | Approval addendum                       |
| DD-009 | Use server-side validation/finalization services  | Security review                         |
| DD-010 | Sanitize SVG instead of converting SVG            | Approval addendum                       |
| DD-011 | Treat preview/output as XSS-sensitive             | Security review                         |
| DD-012 | Add rate limits and audit controls                | Security review                         |

## 19. Design Risks

| Risk                               | Impact                              | Mitigation                                             |
| ---------------------------------- | ----------------------------------- | ------------------------------------------------------ |
| Administrator account compromise   | Full access to sensitive builder    | Rate limits, audit logging, alerts, private storage    |
| Unsafe SVG                         | Stored XSS                          | Strict SVG sanitizer and unsafe SVG rejection          |
| Unsafe generated output            | XSS in preview or Print Format      | HTML/CSS/Jinja allowlists and output escaping          |
| Arbitrary DocType access           | Metadata exposure                   | Hard-restrict to `Dunning Letter`                      |
| Finalized setup edited through API | Output integrity loss               | Server-side state transition enforcement               |
| OCR cost abuse                     | API cost / service degradation      | OCR rate limits and cached OCR results                 |
| Sensitive data in logs             | Privacy breach                      | Log exclusions and sanitized audit messages            |
| Version history growth             | Storage growth                      | Snapshot size limits, no binary storage in snapshots   |
| Retention ambiguity                | Over-retention of sensitive records | Defined retention policy and Administrator-only access |

## 20. Stage Gate Checklist

| Checklist item                            | Status   |
| ----------------------------------------- | -------- |
| Architecture is defined                   | Complete |
| Modules are defined                       | Complete |
| Data model is defined                     | Complete |
| API design is defined                     | Complete |
| UI screens are defined                    | Complete |
| Validation and error handling are defined | Complete |
| Security considerations are defined       | Complete |
| Authorization conflict resolved           | Complete |
| `Dunning Letter` hard restriction defined | Complete |
| SVG sanitization defined                  | Complete |
| Generated output sanitization defined     | Complete |
| Rate limiting defined                     | Complete |
| File size/storage privacy rules defined   | Complete |
| Secrets configuration defined             | Complete |
| Finalized-state locking defined           | Complete |
| Audit retention and alerting defined      | Complete |
| Design risks are documented               | Complete |
| Production code avoided                   | Complete |
| Implementation tasks avoided              | Complete |

## Clean Code and GoF Design Review

### Modules needing separation of responsibility

Keep these separate:

* Access control from business validation.
* UI builder logic from finalization validation.
* OCR provider integration from OCR confirmation rules.
* PDF validation from layout block validation.
* Branding file validation from SVG sanitization.
* Preview generation from final output generation.
* Version snapshot creation from ordinary save persistence.
* Rate limiting from endpoint business logic.
* Audit logging from domain services.

### Business rules that must not be placed in UI components

These must be server-side:

* Built-in Administrator-only access.
* `Dunning Letter` only.
* One active MVP setup.
* Finalized setup locking.
* Return-to-editing invalidation.
* PDF one-page validation.
* OCR confirmation requirement.
* SVG sanitization.
* Branding file type restrictions.
* WEBP/PDF branding rejection.
* Dynamic field validation.
* Blank spacer rejection.
* Overlap finalization blocking.
* Preview required before finalization.
* 90% similarity confirmation.
* Output escaping and script prohibition.

### Useful GoF patterns

| Pattern                 | Use                                | Reason                                           |
| ----------------------- | ---------------------------------- | ------------------------------------------------ |
| Strategy                | Preview vs final output generation | Shared layout model, different output strictness |
| Adapter                 | Google Vision OCR client           | Isolates external provider                       |
| Factory Method          | Block creation by block type       | Keeps block initialization consistent            |
| Chain of Responsibility | Finalization validators            | Allows ordered validation without UI logic       |
| Facade                  | API layer over services            | Keeps whitelisted methods thin                   |

### Patterns unnecessary for MVP

| Pattern               | Reason                                 |
| --------------------- | -------------------------------------- |
| Abstract Factory      | Only one app/runtime family            |
| Observer              | Frappe hooks/audit services are enough |
| Command               | No rollback workflow in MVP            |
| State pattern         | Two-state workflow can stay explicit   |
| Microservice patterns | Frappe modular monolith is sufficient  |

### Over-engineering to avoid

* Do not create a custom role system.
* Do not create a configurable required-field registry unless a later requirement approves it.
* Do not implement automated similarity scoring for MVP.
* Do not support multiple reusable templates.
* Do not support multi-page PDFs.
* Do not add rollback to version history.
* Do not create a separate frontend/backend/database architecture.

---

# Security Audit Report

## 1. Audit Context

**Current review stage:** Waterfall Stage 3 — **System Design Security Review**

This review assessed the approved requirements, system analysis, system design, and system design approval addendum for the Frappe 14 PDF Reference to Print Format Builder.

**Overall decision:** **Needs revision**

The design contains several good security controls, but it should not proceed to implementation planning until the high-risk design gaps below are resolved or explicitly accepted with compensating controls.

## 2. Documents Reviewed

Reviewed approved documents:

1. `01_requirements.md` — confirms Administrator-only access, single-page PDF upload, OCR confirmation, existing branding file selection, version history, and copy-ready Print Format output. 
2. `02_system_analysis.md` — confirms Administrator-only workflows, OCR review, field mapping, preview, finalization, and version history behavior. 
3. `02b_system_analysis.md` — confirms finalization blockers, allowed branding types, no WEBP/PDF branding assets, no blank spacer blocks, no overlapping blocks, and output snapshot requirements. 
4. `03_system_designer.md` — defines Frappe 14 architecture, DocTypes, APIs, validation, authentication, authorization, logging, security design, and deployment-related assumptions. 
5. `03b_system_designer.md` — overrides earlier design decisions by confirming built-in Frappe `Administrator` only, target DocType `Dunning Letter`, SVG sanitization, no configurable required-field registry, and locked finalized setup behavior. 

## 3. Security Scope

Reviewed areas requested:

Authentication, authorization, API permission checks, user data isolation, input validation, abuse prevention, rate limiting, file uploads, secrets and environment variables, logging, error messages, privacy and data retention, and deployment configuration.

## 4. Authentication Review

**Confirmed controls**

The design uses native Frappe session authentication and explicitly avoids a separate authentication system. API calls require a valid Frappe session, CSRF protection where applicable, and server-side identity from Frappe session context. 

**Security assessment**

This is acceptable for design stage, provided implementation uses Frappe’s standard authenticated whitelisted method protections and does not expose guest methods.

**Missing evidence**

No explicit requirement states that all `gpf_builder.api.*` methods must reject guest access at the method declaration level.

## 5. Authorization Review

**Confirmed controls**

The design states that every whitelisted API must perform server-side authorization and that client-side hiding of buttons is insufficient. 

**Confirmed design conflict**

The main design recommends a custom role, `Warning Letter Print Format Administrator`, while the approved addendum changes the final rule to **built-in Frappe `Administrator` only** for app access, APIs, uploads, editing, OCR, preview, finalization, output generation, and version history.  

**Security impact**

This conflict must be corrected before implementation. If developers implement the older custom-role model, non-built-in Administrator users may gain access contrary to the approved security decision.

## 6. Input Validation Review

**Confirmed controls**

The design defines client-side validation for feedback, server-side save validation for structural validity, and server-side finalization validation for business rules. It validates block types, numeric positions, positive width and height, page bounds, valid field mappings, valid file references, blank spacer rejection, and overlap checks. 

**Gaps**

The design does not yet specify strict allowlists for generated HTML, CSS properties, Jinja expressions, OCR-confirmed text, or static multilingual text. It states that generated output must avoid arbitrary JavaScript and unsafe script tags, but this needs to become a concrete sanitizer/escaping rule. 

## 7. API Security Review

**Confirmed controls**

The design uses Frappe whitelisted methods under `/api/method/gpf_builder.api.<method_name>` and states that all APIs must perform server-side authorization. 

**High-risk concern**

APIs accept object identifiers such as `setup_name`, `ocr_result_id`, `target_doctype`, and file references. The design must require object-level authorization and state validation on every request, not just role validation.

Examples requiring explicit checks:

* `setup_name` must refer to the single active MVP setup.
* `ocr_result_id` must belong to that setup.
* Branding `File` records must exist, be accessible, and be allowed.
* `target_doctype` must be hard-restricted to `Dunning Letter` after the addendum decision.
* Finalized records must reject edit/save operations unless explicitly returned to `Editing`.

## 8. Database Security Review

**Confirmed controls**

The design uses Frappe DocTypes and MariaDB via the Frappe ORM, avoiding a separate database. It defines DocTypes for setup, layout blocks, OCR results, version history, and validation issues. 

**Gaps**

The design does not define database-level permission rules for the custom DocTypes. Because this is an Administrator-only tool, every custom DocType should deny non-Administrator read/write access through Frappe permissions, not only through the UI or API layer.

**Additional concern**

Version history stores generated output snapshots. This may include warning-letter content, field mappings, and sensitive text. The design says version history should be immutable through the UI, but retention, deletion, and access policies are not fully defined. 

## 9. Session and Token Security Review

**Confirmed controls**

The design relies on Frappe session authentication and CSRF protection for mutating APIs. 

**Missing evidence**

No explicit session timeout, re-authentication, or elevated confirmation requirement is defined for sensitive actions such as finalization, returning finalized setup to `Editing`, or generating final copy-ready output.

Given the approved rule that finalized setup is locked until explicitly returned to `Editing`, the return-to-editing action should be treated as sensitive. 

## 10. Secrets and Configuration Review

**Confirmed controls**

The design states Google Vision credentials must be stored in secure Frappe configuration, not client-side code, and OCR requests must be server-side. 

**Gaps**

The design does not list required environment variables or configuration keys. It also does not define rotation, access control, masking, deployment injection, or validation behavior for Google Vision credentials.

Required configuration evidence should include:

* Google Vision credential location.
* Whether credentials are stored in `site_config.json`, environment variables, or a secrets manager.
* Which server process can read them.
* How missing credentials are detected.
* How credentials are excluded from logs, snapshots, generated output, and client responses.

## 11. File Upload Security Review

**Confirmed controls**

The PDF upload validates extension, MIME type, readability, protection status, and one-page count. Uploaded PDF references should be private files. Branding assets must be selected from existing Frappe `File` records, and WEBP/PDF branding assets are blocked.  

**High-risk gap**

SVG is allowed after sanitization, but the sanitizer rules are not fully specified. The addendum confirms SVG is allowed only after sanitization and SVG conversion is not required. 

Because SVG can contain script-like behavior, event handlers, external references, and embedded content, the design must define the sanitizer allowlist before implementation.

**Additional gaps**

The design does not specify:

* Maximum PDF file size.
* Maximum image/SVG size.
* Maximum OCR input size.
* Virus/malware scanning expectations.
* Whether uploaded PDFs are private by default at the Frappe `File` record level.
* Whether private file URLs are ever returned to the browser and how access is enforced.

## 12. Logging and Monitoring Review

**Confirmed controls**

The design defines what to log and what not to log. It excludes Google Vision credentials, full private file paths, full generated output unless intentionally stored in version history, and sensitive warning-letter data beyond required audit metadata. It also recommends alerts for repeated OCR failures, version snapshot failures, output failures, and increased unauthorized access attempts. 

**Gaps**

The design does not define log retention, audit log tamper resistance, reviewer access to logs, or alert thresholds.

## 13. Privacy and Data Retention Review

**Confirmed controls**

The design recognizes that sensitive warning-letter data should not be logged beyond required audit metadata. 

**Medium-risk gap**

Privacy and retention rules are incomplete. The system permanently stores the uploaded reference PDF, OCR raw text, edited OCR text, generated output, and version snapshots. The requirements confirm permanent PDF storage and version history, but no retention period, deletion process, data minimization rule, or privacy classification is defined. 

## 14. Rate Limiting and Abuse Prevention Review

**Confirmed controls**

The design says OCR should be explicit, not automatic, and OCR results should be stored to avoid repeated Google Vision calls. 

**High-risk gap**

No rate limits or abuse controls are defined for:

* PDF upload.
* OCR execution.
* Preview generation.
* Final output generation.
* Save/version snapshot creation.
* Finalize / return-to-editing actions.

Even though the tool is Administrator-only, a compromised Administrator session could cause OCR cost abuse, storage abuse, or service degradation.

## 15. Frontend Security Review

**Confirmed controls**

Client-side state is temporary, and server-side state is the source of truth. UI JavaScript must not contain finalization business rules.  

**Gaps**

The design does not define frontend output encoding for preview HTML or sandboxing of generated preview/output. Since the builder renders user-entered static text, OCR-confirmed text, image references, SVG branding, and generated Print Format HTML, the preview surface must be treated as XSS-sensitive.

## 16. Backend Security Review

**Confirmed controls**

Backend services are separated by responsibility: access control, PDF validation, layout blocks, field mapping, OCR, branding, preview, finalization, output generation, version history, and validation. 

**Gaps**

The backend design must explicitly enforce:

* Built-in `Administrator` only.
* Hard restriction to `Dunning Letter`.
* Object ownership / setup scoping for OCR, files, blocks, validation issues, and version history.
* Finalized-state locking.
* Escaping of dynamic field output.
* Sanitization of static text, OCR text, SVG, generated HTML, generated CSS, and generated Jinja.

## 17. Deployment Security Review

**Confirmed controls**

The design chooses a native Frappe 14 modular monolith and avoids separate frontend/backend/database services, reducing authentication and deployment complexity. 

**Missing evidence**

Deployment configuration is not yet sufficiently defined. Missing items include:

* Required environment variables.
* Secret injection method.
* File storage privacy settings.
* HTTPS requirement.
* Frappe site configuration expectations.
* Google Vision network egress restrictions.
* Production logging configuration.
* Backup and restore handling for private PDFs and version history.
* Access control for private file storage.

## 18. Findings

### Finding 1 — Authorization model conflict

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Authorization, API permission checks
**Evidence:** Main design permits custom role or built-in Administrator, while the addendum requires built-in Frappe `Administrator` only.  
**Impact:** Unauthorized privileged users may access the builder if the older role model is implemented.
**Required fix:** Revise all authorization design, API validation, permission matrix, and DocType permissions to enforce built-in `Administrator` only.
**Testing required:** Verify that System Manager, custom-role users, Guest, and authenticated non-Administrator users cannot access pages, APIs, DocTypes, files, OCR, finalization, output, or version history.

### Finding 2 — Target DocType restriction not consistently updated

**Risk:** High
**Status:** Confirmed issue
**Affected area:** API security, data isolation, field mapping
**Evidence:** The original design uses Warning Letter / Outstanding Invoice Notice assumptions, but the addendum confirms exact target DocType `Dunning Letter`.  
**Impact:** If API parameters allow arbitrary DocTypes, an Administrator or compromised session could inspect metadata or generate mappings for unintended DocTypes.
**Required fix:** Hard-restrict target DocType to `Dunning Letter` server-side. Do not trust `target_doctype` from the client except as a value that must equal the approved DocType.
**Testing required:** Attempt API calls using other DocTypes and confirm rejection.

### Finding 3 — SVG sanitization is required but underspecified

**Risk:** High
**Status:** Confirmed issue
**Affected area:** File security, frontend security, generated output
**Evidence:** SVG is allowed only after sanitization, and the design recognizes SVG can carry script-like content.  
**Impact:** Unsafe SVG can create stored XSS in preview, generated output, or Frappe Print Format rendering.
**Required fix:** Define a strict SVG sanitizer policy: remove scripts, event handlers, foreignObject, external references, data/script URLs, embedded active content, and unsafe attributes.
**Testing required:** Upload/select SVGs containing scripts, event handlers, external image references, `javascript:` URLs, and embedded objects; verify rejection or safe sanitization.

### Finding 4 — Generated Print Format output XSS controls are not concrete enough

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Template/output security, frontend security, backend security
**Evidence:** The design says generated output must avoid arbitrary JavaScript, unsafe script tags, and escape dynamic field output where appropriate. 
**Impact:** Static text, OCR text, field values, file URLs, or generated Jinja/HTML could inject unsafe markup into previews or final Print Format output.
**Required fix:** Define allowlisted HTML tags, CSS properties, Jinja expressions, and escaping rules. Treat all OCR/static/admin-entered text as untrusted until encoded for output.
**Testing required:** Use payloads in static text, OCR text, field labels, file names, and dynamic field values to verify no script execution in preview or final output.

### Finding 5 — Rate limiting and abuse prevention are incomplete

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Abuse prevention, OCR, upload, preview, output generation
**Evidence:** OCR is explicit and stored to avoid repeated calls, but no concrete rate limits are defined. 
**Impact:** A compromised session or automation could repeatedly run OCR, upload large files, generate previews, create snapshots, or consume storage/API quota.
**Required fix:** Add server-side throttling and quotas for OCR, upload, preview, save, finalization, output generation, and return-to-editing.
**Testing required:** Repeatedly call each mutating endpoint and confirm throttling, logging, and safe error responses.

### Finding 6 — File upload controls lack size, scanning, and storage enforcement details

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** File upload security
**Evidence:** PDF validation includes extension, MIME type, readability, protection status, and page count, but not size, scanning, or storage limits. 
**Impact:** Large or malicious files could cause denial of service, storage exhaustion, or unsafe downstream processing.
**Required fix:** Define maximum file sizes, accepted MIME verification method, private storage enforcement, and malware scanning decision.
**Testing required:** Upload oversized, malformed, encrypted, polyglot, renamed, and malicious test files.

### Finding 7 — Privacy and retention rules are incomplete

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Privacy, data retention, audit data
**Evidence:** The system stores permanent PDFs and version history with generated output snapshots; logging avoids sensitive data but retention is not defined.  
**Impact:** Sensitive warning-letter data may be retained indefinitely without a business-approved retention policy.
**Required fix:** Define retention, deletion, archival, backup, and access policies for PDFs, OCR text, generated output, validation issues, logs, and version history.
**Testing required:** Verify deletion/retention behavior and confirm sensitive data is not present in logs.

### Finding 8 — Secrets and environment variables are not fully documented

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Secrets, deployment configuration
**Evidence:** Google Vision credentials must be stored securely and not in client-side code, but required configuration is not listed. 
**Impact:** Credentials may be mishandled, logged, committed, exposed to clients, or inconsistently configured across environments.
**Required fix:** Add a deployment configuration section listing all required secrets, storage locations, masking rules, and rotation expectations.
**Testing required:** Verify missing credentials fail safely, credentials are not exposed in logs or responses, and client bundles contain no secrets.

### Finding 9 — Finalized-state locking needs API-level enforcement detail

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Data integrity, authorization, workflow security
**Evidence:** The addendum requires finalized setup to be locked until explicitly returned to `Editing`, with previous final output invalidated and new preview/similarity/finalization required. 
**Impact:** If only the UI enforces locking, direct API calls could alter finalized layouts or outputs.
**Required fix:** Enforce status transitions server-side for every save/edit/finalize/output endpoint.
**Testing required:** Attempt direct API edits after finalization and verify rejection unless a valid return-to-editing action occurs.

### Finding 10 — Audit logs need retention and tamper-resistance rules

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Logging and monitoring
**Evidence:** The design lists audit-worthy events and logging exclusions. 
**Impact:** Security events may be lost, altered, or unavailable during incident review.
**Required fix:** Define audit retention, access control, alert thresholds, and tamper-resistance expectations.
**Testing required:** Verify unauthorized attempts, finalization failures, OCR failures, and output failures create appropriate audit records without sensitive data leakage.

## 19. Risk Rating

**Overall project security risk at design stage:** **High**

Reason: The system handles sensitive documents, file rendering, OCR integration, generated HTML/Jinja output, and privileged Administrator-only workflows. The main blocking risks are authorization-model inconsistency, insufficient SVG/output sanitization detail, missing DocType hard restriction, and missing abuse controls.

## 20. Required Fixes

Before Stage 4 Implementation Planning, update the design to:

1. Replace all custom-role authorization references with built-in Frappe `Administrator` only.
2. Hard-restrict target DocType to `Dunning Letter`.
3. Define object-level API authorization and setup scoping for every endpoint.
4. Add concrete SVG sanitization rules.
5. Add concrete HTML/CSS/Jinja output sanitization and escaping rules.
6. Define rate limits for OCR, upload, preview, save, finalization, output generation, and return-to-editing.
7. Define file size limits, storage privacy rules, and malware scanning decision.
8. Document Google Vision secrets and environment configuration.
9. Define privacy retention rules for PDFs, OCR, generated output, logs, and version history.
10. Enforce finalized-state locking server-side.
11. Define audit log retention, access control, and alert thresholds.

## 21. Recommended Improvements

Add a dedicated **Security Requirements Addendum** back into the Requirements Document. It should include:

* Built-in Administrator-only access.
* Backend authorization required for all APIs.
* `Dunning Letter` as the only allowed target DocType.
* Private file storage requirement.
* SVG sanitization requirement.
* Output escaping and script prohibition.
* Rate limiting and abuse prevention.
* No sensitive data in logs.
* Secrets must not be committed or exposed client-side.
* Defined retention for uploaded PDFs, OCR text, generated output, and audit logs.

## 22. Security Test Cases

Required design-stage security test cases:

1. Non-Administrator cannot load builder page.
2. Non-Administrator cannot call any `gpf_builder.api.*` endpoint.
3. System Manager cannot access the app unless they are the built-in `Administrator`.
4. Guest cannot access files, APIs, previews, output, or version history.
5. API rejects any `target_doctype` other than `Dunning Letter`.
6. API rejects edits to finalized setup.
7. Return-to-editing invalidates previous final output.
8. OCR cannot run without valid credentials.
9. OCR result cannot be used unless confirmed.
10. Repeated OCR calls are rate limited.
11. Oversized PDFs are rejected.
12. Multi-page PDFs are rejected.
13. Corrupted or protected PDFs are rejected.
14. Branding WEBP and PDF files are rejected.
15. Unsafe SVG payloads are rejected or sanitized.
16. Static text XSS payload does not execute in preview.
17. OCR text XSS payload does not execute in preview.
18. Dynamic field value XSS payload is escaped in generated output.
19. Generated output contains no arbitrary JavaScript.
20. Logs do not contain Google Vision credentials, private file paths, full generated output, or sensitive warning-letter content.
21. Unauthorized attempts are logged.
22. Version history is immutable through UI and API.
23. Version snapshot access is restricted to built-in Administrator.
24. Private PDF file cannot be accessed by unauthorized users.

## 23. Approval Decision

**Decision:** **Needs revision**

The design is not approved to proceed to implementation planning until the high-risk findings are resolved, especially:

* Authorization model conflict.
* `Dunning Letter` DocType enforcement.
* SVG sanitization.
* Generated output sanitization.
* Rate limiting and abuse prevention.

## 24. Security Gate Checklist

| Checklist Item                        | Status                                        |
| ------------------------------------- | --------------------------------------------- |
| Authentication reviewed               | Passed with minor missing evidence            |
| Authorization reviewed                | **Failed — design conflict must be resolved** |
| API access reviewed                   | **Needs revision**                            |
| Input validation reviewed             | **Needs revision**                            |
| Database access reviewed              | **Needs revision**                            |
| Secrets reviewed                      | **Needs revision**                            |
| Logging reviewed                      | Conditionally acceptable                      |
| Privacy reviewed                      | **Needs revision**                            |
| Rate limiting reviewed                | **Failed — not sufficiently defined**         |
| Deployment security reviewed          | **Needs revision**                            |
| Critical risks resolved or documented | No critical risks identified                  |
| High risks resolved or documented     | **No — high risks remain unresolved**         |

---

# Security Audit Report

## 1. Audit Context

**Current review stage:** Waterfall Stage 3 — **System Design Security Review**

This review assessed the approved requirements, system analysis, system design, and system design approval addendum for the Frappe 14 PDF Reference to Print Format Builder.

**Overall decision:** **Needs revision**

The design contains several good security controls, but it should not proceed to implementation planning until the high-risk design gaps below are resolved or explicitly accepted with compensating controls.

## 2. Documents Reviewed

Reviewed approved documents:

1. `01_requirements.md` — confirms Administrator-only access, single-page PDF upload, OCR confirmation, existing branding file selection, version history, and copy-ready Print Format output. 
2. `02_system_analysis.md` — confirms Administrator-only workflows, OCR review, field mapping, preview, finalization, and version history behavior. 
3. `02b_system_analysis.md` — confirms finalization blockers, allowed branding types, no WEBP/PDF branding assets, no blank spacer blocks, no overlapping blocks, and output snapshot requirements. 
4. `03_system_designer.md` — defines Frappe 14 architecture, DocTypes, APIs, validation, authentication, authorization, logging, security design, and deployment-related assumptions. 
5. `03b_system_designer.md` — overrides earlier design decisions by confirming built-in Frappe `Administrator` only, target DocType `Dunning Letter`, SVG sanitization, no configurable required-field registry, and locked finalized setup behavior. 

## 3. Security Scope

Reviewed areas requested:

Authentication, authorization, API permission checks, user data isolation, input validation, abuse prevention, rate limiting, file uploads, secrets and environment variables, logging, error messages, privacy and data retention, and deployment configuration.

## 4. Authentication Review

**Confirmed controls**

The design uses native Frappe session authentication and explicitly avoids a separate authentication system. API calls require a valid Frappe session, CSRF protection where applicable, and server-side identity from Frappe session context. 

**Security assessment**

This is acceptable for design stage, provided implementation uses Frappe’s standard authenticated whitelisted method protections and does not expose guest methods.

**Missing evidence**

No explicit requirement states that all `gpf_builder.api.*` methods must reject guest access at the method declaration level.

## 5. Authorization Review

**Confirmed controls**

The design states that every whitelisted API must perform server-side authorization and that client-side hiding of buttons is insufficient. 

**Confirmed design conflict**

The main design recommends a custom role, `Warning Letter Print Format Administrator`, while the approved addendum changes the final rule to **built-in Frappe `Administrator` only** for app access, APIs, uploads, editing, OCR, preview, finalization, output generation, and version history.  

**Security impact**

This conflict must be corrected before implementation. If developers implement the older custom-role model, non-built-in Administrator users may gain access contrary to the approved security decision.

## 6. Input Validation Review

**Confirmed controls**

The design defines client-side validation for feedback, server-side save validation for structural validity, and server-side finalization validation for business rules. It validates block types, numeric positions, positive width and height, page bounds, valid field mappings, valid file references, blank spacer rejection, and overlap checks. 

**Gaps**

The design does not yet specify strict allowlists for generated HTML, CSS properties, Jinja expressions, OCR-confirmed text, or static multilingual text. It states that generated output must avoid arbitrary JavaScript and unsafe script tags, but this needs to become a concrete sanitizer/escaping rule. 

## 7. API Security Review

**Confirmed controls**

The design uses Frappe whitelisted methods under `/api/method/gpf_builder.api.<method_name>` and states that all APIs must perform server-side authorization. 

**High-risk concern**

APIs accept object identifiers such as `setup_name`, `ocr_result_id`, `target_doctype`, and file references. The design must require object-level authorization and state validation on every request, not just role validation.

Examples requiring explicit checks:

* `setup_name` must refer to the single active MVP setup.
* `ocr_result_id` must belong to that setup.
* Branding `File` records must exist, be accessible, and be allowed.
* `target_doctype` must be hard-restricted to `Dunning Letter` after the addendum decision.
* Finalized records must reject edit/save operations unless explicitly returned to `Editing`.

## 8. Database Security Review

**Confirmed controls**

The design uses Frappe DocTypes and MariaDB via the Frappe ORM, avoiding a separate database. It defines DocTypes for setup, layout blocks, OCR results, version history, and validation issues. 

**Gaps**

The design does not define database-level permission rules for the custom DocTypes. Because this is an Administrator-only tool, every custom DocType should deny non-Administrator read/write access through Frappe permissions, not only through the UI or API layer.

**Additional concern**

Version history stores generated output snapshots. This may include warning-letter content, field mappings, and sensitive text. The design says version history should be immutable through the UI, but retention, deletion, and access policies are not fully defined. 

## 9. Session and Token Security Review

**Confirmed controls**

The design relies on Frappe session authentication and CSRF protection for mutating APIs. 

**Missing evidence**

No explicit session timeout, re-authentication, or elevated confirmation requirement is defined for sensitive actions such as finalization, returning finalized setup to `Editing`, or generating final copy-ready output.

Given the approved rule that finalized setup is locked until explicitly returned to `Editing`, the return-to-editing action should be treated as sensitive. 

## 10. Secrets and Configuration Review

**Confirmed controls**

The design states Google Vision credentials must be stored in secure Frappe configuration, not client-side code, and OCR requests must be server-side. 

**Gaps**

The design does not list required environment variables or configuration keys. It also does not define rotation, access control, masking, deployment injection, or validation behavior for Google Vision credentials.

Required configuration evidence should include:

* Google Vision credential location.
* Whether credentials are stored in `site_config.json`, environment variables, or a secrets manager.
* Which server process can read them.
* How missing credentials are detected.
* How credentials are excluded from logs, snapshots, generated output, and client responses.

## 11. File Upload Security Review

**Confirmed controls**

The PDF upload validates extension, MIME type, readability, protection status, and one-page count. Uploaded PDF references should be private files. Branding assets must be selected from existing Frappe `File` records, and WEBP/PDF branding assets are blocked.  

**High-risk gap**

SVG is allowed after sanitization, but the sanitizer rules are not fully specified. The addendum confirms SVG is allowed only after sanitization and SVG conversion is not required. 

Because SVG can contain script-like behavior, event handlers, external references, and embedded content, the design must define the sanitizer allowlist before implementation.

**Additional gaps**

The design does not specify:

* Maximum PDF file size.
* Maximum image/SVG size.
* Maximum OCR input size.
* Virus/malware scanning expectations.
* Whether uploaded PDFs are private by default at the Frappe `File` record level.
* Whether private file URLs are ever returned to the browser and how access is enforced.

## 12. Logging and Monitoring Review

**Confirmed controls**

The design defines what to log and what not to log. It excludes Google Vision credentials, full private file paths, full generated output unless intentionally stored in version history, and sensitive warning-letter data beyond required audit metadata. It also recommends alerts for repeated OCR failures, version snapshot failures, output failures, and increased unauthorized access attempts. 

**Gaps**

The design does not define log retention, audit log tamper resistance, reviewer access to logs, or alert thresholds.

## 13. Privacy and Data Retention Review

**Confirmed controls**

The design recognizes that sensitive warning-letter data should not be logged beyond required audit metadata. 

**Medium-risk gap**

Privacy and retention rules are incomplete. The system permanently stores the uploaded reference PDF, OCR raw text, edited OCR text, generated output, and version snapshots. The requirements confirm permanent PDF storage and version history, but no retention period, deletion process, data minimization rule, or privacy classification is defined. 

## 14. Rate Limiting and Abuse Prevention Review

**Confirmed controls**

The design says OCR should be explicit, not automatic, and OCR results should be stored to avoid repeated Google Vision calls. 

**High-risk gap**

No rate limits or abuse controls are defined for:

* PDF upload.
* OCR execution.
* Preview generation.
* Final output generation.
* Save/version snapshot creation.
* Finalize / return-to-editing actions.

Even though the tool is Administrator-only, a compromised Administrator session could cause OCR cost abuse, storage abuse, or service degradation.

## 15. Frontend Security Review

**Confirmed controls**

Client-side state is temporary, and server-side state is the source of truth. UI JavaScript must not contain finalization business rules.  

**Gaps**

The design does not define frontend output encoding for preview HTML or sandboxing of generated preview/output. Since the builder renders user-entered static text, OCR-confirmed text, image references, SVG branding, and generated Print Format HTML, the preview surface must be treated as XSS-sensitive.

## 16. Backend Security Review

**Confirmed controls**

Backend services are separated by responsibility: access control, PDF validation, layout blocks, field mapping, OCR, branding, preview, finalization, output generation, version history, and validation. 

**Gaps**

The backend design must explicitly enforce:

* Built-in `Administrator` only.
* Hard restriction to `Dunning Letter`.
* Object ownership / setup scoping for OCR, files, blocks, validation issues, and version history.
* Finalized-state locking.
* Escaping of dynamic field output.
* Sanitization of static text, OCR text, SVG, generated HTML, generated CSS, and generated Jinja.

## 17. Deployment Security Review

**Confirmed controls**

The design chooses a native Frappe 14 modular monolith and avoids separate frontend/backend/database services, reducing authentication and deployment complexity. 

**Missing evidence**

Deployment configuration is not yet sufficiently defined. Missing items include:

* Required environment variables.
* Secret injection method.
* File storage privacy settings.
* HTTPS requirement.
* Frappe site configuration expectations.
* Google Vision network egress restrictions.
* Production logging configuration.
* Backup and restore handling for private PDFs and version history.
* Access control for private file storage.

## 18. Findings

### Finding 1 — Authorization model conflict

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Authorization, API permission checks
**Evidence:** Main design permits custom role or built-in Administrator, while the addendum requires built-in Frappe `Administrator` only.  
**Impact:** Unauthorized privileged users may access the builder if the older role model is implemented.
**Required fix:** Revise all authorization design, API validation, permission matrix, and DocType permissions to enforce built-in `Administrator` only.
**Testing required:** Verify that System Manager, custom-role users, Guest, and authenticated non-Administrator users cannot access pages, APIs, DocTypes, files, OCR, finalization, output, or version history.

### Finding 2 — Target DocType restriction not consistently updated

**Risk:** High
**Status:** Confirmed issue
**Affected area:** API security, data isolation, field mapping
**Evidence:** The original design uses Warning Letter / Outstanding Invoice Notice assumptions, but the addendum confirms exact target DocType `Dunning Letter`.  
**Impact:** If API parameters allow arbitrary DocTypes, an Administrator or compromised session could inspect metadata or generate mappings for unintended DocTypes.
**Required fix:** Hard-restrict target DocType to `Dunning Letter` server-side. Do not trust `target_doctype` from the client except as a value that must equal the approved DocType.
**Testing required:** Attempt API calls using other DocTypes and confirm rejection.

### Finding 3 — SVG sanitization is required but underspecified

**Risk:** High
**Status:** Confirmed issue
**Affected area:** File security, frontend security, generated output
**Evidence:** SVG is allowed only after sanitization, and the design recognizes SVG can carry script-like content.  
**Impact:** Unsafe SVG can create stored XSS in preview, generated output, or Frappe Print Format rendering.
**Required fix:** Define a strict SVG sanitizer policy: remove scripts, event handlers, foreignObject, external references, data/script URLs, embedded active content, and unsafe attributes.
**Testing required:** Upload/select SVGs containing scripts, event handlers, external image references, `javascript:` URLs, and embedded objects; verify rejection or safe sanitization.

### Finding 4 — Generated Print Format output XSS controls are not concrete enough

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Template/output security, frontend security, backend security
**Evidence:** The design says generated output must avoid arbitrary JavaScript, unsafe script tags, and escape dynamic field output where appropriate. 
**Impact:** Static text, OCR text, field values, file URLs, or generated Jinja/HTML could inject unsafe markup into previews or final Print Format output.
**Required fix:** Define allowlisted HTML tags, CSS properties, Jinja expressions, and escaping rules. Treat all OCR/static/admin-entered text as untrusted until encoded for output.
**Testing required:** Use payloads in static text, OCR text, field labels, file names, and dynamic field values to verify no script execution in preview or final output.

### Finding 5 — Rate limiting and abuse prevention are incomplete

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Abuse prevention, OCR, upload, preview, output generation
**Evidence:** OCR is explicit and stored to avoid repeated calls, but no concrete rate limits are defined. 
**Impact:** A compromised session or automation could repeatedly run OCR, upload large files, generate previews, create snapshots, or consume storage/API quota.
**Required fix:** Add server-side throttling and quotas for OCR, upload, preview, save, finalization, output generation, and return-to-editing.
**Testing required:** Repeatedly call each mutating endpoint and confirm throttling, logging, and safe error responses.

### Finding 6 — File upload controls lack size, scanning, and storage enforcement details

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** File upload security
**Evidence:** PDF validation includes extension, MIME type, readability, protection status, and page count, but not size, scanning, or storage limits. 
**Impact:** Large or malicious files could cause denial of service, storage exhaustion, or unsafe downstream processing.
**Required fix:** Define maximum file sizes, accepted MIME verification method, private storage enforcement, and malware scanning decision.
**Testing required:** Upload oversized, malformed, encrypted, polyglot, renamed, and malicious test files.

### Finding 7 — Privacy and retention rules are incomplete

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Privacy, data retention, audit data
**Evidence:** The system stores permanent PDFs and version history with generated output snapshots; logging avoids sensitive data but retention is not defined.  
**Impact:** Sensitive warning-letter data may be retained indefinitely without a business-approved retention policy.
**Required fix:** Define retention, deletion, archival, backup, and access policies for PDFs, OCR text, generated output, validation issues, logs, and version history.
**Testing required:** Verify deletion/retention behavior and confirm sensitive data is not present in logs.

### Finding 8 — Secrets and environment variables are not fully documented

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Secrets, deployment configuration
**Evidence:** Google Vision credentials must be stored securely and not in client-side code, but required configuration is not listed. 
**Impact:** Credentials may be mishandled, logged, committed, exposed to clients, or inconsistently configured across environments.
**Required fix:** Add a deployment configuration section listing all required secrets, storage locations, masking rules, and rotation expectations.
**Testing required:** Verify missing credentials fail safely, credentials are not exposed in logs or responses, and client bundles contain no secrets.

### Finding 9 — Finalized-state locking needs API-level enforcement detail

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Data integrity, authorization, workflow security
**Evidence:** The addendum requires finalized setup to be locked until explicitly returned to `Editing`, with previous final output invalidated and new preview/similarity/finalization required. 
**Impact:** If only the UI enforces locking, direct API calls could alter finalized layouts or outputs.
**Required fix:** Enforce status transitions server-side for every save/edit/finalize/output endpoint.
**Testing required:** Attempt direct API edits after finalization and verify rejection unless a valid return-to-editing action occurs.

### Finding 10 — Audit logs need retention and tamper-resistance rules

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Logging and monitoring
**Evidence:** The design lists audit-worthy events and logging exclusions. 
**Impact:** Security events may be lost, altered, or unavailable during incident review.
**Required fix:** Define audit retention, access control, alert thresholds, and tamper-resistance expectations.
**Testing required:** Verify unauthorized attempts, finalization failures, OCR failures, and output failures create appropriate audit records without sensitive data leakage.

## 19. Risk Rating

**Overall project security risk at design stage:** **High**

Reason: The system handles sensitive documents, file rendering, OCR integration, generated HTML/Jinja output, and privileged Administrator-only workflows. The main blocking risks are authorization-model inconsistency, insufficient SVG/output sanitization detail, missing DocType hard restriction, and missing abuse controls.

## 20. Required Fixes

Before Stage 4 Implementation Planning, update the design to:

1. Replace all custom-role authorization references with built-in Frappe `Administrator` only.
2. Hard-restrict target DocType to `Dunning Letter`.
3. Define object-level API authorization and setup scoping for every endpoint.
4. Add concrete SVG sanitization rules.
5. Add concrete HTML/CSS/Jinja output sanitization and escaping rules.
6. Define rate limits for OCR, upload, preview, save, finalization, output generation, and return-to-editing.
7. Define file size limits, storage privacy rules, and malware scanning decision.
8. Document Google Vision secrets and environment configuration.
9. Define privacy retention rules for PDFs, OCR, generated output, logs, and version history.
10. Enforce finalized-state locking server-side.
11. Define audit log retention, access control, and alert thresholds.

## 21. Recommended Improvements

Add a dedicated **Security Requirements Addendum** back into the Requirements Document. It should include:

* Built-in Administrator-only access.
* Backend authorization required for all APIs.
* `Dunning Letter` as the only allowed target DocType.
* Private file storage requirement.
* SVG sanitization requirement.
* Output escaping and script prohibition.
* Rate limiting and abuse prevention.
* No sensitive data in logs.
* Secrets must not be committed or exposed client-side.
* Defined retention for uploaded PDFs, OCR text, generated output, and audit logs.

## 22. Security Test Cases

Required design-stage security test cases:

1. Non-Administrator cannot load builder page.
2. Non-Administrator cannot call any `gpf_builder.api.*` endpoint.
3. System Manager cannot access the app unless they are the built-in `Administrator`.
4. Guest cannot access files, APIs, previews, output, or version history.
5. API rejects any `target_doctype` other than `Dunning Letter`.
6. API rejects edits to finalized setup.
7. Return-to-editing invalidates previous final output.
8. OCR cannot run without valid credentials.
9. OCR result cannot be used unless confirmed.
10. Repeated OCR calls are rate limited.
11. Oversized PDFs are rejected.
12. Multi-page PDFs are rejected.
13. Corrupted or protected PDFs are rejected.
14. Branding WEBP and PDF files are rejected.
15. Unsafe SVG payloads are rejected or sanitized.
16. Static text XSS payload does not execute in preview.
17. OCR text XSS payload does not execute in preview.
18. Dynamic field value XSS payload is escaped in generated output.
19. Generated output contains no arbitrary JavaScript.
20. Logs do not contain Google Vision credentials, private file paths, full generated output, or sensitive warning-letter content.
21. Unauthorized attempts are logged.
22. Version history is immutable through UI and API.
23. Version snapshot access is restricted to built-in Administrator.
24. Private PDF file cannot be accessed by unauthorized users.

## 23. Approval Decision

**Decision:** **Needs revision**

The design is not approved to proceed to implementation planning until the high-risk findings are resolved, especially:

* Authorization model conflict.
* `Dunning Letter` DocType enforcement.
* SVG sanitization.
* Generated output sanitization.
* Rate limiting and abuse prevention.

## 24. Security Gate Checklist

| Checklist Item                        | Status                                        |
| ------------------------------------- | --------------------------------------------- |
| Authentication reviewed               | Passed with minor missing evidence            |
| Authorization reviewed                | **Failed — design conflict must be resolved** |
| API access reviewed                   | **Needs revision**                            |
| Input validation reviewed             | **Needs revision**                            |
| Database access reviewed              | **Needs revision**                            |
| Secrets reviewed                      | **Needs revision**                            |
| Logging reviewed                      | Conditionally acceptable                      |
| Privacy reviewed                      | **Needs revision**                            |
| Rate limiting reviewed                | **Failed — not sufficiently defined**         |
| Deployment security reviewed          | **Needs revision**                            |
| Critical risks resolved or documented | No critical risks identified                  |
| High risks resolved or documented     | **No — high risks remain unresolved**         |

---

# Security Audit Report

## 1. Audit Context

**Current review stage:** Waterfall Stage 3 — **System Design Security Review**

This review assessed the approved requirements, system analysis, system design, and system design approval addendum for the Frappe 14 PDF Reference to Print Format Builder.

**Overall decision:** **Needs revision**

The design contains several good security controls, but it should not proceed to implementation planning until the high-risk design gaps below are resolved or explicitly accepted with compensating controls.

## 2. Documents Reviewed

Reviewed approved documents:

1. `01_requirements.md` — confirms Administrator-only access, single-page PDF upload, OCR confirmation, existing branding file selection, version history, and copy-ready Print Format output. 
2. `02_system_analysis.md` — confirms Administrator-only workflows, OCR review, field mapping, preview, finalization, and version history behavior. 
3. `02b_system_analysis.md` — confirms finalization blockers, allowed branding types, no WEBP/PDF branding assets, no blank spacer blocks, no overlapping blocks, and output snapshot requirements. 
4. `03_system_designer.md` — defines Frappe 14 architecture, DocTypes, APIs, validation, authentication, authorization, logging, security design, and deployment-related assumptions. 
5. `03b_system_designer.md` — overrides earlier design decisions by confirming built-in Frappe `Administrator` only, target DocType `Dunning Letter`, SVG sanitization, no configurable required-field registry, and locked finalized setup behavior. 

## 3. Security Scope

Reviewed areas requested:

Authentication, authorization, API permission checks, user data isolation, input validation, abuse prevention, rate limiting, file uploads, secrets and environment variables, logging, error messages, privacy and data retention, and deployment configuration.

## 4. Authentication Review

**Confirmed controls**

The design uses native Frappe session authentication and explicitly avoids a separate authentication system. API calls require a valid Frappe session, CSRF protection where applicable, and server-side identity from Frappe session context. 

**Security assessment**

This is acceptable for design stage, provided implementation uses Frappe’s standard authenticated whitelisted method protections and does not expose guest methods.

**Missing evidence**

No explicit requirement states that all `gpf_builder.api.*` methods must reject guest access at the method declaration level.

## 5. Authorization Review

**Confirmed controls**

The design states that every whitelisted API must perform server-side authorization and that client-side hiding of buttons is insufficient. 

**Confirmed design conflict**

The main design recommends a custom role, `Warning Letter Print Format Administrator`, while the approved addendum changes the final rule to **built-in Frappe `Administrator` only** for app access, APIs, uploads, editing, OCR, preview, finalization, output generation, and version history.  

**Security impact**

This conflict must be corrected before implementation. If developers implement the older custom-role model, non-built-in Administrator users may gain access contrary to the approved security decision.

## 6. Input Validation Review

**Confirmed controls**

The design defines client-side validation for feedback, server-side save validation for structural validity, and server-side finalization validation for business rules. It validates block types, numeric positions, positive width and height, page bounds, valid field mappings, valid file references, blank spacer rejection, and overlap checks. 

**Gaps**

The design does not yet specify strict allowlists for generated HTML, CSS properties, Jinja expressions, OCR-confirmed text, or static multilingual text. It states that generated output must avoid arbitrary JavaScript and unsafe script tags, but this needs to become a concrete sanitizer/escaping rule. 

## 7. API Security Review

**Confirmed controls**

The design uses Frappe whitelisted methods under `/api/method/gpf_builder.api.<method_name>` and states that all APIs must perform server-side authorization. 

**High-risk concern**

APIs accept object identifiers such as `setup_name`, `ocr_result_id`, `target_doctype`, and file references. The design must require object-level authorization and state validation on every request, not just role validation.

Examples requiring explicit checks:

* `setup_name` must refer to the single active MVP setup.
* `ocr_result_id` must belong to that setup.
* Branding `File` records must exist, be accessible, and be allowed.
* `target_doctype` must be hard-restricted to `Dunning Letter` after the addendum decision.
* Finalized records must reject edit/save operations unless explicitly returned to `Editing`.

## 8. Database Security Review

**Confirmed controls**

The design uses Frappe DocTypes and MariaDB via the Frappe ORM, avoiding a separate database. It defines DocTypes for setup, layout blocks, OCR results, version history, and validation issues. 

**Gaps**

The design does not define database-level permission rules for the custom DocTypes. Because this is an Administrator-only tool, every custom DocType should deny non-Administrator read/write access through Frappe permissions, not only through the UI or API layer.

**Additional concern**

Version history stores generated output snapshots. This may include warning-letter content, field mappings, and sensitive text. The design says version history should be immutable through the UI, but retention, deletion, and access policies are not fully defined. 

## 9. Session and Token Security Review

**Confirmed controls**

The design relies on Frappe session authentication and CSRF protection for mutating APIs. 

**Missing evidence**

No explicit session timeout, re-authentication, or elevated confirmation requirement is defined for sensitive actions such as finalization, returning finalized setup to `Editing`, or generating final copy-ready output.

Given the approved rule that finalized setup is locked until explicitly returned to `Editing`, the return-to-editing action should be treated as sensitive. 

## 10. Secrets and Configuration Review

**Confirmed controls**

The design states Google Vision credentials must be stored in secure Frappe configuration, not client-side code, and OCR requests must be server-side. 

**Gaps**

The design does not list required environment variables or configuration keys. It also does not define rotation, access control, masking, deployment injection, or validation behavior for Google Vision credentials.

Required configuration evidence should include:

* Google Vision credential location.
* Whether credentials are stored in `site_config.json`, environment variables, or a secrets manager.
* Which server process can read them.
* How missing credentials are detected.
* How credentials are excluded from logs, snapshots, generated output, and client responses.

## 11. File Upload Security Review

**Confirmed controls**

The PDF upload validates extension, MIME type, readability, protection status, and one-page count. Uploaded PDF references should be private files. Branding assets must be selected from existing Frappe `File` records, and WEBP/PDF branding assets are blocked.  

**High-risk gap**

SVG is allowed after sanitization, but the sanitizer rules are not fully specified. The addendum confirms SVG is allowed only after sanitization and SVG conversion is not required. 

Because SVG can contain script-like behavior, event handlers, external references, and embedded content, the design must define the sanitizer allowlist before implementation.

**Additional gaps**

The design does not specify:

* Maximum PDF file size.
* Maximum image/SVG size.
* Maximum OCR input size.
* Virus/malware scanning expectations.
* Whether uploaded PDFs are private by default at the Frappe `File` record level.
* Whether private file URLs are ever returned to the browser and how access is enforced.

## 12. Logging and Monitoring Review

**Confirmed controls**

The design defines what to log and what not to log. It excludes Google Vision credentials, full private file paths, full generated output unless intentionally stored in version history, and sensitive warning-letter data beyond required audit metadata. It also recommends alerts for repeated OCR failures, version snapshot failures, output failures, and increased unauthorized access attempts. 

**Gaps**

The design does not define log retention, audit log tamper resistance, reviewer access to logs, or alert thresholds.

## 13. Privacy and Data Retention Review

**Confirmed controls**

The design recognizes that sensitive warning-letter data should not be logged beyond required audit metadata. 

**Medium-risk gap**

Privacy and retention rules are incomplete. The system permanently stores the uploaded reference PDF, OCR raw text, edited OCR text, generated output, and version snapshots. The requirements confirm permanent PDF storage and version history, but no retention period, deletion process, data minimization rule, or privacy classification is defined. 

## 14. Rate Limiting and Abuse Prevention Review

**Confirmed controls**

The design says OCR should be explicit, not automatic, and OCR results should be stored to avoid repeated Google Vision calls. 

**High-risk gap**

No rate limits or abuse controls are defined for:

* PDF upload.
* OCR execution.
* Preview generation.
* Final output generation.
* Save/version snapshot creation.
* Finalize / return-to-editing actions.

Even though the tool is Administrator-only, a compromised Administrator session could cause OCR cost abuse, storage abuse, or service degradation.

## 15. Frontend Security Review

**Confirmed controls**

Client-side state is temporary, and server-side state is the source of truth. UI JavaScript must not contain finalization business rules.  

**Gaps**

The design does not define frontend output encoding for preview HTML or sandboxing of generated preview/output. Since the builder renders user-entered static text, OCR-confirmed text, image references, SVG branding, and generated Print Format HTML, the preview surface must be treated as XSS-sensitive.

## 16. Backend Security Review

**Confirmed controls**

Backend services are separated by responsibility: access control, PDF validation, layout blocks, field mapping, OCR, branding, preview, finalization, output generation, version history, and validation. 

**Gaps**

The backend design must explicitly enforce:

* Built-in `Administrator` only.
* Hard restriction to `Dunning Letter`.
* Object ownership / setup scoping for OCR, files, blocks, validation issues, and version history.
* Finalized-state locking.
* Escaping of dynamic field output.
* Sanitization of static text, OCR text, SVG, generated HTML, generated CSS, and generated Jinja.

## 17. Deployment Security Review

**Confirmed controls**

The design chooses a native Frappe 14 modular monolith and avoids separate frontend/backend/database services, reducing authentication and deployment complexity. 

**Missing evidence**

Deployment configuration is not yet sufficiently defined. Missing items include:

* Required environment variables.
* Secret injection method.
* File storage privacy settings.
* HTTPS requirement.
* Frappe site configuration expectations.
* Google Vision network egress restrictions.
* Production logging configuration.
* Backup and restore handling for private PDFs and version history.
* Access control for private file storage.

## 18. Findings

### Finding 1 — Authorization model conflict

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Authorization, API permission checks
**Evidence:** Main design permits custom role or built-in Administrator, while the addendum requires built-in Frappe `Administrator` only.  
**Impact:** Unauthorized privileged users may access the builder if the older role model is implemented.
**Required fix:** Revise all authorization design, API validation, permission matrix, and DocType permissions to enforce built-in `Administrator` only.
**Testing required:** Verify that System Manager, custom-role users, Guest, and authenticated non-Administrator users cannot access pages, APIs, DocTypes, files, OCR, finalization, output, or version history.

### Finding 2 — Target DocType restriction not consistently updated

**Risk:** High
**Status:** Confirmed issue
**Affected area:** API security, data isolation, field mapping
**Evidence:** The original design uses Warning Letter / Outstanding Invoice Notice assumptions, but the addendum confirms exact target DocType `Dunning Letter`.  
**Impact:** If API parameters allow arbitrary DocTypes, an Administrator or compromised session could inspect metadata or generate mappings for unintended DocTypes.
**Required fix:** Hard-restrict target DocType to `Dunning Letter` server-side. Do not trust `target_doctype` from the client except as a value that must equal the approved DocType.
**Testing required:** Attempt API calls using other DocTypes and confirm rejection.

### Finding 3 — SVG sanitization is required but underspecified

**Risk:** High
**Status:** Confirmed issue
**Affected area:** File security, frontend security, generated output
**Evidence:** SVG is allowed only after sanitization, and the design recognizes SVG can carry script-like content.  
**Impact:** Unsafe SVG can create stored XSS in preview, generated output, or Frappe Print Format rendering.
**Required fix:** Define a strict SVG sanitizer policy: remove scripts, event handlers, foreignObject, external references, data/script URLs, embedded active content, and unsafe attributes.
**Testing required:** Upload/select SVGs containing scripts, event handlers, external image references, `javascript:` URLs, and embedded objects; verify rejection or safe sanitization.

### Finding 4 — Generated Print Format output XSS controls are not concrete enough

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Template/output security, frontend security, backend security
**Evidence:** The design says generated output must avoid arbitrary JavaScript, unsafe script tags, and escape dynamic field output where appropriate. 
**Impact:** Static text, OCR text, field values, file URLs, or generated Jinja/HTML could inject unsafe markup into previews or final Print Format output.
**Required fix:** Define allowlisted HTML tags, CSS properties, Jinja expressions, and escaping rules. Treat all OCR/static/admin-entered text as untrusted until encoded for output.
**Testing required:** Use payloads in static text, OCR text, field labels, file names, and dynamic field values to verify no script execution in preview or final output.

### Finding 5 — Rate limiting and abuse prevention are incomplete

**Risk:** High
**Status:** Confirmed issue
**Affected area:** Abuse prevention, OCR, upload, preview, output generation
**Evidence:** OCR is explicit and stored to avoid repeated calls, but no concrete rate limits are defined. 
**Impact:** A compromised session or automation could repeatedly run OCR, upload large files, generate previews, create snapshots, or consume storage/API quota.
**Required fix:** Add server-side throttling and quotas for OCR, upload, preview, save, finalization, output generation, and return-to-editing.
**Testing required:** Repeatedly call each mutating endpoint and confirm throttling, logging, and safe error responses.

### Finding 6 — File upload controls lack size, scanning, and storage enforcement details

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** File upload security
**Evidence:** PDF validation includes extension, MIME type, readability, protection status, and page count, but not size, scanning, or storage limits. 
**Impact:** Large or malicious files could cause denial of service, storage exhaustion, or unsafe downstream processing.
**Required fix:** Define maximum file sizes, accepted MIME verification method, private storage enforcement, and malware scanning decision.
**Testing required:** Upload oversized, malformed, encrypted, polyglot, renamed, and malicious test files.

### Finding 7 — Privacy and retention rules are incomplete

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Privacy, data retention, audit data
**Evidence:** The system stores permanent PDFs and version history with generated output snapshots; logging avoids sensitive data but retention is not defined.  
**Impact:** Sensitive warning-letter data may be retained indefinitely without a business-approved retention policy.
**Required fix:** Define retention, deletion, archival, backup, and access policies for PDFs, OCR text, generated output, validation issues, logs, and version history.
**Testing required:** Verify deletion/retention behavior and confirm sensitive data is not present in logs.

### Finding 8 — Secrets and environment variables are not fully documented

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Secrets, deployment configuration
**Evidence:** Google Vision credentials must be stored securely and not in client-side code, but required configuration is not listed. 
**Impact:** Credentials may be mishandled, logged, committed, exposed to clients, or inconsistently configured across environments.
**Required fix:** Add a deployment configuration section listing all required secrets, storage locations, masking rules, and rotation expectations.
**Testing required:** Verify missing credentials fail safely, credentials are not exposed in logs or responses, and client bundles contain no secrets.

### Finding 9 — Finalized-state locking needs API-level enforcement detail

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Data integrity, authorization, workflow security
**Evidence:** The addendum requires finalized setup to be locked until explicitly returned to `Editing`, with previous final output invalidated and new preview/similarity/finalization required. 
**Impact:** If only the UI enforces locking, direct API calls could alter finalized layouts or outputs.
**Required fix:** Enforce status transitions server-side for every save/edit/finalize/output endpoint.
**Testing required:** Attempt direct API edits after finalization and verify rejection unless a valid return-to-editing action occurs.

### Finding 10 — Audit logs need retention and tamper-resistance rules

**Risk:** Medium
**Status:** Confirmed issue
**Affected area:** Logging and monitoring
**Evidence:** The design lists audit-worthy events and logging exclusions. 
**Impact:** Security events may be lost, altered, or unavailable during incident review.
**Required fix:** Define audit retention, access control, alert thresholds, and tamper-resistance expectations.
**Testing required:** Verify unauthorized attempts, finalization failures, OCR failures, and output failures create appropriate audit records without sensitive data leakage.

## 19. Risk Rating

**Overall project security risk at design stage:** **High**

Reason: The system handles sensitive documents, file rendering, OCR integration, generated HTML/Jinja output, and privileged Administrator-only workflows. The main blocking risks are authorization-model inconsistency, insufficient SVG/output sanitization detail, missing DocType hard restriction, and missing abuse controls.

## 20. Required Fixes

Before Stage 4 Implementation Planning, update the design to:

1. Replace all custom-role authorization references with built-in Frappe `Administrator` only.
2. Hard-restrict target DocType to `Dunning Letter`.
3. Define object-level API authorization and setup scoping for every endpoint.
4. Add concrete SVG sanitization rules.
5. Add concrete HTML/CSS/Jinja output sanitization and escaping rules.
6. Define rate limits for OCR, upload, preview, save, finalization, output generation, and return-to-editing.
7. Define file size limits, storage privacy rules, and malware scanning decision.
8. Document Google Vision secrets and environment configuration.
9. Define privacy retention rules for PDFs, OCR, generated output, logs, and version history.
10. Enforce finalized-state locking server-side.
11. Define audit log retention, access control, and alert thresholds.

## 21. Recommended Improvements

Add a dedicated **Security Requirements Addendum** back into the Requirements Document. It should include:

* Built-in Administrator-only access.
* Backend authorization required for all APIs.
* `Dunning Letter` as the only allowed target DocType.
* Private file storage requirement.
* SVG sanitization requirement.
* Output escaping and script prohibition.
* Rate limiting and abuse prevention.
* No sensitive data in logs.
* Secrets must not be committed or exposed client-side.
* Defined retention for uploaded PDFs, OCR text, generated output, and audit logs.

## 22. Security Test Cases

Required design-stage security test cases:

1. Non-Administrator cannot load builder page.
2. Non-Administrator cannot call any `gpf_builder.api.*` endpoint.
3. System Manager cannot access the app unless they are the built-in `Administrator`.
4. Guest cannot access files, APIs, previews, output, or version history.
5. API rejects any `target_doctype` other than `Dunning Letter`.
6. API rejects edits to finalized setup.
7. Return-to-editing invalidates previous final output.
8. OCR cannot run without valid credentials.
9. OCR result cannot be used unless confirmed.
10. Repeated OCR calls are rate limited.
11. Oversized PDFs are rejected.
12. Multi-page PDFs are rejected.
13. Corrupted or protected PDFs are rejected.
14. Branding WEBP and PDF files are rejected.
15. Unsafe SVG payloads are rejected or sanitized.
16. Static text XSS payload does not execute in preview.
17. OCR text XSS payload does not execute in preview.
18. Dynamic field value XSS payload is escaped in generated output.
19. Generated output contains no arbitrary JavaScript.
20. Logs do not contain Google Vision credentials, private file paths, full generated output, or sensitive warning-letter content.
21. Unauthorized attempts are logged.
22. Version history is immutable through UI and API.
23. Version snapshot access is restricted to built-in Administrator.
24. Private PDF file cannot be accessed by unauthorized users.

## 23. Approval Decision

**Decision:** **Needs revision**

The design is not approved to proceed to implementation planning until the high-risk findings are resolved, especially:

* Authorization model conflict.
* `Dunning Letter` DocType enforcement.
* SVG sanitization.
* Generated output sanitization.
* Rate limiting and abuse prevention.

## 24. Security Gate Checklist

| Checklist Item                        | Status                                        |
| ------------------------------------- | --------------------------------------------- |
| Authentication reviewed               | Passed with minor missing evidence            |
| Authorization reviewed                | **Failed — design conflict must be resolved** |
| API access reviewed                   | **Needs revision**                            |
| Input validation reviewed             | **Needs revision**                            |
| Database access reviewed              | **Needs revision**                            |
| Secrets reviewed                      | **Needs revision**                            |
| Logging reviewed                      | Conditionally acceptable                      |
| Privacy reviewed                      | **Needs revision**                            |
| Rate limiting reviewed                | **Failed — not sufficiently defined**         |
| Deployment security reviewed          | **Needs revision**                            |
| Critical risks resolved or documented | No critical risks identified                  |
| High risks resolved or documented     | **No — high risks remain unresolved**         |

---

# System Design Approval Addendum — Stakeholder Decisions Recorded

## Confirmed Decisions

| Item                                 | Final Decision                                                               |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| Administrator role model             | Use **built-in Frappe Administrator** only                                   |
| Exact target DocType                 | `Dunning Letter`                                                             |
| Mandatory warning-letter fields      | **Skipped / not defined**                                                    |
| Configurable required-field registry | **Not approved**                                                             |
| Duplicate required fields            | Allowed                                                                      |
| SVG handling                         | SVG allowed **after sanitization**                                           |
| SVG conversion                       | Not required                                                                 |
| Editing after finalization           | Finalized setup must be locked until explicitly returned to `Editing` status |

---

## Design Impact Notes

### 1. Administrator Role

The authorization design must be revised from:

`Warning Letter Print Format Administrator`

to:

`built-in Frappe Administrator only`

Final rule:

Only the built-in Frappe `Administrator` user may access the app, call APIs, upload PDFs, edit layouts, run OCR, preview, finalize, generate output, and view version history.

---

### 2. Target DocType

The system design must use:

`Dunning Letter`

instead of the earlier placeholder:

`Warning Letter / Outstanding Invoice Notice`

Final rule:

All dynamic field selection and field mapping must come from the `Dunning Letter` DocType.

---

### 3. Mandatory Warning-Letter Fields

You selected:

* Exact mandatory fields: **skip this**
* Configurable required-field registry: **No**

This is a design-impacting exception because the approved analysis previously said all warning-letter-required fields are mandatory for finalization.

Final revised design rule:

The system will **not enforce a mandatory required-field list** during finalization unless a later approved requirement defines one.

Finalization will still validate that:

* Any dynamic field block that exists is mapped to a valid `Dunning Letter` field.
* Removed or invalid fields block finalization.
* Empty or incomplete dynamic blocks block finalization.
* But there is no global checklist of required `Dunning Letter` fields.

---

### 4. Duplicate Required Fields

Final rule:

The same `Dunning Letter` field may appear more than once in the generated Print Format.

This supports repeated values such as customer name, document number, date, company name, or address fields.

---

### 5. SVG Handling

Final rule:

SVG branding assets are allowed only after sanitization.

The system must reject unsafe SVG content such as:

* Embedded scripts
* Event handlers
* Unsafe external references
* Script-like markup

SVG files do not need to be converted to another format.

---

### 6. Editing After Finalization

Final rule:

A finalized setup is locked.

To make changes, the Administrator must explicitly return the setup to `Editing` status.

Returning to `Editing` must:

1. Clear finalized status.
2. Invalidate the previous final output.
3. Require a new preview.
4. Require a new 90% visual similarity confirmation.
5. Require finalization validation again.
6. Create a new version history entry on the next save.

---

## Remaining Open Questions

None for System Design.

---

# System Design Approval Addendum — Stakeholder Decisions Recorded

## Confirmed Decisions

| Item                                 | Final Decision                                                               |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| Administrator role model             | Use **built-in Frappe Administrator** only                                   |
| Exact target DocType                 | `Dunning Letter`                                                             |
| Mandatory warning-letter fields      | **Skipped / not defined**                                                    |
| Configurable required-field registry | **Not approved**                                                             |
| Duplicate required fields            | Allowed                                                                      |
| SVG handling                         | SVG allowed **after sanitization**                                           |
| SVG conversion                       | Not required                                                                 |
| Editing after finalization           | Finalized setup must be locked until explicitly returned to `Editing` status |

---

## Design Impact Notes

### 1. Administrator Role

The authorization design must be revised from:

`Warning Letter Print Format Administrator`

to:

`built-in Frappe Administrator only`

Final rule:

Only the built-in Frappe `Administrator` user may access the app, call APIs, upload PDFs, edit layouts, run OCR, preview, finalize, generate output, and view version history.

---

### 2. Target DocType

The system design must use:

`Dunning Letter`

instead of the earlier placeholder:

`Warning Letter / Outstanding Invoice Notice`

Final rule:

All dynamic field selection and field mapping must come from the `Dunning Letter` DocType.

---

### 3. Mandatory Warning-Letter Fields

You selected:

* Exact mandatory fields: **skip this**
* Configurable required-field registry: **No**

This is a design-impacting exception because the approved analysis previously said all warning-letter-required fields are mandatory for finalization.

Final revised design rule:

The system will **not enforce a mandatory required-field list** during finalization unless a later approved requirement defines one.

Finalization will still validate that:

* Any dynamic field block that exists is mapped to a valid `Dunning Letter` field.
* Removed or invalid fields block finalization.
* Empty or incomplete dynamic blocks block finalization.
* But there is no global checklist of required `Dunning Letter` fields.

---

### 4. Duplicate Required Fields

Final rule:

The same `Dunning Letter` field may appear more than once in the generated Print Format.

This supports repeated values such as customer name, document number, date, company name, or address fields.

---

### 5. SVG Handling

Final rule:

SVG branding assets are allowed only after sanitization.

The system must reject unsafe SVG content such as:

* Embedded scripts
* Event handlers
* Unsafe external references
* Script-like markup

SVG files do not need to be converted to another format.

---

### 6. Editing After Finalization

Final rule:

A finalized setup is locked.

To make changes, the Administrator must explicitly return the setup to `Editing` status.

Returning to `Editing` must:

1. Clear finalized status.
2. Invalidate the previous final output.
3. Require a new preview.
4. Require a new 90% visual similarity confirmation.
5. Require finalization validation again.
6. Create a new version history entry on the next save.

---

## Remaining Open Questions

None for System Design.

---

# System Design Document

## 1. Design Input Summary

### Confirmed information

This System Design is based on:

* `01_requirements.md`
* `02_system_analysis.md`
* `02b_system_analysis.md`

The project is a **custom Frappe 14 app** for an **Administrator-only** tool that lets an administrator recreate a **single-page warning letter PDF** as a reusable **Frappe Print Format**.

The system must support:

* Uploading one single-page PDF reference.
* Permanently storing the uploaded reference PDF.
* Manually recreating the PDF layout using editable blocks.
* Static text, dynamic field, image, and branding blocks.
* Field mapping from the Warning Letter / Outstanding Invoice Notice DocType.
* Google Vision OCR assistance for English and Malay.
* Administrator confirmation before OCR text is used.
* Side-by-side preview against the PDF reference.
* Administrator-confirmed 90% visual similarity.
* One saved reusable Print Format for MVP.
* Autonaming format: `GPF-YYYYMMDD-###`.
* Version history with generated output snapshots.
* Final copy-ready output that works when pasted into Frappe built-in Print Format.
* Finalization blocked by missing required mappings, unconfirmed OCR, invalid branding files, blank spacer blocks, overlapping blocks, missing preview, or missing similarity confirmation.

### Confirmed out of scope

The MVP does not include:

* Multi-page PDFs.
* Multiple saved reusable Print Formats.
* Batch generation.
* Lampiran pages.
* Invoice attachment pages.
* Fully automatic layout reconstruction.
* Pixel-perfect conversion guarantee.
* Automated similarity measurement.
* Rollback.
* Uploading new branding files inside this tool.
* Non-administrator access.
* Multi-user approval workflow.

### Design assumptions

1. The app will run inside the existing Frappe 14 environment.
2. The target warning letter data source is the existing **Warning Letter / Outstanding Invoice Notice DocType**.
3. Exact required warning-letter fields are not fully listed in the provided documents, so the design supports a configurable required-field registry rather than hardcoding field names.
4. Branding assets will be selected from existing Frappe `File` records only.
5. Final output will be generated as Frappe Print Format-compatible HTML, CSS, and Jinja-style template content.
6. The app will use Frappe’s native authentication session model.

### Open questions

1. What is the exact DocType name: `Warning Letter`, `Outstanding Invoice Notice`, or another production DocType name?
2. Which specific fields are mandatory for the warning letter?
3. Should Administrator access map to:

   * Built-in `Administrator` user only,
   * `System Manager`,
   * or a custom role such as `Warning Letter Print Format Administrator`?

### Design decision for unresolved role mapping

For this design, the recommended choice is a **custom role**:

`Warning Letter Print Format Administrator`

This avoids giving access to every `System Manager`, while still allowing the built-in `Administrator` user to access everything by default.

---

## 2. Architecture Overview

### Recommended architecture

Use a **native Frappe 14 modular monolith architecture**.

This is the best fit because the project is already constrained to be a custom Frappe 14 app and must integrate tightly with:

* Frappe authentication.
* Frappe roles and permissions.
* Frappe File records.
* Frappe DocTypes.
* Frappe Print Format.
* Frappe versioning/audit behavior.
* Existing Warning Letter / Outstanding Invoice Notice data.

A separate frontend framework or external backend service would add complexity without solving a confirmed MVP requirement.

### Architecture layers

```text
Browser
  |
  | Frappe Desk Page / Custom App UI
  |
Frappe HTTP API Layer
  |
Application Services
  |
Domain Services
  |
Frappe ORM / DocTypes
  |
MariaDB + Frappe File Storage
  |
External Google Vision OCR API
```

### Main components

1. **Builder UI**

   * Displays PDF reference.
   * Allows drawing, editing, aligning, duplicating, deleting blocks.
   * Shows side-by-side preview.
   * Shows validation status.

2. **PDF Reference Service**

   * Validates uploaded PDF.
   * Confirms file type and page count.
   * Stores PDF permanently through Frappe File.

3. **Layout Block Service**

   * Manages block creation, editing, positioning, ordering, duplication, and deletion.
   * Detects overlapping blocks.
   * Prevents blank spacer blocks at validation/finalization.

4. **Field Mapping Service**

   * Reads target DocType metadata.
   * Provides selectable fields.
   * Tracks required field coverage.

5. **OCR Service**

   * Sends PDF or image-rendered PDF page to Google Vision OCR.
   * Stores OCR result as unconfirmed.
   * Allows administrator-edited confirmation.

6. **Branding Asset Service**

   * Lists existing Frappe File records.
   * Allows only PNG, JPG, JPEG, SVG.
   * Rejects WEBP, PDF, and unsupported file types.

7. **Preview Service**

   * Generates sample data.
   * Renders Print Format preview.
   * Stores preview-generated state.

8. **Output Generator Service**

   * Generates copy-ready Frappe Print Format HTML/CSS/Jinja.
   * Validates output before exposing it as final.

9. **Version History Service**

   * Records version number, timestamp, administrator identity, configuration snapshot, changed details, and generated output snapshot.

10. **Finalization Service**

* Runs all finalization rules.
* Blocks finalization on any hard validation failure.

---

## 3. Technology Stack

### Recommended stack

| Layer                    | Recommended technology                                                   | Reason                                                            |
| ------------------------ | ------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Backend framework        | Frappe 14 / Python                                                       | Required by project and best integration path                     |
| Database                 | MariaDB via Frappe ORM                                                   | Native Frappe 14 database layer                                   |
| Frontend                 | Frappe Desk Page with custom JavaScript                                  | Fits Frappe app model and avoids separate SPA complexity          |
| Layout editor            | Native JS with a canvas/SVG helper library such as Konva.js or Fabric.js | Supports drag, resize, draw, select, duplicate, and align blocks  |
| PDF rendering in browser | PDF.js                                                                   | Reliable client-side PDF page rendering for reference display     |
| OCR                      | Google Vision OCR                                                        | Confirmed system dependency                                       |
| File storage             | Frappe File DocType and configured private file storage                  | Required for permanent reference PDF and existing branding assets |
| Template output          | Frappe Print Format-compatible HTML/CSS/Jinja                            | Required copy-ready output target                                 |
| Authentication           | Frappe session authentication                                            | Native and secure                                                 |
| Authorization            | Frappe roles and server-side permission checks                           | Required administrator-only enforcement                           |
| Logging                  | Frappe Error Log + custom app audit logs where needed                    | Native operational traceability                                   |
| Monitoring               | Frappe logs, scheduler health, integration error tracking                | Sufficient for MVP                                                |

### Stack decision

The best stack is:

**Frappe 14 + Python + MariaDB + Frappe Desk Page + JavaScript layout editor + PDF.js + Google Vision OCR.**

### Stack options rejected

| Option                               | Reason rejected                                              |
| ------------------------------------ | ------------------------------------------------------------ |
| Separate React SPA                   | Adds deployment and auth complexity without a confirmed need |
| Separate Node.js API                 | Duplicates Frappe backend responsibilities                   |
| Separate database                    | Breaks Frappe ORM and permissions model                      |
| External print-format service        | Increases risk for copy-ready Frappe compatibility           |
| Fully automated PDF-to-layout engine | Out of scope                                                 |

---

## 4. Module Breakdown

### Module 1: Access Control Module

**Responsibility**

* Verify authenticated user.
* Verify administrator role.
* Deny unauthorized users.

**Linked requirements**

* Administrator-only access.
* Non-administrator access is out of scope.

**Should not handle**

* Layout validation.
* Output generation.
* OCR logic.

---

### Module 2: PDF Reference Module

**Responsibility**

* Accept PDF upload.
* Validate file extension, MIME type, readability, and single-page count.
* Store PDF permanently.
* Link PDF to the reusable Print Format setup.

**Linked requirements**

* Single-page PDF only.
* Permanent PDF reference.
* Invalid, corrupted, protected, or multi-page PDFs rejected.

**Design notes**

* PDF page count validation must happen server-side.
* Client-side validation may be used for early feedback but cannot be trusted.

---

### Module 3: Layout Builder Module

**Responsibility**

* Manage block data.
* Support block drawing, drag, resize, align, duplicate, delete.
* Store position, size, type, order, style, content references.

**Block types**

1. Static text block.
2. Dynamic field block.
3. Image block.
4. Branding block.

**Linked requirements**

* Manual layout recreation.
* Editable layout blocks.
* Overlapping blocks block finalization.
* Blank spacer blocks are not allowed.

---

### Module 4: Field Mapping Module

**Responsibility**

* Read DocType metadata.
* Present available fields.
* Track dynamic block to DocType field mapping.
* Validate all required warning-letter fields are mapped.

**Linked requirements**

* Field selection from Warning Letter / Outstanding Invoice Notice DocType.
* All required warning-letter fields mandatory for finalization.

**Design note**

Because exact fields are not listed, required fields should be configured in a child table named `Required Warning Letter Field`.

---

### Module 5: OCR Module

**Responsibility**

* Send PDF page image or PDF content to Google Vision OCR.
* Store raw OCR result.
* Mark OCR text as unconfirmed by default.
* Allow administrator edit and confirmation.
* Make only confirmed OCR text available for final output.

**Linked requirements**

* Google Vision OCR.
* English and Malay support.
* OCR assistive only.
* Administrator confirmation required.

---

### Module 6: Branding Asset Module

**Responsibility**

* List existing Frappe File records.
* Validate file type.
* Store selected file references.
* Reject unsupported assets.

**Allowed**

* PNG.
* JPG.
* JPEG.
* SVG.

**Blocked**

* WEBP.
* PDF.
* Any other unsupported format.

---

### Module 7: Preview Module

**Responsibility**

* Generate sample data.
* Render the current layout as preview.
* Display side-by-side with uploaded PDF reference.
* Store preview state and timestamp.
* Capture administrator similarity confirmation.

**Linked requirements**

* Auto-generated sample data.
* Side-by-side comparison.
* Administrator-confirmed 90% similarity.
* No automated similarity measurement.

---

### Module 8: Output Generation Module

**Responsibility**

* Convert layout configuration into Frappe-compatible Print Format output.
* Generate copy-ready HTML/CSS/Jinja content.
* Validate generated output structure.
* Store generated output snapshot for version history.

**Linked requirements**

* Output can be copied into Frappe built-in Print Format and works.
* Version history must include generated output snapshots.

---

### Module 9: Version History Module

**Responsibility**

* Create immutable version records on save.
* Store changed block details, field mappings, branding file references, OCR confirmation changes, and generated output snapshot.
* Show version history to administrator.

**Out of scope**

* Rollback.

---

### Module 10: Finalization Module

**Responsibility**

* Run all finalization validation rules.
* Block finalization on hard failures.
* Mark format finalized only after all checks pass.
* Allow output generation only when finalization succeeds or when generating a non-final preview output.

---

## 5. Database Design

Use Frappe DocTypes rather than direct table design.

### 5.1 DocType: `GPF Print Format Setup`

Purpose: Stores the single reusable Print Format configuration.

| Field                       | Type             | Purpose                                                    |
| --------------------------- | ---------------- | ---------------------------------------------------------- |
| `name`                      | Data / Autoname  | Uses `GPF-YYYYMMDD-###`                                    |
| `title`                     | Data             | Human-readable label                                       |
| `target_doctype`            | Link / DocType   | Target Warning Letter / Outstanding Invoice Notice DocType |
| `pdf_reference_file`        | Link / File      | Permanent uploaded PDF reference                           |
| `pdf_page_count`            | Int              | Must equal 1                                               |
| `status`                    | Select           | `Editing`, `Finalized`                                     |
| `similarity_confirmed`      | Check            | Administrator confirmed 90% visual similarity              |
| `similarity_confirmed_by`   | Link / User      | User who confirmed similarity                              |
| `similarity_confirmed_at`   | Datetime         | Confirmation timestamp                                     |
| `last_preview_generated_at` | Datetime         | Tracks preview existence                                   |
| `final_output`              | Long Text / Code | Current generated copy-ready output                        |
| `finalized_by`              | Link / User      | User who finalized                                         |
| `finalized_at`              | Datetime         | Finalization timestamp                                     |
| `current_version_no`        | Int              | Latest saved version                                       |
| `is_active_mvp_record`      | Check            | Used to enforce one reusable Print Format in MVP           |

### 5.2 Child DocType: `GPF Layout Block`

Purpose: Stores each block in the manually recreated layout.

| Field             | Type        | Purpose                                             |
| ----------------- | ----------- | --------------------------------------------------- |
| `parent`          | Link        | Parent `GPF Print Format Setup`                     |
| `block_id`        | Data        | Stable UI identifier                                |
| `block_type`      | Select      | `Static Text`, `Dynamic Field`, `Image`, `Branding` |
| `x`               | Float       | Horizontal position on page canvas                  |
| `y`               | Float       | Vertical position on page canvas                    |
| `width`           | Float       | Block width                                         |
| `height`          | Float       | Block height                                        |
| `z_index`         | Int         | Rendering order                                     |
| `alignment`       | Select      | Left, center, right, justified                      |
| `font_family`     | Data        | Print text font                                     |
| `font_size`       | Float       | Print text size                                     |
| `font_weight`     | Select      | Normal, bold                                        |
| `text_content`    | Long Text   | Static or confirmed OCR text                        |
| `fieldname`       | Data        | Target DocType field for dynamic blocks             |
| `file_reference`  | Link / File | Image or branding asset reference                   |
| `ocr_source_id`   | Data        | Links text to OCR result where applicable           |
| `ocr_confirmed`   | Check       | Required if block uses OCR text                     |
| `is_blank_spacer` | Check       | Must not be true                                    |
| `style_json`      | JSON        | Additional CSS-like style settings                  |

### 5.3 Child DocType: `GPF Required Field`

Purpose: Configures fields required for finalization.

| Field                          | Type  | Purpose                                         |
| ------------------------------ | ----- | ----------------------------------------------- |
| `fieldname`                    | Data  | Required target DocType field                   |
| `label`                        | Data  | Display label                                   |
| `fieldtype`                    | Data  | Frappe field type                               |
| `is_required_for_finalization` | Check | Must be true for required warning letter fields |
| `mapped_block_id`              | Data  | Block that maps this field                      |

### 5.4 DocType: `GPF OCR Result`

Purpose: Stores OCR output and confirmation state.

| Field            | Type        | Purpose                              |
| ---------------- | ----------- | ------------------------------------ |
| `setup`          | Link        | Related Print Format setup           |
| `source_file`    | Link / File | OCR source PDF                       |
| `language_hints` | Data        | `en`, `ms`                           |
| `raw_text`       | Long Text   | Original Google Vision OCR result    |
| `edited_text`    | Long Text   | Administrator-edited text            |
| `confirmed`      | Check       | Whether admin confirmed the OCR text |
| `confirmed_by`   | Link / User | Confirmer                            |
| `confirmed_at`   | Datetime    | Confirmation timestamp               |
| `ocr_status`     | Select      | Pending, Success, Failed             |
| `error_message`  | Small Text  | Failure details                      |

### 5.5 DocType: `GPF Version History`

Purpose: Immutable traceability record for each save.

| Field                         | Type             | Purpose                            |
| ----------------------------- | ---------------- | ---------------------------------- |
| `setup`                       | Link             | Related Print Format setup         |
| `version_no`                  | Int              | Sequential version number          |
| `saved_by`                    | Link / User      | Administrator who saved            |
| `saved_at`                    | Datetime         | Save timestamp                     |
| `change_summary`              | Small Text       | Human-readable change summary      |
| `block_snapshot_json`         | JSON             | Layout block snapshot              |
| `field_mapping_snapshot_json` | JSON             | Field mapping snapshot             |
| `branding_snapshot_json`      | JSON             | Branding file references           |
| `ocr_snapshot_json`           | JSON             | OCR confirmation state             |
| `generated_output_snapshot`   | Long Text / Code | Required generated output snapshot |

### 5.6 DocType: `GPF Validation Issue`

Purpose: Stores validation issue results for display.

| Field        | Type       | Purpose                          |
| ------------ | ---------- | -------------------------------- |
| `setup`      | Link       | Related setup                    |
| `severity`   | Select     | Error, Warning, Info             |
| `code`       | Data       | Machine-readable validation code |
| `message`    | Small Text | Administrator-facing message     |
| `block_id`   | Data       | Optional related block           |
| `fieldname`  | Data       | Optional related field           |
| `created_at` | Datetime   | Validation timestamp             |

---

## 6. API Design

Use Frappe whitelisted methods under:

`/api/method/gpf_builder.api.<method_name>`

All APIs must perform server-side authorization.

---

### API 1: Get builder state

**Method**

`GET`

**Path**

`/api/method/gpf_builder.api.get_builder_state`

**Request**

```json
{
  "setup_name": "GPF-20260513-001"
}
```

**Response**

```json
{
  "setup": {},
  "blocks": [],
  "required_fields": [],
  "ocr_results": [],
  "validation_issues": []
}
```

**Validation**

* User must be authorized.
* Setup must exist.
* Setup must be the active MVP setup.

**Errors**

| Code            | Meaning             |
| --------------- | ------------------- |
| `UNAUTHORIZED`  | User is not allowed |
| `NOT_FOUND`     | Setup not found     |
| `INVALID_STATE` | Setup is not active |

---

### API 2: Upload PDF reference

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.upload_pdf_reference`

**Request**

Multipart file upload:

```json
{
  "file": "warning-letter.pdf"
}
```

**Response**

```json
{
  "setup_name": "GPF-20260513-001",
  "file_url": "/private/files/warning-letter.pdf",
  "page_count": 1
}
```

**Validation**

* File must be PDF.
* MIME type must be PDF.
* PDF must be readable.
* PDF must not be protected in a way that prevents page count extraction.
* Page count must equal 1.

**Errors**

| Code                 | Meaning                     |
| -------------------- | --------------------------- |
| `INVALID_FILE_TYPE`  | Not a PDF                   |
| `INVALID_PAGE_COUNT` | More or fewer than one page |
| `PDF_UNREADABLE`     | Corrupted or protected file |
| `STORAGE_FAILED`     | File could not be saved     |

---

### API 3: Save layout blocks

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.save_blocks`

**Request**

```json
{
  "setup_name": "GPF-20260513-001",
  "blocks": [
    {
      "block_id": "block-001",
      "block_type": "Dynamic Field",
      "x": 40,
      "y": 120,
      "width": 200,
      "height": 32,
      "fieldname": "customer_name"
    }
  ]
}
```

**Response**

```json
{
  "saved": true,
  "validation_issues": []
}
```

**Validation**

* Block type must be valid.
* Position and size must be valid numbers.
* Width and height must be greater than zero.
* Dynamic field blocks must have a valid `fieldname`.
* Static text blocks must have text content unless explicitly empty is meaningful.
* Blank spacer blocks are not allowed.
* Image and branding blocks must have valid file references.

**Errors**

| Code                     | Meaning                     |
| ------------------------ | --------------------------- |
| `INVALID_BLOCK_TYPE`     | Unsupported block type      |
| `INVALID_POSITION`       | Position or size invalid    |
| `INVALID_FIELD_MAPPING`  | Field does not exist        |
| `BLANK_SPACER_BLOCK`     | Blank spacer detected       |
| `INVALID_FILE_REFERENCE` | Image/branding file invalid |

---

### API 4: Get target DocType fields

**Method**

`GET`

**Path**

`/api/method/gpf_builder.api.get_target_fields`

**Request**

```json
{
  "target_doctype": "Outstanding Invoice Notice"
}
```

**Response**

```json
{
  "fields": [
    {
      "fieldname": "customer_name",
      "label": "Customer Name",
      "fieldtype": "Data",
      "required_for_finalization": true
    }
  ]
}
```

**Validation**

* Target DocType must be allowed.
* User must be authorized.

**Errors**

| Code                  | Meaning                    |
| --------------------- | -------------------------- |
| `DOCTYPE_NOT_ALLOWED` | Unsupported target DocType |
| `DOCTYPE_NOT_FOUND`   | Target DocType missing     |

---

### API 5: Run OCR

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.run_ocr`

**Request**

```json
{
  "setup_name": "GPF-20260513-001",
  "language_hints": ["en", "ms"]
}
```

**Response**

```json
{
  "ocr_result_id": "OCR-0001",
  "raw_text": "Recognized text...",
  "confirmed": false
}
```

**Validation**

* PDF reference must exist.
* OCR language hints must be English and/or Malay for MVP.
* Google Vision credentials must be configured.

**Errors**

| Code                 | Meaning                 |
| -------------------- | ----------------------- |
| `PDF_REQUIRED`       | No PDF reference        |
| `OCR_PROVIDER_ERROR` | Google Vision failure   |
| `OCR_CONFIG_MISSING` | Missing OCR credentials |

---

### API 6: Confirm OCR text

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.confirm_ocr_text`

**Request**

```json
{
  "ocr_result_id": "OCR-0001",
  "edited_text": "Confirmed administrator-reviewed text"
}
```

**Response**

```json
{
  "confirmed": true,
  "confirmed_at": "2026-05-13T10:30:00"
}
```

**Validation**

* OCR result must exist.
* Edited text must not be empty when used by a text block.
* User must be authorized.

**Errors**

| Code                   | Meaning                           |
| ---------------------- | --------------------------------- |
| `OCR_RESULT_NOT_FOUND` | OCR record missing                |
| `EMPTY_CONFIRMED_TEXT` | Cannot confirm empty text for use |

---

### API 7: List branding assets

**Method**

`GET`

**Path**

`/api/method/gpf_builder.api.list_branding_assets`

**Request**

```json
{
  "file_type": "image"
}
```

**Response**

```json
{
  "files": [
    {
      "name": "FILE-0001",
      "file_name": "logo.png",
      "file_url": "/private/files/logo.png",
      "extension": "png"
    }
  ]
}
```

**Validation**

* Only existing Frappe File records.
* Only PNG, JPG, JPEG, SVG returned.

**Errors**

| Code                 | Meaning                 |
| -------------------- | ----------------------- |
| `UNAUTHORIZED`       | User not allowed        |
| `FILE_ACCESS_DENIED` | User cannot access file |

---

### API 8: Generate preview

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.generate_preview`

**Request**

```json
{
  "setup_name": "GPF-20260513-001"
}
```

**Response**

```json
{
  "preview_html": "<html>...</html>",
  "sample_data": {},
  "generated_at": "2026-05-13T10:40:00"
}
```

**Validation**

* PDF reference must exist.
* Blocks must be structurally valid.
* Required mappings may be incomplete for preview, but issues should be shown.

**Errors**

| Code                    | Meaning                  |
| ----------------------- | ------------------------ |
| `PDF_REQUIRED`          | No PDF reference         |
| `PREVIEW_RENDER_FAILED` | Preview could not render |

---

### API 9: Confirm visual similarity

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.confirm_similarity`

**Request**

```json
{
  "setup_name": "GPF-20260513-001",
  "confirmed": true
}
```

**Response**

```json
{
  "similarity_confirmed": true,
  "confirmed_by": "administrator@example.com",
  "confirmed_at": "2026-05-13T10:45:00"
}
```

**Validation**

* Preview must have been generated.
* Confirmation must be from authorized administrator.

**Errors**

| Code               | Meaning              |
| ------------------ | -------------------- |
| `PREVIEW_REQUIRED` | No preview generated |
| `UNAUTHORIZED`     | User not allowed     |

---

### API 10: Save reusable Print Format setup

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.save_setup`

**Request**

```json
{
  "setup_name": "GPF-20260513-001",
  "change_summary": "Adjusted header alignment and mapped customer fields"
}
```

**Response**

```json
{
  "saved": true,
  "version_no": 4
}
```

**Validation**

* Setup must exist.
* Version history snapshot must be created.
* Generated output snapshot must be stored.

**Errors**

| Code                      | Meaning                         |
| ------------------------- | ------------------------------- |
| `VERSION_SNAPSHOT_FAILED` | Version history snapshot failed |
| `SAVE_FAILED`             | Setup could not be saved        |

---

### API 11: Validate finalization

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.validate_finalization`

**Request**

```json
{
  "setup_name": "GPF-20260513-001"
}
```

**Response**

```json
{
  "can_finalize": false,
  "issues": [
    {
      "code": "OVERLAPPING_BLOCKS",
      "message": "Blocks block-001 and block-002 overlap."
    }
  ]
}
```

**Validation rules**

* PDF reference exists.
* PDF has one page.
* All required fields are mapped.
* OCR-used text is confirmed.
* Branding file types are valid.
* No WEBP branding assets.
* No PDF branding assets.
* No blank spacer blocks.
* No overlapping blocks.
* Preview has been generated.
* Similarity has been confirmed.
* Generated output can be produced.

---

### API 12: Finalize Print Format

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.finalize_setup`

**Request**

```json
{
  "setup_name": "GPF-20260513-001"
}
```

**Response**

```json
{
  "finalized": true,
  "finalized_at": "2026-05-13T10:50:00"
}
```

**Errors**

| Code                       | Meaning                                  |
| -------------------------- | ---------------------------------------- |
| `FINALIZATION_BLOCKED`     | One or more validation failures          |
| `OUTPUT_GENERATION_FAILED` | Copy-ready output could not be generated |

---

### API 13: Generate copy-ready output

**Method**

`POST`

**Path**

`/api/method/gpf_builder.api.generate_final_output`

**Request**

```json
{
  "setup_name": "GPF-20260513-001"
}
```

**Response**

```json
{
  "output": "<style>...</style><div>...</div>",
  "copy_ready": true
}
```

**Validation**

* Setup must be finalized.
* Output must be non-empty.
* Output must avoid unsafe scripts.
* Output must be compatible with Frappe Print Format editor.

**Errors**

| Code                       | Meaning                       |
| -------------------------- | ----------------------------- |
| `NOT_FINALIZED`            | Setup must be finalized first |
| `OUTPUT_GENERATION_FAILED` | Output failed validation      |

---

## 7. UI Screen Design

### Screen 1: Access Denied Screen

**Purpose**

Inform unauthorized users they cannot access the builder.

**Components**

* Access denied message.
* Current user identity.
* Link back to Frappe Desk.

**User actions**

* Return to Desk.

**Empty state**

Not applicable.

**Loading state**

Brief permission-check spinner.

**Error state**

If permission check fails unexpectedly, show generic access validation error.

---

### Screen 2: Builder Home / Setup Screen

**Purpose**

Central workspace for the single reusable Print Format.

**Components**

* Setup name.
* Status badge: Editing / Finalized.
* PDF reference status.
* Required fields completion status.
* Preview status.
* Similarity confirmation status.
* Finalization readiness panel.
* Main actions:

  * Upload PDF.
  * Open Layout Builder.
  * Generate Preview.
  * Save.
  * Finalize.
  * Generate Output.

**User actions**

* Upload reference PDF.
* Navigate to layout builder.
* Run validation.
* Save changes.
* Finalize setup.

**Empty state**

* “No PDF reference uploaded yet.”
* Show upload prompt.

**Loading state**

* Loading setup configuration.
* Loading validation status.

**Error state**

* Setup could not load.
* Permission denied.
* Active MVP setup conflict.

---

### Screen 3: PDF Upload Screen / Modal

**Purpose**

Allow administrator to upload one single-page warning letter PDF.

**Components**

* File picker.
* PDF validation result.
* Upload progress.
* Current reference PDF preview.
* Replacement warning if a reference already exists.

**User actions**

* Select PDF.
* Upload PDF.
* Cancel.

**Empty state**

* No PDF selected.

**Loading state**

* Uploading.
* Validating PDF.
* Storing PDF.

**Error state**

* Invalid file type.
* Corrupted PDF.
* Protected/unreadable PDF.
* Multi-page PDF.
* Storage failure.

---

### Screen 4: Layout Builder Screen

**Purpose**

Manually recreate the warning letter layout using editable blocks over the PDF reference.

**Components**

* PDF reference canvas.
* Block overlay layer.
* Toolbar:

  * Add static text.
  * Add dynamic field.
  * Add image.
  * Add branding.
  * Duplicate.
  * Delete.
  * Align.
  * Bring forward/send backward.
* Block properties panel.
* Position and size controls.
* Field mapping selector.
* Style controls.
* Validation issue sidebar.

**User actions**

* Draw block.
* Select block.
* Drag block.
* Resize block.
* Configure block type.
* Map dynamic field.
* Select image or branding file.
* Duplicate block.
* Delete block.
* Align blocks.

**Empty state**

* “No layout blocks yet. Draw a block over the PDF reference.”

**Loading state**

* Loading PDF reference.
* Loading existing blocks.
* Saving block changes.

**Error state**

* PDF cannot display.
* Block save failed.
* Invalid field mapping.
* Invalid image reference.
* Unsupported branding asset.

---

### Screen 5: OCR Assistance Screen / Panel

**Purpose**

Assist the administrator by extracting text from the PDF.

**Components**

* Run OCR button.
* Language hint display: English, Malay.
* Raw OCR text area.
* Editable confirmed text area.
* Confirmation checkbox/button.
* OCR status.

**User actions**

* Run OCR.
* Review OCR text.
* Edit OCR text.
* Confirm OCR text.
* Use confirmed OCR text in a static text block.

**Empty state**

* “No OCR has been run yet.”

**Loading state**

* OCR in progress.

**Error state**

* Google Vision unavailable.
* OCR credentials missing.
* OCR returned no useful text.
* OCR text not confirmed.

---

### Screen 6: Branding Asset Selector

**Purpose**

Select existing logo, signature, or footer branding file.

**Components**

* Existing file list.
* Thumbnail preview.
* File name.
* File extension.
* Allowed type badge.
* Search/filter.

**User actions**

* Select existing file.
* Attach to branding block.

**Empty state**

* “No valid PNG, JPG, JPEG, or SVG files found.”

**Loading state**

* Loading existing files.

**Error state**

* File inaccessible.
* Unsupported file type.
* WEBP blocked.
* PDF blocked.

---

### Screen 7: Preview and Similarity Confirmation Screen

**Purpose**

Allow administrator to compare generated preview against original PDF reference.

**Components**

* Left panel: original PDF reference.
* Right panel: generated preview.
* Zoom controls.
* Page fit controls.
* Validation issue summary.
* Similarity confirmation checkbox:

  * “I confirm this preview reaches the required 90% visual similarity target.”
* Notice:

  * “The system does not guarantee pixel-perfect conversion.”

**User actions**

* Generate preview.
* Compare visually.
* Confirm similarity.
* Return to builder for corrections.

**Empty state**

* “Generate a preview to compare against the PDF reference.”

**Loading state**

* Generating sample data.
* Rendering preview.

**Error state**

* Preview generation failed.
* Missing PDF reference.
* Invalid block configuration.

---

### Screen 8: Finalization Screen

**Purpose**

Show final readiness and block finalization if validation fails.

**Components**

* Finalization checklist.
* Blocking validation issues.
* Non-blocking warnings.
* Finalize button.
* Link to affected block or field.

**User actions**

* Run final validation.
* Fix validation issue.
* Finalize setup.

**Empty state**

* Not applicable; validation checklist always appears.

**Loading state**

* Running validation.
* Generating final output.
* Creating version snapshot.

**Error state**

* Missing required fields.
* Overlapping blocks.
* Blank spacer blocks.
* Unconfirmed OCR.
* Invalid branding asset.
* Preview missing.
* Similarity not confirmed.
* Output generation failed.

---

### Screen 9: Copy-Ready Output Screen

**Purpose**

Display final generated Frappe Print Format output.

**Components**

* Read-only code area.
* Copy button.
* Output generated timestamp.
* Compatibility notice.
* Finalization status.

**User actions**

* Copy output.
* Paste into Frappe built-in Print Format editor.
* Return to builder if output issue is found.

**Empty state**

* “Finalize the setup before generating copy-ready output.”

**Loading state**

* Generating output.

**Error state**

* Setup not finalized.
* Output generation failed.
* Output failed compatibility validation.

---

### Screen 10: Version History Screen

**Purpose**

Show saved versions and traceability.

**Components**

* Version list.
* Timestamp.
* Saved by.
* Change summary.
* Changed block details.
* Field mapping changes.
* Branding references.
* OCR confirmation changes.
* Generated output snapshot viewer.

**User actions**

* View version details.
* Copy historical output snapshot for inspection only.

**Empty state**

* “No saved versions yet.”

**Loading state**

* Loading version history.

**Error state**

* Version history cannot load.
* Snapshot missing.

**Important design rule**

Rollback controls must not be shown because rollback is out of scope.

---

## 8. State Management Design

### Server-side state

Server-side state is the source of truth.

Stored state includes:

* PDF reference.
* Layout blocks.
* Field mappings.
* OCR results and confirmation status.
* Branding file references.
* Preview timestamp.
* Similarity confirmation.
* Finalization status.
* Generated output.
* Version history.

### Client-side state

Client-side state is temporary and used for UI responsiveness.

Client-side state includes:

* Currently selected block.
* Dragging/resizing state.
* Unsaved changes indicator.
* Zoom level.
* Active panel.
* Local canvas coordinates.

### State transition model

```text
No PDF
  -> PDF Uploaded
  -> Layout Editing
  -> Preview Generated
  -> Similarity Confirmed
  -> Finalization Validated
  -> Finalized
  -> Copy-Ready Output Generated
```

### Save behavior

* Save stores current progress.
* Save creates a version history record.
* Save does not require all finalization rules to pass.
* Save must still reject structurally invalid data.

### Finalize behavior

Finalize is stricter than save.

Finalize requires:

* Valid PDF.
* Required fields mapped.
* Confirmed OCR where used.
* Valid branding assets.
* No blank spacer blocks.
* No overlapping blocks.
* Preview generated.
* Similarity confirmed.
* Output generation successful.

---

## 9. Authentication Design

### Authentication mechanism

Use native **Frappe session authentication**.

The administrator must already be logged in to Frappe.

### Authentication flow

1. User opens the builder page.
2. Frappe validates session.
3. If no valid session exists, user is redirected to Frappe login.
4. After login, authorization check runs.
5. Authorized users see the builder.
6. Unauthorized users see the Access Denied screen.

### API authentication

All API calls require:

* Valid Frappe session.
* CSRF protection where applicable.
* Server-side user identity from Frappe session context.

### Design decision

No separate authentication system should be introduced.

Reason:

* The app runs inside Frappe.
* Frappe already provides login, sessions, password policies, and user records.
* A separate auth system would increase security risk and maintenance effort.

---

## 10. Authorization Design

### Recommended role

Create a custom role:

`Warning Letter Print Format Administrator`

### Built-in Administrator behavior

The built-in Frappe `Administrator` user should always pass authorization.

### Permission matrix

| Action                 | Required permission                                 |
| ---------------------- | --------------------------------------------------- |
| Access app             | Custom administrator role or built-in Administrator |
| Upload PDF             | Custom administrator role or built-in Administrator |
| Create blocks          | Custom administrator role or built-in Administrator |
| Edit blocks            | Custom administrator role or built-in Administrator |
| Delete blocks          | Custom administrator role or built-in Administrator |
| Use OCR                | Custom administrator role or built-in Administrator |
| Confirm OCR            | Custom administrator role or built-in Administrator |
| Map fields             | Custom administrator role or built-in Administrator |
| Select branding assets | Custom administrator role or built-in Administrator |
| Generate preview       | Custom administrator role or built-in Administrator |
| Confirm similarity     | Custom administrator role or built-in Administrator |
| Save setup             | Custom administrator role or built-in Administrator |
| Finalize setup         | Custom administrator role or built-in Administrator |
| Generate final output  | Custom administrator role or built-in Administrator |
| View version history   | Custom administrator role or built-in Administrator |

### Server-side authorization

Every whitelisted method must check authorization.

Client-side hiding of buttons is not sufficient.

### File authorization

The Branding Asset Module must verify that the selected Frappe File record:

* Exists.
* Is accessible to the authorized administrator.
* Has an allowed file type.
* Is not WEBP.
* Is not PDF.

---

## 11. Validation Design

### Validation levels

1. **Client-side validation**

   * Fast feedback.
   * Prevent obvious mistakes.
   * Not trusted for final enforcement.

2. **Server-side save validation**

   * Enforces structural data validity.
   * Prevents invalid block records.

3. **Server-side finalization validation**

   * Enforces all business rules.

---

### PDF validation

| Rule                               | When enforced       |
| ---------------------------------- | ------------------- |
| File must be PDF                   | Upload              |
| MIME type must be PDF              | Upload              |
| File must be readable              | Upload              |
| File must contain exactly one page | Upload              |
| File must be permanently stored    | Upload/finalization |
| File must be displayable           | Upload/preview      |

---

### Block validation

| Rule                                              | When enforced     |
| ------------------------------------------------- | ----------------- |
| Block type must be valid                          | Save/finalization |
| Position must be numeric                          | Save/finalization |
| Width and height must be greater than zero        | Save/finalization |
| Block must stay within page bounds                | Save/finalization |
| Dynamic block must map to valid field             | Save/finalization |
| Image block must reference valid file             | Save/finalization |
| Branding block must reference valid branding file | Save/finalization |
| Blank spacer block is not allowed                 | Save/finalization |
| Overlapping blocks must block finalization        | Finalization      |

### Overlap detection design

Two blocks overlap if their bounding rectangles intersect.

Pseudocode only:

```text
blocks_overlap(a, b):
    return not (
        a.right <= b.left
        or a.left >= b.right
        or a.bottom <= b.top
        or a.top >= b.bottom
    )
```

Overlap validation should ignore deleted blocks and should use normalized page coordinates.

---

### Field mapping validation

| Rule                                                             | When enforced     |
| ---------------------------------------------------------------- | ----------------- |
| Field must exist in target DocType                               | Save/finalization |
| Required warning-letter fields must be mapped                    | Finalization      |
| Duplicate mappings should be warned unless intentionally allowed | Save/finalization |
| Field type must be renderable                                    | Save/finalization |

---

### OCR validation

| Rule                                            | When enforced    |
| ----------------------------------------------- | ---------------- |
| OCR source PDF must exist                       | OCR run          |
| OCR language hints limited to English and Malay | OCR run          |
| OCR output is unconfirmed by default            | OCR run          |
| OCR-used text must be confirmed                 | Finalization     |
| Administrator-edited OCR text must be stored    | OCR confirmation |

---

### Branding validation

| Rule                                         | When enforced          |
| -------------------------------------------- | ---------------------- |
| Branding file must exist                     | Selection/finalization |
| Branding file must be PNG, JPG, JPEG, or SVG | Selection/finalization |
| WEBP must be rejected                        | Selection/finalization |
| PDF must be rejected                         | Selection/finalization |
| File must be accessible                      | Selection/finalization |

---

### Preview and similarity validation

| Rule                                               | When enforced           |
| -------------------------------------------------- | ----------------------- |
| Preview requires PDF reference                     | Preview                 |
| Preview requires renderable blocks                 | Preview                 |
| Similarity confirmation requires generated preview | Similarity confirmation |
| Similarity must be administrator-confirmed         | Finalization            |
| Automated similarity is not required               | Design rule             |

---

### Output validation

| Rule                                                      | When enforced        |
| --------------------------------------------------------- | -------------------- |
| Output must be generated from current configuration       | Preview/final output |
| Final output requires finalized setup                     | Final output         |
| Output must be non-empty                                  | Output generation    |
| Output must be compatible with Frappe Print Format editor | Output generation    |
| Unsafe scripts must not be included                       | Output generation    |
| Output snapshot must be saved in version history          | Save/finalization    |

---

## 12. Error Handling Design

### Error handling principles

* Show administrator-friendly messages.
* Preserve technical details in logs.
* Do not expose secrets, file paths, stack traces, or Google credentials.
* Blocking finalization errors must clearly explain what to fix.
* OCR failure must not prevent manual layout recreation.
* Output generation failure must not be presented as successful final output.

### Error categories

| Category             | Examples                    | Handling                                  |
| -------------------- | --------------------------- | ----------------------------------------- |
| Authorization errors | Unauthorized user           | Access denied                             |
| File errors          | Invalid PDF, unreadable PDF | Block upload                              |
| Validation errors    | Missing fields, overlap     | Show issue list                           |
| OCR errors           | Google Vision unavailable   | Show OCR failure, allow manual editing    |
| Storage errors       | File save failed            | Show retry-safe error                     |
| Output errors        | Generated output invalid    | Block final output                        |
| Version errors       | Snapshot failed             | Report issue because snapshot is required |
| System errors        | Unexpected exception        | Show generic message, log details         |

### Finalization error behavior

If any finalization rule fails:

* Do not finalize.
* Do not mark status as finalized.
* Do not expose final output as copy-ready.
* Show all blocking issues together.
* Link each issue to the affected field, block, or screen where possible.

### Example finalization issue messages

| Code                       | Message                                                                    |
| -------------------------- | -------------------------------------------------------------------------- |
| `PDF_REFERENCE_MISSING`    | Upload a single-page PDF reference before finalizing.                      |
| `REQUIRED_FIELD_MISSING`   | Required field `{fieldname}` is not mapped to any dynamic block.           |
| `OCR_NOT_CONFIRMED`        | OCR text used in block `{block_id}` must be reviewed and confirmed.        |
| `INVALID_BRANDING_FILE`    | Branding file `{file_name}` is not an allowed PNG, JPG, JPEG, or SVG file. |
| `OVERLAPPING_BLOCKS`       | Blocks `{block_a}` and `{block_b}` overlap. Move or resize one block.      |
| `BLANK_SPACER_BLOCK`       | Blank spacer block `{block_id}` is not allowed.                            |
| `PREVIEW_REQUIRED`         | Generate a preview before finalizing.                                      |
| `SIMILARITY_NOT_CONFIRMED` | Confirm the 90% visual similarity target before finalizing.                |
| `OUTPUT_GENERATION_FAILED` | The copy-ready Print Format output could not be generated.                 |

---

## 13. Logging and Monitoring Design

### What to log

| Event                          | Log level |
| ------------------------------ | --------- |
| Unauthorized access attempt    | Warning   |
| PDF upload success             | Info      |
| PDF upload validation failure  | Warning   |
| OCR request started            | Info      |
| OCR provider failure           | Error     |
| OCR text confirmed             | Info      |
| Save completed                 | Info      |
| Version snapshot created       | Info      |
| Version snapshot failure       | Error     |
| Finalization validation failed | Warning   |
| Finalization completed         | Info      |
| Output generation failed       | Error     |

### What not to log

* Google Vision credentials.
* Full private file paths.
* Full generated output unless stored intentionally in version history.
* Sensitive warning letter data beyond required audit metadata.

### Monitoring approach

For MVP, use:

* Frappe Error Log.
* Frappe request logs.
* Custom audit records for save/finalize events.
* Integration error logs for Google Vision OCR.

### Operational alerts

Recommended alerts:

* OCR provider repeatedly fails.
* Version snapshot creation fails.
* Output generation repeatedly fails.
* Unauthorized access attempts increase.

---

## 14. Security Design

### Access security

* All screens and APIs require authenticated Frappe session.
* All privileged actions require the custom administrator role or built-in Administrator.
* Client-side controls are only convenience; server-side checks are mandatory.

### File security

* Uploaded PDF reference should be stored as a private file.
* Branding files must be selected from existing Frappe File records.
* File extension and MIME type must both be checked.
* PDF and WEBP branding assets must be blocked.
* SVG files must be sanitized or rendered in a safe way because SVG can carry script-like content.

### OCR security

* Google Vision credentials must be stored in secure Frappe configuration, not in client-side code.
* OCR requests should be sent server-side.
* OCR failure details shown to user should be sanitized.

### Template/output security

Generated Print Format output must:

* Avoid arbitrary JavaScript.
* Avoid unsafe script tags.
* Escape dynamic field output where appropriate.
* Limit generated CSS to expected layout properties.
* Avoid exposing server-only paths.
* Reference files using Frappe-compatible file URLs.

### Data integrity

* Version history records should be immutable through UI.
* Finalized status should only be set by the Finalization Service.
* Similarity confirmation should store user and timestamp.
* OCR confirmation should store user and timestamp.

### CSRF and request protection

* Use Frappe’s standard request protection.
* Mutating APIs must require proper session and CSRF handling.

---

## 15. Performance Considerations

### PDF rendering

* Render only the single PDF page.
* Use PDF.js client-side for display.
* Cache rendered page image during the editing session.
* Avoid repeated server PDF parsing after page count is validated.

### Layout editing

* Store normalized coordinates to avoid recalculation errors.
* Debounce frequent drag/resize saves.
* Use local UI state during active dragging.
* Save only after drag/resize ends or on explicit save.

### Preview generation

* Generate preview on demand, not continuously.
* Cache last preview timestamp.
* Invalidate preview when:

  * Blocks change.
  * Field mappings change.
  * Branding assets change.
  * OCR-confirmed content changes.
  * PDF reference changes.

### OCR

* OCR should be explicit, not automatic on every upload.
* Store OCR result to avoid repeated Google Vision calls.
* Allow re-run only when administrator requests it.

### Version history

* Store snapshots only on save/finalization, not every minor canvas movement.
* Use JSON snapshots for traceability.
* Avoid excessive large binary data in version records.

### Output generation

* Generate final output after finalization.
* Store generated output in setup and version snapshot.
* Regenerate only when configuration changes and setup returns to editing state.

---

## 16. File and Folder Structure

Recommended Frappe app structure:

```text
gpf_builder/
  gpf_builder/
    __init__.py

    api/
      __init__.py
      builder.py
      pdf_reference.py
      layout_blocks.py
      field_mapping.py
      ocr.py
      branding.py
      preview.py
      finalization.py
      output_generation.py
      version_history.py

    services/
      access_control_service.py
      pdf_reference_service.py
      layout_block_service.py
      field_mapping_service.py
      ocr_service.py
      branding_asset_service.py
      preview_service.py
      finalization_service.py
      output_generator_service.py
      version_history_service.py
      validation_service.py

    domain/
      block_types.py
      validation_codes.py
      output_template_model.py
      finalization_rules.py

    doctype/
      gpf_print_format_setup/
        gpf_print_format_setup.json
        gpf_print_format_setup.py
      gpf_layout_block/
        gpf_layout_block.json
        gpf_layout_block.py
      gpf_required_field/
        gpf_required_field.json
        gpf_required_field.py
      gpf_ocr_result/
        gpf_ocr_result.json
        gpf_ocr_result.py
      gpf_version_history/
        gpf_version_history.json
        gpf_version_history.py
      gpf_validation_issue/
        gpf_validation_issue.json
        gpf_validation_issue.py

    page/
      gpf_builder/
        gpf_builder.json
        gpf_builder.py
        gpf_builder.js

    public/
      js/
        builder_canvas.js
        pdf_reference_viewer.js
        block_properties_panel.js
        validation_panel.js
        preview_viewer.js
      css/
        gpf_builder.css

    templates/
      print_format_base.html
      preview_shell.html

    integrations/
      google_vision_client.py

    utils/
      pdf_utils.py
      file_type_utils.py
      coordinate_utils.py
      sanitizer.py
      naming.py

  hooks.py
  modules.txt
  patches.txt
```

### Folder responsibility rules

* `api/` exposes whitelisted methods only.
* `services/` contains business logic.
* `domain/` contains rule definitions and constants.
* `doctype/` contains Frappe DocType controllers.
* `integrations/` contains external provider clients.
* `utils/` contains technical helper functions only.
* UI JavaScript must not contain finalization business rules.

---

## 17. External Integrations

### Google Vision OCR

**Purpose**

Provide assistive OCR for English and Malay text extraction.

**Direction**

Server-side integration only.

**Input**

* PDF page image or PDF reference transformed into OCR-compatible input.
* Language hints: English and Malay.

**Output**

* Raw OCR text.
* OCR status.
* Error message if failed.

**Design rules**

* OCR result is unconfirmed by default.
* OCR text cannot be used in final output unless confirmed by administrator.
* OCR failure does not block manual recreation.

---

### Frappe File

**Purpose**

Store uploaded PDF reference and select existing branding assets.

**Used for**

* Permanent PDF reference.
* Existing PNG/JPG/JPEG/SVG branding assets.

**Design rules**

* Uploaded reference PDF should be private.
* Branding assets must already exist.
* Branding asset upload is out of scope.

---

### Frappe Print Format

**Purpose**

Target environment for final generated output.

**Output format**

* HTML.
* CSS.
* Frappe/Jinja-compatible dynamic field expressions.

**Design rules**

* Output must be copy-ready.
* Output must work when pasted into Frappe built-in Print Format.
* Pixel-perfect rendering is not promised.

---

### Target Warning Letter / Outstanding Invoice Notice DocType

**Purpose**

Provides dynamic fields for mapping.

**Design rules**

* Field list must be read from Frappe DocType metadata.
* Required warning-letter fields must be configured and validated.
* Exact field names remain an open question until confirmed.

---

## 18. Design Decisions

### DD-001: Use native Frappe 14 stack

**Decision**

Use Frappe 14, Python, MariaDB, Frappe Desk Page, and custom JavaScript.

**Reason**

The project is a Frappe 14 custom app and must integrate with Frappe Print Format, File, DocType metadata, permissions, and session authentication.

**Linked requirements**

* Custom Frappe 14 app.
* Frappe Print Format integration.
* Existing Frappe files.

---

### DD-002: Use custom administrator role

**Decision**

Use `Warning Letter Print Format Administrator` role, while allowing built-in Administrator.

**Reason**

This is more precise than granting all System Managers access.

**Linked requirements**

* Administrator-only access.

---

### DD-003: Use one active setup record for MVP

**Decision**

Use `GPF Print Format Setup` with server-side enforcement of one active MVP record.

**Reason**

The MVP supports only one saved reusable Print Format, while still preserving a normal named record using `GPF-YYYYMMDD-###`.

**Linked requirements**

* One reusable Print Format only.
* Autonaming format `GPF-YYYYMMDD-###`.

---

### DD-004: Separate Save from Finalize

**Decision**

Save records progress and version history. Finalize enforces full readiness.

**Reason**

System Analysis explicitly separates save and finalize.

**Linked requirements**

* Save reusable Print Format.
* Finalize Print Format.
* Version history required.

---

### DD-005: Store generated output snapshots in version history

**Decision**

Each save creates a generated output snapshot.

**Reason**

Version history output snapshot is required.

**Linked requirements**

* Version history must include generated output snapshots.

---

### DD-006: Administrator-confirmed similarity only

**Decision**

Do not implement automated similarity measurement.

**Reason**

Stakeholder confirmed administrator visual confirmation is acceptable.

**Linked requirements**

* 90% similarity administrator-confirmed.
* Automated similarity measurement not required.

---

### DD-007: Use server-side finalization rule engine

**Decision**

Finalization validation is centralized in `FinalizationService` and `ValidationService`.

**Reason**

Business rules must not be scattered across UI components.

**Linked requirements**

* Missing fields block finalization.
* Overlapping blocks block finalization.
* Blank spacer blocks not allowed.
* Invalid branding files block finalization.
* Unconfirmed OCR blocks finalization.

---

### DD-008: Use PDF.js for browser PDF rendering

**Decision**

Display the single-page PDF reference using PDF.js in the browser.

**Reason**

It provides reliable PDF page display without server-side image rendering for every view.

**Linked requirements**

* Display PDF as visual reference.
* Manual block drawing over reference.

---

### DD-009: Use layout helper library for canvas editing

**Decision**

Use a canvas/SVG helper library such as Konva.js or Fabric.js.

**Reason**

Drag, resize, align, duplicate, and delete operations are core UI requirements.

**Linked requirements**

* Editable layout blocks.
* Manual recreation.

---

### DD-010: Keep OCR assistive and non-blocking for manual layout

**Decision**

OCR failure does not block manual recreation, but unconfirmed OCR text blocks finalization if used.

**Reason**

OCR is assistive only.

**Linked requirements**

* OCR must be confirmed before use.
* OCR failure does not block manual recreation.

---

### Clean Code and GoF Design Review

#### Modules needing separation of responsibility

These modules must remain separate:

1. **UI builder logic** from **finalization validation**.
2. **OCR provider integration** from **OCR confirmation rules**.
3. **PDF validation** from **layout block validation**.
4. **Output generation** from **preview rendering**.
5. **File type validation** from **branding UI selection**.
6. **Version snapshot creation** from **normal save persistence**.
7. **Authentication/authorization** from business validation.

#### Business rules that must not be placed in UI components

The following must be enforced server-side:

* Administrator-only access.
* Single-page PDF validation.
* Required field mapping validation.
* OCR confirmation requirement.
* Branding file type restrictions.
* WEBP and PDF branding asset rejection.
* Blank spacer block rejection.
* Overlap finalization blocking.
* Similarity confirmation requirement.
* Final output generation validity.
* One active reusable Print Format for MVP.

UI components may show these rules but must not be the only enforcement layer.

#### Useful GoF patterns

| Pattern                 | Use                                                      | Reason                                                               |
| ----------------------- | -------------------------------------------------------- | -------------------------------------------------------------------- |
| Strategy                | Output generation strategies for preview vs final output | Preview and final output share layout logic but differ in strictness |
| Adapter                 | Google Vision OCR client                                 | Isolates external OCR provider from domain logic                     |
| Factory Method          | Block creation by block type                             | Avoids scattered block initialization logic                          |
| Composite               | Rendering a page from multiple block objects             | A print page is composed of many renderable blocks                   |
| Chain of Responsibility | Finalization validation rules                            | Allows each validation rule to run independently and report issues   |

#### Patterns that are unnecessary for MVP

| Pattern          | Reason                                                                          |
| ---------------- | ------------------------------------------------------------------------------- |
| Abstract Factory | Only one product family is needed                                               |
| Visitor          | Block operations are not complex enough yet                                     |
| Mediator         | UI interactions can be managed without heavy indirection                        |
| Observer         | Frappe/JS event handling is sufficient                                          |
| Command          | Undo/redo is not required                                                       |
| Memento          | Rollback is out of scope                                                        |
| Singleton        | Frappe document constraints are better than application-level singleton objects |

#### Where over-engineering should be avoided

Avoid:

* Building automated visual similarity measurement.
* Building a full workflow engine.
* Building multi-template support.
* Building rollback infrastructure.
* Building a separate SPA frontend.
* Building separate authentication.
* Building a separate template language.
* Supporting multiple OCR providers before required.
* Supporting multi-page PDF layouts before approved.

---

## 19. Design Risks

| Risk                                                       | Impact                                              | Mitigation                                                                                                         |
| ---------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Exact required warning-letter fields are not listed        | Finalization rules may be incomplete                | Use configurable required-field child table and confirm field list before implementation                           |
| Frappe Print Format rendering differs from builder preview | Output may not match expected copy-ready behavior   | Generate output using Frappe-compatible HTML/CSS/Jinja and test in Frappe Print Format editor during testing stage |
| SVG branding files may contain unsafe content              | Security risk                                       | Sanitize SVG or restrict SVG rendering behavior                                                                    |
| Manual visual similarity is subjective                     | Administrator may confirm inconsistent quality      | Store confirmer and timestamp; show clear non-pixel-perfect notice                                                 |
| Google Vision OCR failure                                  | OCR assistance unavailable                          | Allow manual text entry and treat OCR as assistive                                                                 |
| Canvas coordinate scaling mismatch                         | Preview/output layout may shift                     | Store normalized page coordinates and use consistent page dimensions                                               |
| Overlap detection edge cases                               | Valid designs may be blocked or invalid ones missed | Define precise rectangle intersection rules and allow administrator to adjust blocks                               |
| Version snapshots may become large                         | Database growth                                     | Snapshot only on save/finalization and avoid storing binary data                                                   |
| Existing branding files may have inconsistent permissions  | Asset selection may fail                            | Validate file access during selection and finalization                                                             |
| One-template MVP may later need multiple templates         | Future data model expansion needed                  | Use one active setup constraint rather than hardcoding singleton-only logic                                        |

---

## 20. Stage Gate Checklist

| Checklist item                                                | Status   |
| ------------------------------------------------------------- | -------- |
| Architecture is defined                                       | Complete |
| Modules are defined                                           | Complete |
| Data model is defined                                         | Complete |
| API design is defined                                         | Complete |
| UI screens are defined                                        | Complete |
| Validation and error handling are defined                     | Complete |
| Authentication design is defined                              | Complete |
| Authorization design is defined                               | Complete |
| Security considerations are defined                           | Complete |
| Performance considerations are defined                        | Complete |
| File/folder structure is defined                              | Complete |
| External integrations are defined                             | Complete |
| Design decisions are linked to requirements or analysis items | Complete |
| Clean Code and GoF Design Review is included                  | Complete |
| Design risks are documented                                   | Complete |
| Production code avoided                                       | Complete |
| Implementation tasks avoided                                  | Complete |

### Confirmed information

The design is ready for Stage 4 Implementation Planning once the project accepts:

* Native Frappe 14 stack.
* Custom administrator role.
* Configurable required warning-letter fields.
* Proposed DocType structure.

### Assumptions to confirm before implementation planning

1. Target DocType exact name.
2. Exact required warning-letter field list.
3. Whether SVG sanitization should allow SVG files directly or convert them to safe image rendering.

### Open questions

1. Should access be limited only to built-in `Administrator`, or is the custom role acceptable?
2. Are there any required warning-letter fields that must appear more than once in the output?
3. Should finalized setup be editable again, or should edits require explicitly returning the setup to `Editing` status?