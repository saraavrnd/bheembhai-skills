# PRD — SkillBuilder

**Status:** Draft · **Owner:** Product, Skill Builder · **Last updated:** 2026-11-15

## 1. Problem & Opportunity

Skill authors in this catalog work on the one artifact the platform executes, but they cannot exercise it end to end before it enters the catalog. The available manifest checks validate structure, not behaviour, and running a skill still needs a real project, real Jira and source-control state, and a real model, which authors must not point at production data. Behavioural defects therefore go uncaught until a catalog release and platform import, when fixing them is most expensive. Authors need a safe, faithful loop in which a skill can be created or adapted, run against realistic test data, inspected, and changed again before anyone depends on it.

## 2. Target Users

| User type | Primary need | Notes |
|-----------|--------------|-------|
| Skill author | Create or adapt a skill and see it run against Jira, source control and a model before release | Primary user; must be a current member of the skill-builders group |
| Test-project owner | Give a small group a shared place to run skills with test credentials without exposing those credentials | Owns integration settings; may also be an author |
| Catalog reviewer | Judge a proposed skill from evidence recorded at the exact commit | Consumes the catalog pull request and its linked run and scan reports; does not use the authoring interface |
| Platform administrator | Keep authoring access limited to trusted people and import released skills | External to this product; manages group membership and the catalog import |

## 3. Goals & Success Metrics

> **Metric provenance.** The ADR states these goals qualitatively and supplies no numeric targets.
> Every threshold below is a proposed acceptance target for this PRD, not a commitment given by the
> source; the added ones are enumerated in §8.

- G1 — Authors validate behaviour before a skill is released.
  - Metric: at least 90% of catalog submissions have a passing verified run at the submitted commit.
- G2 — The builder and the platform agree on outcomes.
  - Metric: 100% agreement on verdict and security outcome for the same content and pinned component versions.
- G3 — Iteration is safe.
  - Metric: 0 runs that write to their input branch, and 0 credential values exposed in logs or results.
- G4 — Run preparation stays fast.
  - Metric: at least 95% of run preparations finish within 60 seconds for a skill bundle of up to 5 MB.
- G5 — Re-verification is cheap.
  - Metric: 0 model tokens consumed by a re-verify operation.
- G6 — Every authoring surface is usable with assistive technology.
  - Metric: 100% of audited builder web surfaces pass WCAG 2.1 AA with 0 critical accessibility findings.

## 4. Scope

**Release split (added assumption).** The ADR does not define releases. The MVP/Later split below, and the `MVP`/`Later` tags on every requirement, are this PRD's proposal (see §8).

**In scope (MVP):** sign-in and group-based authoring gate; create, edit and clone builds; skill-file editing and save-to-commit; build branch, head commit and readiness state; test projects and membership; Jira, source-control and model integrations with externally held credentials and MCP server definitions; run setup and skill packaging; run execution and outcome capture; turn and spend caps plus an installation-configured run deadline and retention period; re-runs and output chaining; static security scanning with a hard run gate; non-blocking model security scanning; verification through the shared verification layer and the Ready gate; run reports and audit trail; catalog submission as a pull request; command-line runs and scans; accessibility conformance (added assumption).

**Out of scope (Later / explicitly not now):** Jira fixture seeding; skill history and run comparison; saved suites and nightly scheduling; workflow orchestration with gates and routing; versioning inside the builder; user, group and role administration; project ownership transfer; writing to the platform catalog, platform projects or project skills; changing builtin verifier checks; mocked models or fake Jira and source control by default.

## 5. Feature Areas

