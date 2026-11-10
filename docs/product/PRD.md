# PRD — Skill Builder

**Status:** Draft · **Owner:** Saraav · **Last updated:** 2026-11-10

## 1. Problem & Opportunity

Platform skills are edited only in `bheembhai-skills` (ADR-032), yet the two existing test tiers
are static: tier 1 checks the catalog's shape and tier 2 self-tests a verifier on examples.
Neither exercises a skill against real Jira, GitHub and a model, so a skill author cannot see what
a skill actually did, diagnose why it failed, or prove a fix in the runtime the platform uses.
The cost is paid twice: authors ship unproven skills, and reviewers inherit problems that surface
only on the platform. Trying to close that loop inside the platform would add sandbox projects,
draft catalogs and per-project drafts to its data model, engine and UI, which is heavy for every
project. The opportunity is to let authors prove a skill before it reaches the platform, without
making the platform or its projects the test bed.

## 2. Target Users

| User type | Primary need | Notes |
|-----------|--------------|-------|
| Skill author | Create or clone a skill, run it against real test integrations, inspect the result and submit it to the catalog | Must be in the `skill-builders` Cognito group; spends tokens and writes build branches |
| Project owner | Configure the test project's Jira, GitHub and model integrations and manage members | A skill author who owns that project |
| Platform admin | Manage `skill-builders` group membership; import the released catalog into the platform | External to the builder; the builder has no user-admin screen |
| Catalog reviewer | Review the submitted PR against the Ready evidence | Consumes the PR; uses CODEOWNERS review |
| Builder operator | Run the host and provision Cognito, ECR, Secrets Manager, S3 and IAM | Needs Docker on the host |

## 3. Goals & Success Metrics

- **G1 — Close the authoring loop.** A skill can go from creation to Ready entirely inside the
  builder, in the real platform runtime.
  - Metric: 100% of pilot skills reach Ready through the builder; median time from create to
    first passing verified run is at most one working day.
- **G2 — Match the platform's judgement.** The builder must not be a second, drifting
  implementation.
  - Metric: 100% of golden parity tests pass for scan verdict and rendered `BB_CONTEXT`, with no
    unexplained verdict difference in the pilot.
- **G3 — Be safe by construction.** Test credentials and test data must never leak or be
  overwritten.
  - Metric: zero secret values in the database, logs, results or pages; zero writes to an input
    branch; zero direct writes to the platform or catalog.
- **G4 — Make iteration cheap.** Authors should tune checks and compare outcomes quickly.
  - Metric: re-verify returns in under 60 seconds with zero model tokens; at least 90% of runs
    complete without operator intervention.
- **G5 — Get adopted.** The builder must replace the ad-hoc local loop for the pilot team.
  - Metric: at least 10 skills authored in the first month; at least 50% of Ready builds
    submitted and merged.
- **G6 — Be operable.** The whole product must be deployable, observable and maintainable by one
  operator.
  - Metric: a clean host reaches a serving app in one docker-compose command; every run and scan
    is traceable from a structured log to its database record.

## 4. Scope

**In scope (MVP):** Cognito sign-in restricted to the `skill-builders` group; create, clone and
edit builds; test projects, members and integrations; runs with branch isolation, content-addressed
bundles and the pinned platform runtime; verification and the four Ready checks; static and LLM
security scans; run page, re-run and re-verify; runner CLI for run and scan; Submit to catalog as a
pull request; platform-kit pinning; server-rendered UI, JSON REST APIs, relational storage and
docker-compose deployment.

**Out of scope (Later / explicitly not now):** skill history, run comparison, saved suites and
nightly CI execution (ADR rollout S3); Jira fixture seeding, post-run capture and cleanup (S3);
PR merge and close state synchronisation; a fault-injecting proxy for failure cases; version
numbering inside the builder; running workflows with gates and routing; any change to the
platform's data model, engine or UI; writing to platform projects or project-owned skills; human
review of LLM scan findings.

## 5. Feature Areas

