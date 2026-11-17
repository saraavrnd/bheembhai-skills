```yaml bheembhai:foreach
epics:
  - id: BSB-39
    epic_key: BSB-39
    summary: "Access & identity"
    feature_area: FA-1
    release: MVP
  - id: BSB-40
    epic_key: BSB-40
    summary: "Build creation & skill scaffolding"
    feature_area: FA-2
    release: MVP
  - id: BSB-41
    epic_key: BSB-41
    summary: "Cloning & edit builds"
    feature_area: FA-2
    release: MVP
  - id: BSB-42
    epic_key: BSB-42
    summary: "Skill editing, build state & readiness tracking"
    feature_area: FA-3
    release: MVP
  - id: BSB-43
    epic_key: BSB-43
    summary: "Test projects & membership"
    feature_area: FA-4
    release: MVP
  - id: BSB-44
    epic_key: BSB-44
    summary: "Integrations & credentials"
    feature_area: FA-5
    release: MVP
  - id: BSB-45
    epic_key: BSB-45
    summary: "Run setup & skill packaging"
    feature_area: FA-6
    release: MVP
  - id: BSB-46
    epic_key: BSB-46
    summary: "Static security scanning"
    feature_area: FA-11
    release: MVP
  - id: BSB-47
    epic_key: BSB-47
    summary: "LLM security scanning"
    feature_area: FA-12
    release: MVP
  - id: BSB-48
    epic_key: BSB-48
    summary: "Run execution & outcome capture"
    feature_area: FA-7
    release: MVP
  - id: BSB-49
    epic_key: BSB-49
    summary: "Run guardrails & re-runs"
    feature_area: FA-8
    release: MVP
  - id: BSB-50
    epic_key: BSB-50
    summary: "Run verification & verdict"
    feature_area: FA-10
    release: MVP
  - id: BSB-51
    epic_key: BSB-51
    summary: "Readiness checks & packaging gates"
    feature_area: FA-10
    release: MVP
  - id: BSB-52
    epic_key: BSB-52
    summary: "Run audit trail, retention & usage records"
    feature_area: FA-13
    release: MVP
  - id: BSB-53
    epic_key: BSB-53
    summary: "Run results & reporting"
    feature_area: FA-13
    release: MVP
  - id: BSB-54
    epic_key: BSB-54
    summary: "Catalog submission"
    feature_area: FA-15
    release: MVP
  - id: BSB-55
    epic_key: BSB-55
    summary: "Command line & suites"
    feature_area: FA-16
    release: mixed
  - id: BSB-56
    epic_key: BSB-56
    summary: "Accessibility conformance"
    feature_area: FA-17
    release: MVP
  - id: BSB-57
    epic_key: BSB-57
    summary: "Jira fixture seeding"
    feature_area: FA-9
    release: Later
  - id: BSB-58
    epic_key: BSB-58
    summary: "Skill history & run comparison"
    feature_area: FA-14
    release: Later
```

# Epics — decomposed from the SkillBuilder PRD

Project: **BSB** (`bheembhai-skill-builder`) · Source: `docs/product/PRD.md` · 20 epics · every FR/NFR mapped exactly once.

> **Work-item note.** The requested work item `SkillBuilder-2` could not be retrieved from the
> configured Atlassian site while this plan was written. `SkillBuilder` is not a valid project key
> there (the site exposes BEEM, BSB, EX, GRAP, LNPRTL); a direct fetch of `SkillBuilder-2` returns
> "issue does not exist", and site-wide text and summary searches return no matching issue. These
> epics therefore derive solely from `docs/product/PRD.md`, whose §8 records the same finding and
> grounds the product in `docs/adr/SK-001-skill-builder.md`. If the work item exists elsewhere,
> reconcile its description and acceptance criteria against the PRD before publishing.
>
> **Keys.** Every epic carries its real Jira key from the `bheembhai-skill-builder` (BSB) project,
> published by `sdlc-tracker-sync`; this block and `epic-map.json` hold the same keys. The three
> feature areas with 15 or more requirements were split into two epics each, so their keys carry a
> letter suffix (`FA-2A`/`FA-2B`, `FA-10A`/`FA-10B`, `FA-13A`/`FA-13B`).
>
> **Publishing.** `sdlc-tracker-sync` published these epics to the `bheembhai-skill-builder` (BSB)
> project; `project_key` in `epic-map.json` records that key.
>
> **NFR placement.** Each cross-cutting NFR is mapped to the one epic that owns the behavior it
> constrains (for example NFR-005 to static scanning, NFR-012 to accessibility) rather than being
> scattered or collected into an epic with no functional owner.

---

## EPIC: Access & identity  (BSB-39)

**Feature area:** FA-1 · **Release:** MVP · **Labels:** FA-1, MVP

## Description

The Skill Builder is a web system in which trusted members of the externally managed
skill-builders group create, adapt and run skills. This epic establishes the entire trust
boundary for it: a visitor must sign in through the platform's existing identity provider,
authoring is available only to a current member of the skill-builders group, and every request —
not just the sign-in — rechecks that membership. On first successful sign-in the builder creates
a local user record keyed by the identity-provider subject; later requests and every other epic
use that record to attribute ownership, membership and runs to a person.

The epic exists because everything downstream assumes an authenticated, authorized actor and a
stable local identity. It deliberately does not administer users, groups or roles: the platform
administrator manages group membership outside this product, and the builder never touches the
platform's database.

## Functional scope

- Reject an unauthenticated visitor from every authoring page and API, before any builder data is
  returned (FR-001, NFR-002).
- Sign a user in with the platform identity provider's existing credentials; the builder keeps no
  separate password or credential store (FR-002).
- Allow authoring features only while the signed-in user is a current member of the
  skill-builders group, checking the membership claim on every request rather than caching a
  sign-in-time decision indefinitely (FR-003, FR-004, NFR-003).
- Reject a sign-in attempt by a user who is not a current group member (FR-138).
- Deny authoring access to a user removed from the group no later than one hour after removal
  (FR-141).
- Create exactly one local user record per identity-provider subject on first successful sign-in
  and reuse that record on every later sign-in by the same subject (FR-005, FR-142).
- Never read from or write to the platform's database; identity data comes only from the identity
  provider and the authenticated session (FR-165).

**Edge cases:** session or token expiry mid-edit; a membership claim that changes while a session
is live; the same subject signing in from several sessions; removal from the group while a run is
in flight; an identity-provider outage during recheck.

**Non-goals:** user, group and role administration; invitations; project ownership transfer; any
access to platform data stores.

## Implementation guidance / dependency order

1. Build the authentication middleware and a fail-closed request guard that covers both pages and
   APIs first — every later epic depends on it.
2. Add membership-claim retrieval and per-request enforcement, with a cache TTL short enough to
   satisfy the one-hour removal bound.
3. Add the idempotent local-user upsert keyed by identity-provider subject, then make it the
   foreign key that later epics use for ownership.
4. Add the explicit isolation check that no code path reaches the platform database.
5. Finish with the sign-in, denial and session-expiry surfaces.

This epic is the foundation for FA-2 through FA-17: the local user record owns builds, projects
and runs, and the request guard protects every authoring endpoint those epics add.

## Goal / Definition of Done

An unauthenticated visitor can reach no authoring surface and receives no builder data; a current
member of the skill-builders group signs in and is consistently represented by one local user
record; a non-member is refused; a removed member loses access within one hour.

## Covered requirements (traceability)

- FR-001 — Unauthenticated visitor cannot open any authoring page
- FR-002 — Sign in with the platform identity provider's credentials
- FR-003 — Authoring only for current skill-builders group members
- FR-004 — Membership claim rechecked on every request
- FR-005 — One local user record per identity-provider subject
- FR-138 — Reject sign-in by a non-member
- FR-141 — Removed member denied within one hour
- FR-142 — Reuse the local user record on later sign-in
- FR-165 — Never read or write the platform database
- NFR-002 — Reject unauthenticated requests before returning data
- NFR-003 — Reject requests from non-member users

## Notes

**External prerequisites:** the platform identity provider and the skill-builders group are
supplied outside this product; the platform administrator manages membership. This epic creates
the local user entity that FA-3's build ownership, FA-4's project ownership and FA-6's run
ownership consume.

---

## EPIC: Build creation & skill scaffolding  (BSB-40)

**Feature area:** FA-2 · **Release:** MVP · **Labels:** FA-2, MVP

## Description

This epic is the entry point for a brand-new skill. An author supplies only a skill name and a
one-line description; the builder creates a build branch from the current head of `main` and
scaffolds that skill's own folder under the catalog's skills directory, including `SKILL.md` with
frontmatter, a `verify.yaml` stub and the standard references, templates and examples folders.
The scaffold alone must pass the catalog's static manifest checks, so an author starts from a
structurally valid skill instead of hand-copying catalog conventions. The epic also owns the name
rules that keep the catalog clean: a name may not already exist on `main`, may not be in use by
another open build, and must follow the sdlc prefix, area segment and action segment pattern.

## Functional scope

