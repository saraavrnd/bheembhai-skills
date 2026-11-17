# Stories — BSB-39 (Access & identity)

Epic BSB-39 covers FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141, FR-142, FR-165,
NFR-002 and NFR-003. It is decomposed into the 6 stories below; every one of those 11
requirements is covered by at least one story's acceptance criteria.

**Test fixtures.** The criteria use one Cognito user pool (`https://platform-auth.example.test`,
app client `skill-builder`) with these fixed accounts:

| Account | Password | Subject | Display name | `cognito:groups` |
|---------|----------|---------|--------------|------------------|
| `alice@example.test` | `Alice-Passw0rd!` | `sub-12345` | Alice Author | `["skill-builders"]` |
| `bob@example.test` | `Bob-Passw0rd!` | `sub-67890` | Bob Builder | `["skill-builders"]` |
| `mallory@example.test` | `Mallory-Passw0rd!` | `sub-24680` | Mallory Misfit | `["platform-users"]` |
| `casey@example.test` | `Casey-Passw0rd!` | `sub-99999` | Casey Newcomer | `["skill-builders"]` |
| `dana@example.test` | `Dana-Passw0rd!` | `sub-13579` | *(no `name` claim)* | `["skill-builders"]` |

The authenticated session cookie is `builder_session`. The builder's own database is
`postgres://builder-db:5432/skillbuilder`; its `users` table is the durable system of record keyed
by the Cognito `sub`.

**Representative surfaces.** The criteria name `/builds` (the authoring build list), `/api/builds`,
`/api/me` and `/healthz` as the concrete pages and APIs used by the tests. Every other authoring
page and API route registered by this and later epics is subject to the same guard.

## Coverage summary

| Story | Requirements covered |
|-------|----------------------|
| BSB-39-PENDING-1 — Sign in with platform identity-provider credentials | FR-002 |
| BSB-39-PENDING-2 — Send unauthenticated visitors to sign-in | FR-001, NFR-002 |
| BSB-39-PENDING-3 — Restrict authoring to current skill-builders members | FR-003, FR-138, NFR-003 |
| BSB-39-PENDING-4 — Revoke a removed member's access within one hour | FR-004, FR-141 |
| BSB-39-PENDING-5 — Keep one authoring identity across sign-ins | FR-005, FR-142 |
| BSB-39-PENDING-6 — Refuse to run with platform database access | FR-165 |

---

## STORY: BSB-39-PENDING-1

**Title:** Sign in with platform identity-provider credentials
**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **to sign in with my existing platform identity-provider credentials**, so that **I can reach the skill builder without a second account or password**.

### Acceptance Criteria
Scenario: Successful sign-in with an existing platform account
Given the Cognito fixture account `alice@example.test` with password `Alice-Passw0rd!`, subject `sub-12345`, display name `Alice Author` and `cognito:groups` `["skill-builders"]`
When a visitor submits username `alice@example.test` and password `Alice-Passw0rd!` to `POST /sign-in`
Then the builder responds with HTTP 302 with `Location: /builds` and a `Set-Cookie` header containing `builder_session=` with `HttpOnly` and `SameSite=Lax`, and a follow-up `GET /builds` carrying that cookie responds with HTTP 200 and shows the text `Alice Author`

Scenario: Invalid credentials rejected
Given a visitor on the sign-in page
When the visitor submits username `alice@example.test` with password `wrong-Passw0rd!` to `POST /sign-in`
Then the builder responds with HTTP 401, the body contains the message `Sign-in failed. Check your credentials and try again.`, and the response sets no `builder_session` cookie

Scenario: Identity provider unavailable
Given the Cognito user pool at `https://platform-auth.example.test` refuses TCP connections
When the visitor submits username `alice@example.test` and password `Alice-Passw0rd!` to `POST /sign-in`
Then the builder responds with HTTP 503, the body contains the message `Identity provider unavailable. Try again later.`, and the response sets no `builder_session` cookie

Scenario: No separate credential store
Given the sign-in flow has completed for subject `sub-12345`
When the builder database's `users` table is inspected
Then it has no column named `password`, `password_hash` or `credential`, and the value `Alice-Passw0rd!` does not appear in any `users` column

### Covered requirements
- FR-002

### Out of scope
Account creation, password reset and multi-factor authentication (owned by the platform identity provider); group membership administration; sign-out.