| Area code | Feature area | One-line description |
|-----------|--------------|----------------------|
| FA-1 | Access & identity | Admit only trusted, signed-in members and anchor every later action to a local user |
| FA-2 | Build creation, editing & cloning | Start a build from a new name, a copy of a catalog skill, or an edit of an existing skill |
| FA-3 | Skill editing, build state & readiness tracking | Edit and save skill files, track each build's head commit and invalidate readiness when it moves |
| FA-4 | Test projects & membership | Give a small team a shared project with clear ownership |
| FA-5 | Integrations & credentials | Connect Jira, source control and models without storing secrets |
| FA-6 | Run setup & skill packaging | Resolve inputs and prepare an immutable skill bundle and run branch |
| FA-7 | Run execution & outcome capture | Execute one skill in the platform's runtime and classify its result |
| FA-8 | Run guardrails & re-runs | Bound cost and time, refuse unsafe starts, and repeat runs |
| FA-9 | Jira fixture seeding | Seed and clean up realistic tracker data per run |
| FA-10 | Verification & readiness | Grade the run with the shared verification layer and aggregate the four Ready checks |
| FA-11 | Static security scanning | Block a run when the static scan does not pass |
| FA-12 | LLM security scanning | Advise the author with a model-based scan that never blocks a run |
| FA-13 | Run results & audit trail | Show everything a reviewer needs about one run |
| FA-14 | Skill history & run comparison | Show a skill's runs over time and highlight what changed |
| FA-15 | Catalog submission | Turn a Ready build into a reviewed catalog pull request |
| FA-16 | Command line & suites | Run and scan outside the interface, and repeat named suites |
| FA-17 | Accessibility conformance | Keep every web surface operable with a keyboard and assistive technology (added assumption; see §8) |

## 6. Functional Requirements

FR-130 through FR-137 (FA-17, accessibility) are an added assumption: the ADR contains no
accessibility scope. See §8.

