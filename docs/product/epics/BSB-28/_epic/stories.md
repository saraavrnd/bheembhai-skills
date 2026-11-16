# Stories — BSB-28 (Jira fixture seeding)

Epic BSB-28 covers FR-058, FR-059, FR-060, FR-061 and FR-062. It is decomposed into 5
end-to-end slices below, and coverage of all 5 requirements is verified.

The five slices are what a skill author or project owner sees around a Jira-backed run: the
fixture issues appearing in the project's configured test Jira project marked for this run
(PENDING-1); the aliases the author wrote resolving to the created issue keys the skill receives
(PENDING-2); the post-run tracker state shown for fixture assertions (PENDING-3); the seeded
issues being cleaned up when the run ends while real and other-run issues stay (PENDING-4); and
a nightly sweep that removes leftovers, leaves active runs alone, and reports what it removed
(PENDING-5). Seeding, alias substitution, capture, cleanup and sweeping are the means; each
story asserts the visible outcome first and the durable record behind it second, so no story is
a technical layer on its own.

The durable system of record is the Jira project itself plus the builder's `run_jira` row, which
ADR SK-001 section 9 names with `run_id`, `aliases`, `state_after` and `cleaned_at`. PENDING-4
adds `run_jira.cleaned_count` so the run report can state how many issues it deleted, and
PENDING-5 adds `fixture_sweeps` (`id`, `integration_id`, `started_at`, `finished_at`,
`deleted_count`, `error`) so a project can show its last sweep result. Every seeded issue carries the marker label
`skilltest-` followed by the run id, for example `skilltest-21`. An issue without that exact
marker is outside the builder's authority and is never selected for deletion.

The fixture directory is named after the run's skill: a run of skill `sdlc-fix-bug-reproduce`
reads `fixtures/sdlc-fix-bug-reproduce/jira.json` from its own skills commit. This keeps Jira
fixture selection out of run start (BSB-24 records that Jira is not a run-start choice) and is
the concrete form of the ADR's fixtures directory and jira.json layout. A skill with no fixture
directory runs without seeding.

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than a Jira issue: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404
"Issue does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The
Atlassian MCP server is configured in `.mcp.json`, but this session exposed no Atlassian MCP
tools, so the configured site was queried read-only through its REST API. The epic being
decomposed is BSB-28, read read-only from the same site: summary "Jira fixture seeding", type
Epic, status To Do, labels FA-9/Later, and a description matching the BSB-28 section of
`epics.md`. No Jira write was attempted.

**Release.** Later. This epic is deferred and is not a prerequisite for the first release. It
depends on the MVP project, integration, run and execution epics listed in each story's notes.

**Cross-epic prerequisites and hand-offs (not requirements of these stories).** PENDING-1 runs
after a run reaches `prepared` and before BSB-26 launches the agent container; BSB-26-PENDING-1's
launch contract gains the `BB_JIRA_FIXTURES` environment variable in PENDING-2. The run's
`skills_commit_sha` and skills checkout are produced by BSB-25, the `runs` row by BSB-24, and the
terminal states by BSB-26 and BSB-27; BSB-27's deadline guarantees that a live run eventually
becomes terminal, which is what lets PENDING-5 skip only genuinely active runs. The configured
test Jira project and its opaque secret reference are BSB-23's `integrations` row of kind
`jira`; the project and its owner/membership rule are BSB-22's. The run report frame these
stories extend is BSB-33-PENDING-1's. PENDING-3 owns `run_jira.state_after`; BSB-33-PENDING-4
owns the report's display-oriented `state_before`, `changes` and `capture_error`, and must read
this recorded snapshot rather than maintain a second post-run capture.

A single requirement is claimed by exactly one story:

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-058 — Jira issues are seeded for a run from a fixture file into the project's configured Jira project, marked with the run's ID | BSB-28-PENDING-1 | "A run seeds its fixture into the configured Jira project"; "A malformed fixture is refused before any issue is created"; "A fixture that tries to choose another Jira project is refused"; "A project without a Jira integration cannot seed a fixture"; "A Jira failure part-way through seeding rolls back the issues already created"; "A run without a fixture does not touch Jira" |
| FR-059 — Seeding replaces fixture aliases with the created issue keys | BSB-28-PENDING-2 | "Alias references in the fixture resolve to the created issue keys"; "The run's skill receives the alias map"; "An alias that is not defined before it is used is refused"; "Two runs of the same fixture resolve to their own issue keys" |
| FR-060 — The builder records the Jira state after the run for fixture assertions | BSB-28-PENDING-3 | "The post-run Jira state is recorded and shown"; "A run without a seeded fixture records no Jira state"; "A Jira read failure leaves the run outcome unchanged"; "The recorded state stays fixed after later Jira changes" |
| FR-061 — The builder cleans up the issues it seeded when the run ends, deleting only issues marked with that run's ID | BSB-28-PENDING-4 | "A completed run's seeded issues are deleted and the cleanup is shown"; "A failed run's seeded issues are also deleted"; "A cleanup failure leaves the cleanup pending"; "A second cleanup deletes nothing"; "A run without a seeded fixture cleans up nothing"; "Issues in another project are never deleted" |
| FR-062 — A nightly sweep removes seeded issues carrying a run marker | BSB-28-PENDING-5 | "The nightly sweep removes marked leftovers and the project shows the result"; "A marker for a run still in progress is left for end-of-run cleanup"; "An orphaned marker with no run row is removed"; "Labels that only resemble the marker are not selected"; "A project whose Jira is unavailable does not block other projects"; "A second sweep removes nothing" |

