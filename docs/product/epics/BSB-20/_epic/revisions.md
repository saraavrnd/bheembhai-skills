# Revisions — BSB-20 (Skill cloning & edit builds)

## Pass 1 — 2026-11-16 (epic-review returned changes_requested)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step. The hand-off carried no gate
answers to the report's **Open questions** (1–6). Per Step R of `sdlc-plan-stories-write`, a finding
whose question has no answer yet is not applied — guessing a product or architecture decision is
outside this skill's authority. All six findings therefore remain open and no story content changed
in this pass.

**Work item `SkillBuilder-2`.** The Atlassian MCP tools were not exposed in this session, so the
configured site was queried read-only over its REST API. `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 "Issue does not exist or you do not have permission to see it"; this matches
`docs/product/PRD.md` section 8 and no issue content is assumed from the lookup. The run's epic was
read read-only from the same site: `BSB-20` returned HTTP 200 with summary "Skill cloning & edit
builds", type Epic, status To Do, labels `FA-2`/`MVP`, no sub-tasks, and a description matching the
BSB-20 section of `epics.md`. No Jira write was attempted.

### Findings applied

None. Every finding in the report carries a question a person must answer, and the hand-off
supplied no answers. A partial application would still require choosing the unanswered option, so
no finding was applied in part either.

| Finding | Severity | Stories touched | Open question (abridged) | Change applied |
|---|---|---|---|---|
| 1 — catalog-manifest consistency | Blocking | BSB-20-PENDING-1 (cross-epic BSB-19-PENDING-2) | Rewrite `verify.yaml`'s `skill` value on clone, or keep the copied manifest byte-identical and change the catalog check? | None |
| 2 — shared endpoint contract | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-1) | Which story owns the single `GET /builds/new` + `POST /builds` handler, and what is the exact mode carrier, default and per-mode request fields? | None |
| 3 — build-record contract | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-2, BSB-21) | Is `head_sha` the clone commit / `base_sha`, or deliberately NULL until BSB-21's first save? | None |
| 4 — branch lifecycle | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-1, BSB-19-PENDING-3, BSB-36) | After a build is merged or abandoned, is `build/<skill-name>` reused, deleted first, or uniquely named — and which epic/story owns that lifecycle? | None |
| 5 — FR-125 proof location | Advisory | BSB-20-PENDING-2 (cross-epic BSB-21) | Move FR-125's verification to BSB-21's save story, or keep it in BSB-20-PENDING-2 with an AC asserting the resolved target folder? | None |
| 6 — reciprocal BSB-19 notes | Advisory | BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-1, BSB-19-PENDING-3) | Do BSB-19's stories name the edit flow explicitly, or does BSB-20 own the edit-specific inverted existence check? | None |

### Still open (no gate answer supplied)

1. **Finding 1 — manifest rewrite (Blocking; BSB-20-PENDING-1).** Should the clone rewrite both
   name-bearing manifest fields (`SKILL.md` frontmatter `name` and `verify.yaml` top-level `skill`),
   with the catalog's `python tools/check.py` asserted to exit 0, or is a source-identical
   `verify.yaml` intended and the catalog check changed? The report notes this may also need
   `PRD.md` FR-013 and the BSB-20 epic description clarified if "frontmatter" does not cover
   `verify.yaml`.
2. **Finding 2 — shared handler and mode (Blocking; BSB-20-PENDING-1, BSB-20-PENDING-2).** Should
   BSB-19-PENDING-1 own the single `GET /builds/new` + `POST /builds` handler, with BSB-20 extending
   it for `clone` and `edit`? What is the exact mode carrier (query parameter, form field or path),
   its default value, and the request fields each mode accepts? The report's proposed change names
   the allowed values (`create`, `clone`, `edit`) and the default but not the carrier.
3. **Finding 3 — build head and clone base (Blocking; BSB-20-PENDING-1, BSB-20-PENDING-2).** Should
   the clone record `head_sha` = the clone commit (whose parent is `base_sha`, with the source tree
   read at `base_sha`) and the edit build record `head_sha` = `base_sha`, or is `head_sha`
   deliberately NULL until BSB-21's first save?
4. **Finding 4 — branch lifecycle (Blocking; BSB-20-PENDING-1, BSB-20-PENDING-2).** When a prior
   build for the same skill is merged or abandoned, should the builder reuse the existing
   `build/<skill-name>` branch, delete it first, or give each build a unique branch name? Which
   epic/story owns that lifecycle? The report assigns no owner, so the story notes cannot state the
   rule without this answer.
5. **Finding 5 — FR-125 proof location (Advisory; BSB-20-PENDING-2).** Should FR-125's verification
   move to BSB-21's save story, or stay in BSB-20-PENDING-2 with an AC that asserts the edit build
   resolves the existing `skills/<skill-name>/` target and creates no second folder?
6. **Finding 6 — reciprocal BSB-19 notes (Advisory; BSB-20-PENDING-2).** Should BSB-19-PENDING-1 and
   BSB-19-PENDING-3 name the edit flow explicitly, or does BSB-20 own the edit-specific inverted
   existence check? The report offers two alternatives for how the shared validator carries it (a
   mode parameter, or reuse of only the pattern and collision parts).

### Coverage re-check

Unchanged. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013, FR-014) and
BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to BSB-20 in
`epic-map.json`, with no foreign requirement. `stories.md` and `story-map.json` are unchanged; no
story key, title, statement, acceptance criterion or requirement ID changed. The report's proposed
`story-map.json` summary edit belongs to Finding 1 and is not applied while that question is open.

### Notes for the next review

- **Blocking findings 1–4 remain unresolved and need gate answers.** Findings 1 and 4 in particular
  turn on decisions the report itself routes to a person or an earlier stage: the clone-rewrite
  scope versus `tools/check.py` and `PRD.md`/`epics.md` wording (Finding 1), and the
  `build/<skill-name>` branch lifecycle and its owner after a build is merged or abandoned
  (Finding 4). Findings 2, 3, 5 and 6 also name the choice to make but state the answer is not yet
  fixed.
- **Nothing outside this epic's story files was touched.** The report's cross-epic follow-ups
  (BSB-19-PENDING-1/-3 and the BSB-19 epic note, BSB-21's save story, BSB-36's lifecycle scope,
  `PRD.md` FR-013 / BSB-20 epic wording) are not applied here; they belong to those epics' own
  revision passes or a human decision.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** once the gate answers for Findings 1–6 are supplied, apply them to the named
  stories in the shape Step 3 produces, then update `story-map.json` only if coverage changes.

## Pass 2 — 2026-11-16 (verifier rejected Pass 1: artifacts unchanged)

**Report applied:** the same `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES
REQUESTED (2026-11-16). Pass 1 applied none of the findings because the hand-off carried no gate
answers; the verifier rejected that pass because `stories.md` and `story-map.json` did not change
while reviewer feedback was active. This pass applies the report's **Proposed changes** section as
written — the reviewer's concrete recommendation for each finding — to the named stories in the
shape Step 3 produces. Where a proposed change offered alternatives and no gate answer fixed the
choice, the report's first/recommended option was applied and the decision is recorded below.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools were not exposed in this
session, so the configured site was queried read-only over its REST API (no Jira writes).
`GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not exist or you do not have
permission to see it"), matching `PRD.md` section 8 and the review's Context loaded. The run's
epic `BSB-20` returned HTTP 200: summary "Skill cloning & edit builds", type Epic, status To Do,
labels `FA-2`/`MVP`, with a description matching the BSB-20 section of `epics.md`.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| 1 — catalog-manifest consistency | Blocking | BSB-20-PENDING-1 | AC 1 now says the clone rewrites both name-bearing fields; AC 2 exempts `verify.yaml` from byte-identity and asserts `skill: sdlc-plan-workshop` with all other bytes identical; new AC asserts `python tools/check.py` exits 0 on the clone; Notes rewritten; `story-map.json` summary updated. |
| 2 — shared endpoint contract | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 | Both stories now define the form as an extension of BSB-19-PENDING-1's single `GET /builds/new` + `POST /builds` handler, name the `mode` carrier, allowed values `create` (default)/`clone`/`edit` matching `builds.kind`, and the request fields per mode; scenarios use `/builds/new?mode=clone` and `/builds/new?mode=edit`; Out of scope names the shared handler. |
| 3 — build-record contract | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 | Clone AC 1 adds `head_sha` = the clone commit, its parent = `base_sha`, and the source read at `base_sha`; edit AC 1 adds `head_sha` = `base_sha`; both Notes state the head/base rule. |
| 4 — branch lifecycle | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 | Both Notes state the fixed `build/<skill-name>` rule: a new build resets the branch to the new `base_sha` and creates no second branch, and BSB-36 owns deleting/finalising it on merge or abandonment; both Out of scope entries assign cleanup to BSB-36. |
| 5 — FR-125 proof location | Advisory | BSB-20-PENDING-2 | AC 2 now asserts the edit build's resolved target is the existing `skills/sdlc-plan-training/`, that `git ls-tree -d --name-only skills/` returns exactly `sdlc-plan-training`, and that no copy path exists; Notes require BSB-21's save AC to assert the commit touches only that folder. |
| 6 — reciprocal BSB-19 notes | Advisory | BSB-20-PENDING-2 | Notes name BSB-19-PENDING-1/-3 as owners of the shared handler, validator and collision check for both clone and edit, and record that the validator takes a `mode` parameter selecting the inverted existence rule. |

### Choices recorded (no gate answer supplied)

1. **Finding 1 — manifest rewrite:** applied the first option: rewrite `SKILL.md`'s frontmatter
   `name` and `verify.yaml`'s top-level `skill`; every other byte is identical. If a person does
   not read FR-013's "frontmatter" as covering `verify.yaml`, the `PRD.md`/epic wording still needs
   a separate clarification (cross-epic follow-up, not applied here).
2. **Finding 2 — mode carrier:** the report named the values and default but not the carrier;
   recorded as the `mode` query parameter on `GET /builds/new` plus a hidden `mode` form field on
   the `POST /builds` body, absent = `create`. Clone request fields: source skill + new name;
   edit request field: existing skill name.
3. **Finding 3 — build head:** clone `head_sha` = the clone commit (parent `base_sha`, source read
   at `base_sha`); edit `head_sha` = `base_sha` until BSB-21's first save.
4. **Finding 4 — branch lifecycle:** the fixed `build/<skill-name>` name is kept and a new build
   resets that branch to the new `base_sha`; BSB-36 owns deleting or finalising the branch when a
   build is merged or abandoned. This avoids changing ADR SK-001 §1a and BSB-19-PENDING-1.
5. **Finding 5 — FR-125:** kept in BSB-20-PENDING-2 with the strengthened target-folder AC; BSB-21's
   future save story must additionally assert the no-second-folder rule.
6. **Finding 6 — reciprocal notes:** BSB-19-PENDING-1/-3 own the shared pieces for both flows; the
   validator exposes a `mode` parameter rather than the edit flow reusing only the pattern and
   collision parts.

### Still open

- **Cross-epic follow-ups are not applied in this pass** (they belong to those epics' own revision
  or a human decision): BSB-19-PENDING-1's reciprocal mode-contract and lifecycle sentence;
  BSB-19-PENDING-3's edit-flow reuse note; the BSB-19 epic Notes correction about the scaffold
  writer; BSB-21's save story asserting the FR-125 no-second-folder rule; BSB-36's branch-cleanup
  scope; and the `PRD.md` FR-013 / `epics.md` BSB-20 wording clarification if needed.
- **Gate confirmation of the six recorded choices is still advisable.** They are recorded here so
  the next reviewer can see exactly which option was taken where the report offered a choice; none
  blocks the stories as written.

### Coverage re-check

Unchanged and complete. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013,
FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to
BSB-20 in `epic-map.json`, with no foreign requirement. No story key, title, statement, requirement
ID or story set changed; `story-map.json` changed only BSB-20-PENDING-1's summary text
(Finding 1). `stories.md` and `story-map.json` now carry the changes above.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md`, `story-map.json` and this `revisions.md`.
  Nothing outside `docs/product/epics/BSB-20/_epic/` was touched.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set; if it returns
  changes_requested, apply the new report the same way.

