# Epic Review — BSB-39: Access & identity

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-17 · **Stories reviewed:** BSB-39-PENDING-1, BSB-39-PENDING-2, BSB-39-PENDING-3, BSB-39-PENDING-4, BSB-39-PENDING-5, BSB-39-PENDING-6

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-39/_epic/epic-review.md`.

## Context loaded

- **Target work item `SkillBuilder-2` — unavailable.** A direct Atlassian fetch of
  `https://saraavrnd.atlassian.net/rest/api/3/issue/SkillBuilder-2` returns
  `Issue does not exist or you do not have permission to see it`; the site's project list contains
  BEEM, BSB, EX, GRAP and LNPRTL and no `SkillBuilder` project. This is the same finding already
  recorded in `docs/product/PRD.md` §8 and in `_epic/revisions.md`. This review therefore covers
  the only decomposed epic on disk, **BSB-39**, using the PRD and SK-001 as the source of scope.
- **Epic:** `BSB-39` "Access & identity" (Jira `BSB-39`, fetched; status To Do; labels FA-1, MVP).
  Loaded its summary, description (functional scope, edge cases, implementation guidance,
  Definition of Done, covered requirements, notes) and child links (no child issues yet).
- **Stories:** all 6 from `_epic/stories.md` and `_epic/story-map.json` — the full set, not a
  sample. Story keys are the `BSB-39-PENDING-*` placeholders until `sdlc-tracker-sync` publishes
  them; summaries and requirement mappings in `story-map.json` match `stories.md`.
- **PRD:** `docs/product/PRD.md` §5 FA-1, §6 FR-001–FR-005, FR-138, FR-141, FR-142, FR-165,
  §7 NFR-002/NFR-003, and §8 constraints/assumptions.
- **Design input:** `docs/adr/SK-001-skill-builder.md` §3 (separate Cognito app client,
  `skill-builders` group, `cognito:groups` checked per request, one-hour removal bound, builder
  `users` table keyed by `sub`, no platform-database access), §2/§2a (step-kit `CognitoProvider`
  token verification and AWS role scope) and §9 (the `users` table).
  There is no `docs/architecture.md`, `docs/data-model.md`, `docs/api-contracts/` or
  `docs/ui-conventions.md` in this repo yet; SK-001 is the committed design reference available to
  this pass, and the findings below are grounded in it rather than in an absent file.
- **Other epics checked for cross-epic fit:** `epic-map.json` entries for BSB-40 ("Build creation
  & skill scaffolding"), BSB-42 ("Skill editing, build state & readiness tracking") and BSB-49
  ("Run guardrails & re-runs"). No `epic-sequence.md`/`.json` exists yet, so relative build order
  cannot be confirmed in this pass — that remains `sdlc-plan-epic-sequence`'s job.

## Findings

### Finding 1 — Sign-in flow: two mutually exclusive mechanisms across the epic

- **Severity:** Blocking
- **Stories touched:** BSB-39-PENDING-1, BSB-39-PENDING-2, BSB-39-PENDING-3, BSB-39-PENDING-5
- **Evidence:**
  - BSB-39-PENDING-1 (AC "Successful sign-in with an existing platform account"):
    "When a visitor submits username `alice@example.test` and password `Alice-Passw0rd!` to
    `POST /sign-in` Then the builder responds with HTTP 302 with `Location: /builds` and a
    `Set-Cookie` header containing `builder_session=`". Its invalid-credentials and
    identity-provider-unavailable ACs also POST credentials to `/sign-in`; the invalid-credentials
    precondition says "Given a visitor on the sign-in page", but no story defines a `GET /sign-in`
    page.
  - BSB-39-PENDING-3 (AC "Non-member sign-in rejected"): "When the visitor submits those
    credentials to `POST /sign-in` Then the builder responds with HTTP 403 …".
  - BSB-39-PENDING-2 (AC "Unauthenticated visitor opens an authoring page"): "Then the builder
    responds with HTTP 302 and `Location:
    https://platform-auth.example.test/oauth2/authorize?client_id=skill-builder&response_type=code&scope=openid%20profile%20email&redirect_uri=https%3A%2F%2Fbuilder.example.test%2Fauth%2Fcallback`".
  - BSB-39-PENDING-5 (AC "Sign-in without a subject claim rejected"): "When that token completes
    the sign-in callback at `GET /auth/callback` Then the builder responds with HTTP 400 …".
  - `docs/adr/SK-001-skill-builder.md` §3: the builder is "a **separate app client** in the
    platform's existing Cognito User Pool, with its own callback URL."
- **What is missing/ambiguous/contradictory:** The epic specifies two different, incompatible
  sign-in entry points. Stories 1 and 3 define a builder-hosted username/password form that POSTs
  to `/sign-in` (a direct credential flow). Story 2 sends an unauthenticated visitor who opens an
  authoring page to Cognito's hosted-UI `/oauth2/authorize` endpoint with `response_type=code` (an
  authorization-code redirect flow), so the Story 1 form is never reached by that normal
  unauthenticated path. Story 5
  then introduces `GET /auth/callback`, which only exists in the redirect flow, and exercises only
  its *failure* path; no story owns the success path that exchanges the code, verifies the token,
  creates the session and redirects to `/builds`. A developer cannot satisfy Story 1's AC (POST
  credentials directly, set the session cookie) and Story 2's AC (redirect to the IdP authorize
  endpoint) with one default sign-in flow. The ADR's "own callback URL" points at the redirect
  flow, which makes Stories 1 and 3 the outlier.
