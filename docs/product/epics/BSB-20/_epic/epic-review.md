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
  not exist or you do not have permission to see it"), matching `PRD.md` §8 and the earlier
  BSB-20 report. No issue content is assumed from the lookup.
- **The epic in this run is BSB-20.** The immediately preceding steps of run
  `92173662-ad00-4424-9af4-41e038113d7e` wrote and revised BSB-20's stories, and
  `_epic/revisions.md` records that this review is the next step. `GET /rest/api/3/issue/BSB-20`
  returned HTTP 200: Epic "Skill cloning & edit builds", status To Do, labels `FA-2`/`MVP`, no
  sub-tasks, and a description matching `epics.md`'s BSB-20 section (including "rewrites only the
  skill name in the copied frontmatter" and "add a build mode that distinguishes clone, edit and
  new builds").
- **All 2 stories in BSB-20**, from `stories.md` and `story-map.json` in one read each —
  BSB-20-PENDING-1 and BSB-20-PENDING-2 (the full set, not a sample). `story-map.json` maps
  exactly these two keys with the same requirement IDs.
- **`epic-map.json`** — BSB-20 maps FR-011, FR-012, FR-013, FR-014, FR-124, FR-125 and FR-126;
  no NFR is mapped to this epic (NFR-012 belongs to BSB-38).
- **`PRD.md`** — §5 FA-2, the §6 rows for the seven mapped FRs, §7's NFR table (to confirm no
  BSB-20 NFR), and §8's source note, external catalog prerequisite and edit-build vocabulary.
- **`epics.md`** — BSB-20's description, functional scope, implementation guidance and Definition
  of Done (lines 268–310); BSB-19's section and Notes (shared build record, name validator);
  BSB-18's Notes (signed-in author and local `users` row); BSB-21's section (save-to-commit and
  build head); and BSB-36's description and functional scope (lines 1270–1296), to test the
  branch-lifecycle assignment.
- **BSB-19's 3 stories and `story-map.json`**, because both BSB-20 stories depend on
  BSB-19-PENDING-1 for the shared `GET /builds/new` + `POST /builds` handler and on
  BSB-19-PENDING-3 for the shared name validator and open-build collision check.
- **`docs/adr/SK-001-skill-builder.md`** — §1a (build and fixed `build/<skill-name>` branch,
  whole-folder clone, "rewrites `name:` in the frontmatter", create scaffold), §1b (the four Ready
  checks, including "Manifest valid: Tier 1: `bheembhai-verify` on the skill's `verify.yaml`, and
  `tools/check.py`"), §8 (edit branch and submission) and §9 (`builds` columns: `kind`,
  `cloned_from`, `branch`, `head_sha`, `ready_sha`, `state`).
- **The catalog's static checks** — `README.md` lines 20–39 ("Changing a skill"; `python
  tools/check.py` is tier 1, `bheembhai-verify lint` is tier 2) and `tools/check.py` lines 85–86
  (`SKILL.md` frontmatter `name` must equal the folder) and 105–106 (`verify.yaml` `skill` must
  equal the folder). The live skill folders under `skills/` confirm both name-bearing fields exist.
- **Prior review state — verified applied, not assumed.** The previous `epic-review.md`
  (CHANGES REQUESTED, six findings) was re-checked line by line against the current text:

  | Prior finding | Severity | State in the current stories |
  |---|---|---|
  | 1 — catalog-manifest consistency | Blocking | Applied on the BSB-20 side: PENDING-1 AC 2 rewrites both name-bearing fields, AC 4 runs `tools/check.py`, Notes and the `story-map.json` summary match. Residual epic/PRD/ADR wording under Finding 3; residual verifier proof under Finding 4. |
  | 2 — shared endpoint and mode | Blocking | Partly applied: both stories now name the `mode` carrier, values `create`/`clone`/`edit` and the request fields. The ownership split between BSB-19's handler and BSB-20's modes is still contradictory — Finding 1. |
  | 3 — build-record contract | Blocking | Applied: PENDING-1 AC 1 sets `head_sha` to the clone commit (parent `base_sha`, source read at `base_sha`); PENDING-2 AC 1 sets `head_sha` = `base_sha`; both Notes state the rule. |
  | 4 — branch lifecycle | Blocking | Applied in this epic: both Notes reset the fixed `build/<skill-name>` branch to the new `base_sha`, create no second branch, and assign cleanup to BSB-36. BSB-36 does not yet claim that scope — Finding 2. |
  | 5 — FR-125 proof location | Advisory | Applied as proposed: PENDING-2 AC 2 asserts the resolved existing folder, the exact `git ls-tree` result and no copy path; Notes hand the save-time proof to BSB-21. |
  | 6 — reciprocal BSB-19 notes | Advisory | Partly applied: PENDING-2 Notes name BSB-19-PENDING-1/-3 as owners for both flows and record the validator `mode` parameter. The BSB-19 stories still name only clone — Finding 1. |

- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md` are
  not committed; the PDLC design stage runs after planning, so ADR SK-001 is the design authority
  this pass can use. No `epic-sequence.md`/`.json` exists for BSB-20; ordering is not computed here.

