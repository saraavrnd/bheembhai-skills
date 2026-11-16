# Stories — BSB-22 (Test projects & membership)

Source: Jira epic **BSB-22** — *Test projects & membership* (feature area FA-4, release MVP,
labels FA-4, MVP), fetched read-only from the Atlassian project `bheembhai-skill-builder`; its
summary, description and functional scope are the same as the BSB-22 section of
`docs/product/epics.md`. The requirement IDs mapped to the epic are in
`docs/product/epic-map.json`.

Epic BSB-22 covers 6 requirements. They decompose into the 5 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The run context's item is epic **BSB-22** (summary *Test projects & membership*,
feature area FA-4, release MVP), and `epic-map.json` maps it to six requirements. The Atlassian MCP
tools were not exposed in this session, so the epic was fetched **read-only** through the
equivalent Jira REST call `GET /rest/api/3/issue/BSB-22`: type Epic, status To Do, labels `FA-4`
and `MVP`, with a description, functional scope and covered-requirements list identical to the
BSB-22 section of `docs/product/epics.md`. A read-only Jira search for `SkillBuilder` across every
accessible project returned no issue. Nothing was written to Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-023 | BSB-22-PENDING-1 |
| FR-024 | BSB-22-PENDING-1 |
| FR-025 | BSB-22-PENDING-2 |
| FR-026 | BSB-22-PENDING-3 |
| FR-027 | BSB-22-PENDING-4 |
| FR-028 | BSB-22-PENDING-5 |

## Project and membership contract (test fixture constants)

Every scenario below uses these exact values. The member session, the local `users` rows and the
`skill-builders` gate are established by epic BSB-18. The project and membership records follow
`docs/adr/SK-001-skill-builder.md` §4 and the `projects` and `project_members` tables in §9. The
run-start route used by FR-027 is owned by epic BSB-24, and the integration-settings route used by
FR-028 is owned by epic BSB-23; this epic owns only the membership and owner checks applied to
them. Those checks are delivered as reusable guards (`require_project_member` and
`require_project_owner`). BSB-22-PENDING-4 and BSB-22-PENDING-5 assert only the guard decision —
admit or refuse — and never the protected route's success status, request schema or row columns;
the success-path assertions belong to BSB-24's and BSB-23's own stories, which cite the guard.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT for the signed-in user with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`; the current time in every scenario is `2026-11-15T10:00:00Z` |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing` |
| `users` fixture | exactly three rows, the three users above; `SELECT count(*) FROM users` returns `3` and `SELECT count(*) FROM users WHERE id = 999` returns `0` |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42` and `created_at` = `2026-11-14T09:00:00Z`; id `8` has `name` = `Search smoke`, `owner_id` = `43` and `created_at` = `2026-11-14T09:05:00Z`; ids `1` to `6`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)`; `project_members` has a primary key on `(project_id, user_id)` |
| Role values | `owner` and `member`; the owner also has a `project_members` row whose `role` is `owner` |
| `runs` fixture | exactly zero rows (`SELECT count(*) FROM runs` returns `0`) |
| `integrations` fixture | exactly one row: `id` = `5`, `project_id` = `7`, `kind` = `jira`, `config` = `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`, `secret_ref` = `skill-builder/7/jira`, `mcp` = `null`, `verified_at` = `2026-11-14T09:00:00Z`; no row for project `8` |
| Project API | `POST https://builder.skillbuilder.internal/api/projects` |
| Membership API | `POST https://builder.skillbuilder.internal/api/projects/{project_id}/members` and `DELETE https://builder.skillbuilder.internal/api/projects/{project_id}/members/{user_id}` |
| Run-start route (owned by BSB-24) | `POST https://builder.skillbuilder.internal/api/projects/{project_id}/runs`; the body used in the scenarios below is a placeholder until BSB-24 fixes the request contract |
| Integration route (owned by BSB-23) | `PUT https://builder.skillbuilder.internal/api/projects/{project_id}/integrations/{kind}`; the body used in the scenarios below is a placeholder until BSB-23 fixes the request contract |
| Success statuses (this epic) | HTTP 201 for project create and member add; HTTP 204 for member delete. The run-start 201 and the integration 200 are asserted by BSB-24's and BSB-23's own scenarios, which cite these guards. |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |

Project name rules are this epic's API contract: the submitted `name` is trimmed of leading and
trailing ASCII spaces, and the stored value must then be 1 to 80 characters long. Two projects may
share a name; there is no uniqueness rule. The `projects` row's `owner_id` and the
`project_members` row with `role` = `owner` are written in the same transaction as the project.

