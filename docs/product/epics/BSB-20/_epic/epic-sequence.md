# Epic Sequence — BSB-20: Skill cloning & edit builds

**Status:** AWAITING APPROVAL · **Date:** 2026-11-16 · **Stories:** 2

> Proposed build order by dependency. Review and approve at the gate; `sdlc-tracker-sync` then
> mirrors the approved edges as Jira "blocks" links.
> This is a **provisional** first-run order: no `story-design.md` notes exist for BSB-20 yet, and
> the stories still carry draft `-PENDING-` keys, so no explicit Jira links were available to read
> for them. The ordering below is inferred from requirement traceability and the stories' own
> acceptance criteria and Notes. It will be refined if story designs land and reveal produces/
> consumes relationships. Inferred edges are marked by source; explicit Jira links are ground truth
> and are never changed.

## Build order (waves)

Stories in the same wave are independent → can be built in parallel.

### Wave 1 (no dependencies — start here)
- BSB-20-PENDING-1 — Clone a catalog skill into a new skill under a new name
- BSB-20-PENDING-2 — Open an existing catalog skill in an edit build

There is no Wave 2: neither story in this epic depends on the other.

## Dependencies (with source + confidence)

**No intra-epic edges.** Both stories are producers of their own mode on the shared create-build
handler; neither consumes an endpoint, table, field or artifact that the other produces:

| Story | Depends on | Source | Confidence | Why |
|-------|-----------|--------|-----------|-----|
| _(none within BSB-20)_ | — | — | — | Clone (`BSB-20-PENDING-1`) adds `clone` mode and whole-folder copy; edit (`BSB-20-PENDING-2`) adds `edit` mode and existing-folder resolution. The two modes are siblings on the same handler, not inputs to one another. |

Why they are in the same wave:

- `BSB-20-PENDING-1` produces a `builds` row with `kind = "clone"`, a `build/<new-skill-name>`
  branch, the copied skill folder and its rewritten name — all new artifacts that
  `BSB-20-PENDING-2` neither reads nor writes.
- `BSB-20-PENDING-2` produces a `builds` row with `kind = "edit"`, a `build/<skill-name>` branch
  and resolution to the *existing* `skills/<skill-name>/` folder — it never creates or reads a
  clone, and its inverted name-existence rule (the name must exist on `main`) is the opposite of
  the clone's rule for a new name.
- Requirement traceability splits cleanly too: FR-011–FR-014 (clone) and FR-124–FR-126 (edit) are
  independent requirement groups; neither presupposes the other.

## Cross-epic prerequisites (outside this sequence)

These are real, artifact-derived prerequisites recorded in both stories' **Notes / dependencies**.
They are **not** edges in this epic's graph and are intentionally not placed in `depends_on`: this
sequence covers BSB-20 only, and the prerequisite stories belong to earlier epics whose order is
already fixed by `docs/product/epics.md` (BSB-18 → BSB-19 → BSB-20). `sdlc-deliver-story-start` and
`sdlc-tracker-sync` enforce cross-epic order through that epic ordering, not through this file.

| Story | Prerequisite (other epic) | Source | Confidence | Why |
|-------|---------------------------|--------|-----------|-----|
| BSB-20-PENDING-1, BSB-20-PENDING-2 | BSB-18 (signed-in author; local `users` row) | acceptance-text / requirement | firm | Both stories' Given clauses start from "a signed-in skill author whose local `users` id is 42"; `builds.created_by` references that row. |
| BSB-20-PENDING-1, BSB-20-PENDING-2 | BSB-19-PENDING-1 (build record, branch-name rule, `base_sha`, single shared `GET /builds/new` + `POST /builds` handler) | acceptance-text | firm | Both stories explicitly extend that one handler and add no second handler; the build row and branch rule come from it. |
| BSB-20-PENDING-1, BSB-20-PENDING-2 | BSB-19-PENDING-3 (shared skill-name validator and open-build collision check) | acceptance-text | firm | Both stories reuse the shared validator/collision check; the edit flow passes a `mode` parameter to invert the existence rule. |
| BSB-20-PENDING-1, BSB-20-PENDING-2 | External catalog repository `bheembhai-skills` and its `main` branch | requirement (`PRD.md` §8; ADR SK-001 §1a) | firm | The clone reads the source folder from `main`; the edit build cuts its branch from `main`. |

Forward hand-off (not a prerequisite for either story's acceptance): `BSB-20-PENDING-2` requires
BSB-21's save story to assert that a save commits only to the existing `skills/<skill-name>/`
folder (the FR-125 no-second-folder proof). BSB-21 is a later epic and is not sequenced here.

## Parallelizable groups

`{BSB-20-PENDING-1, BSB-20-PENDING-2}` — both are Wave 1 and can be started immediately.

**Coordination note (not a dependency edge):** both stories extend the same two shared surfaces —
the `GET /builds/new` + `POST /builds` handler and the skill-name validator/collision check from
BSB-19. Two developers working in parallel on the same handler and validator will contend on those
files, so they should either serialize the edits to those files or coordinate the merge. This is
merge contention, not a consumes/produces dependency; neither story needs the other's output.

## Cycles / conflicts flagged (need a human decision)

None. The intra-epic graph has no edges, so it is trivially acyclic and no edge contradicts a
human-set Jira link (no such links exist yet — the stories are still draft `-PENDING-` keys and
have not been published).

## On approval

- `sdlc-tracker-sync` sets "blocks" links: none from this epic — there are no intra-epic edges.
  Cross-epic prerequisites above are not mirrored from this file; the epic order in
  `docs/product/epics.md` already governs them.
- `epic-sequence.json` is read by `sdlc-deliver-story-start`, which refuses a story whose
  prerequisites are not merged.

---
*Both BSB-20 stories are eligible to start now (Wave 1, no intra-epic prerequisites). Re-run
`sdlc-plan-epic-sequence` if stories are added or re-designed; a dependency delta from
`sdlc-deliver-story-design` may sharpen this order for the not-yet-built stories.*
