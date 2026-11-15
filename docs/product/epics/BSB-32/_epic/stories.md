# Stories — BSB-32 (LLM security scanning)

Source: Jira epic **BSB-32** — *LLM security scanning* (feature area FA-12, release MVP,
labels FA-12, MVP), fetched read-only from the Atlassian project `bheembhai-skill-builder`; its
summary, description, functional scope, goal, stated edge cases and covered-requirement list are
the same as the BSB-32 section of `docs/product/epics.md`. The requirement IDs mapped to the epic
are in `docs/product/epic-map.json`.

Epic BSB-32 covers 10 requirements. They decompose into the 6 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-32`), is epic
**BSB-32**. The Atlassian MCP entry in `.mcp.json` is not usable in this session: its `args` value
is a string where Claude Code requires an array, so no Jira MCP tools were offered and the epic was
fetched read-only through the Atlassian REST API with the same credentials. Nothing was written to
Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-082 | BSB-32-PENDING-1 |
| FR-083 | BSB-32-PENDING-2 |
| FR-084 | BSB-32-PENDING-2 |
| FR-085 | BSB-32-PENDING-3 |
| FR-086 | BSB-32-PENDING-5 |
| FR-090 | BSB-32-PENDING-5 |
| FR-093 | BSB-32-PENDING-6 |
| FR-139 | BSB-32-PENDING-4, BSB-32-PENDING-6 |
| FR-156 | BSB-32-PENDING-5 |
| FR-163 | BSB-32-PENDING-6 |

The epic's four stated edge cases are covered explicitly: a static failure means no LLM scan is
triggered (BSB-32-PENDING-1 and BSB-32-PENDING-6), an unavailable scan still lets readiness
proceed (BSB-32-PENDING-4), a project without a configured LLM model profile surfaces
unavailability rather than falling back silently (BSB-32-PENDING-4 and BSB-32-PENDING-6), and the
LLM scan never blocks a run (BSB-32-PENDING-3). The epic's non-goals are respected: there is no
blocking gate, no per-run model override, and no model other than the project's configured
LLM-scan profile.

## LLM scan contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control and object-store
fixture unless it says otherwise. The member session, the local `users` rows and the
`skill-builders` gate are established by epic BSB-18. The project, `projects` rows,
`project_members` rows and project membership checks are established by epic BSB-22. The
`ai_model` integration, its profiles and its secret reference are established by epic BSB-23. The
build, its branch and `head_sha` are epic BSB-21's; the build-creation shapes are epic BSB-20's.
The bundle, skills-commit resolution, run branch and baseline are epic BSB-25's (FR-038 to
FR-043). The run row and its `queued` start state are epic BSB-24's; run terminal states are
epics BSB-26 and BSB-27's. The static scan, its `static_scans` row, its verdict and its report
API are epic BSB-31's (FR-076 to FR-081, FR-087 to FR-089, FR-091, FR-092, FR-154, FR-155).
`builds`, `runs` and `skill_bundles` columns follow `docs/adr/SK-001-skill-builder.md` §1a, §5 and
§9; the scanner image and `bheembhai-skillscan` package follow §2 and §6b.

This epic adds one table, `llm_scans`, and two additive columns to tables other epics own:
`static_scans.llm_stage` (epic BSB-31's table) and `projects.llm_scan_model_profile_id` plus
`projects.llm_scan_tier` (epic BSB-22's table). All are additive; no existing column changes
meaning and no existing epic's scenarios change.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z` |
| Current time | `2026-11-15T10:10:00Z` unless a scenario sets a clock |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing` |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42`; id `8` has `name` = `Search smoke`, `owner_id` = `43`; ids `1` to `6`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)`; Alan has no row for project `7` or `8` |
| Project `7` LLM-scan setting | `projects.llm_scan_model_profile_id` = `3`, `projects.llm_scan_tier` = `medium` |
| Project `8` LLM-scan setting | `projects.llm_scan_model_profile_id` = `NULL`, `projects.llm_scan_tier` = `NULL` |
| `ai_model` integration (project 7) | row `id` = `7`, `project_id` = `7`, `kind` = `ai_model`, `config` = `{"profiles":[{"id":3,"name":"Anthropic test","vendor":"anthropic","base_url":"https://api.anthropic.test","tiers":{"high":"test-model-high","medium":"test-model-medium"}},{"id":4,"name":"Smoke","vendor":"anthropic","base_url":"https://api.anthropic.test","tiers":{"medium":"test-model-medium"}}]}`, `secret_ref` = `skill-builder/7/ai_model`, `verified_at` = `2026-11-14T09:03:00Z` |
| `ai_model` integration (project 8) | none |
| Model secret | the secret held at `skill-builder/7/ai_model` has exactly the value `sk-ant-test-5f2c8e1d` |
| Resolved LLM-scan model for project `7` | integration `7`, profile `3`, tier `medium`, vendor `anthropic`, base URL `https://api.anthropic.test`, model `test-model-medium` |
| Model stub | `https://api.anthropic.test` records every request, its `Authorization` header, method, path and body |
| Build `7` | `kind` = `edit`, `skill` = `sdlc-fix-bug-triage`, `branch` = `build/sdlc-fix-bug-triage`, `created_by` = `42`, `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `NULL`, `state` = `open` |
| Build `9` | `kind` = `create`, `skill` = `sdlc-fix-bug-triage`, `branch` = `build/sdlc-fix-bug-triage-2`, `created_by` = `43`, `head_sha` = `5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b`, `ready_sha` = `NULL`, `state` = `open` |
| Build `7` bundle content | `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` |
| Build `9` bundle content | `0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d` |
| Run `11` | `kind` = `run`, `project_id` = `7`, `user_id` = `42`, `skill` = `sdlc-fix-bug-triage`, `skills_ref` = `build/sdlc-fix-bug-triage`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `input_branch` = `main`, `state` = `queued`, `run_branch` = `NULL`, `claimed_verdict` = `NULL`, `final_verdict` = `NULL`, `verification` = `NULL`; its bundle content is the build `7` content |
| Run `12` | `kind` = `run`, `project_id` = `8`, `user_id` = `43`, `skill` = `sdlc-fix-bug-triage`, `skills_ref` = `build/sdlc-fix-bug-triage-2`, `skills_commit_sha` = `5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b`, `input_branch` = `main`, `state` = `queued`, `run_branch` = `NULL`, `claimed_verdict` = `NULL`, `final_verdict` = `NULL`, `verification` = `NULL`; its bundle content is the build `9` content |
| `runs` fixture state | rows with ids `1` to `9` are other fixture runs, there is no run `10`, run `11` is the project-7 row above and run `12` is the project-8 row above; `SELECT count(*) FROM runs` is `11` |
| Catalog repository | `saraavrnd/bheembhai-skills` |
| Skill | `sdlc-fix-bug-triage`, folder `skills/sdlc-fix-bug-triage/` |
| Object-store bucket | `skill-builder-runs` |
| Kit pin | `skill-builder/kit.txt` contains exactly `kit-v8` |
| `kit.json` for `kit-v8` | `{"kit":"kit-v8","env_contract_version":"4","bheembhai-stepkit":"0.5.0","bheembhai-verify":"2.2.0","bheembhai-skillscan":"1.6.0","agent_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-agent@sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13","scanner_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d"}` |
| Scanner image | `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d`, always pulled by digest and never by tag |
| Scanner package version | `bheembhai-skillscan` `1.6.0` |
| LLM scan API | `POST https://builder.skillbuilder.internal/api/projects/{project_id}/scans` |
| LLM report API | `GET https://builder.skillbuilder.internal/api/llm-scans/{llm_scan_id}` |
| Success statuses | HTTP 202 with `Content-Type: application/json` for an accepted scan start; HTTP 200 with `Content-Type: application/json` for a report read |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |

**Static scan fixtures reused from epic BSB-31.** The base fixture contains these `static_scans`
rows, all with `skill` = `sdlc-fix-bug-triage`, `image_digest` = the scanner image digest above
and `scanner_version` = `1.6.0`. The main content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
has static scan `12` `completed` `passed`; it is the content of build `7` and run `11`. The
project-8 content `0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d`
has static scan `19` `completed` `passed`; it is the content of build `9` and run `12`. A
scenario that needs another static outcome seeds it and says so. A scenario that starts from a
cold cache states that the base fixture's scan rows for its content are absent; that Given
overrides the base fixture for that content.