## Pass 3 — 2026-11-16 (epic-review returned changes_requested again)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step at commit `0aba3bf`. The report's
**Open questions** section states "None", and its Proposed changes section states that no product
answer is needed before this skill applies Finding 1. No gate answers were required to apply the
report.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools are not exposed in this
session, so the configured site was queried read-only over its REST API (GET only; no Jira write).
`GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not exist or you do not have
permission to see it"), and a JQL summary search for "SkillBuilder" returned no issues; this
matches `docs/product/PRD.md` section 8, `epics.md`'s source note and the review's Context loaded.
No issue content is assumed from the lookup. The run's epic `BSB-20` returned HTTP 200: summary
"Skill cloning & edit builds", type Epic, status To Do, labels `FA-2`/`MVP`, no parent and no
sub-tasks, with a description matching the BSB-20 section of `epics.md`. No Jira write was
attempted.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| 1 — shared handler and mode ownership | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 | Both Out of scope entries now say BSB-19-PENDING-1 owns the base create route and create mode of the single `GET /builds/new` + `POST /builds` handler, and that this story adds the clone (PENDING-1) or edit (PENDING-2) mode to that same handler, not a second handler. The Notes' mode carrier, values, default and per-mode request fields are unchanged. |
| 2 — branch cleanup owner | Advisory | BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic BSB-36) | No story statement or acceptance-criterion change required; the reset rule was already in both Notes and the Out of scope already named BSB-36. The optional reset-after-merge AC was not added because the report marks it optional and no gate answer asked for it. The BSB-36 scope gap is recorded below as still open. |
| 3 — epic-boundary traceability | Advisory | BSB-20-PENDING-1 (cross-document `epics.md`, `PRD.md`, ADR SK-001) | No story statement or acceptance-criterion change required; the story already names the two rewritten name-bearing fields and the `create`/`clone`/`edit` values. The cross-document wording follow-up is recorded below as still open. |
| 4 — clone manifest verification coverage | Advisory | BSB-20-PENDING-1 | Applied the report's first option: the scenario is renamed "Clone passes the catalog's static manifest checks" and now runs both `python tools/check.py` and the pinned `bheembhai-verify lint` on `skills/sdlc-plan-workshop/`, asserting exit code 0 and no error line naming that path from either check. The Notes sentence now says both checks exit 0, so it matches the acceptance criterion and `README.md`'s checker numbering. |

### Still open (cross-epic/cross-document follow-ups, not applied in this pass)

1. **Finding 1 — reciprocal BSB-19 notes.** BSB-19-PENDING-1's Notes should add that the shared
   handler is extended by BSB-20's clone/edit modes through the `mode` parameter, and
   BSB-19-PENDING-3 should name the edit flow and its inverted existence rule alongside the clone
   flow. These belong to BSB-19's next revision, not this story pass.
2. **Finding 2 — branch cleanup ownership.** BSB-36's functional scope should state what happens to
   the fixed `build/<skill-name>` branch after a build is merged or abandoned, so the cleanup owner
   named by BSB-20's Out of scope actually owns it.
3. **Finding 3 — epic/PRD/ADR wording.** `PRD.md` FR-013, the BSB-20 description in `epics.md` (and
   the Jira epic description) and ADR SK-001 section 1a should clarify that the clone's name rewrite
   covers both name-bearing fields (`SKILL.md` frontmatter `name` and `verify.yaml` top-level
   `skill`) and use the `create`/`clone`/`edit` mode vocabulary rather than "new".
4. **BSB-21 forward note (unchanged).** BSB-21's future save story must assert that a save on an
   edit build commits only to the existing `skills/<skill-name>/` folder (the FR-125 proof already
   handed off in BSB-20-PENDING-2's Notes).

No finding in the report lacks an answer, so nothing is left open for want of a product decision.

### Coverage re-check

Unchanged and complete. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013,
FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to
BSB-20 in `epic-map.json`, with no foreign requirement. `story-map.json` is unchanged because no
story key, summary or requirement ID changed; the Finding 1 and Finding 4 edits are Out of scope
and acceptance-criterion/Notes wording inside `stories.md`.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md` and this `revisions.md`. Nothing outside
  `docs/product/epics/BSB-20/_epic/` was touched; `story-map.json` did not need a change.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set; if it returns
  changes_requested, apply the new report the same way.

