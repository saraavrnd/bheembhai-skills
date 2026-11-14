# PRD — SkillBuilder

**Status:** Draft · **Owner:** Skill platform team · **Last updated:** 2026-11-14

## 1. Problem & Opportunity
Skill authors maintain the skills that the platform executes, but they cannot exercise a skill
in the runtime that actually runs it without deploying the whole platform. Static checks confirm
that a manifest is well formed; they do not prove that a skill runs, produces a usable result, or
survives real Jira, GitHub and model interactions. Authors therefore learn whether an edit fixed
or broke behaviour only late, and they have no cheap way to compare one version of a skill with
another. The result is slow iteration and a risk that untested or unsafe skill changes reach the
catalog, where every project inherits them. There is an opportunity to give authors an isolated
place to create, run, verify and scan one skill at a time before it is proposed to the catalog.

## 2. Target Users
| User type | Primary need | Notes |
|-----------|--------------|-------|
| Skill author | Create or clone a skill, run it against realistic inputs, see whether it worked, and propose it to the catalog | Primary user; needs a fast edit, run, compare loop |
| Skill-builder project owner | Configure the test project, its members and its integrations, and control credentials | Owns integrations; may also be an author |
| Platform administrator | Decide who may spend tokens and write to the catalog | Manages the authorized-user group outside this product |

## 3. Goals & Success Metrics
- G1 — An author can take a skill from an idea to a passing, verified run without deploying the platform.
  - Metric: 100% of submitted builds have a passing verified run at the submitted commit.
- G2 — The authoring loop is short enough to encourage frequent runs.
  - Metric: median time from edit to verified run is under 10 minutes.
- G3 — Unsafe or unrunnable skills are stopped before they reach the catalog.
  - Metric: 0 skills with a DO_NOT_INSTALL static verdict reach submission, and 100% of runs are preceded by a static scan of the exact skill content.
- G4 — The builder's judgement matches the platform's for the same inputs.
  - Metric: 0 verdict mismatches in the component-parity suite.

## 4. Scope
**In scope (MVP):** sign-in restricted to authorized platform users; create and clone builds; test projects with Jira, GitHub and model integrations; single-skill runs in the same runtime as the platform; result verification; static and LLM security scans; run results, history and re-verification; the readiness checks and catalog submission; a command-line runner for runs and scans.

**Out of scope (Later / explicitly not now):** versioning inside the builder; skills that exist only inside a project; changes to the platform's data model, engine or interface for testing; writing directly to the platform catalog or project skills; changing built-in verification checks; orchestrated runs with workflow gates and routing; mocked model or integration behaviour by default; user administration inside the builder; parallel multi-skill workflow runs.

## 5. Feature Areas
| Area code | Feature area | One-line description |
|-----------|--------------|----------------------|
| FA-1 | Access and identity | Restrict the builder to authorized platform users and keep a local user record |
| FA-2 | Build authoring | Create or clone a skill as a build on its own branch |
| FA-3 | Test projects and integrations | Configure the project, its members, credentials and external integrations |
| FA-4 | Test runs | Execute one skill in the same runtime as the platform and capture its outcome |
| FA-5 | Verification and readiness | Verify a run and decide whether a build is ready to propose |
| FA-6 | Security scanning | Scan a skill statically and with a model before it is trusted |
| FA-7 | Results and history | Show what a run did and how it compares with earlier runs |
| FA-8 | Catalog submission | Turn a ready build into a reviewed catalog pull request |
| FA-9 | Command line and suites | Run tests and scans without the web interface and save repeatable suites |

