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

