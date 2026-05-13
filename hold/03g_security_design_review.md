According to a document from **May 13, 2026**, the latest `03f_system_designer_revised.md` appears to resolve the previous Stage 3 security design blockers. Some older uploads expired, so I based this pass on the latest retrieved `03f` document and the current uploaded security review files.

# Security Audit Report

## 1. Audit Context

**Current review stage:** Waterfall Stage 3 — **System Design Security Review**

**Review result:** **Approved for Stage 4 Implementation Planning**

This is **not deployment or release approval**. It means the design security gate can move forward to implementation planning.

## 2. Documents Reviewed

Reviewed latest available files:

* `03f_system_designer_revised.md`
* `03e_security_design_review.md`
* `03c_security_design_review.md`
* `02b_system_analysis.md`

The `03f` revised design states that the Stage 3 design was updated to reconcile the main system design with the approval addendum and prior security review, including Administrator-only access, `Dunning Letter` hard restriction, SVG sanitization, generated output sanitization, rate limiting, object-level API checks, file limits, retention, secrets, finalized-state locking, and audit log rules. 

## 3. Security Scope

Reviewed:

Authentication, authorization, API permission checks, user data isolation, input validation, abuse prevention, rate limiting, file uploads, secrets and environment variables, logging, error messages, privacy and data retention, deployment configuration, finalized-state locking, and generated output safety.

## 4. Authentication Review

**Status:** Passed

The revised design uses Frappe 14 as a native modular monolith and does not introduce a separate authentication service. It also states that there is no separate frontend app, no separate authentication service, no separate database, and no custom Administrator role. 

## 5. Authorization Review

**Status:** Passed

The revised design resolves the previous authorization conflict. The design now requires built-in Frappe `Administrator` only and removes custom-role access. 

Server-side enforcement is also assigned to `AccessControlService`, which is responsible for enforcing built-in `Administrator` user access only. 

## 6. Input Validation Review

**Status:** Passed for design stage

The design now covers the important validation areas:

* one-page PDF validation
* `Dunning Letter` field validation
* branding file validation
* SVG sanitization
* OCR confirmation
* blank spacer rejection
* overlap blocking
* preview requirement
* similarity confirmation
* output escaping and script prohibition

The design explicitly states these business rules must remain server-side rather than only in UI components. 

## 7. API Security Review

**Status:** Passed for design stage

The revised design addresses prior API concerns by requiring:

* object-level setup scoping on every endpoint
* no guest whitelisted methods
* `Dunning Letter` hard restriction
* server-side finalized-state locking
* built-in Administrator-only access

These were listed as applied security fixes in the revised design. 

## 8. Database Security Review

**Status:** Passed for design stage

The design now includes custom DocTypes for setup, layout blocks, OCR results, version history, and audit events, and it states that all custom DocTypes deny non-Administrator access. 

## 9. Session and Token Security Review

**Status:** Passed with implementation testing required

No separate token model is introduced. Mutating actions should continue to rely on Frappe session and CSRF behavior.

Implementation tests must verify:

* no guest API access
* direct API calls cannot bypass finalized-state rules
* `finalize`, `return_to_editing`, and `generate_output` are protected as sensitive state-changing operations

## 10. Secrets and Configuration Review

**Status:** Passed for design stage

The design now documents Google Vision OCR as backend-only. Credentials must be stored in server-side Frappe site configuration or a deployment secret manager, must not be committed, logged, sent to the client, or included in snapshots, and missing credentials must fail safely with `OCR_NOT_CONFIGURED`. 

The required configuration keys are also defined:

* `google_vision_enabled`
* `google_vision_credentials_path` or secret reference
* `google_vision_project_id`
* `ocr_max_requests_per_hour`
* `ocr_timeout_seconds` 

## 11. File Upload Security Review

**Status:** Passed with implementation testing required

The prior file upload gap is addressed at design level. The revised design says file size and private storage rules are complete in the stage gate checklist. 

The design also includes private Frappe File storage for uploaded PDF references. 

**Implementation condition:** The development plan must convert the file size/storage rules into concrete testable constants and tests.