- **Question (if a person must decide):** Which sign-in mechanism is canonical for the builder:
  (a) a builder-hosted username/password form POSTing to `/sign-in`, or (b) the Cognito hosted-UI
  authorization-code redirect through `/auth/callback`? If (b), where is the success path of the
  callback specified, and is the builder form retired?
- **Proposed change:**
  - **If the redirect flow is chosen (recommended by SK-001 §3):** rewrite BSB-39-PENDING-1 around
    `GET /builds` → 302 to the IdP authorize URL and `GET /auth/callback?code=…` → token
    validation, `Set-Cookie: builder_session=…`, 302 to `/builds`; move the invalid-credentials
    assertion to the IdP/hosted-UI stage (the builder cannot return 401 for a credential it never
    sees) and keep the 503 for an unreachable IdP; the "no separate credential store" AC can
    remain. Rewrite BSB-39-PENDING-3's non-member scenario to the callback flow (valid IdP
    authentication, then builder rejects the token's empty `cognito:groups` with 403, no session,
    no `users` row). Make BSB-39-PENDING-2 the owner of the unauthenticated redirect and
    BSB-39-PENDING-5 the owner of the callback's subject-claim failure; state the callback success
    path in BSB-39-PENDING-1.
  - **If the direct-form flow is chosen:** change BSB-39-PENDING-2's `Location` to the builder's
    own `/sign-in` page (or remove the IdP authorize URL), remove `/auth/callback` from
    BSB-39-PENDING-5 or redefine it as the form's success landing, and add the missing
    `GET /sign-in` page to BSB-39-PENDING-1.
  - **Either way:** the same URL names (`/sign-in`, `/auth/callback`, `redirect_uri`) must appear
    identically in Stories 1, 2, 3 and 5.

### Finding 2 — `/builds` and the build APIs are used as test surfaces but are not scoped or owned by this epic

- **Severity:** Advisory
- **Stories touched:** BSB-39-PENDING-1, BSB-39-PENDING-2, BSB-39-PENDING-3, BSB-39-PENDING-4, BSB-39-PENDING-6
- **Evidence:**
  - `_epic/stories.md` "Representative surfaces": "The criteria name `/builds` (the authoring
    build list), `/api/builds`, `/api/me` and `/healthz` as the concrete pages and APIs used by
    the tests."
  - BSB-39-PENDING-1 (AC 1): "a follow-up `GET /builds` carrying that cookie responds with HTTP
    200 and shows the text `Alice Author`".
  - BSB-39-PENDING-2 (AC "Guard covers every authoring route"): "When the visitor requests
    `GET /builds`, `GET /builds/new`, `GET /api/builds`, `POST /api/builds` and `GET /api/me`
    Then … `GET /api/builds`, `POST /api/builds` and `GET /api/me` each respond with HTTP 401".
  - BSB-39-PENDING-3 and -4: `GET /builds` and `GET /api/builds` are the membership-gate probes.
  - BSB-39-PENDING-6 (AC "Safe configuration"): "`/builds` shows `Alice Author`, `sub-12345` and
    `skill-builders`".
  - No story's Story or "In scope" text says it creates the `/builds` page; BSB-39-PENDING-5's
    "Out of scope" says "Using the identity for ownership of builds or projects (later epics)".
  - `epic-map.json`: BSB-40 "Build creation & skill scaffolding" owns FR-006–FR-010, FR-015–FR-017,
    FR-143 and FR-144 (create/clone/build branches/scaffold); BSB-42 owns the build page and
    readiness tracking. No BSB-39 FR covers a build list page or `POST /api/builds`.
