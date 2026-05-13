# GPF Print Format Builder - Handoff Documentation

## 1. Developer Setup
### 1.1 Installation
1. Install the Frappe app:
   ```bash
   bench get-app gpf_builder
   bench --site [sitename] install-app gpf_builder
   ```
2. Run migrations:
   ```bash
   bench --site [sitename] migrate
   ```

### 1.2 Configuration
- **Google Vision**: You can use either an **API Key** or a **Service Account JSON**:
  - **API Key (Simple)**: Add `"google_api_key": "YOUR_KEY"` to `common_site_config.json`.
  - **Service Account (Advanced)**: Add `google_vision_credentials` (raw JSON content) to `common_site_config.json`. Set via console: `frappe.set_config("google_vision_credentials", open("key.json").read())`.
- **Rate Limits**: Configurable in `GPF Settings` (DocType).
- **PDF Size**: Defaulted to 2MB, configurable in `PDFService`.

## 2. API Contracts
All endpoints are whitelisted and require `Administrator` access.

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `upload_pdf_reference` | POST | Validates and links reference PDF. |
| `save_layout` | POST | Atomically saves layout blocks. |
| `get_preview` | GET | Returns sanitized HTML preview. |
| `finalize_setup` | POST | Locks layout for production. |
| `run_ocr` | POST | Triggers Google Vision OCR. |

## 3. Administrator Usage Guide
### 3.1 Creating a Setup
- Navigate to **GPF Print Format Setup**.
- Create a new record (restricted to `Dunning Letter` for MVP).
- Set it to **Active**.

### 3.2 Designing Layout
- Open the **GPF Builder** page.
- Add **Static Text** or **Dynamic Fields**.
- Position and resize blocks using the interactive canvas.
- For dynamic fields, use valid `Dunning Letter` fieldnames (e.g., `customer_name`).

### 3.3 Finalization
- Ensure at least one block exists.
- Ensure any OCR blocks are **Confirmed**.
- Click **Finalize**. The setup is now locked.

## 4. Security Operations
- **Access Control**: Hard-restricted to the built-in `Administrator`. No other roles or users are permitted.
- **Audit Logs**: Viewed in **GPF Audit Event**. User identifiers are SHA-256 hashed.
- **Private Files**: All PDFs and branding assets must be stored in the `/private/` folder.

## 5. Known Limitations
- Supports **single-page** PDFs only.
- Supports **one active setup** per DocType.
- **No Rollback**: Layout saving is destructive (Atomic Overwrite). Use Version History to review changes.
- **Not Pixel-Perfect**: HTML generation is assistive; browser rendering differences may occur.

## 6. QA Handoff Notes
- **Test Suite**: Run `bench --site [sitename] run-tests --app gpf_builder`.
- **Security Check**: Verify `api_guard()` is present in all `api.py` methods.
- **Sanitization**: All HTML/SVG is filtered through `BrandingService` and `LayoutService`.