| Area code | Feature area | One-line description |
|-----------|--------------|----------------------|
| FA-1 | Identity and access | Sign in with the platform's Cognito pool and enforce the `skill-builders` group on every request |
| FA-2 | Build authoring | Create, clone and edit a skill on its own `build/*` branch |
| FA-3 | Projects and integrations | Test projects, membership, and Jira, GitHub and model integrations with managed secrets |
| FA-4 | Test runs | Prepare, launch and classify one skill run against real integrations |
| FA-5 | Verification and readiness | Grade a run with the pinned verifier and decide when a build is Ready |
| FA-6 | Security scanning | Static and LLM SkillSpector scans with the platform's scanner image and blocking rules |
| FA-7 | Results and history | Run evidence, re-run, re-verify, history and comparison |
| FA-8 | Runner CLI | Run and scan a skill without the web app, including for CI |
| FA-9 | Catalog submission | Turn a Ready build into a reviewed pull request to `main` |
| FA-10 | Platform kit pinning | Run exactly the platform's pinned runtime, images and verifier |
| FA-11 | Deployment and operations | Single-host Docker deployment, schema lifecycle, per-run object storage and least-privilege AWS access |
| FA-12 | Application backend and data | The builder's own server-side REST APIs, relational records and web UI delivery |

## 6. Functional Requirements

