# Stories — BSB-43 (Test projects & membership)

Epic BSB-43 covers FR-023, FR-024, FR-025, FR-026, FR-027 and FR-028. It is decomposed into the
5 stories below; every one of those 6 requirements is covered by at least one story's acceptance
criteria.

**Prerequisite: identity and the authoring gate (FA-1 / BSB-39).** BSB-39 owns sign-in, the
builder's `users` table keyed by the Cognito `sub`, the `builder_session` cookie, and the
request-time check of the caller's current `skill-builders` group claim. Every route in this epic
is an authoring route and inherits that gate: a request with no valid session gets HTTP 401
`{"error":"authentication_required"}`, and a request whose current `cognito:groups` claim lacks
`skill-builders` gets HTTP 403 `{"error":"membership_required"}` before any project data is read
or written. The builder database is `postgres://builder-db:5432/skillbuilder`.

**Fixture accounts.** The Cognito fixture is BSB-39's:

| Account | Subject | Display name | Current `cognito:groups` | `users` row |
|---------|---------|--------------|--------------------------|-------------|
| `alice@example.test` | `sub-12345` | Alice Author | `["skill-builders"]` | `U_alice` |
| `bob@example.test` | `sub-67890` | Bob Builder | `["skill-builders"]` | `U_bob` |
| `casey@example.test` | `sub-99999` | Casey Newcomer | `["skill-builders"]` | `U_casey` |
| `dana@example.test` | `sub-13579` | *(no `name` claim)* | `["skill-builders"]` | `U_dana` |
| `erin@example.test` | `sub-11111` | Erin Ex-member | `[]` | `U_erin` |

`U_alice`, `U_bob`, `U_casey`, `U_dana` and `U_erin` in a payload stand for the actual `users.id`
UUID value read from the database (`SELECT id FROM users WHERE cognito_sub = 'sub-12345'` for
`U_alice`, and likewise for the other subjects); a test substitutes the value. Erin signed in while still in the `skill-builders` group, so her `users`
row exists, but her current claim no longer contains the group. Mallory (`sub-24680`,
`cognito:groups` `["platform-users"]`) has no `users` row and cannot sign in; she is not used by
this epic's scenarios.

**Fixture projects.** The fixture builder database contains these `projects` and
`project_members` rows and no others; scenarios add further membership rows only where their
`Given` says so:

| `projects.id` | `name` | `owner_id` | `created_at` | `project_members` |
|---------------|--------|------------|--------------|-------------------|
| `prj_H5mQ2rT8vX` | Research quality | `U_alice` | `2026-11-16T09:00:00+00:00` | `(U_alice, owner)` |
| `prj_K9pL3wN6zB` | Release notes | `U_dana` | `2026-11-16T09:05:00+00:00` | `(U_dana, owner)` |
| `prj_M2vQ8kT4xD` | Erin's notes | `U_erin` | `2026-11-16T09:10:00+00:00` | `(U_erin, owner)` |

**Owner record.** `projects.owner_id` is the durable owner. Creating a project inserts exactly one
`project_members` row with `role` `owner` for the creator in the same transaction. The database
allows at most one `role` `owner` row per project. No operation in this epic transfers ownership,
and the owner's own membership row cannot be deleted (BSB-43-PENDING-3). The owner is a member of
the project for every membership decision: `role` `owner` authorizes the same project access and
run-start authorization as `role` `member`.

**Request bodies.** Every `POST` and `PUT` JSON route in this epic takes
`Content-Type: application/json`; the scenarios show the exact JSON body. `DELETE` routes carry no
body.

**Project read contract.** `GET /api/projects` returns the projects in which the signed-in user
has a `project_members` row, ordered by `created_at` ascending and then `id` ascending, as an
object with a `projects` array whose entries carry `project_id`, `name`, `owner_id` and `role`.
`GET /api/projects/{project_id}` is
available to a project member and returns HTTP 200 with `project_id`, `name`, `owner_id`, `role`
(`owner` or `member`) and `can_start_run` (`true` exactly when the caller has a `project_members`
row for the project). A project that does not exist returns HTTP 404
`{"error":"project_not_found"}`; a project that exists but in which the caller has no
`project_members` row returns HTTP 403 `{"error":"project_membership_required"}`.
`GET /projects/{project_id}` renders the project page under the same rule and contains an element
with `data-testid="start-run"` whose text is exactly `Start run` and whose `href` is
`/projects/{project_id}/runs/new`; a non-member receives HTTP 403 with a body containing
`You are not a member of this test project`.