- **What is missing/ambiguous/contradictory:** Five of the six stories make their primary
  acceptance criteria depend on a `/builds` page (and, in Story 2, on `GET /builds/new`,
  `GET /api/builds` and `POST /api/builds`) that no BSB-39 story scopes. The page is either
  BSB-40's deliverable — in which case these are cross-epic dependencies that no story's
  Notes/dependencies record — or it is unowned, in which case no story builds it. A developer
  implementing, say, BSB-39-PENDING-1 alone would have to invent a `/builds` page to make its AC
  pass, and a BSB-40 implementer would later build a different one; the same applies to the
  guard scenarios in Story 2 against routes that do not exist yet. This is an epic-boundary hole
  visible only when the stories are compared.
- **Question (if a person must decide):** Does BSB-39 deliver a minimal identity-only `/builds`
  landing page (plus placeholder routes for the future build endpoints) as the surface its own
  acceptance tests use, or do these stories depend on BSB-40's build list and build APIs — and if
  the latter, should BSB-39's page-level tests be rewritten against a surface this epic owns?
- **Proposed change:**
  - **Option A — BSB-39 owns a minimal landing page:** add to BSB-39-PENDING-1's Story/In scope a
    minimal authenticated `/builds` page that renders the signed-in identity but no build records;
    state in the stories preface that it is a BSB-39 test surface that BSB-40 later replaces.
  - **Option B — depend on BSB-40:** add "Depends on BSB-40 (Build creation & skill scaffolding)
    for `GET /builds`, `GET /builds/new`, `GET /api/builds` and `POST /api/builds`" to the Notes of
    BSB-39-PENDING-1, -2, -3, -4 and -6; rewrite page-level assertions that do not need the build
    list (identity display, membership 403) against a BSB-39-owned surface (`/api/me`) where
    possible; and scope BSB-39-PENDING-2's "Guard covers every authoring route" scenario to routes
    this epic registers, noting that BSB-40 re-runs the guard test for its routes.
  - Whichever option is chosen, the stories preface must say who owns `/builds`; currently it
    names the surface without an owner.

### Finding 3 — Session lifetime, membership freshness and the missing session-expiry surface

- **Severity:** Advisory
- **Stories touched:** BSB-39-PENDING-1, BSB-39-PENDING-2, BSB-39-PENDING-3, BSB-39-PENDING-4
- **Evidence:**
  - Jira `BSB-39` edge cases: "session or token expiry mid-edit; a membership claim that changes
    while a session is live; … an identity-provider outage during recheck." Implementation
    guidance: "Add membership-claim retrieval and per-request enforcement, with a cache TTL short
    enough to satisfy the one-hour removal bound" and "Finish with the sign-in, denial and
    session-expiry surfaces."
  - BSB-39-PENDING-1 (AC 1): sets `builder_session` with `HttpOnly` and `SameSite=Lax` only — no
    `Max-Age`, `Expires`, token lifetime or refresh rule anywhere in the story.
  - BSB-39-PENDING-2 (AC "Expired session rejected before data"): a `GET /api/builds` request with
    `builder_session=<token issued at 08:00 UTC with expiry 08:59 UTC>` at 09:00 UTC returns 401.
    It covers only the API; no page/mid-edit expiry behavior is specified.
  - BSB-39-PENDING-3 (AC "Signed-in non-member request rejected"): relies on "whose current
    identity-provider claim is `[]`" and its Notes say it "evaluates the claim at sign-in and on a
    request; BSB-39-PENDING-4 owns the continuous-recheck and removal deadline."
  - BSB-39-PENDING-4 (Notes): "The one-hour limit is the maximum age of any cached membership
    decision; an uncached check is always allowed to be fresher." Its ACs use "the builder's last
    membership decision for her is from 08:00 UTC" and "re-reads the identity-provider claim";
    an IdP connection error returns 503 `membership_unverifiable`.
  - `docs/adr/SK-001-skill-builder.md` §3: the builder "checks the `cognito:groups` claim on every
    request, not only at login, so removing someone from the group takes effect when their token
    expires (one hour at most)."
