# Stories — BSB-26 (Run execution & outcome capture)

Epic BSB-26 covers FR-044, FR-045, FR-046, FR-047, FR-048, FR-049, FR-151 and FR-152.
Decomposed into 4 vertical slices below; coverage of all 8 requirements verified.

The four slices follow one prepared run from the end of preparation to a classified terminal
outcome. The author first gets the prepared skill launched in the platform's own pinned runtime,
with the exact agent image digest, step kit version and verifier version recorded on the run
(PENDING-1); then watches its progress and logs while it executes (PENDING-2); then gets the
outcome classified with the platform engine's rules, the agent's claimed verdict retained and the
output on the run's own branch (PENDING-3); and finally sees the exact model profile, tier and
concrete model the run used, recorded at launch (PENDING-4). Every slice ends in durable state on
the run (`runs.state`, `runs.agent_image_digest`, `runs.stepkit_version`, `runs.verify_version`,
`runs.model_profile_id`, `runs.tier`, `runs.model`, `runs.result_status`, `runs.claimed_verdict`)
that verification, the run report and the usage record consume.

The run is prepared by BSB-25: it moves through `requested`, `preparing` and `prepared`, or to
`preparation_failed`. This epic adds the execution lifecycle values `running`, `completed` and
`failed`, and the engine-classified `result_status` values. It does not write `final_verdict` or
`verification`: BSB-29 runs the shared verification layer after execution. BSB-27 owns the
pre-launch compatibility refusal, the static-scan refusal, turn and spend caps, and the deadline,
including the `failed_timeout` result.

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-044 — execute the skill in the platform's runtime | BSB-26-PENDING-1 | "A prepared run is launched once in the platform's pinned runtime" |
| FR-045 — the run page shows progress while the run executes | BSB-26-PENDING-2 | "A running run's page shows its latest progress"; "New progress and log lines appear while the run executes" |
| FR-046 — the run page shows logs while the run executes | BSB-26-PENDING-2 | "A running run's page shows its log tail"; "New progress and log lines appear while the run executes"; "A log that cannot be read is shown as unavailable" |
| FR-047 — the run outcome is classified using the platform engine's result rules | BSB-26-PENDING-3 | "A successful execution is classified as completed and its claimed verdict is recorded"; "The agent's own verdict is preserved as the classified result"; "A non-zero exit with a valid result is a failed execution"; "A run that produces no readable result is failed incomplete"; "A container that cannot start is a failed infrastructure run"; "The run may write only to its output branch" |
| FR-048 — the exact execution-component versions are recorded | BSB-26-PENDING-1 | "A prepared run is launched once in the platform's pinned runtime"; "A component pinned by tag is refused" |
| FR-049 — the model profile used by the run is recorded | BSB-26-PENDING-4 | "The model profile, tier and concrete model used are recorded and shown"; "A profile changed after the run does not rewrite the run's record" |
| FR-151 — the exact verifier version used by the run is recorded | BSB-26-PENDING-1 | "A prepared run is launched once in the platform's pinned runtime" |
| FR-152 — the model tier used by the run is recorded | BSB-26-PENDING-4 | "The model profile, tier and concrete model used are recorded and shown"; "The tier selects the model mapped by the profile" |

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than an epic: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 "Issue
does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The
Atlassian MCP tools were not exposed in this session, so the configured site was queried read-only
through its REST API. The epic being decomposed is BSB-26, read read-only from the same site:
summary "Run execution & outcome capture", status To Do, labels FA-7/MVP, no parent, no sub-tasks
and no issue links. Its description has no separate acceptance-criteria field; its functional
scope and Definition of Done are the acceptance material used here. No Jira write was attempted
and no issue content is assumed from the lookup.

> New stories use draft keys in the `BSB-26-PENDING` series (`-1` to `-4`). `sdlc-tracker-sync`
> creates each story in Jira, parents it to BSB-26, and replaces the draft key with the real key in
> `story-map.json`.

---

## STORY: BSB-26-PENDING-1

**Title:** Run a prepared skill in the platform's pinned runtime
**Epic:** BSB-26 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-7, MVP

### Story
As a **skill author who is a project member**, I want **the builder to launch my prepared run in the platform's own pinned runtime and record the exact agent, step kit and verifier versions it used**, so that **the run I watch is the same execution path the platform would take and its record can be reproduced later**.

### Acceptance Criteria

