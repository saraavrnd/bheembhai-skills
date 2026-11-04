# SK-002: Single-responsibility skills with one role each

**Status:** Proposed · **Date:** 2026-11-03 · **Deciders:** Saraav

The skills-repo half of platform **ADR-035** (cross-vendor author and reviewer routing). The
platform side — the run modal's primary and reviewer models, model-family resolution, the
family check at run init — is ADR-035 §6–§9 and is not in this repo.

## Context

ADR-035 runs content-creating steps on one model family and review steps on a different one. That
only works if no skill both writes and reviews, so the catalog audit (ADR-035 §4) found the skills
that do more than one job.

## Decision

1. **Every skill declares `role: author | reviewer | integration`** in its SKILL.md frontmatter.
   `tools/check.py` refuses a missing or unknown role, and refuses a reviewer or integration skill
   whose `verify.yaml` has no `builtin:diff_paths` limiting what it writes.
2. **Splits made in this repo:**

   | Skill | Change |
   |---|---|
   | plan-epic-review, plan-story-review | `reviewer`: report only (severity, evidence, question, proposed change). No edits to stories, maps or Jira |
   | plan-stories-write | No Jira writes; new **revise mode** applies a review report plus the gate's answers; draft keys `<EPIC>-PENDING-N` |
   | plan-epics-create | No Jira writes; draft keys `<FA-N>-PENDING` |
   | plan-epic-sequence | No Jira link writes; refine passes record `retired_edges` |
   | fix-bug-triage | Records the intended tracker action; no Jira writes |
   | deliver-docs-sync | Docs only; the in-progress overlap check moved out |
   | deliver-pr-open | No longer runs docs-sync; may only commit the loop's own untracked artifacts |
   | deliver-story-design | Records the dependency delta in its note; no longer calls epic-sequence or writes its files |
   | deliver-code-implement | No longer creates branches (the platform creates the run branch, ADR-013) |
   | arch-design | UI-conventions starter moved out |

3. **New skills:** `sdlc-tracker-sync` (integration: the only planning/triage writer to Jira),
   `sdlc-deliver-impact-flag` (integration: comments on overlapping in-progress stories, every run,
   code pre-filter first), `sdlc-arch-ui-conventions` (author).
4. **Workflows:** story-delivery v2 starts at story-start and runs docs-sync → impact-flag before
   pr-open; tests-write declares `independent_of: [sdlc-deliver-code-implement]`. Bug-fix v2 adds
   tracker-sync after triage and docs-sync → impact-flag before pr-open. New `sdlc-wf-planning`
   (PRD → epics → publish → fan-out) and `sdlc-wf-planning-epic` (stories → epic-review, with
   `changes_requested` back to stories-write revise → sequence → publish), each with a governed
   policy.

## Where this differs from ADR-035, and why

- **Branch creation goes to the platform, not story-start.** story-start already says the platform
  creates the run branch at init, and implement's verify forbids branch rewrites; implement's
  Step 1 was the stray. It now only confirms it is on the run branch.
- **discovery-dependency-inventory is unchanged.** Its `risk` field records observed facts (a newer
  version exists, an advisory is published), not a judgement, and it is wired into generated
  template checks and two consumers (security-posture, risk-register). Splitting it costs more than
  it buys; revisit if the flags start carrying opinions.
- **impact-flag writes `impact-flags.md`**, not into docs-sync's `design-sync.md`, so two skills never
  write the same file.
- **No story-design → epic-sequence edge in story-delivery.** The engine routes by verdict, so a
  "run only when the order changed" edge is not expressible; running sequence + tracker-sync on every
  story would add two steps for a usually-empty delta. story-design records the delta and says when
  a refine run is needed.
- **A non-Fix triage decision is not synced.** Triage's `escalation_required` ends the run for a
  person (as before); tracker-sync runs only on the Fix path. The note still records the comment a
  person should add.
- **`allow_deletes` on `builtin:diff_paths` is not added yet.** That builtin lives in the pinned
  `bheembhai-verify`; the flag needs a verifier release first.
- **story-review stays on demand**, outside `sdlc-wf-planning-epic`: epic-review covers the set, and a
  per-story fan-out inside a fan-out child is not something the engine supports today.

## Consequences

- Planning and triage skills lose their Atlassian MCP write dependency; one skill owns Jira writes.
- Releasing this catalog needs a platform that accepts `role:` in SKILL.md and `independent_of:` in
  workflows (ADR-035). Until then, do not tag a release from it.
