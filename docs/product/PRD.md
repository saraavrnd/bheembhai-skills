# PRD — SkillBuilder

**Status:** Draft · **Owner:** Product · **Last updated:** 2026-11-12

## 1. Problem & Opportunity

Platform skills are only exercised after they are published: the catalog's static and verifier
tiers never run a skill against real Jira, GitHub, or a model, and testing a draft inside the
platform would touch projects, credentials, and data an author does not want to disturb. Skill
authors therefore have no safe, fast way to see what a skill actually does before it reaches the
catalog, so defects, unsafe skills, and mis-graded outputs are discovered late — after review and
release effort has already been spent. There is an opportunity to catch these defects before
catalog review rather than after release.

## 2. Target Users

| User type | Primary need | Notes |
|-----------|--------------|-------|
| Skill author | Create or clone a skill, run it against realistic test data, see the verdict, fix, and submit it | Primary user; writes to the catalog only through a pull request |
| Skill reviewer / catalog maintainer | Judge a catalog pull request from the Ready checks and the linked run and scan evidence | Reviews with CODEOWNERS; not a skill-builder screen |
| Platform administrator | Control who may build skills by managing the Cognito group | Manages membership outside the skill builder |
| Test project owner | Configure the sandbox Jira, GitHub, and model integrations; add project members | Only the owner changes integrations |
| Test project member | Run tests in the project against the configured sandboxes | Cannot change integrations |

## 3. Goals & Success Metrics

- G1 — Authors validate a skill end to end without touching platform projects or production
  credentials.
  - Metric: 100% of validation runs use only the project's configured test integrations.
- G2 — The skill builder and the platform give the same verdict for the same skill bundle.
  - Metric: 0 verdict mismatches across a paired test set of at least 20 skills.
- G3 — Iteration is cheap: tuning checks does not re-run the agent.
  - Metric: a re-verification uses 0 model tokens and 0 agent runs.
- G4 — Test data cannot be lost.
  - Metric: 0 writes to an input branch across all runs.
- G5 — Unsafe skills are stopped before they run.
  - Metric: 100% of bundles with a DO_NOT_INSTALL or CRITICAL static result are blocked from starting a run.
- G6 — A Ready build carries complete evidence to review.
  - Metric: 100% of catalog pull requests opened by the skill builder link all four Ready checks.

## 4. Scope

**In scope (MVP):** runner and CLI; web app sign-in with the platform identity provider; test
projects and Jira, GitHub, and AI-model integrations; build creation by scaffold or clone; edit
builds; build readiness and catalog pull-request submission; one-skill test runs against real
sandboxes; run verification; re-run and re-verify; static and LLM security scanning; run results
pages; single-host deployment.
**Planned for later releases:** skill run history; side-by-side run comparison; saved suites and
scheduled or nightly suite runs; Jira fixture seeding, state capture, and cleanup.
**Out of scope (Later / explicitly not now):** versioning inside the skill builder (a build is a
branch; versions begin at the catalog release); skills that live only in a project; any change to
the platform data model, engine, or UI; writing to the platform catalog or to project skills;
changing builtin verifier checks (that is a verifier release); running multi-step workflows with
gates and routing; mocked models or a fake Jira or GitHub by default; user administration inside
the skill builder.

## 5. Feature Areas

| Area code | Feature area | One-line description |
|-----------|--------------|----------------------|
| FA-1 | Build creation | Create, clone, edit, list, and abandon skill builds on their own branches |
| FA-2 | Build readiness and catalog submission | Evaluate the four Ready checks and open a catalog pull request with evidence |
| FA-3 | Authentication and access | Platform sign-in restricted to the skill-builders group, checked on every request |
| FA-4 | Test projects and integrations | Own projects, membership, and Jira, GitHub, and AI-model integrations with stored secrets |
| FA-5 | Test runs | Run one skill against a sandbox input branch in the platform's pinned runtime |
| FA-6 | Verification and iteration | Grade the run outside the agent, compare claimed and final verdicts, re-run and re-verify |
| FA-7 | Results and history | Show run identity, verdicts, checks, diffs, cost, and later history and comparison |
| FA-8 | Static security scanning | Scan the exact run bundle, cache by content, block unsafe skills, show findings |
| FA-9 | LLM scanning and security reporting | Run the advisory LLM scan in isolation and present a combined security view |
| FA-10 | Jira test data | Seed, capture, label, and clean up Jira fixture data around a run |
| FA-11 | CLI and automation | Run and scan from the command line and drive saved suites and CI behavior runs |
| FA-12 | Runtime pinning and platform boundaries | Take all runtime versions from one pinned kit and never write to the platform |