**Error responses** (every one has `Content-Type: application/json`):

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| `name` is missing, empty, or whitespace only after trimming | 422 | `{"error":{"code":"project_name_required","message":"Project name is required."}}` |
| `name` is longer than 80 characters after trimming | 422 | `{"error":{"code":"project_name_too_long","message":"Project name must be 80 characters or fewer."}}` |
| `user_id` is missing or is not an integer | 422 | `{"error":{"code":"user_id_required","message":"A user_id is required."}}` |
| The target user has no local `users` row | 422 | `{"error":{"code":"member_not_skill_builder","message":"User 999 is not a skill-builder."}}` |
| The target user is already a member of the project, or is its owner | 409 | `{"error":{"code":"member_already_exists","message":"User 43 is already a member of project 7."}}` |
| The owner's own membership row is the removal target | 422 | `{"error":{"code":"owner_cannot_be_removed","message":"The project owner cannot be removed; ownership transfer is not supported."}}` |
| The caller is a project member but not its owner, on a membership route | 403 | `{"error":{"code":"project_owner_required","message":"Only the project owner can change project membership."}}` |
| The caller is a project member but not its owner, on an integration route | 403 | `{"error":{"code":"project_owner_required","message":"Only the project owner can change project integrations."}}` |
| The caller is not a member of the project | 403 | `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}` |
| The removal target is not a member of the project | 404 | `{"error":{"code":"member_not_found","message":"User 44 is not a member of project 7."}}` |
| The project id does not exist | 404 | `{"error":{"code":"project_not_found","message":"Project 999 does not exist."}}` |

In every `member_not_skill_builder`, `member_already_exists`, `member_not_found` and
`project_not_found` body, the quoted or numeric value is the value from the request.

Authorization order on every project-scoped route is fixed: epic BSB-18's session gate first
(HTTP 401 with its `authentication_required` body for a request with no valid session), then
epic BSB-18's group gate (403 `not_a_member` for a signed-in user outside `skill-builders`), then
project resolution (404 `project_not_found`), then the caller's membership (403
`project_membership_required`), then the owner role where the route requires it (403
`project_owner_required`), and only then request-body validation (422). A route therefore never
returns 403 to a caller whose project does not exist, and an unauthorized caller never learns a
body-validation error.

The owner check reads the caller's `project_members` row whose `role` is `owner`;
`projects.owner_id` is the denormalized creator record and must equal that row's `user_id`.

**Membership evidence.** The builder cannot list another person's current `skill-builders` group
membership: it learns membership only from the requesting user's own token (BSB-18-PENDING-3). A
local `users` row is therefore the durable FA-1 evidence that the user was admitted as a
skill-builder at least once. The add request accepts a `user_id` that must resolve to an existing
`users` row; a person the FA-1 gate never admitted has no row and is refused. A person who has left
the group can still have a row, but their own requests are refused by BSB-18's per-request
membership check, so their project membership row grants no access at use time. This boundary is
restated in BSB-22-PENDING-2's Notes; epic-review Finding 3 / Open question 4 is the decision that
settles it and is not answered in this run.

Two cross-epic boundaries are also flagged, not hidden. BSB-22-PENDING-4 delivers the reusable
`require_project_member` guard and BSB-22-PENDING-5 delivers `require_project_owner`; the run-start
route is epic BSB-24's contract and the integration route is epic BSB-23's, so each story asserts
only its guard's decision and carries an acceptance hook naming the consumer epic rather than a
"cannot be accepted before" dependency. This removes the earlier two-way acceptance cycle: BSB-22
can be accepted on the guards alone, and BSB-24's and BSB-23's stories apply them to their routes
and cite them. Requirements FR-027 and FR-028 stay in this epic because the membership and owner
decisions are what they state.

The project and membership **web pages** — the projects list and create page, the project settings
and members page, the add-member picker and the remove control — and the `GET` read endpoints they
need are **not delivered by any story in this epic**. The scenarios below are the JSON API and
guard contract only. Epic review Finding 2 / Open question 2 must assign those surfaces to a named
story or epic; until then they are recorded as a gap here and in each story's Out of scope, not
silently assumed.

---

## STORY: BSB-22-PENDING-1

**Summary:** Create a test project and be recorded as its owner
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **skill author**, I want **to create a test project**, so that **I have a shared sandbox in which I can run skills against test credentials and I own its settings**.

### Acceptance Criteria

