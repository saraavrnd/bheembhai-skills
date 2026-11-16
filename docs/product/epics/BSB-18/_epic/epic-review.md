# Epic Review — BSB-18: Access, identity & the authoring gate

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-18-PENDING-1, BSB-18-PENDING-2, BSB-18-PENDING-3, BSB-18-PENDING-4, BSB-18-PENDING-5

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-18/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The requested item `SkillBuilder-2` has no Jira issue on the configured
  site: a read-only query of `https://saraavrnd.atlassian.net` returned HTTP 404 ("Issue does not
  exist or you do not have permission to see it"), and the site's projects are BEEM, BSB, EX, GRAP
  and LNPRTL. `PRD.md` §8 already records the same result and grounds the product in ADR SK-001.
  The Atlassian MCP tools were not exposed in this session, so the same site's REST API was
  queried read-only (no Jira writes). This review therefore uses the on-disk artifacts, as §8
  instructs.
- **All 5 stories in the epic**, from `stories.md` and `story-map.json` in one read each —
  BSB-18-PENDING-1, -2, -3, -4, -5 (full set, not a sample).
- **`epic-map.json`** — BSB-18 maps FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141,
  FR-142, FR-165, NFR-002 and NFR-003.
- **`PRD.md`** — §5 FA-1, the §6 FR rows for those IDs and the §7 NFR rows, plus §8's source and
  naming caveat.
- **`epics.md`** — the BSB-18 section (description, functional scope, dependency order, DoD,
  covered requirements, notes), and the sections of the epics this review had to check for
  legitimate ownership of what BSB-18's stories assume: BSB-19 (build creation), BSB-21 (build
  page / head state) and BSB-37 (command line).