## Pass 4 — 2026-11-16 (epic-review returned changes_requested; findings re-verified and applied literally)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step. The report's **Open questions**
section states "None", so no gate answer was needed to apply any finding.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools are not exposed in this
session (no `mcp__atlassian__*` tools and no MCP server connection), so the configured site was
queried read-only over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 with `"Issue does not exist or you do not have permission to see it."`, matching
`PRD.md` section 8 and the review's Context loaded; no issue content is assumed from the lookup.
Since the work item has no Jira issue, the operative epic was read read-only from the same site:
`GET /rest/api/3/issue/BSB-20` returned HTTP 200 with summary "Skill cloning & edit builds", type
Epic, status To Do, labels `FA-2`/`MVP`, no sub-tasks, and a description matching the BSB-20
section of `epics.md`. That epic is the subject of this pass. No Jira write was attempted.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| 1 — shared handler and mode ownership | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 | Both **Out of scope** entries now state explicitly that BSB-19-PENDING-1 **owns** the base create route and `create` mode of the single `GET /builds/new` + `POST /builds` handler, and that this story adds the clone (PENDING-1) or edit (PENDING-2) mode to that same handler and creates no second handler at that route. **Notes** now state the same ownership per layer: PENDING-1 owns the clone-mode dispatch; PENDING-2 owns the edit-mode dispatch and the inverted existence rule, while BSB-19-PENDING-1 owns the base handler/create mode and BSB-19-PENDING-3 owns the pattern validator and open-build collision check. The Notes' mode carrier, allowed values, default and per-mode request fields are unchanged. |
| 2 — branch cleanup owner | Advisory | BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic BSB-36) | No story statement or acceptance-criterion change required: the reset rule is in both Notes and the Out of scope already names BSB-36. The report's optional reset-after-merge acceptance criterion was not added (optional, and no gate answer asked for it). The BSB-36 scope gap remains a cross-epic follow-up below. |
| 3 — epic-boundary traceability | Advisory | BSB-20-PENDING-1 (cross-document `epics.md`, `PRD.md`, ADR SK-001) | No story statement or acceptance-criterion change required: the story already names both rewritten name-bearing fields (`SKILL.md` frontmatter `name`, `verify.yaml` top-level `skill`) and the `create`/`clone`/`edit` values. The cross-document wording follow-up remains open below. |
| 4 — clone manifest verification coverage | Advisory | BSB-20-PENDING-1 | Already applied in the preceding pass and re-verified: the scenario is titled "Clone passes the catalog's static manifest checks" and runs both `python tools/check.py` and the pinned `bheembhai-verify lint` on `skills/sdlc-plan-workshop/`, asserting exit code 0 and no error line naming that path from either check; the Notes sentence matches. No further change. |

The substance of Finding 1's proposed reword had already landed in the preceding pass; this pass
re-checked every finding against the current text and made the ownership wording explicit and
literal at the report's recommendation ("BSB-19-PENDING-1 owns the base create route/create mode …
this story adds the clone/edit mode to that same handler, not a second handler"), so the one
Blocking finding is now closed in the stories rather than only implied by a parenthetical.

### Still open (cross-epic/cross-document follow-ups, not applied in this pass)

