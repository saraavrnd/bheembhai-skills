# Template guide — sdlc-plan-prd-review

Guidance for filling `templates/prd-review.md.tmpl`, section by section. Do not copy this
guidance into the output.

## `templates/prd-review.md.tmpl`

### Header

`Verdict` is `CLEAN` (no Blocking findings), `CHANGES REQUESTED` or `ESCALATE` (fidelity is
Drifted). `Pass` counts review passes in this run, starting at 1.

### Context loaded

The files read, one line each: PRD (feature areas, FR/NFR counts), brief (questions and which
were answered at the gate), previous report and revisions on a later pass.

### Idea fidelity

Exactly one verdict line: `- **Verdict:** Faithful` or `- **Verdict:** Drifted`, then one reason.
Drifted means a different product, not a missing requirement.

### Brief coverage

One row per target user, the value hypothesis, each constraint, each non-goal and each Q-n. The
right column names the FR/NFR ids, the scope line or the §8 assumption that carries it, or
`Not carried` (which is then a finding).

### Findings

One `### Finding N — <category>` block per real problem, ordered by impact. Categories come from
`references/review-checklist.md`. The severity line is exactly `- **Severity:** Blocking` or
`- **Severity:** Advisory`. Every FR/NFR id cited must exist in the PRD. If there are no
findings, write `None.`

### Open questions

Each question from the findings again, numbered `RQ-1`, `RQ-2`, … with its proposed default, so a
person at the gate can answer them in one place. `None.` if there are none.

### Proposed changes

The changes as a list `sdlc-plan-prd-write` (revise) can apply in order: requirement id (or
section) → change. Splits name the new requirements' wording.

### Earlier findings

On a later pass: each earlier finding → `Applied`, `Partly applied` (what remains) or `Not
applied`. On the first pass: `First pass.`
