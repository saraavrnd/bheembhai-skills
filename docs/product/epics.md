```yaml bheembhai:foreach
epics:
  - id: BSB-18
    epic_key: BSB-18
    summary: "Access, identity & the authoring gate"
    feature_area: FA-1
    release: MVP
  - id: BSB-19
    epic_key: BSB-19
    summary: "Skill build creation & scaffolding"
    feature_area: FA-2
    release: MVP
  - id: BSB-20
    epic_key: BSB-20
    summary: "Skill cloning & edit builds"
    feature_area: FA-2
    release: MVP
  - id: BSB-21
    epic_key: BSB-21
    summary: "Skill editing, build state & readiness tracking"
    feature_area: FA-3
    release: MVP
  - id: BSB-22
    epic_key: BSB-22
    summary: "Test projects & membership"
    feature_area: FA-4
    release: MVP
  - id: BSB-23
    epic_key: BSB-23
    summary: "Integrations, credentials & MCP definitions"
    feature_area: FA-5
    release: MVP
  - id: BSB-31
    epic_key: BSB-31
    summary: "Static security scanning"
    feature_area: FA-11
    release: MVP
  - id: BSB-32
    epic_key: BSB-32
    summary: "LLM security scanning"
    feature_area: FA-12
    release: MVP
  - id: BSB-24
    epic_key: BSB-24
    summary: "Run start & input selection"
    feature_area: FA-6
    release: MVP
  - id: BSB-25
    epic_key: BSB-25
    summary: "Skill packaging & run branch preparation"
    feature_area: FA-6
    release: MVP
  - id: BSB-26
    epic_key: BSB-26
    summary: "Run execution & outcome capture"
    feature_area: FA-7
    release: MVP
  - id: BSB-27
    epic_key: BSB-27
    summary: "Run guardrails, deadlines & re-runs"
    feature_area: FA-8
    release: MVP
  - id: BSB-29
    epic_key: BSB-29
    summary: "Run verification & verdicts"
    feature_area: FA-10
    release: MVP
  - id: BSB-30
    epic_key: BSB-30
    summary: "Readiness checks & re-verification"
    feature_area: FA-10
    release: MVP
  - id: BSB-33
    epic_key: BSB-33
    summary: "Run report & change evidence"
    feature_area: FA-13
    release: MVP
  - id: BSB-34
    epic_key: BSB-34
    summary: "Run usage, trace & data retention"
    feature_area: FA-13
    release: MVP
  - id: BSB-28
    epic_key: BSB-28
    summary: "Jira fixture seeding"
    feature_area: FA-9
    release: Later
  - id: BSB-35
    epic_key: BSB-35
    summary: "Skill history & run comparison"
    feature_area: FA-14
    release: Later
  - id: BSB-36
    epic_key: BSB-36
    summary: "Catalog submission"
    feature_area: FA-15
    release: MVP
  - id: BSB-37
    epic_key: BSB-37
    summary: "Command line & saved suites"
    feature_area: FA-16
    release: mixed
  - id: BSB-38
    epic_key: BSB-38
    summary: "Accessibility conformance"
    feature_area: FA-17
    release: MVP
```

# Epics — decomposed from the SkillBuilder PRD

**Source:** `docs/product/PRD.md` · **Work item:** SkillBuilder-2 · **Target project:** `BSB` · **Epics:** 21 · **Coverage:** all 165 FRs and 19 NFRs mapped to exactly one epic.

> **Source note.** The configured Atlassian site was queried through the Atlassian MCP for the
> work item `SkillBuilder-2`. No project key `SKILLBUILDER` and no issue `SKILLBUILDER-2` exists;
> the accessible projects are BEEM, BSB, EX, GRAP and LNPRTL, and `BSB` (bheembhai-skill-builder)
> contains only the 21 previously published planning epics. The PRD records the same result in
> §8. This decomposition is therefore grounded in `docs/product/PRD.md`, which in turn is grounded
> in `docs/adr/SK-001-skill-builder.md`. Reconcile against a Jira description if one is supplied later.
>
> **Keys.** Every epic's draft key has been replaced with its real Jira key by `sdlc-tracker-sync`;
> split feature areas use `A`/`B` suffixes so each key stays unique. The real key appears in
> `epic-map.json`, in the machine block above, and in each section heading. The per-epic fan-out
> reads the block above.
>
> **Order.** Epics are ordered by dependency: identity and build authoring first, then project and
> integration setup, then the security and run pipeline, then evidence and submission, then the
> Later slices and the cross-cutting accessibility pass. Each epic body names the epics it depends on.

---

## EPIC: Access, identity & the authoring gate  (BSB-18)
**Feature area:** FA-1 · **Release:** MVP · **Labels:** FA-1, MVP

### Description
Every later capability in the builder is reached by a person, so this epic establishes the trust
boundary around the product. Skill authors are already known to the platform, and the platform
administrator manages membership of the externally owned skill-builders group. The builder must
admit only a signed-in user who is a current member of that group, re-check that membership on
every request rather than trusting a stale sign-in, and anchor all subsequent ownership and
membership decisions to one stable local user record. The builder consumes the platform identity
provider and the group claim; it administers neither, and it must never read or write the
platform's own database. The value is that an author can work in the builder without widening the
trusted audience or copying platform identity data into another store.

### Functional scope
- Reject an unauthenticated visitor before any authoring page or builder data is returned.
- Sign a user in with the platform's existing identity-provider credentials.
- Permit authoring features only while the signed-in user is a current member of the
  skill-builders group, and reject a non-member's sign-in attempt.
- Re-evaluate the skill-builders membership claim on every request, and deny access no later than
  one hour after a user is removed from the group.
- Create exactly one local user record per identity-provider subject on first successful sign-in,
  and reuse that record on later sign-ins.
- Keep the builder isolated from the platform database: it reads and writes only its own records.
- Cover the cross-cutting request-level security requirements that every builder endpoint inherits.
- Non-goals: user, group and role administration, password management, and any write to platform
  identity or project data.

### Implementation guidance / dependency order
1. Integrate the existing identity provider and establish the signed-in session contract.
2. Add the local user upsert keyed by identity-provider subject; this record is the prerequisite
   every later ownership, project-membership and authorship relation references.
3. Add one shared per-request authorization middleware that enforces authentication and current
   skill-builders membership before any handler runs; do not duplicate the check per page.
4. Apply the middleware to every authoring route, including page, API and later command-line
   entry points, then add denial responses that do not leak builder data.
5. Add the external group-removal propagation window (one hour) and verify it with a
   membership-change case.
6. Confirm the builder has no platform-database client or credential path.

### Goal / Definition of Done
An anonymous visitor and a signed-in non-member cannot reach any authoring surface or retrieve
builder data; a current member can sign in once and is admitted; each identity-provider subject
maps to exactly one reused local user record; a removed member is denied within an hour; and the
builder holds no connection to the platform database. No later epic has to re-implement identity
or per-request authorization.

### Covered requirements (traceability)
- FR-001 — Unauthenticated visitors cannot open authoring pages.
- FR-002 — Sign-in uses the platform identity provider's credentials.
- FR-003 — Authoring requires current skill-builders group membership.
- FR-004 — Membership is checked on every request, not only at sign-in.
- FR-005 — One local user record is created per identity-provider subject at first sign-in.
- FR-138 — Non-member sign-in attempts are rejected.
- FR-141 — Removed group members are denied within one hour.
- FR-142 — The existing local user record is reused on later sign-ins.
- FR-165 — The builder never reads or writes the platform database.
- NFR-002 — Requests without a valid session are rejected before builder data is returned.
- NFR-003 — Requests from signed-in non-members are rejected.

### Notes
Depends on external prerequisites: the platform identity provider and the skill-builders group,
both managed outside this product. Every other epic depends on the local user record and the
per-request authorization middleware built here. The group-removal window is an acceptance
boundary, not an invitation to cache membership indefinitely: the check must remain correct for
each request within that window. No group or role administration is in scope.

---

## EPIC: Skill build creation & scaffolding  (BSB-19)
**Feature area:** FA-2 · **Release:** MVP · **Labels:** FA-2, MVP

### Description
A skill author needs a safe starting point before they can edit or test anything. This epic lets
an author create a build from a skill name and a one-line description, cuts a dedicated build
branch from the current head of `main` in the catalog repository, and scaffolds a valid skill
folder on that branch. The scaffold is not an empty directory: it contains `SKILL.md` with the
skill's frontmatter, a `verify.yaml` stub, and the standard references, templates and examples
folders, and it must pass the catalog's static manifest checks without any edit. The same epic
enforces the naming rules that keep catalog skill names consistent and collision-free. The value
is that a new skill begins from a known-good, catalog-compatible shape rather than from an author's
guesswork.

### Functional scope
- Accept a skill name and one-line description and create a build record owned by the signed-in
  author.
