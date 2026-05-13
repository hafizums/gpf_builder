# System Analysis Document

Project: **Frappe 14 PDF Reference to Print Format Builder for Warning Letters**
Stage: **Waterfall Stage 2 — System Analysis**
Source: Approved Requirements Document. 

---

## 1. Requirements Summary

### Confirmed Information

The project is a custom **Frappe 14 app** that allows an **Administrator-only** user to recreate a single-page warning letter PDF as a reusable Frappe Print Format.

The system must support:

1. Administrator-only access.
2. Upload of one single-page warning letter PDF.
3. Permanent storage of the uploaded PDF reference.
4. Display of the PDF as a visual reference.
5. Manual drawing of layout blocks over the PDF.
6. Editable layout blocks with drag, resize, align, duplicate, and delete actions.
7. Static text, dynamic field, image, and branding block types.
8. Field selection from the Warning Letter / Outstanding Invoice Notice DocType.
9. Mapping of dynamic blocks to selected DocType fields.
10. Multilingual text support.
11. Google Vision OCR as an assistive feature.
12. Administrator review and confirmation of OCR output.
13. Auto-generated sample data for preview.
14. Side-by-side comparison between generated preview and original PDF reference.
15. A minimum preview similarity target of 90%.
16. Clear communication that the system does not guarantee pixel-perfect PDF conversion.
17. Selection of logos, signatures, and footer branding from existing files.
18. One saved reusable Print Format in the MVP.
19. Autonaming for the saved Print Format.
20. Version history for saved Print Format changes.
21. Final generated output ready to copy and paste into Frappe Print Format.

### Out of Scope

The MVP does not include:

1. Non-administrator access.
2. Multi-user workflow.
3. Draft, review, and approved workflow states.
4. Multi-page PDF support.
5. Lampiran pages.
6. Invoice attachment pages.
7. Batch generation.
8. Multiple saved Print Formats.
9. Fully automatic layout reconstruction.
10. Pixel-perfect PDF conversion.
11. Use of OCR output without Administrator confirmation.
12. New upload workflow for logos, signatures, or footer branding.
13. Database schema design.
14. System architecture design.
15. Implementation code.
16. Testing plan.
17. Deployment plan.
18. Maintenance plan.

### Analysis Clarifications Added

The following clarifications are recommended for System Design:

1. **Save and Finalize should be separate actions.**
2. **Save** stores progress and creates version history.
3. **Finalize** validates readiness for copy-ready output.
4. The 90% similarity target should be treated as **Administrator-confirmed visual similarity** for MVP unless an automated method is later approved.
5. Only one saved reusable Print Format should exist; saving again should update the existing format and create a version history entry.
6. Version history should support traceability, not rollback, unless rollback is later approved.
7. OCR languages should include at minimum **English and Malay / Bahasa Malaysia**, subject to stakeholder confirmation.
8. Branding assets should be selected from existing image files, preferably PNG, JPG, JPEG, and SVG.
9. Overlapping blocks should be allowed with warnings.
10. Text overflow should warn the Administrator but should not be auto-fixed without confirmation.

---

## 2. Current Problem Analysis

Administrators need a controlled way to recreate an existing warning letter PDF layout inside Frappe Print Format without writing the entire print format from scratch.

The current challenge is that warning letter PDFs may be:

1. Scanned.
2. Image-based.
3. Visually complex.
4. Multilingual.
5. Difficult to convert automatically.
6. Different from the final Frappe Print Format rendering environment.

Because of this, the system must not assume that the uploaded PDF can be automatically converted into a usable Print Format.

### Main Problems

#### 1. Manual Recreation Is Time-Consuming

Without a visual builder, the Administrator must manually write or adjust Print Format output. This is inefficient and error-prone.

#### 2. PDF Content May Not Be Extractable

Some warning letter PDFs may contain scanned images rather than selectable text. OCR can assist but cannot be treated as fully reliable.

#### 3. Layout Accuracy Is Difficult

The final Print Format must visually resemble the original warning letter PDF. However, the MVP target is 90% similarity, not pixel-perfect conversion.

#### 4. Dynamic Data Must Be Controlled

Dynamic content must come from selected fields in the Warning Letter / Outstanding Invoice Notice DocType. The system must prevent incomplete required mappings before finalization.

#### 5. OCR Requires Human Review

OCR output may contain errors, especially for scanned, multilingual, or low-quality PDFs. Administrator confirmation is mandatory before OCR text can be used.

#### 6. Scope Must Remain Limited

The MVP must not expand into multi-page PDF conversion, batch generation, invoice attachments, multiple templates, or automated layout reconstruction.

---

## 3. Proposed System Behavior

### Confirmed System Behavior

The system should operate as an Administrator-only visual layout reconstruction tool.

The Administrator uploads a single-page warning letter PDF. The system stores the PDF permanently and displays it as a visual reference. The Administrator manually draws blocks over the PDF and configures each block as static text, dynamic field content, image, or branding.

The Administrator may use Google Vision OCR to assist with text recognition, but OCR output must remain unconfirmed until reviewed, edited if necessary, and confirmed by the Administrator.

The system generates sample data for preview. The preview is shown side-by-side with the original PDF reference. The Administrator adjusts the recreated layout until the visual similarity target is satisfied.

The Administrator saves the reusable Print Format configuration. The system maintains version history for saved changes. Once validation is complete, the Administrator finalizes the format and receives output ready to copy and paste into Frappe Print Format.

### Recommended Clarified Behavior

#### Save Behavior

Save should allow the Administrator to store progress. A saved configuration may still be incomplete if it has not been finalized.

Each save should:

1. Store the current layout configuration.
2. Update the single reusable Print Format configuration.
3. Record a version history entry.
4. Preserve traceability of changes.

#### Finalize Behavior

Finalize should be a validation action, not a full workflow state.

Finalization should require:

1. Valid PDF reference.
2. Required dynamic field mappings completed.
3. OCR-assisted text confirmed if used.
4. Existing branding files still valid.
5. Preview generated successfully.
6. 90% similarity visually confirmed by Administrator.
7. Final copy-ready output generated.

### System Must Not

The system must not:

