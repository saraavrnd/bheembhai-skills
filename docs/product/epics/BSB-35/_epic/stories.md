# Stories — BSB-35 (Skill history & run comparison)

Source: Jira epic **BSB-35** — *Skill history & run comparison* (feature area FA-14, release Later,
labels FA-14, Later; status To Do), fetched read-only from the Atlassian project
`bheembhai-skill-builder`; its summary, description, functional scope, goal, stated edge cases and
covered-requirement list are the same as the BSB-35 section of `docs/product/epics.md`. The
requirement IDs mapped to the epic are in `docs/product/epic-map.json`.

Epic BSB-35 covers 3 requirements. They decompose into the 3 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-35`), is epic
**BSB-35**. The Atlassian MCP server exposed no tools in this session (the `.mcp.json` entry passes
`args` as a string where Claude Code expects an array), so the epic was fetched read-only through
the Atlassian REST API using the `JIRA_EMAIL`/`JIRA_API_TOKEN` credentials in the environment.
Nothing was written to Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-104 | BSB-35-PENDING-1 |
| FR-105 | BSB-35-PENDING-2 |
| FR-106 | BSB-35-PENDING-3 |

The epic's two stated edge cases are covered explicitly: runs from different skills cannot be
compared (BSB-35-PENDING-2: 409 `skill_mismatch`), and a check that did not exist in the older run
is shown as `new` rather than as a flip (BSB-35-PENDING-3). A check that existed only in the older
run is the symmetric `removed` case. The non-goals are respected: there are no saved suites or
scheduled runs (FA-16, epic BSB-37), and the compare view takes run ids only — it never compares an
arbitrary commit or branch that has no run row.

## History, compare and flip contract (test fixture constants)

Every scenario below starts from this fixed deployment, database and session fixture unless it says
otherwise. The member session, the local `users` rows and the `skill-builders` gate are established
by epic BSB-18. The projects and their `project_members` rows are established by epic BSB-22. The
`runs` row, its state vocabulary, its `skill`, `skills_commit_sha`, `input_branch` and
`run_branch` columns are epic BSB-26's (with `skills_commit_sha` resolved by epic BSB-25).
`runs.final_verdict` and the `verification` block, including its `checks` array, are epic BSB-29's.
Epic BSB-34's purge clears `runs.verification` and keeps `runs.final_verdict`. The `runs` columns
follow `docs/adr/SK-001-skill-builder.md` §9.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T13:00:00Z` |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing` |
| `projects` fixture | project `7` = `Payment regression`, `owner_id` = `42`; project `8` = `Cache migration`, `owner_id` = `43` |
| `project_members` fixture | `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)`, `(project_id 8, user_id 43, role owner)`, `(project_id 8, user_id 44, role member)`; Ada has no row for project `8` |
| Current time | `2026-11-15T12:00:00Z` unless a scenario fixes another time |

**Runs fixture.** Every row has `kind` = `run` unless its row says otherwise. `verification` is the
`runs.verification` JSONB value; `checks` is its `checks` array verbatim. A `NULL` `verification`
means the run has no verification record (it is still running, its runtime never started, or epic
BSB-34 purged its evidence).

| id | project_id | user_id | skill | state | final_verdict | verification / checks | evidence_purged_at | created_at |
|----|-----------|---------|-------|-------|---------------|-----------------------|--------------------|------------|
| 1 | 7 | 42 | `sdlc-fix-bug-triage` | `completed` | `completed` | `{"status":"passed","checks":[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"passed","message":"required change present"},{"id":"scope","status":"passed","message":"within scope"}]}` | `NULL` | `2026-11-15T09:00:00Z` |
| 2 | 7 | 43 | `sdlc-fix-bug-triage` | `completed` | `changes_requested` | `{"status":"passed","checks":[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"failed","message":"required change missing"},{"id":"new-check","status":"passed","message":"new rubric satisfied"}]}` | `NULL` | `2026-11-15T11:00:00Z` |
| 3 | 7 | 42 | `sdlc-fix-bug-triage` | `running` | `NULL` | `NULL` | `NULL` | `2026-11-15T10:30:00Z` |
| 4 | 7 | 42 | `sdlc-fix-bug-triage` | `completed` | `completed` | `NULL` (purged) | `2026-11-15T08:30:00Z` | `2026-11-15T08:00:00Z` |
| 5 | 8 | 43 | `sdlc-fix-bug-triage` | `completed` | `completed` | `{"status":"passed","checks":[{"id":"artifact-contract","status":"passed"}]}` | `NULL` | `2026-11-15T12:00:00Z` |
| 6 | 7 | 42 | `sdlc-fix-bug-reproduce` | `completed` | `completed` | `{"status":"passed","checks":[{"id":"must-change","status":"passed"}]}` | `NULL` | `2026-11-15T12:30:00Z` |
| 7 | 7 | 42 | `sdlc-fix-bug-triage` | `failed_infra` | `NULL` | `NULL` | `NULL` | `2026-11-15T07:00:00Z` |
| 8 | 7 | 42 | `sdlc-fix-bug-triage` | `completed` | `completed` | `{"status":"passed","checks":[]}` | `NULL` | `2026-11-15T06:00:00Z` |
| 9 | 7 | 42 | `sdlc-fix-bug-triage` | `completed` | `changes_requested` | `{"status":"passed","checks":[{"id":"must-change","status":"failed"}]}` | `NULL`; `kind` = `reverify`, `parent_run_id` = `1` | `2026-11-15T11:30:00Z` |

`skills_commit_sha` and `input_branch` per run:

| id | `skills_commit_sha` | `input_branch` |
|----|--------------------|----------------|
| 1 | `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` | `main` |
| 2 | `5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e` | `release/2.4` |
| 3 | `6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f` | `main` |
| 4 | `7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a` | `main` |
| 5 | `8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b` | `main` |
| 6 | `9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c` | `main` |
| 7 | `0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d` | `main` |
| 8 | `1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f2e` | `main` |
| 9 | `2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e7d6c5b4a3f` | `main` |

**History contract.** Two routes read the same query and render the same rows:

| Route | Response |
|-------|----------|
| `GET https://builder.skillbuilder.internal/skills/{skill}/history` | HTML page, HTTP 200, `Content-Type: text/html; charset=utf-8` |
| `GET https://builder.skillbuilder.internal/api/skills/{skill}/history` | JSON, HTTP 200, `Content-Type: application/json` |