**Owner-only writes.** A project write is owner-only when the signed-in user's `users.id` is not
equal to `projects.owner_id`; it returns HTTP 403 `{"error":"owner_required"}` and changes no row.
The check reads `projects.owner_id`, the durable owner record. It answers `owner_required` for
every signed-in skill-builder who is not the owner, whether or not that user is a project member.

**Membership write contract.** `POST /api/projects/{project_id}/members` takes a JSON body with a
`user_id` field naming an existing `users.id` value; `DELETE /api/projects/{project_id}/members/{user_id}` removes the row. A
duplicate add is idempotent: HTTP 200 with the existing `role` and no second row (a first add is
HTTP 201). Removing the membership row whose `role` is `owner` is refused with HTTP 409
`{"error":"last_owner"}`. Removing a user with no membership row is HTTP 404
`{"error":"membership_not_found"}`. A target `user_id` with no `users` row is HTTP 404
`{"error":"user_not_found"}`; a target whose current identity-provider `cognito:groups` claim does
not contain `skill-builders` is HTTP 422 `{"error":"not_a_skill_builder"}`. Invalid project
references are HTTP 404 `{"error":"project_not_found"}`. `projects.owner_id` is never changed by a
membership write.

**Project settings and integration write contract.** `GET /projects/{project_id}/settings` is
available to a project member and renders the project settings container; a non-member receives
HTTP 403 with a body containing `You are not a member of this test project`. Its integration section
for each `kind` in `jira`, `github`, `ai_model` contains an element
`data-testid="integration-section-{kind}"`, and contains an element
`data-testid="integration-edit-{kind}"` only when the caller is the project owner. The write route
is `PUT /api/projects/{project_id}/integrations/{kind}` with a JSON body whose `config` field is an
object carrying non-secret configuration only. A successful write responds HTTP 200 with
`integration_id` matching `^int_[A-Za-z0-9]{10}$`, `project_id`, `kind` and `config`, and stores
at most one `integrations` row per `(project_id, kind)`; the row's `config` equals the submitted
object, and its `secret_ref` and `mcp` are NULL on a row created by this route. FA-5 (BSB-44) owns
the integration fields' meaning and validation, the secret reference, MCP definitions, credential
verification and display; this epic owns the owner-only guard, the settings container and the
`(project_id, kind)` identity of the row.

**Durable systems of record.** Project state lives in the builder database's `projects`,
`project_members` and `integrations` tables (SK-001 §9); a run's durable record is its `runs` row
(SK-001 §9). The acceptance criteria assert those rows, not a mock, cache or in-memory response
alone.

**Scope boundary with later epics.** FA-5 (BSB-44) fills the integrations container; FA-6
(BSB-45) implements the run form and run start and must reuse the membership decision this epic
defines; FA-11/FA-12 scans likewise authorize through project membership; FA-7/FA-8 own run
execution and terminal states. Project ownership transfer, user/group/role administration and
project deletion are out of scope for the product (PRD §4).

## Coverage summary

| Story | Requirements covered |
|-------|----------------------|
| BSB-43-PENDING-1 — Create a test project and become its owner | FR-023, FR-024 |
| BSB-43-PENDING-2 — Add a skill-builder member to a project | FR-025 |
| BSB-43-PENDING-3 — Remove a project member | FR-026 |
| BSB-43-PENDING-4 — Authorize starting a run through project membership | FR-027 |
| BSB-43-PENDING-5 — Restrict project integration changes to the owner | FR-028 |

