# Testing Plan

## 1. Test Input Summary

### Confirmed information

This Testing Plan is for the **Frappe 14 PDF Reference to Print Format Builder for Warning Letters**. The approved Waterfall sequence places this work at **Stage 5 — Testing Planning**, after Requirements, System Analysis, System Design, and Implementation Planning. The Waterfall rules require every stage to include a stage gate checklist and not to change approved requirements. 

The MVP scope includes Administrator-only access, one single-page warning letter PDF reference, manual layout block creation, editable blocks, field mapping, multilingual text, Google Vision OCR as assistive only, sample-data preview, side-by-side visual comparison, 90% Administrator-confirmed similarity, existing branding file selection, one saved reusable Print Format, autonaming, version history, and copy-ready Frappe Print Format output. 

The approved analysis defines the main user workflows: access, PDF upload, layout creation/editing, OCR review and confirmation, field mapping, branding selection, preview comparison, save, finalize, output generation, and version history. 

The approved design hard-restricts the target DocType to **`Dunning Letter`**, separates save from finalization, locks finalized setup until return-to-editing, treats preview/output as XSS-sensitive, defines SVG sanitization, rate limits, audit controls, and server-side validation/finalization services. 

The approved implementation plan requires tests for end-to-end workflow, access control, object-level authorization, finalized-state bypass, sanitizers, rate limits, log redaction, Google Vision secret exposure, private file access, output compatibility, and performance smoke checks. 

### Assumptions

1. Testing will use Frappe’s standard test framework and a controlled Frappe 14 test site.
2. Google Vision OCR will be tested with mocked provider responses for repeatable automated tests, plus one controlled integration test where credentials are available.
3. The exact maximum PDF upload size is configurable and must be supplied before production readiness testing.
4. Visual similarity is manually confirmed by the built-in Frappe `Administrator` user for MVP, not automatically scored.

### Open questions

1. Exact PDF upload size limit must be confirmed before final execution.
2. Exact available fields on the production `Dunning Letter` DocType must be confirmed in the test environment.
3. Business deletion approval workflow remains operationally defined later and should not block functional QA unless deletion behavior is implemented.

---

## 2. Test Strategy

Testing will verify that the implemented system satisfies the approved requirements and design without changing scope, redesigning workflows, or adding production code.

Testing levels:

| Level             | Purpose                                                                                                                            |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Unit tests        | Verify service-level business rules, validators, sanitizers, state rules, and error handling.                                      |
| Integration tests | Verify APIs, DocTypes, Frappe ORM, private files, Google Vision adapter, permissions, and service orchestration.                   |
| System tests      | Verify complete workflows from PDF upload through final output and version history.                                                |
| UAT               | Verify the Administrator can use the system according to approved workflows.                                                       |
| Regression tests  | Protect Administrator-only access, single setup, one-page PDF, confirmed OCR, finalized locking, and copy-ready output behavior.   |
| Security tests    | Verify access control, object scoping, private files, sanitizer, rate limits, secrets, safe errors, and log redaction.             |
| Performance tests | Verify MVP payloads complete within accepted local benchmark thresholds, especially PDF rendering, preview, and output generation. |

Test evidence must include pass/fail result, test data used, requirement/design trace, expected result, actual result, and defect reference where failed.

---

## 3. Test Scope

In scope:

1. Built-in Frappe `Administrator` only access.
2. Rejection of Guest, non-Administrator, System Manager, and custom-role users.
3. One active reusable setup only.
4. `Dunning Letter` hard restriction.
5. Single-page private PDF reference upload and validation.
6. Manual layout blocks: create, move, resize, align, duplicate, delete.
7. Static text, dynamic field, OCR text, image, and branding block behavior.
8. Multilingual text handling.
9. Google Vision OCR assistance, unconfirmed state, review, edit, and confirmation.
10. Existing branding file selection: PNG, JPG, JPEG, sanitized SVG only.
11. WEBP and PDF branding rejection.
12. Preview generation with auto-generated sample data.
13. Side-by-side preview comparison.
14. Administrator-confirmed 90% visual similarity.
15. Save and version history creation.
16. Finalization readiness validation.
17. Finalized-state locking.
18. Return-to-editing invalidation.
19. Copy-ready Frappe Print Format HTML/CSS/Jinja output.
20. Sanitized preview and generated output.
21. Rate limits for upload, OCR, preview, save, finalize, output, and return-to-editing. The design defines limits including upload 5/hour, OCR 3/hour, preview 30/hour, save 60/hour, finalize 10/hour, output 30/hour, and return-to-editing 5/hour. 
22. Audit logging, safe error messages, redaction, and private file access.

---

## 4. Out of Scope

The following must not be tested as supported behavior because they are outside approved MVP scope:

1. Non-Administrator access.
2. Multi-user workflow.
3. Draft/review/approved workflow states.
4. Multi-page PDF support.
5. Lampiran pages.
6. Invoice attachment pages.
7. Batch generation.
8. Multiple saved Print Formats.
9. Fully automatic PDF-to-layout conversion.
10. Pixel-perfect conversion guarantee.
11. Use of OCR output without Administrator confirmation.
12. New branding upload workflow.
13. Rollback from version history.
14. Arbitrary DocType support.
15. Production deployment approval.

---

## 5. Unit Test Cases