- Create the build branch from the current head of `main`.
- Scaffold the skill's own folder under the catalog's skills directory on the build branch,
  including `SKILL.md` with frontmatter, a `verify.yaml` stub, and the standard references,
  templates and examples folders.
- Ensure a newly scaffolded skill passes the catalog's static manifest checks with no manual edit.
- Validate the skill name against the required `sdlc` prefix, area segment and action segment
  pattern, and reject invalid names.
- Reject a name that already exists on `main` and a name already used by another open build.
- Non-goals: cloning an existing skill and editing an existing catalog skill (both in the
  cloning and edit-build epic); running the skill or submitting it to the catalog.

### Implementation guidance / dependency order
1. Define the build record and its authorship link to the local user, so branch, head and
   readiness state have an owner from the start.
2. Implement name parsing and validation first; the name determines the skill folder path and is
   shared with clone and edit flows.
3. Add branch creation from the resolved head of `main`; record that base SHA on the build.
4. Implement one idempotent scaffold writer that emits the folder, frontmatter, verify stub and
   standard subfolders.
5. Run the catalog's static manifest check against the generated scaffold in verification, then
   expose the create-build flow in the authoring interface.
6. Add the uniqueness checks against `main` and against other open builds at creation time, with
   a clear rejection message.

### Goal / Definition of Done
An author can provide a name and description, receive a build on a branch cut from `main`, and
find a catalog-shaped skill folder whose unedited scaffold passes the static manifest checks.
Invalid, duplicate-on-main and open-build names are rejected before a branch is created. The build
record exposes the branch and base SHA that the editing, run and submission epics consume.

### Covered requirements (traceability)
- FR-006 — An author creates a build from a skill name and one-line description.
- FR-007 — The build branch is created from the current head of `main`.
- FR-008 — The skill's own folder is scaffolded on the build branch.
- FR-009 — The scaffold contains `SKILL.md` with the skill frontmatter.
- FR-010 — A new scaffold passes the catalog's static manifest checks unedited.
- FR-015 — A create or clone build is rejected when the name exists on `main`.
- FR-016 — A build is rejected when another open build uses the name.
- FR-017 — Names must follow the `sdlc` prefix, area segment and action segment pattern.
- FR-143 — The scaffold contains a `verify.yaml` stub.
- FR-144 — The scaffold contains the standard references, templates and examples folders.

### Notes
Depends on access and the local user record from the access epic, and on the external catalog
repository and its manifest check. The name validator and scaffold writer are reused by the
cloning and edit-build epic; build head and readiness state are completed in the skill-editing
epic. This epic creates a build but does not make it Ready or submit it.

---

## EPIC: Skill cloning & edit builds  (BSB-20)
**Feature area:** FA-2 · **Release:** MVP · **Labels:** FA-2, MVP

### Description
Most real authoring starts from an existing skill rather than a blank page. This epic gives an
author two ways to derive a build from a catalog skill: clone it under a new name, or open an edit
build that changes the existing skill in place on a branch cut from `main`. Cloning copies the
whole skill folder, rewrites only the skill name in the copied frontmatter, and leaves the source
skill untouched. An edit build reuses the existing skill folder rather than creating a second one,
and is rejected when no such skill exists on `main`. The value is that authors can adapt proven
skills without hand-copying files, without corrupting the source, and without accidentally
forking one skill into two catalog entries.

### Functional scope
- Clone an existing catalog skill under a new name.
- Copy the skill's entire folder to the new skill path.
- Rewrite the skill name in the copied frontmatter, leaving the rest of the copied content intact.
- Leave the source skill's files unchanged in the catalog repository.
- Open an existing catalog skill in an edit build on a branch cut from `main`.
- Make an edit build modify the existing skill folder rather than create a second skill folder.
- Reject an edit build whose skill name does not exist on `main`.
- Reuse the build-creation name rules and open-build collision checks.
- Non-goals: editing file content after the build exists (skill-editing epic); merging the build
  into the catalog (catalog-submission epic).

### Implementation guidance / dependency order
1. Reuse the build-creation record and name validation; add a build mode that distinguishes
   clone, edit and new builds.
2. Implement whole-folder copy from the source skill path, preserving the directory structure and
   file contents.
3. Add frontmatter rewrite as a targeted operation, not a full-file regeneration, so unrelated
   content is preserved.
4. Implement source-immutability checks and assert them in verification.
5. Add edit-build resolution against the skill name on `main`, rejecting missing names and reusing
   the existing skill path.
6. Hand the resulting build to the skill-editing epic with its branch and base SHA recorded.

### Goal / Definition of Done
An author can clone a catalog skill under a new name and gets an independent copy whose
frontmatter name matches the new skill while the source remains byte-for-byte unchanged. An author
can open an edit build for an existing skill, and the branch changes that skill's existing folder;
a name absent from `main` is rejected. Both flows produce builds that follow the same edit, run,
scan, Ready and submit path as a newly created build.

### Covered requirements (traceability)
- FR-011 — An author clones an existing catalog skill under a new name.
- FR-012 — Cloning copies the skill's whole folder to the new path.
- FR-013 — Cloning rewrites the skill name in the copied frontmatter.
- FR-014 — Cloning leaves the source skill's files unchanged.
- FR-124 — An author opens an existing catalog skill in an edit build from `main`.
- FR-125 — An edit build changes the existing skill folder rather than creating another.
- FR-126 — An edit build is rejected when the skill name does not exist on `main`.

### Notes
Depends on build creation and scaffolding (build record, branch creation, name validation) and on
the access epic's local user. The catalog skill itself changes only when the catalog pull request
from the catalog-submission epic merges; an edit build never writes to `main` directly. Clone and
edit builds share the downstream run, scan, readiness and submission path.

---

## EPIC: Skill editing, build state & readiness tracking  (BSB-21)
**Feature area:** FA-3 · **Release:** MVP · **Labels:** FA-3, MVP

### Description
An author must be able to change a skill and trust that what they see is the exact content that
will be tested. This epic provides file editing inside the build's skill folder and makes every
save a commit on the build branch, so the branch is the single version history of the skill. It
also maintains the build's observable state: the latest commit SHA becomes the head, the build page
shows that head and the readiness status for it, and a new commit clears any previously recorded
Ready SHA. The value is that readiness can never be attributed to content the author has already
changed, which keeps the later verification, scan and submission decisions honest.

### Functional scope
- Let an author edit the content of a file in the build's skill folder.
- Save an edited file to the build branch as a commit.
- Create a commit on the build branch for each save, with no separate skill-content versioning.
- Record the latest commit SHA as the build head.
- Show the current head SHA on the build page.
- Show the build's readiness status for its head SHA.
- Clear the previously recorded ready SHA whenever a new commit moves the head.
- Non-goals: rich file management beyond editing files in the skill folder; line-level review;
  computing the readiness checks themselves (readiness epic).

### Implementation guidance / dependency order
1. Read files from the build branch at the recorded head so the editor is bound to a specific SHA.
2. Implement save as a commit on the build branch and make the commit the atomic unit of change.
3. Update the build head to the returned commit SHA on every successful save.
4. Model readiness as a status attached to a specific SHA, never to the build as a floating flag.
5. Add the invalidation rule: a head change clears the recorded ready SHA in the same transaction
   that moves the head.
6. Surface head SHA and per-SHA readiness on the build page, including the stale case where the
   head has moved past the last verified SHA.

### Goal / Definition of Done
An author can open a file in the build's skill folder, edit it and save, and the save appears as a
new commit on the build branch. The build page always shows the current head SHA and the readiness
status that belongs to that SHA. If the head moves after a Ready record, the Ready status is
cleared and the page no longer claims the build is ready.

### Covered requirements (traceability)
- FR-018 — Each save creates a commit on the build branch.
- FR-019 — The latest commit SHA is recorded as the build head.
- FR-020 — The build page shows the current head SHA.
- FR-021 — The build page shows the readiness status for its head SHA.
- FR-022 — A new commit clears the previously recorded ready SHA.
- FR-127 — An author edits a file in the build's skill folder.
- FR-162 — The author saves an edited file to the build branch.

### Notes
Depends on a build, its branch and its base SHA from build creation, and on the signed-in author
from the access epic. The readiness value itself is computed by the readiness epic; this epic
owns the head/ready association and its invalidation. Every save-triggered head change also
invalidates the evidence tied to the old SHA, so catalog submission must re-read readiness at the
current head.

---

## EPIC: Test projects & membership  (BSB-22)
**Feature area:** FA-4 · **Release:** MVP · **Labels:** FA-4, MVP

### Description
Authors need a shared, bounded place to run skills with test credentials, and the credentials and
configuration must have one accountable owner. This epic introduces the test project as the unit
of sharing: a signed-in author creates a project and becomes its owner, the owner adds or removes
other skill-builder users as members, and membership is the authorization basis for starting runs
in that project. Only the owner may change the project's integrations, which keeps credential and
endpoint configuration from drifting across members. The value is a small-team sandbox with clear
ownership, without building user, group or role administration into the product.