- **What is missing/ambiguous/contradictory:** Four stories depend on one session-membership
  freshness model, but they describe it differently and no story owns it end to end. Story 1
  creates the session without defining its lifetime or expiry attributes; Story 2 tests an expired
  *API* token but not a page or mid-edit expiry; Story 3 requires a request to act on the
  "current" claim; Story 4 introduces a separate cached "membership decision" that may be up to one
  hour old and re-reads the IdP at request time (with a 503 when the IdP is unreachable). The ADR's
  mechanism is token-claim verification bounded by token expiry, not a separate membership cache,
  so "current identity-provider claim" (Story 3) and "last membership decision" (Story 4) can
  disagree for a user removed within the cache window: Story 3's scenario expects an immediate 403,
  while Story 4's cache may still hold a member decision. The epic's own "session-expiry surface"
  and "session or token expiry mid-edit" edge case have no owning story.
- **Question (if a person must decide):** Which freshness model does the epic use: (a) verify the
  `cognito:groups` claim in the presented token on every request and let the token's ≤1-hour
  lifetime provide the removal bound (SK-001 §3), or (b) actively re-read membership from the
  identity provider with a separate ≤1-hour cache? And on a page request with an expired session
  mid-edit, should the builder redirect to the sign-in/IdP flow preserving the return path, or
  return a 401/403 surface?
- **Proposed change:**
  - **BSB-39-PENDING-1:** state the session's lifetime and the `builder_session` cookie's
    expiry attributes, and whether re-authentication is driven by the IdP token's `exp`.
  - **BSB-39-PENDING-2:** add the page-level expired-session scenario (e.g. `GET /builds` with an
    expired `builder_session` → 302 to the chosen sign-in entry point, preserving the return path)
    and state the same expiry source as Story 1.
  - **BSB-39-PENDING-3:** replace "current identity-provider claim" with the mechanism chosen —
    "the `cognito:groups` claim in the presented token" or "the current membership decision
    (subject to the ≤1 h freshness bound owned by BSB-39-PENDING-4)" — so its 403 scenario does
    not contradict Story 4's cache.
  - **BSB-39-PENDING-4:** if (a) is chosen, describe the "decision" as the token's claim and the
    one-hour bound as the token lifetime, not a separate cache; if (b) is chosen, define the
    cache key, TTL, refresh trigger and the authoritative source, and record that the IdP
    membership lookup is a new integration/permission not described in SK-001 §3 (to be settled in
    design before implementation).
  - **`stories.md` preface:** add one line defining the session/token model shared by all six
    stories, and add or explicitly scope the missing session-expiry surface (including the
    mid-edit case).

### Finding 4 — The authoring page's identity-display and denial contracts disagree across stories

