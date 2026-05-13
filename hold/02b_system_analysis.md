# System Analysis Document

## 1. Requirements Summary

The remaining System Analysis gaps have now been clarified by the stakeholder.

The project remains an **Administrator-only Frappe 14 custom app** for converting a single-page warning letter PDF reference into a reusable Frappe Print Format through manual layout block recreation, OCR assistance, preview comparison, and final copy-ready output.

The following decisions are now confirmed:

| Topic                            | Confirmed Decision                                                                     |
| -------------------------------- | -------------------------------------------------------------------------------------- |
| Administrator access             | Administrator access is confirmed; exact role mapping will be handled in System Design |
| Required DocType fields          | All fields required for the warning letter must be available                           |
| Mandatory finalization fields    | All fields required for the warning letter are mandatory for finalization              |
| 90% similarity                   | Administrator-confirmed visual similarity is acceptable                                |
| Automated similarity measurement | Not required                                                                           |
| Autonaming format                | `GPF-YYYYMMDD-###`                                                                     |
| OCR languages                    | English and Malay are sufficient for MVP                                               |
| Branding file types              | PNG, JPG, JPEG, SVG                                                                    |
| WEBP support                     | Not allowed                                                                            |
| PDF branding assets              | Not allowed                                                                            |
| Version history output snapshot  | Required                                                                               |
| Rollback                         | Out of scope                                                                           |
| Overlapping blocks               | Should block finalization                                                              |
| Blank spacer blocks              | Not allowed                                                                            |
| Copy-ready output guarantee      | Output can be copied into Frappe built-in Print Format and works                       |

---

## 2. Current Problem Analysis

The original problem remains unchanged: Administrators need a controlled way to recreate an existing single-page warning letter PDF as a usable Frappe Print Format without writing the entire format manually.

The clarified decisions reduce uncertainty in these areas:

1. Finalization can now enforce all warning-letter-required fields.
2. Similarity checking can rely on Administrator visual confirmation.
3. No automated similarity engine is needed.
4. Branding asset rules are now strict.
5. Version history must include generated output snapshots.
6. Final output must work when pasted into Frappe’s built-in Print Format editor.
7. Overlapping blocks are no longer only warnings; they must block finalization.
8. Blank spacer blocks are not allowed.

---

## 3. Proposed System Behavior

The system should allow the Administrator to upload one single-page warning letter PDF, manually recreate the layout using editable blocks, map all required warning letter fields, preview the output, confirm 90% visual similarity, save the reusable Print Format, and generate copy-ready output.

The final output must be valid enough that the Administrator can copy and paste it into Frappe’s built-in Print Format and it works.

The system should not include automated similarity measurement, rollback, WEBP branding files, PDF branding files, blank spacer blocks, or finalization with overlapping blocks.

---

## 4. User Roles and Responsibilities

## Confirmed Role

### Administrator

The Administrator is the only user allowed to use the system.

The stakeholder confirmed Administrator-only access, but the exact technical role mapping remains a System Design decision.

Possible System Design interpretations:

1. Built-in Frappe Administrator user.
2. System Manager role.
3. Custom Administrator role.

### Administrator Responsibilities

1. Upload the single-page warning letter PDF.
2. Manually create layout blocks.
3. Configure static, dynamic, image, and branding blocks.
4. Select all fields required for the warning letter.
5. Confirm OCR text before use.
6. Preview the warning letter.
7. Confirm the 90% similarity target visually.
8. Resolve overlapping blocks before finalization.
9. Save the reusable Print Format.
10. Generate final copy-ready output.
11. Copy and paste the generated output into Frappe built-in Print Format.
12. Review version history, including generated output snapshots.

---

## 5. User Workflows

## Workflow 1: Administrator Access

1. Administrator opens the app.
2. System checks Administrator access.
3. If valid, the system displays the layout builder.
4. If invalid, access is denied.

### Outcome

Only Administrator users can access the app.

---

## Workflow 2: Upload Single-Page PDF Reference

1. Administrator selects a PDF file.
2. System validates that the file is a PDF.
3. System validates that the PDF contains exactly one page.
4. System stores the PDF permanently.
5. System displays the PDF as the visual reference.

### Outcome

The uploaded PDF becomes the permanent warning letter reference.

---

## Workflow 3: Create and Edit Layout Blocks

