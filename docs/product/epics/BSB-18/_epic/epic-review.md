# Epic Review — BSB-18: Access, identity & the authoring gate

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-18-PENDING-1, BSB-18-PENDING-2, BSB-18-PENDING-3

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-18/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The requested item `SkillBuilder-2` has no Jira issue on the configured
  site. The Atlassian MCP tools were not exposed in this session, so the site was queried read-only
  over its REST API: `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not exist
  or you do not have permission to see it"), and the visible projects are BEEM, BSB, EX, GRAP and
  LNPRTL — there is no `SkillBuilder` project. `PRD.md` §8 records the same result and grounds the
  product in ADR SK-001. The epic under review is `BSB-18`, the epic whose story set the preceding
  `sdlc-plan-stories-write` pass in this run wrote; it was read read-only from the same site
  (`GET /rest/api/3/issue/BSB-18` → HTTP 200, summary "Access, identity & the authoring gate",
  status To Do, labels `FA-1`/`MVP`, no sub-tasks, no issue links). No Jira write was attempted.
- **All 3 stories in the epic**, from `stories.md` and `story-map.json` in one read each —
  BSB-18-PENDING-1, BSB-18-PENDING-2, BSB-18-PENDING-3 (full set, not a sample). `story-map.json`
  maps exactly these three keys.
- **`epic-map.json`** — BSB-18 maps FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141,
  FR-142, FR-165, NFR-002 and NFR-003. `epics.md`'s BSB-18 section matches (description, functional
  scope, implementation guidance, DoD, covered requirements).
- **`PRD.md`** — §5 FA-1, the §6 rows for the eleven mapped IDs, the §7 rows for NFR-002 and
  NFR-003, and §8's source, assumptions and stale-traceability wording.
- **`epics.md`** — the BSB-18 section and the sections of the epics that own what BSB-18's stories
  hand off: BSB-19 (build creation), BSB-21 (build page / head state) and BSB-37 (command line).
- **`docs/adr/SK-001-skill-builder.md`** — §1a (builds/branches), §3 (separate Cognito app client,
  `skill-builders` group, per-request `cognito:groups` check, no admin screen), §9 (the builder's
  own `users` table with `cognito_sub` UNIQUE) and §2a (`CognitoProvider`). This is the only
  committed design authority.
- **Sibling epics' story sets** — BSB-19, BSB-20, BSB-22, BSB-23, BSB-31 and BSB-32 `stories.md`
  were read far enough to confirm the cross-epic hand-off: BSB-19/20/22/31 each state a dependency
  on BSB-18 for the signed-in skill author, the local `users` row and (BSB-22, BSB-31) the
  per-request group gate. No sibling story claims a BSB-18 surface or contradicts its contract.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md` are
  not committed in this repo; the PDLC design stage runs after planning, so ADR SK-001 is the design
  context this pass can use. No `epic-sequence.md`/`.json` exists for BSB-18; ordering was checked
  only against `epics.md`/`epic-map.json`, not computed here.
- **Prior review state.** The previous `epic-review.md`'s three findings were re-verified against
  the current text: the public-route exemption for `GET /sign-in` and `GET /auth/callback`, the
  three-value `/sign-in` error contract, and membership in PENDING-2's successful-sign-in fixtures
  are all present. This pass reports only gaps that remain in the current stories.

## Findings

### Finding 1 — Cross-story hand-off: PENDING-2 asserts `/auth/callback` outcomes that PENDING-1 owns but never specifies (`users` upsert, required `sub`/`email`, missing-`sub` refusal)
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-2
- **Evidence:**
  - BSB-18-PENDING-2, "First sign-in creates my builder account and shows it on my account page":
    "When that user completes a successful sign-in through `/auth/callback` Then exactly one
    `users` row exists with `cognito_sub` … and `id` 42."
  - BSB-18-PENDING-2, "Sign-in without a subject claim is refused": "When the builder handles the
    callback Then the builder responds with HTTP 302 … `/sign-in?error=sign_in_incomplete`, sets no
    `sb_session` cookie, creates no `users` row …"
  - BSB-18-PENDING-1, "Current group member signs in and opens the builds page": the callback
    "sets one `sb_session` cookie … responds with HTTP 302 … `/builds`", and renders
    "ada@example.com" on `/builds`. The Given names only the `cognito:groups` claim, not `sub` or
    `email`; the Notes describe the callback and the `sb_session` contract but never a `users`
    upsert or a `sub` requirement.
  - BSB-18-PENDING-2, Notes / dependencies: "Depends on BSB-18-PENDING-1 for the verified token and
    the session contract." It does not say that PENDING-1's callback invokes the upsert or performs
    the missing-`sub` refusal.
