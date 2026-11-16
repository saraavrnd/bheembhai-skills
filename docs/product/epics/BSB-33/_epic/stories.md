# Stories — BSB-33 (Run report & change evidence)

Epic BSB-33 covers FR-094, FR-095, FR-096, FR-097, FR-098, FR-099, FR-100, FR-101, FR-102,
FR-103, FR-140, FR-157 and FR-158. It is decomposed into 5 vertical slices below, and coverage of
all 13 requirements is verified.

The five slices are what an author or debugger reads on one run's report (and, once the reviewer
access rule below is decided, what a catalog reviewer reads too): what ran and
against which pinned components (PENDING-1), the claimed verdict against the final verdict with
every check result (PENDING-2), the code diff from the recorded baseline to the output branch
(PENDING-3), the Jira changes the run made (PENDING-4), and the recorded turn count plus the trace
link when tracing is enabled (PENDING-5).

The report is a projection. Every section renders records other epics own — `runs`,
`runs.verification`, `run_jira` and the captured `runs/<run-id>/diff.json` — and this epic adds no
separately editable report fields. It captures the diff and the Jira change evidence after the run
so the report does not drift when a branch or the tracker moves later.

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than a Jira issue: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404
"Issue does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The
Atlassian MCP tools were not exposed in this session, so the configured site was queried read-only
through its REST API. The epic being decomposed is BSB-33, read read-only from the same site:
summary "Run report & change evidence", type Epic, status To Do, labels FA-13/MVP, and a
description matching the BSB-33 section of `epics.md`. No Jira write was attempted.

**Unresolved cross-epic gap (not claimed by these stories).** The epic's final functional-scope
bullet — a stable report view that catalog reviewers can read without the authoring interface —
has no FR mapped to BSB-33 and is an open question in BSB-22's review (Open question 1) and
BSB-31's review (Finding 5). These stories define the author-facing run report at
`GET /projects/7/runs/21` under the authenticated session and BSB-22's project-membership check.
They deliberately do not invent a reviewer access rule; FR-110's link from the catalog pull
request (BSB-36) needs a human decision on that rule first.

A single requirement may appear in more than one acceptance criterion, but every requirement is
claimed by exactly one story:

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-094 — the run page shows the skill that ran | BSB-33-PENDING-1 | "A completed run's report shows what ran"; "A run that failed before component versions were recorded shows not recorded" |
| FR-095 — the run page shows the input branch | BSB-33-PENDING-1 | "A completed run's report shows what ran"; "A run that failed before component versions were recorded shows not recorded" |
| FR-096 — the run page shows the output branch | BSB-33-PENDING-1 | "A completed run's report shows what ran"; "A run that failed before component versions were recorded shows not recorded" |
| FR-097 — the run page shows the component versions used | BSB-33-PENDING-1 | "A completed run's report shows what ran"; "A run that failed before component versions were recorded shows not recorded" |
| FR-098 — the run page shows the verdict the agent claimed | BSB-33-PENDING-2 | "An upheld claim shows both verdicts and every check result"; "An overturned claim shows both verdicts"; "A run whose verification has not run shows no final verdict" |
| FR-099 — the run page shows each check result | BSB-33-PENDING-2 | "An upheld claim shows both verdicts and every check result"; "An overturned claim shows both verdicts"; "A partial verification record shows checks unavailable" |
| FR-100 — the run page shows the diff from input branch to run branch | BSB-33-PENDING-3 | "The captured diff is shown from the baseline to the output head"; "A run that changed nothing shows an empty diff"; "The shown diff is pinned to the head captured at run completion"; "A diff that was not captured is shown as unavailable" |
| FR-101 — the run page shows the Jira changes the run made | BSB-33-PENDING-4 | "The Jira changes the run made are recorded and shown"; "A run with no Jira changes shows an empty state"; "A Jira change capture that fails is shown as unavailable"; "A project with no Jira integration shows the section as not recorded" |
| FR-102 — the run page shows the run's turn count | BSB-33-PENDING-5 | "The recorded turn count and trace link are shown"; "Tracing disabled shows no trace link"; "A missing trace identifier shows trace unavailable"; "A run that recorded no turns shows not recorded" |
| FR-103 — the run page links to the run's trace when tracing is enabled | BSB-33-PENDING-5 | "The recorded turn count and trace link are shown"; "Tracing disabled shows no trace link"; "A missing trace identifier shows trace unavailable" |
| FR-140 — the builder records the Jira changes a run makes | BSB-33-PENDING-4 | "The Jira changes the run made are recorded and shown"; "A run with no Jira changes shows an empty state"; "A Jira change capture that fails is shown as unavailable" |
| FR-157 — the run page shows the skills commit SHA | BSB-33-PENDING-1 | "A completed run's report shows what ran"; "A run that failed before component versions were recorded shows not recorded" |
| FR-158 — the run page shows the final verdict after verification | BSB-33-PENDING-2 | "An upheld claim shows both verdicts and every check result"; "An overturned claim shows both verdicts"; "A run whose verification has not run shows no final verdict"; "A partial verification record shows checks unavailable" |

