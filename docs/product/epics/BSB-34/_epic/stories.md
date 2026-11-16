# Stories — BSB-34 (Run usage, trace & data retention)

Epic BSB-34 covers FR-159, FR-160, NFR-011, NFR-013, NFR-014, NFR-015, NFR-016, NFR-017 and
NFR-018. It is decomposed into 5 vertical slices below, and coverage of all 9 requirements is
verified.

The five slices account for what one run consumes, what trace it produces and how long its data
survives: the usage record the builder writes when execution ends (PENDING-1), the token usage
and cost an author reads on the run report (PENDING-2), the test-environment trace and the run's
trace identifier (PENDING-3), the installation retention period and its sweep (PENDING-4), and
the project-owner-requested purge of one run's data (PENDING-5).

The usage figures and the trace identifier are durable records on the run. The report is a
projection: PENDING-2 renders the recorded `runs.token_usage` and `runs.cost_usd` values and never
recomputes them from token counts or current model prices. Retention and purge act only on the
objects under `runs/<run-id>/` in the builder's object store; they never delete the `runs` row or
the verification record that keeps the run explainable.

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than a Jira issue: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404
"Issue does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The
Atlassian MCP tools were not exposed in this session, so the configured site was queried read-only
through its REST API. The epic being decomposed is BSB-34, read read-only from the same site:
summary "Run usage, trace & data retention", type Epic, status To Do, labels FA-13/MVP, and a
description matching the BSB-34 section of `epics.md`. No existing Jira issue is parented to
BSB-34, and no Jira write was attempted.

**Cross-epic prerequisites and hand-offs (not requirements of these stories).** PENDING-1 consumes
the terminal execution telemetry object `runs/<run-id>/usage.json`. That object is produced by the
execution path, and BSB-26-PENDING-1 owns the runtime adapter and launch contract but its
acceptance criteria do not name a usage report; BSB-26 must publish this object (or hand the same
record to the builder) or PENDING-1 has no producer. PENDING-3 writes to the external trace store
and records the run's trace identifier, which BSB-33-PENDING-5 reads to render the trace link; this
supplies the BSB-34 side of BSB-33's review Finding 7 / Open question 6. PENDING-4's sweep and
PENDING-5's purge operate on run artifacts written by BSB-26 (logs, progress, step result) and
BSB-33 (the captured diff); ADR SK-001 section 6 names the agent transcript under
`runs/<run-id>/`, but no BSB-26 story currently writes `runs/<run-id>/transcript.json`, so the
execution path must also write that artifact. BSB-25-PENDING-1's out-of-scope names "bundle
retention and purge (BSB-34)"; this epic's requirements cover run transcripts, logs and results
only, so content-addressed `skill_bundles` objects are not deleted by PENDING-4 or PENDING-5 and
BSB-25's note needs reconciling. After either operation deletes an object, a report section that
rendered it (BSB-33's captured diff, BSB-26's log tail) must fall back to its existing unavailable
state; neither sibling story currently defines a "data expired" state, so their reviewers must
confirm that fallback.

