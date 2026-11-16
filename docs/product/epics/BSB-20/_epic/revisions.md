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
