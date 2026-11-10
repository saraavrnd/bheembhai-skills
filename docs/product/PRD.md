# PRD — BheemBhai Skill Builder

**Status:** Draft · **Owner:** Saraav · **Last updated:** 2026-11-10

## 1. Problem & Opportunity

Skill authors cannot tell whether a platform skill behaves correctly in the real runtime before
it reaches the catalog. The catalog's static and example-based test tiers never execute a skill,
and testing inside the platform would require sandbox projects and draft catalogs that touch the
platform's data model, engine and UI. Authors need a fast, safe way to know how a skill will
behave against real Jira, GitHub and a model, and whether it is safe to propose, without
exposing the platform or its projects to test traffic. The opportunity is to close that gap.

## 2. Target Users

| User type | Primary need | Notes |
|-----------|--------------|-------|
| Skill author | Create, clone, run, scan, compare and propose skills against real integrations | Primary user; must belong to the skill-builders group |
| Skill builder project owner | Configure Jira, GitHub and model integrations; manage members and secrets | Owns the project's test setup; may also be an author |
| Platform administrator | Control who can use the skill builder by managing identity-provider group membership | External to the app; there is no in-app user administration screen |
| Catalog reviewer | Review a submission with evidence that the skill is ready | Consumes the pull request and its linked run and scan reports; not an app user |

## 3. Goals & Success Metrics

- G1 — Authors iterate on a skill in the real runtime without touching the platform.
  - Metric: 90 percent of authors complete a create-or-clone to passing-run loop in under 30 minutes on their first attempt.
- G2 — A Ready build carries trustworthy evidence.
  - Metric: 100 percent of submitted builds have all four Ready checks recorded at the head SHA, with a linked passing run and scan report.
- G3 — Runtime and scan behavior match the platform.
  - Metric: 100 percent of compatibility test bundles receive the same scan verdict and the same agent image digest as the platform, and the same context payload is built for the same workflow step.
- G4 — Secrets and platform data stay out of reach.
  - Metric: 0 secret values found in the database, logs, run results or pages across the security test suite, and 0 writes to platform systems.
- G5 — Runs are reliable and cheap to repeat.
  - Metric: 95 percent of started runs reach a terminal state without manual intervention, and Jira seeding plus cleanup adds no more than 60 seconds per run.

## 4. Scope

**In scope (MVP):** identity and group-gated access; test projects, membership and integrations;
create, clone and edit builds; the four Ready checks and Submit to catalog; bundle packing and
branch isolation; pinned agent launch and outcome classification; verification, re-verify and
re-run; static and LLM security scans; run pages, skill history and comparison; Jira fixture
seeding and cleanup; saved suites; CLI and nightly CI; REST API, database, object storage and
single-host deployment.

**Out of scope (Later / explicitly not now):** versioning inside the skill builder; writing to the
platform catalog or project skills; workflow orchestration with gates and routing; changes to the
platform data model, engine or UI; changing builtin verifier checks; mocked models or fake
Jira/GitHub by default; a fault-injecting MCP proxy; a fresh Jira project per run; a user
administration screen; deployment to ECS; automatic merging of catalog pull requests.

## 5. Feature Areas

| Area code | Feature area | One-line description |
|-----------|--------------|----------------------|
| FA-1 | Access and identity | Sign in through the platform identity provider with group-gated access and a local user record |
| FA-2 | Skill creation and cloning | Create a build from a name or clone an existing catalog skill under a new name |
| FA-3 | Build readiness and catalog submission | Show the four Ready checks and open the catalog pull request |
| FA-4 | Test projects and membership | Own projects, manage members and enforce project roles |
| FA-5 | Integrations and secrets | Configure Jira, GitHub and model integrations with secrets kept in the secret manager |
| FA-6 | Run setup and skill bundles | Configure a run, pack the skill and prepare isolated branches and context |
| FA-7 | Run execution and outcome | Launch the pinned agent, follow it and classify the result |
| FA-8 | Verification and re-runs | Grade output with the pinned verifier and support re-verify and re-run |
| FA-9 | Static security scanning | Block unsafe skills with the pinned static scanner before any run |
| FA-10 | LLM security scanning and findings | Run the non-blocking LLM scan and show its findings |
| FA-11 | Results, history and comparison | Run pages, skill history and side-by-side comparison |
| FA-12 | Jira test data and suites | Seed and clean Jira fixtures, and define and run saved suites |
| FA-13 | CLI and automation | Run the same runner from the command line and from CI |
| FA-14 | Server API, persistence and deployment | REST API, database, object storage, pinned kit and single-host operations |

