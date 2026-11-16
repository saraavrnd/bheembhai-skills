# Stories — BSB-37 (Command line & saved suites)

Epic BSB-37 covers FR-116, FR-117, FR-118, FR-119, FR-120, FR-121, FR-122 and FR-123.
Decomposed into 7 vertical slices below; coverage of all eight requirements verified.

The seven slices are the two halves of the epic as an author experiences them. The MVP half adds
no second engine: the terminal starts a run of a skill branch (PENDING-1), runs a static-only
security scan (PENDING-2) and runs the full static-then-LLM security scan (PENDING-3) through the
same run-start, packaging and scan services the interface uses. The Later half adds saved suites:
a member saves a named suite whose entries name a skill, input branch, context and expectations
(PENDING-4), runs it and grades each entry against its expectation (PENDING-5), schedules it for
nightly execution (PENDING-6), and sees every scheduled run's result, including skips and
failures (PENDING-7). Every slice ends in a durable record in the builder's own database — a
"runs" row, a "scans" row, a "suites" row, a "suite_runs" row and its "suite_run_entries" rows —
never in a temporary shim.

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than a Jira issue: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404
"Issue does not exist or you do not have permission to see it.", matching `PRD.md` section 8. No
Atlassian MCP tool was exposed to this session, so the configured site was queried read-only
through its REST API. The epic being decomposed is BSB-37, read from the same site:
summary "Command line & saved suites", type Epic, status To Do, labels FA-16/mixed, and a
description matching the BSB-37 section of `epics.md`. The run context's epic item is BSB-37
(feature area FA-16). No Jira write was attempted.

**Scope decisions (made here because the epic leaves them open, not assumed silently).**
- **Command-line identity.** The CLI uses the platform's Cognito token, never a builder-issued
  credential. It reads the ID token from the `SKILL_BUILDER_TOKEN` environment variable (not a
  command-line flag, so it does not appear in a process list), verifies it with the same
  `CognitoProvider` and `cognito:groups` gate BSB-18-PENDING-3 uses, and requires an existing local
  "users" row for the token's "sub" because project membership references that row. It creates no
  "sb_session" cookie and issues no token. This is the non-interactive half of the authoring gate,
  not a second gate.
- **Command-line run record.** A CLI run calls BSB-24's run-start service with the skill name and
  skills ref instead of a `build_id`. `runs.build_id` is the id of the open build whose skill and
  branch match `--skill` and `--skills-ref`, and NULL when no open build matches. The data-model
  stage must keep `runs.build_id` nullable; the web contract still requires it. Everything after
  the request (packaging, preflight, execution, verification) is BSB-25, BSB-27, BSB-26 and BSB-29
  unchanged.
- **Command-line scan record.** A CLI scan calls the static and full scan services behind
  BSB-31-PENDING-1 and BSB-32-PENDING-2 without a build. Its `scans` row has `build_id` NULL
  because no build requested it, and it still carries no `project_id`, because the BSB-31 scan
  record is content-addressed and reused across projects. The data-model stage must keep
  `scans.build_id` nullable and expose the scan service to a caller that has no build id.
- **Suite definition.** A saved suite stores its entries in `suites.definition` JSONB and stores
  the run's model profile and tier at suite level, so a night run is repeatable. Each entry names
  a skill, input branch, context and expectations exactly as FR-120 requires; the suite-level
  model settings are run inputs, not entry fields. `suites.source_path` stays NULL for a suite
  saved in the builder; importing a `suites/name.yaml` file is out of scope. The suite resolves
  each entry's skill to its open build branch when one exists (and records that build id), or to
  `main` when the skill exists only there.
- **Nightly schedule.** A suite's `schedule_enabled` flag means one run per UTC date at the first
  scheduler tick at or after 02:00 UTC. A scheduled suite run runs as the suite's creator
  (`suites.created_by`); if that user is no longer a project member, the execution is recorded as
  failed rather than run under a stale identity. A unique `(suite_id, scheduled_for)` key makes a
  second tick idempotent.
- **Result record.** Manual and scheduled suite runs both use `suite_runs` and
  `suite_run_entries`. FR-123 is satisfied by the scheduled rows: every scheduled execution
  records its date, state and per-entry outcome (matched, mismatched, skipped or failed), with the
  reason and the linked run id. The data-model stage must add these two tables, plus
  `suites.created_by` and `suites.schedule_enabled`.
- **Suite surface.** Saving, running and scheduling a saved suite are project-page features in this
  epic. The suite-run service they call is the same service a command-line `suite` command would
  call, so a later CLI client would not be a second engine; no `suite` command is added here
  because FR-119 to FR-123 do not require one.

> New stories use draft keys `BSB-37-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-37, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-37-PENDING-1

**Title:** Start a test run from the command line with a non-interactive token
**Epic:** BSB-37 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-16, MVP

### Story
As a **skill author who is a project member**, I want **to start a test run of a skill branch from my terminal with a non-interactive identity-provider token**, so that **I can loop on a skill without the web interface and still get the same run record and execution path the interface produces**.

### Acceptance Criteria

Scenario: A project member starts a run from the command line and one run record is created
Given a Cognito ID token for Ada whose verified "sub" is "c0ffee00-1234-4abc-9def-000000000001", whose "email" claim is "ada@example.com", whose "name" claim is "Ada", and whose "cognito:groups" claim carries "skill-builders", "SKILL_BUILDER_TOKEN" set to that token, a local "users" row id 42 with cognito_sub "c0ffee00-1234-4abc-9def-000000000001" and email "ada@example.com", a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "sdlc-fix-bug-reproduce", branch "build/sdlc-fix-bug-reproduce" and state "open", an "integrations" row id 3 with project_id 7, kind "github", config {"repository": "saraavrnd/skill-builder-sandbox", "base_branch": "main", "test_only": true} and secret_ref "skill-builder/7/integration-3", an "integrations" row id 4 with project_id 7, kind "ai_model", config {"name": "Default", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-opus-5-5", "medium": "claude-sonnet-5-5", "low": "claude-haiku-5-5"}, "test_only": true} and secret_ref "skill-builder/7/integration-4", a secret store holding "ghp-test-token-7a1d" at "skill-builder/7/integration-3" and "sk-ant-test-3c9e" at "skill-builder/7/integration-4", a stub source-control provider listing branch "build/sdlc-fix-bug-reproduce" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" for repository "saraavrnd/bheembhai-skills" and branch "test/atlas/bug-42" at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" for repository "saraavrnd/skill-builder-sandbox", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md", an empty "runs" table with a "runs" id sequence whose next value is 21, a stub runtime adapter whose container-start counter is 0, and a builder clock reading "2026-11-16T11:00:00Z"
When Ada runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --input test/atlas/bug-42 --model-profile 4 --tier medium` against the builder database
Then the process exits with status 0 and prints "Run 21 requested for skill sdlc-fix-bug-reproduce in Project Atlas.", exactly one "runs" row exists with id 21, project_id 7, user_id 42, build_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha NULL, input_branch "test/atlas/bug-42", run_branch NULL, context NULL, model_profile_id 4, tier "medium", state "requested" and kind "run", the row's created_at is "2026-11-16T11:00:00Z", no "sb_session" cookie is set and no server-side session is created, and the stub runtime adapter's container-start counter remains 0

Scenario: The command line refuses a missing, invalid, expired or unprivileged token and a token with no builder account
Given a Cognito ID token for Ada whose verified "sub" is "c0ffee00-1234-4abc-9def-000000000001" and whose "cognito:groups" claim carries "skill-builders", a Cognito ID token for Bob whose verified "sub" is "c0ffee00-1234-4abc-9def-000000000002" and whose "cognito:groups" claim does not carry "skill-builders", a token whose signature fails "CognitoProvider" verification, an expired token whose refresh is not attempted, an empty "SKILL_BUILDER_TOKEN" environment variable, and an empty "users" table
When the CLI is invoked once with no "SKILL_BUILDER_TOKEN" set, once with the unverifiable token, once with the expired token, once with Bob's token, and once with Ada's token while the "users" table is still empty, each time with `run --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --input test/atlas/bug-42 --model-profile 4 --tier medium`
Then all five invocations exit with status 2: the first writes "Set SKILL_BUILDER_TOKEN to a Cognito ID token.", the second and third write "SKILL_BUILDER_TOKEN is not a valid or unexpired Cognito token.", the fourth writes "Access is limited to members of the skill-builders group.", and the fifth writes "No builder account exists for this identity; sign in at /sign-in once." to standard error, no "runs" row is created, no "users" row is created, and standard output and standard error contain no part of any token value