Scenario: A prepared run is launched once in the platform's pinned runtime
Given a "runs" row id 21 with project_id 7, user_id 42, build_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", context {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-triage", "reviewer_feedback": null, "upstream_handoff": null}, model_profile_id 5, tier "low", agent_image_digest NULL, stepkit_version NULL, verify_version NULL, model NULL, result_status NULL, claimed_verdict NULL, execution_error NULL, state "prepared" and kind "run", an "integrations" row id 3 with project_id 7, kind "github", config {"repository": "saraavrnd/skill-builder-sandbox", "base_branch": "main", "test_only": true} and secret_ref "skill-builder/7/integration-3", an "integrations" row id 5 with project_id 7, kind "ai_model", config {"name": "Cheap smoke runs", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-opus-5-5", "medium": "claude-sonnet-5-5", "low": "claude-haiku-5-5"}, "test_only": true} and secret_ref "skill-builder/7/integration-5", an "integrations" row id 6 with project_id 7, kind "jira", config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "BSB", "test_only": true} and secret_ref "skill-builder/7/integration-6", a secret store holding "ghp-test-token-7a1d" at "skill-builder/7/integration-3", "sk-ant-test-3c9e" at "skill-builder/7/integration-5" and "jira-test-token-9f2c" at "skill-builder/7/integration-6", a "skill_bundles" row for skill "sdlc-fix-bug-reproduce" and skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" with bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08" and s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", a pinned platform kit recording agent image digest "sha256:3f1a9c2e5b7d4a6f8c0e2b4d6f8a1c3e5b7d9f0a2c4e6b8d0f1a3c5e7b9d2f4a", step kit version "bheembhai-stepkit 0.3.0", verifier version "bheembhai-verify 0.8.1" and environment-contract version "1", an object store that presigns s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz" to "https://skill-builder-runs.s3.ap-south-1.amazonaws.com/bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz?X-Amz-Signature=6c1f0a", a stub runtime adapter whose container-start counter is 0, and a builder clock reading "2026-11-16T11:00:00Z"
When the execution worker processes run 21
Then the stub runtime adapter's container-start counter is 1, its launch spec has image "sha256:3f1a9c2e5b7d4a6f8c0e2b4d6f8a1c3e5b7d9f0a2c4e6b8d0f1a3c5e7b9d2f4a", stepkit_version "bheembhai-stepkit 0.3.0" and env_contract_version "1", its environment contains BB_SKILL_URL "https://skill-builder-runs.s3.ap-south-1.amazonaws.com/bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz?X-Amz-Signature=6c1f0a", BB_SKILL_SHA256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", RUN_BRANCH "skilltest/21", BB_CONTEXT whose parsed JSON equals run 21's context, and the injected values of integrations 3, 5 and 6, the "runs" row id 21 has state "running", agent_image_digest "sha256:3f1a9c2e5b7d4a6f8c0e2b4d6f8a1c3e5b7d9f0a2c4e6b8d0f1a3c5e7b9d2f4a", stepkit_version "bheembhai-stepkit 0.3.0", verify_version "bheembhai-verify 0.8.1", model_profile_id 5, tier "low", result_status NULL, claimed_verdict NULL, execution_error NULL and started_at "2026-11-16T11:00:00Z", and neither the builder database nor the builder's own log contains "ghp-test-token-7a1d", "sk-ant-test-3c9e" or "jira-test-token-9f2c"

Scenario: Only a prepared run is launched
Given two "runs" rows id 21 with state "preparing" and id 22 with state "preparation_failed", each with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", run_branch "skilltest/21" and "skilltest/22", a "skill_bundles" row for that skill and commit, and a stub runtime adapter whose container-start counter is 0
When the execution worker runs twice
Then neither run is launched, the stub runtime adapter's container-start counter remains 0, the "runs" row id 21 still has state "preparing", the "runs" row id 22 still has state "preparation_failed", and both rows still have execution_error NULL and started_at NULL

Scenario: A run whose bundle cannot be read fails before a container starts
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", model_profile_id 5, tier "low", state "prepared", execution_error NULL and started_at NULL, the integrations and secrets of the previous scenario, a "skill_bundles" row for skill "sdlc-fix-bug-reproduce" and that commit with s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", an object store that returns HTTP 404 "NoSuchKey" for that s3_key, and a stub runtime adapter whose container-start counter is 0
When the execution worker processes run 21
Then the "runs" row id 21 has state "failed", result_status "failed_infra", execution_error "The run's skill bundle is not available.", started_at NULL and finished_at "2026-11-16T11:00:00Z", the stub runtime adapter's container-start counter remains 0, the stub source-control provider received no ref-update or commit request, and no object exists at "runs/21/bb_step_result.json"

Scenario: A component pinned by tag is refused
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", run_branch "skilltest/21", model_profile_id 5, tier "low", state "prepared", agent_image_digest NULL, execution_error NULL and started_at NULL, a "skill_bundles" row for that skill and commit, the integrations and secrets of the first scenario, a pinned platform kit whose agent image is "ghcr.io/saraavrnd/skill-builder-agent:latest" instead of a digest, and a stub runtime adapter whose container-start counter is 0
When the execution worker processes run 21
Then the stub runtime adapter's container-start counter remains 0, the "runs" row id 21 has state "failed", result_status "failed_infra", execution_error "The agent image must be pinned by digest.", agent_image_digest NULL, started_at NULL and finished_at "2026-11-16T11:00:00Z", and no object exists at "runs/21/bb_step_result.json"

### Covered requirements (traceability)
- FR-044
- FR-048
- FR-151

### Out of scope
Creating the run request and the `runs` row (BSB-24); resolving the skills commit, packing the
bundle and creating the run branch and baseline (BSB-25); the compatibility preflight, the
static-scan gate, turn and spend caps and the deadline (BSB-27); the static and LLM scans
(BSB-31 and BSB-32); writing `final_verdict` or `verification` (BSB-29); the progress and log
live view (BSB-26-PENDING-2); classifying the exit into a terminal outcome and publishing the
output branch (BSB-26-PENDING-3); recording the model profile and tier (BSB-26-PENDING-4); the
run report (BSB-33); token, cost and turn usage and retention (BSB-34); Jira fixture seeding
(BSB-28); the command-line run (BSB-37).

### Notes / dependencies
Depends on BSB-24-PENDING-1 for run 21 in state "prepared", its `context` and its project,
build and skill, on BSB-24-PENDING-4 for `model_profile_id` and `tier`, on BSB-25-PENDING-1 and
BSB-25-PENDING-2 for `runs.skills_commit_sha` and the `skill_bundles` row, on BSB-25-PENDING-3
for `runs.run_branch` and `runs.baseline_sha`, and on BSB-23-PENDING-2, BSB-23-PENDING-3 and
BSB-23-PENDING-5 for the source-control, AI-model and Jira integrations and their secret
references. Depends on BSB-18 for the author identity and the per-request gate. Execution acts on
an already-authorized run, so it adds no membership check of its own.

This story owns the execution worker, the runtime-adapter call and the `running` state. The
adapter is the platform's pinned execution path, not a builder-specific imitation: it pulls the
agent image by the digest the kit records, starts one container for run 21, and passes the
environment contract ADR SK-001 section 2a names — the bundle URL and hash, the run branch, the
BashH_CONTEXT built from the run's context, and the run's model environment, which
BSB-26-PENDING-4 owns. The bundle is read through the `skill_bundles` row for
`(skill, skills_commit_sha)` and is treated as an opaque object addressed by `s3_key`; the bundle's
content and format are the open architecture question recorded in BSB-25's review (Finding 1) and
are not restated here. The builder stores only the secret reference and injects the value at
launch; no secret value is written to the database, the builder log, the progress or the result.

The exact component versions are recorded on the run at launch and are not re-derived later:
`runs.agent_image_digest`, `runs.stepkit_version` and `runs.verify_version` already exist in ADR
SK-001 section 9. The verifier version is recorded here even though verification itself runs in
BSB-29, so the pin that will grade the run is fixed at the moment the run starts. A kit that gives
an image by tag instead of digest is refused rather than resolved, because a moving tag would let
the builder and the platform execute different bytes. `runs.started_at` and `runs.finished_at`
must be added by the data-model stage; `runs.result_status` and `runs.execution_error` are added
by BSB-26-PENDING-3.

BSB-27 owns the refusal of incompatible execution components (FR-054), the static-scan gate
(FR-055) and the deadline. When BSB-27's preflight lands, this worker launches only a run that
has passed it; the ordering note recorded in BSB-24's and BSB-25's reviews applies. BSB-26 stops
at the classified execution outcome: it never runs the shared verification layer and never writes
`final_verdict`. BSB-33 reads the recorded versions for the report, BSB-34 reads the run's usage,
and BSB-37's command line uses the same execution path.

---

## STORY: BSB-26-PENDING-2

**Title:** Watch progress and logs while my skill runs
**Epic:** BSB-26 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-7, MVP

### Story
As a **skill author who is a project member**, I want **to watch my run's progress and log output update while the skill executes**, so that **I can tell whether the run is working and diagnose a slow or failing step without waiting for it to finish**.

### Acceptance Criteria

Scenario: A running run's page shows its latest progress and log tail
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", run_branch "skilltest/21", state "running" and started_at "2026-11-16T11:00:00Z", a builder object store holding "runs/21/progress.json" with content {"status": "running", "turns": 3, "max_turns": 12, "last_event": "Wrote bugfix.md"} and "runs/21/agent.log" whose lines are "Cloned run branch skilltest/21." and "Wrote bugfix.md", and a builder clock reading "2026-11-16T11:02:00Z"
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering the heading "Run 21 — sdlc-fix-bug-reproduce", "Status: running", "Turns: 3 of 12", "Last event: Wrote bugfix.md", and a log block containing "Cloned run branch skilltest/21." followed by "Wrote bugfix.md"

Scenario: New progress and log lines appear while the run executes
Given the same signed-in Ada, project 7 and running run 21, a first GET at "/projects/7/runs/21" that rendered "Turns: 3 of 12" and "Wrote bugfix.md", and the object store afterwards receiving a new "runs/21/progress.json" with content {"status": "running", "turns": 4, "max_turns": 12, "last_event": "Pushing skilltest/21"} and an appended "runs/21/agent.log" line "Pushed skilltest/21."
When Ada opens GET "/projects/7/runs/21" again
Then the response is HTTP 200 rendering "Turns: 4 of 12", "Last event: Pushing skilltest/21" and "Pushed skilltest/21.", and the response no longer renders "Turns: 3 of 12"

Scenario: A run that has not written progress or logs yet shows an empty state
Given the same signed-in Ada, project 7 and running run 21, and a builder object store that holds neither "runs/21/progress.json" nor "runs/21/agent.log"
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Status: running", "Waiting for the agent to start." and "No log output yet.", and no error text appears in the body

Scenario: A non-member cannot see a run's progress or logs
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), a "runs" row id 21 with project_id 7, state "running", a builder object store holding "runs/21/progress.json" with content {"status": "running", "turns": 3, "max_turns": 12, "last_event": "Wrote bugfix.md"} and "runs/21/agent.log" containing "Wrote bugfix.md", and an object-store read counter that is 0
When Carol opens GET "/projects/7/runs/21"
Then the response is HTTP 403 with the message "You are not a member of this project.", the body contains neither "Wrote bugfix.md" nor "Turns:", and the object-store read counter remains 0

