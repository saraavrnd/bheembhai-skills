# Stories — BSB-34 (Run usage, trace & data retention)

Source: Jira epic **BSB-34** — *Run usage, trace & data retention* (feature area FA-13, release MVP,
labels FA-13, MVP), fetched read-only from the Atlassian project `bheembhai-skill-builder`; its
summary, description, functional scope, goal, stated edge cases and covered-requirement list are the
same as the BSB-34 section of `docs/product/epics.md`. The requirement IDs mapped to the epic are in
`docs/product/epic-map.json`.

Epic BSB-34 covers 11 requirements. They decompose into the 5 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-34`), is epic
**BSB-34**. The Atlassian MCP server exposed no tools in this session (the `.mcp.json` entry passes
`args` as a string where Claude Code expects an array), so the epic was fetched read-only through
the Atlassian REST API with the same credentials. Nothing was written to Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-102 | BSB-34-PENDING-2 |
| FR-103 | BSB-34-PENDING-3 |
| FR-159 | BSB-34-PENDING-2 |
| FR-160 | BSB-34-PENDING-2 |
| NFR-011 | BSB-34-PENDING-3 |
| NFR-013 | BSB-34-PENDING-4 |
| NFR-014 | BSB-34-PENDING-5 |
| NFR-015 | BSB-34-PENDING-1 |
| NFR-016 | BSB-34-PENDING-1 |
| NFR-017 | BSB-34-PENDING-1 |
| NFR-018 | BSB-34-PENDING-4 |

The epic's three stated edge cases are covered explicitly: a run interrupted before usage is
reported still persists the last usage the runtime wrote (BSB-34-PENDING-1); a purge removes every
transcript, log and result object for the run together and is audited in `run_purges`
(BSB-34-PENDING-4 and BSB-34-PENDING-5); and retention is read from installation configuration,
with a three-month default and a startup failure on an invalid value (BSB-34-PENDING-4). The
non-goals are respected: there is no per-run retention override, no analytics across runs, and no
change to the run's state, verdict or cost enforcement.

## Usage, trace, retention and purge contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control and object-store
fixture unless it says otherwise. The member session, the local `users` rows and the
`skill-builders` gate are established by epic BSB-18. The project, its `projects` row and its
`project_members` rows are established by epic BSB-22. The run, its prepared state, its terminal
state vocabulary, its executor, the run page route and the progress and log APIs are epic BSB-26's.
The build, bundle and run branch are epics BSB-20, BSB-21 and BSB-25's and are not read here except
as the run's identity. The `runs` and `skill_bundles` columns follow
`docs/adr/SK-001-skill-builder.md` §5 and §9.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T13:00:00Z` |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing` |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42`, `created_at` = `2026-11-14T09:00:00Z`; ids `1` to `6`, `8`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly two rows: `(project_id 7, user_id 42, role owner)` and `(project_id 7, user_id 43, role member)`; Alan has no row for project `7` |
| Run 1 | `runs` row: `id` = `1`, `project_id` = `7`, `user_id` = `42`, `skill` = `sdlc-fix-bug-triage`, `skills_ref` = `test/ada/fix-reproduce`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `input_branch` = `main`, `run_branch` = `skilltest/1`, `state` = `completed`, `claimed_verdict` = `completed`, `final_verdict` = `NULL`, `verification` = `NULL`, `kind` = `run`, `created_at` = `2026-11-15T10:00:00Z`, terminal at `2026-11-15T10:05:00Z`; `turn_count`, `input_tokens`, `output_tokens`, `cost_usd`, `trace_id`, `trace_url` and `evidence_purged_at` are `NULL` until a scenario sets them |
| Run 2 | prepared like run `1` except `id` = `2`, `user_id` = `43`, `run_branch` = `skilltest/2` and `created_at` = `2026-11-15T10:01:00Z`; a scenario may set another terminal state |
| Run 3 | prepared like run `1` except `id` = `3`, `run_branch` = `skilltest/3`, `state` = `running`, `claimed_verdict` = `NULL` and `created_at` = `2026-11-15T10:02:00Z` |
| Run 4 | prepared like run `1` except `id` = `4`, `run_branch` = `skilltest/4` and `created_at` = `2026-11-15T10:03:00Z`; a scenario may set another terminal state |
| Run 5 | prepared like run `1` except `id` = `5`, `run_branch` = `skilltest/5`, `state` = `failed_infra`, `claimed_verdict` = `NULL` and `created_at` = `2026-11-15T10:04:00Z` |
| Run 6 | prepared like run `1` except `id` = `6`, `run_branch` = `skilltest/6`, `state` = `failed_timeout`, `claimed_verdict` = `NULL` and `created_at` = `2026-11-15T10:04:30Z` |
| Object-store bucket | `skill-builder-runs`; the prefix for run `1` is `runs/1/` |
| Run evidence objects | The five objects `runs/1/agent.log`, `runs/1/bb_step_result.json`, `runs/1/progress.json`, `runs/1/transcript.jsonl` and `runs/1/usage.json`. The bundle is at `bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz` and is shared, not part of the run prefix |
| Run page | `GET https://builder.skillbuilder.internal/projects/{project_id}/runs/{run_id}` |
| Progress API | `GET https://builder.skillbuilder.internal/api/projects/{project_id}/runs/{run_id}/progress` |
| Log API | `GET https://builder.skillbuilder.internal/api/projects/{project_id}/runs/{run_id}/log?tail={n}` where `n` is an integer from `1` to `200` and defaults to `200` |
| Purge API | `POST https://builder.skillbuilder.internal/api/projects/{project_id}/runs/{run_id}/purge` with an empty body |
| Success status | HTTP 200 with `Content-Type: text/html; charset=utf-8` for the run page; HTTP 200 with `Content-Type: application/json` for the APIs; HTTP 200 for the purge API |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |
| Current time | `2026-11-15T10:00:00Z` unless a scenario fixes another time |