1. Administrator draws blocks over the PDF reference.
2. Administrator assigns each block type:

   * Static text.
   * Dynamic field.
   * Image.
   * Branding element.
3. Administrator drags, resizes, aligns, duplicates, or deletes blocks.
4. System stores block configuration.

### Confirmed Rule

Overlapping blocks must block finalization.

### Outcome

The warning letter layout is manually recreated using editable blocks.

---

## Workflow 4: Configure Required Warning Letter Fields

1. Administrator creates or selects a dynamic field block.
2. System displays fields from the Warning Letter / Outstanding Invoice Notice DocType.
3. Administrator maps all fields required for the warning letter.
4. System stores field mappings.

### Confirmed Rule

All fields required for the warning letter are mandatory for finalization.

### Outcome

The Print Format has complete required warning letter field mapping.

---

## Workflow 5: OCR Assistance

1. Administrator requests OCR assistance.
2. System uses Google Vision OCR.
3. OCR supports English and Malay for MVP.
4. System displays OCR output as unconfirmed.
5. Administrator reviews, edits, and confirms OCR text.
6. Confirmed OCR text can be used in layout blocks.

### Confirmed Rule

OCR is assistive only and must not bypass Administrator confirmation.

---

## Workflow 6: Branding Asset Selection

1. Administrator creates or selects logo, signature, or footer branding block.
2. System displays existing files.
3. Administrator selects an existing PNG, JPG, JPEG, or SVG file.
4. System stores the selected file reference.

### Confirmed Rules

1. WEBP is not allowed.
2. PDF files are not allowed as branding assets.
3. Branding files must come from existing files.

---

## Workflow 7: Preview and Similarity Confirmation

1. System generates sample data.
2. System renders the recreated warning letter preview.
3. System displays preview side-by-side with the PDF reference.
4. Administrator visually compares the preview with the reference.
5. Administrator confirms whether the preview reaches the 90% similarity target.

### Confirmed Rules

1. Administrator-confirmed visual similarity is acceptable.
2. Automated similarity measurement is not required.
3. Pixel-perfect conversion is not promised.

---

## Workflow 8: Save Reusable Print Format

1. Administrator selects Save.
2. System creates or updates the single reusable Print Format configuration.
3. System applies autonaming using `GPF-YYYYMMDD-###`.
4. System records version history.
5. System stores a generated output snapshot in version history.

### Outcome

The reusable Print Format is saved and traceable.

---

## Workflow 9: Finalize Print Format

1. Administrator selects Finalize.
2. System validates:

   * PDF reference exists.
   * All warning-letter-required fields are mapped.
   * OCR content used in layout is confirmed.
   * Branding assets are valid file types.
   * No WEBP branding assets are used.
   * No PDF branding assets are used.
   * No blank spacer blocks exist.
   * No overlapping blocks exist.
   * Preview has been generated.
   * Administrator has confirmed 90% similarity.
3. If validation passes, the Print Format is finalized.
4. If validation fails, the system blocks finalization.

### Outcome

Only a complete, valid, non-overlapping, copy-ready format can be finalized.

---

## Workflow 10: Generate Copy-Ready Output

1. Administrator requests final output.
2. System generates the Print Format output.
3. System displays the output in a copy-ready area.
4. Administrator copies the output.
5. Administrator pastes it into Frappe built-in Print Format.
6. The pasted output works in Frappe Print Format.

### Confirmed Guarantee

“Ready to copy and paste into Frappe Print Format” means:

> The generated output can be copied into Frappe’s built-in Print Format editor and works.

---

## Workflow 11: View Version History

1. Administrator opens version history.
2. System displays saved versions.
3. Each version includes:

   * Version number.
   * Timestamp.
   * Administrator identity.
   * Change summary.
   * Changed block details.
   * Changed field mappings.
   * Changed branding file references.
   * OCR confirmation changes.
   * Generated output snapshot.

### Confirmed Rule

Rollback is out of scope.

---

## 6. Use Cases

## UC-001: Access the App

### Actor

Administrator.

### Goal

Access the warning letter Print Format builder.

### Main Flow

1. Administrator opens the app.
2. System validates Administrator access.
3. System displays the builder.

### Failure Flow

Unauthorized users are denied access.

---

## UC-002: Upload PDF Reference

### Actor

Administrator.

### Goal

Upload a single-page warning letter PDF.

### Main Flow