#### Scenario: Author creates a test project and becomes its owner
Given the `projects` table contains exactly ten rows with ids `1` to `10`, including id `7` with `owner_id` = `42` and id `8` with `owner_id` = `43`
And the `project_members` table contains exactly `7 | 42 | owner`, `7 | 43 | member` and `8 | 43 | owner`
And the `users` table contains exactly the three users with ids `42`, `43` and `44`
And the database clock is `2026-11-15T10:00:00Z`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects` with `Content-Type: application/json` and body exactly `{"name":"Billing regression"}`
Then the builder responds with HTTP status 201
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"id":11,"name":"Billing regression","owner_id":42,"created_at":"2026-11-15T10:00:00Z"}`
And `SELECT id, name, owner_id FROM projects WHERE id = 11` returns exactly `11 | Billing regression | 42`
And `SELECT created_at FROM projects WHERE id = 11` equals the timestamptz `2026-11-15T10:00:00Z`
And `SELECT project_id, user_id, role FROM project_members WHERE project_id = 11` returns exactly `11 | 42 | owner`
And `SELECT count(*) FROM project_members WHERE project_id = 11` returns `1`

#### Scenario: The creating author is recorded as owner, not a fixed operator
Given the `projects` table contains exactly ten rows with ids `1` to `10`, including id `7` with `owner_id` = `42` and id `8` with `owner_id` = `43`
And the `project_members` table contains exactly `7 | 42 | owner`, `7 | 43 | member` and `8 | 43 | owner`
And the `users` table contains exactly the three users with ids `42`, `43` and `44`
And the database clock is `2026-11-15T10:00:00Z`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects` with `Content-Type: application/json` and body exactly `{"name":"Search smoke 2"}`
Then the builder responds with HTTP status 201
And the response body is exactly `{"id":11,"name":"Search smoke 2","owner_id":43,"created_at":"2026-11-15T10:00:00Z"}`
And `SELECT id, name, owner_id FROM projects WHERE id = 11` returns exactly `11 | Search smoke 2 | 43`
And `SELECT project_id, user_id, role FROM project_members WHERE project_id = 11` returns exactly `11 | 43 | owner`
And `SELECT count(*) FROM project_members WHERE project_id = 11 AND user_id = 42` returns `0`

#### Scenario: Project creation refuses a missing name
Given the `projects` table contains exactly ten rows with ids `1` to `10` and the `users` table contains exactly the three users with ids `42`, `43` and `44`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects` with `Content-Type: application/json` and body exactly `{}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_name_required","message":"Project name is required."}}`
And `SELECT count(*) FROM projects` returns `10`

#### Scenario: Project creation refuses an empty name
Given the `projects` table contains exactly ten rows with ids `1` to `10` and the `users` table contains exactly the three users with ids `42`, `43` and `44`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects` with `Content-Type: application/json` and body exactly `{"name":""}`
Then the builder responds with HTTP status 422
And the response body is exactly `{"error":{"code":"project_name_required","message":"Project name is required."}}`
And `SELECT count(*) FROM projects` returns `10`

#### Scenario: Project creation refuses a whitespace-only name
Given the `projects` table contains exactly ten rows with ids `1` to `10` and the `users` table contains exactly the three users with ids `42`, `43` and `44`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects` with `Content-Type: application/json` and body exactly `{"name":"   "}`
Then the builder responds with HTTP status 422
And the response body is exactly `{"error":{"code":"project_name_required","message":"Project name is required."}}`
And `SELECT count(*) FROM projects` returns `10`

