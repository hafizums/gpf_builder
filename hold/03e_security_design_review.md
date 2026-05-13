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
