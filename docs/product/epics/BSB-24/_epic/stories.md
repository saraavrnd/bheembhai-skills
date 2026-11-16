# Stories — BSB-24 (Run start & input selection)

Epic BSB-24 covers FR-037, FR-145, FR-146, FR-147, FR-148, FR-149 and FR-150. Decomposed into 4
vertical slices below; coverage of all 7 requirements verified.

The four slices are journeys an author completes from the run-start page of a test project: start
a run of their build by choosing the skills branch and input branch (PENDING-1), shape the step
context by choosing the workflow and step (PENDING-2), optionally add reviewer feedback or an
upstream handoff for a send-back or BLOCK case (PENDING-3), and choose the model profile and tier
(PENDING-4). Every slice ends in the same durable outcome — a "runs" row that records the choices
— and the page shows the chosen inputs before the run is created. Packaging, the run branch,
scanning and execution ride behind that request in BSB-25, BSB-27, BSB-31 and BSB-26 rather than
forming stories here.

> New stories use draft keys `BSB-24-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-24, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-24-PENDING-1

**Title:** Start a run from a build with the skills branch and input branch I choose
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **to start a run of my build in a test project by choosing the skills branch and the input branch**, so that **the run tests the skill content and the starting repository state I intend and its request records them for reproducibility**.

### Acceptance Criteria

Scenario: The run-start form offers the skills and input branch choices and summarizes them
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", an "integrations" row id 3 with project_id 7, kind "github", config {"repository": "saraavrnd/skill-builder-sandbox", "base_branch": "main", "test_only": true} and secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at path "skill-builder/7/integration-3", and a stub source-control provider that lists branches ["main", "build/bug-fix-resolver", "test/saraav/fix-reproduce"] for repository "saraavrnd/bheembhai-skills" and ["main", "test/atlas/bug-42", "skilltest/20"] for repository "saraavrnd/skill-builder-sandbox"
When Ada opens GET "/projects/7/runs/new?build=7"
Then the response is HTTP 200 rendering the heading "Start a test run in Project Atlas", the "Skills branch" select lists "main", "build/bug-fix-resolver" and "test/saraav/fix-reproduce" with "build/bug-fix-resolver" selected, the "Input branch" select lists "main", "test/atlas/bug-42" and "skilltest/20" with "main" selected, and the "Chosen inputs" summary renders "Build: 7 bug-fix-resolver", "Skills branch: build/bug-fix-resolver" and "Input branch: main"

Scenario: A project member starts a run and the run request records the chosen branches
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", an "integrations" row id 3 with project_id 7, kind "github", config {"repository": "saraavrnd/skill-builder-sandbox", "base_branch": "main", "test_only": true} and secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at path "skill-builder/7/integration-3", an "integrations" row id 4 with project_id 7, kind "ai_model", config {"name": "Default", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-opus-5-5", "medium": "claude-sonnet-5-5", "low": "claude-haiku-5-5"}, "test_only": true} and secret_ref "skill-builder/7/integration-4", a stub source-control provider that lists branches ["main", "build/bug-fix-resolver", "test/saraav/fix-reproduce"] for repository "saraavrnd/bheembhai-skills" and ["main", "test/atlas/bug-42", "skilltest/20"] for repository "saraavrnd/skill-builder-sandbox", a stub catalog tree in which ref "build/bug-fix-resolver" contains "skills/bug-fix-resolver/SKILL.md", an empty "runs" table with a "runs" id sequence whose next value is 21, a builder clock reading "2026-11-16T11:00:00Z", a stub static scanner whose request counter is 0, and an agent stub whose container-start counter is 0
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 201 with a body containing "Run 21 requested for build 7 in Project Atlas.", exactly one "runs" row exists with id 21, project_id 7, user_id 42, build_id 7, skill "bug-fix-resolver", skills_ref "build/bug-fix-resolver", skills_commit_sha NULL, input_branch "test/atlas/bug-42", run_branch NULL, context NULL, model_profile_id 4, tier "medium", state "requested" and kind "run", the row's created_at is "2026-11-16T11:00:00Z", the stub source-control provider received no branch-creation or commit request, the stub static scanner received 0 requests, and the agent stub's container-start counter remains 0

Scenario: A signed-in non-member cannot start a run
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), build 7 with skill "bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an empty "runs" table, and a stub source-control provider whose branch-listing counter is 0
When Carol submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 403 with the message "You are not a member of this project.", no "runs" row is created, the stub source-control provider received 0 branch-listing requests, and the response body contains neither "bug-fix-resolver" nor "build/bug-fix-resolver"

Scenario: A project without a source-control integration cannot start a run
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver" and state "open", an "integrations" table with no row with kind "github" for project 7, an empty "runs" table, and a stub source-control provider whose branch-listing counter is 0
When Ada opens GET "/projects/7/runs/new?build=7" and then submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "main", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then GET "/projects/7/runs/new?build=7" returned HTTP 200 rendering "No source-control integration is configured for this project." with the "Start run" control disabled, the POST returned HTTP 422 with the message "A source-control integration is required to start a run.", no "runs" row was created, and the stub source-control provider received 0 branch-listing requests

Scenario: A skills branch that does not contain the run's skill is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub source-control provider that lists branches ["main", "build/bug-fix-resolver", "test/saraav/fix-reproduce"] for repository "saraavrnd/bheembhai-skills", a stub catalog tree in which ref "build/bug-fix-resolver" contains "skills/bug-fix-resolver/SKILL.md" and ref "test/saraav/fix-reproduce" does not contain "skills/bug-fix-resolver/", an empty "runs" table, and an agent stub whose container-start counter is 0
When Ada submits {"build_id": 7, "skills_branch": "test/saraav/fix-reproduce", "input_branch": "main", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The selected skills branch does not contain skill bug-fix-resolver.", no "runs" row is created, the stub source-control provider received no branch-creation or commit request, and the agent stub's container-start counter remains 0

Scenario: An input branch that does not exist in the sandbox repository is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub source-control provider that lists branches ["main", "build/bug-fix-resolver"] for repository "saraavrnd/bheembhai-skills" and ["main", "test/atlas/bug-42"] for repository "saraavrnd/skill-builder-sandbox", a stub catalog tree in which ref "build/bug-fix-resolver" contains "skills/bug-fix-resolver/SKILL.md", and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-99", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The selected input branch does not exist in the sandbox repository.", and no "runs" row is created

Scenario: A second submission creates a new run and never rewrites the first
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an existing "runs" row id 21 with project_id 7, user_id 42, build_id 7, skill "bug-fix-resolver", skills_ref "build/bug-fix-resolver", skills_commit_sha NULL, input_branch "test/atlas/bug-42", run_branch NULL, context NULL, model_profile_id 4, tier "medium", state "requested" and kind "run", and a "runs" id sequence whose next value is 22
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 201 with a body containing "Run 22 requested for build 7 in Project Atlas.", exactly two "runs" rows exist with ids 21 and 22 and identical project_id, user_id, build_id, skill, skills_ref, input_branch, context, model_profile_id, tier, state and kind, and the "runs" row id 21 still has skills_ref "build/bug-fix-resolver", input_branch "test/atlas/bug-42", model_profile_id 4 and tier "medium"

### Covered requirements (traceability)
- FR-037
- FR-145
- FR-146

### Out of scope
The workflow and step context (BSB-24-PENDING-2); reviewer feedback and upstream handoff
(BSB-24-PENDING-3); choosing and validating the model profile and tier (BSB-24-PENDING-4);
resolving the skills branch to a commit SHA, packaging the skill, creating the run branch and
recording the baseline (BSB-25); the static security scan and the refusal when it does not pass
(BSB-31 and BSB-27); executing the skill, progress and logs (BSB-26); turn and spend caps, the
deadline and re-runs (BSB-27); the run report page (BSB-33); the command-line run start (BSB-37);
creating, editing or deleting builds (BSB-19 and BSB-21); creating projects and membership
(BSB-22); configuring integrations (BSB-23); writing to the input branch.

### Notes / dependencies
Depends on BSB-18 for the signed-in skill author and the per-request authorization middleware, on
BSB-22-PENDING-1 for the "projects" and "project_members" rows and the shared project-membership
check, on BSB-22-PENDING-3 for the run-start entry point at GET "/projects/7/runs/new" and its
membership check, on BSB-19-PENDING-1 for the "builds" row and its skill and branch, on
BSB-23-PENDING-2 for the source-control integration, on BSB-23-PENDING-3 for the AI model profile,
and on BSB-23-PENDING-6 for the run-purpose filter. The durable system of record is the builder's
own "runs" table from ADR SK-001 section 9. This story adds "runs.build_id" so the run is traceable
to the build it tests; the data-model stage must record that column. "runs.skill" comes from the
build's skill, "runs.skills_ref" is the chosen skills branch, "runs.skills_commit_sha" stays NULL
until BSB-25 resolves it, "runs.run_branch" stays NULL until BSB-25 creates the output branch, and
the row starts in state "requested" with kind "run".

This story owns the run-request contract on POST "/projects/7/runs" and the run row it creates.
The request fields are "build_id" (required), "skills_branch" (required, stored as
"runs.skills_ref"), "input_branch" (required), "workflow" and "step" (optional, owned by
BSB-24-PENDING-2), "reviewer_feedback" and "upstream_handoff" (optional, owned by
BSB-24-PENDING-3), and "model_profile_id" and "tier" (required, chosen and validated by
BSB-24-PENDING-4). BSB-24-PENDING-2, -3 and -4 extend this request and the "Chosen inputs" summary;
they do not redefine the run-creation outcome. BSB-27 adds its turn and spend caps to the same
request, and BSB-37 uses the same contract for the command line. The page is the one
BSB-22-PENDING-3 owns at GET "/projects/7/runs/new"; this story fills its choices and summary and
keeps its heading, and the build page (BSB-21) links here with the build id. The membership check
reads the current "project_members" rows on every request, before any build, branch, integration or
run data is read, and "runs.user_id" is the signed-in author.

The skills branch choices are the branches of the catalog repository "bheembhai-skills" returned
by the project's source-control integration; the input branch choices are the branches of that
integration's sandbox repository. The build's own branch is the default skills branch and the
integration's "base_branch" is the default input branch; both defaults are visible in the selects
and overridable. The provider is read on every page load. On submit the chosen skills branch must
contain the path "skills/" followed by the build's skill name, and the chosen input branch must exist in the
sandbox repository. The sandbox repository, the catalog repository and their curated branches are
external prerequisites (PRD section 8). The input branch is read-only: this story never writes it,
and BSB-25 creates the output branch from its head.

Run start does not resolve or package the skill, create the run branch, scan or execute. After the
request is created, BSB-25 resolves "skills_branch" to "skills_commit_sha" and creates
"run_branch"; BSB-27's preflight calls BSB-31-PENDING-1's static-scan route for the run's project
and resolved SHA (for build 7, POST "/api/builds/7/scans/static") before BSB-26 launches the agent
container, and BSB-27 refuses a run whose static verdict is not pass (FR-055). This story records
the project, build and (later) skills commit those steps use and applies the same membership check
before returning any selection data. Jira is not a run-start choice: the run inherits the project's
Jira integration when execution seeds or reads Jira (BSB-26 and BSB-28), so a missing Jira
integration is not a run-start refusal.

Validation order is membership, source-control integration, build and skill, skills branch, input
branch, then the context fields of BSB-24-PENDING-2 and the model fields of BSB-24-PENDING-4; the
first failure is returned. An omitted required field is refused with HTTP 422 and "Choose a build
to run.", "Choose a skills branch." or "Choose an input branch." as applicable, and creates no
"runs" row. A source-control provider that cannot list branches makes the page render
"Source-control branches unavailable; retry." and the POST return HTTP 502 with "The source-control
branch list could not be read."; no "runs" row is created. The run request is immutable once
created: re-submitting creates a second run, and later epics transition state without rewriting the
selected inputs.

---

## STORY: BSB-24-PENDING-2

**Title:** Choose the workflow and step context the run takes its vocabulary from
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **to choose the workflow and step whose context the run uses**, so that **the skill runs with the same statuses, hand-off and gate vocabulary it would see in the platform**.

### Acceptance Criteria

Scenario: The form offers only workflows and steps that use the run's skill
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub source-control provider that lists branches ["main", "build/bug-fix-resolver", "test/saraav/fix-reproduce"] for repository "saraavrnd/bheembhai-skills" and ["main", "test/atlas/bug-42"] for repository "saraavrnd/skill-builder-sandbox", and a stub catalog tree in which ref "build/bug-fix-resolver" contains "skills/bug-fix-resolver/SKILL.md", "config/sdlc-wf-bug-fix.yaml" whose "steps" list holds step id "sdlc-fix-bug-triage" with skill "bug-fix-resolver" and step id "sdlc-fix-bug-reproduce" with skill "bug-fix-reproducer", and "config/sdlc-wf-release.yaml" whose "steps" list holds step id "sdlc-release-pr" with skill "release-opener"
When Ada opens GET "/projects/7/runs/new?build=7&skills_branch=build/bug-fix-resolver"
Then the response is HTTP 200, the "Workflow" select lists "config/sdlc-wf-bug-fix.yaml" and does not list "config/sdlc-wf-release.yaml", the "Step" select lists "sdlc-fix-bug-triage" and does not list "sdlc-fix-bug-reproduce", the "Workflow" select shows "config/sdlc-wf-bug-fix.yaml" selected and the "Step" select shows "sdlc-fix-bug-triage" selected, and the "Chosen inputs" summary renders "Workflow: config/sdlc-wf-bug-fix.yaml" and "Step: sdlc-fix-bug-triage"

Scenario: A run request records the chosen workflow and step
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub catalog tree in which ref "build/bug-fix-resolver" contains "config/sdlc-wf-bug-fix.yaml" whose "steps" list holds step id "sdlc-fix-bug-triage" with skill "bug-fix-resolver", an earlier GET at "/projects/7/runs/new?build=7&skills_branch=build/bug-fix-resolver&workflow=config/sdlc-wf-bug-fix.yaml&step=sdlc-fix-bug-triage" that rendered "Workflow: config/sdlc-wf-bug-fix.yaml" and "Step: sdlc-fix-bug-triage", and an empty "runs" table with a "runs" id sequence whose next value is 21
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 201 with a body containing "Run 21 requested for build 7 in Project Atlas.", and the "runs" row id 21 has skills_ref "build/bug-fix-resolver", input_branch "test/atlas/bug-42", model_profile_id 4, tier "medium", state "requested" and context {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": null, "upstream_handoff": null}

Scenario: A run can start without a workflow or step
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub catalog tree in which ref "build/bug-fix-resolver" contains "config/sdlc-wf-bug-fix.yaml" whose "steps" list holds step id "sdlc-fix-bug-triage" with skill "bug-fix-resolver", and an empty "runs" table with a "runs" id sequence whose next value is 21
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 201 and the "runs" row id 21 has context NULL

Scenario: A workflow that is not in the skills branch is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub catalog tree in which ref "build/bug-fix-resolver" contains "config/sdlc-wf-bug-fix.yaml", and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "workflow": "config/sdlc-wf-missing.yaml", "step": "sdlc-fix-bug-triage", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The selected workflow was not found in the skills branch.", and no "runs" row is created

Scenario: A step that is not in the chosen workflow is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub catalog tree in which ref "build/bug-fix-resolver" contains "config/sdlc-wf-bug-fix.yaml" whose "steps" list holds step id "sdlc-fix-bug-triage" with skill "bug-fix-resolver", and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-not-a-step", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The selected step was not found in the workflow.", and no "runs" row is created

Scenario: A step that runs a different skill is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub catalog tree in which ref "build/bug-fix-resolver" contains "config/sdlc-wf-release.yaml" whose "steps" list holds step id "sdlc-release-pr" with skill "release-opener", and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "workflow": "config/sdlc-wf-release.yaml", "step": "sdlc-release-pr", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The selected step does not run skill bug-fix-resolver.", and no "runs" row is created

Scenario: A workflow or step supplied without its pair is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub catalog tree in which ref "build/bug-fix-resolver" contains "config/sdlc-wf-bug-fix.yaml" whose "steps" list holds step id "sdlc-fix-bug-triage" with skill "bug-fix-resolver", and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "workflow": "config/sdlc-wf-bug-fix.yaml", "model_profile_id": 4, "tier": "medium"} with no step, and then submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "step": "sdlc-fix-bug-triage", "model_profile_id": 4, "tier": "medium"} with no workflow, on POST "/projects/7/runs"
Then the first POST returns HTTP 422 with the message "Choose a step in the workflow.", the second POST returns HTTP 422 with the message "Choose a workflow for the step.", and no "runs" row is created

### Covered requirements (traceability)
- FR-147

### Out of scope
The skills branch and input branch choices and the run-creation outcome (BSB-24-PENDING-1);
reviewer feedback and upstream handoff (BSB-24-PENDING-3); the model profile and tier
(BSB-24-PENDING-4); building BB_CONTEXT and passing it to the container (BSB-26 and the step kit);
editing or creating workflows; running a workflow with gates and routing (the epic's non-goal);
the meaning of the platform's "on:" maps beyond reading the chosen step; a workflow's steps that do
not run this skill.

### Notes / dependencies
Depends on BSB-24-PENDING-1 for the POST contract, the "runs" row and the "Chosen inputs" summary,
on BSB-22-PENDING-3 for the run-start page, on BSB-23-PENDING-2 for the source-control integration
that reads the catalog repository, and on the selected skills branch's "config/" contents, which
are external catalog-repository inputs. This story owns the "Workflow" and "Step" controls and the
"context.workflow" and "context.step" keys of "runs.context". The context object shape is
{"workflow", "step", "reviewer_feedback", "upstream_handoff"}; BSB-24-PENDING-3 owns the two
feedback keys and BSB-24-PENDING-1 owns the request and the run row. When no workflow or step is
chosen and no feedback is supplied, "runs.context" is NULL.

Workflow definitions are the YAML files under "config/" in the selected skills branch — the same
definitions the platform consumes (ADR SK-001 section 5). Only workflows with at least one step
whose "skill:" equals "runs.skill" are offered, and only those steps are offered. The default is
the first such workflow in lexicographic path order and its first matching step; the default is
visible in the selects and overridable. The branch's files are read at page load, so changing the
skills branch re-reads its workflows and steps. The run stores only the workflow path and step id;
BSB-26 and the step kit build BB_CONTEXT ("allowed_result_statuses", "result_status_meanings",
"gate_follows", "gate_role", "reviewer_feedback", "upstream_handoff") from them at execution. This
story does not run the workflow, evaluate its "on:" map or route between steps.

Validation runs after BSB-24-PENDING-1's checks: a workflow that is not under the selected branch's
"config/" is refused, a step that is not in the chosen workflow is refused, a step whose "skill:"
is not the run's skill is refused, and a workflow or step supplied without its pair is refused.
Every refusal creates no "runs" row. BSB-27's re-run copies the context, BSB-37's command line
carries the same fields, BSB-26 owns the BB_CONTEXT rendering, and BSB-33's report may display it.

---

## STORY: BSB-24-PENDING-3

**Title:** Optionally supply reviewer feedback or an upstream handoff
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **to add reviewer feedback or an upstream handoff to a run**, so that **I can reproduce a send-back or a BLOCK hand-off and see how the skill handles the context the platform would give it**.

### Acceptance Criteria

Scenario: Reviewer feedback is stored in the run context and summarized before creation
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an earlier GET at "/projects/7/runs/new?build=7&skills_branch=build/bug-fix-resolver&input_branch=test/atlas/bug-42&reviewer_feedback=The+reproduction+section+is+missing+the+exact+command." that rendered "Reviewer feedback: The reproduction section is missing the exact command.", and an empty "runs" table with a "runs" id sequence whose next value is 21
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "reviewer_feedback": "The reproduction section is missing the exact command.", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 201 with a body containing "Run 21 requested for build 7 in Project Atlas.", and the "runs" row id 21 has state "requested" and context {"workflow": null, "step": null, "reviewer_feedback": "The reproduction section is missing the exact command.", "upstream_handoff": null}

Scenario: An upstream handoff is stored in the run context and summarized before creation
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an earlier GET at "/projects/7/runs/new?build=7&skills_branch=build/bug-fix-resolver&input_branch=test/atlas/bug-42&upstream_handoff=BLOCK%3A+the+reproduction+could+not+be+confirmed." that rendered "Upstream handoff: BLOCK: the reproduction could not be confirmed.", and an empty "runs" table with a "runs" id sequence whose next value is 21
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "upstream_handoff": "BLOCK: the reproduction could not be confirmed.", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 201, and the "runs" row id 21 has context {"workflow": null, "step": null, "reviewer_feedback": null, "upstream_handoff": "BLOCK: the reproduction could not be confirmed."}

Scenario: Reviewer feedback and an upstream handoff can be supplied together
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, and an empty "runs" table with a "runs" id sequence whose next value is 21
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "reviewer_feedback": "Add the exact command.", "upstream_handoff": "BLOCK: the reproduction could not be confirmed.", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 201, and the "runs" row id 21 has context {"workflow": null, "step": null, "reviewer_feedback": "Add the exact command.", "upstream_handoff": "BLOCK: the reproduction could not be confirmed."}

Scenario: Blank reviewer feedback and handoff are stored as not supplied
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, a stub catalog tree in which ref "build/bug-fix-resolver" contains "config/sdlc-wf-bug-fix.yaml" whose "steps" list holds step id "sdlc-fix-bug-triage" with skill "bug-fix-resolver", and an empty "runs" table with a "runs" id sequence whose next value is 21
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": "   ", "upstream_handoff": "  \n ", "model_profile_id": 4, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 201, and the "runs" row id 21 has context {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": null, "upstream_handoff": null}

### Covered requirements (traceability)
- FR-148

### Out of scope
The skills branch and input branch choices and the run-creation outcome (BSB-24-PENDING-1); the
workflow and step choice (BSB-24-PENDING-2); the model profile and tier (BSB-24-PENDING-4);
generating, interpreting or validating the content of reviewer feedback or an upstream handoff;
the platform's send-back and BLOCK routing rules; building BB_CONTEXT and passing it to the
container (BSB-26 and the step kit); Jira fixture seeding and executing the skill (BSB-28 and
BSB-26); displaying the feedback on the run report (BSB-33).

### Notes / dependencies
Depends on BSB-24-PENDING-1 for the POST contract, the run row and the "Chosen inputs" summary, and
on BSB-24-PENDING-2 for the "runs.context" object. This story owns the "reviewer_feedback" and
"upstream_handoff" keys of that object and the two optional text controls. Both values are free
text, stored verbatim after trimming; a blank or whitespace-only value is stored as JSON null.
They are independent: either or both may be supplied, with or without a workflow or step context.
A request that supplies a value with no context stores a context object whose "workflow" and "step"
are null. The builder does not require the chosen step to have a gate or BLOCK edge; it reproduces
the input, and BSB-26 and BSB-27 own how the agent's result is classified.

The step kit renders the two values into BB_CONTEXT as "reviewer_feedback" and
"upstream_handoff"; the builder does not interpret or validate their content. They are user text,
not credentials, and they are stored in the builder database, so they follow the run report's
retention and purge rules (BSB-33 and BSB-34). BSB-27's re-run copies both values, BSB-37's command
line carries the same fields, BSB-26 owns the BB_CONTEXT rendering, and BSB-33's report may display
them.

---

## STORY: BSB-24-PENDING-4

**Title:** Choose the model profile and tier for the run
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **to choose the project's model profile and the high, medium or low tier the run uses**, so that **the run uses the model I intend and its record says exactly which profile and tier were selected**.

### Acceptance Criteria

Scenario: The form offers only run-purpose model profiles and preselects the skill's tier
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an "integrations" row id 4 with project_id 7, kind "ai_model", config {"name": "Default", "test_only": true} and a complete high, medium and low tier mapping, an "integrations" row id 5 with project_id 7, kind "ai_model", config {"name": "Cheap smoke runs", "test_only": true} and a complete high, medium and low tier mapping, an "integrations" row id 6 with project_id 7, kind "ai_model", config {"name": "Production profile", "test_only": false} and a complete high, medium and low tier mapping, a stub run-purpose profile list at GET "/api/projects/7/integrations?purpose=run" that returns {"integrations": [{"id": 4, "kind": "ai_model", "name": "Default"}, {"id": 5, "kind": "ai_model", "name": "Cheap smoke runs"}]}, and a stub catalog tree in which ref "build/bug-fix-resolver" contains "skills/bug-fix-resolver/SKILL.md" whose frontmatter has model "medium"
When Ada opens GET "/projects/7/runs/new?build=7&skills_branch=build/bug-fix-resolver"
Then the response is HTTP 200, the "Model profile" select lists "Default" and "Cheap smoke runs" and does not list "Production profile", no option is selected in the "Model profile" select, the "Model tier" select lists "high", "medium" and "low" with "medium" selected, and the "Start run" control is disabled with the message "Choose a model profile."

Scenario: A run request records the chosen model profile and tier
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an "integrations" row id 5 with project_id 7, kind "ai_model", config {"name": "Cheap smoke runs", "test_only": true} and a complete high, medium and low tier mapping, an earlier GET at "/projects/7/runs/new?build=7&skills_branch=build/bug-fix-resolver&model_profile_id=5&tier=low" that rendered "Model profile: Cheap smoke runs" and "Model tier: low", and an empty "runs" table with a "runs" id sequence whose next value is 21
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 5, "tier": "low"} on POST "/projects/7/runs"
Then the response is HTTP 201 with a body containing "Run 21 requested for build 7 in Project Atlas.", and the "runs" row id 21 has model_profile_id 5, tier "low", skills_ref "build/bug-fix-resolver", input_branch "test/atlas/bug-42", context NULL and state "requested"

Scenario: A model profile from another project is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an "integrations" row id 4 with project_id 7, kind "ai_model" and config {"name": "Default", "test_only": true}, an "integrations" row id 9 with project_id 8, kind "ai_model" and config {"name": "Other project profile", "test_only": true}, and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 9, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The selected model profile is not available for runs in this project.", and no "runs" row is created

Scenario: A profile without the test-purpose confirmation is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an "integrations" row id 4 with project_id 7, kind "ai_model" and config {"name": "Default", "test_only": true}, an "integrations" row id 6 with project_id 7, kind "ai_model" and config {"name": "Production profile", "test_only": false}, and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 6, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The selected model profile is not available for runs in this project.", and no "runs" row is created

Scenario: An integration that is not an AI model profile is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an "integrations" row id 4 with project_id 7, kind "ai_model" and config {"name": "Default", "test_only": true}, an "integrations" row id 8 with project_id 7, kind "jira" and config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "BSB", "test_only": true}, and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 8, "tier": "medium"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The selected model profile is not available for runs in this project.", and no "runs" row is created

Scenario: An unknown model tier is refused
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an "integrations" row id 4 with project_id 7, kind "ai_model", config {"name": "Default", "test_only": true} and a complete high, medium and low tier mapping, and an empty "runs" table
When Ada submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": 4, "tier": "ultra"} on POST "/projects/7/runs"
Then the response is HTTP 422 with the message "The model tier must be high, medium or low.", and no "runs" row is created

Scenario: A project with no run-purpose model profile cannot start a run
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), build 7 with skill "bug-fix-resolver", branch "build/bug-fix-resolver" and state "open", the source-control integration 3 for project 7, an "integrations" row id 6 with project_id 7, kind "ai_model" and config {"name": "Production profile", "test_only": false}, a stub run-purpose profile list at GET "/api/projects/7/integrations?purpose=run" that returns {"integrations": []}, and an empty "runs" table
When Ada opens GET "/projects/7/runs/new?build=7" and then submits {"build_id": 7, "skills_branch": "build/bug-fix-resolver", "input_branch": "test/atlas/bug-42", "model_profile_id": null, "tier": "medium"} on POST "/projects/7/runs"
Then GET "/projects/7/runs/new?build=7" returned HTTP 200 rendering "No model profile is available for runs in this project." with the "Start run" control disabled, the POST returned HTTP 422 with the message "Choose a model profile.", and no "runs" row was created

### Covered requirements (traceability)
- FR-149
- FR-150

### Out of scope
Creating, editing or verifying AI model profiles (BSB-23-PENDING-3 and BSB-23-PENDING-4); the
run-purpose filter itself (BSB-23-PENDING-6); the LLM security scan's separate project-level model
(BSB-32); resolving the concrete model identifier and passing BB_MODEL to the container (BSB-26);
the skill's "model:" frontmatter content (BSB-19); a per-run model override outside the choices
offered here; storing, verifying or rotating the vendor key; changing a project's model profiles at
run start.

### Notes / dependencies
Depends on BSB-24-PENDING-1 for the POST contract, the run row and the "Chosen inputs" summary, on
BSB-23-PENDING-3 for the "ai_model" rows and their complete high, medium and low tier mapping, and
on BSB-23-PENDING-6 for the GET "/api/projects/7/integrations?purpose=run" contract. The form reads
that list; only AI model profiles whose config "test_only" is true are offered. A direct request
naming a profile that is not in the list, belongs to another project, is not kind "ai_model", or is
not test-purpose is refused with one generic message so the builder does not reveal another
project's records. This story owns the "Model profile" and "Model tier" controls and the validation
of "model_profile_id" and "tier"; BSB-24-PENDING-1 owns the run row and already writes those two
values. "runs.model_profile_id" references an "integrations" row with kind "ai_model" and the same
project_id, and "runs.tier" is "high", "medium" or "low".

Defaults are explicit and overridable. When the project has exactly one run-purpose profile it is
preselected; when it has several none is preselected and the author must choose; when it has none
the page renders "No model profile is available for runs in this project." and start is disabled.
The tier select always lists high, medium and low and preselects the skill's "model:" frontmatter
value when that value is one of them; otherwise no tier is preselected and the author must choose.
A tier that is not high, medium or low is refused. The profile's tier mapping is complete
(BSB-23-PENDING-3), so every offered tier resolves to a model and this story does not re-validate
the mapping. The concrete model identifier is resolved from the profile's "models" object at
execution (BSB-26), not stored on the run row beyond the profile id and tier.

BSB-26 records the profile and tier actually used and passes BB_MODEL, BSB-32's LLM scan uses the
project's separate LLM-scan model rather than this run profile, BSB-37's command line carries the
same fields, and BSB-27's re-run copies them. When the profile list changes between page load and
submit, submit-time validation is authoritative and the run row records only accepted values.

---

*Generated by `sdlc-plan-stories-write`. Coverage: FR-037, FR-145, FR-146, FR-147, FR-148, FR-149
and FR-150 all covered. Next steps: `sdlc-plan-epic-review` reviews the set on a different model
family; then `sdlc-plan-epic-sequence` orders the stories and `sdlc-tracker-sync` publishes them to
Jira.*
