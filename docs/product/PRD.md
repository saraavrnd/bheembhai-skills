# PRD — Skill Builder

**Status:** Draft · **Owner:** Saraav · **Last updated:** 2026-11-10

## 1. Problem & Opportunity

Platform skills are edited only in `bheembhai-skills` (ADR-032), but the two existing test tiers
are static: tier 1 checks the catalog's shape and tier 2 self-tests a verifier on examples.
Neither actually runs a skill against real Jira, GitHub and a model, so a skill author cannot see
what a skill did, diagnose the failure and try again in the runtime the platform actually uses.
The cost is paid twice: authors ship unproven skills and reviewers inherit problems that only
appear on the platform, while attempting the loop inside the platform would change its data model,
engine and UI for every project. There is an opportunity to give authors a faithful
edit → run → verify → scan → submit loop that leaves the platform and its projects untouched.

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

## 4. Scope

**In scope (MVP):** Cognito sign-in restricted to the `skill-builders` group; create, clone and
edit builds; test projects, members and integrations; runs with branch isolation, content-addressed
bundles and the pinned platform runtime; verification and the four Ready checks; static and LLM
security scans; run page, re-run and re-verify; runner CLI for run and scan; Submit to catalog as a
pull request; platform-kit pinning; docker-compose deployment.

