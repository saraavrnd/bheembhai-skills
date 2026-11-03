# Design Sync — LEARN-21: Upload course materials

**Date:** 2026-06-19 · **Branch:** `feat/LEARN-21-upload-course-materials` · **Classification:** Incremental

## What this story changed (vs current design)
- New endpoint: `POST /api/courses/{course_id}/materials` (was anticipated as a feature area but
  not yet in the current-endpoints list).
- New data entity row in use: `material` table created (it was sketched in data-model.md; now
  real with concrete fields).
- No new module dependency, no new integration, no new cross-cutting concern.

## Reference updates committed to this branch
- [x] `architecture.md` — added the endpoint to the ingestion module's "current endpoints" line.
- [x] `data-model.md` — promoted `material` from sketch to concrete: `id, course_id, filename,
      mime_type, size_bytes, status, created_at`.
- [x] `api-contracts/materials.yaml` — added the POST contract (request multipart, 201/415/413).
- [x] `AGENTS.md` — added the endpoint to "Current endpoints", `material` to "Data entities".
- [x] `docs/CHANGELOG-design.md` — entry: "LEARN-21: material upload endpoint + material table."

## Structural-change check
None — incremental, fully within the existing architecture. No sdlc-arch-design amendment needed.

---
*Docs committed to the branch; `sdlc-deliver-impact-flag` runs next (see its LEARN-21 example: it
flags LEARN-22), then `sdlc-deliver-pr-open` opens the PR.*
