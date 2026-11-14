# Epics — decomposed from the SkillBuilder PRD

**Source:** `docs/product/PRD.md` · **Epics:** 17 · **Coverage:** 123 functional and 15 non-functional requirements, each mapped exactly once.

> **Jira source check:** the Atlassian site configured for this repository returns no issue named
> `SkillBuilder`, no issues in the `BSB` project, and no issue whose text contains "builder". This
> matches the constraint recorded in PRD §8, so the decomposition below uses the repository PRD as
> the source of truth. If a separate Jira description is produced later, reconcile it against this
> plan before publishing.
>
> Draft keys end in `-PENDING`; `sdlc-tracker-sync` replaces them with the real Jira keys after
> approval. `project_key` is left as `PENDING` because no target Jira project was named for this
> run; the publishing step must stop and ask for one rather than guess.

---

## EPIC: Access & identity
**Draft key:** `FA-1-PENDING` · **Feature area:** FA-1 · **Release:** MVP · **Labels:** FA-1, MVP

### Description
The builder is an internal tool that spends model tokens, can reach external Jira and GitHub
systems, and can open pull requests against the catalog, so it must be reachable only by people the
platform already trusts. This epic establishes the entry boundary for every authoring surface: an
anonymous visitor is stopped before an authoring page loads, a user signs in with the platform's
existing identity-provider credentials, and every request is checked against current membership of
the external `skill-builders` group. On first successful sign-in the builder creates its own local
user record keyed to the identity-provider subject, giving later epics a stable actor to credit for
builds, projects, runs and submissions. Platform administrators continue to manage group membership
outside the builder; this epic consumes that decision rather than offering user administration.

### Functional scope
- Reject unauthenticated visitors from every authoring page before any builder data is shown.
- Sign users in through the existing platform identity provider; do not introduce a second
  credential store.
- Admit a signed-in user to authoring features only while that user is a current member of the
  `skill-builders` group.
- Evaluate group membership on every request, so removing a user from the group takes effect on
  their next request rather than at the next sign-in.
- Create a local user record on first successful sign-in, linked to the identity-provider subject,
  and reuse it on later sign-ins.
- Return the same rejection behavior for unauthenticated and unauthorized callers across UI pages
  and API endpoints.
- Non-goals: user administration, group management, invitations, password reset and role
  definitions inside the builder; those remain with the platform and its administrators.

### Implementation guidance / dependency order
- Start with the session model and a single request-level authentication middleware, then add a
  route guard that covers every authoring page and API route by default; deny-by-default avoids
  protecting pages one at a time.
- Add the `skill-builders` group lookup behind the middleware next. Resolve membership per request
  and cache only for the lifetime of that request.
- Build the local user upsert on first successful sign-in after authentication is stable, and make
  it idempotent on the identity-provider subject.
- Finish with the signed-out and unauthorized experiences and with tests that remove a user from
  the group mid-session. The identity provider and the group itself are external prerequisites
  supplied by the platform.

### Goal / Definition of Done
An unauthenticated visitor cannot open any authoring page or call an authoring API; an authorized
member can sign in and gets exactly one local user record; a user removed from the `skill-builders`
group is rejected on their next request without signing in again.

### Covered requirements (traceability)
- FR-001 — unauthenticated visitors cannot open authoring pages
- FR-002 — sign in with existing platform identity-provider credentials
- FR-003 — authoring access only for current `skill-builders` members
- FR-004 — group membership evaluated on every request
- FR-005 — local user record created on first successful sign-in
- NFR-002 — every unauthenticated request is rejected
- NFR-003 — every request from a non-member is rejected

### Notes
This is the foundation epic: every other epic assumes an authenticated local user and a project
membership model supplied by FA-1 and FA-3A. The identity provider and the `skill-builders` group
are external; the builder has no user-administration screen.

---

## EPIC: Build creation & cloning
**Draft key:** `FA-2A-PENDING` · **Feature area:** FA-2 · **Release:** MVP · **Labels:** FA-2, MVP

### Description
A build is the author's working copy of one skill. This epic lets an author start a build either
from scratch or from an existing catalog skill, and gives every build an isolated branch so
experiments never touch main or the source skill. Creating a build records the skill name and a
one-line description, creates a branch from the current main branch, and scaffolds a skill folder
containing `SKILL.md` with frontmatter, a `verify.yaml` stub, and the `references`, `templates` and
`examples` folders. The scaffold is deliberately valid: it must pass the catalog's static manifest
checks without hand editing, so the author starts from a working shape. Cloning copies an existing
catalog skill into a new build and rewrites only the copied frontmatter name, leaving the source
directory untouched. Build names are validated both for format and for collisions on main and among
open builds, which keeps branches and later catalog submissions unambiguous.

### Functional scope
- Create a build from a skill name and a one-line description.
- Create the build branch from the current main branch at creation time.
- Scaffold the skill folder with `SKILL.md` frontmatter, a `verify.yaml` stub, and the `references`,
  `templates` and `examples` folders.
- Ensure a newly scaffolded skill passes the catalog's static manifest checks without manual edits.
- Clone an existing catalog skill into a new build under a new name.
- Copy the full skill folder into the new build and rewrite the name in the copied frontmatter.
- Leave the source skill's files byte-for-byte unchanged during a clone.
- Reject a build name that already exists on the main branch, that another open build is using, or
  that does not follow the required `sdlc` prefix, area segment and action segment pattern.
- Inputs: skill name, one-line description, and for a clone the source catalog skill.
- Outputs: a build record, a build branch, and a scaffolded or copied skill folder.
- Non-goals: editing the skill after creation (owned by the build-save story in FA-2B), versioning
  inside the builder, and direct writes to the catalog.

### Implementation guidance / dependency order
- Define the build and skill-name model and the validation rules first, because every later step
  depends on an unambiguous, unique name.
- Add branch creation and the scaffold template next; keep the template in one place so the
  manifest check and the scaffold cannot drift apart.
- Build clone after the scaffold path works: reuse the branch and folder machinery, then add the
  frontmatter rewrite and an explicit source-immutability check.
- Wire the catalog static manifest checker last, and use it in tests for both fresh scaffolds and
  cloned skills. This epic depends on FA-1 for the acting user and on source-control access for
  branch creation.

### Goal / Definition of Done
An author can create a build whose branch and scaffold pass the catalog manifest checks with no
manual edits, and can clone a catalog skill into a new build without changing the source skill.
Duplicate names, names already used by an open build, and names that break the required pattern are
rejected with a clear message.