#### Scenario: Project creation refuses a name longer than 80 characters
Given the `projects` table contains exactly ten rows with ids `1` to `10` and the `users` table contains exactly the three users with ids `42`, `43` and `44`
And the `name` value in the request body below is exactly 81 characters long
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects` with `Content-Type: application/json` and body exactly `{"name":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}`
Then the builder responds with HTTP status 422
And the response body is exactly `{"error":{"code":"project_name_too_long","message":"Project name must be 80 characters or fewer."}}`
And `SELECT count(*) FROM projects` returns `10`

### Covered requirements (traceability)
- FR-023
- FR-024

### Out of scope
Renaming or deleting a project; project ownership transfer (an explicit non-goal); project skills and
their contents; project integrations; managing members after creation (BSB-22-PENDING-2 and
BSB-22-PENDING-3); user or group administration (the FA-1 gate owns admission, and the platform
administrator owns the `skill-builders` group); the projects list and create-project web page and
any `GET` project read endpoint — no story in this epic delivers them, and epic-review Finding 2 /
Open question 2 must assign them.

### Notes / dependencies
- Depends on epic BSB-18 for the member session and for the local `users` rows `42`, `43` and `44`
  (`docs/product/epics/BSB-18/_epic/stories.md`, BSB-18-PENDING-4).
- The `projects` and `project_members` records follow `docs/adr/SK-001-skill-builder.md` §9. The
  creator is recorded twice: `projects.owner_id` and a `project_members` row with `role` = `owner`.
  FR-024 asserts both, and the owner row is what makes the owner count as a member for FR-027.
- At most one `owner` row exists per project. Enforce it as a partial unique index on
  `project_members (project_id) WHERE role = 'owner'`, or as an equivalent invariant that
  `sdlc-deliver-story-design` enforces in the same transaction that writes the project; the owner
  check reads this row, and `projects.owner_id` must equal it (contract preamble).
- Any signed-in skill-builder may create a project (FR-023); no installation-level role is required.
  The FA-1 gate refuses a caller who is not a current skill-builder before this route runs.
- The 1-to-80-character name rule, the trim rule and the absence of a uniqueness rule are this
  epic's API contract. The PRD and SK-001 set no project-name rule, so these values are fixed here
  to make the rejection scenarios testable.
- The project id in the scenarios is `11` because the fixed fixture already uses ids `1` to `10`.
  A real sequence may differ; the scenarios assert the next value of the fixture.
- This story is the prerequisite for BSB-22-PENDING-2 to BSB-22-PENDING-5: they all use a project
  whose `owner_id` and `project_members` row this story writes.

---

## STORY: BSB-22-PENDING-2

**Summary:** Owner adds a skill-builder user as a project member
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **skill author who owns a project**, I want **to add another skill-builder user as a project member**, so that **that person can run skills in the project's sandbox without becoming its owner**.

### Acceptance Criteria

#### Scenario: Owner adds a skill-builder user as a member
Given project `7` exists with `owner_id` = `42`
And the `project_members` table contains exactly `7 | 42 | owner`, `7 | 43 | member` and `8 | 43 | owner`, and no row `7 | 44 | member`
And the `users` table contains exactly the three users with ids `42`, `43` and `44`, and id `44` has `email` = `alan@example.com`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/members` with `Content-Type: application/json` and body exactly `{"user_id":44}`
Then the builder responds with HTTP status 201
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"project_id":7,"user_id":44,"role":"member"}`
And `SELECT project_id, user_id, role FROM project_members WHERE project_id = 7 AND user_id = 44` returns exactly `7 | 44 | member`
And `SELECT role FROM project_members WHERE project_id = 7 AND user_id = 42` returns exactly `owner`
And `SELECT count(*) FROM users WHERE id = 44` returns `1`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `3`

#### Scenario: A member who is not the owner cannot add a member
Given project `7` exists with `owner_id` = `42`
And Grace has `project_members` row `7 | 43 | member` and is not the owner
And the `project_members` table has no row `7 | 44 | member`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects/7/members` with `Content-Type: application/json` and body exactly `{"user_id":44}`
Then the builder responds with HTTP status 403
And the response body is exactly `{"error":{"code":"project_owner_required","message":"Only the project owner can change project membership."}}`
And `SELECT count(*) FROM project_members WHERE project_id = 7 AND user_id = 44` returns `0`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `2`

#### Scenario: A non-owner member's invalid body is refused by the owner check, not body validation
Given project `7` exists with `owner_id` = `42`
And Grace has `project_members` row `7 | 43 | member` and is not the owner
And Ada has `project_members` row `7 | 42 | owner`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects/7/members` with `Content-Type: application/json` and body exactly `{}`
Then the builder responds with HTTP status 403
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_owner_required","message":"Only the project owner can change project membership."}}`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `2`

#### Scenario: A non-member cannot add a member
Given project `7` exists with `owner_id` = `42`
And Alan has no `project_members` row for project `7`
And Alan has a valid member session with local `users.id` = `44`
When Alan sends `POST https://builder.skillbuilder.internal/api/projects/7/members` with `Content-Type: application/json` and body exactly `{"user_id":43}`
Then the builder responds with HTTP status 403
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `2`

