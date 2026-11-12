# PRD — BheemBhai Skill Builder

**Status:** Draft · **Owner:** Saraav · **Last updated:** 2026-11-12

## 1. Problem & Opportunity

Skill authors cannot tell whether a platform skill behaves correctly in the real runtime before it
reaches the catalog. The catalog's two existing test tiers are static: one checks the catalog's
shape and the other self-tests the verifier on examples, so neither ever executes a skill against
real Jira, GitHub and a model. Testing a draft inside the platform would mean sandbox projects,
draft catalogs and per-project drafts, which would touch the platform's data model, engine and UI
and would expose real projects to test traffic. Authors therefore discover defects, unsafe skills
and mis-graded outputs late — after review and release effort has already been spent. The
opportunity is to let an author validate a skill against realistic test data before it reaches
review, so defects, unsafe skills and mis-graded outputs are caught while the change is still
cheap.

## 2. Target Users

| User type | Primary need | Notes |
|-----------|--------------|-------|
| Skill author | Create or clone a skill, run it against realistic test data, inspect the verdict and security findings, fix it, and propose it | Primary user; must belong to the `skill-builders` group; spends model tokens and writes build branches |
| Skill builder project owner | Configure the test project's Jira, GitHub and model integrations, manage members, and keep credentials test-only | A skill author who owns that project; only the owner changes integrations |
| Platform administrator | Control who may use the skill builder by managing identity-provider group membership and by provisioning platform resources | External to the app; there is no in-app user-administration screen |
| Catalog reviewer | Judge a submitted pull request from the Ready checks and the linked run and scan evidence | Consumes the pull request; reviews with CODEOWNERS; not an app user |
| Builder operator | Run the host and provision the identity provider, image registry, secret store, object storage and cloud permissions | Needs a container runtime on the host |

## 3. Goals & Success Metrics

- G1 — Authors validate a skill end to end without touching platform projects or production credentials.
  - Metric: 100% of validation runs use only the test integrations configured on their project.
- G2 — The skill builder and the platform reach the same runtime judgement.
  - Metric: 0 verdict mismatches for agent image digest, rendered step context and scan outcome across a paired set of at least 20 skill bundles.
- G3 — Iteration is cheap.
  - Metric: a re-verification uses 0 model tokens and 0 agent runs.
- G4 — Test data and secrets are safe by construction.
  - Metric: 0 writes to an input branch, 0 secret values disclosed in records, logs or pages, and 0 writes to platform systems across the security test suite.
- G5 — Unsafe skills are stopped before they run.
  - Metric: 100% of bundles with a DO_NOT_INSTALL or CRITICAL static result are blocked from starting a run.
- G6 — A Ready build carries complete evidence to review.
  - Metric: 100% of catalog pull requests opened by the skill builder link all four Ready check results at the submitted commit.
- G7 — The pilot replaces the ad-hoc local loop.
  - Metric: at least 10 skills authored in the first month, and at least 50% of Ready builds submitted and merged.

## 4. Scope

**In scope (MVP):** identity and group-gated access; a server-rendered web UI with a dashboard and
navigation; test projects, membership and integrations; create, clone and edit builds; the four
Ready checks and Submit to catalog; content-addressed bundle packing and branch isolation; pinned
agent launch and outcome classification; verification, re-run and re-verify; static and advisory
LLM security scans; the run page; the runner CLI for run and scan; a server-side REST API; the
skill builder's own relational database and object storage; single-host deployment.

**Planned for later releases:** skill run history; side-by-side run comparison; saved suites and
nightly or pull-request-triggered suite runs; Jira fixture seeding, state capture and cleanup;
retention and deletion administration.

**Out of scope (Later / explicitly not now):** versioning inside the skill builder, where a build
is a branch and versions begin at the catalog release; skills that live only in a project; any
change to the platform's data model, engine or UI; writing to the platform catalog or to
project-owned skills; changing builtin verifier checks, which is a verifier release; running
multi-step workflows with gates and routing; mocked models or a fake Jira or GitHub by default; a
fault-injecting MCP proxy; a fresh Jira project per run; a user-administration screen; deployment
to a managed container service; automatic merging of catalog pull requests; and in-app management
of identity-provider group membership.

## 5. Feature Areas

| Area code | Feature area | One-line description |
|-----------|--------------|----------------------|
| FA-1 | Skill builder | A separate authoring and validation system in which an authorised skill author creates or clones a skill, runs it in the platform runtime against test integrations, reads the verdict and security findings, and proposes a proven skill for catalog review |

