# Stories — BSB-28 (Jira fixture seeding)

Source: Jira epic **BSB-28** — *Jira fixture seeding* (feature area FA-9, release Later, labels
FA-9, Later), fetched read-only from the Atlassian project `bheembhai-skill-builder`; its summary,
description, functional scope, goal and stated edge cases are the same as the BSB-28 section of
`docs/product/epics.md`. The requirement IDs mapped to the epic are in
`docs/product/epic-map.json`.

Epic BSB-28 covers 5 requirements. They decompose into the 5 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. This run's item, from the workflow context (`ITEM.id` = `BSB-28`), is epic
**BSB-28**. The Atlassian MCP server was not connected in this session (no Jira MCP tools were
offered, and `.mcp.json` declares `args` as a string), so BSB-28 was fetched read-only through the
Atlassian REST API: summary *Jira fixture seeding*, type Epic, labels `FA-9` and `Later`, status
*To Do*, and a description that matches the BSB-28 section of `docs/product/epics.md`. Nothing was
written to Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-058 | BSB-28-PENDING-1 |
| FR-059 | BSB-28-PENDING-2 |
| FR-060 | BSB-28-PENDING-3 |
| FR-061 | BSB-28-PENDING-4 |
| FR-062 | BSB-28-PENDING-5 |

The epic's three stated edge cases are covered explicitly: a partially seeded fixture rolls back
what it created (BSB-28-PENDING-1), a fixture that names an issue that already exists fails
without deleting it (BSB-28-PENDING-1), and cleanup and the nightly sweep are both idempotent
(BSB-28-PENDING-4 and BSB-28-PENDING-5). The epic's non-goals — no mutation of issues the run did
not seed, and no fixture authoring UI — are carried by BSB-28-PENDING-1 and BSB-28-PENDING-4.

## Jira fixture contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control and Jira fixture
unless it says otherwise. The member session, the local `users` rows and the `skill-builders` gate
are established by epic BSB-18. The project, `projects` rows and `project_members` rows are
established by epic BSB-22. The Jira integration is established by epic BSB-23. The prepared run —
the `runs` row with `skills_commit_sha` and `run_branch` set, the `skill_bundles` row, and the run
branch `skilltest/1` — is the output of epic BSB-25 (FR-038 to FR-043); this epic consumes it. The
executor claim path, the terminal-write rule and the run state vocabulary are epic BSB-26's. The
`runs` and `run_jira` columns follow `docs/adr/SK-001-skill-builder.md` §5 and §9.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42`, `created_at` = `2026-11-14T09:00:00Z`; ids `1` to `6`, `8`, `9` and `10` are unrelated fixture projects with no `jira` integration |
| `project_members` fixture | exactly two rows: `(project_id 7, user_id 42, role owner)` and `(project_id 7, user_id 43, role member)` |
| `jira` integration (project 7) | row `id` = `5`, `project_id` = `7`, `kind` = `jira`, `config` = `{"site_url":"https://old.atlassian.net","project_key":"OLD","fixture":"bug-fix-empty-title"}`, `secret_ref` = `skill-builder/7/jira`, `mcp` = `null`, `verified_at` = `2026-11-14T09:00:00Z` |
| Jira credentials | the secret held at `skill-builder/7/jira` has exactly the keys `email` = `builder-tests@example.com` and `api_token` = `test-jira-token-7d1f`; every Jira request carries HTTP Basic authorization built from them; neither value appears in the database, the run log or a response body |
| Run 1 (the prepared run) | exactly one row: `id` = `1`, `project_id` = `7`, `user_id` = `42`, `skill` = `sdlc-fix-bug-triage`, `skills_ref` = `test/ada/fix-reproduce`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `input_branch` = `main`, `run_branch` = `skilltest/1`, `context` = `{"workflow":"bug-fix","step":"triage"}`, `model_profile_id` = `3`, `tier` = `high`, `state` = `queued`, `kind` = `run`, `created_at` = `2026-11-15T10:00:00Z`; `agent_image_digest`, `stepkit_version`, `verify_version`, `claimed_verdict`, `final_verdict`, `verification`, `cost_usd` and `parent_run_id` are `NULL` |
| `skill_bundles` row | `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `skill` = `sdlc-fix-bug-triage`, `bundle_sha256` = `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`, `s3_key` = `bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz` |
| Skills commit fixture | the commit `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` of `test/ada/fix-reproduce` in `saraavrnd/bheembhai-skills` contains `fixtures/bug-fix-empty-title/jira.json` with exactly the content below |
| Fixture file contents | see the JSON block below this table |
| Jira test site | `https://old.atlassian.net` is served by a stub that records every request as `(method, path, body)` in arrival order and returns the responses named in each scenario |
| Jira project `OLD` initial issues | exactly one issue `OLD-100`, `summary` = `Manual onboarding checklist`, `status` = `To Do`, `labels` = `[]`; the next issue number the stub hands out is `101`, then `102` |
| Run marker | the label `skilltest-1` for run `1` |
| Fixture after seeding | issues `OLD-101` (alias `bug`) and `OLD-102` (alias `task`); both carry `labels` = `["skilltest-1"]` and `status` = `To Do`; `OWL` never appears |
| Current time | `2026-11-15T10:00:00Z` before the claim; run `1` is claimed at `2026-11-15T10:01:00Z`; seeding completes at `2026-11-15T10:01:02Z`; the run's terminal state is written at `2026-11-15T10:05:00Z`; cleanup completes at `2026-11-15T10:05:01Z`; the nightly sweep runs at `2026-11-16T02:00:00Z` |