- **`docs/adr/SK-001-skill-builder.md`** — §1a (builds/branches), §3 (Cognito app client,
  `skill-builders` group, per-request claim check, no admin screen), §9 (the builder's own `users`
  table with `cognito_sub` UNIQUE), §6b. This is the only committed design authority.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md`
  are not committed in this repo; the PDLC chain runs `sdlc-arch-design` after planning, so ADR
  SK-001 is the design context this pass can use. No `epic-sequence.md`/`.json` exists for BSB-18;
  ordering was checked only against `epics.md`/`epic-map.json` and BSB-19's own dependency note,
  not computed here.

## Findings

### Finding 1 — Epic scope boundary: the protected routes every story tests are owned by no story or epic
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3, BSB-18-PENDING-4, BSB-18-PENDING-5
- **Evidence:**
  - BSB-18-PENDING-1, "Current group member signs in": "responds with HTTP 302 to \"/builds\", and a follow-up GET \"/builds\" returns HTTP 200".
  - BSB-18-PENDING-3, "Anonymous page request is redirected…": "the visitor requests the build list page \"/builds\""; "Anonymous API request is rejected": "the client calls GET \"/api/builds\"".
  - BSB-18-PENDING-4, "Current member is admitted on each authoring request": requests "\"/builds\", \"/builds/17\" and GET \"/api/builds\" in sequence" and "each request returns HTTP 200 with the builder data for that route".
  - BSB-18-PENDING-5, "Serving requests opens no platform database connection": "a GET \"/builds\" and one local \"users\" row write".
  - `epics.md` BSB-19 notes: "Depends on access and the local user record from the access epic" — so BSB-18 is sequenced before build creation; BSB-21 owns the build page and head state. No PRD FR and no epic's functional scope names a build list page or a `GET /api/builds` endpoint.
- **What is missing/ambiguous/contradictory:** Four of the five stories lean on `/builds`, `/builds/17` and `/api/builds` as the representative protected surfaces, but no BSB-18 story creates them and no later epic claims them either. PENDING-4's "builder data for that route" and `/builds/17` additionally require a build record that BSB-18 does not create (builds arrive in BSB-19). As written, BSB-18 cannot make its own Scenario 1 / membership Scenario 1 pass without either inventing build-list functionality that belongs to a later epic, or changing what the ACs assert. Each story looks self-contained; only comparing them shows the shared unowned surface.
- **Question (if a person must decide):** Should BSB-18 deliver a minimal authenticated `/builds` landing page and `GET /api/builds` (empty/placeholder builder data) as the representative protected surfaces, or should these ACs target a route BSB-18 itself owns? And is `/builds/17` a BSB-18 test fixture or BSB-19/BSB-21's data? (also Open question 1)
- **Proposed change:**
  - **BSB-18-PENDING-1:** In Notes, name the owner of the post-sign-in `/builds` target and, if the minimal placeholder is chosen, say this epic delivers it; otherwise change the Scenario 1 follow-up to a route this epic delivers.
  - **BSB-18-PENDING-3:** In Notes, say `/builds` and `/api/builds` are BSB-18-owned minimal placeholder routes until BSB-19/BSB-21 replace them (or substitute a BSB-18-owned route in both scenarios). Add "build list content and build records (BSB-19/BSB-21)" to Out of scope.
  - **BSB-18-PENDING-4:** In Notes and Scenario 1, state that `/builds/17` and the returned builder data come from a fixture this epic seeds, or replace `/builds/17` with the minimal route. Name BSB-19/BSB-21 as the eventual data owner.
  - **BSB-18-PENDING-5:** In Notes and Scenario 2, use the same route and state it is the BSB-18 minimal placeholder.
  - Same change for all four listed stories: the route and its data owner are named in every story that uses it.

### Finding 2 — Cross-story shared authorization contract has no owner and no defined session payload
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3, BSB-18-PENDING-4
- **Evidence:**
  - BSB-18-PENDING-1 Notes: "The session contract established here is the prerequisite for BSB-18-PENDING-3 and BSB-18-PENDING-4"; its ACs assert only that the builder "sets a session cookie" — no cookie payload, server-side state, expiry or refresh rule.
  - BSB-18-PENDING-3 Notes: "Depends on BSB-18-PENDING-1 for the signed-in session **and on the shared per-request authorization middleware**" — presented as a prerequisite, not something this story creates.
  - BSB-18-PENDING-4 Notes: "Depends on BSB-18-PENDING-1 … and **shares the per-request authorization middleware with BSB-18-PENDING-3**"; "The check reads the verified token's \"cognito:groups\" claim on every request".
  - BSB-18-PENDING-3 "Expired session is rejected…": "a request whose session ID token expired one minute ago and cannot be refreshed"; PENDING-4's removal case needs a refreshed token whose claim omits the group. Neither story's session is said to carry an ID token or refresh token by PENDING-1.
  - BSB-18-PENDING-3 "Anonymous API request is rejected" pins a JSON denial body (`{"error": "Not authenticated"}`); PENDING-4's 403 scenarios say only "the message … and returns no build data", with no body shape.
  - `epics.md` BSB-18 implementation guidance step 3: "Add one shared per-request authorization middleware that enforces authentication and current skill-builders membership before any handler runs; do not duplicate the check per page."
- **What is missing/ambiguous/contradictory:** The epic expects one middleware and one session contract, but the story split has neither. PENDING-3 treats the middleware as an existing dependency, PENDING-4 says it shares it — neither owns creating it, so two implementers can build two different gates (and two different denial bodies). PENDING-1 "establishes" a session whose contents two sibling stories already depend on but never defines. This is the classic cross-story hand-off `sdlc-plan-story-review` would rediscover independently for each of the three stories.
- **Question (if a person must decide):** Should BSB-18-PENDING-3 own creating the single shared per-request authorization middleware (authentication layer) with BSB-18-PENDING-4 extending it with the membership layer, or should one story own the whole middleware? (also Open question 2)
- **Proposed change:**
  - **BSB-18-PENDING-1:** Add the session contract to the ACs or Notes: cookie name/attributes, server-side session id, the stored verified ID token and refresh token, the expiry/refresh rule the 302-on-expiry case relies on, and the fact that PENDING-3/4 implement against it.
  - **BSB-18-PENDING-3:** Change Notes from "depends on … the shared per-request authorization middleware" to "creates the shared per-request authorization middleware: the authentication layer applied to every page and API route", and define its denial contract for HTML pages versus JSON APIs (building on the existing `{"error": "Not authenticated"}`).
  - **BSB-18-PENDING-4:** Change Notes to "extends the middleware created by BSB-18-PENDING-3 with the skill-builders membership layer; authentication runs before membership; reuses that middleware's denial body for the 403". State that the two stories modify one middleware, not two.
  - Same change for all three listed stories: they name one owner of the middleware and one session contract.

### Finding 3 — Sign-in entry point contradicts across PENDING-1 and PENDING-3
- **Severity:** Blocking
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-3
- **Evidence:** BSB-18-PENDING-1 is built around "the sign-in page at \"/sign-in\"" and Notes call it "the builder's own sign-in page"; its "Invalid credentials are rejected" scenario has "Cognito's token endpoint returns HTTP 400" after the visitor submits credentials directly on `/sign-in`, while its two callback scenarios test `GET "/auth/callback"` with a `code` parameter. BSB-18-PENDING-3, "Anonymous page request is redirected…" and "Expired session is rejected…", both require "HTTP 302 to **the Cognito sign-in URL**". ADR SK-001 §3 says the builder is a "separate app client in the platform's existing Cognito User Pool, with its own callback URL" and does not settle hosted-UI redirect versus a builder-hosted form.
- **What is missing/ambiguous/contradictory:** PENDING-1 and PENDING-3 disagree on where a user actually signs in. PENDING-1 describes a builder-hosted form that submits credentials to Cognito's token endpoint and also an authorization-code callback; PENDING-3 sends unauthenticated users to a Cognito URL. Implemented literally, PENDING-3's redirect bypasses the `/sign-in` page PENDING-1 builds (making it dead code), or PENDING-1's direct-token scenarios never use `/auth/callback`. A developer cannot satisfy both stories without choosing a flow the other story does not describe.
- **Question (if a person must decide):** Which sign-in flow is canonical — the builder-hosted `/sign-in` page posting to Cognito's token endpoint, or a redirect to Cognito's hosted sign-in URL with the `/auth/callback` code exchange? PENDING-1 currently describes both and PENDING-3's 302 target depends on the answer. (also Open question 3)
- **Proposed change:**
  - **BSB-18-PENDING-1:** Restate the story and ACs around one flow. If the builder-hosted form is chosen, keep `/sign-in` for the submit scenarios and restate the two `/auth/callback` scenarios as the builder's own post-sign-in callback (or delete them if the form is a direct token call). If the hosted UI is chosen, rewrite the submit scenarios as a redirect to the Cognito sign-in URL followed by the `/auth/callback` code exchange.
  - **BSB-18-PENDING-3:** Set both 302 targets to the chosen entry point — `"/sign-in"` for the builder-hosted page, or the Cognito authorize URL for the hosted UI — and use the same wording in both scenarios.
  - Same change for both stories: they name the same sign-in entry point.

### Finding 4 — Actor vocabulary: "platform administrator" is used for builder behaviour but is not a builder role
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-3, BSB-18-PENDING-4, BSB-18-PENDING-5 (against BSB-18-PENDING-1 and -2)
- **Evidence:** BSB-18-PENDING-1 and -2 open "As a **skill author**"; BSB-18-PENDING-3, -4 and -5 open "As a **platform administrator**". `PRD.md` FA-1 says "Skill authors are already known to the platform, and the platform administrator manages membership of the externally owned skill-builders group." ADR SK-001 §3 says "Group membership is managed in Cognito by a platform admin. The skill builder has no user admin screen of its own." ADR SK-001 §9's `users` table carries no role column, and `project_members` roles (owner/member) belong to a later epic. All three "platform administrator" stories' ACs are actor-neutral in practice ("a request that carries no session cookie", "a signed-in user", "the built \"skill-builder\" container image").
- **What is missing/ambiguous/contradictory:** The same product capability (who is admitted to the builder) is described with two actor vocabularies across the epic's five stories. "Platform administrator" names the external Cognito group manager, who never uses the builder, while PENDING-3/4/5's ACs exercise the behaviour of any signed-in member. A developer could read the persona as a builder-wide admin role and add an authorization distinction the data model does not have, contradicting PENDING-1/2 where a skill author signs in.
- **Question (if a person must decide):** Are the "platform administrator" personas in BSB-18-PENDING-3/4/5 external stakeholders/operators, or a role inside the builder? ADR SK-001 §3 and §9 define no builder administrator role. (also Open question 4)
- **Proposed change:**
  - **BSB-18-PENDING-3:** Reword the Story persona to "As a skill author" (the person whose data is protected), or to an actor-free "The builder must refuse…" statement; leave the ACs unchanged.
  - **BSB-18-PENDING-4:** Same reword as BSB-18-PENDING-3; leave the ACs unchanged.
  - **BSB-18-PENDING-5:** Either keep "platform administrator" and add a Notes sentence that this is the external Cognito administrator/deployment operator and holds no builder permission, or reword to the operator who configures the deployment. Do not imply a builder role.
  - Same change for all listed stories: the epic uses one actor vocabulary, and no story implies a builder administrator role.

### Finding 5 — "Signed-in non-member" state contradicts the sign-in rejection in PENDING-1
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-1, BSB-18-PENDING-4
- **Evidence:** BSB-18-PENDING-1, "Non-member sign-in is rejected": the builder "responds with HTTP 403 … sets no session cookie, and creates no row in the \"users\" table". BSB-18-PENDING-4, "Signed-in non-member is denied": "Given a signed-in user whose verified ID token does not carry \"skill-builders\"…"; "Token without a group claim is denied": "Given a signed-in user whose verified ID token has no \"cognito:groups\" claim". The only in-epic way to reach that state is PENDING-4's own "Group removal takes effect within one hour" scenario.
- **What is missing/ambiguous/contradictory:** PENDING-1 makes a non-member session impossible at sign-in; PENDING-4's Scenarios 2 and 4 assume one already exists, and neither Given says the session came from an earlier successful sign-in followed by group removal and token refresh. A test author implementing PENDING-4 has to invent a state the system's own rules do not produce, and the fixture may be built differently in each story's test plan. FR-138 settles the intent (reject at sign-in), so this is a reachability/wording gap, not a product question.
- **Proposed change:**
  - **BSB-18-PENDING-4:** Reword the Scenarios 2 and 4 Givens so the state is produced by the epic's own path, e.g. "Given a user who signed in while a member, was later removed from the skill-builders group, and whose refreshed ID token omits \"skill-builders\"…" and "Given such a user whose refreshed ID token has no \"cognito:groups\" claim…".
  - **BSB-18-PENDING-1:** Add a Notes sentence that a signed-in non-member can only arise through PENDING-4's post-sign-in removal/refresh path, since this story rejects non-members at sign-in.
  - Same change for both stories: the non-member session state is reached the same way.

### Finding 6 — PENDING-3 claims the command-line entry point, which is BSB-37's deliverable
- **Severity:** Advisory
- **Stories touched:** BSB-18-PENDING-3 (cross-epic: BSB-37)
- **Evidence:** BSB-18-PENDING-3 Notes: "Applies to every authoring page, API route and later command-line entry point"; its Out of scope does not carve the CLI out. `epics.md` BSB-37 (FA-16, Command line & saved suites) implementation guidance step 3: "Add non-interactive authentication or token handling consistent with the authoring gate"; its Notes: "Command-line operations obey the same project membership and credential rules as the interface." Neither side names the other.
- **What is missing/ambiguous/contradictory:** PENDING-3 asserts its browser-oriented gate (session cookie, 302 to a sign-in page) extends to the CLI, while BSB-37 owns the CLI and says it adds non-interactive authentication. A cookie/redirect gate cannot serve a CLI, so the two epics could build different authentication paths for the same gate, and BSB-18's story scope silently claims part of another epic's deliverable. This is a cross-epic dependency note that is half-written, not a design conflict.
- **Question (if a person must decide):** Does the BSB-18 gate extend to the command line (making CLI authentication part of BSB-18), or does BSB-37 own non-interactive CLI authentication against the same gate? (also Open question 5)
- **Proposed change:**
  - **BSB-18-PENDING-3:** In Notes, replace "and later command-line entry point" with "page and API routes; the command-line entry point is BSB-37 (FA-16) and must authenticate against this gate rather than re-implement it". Add "command-line authentication (BSB-37)" to Out of scope. No change to BSB-37 in this pass — the dependency is written down on this side only.

## Open questions

1. **Finding 1 — route ownership.** Should BSB-18 deliver a minimal authenticated `/builds` landing page and `GET /api/builds` (empty/placeholder builder data) as the representative protected surfaces, or should those ACs target a route BSB-18 itself owns? Is `/builds/17` a BSB-18 test fixture or BSB-19/BSB-21 data?
2. **Finding 2 — middleware ownership.** Should BSB-18-PENDING-3 own creating the shared per-request authorization middleware (authentication layer) and BSB-18-PENDING-4 extend it with the membership layer, or should one story own the whole middleware?
3. **Finding 3 — sign-in flow.** Which sign-in flow is canonical: the builder-hosted `/sign-in` page posting to Cognito's token endpoint, or a redirect to Cognito's hosted sign-in URL with the `/auth/callback` code exchange? PENDING-1 currently describes both; PENDING-3's 302 target depends on the answer.
4. **Finding 4 — administrator persona.** Are the "platform administrator" personas in BSB-18-PENDING-3/4/5 external stakeholders/operators, or a role inside the builder? ADR SK-001 §3/§9 define no builder administrator role.
5. **Finding 6 — CLI scope.** Does BSB-18's gate extend to the command-line entry point (making CLI authentication part of BSB-18), or does BSB-37 own non-interactive CLI authentication against the same gate?

## Proposed changes

`docs/product/epics/BSB-18/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies them):