1. Automatically convert the PDF into a final Print Format without Administrator action.
2. Promise pixel-perfect conversion.
3. Accept multi-page PDFs.
4. Support Lampiran pages.
5. Support invoice attachment pages.
6. Support batch generation.
7. Support multiple saved Print Formats.
8. Allow non-Administrator access.
9. Use unconfirmed OCR output in the final layout.
10. Create database schema or implementation logic during this stage.

---

## 4. User Roles and Responsibilities

## Confirmed Role

### Administrator

The Administrator is the only user role in the MVP.

The Administrator is responsible for:

1. Accessing the app.
2. Uploading the single-page warning letter PDF.
3. Confirming the PDF is the correct warning letter page.
4. Drawing layout blocks manually.
5. Editing layout block position, size, and alignment.
6. Duplicating and deleting blocks.
7. Assigning block types.
8. Entering static text.
9. Reviewing and correcting multilingual text.
10. Running OCR assistance when needed.
11. Reviewing, editing, and confirming OCR output.
12. Selecting dynamic fields from the Warning Letter / Outstanding Invoice Notice DocType.
13. Mapping dynamic fields to layout blocks.
14. Selecting logos, signatures, and footer branding from existing files.
15. Generating previews using sample data.
16. Comparing previews against the PDF reference.
17. Confirming visual similarity target achievement.
18. Saving the reusable Print Format.
19. Finalizing the Print Format.
20. Reviewing version history.
21. Copying the generated output into Frappe Print Format.

## Permission Clarification

The exact meaning of “Administrator” must be confirmed before System Design.

Recommended options:

| Option                                                 | Analysis                                               |
| ------------------------------------------------------ | ------------------------------------------------------ |
| Built-in Frappe Administrator user                     | Strictest and simplest MVP interpretation              |
| System Manager role                                    | Practical if more than one admin user needs access     |
| Custom role: Warning Letter Print Format Administrator | Best long-term control, but requires explicit approval |

### Recommended Analysis Decision

Use the term **Administrator-only** at the analysis level and require System Design to confirm the exact Frappe role model.

## Excluded Roles

The MVP does not include:

1. Template Creator.
2. Template Editor.
3. Template Approver.
4. Business User.
5. Reviewer.
6. Multi-level approval user.

---

## 5. User Workflows

## Workflow 1: Access the Tool

### Trigger

Administrator wants to create, edit, preview, save, or finalize the reusable warning letter Print Format.

### Main Flow

1. Administrator opens the custom app.
2. System checks whether the user has Administrator access.
3. If authorized, the system displays the layout builder.
4. If unauthorized, the system denies access.

### Outcome

Only the Administrator can use the tool.

### Exceptions

1. User is not authorized.
2. User session has expired.
3. Administrator role configuration is missing or incorrect.

---

## Workflow 2: Upload PDF Reference

### Trigger

Administrator wants to upload the warning letter PDF reference.

### Main Flow

1. Administrator selects a PDF file.
2. System validates that the file is a PDF.
3. System validates that the PDF has exactly one page.
4. System stores the PDF permanently.
5. System records PDF metadata.
6. System associates the PDF with the reusable Print Format setup.
7. System displays the PDF as the visual reference.

### Alternative Flow: Multi-Page PDF

1. Administrator selects a multi-page PDF.
2. System rejects or prevents the file from being used.
3. System informs the Administrator that only one warning letter page is supported.

### Alternative Flow: Invalid PDF

1. Administrator selects a corrupted, password-protected, or unreadable PDF.
2. System rejects the file or reports that it cannot be processed.
3. Administrator selects another PDF.

### Outcome

A valid single-page PDF becomes the permanent visual reference.

---

## Workflow 3: Create Layout Blocks

### Trigger

Administrator starts recreating the PDF layout.

### Main Flow

1. Administrator draws a block over the PDF reference.
2. System creates a block with position and size.
3. Administrator assigns a block type:

   * Static text.
   * Dynamic field.
   * Image.
   * Branding element.
4. Administrator configures the block.
5. System stores the block configuration.

### Outcome

The warning letter layout begins to be represented as editable blocks.

---

## Workflow 4: Edit Layout Blocks

### Trigger

Administrator wants to adjust a block.

### Main Flow

1. Administrator selects a block.
2. Administrator drags, resizes, aligns, duplicates, or deletes the block.
3. System updates the layout configuration.
4. System reflects the updated block in preview when preview is generated.

### Alternative Flow: Invalid Block

1. Administrator creates or edits a block with invalid size or position.
2. System warns the Administrator.
3. Administrator corrects the block.

### Outcome

The Administrator can manually refine the recreated layout.

---

## Workflow 5: Configure Static and Multilingual Text

### Trigger

Administrator needs fixed text content in the warning letter.

### Main Flow

1. Administrator creates or selects a static text block.
2. Administrator enters text.
3. System supports multilingual characters.
4. Administrator reviews the content.
5. System stores the text.

### Alternative Flow: Text Overflow

1. Text exceeds the block boundary.
2. System warns the Administrator.
3. Administrator resizes the block, edits the text, or accepts the layout risk if allowed.

### Outcome

Static and multilingual text is included in the recreated layout.

---

## Workflow 6: Use OCR Assistance

### Trigger

Administrator wants OCR assistance for text recognition.

### Main Flow

1. Administrator requests OCR assistance.
2. System sends the PDF reference content to Google Vision OCR.
3. Google Vision returns OCR output.
4. System displays OCR text as unconfirmed.
5. Administrator reviews and edits the OCR output.
6. Administrator confirms the OCR text.
7. System allows confirmed OCR text to be used in layout blocks.

### Alternative Flow: OCR Failure

1. Google Vision OCR is unavailable or fails.
2. System informs the Administrator.
3. Administrator continues manually without OCR.

### Outcome

OCR may assist text entry but cannot bypass Administrator confirmation.

---

## Workflow 7: Map Dynamic Fields

### Trigger

Administrator needs a layout block to display data from the Warning Letter / Outstanding Invoice Notice DocType.

### Main Flow

1. Administrator creates or selects a dynamic field block.
2. System displays selectable fields from the relevant DocType.
3. Administrator selects a field.
4. System maps the selected field to the block.
5. System stores the mapping.

