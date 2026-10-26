# Reproduction — LEARN-87: Uploading "Week1.PDF" fails with "Unsupported file type"

> Lives at `docs/product/bugs/LEARN-87/reproduction.md`.

**Date:** 2026-07-02 · **Stack:** `docker compose up -d api db` (seed: course `c-101`, instructor `inst-1`)

## Bug
- Key: LEARN-87
- Triage: `docs/product/bugs/LEARN-87/bug-triage.md` (Decision: Fix, Severity S3)

## Reproduction
**Attempt 1:** triage steps as written, `Content-Type: application/pdf`.
```
$ curl -s -o - -w ' %{http_code}' -H "Authorization: Bearer $INST_TOKEN" \
    -F "file=@Week1.PDF;type=application/pdf" http://localhost:8000/api/courses/c-101/materials
{"error":"Unsupported file type"} 415
```
**Result:** reproduced.

**Attempt 2:** same file renamed `week1.pdf`.
```
{"material_id":"m-9f2","status":"processing"} 201
```
**Result:** not reproduced (expected; confirms the case-sensitivity hypothesis from the report).

**Attempt 3:** `Notes.DOCX`, `readme.TXT`.
```
{"error":"Unsupported file type"} 415
{"error":"Unsupported file type"} 415
```
**Result:** reproduced for every allowed format with an uppercase extension.

## Observed symptom
**Signature:** `Unsupported file type`
Returned as the `error` field of the 415 response body.

## Minimal failing case
- Layer: unit
- Input: `is_allowed_type("Week1.PDF", "application/pdf")` returns `False`
- Corrections to triage: none (content type `application/pdf` confirmed from browser devtools in the ticket)

## Regression tests
- `tests/integration/ingestion/test_materials_upload.py::test_accepts_uppercase_extension` — regression — `Week1.PDF` → 201, status "processing"
- `tests/unit/ingestion/test_upload_validation.py::test_type_allowlist_ignores_extension_case` — regression — `.PDF`, `.DOCX`, `.TXT`, `.PdF` allowed
- `tests/unit/ingestion/test_upload_validation.py::test_type_allowlist_still_rejects_exe` — guard — `.EXE` and `.exe` still rejected

## Red-phase verification
```
$ pytest -vv tests/unit/ingestion/test_upload_validation.py tests/integration/ingestion/test_materials_upload.py -k "uppercase or extension_case or rejects_exe"
tests/unit/ingestion/test_upload_validation.py::test_type_allowlist_ignores_extension_case FAILED
    AssertionError: is_allowed_type('Week1.PDF', 'application/pdf') -> False; reason: Unsupported file type
tests/unit/ingestion/test_upload_validation.py::test_type_allowlist_still_rejects_exe PASSED
tests/integration/ingestion/test_materials_upload.py::test_accepts_uppercase_extension FAILED
    assert 415 == 201; body={'error': 'Unsupported file type'}
2 failed, 1 passed
```
Both regression tests fail with the signature; the guard passes.

## Notes
- The 415 is produced before the size check, so oversized uppercase files also return 415
  instead of 413. Root-cause analysis should confirm the order is otherwise unchanged.