| ID     | Trace                               | Test case                                                                              | Expected result                                                                                                  |
| ------ | ----------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| UT-001 | FR-001–FR-005, AccessControlService | Validate built-in `Administrator` user.                                                | Access allowed only when `frappe.session.user == "Administrator"`.                                               |
| UT-002 | FR-001–FR-005                       | Validate Guest user.                                                                   | Access denied with safe error code/message.                                                                      |
| UT-003 | FR-001–FR-005                       | Validate authenticated non-Administrator.                                              | Access denied.                                                                                                   |
| UT-004 | FR-001–FR-005                       | Validate System Manager user who is not built-in `Administrator`.                      | Access denied.                                                                                                   |
| UT-005 | FR-044–FR-048, DD-006               | Setup service returns one active MVP setup.                                            | Exactly one active setup is returned; duplicate active setup condition is rejected.                              |
| UT-006 | DD-003                              | Target DocType validator receives `Dunning Letter`.                                    | Accepted.                                                                                                        |
| UT-007 | DD-003                              | Target DocType validator receives any other DocType.                                   | Rejected with `INVALID_TARGET_DOCTYPE`.                                                                          |
| UT-008 | FR-006–FR-012                       | PDF validator receives valid one-page PDF.                                             | Accepted.                                                                                                        |
| UT-009 | FR-010                              | PDF validator receives multi-page PDF.                                                 | Rejected.                                                                                                        |
| UT-010 | FR-006                              | PDF validator receives non-PDF extension/MIME/content.                                 | Rejected.                                                                                                        |
| UT-011 | FR-006                              | PDF validator receives corrupted PDF.                                                  | Rejected with safe error.                                                                                        |
| UT-012 | FR-006                              | PDF validator receives encrypted/protected PDF.                                        | Rejected.                                                                                                        |
| UT-013 | FR-007, security design             | PDF storage validator receives public file.                                            | Rejected; PDF reference must be private.                                                                         |
| UT-014 | FR-013–FR-019                       | Layout block validator receives positive width/height within page bounds.              | Accepted.                                                                                                        |
| UT-015 | FR-013–FR-019                       | Layout block has zero/negative width or height.                                        | Rejected.                                                                                                        |
| UT-016 | FR-013–FR-019                       | Layout block coordinates outside page bounds.                                          | Rejected or validation issue returned according to design.                                                       |
| UT-017 | Validation Design                   | Blank spacer block is submitted.                                                       | Rejected.                                                                                                        |
| UT-018 | Finalization Design                 | Overlapping blocks exist at finalization.                                              | Finalization blocked.                                                                                            |
| UT-019 | FR-020–FR-024                       | Dynamic field maps to valid `Dunning Letter` field.                                    | Accepted.                                                                                                        |
| UT-020 | FR-020–FR-024                       | Dynamic field maps to removed or invalid field.                                        | Rejected.                                                                                                        |
| UT-021 | DD-005                              | Same `Dunning Letter` field is used in duplicate dynamic blocks.                       | Accepted because duplicate field usage is allowed.                                                               |
| UT-022 | FR-025–FR-027                       | Static text includes English, Malay, and Unicode characters.                           | Text is stored and rendered safely without corruption.                                                           |
| UT-023 | FR-028–FR-033                       | OCR result is created after OCR run.                                                   | Stored as unconfirmed by default.                                                                                |
| UT-024 | FR-031–FR-032                       | OCR confirmation service receives edited text.                                         | Normalized text is stored with confirmation metadata.                                                            |
| UT-025 | FR-032                              | OCR text used before confirmation.                                                     | Finalization/output use is blocked.                                                                              |
| UT-026 | FR-034–FR-037, BR-014               | Branding validator receives existing PNG/JPG/JPEG.                                     | Accepted.                                                                                                        |
| UT-027 | Security Design                     | Branding validator receives safe sanitized SVG.                                        | Accepted after sanitizer passes.                                                                                 |
| UT-028 | Security Design                     | SVG contains script tag.                                                               | Rejected as unsafe.                                                                                              |
| UT-029 | Security Design                     | SVG contains event handler, external reference, `javascript:` URL, or `foreignObject`. | Rejected.                                                                                                        |
| UT-030 | FR-034–FR-037                       | Branding validator receives WEBP.                                                      | Rejected.                                                                                                        |
| UT-031 | FR-034–FR-037                       | Branding validator receives PDF.                                                       | Rejected.                                                                                                        |
| UT-032 | FR-038–FR-043                       | Preview service receives valid setup and sample data.                                  | Sanitized preview HTML is generated.                                                                             |
| UT-033 | Security Design                     | Static text contains XSS payload.                                                      | Encoded in preview/output.                                                                                       |
| UT-034 | Security Design                     | OCR text contains XSS payload.                                                         | Encoded in preview/output.                                                                                       |
| UT-035 | Security Design                     | Dynamic field sample contains XSS payload.                                             | Escaped in preview/output.                                                                                       |
| UT-036 | FR-046, BR-019                      | Output generator builds Print Format output.                                           | Output uses allowlisted HTML/CSS/Jinja and no arbitrary JavaScript.                                              |
| UT-037 | DD-008                              | Save attempted when setup is finalized.                                                | Rejected unless returned to Editing.                                                                             |
| UT-038 | DD-008                              | Return-to-editing service executes.                                                    | Status becomes Editing; final output validity, preview readiness, and similarity confirmation are invalidated.   |
| UT-039 | FR-049–FR-051                       | Version history entry created on save/finalize/return-to-editing.                      | Immutable snapshot record is created.                                                                            |
| UT-040 | Logging Design                      | Audit log message contains credential/private path/OCR text.                           | Sensitive values are redacted.                                                                                   |
| UT-041 | Error Handling Design               | Service raises internal exception.                                                     | API-safe stable error response contains no stack trace, secrets, private path, OCR payload, or generated output. |
| UT-042 | RateLimitService                    | Configured endpoint exceeds rate limit.                                                | Request blocked with `RATE_LIMITED` or endpoint-specific rate-limit code.                                        |