**`llm_scans` — the LLM scan record.**

| Column | Type and value |
|--------|----------------|
| `id` | bigint identity primary key |
| `project_id` | bigint NOT NULL; the project whose LLM-scan setting was used |
| `run_id` | bigint NULL; the `runs.id` of the first request when the scan came from run preparation, otherwise `NULL` |
| `build_id` | bigint NULL; the `builds.id` of the first request when the scan came from a full scan, otherwise `NULL` |
| `skill` | text; the skill folder name |
| `skills_commit_sha` | char(40) lowercase hex |
| `content_sha` | char(64) lowercase hex; the SHA-256 of the exact bundle tar.gz, equal to `skill_bundles.bundle_sha256` |
| `image_digest` | text; the `scanner_image` reference from `kit.json`, including `@sha256:` |
| `scanner_version` | text NULL; the `bheembhai-skillscan` version the report states |
| `model_integration_id` | bigint NULL; the project's `integrations.id` of kind `ai_model` |
| `model_profile_id` | smallint NULL; the profile id inside that integration's `config.profiles` |
| `model_tier` | text NULL; `high`, `medium` or `low` |
| `vendor` | text NULL; the profile's `vendor` |
| `base_url` | text NULL; the profile's `base_url` |
| `model` | text NULL; the model the profile's tier mapping resolves to |
| `state` | one of `queued`, `running`, `complete` or `unavailable` |
| `findings` | JSONB NOT NULL default `[]`; each entry has exactly the keys `severity`, `rule`, `file`, `line` |
| `error` | text NULL; on `unavailable` one of `llm_model_profile_missing`, `llm_model_profile_invalid`, `llm_model_key_unavailable`, `llm_endpoint_unreachable`, `llm_scanner_failed`, `llm_report_invalid` or `llm_scan_timeout` |
| `created_at` | timestamptz |
| `started_at` | timestamptz NULL |
| `finished_at` | timestamptz NULL |

`CREATE UNIQUE INDEX llm_scans_live_or_complete ON llm_scans
(content_sha, image_digest, model_integration_id, model_profile_id, model_tier)
WHERE state = 'queued' OR state = 'running' OR state = 'complete';` — at most one live or
complete scan per content, scanner image and model setting. Any number of `unavailable` rows may
exist for the same key, so an unconfigured project, a missing key or a failed model call can be
retried after it is fixed.

A scan row is content-addressed: the first request for a key records its `run_id` or `build_id`,
its `project_id` and its `model_*` values; a later request for the same key reuses that row and
does not rewrite those columns.

**The project's LLM-scan setting (FR-163).** `projects.llm_scan_model_profile_id` and
`projects.llm_scan_tier` name a profile in the project's single `ai_model` integration and one
of its tier keys. The scan resolves `model_integration_id`, `model_profile_id`, `model_tier`,
`vendor`, `base_url` and `model` from that setting and the integration's `config.profiles`. The
integration's `secret_ref` names the secret fetched at container start. There is no installation
default, no run-level override and no fallback model: a project with no setting, or a setting that
names a missing profile or an unmapped tier, is recorded `unavailable` with
`llm_model_profile_missing` or `llm_model_profile_invalid` and no container starts.

**The trigger (FR-082).** `ensure_llm_scan(content_sha, skill, skills_commit_sha, project_id,
run_id=None, build_id=None)` is this epic's service. It first reads
`readiness_scan_outcome(content_sha, 'static')`; unless that returns `passed`, it returns `NULL`
and writes no row. Otherwise it resolves the project's LLM-scan setting and either reuses the
live or complete row for the key or inserts a `queued` row and enqueues the scan. If resolution
fails (no setting, invalid profile, unmapped tier, missing secret), it inserts an `unavailable`
row instead and returns after writing it. The insert or reuse is one transaction; a concurrent
duplicate is caught by `llm_scans_live_or_complete` and the existing row is returned. The service
never waits for a scan to finish.

- **Run preparation (epic BSB-25).** After `ensure_static_scan(bundle)` returns `passed`,
  BSB-25 calls `ensure_llm_scan` with the run's `project_id` and `run_id` and then continues to
  create the run branch, baseline and agent container. It does not read the LLM row's state.
- **Full scan (FR-093).** A `kind` = `full` request sets `static_scans.llm_stage` = `true` on the
  static row it starts or reuses. The scan worker reads `llm_stage` from that row when it writes
  the terminal state. When the static row completes with `verdict` `passed` and `llm_stage`
  `true`, the worker calls `ensure_llm_scan` with the request's `project_id` and `build_id`. When
  the static row completes with `verdict` `failed`, no LLM row is written. When the static row is
  already terminal `passed` at request time, the route calls `ensure_llm_scan` before responding.
- **Static-only (epic BSB-31's `kind` = `static`, the CLI `--static-only`, CI).** Never calls
  `ensure_llm_scan`; a row created by a static-only request has `static_scans.llm_stage` =
  `false`. Reusing a static row whose `llm_stage` is already `true` from an earlier full request
  does not start a second LLM scan; the earlier request owns the LLM stage.
- **No scan on save.** Saving a build or a file never calls `ensure_llm_scan`.

**The scanner invocation.** For scan `51` of the main bundle the builder starts exactly:

```
docker run --rm --network bb-llm-scan --read-only --tmpfs /tmp --label bb.scan_id=51
  --mount type=bind,src=/var/lib/skill-builder/bundles/b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a.tar.gz,dst=/scan/bundle.tar.gz,readonly
  --mount type=bind,src=/var/lib/skill-builder/scans/51,dst=/scan/out
  -e HOME=/tmp
  -e BB_SCAN_MODEL_KEY=sk-ant-test-5f2c8e1d
  123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d
  bheembhai-skillscan scan --stage llm --bundle /scan/bundle.tar.gz --skill sdlc-fix-bug-triage --vendor anthropic --model test-model-medium --endpoint https://api.anthropic.test --out /scan/out/report.json
```

For another scan the label is that scan's id, the host paths are that scan's verified bundle
object and its own output directory, the image is the digest pinned in `kit.json`, and the
`--vendor`, `--model` and `--endpoint` values are that scan's resolved `vendor`, `model` and
`base_url`. The container environment contains exactly `HOME=/tmp` and `BB_SCAN_MODEL_KEY=<the
secret value>`; it contains no `JIRA`, `GITHUB`, `AWS`, `BB_RUN_`, `BB_SKILL_` or `BB_STEPKIT`
variable and no secret reference. The container is labelled `bb.scan_id` and never `bb.run_id`.
The bundle is mounted read-only; only `/scan/out` is writable. The app process only starts the
container and parses the report; it never runs scanner code or calls the model itself. The exact
CLI flags are an adapter decision: if the pinned package's flags differ, only the invocation
changes.

**The network policy.** The container runs on the Docker network `bb-llm-scan`, whose egress
allow-list contains exactly the resolved base URL's host and port (`api.anthropic.test:443` for
the fixture). No other destination, protocol or DNS name is reachable; the static stage's
`--network none` and the run's agent network are not reused. The model key is passed as env only
and is never written to disk, logged, or stored in a builder record.

**The scanner report the adapter normalizes and validates.** The LLM report file is a JSON object
with exactly these required keys (unknown extra keys are ignored):

```
{"scanner_version":"1.6.0","vendor":"anthropic","model":"test-model-medium","findings":[]}
```