**Installation configuration.** These are environment variables read at builder startup. They are
operator-managed installation settings, not per-run or per-project values.

| Variable | Meaning | Default |
|----------|---------|---------|
| `SKILL_BUILDER_TRACING_ENABLED` | `true` enables run tracing; any other value, or unset, disables it | unset (disabled) |
| `LANGFUSE_HOST` | Trace-store base URL | `https://langfuse.skillbuilder.internal` |
| `LANGFUSE_PROJECT_ID` | Trace-store project used in the trace link | `skill-builder` |
| `LANGFUSE_PUBLIC_KEY` | Trace-store public key | required when tracing is enabled |
| `LANGFUSE_SECRET_KEY` | Trace-store secret key | required when tracing is enabled |
| `SKILL_BUILDER_RETENTION_MONTHS` | Run-evidence retention period, a positive integer number of calendar months | `3` |

The `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY` and every model credential are never written to a
run row, a log or an audit record (NFR-004, epic BSB-23's redaction mechanism).

**Usage report contract.** The runtime writes `s3://skill-builder-runs/runs/<run_id>/usage.json`
and refreshes it after every completed model turn, so the last completed write survives a run that
is force-terminated. The file is a JSON object with these fields:

```
{"turns":12,"input_tokens":12345,"output_tokens":6789,"cost_usd":0.0421,"updated_at":"2026-11-15T10:05:00Z"}
```

The component that writes the run's terminal state — epic BSB-26's executor, or epic BSB-27's
deadline or cap supervisor — reads the file and persists the usage columns in the same transaction
as that terminal write. This covers a run terminated before its final usage was reported. Field
rules: `turns`, `input_tokens` and `output_tokens` must be non-negative JSON integers; `cost_usd`
must be a non-negative JSON number with at most six decimal places; `updated_at` is not persisted. A
field that is absent or invalid leaves its column `NULL`; the other fields are still persisted. A
file that is absent, unreadable, not a JSON object or not valid JSON leaves all four columns
`NULL`. Persisting usage never changes any other run column: `runs.state`, `runs.claimed_verdict`,
`runs.final_verdict`, `runs.verification` and `runs.evidence_purged_at` keep the values the terminal
write gave them.

The persisted run columns are `runs.turn_count` (integer), `runs.input_tokens` (bigint),
`runs.output_tokens` (bigint) and the existing `runs.cost_usd` (`numeric(12,6)`). `cost_usd` is
stored as `0.042100` for the report above. `NULL` means the runtime reported no value; the builder
never invents, estimates or rounds usage it did not receive.

**Run page regions owned by this epic.** The run page is epic BSB-26's route and epic BSB-33's
report; this epic owns only these regions and adds no other page region.

| Element id | Exact content |
|------------|---------------|
| `run-turns` | `<div id="run-turns">Turns: 12</div>` when `turn_count` is `12`; `<div id="run-turns">Turns: Not reported</div>` when it is `NULL` |
| `run-tokens` | `<div id="run-tokens">Tokens: 19134 (12345 in, 6789 out)</div>` when `input_tokens` is `12345` and `output_tokens` is `6789`; `<div id="run-tokens">Tokens: Not reported</div>` when either is `NULL` |
| `run-cost` | `<div id="run-cost">Cost: $0.042100</div>` when `cost_usd` is `0.042100`; `<div id="run-cost">Cost: Not reported</div>` when it is `NULL` |
| `run-trace` | `<a id="run-trace" href="https://langfuse.skillbuilder.internal/project/skill-builder/traces/run-1">Open trace</a>` when tracing is enabled and the trace was created; `<div id="run-trace">Trace unavailable.</div>` when tracing is enabled but the trace was not created; no element when tracing is disabled |
| `run-evidence` | `<div id="run-evidence">Run transcripts, logs and results were purged on 2026-11-15T03:00:00Z.</div>` after a purge; absent before a purge |

**Trace contract.** When `SKILL_BUILDER_TRACING_ENABLED` is `true`, the executor creates exactly
one trace per claimed run whose `kind` is `run`, before the agent container starts, with a
deterministic id `run-<run_id>`
and this exact body to `POST {LANGFUSE_HOST}/api/public/traces`, authenticated with HTTP Basic using
`LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`:

```
{"id":"run-1","name":"run-1","metadata":{"env":"skilltest","run_id":"1","project_id":"7","skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b"}}
```

The trace store returns HTTP 200 with `{"id":"run-1"}`. The builder stores
`runs.trace_id` = `run-1` and `runs.trace_url` =
`https://langfuse.skillbuilder.internal/project/skill-builder/traces/run-1`. A trace-store error,
timeout (the request has a 1-second timeout) or malformed response leaves both columns `NULL` and
does not change the run's state, delay its launch beyond that timeout, or fail it. When tracing is
disabled, the builder sends no trace-store request and both columns stay `NULL`. When tracing is
enabled and either key is unset, the builder writes exactly `[skill-builder] missing <variable>` to
stderr and exits with status `1` before claiming any run.

**Retention and purge contract.** One function, `purge_run_evidence(run_id, reason, requested_by)`,
backs both the retention sweep and the on-request purge. It deletes every object whose key starts
with `runs/<run_id>/` in one S3 multi-object delete, then, in the same transaction as the successful
delete, sets `runs.verification = NULL` and `runs.evidence_purged_at` to the purge time and inserts
one `run_purges` row. It does not delete or change the `runs` row, its usage columns, its
`final_verdict`, its `state`, its branch, the shared bundle under `bundles/`, the `run_jira` record
or any scan record.

The retention sweep runs once at builder startup and then every 24 hours at `03:00` UTC. At
`now`, the cutoff is `now - make_interval(months => SKILL_BUILDER_RETENTION_MONTHS)`. A run is
eligible when `runs.created_at < cutoff` and `runs.evidence_purged_at IS NULL`; a run created at or
after the cutoff, or already purged, is skipped. An invalid `SKILL_BUILDER_RETENTION_MONTHS` value
(not a positive integer) is a startup error, not a silent fallback: the builder writes exactly
`[skill-builder] invalid SKILL_BUILDER_RETENTION_MONTHS: must be a positive integer` to stderr and
exits with status `1`.

`run_purges` is an additive audit table: `id` (identity), `run_id`, `reason` (`retention` or
`request`), `requested_by` (nullable `users.id`; `NULL` for retention), `purged_at`,
`objects` (JSONB array of the deleted keys, sorted ascending), `verification_cleared` (boolean,
`true` only when the purge set a non-`NULL` `runs.verification` to `NULL`), `status` (`completed`
or `failed`) and `error` (nullable text). A failed attempt inserts a
`status` = `failed` row with `error` = `object_store_error`, `objects` = `[]` and
`verification_cleared` = `false`, and leaves the run's evidence and `runs` row unchanged.

After a successful purge the run page still renders the usage, cost and trace regions from the
`runs` row, contains the `run-evidence` message above with the purge time, and has no element with
id `run-log`. The log API returns exactly
`{"run_id":1,"lines":[],"truncated":false,"purged":true}` and the progress API returns
`{"run_id":1,"step":null,"state":"completed","message":null,"percent":0,"updated_at":null}`.

## Decisions recorded in this decomposition (confirm at review)

1. **Usage source and columns.** ADR §9 has `runs.cost_usd` but no turn or token columns. This
   decomposition adds `runs.turn_count`, `runs.input_tokens` and `runs.output_tokens` and reads the
   figures from the runtime's incremental `runs/<run_id>/usage.json`. BSB-27 enforces caps from the
   runtime's live cost meter; this epic consumes only the final figures and never enforces a cap or
   deadline. If the platform exposes the same meter under a different file or API, only the reader
   changes.
2. **Trace identity.** The trace id is deterministic (`run-<run_id>`) so the link is reproducible
   and a retried launch cannot create a second trace for one run. This decomposition adds nullable
   `runs.trace_id` and `runs.trace_url` columns. The metadata key `env` with value `skilltest` is
   the ADR's test-environment marker. The agent image's spans are the platform image's concern;
   this epic owns the trace creation, the marker and the run page link.
3. **Retention unit.** "Three months" is implemented as three calendar months, not a fixed 90
   days, so the operator setting is in months. The default is applied only when the variable is
   unset; an empty or invalid value is a startup error.
4. **Purge scope and schema.** "Transcripts, logs and results" is read as every object under the
   run prefix plus `runs.verification` (epic BSB-29 states that record is run-result data). This
   decomposition adds nullable `runs.evidence_purged_at` and the `run_purges` audit table. The
   `runs` row, usage columns, `final_verdict`, branches, shared bundles, `run_jira` and scan rows
   are kept.
   Scan reports are not named by any requirement of this epic even though sibling epics delegate
   any scan retention rule here; that is a gap for epic/PRD review, not something these stories
   hide inside a scenario.
5. **Retention versus request.** Both paths use the same function and audit table; the only
   differences are the `reason`, whether `requested_by` is set, and the trigger (schedule versus
   API).
6. **Purge authorization.** NFR-014 says "on request" without naming an actor. This decomposition
   allows the run's author (`runs.user_id`) or the project owner; a different project member gets
   `run_purge_forbidden`. Epic BSB-22's membership and BSB-18's group gates run first. If review
   wants an operator-only purge, only the authorization check and its 403 body change.
7. **Terminal-only purge.** A `running` or `queued` run has in-flight logs, so a request returns
   `run_not_terminal`. The terminal set is BSB-26's (`completed`, `failed_infra`,
   `failed_execution`, `failed_incomplete`, `failed_timeout`) plus BSB-27's cap state, whose name is
   still open; scenarios use `completed` and `running` only.