The fixture file `fixtures/bug-fix-empty-title/jira.json` is exactly:

```json
{
  "issues": [
    {
      "alias": "bug",
      "issue_type": "Bug",
      "summary": "Checkout fails when the cart is empty",
      "description": "The checkout button does nothing. Tracking issue: @task@."
    },
    {
      "alias": "task",
      "issue_type": "Task",
      "summary": "Investigate empty-cart checkout failure",
      "description": "Found while reproducing @bug@."
    }
  ]
}
```

**Fixture selection and enablement.** The fixture is a project-level setting on the project's
`jira` integration: `config.fixture` names the fixture directory, and an absent or `null` value
means seeding is disabled. The run marker and every later operation key off the run ID, not the
fixture name. This placement is an explicit decision of this decomposition, not a requirement; it
is recorded under **Open decisions** below. A Jira integration configured with a template project
and no `project_key` has no configured project to seed into; fixture seeding is defined only for
`project_key` integrations and that combination is out of scope.

**Fixture file format.** The file is a JSON object with one required key, `issues`, whose value is
an array. Each entry has a required `alias` (unique in the file), `issue_type` and `summary`, and an
optional `description` and `key`. An alias reference is written `@alias@`; the ADR expresses the
same illustrative alias in a double-brace form, and the delimiter is the only difference — the
semantics are the ADR's: the token is replaced with the created key at seed time. Only `summary`
and `description` values may contain alias references.

**Seeding lifecycle.** Seeding runs in the executor's claim path after the claim compare-and-set
and after the provenance values are written, and before the container is created. A run whose
project has no `jira` integration or no `config.fixture` is not seeded at all: no Jira request is
sent, no `run_jira` row is created, and the run starts exactly as BSB-26 describes. When seeding is
enabled, the builder validates the fixture and then creates the issues; a successful seed inserts
the `run_jira` row. If any step fails, the builder deletes every issue it created for this run's
marker, leaves no `run_jira` row, writes no container, and moves the run to the terminal state
`failed_seed` with `claimed_verdict` `NULL`, using BSB-26's terminal-write rule.

**Alias replacement.** Seeding is two-phase. Phase 1 creates every fixture issue in file order,
carrying its raw `summary` and `description` and the marker label. Once every issue exists, phase 2
resolves `@alias@` tokens: the builder sends one `PUT` per issue whose `summary` or `description`
contains a token, with the resolved values. The alias mapping is stored as `run_jira.aliases`, a
JSON object whose keys are the fixture aliases and whose values are the created keys, in fixture
order.

**Post-run state capture.** The builder's Jira finalizer runs once immediately after the executor
writes a terminal `runs.state`, before epic BSB-29 verifies the run. It first captures the post-run
state and then cleans up. The capture reads every key in `run_jira.aliases` in fixture order and
stores `run_jira.state_after` as a JSON object with one `issues` array, in fixture order:

```json
{"issues":[{"alias":"bug","key":"OLD-101","status":"In Progress","summary":"Checkout fails when the cart is empty"},{"alias":"task","key":"OLD-102","status":"Done","summary":"Investigate empty-cart checkout failure"}]}
```

A key the Jira site reports as absent is recorded as
`{"alias":"task","key":"OLD-102","status":null,"summary":null,"missing":true}`. If any other read
fails, the capture is abandoned, `state_after` stays `NULL`, and the failure is logged; cleanup
still runs. A run with no `run_jira` row has nothing to capture or clean up, and the finalizer is a
no-op.

**Cleanup.** Cleanup deletes only the issues recorded in `run_jira.aliases`, in fixture order, and
only while each issue still carries the run's marker label. For each recorded key it reads
`fields=labels`; a key the site reports absent is treated as already cleaned; a key whose labels
do not contain the marker is skipped and logged; otherwise it sends `DELETE`. Cleanup is
all-or-nothing on errors: an unexpected Jira error on any read or delete leaves other issues in
place where possible, leaves `run_jira.cleaned_at` `NULL`, and logs the failure, so the nightly
sweep or a retry can finish the job. When every recorded key is deleted or already absent,
`cleaned_at` is set to the completion time. A second invocation after that sends no delete and
leaves `cleaned_at` unchanged.

**Nightly sweep.** An installation-level scheduled job runs every day at `02:00` UTC. It iterates
every project that has a `jira` integration and searches that integration's configured
`project_key` for issues with at least one label, paging `maxResults=100` until it has read every
result. It selects issues carrying a label that matches exactly the regular expression
`^skilltest-[0-9]+$`. For each such issue it derives the run ID from the label; if a `runs` row
with that ID exists and its `state` is `queued` or `running`, the issue is skipped so an active run
never loses its fixture. Every other marked issue is deleted, including one whose run row no
longer exists. When the sweep deletes at least one issue for a run that has a `run_jira` row with
`cleaned_at` `NULL`, it sets that `cleaned_at` to the sweep time. Issues without a marker label are
never deleted. The sweep is idempotent: a second run deletes nothing that the first removed.

**Jira API contract.** Each call is made against the integration's `config.site_url` with the
credentials held at its `secret_ref`, and each JSON request has `Content-Type: application/json`.