---

## 6. Integration Test Cases

| ID     | Trace               | Test case                                                                | Expected result                                                                                                                            |
| ------ | ------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| IT-001 | P1-T01–P1-T07       | Run migrations on clean test site.                                       | Required DocTypes, fields, indexes, permissions, and one active setup are created idempotently.                                            |
| IT-002 | P1-T06              | Guest reads/writes custom DocTypes directly.                             | Denied.                                                                                                                                    |
| IT-003 | P1-T06              | Non-Administrator reads/writes custom DocTypes directly.                 | Denied.                                                                                                                                    |
| IT-004 | P1-T06              | System Manager reads/writes custom DocTypes directly.                    | Denied unless exactly built-in `Administrator`.                                                                                            |
| IT-005 | API Design          | Guest calls every whitelisted API.                                       | Rejected; no `allow_guest=True` exposure.                                                                                                  |
| IT-006 | API Design          | Non-Administrator calls every API.                                       | Rejected.                                                                                                                                  |
| IT-007 | API Design          | Administrator uploads valid private one-page PDF through API.            | File is linked to active setup and displayed as visual reference.                                                                          |
| IT-008 | FR-010              | Administrator uploads multi-page PDF through API.                        | Rejected; setup PDF reference remains unchanged.                                                                                           |
| IT-009 | API Security        | API receives setup name that is not active MVP setup.                    | Rejected by object-level scoping.                                                                                                          |
| IT-010 | API Security        | OCR result from another setup is submitted for confirmation.             | Rejected.                                                                                                                                  |
| IT-011 | API Security        | Branding file reference from inaccessible/deleted file is submitted.     | Rejected.                                                                                                                                  |
| IT-012 | FR-020–FR-024       | `get_dunning_letter_fields` API is called.                               | Returns fields for `Dunning Letter` only; arbitrary DocType cannot be requested.                                                           |
| IT-013 | FR-028–FR-033       | OCR API with missing Google Vision config.                               | Fails safely with `OCR_NOT_CONFIGURED`; no secret/path exposure.                                                                           |
| IT-014 | FR-028–FR-033       | OCR provider failure is simulated.                                       | Safe error returned; audit event created; Administrator may continue manually.                                                             |
| IT-015 | FR-031–FR-032       | OCR confirm API stores normalized text.                                  | Confirmation metadata shows built-in `Administrator`.                                                                                      |
| IT-016 | FR-038–FR-043       | Generate preview API after valid blocks and mappings.                    | Sanitized preview returned with sample data.                                                                                               |
| IT-017 | FR-042–FR-043       | Similarity confirmation API is submitted by Administrator.               | Confirmation persists server-side.                                                                                                         |
| IT-018 | FR-044–FR-051       | Save layout API updates the single reusable setup.                       | Version history entry is created; no second reusable setup is created.                                                                     |
| IT-019 | Finalization Design | Finalize API with all readiness conditions met.                          | Setup becomes Finalized; output can be generated.                                                                                          |
| IT-020 | Finalization Design | Finalize API with missing preview/similarity/OCR confirmation/mapping.   | Finalization blocked with validation errors.                                                                                               |
| IT-021 | DD-008              | Direct API mutation after finalization.                                  | Rejected for upload, save, OCR, branding, and layout mutation endpoints.                                                                   |
| IT-022 | DD-008              | Return-to-editing API.                                                   | Setup returns to Editing and invalidates final output, preview readiness, and similarity confirmation.                                     |
| IT-023 | FR-046              | Generate output API when finalized and valid.                            | Copy-ready Frappe Print Format output is returned.                                                                                         |
| IT-024 | FR-046              | Generate output when not finalized or output invalidated.                | Rejected.                                                                                                                                  |
| IT-025 | Logging Design      | Protected events are performed.                                          | Audit events are created for upload, OCR, save, finalize, return-to-editing, output generation, rate-limit hit, and unsafe content block.  |
| IT-026 | P6-T07              | Logs and errors after failures.                                          | No credentials, raw files, full OCR text, full private paths, full warning-letter content, or generated output outside approved snapshots. |
| IT-027 | P6-T09              | Unauthorized user requests private PDF URL or app path.                  | File retrieval denied.                                                                                                                     |
| IT-028 | P6-T10              | Generated output is inserted into Frappe Print Format render smoke test. | Renders without prohibited constructs.                                                                                                     |

---

## 7. System Test Cases

