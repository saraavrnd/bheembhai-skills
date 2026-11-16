# Revisions — BSB-20

## Pass 1 — 2026-11-15 — `epic-review.md` (cross-story gap review)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md` — verdict CHANGES
REQUESTED, findings 1–7 and open questions 1–3. Target resolution: the run named
"SkillBuilder", which is the product title in `docs/product/PRD.md`, not a Jira issue. The
Atlassian project `BSB` contains only the epics BSB-18 to BSB-38, so the epic was resolved to
**BSB-20** — the epic this review covers and the one the preceding `sdlc-plan-stories-write`
run wrote. No Jira issue was created or changed.

**Applied (findings with no open question, plus the answer-independent parts of Finding 2):**

- **Finding 2 (blocking) — kind-neutral save-confinement wording.**
  - `stories.md` contract table: the `file_outside_skill_folder` message changed from "An
    **edit build** can only change files under …" to "A **build** can only change files under
    `skills/sdlc-fix-bug-triage/`."
  - `BSB-20-PENDING-3`: the 403 response body in *A save cannot create or change a second skill
    folder* now asserts the kind-neutral message.
  - `BSB-20-PENDING-3` Notes: added "Cannot be accepted before BSB-21's save story (FR-162) is
    delivered; BSB-21 owns the `PUT /api/builds/{id}/files/{path}` contract."
  - `BSB-20-PENDING-1` Notes: added that saves on a clone build are confined to
    `skills/sdlc-fix-bug-recheck/` by the same save-path rule, that the save endpoint and its
    contract are BSB-21's, and that the *Clone leaves the source skill unchanged* scenario makes
    its commit directly with git so it does not depend on BSB-21.
  - `BSB-20-PENDING-2` Notes: added that the target folder recorded at open is the folder the
    save-path confinement rule uses.

- **Finding 3 (blocking) — name-rule ownership and FR-017 wording.**
  - `stories.md` contract table: split into **BSB-19-owned name-rule responses**
    (`skill_name_exists` 409, `skill_name_invalid` 422) and **BSB-20-owned responses**
    (`skill_not_found` 404, `file_outside_skill_folder` 403), with a line stating that BSB-20
    asserts the same response the create path returns for the same name.
  - The `skill_name_invalid` message changed to the FR-017 pattern: "Skill name must follow
    sdlc-<area>-<action> using lowercase letters, digits and hyphens."
  - `BSB-20-PENDING-1`: the *Clone refuses a target name that breaks the catalog name pattern*
    422 body now carries that message, and its Notes say the name-rule rows are BSB-19's contract.
  - `BSB-20-PENDING-2`: no AC change; its `skill_not_found` row stays in the BSB-20-owned group.

- **Finding 4 (advisory) — one field name for the build's skill.**
  - `stories.md`: the shared contract section now states the build's own skill is always the
    `skill` field for every kind, and that BSB-19's `create` kind follows the same convention.
  - `BSB-20-PENDING-1`: the clone request body changed from
    `{"kind":"clone","source":"sdlc-fix-bug-triage","name":"…"}` to `…,"skill":"…"` in the
    happy-path and both rejection scenarios. `BSB-20-PENDING-2` already used `skill`.

- **Finding 5 (advisory) — clone source missing on `main`.**
  - `BSB-20-PENDING-1`: added scenario *Clone refuses a source skill that does not exist on
    main* — a clone of `sdlc-fix-bug-recheck` (absent at the `main` head) to
    `sdlc-fix-bug-retry` returns 404 with the `skill_not_found` body naming
    `sdlc-fix-bug-recheck`, creates no `build/sdlc-fix-bug-retry` branch and no `builds` row.
  - `BSB-20-PENDING-1` Notes: added that the source folder is resolved from the current `main`
    head immediately before branching, the same as BSB-20-PENDING-2.
  - `stories.md` contract table: the `skill_not_found` row now covers both an edit build's skill
    and a clone's source.

- **Finding 6 (advisory) — the edit-open commit is empty.**
  - `BSB-20-PENDING-2`: the first scenario now asserts
    `git diff --name-only 4f3c2b1a… origin/build/sdlc-fix-bug-triage` is empty (the edit-open
    commit changes no files); its Notes say the same.
  - `BSB-20-PENDING-3`: the Givens of the first two scenarios now cite this guarantee — *the
    edit build was opened by BSB-20-PENDING-2, whose open commit changes no files* — in addition
    to the "no save has been made" precondition.