Scenario: A signed-in skill author who is not a project member cannot start a CLI run
Given a Cognito ID token for Carol whose verified "sub" is "c0ffee00-1234-4abc-9def-000000000003" and whose "cognito:groups" claim carries "skill-builders", "SKILL_BUILDER_TOKEN" set to that token, a local "users" row id 44 with that cognito_sub, no "project_members" row for Project Atlas (id 7), an empty "runs" table, and a stub source-control provider whose branch-listing counter is 0
When Carol runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --input test/atlas/bug-42 --model-profile 4 --tier medium`
Then the process exits with status 2, writes "You are not a member of this project." to standard error, creates no "runs" row, and the stub source-control provider received 0 branch-listing requests

Scenario: The command line refuses a skills ref that is missing, lacks the skill, or has no such input branch
Given Ada's token and local "users" row 42, her "project_members" row for Project Atlas (id 7), the source-control integration 3, the AI model integration 4, a stub source-control provider that lists branches ["main", "build/sdlc-fix-bug-reproduce", "test/saraav/fix-reproduce"] for repository "saraavrnd/bheembhai-skills" and ["main", "test/atlas/bug-42"] for repository "saraavrnd/skill-builder-sandbox", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md" and ref "test/saraav/fix-reproduce" does not contain "skills/sdlc-fix-bug-reproduce/", and an empty "runs" table
When Ada runs the CLI three times: once with `--skills-ref missing-branch`, once with `--skills-ref test/saraav/fix-reproduce`, and once with `--skills-ref build/sdlc-fix-bug-reproduce --input test/atlas/bug-99`, each with `--project 7 --skill sdlc-fix-bug-reproduce --model-profile 4 --tier medium`
Then the three invocations exit with status 2 and write "The selected skills branch does not exist in the catalog repository.", "The selected skills branch does not contain skill sdlc-fix-bug-reproduce." and "The selected input branch does not exist in the sandbox repository." to standard error respectively, and no "runs" row is created

Scenario: A project without a source-control integration cannot start a CLI run
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), the AI model integration 4, an "integrations" table with no row with kind "github" for project 7, and an empty "runs" table
When Ada runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --input test/atlas/bug-42 --model-profile 4 --tier medium`
Then the process exits with status 2, writes "A source-control integration is required to start a run." to standard error, and creates no "runs" row

Scenario: The model profile and tier default from the project and the skill and are validated
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), the source-control integration 3, a stub source-control provider that lists branch "build/sdlc-fix-bug-reproduce" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and branch "test/atlas/bug-42" at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", one test-purpose "ai_model" integration id 4 with a complete high, medium and low mapping, another test-purpose "ai_model" integration id 5, a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md" whose frontmatter has model "medium", and an empty "runs" table with a "runs" id sequence whose next value is 21
When Ada runs the CLI four times, each time with `run --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --input test/atlas/bug-42`: once without `--model-profile` and without `--tier` after removing integration 5, once without `--model-profile` with both integrations present, once with `--tier ultra`, and once with `--model-profile 9` where integration 9 belongs to project 8
Then the first invocation exits with status 0 and creates a "runs" row id 21 with model_profile_id 4 and tier "medium", the second, third and fourth invocations exit with status 2 and write "Choose a model profile with --model-profile.", "The model tier must be high, medium or low." and "The selected model profile is not available for runs in this project." to standard error respectively, and only the first invocation creates a "runs" row

### Covered requirements (traceability)
- FR-116

### Out of scope
The `scan` command (BSB-37-PENDING-2 and -3); starting a run through the web form (BSB-24);
resolving the skills branch to a commit, packaging the skill, creating the run branch and
recording the baseline (BSB-25); the run-start preflight, static-scan gate, caps and deadline
(BSB-27); execution and progress (BSB-26); verification and the final verdict (BSB-29); the run
report page (BSB-33); token issuance, Cognito client configuration, refresh and sign-in
(BSB-18); creating projects, membership or integrations (BSB-22 and BSB-23); a local-folder mode
that writes results outside the builder database; a `--follow` mode that streams progress; any
command-line representation of the web run-start form.

### Notes / dependencies
Depends on BSB-18-PENDING-1 and BSB-18-PENDING-3 for the verified Cognito token, the
`CognitoProvider` contract, the "cognito:groups" claim and the exact group-denial message, on
BSB-18-PENDING-2 for the local "users" row keyed by "sub", on BSB-22-PENDING-1 and
BSB-22-PENDING-3 for the "project_members" rows and the shared project-membership check with its
exact 403 message "You are not a member of this project.", on BSB-24-PENDING-1 for the run-start
service and the "runs" row shape, on BSB-24-PENDING-2 and -3 for the context fields, on
BSB-24-PENDING-4 for the model-profile and tier validation and messages, on BSB-23-PENDING-2 for
the source-control integration and repository branches, on BSB-23-PENDING-3 and -6 for the
test-purpose "ai_model" profiles and their complete tier mapping, on BSB-19 and BSB-21 for the
open "builds" row and its branch, and on BSB-25, BSB-27, BSB-26 and BSB-29 for everything that
happens after the run is requested.

This story owns the `run` command of `python -m skill_builder.runner`, its environment variables,
its output, its exit codes and the mapping from flags to the run-start service. The durable system
of record is the builder's own "runs" table from ADR SK-001 section 9; the CLI writes the same row
the web form writes, and it never writes a separate queue, log file or marker. The `run` command
returns after the run is requested; preparation and execution remain asynchronous and are picked
up by the same workers (BSB-25, BSB-27, BSB-26 and BSB-29).

The flags map to BSB-24's contract: `--project` is the "project_id"; `--skill` is the skill name;
`--skills-ref` is the "skills_branch" stored as "runs.skills_ref"; `--input` is the
"input_branch"; `--workflow`, `--step`, `--reviewer-feedback` and `--upstream-handoff` are the
context fields and are validated by BSB-24-PENDING-2 and -3; `--model-profile` and `--tier` are
the run's model fields. A missing `--project`, `--skill`, `--skills-ref` or `--input` is a usage
error: exit status 2 with "Choose a project.", "Choose a skill.", "Choose a skills branch." or
"Choose an input branch." as applicable, and no run. `--model-profile` names an "integrations" row
of kind "ai_model" in the same project whose config "test_only" is true; when it is omitted and the
project has exactly one such profile that profile is used, when it is omitted and there are none
the CLI exits with "No model profile is available for runs in this project.", and when it is
omitted and there are several the CLI exits with "Choose a model profile with --model-profile.".
`--tier` is "high", "medium" or "low"; when it is omitted the CLI uses the "model:" value from the
selected skills commit's "SKILL.md" frontmatter when that value is one of the three, otherwise it
exits with "Choose a model tier with --tier.". The validation and the failure wording are
BSB-24-PENDING-4's; the non-interactive defaults are this command's, because a terminal has no
form to preselect in: the sole run-purpose profile when there is exactly one, and the skill's
frontmatter tier when it is one of the three. `Choose a model profile with --model-profile.` names
the flag because a terminal has no form field to point at.

The CLI resolves the local user from the verified token's "sub" and does not upsert one: project
membership and "runs.user_id" both reference a "users" row that BSB-18-PENDING-2 creates at first
sign-in, so a token with no row is refused rather than silently creating an account without a
sign-in. The group claim is checked on the same invocation as the membership and before the
local "users" lookup and before any project, build, integration or run data is read, so a token
outside "skill-builders" gets the group message even when that identity has no "users" row. The token is read only from
`SKILL_BUILDER_TOKEN`; a `--token` flag is deliberately not offered, and the token value is never
written to the database, standard output, standard error or a log.

`runs.build_id` is resolved as the id of the open "builds" row whose "skill" equals `--skill` and
whose "branch" equals `--skills-ref`; when no open build matches, the column is NULL. This keeps
the common build loop traceable without making a build a prerequisite of a command-line run. The
data-model stage must keep "runs.build_id" nullable; the web request still requires it. When a
CLI run resolves to an open build, it counts towards that build's readiness aggregation exactly
as a web run does; a run with a NULL `build_id` contributes to no build's readiness. The
aggregation is BSB-30's and is not computed here.

---

## STORY: BSB-37-PENDING-2

**Title:** Run a static-only security scan from the command line
**Epic:** BSB-37 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-16, MVP

### Story
As a **skill author who is a project member**, I want **to run a static-only security scan of a skill branch from the terminal**, so that **I can check untrusted skill content without starting a test run or opening the web interface**.

### Acceptance Criteria

