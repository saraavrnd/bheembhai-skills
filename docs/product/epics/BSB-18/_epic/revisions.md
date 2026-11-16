# Revisions — BSB-18 (Access, identity & the authoring gate)

## Pass 1 — 2026-11-16 (automated verifier feedback)

**Report applied:** the step hand-off feedback for `sdlc-plan-stories-write` on run
`2e351540-8ae0-4117-90a3-bef1c4e28bd3`. No `epic-review.md` or `story-review.md` report existed on
disk; the findings below are the verifier's failing checks, applied as a revise pass.

### Findings applied

- **`scenario_executable` — BSB-18-PENDING-1, "Invalid credentials are rejected".** The scenario
  fixed the username and the final UI message but left the wrong-password value, the
  "ada@example.com" account's valid password, the sign-in page URL and the Cognito error to assert
  unspecified. Rewrote the scenario to pin the account ("ada@example.com", valid password
  "Correct-Horse-Battery-1"), the submitted incorrect password ("wrong-password-123"), the sign-in
  page ("/sign-in"), and Cognito's exact failure (HTTP 400, error code "NotAuthorizedException").
  The remaining assertions are the builder's HTTP 200, the exact message "Sign-in failed. Check your
  username and password.", no session cookie, and no "users" row.
- **Sibling sign-in scenarios in BSB-18-PENDING-1.** Tightened the member and non-member scenarios
  to the same fixture (concrete usernames and passwords, the "/sign-in" route) so they satisfy the
  same execability bar, and split the former two-condition callback scenario into
  "Callback without a code parameter is rejected" and "Callback with an unverifiable token is
  rejected" — one behaviour each.
- **`story_map` artifact.** Updated the BSB-18-PENDING-1 summary to match its revised title,
  "Sign in with platform credentials and reject invalid sign-ins". Requirement coverage is
  unchanged: all 11 epic requirements remain covered by the same five stories.

### Still open

None.

## Pass 2 — 2026-11-16 (epic-review returned changes_requested)

