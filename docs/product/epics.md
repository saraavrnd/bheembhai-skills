```yaml bheembhai:foreach
epics:
  - id: FA-1-PENDING
    epic_key: FA-1-PENDING
    summary: "Access, identity & the authoring gate"
    feature_area: FA-1
    release: MVP
  - id: FA-2A-PENDING
    epic_key: FA-2A-PENDING
    summary: "Skill build creation & scaffolding"
    feature_area: FA-2
    release: MVP
  - id: FA-2B-PENDING
    epic_key: FA-2B-PENDING
    summary: "Skill cloning & edit builds"
    feature_area: FA-2
    release: MVP
  - id: FA-3-PENDING
    epic_key: FA-3-PENDING
    summary: "Skill editing, build state & readiness tracking"
    feature_area: FA-3
    release: MVP
  - id: FA-4-PENDING
    epic_key: FA-4-PENDING
    summary: "Test projects & membership"
    feature_area: FA-4
    release: MVP
  - id: FA-5-PENDING
    epic_key: FA-5-PENDING
    summary: "Integrations, credentials & MCP definitions"
    feature_area: FA-5
    release: MVP
  - id: FA-6A-PENDING
    epic_key: FA-6A-PENDING
    summary: "Run start & input selection"
    feature_area: FA-6
    release: MVP
  - id: FA-6B-PENDING
    epic_key: FA-6B-PENDING
    summary: "Skill packaging & run branch preparation"
    feature_area: FA-6
    release: MVP
  - id: FA-7-PENDING
    epic_key: FA-7-PENDING
    summary: "Run execution & outcome capture"
    feature_area: FA-7
    release: MVP
  - id: FA-8-PENDING
    epic_key: FA-8-PENDING
    summary: "Run guardrails, deadlines & re-runs"
    feature_area: FA-8
    release: MVP
  - id: FA-9-PENDING
    epic_key: FA-9-PENDING
    summary: "Jira fixture seeding"
    feature_area: FA-9
    release: Later
  - id: FA-10A-PENDING
    epic_key: FA-10A-PENDING
    summary: "Run verification & verdicts"
    feature_area: FA-10
    release: MVP
  - id: FA-10B-PENDING
    epic_key: FA-10B-PENDING
    summary: "Readiness checks & re-verification"
    feature_area: FA-10
    release: MVP
  - id: FA-11-PENDING
    epic_key: FA-11-PENDING
    summary: "Static security scanning"
    feature_area: FA-11
    release: MVP
  - id: FA-12-PENDING
    epic_key: FA-12-PENDING
    summary: "LLM security scanning"
    feature_area: FA-12
    release: MVP
  - id: FA-13A-PENDING
    epic_key: FA-13A-PENDING
    summary: "Run report & change evidence"
    feature_area: FA-13
    release: MVP
  - id: FA-13B-PENDING
    epic_key: FA-13B-PENDING
    summary: "Run usage, trace & data retention"
    feature_area: FA-13
    release: MVP
  - id: FA-14-PENDING
    epic_key: FA-14-PENDING
    summary: "Skill history & run comparison"
    feature_area: FA-14
    release: Later
  - id: FA-15-PENDING
    epic_key: FA-15-PENDING
    summary: "Catalog submission"
    feature_area: FA-15
    release: MVP
  - id: FA-16-PENDING
    epic_key: FA-16-PENDING
    summary: "Command line & saved suites"
    feature_area: FA-16
    release: mixed
  - id: FA-17-PENDING
    epic_key: FA-17-PENDING
    summary: "Accessibility conformance"
    feature_area: FA-17
    release: MVP
```

# Epics — decomposed from the SkillBuilder PRD

Project: **BSB** (`bheembhai-skill-builder`) · Source: `docs/product/PRD.md` · 21 epics ·
every FR and NFR mapped exactly once.

The epics below follow the PRD's feature areas. Four feature areas were split because they
exceeded a few sprints of work or held two clearly separable themes: FA-2 (create/scaffold vs
clone/edit), FA-6 (run start vs packaging), FA-10 (verification vs readiness) and FA-13 (run
report vs usage/retention). Cross-cutting NFRs are mapped to the epic that owns the outcome they
constrain, except accessibility, which has its own epic (FA-17).

---

## EPIC: Access, identity & the authoring gate  (FA-1-PENDING)

**Feature area:** FA-1 · **Release:** MVP · **Labels:** FA-1, MVP

### Description

This epic builds the builder's trust boundary. Only signed-in people who are current members of
the externally managed `skill-builders` group may reach any authoring surface, and every later
action — creating builds, owning test projects, starting runs, submitting to the catalog — must be
attributable to a local user record. The platform administrator manages group membership outside
this product; the builder only consumes the membership claim. The value is that a shared internal
tool is never opened to untrusted users and that every artifact has a stable local owner.

### Functional scope

- Reject an unauthenticated visitor before any authoring page or builder data is returned (FR-001,
  NFR-002).
- Sign in with the platform identity provider's existing credentials (FR-002).
- Require current `skill-builders` membership for every authoring request, re-checking the claim
  per request rather than only at sign-in (FR-003, FR-004, NFR-003).
- Reject a sign-in attempt by a user who is not a current group member (FR-138).
- Create exactly one local user record per identity-provider subject on first successful sign-in
  (FR-005) and reuse that record on later sign-ins by the same subject (FR-142).
- Deny authoring access to a removed group member no later than one hour after removal (FR-141),
  which bounds how long a cached membership decision may live.
- Non-goals: no user, group or role administration; no invitation or self-service account
  management; group membership is supplied externally.

### Implementation guidance / dependency order

- Define the session model and authentication middleware first; every other story in this epic
  hangs off it.
- Add a membership-claim resolver with a cache lifetime no longer than one hour, then apply the
  combined authentication and membership gate to every authoring route.
- Add the local-user upsert keyed by identity-provider subject, and migrate any existing actions to
  reference that local user.
- Finish with tests for sign-in rejection, per-request re-checks, first-versus-later sign-in, and
  the one-hour removal bound.

### Goal / Definition of Done

An unauthenticated visitor and a signed-in non-member both receive no authoring page or builder
data on any route. A first successful sign-in creates exactly one local user record, a later
sign-in reuses it, and removing a user from the group revokes authoring access within one hour.

### Covered requirements (traceability)

- FR-001 — An unauthenticated visitor cannot open any authoring page.
- FR-002 — A user signs in with the platform identity-provider credentials.
- FR-003 — Authoring features require current skill-builders group membership.
- FR-004 — Membership is re-checked on every request, not only at sign-in.
- FR-005 — One local user record per identity-provider subject on first sign-in.
- FR-138 — A non-member sign-in attempt is rejected.
- FR-141 — Removed members lose authoring access within one hour.
- FR-142 — A later sign-in reuses the existing local user record.
- NFR-002 — Unauthenticated requests are rejected before any builder data is returned.
- NFR-003 — Requests from signed-in non-members are rejected.

### Notes

- Depends on the external platform identity provider and the externally managed `skill-builders`
  group. Every other epic depends on this one for its actor identity and request gate.
- The one-hour removal bound is a cache-lifetime constraint, not a periodic job: a cached claim
  older than one hour must not authorize a request.

---

## EPIC: Skill build creation & scaffolding  (FA-2A-PENDING)

**Feature area:** FA-2 · **Release:** MVP · **Labels:** FA-2, MVP

### Description

This epic lets a skill author go from a name and a one-line description to a valid, catalog-shaped
skill skeleton on its own build branch. The scaffold must pass the catalog's static manifest checks
without edits, so an author starts from a working baseline instead of repairing generated files.
Name validation protects the catalog and keeps concurrent builds from colliding. The primary actor
is the skill author; the value is a reliable first step for every new skill.

### Functional scope

- Create a build from a skill name and a one-line description (FR-006).
- Cut the build branch from the current head of the catalog's `main` branch (FR-007).
- Scaffold the skill's own folder under the catalog's skills directory on the build branch (FR-008),
  including `SKILL.md` with the skill's frontmatter (FR-009), a `verify.yaml` stub (FR-143), and the
  standard references, templates and examples folders (FR-144).
- Guarantee that a newly scaffolded skill passes the catalog's static manifest checks with no edit
  (FR-010).