| ID     | Trace                      | Test case                                                                                                                                                                                                                                         | Expected result                                                                              |
| ------ | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| ST-001 | Core Features 1–16, P6-T01 | Full happy path: Administrator logs in, uploads valid one-page PDF, creates blocks, maps fields, runs OCR, confirms OCR, selects branding, generates preview, confirms 90% similarity, saves, finalizes, generates output, views version history. | End-to-end workflow succeeds with copy-ready output and version history.                     |
| ST-002 | Workflow 1                 | Unauthorized user opens app.                                                                                                                                                                                                                      | Access denied screen/message; no data exposed.                                               |
| ST-003 | Workflow 2                 | Administrator uploads invalid PDF types: non-PDF, corrupted, protected, multi-page, oversized.                                                                                                                                                    | Each is rejected safely; no invalid reference stored.                                        |
| ST-004 | Workflow 3–4               | Administrator creates and edits each block type.                                                                                                                                                                                                  | Blocks can be drawn, moved, resized, aligned, duplicated, and deleted; saved state persists. |
| ST-005 | Workflow 5                 | Administrator enters multilingual static text.                                                                                                                                                                                                    | Text displays correctly in editor, preview, saved layout, and output.                        |
| ST-006 | Workflow 6                 | OCR succeeds but text remains unconfirmed.                                                                                                                                                                                                        | OCR text is visibly unconfirmed and cannot be used in final output until confirmed.          |
| ST-007 | Workflow 6                 | OCR fails.                                                                                                                                                                                                                                        | Administrator receives safe failure message and can continue manually.                       |
| ST-008 | Workflow 7                 | Administrator maps valid dynamic fields.                                                                                                                                                                                                          | Preview/output use mapped fields from `Dunning Letter`.                                      |
| ST-009 | Workflow 8                 | Administrator selects existing valid branding file.                                                                                                                                                                                               | Branding renders in preview and output.                                                      |
| ST-010 | Workflow 9                 | Preview generated with valid sample data.                                                                                                                                                                                                         | Side-by-side comparison with original PDF reference is displayed.                            |
| ST-011 | FR-043                     | Non-pixel-perfect warning is shown.                                                                                                                                                                                                               | UI clearly communicates that output is not automatic or pixel-perfect conversion.            |
| ST-012 | Workflow 10                | Administrator saves incomplete layout.                                                                                                                                                                                                            | Save succeeds when allowed; version history entry is created; setup remains editable.        |
| ST-013 | Workflow 11                | Administrator finalizes incomplete setup.                                                                                                                                                                                                         | Finalization blocked with actionable validation messages.                                    |
| ST-014 | Workflow 11                | Administrator finalizes complete setup.                                                                                                                                                                                                           | Setup is locked as Finalized.                                                                |
| ST-015 | Workflow 12                | Administrator generates final output.                                                                                                                                                                                                             | Read-only copy-ready output is displayed only after valid finalization.                      |
| ST-016 | Workflow 13                | Administrator views version history.                                                                                                                                                                                                              | Version entries show metadata and snapshots; no rollback action is available.                |
| ST-017 | DD-008                     | Administrator returns finalized setup to Editing.                                                                                                                                                                                                 | Previous final output is invalidated and new preview/similarity/finalization are required.   |
| ST-018 | FR-044–FR-048              | Repeated saves.                                                                                                                                                                                                                                   | Existing reusable setup is updated; no multiple saved formats are created.                   |

---

## 8. User Acceptance Test Cases

Primary UAT actor: built-in Frappe `Administrator`.

| ID      | Trace                       | UAT scenario                                               | Acceptance criteria                                                                                                                |
| ------- | --------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| UAT-001 | FR-001–FR-005               | Administrator opens the builder.                           | App opens successfully; non-Administrators cannot access it.                                                                       |
| UAT-002 | FR-006–FR-012               | Administrator uploads one warning letter PDF.              | One-page PDF is accepted and displayed as visual reference.                                                                        |
| UAT-003 | FR-013–FR-019               | Administrator manually recreates the layout using blocks.  | Blocks support draw, drag, resize, align, duplicate, delete, and type assignment.                                                  |
| UAT-004 | FR-020–FR-024               | Administrator maps dynamic fields.                         | Only valid `Dunning Letter` fields are selectable; incomplete required mappings block finalization.                                |
| UAT-005 | FR-025–FR-027               | Administrator enters multilingual text.                    | English/Malay/Unicode text is stored and previewed correctly.                                                                      |
| UAT-006 | FR-028–FR-033               | Administrator uses OCR assistance.                         | OCR text is reviewed, edited if needed, and confirmed before final use.                                                            |
| UAT-007 | FR-034–FR-037               | Administrator selects existing branding assets.            | Existing PNG/JPG/JPEG/safe SVG files can be selected; unsupported assets are rejected.                                             |
| UAT-008 | FR-038–FR-043               | Administrator generates preview and compares side-by-side. | Preview displays next to PDF reference and includes sample data, static text, dynamic fields, confirmed OCR, images, and branding. |
| UAT-009 | FR-042                      | Administrator confirms visual 90% similarity.              | Similarity confirmation is saved server-side.                                                                                      |
| UAT-010 | FR-043, BR-020              | Administrator sees limitation warning.                     | UI states the system does not guarantee pixel-perfect automatic PDF conversion.                                                    |
| UAT-011 | FR-044–FR-048               | Administrator saves reusable setup.                        | One reusable setup is saved with autonaming and remains the only reusable format.                                                  |
| UAT-012 | FR-049–FR-051               | Administrator reviews version history.                     | Saved/finalized changes are traceable.                                                                                             |
| UAT-013 | FR-005, Finalization Design | Administrator finalizes complete setup.                    | Setup is locked and output generation becomes available.                                                                           |
| UAT-014 | FR-046                      | Administrator copies final output.                         | Output is copy-ready for Frappe Print Format.                                                                                      |
| UAT-015 | DD-008                      | Administrator returns setup to Editing.                    | Output is invalidated and finalization requirements must be satisfied again.                                                       |

---

## 9. Regression Test Cases