### Covered requirements (traceability)
- FR-006 — create a build from a skill name and one-line description
- FR-007 — create the build branch from current main
- FR-008 — scaffold the skill folder
- FR-009 — scaffold contains SKILL.md frontmatter, verify.yaml stub and standard folders
- FR-010 — new scaffold passes catalog static manifest checks unedited
- FR-011 — clone an existing catalog skill under a new name
- FR-012 — cloning copies the skill folder
- FR-013 — cloning rewrites the name in the copied frontmatter
- FR-014 — cloning leaves the source skill's files unchanged
- FR-015 — reject a name already present on main
- FR-016 — reject a name used by another open build
- FR-017 — reject a name that breaks the sdlc prefix, area segment and action segment pattern

### Notes
Depends on FA-1 for the author identity. Produces the build and branch that FA-2B records commits
against and that FA-4A resolves when preparing a run. The catalog manifest checker is an external
component consumed, not modified, by the builder.

---

## EPIC: Build state & readiness tracking
**Draft key:** `FA-2B-PENDING` · **Feature area:** FA-2 · **Release:** MVP · **Labels:** FA-2, MVP

### Description
Once a build exists, the author needs a trustworthy answer to two questions: what exactly is the
current version, and is that version ready. This epic makes every save a commit on the build branch
and projects the latest commit SHA as the build head. The build page exposes that head SHA and the
current readiness status so an author can see the exact revision being discussed. The critical rule
is invalidation: a new commit means any previously recorded ready SHA no longer describes the build,
so it is cleared immediately. This epic owns the persistence, display and invalidation of that
state; the checks that decide readiness are implemented in FA-5, but the build's head and ready
fields are the contract every later epic reads.

### Functional scope
- Create a commit on the build branch for each save.
- Record the latest commit SHA on the build branch as the build head.
- Show the build's current head SHA on the build page.
- Show the build's readiness status on the build page.
- Clear the build's previously recorded ready SHA whenever a new commit lands on the build.
- Inputs: saved skill content from the author and the current build branch.
- Outputs: a commit, an updated head SHA, a readiness status and an invalidated ready SHA.
- Non-goals: computing the four readiness checks (FA-5), displaying run results (FA-7A), and
  submitting to the catalog (FA-8).

### Implementation guidance / dependency order
- Implement the save-to-commit path first, because head SHA and invalidation both derive from it.
- Add the head-SHA projection and the build page display next; read the SHA from the branch rather
  than trusting a cached value at render time.
- Add the ready-SHA field and the invalidation rule together, then cover the ordering case where a
  save and a readiness decision race: a commit that lands after a readiness check must win.
- This epic depends on FA-2A for branches and builds, and exposes the head SHA that FA-5 and FA-8
  consume.

### Goal / Definition of Done
Every save produces a commit, the build page always shows the true head SHA, and a new commit
clears the ready status so no build can be submitted against a stale verified revision.

### Covered requirements (traceability)
- FR-018 — each save creates a commit on the build branch
- FR-019 — latest commit SHA recorded as the build head
- FR-020 — build page shows the current head SHA
- FR-021 — build page shows the readiness status
- FR-022 — a new commit clears the previously recorded ready SHA

### Notes
Depends on FA-2A. The readiness status shown here is populated by FA-5; this epic guarantees the
value is tied to the head SHA and is invalidated whenever the head moves.

---

## EPIC: Test projects & membership
**Draft key:** `FA-3A-PENDING` · **Feature area:** FA-3 · **Release:** MVP · **Labels:** FA-3, MVP

### Description
Test projects give authors a shared container for runs, members and integration settings. This epic
defines the project and its access model: a signed-in author creates a project and becomes its
owner, the owner adds and removes members, and members can start runs in the project. It also fixes
the first ownership rule that other epics rely on: only the project owner may change integrations,
even though the integration settings themselves are built in FA-3B. The model exists so that a
small team can share a curated test environment without giving every author the ability to redirect
its Jira or GitHub credentials. User administration stays outside the builder; membership here is
limited to projects the builder owns.

### Functional scope
- Allow a signed-in author to create a test project.
- Record the creator as the project owner.
- Allow the owner to add a project member and remove a project member.
- Allow a project member to start a test run in the project.
- Restrict integration changes to the project owner.
- Inputs: project name and the acting local user; member identities for add and remove.
- Outputs: a project with an owner and a membership list that later epics authorize against.
- Non-goals: organization-wide roles, user administration, per-run sharing and transfer of
  ownership not required by the PRD.

### Implementation guidance / dependency order
- Build the project model and owner assignment first, then the membership relation.
- Add a single project-authorization helper that answers owner, member or neither; use it from
  every project-scoped action rather than reimplementing checks.
- Add the integration-change guard once the helper exists, and have FA-3B call the same helper.
- Authorize starting a run through the same helper in FA-4A. This epic depends on FA-1 for the
  local user identity.

### Goal / Definition of Done
An author can create a project and becomes its owner; the owner can add and remove members; a
member can start a run in the project; a non-member or a non-owner cannot change integrations.

### Covered requirements (traceability)
- FR-023 — a signed-in author creates a test project
- FR-024 — the creator is recorded as project owner
- FR-025 — the owner adds a project member
- FR-026 — the owner removes a project member
- FR-027 — a project member can start a test run
- FR-028 — only the project owner can change integrations

### Notes
Depends on FA-1. Supplies the project context and ownership rule used by FA-3B and FA-4. The
integration configuration itself is delivered by FA-3B; this epic delivers the permission boundary.

---

## EPIC: Integrations & credentials
**Draft key:** `FA-3B-PENDING` · **Feature area:** FA-3 · **Release:** MVP · **Labels:** FA-3, MVP

### Description
A test project needs to reach Jira, GitHub and a model provider, but the builder must never become
a credential store. This epic lets the project owner configure three integrations — a Jira site URL
with a project or template, a GitHub sandbox repository with a base branch, and an AI model profile
with a vendor, base URL and tier-to-model mapping — while keeping the credential values in an
external secret store and referring to them only by reference. The owner can verify credentials and
see when each integration was last verified. The UI never displays a credential value, logs and run
results never contain one, and only test-purpose credentials may be used. The epic also warns when
a GitHub integration points at a repository that a platform project already uses, so a test run
cannot quietly disturb production-adjacent content. These settings become the inputs every run and
scan depend on.

### Functional scope
- Configure a Jira integration with a site URL and a Jira project or template.
- Configure a GitHub integration with a sandbox repository and a base branch.
- Configure an AI model profile with a vendor, a base URL and a tier-to-model mapping.
- Never store an integration credential value in the builder's own records; keep a reference to the
  external secret instead.