- **Finding 7 (advisory) — dependency notes.**
  - `BSB-20-PENDING-3` Notes: added "Depends on BSB-20-PENDING-2 for the edit build and its
    recorded target folder, and on epic BSB-18 for the member session and local `users.id` =
    `42`."
  - `BSB-20-PENDING-2` Notes: added "Prerequisite for BSB-20-PENDING-3."

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 1 / Open questions 1(a) and 1(b) (blocking).** Whether FR-016's "open build" means
  `state` = `open` only or every state with a live branch (`open` and `submitted`); whether the
  rule applies to clone and edit builds as well as create builds and which epic owns it; and
  whether a stale `build/<skill>` branch from a `merged` or `abandoned` build is rejected or
  reset. Applying either branch would invent an error status, code and message and change which
  story owns the rule, so no collision scenario, no collision contract-table row and no
  `BSB-20-PENDING-2` Notes rewrite were made. The `BSB-20-PENDING-3` Givens were likewise left
  without the proposed `state` = `open` wording, since it is tied to the same collision rule.
- **Finding 2 / Open question 3 (blocking, ownership part).** Who owns the save-path
  confinement rule and the `PUT /api/builds/{id}/files/{path}` contract — BSB-21 for every build
  kind, or BSB-20-PENDING-3 sequenced after BSB-21. The answer-independent wording and dependency
  note were applied; the option-(a) change that would replace PENDING-3's exact PUT/403
  assertions with references to BSB-21's contract was not, because choosing it without the
  answer would be guessing.

**Coverage:** unchanged. All 7 requirements mapped to BSB-20 (FR-011 to FR-014, FR-124, FR-125,
FR-126) are still covered by the same three stories. `story-map.json` is unchanged: no story key
or requirement mapping changed, and no Finding 2 answer moved FR-125's save-path part to BSB-21.

**Note for the next review (not a finding of this pass):** the only invalid-name fixture is
`BugTriage`, which fails the lowercase rule. Now that the message states the FR-017
`sdlc-<area>-<action>` pattern, a fixture such as `sdlc-triage` (lowercase but missing the action
segment) would exercise the pattern the message claims. The report asked only for the message
change, so no scenario was added; flagging it so the next reviewer can decide whether to require
it.

## Pass 2 — 2026-11-16 — `epic-review.md` (re-dispatched review, no gate answers)

**Report applied:** the same `docs/product/epics/BSB-20/_epic/epic-review.md` — verdict CHANGES
REQUESTED, findings 1–7 and open questions 1–3. This run was re-dispatched from
`sdlc-plan-epic-review` with no answers at the gate: `settled_decisions` contains zero
eligible/answered entries. Target resolution: the run item is `SkillBuilder`; a read-only Jira
query of project `BSB` returns only epics BSB-18 to BSB-38 and no issue whose summary contains
"SkillBuilder", so `SkillBuilder` is the `docs/product/PRD.md` product title and the target
remains epic **BSB-20**, fetched read-only (summary "Skill cloning & edit builds"; description
and functional scope match `docs/product/epics.md`). No Jira issue was created or changed.

**Applied in this pass:**

- **Finding 1 (answer-independent part only).** `BSB-20-PENDING-3`: all three scenarios' Givens
  now state that the fixture edit build is `id` = `17` in state `open`, matching the state that
  `BSB-20-PENDING-2`'s successful open records. This does not choose an answer to Open question
  1(a) or 1(b).
- The rest of the report's answer-independent changes (Findings 2–7) were applied in Pass 1 and
  remain in place; this pass re-checked them against the report. That covers the owner-split
  contract table, the FR-017 name message, the kind-neutral `file_outside_skill_folder` message,
  the single `skill` request field, the clone-source `skill_not_found` scenario and resolution
  note, the "edit-open commit changes no files" AC, the save-confinement target-folder notes, and
  the `BSB-20-PENDING-2` / `BSB-20-PENDING-3` / epic BSB-18 dependency notes. No story statement,
  AC assertion or contract row was reverted.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 1 / Open questions 1(a) and 1(b) (blocking).** Whether FR-016's "open build" means
  `state` = `open` only or every state with a live branch (`open` and `submitted`); whether the
  rule applies to clone and edit builds as well as create builds and which epic owns it; and
  whether a stale `build/<skill>` branch from a `merged` or `abandoned` build is rejected or
  reset. Applying either branch would invent an error status, code and message and move ownership
  of the rule between epics. Consequently no collision rejection scenario was added to
  `BSB-20-PENDING-1` or `BSB-20-PENDING-2`, no collision row was added to the shared contract
  table, and the `BSB-20-PENDING-1` / `BSB-20-PENDING-2` Notes still point FR-016 at epic BSB-19
  as the report asked to replace.
- **Finding 2 / Open question 3 (blocking, ownership part).** Who owns the save-path confinement
  rule and the `PUT /api/builds/{id}/files/{path}` contract — BSB-21 for every build kind, or
  BSB-20-PENDING-3 sequenced after BSB-21. The answer-independent wording and dependency note
  were applied; the option-(a) change that would replace `BSB-20-PENDING-3`'s exact PUT/403
  assertions with references to BSB-21's contract was not, because choosing it without the answer
  would be guessing.