The product is one feature area. For decomposition, the capability groups below are the proposed
epic boundaries; every functional requirement in section 6 names its capability group.

| Group | Capability group | One-line description |
|-------|------------------|----------------------|
| G-1 | Access and identity | Sign in through the platform identity provider with group-gated access and a local user record |
| G-2 | Build creation and cloning | Create a build from a name, clone an existing catalog skill, or open one for edit |
| G-3 | Build lifecycle and readiness | Track build state and head commit, and evaluate the four Ready checks at that commit |
| G-4 | Catalog submission | Turn a Ready build into a reviewed catalog pull request with evidence |
| G-5 | Test projects and membership | Own projects, manage members and enforce project roles |
| G-6 | Integrations and secrets | Configure Jira, GitHub and AI-model integrations with secrets kept in the secret manager |
| G-7 | Run configuration and skill bundles | Configure a run, pack the skill and prepare isolated branches and context |
| G-8 | Run execution and outcome | Launch the pinned agent, follow progress, and classify the result |
| G-9 | Verification, re-run and re-verify | Grade output with the pinned verifier and support re-run and re-verify |
| G-10 | Static security scanning | Block unsafe skills with the pinned static scanner before any run |
| G-11 | LLM security scanning and reporting | Run the advisory LLM scan and present a combined security view |
| G-12 | Run results, history and comparison | Show run evidence, skill history and side-by-side comparison |
| G-13 | Jira test data and saved suites | Seed and clean Jira fixtures, and define and run saved suites |
| G-14 | CLI and nightly automation | Run and scan from the command line and drive suites from CI |
| G-15 | Server REST API | Expose every app operation through a versioned server-side API |
| G-16 | Web application shell and navigation | Give the user a dashboard, navigation and clear empty and error states |
| G-17 | Persistence, storage and runtime pinning | Persist the app's own data, store artifacts, and pin one platform kit |
| G-18 | Deployment and operations | Deploy the app and database reproducibly on one host with health reporting |