Each `findings` entry has the required keys `severity` (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW` or
`INFO`), `rule` (non-empty string), `file` (non-empty path relative to the bundle root), `line`
(integer at least 1), `message` (string) and `accepted` (boolean); `accepted_reason` is a
non-empty string when `accepted` is true and `null` otherwise. A report is valid only when
`scanner_version` equals the pinned `1.6.0`, `vendor` and `model` equal the values the builder
passed, and every finding satisfies the rules above. The stored finding has exactly the four keys
`severity`, `rule`, `file` and `line`; `message`, `accepted` and `accepted_reason` are validated
then not stored.

A report whose `vendor` or `model` differs from the requested values, whose
`scanner_version` differs, or whose findings are malformed records `state` = `unavailable`,
`error` = `llm_report_invalid`, `findings` = `[]`, `scanner_version` = `NULL` and `finished_at`.
A scanner exit that cannot connect to the configured endpoint records the same shape with
`error` = `llm_endpoint_unreachable`; any other non-zero exit records `error` =
`llm_scanner_failed`. A scanner still running at 600 seconds is killed and records `error` =
`llm_scan_timeout` with `finished_at` = `started_at` + 600 seconds. A missing or unreadable
secret records `error` = `llm_model_key_unavailable` and starts no container.

**The readiness read interface.** Epics BSB-30 and BSB-27 consume the LLM outcome through
`readiness_scan_outcome(content_sha, 'llm')`, which returns `complete`, `unavailable` or
`not_run`, and `readiness_scan_id(content_sha, 'llm')`, which returns the id of the row the
outcome came from or `NULL`. Both select, for the given `content_sha`, the latest terminal row
(`state` `complete` or `unavailable`) by `finished_at` then `id`. No terminal row — including when only a `queued` or `running` row exists — returns
`not_run` and `NULL`. The Ready condition for the LLM check is
`readiness_scan_outcome(content_sha, 'llm') IN ('complete', 'unavailable')`; `not_run` is not
satisfied. This is epic BSB-30's `llm_state` vocabulary, where a scan that cannot run is
`unavailable`, not absent.

**Report API.** `GET https://builder.skillbuilder.internal/api/llm-scans/{llm_scan_id}` returns
HTTP 200 with `Content-Type: application/json` and exactly these keys, in this order, for scan
`51`:

```
{"llm_scan_id":51,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a","state":"complete","model_integration_id":7,"model_profile_id":3,"model_tier":"medium","vendor":"anthropic","model":"test-model-medium","error":null,"scanner_version":"1.6.0","findings":[{"severity":"HIGH","rule":"SP-0090","file":"skills/sdlc-fix-bug-triage/templates/report.md","line":4},{"severity":"MEDIUM","rule":"SP-0117","file":"skills/sdlc-fix-bug-triage/references/run.md","line":8}]}
```

Findings are ordered by severity rank descending (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`),
then `file` ascending by plain byte comparison, then `line` ascending. Each finding object has
exactly the four keys `severity`, `rule`, `file` and `line`. When `state` is `unavailable`,
`error` is the stored code, `scanner_version` is `null` unless a valid report was read, and
`findings` is `[]`; the model fields are the resolved values when resolution succeeded and `null`
otherwise. When a scan is `queued` or `running`, `error` and `scanner_version` are `null` and
`findings` is `[]`. An unknown `llm_scan_id` is HTTP 404 with body exactly
`{"error":{"code":"not_found","message":"LLM scan not found"}}`. A signed-in user without current
`skill-builders` membership is rejected by epic BSB-18's gate with HTTP 403 and body exactly
`{"error":{"code":"not_a_member","message":"You are not a member of the skill-builders group"}}`.

**Build-page section.** Epic BSB-20's `GET https://builder.skillbuilder.internal/builds/{build_id}`
page gains one `<section id="llm-scan-report">` rendered for the build's current `head_sha`
bundle content. It shows the latest `llm_scans` row for that content by `created_at` then `id`,
regardless of state; with no row it shows the no-scan text below. The section contains:

| Element | `complete` | `queued` / `running` | `unavailable` | no scan |
|---|---|---|---|---|
| `<div id="llm-scan-model">` | `Model: test-model-medium` | `Model: test-model-medium` | `Model: Not scanned` | `Model: Not scanned` |
| `<div id="llm-scan-state">` | `LLM scan: Complete` | `LLM scan: Queued` / `LLM scan: Running` | `LLM scan: Unavailable` | `LLM scan: Not run` |
| `<div id="llm-scan-error">` | absent | absent | the exact `error` code | absent |
| `<table id="llm-scan-findings">` | one row per finding | the single row `No findings` | the single row `No findings` | the single row `No LLM scan` |

Each finding row has four cells whose text is the exact `severity`, `rule`, `file` and `line`.
A `complete` scan with no findings shows the single row `No findings`. The section is added by
this epic; epic BSB-20's other page regions are unchanged.

**Full-scan API (FR-093).** `POST https://builder.skillbuilder.internal/api/projects/{project_id}/scans`
with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"full"}`. It starts
or reuses the static scan through epic BSB-31's service and sets `llm_stage` = `true` on that
static row, adds the LLM stage through the trigger above, and returns HTTP 202 with
`Content-Type: application/json` and body exactly:

```
{"scan_id":21,"state":"queued","kind":"full","build_id":7,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a","llm_scan_id":null}
```

`scan_id` is the static scan's id and `state` is that static row's state. `llm_scan_id` is the
LLM row's id when one already exists for the content and project setting, otherwise `null`. A
`kind` = `static` request keeps epic BSB-31's exact response body and never adds `kind` or
`llm_scan_id`. Unknown request keys are ignored: a `model`, `model_profile_id` or `tier` value in
the body never overrides the project's LLM-scan setting. The request creates no `runs` row, no
catalog branch, no baseline and no agent container; only the scanner containers run.

Validation order on that route is fixed and shared with epic BSB-31: epic BSB-18's session gate
(401 `authentication_required`), its group gate (403 `not_a_member`), project resolution (404
`project_not_found`), project membership (403 `project_membership_required`), request-body
validation (422), then build resolution (404 `not_found`) and the scan start.

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| `project_id` `999` does not exist | 404 | `{"error":{"code":"project_not_found","message":"Project 999 does not exist."}}` |
| The caller is not a member of the project | 403 | `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}` |
| `build_id` is missing or is not a JSON integer | 422 | `{"error":{"code":"build_id_required","message":"A build_id is required."}}` |
| `kind` is present and is neither `static` nor `full` | 422 | `{"error":{"code":"kind_invalid","message":"Scan kind 'partial' is not supported."}}` |
| The `builds` row does not exist | 404 | `{"error":{"code":"not_found","message":"Build not found"}}` |

## Decisions recorded in this decomposition (confirm at review)

1. **LLM scan storage.** ADR §9 names no scan table; epic BSB-31 added `static_scans`. This
   decomposition adds `llm_scans`, content-addressed by the bundle SHA-256, the scanner image
   digest and the model setting. A JSONB column on `static_scans` or `runs` would duplicate a
   result per requester and lose reuse, so the scan is its own row. If review prefers another
   store, the states, trigger rule and read interface do not change.
2. **Terminal states.** `llm_scans.state` has `queued`, `running`, `complete` and `unavailable`.
   There is no `failed` terminal state for the LLM stage: FR-139 records a scan that cannot run as
   `unavailable`, and BSB-30's `llm_state` has exactly `complete`, `unavailable` and `not_run`.
   A started scan that errors, times out or returns an invalid report is `unavailable` with an
   error code; a scan is `complete` only when a valid report was read.
3. **Trigger ownership and the `llm_stage` marker.** `ensure_llm_scan` is called by BSB-25's run
   preparation after a passing static scan and by the full-scan worker after a passing static
   scan. `static_scans.llm_stage` (default `false`) is the additive marker that a full request
   asked for the LLM stage, so a worker that finishes the static scan knows whether to call the
   trigger. `kind` = `static`, the CLI `--static-only` and CI never set it and never call the
   trigger. If review prefers a separate full-scan record, only the marker moves.
4. **Reuse key includes the model and the scanner image.** The LLM result depends on the exact
   content, the scanner package and the model. A cached result is reused only when all three
   match; a kit update or a project model change therefore rescans unchanged content. An
   `unavailable` row is never reused, so a fixed profile or key can be retried.
5. **Project LLM-scan setting.** FR-163 says the default model lives on the test project. This
   decomposition adds `projects.llm_scan_model_profile_id` and `projects.llm_scan_tier`, resolved
   through the project's single `ai_model` integration (profile id and tier to model mapping).
   There is no installation default and no fallback. A missing setting, a missing profile or an
   unmapped tier is `unavailable`, never a silent default.
6. **Isolation.** The LLM stage runs in the pinned scanner image as a separate short-lived
   container, on a network whose only egress is the resolved model endpoint, with only the model
   key as a credential. The Docker flags and `bheembhai-skillscan` subcommand above are pinned by
   this decomposition; the properties the requirements need — by-digest image, read-only bundle,
   only the model endpoint reachable, only the model key, 10-minute limit — are asserted
   independently of the flags.
7. **Full-scan response shape.** A `kind` = `full` response returns the static scan id and,
   when it exists, the LLM scan id; `kind` = `static` keeps BSB-31's exact body. This avoids
   changing BSB-31's response contract while giving the full-scan caller one handle for the
   static stage and the optional LLM stage.
8. **Report display ownership.** This epic adds only `<section id="llm-scan-report">` to the
   build page and owns the LLM report API. The run page's Security tab and its rendering are
   epic BSB-33's (FR-157); this epic supplies the report and the model identity that page reads.
9. **Read authorization.** Any current `skill-builders` member may read an LLM report, matching
   BSB-31's static report rule. Project membership gates only the full-scan start (FR-093) and
   the run trigger uses the run's own project check.
10. **Timeout vocabulary.** Epic BSB-31 records a static timeout as `failed` because FR-088 says
    so. FR-139 gives the LLM stage no failed state, so a 600-second LLM timeout is recorded
    `unavailable` with `llm_scan_timeout`. A later request may retry it.

## Cross-epic notes

- **BSB-18 (session and group gate).** Every route and page region here sits behind BSB-18's
  session and `skill-builders` gates. A non-member never reaches scan resolution, storage or a
  report.
- **BSB-20 and BSB-21 (build page and build head).** This epic adds the `llm-scan-report` section
  and the `full-scan-start` control to BSB-20's `GET /builds/{build_id}` page and reads
  `builds.head_sha` and `builds.skill` from BSB-21's build record. BSB-21 must keep `head_sha`
  current on every save. No other BSB-20 page region changes.
- **BSB-22 (project membership and settings).** This epic adds two nullable columns,
  `projects.llm_scan_model_profile_id` and `projects.llm_scan_tier`, and reads BSB-22's project
  resolution and membership decision with its exact 404 `project_not_found` and 403
  `project_membership_required` bodies. It adds no membership rule of its own.
- **BSB-23 (integrations and secrets).** The scan reads one `ai_model` integration per project,
  its `config.profiles` and its `secret_ref`; it never writes an integration, a profile or a
  secret. BSB-23's decomposed stories must keep `vendor`, `base_url`, the profile id and the
  tier-to-model mapping as the fixture shows, and must keep the secret value out of builder
  records and logs (FR-032, FR-036, NFR-004).
- **BSB-24 (run start).** A run's `model_profile_id` and `tier` are the run's own choice and are
  unrelated to the project's LLM-scan setting. This epic never reads or overrides them.
- **BSB-25 (packaging and bundle).** After `ensure_static_scan(bundle)` returns `passed`, BSB-25
  must call `ensure_llm_scan(content_sha, skill, skills_commit_sha, run.project_id,
  run_id=run.id)` and continue immediately to create the run branch, baseline and agent
  container. It must not read `llm_scans.state`, must not wait for the scan and must not treat an
  unavailable row as a preparation failure. A run preparation that calls the trigger before the
  static result is `passed` is wrong.
- **BSB-26 (run execution and states).** The LLM outcome never changes a run's state, verdict,
  logs or cost. Any run-state vocabulary in the scenarios above (`queued`, `running`) is
  BSB-26's; this epic only requires that no LLM transition writes a run row.
- **BSB-27 (refusal and re-runs).** FR-055's refusal reads
  `readiness_scan_outcome(content_sha, 'static')` only. The LLM outcome is never consulted for a
  refusal, a re-run or chained input. A CRITICAL LLM finding is advice, not a block.
- **BSB-30 (readiness).** BSB-30 consumes `readiness_scan_outcome(content_sha, 'llm')` and
  `readiness_scan_id(content_sha, 'llm')` and sets `detail.llm_scan_id`. Its Ready rule already
  treats `complete` and `unavailable` as satisfied and `not_run` as unsatisfied; this epic
  supplies exactly those values. A queued or running scan is `not_run` until it is terminal. If
  two projects scan the same content with different models, both rows exist; the latest terminal
  row is the one the content-keyed readiness read names, and its report shows which model ran.
  Because every terminal LLM state permits Ready, that choice cannot make an unready build Ready.
- **BSB-31 (static scan).** This epic adds `static_scans.llm_stage` (boolean NOT NULL default
  `false`) and extends the `kind` of `POST /api/projects/{project_id}/scans` from `static` to
  `static` or `full`. BSB-31-PENDING-7's `kind_invalid` scenario must be narrowed to values other
  than `static` and `full`; the `full` case is this epic's, and the `kind` = `static` response
  body is unchanged. The LLM stage starts only after BSB-31's builder verdict is `passed`, never
  after a `DO_NOT_INSTALL`, critical-finding, incomplete-coverage or accepted-critical result.
- **BSB-33 (run report).** The run page's Security tab renders the LLM report this epic records
  and the model identity the report API returns. BSB-33 owns that page region; this epic owns the
  report API and the build page section.
- **BSB-34 (retention).** `llm_scans` rows and their findings are builder records; any retention,
  redaction or deletion rule for them is epic BSB-34's.
- **BSB-37 (CLI).** `python -m skill_builder.runner scan` (without `--static-only`) requests the
  same full scan and records the same `static_scans` and `llm_scans` rows through this epic's
  service; `--static-only` never does. The CLI itself is out of scope here.
- **BSB-38 (accessibility).** The `full-scan-start` control and the `llm-scan-report` section are
  new builder web surfaces; their WCAG 2.1 AA and 320-pixel reflow checks belong to epic BSB-38
  and add no requirement here.

---

## STORY: BSB-32-PENDING-1

**Summary:** Queue the LLM scan only after the static scan passes for the content
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **the builder to queue an advisory LLM security scan only for content whose static scan passed**, so that **the model-based review never runs on content the deterministic scan already rejected and always belongs to the content I am about to use**.

### Acceptance Criteria

#### Scenario: A passing static scan in run preparation queues one LLM scan
Given Ada is a current member of the `skill-builders` group and a member of project `7`
And run `11` is `queued` in project `7` for skill `sdlc-fix-bug-triage` at `skills_commit_sha` `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` with bundle content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And static scan `12` is `completed` with `verdict` `passed` for that content
And the base fixture has no `llm_scans` rows and the `llm_scans` identity sequence makes the next row id `51`
When BSB-25's preparation calls `ensure_llm_scan('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'sdlc-fix-bug-triage', '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b', 7, run_id => 11)` after that static result
Then it returns `51`
And `SELECT id, project_id, run_id, build_id, skill, skills_commit_sha, content_sha, image_digest, model_integration_id, model_profile_id, model_tier, vendor, base_url, model, state, findings, error FROM llm_scans WHERE id = 51` returns exactly `51 | 7 | 11 | NULL | sdlc-fix-bug-triage | 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b | b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a | 123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d | 7 | 3 | medium | anthropic | https://api.anthropic.test | test-model-medium | queued | [] | NULL`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'llm')` returns `not_run`
And no LLM scanner container has started when `ensure_llm_scan` returns

#### Scenario: A static scan that did not pass queues no LLM scan
Given static scan `13` is `completed` with `verdict` `failed` for content `c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5`
And no `llm_scans` row exists for that content
When `ensure_llm_scan('c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5', 'sdlc-fix-bug-triage', '7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f', 7, run_id => 12)` is called after that static result
Then it returns `NULL`
And `SELECT count(*) FROM llm_scans WHERE content_sha = 'c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5'` returns `0`
And `readiness_scan_outcome('c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5', 'llm')` returns `not_run`
And no LLM scanner container is started

#### Scenario: Content with no static result queues no LLM scan
Given no `static_scans` row exists for content `b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0`
When `ensure_llm_scan('b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0', 'sdlc-fix-bug-triage', '0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c', 7, run_id => 12)` is called
Then it returns `NULL`
And `SELECT count(*) FROM llm_scans WHERE content_sha = 'b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0'` returns `0`
And no LLM scanner container is started

#### Scenario: A static-only scan never queues an LLM scan
Given Ada is a member of project `7` and build `7`'s head content is `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And project `7` has LLM-scan profile `3` and tier `medium`
And no `static_scans` or `llm_scans` row exists for that content
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` carrying the `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"static"}`
Then the response is HTTP 202 with body exactly `{"scan_id":21,"state":"queued","build_id":7,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a"}`
When the scanner stub completes static scan `21` with `verdict` `passed`
Then `SELECT llm_stage, state, verdict FROM static_scans WHERE id = 21` returns exactly `false | completed | passed`
And `SELECT count(*) FROM llm_scans` returns `0`
And no LLM scanner container is started

#### Scenario: A completed LLM scan for the same content and model is reused
Given LLM scan `51` is `complete` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`, integration `7`, profile `3`, tier `medium` and model `test-model-medium`, with `build_id` `7` and `run_id` `NULL`
And static scan `12` is `completed` with `verdict` `passed` for that content
And the scanner stub records every container start
When `ensure_llm_scan('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'sdlc-fix-bug-triage', '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b', 7, run_id => 11)` is called
Then it returns `51`
And `SELECT count(*) FROM llm_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a'` returns `1`
And `SELECT run_id, build_id FROM llm_scans WHERE id = 51` returns exactly `NULL | 7`
And the scanner stub records no new LLM container start

### Covered requirements (traceability)
- FR-082

### Out of scope
The isolated container, its credential and its network policy (BSB-32-PENDING-2); a run's behaviour while the scan runs (BSB-32-PENDING-3); recording and displaying an unavailable scan (BSB-32-PENDING-4 and BSB-32-PENDING-5); starting a full scan from the build page (BSB-32-PENDING-6); the static scan itself, its cache and its verdict rule (epic BSB-31); packing the bundle and creating the run branch or baseline (epic BSB-25); changing the project's LLM-scan setting (epic BSB-23's integration surface); scans on save (the epic's non-goal).

### Notes / dependencies
- Depends on epic BSB-31 for `readiness_scan_outcome(content_sha, 'static')` and the
  `static_scans` row; on epic BSB-25 for the bundle, its `content_sha` and the call point after
  a passing static result; on epic BSB-24 for the `queued` run; on epic BSB-23 for the project's
  `ai_model` integration, profiles and secret reference; and on epic BSB-22 for the project and
  its LLM-scan setting columns.
- The trigger is deliberately a no-op unless the static outcome is `passed`; it reads the
  durable static result, not the caller's opinion. A caller cannot force an LLM scan for content
  whose static result is missing or failed.
- A static-only request (`kind` = `static`, `--static-only`, CI) does not call
  `ensure_llm_scan`. The static row it creates keeps `llm_stage` = `false`; the LLM stage is not
  part of a static-only scan.
- Reuse is keyed by content, scanner image and model setting. A project model change or a kit
  update creates a new key and therefore a new scan; the old row is kept.
- **Boundary for review — first requester.** The row records the first requester's `run_id` or
  `build_id` and `project_id`, as `static_scans` does. A later request that reuses the row keeps
  those values; the report's model identity still says which model produced the result, so a
  later reader is never told the wrong model ran.

---

## STORY: BSB-32-PENDING-2

**Summary:** Run the LLM scan with only the model key and model-endpoint network access
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-12, MVP

### Story
As a **security-conscious skill author**, I want **the LLM scan to run in an isolated scanner container that holds only the model key and can reach only the model endpoint**, so that **untrusted skill content cannot use the advisory scan to reach my Jira, source control or cloud credentials**.

### Acceptance Criteria

#### Scenario: Only the model key is injected into the LLM scanner container
Given static scan `12` is `completed` with `verdict` `passed` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And project `7` resolves LLM scan to integration `7`, profile `3`, tier `medium`, vendor `anthropic`, base URL `https://api.anthropic.test` and model `test-model-medium`
And the secret at `skill-builder/7/ai_model` has exactly the value `sk-ant-test-5f2c8e1d`
And LLM scan `51` is `queued`
When the LLM scan worker starts the scanner container for scan `51`
Then `docker inspect` reports `HOME=/tmp` and `BB_SCAN_MODEL_KEY=sk-ant-test-5f2c8e1d`, and `BB_SCAN_MODEL_KEY` is the only credential-bearing environment value
And no environment key matches `JIRA`, `GITHUB`, `AWS`, `BB_RUN_`, `BB_SKILL_` or `BB_STEPKIT`, and no environment value contains `skill-builder/7/ai_model`
And the builder-set labels include `bb.scan_id=51` and no `bb.run_id` label
And the bundle is mounted read-only at `/scan/bundle.tar.gz` and `/scan/out` is writable
And the container image is `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d`, pulled by digest

#### Scenario: The LLM scanner container can reach only the model endpoint
Given LLM scan `51` is `running` with base URL `https://api.anthropic.test`
When the container probes `https://api.anthropic.test/v1/messages` and the model stub answers HTTP 200
Then that probe succeeds through the model stub
And probes to `https://example.com`, `https://api.github.com`, `https://saraavrnd.atlassian.net`, `https://s3.eu-west-1.amazonaws.com` and `http://169.254.169.254/latest/meta-data` all fail without a connection
And `docker inspect` reports network `bb-llm-scan`, whose egress allow-list is exactly `api.anthropic.test:443`
And the container is not on the default `bridge` network and not on any run network

#### Scenario: The model key never reaches the builder's logs, disk or records
Given LLM scan `51` runs to `complete` using the secret value `sk-ant-test-5f2c8e1d`
When the builder has written its log and the scan log, and the scan row is stored
Then the builder log contains no occurrence of `sk-ant-test-5f2c8e1d`
And the scan log, which captures the container's stdout and stderr, contains no occurrence of `sk-ant-test-5f2c8e1d`
And no file the builder writes under `/var/lib/skill-builder` contains that value
And `SELECT * FROM llm_scans WHERE id = 51` has no cell equal to `sk-ant-test-5f2c8e1d`
And the builder process's environment after the container starts contains no `BB_SCAN_MODEL_KEY`

#### Scenario: The LLM stage runs in the pinned scanner image, never in the app process
Given LLM scan `51` is `queued` with static scan `12` passed
And the scanner stub records every container start and every model request
And the model stub answers the request with `{"scanner_version":"1.6.0","vendor":"anthropic","model":"test-model-medium","findings":[]}`
When the worker starts scan `51`
Then the container command contains `bheembhai-skillscan scan --stage llm` with `--bundle /scan/bundle.tar.gz`, `--skill sdlc-fix-bug-triage`, `--vendor anthropic`, `--model test-model-medium`, `--endpoint https://api.anthropic.test` and `--out /scan/out/report.json`
And the model stub records exactly one request, made while the scanner container is running
And the builder process opens no connection to `api.anthropic.test` and runs no in-process model client
And the container exits `0` and `SELECT state, scanner_version, findings FROM llm_scans WHERE id = 51` returns exactly `complete | 1.6.0 | []`

### Covered requirements (traceability)
- FR-083
- FR-084

### Out of scope
Which content may trigger a scan and when (BSB-32-PENDING-1); a run's behaviour while the scan runs (BSB-32-PENDING-3); the unavailable record and its error codes (BSB-32-PENDING-4); the report display (BSB-32-PENDING-5); the full-scan entry point (BSB-32-PENDING-6); how the `ai_model` integration, its profiles or its secret are configured (epic BSB-23); the scanner's internal rules and prompts (the pinned `bheembhai-skillscan` package); the static stage's `--network none` (epic BSB-31).

### Notes / dependencies
- Depends on epic BSB-23 for the `ai_model` integration's `vendor`, `base_url`, profile mapping
  and `secret_ref`; on epic BSB-31 for the passed static result; and on the pinned scanner image
  and package in `kit.json` (external prerequisite).
- FR-083 is about the scan container, not the builder: the builder's own IAM role fetches the
  secret reference at start, and the value is passed to the container as env only. NFR-004's
  no-log/no-record rule is epic BSB-23's; this story asserts the scan-specific consequence.
- FR-084 is enforced by the network policy, not by the scanner's behaviour: the allow-list is
  exactly the resolved base URL's host and port. If the profile's `base_url` changes, the
  allow-list changes for the next container; a running container never widens it.
- The scanner's MCP server mode is never used; the LLM stage is a one-shot CLI invocation.
- If the pinned package's flags differ, only the adapter changes; the environment, network,
  mount and label assertions above do not.

---

## STORY: BSB-32-PENDING-3

**Summary:** Never block, refuse or fail a run on the LLM scan
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **a run to start and finish without waiting for the LLM scan**, so that **model-based advice never delays or blocks my iteration loop**.

### Acceptance Criteria

#### Scenario: A run proceeds while its LLM scan is still running
Given static scan `12` is `completed` with `verdict` `passed` for run `11`'s bundle content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And `ensure_llm_scan` has created LLM scan `51` in `queued` for run `11`
And the scanner stub holds LLM scan `51` in `running` until released
When BSB-25's preparation continues after `ensure_llm_scan` returns
Then BSB-25 creates the run branch `skilltest/11` and records its baseline
And a Docker container labelled `bb.run_id=11` starts
And `SELECT state FROM runs WHERE id = 11` returns `running`
And `SELECT state FROM llm_scans WHERE id = 51` returns `running`
And the agent container starts while LLM scan `51` is still `running` and has not been read by BSB-25

#### Scenario: A CRITICAL LLM finding never refuses a run
Given run `11` is `running` with static scan `12` passed
And LLM scan `51` is `running` for run `11`'s content
When LLM scan `51` completes with one `CRITICAL` `SP-0042` finding
Then `SELECT state FROM llm_scans WHERE id = 51` returns exactly `complete`
And `SELECT findings FROM llm_scans WHERE id = 51` returns exactly `[{"severity":"CRITICAL","rule":"SP-0042","file":"skills/sdlc-fix-bug-triage/SKILL.md","line":17}]`
And `SELECT state, final_verdict FROM runs WHERE id = 11` returns exactly `running | NULL`
And the static refusal predicate for run `11` returns `passed`, so the run is not refused
And no `runs` row is written `failed`, `refused` or otherwise changed by the LLM scan

#### Scenario: An unavailable LLM scan never refuses or fails a run
Given run `11` is `running` with static scan `12` passed
And LLM scan `51` is `running` for run `11`'s content
When LLM scan `51` becomes `unavailable` with `error` `llm_endpoint_unreachable`
Then `SELECT state, final_verdict, verification FROM runs WHERE id = 11` returns exactly `running | NULL | NULL`
And `SELECT state, error FROM llm_scans WHERE id = 51` returns exactly `unavailable | llm_endpoint_unreachable`
And the run's agent container is still running and is not killed by the LLM outcome
And no refusal record and no run failure is written

#### Scenario: A run in a project without an LLM-scan profile still runs
Given run `14` is `queued` in project `8`, whose `llm_scan_model_profile_id` and `llm_scan_tier` are `NULL`
And static scan `19` is `completed` with `verdict` `passed` for run `14`'s bundle content `0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d`
And no `llm_scans` row exists for that content
And the `llm_scans` identity sequence makes the next row id `53`
And the scanner stub records every LLM container start
When BSB-25's preparation calls `ensure_llm_scan('0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d', 'sdlc-fix-bug-triage', '5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b', 8, run_id => 14) and continues
Then LLM scan `53` is written `unavailable` with `error` `llm_model_profile_missing`
And no LLM scanner container is started
And BSB-25 creates the run branch `skilltest/14` and records its baseline
And a Docker container labelled `bb.run_id=14` starts
And `SELECT state FROM runs WHERE id = 14` returns `running`

### Covered requirements (traceability)
- FR-085

### Out of scope
The trigger condition and reuse (BSB-32-PENDING-1); the isolation of the scan container (BSB-32-PENDING-2); recording and displaying the unavailable state in detail (BSB-32-PENDING-4 and BSB-32-PENDING-5); the full-scan entry point (BSB-32-PENDING-6); FR-055's static refusal and the run's own deadline or caps (epic BSB-27); the run's terminal outcome and verification (epics BSB-26 and BSB-29); deciding what a READY build requires (epic BSB-30).

### Notes / dependencies
- Depends on epic BSB-25 for calling the trigger after a passing static result and continuing
  without awaiting it; on epic BSB-31 for the static pass; on epic BSB-24 for the run row; and on
  epic BSB-23 for the project's model setting.
- FR-085 has two halves, both asserted: the run does not **wait** for the scan (the scan may still
  be `running` when the agent container starts) and the run is never **refused or failed** by the
  scan, whatever its findings or error.
- A CRITICAL LLM finding is stored and shown, but it is advice. Only the static stage can refuse a
  run, and that refusal is FR-055 in epic BSB-27.
- The trigger's unavailable write is synchronous and cheap; it is not a wait on a container. The
  run continues immediately in every branch.

---

## STORY: BSB-32-PENDING-4

**Summary:** Record an LLM scan that cannot run as unavailable
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **an LLM scan that cannot run to be recorded as unavailable rather than silently missing**, so that **I can see why there was no advisory review and readiness does not stall on a scan that never happened**.

### Acceptance Criteria

#### Scenario: A project without an LLM-scan profile records an unavailable scan
Given run `14` is `queued` in project `8`
And project `8` has `llm_scan_model_profile_id` `NULL` and `llm_scan_tier` `NULL` and no `ai_model` integration
And static scan `19` is `completed` with `verdict` `passed` for content `0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d`
And `readiness_scan_outcome('0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d', 'llm')` returns `not_run`
And the `llm_scans` identity sequence makes the next row id `53`
When `ensure_llm_scan('0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d', 'sdlc-fix-bug-triage', '5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b', 8, run_id => 14)` is called
Then it returns `53`
And `SELECT project_id, run_id, build_id, state, model_integration_id, model_profile_id, model_tier, vendor, base_url, model, error, findings, finished_at FROM llm_scans WHERE id = 53` returns exactly `8 | 14 | NULL | unavailable | NULL | NULL | NULL | NULL | NULL | NULL | llm_model_profile_missing | [] | 2026-11-15T10:10:00Z`
And `readiness_scan_outcome('0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d', 'llm')` returns `unavailable`
And `readiness_scan_id('0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d', 'llm')` returns `53`
And the Ready condition `readiness_scan_outcome(content_sha, 'llm') IN ('complete', 'unavailable')` is true
And no LLM scanner container is started

#### Scenario: A missing model key records unavailable
Given static scan `12` is `completed` with `verdict` `passed` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And project `7` resolves to integration `7`, profile `3`, tier `medium` and model `test-model-medium`
And no live or complete `llm_scans` row exists for that content, integration `7`, profile `3` and tier `medium`
And the secret at `skill-builder/7/ai_model` does not exist or cannot be read
And the `llm_scans` identity sequence makes the next row id `52`
When `ensure_llm_scan('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'sdlc-fix-bug-triage', '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b', 7, run_id => 11)` is called
Then `SELECT state, model_integration_id, model_profile_id, model_tier, vendor, base_url, model, error, findings FROM llm_scans WHERE id = 52` returns exactly `unavailable | 7 | 3 | medium | anthropic | https://api.anthropic.test | test-model-medium | llm_model_key_unavailable | []`
And no LLM scanner container is started
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'llm')` returns `unavailable`

#### Scenario: An unreachable model endpoint records unavailable
Given LLM scan `51` is `queued` with resolved base URL `https://api.anthropic.test`
And the model stub refuses every connection
When the worker starts the scanner container and the scanner exits non-zero because it cannot connect to the endpoint
Then `SELECT state, error, scanner_version, findings, finished_at FROM llm_scans WHERE id = 51` returns exactly `unavailable | llm_endpoint_unreachable | NULL | [] | 2026-11-15T10:10:00Z`
And `docker ps --filter label=bb.scan_id=51` lists no container
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'llm')` returns `unavailable`

#### Scenario: A malformed or mismatched report records unavailable
Given LLM scan `51` is `running` with requested vendor `anthropic` and model `test-model-medium`
When the scanner exits `0` and writes `{"scanner_version":"1.6.0","vendor":"anthropic","model":"other-model","findings":[{"severity":"HIGH","rule":"SP-0090","file":"skills/sdlc-fix-bug-triage/SKILL.md","line":4}]}` to `/scan/out/report.json`
Then `SELECT state, error, scanner_version, findings FROM llm_scans WHERE id = 51` returns exactly `unavailable | llm_report_invalid | NULL | []`
And no partial finding is stored and the model stub records no retry
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'llm')` returns `unavailable`