The history query selects rows from `runs` where `runs.skill` = the path skill, `runs.kind` =
`run`, and the requester has a `project_members` row for `runs.project_id`. A `reverify` row is not
a test run and is not listed. Rows are ordered by `runs.created_at` descending, then `runs.id`
descending. Every row is listed; there is no pagination or result cap.

Each row object is exactly:

```
{"run_id":<id>,"project_id":<project_id>,"skills_commit_sha":"<40 lowercase hex>","input_branch":"<branch>","state":"<runs.state>","final_verdict":<verdict or null>,"checks":<array or null>,"evidence_purged":<boolean>,"created_at":"<ISO-8601 UTC>"}
```

`checks` is `null` exactly when `runs.verification` is `NULL`; otherwise it is the run's
`verification.checks` array reduced to `{"id":<id>,"status":<status>}` objects and ordered by `id`
ascending in Unicode code-point order. `message` and timing fields are not part of a history row.
`evidence_purged` is `true` exactly when `runs.evidence_purged_at` is not `NULL`.

The page renders one `<tr>` per row with `id="run-<run_id>"`, in the same order, inside
`<table id="skill-history">`, under `<h1 id="history-skill">{skill}</h1>`. Each row's cells are
`<td id="run-<run_id>-sha">`, `<td id="run-<run_id>-input-branch">`,
`<td id="run-<run_id>-verdict">` and `<td id="run-<run_id>-checks">`. Their exact text:

| Cell | Exact text |
|------|------------|
| sha | `skills_commit_sha` |
| input branch | `input_branch` |
| verdict | `final_verdict` when not `NULL`; `Pending` when `final_verdict` is `NULL` and `state` is `queued` or `running`; `Not verified` when `final_verdict` is `NULL` in any other state |
| checks | `id: status` for each check joined by `; ` in id order; `No checks recorded` when `checks` is `[]`; `Pending` when `checks` is `null` and `state` is `queued` or `running`; `Not retained (evidence purged)` when `checks` is `null` and `evidence_purged` is `true`; `Not recorded` when `checks` is `null` in any other state |

A skill with no accessible runs renders the exact text `No runs for this skill.` and the API returns
`runs` = `[]`. An unknown skill is not an error: it is the same empty result.

**Compare contract.** Two routes read the same two runs:

| Route | Response |
|-------|----------|
| `GET https://builder.skillbuilder.internal/runs/compare?left={run_id}&right={run_id}` | HTML page, HTTP 200, `Content-Type: text/html; charset=utf-8` |
| `GET https://builder.skillbuilder.internal/api/runs/compare?left={run_id}&right={run_id}` | JSON, HTTP 200, `Content-Type: application/json` |

`left` and `right` are run ids, not commit SHAs or branches. The builder loads both `runs` rows.
For each run it first applies epic BSB-18's session and group gates, then requires a
`project_members` row for that run's `project_id`; a run in a project the caller is not a member of
is reported as not found, so the route never discloses another project's run. Both runs must have
the same `runs.skill`; the response's `skill` is that value.

The JSON body contains these three keys (BSB-35-PENDING-3 adds the `older_run_id`,
`newer_run_id`, `flipped`, `new`, `removed` and `comparison_unavailable` keys described below):

