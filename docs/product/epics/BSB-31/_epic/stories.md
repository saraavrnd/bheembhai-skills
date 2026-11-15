# Stories — BSB-31 (Static security scanning)

Source: Jira epic **BSB-31** — *Static security scanning* (feature area FA-11, release MVP,
labels FA-11, MVP), fetched read-only from the Atlassian project `bheembhai-skill-builder`; its
summary, description, functional scope, goal, stated edge cases and covered-requirement list are
the same as the BSB-31 section of `docs/product/epics.md`. The requirement IDs mapped to the epic
are in `docs/product/epic-map.json`.

Epic BSB-31 covers 14 requirements. They decompose into the 7 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` holds the BSB epics, and this
run's item, from the workflow context (`ITEM.id` = `BSB-31`), is epic **BSB-31**. No Atlassian MCP
tool is connected in this session, so the epic was fetched read-only through the Atlassian REST
API with the same credentials. Nothing was written to Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-076 | BSB-31-PENDING-1 |
| FR-077 | BSB-31-PENDING-2 |
| FR-078 | BSB-31-PENDING-3 |
| FR-079 | BSB-31-PENDING-3 |
| FR-080 | BSB-31-PENDING-3 |
| FR-081 | BSB-31-PENDING-3 |
| FR-087 | BSB-31-PENDING-4 |
| FR-088 | BSB-31-PENDING-4 |
| FR-089 | BSB-31-PENDING-6 |
| FR-091 | BSB-31-PENDING-5 |
| FR-092 | BSB-31-PENDING-7 |
| FR-154 | BSB-31-PENDING-6 |
| FR-155 | BSB-31-PENDING-6 |
| NFR-005 | BSB-31-PENDING-1 |

The epic's three stated edge cases are covered explicitly: content changing mid-scan
(BSB-31-PENDING-2), a scanner that returns a malformed report (BSB-31-PENDING-1) and cache reuse
across different content hashes (BSB-31-PENDING-2). The epic's non-goals are respected: no builtin
verifier check changes and no human override of a static block.

## Static scan contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control, object-store
and kit fixture unless it says otherwise. The member session, the local `users` rows and the
`skill-builders` gate are established by epic BSB-18. The project, `projects` rows and
`project_members` rows are established by epic BSB-22. The build, its branch and `head_sha` are
epic BSB-21's (its requirements, not yet decomposed, are FR-018 to FR-022, FR-127 and FR-162);
the build-creation shapes are epic BSB-20's. The bundle, skills-commit resolution, run branch and
baseline are epic BSB-25's (FR-038 to FR-043). The run row and its `queued` start state are epic
BSB-24's. `builds`, `runs` and `skill_bundles` columns follow
`docs/adr/SK-001-skill-builder.md` §1a, §5 and §9. The scanner image, `bheembhai-skillscan`
package and scanner container follow §2 and §6b.

This epic adds one table to that data model: `static_scans` (Decision 1). It is additive; no
existing column changes meaning.

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
| Build `7` | `kind` = `edit`, `skill` = `sdlc-fix-bug-triage`, `branch` = `build/sdlc-fix-bug-triage`, `created_by` = `42`, `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `NULL`, `state` = `open` |
| `builds` fixture state | rows with ids `1` to `16` exist; build `7` is the row above; build `17` is epic BSB-20's clone fixture |
| Run `11` | `kind` = `run`, `project_id` = `7`, `user_id` = `42`, `skill` = `sdlc-fix-bug-triage`, `skills_ref` = `build/sdlc-fix-bug-triage`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `input_branch` = `main`, `state` = `queued`, `run_branch` = `NULL`, `claimed_verdict` = `NULL`, `final_verdict` = `NULL`, `verification` = `NULL` |
| `runs` fixture state | rows with ids `1` to `9` are other fixture runs, there is no run `10`, and run `11` is the row above; `SELECT count(*) FROM runs` is `10` |
| Catalog repository | `saraavrnd/bheembhai-skills` |
| Skill | `sdlc-fix-bug-triage`, folder `skills/sdlc-fix-bug-triage/` |
| `skills_commit_sha` at the main fixture | `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` |
| Bundle row for that pair | `skill_bundles` (`skills_commit_sha` `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `skill` `sdlc-fix-bug-triage`, `bundle_sha256` `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`, `s3_key` `bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz`) |
| Object-store bucket | `skill-builder-runs` |
| Kit pin | `skill-builder/kit.txt` contains exactly `kit-v8` |
| `kit.json` for `kit-v8` | `{"kit":"kit-v8","env_contract_version":"4","bheembhai-stepkit":"0.5.0","bheembhai-verify":"2.2.0","bheembhai-skillscan":"1.6.0","agent_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-agent@sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13","scanner_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d"}` |
| Scanner image | `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d`, always pulled by digest and never by tag |
| Scanner package version | `bheembhai-skillscan` `1.6.0` |
| Scan API | `POST https://builder.skillbuilder.internal/api/projects/{project_id}/scans` |
| Report API | `GET https://builder.skillbuilder.internal/api/scans/{scan_id}` |
| Success statuses | HTTP 202 with `Content-Type: application/json` for an accepted scan start; HTTP 200 with `Content-Type: application/json` for a report read |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |

**Scan fixture rows.** The base fixture contains no `static_scans` rows. A scenario's Given seeds
exactly the rows it names from the table below, and no other scan row exists while that scenario
runs; the `static_scans` identity sequence is set so the next inserted row gets the id the
scenario asserts. Every row below has `skill` = `sdlc-fix-bug-triage`, `image_digest` = the
scanner image digest above and `scanner_version` = `1.6.0` unless the scenario says otherwise.
A `completed` row has a terminal result; a `failed` row is a scan that did not produce a valid
report. Scores, recommendations and findings are the scanner's own values, stored unchanged.

| Scan | `skills_commit_sha` | `content_sha` | `state` | `verdict` | `score` | `recommendation` | `coverage` | `findings` | Purpose |
|------|---------------------|---------------|---------|-----------|---------|------------------|------------|------------|---------|
| `12` | `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` | `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` | `completed` | `passed` | `100` | `INSTALL` | `complete` | `[]` | the passing scan for the main bundle |
| `13` | `7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f` | `c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5` | `completed` | `failed` | `12` | `DO_NOT_INSTALL` | `complete` | `[]` | a `DO_NOT_INSTALL` scanner verdict |
| `14` | `8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a` | `d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6` | `completed` | `failed` | `80` | `INSTALL` | `complete` | one `CRITICAL` `SP-0042` finding | a critical finding |
| `15` | `9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b` | `e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7` | `completed` | `failed` | `90` | `INSTALL` | `incomplete` | `[]` | incomplete coverage |
| `16` | `1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d` | `f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8` | `completed` | `failed` | `100` | `INSTALL` | `complete` | one accepted `CRITICAL` `SP-0042` finding | an accepted finding cannot clear a block |
| `17` | `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e` | `a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9` | `completed` | `failed` | `63` | `INSTALL` | `complete` | one `CRITICAL`, one `HIGH` and one `MEDIUM` finding | the report display fixture |
| `18` | `0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c` | `b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0` | `running` | `NULL` | `NULL` | `NULL` | `NULL` | `[]` | an in-flight scan |

**`static_scans` — the static scan record (Decision 1).**

| Column | Type and value |
|--------|----------------|
| `id` | bigint identity primary key |
| `run_id` | bigint NULL; the `runs.id` of the first request when the scan came from a run's preparation, otherwise `NULL` |
| `build_id` | bigint NULL; the `builds.id` of the first request when the scan came from the skill page, otherwise `NULL` |
| `skill` | text; the skill folder name |
| `skills_commit_sha` | char(40) lowercase hex |
| `content_sha` | char(64) lowercase hex; the SHA-256 of the exact bundle tar.gz, equal to `skill_bundles.bundle_sha256` |
| `image_digest` | text; the `scanner_image` reference from `kit.json`, including `@sha256:` |
| `scanner_version` | text; the `bheembhai-skillscan` version the report states |
| `state` | one of `queued`, `running`, `completed` or `failed` |
| `verdict` | `passed` or `failed`; `NULL` only while `queued` or `running` |
| `score` | smallint NULL; `0` to `100` from the report |
| `recommendation` | `INSTALL`, `DO_NOT_INSTALL` or `NULL` |
| `coverage` | `complete`, `incomplete` or `NULL` |
| `findings` | JSONB NOT NULL default `[]`; each entry has exactly the keys `severity`, `rule`, `file`, `line` |
| `error` | text NULL; on `failed` one of `scan_timeout`, `scanner_failed`, `scanner_report_invalid`, `scanner_version_mismatch` or `bundle_digest_mismatch` |
| `created_at` | timestamptz |
| `started_at` | timestamptz NULL |
| `finished_at` | timestamptz NULL |

`CREATE UNIQUE INDEX static_scans_live_or_completed ON static_scans (content_sha, image_digest)
WHERE state = 'queued' OR state = 'running' OR state = 'completed';` — at most one live or
completed scan per content and scanner image. Any number of `failed` rows may exist for the same
pair, so a timed-out or malformed scan can be retried (BSB-31-PENDING-2 and BSB-31-PENDING-4).

A scan row is content-addressed: the first request for a `(content_sha, image_digest)` pair
records its `run_id` or `build_id`; a later request for the same pair reuses that row and does
not rewrite those two columns. The report read is authorized by the `skill-builders` group gate,
not by project membership (Decision 3).

**The scanner invocation.** The builder verifies the bundle object's SHA-256 equals the row's
`content_sha` before it starts anything. It starts the pinned image by digest, never by tag.
For scan `12` of the main bundle, the builder starts exactly:

```
docker run --rm --network none --read-only --tmpfs /tmp --label bb.scan_id=12
  --mount type=bind,src=/var/lib/skill-builder/bundles/b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a.tar.gz,dst=/scan/bundle.tar.gz,readonly
  --mount type=bind,src=/var/lib/skill-builder/scans/12,dst=/scan/out
  123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d
  bheembhai-skillscan scan --stage static --bundle /scan/bundle.tar.gz --skill sdlc-fix-bug-triage --out /scan/out/report.json
```

For another scan the label is that scan's id, the two host paths are that scan's verified bundle
object and its own output directory, the image is the digest pinned in `kit.json`, and the
`--skill` value is the bundle's skill folder.

The static stage is given no credential, no secret reference and no application environment; the
only application-set variable is `HOME=/tmp`, and the container is never labelled `bb.run_id`. The
app process only parses the report; it never runs scanner code itself. The exact CLI flags are an
adapter decision (Decision 4): if the pinned package's flags differ, only the invocation changes.

**The scanner report the adapter normalizes and validates.** The report file is a JSON object with
exactly these required keys (unknown extra keys are ignored):

```
{"scanner_version":"1.6.0","verdict":"INSTALL","score":100,"recommendation":"INSTALL","coverage":{"complete":true,"files_scanned":7,"files_skipped":[]},"findings":[]}
```

Each `findings` entry has the required keys `severity` (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW` or
`INFO`), `rule` (non-empty string), `file` (non-empty path relative to the bundle root), `line`
(integer at least 1), `message` (string) and `accepted` (boolean); `accepted_reason` is a
non-empty string when `accepted` is true and `null` otherwise. A report is valid only when
`scanner_version` equals the pinned `1.6.0`, `verdict` and `recommendation` are each `INSTALL` or
`DO_NOT_INSTALL`, `score` is an integer from `0` to `100`, `coverage.complete` is a boolean,
`coverage.files_scanned` is an integer at least `0`, `coverage.files_skipped` is an array and
every finding satisfies the rules above. A report whose `scanner_version` differs records `state`
= `failed`, `verdict` = `failed`, `error` = `scanner_version_mismatch`, `findings` = `[]`, and
leaves `score`, `recommendation` and `coverage` `NULL`. Any other violation records the same
shape with `error` = `scanner_report_invalid`. A non-zero scanner exit records the same shape with
`error` = `scanner_failed`; a mismatch between the object's SHA-256 and `content_sha` records
`error` = `bundle_digest_mismatch` and starts no container.

**The builder's verdict (FR-078 to FR-081, one rule in one place).** The scanner's own `verdict`
and `recommendation` are stored unchanged for display. The builder's `verdict` is `failed` when
any of these holds, and `passed` otherwise:

1. the report's `verdict` is `DO_NOT_INSTALL`;
2. any finding has `severity` = `CRITICAL`, whether or not it is `accepted`;
3. `coverage.complete` is not `true`.

The `accepted` flag never changes the builder's verdict: acceptance is a display attribute, so an
accepted finding cannot clear a block. There is no override of a `failed` verdict (FR-081).

**The readiness read interface.** Epics BSB-30 and BSB-27 consume the static outcome through
`readiness_scan_outcome(content_sha, 'static')`, which returns `passed`, `failed` or `not_run`, and
`readiness_scan_id(content_sha, 'static')`, which returns the id of the row the outcome came from
or `NULL`. Both select, for the given `content_sha` and the currently pinned `image_digest`, the
latest terminal row (`state` `completed` or `failed`) by `finished_at` then `id`. No terminal row —
including when only a `queued` or `running` row exists — returns `not_run` and `NULL`. The
`kind` value `llm` is epic BSB-32's. Epic BSB-30's `detail.static_scan_id` is
`readiness_scan_id(content_sha, 'static')`.

**Report API.** `GET https://builder.skillbuilder.internal/api/scans/{scan_id}` returns HTTP 200
with `Content-Type: application/json` and exactly these keys, in this order, for scan `17`:

```
{"scan_id":17,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e","content_sha":"a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9","state":"completed","verdict":"failed","score":63,"recommendation":"INSTALL","coverage":"complete","error":null,"scanner_version":"1.6.0","image_digest":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d","findings":[{"severity":"CRITICAL","rule":"SP-0042","file":"skills/sdlc-fix-bug-triage/SKILL.md","line":17},{"severity":"HIGH","rule":"SP-0090","file":"skills/sdlc-fix-bug-triage/templates/report.md","line":4},{"severity":"MEDIUM","rule":"SP-0117","file":"skills/sdlc-fix-bug-triage/references/run.md","line":8}]}
```

Findings are ordered by severity rank descending (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`),
then `file` ascending by plain byte comparison, then `line` ascending. Each finding object has
exactly the four keys `severity`, `rule`, `file` and `line`. When `state` is `failed`, `score`,
`recommendation` and `coverage` are `null`, `findings` is `[]` and `error` is the stored code.
When a scan is `queued` or `running`, `verdict`, `score`, `recommendation` and `coverage` are
`null`, `findings` is `[]` and `error` is `null`. An unknown `scan_id` is HTTP 404 with body
exactly `{"error":{"code":"not_found","message":"Scan not found"}}`. A signed-in user without
current `skill-builders` membership is rejected by epic BSB-18's gate with HTTP 403 and body
exactly `{"error":{"code":"not_a_member","message":"You are not a member of the skill-builders group"}}`.

**Build-page section.** Epic BSB-20's `GET https://builder.skillbuilder.internal/builds/{build_id}`
page gains one `<section id="static-scan-report">` rendered for the build's current `head_sha`.
The section shows the latest terminal scan for the bundle content SHA of
(`builds.head_sha`, `builds.skill`): `<div id="static-scan-score">` with the exact text
`Score: 63/100`, `<div id="static-scan-recommendation">` with the exact text
`Recommendation: INSTALL`, and `<table id="static-scan-findings">` with one table row per finding
whose four cells are the exact `severity`, `rule`, `file` and `line`. A scan with no
findings shows the single table row `No findings`. A terminal scan with `state` `failed` shows
`Score: Not scanned`, `Recommendation: Not scanned`, the exact `error` code inside
`<div id="static-scan-error">`, and the single table row `No findings`. With no bundle or no
terminal scan the section shows the exact text `Score: Not scanned`, `Recommendation: Not scanned`
and the single table row `No scan`. The section is added by this epic; epic BSB-20's other page
regions are unchanged.

**Static-only scan API.** `POST https://builder.skillbuilder.internal/api/projects/{project_id}/scans`
with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"static"}`. `kind` is
optional and defaults to `static`; this epic accepts only `static` (epic BSB-32 adds `full`). The
route resolves the build's `head_sha` and skill, packs or reuses the bundle through epic BSB-25 and
starts or reuses the static scan. A successful start is HTTP 202 with `Content-Type:
application/json` and body exactly:

```
{"scan_id":21,"state":"queued","build_id":7,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a"}
```

When a completed or running row exists for the same `(content_sha, image_digest)`, the response is
the same shape with that row's `scan_id` and its `state`; no second container starts. The request
creates no `runs` row, no catalog branch, no `skill_bundles` row for content that already exists
and no agent container (BSB-31-PENDING-7). The response's `build_id` is the request's build id;
the stored `static_scans.run_id` and `static_scans.build_id` keep the first requester's values.

Validation order on that route is fixed: epic BSB-18's session gate (401
`authentication_required`), its group gate (403 `not_a_member`), project resolution (404
`project_not_found`), project membership (403 `project_membership_required`), request-body
validation (422), then build resolution (404 `not_found`) and the scan start.

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| `project_id` `999` does not exist | 404 | `{"error":{"code":"project_not_found","message":"Project 999 does not exist."}}` |
| The caller is not a member of the project | 403 | `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}` |
| `build_id` is missing or is not a JSON integer | 422 | `{"error":{"code":"build_id_required","message":"A build_id is required."}}` |
| `kind` is present and is not `static` | 422 | `{"error":{"code":"kind_invalid","message":"Scan kind 'full' is not supported."}}` |
| The `builds` row does not exist | 404 | `{"error":{"code":"not_found","message":"Build not found"}}` |

## Decisions recorded in this decomposition (confirm at review)

1. **Static scan storage.** ADR §9 names no scan table. This decomposition adds `static_scans`,
   content-addressed by the bundle SHA-256 and the scanner image digest, as an additive table. A
   JSONB column on `runs` would duplicate a result per run and lose the cache, so the cache is the
   table. If review prefers another store, the states, verdict rule and read interface do not
   change.
2. **Scanner report contract.** The platform ADR-034 is not in this repo, so the report's
   normalized shape is pinned above: `scanner_version`, `verdict`, `score`, `recommendation`,
   `coverage` and `findings`, with the finding keys given. If `bheembhai-skillscan` emits a
   different shape, only the adapter and its validation change; the stored columns and the
   builder's verdict rule do not.
3. **Scan record identity and read authorization.** A scan is the content-addressed result for
   `(content_sha, image_digest)`, not a per-run or per-project row. The first requester's `run_id`
   or `build_id` is recorded for trace; later requesters reuse the row. Any current
   `skill-builders` member may read a report; project membership gates only the static-only start
   (FR-092), and the run path is gated by the run start's project check.
4. **Scanner invocation.** The Docker flags and `bheembhai-skillscan` subcommand above are pinned
   by this decomposition. The properties the requirements need — by-digest image, read-only
   bundle, no network, no credential, 10-minute limit — are asserted independently of the flags.
5. **Scan timing in run preparation.** The scan runs after epic BSB-25 has packed the bundle and
   before it creates the run branch, the baseline or the agent container. Epic BSB-30's preflight
   stays before packing. Refusing a run whose static outcome is not `passed` remains FR-055, epic
   BSB-27's; this epic only records the outcome.
6. **Reuse key includes the scanner image.** FR-077 says "the content is unchanged"; the verdict
   also depends on the scanner version (FR-091), so a cached result is reused only when both the
   bundle SHA-256 and the pinned scanner image digest match. A kit update therefore re-scans
   unchanged content, which keeps the parity claim true.
7. **Timeout.** The ten-minute limit is per scanner container, measured from `started_at`; at 600
   seconds the builder kills the container and writes `state` = `failed`, `verdict` = `failed`,
   `error` = `scan_timeout` and `finished_at` = `started_at` + 600 seconds.
8. **Static-only scan entry point.** The "skill page" is epic BSB-20's build page
   `GET /builds/{build_id}`; FR-092's test project is carried as `project_id` on the request. The
   page's control is described in BSB-31-PENDING-7. Epic BSB-32 extends the same route with
   `kind` = `full`.
9. **Report display ownership.** This epic adds only `<section id="static-scan-report">` to the
   build page and owns the report API. The run page's Security tab and its rendering are epic
   BSB-33's (FR-157); this epic supplies the report that page reads.

## Cross-epic notes

- **BSB-18 (session and group gate).** Every route and page region here sits behind BSB-18's
  session and `skill-builders` gates. A non-member never reaches scan resolution or storage.
- **BSB-20 and BSB-21 (build page and build head).** This epic adds the `static-scan-report`
  section to BSB-20's `GET /builds/{build_id}` page and reads `builds.head_sha`, `builds.skill`
  and `builds.branch` from BSB-21's build record. BSB-21 has no stories yet; its decomposition
  must keep `head_sha` current on every save. No other BSB-20 page region changes.
- **BSB-22 (project membership).** FR-092's static-only start applies BSB-22's project
  resolution and membership decision with its exact 404 `project_not_found` and 403
  `project_membership_required` bodies. This epic adds no membership rule of its own.
- **BSB-25 (packaging and bundle).** The scan consumes the exact bundle BSB-25 packs:
  `skill_bundles.bundle_sha256` is the scan's `content_sha` and `skill_bundles.s3_key` is the
  object it verifies and mounts. BSB-25's decomposition must call this epic's
  `ensure_static_scan(bundle)` after packing and before creating the run branch, baseline or
  agent container. If the bundle's SHA-256 does not match `bundle_sha256`, no run branch is
  created for that content and the scan row records `bundle_digest_mismatch`.
- **BSB-27 (refusal, re-runs and output chaining).** FR-055's refusal is BSB-27's: it reads
  `readiness_scan_outcome(content_sha, 'static')` and refuses a run that is not `passed`. Every
  path that starts a run — the first run, a re-run, output chaining and the CLI — must request the
  scan for its exact bundle, so the refusal is never bypassed. This epic does not refuse a run and
  does not write `runs.state`.
- **BSB-30 (readiness).** BSB-30 consumes `readiness_scan_outcome(content_sha, 'static')` and
  `readiness_scan_id(content_sha, 'static')`; `detail.static_scan_id` is this epic's scan id. A
  non-passing builder verdict (including a timeout, a malformed report or an accepted critical
  finding) is `failed` for readiness, never `passed`.
- **BSB-32 (LLM scan).** The LLM stage is triggered only after this epic's static verdict for the
  content SHA is `passed`. BSB-32 extends `POST /api/projects/{project_id}/scans` with
  `kind` = `full`; this epic accepts only `static`. BSB-32 owns its own storage and must record an
  `unavailable` outcome rather than an absent one.
- **BSB-33 (run report).** The run page's Security tab renders the report this epic records
  (FR-157). Epic BSB-33 owns that page region; this epic owns only the report API and the build
  page section.
- **BSB-34 (retention).** Scan reports and their findings live in `static_scans`; any retention or
  redaction rule for them is epic BSB-34's.
- **BSB-37 (CLI).** `python -m skill_builder.runner scan --static-only` calls the same scan service
  and records the same `static_scans` row; the CLI itself is out of scope here.
- **BSB-38 (accessibility).** The build-page scan control and report section are new builder web
  surfaces; their WCAG 2.1 AA and 320-pixel reflow checks belong to epic BSB-38 and add no
  requirement here.

---

## STORY: BSB-31-PENDING-1

**Summary:** Scan the exact bundle before every run in a sealed scanner container
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the builder to scan the exact bundle a run will use before that run executes, in a scanner container with no network and no credential**, so that **a run only ever tests content whose static result belongs to that exact content**.

### Acceptance Criteria

#### Scenario: A run's exact bundle is scanned before the run branch is created
Given run `11` is `queued` with `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` and `run_branch` = `NULL`
And epic BSB-25 has packed the bundle whose `bundle_sha256` is `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` and stored it at `s3://skill-builder-runs/bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz`
And the scanner stub holds the scan in `running` until released
When BSB-25's preparation reaches `ensure_static_scan` for run `11`
Then `SELECT id, run_id, build_id, skill, content_sha, image_digest, state FROM static_scans WHERE id = 12` returns exactly `12 | 11 | NULL | sdlc-fix-bug-triage | b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a | 123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d | running`
And `SELECT run_branch FROM runs WHERE id = 11` is `NULL`
And no Docker container labelled `bb.run_id=11` exists
And BSB-25 has not created `skilltest/11` and has not recorded a baseline

#### Scenario: A completed passing scan becomes the readiness outcome for that content
Given scan `12` is `running` for run `11` and content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And BSB-25's preparation is waiting on it
When the scanner stub writes the passing report with `verdict` `INSTALL`, `score` `100`, `recommendation` `INSTALL`, `coverage.complete` `true` and `findings` `[]` and exits 0
Then `SELECT state, verdict, score, recommendation, coverage, error FROM static_scans WHERE id = 12` returns exactly `completed | passed | 100 | INSTALL | complete | NULL`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'static')` returns `passed`
And `readiness_scan_id('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'static')` returns `12`
And only after that does BSB-25 create the run branch `skilltest/11` and record its baseline

#### Scenario: A bundle whose SHA-256 does not match the recorded content is not scanned
Given `skill_bundles` records `bundle_sha256` = `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` for `(4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b, sdlc-fix-bug-triage)`
And the object at `s3://skill-builder-runs/bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz` has SHA-256 `9f1e2d3c4b5a69788796a5b4c3d2e1f00112233445566778899aabbccddeeffa`
When `ensure_static_scan` is called for run `11`
Then no scanner container is started
And `SELECT state, verdict, error, findings FROM static_scans WHERE id = 12` returns exactly `failed | failed | bundle_digest_mismatch | []`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'static')` returns `failed`

#### Scenario: The static scan container has no network access
Given a scan row `12` is `queued` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
When the builder starts the scanner container
Then `docker inspect` reports `"NetworkMode": "none"` and the label `bb.scan_id` = `12`
And the bundle is mounted read-only at `/scan/bundle.tar.gz` and the report path `/scan/out/report.json` is writable
And the container environment contains no key matching `JIRA`, `GITHUB`, `AWS`, `ANTHROPIC` or `BB_` and no secret reference
And a probe inside the container that opens `https://example.com` and one that connects to `1.1.1.1:443` both fail
And the report is still produced and `SELECT state FROM static_scans WHERE id = 12` returns `completed`

#### Scenario: A malformed scanner report is recorded as a failed scan
Given a scan row `12` is `running` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
When the scanner exits 0 but writes `{"scanner_version":"1.6.0","verdict":"INSTALL","score":100}` to `/scan/out/report.json`
Then `SELECT state, verdict, score, recommendation, coverage, findings, error FROM static_scans WHERE id = 12` returns exactly `failed | failed | NULL | NULL | NULL | [] | scanner_report_invalid`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'static')` returns `failed`
And `ensure_static_scan` returns scan id `12` with `state` `failed` without raising
And `docker ps --filter label=bb.scan_id=12` lists no container

### Covered requirements (traceability)
- FR-076
- NFR-005

### Out of scope
Refusing a run whose static outcome is not `passed` (FR-055, epic BSB-27); reusing a completed result (BSB-31-PENDING-2); deciding which findings, coverage or scanner verdicts make a scan fail (BSB-31-PENDING-3); the ten-minute timeout (BSB-31-PENDING-4); parity with the platform (BSB-31-PENDING-5); the report display (BSB-31-PENDING-6); the static-only start route (BSB-31-PENDING-7). Packing the bundle, resolving the skills commit and creating the run branch or baseline (epic BSB-25). Changing any builtin verifier check (ADR §6a). Overriding a static block (the epic's non-goal).

### Notes / dependencies
- Depends on epic BSB-25 for the exact bundle, its `bundle_sha256` and its `s3_key`; on epic
  BSB-24 for the `queued` run row; and on epic BSB-18 for the member session.
- Depends on the pinned scanner image and `bheembhai-skillscan` package from `kit.json`
  (external prerequisite). If the kit names the image or package fields differently, only the
  adapter changes.
- `ensure_static_scan(bundle)` is this epic's service. Epic BSB-25 calls it after `tools/build.py`
  packs and uploads the bundle and before it creates `skilltest/11`, records the baseline
  or starts the agent container.
- The scan is of the exact content, not of the branch head at some later moment: a commit that
  lands after packing does not change the packed object, and its later content is scanned
  separately (BSB-31-PENDING-2).
- The scanner container is labelled `bb.scan_id` and never `bb.run_id`, so a test can prove the
  app starts no agent container while the scan is running.
- The static stage gets no credential: NFR-005's no-network rule and the absence of a secret
  reference are asserted together. The LLM stage is epic BSB-32's and is not started here.

---

## STORY: BSB-31-PENDING-2

**Summary:** Reuse a completed static scan result for unchanged content and scanner version
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the builder to reuse a completed static scan result when the bundle and scanner version are unchanged, and to scan again when either changes**, so that **repeated runs and scans are fast without ever showing me a result for different content**.

### Acceptance Criteria

#### Scenario: A second request for the same content and scanner image reuses the completed result
Given scan `12` is `completed` with `verdict` `passed` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` and image digest `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d`
And the scanner stub records every container start
When a second run at the same content calls `ensure_static_scan` with the same bundle
Then `SELECT count(*) FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a'` returns `1`
And the scanner stub records no new container start
And `ensure_static_scan` returns scan id `12` with `state` `completed` and `verdict` `passed`