| Operation | Request |
|-----------|---------|
| Create an issue | `POST https://old.atlassian.net/rest/api/2/issue` |
| Update an issue | `PUT https://old.atlassian.net/rest/api/2/issue/{key}` |
| Read summary and status | `GET https://old.atlassian.net/rest/api/2/issue/{key}?fields=summary,status` |
| Read labels | `GET https://old.atlassian.net/rest/api/2/issue/{key}?fields=labels` |
| Delete an issue | `DELETE https://old.atlassian.net/rest/api/2/issue/{key}` |
| Search the project | `GET https://old.atlassian.net/rest/api/2/search?jql=project%3D%22OLD%22%20AND%20labels%20is%20not%20EMPTY&fields=labels,status,summary&maxResults=100&startAt=0` |

A create returns `201` with a body of the form `{"id":"10001","key":"OLD-101"}`. An update and a
delete return `204` with no body. A read returns `200` with a body of the form
`{"key":"OLD-101","fields":{"summary":"Checkout fails when the cart is empty","status":{"name":"In Progress"}}}`.
Any other status is an error: the builder logs it but never copies the authorization header or a
credential value into the log or the database. A failure log line has the exact prefix
`[skill-builder] jira fixture seed failed: ` for seeding, `[skill-builder] jira state capture
failed: ` for capture, and `[skill-builder] jira cleanup failed: ` for cleanup.

**Run state values.** This epic sets exactly one `runs.state` value, `failed_seed`: the Jira
fixture could not be validated or seeded, no container was created, and `claimed_verdict` is
`NULL`. Every other state these stories read (`queued`, `running`, `completed`, the failure states
and the sibling-owned terminal values) belongs to epics BSB-24 to BSB-27.

**Open decisions (flagged for review — no requirement answers them).**

1. *Where the fixture is chosen.* No requirement says whether a fixture is chosen per run or per
   project, or where its name is configured. This decomposition pins it as `config.fixture` on the
   project's `jira` integration, because FR-058 says "the project's configured Jira project" and
   the PRD says "when Jira fixture seeding is enabled". If review decides the fixture is instead a
   run-start input, only the source of the fixture name changes; the marker, file format, seeding,
   capture, cleanup and sweep do not.
2. *The alias token delimiter.* The ADR's example uses a double-brace token; this epic pins
   `@alias@` for the fixture file. If the double-brace form is mandatory, only the delimiter
   changes in the fixture parser and in the scenarios of BSB-28-PENDING-2.
3. *Template-project integrations.* FR-029 allows a Jira integration with a template project
   instead of a project key. This epic seeds only into a `project_key` integration and leaves the
   template-project case out of scope.
4. *Re-runs.* FR-056 (epic BSB-27) re-runs a run with the same inputs. Because the fixture is
   project-level here, a re-run uses the project's current fixture; if exact reproduction is
   required, the fixture name must be recorded per run, which this epic does not add to
   `run_jira` or `runs`.

**Cross-epic notes.**

- **BSB-23 (integrations).** Epic BSB-23 owns the `integrations` table and the Jira integration
  settings. This epic adds one optional key to that integration's `config`, `fixture`.
  BSB-23 has no stories yet, so its decomposition must include `config.fixture`, its absent/`null`
  meaning, and the rule that seeding applies only to integrations with a `project_key`. The
  `site_url`, `project_key` and `secret_ref` meanings are unchanged.
- **BSB-24, BSB-25 and BSB-26 (run lifecycle).** The run-start route (BSB-24), the prepared run
  (BSB-25) and the claim and terminal-write rules (BSB-26) are consumed, not changed. Seeding adds
  one step to BSB-26's claim path between provenance persistence and container creation, and adds
  the terminal state `failed_seed` to the state vocabulary. BSB-26's state table and failure text
  must gain that row in a later revise pass; this epic does not edit BSB-26's files. No BSB-26
  scenario has a Jira integration with `config.fixture`, so those scenarios are unchanged.
- **BSB-27 (guardrails and re-runs).** Epic BSB-27 owns `failed_timeout`, the cap-stop states and
  re-runs. The finalizer runs for every terminal state, including BSB-27's, so a timed-out run's
  seeded issues are still captured and cleaned up. Re-runs are covered by Open decision 4.
- **BSB-33 (run report).** Epic BSB-33 owns FR-140's durable record of the Jira changes a run
  makes and their display. This epic records `run_jira.state_after` for fixture assertions only;
  it does not compute a diff and does not add a run page region.
- **BSB-38 (accessibility).** No web surface is added by this epic, so no NFR-012 scenario exists
  here. The failure text BSB-26 shows for `failed_seed` is BSB-26's surface.

## STORY: BSB-28-PENDING-1

**Summary:** Seed a run's Jira fixture as run-marked issues
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-9, Later

### Story
As a **skill author**, I want **a run to seed its project's Jira fixture as issues marked with the run's ID**, so that **the skill under test starts against realistic tracker data that the builder can always identify and remove**.

### Acceptance Criteria