## 6. Functional Requirements
| ID | Feature area | Requirement (one testable capability) | Release |
|------|--------------|----------------------------------------|---------|
| FR-001 | FA-1 | An unauthenticated visitor cannot open any authoring page | MVP |
| FR-002 | FA-1 | A user signs in with the existing platform identity-provider credentials | MVP |
| FR-003 | FA-1 | The system admits a signed-in user to authoring features only while the user is a current member of the skill-builders group | MVP |
| FR-004 | FA-1 | The system evaluates group membership on every request rather than only at sign-in | MVP |
| FR-005 | FA-1 | The system creates a local user record linked to the identity-provider subject on the user's first successful sign-in | MVP |
| FR-006 | FA-2 | An author creates a build by giving a skill name and a one-line description | MVP |
| FR-007 | FA-2 | Creating a build creates a build branch from the current main branch | MVP |
| FR-008 | FA-2 | Creating a build scaffolds the skill folder | MVP |
| FR-009 | FA-2 | A scaffolded skill contains SKILL.md with frontmatter, a verify.yaml stub, and the references, templates and examples folders | MVP |
| FR-010 | FA-2 | A newly scaffolded skill passes the catalog's static manifest checks without manual edits | MVP |
| FR-011 | FA-2 | An author clones an existing catalog skill under a new name | MVP |
| FR-012 | FA-2 | Cloning copies the skill folder into the new build | MVP |
| FR-013 | FA-2 | Cloning rewrites the name in the copied skill's frontmatter | MVP |
| FR-014 | FA-2 | Cloning leaves the source skill's files unchanged | MVP |
| FR-015 | FA-2 | The system rejects a build name that already exists on the main branch | MVP |
| FR-016 | FA-2 | The system rejects a build name that another open build already uses | MVP |
| FR-017 | FA-2 | The system rejects a build name that does not follow the required sdlc prefix, area segment and action segment pattern | MVP |
| FR-018 | FA-2 | Each save on a build creates a commit on the build branch | MVP |
| FR-019 | FA-2 | The system records the latest commit SHA on the build branch as the build head | MVP |
| FR-020 | FA-2 | The build page shows the build's current head SHA | MVP |
| FR-021 | FA-2 | The build page shows the build's readiness status | MVP |
| FR-022 | FA-2 | A new commit on a build clears the build's previously recorded ready SHA | MVP |
| FR-023 | FA-3 | A signed-in author creates a test project | MVP |
| FR-024 | FA-3 | The creator of a test project is recorded as its owner | MVP |
| FR-025 | FA-3 | The project owner adds a project member | MVP |
| FR-026 | FA-3 | The project owner removes a project member | MVP |
| FR-027 | FA-3 | A project member can start a test run in the project | MVP |
| FR-028 | FA-3 | Only the project owner can change integrations | MVP |
| FR-029 | FA-3 | The project owner configures a Jira integration with a site URL and a project or template | MVP |
| FR-030 | FA-3 | The project owner configures a GitHub integration with a sandbox repository and a base branch | MVP |
| FR-031 | FA-3 | The project owner configures an AI model profile with a vendor, a base URL and a tier-to-model mapping | MVP |
| FR-032 | FA-3 | The builder never stores an integration credential value in its own records | MVP |
| FR-033 | FA-3 | The system verifies an integration's credentials | MVP |
| FR-034 | FA-3 | The system records when an integration's credentials were last verified | MVP |
| FR-035 | FA-3 | The system warns when a GitHub integration points to a repository that a platform project also uses | MVP |
| FR-036 | FA-3 | The interface never displays a credential value | MVP |
| FR-037 | FA-4 | An author starts a run by selecting a skills branch, an input branch, an optional workflow-step context, and a model profile and tier | MVP |
| FR-038 | FA-4 | The system resolves the selected skills branch to a commit SHA | MVP |
| FR-039 | FA-4 | The system packages the skill at that commit for execution | MVP |
| FR-040 | FA-4 | The system reuses a skill package it has already produced for a skills commit instead of producing it again | MVP |
| FR-041 | FA-4 | The system creates a run branch from the input branch head | MVP |
| FR-042 | FA-4 | The system records the input branch head as the run's baseline SHA | MVP |
| FR-043 | FA-4 | The system never writes to the input branch during a run | MVP |
| FR-044 | FA-4 | The system runs the skill in the same runtime as the platform | MVP |
| FR-045 | FA-4 | The system shows run progress while the run executes | MVP |
| FR-046 | FA-4 | The system shows the run's logs while the run executes | MVP |
| FR-047 | FA-4 | The system classifies the run outcome using the same rules as the platform engine | MVP |
| FR-048 | FA-4 | The system records on each run the exact execution component and verifier versions used | MVP |
| FR-049 | FA-4 | The system records on each run the model profile and tier used | MVP |
| FR-050 | FA-4 | The author sets a turn cap for a run | MVP |
| FR-051 | FA-4 | The system stops a run when its turn cap is reached | MVP |
| FR-052 | FA-4 | The author sets a spend cap for a run | MVP |
| FR-053 | FA-4 | The system stops a run when its spend cap is reached | MVP |
| FR-054 | FA-4 | The system refuses to start a run when the selected execution components are incompatible | MVP |
| FR-055 | FA-4 | The system refuses to start a run when the static security scan for the skill content to be run did not pass | MVP |
| FR-056 | FA-4 | The author re-runs a prior run with the same inputs and the latest skills commit | MVP |
| FR-057 | FA-4 | The author uses a run's output branch as the input branch of a subsequent run | MVP |
| FR-058 | FA-4 | The system seeds Jira fixture issues for a run | Later |
| FR-059 | FA-4 | The system replaces fixture aliases with the created issue keys | Later |
| FR-060 | FA-4 | The system records Jira state after a run | Later |
| FR-061 | FA-4 | The system cleans up seeded issues when a run ends | Later |
| FR-062 | FA-4 | The system runs a nightly sweep that removes seeded Jira issues left behind by earlier runs | Later |
| FR-063 | FA-5 | After the agent exits, the system runs the selected verifier on the run branch | MVP |
| FR-064 | FA-5 | The verifier receives the baseline SHA and the skill's verify.yaml from the selected skills commit | MVP |
| FR-065 | FA-5 | The system records the agent's claimed verdict | MVP |
| FR-066 | FA-5 | The system records the post-verification final verdict | MVP |
| FR-067 | FA-5 | The system records whether verification overturned the claim | MVP |
| FR-068 | FA-5 | The system checks the build's manifest validity at a commit SHA | MVP |
| FR-069 | FA-5 | The system marks a build Ready at a commit SHA only when the manifest is valid, a run passes, the static scan is not DO_NOT_INSTALL, and the LLM scan has completed or is recorded as unavailable | MVP |
| FR-070 | FA-5 | The build page shows each of the four readiness checks and its current state | MVP |
| FR-071 | FA-5 | The system refuses to package a skill when the verifier's lint check fails on it | MVP |
| FR-072 | FA-5 | The system refuses to package a skill when the verifier's self-test fails on it | MVP |
| FR-073 | FA-5 | The system refuses to package a skill when the catalog's required verifier range does not include the selected verifier version | MVP |
| FR-074 | FA-5 | The author re-verifies an existing run output branch with a changed verify.yaml without invoking the agent or a model | MVP |
| FR-075 | FA-5 | The re-verification view shows which checks flipped compared with the original verification | MVP |
| FR-076 | FA-6 | The system runs a static security scan on the exact skill content before every run | MVP |
| FR-077 | FA-6 | The system reuses a completed static scan result when the skill content is unchanged | MVP |
| FR-078 | FA-6 | A static scan with a DO_NOT_INSTALL verdict is recorded as not passing | MVP |
| FR-079 | FA-6 | A static scan with a critical finding is recorded as not passing | MVP |
| FR-080 | FA-6 | A static scan with incomplete coverage is recorded as not passing | MVP |
| FR-081 | FA-6 | An accepted finding cannot override a static-scan block | MVP |
| FR-082 | FA-6 | The author triggers the LLM security scan only after the static scan passes for the current skill content | MVP |
| FR-083 | FA-6 | The LLM scan receives no credentials other than the model key | MVP |
| FR-084 | FA-6 | The LLM scan can reach only the model endpoint | MVP |
| FR-085 | FA-6 | The LLM scan never blocks a run | MVP |
| FR-086 | FA-6 | The LLM scan findings are shown to the author | MVP |
| FR-087 | FA-6 | A security scan times out after ten minutes | MVP |
| FR-088 | FA-6 | A timed-out scan is recorded as failed | MVP |
| FR-089 | FA-6 | The static scan report shows the score, the recommendation, and each finding's severity, rule, file and line | MVP |
| FR-090 | FA-6 | The LLM scan report shows the model used and each finding's severity, rule, file and line | MVP |
| FR-091 | FA-6 | The system produces the same scan verdict as the platform for the same skill content and scanner version | MVP |
| FR-092 | FA-6 | The author starts a static-only security scan from the skill page without starting a run | MVP |
| FR-093 | FA-6 | The author starts a full security scan from the skill page without starting a run | MVP |
| FR-094 | FA-7 | The run page shows the skill and its skills commit SHA | MVP |
| FR-095 | FA-7 | The run page shows the run's input branch | MVP |
| FR-096 | FA-7 | The run page shows the run's output branch | MVP |
| FR-097 | FA-7 | The run page shows the component versions the run used | MVP |
| FR-098 | FA-7 | The run page shows the claimed and final verdicts | MVP |
| FR-099 | FA-7 | The run page shows each check result | MVP |
| FR-100 | FA-7 | The run page shows the diff from the input branch to the run branch | MVP |
| FR-101 | FA-7 | The run page shows the Jira changes the run made | MVP |
| FR-102 | FA-7 | The run page shows the run's token usage and cost | MVP |
| FR-103 | FA-7 | The run page links to the run's trace | MVP |
| FR-104 | FA-7 | The skill history lists every run of a skill with its commit SHA, input branch, verdict and check results | Later |
| FR-105 | FA-7 | The compare view shows two runs side by side | Later |
| FR-106 | FA-7 | The compare view highlights the checks that flipped between the two runs | Later |
| FR-107 | FA-8 | The build page enables Submit to catalog only when all four readiness checks pass at the build head SHA | MVP |
| FR-108 | FA-8 | Submitting opens a pull request from the build branch to the catalog main branch using the author's own source-control identity | MVP |
| FR-109 | FA-8 | The pull request description lists the readiness checks at the head SHA | MVP |
| FR-110 | FA-8 | The pull request description links to the run report | MVP |
| FR-111 | FA-8 | The pull request description links to the scan reports | MVP |
| FR-112 | FA-8 | The system records the pull request URL and state on the build | MVP |
| FR-113 | FA-8 | The build state moves through open, submitted, and either merged or abandoned | MVP |
| FR-114 | FA-8 | A save on a submitted build clears its readiness status | MVP |
| FR-115 | FA-8 | The system never writes directly to the platform catalog, platform projects or project skills | MVP |
| FR-116 | FA-9 | The command line starts a test run without the web interface | MVP |
| FR-117 | FA-9 | The command line runs a static-only security scan without a test run | MVP |
| FR-118 | FA-9 | The command line runs a full security scan without a test run | MVP |
| FR-119 | FA-9 | The author saves a named suite of runs | Later |
| FR-120 | FA-9 | A suite entry names a skill, an input branch, a context and expectations | Later |
| FR-121 | FA-9 | The author runs a saved suite | Later |
| FR-122 | FA-9 | The author schedules a saved suite for nightly execution | Later |
| FR-123 | FA-9 | The system records each scheduled run's result | Later |