#### Scenario: A different content hash is scanned again
Given scan `12` is `completed` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And a new commit produces the bundle whose `bundle_sha256` is `b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0`
And the scanner stub holds the new scan in `running`
When `ensure_static_scan` is called with that new bundle
Then the scanner stub records exactly one new container start
And `SELECT count(*) FROM static_scans WHERE content_sha = 'b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0'` returns `1`
And `readiness_scan_outcome('b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0', 'static')` returns `not_run`

#### Scenario: A request while the same content is already running joins the in-flight scan
Given scan `18` is `running` for content `b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0` and our scanner stub holds it open
When a second request for the same content and image arrives
Then `ensure_static_scan` returns scan id `18` with `state` `running`
And `SELECT count(*) FROM static_scans WHERE content_sha = 'b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0'` returns `1`
And the scanner stub records no second container start

#### Scenario: A changed scanner image does not reuse the old result
Given scan `12` is `completed` at image digest `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d`
And `kit.json` now pins scanner image `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:8d1e3f5a7b9c0d2e4f6a8b1c3d5e7f9a0b2c4d6e8f1a3b5c7d9e0f2a4b6c8d1e` with `bheembhai-skillscan` `1.6.0`
When `ensure_static_scan` is called for the same content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
Then the scanner stub records one new container start
And `SELECT count(*) FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a'` returns `2`
And `SELECT count(*) FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a' AND image_digest = '123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:8d1e3f5a7b9c0d2e4f6a8b1c3d5e7f9a0b2c4d6e8f1a3b5c7d9e0f2a4b6c8d1e'` returns `1`