### Notes / dependencies
The platform identity provider (Cognito user pool, separate app client) is an external prerequisite supplied outside this product. The local user record created for the subject is BSB-39-PENDING-5. A non-member's sign-in attempt is rejected by BSB-39-PENDING-3. BSB-39-PENDING-2 and BSB-39-PENDING-3 depend on the session this story issues.

---

## STORY: BSB-39-PENDING-2

**Title:** Send unauthenticated visitors to sign-in
**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **requests without a valid authenticated session rejected before any builder data is returned**, so that **nobody outside the platform can read or act on builder content**.

### Acceptance Criteria
Scenario: Unauthenticated visitor opens an authoring page
Given a visitor with no `builder_session` cookie
When the visitor requests `GET /builds`
Then the builder responds with HTTP 302 and `Location: https://platform-auth.example.test/oauth2/authorize?client_id=skill-builder&response_type=code&scope=openid%20profile%20email&redirect_uri=https%3A%2F%2Fbuilder.example.test%2Fauth%2Fcallback`, and the response body contains no build list and no build identifier

Scenario: Unauthenticated API request
Given a visitor with no `builder_session` cookie
When the visitor calls `GET /api/builds`
Then the builder responds with HTTP 401, `Content-Type: application/json`, body exactly `{"error":"authentication_required"}`, and no build records

Scenario: Expired session rejected before data
Given a request carrying the cookie `builder_session=<token issued at 08:00 UTC with expiry 08:59 UTC>`
When the visitor calls `GET /api/builds` at 09:00 UTC
Then the builder responds with HTTP 401 and body exactly `{"error":"authentication_required"}`, and returns no build records

Scenario: Guard covers every authoring route
Given a visitor with no `builder_session` cookie
When the visitor requests `GET /builds`, `GET /builds/new`, `GET /api/builds`, `POST /api/builds` and `GET /api/me`
Then `GET /builds` and `GET /builds/new` each respond with HTTP 302 to the identity-provider sign-in URL, and `GET /api/builds`, `POST /api/builds` and `GET /api/me` each respond with HTTP 401 and body exactly `{"error":"authentication_required"}`

### Covered requirements
- FR-001
- NFR-002

### Out of scope
Deciding whether a signed-in user belongs to the skill-builders group (BSB-39-PENDING-3); sign-in itself (BSB-39-PENDING-1).

### Notes / dependencies
The guard must fail closed on every page and API route, including routes added by later epics. BSB-39-PENDING-1 provides the authenticated session this story checks for. The route list in "Guard covers every authoring route" is the canonical guarded-route set for both the authentication guard (this story) and the membership guard (BSB-39-PENDING-3), so the two stories cannot drift.

---

## STORY: BSB-39-PENDING-3

**Title:** Restrict authoring to current skill-builders members
**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **authoring available only to users who are current members of the skill-builders group**, so that **only trusted people can create or change skills**.

### Acceptance Criteria
Scenario: Current member reaches authoring
Given Alice (`sub-12345`) is signed in with a token whose current `cognito:groups` claim is `["skill-builders"]`
When Alice requests `GET /builds`
Then the builder responds with HTTP 200 and renders the build list page containing the text `Alice Author`

Scenario: Non-member sign-in rejected
Given the Cognito fixture account `mallory@example.test` with password `Mallory-Passw0rd!`, subject `sub-24680` and `cognito:groups` `["platform-users"]`
When the visitor submits those credentials to `POST /sign-in`
Then the builder responds with HTTP 403, the body contains `Access is restricted to current skill-builders group members`, the response sets no `builder_session` cookie, and the `users` table has zero rows for subject `sub-24680`

Scenario: Signed-in non-member request rejected
Given a signed-in user whose token was issued while `cognito:groups` contained `skill-builders` and whose current identity-provider claim is `[]`
When the user calls `GET /api/builds`
Then the builder responds with HTTP 403 and body exactly `{"error":"membership_required"}`, and returns no build records

Scenario: Missing membership claim rejected
Given a signed-in user whose token contains no `cognito:groups` claim
When the user requests `GET /builds`
Then the builder responds with HTTP 403 and body exactly `{"error":"membership_required"}`, and renders no build data