- Verify an integration's credentials on demand and record when they were last verified.
- Warn when a GitHub integration points to a repository that a platform project also uses.
- Never display a credential value in the interface.
- Restrict all changes to the project owner, using the FA-3A authorization helper.
- Inputs: integration type, non-secret settings, credential references, and the verification call
  to the external system.
- Outputs: verified integration configurations that runs and scans can resolve at execution time.
- Non-goals: credential issuance, rotation policy, production credentials, and platform project
  management; the builder only references external test-purpose secrets.

### Implementation guidance / dependency order
- Start with the integration configuration model and a credential-reference abstraction, so no
  code path ever needs the secret value itself.
- Add the Jira, GitHub and model adapters next, each supporting a verification call and a
  last-verified timestamp.
- Add the repository-overlap warning against the platform's project inventory after the GitHub
  adapter can resolve a repository.
- Finish with UI redaction and log/result filtering tests. This epic depends on FA-3A for ownership
  and on external secret storage and test-purpose credentials.

### Goal / Definition of Done
A project owner can configure and successfully verify Jira, GitHub and model integrations; no
credential value is stored in builder records, shown in the interface or present in logs or run
results; the owner is warned when a sandbox repository overlaps a platform project.

### Covered requirements (traceability)
- FR-029 — configure Jira integration with site URL and project or template
- FR-030 — configure GitHub integration with sandbox repository and base branch
- FR-031 — configure AI model profile with vendor, base URL and tier-to-model mapping
- FR-032 — never store an integration credential value in builder records
- FR-033 — verify an integration's credentials
- FR-034 — record when credentials were last verified
- FR-035 — warn when a GitHub repository is also used by a platform project
- FR-036 — never display a credential value in the interface
- NFR-004 — credential values never appear in logs or run results
- NFR-006 — runs use only test-purpose Jira, source-control and model credentials

### Notes
Depends on FA-3A for the owner-only permission model. Supplies the Jira, GitHub and model settings
used by FA-4A, FA-6B, FA-8 and FA-9. Credential values live outside the builder; this epic is
responsible for keeping references opaque.

---

## EPIC: Run setup & skill packaging
**Draft key:** `FA-4A-PENDING` · **Feature area:** FA-4 · **Release:** MVP · **Labels:** FA-4, MVP

### Description
A run starts with a precise question: which skill content, which input state, which model profile
and tier, and which optional workflow-step context. This epic turns that selection into a prepared,
reproducible execution. The author picks a skills branch and an input branch, optionally supplies a
workflow-step context, and chooses a model profile and tier. The builder resolves the skills branch
to a concrete commit SHA, packages the skill at that commit, and reuses an already-produced package
for the same commit instead of rebuilding it. It then creates a run branch from the input branch
head, records that head as the baseline SHA, and guarantees the input branch is never written to
during the run. Preparing the same skills commit twice must produce an identical package. These
artifacts are what execution, verification and result reporting later consume.

### Functional scope
- Start a run by selecting a skills branch, an input branch, an optional workflow-step context, a
  model profile and a tier.
- Resolve the selected skills branch to a commit SHA at run start.
- Package the skill at that commit for execution.
- Reuse a package already produced for the same skills commit instead of producing it again.
- Create the run branch from the input branch head.
- Record the input branch head as the run's baseline SHA.
- Never write to the input branch during a run.
- Complete the non-model setup for one run within 60 seconds for a skill of up to 5 MB.
- Produce an identical package when the same skills commit is prepared again.
- Inputs: skills branch, input branch, optional workflow-step context, model profile and tier.
- Outputs: resolved skills commit SHA, skill package, run branch and baseline SHA.
- Non-goals: executing the skill (FA-4B), verification (FA-5), and fixture seeding (FA-4D).

### Implementation guidance / dependency order
- Define the run-request model and resolve both branches to concrete SHAs first; every later step
  should operate on a SHA, never on a moving branch name.
- Build the packaging step and a content-addressed package cache keyed by the skills commit next;
  the cache is what makes the 60-second setup and deterministic reuse achievable.
- Add run-branch creation and baseline recording after packaging works, and enforce the input
  branch as read-only in the repository adapter rather than by convention.
- This epic depends on FA-2A for build branches and FA-3B for GitHub integration; its outputs feed
  FA-4B, FA-4C and FA-5. NFR-009 and NFR-001 should be verified here, not deferred to execution.

### Goal / Definition of Done
An author can start a run from a selected skills commit and input branch, the setup completes within
60 seconds for a 5 MB skill, the same skills commit always yields the same package, and the run
branch and baseline SHA are recorded while the input branch remains untouched.

### Covered requirements (traceability)
- FR-037 — start a run with skills branch, input branch, optional context, model profile and tier
- FR-038 — resolve the skills branch to a commit SHA
- FR-039 — package the skill at that commit
- FR-040 — reuse an existing package for the same skills commit
- FR-041 — create the run branch from the input branch head
- FR-042 — record the input branch head as the run's baseline SHA
- FR-043 — never write to the input branch during a run
- NFR-001 — non-model setup completes within 60 seconds for a skill up to 5 MB
- NFR-009 — preparing the same skills commit twice produces an identical package

### Notes
Depends on FA-2A and FA-3B. Consumed by FA-4B for execution, FA-4C for start guards, and FA-5 for
verification inputs. Branch names are resolved once at setup; later phases must not re-resolve them
to a moving head.

---

## EPIC: Run execution & outcome capture
**Draft key:** `FA-4B-PENDING` · **Feature area:** FA-4 · **Release:** MVP · **Labels:** FA-4, MVP

### Description
This epic actually runs one packaged skill in the same runtime the platform uses, rather than a
builder-specific imitation. While it runs, the author can watch progress and logs; when it exits,
the outcome is classified with the platform engine's own rules so the builder's judgement matches
the platform's. Each run records the exact execution-component and verifier versions it used, the
model profile and tier, and a trace marker that identifies the work as a test-environment run. That
metadata is what makes a result reproducible and comparable later. The epic deliberately stops at
capturing the agent's outcome: post-run verification, readiness, and user-facing result pages are
separate epics, each consuming the run record this epic produces.

### Functional scope
- Execute one skill in the same runtime as the platform.
- Show run progress while the run executes.
- Show the run's logs while the run executes.
- Classify the run outcome using the same rules as the platform engine.
- Record the exact execution-component and verifier versions used on each run.
- Record the model profile and tier used on each run.
- Mark every run's trace so it is identifiable as a test-environment run.
- Inputs: the prepared package, run branch, baseline SHA and model selection from FA-4A.
- Outputs: an executed run with streamed progress and logs, a classified terminal outcome, and
  recorded component, verifier, model, tier and trace metadata.
