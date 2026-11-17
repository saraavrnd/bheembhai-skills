# Stories — BSB-39 (Access & identity)

Epic BSB-39 covers FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141, FR-142, FR-165,
NFR-002 and NFR-003. It is decomposed into the 6 stories below; every one of those 11
requirements is covered by at least one story's acceptance criteria.

**Representative surfaces.** The criteria name `/builds` (the authoring build list) and
`GET /api/builds` as the concrete authoring page and API used by the tests. Every other
authoring page and API route registered by this and later epics is subject to the same guard.

## Coverage summary

| Story | Requirements covered |
|-------|----------------------|
| BSB-39-PENDING-1 — Sign in with platform identity-provider credentials | FR-002 |
| BSB-39-PENDING-2 — Block unauthenticated access to every authoring surface | FR-001, NFR-002 |
| BSB-39-PENDING-3 — Restrict authoring to current skill-builders members | FR-003, FR-138, NFR-003 |
| BSB-39-PENDING-4 — Recheck membership and revoke removed members within one hour | FR-004, FR-141 |
| BSB-39-PENDING-5 — Create and reuse one local user record per identity-provider subject | FR-005, FR-142 |
| BSB-39-PENDING-6 — Keep the builder isolated from the platform database | FR-165 |

---

## STORY: Sign in with platform identity-provider credentials  (BSB-39-PENDING-1)

**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **to sign in with my existing platform identity-provider credentials**, so that **I can reach the skill builder without a second account or password**.

### Acceptance Criteria
**Scenario: Successful sign-in with an existing platform account**
- Given a visitor who is a current member of the skill-builders group
- When the visitor submits their valid platform identity-provider credentials
- Then the builder establishes an authenticated session and redirects to the authoring home page `/builds`

**Scenario: Invalid credentials rejected**
- Given a visitor on the sign-in page
- When the visitor submits an incorrect password for a platform account
- Then the sign-in page shows the message "Sign-in failed. Check your credentials and try again." and no builder session is created

**Scenario: Identity provider unavailable**
- Given the platform identity provider is unreachable
- When the visitor attempts to sign in
- Then the sign-in page shows the message "Identity provider unavailable. Try again later." and no builder session is created

**Scenario: No separate credential store**
- Given a user has signed in successfully
- When the builder's database is inspected
- Then it contains no password or password hash for that user

### Covered requirements
- FR-002

### Out of scope
Account creation, password reset and multi-factor authentication (owned by the platform identity provider); group membership administration; sign-out.

### Notes / dependencies
The platform identity provider is an external prerequisite supplied outside this product. The local user record created for the subject is BSB-39-PENDING-5. A non-member's sign-in attempt is rejected by BSB-39-PENDING-3.

---

## STORY: Block unauthenticated access to every authoring surface  (BSB-39-PENDING-2)

**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **requests without a valid authenticated session rejected before any builder data is returned**, so that **nobody outside the platform can read or act on builder content**.

### Acceptance Criteria
**Scenario: Unauthenticated visitor opens an authoring page**
- Given a visitor with no authenticated session
- When the visitor requests the authoring page `/builds`
- Then the builder responds with HTTP 302 to the identity-provider sign-in URL and the response body contains no build data

**Scenario: Unauthenticated API request**
- Given a visitor with no authenticated session
- When the visitor calls `GET /api/builds`
- Then the builder responds with HTTP 401 and body `{"error":"authentication_required"}` and no build records

**Scenario: Expired session rejected before data**
- Given a user whose session expired one minute ago
- When the user calls `GET /api/builds`
- Then the builder responds with HTTP 401 and body `{"error":"authentication_required"}` and no build records

**Scenario: Guard covers every authoring route**
- Given a visitor with no authenticated session
- When the visitor requests each registered authoring page and API route
- Then every page response is HTTP 302 and every API response is HTTP 401, and no response body contains builder data

### Covered requirements
- FR-001
- NFR-002

### Out of scope
Deciding whether a signed-in user belongs to the skill-builders group (BSB-39-PENDING-3); sign-in itself (BSB-39-PENDING-1).

### Notes / dependencies
The guard must fail closed on every page and API route, including routes added by later epics. BSB-39-PENDING-1 provides the authenticated session this story checks for.

---

## STORY: Restrict authoring to current skill-builders members  (BSB-39-PENDING-3)

**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **authoring available only to users who are current members of the skill-builders group**, so that **only trusted people can create or change skills**.

### Acceptance Criteria
**Scenario: Current member reaches authoring**
- Given a signed-in user whose current skill-builders membership claim is `true`
- When the user requests the authoring page `/builds`
- Then the builder responds with HTTP 200 and renders the build list

**Scenario: Non-member sign-in rejected**
- Given a platform user who is not a current member of the skill-builders group
- When the user completes platform sign-in with valid credentials
- Then the builder shows the message "Access is restricted to current skill-builders group members", creates no builder session, and creates no local user record for that identity-provider subject

**Scenario: Signed-in non-member request rejected**
- Given a signed-in user whose current skill-builders membership claim is `false`
- When the user calls `GET /api/builds`
- Then the builder responds with HTTP 403 and body `{"error":"membership_required"}` and no build records

**Scenario: Missing membership claim rejected**
- Given a signed-in user whose identity-provider claim does not include skill-builders membership
- When the user requests the authoring page `/builds`
- Then the builder responds with HTTP 403 and does not render any build data

### Covered requirements
- FR-003
- FR-138
- NFR-003

