# Requirements Document

## 1. Project Overview

**Project Name:** Frappe 14 PDF Reference to Print Format Builder for Warning Letters

**Project Stage:** Requirements Gathering

**Project Type:** Custom Frappe 14 app

This project will provide an administrator-only tool that allows a single-page warning letter PDF to be uploaded as a permanent visual reference. The administrator will manually recreate the document layout using editable blocks, map blocks to selectable fields from the Warning Letter / Outstanding Invoice Notice DocType, preview the recreated format against the original PDF reference, and generate a reusable Frappe Print Format that is ready to copy and paste into Frappe Print Format.

The MVP includes Google Vision OCR as an assistive feature, but OCR output must still be confirmed by the administrator. The system must not promise automatic or pixel-perfect PDF conversion. The minimum acceptable preview similarity is **90% compared with the reference document**.

---

## 2. Problem Statement

Administrators need a controlled way to recreate an existing warning letter PDF layout inside Frappe Print Format without manually writing the entire print format from scratch.

The current challenge is that warning letter PDFs may be scanned, image-based, or visually complex. Automatic conversion may not be reliable. The software must therefore support a visual reference workflow where the administrator recreates the layout manually, assisted by OCR and visual comparison, while keeping the final output usable in Frappe Print Format.

---

## 3. Target Users

### Confirmed Users

The app is intended for:

1. **Administrator only**

No other user group is included in the MVP.

---

## 4. User Roles

### Confirmed Role

| Role          | Description                                                                                                                                                                                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Administrator | The only user allowed to upload PDF references, create reusable Print Formats, edit reusable Print Formats, approve finished warning letter formats, manage layout blocks, select fields, preview output, and generate the final reusable Print Format. |

### Excluded Roles

The MVP does not include separate roles for:

1. Template Creator
2. Template Editor
3. Template Approver
4. Business User
5. Reviewer
6. Multi-level approval user

---

## 5. Core Features

The MVP shall include the following core features:

1. Administrator-only access.
2. Single-page PDF warning letter upload.
3. Permanent storage of the uploaded PDF reference.
4. Manual block drawing over the PDF reference.
5. Editable blocks with resize, drag, align, duplicate, and delete actions.
6. Field selection from the Warning Letter / Outstanding Invoice Notice DocType.
7. Multilingual text support.
8. Google Vision OCR assistive text recognition.
9. Auto-generated sample data for preview.
10. Side-by-side comparison between preview and PDF reference.
11. 90% minimum preview similarity target.
12. Existing file selection for logos, signatures, and footer branding.
13. One saved reusable Print Format.
14. Autonaming for the saved Print Format.
15. Version history for saved Print Format changes.
16. Final Print Format output ready to copy and paste into Frappe Print Format.

---

## 6. Functional Requirements

### 6.1 Administrator Access

FR-001: The system shall allow access only to the Administrator.

FR-002: The Administrator shall be the only user allowed to upload PDF references.

FR-003: The Administrator shall be the only user allowed to create reusable Print Formats.

FR-004: The Administrator shall be the only user allowed to edit reusable Print Formats.

FR-005: The Administrator shall be the only user allowed to approve or finalize a warning letter Print Format.

---

### 6.2 PDF Reference Upload

FR-006: The system shall allow the Administrator to upload one single-page warning letter PDF.

FR-007: The system shall store the uploaded PDF permanently.

FR-008: The uploaded PDF shall be used as a visual reference for layout recreation.

FR-009: The system shall not treat the uploaded PDF as a guaranteed automatic conversion source.

FR-010: The MVP shall reject or prevent multi-page PDF usage.

FR-011: The MVP shall support only the warning letter page.

FR-012: The MVP shall not support Lampiran pages or invoice attachment pages.

---

### 6.3 Manual Layout Block Creation

FR-013: The system shall allow the Administrator to manually draw layout blocks over the PDF reference.

FR-014: The system shall allow layout blocks to be moved by dragging.

FR-015: The system shall allow layout blocks to be resized.

FR-016: The system shall allow layout blocks to be aligned.

FR-017: The system shall allow layout blocks to be duplicated.

FR-018: The system shall allow layout blocks to be deleted.

FR-019: The system shall allow blocks to represent static text, dynamic fields, images, or branding elements.

---

### 6.4 Field Selection and Mapping

