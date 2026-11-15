# Stories — BSB-18 (Access, identity & the authoring gate)

Source: Jira epic **BSB-18** — *Access, identity & the authoring gate* (feature area FA-1, release
MVP, labels FA-1, MVP) and the requirement IDs mapped to it in `docs/product/epic-map.json`.

Epic BSB-18 covers 10 requirements. They decompose into the 4 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-001 | BSB-18-PENDING-1 |
| FR-002 | BSB-18-PENDING-2 |
| FR-003 | BSB-18-PENDING-2 |
| FR-004 | BSB-18-PENDING-3 |
| FR-005 | BSB-18-PENDING-4 |
| FR-138 | BSB-18-PENDING-2 |
| FR-141 | BSB-18-PENDING-3 |
| FR-142 | BSB-18-PENDING-4 |
| NFR-002 | BSB-18-PENDING-1 |
| NFR-003 | BSB-18-PENDING-3 |

## Session and identity contract (test fixture constants)

Every scenario below uses these exact values. They are the builder's configuration for the test
deployment; the Cognito User Pool, its signing keys and the `skill-builders` group are supplied by
the platform, and the builder is configured with the client id and hosted-UI domain named here.

| Item | Exact value |
|------|-------------|
| Builder public URL | `https://builder.skillbuilder.internal` |
| Cognito hosted-UI domain | `https://skill-builder.auth.eu-west-1.amazoncognito.com` |
| Cognito app client id | `skill-builder-web` |
| Cognito redirect URI | `https://builder.skillbuilder.internal/auth/callback` |
| Sign-in redirect target (the `Location` header) | `https://skill-builder.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=skill-builder-web&response_type=code&scope=openid+profile+email&redirect_uri=https%3A%2F%2Fbuilder.skillbuilder.internal%2Fauth%2Fcallback` |
| Cognito token endpoint | `https://skill-builder.auth.eu-west-1.amazoncognito.com/oauth2/token` |
| Cognito issuer (`iss` claim) | `https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample` |
| Session cookie name | `sb_session` |
| Session format | A Cognito ID token JWT: three dot-separated base64url segments `header.payload.signature`, RS256-signed with the User Pool's signing key. The builder requires the claims `sub`, `email`, `name`, `cognito:groups`, `iss`, `aud` and `exp`, with `iss` equal to the issuer above and `aud` equal to `skill-builder-web`. The session expires when `exp` is at or before the current time. |
| Session cookie attributes on success | `Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=3600` |
| Expired-session clearing header | `Set-Cookie: sb_session=; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; Secure; SameSite=Lax` |

---

## STORY: BSB-18-PENDING-1

**Summary:** Require a signed-in session for every authoring page and API request
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to send me to sign in whenever I have no valid session**, so that **no authoring page or builder data is exposed to an unauthenticated visitor**.

### Acceptance Criteria

#### Scenario: Authoring page refuses an unauthenticated visitor
Given the builder is running at `https://builder.skillbuilder.internal` with Cognito app client `skill-builder-web`
And the visitor has no `sb_session` cookie
When the visitor sends `GET https://builder.skillbuilder.internal/builds`
Then the builder responds with HTTP status 302
And the `Location` response header value is exactly `https://skill-builder.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=skill-builder-web&response_type=code&scope=openid+profile+email&redirect_uri=https%3A%2F%2Fbuilder.skillbuilder.internal%2Fauth%2Fcallback`
And the response body is exactly 0 bytes
And the response contains no `Set-Cookie` header

#### Scenario: Authoring API refuses an unauthenticated request
Given the build store contains three builds with ids `1`, `2` and `3` and names `Alpha`, `Beta` and `Gamma`
When a visitor with no `sb_session` cookie sends `GET https://builder.skillbuilder.internal/api/builds` with the header `Accept: application/json`
Then the builder responds with HTTP status 401
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"authentication_required","message":"Sign in to use the skill builder."}}`
And the response body contains none of the strings `Alpha`, `Beta` or `Gamma`

#### Scenario: Expired session is treated as unauthenticated
Given the builder's Cognito issuer is `https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample` and its app client id is `skill-builder-web`
And the visitor's `sb_session` cookie holds a Cognito ID token JWT with claims `sub`=`a1b2c3d4-0000-0000-0000-000000000001`, `email`=`ada@example.com`, `name`=`Ada Lovelace`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T10:00:00Z`, signed RS256 with the User Pool's test signing key
And the current time is `2026-11-15T10:01:00Z`
When the visitor sends `GET https://builder.skillbuilder.internal/builds` carrying that `sb_session` cookie
Then the builder responds with HTTP status 302
And the `Location` response header value is exactly `https://skill-builder.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=skill-builder-web&response_type=code&scope=openid+profile+email&redirect_uri=https%3A%2F%2Fbuilder.skillbuilder.internal%2Fauth%2Fcallback`
And the response carries the header `Set-Cookie: sb_session=; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; Secure; SameSite=Lax`
And the response body is exactly 0 bytes

