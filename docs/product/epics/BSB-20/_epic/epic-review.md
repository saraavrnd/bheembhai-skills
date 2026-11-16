# Epic Review — BSB-20: Skill cloning & edit builds

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-20-PENDING-1, BSB-20-PENDING-2

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-20/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** `SkillBuilder-2` has no Jira issue on the configured site. The Atlassian
  MCP tools are not exposed in this session, so the site was queried read-only over its REST API
  (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does
  not exist or you do not have permission to see it"), and the visible projects are BEEM, BSB, EX,
  GRAP and LNPRTL — no `SkillBuilder` project. This matches `PRD.md` §8 and `epics.md`'s source
  note; no issue content is assumed from the lookup.
- **The epic in this run is BSB-20.** The run context's work item is `SkillBuilder-2` (the PRD's
  parent), and its `ITEM` is BSB-20; the immediately preceding step wrote BSB-20's stories
  (`sdlc-plan-stories-write`, commit `9b8e989`). Read-only `GET /rest/api/3/issue/BSB-20` returned
  HTTP 200: Epic "Skill cloning & edit builds", status To Do, labels `FA-2`/`MVP`, no parent and no
  sub-tasks, with a description matching `epics.md`'s BSB-20 section.
- **All 2 stories in BSB-20**, from `stories.md` and `story-map.json` in one read each —
  BSB-20-PENDING-1 (FR-011, FR-012, FR-013, FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126).
  `story-map.json` maps exactly these two keys with the same requirement IDs.
- **`epic-map.json`** — BSB-20 maps FR-011, FR-012, FR-013, FR-014, FR-124, FR-125 and FR-126; no
  NFR is mapped to this epic (NFR-012 belongs to BSB-38).
- **`PRD.md`** — §5 FA-2, the §6 rows for the seven mapped FRs, §7's NFR table (to confirm no
  BSB-20 NFR), and §8's source note, external prerequisites and no-platform-writes constraint.
- **`epics.md`** — BSB-20's Description, Functional scope, Implementation guidance, Definition of
  Done, Covered requirements and Notes (lines 268–325); BSB-19's section and Notes (shared build
  record, name validator); BSB-18's Notes (signed-in author, local `users` row and the per-request
  gate); BSB-21's section and Notes (save-to-commit, build head and readiness); and BSB-36's
  Description/Functional scope (lines 1270–1296), to test the branch-lifecycle assignment.
- **BSB-19's 3 stories and `story-map.json`**, because both BSB-20 stories depend on
  BSB-19-PENDING-1 for the shared `GET /builds/new` + `POST /builds` handler and on
  BSB-19-PENDING-3 for the shared name validator and open-build collision check.
- **`docs/adr/SK-001-skill-builder.md`** — §1a (build and fixed `build/<skill-name>` branch,
  whole-folder clone, frontmatter rewrite, create scaffold), §1b (Ready "Manifest valid" check),
  §8 (edit branch and submission) and §9 (`builds` columns: `kind`, `cloned_from`, `branch`,
  `head_sha`, `ready_sha`, `state`). `tools/check.py:86` and `:105-106` enforce the two
  name-bearing fields; `README.md:38-39` labels `python tools/check.py` tier 1 and
  `bheembhai-verify lint` tier 2.
- **`_epic/epic-sequence.md` / `.json`** — exists for BSB-20 (AWAITING APPROVAL): both stories are
  Wave 1 with no intra-epic edge, and cross-epic prerequisites BSB-18, BSB-19-PENDING-1 and
  BSB-19-PENDING-3 are recorded. Checked only for dependency consistency; the order was not
  recomputed here.