| ID | Feature area | Requirement (one testable capability) | Release |
|------|--------------|----------------------------------------|---------|
| FR-001 | FA-1 | An unauthenticated visitor cannot open any authoring page. | MVP |
| FR-002 | FA-1 | A user signs in with the platform's existing identity-provider credentials. | MVP |
| FR-003 | FA-1 | A signed-in user reaches authoring features only while that user is a current member of the skill-builders group. | MVP |
| FR-004 | FA-1 | The builder checks the requesting user's skill-builders membership claim on every request, not only at sign-in. | MVP |
| FR-005 | FA-1 | The builder creates one local user record per identity-provider subject on first successful sign-in. | MVP |
| FR-006 | FA-2 | An author creates a build from a skill name and a one-line description. | MVP |
| FR-007 | FA-2 | The builder creates the build branch from the current head of main. | MVP |
| FR-008 | FA-2 | The builder scaffolds the skill's own folder under the catalog's skills directory on the build branch. | MVP |
| FR-009 | FA-2 | The scaffold contains SKILL.md with the skill's frontmatter. | MVP |
| FR-010 | FA-2 | A newly scaffolded skill passes the catalog's static manifest checks without any edit. | MVP |
| FR-011 | FA-2 | An author clones an existing catalog skill under a new name. | MVP |
| FR-012 | FA-2 | Cloning copies the skill's whole folder to the new skill path. | MVP |
| FR-013 | FA-2 | Cloning rewrites the skill name in the copied frontmatter. | MVP |
| FR-014 | FA-2 | Cloning leaves the source skill's files unchanged. | MVP |
| FR-015 | FA-2 | The builder rejects a create or clone build whose skill name already exists on main. | MVP |
| FR-016 | FA-2 | The builder rejects a skill name used by another open build. | MVP |
| FR-017 | FA-2 | The builder rejects a name that does not follow the sdlc prefix, area segment and action segment pattern. | MVP |
| FR-018 | FA-3 | Each save creates a commit on the build branch. | MVP |
| FR-019 | FA-3 | The builder records the latest commit SHA as the build head. | MVP |
| FR-020 | FA-3 | The build page shows the current head SHA. | MVP |
| FR-021 | FA-3 | The build page shows the build's readiness status for its head SHA. | MVP |
| FR-022 | FA-3 | A new commit clears the previously recorded ready SHA. | MVP |
| FR-023 | FA-4 | A signed-in author creates a test project. | MVP |
| FR-024 | FA-4 | The builder records the project creator as the project owner. | MVP |
| FR-025 | FA-4 | The project owner adds another skill-builder user as a project member. | MVP |
| FR-026 | FA-4 | The project owner removes a project member. | MVP |
| FR-027 | FA-4 | Project membership authorizes starting a test run in that project. | MVP |
| FR-028 | FA-4 | Only the project owner can change the project's integrations. | MVP |
| FR-029 | FA-5 | The owner configures a Jira integration with a site URL and either a project key or a template project. | MVP |
| FR-030 | FA-5 | The owner configures a source-control integration with a sandbox repository and a base branch. | MVP |
| FR-031 | FA-5 | The owner configures an AI model profile with a vendor, base URL and tier-to-model mapping. | MVP |
| FR-032 | FA-5 | The builder never stores an integration's credential value in its own records. | MVP |
| FR-033 | FA-5 | The owner verifies an integration's credentials. | MVP |
| FR-034 | FA-5 | The builder records when an integration's credentials were last verified. | MVP |
| FR-035 | FA-5 | The builder warns when a source-control integration targets a repository also used by a platform project. | MVP |
| FR-036 | FA-5 | The builder never displays an integration's credential value in its interface. | MVP |
| FR-037 | FA-6 | An author starts a run in a test project the author is a member of. | MVP |
| FR-038 | FA-6 | The builder resolves the skills branch to a commit SHA at run start. | MVP |
| FR-039 | FA-6 | The builder packages the skill at that commit into a content-addressed bundle. | MVP |
| FR-040 | FA-6 | The builder reuses an existing bundle when the same skills commit is packaged again. | MVP |
| FR-041 | FA-6 | The builder creates the run branch, which is the run's output branch, from the input branch's head. | MVP |
| FR-042 | FA-6 | The builder records the input branch's head SHA as the run's baseline. | MVP |
| FR-043 | FA-6 | A run never writes to its input branch. | MVP |
| FR-044 | FA-7 | The builder executes the skill in the same runtime as the platform. | MVP |
| FR-045 | FA-7 | The run page shows progress while the run executes. | MVP |
| FR-046 | FA-7 | The run page shows logs while the run executes. | MVP |
| FR-047 | FA-7 | The builder classifies the run outcome using the platform engine's result rules. | MVP |
| FR-048 | FA-7 | The builder records the exact execution-component versions used by the run. | MVP |
| FR-049 | FA-7 | The builder records the model profile used by the run. | MVP |
| FR-050 | FA-8 | The author sets a turn cap for a run. | MVP |
| FR-051 | FA-8 | A run stops when it reaches its turn cap. | MVP |
| FR-052 | FA-8 | The author sets a spend cap for a run. | MVP |
| FR-053 | FA-8 | A run stops when it reaches its spend cap. | MVP |
| FR-054 | FA-8 | The builder refuses to start a run when its execution components are incompatible. | MVP |
| FR-055 | FA-8 | The builder refuses to start a run when the static scan for the skill content did not pass. | MVP |
| FR-056 | FA-8 | An author re-runs a prior run with the same inputs and the latest commit of its skills branch. | MVP |
| FR-057 | FA-8 | An author uses a prior run's output branch as the input branch of a later run. | MVP |
| FR-058 | FA-9 | The builder seeds Jira issues for a run from a fixture file into the project's configured Jira project, marked with the run's ID. | Later |
| FR-059 | FA-9 | Seeding replaces fixture aliases with the created issue keys. | Later |
| FR-060 | FA-9 | The builder records the Jira state after the run for fixture assertions. | Later |
| FR-061 | FA-9 | The builder cleans up the issues it seeded when the run ends, deleting only issues marked with that run's ID. | Later |
| FR-062 | FA-9 | A nightly sweep removes seeded issues carrying a run marker. | Later |
| FR-063 | FA-10 | The builder runs the shared verification layer on the run branch after the agent exits. | MVP |
| FR-064 | FA-10 | The verifier receives the run's baseline SHA. | MVP |
| FR-065 | FA-10 | The builder records the verdict the agent claimed. | MVP |
| FR-066 | FA-10 | The builder records the final verdict after verification. | MVP |
| FR-067 | FA-10 | The builder records whether verification overturned the agent's claimed verdict. | MVP |
| FR-068 | FA-10 | The builder checks the manifest validity of a build at a commit SHA. | MVP |
| FR-069 | FA-10 | The builder marks a build Ready at a SHA only when the manifest check passes, a run passes, the static scan passes and the LLM scan is complete or recorded as unavailable. | MVP |
| FR-070 | FA-10 | The build page shows each of the four readiness checks. | MVP |
| FR-071 | FA-10 | The builder refuses to package a skill when the verifier's lint check fails. | MVP |
| FR-072 | FA-10 | The builder refuses to package a skill when the verifier's self-test fails. | MVP |
| FR-073 | FA-10 | The builder refuses to package a skill when the catalog's required verifier range excludes the selected verifier version. | MVP |
| FR-074 | FA-10 | The builder re-verifies an existing output branch with a changed verify.yaml without the agent or a model. | MVP |
| FR-075 | FA-10 | A re-verification shows which checks flipped. | MVP |
| FR-076 | FA-11 | The builder runs a static security scan on the exact skill content before every run. | MVP |
| FR-077 | FA-11 | The builder reuses a completed static scan result when the content is unchanged. | MVP |
| FR-078 | FA-11 | A DO_NOT_INSTALL static verdict is not a passing result. | MVP |
| FR-079 | FA-11 | A critical static finding is not a passing result. | MVP |
| FR-080 | FA-11 | Incomplete static scan coverage is not a passing result. | MVP |
| FR-081 | FA-11 | An accepted finding cannot clear a static-scan block. | MVP |
| FR-082 | FA-12 | The builder triggers the LLM scan only after the static scan passes for the current content. | MVP |
| FR-083 | FA-12 | The LLM scan receives no credential other than the model key. | MVP |
| FR-084 | FA-12 | The LLM scan can reach only the model endpoint. | MVP |
| FR-085 | FA-12 | The LLM scan never blocks a run. | MVP |
| FR-086 | FA-12 | LLM scan findings are shown to the author. | MVP |
| FR-087 | FA-11 | A security scan times out after ten minutes. | MVP |
| FR-088 | FA-11 | A timed-out scan is recorded as failed. | MVP |
| FR-089 | FA-11 | The static scan report shows the scan's score. | MVP |
| FR-090 | FA-12 | The LLM scan report shows which model ran the scan. | MVP |
| FR-091 | FA-11 | The builder's scan verdict matches the platform's for the same content and scanner version. | MVP |
| FR-092 | FA-11 | An author starts a static-only scan from the skill page for a test project the author is a member of, without a run. | MVP |
| FR-093 | FA-12 | An author starts a full security scan from the skill page for a test project the author is a member of, without a run. | MVP |
| FR-094 | FA-13 | The run page shows the skill that ran. | MVP |
| FR-095 | FA-13 | The run page shows the input branch. | MVP |
| FR-096 | FA-13 | The run page shows the output branch. | MVP |
| FR-097 | FA-13 | The run page shows the component versions used. | MVP |
| FR-098 | FA-13 | The run page shows the verdict the agent claimed. | MVP |
| FR-099 | FA-13 | The run page shows each check result. | MVP |
| FR-100 | FA-13 | The run page shows the diff from the input branch to the run branch. | MVP |
| FR-101 | FA-13 | The run page shows the Jira changes the run made. | MVP |
| FR-102 | FA-13 | The run page shows the run's turn count. | MVP |
| FR-103 | FA-13 | The run page links to the run's trace when tracing is enabled. | MVP |
| FR-104 | FA-14 | The skill history lists every run of a skill with its commit SHA, input branch, verdict and checks. | Later |
| FR-105 | FA-14 | The compare view shows two runs side by side. | Later |
| FR-106 | FA-14 | The compare view highlights checks that flipped between the two runs. | Later |
| FR-107 | FA-15 | Submit to catalog is enabled only when the build is Ready at the head SHA. | MVP |
| FR-108 | FA-15 | Submitting opens a catalog pull request from the build branch to the catalog's main branch using the author's own source-control identity. | MVP |
| FR-109 | FA-15 | The pull-request description lists the readiness checks at the head SHA. | MVP |
| FR-110 | FA-15 | The pull-request description links to the run report. | MVP |
| FR-111 | FA-15 | The pull-request description links to the scan reports. | MVP |
| FR-112 | FA-15 | The builder records the pull-request URL on the build. | MVP |
| FR-113 | FA-15 | The build state moves through open, submitted, merged or abandoned. | MVP |
| FR-114 | FA-15 | A save on a submitted build clears its readiness status. | MVP |
| FR-115 | FA-15 | The builder never writes directly to the platform catalog, platform projects or project skills. | MVP |
| FR-116 | FA-16 | The command line starts a test run without the web interface. | MVP |
| FR-117 | FA-16 | The command line runs a static-only security scan without a test run. | MVP |
| FR-118 | FA-16 | The command line runs a full security scan without a test run. | MVP |
| FR-119 | FA-16 | An author saves a named suite of runs. | Later |
| FR-120 | FA-16 | A suite entry names a skill, input branch, context and expectations. | Later |
| FR-121 | FA-16 | An author runs a saved suite. | Later |
| FR-122 | FA-16 | A saved suite can be scheduled for nightly execution. | Later |
| FR-123 | FA-16 | The builder records each scheduled run's result. | Later |
| FR-124 | FA-2 | An author opens an existing catalog skill in an edit build on a branch cut from main. | MVP |
| FR-125 | FA-2 | An edit build changes the existing skill folder rather than creating a second skill folder. | MVP |
| FR-126 | FA-2 | The builder rejects an edit build for a skill name that does not exist on main. | MVP |
| FR-127 | FA-3 | An author edits the content of a file in a build's skill folder. | MVP |
| FR-128 | FA-5 | The owner records the MCP server definition that the Jira integration exposes to a run. | MVP |
| FR-129 | FA-5 | The owner records the MCP server definition that the source-control integration exposes to a run. | MVP |
| FR-130 | FA-17 | Every interactive control in the builder is operable with a keyboard. | MVP |
| FR-131 | FA-17 | Every interactive control shows a visible focus indicator. | MVP |
| FR-132 | FA-17 | Every custom status component exposes a programmatic name, role and state. | MVP |
| FR-133 | FA-17 | Every form field exposes its label, instructions and error message to assistive technology. | MVP |
| FR-134 | FA-17 | Run progress and readiness changes are announced to assistive technology. | MVP |
| FR-135 | FA-17 | Readiness and verdict status are never conveyed by colour alone. | MVP |
| FR-136 | FA-17 | Text and status colours meet WCAG 2.1 AA contrast in normal and hover or focus states. | MVP |
| FR-137 | FA-17 | Automated accessibility checks run in continuous verification. | MVP |
| FR-138 | FA-1 | The builder rejects a sign-in attempt by a user who is not a current member of the skill-builders group. | MVP |
| FR-139 | FA-12 | The builder records an LLM scan that cannot run as unavailable. | MVP |
| FR-140 | FA-13 | The builder records the Jira changes a run makes. | MVP |
| FR-141 | FA-1 | A user removed from the skill-builders group is denied authoring access no later than one hour after removal. | MVP |
| FR-142 | FA-1 | The builder reuses the existing local user record on a later sign-in by the same identity-provider subject. | MVP |
| FR-143 | FA-2 | The scaffold contains a verify.yaml stub. | MVP |
| FR-144 | FA-2 | The scaffold contains the standard references, templates and examples folders. | MVP |
| FR-145 | FA-6 | A run start offers the author a choice of skills branch. | MVP |
| FR-146 | FA-6 | A run start offers the author a choice of input branch. | MVP |
| FR-147 | FA-6 | A run start offers the author a choice of workflow and step context. | MVP |
| FR-148 | FA-6 | A run start lets the author optionally supply reviewer feedback or an upstream handoff. | MVP |
| FR-149 | FA-6 | A run start offers the author a choice of model profile. | MVP |
| FR-150 | FA-6 | A run start offers the author a choice of model tier. | MVP |
| FR-151 | FA-7 | The builder records the exact verifier version used by the run. | MVP |
| FR-152 | FA-7 | The builder records the model tier used by the run. | MVP |
| FR-153 | FA-10 | The verifier receives the verify.yaml from the skills commit. | MVP |
| FR-154 | FA-11 | The static scan report shows the scan's recommendation. | MVP |
| FR-155 | FA-11 | The static scan report lists each finding's severity, rule, file and line. | MVP |
| FR-156 | FA-12 | The LLM scan report lists each finding's severity, rule, file and line. | MVP |
| FR-157 | FA-13 | The run page shows the skills commit SHA. | MVP |
| FR-158 | FA-13 | The run page shows the final verdict after verification. | MVP |
| FR-159 | FA-13 | The run page shows the run's token usage. | MVP |
| FR-160 | FA-13 | The run page shows the run's cost. | MVP |
| FR-161 | FA-15 | The builder records the pull-request state on the build. | MVP |
| FR-162 | FA-3 | The author saves an edited file to the build branch. | MVP |
| FR-163 | FA-12 | A full security scan uses the LLM-scan model profile configured for the scan's test project. | MVP |
| FR-164 | FA-10 | The final verdict recorded for a run is the verdict produced by the shared verification layer. | MVP |

