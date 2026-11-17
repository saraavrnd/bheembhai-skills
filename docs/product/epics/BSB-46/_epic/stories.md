# Stories — BSB-46 (Static security scanning)

Epic BSB-46 covers FR-076, FR-077, FR-078, FR-079, FR-080, FR-081, FR-087, FR-088,
FR-089, FR-091, FR-092, FR-154, FR-155 and NFR-005. It is decomposed into the 8 stories below;
every one of those 14 requirements is covered by at least one story's acceptance criteria.

**Prerequisite: identity, the authoring gate and test projects (FA-1 / BSB-39, FA-4 / BSB-43).**
BSB-39 owns sign-in, the builder's `users` table keyed by the Cognito `sub`, the `builder_session`
cookie and the request-time `skill-builders` group check. BSB-43 owns the test project,
`projects.owner_id`, `project_members` and the owner/member distinction: both roles are project
members for every membership decision in this epic. Every route here is an authoring route and
inherits the FA-1 gate: no valid session is HTTP 401 `{"error":"authentication_required"}`, and a
current `cognito:groups` claim without `skill-builders` is HTTP 403
`{"error":"membership_required"}` before any scan data is read or written. A signed-in
skill-builder who is not a member of the named test project is HTTP 403
`{"error":"project_membership_required"}` for APIs and a page body containing
`You are not a member of this test project` for pages. The builder database is
`postgres://builder-db:5432/skillbuilder`.

**Prerequisite: packaging and the catalog repository (FA-6 / BSB-45).** BSB-45 owns the catalog
fixture `bheembhai-skills`, the deterministic packer `tools/build.py`, the content-addressed
`skill_bundles` row keyed by `(skills_commit_sha, skill)`, `bundle_sha256`, the S3 object
`s3://builder-test/bundles/{bundle_sha256}.tar.zst`, `BB_PACK_LOG`, and the run-start route
`POST /api/projects/{project_id}/runs`. A static scan is never run against a working tree: it runs
against the exact bundle BSB-45 would hand to the run, so the scan's `content_sha256` is that
`bundle_sha256` and the run and the scan provably grade the same bytes. If no bundle row exists,
this epic invokes BSB-45's packer (and its BSB-51 packaging gates) before scanning. **The static
scan uses no project integration and no project secret**: it reads `bheembhai-skills` with the
builder's catalog read credential and runs the pinned scanner image, both external prerequisites
(PRD §8). A project with no `github` or `ai_model` integration can still start a static scan.
The run scenarios use BSB-45's fixture integrations for `prj_H5mQ2rT8vX` — `github`
`int_Gh7kL2pQ9r` naming the sandbox repository `sandbox-org/skilltest`, and `ai_model`
`int_Md4xN8sT2v` with `tier_models` `{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}` —
and the sandbox branch `fixtures/bug-142`, so a run request reaches the static-scan step rather
than failing BSB-45's validation.

**Fixture accounts.** The Cognito fixture is BSB-39's and BSB-43's:

| Account | Subject | Display name | Current `cognito:groups` | `users` row |
|---------|---------|--------------|--------------------------|-------------|
| `alice@example.test` | `sub-12345` | Alice Author | `["skill-builders"]` | `U_alice` |
| `bob@example.test` | `sub-67890` | Bob Builder | `["skill-builders"]` | `U_bob` |
| `casey@example.test` | `sub-99999` | Casey Newcomer | `["skill-builders"]` | `U_casey` |
| `dana@example.test` | `sub-13579` | *(no `name` claim)* | `["skill-builders"]` | `U_dana` |
| `erin@example.test` | `sub-11111` | Erin Ex-member | `[]` | `U_erin` |

`U_alice`, `U_bob`, `U_casey`, `U_dana` and `U_erin` stand for the actual `users.id` UUID value read
from the database (`SELECT id FROM users WHERE cognito_sub = 'sub-12345'` for `U_alice`, and
likewise for the other subjects); a test substitutes the value. Bob has no `project_members` row
unless a scenario's `Given` says so.

**Fixture projects.** The fixture builder database contains these `projects` and
`project_members` rows and no others; scenarios add further membership rows only where their
`Given` says so:

| `projects.id` | `name` | `owner_id` | `created_at` | `project_members` |
|---------------|--------|------------|--------------|-------------------|
| `prj_H5mQ2rT8vX` | Research quality | `U_alice` | `2026-11-16T09:00:00+00:00` | `(U_alice, owner)` |
| `prj_K9pL3wN6zB` | Release notes | `U_dana` | `2026-11-16T09:05:00+00:00` | `(U_dana, owner)` |

**Fixture catalog repository (`bheembhai-skills`).** The repository is BSB-41's and BSB-45's
fixture. `skills/sdlc-research-summarise/` is BSB-45's fixture: `SKILL.md`, `verify.yaml`,
`references/README.md`, `references/corpus.txt` (4,194,304 bytes of the byte `a`),
`templates/brief.md`, `examples/example-brief.md` and `assets/diagram.png` (2,048-byte PNG), a
total of 7 files, so a complete scan reports `{"files_scanned":7,"files_total":7}`. The branches
used by this epic are:

| Branch | Head SHA | Scan marker in `SKILL.md` |
|--------|----------|---------------------------|
| `main` | `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` | *(none — the fixture scanner defaults to `clean`)* |
| `test/saraav/research` | `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` | *(none — defaults to `clean`)* |
| `build/sdlc-research-summarise` | `9b2f4d6a8c0e2f5a7d1b3c6e8f0a2c4d6e8f1a3b` | *(none — defaults to `clean`)* |
| `test/saraav/large` | `e2b4d6f8a0c2e4b6d8f0a2c4e6b8d0f2a4c6e8b0` | *(none — defaults to `clean`)* |
| `test/saraav/static-clean` | `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0` | `<!-- scan-fixture: clean -->` |
| `test/saraav/static-dni` | `b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1` | `<!-- scan-fixture: do-not-install -->` |
| `test/saraav/static-critical` | `c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2` | `<!-- scan-fixture: critical -->` |
| `test/saraav/static-partial` | `d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3` | `<!-- scan-fixture: partial -->` |
| `test/saraav/static-accepted` | `e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4` | `<!-- scan-fixture: accepted -->` |
| `test/saraav/static-accepted-pass` | `f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5` | `<!-- scan-fixture: accepted-pass -->` |
| `test/saraav/static-accepted-partial` | `e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0` | `<!-- scan-fixture: accepted-partial -->` |
| `test/saraav/static-mixed` | `f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9` | `<!-- scan-fixture: mixed -->` |
| `test/saraav/static-timeout` | `a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6` | `<!-- scan-fixture: timeout -->` |
| `test/saraav/static-crash` | `b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7` | `<!-- scan-fixture: crash -->` |
| `test/saraav/static-slow-pass` | `c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8` | `<!-- scan-fixture: slow-pass -->` |

The marker is one line of each static fixture branch's
`skills/sdlc-research-summarise/SKILL.md`; every other file on that branch is byte-identical to
`test/saraav/research`, so a branch's only content difference is the marker (and, for the accepted
cases, the `.skillspector-baseline.yaml` file described below). The marker is part of the bundled
content, so each static branch has a different `content_sha256`. The fixture scanner writes the
`SKILL.md` marker into no field of its report; the report is selected by the case below.

**Pinned scanner kit.** `skill-builder/kit.txt` contains exactly `kit-v7`. Its `kit.json` has
`bheembhai_skillscan_version` `1.4.0`, `scanner_image`
`123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:5d3a9f1c7b2e4a6d8f0b1c3e5a7d9f2b4c6e8a0d1f3b5c7e9a2d4f6b8c0e1a3f`,
and `scanner_image_digest`
`sha256:5d3a9f1c7b2e4a6d8f0b1c3e5a7d9f2b4c6e8a0d1f3b5c7e9a2d4f6b8c0e1a3f`. The builder records
both values on every scan. The scanner image is always given by digest: a `scanner_image` given
by tag (for example `...bheembhai-skillscan:1.4.0` with no digest) is refused before a scan starts.

**Static scanner invocation and report contract.** The builder starts one short-lived scanner
container per scan, never parses skill content in the application process, and never uses the
scanner's MCP server mode. The fixture stand-in for that container is the `BB_SCAN_RUNNER`
executable, which appends one line to the file named by `BB_SCAN_LOG` before it starts the
scanner:

```text
scan <content_sha256> <scanner_version> <scanner_image_digest> network=none
```

The scanner is given the bundle read-only and writes one JSON report to its output mount. The
fixture scanner writes the `scanner_version` value read from the active `kit.json`, so a kit
change is reflected in its report unless a scenario says it deliberately writes a different
value. The report has exactly these fields:

- `scanner_version` — a string that must equal the pinned `bheembhai_skillscan_version`.
- `verdict` — `PASS` or `DO_NOT_INSTALL`.
- `score` — an integer from 0 through 100.
- `recommendation` — a non-empty string.
- `coverage` — an object with non-negative integer `files_scanned` and `files_total`.
- `findings` — an array of objects with `severity` one of `critical`, `high`, `medium`, `low`,
  non-empty `rule`, non-empty `file` relative to `skills/{skill}/`, positive integer `line`, and
  boolean `accepted`.
- `network_probe` — optional string; the fixture scanner writes `blocked` when every outbound
  probe failed.
- `network_attempts` — optional array of objects with `target` and `error`.

A report that is missing, malformed, has an unknown `verdict` or `severity`, or reports a
`scanner_version` other than the pinned one is a **scanner error**, not a result. The builder
stores the scanner's `verdict`, `score`, `recommendation`, `coverage` and `findings` values
unchanged; it adds its own pass classification (below) without rewriting them.

**Accepted findings.** An accepted finding is one the scanner reports with `accepted` `true`,
because the skill folder contains a matching entry in `.skillspector-baseline.yaml` (SK-001 §6b).
The baseline file is part of the scanned content, so adding or editing it changes the bundle's
`content_sha256` and forces a new scan. The builder never reads the baseline itself and never
lets `accepted` change the pass classification. The accepted fixture branches contain:

```yaml
- rule: SKILL-042
  file: SKILL.md
  line: 18
  reason: Test fixture accepted by catalog security on 2026-11-16.
- rule: SKILL-010
  file: references/README.md
  line: 4
  reason: Test fixture accepted by catalog security on 2026-11-16.
- rule: SKILL-020
  file: templates/brief.md
  line: 7
  reason: Test fixture accepted by catalog security on 2026-11-16.
```

The scanner marks a finding `accepted` only when its rule, file and line match an entry; the
`static-accepted-pass` and `static-accepted-partial` fixtures use the `SKILL-020` entry.

**Fixture scan cases.** The fixture scanner selects its report from the `SKILL.md` marker. The
reports are:

| Marker | `verdict` | `score` | `recommendation` | `coverage` | `findings` |
|--------|-----------|---------|------------------|------------|------------|
| *(none)* / `clean` | `PASS` | 100 | `Install` | `{"files_scanned":7,"files_total":7}` | `[]` |
| `do-not-install` | `DO_NOT_INSTALL` | 25 | `Do not install` | `{"files_scanned":7,"files_total":7}` | `[{"severity":"high","rule":"SKILL-042","file":"SKILL.md","line":18,"accepted":false}]` |
| `critical` | `PASS` | 60 | `Review findings before install` | `{"files_scanned":7,"files_total":7}` | `[{"severity":"critical","rule":"SKILL-010","file":"references/README.md","line":4,"accepted":false}]` |
| `partial` | `PASS` | 75 | `Review incomplete coverage` | `{"files_scanned":6,"files_total":7}` | `[]` |
| `accepted` | `DO_NOT_INSTALL` | 25 | `Do not install` | `{"files_scanned":7,"files_total":7}` | `[{"severity":"high","rule":"SKILL-042","file":"SKILL.md","line":18,"accepted":true},{"severity":"critical","rule":"SKILL-010","file":"references/README.md","line":4,"accepted":true}]` |
| `accepted-pass` | `PASS` | 90 | `Install` | `{"files_scanned":7,"files_total":7}` | `[{"severity":"medium","rule":"SKILL-020","file":"templates/brief.md","line":7,"accepted":true}]` |
| `accepted-partial` | `PASS` | 70 | `Review incomplete coverage` | `{"files_scanned":6,"files_total":7}` | `[{"severity":"medium","rule":"SKILL-020","file":"templates/brief.md","line":7,"accepted":true}]` |
| `mixed` | `PASS` | 55 | `Review findings before install` | `{"files_scanned":7,"files_total":7}` | `[{"severity":"low","rule":"SKILL-030","file":"templates/brief.md","line":9,"accepted":false},{"severity":"critical","rule":"SKILL-010","file":"references/README.md","line":4,"accepted":false},{"severity":"high","rule":"SKILL-042","file":"SKILL.md","line":18,"accepted":false},{"severity":"medium","rule":"SKILL-020","file":"templates/brief.md","line":7,"accepted":false}]` |
| `timeout` | *(no report)* | *(none)* | *(none)* | *(none)* | *(none)* |
| `crash` | *(no report)* | *(none)* | *(none)* | *(none)* | *(none)* |
| `slow-pass` | `PASS` | 100 | `Install` | `{"files_scanned":7,"files_total":7}` | `[]` |

`timeout` blocks without writing a report until it is killed; `crash` exits with status 3 and writes
no report; `slow-pass` writes the clean report and exits 0 when the fixture clock reaches
599,999 ms. The fixture scanner treats `.skillspector-baseline.yaml` as policy metadata, not a
skill file: it reads it to set `accepted` and excludes it from `files_scanned` and `files_total`,
so every branch's coverage denominator is the 7 skill files and only the skill file that cannot
be read in the `partial` and `accepted-partial` cases reduces the numerator.

**Static scan record (`static_scans`).** A scan attempt is one `static_scans` row. Columns:

| Column | Meaning |
|--------|---------|
| `id` | `scan_` followed by exactly 10 ASCII alphanumerics |
| `project_id` | the test project the scan is for |
| `user_id` | the `users.id` of the member who triggered it |
| `skill` | the skill folder name |
| `skills_ref` | the submitted branch of `bheembhai-skills` |
| `skills_commit_sha` | the 40-hex commit the branch resolved to at trigger time |
| `content_sha256` | the `skill_bundles.bundle_sha256` of the exact bundle scanned |
| `scanner_version` | the `bheembhai_skillscan_version` from the active `kit.json` (`1.4.0` for `kit-v7`) |
| `scanner_image_digest` | the `scanner_image_digest` from the active `kit.json` (`sha256:5d3a9f1c7b2e4a6d8f0b1c3e5a7d9f2b4c6e8a0d1f3b5c7e9a2d4f6b8c0e1a3f` for `kit-v7`) |
| `origin` | `run_start` or `skill_page` |
| `state` | `running`, `completed` or `failed` |
| `verdict` | `PASS` or `DO_NOT_INSTALL`; NULL while running or after failure |
| `score` | integer 0 through 100; NULL while running or after failure |
| `recommendation` | the scanner's recommendation; NULL while running or after failure |
| `coverage` | JSONB object; NULL while running or after failure |
| `findings` | JSONB array; NULL while running, `[]` when the scanner reported none |
| `passes` | boolean; the builder's classification below |
| `reasons` | JSONB array of reason codes, in the fixed order below |
| `failure_reason` | `timeout` or `scanner_error`; NULL otherwise |
| `report` | the scanner's full JSON report; NULL while running or after a failure without a report |
| `started_at`, `finished_at` | timestamptz; `finished_at` NULL while running |

A partial unique index on (`project_id`, `content_sha256`, `scanner_version`,
`scanner_image_digest`) where `state` is `running` or `completed` makes one active scan per
project, content and scanner build. A trigger that finds that row joins it: a `completed` row is
reused, a `running` row is waited for. A `failed` row is not covered by the index and is never
reused, so a retry creates a new scan. The reuse scope is the test project; cross-project reuse is
out of scope. The `runs` table gains one FA-11 column, `static_scan_id` (text, FK to
`static_scans.id`), set on every run this epic starts.

**Pass classification.** The classifier is one implementation shared by the run gate, the report
and any later Ready or CLI consumer. For a scan row:

- `passes` is `true` exactly when `state` is `completed`, `verdict` is `PASS`,
  `coverage.files_scanned` equals `coverage.files_total` (both are integers and neither is
  negative), and no finding has `severity` `critical`. The `accepted` field is ignored. For a
  `failed` scan `passes` is `false`.
