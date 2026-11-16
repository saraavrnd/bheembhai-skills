# Stories — BSB-35 (Skill history & run comparison)

Epic BSB-35 covers FR-104, FR-105 and FR-106. It is decomposed into 3 vertical slices below, and
coverage of all three requirements is verified.

The three slices are what a skill author sees when diagnosing a skill over time: every run of one
skill in one list with its commit SHA, input branch, verdict and checks (PENDING-1); two runs of
that skill shown side by side on the same four fields plus their check results (PENDING-2); and the
checks that changed between those two runs highlighted with their direction, so a regression or a
regain is visible without reading both reports (PENDING-3).

This epic is a read-only projection. It adds no table and no stored comparison state: every value
it renders already lives on the `runs` row that BSB-24 to BSB-29 write — `runs.skill`,
`runs.skills_commit_sha`, `runs.input_branch`, `runs.final_verdict` and the `runs.verification`
JSON object (ADR SK-001 section 9; the object's shape is fixed by BSB-33-PENDING-2 as
`{"verdict": "pass"|"fail", "overturned": boolean, "checks": [{"id", "level", "status",
"message"}]}`). Nothing here re-executes, re-verifies, edits or purges a run.

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than a Jira issue: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404
"Issue does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The
Atlassian MCP server is configured in `.mcp.json`, but this session exposed no Atlassian MCP
tools, so the configured site was queried read-only through its REST API. The epic being
decomposed is BSB-35, read read-only from the same site: summary "Skill history & run comparison",
type Epic, status To Do, labels FA-14/Later, and a description matching the BSB-35 section of
`epics.md`. No Jira write was attempted.

**Scope decisions (made here because the epic leaves them open, not assumed silently).**
- **Project scope.** Both views are addressed under a project:
  `GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"` and
  `GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=24"`. Project membership
  is the builder's only run-access rule (BSB-22-PENDING-1 and -PENDING-3; BSB-33 applies it to the
  run report), and `runs` already carries `project_id`. FR-104's "every run of a skill" is
  therefore every `runs` row of that skill recorded in the project the view is opened in. A
  cross-project history would need a new aggregation and access rule that no requirement or epic
  defines; it is out of scope rather than invented here.
- **"Commit SHA" is `runs.skills_commit_sha`**, the skills-repository commit whose skill version
  the run executed — not the run branch's output commit. That is the value that distinguishes two
  edits of the same skill, which is what the history is for; the output-commit diff is BSB-33's.
- **"Verdict" is `runs.final_verdict`**, the verdict after verification, rendered `PASS` or `FAIL`;
  a NULL value renders `not run` (the same distinction BSB-33-PENDING-2 makes between claimed and
  final verdict).
- **"Checks" are the entries of `runs.verification.checks`**, rendered in array order as the check
  id, its level in parentheses and its uppercase status — for example
  `manifest.valid (L0) PASS`. A NULL `verification`, or one without a readable non-empty `checks`
  array, renders the check section as `Checks: unavailable`; it is never rendered as an empty list
  or as a pass.
- **Every `runs` row counts as a run**, whatever its `state` and whether its `kind` is `run` or
  `reverify`, so failed runs and re-verification records stay visible. ADR SK-001 section 6 gives
  the compare view exactly this purpose for re-verification ("It shows which checks flipped").
  Retention and purge delete run artifacts, not the `runs` row (BSB-34), so the four displayed
  fields remain available for the history.

A single requirement is covered by exactly one story:

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-104 — the skill history lists every run of a skill with its commit SHA, input branch, verdict and checks | BSB-35-PENDING-1 | "Every run of the skill is listed newest first with its commit, input branch, verdict and checks"; "A failed run with no verification is listed as not run with checks unavailable"; "A skill with no runs shows an empty history" |
| FR-105 — the compare view shows two runs side by side | BSB-35-PENDING-2 | "The history page offers a comparison of its two most recent runs"; "Two runs are shown side by side with their commit, input branch, verdict and checks"; "An invalid selection is rejected"; "A skill with fewer than two runs offers no comparison"; "A run of a different skill is rejected"; "A run from another project is not found"; "A non-member cannot compare runs" |
| FR-106 — the compare view highlights checks that flipped between the two runs | BSB-35-PENDING-3 | "A pass-to-fail and a fail-to-pass check are highlighted with their direction"; "A check present in only one run is not a flip"; "A run with unavailable checks produces no flips" |