- **What is missing/ambiguous/contradictory:** `/auth/callback` is PENDING-1's surface, but
  PENDING-2's acceptance criteria assert two outcomes there that PENDING-1 never specifies. Built
  exactly as written, PENDING-1 can issue an `sb_session` for a verified token with no `sub`, and
  can complete a successful sign-in without ever creating the `users` row that PENDING-2 owns and
  every later epic (`builds.created_by` in BSB-19/20, membership in BSB-22) references. PENDING-2
  says the row must exist and a token without `sub` must be refused with no session and no row. The
  session-versus-upsert order and the required claim set are unwritten, so two implementers can
  produce a session for a subject with no local account.
- **Proposed change:**
  - **BSB-18-PENDING-1:** In Notes, state the callback's success path requires the verified ID
    token's `sub` (and the `email` it renders), calls BSB-18-PENDING-2's create-or-reuse `users`
    upsert before setting `sb_session`, and refuses a verified token missing `sub` with the same
    `sign_in_incomplete` redirect, no session and no `users` row as its other callback failures. Add
    the `sub` and `email` claims to the successful-sign-in scenario's Given so the fixture matches
    the claims the page renders.
  - **BSB-18-PENDING-2:** In Notes, state that it supplies the create-or-reuse `users` upsert and
    the missing-`sub` refusal invoked by BSB-18-PENDING-1's `/auth/callback`, and that the row is
    written before a session is issued. No acceptance-criteria change: its existing scenarios already
    assert the outcomes.
  - Same change for both stories: one documented callback sequence and one required claim set.

### Finding 2 — Cross-story shared contract: `GET /sign-in` is a 302 redirect in PENDING-1's Notes but a 200 rendered page in PENDING-1's and PENDING-3's acceptance criteria
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3
- **Evidence:**
  - BSB-18-PENDING-1, Notes / dependencies: "Sign-in is the authorization-code flow with Cognito's
    hosted sign-in page: `/sign-in` redirects to the app client's Cognito sign-in URL, Cognito
    redirects back to the builder's own callback URL `/auth/callback` …"
  - BSB-18-PENDING-1, "Current group member signs in and opens the builds page": "When ada selects
    'Sign in' at `/sign-in`, completes the Cognito hosted sign-in page …"; its three callback-failure
    scenarios each require "a follow-up GET `/sign-in?error=…` renders the message …".
  - BSB-18-PENDING-3, "Public sign-in page is not gated by the middleware": anonymous
    `GET /sign-in` "responds with HTTP 200 and does not respond with HTTP 302 to `/builds` or to
    `/sign-in?error=session_required`".
- **What is missing/ambiguous/contradictory:** PENDING-1's Notes describe `GET /sign-in` as a
  redirect to Cognito, but two PENDING-1 acceptance criteria and PENDING-3's exemption criterion
  require it to return HTTP 200 and render content, including the error message. A developer
  following the Notes builds a redirect-only route: PENDING-3's 200 assertion fails, and the
  `?error=…` message cannot render at all. A developer following the criteria builds a page but
  has no specified control that starts the Cognito flow. The entry point from `/sign-in` to
  Cognito is therefore unowned, and the two stories disagree on the route's status code.