1. Administrator selects PDF.
2. System validates file type.
3. System validates single-page PDF.
4. System stores PDF permanently.
5. System displays PDF reference.

### Failure Flow

Invalid, corrupted, protected, or multi-page PDFs are rejected.

---

## UC-003: Create Layout Blocks

### Actor

Administrator.

### Goal

Recreate the warning letter layout manually.

### Main Flow

1. Administrator draws block.
2. Administrator assigns block type.
3. Administrator configures block.
4. System stores block data.

### Failure Flow

Invalid blocks are flagged.

---

## UC-004: Edit Layout Blocks

### Actor

Administrator.

### Goal

Adjust block layout.

### Main Flow

1. Administrator selects block.
2. Administrator drags, resizes, aligns, duplicates, or deletes block.
3. System updates layout.

### Failure Flow

If blocks overlap, system must block finalization.

---

## UC-005: Map Required Warning Letter Fields

### Actor

Administrator.

### Goal

Map all fields required for the warning letter.

### Main Flow

1. Administrator selects dynamic block.
2. System displays DocType fields.
3. Administrator selects required field.
4. System stores mapping.

### Failure Flow

Missing required warning letter fields block finalization.

---

## UC-006: Use OCR Assistance

### Actor

Administrator.

### Goal

Use OCR to assist text recognition.

### Main Flow

1. Administrator requests OCR.
2. System uses Google Vision OCR.
3. System displays OCR output.
4. Administrator reviews and confirms text.

### Failure Flow

OCR failure does not block manual recreation.

---

## UC-007: Select Branding Assets

### Actor

Administrator.

### Goal

Select logo, signature, or footer branding.

### Main Flow

1. Administrator selects branding block.
2. System displays existing files.
3. Administrator selects PNG, JPG, JPEG, or SVG.
4. System stores file reference.

### Failure Flow

WEBP, PDF, missing, inaccessible, or unsupported files are rejected or block finalization.

---

## UC-008: Preview Warning Letter

### Actor

Administrator.

### Goal

Preview recreated warning letter.

### Main Flow

1. System generates sample data.
2. System renders preview.
3. System displays preview beside PDF reference.
4. Administrator confirms 90% similarity visually.

### Failure Flow

If similarity is not confirmed, finalization is blocked.

---

## UC-009: Save Reusable Print Format

### Actor

Administrator.

### Goal

Save reusable Print Format configuration.

### Main Flow

1. Administrator saves configuration.
2. System creates or updates one reusable format.
3. System applies autonaming: `GPF-YYYYMMDD-###`.
4. System records version history.
5. System stores generated output snapshot.

### Failure Flow

Save failure or version history failure is reported.

---

## UC-010: Finalize Print Format

### Actor

Administrator.

### Goal

Validate the format for final use.

### Main Flow

1. Administrator selects Finalize.
2. System validates all finalization rules.
3. System blocks finalization if any validation fails.
4. System finalizes the format if validation passes.

### Failure Flow

Finalization is blocked for missing fields, overlapping blocks, blank spacer blocks, invalid branding files, unconfirmed OCR, or unconfirmed similarity.

---

## UC-011: Generate Final Output

### Actor

Administrator.

### Goal

Generate copy-ready Frappe Print Format output.

### Main Flow

1. Administrator generates output.
2. System displays copy-ready output.
3. Administrator copies output into Frappe built-in Print Format.
4. Output works in Frappe Print Format.

### Failure Flow

If output cannot work after copy/paste, the system must treat this as an output generation failure.

---

## UC-012: View Version History

### Actor

Administrator.

### Goal

Trace saved changes.

### Main Flow

1. Administrator opens version history.
2. System displays saved version records.
3. System includes generated output snapshot.

### Failure Flow

Rollback is not available.

---

## 7. Data Flow

## Data Flow 1: PDF Upload

1. Administrator uploads PDF.
2. System validates single-page PDF.
3. System stores PDF permanently.
4. System links PDF to the Print Format setup.

### Data

1. PDF file.
2. File metadata.
3. Page count.
4. Storage reference.
5. Print Format setup reference.

---

## Data Flow 2: Layout Blocks

1. Administrator creates or edits blocks.
2. System stores block type, position, size, alignment, and content.
3. System validates overlap before finalization.

### Data

