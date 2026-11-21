---
name: sdlc-plan-epics-review
role: reviewer   # ADR-035: author | reviewer | integration
description: >
  Review a project's epic plan and epic order against the PRD before the epics are published,
  and report what would make the per-epic story runs go wrong: an epic that bundles two themes or
  is too big to plan in one run, an epic a reader cannot understand without the PRD, an entity
  or actor some epic uses but no epic creates, a cross-epic dependency that is missing, wrong or
  in the wrong wave, an MVP epic that waits on a Later one, a requirement placed in the wrong
  epic. REVIEW ONLY: it writes one report, `epics-review.md`, with each finding, its target
  (`epics` or `order`), the epics and requirements it touches, a question with a proposed default
  where a person must decide, and the proposed change; it never edits the plan.
  `sdlc-plan-epics-create` (revise mode) and then `sdlc-plan-epics-order` apply it. Trigger this
  when the user says "review the epics", "are these epics ready", "check the epic breakdown", or
  as the reviewer step of `sdlc-wf-planning-epics`.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads `PRD.md`, `epics.md`, `epic-map.json` and
  `epic-order.md` / `.json`. Read-only: no edits outside its own report, no Jira writes. Runs on a
  different model family from the plan's author (ADR-035).
---

# sdlc-plan-epics-review — Review the Epic Plan and Order Before Publishing

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table
> in the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see
> `_SHARED-project-layout.md`. Current defaults: `docs/product/PRD.md`, `docs/product/epics.md`,
> `docs/product/epic-map.json`, `docs/product/epic-order.md` and `.json`, and this skill's
> report at `docs/product/epics-review.md`. This skill's own `templates/`, `references/` and
> `examples/` stay inside the skill folder.

Section guidance for this skill's template is in `references/template-guide.md`. Read it before
you fill the template.

> **Cost & context:** This skill runs at the model tier its workflow step sets. Read the PRD's
> requirement table, every epic's section and the order once. Do not load architecture or code.

> **Single responsibility (ADR-035):** this is a `reviewer` skill. It judges the plan that
> `sdlc-plan-epics-create` and `sdlc-plan-epics-order` wrote, and writes only
> `epics-review.md`. It never edits `epics.md`, `epic-map.json`, the order or Jira.

## Why this step exists
Once the epics are published, each one is planned in its own `sdlc-wf-planning-epic` run, often
by a different person. `sdlc-plan-epic-review` then sees one epic at a time and cannot catch a
gap *between* epics: two epics that both assume the other creates the accounts, a dashboard
epic in wave 1 that reads data a wave-3 epic produces. This review is the last moment the whole
plan is in one place.

## Input it expects
- `PRD.md` — the requirement table and feature areas.
- `epics.md` and `epic-map.json` from `sdlc-plan-epics-create`.
- `epic-order.md` and `epic-order.json` from `sdlc-plan-epics-order`.
- On a second or later pass: the previous `epics-review.md` and `epics-revisions.md`, to check
  that each earlier finding was applied.

## Output it produces
One file: `docs/product/epics-review.md` (from `templates/epics-review.md.tmpl`). Nothing else
changes. A later pass overwrites it; `epics-revisions.md` and git history keep the trail.

Each finding records:
- **Target:** `epics` (the plan: boundaries, scope, wording, requirement placement) or `order`
  (an edge or a wave). `sdlc-plan-epics-create` applies `epics` findings; `sdlc-plan-epics-order`
  applies `order` findings on its next pass.
- **Severity:** `Blocking` (a per-epic run would write stories for the wrong scope, or an epic
  could not be built in its wave) or `Advisory` (worth fixing, safe to publish as written).
- **Epics touched** and **Requirements touched** (FR/NFR ids).
- **Evidence:** the epic text, requirement or edge that shows the problem.
- **Question** with a **proposed default**, when the fix is a product decision.
- **Proposed change:** what the author should change. Proposed, not applied.

Plus a **PRD fit** verdict (`Fits` or `PRD gap`).

## Procedure

### Step 1 — Load the plan
Read the PRD requirement table, every epic section, the map and the order. On a later pass, also
read the previous report and `epics-revisions.md`, and fill **Earlier findings**: each one
Applied, Not applied, or Still open (no answer yet).

### Step 2 — Run the checklist
Work through `references/review-checklist.md`: epic boundaries and size, self-containment,
lifecycle across epics, requirement placement, the order's edges and waves, the MVP path, and
readiness for a per-epic run. Skip anything `verify.yaml` already checks mechanically on the
plan (every requirement in exactly one epic, the map and block agree, sections present, the order
covers every epic and is acyclic): those failures never reach you.

### Step 3 — Judge PRD fit
Set **PRD fit** to `Fits` unless the plan cannot be fixed without changing the PRD: two
requirements contradict each other, a requirement cannot be placed in any coherent epic, or an
entity every epic needs is missing from the PRD altogether. That is `PRD gap`, and it goes back
to a person and `sdlc-plan-prd-write` (see Outcomes).

### Step 4 — Write the report and stop
Write each finding with target, severity, evidence, question (with proposed default) and
proposed change, ordered by impact. Write `epics-review.md` and finish. Do not edit the plan,
even when the fix is one word.

> Anti-stall note: read the inputs and write the report in the same turn.

## What this skill is NOT
- Not an editor: `sdlc-plan-epics-create` (revise) and `sdlc-plan-epics-order` apply every change.
- Not a story review: stories do not exist yet. Cross-story gaps are `sdlc-plan-epic-review`'s
  job in each epic's run.
- Not a design review: no architecture or stack opinions.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: PRD fit is `PRD gap`: the plan cannot be fixed without changing the PRD, so a person revises the PRD (`sdlc-wf-planning-prd`) and starts again.
- **changes_requested**: At least one `Blocking` finding, or a question a person must answer. `sdlc-plan-epics-create` (revise) and then `sdlc-plan-epics-order` apply the report.
- **completed**: No `Blocking` findings (advisory ones may remain). The epics are ready to publish.

## Reference files
- `templates/epics-review.md.tmpl` — the report structure.
- `references/template-guide.md` — section-by-section guidance.
- `references/review-checklist.md` — what to look for, and what a real finding looks like.
- `examples/epics-review.md` — an illustrative pass over the Learn Portal plan.
