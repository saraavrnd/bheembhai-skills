# Epic Review — BSB-22: Test projects & membership

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-15 · **Stories reviewed:** BSB-22-PENDING-1, BSB-22-PENDING-2, BSB-22-PENDING-3, BSB-22-PENDING-4, BSB-22-PENDING-5

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-22/_epic/epic-review.md`.

## Context loaded

- **Target resolution.** The run's target was `SkillBuilder`. That is the product title of
  `docs/product/PRD.md`, not a Jira issue; PRD §8 and the BSB-22 `stories.md` header both say so.
  The Atlassian MCP server was not connected in this session, so the epic was resolved from disk.
  BSB-22 is the epic the most recent `sdlc-plan-stories-write` run wrote (commit `70c9c1b`), and it
  has no review yet. Nothing was read from or written to Jira.
- **All 5 BSB-22 stories**, from `docs/product/epics/BSB-22/_epic/stories.md` and `story-map.json`,
  which is the full set: PENDING-1 (create project / owner), PENDING-2 (add member), PENDING-3
  (remove member), PENDING-4 (membership authorizes run start) and PENDING-5 (owner-only
  integration changes). Also read the shared "Project and membership contract" preamble: the
  fixtures, routes, error table, authorization order and membership-evidence boundary.
- `docs/product/epic-map.json`: BSB-22 → FR-023, FR-024, FR-025, FR-026, FR-027, FR-028.
- `docs/product/PRD.md`: §2 target users ("Test-project owner"), §4 scope, the FA-4 rows FR-023 to
  FR-028, the neighbouring rows FR-029 to FR-037, FR-055 to FR-057, FR-092, FR-093, FR-116 to
  FR-118, FR-130 to FR-137, FR-141, FR-145 to FR-150 and FR-163, NFR-002, NFR-003 and NFR-012, and
  §8 "LLM-scan model", "Access model" and "LLM-scan model setting".
- `docs/product/epics.md`: the BSB-22 section (description, edge cases, implementation order, DoD).
  Also read far enough to check cross-epic ownership: BSB-18, BSB-23, BSB-24, BSB-27 (FR-055 to
  FR-057), BSB-31/BSB-32 (FR-092, FR-093, FR-163), BSB-37 (CLI) and BSB-38 (accessibility).
- `docs/adr/SK-001-skill-builder.md`: §1 (server-rendered web app: "login, projects, runs,
  results"), §3 (Cognito group, local `users` table), §4 (projects, integrations, "Only the owner
  can change integrations"), §6b (LLM check: "only the project owner changes the default"), §7
  (the CLI runs the runner without the web app) and §9 (`projects`, `project_members`,
  `integrations`, `runs`). The repo has no separate `architecture.md`, `data-model.md`,
  `api-contracts/` or `ui-conventions.md`; SK-001 §9 is the data model.
- **Cross-epic checks.** BSB-18's `stories.md` was read for the session fixture, the gate order
  (401 `authentication_required`, 403 `not_a_member`), the `/projects/1/settings` page route and
  BSB-18-PENDING-4's local-user notes. BSB-23, BSB-24, BSB-27, BSB-31, BSB-32, BSB-37 and BSB-38
  are not decomposed into stories yet, so their `epics.md` scope is the reference. No
  `sdlc-plan-epic-sequence` output exists yet for any epic.

## Findings

### Finding 1 — Cross-epic architecture fit: PENDING-4 and PENDING-5 accept on behaviour owned by BSB-24 and BSB-23, which in turn depend on BSB-22
- **Severity:** Blocking
- **Stories touched:** BSB-22-PENDING-4, BSB-22-PENDING-5 (and the contract preamble's "Run-start
  route (owned by BSB-24)" / "Integration route (owned by BSB-23)" rows), across the epic boundary
  with BSB-24 and BSB-23.
- **Evidence:**
  - PENDING-4, scenarios "The project owner … starts a run" and "A plain member starts a run",
    assert HTTP 201 and a `runs` row with `skill`, `skills_ref` and `input_branch` from the body
    `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main"}`.
    PENDING-4's Notes: "**Cannot be accepted before epic BSB-24's run-start story (FR-037) is
    delivered.** BSB-24 owns `POST /api/projects/{project_id}/runs`, the run request and response
    contract, and the `runs` row's other columns."
  - PENDING-5, scenario "The owner changes the project's Jira integration", asserts HTTP 200 and a
    rewritten `integrations.config`. Its Notes say it "Cannot be accepted before epic BSB-23's
    integration-settings story (FR-029 to FR-036) is delivered."
  - `epics.md` BSB-24 Notes: "Depends on FA-4 for membership". BSB-23 Notes: "Depends on FA-4 for
    project ownership". The stories.md preamble itself says "The dependency is two-way".
  - `epics.md` BSB-24 scope makes the run request carry workflow/step context, model profile and
    model tier (FR-147, FR-149, FR-150), with "every choice being required where applicable".
    BSB-27 refuses a start whose static scan did not pass (FR-055).