## 6. Functional Requirements

| ID | Feature area | Requirement (one testable capability) | Release |
|------|--------------|----------------------------------------|---------|
| FR-001 | FA-1 | A signed-in user can start a new build by supplying a unique skill name and a one-line description | MVP |
| FR-002 | FA-1 | Creating a build writes the default skill structure: SKILL.md, a verify.yaml stub, a references README, and empty templates and examples directories | MVP |
| FR-003 | FA-1 | A newly created skill passes tier 1 validation with a no-checks-yet warning and no errors | MVP |
| FR-004 | FA-1 | A user can clone an existing catalog skill into a new build under a new name | MVP |
| FR-005 | FA-1 | Clone copies the complete skill folder and rewrites the frontmatter name to the new name | MVP |
| FR-006 | FA-1 | Clone leaves the source skill's files unchanged | MVP |
| FR-007 | FA-1 | Create and Clone reject a name that already exists on the main branch | MVP |
| FR-008 | FA-1 | Create and Clone reject a name used by another open build | MVP |
| FR-009 | FA-1 | Create and Clone reject a name that does not match the sdlc-area-action pattern | MVP |
| FR-010 | FA-1 | Each build is placed on its own build branch named for the skill and cut from main | MVP |
| FR-011 | FA-1 | A user can open an existing catalog skill as an edit build on a new branch | MVP |
| FR-012 | FA-1 | A user can abandon an open build, which moves it to the abandoned state | MVP |
| FR-013 | FA-1 | A user can view a list of builds showing each build's skill, state, and owner | MVP |
| FR-014 | FA-2 | Each save to a build records a commit and stores that commit's SHA on the build | MVP |
| FR-015 | FA-2 | The build page shows the four Ready checks at the build's head commit: manifest valid, passing run, static security, and LLM security | MVP |
| FR-016 | FA-2 | A build is Ready only when all four Ready checks hold at the same head commit | MVP |
| FR-017 | FA-2 | A new commit clears Ready until all four checks pass again at the new head commit | MVP |
| FR-018 | FA-2 | The Submit to catalog action is available only while the build is Ready | MVP |
| FR-019 | FA-2 | Submit to catalog opens a pull request from the build branch to main | MVP |
| FR-020 | FA-2 | Submitting a build moves it to the submitted state | MVP |
| FR-021 | FA-2 | The system marks a build merged when its pull request is merged | MVP |
| FR-022 | FA-2 | The pull request description lists the Ready checks at the submitted commit and links the supporting run and scan reports | MVP |
| FR-023 | FA-2 | The pull request is opened under the submitting user's GitHub identity | MVP |
| FR-024 | FA-3 | A user signs in with an existing platform account | MVP |
| FR-025 | FA-3 | The system refuses sign-in for a user who is not a member of the skill-builders group | MVP |
| FR-026 | FA-3 | The system checks the skill-builders group claim on every request rather than only at sign-in | MVP |
| FR-027 | FA-3 | The system records the signed-in user against the identity-provider subject on first sign-in | MVP |
| FR-028 | FA-3 | The system provides no user-administration screen, and group membership is managed outside the skill builder | MVP |
| FR-029 | FA-4 | A signed-in user can create a test project by supplying a name | MVP |
| FR-030 | FA-4 | The creator of a test project is recorded as its owner | MVP |
| FR-031 | FA-4 | A project owner can add and remove project members | MVP |
| FR-032 | FA-4 | Every project member can start test runs in that project | MVP |
| FR-033 | FA-4 | Only the project owner can create or change the project's integrations | MVP |
| FR-034 | FA-4 | A project owner can configure a Jira integration with a site URL, project key, MCP server definition, and API token | MVP |
| FR-035 | FA-4 | A project owner can configure a GitHub integration with a sandbox repository, base branch, MCP server definition, and access token | MVP |
| FR-036 | FA-4 | The system validates that the GitHub integration token can push build branches and open pull requests in the skills repository | MVP |
| FR-037 | FA-4 | A project owner can define one or more AI model profiles, each with a vendor, base URL, tier-to-model mapping, and API key | MVP |
| FR-038 | FA-4 | The system stores integration secrets in an external secrets store and keeps only a secret reference in its database | MVP |
| FR-039 | FA-4 | The system checks each integration's connection when it is configured and records the last successful check time | MVP |
| FR-040 | FA-4 | The system warns when a GitHub integration points at a repository that a platform project also uses | MVP |
| FR-041 | FA-4 | Integration secret values are injected into a run at launch only and never appear in the database, logs, results, or run pages | MVP |
| FR-042 | FA-4 | A project owner can select the project's default AI model profile for LLM security checks | MVP |
| FR-043 | FA-5 | A user can start a run by selecting a skills branch and one skill from that branch | MVP |
| FR-044 | FA-5 | The system resolves the selected skills branch to a commit SHA at run start and records that SHA on the run | MVP |
| FR-045 | FA-5 | The system packages the selected skill at that commit into a content-addressed bundle produced by the same packer a catalog release uses | MVP |
| FR-046 | FA-5 | The system reuses an existing bundle when the same skill and commit have been packed before | MVP |
| FR-047 | FA-5 | The system delivers the exact bundle to the run with a checksum that the run verifies | MVP |
| FR-048 | FA-5 | A user can select an input branch in the project's sandbox repository as the run's starting state | MVP |
| FR-049 | FA-5 | A user can optionally attach run context from a workflow step, reviewer feedback, or an upstream handoff | MVP |
| FR-050 | FA-5 | A user can select the model profile and tier for a run, defaulting to the skill's declared tier | MVP |
| FR-051 | FA-5 | A user can set a turn cap and a spend cap for a run | MVP |
| FR-052 | FA-5 | A run stops when it reaches its turn cap or its spend cap | MVP |
| FR-053 | FA-5 | The system creates a new run branch named for the run from the input branch head | MVP |
| FR-054 | FA-5 | The system records the input branch head commit as the run's baseline | MVP |
| FR-055 | FA-5 | A run never writes to its input branch, and all run commits go to the run branch | MVP |
| FR-056 | FA-5 | The system starts a run in the same pinned agent runtime that the platform uses for a workflow step | MVP |
| FR-057 | FA-5 | The system displays run progress and the agent log while the run is in progress | MVP |
| FR-058 | FA-5 | On completion, the system classifies the run outcome exactly as the platform engine classifies a step result | MVP |
| FR-059 | FA-5 | Every run records its skills commit, input and output branches, agent image digest, stepkit version, verifier version, model profile, and tier | MVP |
| FR-060 | FA-5 | A user can use a completed run's output branch as the input branch of a subsequent run | MVP |
| FR-061 | FA-6 | After the agent exits, the system verifies the run branch with the pinned verifier and the verify.yaml from the run's skills commit | MVP |
| FR-062 | FA-6 | Verification runs outside the agent container so the agent cannot modify what grades it | MVP |
| FR-063 | FA-6 | Verification uses the run's recorded baseline commit for must-change and precondition checks | MVP |
| FR-064 | FA-6 | The run page shows the verdict the agent claimed, the final verdict after verification, and whether the verdict was overturned | MVP |
| FR-065 | FA-6 | A user can re-run a run with the same inputs against the latest commit of the skills branch | MVP |
| FR-066 | FA-6 | A user can re-verify an existing output branch after only verify.yaml changes, with no agent run and no model tokens | MVP |
| FR-067 | FA-6 | Re-verification grades with the new commit's verify.yaml and reports which checks flipped | MVP |
| FR-068 | FA-6 | The system refuses to start a run when the skill's manifest fails verifier lint or self-test | MVP |
| FR-069 | FA-6 | The system refuses to start a run when catalog.yaml's verifier requirement does not accept the pinned verifier version | MVP |
| FR-070 | FA-7 | The run page shows the run's skill, skills commit, input and output branches, agent image digest, stepkit version, and verifier version | MVP |
| FR-071 | FA-7 | The run page shows the claimed verdict, the final verdict, and the result of every check | MVP |
| FR-072 | FA-7 | The run page shows the diff between the input branch and the output branch | MVP |
| FR-073 | FA-7 | The run page shows the Jira changes recorded for the run | Later |
| FR-074 | FA-7 | The run page shows turns, tokens, cost, and a trace link when tracing is enabled | MVP |
| FR-075 | FA-7 | Only members of a project can view that project's runs | MVP |
| FR-076 | FA-7 | The system stores run records in its database and run artifacts in its own object-storage bucket | MVP |
| FR-077 | FA-7 | A user can view a skill's run history with one row per run showing commit, input branch, verdict, and checks | Later |
| FR-078 | FA-7 | A user can compare two runs side by side and see which checks changed | Later |
| FR-079 | FA-8 | The system runs the static security scan on the exact bundle a run will use before the run starts | MVP |
| FR-080 | FA-8 | A Security check action on a skill runs the static scan on demand | MVP |
| FR-081 | FA-8 | The system caches a static scan result by the bundle's content hash | MVP |
| FR-082 | FA-8 | The system refuses to start a run when the static scan returns DO_NOT_INSTALL | MVP |
| FR-083 | FA-8 | The system refuses to start a run when the static scan reports a CRITICAL finding | MVP |
| FR-084 | FA-8 | The system refuses to start a run when the static scan reports incomplete coverage | MVP |
| FR-085 | FA-8 | The system shows each static finding with its severity, rule, file, and line | MVP |
| FR-086 | FA-8 | The system offers no override for a blocked static scan, and the only remedy is to fix the skill and save | MVP |
| FR-087 | FA-9 | The system queues the LLM security scan only after the static scan passes for the same content hash | MVP |
| FR-088 | FA-9 | The LLM security scan runs only from the Security check action, never from a run | MVP |
| FR-089 | FA-9 | A run never waits for the LLM security scan | MVP |
| FR-090 | FA-9 | LLM security findings never block a run | MVP |
| FR-091 | FA-9 | The system displays the LLM security check as completed or as unavailable | MVP |
| FR-092 | FA-9 | Each security scan runs in a short-lived scanner container that mounts the skill bundle read-only | MVP |
| FR-093 | FA-9 | The static security scan runs in a container with no network access | MVP |
| FR-094 | FA-9 | The LLM security scan container has network access only to the configured model endpoint | MVP |
| FR-095 | FA-9 | A security scan that exceeds its 10-minute limit is recorded as a failed scan | MVP |
| FR-096 | FA-9 | The system never runs the scanner in its MCP server mode | MVP |
| FR-097 | FA-9 | The security tab shows the scan score, recommendation, each finding, and the model used for the LLM check | MVP |
| FR-098 | FA-9 | The security tab presents the static and LLM results as separate checks | MVP |
| FR-099 | FA-10 | Before a run, the system can seed Jira issues from a named fixture | Later |
| FR-100 | FA-10 | Seeding replaces fixture aliases with the real Jira issue keys | Later |
| FR-101 | FA-10 | Seeded Jira issues carry a run-specific test label | Later |
| FR-102 | FA-10 | The system records the Jira state after a run for assertions and display | Later |
| FR-103 | FA-10 | The system cleans up the Jira issues it seeded at the end of the run | Later |
| FR-104 | FA-10 | A nightly sweep cleans up Jira issues left behind by failed runs | Later |
| FR-105 | FA-11 | The runner can be invoked from the command line with project, skill, skills branch, and input branch arguments | MVP |
| FR-106 | FA-11 | A CLI run uses the same pins, verification, and result records as a run started from the web app | MVP |
| FR-107 | FA-11 | The CLI provides a scan command that runs both security stages without a test run | MVP |
| FR-108 | FA-11 | The CLI scan command supports a static-only mode that skips the LLM stage | MVP |
| FR-109 | FA-11 | A user can save a named suite of runs with a skill, input branch, context, and expectations | Later |
| FR-110 | FA-11 | A user can run a saved suite from the web app or the CLI | Later |
| FR-111 | FA-11 | A user can schedule a saved suite to run nightly | Later |
| FR-112 | FA-11 | A pull request labeled for behavior runs triggers a run of the affected skill | Later |
| FR-113 | FA-12 | The system takes its verifier, stepkit, agent image, and scanner image versions from one pinned platform kit | MVP |
| FR-114 | FA-12 | The system refuses an agent image or scanner image identified by a tag instead of a digest | MVP |
| FR-115 | FA-12 | The system refuses to start a run when the pinned stepkit and agent image declare each other incompatible | MVP |
| FR-116 | FA-12 | Updating a runtime component requires only changing the pinned kit version in a pull request | MVP |
| FR-117 | FA-12 | The skill builder never writes to the platform catalog or to project skills | MVP |
| FR-118 | FA-12 | The skill builder uses its own database and never reads or writes the platform database | MVP |

