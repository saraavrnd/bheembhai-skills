# Epic Review — BSB-22: Test projects & membership

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-22-PENDING-1, BSB-22-PENDING-2, BSB-22-PENDING-3, BSB-22-PENDING-4

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-22/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** `SkillBuilder-2` has no Jira issue on the configured site: a read-only
  `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not exist or you do not
  have permission to see it"). The Atlassian MCP tools were not exposed in this session, so the
  same site's REST API was queried read-only (no Jira writes). `PRD.md` §8 and `epics.md`'s source
  note record the same result and ground the product in ADR SK-001.
- **The epic in this run is BSB-22.** `GET /rest/api/3/issue/BSB-22` returned HTTP 200: Epic
  "Test projects & membership", status To Do, labels `FA-4`/`MVP`, no parent and no sub-tasks,
  with a description, functional scope, dependency order, Definition of Done and covered
  requirements matching `epics.md`; `epic-map.json` records it under FA-4/MVP. The run context
  (`ITEM`) binds this step to `BSB-22`.
- **All 4 stories in BSB-22**, from `stories.md` and `story-map.json` in one read each —
  BSB-22-PENDING-1, -2, -3 and -4 (full set, not a sample).
- **`epic-map.json`** — BSB-22 maps FR-023, FR-024, FR-025, FR-026, FR-027 and FR-028, and no NFR.
- **`PRD.md`** — §2 target users (including the catalog reviewer), §5 FA-4, §6 the six FR rows,
  §7 the NFR rows, §8's source note and the project/membership vocabulary.
- **`epics.md`** — the BSB-22 section (description, functional scope, implementation guidance,
  DoD, covered requirements, Notes), the foreach dependency order, and the sections of the epics
  that consume BSB-22's checks or own surfaces its stories touch: BSB-18 (access and the
  per-request middleware), BSB-23 (integrations and the owner-only integration guard), BSB-24
  (run start), BSB-31 (static scans), BSB-32 (LLM scans), BSB-33 (run report), BSB-36 (catalog
  submission), BSB-37 (command line) and BSB-38 (accessibility).
- **`docs/adr/SK-001-skill-builder.md`** — §3 (Cognito app client, the `skill-builders` group,
  per-request claim check, no user admin API), §4 (test project: creator is owner, members can
  run tests, only the owner changes integrations) and §9 (the `users`, `projects`,
  `project_members` with `role` owner/member, `integrations` and `runs` records).
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md`
  are not committed; the PDLC chain runs `sdlc-arch-design` after planning, so ADR SK-001 is the
  design authority this pass can use. No `epic-sequence.md`/`.json` exists for BSB-22; ordering
  was read only from `epics.md`/`epic-map.json` and is not computed here.
- **Other epic story sets checked:** BSB-18, BSB-19 and BSB-20 have stories on disk; BSB-23,
  BSB-24, BSB-31, BSB-32, BSB-33, BSB-36, BSB-37 and BSB-38 have epic definitions but no stories
  yet. Their epic Notes were read to confirm which dependencies are legitimate and written down.

## Findings

### Finding 1 — Cross-epic access rule: the reports linked from a catalog PR are claimed to use the project-membership check
- **Severity:** Blocking
- **Stories touched:** BSB-22-PENDING-1, BSB-22-PENDING-3 (cross-epic: BSB-31, BSB-32, BSB-33,
  BSB-36)
- **Evidence:**
  - BSB-22-PENDING-1, Notes / dependencies: "This story also defines the shared
    project-membership check the rest of the epic and the later project-scoped epics reuse: the
    signed-in user must have a `project_members` row for the project, otherwise the builder
    responds with HTTP 403 ... **BSB-24, BSB-31, BSB-33 and BSB-37 reuse it.**"
  - BSB-22-PENDING-3, Notes / dependencies: "BSB-24 must apply the same check before returning
    any selection data or creating a run (FR-037); **BSB-31's standalone scans, BSB-33's reports
    and BSB-37's command line reuse it.**"
  - `PRD.md` §2 target users: the catalog reviewer "Consumes the catalog pull request and its
    linked run and scan reports; **does not use the authoring interface**."
  - `epics.md` BSB-33 implementation guidance step 6: "Expose a stable report view that catalog
    submission can link to and that **reviewers can read without the authoring interface**."
  - `epics.md` BSB-36 functional scope: "Link the run report and the scan reports from the
    pull-request description." The PR links are the catalog reviewer's only path to that
    evidence.
  - `epics.md` BSB-31 step 5 and BSB-32 step 6 guard the *standalone scan entry point* by project
    membership; neither says the report view linked from the PR is project-member-only.