FR-020: The system shall allow the Administrator to select fields from the Warning Letter / Outstanding Invoice Notice DocType.

FR-021: The system shall allow selected fields to be mapped to dynamic layout blocks.

FR-022: The system shall support user-selected field types from the available DocType fields.

FR-023: The system shall distinguish static text blocks from dynamic field blocks.

FR-024: The system shall prevent finalization where required mapped blocks are incomplete.

---

### 6.5 Multilingual Text

FR-025: The system shall support multilingual text in layout blocks.

FR-026: The system shall support multilingual text in OCR-assisted content where supported by Google Vision.

FR-027: The system shall allow the Administrator to review and correct multilingual text before saving.

---

### 6.6 OCR Assistance Using Google Vision

FR-028: The MVP shall include OCR assistance using Google Vision.

FR-029: OCR shall be used to assist text recognition from the uploaded PDF reference.

FR-030: OCR output shall not be treated as automatically correct.

FR-031: The Administrator shall be able to review OCR output.

FR-032: The Administrator shall confirm or edit OCR output before using it in the final layout.

FR-033: OCR shall not be required to recreate the full layout automatically.

---

### 6.7 Image and Branding Selection

FR-034: The system shall allow logos to be selected from existing files.

FR-035: The system shall allow signatures to be selected from existing files.

FR-036: The system shall allow footer branding to be selected from existing files.

FR-037: The MVP shall not require new image upload for logos, signatures, or footer branding unless selected from existing files.

---

### 6.8 Preview

FR-038: The system shall auto-generate sample data for preview.

FR-039: The system shall allow the Administrator to preview the recreated warning letter using auto-generated sample data.

FR-040: The system shall display the preview side-by-side with the original PDF reference.

FR-041: The preview shall include static text, multilingual text, selected images, branding elements, and mapped dynamic fields.

FR-042: The preview shall target at least 90% visual similarity compared with the reference document.

FR-043: The system shall clearly communicate that the 90% similarity target does not mean pixel-perfect PDF conversion.

---

### 6.9 Save as Reusable Frappe Print Format

FR-044: The system shall support one saved reusable Print Format in the MVP.

FR-045: The saved Print Format shall use autonaming.

FR-046: The system shall generate Print Format output that is ready to copy and paste into Frappe Print Format.

FR-047: The saved Print Format shall be reusable for the warning letter use case.

FR-048: The MVP shall not support multiple saved formats.

---

### 6.10 Version History

FR-049: The system shall maintain version history for saved Print Format changes.

FR-050: Version history shall record changes made by the Administrator.

FR-051: Version history shall support traceability of modifications to the saved Print Format.

---

## 7. Business Rules

BR-001: Only the Administrator may use the app.

BR-002: Only one PDF page is supported in the MVP.

BR-003: Only the warning letter page is supported in the MVP.

BR-004: The uploaded PDF reference shall be stored permanently.

BR-005: The Administrator must manually draw layout blocks over the reference PDF.

BR-006: Blocks must support resize, drag, align, duplicate, and delete.

BR-007: Field mapping must use fields selected by the Administrator from the relevant DocType.

BR-008: Multilingual text is required.

BR-009: OCR is included in the MVP using Google Vision.

BR-010: OCR output must be reviewed and confirmed by the Administrator.

BR-011: Sample data shall be auto-generated.

BR-012: Preview comparison shall be side-by-side with the PDF reference.

BR-013: Minimum acceptable preview similarity is 90%.

BR-014: Logos, signatures, and footer branding shall be selected from existing files.

BR-015: The MVP shall support only one saved reusable Print Format.

BR-016: Saved Print Format naming shall use autonaming.

BR-017: Version history is required.

BR-018: Draft, review, and approved workflow states are not required.

BR-019: The final generated Print Format must be ready to copy and paste into Frappe Print Format.

BR-020: The MVP shall not promise automatic or pixel-perfect PDF conversion.

---

## 8. Data Requirements

### 8.1 PDF Reference Data

DR-001: The system shall store the uploaded single-page PDF reference permanently.

DR-002: The stored PDF reference shall be associated with the saved Print Format setup.

DR-003: The system shall retain enough metadata to identify the uploaded reference document.

---

### 8.2 Layout Block Data

DR-004: The system shall store layout block information.

Each layout block shall require, at minimum:

1. Block identifier
2. Block type
3. Position
4. Size
5. Alignment
6. Content value or field mapping
7. Static or dynamic classification
8. Multilingual text content, where applicable
9. Image reference, where applicable

---

### 8.3 Field Mapping Data

DR-005: The system shall store mappings between layout blocks and selected DocType fields.

DR-006: The system shall allow the Administrator to select fields from the available DocType field list.

DR-007: The system shall store whether a block uses static content, dynamic field content, OCR-assisted content, or selected existing file content.

---

### 8.4 OCR Data

DR-008: The system shall store OCR-assisted text only after Administrator review or confirmation.

DR-009: OCR output shall be distinguishable from manually entered text before confirmation.

---

### 8.5 Preview Data

DR-010: The system shall generate sample data automatically.

DR-011: Sample data shall be used for preview purposes only unless otherwise confirmed later.

---

### 8.6 Print Format Data

DR-012: The system shall store one reusable Print Format configuration.

DR-013: The saved Print Format shall use autonaming.

DR-014: The system shall store version history for Print Format changes.

DR-015: The system shall generate final output suitable for copy and paste into Frappe Print Format.

---

## 9. Permission Requirements

PR-001: Only the Administrator may access the app.

PR-002: Only the Administrator may upload PDF references.

PR-003: Only the Administrator may create reusable Print Formats.

PR-004: Only the Administrator may edit reusable Print Formats.

PR-005: Only the Administrator may approve or finalize the warning letter Print Format.

PR-006: Only the Administrator may select fields for mapping.

PR-007: Only the Administrator may select logos, signatures, and footer branding from existing files.

PR-008: Only the Administrator may view and manage version history.

No separate reviewer, editor, creator, or approver permissions are required in the MVP.

---

## 10. Integration Requirements

IR-001: The system shall run as a custom app in Frappe 14.

IR-002: The system shall integrate with Frappe Print Format functionality.

IR-003: The system shall access selectable fields from the Warning Letter / Outstanding Invoice Notice DocType.

IR-004: The system shall integrate with existing Frappe file records for selecting logos, signatures, and footer branding.

IR-005: The system shall integrate with Google Vision for OCR assistance.

IR-006: The system shall generate output that can be copied and pasted into Frappe Print Format.

IR-007: The MVP shall not integrate with batch generation workflows.

IR-008: The MVP shall not integrate with invoice attachment generation.

IR-009: The MVP shall not support multi-page PDF processing.

---

## 11. UI/UX Requirements

UI-001: The interface shall be available to the Administrator only.

UI-002: The interface shall provide a PDF upload area for one single-page warning letter PDF.

UI-003: The interface shall display the uploaded PDF reference.

UI-004: The interface shall allow the Administrator to manually draw layout blocks over the PDF reference.

UI-005: The interface shall allow blocks to be dragged, resized, aligned, duplicated, and deleted.

UI-006: The interface shall provide field selection from the Warning Letter / Outstanding Invoice Notice DocType.

UI-007: The interface shall support multilingual text entry and correction.

UI-008: The interface shall show OCR-assisted text extracted using Google Vision.

UI-009: The interface shall require Administrator review of OCR output.

UI-010: The interface shall allow logos, signatures, and footer branding to be selected from existing files.

UI-011: The interface shall provide a side-by-side comparison of the PDF reference and generated preview.

UI-012: The interface shall display preview output using auto-generated sample data.

UI-013: The interface shall clearly indicate whether the preview reaches the required 90% similarity target.

UI-014: The interface shall provide a final generated Print Format output area ready for copy and paste into Frappe Print Format.

UI-015: The interface shall show version history for saved Print Format changes.

---

## 12. Non-Functional Requirements

NFR-001: The system shall operate within the Frappe 14 environment.

NFR-002: The system shall restrict access to Administrator only.

NFR-003: The system shall support permanent storage of uploaded PDF references.

NFR-004: The system shall support multilingual content.

NFR-005: The system shall provide reliable manual layout editing behavior.

NFR-006: The system shall clearly communicate that OCR is assistive and may require correction.

NFR-007: The system shall target 90% visual similarity between preview and reference document.

NFR-008: The system shall not guarantee pixel-perfect conversion.

NFR-009: The system shall maintain version history for saved Print Format changes.

NFR-010: The system shall keep MVP scope limited to one warning letter format.

NFR-011: The system shall prevent scope creep into multi-page PDF conversion, batch generation, or invoice attachment generation.