#### Scenario: Content changing mid-scan stays bound to the content that was scanned
Given build `7`'s head is `0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c` and its bundle content is `b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0`
And scan `18` is `running` for that content
When a save moves `builds.head_sha` to `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` with bundle content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` while scan `18` is still running, and the scanner then writes a passing report for scan `18`
Then `SELECT content_sha, state, verdict FROM static_scans WHERE id = 18` returns exactly `b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0 | completed | passed`
And `SELECT count(*) FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a'` returns `0`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'static')` returns `not_run`

#### Scenario: A scan that did not produce a valid report is not reused
Given scan `19` is `failed` with `error` `scanner_report_invalid` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And the scanner stub now returns a valid passing report
When `ensure_static_scan` is called for the same content and image digest
Then the scanner stub records exactly one new container start
And `SELECT count(*) FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a'` returns `2`
And `SELECT state, verdict, error FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a' ORDER BY id DESC LIMIT 1` returns exactly `completed | passed | NULL`

### Covered requirements (traceability)
- FR-077

### Out of scope
The builder's verdict rule for a scan result (BSB-31-PENDING-3); the timeout and its retry (BSB-31-PENDING-4); parity with the platform for the same scanner version (BSB-31-PENDING-5); the report display (BSB-31-PENDING-6); the static-only start route (BSB-31-PENDING-7). Deciding when a new commit exists or moving `builds.head_sha` (epic BSB-21). Packing the bundle (epic BSB-25).