## 7. Non-Functional Requirements

NFR-001's numeric limits, the run deadline (NFR-007, NFR-008) and retention and purge (NFR-013,
NFR-014) are added assumptions, not ADR-given values. The reflow criterion (NFR-012) is likewise
added. The 3-month retention default (NFR-018), the environment-configured run deadline (NFR-019)
and the shared verification layer (FR-063, FR-164) were confirmed in review on 2026-11-15 rather
than given by the ADR. See §8.

| ID | Category | Requirement | Release |
|------|----------|-------------|---------|
| NFR-001 | Performance | Non-model run preparation completes within 60 seconds for a skill bundle of up to 5 MB. | MVP |
| NFR-002 | Security | Every request without a valid authenticated session is rejected before any builder data is returned. | MVP |
| NFR-003 | Security | Every request from a signed-in user who is not a current member of the skill-builders group is rejected. | MVP |
| NFR-004 | Privacy | Credential values never appear in builder logs or run results. | MVP |
| NFR-005 | Security | A static security scan has no network access. | MVP |
| NFR-006 | Privacy | Runs use only test-purpose Jira, source-control and model credentials. | MVP |
| NFR-007 | Reliability | Every run reaches a terminal state within its configured deadline. | MVP |
| NFR-008 | Reliability | A run that exceeds its configured deadline is recorded as failed. | MVP |
| NFR-009 | Reproducibility | Preparing the same skills commit twice produces an identical skill bundle. | MVP |
| NFR-010 | Reproducibility | The same inputs and component versions produce the same verification result. | MVP |
| NFR-011 | Compliance | When tracing is enabled, every run's trace identifies it as a test-environment run. | MVP |
| NFR-012 | Accessibility | Every builder web surface reflows to a 320 CSS-pixel viewport without two-dimensional scrolling. | MVP |
| NFR-013 | Privacy | Run transcripts, logs and results are retained only for a configured period. | MVP |
| NFR-014 | Privacy | Run transcripts, logs and results can be purged on request. | MVP |
| NFR-015 | Cost | Each run records its cost. | MVP |
| NFR-016 | Usage | Each run records its token usage. | MVP |
| NFR-017 | Usage | Each run records its turn count. | MVP |
| NFR-018 | Privacy | The default retention period for run transcripts, logs and results is 3 months. | MVP |
| NFR-019 | Reliability | The run deadline can be changed per installation without a code change. | MVP |

