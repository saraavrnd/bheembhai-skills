---
name: sdlc-plan-prd-review
role: reviewer   # ADR-035: author | reviewer | integration
description: >
  Review a written PRD against the idea brief it came from, before anyone decomposes it into
  epics, and report what would make decomposition go wrong: a requirement that bundles several
  capabilities or cannot be tested, a user or goal from the brief that no requirement serves, an
  actor or entity that some requirement uses but none creates, an answered gate question the PRD
  ignores, scope that drifted beyond the idea. REVIEW ONLY: it writes one report, `prd-review.md`,
  with each finding, the requirements it touches, a question with a proposed default where a
  person must decide, and the proposed change; it never edits the PRD. `sdlc-plan-prd-write`
  (revise mode) applies it. Trigger this when the user says "review this PRD", "is this PRD ready
  for epics", "sanity check the requirements", or as the reviewer step of `sdlc-wf-planning-prd`.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads `PRD.md`, `idea-brief.md` and the run's original
  input. Read-only: no edits outside its own report, no Jira writes. Runs on a different model
  family from the PRD's author (ADR-035).
---

# sdlc-plan-prd-review — Review a PRD Before It Is Decomposed

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table
> in the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see
> `_SHARED-project-layout.md`. Current defaults: the PRD at `docs/product/PRD.md`, the brief at
> `docs/product/idea-brief.md`, and this skill's report at `docs/product/prd-review.md`. This
> skill's own `templates/`, `references/` and `examples/` stay inside the skill folder.

Section guidance for this skill's template is in `references/template-guide.md`. Read it before
you fill the template.

> **Cost & context:** This skill runs at the model tier its workflow step sets. A PRD and a
> brief are short; read both once, in full. Do not load architecture or code: the PRD comes
> before any design.

> **Single responsibility (ADR-035):** this is a `reviewer` skill. It judges the PRD that
> `sdlc-plan-prd-write` wrote and writes only `prd-review.md`. It never edits `PRD.md`, the brief
> or Jira. `sdlc-plan-prd-write` (revise mode) applies the proposed changes on the author's model
> family, and this step then reviews the result again.

## Why this step exists
A PRD error is the most expensive error in the chain: every epic, story, test and line of code
inherits it. `sdlc-plan-epic-review` catches problems across one epic's stories, but nothing
looked at the PRD itself before it fanned out. This is that look, made by a model from a
different family than the one that wrote it.

## Input it expects
- `PRD.md` from `sdlc-plan-prd-write`.
- `idea-brief.md` from `sdlc-plan-idea-frame`, including the answers given at its gate (they are
  in the run hand-off, and `sdlc-plan-prd-write` records them in the PRD's §8).
- The run's original input (`context.query`), to judge fidelity to the idea itself.
- On a second or later pass: the previous `prd-review.md` and `prd-revisions.md`, to check that
  each earlier finding was applied.

## Output it produces
One file: `docs/product/prd-review.md` (from `templates/prd-review.md.tmpl`). Nothing else
changes. A later pass overwrites it; `prd-revisions.md` and git history keep the trail.

Each finding records:
- **Severity:** `Blocking` (decomposition would build the wrong thing, or an epic could not be
  tested) or `Advisory` (worth fixing, safe to decompose as written).
- **Requirements touched:** FR/NFR ids, or the PRD section when no requirement exists yet.
- **Evidence:** the requirement text, brief line or answer that shows the problem.
- **Question** with a **proposed default**, when the fix is a product decision.
- **Proposed change:** what `sdlc-plan-prd-write` (revise) should change. Proposed, not applied.

Plus an **Idea fidelity** verdict (`Faithful` or `Drifted`) and a **Brief coverage** check.

## Procedure

### Step 1 — Load the PRD, the brief and the input
Read all three in full. On a later pass, also read the previous report and `prd-revisions.md`.

### Step 2 — Check the PRD against the brief
Fill **Brief coverage**: each target user, the value hypothesis, each constraint and each
answered (or defaulted) question from the brief — which requirement, NFR, scope line or
assumption carries it. Anything that nothing carries is a finding.

### Step 3 — Run the checklist
Work through `references/review-checklist.md`: atomicity and testability, lifecycle completeness,
scope and MVP boundary, NFR coverage, success metrics, decomposability into epics. Skip anything
`verify.yaml` already checks mechanically on the PRD (numbering, sections, tags, declared feature
areas): those failures never reach you.

### Step 4 — Judge fidelity
Set **Idea fidelity** to `Faithful` unless the PRD describes a materially different product from
the idea and the brief: different primary users, a different core problem, or an MVP that no
longer tests the value hypothesis. That is `Drifted`, and it is a person's call, not a revision
(see Outcomes).

### Step 5 — Write the report and stop
Write each finding with severity, evidence, question (with proposed default) and proposed change.
Order by impact. Write `prd-review.md` and finish. Do not edit the PRD, even when the fix is a
one-word change.

> Anti-stall note: read the inputs and write the report in the same turn.

## What this skill is NOT
- Not an editor: `sdlc-plan-prd-write` (revise) applies every change.
- Not a design review: no architecture, stack or data-model opinions. A requirement that says
  HOW instead of WHAT is a finding; proposing the HOW is not.
- Not a market review: it judges the PRD against the idea it was given, not against competitors.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: Idea fidelity is `Drifted`: the PRD describes a different product from the idea and brief, so a person must re-frame or accept the change.
- **changes_requested**: At least one `Blocking` finding, or a question a person must answer. `sdlc-plan-prd-write` (revise) applies the report.
- **completed**: No `Blocking` findings (advisory ones may remain). The PRD is ready for `sdlc-plan-epics-create`.

## Reference files
- `templates/prd-review.md.tmpl` — the report structure.
- `references/template-guide.md` — section-by-section guidance.
- `references/review-checklist.md` — what to look for, and what a real finding looks like.
- `examples/prd-review.md` — an illustrative pass over a draft of the Learn Portal PRD.