**Coverage:** unchanged. All 7 requirements mapped to BSB-20 (FR-011 to FR-014, FR-124, FR-125,
FR-126) are still covered by the same three stories, no requirement is claimed twice, and
`story-map.json` is unchanged: no story key or requirement mapping changed, and no Finding 2
answer moved FR-125's save-path part to BSB-21.

**Note for the next review (carried from Pass 1, not a new finding):** the only invalid-name
fixture is `BugTriage`, which fails the lowercase rule; a fixture such as `sdlc-triage`
(lowercase but missing the action segment) would exercise the FR-017 pattern the message now
states. The report asked only for the message change, so no scenario was added.

**Next:** a person must answer Open questions 1(a), 1(b) and 3 in the run hand-off; then run
`sdlc-plan-stories-write` again to apply the collision rule and the save-contract ownership, and
re-run `sdlc-plan-epic-review`.

## Pass 3 — 2026-11-16 — verifier check `story_map` artifact change

**Report applied:** the automated verifier rejection of the previous `sdlc-plan-stories-write`
attempt for epic BSB-20. One check failed: artifact `story_map` — `story-map.json` did not change
since precheck while reviewer feedback was active. Target resolution re-checked this pass: a
read-only Jira search of project BSB for `SkillBuilder` returns no issue, so the run item is the
`docs/product/PRD.md` product title; epic **BSB-20** was fetched read-only (summary "Skill cloning
& edit builds", description and functional scope matching `docs/product/epics.md`). No Jira issue
was created or changed.

**Root cause:** Passes 1–2 applied the report's answer-independent changes to `stories.md` only.
The report says no requirement-ID change is expected until Open question 3 is answered, so the
requirement mapping was correctly left alone — but the map's `summary` values are part of the
traceability record and had not been revisited even though two applied findings changed what
`BSB-20-PENDING-1` asserts.

**What changed:**

- `BSB-20-PENDING-1` summary refined to *Clone an existing catalog skill into a new build under a
  validated new name*, naming two surfaces its scenarios already cover but the old summary did
  not: the clone **source** resolved from the current `main` head (Finding 5's `skill_not_found`
  scenario) and the **validated new name** (Finding 3's `skill_name_exists` / `skill_name_invalid`
  assertions). The same wording is mirrored on the story's `**Summary:**` line in `stories.md`.
  No story key, story statement, scenario, requirement mapping or epic boundary changed.
- Findings 2–7 were re-checked against the report and their previous fixes remain in place; no
  wording was reverted.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 1 / Open questions 1(a) and 1(b) (blocking).** Whether FR-016's "open build" means
  `state` = `open` only or every state with a live branch (`open` and `submitted`); whether the
  rule applies to clone and edit builds as well as create builds and which epic owns it; and
  whether a stale `build/<skill>` branch from a `merged` or `abandoned` build is rejected or
  reset. Applying either branch would invent an error status, code and message and move ownership
  between epics, so no collision scenario or contract row was added.
- **Finding 2 / Open question 3 (blocking, ownership part).** Who owns the save-path confinement
  rule and the `PUT /api/builds/{id}/files/{path}` contract — BSB-21 for every build kind, or
  BSB-20-PENDING-3 sequenced after BSB-21. The answer-independent wording and dependency note are
  applied; option (a) was not chosen without the answer.

**Coverage:** unchanged. All 7 requirements mapped to BSB-20 (FR-011 to FR-014, FR-124, FR-125,
FR-126) are still covered by the same three stories, no requirement is claimed twice, and
`story-map.json` maps each requirement to exactly the same story. The summary refinement changes
no requirement ID.

**Note for the next review (carried, not a new finding):** the only invalid-name fixture is
`BugTriage`, which fails the lowercase rule; a fixture such as `sdlc-triage` (lowercase but missing
the action segment) would exercise the FR-017 `sdlc-<area>-<action>` pattern the message states.
The report asked only for the message change, so no scenario was added.

**Next:** a person must answer Open questions 1(a), 1(b) and 3 in the run hand-off; then run
`sdlc-plan-stories-write` again to apply the collision rule and the save-contract ownership, and
re-run `sdlc-plan-epic-review`.

## Pass 4 — 2026-11-16 — `epic-review.md` (re-dispatched review, no gate answers)

**Report applied:** the same `docs/product/epics/BSB-20/_epic/epic-review.md` — verdict CHANGES
REQUESTED, findings 1–7 and open questions 1–3. This run was re-dispatched with no answers at the
gate: `settled_decisions` has zero eligible and zero answered entries, `reviewer_feedback` is empty
and `upstream_handoff` is null. Target resolution: the run item is `SkillBuilder`. An Atlassian MCP
`jira_search` over all projects for `summary ~ "SkillBuilder" OR text ~ "SkillBuilder"` returns no
issue, so `SkillBuilder` is the `docs/product/PRD.md` product title, not a Jira work item. The
foreach item in the run context is epic **BSB-20**, and `jira_get_issue` read it through the
Atlassian MCP: summary "Skill cloning & edit builds", status To Do, labels FA-2 and MVP, with a
description, functional scope and covered-requirements list identical to `docs/product/epics.md`.
No Jira issue was created or changed.

**Applied in this pass (answer-independent only):**

- **Finding 1 (ownership-record part).** The two stories no longer assert an ownership that epic
  BSB-19's scope does not grant, and no answer to Open questions 1(a)/1(b) was invented:
  - `BSB-20-PENDING-1` Out of scope now cites the shared name validator (FR-015, FR-016 and
    FR-017) without claiming its scope, and states that whether FR-016 also governs clone builds
    is Open question 1(a) and is not decided here.
  - `BSB-20-PENDING-1` Notes: the shared name validator is cited as FR-015 and FR-017; the bullet
    states that FR-016's scope for the `clone` kind is unresolved because BSB-19 scopes the rule to
    create builds and this epic defines no separate concurrency rule.
  - `BSB-20-PENDING-2` Notes: the former "refused by the FR-016 rule owned by epic BSB-19" line is
    replaced with the same statement for the `edit` kind — FR-016 falls short of covering it,
    BSB-19 scopes it to create builds, and the owner is Open question 1(a).
- **Name-rule response ownership corrected.** The shared contract preamble and the
  `BSB-20-PENDING-1` Notes now cite the two BSB-19-owned response rows as **FR-015 and FR-017**,
  not FR-015/FR-016/FR-017: the rows are `skill_name_exists` (FR-015) and `skill_name_invalid`
  (FR-017). FR-016 has no response row because no collision scenario is written while its scope is
  open. The coverage summary above the contract table now says the clone scenarios exercise FR-015
  and FR-017, not FR-016.
- **`BSB-20-PENDING-2` summary.** Refined to *Open an existing catalog skill in an edit build cut
  from the current main head and reject a missing skill*, naming both surfaces its scenarios
  already cover (FR-124 open from `main`, FR-126 missing-skill rejection). Mirrored in the story's
  `**Summary:**` line and in `story-map.json`. No story key, story statement, scenario,
  requirement mapping or epic boundary changed.
- **Header provenance.** `stories.md` now records that BSB-20 was fetched through the Atlassian MCP
  (`jira_get_issue`) rather than only "the Atlassian API".

Findings 2–7 remain applied as recorded in Passes 1–2 and were re-checked against the report this
pass; no story statement, AC assertion or contract row was reverted.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 1 / Open questions 1(a) and 1(b) (blocking).** Whether FR-016's "open build" means
  `state` = `open` only or every state with a live branch (`open` and `submitted`); whether the
  rule applies to clone and edit builds as well as create builds and which epic owns it; and
  whether a stale `build/<skill>` branch from a `merged` or `abandoned` build is rejected or
  reset. Applying either branch would invent an error status, code and message and move ownership
  between epics. No collision rejection scenario was added to `BSB-20-PENDING-1` or
  `BSB-20-PENDING-2`, and no collision row was added to the shared contract table.
- **Finding 2 / Open question 3 (blocking, ownership part).** Who owns the save-path confinement
  rule and the `PUT /api/builds/{id}/files/{path}` contract — BSB-21 for every build kind, or
  BSB-20-PENDING-3 sequenced after BSB-21. The answer-independent kind-neutral wording and the
  dependency note are applied; option (a), which would replace `BSB-20-PENDING-3`'s exact PUT/403
  assertions with references to BSB-21's contract, was not chosen without the answer.

**Coverage:** unchanged. All 7 requirements mapped to BSB-20 (FR-011 to FR-014, FR-124, FR-125,
FR-126) are still covered by the same three stories, no requirement is claimed twice, and
`story-map.json` maps each requirement to exactly the same story. The summary refinement and the
FR-016 notes change no requirement ID.

**Note for the next review (carried, not a new finding):** the only invalid-name fixture is
`BugTriage`, which fails the lowercase rule; a fixture such as `sdlc-triage` (lowercase but missing
the action segment) would exercise the FR-017 `sdlc-<area>-<action>` pattern the message states.
The report asked only for the message change, so no scenario was added.

**Next:** a person must answer Open questions 1(a), 1(b) and 3 in the run hand-off; then run
`sdlc-plan-stories-write` again to apply the collision rule and the save-contract ownership, and
re-run `sdlc-plan-epic-review`.
