# Template guide — sdlc-plan-epics-review

Guidance for filling `templates/epics-review.md.tmpl`, section by section. Do not copy this
guidance into the output.

## `templates/epics-review.md.tmpl`

### Header

`Verdict` is `CLEAN` (no Blocking findings), `CHANGES REQUESTED` or `ESCALATE` (PRD gap). `Pass`
counts review passes in this run, starting at 1.

### Context loaded

The files read, one line each: PRD (feature areas, FR/NFR counts), epics (count, keys draft or
real), order (waves, edges, how many provisional), previous report and revisions on a later pass.

### PRD fit

Exactly one verdict line: `- **Verdict:** Fits` or `- **Verdict:** PRD gap`, then one reason.
PRD gap means the epics cannot be fixed without changing the PRD.

### Findings

One `### Finding N — <category>` per finding, with every bullet in the template. `Target` is
exactly `epics` or `order`. `Epics touched` lists keys as they appear in `epic-map.json`. Write
"none" for `Requirements touched` when only an edge is wrong.

### Open questions

Every question from the findings, numbered `Q-1`, `Q-2`, each with its proposed default. The
gate shows these to a person; the answers travel to the revise pass. A fast policy adopts the
defaults.

### Proposed changes

A short list grouped by target: what `sdlc-plan-epics-create` should change, then what
`sdlc-plan-epics-order` should change.

### Earlier findings

"First pass", or each earlier finding with `Applied`, `Not applied` or `Still open`.