#### Scenario: Adding a user the FA-1 gate never admitted is refused
Given project `7` exists with `owner_id` = `42`
And `SELECT count(*) FROM users WHERE id = 999` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/members` with `Content-Type: application/json` and body exactly `{"user_id":999}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"member_not_skill_builder","message":"User 999 is not a skill-builder."}}`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `2`
And `SELECT count(*) FROM users WHERE id = 999` returns `0`

#### Scenario: Adding an existing member is a conflict
Given project `7` exists with `owner_id` = `42`
And Grace already has `project_members` row `7 | 43 | member`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/members` with `Content-Type: application/json` and body exactly `{"user_id":43}`
Then the builder responds with HTTP status 409
And the response body is exactly `{"error":{"code":"member_already_exists","message":"User 43 is already a member of project 7."}}`
And `SELECT count(*) FROM project_members WHERE project_id = 7 AND user_id = 43` returns `1`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `2`

#### Scenario: Adding a member without a user id is refused
Given project `7` exists with `owner_id` = `42`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/members` with `Content-Type: application/json` and body exactly `{}`
Then the builder responds with HTTP status 422
And the response body is exactly `{"error":{"code":"user_id_required","message":"A user_id is required."}}`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `2`

### Covered requirements (traceability)
- FR-025

### Out of scope
Creating or inviting a user who has never signed in; reading or administering the Cognito
`skill-builders` group; per-project roles beyond `owner` and `member`; bulk add; adding a second
owner or transferring ownership; changing a member's role; deleting a member (BSB-22-PENDING-3);
the project settings/members web page, the add-member picker and the `GET
/api/projects/{id}/members` read endpoint — no story in this epic delivers them, and epic-review
Finding 2 / Open questions 2 and 3 must assign them.

### Notes / dependencies
- Depends on BSB-22-PENDING-1 for the project record, its `projects.owner_id` and its owner
  `project_members` row, and on epic BSB-18 for the member session and the local `users` rows.
- This story delivers the membership **API** only. The add-member form and the picker that would
  list local `users` rows are not delivered by this epic (epic-review Finding 2 / Open questions 2
  and 3). The API request carries `user_id`. The builder never creates a `users` row here, so a
  person who has never signed in cannot be added.
- **Boundary for review:** the builder cannot read another person's current `skill-builders` group
  membership; it sees membership only on the requesting user's own token (BSB-18-PENDING-3). A
  `users` row is the durable FA-1 evidence of a past admitted sign-in. A person who has since left
  the group can still have a row, so this route cannot reject them at add time; their own requests
  are refused by BSB-18's per-request gate, and the membership row grants nothing. Rejecting a
  *former* member at add time would need a Cognito directory read that the architecture does not
  provide. The never-admitted case is rejected here (`member_not_skill_builder`). Whether this is
  the accepted add-time meaning of "a current skill-builder" is epic-review Finding 3 / Open
  question 4; this story does not decide it.
- Duplicate add is a 409 conflict, not an idempotent success, so the caller learns the row already
  exists. The owner's own `project_members` row is a membership row too, so adding the owner
  returns the same 409 with the owner's id, not a second row.
- The `project_members` primary key on `(project_id, user_id)` is what makes the duplicate check
  race-free.
- BSB-22-PENDING-3 removes the rows this story creates, BSB-22-PENDING-4 reads them to
  authorize a run start, and BSB-22-PENDING-5 distinguishes them from the owner.

---

## STORY: BSB-22-PENDING-3

**Summary:** Owner removes a project member
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-4, MVP

### Story
As a **skill author who owns a project**, I want **to remove a member from the project**, so that **someone who should no longer use the project's sandbox and test credentials loses access to it**.

### Acceptance Criteria

#### Scenario: Owner removes a member
Given project `7` exists with `owner_id` = `42`
And the `project_members` table contains exactly `7 | 42 | owner`, `7 | 43 | member` and `8 | 43 | owner`
And Grace has `project_members` row `7 | 43 | member`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `DELETE https://builder.skillbuilder.internal/api/projects/7/members/43`
Then the builder responds with HTTP status 204
And the response body is exactly 0 bytes
And `SELECT count(*) FROM project_members WHERE project_id = 7 AND user_id = 43` returns `0`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `1`
And `SELECT project_id, user_id, role FROM project_members WHERE project_id = 7` returns exactly `7 | 42 | owner`
And `SELECT count(*) FROM users WHERE id = 43` returns `1`
And `SELECT count(*) FROM project_members WHERE project_id = 8 AND user_id = 43` returns `1`