> New stories use draft keys in the `BSB-33-PENDING` series (`-1` to `-5`). `sdlc-tracker-sync`
> creates each story in Jira, parents it to BSB-33, and replaces the draft key with the real key in
> `story-map.json`.

---

## STORY: BSB-33-PENDING-1

**Title:** Show what ran: skill, skills commit, both branches and component versions
**Epic:** BSB-33 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **the run report to show the skill and skills commit that ran, the input and output branches, and the exact agent-image, step-kit and verifier versions**, so that **I can identify exactly what executed and reproduce its evidence later without reconstructing it from logs**.

### Acceptance Criteria

Scenario: A completed run's report shows what ran
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), and a "runs" row id 21 with project_id 7, user_id 42, build_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", agent_image_digest "sha256:3f1a9c2e5b7d4a6f8c0e2b4d6f8a1c3e5b7d9f0a2c4e6b8d0f1a3c5e7b9d2f4a", stepkit_version "bheembhai-stepkit 0.3.0", verify_version "bheembhai-verify 0.8.1", state "completed" and kind "run"
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering the heading "Run 21 — sdlc-fix-bug-reproduce", "Skill: sdlc-fix-bug-reproduce", "Skills commit: 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", "Input branch: test/atlas/bug-42", "Output branch: skilltest/21", "Agent image: sha256:3f1a9c2e5b7d4a6f8c0e2b4d6f8a1c3e5b7d9f0a2c4e6b8d0f1a3c5e7b9d2f4a", "Step kit: bheembhai-stepkit 0.3.0" and "Verifier: bheembhai-verify 0.8.1", and the body contains no exception text, stack trace or credential value

Scenario: A run that failed before component versions were recorded shows not recorded
Given the same signed-in Ada with her "project_members" row for project 7, and a "runs" row id 22 with project_id 7, user_id 42, skill "sdlc-fix-bug-reproduce", skills_commit_sha NULL, input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, agent_image_digest NULL, stepkit_version NULL, verify_version NULL, state "preparation_failed", result_status NULL, claimed_verdict NULL, final_verdict NULL, preparation_error "The selected input branch was not found in the sandbox repository." and kind "run"
When Ada opens GET "/projects/7/runs/22"
Then the response is HTTP 200 rendering "Skill: sdlc-fix-bug-reproduce", "Input branch: test/atlas/bug-42", "Skills commit: not recorded", "Output branch: not recorded", "Agent image: not recorded", "Step kit: not recorded", "Verifier: not recorded" and "Preparation error: The selected input branch was not found in the sandbox repository.", and the body contains no exception text, stack trace or the string "None"