> New stories use draft keys in the `BSB-28-PENDING` series (`-1` to `-5`). `sdlc-tracker-sync`
> publishes each story, parents it to BSB-28, and replaces the draft key with the real key in
> `story-map.json`.

---

## STORY: BSB-28-PENDING-1

**Title:** Seed a run's Jira project from a fixture and mark every issue for that run
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-9, Later

### Story
As a **skill author who is a project member**, I want **the builder to create the issues from my skill's Jira fixture in the project's configured test Jira project and mark each one with my run's ID**, so that **my skill runs against realistic tracker data that is visibly attributable to this run and cannot be confused with real tracker content**.

### Acceptance Criteria

Scenario: A run seeds its fixture into the configured Jira project
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), an "integrations" row id 6 with project_id 7, kind "jira", config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "BSB", "test_only": true} and secret_ref "skill-builder/7/integration-6", a secret store holding "jira-test-token-9f2c" at "skill-builder/7/integration-6", a "runs" row id 21 with project_id 7, user_id 42, build_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", state "prepared" and kind "run", a stub source-control provider in which repository "saraavrnd/bheembhai-skills" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" contains "fixtures/sdlc-fix-bug-reproduce/jira.json" with content {"issues": [{"alias": "bug", "summary": "Reproduce bug", "type": "Bug", "labels": ["repro"]}, {"alias": "follow-up", "summary": "Follow-up task", "type": "Task"}]}, a stub Jira server in which project "BSB" holds only human issue "BSB-100" with {"summary": "Real bug", "status": "To Do", "assignee": null, "labels": []} and project "OTHER" holds issue "OTHER-1" with {"summary": "Production issue", "status": "To Do", "assignee": null, "labels": []}, an empty "run_jira" table, a stub runtime adapter whose container-start counter is 0, and a builder clock reading "2026-11-16T11:00:00Z"
When the run reaches state "prepared" and the builder seeds its fixture before execution
Then the stub Jira server created exactly two issues in project "BSB": "BSB-301" with {"summary": "Reproduce bug", "type": "Bug", "labels": ["repro", "skilltest-21"]} and "BSB-302" with {"summary": "Follow-up task", "type": "Task", "labels": ["skilltest-21"]}, the human issue "BSB-100" is unchanged, no issue was created in project "OTHER", the "run_jira" row for run 21 has aliases {"bug": "BSB-301", "follow-up": "BSB-302"}, state_after NULL and cleaned_at NULL, the "runs" row id 21 still has state "prepared", the stub runtime adapter's container-start counter remains 0, and GET "/projects/7/runs/21" renders "Jira fixture: sdlc-fix-bug-reproduce", "2 issues seeded in project BSB" and "Run marker: skilltest-21"

Scenario: A malformed fixture is refused before any issue is created
Given the same signed-in Ada, project 7, Jira integration 6, run 21 and stub runtime adapter, and a stub source-control provider in which "fixtures/sdlc-fix-bug-reproduce/jira.json" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" contains the truncated, invalid JSON text {"issues": [
When the run reaches state "prepared" and the builder attempts to seed its fixture
Then the stub Jira server received zero create and zero delete requests, the "runs" row id 21 has state "failed", result_status "failed_infra", execution_error "The Jira fixture could not be read: invalid JSON." and finished_at "2026-11-16T11:00:00Z", no "run_jira" row exists for run 21, the stub runtime adapter's container-start counter remains 0, and GET "/projects/7/runs/21" renders "Jira fixture failed: The Jira fixture could not be read: invalid JSON." with no exception text or stack trace

Scenario: A fixture that tries to choose another Jira project is refused
Given the same signed-in Ada, project 7, Jira integration 6, run 21 and stub runtime adapter, and a stub source-control provider in which "fixtures/sdlc-fix-bug-reproduce/jira.json" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" contains {"project_key": "OTHER", "issues": [{"alias": "bug", "summary": "Reproduce bug", "type": "Bug"}]}
When the run reaches state "prepared" and the builder attempts to seed its fixture
Then the stub Jira server received zero create requests for projects "BSB" and "OTHER", the "runs" row id 21 has state "failed", result_status "failed_infra" and execution_error "The Jira fixture may not choose a Jira project.", no "run_jira" row exists for run 21, and GET "/projects/7/runs/21" renders "Jira fixture failed: The Jira fixture may not choose a Jira project."

Scenario: A project without a Jira integration cannot seed a fixture
Given a signed-in skill author Ada with a "project_members" row for Project Atlas (id 7), a "runs" row id 23 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "prepared" and kind "run", an "integrations" table with no row of kind "jira" for project 7, a stub source-control provider containing "fixtures/sdlc-fix-bug-reproduce/jira.json" at that commit, and a builder clock reading "2026-11-16T11:00:00Z"
When the run reaches state "prepared" and the builder attempts to seed its fixture
Then the stub Jira server received zero create and zero delete requests, the "runs" row id 23 has state "failed", result_status "failed_infra" and execution_error "A Jira integration is required to seed this run's fixture.", no "run_jira" row exists for run 23, and GET "/projects/7/runs/23" renders "Jira fixture failed: A Jira integration is required to seed this run's fixture."