- Reject a create build when the name already exists on `main` (FR-015), when another open build
  already uses the name (FR-016), or when the name does not follow the `sdlc` prefix, area segment
  and action segment pattern (FR-017).
- Edge cases: the checked-out `main` head moves between validation and branch creation; scaffold
  generation must not depend on the author's local tooling.
- Non-goals: no cloning or editing of existing skills (covered by FA-2B); no versioning inside the
  builder.

### Implementation guidance / dependency order

- Start with the build record and the skill-name parser/validator, because every rejection rule
  depends on them.
- Add branch creation from the current `main` head, then the scaffold writer that emits
  `SKILL.md`, the `verify.yaml` stub and the standard folders in one commit.
- Wire the catalog manifest checks into the create path so a scaffold is validated before the build
  is declared usable, and add the name-uniqueness queries against `main` and open builds.
- Cover the name pattern, duplicate-on-main, duplicate-open-build and unedited-manifest-pass cases
  with tests.

### Goal / Definition of Done

An author can create a build from a name and description, receives a branch cut from the current
`main` head containing a standards-compliant scaffold, and that scaffold passes the catalog's
static manifest checks without edits. All three invalid-name cases are rejected with a clear
message.

### Covered requirements (traceability)

- FR-006 — Create a build from a skill name and one-line description.
- FR-007 — Create the build branch from the current head of main.
- FR-008 — Scaffold the skill folder under the catalog skills directory.
- FR-009 — The scaffold contains SKILL.md with frontmatter.
- FR-010 — A scaffold passes the catalog manifest checks without edits.
- FR-015 — Reject a name that already exists on main.
- FR-016 — Reject a name used by another open build.
- FR-017 — Reject a name outside the sdlc prefix/area/action pattern.
- FR-143 — The scaffold contains a verify.yaml stub.
- FR-144 — The scaffold contains the standard references, templates and examples folders.

### Notes

- Depends on FA-1 for the acting user and on the external catalog repository, its skills-directory
  layout and its manifest-check tooling.
- FA-2B, FA-3, FA-10B and FA-15 consume the build and branch created here.

---

## EPIC: Skill cloning & edit builds  (FA-2B-PENDING)

**Feature area:** FA-2 · **Release:** MVP · **Labels:** FA-2, MVP

### Description

This epic covers the two ways an author reuses existing work rather than starting from scratch:
cloning a catalog skill under a new name, and opening a catalog skill in an edit build. Both must
preserve the catalog as the source of truth — cloning must not touch the source skill, and an edit
build must modify the existing skill folder instead of creating a parallel one. The value is that
authors can adapt proven skills and fix existing ones through the same build, run, scan, Ready and
submit path.

### Functional scope

- Clone an existing catalog skill under a new name (FR-011), copying the skill's whole folder to the
  new skill path (FR-012), rewriting the skill name in the copied frontmatter (FR-013), and leaving
  the source skill's files unchanged (FR-014).
- Open an existing catalog skill in an edit build on a branch cut from `main` (FR-124).
- Make an edit build change the existing skill folder rather than creating a second skill folder
  (FR-125).
- Reject an edit build for a skill name that does not exist on `main` (FR-126).
- Edge cases: the clone target name must pass the same name rules as a new build; an edit build
  must resolve the skill folder from `main` before branching so a renamed or deleted folder is
  caught early.
- Non-goals: no catalog write of any kind; the catalog changes only when the eventual pull request
  is merged.

### Implementation guidance / dependency order

- Reuse the build/branch and name-validation plumbing from FA-2A as the base.
- Build the clone writer first: copy the whole folder, rewrite only the copied frontmatter name,
  and assert the source tree is byte-identical afterwards.
- Then add edit-build resolution: find the existing skill folder on `main`, cut the branch, and
  target that same folder for all later saves.
- Finish with the missing-skill rejection and tests that a clone leaves the source untouched and an
  edit build never creates a second folder.

### Goal / Definition of Done

An author can clone a catalog skill under a new valid name and get an independent copy with the
frontmatter name rewritten, while the source skill is unchanged. An author can open an existing
catalog skill in an edit build whose saves change that skill's existing folder, and a missing skill
name is rejected.

### Covered requirements (traceability)

- FR-011 — Clone an existing catalog skill under a new name.
- FR-012 — Cloning copies the skill's whole folder.
- FR-013 — Cloning rewrites the skill name in the copied frontmatter.
- FR-014 — Cloning leaves the source skill's files unchanged.
- FR-124 — Open an existing catalog skill in an edit build from main.
- FR-125 — An edit build changes the existing skill folder, not a second folder.
- FR-126 — Reject an edit build for a name that does not exist on main.

### Notes

- Depends on FA-2A for build and branch creation and on the external catalog repository.
- FA-3 provides the file editing and save-to-commit behaviour that edit builds and clones then use.

---

## EPIC: Skill editing, build state & readiness tracking  (FA-3-PENDING)

**Feature area:** FA-3 · **Release:** MVP · **Labels:** FA-3, MVP

### Description

This epic gives authors the editing loop and the state that makes readiness meaningful. Authors
edit files in the build's skill folder and save them; every save becomes a commit on the build
branch, and the build records that commit as its head. Because readiness is tied to a specific
commit, any new commit must invalidate the previously ready commit so a stale approval can never be
mistaken for a current one. The actors are skill authors; the value is a trustworthy "what I am
looking at is what was verified" guarantee.

### Functional scope

- Edit the content of a file in a build's skill folder (FR-127) and save the edited file to the
  build branch (FR-162).
- Make each save a commit on the build branch (FR-018).
- Record the latest commit SHA as the build head (FR-019).
- Show the current head SHA on the build page (FR-020) and the readiness status for that head SHA
  (FR-021).
- Clear the previously recorded ready SHA whenever a new commit lands (FR-022).
- Edge cases: two saves racing must not leave the head older than the newest commit; a failed
  commit must leave head unchanged and surface the error.
- Non-goals: no separate version history of skill content inside the builder; the branch is the
  history.

### Implementation guidance / dependency order

- Define the build record fields for head SHA and ready SHA first, including the rule that they are
  independent values.
- Add the save-to-commit service on the build branch, then make every successful commit update head
  and clear ready in the same transaction.
- Build the file editor on top of the save service, and render head SHA plus readiness status on
  the build page.
- Test the invalidation path directly: commit, mark ready, commit again, assert ready is cleared and
  head points at the newest commit.

### Goal / Definition of Done

An author can edit a file in the build's skill folder and save it, and each save appears as a
commit on the build branch. The build page shows the current head SHA and its readiness status, and
any new commit clears the earlier ready SHA.

### Covered requirements (traceability)

- FR-018 — Each save creates a commit on the build branch.
- FR-019 — The latest commit SHA is recorded as the build head.
- FR-020 — The build page shows the current head SHA.
- FR-021 — The build page shows readiness for the head SHA.
- FR-022 — A new commit clears the previously recorded ready SHA.
- FR-127 — An author edits a file in the build's skill folder.
- FR-162 — An author saves an edited file to the build branch.

### Notes

- Depends on FA-2A/FA-2B for the build and its branch, and on the external source-control
  integration for committing.
- Readiness itself is computed by FA-10B; this epic stores, shows and invalidates it whenever the
  head moves.

---

## EPIC: Test projects & membership  (FA-4-PENDING)

**Feature area:** FA-4 · **Release:** MVP · **Labels:** FA-4, MVP

### Description

Test projects are the shared sandbox in which authors run skills against test credentials. This
epic establishes project ownership and membership: an author creates a project and becomes its
owner, the owner adds and removes members, and only the owner may change the project's
integrations. Project membership is the authorization unit for starting runs. The value is a small,
controlled blast radius for test data and a clear answer to "who may run here and who owns the
settings".

### Functional scope

- Create a test project as a signed-in author (FR-023), recording the creator as owner (FR-024).
- Let the owner add another skill-builder user as a project member (FR-025) and remove a member
  (FR-026).
- Use project membership to authorize starting a test run in that project (FR-027).
- Restrict changes to the project's integrations to the owner (FR-028).
- Edge cases: an owner cannot be removed from their own project without a transfer flow, which is
  out of scope; adding a user who is not a current skill-builder must fail through the FA-1 gate.