| ID     | Trace            | Regression case                                                 | Expected result                                                 |
| ------ | ---------------- | --------------------------------------------------------------- | --------------------------------------------------------------- |
| RT-001 | FR-001–FR-005    | Re-run full access-control matrix after any auth/API/UI change. | Only built-in `Administrator` has access.                       |
| RT-002 | FR-006–FR-012    | Re-run PDF validation after file-handling change.               | Only valid private one-page PDF accepted.                       |
| RT-003 | FR-013–FR-019    | Re-run layout block manipulation after UI/canvas changes.       | Draw, drag, resize, align, duplicate, delete still work.        |
| RT-004 | FR-020–FR-024    | Re-run field mapping after DocType metadata changes.            | Only `Dunning Letter` fields accepted.                          |
| RT-005 | FR-028–FR-033    | Re-run OCR confirmation tests after OCR adapter changes.        | OCR remains assistive and unconfirmed until reviewed.           |
| RT-006 | Security Design  | Re-run SVG and output sanitizer tests after rendering changes.  | Unsafe payloads blocked/encoded.                                |
| RT-007 | FR-038–FR-043    | Re-run preview after sample data/rendering changes.             | Preview renders safely and side-by-side.                        |
| RT-008 | FR-044–FR-048    | Re-run single reusable setup tests after save logic changes.    | No multiple saved formats.                                      |
| RT-009 | FR-049–FR-051    | Re-run version history tests after snapshot changes.            | Traceability remains intact; no rollback action appears.        |
| RT-010 | DD-008           | Re-run finalized-state bypass tests after API/service changes.  | Finalized setup cannot be mutated except via return-to-editing. |
| RT-011 | Logging Design   | Re-run redaction tests after logging/error changes.             | Sensitive data remains excluded.                                |
| RT-012 | RateLimitService | Re-run rate-limit tests after config changes.                   | Limits remain enforced.                                         |
| RT-013 | FR-046           | Re-run output compatibility after output generator changes.     | Output remains copy-ready and safe.                             |

---

## 10. Security Test Cases

The design and implementation plan require security testing for Administrator-only access, no guest APIs, object-level scoping, `Dunning Letter` restriction, private files, rate limits, sanitization, secrets, logging, finalized-state locking, and safe output. 

| ID      | Trace                  | Security test                                                                                 | Expected result                                                                                                                            |
| ------- | ---------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| SEC-001 | FR-001–FR-005          | Unauthorized user cannot access protected routes.                                             | Guest, non-Administrator, System Manager, and custom-role users are denied.                                                                |
| SEC-002 | API Security           | Guest cannot access any whitelisted API.                                                      | All API calls rejected; no guest method exposure.                                                                                          |
| SEC-003 | API Security           | Missing session/token is used for protected API call.                                         | Rejected with safe auth error.                                                                                                             |
| SEC-004 | API Security           | Expired session/token is used.                                                                | Rejected with safe auth error.                                                                                                             |
| SEC-005 | Object-level scoping   | User/API references setup not belonging to active MVP setup.                                  | Rejected.                                                                                                                                  |
| SEC-006 | Object-level scoping   | User A cannot access User B’s data.                                                           | Rejected at API, service, and DocType levels. In this MVP, all non-Administrator users are denied entirely.                                |
| SEC-007 | DD-003                 | API attempts arbitrary DocType metadata access.                                               | Rejected; only `Dunning Letter` allowed.                                                                                                   |
| SEC-008 | DD-003                 | Jinja output references non-`Dunning Letter` field.                                           | Rejected or stripped by output validation.                                                                                                 |
| SEC-009 | File Security          | Uploaded PDF reference is public.                                                             | Rejected; private file storage required.                                                                                                   |
| SEC-010 | File Security          | Unauthorized user accesses private PDF URL/path.                                              | Denied.                                                                                                                                    |
| SEC-011 | File Security          | Unauthorized user accesses private branding file.                                             | Denied.                                                                                                                                    |
| SEC-012 | SVG Sanitizer          | SVG contains `<script>`.                                                                      | Rejected.                                                                                                                                  |
| SEC-013 | SVG Sanitizer          | SVG contains event handlers such as `onload`.                                                 | Rejected.                                                                                                                                  |
| SEC-014 | SVG Sanitizer          | SVG contains external reference, `data:`, `javascript:`, embedded object, or `foreignObject`. | Rejected.                                                                                                                                  |
| SEC-015 | Output Sanitizer       | Static text contains XSS payload.                                                             | Encoded; no executable script.                                                                                                             |
| SEC-016 | Output Sanitizer       | OCR text contains XSS payload.                                                                | Encoded; no executable script.                                                                                                             |
| SEC-017 | Output Sanitizer       | Dynamic field sample contains XSS payload.                                                    | Escaped.                                                                                                                                   |
| SEC-018 | Output Sanitizer       | Generated output contains arbitrary JavaScript.                                               | Blocked with `OUTPUT_UNSAFE` or equivalent safe error.                                                                                     |
| SEC-019 | Business Rule          | Frontend attempts to manipulate XP value.                                                     | Not applicable to this approved project because no XP feature exists. Test status: **N/A — requirement not present**.                      |
| SEC-020 | Business Rule          | Duplicate habit completion does not award duplicate XP.                                       | Not applicable to this approved project because no habit/XP feature exists. Test status: **N/A — requirement not present**.                |
| SEC-021 | Validation             | Invalid input is submitted to each mutating API.                                              | Rejected with stable safe error; no partial unsafe write.                                                                                  |
| SEC-022 | Error Handling         | Internal exception occurs.                                                                    | API returns safe error message with no stack trace, secrets, private paths, OCR payloads, or generated output.                             |
| SEC-023 | Authorization          | Admin-only endpoint is called by normal user.                                                 | Rejected.                                                                                                                                  |
| SEC-024 | Secrets                | Google Vision credentials missing.                                                            | Fails safely with `OCR_NOT_CONFIGURED`; no secret exposure.                                                                                |
| SEC-025 | Secrets                | Google Vision credentials invalid.                                                            | Safe failure; credentials not returned/logged.                                                                                             |
| SEC-026 | Secrets                | Inspect frontend bundle/API responses/logs/snapshots.                                         | Secrets are not exposed in frontend, responses, logs, or snapshots.                                                                        |
| SEC-027 | Rate Limits            | Upload limit exceeded.                                                                        | Request blocked.                                                                                                                           |
| SEC-028 | Rate Limits            | OCR limit exceeded.                                                                           | Request blocked.                                                                                                                           |
| SEC-029 | Rate Limits            | Preview/save/finalize/output/return-to-editing limits exceeded.                               | Request blocked with rate-limit error.                                                                                                     |
| SEC-030 | Finalized Locking      | Direct API save/upload/OCR/branding/layout mutation after finalization.                       | Rejected.                                                                                                                                  |
| SEC-031 | Audit Logging          | Unauthorized attempts and unsafe content are triggered.                                       | Audit events are created with sanitized content.                                                                                           |
| SEC-032 | Log Redaction          | Logs inspected after failures.                                                                | No credentials, private paths, raw files, full OCR text, full warning-letter content, or full generated output outside approved snapshots. |
| SEC-033 | Version History Access | Non-Administrator accesses version history.                                                   | Rejected.                                                                                                                                  |
| SEC-034 | CSRF/session           | Mutating request is submitted without valid CSRF/session controls.                            | Rejected according to Frappe session/CSRF behavior.                                                                                        |