## 8. Constraints & Assumptions

**Source.** No separate product-idea input was supplied for this run, and the Atlassian project
`bheembhai-skill-builder` contains no issue titled `SkillBuilder`; its only issues are the BSB-1 to
BSB-17 epics. The single source is therefore the product definition in
`docs/adr/SK-001-skill-builder.md`; it is treated as the product idea. The BSB epic set currently
published in that project was generated from an earlier revision of this PRD, so it is a downstream
traceability view rather than a second source of truth; it is not used here to justify scope.
Requirements FR-124 onward were added in a preceding revision and will be mapped on the next epics
pass. In this revision, capabilities split out of an existing requirement are appended as new
identifiers continuing at FR-164 and NFR-018; no existing FR or NFR identifier is renumbered, so
existing traceability remains valid. FR-063 and FR-163 keep their identifiers but their text was
revised to record the review answers below.

**Review resolutions (2026-11-15).** The five open questions in the previous draft were answered in
review and are now recorded here and in the requirements: a 3-month default retention period
(NFR-018); a run deadline supplied through installation configuration (NFR-019); a shared
verification layer sourced from the Bheembhai solution and used by both the builder and the agent
image (FR-063, FR-164); an LLM-scan default model configured per test project (FR-163); and one
dedicated host running the container service (see the Hosting item below).