> **Input note.** The epic was fetched as Jira issue `BSB-43` through the configured Atlassian MCP
> server (`jira_get_issue`: summary "Test projects & membership", status To Do, labels FA-4 and
> MVP, description matching this file; no comments, remote links or child issues). The run's
> placeholder work item `SkillBuilder-2` does not exist: the MCP `jira_get_issue` call rejects the
> key because it does not match the server's `^[A-Z][A-Z0-9_]+-\d+(?:-\d+)*$` pattern, and a JQL
> text search for `SkillBuilder-2` returns zero issues. This matches `docs/product/PRD.md` §8 and
> `docs/product/epics.md`; the placeholder work item contributes no scope here.

---

## STORY: BSB-43-PENDING-1

**Title:** Create a test project and become its owner
**Epic:** BSB-43 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **skill author**, I want **to create a test project**, so that **my team has a shared place to run skills against test systems**.

### Acceptance Criteria
Scenario: Create a project records the creator as its owner
Given Alice (`sub-12345`, `U_alice`) is signed in with a `builder_session` cookie and the `projects` table contains no row named `Design critique`
When Alice submits `POST /api/projects` with body `{"name":"Design critique"}`
Then the builder responds with HTTP 201 and a JSON body whose `project_id` matches `^prj_[A-Za-z0-9]{10}$`, whose `name` is `Design critique`, whose `owner_id` is `U_alice` and whose `created_at` is an ISO-8601 timestamp within 5 seconds of the test's start; let `P_new` be that `project_id`; the `projects` row with `id` `P_new` has `name` `Design critique` and `owner_id` `U_alice`; the `project_members` table contains exactly one row with `project_id` `P_new`, whose `user_id` is `U_alice` and whose `role` is `owner`; and a follow-up `GET /api/projects` by Alice returns a `projects` array containing an entry with `project_id` `P_new`, `name` `Design critique`, `owner_id` `U_alice` and `role` `owner`, containing `prj_H5mQ2rT8vX` with `role` `owner`, and containing no entry for `prj_K9pL3wN6zB` or `prj_M2vQ8kT4xD`; and a follow-up `GET /projects/{P_new}` by Alice returns HTTP 200 with HTML containing the text `Design critique`

Scenario: Unauthenticated create is rejected
Given a visitor with no `builder_session` cookie
When the visitor submits `POST /api/projects` with body `{"name":"Design critique"}`
Then the builder responds with HTTP 401 and body exactly `{"error":"authentication_required"}`, and the `projects` table contains no row named `Design critique`

Scenario: A non-skill-builder cannot create a project
Given Erin (`sub-11111`, `U_erin`) is signed in with a `builder_session` cookie and her current `cognito:groups` claim is `[]`
When Erin submits `POST /api/projects` with body `{"name":"Design critique"}`
Then the builder responds with HTTP 403 and body exactly `{"error":"membership_required"}`, and the `projects` table contains no row named `Design critique`

Scenario: An empty project name is rejected
Given Alice (`U_alice`) is signed in with a `builder_session` cookie
When Alice submits `POST /api/projects` with body `{"name":"   "}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_project_name"}`, and the `projects` table gains no row for `owner_id` `U_alice`

### Covered requirements (traceability)
- FR-023
- FR-024

### Out of scope
Renaming or editing a project after creation, project deletion and ownership transfer; adding or removing members (BSB-43-PENDING-2 and BSB-43-PENDING-3); project integrations and settings fields (BSB-43-PENDING-5 and FA-5 / BSB-44); builds, runs and scans.

### Notes / dependencies
Depends on FA-1 (BSB-39) for the local `users` row keyed by `sub-12345`, the `builder_session` cookie and the request-time `skill-builders` gate. The durable records are the `projects` row (with `owner_id`) and the creator's `project_members` row with `role` `owner`, written in one transaction (SK-001 §9). `projects.owner_id` is the owner record used by every later story's owner check; the `project_members` owner row is the membership row that makes the owner a member. The one-owner invariant is a database constraint on `project_members`, and no story in this epic transfers ownership. The project list is the read surface the later stories use to confirm a membership.

---

## STORY: BSB-43-PENDING-2

**Title:** Add a skill-builder member to a project
**Epic:** BSB-43 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **test-project owner**, I want **to add another skill-builder as a project member**, so that **my teammates can run skills in our shared project**.