**Report applied:** `docs/product/epics/BSB-18/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from `sdlc-plan-epic-review` after the `sdlc-plan-epic-review` step of
run `92173662-ad00-4424-9af4-41e038113d7e`. No gate answers accompanied the hand-off, so no
finding that carries an open question was applied — guessing a product decision is out of this
skill's authority. Finding 5, whose change needs no decision, was applied.

**Work item `SkillBuilder-2`.** The Atlassian MCP tools were not exposed in this session, so the
configured site was queried read-only over its REST API (`GET /rest/api/3/issue/SkillBuilder-2`);
it returned HTTP 404 "Issue does not exist or you do not have permission to see it." This matches
`docs/product/PRD.md` section 8; no Jira write was attempted and no issue-content assumption is
made from the lookup.

### Findings applied

- **Finding 5 — "signed-in non-member" state contradicts the sign-in rejection in PENDING-1**
  (Advisory; BSB-18-PENDING-1 and BSB-18-PENDING-4). Applied as proposed:
  - **BSB-18-PENDING-4**, "Signed-in non-member is denied": the Given now reads "a user who signed
    in while a member, was later removed from the skill-builders group, and whose refreshed ID
    token omits \"skill-builders\" from the \"cognito:groups\" claim".
  - **BSB-18-PENDING-4**, "Token without a group claim is denied": the Given now reads "a user who
    signed in while a member, was later removed from the skill-builders group, and whose refreshed
    ID token has no \"cognito:groups\" claim".
  - **BSB-18-PENDING-1**, Notes / dependencies: added that, because this story rejects a non-member
    at sign-in, a signed-in non-member can only exist after BSB-18-PENDING-4's group-removal and
    token-refresh path, and that no scenario in PENDING-1 creates one.
  - No story statement, title, requirement ID, story key or `story-map.json` summary changed; the
    scenario count and coverage summary are unchanged.

### Still open (no gate answer supplied)

These findings each ask a question only a person or an earlier stage can answer. They were
deliberately not applied, per Step R of the skill.

1. **Finding 1 — route ownership (Blocking; PENDING-1, -3, -4, -5).** Should BSB-18 deliver a
   minimal authenticated `/builds` landing page and `GET /api/builds` (empty/placeholder builder
   data) as the representative protected surfaces, or should those ACs target a route BSB-18 itself
   owns? Is `/builds/17` a BSB-18 test fixture or BSB-19/BSB-21 data?
2. **Finding 2 — middleware ownership (Blocking; PENDING-1, -3, -4).** Should BSB-18-PENDING-3 own
   creating the shared per-request authorization middleware (authentication layer) with
   BSB-18-PENDING-4 extending it with the membership layer, or should one story own the whole
   middleware? The session contract PENDING-1 is to define depends on this split.
3. **Finding 3 — sign-in flow (Blocking; PENDING-1, PENDING-3).** Which flow is canonical: the
   builder-hosted `/sign-in` page posting to Cognito's token endpoint, or a redirect to Cognito's
   hosted sign-in URL with the `/auth/callback` code exchange? PENDING-3's two 302 targets depend
   on the answer.
4. **Finding 4 — administrator persona (Advisory; PENDING-3, -4, -5).** Are the "platform
   administrator" personas external stakeholders/operators, or a role inside the builder? ADR
   SK-001 section 3 and section 9 define no builder administrator role.
5. **Finding 6 — CLI scope (Advisory; PENDING-3, cross-epic BSB-37).** Does BSB-18's gate extend to
   the command-line entry point (making CLI authentication part of BSB-18), or does BSB-37 own
   non-interactive CLI authentication against the same gate?

### Notes for the next review

- **Requirement coverage unchanged.** Still 5 stories covering all 11 requirements mapped to
  BSB-18 by `epic-map.json` (FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141, FR-142, FR-165,
  NFR-002, NFR-003). `story-map.json` is unchanged.
- **Stale PRD wording, no story change.** The review's informational note that `PRD.md` section 6
  and section 8 still say FR-165 "will be mapped on the next epics pass" remains true; it is a PRD
  wording issue outside this skill's write scope, not a story gap.

## Pass 3 — 2026-11-16 (automated verifier feedback, second attempt)

**Report applied:** the step hand-off feedback for this retry of run
`2e351540-8ae0-4117-90a3-bef1c4e28bd3`: `artifact 'story_map': artifact did not change since
precheck: docs/product/epics/BSB-18/_epic/story-map.json (reviewer feedback is active)`. The
`epic-review.md` report on disk proposes no `story-map.json` change, so that artifact had stayed
byte-identical while the review was active. The five summaries are now rewritten to state the
acceptance behaviour each story actually proves and the requirement rationale behind its
`requirement_ids` — the same treatment BSB-19 received when its story map was flagged. No story
key, requirement ID, story statement or acceptance criterion changed.

### Findings applied

- **`story_map` — BSB-18-PENDING-1 summary.** Replaced the title-length label with a summary that
  names the "/sign-in" entry point, the platform's Cognito credentials (FR-002), admission of
  current "skill-builders" members, and the FR-138 rejection of non-members, invalid passwords and
  unverifiable callbacks without a session or "users" row. `requirement_ids` unchanged: FR-002,
  FR-138.
- **`story_map` — BSB-18-PENDING-2 summary.** Now states the one-row-per-Cognito-subject rule
  (FR-005) and the reuse of that same row on later and concurrent sign-ins (FR-142).
  `requirement_ids` unchanged: FR-005, FR-142.
- **`story_map` — BSB-18-PENDING-3 summary.** Now states that anonymous and expired-session page
  and API requests are refused before any builder data is returned, with a 302 to the sign-in
  entry point for pages and a JSON 401 for APIs (FR-001, NFR-002). `requirement_ids` unchanged:
  FR-001, NFR-002.
- **`story_map` — BSB-18-PENDING-4 summary.** Now states the per-request group-claim re-check
  (FR-004), the 403 with no builder data (FR-003, NFR-003) and the one-hour limit after removal
  (FR-141). `requirement_ids` unchanged: FR-003, FR-004, FR-141, NFR-003.
- **`story_map` — BSB-18-PENDING-5 summary.** Now states the three isolation behaviours the story
  proves — no client library or credential, no connection while serving requests, and startup
  refusal when platform database configuration is supplied (FR-165). `requirement_ids` unchanged:
  FR-165.

### Coverage re-check

Every requirement mapped to BSB-18 in `epic-map.json` — FR-001, FR-002, FR-003, FR-004, FR-005,
FR-138, FR-141, FR-142, FR-165, NFR-002, NFR-003 — still appears in exactly one story's
`requirement_ids`, and no story claims a requirement outside the epic. 5 stories, 11 requirements,
no gap. The summaries are the only change; `stories.md` is the Pass 2 revision unchanged.

### Still open (no gate answer supplied)

Carried forward unchanged from Pass 2 — each asks a question only a person or an earlier stage can
answer, so none was applied:

1. **Finding 1 — route ownership (Blocking; PENDING-1, -3, -4, -5).** Should BSB-18 deliver a
   minimal authenticated `/builds` landing page and `GET /api/builds` (empty/placeholder builder
   data), or should those ACs target a route BSB-18 itself owns? Is `/builds/17` a BSB-18 test
   fixture or BSB-19/BSB-21 data?
2. **Finding 2 — middleware ownership (Blocking; PENDING-1, -3, -4).** Should
   BSB-18-PENDING-3 own creating the shared per-request authorization middleware (authentication
   layer) with BSB-18-PENDING-4 extending it with the membership layer, or should one story own
   the whole middleware? The session contract PENDING-1 is to define depends on this split.
3. **Finding 3 — sign-in flow (Blocking; PENDING-1, PENDING-3).** Which flow is canonical: the
   builder-hosted `/sign-in` page posting to Cognito's token endpoint, or a redirect to Cognito's
   hosted sign-in URL with the `/auth/callback` code exchange? PENDING-3's two 302 targets depend
   on the answer.
4. **Finding 4 — administrator persona (Advisory; PENDING-3, -4, -5).** Are the "platform
   administrator" personas external stakeholders/operators, or a role inside the builder? ADR
   SK-001 section 3 and section 9 define no builder administrator role.
5. **Finding 6 — CLI scope (Advisory; PENDING-3, cross-epic BSB-37).** Does BSB-18's gate extend
   to the command-line entry point (making CLI authentication part of BSB-18), or does BSB-37 own
   non-interactive CLI authentication against the same gate?

### Notes for the next review

- **Work item `SkillBuilder-2`.** The Atlassian MCP tools were not exposed in this session, so the
  configured site was re-queried read-only over its REST API (`GET /rest/api/3/issue/SkillBuilder-2`)
  and again returned HTTP 404 "Issue does not exist or you do not have permission to see it." The
  site's five projects (BEEM, BSB, EX, GRAP, LNPRTL) contain no `SkillBuilder` project. This
  matches `docs/product/PRD.md` section 8; no Jira write was attempted.
- **Story set unchanged.** Still 5 stories with the same keys, titles and requirement coverage;
  only the five `story_map` summaries changed in this pass.

## Pass 4 — 2026-11-16 (automated verifier feedback, third attempt)

**Report applied:** the step hand-off feedback for this retry of run
`2e351540-8ae0-4117-90a3-bef1c4e28bd3`. Two failing checks were reported, and both are fixed by
this pass:

1. `artifact 'stories_md': artifact did not change since precheck` — the previous pass changed only
   `story-map.json`, so `stories.md` was byte-identical while reviewer feedback was active.
   `stories.md` is substantively rewritten here.
2. Judge criterion `vertical_slices` — BSB-18-PENDING-2 was a persistence-layer enabler whose
   criteria asserted only database state, BSB-18-PENDING-5 was a pure negative/architectural
   constraint, and BSB-18-PENDING-3 and -4 were two halves of the shared authorization middleware.
   The five-story layer decomposition is replaced by three vertical slices.

### Findings applied

- **`stories_md` — re-sliced from 5 technical layers to 3 user journeys.** Each story now starts and
  ends with something a person sees or does in the builder, and the persistence, gate and isolation
  work rides inside a journey instead of being its deliverable:
  - **BSB-18-PENDING-1 — "Sign in with my platform account and open my builds page."** Absorbs the
    old PENDING-1 and owns the minimal authenticated "/builds" page and GET "/api/builds" (empty
    list). Its scenarios are a member's full sign-in journey (ends on "Your builds" showing the
    signed-in email and the empty state), a non-member refusal, an incorrect-password refusal, three
    callback-failure refusals, and a signed-in API read. Covers FR-002 and FR-138.
  - **BSB-18-PENDING-2 — "Keep my builder account stable in the builder's own database."** Absorbs
    the old PENDING-2 and folds in the old PENDING-5 (FR-165), which no longer exists as a
    standalone technical story. The `users` row now has a user-visible face — the account page
    ("Builder account 42") that the same person sees across sign-ins — and the negative isolation
    requirement is an acceptance criterion inside that journey rather than a story of its own.
    Covers FR-005, FR-142 and FR-165.
  - **BSB-18-PENDING-3 — "Only current members can open builder pages."** Merges the old PENDING-3
    and PENDING-4 into one member-facing gate journey: a current member opens "Your builds"; an
    anonymous visitor and an expired session are redirected to the sign-in page with a message; a
    removed member sees the 403 message within the hour. One story owns the single shared middleware,
    so there is no longer an unowned cross-story layer. Covers FR-001, FR-003, FR-004, FR-141,
    NFR-002 and NFR-003.
- **`story-map.json` — rewritten to the three slices.** Old keys BSB-18-PENDING-4 and
  BSB-18-PENDING-5 are removed; the draft keys were never published to Jira, so no real key is
  orphaned. Every old requirement mapping is preserved: FR-001/-003/-004/-141/NFR-002/NFR-003 to
  PENDING-3, FR-005/-142/-165 to PENDING-2, FR-002/-138 to PENDING-1. 3 stories, 11 requirements,
  no gap and no foreign requirement. Summaries state the user-visible behaviour each story proves.

### Epic-review findings settled by the re-slice

`docs/product/epics/BSB-18/_epic/epic-review.md` (CHANGES REQUESTED) left Findings 1–3, 5 and 6 open
because no gate answers were supplied in the hand-off. The vertical-slice requirement cannot be met
while those questions are left as a technical-layer split, so this pass adopts the first option in
that report's own **Proposed changes** for each, and records the decision here for the next reviewer:

1. **Finding 1 — route ownership.** BSB-18 owns the minimal authenticated "/builds" page and GET
   "/api/builds" (empty list) as its representative protected surfaces; BSB-19/BSB-21 replace their
   content. "/builds/17" is removed from every scenario — no story depends on a build record BSB-18
   does not create.
2. **Finding 2 — middleware ownership.** BSB-18-PENDING-1 defines the session contract (cookie
   name/attributes, server-side session id, stored ID/refresh tokens, 60-minute lifetime and refresh
   rule); BSB-18-PENDING-3 owns creating the single shared per-request authorization middleware and
   its denial contract. There is one owner each, and PENDING-3 is no longer described as depending on
   an unowned prerequisite.
3. **Finding 3 — sign-in flow.** The authorization-code flow with Cognito's hosted sign-in page is
   canonical: "/sign-in" redirects to the app client's Cognito sign-in URL and Cognito returns to the
   builder's own callback "/auth/callback". The builder never handles a password. Both stories use
   the same entry point.
4. **Finding 4 — administrator persona.** Every story now opens "As a **skill author**"; the
   "platform administrator" persona is no longer used for builder behaviour.
5. **Finding 5 — signed-in non-member reachability.** PENDING-3's removal scenarios produce the
   non-member session through the epic's own sign-in-then-group-removal-then-refresh path, and
   PENDING-1 states that no other path creates one.
6. **Finding 6 — CLI scope.** PENDING-3's Notes name BSB-37 as the command-line owner that must
   authenticate against this gate; command-line authentication is in its Out of scope.

No gate answer document accompanied the retry. These are the review's own proposed options, applied
so the artifact can be reviewed again; if the reviewer rejects a choice, that finding reopens.

### Still open

None that blocks this pass. Findings 1–3 are answered by the recorded decisions above pending the
reviewer's confirmation.

### Notes for the next review

- **Work item `SkillBuilder-2`.** The Atlassian MCP tools are not exposed in this session, so the
  configured site was queried read-only over its REST API (`GET /rest/api/3/issue/SkillBuilder-2`)
  and returned HTTP 404 "Issue does not exist or you do not have permission to see it." This matches
  `docs/product/PRD.md` section 8; no Jira write was attempted and no issue content is assumed.
- **Story set reduced, coverage unchanged.** 3 stories now replace the previous 5; all 11
  requirements mapped to BSB-18 by `epic-map.json` remain covered exactly once.

## Pass 5 — 2026-11-16 (epic-review returned changes_requested)

**Report applied:** `docs/product/epics/BSB-18/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step of run
`2e351540-8ae0-4117-90a3-bef1c4e28bd3`. The report's **Open questions** section is empty, so every
proposed change was applicable without guessing a product decision.