### Notes / dependencies
- Depends on BSB-31-PENDING-1 for the scan row and its terminal states, on epic BSB-25 for
  `bundle_sha256`, and on epic BSB-21 for `builds.head_sha`.
- The reuse key is `(content_sha, image_digest)`, not the commit SHA alone: the same bundle
  content can be reached from different commits, and a scanner kit update must not reuse a verdict
  the new scanner did not produce (FR-091). A completed result with `verdict` `failed` is also
  reused: the same content and scanner is deterministic.
- A `failed` row (timeout, malformed report, digest mismatch) is never reused; a later request
  starts a new scan, which is why the unique index excludes `failed` rows.
- The latest terminal row wins for `readiness_scan_outcome`; a `queued` or `running` row alone is
  `not_run`, never `passed`.
- The scanner stub in the fixture records every `docker run` so "no new container" is observable.

---

## STORY: BSB-31-PENDING-3

**Summary:** Compose a failed static verdict from DO_NOT_INSTALL, critical findings, incomplete coverage and accepted findings
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the builder's static verdict to fail on a DO_NOT_INSTALL scanner verdict, any critical finding, incomplete coverage or an accepted finding that would otherwise clear a block**, so that **a non-passing scan cannot be shown as passing because of how its findings are classified**.

### Acceptance Criteria