- **Proposed change:**
  - **BSB-18-PENDING-1:** In Notes, replace "`/sign-in` redirects to the app client's Cognito
    sign-in URL" with "`GET /sign-in` renders HTTP 200 in every case, including the `?error=…`
    render, and presents a 'Sign in' control that sends the browser to the app client's Cognito
    sign-in URL; Cognito then redirects back to `GET /auth/callback` …". No acceptance-criteria
    change; the scenarios already assume the page.
  - **BSB-18-PENDING-3:** No change. Its "Public sign-in page is not gated by the middleware"
    scenario is the contract PENDING-1 must meet.
  - Same change for both stories: one statement that `GET /sign-in` is a rendered page, never a
    redirect to Cognito.

### Finding 3 — Cross-story session contract: an expired, unrefreshable session is "treated as anonymous" in PENDING-1 but gets a distinct `session_expired` denial in PENDING-3
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3
- **Evidence:**
  - BSB-18-PENDING-1, Notes / dependencies: "… a session whose ID token has expired and whose
    refresh exchange fails is treated as anonymous."
  - BSB-18-PENDING-3, "Visitor without a session is sent to sign in": a browser with no
    `sb_session` cookie gets HTTP 302 to `/sign-in?error=session_required`, and that page renders
    "Sign in to use the builder."
  - BSB-18-PENDING-3, "Expired session is sent back to sign in": a browser "whose `sb_session`
    session exists but whose stored ID token expired one minute ago and whose refresh-token exchange
    returns HTTP 400 with the error code `invalid_grant`" gets HTTP 302 to
    `/sign-in?error=session_expired`, and that page renders "Your session expired. Sign in again."
- **What is missing/ambiguous/contradictory:** The same state — an existing session whose ID token
  expired and whose refresh failed — is described as "treated as anonymous" by the session contract
  PENDING-3 consumes, but PENDING-3's criterion requires it to be distinguished from a request with
  no session and reported with a different error code and message. If PENDING-1's implementation
  discards the session on a failed refresh, the builder can no longer know the browser had a
  session and must fall back to `session_required`; PENDING-3's expired-session scenario then
  fails. The contract must say whether the expired-session state is retained for the denial
  message.
- **Proposed change:**
  - **BSB-18-PENDING-1:** In Notes, replace "treated as anonymous" with an explicit distinction: a
    request with no `sb_session` session is anonymous; a request whose session exists but whose ID
    token expired and refresh failed is unauthenticated but remains identifiable as an expired
    session, and is reported by BSB-18-PENDING-3's middleware as `session_expired` (not
    `session_required`). State that the session state needed to make that distinction is retained
    until the redirect is issued.
  - **BSB-18-PENDING-3:** No acceptance-criteria change; both denial codes and messages are already
    correct. In Notes, state that `session_expired` is used exactly for the expired/unrefreshable
    session case and `session_required` for a request with no session.
  - Same change for both stories: one session-state vocabulary shared by the session contract and
    the middleware's denials.

### Finding 4 — Epic-boundary coverage: PENDING-2's `/account` page is never named as protected or exercised against PENDING-3's middleware
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-2, BSB-18-PENDING-3
- **Evidence:**
  - BSB-18-PENDING-2, "First sign-in creates my builder account…" and "Signing in again shows the
    same account": `GET /account` is exercised only by a signed-in user; no anonymous or
    removed-member case exists.
  - BSB-18-PENDING-3's denial scenarios target `/builds` (page) and `GET /api/builds` (API); its
    "Public sign-in page…" scenario targets `/sign-in`. No scenario targets `/account`.
  - BSB-18-PENDING-3, Notes / dependencies: "every other page and API route is gated."
  - BSB-18-PENDING-2, Notes / dependencies: its only named dependency is BSB-18-PENDING-1; it does
    not say `/account` is gated by PENDING-3's middleware.
- **What is missing/ambiguous/contradictory:** `/account` is an authoring page delivered by
  PENDING-2. PENDING-3's middleware claims to gate every page and API, but the only page any
  acceptance criterion exercises is `/builds`, and PENDING-2 never records its dependence on
  PENDING-3. PENDING-2 can be built and pass every scenario while `/account` is reachable without a
  session, so FR-001 and NFR-002 are covered for that page only by an unwritten inference.