#### Scenario: The owner cannot remove their own membership
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `DELETE https://builder.skillbuilder.internal/api/projects/7/members/42`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"owner_cannot_be_removed","message":"The project owner cannot be removed; ownership transfer is not supported."}}`
And `SELECT project_id, user_id, role FROM project_members WHERE project_id = 7 AND user_id = 42` returns exactly `7 | 42 | owner`
And `SELECT owner_id FROM projects WHERE id = 7` returns `42`

#### Scenario: A member who is not the owner cannot remove a member
Given project `7` exists with `owner_id` = `42`
And Grace has `project_members` row `7 | 43 | member` and is not the owner
And Ada has `project_members` row `7 | 42 | owner`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `DELETE https://builder.skillbuilder.internal/api/projects/7/members/42`
Then the builder responds with HTTP status 403
And the response body is exactly `{"error":{"code":"project_owner_required","message":"Only the project owner can change project membership."}}`
And `SELECT project_id, user_id, role FROM project_members WHERE project_id = 7 AND user_id = 42` returns exactly `7 | 42 | owner`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `2`

#### Scenario: A non-member cannot remove a member
Given project `7` exists with `owner_id` = `42`
And Alan has no `project_members` row for project `7`
And Grace has `project_members` row `7 | 43 | member`
And Alan has a valid member session with local `users.id` = `44`
When Alan sends `DELETE https://builder.skillbuilder.internal/api/projects/7/members/43`
Then the builder responds with HTTP status 403
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM project_members WHERE project_id = 7 AND user_id = 43` returns `1`

#### Scenario: Removing a user who is not a member is refused
Given project `7` exists with `owner_id` = `42`
And the `project_members` table has no row `7 | 44 | member`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `DELETE https://builder.skillbuilder.internal/api/projects/7/members/44`
Then the builder responds with HTTP status 404
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"member_not_found","message":"User 44 is not a member of project 7."}}`
And `SELECT count(*) FROM project_members WHERE project_id = 7` returns `2`

### Covered requirements (traceability)
- FR-026

### Out of scope
Ownership transfer (an explicit non-goal) or any way to remove the owner; deleting the project;
deleting or deactivating the `users` row; deleting or reassigning the removed member's builds and
runs; a transfer flow; changing a member's role; the project settings/members web page and the
remove control — no story in this epic delivers them, and epic-review Finding 2 / Open question 2
must assign them.

### Notes / dependencies
- Depends on BSB-22-PENDING-1 for the project and its owner row, on BSB-22-PENDING-2 for the
  member row being removed, and on epic BSB-18 for the member session and local `users` rows.
- The owner also has a `project_members` row with `role` = `owner`. That row is a membership row,
  so the removal route must refuse it; the 422 `owner_cannot_be_removed` response is the epic's
  stated edge case ("an owner cannot be removed from their own project without a transfer flow,
  which is out of scope").
- Removal deletes only the `project_members` row. The `users` row, the member's membership of other
  projects, and existing builds and runs are untouched (asserted in the first scenario for user
  `43`, who remains owner of project `8`).
- Removal takes effect on the target's next request because BSB-22-PENDING-4 reads
  `project_members` on every run or scan start, on every path listed in BSB-22-PENDING-4. A removed
  member's existing session is not revoked here; the BSB-18 gate still authenticates them, and
  only the project check refuses them.
- Membership and ownership failures are distinct: a non-member caller gets 403
  `project_membership_required`, while a member who is not the owner gets 403
  `project_owner_required`; a non-member target gets 404 `member_not_found`.

---

## STORY: BSB-22-PENDING-4

**Summary:** Membership guard admits project members and refuses non-members at every run start
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **skill author who is a project member**, I want **the run-start path to admit me and refuse anyone outside the project**, so that **I can test my skill against the project's sandbox while non-members cannot start a run there**.

### Acceptance Criteria

#### Scenario: A project member is admitted by the run-start membership guard
Given project `7` exists with `owner_id` = `42`
And Grace has `project_members` row `7 | 43 | member`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/grace/fix-reproduce","input_branch":"main"}`
Then the builder does not respond with HTTP status `403`
And the response body does not contain the string `project_membership_required`
And the response body does not contain the string `project_owner_required`
And the membership guard reads `SELECT role FROM project_members WHERE project_id = 7 AND user_id = 43`, which returns exactly `member`