- Non-goals: no project ownership transfer, no platform-project management, and no user/group
  administration.

### Implementation guidance / dependency order

- Define the project and membership records first, with the owner recorded at creation.
- Add owner-only membership add/remove, then expose membership checks to the run-start path.
- Apply the same owner check to integration settings when FA-5 adds them.
- Finish with authorization tests for member start, non-member start and non-owner integration
  changes.

### Goal / Definition of Done

A signed-in author can create a test project and is recorded as its owner. The owner can add and
remove members, members can start a run in the project, non-members cannot, and only the owner can
change the project's integrations.

### Covered requirements (traceability)

- FR-023 — A signed-in author creates a test project.
- FR-024 — The project creator is recorded as the owner.
- FR-025 — The owner adds another skill-builder as a project member.
- FR-026 — The owner removes a project member.
- FR-027 — Project membership authorizes starting a run in that project.
- FR-028 — Only the project owner changes the project's integrations.

### Notes

- Depends on FA-1 for local users and the authoring gate; the external `skill-builders` group
  determines who can be added.
- FA-5, FA-6A, FA-11 and FA-12 all authorize their actions against project membership or ownership.

---

## EPIC: Integrations, credentials & MCP definitions  (FA-5-PENDING)

**Feature area:** FA-5 · **Release:** MVP · **Labels:** FA-5, MVP

### Description

A test project needs three kinds of external integration — Jira, source control and an AI model —
and none of them may put a credential value into the builder. This epic lets a project owner
configure each integration's non-secret settings, verify its credentials against the external
secret store, and record when verification last succeeded. It also stores the MCP server
definitions that the Jira and source-control integrations expose to a run. The value is a safe
configuration surface: runs use test-purpose credentials without the builder ever holding or
displaying a secret.

### Functional scope

- Configure a Jira integration with a site URL and either a project key or a template project
  (FR-029).
- Configure a source-control integration with a sandbox repository and a base branch (FR-030).
- Configure an AI model profile with a vendor, base URL and tier-to-model mapping (FR-031).
- Store only an opaque secret reference; never store a credential value in builder records (FR-032)
  and never display one in the interface (FR-036).
- Verify an integration's credentials (FR-033) and record when they were last verified (FR-034).
- Warn when a source-control integration targets a repository also used by a platform project
  (FR-035).
- Record the MCP server definition exposed by the Jira integration (FR-128) and by the
  source-control integration (FR-129); a definition is non-secret configuration.
- Constrain runs to test-purpose Jira, source-control and model credentials (NFR-006), and keep
  credential values out of builder logs and run results (NFR-004).
- Edge cases: a verification failure must not erase the stored reference or the last-successful
  timestamp; the overlap warning must not block configuration, only warn.
- Non-goals: the builder does not administer secrets, provision test projects in Jira, or manage
  platform repositories.

### Implementation guidance / dependency order

- Start with the integration schema and the secret-reference type, plus a secret-store adapter that
  accepts and returns only references.
- Add Jira configuration, then source control, then the model profile, each reusing the same
  reference pattern.
- Add credential verification and the last-verified record, then the repository-overlap warning,
  which depends on the external repository inventory.
- Finish with the Jira and source-control MCP definitions and redaction tests proving credentials
  never reach logs, results or the interface.

### Goal / Definition of Done

A project owner can configure Jira, source-control and model integrations using secret references
only, verify their credentials, and see when each was last verified. No credential value is stored,
displayed, logged or returned. Source-control repositories shared with a platform project raise a
warning, and the Jira and source-control MCP definitions are stored with the integration.

### Covered requirements (traceability)

- FR-029 — Jira integration with site URL and project key or template project.
- FR-030 — Source-control integration with sandbox repository and base branch.
- FR-031 — Model profile with vendor, base URL and tier-to-model mapping.
- FR-032 — The builder never stores a credential value.
- FR-033 — The owner verifies an integration's credentials.
- FR-034 — The builder records when credentials were last verified.
- FR-035 — Warn when a source-control repository is also used by a platform project.
- FR-036 — The builder never displays a credential value.
- FR-128 — Store the Jira integration's MCP server definition.
- FR-129 — Store the source-control integration's MCP server definition.
- NFR-004 — Credential values never appear in builder logs or run results.
- NFR-006 — Runs use only test-purpose Jira, source-control and model credentials.

### Notes

- Depends on FA-4 for project ownership and on the external secret store, model endpoints and
  platform repository inventory. Every run-facing epic consumes these integrations.

---

## EPIC: Run start & input selection  (FA-6A-PENDING)

**Feature area:** FA-6 · **Release:** MVP · **Labels:** FA-6, MVP

### Description

This epic is the point where an author turns a configured test project and a built skill into a
concrete run request. The author must be a member of the project, and must be able to choose the
skills branch, input branch, workflow and step context, model profile and model tier, and
optionally supply reviewer feedback or an upstream handoff. The value is that a run is explicit
about every input before anything executes, so results are reproducible and comparable.

### Functional scope

- Start a run in a test project the author is a member of (FR-037).
- Offer a choice of skills branch (FR-145) and input branch (FR-146).
- Offer a choice of workflow and step context (FR-147).
- Let the author optionally supply reviewer feedback or an upstream handoff (FR-148).
- Offer a choice of model profile (FR-149) and model tier (FR-150).
- Edge cases: an empty or non-existent branch, a model profile without a mapping for the chosen
  tier, and a non-member attempt must fail before a run is created.
- Non-goals: this epic does not package the skill or create the run branch; that is FA-6B.

### Implementation guidance / dependency order

- Define the run-request model (skill, inputs, context, feedback, model selection) and validate it
  in one place.
- Reuse FA-4 membership for authorization and FA-5 integrations to populate branch and model
  choices.
- Build the run-start surface and then the API that persists a validated run request for FA-6B.
- Test member versus non-member start, every choice being required where applicable, and the
  optional feedback path.

### Goal / Definition of Done

A project member can start a run and explicitly choose the skills branch, input branch, workflow
and step context, model profile and model tier, with optional reviewer feedback or upstream
handoff. A non-member or an invalid selection is refused before any run is created.

### Covered requirements (traceability)

- FR-037 — An author starts a run in a test project they belong to.
- FR-145 — Run start offers a choice of skills branch.
- FR-146 — Run start offers a choice of input branch.
- FR-147 — Run start offers a choice of workflow and step context.
- FR-148 — Run start accepts optional reviewer feedback or an upstream handoff.
- FR-149 — Run start offers a choice of model profile.
- FR-150 — Run start offers a choice of model tier.

### Notes

- Depends on FA-4 for membership, FA-5 for model profiles and settings, and FA-2/FA-3 for the
  builds whose branches are offered.
- FA-6B, FA-8 and FA-16 consume the validated run request produced here.

---

## EPIC: Skill packaging & run branch preparation  (FA-6B-PENDING)

**Feature area:** FA-6 · **Release:** MVP · **Labels:** FA-6, MVP

### Description

Before a skill executes, the builder must freeze exactly what will run. This epic resolves the
chosen skills branch to a commit, packages that commit into a content-addressed bundle, reuses an
identical bundle when the same commit is prepared again, and creates the run's output branch from
the input branch head while recording the baseline. The input branch is read-only throughout. The
value is reproducibility: a run always executes an immutable artifact, and the diff it produces is
measured from a known baseline.

### Functional scope

- Resolve the skills branch to a commit SHA at run start (FR-038).
- Package the skill at that commit into a content-addressed bundle (FR-039) and reuse an existing
  bundle when the same skills commit is packaged again (FR-040).
- Create the run branch — the run's output branch — from the input branch head (FR-041), and record
  the input head SHA as the run baseline (FR-042).
- Guarantee that a run never writes to its input branch (FR-043).
- Meet the performance target of 60 seconds for non-model preparation of a bundle up to 5 MB
  (NFR-001).
- Produce an identical bundle when the same skills commit is prepared twice (NFR-009).
- Edge cases: a skills branch that moves between selection and resolution must use the resolved
  SHA; a missing or unreadable input branch must fail before a run branch is created.
- Non-goals: this epic does not execute the skill or invoke the verifier.

### Implementation guidance / dependency order