Blocking security note: Release must not be approved if SEC-001, SEC-002, SEC-005, SEC-007, SEC-012–SEC-018, SEC-024–SEC-026, SEC-030, or SEC-032 fail.

---

## 11. Performance Test Cases

| ID       | Trace                   | Performance case                                               | Expected result                                                                                    |
| -------- | ----------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| PERF-001 | P6-T11                  | Render one valid single-page PDF reference in browser.         | Completes within accepted local benchmark threshold.                                               |
| PERF-002 | P6-T11                  | Generate preview for representative MVP layout.                | Completes within accepted local benchmark threshold.                                               |
| PERF-003 | P6-T11                  | Generate copy-ready output for representative finalized setup. | Completes within accepted local benchmark threshold.                                               |
| PERF-004 | RateLimitService        | Burst upload requests beyond configured threshold.             | Excess requests blocked; service remains stable.                                                   |
| PERF-005 | RateLimitService        | Burst OCR requests beyond configured threshold.                | Excess requests blocked; no provider abuse.                                                        |
| PERF-006 | Version History Risk    | Save multiple representative layout versions.                  | Version snapshots remain within configured size expectations; no binary files stored in snapshots. |
| PERF-007 | PreviewService          | Preview with maximum expected number of MVP blocks.            | Preview completes without unsafe timeout or browser freeze.                                        |
| PERF-008 | OutputGenerationService | Output generation with multilingual text and branding.         | Output generated safely within benchmark threshold.                                                |

Open performance criterion: exact numeric thresholds should be approved by the project owner or implementation team before final QA execution. Until then, performance tests are smoke tests, not release-grade load tests.

---

## 12. Edge Case Tests

| ID     | Trace               | Edge case                                                                | Expected result                                                                                    |
| ------ | ------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| EC-001 | FR-006–FR-012       | PDF has exactly one page but unusual page size/orientation.              | Accepted if readable and within limits; displayed correctly.                                       |
| EC-002 | FR-006–FR-012       | PDF has one blank page.                                                  | Accepted or warning shown according to validation rules; finalization still requires valid layout. |
| EC-003 | FR-006–FR-012       | PDF has correct extension but wrong MIME/content.                        | Rejected.                                                                                          |
| EC-004 | FR-013–FR-019       | Block positioned at page boundary.                                       | Accepted if fully within bounds.                                                                   |
| EC-005 | FR-013–FR-019       | Very small but positive block.                                           | Accepted or warned according to validation rules; zero/negative rejected.                          |
| EC-006 | Analysis Workflow   | Text overflow inside block.                                              | Warning shown; no automatic modification without Administrator action.                             |
| EC-007 | FR-025–FR-027       | Malay characters, punctuation, diacritics, and mixed English/Malay text. | Stored/rendered correctly.                                                                         |
| EC-008 | FR-031–FR-032       | OCR text edited to empty.                                                | Rejected if used as required output content; otherwise handled according to validation rules.      |
| EC-009 | FR-020–FR-024       | Previously valid field removed from `Dunning Letter`.                    | Mapping marked invalid; finalization blocked.                                                      |
| EC-010 | DD-005              | Duplicate dynamic field blocks.                                          | Allowed.                                                                                           |
| EC-011 | Finalization Design | Blocks overlap before finalization.                                      | Finalization blocked.                                                                              |
| EC-012 | FR-034–FR-037       | Existing branding file deleted after selection.                          | Preview/finalization warns or blocks until valid replacement selected.                             |
| EC-013 | FR-034–FR-037       | Sanitized SVG becomes unsafe after file replacement.                     | Preview/output/finalization blocked.                                                               |
| EC-014 | FR-038–FR-043       | Preview generated, then layout changed.                                  | Previous preview/similarity should no longer satisfy finalization if invalidated by design.        |
| EC-015 | DD-008              | Return-to-editing after output generated.                                | Output invalidated.                                                                                |
| EC-016 | FR-049–FR-051       | Many saves in sequence.                                                  | Sequential version numbers remain correct and traceable.                                           |
| EC-017 | Logging Design      | Error contains sensitive values.                                         | Sensitive values redacted.                                                                         |
| EC-018 | RateLimitService    | Rate limit window boundary.                                              | Calls just within limit pass; calls over limit fail.                                               |