8. **NULL usage.** A runtime that reports nothing leaves the usage columns `NULL` and the page
   says `Not reported`. The builder does not convert an unknown figure to zero.

## Cross-epic notes

- **BSB-18 and BSB-22.** Every route and page region here sits behind BSB-18's session and
  `skill-builders` gates and BSB-22's project resolution and membership check, with BSB-22's exact
  404 `project_not_found` and 403 `project_membership_required` bodies. This epic adds no
  membership rule of its own; the purge authorization check runs after those checks.
- **BSB-24.** Provides the run's `user_id`, which this epic uses for purge authorization, and the
  run page route's project path. This epic adds no run-creation field.
- **BSB-25.** Provides `skills_commit_sha` and the run prefix's location; retention never deletes
  the shared bundle under `bundles/` or the run branch.
- **BSB-26.** Owns the run row, the terminal-state vocabulary, the executor, the run page route and
  the progress and log APIs. This epic adds a usage read inside BSB-26's terminal write, a `purged`
  state to the log API response, and the purged progress state; it changes no other part of BSB-26's
  contract. BSB-26's log and progress APIs keep their exact unpurged bodies.
- **BSB-27.** Owns turn and spend caps and the deadline, including the state names it writes. Its
  supervisor is a terminal writer and must perform the same usage read and terminal transaction as
  BSB-26's executor. This epic never enforces or changes a cap or deadline; it persists whatever
  usage the runtime wrote before a cap or deadline stop.