A single requirement is claimed by exactly one story:

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-159 — the run page shows the run's token usage | BSB-34-PENDING-2 | "The recorded token usage and cost are shown"; "A run with no recorded usage shows not recorded"; "A run that recorded zero usage shows zero, not not-recorded" |
| FR-160 — the run page shows the run's cost | BSB-34-PENDING-2 | "The recorded token usage and cost are shown"; "A run with no recorded usage shows not recorded"; "A run that recorded zero usage shows zero, not not-recorded" |
| NFR-011 — when tracing is enabled, a run's trace identifies it as a test-environment run | BSB-34-PENDING-3 | "A run with tracing enabled records a test-environment trace"; "Every run uses the installation's environment identity"; "Tracing disabled records no trace"; "A trace store failure does not fail the run" |
| NFR-013 — run transcripts, logs and results are retained only for a configured period | BSB-34-PENDING-4 | "The default retention period is three months"; "A configured retention period overrides the default"; "Only run artifacts expire, not the run or its shared bundle"; "A sweep that cannot delete one run's artifacts continues without deleting its record"; "A later sweep completes after the object store recovers"; "An invalid retention period is refused" |
| NFR-014 — run transcripts, logs and results can be purged on request | BSB-34-PENDING-5 | "The project owner purges a run's data"; "A non-owner project member cannot purge"; "A run from another project is not disclosed"; "A repeated purge is idempotent"; "A failed purge is reported"; "A failed purge can be retried successfully" |
| NFR-015 — each run records its cost | BSB-34-PENDING-1 | "A completed run records its token usage, cost and turn count"; "A run with no telemetry leaves the usage unrecorded"; "An invalid usage record is not partially stored" |
| NFR-016 — each run records its token usage | BSB-34-PENDING-1 | "A completed run records its token usage, cost and turn count"; "A run that made no model calls records zero usage"; "An invalid usage record is not partially stored" |
| NFR-017 — each run records its turn count | BSB-34-PENDING-1 | "A completed run records its token usage, cost and turn count"; "A run that made no model calls records zero usage"; "A run with no telemetry leaves the usage unrecorded" |
| NFR-018 — the default retention period is three months | BSB-34-PENDING-4 | "The default retention period is three months" |

> New stories use draft keys in the `BSB-34-PENDING` series (`-1` to `-5`). `sdlc-tracker-sync`
> creates each story in Jira, parents it to BSB-34, and replaces the draft key with the real key in
> `story-map.json`.

---

## STORY: BSB-34-PENDING-1

**Title:** Record the run's token usage, cost and turn count when it finishes
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **the builder to record my run's token usage, cost and turn count on the run record from its terminal execution telemetry**, so that **what the run consumed and cost is durable evidence I can inspect later instead of reconstructing it from logs**.

### Acceptance Criteria

Scenario: A completed run records its token usage, cost and turn count
Given a "runs" row id 21 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store holding "runs/21/usage.json" with content {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "turn_count": 7, "cost_usd": 0.018473, "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "cost_usd": 0.018473}]}
When the builder records run 21's usage after execution reaches a terminal state
Then the "runs" row id 21 has token_usage {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "total_tokens": 18190, "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "cost_usd": 0.018473}]}, cost_usd 0.018473 and turn_count 7, and the row's state remains "completed" and result_status "completed"

Scenario: A run that made no model calls records zero usage
Given a "runs" row id 22 with project_id 7, user_id 42, skill "sdlc-lint-only", state "completed", result_status "completed", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store holding "runs/22/usage.json" with content {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0, "turn_count": 0, "cost_usd": 0.0, "models": []}
When the builder records run 22's usage after execution reaches a terminal state
Then the "runs" row id 22 has token_usage {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0, "total_tokens": 0, "models": []}, cost_usd 0.0 and turn_count 0, and the row's state remains "completed"

Scenario: A run with no telemetry leaves the usage unrecorded
Given a "runs" row id 23 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "failed", result_status "failed_infra", execution_error "The agent container could not be started.", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store that holds no "runs/23/usage.json"
When the builder attempts to record run 23's usage
Then the "runs" row id 23 still has token_usage NULL, cost_usd NULL and turn_count NULL, its state remains "failed", its result_status remains "failed_infra", and its execution_error remains "The agent container could not be started."

Scenario: An invalid usage record is not partially stored
Given a "runs" row id 24 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store holding "runs/24/usage.json" with content {"input_tokens": -1, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "turn_count": 7, "cost_usd": 0.018473, "models": []}
When the builder attempts to record run 24's usage
Then the "runs" row id 24 still has token_usage NULL, cost_usd NULL and turn_count NULL, the row's state remains "completed", and the builder's own log contains "The run's usage record is invalid." and no token or cost value from that object

Scenario: A credential value in the telemetry is not stored
Given a "runs" row id 21 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, an "integrations" row id 5 for project 7 with kind "ai_model" and secret_ref "skill-builder/7/integration-5", a secret store holding "sk-ant-test-3c9e" at "skill-builder/7/integration-5", and a builder object store holding "runs/21/usage.json" with content {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "turn_count": 7, "cost_usd": 0.018473, "api_key": "sk-ant-test-3c9e", "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": 0.018473, "api_key": "sk-ant-test-3c9e"}]}
When the builder records run 21's usage after execution reaches a terminal state
Then the "runs" row id 21 has token_usage {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "total_tokens": 15630, "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": 0.018473}]}, and neither the "runs" row nor the builder's own log contains "sk-ant-test-3c9e"