### Acceptance Criteria
Scenario: The owner adds a current skill-builder as a member
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `project_members` table has no row for `prj_H5mQ2rT8vX` and Bob (`U_bob`), and Bob's current `cognito:groups` claim is `["skill-builders"]`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/members` with body `{"user_id":"U_bob"}`
Then the builder responds with HTTP 201 and a JSON body whose `project_id` is `prj_H5mQ2rT8vX`, whose `user_id` is `U_bob` and whose `role` is `member`; the `project_members` table contains exactly one row for `prj_H5mQ2rT8vX` and `U_bob` with `role` `member`; and a follow-up `GET /api/projects` by Bob returns a `projects` array containing an entry with `project_id` `prj_H5mQ2rT8vX` and `role` `member`

Scenario: Adding the same member twice is idempotent
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Bob (`U_bob`) already has a `project_members` row for it with `role` `member`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/members` with body `{"user_id":"U_bob"}` again
Then the builder responds with HTTP 200 and a JSON body whose `project_id` is `prj_H5mQ2rT8vX`, `user_id` is `U_bob` and `role` is `member`, and the `project_members` table still contains exactly one row for `prj_H5mQ2rT8vX` and `U_bob` with `role` `member`

Scenario: A non-owner member cannot add a member
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and Casey (`U_casey`) is a current skill-builder with no `project_members` row for it
When Bob submits `POST /api/projects/prj_H5mQ2rT8vX/members` with body `{"user_id":"U_casey"}`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, and the `project_members` table contains no row for `prj_H5mQ2rT8vX` and `U_casey`

Scenario: A non-member cannot add a member
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Casey (`U_casey`) is a current skill-builder with no `project_members` row for it, and Bob (`U_bob`) is a current skill-builder with no `project_members` row for it
When Casey submits `POST /api/projects/prj_H5mQ2rT8vX/members` with body `{"user_id":"U_bob"}`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, and the `project_members` table contains no row for `prj_H5mQ2rT8vX` and `U_bob`

Scenario: A target who is not a current skill-builder is refused
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Erin (`U_erin`) has a `users` row but her current `cognito:groups` claim is `[]`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/members` with body `{"user_id":"U_erin"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"not_a_skill_builder"}`, and the `project_members` table contains no row for `prj_H5mQ2rT8vX` and `U_erin`

Scenario: An unknown user id is refused
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`)
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/members` with body `{"user_id":"00000000-0000-4000-8000-000000000000"}`
Then the builder responds with HTTP 404 and body exactly `{"error":"user_not_found"}`, and the `project_members` table contains no row with `user_id` `00000000-0000-4000-8000-000000000000`

### Covered requirements (traceability)
- FR-025

### Out of scope
Removing a member (BSB-43-PENDING-3); ownership transfer; inviting by email or creating a user account (the target must already have a `users` row created by FA-1 sign-in); administering group or role membership (FA-1 and the external identity provider); project integrations (BSB-43-PENDING-5).

### Notes / dependencies
Depends on BSB-43-PENDING-1 for the project, its owner and the owner's `project_members` row, and on FA-1 (BSB-39) for the target user's `users` row and current group claim. The owner check is `projects.owner_id`; the caller's `project_members` role is not the authorization source for a write. The target's current claim is read from the identity provider at add time (the Cognito user directory is an external prerequisite, as in BSB-39), so a user removed from `skill-builders` cannot be added even though a `users` row remains (the FR-141 gate). Only existing `users` rows can be added; the owner supplies `user_id` and there is no email invitation in this product. The inserted row is the durable membership record used by BSB-43-PENDING-3 and BSB-43-PENDING-4.

---

## STORY: BSB-43-PENDING-3

**Title:** Remove a project member
**Epic:** BSB-43 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **test-project owner**, I want **to remove a member from my project**, so that **someone who no longer needs access cannot run skills there**.

### Acceptance Criteria
Scenario: The owner removes a member
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and Bob's `GET /api/projects` currently lists `prj_H5mQ2rT8vX`
When Alice submits `DELETE /api/projects/prj_H5mQ2rT8vX/members/U_bob`
Then the builder responds with HTTP 204 and an empty body; the `project_members` table contains no row for `prj_H5mQ2rT8vX` and `U_bob`; the `projects` row for `prj_H5mQ2rT8vX` still has `owner_id` `U_alice`; and a follow-up `GET /api/projects` by Bob returns a `projects` array containing no entry for `prj_H5mQ2rT8vX`