- Non-goals: enforcing caps or start guards (FA-4C), running the verifier (FA-5), and rendering
  the run page (FA-7A).

### Implementation guidance / dependency order
- Integrate the platform runtime adapter and invoke the packaged skill first, keeping the runtime
  version selection explicit.
- Add progress and log streaming next, from the same event stream the outcome classifier will read,
  so the UI and the verdict cannot disagree about what happened.
- Port the platform's outcome-classification rules rather than approximating them, and pin them to
  the recorded engine version.
- Capture component, verifier, model, tier and trace metadata at start and completion, and expose
  the run record to FA-5 and FA-7A. This epic depends on FA-4A's package and on external runtime
  and verifier releases.

### Goal / Definition of Done
A packaged skill executes in the platform's runtime, the author sees live progress and logs, the
terminal outcome matches what the platform engine would classify, and the run record identifies the
exact components, verifier, model, tier and test-environment trace used.

### Covered requirements (traceability)
- FR-044 — run the skill in the same runtime as the platform
- FR-045 — show run progress while the run executes
- FR-046 — show run logs while the run executes
- FR-047 — classify the run outcome using platform engine rules
- FR-048 — record the exact execution-component and verifier versions
- FR-049 — record the model profile and tier used
- NFR-011 — every run's trace identifies it as a test-environment run

### Notes
Depends on FA-4A and the external runtime and verifier releases. Produces the run record consumed
by FA-4C, FA-5, FA-7A and FA-8. Runtime and component versions are recorded, never modified.

---

## EPIC: Static security scanning
**Draft key:** `FA-6A-PENDING` · **Feature area:** FA-6 · **Release:** MVP · **Labels:** FA-6, MVP

### Description
No run may execute skill content that has not passed a static security scan. This epic builds the
static half of the security surface: the scanner runs on the exact skill content about to be used,
has no network access, and reuses a completed result when that content has not changed. Its verdict
is strict — a `DO_NOT_INSTALL` recommendation, any critical finding, or incomplete coverage all mean
"not passing", and accepting a finding elsewhere cannot override that block. The report shows the
score, the recommendation, and each finding's severity, rule, file and line. The builder must
produce the same verdict as the platform for the same content and scanner version. An author can
also start a static-only scan from the skill page without starting a run, and a scan that exceeds
ten minutes fails rather than hanging. This epic owns the scan result that both the run-start gate
and build readiness depend on.

### Functional scope
- Run a static security scan on the exact skill content before every run.
- Reuse a completed static scan result when the skill content is unchanged.
- Record a `DO_NOT_INSTALL` static verdict as not passing.
- Record a static scan with a critical finding as not passing.
- Record a static scan with incomplete coverage as not passing.
- Prevent an accepted finding from overriding a static-scan block.
- Show the score, recommendation and each finding's severity, rule, file and line in the static
  report.
- Produce the same scan verdict as the platform for the same skill content and scanner version.
- Let an author start a static-only security scan from the skill page without starting a run.
- Give a scan no network access.
- Time out a scan after ten minutes and record the timed-out scan as failed.
- Inputs: the exact skill content and content hash, the selected scanner version, and the skill
  page trigger.
- Outputs: a pass or fail verdict, a normalized finding report, and a reusable cached result.
- Non-goals: the model-based scan (FA-6B), modifying scanner output rules, and accepting findings
  inside the builder — acceptance is maintained outside it.

### Implementation guidance / dependency order
- Build the scan runner in a no-network sandbox first, and pass it the content hash so the cache
  key is defined before any UI exists.
- Add the verdict mapping and block rules next, including the "accepted finding cannot override"
  rule; these rules are the contract FA-4C and FA-5 consume.
- Add the finding report projection, then the skill-page static-only trigger.
- Finish with platform-parity tests against a fixed content and scanner-version corpus, and with
  the ten-minute timeout path. This epic depends on an external scanner release and feeds FA-4C,
  FA-5 and FA-9.

### Goal / Definition of Done
Every run is preceded by a static scan of the exact content being run; unchanged content reuses the
previous result; blocked verdicts cannot be overridden; reports show score, recommendation and
per-finding location; a scan times out as failed after ten minutes; and the verdict matches the
platform for the same input and scanner version.

### Covered requirements (traceability)
- FR-076 — run a static scan on the exact skill content before every run
- FR-077 — reuse a completed static scan result when content is unchanged
- FR-078 — a DO_NOT_INSTALL verdict is not passing
- FR-079 — a critical finding is not passing
- FR-080 — incomplete coverage is not passing
- FR-081 — an accepted finding cannot override a static-scan block
- FR-087 — a security scan times out after ten minutes
- FR-088 — a timed-out scan is recorded as failed
- FR-089 — static report shows score, recommendation and finding details
- FR-091 — the scan verdict matches the platform for the same content and scanner version
- FR-092 — start a static-only scan from the skill page without a run
- NFR-005 — a static security scan has no network access

### Notes
Depends on an external scanner release and on FA-2A/FA-2B content resolution. The pass/fail verdict
is a hard prerequisite for FA-4C's run-start gate and one of the four checks aggregated by FA-5.
FR-087 and FR-088 also apply to the model scan in FA-6B; they are owned here as shared scan
infrastructure.

---

## EPIC: LLM security scanning
**Draft key:** `FA-6B-PENDING` · **Feature area:** FA-6 · **Release:** MVP · **Labels:** FA-6, MVP

### Description
The model-based scan looks for risks that static rules cannot express. It is intentionally
constrained: it may start only after the static scan passes for the current skill content, it
receives no credentials other than the model key, and it can reach only the model endpoint. It also
never blocks a run — its findings are advisory to the author and are one of the readiness signals,
not a run-start gate. The report names the model used and each finding's severity, rule, file and
line. An author can trigger a full scan from the skill page, meaning static then model, without
starting a run. This epic consumes the static result from FA-6A and the model profile from FA-3B,
and produces the finding set that readiness and result reporting display.

### Functional scope
- Trigger the LLM security scan only after the static scan passes for the current skill content.
- Give the LLM scan no credentials other than the model key.
- Allow the LLM scan to reach only the model endpoint.
- Never let the LLM scan block a run.
- Show the LLM scan findings to the author.
- Show the model used and each finding's severity, rule, file and line in the LLM report.
- Let an author start a full security scan from the skill page without starting a run.
- Inputs: the skill content, a passing static result, the selected model profile and its key.
- Outputs: an advisory finding set, a report naming the model, and a completion or unavailable
  state suitable for the readiness aggregator.