### Functional scope
- Create a test project from the authoring interface.
- Record the project creator as the project owner.
- Let the owner add another skill-builders user as a project member.
- Let the owner remove a project member.
- Authorize starting a test run in a project only for that project's members.
- Restrict changes to the project's integrations to the project owner.
- Non-goals: transferring project ownership, global user/group/role administration, and project
  discovery beyond what an author needs to select a test project.

### Implementation guidance / dependency order
1. Define the project record, its owner reference to the local user, and its membership relation.
2. Implement create-project and owner assignment in one transaction.
3. Add owner-only member add/remove operations, validating that the target user is a current
   skill-builders user.
4. Expose one reusable project-membership authorization check for run start, scans, reports and
   later command-line operations; do not let each feature invent its own rule.
5. Add the owner-only integration-management guard consumed by the integrations epic.

### Goal / Definition of Done
A signed-in author can create a test project and is recorded as its owner. The owner can add and
remove skill-builder users, and only members can start runs or scans in the project. A non-owner
member cannot change the project's integrations. Projects reference stable local user records and
do not create a parallel identity system.

### Covered requirements (traceability)
- FR-023 — A signed-in author creates a test project.
- FR-024 — The project creator is recorded as project owner.
- FR-025 — The owner adds another skill-builder user as a member.
- FR-026 — The owner removes a project member.
- FR-027 — Project membership authorizes starting a test run in the project.
- FR-028 — Only the project owner changes the project's integrations.

### Notes
Depends on the local user record and per-request authorization from the access epic. Every run,
scan, report and command-line epic that operates inside a project reuses the membership check
defined here. Integrations belong to a project and are owner-managed (integrations epic). Project
ownership transfer and role administration are deliberately out of scope for this release.

---

## EPIC: Integrations, credentials & MCP definitions  (BSB-23)
**Feature area:** FA-5 · **Release:** MVP · **Labels:** FA-5, MVP

### Description
A skill run has to reach Jira, a source-control sandbox and a model without the builder ever
holding a credential value. This epic lets a project owner declare those three integrations, keeps
each credential in an external secret store as an opaque reference, verifies that a reference
works, and records when it was last verified. It also stores the non-secret MCP server definitions
that the Jira and source-control integrations expose to a run. The builder warns when a
source-control integration points at a repository already used by a platform project, because that
is how production data gets touched by accident. The value is that authors can run skills against
realistic external systems while the product remains a store of configuration, not of secrets.

### Functional scope
- Configure a Jira integration with a site URL and either a project key or a template project.
- Configure a source-control integration with a sandbox repository and a base branch.
- Configure an AI model profile with a vendor, base URL and tier-to-model mapping.
- Keep every credential value in the external secret store; store only an opaque reference in the
  builder's records, logs, results and interface.
- Verify an integration's credentials and record the last verification time.
- Warn when a source-control integration targets a repository also used by a platform project.
- Never display a credential value in the interface.
- Record the MCP server definition exposed by the Jira integration and by the source-control
  integration; a definition is non-secret configuration, never a credential.
- Ensure runs use only test-purpose Jira, source-control and model credentials.
- Non-goals: secret-store administration, credential rotation policy, and any platform project
  configuration.

### Implementation guidance / dependency order
1. Define the integration record and its opaque secret reference; make the reference the only
   persisted link to a credential.
2. Add provider-specific configuration for Jira, source control and model profiles, validated
   against the owner's input.
3. Implement one verification path per provider that resolves the secret at call time, reports
   pass or fail without echoing the value, and stamps the last-verified time.
4. Add the MCP server definition fields to the Jira and source-control integrations and validate
   that they are non-secret.
5. Add the source-control overlap warning by reading the platform's repository inventory.
6. Enforce owner-only configuration changes using the project guard, and add redaction tests that
   search logs, results and interface responses for credential values.
7. Confirm the model-profile tier mapping is usable by run start and the LLM scan.

### Goal / Definition of Done
A project owner can configure and verify Jira, source-control and model integrations, and a
verified integration is usable by runs. No credential value appears in builder records, logs,
results or the interface, and the builder stores only an opaque reference. A source-control
integration targeting a platform-project repository produces a warning. MCP server definitions
are stored as non-secret configuration and are available to a run.

### Covered requirements (traceability)
- FR-029 — Jira integration stores site URL and project key or template project.
- FR-030 — Source-control integration stores sandbox repository and base branch.
- FR-031 — Model profile stores vendor, base URL and tier-to-model mapping.
- FR-032 — Credential values are never stored in builder records.
- FR-033 — The owner verifies an integration's credentials.
- FR-034 — The last credential verification time is recorded.
- FR-035 — A warning is raised for a repository shared with a platform project.
- FR-036 — Credential values are never displayed in the interface.
- FR-128 — The Jira integration records its MCP server definition.
- FR-129 — The source-control integration records its MCP server definition.
- NFR-004 — Credential values never appear in builder logs or run results.
- NFR-006 — Runs use only test-purpose Jira, source-control and model credentials.

### Notes
Depends on the test project and its owner-only integration guard from the test-projects epic.
Supplies configuration to run start, packaging, execution, static and LLM scanning, Jira fixture
seeding and catalog submission. External prerequisites: the secret store, the platform repository
inventory, the model endpoints, and the sandbox repository and its curated branches. The builder
stores references and non-secret definitions only; it never becomes a secret store.

---

## EPIC: Static security scanning  (BSB-31)
**Feature area:** FA-11 · **Release:** MVP · **Labels:** FA-11, MVP

### Description
Before a skill is allowed to run, its exact content must be scanned for static security problems,
and a failed scan must stop the run rather than merely warn. This epic runs the catalog's static
scanner in an isolated, network-less container against the content that will execute, reuses a
completed result when the content hash is unchanged, and defines narrowly what "passes" means:
not a `DO_NOT_INSTALL` recommendation, no critical finding, and complete scan coverage. An accepted
finding cannot override a block. A scan that exceeds ten minutes is recorded as failed. Authors
also need a standalone static-only scan from the skill page, and the builder's verdict must match
the platform's for identical content and scanner version. The value is a trustworthy hard gate
that behaves the same way in the builder as it will in production.

### Functional scope
- Run a static security scan on the exact skill content before every run.
- Reuse a completed static scan result when the content is unchanged.
- Treat a `DO_NOT_INSTALL` verdict as not passing.
- Treat a critical static finding as not passing.
- Treat incomplete scan coverage as not passing.
- Refuse to let an accepted finding clear a static-scan block.
- Time out a scan after ten minutes and record the timeout as failed.
- Show the scan's score, recommendation, and each finding's severity, rule, file and line in the
  static scan report.
- Match the platform's verdict for the same content and scanner version.
- Let an author start a static-only scan from the skill page for a test project the author belongs
  to, without a run.
- Run the static scan with no network access.
- Non-goals: model-based analysis (LLM scan epic), overriding a block, and changing the scanner's
  own rules.

### Implementation guidance / dependency order
1. Define the scan invocation contract: the exact content identity, the scanner version, and the
   isolated no-network execution environment.
2. Implement content hashing and result reuse before any UI, so repeated scans of unchanged content
   do not rescan.
3. Encode the pass/fail rules as one verdict function: recommendation, critical findings, coverage
   completeness, and accepted findings.
4. Add the ten-minute timeout and persist a timed-out scan as failed.
5. Build the report model (score, recommendation, findings with severity, rule, file, line) and the
   skill-page standalone scan entry point guarded by project membership.
6. Add parity tests against the platform's verdict for a fixed corpus and pinned scanner version.
7. Expose the verdict to run preflight and packaging; both must consume the same function.

### Goal / Definition of Done
Every run and every packaged skill is preceded by a static scan of the exact content, and a
non-passing verdict blocks the run and packaging. A `DO_NOT_INSTALL`, critical finding, incomplete
coverage, timeout or accepted-finding override never passes. Unchanged content reuses the prior
result. An author can trigger a standalone static scan from the skill page and read a report with
score, recommendation and located findings. The builder and platform agree on verdicts for the
same content and scanner version.

### Covered requirements (traceability)
- FR-076 — Static scan runs on the exact skill content before every run.
- FR-077 — A completed static scan result is reused when content is unchanged.
- FR-078 — `DO_NOT_INSTALL` is not a passing result.
- FR-079 — A critical static finding is not a passing result.
- FR-080 — Incomplete static scan coverage is not a passing result.
- FR-081 — An accepted finding cannot clear a static-scan block.
- FR-087 — A security scan times out after ten minutes.
- FR-088 — A timed-out scan is recorded as failed.
- FR-089 — The static scan report shows the scan score.
- FR-091 — The builder's verdict matches the platform's for the same content and scanner version.
- FR-092 — An author starts a static-only scan from the skill page without a run.
- FR-154 — The static scan report shows the scan recommendation.
- FR-155 — The static scan report lists each finding's severity, rule, file and line.
- NFR-005 — A static security scan has no network access.

