# Epic Review — BSB-20: Skill cloning & edit builds

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-20-PENDING-1, BSB-20-PENDING-2

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-20/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** `SkillBuilder-2` has no Jira issue on the configured site: a read-only
  `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not exist or you do not
  have permission to see it"). The Atlassian MCP tools were not exposed in this session, so the
  same site's REST API was queried read-only (no Jira writes). `PRD.md` §8 and `epics.md`'s source
  note record the same result and ground the product in ADR SK-001.
- **The epic in this run is BSB-20.** `GET /rest/api/3/issue/BSB-20` returned HTTP 200: Epic
  "Skill cloning & edit builds", with a description, functional scope, dependency order,
  Definition of Done and covered requirements matching `epics.md`; `epic-map.json` records it under
  FA-2/MVP. It has no child issues yet and no acceptance-criteria field (Epics carry the
  description instead).
- **All 2 stories in BSB-20**, from `stories.md` and `story-map.json` in one read each —
  BSB-20-PENDING-1 and BSB-20-PENDING-2 (full set, not a sample).
- **BSB-19's 3 stories**, because both BSB-20 stories depend on BSB-19-PENDING-1 for the build
  record, branch rule and base_sha and on BSB-19-PENDING-3 for the shared name validator and
  open-build collision check. BSB-19 has a `revisions.md` but no `epic-review.md`.
- **`epic-map.json`** — BSB-20 maps FR-011, FR-012, FR-013, FR-014, FR-124, FR-125 and FR-126.
- **`PRD.md`** — §5 FA-2; §6 the FR rows for those IDs plus FR-010, FR-015, FR-016 and FR-017 (the
  shared name and catalog rules); §7 the NFR rows; §8's source note, external prerequisites and
  edit-build/branch vocabulary.
- **`epics.md`** — the BSB-19, BSB-20, BSB-21 and BSB-36 sections (shared build creation, this
  epic's DoD, the head/readiness/save path, and submission/lifecycle), plus BSB-18's Notes
  (access and the local user record).
- **`docs/adr/SK-001-skill-builder.md`** — §1a (create/clone, the fixed `build/<skill-name>`
  branch, the scaffold shape), §1b (Ready and manifest validity), §6a (`verify.yaml`), §8 (the
  submit/edit-branch path) and §9 (the `builds` columns: `kind`, `cloned_from`, `branch`,
  `head_sha`, `ready_sha`, `state`).
- **The catalog's static check** — `README.md` ("Changing a skill" runs `python tools/check.py`;
  CI runs the same checks) and `tools/check.py` lines 97–106, where `verify.yaml`'s `skill` must
  equal the folder name, and lines 85–86, where `SKILL.md`'s frontmatter `name` must equal it.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md`
  are not committed; the PDLC chain runs `sdlc-arch-design` after planning, so ADR SK-001 is the
  design authority this pass can use. No `epic-sequence.md`/`.json` exists for BSB-20; the
  `epics.md` foreach lists BSB-18, BSB-19 and BSB-20 in that order.

## Findings

### Finding 1 — Cross-story / cross-epic catalog-manifest consistency
- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-1 (cross-epic: BSB-19-PENDING-2)
- **Evidence:**
  - BSB-20-PENDING-1, "Every copied file except SKILL.md is byte-identical to its source":
    "`verify.yaml`, `references/README.md`, `templates/run.md` and `examples/seed.json` are
    byte-identical to their source files." Its Notes repeat the rule: "SKILL.md is the only file
    rewritten, and only its frontmatter name value changes, so the rest of that file and every
    other file stays byte-identical."
  - BSB-19-PENDING-2, "verify.yaml is a valid manifest stub with no checks": "its `skill` value is
    `sdlc-plan-new-skill`."
  - `tools/check.py` lines 97–106: the catalog check loads `skills/<n>/verify.yaml` and errors when
    `v.get("skill") != n` ("verify.yaml skill ... does not match folder"). `README.md`'s
    "Changing a skill" says CI runs `python tools/check.py`.
  - `epics.md` BSB-20 Definition of Done: "Both flows produce builds that follow the same edit,
    run, scan, Ready and submit path as a newly created build."