## Findings

### Finding 1 — Shared handler and mode ownership: the clone/edit ACs exercise `POST /builds` while both stories put the shared handler out of scope
- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic: BSB-19-PENDING-1,
  BSB-19-PENDING-3)
- **Evidence:**
  - BSB-20-PENDING-1 Out of scope (`stories.md:67-73`): "the shared create form and `POST
    /builds` handler (BSB-19-PENDING-1)".
  - BSB-20-PENDING-1 Notes (`stories.md:91-95`): "The clone form extends BSB-19-PENDING-1's single
    `GET /builds/new` + `POST /builds` handler and adds no second handler at that route. The build
    mode is carried as the `mode` query parameter ... allowed values are `create` (the default
    when the parameter is absent), `clone` and `edit` ... In `clone` mode the request fields are
    the source skill name and the new skill name." Its clone ACs submit at
    `/builds/new?mode=clone`.
  - BSB-20-PENDING-2 Out of scope (`stories.md:146-151`): the same "shared create form and `POST
    /builds` handler (BSB-19-PENDING-1)" entry. Its Notes (`stories.md:153-165`) say "BSB-19-PENDING-1
    and BSB-19-PENDING-3 own those shared pieces for both the clone flow and this edit flow; this
    story adds only the edit mode" and that the shared validator takes a `mode` parameter. Its
    edit ACs submit at `/builds/new?mode=edit`.
  - BSB-19-PENDING-1 Notes (`BSB-19/_epic/stories.md:59-63`): "The create form is served at GET
    `/builds/new` and POST `/builds` returns the confirmation body; these routes are owned by this
    epic". The story defines no `mode` parameter and no clone/edit mode; its ACs submit at
    `/builds/new` with a skill name and description only.
  - BSB-19-PENDING-3 Notes (`BSB-19/_epic/stories.md:198-199`): "The validator and collision check
    are reused unchanged by the clone flow in BSB-20"; its Out of scope names clone-build creation
    only, not edit-build creation or a `mode` parameter.
  - `epics.md:294-295` implementation guidance: "add a build mode that distinguishes clone, edit
    and new builds"; ADR SK-001 §9 defines `builds.kind` as `(create, clone, edit)`.
- **What is missing/ambiguous/contradictory:** Each BSB-20 AC requires the shared `POST /builds`
  route to dispatch to clone or edit mode, but the same story's Out-of-scope section says that
  handler belongs to BSB-19-PENDING-1. BSB-19-PENDING-1's story owns the route but defines no
  mode, and BSB-19-PENDING-3's validator is "reused unchanged" for clone only. No story says who
  adds the `mode` parameter and the edit-mode existence inversion: if BSB-20 does not touch the
  handler (as its Out of scope says), the mode is never built; if BSB-20 does extend it (as its
  Notes say), it is modifying a route it just declared out of scope. Two implementers can build a
  second handler at the same route or a create-only handler, and one of the two stories' own
  statements is then false. This is the same shared-endpoint gap the previous pass flagged; the
  mode values and request fields are now specified, but the single owner is not.
- **Question (if a person must decide):** None assuming the split already stated in
  BSB-20-PENDING-2's Notes is confirmed: BSB-19-PENDING-1 owns the base create route and
  BSB-19-PENDING-3 owns the pattern/collision validator, while BSB-20 adds the clone and edit modes
  to that same handler and passes the validator a `mode` value. The finding is the Out-of-scope
  wording that denies that split, not an unresolved product choice. (If the team instead wants
  BSB-19 to own the mode parameter too, that is a cross-epic revision; the proposed change below
  assumes the Notes' split.)
- **Proposed change:**
  - **BSB-20-PENDING-1:** Replace the Out-of-scope entry "the shared create form and `POST
    /builds` handler (BSB-19-PENDING-1)" with "the base create route and create mode of the shared
    `GET /builds/new` + `POST /builds` handler (BSB-19-PENDING-1); this story adds the clone mode
    to that same handler, not a second handler". Keep the Notes' mode carrier, values, default and
    clone request fields unchanged.
  - **BSB-20-PENDING-2:** Make the same Out-of-scope rewording for the edit mode: "the base create
    route and create mode of the shared handler (BSB-19-PENDING-1); this story adds the edit mode
    to that same handler". Keep the Notes' statement that BSB-19-PENDING-1/-3 own the shared pieces
    and that the validator takes a `mode` parameter.
  - **Same change for both stories:** one owner per layer — BSB-19 owns the base handler and the
    pattern/collision validator; BSB-20 owns the clone/edit mode dispatch and the inverted edit
    existence rule. Neither story creates a second handler at `/builds`.
  - **Cross-epic follow-up (not applied here):** BSB-19-PENDING-1's Notes should add that the
    handler is extended by BSB-20's clone/edit modes through the `mode` parameter, and
    BSB-19-PENDING-3 should name the edit flow and its inverted existence rule alongside the clone
    flow. These belong to BSB-19's next revision, not this story pass.

### Finding 2 — Epic-wide scope boundary: branch cleanup is assigned to BSB-36, whose scope does not include it
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic: BSB-36)
- **Evidence:**
  - Both stories' Out of scope (`stories.md:71-72` and `:149-151`): "deleting or reusing
    `build/<skill-name>` after a build is merged or abandoned (BSB-36)".
  - Both stories' Notes (`stories.md:99-102` and `:181-183`): "When a prior build for the same
    skill was merged or abandoned, a new build resets that branch to the new `base_sha` and
    creates no second branch; deleting or finalising the branch on merge or abandonment belongs to
    BSB-36 (submission and build lifecycle), not this epic."
  - `epics.md:1284-1296` (BSB-36 functional scope) lists readiness gating, opening the pull
    request, the description, recording the pull-request URL/state, moving the build through
    open/submitted/merged/abandoned, clearing readiness on a save and the no-direct-write rule. It
    does not mention deleting, reusing or finalising the `build/<skill-name>` branch.
  - ADR SK-001 §1a says an enhancement is a new build (a clone or an edit branch) on the same
    fixed `build/<skill-name>` branch, which is why the reset rule matters.
- **What is missing/ambiguous/contradictory:** The in-epic behaviour is defined and consistent:
  BSB-20 resets the fixed branch to the new `base_sha` and creates no second branch, so a second
  build of the same skill is buildable. But the stories hand the post-merge/post-abandonment
  cleanup to an epic whose own functional scope does not admit it. A BSB-36 implementer reading
  only BSB-36 will not build branch cleanup; the capability is then unowned even though BSB-20's
  Out of scope says it is owned. No BSB-20 acceptance criterion exercises the reset-after-merge
  case either, so the rule lives only in Notes.
- **Question (if a person must decide):** None is needed to build BSB-20 as written — the reset
  rule is explicit. The decision belongs to BSB-36's epic revision: does BSB-36 delete or finalise
  the branch on merge/abandonment, or is the branch left in place for the next build's reset?
- **Proposed change:**
  - **BSB-20-PENDING-1** and **BSB-20-PENDING-2:** No change required to the stories' statements or
    acceptance criteria; the Notes already state the reset rule and the Out of scope already names
    BSB-36. Optional only: add one acceptance criterion for a prior merged/abandoned build if the
    team wants the reset rule proven in this epic rather than in BSB-36.
  - **Cross-epic follow-up (not applied here):** BSB-36's functional scope or Notes should state
    what happens to the fixed `build/<skill-name>` branch after a merge or abandonment, so the
    owner BSB-20 names actually owns it. No BSB-20 story key, requirement or acceptance criterion
    needs to change for this.

### Finding 3 — Epic-boundary traceability: the BSB-20 description and guidance still describe a narrower manifest rewrite and a different mode vocabulary than the stories
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1 (epic boundary; cross-document: `epics.md`, `PRD.md`,
  ADR SK-001 §1a)
- **Evidence:**
  - BSB-20-PENDING-1 AC 2 (`stories.md:26-29`): `verify.yaml` "has skill `sdlc-plan-workshop` and
    every other byte identical to its source", and "`SKILL.md` and `verify.yaml` are the only
    copied files whose bytes differ". Its Notes (`stories.md:85-89`) say `SKILL.md`'s frontmatter
    `name` and `verify.yaml`'s top-level `skill` both become the new name.
  - `epics.md:274-276` description: "Cloning copies the whole skill folder, rewrites **only the
    skill name in the copied frontmatter**, and leaves the source skill untouched." The Jira
    BSB-20 description contains the same sentence. `PRD.md:87` FR-013 says "Cloning rewrites the
    skill name in the copied frontmatter." ADR SK-001 §1a line 84 says the clone "rewrites
    `name:` in the frontmatter."
  - `tools/check.py:105-106` rejects a `verify.yaml` whose `skill` value does not equal its folder
    name, and `tools/check.py:85-86` does the same for `SKILL.md`'s frontmatter `name`; `README.md`
    says CI runs `python tools/check.py`. The story's extra rewrite is therefore required for
    catalog validity, not optional.
  - `epics.md:294-295` implementation guidance says "add a build mode that distinguishes clone,
    edit and **new** builds", while the stories, ADR SK-001 §9 and BSB-19-PENDING-1 all use the
    `builds.kind` value `create` (the default `mode` value in BSB-20).
- **What is missing/ambiguous/contradictory:** The story is correct against the catalog check, but
  the epic description, the PRD's FR-013 and ADR §1a's prose now under-describe it: a reader
  comparing the story to the epic sees a scope expansion ("frontmatter only") that the story
  deliberately exceeds to keep the clone catalog-valid. Separately, the epic guidance's "new"
  vocabulary differs from the stories' `create` value. Neither is a build ambiguity — the stories
  name the exact fields and values — but the epic's own boundary and its traceability text are
  stale relative to the stories that were revised to satisfy `tools/check.py`. This is an
  epic-boundary/documentation gap, not a missing entity or endpoint.
- **Question (if a person must decide):** None needed before code is written; the catalog check
  fixes the behaviour. If the team wants FR-013's "frontmatter" to remain literally limited to
  `SKILL.md`, then the `verify.yaml` rewrite needs a separate requirement or an explicit note in
  the epic; otherwise the epic/PRD wording should be clarified to cover both name-bearing fields.
- **Proposed change:**
  - **BSB-20-PENDING-1:** No statement or acceptance-criterion change. The story already names the
    two rewritten fields and the `create`/`clone`/`edit` mode values.
  - **Cross-document follow-up (not applied here):** On the next `epics.md`/PRD revision, clarify
    BSB-20's description and FR-013 so "the skill name in the copied frontmatter" also covers the
    `verify.yaml` top-level `skill` value required by `tools/check.py`, and use the ADR's
    `create`/`clone`/`edit` vocabulary rather than "new". Clarify ADR SK-001 §1a's clone sentence
    the same way. No change to `epic-map.json` or the requirement IDs.

### Finding 4 — Cross-story verification coverage: the clone proves only `tools/check.py`, while the scaffold and the epic's Definition of Done require the platform manifest gate too
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1 (cross-epic: BSB-19-PENDING-2)
- **Evidence:**
  - BSB-20-PENDING-1 AC 4 (`stories.md:36-39`), titled "Clone passes the catalog's tier-1
    check": it runs only `python tools/check.py` at the branch root and asserts exit code 0 and no
    output line naming `skills/sdlc-plan-workshop`.
  - BSB-19-PENDING-2 AC "Unedited scaffold passes the catalog's static manifest checks"
    (`BSB-19/_epic/stories.md:97-100`): it runs both `python tools/check.py` and the tier-1
    `bheembhai-verify`, asserting check.py exits 0 and tier-1 returns verdict `pass`.
  - ADR SK-001 §1b: "Manifest valid | Tier 1: `bheembhai-verify` on the skill's `verify.yaml`, and
    `tools/check.py`". BSB-20's Definition of Done (`epics.md:309-310`) says both flows "follow
    the same edit, run, scan, Ready and submit path as a newly created build."
  - `README.md:38-39` calls `python tools/check.py` tier 1 and `bheembhai-verify lint` tier 2, so
    the phrase "tier-1 check" in BSB-20-PENDING-1 AC 4 and BSB-19-PENDING-2 does not name the same
    checker consistently.
- **What is missing/ambiguous/contradictory:** The same epic-level "Manifest valid" Ready check is
  proven by two different sets of checks in the two sibling stories. A clone of an existing catalog
  skill is likely to pass `bheembhai-verify` unchanged except for the renamed top-level `skill`,
  but BSB-20-PENDING-1 never runs it, so an implementer can treat `tools/check.py` success as proof
  that the clone is manifest-valid and discover the platform save gate's result only later. The
  risk is low because the source is already a catalog skill and the story copies every other byte,
  but the epic's DoD and BSB-19's standard set a higher bar than BSB-20's ACs.
- **Question (if a person must decide):** None needed for a product decision; the fix is a
  verification-scope choice in BSB-20-PENDING-1 (run the same platform gate as the scaffold, or
  state why the source's existing result carries over).
- **Proposed change:**
  - **BSB-20-PENDING-1:** Either add to AC 4 (or a new AC) that the pinned `bheembhai-verify lint`
    exits 0 on the clone after the two name rewrites, or add a Notes sentence that the source
    skill's verifier result carries over unchanged except for the top-level `skill` value and that
    only `tools/check.py` must be re-run. Rename the scenario so "tier-1" matches `README.md`'s
    numbering (check.py) if the verifier is intentionally out of scope.
  - **Cross-epic:** BSB-19-PENDING-2 needs no change; it already asserts both checks. If BSB-21's
    future save story relies on the same manifest check, it should use the same pair of checks.
    No BSB-19 or BSB-21 story is changed in this pass.

## Open questions

None. The six questions in the previous report have been resolved by the choices recorded in
`_epic/revisions.md` Pass 2 and are embodied in the current stories; the choices are internally
consistent and the remaining items above are either a wording correction with a stated intended
split (Finding 1) or cross-epic/documentation follow-ups (Findings 2–4). No product answer is
needed before `sdlc-plan-stories-write` applies Finding 1.

## Proposed changes

`docs/product/epics/BSB-20/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-20-PENDING-1** — Out of scope: replace "the shared create form and `POST /builds` handler
  (BSB-19-PENDING-1)" with a statement that BSB-19-PENDING-1 owns the base create route/create mode
  of the single `GET /builds/new` + `POST /builds` handler and that this story adds the clone mode
  to that same handler, not a second handler (Finding 1). Optional, advisory: add the
  `bheembhai-verify lint` proof or the carry-over Notes sentence (Finding 4). No other statement,
  acceptance criterion or requirement ID changes; the clone rewrite and `head_sha` rules stay as
  written.