> New stories use draft keys `BSB-35-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-35, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-35-PENDING-1

**Title:** List every run of a skill in one history view
**Epic:** BSB-35 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-14, Later

### Story
As a **skill author who is a project member**, I want **every run of one skill listed with its commit SHA, input branch, verdict and checks**, so that **I can see which edit fixed or broke the skill without opening each run report one by one**.

### Acceptance Criteria

Scenario: Every run of the skill is listed newest first with its commit, input branch, verdict and checks
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", created_at "2026-11-14T09:00:00Z", state "completed", kind "run", final_verdict "pass" and verification {"verdict": "pass", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "must_change", "level": "L1", "status": "pass", "message": "bugfix.md changed."}]}, a "runs" row id 22 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b", input_branch "test/atlas/bug-43", created_at "2026-11-15T10:00:00Z", state "completed", kind "run", final_verdict "fail" and verification {"verdict": "fail", "overturned": true, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "must_change", "level": "L1", "status": "fail", "message": "The run did not change a file."}]}, a "runs" row id 24 with project_id 7, skill "sdlc-deliver-code-implement", skills_commit_sha "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", input_branch "test/atlas/bug-44", created_at "2026-11-16T12:00:00Z", state "completed", kind "run", final_verdict "pass" and verification {"verdict": "pass", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}]}, and a "runs" row id 31 with project_id 8, skill "sdlc-fix-bug-reproduce", skills_commit_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", input_branch "test/atlas/bug-45", created_at "2026-11-16T13:00:00Z", state "completed", kind "run", final_verdict "pass" and verification {"verdict": "pass", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}]}
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"
Then the response is HTTP 200 rendering the heading "History — sdlc-fix-bug-reproduce", the run 22 row before the run 21 row, "Commit: 8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b", "Input branch: test/atlas/bug-43", "Verdict: FAIL", "Checks: manifest.valid (L0) PASS, must_change (L1) FAIL", "Commit: 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", "Input branch: test/atlas/bug-42", "Verdict: PASS" and "Checks: manifest.valid (L0) PASS, must_change (L1) PASS", the run 21 row links to GET "/projects/7/runs/21", the run 22 row links to GET "/projects/7/runs/22", and the response renders no row for Run 24 and no "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", and renders no run from project 8 and no "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e"

Scenario: A failed run with no verification is listed as not run with checks unavailable
Given the same signed-in Ada and her "project_members" row for project 7, the "runs" row id 21 of the previous scenario, and a "runs" row id 23 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha NULL, input_branch "test/atlas/bug-44", created_at "2026-11-16T11:00:00Z", state "failed", kind "run", result_status "failed_infra", execution_error "The agent container could not be started.", final_verdict NULL and verification NULL
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"
Then the response is HTTP 200 listing the run 23 row before the run 21 row, the run 23 row renders "Commit: not recorded", "Input branch: test/atlas/bug-44", "Verdict: not run" and "Checks: unavailable", and the body contains no exception text, stack trace or the string "None"

Scenario: A skill with no runs shows an empty history
Given the same signed-in Ada and her "project_members" row for project 7, and a "runs" table whose only row is id 24 with project_id 7 and skill "sdlc-deliver-code-implement"
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"
Then the response is HTTP 200 rendering "History — sdlc-fix-bug-reproduce" and "No runs recorded for sdlc-fix-bug-reproduce.", and the body renders no "Run 24" row, no commit SHA and no exception text

Scenario: A non-owner project member can read the history
Given a signed-in skill author Bob whose local "users" id is 43 and who has a "project_members" row (project_id 7, user_id 43, role "member") for Project Atlas (id 7), and the "runs" row id 21 of the first scenario
When Bob opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"
Then the response is HTTP 200 rendering "Commit: 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", "Input branch: test/atlas/bug-42", "Verdict: PASS" and "Checks: manifest.valid (L0) PASS, must_change (L1) PASS"

Scenario: A non-member cannot read the history
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), and the "runs" row id 21 of the first scenario
When Carol opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"
Then the response is HTTP 403 with the message "You are not a member of this project.", and the body contains neither "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" nor "test/atlas/bug-42" nor "Run 21"

### Covered requirements (traceability)
- FR-104

### Out of scope
The compare view and flipped-check highlighting (BSB-35-PENDING-2 and -PENDING-3); filtering, search,
sorting controls, date ranges and pagination of the history; a cross-project or site-wide history
aggregation; deleting, purging or annotating runs and run artifacts (BSB-34); re-running or
re-verifying from the history view (BSB-27 and BSB-30 — an explicit epic non-goal); changing a past
run's recorded evidence; the run report's diff, Jira changes, turns, token usage, cost, log and
trace sections (BSB-33 and BSB-34); check messages and per-check detail in history rows (the run
report owns them); catalog submission (BSB-36); command-line history (BSB-37); viewport and
accessibility layout work (BSB-38).

### Notes / dependencies
Depends on BSB-18 for the authenticated session and the skill-builders gate, on BSB-22-PENDING-1
for Project Atlas and BSB-22-PENDING-3 for the shared project-membership check and its exact 403
message "You are not a member of this project.", on BSB-24-PENDING-1 for the `runs` row and its
`created_at`, on BSB-25-PENDING-2 for `runs.skills_commit_sha`, on BSB-26-PENDING-1 and -PENDING-3
for `runs.state`, `runs.result_status` and the terminal outcome, and on BSB-29 for
`runs.final_verdict` and `runs.verification`. The requirements that create those records exist in
those epics even where their stories are written later in the fan-out. This story only reads them;
it re-derives no value and writes nothing.

The route is `GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"`. The skill segment is the
literal `runs.skill` value; ADR SK-001 section 9 has no `skills` table, so a skill with no runs and
a skill name the builder has never seen are indistinguishable and both render the empty state
rather than a 404. Rows are ordered by `runs.created_at` descending and, when two rows share a
timestamp, by `runs.id` descending, so the newest edit is first. Every `runs` row for the skill in
the project is listed regardless of `state` or `kind`; no run is hidden because it failed or
because it is a re-verification record.