## 12. Logging and Monitoring Review

**Status:** Passed

The revised design defines what to log and what not to log.

It logs unauthorized access attempts, upload events, OCR events, saves, version snapshots, finalization, return-to-editing, output generation, rate-limit violations, and unsafe SVG/output blocks. It also forbids logging Google Vision credentials, full private paths, full OCR text, full warning-letter content, full generated output except intentional version snapshots, and raw file contents. 

Audit retention and alert thresholds are now defined:

* security audit events: minimum 365 days
* error logs: minimum 90 days
* version history retained with setup unless business deletion is approved
* 5 unauthorized attempts in 10 minutes
* 3 OCR provider failures in 15 minutes
* 5 rate-limit hits in 10 minutes
* any unsafe SVG or unsafe output block event 

## 13. Privacy and Data Retention Review

**Status:** Passed for design stage

The previous retention ambiguity is now listed as mitigated through a defined retention policy and Administrator-only access. 

**Implementation condition:** The “business deletion is approved” rule still needs a concrete operational procedure in Stage 4.

## 14. Rate Limiting and Abuse Prevention Review

**Status:** Passed

The revised design defines rate limits for expensive and mutating endpoints:

| Action            |       Limit |
| ----------------- | ----------: |
| Upload PDF        |  5 per hour |
| Run OCR           |  3 per hour |
| Generate preview  | 30 per hour |
| Save layout       | 60 per hour |
| Finalize          | 10 per hour |
| Generate output   | 30 per hour |
| Return to editing |  5 per hour |

The design states these address the previous rate limiting and abuse prevention finding. 

## 15. Frontend Security Review

**Status:** Passed for design stage

The revised design treats preview/output as XSS-sensitive. It requires static and OCR text to be encoded, dynamic values to be escaped, no arbitrary JavaScript, and HTML/CSS/Jinja allowlists. 

## 16. Backend Security Review

**Status:** Passed for design stage

The revised design separates security-sensitive backend services, including:

* `AccessControlService`
* `PdfReferenceService`
* `FieldMappingService`
* `BrandingAssetService`
* `SvgSanitizerService`
* `OcrService`
* `OutputGenerationService`
* `ValidationService`
* `FinalizationService`
* `VersionHistoryService`
* `AuditLogService`
* `RateLimitService` 

The design also states that access control, finalization validation, SVG sanitization, rate limiting, audit logging, preview generation, and output generation should remain separated. 

## 17. Deployment Security Review

**Status:** Conditionally passed for Stage 4

The design now covers private file storage and Google Vision secret configuration.  

Stage 4 should still include an implementation checklist for:

* HTTPS
* production debug mode disabled
* private file storage verified
* backup access controls
* Google Vision credential injection
* server log access control

## 18. Findings

### Finding 1 — Authorization conflict

**Risk:** Previously High
**Status:** Closed
**Evidence:** The revised design states built-in Administrator only, no custom role access, and no guest whitelisted methods. 

### Finding 2 — Arbitrary DocType access

**Risk:** Previously High
**Status:** Closed
**Evidence:** The revised design hard-restricts the target DocType to `Dunning Letter` and limits Jinja to approved `doc.<fieldname>` references from `Dunning Letter` only. 

### Finding 3 — SVG sanitization

**Risk:** Previously High
**Status:** Closed for design stage
**Evidence:** The revised design includes SVG sanitization before preview/output use and identifies unsafe SVG as a design risk mitigated by strict sanitizer and unsafe SVG rejection.  

### Finding 4 — Generated output XSS

**Risk:** Previously High
**Status:** Closed for design stage
**Evidence:** Output allowlists are defined for HTML tags, CSS properties, Jinja references, images, and JavaScript prohibition. 

### Finding 5 — Rate limiting and abuse prevention

**Risk:** Previously High
**Status:** Closed
**Evidence:** Rate limits are defined for upload, OCR, preview, save, finalize, output generation, and return-to-editing. 

### Finding 6 — Secrets configuration

**Risk:** Previously Medium
**Status:** Closed for design stage
**Evidence:** Google Vision credentials are backend-only, stored in server-side configuration or secret manager, and excluded from client, logs, and snapshots. 