- **What is missing/ambiguous/contradictory:** The source catalog skill's `verify.yaml` carries the
  source skill's name. Copying it byte-identically into `skills/sdlc-plan-workshop/` leaves
  `skill: sdlc-plan-training`, so `tools/check.py` fails and the clone cannot pass the static
  manifest check or become Ready without a manual edit. BSB-19-PENDING-2's scaffold proves the
  catalog requires `verify.yaml`'s `skill` to equal the folder name; BSB-20-PENDING-1 says the
  only rewrite is `SKILL.md`'s frontmatter `name`. The two stories contradict each other, and the
  clone's "independent, catalog-shaped skill" outcome fails at creation.
- **Question (if a person must decide):** Should the clone rewrite `verify.yaml`'s top-level
  `skill` value to the new name (and should FR-013's "frontmatter" and the epic's "rewrites only
  the skill name in the copied frontmatter" be read as covering it), or is the source-identical
  `verify.yaml` intended and the catalog check changed? (also Open question 1)
- **Proposed change:**
  - **BSB-20-PENDING-1:** In the clone rule, rewrite both name-bearing manifest fields: `SKILL.md`'s
    frontmatter `name` and `verify.yaml`'s top-level `skill`; every other byte of both files and
    every other copied file stays identical. Update AC 2 so `verify.yaml` is exempt from
    byte-identity and assert its `skill` value is the new name; add an AC that
    `python tools/check.py` exits 0 (and tier-1 lint passes) on the clone. Update the Notes
    sentence "SKILL.md is the only file rewritten" to "SKILL.md and verify.yaml's `skill` value are
    the only files rewritten." Update the `story-map.json` summary ("rewriting only the frontmatter
    name") to match.
  - **Cross-epic:** BSB-19-PENDING-2 is the reference rule and needs no change. If the human does
    not read "frontmatter" as covering `verify.yaml`, the BSB-20 epic description and `PRD.md`
    FR-013 wording need a separate clarification; no BSB-19 story change is proposed in this pass.

### Finding 2 — Cross-story / cross-epic shared endpoint contract
- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic: BSB-19-PENDING-1)
- **Evidence:**
  - BSB-19-PENDING-1 Notes: "The create form is served at GET \"/builds/new\" and POST \"/builds\"
    returns the confirmation body; these routes are owned by this epic".
  - BSB-20-PENDING-1 Notes: "The clone form is served at GET \"/builds/new\" with mode clone and
    POST \"/builds\" creates the build."
  - BSB-20-PENDING-2 Notes: "The edit form is served at GET \"/builds/new\" with mode edit and POST
    \"/builds\" creates the build."
  - BSB-19-PENDING-1's four ACs all submit "on the create build form at \"/builds/new\"" with no
    mode and a skill name + description body; BSB-20-PENDING-1 adds a source skill + new name;
    BSB-20-PENDING-2 sends only a skill name.
  - `epics.md` BSB-20 implementation guidance step 1: "add a build mode that distinguishes clone,
    edit and new builds"; ADR SK-001 §9's `builds.kind` enum is `(create, clone, edit)`.
- **What is missing/ambiguous/contradictory:** Three stories share one route and one handler, but
  only BSB-19-PENDING-1 claims ownership and its story has no mode parameter. BSB-20 says "with
  mode clone/edit" without naming how the mode is carried (query parameter, form field, path),
  what the create/default value is, or the request fields each mode accepts. Two implementers can
  build incompatible handlers — one without a mode, one with a different carrier — or BSB-20 can
  add a second handler at the same route. The mode vocabulary is also unsettled: `epics.md` says
  "new", ADR and BSB-19-PENDING-1 use `kind "create"`, and BSB-20 uses "clone"/"edit".
- **Question (if a person must decide):** Should BSB-19-PENDING-1 own the single
  `GET /builds/new` + `POST /builds` handler with a `mode` parameter whose default/create value is
  `create`, with BSB-20 extending it for `clone` and `edit`? What is the exact carrier and the
  request fields per mode? (also Open question 2)
