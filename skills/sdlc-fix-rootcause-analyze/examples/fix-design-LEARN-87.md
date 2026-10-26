# Fix Design — LEARN-87: Uploading "Week1.PDF" fails with "Unsupported file type"

> Lives at `docs/product/bugs/LEARN-87/fix-design.md` (the bug's design note).

**Status:** PROPOSED · **Date:** 2026-07-02 · **Domain:** backend

## Root cause
`is_allowed_type` compares the file extension with the allowlist without normalising case, so
any allowed format with an uppercase extension is rejected, at
`apps/api/app/ingestion/validation.py:14`.

## Causal chain
1. `apps/api/app/ingestion/validation.py:13` — `ext = os.path.splitext(filename)[1]` yields `".PDF"` for `Week1.PDF`.
2. `apps/api/app/ingestion/validation.py:14` — `return ext in ALLOWED_EXTENSIONS` where `ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}` → `False`.
3. `apps/api/app/ingestion/routes.py:41` — on `False`, the route returns 415 before the size check.
4. Signature `Unsupported file type` returned by `apps/api/app/ingestion/routes.py:42`.

## How it got in
Introduced in `a3f9c21` (LEARN-21, "upload course materials"). The LEARN-21 design specified
"MIME type against an allowlist" but the implementation checks the extension; its tests used
only lowercase names. The MIME type sent (`application/pdf`) was correct and never consulted.

## Fix approach
Normalise the extension with `.lower()` before the membership test in `is_allowed_type`. This
fixes every caller of the helper, not just the upload route. Checking the MIME type as the
LEARN-21 design intended is a behaviour change beyond this bug and is left out of scope.

## Target module(s)
- `apps/api/app/ingestion/validation.py` — `is_allowed_type` normalises case.

## Interfaces
No interface change. `is_allowed_type(filename, mime_type) -> bool` keeps its signature.

## Data-model deltas
None. No stored data is wrong: rejected uploads were never persisted.

## Blast radius
- Callers of the changed code: `apps/api/app/ingestion/routes.py:40`, `apps/api/app/ingestion/bulk_import.py:58`
- Siblings (same wrong assumption elsewhere): `apps/api/app/media/avatars.py:22` compares image
  extensions the same way — new bug suggested (different module, different feature).

## Fix scope
**Scope:** local

## Test surface
- Regression tests from test-plan.md must pass: `test_accepts_uppercase_extension`, `test_type_allowlist_ignores_extension_case`
- Guard tests must stay green: `test_type_allowlist_still_rejects_exe`
- Add: `tests/integration/ingestion/test_bulk_import.py::test_bulk_import_accepts_uppercase_extension` (second caller).

## Out of scope
MIME-type validation (needs a story change to LEARN-21's approach); the avatar sibling (new bug).

## Traceability
**Bug:** LEARN-87 · **Introduced by:** LEARN-21 (`a3f9c21`) · **Requirements:** FR-004

---
*Next: `sdlc-deliver-code-implement` builds this fix on `fix/LEARN-87-upload-extension-case` until the regression tests pass.*