**Choices beyond the source.** The following are choices this PRD makes; the ADR does not contain
them. Where a bullet records a review confirmation (2026-11-15), that part is a decision downstream
may rely on. Everything else remains an assumption that no downstream step should treat as given
until a human confirms it.

- **Release split.** The ADR does not distinguish releases. The MVP/Later split in §4–§7, including
  treating accessibility as MVP, is this PRD's proposal.
- **Accessibility.** The ADR describes only server-rendered HTML with the platform's theme and says
  nothing about accessibility, WCAG, assistive technology or automated accessibility checks. FA-17,
  FR-130 through FR-137, G6 and NFR-012 are added here. NFR-012 is deliberately narrowed to a single
  testable reflow criterion; the WCAG 2.1 AA conformance target is carried by G6 and by the separate
  FA-17 functional requirements, not restated as one umbrella requirement. The 320 CSS-pixel width
  in NFR-012 is also an added value.
- **Retention and purge.** The ADR stores run data in the builder's database and S3 bucket but sets
  no retention period and no purge operation. NFR-013, NFR-014 and the installation-level retention
  setting are added here. Review confirmed a default retention period of 3 months (NFR-018).
- **Run deadline.** The ADR bounds turns and spend per run and gives scanner containers a 10-minute
  limit; it states no per-run deadline. NFR-007, NFR-008 and the installation-level deadline setting
  are added here. Review confirmed the deadline is supplied as one of the installation's
  configurable parameters through environment variables (NFR-019), so the deployment sets the value
  and this PRD does not fix a single numeric default.