Scenario: A non-owner member cannot remove a member
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), and Bob (`U_bob`) and Casey (`U_casey`) each have a `project_members` row for it with `role` `member`
When Bob submits `DELETE /api/projects/prj_H5mQ2rT8vX/members/U_casey`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, and the `project_members` table still contains both the `U_bob` row and the `U_casey` row for `prj_H5mQ2rT8vX`

Scenario: A non-member cannot remove a member
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and Casey (`U_casey`) has no `project_members` row for it
When Casey submits `DELETE /api/projects/prj_H5mQ2rT8vX/members/U_bob`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, and the `project_members` table still contains the `U_bob` row for `prj_H5mQ2rT8vX`

Scenario: Removing the owner is refused as the last-owner removal
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and her `project_members` row for it has `role` `owner`
When Alice submits `DELETE /api/projects/prj_H5mQ2rT8vX/members/U_alice`
Then the builder responds with HTTP 409 and body exactly `{"error":"last_owner"}`, the `project_members` table still contains Alice's row with `role` `owner`, the `projects` row still has `owner_id` `U_alice`, and the `project_members` table contains exactly one row for `prj_H5mQ2rT8vX` with `role` `owner`

Scenario: Removing a user who is not a member is refused
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Casey (`U_casey`) has no `project_members` row for it
When Alice submits `DELETE /api/projects/prj_H5mQ2rT8vX/members/U_casey`
Then the builder responds with HTTP 404 and body exactly `{"error":"membership_not_found"}`, and the `project_members` table still contains exactly the `prj_H5mQ2rT8vX`/`U_alice` owner row

Scenario: Removing a member with an in-flight run leaves the run untouched
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and the `runs` table contains a row with `id` `run_8Qm3Rt5Vw`, `project_id` `prj_H5mQ2rT8vX`, `user_id` `U_bob`, `skill` `sdlc-research-summarise` and `state` `running`
When Alice submits `DELETE /api/projects/prj_H5mQ2rT8vX/members/U_bob`
Then the builder responds with HTTP 204; the `project_members` table contains no row for `prj_H5mQ2rT8vX` and `U_bob`; and the `runs` row with `id` `run_8Qm3Rt5Vw` still exists with `project_id` `prj_H5mQ2rT8vX`, `user_id` `U_bob`, `skill` `sdlc-research-summarise` and `state` `running`

### Covered requirements (traceability)
- FR-026

### Out of scope
Adding a member (BSB-43-PENDING-2); cancelling, deleting or otherwise advancing an in-flight run (FA-7 / BSB-48 and FA-8 / BSB-49 own run execution and terminal states); ownership transfer; project deletion; administering the user's `skill-builders` group membership.

### Notes / dependencies
Depends on BSB-43-PENDING-1 for the project and owner record and on BSB-43-PENDING-2 for the membership row being removed. Removal deletes only the `project_members` row; it never changes `projects.owner_id` and never touches a `runs` row, so an in-flight run can reach its own terminal state under FA-7/FA-8. The refusal to remove the `role` `owner` row is the last-owner rule and preserves the one-owner invariant while ownership transfer is out of scope. New starts after a removal are denied by BSB-43-PENDING-4's membership decision; the removed run itself is not cancelled here. An owner who loses `skill-builders` membership is handled by FA-1's request-time gate (BSB-39-PENDING-4), not by this story.

---

## STORY: BSB-43-PENDING-4

**Title:** Authorize starting a run through project membership
**Epic:** BSB-43 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **test-project owner**, I want **only project members to reach the project and its Start run action**, so that **someone outside the team cannot run skills with our test systems**.

### Acceptance Criteria
Scenario: A member is authorized to start a run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Bob (`U_bob`) has a `project_members` row for it with `role` `member`
When Bob requests `GET /api/projects/prj_H5mQ2rT8vX` and `GET /projects/prj_H5mQ2rT8vX` with his `builder_session` cookie
Then the API responds with HTTP 200 and a JSON body whose `project_id` is `prj_H5mQ2rT8vX`, `role` is `member` and `can_start_run` is `true`; the page responds with HTTP 200 and its HTML contains an element with `data-testid="start-run"` whose text is exactly `Start run` and whose `href` is exactly `/projects/prj_H5mQ2rT8vX/runs/new`