#### Scenario: A non-member cannot start a run
Given project `7` exists with `owner_id` = `42`
And Alan has no `project_members` row for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Alan has a valid member session with local `users.id` = `44`
When Alan sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/alan/fix-reproduce","input_branch":"main"}`
Then the builder responds with HTTP status 403
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A removed member cannot start a run
Given project `7` exists with `owner_id` = `42`
And the `project_members` table contains exactly `7 | 42 | owner` and `8 | 43 | owner`, the state BSB-22-PENDING-3 leaves after removing Grace from project `7`
And `SELECT count(*) FROM project_members WHERE project_id = 7 AND user_id = 43` returns `0`
And `SELECT count(*) FROM runs` returns `0`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/grace/fix-reproduce","input_branch":"main"}`
Then the builder responds with HTTP status 403
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A run start against a missing project is refused
Given `SELECT count(*) FROM projects WHERE id = 999` returns `0`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/999/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main"}`
Then the builder responds with HTTP status 404
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_not_found","message":"Project 999 does not exist."}}`
And `SELECT count(*) FROM runs` returns `0`

### Covered requirements (traceability)
- FR-027

### Out of scope
The run-start route's request and response contract, its success status and the `runs` row
columns (epic BSB-24, FR-037); the run setup form and its other fields, skill packaging,
run-branch preparation, run execution, guardrails, deadlines, re-runs and verdicts (epics BSB-24
to BSB-33); listing or reading runs; starting a static or LLM security scan (epics BSB-31 and
BSB-32); project membership management itself (BSB-22-PENDING-2 and BSB-22-PENDING-3).

### Notes / dependencies
- Depends on BSB-22-PENDING-1 for the project and its owner row, on BSB-22-PENDING-2 for member
  rows, on BSB-22-PENDING-3 for the removal the *removed member* scenario exercises, and on epic
  BSB-18 for the member session and local `users` rows.
- **Provides the guard epic BSB-24's run-start story (FR-037) applies.** This story owns the
  reusable `require_project_member` check: it reads the caller's `project_members` row for the
  path's `project_id`, admits the request when the row exists, and refuses it before any run row,
  bundle, branch or container work starts otherwise. BSB-24 owns `POST
  /api/projects/{project_id}/runs`, the run request and response contract, and the `runs` row's
  columns; its story must cite this guard and carry the admitted-path 201 and `runs` row
  assertions. The body above is a placeholder fixture until BSB-24 fixes the request, so only the
  fixture is re-pointed in a revise pass; the 403/404 bodies and the membership decision fixed here
  do not change. The success response and the `runs` row an admitted request produces are asserted
  by BSB-24's run-start story, not here.
- BSB-24's run form needs the caller's projects. The projects list read endpoint that would supply
  them is part of the web-surface gap recorded in the preamble (epic-review Finding 2 / Open
  question 2); this story does not define it.
- Every path that starts a run or a scan for a project applies this same `project_members` check,
  including re-runs and output chaining (BSB-27, FR-056 and FR-057), scans (BSB-31 and BSB-32,
  FR-092 and FR-093) and the CLI (BSB-37, FR-116 to FR-118). The check therefore belongs in the
  run/scan start service, not only in the HTTP route.
- The owner's `project_members` row with `role` = `owner` counts as membership; there is no
  separate owner bypass, so removing the owner would also remove their run access, which is why
  BSB-22-PENDING-3 refuses that removal.
- Membership is read from the durable `project_members` table on every request, not from the
  session or a cached claim. That is what makes the removed-member scenario hold immediately.
- A non-member is refused before any run row, bundle, branch or container work starts; the
  scenarios assert `SELECT count(*) FROM runs` = `0`.
- `project_not_found` is checked before membership, so an unknown project id returns 404
  regardless of which projects the caller belongs to.

---

## STORY: BSB-22-PENDING-5

**Summary:** Owner guard admits only the project owner on integration changes
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-4, MVP

### Story
As a **skill author who owns a project**, I want **only me to be able to change the project's integrations**, so that **other members cannot redirect or alter the project's test credentials and settings**.

### Acceptance Criteria

#### Scenario: The project owner is admitted by the integration owner guard
Given project `7` exists with `owner_id` = `42`
And Ada has `project_members` row `7 | 42 | owner`
And the `integrations` table contains exactly one row with `id` = `5`, `project_id` = `7`, `kind` = `jira`, `config` = `{"site_url":"https://old.atlassian.net","project_key":"OLD"}` and `secret_ref` = `skill-builder/7/jira`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `PUT https://builder.skillbuilder.internal/api/projects/7/integrations/jira` with `Content-Type: application/json` and body exactly `{"site_url":"https://test.atlassian.net","project_key":"TEST"}`
Then the builder does not respond with HTTP status `403`
And the response body does not contain the string `project_owner_required`
And the response body does not contain the string `project_membership_required`
And the owner guard reads `SELECT role FROM project_members WHERE project_id = 7 AND user_id = 42`, which returns exactly `owner`