Scenario: A non-member cannot read a run report
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for Project Atlas (id 7), and the "runs" row id 21 of the first scenario
When Carol opens GET "/projects/7/runs/21"
Then the response is HTTP 403 with the message "You are not a member of this project.", and the body contains neither "sdlc-fix-bug-reproduce" nor "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d"

Scenario: An unknown run is not disclosed
Given the same signed-in Ada with her "project_members" row for project 7, and no "runs" row id 99
When Ada opens GET "/projects/7/runs/99"
Then the response is HTTP 404 with the message "Run not found.", and the body contains no skill, branch, commit or component value

### Covered requirements (traceability)
- FR-094
- FR-095
- FR-096
- FR-097
- FR-157

### Out of scope
Creating the run and choosing its skill, branches, model profile and tier (BSB-24); resolving the
skills commit and creating the run branch and baseline (BSB-25); the run's live status, progress
and log view and the model profile/tier display (BSB-26); the verdict, check, diff, Jira, turn and
trace sections (BSB-33-PENDING-2 to -5); the security tab and scan reports (BSB-31 and BSB-32);
readiness (BSB-30); token usage, cost and retention (BSB-34); the catalog reviewer-facing stable
report view and its access rule (unresolved; see the epic gap above); the catalog pull request
(BSB-36); the command line (BSB-37).

### Notes / dependencies
Depends on BSB-18 for the authenticated session and the skill-builders gate, on BSB-22-PENDING-1
and BSB-22-PENDING-3 for Project Atlas and the shared project-membership check, on BSB-24-PENDING-1
for run 21's skill and input branch, on BSB-25-PENDING-1 and BSB-25-PENDING-2 for
`runs.skills_commit_sha`, on BSB-25-PENDING-3 for `runs.run_branch` and `runs.baseline_sha`, and
on BSB-26-PENDING-1 for `runs.agent_image_digest`, `runs.stepkit_version` and
`runs.verify_version`. This story only reads those recorded values; it re-derives none of them.

The report is `GET "/projects/7/runs/21"`, the run page BSB-26-PENDING-2 already serves, extended
with a read-only "What ran" section. The URL depends only on the project and run ids, so a later
branch move or a later run does not change it; BSB-36's description link can therefore point at
the same run report while it is within its retention window. Access remains the authenticated
session plus the project-membership check from BSB-22; "without the authoring interface" in the
epic does not mean anonymous access (NFR-002 requires a valid session), and the separate
reviewer-facing access rule is the unresolved cross-epic gap recorded above.

A missing recorded value renders as "not recorded" rather than an empty cell, "None" or a crash,
so a run whose preparation failed still has a readable report. The section never edits or writes
`runs` columns; every value comes from the row BSB-24, BSB-25 and BSB-26 wrote.

---

## STORY: BSB-33-PENDING-2

**Title:** Compare the claimed and final verdicts and read every check result
**Epic:** BSB-33 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **the run report to show the verdict the agent claimed, the final verdict after verification and every check result**, so that **I can see whether verification upheld the claim and exactly which checks passed or failed**.

### Acceptance Criteria

Scenario: An upheld claim shows both verdicts and every check result
Given a signed-in skill author Ada who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), and a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", claimed_verdict "completed", final_verdict "pass" and verification {"verdict": "pass", "overturned": false, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "must_change", "level": "L1", "status": "pass", "message": "bugfix.md changed."}, {"id": "precondition.tests", "level": "L1", "status": "pass", "message": "tests/test_fix.py exists."}, {"id": "llm.scan", "level": "L2", "status": "pass", "message": "No instruction injection found."}]}
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Claimed verdict: completed", "Verdict: PASS", "Overturned: no", "manifest.valid (L0): PASS — verify.yaml is valid.", "must_change (L1): PASS — bugfix.md changed." and "precondition.tests (L1): PASS — tests/test_fix.py exists.", "llm.scan (L2): PASS — No instruction injection found." and the body contains no exception text or stack trace