- Start with SHA resolution and the bundle packer, keying the bundle by a content hash so reuse is
  a lookup rather than a rebuild.
- Add bundle reuse and its cache, then create the run branch from the input head and record the
  baseline in one step.
- Enforce the input branch as read-only at the source-control adapter boundary, not only in the UI.
- Finish with timing and reproducibility tests: two preparations of one commit yield identical
  bundles, and a 5 MB bundle prepares within the target.

### Goal / Definition of Done

Starting a run resolves the skills branch to a SHA, produces or reuses an immutable
content-addressed bundle, creates the run branch from the input head and records the baseline. The
input branch is never written to, the same commit always yields the same bundle, and preparation
meets the 60-second target for bundles up to 5 MB.

### Covered requirements (traceability)

- FR-038 — Resolve the skills branch to a commit SHA at run start.
- FR-039 — Package the skill at that commit into a content-addressed bundle.
- FR-040 — Reuse an existing bundle for the same skills commit.
- FR-041 — Create the run branch from the input branch head.
- FR-042 — Record the input head SHA as the run baseline.
- FR-043 — A run never writes to its input branch.
- NFR-001 — Non-model preparation completes within 60 seconds for a bundle up to 5 MB.
- NFR-009 — Preparing the same skills commit twice yields an identical bundle.

### Notes

- Depends on FA-6A for the validated run request, FA-5 for the source-control integration, and the
  external object-storage bucket for bundles.
- FA-7 executes the bundle; FA-10A receives its baseline SHA; FA-13A displays the branch and diff;
  FA-15 opens the pull request from the build branch.

---

## EPIC: Run execution & outcome capture  (FA-7-PENDING)

**Feature area:** FA-7 · **Release:** MVP · **Labels:** FA-7, MVP

### Description

This epic runs one packaged skill in the platform's own runtime and records what happened. An
author watches progress and logs while the run executes, and the builder classifies the outcome
with the platform engine's result rules rather than inventing its own. It also captures the exact
execution-component versions, verifier version, model profile and model tier so the result can be
reproduced and compared. The value is faithful execution: a builder run behaves like a platform
run and leaves enough provenance to explain the result.

### Functional scope

- Execute the skill in the same runtime as the platform (FR-044).
- Show run progress (FR-045) and logs (FR-046) while the run executes.
- Classify the run outcome using the platform engine's result rules (FR-047).
- Record the exact execution-component versions used (FR-048), including the verifier version
  (FR-151), and the model profile (FR-049) and model tier (FR-152) used.
- Edge cases: the runtime failing to start, a runtime that exits without a classifiable result, and
  log truncation must all be recorded rather than silently lost.
- Non-goals: this epic does not enforce caps or deadlines (FA-8), verify the output (FA-10A), or
  own the full run report (FA-13A/FA-13B).

### Implementation guidance / dependency order

- Start with the runtime adapter and its start/stream/exit contract, reusing the platform runner
  rather than a bespoke executor.
- Add progress and log streaming to the run page, then result classification using the platform
  engine's rules.
- Capture component and verifier versions plus model profile and tier at start, and persist them
  with the run.
- Finish with tests for successful, failing and unclassifiable exits and for complete provenance
  capture.

### Goal / Definition of Done

A packaged skill executes in the platform runtime, the author sees progress and logs while it runs,
and the outcome is classified by the platform engine's result rules. Each run records its exact
component versions, verifier version, model profile and model tier.

### Covered requirements (traceability)

- FR-044 — The builder executes the skill in the platform's runtime.
- FR-045 — The run page shows progress while the run executes.
- FR-046 — The run page shows logs while the run executes.
- FR-047 — The builder classifies the outcome using the platform engine's result rules.
- FR-048 — The builder records the exact execution-component versions.
- FR-049 — The builder records the model profile used by the run.
- FR-151 — The builder records the exact verifier version used.
- FR-152 — The builder records the model tier used by the run.

### Notes

- Depends on FA-6B for the bundle and run branch, FA-5 for the model profile, and the external
  platform runtime, agent image and trace store.
- FA-8 wraps execution with caps and the deadline; FA-10A verifies the output; FA-13A/FA-13B
  present and retain the run evidence.

---

## EPIC: Run guardrails, deadlines & re-runs  (FA-8-PENDING)

**Feature area:** FA-8 · **Release:** MVP · **Labels:** FA-8, MVP

### Description

This epic bounds what a run may consume and when it must stop. Authors set a turn cap and a spend
cap per run, the builder stops the run when either is reached, and it refuses to start a run whose
execution components are incompatible or whose static scan did not pass. It also supports the
iteration loop: re-running a prior run with the same inputs against the latest skills commit, and
chaining a prior run's output branch as the next run's input. Every run reaches a terminal state
within an installation-configured deadline, and a run that exceeds it is recorded as failed. The
value is safe, predictable and cheap iteration.

### Functional scope

- Let the author set a turn cap (FR-050) and stop the run when it is reached (FR-051).
- Let the author set a spend cap (FR-052) and stop the run when it is reached (FR-053).
- Refuse to start a run when its execution components are incompatible (FR-054) or when the static
  scan for the skill content did not pass (FR-055).
- Re-run a prior run with the same inputs and the latest commit of its skills branch (FR-056), and
  use a prior run's output branch as a later run's input branch (FR-057).
- Ensure every run reaches a terminal state within its configured deadline (NFR-007) and record a
  deadline breach as failed (NFR-008).
- Make the deadline configurable per installation through environment configuration without a code
  change (NFR-019).
- Edge cases: a cap reached exactly on the final step must still record a terminal state; a
  re-run whose skills branch has no new commit must still be valid; chained inputs must be
  read-only for the later run.
- Non-goals: no workflow orchestration, gates or routing; no per-run override of the installation
  deadline or retention settings.

### Implementation guidance / dependency order

- Define the run policy record (turn cap, spend cap, deadline reference) and enforce caps at the
  runtime step boundary.
- Add the preflight checks for incompatible components and a non-passing static scan before any
  runtime start.
- Add the deadline supervisor that force-terminates and records failure at the configured limit,
  driven by installation configuration.
- Build re-run and output-branch chaining on top of the normal run-start path, reusing FA-6A/FA-6B
  validation.
- Finish with tests for both caps, both refusal paths, deadline breach, re-run and chained input.

### Goal / Definition of Done

A run stops at its turn or spend cap, unsafe or incompatible runs are refused before start, and
every started run reaches a terminal state within the installation's configured deadline, with a
breach recorded as failed. An author can re-run with the same inputs against the latest skills
commit and can chain a prior output branch as the next input.

### Covered requirements (traceability)

- FR-050 — The author sets a turn cap for a run.
- FR-051 — A run stops when it reaches its turn cap.
- FR-052 — The author sets a spend cap for a run.
- FR-053 — A run stops when it reaches its spend cap.
- FR-054 — Refuse to start when execution components are incompatible.
- FR-055 — Refuse to start when the static scan did not pass.
- FR-056 — Re-run with the same inputs and the latest skills-branch commit.
- FR-057 — Use a prior output branch as a later run's input branch.
- NFR-007 — Every run reaches a terminal state within its configured deadline.
- NFR-008 — A run that exceeds its deadline is recorded as failed.
- NFR-019 — The run deadline is changeable per installation without a code change.

### Notes

- Depends on FA-7 for execution and FA-11 for the static-scan verdict, and on the installation's
  environment configuration for the deadline.
- The spend cap is enforced here from the runtime's live cost meter; FA-13B owns durable cost,
  token and turn recording for the finished run.

---

## EPIC: Jira fixture seeding  (FA-9-PENDING)

**Feature area:** FA-9 · **Release:** Later · **Labels:** FA-9, Later

### Description

This later epic gives runs realistic, disposable Jira data. From a fixture file, the builder seeds
issues into the project's configured Jira project, marks every seeded issue with the run ID,
replaces fixture aliases with the new issue keys, and records the Jira state after the run so
assertions can be made. Cleanup removes only issues carrying that run's marker, and a nightly sweep
removes anything left behind. The value is a safe fixture lifecycle: realistic tracker state
without ever removing a manually authored issue.

### Functional scope

- Seed Jira issues for a run from a fixture file into the project's configured Jira project, marked
  with the run's ID (FR-058).