Scenario: A run that is not in this project is not disclosed
Given the same signed-in Ada with her "project_members" row for project 7, a "runs" row id 31 with project_id 8 and skill "other-project-skill", a builder object store holding "runs/31/agent.log" containing "other-project-output", no "runs" row id 99, and an object-store read counter for run 31 that is 0
When Ada opens GET "/projects/7/runs/31" and, as a second request, GET "/projects/7/runs/99"
Then both responses are HTTP 404 with the message "Run not found.", neither body contains "other-project-output" or "other-project-skill", and the object-store read counter for run 31 remains 0

Scenario: A log that cannot be read is shown as unavailable
Given the same signed-in Ada, project 7 and running run 21, a builder object store holding "runs/21/progress.json" with content {"status": "running", "turns": 3, "max_turns": 12, "last_event": "Wrote bugfix.md"} and returning HTTP 503 "Service Unavailable" for "runs/21/agent.log"
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Turns: 3 of 12", "Last event: Wrote bugfix.md" and "Logs unavailable; retry.", and the body contains no exception text, stack trace or credential value

Scenario: Injected credential values are redacted from the live view
Given the same signed-in Ada, project 7 and running run 21, an "integrations" row id 3 for project 7, kind "github", with secret_ref "skill-builder/7/integration-3" and an "integrations" row id 5 for project 7, kind "ai_model", with secret_ref "skill-builder/7/integration-5", a secret store holding "ghp-test-token-7a1d" at "skill-builder/7/integration-3" and "sk-ant-test-3c9e" at "skill-builder/7/integration-5", and a builder object store holding "runs/21/progress.json" with content {"status": "running", "turns": 3, "max_turns": 12, "last_event": "Calling the model"} and "runs/21/agent.log" whose lines are "Using API key sk-ant-test-3c9e" and "git token ghp-test-token-7a1d"
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200, the body contains "Using API key [REDACTED]" and "git token [REDACTED]", and the body contains neither "sk-ant-test-3c9e" nor "ghp-test-token-7a1d"

