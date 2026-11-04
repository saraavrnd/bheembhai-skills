# Impact Flags — LEARN-21: Upload course materials

**Date:** 2026-06-20 · **Stories checked:** 2 · **Flagged:** 1

## Stories checked
- LEARN-22 (In Progress) — passed the pre-filter: its design names the `material` table.
- LEARN-30 (In Review) — no intersection with this diff (works in `tutor/`).

## Flags
| Story | What this change did (path:line / entity / endpoint) | What their design relies on | Comment posted |
|-------|------------------------------------------------------|-----------------------------|----------------|
| LEARN-22 | `material` table created with `status` (`migrations/0004_material.py:12`) | "prep job reads `material.status` and sets it to `ready`" (LEARN-22 `story-design.md`, Data-model deltas) | yes: "Design changed by LEARN-21: `material` table is now live with `status`; re-check your story design — your prep job should transition this exact status field." |

---
*A notification only: flagged developers re-check their own design. This run continues to `sdlc-deliver-pr-open`.*
