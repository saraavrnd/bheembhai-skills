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
| Skill-builder project owner | Configure the test project, its integrations and its members, and control credentials | Owns integrations; may also be an author |
| Platform administrator | Decide who may spend tokens and write to the catalog | Manages the authorized-user group outside this product |

## 3. Goals & Success Metrics
- G1 — An author can take a skill from an idea to a passing, verified run without deploying the platform.
  - Metric: 100% of submitted builds have a passing verified run at the submitted commit.
- G2 — The authoring loop is short enough to encourage frequent runs.
  - Metric: median time from edit to verified run is under 10 minutes.
- G3 — Unsafe or unrunnable skills are stopped before they reach the catalog.
  - Metric: 0 skills with a DO_NOT_INSTALL static verdict reach submission; 100% of runs are preceded by a static scan of the exact bundle.
- G4 — The builder's judgement matches the platform's for the same inputs.
  - Metric: 0 verdict mismatches in the component-parity suite.

## 4. Scope
**In scope (MVP):** authorized sign-in through the platform's existing identity provider; create and clone builds on branches; test projects with Jira, GitHub and model integrations; single-skill runs in the pinned runtime; result verification; static and LLM security scans; run results, history and re-verification; the readiness checks and catalog submission; a command-line runner for runs and scans.

**Out of scope (Later / explicitly not now):** versioning inside the builder; skills that exist only inside a project; changes to the platform's data model, engine or interface for testing; writing directly to the platform catalog or project skills; changing built-in verification checks; orchestrated runs with workflow gates and routing; mocked model or integration behaviour by default; user administration inside the builder; parallel multi-skill workflow runs.

## 5. Feature Areas
| Area code | Feature area | One-line description |
|-----------|--------------|----------------------|
| FA-1 | Access and identity | Restrict the builder to authorized platform users and keep a local user record |
| FA-2 | Build authoring | Create or clone a skill as a build on its own branch |
| FA-3 | Test projects and integrations | Configure the project, its members, credentials and external integrations |
| FA-4 | Test runs | Execute one skill in the pinned runtime and capture its outcome |
| FA-5 | Verification and readiness | Verify a run and decide whether a build is ready to propose |
| FA-6 | Security scanning | Scan a skill statically and with a model before it is trusted |
| FA-7 | Results and history | Show what a run did and how it compares with earlier runs |
| FA-8 | Catalog submission | Turn a ready build into a reviewed catalog pull request |
| FA-9 | Command line and suites | Run tests and scans without the web interface and save repeatable suites |