### Covered requirements (traceability)
- FR-045
- FR-046

### Out of scope
Starting or running the container and recording the component versions (BSB-26-PENDING-1);
classifying the exit into a terminal outcome (BSB-26-PENDING-3); recording the model profile and
tier (BSB-26-PENDING-4); the run report's verdict, component, diff and Jira sections (BSB-33);
the Security tab and scan reports (BSB-31, BSB-32 and BSB-33); the recorded turn count, token
usage, cost and retention (BSB-34); turn and spend caps and the deadline (BSB-27); Jira fixture
seeding (BSB-28); the command-line run's output (BSB-37).

### Notes / dependencies
Depends on BSB-26-PENDING-1 for a run 21 in state "running" and for the adapter that writes the
agent's `progress.json` and `agent.log` to `runs/21/` in the builder's object store (ADR SK-001
sections 5 and 6), on BSB-18 for the signed-in author and the per-request gate, and on BSB-22 for
the shared project-membership check. The run page is GET "/projects/7/runs/21"; BSB-22-PENDING-3
owns the run-start page and the shared membership check, and BSB-33 adds the report sections to
this same page. This story owns only the live progress and log view.

The membership check resolves the run's project first and runs before any artifact is read, so a
non-member and an unknown or other-project run disclose nothing. The live view reads the
`progress.json` document and the tail of `agent.log` from the builder's object store on each
request; it does not attach to the container's stdout and it does not store a second copy of the
log. The progress document's `status`, `turns`, `max_turns` and `last_event` fields are rendered
as the labels in the acceptance criteria; an update to the document is visible on the next
request. A missing progress or log object is an empty state, not an error, because the agent may
not have written it yet. An object-store read failure is a temporary unavailable state, not a
failed run.