- `reasons` is the ordered list of every condition that holds, in this order:
  1. `verdict_do_not_install` when `verdict` is `DO_NOT_INSTALL`;
  2. `critical_finding` when any finding has `severity` `critical`, accepted or not;
  3. `incomplete_coverage` when `coverage.files_scanned` is not equal to `coverage.files_total`.
  A `failed` scan has `reasons` `[]` and explains itself through `failure_reason`.
- A completed scan with `reasons` non-empty is a **blocked** scan. A failed scan is a **failed**
  scan. Only `passes` `true` admits a run.

**Run-start contract extension.** `POST /api/projects/{project_id}/runs` keeps BSB-45's request
body, success fields and error table, and adds one successful field, `static_scan_id`, matching
`^scan_[0-9A-Za-z]{10}$`; the `runs` row's `static_scan_id` equals it. The start order is:
FA-1 session and group gate, project existence and membership, BSB-45's request validation,
packaging gates and bundle resolution, **static scan**, branch creation, run insert. A blocked or
failed scan therefore changes no `runs` row and creates no `skilltest/*` branch; a bundle object
created before the scan may remain in the content-addressed cache, and a `skill_bundles` row may
remain. The added errors are:

| Condition | Response |
|-----------|----------|
| A completed scan has one or more `reasons` | HTTP 422 `{"error":"static_scan_blocked","scan_id":"<scan_id>","reasons":["<ordered reason codes>"]}` |
| The scan timed out | HTTP 503 `{"error":"static_scan_failed","scan_id":"<scan_id>","reason":"timeout"}` |
| The scanner exited without a valid report, or reported the wrong version | HTTP 503 `{"error":"static_scan_failed","scan_id":"<scan_id>","reason":"scanner_error"}` |
| The pinned scanner image is given by tag, not digest | HTTP 503 `{"error":"scanner_image_not_pinned"}`; no `static_scans` row and no run |