---

## 13. Negative Test Cases

| ID     | Trace                 | Negative case                                                    | Expected result                                                   |
| ------ | --------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------- |
| NT-001 | FR-001–FR-005         | Guest opens builder route.                                       | Access denied.                                                    |
| NT-002 | FR-001–FR-005         | Non-Administrator calls upload API.                              | Access denied.                                                    |
| NT-003 | FR-006–FR-012         | Upload multi-page PDF.                                           | Rejected.                                                         |
| NT-004 | FR-006–FR-012         | Upload Lampiran or invoice attachment PDF as supported workflow. | Rejected or not supported; MVP supports warning letter page only. |
| NT-005 | FR-006–FR-012         | Upload public PDF reference.                                     | Rejected.                                                         |
| NT-006 | FR-013–FR-019         | Save block with missing block type.                              | Rejected.                                                         |
| NT-007 | FR-013–FR-019         | Save block outside page.                                         | Rejected.                                                         |
| NT-008 | FR-013–FR-019         | Save blank spacer block.                                         | Rejected.                                                         |
| NT-009 | FR-020–FR-024         | Map dynamic block to arbitrary DocType field.                    | Rejected.                                                         |
| NT-010 | FR-024                | Finalize with incomplete required mappings.                      | Blocked.                                                          |
| NT-011 | FR-032                | Finalize with unconfirmed OCR text used in block.                | Blocked.                                                          |
| NT-012 | FR-034–FR-037         | Select WEBP branding file.                                       | Rejected.                                                         |
| NT-013 | FR-034–FR-037         | Select PDF as branding file.                                     | Rejected.                                                         |
| NT-014 | Security Design       | Select unsafe SVG.                                               | Rejected.                                                         |
| NT-015 | FR-038–FR-043         | Finalize without preview.                                        | Blocked.                                                          |
| NT-016 | FR-042                | Finalize without Administrator 90% similarity confirmation.      | Blocked.                                                          |
| NT-017 | DD-008                | Edit finalized setup by direct API.                              | Rejected.                                                         |
| NT-018 | FR-046                | Generate output before finalization.                             | Rejected.                                                         |
| NT-019 | FR-044–FR-048         | Create second reusable Print Format.                             | Rejected or prevented.                                            |
| NT-020 | Error Handling Design | Send malformed JSON/request shape.                               | Rejected with safe stable error.                                  |
| NT-021 | Security Design       | Inject JavaScript in static/OCR/dynamic content.                 | Encoded or blocked.                                               |
| NT-022 | Logging Design        | Force provider failure containing secret-like text.              | Secret-like values not logged or returned.                        |
| NT-023 | RateLimitService      | Exceed endpoint limits.                                          | Rejected with rate-limit response.                                |

---

## 14. Test Data

| Data item                                      | Purpose                                                                                                                  |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Built-in `Administrator` user                  | Positive authorization tests and UAT.                                                                                    |
| Guest session                                  | Negative route/API tests.                                                                                                |
| Authenticated normal user                      | Negative authorization tests.                                                                                            |
| System Manager user not named `Administrator`  | Confirms exact built-in Administrator enforcement.                                                                       |
| Custom-role user                               | Confirms custom role does not grant access.                                                                              |
| Valid one-page warning letter PDF              | Happy-path upload, preview, finalization, output.                                                                        |
| Multi-page PDF                                 | Rejection test.                                                                                                          |
| Corrupted PDF                                  | Rejection test.                                                                                                          |
| Password-protected/encrypted PDF               | Rejection test.                                                                                                          |
| Oversized PDF                                  | Rejection test once size limit is configured.                                                                            |
| Public PDF File record                         | Private storage enforcement.                                                                                             |
| Private PDF File record                        | Accepted PDF reference.                                                                                                  |
| Existing PNG/JPG/JPEG branding files           | Valid branding tests.                                                                                                    |
| Safe SVG branding file                         | Sanitizer positive test.                                                                                                 |
| Unsafe SVG files                               | Sanitizer negative tests: script, event handler, external URL, `javascript:`, `data:`, `foreignObject`, embedded object. |
| WEBP branding file                             | Rejection test.                                                                                                          |
| PDF branding file                              | Rejection test.                                                                                                          |
| `Dunning Letter` fixture                       | Dynamic field mapping and output rendering.                                                                              |
| Removed/missing field fixture                  | Invalid mapping tests.                                                                                                   |
| Multilingual text strings                      | English/Malay/Unicode rendering tests.                                                                                   |
| OCR mock response: clean text                  | OCR success test.                                                                                                        |
| OCR mock response: multilingual text           | OCR multilingual support test.                                                                                           |
| OCR mock response: XSS payload                 | Sanitization test.                                                                                                       |
| OCR provider failure response                  | Safe failure and audit test.                                                                                             |
| Sample data fixture                            | Preview rendering tests.                                                                                                 |
| Layout fixture with valid blocks               | Preview/finalization/output happy path.                                                                                  |
| Layout fixture with overlaps                   | Finalization blocked.                                                                                                    |
| Layout fixture with out-of-bounds/blank blocks | Validation failures.                                                                                                     |
| Finalized setup fixture                        | Locking and output tests.                                                                                                |
| Returned-to-editing fixture                    | Invalidation tests.                                                                                                      |
| Secret-like config values                      | Secret exposure/log redaction tests.                                                                                     |