- **BSB-20-PENDING-2** — Out of scope: make the same rewording for the edit mode — BSB-19 owns the
  base create route/create mode, this story adds the edit mode to the same handler and keeps the
  Notes' statement that BSB-19-PENDING-1/-3 own the shared pieces and the validator's `mode`
  parameter (Finding 1). No other statement, acceptance criterion or requirement ID changes; the
  FR-125 resolved-target AC and the BSB-21 forward note stay as written.
- **`story-map.json`** — No change. The two story keys, summaries and requirement IDs already
  match the current stories.
- **Cross-epic follow-ups (not applied in this pass):**
  - **BSB-19-PENDING-1** — add the reciprocal sentence that the shared handler is extended by
    BSB-20's clone/edit modes through the `mode` parameter (Finding 1).
  - **BSB-19-PENDING-3** — name the edit flow and its inverted existence rule alongside the clone
    flow, matching BSB-20-PENDING-2's `mode`-parameter note (Finding 1).
  - **BSB-36** — state what happens to the fixed `build/<skill-name>` branch after a build is
    merged or abandoned, since BSB-20's Out of scope assigns that cleanup there (Finding 2).
  - **`PRD.md` FR-013, `epics.md` BSB-20 description and ADR SK-001 §1a** — clarify the clone's
    `verify.yaml` `skill` rewrite and the `create`/`clone`/`edit` mode vocabulary (Finding 3).
  - **BSB-21** — its save story must assert that a save on an edit build commits only to the
    existing `skills/<skill-name>/` folder (the FR-125 proof already handed off in BSB-20-PENDING-2's
    Notes). No BSB-21 story exists yet; this is a forward note.