Scenario: An overturned claim shows both verdicts
Given the same signed-in Ada and project 7, and a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", claimed_verdict "completed", final_verdict "fail" and verification {"verdict": "fail", "overturned": true, "checks": [{"id": "manifest.valid", "level": "L0", "status": "pass", "message": "verify.yaml is valid."}, {"id": "must_change", "level": "L1", "status": "fail", "message": "The run did not change a file."}]}
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Claimed verdict: completed", "Verdict: FAIL", "Overturned: yes", "manifest.valid (L0): PASS — verify.yaml is valid." and "must_change (L1): FAIL — The run did not change a file.", and the body does not render "Overturned: no"

Scenario: A run whose verification has not run shows no final verdict
Given the same signed-in Ada and project 7, and a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", claimed_verdict "completed", final_verdict NULL and verification NULL
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Claimed verdict: completed", "Verdict: not run" and "No check results recorded.", and the body renders neither "Verdict: PASS" nor "Verdict: FAIL" and contains no exception text

Scenario: A partial verification record shows checks unavailable
Given the same signed-in Ada and project 7, and a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", claimed_verdict "completed", final_verdict "pass" and verification {"verdict": "pass", "overturned": false}
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Claimed verdict: completed", "Verdict: PASS", "Overturned: no" and "Check results unavailable.", and the body contains no exception text or stack trace

### Covered requirements (traceability)
- FR-098
- FR-099
- FR-158

### Out of scope
Recording the agent's claimed verdict and classifying the execution outcome (BSB-26-PENDING-3);
running the shared verification layer and writing `runs.final_verdict`, `runs.verification` and
the overturned flag (BSB-29); computing readiness across checks (BSB-30); re-verification
(BSB-30); the diff, Jira, turn and trace sections (BSB-33-PENDING-3 to -5); scan results
(BSB-31, BSB-32); changing builtin verifier checks.

### Notes / dependencies
Depends on BSB-22-PENDING-3 for the shared project-membership check, on BSB-26-PENDING-3 for
`runs.claimed_verdict` and the execution outcome, and on BSB-29 for `runs.final_verdict` and
`runs.verification`. BSB-29 owns writing those values and FR-065/FR-066/FR-067; this story owns
their read contract and presentation only.