| ID | Feature area | Requirement (one testable capability) | Release |
|------|--------------|----------------------------------------|---------|
| FR-001 | FA-1 | The system signs a user in through a dedicated app client of the platform's existing Cognito User Pool. | MVP |
| FR-002 | FA-1 | The system refuses sign-in for a user who is not a member of the `skill-builders` Cognito group and shows a clear reason. | MVP |
| FR-003 | FA-1 | The system verifies every session token's signature and expiry with the platform's Cognito provider. | MVP |
| FR-004 | FA-1 | The system checks the `cognito:groups` claim on every request, not only at sign-in, and refuses a request when the claim is absent. | MVP |
| FR-005 | FA-1 | The system creates a local user record keyed by the Cognito `sub` on first successful sign-in. | MVP |
| FR-006 | FA-1 | The system updates the local user's email and name on each later sign-in. | MVP |
| FR-007 | FA-1 | The system refuses unauthenticated access to every page and API with a sign-in redirect or a 401. | MVP |
| FR-008 | FA-1 | A signed-in user can sign out, and the app session ends. | MVP |
| FR-009 | FA-1 | The system stops honouring a removed group member's access no later than the current token's expiry, at most one hour. | MVP |
| FR-010 | FA-2 | A skill-builder user can create a build by supplying a skill name and a one-line description. | MVP |
| FR-011 | FA-2 | On create, the system writes the default skill structure: `SKILL.md` with frontmatter, a `verify.yaml` v2 stub, and `references/`, `templates/` and `examples/` folders with their README. | MVP |
| FR-012 | FA-2 | A newly created skill passes tier-1 checks with no edits. | MVP |
| FR-013 | FA-2 | A newly created skill reports its absent checks as a warning. | MVP |
| FR-014 | FA-2 | A user can clone an existing catalog skill into a build under a new name. | MVP |
| FR-015 | FA-2 | Clone copies the whole skill folder to the new name. | MVP |
| FR-016 | FA-2 | Clone rewrites `name:` in the copied skill's frontmatter. | MVP |
| FR-017 | FA-2 | Clone leaves the source skill's files unchanged. | MVP |
| FR-018 | FA-2 | Clone records no link back to the original skill. | MVP |
| FR-019 | FA-2 | Create and clone refuse a name that already exists on `main` or on another open build. | MVP |
| FR-020 | FA-2 | Create and clone refuse a name that does not follow `sdlc-<area>-<action>`. | MVP |
| FR-021 | FA-2 | The system creates each build on its own branch `build/<skill-name>` cut from `main`. | MVP |
| FR-022 | FA-2 | The system commits each save on a build. | MVP |
| FR-023 | FA-2 | The system records the resulting commit SHA of each save on the build. | MVP |
| FR-024 | FA-2 | A user can open an existing catalog skill as an edit build on a branch. | MVP |
| FR-025 | FA-2 | The build page shows the build state, its head SHA and its commits. | MVP |
| FR-026 | FA-2 | A user can abandon an open build without changing `main` or the catalog. | MVP |
| FR-027 | FA-3 | A skill-builder user can create a test project, and the creator becomes its owner. | MVP |
| FR-028 | FA-3 | Only a project owner can add or remove project members. | MVP |
| FR-029 | FA-3 | Every project member can start runs in the project. | MVP |
| FR-030 | FA-3 | Only the project owner can change integrations. | MVP |
| FR-031 | FA-3 | A project owner can configure a Jira integration with site URL, project key or template project, and MCP server definition. | MVP |
| FR-032 | FA-3 | A project owner can configure a GitHub integration with sandbox repository, base branch, MCP server definition and access token. | MVP |
| FR-033 | FA-3 | A project owner can configure one or more AI model profiles with vendor, base URL, tier-to-model mapping and API key. | MVP |
| FR-034 | FA-3 | The system stores integration credentials in a secrets store and keeps only the secret reference in its database. | MVP |
| FR-035 | FA-3 | The system verifies an integration's settings and credentials. | MVP |
| FR-036 | FA-3 | The system records when an integration last verified successfully. | MVP |
| FR-037 | FA-3 | The system warns when a GitHub integration points at a repository that a platform project also uses. | MVP |
| FR-038 | FA-3 | The system lists only the projects that the signed-in user is a member of. | MVP |
| FR-039 | FA-4 | A user can start a run by selecting a skills branch, an input branch, an optional context, a model profile and tier, and turn and spend caps. | MVP |
| FR-040 | FA-4 | The system resolves the selected skills branch to a commit SHA and records that SHA on the run. | MVP |
| FR-041 | FA-4 | The system packs the skill at that SHA into a content-addressed bundle. | MVP |
| FR-042 | FA-4 | The system reuses the same bundle when the same skills SHA is run again. | MVP |
| FR-043 | FA-4 | The system uploads the bundle to the builder's own object storage and passes the container a presigned URL and the bundle checksum. | MVP |
| FR-044 | FA-4 | The system creates a new run branch `skilltest/<run-id>` from the input branch head. | MVP |
| FR-045 | FA-4 | The system records the input branch head SHA as the run's baseline. | MVP |
| FR-046 | FA-4 | A run never writes to its input branch. | MVP |
| FR-047 | FA-4 | The system launches the pinned agent image for a run. | MVP |
| FR-048 | FA-4 | The system records the agent image digest, stepkit version and verifier version on the run. | MVP |
| FR-049 | FA-4 | A user can follow run progress and agent logs while the run executes. | MVP |
| FR-050 | FA-4 | The system classifies the run outcome on exit using the same result statuses as the platform's reconciler. | MVP |
| FR-051 | FA-4 | The system enforces the run's turn cap and stops the run when the cap is reached. | MVP |
| FR-052 | FA-4 | The system enforces the run's spend cap and stops the run when the cap is reached. | MVP |
| FR-053 | FA-4 | A user can choose an earlier run's output branch as the next run's input branch. | MVP |
| FR-054 | FA-4 | A user can supply optional reviewer feedback as run context to test send-back behaviour. | MVP |
| FR-055 | FA-4 | A user can supply an optional upstream handoff as run context to test a BLOCK hand-off. | MVP |
| FR-056 | FA-4 | The system refuses to start a run whose exact skill bundle has not passed the static security check. | MVP |
| FR-057 | FA-4 | The system records each run's actor, skill, SHAs, branches, model profile, tier, state and timestamps. | MVP |
| FR-058 | FA-4 | The system can seed Jira issues from a named fixture before a run. | Later |
| FR-059 | FA-4 | The system replaces fixture aliases with real issue keys at seed time. | Later |
| FR-060 | FA-4 | The system records the Jira state after a run for display and assertions. | Later |
| FR-061 | FA-4 | The system cleans up seeded Jira issues after a run. | Later |
| FR-062 | FA-4 | A nightly sweep removes seeded Jira issues that a run left behind. | Later |
| FR-063 | FA-5 | After a run, the system runs the pinned verifier on the run branch outside the agent container. | MVP |
| FR-064 | FA-5 | Verification uses the baseline SHA for `must_change` and preconditions. | MVP |
| FR-065 | FA-5 | Verification uses the skill's `verify.yaml` from the pinned skills commit. | MVP |
| FR-066 | FA-5 | The run page shows the agent's claimed verdict, the final verdict after verification, and whether verification overturned the claim. | MVP |
| FR-067 | FA-5 | The run page shows each L0 and L1 check result, and L2 results when enabled. | MVP |
| FR-068 | FA-5 | The system marks a build Ready at a SHA only when all four checks hold there: valid manifest, passing verified run, static security not `DO_NOT_INSTALL`, and LLM security completed or unavailable. | MVP |
| FR-069 | FA-5 | The build page shows the four Ready checks and their status at the head SHA. | MVP |
| FR-070 | FA-5 | A new commit on a build clears Ready until all four checks pass at the new SHA. | MVP |
| FR-071 | FA-5 | The build page keeps runs against earlier SHAs visible after Ready is cleared. | MVP |
| FR-072 | FA-5 | The system enables Submit to catalog only when all four Ready checks hold at the head SHA. | MVP |
| FR-073 | FA-5 | A user can re-verify an existing output branch against a new `verify.yaml` without launching an agent or spending model tokens. | MVP |
| FR-074 | FA-5 | Re-verify shows which checks flipped relative to the original run. | MVP |
| FR-075 | FA-5 | Before packing a skill, the system runs verifier lint and selftest and refuses to start the run if either fails. | MVP |
| FR-076 | FA-5 | The system refuses to run a skill when `catalog.yaml`'s `requires_verify` does not accept the pinned verifier version. | MVP |
| FR-077 | FA-6 | A user can trigger a static security scan from a skill page. | MVP |
| FR-078 | FA-6 | The system runs every security scan in the pinned scanner container, never in the app process, with the skill bundle mounted read-only. | MVP |
| FR-079 | FA-6 | The static scan runs with no network access. | MVP |
| FR-080 | FA-6 | The LLM scan receives the model key only as environment input and has network access only to the selected model endpoint. | MVP |
| FR-081 | FA-6 | Each scanner container has a 10-minute limit. | MVP |
| FR-082 | FA-6 | The system records a scanner timeout as a failed scan. | MVP |
| FR-083 | FA-6 | The system caches static scan results by skill content SHA. | MVP |
| FR-084 | FA-6 | The system refuses a run when the static scan returns `DO_NOT_INSTALL`, a CRITICAL finding, or incomplete coverage, and shows the findings. | MVP |
| FR-085 | FA-6 | An author cannot override a static-scan block, including with accepted findings. | MVP |
| FR-086 | FA-6 | The system queues an LLM scan only after the static scan passes for the same content SHA. | MVP |
| FR-087 | FA-6 | An LLM scan never blocks a run. | MVP |
| FR-088 | FA-6 | The author selects the model profile for an LLM scan, and only the project owner can change the default. | MVP |
| FR-089 | FA-6 | The Security tab shows the score, recommendation, each finding with severity, rule, file and line, and the model used for the LLM scan. | MVP |
| FR-090 | FA-6 | The system shows scan status (queued, running, complete, failed) on the skill and run pages. | MVP |
| FR-091 | FA-6 | The system does not run a scan automatically on save. | MVP |
| FR-092 | FA-6 | The system stores each scan with its skill content SHA, status, verdict and findings. | MVP |
| FR-093 | FA-7 | The run page shows the skill and skills SHA, input and output branches, agent image digest, stepkit version and verifier version. | MVP |
| FR-094 | FA-7 | The run page shows the diff from the input branch to the run branch. | MVP |
| FR-095 | FA-7 | The run page shows Jira changes, turns, tokens, cost and a trace link when available. | MVP |
| FR-096 | FA-7 | Skill history lists every run of one skill with SHA, input branch, verdict and check results. | Later |
| FR-097 | FA-7 | A user can compare two runs side by side with flipped checks highlighted. | Later |
| FR-098 | FA-7 | A user can re-run a previous run's inputs against the skills branch's latest SHA. | MVP |
| FR-099 | FA-7 | A user can save a named suite of runs. | Later |
| FR-100 | FA-7 | A user can run a saved suite from the UI or the CLI. | Later |
| FR-101 | FA-7 | The system persists runs and their artifacts across app restarts and retrieves them by run id. | MVP |
| FR-102 | FA-8 | The CLI can run one skill with the same pins as the app without starting the web app. | MVP |
| FR-103 | FA-8 | The CLI can run both security scan stages. | MVP |
| FR-104 | FA-8 | The CLI's `--static-only` option skips the LLM scan stage. | MVP |
| FR-105 | FA-8 | The CLI exits with a clear pass or fail status suitable for CI. | MVP |
| FR-106 | FA-8 | The CLI scan starts the same scanner container as the app and requires Docker on the host. | MVP |
| FR-107 | FA-8 | A nightly CI job or a `run-behaviour` PR label can execute a saved suite. | Later |
| FR-108 | FA-9 | A Ready build can be submitted, opening a pull request from `build/<skill-name>` to `main`. | MVP |
| FR-109 | FA-9 | The PR description lists the four Ready checks at the head SHA with links to the run and scan reports. | MVP |
| FR-110 | FA-9 | The system opens the PR with the submitting user's own GitHub identity. | MVP |
| FR-111 | FA-9 | The system stores the PR URL after submission. | MVP |
| FR-112 | FA-9 | The system marks the build `submitted` after submission. | MVP |
| FR-113 | FA-9 | The system marks a build `merged` when its pull request merges. | Later |
| FR-114 | FA-9 | The system marks a build `abandoned` when its pull request closes without merge. | Later |
| FR-115 | FA-9 | The system never writes to the platform or to project skills; submission is a pull request only. | MVP |
| FR-116 | FA-10 | The system pins one platform kit version and installs exactly the components its `kit.json` lists. | MVP |
| FR-117 | FA-10 | The system pulls the agent and scanner images from the platform registry by digest only. | MVP |
| FR-118 | FA-10 | The system refuses a run or scan when an image is supplied by tag. | MVP |
| FR-119 | FA-10 | The system refuses a run or scan when the image and stepkit versions are declared incompatible. | MVP |
| FR-120 | FA-10 | The system records the kit version, image digests and component versions used for each run. | MVP |
| FR-121 | FA-10 | Updating an image, the verifier or the stepkit requires only a `kit.txt` version change in a PR. | MVP |
| FR-122 | FA-11 | The web app and database deploy together with docker-compose on a local machine or a single host. | MVP |
| FR-123 | FA-11 | The system initializes its database schema on deployment. | MVP |
| FR-124 | FA-11 | The system preserves existing data when it upgrades its database schema. | MVP |
| FR-125 | FA-11 | The system stores run bundles, results, logs and transcripts under a per-run prefix in its own object-storage bucket. | MVP |
| FR-126 | FA-11 | The system leaves the platform's data model, engine and UI unchanged. | MVP |
| FR-127 | FA-12 | The system keeps its own records for users, builds, projects, members, integrations, bundles, runs, Jira state and suites in a relational database. | MVP |
| FR-128 | FA-12 | The system exposes an HTTP JSON REST API for every operation the web UI performs. | MVP |
| FR-129 | FA-12 | The system documents its REST API in an OpenAPI description served by the running app. | MVP |
| FR-130 | FA-12 | The system returns a consistent error object with a stable code and the matching HTTP status for every rejected API request. | MVP |
| FR-131 | FA-12 | The system serves every UI page as server-rendered HTML. | MVP |
| FR-132 | FA-12 | The system applies the platform's visual theme to every UI page. | MVP |
| FR-133 | FA-12 | The system exposes an unauthenticated health endpoint that reports app and database status. | MVP |
| FR-134 | FA-12 | The system serves the web UI and its REST API from the same application process. | MVP |
| FR-135 | FA-12 | The system paginates list API responses and returns a stable page cursor. | MVP |