- **What is contradictory:** each pair of acceptance criteria needs the other epic to land first,
  so BSB-22 cannot meet its own DoD ("members can start a run in the project … only the owner can
  change the project's integrations") until BSB-23 and BSB-24 are done. Those epics in turn wait
  on BSB-22. Two things follow. First, PENDING-4's 201 success scenarios specify part of BSB-24's
  contract: a three-field run request that admits a run with no model profile, tier, workflow
  context or passing static scan. Once BSB-24 and BSB-27 land, the same request will be refused
  (422, or the FR-055 refusal), and the BSB-22 scenarios will fail even though the membership
  logic is correct. Second, an implementer picking up PENDING-4 must build some form of the
  run-start route to make the scenarios pass. That is the "two implementers build the same thing
  two ways" case. PENDING-5 has the same problem against BSB-23, to a smaller degree.
- **Question (a person must decide):** How should the membership/owner checks be split from the
  routes they protect? Options:
  - (a) Re-scope PENDING-4 and PENDING-5 to deliver the reusable project-authorization guard
    (`require_project_member`, `require_project_owner`) with its refusal contract (404/403 bodies,
    zero side effects). Their acceptance would be scenarios the guard can pass alone, for example
    a project-scoped route this epic already owns, or the guard applied to the member routes. The
    201/200 success-path assertions would move to BSB-24 (FR-037) and BSB-23 (FR-029 to FR-031),
    which then cite the guard.
  - (b) Move PENDING-4 into BSB-24 and PENDING-5 into BSB-23, so each route and its authorization
    ship together.
  - (c) Keep both as written and accept that BSB-22 closes only after BSB-23 and BSB-24.
- **Proposed change:** under (a), which is recommended because it removes the cycle without moving
  requirements between epics:
  - BSB-22-PENDING-4: replace the two 201 scenarios with a guard-level admitted scenario that
    asserts the request passes authorization, with no claim on status or `runs` columns beyond
    "authorization did not refuse". Alternatively, make the 201 scenarios explicit BSB-24
    acceptance hooks under Notes rather than BSB-22 ACs. Keep the three refusal scenarios
    (non-member, removed member, missing project). Drop the minimal run body from the shared
    fixture table, or mark it "placeholder until BSB-24 fixes the request".
  - BSB-22-PENDING-5: same change. Keep the three 403 scenarios and move the 200 "owner changes
    config" assertion to a BSB-23 acceptance hook.
  - Both stories: replace "Cannot be accepted before epic BSB-2x…" with "Provides the guard BSB-2x
    applies to its route; BSB-2x's run-start/integration story must cite it."
  - Under (b) or (c), `sdlc-plan-stories-write` (revise) applies the matching move or adds an
    explicit "BSB-22 closes after BSB-23 and BSB-24" note.

### Finding 2 — Epic-wide scope boundary: no story owns the web surfaces or the read side of projects and membership
- **Severity:** Blocking
- **Stories touched:** BSB-22-PENDING-1, BSB-22-PENDING-2, BSB-22-PENDING-3 (and PENDING-4/PENDING-5
  for project discovery).
- **Evidence:**
  - Every scenario in all five stories is a JSON API call (`POST /api/projects`,
    `POST|DELETE /api/projects/{id}/members…`). No story has a page, form or listing scenario, and
    no `GET` route for projects or members exists anywhere in the contract table.
  - BSB-22-PENDING-2 Notes: "The add form lists the local `users` rows the FA-1 gate created and
    submits the chosen `users.id`". That form, and the user listing it needs, appear in no story's
    acceptance criteria or out-of-scope list.
  - BSB-18-PENDING-1 pins `/projects/1/settings` as an authoring page route that the gate protects,
    so a project settings page is assumed to exist.
  - SK-001 §1 describes the web app as "login, projects, runs, results", server-rendered HTML (§1
    Stack). BSB-37 Non-goals: "no CLI administration of users, groups or projects", so the web is
    the only human surface for FR-023 to FR-026.
  - BSB-38 (FR-130 to FR-137, NFR-012) "constrains the presentation of features delivered
    elsewhere". It needs these surfaces to exist in some epic.
- **What is missing:** the union of the five out-of-scope lists never mentions a projects list, a
  create-project page, a project page or settings page, a member list, the add-member picker or
  the remove control. It also never says another epic owns them, and no other epic's scope claims
  them. Nothing lets an author learn which projects they belong to. PENDING-4/PENDING-5's callers
  (BSB-24's run form, BSB-23's settings page) both need "projects I am a member of / own", and no
  story provides that read. The add-member picker also raises a product decision no document
  answers: it would show every local user's name and email to any project owner.
- **Question (a person must decide):** (1) Are the project and membership web pages (list, create,
  settings/members view with add and remove) and the read endpoints in BSB-22's scope as new
  stories, or owned by a named other epic? (2) May any project owner see the full list of local
  `users` (name and email) to pick a member, or must the picker take an exact email address
  instead?
- **Proposed change:** assuming (1) "in BSB-22", which is recommended because FR-023 to FR-026 are
  user-facing capabilities and no other epic claims the surface:
  - Add one or two new stories: "Author sees and creates projects in the web app" (projects list
    filtered to the caller's memberships, create form, `GET /api/projects`) and "Owner manages
    members on the project page" (member list, add picker per answer (2), remove control,
    `GET /api/projects/{id}/members`), with the same authorization order as the existing contract.
  - BSB-22-PENDING-1: add "the create-project page (new story)" to Out of scope.
  - BSB-22-PENDING-2 and BSB-22-PENDING-3: add "the member management page (new story)" to Out of
    scope. In PENDING-2, reword "The add form lists…" to point at the new story instead of implying
    this story builds it.
  - BSB-22-PENDING-4 and BSB-22-PENDING-5: add a note that BSB-24's run form and BSB-23's settings
    page read the caller's projects from the new list route.
  - If (1) is answered "another epic", each of PENDING-1, PENDING-2 and PENDING-3 instead names that
    epic in Out of scope, and PENDING-2's "add form" note is removed.

### Finding 3 — Epic-wide scope boundary: the epic's "not a current skill-builder must fail" edge case is narrowed by PENDING-2 to "never admitted"
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-2, BSB-22-PENDING-4 (relies on the run-time refusal), and the
  epic's own edge case.
- **Evidence:** `epics.md` BSB-22 Functional scope: "adding a user who is not a current
  skill-builder must fail through the FA-1 gate." BSB-22-PENDING-2 Notes ("Boundary for review"):
  a former group member who still has a `users` row "cannot [be rejected] at add time". The
  scenario "Adding a user the FA-1 gate never admitted is refused" covers only the never-admitted
  case. The stories.md preamble ("Membership evidence") explicitly flags this for the next review.
  BSB-18-PENDING-4 Notes confirm that a `users` row "does not record current `skill-builders`
  membership".
- **What is ambiguous:** the stories deliver a narrower guarantee than the epic states. It is safe
  to build as written: the former member's own requests are refused per request by BSB-18 (FR-004,
  FR-141), so the row grants nothing, and PENDING-4's run check never admits them past the BSB-18
  gate. But a person has to accept the narrowing. The alternative, rejecting former members at add
  time, needs a Cognito directory read (AdminListGroupsForUser-style IAM permission). SK-001 §3
  does not provide one, so that answer would have to go back to the architecture owner before any
  story change.
