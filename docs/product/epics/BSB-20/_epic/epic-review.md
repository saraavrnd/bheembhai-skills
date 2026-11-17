# Epic Review — BSB-20: Skill cloning & edit builds

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-17 · **Stories reviewed:** BSB-20-PENDING-1, BSB-20-PENDING-2

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-20/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** `SkillBuilder-2` has no Jira issue on the configured site. The Atlassian
  MCP tools are not exposed in this session, so the site was queried read-only over its REST API
  (GET only; no Jira write). `GET /rest/api/2/issue/SkillBuilder-2` returned HTTP 404 ("Issue does
  not exist or you do not have permission to see it"), and the visible projects are BEEM, BSB, EX,
  GRAP and LNPRTL — no `SkillBuilder` project. This matches `PRD.md` §8 and `epics.md`'s source
  note; no issue content is assumed from the lookup.
- **The epic in this run is BSB-20.** The run context's work item is `SkillBuilder-2` (the PRD's
  parent), and its `ITEM` is BSB-20; the immediately preceding step wrote BSB-20's stories
  (`sdlc-plan-stories-write`, HEAD `355f0c0`). Read-only `GET /rest/api/2/issue/BSB-20` returned
  HTTP 200: Epic "Skill cloning & edit builds", status To Do, labels `FA-2`/`MVP`, no parent and no
  sub-tasks, with a description matching `epics.md`'s BSB-20 section. No Jira write was made.
- **All 2 stories in BSB-20**, from `stories.md` and `story-map.json` in one read each —
  BSB-20-PENDING-1 (FR-011, FR-012, FR-013, FR-014) and BSB-20-PENDING-2 (FR-124, FR-125, FR-126).
  `story-map.json` maps exactly these two keys with the same requirement IDs and summaries that
  match the current acceptance text.
- **`epic-map.json`** — BSB-20 maps FR-011, FR-012, FR-013, FR-014, FR-124, FR-125 and FR-126; no
  NFR is mapped to this epic (NFR-012 belongs to BSB-38; NFR-002/NFR-003 belong to BSB-18).
- **`PRD.md`** — §5 FA-2, the §6 rows for the seven mapped FRs (lines 85–91 and 198–200), §7's NFR
  table, §8's external prerequisites, no-platform-writes constraint and edit-build paragraph
  (line 352), and §9's `SkillBuilder-2` caveat (line 368).
- **`epics.md`** — BSB-20's Description, Functional scope, Implementation guidance, Definition of
  Done, Covered requirements and Notes (lines 268–325); BSB-18's Notes (lines 192–197, the local
  user record and per-request gate); BSB-19's section and Notes (lines 201–264, including the
  shared name validator and scaffold writer); BSB-21's section and Notes (lines 329–382, save,
  head and readiness); and BSB-36's section (lines 1270–1329, submission state transitions).
- **BSB-19's 3 stories and `story-map.json`**, because both BSB-20 stories depend on
  BSB-19-PENDING-1 for the shared `GET /builds/new` + `POST /builds` handler and on
  BSB-19-PENDING-3 for the shared name validator and open-build collision check.
- **BSB-36's 4 stories and `story-map.json`**, because both BSB-20 stories assign the fixed-branch
  lifecycle after merge/abandonment to BSB-36. BSB-36-PENDING-2 and PENDING-3 explicitly state
  that they neither delete nor finalise the branch and hand the reset to BSB-20-PENDING-2
  (`BSB-36/_epic/stories.md:87-89`, `:265-267`, `:354-355`, `:386-388`). BSB-36's own
  `epic-review.md` records the same ownership loop as Finding 7 and Open question 5.
- **`docs/adr/SK-001-skill-builder.md`** — §1a (build and fixed `build/<skill-name>` branch,
  whole-folder clone, frontmatter rewrite, create scaffold; line 84), §1b (Ready "Manifest valid"
  check), §8 (edit branch and submission; lines 330–343) and §9 (`builds` columns: `kind`,
  `cloned_from`, `branch`, `created_by`, `head_sha`, `ready_sha`, `state`; line 350).
  `tools/check.py:85-86` and `:105-106` enforce the two name-bearing manifest fields;
  `README.md:38-39` labels `python tools/check.py` tier 1 and `bheembhai-verify lint` tier 2.