### Notes
Depends on the build content from the authoring and editing epics, on project membership for the
standalone scan, and on the pinned static scanner image supplied externally. Its verdict is a
precondition for run start, packaging and readiness, and LLM scanning is triggered only after this
scan passes. The scanner's rules and the platform's parity baseline are external; the builder must
not redefine the scanner's policy. Later Jira fixture seeding does not change this gate.

---

## EPIC: LLM security scanning  (BSB-32)
**Feature area:** FA-12 · **Release:** MVP · **Labels:** FA-12, MVP

### Description
Static analysis cannot reason about intent, so authors get a second, model-based view of risky
skill content. This epic triggers the LLM scan only after the static scan has passed for the
current content, gives it no credential other than the model key, restricts it to the model
endpoint, and makes it strictly advisory: it never blocks a run. The scan uses the model profile
configured on the test project and reports which model ran it, with findings located by severity,
rule, file and line. When the scan cannot run it is recorded as unavailable rather than silently
missing. The value is additional, non-gating evidence for the author and the catalog reviewer
without letting a second security opinion stall delivery.

### Functional scope
- Trigger the LLM scan only after the static scan passes for the current content.
- Give the LLM scan no credential other than the model key.
- Restrict the LLM scan's network reachability to the model endpoint.
- Never block a run on the LLM scan's result.
- Show LLM scan findings to the author.
- Show which model ran the LLM scan.
- Record an LLM scan that cannot run as unavailable.
- List each finding's severity, rule, file and line in the LLM scan report.
- Let an author start a full security scan from the skill page for a test project the author
  belongs to, without a run.
- Use the LLM-scan model profile configured for the scan's test project.
- Non-goals: changing static-scan verdicts, allowing the LLM scan to override a static block, and
  per-run overrides of the scan model.

### Implementation guidance / dependency order
1. Define the LLM scan request as a consumer of the static scan verdict and the exact content
   identity; refuse to start before the static pass exists.
2. Resolve the project's LLM-scan model profile; do not accept a per-run model override.
3. Provision the scan sandbox with only the model key and a network allowlist for the model
   endpoint.
4. Implement unavailable classification for missing configuration, provider failure, or budget
   exhaustion; persist it as an outcome rather than dropping the scan.
5. Build the report model with model identity and findings, and surface it to the author.
6. Add the full-scan skill-page entry point guarded by project membership, triggering static then
   LLM for the same content.
7. Add tests proving a failing LLM scan cannot change a run's ability to start or finish.

### Goal / Definition of Done
For content whose static scan passed, an author can see an LLM scan result with the model that
produced it and located findings, or an explicit unavailable record. The LLM scan has only the
model key and can reach only the model endpoint. A failing or unavailable LLM scan never blocks a
run, and readiness can treat a complete or explicitly unavailable scan as satisfied. A full scan
started from the skill page runs both scans in the required order.

### Covered requirements (traceability)
- FR-082 — The LLM scan is triggered only after the static scan passes.
- FR-083 — The LLM scan receives no credential other than the model key.
- FR-084 — The LLM scan can reach only the model endpoint.
- FR-085 — The LLM scan never blocks a run.
- FR-086 — LLM scan findings are shown to the author.
- FR-090 — The LLM scan report shows which model ran the scan.
- FR-093 — An author starts a full security scan from the skill page without a run.
- FR-139 — An LLM scan that cannot run is recorded as unavailable.
- FR-156 — The LLM scan report lists each finding's severity, rule, file and line.
- FR-163 — A full security scan uses the project's configured LLM-scan model profile.

### Notes
Depends on the static security scanning epic's passing verdict, the integrations epic's model
profile, and project membership for the standalone scan. Readiness requires the LLM scan to be
complete or recorded as unavailable, so the unavailable path is a first-class state, not an error
page. The scan is advisory by design; no run gate, packaging rule or submission rule may depend on
its findings. Model endpoints are external prerequisites.

---

## EPIC: Run start & input selection  (BSB-24)
**Feature area:** FA-6 · **Release:** MVP · **Labels:** FA-6, MVP

### Description
A run is only meaningful if the author chooses the right content, branch, context and model for
the question they are asking. This epic provides the run-start surface: an author who is a member
of a test project selects the skills branch, the input branch, the workflow and step context, an
optional reviewer-feedback or upstream-handoff input, a model profile and a model tier. The epic
validates and records those choices and creates the run so that packaging can prepare immutable
inputs from them. The value is that a run is reproducible and explainable from its request, rather
than inheriting hidden defaults from whichever page the author happened to use.

### Functional scope
- Let an author start a run in a test project the author is a member of.
- Offer a choice of skills branch.
- Offer a choice of input branch.
- Offer a choice of workflow and step context.
- Optionally accept reviewer feedback or an upstream handoff as run input.
- Offer a choice of model profile.
- Offer a choice of model tier.
- Validate the selections against the project's configured integrations and the sandbox
  repository, then create the run request that packaging will consume.
- Non-goals: packaging or executing the skill (later epics); automatically choosing defaults that
  the author cannot see or override; writing to the input branch.

### Implementation guidance / dependency order
1. Define the run-request record with the selected skills branch, input branch, workflow/step
   context, optional feedback or handoff, model profile and model tier.
2. Reuse the project-membership authorization check before any selection data is returned.
3. Populate branch choices from the source-control integration and the curated sandbox branches.
4. Populate workflow and step context choices from the platform's workflow definitions, and model
   profile and tier choices from the project's model integration.
5. Validate that the selection is internally consistent, persist the request immutably, and hand
   it to packaging.
6. Add the interface flow with explicit summaries of the chosen inputs before the run is created.

### Goal / Definition of Done
A project member can start a run by explicitly choosing every input that affects its outcome:
skills branch, input branch, workflow and step context, optional feedback or handoff, model profile
and model tier. A non-member cannot start a run. The created run records the selections that
packaging and execution will use, and the input branch is treated as read-only from the start.

### Covered requirements (traceability)
- FR-037 — An author starts a run in a test project the author belongs to.
- FR-145 — A run start offers a choice of skills branch.
- FR-146 — A run start offers a choice of input branch.
- FR-147 — A run start offers a choice of workflow and step context.
- FR-148 — A run start optionally accepts reviewer feedback or an upstream handoff.
- FR-149 — A run start offers a choice of model profile.
- FR-150 — A run start offers a choice of model tier.

### Notes
Depends on the test-project membership check, the source-control and model integrations, and the
externally supplied sandbox branches and platform workflow definitions. It produces a run request
but does not package or execute content. The selected skills branch and input branch are resolved
to commits by the packaging epic; the input branch is never written to. A later-run flow may
reuse a prior output branch here as an input (guardrails and re-runs epic).

---

## EPIC: Skill packaging & run branch preparation  (BSB-25)
**Feature area:** FA-6 · **Release:** MVP · **Labels:** FA-6, MVP

### Description
An author's selected branches are moving references, so a run must pin exactly what it tests
before execution begins. This epic resolves the skills branch to a commit SHA, packages that
commit into a content-addressed bundle, reuses the bundle when the same skills commit is packaged
again, and creates the run's output branch from the input branch's head. It records the input
branch head as the run's baseline and guarantees that the run never writes to its input branch.
Packaging is deterministic and must stay fast enough for regular authoring. The value is an
immutable, reproducible input and an isolated output branch, which make verification, diffing,
security scanning and re-runs honest.

### Functional scope
- Resolve the skills branch to a commit SHA at run start.
- Package the skill at that commit into a content-addressed bundle.
- Reuse an existing bundle when the same skills commit is packaged again.
- Create the run branch, which is the run's output branch, from the input branch's head.
- Record the input branch's head SHA as the run's baseline.
- Guarantee that a run never writes to its input branch.
- Keep non-model run preparation within 60 seconds for a skill bundle up to 5 MB.
- Produce an identical bundle when the same skills commit is prepared twice.
- Non-goals: executing the skill, grading it, and writing to the input branch or `main`.

### Implementation guidance / dependency order
1. Resolve the skills branch to a commit SHA and freeze that SHA in the run record before doing
   any packaging work.
2. Define a canonical bundle format and a content-addressed key derived from the resolved skills
   commit and packaging rules; canonicalization is what makes the bundle reproducible.
3. Implement bundle build behind the key, with an existence check first so an identical commit
   reuses the stored bundle.
4. Create the run/output branch from the input branch head and record the input head as baseline.
5. Add isolation enforcement so every run-time write target is the output branch and the input
   branch ref is read-only.
6. Add the preparation performance and determinism checks at the intended 5 MB bundle size.
7. Hand the pinned bundle, output branch and baseline SHA to execution, verification and scanning.

