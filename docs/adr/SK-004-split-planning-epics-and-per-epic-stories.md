# SK-004: Split planning into PRD-to-epics and a per-epic stories workflow

**Status:** Proposed · **Date:** 2026-11-21 · **Deciders:** Saraav

Builds on SK-002, SK-003 and platform **ADR-035** (cross-vendor author and reviewer routing),
**ADR-027** (sub-workflow fan-out), **ADR-031** (work-item bindings) and **ADR-006** (a policy is
tied to its workflow).

## Context

`sdlc-wf-planning` runs PRD → epics → Jira, then fans out one `sdlc-wf-planning-epic` child per
epic. That makes one run as long as the PRD is big:

1. **Unbounded and serial.** Nobody knows how many epics a PRD will produce. ADR-027 v1 allows
   only `concurrency: 1`, so ten epics means ten story-write / epic-review / sequence / publish
   loops back to back, each with its own gates, inside one run that cannot finish until the last
   epic's gate is answered.
2. **One owner.** Every child inherits the parent's branch and the person who started the parent
   gets every gate. Epics cannot be handed to the people who will own them.
3. **No order between epics, and no review of the epic plan.** `sdlc-plan-epic-sequence` orders
   stories inside one epic. Nothing orders the epics themselves, and nothing on a different
   model family reviews the epic plan before it is published, although every per-epic run
   inherits its boundaries (the same gap SK-003 closed for the PRD).

## Decision

1. **New workflow `sdlc-wf-planning-epics`** (PRD to epics), run once per PRD:
   `sdlc-plan-epics-create` → `sdlc-plan-epics-order` → `sdlc-plan-epics-review` →
   `sdlc-tracker-sync`, with `epics-review: changes_requested → epics-create` (revise mode),
   which flows through `epics-order` again so the order always matches the revised plan. It ends
   with the epics, and the "blocks" links between them, published to Jira. It writes no stories.
2. **New skill `sdlc-plan-epics-order`** (`author`). Writes `epic-order.md` / `.json` only: one
   entry per epic in `epic-map.json` with its wave, `depends_on` and per-edge source (`link`,
   `prd`, `epic-body`, `lifecycle`) and confidence (`firm` / `provisional`), the MVP path, and
   cycles. A cycle escalates. Named "order" so it is not confused with `sdlc-plan-epic-sequence`,
   which orders the stories of one epic.
3. **New skill `sdlc-plan-epics-review`** (`reviewer`). Writes `epics-review.md` only: a PRD fit
   verdict (`Fits` / `PRD gap`) and findings with a **target** (`epics` or `order`), severity,
   evidence, a question with a proposed default, and a proposed change. Blocking findings →
   `changes_requested`; `PRD gap` → `escalation_required`. Its `changes_requested` edge names
   `sdlc-plan-epics-create`, so it runs on the reviewer model (ADR-035 §3).
4. **`sdlc-plan-epics-create` gains a revise mode.** It applies the `epics` findings, keeps keys
   stable (a split appends a new draft key; a published epic is never merged away), and logs the
   pass in `epics-revisions.md`; verify.yaml checks that log exists when the run came back from
   the review. Create mode is unchanged.
5. **`sdlc-wf-planning-epic` v2 runs on its own, per epic.** It declares `work_item: epic`: a
   person starts it on a published Jira Epic, and several people can run it on different epics at
   the same time. Its steps are unchanged (stories-write → epic-review → epic-sequence →
   tracker-sync). It stays the fan-out child of `sdlc-wf-planning`, where `ITEM.epic_key` gives
   the epic.
6. **`sdlc-tracker-sync` gains an epic-links scope** (approved `epic-order.json` edges become
   "A blocks B" links between epics, never removed automatically) and swaps draft keys in
   `epic-order.json`. **On a per-epic run it touches only that epic's stories and links**, so
   parallel runs cannot overwrite each other.