#### Scenario: A scan that exceeds the ten-minute limit records unavailable
Given LLM scan `51` is `running` with `started_at` = `2026-11-15T10:10:00Z`
And the scanner container does not exit
When 600 seconds have elapsed
Then the builder kills the container
And `SELECT state, error, scanner_version, findings, finished_at FROM llm_scans WHERE id = 51` returns exactly `unavailable | llm_scan_timeout | NULL | [] | 2026-11-15T10:20:00Z`
And `docker ps --filter label=bb.scan_id=51` lists no container
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'llm')` returns `unavailable`

### Covered requirements (traceability)
- FR-139

### Out of scope
Which content may trigger a scan and reuse (BSB-32-PENDING-1); the container's credential and network policy (BSB-32-PENDING-2); a run's behaviour while the scan is unavailable (BSB-32-PENDING-3); the report and error display (BSB-32-PENDING-5); starting a full scan from the build page (BSB-32-PENDING-6); the static scan's own timeout and failed record (epic BSB-31); configuring the project's profile, tier or secret (epic BSB-23); the readiness aggregate and the Ready rule (epic BSB-30); retrying a scan automatically (not required; a later request may retry).

### Notes / dependencies
- Depends on epic BSB-23 for the project's `ai_model` integration, profile mapping and secret
  reference; on epic BSB-31 for the passed static result; on epic BSB-30 for the `llm_state`
  vocabulary (`complete`, `unavailable`, `not_run`) and the Ready rule; and on the pinned scanner
  image and package.
- `unavailable` is a recorded terminal outcome, never an absent row. FR-139's point is that the
  author and readiness can tell "the scan could not run" from "no scan was requested"; the
  scenarios assert both `not_run` before and `unavailable` after.
- Every unavailable cause has its own `error` code so the author can act: configure a profile,
  fix a secret, restore the endpoint, or inspect the scanner. A malformed report stores no
  partial findings.
- The 600-second limit is the scanner container's limit from ADR §6b, measured from `started_at`;
  it is not the run's deadline (NFR-007/NFR-019, epic BSB-27).
- An unavailable row is not reusable: a later `ensure_llm_scan` for the same content and model
  creates a new row after the cause is fixed, while the unavailable row remains as history.

---

## STORY: BSB-32-PENDING-5

**Summary:** Show the LLM scan model and each finding's severity, rule, file and line
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **the LLM scan report to show which model ran the scan and each finding's severity, rule, file and line**, so that **I can judge and fix the model's security advice without guessing which model produced it or where the problem is**.

### Acceptance Criteria

#### Scenario: A completed report shows the model and every finding
Given LLM scan `51` is `complete` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` with `vendor` `anthropic`, `model_profile_id` `3`, `model_tier` `medium` and `model` `test-model-medium`
And its findings are a `HIGH` `SP-0090` finding at `skills/sdlc-fix-bug-triage/templates/report.md` line `4` and a `MEDIUM` `SP-0117` finding at `skills/sdlc-fix-bug-triage/references/run.md` line `8`
When Ada requests `GET https://builder.skillbuilder.internal/api/llm-scans/51` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: application/json` and body exactly `{"llm_scan_id":51,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a","state":"complete","model_integration_id":7,"model_profile_id":3,"model_tier":"medium","vendor":"anthropic","model":"test-model-medium","error":null,"scanner_version":"1.6.0","findings":[{"severity":"HIGH","rule":"SP-0090","file":"skills/sdlc-fix-bug-triage/templates/report.md","line":4},{"severity":"MEDIUM","rule":"SP-0117","file":"skills/sdlc-fix-bug-triage/references/run.md","line":8}]}`
And each finding object has exactly the keys `severity`, `rule`, `file` and `line`
And `GET https://builder.skillbuilder.internal/builds/7` contains `<section id="llm-scan-report">`, `<div id="llm-scan-model">Model: test-model-medium</div>`, `<div id="llm-scan-state">LLM scan: Complete</div>` and a `<table id="llm-scan-findings">` whose two rows have the cells `HIGH | SP-0090 | skills/sdlc-fix-bug-triage/templates/report.md | 4` and `MEDIUM | SP-0117 | skills/sdlc-fix-bug-triage/references/run.md | 8`

#### Scenario: A completed scan with no findings still shows the model
Given LLM scan `55` is `complete` for build `9`'s content `0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d` with `model` `test-model-medium` and `findings` `[]`
And it is the only `llm_scans` row for that content
When Grace requests `GET https://builder.skillbuilder.internal/builds/9` carrying her `sb_session` cookie
Then the page contains `<div id="llm-scan-model">Model: test-model-medium</div>`, `<div id="llm-scan-state">LLM scan: Complete</div>` and a `<table id="llm-scan-findings">` with the single row `No findings`
And `GET https://builder.skillbuilder.internal/api/llm-scans/55` returns `"state":"complete"`, `"model":"test-model-medium"` and `"findings":[]`

#### Scenario: An unavailable scan is shown with its reason
Given LLM scan `54` is `unavailable` for build `7`'s content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` with `error` `llm_model_profile_missing`
And it is the only `llm_scans` row for that content
When Ada requests `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the page contains `<div id="llm-scan-model">Model: Not scanned</div>`, `<div id="llm-scan-state">LLM scan: Unavailable</div>`, `<div id="llm-scan-error">llm_model_profile_missing</div>` and a `<table id="llm-scan-findings">` with the single row `No findings`
And `GET https://builder.skillbuilder.internal/api/llm-scans/54` returns `"state":"unavailable"`, `"error":"llm_model_profile_missing"` and `"findings":[]`

#### Scenario: A build with no LLM scan shows a not-run section
Given no `llm_scans` row exists for build `7`'s content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
When Ada requests `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the page contains `<div id="llm-scan-model">Model: Not scanned</div>`, `<div id="llm-scan-state">LLM scan: Not run</div>`, no `<div id="llm-scan-error">` element and a `<table id="llm-scan-findings">` with the single row `No LLM scan`

#### Scenario: An unknown LLM scan id is not found
Given Ada is a current member of the `skill-builders` group
When Ada requests `GET https://builder.skillbuilder.internal/api/llm-scans/999` carrying the `sb_session` cookie
Then the response is HTTP 404 with body exactly `{"error":{"code":"not_found","message":"LLM scan not found"}}`

### Covered requirements (traceability)
- FR-086
- FR-090
- FR-156

### Out of scope
Producing, triggering or isolating the scan (BSB-32-PENDING-1, BSB-32-PENDING-2 and BSB-32-PENDING-4); a run's behaviour while the scan runs (BSB-32-PENDING-3); the full-scan entry point (BSB-32-PENDING-6); the run page's Security tab and its rendering (epic BSB-33, FR-157); the readiness panel (epic BSB-30); the static report section on the same page (epic BSB-31); accessibility of the new section (epic BSB-38).

### Notes / dependencies
- Depends on epic BSB-32-PENDING-1 for the row, BSB-32-PENDING-2 for the model identity, and
  BSB-32-PENDING-4 for the unavailable state; on epic BSB-20 for the build page; and on epic
  BSB-21 for the build's current `head_sha`.
- FR-090 is satisfied by the report's `model` field and the page's `Model:` line. The value is
  the model the scanner's validated report states, not the value the request asked for; a report
  whose model differs is never displayed because it is `unavailable` (BSB-32-PENDING-4).
- FR-086 is satisfied on the build page, which is the author's skill-page surface. The run page
  Security tab is BSB-33's; it reads the same report API and model identity.
- The findings table order is the report API's order: severity rank descending, then file, then
  line. The page does not re-sort.

---

## STORY: BSB-32-PENDING-6

**Summary:** Start a full security scan from the skill page using the project's LLM-scan profile
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-12, MVP

### Story
As a **skill author who is a member of a test project**, I want **to start a full security scan from a build's skill page without starting a run**, so that **I can get both the deterministic and the model-based security review before spending a run**.

### Acceptance Criteria

#### Scenario: A project member starts a full security scan from the build page
Given Ada is a current member of the `skill-builders` group and a member of project `7`
And build `7`'s head is `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` with bundle content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And project `7` has LLM-scan profile `3` and tier `medium`
And no `static_scans` or `llm_scans` row exists for that content
And the `static_scans` identity sequence makes the next row id `21`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` carrying the `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"full"}`
Then the response is HTTP 202 with `Content-Type: application/json` and body exactly `{"scan_id":21,"state":"queued","kind":"full","build_id":7,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a","llm_scan_id":null}`
And `SELECT run_id, build_id, state, llm_stage FROM static_scans WHERE id = 21` returns exactly `NULL | 7 | queued | true`
And `SELECT count(*) FROM llm_scans` returns `0`
And `SELECT count(*) FROM runs` returns `11`
And no catalog branch is created and no Docker container labelled `bb.run_id` exists
And `GET https://builder.skillbuilder.internal/builds/7` contains `<button id="full-scan-start">Run full security scan</button>`

#### Scenario: The LLM stage starts only after the static stage passes, using the project's profile
Given full scan static row `21` is `running` with `llm_stage` `true`
And project `7` has `llm_scan_model_profile_id` `3` and `llm_scan_tier` `medium`
And the secret at `skill-builder/7/ai_model` has exactly the value `sk-ant-test-5f2c8e1d`
And no `llm_scans` row exists for that content and the `llm_scans` identity sequence makes the next row id `51`
And the scanner stub records the start order of the static and LLM containers
When the scanner stub reports static `verdict` `passed` for row `21`
Then `SELECT state, verdict, llm_stage FROM static_scans WHERE id = 21` returns exactly `completed | passed | true`
And `SELECT project_id, run_id, build_id, state, model_integration_id, model_profile_id, model_tier, vendor, base_url, model FROM llm_scans WHERE id = 51` returns exactly `7 | NULL | 7 | queued | 7 | 3 | medium | anthropic | https://api.anthropic.test | test-model-medium`
And the scanner stub's first start is the static container and its second start is LLM scan `51`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'llm')` returns `not_run` while scan `51` is `queued`

#### Scenario: A full scan whose static stage fails starts no LLM stage
Given full scan static row `21` is `running` with `llm_stage` `true`
And the scanner stub records every LLM container start
When the scanner stub reports static `verdict` `failed` with `recommendation` `DO_NOT_INSTALL` for row `21`
Then `SELECT state, verdict, llm_stage FROM static_scans WHERE id = 21` returns exactly `completed | failed | true`
And `SELECT count(*) FROM llm_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a'` returns `0`
And the scanner stub records no LLM container start
And `GET https://builder.skillbuilder.internal/api/scans/21` returns `"state":"completed"` and `"verdict":"failed"`

#### Scenario: The full scan uses the project's configured model and ignores per-request model values
Given Ada is a member of project `7`
And project `7` has `llm_scan_model_profile_id` `3` and `llm_scan_tier` `medium`
And no `static_scans` or `llm_scans` row exists for build `7`'s content
And the `static_scans` identity sequence makes the next row id `21` and the `llm_scans` identity sequence makes the next row id `51`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` carrying the `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"full","model":"test-model-high","model_profile_id":4,"tier":"high"}`
Then the response is HTTP 202 with `"kind":"full"` and a `scan_id`
And `SELECT llm_stage FROM static_scans WHERE id = 21` returns `true`
When the scanner stub reports static `verdict` `passed` for row `21`
Then `SELECT model_integration_id, model_profile_id, model_tier, vendor, base_url, model FROM llm_scans WHERE id = 51` returns exactly `7 | 3 | medium | anthropic | https://api.anthropic.test | test-model-medium`
And the LLM container command passes `--vendor anthropic`, `--model test-model-medium` and `--endpoint https://api.anthropic.test`
And the request's `model`, `model_profile_id` and `tier` values are not used