## 7. Non-Functional Requirements

| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Security/Privacy | Credential values never appear in the database, logs, run results or run pages; only secret references are persisted. | MVP |
| NFR-002 | Security | The builder's AWS role can read and write only `skill-builder/*` secrets and its own storage bucket, and read only the two platform image repositories. | MVP |
| NFR-003 | Security | Untrusted skill content is parsed only inside the scanner container, never in the app process. | MVP |
| NFR-004 | Security | Every deployed request travels over HTTPS, and session cookies are marked Secure and HttpOnly. | MVP |
| NFR-005 | Integrity | Packing the same skills commit and skill twice yields the same bundle SHA. | MVP |
| NFR-006 | Integrity | Every run and scan is bound to the exact commit SHA and artifact it evaluated. | MVP |
| NFR-007 | Integrity/Isolation | The builder never writes to the platform database, the catalog, project skills or a run's input branch. | MVP |
| NFR-008 | Fidelity | For the same bundle, the builder and the platform produce the same security-scan verdict. | MVP |
| NFR-009 | Fidelity | For the same workflow step, the builder and the platform build the same `BB_CONTEXT`. | MVP |
| NFR-010 | Performance | A security-scan stage completes or fails within its 10-minute limit. | MVP |
| NFR-011 | Performance | Scans and runs execute asynchronously so the UI stays responsive. | MVP |
| NFR-012 | Performance | Re-verify makes no model calls and returns results in under 60 seconds for a typical skill. | MVP |
| NFR-013 | Operability | The whole app stack starts reproducibly with one docker-compose command on a single Docker host. | MVP |
| NFR-014 | Accessibility | The core authoring, run and result flows meet WCAG 2.1 AA and use the platform's visual theme. | MVP |
| NFR-015 | Auditability | Every run, scan and submission records the actor, exact SHAs, pinned versions and timestamp. | MVP |
| NFR-016 | Reliability | An interrupted run is recorded with a terminal state and never leaves its input branch modified. | MVP |
| NFR-017 | Observability | Every request, run and scan emits structured logs carrying its request or run id and no credential value. | MVP |
| NFR-018 | Reliability | A failure in one run or scan does not stop queued or running work for other users. | MVP |

