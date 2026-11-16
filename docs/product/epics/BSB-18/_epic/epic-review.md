# Epic Review — BSB-18: Access, identity & the authoring gate

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-18-PENDING-1, BSB-18-PENDING-2, BSB-18-PENDING-3

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-18/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The requested item `SkillBuilder-2` has no Jira issue on the configured
  site. The Atlassian MCP tools were not exposed in this session, so the same site was queried
  read-only over its REST API: `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue
  does not exist or you do not have permission to see it"), and the visible projects are BEEM, BSB,
  EX, GRAP and LNPRTL — there is no `SkillBuilder` project. `PRD.md` §8 already records the same
  result and grounds the product in ADR SK-001. The epic itself was also read read-only from Jira:
  `BSB-18` (summary "Access, identity & the authoring gate", status To Do, labels FA-1/MVP, no
  sub-tasks yet). No Jira write was attempted.
- **All 3 stories in the epic**, from `stories.md` and `story-map.json` in one read each —
  BSB-18-PENDING-1, -2, -3 (full set, not a sample). The previous five-story layer split no longer
  exists; `_epic/revisions.md` Pass 4 records the re-slice to these three vertical slices.
- **`epic-map.json`** — BSB-18 maps FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141, FR-142,
  FR-165, NFR-002 and NFR-003.
- **`PRD.md`** — §5 FA-1, the §6 FR rows for those IDs and the §7 NFR rows, plus §8's source and
  naming caveat.
- **`epics.md`** — the BSB-18 section (description, functional scope, implementation guidance,
  DoD, covered requirements), and the sections of the epics that own what BSB-18's stories hand
  off: BSB-19 (build creation), BSB-21 (build page / head state) and BSB-37 (command line).
- **`docs/adr/SK-001-skill-builder.md`** — §1a (builds/branches), §3 (Cognito app client,
  `skill-builders` group, per-request claim check, no admin screen), §9 (the builder's own `users`
  table with `cognito_sub` UNIQUE) and §2a (`CognitoProvider`). This is the only committed design
  authority.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md` are
  not committed in this repo; the PDLC chain runs its design stage after planning, so ADR SK-001 is
  the design context this pass can use. No `epic-sequence.md`/`.json` exists for BSB-18; ordering
  was checked only against `epics.md`/`epic-map.json`, not computed here.

## Findings

### Finding 1 — Cross-story shared contract: the authorization middleware is scoped to "any page or API handler", which includes the public sign-in routes PENDING-1 depends on
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3
- **Evidence:**
  - BSB-18-PENDING-3, Notes / dependencies: "This story owns the single shared per-request
    authorization middleware that enforces authentication and current skill-builders membership
    **before any page or API handler runs**; the two stories are not two gates, and
    BSB-18-PENDING-1's sign-in is the only other auth path."
  - BSB-18-PENDING-1, "Current group member signs in…": the Given is a user with "no `sb_session`
    cookie", the When starts "ada selects 'Sign In' at `/sign-in`", and the builder "responds with
    HTTP 302 and a Location header of `/builds`"; its forward-walk was "`/sign-in` redirects to the
    app client's Cognito sign-in URL".
  - BSB-18-PENDING-1, "Callback without a code is refused" / "Cancelled sign-in is refused" /
    "Callback with an unverifiable token is refused": all three start from an anonymous
    `GET "/auth/callback…"` and require "a follow-up GET `/sign-in?error=…` renders the message …".
- **What is missing/ambiguous/contradictory:** PENDING-3 asserts the middleware gates *every* page
  and API handler; PENDING-1 requires an unauthenticated visitor to reach `GET /sign-in`,
  `GET /auth/callback` and the `GET /sign-in?error=…` render. Applied literally, the middleware
  intercepts `/sign-in` (redirecting back to `/sign-in` before the page can render) and
  `/auth/callback` (so no one can ever complete a sign-in), which contradicts PENDING-1. The
  Notes' phrase "PENDING-1's sign-in is the only other auth path" signals that an exemption is
  intended, but it never names the exempt routes or says the middleware skips them. Two
  implementers building these stories separately can produce two different route sets, and a
  wrong guess here propagates into every later epic that applies the middleware.