- **`_epic/epic-sequence.md` / `.json`** — exists for BSB-20 (AWAITING APPROVAL): both stories are
  Wave 1 with no intra-epic edge, and cross-epic prerequisites BSB-18, BSB-19-PENDING-1 and
  BSB-19-PENDING-3 are recorded. Checked for dependency consistency only; the order was not
  recomputed here. The cross-epic row at `epic-sequence.md:57` is now stale (Finding 3).
- **Prior review state — verified against the current text, not assumed.** The previous
  `epic-review.md` (CHANGES REQUESTED, 2026-11-16) and its nine revise passes in `revisions.md`
  were re-checked. Its BSB-20-side remedies are present: PENDING-2's Notes no longer parameterise
  BSB-19's validator and own the inverted existing-on-main predicate; both stories state the fixed
  `build/<skill-name>` reset rule and carry the abandoned/merged reset scenarios; PENDING-1 records
  the FR-013 `verify.yaml` traceability note. The residual gaps that survive are Findings 1–4
  below, all cross-epic or cross-document.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md` are
  not committed; the PDLC design stage runs after planning, so ADR SK-001 is the design authority
  this pass can use. BSB-21 has no decomposed stories yet.

## Findings

### Finding 1 — Epic-boundary branch lifecycle: BSB-20 assigns branch deletion/finalisation to BSB-36, whose stories explicitly disclaim it and hand the reset back to BSB-20

- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic: BSB-36-PENDING-2 and
  BSB-36-PENDING-3).
- **Evidence:**
  - BSB-20-PENDING-1 Out of scope (`stories.md:77-81`): "deleting or finalising
    `build/<skill-name>` after a build is merged or abandoned (BSB-36) — the reset of that fixed
    branch when a new build starts is in scope and asserted above"; its Notes repeat
    "deleting or finalising the branch on merge or abandonment belongs to BSB-36
    (submission and build lifecycle), not this epic" (`:120-123`).
  - BSB-20-PENDING-2 Out of scope (`stories.md:176-179`) and Notes (`:211-214`) carry the same
    BSB-36 assignment.
  - BSB-36-PENDING-2 Notes (`BSB-36/_epic/stories.md:87-89`): "The build branch is neither deleted
    nor finalised here; it stays at its head. BSB-20-PENDING-2 resets `build/skill-name` when a
    later build finds the previous build merged or abandoned". Its Out of scope (`:265-267`) and
    BSB-36-PENDING-3's Out of scope (`:354-355`) again say "deleting or finalising the build
    branch (BSB-20-PENDING-2 resets it for a later build)".
  - `PRD.md` and `epics.md` contain no requirement to delete or finalise a build branch; BSB-36's
    Functional scope (lines 1284–1295) covers state transitions and the PR only.
- **What is missing/ambiguous/contradictory:** The reset behaviour itself is consistent in both
  epics, but the delete/finalise capability is a scope loop: BSB-20 says it belongs to BSB-36;
  BSB-36's stories say it does neither and that BSB-20-PENDING-2 resets the branch for a later
  build. Neither epic builds deletion, and no requirement asks for it. A reader of either epic
  cannot tell whether deletion/finalisation is required and unbuilt, or intentionally dropped.
  This is the same loop BSB-36's review records as Finding 7 / Open question 5.
- **Question (if a person must decide):** Is deleting or finalising the fixed `build/<skill-name>`
  branch after merge/abandonment required for this release? Recommended default: **no** — the
  branch is intentionally left at its head and the next build's reset is the lifecycle. Under that
  answer BSB-20's stories should stop assigning the capability to BSB-36 and state the end state
  directly. If deletion *is* required, it needs a BSB-36 story and BSB-20's assignment stays.
  (Also listed under Open questions.)
- **Proposed change:** Same change for both BSB-20 stories, in Out of scope and Notes only — no
  statement or acceptance criterion changes:
  - **BSB-20-PENDING-1:** Replace "deleting or finalising `build/<skill-name>` after a build is
    merged or abandoned (BSB-36) — the reset of that fixed branch when a new build starts is in
    scope and asserted above" with "deleting or finalising `build/<skill-name>` is not performed by
    this release; after a build is merged or abandoned the branch stays at its head and the next
    build's reset is in scope and asserted above". In Notes, replace "deleting or finalising the
    branch on merge or abandonment belongs to BSB-36 (submission and build lifecycle), not this
    epic" with the same end state.
  - **BSB-20-PENDING-2:** Apply the identical replacement to its Out of scope (`:176-179`) and
    Notes (`:211-214`).
  - **BSB-36 (cross-epic follow-up, not applied here):** If the answer is "no deletion", its
    stories already state the end state and need no change; if "yes", add the branch-cleanup story
    its epic currently lacks.

### Finding 2 — Cross-epic shared-handler/validator contract: BSB-20 names BSB-19 for the edit flow, but BSB-19's stories name only the clone flow and do not define a pattern-only validator

- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic: BSB-19-PENDING-1 and
  BSB-19-PENDING-3).
- **Evidence:**
  - BSB-20-PENDING-2 Notes (`stories.md:183-193`): it depends on BSB-19-PENDING-3 for the "shared
    skill-name pattern validator and open-build collision check" and "reuses BSB-19-PENDING-3's
    skill-name pattern validator and open-build collision check unchanged; the edit mode's
    existence rule is inverted, so this story owns the existing-on-main predicate … and does not
    parameterise BSB-19's validator".
  - BSB-19-PENDING-3 Notes (`BSB-19/_epic/stories.md:197-199`): "The validator and collision check
    are reused unchanged by the clone flow in BSB-20 (FR-015 covers create or clone)." Its Out of
    scope (`:184-188`) names only "clone-build creation (BSB-20)". Its acceptance criteria
    (`:149-172`) define one validator that includes the pattern checks, the reject-on-main check
    and the open-build collision check; the story never separates a "pattern" validator from the
    on-main existence check.
  - BSB-20-PENDING-1 and PENDING-2 both extend BSB-19-PENDING-1's single `GET /builds/new` +
    `POST /builds` handler (`stories.md:73-75`, `:110-116`, `:174-176`, `:207-211`), but
    BSB-19-PENDING-1's Out of scope (`:45-49`) names only "cloning (BSB-20)" and its Notes
    (`:59-63`) say the routes are owned by this epic without a `mode` carrier or an edit-mode
    extension.
  - BSB-19's epic Notes (`epics.md:260-264`) say "The name validator and **scaffold writer** are
    reused by the cloning and edit-build epic." BSB-20-PENDING-1 copies the source folder wholesale
    and BSB-20-PENDING-2 reuses the existing folder; neither uses the scaffold writer.
- **What is missing/ambiguous/contradictory:** The BSB-20 side of the dependency is now written,
  but the earlier-built BSB-19 side is not reciprocal for the edit flow and its vocabulary is
  ambiguous: BSB-20 calls the reused component a "skill-name pattern validator", while
  BSB-19-PENDING-3 describes one "validator" that also rejects a name already on `main`. If
  BSB-19-PENDING-3 is built as written, BSB-20-PENDING-2 cannot reuse that validator unchanged for
  edit without either parameterising it (which the story forbids) or duplicating the pattern
  check. The scaffold-writer sentence is a separate factual error in the BSB-19 epic Notes. This is
  a coordination/interface gap, not a wrong-behaviour gap: the BSB-20 stories state a buildable
  contract.
- **Question (if a person must decide):** None for BSB-20 — its Notes already settle the contract
  (reuse pattern and collision checks, own the inverted predicate, no `mode` parameter). The
  follow-up is a BSB-19 revision. If BSB-19 cannot expose the pattern check separately, the
  BSB-20-PENDING-2 fallback in Proposed changes applies.
- **Proposed change:**
  - **BSB-20-PENDING-1:** No change. Its clone flow shares create's existence rule and reuses
    BSB-19-PENDING-3's checks unchanged.
  - **BSB-20-PENDING-2:** No change under the recommended reading. If BSB-19's validator is not
    separable, add one Notes sentence: "This story implements the skill-name pattern check locally
    rather than calling BSB-19-PENDING-3's validator, because the edit flow's existence rule is
    inverted; the open-build collision check is still shared."
  - **BSB-19-PENDING-1 (cross-epic follow-up, not applied here):** Add to Notes that its shared
    handler is extended by BSB-20's `clone` and `edit` modes through the `mode` carrier, and add
    edit-build creation to its Out of scope alongside cloning.
  - **BSB-19-PENDING-3 (cross-epic follow-up):** Name the edit flow in Out of scope/Notes and state
    the decomposition: pattern check, open-build collision check (both reused unchanged) and the
    on-main existence rule (create/clone only; BSB-20-PENDING-2 owns the inverted edit predicate).
  - **BSB-19 epic Notes (cross-epic follow-up):** Drop "scaffold writer" from the reuse sentence;
    only the name validator is reused by BSB-20.

### Finding 3 — Epic-sequence cross-epic prerequisite row still says the edit flow passes a `mode` parameter

- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-2 (cross-artifact: `_epic/epic-sequence.md`).
- **Evidence:**
  - `epic-sequence.md:57`: "Both stories reuse the shared validator/collision check; the edit flow
    passes a `mode` parameter to invert the existence rule."
  - BSB-20-PENDING-2 Notes (`stories.md:190-193`): the story "reuses BSB-19-PENDING-3's skill-name
    pattern validator and open-build collision check unchanged … does not parameterise BSB-19's
    validator".
  - BSB-19-PENDING-3 Notes (`BSB-19/_epic/stories.md:197-199`): the validator is reused unchanged
    by the clone flow — no `mode` parameter.
- **What is missing/ambiguous/contradictory:** The epic's own sequencing artifact predates the
  Pass 6 revision and now describes the opposite interface from the current PENDING-2 Notes and
  from BSB-19-PENDING-3. An implementer who reads the sequence as the dependency contract could
  build a parameterised validator that the story forbids. The build order itself is unaffected
  (both stories remain Wave 1), so this is a documentation contradiction, not an ordering defect.
- **Question (if a person must decide):** None — the story's Notes are the settled contract; the
  sequence row is stale.
- **Proposed change:**
  - **BSB-20-PENDING-2:** No change.
  - **`_epic/epic-sequence.md` (cross-artifact follow-up, not applied here):** Replace the row's
    "Why" text with "Both stories reuse BSB-19-PENDING-3's pattern validator and open-build
    collision check unchanged; PENDING-2 owns the inverted existing-on-main predicate and does not
    parameterise the validator." Alternatively, re-run `sdlc-plan-epic-sequence` after this review
    so the file is regenerated from the current stories. No `epic-sequence.json` change is needed
    (no edge changed).

### Finding 4 — Epic-boundary traceability: FR-013 and the epic prose still describe a frontmatter-only clone rewrite and a "new" build mode

- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1 (epic boundary; cross-document: `PRD.md` FR-013,
  `epics.md` BSB-20, ADR SK-001 §1a, the Jira epic description); BSB-20-PENDING-2 for the
  `create`/`clone`/`edit` vocabulary.
- **Evidence:**
  - BSB-20-PENDING-1 AC 2 and AC 3 (`stories.md:26-34`) and Notes (`:85-108`) require both
    name-bearing fields to be rewritten: `SKILL.md` frontmatter `name` and `verify.yaml` top-level
    `skill`, with every other byte identical. The Notes record the rationale: `tools/check.py:85-86`
    rejects a mismatched `SKILL.md` name and `:105-106` rejects a mismatched `verify.yaml` `skill`,
    so a source-identical `verify.yaml` cannot pass the catalog's tier-1 check (`README.md:38-39`).
  - `PRD.md:87` FR-013: "Cloning rewrites the skill name in the copied frontmatter."
    `epics.md:274-276` (BSB-20 Description): "rewrites only the skill name in the copied
    frontmatter". `epics.md:305-310` (Definition of Done): "whose frontmatter name matches the new
    skill". ADR SK-001 §1a (line 84): the clone "rewrites `name:` in the frontmatter." The Jira
    epic description (read read-only) repeats the same frontmatter-only sentence.
  - `epics.md:294-295` (Implementation guidance): "add a build mode that distinguishes clone, edit
    and **new** builds", while the stories, ADR SK-001 §9 and the `builds.kind` column use
    `create`, `clone`, `edit`. The Jira description carries the same "new" wording.
- **What is missing/ambiguous/contradictory:** The story is correct against the catalog check, but
  the epic's own Description, DoD and traceability prose (and the FR/ADR/Jira wording)
  under-describe it: a reader comparing the story to FR-013 sees a scope expansion
  ("frontmatter only") that the story deliberately exceeds to keep the clone catalog-valid.
  Separately, the epic guidance's "new" vocabulary differs from the stories' `create` value.
  Neither is a build ambiguity — the story names the exact fields and values — but the epic
  boundary and its traceability text are stale relative to the stories. The story-side
  traceability paragraph already records the reading and names the follow-up.
- **Question (if a person must decide):** None required before code — the catalog check fixes the
  behaviour. If the team wants FR-013's "frontmatter" to remain literally limited to `SKILL.md`,
  the `verify.yaml` rewrite needs a separate requirement or an explicit note in the epic;
  otherwise the epic/PRD/ADR/Jira wording should be clarified to cover both name-bearing fields.
  Recommended default: clarify the documents, because the `verify.yaml` rewrite is required for a
  catalog-valid clone.
- **Proposed change:**
  - **BSB-20-PENDING-1:** No statement or acceptance-criterion change; it already names the two
    rewritten fields and the `create`/`clone`/`edit` values.
  - **BSB-20-PENDING-2:** No change; it already uses `edit` and the shared `mode` values.
  - **Cross-document follow-up (not applied here):** On the next `epics.md`/PRD revision, clarify
    BSB-20's Description and Definition of Done and FR-013 so "the skill name in the copied
    frontmatter" also covers the `verify.yaml` top-level `skill` value required by
    `tools/check.py`, and use the ADR's `create`/`clone`/`edit` vocabulary rather than "new".
    Clarify ADR SK-001 §1a's clone sentence the same way and update the Jira epic description when
    the tracker is next synced. No change to `epic-map.json` or the requirement IDs.

## Open questions

1. **Branch deletion/finalisation (Finding 1).** Is deleting or finalising the fixed
   `build/<skill-name>` branch after a build is merged or abandoned required in this release, or is
   "left at its head, reset by the next build" the intended end state? Recommended default: the
   latter, which matches BSB-36-PENDING-2/-3's stories and requires only the BSB-20 Out-of-scope/
   Notes rewording in Finding 1. If deletion is required, BSB-36 needs a story and BSB-20's BSB-36
   assignment stays.

No other product question is open before `sdlc-plan-stories-write` revises. Findings 2–4 are
cross-epic/cross-document wording fixes with the recommended defaults stated above; they do not
need a gate answer to apply the BSB-20-side proposed changes (none of which change an acceptance
criterion or requirement ID).

## Proposed changes

`docs/product/epics/BSB-20/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-20-PENDING-1** — Out of scope and Notes: replace the "(BSB-36)" branch-cleanup assignment
  with the intended end state ("deletion/finalisation is not performed by this release; after
  merge/abandonment the branch stays at its head and the next build resets it"), as detailed in
  Finding 1. No statement or acceptance-criterion change. Nothing from Finding 2 (its clone-flow
  reuse statement is already correct) or Finding 4 (the story already records the FR-013 rationale
  and rewrites both fields).
- **BSB-20-PENDING-2** — Out of scope and Notes: apply the identical branch-cleanup replacement
  (Finding 1). No statement or acceptance-criterion change. No change for Finding 2 under the
  recommended separable-validator reading; the optional local-pattern-check Notes sentence is the
  fallback if BSB-19's validator cannot be split. No change for Findings 3 or 4.
- **`story-map.json`** — No change. The two summaries already match the current acceptance text;
  none mentions the BSB-36 delete/finalise attribution, so the Finding 1 rewording does not alter
  them. Keys and requirement IDs are untouched.
- **Cross-epic / cross-artifact follow-ups (not applied in this pass):**
  - **BSB-19-PENDING-1 / BSB-19-PENDING-3 / BSB-19 epic Notes** — reciprocate the edit-flow
    handler/validator contract and drop the incorrect "scaffold writer" reuse (Finding 2).
  - **`_epic/epic-sequence.md`** — update line 57's stale `mode`-parameter sentence, or re-run
    `sdlc-plan-epic-sequence` after this review (Finding 3).
  - **`PRD.md` FR-013; `epics.md` BSB-20 Description/DoD/Implementation guidance; ADR SK-001 §1a;
    Jira epic description** — clarify the clone's two name-bearing rewrites and use
    `create`/`clone`/`edit` rather than "new" (Finding 4).
  - **BSB-36** — if the Open question is answered "deletion required", add the branch-cleanup story;
    otherwise its stories already state the intended end state and need no change (Finding 1).
  - **BSB-21** — its future save story must assert that a save on an edit build commits only to the
    existing `skills/<skill-name>/` folder (the FR-125 no-second-folder proof already handed off in
    BSB-20-PENDING-2's Notes). BSB-21 has no decomposed stories yet; this is a forward note, not a
    gap.

No change is proposed to `epic-map.json`, the requirement IDs, the story set, the PRD's FR/NFR
identifiers, or Jira. No Jira write was made; publication remains `sdlc-tracker-sync`'s job.

## Architecture impact

None. The cumulative epic needs no entity, field, endpoint or integration that ADR SK-001 does not
provide: `builds` with `kind`, `cloned_from`, `branch`, `created_by`, `head_sha`, `ready_sha` and
`state` is §9; the fixed `build/<skill-name>` branch, the whole-folder clone and the create
scaffold are §1a; the Ready manifest check is §1b; the edit branch is §1a/§8; and the external
catalog repository is §8. `base_sha` is the column BSB-19-PENDING-1 (an earlier epic, sequenced
before BSB-20) adds to the same record, and both BSB-20 stories' Notes name it, so it is a planned
in-epic addition, not a missing design element. The `verify.yaml` `skill` rewrite is required by
the catalog's existing `tools/check.py` and does not contradict the ADR's clone intent; only its
prose under-describes it. No design-stage pass is needed before sequencing.

## Requirement coverage check

Complete for BSB-20's seven mapped requirements, with no contradicting duplicate claim:

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-011 | BSB-20-PENDING-1 | "Clone creates a build and copies the whole skill folder" (HTTP 201, exactly one `kind "clone"` row with `cloned_from`, branch, `base_sha`, `head_sha`, `state "open"`, `ready_sha NULL`) |
| FR-012 | BSB-20-PENDING-1 | The clone branch's `skills/sdlc-plan-workshop/` tree holds exactly the source folder's five files at the same relative paths and no other file |
| FR-013 | BSB-20-PENDING-1 | "Copied SKILL.md frontmatter carries the new skill name and nothing else changes" (name `sdlc-plan-workshop`; description, role, model and body unchanged); "Every copied file except SKILL.md and verify.yaml is byte-identical to its source" asserts the `verify.yaml` `skill` rewrite. The PRD/epic/ADR prose drift is Finding 4, not a coverage hole |
| FR-014 | BSB-20-PENDING-1 | "Cloning leaves the source skill and main unchanged" (`main` still at `4f1c…`, source files byte-identical) |
| FR-124 | BSB-20-PENDING-2 | "Edit build is opened on a branch cut from the head of main" (HTTP 201, exactly one `kind "edit"` row, branch pointing at the base commit, `head_sha` = `base_sha`) |
| FR-125 | BSB-20-PENDING-2 | "Edit build resolves to the existing skill folder and creates no second one" (resolved target `skills/sdlc-plan-training/`, `git ls-tree -d --name-only skills/` exact, no copy path). The "changes the folder" half is the BSB-21 save commit, deliberately recorded in PENDING-2's Notes (`:202-205`); that is a legitimate cross-epic hand-off written on the depending story, not a silent hole |
| FR-126 | BSB-20-PENDING-2 | "Edit build rejects a skill name that does not exist on main" (HTTP 422, no `builds` row, no branch) |

BSB-20-PENDING-1 also exercises the clone half of FR-015 (name already on `main`) and FR-016 (name
used by an open build) in its duplicate-name and open-build scenarios, but correctly does not claim
those IDs: `epic-map.json` assigns them to BSB-19, whose PENDING-3 exercises the create half and
whose Out of scope/Notes hand the clone reuse to BSB-20. This is a deliberate, non-contradicting
split, not a duplicate claim. No foreign requirement is claimed by either BSB-20 story. BSB-20
maps no NFR: NFR-002/NFR-003 are BSB-18's cross-cutting request gate (named in BSB-18's Notes, and
both stories' "signed-in skill author" precondition inherits it), and NFR-012 (accessibility) is
assigned to BSB-38. No epic-wide silent NFR is left unowned here.

## Dependency-note sanity check

Mostly consistent; the cross-epic mismatches are Findings 1–3.

- **Real keys only.** Every referenced key exists: BSB-19-PENDING-1 and BSB-19-PENDING-3 are in
  BSB-19's `story-map.json`; BSB-18, BSB-21 and BSB-36 exist as epics, and BSB-36's stories are
  written. There is no dangling draft key.
- **Reciprocated — BSB-18.** Both stories depend on BSB-18 for the signed-in author and the local
  `users` row, and BSB-18's Notes say every other epic depends on that record and the per-request
  gate (`epics.md:192-197`). Both stories depend on the external catalog repository
  `bheembhai-skills`, which `PRD.md` §8 and ADR SK-001 §1a name as an external prerequisite.
- **Reciprocated — sibling stories.** BSB-20-PENDING-1 names "opening an edit build
  (BSB-20-PENDING-2)" in Out of scope; PENDING-2 names "creating a fresh or cloned build (BSB-19
  and BSB-20-PENDING-1)". Both are one-way scope exclusions, not ordering edges; consistent.
- **One-sided — BSB-19 (Finding 2).** BSB-20-PENDING-2 says BSB-19-PENDING-3's pattern validator
  and collision check serve the edit flow, and both BSB-20 stories extend BSB-19-PENDING-1's
  handler; BSB-19-PENDING-1 and -3 name only the clone flow and do not define a pattern-only
  validator or a `mode` carrier. The BSB-20 side is written; the earlier-built BSB-19 side is not.
- **One-sided / looped — BSB-36 (Finding 1).** Both BSB-20 stories assign branch deletion/
  finalisation to BSB-36, while BSB-36-PENDING-2/-3 explicitly disclaim it and hand the reset to
  BSB-20-PENDING-2. The reset rule itself is reciprocal; the delete/finalise owner is not.
- **Stale in the epic's own sequence (Finding 3).** `epic-sequence.md:57` still says the edit flow
  passes a `mode` parameter, contradicting the current PENDING-2 Notes. The intra-epic graph
  remains two independent Wave 1 stories with no edge, so build order is unaffected; the row's
  "Why" text needs refreshing or the sequence needs re-running.
- **Forward hand-off, not a gap.** BSB-20-PENDING-2's Notes require BSB-21's future save story to
  assert the FR-125 no-second-folder rule. BSB-21 has no decomposed stories yet, which is normal
  cross-epic sequencing; the dependency is written on the BSB-20 side. `epic-sequence.md` records
  the same forward hand-off and no cycle.
- **Epic-level wording (informational).** BSB-19's epic Notes say "The name validator and scaffold
  writer are reused by the cloning and edit-build epic" (`epics.md:260-264`). BSB-20 uses the name
  validator but not the scaffold writer: the clone copies the source folder and the edit build
  reuses the existing folder. Correct the BSB-19 epic note on a later BSB-19 revision; no BSB-20
  story change (recorded under Finding 2's follow-ups).
- **Ordering not computed.** `epic-sequence.md`/`.json` already exists for BSB-20 and is consistent
  with the stories (both Wave 1, no intra-epic edge, cross-epic prerequisites BSB-18/BSB-19). This
  pass only records the contradictions above; build order remains `sdlc-plan-epic-sequence`'s job.