### Alternative Flow: Field Missing or Removed

1. A previously selected field is unavailable.
2. System marks the mapping invalid.
3. Administrator must select a valid replacement field.

### Outcome

Dynamic content is mapped to valid DocType fields.

---

## Workflow 8: Select Branding Assets

### Trigger

Administrator wants to add a logo, signature, or footer branding.

### Main Flow

1. Administrator creates or selects an image or branding block.
2. System displays existing accessible files.
3. Administrator selects a file.
4. System stores the file reference.
5. Preview renders the selected asset.

### Alternative Flow: File Missing or Inaccessible

1. Selected file is deleted, inaccessible, or unsupported.
2. System warns the Administrator.
3. Administrator selects a valid existing file.

### Outcome

Branding assets are included from existing files only.

---

## Workflow 9: Generate Preview and Compare

### Trigger

Administrator wants to inspect the recreated warning letter.

### Main Flow

1. System auto-generates sample data.
2. System renders the recreated warning letter preview.
3. Preview includes:

   * Static text.
   * Multilingual text.
   * Dynamic fields.
   * Confirmed OCR-assisted text.
   * Selected images.
   * Branding elements.
4. System displays the preview side-by-side with the PDF reference.
5. Administrator compares the preview against the reference.
6. Administrator adjusts layout blocks as needed.

### Similarity Confirmation

For MVP, the 90% similarity target should be confirmed visually by the Administrator unless an automated method is approved later.

### Outcome

Administrator can decide whether the preview is close enough to the reference.

---

## Workflow 10: Save Reusable Print Format

### Trigger

Administrator wants to save progress or save the current configuration.

### Main Flow

1. Administrator chooses Save.
2. System checks whether a reusable Print Format configuration already exists.
3. If none exists, system creates the single reusable configuration.
4. If one exists, system updates the existing configuration.
5. System records a version history entry.
6. System keeps the configuration editable.

### Outcome

The current Print Format configuration is saved, and version history is updated.

---

## Workflow 11: Finalize Print Format

### Trigger

Administrator wants the format to be ready for final output generation.

### Main Flow

1. Administrator chooses Finalize.
2. System validates the PDF reference.
3. System validates required dynamic field mappings.
4. System validates confirmed OCR text.
5. System validates selected image and branding file references.
6. System validates preview readiness.
7. System confirms that the 90% similarity target has been visually confirmed.
8. System marks the configuration as ready for copy-ready output.

### Outcome

The reusable Print Format is validated as ready for final generated output.

### Note

Finalize is not a draft-review-approval workflow. It is a validation action only.

---

## Workflow 12: Generate Copy-Ready Output

### Trigger

Administrator needs the output for Frappe Print Format.

### Main Flow

1. Administrator requests final generated output.
2. System reads the finalized configuration.
3. System generates Print Format output.
4. System displays the output in a copy-ready area.
5. Administrator copies the output.
6. Administrator pastes it into Frappe Print Format.

### Outcome

Administrator receives output intended for use in Frappe Print Format.

---

## Workflow 13: View Version History

### Trigger

Administrator wants to review changes made to the saved reusable Print Format.

### Main Flow

1. Administrator opens version history.
2. System displays recorded save events.
3. Administrator reviews:

   * Version number.
   * Timestamp.
   * Administrator identity.
   * Change summary.
   * Changed blocks.
   * Changed mappings.
   * Changed file references.
   * OCR confirmation changes, where applicable.

### Outcome

Changes are traceable.

---

## 6. Use Cases

## UC-001: Access Administrator Tool

### Primary Actor

Administrator.

### Goal

Access the custom app.

### Preconditions

Administrator permission exists.

### Main Success Scenario

1. Administrator opens the app.
2. System validates Administrator access.
3. System displays the layout builder.

### Failure Scenario

Unauthorized user attempts access and is denied.

---

## UC-002: Upload Single-Page PDF Reference

### Primary Actor

Administrator.

### Goal

Upload the warning letter PDF reference.

### Preconditions

Administrator has access to the app.

### Main Success Scenario

1. Administrator selects a PDF.
2. System validates the file type.
3. System validates that the PDF has one page.
4. System stores the PDF permanently.
5. System displays the PDF reference.

### Failure Scenarios

1. File is not a PDF.
2. PDF has multiple pages.
3. PDF is corrupted.
4. PDF is password-protected.
5. PDF cannot be stored.
6. PDF cannot be displayed.

---

## UC-003: Draw Layout Block

### Primary Actor

Administrator.

### Goal

Create a layout block over the PDF reference.

### Preconditions

PDF reference has been uploaded and displayed.

### Main Success Scenario

1. Administrator draws a block.
2. System creates the block.
3. Administrator assigns a block type.
4. System stores block details.

### Failure Scenarios

1. Block has zero width or height.
2. Block is outside the usable page area.
3. Block type is missing.

---

## UC-004: Edit Layout Block

### Primary Actor

Administrator.

### Goal

Modify layout block placement or behavior.

### Main Success Scenario

1. Administrator selects a block.
2. Administrator drags, resizes, aligns, duplicates, or deletes it.
3. System updates the layout configuration.

### Failure Scenarios

1. Block becomes invalid after editing.
2. Required content is deleted.
3. Duplicate block causes accidental duplicate mapping.
4. Overlapping blocks create visual confusion.

---

## UC-005: Add Static or Multilingual Text

### Primary Actor

Administrator.

### Goal

Add fixed text content.

### Main Success Scenario

1. Administrator selects a static text block.
2. Administrator enters multilingual text.
3. System stores the content.
4. Preview displays the text.

### Failure Scenarios

1. Multilingual characters do not render correctly.
2. Text overflows the block.
3. Font support is insufficient.
4. Text is saved incorrectly.

---

## UC-006: Use OCR Assistance

### Primary Actor

Administrator.

### Goal

Use Google Vision OCR to recognize text from the uploaded PDF.

### Preconditions

PDF reference exists and Google Vision OCR is available.

### Main Success Scenario