- Replace fixture aliases with the new issue keys (FR-059).
- Record the Jira state after the run for fixture assertions (FR-060).
- Clean up seeded issues when the run ends, deleting only issues marked with that run's ID (FR-061).
- Run a nightly sweep that removes seeded issues carrying a run marker (FR-062).
- Edge cases: a partially seeded fixture must still clean up what it created; a fixture that names
  an issue that already exists must fail without deleting it; cleanup must be idempotent.
- Non-goals: no mutation of issues the run did not seed; no fixture authoring UI.

### Implementation guidance / dependency order

- Define the run marker and the fixture-to-issue mapping first; every later operation keys off the
  marker.
- Add seeding and alias replacement, then post-run state capture.
- Add end-of-run cleanup and make it idempotent, then the nightly sweep as a scheduled job.
- Finish with tests that cleanup and the sweep never touch an unmarked issue.

### Goal / Definition of Done

A run can seed marked Jira issues from a fixture, use the created keys in place of aliases, and
record post-run Jira state. End-of-run cleanup and the nightly sweep remove only issues marked with
the relevant run ID, and no unmarked issue is ever deleted.

### Covered requirements (traceability)

- FR-058 — Seed Jira issues from a fixture, marked with the run ID.
- FR-059 — Replace fixture aliases with the new issue keys.
- FR-060 — Record the Jira state after the run for fixture assertions.
- FR-061 — Clean up seeded issues on run end, only those marked with that run's ID.
- FR-062 — A nightly sweep removes seeded issues carrying a run marker.

### Notes

- Later release; not a prerequisite for the first release.
- Depends on FA-5 for the Jira integration and FA-7 for run lifecycle hooks, plus a scheduler for
  the nightly sweep. FA-13A displays the Jira changes a run makes; fixture seeding is an additional
  source of that data, not a requirement for it.

---

## EPIC: Run verification & verdicts  (FA-10A-PENDING)

**Feature area:** FA-10 · **Release:** MVP · **Labels:** FA-10, MVP

### Description

This epic grades what a run produced. After the agent exits, the builder runs the shared
verification layer on the run branch, passing the run's baseline SHA and the `verify.yaml` from the
skills commit. It records the verdict the agent claimed, the final verdict the shared layer
produced, and whether verification overturned the claim. Because the verifier is a shared
third-party package rather than builder-owned code, identical inputs and component versions must
produce an identical result. The value is an independent, platform-consistent judgement of the run.

### Functional scope

- Run the shared verification layer on the run branch after the agent exits (FR-063).
- Pass the verifier the run's baseline SHA (FR-064) and the `verify.yaml` from the skills commit
  (FR-153).
- Record the verdict the agent claimed (FR-065), the final verdict after verification (FR-066), and
  whether verification overturned the claim (FR-067).
- Make the recorded final verdict the one produced by the shared verification layer (FR-164).
- Guarantee that the same inputs and component versions produce the same verification result
  (NFR-010).
- Edge cases: the verifier cannot run, returns no verdict, or returns a verdict for the wrong
  baseline; each must be a recorded verification failure rather than a pass.
- Non-goals: this epic does not aggregate the four readiness checks or re-verify without an agent;
  those are FA-10B.

### Implementation guidance / dependency order

- Start with the verifier adapter around the shared verification layer, invoked outside the agent
  container so the agent cannot alter what grades it.
- Assemble its inputs from FA-6B's baseline and the skills commit's `verify.yaml`, then persist
  claimed and final verdicts plus the overturn flag.
- Constrain the verifier's version through the catalog's pinned requirements and record it with the
  result.
- Finish with determinism tests for identical inputs and for each failure mode.

### Goal / Definition of Done

After a run exits, the shared verification layer grades the run branch with the correct baseline
and `verify.yaml`. The builder records the claimed verdict, the final verdict and whether the claim
was overturned, and the final verdict is exactly the shared layer's verdict. Repeating the same
inputs and component versions produces the same result.

### Covered requirements (traceability)

- FR-063 — Run the shared verification layer on the run branch after the agent exits.
- FR-064 — The verifier receives the run's baseline SHA.
- FR-065 — Record the verdict the agent claimed.
- FR-066 — Record the final verdict after verification.
- FR-067 — Record whether verification overturned the claimed verdict.
- FR-153 — The verifier receives the verify.yaml from the skills commit.
- FR-164 — The final verdict is the one produced by the shared verification layer.
- NFR-010 — Same inputs and component versions produce the same verification result.

### Notes

- Depends on FA-7 for the finished run and FA-6B for the baseline, and on the shared verification
  layer from the Bheembhai solution, which is a third-party dependency for this product.
- FA-10B aggregates this verdict into readiness; FA-13A shows the final verdict on the run page;
  FA-14 compares verdicts across runs.

---

## EPIC: Readiness checks & re-verification  (FA-10B-PENDING)

**Feature area:** FA-10 · **Release:** MVP · **Labels:** FA-10, MVP

### Description

This epic converts a set of independent checks into one trustworthy Ready decision for a specific
commit. A build is Ready at a SHA only when its manifest is valid, a run passes, the static scan
passes, and the LLM scan is complete or recorded as unavailable. The build page shows all four
checks, and packaging is refused when the verifier's lint or self-test fails or when the selected
verifier version falls outside the catalog's required range. It also allows re-verification of an
existing output branch with a changed `verify.yaml`, without re-running the agent or a model, and
shows which checks flipped. The value is a fast, explainable release gate.

### Functional scope

- Check the manifest validity of a build at a commit SHA (FR-068).
- Mark a build Ready at a SHA only when the manifest check passes, a run passes, the static scan
  passes, and the LLM scan is complete or recorded as unavailable (FR-069).
- Show each of the four readiness checks on the build page (FR-070).
- Refuse to package a skill when the verifier's lint check fails (FR-071), when the verifier's
  self-test fails (FR-072), or when the catalog's required verifier range excludes the selected
  verifier version (FR-073).
- Re-verify an existing output branch with a changed `verify.yaml` without the agent or a model
  (FR-074), and show which checks flipped (FR-075).
- Edge cases: a check that has not run must not count as passing; a re-verification against a
  different commit must not update readiness for the build head.
- Non-goals: no change to the verifier's builtin checks; no model tokens for re-verification.

### Implementation guidance / dependency order

- Define the readiness aggregate keyed by build and SHA, with explicit "not run" and "unavailable"
  states so absence never reads as a pass.
- Add the manifest check, then feed in the run result from FA-10A, the static-scan result from
  FA-11 and the LLM-scan state from FA-12.
- Add the packaging preflight gates for lint, self-test and verifier-range compatibility.
- Render the four checks on the build page, then build the re-verify path and its flipped-check
  diff.
- Finish with tests for every combination, especially a passing set that becomes unstuck only when
  all four are satisfied.

### Goal / Definition of Done

A build at a SHA becomes Ready only when all four checks are satisfied, and the build page shows
each check's state. Packaging is refused for a failing lint check, a failing self-test or an
out-of-range verifier version. An author can re-verify an existing output branch with a changed
`verify.yaml` without an agent or model and see which checks changed.

### Covered requirements (traceability)

- FR-068 — Check a build's manifest validity at a commit SHA.
- FR-069 — Mark Ready only when manifest, run, static scan and LLM scan all permit it.
- FR-070 — The build page shows each of the four readiness checks.
- FR-071 — Refuse packaging when the verifier lint check fails.
- FR-072 — Refuse packaging when the verifier self-test fails.
- FR-073 — Refuse packaging when the required verifier range excludes the selected version.
- FR-074 — Re-verify an output branch with a changed verify.yaml without an agent or model.
- FR-075 — A re-verification shows which checks flipped.

### Notes

- Depends on FA-10A for run verification, FA-11 and FA-12 for scan outcomes, FA-3 for the build
  head and ready-SHA invalidation, and the catalog's required verifier range (external
  prerequisite).
- FA-15 enables catalog submission only when this epic reports Ready at the head SHA.

---

## EPIC: Static security scanning  (FA-11-PENDING)

**Feature area:** FA-11 · **Release:** MVP · **Labels:** FA-11, MVP

### Description