Scenario: A project member runs a static-only scan that passes and no run is created
Given Ada's token and local "users" row 42, her "project_members" row for Project Atlas (id 7), the source-control integration 3, a stub source-control provider listing branch "build/sdlc-fix-bug-reproduce" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md", a "skill_bundles" row for "sdlc-fix-bug-reproduce" and commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" with bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08" and s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", no "scans" row for that bundle, a "scans" id sequence whose next value is 11, an empty "runs" table, the pinned kit recording scanner package "bheembhai-skillscan 0.4.2" and image digest "sha256:9c1f0a9d8b7e6f5a", and a stub static scanner that writes the report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []}
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --static-only`
Then the process exits with status 0 and prints "Static scan 11 completed with verdict PASS.", exactly one "scans" row exists with id 11, build_id NULL, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", stage "static", state "completed", verdict "pass", scanner_version "bheembhai-skillscan 0.4.2" and image_digest "sha256:9c1f0a9d8b7e6f5a", the row carries no project_id, no "scans" row with stage "llm" exists, no "runs" row exists, no run branch is created, and the scanner container environment contains no Jira, source-control or model credential

Scenario: A static-only scan that fails the verdict exits non-zero and records the findings
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), the source-control integration 3, the packed bundle and catalog tree of the first scenario, no "scans" row for that bundle, a "scans" id sequence whose next value is 11, an empty "runs" table, and a stub static scanner that writes the report {"score": 41, "recommendation": "DO_NOT_INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "CRITICAL", "rule": "SS-001", "file": "SKILL.md", "line": 3}, {"severity": "HIGH", "rule": "SS-101", "file": "scripts/run.sh", "line": 14}]}
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --static-only`
Then the process exits with status 1 and prints "Static scan 11 completed with verdict FAIL.", the "scans" row id 11 has stage "static", state "completed" and verdict "fail", two "scan_findings" rows exist for scan 11 with severity, rule, file and line matching the report, and no "runs" row exists

Scenario: A static-only scan with a missing, unprivileged or non-member identity is refused
Given Carol's verified token whose "cognito:groups" claim carries "skill-builders" and whose local "users" row 44 has no "project_members" row for Project Atlas (id 7), an empty "SKILL_BUILDER_TOKEN" environment variable, a token whose signature fails "CognitoProvider" verification, a packed bundle for skill "sdlc-fix-bug-reproduce", and a stub static scanner whose container-start counter is 0
When the CLI `scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --static-only` is invoked with no token, with the unverifiable token, and with Carol's token
Then each invocation exits with status 2 and writes "Set SKILL_BUILDER_TOKEN to a Cognito ID token.", "SKILL_BUILDER_TOKEN is not a valid or unexpired Cognito token." and "You are not a member of this project." to standard error respectively, no "scans" row is created, and the stub static scanner's container-start counter remains 0

Scenario: A static-only scan refuses a ref that is missing or lacks the skill
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), the source-control integration 3, a stub source-control provider that lists branches ["main", "build/sdlc-fix-bug-reproduce"] for repository "saraavrnd/bheembhai-skills", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md", and a stub skill packer whose pack counter is 0
When Ada runs the CLI with `--skills-ref missing-branch`, and then with `--skills-ref main` where ref "main" does not contain "skills/sdlc-fix-bug-reproduce/"
Then the two invocations exit with status 2 and write "The selected skills branch does not exist in the catalog repository." and "The selected skills branch does not contain skill sdlc-fix-bug-reproduce." to standard error respectively, the stub skill packer's pack counter remains 0, and no "scans" row is created

Scenario: A project without a source-control integration cannot scan a skill
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), an "integrations" table with no row with kind "github" for project 7, and a stub static scanner whose container-start counter is 0
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --static-only`
Then the process exits with status 2, writes "A source-control integration is required to scan a skill." to standard error, no "scans" row is created, and the stub static scanner's container-start counter remains 0

Scenario: A scanner that writes no report is a failed scan and an operational error
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), the source-control integration 3, the packed bundle and catalog tree of the first scenario, no "scans" row for that bundle, a "scans" id sequence whose next value is 11, and the pinned scanner container exits with code 137 before writing a report
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce --static-only`
Then the process exits with status 2, writes "Static scan 11 failed: Scanner exited with code 137 before writing a report." to standard error, the "scans" row id 11 has stage "static", state "failed", verdict "fail" and failure_reason "Scanner exited with code 137 before writing a report.", and no "runs" row exists

### Covered requirements (traceability)
- FR-117

### Out of scope
The `run` command (BSB-37-PENDING-1) and the full static-then-LLM scan (BSB-37-PENDING-3); the
static scan service, its reuse, verdict rules, ten-minute limit and report (BSB-31-PENDING-1 to
-PENDING-6); the bundle format and packer (BSB-25); the LLM scan and its model profile (BSB-32);
the scan report page (BSB-31-PENDING-5); accepting a finding or changing a scanner rule; any
credential for the scanner container; a local skill directory that is not in the catalog
repository; sending the scan result to the platform.

### Notes / dependencies
Depends on BSB-18-PENDING-1 and BSB-18-PENDING-3 for the verified token and group gate, on
BSB-18-PENDING-2 for the local "users" row, on BSB-22-PENDING-1 and BSB-22-PENDING-3 for the
project and the shared membership check, on BSB-23-PENDING-2 for the source-control integration
used to resolve `--skills-ref` and read the catalog repository, on BSB-25-PENDING-1 and -2 for
resolving the ref to a commit and packing or reusing the content-addressed bundle, and on
BSB-31-PENDING-1 for the static scan service, the "scans" and "scan_findings" rows, the
network-less scanner container and the scanner identity.

This story owns the `scan` command's static mode and its exit status. The command resolves
`--skill` and `--skills-ref` to a commit and a "skill_bundles" row through the same BSB-25 path a
run uses, then calls BSB-31-PENDING-1's static scan service with the project, skill, commit SHA
and bundle and no build id; BSB-31-PENDING-1 must expose that service independently of its
build-keyed route, and the CLI does not call the build-page route and creates no build-specific
record. The
"scans" row it creates has `build_id` NULL because no build is named; the data-model stage must
keep "scans.build_id" nullable. The row carries no `project_id`, because BSB-31's scan record is
content-addressed and reused across projects; the project is the authorization scope only, and the
scan itself resolves no project integration and no credential, exactly as BSB-31-PENDING-6
requires.

Exit status is the command's contract for CI: 0 when the scan completes with verdict "pass", 1
when the scan completes with verdict "fail", and 2 when the request is refused or the scan cannot
complete (auth, membership, unknown ref or skill, missing integration, scanner failure). Standard
output carries the one-line result; refusals and operational failures go to standard error. The
CLI does not print a JSON report, write a SARIF file or open the scan report page; those are out of
scope. A static scan never creates a "runs" row, a run branch or a run report, and it never starts
the LLM stage.

---

## STORY: BSB-37-PENDING-3

**Title:** Run a full static-then-LLM security scan from the command line
**Epic:** BSB-37 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-16, MVP

### Story
As a **skill author who is a project member**, I want **to run the full static-then-LLM security scan of a skill branch from the terminal**, so that **I get the same two-stage evidence the Full security check produces, without a test run or the web interface**.

### Acceptance Criteria

Scenario: A full scan runs the static stage then the project's configured LLM model and records both
Given Ada's token and local "users" row 42, her "project_members" row for Project Atlas (id 7), the source-control integration 3, a stub source-control provider listing branch "build/sdlc-fix-bug-reproduce" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", a stub catalog tree in which that ref contains "skills/sdlc-fix-bug-reproduce/SKILL.md", a "skill_bundles" row for that skill and commit with bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08" and s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", an empty "scans" table with a "scans" id sequence whose next value is 11, an empty "runs" table, a "projects" row id 7 with llm_scan_model_profile_id 8 and llm_scan_model_tier "medium", an "integrations" row id 8 with project_id 7, kind "ai_model", config {"name": "Default", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-opus-5-5", "medium": "claude-sonnet-5-5", "low": "claude-haiku-5-5"}} and secret_ref "skill-builder/7/integration-8", a secret store holding "sk-ant-test-3c9e" at "skill-builder/7/integration-8", a stub static scanner that writes the clean report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []}, and a stub model endpoint that returns HTTP 200 with body {"model": "claude-sonnet-5-5", "findings": [{"severity": "CRITICAL", "rule": "LLM-001", "file": "SKILL.md", "line": 3}, {"severity": "HIGH", "rule": "LLM-101", "file": "scripts/run.sh", "line": 14}]}
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce`
Then the process exits with status 0 and prints "Static scan 11 completed with verdict PASS; LLM scan 12 completed with model claude-sonnet-5-5 and 2 findings.", the static "scans" row id 11 has stage "static", state "completed" and verdict "pass", the LLM "scans" row id 12 has stage "llm", state "completed", model "claude-sonnet-5-5", model_profile_id 8 and verdict NULL, two "scan_findings" rows exist for scan 12 with severity, rule, file and line matching the report, no "runs" row exists, and the stub model endpoint received a request naming model "claude-sonnet-5-5"

Scenario: A failing static stage stops the LLM stage and exits with status 1
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), the source-control integration 3, the packed bundle and catalog tree of the first scenario, an empty "scans" table with a "scans" id sequence whose next value is 11, an empty "runs" table, a "projects" row id 7 with llm_scan_model_profile_id 8 and llm_scan_model_tier "medium", an "integrations" row id 8 with project_id 7, kind "ai_model" and a complete high, medium and low mapping, a secret store holding "sk-ant-test-3c9e" at "skill-builder/7/integration-8", a stub model endpoint whose request counter is 0, and a stub static scanner that writes the report {"score": 41, "recommendation": "DO_NOT_INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "CRITICAL", "rule": "SS-001", "file": "SKILL.md", "line": 3}]}
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce`
Then the process exits with status 1 and prints "Static scan 11 completed with verdict FAIL; LLM scan skipped: static scan did not pass.", the "scans" row id 11 has stage "static", state "completed" and verdict "fail", no "scans" row with stage "llm" exists, the stub model endpoint received 0 requests, and no "runs" row exists