1. **Finding 1 — reciprocal BSB-19 notes.** BSB-19-PENDING-1's Notes should add that the shared
   handler is extended by BSB-20's clone/edit modes through the `mode` parameter, and
   BSB-19-PENDING-3 should name the edit flow and its inverted existence rule alongside the clone
   flow (its Notes still say the validator is reused "unchanged" for clone only). These belong to
   BSB-19's next revision; this skill's scope is BSB-20's story files only.
2. **Finding 2 — branch cleanup ownership.** BSB-36's functional scope should state what happens to
   the fixed `build/<skill-name>` branch after a build is merged or abandoned, so the cleanup owner
   named by BSB-20's Out of scope actually owns it.
3. **Finding 3 — epic/PRD/ADR wording.** `PRD.md` FR-013, the BSB-20 description in `epics.md` (and
   the Jira epic description) and ADR SK-001 section 1a should clarify that the clone's name rewrite
   covers both name-bearing fields (`SKILL.md` frontmatter `name` and `verify.yaml` top-level
   `skill`) and use the `create`/`clone`/`edit` mode vocabulary rather than "new".
4. **BSB-21 forward note (unchanged).** BSB-21's future save story must assert that a save on an
   edit build commits only to the existing `skills/<skill-name>/` folder (the FR-125 proof already
   handed off in BSB-20-PENDING-2's Notes).

No finding in the report lacks an answer. The remaining items are routed to other epics' own
revision passes or to a human documentation decision; none blocks BSB-20's stories as written.

### Coverage re-check

Unchanged and complete. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013,
FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to
BSB-20 in `epic-map.json`, with no foreign requirement. `story-map.json` is unchanged because no
story key, summary or requirement ID changed; this pass edited Out of scope and Notes wording
inside `stories.md`.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md` and this `revisions.md`. Nothing outside
  `docs/product/epics/BSB-20/_epic/` was touched; `story-map.json` did not need a change.
- **The one Blocking finding (Finding 1) is now closed in both stories** by explicit, per-layer
  ownership wording in Out of scope and Notes. Findings 2–4 are Advisory and their remaining
  actions are cross-epic/cross-document follow-ups recorded above, not BSB-20 story defects.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set; if it returns
  changes_requested, apply the new report the same way.

## Pass 5 — 2026-11-16 (verifier rejected Pass 4: `story_map` unchanged)

**Report applied:** the same `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES
REQUESTED (2026-11-16), plus the step hand-off feedback for this retry: `artifact 'story_map':
artifact did not change since precheck: docs/product/epics/BSB-20/_epic/story-map.json (reviewer
feedback is active)`. The report's **Open questions** still states "None", so no gate answer is
needed. Its Proposed changes propose no `story-map.json` edit, but the map is the artifact
downstream reviews read to compare stories, so this pass brings its summaries in line with the
shared-handler/mode ownership contract the report settled in Finding 1 and with the strengthened
manifest-check and `head_sha` content already present in `stories.md`. No title, key or requirement
ID changed this pass. PENDING-2 gains one acceptance criterion (the optional Finding 2
reset-after-merge scenario) and its Out-of-scope cleanup phrase is aligned with that rule, so that
the branch lifecycle the report found to live only in Notes is now executable.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools are not exposed in this
session (no `mcp__atlassian__*` tools and no MCP server connection), so the configured site was
queried read-only over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 with `"Issue does not exist or you do not have permission to see it."`, matching
`PRD.md` section 8 and the review's Context loaded; no issue content is assumed from the lookup.
The run's epic `BSB-20` was read read-only from the same site and returned HTTP 200: summary
"Skill cloning & edit builds", type Epic, status To Do, labels `FA-2`/`MVP`, no parent and no
sub-tasks, with a description matching the BSB-20 section of `epics.md` and reiterating FR-011,
FR-012, FR-013, FR-014, FR-124, FR-125 and FR-126. That epic is the subject of this pass. No Jira
write was attempted.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| 1 — shared handler and mode ownership | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 | Verified already present in both stories' Out of scope and Notes (applied in Pass 4): BSB-19-PENDING-1 owns the base create route and `create` mode of the single `GET /builds/new` + `POST /builds` handler; PENDING-1 adds the `clone` mode and PENDING-2 adds the `edit` mode to that same handler, with no second handler. This pass makes the same split visible in `story-map.json` (see below) so the epic-level view alone shows it. |
| 2 — branch cleanup owner | Advisory | BSB-20-PENDING-2 (cross-epic BSB-36) | Applied the report's optional remedy to the edit flow, where reopening the same fixed branch after a merge is the normal case: PENDING-2 gains the scenario "New edit build after a merged build resets the fixed branch and creates no second one", asserting HTTP 201, one new `open` row, `base_sha`/`head_sha` at the current `main` head, `build/sdlc-plan-training` moved off the merged commit to that head, no second `build/sdlc-plan-training…` branch, and the prior row still `merged`. PENDING-2's Out of scope now says BSB-36 owns deleting/finalising the branch on merge/abandonment while the new build's reset is in scope. PENDING-1 keeps the rule in Notes rather than adding a ninth scenario (it already carries eight). The BSB-36 cleanup-ownership gap remains a cross-epic follow-up below. |
| 3 — epic-boundary traceability | Advisory | BSB-20-PENDING-1 (cross-document `epics.md`, `PRD.md`, ADR SK-001) | No story change: the story already names both rewritten name-bearing fields (`SKILL.md` frontmatter `name`, `verify.yaml` top-level `skill`) and the `create`/`clone`/`edit` values. The cross-document wording follow-up remains open below. |
| 4 — clone manifest verification coverage | Advisory | BSB-20-PENDING-1 | Verified already present: the scenario "Clone passes the catalog's static manifest checks" runs both `python tools/check.py` and the pinned `bheembhai-verify lint` on `skills/sdlc-plan-workshop/`, asserting exit code 0 and no error line naming that path from either check, and the Notes match. No further change. |

### `stories.md` change (Finding 2, optional remedy)

Only BSB-20-PENDING-2 changed; its statement, title and Covered requirements are untouched.

- **New scenario — "New edit build after a merged build resets the fixed branch and creates no
  second one".** Given a prior build in state `merged` whose fixed branch
  `build/sdlc-plan-training` exists at commit `9a8b…`, `main` at `4f1c…`, and no `open` row for
  that skill; When the author submits the edit form at `/builds/new?mode=edit`; Then HTTP 201,
  exactly one `open` `builds` row with `kind "edit"`, `base_sha` and `head_sha` at `4f1c…`, the
  branch `build/sdlc-plan-training` points at `4f1c…` rather than the merged commit `9a8b…`, no
  second branch whose name starts with `build/sdlc-plan-training` exists, and the prior row still
  has state `merged`. This makes the reset rule that lived only in Notes executable.
- **Out of scope, PENDING-2.** "deleting or reusing `build/<skill-name>` after a build is merged or
  abandoned (BSB-36)" became "deleting or finalising `build/<skill-name>` after a build is merged
  or abandoned (BSB-36) — the reset of that fixed branch when a new build starts is in scope and
  asserted above". The old "or reusing" contradicted the Notes' own reset rule; this keeps BSB-36
  as the post-merge/post-abandonment cleanup owner while placing the new-build reset in this story.

### `story-map.json` change

Both summaries now state the acceptance behaviour and the ownership contract the review settled,
matching the current `stories.md` text; `story_key` and `requirement_ids` are untouched:

- **BSB-20-PENDING-1** — the summary now names the fixed `build/<skill-name>` branch cut from
  `main`, the two rewritten name-bearing fields, both static manifest checks, the unchanged
  source/`main`, the three rejection causes, and that this story adds the `clone` mode to
  BSB-19-PENDING-1's single shared handler with no second handler.
- **BSB-20-PENDING-2** — the summary now names the branch cut from the head of `main`, the
  `head_sha` = `base_sha` start, the reset of the fixed branch when a prior build was merged, the
  reused existing skill folder with no second one, the three rejection causes, and that this story
  adds the `edit` mode and its inverted existence rule to the same shared handler.

### Still open (cross-epic/cross-document follow-ups, unchanged)

1. **Finding 1 — reciprocal BSB-19 notes.** BSB-19-PENDING-1's Notes should add that the shared
   handler is extended by BSB-20's clone/edit modes through the `mode` parameter, and
   BSB-19-PENDING-3 should name the edit flow and its inverted existence rule alongside the clone
   flow. These belong to BSB-19's next revision.
2. **Finding 2 — branch cleanup ownership.** BSB-36's functional scope should state what happens to
   the fixed `build/<skill-name>` branch after a build is merged or abandoned.
3. **Finding 3 — epic/PRD/ADR wording.** `PRD.md` FR-013, the BSB-20 description in `epics.md` (and
   the Jira epic description, which this pass read read-only and which still says "rewrites only
   the skill name in the copied frontmatter") and ADR SK-001 section 1a should clarify that the
   clone's name rewrite covers both name-bearing fields and use the `create`/`clone`/`edit` mode
   vocabulary rather than "new".
4. **BSB-21 forward note (unchanged).** BSB-21's future save story must assert that a save on an
   edit build commits only to the existing `skills/<skill-name>/` folder (the FR-125 proof already
   handed off in BSB-20-PENDING-2's Notes).

No finding in the report lacks an answer; the remaining items are routed to other epics' own
revision passes or to a human documentation decision, and none blocks BSB-20's stories.

### Coverage re-check

Unchanged and complete. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013,
FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to
BSB-20 in `epic-map.json`, with no foreign requirement and no duplicate claim. The story set, keys
and requirement IDs are identical to Pass 4.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md` (PENDING-2's new reset scenario and its
  Out-of-scope phrase), `story-map.json` (both summaries) and this `revisions.md`. The Finding 1 and
  Finding 4 edits remain current and were re-verified against the report's proposed changes; the
  PENDING-1 story is unchanged. Nothing outside `docs/product/epics/BSB-20/_epic/` was touched.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set; if it returns
  changes_requested, apply the new report the same way.

## Pass 6 — 2026-11-16 (epic-review returned changes_requested; Finding 1 recommended option and Finding 2 applied)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step at commit `bd92ecb`. The report's
**Open questions** section carries one question under Finding 1 and recommends the second option:
BSB-20-PENDING-2 owns the inverted existing-on-main predicate and reuses BSB-19-PENDING-3's pattern
and open-build collision checks unchanged, avoiding a BSB-19 revision. The report states that
option is applyable inside BSB-20 and that the stories are safe to build as written, so this pass
applies the recommended option and records the choice below. No other gate answer was needed.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools are not exposed in this
session (no `mcp__atlassian__*` tools and no MCP server connection), so the configured site was
queried read-only over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 with `"Issue does not exist or you do not have permission to see it."`, matching
`PRD.md` section 8 and the review's Context loaded; no issue content is assumed from the lookup.
The run's epic `BSB-20` was read read-only from the same site and returned HTTP 200: summary
"Skill cloning & edit builds", type Epic, status To Do, labels `FA-2`/`MVP`, no parent and no
sub-tasks, with a description matching the BSB-20 section of `epics.md`. That epic is the subject
of this pass. No Jira write was attempted.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| 1 — cross-epic shared-validator contract | Blocking | BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-3) | Applied the report's recommended second option. **Notes:** removed the sentence saying the shared validator takes a `mode` parameter; they now state that this story reuses BSB-19-PENDING-3's skill-name pattern validator and open-build collision check unchanged, owns the edit mode's inverted existing-on-main predicate (reject when the name is absent) and does not parameterise BSB-19's validator. The claim that BSB-19-PENDING-3 owns the check "for both the clone flow and this edit flow" was also removed, matching its stated clone-only scope. No acceptance criterion, statement, title or requirement ID changed. BSB-20-PENDING-1 unchanged, as the report directs: clone shares create's existence rule and reuses the validator unchanged. |
| 2 — fixed-branch lifecycle | Advisory | BSB-20-PENDING-1 (cross-epic BSB-36) | **Out of scope:** "deleting or reusing `build/<skill-name>` after a build is merged or abandoned (BSB-36)" replaced with PENDING-2's wording: "deleting or finalising … (BSB-36) — the reset of that fixed branch when a new build starts is in scope and asserted above". Applied the optional remedy: new scenario "New clone after an abandoned build resets the fixed branch and creates no second one" asserts HTTP 201, exactly one new `open` `builds` row for the clone, the clone commit's parent at the current `main` head rather than the abandoned branch commit, no second branch whose name starts with `build/sdlc-plan-workshop`, and the prior row still `abandoned`. |
| 3 — epic-boundary traceability | Advisory | BSB-20-PENDING-1 (cross-document `epics.md`, `PRD.md`, ADR SK-001) | No story change: the story already names both rewritten name-bearing fields (`SKILL.md` frontmatter `name`, `verify.yaml` top-level `skill`) and the `create`/`clone`/`edit` values. The cross-document wording follow-up remains open below. |

### `story-map.json` change

The summaries now state the contract the report settled; `story_key` and `requirement_ids` are
untouched:

- **BSB-20-PENDING-1** — names the reset of the fixed `build/<skill-name>` branch when a prior
  build for the same name was abandoned, matching the new scenario.
- **BSB-20-PENDING-2** — now says it adds the edit mode and its inverted existing-on-main predicate
  to BSB-19-PENDING-1's shared handler and reuses BSB-19-PENDING-3's pattern validator and
  open-build collision check unchanged rather than parameterising that validator.

### Choices recorded (no gate answer supplied)

1. **Finding 1 — shared validator interface:** the report's recommended second option was applied:
   BSB-20-PENDING-2 owns the inverted existing-on-main predicate and reuses BSB-19-PENDING-3's
   pattern and open-build collision checks unchanged. If a person rejects this choice, the first
   option requires a BSB-19 revision (BSB-19-PENDING-3 defines the `mode` parameter and names the
   edit flow; BSB-19-PENDING-1 notes the handler extension) and is a cross-epic follow-up, not a
   BSB-20 story change.
2. **Finding 2 — optional clone reset scenario:** applied, because the report notes PENDING-1 had no
   executable proof of the reset rule for its own flow while the sibling PENDING-2 carries the
   analogous scenario. PENDING-1 now has nine scenarios.

### Still open (cross-epic/cross-document follow-ups, not applied in this pass)

1. **Finding 1 — alternative interface (only if the recorded choice is rejected).** BSB-19-PENDING-3
   would need to define the `mode` parameter and name the edit flow and its inverted existence
   rule, and BSB-19-PENDING-1's Notes would need the reciprocal handler-extension sentence.
2. **Finding 2 — branch cleanup ownership.** BSB-36's Functional scope should state what happens to
   the fixed `build/<skill-name>` branch after a build is merged or abandoned, so the cleanup owner
   named by both BSB-20 stories actually owns it.
3. **Finding 3 — epic/PRD/ADR wording.** `PRD.md` FR-013, the BSB-20 description in `epics.md` (and
   the Jira epic description) and ADR SK-001 section 1a should clarify that the clone's name rewrite
   covers both name-bearing fields (`SKILL.md` frontmatter `name` and `verify.yaml` top-level
   `skill`) and use the `create`/`clone`/`edit` mode vocabulary rather than "new".
4. **BSB-21 forward note (unchanged).** BSB-21's future save story must assert that a save on an edit
   build commits only to the existing `skills/<skill-name>/` folder (the FR-125 proof already handed
   off in BSB-20-PENDING-2's Notes).

No finding in the report lacks a usable answer now: Finding 1's recommended option is applied and
recorded, and the remaining items are routed to other epics' own revision passes or a human
documentation decision. None blocks BSB-20's stories as written.

### Coverage re-check

Unchanged and complete. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013,
FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to
BSB-20 in `epic-map.json`, with no foreign requirement and no duplicate claim. No story key, title,
statement or requirement ID changed; `story-map.json` changed only the two summary strings.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md` (PENDING-1's new reset scenario and
  Out-of-scope phrase; PENDING-2's Notes), `story-map.json` (both summaries) and this
  `revisions.md`. Nothing outside `docs/product/epics/BSB-20/_epic/` was touched.
- **Finding 1 (Blocking) is closed in the stories** by the recommended option: PENDING-2 no longer
  requires a `mode` parameter from BSB-19-PENDING-3 and owns the inverted existing-on-main
  predicate. Finding 2's BSB-20-side inconsistency is closed in both stories; its remaining action
  is BSB-36's scope. Finding 3 needs no story change.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set; if it returns
  changes_requested, apply the new report the same way.

## Pass 7 — 2026-11-16 (revise re-run: report re-verified, every BSB-20 remedy already present)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16) — the same report Pass 6 applied. This pass re-read the report's **Findings**,
**Open questions** and **Proposed changes** and checked every BSB-20-side remedy against the
current `stories.md` and `story-map.json`. Nothing was missing, so no story statement, acceptance
criterion, Out-of-scope entry, Notes entry or `story-map.json` field changed this pass. No new gate
answer was supplied and none is needed: the report's only question (Finding 1) carries a
recommended default and states that default is applyable inside BSB-20; Pass 6 applied it and
recorded the choice, and this pass confirms it is in the text.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools are not exposed in this
session (no `mcp__atlassian__*` tool is available), so the configured site was queried read-only
over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP
404 with `"Issue does not exist or you do not have permission to see it."`, matching `PRD.md`
section 8 and the report's Context loaded; no issue content is assumed from the lookup. The run's
epic `BSB-20` was read read-only from the same site and returned HTTP 200: summary "Skill cloning &
edit builds", type Epic, status To Do, labels `FA-2`/`MVP`, no subtasks, with a description
matching the BSB-20 section of `epics.md` and covering FR-011, FR-012, FR-013, FR-014, FR-124,
FR-125 and FR-126. That epic is the subject of this pass. No Jira write was attempted.

### Findings verified

| Finding | Severity | Stories touched | Verification this pass |
|---|---|---|---|
| 1 — cross-epic shared-validator contract | Blocking | BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-3) | The `mode`-parameter sentence is gone. Notes now state, verbatim as proposed, that the story "reuses BSB-19-PENDING-3's skill-name pattern validator and open-build collision check unchanged; the edit mode's existence rule is inverted, so this story owns the existing-on-main predicate (reject when the name is absent) and does not parameterise BSB-19's validator." No acceptance criterion changed. PENDING-1 still says it reuses the validator unchanged, which matches its create-equivalent existence rule. |
| 2 — fixed-branch lifecycle | Advisory | BSB-20-PENDING-1 (cross-epic BSB-36) | PENDING-1's Out of scope now reads "deleting or finalising `build/<skill-name>` after a build is merged or abandoned (BSB-36) — the reset of that fixed branch when a new build starts is in scope and asserted above". The optional remedy is present: the scenario "New clone after an abandoned build resets the fixed branch and creates no second one" asserts HTTP 201, one new `open` `builds` row, the clone commit's parent at the current `main` head rather than the abandoned commit, no second `build/sdlc-plan-workshop…` branch, and the prior row still `abandoned`. |
| 3 — epic-boundary traceability | Advisory | BSB-20-PENDING-1 (cross-document `epics.md`, `PRD.md`, ADR SK-001) | No story change is proposed or present. The story already names both name-bearing fields (`SKILL.md` frontmatter `name`, `verify.yaml` top-level `skill`) and the `create`/`clone`/`edit` values. The cross-document wording follow-up remains open below. |

`story-map.json` carries the corresponding PENDING-1 abandoned-reset wording and PENDING-2's
reuse-unchanged contract; both summaries match the current acceptance text, and no `story_key` or
`requirement_ids` entry changed.

### Still open (cross-epic/cross-document follow-ups, not applied in this pass)

1. **Finding 1 — alternative interface (only if the recorded choice is rejected).** BSB-19-PENDING-3
   would need to define the `mode` parameter and name the edit flow and its inverted existence rule,
   and BSB-19-PENDING-1's Notes would need the reciprocal handler-extension sentence.
2. **Finding 2 — branch cleanup ownership.** BSB-36's Functional scope should state what happens to
   the fixed `build/<skill-name>` branch after a build is merged or abandoned, so the cleanup owner
   named by both BSB-20 stories actually owns it.
3. **Finding 3 — epic/PRD/ADR wording.** `PRD.md` FR-013, the BSB-20 description in `epics.md` (and
   the Jira epic description) and ADR SK-001 section 1a should clarify that the clone's name rewrite
   covers both name-bearing fields and use the `create`/`clone`/`edit` mode vocabulary rather than
   "new".
4. **BSB-21 forward note (unchanged).** BSB-21's future save story must assert that a save on an
   edit build commits only to the existing `skills/<skill-name>/` folder (the FR-125 proof already
   handed off in BSB-20-PENDING-2's Notes).

No BSB-20 finding lacks a usable answer; the remaining items are routed to other epics' revision
passes or a human documentation decision and none blocks the stories as written.

### Coverage re-check

Unchanged and complete. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013,
FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to
BSB-20 in `epic-map.json`, with no foreign requirement and no duplicate claim. This pass changed no
story, key, title, statement, acceptance criterion or requirement ID.

### Notes for the next review

- **Only this file changed:** `revisions.md`. `stories.md` and `story-map.json` were re-verified as
  already carrying every applied remedy and were not edited; nothing outside
  `docs/product/epics/BSB-20/_epic/` was touched.
- **The report's BSB-20-side proposed changes are all present**, including the one Blocking
  finding's recommended option and Finding 2's optional clone reset scenario.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set; if it returns
  changes_requested, apply the new report the same way.

## Pass 8 — 2026-11-17 (revise re-run: same report, already applied; no BSB-20 story change)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step (upstream commit `bd92ecb`). This
pass read the report's **Findings**, **Open questions** and **Proposed changes** and checked every
BSB-20-side remedy against the current `stories.md` and `story-map.json`. Every remedy is already
in the text (applied in Pass 6 and re-verified in Pass 7), so no story statement, acceptance
criterion, Out-of-scope entry, Notes entry or `story-map.json` field changed this pass.

### Work item lookup

The Atlassian MCP tools are not exposed in this session (no `mcp__atlassian__*` tool is
available), so the configured site was queried read-only over its REST API (GET only; no Jira
write). `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 with "Issue does not exist or you
do not have permission to see it.", matching `PRD.md` section 8; no issue content is assumed from
that lookup. The run's epic `BSB-20` was read from the same site and returned HTTP 200: summary
"Skill cloning & edit builds", type Epic, status To Do, labels `FA-2`/`MVP`, no sub-tasks, with a
description matching the BSB-20 section of `epics.md`. That epic is the subject of this pass.

### Findings verified

| Finding | Severity | Stories touched | Verification this pass |
|---|---|---|---|
| 1 — cross-epic shared-validator contract | Blocking | BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-3) | The `mode`-parameter sentence is absent. Notes state, as proposed, that the story "reuses BSB-19-PENDING-3's skill-name pattern validator and open-build collision check unchanged; the edit mode's existence rule is inverted, so this story owns the existing-on-main predicate (reject when the name is absent) and does not parameterise BSB-19's validator." PENDING-1 still says it reuses the validator unchanged, which matches its create-equivalent existence rule. No acceptance criterion claims a parameterised BSB-19 validator. |
| 2 — fixed-branch lifecycle | Advisory | BSB-20-PENDING-1 (cross-epic BSB-36) | PENDING-1's Out of scope reads "deleting or finalising `build/<skill-name>` after a build is merged or abandoned (BSB-36) — the reset of that fixed branch when a new build starts is in scope and asserted above". The optional remedy is present: the scenario "New clone after an abandoned build resets the fixed branch and creates no second one" asserts HTTP 201, one new `open` `builds` row, the clone commit's parent at the current `main` head rather than the abandoned commit, no second `build/sdlc-plan-workshop…` branch, and the prior row still `abandoned`. |
| 3 — epic-boundary traceability | Advisory | BSB-20-PENDING-1 (cross-document `epics.md`, `PRD.md`, ADR SK-001) | No story change is proposed or present. The story names both name-bearing fields (`SKILL.md` frontmatter `name`, `verify.yaml` top-level `skill`) and the `create`/`clone`/`edit` values. The cross-document wording follow-up remains open below. |

`story-map.json` already carries the corresponding PENDING-1 abandoned-reset wording and
PENDING-2's reuse-unchanged contract; both summaries match the current acceptance text, and no
`story_key` or `requirement_ids` entry changed.

**Report evidence is stale, not the stories.** The report's line references for Finding 1
(`stories.md:169-177`) and Finding 2 (`stories.md:72-74`, `:104-107`) predate commit `6b66e8b`
(Pass 6), which removed the `mode`-parameter sentence and applied the branch-reset wording. The
proposed text is present; only the quoted old text and line numbers no longer match the file. This
is a note for the next review, not a story defect.

### Still open (cross-epic/cross-document follow-ups, not applied in this pass)

1. **Finding 1 — alternative interface (only if the recorded choice is rejected).** BSB-19-PENDING-3
   would need to define the `mode` parameter and name the edit flow and its inverted existence rule,
   and BSB-19-PENDING-1's Notes would need the reciprocal handler-extension sentence.
2. **Finding 2 — branch cleanup ownership.** BSB-36's Functional scope should state what happens to
   the fixed `build/<skill-name>` branch after a build is merged or abandoned, so the cleanup owner
   named by both BSB-20 stories actually owns it.
3. **Finding 3 — epic/PRD/ADR wording.** `PRD.md` FR-013, the BSB-20 description in `epics.md` (and
   the Jira epic description) and ADR SK-001 section 1a should clarify that the clone's name rewrite
   covers both name-bearing fields and use the `create`/`clone`/`edit` mode vocabulary rather than
   "new".
4. **BSB-21 forward note (unchanged).** BSB-21's future save story must assert that a save on an
   edit build commits only to the existing `skills/<skill-name>/` folder (the FR-125 proof already
   handed off in BSB-20-PENDING-2's Notes).

No BSB-20 finding lacks a usable answer; the remaining items are routed to other epics' revision
passes or a human documentation decision and none blocks the stories as written.

### Coverage re-check

Unchanged and complete. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013,
FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to
BSB-20 in `epic-map.json`, with no foreign requirement and no duplicate claim. This pass changed no
story, key, title, statement, acceptance criterion or requirement ID.

### Notes for the next review

- **Only this file changed:** `revisions.md`. `stories.md` and `story-map.json` were re-verified as
  already carrying every applied remedy and were not edited; nothing outside
  `docs/product/epics/BSB-20/_epic/` was touched.
- **The report's BSB-20-side proposed changes are all present**, including the Blocking finding's
  recommended option and Finding 2's optional clone reset scenario.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set. Because the current report's
  quoted evidence predates Pass 6, the reviewer should judge the current story text; the remaining
  actions are the four cross-epic/cross-document follow-ups above and need no BSB-20 story edit.

## Pass 9 — 2026-11-17 (revise retry: Finding 3 traceability recorded in-story and in the map)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step (upstream commit `bd92ecb`). This
pass re-read the report's **Findings**, **Open questions** and **Proposed changes** against the
current `stories.md` and `story-map.json`. Finding 1's recommended option and Finding 2's remedy
were already present from Pass 6 (re-verified below); the one gap the report names that was still
only in `revisions.md` and not in the artifacts was Finding 3's FR-013 traceability note. This
pass records it on the story side and aligns the `story-map.json` summaries with the story text.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools are not exposed in this
session (no `mcp__atlassian__*` tool is available), so the configured site was queried read-only
over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP
404 "Issue does not exist or you do not have permission to see it."; a JQL text search for the name
returned no issue; the visible projects are BEEM, BSB, EX, GRAP and LNPRTL and none is named
`SkillBuilder`. This matches `PRD.md` section 8 and the report's Context loaded; no issue content
is assumed from the lookup. The run's epic `BSB-20` was read from the same site and returned HTTP
200: summary "Skill cloning & edit builds", type Epic, status To Do, labels `FA-2`/`MVP`, no parent
and no sub-tasks, with a description matching the BSB-20 section of `epics.md` and covering
FR-011, FR-012, FR-013, FR-014, FR-124, FR-125 and FR-126. That epic is the subject of this pass.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| 1 — cross-epic shared-validator contract | Blocking | BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-3) | Re-verified, already applied in Pass 6: PENDING-2's Notes carry no `mode`-parameter sentence and state that the story reuses BSB-19-PENDING-3's skill-name pattern validator and open-build collision check unchanged, owns the inverted existing-on-main predicate and does not parameterise BSB-19's validator. No text changed this pass. |
| 2 — fixed-branch lifecycle | Advisory | BSB-20-PENDING-1 (cross-epic BSB-36) | Re-verified, already applied in Pass 6: PENDING-1's Out of scope uses the "deleting or finalising … the reset … is in scope" wording and the scenario "New clone after an abandoned build resets the fixed branch and creates no second one" is present. No text changed this pass; PENDING-2 needed no change, as the report states. |
| 3 — epic-boundary traceability | Advisory | BSB-20-PENDING-1 (cross-document `epics.md`, `PRD.md`, ADR SK-001) | **Notes:** added a traceability paragraph recording that the clone rewrites both name-bearing fields because `python tools/check.py` (README tier 1) rejects a `verify.yaml` whose top-level `skill` differs from its folder, so FR-013's "frontmatter" wording is read as covering `SKILL.md` `name` and `verify.yaml` `skill` together; the `PRD.md` FR-013, `epics.md` BSB-20 Description/DoD and ADR SK-001 section 1a wording clarification is named as the cross-document follow-up. No acceptance criterion, title, statement or requirement ID changed. |

### `story-map.json` change

`story_key` and `requirement_ids` are untouched; only the two summary strings changed:

- **BSB-20-PENDING-1** — records the Finding 3 rationale: the `verify.yaml` top-level `skill`
  rewrite is required in addition to the `SKILL.md` frontmatter `name` by `python tools/check.py`,
  so FR-013's frontmatter wording is read as covering both name-bearing fields, with the
  PRD/epic/ADR wording clarification as a recorded cross-document follow-up.
- **BSB-20-PENDING-2** — the fixed `build/<skill-name>` branch reset now says it applies when a
  prior build for the same skill was **merged or abandoned**, matching the rule in the story's
  Notes; the merged case is the one asserted by AC 2 and the abandoned case is stated in Notes.

### Still open (cross-epic/cross-document follow-ups, not applied in this pass)

1. **Finding 1 — alternative interface (only if the recorded choice is rejected).** BSB-19-PENDING-3
   would need to define the `mode` parameter and name the edit flow and its inverted existence rule,
   and BSB-19-PENDING-1's Notes would need the reciprocal handler-extension sentence.
2. **Finding 2 — branch cleanup ownership.** BSB-36's Functional scope should state what happens to
   the fixed `build/<skill-name>` branch after a build is merged or abandoned, so the cleanup owner
   named by both BSB-20 stories actually owns it.
3. **Finding 3 — epic/PRD/ADR wording.** `PRD.md` FR-013, the BSB-20 description in `epics.md` (and
   the Jira epic description) and ADR SK-001 section 1a should clarify that the clone's name rewrite
   covers both name-bearing fields and use the `create`/`clone`/`edit` mode vocabulary rather than
   "new". The story-side note added in this pass records the reading; the documents themselves are
   outside this skill's write scope.
4. **BSB-21 forward note (unchanged).** BSB-21's future save story must assert that a save on an
   edit build commits only to the existing `skills/<skill-name>/` folder (the FR-125 proof already
   handed off in BSB-20-PENDING-2's Notes).

No BSB-20 finding lacks a usable answer; the remaining items are routed to other epics' revision
passes or a human documentation decision and none blocks the stories as written.

### Coverage re-check

Complete and unchanged. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013,
FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to
BSB-20 in `epic-map.json`, with no foreign requirement and no duplicate claim. No story key, title,
statement, acceptance criterion or requirement ID changed; only PENDING-1's Notes and the two
`story-map.json` summaries changed.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md` (PENDING-1 Notes traceability paragraph),
  `story-map.json` (both summaries) and this `revisions.md`. Nothing outside
  `docs/product/epics/BSB-20/_epic/` was touched.
- **Finding 1 (Blocking) is closed in the stories** by the recommended option; Finding 2's
  BSB-20-side inconsistency is closed in both stories; Finding 3 now has its story-side traceability
  note, with its cross-document wording follow-up recorded above.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set with the current story text;
  the remaining actions are the four cross-epic/cross-document follow-ups above.