- **Severity:** Advisory
- **Stories touched:** BSB-39-PENDING-1, BSB-39-PENDING-2, BSB-39-PENDING-3, BSB-39-PENDING-4, BSB-39-PENDING-5, BSB-39-PENDING-6
- **Evidence:**
  - Identity display: BSB-39-PENDING-1 asserts `GET /builds` "shows the text `Alice Author`";
    BSB-39-PENDING-3 asserts `GET /builds` "renders the build list page containing the text
    `Alice Author`"; BSB-39-PENDING-6 asserts `/builds` "shows `Alice Author`, `sub-12345` and
    `skill-builders`, each matching the Cognito token claims" and, for the no-name fixture, "shows
    `sub-13579` and `skill-builders`, shows the fallback label `Unknown name`". So the same page
    has three different identity contracts.
  - Display-name fallback: BSB-39-PENDING-5's `/api/me` returns `display_name` equal to
    `Alice Author` but defines no value when the `name` claim is absent; BSB-39-PENDING-6 defines
    the UI fallback `Unknown name`. `/api/me` and `/builds` could therefore disagree for Dana
    (`sub-13579`).
  - Denial surface: BSB-39-PENDING-2 sends an unauthenticated *page* request to a 302 redirect;
    BSB-39-PENDING-3 asserts a signed-in non-member's `GET /builds` returns "HTTP 403 and body
    exactly `{"error":"membership_required"}`" (a JSON body on an HTML page); BSB-39-PENDING-4
    asserts `GET /builds` returns "HTTP 403" with no body or content type. Three stories describe
    the browser-facing denial surface three different ways.
- **What is missing/ambiguous/contradictory:** The epic's user-visible contract is split across
  stories. A developer building the `/builds` page from Stories 1 and 3 would render only the
  display name; Story 6's AC would then fail because it requires the raw subject and group claims.
  A developer building the page from Story 6 would show claims that Stories 1 and 3 never asked
  for. On the denial path, Story 3 mandates a JSON body for a page request while Story 4 mandates
  a bare 403 and Story 2 mandates a redirect for the unauthenticated case, so the same page has no
  single defined behavior. Only comparing the stories reveals this; each is self-consistent.
- **Question (if a person must decide):** Should the authoring page display only the display name
  (with `Unknown name` as the fallback) and leave the raw subject/groups to `/api/me`, or is
  showing `sub` and `cognito:groups` on `/builds` intended? And should the browser-facing
  non-member denial be an HTML 403 page (with JSON reserved for `/api/*`), or the JSON error body
  Story 3 currently specifies?
- **Proposed change:**
  - **BSB-39-PENDING-1 and BSB-39-PENDING-3:** if the page is identity-only, assert the display
    name plus the `Unknown name` fallback and drop any implied subject/groups requirement; if the
    richer contract is intended, add the same "shows `sub-…` and `skill-builders`" assertion so
    Stories 1, 3 and 6 say the same thing.
  - **BSB-39-PENDING-5:** define `/api/me`'s `display_name` when the `name` claim is absent
    (return the `Unknown name` fallback, or return null and state that the UI applies the
    fallback), and add a Dana (`sub-13579`) scenario so `/api/me` and `/builds` agree.
  - **BSB-39-PENDING-6:** either reduce its `/builds` assertion to display name + `Unknown name`
    and assert subject/groups through `/api/me`, or keep the richer assertion and add it to
    Stories 1 and 3.
  - **BSB-39-PENDING-2, BSB-39-PENDING-3, BSB-39-PENDING-4:** state one page denial contract —
    e.g. browser pages return an HTML 403 "access denied" surface with the equivalent message,
    while `/api/*` returns `{"error":"membership_required"}`; keep the unauthenticated page
    redirect in Story 2 and make Story 4's page assertion use the same contract.

### Finding 5 — The membership gate's route coverage is asserted only by the authentication story

- **Severity:** Advisory
- **Stories touched:** BSB-39-PENDING-2, BSB-39-PENDING-3
- **Evidence:**
  - BSB-39-PENDING-2 (AC "Guard covers every authoring route") enumerates `GET /builds`,
    `GET /builds/new`, `GET /api/builds`, `POST /api/builds` and `GET /api/me` and asserts the
    unauthenticated behavior for each — this is the authentication guard's route-coverage test.
  - BSB-39-PENDING-3's four ACs exercise only `GET /builds` and `GET /api/builds`; it has no
    scenario covering the membership gate across the same route set, even though its Story says
    authoring is available "only to users who are current members" and its Notes say it evaluates
    the claim "at sign-in and on a request."
  - `_epic/stories.md` "Representative surfaces": "Every other authoring page and API route
    registered by this and later epics is subject to the same guard."
  - PRD NFR-003: "Every request from a signed-in user who is not a current member of the
    skill-builders group is rejected."