#### Scenario: A DO_NOT_INSTALL scanner verdict is not passing
Given the scanner writes a valid report with `verdict` `DO_NOT_INSTALL`, `score` `12`, `recommendation` `DO_NOT_INSTALL`, `coverage.complete` `true` and `findings` `[]`
When the scan for content `c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5` reaches a terminal state
Then `SELECT state, verdict, recommendation, score, coverage FROM static_scans WHERE content_sha = 'c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5'` returns exactly `completed | failed | DO_NOT_INSTALL | 12 | complete`
And `readiness_scan_outcome('c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5', 'static')` returns `failed`

#### Scenario: A critical finding is not passing even when the scanner recommends install
Given the scanner writes a valid report with `verdict` `INSTALL`, `score` `80`, `recommendation` `INSTALL`, `coverage.complete` `true` and one finding with `severity` `CRITICAL`, `rule` `SP-0042`, `file` `skills/sdlc-fix-bug-triage/SKILL.md`, `line` `17` and `accepted` `false`
When the scan for content `d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6` reaches a terminal state
Then `SELECT state, verdict, recommendation, coverage FROM static_scans WHERE content_sha = 'd5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6'` returns exactly `completed | failed | INSTALL | complete`
And `SELECT findings FROM static_scans WHERE content_sha = 'd5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6'` returns exactly `[{"severity":"CRITICAL","rule":"SP-0042","file":"skills/sdlc-fix-bug-triage/SKILL.md","line":17}]`
And `readiness_scan_outcome('d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6', 'static')` returns `failed`