## 6. Functional Requirements — one testable capability per row; columns are ID, feature area, requirement, release and capability group
| FR-001 | FA-1 | A user signs in with their existing platform identity-provider account | MVP | G-1 |
|--------|--------------|--------|---------|------------------|
| FR-002 | FA-1 | The system refuses sign-in when the authenticated user is not a member of the skill-builders group | MVP | G-1 |
| FR-003 | FA-1 | The system checks the skill-builders group claim on every authenticated request, not only at sign-in | MVP | G-1 |
| FR-004 | FA-1 | On first successful sign-in the system creates a local user record keyed by the identity-provider subject identifier | MVP | G-1 |
| FR-005 | FA-1 | The local user record stores the user's email address and display name | MVP | G-1 |
| FR-006 | FA-1 | The system ends the local session when the identity token expires | MVP | G-1 |
| FR-007 | FA-1 | The system ends the local session when the user signs out | MVP | G-1 |
| FR-008 | FA-1 | The system provides no in-app user-administration screen | MVP | G-1 |
| FR-009 | FA-1 | The system never reads or writes the platform database | MVP | G-1 |
| FR-010 | FA-1 | A signed-in user creates a build by supplying a unique skill name and a one-line description | MVP | G-2 |
| FR-011 | FA-1 | On create the system cuts a build branch from main whose name is build/ followed by the skill name | MVP | G-2 |
| FR-012 | FA-1 | On create the system writes the default skill structure for the new skill | MVP | G-2 |
| FR-013 | FA-1 | The default skill structure contains a SKILL.md, a verify.yaml stub, a references README, and empty templates and examples directories | MVP | G-2 |
| FR-014 | FA-1 | A newly created build passes tier-1 manifest validation with a no-checks-yet warning and no errors | MVP | G-2 |
| FR-015 | FA-1 | A user clones an existing catalog skill into a new build under a new name | MVP | G-2 |
| FR-016 | FA-1 | Clone copies the complete skill folder into the new build | MVP | G-2 |
| FR-017 | FA-1 | Clone rewrites the name field in the copied SKILL.md frontmatter to the new name | MVP | G-2 |
| FR-018 | FA-1 | Clone leaves the source skill's files unchanged | MVP | G-2 |
| FR-019 | FA-1 | A cloned skill has no link back to the source skill | MVP | G-2 |
| FR-020 | FA-1 | The system rejects a create or clone name that already exists on the main branch | MVP | G-2 |
| FR-021 | FA-1 | The system rejects a create or clone name that another open build already uses | MVP | G-2 |
| FR-022 | FA-1 | The system rejects a skill name that does not follow the sdlc- prefix plus area and action pattern | MVP | G-2 |
| FR-023 | FA-1 | A user opens an existing catalog skill as an edit build on a branch cut from main | MVP | G-3 |
| FR-024 | FA-1 | The system records each build's kind as create, clone or edit | MVP | G-3 |
| FR-025 | FA-1 | The system records each build's current head commit SHA | MVP | G-3 |
| FR-026 | FA-1 | A user views a list of builds showing each build's skill, kind, state and owner | MVP | G-3 |
| FR-027 | FA-1 | A user abandons an open build and the build state becomes abandoned | MVP | G-3 |
| FR-028 | FA-1 | The build state is one of open, submitted, merged or abandoned | MVP | G-3 |
| FR-029 | FA-1 | The build page shows the four Ready checks at the build's head commit SHA | MVP | G-3 |
| FR-030 | FA-1 | The build page shows the pass or fail state of each Ready check | MVP | G-3 |
| FR-031 | FA-1 | A build is Ready only when all four Ready checks hold at the same head commit SHA | MVP | G-3 |
| FR-032 | FA-1 | The manifest-valid Ready check is satisfied when tier-1 manifest validation passes at the build's head commit SHA | MVP | G-3 |
| FR-033 | FA-1 | The passing-run Ready check is satisfied when at least one run of the build has a final verdict of pass at the head commit SHA | MVP | G-3 |
| FR-034 | FA-1 | The static-security Ready check is satisfied when the static scan of the build bundle at the head commit SHA is not DO_NOT_INSTALL | MVP | G-3 |
| FR-035 | FA-1 | The LLM-security Ready check is satisfied when the LLM scan has completed or is recorded as unavailable for the bundle at the head commit SHA | MVP | G-3 |
| FR-036 | FA-1 | A new commit clears Ready until all four Ready checks pass again at the new head commit SHA | MVP | G-3 |
| FR-037 | FA-1 | Runs and scans recorded on a build remain visible after its Ready state is cleared | MVP | G-3 |
| FR-038 | FA-1 | The build page shows the commit SHA at which the build last became Ready | MVP | G-3 |
| FR-039 | FA-1 | Submit to catalog is enabled only while the build is Ready | MVP | G-4 |
| FR-040 | FA-1 | Submit to catalog opens a pull request from the build branch to the main branch | MVP | G-4 |
| FR-041 | FA-1 | Submitting a build moves it to the submitted state | MVP | G-4 |
| FR-042 | FA-1 | The pull request description lists the four Ready check results at the submitted commit | MVP | G-4 |
| FR-043 | FA-1 | The pull request description links the passing run and the static and LLM security reports | MVP | G-4 |
| FR-044 | FA-1 | The pull request is opened under the submitting user's GitHub identity | MVP | G-4 |
| FR-045 | FA-1 | The system marks a submitted build as merged when its pull request is merged | MVP | G-4 |
| FR-046 | FA-1 | The build page links the submission pull request after submission | MVP | G-4 |
| FR-047 | FA-1 | A signed-in user creates a test project by supplying a name | MVP | G-5 |
| FR-048 | FA-1 | The creator of a test project is recorded as its owner | MVP | G-5 |
| FR-049 | FA-1 | A project owner adds a skill builder user to the project as a member | MVP | G-5 |
| FR-050 | FA-1 | A project owner removes a member from the project | MVP | G-5 |
| FR-051 | FA-1 | A project owner views the project's member list with each member's role | MVP | G-5 |
| FR-052 | FA-1 | Any project member can start a run in the project | MVP | G-5 |
| FR-053 | FA-1 | Only the project owner can change the project's integrations | MVP | G-5 |
| FR-054 | FA-1 | The system denies project access to a user who is not a project member | MVP | G-5 |
| FR-055 | FA-1 | A user lists the projects they own or belong to | MVP | G-5 |
| FR-056 | FA-1 | The project owner configures a Jira integration with a site URL, a project key or template project, an MCP server definition and an API token | MVP | G-6 |
| FR-057 | FA-1 | The project owner configures a GitHub integration with a sandbox repository, a base branch, an MCP server definition and an access token | MVP | G-6 |
| FR-058 | FA-1 | The system validates that a GitHub integration token can push build branches and open pull requests in the skills repository | MVP | G-6 |
| FR-059 | FA-1 | The project owner configures an AI model profile with a vendor, a base URL, a tier-to-model mapping and an API key | MVP | G-6 |
| FR-060 | FA-1 | The project owner configures more than one AI model profile in a project | MVP | G-6 |
| FR-061 | FA-1 | The project owner designates one model profile as the default for LLM security scans | MVP | G-6 |
| FR-062 | FA-1 | The system stores integration secret values in the external secret manager | MVP | G-6 |
| FR-063 | FA-1 | The system stores only the secret reference in its database | MVP | G-6 |
| FR-064 | FA-1 | The system verifies an integration's settings and records the verification time on success | MVP | G-6 |
| FR-065 | FA-1 | The system shows each integration's verification status and time in the UI | MVP | G-6 |
| FR-066 | FA-1 | The system warns when a GitHub integration points at a repository that a platform project also uses | MVP | G-6 |
| FR-067 | FA-1 | The project owner updates an integration's settings | MVP | G-6 |
| FR-068 | FA-1 | The project owner replaces an integration's stored secret | MVP | G-6 |
| FR-069 | FA-1 | The project owner deletes an integration and its stored secret | MVP | G-6 |
| FR-070 | FA-1 | The system never returns a secret value in an API response or renders one in the UI | MVP | G-6 |
| FR-071 | FA-1 | A user starts a run by choosing a project, a skills branch and an input branch | MVP | G-7 |
| FR-072 | FA-1 | A user optionally supplies run context for a run from a workflow step, reviewer feedback, or an upstream handoff | MVP | G-7 |
| FR-073 | FA-1 | A user selects a model profile and tier, defaulting to the skill's declared tier | MVP | G-7 |
| FR-074 | FA-1 | A user sets a turn cap and a spend cap for the run | MVP | G-7 |
| FR-075 | FA-1 | At run start the system resolves the skills branch to a commit SHA and records that SHA on the run | MVP | G-7 |
| FR-076 | FA-1 | The run form shows the resolved skills commit SHA before the user confirms | MVP | G-7 |
| FR-077 | FA-1 | The system packs the skill at that SHA into a content-addressed bundle exactly as a catalog release would | MVP | G-7 |
| FR-078 | FA-1 | The system reuses the stored bundle for the same skills commit SHA instead of packing it again | MVP | G-7 |
| FR-079 | FA-1 | The system uploads the bundle to its own object storage | MVP | G-7 |
| FR-080 | FA-1 | The system gives the agent run a time-limited bundle URL and the bundle SHA-256 checksum | MVP | G-7 |
| FR-081 | FA-1 | The system creates the run branch from the input branch head and records that head SHA as the run baseline | MVP | G-7 |
| FR-082 | FA-1 | A run never writes to its input branch | MVP | G-7 |
| FR-083 | FA-1 | The system refuses to start a run when the skill fails verifier lint or selftest | MVP | G-7 |
| FR-084 | FA-1 | The system refuses to start a run when the catalog's verifier requirement does not accept the pinned verifier version | MVP | G-7 |
| FR-085 | FA-1 | The system refuses to start a run when the selected input branch does not exist | MVP | G-7 |
| FR-086 | FA-1 | The system starts the run in the pinned agent image with the platform's agent environment contract | MVP | G-8 |
| FR-087 | FA-1 | The system supplies integration secrets to the agent run only at start | MVP | G-8 |
| FR-088 | FA-1 | The system refuses to start a run when the pinned agent image digest and step-kit version are incompatible | MVP | G-8 |
| FR-089 | FA-1 | The system follows the run's progress and agent log while the run executes | MVP | G-8 |
| FR-090 | FA-1 | The system shows live run status in the UI while the run executes | MVP | G-8 |
| FR-091 | FA-1 | On run exit the system classifies the run from the exit status and the step result file | MVP | G-8 |
| FR-092 | FA-1 | The system records the verdict claimed by the agent | MVP | G-8 |
| FR-093 | FA-1 | The system records each run's skills commit SHA, agent image digest, step-kit version and verifier version | MVP | G-8 |
| FR-094 | FA-1 | The system stops a run that reaches its turn cap | MVP | G-8 |
| FR-095 | FA-1 | The system stops a run that reaches its spend cap | MVP | G-8 |
| FR-096 | FA-1 | A user cancels a running run | MVP | G-8 |
| FR-097 | FA-1 | A completed run's output branch can be selected as the input branch of a later run | MVP | G-8 |
| FR-098 | FA-1 | After every run the system runs the pinned verifier outside the agent run against the output branch | MVP | G-9 |
| FR-099 | FA-1 | Verification uses the run's recorded baseline SHA for must-change and precondition checks | MVP | G-9 |
| FR-100 | FA-1 | Verification uses the verify.yaml from the run's pinned skills commit | MVP | G-9 |
| FR-101 | FA-1 | The system records the final verdict after verification | MVP | G-9 |
| FR-102 | FA-1 | The system records each L0 and L1 check result, and L2 results when L2 checks are enabled | MVP | G-9 |
| FR-103 | FA-1 | The system shows the claimed verdict and the final verdict | MVP | G-9 |
| FR-104 | FA-1 | The system marks whether the agent's claimed verdict was overturned by verification | MVP | G-9 |
| FR-105 | FA-1 | Re-verify grades an existing output branch with a newer verify.yaml | MVP | G-9 |
| FR-106 | FA-1 | Re-verify calls no model and starts no agent | MVP | G-9 |
| FR-107 | FA-1 | Re-verify records which checks flipped against the parent run | MVP | G-9 |
| FR-108 | FA-1 | Re-run starts the same run inputs against the skills branch latest commit SHA | MVP | G-9 |
| FR-109 | FA-1 | Re-run links the new run to the run it was started from | MVP | G-9 |
| FR-110 | FA-1 | The system runs a static security scan with the pinned scanner image on the exact bundle before every run | MVP | G-10 |
| FR-111 | FA-1 | The static scan reads the bundle read-only and writes its report outside the bundle | MVP | G-10 |
| FR-112 | FA-1 | The static scan runs with no network access | MVP | G-10 |
| FR-113 | FA-1 | Each static scan is limited to 10 minutes | MVP | G-10 |
| FR-114 | FA-1 | A static scan that exceeds 10 minutes is recorded as a failed scan | MVP | G-10 |
| FR-115 | FA-1 | The system refuses a run when the static verdict is DO_NOT_INSTALL | MVP | G-10 |
| FR-116 | FA-1 | The system refuses a run when the static scan reports a CRITICAL finding | MVP | G-10 |
| FR-117 | FA-1 | The system refuses a run when the static scan reports incomplete coverage | MVP | G-10 |
| FR-118 | FA-1 | No override can clear a static scan block | MVP | G-10 |
| FR-119 | FA-1 | An accepted finding cannot clear a static scan block | MVP | G-10 |
| FR-120 | FA-1 | The system caches a static scan result by bundle content SHA and reuses it for the same content SHA | MVP | G-10 |
| FR-121 | FA-1 | The Security check action on a skill triggers a static scan | MVP | G-10 |
| FR-122 | FA-1 | The system records each static scan with its bundle content SHA and scanner image digest | MVP | G-10 |
| FR-123 | FA-1 | The system never uses the scanner's MCP server mode | MVP | G-10 |
| FR-124 | FA-1 | The system shows each static finding with its severity, rule, file and line | MVP | G-10 |
| FR-125 | FA-1 | The system queues the LLM security scan only after the static scan passes for the same content SHA | MVP | G-11 |
| FR-126 | FA-1 | The LLM security scan runs only from the Security check action, never from a run | MVP | G-11 |
| FR-127 | FA-1 | A run never waits for the LLM security scan | MVP | G-11 |
| FR-128 | FA-1 | LLM security findings never block a run | MVP | G-11 |
| FR-129 | FA-1 | The LLM security scan uses the project's default model profile | MVP | G-11 |
| FR-130 | FA-1 | The LLM scan can reach only the configured model endpoint | MVP | G-11 |
| FR-131 | FA-1 | Each LLM scan is limited to 10 minutes | MVP | G-11 |
| FR-132 | FA-1 | An LLM scan that exceeds 10 minutes is recorded as a failed scan | MVP | G-11 |
| FR-133 | FA-1 | The system records the LLM check as unavailable when no model profile can run it | MVP | G-11 |
| FR-134 | FA-1 | The Security tab shows the scan score and recommendation | MVP | G-11 |
| FR-135 | FA-1 | The Security tab presents the static and LLM results as separate checks | MVP | G-11 |
| FR-136 | FA-1 | The Security tab names the model used for the LLM check | MVP | G-11 |
| FR-137 | FA-1 | The run page shows the skill, skills commit SHA and input and output branches | MVP | G-12 |
| FR-138 | FA-1 | The run page shows the agent image digest, step-kit version and verifier version | MVP | G-12 |
| FR-139 | FA-1 | The run page shows the claimed verdict, final verdict and whether the claim was overturned | MVP | G-12 |
| FR-140 | FA-1 | The run page shows each L0 and L1 check, and L2 checks when enabled | MVP | G-12 |
| FR-141 | FA-1 | The run page shows the diff from the input branch to the output branch | MVP | G-12 |
| FR-142 | FA-1 | The run page shows the Jira changes recorded for the run | Later | G-12 |
| FR-143 | FA-1 | The run page shows turns, tokens, cost and a trace link when tracing is enabled | MVP | G-12 |
| FR-144 | FA-1 | The run page provides the agent log and the transcript | MVP | G-12 |
| FR-145 | FA-1 | The skill history lists every run of a skill with its commit, input branch, verdict and checks | Later | G-12 |
| FR-146 | FA-1 | The compare view shows two runs side by side and highlights checks that flipped between them | Later | G-12 |
| FR-147 | FA-1 | Before a run the runner seeds Jira issues from a named fixture file through the Jira REST API | Later | G-13 |
| FR-148 | FA-1 | The runner replaces fixture aliases with the real Jira issue keys at seed time | Later | G-13 |
| FR-149 | FA-1 | The runner records the alias-to-key mapping for the run | Later | G-13 |
| FR-150 | FA-1 | Seeds issues carry a run-specific test label | Later | G-13 |
| FR-151 | FA-1 | The runner records the Jira state after the run | Later | G-13 |
| FR-152 | FA-1 | The runner cleans up the Jira issues it seeded at the end of a run | Later | G-13 |
| FR-153 | FA-1 | A nightly sweep cleans up Jira issues left behind by failed runs | Later | G-13 |
| FR-154 | FA-1 | The runner refuses to start a run when fixture seeding fails | Later | G-13 |
| FR-155 | FA-1 | A user creates a saved suite as a named definition of runs with each run's skill, input branch, context and expectations | Later | G-13 |
| FR-156 | FA-1 | A user edits a saved suite | Later | G-13 |
| FR-157 | FA-1 | A user deletes a saved suite | Later | G-13 |
| FR-158 | FA-1 | A user lists saved suites | Later | G-13 |
| FR-159 | FA-1 | A user runs a saved suite from the UI and the system reports each expectation as pass or fail | Later | G-13 |
| FR-160 | FA-1 | The runner CLI starts a run with a project, skill, skills ref and input branch | MVP | G-14 |
| FR-161 | FA-1 | The CLI writes the same run results to the database or a local folder as the web app does | MVP | G-14 |
| FR-162 | FA-1 | The CLI scan-only mode runs both security stages without an agent run | MVP | G-14 |
| FR-163 | FA-1 | The CLI static-only option skips the LLM scan stage | MVP | G-14 |
| FR-164 | FA-1 | The CLI runs a saved suite by name | Later | G-14 |
| FR-165 | FA-1 | The CLI returns a non-zero exit code when a run fails or a scan blocks | MVP | G-14 |
| FR-166 | FA-1 | The CLI runs without the web app and uses the same pinned kit and image digests as the web app | MVP | G-14 |
| FR-167 | FA-1 | A CI job runs a saved suite nightly through the CLI | Later | G-14 |
| FR-168 | FA-1 | A CI job runs a suite when a pull request carries the behavior-run label | Later | G-14 |
| FR-169 | FA-1 | The server exposes a versioned REST API covering every app resource | MVP | G-15 |
| FR-170 | FA-1 | The web UI and the CLI expose the same operations and return the same results | MVP | G-15 |
| FR-171 | FA-1 | The REST API returns a structured JSON error body for invalid input | MVP | G-15 |
| FR-172 | FA-1 | The REST API validates the identity token and the skill-builders group claim on every endpoint | MVP | G-15 |
| FR-173 | FA-1 | The REST API enforces project membership on project and run endpoints | MVP | G-15 |
| FR-174 | FA-1 | The REST API enforces owner-only integration changes | MVP | G-15 |
| FR-175 | FA-1 | The REST API never returns a secret value | MVP | G-15 |
| FR-176 | FA-1 | After sign-in the user lands on a dashboard that lists their builds and projects | MVP | G-16 |
| FR-177 | FA-1 | Every page shows the signed-in user's display name | MVP | G-16 |
| FR-178 | FA-1 | Every page offers a sign-out action | MVP | G-16 |
| FR-179 | FA-1 | A user navigates from the dashboard to a build, project, run or suite page | MVP | G-16 |
| FR-180 | FA-1 | A dashboard with no builds or projects shows a clear empty state | MVP | G-16 |
| FR-181 | FA-1 | A failed page request shows an error message without removing navigation | MVP | G-16 |
| FR-182 | FA-1 | The system persists users, builds, projects, members, integrations, bundles, runs and suites in its own database | MVP | G-17 |
| FR-183 | FA-1 | The system upgrades its stored data to the current version on start and on upgrade | MVP | G-17 |
| FR-184 | FA-1 | The system stores run artifacts under a per-run object-storage prefix | MVP | G-17 |
| FR-185 | FA-1 | The system records the creator and timestamps for each build, project and run | MVP | G-17 |
| FR-186 | FA-1 | The system pins exactly one platform kit version for all shared platform parts | MVP | G-17 |
| FR-187 | FA-1 | The system installs only the package versions and image digests listed by the pinned kit | MVP | G-17 |
| FR-188 | FA-1 | The system references every agent and scanner image by digest | MVP | G-17 |
| FR-189 | FA-1 | The system refuses to start when an agent or scanner image is referenced by tag | MVP | G-17 |
| FR-190 | FA-1 | Updating a runtime component requires only changing the pinned kit version in a pull request | MVP | G-17 |
| FR-191 | FA-1 | The skill builder never writes to the platform catalog or to project skills | MVP | G-17 |
| FR-192 | FA-1 | The skill builder performs no writes to the platform database | MVP | G-17 |
| FR-193 | FA-1 | The system exposes a health endpoint | MVP | G-18 |
| FR-194 | FA-1 | The system exposes a readiness endpoint that reports the app, data store and run environment status | MVP | G-18 |
| FR-195 | FA-1 | The system starts reproducibly with one command on a single host | MVP | G-18 |
| FR-196 | FA-1 | The app returns to a serving state after a restart without manual intervention | MVP | G-18 |
| FR-197 | FA-1 | Runs and scans execute in a runtime isolated from the web application process | MVP | G-18 |

