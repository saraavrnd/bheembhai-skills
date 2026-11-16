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
