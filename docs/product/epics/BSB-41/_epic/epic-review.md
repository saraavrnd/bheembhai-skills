# Epic Review — BSB-41: Cloning & edit builds

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-17 · **Stories reviewed:** BSB-41-PENDING-1, BSB-41-PENDING-2

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-41/_epic/epic-review.md`.

## Context loaded

- **Target work item `SkillBuilder-2` — unavailable.** A direct Atlassian fetch of
  `https://saraavrnd.atlassian.net/rest/api/3/issue/SkillBuilder-2` returns HTTP 404; this epic's
  own `revisions.md` records that a JQL text search for the key also returns no issue and that the
  configured site has no `SkillBuilder` project. This matches `docs/product/PRD.md` §8 and
  `_epic/stories.md`'s input note. The epic reviewed is therefore **BSB-41**, whose full story set
  is on disk from the latest `sdlc-plan-stories-write` run.
- **Epic:** `BSB-41` "Cloning & edit builds" (Jira `BSB-41`, fetched; status To Do; labels FA-2,
  MVP; no child issues and no issue links yet). Loaded its summary, description, functional scope,
  edge cases, implementation guidance/dependency order, Definition of Done, covered requirements
  and notes.
- **Stories:** all 2 in the epic, from `_epic/stories.md` and `_epic/story-map.json` — the full
  set, not a sample. Story keys are the `BSB-41-PENDING-*` placeholders until
  `sdlc-tracker-sync` publishes them; `story-map.json`'s summaries and requirement mappings match
  `stories.md`.
- **PRD:** `docs/product/PRD.md` §5 FA-2, §6 FR-011–FR-014 and FR-124–FR-126 (the seven
  requirements `epic-map.json` assigns to this epic), the BSB-40-owned FR-015–FR-017, §7 (no NFR
  is mapped to FA-2), and §8's "Authoring surface" and "Edit builds" constraints.
- **Design input:** `docs/adr/SK-001-skill-builder.md` §1a (a build is `build/<skill-name>` cut from
  `main`; Create and Clone; a clone copies the whole folder to `skills/<new-name>/` and rewrites
  `name:`; Clone never changes the original), §1b (Ready and submit gate), §8 (Submit opens a PR
  from `build/<skill-name>` to `main`; an edit build follows the same path), and §9 (the `builds`
  table: `kind` = create/clone/edit, `cloned_from`, `branch`, `head_sha`, `state` =
  open/submitted/merged/abandoned). There is no `docs/architecture.md`, `docs/data-model.md`,
  `docs/api-contracts/` or `docs/ui-conventions.md` in this repo; SK-001 is the committed design
  reference available to this pass, and the findings below are grounded in it plus the epic text.