- **Shared verification layer.** The ADR leaves open whether verification stays in the builder or
  moves into the agent image. Review confirmed the verification layer is a common package used by
  both the builder and the agent image; its source is the Bheembhai solution, so for this project
  it is a third-party dependency rather than code this product owns. The final verdict therefore
  comes from that shared layer (FR-063, FR-164), and the builder invokes it outside the agent
  container so the agent cannot edit what grades it.
- **LLM-scan model.** Review confirmed the default model for the LLM security scan is configured
  per test project, not overridden per run (FR-163). Only the project owner changes it.
- **Hosting.** Review confirmed the builder runs on one dedicated host running the container
  service, not a developer machine and not a managed container service. The run deadline and the
  scan network-isolation guarantees are sized for that single host.
- **Performance goal and numeric targets.** The ADR gives no run-preparation speed goal. G4 and
  NFR-001 are added here, and their thresholds are proposals: the 95% / 60 seconds / 5 MB in G4 and
  the 60 seconds / 5 MB in NFR-001. More generally, the ADR states qualitative outcomes only
  ("same verdict", "never", "no model tokens") and gives no percentages or durations, so the 90% in
  G1 and the 100% in G2 and G6 are also proposed acceptance thresholds. The 0 counts in G3 and G5
  restate the ADR's "never" and "no model tokens" wording as measurable targets.