#### Scenario: A member who is not the owner cannot change an integration
Given project `7` exists with `owner_id` = `42`
And Grace has `project_members` row `7 | 43 | member` and is not the owner
And the `integrations` table contains exactly one row with `project_id` = `7`, `kind` = `jira` and `config` = `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `PUT https://builder.skillbuilder.internal/api/projects/7/integrations/jira` with `Content-Type: application/json` and body exactly `{"site_url":"https://grace.atlassian.net","project_key":"GRACE"}`
Then the builder responds with HTTP status 403
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_owner_required","message":"Only the project owner can change project integrations."}}`
And `SELECT config FROM integrations WHERE project_id = 7 AND kind = 'jira'` equals the JSON value `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`
And `SELECT count(*) FROM integrations WHERE project_id = 7` returns `1`

#### Scenario: A non-member cannot change an integration
Given project `7` exists with `owner_id` = `42`
And Alan has no `project_members` row for project `7`
And the `integrations` table contains exactly one row with `project_id` = `7`, `kind` = `jira` and `config` = `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`
And Alan has a valid member session with local `users.id` = `44`
When Alan sends `PUT https://builder.skillbuilder.internal/api/projects/7/integrations/jira` with `Content-Type: application/json` and body exactly `{"site_url":"https://alan.atlassian.net","project_key":"ALAN"}`
Then the builder responds with HTTP status 403
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT config FROM integrations WHERE project_id = 7 AND kind = 'jira'` equals the JSON value `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`

#### Scenario: Owning one project does not grant integration rights on another
Given project `7` exists with `owner_id` = `42` and project `8` exists with `owner_id` = `43`
And Ada has `project_members` row `7 | 42 | owner` and no `project_members` row for project `8`
And the `integrations` table has no row for project `8`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `PUT https://builder.skillbuilder.internal/api/projects/8/integrations/jira` with `Content-Type: application/json` and body exactly `{"site_url":"https://ada.atlassian.net","project_key":"ADA"}`
Then the builder responds with HTTP status 403
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM integrations WHERE project_id = 8` returns `0`

### Covered requirements (traceability)
- FR-028

### Out of scope
The integration settings schema, validation, success status and response body, and the
`integrations` row write (epic BSB-23, FR-029 to FR-036); credential values, their verification and
the external secret store; MCP server definitions; creating, deleting or reading integrations; the
LLM-scan model setting's schema and route (FR-163), whose owning epic and owner-check placement
are epic-review Finding 4 / Open question 5; the GitHub repository-overlap warning.

### Notes / dependencies
- Depends on BSB-22-PENDING-1 for the project and its owner row, on BSB-22-PENDING-2 for the
  `member` role rows its non-owner scenario exercises, and on epic BSB-18 for the member session
  and local `users` rows.
- **Provides the guard epic BSB-23's integration-settings story (FR-029 to FR-036) applies.**
  This story owns the reusable `require_project_owner` check: an authenticated caller who is a
  member but not the owner gets 403 `project_owner_required`, and a caller who is not a member gets
  403 `project_membership_required`. BSB-23 owns the `PUT
  /api/projects/{project_id}/integrations/{kind}` request and response contract, its success
  status, and the `integrations` row; its story must cite this guard and carry the admitted-path
  200 and rewritten-config assertions. The body above is a placeholder fixture until BSB-23 fixes
  the request, so only the fixture is re-pointed in a revise pass; the 403 bodies and the
  owner/membership decision fixed here do not change. The success response and the rewritten
  `integrations` row an admitted request produces are asserted by BSB-23's integration-settings
  story, not here.
- FR-028 applies to every integration kind BSB-23 adds (`jira`, `github`, `ai_model`); this story
  uses the `jira` kind as the representative fixture.
- Ownership is per project. Ada owning project `7` grants her nothing on project `8`, and Grace
  owning project `8` while being a plain member of project `7` cannot change project `7`
  (the two member scenarios above).
- Credentials are never part of this contract. The request carries only non-secret settings, and
  `secret_ref` is unchanged by a settings update; the value lives in the external secret store
  (epic BSB-23).
- BSB-23's settings page needs the caller's projects. The projects list read endpoint that would
  supply them is part of the web-surface gap recorded in the preamble (epic-review Finding 2 /
  Open question 2); this story does not define it.
- Whether FR-028's owner check also covers the project's LLM-scan default model is epic-review
  Finding 4 / Open question 5; this story does not decide it.
- BSB-23's own decomposition must apply this same check to its integration routes; the 403 bodies
  fixed here are the contract it inherits.