- Non-goals: static scanning (FA-6A), deciding the run outcome, and blocking a run on model-scan
  findings.

### Implementation guidance / dependency order
- Build the isolated scan runner with an egress allowlist limited to the model endpoint and no
  injected credentials except the model key; verify the isolation before adding the trigger.
- Add the static-pass precondition next, reading the FA-6A verdict for the same content hash.
- Add the report projection and the skill-page full-scan trigger after the runner is constrained.
- Make the non-blocking contract explicit in the run path: LLM findings never alter run start or
  the run's classified outcome. A timed-out or unavailable scan is recorded as such, not as a
  blocking failure. This epic depends on FA-6A and FA-3B.

### Goal / Definition of Done
A model scan cannot start before a static pass on the same content; it runs with only the model key
and only the model endpoint reachable; its findings and model name are visible to the author; it
never blocks a run; and the full-scan action works from the skill page without a run.

### Covered requirements (traceability)
- FR-082 — trigger the LLM scan only after the static scan passes for current content
- FR-083 — the LLM scan receives no credentials other than the model key
- FR-084 — the LLM scan can reach only the model endpoint
- FR-085 — the LLM scan never blocks a run
- FR-086 — LLM scan findings are shown to the author
- FR-090 — LLM report shows the model used and finding details
- FR-093 — start a full security scan from the skill page without a run

### Notes
Depends on FA-6A for the static precondition and FA-3B for the model profile. Readiness in FA-5
treats a completed scan as satisfied and an unavailable scan as recorded, but never blocks a run on
model findings. FR-087 and FR-088 (ten-minute timeout, failed when timed out) are owned by FA-6A and
apply to this scan as well.

---

## EPIC: Run guardrails & re-runs
**Draft key:** `FA-4C-PENDING` · **Feature area:** FA-4 · **Release:** MVP · **Labels:** FA-4, MVP

### Description
An unbounded or unsafe run wastes tokens and can damage the environment, so every run has explicit
limits and preconditions. This epic lets the author set a turn cap and a spend cap, enforces both
while the run executes, and guarantees that every run reaches a terminal state by its configured
deadline. A run that exceeds the deadline is recorded as failed. Before a run starts, the builder
refuses it when the selected execution components are incompatible or when the static scan for the
content to be run did not pass. After a run exists, the author can re-run it with the same inputs
and the latest skills commit, or use its output branch as the input branch of a subsequent run.
These controls sit around FA-4B's execution loop and depend on FA-6A's static verdict.

### Functional scope
- Let the author set a turn cap for a run.
- Stop a run when its turn cap is reached.
- Let the author set a spend cap for a run.
- Stop a run when its spend cap is reached.
- Refuse to start a run when the selected execution components are incompatible.
- Refuse to start a run when the static security scan for the content to be run did not pass.
- Re-run a prior run with the same inputs and the latest skills commit.
- Use a run's output branch as the input branch of a subsequent run.
- Ensure every run reaches a terminal state within its configured deadline.
- Record a run that exceeds its deadline as failed.
- Inputs: caps, component selection, prior run configuration and static verdicts.
- Outputs: stopped or failed terminal states, refused starts with reasons, and new runs that reuse
  prior inputs or outputs.
- Non-goals: changing the runtime's own limits, retry policy beyond re-run, and fixture cleanup.

### Implementation guidance / dependency order
- Add turn and spend accounting to the execution loop first, because both caps read the same event
  stream and must stop the run cleanly.
- Add the deadline guard and the "deadline exceeded is failed" terminal rule next.
- Add the preflight refusals — component incompatibility and the static-scan gate — before exposing
  start in the UI.
- Build re-run and output chaining last, once the run record and terminal states are stable; carry
  the same inputs forward but resolve the skills branch to its latest commit. This epic depends on
  FA-4B execution and FA-6A static scanning.

### Goal / Definition of Done
A run stops cleanly at its turn or spend cap, every run reaches a terminal state within its
deadline, an over-deadline run is failed, incompatible or statically blocked runs cannot start, and
an author can re-run or chain runs as specified.

### Covered requirements (traceability)
- FR-050 — the author sets a turn cap
- FR-051 — the run stops when the turn cap is reached
- FR-052 — the author sets a spend cap
- FR-053 — the run stops when the spend cap is reached
- FR-054 — refuse a run when execution components are incompatible
- FR-055 — refuse a run when the static scan for the content did not pass
- FR-056 — re-run a prior run with the same inputs and latest skills commit
- FR-057 — use a run's output branch as a later run's input branch
- NFR-007 — every run reaches a terminal state within its configured deadline
- NFR-008 — a run that exceeds its deadline is recorded as failed

### Notes
Depends on FA-4B and FA-6A. Re-run semantics deliberately resolve the skills branch again to its
latest commit while preserving the other inputs; output chaining is what allows multi-step manual
experiments without workflow orchestration.

---

## EPIC: Verification & readiness
**Draft key:** `FA-5-PENDING` · **Feature area:** FA-5 · **Release:** MVP · **Labels:** FA-5, MVP

### Description
A run's own claim is not trusted on its own. After the agent exits, this epic runs the selected
verifier on the run branch, gives it the baseline SHA and the skill's `verify.yaml` from the selected
skills commit, and records three things: the agent's claimed verdict, the post-verification final
verdict, and whether verification overturned the claim. It also checks the build's manifest
validity at a commit SHA and refuses to package a skill whose verifier lint, verifier self-test or
required verifier-version range fails. Those signals combine into readiness: a build is marked
Ready at a commit SHA only when the manifest is valid, a run passes, the static scan is not
`DO_NOT_INSTALL`, and the LLM scan has completed or is recorded as unavailable. The build page shows
all four checks and their current state. Finally, an author can re-verify an existing output branch
with a changed `verify.yaml` without invoking the agent or a model, and see which checks flipped.
The same inputs and component versions must produce the same verification result.

### Functional scope
- Run the selected verifier on the run branch after the agent exits.
- Give the verifier the baseline SHA and the `verify.yaml` from the selected skills commit.
- Record the agent's claimed verdict.
- Record the post-verification final verdict.
- Record whether verification overturned the claim.
- Check the build's manifest validity at a commit SHA.
- Mark a build Ready at a commit SHA only when the manifest is valid, a run passes, the static scan
  is not `DO_NOT_INSTALL`, and the LLM scan has completed or is recorded as unavailable.
- Show each of the four readiness checks and its current state on the build page.
- Refuse to package a skill when the verifier's lint check fails.
- Refuse to package a skill when the verifier's self-test fails.
- Refuse to package a skill when the catalog's required verifier range excludes the selected
  verifier version.