- **Proposed change:**
  - **BSB-18-PENDING-3:** In Notes, narrow the middleware's stated scope to "protected authoring
    pages and APIs" and name the public routes explicitly — "`GET /sign-in` (including its
    `?error=…` render) and `GET /auth/callback` are public entry points owned by BSB-18-PENDING-1
    and are exempt from this middleware" — then apply the middleware to every other page and API
    route.
  - **BSB-18-PENDING-1:** In Notes, state the reciprocal half: "`GET /sign-in` and
    `GET /auth/callback` are public routes and are not gated by the per-request authorization
    middleware BSB-18-PENDING-3 owns; every other page and API route is."
  - Same change for both stories: one explicit public-route allowlist shared by the two stories.

### Finding 2 — Cross-story shared contract: `/sign-in`'s error-query vocabulary is owned by PENDING-1 but PENDING-3's acceptance criteria require two states PENDING-1 never defines
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3
- **Evidence:**
  - BSB-18-PENDING-1 owns the `/sign-in` page and defines exactly one error state: "a follow-up
    GET `/sign-in?error=sign_in_incomplete` renders the message 'Sign-in was not completed. Try
    again.'" (used by its callback, cancelled-sign-in and unverifiable-token scenarios). No other
    error code or message is defined anywhere in the story.
  - BSB-18-PENDING-3, "Visitor without a session is sent to sign in": "the builder responds with
    HTTP 302 and a Location header of `/sign-in?error=session_required`, a follow-up GET
    `/sign-in?error=session_required` renders the message 'Sign in to use the builder.'"
  - BSB-18-PENDING-3, "Expired session is sent back to sign in": "a follow-up GET
    `/sign-in?error=session_expired` renders the message 'Your session expired. Sign in again.'"
- **What is missing/ambiguous/contradictory:** PENDING-3's two page-denial scenarios depend on
  PENDING-1's `/sign-in` page rendering two query values (`session_required`, `session_expired`)
  and their messages, but PENDING-1's acceptance criteria and Notes define only
  `sign_in_incomplete`. Each story looks complete on its own; compared, PENDING-1 can be built
  exactly as written and PENDING-3's scenarios will still fail because the shared error-state
  contract was never written on either side. This is the hand-off `sdlc-plan-story-review` would
  otherwise rediscover once per story.
- **Proposed change:**
  - **BSB-18-PENDING-1:** In Notes (and, if practical, the `/sign-in` scenario), define the
    complete error-query contract this page renders: `sign_in_incomplete` → "Sign-in was not
    completed. Try again."; `session_required` → "Sign in to use the builder.";
    `session_expired` → "Your session expired. Sign in again." State that these are the only
    error values the page renders and that PENDING-3's redirects use them.
  - **BSB-18-PENDING-3:** In Notes, reference PENDING-1's shared error-query contract rather than
    defining the messages locally; leave its two redirect targets, codes and messages unchanged.
  - Same change for both stories: one error vocabulary and one set of messages, owned by the story
    that owns `/sign-in`.