**External prerequisites.** The platform identity provider, the skill-builders group, the catalog repository and its review flow, the pinned agent and scanner images, the pinned verifier releases, the shared verification layer from the Bheembhai solution (a third-party dependency for this project), the external secret store, the builder's object-storage bucket, the trace store, the curated input branches in the sandbox repository, the platform's repository inventory used for the overlap warning and the model endpoints are supplied outside this product. The builder consumes them; it does not build or administer them.

**Secrets.** Credential values live in the external secret store. The builder stores only an opaque reference and never writes a value to its database, logs, results or interface.

**One skill per run.** The builder runs one skill per run and does not orchestrate workflows, gates or routing.

**Test data.** Jira, source-control and model credentials used for runs are test-purpose credentials; a source-control integration that points at a repository also used by a platform project triggers a warning.

**No platform writes.** The builder never writes to the platform catalog, platform projects or project skills; its only outward write is a catalog pull request opened with the author's identity.

**Release markings.** The release split is an added assumption (see above). Requirements marked Later are deferred from the first release and are not prerequisites for it. All other requirements, including every non-functional requirement, are required for the first release.

**Access model.** The product assumes its users are already trusted by the platform and that group membership is managed externally; it provides no user, group or role administration of its own.

**Authoring surface.** Skill content is edited and saved from the build's own skill folder. Each save is a commit on the build branch; the builder does not version skill content separately from the branch.

**Edit builds.** Editing an existing catalog skill uses an edit build on a branch cut from main. It changes the existing skill folder and follows the same run, scan, Ready and Submit path as a new build; the catalog skill changes only when the catalog pull request merges.

**Branch vocabulary.** A run has one output branch: the run branch created from the input branch head. The PRD calls it the output branch where a later run consumes it as an input. The input branch is read-only for the run.

**MCP definitions.** A Jira or source-control integration may carry an MCP server definition that the runner passes to the skill. The definition is stored with the integration's non-secret settings and is never a credential.

**Jira fixture marking.** When Jira fixture seeding is enabled, seeded issues are created in the project's configured Jira project and marked with the run ID. Cleanup and the nightly sweep act only on marked issues, so a human-created issue is never deleted.

**Installation settings (review-confirmed).** The run deadline (NFR-007, NFR-008, NFR-019) and the retention period (NFR-013) are installation-level settings managed by the operator; an author does not set them per run. Neither setting appears in the ADR. The default retention period is 3 months (NFR-018). The run deadline is one of the installation's configurable parameters, supplied through environment variables (NFR-019), so the deployment sets the value and the PRD fixes no single numeric default.

**LLM-scan model setting.** The LLM security scan's default model lives on the test project, not on the installation and not on the run; the project owner configures it (FR-163).

## 9. Open Questions

None outstanding. The five questions raised in the previous revision were answered in review on 2026-11-15, and their resolutions are recorded in §8 and reflected in FR-063, FR-163, FR-164, NFR-018 and NFR-019.

- *Resolved — retention period:* default to 3 months; configured as an installation setting (NFR-013, NFR-018).
- *Resolved — run deadline:* supplied as an installation configuration parameter through environment variables (NFR-007, NFR-019); no fixed numeric default.
- *Resolved — verification:* the verification layer is a common package used by the builder and the agent image, sourced from the Bheembhai solution and a third-party dependency for this project (FR-063, FR-164).
- *Resolved — LLM scan model:* configured per test project only, not overridable per run (FR-163).
- *Resolved — hosting:* one dedicated host running the container service (see §8, Hosting).

---
*Generated by the `sdlc-plan-prd-write` skill. Next step: run `sdlc-plan-epics-create` to turn feature areas into Jira epics.*
