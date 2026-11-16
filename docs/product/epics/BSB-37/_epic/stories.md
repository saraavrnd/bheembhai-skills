# Stories — BSB-37 (Command line & saved suites)

Source: Jira epic **BSB-37** — *Command line & saved suites* (feature area FA-16, release mixed,
labels FA-16, mixed; status To Do), fetched read-only from the Atlassian project
`bheembhai-skill-builder` through its REST API; its summary, description, functional scope, goal,
stated edge cases and covered-requirement list are the same as the BSB-37 section of
`docs/product/epics.md`. The requirement IDs mapped to the epic are in `docs/product/epic-map.json`.

Epic BSB-37 covers 8 requirements. They decompose into the 7 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-37`), is epic
**BSB-37**. The Atlassian MCP entry in `.mcp.json` is not usable in this session: its `args` value
is a string where Claude Code requires an array, so no Jira MCP tools were offered and the epic was
fetched read-only through the Atlassian REST API with the same credentials. Nothing was written to
Jira.

## Coverage summary

| Requirement | Covered by | Release |
|-------------|------------|---------|
| FR-116 | BSB-37-PENDING-1 | MVP |
| FR-117 | BSB-37-PENDING-2 | MVP |
| FR-118 | BSB-37-PENDING-3 | MVP |
| FR-119 | BSB-37-PENDING-4 | Later |
| FR-120 | BSB-37-PENDING-4 | Later |
| FR-121 | BSB-37-PENDING-5 | Later |
| FR-122 | BSB-37-PENDING-6 | Later |
| FR-123 | BSB-37-PENDING-7 | Later |

The epic's three stated edge cases are covered explicitly: the command line uses the same authoring
identity and `skill-builders` gate as the web (BSB-37-PENDING-1) and the same project-membership
check (BSB-37-PENDING-1, BSB-37-PENDING-2 and BSB-37-PENDING-3); a scan command uses the same
project membership check as the web scan (BSB-37-PENDING-2 and BSB-37-PENDING-3); and a nightly
suite records a `not_started` result for an entry that cannot start (BSB-37-PENDING-7). The
non-goals are respected: no workflow orchestration or gating, and no command-line administration of
users, groups or projects.

## CLI, suite and nightly-run contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control and scan fixture
unless it says otherwise. The member session, the local `users` rows and the `skill-builders` gate
are established by epic BSB-18. The project, `projects` rows and `project_members` rows are
established by epic BSB-22. The run-start route, its validation and its `runs` row are established
by epic BSB-24; the bundle and skills-commit resolution are epic BSB-25's. The static scan service,
its cache and its `static_scans` row are epic BSB-31's; the LLM scan service is epic BSB-32's. The
run's terminal state is epic BSB-26's and `runs.final_verdict` is epic BSB-29's. The `runs` and
`suites` columns follow `docs/adr/SK-001-skill-builder.md` §5, §7 and §9. The nightly suite
scheduler is this epic's; it is an installation-level job separate from epic BSB-28's nightly Jira
sweep.

**Fixture constants.**

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z` |
| Current time | `2026-11-15T10:00:00Z` unless a scenario sets a clock |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace`; her token's `cognito:groups` is `["skill-builders"]` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper`; her token's `cognito:groups` is `["skill-builders"]` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing`; his token's `cognito:groups` is `["skill-builders"]`; he has no `project_members` row for project `7` or project `8` |
| User Mallory | `users.id` = `45`, `cognito_sub` = `d4e5f6a7-0000-0000-0000-000000000004`, `email` = `mallory@example.com`, `name` = `Mallory Trell`; her token's `cognito:groups` is `["catalog-reviewers"]` |
| `users` fixture | exactly four rows, the users above |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42`, `created_at` = `2026-11-14T09:00:00Z`, `llm_scan_model_profile_id` = `3` and `llm_scan_tier` = `medium`; id `8` has `name` = `Search smoke`, `owner_id` = `43`, `created_at` = `2026-11-14T09:05:00Z` and no LLM-scan setting; ids `1` to `6`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)` |
| `runs`, `suites`, `suite_runs`, `suite_run_entries` fixture | exactly zero rows before each scenario unless the scenario states the rows it starts from |
| Catalog repository | `saraavrnd/bheembhai-skills`; branches `build/sdlc-fix-bug-triage`, `main`, `test/ada/fix-reproduce`, `test/ada/fix-reproduce-2` and `test/grace/fix-reproduce` all exist |
| Sandbox repository | `saraavrnd/bheembhai-skill-fixtures`, from project `7`'s `github` integration; its base branch is `main`; branches `fixtures/blocked-handoff`, `fixtures/empty-title`, `main` and `test/ada/run-7-output` all exist |
| Skills present | `sdlc-fix-bug-triage` exists at `skills/sdlc-fix-bug-triage/SKILL.md` on every catalog branch above |
| Workflow config on the catalog branches | `config/bug-fix.yaml` declares workflow `bug-fix` with steps `triage`, `reproduce`, `root-cause`, `implement`; `config/smoke.yaml` declares workflow `smoke` with step `triage` |
| `github` integration (project 7) | row `id` = `6`, `project_id` = `7`, `kind` = `github`, `config` = `{"repo":"saraavrnd/bheembhai-skill-fixtures","base_branch":"main"}`, `secret_ref` = `skill-builder/7/github`, `mcp` = `null`, `verified_at` = `2026-11-14T09:02:00Z` |
| `ai_model` integration (project 7) | row `id` = `7`, `project_id` = `7`, `kind` = `ai_model`, `config` = `{"profiles":[{"id":3,"name":"Anthropic test","vendor":"anthropic","base_url":"https://api.anthropic.test","tiers":{"high":"test-model-high","medium":"test-model-medium"}},{"id":4,"name":"Smoke","vendor":"anthropic","base_url":"https://api.anthropic.test","tiers":{"medium":"test-model-medium"}}]}`, `secret_ref` = `skill-builder/7/ai_model`, `mcp` = `null`, `verified_at` = `2026-11-14T09:03:00Z` |
| Project 7 LLM-scan setting | `llm_scan_model_profile_id` = `3` and `llm_scan_tier` = `medium`, so the LLM scan model is `test-model-medium` (BSB-32's columns) |
| `kit.json` for `kit-v8` | `{"kit":"kit-v8","env_contract_version":"4","bheembhai-stepkit":"0.5.0","bheembhai-verify":"2.2.0","bheembhai-skillscan":"1.6.0","agent_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-agent@sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13","scanner_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-skillscan@sha256:4c9d2e7f1a3b5c8e0d2f4a6b8c1e3d5f7a9b2c4d6e8f0a1b3c5d7e9f2a4b6c8d"}` |
| Skills commit for `test/ada/fix-reproduce` | `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` |
| Bundle content SHA for `(sdlc-fix-bug-triage, test/ada/fix-reproduce)` | `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` |
| Skills commit for `test/ada/fix-reproduce-2` | `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e` |
| Bundle content SHA for `(sdlc-fix-bug-triage, test/ada/fix-reproduce-2)` | `d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5` |
| Existing completed static scan | `static_scans` row `id` = `12`, `skill` = `sdlc-fix-bug-triage`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `content_sha` = `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`, `image_digest` = the scanner image digest above, `state` = `completed`, `verdict` = `passed`, `score` = `100`, `recommendation` = `INSTALL`, `coverage` = `complete`, `findings` = `[]`, `scanner_version` = `1.6.0`, `run_id` = `NULL`, `build_id` = `NULL`, `llm_stage` = `false`; present only in a scenario that says so |
| Scanner stub | records every container start, its image digest, mounts, network policy, environment and args, and writes the report the scenario states |
| Builder HTTP stub | records every request's method, path, headers and body |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |

**Command-line contract.** The CLI is `python -m skill_builder.runner`. It is a thin HTTP client of
the same builder: it sends the same `sb_session` cookie the browser sends, so every request passes
epic BSB-18's session gate and `skill-builders` group gate unchanged, and every project route passes
epic BSB-22's project-membership check unchanged. The CLI never opens the database directly and
never bypasses a gate.

| Item | Exact value |
|------|-------------|
| Base URL variable | `SKILL_BUILDER_URL`, optional; default `https://builder.skillbuilder.internal` |
| Session variable | `SKILL_BUILDER_SESSION`, required; its value is the Cognito ID token JWT and is sent as the header `Cookie: sb_session=` followed by that token |
| Run command | `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --input main --model-profile 3 --tier high` |
| Run command with context | the same command plus `--context '{"workflow":"bug-fix","step":"triage"}'` |
| Static-only scan command | `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --static-only` |
| Full scan command | `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce` |
| Run success output | the run API's exact JSON response body on stdout followed by one newline; stderr empty; exit code `0`; nothing else on stdout |
| Refusal output | exactly `skill_builder: ` followed by the API's `code`, `: `, then the API's `message`, on stderr followed by one newline; stdout empty; exit code `1` |
| Usage or configuration error | exactly `skill_builder: ` followed by the message below, on stderr followed by one newline; stdout empty; exit code `2`; no HTTP request |
| Missing session message | `SKILL_BUILDER_SESSION is not set` |
| Missing project message | `--project is required` |
| Missing skill message | `--skill is required` |
| Missing skills branch message | `--skills-ref is required` |
| Missing input branch message | `--input is required` |
| Missing model profile message | `--model-profile is required` |
| Missing tier message | `--tier is required` |
| Context parse message | `--context must be a JSON object` |
| Poll interval and limit | the scan commands poll every 1 second and give each scan stage 600 seconds, matching the scanner container's ten-minute limit |

**Run command request.** The run command sends exactly one request:
`POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json`
and the `Cookie: sb_session=` header carrying the session token. Its body is compact JSON with keys in exactly this
order: `skill`, `skills_ref`, `input_branch`, `model_profile_id`, `tier`, and then `context` only
when `--context` is supplied. This is byte-for-byte the body epic BSB-24's web run-start form sends
for the same values. The response and the `runs` row are epic BSB-24's, unchanged.

**Scan command requests.** The scan commands cannot use epic BSB-31's and BSB-32's build-based
route because the CLI has a skill and a skills branch, not a `build_id`. This epic adds two thin
CLI adapter routes over the same scan services and the same content-addressed cache:

- `POST https://builder.skillbuilder.internal/api/projects/7/scans/by-ref` with
  `Content-Type: application/json` and body exactly
  `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","kind":"static"}` for the
  static-only command, or exactly
  `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","kind":"full"}` for the
  full command.
- `GET https://builder.skillbuilder.internal/api/projects/7/scans/by-ref/21` to read the CLI
  scan's state.

Both routes apply, in this order: epic BSB-18's session gate (401 `authentication_required`), its
group gate (403 `not_a_member`), project resolution (404 `project_not_found`), project membership
(403 `project_membership_required`), request-body validation (422), skills-branch resolution and
bundle packing (422 `skills_branch_not_found`), then the scan start. A successful start is HTTP 202
with `Content-Type: application/json` and exactly:

```
{"scan_id":21,"state":"queued","kind":"static","skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a"}
```

for `kind` = `static`, and exactly:

```
{"scan_id":21,"state":"queued","kind":"full","skill":"sdlc-fix-bug-triage","skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","content_sha":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a","llm_scan_id":null}
```

for `kind` = `full`, where `llm_scan_id` is the existing LLM row's id when one already exists for
the content and the project's LLM-scan setting, otherwise `null`, matching epic BSB-32. When a
completed or running static row already exists for the same
`(content_sha, image_digest)`, the same shape carries that row's `scan_id` and `state` and no second
container starts. The by-ref start creates no `runs` row, no catalog branch, no baseline for a run
and no agent container; it records `static_scans.run_id` and `static_scans.build_id` as `NULL`
because it has no build requester.

The by-ref start's own body errors are `skill` missing or empty (422 `{"error":{"code":"skill_required","message":"A skill is required."}}`),
`skills_ref` missing or empty (422 `{"error":{"code":"skills_ref_required","message":"A skills branch is required."}}`),
and `kind` missing or not `static` or `full` (422 `{"error":{"code":"kind_invalid","message":"kind must be static or full."}}`).
Unknown body keys are ignored. The `skills_branch_not_found` body is epic BSB-24's; the
`authentication_required`, `not_a_member`, `project_not_found` and `project_membership_required`
bodies are epics BSB-18's and BSB-22's.

The status route returns HTTP 200 with `Content-Type: application/json` and exactly:

```
{"scan_id":21,"kind":"static","state":"completed","verdict":"passed","llm_scan_id":null,"llm_state":null}
```

For a `kind` = `full` scan the same object has `kind` = `full`; once the static stage has passed and
the LLM row exists, `llm_scan_id` is that row's id and `llm_state` is that row's state, where the
row is the latest `llm_scans` row for the scan's `content_sha` by `created_at` then `id` (epic
BSB-30's selection rule). A full scan whose static stage did not pass keeps `llm_scan_id` and
`llm_state` `null`. A static row with `state` = `failed` has `verdict` = `failed`, `llm_scan_id` =
`null` and `llm_state` = `null`.

The CLI's scan output is one line on stdout:

| Terminal outcome | Exact stdout line | Exit |
|------------------|-------------------|------|
| static completed, verdict `passed` | `scan 21: completed verdict=passed` | 0 |
| static completed, verdict `failed` | `scan 21: completed verdict=failed` | 1 |
| static `failed` | `scan 21: failed error=scanner_failed` | 1 |
| full, static passed, LLM `complete` | `scan 21: completed verdict=passed llm_scan=51 llm_state=complete` | 0 |
| full, static passed, LLM `unavailable` | `scan 21: completed verdict=passed llm_scan=51 llm_state=unavailable` | 0 |
| full, static verdict `failed` | `scan 21: completed verdict=failed llm_scan=none` | 1 |

An LLM scan that is `unavailable` never changes the exit code: FR-118 runs the scan, and epic
BSB-32's rule is that the LLM stage never refuses a run. A static `failed` verdict or a static row
`state` = `failed` exits `1`.

**`suites` table (ADR §9, extended by this epic).**

| Column | Type and value |
|--------|----------------|
| `id` | serial primary key; the first saved suite is `1` |
| `project_id` | integer, the owning project |
| `name` | text, non-empty after trimming, at most 100 characters, unique per project |
| `definition` | JSONB, the exact entry object below |
| `source_path` | text NULL; `NULL` for a suite saved through the builder, because this epic writes no repository file for a suite |
| `created_by` | integer, the `users.id` of the author who saved the suite (additive column) |
| `nightly` | boolean NOT NULL DEFAULT `false` (additive column) |
| `next_run_at` | timestamptz NULL; the next `02:00:00Z` at which the suite is due (additive column) |

A unique constraint on `(project_id, name)` is the system of record for FR-119's "named" suite: the
name is unique within one project and may repeat in another project.

**Suite definition.** `suites.definition` is exactly an object with one key `entries`, an array of
1 to 50 objects. Each entry object has exactly these seven keys, in this order:

| Key | Rule |
|-----|------|
| `skill` | non-empty string; that skill's own `skills/sdlc-fix-bug-triage/SKILL.md`-style path must exist on the entry's `skills_ref` branch |
| `skills_ref` | non-empty string naming a branch of `saraavrnd/bheembhai-skills` |
| `input_branch` | non-empty string naming a branch of the project's sandbox repository |
| `context` | JSON object with the same allowed keys and rules as epic BSB-24's `context` |
| `expectations` | JSON object stored unchanged; this epic does not evaluate it |
| `model_profile_id` | positive JSON integer; a profile `id` in the project's `ai_model` integration |
| `tier` | non-empty string; a key of the selected profile's `tiers` mapping |

FR-120 names `skill`, `input_branch`, `context` and `expectations`. The other three keys are the
run inputs epic BSB-24 requires for every run; a suite entry that omitted them could not start a
run. Decision 1 records this addition.

**Suite save API.** `POST https://builder.skillbuilder.internal/api/projects/7/suites` with
`Content-Type: application/json` and a body with exactly the keys `name` and `entries`, in that
order. The `entries` array holds the entry objects above. A successful save is HTTP 201 with
`Content-Type: application/json` and exactly:

```
{"id":1,"project_id":7,"name":"Nightly bug-fix","created_by":42,"nightly":false,"next_run_at":null,"source_path":null,"definition":{"entries":[{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","context":{"workflow":"bug-fix","step":"triage"},"expectations":{"final_verdict":"completed"},"model_profile_id":3,"tier":"high"}]}}
```

Validation order on the save route is fixed: epic BSB-18's session gate (401), its group gate (403),
project resolution (404), project membership (403), body shape (422), suite name (422 or 409), each
entry's fields in entry order (422), then each entry's branch, workflow and model resolution in
entry order (422). A refused save creates no `suites` row.

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| project `999` does not exist | 404 | `{"error":{"code":"project_not_found","message":"Project 999 does not exist."}}` |
| the caller is not a project member | 403 | `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}` |
| `name` is missing, empty or whitespace only | 422 | `{"error":{"code":"suite_name_required","message":"A suite name is required."}}` |
| `name` is longer than 100 characters | 422 | `{"error":{"code":"suite_name_too_long","message":"A suite name must be at most 100 characters."}}` |
| a suite with the same name exists in the project | 409 | `{"error":{"code":"suite_name_taken","message":"Suite 'Nightly bug-fix' already exists in project 7."}}` |
| `entries` is missing, is not an array, or is empty | 422 | `{"error":{"code":"entries_required","message":"A suite must contain at least one entry."}}` |
| `entries` has more than 50 items | 422 | `{"error":{"code":"entries_too_many","message":"A suite may contain at most 50 entries."}}` |
| an entry is not a JSON object | 422 | `{"error":{"code":"entry_invalid","message":"Entry 0 must be a JSON object."}}` |
| an entry is missing a required key | 422 | `{"error":{"code":"entry_field_required","message":"Entry 0 is missing input_branch."}}` |
| an entry has an unknown key | 422 | `{"error":{"code":"entry_field_unknown","message":"Entry 0 contains unknown key 'foo'."}}` |
| `skill` is empty | 422 | `{"error":{"code":"entry_skill_required","message":"Entry 0 must name a skill."}}` |
| `skills_ref` is empty | 422 | `{"error":{"code":"entry_skills_ref_required","message":"Entry 0 must name a skills branch."}}` |
| `input_branch` is empty | 422 | `{"error":{"code":"entry_input_branch_required","message":"Entry 0 must name an input branch."}}` |
| `context` is not a JSON object | 422 | `{"error":{"code":"entry_context_invalid","message":"Entry 0 context must be a JSON object."}}` |
| `expectations` is not a JSON object | 422 | `{"error":{"code":"entry_expectations_invalid","message":"Entry 0 expectations must be a JSON object."}}` |
| `model_profile_id` is missing or not a positive integer | 422 | `{"error":{"code":"entry_model_profile_invalid","message":"Entry 0 model_profile_id must be a positive integer."}}` |
| `tier` is empty | 422 | `{"error":{"code":"entry_tier_required","message":"Entry 0 must name a model tier."}}` |
| `skills_ref` names no catalog branch | 422 | `{"error":{"code":"skills_branch_not_found","message":"Skills branch 'test/ada/missing' does not exist."}}` |
| `input_branch` names no sandbox branch | 422 | `{"error":{"code":"input_branch_not_found","message":"Input branch 'fixtures/missing' does not exist."}}` |
| `skill` is absent from the skills branch | 422 | `{"error":{"code":"skill_not_found","message":"Skill 'sdlc-fix-bug-missing' does not exist on skills branch 'test/ada/fix-reproduce'."}}` |
| `context.workflow` or `context.step` is invalid | 422 | epic BSB-24's exact `workflow_not_found` or `step_not_found` body |
| `model_profile_id` is not a profile of the project | 422 | `{"error":{"code":"model_profile_not_found","message":"Model profile 99 does not exist in project 7."}}` |
| `tier` is not mapped by the profile | 422 | `{"error":{"code":"model_tier_not_mapped","message":"Model profile 3 has no model mapping for tier 'low'."}}` |

**Suite read API and page.** `GET https://builder.skillbuilder.internal/api/projects/7/suites/1`
returns HTTP 200 with `Content-Type: application/json` and the same object as the save response. The
suite list page `GET https://builder.skillbuilder.internal/projects/7/suites` returns HTTP 200 with
`Content-Type: text/html; charset=utf-8` and contains
`<a id="suite-1" href="/projects/7/suites/1">Nightly bug-fix</a>` and
`<span id="suite-1-nightly">Nightly: Off</span>`. The suite detail page
`GET https://builder.skillbuilder.internal/projects/7/suites/1` contains one row per suite entry
with the exact entry `skill`, `input_branch`, `context` and `expectations`. These routes apply epic
BSB-18's gates and epic BSB-22's project-membership check.

**Suite run API.** `POST https://builder.skillbuilder.internal/api/projects/7/suites/1/runs` with
`Content-Type: application/json` and body exactly `{}`. A successful manual run is HTTP 202 with
`Content-Type: application/json` and exactly:

```
{"suite_run_id":1,"suite_id":1,"project_id":7,"trigger":"manual","state":"running","entries":[{"entry_index":0,"skill":"sdlc-fix-bug-triage","run_id":1,"status":"started"},{"entry_index":1,"skill":"sdlc-fix-bug-triage","run_id":2,"status":"started"}]}
```

Validation order on this route is fixed: epic BSB-18's session gate (401), its group gate (403),
project resolution (404), project membership (403), suite resolution (404), body shape (422), then
every entry through epic BSB-24's run-start validation in entry order. A manual run is
all-or-nothing: if any entry is invalid, the route returns HTTP 422 `suite_entry_invalid`, creates
no `suite_runs` row, no `suite_run_entries` row and no `runs` row, and starts no run. If every entry
is valid, it creates one `suite_runs` row, one `suite_run_entries` row per entry in entry order and
one `runs` row per entry through epic BSB-24's route contract; the `runs.user_id` is the calling
user's `users.id`, and `runs.id` values are assigned in entry order starting at `1`.

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| the suite does not exist in the project | 404 | `{"error":{"code":"suite_not_found","message":"Suite 1 not found in project 7."}}` |
| the body is not the empty JSON object | 422 | `{"error":{"code":"invalid_request","message":"The request body must be an empty JSON object."}}` |
| an entry fails epic BSB-24's start validation | 422 | `{"error":{"code":"suite_entry_invalid","message":"Entry 1 cannot start: Input branch 'fixtures/blocked-handoff' does not exist."}}` |

The `suite_entry_invalid` message is exactly `Entry ` + the zero-based entry index + ` cannot start: `
+ epic BSB-24's exact message for that entry.

**Schedule API.** `PUT https://builder.skillbuilder.internal/api/projects/7/suites/1/schedule`
with `Content-Type: application/json` and body exactly `{"nightly":true}` or
`{"nightly":false}`. A successful change is HTTP 200 with `Content-Type: application/json` and
exactly:

```
{"suite_id":1,"project_id":7,"nightly":true,"next_run_at":"2026-11-16T02:00:00Z"}
```

for `nightly` = `true`, and exactly:

```
{"suite_id":1,"project_id":7,"nightly":false,"next_run_at":null}
```

for `nightly` = `false`. `next_run_at` is the next `02:00:00Z` strictly after the current time; at
the fixture clock `2026-11-15T10:00:00Z` it is `2026-11-16T02:00:00Z`. The route applies epic
BSB-18's gates, epic BSB-22's project membership and suite resolution, then body validation. The
only schedule this epic supports is the nightly one; there is no cron expression and no per-day
configuration.

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| the suite does not exist in the project | 404 | `{"error":{"code":"suite_not_found","message":"Suite 1 not found in project 7."}}` |
| `nightly` is missing or is not a JSON boolean | 422 | `{"error":{"code":"nightly_invalid","message":"nightly must be a JSON boolean."}}` |
| the body has a key other than `nightly` | 422 | `{"error":{"code":"schedule_body_invalid","message":"The body must contain exactly the key nightly."}}` |

**Nightly scheduler.** An installation-level job runs every day at `02:00 UTC`. At each run it
selects every `suites` row with `nightly` = `true` and `next_run_at` less than or equal to the job's
current time. For each selected suite it creates exactly one `suite_runs` row with `trigger` =
`nightly`, `scheduled_for` = the UTC date of the job (`2026-11-16`), `state` = `running`,
`created_at` = the job time and `finished_at` = `NULL`, then creates one `suite_run_entries` row per
suite entry in entry order with `status` = `pending` and `run_id` = `NULL`, then attempts each entry
in entry order through epic BSB-24's run-start validation. A unique constraint on
`(suite_id, scheduled_for)` for `trigger` = `nightly` makes the job idempotent: if a `suite_runs`
row already exists for that suite and date, the job creates no second row, no entry rows and no
runs, and still advances `suites.next_run_at` to the next day's `02:00:00Z`, exactly as a first
processing would. After a suite is processed, `suites.next_run_at` is the next day's `02:00:00Z`
(`2026-11-17T02:00:00Z`).

The job is an internal installation job and holds no user session. It calls the same run-start
validation and `runs`-row service the route calls, with `suites.created_by` as the acting user, so
it performs the same project, field, integration, branch, workflow and model checks without a
session gate that has no caller to pass. A run it creates has `runs.user_id` =
`suites.created_by`.

For an entry that passes validation, the job creates the `runs` row through that service, sets
`suite_run_entries.run_id` to the new run id and `status` = `started`, and leaves the run in
`queued`. For an entry that fails validation, the job sets `status` = `not_started`, `run_id` =
`NULL`, `error_code` to epic BSB-24's exact code and `error_message` to epic BSB-24's exact
message, and continues with the next entry. A nightly suite therefore records a result for every
entry even when no run can start.

**Result recording.** This epic adds two tables:

| Table | Columns |
|-------|---------|
| `suite_runs` | `id`, `suite_id`, `project_id`, `trigger` (`manual` or `nightly`), `scheduled_for` (date NULL for a manual run), `state` (`running` or `completed`), `created_at`, `finished_at` |
| `suite_run_entries` | `id`, `suite_run_id`, `entry_index`, `skill`, `skills_ref`, `input_branch`, `context`, `expectations`, `model_profile_id`, `tier`, `run_id` (NULL when not started), `status` (`pending`, `started`, `finished` or `not_started`), `result_state`, `result_final_verdict`, `error_code`, `error_message` |

When a run that is referenced by a `suite_run_entries.run_id` reaches a terminal `runs.state`
(`completed`, `failed_incomplete`, `failed_execution` or `failed_timeout`), the builder sets that
entry's `status` = `finished` and `result_state` = `runs.state` in the same transaction. The update
that writes `runs.final_verdict` also sets `result_final_verdict` = `runs.final_verdict`. A run
that is terminal before verification never gets a `runs.final_verdict` (epic BSB-29), so its
`result_final_verdict` stays `NULL` while its `result_state` is still recorded. A run's deadline
guarantees a terminal state (epic BSB-27, NFR-007), so every started entry eventually
finishes. A `suite_runs` row moves from `running` to `completed` when every one of its entries is
`finished` or `not_started`; its `finished_at` is the time the last entry resolved. An entry that
never started keeps `result_state` and `result_final_verdict` `NULL` and carries its exact
`error_code` and `error_message`.

The result API `GET https://builder.skillbuilder.internal/api/projects/7/suite-runs/1` returns
HTTP 200 with `Content-Type: application/json` and exactly:

```
{"suite_run_id":1,"suite_id":1,"project_id":7,"trigger":"nightly","scheduled_for":"2026-11-16","state":"completed","started_at":"2026-11-16T02:00:00Z","finished_at":"2026-11-16T02:05:00Z","entries":[{"entry_index":0,"skill":"sdlc-fix-bug-triage","input_branch":"main","run_id":1,"status":"finished","result_state":"completed","result_final_verdict":"completed","error_code":null,"error_message":null},{"entry_index":1,"skill":"sdlc-fix-bug-triage","input_branch":"fixtures/blocked-handoff","run_id":2,"status":"finished","result_state":"completed","result_final_verdict":"changes_requested","error_code":null,"error_message":null}]}
```

The result's `started_at` is the `suite_runs.created_at` value; `scheduled_for` is the ISO date for
a nightly run and `null` for a manual run.

The suite detail page
`GET https://builder.skillbuilder.internal/projects/7/suites/1` contains a
`<section id="suite-runs">` with one table row per entry, keyed by entry index, in the form
`<tr id="suite-run-entry-0"><td>1</td><td>sdlc-fix-bug-triage</td><td>main</td><td>completed</td><td>completed</td></tr>`
and, for an entry that did not start,
`<tr id="suite-run-entry-1"><td>2</td><td>sdlc-fix-bug-triage</td><td>fixtures/missing</td><td>not started</td><td>input_branch_not_found</td></tr>`.
The five cells are, in order, the entry's 1-based position, the skill, the input branch, the
result state (or `not started`) and the final verdict (or the error code).
The section also contains `<div id="suite-run-state">State: Completed</div>` once the suite run
completes. The result API and the page apply epic BSB-18's gates and epic BSB-22's project
membership.

**No repository or platform write.** Saving a suite writes only the `suites` row; it writes no
`suites/*.yaml` file and no commit. Running, scheduling and recording a suite write only the
builder's own rows and start runs and scanner containers. This epic makes no platform API call and
writes no platform catalog, project or project skill, matching `docs/adr/SK-001-skill-builder.md`'s
no-platform-write rule.

## Decisions recorded in this decomposition (confirm at review)

1. **Suite entry carries the three run inputs FR-120 omits.** FR-120 names `skill`, `input_branch`,
   `context` and `expectations`; epic BSB-24's run start also requires `skills_ref`,
   `model_profile_id` and `tier`. This decomposition requires those three additional per-entry keys
   so every suite entry can start a run with no implicit default. If review prefers suite-level
   defaults, only the save validation and the stored `definition` change; the suite-run, schedule
   and result contracts do not.
2. **Suite storage.** The ADR §9 `suites` row is the durable system of record and `definition` JSONB
   holds the entries. `source_path` stays `NULL` for a builder-saved suite; this epic does not add a
   repository write or a `suites/*.yaml` export. If review prefers the YAML file as the source of
   truth, only the save adapter changes.
3. **Suite-run storage.** The ADR names no suite-run or per-entry result table. This decomposition
   adds `suite_runs` and `suite_run_entries`; the per-entry row is what makes FR-123's result and
   the epic's cannot-start edge case durable. If review prefers a JSONB result on `suites`, only the
   read shape changes.
4. **CLI transport.** The CLI is a thin HTTP client of the builder and sends the same `sb_session`
   cookie the browser sends. This reuses epic BSB-18's session and group gates and epic BSB-22's
   project-membership check exactly, and is what makes the CLI's identity, membership and
   refusal behaviour testable. Direct database access is rejected because it would bypass the gate.
   This reads `docs/adr/SK-001-skill-builder.md` §7's "runs the same runner without the web app" as
   the same runner and the same run path reached behind a CLI client, which is how the epic's
   implementation guidance puts it ("behind a CLI client with the same authentication and
   project-membership checks"), not as an unauthenticated local execution path that would have no
   authoring identity to gate.
5. **CLI scan adapter.** Epic BSB-31's and BSB-32's scan starts take a `build_id`, while the CLI has
   a skill and a skills branch. This decomposition adds
   `POST /api/projects/{project_id}/scans/by-ref` and its status route as thin adapters over the
   same scan services and the same content-addressed cache; there is no second scan
   implementation. If review prefers the CLI to require an existing build, only the adapter
   changes; the `static_scans` and `llm_scans` rows do not.
6. **Nightly trigger and identity.** The nightly scheduler is this epic's installation-level job,
   separate from epic BSB-28's nightly Jira sweep. A nightly run's `runs.user_id` is
   `suites.created_by`, because no human triggers it; a manual suite run uses the calling user.
7. **Manual versus nightly validation.** A manual suite run validates every entry before starting
   any, so a broken entry refuses the whole request with `suite_entry_invalid` and creates nothing.
   A nightly run cannot return an error to a person, so it records a `not_started` result per entry
   and continues. That difference is what satisfies the epic's "a nightly run must record a result
   even when it cannot start".
8. **Expectations are stored, not evaluated.** `expectations` is saved verbatim as a JSON object and
   shown with the entry; this epic records the run's actual `state` and `final_verdict` next to it
   but does not compute a pass or fail from the expectation, because no requirement defines one.
9. **Schedule shape.** Scheduling is a boolean nightly switch at a fixed `02:00 UTC`; this epic
   adds no cron expression, time zone, per-day schedule or notification.
10. **CLI run flags beyond the ADR signature.** `docs/adr/SK-001-skill-builder.md` §7 writes the
    run signature as `run --project --skill --skills-ref --input`; epic BSB-24's run start also
    requires `model_profile_id` and `tier` with no default. This decomposition adds the required
    `--model-profile` and `--tier` flags so the command can start a run at all. The two flags are
    passed through unchanged; the route's `model_profile_required`, `tier_required` and
    `model_tier_not_mapped` rules still apply. If review prefers a default profile and tier from
    the project, only the CLI's argument handling changes.

## Cross-epic notes

- **BSB-18 (session and group gate).** The CLI sends the same `sb_session` token as the browser, so
  every command, suite page, suite API, schedule API and result API passes the same session and
  `skill-builders` gates. A non-member never reaches a project or suite check.
- **BSB-22 (project membership).** Every run, scan, suite, schedule and result route applies the
  same project-membership check as the web. The CLI edge case in the epic is therefore the same
  check, not a second policy.
- **BSB-24 (run start).** The run command and every suite entry reuse the run-start route's request
  fields, validation order, error bodies and `runs` row contract. This epic adds no run-start
  validation of its own except the suite-entry wrapper `suite_entry_invalid` and the entry fields
  the suite schema carries.
- **BSB-25 (bundle and branch).** The scan adapter and every suite run resolve the skills branch to
  a commit SHA and pack or reuse the bundle through BSB-25's path; this epic adds no second packer.
- **BSB-26, BSB-27 and BSB-29 (run states and verdicts).** Result recording mirrors `runs.state` and
  `runs.final_verdict`; it does not invent a verdict or a terminal state. BSB-27's deadline makes a
  started entry's result eventual.
- **BSB-31 and BSB-32 (scans).** The CLI scan adapter calls the same static and LLM scan services
  and reuses their content-addressed rows. `--static-only` never sets `llm_stage` and never calls
  the LLM trigger; the full command does.
- **BSB-28 (nightly sweep).** The nightly suite scheduler is a separate job at the same `02:00 UTC`
  installation time. It records only suite rows and starts runs; it never touches Jira fixtures.
- **BSB-35 (history and compare).** This epic adds no history or compare view; a suite run is its
  own grouping and does not change BSB-35's run list.
- **BSB-36 (catalog submission).** This epic adds no submit command and no catalog pull request.
  A suite run is a test run, not a submission.
- **BSB-38 (accessibility).** The suite list, suite detail and result rows are new builder web
  surfaces; their keyboard, focus, contrast and 320-pixel reflow checks belong to BSB-38 and add no
  requirement here.

---

## STORY: BSB-37-PENDING-1

**Summary:** Start a test run from the command line under the same session, skill-builders and project-membership gates as the web
**Epic:** BSB-37 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-16, MVP

### Story
As a **skill author**, I want **to start a test run for a project from the command line using the same authoring identity and membership gate as the web interface**, so that **I can script runs and CI-style checks without a browser while every run stays attributable and permitted**.

### Acceptance Criteria

#### Scenario: The command line starts a run and prints the created run
Given Ada is signed in with a valid `sb_session` token and is a current member of the `skill-builders` group
And Ada is the owner of project `7`, which has a `github` integration and an `ai_model` integration with profile `3`
And the `runs` table has exactly zero rows
And `SKILL_BUILDER_URL` is `https://builder.skillbuilder.internal`
And `SKILL_BUILDER_SESSION` is Ada's exact ID token
When Ada runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --input main --model-profile 3 --tier high`
Then the builder HTTP stub records exactly one request, `POST https://builder.skillbuilder.internal/api/projects/7/runs`
And that request carries `Content-Type: application/json` and the `Cookie: sb_session=` header carrying Ada's exact ID token
And that request's body is exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
And the command exits with code `0`
And the command's stderr is empty
And the command's stdout is exactly `{"id":1,"project_id":7,"user_id":42,"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","context":{},"model_profile_id":3,"tier":"high","state":"queued","kind":"run","created_at":"2026-11-15T10:00:00Z"}` followed by one newline
And `SELECT project_id, user_id, skill, skills_ref, input_branch, model_profile_id, tier, state, kind FROM runs WHERE id = 1` returns exactly `7 | 42 | sdlc-fix-bug-triage | test/ada/fix-reproduce | main | 3 | high | queued | run`
And `SELECT context FROM runs WHERE id = 1` equals the JSON value `{}`

#### Scenario: The command line and the web form produce identical requests and run rows
Given two fresh copies of the fixture, each with the `runs` table containing exactly zero rows
And in copy A Ada submits the run-start form for project `7` with skill `sdlc-fix-bug-triage`, skills branch `test/ada/fix-reproduce`, input branch `main`, model profile `3` and tier `high`
And in copy B Ada runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --input main --model-profile 3 --tier high` with the same values and her token
When the builder HTTP stub's recorded request from copy A and its recorded request from copy B are compared
Then both requests have method `POST`, path `/api/projects/7/runs`, `Content-Type: application/json` and the same `Cookie` header value
And both request bodies are exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
And the `runs` row in copy A and the `runs` row in copy B have identical values on every column
And both requests are admitted with HTTP 201 and, in copy B, the command exits with code `0`

#### Scenario: A missing session is a usage error and makes no request
Given `SKILL_BUILDER_SESSION` is unset
And the builder HTTP stub has recorded zero requests
When Ada runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --input main --model-profile 3 --tier high`
Then the command exits with code `2`
And the command's stdout is empty
And the command's stderr is exactly `skill_builder: SKILL_BUILDER_SESSION is not set` followed by one newline
And the builder HTTP stub still records zero requests
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: An expired session is refused by the shared session gate
Given Ada's ID token has `exp` = `2026-11-15T09:59:59Z` and the current time is `2026-11-15T10:00:00Z`
And `SKILL_BUILDER_SESSION` is that expired token
When Ada runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --input main --model-profile 3 --tier high`
Then the builder returns HTTP 401 with body exactly `{"error":{"code":"authentication_required","message":"Sign in to use the skill builder."}}`
And the command exits with code `1`
And the command's stdout is empty
And the command's stderr is exactly `skill_builder: authentication_required: Sign in to use the skill builder.` followed by one newline
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A caller outside the skill-builders group is refused before project membership
Given Mallory's ID token has `cognito:groups` = `["catalog-reviewers"]`
And `SKILL_BUILDER_SESSION` is Mallory's token
When Mallory runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --input main --model-profile 3 --tier high`
Then the builder returns HTTP 403 with body exactly `{"error":{"code":"not_a_member","message":"You are not a member of the skill-builders group"}}`
And the command exits with code `1`
And the command's stderr is exactly `skill_builder: not_a_member: You are not a member of the skill-builders group` followed by one newline
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A signed-in skill-builders member outside the project is refused
Given Alan is a current member of the `skill-builders` group and has no `project_members` row for project `7`
And `SKILL_BUILDER_SESSION` is Alan's token
When Alan runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --input main --model-profile 3 --tier high`
Then the builder returns HTTP 403 with body exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And the command exits with code `1`
And the command's stderr is exactly `skill_builder: project_membership_required: You are not a member of this project.` followed by one newline
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A skills branch that does not exist is refused with the run-start error
Given Ada is a current project member
And `SKILL_BUILDER_SESSION` is Ada's token
When Ada runs `python -m skill_builder.runner run --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/missing --input main --model-profile 3 --tier high`
Then the builder returns HTTP 422 with body exactly `{"error":{"code":"skills_branch_not_found","message":"Skills branch 'test/ada/missing' does not exist."}}`
And the command exits with code `1`
And the command's stderr is exactly `skill_builder: skills_branch_not_found: Skills branch 'test/ada/missing' does not exist.` followed by one newline
And `SELECT count(*) FROM runs` returns `0`

### Covered requirements (traceability)
- FR-116

### Out of scope
Starting a security scan from the command line (BSB-37-PENDING-2 and BSB-37-PENDING-3); saving,
running or scheduling a suite (BSB-37-PENDING-4, BSB-37-PENDING-5, BSB-37-PENDING-6 and
BSB-37-PENDING-7); selecting branches or model profiles interactively (epic BSB-24's options API);
the run-start form itself (epic BSB-24); packaging and the run branch (epic BSB-25); creating,
editing or deleting users, groups or projects (the epic's non-goal); workflow orchestration or
gating (the epic's non-goal); re-runs, re-verification, history, compare or submit (epics BSB-27,
BSB-30, BSB-35 and BSB-36).

### Notes / dependencies
- Depends on epic BSB-18 for the session and `skill-builders` gates, epic BSB-22 for project
  membership, epic BSB-23 for the `github` and `ai_model` integration shapes, and epic BSB-24 for
  the run-start route, its validation, its error bodies and the `runs` row.
- The CLI is a thin HTTP client. It sends the same `sb_session` token the browser sends and never
  opens the database, so the web and command-line paths cannot drift in identity or membership.
- The command-line body order (`skill`, `skills_ref`, `input_branch`, `model_profile_id`, `tier`,
  then `context`) is the order epic BSB-24's web form sends, which is what makes the parity check
  byte-for-byte.
- `--context` is optional; when supplied it is parsed as a JSON object and appended after `tier`.
  When omitted no `context` key is sent and epic BSB-24 stores `{}`.
- Prerequisite for BSB-37-PENDING-5 and BSB-37-PENDING-6, whose suite runs start through the same
  run contract.

---

## STORY: BSB-37-PENDING-2

**Summary:** Run a static-only security scan from the command line without creating a test run
**Epic:** BSB-37 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-16, MVP

### Story
As a **skill author**, I want **to run a static-only security scan of a skill branch from the command line without starting a test run**, so that **I can gate scripted or CI work on the static verdict before any agent runs**.

### Acceptance Criteria

#### Scenario: A static-only scan runs one scanner container and creates no test run
Given Ada is a current member of the `skill-builders` group and the owner of project `7`
And `SKILL_BUILDER_SESSION` is Ada's token
And the scanner stub answers with `{"scanner_version":"1.6.0","verdict":"INSTALL","score":100,"recommendation":"INSTALL","coverage":{"complete":true,"files_scanned":7,"files_skipped":[]},"findings":[]}`
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --static-only`
Then the builder HTTP stub records exactly one start request, `POST https://builder.skillbuilder.internal/api/projects/7/scans/by-ref`
And that request carries the `Cookie: sb_session=` header carrying Ada's exact ID token and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","kind":"static"}`
And the scanner stub records exactly one static scanner container with the scanner image digest from `kit.json`, the bundle mounted read-only, no network and no credential
And a `static_scans` row `21` is stored with `skill` = `sdlc-fix-bug-triage`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `content_sha` = `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`, `state` = `completed`, `verdict` = `passed`, `score` = `100`, `recommendation` = `INSTALL`, `coverage` = `complete`, `findings` = `[]`, `scanner_version` = `1.6.0`, `run_id` = `NULL`, `build_id` = `NULL` and `llm_stage` = `false`
And the command exits with code `0`
And the command's stdout is exactly `scan 21: completed verdict=passed` followed by one newline
And the command's stderr is empty
And `SELECT count(*) FROM runs` returns `0`
And the scanner stub records zero LLM scanner containers
And `SELECT count(*) FROM llm_scans` returns `0`
And no catalog branch, no baseline and no agent container is created

#### Scenario: A static scan with a blocking finding exits non-zero
Given Ada is a current project member with a valid session
And the scanner stub answers with `{"scanner_version":"1.6.0","verdict":"DO_NOT_INSTALL","score":63,"recommendation":"DO_NOT_INSTALL","coverage":{"complete":true,"files_scanned":7,"files_skipped":[]},"findings":[{"severity":"CRITICAL","rule":"SP-0042","file":"skills/sdlc-fix-bug-triage/SKILL.md","line":17}]}`
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --static-only`
Then the `static_scans` row `21` has `state` = `completed` and `verdict` = `failed`
And the command exits with code `1`
And the command's stdout is exactly `scan 21: completed verdict=failed` followed by one newline
And the command's stderr is empty
And `SELECT count(*) FROM runs` returns `0`
And the scanner stub records zero LLM scanner containers

#### Scenario: A scanner that cannot produce a report exits non-zero
Given Ada is a current project member with a valid session
And the scanner stub exits with a non-zero status and writes no report
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --static-only`
Then the `static_scans` row `21` has `state` = `failed`, `verdict` = `failed`, `error` = `scanner_failed` and `findings` = `[]`
And the command exits with code `1`
And the command's stdout is exactly `scan 21: failed error=scanner_failed` followed by one newline
And the command's stderr is empty
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A project non-member is refused before any scanner starts
Given Alan is a current member of the `skill-builders` group and has no `project_members` row for project `7`
And `SKILL_BUILDER_SESSION` is Alan's token
When Alan runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --static-only`
Then the builder returns HTTP 403 with body exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And the command exits with code `1`
And the command's stderr is exactly `skill_builder: project_membership_required: You are not a member of this project.` followed by one newline
And the scanner stub records zero scanner containers
And `SELECT count(*) FROM static_scans` returns `0`

#### Scenario: A missing session is a usage error and starts nothing
Given `SKILL_BUILDER_SESSION` is unset
And the builder HTTP stub has recorded zero requests
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --static-only`
Then the command exits with code `2`
And the command's stdout is empty
And the command's stderr is exactly `skill_builder: SKILL_BUILDER_SESSION is not set` followed by one newline
And the builder HTTP stub records zero requests
And the scanner stub records zero scanner containers

#### Scenario: A completed result for the same content is reused without a second container
Given static scan `12` exists as the fixture row, completed with `verdict` = `passed` for content SHA `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` and the pinned scanner image digest
And Ada is a current project member with a valid session
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce --static-only`
Then the builder returns the by-ref start response with `scan_id` = `12` and `state` = `completed`
And the scanner stub records zero scanner containers
And the command exits with code `0`
And the command's stdout is exactly `scan 12: completed verdict=passed` followed by one newline
And `SELECT count(*) FROM static_scans` returns `1`

### Covered requirements (traceability)
- FR-117

### Out of scope
The full LLM security scan (BSB-37-PENDING-3); starting a test run (epic BSB-24 and
BSB-37-PENDING-1); saving, running or scheduling a suite (BSB-37-PENDING-4 to
BSB-37-PENDING-7); the static scan's verdict rule, cache key, timeout, report format and storage
(epic BSB-31); scanning from the skill page's Security check button (epic BSB-31); the LLM stage's
trigger, model, unavailable states and report (epic BSB-32); presenting findings in a web page
(epic BSB-31); overriding a static block (the epic's non-goal); workflow orchestration (the epic's
non-goal).

### Notes / dependencies
- Depends on epic BSB-18 for the session and group gates, epic BSB-22 for project membership, epic
  BSB-25 for branch resolution and bundle packing, and epic BSB-31 for the static scan service,
  its content-addressed cache and its `static_scans` row.
- The by-ref route is a thin CLI adapter (Decision 5); it calls the same static scan service the
  build-based route calls, so the verdict rule and cache are not duplicated.
- `--static-only` never sets `llm_stage` and never calls epic BSB-32's LLM trigger. The full
  command in BSB-37-PENDING-3 does.
- The CLI polls the status route every second and gives the scan 600 seconds, matching the scanner
  container's ten-minute limit. A scan still running at 600 seconds is epic BSB-31's
  `scan_timeout`; the CLI prints `scan 21: failed error=scan_timeout` and exits `1`.
- The exit code reflects the static verdict, which is the only stage this command runs.

---

## STORY: BSB-37-PENDING-3

**Summary:** Run a full security scan from the command line without creating a test run
**Epic:** BSB-37 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-16, MVP

### Story
As a **skill author**, I want **to run the full static and LLM security scan of a skill branch from the command line without starting a test run**, so that **scripted and CI work gets the same two-stage security result the web Security check gives, with no agent container**.

### Acceptance Criteria

#### Scenario: A full scan runs both stages and prints both outcomes
Given Ada is a current member of the `skill-builders` group and the owner of project `7`
And `SKILL_BUILDER_SESSION` is Ada's token
And project `7`'s LLM-scan setting resolves to profile `3` tier `medium`, so the model is `test-model-medium`
And the scanner stub answers the static stage with `verdict` `INSTALL`, `score` `100`, `recommendation` `INSTALL`, `coverage.complete` `true` and `findings` `[]`
And the scanner stub answers the LLM stage with `{"scanner_version":"1.6.0","vendor":"anthropic","model":"test-model-medium","findings":[]}`
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce`
Then the builder HTTP stub records exactly one start request, `POST https://builder.skillbuilder.internal/api/projects/7/scans/by-ref`
And that request's body is exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","kind":"full"}`
And the scanner stub records exactly one static scanner container and, after the static verdict is `passed`, exactly one LLM scanner container
And the LLM scanner container has model `test-model-medium`, the model key only in its environment and network access only to `https://api.anthropic.test`
And the `static_scans` row `21` has `llm_stage` = `true` and `state` = `completed` with `verdict` = `passed`
And the `llm_scans` row `51` has `state` = `complete` for the same content SHA
And the command exits with code `0`
And the command's stdout is exactly `scan 21: completed verdict=passed llm_scan=51 llm_state=complete` followed by one newline
And the command's stderr is empty
And `SELECT count(*) FROM runs` returns `0`
And the scanner stub records zero agent containers

#### Scenario: A static failure stops the LLM stage and exits non-zero
Given Ada is a current project member with a valid session
And the scanner stub answers the static stage with `verdict` `DO_NOT_INSTALL`, `recommendation` `DO_NOT_INSTALL`, `score` `63` and a finding whose `severity` is `CRITICAL`
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce`
Then the `static_scans` row `21` has `state` = `completed` and `verdict` = `failed`
And the scanner stub records zero LLM scanner containers
And `SELECT count(*) FROM llm_scans` returns `0`
And the command exits with code `1`
And the command's stdout is exactly `scan 21: completed verdict=failed llm_scan=none` followed by one newline
And the command's stderr is empty
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: An unavailable LLM scan is reported but does not fail the command
Given Ada is a current project member with a valid session
And the scanner stub answers the static stage with `verdict` `INSTALL`, `score` `100`, `recommendation` `INSTALL`, `coverage.complete` `true` and `findings` `[]`
And the LLM stage records `state` = `unavailable` with `error` = `llm_model_key_unavailable` for the same content SHA and model `test-model-medium`
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce`
Then the `static_scans` row `21` has `state` = `completed` and `verdict` = `passed`
And the `llm_scans` row `51` has `state` = `unavailable` and `error` = `llm_model_key_unavailable`
And the command exits with code `0`
And the command's stdout is exactly `scan 21: completed verdict=passed llm_scan=51 llm_state=unavailable` followed by one newline
And the command's stderr is empty
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A project non-member is refused before either scanner starts
Given Alan is a current member of the `skill-builders` group and has no `project_members` row for project `7`
And `SKILL_BUILDER_SESSION` is Alan's token
When Alan runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage --skills-ref test/ada/fix-reproduce`
Then the builder returns HTTP 403 with body exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And the command exits with code `1`
And the command's stderr is exactly `skill_builder: project_membership_required: You are not a member of this project.` followed by one newline
And the scanner stub records zero static and zero LLM scanner containers
And `SELECT count(*) FROM static_scans` returns `0`
And `SELECT count(*) FROM llm_scans` returns `0`

#### Scenario: A missing skills branch is a usage error and starts nothing
Given `SKILL_BUILDER_SESSION` is Ada's valid token
And Ada omits the `--skills-ref` argument
When Ada runs `python -m skill_builder.runner scan --project 7 --skill sdlc-fix-bug-triage`
Then the command exits with code `2`
And the command's stdout is empty
And the command's stderr is exactly `skill_builder: --skills-ref is required` followed by one newline
And the builder HTTP stub records zero requests
And the scanner stub records zero scanner containers

### Covered requirements (traceability)
- FR-118

### Out of scope
The static-only scan (BSB-37-PENDING-2); starting a test run (epic BSB-24 and BSB-37-PENDING-1);
saving, running or scheduling a suite (BSB-37-PENDING-4 to BSB-37-PENDING-7); the static verdict
rule, cache and timeout (epic BSB-31); the LLM trigger rule, model selection, unavailable causes
and report (epic BSB-32); presenting the scans on the skill page (epics BSB-31 and BSB-32);
overriding the project's LLM-scan model from the command line (epic BSB-32's rule is per project);
workflow orchestration (the epic's non-goal).

### Notes / dependencies
- Depends on epic BSB-18 for the session and group gates, epic BSB-22 for project membership, epic
  BSB-25 for branch resolution and bundle packing, epic BSB-31 for the static stage and epic BSB-32
  for the LLM stage.
- The full command sets `llm_stage` = `true` on the static row, which is epic BSB-32's marker for
  "start the LLM stage after a passing static scan". The static-only command never sets it.
- The LLM model comes from project `7`'s LLM-scan setting, never from a command-line flag. An
  `unavailable` LLM scan still prints its id and state and exits `0`, because the LLM stage never
  refuses a run.
- The CLI learns the LLM row's id from the by-ref status route after the static stage passes; the
  start response's `llm_scan_id` is `null` because no LLM row exists at start time.
- The full command waits up to 600 seconds for each stage, matching the ten-minute scanner
  container limit.

---

## STORY: BSB-37-PENDING-4

**Summary:** Save a named suite whose entries name skill, skills branch, input branch, context, expectations, model profile and tier
**Epic:** BSB-37 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-16, Later

### Story
As a **skill author**, I want **to save a named suite whose entries each name a skill, skills branch, input branch, context, expectations, model profile and tier**, so that **I can repeat exactly the same set of runs later without re-entering every choice**.

### Acceptance Criteria

#### Scenario: An author saves a named suite and reads it back
Given Ada is a current member of the `skill-builders` group and the owner of project `7`
And the `suites` table has exactly zero rows
And `sdlc-fix-bug-triage` exists at `skills/sdlc-fix-bug-triage/SKILL.md` on catalog branch `test/ada/fix-reproduce`
And the sandbox branch `main` exists and `config/bug-fix.yaml` on `test/ada/fix-reproduce` declares workflow `bug-fix` with step `triage`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/suites` with `Content-Type: application/json` and body exactly `{"name":"Nightly bug-fix","entries":[{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","context":{"workflow":"bug-fix","step":"triage"},"expectations":{"final_verdict":"completed"},"model_profile_id":3,"tier":"high"}]}`
Then the response is HTTP 201 with `Content-Type: application/json`
And the response body is exactly `{"id":1,"project_id":7,"name":"Nightly bug-fix","created_by":42,"nightly":false,"next_run_at":null,"source_path":null,"definition":{"entries":[{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","context":{"workflow":"bug-fix","step":"triage"},"expectations":{"final_verdict":"completed"},"model_profile_id":3,"tier":"high"}]}}`
And `SELECT project_id, name, created_by, nightly, next_run_at, source_path FROM suites WHERE id = 1` returns exactly `7 | Nightly bug-fix | 42 | false | NULL | NULL`
And `SELECT definition FROM suites WHERE id = 1` equals the JSON value `{"entries":[{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","context":{"workflow":"bug-fix","step":"triage"},"expectations":{"final_verdict":"completed"},"model_profile_id":3,"tier":"high"}]}`
And `GET https://builder.skillbuilder.internal/api/projects/7/suites/1` returns HTTP 200 with the same body
And `GET https://builder.skillbuilder.internal/projects/7/suites` returns HTTP 200 with `Content-Type: text/html; charset=utf-8` and contains `<a id="suite-1" href="/projects/7/suites/1">Nightly bug-fix</a>` and `<span id="suite-1-nightly">Nightly: Off</span>`
And no commit, no file and no repository write is created

#### Scenario: A duplicate suite name in the same project is refused
Given project `7` already has suite `1` named `Nightly bug-fix`
And project `8` has a suite named `Nightly bug-fix` as an unrelated fixture row
And Ada is a current project member with a valid session
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/suites` with `Content-Type: application/json` and the same body as the successful save
Then the response is HTTP 409
And the response body is exactly `{"error":{"code":"suite_name_taken","message":"Suite 'Nightly bug-fix' already exists in project 7."}}`
And `SELECT count(*) FROM suites WHERE project_id = 7` returns `1`
And `SELECT count(*) FROM suites WHERE project_id = 8` returns `1`

#### Scenario: An entry missing a required field is refused with its index
Given Ada is a current project member with a valid session
And the request body is exactly `{"name":"Nightly bug-fix","entries":[{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","context":{"workflow":"bug-fix","step":"triage"},"expectations":{"final_verdict":"completed"},"model_profile_id":3,"tier":"high"}]}`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/suites` with `Content-Type: application/json` and that body
Then the response is HTTP 422
And the response body is exactly `{"error":{"code":"entry_field_required","message":"Entry 0 is missing input_branch."}}`
And `SELECT count(*) FROM suites` returns `0`

#### Scenario: An entry naming a skills branch that does not exist is refused before the suite is saved
Given Ada is a current project member with a valid session
And the request body is exactly `{"name":"Nightly bug-fix","entries":[{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/missing","input_branch":"main","context":{"workflow":"bug-fix","step":"triage"},"expectations":{"final_verdict":"completed"},"model_profile_id":3,"tier":"high"}]}`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/suites` with `Content-Type: application/json` and that body
Then the response is HTTP 422
And the response body is exactly `{"error":{"code":"skills_branch_not_found","message":"Skills branch 'test/ada/missing' does not exist."}}`
And `SELECT count(*) FROM suites` returns `0`

#### Scenario: A suite with no entries is refused
Given Ada is a current project member with a valid session
And the request body is exactly `{"name":"Nightly bug-fix","entries":[]}`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/suites` with `Content-Type: application/json` and that body
Then the response is HTTP 422
And the response body is exactly `{"error":{"code":"entries_required","message":"A suite must contain at least one entry."}}`
And `SELECT count(*) FROM suites` returns `0`

#### Scenario: A signed-in skill-builders member outside the project cannot save a suite
Given Alan is a current member of the `skill-builders` group and has no `project_members` row for project `7`
And `SKILL_BUILDER_SESSION` is Alan's token
When Alan sends `POST https://builder.skillbuilder.internal/api/projects/7/suites` with `Content-Type: application/json` and a valid suite body
Then the response is HTTP 403
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM suites` returns `0`

### Covered requirements (traceability)
- FR-119
- FR-120

### Out of scope
Running a saved suite (BSB-37-PENDING-5); scheduling it (BSB-37-PENDING-6); recording its results
(BSB-37-PENDING-7); editing, renaming, cloning or deleting a saved suite; suite versioning; a
repository `suites/*.yaml` file or export; importing a suite from a file; sharing a suite with
another project; notifications; evaluating the `expectations` object; the run-start validation and
error rules themselves (epic BSB-24); the project's integration configuration (epic BSB-23);
accessibility of the suite page (epic BSB-38).

### Notes / dependencies
- Depends on epic BSB-18 for the session and group gates, epic BSB-22 for project membership, epic
  BSB-23 for the `github` and `ai_model` integration shapes, and epic BSB-24 for the context and
  model rules the entries reuse.
- The suite entry carries the three run inputs FR-120 omits (`skills_ref`, `model_profile_id` and
  `tier`) so that BSB-37-PENDING-5 can start each entry with no guess (Decision 1). The four fields
  FR-120 names are all present and validated.
- `expectations` is stored unchanged and is not evaluated (Decision 8); it is the author's note for
  what the run is expected to show.
- `source_path` is `NULL` and the save writes no repository file (Decision 2). The `suites` row is
  the durable system of record.
- The unique `(project_id, name)` constraint is per project, so the same suite name in project `8`
  does not block project `7`.
- Prerequisite for BSB-37-PENDING-5, BSB-37-PENDING-6 and BSB-37-PENDING-7.

---

## STORY: BSB-37-PENDING-5

**Summary:** Run a saved suite and create one run per entry
**Epic:** BSB-37 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-16, Later

### Story
As a **skill author**, I want **to run a saved suite and have the builder start one test run for each entry in it**, so that **I can repeat a whole named set of checks with one action and keep the runs grouped together**.

### Acceptance Criteria

#### Scenario: Running a two-entry suite starts one run per entry in order
Given Ada is a current project member with a valid session
And suite `1` in project `7` has exactly two entries: entry `0` with skill `sdlc-fix-bug-triage`, skills branch `test/ada/fix-reproduce`, input branch `main`, context `{"workflow":"bug-fix","step":"triage"}`, expectations `{"final_verdict":"completed"}`, model profile `3` and tier `high`; entry `1` with skill `sdlc-fix-bug-triage`, skills branch `test/ada/fix-reproduce-2`, input branch `fixtures/blocked-handoff`, context `{"workflow":"bug-fix","step":"reproduce"}`, expectations `{"final_verdict":"completed"}`, model profile `4` and tier `medium`
And the `runs`, `suite_runs` and `suite_run_entries` tables have exactly zero rows
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/suites/1/runs` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 202 with `Content-Type: application/json`
And the response body is exactly `{"suite_run_id":1,"suite_id":1,"project_id":7,"trigger":"manual","state":"running","entries":[{"entry_index":0,"skill":"sdlc-fix-bug-triage","run_id":1,"status":"started"},{"entry_index":1,"skill":"sdlc-fix-bug-triage","run_id":2,"status":"started"}]}`
And `SELECT suite_id, project_id, trigger, scheduled_for, state FROM suite_runs WHERE id = 1` returns exactly `1 | 7 | manual | NULL | running`
And `SELECT entry_index, run_id, status FROM suite_run_entries WHERE suite_run_id = 1 ORDER BY entry_index` returns exactly `0 | 1 | started` and `1 | 2 | started`
And `SELECT id, project_id, user_id, skill, skills_ref, input_branch, model_profile_id, tier, state, kind FROM runs ORDER BY id` returns exactly `1 | 7 | 42 | sdlc-fix-bug-triage | test/ada/fix-reproduce | main | 3 | high | queued | run` and `2 | 7 | 42 | sdlc-fix-bug-triage | test/ada/fix-reproduce-2 | fixtures/blocked-handoff | 4 | medium | queued | run`
And `SELECT context FROM runs WHERE id = 1` equals the JSON value `{"workflow":"bug-fix","step":"triage"}`
And `SELECT context FROM runs WHERE id = 2` equals the JSON value `{"workflow":"bug-fix","step":"reproduce"}`

#### Scenario: A branch that disappeared makes the manual run refuse before starting any entry
Given Ada is a current project member with a valid session
And suite `1` has two entries that were valid when the suite was saved
And the sandbox branch `fixtures/blocked-handoff` has since been deleted from `saraavrnd/bheembhai-skill-fixtures`
And entry `1` names that input branch
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/suites/1/runs` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 422
And the response body is exactly `{"error":{"code":"suite_entry_invalid","message":"Entry 1 cannot start: Input branch 'fixtures/blocked-handoff' does not exist."}}`
And `SELECT count(*) FROM suite_runs` returns `0`
And `SELECT count(*) FROM suite_run_entries` returns `0`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A signed-in skill-builders member outside the project cannot run the suite
Given Alan is a current member of the `skill-builders` group and has no `project_members` row for project `7`
And `SKILL_BUILDER_SESSION` is Alan's token
And suite `1` exists in project `7`
When Alan sends `POST https://builder.skillbuilder.internal/api/projects/7/suites/1/runs` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 403
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM suite_runs` returns `0`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A suite in another project is not addressable through this project
Given Ada is a current project member of project `7`
And suite `2` exists in project `8`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/suites/2/runs` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 404
And the response body is exactly `{"error":{"code":"suite_not_found","message":"Suite 2 not found in project 7."}}`
And `SELECT count(*) FROM suite_runs` returns `0`
And `SELECT count(*) FROM runs` returns `0`

### Covered requirements (traceability)
- FR-121

### Out of scope
Saving the suite or validating its entries at save time (BSB-37-PENDING-4); scheduling the suite or
the nightly trigger (BSB-37-PENDING-6); recording each entry's result (BSB-37-PENDING-7); starting
a single run directly (epic BSB-24 and BSB-37-PENDING-1); re-running a suite entry or a previous
suite run; running suite entries in parallel; retrying a failed entry; cancelling or pausing a suite
run; running a suite that is scheduled (the nightly path is BSB-37-PENDING-6); notifications.

### Notes / dependencies
- Depends on BSB-37-PENDING-4 for the saved suite and its entries, on epic BSB-18 for the session
  and group gates, on epic BSB-22 for project membership, and on epic BSB-24 for each entry's
  run-start validation and `runs` row.
- A manual run is all-or-nothing: every entry is validated before any run starts, so a broken entry
  cannot leave a half-started suite (Decision 7). The nightly path records per-entry `not_started`
  results instead because it has no interactive caller.
- `runs.user_id` is the calling user, not the suite's creator; a project member running someone
  else's suite is attributable to the caller.
- The suite run is `running` until BSB-37-PENDING-7 records every entry's result. This story creates
  the grouping rows; it does not wait for the runs to finish.
- The runs start in entry order, and the `runs.id` values follow that order in the fixture. The
  implementation may interleave later work, but the suite's entry-to-run mapping is fixed.

---

## STORY: BSB-37-PENDING-6

**Summary:** Schedule a saved suite for nightly execution and run it once per night
**Epic:** BSB-37 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-16, Later

### Story
As a **skill author**, I want **to schedule a saved suite to run every night and to stop the schedule when I no longer need it**, so that **a repeatable set of checks runs without me and never runs twice in one night**.

### Acceptance Criteria

#### Scenario: An author schedules a suite for nightly execution
Given Ada is a current project member with a valid session
And suite `1` in project `7` has `nightly` = `false` and `next_run_at` = `NULL`
And the current time is `2026-11-15T10:00:00Z`
When Ada sends `PUT https://builder.skillbuilder.internal/api/projects/7/suites/1/schedule` with `Content-Type: application/json` and body exactly `{"nightly":true}`
Then the response is HTTP 200 with `Content-Type: application/json`
And the response body is exactly `{"suite_id":1,"project_id":7,"nightly":true,"next_run_at":"2026-11-16T02:00:00Z"}`
And `SELECT nightly, next_run_at FROM suites WHERE id = 1` returns exactly `true | 2026-11-16T02:00:00Z`
And `GET https://builder.skillbuilder.internal/projects/7/suites` contains `<span id="suite-1-nightly">Nightly: On</span>`

#### Scenario: The nightly job starts one suite run for each due nightly suite
Given suite `1` in project `7` has `nightly` = `true`, `next_run_at` = `2026-11-16T02:00:00Z` and `created_by` = `42`
And suite `1` has exactly one entry: skill `sdlc-fix-bug-triage`, skills branch `test/ada/fix-reproduce`, input branch `main`, context `{"workflow":"bug-fix","step":"triage"}`, expectations `{"final_verdict":"completed"}`, model profile `3` and tier `high`
And suite `2` in project `8` has `nightly` = `false` and `next_run_at` = `NULL`
And the `runs`, `suite_runs` and `suite_run_entries` tables have exactly zero rows
And the current time is `2026-11-16T02:00:00Z`
When the nightly suite scheduler runs
Then exactly one `suite_runs` row exists: `id` = `1`, `suite_id` = `1`, `project_id` = `7`, `trigger` = `nightly`, `scheduled_for` = `2026-11-16`, `state` = `running`, `created_at` = `2026-11-16T02:00:00Z`, `finished_at` = `NULL`
And exactly one `suite_run_entries` row exists for `suite_run_id` = `1` with `entry_index` = `0`, `run_id` = `1`, `status` = `started`, `result_state` = `NULL`, `result_final_verdict` = `NULL`, `error_code` = `NULL` and `error_message` = `NULL`
And exactly one `runs` row exists: `id` = `1`, `project_id` = `7`, `user_id` = `42`, `skill` = `sdlc-fix-bug-triage`, `skills_ref` = `test/ada/fix-reproduce`, `input_branch` = `main`, `model_profile_id` = `3`, `tier` = `high`, `state` = `queued` and `kind` = `run`, and its `context` equals the JSON value `{"workflow":"bug-fix","step":"triage"}`
And `SELECT nightly, next_run_at FROM suites WHERE id = 1` returns exactly `true | 2026-11-17T02:00:00Z`
And `SELECT count(*) FROM suite_runs WHERE suite_id = 2` returns `0`

#### Scenario: Running the nightly job twice in one night does not duplicate the suite run
Given the nightly job has already created `suite_runs` row `1` for suite `1` and `scheduled_for` = `2026-11-16` and one `runs` row
And suite `1` still has `next_run_at` = `2026-11-16T02:00:00Z`, as if the first attempt stopped before advancing it
And the current time is `2026-11-16T02:00:30Z`
When the nightly suite scheduler runs again
Then `SELECT count(*) FROM suite_runs WHERE suite_id = 1 AND scheduled_for = '2026-11-16'` returns `1`
And `SELECT count(*) FROM suite_run_entries WHERE suite_run_id = 1` returns `1`
And `SELECT count(*) FROM runs` returns `1`
And `SELECT next_run_at FROM suites WHERE id = 1` returns `2026-11-17T02:00:00Z`

#### Scenario: Unscheduling stops future nightly runs
Given suite `1` in project `7` has `nightly` = `true` and `next_run_at` = `2026-11-16T02:00:00Z`
And the `suite_runs` table has exactly zero rows
And Ada is a current project member with a valid session
When Ada sends `PUT https://builder.skillbuilder.internal/api/projects/7/suites/1/schedule` with `Content-Type: application/json` and body exactly `{"nightly":false}`
Then the response is HTTP 200
And the response body is exactly `{"suite_id":1,"project_id":7,"nightly":false,"next_run_at":null}`
And `SELECT nightly, next_run_at FROM suites WHERE id = 1` returns exactly `false | NULL`

#### Scenario: The nightly job skips a suite that is no longer nightly
Given suite `1` in project `7` has `nightly` = `false` and `next_run_at` = `NULL`
And the `suite_runs`, `suite_run_entries` and `runs` tables have exactly zero rows
And the current time is `2026-11-17T02:00:00Z`
When the nightly suite scheduler runs
Then `SELECT count(*) FROM suite_runs WHERE suite_id = 1` returns `0`
And `SELECT count(*) FROM suite_run_entries` returns `0`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A signed-in skill-builders member outside the project cannot schedule the suite
Given Alan is a current member of the `skill-builders` group and has no `project_members` row for project `7`
And `SKILL_BUILDER_SESSION` is Alan's token
And suite `1` in project `7` has `nightly` = `false`
When Alan sends `PUT https://builder.skillbuilder.internal/api/projects/7/suites/1/schedule` with `Content-Type: application/json` and body exactly `{"nightly":true}`
Then the response is HTTP 403
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT nightly FROM suites WHERE id = 1` returns `false`

#### Scenario: A non-boolean nightly value is refused
Given Ada is a current project member with a valid session
And suite `1` in project `7` has `nightly` = `false`
When Ada sends `PUT https://builder.skillbuilder.internal/api/projects/7/suites/1/schedule` with `Content-Type: application/json` and body exactly `{"nightly":"yes"}`
Then the response is HTTP 422
And the response body is exactly `{"error":{"code":"nightly_invalid","message":"nightly must be a JSON boolean."}}`
And `SELECT nightly, next_run_at FROM suites WHERE id = 1` returns exactly `false | NULL`

### Covered requirements (traceability)
- FR-122

### Out of scope
Saving, editing or running the suite by hand (BSB-37-PENDING-4 and BSB-37-PENDING-5); recording
each entry's result (BSB-37-PENDING-7); cron expressions, time zones, per-day schedules or
multiple schedules per suite; notifications or reports about the schedule; retrying a missed
night; running a suite more than once per night; administrating the installation's jobs (the
operator's job); workflow orchestration (the epic's non-goal).

### Notes / dependencies
- Depends on BSB-37-PENDING-4 for the saved suite and BSB-37-PENDING-5 for the suite-run and
  per-entry rows the nightly job creates; on epic BSB-18 for the schedule route's session and
  group gates; on epic BSB-22 for project membership; and on epic BSB-24 for each entry's run-start
  validation.
- The nightly suite scheduler is this epic's installation-level job at `02:00 UTC`, separate from
  epic BSB-28's nightly Jira sweep. It uses `suites.created_by` as the run's user because no human
  triggers it (Decision 6).
- The unique `(suite_id, scheduled_for)` key is the idempotency guard. A second run on the same
  night finds the existing row and does nothing; it does not create a second set of runs.
- `next_run_at` is always the next `02:00:00Z` after the current time. Scheduling, unscheduling and
  each processed night update it; this epic adds no other schedule shape (Decision 9).
- The job creates the `suite_runs` row and all `suite_run_entries` rows before attempting any
  entry, so BSB-37-PENDING-7 can record a result for every entry even when none can start.

---

## STORY: BSB-37-PENDING-7

**Summary:** Record each scheduled suite entry's result, including an entry that cannot start
**Epic:** BSB-37 · **Release:** Later · **Estimate:** 5 · **Labels:** FA-16, Later

### Story
As a **skill author**, I want **to see a recorded result for every entry of a scheduled suite run, including an entry whose run could not start**, so that **a nightly failure is visible instead of silently missing from the suite's history**.

### Acceptance Criteria

#### Scenario: Each started entry's result is recorded when its run reaches a terminal state
Given nightly `suite_runs` row `1` exists for suite `1` in project `7` with `trigger` = `nightly`, `scheduled_for` = `2026-11-16`, `state` = `running`, `created_at` = `2026-11-16T02:00:00Z` and `finished_at` = `NULL`
And `suite_run_entries` has entry `0` with `run_id` = `1` and `status` = `started` and entry `1` with `run_id` = `2` and `status` = `started`
And run `1` and run `2` are queued
When run `1` is written with `state` = `completed` and `final_verdict` = `completed` and run `2` is written with `state` = `completed` and `final_verdict` = `changes_requested` at `2026-11-16T02:05:00Z`
Then `SELECT entry_index, run_id, status, result_state, result_final_verdict, error_code, error_message FROM suite_run_entries WHERE suite_run_id = 1 ORDER BY entry_index` returns exactly `0 | 1 | finished | completed | completed | NULL | NULL` and `1 | 2 | finished | completed | changes_requested | NULL | NULL`
And `SELECT state, finished_at FROM suite_runs WHERE id = 1` returns exactly `completed | 2026-11-16T02:05:00Z`
And `GET https://builder.skillbuilder.internal/api/projects/7/suite-runs/1` returns HTTP 200 with `Content-Type: application/json`
And that response body is exactly `{"suite_run_id":1,"suite_id":1,"project_id":7,"trigger":"nightly","scheduled_for":"2026-11-16","state":"completed","started_at":"2026-11-16T02:00:00Z","finished_at":"2026-11-16T02:05:00Z","entries":[{"entry_index":0,"skill":"sdlc-fix-bug-triage","input_branch":"main","run_id":1,"status":"finished","result_state":"completed","result_final_verdict":"completed","error_code":null,"error_message":null},{"entry_index":1,"skill":"sdlc-fix-bug-triage","input_branch":"fixtures/blocked-handoff","run_id":2,"status":"finished","result_state":"completed","result_final_verdict":"changes_requested","error_code":null,"error_message":null}]}`

#### Scenario: A run that fails execution is still recorded as a result
Given nightly `suite_runs` row `1` exists with entry `0` run `1` and entry `1` run `2` both `started`
And run `1` has been written with `state` = `completed` and `final_verdict` = `completed`
And run `2` is queued
When the builder writes run `2` with `state` = `failed_execution` and `final_verdict` = `failed_execution`
Then `SELECT status, result_state, result_final_verdict, error_code FROM suite_run_entries WHERE suite_run_id = 1 AND entry_index = 1` returns exactly `finished | failed_execution | failed_execution | NULL`
And `SELECT state FROM suite_runs WHERE id = 1` returns `completed`
And the result API's entry `1` has `status` = `finished`, `result_state` = `failed_execution` and `result_final_verdict` = `failed_execution`

#### Scenario: An entry that cannot start records not_started and does not stop the other entries
Given suite `1` in project `7` has two entries: entry `0` with input branch `main` and entry `1` with input branch `fixtures/missing`
And the sandbox branch `fixtures/missing` does not exist
And the current time is `2026-11-16T02:00:00Z`
When the nightly suite scheduler runs and then run `1` (entry `0`) is written with `state` = `completed` and `final_verdict` = `completed` at `2026-11-16T02:05:00Z`
Then `SELECT entry_index, run_id, status, result_state, result_final_verdict, error_code, error_message FROM suite_run_entries WHERE suite_run_id = 1 ORDER BY entry_index` returns exactly `0 | 1 | finished | completed | completed | NULL | NULL` and `1 | NULL | not_started | NULL | NULL | input_branch_not_found | Input branch 'fixtures/missing' does not exist.`
And `SELECT count(*) FROM runs` returns `1`
And `SELECT state, finished_at FROM suite_runs WHERE id = 1` returns exactly `completed | 2026-11-16T02:05:00Z`
And the result API's entry `1` has `status` = `not_started`, `run_id` = `null`, `error_code` = `input_branch_not_found` and `error_message` = `Input branch 'fixtures/missing' does not exist.`

#### Scenario: A nightly suite with no startable entry still records one result per entry
Given suite `1` in project `7` has two entries: entry `0` with input branch `fixtures/missing` and entry `1` with skills branch `test/ada/missing`
And neither `fixtures/missing` nor `test/ada/missing` exists
And the `runs`, `suite_runs` and `suite_run_entries` tables have exactly zero rows
And the current time is `2026-11-16T02:00:00Z`
When the nightly suite scheduler runs
Then `SELECT count(*) FROM runs` returns `0`
And `SELECT state, finished_at FROM suite_runs WHERE id = 1` returns exactly `completed | 2026-11-16T02:00:00Z`
And `SELECT entry_index, run_id, status, result_state, result_final_verdict, error_code, error_message FROM suite_run_entries WHERE suite_run_id = 1 ORDER BY entry_index` returns exactly `0 | NULL | not_started | NULL | NULL | input_branch_not_found | Input branch 'fixtures/missing' does not exist.` and `1 | NULL | not_started | NULL | NULL | skills_branch_not_found | Skills branch 'test/ada/missing' does not exist.`
And `GET https://builder.skillbuilder.internal/api/projects/7/suite-runs/1` returns HTTP 200 with a body whose `state` is `completed`, whose entry `0` has `status` = `not_started`, `run_id` = `null` and `error_code` = `input_branch_not_found`, and whose entry `1` has `status` = `not_started`, `run_id` = `null` and `error_code` = `skills_branch_not_found`

#### Scenario: The suite page shows each entry's recorded result
Given nightly `suite_runs` row `1` exists for suite `1` in project `7` and is `completed`
And entry `0` is `finished` with skill `sdlc-fix-bug-triage`, input branch `main`, `result_state` = `completed` and `result_final_verdict` = `completed`
And entry `1` is `not_started` with skill `sdlc-fix-bug-triage`, input branch `fixtures/missing` and `error_code` = `input_branch_not_found`
When Ada sends `GET https://builder.skillbuilder.internal/projects/7/suites/1` carrying her valid `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the response contains `<section id="suite-runs">`
And the response contains `<div id="suite-run-state">State: Completed</div>`
And the response contains `<tr id="suite-run-entry-0"><td>1</td><td>sdlc-fix-bug-triage</td><td>main</td><td>completed</td><td>completed</td></tr>`
And the response contains `<tr id="suite-run-entry-1"><td>2</td><td>sdlc-fix-bug-triage</td><td>fixtures/missing</td><td>not started</td><td>input_branch_not_found</td></tr>`

### Covered requirements (traceability)
- FR-123

### Out of scope
Saving the suite (BSB-37-PENDING-4); a manual suite run (BSB-37-PENDING-5); the scheduler's timing
and idempotency (BSB-37-PENDING-6); computing `runs.final_verdict` or `runs.verification` (epic
BSB-29); deciding what a verdict means (epic BSB-33); re-running a failed entry, retrying a suite
run or notifying anyone; purging or retaining suite results (epic BSB-34); editing or deleting a
suite's history; a comparison of suite runs across nights; accessibility of the result table (epic
BSB-38).

### Notes / dependencies
- Depends on BSB-37-PENDING-6 for the nightly `suite_runs` row and its pre-created
  `suite_run_entries` rows, and on epics BSB-26, BSB-27 and BSB-29 for the run's terminal state and
  `final_verdict`. It adds no verdict of its own.
- The result write is part of the same transaction that writes `runs.state`, and the update that
  writes `runs.final_verdict` fills `result_final_verdict`. A run in a terminal state therefore
  cannot be missing from the suite's results.
- A `not_started` entry is a result, not an absence: the epic's edge case requires a recorded result
  even when the run cannot start. The exact `error_code` and `error_message` are epic BSB-24's, not
  a new suite error vocabulary.
- The suite run is `completed` when every entry is `finished` or `not_started`; there is no
  separate failed suite state, because the per-entry results carry the failure.
- `suite_run_entries` copies the entry fields at trigger time, so a later edit to the suite
  definition cannot rewrite what a past scheduled run actually attempted.

---

*Generated by `sdlc-plan-stories-write`. Coverage: all 8 requirements mapped to BSB-37 are covered
by these 7 stories. Next step: `sdlc-plan-epic-review` reviews this set, then `sdlc-tracker-sync`
publishes the approved stories to Jira.*