- **What is missing/ambiguous/contradictory:** The authentication guard is proven route-by-route;
  the membership guard is proven on only two routes. A developer could apply the membership check
  to `/builds` and `/api/builds` exactly as tested and miss `/builds/new`, `POST /api/builds`,
  `/api/me`, or the routes later epics add, while still passing every Story 3 AC. NFR-003's
  "every request" is claimed by Story 3 but not exercised across the epic's route set. This is a
  cross-story coverage gap, not a single-story missing unhappy path.
- **Question (if a person must decide):** No product decision — the fix is an acceptance-criteria
  coverage fix; the only choice is whether to reuse Story 2's route list verbatim.
- **Proposed change:**
  - **BSB-39-PENDING-3:** add a "Membership guard covers every authoring route" scenario that
    mirrors Story 2's route list and asserts HTTP 403 with body exactly
    `{"error":"membership_required"}` and no data for a signed-in non-member on each, plus the same
    "including routes added by later epics" note Story 2 carries.
  - **BSB-39-PENDING-2:** add a sentence to its "Guard covers every authoring route" AC or Notes
    that this route list is the canonical guarded-route set for both the authentication and
    membership guards, so the two stories cannot drift.

### Finding 6 — Dependency notes are one-sided and one cross-epic owner is unnamed

- **Severity:** Advisory
- **Stories touched:** BSB-39-PENDING-1, BSB-39-PENDING-2, BSB-39-PENDING-3, BSB-39-PENDING-4, BSB-39-PENDING-5
- **Evidence:**
  - BSB-39-PENDING-2 Notes: "BSB-39-PENDING-1 provides the authenticated session this story checks
    for." BSB-39-PENDING-1's Notes do not mention BSB-39-PENDING-2.
  - BSB-39-PENDING-5 Notes: "Depends on BSB-39-PENDING-1 for successful sign-in and on
    BSB-39-PENDING-3 for the member-only gate." BSB-39-PENDING-1 mentions BSB-39-PENDING-5 ("The
    local user record created for the subject is BSB-39-PENDING-5"), but BSB-39-PENDING-3's Notes
    do not mention BSB-39-PENDING-5.
  - BSB-39-PENDING-1 Notes: "A non-member's sign-in attempt is rejected by BSB-39-PENDING-3."
    BSB-39-PENDING-3's Notes do not mention BSB-39-PENDING-1, although its non-member AC posts to
    the `/sign-in` flow Story 1 defines.
  - BSB-39-PENDING-4's "Out of scope": "Terminating a run that is already executing when the
    author is removed (owned by the run guardrail epic)". `epic-map.json` identifies BSB-49 ("Run
    guardrails & re-runs") as that epic, but the note never names its key.
- **What is missing/ambiguous/contradictory:** The dependency graph is only half-written. Read in
  isolation, Story 3 looks independent of Story 1 even though its non-member scenario depends on
  Story 1's sign-in endpoint; Story 1 looks independent of Story 2 even though the session it
  issues is what Story 2 checks; and Story 3 does not acknowledge that Story 5 consumes its
  member gate. The one genuine cross-epic handoff (in-flight run termination) names no key, so a
  reader cannot confirm BSB-49 is the intended owner. None of these notes points at a
  non-existent story — the issue is reciprocity and naming, not ordering.
- **Question (if a person must decide):** No product decision — the fix is to write the existing
  dependencies down and confirm the BSB-49 handoff.
- **Proposed change:**
  - **BSB-39-PENDING-1:** add "BSB-39-PENDING-2 and BSB-39-PENDING-3 depend on the session this
    story issues" to its Notes.
  - **BSB-39-PENDING-3:** add "Depends on BSB-39-PENDING-1 for the sign-in flow its non-member
    scenario exercises" and "BSB-39-PENDING-5 depends on this story's member gate" to its Notes.
  - **BSB-39-PENDING-4:** change "the run guardrail epic" to "BSB-49 (Run guardrails & re-runs)"
    in its Out of scope (or confirm a different key if BSB-49 is not the intended owner).
  - **BSB-39-PENDING-2:** its existing note "BSB-39-PENDING-1 provides the session this story
    checks for" is correct; the missing reciprocal half belongs in Story 1. When resolving
    Finding 2, name BSB-40 explicitly for the routes it will add rather than the generic "later
    epics".
  - **BSB-39-PENDING-5:** no wording change to its own notes — its dependency on Story 3 is
    correctly stated; Story 3 gains the reciprocal note, which is what closes this mismatch.