Scenario: A Jira failure part-way through seeding rolls back the issues already created
Given the same signed-in Ada, project 7, Jira integration 6, a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "prepared", a stub source-control provider containing a fixture with three issues whose aliases are "bug", "follow-up" and "regression", and a stub Jira server that creates "BSB-301" and "BSB-302" and then returns HTTP 503 "Service Unavailable" for the third create request
When the run reaches state "prepared" and the builder attempts to seed its fixture
Then the stub Jira server received delete requests for exactly "BSB-301" and "BSB-302", no issue carrying the label "skilltest-21" remains in project "BSB", the "runs" row id 21 has state "failed", result_status "failed_infra" and execution_error "The Jira fixture could not be seeded.", no "run_jira" row exists for run 21, and GET "/projects/7/runs/21" renders "Jira fixture failed: The Jira fixture could not be seeded." and "0 issues remain"

Scenario: A run without a fixture does not touch Jira
Given the same signed-in Ada, project 7 and Jira integration 6, and a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "prepared", and a stub source-control provider at that commit that contains no "fixtures/sdlc-fix-bug-reproduce/jira.json" file
When the run reaches state "prepared" and the builder looks for its fixture
Then the stub Jira server received zero create and zero delete requests, no "run_jira" row exists for run 24, the "runs" row id 24 still has state "prepared", and GET "/projects/7/runs/24" renders "Jira fixture: none"

### Covered requirements (traceability)
- FR-058

### Out of scope
Starting the run and choosing its project, skill, branches and model (BSB-24); resolving the
skills commit and packing the bundle (BSB-25); executing the skill and reaching a classified
outcome (BSB-26); turn and spend caps, the deadline and re-runs (BSB-27); replacing aliases with
created keys and handing the alias map to the skill (BSB-28-PENDING-2); recording the post-run
Jira state (BSB-28-PENDING-3); end-of-run cleanup (BSB-28-PENDING-4); the nightly sweep
(BSB-28-PENDING-5); configuring or verifying the Jira integration (BSB-23); the report's identity,
verdict, diff, Jira-change, turn and trace sections (BSB-33); catalog submission (BSB-36); the
command line (BSB-37); any tracker write outside the integration's configured project, and any
change to a human-created issue.

### Notes / dependencies
Depends on BSB-18 for the signed-in skill author, on BSB-22-PENDING-1 for the project and its
membership row, on BSB-23-PENDING-1 for the Jira integration's site URL, project key, test-only
flag and opaque secret reference, on BSB-24-PENDING-1 for the "runs" row, on BSB-25-PENDING-1
for "runs.skills_commit_sha" and the catalog checkout, and on BSB-26 for the pre-launch state.
The Jira provider is called with the test-purpose credential resolved from the secret store at
call time; no credential value is persisted or rendered (NFR-004, NFR-006).

The fixture format is defined here, as the epic's implementation step 1 requires: a JSON object
whose "issues" member is a non-empty array; each issue has a unique "alias" matching
[a-z][a-z0-9_]*, a non-empty "summary" and a "type" of Bug, Task or Story; "description",
"labels" and "assignee" are optional; the fixture may not carry a "project_key" because the
integration's "project_key" is the only write target. The fixture is read from the run's skills
commit through the same source-control provider BSB-25 used. Seeding happens after the run is
"prepared" and before BSB-26 launches the container, so a seeding failure never starts execution:
the run is marked "failed" with result_status "failed_infra" and an execution_error, following
BSB-26's pre-launch infrastructure failures.

The marker label "skilltest-" plus the run id is the whole deletion criterion for PENDING-4 and
PENDING-5. Every created issue gets it in addition to the fixture's own labels. Rollback after a
mid-seed failure deletes only the issues this attempt created; if a rollback delete also fails,
the leftover marker is left for the nightly sweep. The run report gains a read-only "Jira
fixture" section on the page BSB-33-PENDING-1 frames; BSB-33-PENDING-4's Jira change capture is a
separate read and must not re-seed anything.

---

## STORY: BSB-28-PENDING-2

**Title:** Use fixture aliases in a run and receive the real Jira issue keys
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-9, Later

### Story
As a **skill author who is a project member**, I want **the aliases I write in my fixture to resolve to the issue keys the builder created and the resolved map to reach my skill**, so that **my skill can reference seeded issues by stable names instead of copying keys out of Jira**.

### Acceptance Criteria