## 7. Non-Functional Requirements

| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Security | Integration credentials are stored only in an external secrets store, and the database, logs, results, and run pages never contain a secret value | MVP |
| NFR-002 | Security | The skill builder's cloud role can read and write only secrets under its own secret path | MVP |
| NFR-003 | Security | A user whose skill-builders group membership is removed loses access within one hour, when the current token expires | MVP |
| NFR-004 | Security | Outbound access is limited to the sandbox GitHub repository, the Jira test project, the configured model endpoints, and the skill builder's own AWS services | MVP |
| NFR-005 | Privacy | Test projects must use test-only Jira, GitHub, and model credentials, and the system warns when a GitHub repository is shared with a platform project | MVP |
| NFR-006 | Performance | Jira seeding and cleanup together complete within 60 seconds per run | Later |
| NFR-007 | Reliability | A run aborted by a container, scanner, or infrastructure failure is recorded with a failed state rather than a pass verdict | MVP |
| NFR-008 | Operational | The skill builder deploys as a web app plus database on a single host | MVP |
| NFR-009 | Operational | The skill builder host provides a container runtime for run and scan containers | MVP |
| NFR-010 | Observability | Every run records turns, tokens, and cost, and, when tracing is enabled, a trace tagged for the skill-test environment | MVP |
| NFR-011 | Accessibility | The web interface meets WCAG 2.1 AA | MVP |

