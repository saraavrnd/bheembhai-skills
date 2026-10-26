# Test Plan — LEARN-87: Uploading "Week1.PDF" fails with "Unsupported file type"

**Work item:** bug · **Date:** 2026-07-02 · **Runners:** pytest (unit + integration)

## Scenario → test mapping
Every regression scenario fails now with the signature in reproduction.md; every guard passes
now. Both must pass after the fix.

| # | Scenario | Layer | Test file::test name | Type |
|---|----------|-------|----------------------|------|
| 1 | `Week1.PDF` (1.2 MB, application/pdf) is accepted → 201, status "processing" | integration | `tests/integration/ingestion/test_materials_upload.py::test_accepts_uppercase_extension` | regression |
| 2 | Allowlist ignores extension case (`.PDF`, `.DOCX`, `.TXT`, `.PdF`) | unit | `tests/unit/ingestion/test_upload_validation.py::test_type_allowlist_ignores_extension_case` | regression |
| 3 | Disallowed types stay rejected in any case (`.exe`, `.EXE`) | unit | `tests/unit/ingestion/test_upload_validation.py::test_type_allowlist_still_rejects_exe` | guard |

## Coverage check
- [x] The reported case has a regression test at the layer the user saw (scenario 1, endpoint).
- [x] Regression tests assert the expected behaviour from bug-triage.md (201 / allowed), not the current 415.
- [x] Guard test covers the nearest working case (disallowed types still rejected).

## Red-phase verification
```
$ pytest -vv tests/unit/ingestion/test_upload_validation.py tests/integration/ingestion/test_materials_upload.py -k "uppercase or extension_case or rejects_exe"
tests/unit/ingestion/test_upload_validation.py::test_type_allowlist_ignores_extension_case FAILED
tests/unit/ingestion/test_upload_validation.py::test_type_allowlist_still_rejects_exe PASSED
tests/integration/ingestion/test_materials_upload.py::test_accepts_uppercase_extension FAILED
2 failed, 1 passed
```

## Traceability
**Bug:** LEARN-87 · **Expected behaviour from:** LEARN-21 scenario 1 · **Requirements:** FR-004

---
*Next: `sdlc-fix-rootcause-analyze` explains why these fail; `sdlc-deliver-code-implement` makes them pass.*