Scenario: Alias references in the fixture resolve to the created issue keys
Given a signed-in skill author Ada with a "project_members" row for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "prepared", a "integrations" row id 6 with project_id 7, kind "jira", config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "BSB", "test_only": true} and secret_ref "skill-builder/7/integration-6", a secret store holding "jira-test-token-9f2c" at that path, a stub source-control provider whose "fixtures/sdlc-fix-bug-reproduce/jira.json" at that commit contains {"issues": [{"alias": "bug", "summary": "Reproduce bug", "type": "Bug", "description": "Reporter saw the failure."}, {"alias": "follow-up", "summary": "Follow-up for ${bug}", "type": "Task", "description": "Blocks ${bug}"}]}, a stub Jira server that returns "BSB-301" for the first create and "BSB-302" for the second, and a builder clock reading "2026-11-16T11:00:00Z"
When the run reaches state "prepared" and the builder seeds its fixture
Then the created issue "BSB-302" has summary "Follow-up for BSB-301" and description "Blocks BSB-301", no created issue field contains the text "${", the "run_jira" row for run 21 has aliases {"bug": "BSB-301", "follow-up": "BSB-302"}, and GET "/projects/7/runs/21" renders "Aliases: bug → BSB-301, follow-up → BSB-302"

Scenario: The run's skill receives the alias map
Given the same signed-in Ada, project 7 and Jira integration 6, a seeded "run_jira" row for run 21 with aliases {"bug": "BSB-301", "follow-up": "BSB-302"}, a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", input_branch "test/atlas/bug-42", run_branch "skilltest/21", context {"workflow": "config/sdlc-wf-bug-fix.yaml", "step": "sdlc-fix-bug-reproduce"}, state "prepared" and kind "run", and a stub runtime adapter whose container-start counter is 0
When the run is launched for execution
Then the stub runtime adapter's container-start counter is 1, its launch environment contains "BB_JIRA_FIXTURES" with the value {"bug": "BSB-301", "follow-up": "BSB-302"}, its launch environment's "BB_CONTEXT" equals run 21's stored context unchanged, and no launch environment value contains the text "${bug}"

Scenario: An alias that is not defined before it is used is refused
Given the same signed-in Ada, project 7, Jira integration 6, a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "prepared", and a stub source-control provider whose fixture contains {"issues": [{"alias": "follow-up", "summary": "Follow-up for ${missing}", "type": "Task"}]}
When the run reaches state "prepared" and the builder attempts to seed its fixture
Then the stub Jira server received zero create requests, the "runs" row id 21 has state "failed", result_status "failed_infra" and execution_error "The Jira fixture is invalid: alias ${missing} is not defined before it is used.", no "run_jira" row exists for run 21, and GET "/projects/7/runs/21" renders "Jira fixture failed: The Jira fixture is invalid: alias ${missing} is not defined before it is used."

Scenario: Two runs of the same fixture resolve to their own issue keys
Given the same signed-in Ada, project 7 and Jira integration 6, two "runs" rows id 21 and 22 with project_id 7, skill "sdlc-fix-bug-reproduce" and state "prepared", a stub source-control provider whose fixture contains {"issues": [{"alias": "bug", "summary": "Reproduce bug", "type": "Bug"}]}, and a stub Jira server that returns "BSB-301" for run 21's create and "BSB-303" for run 22's create
When each run reaches state "prepared" and the builder seeds its fixture
Then the "run_jira" row for run 21 has aliases {"bug": "BSB-301"}, the "run_jira" row for run 22 has aliases {"bug": "BSB-303"}, the two rows are distinct, and GET "/projects/7/runs/22" renders "Aliases: bug → BSB-303"

### Covered requirements (traceability)
- FR-059

### Out of scope
Reading and validating the fixture, creating issues and applying the run marker (BSB-28-PENDING-1);
recording the post-run Jira state (BSB-28-PENDING-3); cleanup and the nightly sweep
(BSB-28-PENDING-4 and -5); rewriting issue descriptions or links in Jira after creation (aliases
are resolved before creation, and forward or circular references are refused rather than patched);
choosing a fixture at run start (a run's fixture is fixed by its skill); configuring the Jira
integration (BSB-23); the report's other sections (BSB-33).

### Notes / dependencies
Depends on BSB-28-PENDING-1 for the seeded issues, the "run_jira" row and its "aliases" column,
and on BSB-26-PENDING-1 for the runtime launch contract. Alias tokens use the form ${alias} in
any string field of a fixture issue. A reference must name an alias defined earlier in the
"issues" array; an undefined, forward or circular reference fails validation before any issue is
created, so the builder never rewrites a Jira issue after creation.

The alias map is persisted in "run_jira.aliases" and also handed to the skill as the
"BB_JIRA_FIXTURES" environment variable (JSON object, alias to issue key). The run's stored
"context" is immutable and is passed as "BB_CONTEXT" unchanged; the map is additive, so a skill
that does not use fixtures is unaffected. This extends BSB-26-PENDING-1's launch environment by
one variable. The report's "Jira fixture" section shows the resolved map beside the seeded count
from PENDING-1. Two runs never share a map or reuse another run's keys.

---

## STORY: BSB-28-PENDING-3

**Title:** See the post-run Jira state of my fixture on the run report
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-9, Later

### Story
As a **skill author who is a project member**, I want **the builder to record the Jira state after my run and show it on the run report**, so that **I can assert what the skill actually did to the tracker data without opening Jira or racing a later edit**.

### Acceptance Criteria

Scenario: The post-run Jira state is recorded and shown
Given a signed-in skill author Ada with a "project_members" row for Project Atlas (id 7), an "integrations" row id 6 with project_id 7, kind "jira", config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "BSB", "test_only": true} and secret_ref "skill-builder/7/integration-6", a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed" and final_verdict "pass", a "run_jira" row for run 21 with aliases {"bug": "BSB-301", "follow-up": "BSB-302"}, state_after NULL and cleaned_at NULL, a stub Jira server in which project "BSB" holds "BSB-301" with {"summary": "Reproduce bug", "status": "Done", "assignee": "ada", "labels": ["repro", "skilltest-21"]}, "BSB-302" with {"summary": "Follow-up for BSB-301", "status": "To Do", "assignee": null, "labels": ["skilltest-21"]} and human issue "BSB-100" with {"summary": "Real bug", "status": "To Do", "assignee": null, "labels": []}, a stub Jira server write counter that is 0, and a builder clock reading "2026-11-16T11:05:00Z"
When the run reaches a terminal state and the builder records the Jira state for fixture assertions, before cleanup runs
Then the "run_jira" row for run 21 has state_after {"BSB-301": {"summary": "Reproduce bug", "status": "Done", "assignee": "ada", "labels": ["repro", "skilltest-21"]}, "BSB-302": {"summary": "Follow-up for BSB-301", "status": "To Do", "assignee": null, "labels": ["skilltest-21"]}, "BSB-100": {"summary": "Real bug", "status": "To Do", "assignee": null, "labels": []}} and cleaned_at NULL, the stub Jira server received zero create, update and delete requests, and GET "/projects/7/runs/21" renders "Jira fixture state: recorded at 2026-11-16T11:05:00Z", "bug (BSB-301): Done" and "follow-up (BSB-302): To Do"