#### Scenario: A project without an LLM-scan profile still completes the static stage
Given Grace is a current member of the `skill-builders` group and the owner of project `8`
And build `9`'s head is `5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b` with bundle content `0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d`
And project `8` has `llm_scan_model_profile_id` `NULL` and `llm_scan_tier` `NULL` and no `ai_model` integration
And no `static_scans` or `llm_scans` row exists for that content
And the `static_scans` identity sequence makes the next row id `22` and the `llm_scans` identity sequence makes the next row id `53`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects/8/scans` carrying her `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":9,"kind":"full"}`
Then the response is HTTP 202 with `"scan_id":22`, `"kind":"full"` and `"llm_scan_id":null`
And `SELECT llm_stage FROM static_scans WHERE id = 22` returns `true`
When the scanner stub reports static `verdict` `passed` for row `22`
Then `SELECT state, model_integration_id, model_profile_id, model_tier, vendor, base_url, model, error, findings FROM llm_scans WHERE id = 53` returns exactly `unavailable | NULL | NULL | NULL | NULL | NULL | NULL | llm_model_profile_missing | []`
And no LLM container starts
And `GET https://builder.skillbuilder.internal/api/scans/22` returns `"state":"completed"` and `"verdict":"passed"`
And `readiness_scan_outcome('0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d', 'llm')` returns `unavailable`, which permits Ready