#### Scenario: Claiming a run seeds its fixture as marked issues
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `jira` integration row `5` has `config` = `{"site_url":"https://old.atlassian.net","project_key":"OLD","fixture":"bug-fix-empty-title"}`
And run `1` exists prepared with `state` = `queued` and `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the Jira stub's project `OLD` contains only issue `OLD-100` and its next issue number is `101`
And `SELECT count(*) FROM run_jira` returns `0`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1` at `2026-11-15T10:01:00Z`
Then the Jira stub records exactly two `POST /rest/api/2/issue` requests, in this order
And the first request body is exactly `{"fields":{"project":{"key":"OLD"},"issuetype":{"name":"Bug"},"summary":"Checkout fails when the cart is empty","description":"The checkout button does nothing. Tracking issue: @task@.","labels":["skilltest-1"]}}`
And the second request body is exactly `{"fields":{"project":{"key":"OLD"},"issuetype":{"name":"Task"},"summary":"Investigate empty-cart checkout failure","description":"Found while reproducing @bug@.","labels":["skilltest-1"]}}`
And the Jira stub contains exactly three issues: `OLD-100` with `labels` = `[]`, `OLD-101` with `labels` = `["skilltest-1"]`, and `OLD-102` with `labels` = `["skilltest-1"]`
And `SELECT aliases FROM run_jira WHERE run_id = 1` equals the JSON value `{"bug":"OLD-101","task":"OLD-102"}`
And `SELECT count(*) FROM run_jira WHERE run_id = 1 AND state_after IS NULL AND cleaned_at IS NULL` returns `1`
And within 2 seconds `SELECT state FROM runs WHERE id = 1` returns `running`
And the runtime has started exactly one container labelled `bb.run_id` = `1`

#### Scenario: A project with no fixture configured seeds nothing
Given project `7` exists with the `jira` integration row `5` whose `config` is exactly `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`
And run `1` exists prepared with `state` = `queued`
And `SELECT count(*) FROM run_jira` returns `0`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then the Jira stub records zero requests
And `SELECT count(*) FROM run_jira` returns `0`
And the Jira stub's project `OLD` still contains exactly one issue `OLD-100`
And the runtime has started exactly one container labelled `bb.run_id` = `1`

#### Scenario: A missing fixture file fails the run before any issue is created
Given the `jira` integration row `5` has `config.fixture` = `missing-fixture`
And `fixtures/missing-fixture/jira.json` does not exist at commit `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And run `1` exists prepared with `state` = `queued`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then the Jira stub records zero requests
And within 2 seconds `SELECT state, claimed_verdict FROM runs WHERE id = 1` returns exactly `failed_seed | NULL`
And `SELECT count(*) FROM run_jira WHERE run_id = 1` returns `0`
And the first line of `s3://skill-builder-runs/runs/1/agent.log` is exactly `[skill-builder] jira fixture seed failed: fixture 'missing-fixture' has no jira.json at 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the runtime has started no container labelled `bb.run_id` = `1`

#### Scenario: A fixture that names an existing issue fails without deleting it
Given the `jira` integration row `5` has `config.fixture` = `pinned-keys`
And `fixtures/pinned-keys/jira.json` at the skills commit declares one entry with `alias` = `bug`, `key` = `OLD-50`, `issue_type` = `Bug` and `summary` = `Pinned fixture issue`
And the Jira stub's project `OLD` contains issue `OLD-50` with `summary` = `A human-authored issue`, `status` = `To Do` and `labels` = `[]`
And run `1` exists prepared with `state` = `queued`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then `SELECT state FROM runs WHERE id = 1` returns `failed_seed`
And the Jira stub records zero `POST` and zero `DELETE` requests
And issue `OLD-50` still has `summary` = `A human-authored issue`, `status` = `To Do` and `labels` = `[]`
And `SELECT count(*) FROM run_jira WHERE run_id = 1` returns `0`
And the first line of `s3://skill-builder-runs/runs/1/agent.log` is exactly `[skill-builder] jira fixture seed failed: fixture 'pinned-keys' names existing issue 'OLD-50'`
And the runtime has started no container labelled `bb.run_id` = `1`

#### Scenario: A failure partway through seeding deletes what it created
Given the `jira` integration row `5` has `config.fixture` = `bug-fix-empty-title`
And the Jira stub accepts the first `POST /rest/api/2/issue` with `201` and `{"id":"10001","key":"OLD-101"}`
And the Jira stub returns `500` with `{"errorMessages":["Internal server error"]}` to the second `POST /rest/api/2/issue`
And run `1` exists prepared with `state` = `queued`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then the Jira stub records one `DELETE /rest/api/2/issue/OLD-101`
And the Jira stub contains exactly one issue: `OLD-100` with `labels` = `[]`
And `SELECT state, claimed_verdict FROM runs WHERE id = 1` returns exactly `failed_seed | NULL`
And `SELECT count(*) FROM run_jira WHERE run_id = 1` returns `0`
And the first line of `s3://skill-builder-runs/runs/1/agent.log` is exactly `[skill-builder] jira fixture seed failed: POST /rest/api/2/issue for alias 'task' returned HTTP 500`
And the runtime has started no container labelled `bb.run_id` = `1`
And a further claim pass leaves `SELECT state FROM runs WHERE id = 1` as `failed_seed`

### Covered requirements (traceability)
- FR-058