A NULL `skills_commit_sha` renders "Commit: not recorded", matching BSB-33's not-recorded
vocabulary, because a run can fail before the skills commit is resolved. A NULL `final_verdict`
renders "Verdict: not run" rather than "FAIL", and a NULL `verification` or one without a readable
non-empty `checks` array renders "Checks: unavailable" rather than an empty list. The check list
renders every entry in array order, including an L2 entry when L2 scanning was enabled, as
the check id, its level in parentheses and its uppercase status (for example
`manifest.valid (L0) PASS`); the check `message` is not shown here (the run report shows it). Each
row's run id links to that run's existing report at the route `GET "/projects/7/runs/"` followed by
the run id, which BSB-33 owns; the link is the only navigation this story adds. The compare form
that PENDING-2 adds to this page is PENDING-2's; this story renders only the history list.

The project is the authorization scope, not a filter the author can change: a run of the same
skill in another project is outside this view, and no cross-project history is invented. The
history is read-only over recorded evidence and does not re-execute, re-verify or mutate any run.
Retention and purge (BSB-34) remove run artifacts and leave the `runs` row and its verification
metadata, so a purged run still appears with its four fields and its report states its retention
status.

---

## STORY: BSB-35-PENDING-2

**Title:** Compare two runs of a skill side by side
**Epic:** BSB-35 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-14, Later

### Story
As a **skill author who is a project member**, I want **two runs of one skill shown side by side with their commit, input branch, verdict and check results**, so that **I can inspect exactly what differed between two iterations in one view**.

### Acceptance Criteria

Scenario: The history page offers a comparison of its two most recent runs
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", created_at "2026-11-14T09:00:00Z", state "completed", kind "run" and final_verdict "pass", a "runs" row id 22 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b", input_branch "test/atlas/bug-43", created_at "2026-11-15T10:00:00Z", state "completed", kind "run" and final_verdict "fail", and a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", input_branch "test/atlas/bug-44", created_at "2026-11-16T12:00:00Z", state "completed", kind "run" and final_verdict "pass"
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"
Then the response is HTTP 200 rendering a "Compare runs" form with a "Left run" select, a "Right run" select and a "Compare" button that submits GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare", both selects list the options "Run 21", "Run 22" and "Run 24", and the "Left run" select has "Run 22" selected while the "Right run" select has "Run 24" selected