### Out of scope
The one-hour revocation window for a removed member (BSB-39-PENDING-4); administering users, groups or roles; invitations.

### Notes / dependencies
The membership claim is issued by the platform identity provider and managed by the platform administrator outside this product. This story evaluates the claim at sign-in and on a request; BSB-39-PENDING-4 owns the continuous-recheck and removal deadline.

---

## STORY: Recheck membership and revoke removed members within one hour  (BSB-39-PENDING-4)

**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **membership rechecked on every request and a removed member denied within one hour**, so that **revoking someone's trust takes effect without waiting for them to sign out**.

### Acceptance Criteria
**Scenario: Removed member denied at the one-hour boundary**
- Given a user signed in at 08:00 while a member of the skill-builders group
- When the user is removed from the group at 09:00 and calls `GET /api/builds` at 10:00 without signing out
- Then the builder responds with HTTP 403 and body `{"error":"membership_required"}` and no build records

**Scenario: Recheck covers pages and APIs**
- Given a signed-in user removed from the skill-builders group 61 minutes ago
- When the user requests the authoring page `/builds` and then calls `GET /api/builds`
- Then the page responds with HTTP 403 and the API responds with HTTP 403 and body `{"error":"membership_required"}`

**Scenario: Current member keeps access across requests**
- Given a signed-in user whose current skill-builders membership claim is `true`
- When the user calls `GET /api/builds` at 08:00 and again at 09:00
- Then both requests respond with HTTP 200

**Scenario: Unverifiable membership fails closed**
- Given the platform identity provider is unreachable and the builder holds no membership decision younger than 60 minutes for the user
- When the user calls `GET /api/builds`
- Then the builder responds with HTTP 503 and body `{"error":"membership_unverifiable"}` and no build records

### Covered requirements
- FR-004
- FR-141

### Out of scope
Terminating a run that is already executing when the author is removed (owned by the run guardrail epic); group membership administration.

### Notes / dependencies
Depends on BSB-39-PENDING-3 for the membership-claim check. The one-hour limit is the maximum age of any cached membership decision; an uncached check is always allowed to be fresher. Behaviour for runs already in flight is explicitly outside this story.

---

## STORY: Create and reuse one local user record per identity-provider subject  (BSB-39-PENDING-5)

**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to keep exactly one local user record for me across sign-ins**, so that **my builds, projects and runs are attributed to the same person every time**.

### Acceptance Criteria
**Scenario: First successful sign-in creates one record**
- Given no local user record exists for identity-provider subject `sub-12345`
- When that subject signs in successfully for the first time
- Then the builder database contains exactly one local user record whose identity-provider subject is `sub-12345`

**Scenario: Later sign-in reuses the record**
- Given a local user record exists for identity-provider subject `sub-12345`
- When that subject signs in successfully from a second browser session
- Then the builder database still contains exactly one record for `sub-12345` and the new session carries the existing record's user id

**Scenario: Distinct subjects get distinct records**
- Given identity-provider subjects `sub-12345` and `sub-67890` have no local user records
- When each subject signs in successfully
- Then the builder database contains two local user records, one for `sub-12345` and one for `sub-67890`

**Scenario: Failed sign-in creates no record**
- Given no local user record exists for identity-provider subject `sub-99999`
- When a sign-in attempt for that subject fails because the password is incorrect
- Then the builder database contains zero local user records for `sub-99999`

**Scenario: Concurrent first sign-ins create one record**
- Given no local user record exists for identity-provider subject `sub-12345`
- When two sign-ins for that subject complete at the same time
- Then the builder database contains exactly one local user record for `sub-12345`

### Covered requirements
- FR-005
- FR-142

### Out of scope
Using the local user record for ownership of builds or projects (later epics); merging two existing records; editing a user's profile.

### Notes / dependencies
Depends on BSB-39-PENDING-1 for successful sign-in and on BSB-39-PENDING-3 for the member-only gate. The record is stored in the builder's own database; the identity-provider subject is the unique key. Later epics use this record's user id as the owner key.

---

## STORY: Keep the builder isolated from the platform database  (BSB-39-PENDING-6)

**Epic:** BSB-39 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **platform administrator**, I want **the builder to never read from or write to the platform's database**, so that **a builder defect or compromise cannot expose or corrupt platform data**.

### Acceptance Criteria
**Scenario: No platform database connection is opened**
- Given the builder is deployed with the platform database reachable
- When sign-in, the authoring home page `/builds` and `GET /api/builds` are exercised
- Then the platform database connection log records zero connections from the builder and a sentinel row in the platform database is unchanged

**Scenario: Configuration carries no platform database credentials**
- Given the builder's configuration and secret references
- When they are inspected
- Then they contain no platform database host, database name, username, password or connection string

**Scenario: Identity attributes come only from the identity provider and session**
- Given a signed-in user
- When the builder renders that user's identity in the authoring home page
- Then the displayed subject, display name and group membership each match the identity-provider claim or the authenticated session

**Scenario: Source contains no platform database access path**
- Given the builder source and its dependency list
- When the isolation check runs
- Then it reports zero references to a platform database driver, connection string or query helper

### Covered requirements
- FR-165

### Out of scope
Reading or writing any other platform data store; the platform's catalog import; administering the platform database's own permissions and backups.

### Notes / dependencies
The platform database is an external system owned by the platform; this story verifies the builder has no path to it. The isolation check is a required gate for every later epic that adds a data-access path.
