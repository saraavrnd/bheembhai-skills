# Epic Review — BSB-42: Skill editing, build state & readiness tracking

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-17 · **Stories reviewed:** BSB-42-PENDING-1, BSB-42-PENDING-2

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-42/_epic/epic-review.md`.

## Context loaded

- **Target work item `SkillBuilder-2` — unavailable.** A read-only Atlassian REST fetch of
  `https://saraavrnd.atlassian.net/rest/api/3/issue/SkillBuilder-2` returns HTTP 404 ("Issue does
  not exist or you do not have permission to see it"); the site's project list contains BEEM, BSB,
  EX, GRAP and LNPRTL and no `SkillBuilder` project. This matches `docs/product/PRD.md` §8 and the
  input note in this epic's `_epic/stories.md`. The Atlassian MCP server configured in `.mcp.json`
  was not exposed as a tool in this session (the CLI reports the `atlassian` entry invalid and
  skipped), so the read-only Jira REST API was used. The work item contributes no scope here.
- **Epic:** `BSB-42` "Skill editing, build state & readiness tracking" (Jira `BSB-42`, fetched;
  status To Do; labels FA-3, MVP; no child issues and no issue links yet). Loaded its summary,
  description, functional scope, edge cases, implementation guidance/dependency order, Definition
  of Done, covered requirements and notes.
- **Stories:** all 2 in the epic, from `_epic/stories.md` and `_epic/story-map.json` — the full set,
  not a sample. Story keys are the `BSB-42-PENDING-*` placeholders until `sdlc-tracker-sync`
  publishes them; `story-map.json`'s summaries and requirement mappings match `stories.md`.
- **PRD:** `docs/product/PRD.md` §5 FA-3, §6 FR-018–FR-022, FR-127 and FR-162 (the seven
  requirements `epic-map.json` assigns to BSB-42), §8's "Authoring surface" and "Edit builds"
  constraints, and §7 (no NFR is mapped to FA-3).