## 8. Constraints & Assumptions

- **Authoritative input.** The run's work item is the story key `SkillBuilder`. A search of the
  configured Jira site across every visible project, including `BSB` (bheembhai-skill-builder)
  and `BEEM`, found no issue with that key, summary, description, or comment. This PRD therefore
  treats `docs/adr/SK-001-skill-builder.md` as the authoritative product description. If a Jira
  issue exists outside this site, its acceptance criteria must be reconciled before decomposition.
- **Repository placement.** The skill builder lives in `bheembhai-skills` as its own module; the
  catalog packaging only covers `skills/`, `config/`, and `catalog.yaml`, so the skill builder
  never enters a catalog release.
- **Platform prerequisite.** The platform side of the shared runtime — the step kit and the
  versioned platform kit release — is a prerequisite tracked in platform ADR-033 and is not
  delivered by this PRD.
- **Deployment choice.** The skill builder runs on a single host with a container runtime and
  docker-compose, resolving SK-001 open question 3 for this release.
- **Jira isolation choice.** One shared Jira test project is used, and every seeded issue is
  labeled for its run, resolving SK-001 open question 1. A fresh project per run is not used.
- **Verification placement.** Verification stays in the skill builder for this release, resolving
  SK-001 open question 2; moving it into the agent image later does not change the outcome here.