- **Proposed change:**
  - **BSB-18-PENDING-2:** In Notes, state that `GET /account` is a protected authoring page gated by
    BSB-18-PENDING-3's per-request middleware, and that an anonymous or removed-member request
    returns no email or account data. No change to the signed-in scenarios.
  - **BSB-18-PENDING-3:** Add `/account` to the representative protected-page inventory in Notes,
    or extend "Visitor without a session is sent to sign in" with an `/account` variant. Do not
    change the middleware rule itself.
  - Same change for both stories: `/account` appears in the protected-surface inventory and is
    covered by a denial assertion.

## Open questions

None. All four findings are contract, hand-off, session-state or protected-surface inventory fixes
that follow from the stories' own acceptance criteria and ADR SK-001; none requires a product
decision. The previous review's open questions remain settled by the Pass 4 re-slice recorded in
`_epic/revisions.md`.

## Proposed changes

`docs/product/epics/BSB-18/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-18-PENDING-1** — Notes: state the callback requires `sub`/`email`, calls PENDING-2's
  create-or-reuse `users` upsert before issuing `sb_session`, refuses a missing-`sub` token with
  `sign_in_incomplete`/no session, and reword `GET /sign-in` as a rendered 200 page with a "Sign in"
  control (not a redirect); distinguish an expired/unrefreshable session from an anonymous request.
  Add the `sub` and `email` claims to the successful-sign-in scenario's Given. Closes the PENDING-1
  side of Findings 1, 2 and 3.
- **BSB-18-PENDING-2** — Notes: state it supplies the users upsert and missing-`sub` refusal invoked
  by PENDING-1's `/auth/callback` before session issuance, and that `GET /account` is protected by
  PENDING-3's middleware. No acceptance-criteria change. Closes the PENDING-2 side of Findings 1 and
  4.
- **BSB-18-PENDING-3** — Notes: state the `session_expired` versus `session_required` distinction,
  and name `/account` among the protected pages (or add an `/account` denial scenario). Its
  `/sign-in` 200 assertion is unchanged and is the contract PENDING-1 must meet. Closes the
  PENDING-3 side of Findings 2, 3 and 4.

No change is proposed to `story-map.json`, `epic-map.json`, the PRD, `epics.md` or Jira;
requirement coverage is unchanged by these edits.

## Architecture impact

None. Every finding is a page, callback, session-state or protected-surface contract inside BSB-18's
own stories. The identities and records they rely on are already recorded in ADR SK-001: the
separate Cognito app client and externally managed `skill-builders` group (§3), its per-request
`cognito:groups` check (§3), and the builder's own `users` table keyed by `cognito_sub` UNIQUE
(§9). The server-side session record PENDING-1 introduces is internal state for the later
data-model artifact; nothing here needs a new entity, field, endpoint or integration, and no
design-stage pass is required before `sdlc-plan-stories-write` (revise) applies the report.

## Requirement coverage check

Complete and non-duplicated. Every requirement `epic-map.json` assigns to BSB-18 is exercised by at
least one story's acceptance criteria, and no FR/NFR is claimed by two stories in contradictory
ways:

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-001 | BSB-18-PENDING-3 | "Visitor without a session is sent to sign in" / "API request without a session is rejected" (with the `/account` caveat in Finding 4) |
| FR-002 | BSB-18-PENDING-1 | "Current group member signs in and opens the builds page" / "Incorrect password does not create a builder session" (platform Cognito credentials) |
| FR-003 | BSB-18-PENDING-3 | "Current member opens the builds page" / "Removed member is denied within one hour" |
| FR-004 | BSB-18-PENDING-3 | "Removed member is denied within one hour" (group claim re-read at 11:15 after the 11:00 refresh) |
| FR-005 | BSB-18-PENDING-2 | "First sign-in creates my builder account and shows it on my account page" |
| FR-138 | BSB-18-PENDING-1 | "Non-member sign-in is refused" (403, no session, no `users` row) |
| FR-141 | BSB-18-PENDING-3 | "Removed member is denied within one hour" |
| FR-142 | BSB-18-PENDING-2 | "Signing in again shows the same account" |
| FR-165 | BSB-18-PENDING-2 | All three isolation scenarios (no connection, no client/credential, startup refusal) |
| NFR-002 | BSB-18-PENDING-3 | "Visitor without a session…" / "API request without a session…" / "Expired session…" |
| NFR-003 | BSB-18-PENDING-3 | "Removed member is denied within one hour" / "Removed member's API request is denied" with no builder data |

The apparent overlap between PENDING-1's sign-in rejection and PENDING-3's per-request denial is a
deliberate, consistent split: the same 403 message, one at sign-in for FR-138 and one on every
request for FR-003/FR-004/NFR-003. No wording drift was found in the PRD's FR/NFR rows. One
informational note, unchanged from the previous review: `PRD.md` §8 still says FR-165 "will be
mapped on the next epics pass" although `epic-map.json` already maps it to BSB-18 and PENDING-2
covers it — a stale sentence in the PRD, not a story gap; no story change is proposed for it.

## Dependency-note sanity check

Mostly consistent; the four findings above are the remaining mismatches.

- **Reciprocated and real:** PENDING-1 defines the `sb_session` session contract "that
  BSB-18-PENDING-2 and BSB-18-PENDING-3 consume"; PENDING-2 says it "Depends on BSB-18-PENDING-1
  for the verified token and the session contract", and PENDING-3 says it "Depends on
  BSB-18-PENDING-1 for the signed-in session contract and for the minimal `/builds` page and GET
  `/api/builds`". PENDING-1's Notes reciprocate by naming both consumers and by naming
  `GET /sign-in` and `GET /auth/callback` as public routes exempt from PENDING-3's middleware.
- **No cycle and no orphan:** all referenced story keys exist in `story-map.json`; PENDING-2's only
  named in-epic dependency is PENDING-1; PENDING-3's only named in-epic dependency is PENDING-1.
- **Cross-epic notes written down:** PENDING-1 names BSB-19 and BSB-21 as the owners that replace
  the minimal `/builds` page and `GET /api/builds` content; PENDING-3 names BSB-37 as the
  command-line owner that must authenticate against this gate, with CLI authentication in its Out
  of scope. BSB-19, BSB-20, BSB-22 and BSB-31 each state their dependency on BSB-18's signed-in
  author, local `users` row and (BSB-22, BSB-31) the per-request gate. No note points at a
  non-existent epic or story; BSB-21 and BSB-37 are planned epics without decomposed stories yet,
  which is a normal cross-epic dependency.
- **Mismatch — Finding 1:** PENDING-2 asserts the `users` upsert and missing-`sub` refusal on
  PENDING-1's `/auth/callback`, but PENDING-1's callback Notes never mention either.
- **Mismatch — Finding 2:** PENDING-1's Notes say `/sign-in` redirects to Cognito; PENDING-1's and
  PENDING-3's acceptance criteria require it to render HTTP 200.
- **Mismatch — Finding 3:** PENDING-1's session contract calls an expired, unrefreshable session
  "anonymous"; PENDING-3's expired-session criterion gives it a distinct `session_expired` denial.
- **Unstated dependency — Finding 4:** PENDING-2's `GET /account` is protected only by PENDING-3's
  middleware, which PENDING-2's Notes do not name and no acceptance criterion exercises.
- Build order is intentionally not computed here — that remains `sdlc-plan-epic-sequence`'s job;
  this pass only records the dependency gaps.

---
*On approval: `docs/product/epics/BSB-18/_epic/stories.md` is updated in place for BSB-18-PENDING-1,
-2 and -3; no Jira keys exist yet for these draft stories, and no Jira write is made in this pass.
Next: `sdlc-plan-epic-sequence` once the revise pass lands, then the per-story review for any
single-story concern this epic-level pass deliberately did not raise.*