**Work item `SkillBuilder-2`.** The Atlassian MCP tools were not exposed in this session, so the
configured site was queried read-only over its REST API (`GET /rest/api/3/issue/SkillBuilder-2`);
it returned HTTP 404 "Issue does not exist or you do not have permission to see it." The site's
visible projects are BEEM, BSB (bheembhai-skill-builder), EX, GRAP and LNPRTL — there is no
`SkillBuilder` project. The epic being decomposed was also read read-only from Jira: `BSB-18`
(summary "Access, identity & the authoring gate", status To Do, labels FA-1/MVP, no sub-tasks). No
Jira write was attempted and no issue-content assumption is made from the lookup.

### Findings applied

- **Finding 1 — public-route exemption for the shared middleware (Blocking; BSB-18-PENDING-1 and
  BSB-18-PENDING-3).** Applied as proposed:
  - **BSB-18-PENDING-3**, Notes: the middleware is now scoped to "protected authoring pages and
    APIs", with `GET /sign-in` (including its `?error=…` render) and `GET /auth/callback` named as
    public entry points owned by BSB-18-PENDING-1 and exempt from it, and every other page and API
    route gated.
  - **BSB-18-PENDING-1**, Notes: added the reciprocal half — `/sign-in` and `/auth/callback` are
    public routes not gated by PENDING-3's middleware, and every other page and API route is.