- Re-verify an existing run output branch with a changed `verify.yaml` without invoking the agent
  or a model.
- Show which checks flipped compared with the original verification in the re-verification view.
- Produce the same verification result for the same inputs and component versions.
- Inputs: run branch, baseline SHA, skills commit and its `verify.yaml`, build manifest, static
  verdict, LLM scan state and selected verifier version.
- Outputs: claimed and final verdicts, overturn flag, packaging refusals, four named readiness
  checks, Ready or not-ready state at a SHA, and a re-verification comparison.
- Non-goals: running the agent (FA-4B), performing the scans (FA-6A/FA-6B), and opening the
  catalog pull request (FA-8).

### Implementation guidance / dependency order
- Build verifier invocation and verdict recording first, because every readiness input downstream
  depends on a trustworthy final verdict.
- Add the packaging refusals — lint, self-test and verifier-range — next, before any readiness
  aggregation, so an invalid package cannot enter a run.
- Build manifest validity and the four-check readiness aggregator after verdicts and scan state are
  available; the Ready rule must be computed from the same head SHA the build page displays.
- Add the re-verification path last, reusing the verifier invocation and diffing checks against the
  original result. Pin the verifier version per run so NFR-010 is testable. This epic depends on
  FA-4B, FA-6A, FA-6B and FA-2B.

### Goal / Definition of Done
Every run records a claimed verdict, a final verdict and an overturn flag; a build is Ready only
when all four checks pass at its head SHA; the build page shows each check; invalid packages are
refused; and an author can re-verify an output branch with a changed `verify.yaml` and see flipped
checks without running the agent or a model.

### Covered requirements (traceability)
- FR-063 — run the selected verifier on the run branch after the agent exits
- FR-064 — verifier receives the baseline SHA and the skills commit's verify.yaml
- FR-065 — record the agent's claimed verdict
- FR-066 — record the post-verification final verdict
- FR-067 — record whether verification overturned the claim
- FR-068 — check the build's manifest validity at a commit SHA
- FR-069 — mark Ready only when manifest, run, static scan and LLM scan conditions are met
- FR-070 — build page shows each of the four readiness checks
- FR-071 — refuse to package when the verifier's lint check fails
- FR-072 — refuse to package when the verifier's self-test fails
- FR-073 — refuse to package when the required verifier range excludes the selected version
- FR-074 — re-verify an output branch with a changed verify.yaml without the agent or a model
- FR-075 — re-verification shows which checks flipped
- NFR-010 — same inputs and component versions produce the same verification result

### Notes
Depends on FA-4B for runs, FA-6A and FA-6B for scan state, and FA-2B for the build head. The Ready
state is the contract FA-8 gates submission on. LLM-scan unavailability is a recorded state, not a
blocking failure.

---

## EPIC: Run results & audit trail
**Draft key:** `FA-7A-PENDING` · **Feature area:** FA-7 · **Release:** MVP · **Labels:** FA-7, MVP

### Description
After a run finishes, the author needs to understand what happened without reading raw logs or
trusting a summary. This epic builds the run page: it shows the skill and the exact skills commit
SHA, the input and output branches, the component versions used, the claimed and final verdicts,
every check result, the diff from the input branch to the run branch, the Jira changes the run made,
the token usage and cost, and a link to the run's trace. The page is the evidence pack an author
uses to decide whether to re-verify, adjust the skill or submit, and its links are reused in the
catalog pull-request description. The epic also records token usage and cost per run so the spend
view is based on recorded facts rather than estimates.

### Functional scope
- Show the skill and its skills commit SHA on the run page.
- Show the run's input branch and output branch.
- Show the component versions the run used.
- Show the claimed and final verdicts.
- Show each check result.
- Show the diff from the input branch to the run branch.
- Show the Jira changes the run made.
- Show the run's token usage and cost.
- Link to the run's trace.
- Record each run's token usage and cost.
- Inputs: run record, verification results, repository diff, Jira change log and usage accounting.
- Outputs: a complete run results page and a durable cost record.
- Non-goals: cross-run history and comparison (FA-7B), re-verification (FA-5) and submitting to the
  catalog (FA-8).

### Implementation guidance / dependency order
- Build the run projection from the run record and verification results first; the page should read
  one assembled view rather than querying runtime internals per panel.
- Add branch diffing and Jira change collection next, both scoped to the recorded baseline and run
  branches.
- Add token and cost accounting from usage events, then the trace link.
- Keep the run report addressable and linkable so FA-8 can reuse it in a pull-request description.
  This epic depends on FA-4B, FA-4C, FA-5 and FA-3B.

### Goal / Definition of Done
An author can open one run page and see the exact skill commit, both branches, component versions,
both verdicts, every check, the code diff, the Jira changes, token usage and cost, and a working
trace link; token usage and cost are recorded per run.

### Covered requirements (traceability)
- FR-094 — run page shows the skill and skills commit SHA
- FR-095 — run page shows the input branch
- FR-096 — run page shows the output branch
- FR-097 — run page shows the component versions used
- FR-098 — run page shows the claimed and final verdicts
- FR-099 — run page shows each check result
- FR-100 — run page shows the diff from input branch to run branch
- FR-101 — run page shows the Jira changes the run made
- FR-102 — run page shows token usage and cost
- FR-103 — run page links to the run's trace
- NFR-015 — each run records its token usage and cost

### Notes
Depends on FA-4B, FA-4C, FA-5 and FA-3B. The run report is the artifact FA-8 links from the catalog
pull-request description. History and comparison over multiple runs are deliberately separate
(FA-7B).

---

## EPIC: Jira fixture seeding
**Draft key:** `FA-4D-PENDING` · **Feature area:** FA-4 · **Release:** Later · **Labels:** FA-4, Later

### Description
Skills that touch Jira need realistic issues to work against without depending on hand-made
production data. This later epic seeds fixture issues for a run, replaces fixture aliases with the
created issue keys so the skill sees ordinary-looking keys, records the Jira state after the run,
and cleans the seeded issues up when the run ends. A nightly sweep removes seeded issues left behind
by earlier runs that failed or were interrupted. Fixture definitions are curated outside the builder
and reused across runs, so this epic is about deterministic setup, alias substitution, state
capture and safe cleanup rather than about authoring fixture content. It is intentionally outside
the MVP.

### Functional scope
- Seed Jira fixture issues for a run.
- Replace fixture aliases with the created issue keys.
- Record Jira state after a run.
- Clean up seeded issues when a run ends.
- Run a nightly sweep that removes seeded Jira issues left behind by earlier runs.
- Inputs: curated fixture definitions, the project's Jira integration and the run lifecycle.
- Outputs: created issues with resolved aliases, a post-run Jira state record, clean teardown and a
  sweep report.
