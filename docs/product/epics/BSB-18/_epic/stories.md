# Stories — BSB-18 (Access, identity & the authoring gate)

Epic BSB-18 covers FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141, FR-142, FR-165,
NFR-002 and NFR-003. Decomposed into 5 stories below; coverage of all 11 requirements verified.

> New stories use draft keys `BSB-18-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-18, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-18-PENDING-1

**Title:** Sign in with the platform identity provider
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **to sign in to the builder with the same platform credentials I already use**, so that **entering the builder does not require a second account or a separate password**.

### Acceptance Criteria

Scenario: Current group member signs in
Given a Cognito user "ada@example.com" with a valid password whose verified ID token carries "skill-builders" in the "cognito:groups" claim
When the user completes sign-in through the builder's Cognito app client at "/auth/callback"
Then the builder sets a session cookie and responds with HTTP 302 to "/builds", and a follow-up GET "/builds" returns HTTP 200

Scenario: Non-member sign-in is rejected
Given a Cognito user with valid credentials whose verified ID token does not carry "skill-builders" in the "cognito:groups" claim
When the user completes sign-in at "/auth/callback"
Then the builder responds with HTTP 403 and the message "Access is limited to members of the skill-builders group", sets no session cookie, and creates no row in the "users" table

Scenario: Invalid credentials are rejected
Given a visitor who is not signed in to Cognito
When they submit the username "ada@example.com" with an incorrect password on the platform sign-in page
Then Cognito returns an authentication error, the builder sets no session cookie, and the sign-in page shows "Sign-in failed. Check your username and password."

Scenario: Callback without a verifiable token is rejected
Given a request to "/auth/callback" with no "code" parameter, or with an ID token whose signature fails "CognitoProvider" verification
When the builder handles the callback
Then it responds with HTTP 401, sets no session cookie, and returns no builder data

### Covered requirements (traceability)
- FR-002
- FR-138

### Out of scope
Password reset, password policy and multi-factor enrolment (owned by the platform identity provider);
user, group and role administration; issuing tokens other than the platform's; local username and
password storage.

### Notes / dependencies
Depends on the external Cognito User Pool and the externally managed "skill-builders" group
(ADR SK-001 section 3). The session contract established here is the prerequisite for
BSB-18-PENDING-3 and BSB-18-PENDING-4. The local "users" row insert is detailed in
BSB-18-PENDING-2 and must not turn a rejected non-member sign-in into a successful one.

---

## STORY: BSB-18-PENDING-2

**Title:** Create and reuse one local user record per person
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to recognise me as the same local user every time I sign in**, so that **builds, projects and runs I create stay attached to one stable identity**.

### Acceptance Criteria

Scenario: First successful sign-in creates one local user record
Given a Cognito user whose "sub" is "c0ffee00-1234-4abc-9def-000000000001" and who has no row in the builder's own "users" table
When that user completes a successful sign-in through the builder
Then exactly one "users" row exists with "cognito_sub" equal to "c0ffee00-1234-4abc-9def-000000000001", and the session's local user id equals that row's "id"

Scenario: Later sign-in reuses the existing record
Given the same "cognito_sub" has already signed in once and the "users" table holds one row with "id" 42 for it
When that subject completes another successful sign-in
Then the builder reuses "users.id" 42 and the number of "users" rows with that "cognito_sub" remains 1

Scenario: Concurrent first sign-ins create no duplicate
Given two sign-in callbacks for the same "cognito_sub" arrive before any "users" row exists for it
When both callbacks complete successfully
Then the "users" table contains exactly one row for that "cognito_sub" and both sessions carry the same local user id

Scenario: Verified token without a subject claim is rejected
Given a verified ID token that has no "sub" claim
When the builder handles the sign-in callback
Then it responds with HTTP 400 and the message "Identity token has no subject", sets no session cookie, and creates no "users" row

### Covered requirements (traceability)
- FR-005
- FR-142

### Out of scope
Editing a user's profile in the builder; user administration, deactivation or deletion; copying any
profile attribute that the identity-provider token does not carry; synchronising users from the
platform database.

### Notes / dependencies
Depends on BSB-18-PENDING-1 for the verified token and session. The persisted record is the durable
system of record named in ADR SK-001 section 9: the builder's own "users" table with "cognito_sub"
UNIQUE, and it is the prerequisite every later ownership and membership relation references. The
uniqueness constraint, not application-level counting, must make the concurrent case pass.

---

## STORY: BSB-18-PENDING-3

**Title:** Block unauthenticated requests before any builder data is returned
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **every authoring page and API to refuse a request that has no valid signed-in session**, so that **builder data is never exposed to an anonymous visitor**.

### Acceptance Criteria

Scenario: Anonymous page request is redirected before data is returned
Given a request that carries no session cookie
When the visitor requests the build list page "/builds"
Then the builder responds with HTTP 302 to the Cognito sign-in URL, and the response body contains no build names, skill names or user email addresses

Scenario: Anonymous API request is rejected
Given a request that carries no session cookie
When the client calls GET "/api/builds"
Then the builder responds with HTTP 401 and the JSON body {"error": "Not authenticated"} and returns no build data

Scenario: Expired session is rejected before data is returned
Given a request whose session ID token expired one minute ago and cannot be refreshed
When the visitor requests "/builds"
Then the builder responds with HTTP 302 to the Cognito sign-in URL and the response body contains no builder data

### Covered requirements (traceability)
- FR-001
- NFR-002

### Out of scope
Sign-in itself (BSB-18-PENDING-1); membership evaluation (BSB-18-PENDING-4); the content and
layout of the sign-in page; rate limiting or account lockout.

### Notes / dependencies
Depends on BSB-18-PENDING-1 for the signed-in session and on the shared per-request authorization
middleware. Applies to every authoring page, API route and later command-line entry point; the two
routes named here are the representative checks, not an exhaustive route list. A denial must not
include builder data in headers, body or a redirect query string.

---

## STORY: BSB-18-PENDING-4

**Title:** Enforce current skill-builders membership on every request
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **the builder to re-check the "skill-builders" claim on every request**, so that **removing someone from the group stops their access even while an earlier session is still around**.

### Acceptance Criteria

Scenario: Current member is admitted on each authoring request
Given a signed-in user whose verified ID token carries "skill-builders" in the "cognito:groups" claim
When the user requests "/builds", "/builds/17" and GET "/api/builds" in sequence
Then each request returns HTTP 200 with the builder data for that route

Scenario: Signed-in non-member is denied
Given a signed-in user whose verified ID token does not carry "skill-builders" in the "cognito:groups" claim
When the user requests "/builds"
Then the builder responds with HTTP 403 and the message "Access is limited to members of the skill-builders group" and returns no build data

Scenario: Group removal takes effect within one hour
Given a user signed in at 10:00 while carrying "skill-builders" in the "cognito:groups" claim
When the user is removed from the group at 10:15 and requests "/builds" at 11:15 with a token issued after 10:15 that omits "skill-builders"
Then the builder responds with HTTP 403 and the message "Access is limited to members of the skill-builders group" and returns no build data

Scenario: Token without a group claim is denied
Given a signed-in user whose verified ID token has no "cognito:groups" claim
When the user requests GET "/api/builds"
Then the builder responds with HTTP 403 and the message "Access is limited to members of the skill-builders group" and returns no build data

### Covered requirements (traceability)
- FR-003
- FR-004
- FR-141
- NFR-003

### Out of scope
Group membership administration; token issuance and refresh internals owned by Cognito; caching
rules shorter than the token lifetime; per-page or per-role authorization beyond the group gate.

### Notes / dependencies
Depends on BSB-18-PENDING-1 for the signed-in session and shares the per-request authorization
middleware with BSB-18-PENDING-3. The check reads the verified token's "cognito:groups" claim on
every request; it must not memoise a positive membership result past the token's lifetime. The
one-hour boundary is the acceptance limit, not an invitation to cache membership indefinitely.

---

## STORY: BSB-18-PENDING-5

**Title:** Keep the builder isolated from the platform database
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **the builder to run with no access path to the platform database**, so that **builder activity can never read platform data or write into it**.

### Acceptance Criteria

Scenario: Builder image and configuration carry no platform database access
Given the built "skill-builder" container image and its deployment environment
When its dependencies and configuration are inspected
Then no platform database client library, connection string, hostname or credential is present, and the only database configuration is the builder's own database DSN

Scenario: Serving requests opens no platform database connection
Given a signed-in user whose verified ID token carries "skill-builders" in the "cognito:groups" claim
When the builder serves one complete sign-in, a GET "/builds" and one local "users" row write
Then a network capture on the builder host records zero connections to the platform database host or port

Scenario: Startup refuses a platform database configuration
Given a builder deployment whose environment supplies a platform database connection string or credential
When the builder starts
Then startup fails with the message "Builder must not be configured with platform database credentials" and the process exits with a non-zero status

### Covered requirements (traceability)
- FR-165

### Out of scope
The platform's own database administration and row-level security; the builder's own schema
migrations beyond the "users" table; mirroring or importing platform identity data; network
policy for integrations or model endpoints.

### Notes / dependencies
Depends on the builder's own database from ADR SK-001 section 9 and on the sign-in flow in
BSB-18-PENDING-1 and BSB-18-PENDING-2 for the traffic the capture observes. The builder reads and
writes only its own "users" table and other builder-owned records; the platform database is
external and unnamed to the builder. This is a negative requirement, so the proof is the absence
of a client, credential and connection rather than a positive query.