## 7. Non-Functional Requirements
| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Performance | The non-model setup for one run completes within 60 seconds for a skill of up to 5 MB | MVP |
| NFR-002 | Security | Every request from an unauthenticated caller is rejected | MVP |
| NFR-003 | Security | Every request from a caller who is not a current member of the skill-builders group is rejected | MVP |
| NFR-004 | Security | Credential values never appear in logs or run results | MVP |
| NFR-005 | Security | A static security scan has no network access | MVP |
| NFR-006 | Security | A test run uses only test-purpose Jira, source-control and model credentials, never production credentials | MVP |
| NFR-007 | Reliability | Every run reaches a terminal state within its configured deadline | MVP |
| NFR-008 | Reliability | A run that exceeds its deadline is recorded as failed | MVP |
| NFR-009 | Reproducibility | Preparing the same skills commit twice produces an identical skill package | MVP |
| NFR-010 | Reproducibility | The same inputs and component versions produce the same verification result | MVP |
| NFR-011 | Observability | Every run's trace identifies it as a test-environment run | MVP |
| NFR-012 | Accessibility | The web interface meets WCAG 2.1 AA | MVP |
| NFR-013 | Privacy | Run transcripts, logs and results are retained only for a configured period | Later |
| NFR-014 | Privacy | Run transcripts, logs and results can be purged on request | Later |
| NFR-015 | Cost | Each run records its token usage and cost | MVP |