## 6. Functional Requirements
| ID | Feature area | Requirement (one testable capability) | Release |
|------|--------------|----------------------------------------|---------|
| FR-001 | FA-1 | An unauthenticated visitor is denied access to every authoring page and is redirected to sign in | MVP |
| FR-002 | FA-1 | A user signs in with the existing platform identity-provider credentials | MVP |
| FR-003 | FA-1 | The system admits a signed-in user to authoring features only while the user is a current member of the skill-builders group | MVP |
| FR-004 | FA-1 | The system re-checks group membership on every request so that a removed user loses access without signing in again | MVP |
| FR-005 | FA-1 | The system creates a local user record linked to the identity-provider subject on the user's first successful sign-in | MVP |
| FR-006 | FA-2 | An author creates a build by giving a skill name and a one-line description; the system creates a build branch from the current main branch and scaffolds the skill folder | MVP |
| FR-007 | FA-2 | A scaffolded skill contains SKILL.md with frontmatter, a verify.yaml stub, and references, templates and examples folders | MVP |
| FR-008 | FA-2 | A newly scaffolded skill passes the catalog's static manifest checks without manual edits | MVP |
| FR-009 | FA-2 | An author clones an existing catalog skill under a new name; the system copies the skill folder and rewrites the name in the frontmatter | MVP |
| FR-010 | FA-2 | Cloning leaves the source skill's files unchanged | MVP |
| FR-011 | FA-2 | The system rejects a build name that already exists on the main branch | MVP |
| FR-012 | FA-2 | The system rejects a build name that another open build already uses | MVP |
| FR-013 | FA-2 | The system rejects a build name that does not follow the required sdlc prefix, area segment and action segment pattern | MVP |
| FR-014 | FA-2 | Each save on a build creates a commit on the build branch and records the commit SHA as the build head | MVP |
| FR-015 | FA-2 | The build page shows the build's current head SHA and its readiness status | MVP |
| FR-016 | FA-2 | A new commit on a build clears the build's previously recorded ready SHA | MVP |
| FR-017 | FA-3 | A signed-in author creates a test project and becomes its owner | MVP |
| FR-018 | FA-3 | The project owner adds and removes project members | MVP |
| FR-019 | FA-3 | A project member can start a test run in the project while only the owner can change integrations | MVP |
| FR-020 | FA-3 | The project owner configures a Jira integration with a site URL, a project or template, and an MCP server definition | MVP |
| FR-021 | FA-3 | The project owner configures a GitHub integration with a sandbox repository, a base branch and an MCP server definition | MVP |
| FR-022 | FA-3 | The project owner configures one or more AI model profiles with a vendor, a base URL and a tier-to-model mapping | MVP |
| FR-023 | FA-3 | The system stores each integration credential in a managed secret store and keeps only a secret reference in its database | MVP |
| FR-024 | FA-3 | The system verifies an integration's credentials and records the verification time | MVP |
| FR-025 | FA-3 | The system warns when a GitHub integration points to a repository that a platform project also uses | MVP |
| FR-026 | FA-3 | The system never displays a credential value in the interface, logs or run results | MVP |
| FR-027 | FA-4 | An author starts a run by selecting a skills branch, an input branch, an optional workflow-step context, and a model profile and tier | MVP |
| FR-028 | FA-4 | The system resolves the selected skills branch to a commit SHA and packs the skill into a content-addressed bundle | MVP |
| FR-029 | FA-4 | The system reuses an already packed bundle for a skills commit SHA instead of packing it again | MVP |
| FR-030 | FA-4 | The system creates a new run branch from the input branch head and records the input head as the baseline SHA | MVP |
| FR-031 | FA-4 | The system never writes to the input branch during a run | MVP |
| FR-032 | FA-4 | The system runs the skill with the pinned execution components and follows run progress and logs while it executes | MVP |
| FR-033 | FA-4 | The system classifies the run outcome using the same rules as the platform engine | MVP |
| FR-034 | FA-4 | The system records the execution image digest, step-kit version, verifier version, model profile and tier on the run | MVP |
| FR-035 | FA-4 | The author sets a turn cap for a run, and the system stops the run when the cap is reached | MVP |
| FR-036 | FA-4 | The author sets a spend cap for a run, and the system stops the run when the cap is reached | MVP |
| FR-037 | FA-4 | The system refuses to start a run when the selected execution image and step-kit versions are incompatible | MVP |
| FR-038 | FA-4 | The system refuses to start a run when the static security check has not passed for the exact bundle | MVP |
| FR-039 | FA-4 | The author re-runs a prior run with the same inputs and the latest skills commit | MVP |
| FR-040 | FA-4 | The author uses a run's output branch as the input branch of a subsequent run | MVP |
| FR-041 | FA-4 | The system seeds Jira fixture issues for a run and replaces fixture aliases with the created issue keys | Later |
| FR-042 | FA-4 | The system records Jira state after a run and cleans up the seeded issues when the run ends | Later |
| FR-043 | FA-4 | The system runs a nightly sweep that removes seeded Jira issues left behind by earlier runs | Later |
| FR-044 | FA-5 | After the agent exits, the system runs the pinned verifier on the run branch outside the agent's execution environment | MVP |
| FR-045 | FA-5 | The verifier receives the baseline SHA and the skill's verify.yaml from the pinned skills commit | MVP |
| FR-046 | FA-5 | The system records the agent's claimed verdict, the post-verification final verdict, and whether verification overturned the claim | MVP |
| FR-047 | FA-5 | The system marks a build Ready at a commit SHA only when the manifest is valid, a run passes, the static scan is not DO_NOT_INSTALL, and the LLM scan has completed or is recorded as unavailable | MVP |
| FR-048 | FA-5 | The build page shows each of the four readiness checks and its current state | MVP |
| FR-049 | FA-5 | The system refuses to pack a skill when the pinned verifier's lint or self-test fails on it | MVP |
| FR-050 | FA-5 | The system refuses to pack a skill when the catalog's required verifier range does not include the pinned verifier version | MVP |
| FR-051 | FA-5 | The author re-verifies an existing run output branch with a changed verify.yaml without invoking the agent or a model | MVP |
| FR-052 | FA-5 | The re-verification view shows which checks flipped compared with the original verification | MVP |
| FR-053 | FA-6 | The system runs a static security scan on the exact bundle before every run | MVP |
| FR-054 | FA-6 | The static scan runs in a short-lived isolated environment with no network access | MVP |
| FR-055 | FA-6 | The scanner never runs inside the application process | MVP |
| FR-056 | FA-6 | The system caches a static scan result by bundle content SHA | MVP |
| FR-057 | FA-6 | The system refuses a run when the static scan returns DO_NOT_INSTALL, a critical finding or incomplete coverage | MVP |
| FR-058 | FA-6 | An accepted finding cannot override a static-scan block, so the author must fix the skill | MVP |
| FR-059 | FA-6 | The author triggers the LLM security scan only after the static scan passes for the current content SHA | MVP |
| FR-060 | FA-6 | The LLM scan receives no credentials other than the model key and can reach only the model endpoint | MVP |
| FR-061 | FA-6 | The LLM scan never blocks a run, and its findings are shown to the author | MVP |
| FR-062 | FA-6 | The system limits each scan to ten minutes and treats a timeout as a failed scan | MVP |
| FR-063 | FA-6 | The system shows the scan score, the recommendation, each finding's severity, rule, file and line, and the model used for the LLM scan | MVP |
| FR-064 | FA-6 | The system produces the same scan verdict as the platform for the same skill bundle and pinned scanner | MVP |
| FR-065 | FA-6 | The author starts a static-only or a full security scan from the skill page without starting a run | MVP |
| FR-066 | FA-7 | The run page shows the skill, skills commit SHA, input and output branches, pinned component versions, claimed and final verdicts, and each check result | MVP |
| FR-067 | FA-7 | The run page shows the diff from the input branch to the run branch | MVP |
| FR-068 | FA-7 | The run page shows the Jira changes the run made | MVP |
| FR-069 | FA-7 | The run page shows the run's token usage and cost | MVP |
| FR-070 | FA-7 | The run page links to the run's trace | MVP |
| FR-071 | FA-7 | The skill history lists every run of a skill with its commit SHA, input branch, verdict and check results | Later |
| FR-072 | FA-7 | The compare view shows two runs side by side and highlights the checks that flipped between them | Later |
| FR-073 | FA-8 | The build page enables Submit to catalog only when all four readiness checks pass at the build head SHA | MVP |
| FR-074 | FA-8 | Submitting opens a pull request from the build branch to the catalog main branch using the author's own source-control identity | MVP |
| FR-075 | FA-8 | The pull request description lists the readiness checks at the head SHA and links to the run and scan reports | MVP |
| FR-076 | FA-8 | The system records the pull request URL and state on the build | MVP |
| FR-077 | FA-8 | The build state moves through open, submitted, and either merged or abandoned | MVP |
| FR-078 | FA-8 | The system never writes directly to the platform catalog, platform projects or project skills | MVP |
| FR-079 | FA-8 | A save after review comments creates a new commit that clears readiness until all checks pass again | MVP |
| FR-080 | FA-9 | The command line starts a test run without the web interface using the same pinned components and writes results to the same store | MVP |
| FR-081 | FA-9 | The command line runs a static-only or full security scan without a test run | MVP |
| FR-082 | FA-9 | The author saves a named suite of runs, each with a skill, input branch, context and expectations | Later |
| FR-083 | FA-9 | The author runs a saved suite from the web interface or the command line | Later |
| FR-084 | FA-9 | The system schedules a saved suite for nightly execution and records each run's result | Later |