- **Proposed change:**
  - **BSB-20-PENDING-1:** Notes: state the clone form extends BSB-19-PENDING-1's single handler,
    not a second one; name the mode carrier and the allowed values (`create`, `clone`, `edit`,
    matching `builds.kind`), the default, and the clone request fields (source skill + new name).
    Out of scope: add "the shared create form and POST /builds handler (BSB-19-PENDING-1)."
  - **BSB-20-PENDING-2:** Same extension statement; name the edit request fields (skill name) and
    the same mode carrier and values. Out of scope: same shared-handler entry.
  - Same change for both stories: one handler, one mode contract. Cross-epic: BSB-19-PENDING-1
    needs a reciprocal sentence; no BSB-19 change is proposed in this pass.

### Finding 3 — Cross-story build-record contract
- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic: BSB-19-PENDING-2, BSB-21)
- **Evidence:**
  - BSB-20-PENDING-1's clone AC enumerates the new `builds` row as "skill ..., kind \"clone\",
    cloned_from ..., created_by 42, branch ..., base_sha ..., state \"open\" and ready_sha NULL" —
    no `head_sha`. BSB-20-PENDING-2's edit AC enumerates the same columns with `kind "edit"` and
    `cloned_from NULL` — no `head_sha`.
  - BSB-19-PENDING-2, "Scaffold is committed on the build branch and nothing else changes":
    "`builds.head_sha` for build 1 equals that new commit SHA".
  - `epics.md` BSB-21 implementation guidance step 1: "Read files from the build branch at the
    recorded head"; FR-019 records the latest commit SHA as the build head and FR-020 shows it.
    ADR SK-001 §9's `builds` has `head_sha`.
  - BSB-20-PENDING-1's Given fixes `main` at 4f1c and the source folder on `main`, but nothing says
    the source is read at the recorded `base_sha` or that the clone commit's parent is `base_sha`.
- **What is missing/ambiguous/contradictory:** A clone makes a copy commit but never records it as
  the build head; an edit branch starts at `base_sha` but its head is undefined. BSB-21's editor
  and readiness path and BSB-36's submission read `head_sha`; a NULL or disagreeing value breaks
  the shared path the epic's DoD promises. Separately, if `main` advances between base resolution
  and the copy, reading the source from the moving `main` ref can copy content newer than
  `base_sha`, making the clone commit carry unrelated changes and breaking the base/head diff
  contract.
- **Question (if a person must decide):** Should the clone record `head_sha` = the clone commit
  (whose parent is `base_sha`, with the source tree read at `base_sha`) and the edit build record
  `head_sha` = `base_sha`, or is `head_sha` deliberately NULL until BSB-21's first save? (also
  Open question 3)
- **Proposed change:**
  - **BSB-20-PENDING-1:** Add `head_sha` to the row's column list in AC 1 and assert it equals the
    clone commit; assert the clone commit's parent is `base_sha` and the source tree is read at
    `base_sha`; Notes: "The copy commit sets `builds.head_sha`; `base_sha` stays fixed."
  - **BSB-20-PENDING-2:** Add `head_sha` to the row's column list in AC 1 and assert it equals
    `base_sha`; Notes: "The branch has no commit of its own, so `head_sha` starts at `base_sha` and
    BSB-21's first save moves it."
  - Same change for both stories: the row's `head_sha` is defined and asserted.

### Finding 4 — Epic-wide scope boundary / cross-epic lifecycle
- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic: BSB-19-PENDING-1,
  BSB-19-PENDING-3, BSB-36)
- **Evidence:**
  - ADR SK-001 §1a: "It lives on its own branch of `bheembhai-skills`, `build/<skill-name>`, cut
    from `main`."
  - BSB-19-PENDING-1 Notes: "The branch name is the literal prefix \"build/\" followed by the skill
    name."
  - BSB-19-PENDING-3, "Name used by another open build is rejected": "another open build" is a
    `builds` row whose `state` is "open".
  - BSB-36 functional scope: "Move the build state through open, submitted, merged or abandoned";
    it opens a PR from the build branch to `main` and never mentions deleting or reusing the
    branch.
  - BSB-20-PENDING-1/2 create `build/sdlc-plan-workshop` / `build/sdlc-plan-training` from `main`.