## 6. Functional Requirements

| ID | Feature area | Requirement (one testable capability) | Release |
|------|--------------|----------------------------------------|---------|
| FR-001 | FA-1 | A user signs in with the platform identity provider using their existing platform username and password | MVP |
| FR-002 | FA-1 | The system refuses sign-in when the authenticated user is not a member of the skill-builders group | MVP |
| FR-003 | FA-1 | The system checks the skill-builders group claim on every authenticated request, not only at sign-in | MVP |
| FR-004 | FA-1 | On first successful sign-in, the system creates a local user record keyed by the identity provider subject identifier and stores the user's email and display name | MVP |
| FR-005 | FA-1 | The system ends the local session when the identity token expires | MVP |
| FR-006 | FA-1 | The system never reads or writes the platform database | MVP |
| FR-007 | FA-2 | A signed-in user creates a build by giving a skill name and a one-line description | MVP |
| FR-008 | FA-2 | On create, the system cuts the build branch build/<skill-name> from main and writes the default skill structure to skills/<skill-name>/ | MVP |
| FR-009 | FA-2 | The default structure contains SKILL.md, a verify.yaml stub, and references, templates and examples directories | MVP |
| FR-010 | FA-2 | A newly created build passes tier-1 manifest validation with no edits and reports that it has no checks | MVP |
| FR-011 | FA-2 | A user clones an existing catalog skill under a new name, and the system copies the source folder and rewrites the name field in the copied SKILL.md frontmatter | MVP |
| FR-012 | FA-2 | On clone, the source skill files remain unchanged | MVP |
| FR-013 | FA-2 | The system refuses a create or clone name that already exists on main or on another open build | MVP |
| FR-014 | FA-2 | The system refuses a skill name that does not match the sdlc-<area>-<action> pattern | MVP |
| FR-015 | FA-3 | The build page shows the four Ready checks at the build's head commit SHA | MVP |
| FR-016 | FA-3 | The build page shows the pass or fail state of each Ready check | MVP |
| FR-017 | FA-3 | A new commit on a build clears the build's Ready SHA | MVP |
| FR-018 | FA-3 | After a new commit, the system evaluates the four Ready checks at the new head SHA | MVP |
| FR-019 | FA-3 | Submit to catalog is enabled only when all four Ready checks pass at the head SHA | MVP |
| FR-020 | FA-3 | Submit to catalog opens a pull request from the build branch to main | MVP |
| FR-021 | FA-3 | The pull request description lists the four Ready checks at the head SHA and links the passing run and the scan reports | MVP |
| FR-022 | FA-3 | The pull request is opened with the submitting user's GitHub identity | MVP |
| FR-023 | FA-3 | A user opens an existing catalog skill on an edit branch and uses the same Ready and Submit flow | MVP |
| FR-024 | FA-3 | The build page shows the build state as open, submitted, merged or abandoned | MVP |
| FR-025 | FA-3 | Runs and scans recorded on a build remain visible after its Ready SHA is cleared | MVP |
| FR-026 | FA-4 | A signed-in user creates a test project and becomes its owner | MVP |
| FR-027 | FA-4 | The project owner adds a skill builder user to the project as a member and removes a member from the project | MVP |
| FR-028 | FA-4 | Any project member can start a run in the project | MVP |
| FR-029 | FA-4 | Only the project owner can change the project's integrations | MVP |
| FR-030 | FA-4 | The system denies project access to a user who is not a project member | MVP |
| FR-031 | FA-4 | A user lists the projects they own or belong to | MVP |
| FR-032 | FA-5 | The project owner configures a Jira integration with a site URL, a project key or template project, an MCP server definition and an API token | MVP |
| FR-033 | FA-5 | The project owner configures a GitHub integration with a sandbox repository, a base branch, an MCP server definition and a token scoped to the sandbox repository and to build branch and pull request operations | MVP |
| FR-034 | FA-5 | The project owner configures one or more AI model profiles with a vendor, base URL, tier-to-model mapping and API key | MVP |
| FR-035 | FA-5 | The system stores integration secret values in the secret manager and only the secret reference in its database | MVP |
| FR-036 | FA-5 | The system verifies an integration's settings and records the verification time on success | MVP |
| FR-037 | FA-5 | The system warns when a GitHub integration points at a repository that a platform project also uses | MVP |
| FR-038 | FA-5 | The project owner updates an integration's settings or stored secret and deletes an integration with its secret | MVP |
| FR-039 | FA-5 | The system never returns a secret value in an API response or renders it in the UI | MVP |
| FR-040 | FA-6 | A user starts a run by choosing a project, a skills branch, an input branch, an optional context, a model profile and a tier | MVP |
| FR-041 | FA-6 | At run start the system resolves the skills branch to a commit SHA and packs the skill at that SHA into a content-addressed bundle exactly as a catalog release would | MVP |
| FR-042 | FA-6 | The system reuses the stored bundle for the same skills commit SHA instead of repacking it | MVP |
| FR-043 | FA-6 | The system uploads the bundle to its own object storage and makes it available to the agent container with a SHA-256 checksum | MVP |
| FR-044 | FA-6 | The system creates the run branch skilltest/<run-id> from the input branch head and records that head SHA as the run baseline | MVP |
| FR-045 | FA-6 | A run never writes to its input branch | MVP |
| FR-046 | FA-6 | The system refuses to start a run when the skill fails verifier lint or selftest, or when requires_verify does not accept the pinned verifier version | MVP |
| FR-047 | FA-6 | A user optionally selects a workflow and step to supply context vocabulary and may supply reviewer feedback or an upstream handoff | MVP |
| FR-048 | FA-6 | A user selects the model profile and tier, defaulting to the skill's declared tier, and sets a turn cap and a spend cap | MVP |
| FR-049 | FA-7 | The system starts the pinned agent image for the run and supplies the platform's agent environment contract so the container can clone, run the skill, commit, push and upload its result | MVP |
| FR-050 | FA-7 | The system refuses to start a run when the pinned agent image digest and step-kit version are incompatible | MVP |
| FR-051 | FA-7 | The system follows progress and agent logs while the run executes and shows live run status in the UI | MVP |
| FR-052 | FA-7 | On container exit, the system classifies the run from the exit status and bb_step_result.json | MVP |
| FR-053 | FA-7 | The system records the verdict claimed by the agent and the pinned provenance of the run: skills commit SHA, agent image digest, step-kit version and verifier version | MVP |
| FR-054 | FA-7 | The system stops a run that reaches its turn cap | MVP |
| FR-055 | FA-7 | The system stops a run that reaches its spend cap | MVP |
| FR-056 | FA-7 | A completed run's output branch can be selected as the input branch of a later run | MVP |
| FR-057 | FA-8 | After every run, the system checks out the run branch and runs the pinned verifier outside the agent container, using the baseline SHA for must_change and precondition checks and the verify.yaml from the pinned skills commit | MVP |
| FR-058 | FA-8 | The system records the final verdict and each L0 and L1 check result, plus L2 results when L2 checks are enabled | MVP |
| FR-059 | FA-8 | The system shows the claimed verdict and the final verdict and marks whether the claim was overturned | MVP |
| FR-060 | FA-8 | Re-verify grades an existing output branch with a new verify.yaml | MVP |
| FR-061 | FA-8 | Re-verify calls no model, starts no agent and records which checks flipped versus the parent run | MVP |
| FR-062 | FA-8 | Re-run starts the same inputs against the skills branch's latest SHA and links the new record to a parent run | MVP |
| FR-063 | FA-9 | The system runs a static security scan with the pinned scanner image on the exact bundle before every run | MVP |
| FR-064 | FA-9 | The static scan runs in a short-lived container with a read-only bundle mount, an output mount for the report, no network access and a 10-minute limit | MVP |
| FR-065 | FA-9 | A static scan timeout is recorded as a failed scan | MVP |
| FR-066 | FA-9 | The system refuses a run when the static verdict is DO_NOT_INSTALL | MVP |
| FR-067 | FA-9 | The system refuses a run when the static scan reports a CRITICAL finding | MVP |
| FR-068 | FA-9 | The system refuses a run when the static scan coverage is incomplete | MVP |
| FR-069 | FA-9 | No override can clear a static scan block, and accepted findings cannot clear it | MVP |
| FR-070 | FA-9 | The system caches a static scan result by bundle content SHA and reuses it for the same content SHA | MVP |
| FR-071 | FA-9 | The Security check button triggers a static scan | MVP |
| FR-072 | FA-10 | The system queues the LLM scan only after the static check passes for the same content SHA | MVP |
| FR-073 | FA-10 | A run never waits for the LLM check, and the LLM check never blocks a run | MVP |
| FR-074 | FA-10 | The LLM check uses a model profile from the test project, and only the project owner can change the default model for LLM scans | MVP |
| FR-075 | FA-10 | The LLM scan container reaches only the configured model endpoint and has a 10-minute limit | MVP |
| FR-076 | FA-10 | The Security tab on the skill and run pages shows the scan score and recommendation and lists each finding with its severity, rule, file and line | MVP |
| FR-077 | FA-10 | The Security tab names the model used for the LLM check | MVP |
| FR-078 | FA-10 | The system never uses the scanner's MCP server mode | MVP |
| FR-079 | FA-11 | The run page shows the skill, skills SHA, input branch, output branch, agent image digest, step-kit version and verifier version | MVP |
| FR-080 | FA-11 | The run page shows the claimed verdict, final verdict, whether the claim was overturned and each L0 and L1 check, plus L2 checks when enabled | MVP |
| FR-081 | FA-11 | The run page shows the diff from the input branch to the output branch, the Jira changes, turns, tokens, cost and a trace link when tracing is enabled | MVP |
| FR-082 | FA-11 | The skill history lists every run of a skill with its SHA, input branch, verdict and checks | MVP |
| FR-083 | FA-11 | The compare view shows two runs side by side and highlights checks that flipped between them | MVP |
| FR-084 | FA-12 | Before a run, the runner seeds Jira issues from a named fixture file through the Jira REST API | MVP |
| FR-085 | FA-12 | The runner replaces fixture aliases with real issue keys at seed time and records the alias-to-key mapping for the run | MVP |
| FR-086 | FA-12 | The runner records the Jira state after the run | MVP |
| FR-087 | FA-12 | The runner cleans up seeded issues at the end of a run | MVP |
| FR-088 | FA-12 | A nightly sweep cleans up seeded issues left behind by failed runs | MVP |
| FR-089 | FA-12 | A user creates, edits, deletes and lists a saved suite as a named definition of runs with each run's skill, input branch, context and expectations | MVP |
| FR-090 | FA-12 | A user runs a saved suite from the UI and the system evaluates each expectation and reports pass or fail | MVP |
| FR-091 | FA-13 | The runner CLI starts a run with a project, skill, skills ref and input branch | MVP |
| FR-092 | FA-13 | The CLI writes the same run results to the database or a local folder as the web app does | MVP |
| FR-093 | FA-13 | The CLI scan-only mode runs both security stages without an agent run, and its static-only option skips the LLM stage | MVP |
| FR-094 | FA-13 | The CLI runs a saved suite by name and returns a non-zero exit code when a run fails or a scan blocks | MVP |
| FR-095 | FA-13 | A CI job runs a saved suite nightly through the CLI | MVP |
| FR-096 | FA-13 | The CLI runs without the web app | MVP |
| FR-097 | FA-14 | The server exposes a REST API covering projects, integrations, builds, runs, scans, results and suites | MVP |
| FR-098 | FA-14 | The web UI and CLI expose the same operations and return the same results | MVP |
| FR-099 | FA-14 | The REST API returns JSON with a structured error body for invalid input | MVP |
| FR-100 | FA-14 | The REST API validates the identity token and the skill-builders group claim on every endpoint | MVP |
| FR-101 | FA-14 | The REST API enforces project membership and owner-only integration changes | MVP |
| FR-102 | FA-14 | The system persists users, builds, projects, members, integrations, bundles, runs, Jira run data and suites in its own database | MVP |
| FR-103 | FA-14 | The system stores run artifacts under a per-run object-storage prefix | MVP |
| FR-104 | FA-14 | The system pins exactly one platform kit version for all shared platform parts | MVP |
| FR-105 | FA-14 | The system installs only the package versions and image digests listed by the pinned kit | MVP |
| FR-106 | FA-14 | The system pulls agent and scanner images by digest and refuses a tag reference | MVP |
| FR-107 | FA-14 | The system exposes health and readiness endpoints for the app, database and container runtime | MVP |
| FR-108 | FA-14 | The app and database deploy reproducibly on a single Docker host | MVP |
| FR-109 | FA-14 | The system records the creator and timestamps for each build, project and run | MVP |