This epic puts a deterministic static security gate in front of every run. The builder scans the
exact skill content before a run starts, reuses a completed result when the content is unchanged,
and treats several outcomes as non-passing: a `DO_NOT_INSTALL` verdict, any critical finding,
incomplete coverage, and an accepted finding that would otherwise clear a block. Scans time out
after ten minutes and a timed-out scan is recorded as failed. The static scan report shows the
score, recommendation and each finding's severity, rule, file and line, and the builder's verdict
must match the platform's for the same content and scanner version. Authors can also start a
static-only scan from the skill page without a run. The scan container has no network access.

### Functional scope

- Run a static security scan on the exact skill content before every run (FR-076), reusing a
  completed result when the content is unchanged (FR-077).
- Treat a `DO_NOT_INSTALL` static verdict (FR-078), a critical finding (FR-079), incomplete scan
  coverage (FR-080), and an accepted finding (FR-081) as non-passing.
- Time a scan out after ten minutes (FR-087) and record a timed-out scan as failed (FR-088).
- Show the scan's score (FR-089), recommendation (FR-154), and each finding's severity, rule, file
  and line (FR-155).
- Match the platform's scan verdict for the same content and scanner version (FR-091).
- Let an author start a static-only scan from the skill page for a test project they belong to,
  without a run (FR-092).
- Run the scan with no network access (NFR-005).
- Edge cases: content changing mid-scan, a scanner that returns a malformed report, and cache
  reuse across different content hashes.
- Non-goals: the builder does not change builtin verifier checks and does not accept a human
  override of a static block.

### Implementation guidance / dependency order

- Start with the scanner-container adapter and its network isolation, keyed by a content hash so
  results can be reused safely.
- Implement the verdict rules in one place — `DO_NOT_INSTALL`, critical findings, incomplete
  coverage and accepted findings all compose into a single passing decision.
- Add the timeout and failure recording, then the report model and UI with score, recommendation
  and findings.
- Add the standalone static-only scan path for project members, and finish with parity tests
  against the platform for identical content and scanner versions.

### Goal / Definition of Done

Every run is preceded by a static scan of its exact content, and no run starts on a non-passing
result. Unchanged content reuses its completed result. A scan that exceeds ten minutes is recorded
as failed. The report shows score, recommendation and findings, the builder's verdict matches the
platform's, and project members can request a static-only scan without a run.

### Covered requirements (traceability)

- FR-076 — Run a static scan on the exact skill content before every run.
- FR-077 — Reuse a completed static scan result when the content is unchanged.
- FR-078 — A DO_NOT_INSTALL verdict is not passing.
- FR-079 — A critical static finding is not passing.
- FR-080 — Incomplete static scan coverage is not passing.
- FR-081 — An accepted finding cannot clear a static-scan block.
- FR-087 — A security scan times out after ten minutes.
- FR-088 — A timed-out scan is recorded as failed.
- FR-089 — The static scan report shows the scan score.
- FR-091 — The builder's scan verdict matches the platform's for the same content and version.
- FR-092 — An author starts a static-only scan from the skill page without a run.
- FR-154 — The static scan report shows the scan's recommendation.
- FR-155 — The static scan report lists each finding's severity, rule, file and line.
- NFR-005 — A static security scan has no network access.

### Notes

- Depends on FA-6B for the exact content and bundle, and on the pinned scanner image (external
  prerequisite).
- FA-8 refuses a run whose static scan did not pass; FA-10B consumes the static verdict for
  readiness; FA-12 triggers only after this scan passes.

---

## EPIC: LLM security scanning  (FA-12-PENDING)

**Feature area:** FA-12 · **Release:** MVP · **Labels:** FA-12, MVP

### Description

This epic adds an advisory, model-based security review alongside the deterministic static scan. It
runs only after the static scan passes for the current content, receives no credential other than
the model key, and can reach only the model endpoint. It never blocks a run: its findings are shown
to the author, and if it cannot run the builder records it as unavailable. A full security scan can
also be started from the skill page without a run, using the LLM-scan model profile configured on
the test project. The value is earlier, richer feedback without making run availability depend on a
model call.

### Functional scope

- Trigger the LLM scan only after the static scan passes for the current content (FR-082).
- Give the scan no credential other than the model key (FR-083) and let it reach only the model
  endpoint (FR-084).
- Never block a run on the LLM scan (FR-085), and show its findings to the author (FR-086).
- Show which model ran the scan (FR-090) and list each finding's severity, rule, file and line
  (FR-156).
- Let an author start a full security scan from the skill page for a test project they belong to,
  without a run (FR-093).
- Record an LLM scan that cannot run as unavailable (FR-139).
- Use the LLM-scan model profile configured for the scan's test project (FR-163).
- Edge cases: a static failure means no LLM scan is triggered; an unavailable scan must still let
  readiness proceed; a project without a configured LLM model profile must surface unavailability
  rather than fall back silently.
- Non-goals: no blocking gate, no per-run model override, and no model other than the project's
  configured LLM-scan profile.

### Implementation guidance / dependency order

- Add the trigger hook after a passing static result, carrying the current content hash.
- Build the isolated LLM scan client with only the model key and an allow-list restricted to the
  model endpoint, then persist findings and the model identity.
- Record the unavailable state explicitly and make it a first-class readiness value for FA-10B.
- Add the standalone full-scan entry point for project members and bind it to the project's
  configured LLM-scan model profile.
- Finish with tests proving a run never blocks on this scan and that no non-model credential reaches
  it.

### Goal / Definition of Done

The LLM scan runs only after a passing static scan, uses only the model key, reaches only the model
endpoint, and never blocks or fails a run. Its findings, model identity and unavailable state are
recorded and shown, and project members can start a full security scan without a run using the
project's configured LLM-scan model profile.

### Covered requirements (traceability)

- FR-082 — Trigger the LLM scan only after the static scan passes for current content.
- FR-083 — The LLM scan receives no credential other than the model key.
- FR-084 — The LLM scan can reach only the model endpoint.
- FR-085 — The LLM scan never blocks a run.
- FR-086 — LLM scan findings are shown to the author.
- FR-090 — The LLM scan report shows which model ran the scan.
- FR-093 — An author starts a full security scan from the skill page without a run.
- FR-139 — An LLM scan that cannot run is recorded as unavailable.
- FR-156 — The LLM scan report lists each finding's severity, rule, file and line.
- FR-163 — A full security scan uses the test project's configured LLM-scan model profile.

### Notes

- Depends on FA-11 for the passing static scan and FA-5 for the model integration and project
  settings.
- FA-10B treats "complete or unavailable" as the readiness condition; this epic supplies that
  state.

---

## EPIC: Run report & change evidence  (FA-13A-PENDING)

**Feature area:** FA-13 · **Release:** MVP · **Labels:** FA-13, MVP

### Description

This epic gives a reviewer everything needed to judge what a single run did. The run page shows the
skill, the input and output branches, the component versions, the verdict the agent claimed, each
check result, the diff from input to run branch, the Jira changes the run made, the skills commit
SHA and the final verdict after verification. The builder also records those Jira changes so the
page is backed by durable evidence rather than a live query. The value is a self-contained review
artifact for one run at the exact commit that ran.

### Functional scope

- Show on the run page: the skill that ran (FR-094), the input branch (FR-095), the output branch
  (FR-096), the component versions used (FR-097), the verdict the agent claimed (FR-098), each check
  result (FR-099), the diff from the input branch to the run branch (FR-100), the Jira changes the
  run made (FR-101), the skills commit SHA (FR-157) and the final verdict after verification
  (FR-158).
- Record the Jira changes a run makes (FR-140) so they remain available as evidence.
- Edge cases: a run branch identical to its input shows an empty diff; a run that made no Jira
  change shows an explicit empty state rather than an error; a missing trace or scan report does not
  hide the rest of the report.
- Non-goals: this epic does not show usage, cost, trace links or retention (FA-13B), and does not
  compare runs (FA-14).

### Implementation guidance / dependency order

- Define the run-report read model that joins the run, its branches, component versions, checks and
  verdicts.
- Add branch/parent resolution and diff computation from the recorded baseline to the run branch,
  then render them with the check-result list.
- Capture Jira changes through the run's Jira integration into a durable record, then display them.
- Add the final-verdict and skills-commit fields, and finish with tests for empty diff, empty Jira
  change set and partial evidence.