- **BSB-18-PENDING-1** — Notes: define the session contract (cookie, server-side session id, ID/refresh tokens, expiry/refresh) that PENDING-3/4 consume; name the owner of the post-sign-in `/builds` target; state that a signed-in non-member is only reachable via PENDING-4's removal/refresh path. Story/ACs: settle the sign-in flow and make the `/sign-in` and `/auth/callback` scenarios describe that one flow. Closes Findings 1, 2, 3, 5 (the PENDING-1 side).
- **BSB-18-PENDING-2** — No change. Its `users` upsert, `cognito_sub` UNIQUE and reuse rules already match ADR SK-001 §9 and its dependency on PENDING-1 is reciprocal.
- **BSB-18-PENDING-3** — Story persona: "As a skill author" or actor-free. Notes: it creates the shared per-request authorization middleware and owns the denial contract; `/builds` and `/api/builds` are BSB-18 minimal placeholders (or substitute a BSB-18-owned route); the CLI belongs to BSB-37. Both 302 targets become the chosen sign-in entry point. Out of scope: build-list content/build records (BSB-19/BSB-21) and CLI authentication (BSB-37). Closes Findings 1, 2, 3, 4, 6 (the PENDING-3 side).
- **BSB-18-PENDING-4** — Story persona: "As a skill author" or actor-free. Notes: extends PENDING-3's middleware with the membership layer and reuses its denial body; `/builds/17` data comes from a stated fixture or is replaced. Scenarios 2 and 4: produce the signed-in non-member state via the removal/refresh path. Closes Findings 1, 2, 4, 5 (the PENDING-4 side).
- **BSB-18-PENDING-5** — Story persona: keep "platform administrator" only with a Note that it is the external Cognito administrator/deployment operator, not a builder role (or reword to the operator). Notes/Scenario 2: use the same placeholder `/builds` route as Findings 1's resolution. Closes Findings 1 and 4 (the PENDING-5 side).