## 7. Non-Functional Requirements

| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Performance | A run start request is acknowledged and persisted within 10 seconds, excluding agent execution | MVP |
| NFR-002 | Performance | The run page shows status no more than 15 seconds stale while a run executes | MVP |
| NFR-003 | Performance | A skill's history page loads in under 3 seconds with 200 recorded runs | MVP |
| NFR-004 | Security | Every authenticated request validates the identity token and the skill-builders group claim before any action | MVP |
| NFR-005 | Security | Secret values never appear in database rows, logs, run results, error messages or rendered pages | MVP |
| NFR-006 | Security | The static scan container has no network access, and the LLM scan container reaches only the configured model endpoint | MVP |
| NFR-007 | Security | The application's cloud identity can read and write only skill-builder secrets and its own object-storage bucket | MVP |
| NFR-008 | Security | Agent and scanner images are always referenced by digest, never by tag | MVP |
| NFR-009 | Privacy | The skill builder stores only its own data and performs no writes to the platform or its catalog | MVP |
| NFR-010 | Reliability | Every started run reaches a terminal state of pass, fail, error or cancelled within its configured limits | MVP |
| NFR-011 | Reliability | A scan container that exceeds 10 minutes is stopped and recorded as a failed scan | MVP |
| NFR-012 | Operability | The app and database start reproducibly with one command on a single host | MVP |
| NFR-013 | Operability | Health and readiness endpoints report the app, database and container runtime status | MVP |
| NFR-014 | Auditability | Every run records its skills SHA, agent image digest, step-kit version and verifier version | MVP |
| NFR-015 | Accessibility | The web UI meets WCAG 2.1 AA | MVP |
| NFR-016 | Compliance | Only test Jira sites, sandbox repositories and test model keys are used, and production credentials are out of scope | MVP |
| NFR-017 | Scalability | The system supports at least five concurrent runs on one Docker host | MVP |