Scenario: An unavailable or failed LLM stage is recorded and reported without blocking a static pass
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), the source-control integration 3, the packed bundle and catalog tree of the first scenario, an empty "scans" table with a "scans" id sequence whose next value is 11, an empty "runs" table, a "projects" row id 7 with llm_scan_model_profile_id NULL and llm_scan_model_tier NULL, an "integrations" row id 8 with project_id 7, kind "ai_model" and a complete high, medium and low mapping, a secret store holding "sk-ant-test-3c9e" at "skill-builder/7/integration-8", a stub static scanner that writes the clean report, a stub LLM scanner that starts at "2026-11-16T11:00:00Z" and writes no report, and a fake clock
When Ada runs the full scan once, and then again after setting the project's llm_scan_model_profile_id to 8 and llm_scan_model_tier to "medium", with the fake clock reaching "2026-11-16T11:10:01Z" during the second invocation while the LLM scan is still running
Then the first invocation exits with status 0 and prints "Static scan 11 completed with verdict PASS; LLM scan unavailable: No LLM scan model profile is configured for this project.", the second invocation exits with status 1 and prints "Static scan 11 completed with verdict PASS; LLM scan 13 failed: LLM scan exceeded the ten-minute limit.", the static "scans" row id 11 is reused with state "completed" and verdict "pass" for both invocations, the first LLM "scans" row id 12 has state "unavailable" and failure_reason "No LLM scan model profile is configured for this project.", the second LLM "scans" row id 13 has state "failed" and failure_reason "LLM scan exceeded the ten-minute limit.", and neither invocation creates a "runs" row

Scenario: A full scan with a missing, unprivileged or non-member identity is refused
Given Carol's verified token whose "cognito:groups" claim carries "skill-builders" and whose local "users" row 44 has no "project_members" row for Project Atlas (id 7), an empty "SKILL_BUILDER_TOKEN" environment variable, a token whose signature fails "CognitoProvider" verification, a packed bundle for skill "sdlc-fix-bug-reproduce", a stub static scanner whose container-start counter is 0, and a stub model endpoint whose request counter is 0
When the CLI `scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref build/sdlc-fix-bug-reproduce` is invoked with no token, with the unverifiable token, and with Carol's token
Then each invocation exits with status 2 and writes "Set SKILL_BUILDER_TOKEN to a Cognito ID token.", "SKILL_BUILDER_TOKEN is not a valid or unexpired Cognito token." and "You are not a member of this project." to standard error respectively, no "scans" row is created, the stub static scanner's container-start counter remains 0, and the stub model endpoint received 0 requests