- **Design input:** `docs/adr/SK-001-skill-builder.md` §1a (a build is a branch; each save is a
  commit; runs and scans are recorded against the commit SHA), §1b (Ready at a commit SHA; any new
  commit clears Ready), and §9 (the `builds` table: `id`, `skill`, `kind`, `cloned_from`, `branch`,
  `created_by`, `head_sha`, `ready_sha`, `pr_url`, `state`). Also read `_epic/stories.md` of BSB-41
  (the edit-build fixture, `build/sdlc-research-summarise`, and its "An edit changes the existing
  folder in place" save scenario) and BSB-39 (the alice/sub-12345 fixture and `builder_session`).
  There is no `docs/architecture.md`, `docs/data-model.md`, `docs/api-contracts/` or
  `docs/ui-conventions.md` in this repo; SK-001 is the committed design reference available to this
  pass, and the findings below are grounded in it plus the PRD, the epic text and the sibling
  stories.
- **Other epics checked for cross-epic fit:** `epic-map.json` entries for BSB-40 ("Build creation &
  skill scaffolding" — build entity, `build/` branch, name rules, build list), BSB-41 ("Cloning &
  edit builds" — clone/edit build kinds and their skill folders), BSB-51 ("Readiness checks &
  packaging gates" — FA-10B writes `ready_sha`), BSB-54 ("Catalog submission" — FR-107–FR-115,
  including `state` values and FR-114's submitted-build save) and BSB-45 ("Run setup & skill
  packaging" — packaging pins the build head). No `epic-sequence.md`/`.json` exists yet, so relative
  build order cannot be confirmed in this pass — that remains `sdlc-plan-epic-sequence`'s job.

## Findings

### Finding 1 — Epic-wide scope boundary & requirement coverage: the "edit/load a file" surface for FR-127 is owned by neither story

- **Severity:** Blocking
- **Stories touched:** BSB-42-PENDING-1, BSB-42-PENDING-2
- **Evidence:**
  - FR-127 is assigned to BSB-42 by `epic-map.json` and is listed as covered by
    BSB-42-PENDING-1 in `_epic/stories.md`'s Coverage summary and in the story's own "Covered
    requirements". FR-127's text is "An author edits the content of a file in a build's skill
    folder" (`PRD.md` §6); the epic's functional scope repeats it.
  - BSB-42-PENDING-1's Story says "I want to edit and save a file in my build's skill folder", but
    all seven of its acceptance scenarios are `PUT /api/builds/{build_id}/files/{path}` save calls.
    None loads a file's current content, names a page or route where the author views/edits that
    content, or asserts anything about the edit action itself. The only "edit" in the story is the
    content supplied in the save body.
  - The Save contract in the stories preface (line 95) defines `base_sha` as "the 40-hex head SHA
    the author loaded before editing", but no story defines the read that produces the content the
    author loads or exposes the file to an editor.
  - BSB-42-PENDING-1's "Out of scope" defers "the build page (BSB-42-PENDING-2)". BSB-42-PENDING-2
    owns the build page, but its read contract only defines `GET /api/builds/{build_id}` fields
    (`build_id`, `skill_name`, `branch`, `head_sha`, `ready_sha`, `ready`, `state`) and three
    `data-testid` elements (`build-head-sha`, `build-readiness`, `build-ready-sha`) — no file list,
    file content or edit surface. BSB-42-PENDING-2's own "Out of scope" does not claim or mention a
    file-editing surface either.
  - In other words, the story that defers the page and the story that owns the page together leave
    FR-127's edit action unowned. This is invisible from either story alone: Story 1 looks like it
    covers FR-127 through its save bodies, and Story 2 looks complete for FR-020/021/022.
- **What is missing/ambiguous/contradictory:** FR-127 is claimed but never exercised by an
  acceptance criterion, and the epic's DoD ("An author can edit and save a file") is met only for
  "save". A developer implementing the two stories exactly as written would build the save endpoint
  and the head/readiness page but no way for an author to open a file from the build's skill folder
  and edit it. The `base_sha` the save requires is likewise obtained from nowhere.
- **Question (if a person must decide):** Which story owns the surface that lets an author load a
  file's current content (and the head SHA that becomes `base_sha`) from the build's skill folder:
  (a) BSB-42-PENDING-1 adds a file-read/edit surface and its acceptance criteria, (b) BSB-42-PENDING-2's
  build page owns it, or (c) it is deliberately delivered by another epic, in which case Story 1
  must say so and must stop claiming FR-127?
- **Proposed change:**
  - **If (a) — BSB-42-PENDING-1 owns it:** add a read contract and one scenario, e.g.
    `GET /api/builds/{build_id}/files/{path}` returns `path`, `content`, `encoding` and the current
    `head_sha`; the scenario loads `SKILL.md`, asserts its content equals the fixture blob, and
    then uses the returned `head_sha` as `base_sha` in the existing save scenario. Add the read
    route beside the save route in the Save contract and keep FR-127 in the story's Covered
    requirements.
  - **If (b) — BSB-42-PENDING-2's build page owns it:** add the file-list/content/edit surface to
    the build-page read contract with its own scenario, and move FR-127 to BSB-42-PENDING-2 in
    `stories.md`'s coverage summary, the story's Covered requirements and `story-map.json` (a
    revise-mode change).
  - **If (c) — another epic owns it:** add the owning epic/story key to BSB-42-PENDING-1's
    Notes/dependencies and Out of scope, and remove FR-127 from BSB-42-PENDING-1's Covered
    requirements and from `story-map.json`'s `requirement_ids` for that story so the traceability
    is accurate.
  - **Same change for both stories:** once the answer is chosen, add the same one-sentence
    statement of where the editor lives and what the author loads for `base_sha` to each story's
    Notes/dependencies, so neither story's implementer has to infer it from the sibling.
  - **`_epic/stories.md` (preface):** state the owner of the editor/file-read surface next to the
    existing "Save contract" and "Build-page read contract" paragraphs.

### Finding 2 — Cross-epic dependency notes: BSB-42-PENDING-2 reads the `builds` row, branch, build kinds and `state` whose owners it never names

- **Severity:** Advisory
- **Stories touched:** BSB-42-PENDING-2 (with BSB-42-PENDING-1 as the sibling that does record the
  same upstream dependencies)
- **Evidence:**
  - BSB-42-PENDING-2's read contract returns `build_id`, `skill_name`, `branch`, `head_sha`,
    `ready_sha`, `ready` and `state` — fields that come from the `builds` row and the
    `build/<skill-name>` branch, and its fixture is an `edit` build.
  - BSB-42-PENDING-2's Notes name only `BSB-42-PENDING-1`, `FA-10B (BSB-51)` and `FA-15 (BSB-54)`.
    They never name BSB-40 (build entity, `build/` branch, build list) or BSB-41 (the `create`,
    `clone` and `edit` build kinds and their skill folders), although the story says the contract
    "applies to create, clone and edit builds alike because all three kinds use the same `builds`
    row and build branch".
  - The sibling BSB-42-PENDING-1 does record them: "Depends on FA-2A (BSB-40) for the build entity,
    the `build/` branch cut from `main` and the build list, and on FA-2B (BSB-41) for the `edit`
    build kind and its existing skill folder."
  - `state` (open/submitted/merged/abandoned) is FR-113's and is owned by BSB-54 per
    `epic-map.json`; BSB-42-PENDING-2 lists `state` in its read model and defers "build state
    transitions (FR-113)" in Out of scope, but its Notes name BSB-54 only for readiness and FR-114,
    not for the `state` values it returns.
  - `epic-map.json` confirms BSB-40 owns FR-006–FR-010, FR-015–FR-017, FR-143 and FR-144; BSB-41
    owns FR-011–FR-014 and FR-124–FR-126; BSB-54 owns FR-107–FR-115 including FR-113.
- **What is missing/ambiguous/contradictory:** Read on its own, BSB-42-PENDING-2 looks as if the
  `builds` row, build branch, build kinds and `state` values already exist with no upstream owner.
  This is the legitimate-cross-epic-deliverable case where the depending story's own Notes stay
  silent: no architecture change is needed, but the dependencies should be written down so the
  story is not sequenced or built as if it were standalone. The same gap would otherwise be
  re-discovered by `sdlc-deliver-story-design`.
- **Question (if a person must decide):** None — the owners are already fixed by `epic-map.json`;
  the fix is a dependency-note correction.
- **Proposed change:**
  - **BSB-42-PENDING-2:** add to `Notes / dependencies`: "Depends on BSB-40 for the `builds` row and
    `build/<skill-name>` branch the page reads (`build_id`, `skill`, `branch`, `head_sha`,
    `ready_sha`) and on BSB-41 for the `create`/`clone`/`edit` build kinds and their skill folders.
    The allowed `state` values (open, submitted, merged, abandoned) are FR-113's and belong to
    BSB-54; this story only displays the current value." Keep the existing BSB-51 and BSB-54 notes.

## Open questions

1. **File-load/edit surface (Finding 1).** Which story owns the surface that lets an author load a
   file's current content — and the head SHA used as `base_sha` — from the build's skill folder:
   BSB-42-PENDING-1, BSB-42-PENDING-2's build page, or another epic? The answer decides whether
   FR-127 stays mapped to Story 1 or moves.

## Proposed changes

Per touched story, for `sdlc-plan-stories-write` (revise mode). All changes are proposed, not
applied.

- **BSB-42-PENDING-1:** add the file-load/edit surface and its scenario if the answer to Open
  question 1 is (a), including the read route in the Save contract and the loaded `head_sha` as
  `base_sha`; if the answer is (b), remove FR-127 from its Covered requirements; if (c), name the
  owning epic/story in Notes and Out of scope and remove FR-127. In every case add the
  editor-ownership sentence to Notes/dependencies. Keep the existing save, commit, head and
  rejection scenarios unchanged.
- **BSB-42-PENDING-2:** add the file-load/edit surface and its scenario if the answer to Open
  question 1 is (b), and take FR-127; add the BSB-40/BSB-41/`state` dependency sentence from
  Finding 2 to Notes/dependencies. Its head/readiness scenarios, read contract and Out of scope
  otherwise stand.
- **`_epic/stories.md` (preface):** state which story owns the editor/file-read surface and what
  the author loads to obtain `base_sha` (Finding 1).
- **`_epic/story-map.json`:** change only if the answer to Open question 1 moves FR-127 from
  BSB-42-PENDING-1 to BSB-42-PENDING-2, or removes it from this epic; otherwise no change.

## Architecture impact

None. Both findings close by changing a story's statement, acceptance criteria, scope or dependency
notes. The design the epic relies on already exists in
`docs/adr/SK-001-skill-builder.md` §1a (a build is `build/<skill-name>`; each save is a commit), §1b
(Ready at a commit SHA; any new commit clears Ready) and §9 (`builds.head_sha`, `builds.ready_sha`
and `builds.state`), and the catalog git repository is the durable file store. No new entity, field,
endpoint or integration outside this epic's own deliverables is required.

## Requirement coverage check

No — six of the seven requirements assigned to BSB-42 are exercised by at least one story's
acceptance criteria, but FR-127 is claimed without an exercising acceptance criterion (Finding 1):

| Requirement | Story | Exercising acceptance criteria |
|---|---|---|
| FR-018 | BSB-42-PENDING-1 | "Save an edited file creates one commit and advances the build head"; binary, no-op, conflict and failure scenarios |
| FR-019 | BSB-42-PENDING-1 | The same scenarios assert `builds.head_sha` equals the new commit / stays unchanged on a no-op or failure |
| FR-020 | BSB-42-PENDING-2 | "Build page shows the current head SHA" (`build-head-sha` text and `GET /api/builds/{build_id}` `head_sha`) |
| FR-021 | BSB-42-PENDING-2 | "Build page shows Ready only when the ready SHA equals the head SHA", "…Not ready when no ready SHA is recorded", "…when the recorded ready SHA is not the head SHA" |
| FR-022 | BSB-42-PENDING-2 | "A save that creates a commit clears the previously recorded ready SHA", plus the no-op and failed-commit non-clearing scenarios |
| FR-127 | *(claimed by BSB-42-PENDING-1; no exercising AC)* | No scenario loads or edits a file's content; all save scenarios submit content — see Finding 1 |
| FR-162 | BSB-42-PENDING-1 | "Save an edited file creates one commit and advances the build head" and the other save scenarios |

Notes:
- FR-022's clearing is performed by the Story 1 save operation but asserted and mapped to Story 2;
  the two stories describe this split consistently in their Notes, so it is non-contradicting, not
  a duplicate claim.
- No NFR is assigned to BSB-42 by `epic-map.json`; NFR-002/NFR-003 belong to BSB-39 and NFR-012 to
  BSB-56. FA-3 raises no feature-area NFR row of its own.
- No requirement-wording drift was found: FR-018–FR-022, FR-127 and FR-162 match the current
  `PRD.md` §6 text, and `epic-map.json`'s `requirement_ids` match the epic's Jira "Covered
  requirements". The PRD's stale §8 bookkeeping (BSB-18–BSB-38, FR-165 "will be mapped") is outside
  this epic and does not change BSB-42's coverage.

## Dependency-note sanity check

No — the notes are mostly correct but one story omits its upstream owners. Mismatches found:

- **BSB-42-PENDING-1 ↔ BSB-42-PENDING-2:** reciprocal and correct. Story 2 depends on Story 1's
  save action and owns the FR-022 rule; Story 1 records that Story 2 owns clearing `ready_sha` when
  a save creates a commit.
- **BSB-42-PENDING-1 → BSB-41-PENDING-2:** reciprocal and correct. Story 1 names BSB-41-PENDING-2's
  "An edit changes the existing folder in place" scenario as depending on this save action, and
  BSB-41-PENDING-2's Notes name FA-3 (BSB-42) for the same save.
- **BSB-42-PENDING-1 → BSB-40, BSB-41, BSB-51, BSB-54:** correct keys and correct dependence.
- **BSB-42-PENDING-2 → BSB-40 and BSB-41:** absent — see Finding 2. The story's read model, fixture
  and "applies to create, clone and edit builds" sentence depend on them.
- **BSB-42-PENDING-2 → BSB-54:** partially correct. BSB-54 is named for readiness and FR-114, but
  not for the `state` values the read model returns; the same note should name FR-113's owner.
- **BSB-42-PENDING-2 → BSB-51:** correct key and correct dependence for `ready_sha`.
- No dependency note refers to a story key that does not exist. `BSB-41-PENDING-2` exists in
  `stories.md`; BSB-40, BSB-41, BSB-51 and BSB-54 exist as epics in `epic-map.json`. BSB-40's and
  BSB-51's own stories are not written yet, so reciprocity on their side cannot be checked in this
  pass. No `epic-sequence.md`/`.json` exists yet, so sequencing position cannot be checked here;
  build order itself is `sdlc-plan-epic-sequence`'s job.