No change is proposed to `epic-map.json`, the requirement IDs, the story set, the PRD's FR/NFR
identifiers, or Jira. No Jira write was made; publication remains `sdlc-tracker-sync`'s job.

## Architecture impact

None. The stories need no entity, field, endpoint or integration that ADR SK-001 lacks: `builds`
with `kind`, `cloned_from`, `branch`, `head_sha` and `ready_sha` is §9; the fixed
`build/<skill-name>` branch, the whole-folder clone and the create scaffold are §1a; the Ready
manifest check is §1b; and `base_sha` is the column BSB-19-PENDING-1 adds to the same record for
the epic's base-SHA requirement. The catalog's folder-name rules are already enforced by
`tools/check.py`. No design-stage pass is needed before sequencing.

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
whose Out of scope and Notes hand the clone reuse to BSB-20. This is a deliberate, non-contradicting
split, not a duplicate claim. No foreign requirement is claimed by either BSB-20 story. No FR/NFR
wording drift was found in the IDs or their PRD rows; the remaining wording issue is the epic/PRD
description of the clone rewrite in Finding 3, not a requirement-ID change. BSB-20 maps no NFR, and
NFR-012 (accessibility) is assigned to BSB-38, so no epic-wide silent NFR is left unowned here.

## Dependency-note sanity check