**Out of scope (Later / explicitly not now):** skill history, run comparison, saved suites and
nightly CI execution (ADR rollout S3); Jira fixture seeding, post-run capture and cleanup (S3);
PR merge/close state synchronisation; a fault-injecting proxy for failure cases; version numbering
inside the builder; running workflows with gates and routing; any change to the platform's data
model, engine or UI; writing to platform projects or project-owned skills; human review of LLM
scan findings.

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
| FR-003 | FA-1 | The system checks the `cognito:groups` claim on every request, not only at sign-in, and refuses a request when the claim is absent. | MVP |
| FR-004 | FA-1 | The system creates a local user record keyed by the Cognito `sub` on first successful sign-in and updates the user's email and name on later sign-ins. | MVP |
| FR-005 | FA-1 | The system refuses unauthenticated access to every page and API with a sign-in redirect or a 401. | MVP |
| FR-006 | FA-1 | A signed-in user can sign out, and the app session ends. | MVP |
| FR-007 | FA-1 | The system stops honouring a removed group member's access no later than the current token's expiry, at most one hour. | MVP |
| FR-008 | FA-2 | A skill-builder user can create a build by supplying a skill name and a one-line description. | MVP |
| FR-009 | FA-2 | On create, the system writes the default skill structure: `SKILL.md` with frontmatter, a `verify.yaml` v2 stub, and `references/`, `templates/` and `examples/` folders. | MVP |
| FR-010 | FA-2 | A newly created skill passes tier-1 checks with no edits and reports its absent checks as a warning. | MVP |
| FR-011 | FA-2 | A user can clone an existing catalog skill into a build under a new name. | MVP |
| FR-012 | FA-2 | Clone copies the whole skill folder to the new name and rewrites `name:` in the frontmatter. | MVP |
| FR-013 | FA-2 | Clone leaves the source skill's files unchanged and creates no link back to the original. | MVP |
| FR-014 | FA-2 | Create and clone refuse a name that already exists on `main` or on another open build. | MVP |
| FR-015 | FA-2 | Create and clone refuse a name that does not follow `sdlc-<area>-<action>`. | MVP |
| FR-016 | FA-2 | The system creates each build on its own branch `build/<skill-name>` cut from `main`. | MVP |
| FR-017 | FA-2 | The system commits each save on a build and records the resulting commit SHA. | MVP |
| FR-018 | FA-2 | A user can open an existing catalog skill as an edit build on a branch. | MVP |
| FR-019 | FA-2 | The build page shows the build state (open, submitted, merged, abandoned), its head SHA and its commits. | MVP |
| FR-020 | FA-2 | A user can abandon an open build without changing `main` or the catalog. | MVP |
| FR-021 | FA-3 | A skill-builder user can create a test project, and the creator becomes its owner. | MVP |
| FR-022 | FA-3 | Only a project owner can add or remove project members. | MVP |
| FR-023 | FA-3 | Every project member can start runs in the project, and only the owner can change integrations. | MVP |
| FR-024 | FA-3 | A project owner can configure a Jira integration with site URL, project key or template project, and MCP server definition. | MVP |
| FR-025 | FA-3 | A project owner can configure a GitHub integration with sandbox repository, base branch, MCP server definition and access token. | MVP |
| FR-026 | FA-3 | A project owner can configure one or more AI model profiles with vendor, base URL, tier-to-model mapping and API key. | MVP |
| FR-027 | FA-3 | The system stores integration credentials in a secrets store and keeps only the secret reference in its database. | MVP |
| FR-028 | FA-3 | The system verifies an integration's settings and credentials and records when verification last succeeded. | MVP |
| FR-029 | FA-3 | The system warns when a GitHub integration points at a repository that a platform project also uses. | MVP |
| FR-030 | FA-3 | The system lists only the projects that the signed-in user is a member of. | MVP |
| FR-031 | FA-4 | A user can start a run by selecting a skills branch, an input branch, an optional context, a model profile and tier, and turn and spend caps. | MVP |
| FR-032 | FA-4 | The system resolves the selected skills branch to a commit SHA and records that SHA on the run. | MVP |
| FR-033 | FA-4 | The system packs the skill at that SHA into a content-addressed bundle and reuses the same bundle when the same SHA is run again. | MVP |
| FR-034 | FA-4 | The system uploads the bundle to the builder's own object storage and passes the container a presigned URL and checksum. | MVP |
| FR-035 | FA-4 | The system creates a new run branch `skilltest/<run-id>` from the input branch head and records that head SHA as the baseline. | MVP |
| FR-036 | FA-4 | A run never writes to its input branch. | MVP |
| FR-037 | FA-4 | The system launches the pinned agent image and records the agent image digest, stepkit version and verifier version on the run. | MVP |
| FR-038 | FA-4 | A user can follow run progress and agent logs while the run executes. | MVP |
| FR-039 | FA-4 | The system classifies the run outcome on exit using the same result statuses as the platform's reconciler. | MVP |
| FR-040 | FA-4 | The system enforces the run's turn and spend caps and stops the run when a cap is reached. | MVP |
| FR-041 | FA-4 | A user can choose an earlier run's output branch as the next run's input branch. | MVP |
| FR-042 | FA-4 | A user can supply optional reviewer feedback or upstream handoff context to test send-back and BLOCK behaviour. | MVP |
| FR-043 | FA-4 | The system refuses to start a run whose exact skill bundle has not passed the static security check. | MVP |
| FR-044 | FA-4 | The system records each run's actor, skill, SHAs, branches, model profile, tier, state and timestamps. | MVP |
| FR-045 | FA-4 | The system can seed Jira issues from a named fixture before a run and replace fixture aliases with real issue keys. | Later |
| FR-046 | FA-4 | The system records the Jira state after a run for display and assertions. | Later |
| FR-047 | FA-4 | The system cleans up seeded Jira issues after a run and sweeps leftovers nightly. | Later |
| FR-048 | FA-5 | After a run, the system runs the pinned verifier on the run branch outside the agent container. | MVP |
| FR-049 | FA-5 | Verification uses the baseline SHA for `must_change` and preconditions and the skill's `verify.yaml` from the pinned skills commit. | MVP |
| FR-050 | FA-5 | The run page shows the agent's claimed verdict, the final verdict after verification, and whether verification overturned the claim. | MVP |
| FR-051 | FA-5 | The run page shows each L0 and L1 check result, and L2 checks when enabled. | MVP |
| FR-052 | FA-5 | The system marks a build Ready at a SHA only when all four checks hold there: valid manifest, passing verified run, static security not `DO_NOT_INSTALL`, and LLM security completed or unavailable. | MVP |
| FR-053 | FA-5 | The build page shows the four Ready checks and their status at the head SHA. | MVP |
| FR-054 | FA-5 | A new commit on a build clears Ready until all four checks pass at the new SHA. | MVP |
| FR-055 | FA-5 | The build page keeps runs against earlier SHAs visible after Ready is cleared. | MVP |
| FR-056 | FA-5 | The system enables Submit to catalog only when all four Ready checks hold at the head SHA. | MVP |
| FR-057 | FA-5 | A user can re-verify an existing output branch against a new `verify.yaml` without launching an agent or spending model tokens. | MVP |
| FR-058 | FA-5 | Re-verify shows which checks flipped relative to the original run. | MVP |
| FR-059 | FA-5 | Before packing a skill, the system runs verifier lint and selftest and refuses to start the run if either fails. | MVP |
| FR-060 | FA-5 | The system refuses to run a skill when `catalog.yaml`'s `requires_verify` does not accept the pinned verifier version. | MVP |
| FR-061 | FA-6 | A user can trigger a static security scan from a skill page. | MVP |
| FR-062 | FA-6 | The system runs every security scan in the pinned scanner container, never in the app process, with the skill bundle mounted read-only. | MVP |
| FR-063 | FA-6 | The static scan runs with no network access. | MVP |
| FR-064 | FA-6 | The LLM scan receives the model key only as environment input and has network access only to the selected model endpoint. | MVP |
| FR-065 | FA-6 | Each scanner container has a 10-minute limit, and a timeout is recorded as a failed scan. | MVP |
| FR-066 | FA-6 | The system caches static scan results by skill content SHA. | MVP |
| FR-067 | FA-6 | The system refuses a run when the static scan returns `DO_NOT_INSTALL`, a CRITICAL finding, or incomplete coverage, and shows the findings. | MVP |
| FR-068 | FA-6 | An author cannot override a static-scan block, including with accepted findings. | MVP |
| FR-069 | FA-6 | The system queues an LLM scan only after the static scan passes for the same content SHA. | MVP |
| FR-070 | FA-6 | An LLM scan never blocks a run. | MVP |
| FR-071 | FA-6 | The author selects the model profile for an LLM scan, and only the project owner can change the default. | MVP |
| FR-072 | FA-6 | The Security tab shows the score, recommendation, each finding with severity, rule, file and line, and the model used for the LLM scan. | MVP |
| FR-073 | FA-6 | The system shows scan status (queued, running, complete, failed) on the skill and run pages. | MVP |
| FR-074 | FA-6 | The system does not run a scan automatically on save. | MVP |
| FR-075 | FA-7 | The run page shows the skill and skills SHA, input and output branches, image digest, stepkit version and verifier version. | MVP |
| FR-076 | FA-7 | The run page shows the diff from the input branch to the run branch. | MVP |
| FR-077 | FA-7 | The run page shows Jira changes, turns, tokens, cost and a trace link when available. | MVP |
| FR-078 | FA-7 | Skill history lists every run of one skill with SHA, input branch, verdict and check results. | Later |
| FR-079 | FA-7 | A user can compare two runs side by side with flipped checks highlighted. | Later |
| FR-080 | FA-7 | A user can re-run a previous run's inputs against the skills branch's latest SHA. | MVP |
| FR-081 | FA-7 | A user can save a named suite of runs and run it from the UI or CLI. | Later |
| FR-082 | FA-7 | The system persists runs and their artifacts across app restarts and retrieves them by run id. | MVP |
| FR-083 | FA-8 | The CLI can run one skill with the same pins as the app without starting the web app. | MVP |
| FR-084 | FA-8 | The CLI can run both security scan stages, with `--static-only` skipping the LLM stage. | MVP |
| FR-085 | FA-8 | The CLI exits with a clear pass/fail status suitable for CI. | MVP |
| FR-086 | FA-8 | The CLI scan starts the same scanner container as the app and requires Docker on the host. | MVP |
| FR-087 | FA-8 | A nightly CI job or a `run-behaviour` PR label can execute a saved suite. | Later |
| FR-088 | FA-9 | A Ready build can be submitted, opening a PR from `build/<skill-name>` to `main`. | MVP |
| FR-089 | FA-9 | The PR description lists the four Ready checks at the head SHA with links to the run and scan reports. | MVP |
| FR-090 | FA-9 | The system opens the PR with the submitting user's own GitHub identity. | MVP |
| FR-091 | FA-9 | After submission the system stores the PR URL and marks the build `submitted`. | MVP |
| FR-092 | FA-9 | The system marks a build `merged` when its PR merges and `abandoned` when the PR closes without merge. | Later |
| FR-093 | FA-9 | The system never writes to the platform or to project skills; submission is a pull request only. | MVP |
| FR-094 | FA-10 | The system pins one platform kit version and installs exactly the components its `kit.json` lists. | MVP |
| FR-095 | FA-10 | The system pulls the agent and scanner images from the platform registry by digest only. | MVP |
| FR-096 | FA-10 | The system refuses a run or scan when an image is supplied by tag or when the image and stepkit versions are declared incompatible. | MVP |
| FR-097 | FA-10 | The system records the kit version, image digests and component versions used for each run. | MVP |
| FR-098 | FA-10 | Updating an image, the verifier or the stepkit requires only a `kit.txt` version change in a PR. | MVP |
| FR-099 | FA-11 | The web app and database deploy together with docker-compose on a local machine or a single host. | MVP |
| FR-100 | FA-11 | The system initializes its database schema on deployment and preserves existing data on upgrade. | MVP |
| FR-101 | FA-12 | The system keeps its own records for users, builds, projects, members, integrations, bundles, runs, Jira state and suites. | MVP |
| FR-102 | FA-11 | The system stores run bundles, results, logs and transcripts under a per-run prefix in its own object-storage bucket. | MVP |
| FR-103 | FA-12 | The system exposes the REST APIs used by the web UI and CLI. | MVP |
| FR-104 | FA-11 | The system leaves the platform's data model, engine and UI unchanged. | MVP |
| FR-105 | FA-12 | The system serves the web UI and its REST APIs from the same application process. | MVP |