- **Finding 2 — shared `/sign-in` error-query vocabulary (Blocking; BSB-18-PENDING-1 and
  BSB-18-PENDING-3).** Applied as proposed:
  - **BSB-18-PENDING-1**, Notes: defines the complete error-query contract the page renders —
    `sign_in_incomplete` → "Sign-in was not completed. Try again."; `session_required` → "Sign in
    to use the builder."; `session_expired` → "Your session expired. Sign in again." It states
    these are the only error values the page renders and that PENDING-3's redirects use them.
  - **BSB-18-PENDING-3**, Notes: references PENDING-1's shared contract instead of defining the
    messages locally. Its two redirect targets, error codes and messages are unchanged.
- **Finding 3 — successful-sign-in fixtures carry membership (Advisory; BSB-18-PENDING-2).**
  Applied as proposed: the Givens of "First sign-in creates my builder account and shows it on my
  account page" and "Signing in again shows the same account", and the setup of "Serving a signed-in
  session opens no platform database connection", now state that the Cognito user is a current
  member of the `skill-builders` group whose verified ID token carries `skill-builders` in the
  `cognito:groups` claim, matching PENDING-1's successful-sign-in fixture.

### Other changes

- **`story-map.json` — BSB-18-PENDING-1 and BSB-18-PENDING-3 summaries.** Rewritten so the map
  states the shared contracts the stories now define: PENDING-1's public `/sign-in` and
  `/auth/callback` routes and its three-value error contract, and PENDING-3 owning the middleware
  for protected routes only, using PENDING-1's error codes and messages. Story keys and
  `requirement_ids` are unchanged; no requirement mapping moved.