- **BSB-29.** Declares `runs.verification` run-result data that this epic's purge must cover. The
  purge clears it and keeps `runs.final_verdict`; the run page must render a missing verification
  detail rather than an error after a purge.
- **BSB-31 and BSB-32.** Their scan rows are builder records and their stories delegate any
  retention, redaction or deletion rule here. This epic's requirements name only run transcripts,
  logs and results, so these stories neither retain nor delete `static_scans` or `llm_scans`. The
  delegation needs its own requirement before a scan-retention rule can be written.
- **BSB-33.** Owns the full run report and the rest of the run page. This epic owns only the
  `run-turns`, `run-tokens`, `run-cost`, `run-trace` and `run-evidence` regions; BSB-33's epic
  already excludes usage, cost and trace links from its scope. After a purge, BSB-33's report must
  read the preserved `runs` columns and render the `run-evidence` state instead of re-reading the
  deleted objects.
- **BSB-35.** Skill history and run comparison read the `runs` row after evidence is gone; the
  preserved usage columns and `final_verdict` keep those views meaningful. The purged verification
  detail is not recoverable.
- **BSB-37.** A CLI purge command is not required here; the purge API and the internal function are
  the operations this epic defines.
- **BSB-38.** The new run page regions are builder web surfaces, so their WCAG 2.1 AA and
  320-pixel reflow checks belong to BSB-38. This epic adds no separate accessibility requirement.

---

## STORY: BSB-34-PENDING-1

**Summary:** Record the run's turn count, token usage and cost from the runtime
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **skill author**, I want **the builder to persist my run's turn count, token usage and cost from the runtime**, so that **I can see what a run consumed even when it was interrupted before reporting a final result**.

### Acceptance Criteria

#### Scenario: A completed run's usage is persisted from the runtime report
Given run `1` is `running` with `claimed_verdict` = `completed` and its `turn_count`, `input_tokens`, `output_tokens` and `cost_usd` are `NULL`
And `s3://skill-builder-runs/runs/1/usage.json` contains exactly `{"turns":12,"input_tokens":12345,"output_tokens":6789,"cost_usd":0.0421,"updated_at":"2026-11-15T10:05:00Z"}`
When the executor performs run `1`'s terminal write, setting `state` = `completed`
Then `SELECT turn_count, input_tokens, output_tokens, cost_usd FROM runs WHERE id = 1` returns exactly `12 | 12345 | 6789 | 0.042100`
And `SELECT state, claimed_verdict, final_verdict, verification FROM runs WHERE id = 1` returns exactly `completed | completed | NULL | NULL`

#### Scenario: An interrupted run exposes the usage recorded before it stopped
Given run `6` is `running` and the deadline supervisor stops it at `2026-11-15T10:06:00Z`
And `s3://skill-builder-runs/runs/6/usage.json` contains exactly `{"turns":7,"input_tokens":8000,"output_tokens":4000,"cost_usd":0.021,"updated_at":"2026-11-15T10:05:58Z"}`
When the deadline supervisor performs run `6`'s terminal write, setting `state` = `failed_timeout`
Then `SELECT turn_count, input_tokens, output_tokens, cost_usd FROM runs WHERE id = 6` returns exactly `7 | 8000 | 4000 | 0.021000`
And `SELECT state, claimed_verdict FROM runs WHERE id = 6` returns exactly `failed_timeout | NULL`

#### Scenario: A run with no usage report leaves the usage columns unrecorded
Given run `5` is `running`
And `s3://skill-builder-runs/runs/5/usage.json` does not exist
When the executor performs run `5`'s terminal write, setting `state` = `failed_infra`
Then `SELECT turn_count, input_tokens, output_tokens, cost_usd FROM runs WHERE id = 5` returns exactly `NULL | NULL | NULL | NULL`
And `SELECT state FROM runs WHERE id = 5` returns `failed_infra`

#### Scenario: An invalid field does not discard the valid fields
Given run `4` is `running` and its usage columns are `NULL`
And `s3://skill-builder-runs/runs/4/usage.json` contains exactly `{"turns":-1,"input_tokens":12345,"output_tokens":6789,"cost_usd":0.0421,"updated_at":"2026-11-15T10:05:00Z"}`
When the executor performs run `4`'s terminal write, setting `state` = `completed`
Then `SELECT turn_count, input_tokens, output_tokens, cost_usd FROM runs WHERE id = 4` returns exactly `NULL | 12345 | 6789 | 0.042100`
And `SELECT state FROM runs WHERE id = 4` returns `completed`

### Covered requirements (traceability)
- NFR-015
- NFR-016
- NFR-017