The read contract for `runs.verification` is a JSON object with `verdict` (`"pass"` or `"fail"`),
`overturned` (boolean) and `checks` (an array). Each check entry has `id` (the check identifier
from `verify.yaml` or the builtin set), `level` (`"L0"`, `"L1"` or `"L2"` when enabled), `status`
(`"pass"` or `"fail"`) and `message` (the verifier's human-readable reason). BSB-29 must persist
that shape; this story renders every entry in array order, including any L2 entry present when
L2 scanning is enabled, and does not infer a verdict.

The two verdicts are distinct and must not be collapsed: `runs.claimed_verdict` is what the agent
said, `runs.final_verdict` is what the shared verification layer decided. The final-verification verdict is
rendered on the "Verdict:" line that BSB-32-PENDING-5's acceptance criteria already expect; the
agent's claim is on the separate "Claimed verdict:" line, so the two are never confused. A missing
`final_verdict` means verification has not run (or the run never reached verification) and renders
as "not run", not as a pass. A `verification` object without a readable `checks` array renders
"Check results unavailable." rather than an empty table or an error, so a partial record never
hides the final verdict.

---

## STORY: BSB-33-PENDING-3

**Title:** See the code diff from the input branch to the output branch
**Epic:** BSB-33 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **the run report to show the diff from the input branch's recorded baseline to the run's output-branch head, captured once when the run finishes**, so that **I can see exactly what the run changed and the evidence does not drift when the branch moves later**.

### Acceptance Criteria

Scenario: The captured diff is shown from the baseline to the output head
Given a signed-in skill author Ada who has a "project_members" row for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", input_branch "test/atlas/bug-42", run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", state "completed" and result_status "completed", and a stub source-control provider whose ref "refs/heads/skilltest/21" points at "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1" and whose compare of base "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" to head "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1" returns files [{"filename": "bugfix.md", "status": "added", "additions": 12, "deletions": 0, "patch": "@@ -0,0 +1,12 @@\n+def subtract(a, b):\n+    return a - b"}, {"filename": "src/calc.py", "status": "modified", "additions": 2, "deletions": 1, "patch": "@@ -4,1 +4,2 @@\n-def add(a, b):\n+def add(a, b):\n+    # guard"}], additions 14 and deletions 1
When the run reaches a terminal state and the builder captures the run diff, and Ada then opens GET "/projects/7/runs/21"
Then the builder's object store holds "runs/21/diff.json" with {"base_sha": "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", "head_sha": "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", "additions": 14, "deletions": 1, "files": [{"filename": "bugfix.md", "status": "added", "additions": 12, "deletions": 0, "patch": "@@ -0,0 +1,12 @@\n+def subtract(a, b):\n+    return a - b"}, {"filename": "src/calc.py", "status": "modified", "additions": 2, "deletions": 1, "patch": "@@ -4,1 +4,2 @@\n-def add(a, b):\n+def add(a, b):\n+    # guard"}]}, and the response renders "Changes: 2 files, 14 additions, 1 deletion", "bugfix.md — added (12 additions, 0 deletions)", "src/calc.py — modified (2 additions, 1 deletion)" and "def subtract(a, b):"

Scenario: A run that changed nothing shows an empty diff
Given the same signed-in Ada and project 7, a "runs" row id 22 with project_id 7, input_branch "test/atlas/bug-42", run_branch "skilltest/22", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", state "completed" and result_status "completed", and a stub source-control provider whose ref "refs/heads/skilltest/22" points at "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" and whose compare of that commit to itself returns files [], additions 0 and deletions 0
When the run reaches a terminal state and the builder captures the run diff, and Ada then opens GET "/projects/7/runs/22"
Then the builder's object store holds "runs/22/diff.json" with {"base_sha": "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", "head_sha": "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", "additions": 0, "deletions": 0, "files": []}, and the response renders "No changes between test/atlas/bug-42 and skilltest/22."

Scenario: The shown diff is pinned to the head captured at run completion
Given a "runs" row id 21 as in the first scenario whose "runs/21/diff.json" was captured with head_sha "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1", and a stub source-control provider whose ref "refs/heads/skilltest/21" has since moved to "d5e9a1c3b6f2e4a8c0d7b9f1a3e5c7b9d1f0a2c4" and whose compare counter is 1
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Changes: 2 files, 14 additions, 1 deletion" and "bugfix.md — added (12 additions, 0 deletions)", the provider's compare counter remains 1, and the body does not contain "d5e9a1c3b6f2e4a8c0d7b9f1a3e5c7b9d1f0a2c4"

Scenario: A diff that was not captured is shown as unavailable
Given the same signed-in Ada and project 7, a "runs" row id 23 with project_id 7, input_branch "test/atlas/bug-42", run_branch "skilltest/23", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", state "completed", result_status "completed" and diff_error NULL, and a stub source-control provider whose compare of the baseline to the output head returns HTTP 503 "Service Unavailable"
When the run reaches a terminal state and the builder attempts to capture the run diff, and Ada then opens GET "/projects/7/runs/23"
Then the "runs" row id 23 still has state "completed" and result_status "completed" with diff_error "The run diff could not be captured.", no object exists at "runs/23/diff.json", and the response is HTTP 200 rendering "Diff unavailable: The run diff could not be captured." with no exception text or stack trace

### Covered requirements (traceability)
- FR-100

### Out of scope
Creating the run branch and the baseline (BSB-25); executing the skill and pushing its commits
(BSB-26); verification's use of the baseline (BSB-29); readiness (BSB-30); the report's identity,
verdict, Jira, turn and trace sections (BSB-33-PENDING-1, -2, -4, -5); storing or rendering the
agent's transcript (BSB-26 and BSB-34); comparing two runs (BSB-35, Later).

### Notes / dependencies
Depends on BSB-22-PENDING-3 for the shared project-membership check, on BSB-23-PENDING-2 for the
source-control integration and its sandbox repository, on BSB-25-PENDING-3 for
`runs.baseline_sha` and `runs.run_branch`, and on BSB-26-PENDING-3 for the run reaching a terminal
state with its output branch pushed.

This story owns the one-time diff capture and its durable record: after the run reaches a
terminal state, the builder resolves the output branch's head, asks the source-control provider
for the comparison from `runs.baseline_sha` to that head, and writes `runs/<run-id>/diff.json` to
the builder's run bucket. The object carries `base_sha`, `head_sha`, per-file `filename`,
`status`, `additions`, `deletions` and `patch`, plus the totals. That object is the evidence the
report renders; the report does not call the source-control provider, so the diff cannot change
when the branch moves or when a later run pushes to it. The capture failure is recorded in
`runs.diff_error` and never changes the run's execution outcome or verdict; the report degrades to
an unavailable state.

The diff is the run's own change evidence, not a review of the catalog branch: `base_sha` is the
input branch's recorded baseline, `head_sha` is the run branch's head at completion, and the input
branch is never a diff target (the run never writes to it, FR-043).

---

## STORY: BSB-33-PENDING-4

**Title:** Record and show the Jira changes a run made
**Epic:** BSB-33 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **the builder to record the Jira issues the run created or changed, and the report to show those changes**, so that **I can see the tracker side effects of the run without diffing Jira by hand**.

### Acceptance Criteria

Scenario: The Jira changes the run made are recorded and shown
Given a signed-in skill author Ada who has a "project_members" row for Project Atlas (id 7), an "integrations" row id 6 with project_id 7, kind "jira", config {"site_url": "https://saraavrnd.atlassian.net", "project_key": "BSB", "test_only": true} and secret_ref "skill-builder/7/integration-6", a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed" and final_verdict "pass", and a stub Jira server in which project "BSB" holds issue "BSB-201" with {"summary": "Reproduce bug", "status": "To Do", "assignee": null, "labels": []} when the run starts and {"summary": "Reproduce bug", "status": "In Progress", "assignee": "ada", "labels": []} plus new issue "BSB-203" with {"summary": "Follow-up regression", "status": "To Do", "assignee": null, "labels": []} when the run finishes
When the run reaches a terminal state and the builder captures the Jira changes, and Ada then opens GET "/projects/7/runs/21"
Then the "run_jira" row for run 21 has state_before {"BSB-201": {"summary": "Reproduce bug", "status": "To Do", "assignee": null, "labels": []}}, state_after {"BSB-201": {"summary": "Reproduce bug", "status": "In Progress", "assignee": "ada", "labels": []}, "BSB-203": {"summary": "Follow-up regression", "status": "To Do", "assignee": null, "labels": []}} and changes [{"issue_key": "BSB-201", "change": "updated", "field": "status", "from": "To Do", "to": "In Progress"}, {"issue_key": "BSB-201", "change": "updated", "field": "assignee", "from": null, "to": "ada"}, {"issue_key": "BSB-203", "change": "created"}], and the response renders "Jira changes: 3", "BSB-201 status: To Do → In Progress", "BSB-201 assignee: unassigned → ada" and "BSB-203 created"

Scenario: A run with no Jira changes shows an empty state
Given the same signed-in Ada, project 7, Jira integration 6 and run 21, and a stub Jira server in which project "BSB" holds issue "BSB-201" with {"summary": "Reproduce bug", "status": "To Do", "assignee": null, "labels": []} both when the run starts and when it finishes and creates no issue
When the run reaches a terminal state and the builder captures the Jira changes, and Ada then opens GET "/projects/7/runs/21"
Then the "run_jira" row for run 21 has state_before equal to state_after and changes [], and the response renders "No Jira changes."

Scenario: A Jira change capture that fails is shown as unavailable
Given the same signed-in Ada, project 7, Jira integration 6 and run 21 with state "completed", result_status "completed" and final_verdict "pass", and a stub Jira server that returns HTTP 503 "Service Unavailable" for the project issue read
When the run reaches a terminal state and the builder attempts to capture the Jira changes, and Ada then opens GET "/projects/7/runs/21"
Then the "runs" row id 21 still has state "completed", result_status "completed" and final_verdict "pass", the "run_jira" row for run 21 has changes NULL and capture_error "The Jira changes could not be recorded.", and the response renders "Jira changes unavailable: The Jira changes could not be recorded." with no exception text or stack trace

Scenario: A project with no Jira integration shows the section as not recorded
Given the same signed-in Ada and project 7 with no "integrations" row with kind "jira", and a "runs" row id 22 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed" and final_verdict "pass"
When the run reaches a terminal state and the builder skips the Jira change capture because no Jira integration is configured, and Ada then opens GET "/projects/7/runs/22"
Then the "run_jira" table has no row for run 22, the run's state remains "completed" and final_verdict "pass", and the response renders "Jira changes: not recorded (no Jira integration)." with no exception text

### Covered requirements (traceability)
- FR-140
- FR-101

### Out of scope
Configuring or verifying the Jira integration and its MCP definition (BSB-23); starting the run
(BSB-24); executing the skill and its Jira calls (BSB-26); Jira fixture seeding, alias
substitution, cleanup and the nightly sweep (BSB-28, Later); recording `run_jira.state_after` for
fixture assertions (FR-060, BSB-28); the report's identity, verdict, diff, turn and trace sections
(BSB-33-PENDING-1, -2, -3, -5); writing to Jira from the builder (the run's own Jira calls are the
only writes, and the builder never writes to a human-created issue).

### Notes / dependencies
Depends on BSB-22-PENDING-3 for the shared project-membership check, on BSB-23-PENDING-1 for the
Jira integration and its secret reference, and on BSB-26 for the run reaching a terminal state.
The data model already names `run_jira` with `run_id`, `aliases`, `state_after` and `cleaned_at`
(ADR SK-001 section 9); this story adds `state_before` JSONB, `changes` JSONB and `capture_error`
text, all nullable, and the data-model stage must record them.

Capture is a bounded before/after read of the issues in the integration's configured Jira project,
not a proxy of the agent's calls: the builder takes the project snapshot when the run starts,
takes it again when the run reaches a terminal state, and persists the field-level differences as
`run_jira.changes`. The run window is the attribution boundary; the project's Jira credentials are
test-purpose and the project is the test project's configured tracker (NFR-006). A created issue
is one `"change": "created"` entry; a deleted issue would be one `"change": "deleted"` entry; an
updated issue yields one entry per changed field with `from` and `to`. The capture never writes to
Jira and never changes the run's outcome or verdict.

`run_jira.state_after` remains the post-run snapshot ADR SK-001 names; `state_before` is added so
the change list is auditable. This story does not implement FR-060's fixture assertions or any
BSB-28 cleanup; it records the tracker side effects for the report and keeps them with the run.
The failure and no-integration states are explicit so a missing Jira read never fails the run or
hides the report's other evidence.

---

## STORY: BSB-33-PENDING-5

**Title:** See the recorded turn count and the trace link
**Epic:** BSB-33 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-13, MVP

### Story
As a **skill author who is a project member**, I want **the run report to show the run's recorded turn count and, when tracing is enabled and a trace identifier exists, a link to its trace**, so that **I can understand how much work the run did and jump to the full trace without searching the trace store**.

### Acceptance Criteria

Scenario: The recorded turn count and trace link are shown
Given a signed-in skill author Ada who has a "project_members" row for Project Atlas (id 7), a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", state "completed", result_status "completed", turn_count 7 and trace_id "trace-4f2c9a1b7d3e", and installation tracing configuration with tracing enabled and trace URL template "https://langfuse.test/traces/{trace_id}"
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Recorded turns: 7" and an anchor with text "Open trace" and href "https://langfuse.test/traces/trace-4f2c9a1b7d3e", and the body contains no exception text or stack trace

Scenario: Tracing disabled shows no trace link
Given the same signed-in Ada and project 7, a "runs" row id 21 with project_id 7, state "completed", turn_count 7 and trace_id NULL, and installation tracing configuration with tracing disabled and trace URL template "https://langfuse.test/traces/{trace_id}"
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Recorded turns: 7" and "Tracing is disabled.", the body contains no anchor to "https://langfuse.test", and the body contains no "Open trace" link

Scenario: A missing trace identifier shows trace unavailable
Given the same signed-in Ada and project 7, a "runs" row id 21 with project_id 7, state "completed", turn_count 7 and trace_id NULL, and installation tracing configuration with tracing enabled and trace URL template "https://langfuse.test/traces/{trace_id}"
When Ada opens GET "/projects/7/runs/21"
Then the response is HTTP 200 rendering "Recorded turns: 7" and "Trace unavailable.", the body contains no anchor to "https://langfuse.test", and the body contains no exception text or stack trace

Scenario: A run that recorded no turns shows not recorded
Given the same signed-in Ada and project 7, a "runs" row id 22 with project_id 7, skill "sdlc-fix-bug-reproduce", state "failed", result_status "failed_infra", turn_count NULL and trace_id NULL, and installation tracing configuration with tracing enabled and trace URL template "https://langfuse.test/traces/{trace_id}"
When Ada opens GET "/projects/7/runs/22"
Then the response is HTTP 200 rendering "Recorded turns: not recorded" and "Trace unavailable.", and the body does not render "Recorded turns: 0"

### Covered requirements (traceability)
- FR-102
- FR-103

### Out of scope
Recording token usage, cost and turn count from execution telemetry (BSB-34; NFR-015, NFR-016 and
NFR-017); marking the trace as a test-environment trace (BSB-34; NFR-011); choosing or storing the
trace identifier (the trace store and BSB-34); the run's live progress turn counter while it
executes (BSB-26-PENDING-2); retention and purge of transcripts, logs and results (BSB-34);
rendering the trace itself; the report's identity, verdict, diff and Jira sections
(BSB-33-PENDING-1 to -4).

### Notes / dependencies
Depends on BSB-22-PENDING-3 for the shared project-membership check, on BSB-26 for the run reaching
a terminal state, and on BSB-34 for `runs.turn_count` (NFR-017), `runs.trace_id` and the
installation's tracing configuration (NFR-011; the trace store is external). BSB-34 owns recording
those values; this story owns only their presentation on the report. The requirements that create
the prerequisite records already exist in BSB-34's epic, even though that epic's stories are
written later in the fan-out.

The recorded turn count is the run's durable execution figure, not the live progress counter
BSB-26-PENDING-2 renders while the run executes ("Turns: 3 of 12"). The report labels it
"Recorded turns" so the two cannot be confused. A NULL turn count renders "not recorded" rather
than "0". The trace link is rendered only when tracing is enabled and `runs.trace_id` is non-null: the
report substitutes the identifier into the configured trace URL template, so it does not invent a
trace-store path scheme. The tracing flag, the template and `runs.trace_id` are BSB-34's
configuration and records. When tracing is disabled the report says so, and when tracing is
enabled without an identifier it says the trace is unavailable. Neither case is an error on the
report.