- **Question (a person must decide):** Do you accept "has a local `users` row" (admitted at least
  once) as the add-time meaning of "a current skill-builder", relying on BSB-18's per-request gate
  to neutralize former members? Or must add-time rejection cover former members too?
- **Proposed change:** if accepted (recommended), BSB-22-PENDING-2: move the "Boundary for review"
  bullet to a settled note: "Decision (epic review 2026-11-15): add-time check is 'has a local
  `users` row'; former members are neutralized by BSB-18's per-request gate." Add an Out-of-scope
  line: "rejecting a former group member at add time (needs a Cognito directory read)".
  BSB-22-PENDING-4: add one line to Notes that a former group member who still holds a
  `project_members` row is refused by BSB-18's gate before this check runs. No other story
  changes.

### Finding 4 — Epic-wide scope boundary: the owner-only rule for the project's LLM-scan default model has no owner
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-5 (and the epic boundary with BSB-23 and BSB-32).
- **Evidence:** BSB-22-PENDING-5 Out of scope: "the LLM-scan model setting (FR-163)", with no
  owning epic named. PRD §8 "LLM-scan model": "configured per test project … Only the project owner
  changes it". SK-001 §6b: "only the project owner changes the default". BSB-32 covers FR-163 as
  *using* the configured profile. BSB-23 covers configuring model profiles (FR-031) but not the
  per-project default selection. Neither epic's scope states the owner-only rule.