Scenario: Two runs are shown side by side with their commit, input branch, verdict and checks
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", created_at "2026-11-14T09:00:00Z", state "completed", kind "run", final_verdict "pass" and verification {"verdict": "pass", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "must_change", "level": "L1", "status": "pass", "message": "bugfix.md changed."}]}, and a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", input_branch "test/atlas/bug-44", created_at "2026-11-16T12:00:00Z", state "completed", kind "run", final_verdict "fail" and verification {"verdict": "fail", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "precondition.tests", "level": "L1", "status": "fail", "message": "tests/test_fix.py does not exist."}]}
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=24"
Then the response is HTTP 200 rendering the two run header cells "Run 21" then "Run 24" in that order, "Commit: 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" in the left column and "Commit: c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1" in the right column, "Input branch: test/atlas/bug-42" in the left column and "Input branch: test/atlas/bug-44" in the right column, "Verdict: PASS" in the left column and "Verdict: FAIL" in the right column, a "manifest.valid (L0)" row with "PASS" in both columns, a "must_change (L1)" row with "PASS" in the left column and "not present" in the right column, a "precondition.tests (L1)" row with "not present" in the left column and "FAIL" in the right column, and the body contains no exception text or stack trace

Scenario: An invalid selection is rejected
Given the same signed-in Ada and her "project_members" row for project 7, and the "runs" rows 21 and 24 of the first scenario
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21" and then GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=21"
Then the first response is HTTP 422 with the message "Select two runs to compare.", the second response is HTTP 422 with the message "Choose two different runs.", and neither body renders a comparison table, a "Run 21" header cell or a commit SHA

Scenario: A skill with fewer than two runs offers no comparison
Given the same signed-in Ada and her "project_members" row for project 7, and a "runs" table whose only row is id 24 with project_id 7 and skill "sdlc-fix-bug-reproduce"
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/history"
Then the response is HTTP 200 rendering the run 24 row, "Two runs are needed to compare.", and no "Compare runs" form and no "Compare" button

Scenario: A run of a different skill is rejected
Given the same signed-in Ada and her "project_members" row for project 7, the "runs" row id 21 of the first scenario, and a "runs" row id 24 with project_id 7, skill "sdlc-deliver-code-implement", skills_commit_sha "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", input_branch "test/atlas/bug-44", state "completed", kind "run", final_verdict "pass" and verification {"verdict": "pass", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}]}
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=24"
Then the response is HTTP 422 with the message "Both runs must be for sdlc-fix-bug-reproduce.", and the body renders no comparison table and does not contain "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1"

Scenario: A run from another project is not found
Given the same signed-in Ada and her "project_members" row for project 7, the "runs" row id 21 of the first scenario, and a "runs" row id 31 with project_id 8, skill "sdlc-fix-bug-reproduce", skills_commit_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", input_branch "test/atlas/bug-45", state "completed", kind "run" and final_verdict "pass"
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=31"
Then the response is HTTP 404 with the message "Run not found.", and the body renders no comparison table and does not contain "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e"

Scenario: A non-member cannot compare runs
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), and the "runs" rows 21 and 24 of the first scenario
When Carol opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=24"
Then the response is HTTP 403 with the message "You are not a member of this project.", a follow-up GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=99&right=98" also returns HTTP 403 with that message rather than 404, and neither response body contains "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" or "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1"

### Covered requirements (traceability)
- FR-105

### Out of scope
Highlighting flipped checks and the "Checks flipped" summary (BSB-35-PENDING-3); the history rows,
their ordering and their empty state (BSB-35-PENDING-1 — this story adds only the compare form to
that page); comparing more than two runs or saving/sharing a comparison; comparing runs of
different skills or runs from different projects (epic non-goals); the code diff between input and
output branches, Jira changes, logs, traces, token usage, cost and per-check messages (BSB-33 and
BSB-34); re-running or re-verifying the compared runs and changing their recorded evidence (BSB-27
and BSB-30); a side-by-side editor or any write action; accessibility layout work (BSB-38).