#### Scenario: Every authoring page route enforces the session gate
Given the builder's authoring page routes are `/builds`, `/builds/1`, `/builds/1/files` and `/projects/1/settings` under `https://builder.skillbuilder.internal`
When a visitor with no `sb_session` cookie sends `GET` to each of those four routes
Then each response has HTTP status 302
And each response's `Location` header value is exactly `https://skill-builder.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=skill-builder-web&response_type=code&scope=openid+profile+email&redirect_uri=https%3A%2F%2Fbuilder.skillbuilder.internal%2Fauth%2Fcallback`
And each response body is exactly 0 bytes
And no response contains a `Set-Cookie` header

### Covered requirements (traceability)
- FR-001
- NFR-002

### Out of scope
The sign-in flow itself and what happens after a successful sign-in (story BSB-18-PENDING-2);
skill-builders group membership checks for a request that does carry a session (story
BSB-18-PENDING-3); project-level authorization such as project membership or ownership (epics
BSB-22 and BSB-23).

### Notes / dependencies
- Establishes the session cookie and the authentication middleware that the other three stories in
  this epic consume. The session cookie is the `sb_session` ID token JWT defined in the Session and
  identity contract above.
- The Cognito User Pool, its signing key, the hosted-UI domain `skill-builder.auth.eu-west-1.amazoncognito.com`
  and the `skill-builders` group are supplied by the platform; the builder is configured with the
  client id `skill-builder-web` and the redirect URI `https://builder.skillbuilder.internal/auth/callback`.
  The exact sign-in `Location` value a test must expect is the one stated in each scenario.
- NFR-002 is the API half of the gate: reject before any builder data is returned.

---

## STORY: BSB-18-PENDING-2

**Summary:** Sign in with platform credentials as a current skill-builders member
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **to sign in with my existing platform identity-provider credentials and be admitted only while I am in the skill-builders group**, so that **I do not need a separate builder account and only trusted people reach authoring features**.

### Acceptance Criteria

#### Scenario: Current group member signs in with platform credentials
Given the hosted UI at `https://skill-builder.auth.eu-west-1.amazoncognito.com` authenticates a user and redirects the browser to `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-1`
And the builder exchanges `test-auth-code-1` at `https://skill-builder.auth.eu-west-1.amazoncognito.com/oauth2/token` with client id `skill-builder-web`
And the exchange returns a Cognito ID token JWT with claims `sub`=`a1b2c3d4-0000-0000-0000-000000000001`, `email`=`ada@example.com`, `name`=`Ada Lovelace`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
When the browser follows that callback URL
Then the builder responds with HTTP status 302 and the `Location` header `https://builder.skillbuilder.internal/builds`
And the response sets `Set-Cookie: sb_session=` followed by that ID token JWT, with the attributes `Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=3600`
And a subsequent `GET https://builder.skillbuilder.internal/builds` carrying that `sb_session` cookie returns HTTP status 200
And the response body contains the exact text `Signed in as Ada Lovelace (ada@example.com)`