- **What is missing/ambiguous/contradictory:** After a skill's first build is merged or abandoned,
  its `build/<skill-name>` branch may still exist. A later edit build — the normal "an enhancement
  is a new build" path from ADR §1a — tries to create the same branch; BSB-19-PENDING-3's
  open-build check does not apply because the prior build is not open. No story or epic says
  whether the builder reuses the branch, deletes it first, or gives each build a unique name, and
  none assigns the cleanup. Two implementers can assume different behavior, and the second edit of
  a skill can fail at branch creation.
- **Question (if a person must decide):** When a prior build for the same skill is merged or
  abandoned, should the builder reuse the existing `build/<skill-name>` branch, delete it first, or
  give each build a unique branch name? Which epic/story owns that lifecycle (BSB-36,
  BSB-19-PENDING-1, or a new rule)? (also Open question 4)
- **Proposed change:**
  - **BSB-20-PENDING-1** and **BSB-20-PENDING-2:** In Notes, state the branch lifecycle rule and
    name its owner; in Out of scope, explicitly assign branch cleanup for merged/abandoned builds
    to the named owner (or state the unique-name rule if that is chosen). If the answer is unique
    branch names, the branch rule in BSB-19-PENDING-1 and ADR §1a needs the same change — a
    follow-up, not this pass.
  - Same change for both stories: the branch lifecycle rule is written in every story that creates
    a build branch.

### Finding 5 — Requirement coverage / epic-level traceability
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-2 (cross-epic: BSB-21)
- **Evidence:**
  - FR-125: "An edit build changes the existing skill folder rather than creating a second skill
    folder."
  - BSB-20-PENDING-2, AC 1: the branch `build/sdlc-plan-training` points at commit 4f1c. AC 2: at
    the branch head, `git ls-tree -d --name-only skills/` returns the same folder list as at 4f1c,
    and no `skills/sdlc-plan-training-copy/` or `skills/sdlc-plan-training-2/` path exists.
  - Since AC 1 pins the branch to 4f1c, AC 2 is true by construction; no edit or save commit has
    occurred. BSB-20-PENDING-2 Notes: "The branch holds exactly one folder ... so the save flow
    delivered in BSB-21 (FR-127) commits to that existing folder and never to a second one."
  - `epics.md` BSB-21 covers save-to-commit (FR-018, FR-127, FR-162).
- **What is missing/ambiguous/contradictory:** FR-125 is claimed by BSB-20-PENDING-2, but its
  acceptance criteria do not exercise the rule: a branch that points at `main` necessarily has
  `main`'s folder list. The first place a second folder could appear is BSB-21's save flow, which
  is not written yet. A per-story review could pass BSB-20-PENDING-2 while the no-second-folder
  rule is never tested. The Notes state the contract correctly, so the risk is traceability, not a
  wrong implementation.
- **Question (if a person must decide):** Should FR-125's verification move to BSB-21's save story
  (with BSB-20-PENDING-2 asserting only the resolved target folder), or should BSB-20-PENDING-2
  keep FR-125 and add an AC that the edit build resolves the existing `skills/<skill-name>/` target
  with no second path? (also Open question 5)
- **Proposed change:**
  - **BSB-20-PENDING-2:** Replace or strengthen AC 2 so it asserts the edit build's resolved target
    is the existing `skills/<skill-name>/` folder (not merely that the branch equals `base_sha`),
    and add a Notes sentence that BSB-21's save AC must assert the commit touches only that folder.
    If the human prefers, move the FR-125 proof to BSB-21 and leave the target-folder assertion
    here.
  - **Cross-epic:** BSB-21's future story needs the no-second-folder AC; no BSB-21 story exists
    yet.