## 7. Non-Functional Requirements

| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Performance | A run start request is acknowledged and persisted within 10 seconds, excluding agent execution | MVP |
| NFR-002 | Performance | The run page shows status no more than 15 seconds stale while a run executes | MVP |
| NFR-003 | Performance | 95 percent of read-only REST API requests return within 1 second | MVP |
| NFR-004 | Security | Every authenticated request validates the identity token and the skill-builders group claim before any action | MVP |
| NFR-005 | Security | Secret values never appear in database rows, logs, run results, error messages or rendered pages | MVP |
| NFR-006 | Security | The static scan runs with no network access | MVP |
| NFR-007 | Security | The LLM scan can reach only the configured model endpoint | MVP |
| NFR-008 | Security | The application's cloud identity can read and write only skill-builder secrets and its own object-storage bucket | MVP |
| NFR-009 | Security | Agent and scanner images are always referenced by digest, never by tag | MVP |
| NFR-010 | Security | Removing a user from the skill-builders group takes effect within one hour, when the current token expires | MVP |
| NFR-011 | Privacy | The skill builder stores only its own data and performs no writes to the platform or its catalog | MVP |
| NFR-012 | Privacy | Every Jira, GitHub and model credential used by a test project is test-only, and production credentials are out of scope | MVP |
| NFR-013 | Reliability | Every started run reaches a terminal state of pass, fail, error or cancelled within its configured limits | MVP |
| NFR-014 | Reliability | A scan that exceeds 10 minutes is stopped and recorded as a failed scan | MVP |
| NFR-015 | Reliability | The app returns to a serving state after a restart without manual intervention | MVP |
| NFR-016 | Operability | The app and database deploy reproducibly with one command on a single host | MVP |
| NFR-017 | Auditability | Every run records its skills commit SHA, agent image digest, step-kit version and verifier version | MVP |
| NFR-018 | Observability | Every run records its turns, tokens and cost | MVP |
| NFR-019 | Observability | When tracing is enabled, every run records a trace tagged for the skill-test environment | MVP |
| NFR-020 | Accessibility | The web UI meets WCAG 2.1 AA | MVP |
| NFR-021 | Compliance | Only test Jira sites, sandbox repositories and test model keys are used, and no production data is read or written | MVP |
| NFR-022 | Scalability | The system supports at least five concurrent runs on one host | MVP |

