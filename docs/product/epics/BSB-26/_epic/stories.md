# Stories — BSB-26 (Run execution & outcome capture)

Source: Jira epic **BSB-26** — *Run execution & outcome capture* (feature area FA-7, release MVP,
labels FA-7, MVP), fetched read-only from the Atlassian project `bheembhai-skill-builder`; its
summary, description, functional scope, goal and stated edge cases are the same as the BSB-26
section of `docs/product/epics.md`. The requirement IDs mapped to the epic are in
`docs/product/epic-map.json`.

Epic BSB-26 covers 8 requirements. They decompose into the 4 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-26`), is epic
**BSB-26**, fetched read-only through the Atlassian REST API (the Atlassian MCP server was not
connected in this session), and its eight requirements are the ones decomposed here. Nothing was
written to Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-044 | BSB-26-PENDING-1 |
| FR-045 | BSB-26-PENDING-2 |
| FR-046 | BSB-26-PENDING-2 |
| FR-047 | BSB-26-PENDING-3 |
| FR-048 | BSB-26-PENDING-4 |
| FR-049 | BSB-26-PENDING-4 |
| FR-151 | BSB-26-PENDING-4 |
| FR-152 | BSB-26-PENDING-4 |

The epic's three stated edge cases are covered explicitly: a runtime that fails to start is
recorded as `failed_infra` (BSB-26-PENDING-1), a runtime that exits without a classifiable result
is recorded as `failed_incomplete` or `failed_execution` (BSB-26-PENDING-3), and log truncation is
recorded with an exact marker in the stored log and on the run page (BSB-26-PENDING-2).

## Execution and outcome contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control and object-store
fixture unless it says otherwise. The member session, the local `users` rows and the
`skill-builders` gate are established by epic BSB-18. The project, `projects` rows and
`project_members` rows are established by epic BSB-22. The integrations are established by epic
BSB-23. The prepared run — the `runs` row with `skills_commit_sha` and `run_branch` set, the
`skill_bundles` row, and the run branch `skilltest/1` — is the output of epic BSB-25 (FR-038 to
FR-043); this epic consumes it. The run columns and the `skill_bundles` columns follow
`docs/adr/SK-001-skill-builder.md` §5 and §9.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z` |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing` |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42`, `created_at` = `2026-11-14T09:00:00Z`; id `8` has `name` = `Search smoke`, `owner_id` = `43`; ids `1` to `6`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)`; Alan has no row for project `7` |
| `ai_model` integration (project 7) | row `id` = `7`, `kind` = `ai_model`, `config` = `{"profiles":[{"id":3,"name":"Anthropic test","vendor":"anthropic","base_url":"https://api.anthropic.test","tiers":{"high":"test-model-high","medium":"test-model-medium"}},{"id":4,"name":"Smoke","vendor":"anthropic","base_url":"https://api.anthropic.test","tiers":{"medium":"test-model-medium"}}]}`, `secret_ref` = `skill-builder/7/ai_model` |
| `github` integration (project 7) | row `id` = `6`, `kind` = `github`, `config` = `{"repo":"saraavrnd/bheembhai-skill-fixtures","base_branch":"main"}`, `secret_ref` = `skill-builder/7/github`, `mcp` = `null`, `verified_at` = `2026-11-14T09:02:00Z` |
| `jira` integration (project 7) | row `id` = `5`, `kind` = `jira`, `config` = `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`, `secret_ref` = `skill-builder/7/jira`, `mcp` = `{"servers":[{"name":"jira","transport":"stdio","command":"mcp-atlassian","args":["--jira-url","https://old.atlassian.net"]}]}`, `verified_at` = `2026-11-14T09:00:00Z` |
| Integration credentials | the secret held at `skill-builder/7/ai_model` has exactly the value `sk-ant-test-5f2c8e1d`; the `github` and `jira` credentials are held at their `secret_ref` values. Every credential is injected into the runtime by reference and never appears in the stored environment or the log |
| Run 1 (the prepared run) | exactly one row: `id` = `1`, `project_id` = `7`, `user_id` = `42`, `skill` = `sdlc-fix-bug-triage`, `skills_ref` = `test/ada/fix-reproduce`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `input_branch` = `main`, `run_branch` = `skilltest/1`, `context` = `{"workflow":"bug-fix","step":"triage"}`, `model_profile_id` = `3`, `tier` = `high`, `state` = `queued`, `kind` = `run`, `created_at` = `2026-11-15T10:00:00Z`; `agent_image_digest`, `stepkit_version`, `verify_version`, `claimed_verdict`, `final_verdict`, `verification`, `cost_usd` and `parent_run_id` are `NULL` |
| Run 2 (only the kit-v8 scenario) | prepared exactly like run `1` except `id` = `2` and `run_branch` = `skilltest/2`; the rest of the row is identical apart from `created_at` = `2026-11-15T10:00:01Z` |
| Run 3 (only the reviewer-feedback scenario) | prepared exactly like run `1` except `id` = `3`, `run_branch` = `skilltest/3` and `context` = `{"workflow":"bug-fix","step":"triage","reviewer_feedback":"Please handle an empty issue title without failing.","upstream_handoff":{"step":"reproduce","result_status":"completed","summary":"Reproduction confirmed on the input branch."}}`; `created_at` = `2026-11-15T10:00:02Z` |
| `skill_bundles` row | `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `skill` = `sdlc-fix-bug-triage`, `bundle_sha256` = `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`, `s3_key` = `bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz` |
| Object-store bucket | `skill-builder-runs`; the run prefix is `runs/1/` |
| Bundle URL | a presigned GET URL on `skill-builder-runs` whose path is exactly `/bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz`; the query string is generated per launch and is not asserted |
| `skill-builder/kit.txt` | exactly `kit-v7` |
| `kit.json` for `kit-v7` | `{"kit":"kit-v7","env_contract_version":"3","bheembhai-stepkit":"0.4.0","bheembhai-verify":"2.1.2","agent_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-agent@sha256:4d2a6f8c0e1b3a5d7f9c2e4a6b8d0f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d"}` |
| `kit.json` for `kit-v8` (only the kit-v8 scenario) | `{"kit":"kit-v8","env_contract_version":"4","bheembhai-stepkit":"0.5.0","bheembhai-verify":"2.2.0","agent_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-agent@sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13"}` |
| Runtime | Docker on the builder host, driven through the pinned step kit's launch spec; every agent container carries the labels `bb.run_id` = the run id and `bb.stepkit` = the step kit version |
| Workflow step context | the skills commit's `config/bug-fix.yaml` declares workflow `bug-fix` with step `triage`; for step `triage` it declares `allowed_result_statuses` exactly `["completed","BLOCK","changes_requested","escalation_required"]` |
| Run page | `GET https://builder.skillbuilder.internal/projects/{project_id}/runs/{run_id}` |
| Progress API | `GET https://builder.skillbuilder.internal/api/projects/{project_id}/runs/{run_id}/progress` |
| Log API | `GET https://builder.skillbuilder.internal/api/projects/{project_id}/runs/{run_id}/log?tail={n}` where `n` is an integer from `1` to `200` and defaults to `200` |
| Success status | HTTP 200 with `Content-Type: text/html; charset=utf-8` for the run page; HTTP 200 with `Content-Type: application/json` for both APIs |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |
| Current time | `2026-11-15T10:00:00Z` before execution; run `1` is claimed at `2026-11-15T10:01:00Z` |

