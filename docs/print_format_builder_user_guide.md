# Print Format Builder User Guide

This guide explains how to use the **GPF Print Format Builder** in Frappe to create a visual print layout for the **Dunning Letter** DocType.

The builder lets an Administrator upload a single-page PDF reference, place text and document fields visually on top of it, preview the generated layout, and finalize the setup for production use.

## Table of Contents

1. [Purpose](#purpose)
2. [Who Can Use It](#who-can-use-it)
3. [Before You Start](#before-you-start)
4. [Open the Builder](#open-the-builder)
5. [Builder Screen Overview](#builder-screen-overview)
6. [Complete Workflow](#complete-workflow)
7. [Select a Target DocType and Source Document](#select-a-target-doctype-and-source-document)
8. [Upload the PDF Reference](#upload-the-pdf-reference)
9. [Add Layout Blocks](#add-layout-blocks)
10. [Edit Block Properties](#edit-block-properties)
11. [Use Dynamic Fields](#use-dynamic-fields)
12. [Use OCR Text](#use-ocr-text)
13. [Use Images and Branding](#use-images-and-branding)
14. [Positioning and Sizing](#positioning-and-sizing)
15. [Save the Layout](#save-the-layout)
16. [Preview the Layout](#preview-the-layout)
17. [Reset the Layout](#reset-the-layout)
18. [Generate Print Format Output](#generate-print-format-output)
19. [Finalize the Setup](#finalize-the-setup)
20. [Return to Editing](#return-to-editing)
21. [Validation Rules](#validation-rules)
22. [Rate Limit Settings](#rate-limit-settings)
23. [Recommended Working Practices](#recommended-working-practices)
24. [Troubleshooting](#troubleshooting)
25. [Limitations](#limitations)

## Purpose

Use the Print Format Builder when you need to reproduce a PDF-style Dunning Letter layout without manually writing all HTML and CSS.

The builder supports:

- A single-page PDF reference as the layout background.
- Static text blocks.
- Dynamic fields from the Dunning Letter DocType.
- OCR text blocks.
- Image and branding blocks.
- Visual drag-and-resize layout editing.
- HTML preview generation.
- Finalized, locked output for production.

## Who Can Use It

The builder is restricted to the **Administrator** role/user.

Non-Administrator users should not be able to:

- Open the builder page.
- Upload PDF references.
- Save layouts.
- Run OCR.
- Generate output.
- Finalize or unlock a setup.

## Before You Start

Prepare the following:

- Administrator login access.
- A clean, single-page PDF reference of the desired Dunning Letter layout.
- The PDF must be private, readable, unprotected, and no larger than 2 MB.
- Any logo, signature, stamp, or branding image that must appear in the final layout.
- Knowledge of which Dunning Letter fields should appear in the print format.

## Open the Builder

1. Log in to Frappe Desk as Administrator.
2. Open the route:

   ```text
   /app/gpf-builder
   ```

3. The page title should show:

   ```text
   GPF Print Format Builder
   ```

4. Wait for the setup status, field list, and canvas to load.

## Builder Screen Overview

The builder contains four main areas.

### Toolbar

The toolbar contains the main actions:

| Button | Purpose |
| --- | --- |
| `PDF` | Upload and link the PDF reference. |
| `PDF Text` | Extract selectable text from the uploaded PDF for copy/paste. |
| `Save` | Save the current layout blocks. |
| `Preview` | Open an HTML preview of the saved layout. |
| `Output` | Generate copy-ready Print Format HTML. |
| `Text` | Add a static text block. |
| `Field` | Add a dynamic source document field block. |
| `OCR Text` | Add an OCR text block. |
| `Image` | Add an image block. |
| `Branding` | Add a branding block. |
| `Duplicate` | Duplicate the selected block. |
| `Reset` | Clear the PDF reference, layout blocks, OCR results, and source document selection after confirmation. |
| `Delete` | Delete the selected block. |
| `Fullscreen` | Expand the builder over the full browser viewport. |
| `V Ruler` | Add a draggable vertical ruler for left/right alignment. |
| `H Ruler` | Add a draggable horizontal ruler for top/bottom alignment. |
| `Clear Rulers` | Remove all editor ruler guides. |
| `Run OCR` | Run OCR against the uploaded PDF reference. |
| `Finalize` | Save, validate, and lock the layout. |
| `Return` | Return a finalized setup to editing mode. Only visible after finalization. |

### Status Bar

The status bar shows:

- Active setup name.
- Setup status: `Editing` or `Finalized`.
- Current PDF reference file, if one is uploaded.

### Canvas

The canvas is the visual editing area.

If a PDF reference is uploaded, the first page is rendered as the background. Blocks are placed on top of this background.

### Property Panel

The property panel shows editable properties for the selected block:

- Block Type
- Static Text
- Fieldname
- OCR Result
- File Reference
- Text Appearance
- X %
- Y %
- W %
- H %

It also shows the allowed target DocType fields that can be used in dynamic field blocks.

The `OCR Results` section shows detected OCR text from the uploaded PDF. Each OCR result can be viewed, confirmed, or applied to an OCR Text block.

The `Source Document` section lets you select the target DocType and the source record that should provide real values for dynamic fields.

Use `Fullscreen` when you need more room for precise alignment. Click it again, or press `Esc`, to return to the normal Desk view.

Use `V Ruler` and `H Ruler` to add draggable alignment guides. Vertical rulers show left and right percentage positions. Horizontal rulers show top and bottom percentage positions. Rulers are editor-only helpers and are not saved into the generated print format.

## Complete Workflow

Use this normal workflow:

1. Open `/app/gpf-builder`.
2. Select the target DocType and source document.
3. Upload the PDF reference.
4. Add blocks for text, fields, images, and OCR text.
5. Move and resize blocks on the canvas.
6. Edit each block in the property panel.
7. Save the layout.
8. Preview the layout.
9. Adjust and save again until the layout is correct.
10. Run and confirm OCR if OCR blocks are used.
11. Finalize the setup.
12. Generate the output.
13. Copy the generated HTML into the intended Frappe Print Format workflow.

## Select a Target DocType and Source Document

Use the `Source Document` section in the right panel to choose:

- `Target DocType`: the DocType this print layout is being built for.
- Source document: the specific record used to preview real dynamic field values.

After selecting a target DocType and source document:

- Dynamic Field blocks on the canvas show values from the selected source document.
- `Preview` renders dynamic fields using the selected source document.
- `Output` generates HTML using the selected source document when run from the builder.

If no source document is selected, preview uses redacted sample values and generated output may show blank dynamic fields.

Changing the target DocType clears the current PDF reference, layout blocks, and OCR results because existing blocks may no longer match the new DocType fields.

## Upload the PDF Reference

1. Click `PDF`.
2. Select the reference PDF.
3. Upload it as a private file.
4. Wait for the success message:

   ```text
   PDF reference saved.
   ```

5. Confirm the PDF name appears in the status bar.
6. Confirm the PDF renders as the canvas background.

### PDF Requirements

The uploaded PDF must meet these rules:

| Rule | Requirement |
| --- | --- |
| File type | `.pdf` only |
| Storage | Private file |
| Size | Maximum 2 MB |
| Page count | Exactly 1 page |
| Readability | Not corrupted or password-protected |

If the PDF does not render, verify that the file is valid and stored privately.

### Copy Text from the PDF

After uploading a PDF reference, click `PDF Text` to open the extracted PDF text in a selectable dialog.

Use this when you need to copy wording from the reference PDF into a Static Text block.

If the dialog says no selectable text was found, the PDF is probably scanned image content. Use OCR Text blocks for scanned regions instead.

## Add Layout Blocks

Click one of the block buttons in the toolbar:

- `Text`
- `Field`
- `OCR Text`
- `Image`
- `Branding`

New blocks are added near the top-left of the canvas. Select a block to edit it.

## Edit Block Properties

Click a block on the canvas. Its properties appear in the right panel.

### Block Type

Controls how the block is rendered.

Allowed values:

- `Static Text`
- `Dynamic Field`
- `OCR Text`
- `Image`
- `Branding`

### Static Text

Used by `Static Text` blocks.

Enter the literal text that should appear in the print format, such as:

```text
FINAL NOTICE
```

Static text cannot be empty when the layout is saved.

### Fieldname

Used by `Dynamic Field` blocks.

Enter or select a valid Dunning Letter fieldname, such as:

```text
customer_name
posting_date
due_date
outstanding_amount
company
```

The fieldname must be in the allowed field list.

### OCR Result

Used by `OCR Text` blocks.

This should reference a saved OCR result. OCR results must be confirmed before finalization.

### File Reference

Used by `Image` and `Branding` blocks.

Enter the Frappe File document name or file URL for the uploaded image.

Supported branding/image formats:

- `.png`
- `.jpg`
- `.jpeg`
- `.svg`

Rejected formats include:

- `.webp`
- `.pdf`

### X %, Y %, W %, H %

These fields control block placement and size as percentages of the page:

| Field | Meaning |
| --- | --- |
| `X %` | Horizontal position from the left edge. |
| `Y %` | Vertical position from the top edge. |
| `W %` | Width as a percentage of page width. |
| `H %` | Height as a percentage of page height. |

All values must stay within `0` to `100`, and the block must not exceed the page boundary.

### Text Appearance

Use these controls to match text against the PDF reference:

| Field | Purpose |
| --- | --- |
| `Font Size` | Controls text size in pixels. |
| `Line Height` | Controls vertical spacing between text lines. |
| `Weight` | Switches between normal and bold text. |
| `Align` | Aligns text left, center, or right inside the block. |
| `Color` | Sets the text color. |
| `Style` | Switches between normal and italic text. |

The canvas uses these same style values while editing, so the block should visually match the generated preview more closely.

## Use Dynamic Fields

Dynamic fields pull data from the Dunning Letter document.

### Add a Dynamic Field

1. Click `Field`.
2. Select the new block.
3. Click a field from the `Fields` list in the right panel, or type the fieldname manually.
4. Move and resize the block.
5. Click `Save`.

### Allowed Field Types

The builder allows printable data-style fields:

- Data
- Text
- Long Text
- Small Text
- Select
- Date
- Datetime
- Currency
- Int
- Float
- Link
- Check

System and layout fields are excluded.

Examples of excluded fields:

- `name`
- `owner`
- `creation`
- `modified`
- `modified_by`
- `docstatus`
- `idx`
- Section Breaks
- Column Breaks

## Use OCR Text

OCR is used when text should be extracted from the uploaded reference PDF.

### Run OCR

1. Upload a valid PDF reference first.
2. Click `OCR Text` to add an OCR block.
3. Move and resize the OCR Text block so it tightly covers only the PDF text you want to extract.
4. Keep that OCR Text block selected.
5. Click `Run OCR`.
6. Review the detected text dialog.
7. The OCR result is automatically attached to the selected OCR Text block.
8. The result also appears in the `OCR Results` section of the property panel.
9. Click `Confirm` after checking that the text is correct.
10. Save the layout.

OCR scans the selected OCR Text block area, not the whole PDF. Create separate OCR Text blocks for separate text areas.

### OCR Confirmation

OCR results must be confirmed before finalization.

If an OCR block references an unconfirmed OCR result, finalization is blocked.

Use OCR Text for text that should come from the scanned/reference PDF. Use Static Text for wording you want to type manually.

## Use Images and Branding

Use `Image` or `Branding` blocks for visual assets such as:

- Logo
- Letterhead element
- Signature
- Stamp
- Footer image

### Add an Image or Branding Block

1. Upload the image as a Frappe File.
2. Click `Image` or `Branding`.
3. Select the block.
4. Enter the File document name or file URL in `File Reference`.
5. Position and resize the block.
6. Save the layout.

Images are rendered with:

```css
object-fit: contain;
```

This keeps the image inside the block without cropping.

## Positioning and Sizing

You can position blocks in two ways:

1. Drag and resize the block directly on the canvas.
2. Enter exact percentage values in the property panel.

Use percentage fields for accurate alignment.

Example:

| Field | Value |
| --- | --- |
| `X %` | `10` |
| `Y %` | `20` |
| `W %` | `40` |
| `H %` | `5` |

This places the block 10% from the left, 20% from the top, 40% wide, and 5% high.

## Save the Layout

Click `Save` after making changes.

Saving writes the current canvas blocks to the active setup.

Important behavior:

- Save replaces the saved block list with the current canvas state.
- Deleted blocks are removed from the saved layout.
- Unsaved canvas changes are not available to preview or output generation.

## Preview the Layout

1. Click `Save`.
2. Click `Preview`.
3. Review the generated HTML preview.

The preview uses redacted sample data for dynamic fields.

Example preview values may include:

| Field | Sample Value |
| --- | --- |
| `customer_name` | `JOHN DOE (REDACTED)` |
| `customer` | `CUST-00001` |
| `posting_date` | `2026-05-13` |
| `due_date` | `2026-05-20` |
| `outstanding_amount` | `1,234.56` |
| `company` | `SAMPLE CORP` |

If the preview looks wrong:

1. Close the preview.
2. Adjust the blocks.
3. Save again.
4. Preview again.

## Reset the Layout

Use `Reset` when you need to return the builder to a clean state.

1. Click `Reset`.
2. Confirm the prompt:

   ```text
   Reset the builder?
   ```

3. The builder clears the PDF reference.
4. The builder removes all layout blocks from the canvas and database.
5. The builder removes OCR results for the active setup.
6. The builder clears the selected source document.

Reset does not delete uploaded File records. It only unlinks the PDF reference from the builder setup.

## Generate Print Format Output

Click `Output` to generate the copy-ready Print Format HTML.

The setup must be finalized before production output can be generated.

The output is intended to be used in the related Frappe Print Format workflow for the Dunning Letter layout.

## Finalize the Setup

Finalization locks the layout for production use.

1. Confirm all blocks are correct.
2. Click `Save`.
3. Click `Finalize`.
4. Confirm the prompt:

   ```text
   Finalize and lock this layout?
   ```

5. The setup status changes to:

   ```text
   Finalized
   ```

After finalization:

- Editing controls are hidden.
- Blocks cannot be dragged.
- The layout is locked.
- A version snapshot is created.
- The `Return` button becomes available.

## Return to Editing

Use `Return` when a finalized layout needs changes.

1. Click `Return`.
2. The setup status changes back to:

   ```text
   Editing
   ```

3. Edit the layout.
4. Save.
5. Finalize again when ready.

Returning to editing creates a version snapshot.

## Validation Rules

The builder validates layout data before saving or finalizing.

### Block Validation

Each block must have:

- A valid block type.
- `x`, `y`, `width`, and `height` values between `0` and `100`.
- Width greater than `0`.
- Height greater than `0`.
- No overflow beyond the page boundary.

### Static Text Validation

Static Text blocks must contain non-empty text.

### Dynamic Field Validation

Dynamic Field blocks must use an allowed Dunning Letter fieldname.

### OCR Validation

OCR blocks that reference OCR results require valid OCR result records.

Before finalization, referenced OCR results must be confirmed.

### Image and Branding Validation

Image and Branding blocks must use valid file references and supported image formats.

### Finalization Validation

Finalization requires:

- Setup is currently in `Editing` status.
- At least one layout block exists.
- OCR results are confirmed if OCR blocks are used.
- Blocks do not overlap.

If two blocks overlap, finalization is blocked.

## Rate Limit Settings

Administrators can configure builder rate limits in:

```text
GPF Rate Limit Settings
```

The settings are applied per user and per action.

| Setting | Default | Applies To |
| --- | ---: | --- |
| `Enable Rate Limiting` | Enabled | Turns all builder rate limiting on or off. |
| `Window Seconds` | `3600` | Length of the rate-limit window. |
| `Upload PDF Limit` | `5` | PDF reference uploads. |
| `Run OCR Limit` | `3` | OCR runs. |
| `Generate Preview Limit` | `30` | Preview generation. |
| `Save Layout Limit` | `60` | Layout saves. |
| `Finalize Limit` | `10` | Finalization attempts. |
| `Generate Output Limit` | `30` | Output generation. |
| `Return to Editing Limit` | `5` | Returning a finalized setup to editing. |

Set a limit to `0` to disable limiting for that specific action while leaving other action limits enabled.

## Recommended Working Practices

### Save Frequently

Save after each meaningful layout change.

Preview and output generation use the saved layout, not unsaved canvas edits.

### Use Small Blocks

Create separate blocks for separate content areas.

For example, use separate blocks for:

- Heading
- Customer name
- Address
- Outstanding amount
- Footer
- Signature

### Avoid Overlaps

Blocks that overlap prevent finalization.

Leave enough spacing between blocks, especially for dynamic fields whose values may be longer than expected.

### Use Dynamic Fields for Document Data

Use static text only for fixed wording.

Use dynamic fields for values that come from the Dunning Letter document, such as customer, dates, amount, company, or contact details.

### Preview Before Finalizing

Always preview before finalizing.

Check:

- Text alignment.
- Field placement.
- Image scale.
- Page spacing.
- Missing or incorrect fields.
- Content overflow.

### Keep the PDF Simple

The reference PDF should be a clean one-page visual guide.

Avoid using large, scanned, protected, or multi-page files.

## Troubleshooting

### Builder Does Not Open

Check:

- You are logged in as Administrator.
- The `gpf_builder` app is installed.
- The route is `/app/gpf-builder`.
- Browser console has no missing asset errors for Konva or PDF.js.

### PDF Upload Fails

Possible causes:

- File is not a PDF.
- File is public instead of private.
- File is larger than 2 MB.
- File has more than one page.
- File is password-protected.
- File is corrupted.

### PDF Does Not Appear on Canvas

Check:

- The PDF was uploaded successfully.
- The status bar shows the PDF name.
- The PDF file URL is accessible to the logged-in Administrator.
- Browser console has no PDF.js rendering errors.

### Field Block Does Not Save

Check:

- The block type is `Dynamic Field`.
- The fieldname exists in the allowed field list.
- The field is a supported data-style field.
- The fieldname has no spelling error.

### Static Text Block Does Not Save

Static Text blocks cannot be empty.

Enter text or delete the block.

### OCR Cannot Run

Check:

- A PDF reference is uploaded.
- OCR provider configuration is available.
- Rate limits have not been exceeded.
- The PDF belongs to the active setup.

### Finalization Fails Because of OCR

Confirm every OCR result referenced by an OCR Text block.

Remove unused OCR blocks or clear invalid OCR references.

### Finalization Fails Because Blocks Overlap

Move or resize the overlapping blocks.

Finalization blocks overlapping rectangles, even if their text does not visually collide.

### Output Button Fails

Check:

- The setup is finalized.
- At least one block exists.
- The layout saved successfully before finalization.

## Limitations

Current limitations:

- The builder targets the `Dunning Letter` DocType.
- PDF references must be single-page PDFs.
- PDF references must be private files.
- PDF references are limited to 2 MB.
- Finalization blocks overlapping layout rectangles.
- Preview uses redacted sample data, not a real Dunning Letter record.
- The builder is restricted to Administrator access.
- Advanced styling is stored internally as sanitized style JSON; the current UI exposes core placement and content fields.

## Quick Reference

### Normal Build Flow

```text
Open Builder
Upload PDF
Add Blocks
Set Properties
Save
Preview
Adjust
Save
Finalize
Generate Output
```

### Block Types

| Block Type | Use For |
| --- | --- |
| `Static Text` | Fixed text printed exactly as entered. |
| `Dynamic Field` | Values from the Dunning Letter document. |
| `OCR Text` | Confirmed OCR text from the reference PDF. |
| `Image` | General image assets. |
| `Branding` | Logos, letterhead, stamps, signatures, or brand assets. |

### Main Statuses

| Status | Meaning |
| --- | --- |
| `Editing` | Layout can be changed. |
| `Finalized` | Layout is locked for production output. |