### Goal / Definition of Done

A reviewer opening a run page sees the skill, input and output branches, component versions, the
claimed verdict, every check result, the input-to-run diff, the Jira changes the run made, the
skills commit SHA and the final verdict. The Jira changes are recorded durably and remain visible
even if the project's Jira state later changes.

### Covered requirements (traceability)

- FR-094 — The run page shows the skill that ran.
- FR-095 — The run page shows the input branch.
- FR-096 — The run page shows the output branch.
- FR-097 — The run page shows the component versions used.
- FR-098 — The run page shows the verdict the agent claimed.
- FR-099 — The run page shows each check result.
- FR-100 — The run page shows the diff from input branch to run branch.
- FR-101 — The run page shows the Jira changes the run made.
- FR-140 — The builder records the Jira changes a run makes.
- FR-157 — The run page shows the skills commit SHA.
- FR-158 — The run page shows the final verdict after verification.

### Notes

- Depends on FA-7 for the executed run, FA-6B for branches and baseline, FA-10A for the final
  verdict, and FA-5 for the Jira integration used to observe changes.
- FA-15 links to this report from the catalog pull request; FA-14 reuses its data for history and
  comparison. Jira fixture seeding (FA-9) is later and is not required for this evidence.

---

## EPIC: Run usage, trace & data retention  (FA-13B-PENDING)

**Feature area:** FA-13 · **Release:** MVP · **Labels:** FA-13, MVP

### Description

This epic covers the operational evidence attached to a run beyond its diff and checks: how much it
consumed, where its trace lives, and how long its data may be kept. Each run records its turn
count, token usage and cost, and the run page shows them. When tracing is enabled, the run page
links to the trace, and the trace identifies the run as a test-environment run. Run transcripts,
logs and results are retained for a configured period — three months by default — and can be purged
on request. The value is cost visibility, debuggability and a defined data lifecycle for test
transcripts that may contain sensitive content.

### Functional scope

- Show the run's turn count (FR-102), token usage (FR-159) and cost (FR-160) on the run page.
- Link to the run's trace when tracing is enabled (FR-103); when tracing is enabled, the trace
  identifies the run as a test-environment run (NFR-011).
- Record each run's cost (NFR-015), token usage (NFR-016) and turn count (NFR-017).
- Retain run transcripts, logs and results only for a configured period (NFR-013), defaulting to
  three months (NFR-018), and allow them to be purged on request (NFR-014).
- Edge cases: a run interrupted before usage is reported must still expose what was recorded; a
  purge must remove transcripts, logs and results together and be auditable; retention must be
  driven by installation configuration, not hard-coded.
- Non-goals: no per-run retention override; no user-facing analytics beyond the single run.

### Implementation guidance / dependency order

- Start with usage and cost capture from the runtime, persisting turn count, tokens and cost on the
  run record.
- Add trace linkage and the test-environment trace marker when tracing is enabled.
- Implement the retention setting, defaulting to three months, then the purge operation that
  removes transcripts, logs and results for a run.
- Render usage, cost and the trace link on the run page, and finish with tests for default
  retention, purge completeness and interrupted-run usage.

### Goal / Definition of Done

Every run records and shows its turn count, token usage and cost. When tracing is enabled the run
page links to a trace that identifies the run as a test-environment run. Run transcripts, logs and
results are retained for a configured period that defaults to three months and can be purged on
request.

### Covered requirements (traceability)

- FR-102 — The run page shows the run's turn count.
- FR-103 — The run page links to the run's trace when tracing is enabled.
- FR-159 — The run page shows the run's token usage.
- FR-160 — The run page shows the run's cost.
- NFR-011 — When tracing is enabled, the trace identifies the run as a test-environment run.
- NFR-013 — Run transcripts, logs and results are retained only for a configured period.
- NFR-014 — Run transcripts, logs and results can be purged on request.
- NFR-015 — Each run records its cost.
- NFR-016 — Each run records its token usage.
- NFR-017 — Each run records its turn count.
- NFR-018 — The default retention period is three months.

### Notes

- Depends on FA-7 for run telemetry, the external trace store and object storage, and the
  installation-level retention setting. The run deadline setting used by FA-8 is a separate
  installation setting.
- FA-8 enforces the spend cap from the runtime's live cost meter; this epic persists the final
  cost, token and turn figures and presents them on the run page.

---

## EPIC: Skill history & run comparison  (FA-14-PENDING)

**Feature area:** FA-14 · **Release:** Later · **Labels:** FA-14, Later

### Description

This later epic makes a skill's run history legible over time. It lists every run of a skill with
its commit SHA, input branch, verdict and checks, lets a reviewer compare two runs side by side, and
highlights the checks that flipped between them. The value is regression detection: an author can
see whether a change improved or degraded a skill without re-reading each run report.

### Functional scope

- List every run of a skill with its commit SHA, input branch, verdict and checks (FR-104).
- Show two runs side by side in a compare view (FR-105).
- Highlight checks that flipped between the two runs (FR-106).
- Edge cases: runs from different skills must not be comparable; a check that did not exist in the
  older run is shown as new rather than flipped.
- Non-goals: no saved suites or scheduled runs (FA-16); no comparison of arbitrary commits without
  runs.

### Implementation guidance / dependency order

- Build on the run-report read model from FA-13A, adding a skill-scoped history query first.
- Add a side-by-side comparison view over two selected runs.
- Compute flipped checks from the same check-result representation and highlight only genuine
  state changes.
- Finish with tests for same-skill enforcement, missing checks and flipped checks.

### Goal / Definition of Done

An author can open a skill's history and see every run with its commit SHA, input branch, verdict
and checks. They can compare two runs side by side and see exactly which checks flipped.

### Covered requirements (traceability)

- FR-104 — The skill history lists every run with commit SHA, input branch, verdict and checks.
- FR-105 — The compare view shows two runs side by side.
- FR-106 — The compare view highlights checks that flipped between the two runs.

### Notes

- Later release; not a prerequisite for the first release.
- Depends on FA-13A for run-report data and FA-10A for verdicts.

---

## EPIC: Catalog submission  (FA-15-PENDING)

**Feature area:** FA-15 · **Release:** MVP · **Labels:** FA-15, MVP

### Description

This epic closes the authoring loop: a Ready build becomes a reviewed catalog pull request. Submit
is enabled only when the build is Ready at its head SHA, and submitting opens a pull request from
the build branch to the catalog's main branch using the author's own source-control identity. The
pull-request description lists the readiness checks at the head SHA and links to the run report and
scan reports, so a catalog reviewer can judge the proposal without leaving the review. The builder
records the pull-request URL and state, tracks the build through open, submitted, merged or
abandoned, and clears readiness on any later save. The builder never writes directly to the catalog
or the platform.

### Functional scope

- Enable submit only when the build is Ready at its head SHA (FR-107).
- Open a catalog pull request from the build branch to the catalog's main branch using the author's
  own source-control identity (FR-108).
- List the readiness checks at the head SHA in the pull-request description (FR-109) and link to the
  run report (FR-110) and the scan reports (FR-111).
- Record the pull-request URL (FR-112) and state (FR-161) on the build.
- Move build state through open, submitted, merged or abandoned (FR-113), and clear readiness when a
  submitted build is saved again (FR-114).
- Never write directly to the platform catalog, platform projects or project skills (FR-115).
- Edge cases: a pull request closed without merge maps to abandoned; a save after submission clears
  readiness but does not close the pull request; a permission failure on the author's identity must
  surface without falling back to a service identity.
- Non-goals: no direct catalog import, no merge automation, and no platform-project writes.

### Implementation guidance / dependency order

- Define the build state machine and the readiness gate that blocks submit before the call is made.
- Add the pull-request client using the author's own source-control identity, then compose the
  description from readiness checks, the run report and the scan reports.
- Record the returned URL and state, and reconcile state changes from the source-control provider.
- Add submit-time readiness invalidation on a later save, and finish with tests for the state
  machine, identity-only creation and the no-direct-write rule.

### Goal / Definition of Done

Submit is available only for a build Ready at its head SHA. Submitting opens a catalog pull request
from the build branch under the author's own source-control identity, with readiness checks and
links to the run and scan reports in the description. The build records the pull-request URL and
state, moves through the four states, loses readiness on a later save, and never writes directly to
the catalog or platform.