#### Scenario: A user who is not a project member cannot start a full scan
Given Alan is a current member of the `skill-builders` group and is not a member of project `7`
When Alan sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` carrying his `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"full"}`
Then the response is HTTP 403 with body exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM static_scans` returns `0` and `SELECT count(*) FROM llm_scans` returns `0`
And no scanner container starts

### Covered requirements (traceability)
- FR-093
- FR-139
- FR-163

### Out of scope
The trigger condition and reuse without a full-scan request (BSB-32-PENDING-1); the container's credential and network policy (BSB-32-PENDING-2); a run's behaviour while a scan runs (BSB-32-PENDING-3); the full unavailable cause matrix (BSB-32-PENDING-4); the report and page display (BSB-32-PENDING-5); the static-only button and route (epic BSB-31); project creation, listing and membership management (epic BSB-22); configuring the AI model integration, its profiles or its secret (epic BSB-23); running a test run (epics BSB-24 to BSB-27); the CLI `scan` command (epic BSB-37).

### Notes / dependencies
- Depends on epic BSB-18 for the member session and group gate; on epic BSB-22 for project
  resolution, membership and the two LLM-scan setting columns; on epic BSB-23 for the `ai_model`
  integration, profile mapping and secret reference; on epic BSB-31 for the static scan, its
  route, `kind` validation and report API; on epic BSB-20 and BSB-21 for the build page and
  `head_sha`; and on epic BSB-25 for packing the build head's bundle.