### Out of scope
Showing the figures on the run page (BSB-34-PENDING-2). Enforcing a turn or spend cap or a deadline, and naming the cap terminal state (epic BSB-27). Computing, estimating or back-filling usage the runtime did not report. Cost for a re-verify run, which starts no runtime and reports no usage (epic BSB-30). The live cost meter itself (epic BSB-27).

### Notes / dependencies
- Depends on epic BSB-26 for the run row and the executor, and on epic BSB-27 for the deadline and
  cap supervisor. "Terminal writer" means whichever of those two components ends the run; both must
  read `usage.json` and persist the usage columns in the same transaction as the terminal state.
- The runtime refreshes `usage.json` after every completed model turn; the terminal writer's read
  takes the last completed write, so a force-terminated run persists the turns, tokens and cost it
  had actually reported.
- The usage columns are additive fields that BSB-26 and BSB-29 do not write. Persisting them must
  not use a compare-and-set on `state`, and must not be a second update after the terminal write:
  a purge could otherwise delete `usage.json` between the two writes.

---

## STORY: BSB-34-PENDING-2

**Summary:** Show the run's turns, tokens and cost on the run page
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-13, MVP

### Story
As a **skill author**, I want **the run page to show my run's turns, tokens and cost**, so that **I can judge a skill's effort and cost without reading its logs**.

### Acceptance Criteria

#### Scenario: The run page shows recorded turns, tokens and cost
Given run `1` is `completed` with `turn_count` = `12`, `input_tokens` = `12345`, `output_tokens` = `6789` and `cost_usd` = `0.042100`
And Ada is a member of project `7`
When Ada requests `GET https://builder.skillbuilder.internal/projects/7/runs/1` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the page contains `<div id="run-turns">Turns: 12</div>`
And the page contains `<div id="run-tokens">Tokens: 19134 (12345 in, 6789 out)</div>`
And the page contains `<div id="run-cost">Cost: $0.042100</div>`

#### Scenario: Zero usage is shown as zero, not as missing
Given run `2` is `completed` with `turn_count` = `0`, `input_tokens` = `0`, `output_tokens` = `0` and `cost_usd` = `0.000000`
And Ada is a member of project `7`
When Ada requests `GET https://builder.skillbuilder.internal/projects/7/runs/2` carrying the `sb_session` cookie
Then the page contains `<div id="run-turns">Turns: 0</div>`
And the page contains `<div id="run-tokens">Tokens: 0 (0 in, 0 out)</div>`
And the page contains `<div id="run-cost">Cost: $0.000000</div>`

#### Scenario: A run with no usage report shows Not reported in each region
Given run `5` is `failed_infra` with `turn_count`, `input_tokens`, `output_tokens` and `cost_usd` all `NULL`
And Ada is a member of project `7`
When Ada requests `GET https://builder.skillbuilder.internal/projects/7/runs/5` carrying the `sb_session` cookie
Then the response is HTTP 200
And the page contains `<div id="run-turns">Turns: Not reported</div>`
And the page contains `<div id="run-tokens">Tokens: Not reported</div>`
And the page contains `<div id="run-cost">Cost: Not reported</div>`

#### Scenario: Usage remains visible after the run's evidence is purged
Given run `4` is `completed` with `turn_count` = `12`, `input_tokens` = `12345`, `output_tokens` = `6789`, `cost_usd` = `0.042100` and `evidence_purged_at` = `2026-11-15T12:00:00Z`
And Ada is a member of project `7`
When Ada requests `GET https://builder.skillbuilder.internal/projects/7/runs/4` carrying the `sb_session` cookie
Then the page contains `<div id="run-turns">Turns: 12</div>`
And the page contains `<div id="run-tokens">Tokens: 19134 (12345 in, 6789 out)</div>`
And the page contains `<div id="run-cost">Cost: $0.042100</div>`

### Covered requirements (traceability)
- FR-102
- FR-159
- FR-160