```
{"skill":"<skill>","left":<run object>,"right":<run object>}
```

Each run object is the history row object defined above. The page renders
`<table id="run-comparison">` with a header row whose second and third header cells are
`<th>Run <left id></th>` and `<th>Run <right id></th>`, and one row per compared field with the
cells `<td id="left-sha">`, `<td id="right-sha">`, `<td id="left-input-branch">`,
`<td id="right-input-branch">`, `<td id="left-verdict">`, `<td id="right-verdict">`,
`<td id="left-checks">` and `<td id="right-checks">`. The values are the same cell texts as the
history row: SHA, input branch, verdict and checks. The page also contains
`<span id="compare-skill">{skill}</span>`. The left column is always the run passed as `left` and
the right column the run passed as `right`, whatever their creation times.

Request errors use the shared body `{"error":{"code":"code_value","message":"message text"}}` and
apply identically to the page and the API (the page returns the error as JSON):

| Condition | Status | `code` | `message` exactly |
|-----------|--------|--------|-------------------|
| `left` or `right` is missing, not an integer, or less than `1` | 422 | `invalid_comparison_request` | `Both left and right run ids must be positive integers.` |
| a run does not exist, or the caller is not a member of its project | 404 | `run_not_found` | `Run <id> does not exist.` |
| `left` = `right` | 409 | `same_run` | `Choose two different runs to compare.` |
| the two runs have different `skill` values | 409 | `skill_mismatch` | `Runs <left id> and <right id> are not runs of the same skill.` |

A caller who is not a member of both projects is refused even when both runs exist; the 404 is the
same one an unknown run gets.

**Flipped-check contract.** The comparison reads the same check representation epic BSB-29 stores
at `runs.verification->'checks'`: each check has an `id` and a `status`. The older run is the one
with the smaller `(created_at, run_id)`; the newer run is the other one, so the direction is
independent of which id was passed as `left`. Both runs must have a recorded `verification` with a
`checks` array (an empty array counts). If either run's `checks` is `null`, the flip lists cannot be
computed (see `comparison_unavailable`).

For every check id present in both runs, a `status` difference is one flip
`{"check":"<id>","from":"<older status>","to":"<newer status>"}`. A check id present only in the
newer run is `new`; a check id present only in the older run is `removed`; neither is a flip. The
`flipped`, `new` and `removed` arrays are each sorted by `check` ascending in Unicode code-point
order. A check whose `message` or timing changed but whose `status` is the same is not a flip.

The JSON body is exactly:

```
{"skill":"<skill>","left":<run object>,"right":<run object>,"older_run_id":<id>,"newer_run_id":<id>,"flipped":<array or null>,"new":<array or null>,"removed":<array or null>,"comparison_unavailable":<reason or null>}
```

`flipped` entries are `{"check":"<id>","from":"<older status>","to":"<newer status>"}`; `new`
entries are `{"check":"<id>","status":"<newer status>"}`; `removed` entries are
`{"check":"<id>","status":"<older status>"}`. When both runs have recorded checks,
`comparison_unavailable` is `null` and all three arrays are present (possibly empty). When they do
not, all three arrays are `null` and `comparison_unavailable` is `evidence_purged` if either run's
`evidence_purged` is `true`, otherwise `run_not_verified`.

The compare page contains `<section id="compare-flips">`. When the lists are available it contains
`<h2 id="flips-heading">Changes from run <older id> to run <newer id></h2>`, then `<li>` lines in
this order: every flip as `<id>: <from> → <to>`, then every new check as
`<id>: new (<status>)`, then every removed check as `<id>: removed (<status>)`. When all three
lists are empty it contains the exact text `No checks flipped`. When the lists are unavailable it
contains `<p id="flips-unavailable">` with the exact text
`Checks not retained for comparison (run <id> evidence was purged).` for `evidence_purged`, or
`Checks not available for comparison (run <id> is not verified).` for `run_not_verified`; `<id>` is
the run whose checks are missing (the lower id if both are).

## Decisions recorded in this decomposition (confirm at review)

1. **Skill-scoped history with project-membership filtering.** FR-104 says "every run of a skill",
   and the epic's implementation guidance says to add a "skill-scoped history query". The history
   therefore keys on `runs.skill` and lists every accessible run across the requester's projects.
   Access is filtered with epic BSB-22's `project_members` rule rather than exposing every project's
   runs to every author. A caller who is not a member of any project containing the skill gets an
   empty history.
2. **"Run" means a test run.** `kind` = `run` rows are listed; a `kind` = `reverify` row is epic
   BSB-30's separate comparison artifact and is excluded. Including it would double-count one test
   run and would overlap BSB-30's re-verify comparison. If review wants re-verifications in the
   history, only the `kind` predicate and the row order change.