- Create a build from a skill name and a one-line description (FR-006).
- Create the build branch from the current head of `main` (FR-007).
- Scaffold the skill's own folder under the catalog's skills directory on that branch (FR-008).
- Emit `SKILL.md` carrying the skill's frontmatter (FR-009).
- Emit a `verify.yaml` stub (FR-143).
- Emit the standard references, templates and examples folders (FR-144).
- Ensure the freshly scaffolded skill passes the catalog's static manifest checks with no edit
  (FR-010).
- Reject a create whose skill name already exists on `main` (FR-015), is used by another open
  build (FR-016), or does not follow the sdlc prefix, area and action pattern (FR-017).

**Edge cases:** two authors creating the same name at once (the open-build check needs a unique
constraint, not just a read); `main` moving between name validation and branch creation (record
the SHA actually branched from); partial scaffold failure (no half-built build is left open);
name normalisation and reserved names.

**Non-goals:** cloning an existing skill or editing an existing catalog skill (FA-2B); editing,
running or scanning the build (later epics).

## Implementation guidance / dependency order

1. Implement skill-name validation, the `main`-existence check and the open-build uniqueness rule
   first; FA-2B reuses them.
2. Add the build entity (owner from FA-1, name, branch, base SHA, build kind, state).
3. Create the build branch from `main`'s recorded head.
4. Add the scaffold generator that emits `SKILL.md`, the `verify.yaml` stub and the folder
   skeleton.
5. Finish by running the catalog's static manifest checks against a generated scaffold in CI so
   FR-010 cannot regress.

The build entity and branch added here are extended by FA-3 (head and readiness tracking) and
consumed by FA-6 (packaging), FA-10B (readiness), FA-15 (submission) and FA-2B (clone/edit).

## Goal / Definition of Done

An author can start a new build from just a name and a description; the builder places a
manifest-valid scaffold on a branch cut from `main`; duplicate, in-use and malformed names are
refused with a clear reason.

## Covered requirements (traceability)

- FR-006 — Create a build from a name and one-line description
- FR-007 — Create the build branch from the head of main
- FR-008 — Scaffold the skill folder under the catalog skills directory
- FR-009 — Scaffold SKILL.md with frontmatter
- FR-010 — Scaffold passes catalog manifest checks unedited
- FR-015 — Reject a name that already exists on main
- FR-016 — Reject a name used by another open build
- FR-017 — Reject a name outside the sdlc prefix/area/action pattern
- FR-143 — Scaffold a verify.yaml stub
- FR-144 — Scaffold references, templates and examples folders

## Notes

**Depends on:** FA-1 (the owning local user and request guard). **Feeds:** FA-2B (shared name
validation), FA-3 (build/branch state), FA-6, FA-10B, FA-15. The catalog repository and its
manifest checks are external prerequisites.

---

## EPIC: Cloning & edit builds  (BSB-41)

**Feature area:** FA-2 · **Release:** MVP · **Labels:** FA-2, MVP

## Description

This epic covers starting from a skill that already exists instead of a blank template. An author
can clone a catalog skill under a new name: the builder copies the skill's whole folder to the new
skill path, rewrites the skill name in the copied frontmatter, and leaves the source skill's files
untouched. Separately, an author can open an existing catalog skill in an edit build — a branch
cut from `main` that changes that same skill's folder in place rather than creating a second
folder — and then follow the same run, scan, Ready and Submit path as any other build. Edit builds
make the builder the place to fix a catalog skill, while the original changes only when a catalog
pull request merges (FA-15).

## Functional scope

- Clone an existing catalog skill under a new name (FR-011).
- Copy the skill's whole folder to the new skill path (FR-012).
- Rewrite the skill name in the copied frontmatter (FR-013).
- Leave the source skill's files unchanged (FR-014).
- Open an existing catalog skill in an edit build on a branch cut from `main` (FR-124).
- Make an edit build change the existing skill folder rather than create a second folder (FR-125).
- Reject an edit build for a skill name that does not exist on `main` (FR-126).

**Edge cases:** source folders containing binaries or large files; frontmatter variants and
comments that must survive the rewrite; case-insensitive name collisions; the source skill
changing while a clone is prepared (clone from a pinned SHA); an edit build and a clone of the
same skill open concurrently.

**Non-goals:** writing to the catalog directly or merging the build branch (FA-15); running or
scanning the result (later epics).

## Implementation guidance / dependency order

1. Reuse FA-2A's name validation, build entity and branch creation, adding a `build_kind` of
   clone or edit.
2. Implement the folder copy for clones, then the frontmatter parse/rewrite, and assert the source
   tree is byte-identical afterwards.
3. Implement edit-build resolution of the existing skill folder from `main` and reject an unknown
   name early.
4. Finish with a check that a clone or edit produces exactly one skill folder at the intended
   path.

**Depends on:** FA-2A (name rules, build/branch creation). **Feeds:** FA-3 (both build kinds are
edited and tracked the same way), FA-6, FA-10B, FA-15.

## Goal / Definition of Done

An author can clone a catalog skill under a new name with its folder copied and its frontmatter
renamed while the source is untouched, and can open an existing skill in an edit build that
changes that skill's folder in place.

## Covered requirements (traceability)

- FR-011 — Clone an existing catalog skill under a new name
- FR-012 — Copy the skill's whole folder
- FR-013 — Rewrite the skill name in the copied frontmatter
- FR-014 — Leave the source skill's files unchanged
- FR-124 — Open an existing catalog skill in an edit build from main
- FR-125 — An edit build changes the existing skill folder
- FR-126 — Reject an edit build for a name absent from main

## Notes

**Depends on:** FA-2A. Name rejection rules (FR-015 through FR-017) also apply to clone names and
are implemented once in FA-2A; this epic does not restate them.

---

## EPIC: Skill editing, build state & readiness tracking  (BSB-42)

**Feature area:** FA-3 · **Release:** MVP · **Labels:** FA-3, MVP

## Description

This epic is the authoring loop inside a build. An author edits the content of a file in the
build's skill folder and saves it; each save becomes a commit on the build branch, and the latest
commit SHA becomes the build's head. The build page shows both the current head SHA and the
readiness status for that exact SHA. When a new commit moves the head, the previously recorded
ready SHA is cleared, so "Ready" can never describe code the author has already changed. This
gives the rest of the builder a single, honest pointer — the build head — that packaging,
readiness, reporting and submission all refer to.

## Functional scope

- Edit the content of a file in a build's skill folder (FR-127).
- Save an edited file to the build branch (FR-162).
- Create a commit on the build branch for each save (FR-018).
- Record the latest commit SHA as the build head (FR-019).
- Show the current head SHA on the build page (FR-020).
- Show the build's readiness status for that head SHA (FR-021).
- Clear the previously recorded ready SHA when a new commit is created (FR-022).

**Edge cases:** two saves racing on the same file (optimistic concurrency with a conflict
response); a no-op save that should not create an empty commit; a commit failure leaving the
previous head intact; binary or large files; a save on a build whose pull request is already open
(which also clears readiness under FR-114 in FA-15).

**Non-goals:** versioning skill content separately from the branch; merging branches; computing
the readiness checks themselves (FA-10B).

## Implementation guidance / dependency order

1. Build the save/commit service first: write content, commit on the build branch, return the new
   SHA, and make the operation atomic per file.
2. Add head tracking, storing head SHA and ready SHA as separate fields so invalidation is a
   pointer comparison rather than a rewrite.
3. Add the build-page surfaces for head SHA and readiness.
4. Add the invalidation rule (head change clears ready SHA) and test it against every path that
   can create a commit.
5. Finish with concurrency and failure handling.

**Depends on:** FA-2A/FA-2B (build and branch exist). **Feeds:** FA-6 (packaging pins the head
SHA), FA-10B (Ready is recorded at a SHA), FA-13A (reports show the skills commit), FA-15 (submit
reads build state and readiness).

## Goal / Definition of Done

An author can edit and save a file in the build's skill folder; every save appears as a commit
that becomes the build head; the build page shows the head SHA and the readiness for that SHA; and
saving a new commit clears any prior ready status.

## Covered requirements (traceability)

- FR-018 — Each save creates a commit on the build branch
- FR-019 — Record the latest commit SHA as the build head
- FR-020 — Build page shows the current head SHA
- FR-021 — Build page shows readiness status for the head SHA
- FR-022 — A new commit clears the previously recorded ready SHA
- FR-127 — Edit a file in the build's skill folder
- FR-162 — Save an edited file to the build branch

## Notes

**Depends on:** FA-1 (owner identity), FA-2A/FA-2B (build and branch). **Feeds:** FA-6, FA-10B,
FA-13A, FA-15. The ready-SHA field this epic persists is written by FA-10B and read by FA-15.

---

## EPIC: Test projects & membership  (BSB-43)

**Feature area:** FA-4 · **Release:** MVP · **Labels:** FA-4, MVP

## Description

A test project is the shared container in which a small group runs skills against test systems.
A signed-in author creates one and becomes its owner; the owner adds other skill-builder users as
members and removes them; membership is what authorizes an author to start a run or a scan in
that project; and only the owner may change the project's integrations. The epic's value is
sharing without credential exposure: teammates can operate in the same project, but the owner
controls what systems it points at and who may use it. The project also carries the non-secret
configuration (integrations, the LLM-scan model choice) that later epics read.