- **Prior review state — verified applied, not assumed.** The previous `epic-review.md` (CHANGES
  REQUESTED, one Blocking finding) was re-checked line by line against the current text. Its
  BSB-20-side remedies are present: both Out-of-scope entries now say BSB-19-PENDING-1 owns the base
  create route and create mode of the single handler and that each story adds only its own mode to
  that same handler (Finding 1 of that pass); PENDING-1 asserts both static manifest checks
  (Finding 4); PENDING-2 has the resolved-existing-folder AC and the reset-after-merge AC
  (Findings 2 and 5). The residual cross-story/cross-epic gaps that survive are Findings 1–3 below.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md` are
  not committed; the PDLC design stage runs after planning, so ADR SK-001 is the design authority
  this pass can use.

## Findings

### Finding 1 — Cross-epic shared-validator contract: PENDING-2 requires a `mode` parameter that BSB-19-PENDING-3 says does not exist

- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-2 (cross-epic: BSB-19-PENDING-3 and BSB-19-PENDING-1);
  BSB-20-PENDING-1 is a consistent user of the same validator and needs no change.
- **Evidence:**
  - BSB-20-PENDING-2 Notes (`stories.md:169-177`): "BSB-19-PENDING-3 owns the skill-name pattern
    validator and open-build collision check for both the clone flow and this edit flow; this story
    owns the `edit`-mode dispatch on the same handler and the inverted existence rule. … Because of
    that inversion, the shared validator takes a `mode` parameter (`create`/`clone` versus `edit`)
    that selects the existence rule, while the pattern and open-build collision parts are reused
    unchanged."
  - BSB-19-PENDING-3 Notes (`BSB-19/_epic/stories.md:197-199`): "The validator and collision check
    are reused unchanged by the clone flow in BSB-20 (FR-015 covers create or clone)." Its Out of
    scope (`:184-188`) names only "clone-build creation (BSB-20)", not edit-build creation, and
    defines no `mode` parameter.
  - BSB-19-PENDING-1 Notes (`BSB-19/_epic/stories.md:59-63`): "The create form is served at GET
    `/builds/new` and POST `/builds` returns the confirmation body; these routes are owned by this
    epic". It defines no `mode` parameter and no edit mode; its Out of scope (`:45-49`) names
    "cloning (BSB-20)" but not BSB-20's edit mode.
  - BSB-20-PENDING-1 Notes (`stories.md:78-81`) says it reuses the same validator "unchanged",
    which agrees with BSB-19-PENDING-3 for the clone flow — the contradiction is specific to the
    edit flow.
- **What is missing/ambiguous/contradictory:** The two epics describe the same shared component
  with opposite interfaces. BSB-19 is sequenced first and its story promises the validator and
  collision check are "reused unchanged" for clone only; BSB-20-PENDING-2 expects that validator to
  accept a `mode` parameter and to serve the edit flow, whose existence rule is the inverse. If
  BSB-19-PENDING-3 is built as written, BSB-20-PENDING-2 cannot reuse it unchanged — it must modify
  a component the earlier epic declared frozen — and the edit flow's inverted existence rule has no
  agreed home. Two implementers can therefore build two different validators, or one can build the
  wrong one. The BSB-20-side Out-of-scope/handler ownership is now correct; the remaining defect is
  the validator's cross-epic contract.
- **Question (if a person must decide):** Should the shared validator take a `mode` parameter
  (which requires revising BSB-19-PENDING-3 to define it and name the edit flow), or should
  BSB-20-PENDING-2 own the inverted existing-on-main predicate and reuse BSB-19-PENDING-3's
  pattern and open-build collision checks unchanged? The report recommends the second option
  because BSB-19 is built first and its Notes already promise "reused unchanged"; that option is
  applyable inside BSB-20 without a BSB-19 revision. (Also listed under Open questions.)
- **Proposed change:**
  - **BSB-20-PENDING-2:** Replace the `mode`-parameter sentence in Notes with: "This story reuses
    BSB-19-PENDING-3's skill-name pattern validator and open-build collision check unchanged; the
    edit mode's existence rule is inverted, so this story owns the existing-on-main predicate
    (reject when the name is absent) and does not parameterise BSB-19's validator." Keep the rest
    of the Notes and every acceptance criterion unchanged.
  - **BSB-20-PENDING-1:** No change. Its clone mode needs no `mode` parameter because its
    existence rule matches create's (reject a name already on `main`), so it can call
    BSB-19-PENDING-3's validator unchanged; only PENDING-2 needs the inversion. Its "reused
    unchanged" statement therefore already matches BSB-19-PENDING-3.
  - **Cross-epic follow-up (not applied here), only if the second option is rejected:** revise
    BSB-19-PENDING-3 to define the `mode` parameter and name the edit flow and its inverted
    existence rule, and add to BSB-19-PENDING-1's Notes that its handler is extended by BSB-20's
    clone/edit modes. That is a BSB-19 revision, outside this epic's story pass.

### Finding 2 — Fixed-branch lifecycle: PENDING-1 hands "reusing" to BSB-36 while PENDING-2 puts the reset in scope and asserts it

- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic: BSB-36)
- **Evidence:**
  - BSB-20-PENDING-1 Out of scope (`stories.md:72-74`): "deleting or reusing `build/<skill-name>`
    after a build is merged or abandoned (BSB-36)".
  - BSB-20-PENDING-1 Notes (`stories.md:104-107`): "When a prior build for the same skill was
    merged or abandoned, a new build resets that branch to the new `base_sha` and creates no second
    branch; deleting or finalising the branch on merge or abandonment belongs to BSB-36".
  - BSB-20-PENDING-2 Out of scope (`stories.md:160-162`): "deleting or finalising
    `build/<skill-name>` after a build is merged or abandoned (BSB-36) — the reset of that fixed
    branch when a new build starts is in scope and asserted above"; and its AC 2
    (`stories.md:126-129`) asserts the reset after a merged build.
  - BSB-36 Functional scope (`epics.md:1284-1295`) covers readiness gating, opening the pull
    request, recording its URL/state, the open/submitted/merged/abandoned transitions, clearing
    readiness on save and the no-direct-write rule; it never mentions deleting, finalising or
    reusing the fixed build branch.
- **What is missing/ambiguous/contradictory:** The two sibling stories now describe the same fixed
  branch rule differently. PENDING-2 says the reset is in scope and proves it with an AC;
  PENDING-1's Out of scope still says "reusing" belongs to BSB-36, which contradicts PENDING-1's
  own Notes (which state the reset) and PENDING-2's wording. PENDING-1 also has no acceptance
  criterion for the clone flow's equivalent case — a prior *abandoned* build for the same new name.
  (The *merged* case cannot reach clone: the merged name is then on `main`, so the clone's
  "already exists on main" rule rejects it; the abandoned case can reach it.) Meanwhile the
  cleanup owner named by both stories, BSB-36, does not claim the post-merge/post-abandonment
  branch lifecycle at all. The intended rule is clear from the Notes, so the stories are safe to
  build as written, but the scope wording and the proof are inconsistent across the siblings.
- **Question (if a person must decide):** None for BSB-20 — the reset rule is already stated in
  both Notes. The ownership question is BSB-36's: does BSB-36 delete or finalise the fixed branch
  after a merge/abandonment, or leave it for the next build's reset? That is a cross-epic follow-up,
  not a BSB-20 product decision.
- **Proposed change:**
  - **BSB-20-PENDING-1:** Replace the Out-of-scope entry "deleting or reusing
    `build/<skill-name>` after a build is merged or abandoned (BSB-36)" with PENDING-2's wording:
    "deleting or finalising `build/<skill-name>` after a build is merged or abandoned (BSB-36) — the
    reset of that fixed branch when a new build starts is in scope." Optionally add one acceptance
    criterion for a prior abandoned build for the same new name, asserting the branch resets to the
    new `base_sha`, the clone commit's parent is that `base_sha`, and no second branch is created
    (the clone analogue of PENDING-2's AC 2).
  - **BSB-20-PENDING-2:** No change; its Out of scope and AC 2 already state the intended rule.
  - **Cross-epic follow-up (not applied here):** BSB-36's Functional scope or Notes should state
    what happens to the fixed `build/<skill-name>` branch after a merge or abandonment, so the
    owner both BSB-20 stories name actually owns it. No BSB-20 story key, requirement or AC needs
    to change for that.

### Finding 3 — Epic-boundary traceability: the epic Description/DoD, FR-013 and ADR §1a still describe a narrower frontmatter-only rewrite and the "new" mode vocabulary

- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1 (epic boundary; cross-document: `epics.md` BSB-20,
  `PRD.md` FR-013, ADR SK-001 §1a; the Jira epic description carries the same stale sentence)
- **Evidence:**
  - BSB-20-PENDING-1 AC 2 and AC 3 (`stories.md:26-34`) and Notes (`:85-92`) require both
    name-bearing fields to be rewritten: `SKILL.md` frontmatter `name` and `verify.yaml` top-level
    `skill`, with every other byte identical.
  - `epics.md:274-276` (BSB-20 Description): "Cloning copies the whole skill folder, rewrites
    **only the skill name in the copied frontmatter**, and leaves the source skill untouched."
    `epics.md:305-310` (Definition of Done): "whose frontmatter name matches the new skill".
    `PRD.md:87` FR-013: "Cloning rewrites the skill name in the copied frontmatter." ADR SK-001
    §1a: the clone "rewrites `name:` in the frontmatter."
  - `tools/check.py:86` rejects a `SKILL.md` frontmatter `name` that differs from the folder, and
    `:105-106` rejects a `verify.yaml` whose `skill` value differs from the folder; `README.md:38`
    records `python tools/check.py` as a CI check. The `verify.yaml` rewrite is therefore required
    for a catalog-valid clone, not optional.
  - `epics.md:294-295` (Implementation guidance): "add a build mode that distinguishes clone, edit
    and **new** builds", while the stories, ADR SK-001 §9 and BSB-19-PENDING-1 all use the
    `builds.kind` value `create` (the default `mode` value in BSB-20).
- **What is missing/ambiguous/contradictory:** The story is correct against the catalog check, but
  the epic's own Description, DoD and traceability text (and the FR/ADR prose) under-describe it: a
  reader comparing the story to FR-013 sees a scope expansion ("frontmatter only") that the story
  deliberately exceeds to keep the clone catalog-valid. Separately, the epic guidance's "new"
  vocabulary differs from the stories' `create` value. Neither is a build ambiguity — the story
  names the exact fields and values — but the epic boundary and its traceability text are stale
  relative to the stories revised to satisfy `tools/check.py`.
- **Question (if a person must decide):** None required before code — the catalog check fixes the
  behaviour. If the team wants FR-013's "frontmatter" to remain literally limited to `SKILL.md`,
  the `verify.yaml` rewrite needs a separate requirement or an explicit note in the epic; otherwise
  the epic/PRD/ADR wording should be clarified to cover both name-bearing fields.
- **Proposed change:**
  - **BSB-20-PENDING-1:** No statement or acceptance-criterion change. The story already names the
    two rewritten fields and the `create`/`clone`/`edit` values.
  - **Cross-document follow-up (not applied here):** On the next `epics.md`/PRD revision, clarify
    BSB-20's Description and Definition of Done and FR-013 so "the skill name in the copied
    frontmatter" also covers the `verify.yaml` top-level `skill` value required by
    `tools/check.py`, and use the ADR's `create`/`clone`/`edit` vocabulary rather than "new".
    Clarify ADR SK-001 §1a's clone sentence the same way. No change to `epic-map.json` or the
    requirement IDs.

## Open questions

1. **Shared-validator interface (Finding 1).** Does BSB-19-PENDING-3's validator take a `mode`
   parameter (requiring a BSB-19 revision), or does BSB-20-PENDING-2 own the inverted
   existing-on-main predicate and reuse BSB-19's pattern and open-collision checks unchanged?
   Recommended default: the second option, which is applyable inside BSB-20 and keeps
   BSB-19-PENDING-3's "reused unchanged" true. The first option is a cross-epic revision recorded
   as a follow-up in Finding 1.

No other product question is open. Finding 2's BSB-36 ownership question is cross-epic, and
Finding 3's documentation clarification needs no gate answer before code.

## Proposed changes

`docs/product/epics/BSB-20/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-20-PENDING-1** — Out of scope: replace "deleting or reusing `build/<skill-name>` after a
  build is merged or abandoned (BSB-36)" with PENDING-2's "deleting or finalising … — the reset of
  that fixed branch when a new build starts is in scope" wording (Finding 2). Optional, advisory:
  add the clone reset-after-abandoned-build acceptance criterion described in Finding 2. No change
  for Finding 1 (its "reused unchanged" statement is already correct) or Finding 3.