Credential values are injected into the container at launch (ADR SK-001 section 4) and must never
be rendered or stored. The builder knows the run's injected values from its secret references and
replaces any occurrence in the rendered progress or log with "[REDACTED]". NFR-004 is mapped to
BSB-23; this story applies the same rule to the run's live view and claims no requirement beyond
FR-045 and FR-046. The live view does not show the recorded turn count, token usage or cost
(BSB-34) and does not show the verdict or the component versions (BSB-33); the "Turns" here is the
agent's live progress counter, not the recorded turn count.

---

## STORY: BSB-26-PENDING-3

**Title:** Get a classified run outcome and output on my run branch
**Epic:** BSB-26 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-7, MVP

### Story
As a **skill author who is a project member**, I want **the builder to classify my run's outcome with the platform engine's result rules, keep the verdict the agent claimed, and leave its changes only on the run branch**, so that **I know whether the skill completed or failed and the next stage can verify exactly what it produced**.

### Acceptance Criteria

Scenario: A successful execution is classified as completed and its claimed verdict is recorded
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", state "running", started_at "2026-11-16T11:00:00Z", result_status NULL, claimed_verdict NULL, execution_error NULL and final_verdict NULL, a stub agent container for run 21 that exits with code 0 after uploading "runs/21/bb_step_result.json" with content {"status": "completed", "summary": "Applied the reproduced fix.", "files": ["bugfix.md"]}, a stub source-control provider in which the run's writer pushed commit "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1" to "refs/heads/skilltest/21", and a builder clock reading "2026-11-16T11:05:00Z"
When the execution worker observes the container exit
Then the "runs" row id 21 has state "completed", result_status "completed", claimed_verdict "completed", execution_error NULL, finished_at "2026-11-16T11:05:00Z" and final_verdict NULL, the stub source-control provider's ref "refs/heads/skilltest/21" points at "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", the provider received no ref-update or commit request for "refs/heads/main" or "refs/heads/test/atlas/bug-42", and GET "/projects/7/runs/21" renders "Outcome: completed"