Scenario: A run without a seeded fixture records no Jira state
Given the same signed-in Ada and project 7, a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed" and final_verdict "pass", and no "run_jira" row for run 24
When the run reaches a terminal state and the builder records the Jira state for fixture assertions
Then no "run_jira" row is created for run 24, the "runs" row id 24 still has state "completed" and final_verdict "pass", and GET "/projects/7/runs/24" renders "Jira fixture: none" and no "Jira fixture state" section

Scenario: A Jira read failure leaves the run outcome unchanged
Given the same signed-in Ada, project 7, Jira integration 6 and "run_jira" row for run 21 with aliases {"bug": "BSB-301"} and state_after NULL, a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed" and final_verdict "pass", and a stub Jira server that returns HTTP 503 "Service Unavailable" for the project issue read
When the run reaches a terminal state and the builder attempts to record the Jira state for fixture assertions
Then the "runs" row id 21 still has state "completed", result_status "completed" and final_verdict "pass", the "run_jira" row for run 21 has state_after NULL, and GET "/projects/7/runs/21" renders "Jira fixture state unavailable: The Jira state could not be recorded." with no exception text or stack trace

Scenario: The recorded state stays fixed after later Jira changes
Given the "run_jira" row for run 21 already has state_after {"BSB-301": {"summary": "Reproduce bug", "status": "Done", "assignee": "ada", "labels": ["repro", "skilltest-21"]}}, and a stub Jira server in which a human later changes "BSB-301" to status "In Progress"
When Ada opens GET "/projects/7/runs/21"
Then the "run_jira" row's state_after still records "BSB-301" with status "Done", the stub Jira server's project issue read counter did not increase when the page was opened, and the response renders "bug (BSB-301): Done"

### Covered requirements (traceability)
- FR-060

### Out of scope
Reading and validating the fixture, creating issues and applying the run marker (BSB-28-PENDING-1);
alias resolution (BSB-28-PENDING-2); end-of-run cleanup and the nightly sweep (BSB-28-PENDING-4
and -5); the report's display-oriented before state, change list and capture error (BSB-33-PENDING-4,
which reads this snapshot); evaluating fixture assertions or failing the run on an assertion
mismatch; showing Jira changes the skill made as a diff (BSB-33); writing to Jira.

### Notes / dependencies
Depends on BSB-28-PENDING-1 for the "run_jira" row and seeded issue keys, on BSB-28-PENDING-2 for
the alias map, on BSB-23-PENDING-1 for the Jira integration and its test credential, and on
BSB-26 / BSB-27 for the run reaching a terminal state. This story owns the write of
"run_jira.state_after" named by ADR SK-001 section 9; it captures the configured project's issues,
keyed by issue key, with summary, status, assignee and labels, so a fixture assertion resolves an
alias through "run_jira.aliases" and then reads the recorded state rather than a live Jira read.

The capture happens once, when the run reaches a terminal state and before PENDING-4 deletes the
seeded issues, so the recorded state still describes the seeded issues. It is read-only and never
changes the run's outcome, result_status or final_verdict; a Jira read failure leaves
"state_after" NULL and is shown as unavailable. BSB-33-PENDING-4's report capture owns
"state_before", "changes" and "capture_error"; where both epics are present they share this
terminal-time snapshot rather than taking two divergent post-run reads.

---

## STORY: BSB-28-PENDING-4

**Title:** See a run's seeded Jira issues cleaned up when it ends, without touching real issues
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-9, Later