## 8. Constraints & Assumptions

- **Input basis.** The launch notes name a target Jira story, "SkillBuilder". On 2026-11-10 the
  configured Atlassian site was searched for it: full-text searches across all projects for
  "SkillBuilder", "Skill Builder" and "builder" returned no issue, and a listing of every issue
  created in the previous 60 days returned only three unrelated issues. The `BSB`
  (bheembhai-skill-builder) project contains no issues. No summary, description or acceptance
  criteria could therefore be fetched. As the launch notes direct, this PRD treats
  `docs/adr/SK-001-skill-builder.md` plus the notes as the authoritative product input. No story
  details were invented; the Jira story is assumed to be created or linked later by the planning
  workflow.
- **Platform dependency.** The builder consumes the platform's shared runtime kit (platform
  ADR-033). Platform rollout S0, extracting `bheembhai-stepkit` and publishing a `kit-v*` release,
  must ship before a run can execute; the builder pins one kit version.
- **Provisioned infrastructure.** The platform's Cognito User Pool exists, with a dedicated app
  client and the `skill-builders` group; a platform admin manages membership. The builder host has
  a Docker daemon, a read-only ECR identity for the two platform images, a Secrets Manager path
  `skill-builder/*`, its own S3 bucket, and an IAM role scoped to those resources.
