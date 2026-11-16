# Stories — BSB-34 (Run usage, trace & data retention)

Epic BSB-34 covers FR-159, FR-160, NFR-011, NFR-013, NFR-014, NFR-015, NFR-016, NFR-017 and
NFR-018. It is decomposed into 4 end-to-end slices below, and coverage of all 9 requirements is
verified. Every story ends in something a person sees on a product surface: the run report's
usage and turn figures, the trace a compliance reviewer opens from that report, the report's
"Run data" retention state, and the report's purged state after a project owner's request.

The four slices answer four user questions: what did this run consume and cost (PENDING-1); is
its trace demonstrably a test-environment trace (PENDING-2); is its stored data still inside the
retention window, and what does the report show when it is not (PENDING-3); and how does a
project owner remove its data before the window ends (PENDING-4). The recording, tracing, sweep
and purge mechanics are the means; each story's acceptance criteria assert the visible outcome
first and the durable record behind it second, so a technical layer is never a story on its own.

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than a Jira issue: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404
"Issue does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The
Atlassian MCP server is configured in `.mcp.json`, but this session exposed no Atlassian MCP
tools, so the configured site was queried read-only through its REST API. The epic being
decomposed is BSB-34, read read-only from the same site: summary "Run usage, trace & data
retention", type Epic, status To Do, labels FA-13/MVP, and a description matching the BSB-34
section of `epics.md`. No existing Jira issue is parented to BSB-34, and no Jira write was
attempted.

**Cross-epic prerequisites and hand-offs (not requirements of these stories).** PENDING-1 consumes
the terminal execution telemetry object `runs/<run-id>/usage.json`. That object is produced by the
execution path, and BSB-26-PENDING-1 owns the runtime adapter and launch contract but its
acceptance criteria do not name a usage report; BSB-26 must publish this object (or hand the same
record to the builder) or PENDING-1 has no producer. PENDING-1's report uses BSB-33-PENDING-5's
existing "Recorded turns" line and BSB-33-PENDING-1's report at GET "/projects/7/runs/21"; FR-102
(the turn-count display) and the report frame remain BSB-33's requirements and are not claimed
here. PENDING-2 writes to the external trace store and records the run's trace identifier, which
BSB-33-PENDING-5 reads to render the "Open trace" link; this supplies the BSB-34 side of BSB-33's
review Finding 7 / Open question 6, and FR-103 (the link) remains BSB-33's requirement. PENDING-3's
sweep and PENDING-4's purge operate on run artifacts written by BSB-26 (logs, progress, step
result) and BSB-33 (the captured diff); ADR SK-001 section 6 names the agent transcript under
`runs/<run-id>/`, but no BSB-26 story currently writes `runs/<run-id>/transcript.json`, so the
execution path must also write that artifact. PENDING-3 adds the report's "Run data" section,
which owns the retained/expired/pending status and the artifact download links; the log tail and
diff sections BSB-26-PENDING-2 and BSB-33-PENDING-3 own must degrade to their existing unavailable
state when the objects are gone. BSB-25-PENDING-1's out-of-scope names "bundle retention and purge
(BSB-34)"; this epic's requirements cover run transcripts, logs and results only, so
content-addressed `skill_bundles` objects are not deleted by PENDING-3 or PENDING-4 and BSB-25's
note needs reconciling.

A single requirement is claimed by exactly one story:

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-159 — the run page shows the run's token usage | BSB-34-PENDING-1 | "A completed run's usage, cost and turns are shown"; "A run that made no model calls shows zero, not not-recorded"; "A run with no telemetry shows not recorded" |
| FR-160 — the run page shows the run's cost | BSB-34-PENDING-1 | "A completed run's usage, cost and turns are shown"; "A run that made no model calls shows zero, not not-recorded"; "A run with no telemetry shows not recorded" |
| NFR-011 — when tracing is enabled, a run's trace identifies it as a test-environment run | BSB-34-PENDING-2 | "A test-environment trace is opened from the run report"; "Every run carries the installation's test-environment identity"; "Tracing disabled shows no trace"; "An unavailable trace store shows trace unavailable" |
| NFR-013 — run transcripts, logs and results are retained only for a configured period | BSB-34-PENDING-3 | "The default three-month period expires an old run's data"; "A configured retention period overrides the default"; "A run still inside the window keeps its data"; "Only run artifacts expire"; "An undeletable run is shown as expiry pending" |
| NFR-014 — run transcripts, logs and results can be purged on request | BSB-34-PENDING-4 | "The project owner purges a run's data and sees it recorded"; "A non-owner project member cannot purge"; "A run from another project is not disclosed"; "A repeated purge is idempotent"; "A failed purge is reported"; "A failed purge can be retried successfully" |
| NFR-015 — each run records its cost | BSB-34-PENDING-1 | "A completed run's usage, cost and turns are shown"; "A run with no telemetry shows not recorded" |
| NFR-016 — each run records its token usage | BSB-34-PENDING-1 | "A completed run's usage, cost and turns are shown"; "A run that made no model calls shows zero, not not-recorded"; "An invalid usage record is not stored or shown" |
| NFR-017 — each run records its turn count | BSB-34-PENDING-1 | "A completed run's usage, cost and turns are shown"; "A run that made no model calls shows zero, not not-recorded"; "A run with no telemetry shows not recorded" |
| NFR-018 — the default retention period is three months | BSB-34-PENDING-3 | "The default three-month period expires an old run's data" |

