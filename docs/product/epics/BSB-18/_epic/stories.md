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

---

## STORY: BSB-18-PENDING-1

**Summary:** Require a signed-in session for every authoring request
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to send me to sign in whenever I have no valid session**, so that **no authoring page or builder data is exposed to an unauthenticated visitor**.

### Acceptance Criteria

#### Scenario: Authoring page refuses an unauthenticated visitor
Given a visitor with no session cookie
When the visitor requests `/builds`
Then the builder responds with HTTP 302 and a `Location` header pointing at the platform identity-provider sign-in URL
And the response contains no authoring page markup
And the response contains no build, skill, branch or project data

#### Scenario: Authoring API refuses an unauthenticated request
Given the build store contains builds named "Alpha", "Beta" and "Gamma"
When a visitor with no session cookie sends `GET /api/builds` with `Accept: application/json`
Then the builder responds with HTTP 401
And the response body contains the error code `authentication_required`
And the response body contains none of "Alpha", "Beta" or "Gamma"

#### Scenario: Expired session is treated as unauthenticated
Given a visitor whose session cookie expired 1 minute ago
When the visitor requests `/builds`
Then the builder responds with HTTP 302 to the platform identity-provider sign-in URL
And the response clears the expired session cookie

#### Scenario: Every authoring page route enforces the session gate
Given the authoring page routes `/builds`, `/builds/1`, `/builds/1/files` and `/projects/1/settings`
When a visitor with no session cookie requests each route
Then every request responds with HTTP 302 to the platform identity-provider sign-in URL
And no response contains an authoring page or builder data

### Covered requirements (traceability)
- FR-001
- NFR-002

### Out of scope
The sign-in flow itself and what happens after a successful sign-in (story BSB-18-PENDING-2);
skill-builders group membership checks (story BSB-18-PENDING-3); project-level authorization such
as project membership or ownership (epics BSB-22 and BSB-23).

### Notes / dependencies
- Establishes the session model and the authentication middleware that the other three stories in
  this epic consume. Nothing in this story reads or writes a local user record.
- The platform identity provider and its sign-in URL are external prerequisites (epic BSB-18
  notes); the builder consumes them rather than implementing them.
- NFR-002 is the API half of the gate: reject before any builder data is returned.

---

## STORY: BSB-18-PENDING-2

**Summary:** Sign in with platform credentials as a current skill-builders member
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **to sign in with my existing platform identity-provider credentials and be admitted only while I am in the skill-builders group**, so that **I do not need a separate builder account and only trusted people reach authoring features**.

### Acceptance Criteria

#### Scenario: Current group member signs in with platform credentials
Given a person with valid platform identity-provider credentials and a current skill-builders membership claim
When they complete sign-in at the identity provider
Then the builder creates an authenticated session
And redirects them to `/builds`
And `/builds` shows their identity-provider display name and email address

#### Scenario: Non-member sign-in is rejected
Given a person with valid platform identity-provider credentials and no current skill-builders membership claim
When they complete sign-in at the identity provider
Then the builder creates no authenticated session
And responds with HTTP 403 and the message "You are not a member of the skill-builders group"
And no local user record is created for that identity-provider subject

#### Scenario: Identity without a membership claim is rejected
Given a person whose identity-provider response contains no skill-builders membership claim
When they complete sign-in at the identity provider
Then the builder treats them as a non-member
And responds with HTTP 403 and the message "You are not a member of the skill-builders group"

#### Scenario: Invalid identity-provider credentials create no session
Given a person who is a current member of skill-builders
When they enter an incorrect password at the identity provider
Then the identity provider rejects the sign-in
And the builder creates no session
And no session cookie is set

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
- Depends on the session established by story BSB-18-PENDING-1 and on the external platform identity
  provider and the externally managed `skill-builders` group.
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
Given a signed-in user whose skill-builders membership claim is current
When the user requests `/builds`
Then the builder returns HTTP 200
And the page shows the build list