## 7. Non-Functional Requirements

| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Security/Privacy | Credential values never appear in the database, logs, run results or run pages; only secret references are persisted. | MVP |
| NFR-002 | Security | The builder's AWS role can read and write only `skill-builder/*` secrets and its own storage bucket, and read only the two platform image repositories. | MVP |
| NFR-003 | Security | Untrusted skill content is parsed only inside the scanner container, never in the app process. | MVP |
| NFR-004 | Integrity | Packing the same skills commit and skill twice yields the same bundle SHA, and every run and scan is bound to the exact SHA it evaluated. | MVP |
| NFR-005 | Integrity/Isolation | The builder never writes to the platform database, the catalog, project skills or a run's input branch. | MVP |
| NFR-006 | Fidelity | For the same inputs the builder and the platform produce the same scan verdict and the same `BB_CONTEXT`. | MVP |
| NFR-007 | Performance | A scan stage completes or fails within its 10-minute limit, and scans and runs execute asynchronously so the UI stays responsive. | MVP |
| NFR-008 | Performance | Re-verify completes without model calls and returns results in under 60 seconds for a typical skill. | MVP |
| NFR-009 | Operability | The whole app stack starts reproducibly with one docker-compose command on a single Docker host. | MVP |
| NFR-010 | Accessibility | The core authoring, run and result flows meet WCAG 2.1 AA and use the platform's visual theme. | MVP |
| NFR-011 | Auditability | Every run, scan and submission records the actor, exact SHAs, pinned versions and timestamp. | MVP |
| NFR-012 | Reliability | A run that is interrupted is recorded with a terminal state and never leaves its input branch modified. | MVP |