Scenario: The owner is authorized to start a run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and her `project_members` row for it has `role` `owner`
When Alice requests `GET /api/projects/prj_H5mQ2rT8vX` and `GET /projects/prj_H5mQ2rT8vX` with her `builder_session` cookie
Then the API responds with HTTP 200 and a JSON body whose `role` is `owner` and `can_start_run` is `true`, and the page responds with HTTP 200 and contains an element with `data-testid="start-run"` whose text is exactly `Start run`

Scenario: A skill-builder who is not a project member is denied
Given Casey (`U_casey`) is a current skill-builder with no `project_members` row for `prj_H5mQ2rT8vX`
When Casey requests `GET /api/projects/prj_H5mQ2rT8vX` and `GET /projects/prj_H5mQ2rT8vX` with her `builder_session` cookie
Then the API responds with HTTP 403 and body exactly `{"error":"project_membership_required"}`, the page responds with HTTP 403 with a body containing `You are not a member of this test project`, and neither response contains the text `Research quality`, the value `U_alice`, or an element with `data-testid="start-run"`

Scenario: The owner of another project is denied
Given Dana (`U_dana`) owns `prj_K9pL3wN6zB` and has no `project_members` row for `prj_H5mQ2rT8vX`
When Dana requests `GET /api/projects/prj_H5mQ2rT8vX` and `GET /projects/prj_H5mQ2rT8vX` with her `builder_session` cookie
Then the API responds with HTTP 403 and body exactly `{"error":"project_membership_required"}`, the page responds with HTTP 403 with a body containing `You are not a member of this test project`, and neither response contains an element with `data-testid="start-run"`

Scenario: A removed member loses the start authorization
Given Bob (`U_bob`) previously had a `project_members` row for `prj_H5mQ2rT8vX` and Alice (`U_alice`) has removed it
When Bob requests `GET /api/projects/prj_H5mQ2rT8vX` and `GET /projects/prj_H5mQ2rT8vX` with his `builder_session` cookie
Then the API responds with HTTP 403 and body exactly `{"error":"project_membership_required"}`, the page responds with HTTP 403 with a body containing `You are not a member of this test project`, and neither response contains an element with `data-testid="start-run"`

Scenario: An owner who lost skill-builders membership is denied by the authoring gate
Given Erin (`U_erin`) owns `prj_M2vQ8kT4xD` and her current `cognito:groups` claim is `[]`
When Erin requests `GET /api/projects/prj_M2vQ8kT4xD` with her `builder_session` cookie
Then the builder responds with HTTP 403 and body exactly `{"error":"membership_required"}`, and the response contains no project data

### Covered requirements (traceability)
- FR-027

### Out of scope
Creating, preparing or executing a run, and the run form's input fields (FA-6 / BSB-45 and FA-7 / BSB-48); the run-start submit endpoint itself; scans and their start surfaces (FA-11 / FA-12 use the same project-membership decision); adding or removing members (BSB-43-PENDING-2 and BSB-43-PENDING-3); builds.

### Notes / dependencies
Depends on BSB-43-PENDING-1 for the project and owner record and on BSB-43-PENDING-2/3 for membership rows. `can_start_run` is derived on read from the caller's `project_members` row and is never stored, so a removed member cannot retain it. The run form at `/projects/{project_id}/runs/new` and the run-start endpoint are FA-6 (BSB-45); BSB-45 must call the same project-membership decision this story defines, and FA-11/FA-12 must do the same for scan starts, rather than re-implementing the check. The project page's Start run action is the user-visible surface of that decision; the run form itself and the run `runs` row are outside this story. The owner-lost-group scenario is the epic's edge case and is enforced by FA-1's request-time gate before the project-membership check.

---

## STORY: BSB-43-PENDING-5