- **BSB-20-PENDING-2** — Notes: replace the sentence that says the shared validator takes a `mode`
  parameter with a statement that this story reuses BSB-19-PENDING-3's pattern validator and
  open-build collision check unchanged and owns the inverted existing-on-main predicate for the
  edit mode (Finding 1, recommended option). No other statement, acceptance criterion or
  requirement ID changes; the resolved-existing-folder AC and the reset-after-merge AC stay as
  written. If the first option is chosen instead, leave PENDING-2 as written and revise
  BSB-19-PENDING-3.
- **`story-map.json`** — No change. The two summaries, keys and requirement IDs already match the
  current stories; neither summary mentions the validator's `mode` parameter, so the Finding 1
  rewording does not alter them.
- **Cross-epic / cross-document follow-ups (not applied in this pass):**
  - **BSB-19-PENDING-3** — define the `mode` parameter and name the edit flow and its inverted
    existence rule, if the team rejects the recommended in-epic option (Finding 1).
  - **BSB-19-PENDING-1** — add the reciprocal sentence that its handler is extended by BSB-20's
    clone/edit modes through the `mode` parameter (Finding 1).
  - **BSB-36** — state what happens to the fixed `build/<skill-name>` branch after a build is
    merged or abandoned, since both BSB-20 stories assign that cleanup there (Finding 2).
  - **`PRD.md` FR-013, `epics.md` BSB-20 Description/DoD, ADR SK-001 §1a** — clarify the clone's
    `verify.yaml` `skill` rewrite and the `create`/`clone`/`edit` mode vocabulary (Finding 3).
  - **BSB-21** — its future save story must assert that a save on an edit build commits only to
    the existing `skills/<skill-name>/` folder (the FR-125 no-second-folder proof already handed
    off in BSB-20-PENDING-2's Notes). BSB-21 has no decomposed stories yet; this is a forward note.

No change is proposed to `epic-map.json`, the requirement IDs, the story set, the PRD's FR/NFR
identifiers, or Jira. No Jira write was made; publication remains `sdlc-tracker-sync`'s job.

## Architecture impact

None. The visible risks are story wording and cross-epic ownership, not missing design. The
cumulative epic needs no entity, field, endpoint or integration that ADR SK-001 does not provide:
`builds` with `kind`, `cloned_from`, `branch`, `head_sha`, `ready_sha` and `state` is §9; the fixed
`build/<skill-name>` branch, the whole-folder clone and the create scaffold are §1a; the Ready
manifest check is §1b; and the external catalog repository is §8. `base_sha` is the column
BSB-19-PENDING-1 (an earlier epic, sequenced before BSB-20) adds to the same record, and both
BSB-20 stories' Notes name it, so it is a planned in-epic addition, not a missing design element.
No design-stage pass is needed before sequencing.

## Requirement coverage check

Complete for BSB-20's seven mapped requirements, with no contradicting duplicate claim:

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-011 | BSB-20-PENDING-1 | "Clone creates a build and copies the whole skill folder" (HTTP 201, exactly one `kind "clone"` row with `cloned_from`, branch, `base_sha`, `head_sha`, `state "open"`, `ready_sha NULL`) |
| FR-012 | BSB-20-PENDING-1 | The clone branch's `skills/sdlc-plan-workshop/` tree holds exactly the source folder's five files at the same relative paths and no other file |
| FR-013 | BSB-20-PENDING-1 | "Copied SKILL.md frontmatter carries the new skill name and nothing else changes" (name `sdlc-plan-workshop`; description, role, model and body unchanged); the `verify.yaml` `skill` rewrite is the catalog-validity addition noted in Finding 3 |
| FR-014 | BSB-20-PENDING-1 | "Cloning leaves the source skill and main unchanged" (`main` still at `4f1c…`, source files byte-identical) |
| FR-124 | BSB-20-PENDING-2 | "Edit build is opened on a branch cut from the head of main" (HTTP 201, exactly one `kind "edit"` row, branch pointing at the base commit, `head_sha` = `base_sha`) |
| FR-125 | BSB-20-PENDING-2 | "Edit build resolves to the existing skill folder and creates no second one" (resolved target `skills/sdlc-plan-training/`, `git ls-tree -d --name-only skills/` exact, no copy path). The "changes the folder" half is the BSB-21 save commit, deliberately recorded in PENDING-2's Notes; no BSB-21 stories exist yet |
| FR-126 | BSB-20-PENDING-2 | "Edit build rejects a skill name that does not exist on main" (HTTP 422, no `builds` row, no branch) |

BSB-20-PENDING-1 also exercises the clone half of FR-015 (name already on `main`) and FR-016 (name
used by an open build) in its duplicate-name and open-build scenarios, but correctly does not claim
those IDs: `epic-map.json` assigns them to BSB-19, whose PENDING-3 exercises the create half and
whose Out of scope and Notes hand the clone reuse to BSB-20. This is a deliberate,
non-contradicting split, not a duplicate claim. No foreign requirement is claimed by either BSB-20
story. No FR/NFR wording drift was found in the ID mapping itself; the remaining wording issue is
the epic/PRD description of the clone rewrite in Finding 3, not a requirement-ID change. BSB-20
maps no NFR, and NFR-012 (accessibility) is assigned to BSB-38, so no epic-wide silent NFR is left
unowned here.

## Dependency-note sanity check

Mostly consistent; the two cross-epic mismatches are Findings 1 and 2.

- **Real keys only.** Every referenced key exists: BSB-19-PENDING-1 and BSB-19-PENDING-3 are in
  BSB-19's `story-map.json`; BSB-18, BSB-21 and BSB-36 exist as epics; there is no dangling draft
  key.
- **Reciprocated.** BSB-20-PENDING-1/-2 depend on BSB-18 for the signed-in author and the local
  `users` row, and BSB-18's Notes say every other epic depends on that record and the per-request
  gate. Both stories depend on the external catalog repository `bheembhai-skills`, which `PRD.md`
  §8 and ADR SK-001 §1a name as an external prerequisite. The two BSB-20 stories name each other in
  Out of scope (PENDING-1: "opening an edit build (BSB-20-PENDING-2)"; PENDING-2: "creating a fresh
  or cloned build (BSB-19 and BSB-20-PENDING-1)"). For the clone flow, BSB-19-PENDING-1's Out of
  scope names "cloning (BSB-20)" and BSB-19-PENDING-3's Notes say the clone flow reuses the
  validator and collision check.
- **One-sided — Finding 1.** BSB-20-PENDING-2 says BSB-19-PENDING-3's validator serves the edit
  flow and takes a `mode` parameter, while BSB-19-PENDING-3 says it is reused unchanged and names
  only the clone flow; BSB-19-PENDING-1 also does not say its handler is extended by BSB-20's edit
  mode. The BSB-20 side is written; the earlier-built BSB-19 side is not.
- **One-sided — Finding 2.** Both BSB-20 stories assign post-merge/post-abandonment branch cleanup
  to BSB-36, whose Functional scope does not mention deleting, finalising or reusing the
  `build/<skill-name>` branch.
- **Forward hand-off, not a gap.** BSB-20-PENDING-2's Notes require BSB-21's save story to assert
  the FR-125 no-second-folder rule. BSB-21 has no decomposed stories yet, which is normal
  cross-epic sequencing; the dependency is written on the BSB-20 side. `epic-sequence.md` records
  the same forward hand-off and no cycle.
- **Epic-level wording (informational).** BSB-19's epic Notes say "the name validator and scaffold
  writer [are] reused by the cloning and edit-build epic." BSB-20 uses the name validator but not
  the scaffold writer: the clone copies the source folder and the edit build reuses the existing
  folder. Correct the BSB-19 epic note on a later BSB-19 revision; no BSB-20 story change.
- **Ordering not computed.** `epic-sequence.md`/`.json` already exists for BSB-20 and is consistent
  with the stories (both Wave 1, no intra-epic edge, cross-epic prerequisites BSB-18/BSB-19). This
  pass only records the dependency gaps above; build order remains `sdlc-plan-epic-sequence`'s job.