- **External prerequisites.** The platform identity provider, its application client and
  skill-builders group, the image registry repositories, the secrets path, the object-storage
  bucket, the cloud role, the sandbox GitHub repository, the Jira test project, and the sandbox
  input branches are provisioned outside the skill builder before first use.
- **Credential policy.** Every Jira, GitHub, and model credential used by a test project is
  test-only; the skill builder never receives production credentials.
- **Added affordances.** The build list, the abandon action, member-only run visibility, and the
  submitted and merged build states are explicit requirements derived from the build data model
  and the catalog pull-request flow in SK-001, not new product scope.
- **Accessibility target.** WCAG 2.1 AA is an added assumption; SK-001 does not state an
  accessibility target.
- **Web and storage stack.** The web app is server-rendered using the platform theme, and the
  database is PostgreSQL or SQLite for a single host, both from SK-001. These are implementation
  constraints and are not decomposed into requirements.

## 9. Open Questions

- Which sandbox GitHub repository, Jira test project, and input branches form the pilot?
- What are the default turn and spend caps for a run, and who may raise them?
- How long are run records, bundles, logs, and transcripts retained, and what deletes them?
- How are stale run branches and abandoned builds cleaned up?
- Should the LLM security check become required before Submit, or stay advisory?
- Which model vendors and model profiles must ship in the first release?
- What happens when two runs target the same skill and input branch at the same time?

---
*Generated by the `sdlc-plan-prd-write` skill. Next step: run `sdlc-plan-epics-create` to turn feature areas into Jira epics.*