3. **Verdict means the final verdict.** The history and compare views show `runs.final_verdict`,
   the value epic BSB-29 records after verification and epic BSB-34 preserves when evidence is
   purged. The claimed verdict is not shown; the run report (epic BSB-33) owns that comparison.
4. **Checks mean the verifier's check results.** Both views read `runs.verification.checks` reduced
   to `id` and `status`. They do not read the four Ready checks (epic BSB-30's build-level
   aggregation) or the security-scan reports (epics BSB-31 and BSB-32), which are not per-run
   verifier checks.
5. **No pagination.** FR-104 says every run; this decomposition returns the whole list. The Later
   release scale does not justify a paging contract. A later change can add a cursor without
   changing any field in a row object.
6. **Compare takes run ids only.** The compare view never resolves a branch or commit to a run and
   never compares a commit without a run row (the epic's non-goal). A run that does not exist, is
   in a project the caller cannot see, or belongs to another skill is not comparable.
7. **Older/newer is by time, not by column.** Flips read older → newer using `(created_at,
   run_id)`, because the epic defines a missing check relative to "the older run". Swapping the
   `left` and `right` parameters swaps the two columns but not the flip direction or the meaning of
   `new` and `removed`.
8. **Presence changes are not flips.** This deliberately differs from epic BSB-30's re-verify
   comparison, which lists a one-sided check as a flip with `absent`: the BSB-35 epic explicitly
   says a check absent from the older run is shown as `new`. A check absent from the newer run is
   the symmetric `removed`.
9. **Unavailable comparison is not an error.** A purged or unverified run still has a verdict,
   commit SHA and input branch, so the two-column compare view remains useful. The JSON keeps the
   two run objects and reports `comparison_unavailable` with a reason; the page renders the reason
   inside the flips region. A 409 would discard the side-by-side view the requirement asks for.
10. **One representation, two surfaces.** The history page and API, and the compare page and API,
    share the same query and row object. A test can assert either surface; no surface adds a field
    the other does not have.

## Cross-epic notes

- **BSB-18 (access).** Every route here sits behind the session and `skill-builders` gates; this
  epic adds no authentication rule. A request without a valid session gets BSB-18's 401 and a
  signed-in non-member gets its 403 before any history or compare query runs.
- **BSB-22 (projects and membership).** The history filter and the compare authorization both use
  `project_members`. This epic adds no membership rule and never lets a caller see a run from a
  project where the caller has no membership row.
- **BSB-25 and BSB-26 (run row).** They own `runs.skill`, `skills_commit_sha`, `input_branch`,
  `run_branch`, `state` and the terminal-state vocabulary. This epic reads those columns and writes
  none of them.
- **BSB-29 (verdicts and verification).** It owns `final_verdict` and the `verification.checks`
  representation, including each check's `id` and `status`. This epic reads that representation
  unchanged and requires no new check field. A terminal run whose runtime never started keeps
  `final_verdict` and `verification` `NULL`; history shows `Not verified` and `Not recorded`.
- **BSB-30 (re-verification).** It owns the re-verify comparison and its `absent` semantics. This
  epic does not change it and does not list `kind` = `reverify` rows; it uses its own `new` and
  `removed` outcome for independent runs, as the BSB-35 epic requires.
- **BSB-33 (run report).** It owns the run page and the full per-run report. History rows link to
  `https://builder.skillbuilder.internal/projects/{project_id}/runs/{run_id}` but this epic adds no
  run-page region. The per-check detail, messages and timing stay on the run report.
- **BSB-34 (retention and purge).** Its purge sets `runs.verification` to `NULL` and keeps
  `runs.final_verdict` and the usage columns. History therefore keeps the verdict and reports the
  checks as `Not retained (evidence purged)`; compare still shows both runs but reports
  `comparison_unavailable` = `evidence_purged`.
- **BSB-37 (command line).** A CLI history or compare command is not required by this epic; the
  pages and JSON APIs are the whole surface.
- **BSB-38 (accessibility).** The history table, compare table and flips region are builder web
  surfaces; their WCAG 2.1 AA and 320-pixel reflow checks belong to BSB-38 and add no requirement
  here.

---

## STORY: BSB-35-PENDING-1

**Summary:** List a skill's accessible runs with commit SHA, input branch, verdict and checks on page and API
**Epic:** BSB-35 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-14, Later

### Story
As a **skill author**, I want **to open a skill's history and see every run with its commit SHA, input branch, verdict and checks**, so that **I can see how the skill's results changed over time without opening each run report**.

### Acceptance Criteria

#### Scenario: Every accessible run is listed newest first with its four fields
Given Ada is a member of project `7` and is not a member of project `8`
And runs `1`, `2`, `3` and `4` exist with the fixture values above
When Ada requests `GET https://builder.skillbuilder.internal/skills/sdlc-fix-bug-triage/history` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the page contains `<h1 id="history-skill">sdlc-fix-bug-triage</h1>`
And the `<tr>` ids inside `<table id="skill-history">` in document order are exactly `run-2`, `run-3`, `run-1`, `run-4`
And the `run-<id>-sha` cell of every listed row contains exactly that run's `skills_commit_sha`
And the page contains `<td id="run-2-sha">5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e</td>`
And the page contains `<td id="run-2-input-branch">release/2.4</td>`
And the page contains `<td id="run-2-verdict">changes_requested</td>`
And the page contains `<td id="run-2-checks">artifact-contract: passed; must-change: failed; new-check: passed</td>`
And the page contains `<td id="run-1-sha">4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b</td>`
And the page contains `<td id="run-1-input-branch">main</td>`
And the page contains `<td id="run-1-verdict">completed</td>`
And the page contains `<td id="run-1-checks">artifact-contract: passed; must-change: passed; scope: passed</td>`

#### Scenario: The history API returns the same rows as JSON
Given Ada is a member of project `7`
And only runs `1` and `2` exist for skill `sdlc-fix-bug-triage`
When Ada requests `GET https://builder.skillbuilder.internal/api/skills/sdlc-fix-bug-triage/history` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: application/json`
And the response body is exactly `{"skill":"sdlc-fix-bug-triage","runs":[{"run_id":2,"project_id":7,"skills_commit_sha":"5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e","input_branch":"release/2.4","state":"completed","final_verdict":"changes_requested","checks":[{"id":"artifact-contract","status":"passed"},{"id":"must-change","status":"failed"},{"id":"new-check","status":"passed"}],"evidence_purged":false,"created_at":"2026-11-15T11:00:00Z"},{"run_id":1,"project_id":7,"skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","input_branch":"main","state":"completed","final_verdict":"completed","checks":[{"id":"artifact-contract","status":"passed"},{"id":"must-change","status":"passed"},{"id":"scope","status":"passed"}],"evidence_purged":false,"created_at":"2026-11-15T09:00:00Z"}]}`

#### Scenario: Pending, unverified and purged runs show an explicit state instead of a blank cell
Given Ada is a member of project `7`
And runs `3`, `4`, `7` and `8` exist with the fixture values above
When Ada requests `GET https://builder.skillbuilder.internal/skills/sdlc-fix-bug-triage/history` carrying the `sb_session` cookie
Then the page contains `<td id="run-3-verdict">Pending</td>`
And the page contains `<td id="run-3-checks">Pending</td>`
And the page contains `<td id="run-7-verdict">Not verified</td>`
And the page contains `<td id="run-7-checks">Not recorded</td>`
And the page contains `<td id="run-4-verdict">completed</td>`
And the page contains `<td id="run-4-checks">Not retained (evidence purged)</td>`
And the page contains `<td id="run-8-verdict">completed</td>`
And the page contains `<td id="run-8-checks">No checks recorded</td>`
And the row ids in document order are exactly `run-3`, `run-4`, `run-7`, `run-8`

#### Scenario: Runs of another skill, another project and re-verifications are excluded
Given Ada is a member of project `7` and is not a member of project `8`
And runs `1`, `2`, `3`, `4`, `5`, `6` and `9` exist with the fixture values above
When Ada requests `GET https://builder.skillbuilder.internal/skills/sdlc-fix-bug-triage/history` carrying the `sb_session` cookie
Then the `<tr>` ids inside `<table id="skill-history">` in document order are exactly `run-2`, `run-3`, `run-1`, `run-4`
And the page has no element with id `run-5`
And the page has no element with id `run-6`
And the page has no element with id `run-9`
And the page does not contain the text `sdlc-fix-bug-reproduce`

#### Scenario: A skill with no accessible runs shows the empty state
Given Ada is a member of project `7`
And no `kind` = `run` row with `skill` = `sdlc-unknown-skill` exists in any project Ada belongs to
When Ada requests `GET https://builder.skillbuilder.internal/skills/sdlc-unknown-skill/history` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the page contains exactly `No runs for this skill.`
And the page has no element with id `run-1`
When Ada requests `GET https://builder.skillbuilder.internal/api/skills/sdlc-unknown-skill/history` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: application/json`
And the response body is exactly `{"skill":"sdlc-unknown-skill","runs":[]}`

### Covered requirements (traceability)
- FR-104

### Out of scope
Reporting each run's full detail, messages, timing, diff, Jira changes or security scans (epic BSB-33). Listing `kind` = `reverify` rows, which epic BSB-30 owns (decision 2). Showing the claimed verdict alongside the final verdict (epic BSB-33, FR-098 and FR-158). Starting, re-running or re-verifying a run (epics BSB-26, BSB-27 and BSB-30). Pagination, filtering, sorting controls or a project chooser. Saved suites or scheduled runs (FA-16, epic BSB-37).

### Notes / dependencies
- Depends on epic BSB-26 for the `runs` row and its skill, SHA, input branch and state, epic
  BSB-25 for the resolved `skills_commit_sha`, epic BSB-29 for `final_verdict` and
  `verification.checks`, and epics BSB-18 and BSB-22 for the session, group, project and membership
  data behind the query.
- The query joins `runs` to `project_members` on `(runs.project_id, requester user)` so the result
  is the requester's accessible slice of the skill's runs. A row in a project where the requester
  has no membership row is absent from both the page and the API, not shown as an error.
- Ordering is `created_at` descending then `id` descending, so two runs created in the same second
  still have a deterministic order.
- Checks are reduced to `id` and `status` and sorted by `id`; the full check objects, including
  `message`, stay on the run report (epic BSB-33). A run whose evidence epic BSB-34 purged has
  `checks` = `null` while `final_verdict` remains, which is why verdict and checks are displayed
  independently.
- The three empty-state rules (`Pending`, `Not verified`/`Not recorded`, `Not retained (evidence
  purged)`) let the page distinguish a run still in flight, a run whose runtime never started, and a
  run whose evidence was purged, without ever showing a blank cell.

---

## STORY: BSB-35-PENDING-2

**Summary:** Compare two runs of one skill side by side on page and API
**Epic:** BSB-35 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-14, Later

### Story
As a **skill author**, I want **to compare two runs of a skill side by side**, so that **I can judge whether a change improved or degraded the skill without re-reading each run report**.

### Acceptance Criteria

#### Scenario: Two runs of one skill are shown side by side
Given Ada is a member of project `7`
And runs `1` and `2` exist with the fixture values above
When Ada requests `GET https://builder.skillbuilder.internal/runs/compare?left=1&right=2` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the page contains `<table id="run-comparison">`
And the page contains `<span id="compare-skill">sdlc-fix-bug-triage</span>`
And the page contains `<th>Run 1</th>` and `<th>Run 2</th>`
And the page contains `<td id="left-sha">4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b</td>`
And the page contains `<td id="right-sha">5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e</td>`
And the page contains `<td id="left-input-branch">main</td>`
And the page contains `<td id="right-input-branch">release/2.4</td>`
And the page contains `<td id="left-verdict">completed</td>`
And the page contains `<td id="right-verdict">changes_requested</td>`
And the page contains `<td id="left-checks">artifact-contract: passed; must-change: passed; scope: passed</td>`
And the page contains `<td id="right-checks">artifact-contract: passed; must-change: failed; new-check: passed</td>`

#### Scenario: The compare API returns both run objects
Given Ada is a member of project `7`
And runs `1` and `2` exist with the fixture values above
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=2` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: application/json`
And the response body's `skill` is exactly `sdlc-fix-bug-triage`
And the response body's `left` is exactly `{"run_id":1,"project_id":7,"skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","input_branch":"main","state":"completed","final_verdict":"completed","checks":[{"id":"artifact-contract","status":"passed"},{"id":"must-change","status":"passed"},{"id":"scope","status":"passed"}],"evidence_purged":false,"created_at":"2026-11-15T09:00:00Z"}`
And the response body's `right` is exactly `{"run_id":2,"project_id":7,"skills_commit_sha":"5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e","input_branch":"release/2.4","state":"completed","final_verdict":"changes_requested","checks":[{"id":"artifact-contract","status":"passed"},{"id":"must-change","status":"failed"},{"id":"new-check","status":"passed"}],"evidence_purged":false,"created_at":"2026-11-15T11:00:00Z"}`

#### Scenario: Runs of different skills are not comparable
Given Ada is a member of project `7`
And run `1` is of skill `sdlc-fix-bug-triage` and run `6` is of skill `sdlc-fix-bug-reproduce`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=6` carrying the `sb_session` cookie
Then the response is HTTP 409 with `Content-Type: application/json`
And the response body is exactly `{"error":{"code":"skill_mismatch","message":"Runs 1 and 6 are not runs of the same skill."}}`
And the page `GET https://builder.skillbuilder.internal/runs/compare?left=1&right=6` returns the same status and body

#### Scenario: An unknown or inaccessible run is not found
Given Ada is a member of project `7` and is not a member of project `8`
And run `5` is in project `8`
And run `999` does not exist
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=999` carrying the `sb_session` cookie
Then the response is HTTP 404 with `Content-Type: application/json`
And the response body is exactly `{"error":{"code":"run_not_found","message":"Run 999 does not exist."}}`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=5` carrying the `sb_session` cookie
Then the response is HTTP 404 with `Content-Type: application/json`
And the response body is exactly `{"error":{"code":"run_not_found","message":"Run 5 does not exist."}}`

#### Scenario: A run cannot be compared with itself
Given Ada is a member of project `7`
And run `1` exists
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=1` carrying the `sb_session` cookie
Then the response is HTTP 409 with `Content-Type: application/json`
And the response body is exactly `{"error":{"code":"same_run","message":"Choose two different runs to compare."}}`

#### Scenario: A missing or malformed run id is rejected
Given Ada is a member of project `7`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1` carrying the `sb_session` cookie
Then the response is HTTP 422 with `Content-Type: application/json`
And the response body is exactly `{"error":{"code":"invalid_comparison_request","message":"Both left and right run ids must be positive integers."}}`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=abc&right=2` carrying the `sb_session` cookie
Then the response is HTTP 422 with `Content-Type: application/json`
And the response body is exactly `{"error":{"code":"invalid_comparison_request","message":"Both left and right run ids must be positive integers."}}`

### Covered requirements (traceability)
- FR-105

### Out of scope
Highlighting or computing flipped checks (BSB-35-PENDING-3). Reporting each run's full detail, messages, diff, Jira changes or security scans (epic BSB-33). Comparing a branch or commit that has no run row (the epic's non-goal). Selecting runs through a UI widget beyond the `left` and `right` run ids. Cross-skill comparison; it is refused. Saved suites or scheduled runs (FA-16, epic BSB-37).

### Notes / dependencies
- Depends on epic BSB-26 for the run rows and epics BSB-18 and BSB-22 for the session, group,
  project and membership checks. It reads `final_verdict` and `verification.checks` from epic
  BSB-29 without changing them.
- `left` and `right` are run ids only, so a commit SHA or branch name cannot be compared unless it
  has a run row. This is the epic's "no comparison of arbitrary commits without runs" non-goal.
- A run in a project the caller cannot see is reported exactly as an unknown run (404
  `run_not_found`), so the compare route cannot be used to probe another project's run ids.
- The two run objects are the same objects the history returns (decision 10), so a compare page can
  link each column to `GET https://builder.skillbuilder.internal/projects/{project_id}/runs/{run_id}`
  and a test can reuse the history row expectations.
- The page and the API share the same validation and authorization; the error table above applies
  to both, and the page returns the shared JSON error body for a failed request.

---

## STORY: BSB-35-PENDING-3

**Summary:** Highlight checks that flipped between two compared runs on page and API
**Epic:** BSB-35 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-14, Later

### Story
As a **skill author**, I want **the compare view to highlight the checks that flipped between the two runs**, so that **I can see exactly which behaviours a change improved or degraded**.

### Acceptance Criteria

#### Scenario: A check that flips between the older and newer run is highlighted
Given Ada is a member of project `7`
And run `1` has checks `artifact-contract: passed`, `must-change: passed` and `scope: passed`
And run `2` has checks `artifact-contract: passed`, `must-change: failed` and `new-check: passed`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=2` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: application/json`
And the response body is exactly `{"skill":"sdlc-fix-bug-triage","left":{"run_id":1,"project_id":7,"skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","input_branch":"main","state":"completed","final_verdict":"completed","checks":[{"id":"artifact-contract","status":"passed"},{"id":"must-change","status":"passed"},{"id":"scope","status":"passed"}],"evidence_purged":false,"created_at":"2026-11-15T09:00:00Z"},"right":{"run_id":2,"project_id":7,"skills_commit_sha":"5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e","input_branch":"release/2.4","state":"completed","final_verdict":"changes_requested","checks":[{"id":"artifact-contract","status":"passed"},{"id":"must-change","status":"failed"},{"id":"new-check","status":"passed"}],"evidence_purged":false,"created_at":"2026-11-15T11:00:00Z"},"older_run_id":1,"newer_run_id":2,"flipped":[{"check":"must-change","from":"passed","to":"failed"}],"new":[{"check":"new-check","status":"passed"}],"removed":[{"check":"scope","status":"passed"}],"comparison_unavailable":null}`
And the page `GET https://builder.skillbuilder.internal/runs/compare?left=1&right=2` contains `<section id="compare-flips">`
And the page contains `<h2 id="flips-heading">Changes from run 1 to run 2</h2>`
And the page contains `<li>must-change: passed → failed</li>`
And the page does not contain `<li>must-change: failed → passed</li>`

#### Scenario: Multiple flip entries are sorted by check id
Given Ada is a member of project `7`
And run `1` has checks `must-change: passed` and `artifact-contract: failed`
And run `2` has checks `must-change: failed` and `artifact-contract: passed`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=2` carrying the `sb_session` cookie
Then `flipped` in the response body is exactly `[{"check":"artifact-contract","from":"failed","to":"passed"},{"check":"must-change","from":"passed","to":"failed"}]`
And the page contains `<li>artifact-contract: failed → passed</li>` before `<li>must-change: passed → failed</li>`

#### Scenario: A one-sided check is new or removed, never a flip
Given Ada is a member of project `7`
And run `1` has checks `artifact-contract: passed` and `scope: passed`
And run `2` has checks `artifact-contract: passed` and `new-check: passed`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=2` carrying the `sb_session` cookie
Then `flipped` in the response body is exactly `[]`
And `new` in the response body is exactly `[{"check":"new-check","status":"passed"}]`
And `removed` in the response body is exactly `[{"check":"scope","status":"passed"}]`
And the page contains `<li>new-check: new (passed)</li>`
And the page contains `<li>scope: removed (passed)</li>`
And the page does not contain `<li>new-check: passed → passed</li>`
And the page does not contain `<li>new-check: absent → passed</li>`

#### Scenario: Two runs with the same checks report no flips
Given Ada is a member of project `7`
And runs `1` and `2` both have exactly the checks `artifact-contract: passed` and `must-change: passed`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=2` carrying the `sb_session` cookie
Then `flipped` in the response body is exactly `[]`
And `new` in the response body is exactly `[]`
And `removed` in the response body is exactly `[]`
And `comparison_unavailable` in the response body is `null`
And the page contains exactly `No checks flipped`

#### Scenario: The older-to-newer direction does not depend on left and right
Given Ada is a member of project `7`
And run `1` is older than run `2`
When Ada requests `GET https://builder.skillbuilder.internal/runs/compare?left=2&right=1` carrying the `sb_session` cookie
Then the page contains `<td id="left-verdict">changes_requested</td>`
And the page contains `<td id="right-verdict">completed</td>`
And the page contains `<h2 id="flips-heading">Changes from run 1 to run 2</h2>`
And the page contains `<li>must-change: passed → failed</li>`
And `flipped` in the API response is exactly `[{"check":"must-change","from":"passed","to":"failed"}]`

#### Scenario: A purged run keeps the side-by-side view but makes flips unavailable
Given Ada is a member of project `7`
And run `1` has recorded checks
And run `4` is `completed` with checks `null` and `evidence_purged` = `true`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=4` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: application/json`
And `flipped` in the response body is `null`
And `new` in the response body is `null`
And `removed` in the response body is `null`
And `comparison_unavailable` in the response body is `evidence_purged`
And the page contains `<td id="left-sha">4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b</td>`
And the page contains `<td id="right-checks">Not retained (evidence purged)</td>`
And the page contains `<p id="flips-unavailable">Checks not retained for comparison (run 4 evidence was purged).</p>`

#### Scenario: An unverified run makes flips unavailable without hiding the runs
Given Ada is a member of project `7`
And run `1` has recorded checks
And run `7` is `failed_infra` with `final_verdict` = `NULL`, `verification` = `NULL` and `evidence_purged` = `false`
When Ada requests `GET https://builder.skillbuilder.internal/api/runs/compare?left=1&right=7` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: application/json`
And `flipped` in the response body is `null`
And `new` in the response body is `null`
And `removed` in the response body is `null`
And `comparison_unavailable` in the response body is `run_not_verified`
And the page contains `<td id="right-verdict">Not verified</td>`
And the page contains `<p id="flips-unavailable">Checks not available for comparison (run 7 is not verified).</p>`

### Covered requirements (traceability)
- FR-106

### Out of scope
Deciding what a verifier check means or adding checks (the external pinned verifier release). Comparing a re-verification with its target run (epic BSB-30, which owns the `absent` comparison). Reporting check messages, timing, diff, Jira changes or security scans (epic BSB-33). Comparing arbitrary commits or branches with no run row (the epic's non-goal). Saved suites or scheduled runs (FA-16, epic BSB-37).

### Notes / dependencies
- Depends on BSB-35-PENDING-2 for the compare route, the two run objects and the same-skill,
  membership and validation rules, and on epic BSB-29 for the `verification.checks` representation
  keyed by `id` with a `status`. It adds the `older_run_id`, `newer_run_id`, `flipped`, `new`,
  `removed` and `comparison_unavailable` fields and the `<section id="compare-flips">` region.
- A flip is a change in `status` for the same check `id`; a changed `message`, duration or timing is
  not a flip. A check present on one side only is `new` (present only in the newer run) or
  `removed` (present only in the older run), which is the epic's explicit edge case.
- The older run is chosen by `(created_at, run_id)`, so passing `left=2&right=1` swaps the columns
  but not the meaning of `from`, `to`, `new` or `removed`.
- The flips region is rendered only after both run objects, so a purged or unverified run still
  shows its commit SHA, input branch and verdict. This is deliberate (decision 9): FR-105's
  side-by-side view does not depend on FR-106's check comparison.
- The three lists are each sorted by `check` ascending in Unicode code-point order, and the page
  lists flips, then new checks, then removed checks.