7. **Two policies.** `sdlc-policy-planning-epics-governed`: a lead answers the review's questions
   and signs off the plan and order (`completed`, `changes_requested`, `escalation_required`)
   before anything is published, and a person sees a cycle from `epics-order`.
   `sdlc-policy-planning-epics-fast`: review questions are defaulted; a person still signs off
   (`completed`, `escalation_required`) before publishing.
8. **`sdlc-wf-planning` stays** as the all-in-one run for small PRDs planned by one person.

## How a per-epic run gets its epic

The options were:

- **ADR-027 run inputs** (`ITEM` set by hand). ADR-027 says a child "can be triggered by hand for
  a single item", but defers the run-form input editor, and a hand-typed epic key is easy to get
  wrong.
- **A work-item binding from the run's Jira issue** (chosen). It is how story delivery and bug
  fix already choose their item: a person picks the issue, the platform checks its type. ADR-031
  §1.1 maps Bug → `bug` and everything else → `story`; this needs **Epic → `epic`**, with:

  | Name | Epic run |
  |---|---|
  | `{epic}` | the run issue's key |
  | `{layout.epic_dir}` | `docs/product/epics/<EPIC_KEY>/_epic/` |
  | `context.epic` | the epic: summary, description, labels, links |
  | `context.work_item` | `{type: epic, is_bug: false, key}` |
  | Run branch | `plan/<safe_key>/<DDMMYYYYHHmm>-<uuid4>` |

  The run is refused at start if the issue is not an Epic, or if the epic is not in
  `epic-map.json` at the base branch (`sdlc-plan-stories-write`'s `epic_in_map` precondition
  also catches this). A fan-out child keeps taking `{epic}` from `ITEM.epic_key`; the type check
  is skipped for children, since they have no run issue of their own.

## Where this differs from the conventions, and why

- **Literal paths in verify.yaml**, as in SK-003: `docs/product/epic-order.json`,
  `epics-review.md` and `epics-revisions.md` until the platform binds `{layout.epic_order}`,
  `{layout.epics_review}` and `{layout.epics_revisions}`. The default Project Layout rows are
  added.
- **The plan must be merged before per-epic runs start.** A standalone run branches from the
  project's base branch, so `epics.md`, `epic-map.json` and `epic-order.json` (with real keys)
  must be merged there first. The fan-out child does not need this: it shares the parent's branch.
- **Epic links are only added, never removed.** A story link can be retired by a refine pass;
  an epic re-order is rare and its links are often edited by hand in Jira, so a dropped edge is
  reported for a person instead.

## Alternatives considered

- **Raise ADR-027 concurrency above 1.** It would make the all-in-one run faster, but still one
  run, one branch and one person's gates; and concurrency > 1 is deferred in the platform.
- **Fold ordering into `sdlc-plan-epics-create`.** It already orders epics for readability, but
  an approved, machine-readable order is what tracker-sync links and what a reviewer can check;
  SK-002 keeps it a separate step.
- **A new standalone copy of the per-epic workflow.** Two workflows with the same four steps
  would drift; one workflow with two entry points does not.

## Follow-ups

1. **Platform (needed before release):** map Jira `Epic` → `work_item: epic` and bind the names
   above (ADR-031 §1); accept `epic` in `runs.work_item_type` and in the workflow validator. Until
   then, a platform that rejects `work_item: epic` will reject `sdlc-wf-planning-epic` v2, and
   `catalog.yaml`'s `requires_platform` must be raised to the first platform version with it.
2. Platform: bind `{layout.epic_order}`, `{layout.epics_review}` and `{layout.epics_revisions}`,
   then swap the literal paths.
3. Optionally declare `work_items: [epic]` on the per-epic skills' verify.yaml so they are
   refused on story and bug runs.
4. Bump `catalog.yaml`'s `version` when this is released.

## Consequences

- A PRD becomes published, ordered and reviewed epics in one bounded run, whatever the number of
  epics.
- Each epic's stories are planned in their own run, owned by whoever starts it, in parallel.
- The planning chain is now three workflows: `sdlc-wf-planning-prd` → `sdlc-wf-planning-epics` →
  `sdlc-wf-planning-epic` (× N), with `sdlc-wf-planning` kept as the single-run alternative.