NFR-012: The generated output shall be clear enough for an Administrator to copy and paste into Frappe Print Format.

---

## 13. Out of Scope

The following items are out of scope for the MVP:

1. Non-administrator access.
2. Multi-user workflow.
3. Draft, review, and approved workflow states.
4. Multi-page PDF support.
5. Lampiran pages.
6. Invoice attachment pages.
7. Batch generation.
8. Multiple saved Print Formats.
9. Automatic pixel-perfect PDF conversion.
10. Fully automatic layout reconstruction.
11. Use of OCR output without Administrator confirmation.
12. New upload workflow for logos, signatures, and footer branding.
13. Database schema design.
14. System architecture design.
15. Implementation code.
16. Testing plan.
17. Deployment plan.
18. Maintenance plan.

---

## 14. Assumptions

A-001: The Warning Letter / Outstanding Invoice Notice DocType already exists or will be defined before later Waterfall stages.

A-002: The Administrator has permission in Frappe to access existing files for logos, signatures, and footer branding.

A-003: Google Vision OCR access will be available for the Frappe environment.

A-004: The 90% preview similarity target will be assessed visually or by a method to be defined in later stages.

A-005: “Ready to use in Frappe Print Format” means the generated output can be copied and pasted into Frappe’s Print Format editor by the Administrator.

A-006: Version history means tracking changes to the saved Print Format configuration, not necessarily restoring full previous versions unless later confirmed.

A-007: Autonaming rules will be defined during later analysis, but the requirement is confirmed at the business level.

---

## 15. Acceptance Criteria

AC-001: The app is accessible only to the Administrator.

AC-002: The Administrator can upload one single-page warning letter PDF.

AC-003: The uploaded PDF is stored permanently.

AC-004: The uploaded PDF is displayed as a visual reference.

AC-005: The Administrator can manually draw layout blocks over the PDF reference.

AC-006: The Administrator can resize layout blocks.

AC-007: The Administrator can drag layout blocks.

AC-008: The Administrator can align layout blocks.

AC-009: The Administrator can duplicate layout blocks.

AC-010: The Administrator can delete layout blocks.

AC-011: The Administrator can select fields from the Warning Letter / Outstanding Invoice Notice DocType.

AC-012: The Administrator can map selected fields to dynamic blocks.

AC-013: The system supports multilingual text.

AC-014: Google Vision OCR is available as an assistive feature.

AC-015: OCR output requires Administrator review or confirmation.

AC-016: Sample data is auto-generated for preview.

AC-017: The Administrator can preview the generated warning letter.

AC-018: The Administrator can compare the preview side-by-side with the uploaded PDF reference.

AC-019: The preview reaches the required 90% similarity target, subject to the approved measurement method.

AC-020: Logos, signatures, and footer branding can be selected from existing files.

AC-021: The MVP supports one saved reusable Print Format.

AC-022: The saved Print Format uses autonaming.

AC-023: Version history is maintained for saved Print Format changes.

AC-024: The final generated Print Format output is ready to copy and paste into Frappe Print Format.

AC-025: The MVP does not support multi-page PDFs.

AC-026: The MVP does not support Lampiran pages.

AC-027: The MVP does not support invoice attachment pages.

AC-028: The MVP does not support batch generation.

AC-029: The MVP does not promise automatic or pixel-perfect PDF conversion.

---

## 16. Open Questions

All previously listed open questions have now been answered at the requirements level.

Remaining clarification items for later Waterfall stages:

1. How will the 90% similarity target be measured or verified?
2. What exact fields exist in the Warning Letter / Outstanding Invoice Notice DocType?
3. What exact autonaming format should be used?
4. What level of version history detail is required?
5. Which Google Vision OCR languages must be enabled for multilingual support?
6. What file types are allowed for logos, signatures, and footer branding from existing files?

---

## 17. Stage Gate Checklist

| Checklist Item                            | Status                                                              |
| ----------------------------------------- | ------------------------------------------------------------------- |
| Project goal is clear                     | Complete                                                            |
| User roles are identified                 | Complete — Administrator only                                       |
| Core features are listed                  | Complete                                                            |
| Business rules are captured               | Complete                                                            |
| Acceptance criteria are defined           | Complete                                                            |
| Open questions are resolved or documented | Complete at requirements level; remaining clarifications documented |