## 7. Non-Functional Requirements
| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Performance | The non-model setup for one run, covering branch creation, bundle packing and launch preparation, completes within 60 seconds for a skill bundle of up to 5 MB | MVP |
| NFR-002 | Security | Every request is authenticated and authorized against the caller's current group membership, and an unauthenticated or unauthorized request is rejected | MVP |
| NFR-003 | Security | Credential values never appear in the application database, logs, run results or pages, and only secret references are stored | MVP |
| NFR-004 | Security | A static security scan has no network access | MVP |
| NFR-005 | Security | A test run uses only test-purpose Jira, source-control and model credentials and never production credentials | MVP |
| NFR-006 | Reliability | Every run reaches a terminal state within its configured deadline, and a run that exceeds the deadline is recorded as failed | MVP |
| NFR-007 | Reproducibility | Packing the same skills commit twice produces the same bundle SHA | MVP |
| NFR-008 | Reproducibility | The same inputs and pinned versions produce the same verification result | MVP |
| NFR-009 | Observability | Every run records its pinned component versions and emits trace metadata identifying it as a test-environment run | MVP |
| NFR-010 | Accessibility | The web interface meets WCAG 2.1 AA | MVP |
| NFR-011 | Privacy | Run transcripts, logs and results are retained only for a configured period and can be purged on request | Later |
| NFR-012 | Cost | Each run records its token usage and cost and enforces the run's spend cap | MVP |
| NFR-013 | Operability | The system deploys on a single host with its database and object storage and starts with one documented command | MVP |