### Covered requirements (traceability)
- NFR-015
- NFR-016
- NFR-017

### Out of scope
Showing token usage or cost on the run report (BSB-34-PENDING-2); the test-environment trace and
`runs.trace_id` (BSB-34-PENDING-3); retention and purge (BSB-34-PENDING-4 and BSB-34-PENDING-5);
the live progress counter and the log tail while a run executes (BSB-26-PENDING-2); executing the
run and classifying its outcome (BSB-26-PENDING-3); recording the model profile, tier and concrete
model (BSB-26-PENDING-4); turn and spend caps and the deadline (BSB-27); displaying the recorded
turn count on the report (BSB-33-PENDING-5); verification and verdicts (BSB-29); computing prices
or estimating cost from a pricing table.

### Notes / dependencies
Depends on the execution path for the terminal telemetry object `runs/<run-id>/usage.json`. That
object is written during execution; BSB-26-PENDING-1 owns the runtime adapter and launch contract,
but BSB-26's stories do not name a usage report, so BSB-26 must publish this object (or pass the
same record to the builder) as a cross-epic hand-off. This story owns only the recording of its
documented fields into the run record.

The telemetry contract is a JSON object with non-negative integers `input_tokens`, `output_tokens`,
`cache_read_tokens`, `cache_write_tokens` and `turn_count`, a non-negative number `cost_usd`, and
a `models` array whose entries carry `model` and the same token and cost fields for that model.
The builder computes `total_tokens` as the sum of the four token counts; it does not trust a
telemetry-supplied total. A record is accepted only when every required field is present and
valid; otherwise all three columns stay NULL and the record is not partially written. No cost is
recomputed from token counts or a price table: `runs.cost_usd` is the telemetry's cost.

ADR SK-001 section 9 already lists `runs.cost_usd`; this story adds `runs.token_usage` JSONB and
`runs.turn_count` integer, and the data-model stage must record them. BSB-33-PENDING-5 reads
`runs.turn_count`; this story is its producer. ADR section 9 does not list `token_usage` or
`turn_count`.

The recorded turn count is the terminal execution total, not the agent's live progress counter
BSB-26-PENDING-2 renders as "Turns: 3 of 12"; BSB-27 enforces the turn and spend caps from the
live telemetry path and owns no column here. Credential values never enter the usage record: the
builder stores only the documented fields, so an extra field such as `api_key` is dropped. NFR-004
is mapped to BSB-23-PENDING-5, whose shared redaction rule this story applies without claiming that
requirement; NFR-004 is not in this epic's requirement set.

---

## STORY: BSB-34-PENDING-2

**Title:** See the run's recorded token usage and cost on its report
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **the run report to show the token usage and cost recorded for the run**, so that **I can see what the run consumed and cost without opening telemetry files or estimating it from logs**.

### Acceptance Criteria

Scenario: The recorded token usage and cost are shown
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), and a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", token_usage {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "total_tokens": 18190, "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "cost_usd": 0.018473}]} and cost_usd 0.018473
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Tokens: 12,450 input, 3,180 output, 2,048 cache read, 512 cache write (18,190 total)" and "Cost: $0.018473", and the body contains no exception text or stack trace

Scenario: A run with no recorded usage shows not recorded
Given the same signed-in Ada and project 7, and a "runs" row id 22 with project_id 7, skill "sdlc-fix-bug-reproduce", state "failed", result_status "failed_infra", token_usage NULL and cost_usd NULL
When Ada opens GET "/projects/7/runs/22"
Then the response is HTTP 200 rendering "Tokens: not recorded" and "Cost: not recorded", and the body renders neither "Tokens: 0" nor "Cost: $0.000000"

