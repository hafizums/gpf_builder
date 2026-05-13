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