#### Scenario: Non-member sign-in is rejected
Given the hosted UI authenticates a user and redirects the browser to `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-2`
And the exchange returns a Cognito ID token JWT with claims `sub`=`b2c3d4e5-0000-0000-0000-000000000002`, `email`=`bob@example.com`, `name`=`Bob Stone`, `cognito:groups`=`["platform-users"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
When the browser follows that callback URL
Then the builder responds with HTTP status 403
And the response body contains the exact text `You are not a member of the skill-builders group`
And the response contains no `Set-Cookie: sb_session=` header
And `SELECT count(*) FROM users WHERE cognito_sub = 'b2c3d4e5-0000-0000-0000-000000000002'` returns `0`

#### Scenario: Identity without a membership claim is rejected
Given the hosted UI authenticates a user and redirects the browser to `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-3`
And the exchange returns a Cognito ID token JWT with claims `sub`=`c3d4e5f6-0000-0000-0000-000000000003`, `email`=`carol@example.com`, `name`=`Carol Diaz`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`, with no `cognito:groups` claim
When the browser follows that callback URL
Then the builder responds with HTTP status 403
And the response body contains the exact text `You are not a member of the skill-builders group`
And the response contains no `Set-Cookie: sb_session=` header
And `SELECT count(*) FROM users WHERE cognito_sub = 'c3d4e5f6-0000-0000-0000-000000000003'` returns `0`

#### Scenario: Failed hosted-UI sign-in creates no session
Given a person who is a current member of the `skill-builders` group
And the hosted UI rejects their incorrect password and redirects the browser to `https://builder.skillbuilder.internal/auth/callback?error=access_denied&error_description=Invalid+password`
When the browser follows that callback URL
Then the builder responds with HTTP status 401
And the response body contains the exact text `Sign-in failed. Check your credentials and try again.`
And the response contains no `Set-Cookie: sb_session=` header
And a subsequent `GET https://builder.skillbuilder.internal/builds` with no `sb_session` cookie responds with HTTP status 302 and the `Location` header `https://skill-builder.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=skill-builder-web&response_type=code&scope=openid+profile+email&redirect_uri=https%3A%2F%2Fbuilder.skillbuilder.internal%2Fauth%2Fcallback`

### Covered requirements (traceability)
- FR-002
- FR-003
- FR-138

### Out of scope
The unauthenticated-request gate (story BSB-18-PENDING-1); membership re-checks on later requests
and the one-hour removal bound (story BSB-18-PENDING-3); creating or reusing the local user record
beyond not creating one for a rejected identity (story BSB-18-PENDING-4); group administration,
which is external to this product.

### Notes / dependencies
- Depends on the session established by story BSB-18-PENDING-1 and on the Cognito User Pool with
  hosted-UI domain `https://skill-builder.auth.eu-west-1.amazoncognito.com` and the externally
  managed `skill-builders` group. The redirect target and callback URI are fixed in the Session and
  identity contract at the top of this file.
- Story BSB-18-PENDING-4 consumes this story's successful sign-in path; a rejected sign-in must
  never reach local-user creation.
- FR-003 is met here at the sign-in boundary; FR-004 and NFR-003 apply it to every later request in
  story BSB-18-PENDING-3.

---

## STORY: BSB-18-PENDING-3

**Summary:** Re-check skill-builders membership on every request and revoke within one hour
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **platform owner**, I want **the builder to re-check skill-builders membership on every authoring request and honour a removal within one hour**, so that **a removed member cannot keep using the builder with an old session**.

### Acceptance Criteria

#### Scenario: Signed-in member passes the per-request membership check
Given the builder's Cognito issuer is `https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`
And the `sb_session` cookie holds a Cognito ID token JWT with `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
And the current time is `2026-11-15T10:00:00Z`
And the build store contains builds named `Alpha`, `Beta` and `Gamma`
When the user sends `GET https://builder.skillbuilder.internal/builds` carrying that `sb_session` cookie
Then the builder returns HTTP status 200
And the response body contains the strings `Alpha`, `Beta` and `Gamma` in that order

#### Scenario: Signed-in non-member is rejected on every authoring route
Given the `sb_session` cookie holds a Cognito ID token JWT with `cognito:groups`=`["platform-users"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
And the current time is `2026-11-15T10:00:00Z`
When the user sends `GET` to each of `https://builder.skillbuilder.internal/builds`, `https://builder.skillbuilder.internal/api/builds`, `https://builder.skillbuilder.internal/builds/1/files` and `https://builder.skillbuilder.internal/projects/1/settings` carrying that `sb_session` cookie
Then each request is rejected with HTTP status 403
And each page response body contains the exact text `You are not a member of the skill-builders group`
And the `GET https://builder.skillbuilder.internal/api/builds` response body is exactly `{"error":{"code":"not_a_member","message":"You are not a member of the skill-builders group"}}`
And no response contains build, skill, branch or project data