### Out of scope
Recording the figures (BSB-34-PENDING-1). The trace link (BSB-34-PENDING-3). The purged-evidence message and the removed log region (BSB-34-PENDING-4). Any cross-run analytics, comparison or aggregate spend view (epic BSB-35's non-goal here). The rest of the run report (epic BSB-33).

### Notes / dependencies
- Depends on BSB-34-PENDING-1 for the columns and on epic BSB-26 for the run page route, its
  session and membership gates, and the existing page shell.
- The three values are independent: each region follows its own column, so a partially reported run
  shows a value in one region and `Not reported` in another.
- The token total is `input_tokens + output_tokens`; the page shows the two components in
  parentheses so a large input-only run is visible as such.
- Cost is formatted from `numeric(12,6)` with exactly six decimal places and a leading `$`; the
  builder never recomputes it from tokens.

---

## STORY: BSB-34-PENDING-3

**Summary:** Link each traced run to a test-environment trace
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **skill author**, I want **the run page to link to the run's trace, tagged as a test-environment run**, so that **I can debug the run in the trace store and never mistake builder data for production data**.

### Acceptance Criteria

#### Scenario: Tracing enabled creates one test-environment trace and links it from the run page
Given `SKILL_BUILDER_TRACING_ENABLED` is `true`
And `LANGFUSE_HOST` is `https://langfuse.skillbuilder.internal` and `LANGFUSE_PROJECT_ID` is `skill-builder`
And the trace-store stub records every request to `/api/public/traces`
And run `1` is prepared and `state` = `queued`
When the executor claims run `1` at `2026-11-15T10:01:00Z`
Then the stub received exactly one `POST https://langfuse.skillbuilder.internal/api/public/traces`
And that request's JSON body is exactly `{"id":"run-1","name":"run-1","metadata":{"env":"skilltest","run_id":"1","project_id":"7","skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b"}}`
And `SELECT trace_id, trace_url FROM runs WHERE id = 1` returns exactly `run-1 | https://langfuse.skillbuilder.internal/project/skill-builder/traces/run-1`
And the run page contains `<a id="run-trace" href="https://langfuse.skillbuilder.internal/project/skill-builder/traces/run-1">Open trace</a>`

#### Scenario: Each claimed run gets its own trace
Given `SKILL_BUILDER_TRACING_ENABLED` is `true` and the trace-store stub records every request to `/api/public/traces`
And runs `1` and `2` are prepared and `state` = `queued`
When the executor claims run `1` and then run `2`
Then the stub received exactly two trace requests, with ids `run-1` and `run-2`
And each request's `metadata.run_id` equals the id suffix of its trace id
And each request's `metadata.env` is `skilltest`
And `SELECT id, trace_id FROM runs WHERE id IN (1, 2) ORDER BY id` returns exactly `1 | run-1` and `2 | run-2`

#### Scenario: Tracing disabled creates no trace and shows no trace link
Given `SKILL_BUILDER_TRACING_ENABLED` is `false`
And the trace-store stub records every request to `/api/public/traces`
And run `1` is prepared and `state` = `queued`
When the executor claims run `1`
Then the stub received no trace request
And `SELECT trace_id, trace_url FROM runs WHERE id = 1` returns exactly `NULL | NULL`
And the run page has no element with id `run-trace`
And the run page does not contain the text `Open trace`

#### Scenario: A trace-store failure does not block or fail the run
Given `SKILL_BUILDER_TRACING_ENABLED` is `true`
And the trace-store stub responds to every trace request with HTTP 500
And run `1` is prepared and `state` = `queued`
When the executor claims run `1`
Then within 2 seconds `SELECT state FROM runs WHERE id = 1` returns `running`
And exactly one agent container labelled `bb.run_id` = `1` has started
And `SELECT trace_id, trace_url FROM runs WHERE id = 1` returns exactly `NULL | NULL`
And the run page contains `<div id="run-trace">Trace unavailable.</div>`
And the run page does not contain the text `Open trace`

### Covered requirements (traceability)
- FR-103
- NFR-011

### Out of scope
Recording or showing the trace's spans, token usage or model calls (the trace store and the platform agent image own those; usage is BSB-34-PENDING-1). Deleting the external trace when run evidence is purged (BSB-34-PENDING-4 and BSB-34-PENDING-5 keep the trace; the trace store's own retention governs it). Tracing a re-verify run, which starts no runtime (epic BSB-30). The trace store's own UI and project administration.

### Notes / dependencies
- Depends on epic BSB-26 for the claim point, the run row and the container launch, and on the
  external trace store named in the PRD's prerequisites. When tracing is enabled and the store is
  unavailable, tracing is observability only: the run still starts and its state is unchanged.
- The trace metadata carries `env` = `skilltest` so the trace identifies itself as a
  test-environment run (NFR-011); `run_id`, `project_id`, `skill` and `skills_commit_sha` make the
  trace findable from the run and the run findable from the trace.
- The id is deterministic, so a retried claim cannot create a second trace for the same run. If the
  trace already exists, the trace store's idempotent write is accepted; the run row keeps the same
  id and URL.
- The public and secret keys are sent only in the HTTP Basic header and are never logged or stored
  on the run (NFR-004).

---

## STORY: BSB-34-PENDING-4

**Summary:** Retain run evidence for the configured period and purge it when it expires
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **platform operator**, I want **run transcripts, logs and results retained only for the installation's configured period, three months by default**, so that **sensitive test content has a defined lifecycle and the period is changed by configuration rather than code**.

### Acceptance Criteria

#### Scenario: The default retention period of three months purges expired evidence and keeps newer evidence
Given `SKILL_BUILDER_RETENTION_MONTHS` is unset
And run `11` is `completed`, created at `2026-08-14T10:00:00Z`, with `turn_count` = `12`, `cost_usd` = `0.042100`, `verification` containing `"status":"passed"` and the five evidence objects under `runs/11/`
And run `12` is `completed`, created at `2026-08-16T10:00:00Z`, with `verification` containing `"status":"passed"` and the five evidence objects under `runs/12/`
And `run_purges` is empty
When the retention sweep runs at `2026-11-15T03:00:00Z`
Then no object whose key starts with `runs/11/` exists in `skill-builder-runs`
And `SELECT verification, evidence_purged_at, turn_count, cost_usd FROM runs WHERE id = 11` returns exactly `NULL | 2026-11-15T03:00:00Z | 12 | 0.042100`
And every object whose key starts with `runs/12/` still exists
And `SELECT verification->>'status', evidence_purged_at FROM runs WHERE id = 12` returns exactly `passed | NULL`
And `SELECT reason, requested_by, status, objects, verification_cleared FROM run_purges WHERE run_id = 11` returns exactly `retention | NULL | completed | ["runs/11/agent.log","runs/11/bb_step_result.json","runs/11/progress.json","runs/11/transcript.jsonl","runs/11/usage.json"] | true`
And `SELECT count(*) FROM run_purges WHERE run_id = 12` returns `0`