## 8. Constraints & Assumptions
- **Source of this PRD.** The Jira work item named `SkillBuilder` was not retrievable from the configured Atlassian site: no issue with that key is visible, the `bheembhai-skill-builder` (BSB) project contains no issues, and a site-wide search returned no issue with "builder" in its summary or text. This PRD therefore takes the product definition from this repository's decision record SK-001 (skill builder), which names the skill builder as the product. If a separate Jira description exists, reconcile it against this assumption before decomposition.
- The builder is separate from the platform: it never writes to the platform's data model, catalog, projects or project skills, and the platform does not change to support testing.
- The platform's existing identity provider and the `skill-builders` group are external prerequisites. Group membership is managed outside the builder; the builder has no user-administration screen.
- The catalog repository, its main branch and the platform catalog import flow are external. Submission stops at a pull request.
- External integrations are Jira, GitHub and one or more model providers. Their credentials must be test-purpose, never production.
- The execution components, verifier and scanner are external releases that the builder consumes at a selected version and does not modify.
- The skills branches under test and the sandbox input branches are curated outside the builder and reused across runs.
- One run tests exactly one skill. Multi-step workflow orchestration is out of scope.
- There is no versioning inside the builder; versions begin at the catalog release.
- Fixture data for Jira is curated outside the run and reused across runs.
- A security finding's acceptance status is maintained outside the builder.

## 9. Open Questions
- Should each run get a fresh Jira project, or should one shared project carry a run label on every seeded issue?
- Should verification stay in the builder permanently, or move into the runtime later while the builder keeps re-verification?
- Which deployment target is intended for the first release: a developer laptop, a single host, or a managed container service?
- Which skills form the pilot set for the first end-to-end release?
- Which model profile should be the default for the LLM security scan?

---
*Generated by the `sdlc-plan-prd-write` skill. Next step: run `sdlc-plan-epics-create` to turn feature areas into Jira epics.*