### Notes / dependencies
Depends on BSB-18 for the authenticated session and the skill-builders gate, on BSB-22-PENDING-1
for Project Atlas and BSB-22-PENDING-3 for the shared project-membership check and its exact 403
message, on BSB-24-PENDING-1 for the `runs` rows, on BSB-25-PENDING-2 for `runs.skills_commit_sha`,
on BSB-26-PENDING-1 and -PENDING-3 for `runs.state` and the terminal outcome, and on BSB-29 for
`runs.final_verdict` and `runs.verification`. This story reads the same recorded values the run
report reads; it re-derives and writes none of them.

This story also adds the compare form to PENDING-1's history page. The form has two selects named
`left` and `right`, each listing every run in the history in the page's order, defaulting to the
two most recent runs with the earlier on the left and the later on the right so a later flip
arrow reads oldest to newest; its Compare button submits GET to the compare route with the two
selected ids. With fewer than two runs the form is not rendered and the page says "Two runs are
needed to compare." The form changes no record, and the history rows themselves remain
PENDING-1's.

The route is `GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=24"`. Both
`left` and `right` are required and must name distinct `runs` rows that belong to project 7 and
whose `skill` equals the route's skill segment. The left query parameter renders the left column
and the right parameter the right column; the order is the caller's, not a sort. The
project-membership check runs before either run lookup, so a non-member receives 403 even for run
ids that do not exist, and learns nothing about whether a run exists. A run that exists in another
project is treated as not found, so the route never discloses another project's run.

The comparison is a real two-column table over the same records as the history: a header cell per
run, then the commit, input branch and verdict, then one row per check id present in either run.
The check row is identified by the check `id` plus its `level` in parentheses; the left and right
cells hold that run's uppercase status. A check id absent from one run's `checks` array renders
"not present" in that run's cell rather than being hidden or treated as failed. A check id present
in both runs with statuses "pass" and "fail" is a flip, but the comparison story only renders the
two statuses; the flip marker and summary are PENDING-3's. The view is read-only: it changes no
run, creates no record and stores no comparison. The same `runs` rows always produce the same
table.

A run whose `skills_commit_sha` is NULL renders "Commit: not recorded"; a run whose `final_verdict`
is NULL renders "Verdict: not run"; and a run with no readable non-empty `checks` array renders
"Checks: unavailable" in its checks cell. When both runs have readable `checks` arrays the
comparison uses one row per check id; when either run lacks one, the comparison falls back to a
single "Checks" row with each column's rendered list or "Checks: unavailable", so the readable
side's checks stay visible and no check is paired with a status the other run never recorded.
Those fallbacks are identical to the history's, so a failed run can be one side of a comparison
without inventing a verdict. The comparison is over recorded check results only; it does not diff
code, Jira state or logs, and it never re-executes either run.

---

## STORY: BSB-35-PENDING-3

**Title:** Highlight checks that flipped between the compared runs
**Epic:** BSB-35 · **Release:** Later · **Estimate:** 3 · **Labels:** FA-14, Later

### Story
As a **skill author who is a project member**, I want **checks that flipped between two compared runs highlighted with their direction**, so that **I can spot a regression or a regain at a glance**.

### Acceptance Criteria

Scenario: A pass-to-fail and a fail-to-pass check are highlighted with their direction
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", state "completed", kind "run", final_verdict "fail" and verification {"verdict": "fail", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "must_change", "level": "L1", "status": "pass", "message": "bugfix.md changed."}, {"id": "precondition.tests", "level": "L1", "status": "fail", "message": "tests/test_fix.py does not exist."}]}, and a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", input_branch "test/atlas/bug-42", state "completed", kind "run", final_verdict "fail" and verification {"verdict": "fail", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "must_change", "level": "L1", "status": "fail", "message": "The run did not change a file."}, {"id": "precondition.tests", "level": "L1", "status": "pass", "message": "tests/test_fix.py exists."}]}
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=24"
Then the response is HTTP 200 rendering "Checks flipped: 2.", the check row "must_change (L1) — Flipped: PASS → FAIL", the check row "precondition.tests (L1) — Flipped: FAIL → PASS", and a "manifest.valid (L0)" row whose text contains no "Flipped:" marker