- Non-goals: authoring fixture content, using production Jira data, and seeding for runs that do
  not opt in.

### Implementation guidance / dependency order
- Define the fixture-to-issue mapping and the alias substitution contract first, because the skill
  content depends on aliases resolving to real keys.
- Add seeding through the project's Jira integration, then state capture after the run.
- Add cleanup on every terminal path, including failure and cancellation, before adding the nightly
  sweep as a backstop.
- Mark seeded issues so cleanup can never delete a human-created issue; the sweep must use the same
  marker. This epic depends on FA-3B and the run lifecycle in FA-4B and FA-4C.

### Goal / Definition of Done
A run that opts into fixtures starts with seeded issues, sees resolved keys instead of aliases, has
its Jira state recorded, and leaves no seeded issues behind on any terminal path; the nightly sweep
removes leftovers from earlier runs and never touches human-created issues.

### Covered requirements (traceability)
- FR-058 — seed Jira fixture issues for a run
- FR-059 — replace fixture aliases with created issue keys
- FR-060 — record Jira state after a run
- FR-061 — clean up seeded issues when a run ends
- FR-062 — nightly sweep removes leftover seeded issues

### Notes
Later release; not part of the MVP path. Depends on FA-3B for Jira access and on FA-4B/FA-4C for run
lifecycle events. Fixture data is curated outside the builder.

---

## EPIC: Skill history & run comparison
**Draft key:** `FA-7B-PENDING` · **Feature area:** FA-7 · **Release:** Later · **Labels:** FA-7, Later

### Description
An author iterating on a skill needs to see how the current attempt relates to earlier ones. This
later epic adds a skill history that lists every run of a skill with its commit SHA, input branch,
verdict and check results, and a compare view that places two runs side by side and highlights the
checks that flipped between them. It also covers the privacy obligations that apply once results
accumulate: run transcripts, logs and results are retained only for a configured period and can be
purged on request. The history and comparison views build on the run results in FA-7A, and the
retention and purge behavior applies to the same stored artifacts.

### Functional scope
- List every run of a skill with its commit SHA, input branch, verdict and check results.
- Show two runs side by side in a compare view.
- Highlight the checks that flipped between the two compared runs.
- Retain run transcripts, logs and results only for a configured period.
- Purge run transcripts, logs and results on request.
- Inputs: recorded runs and results from FA-7A, and the configured retention period.
- Outputs: a skill history list, a comparison view with flips, and retention and purge behavior.
- Non-goals: changing run results, re-running a skill, and comparing more than two runs at once.

### Implementation guidance / dependency order
- Build the history index over recorded runs first, keyed by skill and ordered by time.
- Add the compare view next, reusing the check-result model from FA-7A so flipped checks are a
  comparison of the same structure rather than a second interpretation.
- Add retention and purge last, once every artifact location it must cover is enumerated. Apply
  purge to transcripts, logs and results together, and verify a purge cannot leave a partial
  transcript behind. This epic depends on FA-7A.

### Goal / Definition of Done
An author can list every run of a skill and compare any two runs side by side with flipped checks
highlighted; transcripts, logs and results expire after the configured period and can be purged on
request.

### Covered requirements (traceability)
- FR-104 — skill history lists every run with commit SHA, input branch, verdict and checks
- FR-105 — compare view shows two runs side by side
- FR-106 — compare view highlights checks that flipped
- NFR-013 — transcripts, logs and results retained only for a configured period
- NFR-014 — transcripts, logs and results can be purged on request

### Notes
Later release; not part of the MVP path. Depends on FA-7A for the run results and on the platform's
retention configuration. Comparison is limited to two runs by the PRD.

---

## EPIC: Catalog submission
**Draft key:** `FA-8-PENDING` · **Feature area:** FA-8 · **Release:** MVP · **Labels:** FA-8, MVP

### Description
Submission is the hand-off from the isolated builder to the reviewed catalog, and it must be
deliberate. This epic enables Submit to catalog only when all four readiness checks pass at the
build head SHA, then opens a pull request from the build branch to the catalog main branch using
the author's own source-control identity. The pull-request description carries the evidence a
reviewer needs: the readiness checks at the head SHA, a link to the run report and links to the scan
reports. The builder records the pull-request URL and state on the build, and moves the build
through open, submitted, and merged or abandoned. A save on a submitted build clears its readiness
status so a stale approval cannot ride along with new content. The builder never writes directly to
the platform catalog, platform projects or project skills; the pull request is the only output.

### Functional scope
- Enable Submit to catalog only when all four readiness checks pass at the build head SHA.
- Open a pull request from the build branch to the catalog main branch using the author's own
  source-control identity.
- Put the readiness checks at the head SHA in the pull-request description.
- Link the run report and the scan reports from the pull-request description.
- Record the pull-request URL and state on the build.
- Move the build through open, submitted, and either merged or abandoned.
- Clear a submitted build's readiness status when a save occurs.
- Never write directly to the platform catalog, platform projects or project skills.
- Inputs: Ready build at a head SHA, run report, scan reports and the author's source-control
  identity.
- Outputs: a catalog pull request, its URL and state on the build, and build state transitions.
- Non-goals: merging the pull request, bypassing catalog review, and publishing without the four
  readiness checks.

### Implementation guidance / dependency order
- Build the submission gate from the readiness result first, and compute it against the same head
  SHA the build page shows; any mismatch must block.
- Add pull-request creation with the author's identity next, then assemble the description from the
  recorded readiness checks, run report link and scan report links.
- Add pull-request state synchronization and the open/submitted/merged/abandoned state machine after
  creation works.
- Wire the save-on-submitted invalidation last, and add a test that no code path writes to the
  catalog, platform projects or project skills directly. This epic depends on FA-5, FA-7A, FA-3B
  and FA-2B.

### Goal / Definition of Done
Submit is available only for a build whose four readiness checks pass at its head; submitting opens
a catalog pull request under the author's identity with the checks, run report and scan reports in
the description; the build records the pull-request URL and state and moves through the required
states; a new save clears readiness; and the builder never writes directly to the catalog.

### Covered requirements (traceability)
- FR-107 — enable Submit only when all four readiness checks pass at the head SHA
- FR-108 — open a catalog pull request using the author's source-control identity
- FR-109 — pull-request description lists readiness checks at the head SHA
- FR-110 — pull-request description links to the run report
- FR-111 — pull-request description links to the scan reports
- FR-112 — record the pull-request URL and state on the build
- FR-113 — build state moves through open, submitted, merged or abandoned
- FR-114 — a save on a submitted build clears its readiness status
- FR-115 — never write directly to the platform catalog, projects or project skills