## 8. Constraints & Assumptions

**Product source.** This PRD is derived from ADR SK-001, "Skill builder — create, test, scan and
ready platform skills" (`docs/adr/SK-001-skill-builder.md`, status Proposed, 2026-11-02, decider
Saraav), plus the launch note that the deliverable is the skill builder as an app with a UI, server
side REST APIs and a database.

**Jira story.** At the time of writing, no issue titled "SkillBuilder" exists in any accessible
Jira project (BEEM, BSB, EX, GRAP, LNPRTL). The `BSB` project named `bheembhai-skill-builder`
exists but contains no issues, so no issue-level summary, description or acceptance criteria were
available. This PRD treats ADR SK-001 and the launch note as the authoritative input and records
the gap in Open Questions rather than inventing story details.

**External prerequisites (out of scope to build here).**
- The platform identity provider, its app client and the `skill-builders` group. A platform
  administrator provisions the group and manages membership; the app has no user admin screen.
- The platform kit release (`kit-v*`) containing `bheembhai-verify` and `bheembhai-stepkit`, and
  the agent and scanner image builds published to the platform registry.
- The cloud account resources: the object-storage bucket, the `skill-builder/*` secret path and
  the IAM role that permits only those resources.
- The sandbox GitHub repository and its curated input branches, the Jira test site, the fixture
  files, the submitting user's GitHub identity and the model vendor keys.