### Story
As a **skill author who is a project member**, I want **the builder to delete the issues it seeded for my run when the run ends and show the cleanup on the run report**, so that **my test Jira project does not accumulate fixture data and I can trust that real or other runs' issues are never removed**.

### Acceptance Criteria

Scenario: A completed run's seeded issues are deleted and the cleanup is shown
Given a signed-in skill author Ada with a "project_members" row for Project Atlas (id 7), an "integrations" row id 6 with project_id 7, kind "jira", config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "BSB", "test_only": true} and secret_ref "skill-builder/7/integration-6", a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed" and final_verdict "pass", a "run_jira" row for run 21 with aliases {"bug": "BSB-301", "follow-up": "BSB-302"}, state_after {"BSB-301": {"summary": "Reproduce bug", "status": "Done", "assignee": "ada", "labels": ["repro", "skilltest-21"]}} and cleaned_at NULL, a stub Jira server in which project "BSB" holds "BSB-301" and "BSB-302" each labelled "skilltest-21", "BSB-401" labelled "skilltest-22" for completed run 22, and human issue "BSB-100" with no marker label, and a builder clock reading "2026-11-16T11:05:30Z"
When run 21 reaches a terminal state and the builder cleans up its seeded issues
Then the stub Jira server received delete requests for exactly "BSB-301" and "BSB-302", "BSB-401" and "BSB-100" still exist, the "run_jira" row for run 21 has cleaned_at "2026-11-16T11:05:30Z", cleaned_count 2 and state_after unchanged, the "runs" row id 21 still has state "completed" and final_verdict "pass", and GET "/projects/7/runs/21" renders "Jira fixture cleanup: 2 issues deleted at 2026-11-16T11:05:30Z"

Scenario: A failed run's seeded issues are also deleted
Given the same signed-in Ada, project 7 and Jira integration 6, a "runs" row id 22 with project_id 7, skill "sdlc-fix-bug-reproduce", state "failed", result_status "failed_execution", execution_error "The agent process exited with code 2." and final_verdict NULL, a "run_jira" row for run 22 with aliases {"bug": "BSB-301"} and cleaned_at NULL, a stub Jira server in which project "BSB" holds "BSB-301" labelled "skilltest-22", and a builder clock reading "2026-11-16T11:06:00Z"
When run 22 reaches a terminal state and the builder cleans up its seeded issues
Then the stub Jira server received a delete request for "BSB-301", the "run_jira" row for run 22 has cleaned_at "2026-11-16T11:06:00Z" and cleaned_count 1, the "runs" row id 22 still has state "failed", result_status "failed_execution" and execution_error "The agent process exited with code 2.", and GET "/projects/7/runs/22" renders "Jira fixture cleanup: 1 issue deleted at 2026-11-16T11:06:00Z"

Scenario: A cleanup failure leaves the cleanup pending
Given the same signed-in Ada, project 7 and Jira integration 6, run 21 with state "completed", result_status "completed" and final_verdict "pass", a "run_jira" row for run 21 with aliases {"bug": "BSB-301", "follow-up": "BSB-302"} and cleaned_at NULL, a builder clock reading "2026-11-16T11:06:00Z", and a stub Jira server in which project "BSB" holds "BSB-301" and "BSB-302" each labelled "skilltest-21" and human issue "BSB-100", and that returns HTTP 503 "Service Unavailable" for the delete of "BSB-301" and succeeds for "BSB-302"
When run 21 reaches a terminal state and the builder cleans up its seeded issues
Then the stub Jira server received delete requests for both "BSB-301" and "BSB-302", "BSB-301" still exists for the nightly sweep, "BSB-100" still exists, the "run_jira" row for run 21 has cleaned_at NULL and cleaned_count NULL, the "runs" row id 21 still has state "completed", result_status "completed" and final_verdict "pass", and GET "/projects/7/runs/21" renders "Jira fixture cleanup pending: The Jira fixture could not be cleaned up."

Scenario: A second cleanup deletes nothing
Given the same signed-in Ada, project 7, Jira integration 6 and run 21, a "run_jira" row for run 21 with cleaned_at "2026-11-16T11:05:30Z" and cleaned_count 2, a builder clock reading "2026-11-16T12:00:00Z", and a stub Jira server in which project "BSB" holds no issue labelled "skilltest-21" and human issue "BSB-100" and whose delete counter is 0
When the builder invokes cleanup for run 21 again
Then the stub Jira server's delete counter remains 0, the "run_jira" row for run 21 still has cleaned_at "2026-11-16T11:05:30Z" and cleaned_count 2, and GET "/projects/7/runs/21" still renders "Jira fixture cleanup: 2 issues deleted at 2026-11-16T11:05:30Z"

Scenario: A run without a seeded fixture cleans up nothing
Given the same signed-in Ada and project 7, a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed" and final_verdict "pass", no "run_jira" row for run 24, and a stub Jira server whose delete counter is 0
When run 24 reaches a terminal state and the builder cleans up its seeded issues
Then the stub Jira server's delete counter remains 0, no "run_jira" row exists for run 24, and GET "/projects/7/runs/24" renders "Jira fixture: none" and no "Jira fixture cleanup" section

