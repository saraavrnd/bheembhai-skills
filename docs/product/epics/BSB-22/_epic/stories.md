# Stories — BSB-22 (Test projects & membership)

Epic BSB-22 covers FR-023, FR-024, FR-025, FR-026, FR-027 and FR-028. Decomposed into 4 stories
below; coverage of all 6 requirements verified.

The four slices are journeys through one bounded test project: create it and own it, fill it with
teammates, let those members reach the project's run-start path while keeping outsiders out, and
keep its integrations under the owner's control. Each is a user-visible outcome, not a layer of a
project-management API. Ownership transfer and user, group and role administration are the epic's
non-goals and recur in each story's Out of scope.

> New stories use draft keys `BSB-22-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-22, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-22-PENDING-1

**Title:** Create a test project and become its owner
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **skill author**, I want **to create a test project and be recorded as its owner**, so that **I have a bounded place to run my skills with test data that I control**.

### Acceptance Criteria

Scenario: A signed-in author creates a project and is recorded as its owner
Given a signed-in skill author whose local "users" id is 42 and email is "ada@example.com", an empty "projects" table, an empty "project_members" table, a "projects" id sequence whose next value is 7, and a builder clock reading "2026-11-16T10:00:00Z"
When the author submits the project name "Project Atlas" on the create project form at "/projects/new" with POST "/projects"
Then the builder responds with HTTP 201 and a body containing "Project 7 Project Atlas created.", exactly one "projects" row exists with id 7, name "Project Atlas", owner_id 42 and created_at "2026-11-16T10:00:00Z", exactly one "project_members" row exists with project_id 7, user_id 42 and role "owner", and a follow-up GET "/projects/7" returns HTTP 200 rendering "Project Atlas", "Owner: ada@example.com" and "Members: ada@example.com (owner)"

Scenario: The creator is the owner even when the request names another user
Given a signed-in skill author whose local "users" id is 42 and email is "ada@example.com", another skill-builders user whose local "users" id is 43 and email is "bob@example.com", and an empty "projects" table
When the author submits the project name "Project Atlas" together with an extra "owner_id" field of 43 on POST "/projects"
Then the builder responds with HTTP 201, exactly one "projects" row exists for "Project Atlas" with owner_id 42, exactly one "project_members" row exists for that project with user_id 42 and role "owner", and no "project_members" row exists with user_id 43

Scenario: A blank project name is rejected
Given a signed-in skill author and an empty "projects" table
When the author submits a project name of "   " on the create project form at "/projects/new"
Then the builder responds with HTTP 422 and the message "A project name is required.", and creates no "projects" row and no "project_members" row

### Covered requirements (traceability)
- FR-023
- FR-024

### Out of scope
Adding or removing project members (BSB-22-PENDING-2); authorizing runs in the project
(BSB-22-PENDING-3); integration management (BSB-22-PENDING-4); transferring ownership; renaming or
deleting a project; changing a member's role; user, group and role administration; project
discovery beyond the minimal list of projects the author belongs to.

### Notes / dependencies
Depends on the access epic BSB-18 for the signed-in skill author, the local "users" row that
"projects.owner_id" references, and the per-request authorization middleware that gates every
route below. The durable system of record is the builder's own "projects" table (id, name,
owner_id, created_at) and "project_members" table (project_id, user_id, role) from ADR SK-001
section 9, not a placeholder. Creating the project and the owner's membership row is one
transaction: the authenticated user is always recorded as owner_id 42 and as the only "owner"
member, even when the request body carries another user's id, so ownership cannot be set from
submitted form fields.

The project page is served at GET "/projects/7". GET "/projects" is the minimal "Your projects"
list an author needs to select a project, and the epic's non-goal excludes discovery beyond that.
This story also defines the shared project-membership check the rest of the epic and the later
project-scoped epics reuse: the signed-in user must have a "project_members" row for the project,
otherwise the builder responds with HTTP 403 and the message "You are not a member of this
project." before returning any project data. BSB-22-PENDING-3 exercises that check on the
run-start path, and BSB-24, BSB-31, BSB-33 and BSB-37 reuse it. Ownership transfer, renaming,
deleting a project, and user, group or role administration are out of scope for this release.

---

## STORY: BSB-22-PENDING-2

**Title:** Add and remove project members
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-4, MVP

### Story
As a **project owner**, I want **to add skill-builders users to my project and remove them again**, so that **a small team can share the project while access stays under my control**.

### Acceptance Criteria

Scenario: The owner adds a known skill-builders user as a member
Given Project Atlas (id 7, owner_id 42) whose "project_members" table holds only the row with project_id 7, user_id 42 and role "owner", and builder users Ada (id 42, "ada@example.com") and Bob (id 43, "bob@example.com")
When Ada submits the email "bob@example.com" on the add-member form at "/projects/7/members/new" with POST "/projects/7/members"
Then the builder responds with HTTP 201 and a body containing "bob@example.com added to Project Atlas as a member.", exactly one "project_members" row exists with project_id 7, user_id 43 and role "member", GET "/projects/7" renders "bob@example.com (member)", and a follow-up GET "/projects" as Bob renders "Your projects" with a link to "Project Atlas"

Scenario: The owner removes a member and that member loses access
Given Project Atlas (id 7) whose "project_members" table holds rows (project_id 7, user_id 42, role "owner") and (project_id 7, user_id 43, role "member"), with Ada at user 42 and Bob at user 43
When Ada submits POST "/projects/7/members/43/delete"
Then the builder responds with HTTP 200 and a body containing "bob@example.com removed from Project Atlas.", no "project_members" row exists for project 7 and user 43, GET "/projects/7" no longer renders "bob@example.com", Bob's next GET "/projects/7" returns HTTP 403 with the message "You are not a member of this project.", and Bob's GET "/projects" does not list "Project Atlas"

Scenario: Adding an email with no builder account is refused
Given Project Atlas (id 7) owned by Ada (user 42), and no "users" row with email "carol@example.com"
When Ada submits the email "carol@example.com" on POST "/projects/7/members"
Then the builder responds with HTTP 422 and the message "No skill-builders user with email carol@example.com.", creates no "project_members" row for project 7, and creates no "users" row

Scenario: Adding an existing member is refused
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member"), and a "users" row for Bob with email "bob@example.com"
When Ada submits the email "bob@example.com" on POST "/projects/7/members"
Then the builder responds with HTTP 422 and the message "bob@example.com is already a member of this project.", and the "project_members" table still contains exactly one row for project 7 and user 43

Scenario: A non-owner member cannot add a member
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member"), and a builder user Carol (id 44, "carol@example.com")
When Bob submits the email "carol@example.com" on POST "/projects/7/members"
Then the builder responds with HTTP 403 and the message "Only the project owner can change project members.", and no "project_members" row exists for project 7 and user 44

Scenario: A non-owner member cannot remove a member
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member"), and Carol at user 44 has no "project_members" row for project 7
When Bob submits POST "/projects/7/members/44/delete"
Then the builder responds with HTTP 403 and the message "Only the project owner can change project members.", and no "project_members" row exists for project 7 and user 44

Scenario: The owner cannot remove themselves
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member")
When Ada submits POST "/projects/7/members/42/delete"
Then the builder responds with HTTP 422 and the message "The project owner cannot be removed from the project.", and the "project_members" row for project 7 and user 42 still exists

### Covered requirements (traceability)
- FR-025
- FR-026

### Out of scope
Creating a project and the project page (BSB-22-PENDING-1); authorizing runs in the project
(BSB-22-PENDING-3); integration changes (BSB-22-PENDING-4); transferring ownership; changing a
member's role; inviting people who have never signed in, or sending invitations and notifications;
creating builder accounts; user, group and role administration; project renaming or deletion.

### Notes / dependencies
Depends on BSB-22-PENDING-1 for the "projects" and "project_members" records, the project page and
the shared project-membership check, and on BSB-18 for the signed-in users and the local "users"
table. Member management is owner-only: this story defines the shared owner guard every
project-administration route uses. The signed-in user must first pass the project-membership check,
then must have a "project_members" row for the project with role "owner"; a member without that
role receives HTTP 403 and the message "Only the project owner can change project members."
BSB-23's integration configuration routes apply the same owner-only rule, with the message "Only
the project owner can change integrations." BSB-22-PENDING-4 exercises it there.

The add form identifies the target by email and looks the person up in the builder's own "users"
table; a single matching row is required, no match returns HTTP 422 and creates nothing, and this
flow never creates a "users" row. The builder has no Cognito directory or admin API (ADR SK-001
section 3), so "skill-builders user" here means a person with a builder account, which BSB-18
creates only after a successful sign-in as a current member of the "skill-builders" group. Current
group membership is enforced again on every request by BSB-18's middleware, so a person later
removed from the group cannot act on any project membership row they hold. Removing the owner is
refused rather than leaving the project with an owner_id and no owner membership row; ownership
transfer is out of scope for this release. Membership is per project: a member of Project Atlas has
no access to any other project.

---

## STORY: BSB-22-PENDING-3

**Title:** Let members reach the run-start path and keep non-members out
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **project member**, I want **to open my project's run-start page**, so that **I can start test runs in the project I belong to and people outside the project cannot**.

### Acceptance Criteria

Scenario: A project member opens the run-start page
Given Project Atlas (id 7) whose "project_members" table holds rows (project_id 7, user_id 42, role "owner") and (project_id 7, user_id 43, role "member"), with Bob at user 43
When Bob opens GET "/projects/7/runs/new"
Then the builder responds with HTTP 200 rendering the heading "Start a test run in Project Atlas" and the text "Project Atlas"

Scenario: The project owner also opens the run-start page
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member")
When Ada opens GET "/projects/7/runs/new"
Then the builder responds with HTTP 200 rendering the heading "Start a test run in Project Atlas"

Scenario: A signed-in non-member is refused the run-start page
Given Project Atlas (id 7) whose "project_members" table holds rows only for Ada (user 42, role "owner") and Bob (user 43, role "member"), and Carol (user 44) is a signed-in skill-builders user with no "project_members" row for project 7
When Carol opens GET "/projects/7/runs/new"
Then the builder responds with HTTP 403 and the message "You are not a member of this project.", and the response body does not contain "Project Atlas"

Scenario: A signed-in non-member cannot submit a run start
Given Project Atlas (id 7) whose "project_members" table holds rows only for Ada (user 42, role "owner") and Bob (user 43, role "member"), and Carol (user 44) is a signed-in skill-builders user with no "project_members" row for project 7
When Carol submits a run start for project 7 on POST "/projects/7/runs"
Then the builder responds with HTTP 403 and the message "You are not a member of this project.", and no "runs" row is created for project 7

Scenario: A removed member is refused the run-start page
Given Bob had the "project_members" row for project 7 and user 43, and the owner has since removed it so no "project_members" row exists for project 7 and user 43
When Bob opens GET "/projects/7/runs/new"
Then the builder responds with HTTP 403 and the message "You are not a member of this project.", and the response does not render the heading "Start a test run in Project Atlas"

### Covered requirements (traceability)
- FR-027

### Out of scope
Creating a project and the project page (BSB-22-PENDING-1); adding and removing members
(BSB-22-PENDING-2); integration changes (BSB-22-PENDING-4); the run-start input choices, run
record, packaging and execution (BSB-24 onward); security scans and their standalone entry points
(BSB-31, BSB-32); run reports (BSB-33); command-line runs (BSB-37).

### Notes / dependencies
Depends on BSB-22-PENDING-1 for the project, its "project_members" rows and the shared
project-membership check, and on BSB-22-PENDING-2 for adding and removing members. This story owns
the run-start entry point for a test project: GET "/projects/7/runs/new" serves the page that
BSB-24 completes with the skills branch, input branch, workflow and step context, model profile and
model tier choices (FR-145 to FR-150). Run creation and input selection are not part of this
story; the "runs" table is defined in ADR SK-001 section 9 and is BSB-24's system of record under
FR-037.

The authorization rule is the one BSB-22-PENDING-1 defines: a project member is a signed-in user
with a "project_members" row for the project, whatever its role, and a signed-in skill-builders
user without that row is refused with HTTP 403 and the message "You are not a member of this
project." before any project or run data is returned. An anonymous visitor is refused by BSB-18's
per-request middleware before this check runs. The check reads the current "project_members" rows
on every request, so removing a member takes effect on that person's next request without a new
sign-in. BSB-24 must apply the same check before returning any selection data or creating a run
(FR-037); BSB-31's standalone scans, BSB-33's reports and BSB-37's command line reuse it. The
project owner is a member for this purpose, so the owner passes the same check.

---

## STORY: BSB-22-PENDING-4

**Title:** Keep the project's integrations under the owner's control
**Epic:** BSB-22 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-4, MVP

### Story
As a **project owner**, I want **only myself to be able to change the project's integrations**, so that **members cannot change the credentials and endpoints every run in the project depends on**.

### Acceptance Criteria

Scenario: The owner sees the integrations management controls
Given Project Atlas (id 7) whose "project_members" table holds rows (project_id 7, user_id 42, role "owner") and (project_id 7, user_id 43, role "member"), and no integration configured for project 7
When Ada (user 42) opens GET "/projects/7/settings"
Then the builder responds with HTTP 200 rendering "Project Atlas", the section heading "Integrations", the text "No integrations configured yet.", the link "Add integration" whose target is "/projects/7/integrations/new", and the text "Only the project owner can change integrations."

Scenario: A non-owner member sees the integrations section read-only
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member")
When Bob (user 43) opens GET "/projects/7/settings"
Then the builder responds with HTTP 200 rendering the section heading "Integrations" and the text "Only the project owner can change integrations.", and the response contains no link whose text is "Add integration"

Scenario: A non-owner member cannot change an integration
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member")
When Bob submits a Jira integration configuration with site URL "https://example.atlassian.net" and project key "TEST" on POST "/projects/7/integrations"
Then the builder responds with HTTP 403 and the message "Only the project owner can change integrations.", and no "integrations" row is created for project 7

Scenario: A signed-in non-member is refused the settings page
Given Project Atlas (id 7) whose "project_members" table holds rows only for Ada (user 42, role "owner") and Bob (user 43, role "member"), and Carol (user 44) is a signed-in skill-builders user with no "project_members" row for project 7
When Carol (user 44) opens GET "/projects/7/settings"
Then the builder responds with HTTP 403 and the message "You are not a member of this project.", and the response body does not contain "Integrations"

### Covered requirements (traceability)
- FR-028

### Out of scope
Creating a project and the project page (BSB-22-PENDING-1); adding and removing members
(BSB-22-PENDING-2); authorizing runs (BSB-22-PENDING-3); the integration configuration fields,
credential references, credential verification and MCP definitions (BSB-23, FR-029 to FR-036,
FR-128, FR-129); secret-store administration and credential rotation; displaying credentials
(BSB-23 owns the redaction guarantee).

### Notes / dependencies
Depends on BSB-22-PENDING-1 for the project, the "project_members" rows and the shared
project-membership check, and on BSB-22-PENDING-2 for the owner guard. This story owns the project
settings page at GET "/projects/7/settings", its "Integrations" section and the owner-only
integration-management guard. The integration form, its configuration fields, the opaque secret
reference and the verification step are BSB-23 (FR-029 to FR-036, FR-128 and FR-129); BSB-23 must
call this guard on every integration change route, and "POST /projects/7/integrations" is the
representative guarded route used by this story's acceptance criteria.

The guard applies two checks in order. The project-membership check runs first: a signed-in user
without a "project_members" row for the project receives HTTP 403 and the message "You are not a
member of this project." and sees no project data. The owner check runs second: a member whose
"project_members" role is not "owner" receives HTTP 403 and the message "Only the project owner can
change integrations." on any change attempt, and the settings page is read-only for them.
Integration changes are refused before any configuration is read or written, so a refused change
leaves the project's integrations unchanged. The "integrations" table is defined in ADR SK-001
section 9 and belongs to BSB-23; this story creates no integration record. Integration
administration itself, credential handling and MCP definitions are not part of this epic.