## Functional scope

- Create a test project as a signed-in author (FR-023).
- Record the creator as the project owner (FR-024).
- Let the owner add another skill-builder user as a project member (FR-025).
- Let the owner remove a project member (FR-026).
- Use project membership to authorize starting a test run in that project (FR-027).
- Restrict changes to a project's integrations to its owner (FR-028).

**Edge cases:** adding a user who is not a current member of the skill-builders group (refuse);
duplicate membership (idempotent); removing a member with a run in flight (deny new starts, let
the run reach a terminal state); removal of the last owner (not allowed); an owner who loses
skill-builders membership (handled by FA-1's gate).

**Non-goals:** project ownership transfer, user/group/role administration, and project deletion
are out of scope for this product.

## Implementation guidance / dependency order

1. Add the project entity with its owner and the membership join table; enforce the one-owner
   invariant.
2. Add create-project and add/remove-member flows with owner-only authorization.
3. Expose a single membership/ownership authorization helper and use it from the first later
   caller rather than re-implementing checks.
4. Add the project settings container that FA-5 fills with integrations and the LLM-scan model.

**Depends on:** FA-1 (local user and group gate). **Feeds:** FA-5 (owner-only integration
changes), FA-6 (membership authorizes a run), FA-11 and FA-12 (membership authorizes a scan),
FA-9 (the project's Jira settings).

## Goal / Definition of Done

An author can create a test project and own it; the owner can add and remove skill-builder
members; membership authorizes starting a run in the project; and a non-owner cannot change the
project's integrations.

## Covered requirements (traceability)

- FR-023 — A signed-in author creates a test project
- FR-024 — Record the creator as the project owner
- FR-025 — The owner adds another skill-builder user as a member
- FR-026 — The owner removes a project member
- FR-027 — Membership authorizes starting a test run
- FR-028 — Only the owner changes the project's integrations

## Notes

**Depends on:** FA-1. **Feeds:** FA-5, FA-6, FA-11, FA-12, FA-9, and FR-163's project-level
LLM-scan model setting.

---

## EPIC: Integrations & credentials  (BSB-44)

**Feature area:** FA-5 · **Release:** MVP · **Labels:** FA-5, MVP

## Description

To run a skill, a test project must point at a Jira site, a source-control sandbox and a model
endpoint. This epic lets the project owner configure those three integrations and keeps the
builder from becoming a secret store: credential values live in the external secret store and the
builder records only an opaque reference, never shows a value, and never lets one reach its logs
or run results. The owner can verify an integration's credentials and the builder records when
they were last verified. The epic also warns when a source-control integration targets a
repository that a platform project also uses, and records the MCP server definitions that the Jira
and source-control integrations expose to runs — non-secret configuration, not credentials.

## Functional scope

- Configure a Jira integration from a site URL and either a project key or a template project
  (FR-029).
- Configure a source-control integration from a sandbox repository and a base branch (FR-030).
- Configure a model profile from a vendor, a base URL and a tier-to-model mapping (FR-031).
- Never store an integration's credential value in the builder's own records (FR-032).
- Verify an integration's credentials (FR-033).
- Record when an integration's credentials were last verified (FR-034).
- Warn when a source-control integration targets a repository also used by a platform project
  (FR-035).
- Never display an integration's credential value in the interface (FR-036).
- Record the MCP server definition the Jira integration exposes to a run (FR-128).
- Record the MCP server definition the source-control integration exposes to a run (FR-129).
- Keep credential values out of builder logs and run results (NFR-004).
- Ensure runs use only test-purpose Jira, source-control and model credentials (NFR-006).

**Edge cases:** the secret store being unreachable during save or verification; a verification
that times out or is refused (record failure, keep the previous verified timestamp meaning
intact); malformed MCP definitions; a tier with no model mapping; the platform repository
inventory being unavailable (the overlap warning degrades to "unknown", not a false negative); a
credential reference rotated in the secret store.

**Non-goals:** administering the external secret store; provisioning Jira, sandbox repositories or
model endpoints; storing any secret in the builder database.

## Implementation guidance / dependency order

1. Define the secret-reference abstraction first: write a value to the secret store, keep only an
   opaque handle, and read through the handle at execution time.
2. Add integration CRUD guarded by FA-4's owner check, with the tier-to-model mapping validated.
3. Add credential verification and the last-verified timestamp.
4. Add the repository-overlap warning against the platform's inventory.
5. Add the MCP server definition fields for the Jira and source-control integrations.
6. Finish with a redaction layer that scrubs credential values from logs, errors and results, and
   proves it with tests.

**Depends on:** FA-4 (owner-only authorization and the project settings container). **Feeds:**
FA-6 (run inputs and model profile), FA-7 (model profile), FA-9 (Jira integration), FA-12
(LLM-scan model endpoint), FA-15 (source-control identity).

## Goal / Definition of Done

A project owner can configure and verify Jira, source-control and model integrations; no credential
value is ever stored, displayed or logged by the builder; MCP definitions are recorded; and an
overlapping source-control repository produces a warning.

## Covered requirements (traceability)

- FR-029 — Configure a Jira integration with site URL and project or template
- FR-030 — Configure a source-control integration with sandbox repo and base branch
- FR-031 — Configure a model profile with vendor, base URL and tier mapping
- FR-032 — Never store a credential value in builder records
- FR-033 — Verify an integration's credentials
- FR-034 — Record when credentials were last verified
- FR-035 — Warn when a repository is also used by a platform project
- FR-036 — Never display a credential value
- FR-128 — Record the Jira integration's MCP server definition
- FR-129 — Record the source-control integration's MCP server definition
- NFR-004 — Credential values never appear in logs or run results
- NFR-006 — Runs use only test-purpose credentials

## Notes

**Depends on:** FA-4. **External prerequisites:** the secret store, the platform repository
inventory and the test Jira/source-control/model endpoints are supplied outside this product.

---

## EPIC: Run setup & skill packaging  (BSB-45)

**Feature area:** FA-6 · **Release:** MVP · **Labels:** FA-6, MVP

## Description

This epic turns an author's intent into a prepared, immutable run. The author starts a run in a
test project they belong to and chooses the skills branch, the input branch, a workflow and step
context, optionally some reviewer feedback or an upstream handoff, and a model profile and tier.
The builder resolves the skills branch to a commit SHA at run start, packages the skill at that
commit into a content-addressed bundle (reusing an existing bundle when the same commit is
packaged again), creates the run branch — the run's output branch — from the input branch's head,
and records that head as the run's baseline. The run never writes to its input branch. The result
is a reproducible, fast preparation step and a hard boundary between what the run reads and what
it produces.

## Functional scope

- Start a run in a test project the author is a member of (FR-037).
- Resolve the skills branch to a commit SHA at run start (FR-038).
- Package the skill at that commit into a content-addressed bundle (FR-039).
- Reuse an existing bundle when the same skills commit is packaged again (FR-040).
- Create the run branch from the input branch's head (FR-041).
- Record the input branch's head SHA as the run's baseline (FR-042).
- Never write to the run's input branch (FR-043).
- Offer a choice of skills branch (FR-145), input branch (FR-146), workflow and step context
  (FR-147), optional reviewer feedback or upstream handoff (FR-148), model profile (FR-149) and
  model tier (FR-150).
- Prepare non-model run inputs within 60 seconds for a skill bundle of up to 5 MB (NFR-001).
- Produce an identical bundle whenever the same skills commit is prepared twice (NFR-009).

**Edge cases:** the skills branch moving between SHA resolution and packaging (pin the resolved
SHA); an input branch that does not exist or is the same as the run branch; a cached bundle whose
content hash no longer matches; concurrent runs sharing one bundle; a very large bundle; optional
feedback that is malformed; a model tier with no mapping (FA-5 validation).

**Non-goals:** executing the skill (FA-7); orchestrating multi-step workflows, gates or routing
(the builder runs one skill per run).

## Implementation guidance / dependency order

1. Add the run entity and the run-start configuration flow, validating membership and every
   selected input.
2. Implement deterministic SHA resolution and record it on the run.
3. Build the deterministic bundler with a content hash and a cache keyed by skills SHA plus
   packaging inputs; prove byte-identical output on a repeat.
4. Create the run branch from the input head and record the baseline SHA.
5. Enforce input-branch read-only behavior at the branch/permission layer, not only in application
   code.
6. Finish with the preparation-time budget: measure and tune to NFR-001 for a 5 MB bundle.

**Depends on:** FA-4 (membership), FA-5 (integrations and model profile), FA-3 (build head and
branch). Packaging must also invoke the verifier lint/self-test/range gates owned by FA-10B
(FR-071 through FR-073) before a bundle is accepted. **Feeds:** FA-7, FA-8, FA-9, FA-11, FA-12,
FA-16.

## Goal / Definition of Done

An author who belongs to a test project can start a run by choosing the documented inputs; the
builder pins the skills commit, produces a reusable content-addressed bundle, creates a separate
run branch from the input head and records the baseline; the input branch is never modified; and
repeated preparation of the same commit is identical and fast.

## Covered requirements (traceability)

- FR-037 — Start a run in a test project the author belongs to
- FR-038 — Resolve the skills branch to a commit SHA
- FR-039 — Package the skill into a content-addressed bundle
- FR-040 — Reuse a bundle for the same skills commit
- FR-041 — Create the run branch from the input branch head
- FR-042 — Record the input branch head as the baseline
- FR-043 — A run never writes to its input branch
- FR-145 — Offer a choice of skills branch
- FR-146 — Offer a choice of input branch
- FR-147 — Offer a choice of workflow and step context
- FR-148 — Optionally supply reviewer feedback or an upstream handoff
- FR-149 — Offer a choice of model profile
- FR-150 — Offer a choice of model tier
- NFR-001 — Run preparation within 60 seconds for a 5 MB bundle
- NFR-009 — Same skills commit produces an identical bundle

## Notes

**Depends on:** FA-3, FA-4, FA-5, and the packaging gates in FA-10B. **Feeds:** FA-7, FA-8,
FA-9, FA-11, FA-12, FA-16. The run/baseline/run-branch entities created here are the anchor for
every later run-scoped epic.

---

## EPIC: Static security scanning  (BSB-46)

**Feature area:** FA-11 · **Release:** MVP · **Labels:** FA-11, MVP

## Description

Unsafe skill content must not reach a run. This epic runs a static security scan on the exact
skill content before every run, inside a scanner that has no network access. A completed scan
result is reused when the content has not changed. The scan passes only when the verdict is not
`DO_NOT_INSTALL`, no critical finding exists and coverage is complete; an accepted finding can
never clear the block, and a timed-out scan is recorded as failed. Reports show the score, the
recommendation and each finding's severity, rule, file and line. The builder's verdict must match
the platform's for the same content and scanner version, so an author can trust the gate. An
author can also start a static-only scan from the skill page without creating a run.

## Functional scope

- Run a static security scan on the exact skill content before every run (FR-076).
- Reuse a completed static scan result when the content is unchanged (FR-077).
- Treat a `DO_NOT_INSTALL` verdict as not passing (FR-078).
- Treat a critical finding as not passing (FR-079).
- Treat incomplete scan coverage as not passing (FR-080).
- Never let an accepted finding clear a static-scan block (FR-081).
- Time out a security scan after ten minutes (FR-087).
- Record a timed-out scan as failed (FR-088).
- Show the scan's score in the report (FR-089).
- Match the platform's verdict for the same content and scanner version (FR-091).
- Start a static-only scan from the skill page for a test project the author belongs to, without
  a run (FR-092).
- Show the scan's recommendation in the report (FR-154).
- List each finding's severity, rule, file and line (FR-155).
- Run the static scan with no network access (NFR-005).

**Edge cases:** scanner crash versus timeout; partial coverage; an unchanged content hash with a
changed scanner version (must not reuse — include the scanner version in the cache key);
findings previously accepted by policy; scanner image unavailable; a scan started from the skill
page while an identical run-triggered scan is in flight.

**Non-goals:** the model-based scan (FA-12); fixing findings; changing builtin verifier checks
(out of scope).

## Implementation guidance / dependency order

1. Build the network-isolated scanner runner and its result model first; make the isolation a
   tested property.
2. Add the content-addressed scan cache keyed by content hash and scanner version, and the
   timeout/failure recording.
3. Implement the pass classifier exactly as FR-078 through FR-081 specify, so the run gate and the
   Ready check share one implementation.
4. Add the report fields (score, recommendation, findings) and the platform-parity comparison.
5. Finish with the skill-page static-only scan entry point, reusing FA-4 membership.

**Depends on:** FA-4 (membership for a skill-page scan), FA-6 (the packaged content hash). **Feeds:**
FA-8's pre-run gate (FR-055), FA-10B's Ready evaluation (FR-069/FR-070), FA-15's report links and
FA-16's CLI scan.

## Goal / Definition of Done

Before every run the exact skill content is statically scanned with no network access; a
non-passing scan blocks the run; unchanged content reuses a prior result; reports show score,
recommendation and findings; timeouts are failures; and the verdict agrees with the platform's.

## Covered requirements (traceability)

- FR-076 — Statically scan the exact skill content before every run
- FR-077 — Reuse a completed static scan result for unchanged content
- FR-078 — DO_NOT_INSTALL is not a passing result
- FR-079 — A critical finding is not a passing result
- FR-080 — Incomplete coverage is not a passing result
- FR-081 — An accepted finding cannot clear the block
- FR-087 — Security scans time out after ten minutes
- FR-088 — A timed-out scan is recorded as failed
- FR-089 — The report shows the scan score
- FR-091 — The verdict matches the platform's for the same content/version
- FR-092 — Start a static-only scan from the skill page
- FR-154 — The report shows the scan recommendation
- FR-155 — The report lists severity, rule, file and line per finding
- NFR-005 — The static scan has no network access

## Notes

**Depends on:** FA-4, FA-6. **External prerequisites:** the pinned scanner image. This epic is
the source of the static-scan fact consumed by FA-8 and FA-10B; it must not be re-implemented
there.

---

## EPIC: LLM security scanning  (BSB-47)

**Feature area:** FA-12 · **Release:** MVP · **Labels:** FA-12, MVP

## Description

This epic adds a model-based security review that advises the author without ever blocking a run.
The builder triggers it only after the static scan passes for the current content. The scan is
isolated to the greatest extent possible: it receives no credential other than the model key and
can reach only the model endpoint. Its findings are shown to the author and the report lists each
finding's severity, rule, file and line and names the model that ran the scan. A scan that cannot
run is recorded as unavailable rather than failed, and an unavailable scan still lets a build
become Ready. An author can also start a full security scan from the skill page without a run; that
scan uses the LLM-scan model profile configured on the scan's test project.

## Functional scope

- Trigger the LLM scan only after the static scan passes for the current content (FR-082).
- Give the scan no credential other than the model key (FR-083).
- Let the scan reach only the model endpoint (FR-084).
- Never let the LLM scan block a run (FR-085).
- Show LLM scan findings to the author (FR-086).
- Show which model ran the scan (FR-090).
- Start a full security scan from the skill page for a test project the author belongs to, without
  a run (FR-093).
- Record an LLM scan that cannot run as unavailable (FR-139).
- List each finding's severity, rule, file and line (FR-156).
- Use the LLM-scan model profile configured for the scan's test project in a full scan (FR-163).

**Edge cases:** the model timing out or erroring (record unavailable); partial findings; the model
endpoint unreachable; the static result changing between trigger and execution (re-check the
precondition); prompt-injection text inside skill content (treat it as data, not instructions); a
project with no LLM-scan model configured; the model returning no findings.

**Non-goals:** blocking runs; replacing the static scan; changing the project's model setting
per run (only the owner configures it).

## Implementation guidance / dependency order

1. Add the model-profile resolver bound to the test project, then the scan job with the static-pass
   precondition from FA-11.
2. Enforce the network allowlist (model endpoint only) and the credential restriction (model key
   only) in the scan environment, and test both.
3. Add the report model (findings, severity, rule, file, line, model) and the author-facing view.
4. Add the unavailable outcome and its effect on readiness (satisfied, not blocking) through
   FA-10B.
5. Finish with the skill-page full-scan entry point, reusing FA-4 membership.

**Depends on:** FA-11 (static-pass precondition), FA-4 (membership), FA-5 (model endpoint and
profile). **Feeds:** FA-10B's Ready evaluation (FR-069/FR-070), FA-15's report links, FA-16's CLI
full scan.

## Goal / Definition of Done

After a passing static scan, the builder runs a model-based security scan that cannot block a run,
uses only the model key and endpoint, records unavailable when it cannot run, and shows findings
and the model used; an author can start a full scan from the skill page without a run.

## Covered requirements (traceability)

- FR-082 — Trigger the LLM scan only after a passing static scan
- FR-083 — The scan receives no credential other than the model key
- FR-084 — The scan can reach only the model endpoint
- FR-085 — The LLM scan never blocks a run
- FR-086 — LLM scan findings are shown to the author
- FR-090 — The report shows the model that ran the scan
- FR-093 — Start a full scan from the skill page without a run
- FR-139 — Record an LLM scan that cannot run as unavailable
- FR-156 — The report lists severity, rule, file and line per finding
- FR-163 — A full scan uses the project's LLM-scan model profile

## Notes

**Depends on:** FA-4, FA-5, FA-11. **External prerequisites:** the model endpoint. An unavailable
scan is a recorded, non-blocking outcome by design (FR-139 and FR-069).

---

## EPIC: Run execution & outcome capture  (BSB-48)

**Feature area:** FA-7 · **Release:** MVP · **Labels:** FA-7, MVP

## Description

This epic executes one prepared run and captures what happened. The builder runs the skill in the
same runtime as the platform, streams progress and logs to the run page while it executes,
classifies the outcome using the platform engine's result rules, and records the exact execution
component versions, the verifier version, the model profile and the model tier the run used. When
tracing is enabled, the run's trace identifies it as a test-environment run. Capturing these facts
at execution time is what lets verification, reporting, comparison and audit refer to exactly what
ran rather than reconstructing it later.

## Functional scope

- Execute the skill in the same runtime as the platform (FR-044).
- Show progress on the run page while the run executes (FR-045).
- Show logs on the run page while the run executes (FR-046).
- Classify the run outcome with the platform engine's result rules (FR-047).
- Record the exact execution-component versions used by the run (FR-048).
- Record the model profile used by the run (FR-049).
- Record the exact verifier version used by the run (FR-151).
- Record the model tier used by the run (FR-152).
- When tracing is enabled, identify the run's trace as a test-environment run (NFR-011).

**Edge cases:** the agent container crashing versus exiting non-zero; a runtime image that does not
match the recorded component versions; log-stream backpressure or disconnection; missing component
metadata; tracing disabled (nothing to mark); a run cancelled at the deadline (FA-8 records the
terminal state).

**Non-goals:** computing verification (FA-10A); enforcing caps, deadlines or pre-run gates (FA-8);
workflow orchestration.

## Implementation guidance / dependency order

1. Build the runtime adapter that starts the platform's execution container from the prepared
   bundle and run branch, and make it the only path that executes skills.
2. Add the progress/log event stream and the run-page surface that consumes it.
3. Implement the outcome classifier against the platform engine's result rules, with fixture
   outcomes for tests.
4. Add the run metadata record: component versions, verifier version, model profile and tier.
5. Finish with trace tagging so a test-environment run is identifiable when tracing is enabled.

**Depends on:** FA-5 (model profile), FA-6 (prepared bundle, run branch, baseline). **Feeds:**
FA-8 (caps and deadlines), FA-10A (the run output to verify), FA-13A and FA-13B (reports and
records).

## Goal / Definition of Done

A prepared run executes in the platform runtime with live progress and logs, its outcome is
classified by the platform engine's rules, the exact components and model used are recorded, and
an enabled trace identifies the run as a test-environment run.

## Covered requirements (traceability)

- FR-044 — Execute the skill in the same runtime as the platform
- FR-045 — The run page shows progress while executing
- FR-046 — The run page shows logs while executing
- FR-047 — Classify the outcome with the platform engine's result rules
- FR-048 — Record the exact execution-component versions
- FR-049 — Record the model profile used
- FR-151 — Record the exact verifier version used
- FR-152 — Record the model tier used
- NFR-011 — An enabled trace identifies the run as a test-environment run

## Notes

**Depends on:** FA-5, FA-6. **External prerequisites:** the pinned platform runtime and component
images, and the trace store. This epic creates the run metadata that FA-13A displays, FA-13B
records and FA-14 compares.

---

## EPIC: Run guardrails & re-runs  (BSB-49)

**Feature area:** FA-8 · **Release:** MVP · **Labels:** FA-8, MVP

## Description

This epic bounds a run's cost and time, refuses unsafe starts, and makes iteration cheap. An author
sets a turn cap and a spend cap for a run; the run stops when it reaches either. The builder refuses
to start a run when its execution components are incompatible and when the static scan for the
skill content did not pass. A run must reach a terminal state within its configured deadline, and a
run that exceeds the deadline is recorded as failed; the deadline is set per installation through
environment configuration, not in code. Finally, an author can re-run a prior run with the same
inputs and the latest commit of its skills branch, and can use a prior run's output branch as the
input branch of a later run, enabling cheap output chaining.

## Functional scope

- Let the author set a turn cap for a run (FR-050).
- Stop a run when it reaches its turn cap (FR-051).
- Let the author set a spend cap for a run (FR-052).
- Stop a run when it reaches its spend cap (FR-053).
- Refuse to start a run when its execution components are incompatible (FR-054).
- Refuse to start a run when the static scan for the skill content did not pass (FR-055).
- Re-run a prior run with the same inputs and the latest commit of its skills branch (FR-056).
- Use a prior run's output branch as a later run's input branch (FR-057).
- Ensure every run reaches a terminal state within its configured deadline (NFR-007).
- Record a run that exceeds its deadline as failed (NFR-008).
- Allow the run deadline to change per installation without a code change (NFR-019).

**Edge cases:** both caps reached in the same turn (stop once, record the triggering cap); spend
estimation error near the cap; the deadline expiring during preparation as well as during
execution; an unavailable component-compatibility matrix (fail closed); the skills branch moving
between a re-run request and start (resolve latest at start); chaining a branch that no run
produced; zero or negative caps (reject).

**Non-goals:** nightly scheduling and saved suites (Later, FA-16); workflow gates and routing
(explicitly out of scope).

## Implementation guidance / dependency order

1. Add the pre-run preflight: component-compatibility check and the static-scan gate from FA-11
   (FR-054, FR-055).
2. Add cap fields to run setup and enforce them in the execution loop from FA-7, recording which
   cap stopped the run.
3. Add the deadline timer over preparation and execution, sourced from installation environment
   configuration, and the failed terminal state on expiry.
4. Implement re-run by reusing FA-6 setup with the same inputs and the resolved latest skills
   commit.
5. Finish with output-branch chaining, validating that the chosen output branch came from a run.

**Depends on:** FA-6 (run setup), FA-7 (execution loop), FA-11 (static scan gate), FA-5 (component
compatibility inputs). **Feeds:** FA-13A (turn count, cost, terminal state) and FA-16 (suite
runner reuses the same run path).

## Goal / Definition of Done

A run stops at its turn or spend cap, never starts with incompatible components or a non-passing
static scan, reaches a terminal state within the installation's deadline and is failed if it does
not, and can be re-run or chained from a prior run's output branch.

## Covered requirements (traceability)

- FR-050 — The author sets a run turn cap
- FR-051 — A run stops at its turn cap
- FR-052 — The author sets a run spend cap
- FR-053 — A run stops at its spend cap
- FR-054 — Refuse a start with incompatible execution components
- FR-055 — Refuse a start when the static scan did not pass
- FR-056 — Re-run with the same inputs and latest skills commit
- FR-057 — Use a prior output branch as a later run's input
- NFR-007 — Every run reaches a terminal state within its deadline
- NFR-008 — A run over its deadline is recorded as failed
- NFR-019 — The run deadline is installation-configurable

## Notes

**Depends on:** FA-5, FA-6, FA-7, FA-11. NFR-019 means the deadline value is supplied through
installation environment variables; this epic exposes and consumes that setting but fixes no
numeric default.

---

## EPIC: Run verification & verdict  (BSB-50)

**Feature area:** FA-10 · **Release:** MVP · **Labels:** FA-10, MVP

## Description

A run's claimed success is not the same as a verified one. This epic invokes the shared
verification layer on the run branch after the agent exits, passing the run's baseline SHA so the
verifier can judge exactly what changed, and supplies the `verify.yaml` from the skills commit. It
records the verdict the agent claimed, the final verdict produced by the shared layer, and whether
verification overturned the claim. Because the layer is a common package used by both the builder
and the agent image, it runs outside the agent container so the agent cannot edit what grades it.
The epic also makes re-verification cheap: an existing output branch can be re-verified against a
changed `verify.yaml` without running the agent or a model, and the result shows which checks
flipped.

## Functional scope

- Run the shared verification layer on the run branch after the agent exits (FR-063).
- Pass the run's baseline SHA to the verifier (FR-064).
- Record the verdict the agent claimed (FR-065).
- Record the final verdict after verification (FR-066).
- Record whether verification overturned the claimed verdict (FR-067).
- Re-verify an existing output branch with a changed `verify.yaml` without the agent or a model
  (FR-074).
- Show which checks flipped in a re-verification (FR-075).
- Give the verifier the `verify.yaml` from the skills commit (FR-153).
- Record the shared verification layer's verdict as the final verdict (FR-164).
- Produce the same verification result for the same inputs and component versions (NFR-010).

**Edge cases:** the verification layer unavailable or erroring; a malformed or missing
`verify.yaml`; an output branch with no run; a baseline that cannot be resolved; a re-verify where
the output branch was deleted; non-deterministic checks; the agent attempting to modify the
verifier (must be impossible because it runs outside the container).

**Non-goals:** defining builtin verifier checks (out of scope); aggregating the four Ready checks
(FA-10B); making verification block a run at start (FA-8 does the static gate).

## Implementation guidance / dependency order

1. Integrate the shared verification layer as an external dependency and invoke it outside the
   agent container; assert the isolation in a test.
2. Resolve the baseline SHA from FA-6 and the `verify.yaml` from the skills commit, then record
   claimed verdict, final verdict and the overturned flag.
3. Add the normal verification path after execution (FA-7's terminal event).
4. Add the re-verify path: load an output branch and a supplied `verify.yaml`, invoke the same
   layer without an agent or model, and diff the check results to produce the flip set.
5. Make the result deterministic for identical inputs and pinned component versions.

**Depends on:** FA-6 (baseline and skills commit), FA-7 (run output). **Feeds:** FA-10B (the
run-passed component of Ready), FA-13A (final verdict), FA-14 (check comparison).

## Goal / Definition of Done

Every completed run is verified by the shared layer with its baseline and skills-commit
`verify.yaml`; claimed, final and overturned verdicts are recorded; and an output branch can be
re-verified without an agent or model, showing which checks flipped.

## Covered requirements (traceability)

- FR-063 — Run the shared verification layer on the run branch
- FR-064 — Pass the run's baseline SHA to the verifier
- FR-065 — Record the agent's claimed verdict
- FR-066 — Record the final verdict after verification
- FR-067 — Record whether verification overturned the claim
- FR-074 — Re-verify an output branch without the agent or a model
- FR-075 — Show which checks flipped on re-verification
- FR-153 — The verifier receives the verify.yaml from the skills commit
- FR-164 — The final verdict is the shared verification layer's
- NFR-010 — Same inputs and component versions produce the same verification result

## Notes

**Depends on:** FA-6, FA-7. **External prerequisite:** the shared verification layer from the
Bheembhai solution is a third-party dependency, not code this product owns. Verification runs
outside the agent container by design.

---

## EPIC: Readiness checks & packaging gates  (BSB-51)

**Feature area:** FA-10 · **Release:** MVP · **Labels:** FA-10, MVP

## Description

This epic defines what "Ready" means and protects packaging. The builder checks a build's manifest
validity at a commit SHA and marks the build Ready at that SHA only when four facts hold: the
manifest check passes, a run passes, the static scan passes, and the LLM scan is complete or
recorded as unavailable. The build page shows each of the four checks separately so an author can
see what is missing. Packaging is refused when the verifier's lint check fails, when the verifier's
self-test fails, and when the catalog's required verifier range excludes the selected verifier
version. Together these gates mean no unvalidated skill content can be packaged or submitted.

## Functional scope

- Check the manifest validity of a build at a commit SHA (FR-068).
- Mark a build Ready at a SHA only when the manifest check, a passing run, a passing static scan
  and a complete-or-unavailable LLM scan all hold (FR-069).
- Show each of the four readiness checks on the build page (FR-070).
- Refuse to package a skill when the verifier's lint check fails (FR-071).
- Refuse to package a skill when the verifier's self-test fails (FR-072).
- Refuse to package a skill when the catalog's required verifier range excludes the selected
  verifier version (FR-073).

**Edge cases:** an LLM scan recorded unavailable counts as satisfied (FR-139); a manifest check
requested for a SHA that no longer exists; the head moving after checks pass (FA-3 clears ready
SHA); an unparseable required-verifier range (fail closed); a flaky lint result; ready evaluated
for a build whose pull request is already open.

**Non-goals:** producing the verdict (FA-10A), running the scans (FA-11 and FA-12), packaging
itself (FA-6 owns the path these gates protect), opening the pull request (FA-15).

## Implementation guidance / dependency order

1. Define a readiness fact model keyed by build SHA, holding the four check outcomes and their
   evidence links.
2. Implement the manifest check at a SHA and the aggregation rule for Ready.
3. Add the build-page view of each of the four checks.
4. Add the packaging preflight: verifier lint, self-test and required-verifier-range checks,
   invoked by FA-6's packaging path.
5. Ensure FA-3's head change invalidates the Ready status, and test the interaction.

**Depends on:** FA-3 (head and ready pointer), FA-6 (packaging path), FA-10A (run verdict), FA-11
(static scan), FA-12 (LLM scan). **Feeds:** FA-15 (submit is enabled only when Ready).

## Goal / Definition of Done

A build is Ready at a SHA only when all four checks hold and the build page shows each one;
packaging is refused on lint failure, self-test failure or an excluded verifier version; and a new
commit clears the Ready status.

## Covered requirements (traceability)

- FR-068 — Check manifest validity at a commit SHA
- FR-069 — Mark Ready only when all four readiness checks hold
- FR-070 — Show each of the four readiness checks
- FR-071 — Refuse packaging when verifier lint fails
- FR-072 — Refuse packaging when verifier self-test fails
- FR-073 — Refuse packaging when the required verifier range excludes the version

## Notes

**Depends on:** FA-3, FA-6, FA-10A, FA-11, FA-12. **Feeds:** FA-15. "Unavailable" is a legitimate
LLM-scan outcome for readiness (FR-139) and must not be treated as a failure here.

---

## EPIC: Run audit trail, retention & usage records  (BSB-52)

**Feature area:** FA-13 · **Release:** MVP · **Labels:** FA-13, MVP

## Description

Behind the run report sits the durable record a reviewer or auditor relies on. This epic records
the Jira changes a run makes, and records each run's cost, token usage and turn count as structured
usage data. It also applies the privacy side of run data: transcripts, logs and results are retained
only for a configured period (three months by default) and can be purged on request. The epic
creates the records that FA-13A renders and FA-14 compares; because purge may remove them, those
epics must treat older runs as potentially unavailable.

## Functional scope

- Record the Jira changes a run makes (FR-140).
- Retain run transcripts, logs and results only for a configured period (NFR-013).
- Allow run transcripts, logs and results to be purged on request (NFR-014).
- Record each run's cost (NFR-015).
- Record each run's token usage (NFR-016).
- Record each run's turn count (NFR-017).
- Default the retention period to three months (NFR-018).

**Edge cases:** the Jira integration being unavailable or the run failing before a change is
recorded (record what is known); purge requested while a run is in flight; the retention boundary
and time zone; a partial purge failure (retryable, never silently reported as complete); the
runtime not reporting cost or usage (record unavailable, not zero); purged data referenced by a
comparison view.

**Non-goals:** displaying these records (FA-13A and FA-14); the run deadline (FA-8); installation
settings UI beyond consuming the operator-managed retention value.

## Implementation guidance / dependency order

1. Add an append-only run record/event store for Jira changes and usage data, written from FA-7's
   execution events.
2. Add cost, token and turn extraction from the runtime result, recording unavailable when absent.
3. Add the retention configuration (installation level, default three months) and a retention
   sweeper.
4. Add the purge operation with an audit of what it removed and a retryable failure path.
5. Expose read access for FA-13A and FA-14, with a clear "purged/unavailable" state.

**Depends on:** FA-5 (Jira integration, to observe changes), FA-6 (run identity) and FA-7
(execution events). **Feeds:** FA-13A (display), FA-14 (comparison), FA-15 (audit links).

## Goal / Definition of Done

Every run has durable records of its Jira changes, cost, token usage and turn count; run data is
retained for the configured period (three months by default) and can be purged on request, with
purges auditable and older records correctly reported as unavailable.

## Covered requirements (traceability)

- FR-140 — Record the Jira changes a run makes
- NFR-013 — Retain transcripts, logs and results only for a configured period
- NFR-014 — Purge transcripts, logs and results on request
- NFR-015 — Each run records its cost
- NFR-016 — Each run records its token usage
- NFR-017 — Each run records its turn count
- NFR-018 — Default retention period is three months

## Notes

**Depends on:** FA-5, FA-6, FA-7. The retention period is an installation-level setting managed by
the operator; the three-month default is the PRD's confirmed value. Purge may make records that
FA-13A and FA-14 expect unavailable.

---

## EPIC: Run results & reporting  (BSB-53)

**Feature area:** FA-13 · **Release:** MVP · **Labels:** FA-13, MVP

## Description

This epic is the run page: the single place that shows everything a reviewer needs to judge one
run. It shows the skill that ran, the input and output branches and the skills commit, the
component versions used, the verdict the agent claimed and the final verdict after verification,
each check result, the diff from the input branch to the run branch, the Jira changes the run made,
the run's turn count, token usage and cost, and a link to the run's trace when tracing is enabled.
Progress and logs live on the same page during execution (FA-7 owns streaming them). The value is
that a catalog reviewer can consume the run report and its evidence without reconstructing the run
from raw logs.

## Functional scope

- Show the skill that ran (FR-094).
- Show the input branch (FR-095) and the output branch (FR-096).
- Show the component versions used (FR-097).
- Show the verdict the agent claimed (FR-098).
- Show each check result (FR-099).
- Show the diff from the input branch to the run branch (FR-100).
- Show the Jira changes the run made (FR-101).
- Show the run's turn count (FR-102).
- Link to the run's trace when tracing is enabled (FR-103).
- Show the skills commit SHA (FR-157).
- Show the final verdict after verification (FR-158).
- Show the run's token usage (FR-159).
- Show the run's cost (FR-160).

**Edge cases:** a very large diff (paginate or truncate with a clear indication); no Jira changes
(show an explicit empty state); tracing disabled (no link); a run still in flight (partial data,
readable while it completes); cost or usage unavailable; records purged under retention (show
unavailable, not zero).

**Non-goals:** live execution streaming (FA-7), history and comparison (FA-14), the underlying
audit/usage records (FA-13B), retention and purge (FA-13B).

## Implementation guidance / dependency order

1. Define a read model that joins the run record, verdict, check results, branch diff and audit
   records; key it by run ID.
2. Add the run-page sections for identity, branches and commit, components and verdicts.
3. Add the check-result list and the branch diff with pagination.
4. Add the audit-backed sections — Jira changes, turn count, token usage and cost — sourced from
   FA-13B records, with explicit unavailable states.
5. Finish with the trace link when tracing is enabled.

**Depends on:** FA-6 (run identity/branches/baseline), FA-7 (metadata), FA-10A (final verdict and
checks), FA-13B (Jira changes, usage, cost, retention state). **Feeds:** FA-15 (linked run report)
and FA-14 (the data this page exposes).

## Goal / Definition of Done

A reviewer opening one run page can see the skill, branches, skills commit, components, claimed and
final verdicts, every check, the branch diff, Jira changes, turn count, token usage, cost and a
trace link when tracing is enabled, with explicit empty and unavailable states.

## Covered requirements (traceability)

- FR-094 — The run page shows the skill that ran
- FR-095 — The run page shows the input branch
- FR-096 — The run page shows the output branch
- FR-097 — The run page shows the component versions
- FR-098 — The run page shows the claimed verdict
- FR-099 — The run page shows each check result
- FR-100 — The run page shows the input-to-run branch diff
- FR-101 — The run page shows the run's Jira changes
- FR-102 — The run page shows the run's turn count
- FR-103 — The run page links to the trace when tracing is enabled
- FR-157 — The run page shows the skills commit SHA
- FR-158 — The run page shows the final verdict
- FR-159 — The run page shows token usage
- FR-160 — The run page shows the run's cost

## Notes

**Depends on:** FA-6, FA-7, FA-10A, FA-13B. **Feeds:** FA-15 and FA-14. FR-101, FR-159 and FR-160
display audit records created in FA-13B (FR-140, NFR-015, NFR-016); FR-102 displays the turn count
recorded under NFR-017.

---

## EPIC: Catalog submission  (BSB-54)

**Feature area:** FA-15 · **Release:** MVP · **Labels:** FA-15, MVP

## Description

This epic turns a Ready build into a reviewed catalog pull request — the product's only outward
write. Submit to catalog is enabled only when the build is Ready at its head SHA. Submitting opens
a pull request from the build branch to the catalog's main branch using the author's own
source-control identity, with a description that lists the readiness checks at the head SHA and
links to the run report and the scan reports. The builder records the pull-request URL and state
on the build, and the build state moves through open, submitted, merged or abandoned. A save on a
submitted build clears its readiness. The builder never writes directly to the platform catalog,
platform projects or project skills; the catalog changes only when a human merges the pull
request.

## Functional scope

- Enable Submit to catalog only when the build is Ready at the head SHA (FR-107).
- Open a catalog pull request from the build branch to the catalog's main branch using the
  author's own source-control identity (FR-108).
- List the readiness checks at the head SHA in the pull-request description (FR-109).
- Link the run report (FR-110) and the scan reports (FR-111) in the description.
- Record the pull-request URL on the build (FR-112).
- Move the build state through open, submitted, merged or abandoned (FR-113).
- Clear readiness when a submitted build is saved (FR-114).
- Never write directly to the platform catalog, platform projects or project skills (FR-115).
- Record the pull-request state on the build (FR-161).

**Edge cases:** pull-request creation failing on authentication or a branch conflict; the build
branch deleted before submission; a pull request closed without merging (abandoned); a save after
merge (new readiness cycle); duplicate submit attempts; catalog `main` moving while the build
branch is behind (surface a rebase need, do not auto-merge).

**Non-goals:** merging the pull request; catalog review tooling; any direct catalog write; using a
project integration credential instead of the author's identity.

## Implementation guidance / dependency order

1. Add the submission precondition: Ready at head SHA from FA-10B, with a clear disabled reason.
2. Implement pull-request creation through the source-control provider using the author's own
   identity, and record the URL immediately.
3. Build the description from readiness evidence, the run report link and scan report links.
4. Add the build state machine and consume pull-request state (webhook or poll) to move between
   submitted, merged and abandoned.
5. Wire FA-3's save path so a save on a submitted build clears readiness, and assert no direct
   catalog write path exists.

**Depends on:** FA-3 (head/ready), FA-10B (Ready gate and evidence), FA-13A (run report link),
FA-11 and FA-12 (scan reports). **External prerequisites:** the catalog repository, its review
flow and the author's source-control identity.

## Goal / Definition of Done

Submit is available only for a Ready build; submitting opens a catalog pull request with the
readiness checks and report links, using the author's identity; the URL and state are recorded and
the build state tracks the pull request; a save clears readiness; and the builder never writes to
the catalog directly.

## Covered requirements (traceability)

- FR-107 — Submit enabled only when Ready at the head SHA
- FR-108 — Open a catalog pull request with the author's own identity
- FR-109 — Description lists readiness checks at the head SHA
- FR-110 — Description links to the run report
- FR-111 — Description links to the scan reports
- FR-112 — Record the pull-request URL on the build
- FR-113 — Build state open, submitted, merged or abandoned
- FR-114 — A save on a submitted build clears readiness
- FR-115 — Never write directly to the catalog, platform projects or project skills
- FR-161 — Record the pull-request state on the build

## Notes

**Depends on:** FA-3, FA-10B, FA-11, FA-12, FA-13A. **External prerequisites:** the catalog
repository and review flow. This is the only epic permitted an outward write, and it is limited to
opening a pull request.

---

## EPIC: Command line & suites  (BSB-55)

**Feature area:** FA-16 · **Release:** mixed · **Labels:** FA-16, mixed

## Description

Not every run needs the web interface. This epic gives authors a command line that starts a test
run without the interface, runs a static-only security scan without a test run, and runs a full
security scan without a test run — the MVP slice. The Later slice adds named suites: an author
saves a suite whose entries name a skill, input branch, context and expectations, runs the suite,
schedules it for nightly execution, and the builder records each scheduled run's result. The CLI
must use the same run-start, packaging and scan services as the web interface so outcomes and
gates cannot diverge; suites turn repeated regression checks into a repeatable batch.

## Functional scope

- Start a test run from the command line without the web interface (FR-116, MVP).
- Run a static-only security scan from the command line without a test run (FR-117, MVP).
- Run a full security scan from the command line without a test run (FR-118, MVP).
- Save a named suite of runs (FR-119, Later).
- Have a suite entry name a skill, input branch, context and expectations (FR-120, Later).
- Run a saved suite (FR-121, Later).
- Schedule a saved suite for nightly execution (FR-122, Later).
- Record each scheduled run's result (FR-123, Later).

**Edge cases:** non-Web authentication and token handling without leaking credentials; machine-
readable output and meaningful exit codes; one suite entry failing while others continue; the
scheduled window being missed (catch-up or skip, stated explicitly); overlapping scheduled runs;
secrets supplied through the environment; a CLI request that duplicates an in-flight run.

**Non-goals:** workflow orchestration with gates and routing (explicitly out of scope); a second
implementation of run/scan logic.

## Implementation guidance / dependency order

1. Build the CLI transport and authentication over the existing run-start and scan services; do
   not fork their logic.
2. Add the three MVP commands — run, static-only scan, full scan — with stable output and exit
   codes.
3. Then, in the Later slice, add suite definition persistence and the suite entry schema.
4. Add the suite runner, then the nightly scheduler and per-run result recording.

**Depends on:** FA-4 (membership), FA-5 (integrations), FA-6 (run setup), FA-7 (execution), FA-11
and FA-12 (scans). **Feeds:** no epic; suites consume the same run path.

## Goal / Definition of Done

MVP: an author can start a test run and start static-only and full scans from the command line
with the same gates and outcomes as the web interface. Later: an author can save, run and schedule
a named suite, and each scheduled run's result is recorded.

## Covered requirements (traceability)

- FR-116 — The command line starts a test run without the interface (MVP)
- FR-117 — The command line runs a static-only scan without a test run (MVP)
- FR-118 — The command line runs a full scan without a test run (MVP)
- FR-119 — An author saves a named suite of runs (Later)
- FR-120 — A suite entry names a skill, input branch, context and expectations (Later)
- FR-121 — An author runs a saved suite (Later)
- FR-122 — A saved suite can be scheduled nightly (Later)
- FR-123 — The builder records each scheduled run's result (Later)

## MVP subset (if release = mixed)

MVP: FR-116, FR-117, FR-118. Later: FR-119, FR-120, FR-121, FR-122, FR-123.

## Notes

**Depends on:** FA-4, FA-5, FA-6, FA-7, FA-11, FA-12. The builder runs one skill per run; this epic
does not orchestrate workflows, gates or routing.

---

## EPIC: Accessibility conformance  (BSB-56)

**Feature area:** FA-17 · **Release:** MVP · **Labels:** FA-17, MVP

## Description

Every authoring surface must be usable with a keyboard and assistive technology, not only with a
mouse and sight. This epic establishes the shared accessible primitives the whole builder uses —
keyboard-operable controls with visible focus, status components with a programmatic name, role and
state, form fields that expose label, instructions and error, and live announcements for run
progress and readiness changes — and then verifies every web surface against them. Status must
never be conveyed by colour alone, text and status colours must meet WCAG 2.1 AA contrast in
normal, hover and focus states, every surface must reflow to a 320 CSS-pixel viewport without
two-dimensional scrolling, and automated accessibility checks must run in continuous verification.
This is an added scope assumption in the PRD (the ADR is silent on accessibility), but it is an
MVP requirement for every builder surface.

## Functional scope

- Make every interactive control operable with a keyboard (FR-130).
- Give every interactive control a visible focus indicator (FR-131).
- Expose a programmatic name, role and state on every custom status component (FR-132).
- Expose every form field's label, instructions and error message to assistive technology
  (FR-133).
- Announce run progress and readiness changes to assistive technology (FR-134).
- Never convey readiness or verdict status by colour alone (FR-135).
- Meet WCAG 2.1 AA contrast for text and status colours in normal and hover or focus states
  (FR-136).
- Run automated accessibility checks in continuous verification (FR-137).
- Reflow every builder web surface to a 320 CSS-pixel viewport without two-dimensional scrolling
  (NFR-012).

**Edge cases:** custom status badges and progress widgets; live-region announcements that
duplicate or drop on fast updates; focus trapping in modals and drawers; dynamic server-rendered
HTML re-rendered by navigation; colour combinations in dark/light themes if both exist; error
messages appearing after submit; keyboard-only completion of every workflow.

**Non-goals:** native mobile applications (the scope is web surfaces); WCAG 2.1 AAA; accessibility
of external systems the builder links to.

## Implementation guidance / dependency order

1. Deliver the shared accessible primitives first — status badge, form field, focus styles and a
   live-region helper — so later epics build surfaces from them rather than retrofitting.
2. Add the automated accessibility check to continuous verification (FR-137) early, so every
   subsequent epic is gated by it.
3. Add keyboard and focus audits of each surface as it lands, starting with access and build
   creation.
4. Add announcement behavior for run progress and readiness as FA-7/FA-10B surfaces land.
5. Finish with contrast and 320-pixel reflow audits across every surface, and record the audit in
   the report linked from the catalog pull request.

**Depends on:** all web-surface epics (FA-1, FA-2A, FA-2B, FA-3, FA-4, FA-5, FA-6, FA-7, FA-8,
FA-10B, FA-13A, FA-15, FA-16 surfaces) for the final audit, but its primitives and automated check
must land before the first surface to avoid retrofitting. **Feeds:** the accessibility evidence
used at catalog review.

## Goal / Definition of Done

Every builder web surface can be operated by keyboard with visible focus and assistive-technology
names, roles, states, labels, errors and announcements; status is never colour-only; contrast meets
WCAG 2.1 AA; each surface reflows to 320 CSS pixels; and automated accessibility checks gate
continuous verification with zero critical findings.

## Covered requirements (traceability)

- FR-130 — Every interactive control is keyboard operable
- FR-131 — Every interactive control shows visible focus
- FR-132 — Custom status components expose name, role and state
- FR-133 — Form fields expose label, instructions and error
- FR-134 — Run progress and readiness changes are announced
- FR-135 — Readiness and verdict are never colour-only
- FR-136 — Text and status colours meet WCAG 2.1 AA contrast
- FR-137 — Automated accessibility checks run in continuous verification
- NFR-012 — Every web surface reflows to 320 CSS pixels

## Notes

**Cross-cutting.** Depends on every web-surface epic for completion, but its shared primitives and
CI check should be delivered first (alongside FA-1/FA-2A). Accessibility is an added PRD assumption
(§8) and MVP scope; G6 and NFR-012 carry the target.

---

## EPIC: Jira fixture seeding  (BSB-57)

**Feature area:** FA-9 · **Release:** Later · **Labels:** FA-9, Later

## Description

Deferred from the first release. Skills that change Jira need realistic tracker data that does not
pollute a real project. This epic seeds Jira issues for a run from a fixture file into the test
project's configured Jira project, marking every seeded issue with the run's ID; it replaces
fixture aliases in the skill's inputs with the created issue keys, records the Jira state after the
run so fixture assertions can be checked, and cleans up the issues it seeded when the run ends.
Cleanup deletes only issues marked with that run's ID; a nightly sweep removes any seeded issue
that carries a run marker but outlived its run. The chosen model is one shared Jira project with a
per-run marker, not a fresh project per run, so a human-created issue is never deleted.

## Functional scope

- Seed Jira issues for a run from a fixture file into the project's configured Jira project, marked
  with the run's ID (FR-058).
- Replace fixture aliases with the created issue keys (FR-059).
- Record the Jira state after the run for fixture assertions (FR-060).
- Clean up seeded issues when the run ends, deleting only issues marked with that run's ID (FR-061).
- Run a nightly sweep that removes seeded issues carrying a run marker (FR-062).

**Edge cases:** partial seeding failure (clean up what was created); alias collisions between
fixtures; a human-created issue that happens to share a title (never delete — only the marker
counts); Jira rate limits; a missing or malformed run marker; the nightly sweep overlapping a live
run (skip issues whose run is not terminal); the configured Jira project changing mid-run.

**Non-goals:** a fresh Jira project per run (rejected in favour of one shared project with a
marker); deleting any issue without the run marker; fixture authoring tooling beyond the file
format.

## Implementation guidance / dependency order

1. Define the fixture file format, the run marker and the alias map first; these are the contract
   cleanup and assertions rely on.
2. Add the seeding service at run start, after FA-6 has resolved the run's Jira integration.
3. Add alias substitution into the run inputs and record the post-run Jira state.
4. Add cleanup on the run's terminal event, scoped strictly by the run marker.
5. Finish with the nightly sweep, treating non-terminal runs as ineligible.

**Depends on:** FA-5 (Jira integration and project configuration), FA-6 (run identity and setup),
FA-7 (run lifecycle events for cleanup). **Later release:** not a prerequisite for the MVP.

## Goal / Definition of Done

A run can seed Jira issues from a fixture with aliases resolved, have its post-run Jira state
recorded for assertions, and clean up exactly the issues it marked with its run ID; a nightly sweep
removes any leftover marked issues, and no unmarked issue is ever deleted.

## Covered requirements (traceability)

- FR-058 — Seed Jira issues from a fixture, marked with the run ID
- FR-059 — Replace fixture aliases with created issue keys
- FR-060 — Record the Jira state after the run for assertions
- FR-061 — Clean up only issues marked with the run ID
- FR-062 — A nightly sweep removes leftover marked issues

## Notes

**Depends on:** FA-5, FA-6, FA-7. **Later release.** The shared-project-plus-marker model is a PRD
decision (§8, Jira isolation); it is what makes deleting only marked issues safe.

---

## EPIC: Skill history & run comparison  (BSB-58)

**Feature area:** FA-14 · **Release:** Later · **Labels:** FA-14, Later

## Description

Deferred from the first release. Once a skill has run many times, an author needs to see how it has
behaved over time. This epic lists every run of a skill with its commit SHA, input branch, verdict
and checks, and provides a compare view that shows two runs side by side and highlights the checks
that flipped between them. The value is diagnosing a regression or confirming an improvement across
iterations of the same skill, rather than reading one run at a time. It reads the records created
by FA-13A and FA-13B and must show purged runs as unavailable rather than silently omitting them.

## Functional scope

- List every run of a skill with its commit SHA, input branch, verdict and checks (FR-104).
- Show two runs side by side in a compare view (FR-105).
- Highlight checks that flipped between the two compared runs (FR-106).

**Edge cases:** a long history (paginate); runs whose records were purged under retention (show
unavailable); comparing two identical runs (no flips); comparing runs of different skills
(disallow); a run still in flight; runs from before a check was introduced (treat as unknown, not
flipped).

**Non-goals:** re-running from history (FA-8 owns re-run), starting a run (FA-6), nightly suites
(FA-16), retention and purge (FA-13B).

## Implementation guidance / dependency order

1. Build the per-skill run index from the run records, with pagination and a purged/unavailable
   state.
2. Add the history view with commit SHA, input branch, verdict and checks per row.
3. Add the two-run selection and side-by-side comparison view.
4. Compute the flipped-check set from the two runs' check results, treating unknown as unknown.

**Depends on:** FA-13A (report data), FA-13B (records and retention state), FA-10A (check results).
**Later release:** not a prerequisite for the MVP.

## Goal / Definition of Done

An author can see every run of a skill with its commit, input branch, verdict and checks, select two
runs, and see them side by side with the checks that flipped highlighted, with purged data shown as
unavailable.

## Covered requirements (traceability)

- FR-104 — Skill history lists every run with commit, input branch, verdict and checks
- FR-105 — Compare view shows two runs side by side
- FR-106 — Compare view highlights checks that flipped

## Notes

**Depends on:** FA-10A, FA-13A, FA-13B. **Later release.** Retention (NFR-013) can remove older
runs; the view must present that explicitly.

---

*Generated by `sdlc-plan-epics-create`. Coverage: all 165 FRs and 19 NFRs mapped to exactly one epic.
Next steps: `sdlc-tracker-sync` publishes the epics to Jira, then `sdlc-plan-stories-write` runs for
each epic through the planning fan-out.*