1. Administrator requests OCR.
2. System sends the PDF reference to OCR processing.
3. System displays OCR output as unconfirmed.
4. Administrator reviews and edits the output.
5. Administrator confirms the OCR text.
6. Confirmed text becomes usable in the layout.

### Failure Scenarios

1. OCR service is unavailable.
2. OCR returns incorrect text.
3. OCR misses text.
4. OCR language support is insufficient.
5. Administrator does not confirm the OCR output.

---

## UC-007: Map Dynamic Field

### Primary Actor

Administrator.

### Goal

Map a block to a selected DocType field.

### Preconditions

Warning Letter / Outstanding Invoice Notice DocType field list is available.

### Main Success Scenario

1. Administrator selects a dynamic block.
2. System displays available fields.
3. Administrator selects a field.
4. System stores the mapping.

### Failure Scenarios

1. Field list cannot be loaded.
2. Selected field no longer exists.
3. Required dynamic block is unmapped.
4. Field type is incompatible with expected display.
5. Same field is mapped multiple times unintentionally.

---

## UC-008: Select Branding Asset

### Primary Actor

Administrator.

### Goal

Select logo, signature, or footer branding from existing files.

### Main Success Scenario

1. Administrator selects an image or branding block.
2. System displays accessible existing files.
3. Administrator selects a file.
4. System stores the file reference.
5. Preview displays the asset.

### Failure Scenarios

1. File is missing.
2. File is inaccessible.
3. File type is unsupported.
4. Image does not fit the block.
5. Image is distorted.

---

## UC-009: Preview Warning Letter

### Primary Actor

Administrator.

### Goal

Preview the recreated warning letter.

### Main Success Scenario

1. System generates sample data.
2. System renders the warning letter preview.
3. System displays preview beside the PDF reference.
4. Administrator compares the two.
5. Administrator adjusts the layout if needed.

### Failure Scenarios

1. Sample data cannot be generated.
2. Preview rendering fails.
3. Dynamic fields display incorrectly.
4. Multilingual text displays incorrectly.
5. Preview does not meet the 90% similarity target.

---

## UC-010: Save Reusable Print Format

### Primary Actor

Administrator.

### Goal

Save the reusable Print Format configuration.

### Main Success Scenario

1. Administrator saves the configuration.
2. System creates or updates the single saved reusable format.
3. System records version history.

### Failure Scenarios

1. Save operation fails.
2. Existing saved format conflict cannot be resolved.
3. Version history cannot be recorded.
4. Autonaming cannot be applied.

---

## UC-011: Finalize Print Format

### Primary Actor

Administrator.

### Goal

Validate that the format is ready for copy-ready output.

### Main Success Scenario

1. Administrator selects Finalize.
2. System validates required data.
3. System verifies required mappings.
4. System checks OCR confirmation.
5. System checks file references.
6. System confirms similarity target confirmation.
7. System marks the format as ready.

### Failure Scenarios

1. Required fields are unmapped.
2. OCR text is unconfirmed.
3. Branding file is missing.
4. Preview has not been generated.
5. Similarity target has not been confirmed.

---

## UC-012: Generate Final Print Format Output

### Primary Actor

Administrator.

### Goal

Generate output ready to copy and paste into Frappe Print Format.

### Main Success Scenario

1. Administrator requests generated output.
2. System generates output from the finalized configuration.
3. System displays output in a copy-ready area.
4. Administrator copies the output into Frappe Print Format.

### Failure Scenarios

1. Configuration is incomplete.
2. Output generation fails.
3. Output is not usable after copy/paste.
4. Output differs from preview.

---

## UC-013: View Version History

### Primary Actor

Administrator.

### Goal

Review saved changes.

### Main Success Scenario

1. Administrator opens version history.
2. System displays recorded versions.
3. Administrator reviews change details.

### Failure Scenarios

1. Version history is missing.
2. Change details are incomplete.
3. Version information is unclear.
4. Version history does not identify what changed.

---

## 7. Data Flow

## Data Flow 1: PDF Reference Upload

1. Administrator selects PDF.
2. System validates file type.
3. System validates page count.
4. System stores PDF permanently.
5. System stores PDF metadata.
6. System links PDF to the reusable Print Format setup.
7. System displays PDF as visual reference.

### Data Involved

1. PDF file.
2. File type.
3. Page count.
4. PDF metadata.
5. Storage reference.
6. Print Format setup association.

---

## Data Flow 2: Layout Block Creation and Editing

1. Administrator draws or edits block.
2. System captures block position and size.
3. Administrator assigns block type.
4. Administrator configures content, field mapping, or file reference.
5. System stores block configuration.
6. Preview uses block configuration for rendering.

### Data Involved

1. Block identifier.
2. Block type.
3. Position.
4. Size.
5. Alignment.
6. Static or dynamic classification.
7. Content value.
8. Field mapping.
9. Multilingual text content.
10. Image or branding file reference.

---

## Data Flow 3: Field Mapping

1. System retrieves available fields from Warning Letter / Outstanding Invoice Notice DocType.
2. Administrator selects a field.
3. System links the selected field to a dynamic block.
4. System stores mapping.
5. Preview uses auto-generated sample data for the selected field.

### Data Involved

1. DocType field list.
2. Selected field.
3. Field label.
4. Field type.
5. Dynamic block identifier.
6. Mapping status.
7. Required-for-finalization flag, if approved.

---

## Data Flow 4: OCR Assistance

1. Administrator requests OCR.
2. System sends PDF reference content to Google Vision OCR.
3. Google Vision returns OCR output.
4. System displays OCR output as unconfirmed.
5. Administrator reviews and edits the output.
6. Administrator confirms text.
7. System stores confirmed OCR-assisted text.

### Data Involved

1. PDF reference content.
2. Raw OCR result.
3. OCR language result, where available.
4. Edited OCR text.
5. OCR confirmation status.
6. Confirmed text.
7. Associated layout block.

### Rule

Unconfirmed OCR output must remain distinguishable from confirmed text.

---

## Data Flow 5: Existing File Selection

1. System displays existing accessible files.
2. Administrator selects logo, signature, or footer branding.
3. System validates file availability and type.
4. System stores file reference in the relevant block.
5. Preview renders the file.

### Data Involved