#### Scenario: Signed-in non-member is rejected on every authoring route
Given a signed-in user whose skill-builders membership claim is false
When the user requests `/builds`, `/api/builds`, `/builds/1/files` and `/projects/1/settings`
Then every request is rejected with HTTP 403 and the message "You are not a member of the skill-builders group"
And no response contains build, skill, branch or project data

#### Scenario: Removed member is denied once the cached claim is older than one hour
Given a signed-in user who was admitted as a skill-builders member and whose last successful membership lookup was 61 minutes ago
And the user was removed from the skill-builders group 30 minutes ago
When the user requests `/builds`
Then the request is rejected with HTTP 403 and the message "You are not a member of the skill-builders group"
And no build data is returned

#### Scenario: Removal denies access no later than 60 minutes after it happens
Given a signed-in user who was a skill-builders member at their last membership lookup
When the user is removed from the skill-builders group at 10:00
Then every authoring request made at or after 11:00 is rejected with HTTP 403
And the message is "You are not a member of the skill-builders group"

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
- Depends on story BSB-18-PENDING-1 for the session and story BSB-18-PENDING-2 for the admitted
  member identity, and on the external identity provider's membership claim.
- The membership decision may be cached, but no cached positive decision older than 60 minutes may
  authorize a request: that cache lifetime is what makes FR-141's one-hour bound hold.
- A membership claim that is absent or false is treated as not a member, never as a pass.

---

## STORY: BSB-18-PENDING-4

**Summary:** Maintain one local user record per identity-provider subject
**Epic:** BSB-18 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-1, MVP

### Story
As a **skill author**, I want **the builder to keep exactly one local user record tied to my identity-provider subject**, so that **my builds, projects and runs stay attributed to me across sign-ins even if my email address changes**.

### Acceptance Criteria

#### Scenario: First successful sign-in creates one local user record
Given identity-provider subject `auth0|user-123` with email `ada@example.com` and display name "Ada Lovelace" and no local user record
When the user completes a successful sign-in
Then exactly one local user record exists with identity-provider subject `auth0|user-123`
And that record stores email `ada@example.com` and display name "Ada Lovelace"
And the authenticated session references that local user record

#### Scenario: Later sign-in reuses the existing local user record
Given one local user record exists for identity-provider subject `auth0|user-123`
When the same subject completes a later successful sign-in
Then the builder reuses that local user record
And the count of local user records for subject `auth0|user-123` is exactly 1
And the new session references the same local user record as the first session

#### Scenario: Changed email does not create a second record
Given one local user record exists for identity-provider subject `auth0|user-123` with email `ada@example.com`
When the same subject signs in and the identity provider reports email `ada.lovelace@example.com`
Then the builder reuses the existing local user record
And the count of local user records for subject `auth0|user-123` is exactly 1

#### Scenario: Failed sign-in creates no local user record
Given identity-provider subject `auth0|user-999` has no local user record
When that person's sign-in attempt fails at the identity provider
Then no local user record is created for subject `auth0|user-999`

#### Scenario: Rejected non-member sign-in creates no local user record
Given identity-provider subject `auth0|user-456` has no local user record and no current skill-builders membership claim
When that person completes sign-in and the authoring gate rejects them
Then no local user record is created for subject `auth0|user-456`

#### Scenario: Concurrent first sign-ins create exactly one record
Given identity-provider subject `auth0|user-777` has no local user record
When two first-time sign-ins for that subject complete within the same second
Then exactly one local user record exists for subject `auth0|user-777`
And both authenticated sessions reference that same record

### Covered requirements (traceability)
- FR-005
- FR-142

### Out of scope
User profile editing or self-service account management; linking multiple identity-provider
subjects to one person; deleting or merging local user records; roles and permissions beyond the
authoring gate.

### Notes / dependencies
- Depends on story BSB-18-PENDING-2 for the successful sign-in path and on story BSB-18-PENDING-1
  for the session that stores the record reference.
- The local user record is the durable owner reference later epics use for builds, projects and
  runs; its identity-provider subject must be unique in the record store.
- Only a successful, admitted sign-in creates or reuses a record. A failed sign-in or a
  membership-rejected sign-in creates none.