#### Scenario: A configured period overrides the default
Given `SKILL_BUILDER_RETENTION_MONTHS` is `1`
And run `13` is `completed`, created at `2026-10-14T10:00:00Z`, with the five evidence objects under `runs/13/`
And run `14` is `completed`, created at `2026-10-16T10:00:00Z`, with the five evidence objects under `runs/14/`
When the retention sweep runs at `2026-11-15T03:00:00Z`
Then no object whose key starts with `runs/13/` exists
And every object whose key starts with `runs/14/` still exists
And `SELECT evidence_purged_at FROM runs WHERE id = 13` returns `2026-11-15T03:00:00Z`
And `SELECT evidence_purged_at FROM runs WHERE id = 14` returns `NULL`

#### Scenario: An already purged run is skipped
Given run `11` has `evidence_purged_at` = `2026-11-15T03:00:00Z` and no objects under `runs/11/`
And `run_purges` contains exactly one `completed` row for run `11`
When the retention sweep runs again at `2026-11-16T03:00:00Z`
Then `SELECT evidence_purged_at FROM runs WHERE id = 11` returns `2026-11-15T03:00:00Z`
And `SELECT count(*) FROM run_purges WHERE run_id = 11` returns `1`

#### Scenario: An invalid retention configuration stops the builder instead of guessing
Given `SKILL_BUILDER_RETENTION_MONTHS` is `abc`
When the builder starts
Then the builder exits with status `1`
And its standard error contains exactly `[skill-builder] invalid SKILL_BUILDER_RETENTION_MONTHS: must be a positive integer`
And no retention sweep runs

#### Scenario: A purged run still renders its preserved report regions and reports the purge
Given run `11` was purged by the retention sweep at `2026-11-15T03:00:00Z`
And run `11` has `state` = `completed`, `turn_count` = `12`, `input_tokens` = `12345`, `output_tokens` = `6789`, `cost_usd` = `0.042100` and `final_verdict` = `completed`
And Ada is a member of project `7`
When Ada requests the run page, the log API and the progress API for run `11` with the `sb_session` cookie
Then the run page is HTTP 200 and contains `<div id="run-evidence">Run transcripts, logs and results were purged on 2026-11-15T03:00:00Z.</div>`
And the run page has no element with id `run-log`
And the run page contains `<div id="run-turns">Turns: 12</div>`, `<div id="run-tokens">Tokens: 19134 (12345 in, 6789 out)</div>` and `<div id="run-cost">Cost: $0.042100</div>`
And the log API returns exactly `{"run_id":11,"lines":[],"truncated":false,"purged":true}`
And the progress API returns exactly `{"run_id":11,"step":null,"state":"completed","message":null,"percent":0,"updated_at":null}`

### Covered requirements (traceability)
- NFR-013
- NFR-018