1. Existing file record.
2. File reference.
3. File type.
4. File accessibility status.
5. Image or branding block identifier.

---

## Data Flow 6: Preview Generation

1. System generates sample data.
2. System combines:

   * Layout blocks.
   * Static text.
   * Multilingual text.
   * Confirmed OCR text.
   * Dynamic field mappings.
   * Existing file references.
3. System renders preview.
4. System displays preview beside PDF reference.
5. Administrator visually compares output.
6. Administrator confirms or rejects similarity target achievement.

### Data Involved

1. Layout configuration.
2. Sample data.
3. Static text.
4. Multilingual text.
5. Dynamic mappings.
6. File references.
7. Preview output.
8. Similarity confirmation status.

---

## Data Flow 7: Save and Version History

1. Administrator saves the configuration.
2. System creates or updates the single reusable Print Format setup.
3. System records version history.
4. System keeps configuration available for further editing.

### Data Involved

1. Saved configuration.
2. Version number.
3. Timestamp.
4. Administrator identity.
5. Change summary.
6. Changed block data.
7. Changed field mappings.
8. Changed file references.
9. OCR confirmation changes.
10. Generated output snapshot or reference, if approved.

---

## Data Flow 8: Finalization

1. Administrator requests finalization.
2. System validates required data.
3. System checks field mappings.
4. System checks OCR confirmation.
5. System checks file references.
6. System checks preview readiness.
7. System verifies similarity confirmation.
8. System marks configuration ready for final output.

### Data Involved

1. Saved configuration.
2. Validation results.
3. Required mapping status.
4. OCR confirmation status.
5. Branding file status.
6. Similarity confirmation status.
7. Finalization status.

---

## Data Flow 9: Final Output Generation

1. Administrator requests final output.
2. System reads finalized configuration.
3. System generates copy-ready Print Format output.
4. System displays output.
5. Administrator copies and pastes it into Frappe Print Format.

### Data Involved

1. Finalized layout configuration.
2. Field mappings.
3. Static text.
4. Confirmed OCR text.
5. Existing file references.
6. Generated output.

---

## 8. Business Logic Analysis

## BL-001: Administrator-Only Access

Only the Administrator may access the app and perform all actions.

### Rule

Every major action requires Administrator permission.

### Open Item

The exact Frappe permission definition of Administrator must be confirmed.

---

## BL-002: Single-Page PDF Only

The system must allow only one single-page warning letter PDF.

### Rule

Multi-page PDFs must be rejected or prevented.

---

## BL-003: Warning Letter Page Only

The MVP supports only the warning letter page.

### Rule

Lampiran pages and invoice attachment pages are outside scope.

---

## BL-004: PDF Is a Visual Reference

The uploaded PDF is not a guaranteed conversion source.

### Rule

The Administrator must manually recreate the layout using blocks.

---

## BL-005: Manual Layout Block Creation

Administrator must draw layout blocks over the PDF reference.

### Required Block Actions

1. Drag.
2. Resize.
3. Align.
4. Duplicate.
5. Delete.

---

## BL-006: Block Type Determines Required Information

| Block Type       | Required Information                                        |
| ---------------- | ----------------------------------------------------------- |
| Static text      | Text content, position, size, alignment                     |
| Dynamic field    | Selected DocType field, position, size, alignment           |
| Image            | Existing file reference, position, size, alignment          |
| Branding element | Existing logo, signature, or footer branding file reference |

---

## BL-007: Dynamic Fields Must Come from Relevant DocType

Dynamic mappings must use fields from the Warning Letter / Outstanding Invoice Notice DocType.

### Rule

Administrator should select fields from the available field list.

### Gap

Exact field list remains unknown.

---

## BL-008: Required Field Mappings

Finalization must be prevented if required mapped blocks are incomplete.

### Recommended Rule

A mapped block should be required when:

1. The selected DocType field is mandatory.
2. The Administrator marks the block as required for finalization.
3. The business process requires the field to appear on the warning letter.

### Remaining Question

Which fields are mandatory for the warning letter output?

---

## BL-009: OCR Is Assistive Only

OCR output must not be automatically trusted.

### Rule

OCR text must be reviewed, edited if necessary, and confirmed by the Administrator before use.

---

## BL-010: Multilingual Text Support

The system must support multilingual text in layout blocks and OCR-assisted content.

### Recommended Minimum OCR Languages

1. English.
2. Malay / Bahasa Malaysia.

### Remaining Question

Are Chinese, Tamil, Arabic, or other languages required?

---

## BL-011: Existing File Selection Only for Branding

Logos, signatures, and footer branding must be selected from existing files.

### Recommended Allowed File Types

1. PNG.
2. JPG.
3. JPEG.
4. SVG.

### Remaining Question

Should WEBP or PDF assets be allowed?

---

## BL-012: Preview Uses Auto-Generated Sample Data

Preview must use sample data generated by the system.

### Rule

Sample data is for preview only unless later requirements say otherwise.

---

## BL-013: 90% Similarity Target

The recreated preview must target at least 90% similarity compared with the PDF reference.

### Recommended MVP Rule

Similarity should be confirmed visually by the Administrator.

### Rule

The system must communicate that this does not mean pixel-perfect conversion.

---

## BL-014: Save vs Finalize

Save and Finalize should be separate.

### Save

Save stores progress and records version history.

### Finalize

Finalize validates readiness and enables final copy-ready output.

---

## BL-015: One Saved Reusable Print Format

The MVP supports only one saved reusable Print Format.

### Recommended Rule

If a saved format already exists, saving again updates the existing format and creates a new version history entry.

---

## BL-016: Autonaming

The saved Print Format must use autonaming.

### Recommended Format

`WARNING-LETTER-PRINT-FORMAT-YYYYMMDD-###`

### Remaining Question

Stakeholders must approve the exact autonaming format.

---

## BL-017: Version History

Version history must record changes made by the Administrator.

### Recommended Minimum Version History

1. Version number.
2. Timestamp.
3. Administrator identity.
4. Change summary.
5. Changed blocks.
6. Changed mappings.
7. Changed image or branding references.
8. OCR confirmation changes.

### Not Required for MVP