Scenario: A full scan refuses a ref that lacks the skill and never starts either stage
Given Ada's token, local "users" row 42 and "project_members" row for Project Atlas (id 7), the source-control integration 3, a stub source-control provider that lists branch "main" for repository "saraavrnd/bheembhai-skills", a stub catalog tree in which ref "main" does not contain "skills/sdlc-fix-bug-reproduce/", a stub static scanner whose container-start counter is 0, and a stub model endpoint whose request counter is 0
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-reproduce --skills-ref main`
Then the process exits with status 2, writes "The selected skills branch does not contain skill sdlc-fix-bug-reproduce." to standard error, no "scans" row is created, the stub static scanner's container-start counter remains 0, and the stub model endpoint received 0 requests

### Covered requirements (traceability)
- FR-118

### Out of scope
The static-only scan (BSB-37-PENDING-2) and the `run` command (BSB-37-PENDING-1); the full-scan
service, its route, its static-first rule and its report (BSB-32-PENDING-2); the LLM scan's
credential and network isolation (BSB-32-PENDING-3); the unavailable and failed LLM outcomes
(BSB-32-PENDING-4); configuring the project's LLM-scan model (BSB-32-PENDING-1); the static scan
service (BSB-31); starting, executing or verifying a run (BSB-24, BSB-26 and BSB-29); a per-scan
model override; accepting an LLM finding; sending the scan result to the platform.

### Notes / dependencies
Depends on BSB-18-PENDING-1 and BSB-18-PENDING-3 for the verified token and group gate, on
BSB-18-PENDING-2 for the local "users" row, on BSB-22-PENDING-1 and BSB-22-PENDING-3 for the
project and the shared membership check, on BSB-23-PENDING-2 for the source-control integration,
on BSB-25-PENDING-1 and -2 for resolving the ref to a commit and packing or reusing the bundle, on
BSB-31-PENDING-1 for the static stage and the "scans" rows, on BSB-32-PENDING-2 for the full-scan
service and the static-first rule, on BSB-32-PENDING-1 for the project's existing "llm_scan_model_profile_id" and "llm_scan_model_tier" settings, and on
BSB-32-PENDING-4 for the unavailable and failed LLM outcomes and their exact failure reasons. Both
CLI scan commands create "scans" rows with `build_id` NULL because no build requested them; the
data-model stage must keep "scans.build_id" nullable, and the scan row still carries no
`project_id`.

This story owns the `scan` command's full mode. The command resolves the skill and ref through
BSB-25's packaging path, then calls the same full-scan service BSB-32-PENDING-2 uses with the
project, skill, commit SHA and bundle and no build id; BSB-32-PENDING-2 must expose that service
independently of its build-keyed route, and the CLI does not call the build-page route and creates
no build-specific record. The service runs the static stage first and starts the LLM stage only when
the static verdict for that commit and bundle is "pass"; the CLI adds no per-scan model override
and no `--model-profile` or `--model` flag, so a request that carries one is a usage error. The
LLM model is the project's configured LLM-scan profile and tier, exactly as BSB-32-PENDING-1
requires.

Exit status is the scan's contract for CI: 0 when the static stage passes and the LLM stage
completes or is recorded "unavailable"; 1 when the static verdict is "fail" or the LLM stage state
is "failed"; 2 when the request is refused, the ref or skill is missing, authentication or
membership fails, or the static stage cannot complete. A full scan creates no "runs" row, run
branch or run report, and an LLM finding never changes the static verdict or blocks anything;
the scan's advisory meaning is BSB-32's. The scan report is read through BSB-31-PENDING-5's
GET "/scans/{id}" route when the author wants the detailed page; the CLI prints only the one-line
summary.

---

## STORY: BSB-37-PENDING-4

**Title:** Save a named suite of runs with entries and expectations
**Epic:** BSB-37 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-16, Later

### Story
As a **skill author who is a project member**, I want **to save a named suite of runs whose entries name a skill, input branch, context and expectation**, so that **I can repeat the same regression checks without rebuilding each run by hand**.

### Acceptance Criteria

Scenario: A project member saves a named suite with two entries
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), an open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", an open build 8 with skill "sdlc-fix-bug-triage" and branch "build/sdlc-fix-bug-triage", an "integrations" row id 3 with project_id 7, kind "github", config {"repository": "saraavrnd/skill-builder-sandbox", "base_branch": "main", "test_only": true} and secret_ref "skill-builder/7/integration-3", a stub source-control provider that lists branch "test/atlas/bug-42" for repository "saraavrnd/skill-builder-sandbox", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md" and ref "build/sdlc-fix-bug-triage" contains "skills/sdlc-fix-bug-triage/SKILL.md", an "integrations" row id 4 with project_id 7, kind "ai_model", config {"name": "Default", "test_only": true} and a complete high, medium and low tier mapping, an empty "suites" table with a "suites" id sequence whose next value is 5, and a builder clock reading "2026-11-16T11:00:00Z"
When Ada submits the suite name "Nightly bug-fix regression", model profile 4, tier "medium", and entries [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": "", "upstream_handoff": "", "expected_verdict": "pass"}, {"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-42", "workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": "Add the exact command.", "upstream_handoff": "", "expected_verdict": "pass"}] on POST "/projects/7/suites"
Then the response is HTTP 201 with a body containing "Suite 5 Nightly bug-fix regression created.", exactly one "suites" row exists with id 5, project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled false, created_by 42 and created_at "2026-11-16T11:00:00Z", its definition is {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": null, "upstream_handoff": null}, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-42", "context": {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": "Add the exact command.", "upstream_handoff": null}, "expectations": {"final_verdict": "pass"}}]}, and a follow-up GET "/projects/7/suites/5" returns HTTP 200 rendering "Suite: Nightly bug-fix regression", "Entries: 2", "Entry 1: sdlc-fix-bug-reproduce on test/atlas/bug-42, expected PASS", "Entry 2: sdlc-fix-bug-triage on test/atlas/bug-42, expected PASS" and "Nightly schedule: off"

Scenario: A suite name that already exists in the project is refused
Given Ada's "project_members" row for Project Atlas (id 7), a "suites" row id 5 with project_id 7 and name "Nightly bug-fix regression", and a "suites" id sequence whose next value is 6
When Ada submits the name "Nightly bug-fix regression" with one entry for skill "sdlc-fix-bug-reproduce" on input branch "test/atlas/bug-42" with expected verdict "pass" on POST "/projects/7/suites"
Then the response is HTTP 422 with the message "A suite named 'Nightly bug-fix regression' already exists in this project.", no second "suites" row is created, and the "suites" row id 5 is unchanged

Scenario: A blank or over-long suite name is refused
Given Ada's "project_members" row for Project Atlas (id 7), an empty "suites" table, and one submitted entry for skill "sdlc-fix-bug-reproduce" on input branch "test/atlas/bug-42" with expected verdict "pass"
When Ada submits a suite name of "   " and then a suite name of 101 "x" characters on POST "/projects/7/suites"
Then the first response is HTTP 422 with the message "Choose a name for the suite.", the second response is HTTP 422 with the message "The suite name must be 100 characters or fewer.", and no "suites" row is created

Scenario: A suite with no entries or an entry without a skill or input branch is refused
Given Ada's "project_members" row for Project Atlas (id 7), an empty "suites" table, a valid name "Nightly bug-fix regression", and the two open builds and catalog tree of the first scenario
When Ada submits the suite with an empty entries list, then with one entry whose "skill" is "", then with one entry whose "input_branch" is ""
Then the three responses are HTTP 422 with the messages "Add at least one entry to the suite.", "Each suite entry must name a skill." and "Each suite entry must name an input branch." respectively, and no "suites" row is created

Scenario: An unknown skill, a missing input branch or an invalid expectation is refused
Given Ada's "project_members" row for Project Atlas (id 7), an empty "suites" table, an open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", the source-control integration 3, a stub source-control provider that lists only branch "test/atlas/bug-42" for repository "saraavrnd/skill-builder-sandbox", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md" and neither an open build nor ref "main" contains "skills/sdlc-fix-bug-removed/", and a valid name "Nightly bug-fix regression"
When Ada submits one entry naming skill "sdlc-fix-bug-removed", then one entry naming skill "sdlc-fix-bug-reproduce" with input branch "test/atlas/bug-99", then one entry for skill "sdlc-fix-bug-reproduce" on input branch "test/atlas/bug-42" with expected verdict "sometimes"
Then the three responses are HTTP 422 with the messages "Unknown skill sdlc-fix-bug-removed.", "The selected input branch does not exist in the sandbox repository." and "The expected final verdict must be pass, fail or any." respectively, and no "suites" row is created

Scenario: A model profile or tier that a run could not use is refused
Given Ada's "project_members" row for Project Atlas (id 7), an empty "suites" table, an open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", the source-control integration 3, a stub source-control provider that lists branch "test/atlas/bug-42" for repository "saraavrnd/skill-builder-sandbox", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md", a valid name "Nightly bug-fix regression" with one valid entry for skill "sdlc-fix-bug-reproduce" on input branch "test/atlas/bug-42" expecting "pass", an "integrations" row id 4 with project_id 7, kind "ai_model", config {"name": "Default", "test_only": true} and a complete high, medium and low mapping, an "integrations" row id 6 with project_id 7, kind "ai_model" and config {"name": "Production profile", "test_only": false}, an "integrations" row id 9 with project_id 8 and kind "ai_model", and an "integrations" row id 8 with project_id 7 and kind "jira"
When Ada submits the suite with model profile 6, then with model profile 9, then with model profile 8, then with model profile 4 and tier "ultra"
Then the first three responses are HTTP 422 with the message "The selected model profile is not available for runs in this project.", the fourth response is HTTP 422 with the message "The model tier must be high, medium or low.", and no "suites" row is created

Scenario: A signed-in skill author who is not a project member cannot save a suite
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), and an empty "suites" table
When Carol opens GET "/projects/7/suites/new" and submits a valid suite on POST "/projects/7/suites"
Then GET "/projects/7/suites/new" returns HTTP 403 with the message "You are not a member of this project.", the POST returns HTTP 403 with the same message, and no "suites" row is created

### Covered requirements (traceability)
- FR-119
- FR-120

### Out of scope
Running a saved suite (BSB-37-PENDING-5); scheduling it (BSB-37-PENDING-6); recording scheduled
results (BSB-37-PENDING-7); editing, renaming, duplicating or deleting a saved suite; importing a
suite from `suites/name.yaml`; per-entry model profiles or tiers; accepting an entry's expectation
before the run exists; project-level suite lists beyond the project page; a suite entry that names
a build instead of a skill; a suite entry that targets a branch other than the skill's open build
branch or `main`.

### Notes / dependencies
Depends on BSB-18 for the signed-in skill author and the per-request gate, on BSB-22-PENDING-1
and BSB-22-PENDING-3 for Project Atlas, the "project_members" rows and the shared membership
check, on BSB-19 and BSB-21 for open "builds" rows and their branches, on BSB-23-PENDING-2 for
the source-control integration and the sandbox branches, on BSB-23-PENDING-3 and -6 for the
test-purpose "ai_model" profiles and their tier mapping, on BSB-24-PENDING-2 and -3 for the
context field validation and messages, and on BSB-24-PENDING-4 for the model-profile and tier
validation and messages.

The durable system of record is the builder's own "suites" table from ADR SK-001 section 9. This
story adds `suites.created_by`, `suites.schedule_enabled` and `suites.created_at` and fixes the
suite's definition shape; the data-model stage must record them. `suites.definition` is JSONB with the shape
{"model_profile_id": integer, "tier": "high" | "medium" | "low", "entries": [{"skill": string,
"input_branch": string, "context": {"workflow": string or null, "step": string or null,
"reviewer_feedback": string or null, "upstream_handoff": string or null}, "expectations":
{"final_verdict": "pass" | "fail" | "any"}}]}. The suite-level model profile and tier are run
inputs stored once so the suite is repeatable; they are not entry fields. `suites.source_path`
stays NULL for a suite saved in the builder. The suite is project-scoped and its name is unique
within the project (`UNIQUE (project_id, name)`); the "suites" id sequence is the durable key.

Save-time validation reads the current records before writing: membership first, then the name,
then the entries, then the model settings; the first failure is returned and the whole request is
one transaction, so a refused save writes nothing. Each entry's skill must exist as an open build's
skill or on the catalog `main` ref; each entry's input branch must exist in the project's sandbox
repository; an entry's expectation is required and is one of "pass", "fail" or "any". A missing
source-control integration makes the request fail with "A source-control integration is required to
save a suite." rather than saving an entry that can never run. The form at GET
"/projects/7/suites/new" is served only to a project member and lists only the project's open-build
skills and sandbox branches, so the author chooses from records rather than free text; the route's
submit-time validation is authoritative.

The suite does not resolve the skill to a branch at save time beyond checking that it exists; that
resolution happens at run time (BSB-37-PENDING-5), because a build branch can move between the save
and the run and a suite should test the branch as it is then. The skill's open build branch is the
default skills ref for an entry; a skill that exists only on `main` uses `main` and records no
build id (see PENDING-5). Deleting a build does not delete the suite; the entry is handled at run
time by PENDING-5's skip record.

---

## STORY: BSB-37-PENDING-5

**Title:** Run a saved suite and grade each entry against its expectation
**Epic:** BSB-37 · **Release:** Later · **Estimate:** 8 · **Labels:** FA-16, Later

### Story
As a **skill author who is a project member**, I want **to run a saved suite and see each entry's run graded against its expected final verdict**, so that **I can tell in one pass which parts of the regression suite still behave as expected**.

### Acceptance Criteria

Scenario: A project member runs a two-entry suite and one run is created per entry
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled false, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": null, "upstream_handoff": null}, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-42", "context": {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": "Add the exact command.", "upstream_handoff": null}, "expectations": {"final_verdict": "pass"}}]}, open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", open build 8 with skill "sdlc-fix-bug-triage" and branch "build/sdlc-fix-bug-triage", the source-control integration 3, a stub source-control provider that lists branches "build/sdlc-fix-bug-reproduce", "build/sdlc-fix-bug-triage" and "test/atlas/bug-42", a stub catalog tree that contains each skill at its build branch, the "ai_model" integration 4 with a complete high, medium and low mapping, an empty "runs" table with a "runs" id sequence whose next value is 21, an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31, and a builder clock reading "2026-11-16T11:00:00Z"
When Ada submits the "Run suite" control on GET "/projects/7/suites/5", which calls POST "/projects/7/suites/5/runs" with an empty body
Then the response is HTTP 201 with {"suite_run_id": 31, "runs": [{"entry_index": 1, "run_id": 21}, {"entry_index": 2, "run_id": 22}]}, exactly one "suite_runs" row exists with id 31, suite_id 5, project_id 7, user_id 42, trigger "manual", scheduled_for NULL, state "running", entries_total 2, entries_matched 0, entries_mismatched 0, entries_skipped 0, entries_failed 0 and started_at "2026-11-16T11:00:00Z", the "runs" row id 21 has project_id 7, user_id 42, build_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", input_branch "test/atlas/bug-42", context {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": null, "upstream_handoff": null}, model_profile_id 4, tier "medium", state "requested" and kind "run", the "runs" row id 22 has project_id 7, user_id 42, build_id 8, skill "sdlc-fix-bug-triage", skills_ref "build/sdlc-fix-bug-triage", input_branch "test/atlas/bug-42", context {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": "Add the exact command.", "upstream_handoff": null}, model_profile_id 4, tier "medium", state "requested" and kind "run", exactly two "suite_run_entries" rows exist with suite_run_id 31, entry_index 1 and 2, run_id 21 and 22, expected_verdict "pass", state "pending" and actual_verdict NULL, and no execution worker has started a container yet

Scenario: Each entry is graded against its expectation when its run reaches a terminal verdict
Given the "suite_runs" row id 31 and "runs" rows 21 and 22 of the first scenario, the "suite_run_entries" rows for entries 1 and 2, and a builder clock reading "2026-11-16T11:05:00Z"
When run 21 reaches a terminal state with final_verdict "pass" and run 22 reaches a terminal state with final_verdict "fail"
Then the "suite_run_entries" row for entry 1 has run_id 21, expected_verdict "pass", actual_verdict "pass", state "matched" and reason NULL, the "suite_run_entries" row for entry 2 has run_id 22, expected_verdict "pass", actual_verdict "fail", state "mismatched" and reason "Expected PASS, got FAIL.", the "suite_runs" row id 31 has state "completed", entries_matched 1, entries_mismatched 1, entries_skipped 0, entries_failed 0 and finished_at "2026-11-16T11:05:00Z", and GET "/projects/7/suites/5" renders "Suite run 31", "manual", "completed", "1 matched, 1 mismatched, 0 skipped, 0 failed", "Entry 1: sdlc-fix-bug-reproduce, Run 21, expected PASS, actual PASS, matched" and "Entry 2: sdlc-fix-bug-triage, Run 22, expected PASS, actual FAIL, mismatched"

Scenario: An entry whose skill has disappeared is skipped and the other entries still run
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled false, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-removed", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, Ada's "project_members" row for Project Atlas (id 7), open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", open build 8 with skill "sdlc-fix-bug-triage" and branch "build/sdlc-fix-bug-triage", a stub catalog tree in which each open build branch contains its skill and neither an open build nor ref "main" contains "skills/sdlc-fix-bug-removed/", the source-control integration 3, a stub source-control provider that lists branches "build/sdlc-fix-bug-reproduce", "build/sdlc-fix-bug-triage" and "test/atlas/bug-42", the "ai_model" integration 4, an empty "runs" table with a "runs" id sequence whose next value is 21, and an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31
When Ada submits the "Run suite" control on GET "/projects/7/suites/5"
Then the response is HTTP 201 and its "runs" list has two entries for entry_index 1 and 2, exactly two "runs" rows exist with ids 21 and 22, the "suite_run_entries" row for entry 3 has run_id NULL, expected_verdict "pass", actual_verdict NULL, state "skipped" and reason "Unknown skill sdlc-fix-bug-removed.", the "suite_runs" row id 31 has entries_total 3, entries_skipped 1 and state "running", and the other two suite entries still have run ids 21 and 22

Scenario: An entry whose run cannot be created is failed while the other entries still run
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled false, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-99", "context": null, "expectations": {"final_verdict": "pass"}}]}, Ada's "project_members" row for Project Atlas (id 7), open build 7 with skill "sdlc-fix-bug-reproduce", open build 8 with skill "sdlc-fix-bug-triage", the source-control integration 3, a stub source-control provider that lists branch "test/atlas/bug-42" but not "test/atlas/bug-99", a stub catalog tree that contains each skill at its open build branch, the "ai_model" integration 4, an empty "runs" table with a "runs" id sequence whose next value is 21, and an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31
When Ada submits the "Run suite" control on GET "/projects/7/suites/5"
Then the "suite_run_entries" row for entry 1 links the one existing "runs" row id 21, the "suite_run_entries" row for entry 2 has run_id NULL, state "failed" and reason "The selected input branch does not exist in the sandbox repository.", the "suite_runs" row id 31 has entries_total 2, entries_skipped 0, entries_failed 1 and state "running", and GET "/projects/7/suites/5" renders "Entry 2: sdlc-fix-bug-triage, no run, expected PASS, failed: The selected input branch does not exist in the sandbox repository."

Scenario: A suite whose saved model profile is no longer available fails before any run starts
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled false, created_by 42 and definition {"model_profile_id": 7, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, Ada's "project_members" row for Project Atlas (id 7), an open build for "sdlc-fix-bug-reproduce", the source-control integration 3, an "integrations" table with no row id 7 for project 7, an empty "runs" table, and an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31
When Ada submits the "Run suite" control on GET "/projects/7/suites/5"
Then exactly one "suite_runs" row exists with id 31, suite_id 5, trigger "manual", state "failed", entries_total 1, entries_matched 0, entries_mismatched 0, entries_skipped 0, entries_failed 1 and failure_reason "The suite's model profile is no longer available.", the single "suite_run_entries" row has run_id NULL, state "failed" and the same reason, no "runs" row is created, and GET "/projects/7/suites/5" renders "Suite run 31: failed" and "The suite's model profile is no longer available."

Scenario: A signed-in skill author who is not a project member cannot run a suite
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL and created_by 42, and empty "runs" and "suite_runs" tables
When Carol opens GET "/projects/7/suites/5" and submits POST "/projects/7/suites/5/runs"
Then GET "/projects/7/suites/5" returns HTTP 403 with the message "You are not a member of this project.", the POST returns HTTP 403 with the same message, no "runs" row is created, and no "suite_runs" row is created

### Covered requirements (traceability)
- FR-121

### Out of scope
Saving, editing or deleting a suite (BSB-37-PENDING-4); scheduling a suite
(BSB-37-PENDING-6); the scheduled result record (BSB-37-PENDING-7); a command-line `suite`
command (the suite-run service is shared, but this epic adds no such client); starting, executing or
verifying an individual run (BSB-24, BSB-25, BSB-26, BSB-27 and BSB-29); retrying a mismatched or
failed entry; stopping a suite after a mismatch; parallel versus sequential execution of entries
beyond the order they are requested; a per-entry model profile or tier; a suite entry targeting a
branch other than the skill's open build branch or `main`; editing the suite from the run page.

### Notes / dependencies
Depends on BSB-37-PENDING-4 for the "suites" row and its definition, on BSB-18 for the signed-in
author and the per-request gate, on BSB-22-PENDING-1 and BSB-22-PENDING-3 for the project and the
shared membership check, on BSB-19 and BSB-21 for open "builds" rows and their branches, on
BSB-23-PENDING-2 for the source-control integration and sandbox branches, on BSB-23-PENDING-3
and -6 for the "ai_model" profiles, on BSB-24-PENDING-1 for the run-start service and the "runs"
row, on BSB-24-PENDING-2 and -3 for the context fields, on BSB-24-PENDING-4 for the model profile
and tier, on BSB-25 for packaging and the run branch, on BSB-27 for the run-start preflight, on
BSB-26 for execution, and on BSB-29 for "runs.final_verdict".

The durable system of record is the builder's own database: one "suite_runs" row for the
execution and one "suite_run_entries" row per suite entry, plus one "runs" row per entry that
could be requested. The data-model stage must add `suite_runs` (id, suite_id, project_id, user_id,
trigger, scheduled_for, state, entries_total, entries_matched, entries_mismatched,
entries_skipped, entries_failed, failure_reason, started_at, finished_at) and
`suite_run_entries` (id, suite_run_id, entry_index, run_id, expected_verdict, actual_verdict,
state, reason, UNIQUE (suite_run_id, entry_index)). Both tables are the same ones PENDING-6 and
PENDING-7 use; this story is the manual execution path, not a separate model.

Each entry is resolved at run time: the skill's open build branch when an open build exists,
otherwise `main` when the skill exists there, otherwise the entry is skipped with "Unknown skill" followed by the skill name, and no run. The `runs` row for an entry uses that build id (NULL for `main`), the entry's
skill, that skills ref, the entry's input branch, the entry's context and the suite's model
profile and tier. The run-start service is BSB-24's, extended for a skill-and-ref request exactly
as BSB-37-PENDING-1 uses it; packaging, preflight, execution and verification are unchanged. The
suite run requests the entries in their stored order; it does not wait for each run in the request
handler.

Grading is by "runs.final_verdict" only: expected "pass" or "fail" must equal the final verdict;
expected "any" matches either and exists so an exploratory entry can still be recorded; a run
that reaches a terminal state without a final verdict is "failed" with "The run ended without a
final verdict."; a request that cannot create a run is "failed" with the run-start service's exact
refusal message; a missing skill is "skipped". A "suite_runs" row is "running" while any entry is
pending or its run is not terminal, and becomes "completed" when every entry is terminal; it is
"failed" with `failure_reason` when no entry can be attempted (a missing model profile, a
non-member suite owner, or an unreadable definition). The counts always add up to
`entries_total`. The suite run is not a second execution engine: every entry's run is created by
the same run-start service and graded by the same verifier result.

---

## STORY: BSB-37-PENDING-6

**Title:** Schedule a saved suite for nightly execution
**Epic:** BSB-37 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-16, Later

### Story
As a **skill author who is a project member**, I want **to schedule a saved suite for nightly execution**, so that **the regression checks run without anyone remembering to start them**.

### Acceptance Criteria

Scenario: A project member enables the nightly schedule for a saved suite
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", schedule_enabled false and created_by 42, and a builder clock reading "2026-11-16T11:00:00Z"
When Ada submits the "Nightly schedule" toggle as on, which calls POST "/projects/7/suites/5/schedule" with {"enabled": true}
Then the response is HTTP 200 with a body containing "Suite 5 scheduled nightly at 02:00 UTC.", the "suites" row id 5 has schedule_enabled true and no other column changed, and GET "/projects/7/suites/5" renders "Nightly schedule: on (02:00 UTC)"

Scenario: A project member turns the nightly schedule off
Given the "suites" row id 5 with schedule_enabled true, Ada's "project_members" row for Project Atlas (id 7), and a builder clock reading "2026-11-16T12:00:00Z"
When Ada submits POST "/projects/7/suites/5/schedule" with {"enabled": false}
Then the response is HTTP 200 with a body containing "Suite 5 schedule turned off.", the "suites" row id 5 has schedule_enabled false and no other column changed, and GET "/projects/7/suites/5" renders "Nightly schedule: off"

Scenario: A nightly tick creates exactly one scheduled suite run for the date
Given two "suites" rows: id 5 for project 7 with name "Nightly bug-fix regression", source_path NULL, schedule_enabled true, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, and id 6 for project 7 with name "Nightly triage regression", source_path NULL, schedule_enabled true, created_by 43 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, local "users" rows 42 and 43, "project_members" rows (project_id 7, role "member") for user_id 42 and user_id 43, the source-control integration 3, the "ai_model" integration 4, open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", open build 8 with skill "sdlc-fix-bug-triage" and branch "build/sdlc-fix-bug-triage", a stub source-control provider that lists branch "test/atlas/bug-42" and both build branches, a stub catalog tree that contains each skill at its build branch, an empty "runs" table with a "runs" id sequence whose next value is 21, an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31, and a builder clock reading "2026-11-17T01:59:59Z"
When the nightly scheduler ticks at "2026-11-17T02:00:00Z"
Then exactly two "suite_runs" rows exist with ids 31 and 32, suite_id 5 and 6, project_id 7, user_id 42 and 43, trigger "scheduled", scheduled_for "2026-11-17" and state "running", exactly two "runs" rows exist with ids 21 and 22 for the two entries, and GET "/projects/7/suites/5" renders "Suite run 31" and "2026-11-17" with trigger "scheduled"

Scenario: A second nightly tick on the same date creates no duplicate execution
Given the "suite_runs" row id 31 with suite_id 5, trigger "scheduled", scheduled_for "2026-11-17" and one entry that links "runs" row id 21, the "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled true and created_by 42, and a builder clock reading "2026-11-17T02:00:00Z"
When the nightly scheduler ticks at "2026-11-17T02:05:00Z"
Then no second "suite_runs" row exists for suite 5 with scheduled_for "2026-11-17", exactly one "suite_runs" row exists for suite 5 on that date, and no "runs" row is created for the second tick

Scenario: A disabled suite is not scheduled
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled false and created_by 42, an empty "suite_runs" table, and a builder clock reading "2026-11-17T01:59:59Z"
When the nightly scheduler ticks at "2026-11-17T02:00:00Z"
Then no "suite_runs" row is created for suite 5, and "suites.schedule_enabled" remains false

Scenario: A signed-in skill author who is not a project member cannot change a suite's schedule
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), and a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled false and created_by 42
When Carol submits POST "/projects/7/suites/5/schedule" with {"enabled": true}
Then the response is HTTP 403 with the message "You are not a member of this project.", the "suites" row id 5 has schedule_enabled false, and no "suite_runs" row is created

### Covered requirements (traceability)
- FR-122

### Out of scope
Saving, editing or deleting a suite (BSB-37-PENDING-4); running a suite manually
(BSB-37-PENDING-5); the per-entry scheduled result record (BSB-37-PENDING-7); a per-suite
schedule time other than 02:00 UTC; a cron expression or multiple schedules per suite; time zones
other than UTC; pausing a single night; notifications on success or failure; a schedule for
anything other than a saved suite; workflow orchestration in the builder.

### Notes / dependencies
Depends on BSB-37-PENDING-4 for the "suites" row and its `schedule_enabled` column, on
BSB-37-PENDING-5 for the suite-run service that creates the per-entry runs, on BSB-22-PENDING-1
and BSB-22-PENDING-3 for the project and the shared membership check, on BSB-18 for the
authenticated author, and on the run pipeline (BSB-24, BSB-25, BSB-26, BSB-27 and BSB-29) for
each entry's run.

This story owns the schedule control, the nightly scheduler tick and the `suite_runs` rows with
trigger "scheduled". The durable flag is `suites.schedule_enabled` from ADR SK-001 section 9's
"suites" table extended by PENDING-4; the data-model stage must record it. "Nightly" is fixed
here to 02:00 UTC and is not configurable: the first scheduler tick at or after 02:00 UTC on a
UTC date creates one scheduled execution for each suite whose flag is true, and later ticks on
the same date create none. The scheduler reads `suites.created_by` and uses that user as the
`suite_runs.user_id` and each `runs.user_id`; a suite whose creator is no longer a project member
is still ticked but its execution is recorded as failed by PENDING-7 rather than run under a stale
identity. The `UNIQUE (suite_id, scheduled_for)` constraint on `suite_runs` is the idempotency
guard; a duplicate insert is treated as already scheduled, not as an error.

The scheduler is a builder process, not a workflow engine: it starts no run of its own, and it
calls the same suite-run service PENDING-5 owns, which in turn calls the same run-start service
the web and CLI use. A suite is not scheduled at the moment of saving; saving leaves
`schedule_enabled` false until a member enables it. Turning the flag off affects only future
dates; a scheduled execution already running is not cancelled. No email, chat or webhook
notification is sent.

---

## STORY: BSB-37-PENDING-7

**Title:** Record every scheduled suite run's result, including skips and failures
**Epic:** BSB-37 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-16, Later

### Story
As a **skill author who is a project member**, I want **every scheduled suite run to record its date, state and each entry's outcome with the reason**, so that **I can tell what the night run proved and what it could not run, without reading logs**.

### Acceptance Criteria

Scenario: A scheduled suite run records each entry's matched or mismatched expectation
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", schedule_enabled true, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, Ada's "project_members" row for Project Atlas (id 7), open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", open build 8 with skill "sdlc-fix-bug-triage" and branch "build/sdlc-fix-bug-triage", the source-control integration 3, a stub source-control provider that lists "test/atlas/bug-42" and both build branches, a stub catalog tree that contains each skill at its build branch, the "ai_model" integration 4, an empty "runs" table with a "runs" id sequence whose next value is 21, an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31, and a fake clock reading "2026-11-17T02:00:00Z"
When the nightly scheduler ticks, runs 21 and 22 reach terminal states with final_verdict "pass" and "fail", and the fake clock advances to "2026-11-17T02:15:00Z"
Then the "suite_runs" row id 31 has suite_id 5, project_id 7, user_id 42, trigger "scheduled", scheduled_for "2026-11-17", state "completed", entries_total 2, entries_matched 1, entries_mismatched 1, entries_skipped 0, entries_failed 0, started_at "2026-11-17T02:00:00Z" and finished_at "2026-11-17T02:15:00Z", the "suite_run_entries" row for entry 1 has run_id 21, expected_verdict "pass", actual_verdict "pass", state "matched" and reason NULL, the "suite_run_entries" row for entry 2 has run_id 22, expected_verdict "pass", actual_verdict "fail", state "mismatched" and reason "Expected PASS, got FAIL.", and GET "/projects/7/suites/5" renders "2026-11-17", "scheduled", "1 matched, 1 mismatched, 0 skipped, 0 failed", "Entry 1: sdlc-fix-bug-reproduce, Run 21, expected PASS, actual PASS, matched" and "Entry 2: sdlc-fix-bug-triage, Run 22, expected PASS, actual FAIL, mismatched"

Scenario: A scheduled entry whose skill has disappeared is recorded as skipped
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled true, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-removed", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, Ada's "project_members" row for Project Atlas (id 7), open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md" and neither an open build nor ref "main" contains "skills/sdlc-fix-bug-removed/", the source-control integration 3, a stub source-control provider that lists "test/atlas/bug-42" and "build/sdlc-fix-bug-reproduce", the "ai_model" integration 4, an empty "runs" table with a "runs" id sequence whose next value is 21, an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31, and a builder clock reading "2026-11-17T02:00:00Z"
When the nightly scheduler ticks
Then exactly one "runs" row exists with id 21 for entry 1, the "suite_run_entries" row for entry 2 has run_id NULL, expected_verdict "pass", actual_verdict NULL, state "skipped" and reason "Unknown skill sdlc-fix-bug-removed.", the "suite_runs" row id 31 has entries_total 2, entries_skipped 1 and state "running" while entry 1 is still running, and GET "/projects/7/suites/5" renders "Entry 2: sdlc-fix-bug-removed, no run, expected PASS, skipped: Unknown skill sdlc-fix-bug-removed."

Scenario: A scheduled entry whose run cannot be created is recorded as failed while the other entries run
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled true, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-99", "context": null, "expectations": {"final_verdict": "pass"}}]}, Ada's "project_members" row for Project Atlas (id 7), open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", open build 8 with skill "sdlc-fix-bug-triage" and branch "build/sdlc-fix-bug-triage", the source-control integration 3, a stub source-control provider that lists "test/atlas/bug-42" and both build branches but not "test/atlas/bug-99", a stub catalog tree that contains each skill at its build branch, the "ai_model" integration 4, an empty "runs" table with a "runs" id sequence whose next value is 21, an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31, and a builder clock reading "2026-11-17T02:00:00Z"
When the nightly scheduler ticks
Then exactly one "runs" row exists with id 21 for entry 1, the "suite_run_entries" row for entry 2 has run_id NULL, state "failed" and reason "The selected input branch does not exist in the sandbox repository.", the "suite_runs" row id 31 has entries_total 2, entries_skipped 0, entries_failed 1 and state "running", and GET "/projects/7/suites/5" renders "Entry 2: sdlc-fix-bug-triage, no run, expected PASS, failed: The selected input branch does not exist in the sandbox repository."

Scenario: A scheduled run for a suite whose creator has left the project is recorded as failed
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled true, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}, {"skill": "sdlc-fix-bug-triage", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, no "project_members" row for project_id 7 and user_id 42, the source-control integration 3, open build 7 with skill "sdlc-fix-bug-reproduce", open build 8 with skill "sdlc-fix-bug-triage", a stub source-control provider that lists "test/atlas/bug-42" and both build branches, a stub catalog tree that contains each skill at its build branch, the "ai_model" integration 4, an empty "runs" table, an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31, and a builder clock reading "2026-11-17T02:00:00Z"
When the nightly scheduler ticks
Then exactly one "suite_runs" row exists with id 31, suite_id 5, project_id 7, user_id 42, trigger "scheduled", scheduled_for "2026-11-17", state "failed", entries_total 2, entries_matched 0, entries_mismatched 0, entries_skipped 0, entries_failed 2 and failure_reason "The suite owner is no longer a project member.", each "suite_run_entries" row has run_id NULL, state "failed" and the same reason, no "runs" row is created, and GET "/projects/7/suites/5" renders "Suite run 31: failed" and "The suite owner is no longer a project member."

Scenario: A scheduled run whose entry ended without a final verdict is recorded as failed
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled true, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, Ada's "project_members" row for Project Atlas (id 7), open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", the source-control integration 3, a stub source-control provider that lists "test/atlas/bug-42" and "build/sdlc-fix-bug-reproduce", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md", the "ai_model" integration 4, an empty "runs" table with a "runs" id sequence whose next value is 21, an empty "suite_runs" table with a "suite_runs" id sequence whose next value is 31, and a builder clock reading "2026-11-17T02:00:00Z"
When the nightly scheduler ticks and run 21 reaches a terminal state with state "failed" and final_verdict NULL
Then the "suite_run_entries" row for entry 1 has run_id 21, expected_verdict "pass", actual_verdict NULL, state "failed" and reason "The run ended without a final verdict.", the "suite_runs" row id 31 has state "completed", entries_total 1, entries_matched 0, entries_mismatched 0, entries_skipped 0 and entries_failed 1, and GET "/projects/7/suites/5" renders "Entry 1: sdlc-fix-bug-reproduce, Run 21, expected PASS, no final verdict, failed: The run ended without a final verdict."

Scenario: Scheduled results are kept across dates and are not overwritten by a later manual run
Given a "suites" row id 5 with project_id 7, name "Nightly bug-fix regression", source_path NULL, schedule_enabled true, created_by 42 and definition {"model_profile_id": 4, "tier": "medium", "entries": [{"skill": "sdlc-fix-bug-reproduce", "input_branch": "test/atlas/bug-42", "context": null, "expectations": {"final_verdict": "pass"}}]}, the "suite_runs" row id 31 for scheduled_for "2026-11-17" with state "completed" and one matched entry, the "runs" row id 21 linked from that entry, Ada's "project_members" row for Project Atlas (id 7), open build 7 with skill "sdlc-fix-bug-reproduce" and branch "build/sdlc-fix-bug-reproduce", the source-control integration 3, a stub source-control provider that lists "test/atlas/bug-42" and "build/sdlc-fix-bug-reproduce", a stub catalog tree in which ref "build/sdlc-fix-bug-reproduce" contains "skills/sdlc-fix-bug-reproduce/SKILL.md", the "ai_model" integration 4, a "suite_runs" id sequence whose next value is 32, a "runs" id sequence whose next value is 22, and a builder clock reading "2026-11-18T02:00:00Z"
When the nightly scheduler ticks for "2026-11-18" and the resulting run 22 finishes with final_verdict "pass", and then Ada runs the suite manually at "2026-11-18T09:00:00Z"
Then the "suite_runs" row id 31 still has scheduled_for "2026-11-17" and its entry still links run 21, a second scheduled "suite_runs" row id 32 exists with scheduled_for "2026-11-18" and its entry links run 22, a third manual "suite_runs" row id 33 exists with trigger "manual" and its entry links run 23, and GET "/projects/7/suites/5" renders the three rows "2026-11-17 scheduled completed", "2026-11-18 scheduled completed" and "2026-11-18 manual running" in that order

### Covered requirements (traceability)
- FR-123

### Out of scope
Saving or editing a suite (BSB-37-PENDING-4); running a suite manually beyond the results it
records (BSB-37-PENDING-5); enabling or disabling the schedule (BSB-37-PENDING-6); retrying,
cancelling or deleting a scheduled execution; a notification, email or webhook; retaining results
beyond the run-retention setting (BSB-34); a scheduled run that starts a workflow or a second
engine; a per-entry model profile; reading the detailed run report (BSB-33); changing a
scheduled execution after it finishes.

### Notes / dependencies
Depends on BSB-37-PENDING-4 for the "suites" row and its definition, on BSB-37-PENDING-5 for the
suite-run service, the `suite_runs` and `suite_run_entries` tables, the grading rules and the
suite page, on BSB-37-PENDING-6 for the `schedule_enabled` flag and the nightly tick, on
BSB-22-PENDING-1 and BSB-22-PENDING-3 for the project and the shared membership check, on BSB-18
for the authenticated author, and on BSB-24, BSB-25, BSB-26, BSB-27 and BSB-29 for each entry's
run and its `final_verdict`.

This story owns the scheduled execution's result record and its display. The durable system of
record is the builder's own `suite_runs` and `suite_run_entries` tables introduced by
BSB-37-PENDING-5, not a log file, a temporary shard or a notification. The data-model stage must
add the `failure_reason` column on `suite_runs` and the `reason` column on `suite_run_entries`
if PENDING-5's shape is implemented as written; the `UNIQUE (suite_id, scheduled_for)` constraint
is what makes a date's scheduled execution a single record. Every scheduled execution writes one
`suite_runs` row with `trigger` "scheduled" and `scheduled_for` equal to the UTC date, one
`suite_run_entries` row per suite entry in stored order, and one `runs` row per entry that could
be requested; skipped and failed entries have a NULL `run_id` and a reason, so "what did not run"
is visible without log reading.

The terminal states are PENDING-5's: "matched" when the expected verdict equals
`runs.final_verdict` or the expectation is "any"; "mismatched" when the two differ; "skipped"
when the skill no longer exists; "failed" when the run could not be requested or ended without a
final verdict. A `suite_runs` row is "completed" when every entry is terminal and "failed" with
`failure_reason` when no entry can be attempted. The counts always sum to `entries_total`. The
suite page renders the rows in reverse chronological order by `started_at`, with the scheduled
date, trigger, state, counts and each entry's skill, run id, expected verdict, actual verdict,
state and reason. Results are immutable once written: a later run creates a new `suite_runs` row
and never rewrites an earlier one, and the general retention and purge rules are BSB-34's. A
scheduled execution is not a second execution engine: every `runs` row is created by the same
run-start service and graded by the same verification result BSB-29 produces.

---

*Generated by `sdlc-plan-stories-write`. Coverage: FR-116, FR-117, FR-118, FR-119, FR-120, FR-121,
FR-122 and FR-123 all covered. Next steps: `sdlc-plan-epic-review` reviews the set on a different
model family; then `sdlc-plan-epic-sequence` orders the stories and `sdlc-tracker-sync` publishes
them to Jira.*