#### Scenario: Removed member keeps access only while their token is valid
Given the user signed in at `2026-11-15T10:00:00Z` and their `sb_session` cookie holds a Cognito ID token JWT with `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
And the user is removed from the `skill-builders` group at `2026-11-15T10:00:00Z`
And the build store contains builds named `Alpha`, `Beta` and `Gamma`
When the user sends `GET https://builder.skillbuilder.internal/builds` at `2026-11-15T10:59:59Z` carrying that `sb_session` cookie
Then the builder returns HTTP status 200
And the response body contains the strings `Alpha`, `Beta` and `Gamma` in that order

#### Scenario: Removed member is denied at the session token expiry
Given the user signed in at `2026-11-15T10:00:00Z` and their `sb_session` cookie holds a Cognito ID token JWT with `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
And the user is removed from the `skill-builders` group at `2026-11-15T10:00:00Z`
When the user sends `GET https://builder.skillbuilder.internal/builds` at `2026-11-15T11:00:00Z` carrying that `sb_session` cookie
Then the builder responds with HTTP status 302
And the `Location` response header value is exactly `https://skill-builder.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=skill-builder-web&response_type=code&scope=openid+profile+email&redirect_uri=https%3A%2F%2Fbuilder.skillbuilder.internal%2Fauth%2Fcallback`
And the response carries the header `Set-Cookie: sb_session=; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; Secure; SameSite=Lax`
And the response body is exactly 0 bytes

#### Scenario: Removed member cannot re-authenticate into the builder
Given the user was removed from the `skill-builders` group at `2026-11-15T10:00:00Z`
And the hosted UI authenticates that user at `2026-11-15T11:01:00Z` and the exchange returns a fresh Cognito ID token JWT with `cognito:groups`=`["platform-users"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T12:01:00Z`
When the browser follows the callback to `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-4`
Then the builder responds with HTTP status 403
And the response body contains the exact text `You are not a member of the skill-builders group`
And the response contains no `Set-Cookie: sb_session=` header

### Covered requirements (traceability)
- FR-004
- FR-141
- NFR-003

### Out of scope
Rejecting a non-member at sign-in (story BSB-18-PENDING-2); the session gate for requests with no
session at all (story BSB-18-PENDING-1); creating local user records (story BSB-18-PENDING-4);
role and permission administration inside the builder, and group membership maintenance, which is
external to this product.

### Notes / dependencies
- Depends on story BSB-18-PENDING-1 for the session cookie and story BSB-18-PENDING-2 for the
  admitted member identity, and on the Cognito `cognito:groups` claim.
- Every request validates the `sb_session` ID token JWT (signature, `iss`, `aud`, `exp`) and the
  `cognito:groups` claim; there is no request path that skips the claim check after sign-in.
- The one-hour bound in FR-141 holds because Cognito issues the ID token with `exp` at most one
  hour after sign-in and the builder accepts no token at or after `exp`; a removed member's existing
  token therefore stops authorizing at `exp`, and their next sign-in is rejected under
  BSB-18-PENDING-2.
- A membership claim that is absent or does not contain `skill-builders` is treated as not a member,
  never as a pass.

---

## STORY: BSB-18-PENDING-4

**Summary:** Maintain one local user record per identity-provider subject
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to keep exactly one local user record tied to my identity-provider subject**, so that **my builds, projects and runs stay attributed to me across sign-ins even if my email address changes**.

### Acceptance Criteria

#### Scenario: First successful sign-in creates one local user record
Given the `users` table has no row with `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`
And the hosted UI redirects the browser to `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-5`
And the exchange returns a Cognito ID token JWT with claims `sub`=`a1b2c3d4-0000-0000-0000-000000000001`, `email`=`ada@example.com`, `name`=`Ada Lovelace`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
When the browser follows that callback URL
Then `SELECT count(*) FROM users WHERE cognito_sub = 'a1b2c3d4-0000-0000-0000-000000000001'` returns `1`
And that row's `email` column is exactly `ada@example.com`
And that row's `name` column is exactly `Ada Lovelace`
And a subsequent `GET https://builder.skillbuilder.internal/builds` carrying the issued `sb_session` cookie returns a response body containing the exact text `Signed in as Ada Lovelace (ada@example.com)`

