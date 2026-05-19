# GPF Print Format Builder

GPF Print Format Builder is a custom Frappe 14 app for visually recreating single-page PDF-style documents as Frappe Print Format HTML.

It is intended for administrator-controlled print layouts where writing the full HTML/CSS by hand is slow or error-prone. An Administrator can upload a PDF reference, place editable blocks over it, map blocks to DocType fields, preview the result, save reusable layout templates, and generate copy-ready Print Format HTML.

The builder is a visual authoring tool. It does not automatically convert arbitrary PDFs into perfect print formats.

## What It Does

- Uploads one private, single-page PDF reference.
- Renders the PDF as a visual canvas background.
- Lets an Administrator add and position layout blocks:
  - Static Text
  - Dynamic Field
  - OCR Text
  - Image
  - Branding
- Supports block drag, resize, duplicate, delete, rulers, and fullscreen editing.
- Maps Dynamic Field blocks to fields from the selected target DocType.
- Supports source-document preview values.
- Provides OCR assistance for selectable or scanned PDF text.
- Saves and loads reusable layout templates for the current target DocType.
- Generates preview HTML and final copy-ready Print Format HTML.
- Finalizes a setup to lock production output.
- Keeps audit logs and applies API access controls and rate limits.

## Who This Is For

The app is built for Frappe Administrators who need to reproduce official letter or form layouts in Frappe Print Format.

Access is intentionally restricted. The current MVP assumes the `Administrator` user handles setup, editing, template management, OCR, output generation, and finalization.

## Typical Workflow

1. Open the builder at:

   ```text
   /app/gpf-builder
   ```

2. Select the target DocType and a source document for real preview values.
3. Upload a single-page PDF reference.
4. Add blocks for static text, fields, OCR text, logos, signatures, or other images.
5. Move and resize blocks on the canvas.
6. Save the layout.
7. Preview and adjust until the output matches the reference closely enough.
8. Optionally save the current layout as a reusable template.
9. Finalize the setup when the layout is ready.
10. Generate and copy the final HTML into the intended Frappe Print Format workflow.

For a fuller user-facing guide, see [docs/print_format_builder_user_guide.md](docs/print_format_builder_user_guide.md).

## Main Builder Actions

| Action | Purpose |
| --- | --- |
| `PDF` | Upload the reference PDF. |
| `PDF Text` | Extract selectable PDF text for copy/paste. |
| `Save` | Save the current layout blocks. |
| `Save Template` | Save the current block layout as a named reusable template. |
| `Load Template` | Replace the current layout with a saved template for the active target DocType. |
| `Preview` | Render the current layout as preview HTML. |
| `Output` | Generate copy-ready Print Format HTML. |
| `Text` | Add a Static Text block. |
| `Field` | Add a Dynamic Field block. |
| `OCR Text` | Add an OCR-backed text block. |
| `Image` | Add an image block. |
| `Branding` | Add a branding image block. |
| `Finalize` | Validate and lock the setup. |
| `Return` | Return a finalized setup to editing mode. |

## Installation

From a Frappe bench:

```bash
bench get-app /path/to/gpf_builder
bench --site <site-name> install-app gpf_builder
bench --site <site-name> migrate
bench build --app gpf_builder
bench restart
```

If the app already exists in the bench, usually this is enough after pulling changes:

```bash
bench --site <site-name> migrate
bench build --app gpf_builder
bench restart
```

Frappe 14 asset builds require a compatible Node version. If `bench build` fails with an engine error, update Node to the version required by your Frappe install and rerun the build.

## Configuration

### Active Setup

The app maintains an active `GPF Print Format Setup`. The setup stores:

- Target DocType
- PDF reference
- Editing/finalized status
- Current layout blocks

The patch `gpf_builder.patches.create_active_setup` creates the initial active setup during migration if needed.

### Target DocType

The builder can switch the target DocType from the Source Document panel. Changing target DocType clears incompatible builder state, including current blocks, OCR results, and PDF reference.

### OCR

OCR support depends on the configured OCR provider and dependencies. The app includes Google Vision-related dependencies, but OCR output is treated as assistive text only. Administrators should review and confirm OCR results before using them in final layouts.

### Rate Limits

Rate limits are enforced through `GPF Rate Limit Settings` and `RateLimitService`. They protect expensive or sensitive actions such as PDF upload, OCR, preview generation, layout saving, output generation, and finalization.

## Templates

Layout templates are stored in `GPF Layout Template`.

A template contains a normalized JSON snapshot of layout blocks for one target DocType. Templates are scoped by target DocType so a template made for one DocType cannot be loaded into another DocType.

Template actions:

- `Save Template`: stores the current canvas blocks under a title.
- `Load Template`: replaces the current layout with the selected template.
- `Delete`: removes a saved template.

Loading a template overwrites the current layout blocks after confirmation.

## Development Overview

Important paths:

| Path | Purpose |
| --- | --- |
| `gpf_builder/api/api.py` | Whitelisted API methods called by the page. |
| `gpf_builder/api/guard.py` | Administrator access guard. |
| `gpf_builder/services/layout_service.py` | Layout validation and persistence. |
| `gpf_builder/services/template_service.py` | Layout template validation and persistence. |
| `gpf_builder/services/preview_service.py` | Preview HTML and shared print CSS. |
| `gpf_builder/services/output_service.py` | Final Print Format HTML generation. |
| `gpf_builder/services/pdf_service.py` | PDF validation and file handling. |
| `gpf_builder/services/ocr_service.py` | OCR extraction and normalization. |
| `gpf_builder/services/finalization_service.py` | Finalization and return-to-editing behavior. |
| `gpf_builder/gpf_builder/page/gpf_builder/` | Desk page HTML, JS, CSS. |
| `gpf_builder/gpf_builder/doctype/` | Frappe DocType definitions. |
| `gpf_builder/tests/` | Unit and integration tests. |

The frontend uses Konva for the visual canvas and PDF.js for PDF preview rendering.

## Running Tests

Run the app test suite from the bench:

```bash
bench --site <site-name> run-tests --app gpf_builder
```

Useful targeted tests:

```bash
bench --site <site-name> run-tests --app gpf_builder --module gpf_builder.tests.test_unit_layout_service
bench --site <site-name> run-tests --app gpf_builder --module gpf_builder.tests.test_unit_template_service
bench --site <site-name> run-tests --app gpf_builder --module gpf_builder.tests.test_unit_output_service
bench --site <site-name> run-tests --app gpf_builder --module gpf_builder.tests.test_unit_preview_service
```

## Known Limitations

- Only single-page PDF references are supported.
- The builder is not a full PDF-to-HTML converter.
- OCR is assistive and must be reviewed by an Administrator.
- Final output is HTML/CSS intended for Frappe Print Format workflows.
- The MVP is Administrator-only.
- Layout accuracy depends on careful manual block placement and preview checks.

## Related Documentation

- [docs/print_format_builder_user_guide.md](docs/print_format_builder_user_guide.md)
- [01_requirements.md](01_requirements.md)
- [03_system_design.md](03_system_design.md)
- [04_implementation_plan.md](04_implementation_plan.md)
- [05_testing_plan.md](05_testing_plan.md)