- A full scan is asynchronous: the `202` returns the static scan id, and the author reads the
  static report through BSB-31's `GET /api/scans/{scan_id}`, the LLM report through
  `GET /api/llm-scans/{llm_scan_id}` and the build page's two sections. The response's
  `llm_scan_id` is `null` until a row exists; the worker creates it after the static pass.
- The static stage runs first. A static failure means no LLM stage, as the epic requires; the
  failed static report is still the author's result.
- **Boundary for review — project picker.** The build page's control needs the caller's projects
  to choose the test project FR-093 requires. Epic BSB-22 owns the `projects` and
  `project_members` rows but its stories do not define a project-list endpoint or page. If
  BSB-22 does not add one, the control takes a numeric `project_id` instead of a picker; the
  route and every scenario above do not change.
- FR-163's "configured for the scan's test project" is proved two ways: the project setting
  chooses the profile, tier and model, and a request that carries its own model values still
  uses the project's. There is no per-run or per-request override.
- The full scan creates no `runs` row, no run branch, no baseline and no agent container; only
  the scanner containers run. It is not a run and does not consume a run's turn or spend caps.

---

*Generated by `sdlc-plan-stories-write`. Coverage: FR-082, FR-083, FR-084, FR-085, FR-086,
FR-090, FR-093, FR-139, FR-156 and FR-163 all covered. Next steps: `sdlc-plan-epic-review`
reviews this set; `sdlc-tracker-sync` publishes the approved stories to Jira.*