#### Scenario: Incomplete scan coverage is not passing
Given the scanner writes a valid report with `verdict` `INSTALL`, `score` `90`, `recommendation` `INSTALL`, `coverage.complete` `false`, `coverage.files_skipped` `["skills/sdlc-fix-bug-triage/examples/bug-triage-LEARN-87.md"]` and `findings` `[]`
When the scan for content `e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7` reaches a terminal state
Then `SELECT state, verdict, recommendation, coverage FROM static_scans WHERE content_sha = 'e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7'` returns exactly `completed | failed | INSTALL | incomplete`
And `readiness_scan_outcome('e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7', 'static')` returns `failed`

#### Scenario: An accepted finding cannot clear a static-scan block
Given the scanner writes a valid report with `verdict` `INSTALL`, `score` `100`, `recommendation` `INSTALL`, `coverage.complete` `true` and one finding with `severity` `CRITICAL`, `rule` `SP-0042`, `file` `skills/sdlc-fix-bug-triage/SKILL.md`, `line` `17`, `accepted` `true` and `accepted_reason` `Reviewed in .skillspector-baseline.yaml by the catalog owners`
When the scan for content `f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8` reaches a terminal state
Then `SELECT state, verdict, recommendation, coverage FROM static_scans WHERE content_sha = 'f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8'` returns exactly `completed | failed | INSTALL | complete`
And `SELECT findings FROM static_scans WHERE content_sha = 'f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8'` returns exactly `[{"severity":"CRITICAL","rule":"SP-0042","file":"skills/sdlc-fix-bug-triage/SKILL.md","line":17}]`
And `readiness_scan_outcome('f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8', 'static')` returns `failed`

### Covered requirements (traceability)
- FR-078
- FR-079
- FR-080
- FR-081