1. Rollback.
2. Visual diff.
3. Multi-user approval trail.

---

## BL-018: Text Overflow

If text exceeds a block boundary, the system should warn the Administrator.

### Rule

The system should not auto-resize or auto-change content without Administrator action.

---

## BL-019: Overlapping Blocks

Overlapping blocks should be allowed but warned.

### Reason

Some warning letters may intentionally overlap stamps, signatures, headers, backgrounds, or branding.

---

## BL-020: Blank Blocks

Blank blocks should not be allowed for finalization unless a specific spacer or visual layout block type is approved.

---

## 9. Permission and Access Analysis

## Confirmed Permissions

| Action                                        | Allowed User       |
| --------------------------------------------- | ------------------ |
| Access app                                    | Administrator only |
| Upload PDF reference                          | Administrator only |
| Create reusable Print Format                  | Administrator only |
| Edit reusable Print Format                    | Administrator only |
| Finalize warning letter Print Format          | Administrator only |
| Select DocType fields                         | Administrator only |
| Select logos, signatures, and footer branding | Administrator only |
| Generate preview                              | Administrator only |
| Generate final output                         | Administrator only |
| View version history                          | Administrator only |

## Permission Risks

1. The Administrator role definition may be ambiguous.
2. Existing files may be accessible or inaccessible depending on Frappe file permissions.
3. Version history may expose sensitive content if not restricted.
4. OCR processing may involve sensitive warning letter content.
5. Generated output may expose mapped fields or business-sensitive formatting.

## Recommended Permission Rule

The system should respect existing Frappe file permissions and should not bypass them unless explicitly approved.

## Open Permission Question

Which permission model should be used?

1. Built-in Administrator account.
2. System Manager role.
3. Custom Administrator role.
4. Another Frappe permission model.

---

## 10. Validation Rules

## PDF Upload Validation

1. File must be PDF.
2. PDF must contain exactly one page.
3. PDF must be readable.
4. PDF must be displayable.
5. PDF must be stored permanently.
6. Multi-page PDFs must be rejected.
7. Lampiran pages are not supported.
8. Invoice attachment pages are not supported.

## Layout Block Validation

1. Block must have a unique identifier.
2. Block must have a valid type.
3. Block must have valid position.
4. Block must have valid size.
5. Block must have valid alignment.
6. Block must not have zero width or height.
7. Dynamic block must have a selected field before finalization if required.
8. Static text block must have text unless empty content is explicitly allowed.
9. Image or branding block must reference an existing valid file.
10. OCR-assisted text must be confirmed before final output.

## Field Mapping Validation

1. Selected field must exist in the relevant DocType field list.
2. Field mapping must be linked to a valid block.
3. Required mappings must be complete before finalization.
4. Removed fields must invalidate affected mappings.
5. Incompatible field types should trigger warning or prevention, depending on final design rules.
6. Same field mapped multiple times should be allowed only with warning.

## OCR Validation

1. OCR output must be marked unconfirmed by default.
2. OCR output must not be used in final output until confirmed.
3. Administrator must be able to edit OCR output.
4. Confirmed OCR text must be distinguishable from raw OCR output.
5. Unsupported or uncertain OCR language output must require manual review.

## Multilingual Text Validation

1. Multilingual characters must be accepted.
2. Multilingual text must be preserved after save.
3. Multilingual text must render in preview.
4. Text overflow should generate warning.
5. Required OCR languages must be confirmed.

## Branding File Validation

1. Branding file must already exist.
2. Branding file must be accessible to the Administrator.
3. Branding file must use an allowed type.
4. Branding file must be renderable in preview.
5. Missing or deleted file references must block finalization.

## Preview Validation

1. Preview must use auto-generated sample data.
2. Preview must include static text, multilingual text, dynamic fields, selected images, and branding.
3. Preview must be displayed side-by-side with the PDF reference.
4. Preview must clearly communicate the 90% similarity target.
5. Preview must communicate that pixel-perfect conversion is not guaranteed.
6. Similarity should be confirmed visually by the Administrator for MVP.

## Save Validation

1. Only Administrator can save.
2. Save should create or update the single reusable Print Format configuration.
3. Save should record version history.
4. Save may allow incomplete configuration if not finalized.

## Finalization Validation

1. Required mappings must be complete.
2. OCR-assisted content must be confirmed.
3. Branding file references must be valid.
4. Preview must be generated.
5. Similarity target must be confirmed.
6. Final output must be available after successful finalization.

## Final Output Validation

1. Output must be generated from the saved or finalized configuration.
2. Output must be displayed in a copy-ready area.
3. Output must be suitable for copying into Frappe Print Format.
4. Output is not guaranteed to be pixel-perfect.

---

## 11. Edge Cases

## PDF Edge Cases

1. PDF has more than one page.
2. PDF has zero pages.
3. PDF is corrupted.
4. PDF is password-protected.
5. PDF is scanned and image-only.
6. PDF is very large.
7. PDF has unusual dimensions.
8. PDF is rotated.
9. PDF contains low-resolution images.
10. PDF is stored but later becomes unavailable.
11. PDF renders differently from expected.

## Layout Block Edge Cases

1. Block is drawn outside page boundary.
2. Block has zero width or height.
3. Block is too small to edit.
4. Blocks overlap.
5. Duplicate block creates accidental duplicate mapping.
6. Deleted block was required.
7. Text overflows the block.
8. Image is distorted.
9. Image does not preserve aspect ratio.
10. Multilingual text expands beyond expected width.
11. Administrator creates too many blocks.
12. Block alignment differs between editor and preview.

## Field Mapping Edge Cases

1. Field list cannot be loaded.
2. Selected field is removed later.
3. Selected field is renamed.
4. Field type changes.
5. Same field is mapped multiple times.
6. Required field is unmapped.
7. Optional field has no sample data.
8. Long sample field value breaks layout.
9. Currency, date, or number formatting affects layout.
10. Multilingual dynamic values affect layout direction or spacing.

## OCR Edge Cases