Scenario: A run that recorded zero usage shows zero, not not-recorded
Given the same signed-in Ada and project 7, and a "runs" row id 23 with project_id 7, skill "sdlc-lint-only", state "completed", result_status "completed", token_usage {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0, "total_tokens": 0, "models": []} and cost_usd 0.0
When Ada opens GET "/projects/7/runs/23"
Then the response is HTTP 200 rendering "Tokens: 0 input, 0 output, 0 cache read, 0 cache write (0 total)" and "Cost: $0.000000", and the body does not render "not recorded"

Scenario: A non-member cannot see a run's usage or cost
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), and the "runs" row id 21 of the first scenario
When Carol opens GET "/projects/7/runs/21"
Then the response is HTTP 403 with the message "You are not a member of this project.", and the body contains neither "12,450" nor "0.018473"

### Covered requirements (traceability)
- FR-159
- FR-160

### Out of scope
Recording the usage, cost and turn count (BSB-34-PENDING-1); the trace and its identifier
(BSB-34-PENDING-3); retention and purge (BSB-34-PENDING-4 and BSB-34-PENDING-5); the report's
identity, verdict, check, diff, Jira, turn and trace sections (BSB-33-PENDING-1 to -5); the
security tab and scan reports (BSB-31 and BSB-32); recomputing cost from token counts or changing
model prices; a spend dashboard, trend view or per-project usage aggregation.

### Notes / dependencies
Depends on BSB-22-PENDING-3 for the shared project-membership check, on BSB-26-PENDING-3 for the
run reaching a terminal state, and on BSB-34-PENDING-1 for `runs.token_usage` and `runs.cost_usd`.
The page is the run report BSB-33-PENDING-1 already serves at GET "/projects/7/runs/21"; this
story adds a read-only "Usage and cost" section to that page and does not change its routing,
authentication or other sections.

The section renders the recorded values only. `total_tokens` is the sum recorded by
BSB-34-PENDING-1; the display formats token counts with thousands separators and cost with exactly
six decimal places after "$" (the scale of `runs.cost_usd`). A NULL `token_usage` or NULL
`cost_usd` is the single not-recorded state and renders "not recorded", never zero, so a run whose
telemetry was absent cannot be mistaken for a free run. A recorded all-zero object is the distinct
zero state. The section reads no telemetry file and never derives cost from the model profile or a
price table, so a later price change cannot rewrite past evidence.

---

## STORY: BSB-34-PENDING-3

**Title:** Mark every run's trace as a test-environment trace and record its identifier
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-13, MVP

### Story
As a **platform administrator**, I want **every trace created for a run to carry the installation's test-environment identity and to be linked to its run**, so that **skill-test traces are never confused with production traffic and any trace can be traced back to the run that produced it**.

### Acceptance Criteria

Scenario: A run with tracing enabled records a test-environment trace
Given a "runs" row id 21 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "prepared", trace_id NULL and kind "run", installation tracing configuration {"enabled": true, "environment": "skilltest", "url_template": "https://langfuse.test/traces/{trace_id}"}, and a stub trace store that assigns id "trace-4f2c9a1b7d3e" to the first trace it receives
When the builder launches run 21
Then the configured trace store holds exactly one trace with id "trace-4f2c9a1b7d3e", env "skilltest" and metadata {"run_id": 21, "project_id": 7}, and the "runs" row id 21 has trace_id "trace-4f2c9a1b7d3e"

Scenario: Every run uses the installation's environment identity
Given installation tracing configuration {"enabled": true, "environment": "skilltest", "url_template": "https://langfuse.test/traces/{trace_id}"}, a "runs" row id 21 with project_id 7, state "prepared" and trace_id NULL, a "runs" row id 31 with project_id 8, state "prepared" and trace_id NULL, and a stub trace store that assigns id "trace-4f2c9a1b7d3e" to its first trace and id "trace-8a1b2c3d4e5f" to its second trace
When the builder launches run 21 and then run 31
Then the trace store holds two traces, each with env "skilltest", the "runs" row id 21 has trace_id "trace-4f2c9a1b7d3e", and the "runs" row id 31 has trace_id "trace-8a1b2c3d4e5f"