## Open questions

1. **Sign-in mechanism (Finding 1).** Is the canonical sign-in a builder-hosted username/password
   form POSTing to `/sign-in`, or the Cognito hosted-UI authorization-code redirect through
   `/auth/callback`? If the redirect flow, where is the callback's success path specified?
2. **`/builds` ownership (Finding 2).** Does BSB-39 deliver a minimal identity-only `/builds`
   landing page and placeholder build routes, or do its stories depend on BSB-40's build list and
   build APIs? If the latter, should the page-level ACs be rewritten against a BSB-39-owned
   surface?
3. **Session and membership freshness (Finding 3).** Is the one-hour removal bound provided by the
   identity-provider token's lifetime with a per-request claim check (SK-001 §3), or by a separate
   ≤1-hour membership-decision cache? And what should an expired session do on a page mid-edit —
   redirect preserving the return path, or return a 401/403 surface?
4. **Authoring-page identity and denial contract (Finding 4).** Should `/builds` show only the
   display name (with `Unknown name` fallback) or also the raw subject and group claims, and should
   a signed-in non-member's page request render an HTML 403 page rather than the JSON error body
   Story 3 currently specifies?

## Proposed changes

Per touched story, for `sdlc-plan-stories-write` (revise mode). All changes are proposed, not
applied.

- **BSB-39-PENDING-1:** rewrite the sign-in scenarios to the chosen flow (Finding 1); add or
  explicitly depend on a minimal `/builds` landing page (Finding 2); define the `builder_session`
  lifetime/expiry attributes and the callback's success path (Finding 3); align the `/builds`
  identity assertion with the chosen page contract and `Unknown name` fallback (Finding 4); add the
  Notes sentence naming Stories 2 and 3 as dependents (Finding 6).
- **BSB-39-PENDING-2:** point the unauthenticated page redirect at the chosen sign-in entry point
  (Finding 1); scope the guarded-route scenario to routes this epic registers, or name BSB-40 and
  the placeholder-route dependency (Finding 2); add the page-level expired-session scenario and
  align the expiry source with Story 1 (Finding 3); state the page denial contract together with
  Stories 3 and 4 (Finding 4); cross-reference its route list as the canonical set for both
  guards (Finding 5); replace "later epics" with BSB-40 where applicable (Finding 6).
- **BSB-39-PENDING-3:** rewrite the non-member sign-in scenario to the chosen flow (Finding 1);
  replace "current identity-provider claim" with the chosen claim/cache mechanism (Finding 3);
  align the page denial contract and identity assertion with Stories 1/2/4/6 (Finding 4); add the
  every-authoring-route membership scenario and the later-epics note (Finding 5); add the Notes
  dependency on Story 1 and the note that Story 5 depends on its gate (Finding 6).
- **BSB-39-PENDING-4:** use the chosen `/builds` surface or record the BSB-40 dependency
  (Finding 2); define the cache key/TTL/refresh trigger or align with the token-lifetime model
  (Finding 3); align the page denial contract (Finding 4); name BSB-49 in its Out of scope
  (Finding 6).
- **BSB-39-PENDING-5:** make the `/auth/callback` subject-claim failure consistent with the chosen
  flow and give the callback's success path a home (Finding 1); define `/api/me`'s `display_name`
  for the no-name fixture and add Dana's scenario so it matches `/builds` (Finding 4); keep the
  existing dependency notes and add the reciprocal note in Story 3 (Finding 6).
- **BSB-39-PENDING-6:** make the `/builds` identity assertion match the page contract chosen in
  Finding 4, and use (or explicitly depend on) the `/builds` surface from Finding 2.
- **`_epic/stories.md` (preface):** state who owns `/builds` (Finding 2) and add one line defining
  the session/token and membership-freshness model shared by all six stories, including the
  mid-edit expiry case (Finding 3).

## Architecture impact