#### Scenario: Later sign-in reuses the existing local user record
Given exactly one `users` row exists with `id` = `42` and `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`
When that subject completes a later successful sign-in through `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-6` and the exchange returns a new Cognito ID token JWT with claims `sub`=`a1b2c3d4-0000-0000-0000-000000000001`, `email`=`ada@example.com`, `name`=`Ada Lovelace`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
Then `SELECT count(*) FROM users WHERE cognito_sub = 'a1b2c3d4-0000-0000-0000-000000000001'` returns `1`
And the row's `id` is still `42`
And the `GET https://builder.skillbuilder.internal/builds` response for the new session contains the exact text `Signed in as Ada Lovelace (ada@example.com)`

#### Scenario: Changed email does not create a second record
Given exactly one `users` row exists with `id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001` and `email` = `ada@example.com`
When that subject signs in through `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-8` and the exchange returns a new Cognito ID token JWT with claims `sub`=`a1b2c3d4-0000-0000-0000-000000000001`, `email`=`ada.lovelace@example.com`, `name`=`Ada Lovelace`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
Then `SELECT count(*) FROM users WHERE cognito_sub = 'a1b2c3d4-0000-0000-0000-000000000001'` returns `1`
And the row's `id` is still `42`
And the row's `email` is exactly `ada.lovelace@example.com`

#### Scenario: Failed sign-in creates no local user record
Given the `users` table has no row with `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000099`
And the hosted UI returns `https://builder.skillbuilder.internal/auth/callback?error=access_denied&error_description=Invalid+password` with no authorization code
When the browser follows that callback URL
Then the builder responds with HTTP status 401
And `SELECT count(*) FROM users WHERE cognito_sub = 'a1b2c3d4-0000-0000-0000-000000000099'` returns `0`

#### Scenario: Rejected non-member sign-in creates no local user record
Given the `users` table has no row with `cognito_sub` = `d4e5f6a7-0000-0000-0000-000000000004`
And the exchange returns a Cognito ID token JWT with claims `sub`=`d4e5f6a7-0000-0000-0000-000000000004`, `email`=`dave@example.com`, `name`=`Dave Kim`, `cognito:groups`=`["platform-users"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
When the browser follows the callback to `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-7`
Then the builder responds with HTTP status 403
And `SELECT count(*) FROM users WHERE cognito_sub = 'd4e5f6a7-0000-0000-0000-000000000004'` returns `0`

#### Scenario: Concurrent first sign-ins create exactly one record
Given the `users` table has no row with `cognito_sub` = `e5f6a7b8-0000-0000-0000-000000000005`
When two first-time sign-ins for that subject complete concurrently at `2026-11-15T10:00:00Z` through `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-9a` and `https://builder.skillbuilder.internal/auth/callback?code=test-auth-code-9b`, and each exchange returns a Cognito ID token JWT with claims `sub`=`e5f6a7b8-0000-0000-0000-000000000005`, `email`=`erin@example.com`, `name`=`Erin Park`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`
Then both callbacks respond with HTTP status 302 and the `Location` header `https://builder.skillbuilder.internal/builds`
And both responses set an `sb_session` cookie
And `SELECT count(*) FROM users WHERE cognito_sub = 'e5f6a7b8-0000-0000-0000-000000000005'` returns `1`
And a `GET https://builder.skillbuilder.internal/builds` carrying either issued `sb_session` cookie returns a response body containing the exact text `Signed in as Erin Park (erin@example.com)`

### Covered requirements (traceability)
- FR-005
- FR-142

### Out of scope
User profile editing or self-service account management; linking multiple identity-provider
subjects to one person; deleting or merging local user records; roles and permissions beyond the
authoring gate.

### Notes / dependencies
- Depends on story BSB-18-PENDING-2 for the successful sign-in path and on story BSB-18-PENDING-1
  for the `sb_session` cookie.
- The local `users` table is the durable owner reference later epics use for builds, projects and
  runs; `cognito_sub` is UNIQUE, which is what makes the concurrent-sign-in scenario hold.
- On a reuse, the row's `email` and `name` are refreshed from the current ID token; the row `id` and
  `cognito_sub` never change. That is why the changed-email scenario keeps `id` 42 and stores the
  new address.
- Only a successful, admitted sign-in creates or reuses a record. A failed sign-in or a
  membership-rejected sign-in creates none.