---

## 15. Bug Severity Rules

| Severity | Definition                                                                 | Examples                                                                                                                                                            |
| -------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Critical | Blocks release; security/data integrity failure or core workflow unusable. | Non-Administrator can access app/API; unsafe generated JavaScript executes; finalized setup can be mutated by direct API; private PDF exposed; secrets exposed.     |
| High     | Major requirement failure with no acceptable workaround.                   | Multi-page PDF accepted; unconfirmed OCR can be finalized; arbitrary DocType allowed; output cannot be generated after valid finalization; version history missing. |
| Medium   | Requirement partially fails but workaround exists or limited impact.       | Text overflow warning missing; preview error message unclear; valid branding file rejected incorrectly; rate-limit message inconsistent.                            |
| Low      | Cosmetic, minor usability, documentation, or non-blocking issue.           | Minor label mismatch, alignment issue not affecting validation, harmless copy text inconsistency.                                                                   |

Bug mapping requirement: every defect must map to failed requirement, workflow, business rule, design item, or implementation task.

Release must not be approved with any open Critical defect, any unresolved security High defect, or missing critical security tests.

---

## 16. Pass/Fail Criteria

### Pass criteria

1. All Critical and High test cases pass.
2. All security tests for access control, object scoping, private files, sanitizer, secrets, safe errors, rate limits, log redaction, and finalized-state bypass pass.
3. Full end-to-end system test passes with representative one-page PDF fixture.
4. UAT confirms Administrator can complete upload, layout, OCR confirmation, preview, similarity confirmation, save, finalize, output copy, and version history review.
5. Final output passes Print Format compatibility and sanitizer checks.
6. Version history is created and restricted to built-in `Administrator`.
7. No approved requirement is changed or expanded during testing.
8. Out-of-scope features remain unavailable.

### Fail criteria

1. Any unauthorized user can access protected routes, APIs, DocTypes, private files, version history, or generated output.
2. Arbitrary DocType access is possible.
3. Multi-page PDF is accepted as supported input.
4. OCR can be used in final output without Administrator confirmation.
5. Unsafe SVG, unsafe preview, or unsafe generated output is accepted.
6. Secrets, private paths, OCR payloads, raw files, or sensitive warning-letter content appear in logs/API errors.
7. Finalized setup can be edited without return-to-editing.
8. Output cannot be generated after a valid finalized setup.
9. Required integration, UAT, regression, edge, negative, security, or pass/fail criteria are missing.

---

## 17. Test Completion Checklist

| Checklist item                                       | Status   |
| ---------------------------------------------------- | -------- |
| Requirements traced to test cases                    | Planned  |
| Workflows traced to system/UAT cases                 | Planned  |
| Business rules traced to positive and negative cases | Planned  |
| Design items traced to integration/security cases    | Planned  |
| Unit tests defined                                   | Complete |
| Integration tests defined                            | Complete |
| System tests defined                                 | Complete |
| UAT cases defined                                    | Complete |
| Regression tests defined                             | Complete |
| Security tests defined                               | Complete |
| Performance tests defined                            | Complete |
| Edge cases defined                                   | Complete |
| Negative tests defined                               | Complete |
| Test data defined                                    | Complete |
| Bug severity rules defined                           | Complete |
| Pass/fail criteria defined                           | Complete |
| Blocking release criteria defined                    | Complete |
| Open questions documented                            | Complete |
| No production code written                           | Complete |
| Requirements unchanged                               | Complete |
| System design unchanged                              | Complete |

---

## 18. Stage Gate Checklist

| Stage gate item                               | Status   |
| --------------------------------------------- | -------- |
| Functional test cases are defined             | Complete |
| Integration tests are defined                 | Complete |
| UAT cases are defined                         | Complete |
| Regression tests are defined                  | Complete |
| Edge cases are covered                        | Complete |
| Negative cases are covered                    | Complete |
| Security tests are defined                    | Complete |
| Performance tests are defined                 | Complete |
| Test data is defined                          | Complete |
| Pass/fail criteria are clear                  | Complete |
| Bug severity rules are clear                  | Complete |
| Blocking issues are identified                | Complete |
| Administrator-only access is tested           | Complete |
| `Dunning Letter` hard restriction is tested   | Complete |
| Private file storage is tested                | Complete |
| OCR confirmation requirement is tested        | Complete |
| SVG and output sanitization are tested        | Complete |
| Rate limits are tested                        | Complete |
| Log redaction and safe errors are tested      | Complete |
| Finalized-state locking is tested             | Complete |
| Return-to-editing invalidation is tested      | Complete |
| Copy-ready output compatibility is tested     | Complete |
| Stage 5 output does not change requirements   | Complete |
| Stage 5 output does not redesign the system   | Complete |
| Stage 5 output does not write production code | Complete |

**Stage gate decision:** Testing Planning is complete as a plan, but release is **not approved** until the test suite is implemented, executed, evidenced, and all blocking failures are resolved.