Scenario: Tracing disabled records no trace
Given a "runs" row id 21 with project_id 7, state "prepared" and trace_id NULL, installation tracing configuration {"enabled": false, "environment": "skilltest", "url_template": "https://langfuse.test/traces/{trace_id}"}, and a stub trace store whose creation counter is 0
When the builder launches run 21
Then the trace store's creation counter remains 0, the "runs" row id 21 has trace_id NULL, and run 21 proceeds to state "running" with execution_error NULL

Scenario: A trace store failure does not fail the run
Given a "runs" row id 21 with project_id 7, state "prepared" and trace_id NULL, installation tracing configuration {"enabled": true, "environment": "skilltest", "url_template": "https://langfuse.test/traces/{trace_id}"}, and a stub trace store that returns HTTP 503 "Service Unavailable" for trace creation
When the builder launches run 21
Then the trace store's creation counter is 1, the "runs" row id 21 has trace_id NULL, and run 21 proceeds to state "running" with execution_error NULL and is not refused or failed by the trace-store error

### Covered requirements (traceability)
- NFR-011

### Out of scope
Rendering the "Open trace" link and the disabled/unavailable states on the report
(BSB-33-PENDING-5); the trace's spans, prompts, outputs and LLM-call detail; choosing or operating
the trace store (external); the trace store's own retention and purge; recording token usage, cost
and turn count (BSB-34-PENDING-1); retention and purge of run artifacts (BSB-34-PENDING-4 and
BSB-34-PENDING-5); changing the platform's trace format.

### Notes / dependencies
Depends on BSB-26-PENDING-1 for the run launch path and the runtime adapter. The builder registers
exactly one trace for a prepared run and then launches it, so the trace exists before the agent
makes its first model call; the launch path must call this hook and pass the trace identifier to
the runtime adapter as a cross-epic hand-off, because BSB-26-PENDING-1's acceptance criteria do not
name tracing. The external trace store is a dependency of the epic, not a component this story
builds; a stub trace store stands in for it in tests.

The installation tracing configuration has three operator-managed fields: `enabled` (boolean),
`environment` (the installation's trace environment identity, "skilltest" for a skill-test
deployment) and `url_template` (the trace-store URL template with `{trace_id}`). The marker is the
installation's environment identity, never a per-run author choice, so every run of the installation
is marked the same way. A deployment that turns tracing off creates no trace and records no
identifier; turning it on never changes a run's outcome. A trace store that is unavailable leaves
`runs.trace_id` NULL and the run continues: tracing is non-gating, and BSB-33-PENDING-5 already
renders "Trace unavailable." for the enabled-with-no-identifier state.

ADR SK-001 section 9 lists no `runs.trace_id`; this story adds it and the data-model stage must
record it. BSB-33-PENDING-5 reads `runs.trace_id` and the installation `url_template` to render
"Open trace" and this story is their producer, which resolves the BSB-34 side of that story's
one-sided dependency (BSB-33's review Finding 7 / Open question 6). FR-103 (the report's trace
link) remains BSB-33's requirement and is not claimed here; this story covers NFR-011 only.

---

## STORY: BSB-34-PENDING-4

**Title:** Expire run transcripts, logs and results after the installation retention period
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **platform administrator**, I want **the builder to delete each run's transcript, logs and results once the installation's retention period has elapsed (three months by default) while keeping the run's audit-critical metadata**, so that **test data is not retained indefinitely and the run record remains explainable after its artifacts expire**.

### Acceptance Criteria