None. Every finding above closes by changing the stories' statement, acceptance criteria, scope or
dependency notes. The design the epic relies on already exists in `docs/adr/SK-001-skill-builder.md`
§3 (separate Cognito app client, `cognito:groups` checked per request, one-hour removal bound,
builder `users` table keyed by `sub`, no platform-database access) and §9 (the `users` table). No
new entity, field, endpoint or integration is required. If the answer to Open question 3 is a live
identity-provider membership lookup rather than token-claim verification, that integration is not
described in SK-001 §3 and would need to be settled in design before implementation; on the ADR's
existing mechanism no architecture change is needed.

## Requirement coverage check

Yes — all 11 requirements assigned to BSB-39 by `epic-map.json` are exercised by at least one
story's acceptance criteria, with no requirement claimed by zero stories:

| Requirement | Story | Exercising acceptance criteria |
|---|---|---|
| FR-001 | BSB-39-PENDING-2 | Unauthenticated authoring page and API scenarios |
| FR-002 | BSB-39-PENDING-1 | Successful sign-in, invalid credentials, IdP unavailable |
| FR-003 | BSB-39-PENDING-3 | Current member reaches authoring; non-member rejected |
| FR-004 | BSB-39-PENDING-4 | Removed member denied; recheck covers pages and APIs |
| FR-005 | BSB-39-PENDING-5 | First sign-in creates one identity; concurrent first sign-ins |
| FR-138 | BSB-39-PENDING-3 | Non-member sign-in rejected |
| FR-141 | BSB-39-PENDING-4 | Removed member denied at the one-hour boundary |
| FR-142 | BSB-39-PENDING-5 | Later sign-in reuses the same identity |
| FR-165 | BSB-39-PENDING-6 | Platform-database configuration rejected at startup; no platform data |
| NFR-002 | BSB-39-PENDING-2 | Every unauthenticated request rejected before data |
| NFR-003 | BSB-39-PENDING-3 | Signed-in non-member request rejected |

Notes:
- NFR-003 is exercised only on `/builds` and `/api/builds`, not across the route set Story 2
  enumerates — see Finding 5.
- FR-003/FR-138 (Story 3) and FR-004/FR-141 (Story 4) overlap at the per-request membership check;
  the stories claim distinct IDs but describe the check with different freshness semantics — see
  Finding 3. After the proposed boundary is written down, the slices are non-contradicting.
- No requirement-wording drift was found against the current PRD §6/§7. Two stale bookkeeping
  statements sit outside the story set: PRD §8 still says FR-165 "will be mapped on the next epics
  pass" (the `epic-map.json` entry and Story 6 already map it), and it describes the BSB project as
  holding only BSB-18–BSB-38 (the map now holds BSB-39–BSB-58). Neither changes a story's coverage.

## Dependency-note sanity check

No — the dependency notes are not fully reciprocal. Mismatches found:

- **BSB-39-PENDING-2 → BSB-39-PENDING-1:** Story 2 says Story 1 provides the session; Story 1's
  Notes do not acknowledge Story 2.
- **BSB-39-PENDING-5 → BSB-39-PENDING-3:** Story 5 depends on Story 3's member gate; Story 3's
  Notes do not mention Story 5.
- **BSB-39-PENDING-1 → BSB-39-PENDING-3:** Story 1 says non-members are rejected by Story 3;
  Story 3 does not record that its non-member scenario depends on Story 1's sign-in flow.
- **BSB-39-PENDING-3 ↔ BSB-39-PENDING-4:** reciprocal and correct (Story 3 defers the
  continuous recheck to Story 4; Story 4 depends on Story 3).
- **BSB-39-PENDING-1 ↔ BSB-39-PENDING-5:** reciprocal and correct in both directions.
- **BSB-39-PENDING-4 → "the run guardrail epic":** the owner is not named; `epic-map.json`
  identifies BSB-49 ("Run guardrails & re-runs"), but the note gives no key to confirm it.
- No dependency note refers to a story key that does not exist in this epic.
- Build order itself is not computed here; that is `sdlc-plan-epic-sequence`'s job. Note that no
  `epic-sequence.md`/`.json` exists yet, so the BSB-40 dependency in Finding 2 cannot be checked
  for sequencing position in this pass.