- **Test-only data.** Jira tokens, GitHub tokens and model keys point at a test Jira site, a
  sandbox repository and test model access. The builder warns when a sandbox repository overlaps a
  platform project.
- **MVP boundary.** MVP corresponds to ADR rollout S1-S2 (runner, CLI, web app, Ready and
  submission). ADR rollout S3 (skill history, comparison, suites, nightly CI, Jira seeding and
  cleanup) is marked Later.
- **Stack.** Python and FastAPI, server-rendered HTML using the platform's theme, PostgreSQL or
  SQLite for a single host, and Docker as the container runtime. The REST API is JSON over HTTP
  served by the same FastAPI process as the UI.
- **Repository.** The builder lives in `bheembhai-skills` but is excluded from catalog releases;
  `tools/build.py` packs only `skills/`, `config/` and `catalog.yaml`.
- **No versioning inside the builder.** A build is a branch, and each save is a commit; versions
  begin at the catalog release.
- **No platform change.** The builder adds no testing behaviour to the platform's data model,
  engine or UI.

## 9. Open Questions

- Jira isolation: a fresh Jira project per run, or one shared project with a `skilltest-<run>`
  label on everything?
- Should verification stay in the builder for good, or move into the agent image later? The
  runner works either way; the answer decides only where the result comes from.
- Where does the builder run: a laptop with Docker, one EC2 host, or ECS?
- One stepkit package, or split the auth and secrets helpers into their own package?
- What concurrency must one host support, and should runs above that limit queue or be refused?
- How long are run artifacts and transcripts retained, and what cleanup policy applies?
- Which API versioning scheme should the REST API use once the UI and CLI are both consumers?
- Which GitHub credential mode is used for the submission PR: a per-user fine-grained token, or a
  GitHub App that acts for the user? The requirement is that the author is the person, not the app.

---
*Generated by the `sdlc-plan-prd-write` skill. Next step: run `sdlc-plan-epics-create` to turn feature areas into epics.*