### Out of scope
The on-request purge API and its authorization (BSB-34-PENDING-5). Deleting the `runs` row, its usage columns, `final_verdict`, branch, shared bundle, `run_jira` record or scan rows. Deleting the external trace (the trace store's own retention). A per-run override of the installation period (the epic's non-goal). Retention and deletion rules for scan records (no requirement in this epic). Analytics across runs beyond a single run (the epic's non-goal).

### Notes / dependencies
- Depends on BSB-34-PENDING-1 for the usage columns that survive the purge and on
  BSB-34-PENDING-5 for the shared `purge_run_evidence` operation and the `run_purges` audit table.
  The sweep is the scheduled caller; the request API is the manual caller.
- The cutoff is calendar months, not days: at `2026-11-15T03:00:00Z` the three-month cutoff is
  `2026-08-15T03:00:00Z`, so the run created on `2026-08-14` is older than the cutoff and the run
  created on `2026-08-16` is not.
- The sweep deletes every object under `runs/<run_id>/`, so any future object the builder adds to a
  run prefix is covered without another retention rule. Objects outside the prefix, including the
  shared bundle, are never touched.
- `runs.verification` is cleared because epic BSB-29 declares it run-result data; `final_verdict`
  is kept so the run report, skill history and comparison views still have a verdict.
- An invalid value fails fast because a silent fallback could either never purge or purge
  everything. A missing variable uses the three-month default.

---

## STORY: BSB-34-PENDING-5

**Summary:** Purge a run's evidence on request and audit the purge
**Epic:** BSB-34 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **skill author**, I want **to purge a run's transcripts, logs and results on request**, so that **I can remove sensitive test content without deleting the run's history or losing the audit trail**.

### Acceptance Criteria

#### Scenario: The run's author purges its evidence
Given Ada is a member of project `7`
And run `1` is `completed`, `user_id` = `42`, with `verification` containing `"status":"passed"` and the five evidence objects under `runs/1/`
And `run_purges` is empty
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/1/purge` with the `sb_session` cookie and an empty body at `2026-11-15T12:00:00Z`
Then the response is HTTP 200 with `Content-Type: application/json`
And the response body is exactly `{"run_id":1,"purged_at":"2026-11-15T12:00:00Z","objects_deleted":5,"verification_cleared":true,"already_purged":false}`
And no object whose key starts with `runs/1/` exists in `skill-builder-runs`
And `SELECT verification, evidence_purged_at FROM runs WHERE id = 1` returns exactly `NULL | 2026-11-15T12:00:00Z`
And `SELECT reason, requested_by, status, objects, verification_cleared FROM run_purges WHERE run_id = 1` returns exactly `request | 42 | completed | ["runs/1/agent.log","runs/1/bb_step_result.json","runs/1/progress.json","runs/1/transcript.jsonl","runs/1/usage.json"] | true`
And the run page contains `<div id="run-evidence">Run transcripts, logs and results were purged on 2026-11-15T12:00:00Z.</div>` and has no element with id `run-log`
And the log API returns exactly `{"run_id":1,"lines":[],"truncated":false,"purged":true}`

#### Scenario: The project owner purges another member's run
Given Ada is the owner of project `7` and is not the author of run `2`
And run `2` is `completed`, `user_id` = `43`, with `verification` containing `"status":"passed"` and the five evidence objects under `runs/2/`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/2/purge` with the `sb_session` cookie and an empty body at `2026-11-15T12:01:00Z`
Then the response is HTTP 200 with body exactly `{"run_id":2,"purged_at":"2026-11-15T12:01:00Z","objects_deleted":5,"verification_cleared":true,"already_purged":false}`
And no object whose key starts with `runs/2/` exists
And `SELECT reason, requested_by, status FROM run_purges WHERE run_id = 2` returns exactly `request | 42 | completed`

#### Scenario: A project member who is neither the author nor the owner cannot purge
Given Grace is a member of project `7` with `role` = `member` and is not the author of run `1`
And run `1` is `completed`, `user_id` = `42`, with `verification` containing `"status":"passed"` and the five evidence objects under `runs/1/`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/1/purge` with the `sb_session` cookie and an empty body
Then the response is HTTP 403
And the response body is exactly `{"error":{"code":"run_purge_forbidden","message":"Only the run's author or the project owner can purge this run."}}`
And every object whose key starts with `runs/1/` still exists
And `SELECT verification->>'status', evidence_purged_at FROM runs WHERE id = 1` returns exactly `passed | NULL`
And `SELECT count(*) FROM run_purges WHERE run_id = 1` returns `0`

#### Scenario: A non-terminal run cannot be purged
Given Ada is a member of project `7` and the author of run `3`
And run `3` is `running`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/3/purge` with the `sb_session` cookie and an empty body
Then the response is HTTP 409
And the response body is exactly `{"error":{"code":"run_not_terminal","message":"Run 3 is not in a terminal state and cannot be purged."}}`
And `SELECT state, evidence_purged_at FROM runs WHERE id = 3` returns exactly `running | NULL`
And `SELECT count(*) FROM run_purges WHERE run_id = 3` returns `0`

#### Scenario: Purging an already purged run is idempotent
Given Ada is a member of project `7` and the author of run `1`
And run `1` was purged at `2026-11-15T12:00:00Z`, has no objects under `runs/1/`, and `run_purges` contains exactly one `completed` row for run `1`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/1/purge` with the `sb_session` cookie and an empty body at `2026-11-15T12:05:00Z`
Then the response is HTTP 200 with body exactly `{"run_id":1,"purged_at":"2026-11-15T12:00:00Z","objects_deleted":0,"verification_cleared":false,"already_purged":true}`
And `SELECT evidence_purged_at FROM runs WHERE id = 1` returns `2026-11-15T12:00:00Z`
And `SELECT count(*) FROM run_purges WHERE run_id = 1` returns `1`

#### Scenario: A purge that cannot delete the evidence leaves the run unchanged
Given Ada is a member of project `7` and the author of run `4`
And run `4` is `completed` with `verification` containing `"status":"passed"` and the five evidence objects under `runs/4/`
And the object-store stub returns HTTP 500 for the multi-object delete
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/4/purge` with the `sb_session` cookie and an empty body at `2026-11-15T12:06:00Z`
Then the response is HTTP 502
And the response body is exactly `{"error":{"code":"purge_failed","message":"Run evidence could not be purged."}}`
And every object whose key starts with `runs/4/` still exists
And `SELECT verification->>'status', evidence_purged_at FROM runs WHERE id = 4` returns exactly `passed | NULL`
And `SELECT reason, requested_by, status, objects, verification_cleared, error FROM run_purges WHERE run_id = 4` returns exactly `request | 42 | failed | [] | false | object_store_error`

### Covered requirements (traceability)
- NFR-014

### Out of scope
The scheduled retention sweep, its configuration and its default (BSB-34-PENDING-4). Purging a queued or running run. Purging the external trace (the trace store's own retention), the `runs` row, its usage columns, `final_verdict`, branch, shared bundle, `run_jira` record or scan rows. A CLI purge command (epic BSB-37). Bulk purge across runs or projects, and a user-facing purge history page. Redaction rules for scan records (no requirement in this epic).

### Notes / dependencies
- Depends on BSB-34-PENDING-4 for the shared `purge_run_evidence` operation and the `run_purges`
  table, and on epics BSB-18 and BSB-22 for the session, group, project and membership checks that
  run before this story's authorization check.
- The authorization check reads `runs.user_id` and the caller's `project_members.role` for the run's
  project. A caller who fails either check is denied; the check does not reveal whether the run
  exists to a non-member because BSB-22's membership check runs first.
- The purge deletes every object under the run prefix, so it covers the transcript, log, progress,
  result and usage files together. The multi-object delete is one call; an error leaves the run's
  database fields and `evidence_purged_at` unchanged and records a `failed` audit row.
- A second request after a successful purge returns the original `purged_at`, reports
  `already_purged` = `true`, deletes nothing and inserts no second audit row.
- The response's `objects_deleted` is the number of keys the object store confirmed deleted; it is
  `0` for an already-purged run and for a failed attempt.