Scenario: The agent's own verdict is preserved as the classified result
Given the same running run 21 and clock, the source-control state of the previous scenario, and a stub agent container that exits with code 0 after uploading "runs/21/bb_step_result.json" with content {"status": "BLOCK", "summary": "The reproduction could not be confirmed.", "files": []}
When the execution worker observes the container exit
Then the "runs" row id 21 has state "completed", result_status "BLOCK", claimed_verdict "BLOCK", execution_error NULL, finished_at "2026-11-16T11:05:00Z" and final_verdict NULL, and GET "/projects/7/runs/21" renders "Outcome: BLOCK"

Scenario: A non-zero exit with a valid result is a failed execution
Given the same running run 21 and clock, and a stub agent container that exits with code 2 after uploading "runs/21/bb_step_result.json" with content {"status": "completed", "summary": "Applied the reproduced fix.", "files": ["bugfix.md"]}
When the execution worker observes the container exit
Then the "runs" row id 21 has state "failed", result_status "failed_execution", claimed_verdict "completed", execution_error "The agent process exited with code 2.", finished_at "2026-11-16T11:05:00Z" and final_verdict NULL, and GET "/projects/7/runs/21" renders "Outcome: failed_execution"

Scenario: A run that produces no readable result is failed incomplete
Given the same running run 21 and clock, and a stub agent container that exits with code 0 without uploading "runs/21/bb_step_result.json"
When the execution worker observes the container exit
Then the "runs" row id 21 has state "failed", result_status "failed_incomplete", claimed_verdict NULL, execution_error "The run produced no readable result.", finished_at "2026-11-16T11:05:00Z" and final_verdict NULL, and no object exists at "runs/21/bb_step_result.json"

Scenario: A container that cannot start is a failed infrastructure run
Given the same running run 21, a stub runtime adapter that reports "Cannot pull agent image: no basic auth credentials" after its container-start counter reaches 1, and a builder clock reading "2026-11-16T11:00:05Z"
When the execution worker observes the adapter's start failure
Then the "runs" row id 21 has state "failed", result_status "failed_infra", claimed_verdict NULL, execution_error "The agent container could not be started.", finished_at "2026-11-16T11:00:05Z" and final_verdict NULL, the stub source-control provider received no ref-update or commit request, and no object exists at "runs/21/bb_step_result.json"

Scenario: The run may write only to its output branch
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", input_branch "test/atlas/bug-42", run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", state "running" and final_verdict NULL, a stub source-control provider that records every ref-update and commit request and whose ref "refs/heads/main" points at "f00d1c2e3a4b5d6f7a8b9c0d1e2f3a4b5c6d7e8f", whose ref "refs/heads/test/atlas/bug-42" points at "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" and whose ref "refs/heads/skilltest/21" points at "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", and the run's source-control writer from BSB-25-PENDING-3 whose only accepted target is "refs/heads/skilltest/21"
When the run's source-control writer attempts three pushes of commit "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1" — first to "refs/heads/skilltest/21", second to "refs/heads/main", third to "refs/heads/test/atlas/bug-42"
Then the first push is recorded once on "refs/heads/skilltest/21", the second and third are refused with "A run can only write to its run branch.", the provider's refs "refs/heads/main" and "refs/heads/test/atlas/bug-42" still point at "f00d1c2e3a4b5d6f7a8b9c0d1e2f3a4b5c6d7e8f" and "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", and the provider recorded 0 ref-update and 0 commit requests for them

### Covered requirements (traceability)
- FR-047

### Out of scope
Launching the container and recording the component versions (BSB-26-PENDING-1); the progress
and log live view (BSB-26-PENDING-2); recording the model profile and tier (BSB-26-PENDING-4);
running the shared verification layer, recording `final_verdict` and `verification`, and deciding
whether the claimed verdict was overturned (BSB-29); the compatibility, static-scan, turn-cap and
spend-cap refusals and the deadline, including `failed_timeout` (BSB-27); the static and LLM scans
(BSB-31 and BSB-32); readiness and re-verification (BSB-30); the run report's diff, Jira changes
and check sections (BSB-33); token, cost and turn usage and retention (BSB-34); Jira fixture
seeding (BSB-28); the command-line run (BSB-37).

### Notes / dependencies
Depends on BSB-26-PENDING-1 for a run in state "running", for the adapter that reports the
container exit, and for the `result_status` and `execution_error` columns; on BSB-25-PENDING-3 for
the run's source-control writer and the isolation rule; and on BSB-24-PENDING-1 for the run's
`input_branch` and `run_branch`. The result document is the agent image's
`runs/21/bb_step_result.json` (ADR SK-001 sections 5 and 6); the builder reads it and never
rewrites it.