Scenario: The default retention period is three months
Given installation retention configuration with retention_months unset, a "runs" row id 21 with state "completed", final_verdict "pass", cost_usd 0.018473 and finished_at "2026-08-16T03:00:00Z", a builder object store holding "runs/21/agent.log", "runs/21/transcript.json", "runs/21/bb_step_result.json", "runs/21/diff.json" and "runs/21/usage.json", and a builder clock reading "2026-11-16T03:00:00Z"
When the retention sweep runs
Then the effective retention period is 3 months, no object exists under "runs/21/", and the "runs" row id 21 remains with state "completed", final_verdict "pass", cost_usd 0.018473 and finished_at "2026-08-16T03:00:00Z"

Scenario: A configured retention period overrides the default
Given installation retention configuration with retention_months 6, a "runs" row id 21 with state "completed" and finished_at "2026-05-01T00:00:00Z", a "runs" row id 22 with state "completed" and finished_at "2026-06-01T00:00:00Z", a builder object store holding "runs/21/agent.log" and "runs/21/transcript.json" for run 21 and "runs/22/agent.log", "runs/22/transcript.json" and "runs/22/bb_step_result.json" for run 22, and a builder clock reading "2026-11-16T03:00:00Z"
When the retention sweep runs
Then no object exists under "runs/21/", the objects "runs/22/agent.log", "runs/22/transcript.json" and "runs/22/bb_step_result.json" still exist, and the "runs" rows id 21 and id 22 both remain

Scenario: Only run artifacts expire, not the run or its shared bundle
Given installation retention configuration with retention_months 3, a "runs" row id 21 with state "completed", final_verdict "pass" and finished_at "2026-05-01T00:00:00Z", a "skill_bundles" row for skill "sdlc-fix-bug-reproduce" and skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" with s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", a builder object store holding "runs/21/agent.log" and that bundle object, and a builder clock reading "2026-11-16T03:00:00Z"
When the retention sweep runs
Then no object exists at "runs/21/agent.log", the object "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz" still exists, and the "runs" row id 21 and the "skill_bundles" row still exist

Scenario: A sweep that cannot delete one run's artifacts continues without deleting its record
Given installation retention configuration with retention_months 3, a "runs" row id 21 with state "completed" and finished_at "2026-05-01T00:00:00Z", a "runs" row id 22 with state "completed" and finished_at "2026-05-02T00:00:00Z", a builder object store holding "runs/21/agent.log", "runs/21/transcript.json", "runs/22/agent.log" and "runs/22/bb_step_result.json" and returning HTTP 503 "Service Unavailable" for every delete under "runs/21/" while accepting deletes under "runs/22/", and a builder clock reading "2026-11-16T03:00:00Z"
When the retention sweep runs
Then no object exists under "runs/22/", the objects "runs/21/agent.log" and "runs/21/transcript.json" still exist, and the "runs" rows id 21 and id 22 both remain

Scenario: A later sweep completes after the object store recovers
Given the failed sweep of the previous scenario at "2026-11-16T03:00:00Z", and a builder object store that now accepts deletes under "runs/21/" and a builder clock reading "2026-11-17T03:00:00Z"
When the retention sweep runs again
Then no object exists under "runs/21/" and the "runs" row id 21 still remains with state "completed"

Scenario: An invalid retention period is refused
Given installation retention configuration with retention_months 0
When the builder starts
Then it refuses to start with the message "The retention period must be at least one month." and no retention sweep runs

### Covered requirements (traceability)
- NFR-013
- NFR-018

### Out of scope
Purging one run's data on request (BSB-34-PENDING-5); recording usage and cost
(BSB-34-PENDING-1); the trace store's own retention and purge (external); deleting the `runs`
row, its verification record, its verdicts, its usage values or any other database metadata;
deleting content-addressed `skill_bundles` objects; deleting another project's data; operator
settings UI; backup or archival copies outside the builder's object store.

### Notes / dependencies
Depends on BSB-26-PENDING-3 for `runs.finished_at` and the terminal run state, on BSB-26-PENDING-2
for `runs/<run-id>/agent.log` and `runs/<run-id>/progress.json`, on BSB-26-PENDING-3 for
`runs/<run-id>/bb_step_result.json`, and on BSB-33-PENDING-3 for the captured
`runs/<run-id>/diff.json` it renders. ADR SK-001 section 6 names the agent transcript under
`runs/<run-id>/`; no BSB-26 story currently writes `runs/<run-id>/transcript.json`, so the
execution path must write it as a cross-epic hand-off or the transcript has no producer.