1. Block ID.
2. Block type.
3. Position.
4. Size.
5. Alignment.
6. Content.
7. Field mapping.
8. Image reference.

---

## Data Flow 3: Field Mapping

1. System provides Warning Letter / Outstanding Invoice Notice DocType fields.
2. Administrator maps fields required for the warning letter.
3. System stores mappings.
4. Finalization checks all required fields are mapped.

### Data

1. DocType field list.
2. Required warning letter field list.
3. Selected fields.
4. Block mappings.
5. Mapping status.

---

## Data Flow 4: OCR

1. System sends PDF reference to Google Vision OCR.
2. OCR returns English or Malay text.
3. System marks OCR output as unconfirmed.
4. Administrator confirms or edits text.
5. System stores confirmed OCR text.

### Data

1. Raw OCR output.
2. Edited OCR output.
3. Confirmation status.
4. Confirmed text.
5. Associated block.

---

## Data Flow 5: Branding Files

1. System displays existing files.
2. Administrator selects PNG, JPG, JPEG, or SVG.
3. System stores file reference.
4. System rejects or blocks WEBP and PDF branding assets.

### Data

1. File reference.
2. File type.
3. Accessibility status.
4. Branding block reference.

---

## Data Flow 6: Preview

1. System generates sample data.
2. System renders preview.
3. Administrator confirms 90% similarity visually.
4. System stores similarity confirmation status.

### Data

1. Sample data.
2. Layout configuration.
3. Preview output.
4. Similarity confirmation.

---

## Data Flow 7: Save and Version History

1. Administrator saves configuration.
2. System applies autonaming.
3. System stores current configuration.
4. System records version history.
5. System stores generated output snapshot.

### Data

1. Format name: `GPF-YYYYMMDD-###`.
2. Version number.
3. Timestamp.
4. Administrator identity.
5. Change summary.
6. Configuration snapshot.
7. Generated output snapshot.

---

## Data Flow 8: Final Output

1. System reads finalized configuration.
2. System generates output.
3. Administrator copies output.
4. Administrator pastes into Frappe built-in Print Format.
5. Output works.

### Data

1. Finalized configuration.
2. Generated Print Format output.
3. Copy-ready output content.

---

## 8. Business Logic Analysis

## BL-001: Administrator-Only Access

Only Administrator users may use the app.

---

## BL-002: Single-Page PDF Only

Only one-page warning letter PDFs are allowed.

---

## BL-003: Manual Recreation Required

The Administrator must manually recreate the layout with blocks.

---

## BL-004: OCR Is Assistive Only

OCR output must be confirmed before use.

---

## BL-005: Required Warning Letter Fields

All fields required for the warning letter are mandatory for finalization.

---

## BL-006: 90% Similarity Confirmation

90% similarity is confirmed visually by the Administrator.

Automated similarity measurement is not required.

---

## BL-007: Autonaming

Saved Print Format name must follow:

`GPF-YYYYMMDD-###`

---

## BL-008: Branding File Types

Allowed:

1. PNG.
2. JPG.
3. JPEG.
4. SVG.

Not allowed:

1. WEBP.
2. PDF.
3. Other unsupported file types.

---

## BL-009: Version History

Version history must include generated output snapshots.

Rollback is out of scope.

---

## BL-010: Overlapping Blocks

Overlapping blocks must block finalization.

---

## BL-011: Blank Spacer Blocks

Blank spacer blocks are not allowed.

---

## BL-012: Final Output Guarantee

The generated output must be copyable into Frappe built-in Print Format and work there.

---

## 9. Permission and Access Analysis

| Action                 | Permission         |
| ---------------------- | ------------------ |
| Access app             | Administrator only |
| Upload PDF             | Administrator only |
| Create blocks          | Administrator only |
| Edit blocks            | Administrator only |
| Use OCR                | Administrator only |
| Confirm OCR            | Administrator only |
| Map fields             | Administrator only |
| Select branding assets | Administrator only |
| Preview                | Administrator only |
| Confirm similarity     | Administrator only |
| Save reusable format   | Administrator only |
| Finalize format        | Administrator only |
| Generate output        | Administrator only |
| View version history   | Administrator only |

### Remaining Design Detail

The exact Frappe role mapping remains for System Design.

---

## 10. Validation Rules

## PDF Validation

1. Must be PDF.
2. Must contain exactly one page.
3. Must be readable.
4. Must be stored permanently.
5. Must be displayable.