No change is proposed to `story-map.json`, `epic-map.json`, the PRD, the epics file or Jira; requirement coverage is unchanged by these edits.

## Architecture impact

None. All six findings are story-boundary, wording or dependency-note issues. The identities and records the stories rely on already exist in ADR SK-001: the builder's own `users` table keyed by a UNIQUE `cognito_sub` (§9), and the Cognito app client with the `skill-builders` group (§3). No new entity, field or integration is needed from the design stage before `sdlc-plan-stories-write` (revise) applies this report.

## Requirement coverage check

Yes — complete and non-duplicated. Every requirement `epic-map.json` assigns to BSB-18 is exercised by at least one story's acceptance criteria:

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-001 | BSB-18-PENDING-3 | Anonymous `/builds` and `/api/builds` requests are refused before data is returned |
| FR-002 | BSB-18-PENDING-1 | "Current group member signs in" uses the platform credentials and Cognito |
| FR-003 | BSB-18-PENDING-4 | "Current member is admitted…" / "Signed-in non-member is denied" |
| FR-004 | BSB-18-PENDING-4 | The claim is checked on every request, including a later `/builds` request |
| FR-005 | BSB-18-PENDING-2 | "First successful sign-in creates one local user record" |
| FR-138 | BSB-18-PENDING-1 | "Non-member sign-in is rejected" (403, no session, no `users` row) |
| FR-141 | BSB-18-PENDING-4 | "Group removal takes effect within one hour" |
| FR-142 | BSB-18-PENDING-2 | "Later sign-in reuses the existing record" |
| FR-165 | BSB-18-PENDING-5 | All three isolation scenarios (image/config, no connection, startup refusal) |
| NFR-002 | BSB-18-PENDING-3 | Anonymous and expired-session requests are rejected before builder data |
| NFR-003 | BSB-18-PENDING-4 | All signed-in non-member scenarios return 403 with no builder data |