### Finding 6 — Dependency-note sanity (one-sided claim)
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-2 (cross-epic: BSB-19-PENDING-1, BSB-19-PENDING-3)
- **Evidence:**
  - BSB-20-PENDING-2 Notes: "Depends on BSB-19-PENDING-1 for the build record, the branch name
    rule and base_sha, and on BSB-19-PENDING-3 for the shared skill-name validator and open-build
    collision check."
  - BSB-19-PENDING-1 Out of scope names "cloning (BSB-20)" and puts "editing, saving and build-head
    tracking after creation" in BSB-21; it does not name BSB-20's edit-build creation or the edit
    mode of the shared handler.
  - BSB-19-PENDING-3 Out of scope: "clone-build creation (BSB-20), which must reuse this same
    validator and collision check"; its Notes: "The validator and collision check are reused
    unchanged by the clone flow in BSB-20" — clone only.
  - `epics.md` BSB-19 Notes names both ("the cloning and edit-build epic"), but the stories do not.
- **What is missing/ambiguous/contradictory:** BSB-19 is sequenced before BSB-20. An implementer of
  BSB-19-PENDING-1/-3 reading only those stories can scope the shared build-creation handler and
  validator to create+clone and leave the edit flow's open-build collision check to be
  reimplemented. BSB-19-PENDING-1's Out of scope sends "editing, saving and build-head tracking" to
  BSB-21, which reads as content editing, not BSB-20's edit-build creation, so it does not close
  the gap. BSB-20-PENDING-2 correctly claims the dependency, but the BSB-19 side does not
  acknowledge the edit flow at story level. The edit flow also inverts the on-main existence
  check, so "reused unchanged" cannot be literally true for the whole validator.
- **Question (if a person must decide):** Should BSB-19-PENDING-1 and BSB-19-PENDING-3 name the
  edit flow too (the shared handler, validator and collision check are reused by
  BSB-20-PENDING-2, with the existence check inverted for edit), or does BSB-20 own the
  edit-specific inversion? (also Open question 6)
- **Proposed change:**
  - **BSB-20-PENDING-2:** Notes: name BSB-19-PENDING-1/-3 as the owners of the shared
    build-creation handler, name validator and collision check for both clone and edit; state that
    the edit flow contributes the inverted existence check, so the shared validator must expose it
    as a mode parameter (or the edit flow reuses only the pattern and collision parts).
  - **Cross-epic:** BSB-19-PENDING-1/-3 need a reciprocal phrase; no BSB-19 change is proposed in
    this pass.

## Open questions

1. **Finding 1 — manifest rewrite.** Should the clone rewrite `verify.yaml`'s top-level `skill`
   value to the new name, and should FR-013's "frontmatter" and the epic's "rewrites only the skill
   name in the copied frontmatter" be read as covering it, or is the source-identical
   `verify.yaml` intended?
2. **Finding 2 — shared handler and mode.** Should BSB-19-PENDING-1 own the single
   `GET /builds/new` + `POST /builds` handler with a `mode` parameter whose default/create value
   is `create`, with BSB-20 extending it for `clone` and `edit`? What is the exact carrier
   (query parameter, form field, path) and the request fields per mode?
3. **Finding 3 — build head and clone base.** Should the clone record `head_sha` = the clone commit
   (parent `base_sha`, source read at `base_sha`) and the edit build record `head_sha` =
   `base_sha`, or is `head_sha` deliberately NULL until BSB-21's first save?
4. **Finding 4 — branch lifecycle.** When a prior build for the same skill is merged or abandoned,
   should the builder reuse the existing `build/<skill-name>` branch, delete it first, or give each
   build a unique branch name? Which epic/story owns that lifecycle?
5. **Finding 5 — FR-125 proof location.** Should FR-125's verification move to BSB-21's save story,
   or stay in BSB-20-PENDING-2 with an AC that asserts the resolved target folder?
6. **Finding 6 — reciprocal BSB-19 notes.** Should BSB-19-PENDING-1 and BSB-19-PENDING-3 name the
   edit flow explicitly, or does BSB-20 own the edit-specific inversion?

## Proposed changes