**Assumptions made where the ADR leaves a choice open.**
- A1 — v1 runs on one Docker host (laptop or single EC2 instance). ECS is Later.
- A2 — Verification stays in the skill builder for v1. Moving it into the agent image is Later.
- A3 — Jira isolation uses one dedicated test project per skill-builder project, with a
  `skilltest-<run-id>` label on every seeded issue, cleaned up per run and by a nightly sweep. A
  fresh Jira project per run is Later.
- A4 — The step kit ships as one package. Splitting auth and secrets helpers is a platform
  decision and does not change this PRD.
- A5 — LLM scanning is on demand and non-blocking; there is no human-review step in the skill
  builder.
- A6 — The deployment is single-tenant for the platform team; per-customer tenancy is out of
  scope.
- A7 — Only test credentials are used. Production Jira, GitHub and model credentials are out of
  scope.
- A8 — The numeric targets in Goals are product targets to validate in the pilot, not measured
  baselines.

**Product contract names.** This is an internal developer tool, so some requirements name the
platform artifacts an author works with, such as `verify.yaml`, the step kit, the pinned kit and
image digests. Those names are part of the user-visible contract, not implementation choices.

**Ready definition.** A build is Ready at a commit SHA when four checks hold at that SHA: the
manifest is valid under tier-1 verifier checks, at least one run has a final verdict of pass after
verification, the static security check is not DO_NOT_INSTALL, and the LLM security check has
completed or is recorded as unavailable.