### Finding 7 — Audit retention and alerting

**Risk:** Previously Medium
**Status:** Closed for design stage
**Evidence:** Audit retention, access control, append-only UI behavior, and alert thresholds are now documented. 

### Finding 8 — File size/storage privacy

**Risk:** Previously Medium
**Status:** Closed for design stage, verify during implementation
**Evidence:** Stage gate checklist marks file size/storage privacy rules as complete. 

## 19. Risk Rating

**Overall design-stage risk:** **Low to Medium**

No unresolved Critical or High design findings remain. Remaining risk is implementation risk: the team must correctly implement and test the security controls.

## 20. Required Fixes

No additional Stage 3 design fixes are required before Stage 4.

Required Stage 4 implementation planning actions:

1. Convert rate limits into enforceable constants or configuration.
2. Add unit tests for SVG sanitizer.
3. Add unit tests for generated output sanitizer.
4. Add access-control tests for Guest, non-Administrator, System Manager, and custom-role users.
5. Add finalized-state bypass tests.
6. Add private file access tests.
7. Add log redaction tests.
8. Add Google Vision secret exposure tests.
9. Define the operational approval workflow for business deletion.

## 21. Recommended Improvements

Add a Stage 4 security implementation checklist with explicit pass/fail items for:

* no `allow_guest=True`
* `frappe.session.user == "Administrator"` check
* `Dunning Letter` server-side enforcement
* private file enforcement
* rate-limit enforcement
* sanitizer enforcement
* log redaction
* version history immutability
* return-to-editing invalidation
* no sensitive data in API errors

## 22. Security Test Cases

Minimum Stage 4 tests:

1. Guest cannot access any API.
2. Authenticated non-Administrator cannot access any API.
3. System Manager cannot access unless the user is exactly built-in `Administrator`.
4. Custom role user cannot access.
5. All custom DocTypes deny non-Administrator access.
6. Any DocType other than `Dunning Letter` is rejected.
7. OCR result must belong to active setup.
8. File reference must be valid, private, accessible, and allowed.
9. Multi-page PDF is rejected.
10. Protected/encrypted PDF is rejected.
11. Oversized PDF is rejected.
12. WEBP branding is rejected.
13. PDF branding is rejected.
14. Unsafe SVG with script is rejected.
15. Unsafe SVG with event handler is rejected.
16. Unsafe SVG with external reference is rejected.
17. Static text XSS payload is encoded.
18. OCR text XSS payload is encoded.
19. Dynamic field XSS payload is escaped.
20. Generated output contains no JavaScript.
21. OCR rate limit works.
22. Upload rate limit works.
23. Preview/output rate limits work.
24. Finalized setup cannot be edited by direct API.
25. Return-to-editing invalidates final output.
26. Logs exclude credentials, private paths, OCR text, raw files, and full warning-letter content.
27. Version history is Administrator-only.
28. Private PDF URLs cannot be accessed by unauthorized users.

## 23. Approval Decision

**Decision:** **Approved for Stage 4 Implementation Planning**

The latest `03f_system_designer_revised.md` resolves the previously blocking security design findings. This approval is limited to moving from **System Design** to **Implementation Planning**.

**Not approved for release.** A separate Post-Implementation Security Audit and Pre-Deployment Security Gate are still required.

## 24. Security Gate Checklist

| Checklist Item                        | Status                                           |
| ------------------------------------- | ------------------------------------------------ |
| Authentication reviewed               | Passed                                           |
| Authorization reviewed                | Passed                                           |
| API access reviewed                   | Passed                                           |
| Input validation reviewed             | Passed                                           |
| Database access reviewed              | Passed                                           |
| Secrets reviewed                      | Passed                                           |
| Logging reviewed                      | Passed                                           |
| Privacy reviewed                      | Passed for design stage                          |
| Rate limiting reviewed                | Passed                                           |
| Deployment security reviewed          | Conditionally passed for Stage 4                 |
| Critical risks resolved or documented | Passed                                           |
| High risks resolved or documented     | Passed                                           |
| 