No FR/NFR is claimed by two stories with contradicting definitions. The apparent overlap between PENDING-1's sign-in rejection and PENDING-4's per-request denial is a deliberate, consistent split (same 403 message; one at sign-in per FR-138, one on every request per FR-003/FR-004/NFR-003). No wording drift was found against the current `PRD.md` rows. One informational note: `PRD.md` §6 and §8 still say FR-165 "will be mapped on the next epics pass", but `epic-map.json` already maps it to BSB-18 and PENDING-5 covers it — a stale sentence in the PRD, not a story gap; no story change is proposed for it.

## Dependency-note sanity check

Mostly yes; three mismatches, all recorded above as Findings 1, 2 and 6.

- **Reciprocated and real:** PENDING-1's "prerequisite for PENDING-3 and PENDING-4" is matched by PENDING-3's and PENDING-4's "Depends on BSB-18-PENDING-1"; PENDING-1's reference to PENDING-2's local-user insert is matched by PENDING-2's "Depends on BSB-18-PENDING-1". All keys exist in `story-map.json`.
- **Directionally correct, no reciprocity needed:** PENDING-5 names PENDING-1 and PENDING-2 as its prerequisites for the traffic capture; neither sibling depends on PENDING-5, so their silence is not a one-sided claim.
- **Mismatch — Finding 1:** PENDING-1, -3, -4 and -5 all depend on `/builds` and `/api/builds` existing, but no story or epic owns them; the dependency is nowhere written.
- **Mismatch — Finding 2:** PENDING-3 calls the shared middleware a prerequisite and PENDING-4 says it shares it, but no story claims to create it; PENDING-1's "session contract" is likewise asserted as a prerequisite without a definition.
- **Mismatch — Finding 6:** PENDING-3 claims coverage of the "later command-line entry point" without naming BSB-37, which owns the CLI and adds its own non-interactive authentication.
- No note points at a story key that does not exist. Build order is intentionally not computed here — that remains `sdlc-plan-epic-sequence`'s job; this pass only records the dependency gaps.