## 8. Constraints & Assumptions
- **Source of this PRD.** The Jira work item `SkillBuilder` was not retrievable from the configured Atlassian site when this PRD was written: no issue by that key was visible, and the `bheembhai-skill-builder` project contained no issues. This PRD therefore takes the product definition from this repository's decision records SK-001 (skill builder) and SK-002, which name the skill builder as the product. If a separate Jira description exists, reconcile it against this assumption before decomposition.
- The builder is a separate application in the same repository as the catalog. It shares only versioned components with the platform and never writes to the platform's data model, catalog or projects.
- The platform's existing identity provider and the `skill-builders` group are external prerequisites. Group membership is managed outside the builder; the builder has no user-administration screen.
- The catalog repository, its main branch and the platform catalog import flow are external. Submission stops at a pull request.
- External integrations are Jira, GitHub and one or more model providers. Their credentials are test-purpose and live in a managed secret store.
- The runtime host must support containers, because runs and scans execute in prebuilt images.
- One run tests exactly one skill. Multi-step workflow orchestration is out of scope.
- Fixture data for Jira and input branches for the sandbox repository are curated outside the run and reused across runs.

## 9. Open Questions
- Should each run get a fresh Jira project, or should one shared project carry a run label on every seeded issue?
- Should verification stay in the builder permanently, or move into the agent image later while the builder keeps re-verification?
- Which deployment target is intended for the first release: a developer laptop with containers, a single host, or a managed container service?
- Should the shared step kit remain one package, or should the identity and secret helpers split into their own package?
- Which skills form the pilot set for the first end-to-end release?
- Which model profile should be the default for the LLM security scan?

---
*Generated by the `sdlc-plan-prd-write` skill. Next step: run `sdlc-plan-epics-create` to turn feature areas into Jira epics.*