### Goal / Definition of Done
Starting a run resolves the skills branch to a SHA and produces, or reuses, a content-addressed
bundle for that exact commit. The run has an output branch created from the input head and a
recorded baseline SHA. The same skills commit prepared twice yields an identical bundle and reuses
the stored one. A 5 MB bundle prepares within 60 seconds for non-model work. No run path can write
to the input branch.

### Covered requirements (traceability)
- FR-038 — The skills branch is resolved to a commit SHA at run start.
- FR-039 — The skill at that commit is packaged into a content-addressed bundle.
- FR-040 — An existing bundle is reused for the same skills commit.
- FR-041 — The run branch is created from the input branch head.
- FR-042 — The input branch head is recorded as the run baseline.
- FR-043 — A run never writes to its input branch.
- NFR-001 — Non-model run preparation completes within 60 seconds for a 5 MB bundle.
- NFR-009 — The same skills commit produces an identical bundle twice.

### Notes
Depends on the run request and selected branches from run start, and on the source-control
integration from the integrations epic. Supplies the pinned bundle and baseline to execution,
static scanning, verification and the run report; the output branch can later become another run's
input branch. The 60-second and 5 MB values are acceptance thresholds proposed by the PRD, not
ADR-given commitments. Curated input branches in the sandbox repository are external inputs.

---

## EPIC: Run execution & outcome capture  (BSB-26)
**Feature area:** FA-7 · **Release:** MVP · **Labels:** FA-7, MVP

### Description
This epic actually runs one skill in the platform's runtime, on the packaged bundle and output
branch, and captures enough about the execution to explain its result. While the run is in
progress the author can see progress and logs. When it finishes, the builder classifies the
outcome with the platform engine's rules and records the exact execution-component versions, the
verifier version, the model profile and the model tier that were used. The value is that a run is
not a black box: its process is observable while it happens and its inputs and components are
pinned in the record afterwards, which is what later verification and reproduction rely on.

### Functional scope
- Execute the skill in the same runtime as the platform.
- Show run progress while the run executes.
- Show run logs while the run executes.
- Classify the run outcome using the platform engine's result rules.
- Record the exact execution-component versions used by the run.
- Record the verifier version used by the run.
- Record the model profile used by the run.
- Record the model tier used by the run.
- Emit the run's output on the output branch and a final status that downstream verification can
  act on.
- Non-goals: verifying the run's claims (verification epic), applying cost and time caps
  (guardrails epic), and exposing the full report (run report epic).

### Implementation guidance / dependency order
1. Integrate the platform's runtime adapter so the builder invokes the same execution path as the
   platform rather than a builder-specific imitation.
2. Stream progress and logs from the runtime into the run's live view without storing credential
   values.
3. Persist execution-component versions and the verifier version at run start/end so they describe
   the actual execution.
4. Capture the selected model profile and tier from the run request into the run record.
5. Classify the final outcome with the platform engine's result rules and persist both the status
   and the agent's claimed verdict for verification to compare.
6. Expose the terminal state and output-branch ref to verification, scanning and reporting.

### Goal / Definition of Done
A packaged skill runs in the platform's runtime, and an author can watch progress and logs while
it executes. The run reaches a classified outcome and records the exact execution-component
versions, verifier version, model profile and model tier. Its output is on its own output branch
and its terminal status is available to verification and reporting.

### Covered requirements (traceability)
- FR-044 — The builder executes the skill in the platform's runtime.
- FR-045 — The run page shows progress while the run executes.
- FR-046 — The run page shows logs while the run executes.
- FR-047 — The run outcome is classified using the platform engine's result rules.
- FR-048 — The exact execution-component versions are recorded.
- FR-049 — The model profile used by the run is recorded.
- FR-151 — The exact verifier version used by the run is recorded.
- FR-152 — The model tier used by the run is recorded.

### Notes
Depends on the packaged bundle, output branch and baseline from packaging, and on the model
profile and tier selected at run start. Pinned agent, scanner and verifier images are external
prerequisites. Execution hands off to verification, which runs outside the agent container, and to
the guardrails epic for caps and deadlines. The claim recorded here is not the final verdict; the
verification epic owns that distinction.

---

## EPIC: Run guardrails, deadlines & re-runs  (BSB-27)
**Feature area:** FA-8 · **Release:** MVP · **Labels:** FA-8, MVP

### Description
Test runs must be bounded and repeatable. This epic lets an author set turn and spend caps, stops
a run when either cap is reached, refuses to start a run whose execution components are
incompatible or whose skill content did not pass the static scan, and enforces an
installation-configured deadline so every run reaches a terminal state. It also supports the
iterate-and-chain loop: re-run a prior run with the same inputs against the latest commit of its
skills branch, and use a prior run's output branch as the input branch of a later run. The value
is that authors can explore safely, cannot burn unbounded time or spend, and can build multi-step
experiments without hand-copying run configuration.

### Functional scope
- Let the author set a turn cap for a run and stop the run when it is reached.
- Let the author set a spend cap for a run and stop the run when it is reached.
- Refuse to start a run when its execution components are incompatible.
- Refuse to start a run when the static scan for the skill content did not pass.
- Re-run a prior run with the same inputs and the latest commit of its skills branch.
- Use a prior run's output branch as the input branch of a later run.
- Ensure every run reaches a terminal state within its configured deadline.
- Record a run that exceeds its configured deadline as failed.
- Allow the run deadline to be changed per installation without a code change.
- Non-goals: nightly scheduling and saved suites (command-line and suites epic); changing the
  platform's component compatibility rules; authoring per-run installation settings.

### Implementation guidance / dependency order
1. Add turn and spend caps to the run request with validation and explicit units.
2. Enforce caps from the execution telemetry path and stop the run with a recorded reason when a
   cap is reached.
3. Add a preflight that rejects incompatible execution components before a bundle or branch is
   prepared, and add the static-scan precondition using the scanning epic's verdict function.
4. Implement a deadline from an environment-supplied installation setting, with a watchdog that
   marks overdue runs failed and reaches a terminal state even if the runtime is unresponsive.
5. Implement re-run by copying the prior run's resolved inputs while re-resolving the skills branch
   to its latest commit; never reuse a stale bundle for a new commit.
6. Implement output-branch chaining by creating a later run whose input branch is the prior run's
   output branch, preserving the later run's baseline rules.
7. Add tests for cap-stop, deadline-stop, incompatible-component refusal and scan-gate refusal.

### Goal / Definition of Done
A run stops when it reaches its turn cap or spend cap, and a run that exceeds the installation
deadline is recorded as failed and reaches a terminal state. A run with incompatible components or
a non-passing static scan is refused before execution. An author can re-run a prior run against
the latest skills commit and can chain a prior output branch into a later run. The deadline is
changed by installation configuration without a code change.

### Covered requirements (traceability)
- FR-050 — The author sets a turn cap for a run.
- FR-051 — A run stops when it reaches its turn cap.
- FR-052 — The author sets a spend cap for a run.
- FR-053 — A run stops when it reaches its spend cap.
- FR-054 — A run is refused when execution components are incompatible.
- FR-055 — A run is refused when the static scan did not pass.
- FR-056 — A prior run can be re-run with the same inputs at the latest skills commit.
- FR-057 — A prior run's output branch can be a later run's input branch.
- NFR-007 — Every run reaches a terminal state within its configured deadline.
- NFR-008 — A run exceeding its deadline is recorded as failed.
- NFR-019 — The run deadline is changeable per installation without a code change.

### Notes
Depends on run start, packaging, execution and the static security scanning verdict. The deadline
and retention settings are installation-level operator settings supplied through environment
variables, not author-editable per run; no single numeric default is fixed by the PRD. Re-runs
reuse the original inputs but must re-package a moved skills branch, and chained runs still treat
their input branch as read-only. Saved suites and nightly scheduling are deferred to the
command-line and suites epic.

---

## EPIC: Run verification & verdicts  (BSB-29)
**Feature area:** FA-10 · **Release:** MVP · **Labels:** FA-10, MVP

### Description
An agent's own claim about whether it succeeded is evidence, not the answer. This epic runs the
shared verification layer on the run branch after the agent exits, passing the run's baseline SHA
and the `verify.yaml` from the skills commit, and records both the verdict the agent claimed and
the final verdict produced by the verifier. It records whether verification overturned the claim.
The final verdict is the shared layer's verdict, not the builder's reimplementation, and the same
inputs and component versions must produce the same result. The value is a grade the author and
the catalog reviewer can trust, produced outside the agent's control.

### Functional scope
- Run the shared verification layer on the run branch after the agent exits.
- Pass the run's baseline SHA to the verifier.
- Pass the `verify.yaml` from the skills commit to the verifier.
- Record the verdict the agent claimed.
- Record the final verdict after verification.
- Record whether verification overturned the agent's claimed verdict.
- Record the final verdict as the verdict produced by the shared verification layer.
- Produce the same verification result for the same inputs and component versions.
- Run verification outside the agent container so the agent cannot edit what grades it.
- Non-goals: computing readiness across checks (readiness epic), changing verifier checks, and
  re-verifying with a changed `verify.yaml` (readiness and re-verification epic).