Scenario: Issues in another project are never deleted
Given the same signed-in Ada, project 7, Jira integration 6 and run 21 with a "run_jira" row whose aliases are {"bug": "BSB-301"} and cleaned_at NULL, a builder clock reading "2026-11-16T11:06:00Z", and a stub Jira server in which project "BSB" holds "BSB-301" labelled "skilltest-21" and project "OTHER" holds "OTHER-7" labelled "skilltest-21"
When run 21 reaches a terminal state and the builder cleans up its seeded issues
Then the stub Jira server received exactly one delete request, for "BSB-301" in project "BSB", "OTHER-7" in project "OTHER" still exists, and the "run_jira" row for run 21 has cleaned_at "2026-11-16T11:06:00Z" and cleaned_count 1

### Covered requirements (traceability)
- FR-061

### Out of scope
Seeding, validation and rollback after a failed seed (BSB-28-PENDING-1); alias resolution
(BSB-28-PENDING-2); recording the post-run Jira state (BSB-28-PENDING-3, which runs before this
cleanup); the nightly sweep of leftovers (BSB-28-PENDING-5); deleting or modifying any issue
without the exact run marker, including human-created issues; deleting a run's output branch,
bundle, logs or report; changing the run's outcome, result_status or final_verdict; configuring
the Jira integration (BSB-23).

### Notes / dependencies
Depends on BSB-28-PENDING-1 for the seeded issues and the marker, on BSB-28-PENDING-3 for the
pre-cleanup snapshot, on BSB-23-PENDING-1 for the Jira integration and its test credential, and on
BSB-26 / BSB-27 for the terminal state. Cleanup runs whenever the run reaches a terminal state,
whether completed or failed, and it runs after the post-run state is recorded so the snapshot
still describes the seeded issues. The deletion selection is exactly the issues in the
integration's configured project carrying the label "skilltest-" plus this run's id; an issue
without that exact label is never selected, which is the safety boundary the epic states.

This story adds "run_jira.cleaned_count" (integer, NULL until a cleanup attempt succeeds) so the
report can state how many issues it deleted; the data-model stage must record it. Setting
"run_jira.cleaned_at" and "cleaned_count" makes the cleanup observable and idempotent: a repeated
terminal event or a retry deletes nothing and leaves both values unchanged. If any delete fails,
the builder still attempts the remaining deletes, leaves "cleaned_at" and "cleaned_count" NULL and
shows the cleanup as pending; the surviving marker is then the nightly sweep's work (PENDING-5).
Cleanup never changes the run's outcome or verdict.

---

## STORY: BSB-28-PENDING-5

**Title:** See leftover fixture issues swept nightly, and real Jira issues left alone
**Epic:** BSB-28 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-9, Later

### Story
As a **project owner**, I want **a nightly sweep that removes Jira issues left behind with a run marker and reports what it removed**, so that **stale test data does not accumulate in the test Jira project while human-created and active-run issues are never touched**.

### Acceptance Criteria

Scenario: The nightly sweep removes marked leftovers and the project shows the result
Given Project Atlas (id 7) with an "integrations" row id 6 with project_id 7, kind "jira", config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "BSB", "test_only": true} and secret_ref "skill-builder/7/integration-6", a secret store holding "jira-test-token-9f2c" at that path, "runs" rows id 21 with state "completed" and id 22 with state "failed", an empty "fixture_sweeps" table, a stub Jira server in which project "BSB" holds "BSB-301" and "BSB-302" labelled "skilltest-21", "BSB-303" labelled "skilltest-22", human issue "BSB-401" with no label and human issue "BSB-402" labelled "repro", and a builder clock reading "2026-11-16T02:00:00Z"
When the nightly fixture sweep runs with the clock at "2026-11-16T02:00:00Z"
Then the stub Jira server received delete requests for exactly "BSB-301", "BSB-302" and "BSB-303", "BSB-401" and "BSB-402" still exist, a "fixture_sweeps" row exists for integration 6 with started_at "2026-11-16T02:00:00Z", finished_at "2026-11-16T02:00:00Z", deleted_count 3 and error NULL, and GET "/projects/7/integrations" renders "Jira test data: last sweep 2026-11-16T02:00:00Z — 3 issues removed"

Scenario: A marker for a run still in progress is left for end-of-run cleanup
Given Project Atlas (id 7) with Jira integration 6, a "runs" row id 23 with project_id 7, state "running" and kind "run", an empty "fixture_sweeps" table, a stub Jira server in which project "BSB" holds "BSB-304" labelled "skilltest-23", and a builder clock reading "2026-11-16T02:00:00Z"
When the nightly fixture sweep runs
Then "BSB-304" still exists, the "runs" row id 23 still has state "running", a "fixture_sweeps" row exists for integration 6 with deleted_count 0 and error NULL, and GET "/projects/7/integrations" renders "Jira test data: last sweep 2026-11-16T02:00:00Z — 0 issues removed"