### Covered requirements (traceability)

- FR-107 — Submit is enabled only when the build is Ready at the head SHA.
- FR-108 — Submitting opens a catalog pull request using the author's source-control identity.
- FR-109 — The pull-request description lists readiness checks at the head SHA.
- FR-110 — The pull-request description links to the run report.
- FR-111 — The pull-request description links to the scan reports.
- FR-112 — The builder records the pull-request URL on the build.
- FR-113 — The build state moves through open, submitted, merged or abandoned.
- FR-114 — A save on a submitted build clears its readiness status.
- FR-115 — The builder never writes directly to the catalog, platform projects or project skills.
- FR-161 — The builder records the pull-request state on the build.

### Notes

- Depends on FA-10B for Ready, FA-3 for the build head and readiness invalidation, FA-5 for the
  author's source-control integration, and FA-13A for the run report and scan-report links. The
  catalog review flow itself is external to this product.

---

## EPIC: Command line & saved suites  (FA-16-PENDING)

**Feature area:** FA-16 · **Release:** mixed · **Labels:** FA-16, mixed

### Description

This epic takes the builder outside the web interface and then adds repeatable suites. In the MVP,
the command line starts a test run and runs static-only or full security scans without a test run,
which supports scripted verification and CI-style use. Later, authors can save a named suite of run
entries — each naming a skill, input branch, context and expectations — run the suite, schedule it
nightly, and see each scheduled run's result. The value is automation: the same safe test loop
without a human driving the browser.

### Functional scope

- MVP: start a test run from the command line without the web interface (FR-116), run a static-only
  security scan without a test run (FR-117), and run a full security scan without a test run
  (FR-118).
- Later: save a named suite of runs (FR-119), where each entry names a skill, input branch, context
  and expectations (FR-120), run a saved suite (FR-121), schedule a suite for nightly execution
  (FR-122), and record each scheduled run's result (FR-123).
- Edge cases: the CLI must authenticate with the same authoring identity and membership gate as the
  web surface; a scan command must use the same project membership check; a nightly run must record
  a result even when it cannot start.
- Non-goals: no workflow orchestration or gating; no CLI administration of users, groups or
  projects.

### Implementation guidance / dependency order

- Reuse the run-start validation and packaging path from FA-6A/FA-6B behind a CLI client with the
  same authentication and project-membership checks.
- Add the static-only and full scan commands on top of FA-11 and FA-12.
- Then add the suite model and suite runner, followed by the nightly scheduler and per-scheduled-run
  result recording.
- Finish with tests that CLI and web paths produce identical requests and that a suite records a
  result for every entry.

### Goal / Definition of Done

MVP: an author can start a test run and run static-only or full security scans from the command
line without the web interface, under the same identity and membership rules. Later: an author can
save and run a named suite, schedule it nightly, and see each scheduled run's recorded result.

### Covered requirements (traceability)

- FR-116 — The command line starts a test run without the web interface.
- FR-117 — The command line runs a static-only scan without a test run.
- FR-118 — The command line runs a full security scan without a test run.
- FR-119 — An author saves a named suite of runs.
- FR-120 — A suite entry names a skill, input branch, context and expectations.
- FR-121 — An author runs a saved suite.
- FR-122 — A saved suite can be scheduled for nightly execution.
- FR-123 — The builder records each scheduled run's result.

### MVP subset (if release = mixed)

- MVP: FR-116, FR-117, FR-118.
- Later: FR-119, FR-120, FR-121, FR-122, FR-123.

### Notes

- Depends on FA-6A/FA-6B for run start and preparation, FA-11 and FA-12 for scans, and a scheduler
  for the later nightly suites.

---

## EPIC: Accessibility conformance  (FA-17-PENDING)

**Feature area:** FA-17 · **Release:** MVP · **Labels:** FA-17, MVP

### Description

This epic keeps every builder web surface operable with a keyboard and assistive technology. All
interactive controls must be keyboard operable and show visible focus; custom status components
must expose a programmatic name, role and state; form fields must expose labels, instructions and
errors; run progress and readiness changes must be announced; status must never be conveyed by
colour alone; and text and status colours must meet WCAG 2.1 AA contrast in normal, hover and focus
states. Every surface must reflow to a 320 CSS-pixel viewport without two-dimensional scrolling, and
automated accessibility checks run in continuous verification. This is a cross-cutting quality bar
applied to the surfaces delivered by the other epics.

### Functional scope

- Make every interactive control keyboard operable (FR-130) and give every control a visible focus
  indicator (FR-131).
- Give every custom status component a programmatic name, role and state (FR-132), and expose every
  form field's label, instructions and error message to assistive technology (FR-133).
- Announce run progress and readiness changes to assistive technology (FR-134).
- Never convey readiness or verdict status by colour alone (FR-135), and meet WCAG 2.1 AA contrast
  for text and status colours in normal and hover or focus states (FR-136).
- Run automated accessibility checks in continuous verification (FR-137).
- Reflow every builder web surface to a 320 CSS-pixel viewport without two-dimensional scrolling
  (NFR-012).
- Edge cases: status badges, diff viewers, log streams and the file editor are the highest-risk
  surfaces and must each be covered; dynamic readiness changes need a live region, not a visual
  colour change.
- Non-goals: this epic does not add features; it constrains the presentation of features delivered
  elsewhere.

### Implementation guidance / dependency order

- Build shared accessible primitives first: focus styling, status and form-field components with
  programmatic semantics, and a live-region helper for progress and readiness.
- Apply the primitives to each authoring surface as that surface is built, rather than retrofitting
  at the end; the file editor, run page and diff viewer need explicit review.
- Establish contrast-compliant colour tokens for normal, hover and focus states.
- Add the 320 CSS-pixel reflow pass across every surface, then wire automated accessibility checks
  into continuous verification so regressions are caught on each change.
- Finish with an audit of every web surface against the four WCAG 2.1 AA-relevant behaviours and
  zero critical findings.

### Goal / Definition of Done

Every builder web surface is fully keyboard operable with visible focus, exposes correct
programmatic semantics for status and form fields, announces progress and readiness changes, and
never relies on colour alone. Text and status colours meet WCAG 2.1 AA contrast in normal, hover
and focus states, every surface reflows to 320 CSS pixels without two-dimensional scrolling, and
automated accessibility checks run in continuous verification with no critical findings.

### Covered requirements (traceability)

- FR-130 — Every interactive control is keyboard operable.
- FR-131 — Every interactive control shows a visible focus indicator.
- FR-132 — Every custom status component exposes a name, role and state.
- FR-133 — Every form field exposes its label, instructions and error message.
- FR-134 — Run progress and readiness changes are announced to assistive technology.
- FR-135 — Readiness and verdict status are never conveyed by colour alone.
- FR-136 — Text and status colours meet WCAG 2.1 AA contrast in normal and hover or focus states.
- FR-137 — Automated accessibility checks run in continuous verification.
- NFR-012 — Every builder web surface reflows to a 320 CSS-pixel viewport without 2D scrolling.

### Notes

- Cross-cutting: depends on every epic that renders a web surface. It can be implemented
  incrementally alongside those epics, but the epic is not done until every surface passes.
- The WCAG 2.1 AA target and the 320 CSS-pixel reflow value are PRD-added assumptions recorded in
  the PRD's constraints section, not ADR-given values.

---

## Handoff

- **21 epics planned.** Every PRD requirement — 164 FRs and 19 NFRs — lands in exactly one epic;
  `docs/product/epic-map.json` is the machine-readable traceability record.
- The source is `docs/product/PRD.md`. The PRD records that the Atlassian project
  `bheembhai-skill-builder` (BSB) is the target project and that it contained no issue titled
  `SkillBuilder`; this decomposition is therefore derived from the PRD, not from a Jira work item.
- Next steps: run `sdlc-tracker-sync` to publish these epics to the target Jira project and replace
  the draft `-PENDING` keys with real issue keys, then run `sdlc-plan-stories-write` for each
  published epic.
- This step is authoring only: it writes `epics.md` and `epic-map.json`. Publishing these epics to
  Jira belongs to `sdlc-tracker-sync`, not to this skill.