1. OCR service is unavailable.
2. OCR returns no text.
3. OCR text order is incorrect.
4. OCR misreads multilingual characters.
5. OCR detects branding text incorrectly.
6. OCR detects signatures or logos as text.
7. OCR output is incomplete.
8. OCR language is unsupported.
9. Administrator forgets to confirm OCR text.
10. OCR output conflicts with manually entered content.

## Branding Edge Cases

1. Selected file is deleted.
2. Selected file permission changes.
3. Selected file type is unsupported.
4. Selected image is too large.
5. Selected image is too small or low-quality.
6. Signature image has transparent background issues.
7. Footer branding does not fit the layout.
8. SVG rendering differs between preview and Frappe Print Format.

## Preview Edge Cases

1. Preview fails to render.
2. Sample data cannot be generated.
3. Preview does not match final output.
4. Similarity target is disputed.
5. Preview is below 90%.
6. Preview comparison is difficult on small screens.
7. Multilingual text renders incorrectly.
8. Image scaling differs.
9. Dynamic values overflow.
10. Administrator confirms similarity despite visible mismatch.

## Save and Version History Edge Cases

1. Administrator attempts to create a second saved Print Format.
2. Save fails midway.
3. Version history is not recorded.
4. Version history lacks useful detail.
5. Autonaming creates duplicate names.
6. Administrator wants rollback, but rollback is not included.
7. Generated output is copied before latest save.
8. Finalization occurs on outdated saved data.

---

## 12. Failure Scenarios

## FS-001: Unauthorized Access

An unauthorized user attempts to access the app.

### Expected Handling

System denies access and prevents all functions.

---

## FS-002: Invalid PDF Upload

Administrator uploads a non-PDF file.

### Expected Handling

System rejects the file and asks for a valid PDF.

---

## FS-003: Multi-Page PDF Upload

Administrator uploads a PDF with more than one page.

### Expected Handling

System rejects or prevents the file from being used.

---

## FS-004: PDF Storage Failure

PDF passes validation but cannot be stored permanently.

### Expected Handling

System reports the failure and does not allow layout work to proceed as if the PDF is available.

---

## FS-005: PDF Display Failure

PDF is stored but cannot be displayed as a visual reference.

### Expected Handling

System reports that the reference cannot be displayed and blocks layout work until resolved.

---

## FS-006: OCR Service Failure

Google Vision OCR is unavailable.

### Expected Handling

System informs the Administrator and allows manual entry to continue.

---

## FS-007: Incorrect OCR Output

OCR returns inaccurate text.

### Expected Handling

System requires Administrator review and confirmation before use.

---

## FS-008: Unconfirmed OCR Text Used in Layout

Administrator attempts to finalize with unconfirmed OCR text.

### Expected Handling

System blocks finalization and requires confirmation.

---

## FS-009: Missing Required Mapping

Administrator attempts to finalize with missing required dynamic fields.

### Expected Handling

System blocks finalization and identifies incomplete mappings.

---

## FS-010: Field Removed After Mapping

A previously mapped field is no longer available.

### Expected Handling

System marks the mapping invalid and requires correction.

---

## FS-011: Branding File Missing

Selected logo, signature, or footer branding file is deleted or inaccessible.

### Expected Handling

System warns the Administrator and blocks finalization until replaced.

---

## FS-012: Preview Generation Failure

System cannot generate preview.

### Expected Handling

System reports the failure and prevents misleading comparison.

---

## FS-013: Similarity Target Not Confirmed

Administrator attempts to finalize without confirming the 90% similarity target.

### Expected Handling

System blocks finalization until similarity is confirmed.

---

## FS-014: Save Failure

System cannot save the reusable Print Format configuration.

### Expected Handling

System reports the failure and avoids recording an incomplete saved state.

---

## FS-015: Version History Failure

Changes are saved but version history cannot be recorded.

### Expected Handling

System reports the traceability issue because version history is required.

---

## FS-016: Final Output Generation Failure

System cannot generate copy-ready output.

### Expected Handling

System reports the failure and does not present incomplete output as final.

---

## FS-017: Output Not Usable After Copy/Paste

Generated output does not work correctly in Frappe Print Format.

### Expected Handling

System should indicate the issue and allow Administrator to return to layout editing or configuration correction.

---

## 13. Constraints

## Confirmed Constraints

1. The system must run as a custom app in Frappe 14.
2. The system must integrate with Frappe Print Format functionality.
3. The system must access fields from the Warning Letter / Outstanding Invoice Notice DocType.
4. The system must use Google Vision OCR for assistive OCR.
5. The system must integrate with existing Frappe file records.
6. The system must restrict access to Administrator only.
7. The MVP must support only one single-page warning letter PDF.
8. The uploaded PDF must be stored permanently.
9. The system must support manual layout block creation.
10. OCR output must require Administrator confirmation.
11. The system must support multilingual content.
12. Preview must be side-by-side with the PDF reference.
13. Preview must target 90% similarity.
14. The system must not promise pixel-perfect conversion.
15. The MVP must support only one saved reusable Print Format.
16. Saved Print Format naming must use autonaming.
17. Version history is required.
18. Final output must be ready to copy and paste into Frappe Print Format.
19. Multi-page PDFs are not supported.
20. Batch generation is not supported.
21. Invoice attachments are not supported.
22. Lampiran pages are not supported.

## Stage Constraints

This document must not include:

1. Database schema design.
2. Final technical architecture.
3. Implementation code.
4. Testing plan.
5. Deployment plan.
6. Maintenance plan.

---

## 14. Dependencies

## Functional Dependencies

1. Frappe 14 environment.
2. Frappe Print Format functionality.
3. Warning Letter / Outstanding Invoice Notice DocType.
4. Existing Frappe file records.
5. Google Vision OCR.
6. Administrator permission configuration.

## Data Dependencies

1. Uploaded PDF reference.
2. PDF metadata.
3. Layout block configuration.
4. Field mappings.
5. Static text content.
6. Multilingual text content.
7. OCR output and confirmation status.
8. Existing file references.
9. Auto-generated sample data.
10. Saved Print Format configuration.
11. Version history records.
12. Final generated output.

## External Dependencies

1. Google Vision OCR service availability.
2. Google Vision OCR language support.
3. Network or service connectivity required for OCR.
4. Frappe file access controls.