`docs/product/epics/BSB-20/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-20-PENDING-1** — Story/ACs/Notes: rewrite `SKILL.md`'s frontmatter `name` and
  `verify.yaml`'s `skill` value to the new name; exempt both from the byte-identical assertion and
  add a `python tools/check.py` (tier-1) AC; define the clone form as an extension of
  BSB-19-PENDING-1's single `GET /builds/new` + `POST /builds` handler with a named mode carrier
  and request fields; add `head_sha` = the clone commit, assert its parent is `base_sha` and the
  source is read at `base_sha`; state the branch lifecycle rule for a prior merged/abandoned build
  and its owner. Closes Findings 1, 2, 3 and 4 (the PENDING-1 side).
- **BSB-20-PENDING-2** — Story/ACs/Notes: define the edit form as the same shared handler with
  mode `edit` and its request fields; add `head_sha` = `base_sha`; strengthen AC 2 to assert the
  resolved existing `skills/<skill-name>/` target and the no-second-folder rule (or defer the
  FR-125 proof to BSB-21 with a note); state the branch lifecycle rule and owner; name
  BSB-19-PENDING-1/-3 as the shared-handler/validator/collision owners for both clone and edit and
  record the inverted existence check. Closes Findings 2, 3, 4, 5 and 6 (the PENDING-2 side).
- **`story-map.json`** — No requirement IDs or story set change. BSB-20-PENDING-1's summary text
  should change from "rewriting only the frontmatter name" to also name the `verify.yaml` `skill`
  rewrite (Finding 1). BSB-20-PENDING-2's summary is unchanged.

Cross-epic follow-ups (not applied in this pass; they need a human decision or their own epic
revision):

- **BSB-19-PENDING-1** — add the reciprocal mode-contract sentence for the shared
  `GET /builds/new` + `POST /builds` handler; add the branch lifecycle rule if the answer changes
  the fixed `build/<skill-name>` name; name the edit flow in Out of scope.
- **BSB-19-PENDING-3** — name the edit flow (BSB-20-PENDING-2) in the validator/collision reuse
  note, not just the clone flow.
- **BSB-19 epic Notes** — the claim that "the scaffold writer [is] reused by the cloning and
  edit-build epic" is not true: the clone copies the source folder and the edit build reuses the
  existing folder; neither BSB-20 story uses the scaffold writer. Correct the epic note on a later
  BSB-19 revision.
- **BSB-21** — its save story must assert that a save on an edit build commits only to the
  existing `skills/<skill-name>/` folder (the FR-125 proof).
- **BSB-36** — its lifecycle scope should say whether the `build/<skill-name>` branch is deleted or
  reused after a build is merged or abandoned.
- **`PRD.md` FR-013 / `epics.md` BSB-20 description** — if "frontmatter" is not read as covering
  `verify.yaml`'s `skill` value, clarify the clone rewrite wording.

No change is proposed to `epic-map.json`, the requirement IDs, the story set, `sdlc-tracker-sync`
or Jira; requirement coverage is unchanged by these edits.

## Architecture impact

None. Every finding is a story-boundary, contract or dependency-note issue. The records and rules
the stories rely on already exist: the `builds` table with `kind`, `cloned_from`, `branch`,
`head_sha`, `base_sha` (the last added by BSB-19-PENDING-1) and `ready_sha` (ADR SK-001 §9), the
fixed `build/<skill-name>` branch rule (§1a), and the catalog's `SKILL.md`/`verify.yaml`
folder-name checks (`tools/check.py`). No new entity, field, endpoint or integration is needed. The
branch-lifecycle finding is a rule to write (reuse, delete, or unique naming), not a missing
record.

## Requirement coverage check

Yes for six of the seven requirements; one traceability defect (Finding 5).

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-011 | BSB-20-PENDING-1 | "Clone creates a build and copies the whole skill folder" (HTTP 201, one `kind "clone"` row) |
| FR-012 | BSB-20-PENDING-1 | The clone branch's `skills/sdlc-plan-workshop/` tree holds exactly the source folder's files at the same relative paths |
| FR-013 | BSB-20-PENDING-1 | "Copied SKILL.md frontmatter carries the new skill name and nothing else changes" — the `verify.yaml` `skill` rewrite is an additional catalog-validity obligation for `tools/check.py`, not named by FR-013 (Finding 1) |
| FR-014 | BSB-20-PENDING-1 | "Cloning leaves the source skill and main unchanged" (source files byte-identical, `main` unmoved) |
| FR-124 | BSB-20-PENDING-2 | "Edit build is opened on a branch cut from the head of main" (branch points at the base commit) |
| FR-125 | BSB-20-PENDING-2 | Claimed, but AC 2 is satisfied by the branch pointing at the base commit; no edit commit exists, so the no-second-folder rule is only provable in BSB-21's save flow (Finding 5) |
| FR-126 | BSB-20-PENDING-2 | "Edit build rejects a skill name that does not exist on main" (HTTP 422, no row, no branch) |

The clone half of FR-015 (a name already on `main`) and FR-016 (a name used by an open build) is
exercised by BSB-20-PENDING-1's duplicate-name and open-build scenarios, but those IDs are mapped
to BSB-19 and are exercised there for create. BSB-19-PENDING-3's Out of scope and Notes explicitly
say the clone flow reuses the same validator and collision check, so this is a deliberate,
non-contradicting split, not a duplicate claim. FR-017's pattern rule is likewise exercised in
BSB-19-PENDING-3 for create and reused by clone; BSB-20-PENDING-1 has no malformed-clone-name AC,
which is acceptable only while that reuse note stands.

No FR/NFR wording drift was found between `epic-map.json` and the current `PRD.md` rows, and the
Jira BSB-20 description matches `epics.md`'s description and DoD. FR-124's wording "from `main`"
versus the PRD's "on a branch cut from `main`" is immaterial.

## Dependency-note sanity check

Mostly yes; two story-level mismatches (Findings 4 and 6) and one epic-level wording inconsistency.

- **Reciprocated and real:** BSB-20-PENDING-1's dependence on BSB-19-PENDING-1/-3 is matched by
  BSB-19-PENDING-3's Out of scope and Notes ("the clone flow in BSB-20") and by
  BSB-19-PENDING-1's Out of scope ("cloning (BSB-20)"). BSB-20-PENDING-1/-2's dependence on BSB-18
  is matched by BSB-18's epic Notes: "Every other epic depends on the local user record and the
  per-request authorization middleware built here."
- **One-sided — Finding 6:** BSB-20-PENDING-2's dependence on BSB-19-PENDING-1/-3 for the edit flow
  is not reciprocated; BSB-19's story notes and Out of scope name the clone flow and send content
  "editing, saving and build-head tracking" to BSB-21, but never mention BSB-20's edit-build
  creation or the edit mode of the shared handler.
- **Unwritten — Finding 4:** no note assigns the branch lifecycle for a prior merged or abandoned
  build; BSB-19-PENDING-3 only checks open builds and BSB-36's scope does not mention deleting the
  branch.
- **Epic-level wording:** BSB-19's Notes say "the name validator and scaffold writer [are] reused
  by the cloning and edit-build epic." Neither BSB-20 story uses the scaffold writer (the clone
  copies the source folder; the edit build reuses the existing folder). BSB-20 depends on the
  build record, branch rule, `base_sha`, validator and collision check, not the scaffold writer.
  Correct the BSB-19 epic note on a later BSB-19 revision; no BSB-20 story change.
- **No dangling keys:** every referenced key exists. BSB-19-PENDING-1 and BSB-19-PENDING-3 are in
  BSB-19's `story-map.json`; BSB-21 and BSB-36 exist as epics but their stories are not written
  yet. BSB-18 is the access epic.
- **Ordering not computed:** `epics.md`'s foreach lists BSB-18, BSB-19 and BSB-20 in that order,
  and no `epic-sequence.md`/`.json` exists for BSB-20. Sequencing remains
  `sdlc-plan-epic-sequence`'s job; this pass only records the dependency gaps.