- **What is missing:** a PRD-stated authorization rule that no story's acceptance criteria and no
  other epic's scope carries. Unless PENDING-5's guard is explicitly extended to it, it would be
  built with member-level access.
- **Question (a person must decide):** Is the project's LLM-scan default model an integration
  setting, so FR-028 and PENDING-5's owner check cover it? Or is it a separate project setting
  whose owner check belongs to BSB-23 or BSB-32?
- **Proposed change:** if it is an integration setting (recommended, because SK-001 §6b places the
  choice among the project's **AI models** profiles of §4): in BSB-22-PENDING-5, change the
  Out-of-scope entry to "the LLM-scan model setting's schema (BSB-23/BSB-32)". Add to Notes:
  "FR-028's owner check also covers changing the project's LLM-scan default model (PRD §8,
  FR-163); whichever route BSB-23/BSB-32 define for it must apply `project_owner_required`." If the
  answer is "separate setting", PENDING-5's Out of scope names the owning epic instead.

### Finding 5 — Cross-epic architecture fit: the membership check is pinned to one HTTP route while other run- and scan-start paths are unnamed
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-4, BSB-22-PENDING-3 (its "takes effect on the target's next
  request" claim relies on PENDING-4 covering every start path).
- **Evidence:** BSB-22-PENDING-4 Notes: "Membership is read from the durable `project_members`
  table on every request". They name only `POST /api/projects/{project_id}/runs` and the scan
  reuse by BSB-31/BSB-32 (FR-092, FR-093). Other paths also start a run or scan: re-runs (FR-056)
  and output chaining (FR-057) in BSB-27, and CLI run/scan (FR-116 to FR-118) in BSB-37, whose edge
  cases demand "the same project membership check". SK-001 §7 says the CLI "runs the same runner
  without the web app", so an HTTP-route-only check would not cover it. BSB-22-PENDING-3 Notes:
  "Removal takes effect on the target's next request because BSB-22-PENDING-4 reads
  `project_members` on every run start."
- **What is missing:** PENDING-3's guarantee holds only if every start path applies PENDING-4's
  check. PENDING-4 does not say so, and does not say where the check lives (route vs run-start
  service) for paths that bypass the HTTP API.
- **Proposed change:** BSB-22-PENDING-4 Notes: extend the reuse bullet to "Every path that starts
  a run or a scan for a project applies this same check, including re-run and output chaining
  (BSB-27, FR-056, FR-057), scans (BSB-31/BSB-32, FR-092, FR-093) and the CLI (BSB-37, FR-116 to
  FR-118). The check therefore belongs in the run/scan start service, not only in the HTTP route."
  BSB-22-PENDING-3 Notes: change "because BSB-22-PENDING-4 reads `project_members` on every run
  start" to "… on every run or scan start, on every path listed in BSB-22-PENDING-4".

### Finding 6 — Cross-story consistency: the fixed authorization order omits BSB-18's group check and the place of body validation
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-2, BSB-22-PENDING-3, BSB-22-PENDING-4, BSB-22-PENDING-5 (all
  inherit the preamble's "Authorization order on every project-scoped route is fixed").
- **Evidence:** the preamble orders 401 `authentication_required` → 404 `project_not_found` → 403
  `project_membership_required` → 403 `project_owner_required`. BSB-18-PENDING-3 returns 403
  `{"error":{"code":"not_a_member",…}}` for a signed-in user outside `skill-builders`. That step
  sits between 401 and 404 and is absent from the BSB-22 order. The order is also silent about
  where body validation falls. Examples: a non-owner member sending `{}` to
  `POST /api/projects/7/members` (PENDING-2's `user_id_required`), or a non-member sending an
  invalid integration body (PENDING-5). Each story's implementer could place 422 before or after
  the 403s.
- **What is ambiguous:** the order is declared "fixed" for four stories at once but is incomplete
  in two places. The result is two observable responses (403 vs 422) depending on who builds which
  route.
- **Proposed change:** contract preamble, applied once and inherited identically by PENDING-2,
  PENDING-3, PENDING-4 and PENDING-5: state the order as "401 `authentication_required` → 403
  `not_a_member` (BSB-18) → 404 `project_not_found` → 403 `project_membership_required` → 403
  `project_owner_required` where required → 422 request-body validation". Add one scenario to
  PENDING-2: a non-owner member sends `{}`, and the expected result is 403 `project_owner_required`,
  not 422.

### Finding 7 — Cross-story actor & role consistency: two owner records, no stated source of truth for the owner check
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-1, BSB-22-PENDING-2, BSB-22-PENDING-3, BSB-22-PENDING-5 (and
  BSB-22-PENDING-4's "no separate owner bypass" note).
- **Evidence:** PENDING-1 writes the owner twice: `projects.owner_id` and a `project_members` row
  with `role` = `owner`. PENDING-2, PENDING-3 and PENDING-5 each enforce "owner only" but none says
  which record the check reads. PENDING-3's owner-removal refusal compares the target with "the
  owner's own membership row", and its scenario also asserts `projects.owner_id`. SK-001 §9 has
  both columns and no constraint that keeps them equal or allows exactly one `owner` row per
  project.
- **What is ambiguous:** the two records cannot diverge through any MVP story (no transfer, owner
  removal refused). But three separate owner checks may read different records, and nothing
  prevents a second `role = owner` row, for example from a seed script or a later epic.
- **Proposed change:** stories.md preamble, inherited by PENDING-2, PENDING-3 and PENDING-5: "The
  owner check reads `project_members.role = 'owner'` for the caller; `projects.owner_id` is the
  denormalized creator record and must equal it." Or name the opposite source, but the same
  sentence for all three stories. BSB-22-PENDING-1 Notes: add "at most one `owner` row per project
  (partial unique index on `project_members(project_id) WHERE role = 'owner'`)", or state it as an
  invariant for `sdlc-deliver-story-design` to enforce.

### Finding 8 — Dependency-note sanity: PENDING-5 uses PENDING-2's member row without the dependency PENDING-4 declares for the same row
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-2, BSB-22-PENDING-4, BSB-22-PENDING-5.
- **Evidence:** BSB-22-PENDING-4 Notes: "Depends on … BSB-22-PENDING-2 for member rows". BSB-22-
  PENDING-5's scenario "A member who is not the owner cannot change an integration" uses Grace's
  `7 | 43 | member` row in the same way, but its Notes list only "BSB-22-PENDING-1 … and … epic
  BSB-18". BSB-22-PENDING-2's forward note ("BSB-22-PENDING-3 removes the rows this story creates,
  and BSB-22-PENDING-4 reads them") also omits PENDING-5.
- **What is inconsistent:** a one-sided dependency claim. Read alone, PENDING-5 looks independent
  of PENDING-2, but its member-vs-owner distinction only means something once member rows exist.
- **Proposed change:** BSB-22-PENDING-5 Notes: "Depends on BSB-22-PENDING-2 for the `member` role
  rows its non-owner scenario exercises." BSB-22-PENDING-2 Notes: extend the forward note to "…
  BSB-22-PENDING-4 reads them to authorize a run start, and BSB-22-PENDING-5 distinguishes them
  from the owner." This does not compute a build order; that stays `sdlc-plan-epic-sequence`'s job.

## Open questions

1. **(Finding 1)** How are the run-start and integration authorization checks split from the
   routes they protect? (a) Re-scope PENDING-4/PENDING-5 to a reusable guard and move the 201/200
   success assertions to BSB-24/BSB-23 (recommended); (b) move the two stories into BSB-24 and
   BSB-23; or (c) keep them and accept that BSB-22 closes only after BSB-23 and BSB-24.
2. **(Finding 2)** Are the project and membership web pages (list, create, project settings,
   member list with add and remove) and their read endpoints in BSB-22 as new stories, or owned by
   a named other epic?
3. **(Finding 2)** May any project owner see every local user's name and email to pick a member,
   or must the add-member picker take an exact email address instead?
4. **(Finding 3)** Is "has a local `users` row" the accepted add-time meaning of "a current
   skill-builder", with former group members neutralized by BSB-18's per-request gate? Or must
   add-time rejection cover former members (which needs a Cognito directory read the current
   design does not include)?
5. **(Finding 4)** Is the project's LLM-scan default model an integration setting covered by
   FR-028 / PENDING-5's owner check, or a separate project setting whose owner check belongs to
   BSB-23 or BSB-32?

## Proposed changes

`docs/product/epics/BSB-22/_epic/stories.md`. For `sdlc-plan-stories-write` (revise) to apply after
the open questions are answered; nothing here is applied.

- **Contract preamble** (inherited by PENDING-2 to PENDING-5):
  - Complete the authorization order with BSB-18's 403 `not_a_member` and a final 422 body
    validation step (Finding 6).
  - Name the source of truth for the owner check (Finding 7).
  - Mark or drop the minimal run body in the fixture table per Q1 (Finding 1).
  - Mark the membership-evidence paragraph as decided per Q4 (Finding 3).
- **New story / stories** (per Q2/Q3): the projects list and create page with `GET /api/projects`,
  and the member management page with `GET /api/projects/{id}/members`, the add picker and the
  remove control (Finding 2).
- **BSB-22-PENDING-1:**
  - Out of scope: name the create-project page's owner (Finding 2).
  - Notes: the at-most-one-owner invariant (Finding 7).
- **BSB-22-PENDING-2:**
  - Notes: re-point the "add form" note to the owning story (Finding 2), and settle the "Boundary
    for review" bullet per Q4 (Finding 3).
  - Extend the forward note to PENDING-5 (Finding 8).
  - Out of scope: the member page's owner (Finding 2), and rejection of former members at add time
    if Q4 is accepted (Finding 3).
  - AC: add the non-owner-with-invalid-body → 403 scenario (Finding 6).
- **BSB-22-PENDING-3:**
  - Out of scope: the member page's owner (Finding 2).
  - Notes: "every run or scan start, on every path listed in PENDING-4" (Finding 5).
- **BSB-22-PENDING-4:**
  - AC and Notes re-scoped per Q1: the guard-level admitted scenario replaces the two 201
    scenarios, and "Cannot be accepted before BSB-24" becomes "BSB-24 cites this guard"
    (Finding 1).
  - Notes: the list of run/scan start paths and the service-layer placement of the check
    (Finding 5); the former-member line (Finding 3); "BSB-24's run form reads the caller's
    projects from the new list route" (Finding 2).
- **BSB-22-PENDING-5:**
  - AC and Notes re-scoped per Q1: the 200 success scenario moves to a BSB-23 hook, and "Cannot
    be accepted before BSB-23" becomes "BSB-23 cites this guard" (Finding 1).
  - Out of scope and Notes for the LLM-scan default model per Q5 (Finding 4).
  - Notes: depends on PENDING-2 (Finding 8); "BSB-23's settings page reads the caller's projects
    from the new list route" (Finding 2).

## Architecture impact

None. Every finding is resolved by a story change or a scope decision. Nothing needs an entity,
column, endpoint or integration beyond SK-001 §4 and §9: the read routes in Finding 2 and the
guard in Finding 1 are API additions over the existing `projects` and `project_members` tables.
The only path that would need a design change is the non-recommended answer to Q4 (a Cognito
directory read). That is recorded in Finding 3 as a consequence of that answer, not as a current
conflict.

## Requirement coverage check

Yes, with notes.
- FR-023 (PENDING-1), FR-024 (PENDING-1), FR-025 (PENDING-2), FR-026 (PENDING-3), FR-027
  (PENDING-4) and FR-028 (PENDING-5) are each exercised by at least one acceptance scenario.
- No FR is claimed by two stories, so there are no contradicting claims.
- The `epic-map.json` IDs match the current `PRD.md` wording for FR-023 to FR-028, and the stories'
  covered-requirement lists match `story-map.json`.
- Notes:
  - FR-027's and FR-028's success halves currently depend on BSB-24/BSB-23 behaviour (Finding 1).
  - FR-023 to FR-026 are covered at the API level only, with no surface a human can use
    (Finding 2).
  - FR-025's "skill-builder user" is interpreted narrower than the epic's edge case (Finding 3).
  - The PRD's owner-only rule for the LLM-scan default (§8, FR-163) is carried by no story
    (Finding 4).

## Dependency-note sanity check

Mostly yes. Every in-epic dependency note names a real BSB-22 story, and every cross-epic note
names a real epic (BSB-18, BSB-23, BSB-24, BSB-31, BSB-32). Specific checks:
- PENDING-1's "prerequisite for BSB-22-PENDING-2 to BSB-22-PENDING-5" is reciprocated by all four.
- PENDING-3's dependency on PENDING-2 is reciprocated by PENDING-2's forward note.
- PENDING-4's dependencies on PENDING-2 and PENDING-3 are reciprocated.

Mismatches:
- PENDING-5 relies on PENDING-2's member rows without declaring it, and PENDING-2's forward note
  omits PENDING-5 (Finding 8).
- PENDING-4/PENDING-5 ↔ BSB-24/BSB-23 form a two-way acceptance dependency (Finding 1). Q1 should
  resolve it before `sdlc-plan-epic-sequence` runs.
- PENDING-4 does not name BSB-27 or BSB-37 as consumers of its check (Finding 5).

Build order itself is left to `sdlc-plan-epic-sequence`.