Mostly consistent; two cross-epic mismatches remain (Findings 1 and 2).

- **Real keys only.** Every referenced key exists: BSB-19-PENDING-1 and BSB-19-PENDING-3 are in
  BSB-19's `story-map.json`; BSB-18, BSB-21 and BSB-36 exist as epics; there is no dangling draft
  key.
- **Reciprocated.** BSB-20-PENDING-1/-2 depend on BSB-18 for the signed-in author and the local
  `users` row, and BSB-18's epic Notes say every other epic depends on that record and the
  per-request gate. They depend on the external catalog repository `bheembhai-skills`, which
  `PRD.md` §8 and ADR SK-001 §1a name as an external prerequisite. For the clone flow, BSB-19's
  side is written: BSB-19-PENDING-1 Out of scope names "cloning (BSB-20)" and BSB-19-PENDING-3's
  Out of scope and Notes say the clone flow reuses the validator and collision check.
- **One-sided — Finding 1.** BSB-20-PENDING-2 depends on BSB-19-PENDING-1/-3 for the edit flow and
  the shared validator's `mode` parameter, but BSB-19-PENDING-1/-3 name only the clone flow and
  define no `mode` parameter. The BSB-20 side is written; the earlier-built BSB-19 side is not.
  The same finding covers the contradictory Out-of-scope wording in both BSB-20 stories.
- **One-sided — Finding 2.** BSB-20's Notes and Out of scope assign branch cleanup after a merge
  or abandonment to BSB-36, but BSB-36's functional scope does not mention deleting, reusing or
  finalising the `build/<skill-name>` branch.
- **Forward hand-off, not a gap.** BSB-20-PENDING-2's Notes require BSB-21's save story to assert
  the FR-125 no-second-folder rule. BSB-21 has no decomposed stories yet, which is normal
  cross-epic sequencing; the dependency is written on the BSB-20 side.
- **Epic-level wording (informational).** BSB-19's epic Notes say "the name validator and scaffold
  writer [are] reused by the cloning and edit-build epic." BSB-20 uses the name validator but not
  the scaffold writer: the clone copies the source folder and the edit build reuses the existing
  folder. Correct the BSB-19 epic note on a later BSB-19 revision; no BSB-20 story change.
- **Ordering not computed.** `epics.md` lists BSB-18, BSB-19 and BSB-20 in that order, and no
  `epic-sequence.md`/`.json` exists for BSB-20. This pass only records the dependency gaps; build
  order remains `sdlc-plan-epic-sequence`'s job.