The retention period is an installation setting in whole months (`retention_months`, default 3,
minimum 1) managed by the operator; an author cannot set it per run. A run's artifacts expire at
the same UTC day-of-month and time `retention_months` months after `runs.finished_at`, so a run
finished at "2026-08-16T03:00:00Z" expires at "2026-11-16T03:00:00Z". An invalid setting (zero or
negative) is refused at startup rather than silently disabling retention, because retaining run
data indefinitely would violate NFR-013. A run with neither `finished_at` nor `started_at` has no
run artifacts and is skipped by the sweep.

The sweep deletes every object under `runs/<run-id>/`: the agent transcript, `agent.log`,
`progress.json`, `bb_step_result.json`, the captured `diff.json` and the terminal `usage.json`. It
never deletes the `runs` row or its verdict, verification or usage columns, so the run remains
explainable after its evidence is gone. `skill_bundles` objects are keyed by
`(skill, skills_commit_sha)` and shared by every run at that commit; they are not run-scoped and
are not deleted here. BSB-25-PENDING-1's out-of-scope names "bundle retention and purge (BSB-34)",
which this story does not implement; that note needs reconciling with BSB-34's epic scope, which
covers run transcripts, logs and results only. The sweep acts only on the builder's object store
and never renders or rewrites a credential value; NFR-004 remains BSB-23-PENDING-5's requirement.

---

## STORY: BSB-34-PENDING-5

**Title:** Purge a run's transcripts, logs and results on request
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **project owner**, I want **to purge one run's transcripts, logs and results on request, with the deletion recorded on the run**, so that **I can remove test data before its retention period ends and show that the deletion was authorized and completed**.

### Acceptance Criteria

Scenario: The project owner purges a run's data
Given a signed-in project owner Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass", purged_at NULL, purged_by NULL and purge_error NULL, a builder object store holding "runs/21/agent.log", "runs/21/transcript.json", "runs/21/bb_step_result.json", "runs/21/diff.json" and "runs/21/usage.json", and a builder clock reading "2026-11-16T11:10:00Z"
When Ada sends POST "/projects/7/runs/21/purge"
Then the response is HTTP 200 with body {"status": "purged", "objects_deleted": 5}, no object exists under "runs/21/", and the "runs" row id 21 remains with state "completed", final_verdict "pass", purged_at "2026-11-16T11:10:00Z", purged_by 42 and purge_error NULL

Scenario: A non-owner project member cannot purge
Given a signed-in skill author Carol whose local "users" id is 44 and who has a "project_members" row (project_id 7, user_id 44, role "member") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, state "completed", purged_at NULL, purged_by NULL and purge_error NULL, and a builder object store holding "runs/21/agent.log" and "runs/21/bb_step_result.json"
When Carol sends POST "/projects/7/runs/21/purge"
Then the response is HTTP 403 with the message "Only the project owner can purge run data.", the objects "runs/21/agent.log" and "runs/21/bb_step_result.json" still exist, and the "runs" row id 21 still has purged_at NULL, purged_by NULL and purge_error NULL

Scenario: A run from another project is not disclosed
Given the same signed-in Ada with her "project_members" row (project_id 7, user_id 42, role "owner"), a "runs" row id 31 with project_id 8, state "completed", purged_at NULL, purged_by NULL and purge_error NULL, a builder object store holding "runs/31/agent.log", and an object-store delete counter for run 31 that is 0
When Ada sends POST "/projects/7/runs/31/purge"
Then the response is HTTP 404 with the message "Run not found.", the object "runs/31/agent.log" still exists, the object-store delete counter for run 31 remains 0, and the "runs" row id 31 still has purged_at NULL