### Finding 3 — Cross-story precondition consistency: PENDING-2's "successful sign-in" fixtures omit the skill-builders membership that PENDING-1 makes a precondition of success
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-2
- **Evidence:**
  - BSB-18-PENDING-1, "Non-member sign-in is refused": "Then the builder responds with HTTP 403
    rendering the message 'Access is limited to members of the skill-builders group', sets no
    `sb_session` cookie, and creates no row in the `users` table." A successful sign-in therefore
    requires a current member whose token carries `"skill-builders"`.
  - BSB-18-PENDING-2, "First sign-in creates my builder account…": the Given is "a Cognito user
    whose `sub` is … and whose verified ID token carries the email …, an empty builder `users`
    table, and a `users` id sequence whose next value is 42" — no `cognito:groups` membership —
    then "When that user completes a **successful sign-in** through `/auth/callback`".
  - BSB-18-PENDING-2, "Signing in again shows the same account": same omission ("that subject
    completes another successful sign-in"); "Serving a signed-in session opens no platform
    database connection" likewise starts from "one successful sign-in through `/auth/callback`".
- **What is missing/ambiguous/contradictory:** The two stories disagree about what a
  "successful sign-in" fixture contains. PENDING-2's Scenarios 1, 2 and 4 presume success while
  omitting the group claim PENDING-1 requires; a test author who seeds those fixtures from
  PENDING-2 alone can get PENDING-1's 403 instead of the `users` row/account page the scenario
  expects. The intent is clear and safe to build as written (the phrase "successful sign-in"
  already implies PENDING-1's gate passed), so this is a fixture-wording gap, not a product
  question.
- **Proposed change:**
  - **BSB-18-PENDING-2:** In the Givens of "First sign-in creates my builder account", "Signing in
    again shows the same account", and the setup of "Serving a signed-in session opens no platform
    database connection", state that the Cognito user is a current member of the `skill-builders`
    group (e.g. "whose verified ID token carries `skill-builders` in the `cognito:groups`
    claim"), matching PENDING-1's successful-sign-in fixture.
  - **BSB-18-PENDING-1:** No change beyond Findings 1 and 2; its own successful-sign-in scenario
    already carries the group claim.

## Open questions

None. All three findings are cross-story contract or fixture wording fixes; none requires a
product decision. The questions in the previous review (route ownership, middleware ownership,
sign-in flow, administrator persona, CLI scope) were settled by the Pass 4 re-slice recorded in
`_epic/revisions.md`, and the current stories are consistent with those decisions except where the
findings above show the written contract still stops short.

## Proposed changes

`docs/product/epics/BSB-18/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-18-PENDING-1** — Notes: name `GET /sign-in` (including its `?error=…` render) and
  `GET /auth/callback` as public routes exempt from PENDING-3's middleware; define the complete
  `/sign-in` error-query contract (`sign_in_incomplete`, `session_required`, `session_expired`)
  with its three messages. Closes the PENDING-1 side of Findings 1 and 2.
- **BSB-18-PENDING-2** — Scenarios 1, 2 and the "Serving a signed-in session…" setup: state that
  the Cognito user is a current `skill-builders` member. Closes Finding 3.
- **BSB-18-PENDING-3** — Notes: scope the middleware to protected authoring pages and APIs, with
  `/sign-in` and `/auth/callback` named as public exemptions, and reference PENDING-1's shared
  error-query contract for the two page-denial redirects. Closes the PENDING-3 side of Findings 1
  and 2.

No change is proposed to `story-map.json`, `epic-map.json`, the PRD, `epics.md` or Jira;
requirement coverage is unchanged by these edits.

## Architecture impact

None. Every finding is a story-boundary, shared-contract or fixture-wording issue. The identities
and records the stories rely on already exist in ADR SK-001: the builder's own `users` table keyed
by a UNIQUE `cognito_sub` (§9) and the Cognito app client with the `skill-builders` group and
per-request claim check (§3). The server-side session store introduced by PENDING-1's session
contract is not enumerated in ADR SK-001 §9's table list, but it contradicts nothing there; it is
internal state for the later data-model artifact to capture, not a reason to hold this report.
No finding requires a design-stage change before `sdlc-plan-stories-write` (revise) applies it.

## Requirement coverage check

Complete and non-duplicated. Every requirement `epic-map.json` assigns to BSB-18 is exercised by at
least one story's acceptance criteria, and no FR/NFR is claimed by two stories in contradictory
ways:

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-001 | BSB-18-PENDING-3 | "Visitor without a session is sent to sign in" / "API request without a session is rejected" |
| FR-002 | BSB-18-PENDING-1 | "Current group member signs in and opens the builds page" (platform Cognito credentials) |
| FR-003 | BSB-18-PENDING-3 | "Current member opens the builds page" / "Removed member is denied within one hour" |
| FR-004 | BSB-18-PENDING-3 | Group claim re-read on every request; removal scenario at 11:15 |
| FR-005 | BSB-18-PENDING-2 | "First sign-in creates my builder account and shows it on my account page" |
| FR-138 | BSB-18-PENDING-1 | "Non-member sign-in is refused" (403, no session, no `users` row) |
| FR-141 | BSB-18-PENDING-3 | "Removed member is denied within one hour" |
| FR-142 | BSB-18-PENDING-2 | "Signing in again shows the same account" |
| FR-165 | BSB-18-PENDING-2 | All three isolation scenarios (no connection, no client/credential, startup refusal) |
| NFR-002 | BSB-18-PENDING-3 | Anonymous and expired-session requests refused before builder data |
| NFR-003 | BSB-18-PENDING-3 | "Removed member is denied…" / "Removed member's API request is denied" with no builder data |

The apparent overlap between PENDING-1's sign-in rejection and PENDING-3's per-request denial is a
deliberate, consistent split (same 403 message; one at sign-in per FR-138, one on every request per
FR-003/FR-004/NFR-003). No wording drift was found in the FR/NFR rows themselves. One informational
note, unchanged from the previous review: `PRD.md` §8 still says FR-165 "will be mapped on the next
epics pass" although `epic-map.json` already maps it to BSB-18 and PENDING-2 covers it — a stale
sentence in the PRD, not a story gap; no story change is proposed for it.

## Dependency-note sanity check

Mostly consistent; the two contract gaps above are the mismatches, plus the implicit fixture
dependency behind Finding 3.

- **Reciprocated and real:** PENDING-1 defines the `sb_session` session contract "that
  BSB-18-PENDING-2 and BSB-18-PENDING-3 consume"; PENDING-2 says it "Depends on
  BSB-18-PENDING-1 for the verified token and the session contract", and PENDING-3 says it
  "Depends on BSB-18-PENDING-1 for the signed-in session contract and for the minimal `/builds`
  page and GET `/api/builds`". Both directions agree.
- **No cycle and no orphan:** PENDING-1's out-of-scope defers account continuity and the account
  page to PENDING-2; PENDING-2's only dependency is PENDING-1. All referenced keys exist in
  `story-map.json`.
- **Cross-epic notes written down:** PENDING-1 names BSB-19 and BSB-21 as the owners that replace
  the minimal `/builds` page and `GET /api/builds` content, and PENDING-3 names BSB-37 as the
  command-line owner that must authenticate against this gate (with CLI authentication in its Out
  of scope). No note points at a non-existent epic or story.
- **Mismatch — Finding 1:** PENDING-3's middleware scope claims every page/API, while PENDING-1
  requires the public `/sign-in` and `/auth/callback` routes; the public-route exemption is the
  unwritten half of the shared contract.
- **Mismatch — Finding 2:** PENDING-3's page-denial redirects depend on `/sign-in` error states
  that PENDING-1 (the `/sign-in` owner) never defines.
- **Implicit dependency — Finding 3:** PENDING-2's successful-sign-in fixtures depend on
  PENDING-1's membership gate without carrying the group claim.
- Build order is intentionally not computed here — that remains `sdlc-plan-epic-sequence`'s job;
  this pass only records the dependency gaps.

---
*On approval: `docs/product/epics/BSB-18/_epic/stories.md` is updated in place for BSB-18-PENDING-1,
-2 and -3; no Jira keys exist yet for these draft stories, and no Jira write is made in this pass.
Next: `sdlc-plan-epic-sequence` once the revise pass lands, then the per-story review for any
single-story concern this epic-level pass deliberately did not raise.*