`runs.agent_image_digest` stores the digest only (`sha256:` followed by 64 lowercase hex
characters), not the repository prefix. The ECR repository and tag are never stored on the run; a
tag such as `:latest` is never accepted in place of a digest.

**Run state values.** The values below are the states these stories set or read. The starting
value `queued` is created by epic BSB-24; the terminal values are created here, except
`failed_timeout`, which epic BSB-27 owns. Two further terminal values belong to sibling epics and
are not set by these stories: the value epic BSB-27 records when a run stops at its turn or spend
cap (FR-051, FR-053), and the value epic BSB-25 records when preparation fails. Their exact names
are still open (Open question 3 of this epic's review), so no scenario below asserts them.

| `runs.state` | Meaning | Set by |
|--------------|---------|--------|
| `queued` | the run exists and is prepared (or still being prepared) but has not been claimed | epic BSB-24 creates it; epic BSB-25 leaves a prepared run in this state |
| `running` | an executor has claimed the run and the runtime is executing | BSB-26-PENDING-1 |
| `completed` | the runtime exited and the platform engine returned a classifiable result status | BSB-26-PENDING-3 |
| `failed_infra` | the runtime could not be started | BSB-26-PENDING-1 |
| `failed_execution` | the runtime exited non-zero and produced no valid result | BSB-26-PENDING-3 |
| `failed_incomplete` | the runtime exited but the uploaded result was missing, malformed, or not an allowed status | BSB-26-PENDING-3 |
| `failed_timeout` | the run exceeded its deadline | epic BSB-27; never set by these stories |

**Terminal-write rule.** Every transition out of `running` is a single compare-and-set update on
`state = 'running'`; the first terminal write wins and a later writer that finds the row no longer
`running` leaves it unchanged. Epic BSB-27 writes its terminal state before it stops the
container.

**Executor claim contract.** The builder runs one or more executor processes. On each claim pass
(interval exactly 1 second) an executor claims the oldest run matching
`state = 'queued' AND skills_commit_sha IS NOT NULL AND run_branch IS NOT NULL` with one
compare-and-set update that changes `state` to `running` and returns the row. Exactly one executor
wins a given run. A run whose `skills_commit_sha` or `run_branch` is `NULL` is never claimed. A run
already in `running` or in any terminal state is never claimed again. On claim, before the
container is created, the executor persists the provenance values in BSB-26-PENDING-4.

**Result rules (the platform engine's join).** After a container that started exits, the executor
classifies the outcome from the exit status and `s3://skill-builder-runs/runs/1/bb_step_result.json`
exactly as follows. A `result_status` is valid only when the uploaded file is a JSON object whose
`result_status` is a string present in `allowed_result_statuses`.

| Runtime event | `bb_step_result.json` | `runs.state` | `runs.claimed_verdict` |
|---|---|---|---|
| exits with status `0` or any non-zero status | valid, allowed `result_status` | `completed` | that `result_status` |
| exits with status `0` | missing, not valid JSON, no string `result_status`, or a status not in `allowed_result_statuses` | `failed_incomplete` | `NULL` |
| exits with a non-zero status | missing, not valid JSON, no string `result_status`, or a status not in `allowed_result_statuses` | `failed_execution` | `NULL` |
| runtime fails to start | not read | `failed_infra` | `NULL` |

A valid uploaded result takes precedence over the exit status: a skill that reports `BLOCK` or
`changes_requested` and exits non-zero is a completed execution whose claimed verdict is that
status. `runs.final_verdict` and `runs.verification` are not written by this epic; they stay `NULL`
until epic BSB-29 verifies the output.

The run page renders the outcome region with exactly one of these texts:

| `runs.state` | Exact page text |
|--------------|-----------------|
| `completed` | `Outcome: ` followed by `runs.claimed_verdict` (for example `Outcome: completed` or `Outcome: BLOCK`) |
| `failed_infra` | `The runtime could not be started.` |
| `failed_execution` | `The runtime exited with a non-zero status without a valid result.` |
| `failed_incomplete` | `The runtime exited without a classifiable result.` |

While the run is `running` the outcome region is absent.

**Environment handed to the runtime.** For run `1` the executor starts the agent container with
the image from `kit.json` and, among the builder-set variables, exactly these values; the model,
`github` and `jira` credentials are injected from Secrets Manager by epic BSB-23's mechanism and
are not stored or logged.

| Variable | Value |
|----------|-------|
| `RUN_BRANCH` | `skilltest/1` |
| `BB_RUN_ID` | `1` |
| `BB_SKILL_URL` | the presigned bundle URL above |
| `BB_SKILL_SHA256` | `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` |
| `BB_MODEL` | `test-model-high` (profile `3`, tier `high`) |
| `BB_CONTEXT` | the pinned step kit's `build_step_context` output for run `1`; its `allowed_result_statuses` is exactly `["completed","BLOCK","changes_requested","escalation_required"]` and its `gate_follows`, `gate_role`, `reviewer_feedback` and `upstream_handoff` are `false`, `null`, `null` and `null`. The rest of the object's shape belongs to the platform step kit and is not restated here |
| `BB_REPO_URL` | `https://github.com/saraavrnd/bheembhai-skill-fixtures.git`, built from the `github` integration's `config.repo` |
| `BB_BASE_BRANCH` | `main`, built from the `github` integration's `config.base_branch` |
| `BB_MCP_CONFIG` | the JSON value `{"servers":[{"name":"jira","transport":"stdio","command":"mcp-atlassian","args":["--jira-url","https://old.atlassian.net"]}]}`, built from the `jira` integration's `mcp` value; the `github` integration's `mcp` is `null` and contributes no server |
| `BB_PROGRESS_PUT_URL` | a presigned PUT URL on `skill-builder-runs` whose path is exactly `/runs/1/progress.json`; the query string is generated per launch and is not asserted |
| `BB_RESULT_PUT_URL` | a presigned PUT URL on `skill-builder-runs` whose path is exactly `/runs/1/bb_step_result.json`; the query string is generated per launch and is not asserted |

`BB_REPO_URL`, `BB_BASE_BRANCH` and `BB_MCP_CONFIG` are built from the project's `github` and
`jira` integrations; the two PUT URLs are the ADR-014 presigned URLs the step kit's env contract
requires. No credential value appears in the stored environment or the log (NFR-004, epic
BSB-23).

**Progress contract.** While the agent runs, it writes `progress.json` to
`s3://skill-builder-runs/runs/1/progress.json`. The builder reads that object once per second and
the progress API returns the latest read plus the run id and the run's current state:

```
{"run_id":1,"step":"triage","state":"running","message":"Reading issue LEARN-87","percent":40,"updated_at":"2026-11-15T10:01:05Z"}
```

The progress region is the element with id `run-progress`. The `state` in the API body and in that
region is always `runs.state`, never the `state` field the agent writes inside `progress.json`; the
agent's own value is ignored. The run page shows the progress region with the exact text
`Running step triage — Reading issue LEARN-87 (40%)`. Before the first `progress.json` is readable
the progress API returns
`{"run_id":1,"step":null,"state":"running","message":null,"percent":0,"updated_at":null}` and the
page's progress region shows `Waiting for the skill to report progress.` A `percent` outside `0` to
`100` is clamped to that range for display.

Once `runs.state` is terminal the run page has no element with id `run-progress`, exactly as it has
no outcome region while the run is `running`. The progress API keeps returning the last read values
with `state` set to the run's `runs.state` value; when no `progress.json` was ever readable it
returns `{"run_id":1,"step":null,"state":"failed_infra","message":null,"percent":0,"updated_at":null}`
for a `failed_infra` run, with the `state` value following `runs.state`.

**Log contract.** While the agent runs, its standard output and standard error are captured to
`s3://skill-builder-runs/runs/1/agent.log`. The log API returns the last `tail` lines, split on
`\n`, with a trailing newline producing no empty final element:

```
{"run_id":1,"lines":["2026-11-15T10:01:01Z INFO starting skill sdlc-fix-bug-triage","2026-11-15T10:01:03Z INFO reading issue LEARN-87","2026-11-15T10:01:05Z INFO writing bug-triage.md"],"truncated":false}
```

The run page shows those lines in order in an element with id `run-log`. Before the first
`agent.log` is readable the log API returns `{"run_id":1,"lines":[],"truncated":false}` and that
element shows `Waiting for log output.`

The stored log is capped at `10485760` bytes. When the runtime emits more, the builder stores the
last `10485760` bytes and prepends this exact marker line:

```
[skill-builder] log truncated: showing the last 10485760 bytes of 12582912 bytes; 2097152 earlier bytes discarded.
```

In that case the log API sets `"truncated":true`, returns the marker as `lines[0]`, and follows it
with the last `tail` lines of the stored log; the run page shows the marker above the log.
Truncation never changes `runs.state`.

The log API and the page's `run-log` element keep serving the stored log after `runs.state` becomes
terminal, so a start-failure line or a truncation marker stays readable until epic BSB-33 replaces
the page; ending a run never deletes or hides its log.

Before the captured log is stored or served, every occurrence of a known credential value is
replaced with exactly `[REDACTED]` (NFR-004, using epic BSB-23's redaction mechanism). Which
process writes `agent.log` — the builder's capture of the container's standard output and standard
error, or an upload by the image — is still open (Open question 2 of this epic's review); this
contract fixes the stored object and the lines the API and page serve, not the writer.

**Error responses** (each has `Content-Type: application/json`). The checks run in this fixed
order: BSB-18's session and group gates, then BSB-22's `project_not_found` on the path project,
then BSB-22's membership check on the path project, then this epic's `run_not_found`. The earlier
checks' fixed bodies are not restated here.

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| `run_id` names no `runs` row | 404 | `{"error":{"code":"run_not_found","message":"Run 999 does not exist."}}` |
| the run's `project_id` differs from the path's `project_id` | 404 | `{"error":{"code":"run_not_found","message":"Run 1 does not exist."}}` |
| the run's `project_id` has no `project_members` row for the caller | 403 | `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}` |

In `run_not_found` the number is the `run_id` from the path.

**Cross-epic notes.**

- **BSB-24's workflow fixture and the default context.** Epic BSB-24 owns workflow and step
  selection and its fixture already declares workflow `bug-fix` with steps `triage`, `reproduce`,
  `root-cause` and `implement`. This epic consumes one more field of that fixture, step `triage`'s
  `allowed_result_statuses`. BSB-24's scenarios assert only the workflow and step names, so no
  BSB-24 scenario changes. When the author omits `context`, BSB-24 stores `{}` and defers default
  workflow and step resolution to this epic. Who resolves the default — run start or BSB-26 at
  claim — and what a run whose skill is used by no workflow, or by more than one, does is still
  open (BSB-24 Open question 4, repeated as Open question 1 of this epic's review). No scenario
  below asserts a `BB_CONTEXT` or an `allowed_result_statuses` value for an omitted context until
  that answer is recorded.
- **BSB-25 hand-off.** Epic BSB-25 (FR-038 to FR-043) has no stories yet. This epic assumes its
  outputs: `skills_commit_sha`, `run_branch`, the `skill_bundles` row and the run branch
  `skilltest/1`, per §5 of the ADR. A prepared run stays `queued` until an executor claims it. If
  BSB-25 later introduces a distinct prepared state or a different trigger, only the claim
  predicate and the stories' "prepared and queued" preconditions are re-pointed; the result rules,
  environment values and provenance columns do not change.
- **BSB-27.** Epic BSB-27 owns turn and spend caps, the installation deadline, `failed_timeout`,
  scan refusals and re-runs. This epic never enforces a cap or a deadline; a run it leaves
  `running` may be terminated as `failed_timeout` by BSB-27.
- **BSB-29.** Epic BSB-29 owns verification. `final_verdict` and `verification` stay `NULL` here.
  BSB-29 must use the `verify_version` this epic records on the run, not a value read from
  `kit.txt` at verification time.
- **BSB-33 and BSB-34.** Epic BSB-33 extends the run page and owns the full run report and change
  evidence; this epic owns only the live progress region, the log region, the run state and the
  failure-reason text on that page. Epic BSB-34 owns token usage and cost; `cost_usd` and the
  token columns stay untouched here.

## STORY: BSB-26-PENDING-1

**Summary:** Execute a prepared run in the pinned platform runtime
**Epic:** BSB-26 · **Release:** MVP · **Estimate:** 8 · **Labels:** FA-7, MVP

### Story
As a **skill author**, I want **my prepared run to execute in the platform's own runtime and pinned agent image**, so that **a builder run behaves like a platform run instead of a builder-specific simulation, and a runtime that cannot start is recorded as an infrastructure failure rather than disappearing**.

### Acceptance Criteria

#### Scenario: A prepared run is claimed and starts in the pinned agent image
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And run `1` exists prepared and `state` = `queued` with `skills_commit_sha` and `run_branch` set as in the contract
And the `skill_bundles` row and bundle object exist as in the contract
And `skill-builder/kit.txt` contains `kit-v7`
And the builder executor is running with a 1-second claim interval
When the executor performs its next claim at `2026-11-15T10:01:00Z`
Then within 2 seconds `SELECT state FROM runs WHERE id = 1` returns `running`
And the runtime has started exactly one container labelled `bb.run_id` = `1`
And that container's image is exactly `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-agent@sha256:4d2a6f8c0e1b3a5d7f9c2e4a6b8d0f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d`
And the container's label `bb.stepkit` is exactly `0.4.0`
And the container's environment contains `RUN_BRANCH` = `skilltest/1`, `BB_RUN_ID` = `1`, `BB_SKILL_SHA256` = `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` and `BB_MODEL` = `test-model-high`
And the container's `BB_SKILL_URL` is a presigned URL whose path is exactly `/bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz`
And the container's `BB_PROGRESS_PUT_URL` is a presigned URL whose path is exactly `/runs/1/progress.json`
And the container's `BB_RESULT_PUT_URL` is a presigned URL whose path is exactly `/runs/1/bb_step_result.json`
And the container's `BB_CONTEXT` is the pinned step kit's `build_step_context` output for run `1`, whose `allowed_result_statuses` is exactly `["completed","BLOCK","changes_requested","escalation_required"]`

#### Scenario: The runtime receives the project's git coordinates and MCP configuration
Given run `1` exists prepared and `state` = `queued` as in the contract
And `skill-builder/kit.txt` contains `kit-v7`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then the runtime has started exactly one container labelled `bb.run_id` = `1`
And that container's environment contains `BB_REPO_URL` = `https://github.com/saraavrnd/bheembhai-skill-fixtures.git` and `BB_BASE_BRANCH` = `main`
And that container's `BB_MCP_CONFIG` is the JSON value `{"servers":[{"name":"jira","transport":"stdio","command":"mcp-atlassian","args":["--jira-url","https://old.atlassian.net"]}]}`
And none of that container's environment values is exactly `sk-ant-test-5f2c8e1d`

#### Scenario: Reviewer feedback and upstream handoff reach the runtime context
Given run `3` exists prepared and `state` = `queued` with the context in the fixture table
And `skill-builder/kit.txt` contains `kit-v7`
And the builder executor is running with a 1-second claim interval
When the executor claims run `3`
Then within 2 seconds `SELECT state FROM runs WHERE id = 3` returns `running`
And the runtime has started exactly one container labelled `bb.run_id` = `3`
And that container's `BB_CONTEXT` is the pinned step kit's `build_step_context` output for run `3`, whose `reviewer_feedback` is exactly `Please handle an empty issue title without failing.`
And that container's `BB_CONTEXT`'s `upstream_handoff` is exactly the JSON value `{"step":"reproduce","result_status":"completed","summary":"Reproduction confirmed on the input branch."}`

#### Scenario: A run that is not prepared is not claimed
Given run `1` exists with `state` = `queued`, `skills_commit_sha` = `NULL` and `run_branch` = `NULL`
And the builder executor is running with a 1-second claim interval
When the executor performs three claim passes
Then `SELECT state FROM runs WHERE id = 1` still returns `queued`
And the runtime has started no container labelled `bb.run_id` = `1`

#### Scenario: Two executors claim a prepared run exactly once
Given run `1` exists prepared and `state` = `queued` as in the contract
And two builder executor processes `A` and `B` are running with a 1-second claim interval
When both processes complete their next claim pass at `2026-11-15T10:01:00Z`
Then exactly one process changes `runs.state` from `queued` to `running`
And `SELECT count(*) FROM runs WHERE id = 1 AND state = 'running'` returns `1`
And the runtime has started exactly one container labelled `bb.run_id` = `1`

#### Scenario: A runtime that fails to start is recorded as an infrastructure failure
Given run `1` exists prepared and `state` = `queued` as in the contract
And the runtime adapter is configured so that starting the pinned agent image fails with exactly `Error response from daemon: No such image`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then within 2 seconds `SELECT state, claimed_verdict FROM runs WHERE id = 1` returns exactly `failed_infra | NULL`
And the first line of `s3://skill-builder-runs/runs/1/agent.log` is exactly `[skill-builder] runtime start failed: Error response from daemon: No such image`
And the run page at `GET https://builder.skillbuilder.internal/projects/7/runs/1` contains the exact text `The runtime could not be started.`
And that page's element with id `run-log` contains the exact text `[skill-builder] runtime start failed: Error response from daemon: No such image`
And a further claim pass leaves `SELECT state FROM runs WHERE id = 1` as `failed_infra`
And the runtime has started no container labelled `bb.run_id` = `1`

### Covered requirements (traceability)
- FR-044

### Out of scope
Resolving the skills branch to a commit SHA, packing the bundle, creating the run branch and
recording the baseline (epic BSB-25, FR-038 to FR-043). Classifying the outcome after a started
container exits (BSB-26-PENDING-3). Recording component versions, verifier version, model profile
and tier on the run row (BSB-26-PENDING-4). Turn and spend caps, the deadline, `failed_timeout`,
scan refusals and re-runs (epic BSB-27). Verifying the run's output (epic BSB-29). Run reports,
history, comparison, tracing, token usage and cost (epics BSB-33, BSB-34 and BSB-35). The CLI
entry point that starts the same runner (epic BSB-37).

### Notes / dependencies
- Depends on epic BSB-24 for the `runs` row and its `queued` starting state, on epic BSB-25 for the
  prepared `skills_commit_sha`, `run_branch` and `skill_bundles` row, and on epic BSB-23 for the
  `ai_model`, `github` and `jira` integrations and for FR-128/FR-129's stored MCP definitions,
  which this story renders into the container environment. It also depends on the
  installation-provisioned `skill-builder-runs` bucket (SK-001 §6, the same bucket BSB-25 writes
  bundles to).
- This story renders FR-128/FR-129's stored MCP definitions and the `github` integration's
  repository coordinates into `BB_MCP_CONFIG`, `BB_REPO_URL` and `BB_BASE_BRANCH`, and supplies
  the step kit's presigned PUT URLs for `progress.json` and `bb_step_result.json`. Credential values
  are injected by `secret_ref` and never appear in the stored environment or the log (NFR-004,
  epic BSB-23).
- The agent image and the launch spec are the platform's own, pinned by `kit.txt` and `kit.json`;
  this story reuses the step kit's launcher and does not build a bespoke executor. The test asserts
  the digest, the step kit label and the environment contract rather than the launch code path.
- The launch environment carries the step kit's tracing settings with the test-environment marker
  required by NFR-011; epic BSB-34 owns the trace store and the marker's value.
- The claim is one compare-and-set update, so two executors cannot both start a container. The
  executor does not claim a row until BSB-25 has set both `skills_commit_sha` and `run_branch`.
  A run BSB-25 leaves `queued` because its preparation failed is BSB-25's to terminate and is
  never claimed here. After an executor restart, an executor finds its in-flight runs by the
  `bb.run_id` container label.
- A start failure is terminal: there is no automatic retry in this epic. Re-running a failed run
  belongs to epic BSB-27 (FR-056). The reason is durable in two places: the `runs.state` value and
  the first line of the stored log.
- The run page route and the two API routes are under BSB-18's session and group gates and BSB-22's
  project-membership check. BSB-33 extends the same page and must not remove these live regions.

---

## STORY: BSB-26-PENDING-2

**Summary:** Watch a running skill's progress and logs
**Epic:** BSB-26 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-7, MVP

### Story
As a **skill author**, I want **to watch a running skill's progress and logs on the run page**, so that **I can tell whether the skill is working, where it is, and whether it is stuck before the run ends**.

### Acceptance Criteria

#### Scenario: The run page shows the latest progress and log lines
Given run `1` exists with `state` = `running` and Ada is a member of project `7`
And `s3://skill-builder-runs/runs/1/progress.json` contains exactly `{"step":"triage","state":"running","message":"Reading issue LEARN-87","percent":40,"updated_at":"2026-11-15T10:01:05Z"}`
And `s3://skill-builder-runs/runs/1/agent.log` contains exactly the three lines `2026-11-15T10:01:01Z INFO starting skill sdlc-fix-bug-triage`, `2026-11-15T10:01:03Z INFO reading issue LEARN-87` and `2026-11-15T10:01:05Z INFO writing bug-triage.md`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/projects/7/runs/1` carrying that `sb_session` cookie
Then the builder responds with HTTP status 200
And the `Content-Type` response header is `text/html; charset=utf-8`
And the response body contains the exact text `Running step triage — Reading issue LEARN-87 (40%)`
And the response body's element with id `run-log` contains those three log lines in that order
And the response body does not contain the text `Waiting for the skill to report progress.`

#### Scenario: Progress and log APIs return the current values
Given run `1` exists with `state` = `running` and Ada is a member of project `7`
And `progress.json` and `agent.log` contain the objects and lines from the previous scenario
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/progress` and `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/log?tail=200` carrying that `sb_session` cookie
Then the progress response is HTTP 200 with `Content-Type` `application/json` and its body equals the JSON value `{"run_id":1,"step":"triage","state":"running","message":"Reading issue LEARN-87","percent":40,"updated_at":"2026-11-15T10:01:05Z"}`
And the log response is HTTP 200 with `Content-Type` `application/json` and its body equals the JSON value `{"run_id":1,"lines":["2026-11-15T10:01:01Z INFO starting skill sdlc-fix-bug-triage","2026-11-15T10:01:03Z INFO reading issue LEARN-87","2026-11-15T10:01:05Z INFO writing bug-triage.md"],"truncated":false}`

#### Scenario: New progress and log output appear within two seconds
Given run `1` exists with `state` = `running` and the progress and log objects from the previous scenario
And the builder reads `progress.json` and `agent.log` once per second
When `progress.json` is replaced with exactly `{"step":"triage","state":"running","message":"Writing bug-triage.md","percent":80,"updated_at":"2026-11-15T10:01:20Z"}`
And the line `2026-11-15T10:01:21Z INFO writing bug-triage.md` is appended to `agent.log`
Then within 2 seconds a fresh `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/progress` returns a body whose `message` is exactly `Writing bug-triage.md` and whose `percent` is `80`
And within 2 seconds a fresh `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/log?tail=200` returns `lines` whose last element is exactly `2026-11-15T10:01:21Z INFO writing bug-triage.md`
And a fresh `GET https://builder.skillbuilder.internal/projects/7/runs/1` contains the exact text `Running step triage — Writing bug-triage.md (80%)`

#### Scenario: A run with no progress or log output shows an explicit empty state
Given run `1` exists with `state` = `running`
And `s3://skill-builder-runs/runs/1/progress.json` does not exist
And `s3://skill-builder-runs/runs/1/agent.log` does not exist
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/projects/7/runs/1` carrying that `sb_session` cookie
Then the response body contains the exact text `Waiting for the skill to report progress.`
And the response body's element with id `run-log` contains the exact text `Waiting for log output.`
And the progress API returns the JSON value `{"run_id":1,"step":null,"state":"running","message":null,"percent":0,"updated_at":null}`
And the log API returns the JSON value `{"run_id":1,"lines":[],"truncated":false}`

#### Scenario: A run that failed to start keeps its log and reports no progress
Given run `1` exists with `state` = `failed_infra`
And `s3://skill-builder-runs/runs/1/agent.log`'s first line is exactly `[skill-builder] runtime start failed: Error response from daemon: No such image`
And `s3://skill-builder-runs/runs/1/progress.json` does not exist
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/projects/7/runs/1` and `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/progress` and `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/log?tail=200` carrying that `sb_session` cookie
Then the run page responds with HTTP status 200 and contains the exact text `The runtime could not be started.`
And the run page has no element with id `run-progress` and does not contain the text `Waiting for the skill to report progress.`
And the progress response is HTTP 200 and its body equals the JSON value `{"run_id":1,"step":null,"state":"failed_infra","message":null,"percent":0,"updated_at":null}`
And the log response's `lines[0]` is exactly `[skill-builder] runtime start failed: Error response from daemon: No such image`
And the run page's element with id `run-log` contains the exact text `[skill-builder] runtime start failed: Error response from daemon: No such image`

#### Scenario: A credential value in the log is redacted before it is stored
Given run `1` exists with `state` = `running`
And the runtime emits the line `2026-11-15T10:01:02Z WARN using key sk-ant-test-5f2c8e1d`
And the `ai_model` credential's value is exactly `sk-ant-test-5f2c8e1d`
And the builder's redaction mask is exactly `[REDACTED]`
When the captured log is stored and served
Then `s3://skill-builder-runs/runs/1/agent.log` contains the line `2026-11-15T10:01:02Z WARN using key [REDACTED]` and no line containing `sk-ant-test-5f2c8e1d`
And `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/log?tail=200` returns `lines` containing exactly `2026-11-15T10:01:02Z WARN using key [REDACTED]` and no element containing `sk-ant-test-5f2c8e1d`
And the run page does not contain the text `sk-ant-test-5f2c8e1d`

#### Scenario: A truncated log is marked, not silently shortened
Given run `1` exists with `state` = `running`
And the runtime emitted `12582912` bytes of log output
And the builder's log capture limit is `10485760` bytes
When the builder flushes the captured log to `s3://skill-builder-runs/runs/1/agent.log`
Then the stored log's first line is exactly `[skill-builder] log truncated: showing the last 10485760 bytes of 12582912 bytes; 2097152 earlier bytes discarded.`
And `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/log?tail=200` returns a body whose `truncated` is `true` and whose `lines[0]` is exactly `[skill-builder] log truncated: showing the last 10485760 bytes of 12582912 bytes; 2097152 earlier bytes discarded.`
And the run page contains the exact text `[skill-builder] log truncated: showing the last 10485760 bytes of 12582912 bytes; 2097152 earlier bytes discarded.`
And `SELECT state FROM runs WHERE id = 1` still returns `running`

#### Scenario: A non-member cannot read a run's progress or logs
Given run `1` exists in project `7` with `state` = `running`
And Alan has no `project_members` row for project `7`
And Alan has a valid member session with local `users.id` = `44`
When Alan sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/progress` carrying that `sb_session` cookie
Then the builder responds with HTTP status 403
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And the response body contains no log line or progress message text

#### Scenario: A non-member cannot open the run page
Given run `1` exists in project `7` with `state` = `running`
And Alan has no `project_members` row for project `7`
And Alan has a valid member session with local `users.id` = `44`
When Alan sends `GET https://builder.skillbuilder.internal/projects/7/runs/1` carrying that `sb_session` cookie
Then the builder responds with HTTP status 403
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And the response body contains no log line or progress message text

#### Scenario: An unknown run id is not found
Given Ada is a member of project `7` with local `users.id` = `42`
And no `runs` row has `id` = `999`
When Ada sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/999/progress` carrying that `sb_session` cookie
Then the builder responds with HTTP status 404
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"run_not_found","message":"Run 999 does not exist."}}`

#### Scenario: A run from another project is not found through this path
Given run `1` exists in project `7` with `state` = `running`
And Grace is a member of project `7` with role `member` and owner of project `8`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `GET https://builder.skillbuilder.internal/api/projects/8/runs/1/progress` carrying that `sb_session` cookie
Then the builder responds with HTTP status 404
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"run_not_found","message":"Run 1 does not exist."}}`

### Covered requirements (traceability)
- FR-045
- FR-046

### Out of scope
Showing the final verdict, diff, Jira changes, token usage, cost or trace link (epics BSB-33 and
BSB-34). Verifying the run's output (epic BSB-29). Retention and purge of the stored log and
transcript (epic BSB-34, NFR-013 to NFR-018). Streaming the log into the page without any poll
(the page's client-side refresh may poll; the acceptance criteria fix the observable values, not
the transport). Accessibility of the progress and log regions (epic BSB-38, FR-130 to FR-137 and
NFR-012).

### Notes / dependencies
- Depends on BSB-26-PENDING-1 for a run in state `running` and on the installation-provisioned
  `skill-builder-runs` bucket (SK-001 §6, the same bucket BSB-25 writes bundles to). It depends on
  the agent image's existing `progress.json` output, which is part of the platform image contract.
  Which process writes `agent.log` — the builder's capture of the container's standard output and
  standard error, or an upload by the image — is still open (Open question 2 of this epic's
  review); this story asserts the stored object and the served lines, not the writer.
- The captured log passes through epic BSB-23's NFR-004 redaction before it is stored or served.
  Every occurrence of a known credential value is replaced with exactly `[REDACTED]`; the mask is
  this fixture's contract constant and epic BSB-23 owns the mechanism.
- The run page route and both APIs apply the same BSB-18 session and group gates and the BSB-22
  project-membership check as the run-start routes. A non-member gets the fixed BSB-22 403 body on
  both the page and the APIs. The two 404 bodies follow the preamble's fixed check order, so a
  path/run project mismatch is answered by `run_not_found`, not by disclosure of the other
  project's run.
- The log cap is a capture/display cap, not a retention policy: retention and purge belong to epic
  BSB-34. The truncation marker is the durable record that bytes were discarded.
- The page is server-rendered with a progress region with id `run-progress` and a log element with
  id `run-log`; BSB-33 extends that page with the full report and must keep these ids and texts.
  The progress region is absent once the run is terminal, while the log element keeps serving the
  stored log.
- Progress and log content are untrusted text from the skill; the page escapes it as text and the
  APIs return it as JSON strings. Rendering is not HTML.

---

## STORY: BSB-26-PENDING-3

**Summary:** Classify the run outcome with the platform engine's result rules
**Epic:** BSB-26 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-7, MVP

### Story
As a **skill author**, I want **the run outcome classified by the platform engine's result rules**, so that **a builder result means the same as a platform result and an unclassifiable exit is recorded as a failure instead of being mistaken for a pass**.

### Acceptance Criteria

#### Scenario: A completed result status is recorded as the claimed verdict
Given run `1` exists with `state` = `running`
And the agent container exits with status `0`
And `s3://skill-builder-runs/runs/1/bb_step_result.json` contains exactly `{"result_status":"completed","summary":"Triage finished."}`
When the executor reconciles the exit
Then within 2 seconds `SELECT state, claimed_verdict, final_verdict FROM runs WHERE id = 1` returns exactly `completed | completed | NULL`
And the run page contains the exact text `Outcome: completed`
And the run page has no element with id `run-progress`

#### Scenario: A BLOCK result is preserved rather than treated as a failure
Given run `1` exists with `state` = `running`
And the agent container exits with status `0`
And `bb_step_result.json` contains exactly `{"result_status":"BLOCK","summary":"Issue has no reproduction steps."}`
When the executor reconciles the exit
Then `SELECT state, claimed_verdict, final_verdict FROM runs WHERE id = 1` returns exactly `completed | BLOCK | NULL`

#### Scenario: A valid result takes precedence over a non-zero exit status
Given run `1` exists with `state` = `running`
And the agent container exits with status `2`
And `bb_step_result.json` contains exactly `{"result_status":"changes_requested","summary":"Reproduce first."}`
When the executor reconciles the exit
Then `SELECT state, claimed_verdict, final_verdict FROM runs WHERE id = 1` returns exactly `completed | changes_requested | NULL`
And the run page contains the exact text `Outcome: changes_requested`

#### Scenario: An exit with no uploaded result is recorded as failed_incomplete
Given run `1` exists with `state` = `running`
And the agent container exits with status `0`
And `s3://skill-builder-runs/runs/1/bb_step_result.json` does not exist
When the executor reconciles the exit
Then within 2 seconds `SELECT state, claimed_verdict, final_verdict FROM runs WHERE id = 1` returns exactly `failed_incomplete | NULL | NULL`
And the run page contains the exact text `The runtime exited without a classifiable result.`

#### Scenario: A non-zero exit with no result is recorded as failed_execution
Given run `1` exists with `state` = `running`
And the agent container exits with status `2`
And `bb_step_result.json` does not exist
When the executor reconciles the exit
Then `SELECT state, claimed_verdict, final_verdict FROM runs WHERE id = 1` returns exactly `failed_execution | NULL | NULL`
And the run page contains the exact text `The runtime exited with a non-zero status without a valid result.`

#### Scenario: A result status outside the allowed set is not accepted
Given run `1` exists with `state` = `running`
And run `1`'s workflow step declares `allowed_result_statuses` exactly `["completed","BLOCK","changes_requested","escalation_required"]`
And the agent container exits with status `0`
And `bb_step_result.json` contains exactly `{"result_status":"done","summary":"Finished."}`
When the executor reconciles the exit
Then `SELECT state, claimed_verdict, final_verdict FROM runs WHERE id = 1` returns exactly `failed_incomplete | NULL | NULL`
And the run page contains the exact text `The runtime exited without a classifiable result.`

#### Scenario: A run already terminated at its deadline is not overwritten
Given run `1` exists with `state` = `failed_timeout` and `claimed_verdict` = `NULL`
And the agent container labelled `bb.run_id` = `1` exits with status `137`
And `s3://skill-builder-runs/runs/1/bb_step_result.json` does not exist
When the executor reconciles the exit
Then within 2 seconds `SELECT state, claimed_verdict, final_verdict FROM runs WHERE id = 1` returns exactly `failed_timeout | NULL | NULL`

#### Scenario: A restarted executor reconciles a container that already exited
Given run `1` exists with `state` = `running`
And a container labelled `bb.run_id` = `1` exists, is not running, and exited with status `0`
And `s3://skill-builder-runs/runs/1/bb_step_result.json` contains exactly `{"result_status":"completed","summary":"Triage finished."}`
And a builder executor process starts with no in-memory record of run `1`
When the executor performs its startup reconciliation by the `bb.run_id` label
Then within 2 seconds `SELECT state, claimed_verdict, final_verdict FROM runs WHERE id = 1` returns exactly `completed | completed | NULL`
And the run page contains the exact text `Outcome: completed`

### Covered requirements (traceability)
- FR-047

### Out of scope
Starting the runtime, claiming the run and recording a start failure (BSB-26-PENDING-1).
Recording component and verifier versions, model profile and tier (BSB-26-PENDING-4). Verifying
the run's output and setting `final_verdict` or `verification` (epic BSB-29). Enforcing turn and
spend caps, the deadline and `failed_timeout` (epic BSB-27). Retrying or re-running a failed run
(epic BSB-27). Security scans before the run (epics BSB-31 and BSB-32).

### Notes / dependencies
- Depends on BSB-26-PENDING-1 for a started run in state `running`, and on the pinned step kit's
  outcome join (the same join the platform engine uses). The fixture statuses are the platform
  step kit's domain statuses; the allowed set comes from the selected workflow step's config on
  the skills commit. `bb_step_result.json` is read from the object at the key PENDING-1's
  `BB_RESULT_PUT_URL` points at (`runs/1/bb_step_result.json`). When the author omitted `context`,
  which workflow step supplies `allowed_result_statuses` is still open (Open question 1 of this
  epic's review); no scenario here classifies an omitted-context run.
- Every terminal write is a compare-and-set from `state = 'running'`; the first terminal write
  wins. A run already in a terminal state — for example `failed_timeout` written by epic BSB-27 —
  is left unchanged when its container later exits.
- An executor that starts after a restart finds in-flight runs by the `bb.run_id` container label
  and reconciles a container that has already exited, using the same compare-and-set.
- A valid uploaded result takes precedence over the process exit status. A skill that reports
  `BLOCK` and exits non-zero is a completed execution with claimed verdict `BLOCK`; the verdict is
  not a run failure. Failure classifications are reserved for exits with no valid allowed result.
- The run row is the durable record: `state` records the engine classification and
  `claimed_verdict` records the agent's claimed verdict only when one is valid. `final_verdict` and
  `verification` stay `NULL` here because verification is epic BSB-29's job.
- `failed_timeout` is never set by this story; epic BSB-27 sets it when the installation deadline
  is exceeded. This story only asserts that a run already in that state is not overwritten and
  that a restarted executor does not misclassify a container BSB-27 stopped.
- The page texts asserted here are the failure-reason text this epic owns; epic BSB-33 extends the
  same page with the full report.

---

## STORY: BSB-26-PENDING-4

**Summary:** Record the run's exact execution provenance
**Epic:** BSB-26 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-7, MVP

### Story
As a **skill author**, I want **each run to record the exact execution components, verifier version, model profile and model tier it used**, so that **I can reproduce and compare the result later instead of guessing which versions produced it**.

### Acceptance Criteria

#### Scenario: A successful run records the exact components, verifier and model
Given run `1` exists prepared and `state` = `queued` as in the contract
And `skill-builder/kit.txt` contains `kit-v7`
And the `kit.json` for `kit-v7` has step kit `0.4.0`, verifier `2.1.2` and the agent image digest `sha256:4d2a6f8c0e1b3a5d7f9c2e4a6b8d0f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d`
And run `1` uses model profile `3` and tier `high`
When the executor claims run `1` and the container starts
Then `SELECT agent_image_digest, stepkit_version, verify_version FROM runs WHERE id = 1` returns exactly `sha256:4d2a6f8c0e1b3a5d7f9c2e4a6b8d0f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d | 0.4.0 | 2.1.2`
And `SELECT model_profile_id, tier FROM runs WHERE id = 1` returns exactly `3 | high`
And the container's environment contains `BB_MODEL` = `test-model-high`
And while the container is still running, `SELECT stepkit_version FROM runs WHERE id = 1` returns `0.4.0`

#### Scenario: The recorded versions come from the pinned kit, not from constants
Given run `2` exists prepared and `state` = `queued` as in the contract
And `skill-builder/kit.txt` contains `kit-v8`
And the `kit.json` for `kit-v8` has step kit `0.5.0`, verifier `2.2.0` and the agent image digest `sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13`
And run `2` uses model profile `3` and tier `high`
When the executor claims run `2` and the container starts
Then `SELECT agent_image_digest, stepkit_version, verify_version, model_profile_id, tier FROM runs WHERE id = 2` returns exactly `sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13 | 0.5.0 | 2.2.0 | 3 | high`
And the container's label `bb.stepkit` is exactly `0.5.0`
And the container's environment contains `BB_MODEL` = `test-model-high`

#### Scenario: A run that fails to start still records its provenance
Given run `1` exists prepared and `state` = `queued` as in the contract
And `skill-builder/kit.txt` contains `kit-v7`
And the runtime adapter is configured so that starting the pinned agent image fails with exactly `Error response from daemon: No such image`
When the executor claims run `1`
Then `SELECT state, agent_image_digest, stepkit_version, verify_version, model_profile_id, tier FROM runs WHERE id = 1` returns exactly `failed_infra | sha256:4d2a6f8c0e1b3a5d7f9c2e4a6b8d0f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d | 0.4.0 | 2.1.2 | 3 | high`

#### Scenario: Later kit pin changes do not rewrite a completed run
Given run `1` has the provenance recorded by the first scenario and its execution has finished
And run `2` exists prepared and `state` = `queued` as in the contract
And `skill-builder/kit.txt` is later changed to contain `kit-v8`
When the executor claims run `2` under `kit-v8`
Then `SELECT agent_image_digest, stepkit_version, verify_version FROM runs WHERE id = 1` still returns exactly `sha256:4d2a6f8c0e1b3a5d7f9c2e4a6b8d0f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d | 0.4.0 | 2.1.2`
And `SELECT agent_image_digest, stepkit_version, verify_version FROM runs WHERE id = 2` returns exactly `sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13 | 0.5.0 | 2.2.0`

### Covered requirements (traceability)
- FR-048
- FR-049
- FR-151
- FR-152

### Out of scope
Choosing the model profile or tier at run start (epic BSB-24, FR-149 and FR-150). Storing or
displaying integration credentials (epic BSB-23, FR-032 and FR-036). Running verification and
setting `final_verdict` or `verification` (epic BSB-29). Displaying the provenance in the full run
report (epic BSB-33, FR-157). Token usage and cost (epic BSB-34). Security-scan component
versions (epics BSB-31 and BSB-32).

### Notes / dependencies
- Depends on BSB-26-PENDING-1 for the executor and the claim step, on epic BSB-24 for the recorded
  `model_profile_id` and `tier`, and on epic BSB-23 for the `ai_model` profile mapping that turns
  profile `3`/tier `high` into `test-model-high`. Epic BSB-24 writes `model_profile_id` and `tier`
  at run start; this story owns the guarantee that those are the values the runtime uses (the
  resolved `BB_MODEL`) and that they survive execution, including a start failure.
- The three execution components persisted on the run are the agent image digest and the step kit
  version (FR-048) and the verifier version (FR-151). The scanner image is a scan-time component,
  not a run-time one, and is out of scope here. The model profile and tier are stored as
  `model_profile_id` and `tier` (FR-049, FR-152) and the resolved model name is passed to the
  runtime as `BB_MODEL`.
- The values are read from `kit.txt`/`kit.json` at claim time and written to the run row before
  the container is created, so a start failure still leaves the provenance recorded. They are not
  re-read later; a later kit pin change cannot rewrite a past run.
- Epic BSB-29 must verify with the `verify_version` recorded on the run, not with whatever
  `kit.txt` contains at verification time.
- Only the model is resolved here: `BB_MODEL` is this story's environment value. The `github` and
  `jira` integrations, `BB_MCP_CONFIG`, `BB_REPO_URL`, `BB_BASE_BRANCH` and the presigned PUT URLs
  are BSB-26-PENDING-1's environment values.