This story owns the classification of the execution, the terminal execution values of
`runs.state`, and the output-branch publication. The platform engine's result rules join the
container exit status with `bb_step_result.json` (ADR SK-001 section 2a; `docs/skill-chain.md`
"Reporting the outcome"): a zero exit with a valid document takes the document's `status` as the
result status, a non-zero exit is `failed_execution`, a missing or unreadable document is
`failed_incomplete`, and a container that cannot be started is `failed_infra`. The four domain
statuses — `completed`, `BLOCK`, `changes_requested` and `escalation_required` — are accepted
verbatim, not mapped into a builder-specific vocabulary. `BLOCK` is shown as a classified outcome,
not rewritten to a success; whether the claimed verdict survives verification is BSB-29's job.
`failed_timeout` is BSB-27's deadline outcome and is not produced here.

`runs.state` is the lifecycle: `running` becomes `completed` when the execution produced a usable
outcome for verification, and `failed` when it did not. `runs.result_status` carries the engine's
classification and `runs.claimed_verdict` carries the document's `status` when the document exists,
including when the exit was non-zero; both columns are added by the data-model stage together with
`runs.execution_error`. `runs.final_verdict` and `runs.verification` stay NULL — BSB-29 writes them.
The run's own metadata is never rewritten: the inputs, skills commit, bundle and component
versions recorded earlier stay as they were.

The agent's changes are pushed through the run's source-control writer from BSB-25-PENDING-3, and
the only accepted target is `runs.run_branch`. A write to `refs/heads/main`, to the input branch or
to any other ref is refused, so the output exists only on `skilltest/21` from the recorded
baseline. This is the cross-epic follow-up BSB-25's review records for BSB-26 (Finding 6): the
deny-by-default rule is used here, not only the input-branch comparison. BSB-33 uses the baseline
and the run branch for the diff, BSB-29 grades the run branch, and BSB-34 consumes the terminal
record for usage.

---

## STORY: BSB-26-PENDING-4

**Title:** See the exact model profile and tier the run used
**Epic:** BSB-26 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-7, MVP

### Story
As a **skill author who is a project member**, I want **the run to record the exact model profile, tier and concrete model it executed with and to show them on the run page**, so that **I can reproduce the run, compare tiers fairly, and know which model produced the result**.

### Acceptance Criteria

Scenario: The model profile, tier and concrete model used are recorded and shown
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", run_branch "skilltest/21", model_profile_id 5, tier "medium", model NULL, state "prepared" and execution_error NULL, an "integrations" row id 5 with project_id 7, kind "ai_model", config {"name": "Cheap smoke runs", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-opus-5-5", "medium": "claude-sonnet-5-5", "low": "claude-haiku-5-5"}, "test_only": true} and secret_ref "skill-builder/7/integration-5", a secret store holding "sk-ant-test-3c9e" at "skill-builder/7/integration-5", the "skill_bundles" row, source-control and Jira integrations of BSB-26-PENDING-1, a stub runtime adapter whose container-start counter is 0 and whose environment is empty, a stub model endpoint whose request counter is 0, and a builder clock reading "2026-11-16T11:00:00Z"
When the execution worker processes run 21
Then the stub runtime adapter's container-start counter is 1, its environment contains BB_MODEL "claude-sonnet-5-5", the vendor key "sk-ant-test-3c9e" and the base URL "https://api.anthropic.com", the "runs" row id 21 has model_profile_id 5, tier "medium", model "claude-sonnet-5-5" and state "running", and after the run reaches state "completed" GET "/projects/7/runs/21" renders "Model profile: Cheap smoke runs (id 5)", "Model tier: medium" and "Model: claude-sonnet-5-5"

Scenario: The tier selects the model mapped by the profile
Given two "runs" rows id 21 with tier "low" and id 22 with tier "high", each with project_id 7, skill "sdlc-fix-bug-reproduce", run_branch "skilltest/21" and "skilltest/22", model_profile_id 5, model NULL and state "prepared", the AI-model integration 5 of the previous scenario with its complete high, medium and low mapping, the "skill_bundles" rows and source-control and Jira integrations of BSB-26-PENDING-1, and a stub runtime adapter whose container-start counter is 0
When the execution worker processes run 21 and afterwards run 22
Then run 21's launch environment contains BB_MODEL "claude-haiku-5-5" and run 22's launch environment contains BB_MODEL "claude-opus-5-5", the "runs" row id 21 has tier "low" and model "claude-haiku-5-5", and the "runs" row id 22 has tier "high" and model "claude-opus-5-5"