- **What is missing/ambiguous/contradictory:** The project-membership check as BSB-22 defines it
  returns 403 to any signed-in user without a `project_members` row. BSB-22's reuse lists apply
  that check to "BSB-33's reports" and to BSB-31's scan surface, while BSB-33's own epic promises
  a stable report that catalog reviewers can read without the authoring interface, and BSB-36
  links those reports from the catalog PR. A catalog reviewer is a different user type from a
  test-project member, and neither `PRD.md` §2 nor BSB-33's epic establishes that a reviewer
  holds a `project_members` row for the project whose run is reported. Implemented literally,
  the two epics disagree about the same report URL: BSB-22 gates it, BSB-33 opens it. The same
  question applies to the scan reports BSB-36 links.
- **Question (if a person must decide):** Should the stable run/scan report views linked from a
  catalog pull request be readable outside the builder authoring gate and the project-membership
  check? If yes, what authorizes the reviewer (a signed share link, a separate read-only access
  rule, or a public view), and which of BSB-31/BSB-32/BSB-33 owns it? (also Open question 1)
- **Proposed change:**
  - **BSB-22-PENDING-1:** In Notes, narrow the shared check to "author-facing project surfaces
    and entry points" and state that BSB-33's reviewer-facing stable report (and the BSB-31/32
    report views linked from a catalog PR) use a separate access rule owned by those epics, not
    the project-membership check. Remove BSB-33 from the blanket reuse list (or qualify it as
    "the author-facing run page only").
  - **BSB-22-PENDING-3:** Make the same change to its reuse sentence: keep BSB-24 and BSB-37;
    qualify BSB-31 and drop the unqualified "BSB-33's reports" claim.
  - Same change for both stories: the project-membership check is scoped to author-facing
    surfaces, and the catalog-reviewer evidence path is explicitly someone else's.
  - **Cross-epic (not applied here):** BSB-33 must state how the stable report is accessed
    outside the authoring interface; BSB-31/BSB-32 need the same sentence for their report
    views; BSB-36's link contract then points at those views. If the human decides the reports
    are project-member-only instead, BSB-33's and BSB-36's scope must change, not BSB-22's.

### Finding 2 — Cross-epic route ownership: two acceptance criteria exercise mutation routes their own stories disclaim
- **Severity:** Blocking
- **Stories touched:** BSB-22-PENDING-3, BSB-22-PENDING-4 (cross-epic: BSB-23, BSB-24)
- **Evidence:**
  - BSB-22-PENDING-3, "A signed-in non-member cannot submit a run start": "When Carol submits a
    run start for project 7 on POST `/projects/7/runs` Then the builder responds with HTTP 403
    ... and no `runs` row is created for project 7." Its own Notes: "This story owns the
    run-start entry point ... GET `/projects/7/runs/new` serves the page that BSB-24 completes
    ... **Run creation and input selection are not part of this story**; the `runs` table ...
    is BSB-24's system of record under FR-037."
  - BSB-22-PENDING-4, "A non-owner member cannot change an integration": "When Bob submits a Jira
    integration configuration ... on POST `/projects/7/integrations` Then the builder responds
    with HTTP 403 ... and no `integrations` row is created for project 7." Its Notes: "The
    integration form, its configuration fields, the opaque secret reference and the verification
    step are BSB-23 ...; BSB-23 must call this guard on every integration change route, and
    `POST /projects/7/integrations` is the representative guarded route used by this story's
    acceptance criteria."
  - `epics.md` BSB-24 implementation step 2: "Reuse the project-membership authorization check
    before any selection data is returned," and BSB-24's DoD: "A non-member cannot start a run."
  - `epics.md` BSB-23 implementation step 6: "Enforce owner-only configuration changes using the
    project guard," and BSB-23's Notes: "Depends on the test project and its owner-only
    integration guard from the test-projects epic."
  - `epics.md`'s foreach dependency order lists BSB-22 before BSB-23 and BSB-24. (This report is
    not computing a build order; it is only noting that the two directions point at each other.)
