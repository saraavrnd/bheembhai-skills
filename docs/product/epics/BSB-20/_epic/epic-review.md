# Epic Review — BSB-20: Skill cloning & edit builds

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-15 · **Stories reviewed:** BSB-20-PENDING-1, BSB-20-PENDING-2, BSB-20-PENDING-3

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-20/_epic/epic-review.md`.

## Context loaded

- **Target resolution.** The run's target was `SkillBuilder`, which is the product title of
  `docs/product/PRD.md`, not a Jira issue (the PRD §8 and the BSB-20 `stories.md` header both
  say this). The Atlassian MCP server was not connected in this session, so the epic was
  resolved from disk: BSB-20 is the epic that the most recent `sdlc-plan-stories-write` run
  wrote (commit `bc0c2ce`), and it has no review yet. Nothing was read from or written to Jira.
- **All 3 BSB-20 stories**, from `docs/product/epics/BSB-20/_epic/stories.md` and
  `story-map.json`: the full set. That covers BSB-20-PENDING-1 (clone), BSB-20-PENDING-2 (open
  edit build) and BSB-20-PENDING-3 (edit-build saves stay in the existing folder). Also read the
  shared "Build and catalog contract" fixture table at the top of `stories.md`.
- `docs/product/epic-map.json`: BSB-20 → FR-011, FR-012, FR-013, FR-014, FR-124, FR-125, FR-126.
- `docs/product/PRD.md`: FR-006 to FR-022, FR-113, FR-124 to FR-127, FR-143, FR-144 and FR-162
  rows; §8 "Edit builds", "Authoring surface", "No platform writes" and "External prerequisites".
- `docs/product/epics.md`: the BSB-19, BSB-20, BSB-21 and BSB-36 sections, plus BSB-18's section
  for the session gate.
- `docs/adr/SK-001-skill-builder.md`: §1a (create and clone, `build/<skill-name>` branches, name
  rules), §1b (Ready), §8 (edit branch → PR path) and §9 (the `builds` table with `kind` and
  `state` (open, submitted, merged, abandoned)). The repo has no separate `architecture.md`,
  `data-model.md`, `api-contracts/` or `ui-conventions.md`. SK-001 §9 is the data model.
- **Cross-epic checks.** Read BSB-18's `stories.md` only for the session fixture, the gate
  middleware and the error-body shape. They are consistent with BSB-20, so there is no finding
  there. BSB-19, BSB-21 and BSB-36 are not decomposed into stories yet, so their `epics.md`
  scope is the reference. No epic-level `sdlc-plan-epic-sequence` output exists yet.

## Findings

### Finding 1 — Epic-wide scope boundary: name/branch collisions for clone and edit builds have no owner
- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2, BSB-20-PENDING-3 (and the epic boundary with BSB-19 and BSB-36)
- **Evidence:**
  - BSB-20-PENDING-2 Notes: "A second open build for the same skill name is refused by the FR-016
    rule owned by epic BSB-19; this story does not add a separate concurrency rule."
  - BSB-20-PENDING-1 Notes rely on "the shared name validator (FR-015, FR-016, FR-017)" from BSB-19.
  - `epics.md` BSB-19 Functional scope: "Reject a **create** build when the name already exists on
    `main` (FR-015), when another open build already uses the name (FR-016) …". BSB-19 scopes the
    rule to create builds only. SK-001 §1a says "**Both** [create and clone] refuse a name that
    already exists on `main` or on another open build" and does not mention edit builds.
  - The branch is always `build/<skill-name>` (SK-001 §1a, and the `stories.md` contract table).
    Every fixture in BSB-20-PENDING-1 and BSB-20-PENDING-2 assumes the case away: "no branch
    `build/sdlc-fix-bug-triage` exists on the origin remote". BSB-20-PENDING-2 only excludes
    `builds` rows with `state` = `open`. So the fixture allows a `submitted`, `merged` or
    `abandoned` row for the same skill (SK-001 §9 and FR-113, owned by BSB-36), and that row's
    `build/<skill>` branch can still exist.
- **What is missing/ambiguous/contradictory:** The two stories each say a sibling epic owns the
  rule, but that epic's scope does not include either of their build kinds. Read side by side:
  - Nobody owns FR-016 for **edit** builds, because BSB-19 only covers create and PENDING-2
    defers to BSB-19.
  - Nobody owns what happens when `build/<skill>` already exists but no build with that skill is
    in the `open` state.

  The second case is not rare. Any skill that came into the catalog through the builder already
  had a `build/<skill>` branch, and a second edit of the same skill needs the same branch name.
  The worst case is a `submitted` build, whose branch has a live catalog PR. A new edit build
  would either fail to create the ref (an undefined error) or reset the branch under the open PR.
  Each of PENDING-1, PENDING-2 and PENDING-3 could resolve this differently.
- **Question (if a person must decide):** (a) Does "open build" in FR-016 mean `state` = `open`
  only, or every state that still has a live branch (`open` and `submitted`)? Does the rule apply
  to clone and edit builds as well as create builds, and which epic owns it? (b) If
  `build/<skill>` already exists on origin for a `merged` or `abandoned` build, or was left over
  from outside the builder, should a new clone or edit build be rejected with a named error, or
  should the stale branch be reset? If it is reset, which epic owns that cleanup (BSB-36's state
  machine or BSB-20)?
- **Proposed change:** Same intent for all three stories, once the questions are answered:
  - BSB-20-PENDING-1: add a rejection scenario for a clone whose target name has a live build
    branch, with the agreed status, code and message added to the shared contract table. Change
    the Notes so they say which epic owns FR-016 for the `clone` kind.
  - BSB-20-PENDING-2: add the same rejection scenario for the `edit` kind (for example, a
    `submitted` build of `sdlc-fix-bug-triage` with `build/sdlc-fix-bug-triage` still on origin).
    Replace the Notes line "refused by the FR-016 rule owned by epic BSB-19" with the actual owner
    and rule. If the answer is "reset a stale branch", add that scenario instead.
  - BSB-20-PENDING-3: change its Givens to "an edit build with `id` = `17` in state `open`", so
    its precondition matches the collision rule above.
  - If the answer moves the rule into BSB-19's or BSB-36's scope, record that hand-off in each
    story's Notes so those epics' decompositions pick it up.

### Finding 2 — Cross-epic architecture fit: BSB-20-PENDING-3 fixes BSB-21's save contract for edit builds only
- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-3, BSB-20-PENDING-1, BSB-20-PENDING-2 (and the epic boundary with BSB-21)
- **Evidence:**
  - BSB-20-PENDING-3 Notes: "Depends on epic BSB-21 for the save endpoint (FR-127 and FR-162). The
    `PUT` request and `200` response in the scenarios are the minimal path contract this story
    needs". Its Out of scope also excludes "the save-to-commit mechanics … (epic BSB-21)". Yet all
    three of its scenarios send
    `PUT /api/builds/17/files/<path relative to the skill folder>`. They assert the response
    fields `path`, `branch` and `commit_sha`, and a 403 `file_outside_skill_folder` body whose
    message reads "An **edit build** can only change files under skills/sdlc-fix-bug-triage/."
  - BSB-20-PENDING-1 Out of scope: "Editing the cloned skill's files after the clone completes
    (epic BSB-21 …)". So clone and create builds get no path-confinement rule from this epic. The
    PENDING-1 scenario "Clone leaves the source skill unchanged" has the author "commit" a file on
    the clone branch without naming the mechanism.
  - `epics.md` BSB-20 Notes: "FA-3 provides the file editing and save-to-commit behaviour that edit
    builds and clones then use". `epics.md` BSB-21 Notes: "Depends on FA-2A/FA-2B for the build and
    its branch". BSB-20 and BSB-21 each name the other as a prerequisite.
- **What is missing/ambiguous/contradictory:** The endpoint belongs to BSB-21, but BSB-20-PENDING-3
  is the only story in the plan that defines its URL shape, response JSON and confinement error.
  It also words them for the `edit` kind only. BSB-21's save story (not written yet) has to
  choose: adopt this contract for all build kinds, or define a different one. If it defines a
  different one, PENDING-3's exact-body assertions break, or clone and create builds end up with
  a different confinement rule from edit builds. Two implementers can build two incompatible
  contracts. PENDING-3 also cannot be accepted until BSB-21's save endpoint exists, while BSB-21
  declares a dependency back on this epic. That is a two-way epic dependency that
  `sdlc-plan-epic-sequence` can only untangle at story level if it is written down.
- **Question (if a person must decide):** Who owns the save-path confinement rule ("every save
  resolves inside `skills/<build.skill>/`; anything outside is refused")? Option (a): BSB-21's save
  story owns it for every build kind (create, clone, edit), with a kind-neutral error message.
  PENDING-3 then shrinks to what only BSB-20 decides: the edit build's target folder is the
  existing `skills/<skill>/`, recorded when the build opens and exercised through BSB-21's
  contract. Option (b): BSB-20-PENDING-3 keeps the rule and the PUT contract, is explicitly
  sequenced after BSB-21's save story, and its error message becomes kind-neutral so clone and
  create builds can share it.
- **Proposed change:**
  - BSB-20-PENDING-3: in either option, change the 403 message to a kind-neutral form (for
    example "A build can only change files under skills/sdlc-fix-bug-triage/."). Add an explicit
    Notes line: "Cannot be accepted before BSB-21's save story (FR-162) is delivered; BSB-21 owns
    the `PUT /api/builds/{id}/files/{path}` contract." Under option (a), replace the exact PUT
    response and 403 assertions with references to BSB-21's contract, and keep only the
    folder-target assertions (the `git diff --name-only` and `git ls-tree` checks).
  - BSB-20-PENDING-1: add a Notes line saying saves on a clone build are confined to
    `skills/sdlc-fix-bug-recheck/` by the same rule, owned where the answer places it. State that
    the "Clone leaves the source skill unchanged" scenario's commit is made directly with git by
    the test, not through the builder's save endpoint, so it does not depend on BSB-21.
  - BSB-20-PENDING-2: add a Notes line saying the target folder it records at open is what the
    confinement rule uses.

### Finding 3 — Cross-epic contradiction: BSB-20-PENDING-1 fixes BSB-19's name-rule error text, and the text misstates FR-017
- **Severity:** Blocking
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2 (shared contract table; epic boundary with BSB-19)
- **Evidence:**
  - The `stories.md` contract table rows `skill_name_exists` (409) and `skill_name_invalid` (422)
    are asserted byte-for-byte in BSB-20-PENDING-1's two rejection scenarios. The 422 message is
    "Skill name must start with 'sdlc-' and use only lowercase letters, digits and hyphens."
  - BSB-20-PENDING-1 Out of scope: "defining or changing the catalog name rules themselves — the
    clone path calls the name validator that create builds use, and epic BSB-19 owns FR-015,
    FR-016 and FR-017."
  - PRD FR-017: "rejects a name that does not follow the sdlc prefix, area segment and action
    segment pattern". SK-001 §1a: names "follow `sdlc-<area>-<action>`". BSB-19 DoD: "All three
    invalid-name cases are rejected with a clear message."
- **What is missing/ambiguous/contradictory:** BSB-20 says it does not own the validator, but its
  contract table fixes the validator's exact output before BSB-19 is decomposed. The fixed 422
  text also describes a looser rule than FR-017. `sdlc-triage` satisfies the message, yet FR-017
  rejects it because it has no action segment. If BSB-19 writes its message to match FR-017,
  PENDING-1's exact-body assertion fails. If BSB-19 copies PENDING-1's text, users get a message
  that misstates the rule. The edge case the epic itself states, "the clone target name must pass
  the same name rules as a new build", needs one shared contract, not two.
- **Question (if a person must decide):** None. This is a wording and ownership fix: the rule is
  fixed by FR-017 and SK-001 §1a.
- **Proposed change:**
  - BSB-20-PENDING-1: change the `skill_name_invalid` message so it states the FR-017 pattern (for
    example "Skill name must follow sdlc-<area>-<action> using lowercase letters, digits and
    hyphens."). Mark both name-rule rows in the contract table as "owned by BSB-19; BSB-20 asserts
    the same response the create path returns for the same name". BSB-19's decomposition will
    then inherit them rather than re-invent them.
  - BSB-20-PENDING-2: no AC change, because its 404 `skill_not_found` row is BSB-20's own. Keep it
    in the contract table, but separate the BSB-20-owned rows from the BSB-19-owned rows so the
    ownership is visible.

### Finding 4 — Cross-story consistency: the same POST contract names the target skill differently per kind
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2
- **Evidence:**
  - BSB-20-PENDING-1 body: `{"kind":"clone","source":"sdlc-fix-bug-triage","name":"sdlc-fix-bug-recheck"}`.
    The build's own skill goes in `name`.
  - BSB-20-PENDING-2 body: `{"kind":"edit","skill":"sdlc-fix-bug-triage"}`. The build's own skill
    goes in `skill`.
  - Both stories' Notes say they extend BSB-19's single `POST /api/builds` contract. Both
    responses, and the `builds` column, call the field `skill`.
- **What is missing/ambiguous/contradictory:** The two sibling stories extend one request contract
  and use two field names for the same concept, "the skill this build authors". BSB-19's create
  body (not yet written) will add a third choice. The stories can be built as written, but the
  API will be inconsistent.
- **Question (if a person must decide):** None. Pick one name. `skill` matches the response and
  the `builds` column.
- **Proposed change:**
  - BSB-20-PENDING-1: use `{"kind":"clone","source":"sdlc-fix-bug-triage","skill":"sdlc-fix-bug-recheck"}`
    (or keep `name` and change PENDING-2 to match).
  - BSB-20-PENDING-2: keep `skill`, or change to `name` to match whichever is chosen.
  - Add the per-kind request body shapes to the shared contract table once, so BSB-19's create
    body follows the same convention.

### Finding 5 — Cross-story scope hole: a clone source missing from the current main is handled by no story
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-1, BSB-20-PENDING-2
- **Evidence:**
  - BSB-20-PENDING-2 resolves the skill from the current `main` head before branching. It has two
    404 `skill_not_found` scenarios, including "Edit build whose skill was deleted from main after
    selection". Its Notes say "A stale listing is never used".
  - BSB-20-PENDING-1 has no scenario and no Notes for a clone `source` that does not exist on the
    current `main` head, including one deleted after the author picked it. Its Out of scope does
    not mention the case either. The epic edge case ("resolve the skill folder from `main` before
    branching so a renamed or deleted folder is caught early") is written for edit builds only.
- **What is missing/ambiguous/contradictory:** The same stale-listing race exists for the clone
  source. Only the edit sibling defines the behaviour and the error code. A clone implementer
  could return a 500, a 422 or an empty copy, which would diverge from `skill_not_found`.
- **Question (if a person must decide):** None. Reuse the sibling's resolution rule and error.
- **Proposed change:**
  - BSB-20-PENDING-1: add a scenario in which `{"kind":"clone","source":"sdlc-fix-bug-recheck","name":"sdlc-fix-bug-retry"}`
    at `main` head `4f3c2b1a…` returns 404 with the `skill_not_found` body naming
    `sdlc-fix-bug-recheck`, and creates no branch and no `builds` row. Add a Notes line saying the
    source folder is resolved from the current `main` head immediately before branching, the same
    as BSB-20-PENDING-2.
  - BSB-20-PENDING-2: change the contract-table row label from "Edit skill name does not exist…"
    to cover both an edit skill and a clone source.

### Finding 6 — Cross-story consistency: the edit-open commit's content is unstated in PENDING-2 but assumed empty by PENDING-3
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-2, BSB-20-PENDING-3
- **Evidence:**
  - BSB-20-PENDING-2: the open creates exactly one commit on top of `main`
    (`rev-list --count … = 1`), and only the skill folder's tree id is asserted to equal `main`'s.
  - BSB-20-PENDING-3 Givens for the first two scenarios: "no save has been made on that branch,
    so `git diff --name-only 4f3c2b1a… origin/build/sdlc-fix-bug-triage` is empty". That is only
    true if the edit-open commit changes no path anywhere in the repository.
- **What is missing/ambiguous/contradictory:** A PENDING-2 implementation whose open commit writes
  something outside the skill folder satisfies every PENDING-2 AC. A build-metadata file is one
  plausible example. That same implementation would break PENDING-3's precondition and its
  "returns exactly `skills/sdlc-fix-bug-triage/SKILL.md`" assertion.
- **Question (if a person must decide):** None.
- **Proposed change:**
  - BSB-20-PENDING-2: add to the first scenario "And
    `git diff --name-only 4f3c2b1a… origin/build/sdlc-fix-bug-triage` is empty (the edit-open
    commit changes no files)". Add a Notes line saying the open commit is empty.
  - BSB-20-PENDING-3: change the Givens to cite that PENDING-2 guarantee ("the edit build was
    opened by BSB-20-PENDING-2, whose open commit changes no files").

### Finding 7 — Dependency-note sanity: PENDING-3's in-epic and session dependencies are unstated
- **Severity:** Advisory
- **Stories touched:** BSB-20-PENDING-3, BSB-20-PENDING-2
- **Evidence:**
  - BSB-20-PENDING-3 Notes: "The target folder is fixed when the edit build is opened (story
    BSB-20-PENDING-2)". This is stated as a fact, not as a dependency. The story's Givens need an
    open edit build and "a valid member session with local `users.id` = `42`", but its Notes list
    only BSB-21.
  - BSB-20-PENDING-2 Notes do not name BSB-20-PENDING-3 as a consumer. Both siblings
    (PENDING-1, PENDING-2) explicitly list "Depends on epic BSB-18 for the member session".
- **What is missing/ambiguous/contradictory:** PENDING-3 has an in-epic prerequisite (PENDING-2)
  and a cross-epic prerequisite (BSB-18) that its own dependency notes leave out.
  `sdlc-plan-epic-sequence` reads these notes.
- **Question (if a person must decide):** None.
- **Proposed change:**
  - BSB-20-PENDING-3: add "Depends on BSB-20-PENDING-2 for the edit build and its recorded target
    folder, and on epic BSB-18 for the member session and local `users.id` = `42`."
  - BSB-20-PENDING-2: add "Prerequisite for BSB-20-PENDING-3."

## Open questions

1. **Finding 1(a):** Does FR-016's "open build" mean `state` = `open` only, or every state with a
   live branch (`open` and `submitted`)? Does it apply to clone and edit builds as well as create
   builds, and which epic owns it? (BSB-19 currently scopes it to create builds only.)
2. **Finding 1(b):** When `build/<skill>` already exists on origin for a `merged` or `abandoned`
   build (or was left over from outside the builder), should a new clone or edit build be
   rejected with a named error, or should the stale branch be reset? If reset, does BSB-36 or
   BSB-20 own that?
3. **Finding 2:** Who owns the save-path confinement rule and the
   `PUT /api/builds/{id}/files/{path}` contract? Option (a): BSB-21, for every build kind, with
   PENDING-3 reduced to the edit build's target folder. Option (b): BSB-20-PENDING-3, sequenced
   after BSB-21's save story, with a kind-neutral error.

## Proposed changes

`docs/product/epics/BSB-20/_epic/stories.md`, to be applied by `sdlc-plan-stories-write` (revise):

- **Shared contract table:**
  - Separate BSB-19-owned rows (`skill_name_exists`, `skill_name_invalid`) from BSB-20-owned rows
    (Finding 3).
  - Change the `skill_name_invalid` message to the FR-017 `sdlc-<area>-<action>` pattern
    (Finding 3).
  - Widen the `skill_not_found` row to cover the clone source (Finding 5).
  - Make the `file_outside_skill_folder` message kind-neutral (Finding 2).
  - Add per-kind request bodies with one field name for the build's skill (Finding 4).
  - Add the collision error row agreed under Open questions 1–2 (Finding 1).
- **BSB-20-PENDING-1:**
  - Collision rejection scenario and FR-016 ownership note (Finding 1).
  - Confinement-owner note, and a note that the source-unchanged scenario's commit is a direct git
    commit (Finding 2).
  - Name-rule rows marked as BSB-19's response (Finding 3).
  - Request field renamed (Finding 4).
  - New `skill_not_found` scenario for a missing clone source, plus a resolution note
    (Finding 5).
- **BSB-20-PENDING-2:**
  - Collision rejection scenario for the `edit` kind, and the FR-016 Notes line corrected
    (Finding 1).
  - Note that its recorded target folder is what save confinement uses (Finding 2).
  - Request field aligned (Finding 4).
  - New "edit-open commit changes no files" AC and note (Finding 6).
  - "Prerequisite for BSB-20-PENDING-3" note (Finding 7).
- **BSB-20-PENDING-3:**
  - Givens state `state` = `open` (Finding 1).
  - Kind-neutral 403 message; explicit "cannot be accepted before BSB-21's save story" note; and,
    under option (a), the PUT contract assertions replaced by references to BSB-21 (Finding 2).
  - Givens cite PENDING-2's empty open commit (Finding 6).
  - Dependencies on BSB-20-PENDING-2 and BSB-18 added (Finding 7).
- `story-map.json`: no requirement-ID change is expected. Update it only if the Finding 2 answer
  moves FR-125's save-path part to BSB-21; that would be an `epic-map.json` change, which is
  out of this report's scope.

## Architecture impact
None. Every finding fits within SK-001 as written: the `build/<skill-name>` branch naming, the
`builds.kind` and `builds.state` columns, and the split of save and commit behaviour into FA-3.
The answers to the open questions decide ownership and behaviour inside that design. If the
person answering Open question 2 instead wants a different build-branch naming scheme (for
example a per-build suffix), that would change SK-001 §1a, and this review should be re-run
after that design change lands.

## Requirement coverage check
**Yes, with one caveat.**
- Every FR mapped to BSB-20 is exercised by at least one story's acceptance criteria:
  - FR-011 to FR-014: BSB-20-PENDING-1, through the clone, folder-copy, frontmatter-rewrite and
    source-unchanged scenarios.
  - FR-124 and FR-126: BSB-20-PENDING-2, through the open, cut-from-current-main and two 404
    scenarios.
  - FR-125: BSB-20-PENDING-3.
- No FR is claimed by two stories, and no story claims an FR outside the epic. The FR wording in
  `epic-map.json`, `epics.md` and the stories matches the current `PRD.md` rows. BSB-20 has no
  NFRs mapped. The epic-wide NFRs that touch these surfaces are owned elsewhere: the session gate
  is BSB-18's middleware, and accessibility and reflow are BSB-38's. No silent-NFR gap was found.
- **Caveat:** FR-125's coverage depends on BSB-21's save endpoint (Finding 2). Until its owner is
  settled, FR-125 is covered by ACs that cannot be run inside this epic.
- FR-015 to FR-017 are exercised but not claimed by PENDING-1, which is correct. Finding 3
  corrects how their error text is asserted.

## Dependency-note sanity check
**No, there are mismatches (Findings 1, 2 and 7).**
- Every story key or epic named in a dependency note exists (BSB-18, BSB-19, BSB-21, BSB-36 and
  BSB-20-PENDING-2).
- Mismatches:
  1. PENDING-1 and PENDING-2 both defer FR-016 to BSB-19, but BSB-19's scope covers create builds
     only (Finding 1).
  2. BSB-20 says it depends on BSB-21 for saves, and BSB-21 says it depends on BSB-20 for builds
     (Finding 2). This is a two-way epic-level dependency. Story-level notes need to make it
     resolvable.
  3. PENDING-3 relies on PENDING-2 and BSB-18 without saying so, and PENDING-2 does not name
     PENDING-3 (Finding 7).
- Build order is left to `sdlc-plan-epic-sequence`. This pass only flags the note mismatches.

---
*Next: `sdlc-plan-stories-write` (revise) applies the proposed changes once Open questions 1–3 are
answered. Then re-run this review, and then `sdlc-plan-epic-sequence`. No Jira issue, story file
or map was changed by this review.*