Scenario: A check present in only one run is not a flip
Given the same signed-in Ada and her "project_members" row for project 7, a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", state "completed", kind "run", final_verdict "pass" and verification {"verdict": "pass", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "must_change", "level": "L1", "status": "pass", "message": "bugfix.md changed."}]}, and a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", input_branch "test/atlas/bug-44", state "completed", kind "run", final_verdict "fail" and verification {"verdict": "fail", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "precondition.tests", "level": "L1", "status": "fail", "message": "tests/test_fix.py does not exist."}]}
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=24"
Then the response is HTTP 200 rendering "Checks flipped: 0.", the "must_change (L1)" row with "not present" in the right column, the "precondition.tests (L1)" row with "not present" in the left column, and no "Flipped:" text anywhere in the response

Scenario: A run with unavailable checks produces no flips
Given the same signed-in Ada and her "project_members" row for project 7, the "runs" row id 21 of the first scenario, and a "runs" row id 24 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", input_branch "test/atlas/bug-44", state "completed", kind "run", final_verdict "pass" and verification {"verdict": "pass", "overturned": false}
When Ada opens GET "/projects/7/skills/sdlc-fix-bug-reproduce/compare?left=21&right=24"
Then the response is HTTP 200 rendering "Checks: unavailable" in the right column's checks cell, "manifest.valid (L0) PASS", "must_change (L1) PASS" and "precondition.tests (L1) FAIL" in the left column's checks cell, "Checks flipped: 0.", no "Flipped:" text anywhere in the response, and no exception text or stack trace

### Covered requirements (traceability)
- FR-106

### Out of scope
Rendering the two comparison columns and choosing the two runs (BSB-35-PENDING-2); the history list
(BSB-35-PENDING-1); changing a check's recorded status or re-verifying either run (BSB-29 and
BSB-30); explaining why a check flipped or rendering its message (the run report, BSB-33); diffing
code, Jira state or logs between runs; comparing more than two runs; persisting a flip result or
saving a comparison; treating a check that is absent from one run or unavailable as a flip;
accessibility layout work (BSB-38).

### Notes / dependencies
Depends on BSB-35-PENDING-2 for the comparison table, its route and its left/right order, and on
the same prerequisite records as the other two stories: BSB-22-PENDING-3 for the shared
project-membership check, BSB-24-PENDING-1 for the `runs` rows, BSB-25-PENDING-2 for
`runs.skills_commit_sha`, and BSB-29 for `runs.verification`. This story adds no route and no
record; it extends the comparison's rendering with a computed flip marker and summary.

A flip is defined over check *identity*, which is the check `id`: a check is flipped when the same
`id` is present in both runs' `checks` arrays and one run records `"status": "pass"` while the
other records `"status": "fail"`. Both directions count — a pass in the left run and a fail in the
right is "Flipped: PASS → FAIL", and the reverse is "Flipped: FAIL → PASS". The arrow always reads
from the left column to the right column, so the caller's `left`/`right` order defines the
direction; swapping the parameters swaps the arrows. The check `level` is displayed but is not
part of identity, because `verify.yaml` check ids are unique within a run.

A check id present in only one run is rendered "not present" in the other column and is never a
flip: absence is not a failure, so it is neither highlighted nor counted. When either run has no
readable non-empty `checks` array, the comparison uses its single "Checks" row fallback instead of
per-check rows: that column renders "Checks: unavailable", no identity is paired, no flip is
marked, and the summary is "Checks flipped: 0.". The summary counts only flipped check identities
and renders "Checks flipped: N." above the table.

The marker is text as well as styling so it does not depend on colour alone: a flipped check row's
label ends with " — Flipped: " followed by the left status, an arrow and the right status, and an
unchanged row keeps the plain label of check id plus level in parentheses. The flip computation is
per request over the recorded arrays; nothing is stored, and the same two runs always produce the
same markers and count. It does not infer a flip from a verdict change, from a check's message, or
from the run branch's code; only the recorded per-check statuses count.