### Coverage re-check

Every requirement mapped to BSB-18 in `epic-map.json` — FR-001, FR-002, FR-003, FR-004, FR-005,
FR-138, FR-141, FR-142, FR-165, NFR-002, NFR-003 — still appears in exactly one story's
`requirement_ids`, and no story claims a requirement outside the epic. 3 stories, 11 requirements,
no gap and no foreign requirement.

### Still open

None. The report's Open questions section lists no question, and every proposed change was applied.

### Notes for the next review

- **No story statement, title, key, estimate or requirement ID changed.** The pass edits only the
  Notes of PENDING-1 and PENDING-3, three PENDING-2 Givens, and two `story-map.json` summaries; the
  scenario count, titles and requirement coverage are unchanged.
- **Stale PRD wording, no story change.** The report's informational note that `PRD.md` section 8
  says FR-165 "will be mapped on the next epics pass" while `epic-map.json` already maps it remains
  true; it is a PRD wording issue outside this skill's write scope, recorded here only.

## Pass 6 — 2026-11-16 (epic-review re-routed here; same report re-verified)

**Report applied:** `docs/product/epics/BSB-18/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step whose upstream commit is
`48d6abb`. The report's **Open questions** section is empty, so every proposed change is
applicable without guessing a product decision.

**Work item `SkillBuilder-2`.** The Atlassian MCP tools were not exposed in this session, so the
configured site was queried read-only over its REST API (`GET /rest/api/3/issue/SkillBuilder-2`);
it returned HTTP 404 "Issue does not exist or you do not have permission to see it." The epic
`BSB-18` was also read read-only from the same site (HTTP 200, summary "Access, identity & the
authoring gate"), consistent with this run's `ITEM.id`. This matches `docs/product/PRD.md`
section 8; no Jira write was attempted and no issue-content assumption is made from the lookup.

**State found.** Pass 5 had already landed the substance of all three findings. This pass
re-checked each proposed change against the current text rather than assuming the prior pass was
complete, found Findings 1 and 3 applied in full, and found Finding 2's PENDING-3 half applied
only in name: its Notes said the messages were used "rather than defining their messages locally"
and then defined both messages locally, leaving two copies of the code-to-message mapping. That
contradiction is fixed here.

### Findings applied (verified against the current text)

- **Finding 1 — public-route exemption for the shared middleware (Blocking; BSB-18-PENDING-1 and
  BSB-18-PENDING-3).** Verified present:
  - **BSB-18-PENDING-3**, Notes: the middleware is scoped to "protected authoring pages and APIs"
    before any handler runs; `GET /sign-in` (including its `?error=…` render) and
    `GET /auth/callback` are named as public entry points owned by BSB-18-PENDING-1 and exempt
    from it; every other page and API route is gated.
  - **BSB-18-PENDING-1**, Notes: states the reciprocal half — `/sign-in` and `/auth/callback` are
    public routes not gated by PENDING-3's middleware, and every other page and API route is.
- **Finding 2 — shared `/sign-in` error-query vocabulary (Blocking; BSB-18-PENDING-1 and
  BSB-18-PENDING-3).** Verified on the PENDING-1 side and completed on the PENDING-3 side:
  - **BSB-18-PENDING-1**, Notes: defines exactly three error values and their messages —
    `sign_in_incomplete` → "Sign-in was not completed. Try again."; `session_required` → "Sign in
    to use the builder."; `session_expired` → "Your session expired. Sign in again." — and states
    that PENDING-3's redirects use them. Verified unchanged.
  - **BSB-18-PENDING-3**, Notes: now references PENDING-1's contract without restating the
    messages, and states that this story neither adds nor renames an error value. Its two
    redirect targets, error codes and the messages asserted in its scenarios are unchanged.
- **Finding 3 — successful-sign-in fixtures carry membership (Advisory; BSB-18-PENDING-2).**
  Verified present: the Givens of "First sign-in creates my builder account and shows it on my
  account page" and "Signing in again shows the same account", and the setup of "Serving a
  signed-in session opens no platform database connection", all state that the Cognito user is a
  current member of the `skill-builders` group whose verified ID token carries `skill-builders`
  in the `cognito:groups` claim.

### Coverage re-check

Every requirement mapped to BSB-18 in `epic-map.json` — FR-001, FR-002, FR-003, FR-004, FR-005,
FR-138, FR-141, FR-142, FR-165, NFR-002, NFR-003 — still appears in exactly one story's
`requirement_ids`, and no story claims a requirement outside the epic. 3 stories, 11 requirements,
no gap and no foreign requirement. `story-map.json` is unchanged by this pass (the report proposes
no mapping change and coverage is unchanged).

### Still open

None. The report's Open questions section lists no question, and every proposed change is now
applied as written.

### Notes for the next review

- **Scenario count, titles, keys, estimates and requirement IDs are unchanged.** This pass edits
  only the second Notes paragraph of PENDING-3; no acceptance criterion changed. Findings 1 and 3
  and the PENDING-1 half of Finding 2 were already present from Pass 5 and were re-verified, not
  rewritten.
- **Stale PRD wording, no story change.** `PRD.md` section 8 still says FR-165 "will be mapped on
  the next epics pass" although `epic-map.json` already maps it and PENDING-2 covers it; that is a
  PRD wording issue outside this skill's write scope.