Scenario: An orphaned marker with no run row is removed
Given Project Atlas (id 7) with Jira integration 6, no "runs" row id 99, an empty "fixture_sweeps" table, a stub Jira server in which project "BSB" holds "BSB-305" labelled "skilltest-99", and a builder clock reading "2026-11-16T02:00:00Z"
When the nightly fixture sweep runs
Then the stub Jira server received a delete request for "BSB-305", a "fixture_sweeps" row exists for integration 6 with deleted_count 1 and error NULL, and GET "/projects/7/integrations" renders "Jira test data: last sweep 2026-11-16T02:00:00Z — 1 issue removed"

Scenario: Labels that only resemble the marker are not selected
Given Project Atlas (id 7) with Jira integration 6, a "runs" row id 21 with project_id 7, kind "run" and state "completed", an empty "fixture_sweeps" table, a stub Jira server in which project "BSB" holds "BSB-306" labelled "skilltest-manual", "BSB-307" labelled "skilltest-" and "BSB-308" labelled "skilltest-21-extra", and a builder clock reading "2026-11-16T02:00:00Z"
When the nightly fixture sweep runs
Then the stub Jira server received zero delete requests, "BSB-306", "BSB-307" and "BSB-308" still exist, a "fixture_sweeps" row exists for integration 6 with deleted_count 0 and error NULL, and GET "/projects/7/integrations" renders "Jira test data: last sweep 2026-11-16T02:00:00Z — 0 issues removed"

Scenario: A project whose Jira is unavailable does not block other projects
Given Project Atlas (id 7) with Jira integration 6 and project 8 with an "integrations" row id 9 with project_id 8, kind "jira", config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "OPS", "test_only": true} and secret_ref "skill-builder/8/integration-9", a secret store holding "jira-test-token-8a1b" at that path, a "runs" row id 31 with project_id 8, state "completed" and kind "run", a stub Jira server that returns HTTP 503 "Service Unavailable" for the project "BSB" issue list and succeeds for project "OPS" where it holds "OPS-10" labelled "skilltest-31" and human issue "OPS-11" with no label, an empty "fixture_sweeps" table, and a builder clock reading "2026-11-16T02:00:00Z"
When the nightly fixture sweep runs
Then the stub Jira server received a delete request for "OPS-10" in project "OPS", "OPS-11" still exists, the stub Jira server received no delete request for any project "BSB" issue, a "fixture_sweeps" row for integration 6 has deleted_count NULL and error "The Jira fixture sweep failed for this project.", a "fixture_sweeps" row for integration 9 has deleted_count 1 and error NULL, GET "/projects/7/integrations" renders "Jira test data: last sweep failed for this project." and GET "/projects/8/integrations" renders "Jira test data: last sweep 2026-11-16T02:00:00Z — 1 issue removed"

Scenario: A second sweep removes nothing
Given Project Atlas (id 7) with Jira integration 6, "runs" rows id 21 and id 22 with terminal states, a "fixture_sweeps" table with one completed sweep row for integration 6, a stub Jira server in which project "BSB" holds only human issues "BSB-401" and "BSB-402" and no issue carries a valid run marker, and a builder clock reading "2026-11-17T02:00:00Z"
When the nightly fixture sweep runs
Then the stub Jira server received zero delete requests, a "fixture_sweeps" row exists for integration 6 with deleted_count 0 and error NULL, "BSB-401" and "BSB-402" still exist, and GET "/projects/7/integrations" renders "Jira test data: last sweep 2026-11-17T02:00:00Z — 0 issues removed"

### Covered requirements (traceability)
- FR-062

### Out of scope
End-of-run cleanup, which is the first attempt for a normal run (BSB-28-PENDING-4); seeding and
rollback (BSB-28-PENDING-1); alias resolution (BSB-28-PENDING-2); recording the post-run Jira
state (BSB-28-PENDING-3); deleting issues without an exact valid run marker, including
human-created issues and issues whose labels only resemble a marker; sweeping a Jira integration
that is not the project's configured test integration; defining the scheduler, installation
settings or run frequency beyond the nightly invocation this story observes; changing any run's
state or outcome.

### Notes / dependencies
Depends on BSB-28-PENDING-1 for the marker convention, on BSB-28-PENDING-4 for normal
end-of-run cleanup and "run_jira.cleaned_at", on BSB-23-PENDING-1 for the Jira integration and its
test credential, and on BSB-22-PENDING-4 for the project integrations page the last-sweep line is
added to. The sweep visits every "integrations" row of kind "jira" whose config marks it
"test_only": true and, in that integration's configured "project_key", selects issues whose labels
contain an exact token matching skilltest- followed by one or more digits. A label such as
"skilltest-manual" or "skilltest-21-extra" is not a marker. Unmarked issues are never selected.

For each marker, the sweep reads the run id from the label. A run in a non-terminal state
(requested, preparing, prepared or running) is left for its own end-of-run cleanup; a terminal run
(completed, failed or preparation_failed) and a marker whose run row does not exist are leftovers
and are deleted. BSB-27's deadline guarantees that a run does not remain non-terminal forever, so
the skip is bounded. Each integration's result is recorded in the new "fixture_sweeps" table;
a failure in one project is recorded and does not stop the other projects, and a failed project's
issues are not partially deleted beyond the requests Jira accepted. The project integrations page
shows the latest sweep row for that project's Jira integration. The sweep's nightly trigger is an
implementation detail; this story asserts the invocation's effect, not the scheduler.