**Skills repository CI.** The existing CI static check on pull requests in `bheembhai-skills`
stays in place and must use the same pinned scanner image as the app. It is repo CI, not an app
feature, and is not enumerated as a functional requirement here.

**Stack and placement constraints from the ADR.** Python, FastAPI, server-rendered HTML with the
platform theme, PostgreSQL or SQLite for a single host, and Docker as the container runtime. The
app lives under `skill-builder/` in `bheembhai-skills`, with `app/`, `runner/`, `kit.txt` and
`docker-compose.yml`. `tools/build.py` packs only `skills/`, `config/` and `catalog.yaml`, so the
skill builder never enters a catalog release. The pinned kit version is recorded in
`skill-builder/kit.txt` and the exact parts are listed in its `kit.json`.

## 9. Open Questions

- Where is the Jira story "SkillBuilder"? No such issue was found in any accessible project.
  Confirm the story and its acceptance criteria and reconcile them with this PRD.
- Confirm the Jira isolation choice in A3: one test project plus per-run labels, or a fresh Jira
  project per run.
- Confirm A2: does verification stay in the skill builder for v1, or move into the agent image
  once that path exists?
- Confirm the v1 deployment target in A1: one Docker host, a dedicated EC2 host, or ECS.
- Confirm whether the step kit ships as one package or as separate auth and secrets packages.
- What retention period applies to run artifacts, logs and transcripts? The ADR does not specify
  one.
- What concurrency target should replace the five-run assumption in NFR-017 after the pilot host
  is sized?
- Should Langfuse traces go to a separate project or carry `env = skilltest` in the existing
  project?

---

*Generated by the `sdlc-plan-prd-write` skill. Next step: run `sdlc-plan-epics-create` to turn feature areas into Jira epics.*