Scenario: A repeated purge is idempotent
Given the same signed-in Ada with her "project_members" row for project 7, a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass", purged_at "2026-11-15T09:00:00Z", purged_by 42 and purge_error NULL, and a builder object store with no object under "runs/21/"
When Ada sends POST "/projects/7/runs/21/purge"
Then the response is HTTP 200 with body {"status": "already purged", "objects_deleted": 0}, and the "runs" row id 21 still has purged_at "2026-11-15T09:00:00Z" and purged_by 42

Scenario: A failed purge is reported
Given the same signed-in Ada with her "project_members" row for project 7, a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass", purged_at NULL, purged_by NULL and purge_error NULL, a builder object store holding "runs/21/agent.log" and "runs/21/bb_step_result.json" and returning HTTP 503 "Service Unavailable" for every delete under "runs/21/", and a builder clock reading "2026-11-16T11:10:00Z"
When Ada sends POST "/projects/7/runs/21/purge"
Then the response is HTTP 503 with the message "The run's data could not be purged. Retry later.", the "runs" row id 21 still has purged_at NULL and purged_by NULL with purge_error "The run's data could not be purged.", and the run's state remains "completed" with final_verdict "pass"

Scenario: A failed purge can be retried successfully
Given the failed purge of the previous scenario and a builder object store that now accepts deletes under "runs/21/" with "runs/21/agent.log" and "runs/21/bb_step_result.json" still present, and a builder clock reading "2026-11-16T11:20:00Z"
When Ada sends POST "/projects/7/runs/21/purge" again
Then the response is HTTP 200 with body {"status": "purged", "objects_deleted": 2}, no object exists under "runs/21/", and the "runs" row id 21 has purged_at "2026-11-16T11:20:00Z", purged_by 42 and purge_error NULL

### Covered requirements (traceability)
- NFR-014

### Out of scope
The scheduled retention sweep and the installation retention setting (BSB-34-PENDING-4);
recording usage and cost (BSB-34-PENDING-1); purging traces from the external trace store;
deleting the `runs` row, its verification record, its verdicts or its usage values; deleting
content-addressed `skill_bundles` objects; purging another project's data; deleting a whole
project or its builds; the run page's display and layout (BSB-33-PENDING-1); the command line
(BSB-37).

### Notes / dependencies
Depends on BSB-18 for the authenticated session and the skill-builders gate, on BSB-22-PENDING-3
for the shared project-membership check, on BSB-26-PENDING-2 and BSB-26-PENDING-3 for
`runs/<run-id>/agent.log`, `runs/<run-id>/progress.json` and `runs/<run-id>/bb_step_result.json`,
and on BSB-33-PENDING-3 and BSB-34-PENDING-1 for the captured `runs/<run-id>/diff.json` and
`runs/<run-id>/usage.json`. The operation is POST "/projects/7/runs/21/purge" on the builder's
authenticated surface; it resolves the run's project and checks the project-owner role before any
object is read or deleted, and it never discloses a run from another project.

The PRD says run data "can be purged on request" without naming the authorizing role. This story
requires the project's owner role, consistent with the test-project owner's role as the project's
administrator; a project member who is not the owner is denied. Purging is idempotent: a run whose
`purged_at` is already set returns "already purged" and changes nothing. The deletion covers every
object under `runs/<run-id>/` — the transcript, logs, step result, captured diff and usage record —
and never the `runs` row or its audit columns, so the purge remains explainable. A partial failure
is reported as HTTP 503, recorded in `runs.purge_error`, and retried by sending the request again;
a retry deletes whatever remains and then sets `purged_at` and `purged_by`.

The data-model stage must add nullable `runs.purged_at` timestamptz, `runs.purged_by` integer
(the purging user's id) and `runs.purge_error` text; ADR SK-001 section 9 lists none of them.
`purged_at` and `purged_by` are the auditable result the epic requires, and they are never cleared
by a later purge attempt; `purge_error` is cleared when a retry succeeds. No credential value is
deleted, rendered or logged by this operation; NFR-004 remains BSB-23-PENDING-5's requirement.