- **Other epics checked for cross-epic fit:** `epic-map.json` entries for BSB-40 ("Build creation &
  skill scaffolding" — build entity, branch creation, name rules), BSB-42 ("Skill editing, build
  state & readiness tracking" — FR-018 save creates a commit, FR-020/021 build page), BSB-54
  ("Catalog submission" — FR-113 build state open/submitted/merged/abandoned, PR flow) and BSB-45
  ("Run setup & skill packaging"). BSB-39's stories were read only to confirm the guard coverage of
  the `POST /api/builds` and `GET /api/builds` routes. No `epic-sequence.md`/`.json` exists yet, so
  relative build order cannot be confirmed in this pass — that remains `sdlc-plan-epic-sequence`'s
  job.

## Findings

### Finding 1 — The `GET /api/builds` observation surface is asserted by both stories but owned by no story or epic

- **Severity:** Blocking
- **Stories touched:** BSB-41-PENDING-1, BSB-41-PENDING-2
- **Evidence:**
  - `_epic/stories.md` preface (lines 11–12): "This epic extends the build-creation endpoint
    `POST /api/builds` with `"build_kind":"clone"` and `"build_kind":"edit"`, and the build list
    `GET /api/builds` used to observe an accepted or rejected build". Line 21: "The builder's build
    list `GET /api/builds` is where an accepted or rejected build is observed. The acceptance
    criteria therefore assert … the build list".
  - BSB-41-PENDING-1 (AC "A main move affects neither an existing clone build nor the base of the
    next clone", line 168): "`GET /api/builds` still reports `base_sha`
    `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` for it". Its two rejected-clone ACs (lines 173 and
    178) assert "`GET /api/builds` lists no build whose `branch` is …".
  - BSB-41-PENDING-2 (AC "Edit build targets the existing skill folder, not a second folder", line
    211): "the build's `skill_path` in `GET /api/builds` is `skills/sdlc-research-summarise`". Its
    rejected-edit AC (line 221) asserts no build with that branch, and its concurrency AC (line
    226) asserts "`GET /api/builds` returns both builds with distinct `branch` values".
  - Neither story's Story/In scope/Out of scope text defines `GET /api/builds`; no AC defines its
    response or item shape. Neither story's Notes name an owner: BSB-41-PENDING-1's Notes (line
    190) name BSB-40 only for "the build entity, the `build/` branch cut from `main`, and name
    validation"; BSB-41-PENDING-2's Notes (line 237) name BSB-40 and BSB-42 only.
  - `epic-map.json` gives BSB-40 the create/branch/name requirements (FR-006–FR-010, FR-015–FR-017,
    FR-143, FR-144) and BSB-42 the build page (FR-020, FR-021); no epic maps an FR for a build-list
    endpoint. `docs/adr/SK-001-skill-builder.md` §9 defines the `builds` table but no list API.
    BSB-39's stories already use `GET /api/builds` as a guard probe, and its `epic-review.md`
    Finding 2 recorded the same unowned `/builds`/`build` API surface without resolving it.
- **What is missing/ambiguous/contradictory:** Both stories make acceptance assertions against a
  data API that no story in this epic builds and no epic claims. The item fields the assertions
  rely on (`base_sha`, `skill_path`, `branch`) are not defined anywhere, so an implementer of
  BSB-41-PENDING-1 and an implementer of BSB-41-PENDING-2 (or of BSB-39's guard tests) can each
  invent a different list shape for the same route. This is an epic-boundary hole visible only
  when the two stories are read together; each story on its own reads as if the list already
  existed.
- **Question (if a person must decide):** Which epic owns `GET /api/builds`, and what is its
  response shape? If BSB-40 owns it, its story set must define the list (the natural fields are
  `build_id`, `build_kind`, `skill_name`, `skill_path`, `branch`, `base_sha`, `head_sha`, and
  `source_skill` for clones); if BSB-41 owns it, one story here must define and assert it.
- **Proposed change:**
  - **BSB-41-PENDING-1 and BSB-41-PENDING-2 (same change for both):** add to `Notes / dependencies`
    a sentence naming the owner of `GET /api/builds` and the item fields the story asserts, e.g.
    "Depends on BSB-40 for `GET /api/builds`, whose list item carries `build_id`, `build_kind`,
    `skill_name`, `skill_path`, `branch`, `base_sha`, `head_sha` and, for clones, `source_skill`."
    If the decision is that BSB-41 owns the list, add one read-only scenario to BSB-41-PENDING-1
    that asserts the item shape for a clone and the same fields for the edit build in
    BSB-41-PENDING-2, and keep both stories' Notes pointing at it.
  - **`_epic/stories.md` (preface):** name the owner of `GET /api/builds` and state the item shape
    instead of asserting the endpoint as given; keep the sentence that the list is the observation
    surface for accepted and rejected builds.

### Finding 2 — Both build kinds assume a free `build/<skill-name>` branch; neither defines what happens when a merged or abandoned build's branch still exists

- **Severity:** Advisory
- **Stories touched:** BSB-41-PENDING-1, BSB-41-PENDING-2
- **Evidence:**
  - BSB-41-PENDING-1 (AC "Clone an existing catalog skill", lines 141–143): the precondition is
    "no open build named `sdlc-research-digest`", and the success branch is
    `build/sdlc-research-digest`. Its rejected-clone ACs (lines 173, 178) assert
    `git branch --list build/<name>` is empty.
  - BSB-41-PENDING-2 (AC "Open an existing catalog skill in an edit build", lines 204–206): the
    precondition is "no open build for `sdlc-research-summarise`", and the success branch is
    `build/sdlc-research-summarise` with `head_sha` equal to the `main` commit.
  - `_epic/stories.md` preface (lines 8–13) delegates "the on-main and open-build checks" to FA-2A
    (BSB-40) and says they are "not restated here". `docs/adr/SK-001-skill-builder.md` §1a says
    "Both refuse a name that already exists on `main` or on another open build"; §8 says Submit
    opens a PR from `build/<skill-name>` to `main`; §9 gives the build state as
    open/submitted/merged/abandoned. Nothing says the branch is deleted when a build is merged or
    abandoned.
  - BSB-54 (FA-15, FR-113) owns the build state machine; its epic edge cases mention "the build
    branch deleted before submission" and "a pull request closed without merging (abandoned)", but
    not a later build reusing a name whose branch still exists. Neither BSB-41 story's Notes
    (lines 190, 237) mention branch disposal or reuse.
- **What is missing/ambiguous/contradictory:** A new edit build for a skill whose previous build
  was merged or abandoned, or a clone using a name from an abandoned build, passes the *open-build*
  check but may find `build/<skill-name>` still exists. The stories then give no behavior: reusing
  the branch would violate BSB-41-PENDING-2's own assertion that the new edit build's `head_sha`
  equals the `main` commit and FR-124's "branch cut from `main`"; refusing needs an error contract
  no story states; deleting the branch is a lifecycle decision no epic owns. This is visible only
  when both build kinds are compared with the build-state epic.
- **Question (if a person must decide):** When a previous build of the same skill is merged or
  abandoned and its `build/<skill-name>` branch still exists, should a new edit or clone build
  (a) reuse and reset the branch to the current `main`, (b) refuse with a named error, or (c)
  rely on the branch having been deleted when the build left the open state? And does BSB-41 own
  that behavior or does BSB-54?
- **Proposed change:**
  - **If BSB-54 owns it (recommended, because it owns the build state machine):** add to
    `Notes / dependencies` of both **BSB-41-PENDING-1** and **BSB-41-PENDING-2** (same sentence for
    each): "A merged or abandoned build's `build/<skill-name>` branch, including its reuse or
    deletion, is owned by BSB-54 (FA-15, FR-113); this story assumes the branch does not exist or
    that BSB-54 resets it to the current `main`." Add the corresponding precondition wording to
    both stories' creation scenarios.
  - **If BSB-41 owns it:** add one scenario to **BSB-41-PENDING-2** covering a pre-existing
    `build/sdlc-research-summarise` from an abandoned build, and one to **BSB-41-PENDING-1**
    covering a clone name left by an abandoned build; assert the chosen behavior and the exact
    rejection body if the answer is to refuse.
  - **`_epic/stories.md` (preface):** state the branch-reuse assumption once for both build kinds,
    next to the existing "open-build checks are FA-2A's" delegation.

### Finding 3 — The shared `POST /api/builds` request contract leaves `description` undefined for clone and edit, and names the target skill differently in each body

- **Severity:** Advisory
- **Stories touched:** BSB-41-PENDING-1, BSB-41-PENDING-2
- **Evidence:**
  - BSB-41-PENDING-1 sends `"description":"Digest research sources for a weekly brief"` in every
    clone body (lines 142, 152, 162, 167, 172, 177), but its AC "Frontmatter name rewritten and
    everything else preserved" (line 153) requires each source's `description`, `compatibility` and
    `model` frontmatter values to be byte-identical in the clone, and the stories preface's
    "Frontmatter name rewrite rule" says exactly one line — the `name:` line — changes.
  - BSB-41-PENDING-2 sends `"description":"Tighten the summary"` in its edit build body (line 205),
    but the edit build creates no commit (its `head_sha` equals `base_sha`, line 206); the only
    description-like change is the author's direct edit of `SKILL.md` in the save scenario (lines
    214–216), which belongs to BSB-42.
  - The clone body names the new skill `"name"`, while the edit body names the existing skill
    `"skill_name"`; the 201 response for both uses `skill_name`. The preface's "Build-creation
    contract" (lines 111–114) lists the response fields but not the request fields.
  - `docs/adr/SK-001-skill-builder.md` §9's `builds` table has no description column;
    `epic-map.json` gives FR-006 ("a skill name and a one-line description") to BSB-40, where the
    create path writes the scaffold `SKILL.md`.
- **What is missing/ambiguous/contradictory:** Both stories send a `description` on the shared
  `POST /api/builds` endpoint, but neither says what happens to it. A developer can reasonably
  write it into the copied frontmatter (breaking BSB-41-PENDING-1's own byte-identity assertion),
  store it on the build (requiring a build field no epic defines), or drop it (leaving a required-
  looking body field inert). The `name`/`skill_name` split on the same endpoint invites two request
  shapes for create/clone and edit that no single contract sentence reconciles.
- **Question (if a person must decide):** For clone and edit builds, is `description` (a) build
  metadata that must be stored and shown, (b) meaningful only for create, or (c) refused? And
  should the request field for the target skill be `name` for create/clone and `skill_name` for
  edit, as the current bodies show?
- **Proposed change:**
  - **BSB-41-PENDING-1 and BSB-41-PENDING-2 (same change for both):** state the chosen `description`
    behavior in `Notes / dependencies` or the story text. If it is build metadata, name the build
    field it lands in (BSB-40's entity) and add it to the `GET /api/builds` item; if it is
    create-only, state that clone/edit ignore it and remove it from these request bodies.
  - **BSB-41-PENDING-1:** keep the explicit sentence that a clone never rewrites the copied
    `description:` frontmatter from the request and that only the `name:` line changes.
  - **BSB-41-PENDING-2:** state what an edit build does with `description` (store on the build or
    ignore) and that it never writes the skill file at build creation.
  - **`_epic/stories.md` (preface):** add the request fields to the "Build-creation contract" and
    either normalise the target-name field across create/clone/edit or say why clone uses `name`
    and edit uses `skill_name`.

### Finding 4 — Story 2's concurrency scenario depends on Story 1's clone endpoint, but only Story 1 records the relationship

- **Severity:** Advisory
- **Stories touched:** BSB-41-PENDING-1, BSB-41-PENDING-2
- **Evidence:**
  - BSB-41-PENDING-1's Notes (line 190): "An open edit build of the same source is unaffected by a
    clone (BSB-41-PENDING-2)."
  - BSB-41-PENDING-2's AC "A concurrent clone of the same skill leaves the edit build untouched"
    (lines 223–226) submits the clone body from Story 1
    (`{"build_kind":"clone","source_skill":"sdlc-research-summarise","name":"sdlc-research-digest",…}`)
    and asserts Story 1's clone branch and files.
  - BSB-41-PENDING-2's Notes (line 237) name only FA-2A (BSB-40) and FA-3 (BSB-42); they do not
    mention BSB-41-PENDING-1.
- **What is missing/ambiguous/contradictory:** The dependency is one-sided. Read on its own, Story 2
  looks buildable without Story 1, even though its concurrency acceptance criterion exercises
  Story 1's clone endpoint and cannot pass until that endpoint exists. A one-sided note is the
  classic setup for someone building B (or sequencing B) without realizing A is required.
- **Question (if a person must decide):** None — the fix is to record the existing dependency on
  both sides.
- **Proposed change:**
  - **BSB-41-PENDING-1:** keep its existing note and make the reciprocal claim explicit: "BSB-41-PENDING-2's
    'A concurrent clone of the same skill leaves the edit build untouched' scenario depends on this
    story's clone endpoint."
  - **BSB-41-PENDING-2:** add to `Notes / dependencies`: "Depends on BSB-41-PENDING-1 for the clone
    endpoint exercised by 'A concurrent clone of the same skill leaves the edit build untouched'."
  - **`_epic/stories.md` (preface):** no change required; the stories' own Notes carry this.

## Open questions

1. **`GET /api/builds` ownership and shape (Finding 1).** Which epic builds the build-list endpoint
   the two stories assert, and what does each list item carry? BSB-40 is the natural owner (it owns
   build creation), but neither its epic scope nor any FR currently names a list.
2. **Branch reuse after a merged or abandoned build (Finding 2).** When `build/<skill-name>` survives
   a merged or abandoned build, should a new edit or clone build reset it, refuse, or assume it was
   deleted — and is that BSB-41's or BSB-54's behavior?
3. **`description` on clone and edit (Finding 3).** Is the `description` in these request bodies
   build metadata, create-only, or rejected, and should the target skill name be one request field
   across the three build kinds?

## Proposed changes

Per touched story, for `sdlc-plan-stories-write` (revise mode). All changes are proposed, not
applied.

- **BSB-41-PENDING-1:** add the `GET /api/builds` owner and item shape to its Notes (Finding 1);
  add the branch-reuse assumption or BSB-54 dependency to its Notes and creation-scenario
  precondition (Finding 2); state the `description` behavior and the target-name field in the
  build-creation contract (Finding 3); make the reciprocal note that Story 2's concurrency
  scenario depends on this story's clone endpoint (Finding 4). Keep the existing `name:`-only
  rewrite rule and its byte-identity assertions unchanged.
- **BSB-41-PENDING-2:** add the same `GET /api/builds` owner and item shape to its Notes (Finding
  1); add the same branch-reuse assumption or BSB-54 dependency to its Notes and creation-scenario
  precondition (Finding 2); state what an edit build does with `description` and reconcile the
  `skill_name` request field (Finding 3); add the missing Notes dependency on BSB-41-PENDING-1
  for the concurrency scenario (Finding 4).
- **`_epic/stories.md` (preface):** name the `GET /api/builds` owner and its item shape (Finding
  1); state the branch-reuse assumption next to the FA-2A delegation (Finding 2); add the
  request fields and the `description` rule to the "Build-creation contract" and reconcile
  `name` vs `skill_name` (Finding 3).
- **`_epic/story-map.json`:** no change proposed — story keys, summaries and requirement mappings
  remain accurate; the changes above do not add, remove or re-map a requirement.

## Architecture impact

None. Every finding closes by changing a story's statement, acceptance criteria, scope or
dependency notes, or by recording an ownership decision for a surface the stories already assume.
The clone and edit build kinds already exist in `docs/adr/SK-001-skill-builder.md` §9 (`kind` =
create, clone, edit), and the build entity, including the base SHA, is already described in the
BSB-40 epic section and mapped to BSB-40 in `epic-map.json`. One design-document drift is recorded for the
BSB-40 pass rather than as a change this epic needs: SK-001 §9's `builds` table lists no
`base_sha` column even though both stories assert it, and it calls the clone source `cloned_from`
while the stories' API field is `source_skill`. Those belong to BSB-40's entity and contract to
define; BSB-41's stories need no new entity, field, endpoint or integration beyond the
`GET /api/builds` ownership decision in Finding 1.

## Requirement coverage check

Yes — all 7 requirements assigned to BSB-41 by `epic-map.json` are exercised by at least one
story's acceptance criteria, each by exactly one story, and no story claims a requirement the
other also claims:

| Requirement | Story | Exercising acceptance criteria |
|---|---|---|
| FR-011 | BSB-41-PENDING-1 | "Clone an existing catalog skill" — 201 with `build_kind` `clone`, new name, new branch |
| FR-012 | BSB-41-PENDING-1 | "Whole skill folder copied, with only the SKILL.md name line rewritten" — 7 paths, 6 equal blob SHAs |
| FR-013 | BSB-41-PENDING-1 | "Frontmatter name rewritten and everything else preserved" — the `name:` line is the only differing line |
| FR-014 | BSB-41-PENDING-1 | "Source skill left unchanged" — source tree SHA and `main` unchanged, clean status |
| FR-124 | BSB-41-PENDING-2 | "Open an existing catalog skill in an edit build" — 201 on `build/<skill-name>` cut from `main` |
| FR-125 | BSB-41-PENDING-2 | "Edit build targets the existing skill folder, not a second folder" and "An edit changes the existing folder in place" |
| FR-126 | BSB-41-PENDING-2 | "Edit build for a skill absent from main rejected" — 404 `skill_not_found_on_main`, no branch, no build |

Notes:
- FR-015–FR-017 are BSB-40's per `epic-map.json`, and both stories' preface and Out of scope
  correctly delegate clone-name validation and the open-build rules to FA-2A; no duplicate claim.
- FR-125's "changes the existing folder" half is exercised through the save scenario, which
  depends on BSB-42's FR-018 save action. BSB-41-PENDING-2's Notes record that dependency and limit
  it to that one scenario; the other two edit scenarios establish the target path without BSB-42.
- No requirement-wording drift was found: FR-011–FR-014 and FR-124–FR-126 match the current PRD
  §6 text, and `epic-map.json`'s `requirement_ids` match the epic's Jira "Covered requirements".
- The PRD's stale §8 bookkeeping (it says the BSB project holds only BSB-18–BSB-38, and that
  FR-165 "will be mapped on the next epics pass" although BSB-39 already maps it) is outside this
  epic and does not change BSB-41's coverage.
- No NFR is mapped to BSB-41 by `epic-map.json`, and FA-2 raises no feature-area NFR row. NFR-002
  and NFR-003 are BSB-39's; BSB-39's stories already name `POST /api/builds` and
  `GET /api/builds` in their guard route list, so this epic does not silently drop an epic-wide
  NFR.

## Dependency-note sanity check

No — the notes are mostly correct but not fully reciprocal and miss two surfaces. Mismatches
found:

- **BSB-41-PENDING-2 → BSB-41-PENDING-1:** Story 2's concurrency scenario depends on Story 1's
  clone endpoint, but Story 2's Notes do not mention Story 1 — see Finding 4.
- **BSB-41-PENDING-1 → BSB-41-PENDING-2:** present ("An open edit build of the same source is
  unaffected by a clone"), and the reciprocal half is the missing item above.
- **Both stories → BSB-40:** correct key. BSB-41-PENDING-1 depends on BSB-40 for the build entity,
  the `build/` branch cut from `main` and name validation; BSB-41-PENDING-2 depends on BSB-40 for
  the build entity and branch creation. BSB-40's own stories are not written yet, so reciprocity
  cannot be checked in this pass.
- **Both stories → `GET /api/builds`:** no note names an owner or the response shape — see
  Finding 1.
- **Both stories → branch disposal after a merged/abandoned build:** no note at all — see
  Finding 2.
- **BSB-41-PENDING-1 → BSB-42, BSB-45 and BSB-54:** correct keys (`epic-map.json` maps FA-3 to
  BSB-42, FA-6 to BSB-45 and FA-15 to BSB-54).
- **BSB-41-PENDING-2 → BSB-42 (FR-018 save):** correct key and correctly limited to the one save
  scenario; no `epic-sequence.md`/`.json` exists yet, so the sequencing position cannot be checked
  in this pass.
- No dependency note refers to a story key that does not exist in this epic or to a nonexistent
  epic. Build order itself is not computed here; that is `sdlc-plan-epic-sequence`'s job.