## 8. Constraints & Assumptions

- **Input basis.** The launch notes name a target Jira story, "SkillBuilder". On 2026-11-10 the
  configured Atlassian site was searched across all issue types for that summary and for
  "builder"; no matching issue exists, and the `BSB` (bheembhai-skill-builder) project contains no
  issues at all. No summary, description or acceptance criteria could therefore be fetched. As
  the launch notes direct, this PRD treats `docs/adr/SK-001-skill-builder.md` plus the notes as the
  authoritative product input; no story details were invented, and the Jira story is assumed to be
  created or linked later by the planning workflow.
- **Platform dependency.** The builder consumes the platform's shared runtime kit (platform
  ADR-033). Platform rollout S0 — extracting `bheembhai-stepkit` and publishing a `kit-v*`
  release — must ship before a run can execute; the builder pins one kit version.
- **Provisioned infrastructure.** The platform's Cognito User Pool exists, with a dedicated app
  client and the `skill-builders` group; a platform admin manages membership. The builder host
  has a Docker daemon, a read-only ECR identity for the two platform images, a Secrets Manager
  path `skill-builder/*`, its own S3 bucket, and an IAM role scoped to those resources.
- **Test-only data.** Jira tokens, GitHub tokens and model keys point at a test Jira site, a
  sandbox repository and test model access. The builder warns when a sandbox repository overlaps
  a platform project.
- **MVP boundary.** MVP corresponds to ADR rollout S1–S2 (runner, CLI, web app, Ready and
  submission). ADR rollout S3 (skill history, comparison, suites, nightly CI, Jira seeding and
  cleanup) is marked Later.
- **Stack.** Python and FastAPI, server-rendered HTML using the platform's theme, PostgreSQL or
  SQLite for a single host, and Docker as the container runtime.
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
- Which GitHub credential mode is used for the submission PR: a per-user fine-grained token, or a
  GitHub App that acts for the user? The requirement is that the author is the person, not the app.

---
*Generated by the `sdlc-plan-prd-write` skill. Next step: run `sdlc-plan-epics-create` to turn feature areas into Jira epics.*