## 8. Constraints & Assumptions

**Authoritative input and missing story.** The run's work item is the story key `SkillBuilder4`.
The Atlassian MCP server configured for this repository was queried for that key and for its
summary, description and acceptance criteria; the key does not match Jira's issue-key format, and
searches for `SkillBuilder4` in the issue summary, description and full text returned no issue.
The `BSB` (`bheembhai-skill-builder`) project exists but contains no issues. No issue-level
summary, description or acceptance criteria were therefore available. This PRD treats
`docs/adr/SK-001-skill-builder.md` ("Skill builder — create, test, scan and ready platform
skills", status Proposed, 2026-11-02, decider Saraav) as the authoritative product description and
records the gap in Open Questions rather than inventing story details. If a Jira issue exists on
another site, its acceptance criteria must be reconciled with this PRD before decomposition.

**One feature area, eighteen capability groups.** The product is one authoring system delivered as
one application, so it is described as one feature area, `FA-1` "Skill builder". The 18 capability
groups in section 5 are the proposed epic boundaries; each functional requirement names its group
in its fifth column, and each group has at least one requirement.

**Repository placement and layout.** The skill builder lives in `bheembhai-skills` as its own
module under `skill-builder/`, with `app/`, `runner/`, `kit.txt` and `docker-compose.yml`.
`tools/build.py` packs only `skills/`, `config/` and `catalog.yaml`, so the skill builder never
enters a catalog release. No `AGENTS.md` exists in this repository yet, so this PRD was written at
the default layout path `docs/product/PRD.md`; `sdlc-arch-repo-scaffold` will add the conventions
file, and the table may move the artifact later.

**Platform prerequisite.** The platform side of the shared runtime — the step kit and the
versioned platform kit release carrying `bheembhai-verify`, `bheembhai-stepkit`, the agent image
digest and the scanner image digest — is a prerequisite tracked in platform ADR-033 and is not
delivered by this PRD. The agent and scanner images are published to the platform registry.

**External prerequisites (out of scope to build here).** The platform identity provider, its
application client and the `skill-builders` group; the cloud object-storage bucket, the
`skill-builder` secret path and the cloud identity that permits only those resources; the sandbox
GitHub repository and its curated input branches; the Jira test site and fixture files; each
user's GitHub identity; and the model vendor keys.

**Resolved choices where SK-001 leaves the question open.**
- A1 — v1 runs on one container host (a laptop or a single instance) with docker-compose. A
  managed container service is out of scope.
- A2 — Verification stays in the skill builder for v1. Moving it into the agent image later does
  not change the outcome required here.
- A3 — Jira isolation uses one dedicated test project per skill-builder project, with a
  run-specific `skilltest` label on every seeded issue, cleaned up per run and by a nightly sweep.
  A fresh Jira project per run is out of scope.
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
- A9 — v1 lets a user abandon an open build from the build page. Automatic abandonment of stale
  builds is out of scope.

**Product contract names.** This is an internal developer tool, so some requirements name the
platform artifacts an author works with, such as `verify.yaml`, the step kit, the pinned kit and
the image digests. Those names are part of the user-visible contract, not implementation choices.

**Ready definition.** A build is Ready at a commit SHA when four checks hold at that SHA: the
manifest is valid under tier-1 verifier checks, at least one run has a final verdict of pass after
verification, the static security check is not `DO_NOT_INSTALL`, and the LLM security check has
completed or is recorded as unavailable.

**Implementation choices not enumerated as requirements.** The stack is Python, FastAPI,
server-rendered HTML with the platform theme, PostgreSQL or SQLite for a single host, and Docker as
the container runtime. These are decisions from SK-001; the numbered requirements state only the
observable behavior.

**Skills repository CI.** The existing CI static check on pull requests in `bheembhai-skills`
stays in place and must use the same pinned scanner image as the app. It is repository CI, not an
app feature, and is not enumerated as a functional requirement here.

## 9. Open Questions

- Where is the Jira story `SkillBuilder4`? The configured Atlassian site has no such issue.
  Confirm the story and its acceptance criteria and reconcile them with this PRD.
- Which sandbox GitHub repository, Jira test project and input branches form the pilot?
- What are the default turn and spend caps for a run, and who may raise them?
- How long are run records, bundles, logs and transcripts retained, and what deletes them?
- How are stale run branches and abandoned builds cleaned up?
- Should the LLM security check become required before Submit, or stay advisory?
- Which model vendors and model profiles must ship in the first release?
- What happens when two runs target the same skill and input branch at the same time?

---
*Generated by the `sdlc-plan-prd-write` skill. Next step: run `sdlc-plan-epics-create` to turn the capability groups into Jira epics.*