**Title:** Restrict project integration changes to the owner
**Epic:** BSB-43 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **test-project owner**, I want **only me to change my project's integrations**, so that **a teammate cannot point the project at different test systems or expose credentials**.

### Acceptance Criteria
Scenario: The owner changes a project integration
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"} }`
Then the builder responds with HTTP 200 and a JSON body whose `integration_id` matches `^int_[A-Za-z0-9]{10}$`, whose `project_id` is `prj_H5mQ2rT8vX`, whose `kind` is `jira` and whose `config` equals `{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"}`; the `integrations` table contains exactly one row for `prj_H5mQ2rT8vX` and `kind` `jira`, with that `integration_id`, that `config`, `secret_ref` NULL and `mcp` NULL

Scenario: The owner updates one kind without changing another
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira` and `config` `{"site_url":"https://alice-test.atlassian.net","project_key":"OLD"}`, and contains a row for `prj_H5mQ2rT8vX` with `kind` `ai_model` and `config` `{"vendor":"anthropic","tier_models":{"fast":"claude-haiku-5-5"} }`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"CHANGED"} }`
Then the builder responds with HTTP 200 with a JSON body whose `kind` is `jira` and whose `config` equals `{"site_url":"https://alice-test.atlassian.net","project_key":"CHANGED"}`; the `integrations` table still contains exactly one jira row for `prj_H5mQ2rT8vX`, whose `integration_id` is unchanged and whose `config` is the new object; and the `integrations` table still contains exactly one `ai_model` row for `prj_H5mQ2rT8vX` whose `integration_id` and `config` are unchanged

Scenario: A non-owner member cannot change an integration
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`
When Bob submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://bob-test.atlassian.net","project_key":"BOB"} }`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, and the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`

Scenario: A skill-builder who is not a project member cannot change an integration
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Casey (`U_casey`) has no `project_members` row for it, and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`
When Casey submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://casey-test.atlassian.net","project_key":"CASEY"} }`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, and the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`

Scenario: The owner of another project cannot change this project's integrations
Given Dana (`U_dana`) owns `prj_K9pL3wN6zB` and has no `project_members` row for `prj_H5mQ2rT8vX`, and `prj_K9pL3wN6zB` has no `integrations` row with `kind` `jira`
When Dana submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://dana-test.atlassian.net","project_key":"DANA"} }`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the `integrations` table contains no row for `prj_K9pL3wN6zB` with `kind` `jira`

Scenario: The settings page shows integration edit controls only to the owner
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Bob (`U_bob`) has a `project_members` row for it with `role` `member`
When Alice requests `GET /projects/prj_H5mQ2rT8vX/settings` and Bob requests `GET /projects/prj_H5mQ2rT8vX/settings` with their `builder_session` cookies
Then both requests respond with HTTP 200; Alice's HTML contains an element with `data-testid="integration-section-jira"` and an element with `data-testid="integration-edit-jira"`; and Bob's HTML contains an element with `data-testid="integration-section-jira"` but no element with `data-testid="integration-edit-jira"`

### Covered requirements (traceability)
- FR-028

### Out of scope
The integration fields' meaning, required fields and validation; credential values and the external secret store; `secret_ref` contents; MCP server definitions; credential verification and `verified_at`; the repository-overlap warning; model profile tier mapping and model validation (all FA-5 / BSB-44); displaying non-owner project settings beyond the edit affordance; ownership transfer; builds, runs and scans.

### Notes / dependencies
Depends on BSB-43-PENDING-1 for the project and its `projects.owner_id` owner record. The project settings container is the one the epic's implementation guidance assigns to FA-4; FA-5 (BSB-44) fills it with the Jira, source-control and model integrations, and its integration CRUD must call the same owner guard rather than re-implement it (BSB-44's epic depends on FA-4 for exactly this). This story owns the owner-only guard, the settings page's owner-only edit affordance, and the `(project_id, kind)` identity and non-secret `config` of the `integrations` row; BSB-44 owns everything about the integration's contents and credentials. The owner check reads `projects.owner_id`, so a member's `project_members` row never authorizes an integration write. An owner who loses `skill-builders` membership is denied by FA-1's request-time gate before the owner check (BSB-39-PENDING-4).