### Implementation guidance / dependency order
1. Define the verification invocation contract: run branch, baseline SHA, skills commit's
   `verify.yaml`, and the pinned verifier version.
2. Integrate the shared verification layer as an external package; do not copy its checks into
   the builder.
3. Invoke verification outside the agent container after the agent process exits, so the run
   cannot influence the grader.
4. Persist the agent's claimed verdict before verification, then the final verdict and the
   overturned flag after it.
5. Persist the check-level results and the component versions that produced them, for readiness,
   the run report and re-verification.
6. Add reproducibility tests that replay the same inputs and component versions and compare
   verdicts.

### Goal / Definition of Done
After every agent run, the shared verification layer grades the run branch using the baseline SHA
and the skills commit's `verify.yaml`, outside the agent's reach. The run record contains the
agent's claimed verdict, the final verifier verdict and whether the verdict was overturned. The
final verdict is always the shared layer's output. Repeating the same inputs and component
versions produces the same verification result.

### Covered requirements (traceability)
- FR-063 — The shared verification layer runs on the run branch after the agent exits.
- FR-064 — The verifier receives the run's baseline SHA.
- FR-065 — The verdict the agent claimed is recorded.
- FR-066 — The final verdict after verification is recorded.
- FR-067 — Whether verification overturned the claimed verdict is recorded.
- FR-153 — The verifier receives the `verify.yaml` from the skills commit.
- FR-164 — The final verdict is the shared verification layer's verdict.
- NFR-010 — The same inputs and component versions produce the same verification result.

### Notes
Depends on the packaged baseline and output branch, the executed run and its claimed verdict, and
the pinned verifier version from execution. The shared verification layer is a third-party
dependency sourced from the Bheembhai solution and used by both the builder and the agent image;
the builder must not fork it. Readiness consumes the final verdict and check results, and the run
report presents both claimed and final verdicts. Changing verifier checks is explicitly out of
scope.

---

## EPIC: Readiness checks & re-verification  (BSB-30)
**Feature area:** FA-10 · **Release:** MVP · **Labels:** FA-10, MVP

### Description
A build may be called Ready only when a specific, auditable set of checks holds at its current
head SHA. This epic defines and aggregates those checks: manifest validity at the SHA, a passing
run, a passing static scan, and an LLM scan that is complete or explicitly recorded as unavailable.
It shows each of the four checks on the build page, refuses to package a skill when the verifier's
lint or self-test fails or when the catalog's required verifier range excludes the selected
verifier version, and supports cheap re-verification: grade an existing output branch again with
a changed `verify.yaml` without the agent or a model, and show which checks flipped. The value is
a defensible Ready gate and an inexpensive way to recheck a run after verification rules change.

### Functional scope
- Check the manifest validity of a build at a commit SHA.
- Mark a build Ready at a SHA only when the manifest check passes, a run passes, the static scan
  passes and the LLM scan is complete or recorded as unavailable.
- Show each of the four readiness checks on the build page.
- Refuse to package a skill when the verifier's lint check fails.
- Refuse to package a skill when the verifier's self-test fails.
- Refuse to package a skill when the catalog's required verifier range excludes the selected
  verifier version.
- Re-verify an existing output branch with a changed `verify.yaml` without the agent or a model.
- Show which checks flipped during a re-verification.
- Non-goals: changing builtin verifier checks, treating the LLM scan as a blocker, and submitting
  to the catalog (catalog-submission epic).

### Implementation guidance / dependency order
1. Define a readiness record keyed by build SHA with one result per check; readiness is derived,
   not a manually set flag.
2. Implement the manifest check at a SHA using the catalog's static manifest rules.
3. Consume the run verdict, static scan verdict and LLM scan state from their epics into the four
   check results.
4. Implement aggregation so Ready requires every check to pass at the same SHA, and make the
   build page render each check separately for diagnosis.
5. Add the packaging preflight for verifier lint, verifier self-test and catalog verifier-range
   compatibility; packaging must call this preflight before producing a bundle.
6. Implement re-verification against an existing output branch with a supplied changed
   `verify.yaml`, explicitly skipping agent execution and model calls, then diff check results
   against the prior verification and show flips.
7. Verify a re-verification consumes zero model tokens.

### Goal / Definition of Done
A build is Ready at a SHA only when the manifest check, a run, the static scan and the LLM scan
state all satisfy the rule at that same SHA, and the build page shows each check. Packaging is
refused when verifier lint fails, verifier self-test fails, or the catalog's required verifier
range excludes the selected version. An author can re-verify an existing output branch with a
changed `verify.yaml` without the agent or a model and see exactly which checks flipped.

### Covered requirements (traceability)
- FR-068 — The manifest validity of a build at a commit SHA is checked.
- FR-069 — Ready requires manifest, run, static scan and LLM scan conditions at the SHA.
- FR-070 — The build page shows each of the four readiness checks.
- FR-071 — Packaging is refused when the verifier lint check fails.
- FR-072 — Packaging is refused when the verifier self-test fails.
- FR-073 — Packaging is refused when the required verifier range excludes the selected version.
- FR-074 — An output branch is re-verified with a changed `verify.yaml`, without agent or model.
- FR-075 — A re-verification shows which checks flipped.

### Notes
Depends on the verification epic for verdicts and check results, the static and LLM scan epics for
security check state, the build head and invalidation rule from the editing epic, and the catalog's
manifest rules and verifier releases supplied externally. Catalog submission depends on Ready at
the current head. Re-verification must not invoke the agent or consume model tokens, which is also
a stated success metric. Readiness is always evaluated at one SHA; a head move invalidates it.

---

## EPIC: Run report & change evidence  (BSB-33)
**Feature area:** FA-13 · **Release:** MVP · **Labels:** FA-13, MVP

### Description
An author, reviewer or debugger needs one place that explains what a run did and why it was
judged the way it was. This epic builds the run report: the skill and skills commit that ran, the
input and output branches, the component versions, the agent's claimed verdict and the final
verdict, each check result, the diff from input branch to output branch, the Jira changes the run
made, the turn count, and a link to the trace when tracing is enabled. The value is that a run's
evidence is inspectable without reconstructing it from logs, and the catalog pull request can point
at a stable report.

### Functional scope
- Show the skill that ran and the skills commit SHA.
- Show the input branch and the output branch.
- Show the component versions used by the run.
- Show the verdict the agent claimed and the final verdict after verification.
- Show each check result.
- Show the diff from the input branch to the run branch.
- Record and show the Jira changes the run made.
- Show the run's turn count.
- Link to the run's trace when tracing is enabled.
- Present the report as the stable evidence target linked from catalog submission.
- Non-goals: token usage and cost detail, retention and purge (usage and retention epic); run
  history and comparison (Later history epic).

### Implementation guidance / dependency order
1. Define the run-report projection over the run, verification and scan records; do not duplicate
   their data as separately editable fields.
2. Capture the input-to-output diff from the recorded baseline and output branch after the run.
3. Capture the Jira changes the run made from the run's Jira-integration activity and persist them
   with the run.
4. Add verdict, check, component and turn-count sections from the execution and verification
   records.
5. Add the trace link only when tracing is enabled and the trace identifier exists.
6. Expose a stable report view that catalog submission can link to and that reviewers can read
   without the authoring interface.

### Goal / Definition of Done
Every run has a report that shows its skill and skills commit, both branches, component versions,
claimed and final verdicts, every check result, the branch diff, the Jira changes it made, its
turn count and, when tracing is enabled, a trace link. The report is the evidence target the
catalog pull request links to.

### Covered requirements (traceability)
- FR-094 — The run page shows the skill that ran.
- FR-095 — The run page shows the input branch.
- FR-096 — The run page shows the output branch.
- FR-097 — The run page shows the component versions used.
- FR-098 — The run page shows the verdict the agent claimed.
- FR-099 — The run page shows each check result.
- FR-100 — The run page shows the diff from input branch to run branch.
- FR-101 — The run page shows the Jira changes the run made.
- FR-102 — The run page shows the run's turn count.
- FR-103 — The run page links to the run's trace when tracing is enabled.
- FR-140 — The builder records the Jira changes a run makes.
- FR-157 — The run page shows the skills commit SHA.
- FR-158 — The run page shows the final verdict after verification.

### Notes
Depends on run start, packaging, execution, verification and the Jira integration. The trace store
is external; a missing trace link is expected when tracing is disabled. Token usage, cost and
retention live in the usage, trace and retention epic, while history and comparison are deferred.
Catalog submission links this report and the scan reports from the pull-request description.

---

## EPIC: Run usage, trace & data retention  (BSB-34)
**Feature area:** FA-13 · **Release:** MVP · **Labels:** FA-13, MVP

