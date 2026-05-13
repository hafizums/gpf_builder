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