> New stories use draft keys in the `BSB-34-PENDING` series (`-1` to `-4`). `sdlc-tracker-sync`
> creates each story in Jira, parents it to BSB-34, and replaces the draft key with the real key in
> `story-map.json`.

---

## STORY: BSB-34-PENDING-1

**Title:** See what a run consumed and cost on its report
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **the run report to show the token usage, cost and turn count recorded when my run finished**, so that **I can see what the run consumed and cost as durable evidence instead of reconstructing it from logs or estimating it from current model prices**.

### Acceptance Criteria

Scenario: A completed run's usage, cost and turns are shown
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store holding "runs/21/usage.json" with content {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "turn_count": 7, "cost_usd": 0.018473, "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "cost_usd": 0.018473}]}
When the builder records run 21's usage as execution reaches its terminal state and Ada opens GET "/projects/7/runs/21"
Then the "runs" row id 21 has token_usage {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "total_tokens": 18190, "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 2048, "cache_write_tokens": 512, "cost_usd": 0.018473}]}, cost_usd 0.018473 and turn_count 7, the row's state remains "completed" and result_status "completed", and the response is HTTP 200 rendering "Tokens: 12,450 input, 3,180 output, 2,048 cache read, 512 cache write (18,190 total)", "Cost: $0.018473" and "Recorded turns: 7", with no exception text or stack trace in the body

Scenario: A run that made no model calls shows zero, not not-recorded
Given the same signed-in Ada and project 7, a "runs" row id 22 with project_id 7, user_id 42, skill "sdlc-lint-only", state "completed", result_status "completed", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store holding "runs/22/usage.json" with content {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0, "turn_count": 0, "cost_usd": 0.0, "models": []}
When the builder records run 22's usage and Ada opens GET "/projects/7/runs/22"
Then the "runs" row id 22 has token_usage {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0, "cache_write_tokens": 0, "total_tokens": 0, "models": []}, cost_usd 0.0 and turn_count 0, and the response is HTTP 200 rendering "Tokens: 0 input, 0 output, 0 cache read, 0 cache write (0 total)", "Cost: $0.000000" and "Recorded turns: 0", and the body does not render "not recorded"

Scenario: A run with no telemetry shows not recorded
Given the same signed-in Ada and project 7, a "runs" row id 23 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "failed", result_status "failed_infra", execution_error "The agent container could not be started.", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store that holds no "runs/23/usage.json"
When the builder attempts to record run 23's usage and Ada opens GET "/projects/7/runs/23"
Then the "runs" row id 23 still has token_usage NULL, cost_usd NULL and turn_count NULL, its state remains "failed", its result_status remains "failed_infra", and its execution_error remains "The agent container could not be started.", and the response is HTTP 200 rendering "Tokens: not recorded", "Cost: not recorded" and "Recorded turns: not recorded"

Scenario: An invalid usage record is not stored or shown
Given the same signed-in Ada and project 7, a "runs" row id 24 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store holding "runs/24/usage.json" with content {"input_tokens": -1, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "turn_count": 7, "cost_usd": 0.018473, "models": []}
When the builder attempts to record run 24's usage and Ada opens GET "/projects/7/runs/24"
Then the "runs" row id 24 still has token_usage NULL, cost_usd NULL and turn_count NULL, the builder's own log contains "The run's usage record is invalid.", and the response is HTTP 200 rendering "Tokens: not recorded", "Cost: not recorded" and "Recorded turns: not recorded" with no "3,180" or "0.018473" anywhere in the body

Scenario: A credential value in the telemetry is never stored or shown
Given the same signed-in Ada and project 7, a "runs" row id 21 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", finished_at "2026-11-16T11:05:00Z", token_usage NULL, cost_usd NULL and turn_count NULL, and a builder object store holding "runs/21/usage.json" with content {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "turn_count": 7, "cost_usd": 0.018473, "api_key": "sk-ant-test-3c9e", "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": 0.018473, "api_key": "sk-ant-test-3c9e"}]}
When the builder records run 21's usage and Ada opens GET "/projects/7/runs/21"
Then the "runs" row id 21 has token_usage {"input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "total_tokens": 15630, "models": [{"model": "claude-haiku-5-5", "input_tokens": 12450, "output_tokens": 3180, "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": 0.018473}]}, and neither the "runs" row, the builder's own log, nor the response body contains "sk-ant-test-3c9e"

Scenario: A non-member cannot see a run's usage, cost or turns
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), and the "runs" row id 21 of the first scenario
When Carol opens GET "/projects/7/runs/21"
Then the response is HTTP 403 with the message "You are not a member of this project.", and the body contains neither "12,450", "0.018473" nor "Recorded turns: 7"

### Covered requirements (traceability)
- FR-159
- FR-160
- NFR-015
- NFR-016
- NFR-017

### Out of scope
Separately recording usage without showing it (this story owns both ends of the same outcome);
the test-environment trace and `runs.trace_id` (BSB-34-PENDING-2); retention and purge
(BSB-34-PENDING-3 and BSB-34-PENDING-4); the report's identity, verdict, check, diff, Jira and
trace sections (BSB-33-PENDING-1 to -5); the live progress counter and the log tail while a run
executes (BSB-26-PENDING-2); executing the run and classifying its outcome (BSB-26-PENDING-3);
recording the model profile, tier and concrete model (BSB-26-PENDING-4); turn and spend caps and
the deadline (BSB-27); computing prices or estimating cost from a pricing table.

### Notes / dependencies
This story merges the recording and the display into one slice: the builder records the terminal
telemetry, and the same acceptance criteria then prove the value reaches Ada on the report, so
neither half is deferred to another story. It depends on BSB-26-PENDING-3 for the run reaching a
terminal state, on BSB-26-PENDING-1 for the execution path that writes
`runs/<run-id>/usage.json`, and on BSB-33-PENDING-1 for the report page at
GET "/projects/7/runs/21"; it adds a read-only "Usage and cost" section to that page and does not
change its routing, authentication or other sections. The "Recorded turns" line is
BSB-33-PENDING-5's existing display from `runs.turn_count` (FR-102, not claimed here); this story
supplies that column (NFR-017) and asserts the line end-to-end.

The telemetry contract is a JSON object with non-negative integers `input_tokens`, `output_tokens`,
`cache_read_tokens`, `cache_write_tokens` and `turn_count`, a non-negative number `cost_usd`, and
a `models` array whose entries carry `model` and the same token and cost fields for that model.
The builder computes `total_tokens` as the sum of the four token counts; it does not trust a
telemetry-supplied total. A record is accepted only when every required field is present and
valid; otherwise all three columns stay NULL and the record is not partially written. No cost is
recomputed from token counts or a price table: `runs.cost_usd` is the telemetry's cost.

ADR SK-001 section 9 already lists `runs.cost_usd`; this story adds `runs.token_usage` JSONB and
`runs.turn_count` integer, and the data-model stage must record them. ADR section 9 does not list
`token_usage` or `turn_count`. The recorded turn count is the terminal execution total, not the
agent's live progress counter BSB-26-PENDING-2 renders as "Turns: 3 of 12"; BSB-27 enforces the
turn and spend caps from the live telemetry path and owns no column here. The section renders the
recorded values only: `total_tokens` is the sum recorded above, token counts use thousands
separators, and cost uses exactly six decimal places after "$" (the scale of `runs.cost_usd`). A
NULL `token_usage` or NULL `cost_usd` is the single not-recorded state and renders "not recorded",
never zero, so a run whose telemetry was absent cannot be mistaken for a free run. A recorded
all-zero object is the distinct zero state. Credential values never enter the usage record or the
report: the builder stores only the documented fields, so an extra field such as `api_key` is
dropped. NFR-004 is mapped to BSB-23-PENDING-5, whose shared redaction rule this story applies
without claiming that requirement.

---

## STORY: BSB-34-PENDING-2

**Title:** Open a run's trace and see it is marked as a test-environment run
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-13, MVP

### Story
As a **test-project owner**, I want **every run's trace to carry the installation's test-environment identity and to open from the run's report**, so that **I can show a compliance reviewer that the run touched only the test environment and can never be mistaken for production traffic**.

### Acceptance Criteria

Scenario: A test-environment trace is opened from the run report
Given a signed-in test-project owner Ada who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "prepared" and trace_id NULL, installation tracing configuration {"enabled": true, "environment": "skilltest", "url_template": "https://langfuse.test/traces/{trace_id}"}, and a trace store that assigns id "trace-4f2c9a1b7d3e" to the first trace it receives
When the builder launches run 21 and Ada opens the "Open trace" link on GET "/projects/7/runs/21"
Then the trace store holds exactly one trace with id "trace-4f2c9a1b7d3e", env "skilltest" and metadata {"run_id": 21, "project_id": 7}, the "runs" row id 21 has trace_id "trace-4f2c9a1b7d3e", and the report's link has href "https://langfuse.test/traces/trace-4f2c9a1b7d3e" and resolves to HTTP 200 showing that same trace with env "skilltest"

Scenario: Every run carries the installation's test-environment identity
Given installation tracing configuration {"enabled": true, "environment": "skilltest", "url_template": "https://langfuse.test/traces/{trace_id}"}, a "runs" row id 21 with project_id 7, state "prepared" and trace_id NULL, a "runs" row id 31 with project_id 8, state "prepared" and trace_id NULL, and a trace store that assigns id "trace-4f2c9a1b7d3e" to its first trace and id "trace-8a1b2c3d4e5f" to its second trace
When the builder launches runs 21 and 31 and Ada opens each run's report
Then the trace store holds exactly two traces, each with env "skilltest" and neither with env "production", the "runs" rows id 21 and id 31 have trace_id "trace-4f2c9a1b7d3e" and "trace-8a1b2c3d4e5f", and the reports' links resolve to "https://langfuse.test/traces/trace-4f2c9a1b7d3e" and "https://langfuse.test/traces/trace-8a1b2c3d4e5f" respectively

Scenario: Tracing disabled shows no trace
Given a "runs" row id 21 with project_id 7, state "prepared" and trace_id NULL, installation tracing configuration {"enabled": false, "environment": "skilltest", "url_template": "https://langfuse.test/traces/{trace_id}"}, and a trace store whose creation counter is 0
When the builder launches run 21 and Ada opens GET "/projects/7/runs/21"
Then the trace store's creation counter remains 0, the "runs" row id 21 has trace_id NULL and state "running" with execution_error NULL, and the report renders "Tracing is disabled." with no anchor to "https://langfuse.test"

Scenario: An unavailable trace store shows trace unavailable
Given a "runs" row id 21 with project_id 7, state "prepared" and trace_id NULL, installation tracing configuration {"enabled": true, "environment": "skilltest", "url_template": "https://langfuse.test/traces/{trace_id}"}, and a trace store that returns HTTP 503 "Service Unavailable" for trace creation
When the builder launches run 21 and Ada opens GET "/projects/7/runs/21"
Then the trace store's creation counter is 1, the "runs" row id 21 has trace_id NULL and proceeds to state "running" with execution_error NULL, and the report renders "Trace unavailable." with no anchor to "https://langfuse.test" and no exception text

Scenario: A non-member cannot reach the trace from the run report
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), and the "runs" row id 21 of the first scenario
When Carol opens GET "/projects/7/runs/21"
Then the response is HTTP 403 with the message "You are not a member of this project.", and the body contains neither "trace-4f2c9a1b7d3e" nor "langfuse.test"

### Covered requirements (traceability)
- NFR-011

### Out of scope
Choosing or operating the trace store (external); the trace's spans, prompts, outputs and LLM-call
detail; the trace store's own retention and purge; recording token usage, cost and turn count
(BSB-34-PENDING-1); retention and purge of run artifacts (BSB-34-PENDING-3 and BSB-34-PENDING-4);
changing the platform's trace format; per-run author choice of trace environment.

### Notes / dependencies
The outcome this story delivers is what the reviewer sees when the trace opens: a trace tagged with
the installation's test-environment identity, reachable from the run's report. The trace client and
the identifier column are the means, not the slice. It depends on BSB-26-PENDING-1 for the run
launch path and the runtime adapter, on BSB-33-PENDING-5 for the report's "Open trace" link and its
"Tracing is disabled." and "Trace unavailable." states (FR-103, not claimed here), and on BSB-33's
report at GET "/projects/7/runs/21". The builder registers exactly one trace for a prepared run and
then launches it, so the trace exists before the agent makes its first model call; the launch path
must call this hook and pass the trace identifier to the runtime adapter as a cross-epic hand-off,
because BSB-26-PENDING-1's acceptance criteria do not name tracing. The external trace store is a
dependency of the epic, not a component this story builds; tests exercise it at the trace store's API boundary,
which is the system of record the criterion asserts.

The installation tracing configuration has three operator-managed fields: `enabled` (boolean),
`environment` (the installation's trace environment identity, "skilltest" for a skill-test
deployment) and `url_template` (the trace-store URL template with `{trace_id}`). The marker is the
installation's environment identity, never a per-run author choice, so every run of the installation
is marked the same way and no run can carry its own environment value. A deployment that turns
tracing off creates no trace and records no identifier; turning it on never changes a run's
outcome. A trace store that is unavailable leaves `runs.trace_id` NULL and the run continues:
tracing is non-gating, and BSB-33-PENDING-5 renders the report's unavailable state.

ADR SK-001 section 9 lists no `runs.trace_id`; this story adds it and the data-model stage must
record it. BSB-33-PENDING-5 reads `runs.trace_id` and the installation `url_template` to render
"Open trace", and this story is their producer, which resolves the BSB-34 side of that story's
one-sided dependency (BSB-33's review Finding 7 / Open question 6).

---

## STORY: BSB-34-PENDING-3

**Title:** See that an old run's logs, transcript and results have expired
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **a run's report to show whether its transcript, logs and results are still kept or have expired under the installation's retention period**, so that **I can rely on old test data not being retained or readable after its window and still read recent run evidence**.

### Acceptance Criteria

Scenario: The default three-month period expires an old run's data
Given installation retention configuration with retention_months unset, a signed-in skill author Ada who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", final_verdict "pass" and finished_at "2026-05-01T04:00:00Z", a "runs" row id 22 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", final_verdict "pass" and finished_at "2026-10-01T04:00:00Z", a builder object store holding "runs/21/agent.log", "runs/21/transcript.json", "runs/21/bb_step_result.json", "runs/21/diff.json", "runs/21/usage.json", "runs/22/agent.log" and "runs/22/transcript.json", and a builder clock reading "2026-11-16T12:00:00Z"
When the retention sweep runs and Ada opens GET "/projects/7/runs/21" and GET "/projects/7/runs/22"
Then no object exists under "runs/21/", the run 21 response is HTTP 200 rendering "Run data: expired on 2026-08-01 (retained for 3 months)", "Verdict: PASS" and "Skill: sdlc-fix-bug-reproduce" with no "Download agent log" or "Download transcript" link, the objects "runs/22/agent.log" and "runs/22/transcript.json" still exist, and the run 22 response is HTTP 200 rendering "Run data: retained until 2027-01-01", "Download agent log" and "Download transcript"

Scenario: A configured retention period overrides the default
Given installation retention configuration with retention_months 6, the same signed-in Ada and project 7, a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass" and finished_at "2026-05-01T04:00:00Z", a "runs" row id 22 with project_id 7, state "completed", final_verdict "pass" and finished_at "2026-06-01T04:00:00Z", a builder object store holding "runs/21/agent.log", "runs/21/transcript.json", "runs/22/agent.log" and "runs/22/transcript.json", and a builder clock reading "2026-11-16T12:00:00Z"
When the retention sweep runs and Ada opens GET "/projects/7/runs/21" and GET "/projects/7/runs/22"
Then no object exists under "runs/21/", the run 21 response renders "Run data: expired on 2026-11-01 (retained for 6 months)" with no "Download agent log" link, the objects "runs/22/agent.log" and "runs/22/transcript.json" still exist, and the run 22 response renders "Run data: retained until 2026-12-01", "Download agent log" and "Download transcript"

Scenario: A run still inside the window keeps its data
Given installation retention configuration with retention_months unset, the same signed-in Ada and project 7, a "runs" row id 23 with project_id 7, state "completed", final_verdict "pass" and finished_at "2026-11-01T09:00:00Z", a builder object store holding "runs/23/agent.log" and "runs/23/transcript.json", and a builder clock reading "2026-11-16T12:00:00Z"
When the retention sweep runs and Ada opens GET "/projects/7/runs/23"
Then the objects "runs/23/agent.log" and "runs/23/transcript.json" still exist, and the response is HTTP 200 rendering "Run data: retained until 2027-02-01", "Download agent log" and "Download transcript"

Scenario: A run with no stored artifacts shows the empty state
Given installation retention configuration with retention_months unset, the same signed-in Ada and project 7, a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", state "failed", result_status "failed_infra", execution_error "The agent container could not be started." and finished_at "2026-11-01T09:00:00Z", a builder object store with no object under "runs/24/", and a builder clock reading "2026-11-16T12:00:00Z"
When Ada opens GET "/projects/7/runs/24"
Then the response is HTTP 200 rendering "Run data: retained until 2027-02-01" and "No run data was recorded.", with no exception text and no "Download agent log" link

Scenario: Only run artifacts expire, not the run record or its shared bundle
Given installation retention configuration with retention_months 3, the same signed-in Ada and project 7, a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass" and finished_at "2026-05-01T04:00:00Z", a "skill_bundles" row for skill "sdlc-fix-bug-reproduce" and skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" with s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", a builder object store holding "runs/21/agent.log", "runs/21/transcript.json" and that bundle object, and a builder clock reading "2026-11-16T12:00:00Z"
When the retention sweep runs and Ada opens GET "/projects/7/runs/21"
Then no object exists under "runs/21/", the object "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz" still exists, the "runs" row id 21 and the "skill_bundles" row still exist, and the response is HTTP 200 rendering "Run data: expired on 2026-08-01 (retained for 3 months)", "Verdict: PASS" and "Skill: sdlc-fix-bug-reproduce"

Scenario: An undeletable run is shown as expiry pending
Given installation retention configuration with retention_months 3, the same signed-in Ada and project 7, a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass" and finished_at "2026-05-01T04:00:00Z", a builder object store holding "runs/21/agent.log" and "runs/21/transcript.json" and returning HTTP 503 "Service Unavailable" for every delete under "runs/21/", and a builder clock reading "2026-11-16T12:00:00Z"
When the retention sweep runs and Ada opens GET "/projects/7/runs/21"
Then the objects "runs/21/agent.log" and "runs/21/transcript.json" still exist, the builder's own log contains "Run data for run 21 could not be deleted.", and the response is HTTP 200 rendering "Run data: expiry pending: The run's data could not be deleted." with no "Download agent log" or "Download transcript" link

### Covered requirements (traceability)
- NFR-013
- NFR-018

### Out of scope
Purging one run's data on request (BSB-34-PENDING-4); recording usage and cost
(BSB-34-PENDING-1); the trace store's own retention and purge (external); deleting the `runs`
row, its verification record, its verdicts, its usage values or any other database metadata;
deleting content-addressed `skill_bundles` objects; deleting another project's data; an operator
settings UI; backup or archival copies outside the builder's object store; the live log tail and
diff rendering BSB-26-PENDING-2 and BSB-33-PENDING-3 own.

### Notes / dependencies
The visible outcome is the report's "Run data" section: a retained-until date and artifact
download links while the run is inside the window, an expired notice and no links once it is past
it, and an expiry-pending notice when a deletion failed. The scheduled sweep is an implementation
detail behind that outcome; every scenario asserts what Ada sees on the report (plus the durable
object-store state that makes the notice true) and never the sweep's internals. The section is
added to BSB-33-PENDING-1's report at GET "/projects/7/runs/21" and changes no routing,
authentication or other section.

The retention period is an installation setting in whole months (`retention_months`, default 3,
minimum 1) managed by the operator; an author cannot set it per run. A run's artifacts expire at
the same UTC day-of-month and time `retention_months` months after `runs.finished_at`, so a run
finished at "2026-05-01T04:00:00Z" expires at "2026-08-01T04:00:00Z" and is shown expired on
2026-11-16 with "retained for 3 months". The report and the sweep use the same setting and the same
expiry rule, so the notice cannot disagree with the deletion. A run that is past expiry but whose
objects could not be deleted is shown as "expiry pending" and offers no download, rather than
being falsely shown as expired or exposing data past its window. A run that never produced
artifacts shows "No run data was recorded." rather than an error.

The sweep deletes every object under `runs/<run-id>/`: the agent transcript, `agent.log`,
`progress.json`, `bb_step_result.json`, the captured `diff.json` and the terminal `usage.json`. It
never deletes the `runs` row or its verdict, verification or usage columns, so the run remains
explainable after its evidence is gone. `skill_bundles` objects are keyed by
`(skill, skills_commit_sha)` and shared by every run at that commit; they are not run-scoped and
are not deleted here. BSB-25-PENDING-1's out-of-scope names "bundle retention and purge (BSB-34)",
which this story does not implement; that note needs reconciling with BSB-34's epic scope, which
covers run transcripts, logs and results only.

Depends on BSB-26-PENDING-3 for `runs.finished_at` and the terminal run state, on BSB-26-PENDING-2
for `runs/<run-id>/agent.log` and `runs/<run-id>/progress.json`, on BSB-26-PENDING-3 for
`runs/<run-id>/bb_step_result.json`, and on BSB-33-PENDING-3 for the captured
`runs/<run-id>/diff.json` it renders. ADR SK-001 section 6 names the agent transcript under
`runs/<run-id>/`; no BSB-26 story currently writes `runs/<run-id>/transcript.json`, so the
execution path must write it as a cross-epic hand-off or the transcript has no producer. The log
and diff sections BSB-26-PENDING-2 and BSB-33-PENDING-3 own must degrade to their existing
unavailable state when the objects are gone; their reviewers must confirm that fallback. The sweep
acts only on the builder's object store and never renders or rewrites a credential value; NFR-004
remains BSB-23-PENDING-5's requirement.

---

## STORY: BSB-34-PENDING-4

**Title:** Purge a run's data on request and see it recorded on the report
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **project owner**, I want **to purge one run's transcripts, logs and results on request and see the purge recorded on the run's report**, so that **I can remove test data before its retention window ends and show that the deletion was authorized and completed**.

### Acceptance Criteria

Scenario: The project owner purges a run's data and sees it recorded
Given a signed-in project owner Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass", purged_at NULL, purged_by NULL and purge_error NULL, a builder object store holding "runs/21/agent.log", "runs/21/transcript.json", "runs/21/bb_step_result.json", "runs/21/diff.json" and "runs/21/usage.json", and a builder clock reading "2026-11-16T11:10:00Z"
When Ada sends POST "/projects/7/runs/21/purge" and then opens GET "/projects/7/runs/21"
Then the POST response is HTTP 200 with body {"status": "purged", "objects_deleted": 5}, no object exists under "runs/21/", the "runs" row id 21 remains with state "completed", final_verdict "pass", purged_at "2026-11-16T11:10:00Z", purged_by 42 and purge_error NULL, and the report is HTTP 200 rendering "Run data: purged on 2026-11-16 11:10 UTC by Ada", "Verdict: PASS" and no "Download agent log" or "Download transcript" link

Scenario: A non-owner project member cannot purge
Given a signed-in skill author Carol whose local "users" id is 44 and who has a "project_members" row (project_id 7, user_id 44, role "member") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, state "completed", purged_at NULL, purged_by NULL and purge_error NULL, and a builder object store holding "runs/21/agent.log" and "runs/21/bb_step_result.json"
When Carol sends POST "/projects/7/runs/21/purge" and then opens GET "/projects/7/runs/21"
Then the POST response is HTTP 403 with the message "Only the project owner can purge run data.", the objects "runs/21/agent.log" and "runs/21/bb_step_result.json" still exist, the "runs" row id 21 still has purged_at NULL, purged_by NULL and purge_error NULL, and the report renders "Download agent log" and no "Purge run data" action

Scenario: A run from another project is not disclosed
Given the same signed-in Ada with her "project_members" row (project_id 7, user_id 42, role "owner"), a "runs" row id 31 with project_id 8, state "completed", purged_at NULL, purged_by NULL and purge_error NULL, a builder object store holding "runs/31/agent.log", and an object-store delete counter for run 31 that is 0
When Ada sends POST "/projects/7/runs/31/purge"
Then the response is HTTP 404 with the message "Run not found.", the object "runs/31/agent.log" still exists, the object-store delete counter for run 31 remains 0, and the "runs" row id 31 still has purged_at NULL

Scenario: A repeated purge is idempotent
Given the same signed-in Ada with her "project_members" row for project 7, a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass", purged_at "2026-11-15T09:00:00Z", purged_by 42 and purge_error NULL, and a builder object store with no object under "runs/21/"
When Ada sends POST "/projects/7/runs/21/purge" again and opens GET "/projects/7/runs/21"
Then the response is HTTP 200 with body {"status": "already purged", "objects_deleted": 0}, the "runs" row id 21 still has purged_at "2026-11-15T09:00:00Z" and purged_by 42, and the report renders "Run data: purged on 2026-11-15 09:00 UTC by Ada" and no "Purge run data" action

Scenario: A failed purge is reported
Given the same signed-in Ada with her "project_members" row for project 7, a "runs" row id 21 with project_id 7, state "completed", final_verdict "pass", purged_at NULL, purged_by NULL and purge_error NULL, a builder object store holding "runs/21/agent.log" and "runs/21/bb_step_result.json" and returning HTTP 503 "Service Unavailable" for every delete under "runs/21/", and a builder clock reading "2026-11-16T11:10:00Z"
When Ada sends POST "/projects/7/runs/21/purge" and then opens GET "/projects/7/runs/21"
Then the POST response is HTTP 503 with the message "The run's data could not be purged. Retry later.", the "runs" row id 21 still has purged_at NULL and purged_by NULL with purge_error "The run's data could not be purged.", the objects "runs/21/agent.log" and "runs/21/bb_step_result.json" still exist, and the report renders "Run data: purge failed: The run's data could not be purged.", "Download agent log" and "Verdict: PASS"

Scenario: A failed purge can be retried successfully
Given the failed purge of the previous scenario and a builder object store that now accepts deletes under "runs/21/" with "runs/21/agent.log" and "runs/21/bb_step_result.json" still present, and a builder clock reading "2026-11-16T11:20:00Z"
When Ada sends POST "/projects/7/runs/21/purge" again and opens GET "/projects/7/runs/21"
Then the response is HTTP 200 with body {"status": "purged", "objects_deleted": 2}, no object exists under "runs/21/", the "runs" row id 21 has purged_at "2026-11-16T11:20:00Z", purged_by 42 and purge_error NULL, and the report renders "Run data: purged on 2026-11-16 11:20 UTC by Ada" and no "Download agent log" link

### Covered requirements (traceability)
- NFR-014

### Out of scope
The scheduled retention sweep and the installation retention setting (BSB-34-PENDING-3);
recording usage and cost (BSB-34-PENDING-1); purging traces from the external trace store;
deleting the `runs` row, its verification record, its verdicts or its usage values; deleting
content-addressed `skill_bundles` objects; purging another project's data; deleting a whole
project or its builds; the run page's other sections and layout (BSB-33-PENDING-1 to -5); the
command line (BSB-37).

### Notes / dependencies
The outcome is the owner's request plus the report's record of it: after a successful purge the
"Run data" section states when and by whom the data was purged and no longer offers downloads;
after a failure it states the failure and the reason while the data remains readable. The
deletion mechanics are the means, not the slice. The operation is
POST "/projects/7/runs/21/purge" on the builder's authenticated surface; it resolves the run's
project and checks the project-owner role before any object is read or deleted, and it never
discloses a run from another project. It depends on BSB-18 for the authenticated session and the
skill-builders gate, on BSB-22-PENDING-3 for the shared project-membership check, on
BSB-26-PENDING-2 and BSB-26-PENDING-3 for `runs/<run-id>/agent.log`,
`runs/<run-id>/progress.json` and `runs/<run-id>/bb_step_result.json`, and on BSB-33-PENDING-3 and
BSB-34-PENDING-1 for the captured `runs/<run-id>/diff.json` and `runs/<run-id>/usage.json`.

The PRD says run data "can be purged on request" without naming the authorizing role. This story
requires the project's owner role, consistent with the test-project owner's role as the project's
administrator; a project member who is not the owner is denied and is shown no purge action.
Purging is idempotent: a run whose `purged_at` is already set returns "already purged" and changes
nothing. The deletion covers every object under `runs/<run-id>/` — the transcript, logs, step
result, captured diff and usage record — and never the `runs` row or its audit columns, so the
purge remains explainable. A partial failure is reported as HTTP 503, recorded in
`runs.purge_error`, and retried by sending the request again; a retry deletes whatever remains and
then sets `purged_at` and `purged_by`.

The data-model stage must add nullable `runs.purged_at` timestamptz, `runs.purged_by` integer
(the purging user's id) and `runs.purge_error` text; ADR SK-001 section 9 lists none of them.
`purged_at` and `purged_by` are the auditable result the epic requires, and they are never cleared
by a later purge attempt; `purge_error` is cleared when a retry succeeds. No credential value is
deleted, rendered or logged by this operation; NFR-004 remains BSB-23-PENDING-5's requirement.
