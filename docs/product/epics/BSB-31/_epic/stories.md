# Stories — BSB-31 (Static security scanning)

Epic BSB-31 covers FR-076, FR-077, FR-078, FR-079, FR-080, FR-081, FR-087, FR-088, FR-089, FR-091,
FR-092, FR-154, FR-155 and NFR-005. Decomposed into 7 stories below; coverage of all 14
requirements verified.

The slices follow the path of one static scan result: scan the exact bundle before a run with no
network (PENDING-1), reuse the completed result when nothing changed (PENDING-2), decide pass or
fail from the report (PENDING-3), stop and record a scan that exceeds ten minutes (PENDING-4), show
the report the verdict is based on (PENDING-5), let an author start a static-only scan without a
run (PENDING-6), and prove the verdict equals the platform's for the same content and scanner
version (PENDING-7). Each slice is a user-visible outcome, not a layer of a scanning service.

> New stories use draft keys `BSB-31-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-31, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-31-PENDING-1

**Title:** Scan the exact run bundle in a network-less container before the run starts
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **every run to be preceded by a static security scan of the exact bundle it will execute, in a container with no network access**, so that **a run can only start on content that has been scanned and the scanner cannot reach anything outside that bundle**.

### Acceptance Criteria

Scenario: Unscanned content is scanned before the run-start preflight returns a verdict
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row for test project 3 with role "member", build 7 for skill "bug-fix-resolver" at head SHA "4f2c9a1", a "skill_bundles" row for "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" and s3_key "bundles/4f2c9a1.tar.gz", no row in "scans" for that bundle_sha256, the pinned kit recording scanner package "bheembhai-skillscan 0.4.2" and image digest "sha256:9c1f0a9d8b7e6f5a", and a stub scanner that writes the report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []} after 3 seconds
When the run-start preflight for test project 3 calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 201 with {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": false}, exactly one "scans" row exists with id 11, build_id 7, skill "bug-fix-resolver", stage "static", skills_commit_sha "4f2c9a1", bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", scanner_version "bheembhai-skillscan 0.4.2", image_digest "sha256:9c1f0a9d8b7e6f5a", state "completed", verdict "pass", score 96, recommendation "INSTALL" and coverage_complete true, and the stub scanner records that it received the bundle at s3_key "bundles/4f2c9a1.tar.gz" mounted read-only.

Scenario: The scan reads the requested commit's bundle, not a newer branch head
Given the run-start preflight runs as a signed-in member of test project 3, build 7 whose branch has advanced to head SHA "8a7d3e0", a "skill_bundles" row for "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", no "skill_bundles" row for "8a7d3e0", and a stub scanner that reports which s3_key it was given
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the stub scanner records s3_key "bundles/4f2c9a1.tar.gz", the "scans" row records skills_commit_sha "4f2c9a1" and bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", and the scan does not read or record commit "8a7d3e0".

Scenario: The static scanner container has no network access
Given the static scan of bundle "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" is started with the scanner container's Docker network mode set to "none", a stub scanner that writes the clean report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []}, and a dummy HTTP server listening at "http://10.0.0.5:8080" that records every request it receives
When the scanner attempts an HTTPS request to "https://example.com" and an HTTP request to "http://10.0.0.5:8080"
Then both requests fail before a response is received, the dummy server records 0 requests, the scan completes with state "completed" from the read-only mounted bundle, and the "scans" row records verdict "pass" for the clean report.

Scenario: A scanner that writes no report is recorded as failed, not passing
Given the run-start preflight runs as a signed-in member of test project 3, and the pinned scanner container exits with code 137 before writing a report
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"} for bundle "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
Then the response is HTTP 201 with {"scan_id": 11, "state": "failed", "verdict": "fail", "reused": false}, the "scans" row has state "failed", verdict "fail", score NULL, recommendation NULL and failure_reason "Scanner exited with code 137 before writing a report.", and no "scan_findings" row is written.

Scenario: A scan is refused when the commit has no packed bundle
Given the run-start preflight runs as a signed-in member of test project 3, and build 7 at head SHA "4f2c9a1" has no "skill_bundles" row for "4f2c9a1"
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 409 with {"error": "No packed bundle exists for commit 4f2c9a1."}, and no "scans" row and no "scan_findings" row are created.

### Covered requirements (traceability)
- FR-076
- NFR-005

### Out of scope
Refusing the run when the verdict is not pass (FR-055, BSB-27); refusing packaging when the verdict
is not pass (no FR maps packaging refusal to BSB-31 — the packaging gate belongs to BSB-25/BSB-30
and the epic's Definition of Done wording must be corrected there; recorded as a cross-epic gap in
the Notes); aggregating the Ready checks (BSB-30); packing the bundle itself (BSB-25);
the LLM scan stage (BSB-32); changing the scanner's rules, severities or recommendation values;
reusing an earlier result (BSB-31-PENDING-2); the verdict rules themselves (BSB-31-PENDING-3 owns
the verdict function this story calls and whose output it records; this story asserts that output
but defines no rule); rendering the report page (BSB-31-PENDING-5).

### Notes / dependencies
Depends on BSB-18 for the signed-in skill-builder author and the per-request group gate, on BSB-19
and BSB-21 for the build and its head SHA, on BSB-25 for the packed `skill_bundles` row at that
SHA, and on the externally pinned scanner image and package recorded in the platform kit. The
scanner's own policy is external; this story does not define or change a rule.

This story owns the static scan service, the `scans` and `scan_findings` records, and the
synchronous `POST /api/builds/7/scans/static` route that every other caller uses. A scan request
returns only after the scan reaches `completed` or `failed`, so a caller always receives a verdict.
The route accepts `project_id` and `skills_commit_sha`; it reads the `skill_bundles` row for that
SHA and scans that bundle, never the branch head and never an unpacked working tree.

The service exposes one direct entry point that takes a packed bundle fixture (its bytes or
`skill_bundles` row) plus the pinned scanner version and image digest, with no build or project,
and returns the same scan result the route returns; the route is a thin caller of it. A scan
created through that entry point has `build_id` NULL (BSB-31-PENDING-7 uses it for the parity
test). `build_id` on a route-created scan records the build that first requested the scan for
provenance only; it does not scope reuse (BSB-31-PENDING-2) or the report route
(BSB-31-PENDING-5).

The scan record's identity/reuse key is `skill` + `stage` + `bundle_sha256` + `scanner_version`
(BSB-31-PENDING-2 owns reuse). `skills_commit_sha` is recorded on the row for provenance and to say
which content a run scanned, but it does not by itself force a new scan: the same bundle bytes
committed at a new SHA reuse the completed row. The row carries no `project_id`, so identical
content can be reused across projects.

ADR SK-001 section 9 names no scan table, so this epic introduces `scans` (id, build_id nullable,
skill, stage, skills_commit_sha, bundle_sha256, scanner_version, image_digest, state, verdict,
verdict_reasons, score, recommendation, coverage_complete, report, failure_reason, started_at,
finished_at) and `scan_findings` (id, scan_id, severity, rule, file, line, accepted,
acceptance_reason); the data-model stage must record them. `report` is the scanner's report
document (score, recommendation, coverage counts and findings), so the report page can show the
coverage counts and every located finding.

This story depends on BSB-31-PENDING-3 for the one verdict function. The function takes the
scanner report plus the scanned bundle's `.skillspector-baseline.yaml` and returns `verdict`,
`verdict_reasons` and the `scan_findings` rows, which this story persists alongside the report's
own score, recommendation and coverage fields on the `scans` row. It does not set `state` for a
scan with no usable report; that failed state is this story's and BSB-31-PENDING-4's. This story
does not recompute the verdict, so its acceptance criteria assert the value the function returns.
Dependency direction is stated in
BSB-31-PENDING-3's Notes: at runtime this story calls that function; the function depends on this
story only for the record contract.

The route applies the shared project-membership check that BSB-22-PENDING-1 defines and
BSB-22-PENDING-3 applies on the run-start path, for the signed-in author on every request.

Run-start invocation (FR-076's "before every run"): the run-start flow is BSB-24's, and it invokes
this route for the run's project and the exact `skills_commit_sha` after BSB-25 has packed the
bundle at that SHA and before the agent container launches. The packed bundle is a precondition:
there is no scan before packaging, and a missing `skill_bundles` row is the HTTP 409 above. The
verdict returned by that call is the value BSB-27's FR-055 refusal consumes and BSB-30's FR-069
readiness reads; neither BSB-27 nor BSB-30 recomputes it. BSB-24's, BSB-25's and BSB-27's own
stories must name this call and its position when those epics are decomposed; until then this story
supplies the contract they call. BSB-32's full security scan calls this static stage first, and the
standalone author-triggered use is exercised in BSB-31-PENDING-6. A container that cannot start or
produces no report is a failed scan, never a missing or passing one.

Time budget: the static scan's own fixed ceiling is 600 seconds (BSB-31-PENDING-4) and the
run-start preflight waits synchronously for the verdict, so a cache-miss run start can wait up to
ten minutes; a reuse hit (BSB-31-PENDING-2) adds no scan time. The scan is a separate synchronous
gate, not part of BSB-25's 60-second / 5 MB non-model bundle-preparation budget (NFR-001);
NFR-001's "run preparation" wording and BSB-25 must be reconciled to say so (cross-epic follow-up).

Packaging gate: BSB-31 supplies only the verdict. No FR mapped to BSB-31 assigns a packaging
refusal, and BSB-25's and BSB-30's epics name no static-scan packaging gate; FR-055 (BSB-27)
refuses the run on a non-pass verdict and FR-069 (BSB-30) reads it for Ready, while packaging
refusal belongs to the verifier checks FR-071 to FR-073 under BSB-30. The epic's Definition of Done
sentence that says a non-passing verdict also blocks packaging therefore needs its owner and
requirement fixed in BSB-25/BSB-30 (or the sentence removed); no story here claims it. This is
recorded as a cross-epic gap for the next review, not implemented here.

---

## STORY: BSB-31-PENDING-2

**Title:** Reuse a completed static scan result when the content and scanner version are unchanged
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **a completed static scan result reused when the exact content and scanner version are unchanged**, so that **repeated runs do not repeat the same scan while still receiving the same verdict**.

### Acceptance Criteria

Scenario: An unchanged bundle and scanner version reuse the completed result
Given the run-start preflight runs as a signed-in member of test project 3, a completed "scans" row id 11 for bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" with scanner_version "bheembhai-skillscan 0.4.2", state "completed", verdict "pass" and score 96, build 7 still packs that bundle at head SHA "4f2c9a1", and a stub scanner whose container-start counter is 0
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 200 with {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": true}, the "scans" table still contains exactly 1 row, and the stub scanner's container-start counter remains 0.

Scenario: Changed bundle content starts a new scan
Given the run-start preflight runs as a signed-in member of test project 3, a completed "scans" row id 11 for bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", and a new commit "8a7d3e0" packed as bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "8a7d3e0"}
Then the response is HTTP 201 with {"scan_id": 12, "state": "completed", "verdict": "pass", "reused": false}, a new "scans" row id 12 records skills_commit_sha "8a7d3e0" and bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", scan 11 is unchanged, and the stub scanner's container-start counter is 1.

Scenario: A different scanner version starts a new scan
Given the run-start preflight runs as a signed-in member of test project 3, a completed "scans" row id 11 for bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" with scanner_version "bheembhai-skillscan 0.4.2", and the pinned kit now records scanner package "bheembhai-skillscan 0.5.0" and image digest "sha256:7d2e4b8c0f1a3e5d"
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 201 with {"scan_id": 12, "state": "completed", "verdict": "pass", "reused": false}, the new "scans" row records scanner_version "bheembhai-skillscan 0.5.0" and image_digest "sha256:7d2e4b8c0f1a3e5d", scan 11 is unchanged, and the stub scanner's container-start counter is 1.

Scenario: A failed scan is not reused and a new scan runs
Given the run-start preflight runs as a signed-in member of test project 3, a "scans" row id 11 for bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" with state "failed" and failure_reason "Scanner exited with code 137 before writing a report.", and no completed scan for that bundle
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 201 with {"scan_id": 12, "state": "completed", "verdict": "pass", "reused": false}, a new "scans" row id 12 exists, scan 11 remains visible with state "failed", and the stub scanner's container-start counter is 1.

Scenario: A completed failing result is reused and stays failing
Given the run-start preflight runs as a signed-in member of test project 3, a completed "scans" row id 11 for bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" with state "completed", verdict "fail", recommendation "DO_NOT_INSTALL" and verdict_reasons ["recommendation DO_NOT_INSTALL"], and a stub scanner whose container-start counter is 0
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 200 with {"scan_id": 11, "state": "completed", "verdict": "fail", "reused": true}, no new "scans" row exists, and the stub scanner's container-start counter remains 0.

Scenario: The same bundle content at a new commit reuses the completed result
Given the run-start preflight runs as a signed-in member of test project 3, a completed "scans" row id 11 for bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" with scanner_version "bheembhai-skillscan 0.4.2", state "completed" and verdict "pass", a new commit "8a7d3e0" packed as the same bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", and a stub scanner whose container-start counter is 0
When the run-start preflight calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "8a7d3e0"}
Then the response is HTTP 200 with {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": true}, the "scans" table still contains exactly 1 row, that row keeps skills_commit_sha "4f2c9a1", and the stub scanner's container-start counter remains 0.

Scenario: A request from a different build and project reuses the completed result
Given a completed "scans" row id 11 for bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" with scanner_version "bheembhai-skillscan 0.4.2", state "completed" and verdict "pass", build 9 in test project 5 at head SHA "c0ffee1" packed as the same bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", a signed-in member of test project 5, and a stub scanner whose container-start counter is 0
When the run-start preflight for test project 5 calls POST "/api/builds/9/scans/static" with {"project_id": 5, "skills_commit_sha": "c0ffee1"}
Then the response is HTTP 200 with {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": true}, no new "scans" row exists, and the stub scanner's container-start counter remains 0.

### Covered requirements (traceability)
- FR-077

### Out of scope
Starting a scan (BSB-31-PENDING-1); deciding pass or fail from the report (BSB-31-PENDING-3);
timing out a scan (BSB-31-PENDING-4); the report page (BSB-31-PENDING-5); invalidating a result for
reasons other than content or scanner version (for example a manual purge or retention expiry);
scanning changed content in place; any cross-project access decision about who may read a reused
result (that is the report view's rule in BSB-31-PENDING-5).

### Notes / dependencies
Depends on BSB-31-PENDING-1 for the scan service, the `scans` row and the synchronous route, and
on BSB-31-PENDING-3 for the verdict of a newly created scan; a reused row returns the `verdict`
already stored by BSB-31-PENDING-3 and computes nothing. This story owns the reuse key: a scan is
reused only when `stage` is "static", `bundle_sha256`, `skill` and `scanner_version` all match the
requested bundle and the existing row's state is "completed". The key is content-only:
`skills_commit_sha` is recorded on the row for provenance and `build_id` is provenance, but neither
scopes reuse, so the same bytes committed at a new SHA and the same bytes requested by another
build or project reuse the existing row. A completed scan is reused whether its verdict is pass or
fail, so unchanged content is never re-scanned until it or the scanner changes. A row with state
"failed" (including a timeout from BSB-31-PENDING-4) is never reused.

Because a scan row carries no `project_id`, a completed result is reusable by any project whose run
uses the same content and scanner version; the standalone request's project-membership check runs
before reuse lookup (BSB-31-PENDING-6). BSB-24 and BSB-25 consume the route; they do not
implement their own cache. A scanner-version change is a new reuse key even when content is
identical, because the result may differ and BSB-31-PENDING-7's parity claim is version-specific.

This story is invoked through the same `POST /api/builds/{id}/scans/static` path as
BSB-31-PENDING-1: BSB-24's run-start flow calls it after BSB-25 has packed the bundle at the
requested SHA and before the agent container launches, and BSB-31-PENDING-6's standalone control
calls the same route. This story adds no second entry point.

---

## STORY: BSB-31-PENDING-3

**Title:** Pass a static scan only when it is non-blocking, critical-free and complete
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the static verdict to fail on a DO_NOT_INSTALL recommendation, any critical finding or incomplete coverage, and never let an accepted finding clear a block**, so that **a known security problem cannot be reported as a pass**.

### Acceptance Criteria

Scenario: A clean, complete report passes
Given a scanner report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []} for bundle "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
When the static scan completes
Then the "scans" row has state "completed", verdict "pass", score 96, recommendation "INSTALL", coverage_complete true and verdict_reasons [], and no "scan_findings" row is written.

Scenario: A DO_NOT_INSTALL recommendation fails even with no critical finding
Given a scanner report {"score": 0, "recommendation": "DO_NOT_INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "HIGH", "rule": "SS-210", "file": "SKILL.md", "line": 8}]}
When the static scan completes
Then the "scans" row has state "completed" and verdict "fail", verdict_reasons is ["recommendation DO_NOT_INSTALL"], and one "scan_findings" row exists with severity "HIGH", rule "SS-210", file "SKILL.md", line 8 and accepted false.

Scenario: Any critical finding fails even with a non-blocking recommendation
Given a scanner report {"score": 41, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "CRITICAL", "rule": "SS-001", "file": "SKILL.md", "line": 3}, {"severity": "LOW", "rule": "SS-300", "file": "scripts/run.sh", "line": 7}]}
When the static scan completes
Then the "scans" row has state "completed" and verdict "fail", verdict_reasons is ["1 critical finding"], and two "scan_findings" rows exist, one "CRITICAL"/"SS-001"/"SKILL.md"/3 with accepted false and one "LOW"/"SS-300"/"scripts/run.sh"/7 with accepted false.

Scenario: Incomplete coverage fails even with no blocking recommendation and no critical finding
Given a scanner report {"score": 88, "recommendation": "INSTALL", "coverage": {"complete": false, "files_scanned": 9, "files_total": 12}, "findings": []}
When the static scan completes
Then the "scans" row has state "completed", verdict "fail", coverage_complete false, and verdict_reasons is ["coverage incomplete: 9 of 12 files scanned"], and no "scan_findings" row is written.

Scenario: An accepted critical finding cannot clear the block
Given a scanner report {"score": 41, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "CRITICAL", "rule": "SS-001", "file": "SKILL.md", "line": 3}]} for a bundle whose ".skillspector-baseline.yaml" contains the entry {"rule": "SS-001", "file": "SKILL.md", "line": 3, "reason": "Temporary exception approved 2026-11-10"}
When the static scan completes
Then the "scans" row has state "completed" and verdict "fail", verdict_reasons is ["1 critical finding"], and the "scan_findings" row for "SS-001" has accepted true and acceptance_reason "Temporary exception approved 2026-11-10".

Scenario: An accepted non-critical finding does not itself fail a clean scan
Given a scanner report {"score": 90, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "HIGH", "rule": "SS-150", "file": "scripts/run.sh", "line": 21}]} for a bundle whose ".skillspector-baseline.yaml" contains the entry {"rule": "SS-150", "file": "scripts/run.sh", "line": 21, "reason": "Reviewed and accepted 2026-11-10"}
When the static scan completes
Then the "scans" row has state "completed" and verdict "pass", verdict_reasons is [], and the "scan_findings" row for "SS-150" remains present with accepted true and acceptance_reason "Reviewed and accepted 2026-11-10".

### Covered requirements (traceability)
- FR-078
- FR-079
- FR-080
- FR-081

### Out of scope
Running the scan or isolating its network (BSB-31-PENDING-1); reusing a prior result
(BSB-31-PENDING-2); the ten-minute timeout and failed-record state (BSB-31-PENDING-4); the report
page layout (BSB-31-PENDING-5); authoring, reviewing or approving baseline entries (the
`.skillspector-baseline.yaml` file and its CODEOWNERS review are external to this epic); defining
the scanner's rule set, severities or recommendation vocabulary; overriding a verdict by any other
means.

### Notes / dependencies
Depends on BSB-31-PENDING-1 for the `scans` and `scan_findings` record contract and on
BSB-31-PENDING-2 only to know when a completed result is reused instead of computed.

This story owns the one verdict function every caller uses; no caller recomputes the verdict from a
report. The function's input is the scanner report document plus the scanned bundle's
`.skillspector-baseline.yaml` (when present); its output is `verdict`, `verdict_reasons` and the
`scan_findings` rows (severity, rule, file, line, accepted, acceptance_reason), which the caller
persists alongside the report's own score, recommendation and coverage fields on the `scans` row.
It does not set `state` for a scan with no usable report — that failed state belongs to
BSB-31-PENDING-1 and BSB-31-PENDING-4.

The function's callers are BSB-31-PENDING-1 (the scan service and HTTP route persist its output),
BSB-31-PENDING-2 (a newly created scan; a reused row returns the stored verdict), BSB-31-PENDING-5
(renders `verdict` and `verdict_reasons`), BSB-31-PENDING-6 (the standalone trigger) and
BSB-31-PENDING-7 (the parity test). Dependency direction: at runtime BSB-31-PENDING-1 depends on
this story for the function, and this story depends on BSB-31-PENDING-1 only for the record
contract and never calls the route or the scan service; BSB-31-PENDING-2's new-scan path likewise
calls the function. The contract is fixed here so the two stories can be built together; neither
story may ship a second verdict implementation.

A verdict is "pass" only when the recommendation is not "DO_NOT_INSTALL",
no finding has severity "CRITICAL", and `coverage.complete` is true; those three conditions each
add their exact reason to `verdict_reasons`, in the fixed order recommendation, critical finding,
coverage, when more than one fails. The verdict is computed from the findings as the scanner
reports them, before any acceptance is applied; an accepted finding is then recorded on
`scan_findings` when `.skillspector-baseline.yaml` in the scanned bundle matches its rule, file and
line. Acceptance only annotates the row: it never removes a reason from `verdict_reasons` and never
changes a "fail" to a "pass".
A scan that produces no usable report is "failed" rather than "completed" with a verdict (see
BSB-31-PENDING-1 and BSB-31-PENDING-4), so this story applies only to a completed report.

BSB-30's readiness check reads `verdict` (FR-069) and BSB-27 refuses a run on a non-pass verdict
(FR-055); neither re-implements these rules. BSB-31 supplies only the verdict: no FR mapped to
BSB-31 assigns a packaging refusal, and BSB-25's and BSB-30's epics name no static-scan packaging
gate. The epic's Definition of Done sentence that says a non-passing verdict also blocks packaging
therefore needs its owner and requirement fixed in BSB-25/BSB-30 (or the sentence removed); it is
recorded as a cross-epic gap in BSB-31-PENDING-1's Notes and not claimed here. The scanner's policy
and baseline format are external prerequisites; changing either belongs to the platform's scanner,
not this epic.

---

## STORY: BSB-31-PENDING-4

**Title:** Stop a static scan after ten minutes and record it as failed
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **a static scan stopped after ten minutes and recorded as failed**, so that **a stuck scanner cannot hold up a run or be mistaken for a pass**.

### Acceptance Criteria

Scenario: A scan still running at ten minutes is terminated and recorded as failed
Given the scan request runs as a signed-in member of test project 3, a stub scanner that starts at "2026-11-16T10:00:00Z", writes no report and keeps running, a fake clock, no override of the ten-minute limit, and the scan was started by POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
When the clock reaches "2026-11-16T10:10:01Z" with the scan still running
Then the scanner container is killed, the "scans" row has state "failed", verdict "fail", score NULL, recommendation NULL, failure_reason "Scan exceeded the ten-minute limit." and finished_at "2026-11-16T10:10:00Z", no "scan_findings" row is written, and the synchronous POST "/api/builds/7/scans/static" response is HTTP 201 with {"scan_id": 11, "state": "failed", "verdict": "fail", "reused": false}.

Scenario: A scan that finishes under ten minutes completes normally
Given the scan request runs as a signed-in member of test project 3, a stub scanner that writes the report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []} after 599 seconds, a fake clock, and the scan started at "2026-11-16T10:00:00Z" by POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
When the clock reaches "2026-11-16T10:09:59Z"
Then the scanner container is not killed, the "scans" row has state "completed", verdict "pass", failure_reason NULL and finished_at "2026-11-16T10:09:59Z", and the response is HTTP 201 with {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": false}.

Scenario: The ten-minute boundary terminates a scan that has not finished
Given the scan request runs as a signed-in member of test project 3, a stub scanner that writes no report and is still running at 600 seconds after the scan started at "2026-11-16T10:00:00Z" by POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
When the clock reaches exactly "2026-11-16T10:10:00Z"
Then the scanner container is killed, the "scans" row has state "failed", verdict "fail" and failure_reason "Scan exceeded the ten-minute limit.", and the response is HTTP 201 with {"scan_id": 11, "state": "failed", "verdict": "fail", "reused": false}.

### Covered requirements (traceability)
- FR-087
- FR-088

### Out of scope
Deciding pass or fail from a completed report (BSB-31-PENDING-3); reuse of a timed-out result
(BSB-31-PENDING-2 already excludes a failed row); the report page's rendering of a timeout
(BSB-31-PENDING-5); configuring or overriding the limit per project or per run; retrying a timed-out
scan automatically; the LLM scan's own per-container limit (BSB-32); scanner image pull policy or
registry availability.

### Notes / dependencies
Depends on BSB-31-PENDING-1 for the scan service and the synchronous route, and on BSB-31-PENDING-3
for the verdict function. This story owns the ten-minute (600-second) execution limit and its
enforcement around the scanner container. The limit is fixed for the static stage: no project, run
or request field can change it. A scan that has not reached state "completed" by 600 seconds is
killed and recorded with state "failed" and verdict "fail", so a timeout can never be reused as a
result and can never pass a run or readiness check. The reason string is exactly "Scan exceeded the
ten-minute limit." so the report and downstream consumers read one value; BSB-31-PENDING-5 renders
it as "Scan failed: Scan exceeded the ten-minute limit.".

This story is a caller of the same `POST /api/builds/{id}/scans/static` path as
BSB-31-PENDING-1: BSB-24's run-start flow calls it after BSB-25 has packed the bundle at the
requested SHA and before the agent container launches, and the ten-minute wait is why that call is
synchronous. The 600-second ceiling is the static scan's own budget: the scan is a separate
synchronous gate, not part of BSB-25's 60-second / 5 MB non-model bundle-preparation budget
(NFR-001); the PRD's "run preparation" wording and BSB-25 must be reconciled to say so (cross-epic
follow-up). A cache-miss run start can therefore wait up to ten minutes, while a reuse hit
(BSB-31-PENDING-2) adds no scan time.

BSB-32's LLM stage has its own ten-minute per-container limit and is out of scope here. The
run-start preflight's own deadline is BSB-27's concern; this story only guarantees that the static
scan call returns a failed verdict at the limit rather than hanging past it.

---

## STORY: BSB-31-PENDING-5

**Title:** Show the static scan score, recommendation and located findings in the report
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the static scan report to show the score, the recommendation and every finding's severity, rule, file and line**, so that **I can see exactly what the verdict is based on and fix the content that blocked it**.

### Acceptance Criteria

Scenario: A completed passing scan shows its score, recommendation and coverage
Given a completed "scans" row id 11 for build 7 with state "completed", verdict "pass", score 96, recommendation "INSTALL", coverage_complete true, report {"coverage": {"files_scanned": 12, "files_total": 12}} and no "scan_findings" rows, and a signed-in skill author
When the author opens GET "/scans/11"
Then the response is HTTP 200 and the page contains the text "Verdict: PASS", "Static scan score: 96", "Recommendation: INSTALL", "Coverage: 12 of 12 files scanned" and "No findings."

Scenario: Every finding is shown with severity, rule, file and line
Given a completed "scans" row id 12 for build 7 with verdict "fail" and two "scan_findings" rows, one with severity "CRITICAL", rule "SS-001", file "SKILL.md" and line 3, and one with severity "HIGH", rule "SS-101", file "scripts/run.sh" and line 14
When the author opens GET "/scans/12"
Then the response is HTTP 200 and the findings table lists findings in descending severity and contains the rows "CRITICAL SS-001 SKILL.md:3" followed by "HIGH SS-101 scripts/run.sh:14".

Scenario: A non-passing scan shows the reasons for its verdict
Given a completed "scans" row id 13 for build 7 with verdict "fail" and verdict_reasons ["recommendation DO_NOT_INSTALL", "coverage incomplete: 9 of 12 files scanned"]
When the author opens GET "/scans/13"
Then the response is HTTP 200 and the page contains "Verdict: FAIL", "recommendation DO_NOT_INSTALL" and "coverage incomplete: 9 of 12 files scanned".

Scenario: A scan still in progress shows no score or recommendation
Given a "scans" row id 14 for build 7 with state "running" and score NULL, recommendation NULL and verdict NULL
When the author opens GET "/scans/14"
Then the response is HTTP 200 and the page contains "Scan in progress" and does not contain "Static scan score:" or "Recommendation:".

Scenario: An unknown scan id is not found
Given no "scans" row with id 99
When the author opens GET "/scans/99"
Then the response is HTTP 404 with {"error": "Scan 99 not found."} and no score, recommendation or finding is rendered.

Scenario: A failed scan shows its failure reason instead of an in-progress state
Given a "scans" row id 15 for build 7 with state "failed", verdict "fail", score NULL, recommendation NULL, coverage_complete NULL and failure_reason "Scan exceeded the ten-minute limit."
When the author opens GET "/scans/15"
Then the response is HTTP 200 and the page contains "Verdict: FAIL" and "Scan failed: Scan exceeded the ten-minute limit.", and does not contain "Scan in progress", "Static scan score:" or "Recommendation:".

Scenario: A scan reused by a different build and project renders from the same URL
Given a completed "scans" row id 11 requested by build 7 in test project 3 and reused by build 9 in test project 5 (both runs packed bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"), with state "completed", verdict "pass", score 96, recommendation "INSTALL", coverage_complete true and no "scan_findings" rows, and a signed-in skill author
When the author opens GET "/scans/11"
Then the response is HTTP 200 and the page contains "Verdict: PASS", "Static scan score: 96", "Recommendation: INSTALL" and "Coverage: 12 of 12 files scanned".

### Covered requirements (traceability)
- FR-089
- FR-154
- FR-155

### Out of scope
Starting or running a scan (BSB-31-PENDING-1 and BSB-31-PENDING-6); computing the verdict
(BSB-31-PENDING-3); timeout behaviour (BSB-31-PENDING-4); the LLM scan report, which model ran it
and the combined security tab (BSB-32); the catalog reviewer's stable report view and its access
rule (unowned today — a cross-epic gap for BSB-36/BSB-33; this story supplies no second route);
exporting the report as SARIF or another file format; filtering or sorting findings; editing a
finding or its acceptance from the page.

### Notes / dependencies
Depends on BSB-31-PENDING-1 for the `scans` and `scan_findings` records and on BSB-31-PENDING-3 for
the `verdict` and `verdict_reasons` it renders; BSB-31-PENDING-4 supplies the failed/timeout state
this page must render. This story owns the authoring report route `GET /scans/11` and its field
mapping: `score` and `recommendation` are shown exactly as the scanner wrote them; each finding's
`severity`, `rule`, `file` and `line` are shown in one row; a scan with no findings shows "No
findings."; a scan that has not completed shows "Scan in progress" and no score; a scan with state
"failed" shows "Verdict: FAIL" and "Scan failed: <failure_reason>", never "Scan in progress" and
never a score or recommendation; an unknown scan id is 404. The fixed failure text template is
"Scan failed: " followed by the row's `failure_reason`, so a timeout renders "Scan failed: Scan
exceeded the ten-minute limit." (BSB-31-PENDING-4) and a scanner that wrote no report renders
"Scan failed: Scanner exited with code 137 before writing a report." (BSB-31-PENDING-1).

Access rule: the report route is part of the authoring interface and is gated by BSB-18's signed-in
skill-builder check only (a signed-in author outside the `skill-builders` group receives HTTP 403).
The route is content-addressed and is not scoped to the build or project that first requested the
scan, so a completed result reused by another build (BSB-31-PENDING-2) renders from the same URL.
It does not apply the project-membership check. A catalog reviewer named in PRD section 2 does not
use the authoring interface, so this gated URL cannot itself be the report link FR-111 asks the
catalog pull request to carry. No epic currently owns a stable reviewer-facing scan-report view or
its access rule: BSB-33's stable view is the run report and BSB-36 only links the scan reports.
That view and its access rule must be added by BSB-36 (or BSB-33 if it extends its stable view),
and its access rule must not be the authoring-interface gate, since PRD section 2 says the reviewer
does not use that interface — or the PRD's reviewer assumption corrected. This is a cross-epic gap
recorded for the next review; this story adds no second route. The report contains no credential, so no redaction is required beyond the
BSB-23 secret rule for integration values. The HTML route and the report model are shared with the
run page's Security tab (BSB-26/BSB-33 link the run's scan); this story owns the scan-only page,
not the run page layout.

---

## STORY: BSB-31-PENDING-6

**Title:** Start a static-only scan from the skill page for a test project the author belongs to
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **to start a static-only scan from the skill page for a test project I belong to without creating a run**, so that **I can check a skill before spending a run on it**.

### Acceptance Criteria

Scenario: A project member starts a static-only scan and no run is created
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row for test project 3 with role "owner", build 7 at head SHA "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", no "scans" row for that bundle, an empty "runs" table, and a stub scanner that writes the clean report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []}
When she submits the "Security check (static only)" control on GET "/builds/7", which calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 201 with {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": false}, exactly one "scans" row exists with stage "static", skills_commit_sha "4f2c9a1" and bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", and the "runs" table still contains 0 rows.

Scenario: A non-owner member can start the scan
Given a signed-in skill author Bob whose local "users" id is 43 and who has a "project_members" row for test project 3 with role "member", build 7 at head SHA "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", no "scans" row for that bundle, and a stub scanner that writes the clean report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []}
When Bob calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 201 with {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": false}, and exactly one "scans" row exists.

Scenario: A signed-in author who is not a project member is refused
Given a signed-in skill author Carol whose local "users" id is 44 and who has no "project_members" row for test project 3, build 7 at head SHA "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", no "scans" row for that bundle, and a stub scanner whose container-start counter is 0
When Carol calls POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 403 with {"error": "You are not a member of this project."}, no "scans" row and no "scan_findings" row are created, and the stub scanner's container-start counter remains 0.

Scenario: An author with no project membership has no project to scan for
Given a signed-in skill author Dave who is a current member of the "skill-builders" group, whose local "users" id is 45 and who has no "project_members" rows, and build 7 at head SHA "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
When Dave opens GET "/builds/7"
Then the response is HTTP 200 and the "Security check (static only)" control is disabled with the message "No test project available.", and a direct POST "/api/builds/7/scans/static" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"} returns HTTP 403 with {"error": "You are not a member of this project."} and creates no "scans" row.

Scenario: A static-only scan needs no integration or credential
Given test project 3 has zero "integrations" rows and no secret exists under "skill-builder/3/", and a signed-in project member starts a static-only scan for bundle "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
When the scan completes
Then the response is HTTP 201 with {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": false}, exactly one "scans" row exists with stage "static", no "llm" stage scan row exists, and the scanner container environment contains no Jira, source-control or model credential.

### Covered requirements (traceability)
- FR-092

### Out of scope
The full security scan that runs static then LLM from the same page (FR-093, BSB-32); the LLM
scan's model profile (BSB-32/BSB-23); starting a run (BSB-24); the CLI scan (BSB-37); report
rendering (BSB-31-PENDING-5); adding, removing or listing project members (BSB-22); credential
resolution or mapping integrations to a run (BSB-23/BSB-24); scanning a commit with no packed
bundle (BSB-31-PENDING-1).

### Notes / dependencies
Depends on BSB-18 for the signed-in skill-builder author and its per-request group gate, on
BSB-21 for the build page `GET /builds/{id}`, its head SHA and its access rule, on BSB-22-PENDING-1
for the test project and for defining the shared project-membership check, on BSB-22-PENDING-3 for
the run-start application of that check and its exact 403 message "You are not a member of this
project.", and on BSB-25 for the packed bundle. This story owns the "Security check (static only)"
control and the author-facing request contract; the `POST /api/builds/7/scans/static` route and
scan service are BSB-31-PENDING-1's, and each response's `verdict` is produced by
BSB-31-PENDING-3's verdict function, so this story defines no verdict rule. This story adds the
control to BSB-21's build page and does not own that page: the page, its head SHA and the
`signed-in skill-builders group member` access rule are BSB-21's (with BSB-18's authoring gate),
and a signed-in group member such as Dave can open `GET /builds/7`. The control carries a project
selector listing only the test projects in which the signed-in author has
a current `project_members` row (read from BSB-22's records); the selected `project_id` is sent with
`skills_commit_sha`, and an author with no membership sees the control disabled with "No test
project available." rather than a selector. The request requires `project_id` and
`skills_commit_sha`; the membership check reads the current `project_members` rows on every request
and runs before the bundle lookup, the reuse lookup and any scanner start, so a refused caller
learns nothing about the bundle or a prior scan.

The project is the authorization scope only: a static-only scan resolves no project integration and
no credential. The full security scan (static then LLM) is BSB-32's separate entry point and model
profile; it calls this static stage first. The skill page's ordinary build access is BSB-18's
authoring gate; the route's project-membership check guards the scan trigger, not the build page.
This story owns and exercises the standalone trigger; BSB-24's run-start preflight calls the same
route as an already-authorized project member, after BSB-25 has packed the bundle at the requested
SHA and before the agent container launches. A successful standalone scan does not create a `runs`
row, a run branch or a run report.

---

## STORY: BSB-31-PENDING-7

**Title:** Match the platform's static verdict for the same content and scanner version
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **builder team member maintaining the static scan**, I want **the builder's static verdict to match the platform's for the same content and pinned scanner version**, so that **the evidence recorded in the builder is trustworthy when the catalog reviewer reads it through the catalog pull request**.

### Acceptance Criteria

Scenario: The builder's verdict matches the platform's on a fixed corpus
Given the parity fixture "tests/fixtures/scan-parity.json" records four bundles with their scanner report and platform verdict for scanner version "bheembhai-skillscan 0.4.2": {"bundle": "clean", "bundle_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "report": {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []}, "platform_verdict": "pass"}, {"bundle": "do-not-install", "bundle_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", "report": {"score": 0, "recommendation": "DO_NOT_INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "HIGH", "rule": "SS-210", "file": "SKILL.md", "line": 8}]}, "platform_verdict": "fail"}, {"bundle": "critical", "bundle_sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae", "report": {"score": 41, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "CRITICAL", "rule": "SS-001", "file": "SKILL.md", "line": 3}]}, "platform_verdict": "fail"} and {"bundle": "incomplete-coverage", "bundle_sha256": "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9", "report": {"score": 88, "recommendation": "INSTALL", "coverage": {"complete": false, "files_scanned": 9, "files_total": 12}, "findings": []}, "platform_verdict": "fail"}, the builder is pinned to scanner package "bheembhai-skillscan 0.4.2" and image digest "sha256:9c1f0a9d8b7e6f5a", and a stub scanner returns each bundle's recorded report
When the parity test runs the static scan service on each fixture bundle through the same scan and verdict path as POST "/api/builds/7/scans/static", called directly with the bundle fixture so no build or project is needed, and compares the resulting verdict with the fixture's platform_verdict
Then each of the 4 builder verdicts equals its platform_verdict, the test reports "4 of 4 bundles match", and every resulting scan record carries scanner_version "bheembhai-skillscan 0.4.2", image_digest "sha256:9c1f0a9d8b7e6f5a" and build_id NULL.

Scenario: Every scan records the exact scanner identity it used
Given the pinned kit records scanner package "bheembhai-skillscan 0.4.2" and image digest "sha256:9c1f0a9d8b7e6f5a", and the kit names no image tag for the scanner
When a static scan completes
Then the "scans" row records scanner_version "bheembhai-skillscan 0.4.2" and image_digest "sha256:9c1f0a9d8b7e6f5a", and the scanner container is started from that image digest rather than from an image tag such as "latest".

Scenario: A scanner version mismatch is reported rather than compared
Given the builder is pinned to scanner package "bheembhai-skillscan 0.4.2", and the platform baseline fixture was recorded with scanner package "bheembhai-skillscan 0.3.9"
When the parity test runs
Then it fails with the message "Scanner version mismatch: builder bheembhai-skillscan 0.4.2, baseline bheembhai-skillscan 0.3.9." and compares no verdict.

Scenario: A bundle with no platform baseline fails the parity test
Given the parity fixture has no entry for bundle_sha256 "6b3a55e0261b0304143f805a24924d0c1c44524821305f31d9277843b8a10f47"
When the parity test scans that bundle and looks up its platform_verdict
Then the test fails with the message "Bundle 6b3a55e0261b0304143f805a24924d0c1c44524821305f31d9277843b8a10f47 has no platform baseline." and no builder verdict is reported as matching.

### Covered requirements (traceability)
- FR-091

### Out of scope
Maintaining the platform's parity baseline or the fixed corpus (external to the builder); changing
the scanner's rules, severities or recommendation vocabulary; the LLM scan's parity with the
platform (BSB-32); per-run or per-project scanner overrides; the CI run of the static check in the
skills repository (external); the authoring report page (BSB-31-PENDING-5); the scan's pass/fail
rules (BSB-31-PENDING-3).

### Notes / dependencies
Depends on BSB-31-PENDING-1 for the scan record and the direct bundle-fixture service entry point,
on BSB-31-PENDING-3 for the verdict function, and on the externally supplied platform baseline and
pinned scanner image recorded in the kit. This story owns the parity test, the fixture's consumed
shape (`bundle`, `bundle_sha256`, `report`, `platform_verdict`), the parity assertion over the
scanner-identity fields on every `scans` row (`scanner_version`, `image_digest`, which
BSB-31-PENDING-1 writes), the `build_id NULL` assertion for build-less scans, and the failure
messages above. The parity test calls BSB-31-PENDING-1's direct bundle-fixture entry point (the
same entry point the HTTP route calls), passing the packed bundle fixture plus the pinned scanner
version and image digest, so it needs no build or project; every scan it creates has `build_id`
NULL per BSB-31-PENDING-1's record contract. The verdict comes from BSB-31-PENDING-3's function
and is not reimplemented in the test. The test does not own the baseline values: those come from
the platform's own scan of the same bundle with the same pinned scanner version, and the fixture is
refreshed when the platform pins a new scanner. The catalog reviewer consumes this parity evidence
through the catalog pull request's linked reports (FR-111), not through a builder screen.

Parity is asserted only when the builder's scanner version equals the baseline's; a mismatch is a
loud test failure, not a verdict comparison against a different scanner. The builder never
redefines the scanner's policy. The parity test runs against the local scanner image digest, not a
tag, so an image drift is visible as a version or digest difference rather than a silent verdict
change. The LLM stage's parity and model identity are BSB-32's.

---

**Story coverage summary**

| Requirement | Exercising story | Acceptance criteria that covers it |
|---|---|---|
| FR-076 | BSB-31-PENDING-1 | "Unscanned content is scanned before the run-start preflight returns a verdict"; "The scan reads the requested commit's bundle, not a newer branch head" |
| FR-077 | BSB-31-PENDING-2 | "An unchanged bundle and scanner version reuse the completed result"; "Changed bundle content starts a new scan"; "A different scanner version starts a new scan"; "The same bundle content at a new commit reuses the completed result"; "A request from a different build and project reuses the completed result" |
| FR-078 | BSB-31-PENDING-3 | "A DO_NOT_INSTALL recommendation fails even with no critical finding" |
| FR-079 | BSB-31-PENDING-3 | "Any critical finding fails even with a non-blocking recommendation" |
| FR-080 | BSB-31-PENDING-3 | "Incomplete coverage fails even with no blocking recommendation and no critical finding" |
| FR-081 | BSB-31-PENDING-3 | "An accepted critical finding cannot clear the block" |
| FR-087 | BSB-31-PENDING-4 | "A scan still running at ten minutes is terminated and recorded as failed"; "The ten-minute boundary terminates a scan that has not finished" |
| FR-088 | BSB-31-PENDING-4 | Same two scenarios: state "failed", verdict "fail", failure_reason "Scan exceeded the ten-minute limit." |
| FR-089 | BSB-31-PENDING-5 | "A completed passing scan shows its score, recommendation and coverage"; "A failed scan shows its failure reason instead of an in-progress state"; "A scan reused by a different build and project renders from the same URL" |
| FR-091 | BSB-31-PENDING-7 | "The builder's verdict matches the platform's on a fixed corpus"; "Every scan records the exact scanner identity it used"; "A scanner version mismatch is reported rather than compared"; "A bundle with no platform baseline fails the parity test" |
| FR-092 | BSB-31-PENDING-6 | "A project member starts a static-only scan and no run is created"; "A non-owner member can start the scan"; "A signed-in author who is not a project member is refused"; "An author with no project membership has no project to scan for" |
| FR-154 | BSB-31-PENDING-5 | "A completed passing scan shows its score, recommendation and coverage" |
| FR-155 | BSB-31-PENDING-5 | "Every finding is shown with severity, rule, file and line" |
| NFR-005 | BSB-31-PENDING-1 | "The static scanner container has no network access" |

All 14 requirements mapped to BSB-31 by `epic-map.json` are covered; no story claims a requirement
outside this epic.