### Out of scope
Replacing alias tokens inside the fixture content and storing the alias mapping (BSB-28-PENDING-2).
Capturing the post-run Jira state (BSB-28-PENDING-3). End-of-run cleanup (BSB-28-PENDING-4) and
the nightly sweep (BSB-28-PENDING-5). Jira integrations configured with a template project instead
of a project key. A fixture authoring or editing interface, and any mutation of an issue the run
did not seed (the epic's non-goals). Provisioning the Jira project, its issue types or its
credentials (epic BSB-23).

### Notes / dependencies
- Depends on epic BSB-23 for the `jira` integration, its `site_url`, `project_key` and
  `secret_ref`; on epic BSB-24 for the `runs` row and its `queued` starting state; on epic BSB-25
  for the prepared `skills_commit_sha`, `run_branch` and `skill_bundles` row; and on epic BSB-26 for
  the claim path, the terminal-write rule and the run log. The fixture file is read from
  `saraavrnd/bheembhai-skills` at the run's `skills_commit_sha`.
- The run marker is the single label `skilltest-1`; it is the only identification the cleanup and
  the sweep may rely on. A human-authored issue never carries it.
- The fixture name comes from `config.fixture` (Open decision 1); a template-project integration is
  out of scope (Open decision 3). The `@alias@` token delimiter is Open decision 2.
- Seeding is a new pre-launch step in BSB-26's claim path, and `failed_seed` a new terminal state;
  BSB-26's state table must gain it in a later revise pass (cross-epic note above).
- Failure reasons are the HTTP status for a Jira error, the fixture name for a missing or invalid
  file, and the offending key for an existing-issue collision. Credential values and the
  Authorization header are never logged.

## STORY: BSB-28-PENDING-2

**Summary:** Replace fixture aliases with the created issue keys
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-9, Later

### Story
As a **skill author**, I want **alias references in my fixture file to become the real Jira issue keys**, so that **fixture issues that refer to each other point at the issues the run actually created instead of at stale or invented keys**.

### Acceptance Criteria

#### Scenario: Alias tokens resolve to the created keys
Given the `jira` integration row `5` has `config.fixture` = `bug-fix-empty-title`
And run `1` exists prepared with `state` = `queued`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then after the two creates the Jira stub records exactly two `PUT` requests, in this order
And the first `PUT` is to `https://old.atlassian.net/rest/api/2/issue/OLD-101` with body exactly `{"fields":{"description":"The checkout button does nothing. Tracking issue: OLD-102."}}`
And the second `PUT` is to `https://old.atlassian.net/rest/api/2/issue/OLD-102` with body exactly `{"fields":{"description":"Found while reproducing OLD-101."}}`
And issue `OLD-101` in the stub has `description` = `The checkout button does nothing. Tracking issue: OLD-102.`
And issue `OLD-102` in the stub has `description` = `Found while reproducing OLD-101.`
And `SELECT aliases FROM run_jira WHERE run_id = 1` equals the JSON value `{"bug":"OLD-101","task":"OLD-102"}`
And `SELECT state FROM runs WHERE id = 1` returns `running`
And no issue in the stub has a `summary` or `description` containing `@`

#### Scenario: A fixture with no alias references sends no update
Given the `jira` integration row `5` has `config.fixture` = `no-cross-references`
And `fixtures/no-cross-references/jira.json` declares issues `bug` and `task` whose `summary` and `description` contain no alias token
And run `1` exists prepared with `state` = `queued`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then the Jira stub records exactly two `POST /rest/api/2/issue` requests and zero `PUT` requests
And `SELECT aliases FROM run_jira WHERE run_id = 1` equals the JSON value `{"bug":"OLD-101","task":"OLD-102"}`
And `SELECT state FROM runs WHERE id = 1` returns `running`

#### Scenario: An unknown alias fails the seed before any issue is created
Given the `jira` integration row `5` has `config.fixture` = `unknown-alias`
And `fixtures/unknown-alias/jira.json` declares one issue with `alias` = `bug` and `description` = `Blocks @missing@.`
And the file declares no issue with `alias` = `missing`
And run `1` exists prepared with `state` = `queued`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then the Jira stub records zero `POST` and zero `DELETE` requests
And `SELECT state FROM runs WHERE id = 1` returns `failed_seed`
And `SELECT count(*) FROM run_jira WHERE run_id = 1` returns `0`
And the first line of `s3://skill-builder-runs/runs/1/agent.log` is exactly `[skill-builder] jira fixture seed failed: fixture 'unknown-alias' references unknown alias 'missing'`
And the runtime has started no container labelled `bb.run_id` = `1`

#### Scenario: A duplicate alias fails the seed before any issue is created
Given the `jira` integration row `5` has `config.fixture` = `duplicate-alias`
And `fixtures/duplicate-alias/jira.json` declares two issues whose `alias` is `bug`
And run `1` exists prepared with `state` = `queued`
And the builder executor is running with a 1-second claim interval
When the executor claims run `1`
Then the Jira stub records zero `POST` and zero `DELETE` requests
And `SELECT state FROM runs WHERE id = 1` returns `failed_seed`
And `SELECT count(*) FROM run_jira WHERE run_id = 1` returns `0`
And the first line of `s3://skill-builder-runs/runs/1/agent.log` is exactly `[skill-builder] jira fixture seed failed: fixture 'duplicate-alias' repeats alias 'bug'`
And the runtime has started no container labelled `bb.run_id` = `1`

### Covered requirements (traceability)
- FR-059

### Out of scope
Creating the issues, applying the run marker and inserting the `run_jira` row (BSB-28-PENDING-1).
Capturing the post-run state (BSB-28-PENDING-3), cleanup (BSB-28-PENDING-4) and the sweep
(BSB-28-PENDING-5). Alias references in fields other than `summary` and `description`. Rewriting
the fixture file on disk.

### Notes / dependencies
- Depends on BSB-28-PENDING-1 for the created issue keys and the `run_jira` row. The alias mapping
  is written in fixture order and is the only place the cleanup and the state capture learn which
  key belongs to which alias.
- The two-phase order matters: phase 2 runs only after every issue in phase 1 exists, so a forward
  reference (an issue whose token names an issue declared later in the file) resolves exactly like
  a backward reference. No token survives in a stored issue.
- The alias token delimiter is Open decision 2; changing it changes only this parser and these
  scenarios.

## STORY: BSB-28-PENDING-3

**Summary:** Record the seeded issues' state after the run
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-9, Later

### Story
As a **skill author**, I want **the builder to record the Jira state of the seeded issues after the run**, so that **I can assert what the skill actually changed without keeping the disposable issues in Jira**.

### Acceptance Criteria

#### Scenario: The post-run state of every seeded issue is recorded
Given run `1` exists with `state` = `running` and a `run_jira` row whose `aliases` = `{"bug":"OLD-101","task":"OLD-102"}` and `state_after` = `NULL`
And the Jira stub's project `OLD` contains `OLD-101` with `summary` = `Checkout fails when the cart is empty` and `status` = `In Progress`, and `OLD-102` with `summary` = `Investigate empty-cart checkout failure` and `status` = `Done`
And the runtime has exited with status `0` and uploaded a valid result with `result_status` = `completed`
And the builder clock reads `2026-11-15T10:05:00Z`
When the executor writes `runs.state` = `completed`
Then the Jira stub records `GET /rest/api/2/issue/OLD-101?fields=summary,status` and then `GET /rest/api/2/issue/OLD-102?fields=summary,status`
And `SELECT state_after FROM run_jira WHERE run_id = 1` equals the JSON value `{"issues":[{"alias":"bug","key":"OLD-101","status":"In Progress","summary":"Checkout fails when the cart is empty"},{"alias":"task","key":"OLD-102","status":"Done","summary":"Investigate empty-cart checkout failure"}]}`
And `SELECT state FROM runs WHERE id = 1` returns `completed`

#### Scenario: The state is captured before the issues are cleaned up
Given run `1` exists with `state` = `running` and a `run_jira` row whose `aliases` = `{"bug":"OLD-101","task":"OLD-102"}` and `state_after` = `NULL` and `cleaned_at` = `NULL`
And the Jira stub serves both seeded issues as in the previous scenario
And the runtime has exited with a classifiable `completed` result
When the executor writes `runs.state` = `completed`
Then the stub's request log contains the two `GET` reads of `fields=summary,status` before the first `DELETE`
And `SELECT state_after IS NOT NULL, cleaned_at FROM run_jira WHERE run_id = 1` returns exactly `true | 2026-11-15T10:05:01Z`

#### Scenario: An issue deleted during the run is recorded as missing
Given run `1` exists with `state` = `running` and a `run_jira` row whose `aliases` = `{"bug":"OLD-101","task":"OLD-102"}`
And the Jira stub serves `OLD-101` with `status` = `In Progress`
And the Jira stub returns `404` with `{"errorMessages":["Issue does not exist"]}` for any read of `OLD-102`
And the runtime has exited with a classifiable `completed` result
When the executor writes `runs.state` = `completed`
Then `SELECT state_after FROM run_jira WHERE run_id = 1` equals the JSON value `{"issues":[{"alias":"bug","key":"OLD-101","status":"In Progress","summary":"Checkout fails when the cart is empty"},{"alias":"task","key":"OLD-102","status":null,"summary":null,"missing":true}]}`
And cleanup still runs and sets `cleaned_at` = `2026-11-15T10:05:01Z`

#### Scenario: A run with no seeded issues captures nothing
Given run `1` exists with `state` = `running` and no `run_jira` row
And the runtime has exited with a classifiable `completed` result
When the executor writes `runs.state` = `completed`
Then the Jira stub records zero `GET /rest/api/2/issue/` requests
And `SELECT count(*) FROM run_jira WHERE run_id = 1` returns `0`
And `SELECT state FROM runs WHERE id = 1` returns `completed`

#### Scenario: A failed read leaves the state unrecorded and cleanup still runs
Given run `1` exists with `state` = `running` and a `run_jira` row whose `aliases` = `{"bug":"OLD-101","task":"OLD-102"}` and `state_after` = `NULL`
And the Jira stub serves `OLD-101` normally and returns `500` for the read of `OLD-102`
And the runtime has exited with a classifiable `completed` result
When the executor writes `runs.state` = `completed`
Then `SELECT state_after FROM run_jira WHERE run_id = 1` is `NULL`
And the Jira stub records `DELETE /rest/api/2/issue/OLD-101` and `DELETE /rest/api/2/issue/OLD-102`
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` equals the timestamptz `2026-11-15T10:05:01Z`
And the stored run log contains the exact line `[skill-builder] jira state capture failed: GET /rest/api/2/issue/OLD-102?fields=summary,status returned HTTP 500`
And `SELECT state FROM runs WHERE id = 1` returns `completed`

### Covered requirements (traceability)
- FR-060

### Out of scope
Deleting the issues after capture (BSB-28-PENDING-4) and the nightly sweep (BSB-28-PENDING-5).
The fixture assertions themselves and any display of the recorded state; the run report, the
durable Jira-change record and its display belong to epic BSB-33 (FR-140). Reading Jira changes
the skill did not make through the seeded issues.

### Notes / dependencies
- Depends on BSB-28-PENDING-1 and BSB-28-PENDING-2 for the `run_jira` row, its `aliases` mapping
  and the seeded issues; on BSB-26 for the terminal-write rule and the run log; and on BSB-27 for
  the sibling terminal states that also trigger the finalizer.
- The finalizer runs once after the terminal state is written and before epic BSB-29 verifies the
  run, so verification never sees the disposable issues and never depends on them.
- A capture failure is recorded, not raised: it never changes `runs.state` and never blocks
  cleanup. `state_after` staying `NULL` tells a later reader that no post-run state was captured.

## STORY: BSB-28-PENDING-4

**Summary:** Clean up a run's seeded Jira issues when it ends
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-9, Later

### Story
As a **skill author**, I want **the builder to remove only the issues it seeded when the run ends**, so that **disposable fixture data does not accumulate and a human-authored issue is never deleted**.

### Acceptance Criteria

#### Scenario: Run end deletes exactly the seeded issues and records the cleanup
Given run `1` exists with `state` = `completed` and a `run_jira` row whose `aliases` = `{"bug":"OLD-101","task":"OLD-102"}`, `state_after` is recorded and `cleaned_at` = `NULL`
And the Jira stub's project `OLD` contains `OLD-100` with `labels` = `[]`, `OLD-101` with `labels` = `["skilltest-1"]` and `OLD-102` with `labels` = `["skilltest-1"]`
And the builder clock reads `2026-11-15T10:05:01Z` when cleanup completes
When the Jira finalizer runs for run `1`
Then the Jira stub records exactly two `DELETE` requests, in this order: `DELETE /rest/api/2/issue/OLD-101` and `DELETE /rest/api/2/issue/OLD-102`
And the stub's project `OLD` contains exactly one issue: `OLD-100` with `labels` = `[]`
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` equals the timestamptz `2026-11-15T10:05:01Z`

#### Scenario: An unmarked issue is never deleted
Given run `1` exists with `state` = `completed` and the `run_jira` row above
And the Jira stub's project `OLD` contains `OLD-100` with `summary` = `Checkout fails when the cart is empty`, `labels` = `[]` and `OLD-101` and `OLD-102` as above
When the Jira finalizer runs for run `1`
Then the Jira stub records no `DELETE /rest/api/2/issue/OLD-100`
And issue `OLD-100` still exists with `summary` = `Checkout fails when the cart is empty` and `labels` = `[]`

#### Scenario: A recorded issue that lost the marker is skipped
Given run `1` exists with `state` = `completed` and a `run_jira` row whose `aliases` = `{"bug":"OLD-101","task":"OLD-102"}` and `cleaned_at` = `NULL`
And the Jira stub serves `OLD-101` with `labels` = `[]` and `OLD-102` with `labels` = `["skilltest-1"]`
When the Jira finalizer runs for run `1`
Then the Jira stub records no `DELETE /rest/api/2/issue/OLD-101`
And the Jira stub records `DELETE /rest/api/2/issue/OLD-102`
And issue `OLD-101` still exists with `labels` = `[]`
And the stored run log contains the exact line `[skill-builder] jira cleanup skipped OLD-101: run marker 'skilltest-1' is absent`
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` equals the timestamptz `2026-11-15T10:05:01Z`

#### Scenario: Cleanup is idempotent
Given run `1` exists with `state` = `completed` and a `run_jira` row whose `cleaned_at` = `2026-11-15T10:05:01Z`
And the Jira stub's project `OLD` contains only `OLD-100` with `labels` = `[]`
When the Jira finalizer runs for run `1` again
Then the Jira stub records zero `DELETE` requests
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` still equals the timestamptz `2026-11-15T10:05:01Z`
And the run log gains no new cleanup failure line

#### Scenario: An issue that is already gone counts as cleaned
Given run `1` exists with `state` = `completed` and a `run_jira` row whose `aliases` = `{"bug":"OLD-101","task":"OLD-102"}` and `cleaned_at` = `NULL`
And the Jira stub returns `404` for any read of `OLD-101`
And the Jira stub serves `OLD-102` with `labels` = `["skilltest-1"]`
When the Jira finalizer runs for run `1`
Then the Jira stub records no `DELETE /rest/api/2/issue/OLD-101`
And the Jira stub records `DELETE /rest/api/2/issue/OLD-102`
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` equals the timestamptz `2026-11-15T10:05:01Z`

#### Scenario: A deletion failure leaves the record uncleaned for the sweep
Given run `1` exists with `state` = `completed` and a `run_jira` row whose `aliases` = `{"bug":"OLD-101","task":"OLD-102"}` and `cleaned_at` = `NULL`
And the Jira stub accepts `DELETE /rest/api/2/issue/OLD-101` with `204`
And the Jira stub returns `500` for `DELETE /rest/api/2/issue/OLD-102`
When the Jira finalizer runs for run `1`
Then issue `OLD-101` is gone from the stub
And issue `OLD-102` still exists with `labels` = `["skilltest-1"]`
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` is `NULL`
And the stored run log contains the exact line `[skill-builder] jira cleanup failed: DELETE /rest/api/2/issue/OLD-102 returned HTTP 500`
And `SELECT state FROM runs WHERE id = 1` still returns `completed`

### Covered requirements (traceability)
- FR-061

### Out of scope
Capturing the post-run state before cleanup (BSB-28-PENDING-3). The nightly sweep that removes what
cleanup leaves behind (BSB-28-PENDING-5). Deleting any issue that is not recorded in
`run_jira.aliases` — the epic's non-goal of never mutating an issue the run did not seed. Cleanup
for a run that never seeded a fixture, and any UI for cleanup.

### Notes / dependencies
- Depends on BSB-28-PENDING-1 for the seeded issues and the `run_jira` row, on BSB-28-PENDING-3
  for the capture-before-cleanup order, and on BSB-26 and BSB-27 for the terminal states that
  invoke the finalizer.
- The marker check is defensive: the recorded key is deleted only while its issue still carries
  `skilltest-1`, so a key that came back without the marker is never treated as disposable.
- The cleanup is best-effort by design: a failed delete leaves `cleaned_at` `NULL` and the issue
  in place for BSB-28-PENDING-5. A retry or the sweep completes it.

## STORY: BSB-28-PENDING-5

**Summary:** Sweep leftover seeded Jira issues nightly
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-9, Later

### Story
As a **skill author**, I want **a nightly sweep of leftover issues carrying a run marker**, so that **a crashed, interrupted or failed run cannot leave disposable issues in Jira indefinitely**.

### Acceptance Criteria

#### Scenario: The sweep removes a finished run's leftovers
Given project `7` has the `jira` integration row `5` with `project_key` = `OLD`
And run `1` exists with `state` = `completed` and a `run_jira` row whose `cleaned_at` = `NULL`
And the Jira stub's project `OLD` contains `OLD-100` with `labels` = `[]`, `OLD-101` with `labels` = `["skilltest-1"]` and `OLD-102` with `labels` = `["skilltest-1"]`
And the sweep runs at `2026-11-16T02:00:00Z`
When the nightly sweep runs
Then the Jira stub records exactly two `DELETE` requests: `DELETE /rest/api/2/issue/OLD-101` and `DELETE /rest/api/2/issue/OLD-102`
And the stub's project `OLD` contains exactly one issue: `OLD-100` with `labels` = `[]`
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` equals the timestamptz `2026-11-16T02:00:00Z`

#### Scenario: The sweep never removes a running run's issues
Given project `7` has the `jira` integration row `5` with `project_key` = `OLD`
And run `1` exists with `state` = `running` and a `run_jira` row whose `cleaned_at` = `NULL`
And the Jira stub's project `OLD` contains `OLD-101` and `OLD-102`, each with `labels` = `["skilltest-1"]`
When the nightly sweep runs
Then the Jira stub records zero `DELETE` requests
And both `OLD-101` and `OLD-102` still exist with `labels` = `["skilltest-1"]`
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` is `NULL`

#### Scenario: The sweep removes an orphan marker and leaves unmarked issues
Given project `7` has the `jira` integration row `5` with `project_key` = `OLD`
And `SELECT count(*) FROM runs WHERE id = 1` returns `0`
And the Jira stub's project `OLD` contains `OLD-100` with `labels` = `["onboarding"]`, `OLD-101` with `labels` = `["skilltest-1"]` and `OLD-102` with `labels` = `["skilltest-9"]`
And no `runs` row exists with id `9`
When the nightly sweep runs
Then the Jira stub records exactly two `DELETE` requests: `DELETE /rest/api/2/issue/OLD-101` and `DELETE /rest/api/2/issue/OLD-102`
And issue `OLD-100` still exists with `labels` = `["onboarding"]`
And the sweep writes no `run_jira` row

#### Scenario: A project with no marked issues deletes nothing
Given project `7` has the `jira` integration row `5` with `project_key` = `OLD`
And the Jira stub's project `OLD` contains only `OLD-100` with `labels` = `["onboarding"]`
When the nightly sweep runs
Then the Jira stub records zero `DELETE` requests
And issue `OLD-100` still exists with `labels` = `["onboarding"]`
And the sweep exits successfully

#### Scenario: A second sweep in the same night deletes nothing
Given the sweep has just deleted every marked issue of run `1` and set its `cleaned_at`
And the Jira stub's project `OLD` contains only unmarked issues
When the nightly sweep runs again in the same night
Then the Jira stub records zero `DELETE` requests
And `SELECT cleaned_at FROM run_jira WHERE run_id = 1` still equals the timestamptz `2026-11-16T02:00:00Z`

### Covered requirements (traceability)
- FR-062

### Out of scope
End-of-run cleanup (BSB-28-PENDING-4) and seeding (BSB-28-PENDING-1). Sweeping a project whose
`jira` integration has been removed, and sweeping a Jira site outside a project's configured
integration. Deleting an issue with no `skilltest-` marker for any reason, and any UI or alert for
the sweep.

### Notes / dependencies
- Depends on BSB-28-PENDING-1 for the marker and on BSB-28-PENDING-4 for the `cleaned_at` record;
  on BSB-23 for the project's `jira` integration; and on the installation's scheduler (the epic's
  dependency note names a scheduler for this job).
- A `runs` row is active exactly while its `state` is `queued` or `running`; every other value is
  terminal, including values owned by sibling epics. The sweep therefore needs no fixed list of
  terminal state names.
- The sweep is the safety net for a run whose finalizer never ran, for a seed whose rollback was
  interrupted, and for a run row that no longer exists. It reads across pages of 100 and stops
  when it has read the reported total.

---
*Generated by `sdlc-plan-stories-write`. Coverage: FR-058, FR-059, FR-060, FR-061 and FR-062 all
covered. Next steps: `sdlc-plan-epic-review` reviews this set; `sdlc-tracker-sync` publishes the
approved stories to Jira.*