### Out of scope
Changing the scanner's own `verdict`, `score` or `recommendation` (the scanner package's contract); overriding a `failed` verdict (the epic's non-goal); the report display of the scanner's own recommendation (BSB-31-PENDING-6); the LLM scan's verdict rules (epic BSB-32); making `readiness_scan_outcome` available (BSB-31-PENDING-1 and the contract preamble).

### Notes / dependencies
- Depends on BSB-31-PENDING-1 for the valid-report adapter and the `static_scans` row, and on the
  contract preamble's scanner report schema.
- The builder's verdict is computed once from the report and stored in `static_scans.verdict`;
  the scanner's own `verdict` and `recommendation` are stored unchanged for display. The two may
  disagree: a scanner can recommend `INSTALL` while a critical finding or incomplete coverage
  makes the builder's verdict `failed`.
- `accepted` is a display attribute. It never removes a finding from `static_scans.findings` and
  never changes the builder's verdict, so acceptance cannot clear a block (FR-081).
- The `findings` JSONB stores exactly the four display keys; the report's `message`,
  `accepted` and `accepted_reason` are consumed during verdict computation and not stored.

---

## STORY: BSB-31-PENDING-4

**Summary:** Time a static scan out after ten minutes and record it as failed
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **a static scan that runs longer than ten minutes to be stopped and recorded as failed**, so that **a hung scanner cannot hold a run or a scan open indefinitely or be mistaken for a pass**.

### Acceptance Criteria

#### Scenario: A scan still running at ten minutes is killed and recorded as failed
Given a scan row `19` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` is `running` with `started_at` `2026-11-15T10:00:00Z`
And the scanner stub has not written a report and has not exited
When the builder's clock reaches `2026-11-15T10:10:00Z`
Then the scanner container is killed and removed
And `SELECT state, verdict, score, recommendation, coverage, findings, error, finished_at FROM static_scans WHERE id = 19` returns exactly `failed | failed | NULL | NULL | NULL | [] | scan_timeout | 2026-11-15T10:10:00Z`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'static')` returns `failed`

#### Scenario: A scan that finishes just before the limit is completed, not timed out
Given a scan row `20` for content `c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5` is `running` with `started_at` `2026-11-15T10:00:00Z`
When the scanner writes a valid passing report and exits 0 at `2026-11-15T10:09:59Z`
Then `SELECT state, verdict, error, finished_at FROM static_scans WHERE id = 20` returns exactly `completed | passed | NULL | 2026-11-15T10:09:59Z`
And the builder does not kill the container

#### Scenario: A timed-out scan is not reused and a retry starts a new scan
Given scan `19` is `failed` with `error` `scan_timeout` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And the scanner stub now returns a valid passing report
When `ensure_static_scan` is called again for the same content and scanner image
Then the scanner stub records exactly one new container start
And `SELECT count(*) FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a'` returns `2`
And `SELECT state, verdict, error FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a' ORDER BY id DESC LIMIT 1` returns exactly `completed | passed | NULL`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'static')` returns `passed`

### Covered requirements (traceability)
- FR-087
- FR-088

### Out of scope
The agent run's deadline and turn/spend caps (epic BSB-27); the LLM scan's deadline (epic BSB-32); the readiness aggregate (epic BSB-30); the report display of a timed-out scan (BSB-31-PENDING-6); changing the scanner's own timeout handling inside its process (the scanner package).

### Notes / dependencies
- Depends on BSB-31-PENDING-1 for the container start and the scan row, and on
  BSB-31-PENDING-2 for the reuse rule. A `failed` row is outside the unique index, so the retry
  can create a new row.
- The limit is 600 seconds measured from `static_scans.started_at`, per scanner container. At
  the limit the builder kills the container and records the exact `finished_at`; it never waits
  for the scanner to exit.
- A timed-out scan is a non-passing result for `readiness_scan_outcome` and for epic BSB-27's
  refusal; it is never `not_run`, because the scan did run and did not pass.
- No partial report is stored: `score`, `recommendation`, `coverage` and `findings` stay unset and
  `findings` is `[]`.

---

## STORY: BSB-31-PENDING-5

**Summary:** Match the platform's static verdict for the same content and scanner version
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the builder's static result to match the platform's result for the same bundle and scanner version**, so that **a skill that passes here is not rejected at import and a failing skill is not falsely cleared here**.

### Acceptance Criteria

#### Scenario: The parity fixture produces the platform's result for every case
Given the parity fixture contains, for each case, a bundle with its `bundle_sha256` and a platform record whose `verdict` is the platform's own builder verdict for that content, recorded with scanner image digest `123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d` and `bheembhai-skillscan` `1.6.0`
And the cases are `install-clean`, `do-not-install`, `critical-finding`, `incomplete-coverage` and `accepted-critical`
And the `accepted-critical` platform record has `verdict` `failed`, `recommendation` `INSTALL` and one accepted `CRITICAL` finding
When the builder scans each bundle with the same scanner image digest and scanner version
Then for every case the builder's `static_scans.verdict`, `score`, `recommendation` and `coverage` equal the platform report's values
And for every case the builder's `findings` array equals the platform report's findings reduced to the keys `severity`, `rule`, `file` and `line`, in the same order
And the parity test reports `5 passed, 0 failed`

#### Scenario: A report from a different scanner version is rejected instead of compared
Given the pinned `bheembhai-skillscan` version is `1.6.0`
And a scanner writes a valid-looking report with `"scanner_version":"1.7.0"` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
When the scan reaches a terminal state
Then `SELECT state, verdict, score, recommendation, coverage, findings, error FROM static_scans WHERE content_sha = 'b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a'` returns exactly `failed | failed | NULL | NULL | NULL | [] | scanner_version_mismatch`
And `readiness_scan_outcome('b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a', 'static')` returns `failed`

### Covered requirements (traceability)
- FR-091

### Out of scope
The platform's own scan implementation and its verdict rules; the LLM scan and its model identity (epic BSB-32); the scanner's internal SkillSpector rules; the report display (BSB-31-PENDING-6); the CI workflow that runs the static check on pull requests (the repo's `ci.yml`, outside this epic).

### Notes / dependencies
- Depends on BSB-31-PENDING-1 and BSB-31-PENDING-3 for the scan adapter and the builder's
  verdict, and on the pinned scanner image and package version from `kit.json`.
- The parity fixture's platform reports are recorded outside this repo from the platform's
  scanner at the same image digest and `bheembhai-skillscan` version; the fixture is data, not a
  second implementation. A parity failure names the case and the first differing field.
- The `accepted-critical` case is the FR-081 check: the platform report marks the critical finding
  accepted and recommends `INSTALL`, and the builder must still record `failed`.
- Because the reuse key includes `image_digest`, a kit update re-scans unchanged content instead
  of reusing a result from a different scanner version; that is what keeps this parity claim true
  over time.

---

## STORY: BSB-31-PENDING-6

**Summary:** Show the static scan score, recommendation and findings
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author**, I want **the static scan report to show its score, its recommendation and each finding's severity, rule, file and line**, so that **I can see what the scanner found and where to fix it**.

### Acceptance Criteria

#### Scenario: The report shows the score and the scanner's recommendation
Given scan `17` is `completed` with `verdict` `failed`, `score` `63`, `recommendation` `INSTALL` and `coverage` `complete`
And build `7`'s head is `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e` with bundle content `a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9`
When Ada sends `GET https://builder.skillbuilder.internal/api/scans/17` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: application/json`
And the response body equals exactly `{"scan_id":17,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e","content_sha":"a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9","state":"completed","verdict":"failed","score":63,"recommendation":"INSTALL","coverage":"complete","error":null,"scanner_version":"1.6.0","image_digest":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d","findings":[{"severity":"CRITICAL","rule":"SP-0042","file":"skills/sdlc-fix-bug-triage/SKILL.md","line":17},{"severity":"HIGH","rule":"SP-0090","file":"skills/sdlc-fix-bug-triage/templates/report.md","line":4},{"severity":"MEDIUM","rule":"SP-0117","file":"skills/sdlc-fix-bug-triage/references/run.md","line":8}]}`
And `GET https://builder.skillbuilder.internal/builds/7` contains `<div id="static-scan-score">Score: 63/100</div>` and `<div id="static-scan-recommendation">Recommendation: INSTALL</div>`

#### Scenario: The report lists each finding's severity, rule, file and line
Given scan `17` has the three findings above
And build `7`'s head is `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e` with bundle content `a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9`
When Ada reads `GET https://builder.skillbuilder.internal/api/scans/17`
Then the `findings` array has exactly three entries in the order `CRITICAL SP-0042 skills/sdlc-fix-bug-triage/SKILL.md 17`, `HIGH SP-0090 skills/sdlc-fix-bug-triage/templates/report.md 4`, `MEDIUM SP-0117 skills/sdlc-fix-bug-triage/references/run.md 8`
And every entry has exactly the keys `severity`, `rule`, `file` and `line`
And the build page's `<table id="static-scan-findings">` has one table row per entry, whose four cells are exactly that entry's `severity`, `rule`, `file` and `line`

#### Scenario: A passing scan with no findings shows an empty list
Given scan `12` is `completed` with `verdict` `passed`, `score` `100`, `recommendation` `INSTALL` and `findings` `[]`
When Ada sends `GET https://builder.skillbuilder.internal/api/scans/12`
Then the response body has `"score":100`, `"recommendation":"INSTALL"` and `"findings":[]`
And the build page's `<table id="static-scan-findings">` has exactly one row with the text `No findings`

#### Scenario: An unknown scan id is not found
Given Ada is a current member of the `skill-builders` group
When Ada sends `GET https://builder.skillbuilder.internal/api/scans/999` carrying the `sb_session` cookie
Then the response is HTTP 404 with `Content-Type: application/json` and body exactly `{"error":{"code":"not_found","message":"Scan not found"}}`

