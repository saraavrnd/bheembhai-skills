# Epic Review — BSB-18: Access, identity & the authoring gate

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-15 · **Stories reviewed:** BSB-18-PENDING-1, BSB-18-PENDING-2, BSB-18-PENDING-3, BSB-18-PENDING-4

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-18/_epic/epic-review.md`.

## Context loaded

- **Target resolution.** The run named the target "SkillBuilder", which is the product (`PRD.md`
  title), not a Jira issue. The PRD itself (§8) records that the Atlassian project has no issue
  titled `SkillBuilder`. No Atlassian MCP tools were available in this session, so the epic was
  resolved from disk instead. BSB-18 is the only epic with a decomposed story set on this branch
  (`docs/product/epics/BSB-18/_epic/`). No Jira read or write was made.
- **Full story set:** all four BSB-18 stories from `stories.md`, including the shared
  *Session and identity contract* table, plus `story-map.json` and `revisions.md` (passes 1–2).
  The four stories are BSB-18-PENDING-1 (session gate), -2 (sign-in), -3 (per-request membership and
  one-hour bound) and -4 (local user record).
- **Requirements:** `epic-map.json` entry for BSB-18 (FR-001–FR-005, FR-138, FR-141, FR-142,
  NFR-002, NFR-003); `PRD.md` §2 (target users), §5 (FA-1), §6 and §7 rows for those IDs, §8
  (access model, external prerequisites); `epics.md` BSB-18 section (scope, implementation
  guidance, notes).
- **Architecture:** this repo has no `docs/architecture.md`, `docs/data-model.md`,
  `docs/api-contracts/` or `docs/ui-conventions.md` (no `AGENTS.md`/`CLAUDE.md` Project Layout
  table either, so the default layout applies). The committed design for this epic is
  `docs/adr/SK-001-skill-builder.md`: §3 (Cognito login, `skill-builders` group, per-request
  `cognito:groups` check, "one hour at most", `users` keyed by `sub`), §7 (the CLI), §9 (data model:
  `users`, `builds.created_by`, `projects.owner_id`, `project_members`, `runs.user_id`) and
  "Tests (what pins this)". `SK-002` was skimmed by keyword (no identity content).
- **Other epics checked** (only for cross-epic assumptions about the FA-1 gate): BSB-22 (test
  projects and membership: "adding a user who is not a current skill-builder must fail through the
  FA-1 gate"), BSB-23 (owner-only integration settings) and BSB-37 (CLI: "must authenticate with
  the same authoring identity and membership gate as the web surface"). No `epic-sequence.md`
  exists yet. `epics.md` says every other epic depends on BSB-18.

## Findings

### Finding 1 — Epic-wide scope boundary: no story owns the "valid session" check (signature, issuer, audience)
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3 (and the shared Session and identity
  contract that BSB-18-PENDING-2 and BSB-18-PENDING-4 also use)
- **Evidence:**
  - BSB-18-PENDING-1 claims NFR-002 ("Every request without a **valid** authenticated session is
    rejected"). Its scenarios cover only *no cookie* (page 302, API 401) and *expired `exp`* (page
    302 + clearing header). Its out-of-scope says membership checks for "a request that does
    carry a session" belong to BSB-18-PENDING-3.
  - BSB-18-PENDING-3's Notes say "Every request validates the `sb_session` ID token JWT
    (signature, `iss`, `aud`, `exp`)", but none of its five scenarios gives a token with a bad
    signature, a foreign `iss` or a foreign `aud`. Its scope is the `cognito:groups` claim.
  - The contract table requires `aud` = `skill-builder-web`. SK-001 §3 says the builder is a
    *separate app client in the platform's existing User Pool*. So a token issued to the
    platform's own app client has a valid signature and a valid `iss`. Only the `aud` check stops
    it from being accepted.
- **What is missing/ambiguous/contradictory:** The two stories split the session check. Each
  implementer can reasonably assume the other validates signature, `iss` and `aud`. No acceptance
  criterion in the epic exercises them. The API-surface response for a session cookie that is
  present but invalid or expired is also undefined. BSB-18-PENDING-1 defines the API 401 only for
  "no cookie", and both stories define the expired-cookie case only for a page route (302). A
  forged or foreign-client token is exactly the NFR-002 case, and today nobody owns it.
- **Question (if a person must decide):** None. This is an ownership and wording fix that follows
  from NFR-002 and the existing contract.
- **Proposed change:**
  - **BSB-18-PENDING-1:** make it the single owner of "valid session" = signature (User Pool
    key), `iss`, `aud`, `exp` and the presence of the required claims. Add scenarios, each using the
    contract's exact `Location`, clearing `Set-Cookie` and 0-byte body:
    - (a) a token whose signature does not verify → page 302 + clearing header;
    - (b) a token with `aud` = a different app client of the same pool → page 302 + clearing
      header;
    - (c) a token with a different `iss` → page 302 + clearing header;
    - (d) an expired or invalid cookie on `GET /api/builds` → HTTP 401 with the existing
      `authentication_required` JSON body plus the clearing header, and none of `Alpha`/`Beta`/`Gamma`.

    Extend the out-of-scope line to "membership checks for a request that carries a *valid*
    session".
  - **BSB-18-PENDING-3:** change the Notes bullet to say the token's validity (signature, `iss`,
    `aud`, `exp`) is enforced by BSB-18-PENDING-1's gate. This story adds only the
    `cognito:groups` check, which runs after that gate on every request. No scenario change.

### Finding 2 — Cross-epic / external dependency silently assumed: the one-hour removal bound depends on the platform's ID-token lifetime
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-3 (the guarantee), BSB-18-PENDING-1 and BSB-18-PENDING-2
  (the shared contract and session issuance), BSB-18-PENDING-4 (its scenarios use the same token
  fixtures)
- **Evidence:**
  - BSB-18-PENDING-3 Notes: "The one-hour bound in FR-141 holds because Cognito issues the ID token
    with `exp` at most one hour after sign-in and the builder accepts no token at or after `exp`."
  - The contract table says the User Pool and signing keys "are supplied by the platform". It
    lists the required claims as `sub`, `email`, `name`, `cognito:groups`, `iss`, `aud`, `exp`.
    There is no `iat`/`auth_time`, and no stated token-validity setting.
  - BSB-18-PENDING-2 sets `Max-Age=3600` on the cookie. That limit is enforced only by the browser,
    and a replayed cookie ignores it.
  - `epics.md` BSB-18 Notes: "a cached claim older than one hour must not authorize a request".
- **What is missing/ambiguous/contradictory:** In Cognito, ID-token validity is a per-app-client
  setting and can be longer than one hour. FR-141 (an MVP security requirement) holds only if the
  platform configures the `skill-builder-web` client with an ID-token validity of 60 minutes or
  less. No story writes that down as an external prerequisite, and nothing in the builder enforces
  it. Every scenario fixture uses `exp` = issue + 1 h, so a longer-lived token would pass every
  test while breaking FR-141. The fix changes the shared contract, which all four stories' token
  fixtures follow. That makes it an epic-level decision, not a BSB-18-PENDING-3 wording fix.
- **Question (if a person must decide):** Should the builder enforce the one-hour bound itself
  (refuse any session whose `iat` is 3600 s or more before the current time, whatever `exp` says)?
  Or should FR-141 rely on the platform's ID-token validity for `skill-builder-web` being ≤ 60
  minutes, recorded as an external prerequisite? (Open question 1)
- **Proposed change:**
  - **If the builder enforces it:**
    - Contract table: add `iat` to the required claims and add "a session is also expired when
      `iat` is 3600 s or more before the current time".
    - BSB-18-PENDING-1: add a scenario where a token with `exp` 24 h out but `iat` 3600 s ago is
      treated as unauthenticated (302 + clearing header).
    - BSB-18-PENDING-3: rewrite the FR-141 note to cite the builder's own `iat` bound, and add
      `iat` to the removed-member scenarios.
    - BSB-18-PENDING-2 and BSB-18-PENDING-4: add `iat` to every token fixture.
  - **If the builder relies on platform configuration:**
    - Contract table: add a row "ID-token validity for app client `skill-builder-web`: ≤ 60
      minutes (platform-configured prerequisite)".
    - BSB-18-PENDING-3 Notes: name that prerequisite as the dependency FR-141 rests on.
    - BSB-18-PENDING-1 Notes: list it with the other platform-supplied items.

### Finding 3 — Epic-wide scope boundary / cross-epic dependency: non-browser clients (CLI, BSB-37) assume this epic's gate, which only accepts a browser cookie
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3 (the gate surfaces), BSB-18-PENDING-4
  (attribution of actions to a local user)
- **Evidence:**
  - BSB-37 (`epics.md`), edge cases: "the CLI must authenticate with the same authoring identity and
    membership gate as the web surface". FR-116–FR-118 (CLI run and scans) are MVP.
  - BSB-18-PENDING-1 and BSB-18-PENDING-3 recognise only the `sb_session` cookie, which is
    obtained only through the hosted-UI authorization-code redirect (BSB-18-PENDING-2).
  - No story's out-of-scope mentions non-browser clients or an `Authorization` header.
  - FR-004 / NFR-002 / NFR-003 say "every request". The epic description says every later action,
    including "starting runs", must be attributable to a local user record. SK-001 §9 gives
    `runs.user_id`.
  - SK-001 §7 describes the CLI as `python -m skill_builder.runner …` "without the web app", so it
    may not pass through any HTTP gate at all.
- **What is missing/ambiguous/contradictory:** BSB-37 counts on FA-1 to supply the CLI's identity
  and membership check. BSB-18 neither supplies it nor disclaims it, so nobody owns it. If BSB-18
  is built as written, an MVP CLI run either has no attributable user and no membership check, or
  BSB-37 invents its own token handling. A second, divergent gate would be a security-relevant
  inconsistency.
- **Question (if a person must decide):** Does BSB-18 own authentication for non-browser clients
  (e.g. the API gate also accepts `Authorization: Bearer <Cognito ID token>` and validates it with
  the same signature, `iss`, `aud`, `exp` and `cognito:groups` rules)? Or is CLI identity and
  membership BSB-37's concern, with BSB-18 explicitly scoped to the browser session? (Open
  question 2)
- **Proposed change:**
  - **If BSB-18 owns it:** add a story (or extend BSB-18-PENDING-1 and BSB-18-PENDING-3) with
    scenarios for a bearer ID token on `GET /api/builds`:
    - valid member → 200;
    - missing or invalid → 401 `authentication_required`;
    - non-member → 403 `not_a_member`.

    BSB-18-PENDING-4 Notes then state that a bearer-authenticated request resolves to the same
    `users` row by `cognito_sub`.
  - **If BSB-37 owns it:** add to the out-of-scope of BSB-18-PENDING-1 and BSB-18-PENDING-3:
    "Authentication of non-browser clients (the command line, FR-116–FR-118) — owned by epic
    BSB-37; this epic's gate covers browser sessions only". Add the same pointer to
    BSB-18-PENDING-4's out-of-scope for local-user attribution of CLI actions.

  In both cases the mechanism the CLI uses to get a token is not designed in SK-001 §7. Whichever
  epic owns it must settle that before its story design (see Architecture impact).

### Finding 4 — Epic-wide scope boundary: no story resolves the signed-in request to its local user record
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3, BSB-18-PENDING-4
- **Evidence:**
  - Epic description: "every later action … must be attributable to a local user record".
  - BSB-18-PENDING-4 Notes: "The local `users` table is the durable owner reference later epics
    use".
  - SK-001 §9 has `builds.created_by`, `projects.owner_id` and `runs.user_id`.
  - BSB-18-PENDING-4's scenarios cover the upsert only at the callback. BSB-18-PENDING-1 and
    BSB-18-PENDING-3 validate the token on each request but never map `sub` → `users.id`.
- **What is missing/ambiguous/contradictory:** No acceptance criterion says that an admitted
  request carries the local `users.id`. None says what happens when a valid, member token's `sub`
  has no `users` row (for example, a session issued before the record existed). Every downstream
  epic (BSB-19, BSB-22, BSB-24) will otherwise each write its own `sub` lookup. Safe to build as
  written; worth closing here once.
- **Question (if a person must decide):** None. The proposal below follows BSB-18-PENDING-4's own
  rule that "only a successful, admitted sign-in creates or reuses a record".
- **Proposed change:**
  - **BSB-18-PENDING-4:** add a Notes bullet that the gate exposes the local `users.id`, resolved
    by `cognito_sub`, to every admitted request. Add a scenario: a valid member token whose `sub`
    has no `users` row is treated as unauthenticated (page 302 + clearing header; API 401
    `authentication_required`), and no row is created.
  - **BSB-18-PENDING-1 and BSB-18-PENDING-3:** add a Notes cross-reference that local-user
    resolution is BSB-18-PENDING-4's and happens after the session and membership checks.

### Finding 5 — Cross-story actor & role consistency: "platform owner" is not a defined user type
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-3 (and, for consistency, BSB-18-PENDING-1, BSB-18-PENDING-2,
  BSB-18-PENDING-4)
- **Evidence:** BSB-18-PENDING-3: "As a **platform owner**…". BSB-18-PENDING-1, -2 and -4 use
  "As a **skill author**". `PRD.md` §2 defines Skill author, Test-project owner, Catalog reviewer
  and Platform administrator, and no "platform owner". "Platform owner" is easily confused with
  the BSB-22 *test-project owner*, the role that later epics authorize against.
- **What is missing/ambiguous/contradictory:** The actor is prose shorthand with no backing user
  type. The intended actor (whoever removes members from `skill-builders`) is the PRD's
  *Platform administrator*.
- **Question (if a person must decide):** None.
- **Proposed change:** BSB-18-PENDING-3: replace "platform owner" with "platform administrator"
  (PRD §2). BSB-18-PENDING-1, -2 and -4: no change; "skill author" is already the PRD term.

### Finding 6 — Cross-story scope overlap: the gate's "every request" vs. the unauthenticated callback route
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-2
- **Evidence:** BSB-18-PENDING-1's summary is "Require a signed-in session for every authoring page
  and API request", and its Notes say it builds the middleware the other stories consume.
  BSB-18-PENDING-2's every scenario needs `GET /auth/callback` to be reachable *without* an
  `sb_session` cookie. Neither story names the routes the gate exempts.
- **What is missing/ambiguous/contradictory:** Without a stated allow-list, one implementer may
  gate everything (which breaks sign-in) and another may exempt a broad prefix (which weakens
  NFR-002).
- **Question (if a person must decide):** None.
- **Proposed change:**
  - **BSB-18-PENDING-1:** add a Notes bullet: "`/auth/callback` is the only route the session gate
    does not apply to; any further unauthenticated route must be added here explicitly". Optionally
    add a scenario that `GET /auth/callback?error=access_denied` with no cookie reaches the
    callback handler (401 from BSB-18-PENDING-2) rather than a 302 to sign-in.
  - **BSB-18-PENDING-2:** add a Notes cross-reference to that exemption.

### Finding 7 — Cross-epic dependency note: BSB-22 expects FA-1 to tell whether another user is a current skill-builder
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-3, BSB-18-PENDING-4
- **Evidence:**
  - BSB-22 (`epics.md`), edge cases: "adding a user who is not a current skill-builder must fail
    through the FA-1 gate". FR-025: "The project owner adds another skill-builder user".
  - BSB-18-PENDING-3 checks membership only from the *requesting* user's own `cognito:groups`
    claim.
  - BSB-18-PENDING-4's `users` row holds `id`, `cognito_sub`, `email`, `name` (SK-001 §9) and
    nothing about membership.
- **What is missing/ambiguous/contradictory:** As designed, the builder cannot tell whether a
  *different* user is currently in `skill-builders`. A local record proves only that the person
  was admitted at least once. The BSB-18 stories are correct for this epic. But
  BSB-18-PENDING-4's Notes present the table as the owner reference later epics use without
  stating that limit, so BSB-22 may assume a capability FA-1 does not provide. BSB-22 is
  sequenced after BSB-18 ("Depends on FA-1"), so this is a missing dependency note, not a design
  conflict.
- **Question (if a person must decide):** None for this epic. How BSB-22 decides who is
  addable is that epic's decision.
- **Proposed change:**
  - **BSB-18-PENDING-4:** add a Notes bullet: "A `users` row proves the subject was admitted at
    least once; it does not record current `skill-builders` membership. Current membership is
    known only for the requesting user, from their own token (BSB-18-PENDING-3)."
  - **BSB-18-PENDING-3:** add the matching one-line pointer in its Notes.

## Open questions

1. **(Finding 2)** Should the builder enforce FR-141's one-hour bound itself, by refusing any
   session whose `iat` is 3600 s or more before the current time? Or should it rely on the
   platform configuring ID-token validity ≤ 60 minutes for app client `skill-builder-web`,
   recorded as an external prerequisite? Grounds: BSB-18-PENDING-3 Notes, the contract table's
   required-claims list, and SK-001 §3 ("one hour at most").
2. **(Finding 3)** Does BSB-18 own authentication for non-browser clients (a bearer ID token on the
   API gate, same validation and membership rules)? Or is CLI identity and membership BSB-37's
   concern, with BSB-18 explicitly scoped to browser sessions? Grounds: BSB-37 edge cases in
   `epics.md`, FR-116–FR-118 (MVP), SK-001 §7.

## Proposed changes

| Story | Change | Closes |
|-------|--------|--------|
| Contract table (shared by all four) | Per Q1: add `iat` to required claims plus the `iat` expiry rule, **or** add the "ID-token validity ≤ 60 min" platform-prerequisite row | F2 |
| BSB-18-PENDING-1 | Own "valid session" (signature, `iss`, `aud`, `exp`, required claims). Add scenarios for bad signature, foreign `aud` (same pool), foreign `iss`, and invalid/expired cookie on `/api/builds` (401 `authentication_required` + clearing header). Narrow out-of-scope to "a request that carries a *valid* session" | F1 |
| BSB-18-PENDING-1 | Per Q1: add the `iat`-bound scenario, or list the token-validity prerequisite in Notes | F2 |
| BSB-18-PENDING-1 | Per Q2: add bearer-token scenarios, **or** add "non-browser clients — BSB-37" to out-of-scope | F3 |
| BSB-18-PENDING-1 | Notes: local-user resolution is BSB-18-PENDING-4's, after the session and membership checks | F4 |
| BSB-18-PENDING-1 | Notes: `/auth/callback` is the only route exempt from the gate (optional callback-reachability scenario) | F6 |
| BSB-18-PENDING-2 | Per Q1: add `iat` to token fixtures (enforce option only) | F2 |
| BSB-18-PENDING-2 | Notes: cross-reference the `/auth/callback` gate exemption | F6 |
| BSB-18-PENDING-3 | Notes: token validity is BSB-18-PENDING-1's gate; this story adds the `cognito:groups` check | F1 |
| BSB-18-PENDING-3 | Per Q1: rewrite the FR-141 note to cite the builder's `iat` bound (and add `iat` to the removed-member fixtures), or name the platform token-validity prerequisite | F2 |
| BSB-18-PENDING-3 | Per Q2: add bearer-token non-member scenario (403 `not_a_member`), **or** add "non-browser clients — BSB-37" to out-of-scope | F3 |
| BSB-18-PENDING-3 | Notes: local-user resolution cross-reference | F4 |
| BSB-18-PENDING-3 | Actor "platform owner" → "platform administrator" (PRD §2) | F5 |
| BSB-18-PENDING-3 | Notes: membership is known only for the requesting user | F7 |
| BSB-18-PENDING-4 | Per Q1: add `iat` to token fixtures (enforce option only) | F2 |
| BSB-18-PENDING-4 | Per Q2: Notes on bearer-request user resolution, **or** out-of-scope pointer to BSB-37 for CLI attribution | F3 |
| BSB-18-PENDING-4 | Notes: the gate exposes `users.id` by `cognito_sub` to every admitted request. Scenario: a valid member token with no `users` row → unauthenticated (302 / 401 + clearing header), no row created | F4 |
| BSB-18-PENDING-4 | Notes: a `users` row proves past admission, not current `skill-builders` membership | F7 |

`story-map.json` changes only if Q2 is answered by adding a new story. Requirement mapping is
otherwise unchanged.

## Architecture impact

None for this epic's stories. Findings 1, 2, 4, 5, 6 and 7 are story and contract changes within
SK-001 §3 and §9 as written. Finding 2's "builder enforces `iat`" option uses claims a Cognito ID
token already carries, and the `CognitoProvider` verification SK-001 §3 already names. Finding 3
is a scope-ownership question for a person at this gate. The CLI's token-acquisition mechanism,
which SK-001 §7 leaves unspecified, belongs to whichever epic Q2 assigns it to. It does not
change any BSB-18 story as written.

## Requirement coverage check

**Yes, with caveats.** Every FR/NFR `epic-map.json` assigns to BSB-18 is exercised by at least one
story's acceptance criteria, and no two stories make contradicting claims:

| Requirement | Exercised by (ACs) | Notes |
|-------------|--------------------|-------|
| FR-001 | BSB-18-PENDING-1 (page 302 scenarios) | — |
| FR-002 | BSB-18-PENDING-2 (member sign-in, failed hosted-UI sign-in) | — |
| FR-003 | BSB-18-PENDING-2 (at sign-in), BSB-18-PENDING-3 (per request) | Distinct slices (sign-in boundary vs. later requests), consistent 403 text |
| FR-004 | BSB-18-PENDING-3 (non-member on four routes) | — |
| FR-005 | BSB-18-PENDING-4 (first sign-in, concurrent first sign-ins) | — |
| FR-138 | BSB-18-PENDING-2 (non-member, no-claim), BSB-18-PENDING-3 (re-authentication after removal) | Consistent |
| FR-141 | BSB-18-PENDING-3 (valid until `exp`, denied at `exp`) | Holds only under the unstated token-lifetime assumption (Finding 2) |
| FR-142 | BSB-18-PENDING-4 (reuse, changed email) | — |
| NFR-002 | BSB-18-PENDING-1 (no cookie on page and API; expired on page) | Invalid signature, foreign `iss`/`aud` and the API's invalid/expired-cookie case are not exercised (Finding 1) |
| NFR-003 | BSB-18-PENDING-3 (403 page text and API `not_a_member` body) | — |

"A rejected or failed sign-in creates no `users` row" is asserted in both BSB-18-PENDING-2 and
BSB-18-PENDING-4. The assertions agree (count `0`), so this is harmless duplication, not a gap.

Traceability: the PRD §6/§7 wording of all ten IDs still matches `epics.md`'s BSB-18 traceability
list and `epic-map.json`. No drift.

## Dependency-note sanity check

**Yes.** Every dependency note refers to a real story, and the notes are reciprocated:

- BSB-18-PENDING-1: "the other three stories consume" its session and middleware. BSB-18-PENDING-2,
  -3 and -4 each list a dependency on BSB-18-PENDING-1.
- BSB-18-PENDING-2: "Story BSB-18-PENDING-4 consumes this story's successful sign-in path", which
  BSB-18-PENDING-4 reciprocates ("Depends on story BSB-18-PENDING-2"). Its pointer that FR-004 and
  NFR-003 apply in BSB-18-PENDING-3 is reciprocated by BSB-18-PENDING-3's dependency on
  BSB-18-PENDING-2.
- Cross-epic references in out-of-scope (BSB-22, BSB-23 for project-level authorization) name
  real epics in `epic-map.json`.
- Missing dependency notes are covered by Findings 2 (platform token lifetime), 3 (BSB-37) and 7
  (BSB-22). No mismatched or dangling note was found.
- All story keys are still `BSB-18-PENDING-n` (not yet published by `sdlc-tracker-sync`). That is
  expected at this stage. Build order is left to `sdlc-plan-epic-sequence`.