## Block Validation

1. Block must have valid type.
2. Block must have valid position.
3. Block must have valid size.
4. Block must not overlap another block at finalization.
5. Blank spacer blocks are not allowed.
6. Blocks must contain required content based on type.

## Field Mapping Validation

1. All fields required for the warning letter must be mapped.
2. Missing required mappings block finalization.
3. Invalid or removed fields block finalization.

## OCR Validation

1. OCR output starts as unconfirmed.
2. OCR output must be confirmed before finalization if used.
3. OCR supports English and Malay for MVP.

## Branding Validation

1. Branding assets must be existing files.
2. Allowed types: PNG, JPG, JPEG, SVG.
3. WEBP is not allowed.
4. PDF is not allowed.
5. Missing or inaccessible assets block finalization.

## Preview Validation

1. Preview must use sample data.
2. Preview must be displayed side-by-side with the PDF reference.
3. Administrator must confirm 90% visual similarity.
4. Automated similarity measurement is not required.

## Save Validation

1. Must use autonaming format `GPF-YYYYMMDD-###`.
2. Must create or update one reusable Print Format.
3. Must create version history.
4. Must include generated output snapshot in version history.

## Finalization Validation

Finalization is blocked if:

1. Required warning letter fields are not mapped.
2. OCR text is unconfirmed.
3. Branding file type is invalid.
4. Branding file is missing.
5. Blocks overlap.
6. Blank spacer blocks exist.
7. Preview has not been generated.
8. 90% visual similarity has not been confirmed.
9. Final output cannot be generated.

## Output Validation

1. Output must be copy-ready.
2. Output must work when pasted into Frappe built-in Print Format.

---

## 11. Edge Cases

1. Multi-page PDF uploaded.
2. Corrupted PDF uploaded.
3. PDF is password-protected.
4. PDF is scanned and OCR performs poorly.
5. OCR returns incorrect Malay or English text.
6. Required warning letter field is missing.
7. Required field is not mapped.
8. Branding file is WEBP.
9. Branding file is PDF.
10. Branding file is deleted after selection.
11. Branding file permission changes.
12. Blocks overlap.
13. Blank spacer block exists.
14. Preview is not generated.
15. Administrator does not confirm similarity.
16. Version history snapshot fails.
17. Generated output does not work in Frappe built-in Print Format.
18. Save creates duplicate name.
19. Administrator attempts rollback.
20. Administrator attempts to create more than one reusable format.

---

## 12. Failure Scenarios

## FS-001: Unauthorized User Access

System denies access.

## FS-002: Multi-Page PDF

System rejects the upload.

## FS-003: OCR Failure

System allows manual layout creation to continue.

## FS-004: Missing Required Warning Letter Field

System blocks finalization.

## FS-005: Invalid Branding File

System blocks finalization.

## FS-006: Overlapping Blocks

System blocks finalization.

## FS-007: Blank Spacer Block

System blocks finalization.

## FS-008: Similarity Not Confirmed

System blocks finalization.

## FS-009: Version History Snapshot Failure

System reports the issue because output snapshot is required.

## FS-010: Rollback Requested

System does not provide rollback because rollback is out of scope.

## FS-011: Final Output Does Not Work in Frappe Print Format

System treats this as output generation failure.

---

## 13. Constraints

1. Frappe 14 custom app.
2. Administrator-only access.
3. Single-page warning letter PDF only.
4. Manual block-based recreation.
5. Google Vision OCR assistive only.
6. English and Malay OCR support for MVP.
7. One reusable Print Format only.
8. Autonaming format: `GPF-YYYYMMDD-###`.
9. Branding files limited to PNG, JPG, JPEG, SVG.
10. WEBP not allowed.
11. PDF branding files not allowed.
12. Blank spacer blocks not allowed.
13. Overlapping blocks block finalization.
14. Version history must include generated output snapshots.
15. Rollback is out of scope.
16. Automated similarity measurement is not required.
17. Final output must work in Frappe built-in Print Format after copy/paste.
18. No database design in this stage.
19. No technical architecture in this stage.
20. No implementation code in this stage.

---

## 14. Dependencies

1. Frappe 14 environment.
2. Frappe built-in Print Format.
3. Warning Letter / Outstanding Invoice Notice DocType.
4. Required warning letter fields.
5. Existing file records for branding assets.
6. Google Vision OCR.
7. English and Malay OCR capability.
8. Administrator permission configuration.
9. Version history storage capability.
10. Generated output snapshot capability.

