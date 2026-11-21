# Template guide — sdlc-plan-epics-order

Guidance for filling this skill's templates, section by section. Do not copy this guidance into
the output.

## `templates/epic-order.md.tmpl`

### Header

`Status` stays `AWAITING REVIEW`: the review and its gate come after this step. `Waves` is the
highest wave number.

### Waves

One `### Wave N` heading per wave, every epic exactly once, with its release tag. Under wave 2
and later, name each epic's dependencies.

### Dependencies

One row per edge, the same edges as `depends_on` in the `.json`. `Why` names the thing the
dependent epic uses and the other creates ("uses the student roster that LEARN-15 imports"),
not just "needs it first".

### Parallel groups

Which epics can be built at the same time by different teams, wave by wave. Note that story
planning (`sdlc-wf-planning-epic`) can run for every epic at once regardless of waves; the
waves constrain building, not planning.

### MVP path

The epic keys, in wave order, needed to ship every MVP requirement, and the same list in
`mvp_path` in the `.json`. If an MVP epic depends on a `Later` epic, say so here and list it
under Cycles and conflicts.

### Cycles and conflicts

"None", or each cycle with its recommended re-slice, each MVP-on-Later dependency, and any
inference that contradicts an existing Jira link.

## `templates/epic-order.schema.json`

`epic_key` values match `epic-map.json` exactly, draft keys included. Set `confidence:
provisional` on every `epic-body` and `lifecycle` edge.