**Skill-page scan contract.** The skill page is
`GET /projects/{project_id}/skills/{skill}`; it is a project-scoped scan page, not a project copy
of a skill. It offers the branches of `bheembhai-skills` that contain `skills/{skill}/` and a
**Security check** button. A scan is
`POST /api/projects/{project_id}/skills/{skill}/scans` with `Content-Type: application/json` and
body `{"skills_ref":"<branch>"}`. The caller must be a project member; the route needs no project
integration and no secret. The builder resolves the branch, packages or reuses the bundle (with
BSB-51's packaging gates), then starts the static scan; it creates no `runs` row, no
`skilltest/*` branch and spends no model tokens. The response is:

- HTTP 202, body `{"scan_id":"<scan_id>","state":"running","reused":false,"project_id":"<id>","skill":"<skill>","skills_ref":"<branch>","skills_commit_sha":"<40-hex>","content_sha256":"<64-hex>"}` when a new scan starts.
- HTTP 202 with the same fields, `state` `running` and `reused` `true` when an identical scan is
  already running for the project; the caller joins it.
- HTTP 200 with the same fields, `state` `completed`, `reused` `true` and the report fields below
  when an identical completed scan exists.

The added errors are: HTTP 422 `{"error":"skills_ref_required"}` for a missing or blank
`skills_ref`; HTTP 404 `{"error":"skills_branch_not_found","branch":"<branch>"}` for a branch
absent from `bheembhai-skills`; HTTP 404 `{"error":"skill_not_found","skill":"<skill>"}` when the
folder is absent at the resolved commit; HTTP 422 `{"error":"packaging_gates_failed"}` when
BSB-51's gates reject the skill; HTTP 503 `{"error":"bundle_store_unavailable"}` when the bundle
cannot be stored; HTTP 503 `{"error":"scanner_image_not_pinned"}` for a tagged scanner image.
Authentication, group and membership errors precede all validation, and a rejected request
creates no `static_scans` row and writes no `BB_SCAN_LOG` line. The scan itself runs
asynchronously: a trigger returns without waiting for the scanner, and the result is read from
`GET /api/scans/{scan_id}` or `GET /scans/{scan_id}`.

**Report contract.** `GET /api/scans/{scan_id}` is available to a member of the scan's
`project_id` and returns HTTP 200 with JSON carrying `scan_id`, `project_id`, `user_id`, `skill`,
`skills_ref`, `skills_commit_sha`, `content_sha256`, `scanner_version`, `scanner_image_digest`,
`origin`, `state`, `verdict`, `score`, `recommendation`, `coverage`, `findings`, `passes`,
`reasons`, `failure_reason`, `started_at` and `finished_at`. `findings` is normalized to the
stable order: severity rank `critical`, `high`, `medium`, `low`; then `file` in ascending byte
order; then `line` ascending; then `rule` in ascending byte order. A report with no result has
`verdict`, `score`, `recommendation` and `coverage` null, `findings` `[]`, `passes` false and
`reasons` `[]`. `GET /scans/{scan_id}` renders the same data as HTML and contains
`data-testid="scan-verdict"` (text exactly `PASS`, `DO_NOT_INSTALL` or `Failed`),
`data-testid="scan-score"` (text exactly the decimal score, or `—` when null),
`data-testid="scan-recommendation"` (text exactly the recommendation, or `—` when null),
`data-testid="scan-scanner-version"` (text exactly the scanner version), one
`data-testid="scan-finding"` element per finding with attributes `data-severity`, `data-rule`,
`data-file` and `data-line`, one `data-testid="scan-reason"` element per reason with text exactly
the reason code, and `data-testid="scan-failure"` with text exactly
`Scan failed: timed out after 600 seconds` for a timeout or `Scan failed: scanner error` for a
scanner error. A non-member gets HTTP 403; an unknown scan id gets HTTP 404
`{"error":"scan_not_found"}`; no session gets HTTP 401 `{"error":"authentication_required"}`.

**Timeout contract.** The scanner's deadline is 600,000 ms from `started_at`; at exactly
600,000 ms the builder terminates the scanner container and records the scan as `failed` with
`failure_reason` `timeout` and `finished_at` equal to `started_at` plus 600,000 ms. A scanner that
writes a valid report and exits 0 at 599,999 ms is `completed`. The fixture clock in the tests
advances the scan deadline without waiting real time; the production deadline is always 600,000
ms.

**Scope boundaries.** FA-12 (BSB-47) owns the model-based scan, its model profile and the full
scan; this epic starts only the static stage and makes no model call. FA-8 (BSB-49) owns the
pre-run preflight that refuses a start when the static scan did not pass (FR-055); it consumes
this epic's classifier and does not re-implement it. FA-10B (BSB-51) owns Ready evaluation
(FR-069/FR-070) and the packaging gates invoked before a bundle is accepted. FA-13 (BSB-52/53)
owns run reports and audit records. FA-16 (BSB-55) owns the CLI static-only scan (FR-117); it
calls the same scan service. FA-15 (BSB-54) owns catalog submission.

> **Input note.** The run's placeholder work item `SkillBuilder-2` was queried through the
> Atlassian MCP configured in `.mcp.json`: `jira_get_issue` rejects the key before any request
> with its own key pattern `^[A-Z][A-Z0-9_]+-\d+(?:-\d+)*$` because `SkillBuilder` contains
> lowercase letters; `jira_search` with `text ~ "SkillBuilder-2"` and `summary ~ "SkillBuilder"`
> returned no issues; `jira_get_all_projects` returned BEEM, BSB, EX, GRAP and LNPRTL with no
> `SkillBuilder` project. The placeholder contributes no scope, and `docs/product/PRD.md` §8
> records the same finding. The run's actual item is the epic `BSB-46`, fetched through the same
> MCP: summary "Static security scanning", type Epic, status To Do, labels FA-11 and MVP; its
> description, functional scope, edge cases, non-goals, implementation guidance, Definition of
> Done and covered requirements match `docs/product/epics.md` and `docs/product/epic-map.json`.

## Coverage summary

| Story | Requirements covered |
|-------|----------------------|
| BSB-46-PENDING-1 — Block a run whose static scan does not pass | FR-076, FR-078, FR-079, FR-080 |
| BSB-46-PENDING-2 — Reuse a completed static scan for unchanged content | FR-077 |
| BSB-46-PENDING-3 — Keep an accepted finding from clearing a static-scan block | FR-081 |
| BSB-46-PENDING-4 — Time out a static scan after ten minutes and record it as failed | FR-087, FR-088 |
| BSB-46-PENDING-5 — Show the scan score, recommendation and findings in the report | FR-089, FR-154, FR-155 |
| BSB-46-PENDING-6 — Match the platform's verdict for the same content and scanner version | FR-091 |
| BSB-46-PENDING-7 — Start a static-only scan from the skill page without a run | FR-092 |
| BSB-46-PENDING-8 — Run the static scan with no network access | NFR-005 |

---

## STORY: BSB-46-PENDING-1

**Title:** Block a run whose static scan does not pass
**Epic:** BSB-46 · **Release:** MVP · **Estimate:** 8 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **every run to stop when the static security scan of its exact skill content does not pass**, so that **unsafe content cannot reach a test run even when the scanner's verdict alone looks acceptable or the scan is incomplete**.

### Acceptance Criteria
Scenario: A clean skill is scanned before the run is created
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-clean` is at commit `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0`, its `skills/sdlc-research-summarise/SKILL.md` contains `<!-- scan-fixture: clean -->`, `BB_SCAN_LOG` is empty, and `skill_bundles` has no row for that commit and `sdlc-research-summarise`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-clean","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 201 and a JSON body whose `static_scan_id` matches `^scan_[0-9A-Za-z]{10}$` and whose `bundle_sha256` matches `^[0-9a-f]{64}$`; let `S` be the `static_scan_id` and `B` the `bundle_sha256`; the `static_scans` row `S` has `project_id` `prj_H5mQ2rT8vX`, `user_id` `U_alice`, `skill` `sdlc-research-summarise`, `skills_ref` `test/saraav/static-clean`, `skills_commit_sha` `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0`, `content_sha256` `B`, `scanner_version` `1.4.0`, `scanner_image_digest` `sha256:5d3a9f1c7b2e4a6d8f0b1c3e5a7d9f2b4c6e8a0d1f3b5c7e9a2d4f6b8c0e1a3f`, `origin` `run_start`, `state` `completed`, `verdict` `PASS`, `score` 100, `recommendation` `Install`, `coverage` exactly `{"files_scanned":7,"files_total":7}`, `findings` exactly `[]`, `passes` true, `reasons` exactly `[]` and `failure_reason` NULL; the `runs` row whose `id` is the response's `run_id` has `static_scan_id` `S`; and `BB_SCAN_LOG` contains exactly one line `scan B 1.4.0 sha256:5d3a9f1c7b2e4a6d8f0b1c3e5a7d9f2b4c6e8a0d1f3b5c7e9a2d4f6b8c0e1a3f network=none`

Scenario: A DO_NOT_INSTALL verdict blocks the run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-dni` is at commit `b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1`, and `BB_SCAN_LOG` is empty
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-dni","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and a JSON body whose `error` is `static_scan_blocked`, whose `scan_id` matches `^scan_[0-9A-Za-z]{10}$` and whose `reasons` equals `["verdict_do_not_install"]`; let `S` be that `scan_id`; the `static_scans` row `S` has `state` `completed`, `verdict` `DO_NOT_INSTALL`, `score` 25, `recommendation` `Do not install`, `coverage` exactly `{"files_scanned":7,"files_total":7}`, `findings` exactly `[{"severity":"high","rule":"SKILL-042","file":"SKILL.md","line":18,"accepted":false}]`, `passes` false and `reasons` exactly `["verdict_do_not_install"]`; the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`; and no branch matching `skilltest/*` is created in the sandbox repository

Scenario: A critical finding blocks a run whose verdict is PASS
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-critical` is at commit `c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2`, and `BB_SCAN_LOG` is empty
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-critical","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and a JSON body whose `error` is `static_scan_blocked` and whose `reasons` equals `["critical_finding"]`; let `S` be that body's `scan_id`; the `static_scans` row `S` has `state` `completed`, `verdict` `PASS`, `score` 60, `recommendation` `Review findings before install`, `findings` exactly `[{"severity":"critical","rule":"SKILL-010","file":"references/README.md","line":4,"accepted":false}]`, `passes` false and `reasons` exactly `["critical_finding"]`; the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`; and no branch matching `skilltest/*` is created

Scenario: Incomplete coverage blocks a run whose verdict is PASS
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-partial` is at commit `d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3`, and `BB_SCAN_LOG` is empty
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-partial","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and a JSON body whose `error` is `static_scan_blocked` and whose `reasons` equals `["incomplete_coverage"]`; let `S` be that body's `scan_id`; the `static_scans` row `S` has `state` `completed`, `verdict` `PASS`, `score` 75, `recommendation` `Review incomplete coverage`, `coverage` exactly `{"files_scanned":6,"files_total":7}`, `findings` exactly `[]`, `passes` false and `reasons` exactly `["incomplete_coverage"]`; the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`; and no branch matching `skilltest/*` is created

Scenario: A non-member cannot start a run and no scan is started
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `builder_session` cookie, the `project_members` table has no row for `prj_H5mQ2rT8vX` and `U_bob`, and `BB_SCAN_LOG` is empty
When Bob submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-clean","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 403 and body exactly `{"error":"project_membership_required"}`, the `static_scans` table gains no row for `project_id` `prj_H5mQ2rT8vX`, `BB_SCAN_LOG` is empty, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: A scanner crash fails the scan without starting a run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-crash` is at commit `b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7`, its fixture scanner exits with status 3 and writes no report, and `BB_SCAN_LOG` is empty
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-crash","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 503 and a JSON body whose `error` is `static_scan_failed`, whose `scan_id` matches `^scan_[0-9A-Za-z]{10}$` and whose `reason` is `scanner_error`; the `static_scans` row with that id has `state` `failed`, `failure_reason` `scanner_error`, `verdict` NULL, `score` NULL, `recommendation` NULL, `coverage` NULL, `findings` exactly `[]`, `passes` false and `reasons` exactly `[]`; the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`; and no branch matching `skilltest/*` is created

### Covered requirements (traceability)
- FR-076
- FR-078
- FR-079
- FR-080

### Out of scope
The reuse of a completed scan (BSB-46-PENDING-2); the special handling of accepted findings (BSB-46-PENDING-3); the ten-minute timeout and its failure record (BSB-46-PENDING-4); the report fields beyond the pass reasons (BSB-46-PENDING-5); platform-parity comparison (BSB-46-PENDING-6); the skill-page entry point (BSB-46-PENDING-7); the scanner's network isolation (BSB-46-PENDING-8); the model-based scan (FA-12 / BSB-47); fixing findings; the pre-run preflight owned by FA-8 (BSB-49, FR-055) and the packaging gates owned by FA-10B (BSB-51).

### Notes / dependencies
Depends on FA-1 (BSB-39) for the `users` row, the `builder_session` cookie and the request-time `skill-builders` gate; on FA-4 (BSB-43) for `projects` and `project_members`; and on FA-6 (BSB-45) for `POST /api/projects/{project_id}/runs`, the packer, `skill_bundles`, `bundle_sha256` and `BB_PACK_LOG`. The scan is performed on the bundle BSB-45 would hand to the run, so its `content_sha256` is the run's `bundle_sha256`; this is how FR-076's "exact skill content" is proved. The scan happens after the bundle is resolved and before the run branch is created, which is why a blocked run leaves no branch. The classifier in the preface is the single implementation FA-8 (FR-055), FA-10B (FR-069/FR-070) and FA-16 (FR-117) must reuse. `static_scan_id` is the one new `runs` column (SK-001 §9 lists none), added because a run must be traceable to the scan that admitted it; if the architecture pins a different name, only that name changes.

---

## STORY: BSB-46-PENDING-2

**Title:** Reuse a completed static scan for unchanged content
**Epic:** BSB-46 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **a repeated run of unchanged skill content to reuse its completed static scan**, so that **repeated runs prepare quickly and grade exactly the same bytes without rescanning**.

### Acceptance Criteria
Scenario: A second run of the same content reuses the completed scan
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and Alice has prepared run `run_Ab3dE5fG7h` from `test/saraav/static-clean` so that a completed scan `S0` exists for the project with `content_sha256` `B` and `BB_SCAN_LOG` contains one line
When Alice starts a second run from the same body with `skills_branch` `test/saraav/static-clean`
Then the builder responds with HTTP 201 and the response's `static_scan_id` is `S0`; the `runs` table contains exactly two rows for `project_id` `prj_H5mQ2rT8vX` and both have `static_scan_id` `S0`; the `static_scans` table contains exactly one row for `project_id` `prj_H5mQ2rT8vX` and `content_sha256` `B`; and `BB_SCAN_LOG` still contains exactly one line

Scenario: Changed content starts a new scan
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, a completed scan `S0` exists for `test/saraav/static-clean` at commit `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0` with `content_sha256` `B0`, and `BB_SCAN_LOG` contains one line
When the test creates a commit `C2` on `test/saraav/static-clean` whose `skills/sdlc-research-summarise/SKILL.md` adds the line `# Research summarise (v2)` after the title (`C2` is that commit's own 40-hex SHA), and Alice starts a run from the same body with `skills_branch` `test/saraav/static-clean`
Then the builder responds with HTTP 201; let `B2` be the response's `bundle_sha256`; `B2` is not `B0`; the `static_scans` table contains a new row `S1` with `content_sha256` `B2`, `skills_commit_sha` `C2`, `state` `completed`, `passes` true; the `runs` row for the new run has `static_scan_id` `S1`; and `BB_SCAN_LOG` contains exactly two lines, the first ending with `B0` and the second ending with `B2`

Scenario: The same content with a different scanner version is not reused
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, a completed scan `S0` exists for `test/saraav/static-clean` with `content_sha256` `B`, `scanner_version` `1.4.0` and `scanner_image_digest` `sha256:5d3a9f1c7b2e4a6d8f0b1c3e5a7d9f2b4c6e8a0d1f3b5c7e9a2d4f6b8c0e1a3f`, and `BB_SCAN_LOG` contains one line
When the test replaces `skill-builder/kit.txt` with `kit-v8`, whose `kit.json` has `bheembhai_skillscan_version` `1.4.1` and `scanner_image_digest` `sha256:9e4b17c2a6f8d1e3a5b7c9d0e2f4a6b8c1d3e5f7a9b0c2d4e6f8a1b3c5d7e9f0`, and Alice starts a run from the same body with `skills_branch` `test/saraav/static-clean`
Then the builder responds with HTTP 201; the `static_scans` table contains a new row `S1` with `content_sha256` `B`, `scanner_version` `1.4.1` and `scanner_image_digest` `sha256:9e4b17c2a6f8d1e3a5b7c9d0e2f4a6b8c1d3e5f7a9b0c2d4e6f8a1b3c5d7e9f0`; the row `S0` still has `scanner_version` `1.4.0`; the new run's `static_scan_id` is `S1`; and `BB_SCAN_LOG` contains exactly two lines, the second ending `1.4.1 sha256:9e4b17c2a6f8d1e3a5b7c9d0e2f4a6b8c1d3e5f7a9b0c2d4e6f8a1b3c5d7e9f0 network=none`

Scenario: A completed failing scan is reused and still blocks
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and a completed scan `S0` exists for `test/saraav/static-dni` with `content_sha256` `B`, `verdict` `DO_NOT_INSTALL`, `passes` false and `BB_SCAN_LOG` contains one line
When Alice starts a run from the same body with `skills_branch` `test/saraav/static-dni`
Then the builder responds with HTTP 422 and a JSON body whose `error` is `static_scan_blocked`, whose `scan_id` is `S0` and whose `reasons` equals `["verdict_do_not_install"]`; the `static_scans` table still contains exactly one row for `content_sha256` `B`; `BB_SCAN_LOG` still contains exactly one line; and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: A failed scan is not reused
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, a failed scan `Sf` exists for `test/saraav/static-crash` with `content_sha256` `Bf`, `state` `failed` and `failure_reason` `scanner_error`, and `BB_SCAN_LOG` contains one line
When Alice starts a run from the same body with `skills_branch` `test/saraav/static-crash`
Then the builder responds with HTTP 503 and a JSON body whose `error` is `static_scan_failed` and whose `scan_id` is not `Sf`; the `static_scans` table contains `Sf` and one new row `Sn` with `state` `failed` and `failure_reason` `scanner_error`; `BB_SCAN_LOG` contains exactly two lines; and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: Concurrent starts of the same content share one scan
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row with `role` `member`, both are signed in, `test/saraav/static-clean` is at commit `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0`, no `static_scans` row exists for the project and that content, and `BB_SCAN_LOG` is empty
When Alice and Bob submit the same run body with `skills_branch` `test/saraav/static-clean` at the same time
Then both requests respond with HTTP 201 and the same `static_scan_id` `S`; the `static_scans` table contains exactly one row for `project_id` `prj_H5mQ2rT8vX` and that `content_sha256`; both `runs` rows have `static_scan_id` `S`; and `BB_SCAN_LOG` contains exactly one line

### Covered requirements (traceability)
- FR-077

### Out of scope
The first scan of a content hash (BSB-46-PENDING-1); accepted-finding semantics (BSB-46-PENDING-3); the timeout rules (BSB-46-PENDING-4); the report rendering (BSB-46-PENDING-5); platform-parity comparison (BSB-46-PENDING-6); the skill-page trigger (BSB-46-PENDING-7); cross-project reuse and eviction of old scan rows; caching across a scanner image change without a version change.

### Notes / dependencies
Depends on BSB-46-PENDING-1 for the run-start gate and the `static_scans` row shape. The reuse key is (`project_id`, `content_sha256`, `scanner_version`, `scanner_image_digest`); `content_sha256` is BSB-45's deterministic `bundle_sha256`, so unchanged content always hashes identically and a changed branch or changed `.skillspector-baseline.yaml` always changes it. A completed scan is reused even when it does not pass, because FR-077 reuses a completed result and the block remains; a `failed` scan is not a completed result and is always retried. The concurrent-start case is resolved by the partial unique index in the preface: one trigger inserts `running`, the racing trigger finds it and joins, and both runs link to the winner. The `kit-v8` fixture is a test-only pin change; the production kit is `kit-v7` and the scanner version is `1.4.0`.

---

## STORY: BSB-46-PENDING-3

**Title:** Keep an accepted finding from clearing a static-scan block
**Epic:** BSB-46 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **an accepted finding to remain visible but never to turn a non-passing scan into a passing one**, so that **a policy acceptance cannot be used to bypass the static-scan gate**.

### Acceptance Criteria
Scenario: An accepted DO_NOT_INSTALL verdict still blocks the run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-accepted` is at commit `e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4`, its `.skillspector-baseline.yaml` accepts `SKILL-042` and `SKILL-010`, and `BB_SCAN_LOG` is empty
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-accepted","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and a JSON body whose `error` is `static_scan_blocked` and whose `reasons` equals `["verdict_do_not_install","critical_finding"]`; let `S` be that body's `scan_id`; the `static_scans` row `S` has `state` `completed`, `verdict` `DO_NOT_INSTALL`, `findings` exactly `[{"severity":"high","rule":"SKILL-042","file":"SKILL.md","line":18,"accepted":true},{"severity":"critical","rule":"SKILL-010","file":"references/README.md","line":4,"accepted":true}]`, `passes` false and `reasons` exactly `["verdict_do_not_install","critical_finding"]`; and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: An accepted critical finding alone still blocks a PASS scan
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-critical` is at commit `c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2`, and the test adds a `.skillspector-baseline.yaml` to that branch accepting `SKILL-010` at `references/README.md` line 4
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-critical","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and a JSON body whose `error` is `static_scan_blocked` and whose `reasons` equals `["critical_finding"]`; let `S` be that body's `scan_id`; the `static_scans` row `S` has `verdict` `PASS`, `score` 60, `findings` exactly `[{"severity":"critical","rule":"SKILL-010","file":"references/README.md","line":4,"accepted":true}]`, `passes` false and `reasons` exactly `["critical_finding"]`; and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: Acceptance does not turn a passing scan into a block
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-accepted-pass` is at commit `f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5`, and its report has `verdict` `PASS`, `score` 90 and one accepted `medium` finding
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-accepted-pass","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 201; the `static_scans` row has `verdict` `PASS`, `score` 90, `findings` exactly `[{"severity":"medium","rule":"SKILL-020","file":"templates/brief.md","line":7,"accepted":true}]`, `passes` true and `reasons` exactly `[]`; and the `runs` row has that scan's `static_scan_id`

Scenario: Acceptance cannot clear an incomplete-coverage block
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-accepted-partial` is at commit `e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0`, and its report has `verdict` `PASS`, `score` 70, `coverage` `{"files_scanned":6,"files_total":7}` and one accepted `medium` finding
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-accepted-partial","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and a JSON body whose `error` is `static_scan_blocked` and whose `reasons` equals `["incomplete_coverage"]`; the `static_scans` row named by that body has `passes` false, `coverage` exactly `{"files_scanned":6,"files_total":7}` and `findings` exactly `[{"severity":"medium","rule":"SKILL-020","file":"templates/brief.md","line":7,"accepted":true}]`; and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

### Covered requirements (traceability)
- FR-081

### Out of scope
Who may write a `.skillspector-baseline.yaml` entry and its CODEOWNERS review (catalog policy, SK-001 §6b); the scanner's own matching of a baseline entry to a finding; changing or overriding a finding's severity; the model-based scan's accepted findings (FA-12 / BSB-47); fixing a finding or editing the skill.

### Notes / dependencies
Depends on BSB-46-PENDING-1 for the pass classifier and the run-start gate. The scanner, not the builder, decides `accepted`; the builder only refuses to let that boolean alter `passes` or `reasons`. This is the epic's "findings previously accepted by policy" edge case: acceptance is shown to the author and retained in `findings`, but the block stands. Because `.skillspector-baseline.yaml` is part of the scanned bundle, editing it changes `content_sha256` and forces a new scan under `BSB-46-PENDING-2`; it still cannot clear a critical, `DO_NOT_INSTALL` or incomplete-coverage block.

---

## STORY: BSB-46-PENDING-4

**Title:** Time out a static scan after ten minutes and record it as failed
**Epic:** BSB-46 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **a static scan that runs past ten minutes to be stopped and recorded as failed**, so that **a hung or crashing scanner cannot hold a run open or be mistaken for a pass**.

### Acceptance Criteria
Scenario: A scan still running at ten minutes is killed and recorded as failed
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-timeout` is at commit `a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6`, its fixture scanner blocks without writing a report, the builder's scan clock is the fixture clock, and `BB_SCAN_LOG` is empty
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/static-timeout","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}` and the fixture clock advances to 600,000 ms after the scan starts
Then the builder terminates the scanner and responds with HTTP 503 and a JSON body whose `error` is `static_scan_failed`, whose `scan_id` matches `^scan_[0-9A-Za-z]{10}$` and whose `reason` is `timeout`; let `S` be that `scan_id`; the `static_scans` row `S` has `state` `failed`, `failure_reason` `timeout`, `verdict` NULL, `score` NULL, `recommendation` NULL, `coverage` NULL, `findings` exactly `[]`, `passes` false, `reasons` exactly `[]` and `finished_at` exactly 600,000 ms after `started_at`; the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`; and no branch matching `skilltest/*` is created

Scenario: A scan that completes just before the deadline is completed
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-slow-pass` is at commit `c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8`, its fixture scanner writes the clean report and exits 0 at fixture-clock 599,999 ms, and `BB_SCAN_LOG` is empty
When Alice starts a run with `skills_branch` `test/saraav/static-slow-pass` and the fixture clock advances to 599,999 ms after the scan starts
Then the builder responds with HTTP 201; the `static_scans` row has `state` `completed`, `verdict` `PASS`, `score` 100, `passes` true, `failure_reason` NULL and `finished_at` exactly 599,999 ms after `started_at`; and the `runs` row has that scan's `static_scan_id`

Scenario: A malformed scanner report is recorded as a scanner error
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, the fixture scanner for `test/saraav/static-crash` instead exits 0 and writes exactly `{"scanner_version":"1.4.0","verdict":"MAYBE"}`, and `BB_SCAN_LOG` is empty
When Alice starts a run with `skills_branch` `test/saraav/static-crash`
Then the builder responds with HTTP 503 and a JSON body whose `error` is `static_scan_failed` and whose `reason` is `scanner_error`; the `static_scans` row named by that body has `state` `failed`, `failure_reason` `scanner_error`, `verdict` NULL, `score` NULL, `coverage` NULL and `passes` false; and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: A timed-out skill-page scan is visible as failed and can be retried
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-timeout` is at commit `a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6`, and Alice has started a skill-page scan `S` for it with the fixture clock
When the fixture clock advances to 600,000 ms after the scan starts and the test reads `GET /api/scans/S` and `GET /scans/S`
Then `GET /api/scans/S` returns HTTP 200 with `state` `failed`, `failure_reason` `timeout`, `verdict` null, `score` null and `passes` false; `GET /scans/S` contains `data-testid="scan-failure"` with text exactly `Scan failed: timed out after 600 seconds`, `data-testid="scan-verdict"` with text exactly `Failed`, and `data-testid="scan-score"` with text exactly `—`; the `runs` table gains no row; and a second scan of the same content gets a different `scan_id`, because the failed row is not reused

### Covered requirements (traceability)
- FR-087
- FR-088

### Out of scope
The run deadline and spend caps owned by FA-8 (BSB-49, NFR-007/NFR-008/NFR-019); retry policy, backoff or notification for a failed scan; the scanner's own internal timeouts; the LLM stage's timeout (FA-12 / BSB-47); any human override of a failed scan.

### Notes / dependencies
Depends on BSB-46-PENDING-1 for the run-start gate and BSB-46-PENDING-2 for the rule that a failed scan is not reused. The deadline is measured from `static_scans.started_at` and is 600,000 ms in production. The tests use a fixture clock to exercise the boundary without waiting ten minutes; this is a test seam, not a product setting. A timeout and a scanner error both leave `state` `failed`; `failure_reason` distinguishes them, and neither has a score or recommendation, so FR-088's "recorded as failed" is directly observable in `static_scans` and the report. The scanner is killed, not merely marked failed: no scanner process outlives the deadline.

---

## STORY: BSB-46-PENDING-5

**Title:** Show the scan score, recommendation and findings in the report
**Epic:** BSB-46 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the static-scan report to show the score, the recommendation and every finding's severity, rule, file and line**, so that **I can see exactly why a run was blocked and what to fix**.

### Acceptance Criteria
Scenario: A blocked scan's report shows its score, recommendation and findings
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and a scan `S` for `test/saraav/static-dni` has completed with the report in the preface
When Alice calls `GET /api/scans/S` and opens `GET /scans/S`
Then the JSON has `scan_id` `S`, `state` `completed`, `verdict` `DO_NOT_INSTALL`, `score` 25, `recommendation` `Do not install`, `coverage` exactly `{"files_scanned":7,"files_total":7}`, `findings` exactly `[{"severity":"high","rule":"SKILL-042","file":"SKILL.md","line":18,"accepted":false}]`, `passes` false and `reasons` exactly `["verdict_do_not_install"]`; the HTML contains `data-testid="scan-verdict"` with text exactly `DO_NOT_INSTALL`, `data-testid="scan-score"` with text exactly `25`, `data-testid="scan-recommendation"` with text exactly `Do not install`, one `data-testid="scan-finding"` element with `data-severity` `high`, `data-rule` `SKILL-042`, `data-file` `SKILL.md` and `data-line` `18`, and one `data-testid="scan-reason"` element with text exactly `verdict_do_not_install`

Scenario: A passing scan's report shows the score and recommendation with no findings
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and a scan `S` for `test/saraav/static-clean` has completed
When Alice calls `GET /api/scans/S` and opens `GET /scans/S`
Then the JSON has `verdict` `PASS`, `score` 100, `recommendation` `Install`, `coverage` exactly `{"files_scanned":7,"files_total":7}`, `findings` exactly `[]`, `passes` true and `reasons` exactly `[]`; the HTML contains `data-testid="scan-verdict"` with text exactly `PASS`, `data-testid="scan-score"` with text exactly `100`, `data-testid="scan-recommendation"` with text exactly `Install`, zero `data-testid="scan-finding"` elements and no `data-testid="scan-reason"` element

Scenario: Findings are listed in a stable order
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and a scan `S` for `test/saraav/static-mixed` has completed with the four findings in the preface's `mixed` case, returned by the fixture scanner in the order low, critical, high, medium
When Alice calls `GET /api/scans/S`
Then `findings` equals exactly `[{"severity":"critical","rule":"SKILL-010","file":"references/README.md","line":4,"accepted":false},{"severity":"high","rule":"SKILL-042","file":"SKILL.md","line":18,"accepted":false},{"severity":"medium","rule":"SKILL-020","file":"templates/brief.md","line":7,"accepted":false},{"severity":"low","rule":"SKILL-030","file":"templates/brief.md","line":9,"accepted":false}]`

Scenario: A failed scan's report shows no score or recommendation
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and a scan `S` for `test/saraav/static-timeout` has `state` `failed` and `failure_reason` `timeout`
When Alice calls `GET /api/scans/S` and opens `GET /scans/S`
Then the JSON has `state` `failed`, `verdict` null, `score` null, `recommendation` null, `coverage` null, `findings` exactly `[]`, `passes` false and `failure_reason` `timeout`; the HTML contains `data-testid="scan-verdict"` with text exactly `Failed`, `data-testid="scan-score"` with text exactly `—`, `data-testid="scan-recommendation"` with text exactly `—`, zero `data-testid="scan-finding"` elements, and `data-testid="scan-failure"` with text exactly `Scan failed: timed out after 600 seconds`

Scenario: A non-member cannot read a scan report
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), scan `S` belongs to `prj_H5mQ2rT8vX`, Bob (`U_bob`) has a `builder_session` cookie, and the `project_members` table has no row for `prj_H5mQ2rT8vX` and `U_bob`
When Bob calls `GET /api/scans/S` and opens `GET /scans/S`
Then `GET /api/scans/S` responds with HTTP 403 and body exactly `{"error":"project_membership_required"}`, `GET /scans/S` responds with HTTP 403 and a body containing `You are not a member of this test project`, and neither response contains `score`, `recommendation` or `findings` data

Scenario: A request with no session is rejected before any report data
Given no `builder_session` cookie and a scan `S` that exists
When the visitor calls `GET /api/scans/S` and opens `GET /scans/S`
Then `GET /api/scans/S` responds with HTTP 401 and body exactly `{"error":"authentication_required"}`, `GET /scans/S` responds with HTTP 401, and neither response contains report data

Scenario: An unknown scan is not found
Given Alice (`U_alice`) has a `builder_session` cookie and no scan row has id `scan_ZZZZZZZZZZ`
When Alice calls `GET /api/scans/scan_ZZZZZZZZZZ` and opens `GET /scans/scan_ZZZZZZZZZZ`
Then `GET /api/scans/scan_ZZZZZZZZZZ` responds with HTTP 404 and body exactly `{"error":"scan_not_found"}`, `GET /scans/scan_ZZZZZZZZZZ` responds with HTTP 404 and a body containing `Scan not found`, and neither response contains report data

### Covered requirements (traceability)
- FR-089
- FR-154
- FR-155

### Out of scope
The report's visual design beyond the required `data-testid` elements and texts; the run page's Security tab and run report links (FA-13 / BSB-53); the LLM scan's model field and findings (FA-12 / BSB-47); exporting a report to SARIF for the catalog CI; downloading the raw scanner report.

### Notes / dependencies
Depends on BSB-46-PENDING-1 for the scan row and on BSB-46-PENDING-2 for the completed result being available. The builder stores the scanner's `score` and `recommendation` verbatim (FR-089, FR-154) and normalizes only the finding order (FR-155); no field is synthesized. The order is severity rank (critical, high, medium, low), then file, then line, then rule, so two identical scanner reports always render identically. A failed scan has no partial score: the report says it failed, which prevents a reader from treating an incomplete scan as a low score. The `—` placeholder is a literal em dash.

---

## STORY: BSB-46-PENDING-6

**Title:** Match the platform's verdict for the same content and scanner version
**Epic:** BSB-46 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the builder's scan result to be the platform's own result for the same bundle and pinned scanner version**, so that **a scan that passes here will not be blocked when the skill reaches the platform**.

### Acceptance Criteria
Scenario: The builder stores the platform scanner's result unchanged for the conformance corpus
Given the six completed cases `test/saraav/static-clean`, `test/saraav/static-dni`, `test/saraav/static-critical`, `test/saraav/static-partial`, `test/saraav/static-accepted` and `test/saraav/static-accepted-pass`, and for each case the platform oracle runs the pinned scanner image `sha256:5d3a9f1c7b2e4a6d8f0b1c3e5a7d9f2b4c6e8a0d1f3b5c7e9a2d4f6b8c0e1a3f` directly on the same bundle
When each case is scanned through the builder's skill-page trigger and the run gate
Then for each case the `static_scans` row's `verdict`, `score`, `recommendation`, `coverage` and `findings` equal the platform oracle report's values after both are put in the preface's finding order, and both the builder and the oracle report `scanner_version` `1.4.0`

Scenario: A report from a different scanner version is rejected rather than compared
Given `skill-builder/kit.txt` is `kit-v8` and its `kit.json` has `bheembhai_skillscan_version` `1.4.1`, but the fixture scanner for `test/saraav/static-clean` writes a report whose `scanner_version` is `1.4.0`
When Alice starts a run with `skills_branch` `test/saraav/static-clean`
Then the builder responds with HTTP 503 and a JSON body whose `error` is `static_scan_failed` and whose `reason` is `scanner_error`; the `static_scans` row has `state` `failed` and `failure_reason` `scanner_error`; no run is created; and no report from that scan is labelled as a 1.4.1 platform result

Scenario: A scanner image given by tag is refused before a scan starts
Given `skill-builder/kit.txt` is `kit-v7`, but its `kit.json` sets `scanner_image` to `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan:1.4.0` and omits `scanner_image_digest`
When Alice starts a run or submits a skill-page scan
Then the builder responds with HTTP 503 and body exactly `{"error":"scanner_image_not_pinned"}`, the `static_scans` table gains no row, `BB_SCAN_LOG` is empty, and the `runs` table gains no row

### Covered requirements (traceability)
- FR-091

### Out of scope
Changing the platform's scanner or its ADR-034 rules; comparing runs of different scanner versions; a model-based verdict (FA-12 / BSB-47); catalog CI's own SARIF upload; the platform's import flow and its re-scan.

### Notes / dependencies
Depends on BSB-46-PENDING-1 for the classifier and BSB-46-PENDING-5 for the report fields. The builder and the platform share one pinned scanner image (`bheembhai-skillscan` `1.4.0`, digest from `kit.json`), and the builder stores the scanner's fields rather than recomputing them, so FR-091's "same verdict for the same content and scanner version" is a property of the stored result, not a coincidence of two implementations. The platform oracle in the test is the same image invoked directly, which is the platform's ADR-034 behaviour; the builder's stricter `passes` decision (critical finding, incomplete coverage) is this epic's FR-078 through FR-081 and does not rewrite `verdict`. The digest pin is what makes the comparison meaningful: a tag could move the scanner under the same version string, so a tagged image is refused before a scan row exists.

---

## STORY: BSB-46-PENDING-7

**Title:** Start a static-only scan from the skill page without a run
**Epic:** BSB-46 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **to run a static-only scan from a project's skill page without creating a run**, so that **I can check the security findings before spending a run or a model call**.

### Acceptance Criteria
Scenario: A project member starts a static-only scan from the skill page
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie, `test/saraav/static-dni` is at commit `b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1`, `static_scans` has no row for the project with `skills_ref` `test/saraav/static-dni`, `BB_SCAN_LOG` is empty, and the fixture model endpoint records zero requests
When Alice opens `GET /projects/prj_H5mQ2rT8vX/skills/sdlc-research-summarise`, selects `test/saraav/static-dni`, and submits `POST /api/projects/prj_H5mQ2rT8vX/skills/sdlc-research-summarise/scans` with body `{"skills_ref":"test/saraav/static-dni"}`
Then the builder responds with HTTP 202 and a JSON body whose `scan_id` matches `^scan_[0-9A-Za-z]{10}$`, whose `state` is `running`, whose `reused` is false, whose `project_id` is `prj_H5mQ2rT8vX`, whose `skill` is `sdlc-research-summarise`, whose `skills_ref` is `test/saraav/static-dni`, whose `skills_commit_sha` is `b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1` and whose `content_sha256` matches `^[0-9a-f]{64}$`; after the scanner finishes, `GET /api/scans/{scan_id}` has `state` `completed`, `verdict` `DO_NOT_INSTALL`, `score` 25 and `recommendation` `Do not install`; the `runs` table has no row for `project_id` `prj_H5mQ2rT8vX`; no branch matching `skilltest/*` exists; the fixture model endpoint recorded zero requests; and `BB_SCAN_LOG` contains exactly one line

Scenario: The skill page offers the scan entry point and the latest result
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and a completed scan `S` exists for the project and `sdlc-research-summarise`
When Alice opens `GET /projects/prj_H5mQ2rT8vX/skills/sdlc-research-summarise`
Then the builder responds with HTTP 200 and HTML containing an element with `data-testid="skill-security"`, a `select` with `data-testid="skills-ref"` whose options include `main` and `test/saraav/static-clean`, a `button` with `data-testid="static-scan-start"` whose text is exactly `Security check`, and an `a` with `data-testid="scan-link"` whose `href` is exactly `/scans/S`

Scenario: A skill page with no scans shows the empty state
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and `static_scans` has no row for the project and `sdlc-research-summarise`
When Alice opens `GET /projects/prj_H5mQ2rT8vX/skills/sdlc-research-summarise`
Then the builder responds with HTTP 200 and HTML containing `data-testid="no-scan"` with text exactly `No security scan yet` and an enabled `data-testid="static-scan-start"` button, and the HTML contains no `data-testid="scan-link"` element

Scenario: A non-member cannot start or read a scan from the skill page
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `builder_session` cookie, the `project_members` table has no row for `prj_H5mQ2rT8vX` and `U_bob`, and `BB_SCAN_LOG` is empty
When Bob opens `GET /projects/prj_H5mQ2rT8vX/skills/sdlc-research-summarise` and submits `POST /api/projects/prj_H5mQ2rT8vX/skills/sdlc-research-summarise/scans` with body `{"skills_ref":"test/saraav/static-clean"}`
Then the page responds with HTTP 403 and a body containing `You are not a member of this test project`, the POST responds with HTTP 403 and body exactly `{"error":"project_membership_required"}`, the `static_scans` table gains no row for `project_id` `prj_H5mQ2rT8vX`, and `BB_SCAN_LOG` is empty

Scenario: A request with no session is rejected
Given no `builder_session` cookie
When the visitor submits `POST /api/projects/prj_H5mQ2rT8vX/skills/sdlc-research-summarise/scans` with body `{"skills_ref":"test/saraav/static-clean"}`
Then the builder responds with HTTP 401 and body exactly `{"error":"authentication_required"}`, the `static_scans` table gains no row for `project_id` `prj_H5mQ2rT8vX`, and `BB_SCAN_LOG` is empty

Scenario: An unknown skills ref is rejected before scanning
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and `bheembhai-skills` has no branch `test/saraav/missing`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/skills/sdlc-research-summarise/scans` with body `{"skills_ref":"test/saraav/missing"}`
Then the builder responds with HTTP 404 and body exactly `{"error":"skills_branch_not_found","branch":"test/saraav/missing"}`, the `static_scans` table gains no row for `project_id` `prj_H5mQ2rT8vX`, and `BB_SCAN_LOG` is empty

Scenario: A skill absent from the resolved commit is rejected before scanning
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and `skills/sdlc-missing-skill/` does not exist at `test/saraav/static-clean` commit `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/skills/sdlc-missing-skill/scans` with body `{"skills_ref":"test/saraav/static-clean"}`
Then the builder responds with HTTP 404 and body exactly `{"error":"skill_not_found","skill":"sdlc-missing-skill"}`, the `static_scans` table gains no row for `project_id` `prj_H5mQ2rT8vX`, and `BB_SCAN_LOG` is empty

### Covered requirements (traceability)
- FR-092

### Out of scope
The LLM or full security scan and its model selection (FA-12 / BSB-47, FR-093, FR-163); the CLI static-only scan (FA-16 / BSB-55, FR-117); a project skill copy or editing a skill from this page; fixing findings; starting a run from the skill page; the scan history for a skill beyond the latest result.

### Notes / dependencies
Depends on FA-4 (BSB-43) for `projects` and `project_members`; on FA-6 (BSB-45) for the catalog repository, the packer, `skill_bundles` and the `bundle_sha256`; and on BSB-46-PENDING-1 and BSB-46-PENDING-2 for the scan row and its reuse. The page is a project-scoped scan page, not a second copy of the skill: the content is always read from `bheembhai-skills` at the selected ref, and the project supplies membership only. It deliberately needs no project integration, which is why a project with no `github` or `ai_model` row can still use it. The trigger is asynchronous so a scan with the ten-minute deadline cannot hold an HTTP request open; the page polls `GET /api/scans/{scan_id}`. A `skills_ref` may be `main`, a `test/` branch or a `build/` branch; this story does not require it to be a build branch. The model endpoint's zero requests prove the static stage spends no model tokens and that the LLM stage is not queued here.

---

## STORY: BSB-46-PENDING-8

**Title:** Run the static scan with no network access
**Epic:** BSB-46 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **platform administrator**, I want **every static scan to run in a container with no network access**, so that **scanning untrusted skill content cannot exfiltrate data, reach internal services or call a model**.

### Acceptance Criteria
Scenario: A static scan has no network route, DNS or cloud metadata access
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, a static scan runs for `test/saraav/static-clean`, and the fixture scanner attempts a TCP connection to `1.1.1.1:443`, a DNS lookup of `example.com` and an HTTP GET of `http://169.254.169.254/latest/meta-data/`
When the scan completes
Then every probe fails, the scanner report's `network_probe` is exactly `blocked`, its `network_attempts` equals exactly `[{"target":"1.1.1.1:443","error":"unreachable"},{"target":"example.com:443","error":"dns_failed"},{"target":"169.254.169.254:80","error":"unreachable"}]`, the `static_scans.report.network_probe` is exactly `blocked`, and the scan is `completed` with `passes` true

Scenario: The scanner cannot reach a listener on the host
Given a TCP listener on the host at `127.0.0.1:9090` that records every accepted connection, a static scan runs for `test/saraav/static-clean`, and the fixture scanner attempts an HTTP GET of `http://127.0.0.1:9090/`
When the scan completes
Then the listener recorded zero connections, the scanner report's `network_attempts` equals exactly `[{"target":"127.0.0.1:9090","error":"unreachable"}]`, and the scan is `completed` with `passes` true

Scenario: Both scan entry points start the scanner with network access disabled
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, `BB_SCAN_LOG` is empty, and Alice starts one run-triggered scan for `test/saraav/static-clean` and one skill-page scan for `test/saraav/static-dni`
When both scans complete
Then `BB_SCAN_LOG` contains exactly two lines, each ending with `network=none`, and both `static_scans` rows have `state` `completed`

Scenario: A scan cannot alter the bundle it grades
Given a static scan runs for `test/saraav/static-clean` with `content_sha256` `B`, the bundle is mounted read-only, and the fixture scanner attempts to append `tampered` to `/work/bundle/skills/sdlc-research-summarise/SKILL.md`
When the scan completes
Then the write fails with `EROFS`, the object at `s3://builder-test/bundles/B.tar.zst` still hashes to `B`, the `skill_bundles` row with `bundle_sha256` `B` is unchanged, and the scan is `completed` with `passes` true

### Covered requirements (traceability)
- NFR-005

### Out of scope
The LLM stage's restricted network access to the model endpoint (FA-12 / BSB-47, FR-084); the scanner image's own build and vulnerability patching (external prerequisite); the host's firewall and egress policy; scanning on a developer machine; the scanner's MCP server mode, which is never used.

### Notes / dependencies
Depends on BSB-46-PENDING-1 for the scan runner and BSB-46-PENDING-7 for the second entry point. The scanner container is started with its network namespace disabled (`--network none`) and the bundle mounted read-only; the application process never parses skill content, so untrusted content has no path to the builder's network or credentials. The probe results are recorded in the raw scanner report, which makes NFR-005 observable from the durable scan record rather than only from the container configuration. The host listener case is the stronger assertion: a container with only loopback still cannot reach a host service, so a skill cannot use the scanner to call a model or an internal API. The read-only bundle case protects the exact-content guarantee the rest of the epic relies on.

---

## Coverage check

Every requirement in BSB-46's `epic-map.json` entry appears above:

- FR-076 — BSB-46-PENDING-1
- FR-077 — BSB-46-PENDING-2
- FR-078 — BSB-46-PENDING-1
- FR-079 — BSB-46-PENDING-1
- FR-080 — BSB-46-PENDING-1
- FR-081 — BSB-46-PENDING-3
- FR-087 — BSB-46-PENDING-4
- FR-088 — BSB-46-PENDING-4
- FR-089 — BSB-46-PENDING-5
- FR-091 — BSB-46-PENDING-6
- FR-092 — BSB-46-PENDING-7
- FR-154 — BSB-46-PENDING-5
- FR-155 — BSB-46-PENDING-5
- NFR-005 — BSB-46-PENDING-8
