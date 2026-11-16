# Stories — BSB-18 (Access, identity & the authoring gate)

Epic BSB-18 covers FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141, FR-142, FR-165,
NFR-002 and NFR-003. Decomposed into 3 vertical slices below; coverage of all 11 requirements
verified.

The three slices are end-to-end journeys a person completes in the builder — enter it, be
recognised again, and be kept out once access ends — not layers of one gate. The minimal
authenticated "/builds" page, the account page and GET "/api/builds" are BSB-18's own surfaces;
BSB-19 and BSB-21 later replace their content with real builds.

> New stories use draft keys `BSB-18-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-18, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-18-PENDING-1

**Title:** Sign in with my platform account and open my builds page
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **to sign in with my existing platform account and land on my builds page**, so that **I can enter the builder without a second account and immediately see where my builds will live**.

### Acceptance Criteria

Scenario: Current group member signs in and opens the builds page
Given a Cognito user "ada@example.com" with the password "Correct-Horse-Battery-1" who is a member of the "skill-builders" group and has no "sb_session" cookie
When ada selects "Sign in" at "/sign-in", completes the Cognito hosted sign-in page as "ada@example.com" with "Correct-Horse-Battery-1", and Cognito redirects to GET "/auth/callback?code=valid-code-ada" with a verified ID token whose "cognito:groups" claim carries "skill-builders"
Then the builder sets one "sb_session" cookie with "HttpOnly", "Secure" and "SameSite=Lax", responds with HTTP 302 and a Location header of "/builds", and a follow-up GET "/builds" returns HTTP 200 rendering the heading "Your builds", the text "ada@example.com" and the empty-state text "You have no builds yet."

Scenario: Non-member sign-in is refused
Given a Cognito user "bob@example.com" with the password "Correct-Horse-Battery-2" who is not a member of the "skill-builders" group and has no "sb_session" cookie
When bob selects "Sign in" at "/sign-in", completes the Cognito hosted sign-in page, and Cognito redirects to GET "/auth/callback?code=valid-code-bob" with a verified ID token whose "cognito:groups" claim does not carry "skill-builders"
Then the builder responds with HTTP 403 rendering the message "Access is limited to members of the skill-builders group", sets no "sb_session" cookie, and creates no row in the "users" table

Scenario: Incorrect password does not create a builder session
Given the Cognito user "ada@example.com" exists with the password "Correct-Horse-Battery-1"
When a visitor submits "ada@example.com" with the incorrect password "wrong-password-123" on the Cognito hosted sign-in page
Then Cognito re-renders its sign-in page with the message "Incorrect username or password.", the builder receives no GET "/auth/callback" request, and no "sb_session" cookie is set

Scenario: Callback without a code is refused
Given a GET request to "/auth/callback" that carries neither a "code" nor an "error" query parameter
When the builder handles the callback
Then the builder responds with HTTP 302 and a Location header of "/sign-in?error=sign_in_incomplete", sets no "sb_session" cookie, and a follow-up GET "/sign-in?error=sign_in_incomplete" renders the message "Sign-in was not completed. Try again."

Scenario: Cancelled sign-in is refused
Given a GET request to "/auth/callback?error=access_denied"
When the builder handles the callback
Then the builder responds with HTTP 302 and a Location header of "/sign-in?error=sign_in_incomplete", sets no "sb_session" cookie, and a follow-up GET "/sign-in?error=sign_in_incomplete" renders the message "Sign-in was not completed. Try again."

Scenario: Callback with an unverifiable token is refused
Given a GET request to "/auth/callback?code=test-code" that Cognito answers with an ID token whose signature fails "CognitoProvider" verification
When the builder handles the callback
Then the builder responds with HTTP 302 and a Location header of "/sign-in?error=sign_in_incomplete", sets no "sb_session" cookie, and a follow-up GET "/sign-in?error=sign_in_incomplete" renders the message "Sign-in was not completed. Try again."

Scenario: Signed-in member reads their empty build list from the API
Given a signed-in member with a valid "sb_session" cookie whose verified ID token carries "skill-builders", and no "builds" row owned by that member
When the client calls GET "/api/builds" with that cookie
Then the builder responds with HTTP 200 and the JSON body {"builds": []}

### Covered requirements (traceability)
- FR-002
- FR-138

### Out of scope
Password reset, password policy and multi-factor enrolment (owned by the platform identity provider);
user, group and role administration; issuing tokens other than the platform's; local username and
password storage; build creation, build records and build-list content (BSB-19, BSB-21); the
account continuity and account page of BSB-18-PENDING-2.

### Notes / dependencies
Depends on the external Cognito User Pool and the externally managed "skill-builders" group
(ADR SK-001 section 3). Sign-in is the authorization-code flow with Cognito's hosted sign-in page:
"/sign-in" redirects to the app client's Cognito sign-in URL, Cognito redirects back to the
builder's own callback URL "/auth/callback", and the builder exchanges the "code" at the token
endpoint. It never receives or stores the user's password.

The session contract that BSB-18-PENDING-2 and BSB-18-PENDING-3 consume is defined here: the
"sb_session" cookie carries only a server-side session id; the server-side session stores the
verified ID token and the Cognito refresh token; the ID token lifetime is 60 minutes and the
builder refreshes it with the refresh token before expiry; a session whose ID token has expired and
whose refresh exchange fails is treated as anonymous. A rejected sign-in sets no session.

This story delivers BSB-18's minimal authenticated "/builds" page and GET "/api/builds" returning
the empty list; they are the representative protected surfaces for this epic, not a build-list
feature. BSB-19 and BSB-21 replace their content with real build records, so no story here depends
on a build that BSB-18 does not create. Test fixtures: "ada@example.com" with
"Correct-Horse-Battery-1" (member) and "bob@example.com" with "Correct-Horse-Battery-2"
(non-member).

`GET /sign-in` (including its `?error=…` render) and `GET /auth/callback` are public routes: they
are not gated by the per-request authorization middleware BSB-18-PENDING-3 owns, and every other
page and API route is. `/sign-in` renders exactly three error values, and BSB-18-PENDING-3's
redirects use them: `sign_in_incomplete` renders "Sign-in was not completed. Try again.";
`session_required` renders "Sign in to use the builder."; `session_expired` renders "Your session
expired. Sign in again." No other error value is rendered, and an unrecognised `error` value
renders the page with no message.

Because this story refuses a non-member at sign-in, a signed-in non-member can only exist after
BSB-18-PENDING-3's group-removal and token-refresh path; no scenario in this story creates one.

---

## STORY: BSB-18-PENDING-2

**Title:** Keep my builder account stable in the builder's own database
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to keep one stable account for me in its own database and never touch the platform database**, so that **the work I create later stays attributed to me and my platform data is never copied into the builder**.

### Acceptance Criteria

Scenario: First sign-in creates my builder account and shows it on my account page
Given a Cognito user who is a current member of the "skill-builders" group, whose "sub" is "c0ffee00-1234-4abc-9def-000000000001", whose verified ID token carries the email "ada@example.com" and carries "skill-builders" in the "cognito:groups" claim, an empty builder "users" table, and a "users" id sequence whose next value is 42
When that user completes a successful sign-in through "/auth/callback"
Then exactly one "users" row exists with "cognito_sub" "c0ffee00-1234-4abc-9def-000000000001" and "id" 42, and GET "/account" returns HTTP 200 rendering "ada@example.com" and "Builder account 42"

Scenario: Signing in again shows the same account
Given the "users" table holds one row with "id" 42 and "cognito_sub" "c0ffee00-1234-4abc-9def-000000000001", GET "/account" in an earlier browser rendered "Builder account 42", and that Cognito user is a current member of the "skill-builders" group whose verified ID token carries "skill-builders" in the "cognito:groups" claim
When that subject completes another successful sign-in in a second browser and requests "/account"
Then the second browser's GET "/account" returns HTTP 200 rendering "Builder account 42", and the "users" table still contains exactly one row for that "cognito_sub"

Scenario: Sign-in without a subject claim is refused
Given a visitor completing "/auth/callback" for whom Cognito returns a verified ID token that has no "sub" claim
When the builder handles the callback
Then the builder responds with HTTP 302 and a Location header of "/sign-in?error=sign_in_incomplete", sets no "sb_session" cookie, creates no "users" row, and a follow-up GET "/sign-in?error=sign_in_incomplete" renders the message "Sign-in was not completed. Try again."

Scenario: Serving a signed-in session opens no platform database connection
Given the builder deployed with only its own database DSN and the "skill-builder" container image, and a Cognito user who is a current member of the "skill-builders" group whose verified ID token carries "skill-builders" in the "cognito:groups" claim
When the builder serves one successful sign-in through "/auth/callback", one GET "/builds" and one GET "/account"
Then a network capture on the builder host records zero connections to the platform database host or port

Scenario: Builder image carries no platform database client or credential
Given the built "skill-builder" container image and its deployment environment
When its dependency manifest and environment variables are inspected
Then no platform database client library, connection string, hostname or credential is present, and the only database configuration is the builder's own DSN

Scenario: Startup refuses a platform database configuration
Given a builder deployment whose environment supplies a platform database connection string or credential
When the builder starts
Then startup fails with the message "Builder must not be configured with platform database credentials", the process exits with a non-zero status, and GET "/sign-in" is not served

### Covered requirements (traceability)
- FR-005
- FR-142
- FR-165

### Out of scope
Editing a user's profile in the builder; user administration, deactivation or deletion; copying any
profile attribute that the identity-provider token does not carry; synchronising users from the
platform database; the platform's own database administration and row-level security; builder schema
migrations beyond the "users" table; network policy for integrations or model endpoints.

### Notes / dependencies
Depends on BSB-18-PENDING-1 for the verified token and the session contract. The persisted record is
the durable system of record named in ADR SK-001 section 9: the builder's own "users" table with
"cognito_sub" UNIQUE, and it is the prerequisite every later ownership and membership relation
references. The uniqueness constraint, not application-level counting, must make the reuse case
pass.

GET "/account" is BSB-18's minimal account page, delivered by this story. It renders the email and
the local "users.id" from that row, which is the user-visible face of the stable local identity;
the id is a reference, not a permission, and the "users" table carries no role column. Later epics
may extend the page, but no later epic manages users.

FR-165 is a negative requirement: the proof is the absence of a client, credential and connection —
observed at runtime, in the image, and by the startup refusal — rather than a positive query. The
platform database is external and unnamed to the builder.

---

## STORY: BSB-18-PENDING-3

**Title:** Only current members can open builder pages
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to refuse anyone who is not signed in or has left the skill-builders group**, so that **only current members can see builder pages and my work stays inside the team**.

### Acceptance Criteria

Scenario: Current member opens the builds page
Given a user signed in with a valid "sb_session" cookie whose verified ID token carries "skill-builders" in the "cognito:groups" claim
When the user requests "/builds"
Then the builder responds with HTTP 200 rendering "Your builds" and "You have no builds yet."

Scenario: Public sign-in page is not gated by the middleware
Given a browser that carries no "sb_session" cookie
When it requests GET "/sign-in"
Then the builder responds with HTTP 200 and does not respond with HTTP 302 to "/builds" or to "/sign-in?error=session_required"

Scenario: Visitor without a session is sent to sign in
Given a browser that carries no "sb_session" cookie
When it requests the page "/builds"
Then the builder responds with HTTP 302 and a Location header of "/sign-in?error=session_required", a follow-up GET "/sign-in?error=session_required" renders the message "Sign in to use the builder.", and both response bodies contain no build names, skill names or email addresses

Scenario: API request without a session is rejected
Given a request that carries no "sb_session" cookie
When the client calls GET "/api/builds"
Then the builder responds with HTTP 401 and the JSON body {"error": "Not authenticated"} and returns no build data

Scenario: Expired session is sent back to sign in
Given a browser whose "sb_session" session exists but whose stored ID token expired one minute ago and whose refresh-token exchange returns HTTP 400 with the error code "invalid_grant"
When it requests "/builds"
Then the builder responds with HTTP 302 and a Location header of "/sign-in?error=session_expired", a follow-up GET "/sign-in?error=session_expired" renders the message "Your session expired. Sign in again.", and both response bodies contain no build names or email addresses

Scenario: Removed member is denied within one hour
Given a user signed in at 10:00 while the "cognito:groups" claim carried "skill-builders", removed from the group at 10:15, and holding a refreshed ID token issued at 11:00 that omits "skill-builders"
When the user requests "/builds" at 11:15
Then the builder responds with HTTP 403 rendering "Access is limited to members of the skill-builders group" and the response body contains no build names or email addresses

Scenario: Removed member's API request is denied
Given a user who signed in while a member and was later removed from the skill-builders group, whose refreshed ID token has no "cognito:groups" claim
When the client calls GET "/api/builds" with that session
Then the builder responds with HTTP 403 and the JSON body {"error": "Access is limited to members of the skill-builders group"} and returns no build data

### Covered requirements (traceability)
- FR-001
- FR-003
- FR-004
- FR-141
- NFR-002
- NFR-003

### Out of scope
Signing in (BSB-18-PENDING-1); creating the local user record and the account page
(BSB-18-PENDING-2); group membership administration; token issuance and refresh internals owned by
Cognito; caching rules shorter than the token lifetime; per-page or per-role authorization beyond
the group gate; build-list content and build records (BSB-19, BSB-21); command-line authentication
(BSB-37); rate limiting or account lockout.

### Notes / dependencies
Depends on BSB-18-PENDING-1 for the signed-in session contract and for the minimal "/builds" page
and GET "/api/builds" this story protects.

This story owns the single shared per-request authorization middleware that enforces authentication
and current skill-builders membership on protected authoring pages and APIs before any handler runs.
`GET /sign-in` (including its `?error=…` render) and `GET /auth/callback` are public entry points
owned by BSB-18-PENDING-1 and are exempt from this middleware; every other page and API route is
gated. The two stories are not two gates, and BSB-18-PENDING-1's sign-in is the only other auth
path. "Public sign-in page is not gated by the middleware" is the executable proof of that
exemption. Both denial contracts stated in the scenarios are this middleware's contract.

The two page-denial redirects use the `/sign-in` error-query contract owned by BSB-18-PENDING-1
rather than a vocabulary defined here: `session_required` and `session_expired` are two of the
three error values that page specifies, and the redirect targets, codes and messages in the
scenarios above are exactly that contract. This story neither adds nor renames an error value, so
there is one code-to-message mapping, owned by the story that owns `/sign-in`. BSB-37's
command-line entry point must authenticate against this same gate rather than re-implement it;
command-line authentication is out of scope here.

The check reads the verified token's "cognito:groups" claim on every request and must not memoise a
positive membership result past the token's lifetime; the one-hour boundary is the acceptance limit,
not an invitation to cache membership indefinitely. A signed-in non-member is reached only through
the group-removal and token-refresh path described in the two removal scenarios. A denial must not
include builder data in headers, body or a redirect query string.