## Clarification Dependencies

Before System Design, stakeholders should confirm:

1. Exact Administrator role model.
2. Exact DocType fields.
3. Mandatory dynamic fields.
4. Similarity confirmation method.
5. Autonaming format.
6. OCR languages.
7. Allowed branding file types.
8. Version history detail level.

---

## 15. Risks

## R-001: Similarity Measurement Risk

The 90% similarity target is required, but the measurement method is not fully defined.

### Impact

Acceptance may be disputed.

### Recommended Mitigation

Use Administrator-confirmed visual similarity for MVP unless automated measurement is approved.

---

## R-002: OCR Accuracy Risk

OCR may misread scanned or multilingual text.

### Impact

Incorrect text may appear in the final output.

### Mitigation

Require Administrator review, editing, and confirmation.

---

## R-003: Scope Creep Risk

Users may expect automatic conversion, multi-page support, or batch generation.

### Impact

MVP scope may expand beyond approved requirements.

### Mitigation

Keep excluded features clearly documented.

---

## R-004: Permission Ambiguity Risk

“Administrator” is not yet mapped to an exact Frappe role.

### Impact

Access control may be implemented inconsistently.

### Mitigation

Confirm role model before System Design.

---

## R-005: Print Format Output Risk

The generated output may preview correctly but behave differently after copy/paste into Frappe Print Format.

### Impact

Administrator may need manual correction.

### Mitigation

Define copy-ready expectations clearly during System Design.

---

## R-006: Version History Ambiguity Risk

The required detail level for version history is not fully defined.

### Impact

Traceability may not meet expectations.

### Mitigation

Use minimum traceability fields and keep rollback out of MVP unless approved.

---

## R-007: Multilingual Rendering Risk

Multilingual text may not display correctly.

### Impact

Warning letters may contain incorrect or unreadable text.

### Mitigation

Confirm required languages and validate rendering behavior during later stages.

---

## R-008: Branding Asset Compatibility Risk

Existing files may use unsupported formats or become inaccessible.

### Impact

Preview or final output may break.

### Mitigation

Restrict allowed file types and validate file availability.

---

## R-009: Single Saved Format Conflict Risk

The MVP supports only one saved reusable format.

### Impact

Administrator may expect multiple formats.

### Mitigation

Update existing single format on save and record version history.

---

## R-010: Required Field Ambiguity Risk

The system must prevent incomplete required mappings, but required fields are not yet confirmed.

### Impact

Finalization rules may be incomplete.

### Mitigation

Confirm mandatory DocType fields before System Design.

---

## 16. Analysis Gaps

## Gaps Resolved for Analysis

The following gaps now have recommended analysis decisions:

| Gap                            | Resolution                                                           |
| ------------------------------ | -------------------------------------------------------------------- |
| Save vs finalization           | Save stores progress; Finalize validates readiness                   |
| 90% similarity method          | Administrator-confirmed visual similarity for MVP                    |
| Existing saved format behavior | Saving updates the single existing format                            |
| Version history purpose        | Traceability only; rollback not required                             |
| OCR handling                   | OCR output must remain unconfirmed until reviewed                    |
| Text overflow                  | Warn Administrator; do not auto-fix                                  |
| Overlapping blocks             | Allow with warning                                                   |
| Blank blocks                   | Do not allow for finalization unless a spacer type is later approved |
| Branding assets                | Use existing files only                                              |
| Branding file types            | Recommend PNG, JPG, JPEG, SVG                                        |
| OCR languages                  | Recommend English and Malay minimum                                  |
| Copy-ready output              | Usable for copy/paste, not pixel-perfect                             |
| Approval workflow              | No workflow states; finalization is validation only                  |

## Remaining Open Questions

These must be confirmed before or during System Design:

1. Does “Administrator” mean the built-in Frappe Administrator user, System Manager role, or a custom role?
2. What exact fields exist in the Warning Letter / Outstanding Invoice Notice DocType?
3. Which fields are mandatory for finalization?
4. Is Administrator-confirmed visual similarity acceptable for the 90% target?
5. Should an automated similarity measurement be required later?
6. Is the proposed autonaming format acceptable: `WARNING-LETTER-PRINT-FORMAT-YYYYMMDD-###`?
7. Are English and Malay sufficient OCR languages for MVP?
8. Are PNG, JPG, JPEG, and SVG sufficient for branding assets?
9. Should WEBP be allowed?
10. Should PDF files be allowed as branding assets?
11. Should version history include generated output snapshots?
12. Is rollback explicitly out of scope for version history?
13. Should overlapping blocks ever block finalization?
14. Should blank spacer blocks be allowed?
15. What exact guarantee is expected from “ready to copy and paste into Frappe Print Format”?

---

## 17. Stage Gate Checklist

| Checklist Item                       |   Status | Notes                                                                                                                       |
| ------------------------------------ | -------: | --------------------------------------------------------------------------------------------------------------------------- |
| Main workflows are clear             | Complete | Access, upload, block editing, OCR, mapping, preview, save, finalize, output, and version history workflows are documented. |
| Use cases are documented             | Complete | Administrator-only use cases are listed.                                                                                    |
| Data flow is understood              | Complete | Data flows are documented without database schema design.                                                                   |
| Business rules are analyzed          | Complete | Core business rules and clarified rules are documented.                                                                     |
| Edge cases are listed                | Complete | PDF, block, field, OCR, branding, preview, save, and version history edge cases are included.                               |
| Failure scenarios are listed         | Complete | Major failure scenarios and expected handling are documented.                                                               |
| Analysis gaps are documented         | Complete | Remaining open questions are listed.                                                                                        |
| Confirmed information is separated   | Complete | Confirmed scope is based on the approved Requirements Document.                                                             |
| Assumptions are identified           | Complete | Recommended analysis decisions are clearly marked.                                                                          |
| Open questions are identified        | Complete | Questions requiring stakeholder confirmation are documented.                                                                |
| Database design avoided              | Complete | No schema is included.                                                                                                      |
| Implementation code avoided          | Complete | No code is included.                                                                                                        |
| Final technical architecture avoided | Complete | Architecture is deferred to System Design.                                                                                  |

---

