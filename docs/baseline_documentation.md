# Dependencies and Environment Baseline

## Dependencies

### Layout Editing
- **Library**: Konva.js or Fabric.js (Canvas helper library)
- **Purpose**: To handle layout drawing, dragging, resizing, and alignment interactions in the browser.

### PDF Rendering
- **Library**: PDF.js
- **Purpose**: To render single-page PDF references as a background for the layout builder in the browser.

### Backend OCR
- **Service**: Google Vision API
- **Client**: Google Cloud Vision Python SDK
- **Configuration Keys**:
  - `google_vision_enabled`: Boolean
  - `google_vision_credentials_path`: String (path to service account JSON or secret reference)
  - `google_vision_project_id`: String
  - `ocr_max_requests_per_hour`: Integer
  - `ocr_timeout_seconds`: Integer

## Testing Conventions

Tests are located in `gpf_builder/tests/` and follow this naming convention:

- **Unit Tests**: `test_unit_*.py` - Testing isolated service logic.
- **API Tests**: `test_api_*.py` - Testing whitelisted API endpoints and request/response shapes.
- **Integration Tests**: `test_int_*.py` - Testing interaction between services and the database.
- **Security Tests**: `test_sec_*.py` - Testing access control, sanitization, and rate limits.
- **End-to-End Tests**: `test_e2e_*.py` - Testing complete workflows from UI/API to final output.

Execution command: `bench run-tests --app gpf_builder`