Scenario: A profile changed after the run does not rewrite the run's record
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", model_profile_id 5, tier "low", model "claude-haiku-5-5", state "completed", result_status "completed", claimed_verdict "completed" and final_verdict NULL, a signed-in skill author Ada who has a "project_members" row for Project Atlas (id 7), and an "integrations" row id 5 with project_id 7, kind "ai_model", config {"name": "Renamed profile", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-opus-5-5", "medium": "claude-sonnet-5-5", "low": "claude-haiku-9-9"}, "test_only": true}
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Model tier: low" and "Model: claude-haiku-5-5", and the body does not render "claude-haiku-9-9"

Scenario: A model profile that disappeared before launch fails the run
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", run_branch "skilltest/21", model_profile_id 5, tier "low", model NULL, state "prepared" and execution_error NULL, no "integrations" row with id 5 for project 7, the "skill_bundles" row and the source-control and Jira integrations of BSB-26-PENDING-1, a stub runtime adapter whose container-start counter is 0, and a stub model endpoint whose request counter is 0
When the execution worker processes run 21
Then the "runs" row id 21 has state "failed", result_status "failed_infra", execution_error "The run's model profile is no longer available.", model NULL, started_at NULL and finished_at "2026-11-16T11:00:00Z", the stub runtime adapter's container-start counter remains 0, and the stub model endpoint's request counter remains 0

### Covered requirements (traceability)
- FR-049
- FR-152

### Out of scope
Choosing a model profile and tier in the run request and validating them (BSB-24-PENDING-4);
creating, editing or deleting AI model profiles and their tier mappings (BSB-23-PENDING-3);
storing, verifying or rotating the vendor key (BSB-23); the LLM security scan's separate
project-level model (BSB-32); launching the container, recording the other component versions and
classifying the outcome (BSB-26-PENDING-1 and BSB-26-PENDING-3); the run report's model fields
(BSB-33); token usage and cost (BSB-34); a per-run model override outside the profile and tier.

### Notes / dependencies
Depends on BSB-24-PENDING-4 for `runs.model_profile_id` and `runs.tier`, on BSB-23-PENDING-3 for
the `ai_model` integration and its complete high, medium and low tier mapping, on
BSB-23-PENDING-4 for the stored vendor key, on BSB-26-PENDING-1 for the execution worker and the
launch environment, and on BSB-22 for the run page's membership check. The profile is read at
launch, not at page load, so the record describes what the container actually used.

This story owns the model fields on the run and their display. At launch it reads the profile
`model_profile_id`, resolves `tier` through the profile's `models` object to the concrete model
identifier, puts that identifier in the launch environment as `BB_MODEL` together with the
profile's vendor key and base URL, and records `runs.model_profile_id`, `runs.tier` and
`runs.model`. `runs.model` must be added by the data-model stage; the other two columns already
exist in ADR SK-001 section 9. The profile's key is injected at launch from Secrets Manager and is
never written to the database, the builder log, the progress or the result. The profile is not
re-resolved for display: the page shows the recorded profile id, tier and concrete model, so a
later rename or mapping change cannot rewrite history. The profile's name is shown for
readability from the current integration record, but the record that matters is the id.

There is no fallback. If the selected profile is gone or is not an AI-model profile for the run's
project at launch, the run fails with the message above and no container starts; it is not retried
with another profile or a default model. The vendor key and base URL are not exposed in the run
page. The run's model environment is built here and consumed by BSB-26-PENDING-1's launch; the
model endpoint is called by the agent, not by the builder, so this story makes no model request
itself. BSB-33 may show the same recorded values in the run report, and BSB-34 accounts for the
tokens and cost the model call produced.

---

*Generated by `sdlc-plan-stories-write`. Coverage: FR-044, FR-045, FR-046, FR-047, FR-048, FR-049,
FR-151 and FR-152 all covered. Next steps: `sdlc-plan-epic-review` reviews the set on a different
model family; then `sdlc-plan-epic-sequence` orders the stories and `sdlc-tracker-sync` publishes
them to Jira.*