### Description
Running skills against real systems produces usage and cost data, trace data and stored artifacts
that must be accounted for and eventually removed. This epic records each run's token usage, cost
and turn count, ensures a run's trace identifies it as a test-environment run, and applies the
installation's retention policy to run transcripts, logs and results, with a purge operation on
request and a three-month default retention period. The value is cost visibility, safe trace
attribution, and a defensible data lifecycle that does not retain test data forever.

### Functional scope
- Record each run's cost.
- Record each run's token usage.
- Record each run's turn count.
- When tracing is enabled, identify every run's trace as a test-environment run.
- Retain run transcripts, logs and results only for a configured period.
- Purge run transcripts, logs and results on request.
- Default the retention period to three months.
- Surface usage and cost on the run record for the run report.
- Non-goals: changing the platform's trace format, retaining data indefinitely, and author-set
  per-run retention.

### Implementation guidance / dependency order
1. Capture token usage, cost and turn count from execution telemetry into the run record.
2. Apply the test-environment marker to every trace at creation, using the installation's
   environment identity rather than a per-run flag.
3. Define the retention setting as an installation-level configuration value with a three-month
   default, and store timestamps that allow expiry to be evaluated.
4. Implement the retention sweep over transcripts, logs and results, leaving audit-critical run
   metadata as specified by the retention policy.
5. Implement an explicit purge operation for a run's transcripts, logs and results, with
   authorization and an auditable result.
6. Expose usage and cost to the run report without duplicating the stored values.

### Goal / Definition of Done
Each run records its token usage, cost and turn count, and the run report can display them. When
tracing is enabled, each trace is identified as a test-environment run. Run transcripts, logs and
results expire under an installation-configured retention period whose default is three months,
and an authorized purge removes them on request. No credential value is captured by this telemetry.

### Covered requirements (traceability)
- FR-159 — The run page shows the run's token usage.
- FR-160 — The run page shows the run's cost.
- NFR-011 — When tracing is enabled, a run's trace identifies it as a test-environment run.
- NFR-013 — Run transcripts, logs and results are retained only for a configured period.
- NFR-014 — Run transcripts, logs and results can be purged on request.
- NFR-015 — Each run records its cost.
- NFR-016 — Each run records its token usage.
- NFR-017 — Each run records its turn count.
- NFR-018 — The default retention period is three months.

### Notes
Depends on execution telemetry and the external trace store, and on the installation settings
managed by the operator. The three-month default and the installation-level retention setting are
review-confirmed assumptions recorded by the PRD, not ADR-given values. Retention applies to
transcripts, logs and results; the policy must not retain credential values and must not interfere
with the evidence the run report requires while that evidence is within its retention window.

---

## EPIC: Jira fixture seeding  (BSB-28)
**Feature area:** FA-9 · **Release:** Later · **Labels:** FA-9, Later

### Description
Later, authors will want skills that operate on Jira to run against realistic tracker data instead
of an empty project. This epic seeds Jira issues for a run from a fixture file into the project's
configured Jira project, marks every created issue with the run's ID, replaces fixture aliases
with the created issue keys, records the Jira state after the run for fixture assertions, and
cleans up when the run ends. Cleanup and a nightly sweep delete only issues carrying a run marker,
so a human-created issue is never deleted. The value is faithful, isolated Jira test data without
the risk of touching real tracker content.

### Functional scope
- Seed Jira issues for a run from a fixture file into the project's configured Jira project,
  marked with the run's ID.
- Replace fixture aliases with the created issue keys.
- Record the Jira state after the run for fixture assertions.
- Clean up seeded issues when the run ends, deleting only issues marked with that run's ID.
- Run a nightly sweep that removes seeded issues carrying a run marker.
- Non-goals: deleting or modifying human-created issues, seeding from the platform's own data,
  and any tracker write outside the configured test Jira project.

### Implementation guidance / dependency order
1. Define the fixture format and alias vocabulary, and validate it before creating any issue.
2. Implement issue creation in the project's configured Jira project with an unambiguous
   machine-readable run marker on every seeded issue.
3. Build the alias-to-key map and substitute aliases into the run's fixture-facing inputs.
4. Capture post-run Jira state for fixture assertions.
5. Implement end-of-run cleanup that selects only issues carrying the current run marker.
6. Implement the nightly sweep over marked issues, independent of any live run.
7. Add tests asserting that unmarked human issues are never selectable for deletion.

### Goal / Definition of Done
A fixture file seeds the configured test Jira project, every seeded issue carries the run's
marker, aliases resolve to real issue keys, post-run Jira state is recorded, and end-of-run cleanup
plus a nightly sweep remove only issues marked with a run ID. No human-created issue is ever
deleted.

### Covered requirements (traceability)
- FR-058 — Jira issues are seeded from a fixture file, marked with the run ID.
- FR-059 — Fixture aliases are replaced with created issue keys.
- FR-060 — Jira state after the run is recorded for fixture assertions.
- FR-061 — Seeded issues are cleaned up at run end, only those marked with that run's ID.
- FR-062 — A nightly sweep removes seeded issues carrying a run marker.

### Notes
Deferred to a later release and not a prerequisite for the first release. Depends on the Jira
integration and the test project's configured Jira project, and on the run identity that owns the
marker. The marker is the safety boundary: the builder has no authority over unmarked issues.
Fixture seeding must use test-purpose Jira credentials and must not write to the platform's own
tracker data.

---

## EPIC: Skill history & run comparison  (BSB-35)
**Feature area:** FA-14 · **Release:** Later · **Labels:** FA-14, Later

### Description
Later, authors need to see how a skill has behaved over time and what changed between two runs.
This epic lists every run of a skill with its commit SHA, input branch, verdict and checks, and
provides a side-by-side comparison of two runs that highlights checks which flipped. The value is
fast diagnosis of regressions and regains across iterations without reading run reports one by
one.

### Functional scope
- List every run of a skill with its commit SHA, input branch, verdict and checks.
- Show two runs side by side in a comparison view.
- Highlight checks that flipped between the two compared runs.
- Non-goals: scheduling or re-running from the history view, changing a past run's evidence, and
  comparing runs across different skills.

### Implementation guidance / dependency order
1. Build the history query over completed runs keyed by skill identity, ordered by time.
2. Expose the per-run summary fields (commit SHA, input branch, verdict, checks) from the run
   record rather than re-deriving them in the UI.
3. Implement the two-run comparison model over the same check identities.
4. Diff check results and mark flips, including pass-to-fail and fail-to-pass.
5. Add the history and compare views after the run report is stable.

### Goal / Definition of Done
An author can see every run of a skill with its commit SHA, input branch, verdict and checks, and
can compare two runs side by side with flipped checks clearly highlighted.

### Covered requirements (traceability)
- FR-104 — Skill history lists every run with commit SHA, input branch, verdict and checks.
- FR-105 — The compare view shows two runs side by side.
- FR-106 — The compare view highlights checks that flipped between the two runs.

### Notes
Deferred to a later release. Depends on the run report and the persisted verification check
results. Comparison is read-only over recorded evidence; it never re-executes or re-verifies a
run. History is scoped to one skill.

---

## EPIC: Catalog submission  (BSB-36)
**Feature area:** FA-15 · **Release:** MVP · **Labels:** FA-15, MVP

### Description
The end of the authoring loop is a reviewed catalog pull request, not a direct change to the
catalog. This epic enables submission only when the build is Ready at its current head SHA, opens
a pull request from the build branch to the catalog's `main` branch using the author's own
source-control identity, and writes a description that lists the readiness checks and links the
run and scan reports. It records the pull-request URL and state on the build and moves the build
through open, submitted, merged or abandoned. A save on a submitted build clears its readiness,
and the builder never writes directly to the platform catalog, platform projects or project
skills. The value is a reviewable, evidence-backed change that follows the catalog's existing
review flow.

### Functional scope
- Enable Submit to catalog only when the build is Ready at its head SHA.
- Open a catalog pull request from the build branch to the catalog's `main` branch using the
  author's own source-control identity.
- List the readiness checks at the head SHA in the pull-request description.
- Link the run report and the scan reports from the pull-request description.
- Record the pull-request URL and state on the build.
- Move the build state through open, submitted, merged or abandoned.
- Clear a submitted build's readiness status when a save creates a new commit.
- Never write directly to the platform catalog, platform projects or project skills.
- Non-goals: merging the pull request, administering the catalog review workflow, and bypassing
  the Ready gate.

### Implementation guidance / dependency order
1. Re-check readiness at the current head SHA at submission time; do not trust a cached Ready
   flag.
2. Resolve the author's own source-control identity from the project's source-control integration
   and open the pull request from the build branch to the catalog `main` branch.
3. Assemble the description from the four readiness checks, the run-report link and the static and
   LLM scan report links.