- **What is missing/ambiguous/contradictory:** Each AC requires a mutation endpoint that the same
  story says another epic owns, and no story says who builds the route skeleton or what its
  request contract is. BSB-22-PENDING-3 disclaims run creation while asserting behavior on
  `POST /projects/7/runs`; BSB-22-PENDING-4 says BSB-23 owns the form but calls the route
  "representative" without saying whether BSB-22 creates it. The dependencies run both ways:
  BSB-22's ACs need BSB-23/BSB-24's routes, while BSB-23/BSB-24's own epic notes need BSB-22's
  guards. Two implementers can build the same route differently, or a BSB-22 implementer must
  build another epic's endpoint to make its own AC pass. This is the same shared-endpoint
  contract gap the BSB-20 review flagged as Blocking.
- **Question (if a person must decide):** Should BSB-22 own minimal guarded `POST
  /projects/7/runs` and `POST /projects/7/integrations` routes (with BSB-24/BSB-23 extending them
  with creation fields and input selection), or should those denial ACs move to BSB-24/BSB-23 and
  BSB-22 test the guard only on its own GET pages? If BSB-22 owns them, what is the route's
  request contract and guard order? (also Open question 2)
- **Proposed change:**
  - **BSB-22-PENDING-3:** State the chosen ownership explicitly in Notes. If BSB-22 owns the
    route, say it owns the minimal guarded `POST /projects/7/runs` route — the guard runs before
    any request body is read, a non-member gets the 403 contract, and no `runs` row is created —
    and that BSB-24 completes it with input selection and run creation. If the AC moves, replace
    AC 4 with the guard contract BSB-24 must call and keep only the page-access ACs, and correct
    the "Run creation and input selection are not part of this story" sentence so it no longer
    contradicts an AC.
  - **BSB-22-PENDING-4:** Make the same choice for `POST /projects/7/integrations`; if BSB-22
    owns the guarded route, say so; if not, move AC 3 to BSB-23 and keep the read-only settings
    ACs. Update the "representative guarded route" sentence to name who builds the route
    skeleton.
  - Same change for both stories: one owner per route, one guard order, one denial contract.