---

## 15. Risks

| Risk                                                     | Impact                                        | Mitigation                                                                          |
| -------------------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------- |
| Administrator role mapping remains broad                 | Permission ambiguity                          | Resolve during System Design                                                        |
| Required warning letter fields are not explicitly listed | Finalization rules may be unclear             | Define field list during System Design                                              |
| OCR errors                                               | Incorrect text                                | Require Administrator confirmation                                                  |
| Output does not work in Frappe Print Format              | MVP acceptance failure                        | Validate copy-paste output behavior during later stages                             |
| Overlap detection may block intentional designs          | Some layouts may need redesign                | Administrator must adjust blocks because overlap is confirmed to block finalization |
| Version snapshot storage may increase data size          | Storage growth                                | Define snapshot detail during System Design                                         |
| No rollback                                              | Administrator cannot restore previous version | Clearly communicate rollback is out of scope                                        |
| Manual similarity confirmation is subjective             | Different users may judge differently         | Administrator confirmation is accepted for MVP                                      |

---

## 16. Analysis Gaps

## Resolved Gaps

| Previous Gap                                   | Final Decision                                           |
| ---------------------------------------------- | -------------------------------------------------------- |
| Administrator-confirmed similarity acceptable? | Yes                                                      |
| Automated similarity required?                 | No                                                       |
| Autonaming format                              | `GPF-YYYYMMDD-###`                                       |
| OCR languages                                  | English and Malay                                        |
| Branding file types                            | PNG, JPG, JPEG, SVG                                      |
| WEBP allowed?                                  | No                                                       |
| PDF branding assets allowed?                   | No                                                       |
| Version history output snapshot?               | Yes                                                      |
| Rollback out of scope?                         | Yes                                                      |
| Overlapping blocks block finalization?         | Yes                                                      |
| Blank spacer blocks allowed?                   | No                                                       |
| Copy-ready meaning                             | Can paste into Frappe built-in Print Format and it works |
| Mandatory finalization fields                  | All fields required for the warning letter               |

## Remaining Analysis Gaps

Only these remain for System Design detail:

1. Exact Frappe role mapping for Administrator access.
2. Exact field list for the Warning Letter / Outstanding Invoice Notice DocType.
3. Exact version history snapshot detail level.
4. Exact validation method to prove generated output works in Frappe built-in Print Format.

---

## 17. Stage Gate Checklist

| Checklist Item                 |   Status | Notes                                                                 |
| ------------------------------ | -------: | --------------------------------------------------------------------- |
| Main workflows are clear       | Complete | All major workflows are documented.                                   |
| Use cases are documented       | Complete | Administrator-only use cases are defined.                             |
| Data flow is understood        | Complete | Main data flows are documented.                                       |
| Business rules are analyzed    | Complete | Updated business rules reflect stakeholder answers.                   |
| Edge cases are listed          | Complete | Edge cases include clarified constraints.                             |
| Failure scenarios are listed   | Complete | Failure handling is documented.                                       |
| Analysis gaps are documented   | Complete | Most gaps are resolved; remaining items are for System Design detail. |
| Database design avoided        | Complete | No schema included.                                                   |
| Implementation code avoided    | Complete | No code included.                                                     |
| Technical architecture avoided | Complete | Architecture deferred to System Design.                               |

---

## Handoff to System Designer

Use this System Analysis Document and the approved Requirements Document as the source for System Design.

The System Designer must preserve these confirmed analysis decisions:

1. Administrator-only access.
2. One single-page warning letter PDF.
3. Manual block-based layout recreation.
4. Google Vision OCR as assistive only.
5. English and Malay OCR support.
6. All warning-letter-required fields must be mapped before finalization.
7. Administrator visually confirms 90% similarity.
8. No automated similarity measurement.
9. Autonaming format: `GPF-YYYYMMDD-###`.
10. Branding files limited to PNG, JPG, JPEG, SVG.
11. WEBP and PDF branding assets are not allowed.
12. Version history must include generated output snapshots.
13. Rollback is out of scope.
14. Overlapping blocks block finalization.
15. Blank spacer blocks are not allowed.
16. Final output must be copyable into Frappe built-in Print Format and work.