4. Record the returned pull-request URL and state on the build.
5. Model the build lifecycle transitions and expose them on the build page.
6. Reuse the save-to-commit path to clear readiness on a submitted build when a new commit moves
   the head.
7. Add guards and tests proving there is no direct write path to the catalog, platform projects or
   project skills.

### Goal / Definition of Done
Submit to catalog is available only for a Ready build at its current head. Submitting opens a
catalog pull request from the build branch to the catalog `main` using the author's identity, with
the readiness checks and run and scan report links in the description. The build records the
pull-request URL and state and moves through open, submitted, merged or abandoned. A save on a
submitted build clears readiness, and no code path writes directly to the catalog or platform
data.

### Covered requirements (traceability)
- FR-107 — Submit to catalog is enabled only when the build is Ready at the head SHA.
- FR-108 — Submitting opens a catalog pull request using the author's source-control identity.
- FR-109 — The pull-request description lists the readiness checks at the head SHA.
- FR-110 — The pull-request description links to the run report.
- FR-111 — The pull-request description links to the scan reports.
- FR-112 — The pull-request URL is recorded on the build.
- FR-113 — The build state moves through open, submitted, merged or abandoned.
- FR-114 — A save on a submitted build clears its readiness status.
- FR-115 — The builder never writes directly to the platform catalog, platform projects or
  project skills.
- FR-161 — The pull-request state is recorded on the build.

### Notes
Depends on the readiness gate, the run and scan reports, the source-control integration and the
build head/invalidation rule. External prerequisites: the catalog repository, its `main` branch
and its review flow, and the author's source-control identity. The only outward write is the
catalog pull request; the catalog skill changes only when a human merges it. Direct writes to the
platform catalog, platform projects or project skills are forbidden.

---

## EPIC: Command line & saved suites  (BSB-37)
**Feature area:** FA-16 · **Release:** mixed · **Labels:** FA-16, mixed

### Description
Some authors work from a terminal, and repeated checks are better expressed as a suite than as
clicks. The MVP of this epic exposes the same run and scan services on the command line: start a
test run, run a static-only scan, and run a full security scan, all without the web interface. The
Later slice adds saved suites: an author saves a named suite whose entries name a skill, input
branch, context and expectations, runs the suite, schedules it nightly, and the builder records
each scheduled run's result. The value is automation parity with the interface in the MVP and
repeatable regression suites later, without creating a second execution path.

### Functional scope
- MVP: start a test run from the command line without the web interface.
- MVP: run a static-only security scan from the command line without a test run.
- MVP: run a full security scan from the command line without a test run.
- Later: save a named suite of runs.
- Later: give each suite entry a skill, input branch, context and expectations.
- Later: run a saved suite.
- Later: schedule a saved suite for nightly execution.
- Later: record each scheduled run's result.
- Non-goals: a separate command-line implementation of run or scan logic; suite editing outside
  the saved-suite feature; workflow orchestration in the builder.

### Implementation guidance / dependency order
1. Put the command-line surface on the same run-start and scan services as the interface; the CLI
   is a client, not a second engine.
2. Reuse project membership, integration resolution and the static/LLM scan rules for CLI
   invocations.
3. Add non-interactive authentication or token handling consistent with the authoring gate.
4. Later: define the suite and suite-entry model over existing run inputs.
5. Later: implement suite execution by creating one run per entry through the same run service.
6. Later: add nightly scheduling and persist each scheduled run's result, including skips and
   failures.

### Goal / Definition of Done
MVP: an author can start a test run, a static-only scan and a full security scan from the command
line without the web interface, with the same authorization, scanning and evidence behaviour as
the interface. Later: an author can save a named suite whose entries name a skill, input branch,
context and expectations, run it, schedule it nightly and see each scheduled run's result.

### Covered requirements (traceability)
- FR-116 — The command line starts a test run without the web interface.
- FR-117 — The command line runs a static-only security scan without a test run.
- FR-118 — The command line runs a full security scan without a test run.
- FR-119 — An author saves a named suite of runs.
- FR-120 — A suite entry names a skill, input branch, context and expectations.
- FR-121 — An author runs a saved suite.
- FR-122 — A saved suite can be scheduled for nightly execution.
- FR-123 — The builder records each scheduled run's result.

### MVP subset (if release = mixed)
- MVP: FR-116, FR-117, FR-118 — command-line run and scan parity.
- Later: FR-119, FR-120, FR-121, FR-122, FR-123 — saved suites, suite execution and nightly
  scheduling.

### Notes
Depends on the run-start, packaging, execution, static scan and LLM scan services; it must not
reimplement them. The Later suite slice also depends on the run record and the source-control
branch vocabulary. Nightly scheduling is a builder feature only for saved suites; general
workflow orchestration with gates and routing remains out of scope. Command-line operations obey
the same project membership and credential rules as the interface.

---

## EPIC: Accessibility conformance  (BSB-38)
**Feature area:** FA-17 · **Release:** MVP · **Labels:** FA-17, MVP

### Description
Every authoring surface must be usable with a keyboard and assistive technology, not only with a
mouse and sight. This cross-cutting epic applies to all web surfaces built by the other epics: it
requires every interactive control to be keyboard-operable with a visible focus indicator, every
custom status component to expose a programmatic name, role and state, every form field to expose
its label, instructions and error message, and run progress and readiness changes to be announced.
Status must never be conveyed by colour alone, text and status colours must meet WCAG 2.1 AA
contrast in normal and hover/focus states, builder surfaces must reflow to a 320 CSS-pixel viewport
without two-dimensional scrolling, and automated accessibility checks must run in continuous
verification. The value is that every author can use the product, and accessibility regressions are
caught by the pipeline rather than by users.

### Functional scope
- Make every interactive control operable with a keyboard.
- Show a visible focus indicator on every interactive control.
- Expose a programmatic name, role and state on every custom status component.
- Expose each form field's label, instructions and error message to assistive technology.
- Announce run progress and readiness changes to assistive technology.
- Never convey readiness or verdict status by colour alone.
- Meet WCAG 2.1 AA contrast for text and status colours in normal and hover or focus states.
- Reflow every builder web surface to a 320 CSS-pixel viewport without two-dimensional scrolling.
- Run automated accessibility checks in continuous verification.
- Non-goals: accessibility of surfaces outside the builder, certification claims beyond
  WCAG 2.1 AA for the audited builder surfaces, and native mobile clients.

### Implementation guidance / dependency order
1. Establish accessible primitives for controls, form fields and status components before feature
   pages proliferate, so later epics build on conforming components.
2. Add keyboard interaction and visible focus to each primitive and verify tab order in each flow.
3. Add programmatic names, roles and states for custom status indicators.
4. Wire form labels, instructions and error messages to their fields.
5. Add live-region announcements for run progress and readiness changes.
6. Replace colour-only status encoding with text or shape cues and enforce contrast tokens in the
   design system.
7. Add the 320 CSS-pixel reflow checks to the UI test suite.
8. Add automated accessibility checks to continuous verification and fail the pipeline on critical
   findings.

### Goal / Definition of Done
Every builder web surface is operable by keyboard with visible focus, custom statuses expose name,
role and state, forms expose labels, instructions and errors, and progress and readiness changes
are announced. Status is never colour-only, colours meet WCAG 2.1 AA contrast in normal and
hover/focus states, every surface reflows to 320 CSS pixels without two-dimensional scrolling, and
automated accessibility checks run in continuous verification with zero critical findings on the
audited surfaces.

### Covered requirements (traceability)
- FR-130 — Every interactive control is operable with a keyboard.
- FR-131 — Every interactive control shows a visible focus indicator.
- FR-132 — Every custom status component exposes a programmatic name, role and state.
- FR-133 — Every form field exposes its label, instructions and error message.
- FR-134 — Run progress and readiness changes are announced to assistive technology.
- FR-135 — Readiness and verdict status are never conveyed by colour alone.
- FR-136 — Text and status colours meet WCAG 2.1 AA contrast in normal and hover/focus states.
- FR-137 — Automated accessibility checks run in continuous verification.
- NFR-012 — Every builder web surface reflows to 320 CSS pixels without two-dimensional scrolling.

### Notes
This is a cross-cutting epic: it constrains every web surface built by the access, build, project,
integration, run, scan, report and submission epics, so its primitives should be established early
even though the conformance pass closes late. The accessibility scope, the WCAG 2.1 AA target and
the 320 CSS-pixel reflow value are added assumptions recorded by the PRD, not ADR-given
requirements. Automated checks are part of continuous verification, not a one-time audit.

---

*Decomposed by `sdlc-plan-epics-create`. Next steps: run `sdlc-tracker-sync` to publish the epics
and replace the draft keys, then run `sdlc-plan-stories-write` for each epic. Coverage check: all
165 functional requirements and 19 non-functional requirements from `docs/product/PRD.md` are
mapped to exactly one epic across this file and `epic-map.json`.*