### Notes
Depends on FA-5 for readiness, FA-7A for the run report, FA-3B for the author's source-control
identity and FA-2B for build state. The catalog repository and its review flow are external; the
builder's responsibility ends at the pull request.

---

## EPIC: Command line & suites
**Draft key:** `FA-9-PENDING` · **Feature area:** FA-9 · **Release:** mixed · **Labels:** FA-9, mixed

### Description
Authors who work from a terminal, or who want a run to happen outside a browser session, need the
same capabilities without the web interface. The MVP slice of this epic adds a command-line runner
that starts a test run, runs a static-only security scan without a run, and runs a full security
scan without a run, all using the same service layer as the web UI so behaviour cannot drift. The
later slice adds named suites: an author saves a suite of runs, each entry naming a skill, an input
branch, a context and expectations, then runs the suite on demand or schedules it for nightly
execution. Each scheduled run's result is recorded so the author can see whether the suite held. The
CLI and suites are clients of the run, scan and verification capabilities built in earlier epics,
not parallel implementations.

### Functional scope
- MVP: start a test run from the command line without the web interface.
- MVP: run a static-only security scan from the command line without a test run.
- MVP: run a full security scan from the command line without a test run.
- Later: save a named suite of runs.
- Later: let a suite entry name a skill, an input branch, a context and expectations.
- Later: run a saved suite.
- Later: schedule a saved suite for nightly execution.
- Later: record each scheduled run's result.
- Inputs: command-line arguments or saved suite definitions, plus the same configuration and
  credentials the web path uses.
- Outputs: run and scan results, saved suite definitions, and recorded scheduled results.
- Non-goals: a second execution path, workflow orchestration, and multi-skill parallel runs.

### Implementation guidance / dependency order
- Expose a stable service-layer API for start-run, static scan and full scan first; the CLI should
  be a thin client over it, so the web and command-line paths cannot diverge.
- Build the CLI commands for the MVP slice next, including non-interactive authentication and clear
  exit codes.
- Add the suite model and suite runner in the later slice, reusing the same start-run service.
- Add scheduling and result recording last, and make a scheduled invocation idempotent per night so
  a retry does not create duplicate runs. This epic depends on FA-4A, FA-4B, FA-5, FA-6A and FA-6B.

### Goal / Definition of Done
An author can start a run, a static-only scan and a full scan from the command line with the same
results as the web interface; in the later slice, an author can save a named suite, run it on
demand, schedule it nightly, and see each scheduled run's recorded result.

### Covered requirements (traceability)
- FR-116 — command line starts a test run without the web interface
- FR-117 — command line runs a static-only security scan without a test run
- FR-118 — command line runs a full security scan without a test run
- FR-119 — save a named suite of runs
- FR-120 — a suite entry names a skill, input branch, context and expectations
- FR-121 — run a saved suite
- FR-122 — schedule a saved suite for nightly execution
- FR-123 — record each scheduled run's result

### MVP subset (if release = mixed)
MVP: FR-116, FR-117, FR-118. Later: FR-119, FR-120, FR-121, FR-122, FR-123.

### Notes
Depends on FA-4A, FA-4B, FA-5, FA-6A and FA-6B. The MVP slice is the CLI for runs and scans; the
suite and scheduling slice is Later. The command line must call the same service layer as the web
interface rather than reimplementing run or scan logic.

---

## EPIC: Accessibility conformance
**Draft key:** `FA-X-PENDING` · **Feature area:** cross-cutting · **Release:** MVP · **Labels:** cross-cutting, accessibility, MVP

### Description
Every authoring surface in the builder is a web interface, and it must be usable by people who rely
on assistive technology. This cross-cutting epic owns conformance with WCAG 2.1 AA across the whole
product rather than leaving accessibility to be picked up inconsistently inside feature epics. It
covers the sign-in and authorization pages, build and project management, run setup and live
progress, verification and readiness views, results and history, security reports, catalog
submission and the command-line-facing documentation pages. The work is both preventive — a
component baseline and automated checks — and corrective — an audit of each surface as it lands,
with remediation tracked to closure. Because the requirement applies to the whole interface, it is
deliberately separate from every feature epic.

### Functional scope
- Meet WCAG 2.1 AA across every web interface in the builder.
- Cover keyboard operation and visible focus for all interactive controls, including run progress
  and log views.
- Provide programmatic names, roles and states for custom components such as readiness checks,
  verdict badges and diff viewers.
- Meet contrast requirements in normal and hover/focus states, including status colors.
- Expose form labels, instructions and error messages programmatically and associate them with the
  fields they describe.
- Ensure status changes such as run progress and readiness updates are announced without relying
  on color alone.
- Include accessibility checks in the component baseline and in continuous verification.
- Inputs: the web surfaces delivered by FA-1 through FA-9 and the shared component library.
- Outputs: a documented WCAG 2.1 AA audit result and remediated surfaces.
- Non-goals: WCAG AAA, native mobile applications, and changing the platform interface outside the
  builder.

### Implementation guidance / dependency order
- Establish an accessible component baseline and automated checks early, before feature teams build
  many pages on top of inaccessible primitives.
- Audit each surface as it becomes usable, starting with sign-in and build creation, which every
  author must pass through.
- Remediate the highest-traffic surfaces first — build page, run setup, run results and submission
  — then complete the remaining admin and report views.
- Keep a final manual audit with assistive technology as the release gate; automated checks alone
  do not establish WCAG 2.1 AA. This epic runs alongside FA-1 through FA-9 rather than after them,
  and its release gate is the complete web interface.

### Goal / Definition of Done
A WCAG 2.1 AA audit passes across every builder web surface, automated accessibility checks run in
continuous verification, and an author using a keyboard or assistive technology can complete the
full create, run, verify and submit flow.

### Covered requirements (traceability)
- NFR-012 — the web interface meets WCAG 2.1 AA

### Notes
Cross-cutting and continuous: it starts with the component baseline and completes when all surfaces
exist. It depends on the interfaces delivered by FA-1 through FA-9 but does not own their feature
behavior. NFR-012 is the only requirement assigned to this epic.

---

*Generated by `sdlc-plan-epics-create`. Every PRD requirement is mapped exactly once in
`epic-map.json`. Next steps: `sdlc-tracker-sync` publishes the epics to Jira, then
`sdlc-plan-stories-write` runs for each epic.*