Scenario: Membership guard covers every authoring route
Given a signed-in user whose token contains no `cognito:groups` claim
When the user requests `GET /builds`, `GET /builds/new`, `GET /api/builds`, `POST /api/builds` and `GET /api/me`
Then `GET /builds`, `GET /builds/new`, `GET /api/builds`, `POST /api/builds` and `GET /api/me` each respond with HTTP 403 and body exactly `{"error":"membership_required"}`, and none of the responses returns build data

### Covered requirements
- FR-003
- FR-138
- NFR-003

### Out of scope
The one-hour revocation window for a removed member (BSB-39-PENDING-4); administering users, groups or roles; invitations.

### Notes / dependencies
The membership claim is issued by the platform identity provider and managed by the platform administrator outside this product. This story evaluates the claim at sign-in and on a request; BSB-39-PENDING-4 owns the continuous-recheck and removal deadline. Depends on BSB-39-PENDING-1 for the sign-in flow its non-member scenario exercises. BSB-39-PENDING-5 depends on this story's member gate. The route list in "Membership guard covers every authoring route" is the same canonical guarded-route set as BSB-39-PENDING-2 and includes routes added by later epics.

---

## STORY: BSB-39-PENDING-4

**Title:** Revoke a removed member's access within one hour
**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **membership rechecked on every request and a removed member denied within one hour**, so that **revoking someone's trust takes effect without waiting for them to sign out**.

### Acceptance Criteria
Scenario: Removed member denied at the one-hour boundary
Given Alice (`sub-12345`) signed in at 08:00 UTC and the builder's last membership decision for her is from 08:00 UTC with `cognito:groups` `["skill-builders"]`
When Alice is removed from the `skill-builders` group at 08:15 UTC and calls `GET /api/builds` at 09:15 UTC without signing out
Then the builder re-reads the identity-provider claim, finds `cognito:groups` `[]`, and responds with HTTP 403 and body exactly `{"error":"membership_required"}` with no build records

Scenario: Recheck covers pages and APIs
Given Alice was removed from the `skill-builders` group 61 minutes before the request
When Alice requests `GET /builds` and then calls `GET /api/builds`
Then `GET /builds` responds with HTTP 403 and `GET /api/builds` responds with HTTP 403 and body exactly `{"error":"membership_required"}`, and neither response returns build data

Scenario: Current member keeps access across requests
Given Alice (`sub-12345`) has `cognito:groups` `["skill-builders"]` at 08:00 UTC and still has `cognito:groups` `["skill-builders"]` at 09:00 UTC
When Alice calls `GET /api/builds` at 08:00 UTC and again at 09:00 UTC
Then both requests respond with HTTP 200

Scenario: Unverifiable membership fails closed
Given Alice's last verified membership decision is from 08:00 UTC and the identity provider returns a connection error at 09:01 UTC
When Alice calls `GET /api/builds` at 09:01 UTC
Then the builder responds with HTTP 503 and body exactly `{"error":"membership_unverifiable"}`, and returns no build records

### Covered requirements
- FR-004
- FR-141

### Out of scope
Terminating a run that is already executing when the author is removed (owned by BSB-49 — Run guardrails & re-runs); group membership administration.

### Notes / dependencies
Depends on BSB-39-PENDING-3 for the membership-claim check. The one-hour limit is the maximum age of any cached membership decision; an uncached check is always allowed to be fresher. Behaviour for runs already in flight is explicitly outside this story.

---

## STORY: BSB-39-PENDING-5

**Title:** Keep one authoring identity across sign-ins
**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to recognize me as the same person in every browser and on every sign-in**, so that **my identity and membership are attributed consistently instead of being duplicated or mixed with someone else's**.

### Acceptance Criteria
Scenario: First sign-in creates one identity
Given the builder's `users` table has no row for Cognito subject `sub-12345`
When Alice (`alice@example.test`, `Alice-Passw0rd!`, subject `sub-12345`) completes sign-in and calls `GET /api/me`
Then the response is HTTP 200 with `subject` equal to `sub-12345`, `display_name` equal to `Alice Author`, `groups` equal to `["skill-builders"]`, and a `user_id` matching `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`, and the `users` table contains exactly one row for subject `sub-12345`

Scenario: Later sign-in reuses the same identity
Given Alice (`sub-12345`) is signed in in browser A and `GET /api/me` in browser A returns `user_id` value `U`
When Alice signs in again with `Alice-Passw0rd!` in a separate browser B and calls `GET /api/me` there
Then browser B's `user_id` equals `U`, and its `subject` is `sub-12345` and `display_name` is `Alice Author`