#### Scenario: A build with no scan shows the not-scanned state
Given build `7`'s `head_sha` is `2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c`
And no `skill_bundles` row and no terminal `static_scans` row exist for that commit and `sdlc-fix-bug-triage`
When Ada sends `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the page's `<section id="static-scan-report">` contains the exact text `Score: Not scanned` and `Recommendation: Not scanned`
And `<table id="static-scan-findings">` has exactly one row with the text `No scan`

### Covered requirements (traceability)
- FR-089
- FR-154
- FR-155

### Out of scope
The run page's Security tab (epic BSB-33, FR-157); the LLM scan's model identity and findings (epic BSB-32); the readiness panel's four-check rows (epic BSB-30, FR-070); the scanner's raw report format (the adapter); changing a finding or its severity (the scanner package).

### Notes / dependencies
- Depends on BSB-31-PENDING-1 and BSB-31-PENDING-3 for the stored row and its values, and on
  epic BSB-20's build page for the section and epic BSB-21 for `builds.head_sha`.
- The report shows the scanner's own `score` and `recommendation`, not a builder-computed value;
  the builder's `verdict` is a separate field so a report can show `Recommendation: INSTALL` with
  `verdict` `failed`.
- `findings` is ordered by severity rank, then file, then line, and the page uses the same order.
- A `failed` scan (timeout, malformed report, digest mismatch or version mismatch) has `score`,
  `recommendation` and `coverage` `null`, `findings` `[]` and the `error` code; the page shows
  `Score: Not scanned`, `Recommendation: Not scanned`, the `error` code and the `No findings` row.
- The build page's section renders the latest terminal scan for the current head's bundle content
  SHA; a scan for an older head is never shown for the current head.

---

## STORY: BSB-31-PENDING-7

**Summary:** Start a static-only scan from the skill page without a run
**Epic:** BSB-31 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-11, MVP

### Story
As a **skill author who is a member of a test project**, I want **to start a static-only scan for a build from its skill page without starting a run**, so that **I can check the skill's security before spending a run**.

### Acceptance Criteria

#### Scenario: A project member starts a static-only scan from the build page
Given Ada is a current member of the `skill-builders` group and a member of project `7`
And build `7`'s head is `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` with bundle content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And no terminal or live `static_scans` row exists for that content and image digest
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` carrying the `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"static"}`
Then the response is HTTP 202 with `Content-Type: application/json` and body exactly `{"scan_id":21,"state":"queued","build_id":7,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a"}`
And `SELECT run_id, build_id, state FROM static_scans WHERE id = 21` returns exactly `NULL | 7 | queued`
And `SELECT count(*) FROM runs` returns `10`
And no catalog branch is created and no Docker container labelled `bb.run_id` exists
And `GET https://builder.skillbuilder.internal/builds/7` contains `<button id="static-scan-start">Run static scan</button>`

#### Scenario: A started static-only scan completes without starting a run
Given scan `21` is `queued` for build `7` and content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And `SELECT count(*) FROM runs` returns `10`
When the scanner completes with a passing report
Then `GET https://builder.skillbuilder.internal/api/scans/21` returns `"state":"completed"` and `"verdict":"passed"`
And `SELECT count(*) FROM runs` returns `10`
And no Docker container labelled `bb.run_id` exists

#### Scenario: A user who is not a project member cannot start the scan
Given Alan is a current member of the `skill-builders` group and is not a member of project `7`
When Alan sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` carrying his `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"static"}`
Then the response is HTTP 403 with body exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM static_scans` returns `0` and no scanner container starts

#### Scenario: An unknown project is not found before membership is checked
Given Ada is a current member of the `skill-builders` group
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/999/scans` carrying the `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":7,"kind":"static"}`
Then the response is HTTP 404 with body exactly `{"error":{"code":"project_not_found","message":"Project 999 does not exist."}}`

#### Scenario: An unknown build is not found after the project check passes
Given Ada is a member of project `7`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` carrying the `sb_session` cookie with `Content-Type: application/json` and body exactly `{"build_id":999,"kind":"static"}`
Then the response is HTTP 404 with body exactly `{"error":{"code":"not_found","message":"Build not found"}}`
And `SELECT count(*) FROM static_scans` returns `0`

#### Scenario: A missing build id is refused
Given Ada is a member of project `7`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` carrying the `sb_session` cookie with `Content-Type: application/json` and body exactly `{"kind":"static"}`
Then the response is HTTP 422 with body exactly `{"error":{"code":"build_id_required","message":"A build_id is required."}}`

#### Scenario: Starting a scan for already-scanned content reuses the result
Given scan `12` is `completed` with `verdict` `passed` for content `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And the scanner stub records every container start
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/scans` with body exactly `{"build_id":7,"kind":"static"}`
Then the response is HTTP 202 with body exactly `{"scan_id":12,"state":"completed","build_id":7,"skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a"}`
And the scanner stub records no new container start

### Covered requirements (traceability)
- FR-092

### Out of scope
The LLM stage and a full security scan (epic BSB-32, FR-093); run start and the run's own static gate (epics BSB-24 and BSB-27); project creation, project listing and membership management (epic BSB-22); the build page's other sections (epics BSB-20 and BSB-21); the CLI's `scan --static-only` command (epic BSB-37); the scanner's internal rules and report format (the scanner package); the report display (BSB-31-PENDING-6).

### Notes / dependencies
- Depends on epic BSB-18 for the member session and group gate, on epic BSB-22 for project
  resolution and membership, on epic BSB-21 for `builds.head_sha`, and on epic BSB-25 for packing
  the build head's bundle. It consumes BSB-31-PENDING-1 for the scan and BSB-31-PENDING-2 for
  reuse.
- **Boundary for review — project picker.** The build page's control needs the caller's projects
  to choose the test project FR-092 requires. Epic BSB-22 owns the `projects` and
  `project_members` rows but its stories do not define a project-list endpoint or page. If BSB-22
  does not add one, the control takes a numeric `project_id` instead of a picker; the scan API and
  every scenario above do not change.
- The route is `POST /api/projects/{project_id}/scans` so that membership is checked before the
  request body, in the same order as epic BSB-22's other project routes. The build id is in the
  body because the page is build-scoped.
- A static-only scan is asynchronous: the response is `202` with the scan id and the author reads
  the report through `GET /api/scans/{scan_id}`. It creates no `runs` row, no run branch, no
  baseline and no agent container; only the scanner container runs.
- `kind` defaults to `static`; this epic accepts only `static`. Epic BSB-32 adds `full` to the
  same route and runs the static stage first.
- The button is the only new build-page control this epic adds (`static-scan-start`); the report
  section is BSB-31-PENDING-6's.