### Finding 3 — Cross-story guard ownership: PENDING-2 and PENDING-4 both claim the owner guard
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-2, BSB-22-PENDING-4
- **Evidence:**
  - BSB-22-PENDING-2, Notes / dependencies: "Member management is owner-only: this story
    defines **the shared owner guard every project-administration route uses**." Then: "BSB-23's
    integration configuration routes apply the same owner-only rule, with the message 'Only the
    project owner can change integrations.' BSB-22-PENDING-4 exercises it there."
  - BSB-22-PENDING-4, Notes / dependencies: "Depends on BSB-22-PENDING-2 for the owner guard.
    This story **owns** ... the **owner-only integration-management guard**." Its guard runs
    "two checks in order": membership first, then role `owner`, with the message "Only the
    project owner can change integrations."
  - `epics.md` BSB-22 implementation guidance step 3 ("Add owner-only member add/remove
    operations") and step 5 ("Add the owner-only integration-management guard consumed by the
    integrations epic") treat these as two deliverables; BSB-23's Notes call it "its owner-only
    integration guard."
  - `story-map.json`: PENDING-2's summary says "shared owner guard"; PENDING-4's says "the shared
    owner-only integration guard."
- **What is missing/ambiguous/contradictory:** Two stories each claim to define/own the guard
  used on integration routes, and PENDING-2's "every project-administration route" contradicts
  PENDING-4's ownership. The denial messages differ by resource, so a single guard must be
  parameterised — but neither story says whether there is one guard with a message parameter or
  two guards. A developer reading PENDING-2 alone can apply "Only the project owner can change
  project members." on an integration route and fail PENDING-4's AC.
- **Proposed change:**
  - **BSB-22-PENDING-2:** Narrow "the shared owner guard every project-administration route
    uses" to "the member-management owner guard"; state that BSB-22-PENDING-4 owns the
    integration-management use, and that both call one shared owner check (membership first,
    then `role = "owner"`) parameterised by the resource-specific denial message.
  - **BSB-22-PENDING-4:** State that it uses the same shared owner check rather than a second
    implementation, and that it owns the integration-management message. Keep its two-check
    order.
  - Same change for both stories: one owner check, two documented uses and two messages.

### Finding 4 — Epic-wide scope boundary: no story defines how a user reaches the project surfaces
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-1, BSB-22-PENDING-2, BSB-22-PENDING-4
- **Evidence:**
  - BSB-22-PENDING-1, "A signed-in author creates a project…": the author submits "on the create
    project form at `/projects/new`". Its Notes define `GET /projects` as "the minimal 'Your
    projects' list an author needs to select a project", but no story renders a link to
    `/projects/new` and no AC asserts one.
  - BSB-22-PENDING-1, same scenario: a follow-up `GET /projects/7` renders "Members:
    ada@example.com (owner)", but no story renders an "Add member" or "Settings" link there.
  - BSB-22-PENDING-2: Ada submits the email "on the add-member form at
    `/projects/7/members/new`"; removal is "POST `/projects/7/members/43/delete`" with no page or
    control defined.
  - BSB-22-PENDING-4, "The owner sees the integrations management controls": Ada opens `GET
    /projects/7/settings`; the page renders an "Add integration" link, but no story renders a
    link *to* the settings page.
  - BSB-22-PENDING-1's Out of scope excludes "project discovery beyond the minimal list of
    projects the author belongs to"; no story's Out of scope assigns the missing navigation.
- **What is missing/ambiguous/contradictory:** The four stories define pages and actions that are
  reachable only by typing a URL. The union leaves the journeys disconnected: an author cannot
  reach the create form from the projects list, and an owner cannot reach member management or
  project settings from the project page. No story's acceptance criteria cover these entry
  points and no story's Out of scope admits the hole, so no implementer owns it.
- **Proposed change:**
  - **BSB-22-PENDING-1:** Add ACs (or a Notes contract) that the projects list renders a "New
    project" link to `/projects/new`, and that the project page renders an owner-only "Add
    member" link to `/projects/7/members/new` and a "Settings" link to `/projects/7/settings`.
  - **BSB-22-PENDING-2:** Define where the add-member form and the remove control are reached
    from — e.g. the owner sees "Add member" on the project page and a "Remove" control on each
    non-owner member row posting to `/projects/7/members/<id>/delete`. Add an AC for the
    control.
  - **BSB-22-PENDING-4:** Add an AC or Notes sentence that the settings page is reached from the
    project page, or leave the link to PENDING-1 and say so.
  - Same change for the three stories: each surface's entry point is owned by the page that
    hosts the link. If direct-URL-only surfaces are intended, record that in the relevant Out of
    scope so the hole is assigned rather than silent.

### Finding 5 — Dependency-note sanity: the membership-check reuse lists omit BSB-32
- **Severity:** Advisory
- **Stories touched:** BSB-22-PENDING-1, BSB-22-PENDING-3 (cross-epic: BSB-24, BSB-31, BSB-32,
  BSB-33, BSB-37)
- **Evidence:**
  - BSB-22-PENDING-1, Notes: "BSB-24, BSB-31, BSB-33 and BSB-37 reuse it."
  - BSB-22-PENDING-3, Notes: "BSB-24 must apply the same check ...; BSB-31's standalone scans,
    BSB-33's reports and BSB-37's command line reuse it." Its Out of scope, however, names
    "security scans and their standalone entry points (BSB-31, BSB-32)".
  - `epics.md` BSB-32 implementation guidance step 6: "Add the full-scan skill-page entry point
    guarded by project membership, triggering static then LLM for the same content."
  - `epics.md` BSB-22 Notes: "Every run, scan, report and command-line epic that operates inside
    a project reuses the membership check defined here."
- **What is missing/ambiguous/contradictory:** Both reuse lists omit BSB-32 even though BSB-32's
  epic explicitly requires a full-scan entry point guarded by project membership and
  BSB-22-PENDING-3's own Out of scope names BSB-32. A BSB-32 implementer reading only its own
  epic sees the requirement but no story-level pointer to the check; a BSB-22 implementer sees
  BSB-32 in one list and not the other. This is a one-sided, uneven cross-epic dependency note.
- **Proposed change:**
  - **BSB-22-PENDING-1:** Add BSB-32 to the reuse sentence: "BSB-24, BSB-31, BSB-32, BSB-33 and
    BSB-37 reuse it."
  - **BSB-22-PENDING-3:** Make the same addition and name BSB-32's full-scan entry point
    alongside BSB-31's standalone scan.
  - Same change for both stories: the reuse list names every epic whose own definition requires
    the check.

## Open questions

1. **Run/scan report access (Finding 1).** Should the stable run and scan report views linked
   from a catalog pull request be readable outside the builder authoring gate and the
   project-membership check, as `PRD.md` §2's catalog reviewer and `epics.md` BSB-33 step 6
   imply? If so, what authorizes the reviewer and which epic owns it — and BSB-22's reuse lists
   must stop claiming those views use the project-membership check.
2. **Future mutation-route ownership (Finding 2).** Should BSB-22 own minimal guarded `POST
   /projects/7/runs` and `POST /projects/7/integrations` routes that BSB-24 and BSB-23 extend,
   or should the two denial ACs move to BSB-24/BSB-23 while BSB-22 tests the guard only on its
   own GET pages? The answer decides who builds the route skeletons and what request contract
   `epics.md`'s BSB-23/BSB-24 stories must adopt.

## Proposed changes

`docs/product/epics/BSB-22/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-22-PENDING-1** — Notes: scope the shared project-membership check to author-facing
  surfaces, qualify/remove the BSB-31 and BSB-33 reuse claims, and add BSB-32 to the reuse list.
  Story/ACs: render the "New project" link on the projects list and the owner-only "Add member"
  and "Settings" links on the project page, with an AC for each. Closes Findings 1, 4 and 5 (the
  PENDING-1 side).
- **BSB-22-PENDING-2** — Notes: narrow the "shared owner guard every project-administration
  route uses" claim to the member-management use, and state that PENDING-4 owns the
  integration-management use of one parameterised owner check. Story/ACs: define where the
  add-member form and the remove control are reached from, and assert the removal control.
  Closes Findings 3 and 4 (the PENDING-2 side).
- **BSB-22-PENDING-3** — Notes: resolve the `POST /projects/7/runs` ownership and guard contract
  (BSB-22-owned minimal guarded route or BSB-24-owned AC), fix the "run creation ... not part of
  this story" contradiction, qualify the BSB-31/BSB-33 reuse claims, and add BSB-32 to the reuse
  list. Closes Findings 1, 2 and 5 (the PENDING-3 side).
- **BSB-22-PENDING-4** — Notes: resolve the `POST /projects/7/integrations` route ownership and
  guard contract, and state that it uses the shared owner check with the integration-management
  message rather than a second guard. Story/ACs: state how the settings page is reached. Closes
  Findings 2, 3 and 4 (the PENDING-4 side).
- **`story-map.json`** — No requirement IDs or story set change. After the above, PENDING-1's
  summary should match its ACs ("open the members-only project page from the author's projects
  list" currently asserts a list link and a non-member denial its ACs do not test); PENDING-2's
  and PENDING-4's "shared owner guard" wording should match the narrowed guard ownership.

Cross-epic follow-ups (not applied in this pass; they need their own epic revisions or a human
decision):

- **BSB-33** — define the stable report view's reviewer access rule and stop implying the report
  is project-member-only; align with `PRD.md` §2's catalog reviewer.
- **BSB-31 / BSB-32** — state the access rule for the report views linked from a catalog PR, and
  have their stories name the shared project-membership check (BSB-32 is currently missing from
  BSB-22's lists).
- **BSB-23 / BSB-24** — adopt the `POST /projects/7/integrations` and `POST /projects/7/runs`
  route contract chosen in Open question 2, or move their own denial ACs there.
- **BSB-36** — confirm the report links point at the reviewer-readable views, not the
  author-only pages.

No change is proposed to `epic-map.json`, the requirement IDs, the story set,
`sdlc-tracker-sync` or Jira; requirement coverage is unchanged by these edits except for the
FR-027 traceability note below.

## Architecture impact

None. Every finding is a story-boundary, shared-contract, access-rule or dependency-note issue.
The records and rules the stories rely on already exist in ADR SK-001: §9's `projects`,
`project_members` (role `owner`/`member`), `integrations` and `runs` tables, and §3/§4's
`skill-builders` group, per-request claim check and "creator is the owner; members run; only the
owner changes integrations" rule. No new entity, field, endpoint or integration is required by
BSB-22's stories. Finding 2's future routes are BSB-23/BSB-24 deliverables and Finding 1's
reviewer-facing views are BSB-31/BSB-33 deliverables; this report only asks BSB-22's notes to
stop claiming or owning them. No design-stage change is needed before
`sdlc-plan-stories-write` (revise) applies the report.

## Requirement coverage check

Yes for all six requirements, with two traceability notes; no requirement is claimed by two
stories in contradictory ways.

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-023 | BSB-22-PENDING-1 | "A signed-in author creates a project and is recorded as its owner" (HTTP 201, one `projects` row) |
| FR-024 | BSB-22-PENDING-1 | Same scenario: `owner_id` 42 and one `project_members` row with role `owner`; "The creator is the owner even when the request names another user" |
| FR-025 | BSB-22-PENDING-2 | "The owner adds a known skill-builders user as a member" (HTTP 201, role `member`, list shows the project) |
| FR-026 | BSB-22-PENDING-2 | "The owner removes a member and that member loses access" (row gone, 403 on the project, list no longer shows it) |
| FR-027 | BSB-22-PENDING-3 | Member and owner open `GET /projects/7/runs/new` (200); non-member and removed member are refused (403) on the page and on `POST /projects/7/runs`. **Traceability note:** no AC shows a member successfully *starting* a run; that positive path is FR-037/BSB-24, and PENDING-3's Notes should say so explicitly (part of Finding 2). |
| FR-028 | BSB-22-PENDING-4 | Owner sees the integration controls; non-owner member sees read-only and is refused the change (403); non-member is refused the page (403). The actual integration write is BSB-23 (FR-029 to FR-036). |

No NFR is mapped to BSB-22 in `epic-map.json`; the cross-cutting NFR-012 accessibility is
BSB-38's epic. No FR/NFR wording drift was found between `epic-map.json` and the current
`PRD.md` rows, and the Jira BSB-22 description matches `epics.md`'s description, scope, DoD and
covered requirements. One story-map mismatch is noted under Proposed changes: PENDING-1's
summary claims the project page is opened "from the author's projects list" and is
"members-only", but its own ACs do not test the list link or a non-member denial (PENDING-2's
removal AC covers the post-removal denial).

## Dependency-note sanity check

Mostly consistent; four story-level mismatches (Findings 1, 2, 3 and 5) and one epic-level
unevenness.

- **Reciprocated and real within the epic:** PENDING-2, PENDING-3 and PENDING-4 each say they
  depend on PENDING-1, and PENDING-1's Out of scope names all three; PENDING-3 and PENDING-4 say
  they depend on PENDING-2, and PENDING-2's Out of scope names both. PENDING-1 says PENDING-3
  exercises the membership check on the run-start path, and PENDING-3 agrees. PENDING-2 says
  PENDING-4 exercises the owner rule on integration routes, and PENDING-4 agrees (but see
  Finding 3 on guard ownership).
- **Reciprocated cross-epic:** BSB-18's epic Notes say every later epic depends on the local
  user record and per-request middleware; BSB-22-PENDING-1/-2 name BSB-18. BSB-23's Notes say it
  depends on the owner-only integration guard from the test-projects epic, and PENDING-4 claims
  that guard. BSB-24's Notes say it depends on the test-project membership check, and
  PENDING-3 names BSB-24. BSB-37's Notes say it obeys the same project membership, and
  PENDING-1/PENDING-3 name BSB-37.
- **One-sided — Finding 5:** BSB-22's reuse lists name BSB-24, BSB-31, BSB-33 and BSB-37 but
  omit BSB-32, whose own epic requires a project-membership-guarded full-scan entry point;
  PENDING-3's Out of scope names BSB-32, so the omission is also internally inconsistent.
- **Contradicted — Finding 1:** BSB-22 claims BSB-33's reports reuse the project-membership
  check, while BSB-33's epic promises a stable report reviewers can read without the authoring
  interface and `PRD.md` §2 makes the catalog reviewer a target user. BSB-33's epic does not
  mention project membership at all.
- **Ownership conflict — Finding 3:** PENDING-2 and PENDING-4 both claim the owner guard used on
  integration routes; the epic's guidance treats the member-management guard and the
  integration-management guard as two deliverables, so the stories need one shared check with
  two documented uses.
- **Route ownership — Finding 2:** PENDING-3 and PENDING-4 exercise mutation routes their own
  Notes assign to BSB-24 and BSB-23; no note says who builds the route skeletons.
- **No dangling keys:** every referenced key exists — BSB-18's stories are on disk; BSB-23,
  BSB-24, BSB-31, BSB-32, BSB-33, BSB-36, BSB-37 and BSB-38 exist as epics, though their stories
  are not written yet.
- **Ordering not computed:** `epics.md`'s foreach lists BSB-22, BSB-23, ..., BSB-24, ..., BSB-33,
  ..., BSB-37; no `epic-sequence.md`/`.json` exists for BSB-22. Sequencing remains
  `sdlc-plan-epic-sequence`'s job; this pass only records the dependency gaps.

---

*On approval: `docs/product/epics/BSB-22/_epic/stories.md` is updated in place for
BSB-22-PENDING-1, -2, -3 and -4 (and the PENDING-1/PENDING-2/PENDING-4 summaries in
`story-map.json`). No Jira keys exist yet for these draft stories, and no Jira write is made in
this pass. Next: `sdlc-plan-stories-write` (revise), then `sdlc-plan-epic-sequence` and the
per-story review for single-story concerns this epic-level pass deliberately did not raise.*