Scenario: Distinct subjects get distinct identities
Given Alice (`sub-12345`) and Bob (`bob@example.test`, `Bob-Passw0rd!`, subject `sub-67890`) have no `users` rows
When each completes sign-in and calls `GET /api/me`
Then Alice's response has `display_name` `Alice Author` and Bob's has `display_name` `Bob Builder`, and their `user_id` values differ

Scenario: Failed sign-in creates no identity
Given the builder's `users` table has no row for subject `sub-99999`
When Casey (`casey@example.test`, subject `sub-99999`) submits password `wrong-Passw0rd!` to `POST /sign-in`
Then the builder responds with HTTP 401 and sets no `builder_session` cookie, and a follow-up `GET /api/me` responds with HTTP 401

Scenario: Concurrent first sign-ins keep one identity
Given the builder's `users` table has no row for subject `sub-12345`
When two sign-ins for Alice (`sub-12345`, `Alice-Passw0rd!`) complete at the same time and each calls `GET /api/me`
Then both responses return the same `user_id`, and the `users` table contains exactly one row for subject `sub-12345`

Scenario: Sign-in without a subject claim rejected
Given a Cognito token for `alice@example.test` that contains no `sub` claim
When that token completes the sign-in callback at `GET /auth/callback`
Then the builder responds with HTTP 400, the body contains `Identity provider returned no subject claim`, sets no `builder_session` cookie, and writes no `users` row

### Covered requirements
- FR-005
- FR-142

### Out of scope
Using the identity for ownership of builds or projects (later epics); merging two existing records; editing a user's profile.

### Notes / dependencies
Depends on BSB-39-PENDING-1 for successful sign-in and on BSB-39-PENDING-3 for the member-only gate. The durable record is the builder's own `users` table keyed by the Cognito `sub`, exposed to the UI and tests through `GET /api/me`. Later epics use the returned `user_id` as the owner key.

---

## STORY: BSB-39-PENDING-6

**Title:** Refuse to run with platform database access
**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **the builder to refuse to start when its configuration points at the platform database**, so that **a misconfiguration cannot expose or corrupt platform data**.

### Acceptance Criteria
Scenario: Safe configuration serves identity only from the identity provider
Given the builder configuration contains `BUILDER_DATABASE_URL=postgres://builder-db:5432/skillbuilder` and no `PLATFORM_DATABASE_URL` or `PLATFORM_DB_*` variable
When the builder starts and Alice (`sub-12345`, `Alice Author`) signed in with `cognito:groups` `["skill-builders"]` opens `GET /builds`
Then `GET /healthz` responds with HTTP 200 and body exactly `{"status":"ok","dataSources":["builder"]}`, and `/builds` shows `Alice Author`, `sub-12345` and `skill-builders`, each matching the Cognito token claims

Scenario: Platform database configuration rejected at startup
Given the builder configuration contains `PLATFORM_DATABASE_URL=postgres://platform-db.internal:5432/platform`
When the builder starts
Then the process exits with status code 1, writes `Configuration rejected: platform database access is not permitted` to stderr, and nothing listens on port 8080

Scenario: Platform database DSN hidden in a secret reference rejected at startup
Given the builder configuration sets `BUILDER_DATABASE_SECRET=builder-db-credentials` and that secret resolves to `postgres://platform-db.internal:5432/platform`
When the builder starts
Then the process exits with status code 1, writes `Configuration rejected: platform database access is not permitted` to stderr, and nothing listens on port 8080

Scenario: Missing display-name claim still renders identity without platform data
Given Dana's Cognito token has subject `sub-13579` and `cognito:groups` `["skill-builders"]` and no `name` claim
When Dana opens `GET /builds`
Then the page responds with HTTP 200, shows `sub-13579` and `skill-builders`, shows the fallback label `Unknown name`, and contains no value read from the platform database

### Covered requirements
- FR-165

### Out of scope
Reading or writing any other platform data store; the platform's catalog import; administering the platform database's own permissions and backups.

### Notes / dependencies
The platform database is an external system owned by the platform; this story makes the builder fail closed rather than merely avoid it by convention. The `dataSources` value on `/healthz` gives the platform administrator an observable confirmation that only the builder database is in use, and the isolation guard is re-run for every later epic that adds a data-access path.
