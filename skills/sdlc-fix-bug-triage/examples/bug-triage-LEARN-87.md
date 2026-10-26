# Bug triage — LEARN-87: Uploading "Week1.PDF" fails with "Unsupported file type"

> Lives at `docs/product/bugs/LEARN-87/bug-triage.md` (per-bug folder; the folder carries the key).

**Date:** 2026-07-02 · **Reported by:** instructor (support ticket #4412) · **Reported in:** production, Chrome 126

## Bug
- Key: LEARN-87
- Summary: Uploading "Week1.PDF" fails with "Unsupported file type"
- Linked issues: relates to LEARN-21 (Upload course materials)

## Expected vs actual
**Expected:** A PDF of at most 25 MB is accepted and stored with status "processing".
**Source:** `docs/product/epics/LEARN-11/stories/LEARN-21/test-plan.md` — scenario 1, "Accepted upload (≤25 MB, PDF/DOCX/TXT) → 201, status "processing" within 2s"; LEARN-21 acceptance criteria name the format, not the file-name case.

**Actual:** `POST /api/courses/{course_id}/materials` with `Week1.PDF` (1.2 MB) returns
`415 {"error": "Unsupported file type"}`. The same file renamed to `week1.pdf` uploads fine.

## Steps to reproduce
1. As an instructor of course `c-101`, have a valid 1.2 MB PDF named `Week1.PDF`.
2. `POST /api/courses/c-101/materials` with the file as multipart field `file`, content type
   `application/pdf` *(assumed: the browser sends `application/pdf` for .PDF files)*.
3. Observe `415` with body `{"error": "Unsupported file type"}`; no `material` row is created.

## Severity
**Severity:** S3 — upload of a supported format is rejected; affects files with an uppercase
extension (common on Windows scanners); workaround: rename the file.

## Affected area
- `apps/api/app/ingestion/routes.py` — upload endpoint returning the 415.
- `apps/api/app/ingestion/validation.py` — type allowlist the route calls.

## Decision
**Decision:** Fix
A documented format is rejected based on file-name case; the steps are concrete and the
expected behaviour is defined by LEARN-21.

## Jira
- Status before: To Do
- Status after: In Progress
- Action: transition "Start Progress" applied; severity S3 and component "ingestion" set.

## Notes
- Reporter suspects "the virus scanner"; there is no virus scanner in the upload path per
  architecture.md. Not used.
- Check whether `.DOCX` / `.TXT` behave the same; the reproduce step should cover them.
