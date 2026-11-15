# Stories — BSB-24 (Run start & input selection)

Source: Jira epic **BSB-24** — *Run start & input selection* (feature area FA-6, release MVP,
labels FA-6, MVP), fetched read-only from the Atlassian project `bheembhai-skill-builder`; its
summary, description, functional scope, goal and stated edge cases are the same as the BSB-24
section of `docs/product/epics.md`. The requirement IDs mapped to the epic are in
`docs/product/epic-map.json`.

Epic BSB-24 covers 7 requirements. They decompose into the 5 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context, is epic **BSB-24**, fetched
read-only through the Atlassian API (the Atlassian MCP server was not connected in this session),
and its seven requirements are the ones decomposed here. Nothing was written to Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-037 | BSB-24-PENDING-1 |
| FR-145 | BSB-24-PENDING-2 |
| FR-146 | BSB-24-PENDING-2 |
| FR-147 | BSB-24-PENDING-3 |
| FR-148 | BSB-24-PENDING-4 |
| FR-149 | BSB-24-PENDING-5 |
| FR-150 | BSB-24-PENDING-5 |

The epic's three stated edge cases are covered explicitly: a non-member attempt fails before a run
is created (BSB-24-PENDING-1), an empty or non-existent branch fails before a run is created
(BSB-24-PENDING-2), and a model profile without a mapping for the chosen tier fails before a run is
created (BSB-24-PENDING-5).

## Run-start contract (test fixture constants)

Every scenario below starts from this fixed deployment, database and source-control fixture unless
it says otherwise. The member session, the local `users` rows and the `skill-builders` gate are
established by epic BSB-18. The project, `projects` rows and `project_members` rows are established
by epic BSB-22. The `github` and `ai_model` integration shapes below are the minimum this epic
consumes; epic BSB-23 owns the full integration schemas (FR-029 to FR-036), so if BSB-23 names a
field differently only this fixture is re-pointed in a revise pass — the validation decisions,
error codes and run-row contract fixed here do not change. The run, its inputs and the `runs`
columns follow `docs/adr/SK-001-skill-builder.md` §5 and §9.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT for the signed-in user with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`; the current time in every scenario is `2026-11-15T10:00:00Z` |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing` |
| `users` fixture | exactly three rows, the three users above |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42` and `created_at` = `2026-11-14T09:00:00Z`; id `8` has `name` = `Search smoke`, `owner_id` = `43` and `created_at` = `2026-11-14T09:05:00Z`; ids `1` to `6`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)` |
| `runs` fixture | exactly zero rows (`SELECT count(*) FROM runs` returns `0`), so the first run created has `id` = `1` |
| Catalog repository | `saraavrnd/bheembhai-skills`, the repository the builder is configured with; `main` is its default branch |
| Sandbox repository | `saraavrnd/bheembhai-skill-fixtures`, from the project's `github` integration; its base branch is `main` |
| Catalog branches offered | `build/sdlc-fix-bug-triage`, `main`, `test/ada/fix-reproduce`, `test/ada/fix-reproduce-2`, `test/grace/fix-reproduce`, each existing on `saraavrnd/bheembhai-skills` |
| Sandbox branches offered | `fixtures/blocked-handoff`, `fixtures/empty-title`, `main`, `test/ada/run-7-output`, each existing on `saraavrnd/bheembhai-skill-fixtures` |
| Skills present on the fixture branches | `sdlc-fix-bug-triage` exists at `skills/sdlc-fix-bug-triage/` on every catalog branch offered |
| Workflow config on the fixture branches | `config/bug-fix.yaml` declares workflow `bug-fix` with steps `triage`, `reproduce`, `root-cause`, `implement`; `config/smoke.yaml` declares workflow `smoke` with step `triage` |
| `github` integration (project 7) | row `id` = `6`, `project_id` = `7`, `kind` = `github`, `config` = `{"repo":"saraavrnd/bheembhai-skill-fixtures","base_branch":"main"}`, `secret_ref` = `skill-builder/7/github`, `mcp` = `null`, `verified_at` = `2026-11-14T09:02:00Z` |
| `ai_model` integration (project 7) | row `id` = `7`, `project_id` = `7`, `kind` = `ai_model`, `config` = `{"profiles":[{"id":3,"name":"Anthropic test","vendor":"anthropic","base_url":"https://api.anthropic.test","tiers":{"high":"test-model-high","medium":"test-model-medium"}},{"id":4,"name":"Smoke","vendor":"anthropic","base_url":"https://api.anthropic.test","tiers":{"medium":"test-model-medium"}}]}`, `secret_ref` = `skill-builder/7/ai_model`, `mcp` = `null`, `verified_at` = `2026-11-14T09:03:00Z` |
| `jira` integration (project 7) | row `id` = `5`, `project_id` = `7`, `kind` = `jira`, `config` = `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`, `secret_ref` = `skill-builder/7/jira`, `mcp` = `null`, `verified_at` = `2026-11-14T09:00:00Z` |
| `integrations` fixture (project 7) | exactly the three rows above (`id` 5, 6 and 7); project `8` has no `integrations` rows |
| Run-start page | `GET https://builder.skillbuilder.internal/projects/{project_id}/runs/new` |
| Run-start options API | `GET https://builder.skillbuilder.internal/api/projects/{project_id}/runs/options?skills_ref={branch}` |
| Run-start API | `POST https://builder.skillbuilder.internal/api/projects/{project_id}/runs` with `Content-Type: application/json` |
| Success status | HTTP 201 with `Content-Type: application/json` for an admitted run start; HTTP 200 with `Content-Type: application/json` for the options API; HTTP 200 with `Content-Type: text/html; charset=utf-8` for the run-start page |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |
| Initial run state | `runs.state` = `queued`; the rest of the run state machine belongs to epics BSB-25 to BSB-27 |
| Run kind | `runs.kind` = `run` (the `reverify` kind belongs to epic BSB-29) |

The `runs` row a successful start returns and persists is exactly these columns:

| Column | Value at run start |
|--------|--------------------|
| `id` | the next value of the fixture sequence, `1` |
| `project_id` | the `project_id` in the path |
| `user_id` | the caller's local `users.id` |
| `skill` | the request's `skill` |
| `skills_ref` | the request's `skills_ref` |
| `skills_commit_sha` | `NULL` — epic BSB-25 resolves the branch to a SHA |
| `input_branch` | the request's `input_branch` |
| `run_branch` | `NULL` — epic BSB-25 creates it |
| `context` | the request's context, or `{}` when omitted |
| `model_profile_id` | the request's `model_profile_id` |
| `tier` | the request's `tier` |
| `agent_image_digest`, `stepkit_version`, `verify_version` | `NULL` — epic BSB-26 records them |
| `state` | `queued` |
| `claimed_verdict`, `final_verdict`, `verification`, `cost_usd` | `NULL` |
| `parent_run_id` | `NULL` — re-runs belong to epic BSB-27 |
| `kind` | `run` |
| `created_at` | the database clock, `2026-11-15T10:00:00Z` |

The successful start response body is exactly:

```
{"id":1,"project_id":7,"user_id":42,"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","context":{},"model_profile_id":3,"tier":"high","state":"queued","kind":"run","created_at":"2026-11-15T10:00:00Z"}
```

For any other admitted request, the same object with that request's `user_id`, `skill`,
`skills_ref`, `input_branch`, `context`, `model_profile_id` and `tier`; `context` keys are emitted
in the order `workflow`, `step`, `reviewer_feedback`, `upstream_handoff`.

**Run-start request fields.** The body is a JSON object with:

| Field | Required | Type and rule |
|-------|----------|---------------|
| `skill` | yes | non-empty string after trimming leading and trailing ASCII spaces |
| `skills_ref` | yes | non-empty string after trimming; must name a branch of `saraavrnd/bheembhai-skills` |
| `input_branch` | yes | non-empty string after trimming; must name a branch of the project's sandbox repository |
| `model_profile_id` | yes | JSON integer; must be the `id` of a profile in the project's `ai_model` integration |
| `tier` | yes | non-empty string; must be a key of the selected profile's `tiers` mapping |
| `context` | no | JSON object; when omitted the stored context is `{}` |
| `context.workflow` | no | string; must name a workflow in the selected skills branch's `config/`; when supplied, `context.step` is required |
| `context.step` | no | string; must name a step of `context.workflow`; when supplied, `context.workflow` is required |
| `context.reviewer_feedback` | no | JSON string, stored unchanged |
| `context.upstream_handoff` | no | JSON object, stored unchanged; its internal shape belongs to the platform step kit |

An unknown top-level field — a key not in this table — is ignored: it is neither stored nor
refused, and only the fields above reach validation and the `runs` row.

The options response for `GET .../runs/options?skills_ref=test/ada/fix-reproduce` is exactly:

```
{"skills_branches":["build/sdlc-fix-bug-triage","main","test/ada/fix-reproduce","test/ada/fix-reproduce-2","test/grace/fix-reproduce"],"input_branches":["fixtures/blocked-handoff","fixtures/empty-title","main","test/ada/run-7-output"],"workflows":[{"name":"bug-fix","steps":["triage","reproduce","root-cause","implement"]},{"name":"smoke","steps":["triage"]}],"model_profiles":[{"id":3,"name":"Anthropic test","tiers":["high","medium"]},{"id":4,"name":"Smoke","tiers":["medium"]}]}
```

Branch names are ordered ascending by plain byte comparison; workflows are ordered by `name`;
profiles are ordered by `id`; tier keys are ordered ascending by plain byte comparison. When
`skills_ref` is absent from the query, `workflows` is `[]`. When it names no branch, `workflows` is
`[]`; branch existence is enforced by the start API, not by the options API.

**Validation order** on the start API is fixed: epic BSB-18's session gate (401
`authentication_required`), then BSB-18's group gate (403 `not_a_member`), then project resolution
(404 `project_not_found`), then project membership (403 `project_membership_required`), then the
field stage, then the integration-and-branch stage, then the workflow stage, then the model stage,
and only then the `runs` row.

- **Field stage**, in order: `skill_required`, `skills_ref_required`, `input_branch_required`,
  `model_profile_required`, `model_profile_invalid`, `tier_required`, `context_invalid`
  (including an unknown context key), `step_required` / `workflow_required`,
  `reviewer_feedback_invalid`, `upstream_handoff_invalid`. An unknown top-level field is ignored
  and produces no error.
- **Integration-and-branch stage**, in order: `source_control_not_configured`,
  `skills_branch_not_found`, `input_branch_not_found`.
- **Workflow stage**, in order: `workflow_not_found`, `step_not_found`.
- **Model stage**, in order: `model_profile_not_found`, `model_tier_not_mapped`.

A refused start creates no `runs` row, no branch and no bundle. The options API applies the
same BSB-18 gates and the same project resolution and membership check before returning choices.

Where this contract says the request fields, the response or the `runs` row is "exactly"
something, it means exactly as of this epic: epic BSB-27 later extends the route with turn and
spend cap request fields and `runs` columns (FR-050, FR-052; SK-001 §9 has no cap columns yet) and
the FR-054/FR-055 start refusals.

**Error responses** (each has `Content-Type: application/json`):

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| `skill` is missing, empty, or whitespace only after trimming | 422 | `{"error":{"code":"skill_required","message":"A skill is required."}}` |
| `skills_ref` is missing, empty, or whitespace only after trimming | 422 | `{"error":{"code":"skills_ref_required","message":"A skills branch is required."}}` |
| `skills_ref` names no branch of `saraavrnd/bheembhai-skills` | 422 | `{"error":{"code":"skills_branch_not_found","message":"Skills branch 'test/ada/missing' does not exist."}}` |
| `input_branch` is missing, empty, or whitespace only after trimming | 422 | `{"error":{"code":"input_branch_required","message":"An input branch is required."}}` |
| `input_branch` names no branch of the project's sandbox repository | 422 | `{"error":{"code":"input_branch_not_found","message":"Input branch 'fixtures/missing' does not exist."}}` |
| The project has no source-control (`github`) integration | 422 | `{"error":{"code":"source_control_not_configured","message":"Project 8 has no source-control integration."}}` |
| `context` is present and is not a JSON object | 422 | `{"error":{"code":"context_invalid","message":"The context must be a JSON object."}}` |
| `context` contains a key other than `workflow`, `step`, `reviewer_feedback`, `upstream_handoff` | 422 | `{"error":{"code":"context_invalid","message":"The context contains an unknown key 'foo'."}}` |
| `context.workflow` is supplied without `context.step` | 422 | `{"error":{"code":"step_required","message":"A step is required when a workflow is supplied."}}` |
| `context.step` is supplied without `context.workflow` | 422 | `{"error":{"code":"workflow_required","message":"A workflow is required when a step is supplied."}}` |
| `context.workflow` names no workflow on the selected skills branch | 422 | `{"error":{"code":"workflow_not_found","message":"Workflow 'release' does not exist on skills branch 'test/ada/fix-reproduce'."}}` |
| `context.step` names no step of the selected workflow | 422 | `{"error":{"code":"step_not_found","message":"Step 'deploy' does not exist in workflow 'smoke'."}}` |
| `context.reviewer_feedback` is present and is not a JSON string | 422 | `{"error":{"code":"reviewer_feedback_invalid","message":"Reviewer feedback must be a string."}}` |
| `context.upstream_handoff` is present and is not a JSON object | 422 | `{"error":{"code":"upstream_handoff_invalid","message":"The upstream handoff must be a JSON object."}}` |
| `model_profile_id` is missing | 422 | `{"error":{"code":"model_profile_required","message":"A model profile is required."}}` |
| `model_profile_id` is present and is not a positive JSON integer | 422 | `{"error":{"code":"model_profile_invalid","message":"model_profile_id must be a positive integer."}}` |
| `tier` is missing, empty, or whitespace only after trimming | 422 | `{"error":{"code":"tier_required","message":"A model tier is required."}}` |
| `model_profile_id` is not a profile of the project | 422 | `{"error":{"code":"model_profile_not_found","message":"Model profile 99 does not exist in project 7."}}` |
| `tier` is not a key of the selected profile's `tiers` mapping | 422 | `{"error":{"code":"model_tier_not_mapped","message":"Model profile 3 has no model mapping for tier 'low'."}}` |
| The caller is not a member of the project | 403 | `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}` |
| The project id does not exist | 404 | `{"error":{"code":"project_not_found","message":"Project 999 does not exist."}}` |

In every `skills_branch_not_found`, `input_branch_not_found`, `source_control_not_configured`,
`workflow_not_found`, `model_profile_not_found` and `model_tier_not_mapped` body, the quoted or
numeric value is the value from the request or path. The 401 and 403 bodies of the BSB-18 gates are
fixed by BSB-18 and are not restated here.

**Cross-epic note — BSB-22's run-start fixture.** Epic BSB-22 owns the project and membership rules,
and its BSB-22-PENDING-4 fixes `POST /api/projects/{project_id}/runs` as the shared run-start route
with the request fields `skill`, `skills_ref` and `input_branch`. This epic owns the full contract
of that route. BSB-22-PENDING-4's scenarios predate this epic: their run-start bodies omit
`model_profile_id` and `tier`, and their fixture for project `7` has no `github` or `ai_model`
integration. That story's Notes explicitly permit its shared fixture to be re-pointed in a revise
pass. To keep BSB-22-PENDING-4 true, its run-start scenarios must use the `github` and `ai_model`
rows above and add `"model_profile_id":3,"tier":"high"` to the Ada and Grace request bodies; its
403 `project_membership_required`, 404 `project_not_found` and `runs`-row assertions do not change.
This epic does not edit BSB-22's files. BSB-22-PENDING-5's jira-only integration fixture is a
different scenario and is unchanged.

## STORY: BSB-24-PENDING-1

**Summary:** Start a run in a project I am a member of
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **to start a run in that project with an explicit run request**, so that **my run is queued against exactly the inputs I chose and people who are not project members cannot start one**.

### Acceptance Criteria

#### Scenario: Project owner starts a run and the validated request is queued
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows, including the `github` and `ai_model` rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 201
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"id":1,"project_id":7,"user_id":42,"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","context":{},"model_profile_id":3,"tier":"high","state":"queued","kind":"run","created_at":"2026-11-15T10:00:00Z"}`
And `SELECT project_id, user_id, skill, skills_ref, input_branch, model_profile_id, tier, state, kind FROM runs WHERE id = 1` returns exactly `7 | 42 | sdlc-fix-bug-triage | test/ada/fix-reproduce | main | 3 | high | queued | run`
And `SELECT context FROM runs WHERE id = 1` equals the JSON value `{}`
And `SELECT count(*) FROM runs WHERE id = 1 AND skills_commit_sha IS NULL AND run_branch IS NULL AND parent_run_id IS NULL` returns `1`
And `SELECT created_at FROM runs WHERE id = 1` equals the timestamptz `2026-11-15T10:00:00Z`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: A plain member, not only the owner, starts a run
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 43 | member`
And the `integrations` table contains the three fixture rows, including the `github` and `ai_model` rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/grace/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 201
And the response body is exactly `{"id":1,"project_id":7,"user_id":43,"skill":"sdlc-fix-bug-triage","skills_ref":"test/grace/fix-reproduce","input_branch":"main","context":{},"model_profile_id":3,"tier":"high","state":"queued","kind":"run","created_at":"2026-11-15T10:00:00Z"}`
And `SELECT project_id, user_id, skill, skills_ref, input_branch FROM runs WHERE id = 1` returns exactly `7 | 43 | sdlc-fix-bug-triage | test/grace/fix-reproduce | main`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: A non-member cannot start a run
Given project `7` exists with `owner_id` = `42`
And Alan has no `project_members` row for project `7`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Alan has a valid member session with local `users.id` = `44`
When Alan sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 403
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A run start against a missing project is refused
Given `SELECT count(*) FROM projects WHERE id = 999` returns `0`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/999/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 404
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"project_not_found","message":"Project 999 does not exist."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A run start without a skill is refused before any run is created
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"skill_required","message":"A skill is required."}}`
And `SELECT count(*) FROM runs` returns `0`

### Covered requirements (traceability)
- FR-037

### Out of scope
The project membership and ownership rules themselves (epic BSB-22); this story only applies BSB-22's
membership decision at the run-start route. The choice and validation of branches
(BSB-24-PENDING-2), workflow and step (BSB-24-PENDING-3), reviewer feedback and upstream handoff
(BSB-24-PENDING-4), and model profile and tier (BSB-24-PENDING-5). Resolving the skills branch to a
commit SHA, packaging the skill bundle and creating the run branch or baseline (epic BSB-25, FR-038
to FR-043). Executing the skill, recording component versions and classifying the outcome (epic
BSB-26). Turn and spend caps, deadline, static-scan refusal, re-runs and output chaining (epic
BSB-27 and epics BSB-31 and BSB-32). Run pages, history and comparison (epics BSB-33 to BSB-35).
Project and integration configuration (epics BSB-22 and BSB-23). The CLI (epic BSB-37).

### Notes / dependencies
- Depends on epic BSB-18 for the member session and local `users` rows, on epic BSB-22 for the
  project and its `project_members` rule (BSB-22-PENDING-1 to BSB-22-PENDING-3), and on epic BSB-23
  for the `github` and `ai_model` integrations (FR-029 to FR-036). The integration rows in the
  contract above are the minimum fixture this epic consumes; BSB-23 owns their full schemas.
- **Shares the route with BSB-22-PENDING-4.** That story owns the membership decision and fixes
  `POST /api/projects/{project_id}/runs`; this story owns the route's full request, response and
  `runs`-row contract. The cross-epic note in the contract preamble records the small fixture
  re-point BSB-22 needs.
- The `runs` row is the durable evidence that a run was started. It is written in one transaction
  only after every validation in the contract preamble passes. `skills_commit_sha`, `run_branch`,
  `agent_image_digest`, `stepkit_version`, `verify_version`, `claimed_verdict`, `final_verdict`,
  `verification`, `cost_usd` and `parent_run_id` stay `NULL` here; epic BSB-25 fills the first two,
  epic BSB-26 the version and verdict columns, and epic BSB-27 the parent.
- The initial `state` is `queued`. Epics BSB-25 to BSB-27 consume that value; this story does not
  transition it.
- The route is an API route under BSB-18's session and group gates; `/api/projects/{project_id}/runs`
  and the options route must be added to the set of authoring routes BSB-18's gate protects.
- A non-member is refused before branch validation or any run row, bundle, branch or container
  work: the scenarios assert `SELECT count(*) FROM runs` = `0`.
- `skill` is only checked for presence here. Whether that skill folder exists on the chosen skills
  branch is resolved by epic BSB-25 when it packs the branch.
- Epic BSB-27 extends this route: turn and spend cap request fields and `runs` columns (FR-050,
  FR-052; SK-001 §9 has no cap columns yet), and the FR-054/FR-055 refusals as stages before the
  `runs` row. "Exactly" in this contract means exactly as of this epic.
- Depends on epic BSB-23 giving each `ai_model` profile a stable positive integer `id` that is
  never reused within a project; if BSB-23 keys profiles differently, `model_profile_id` and its
  error codes are re-pointed, not only the fixture.

---

## STORY: BSB-24-PENDING-2

**Summary:** Choose the skills branch and input branch
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **the run start to offer the skills branches of the catalog and the input branches of the project's sandbox**, so that **I can choose the exact starting state for the run and a branch that does not exist is refused before anything is queued**.

### Acceptance Criteria

#### Scenario: Run-start page shows the branch choices
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows, including the `github` row for project `7`
And the catalog branch and sandbox branch fixtures exist as listed in the contract
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/projects/7/runs/new` carrying that `sb_session` cookie
Then the builder responds with HTTP status 200
And the `Content-Type` response header is `text/html; charset=utf-8`
And the response body contains the exact text `build/sdlc-fix-bug-triage`
And the response body contains the exact text `test/ada/fix-reproduce`
And the response body contains the exact text `test/ada/fix-reproduce-2`
And the response body contains the exact text `test/grace/fix-reproduce`
And the response body contains the exact text `fixtures/blocked-handoff`
And the response body contains the exact text `fixtures/empty-title`

#### Scenario: Submitting the run-start form creates the run through the start API
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch and sandbox branch fixtures exist as listed in the contract
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada fills in `sdlc-fix-bug-triage` as the skill, `test/ada/fix-reproduce` as the skills branch, `main` as the input branch, model profile `3` and tier `high` on `GET https://builder.skillbuilder.internal/projects/7/runs/new` and submits the form
Then the builder receives `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
And the builder responds with HTTP status 201
And the response body is exactly `{"id":1,"project_id":7,"user_id":42,"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","context":{},"model_profile_id":3,"tier":"high","state":"queued","kind":"run","created_at":"2026-11-15T10:00:00Z"}`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: Options API lists the skills branches and input branches
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows, including the `github` row for project `7`
And the catalog branch and sandbox branch fixtures exist as listed in the contract
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/options?skills_ref=test/ada/fix-reproduce` carrying that `sb_session` cookie
Then the builder responds with HTTP status 200
And the `Content-Type` response header is `application/json`
And the JSON response body's `skills_branches` value is exactly `["build/sdlc-fix-bug-triage","main","test/ada/fix-reproduce","test/ada/fix-reproduce-2","test/grace/fix-reproduce"]`
And the JSON response body's `input_branches` value is exactly `["fixtures/blocked-handoff","fixtures/empty-title","main","test/ada/run-7-output"]`

#### Scenario: The chosen skills branch and input branch are recorded on the run
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch and sandbox branch fixtures exist as listed in the contract
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce-2","input_branch":"fixtures/blocked-handoff","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 201
And the response body's `skills_ref` value is exactly `test/ada/fix-reproduce-2`
And the response body's `input_branch` value is exactly `fixtures/blocked-handoff`
And `SELECT skills_ref, input_branch FROM runs WHERE id = 1` returns exactly `test/ada/fix-reproduce-2 | fixtures/blocked-handoff`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: An empty skills branch is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"skills_ref_required","message":"A skills branch is required."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A skills branch that does not exist is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM branches WHERE name = 'test/ada/missing'` returns `0` for the catalog repository
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/missing","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"skills_branch_not_found","message":"Skills branch 'test/ada/missing' does not exist."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: An empty input branch is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"input_branch_required","message":"An input branch is required."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: An input branch that does not exist is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM branches WHERE name = 'fixtures/missing'` returns `0` for the sandbox repository
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"fixtures/missing","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"input_branch_not_found","message":"Input branch 'fixtures/missing' does not exist."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A project without a source-control integration cannot offer or start a run
Given project `8` exists with `owner_id` = `43`
And `project_members` contains row `8 | 43 | owner`
And the `integrations` table has no row for project `8`
And `SELECT count(*) FROM runs` returns `0`
And Grace has a valid member session with local `users.id` = `43`
When Grace sends `POST https://builder.skillbuilder.internal/api/projects/8/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/grace/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"source_control_not_configured","message":"Project 8 has no source-control integration."}}`
And `SELECT count(*) FROM runs` returns `0`

### Covered requirements (traceability)
- FR-145
- FR-146

### Out of scope
Creating, deleting, protecting or pushing to branches; the `github` integration's settings,
credentials and verification (epic BSB-23). Resolving the chosen skills branch to a commit SHA,
creating the run branch and recording the baseline (epic BSB-25, FR-038 to FR-043). Validating that
the chosen skill folder exists on the chosen branch (epic BSB-25). Workflow and step choice
(BSB-24-PENDING-3), reviewer feedback and upstream handoff (BSB-24-PENDING-4), and model profile and
tier choice (BSB-24-PENDING-5). Listing branches of any repository other than the catalog and the
project's sandbox repository. Accessibility of the branch controls on the run-start page (epic
BSB-38, FR-130 to FR-137 and NFR-012).

### Notes / dependencies
- Depends on BSB-24-PENDING-1 for the run-start route and the `runs` row, and on epic BSB-23 for the
  `github` integration (FR-030) and its credential. The `config.repo` and `config.base_branch`
  values in the contract are the minimum fixture; BSB-23 owns the full integration schema.
- The catalog repository `saraavrnd/bheembhai-skills` is the builder's fixed configuration; the
  sandbox repository comes from the project's `github` integration. Both branch lists are read
  through that integration's token without writing either repository.
- The options API and the run-start page apply the same BSB-18 session and group gates and the same
  BSB-22 project resolution and membership check as the start route. A non-member gets the BSB-22
  403 `project_membership_required` body and sees no branch data.
- The options API's `workflows` value is `[]` when `skills_ref` is absent or names no branch; the
  start route, not the options API, refuses a branch that does not exist.
- `source_control_not_configured` comes before both branch lookups: a project with no `github`
  integration is refused before either `skills_branch_not_found` or `input_branch_not_found` could
  be returned.
- An empty or whitespace-only branch value is a required-field failure (`skills_ref_required` or
  `input_branch_required`), not a not-found failure. A non-empty value that names no branch is
  `skills_branch_not_found` or `input_branch_not_found`. Both happen before a `runs` row is written.
- The input branch is read-only throughout the product (PRD §8, ADR §5). This story only lists and
  records it; it never writes to it.

---

## STORY: BSB-24-PENDING-3

**Summary:** Choose the workflow and step context
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **the run start to offer the workflows and steps declared on the chosen skills branch**, so that **the run takes its context vocabulary from the skill I am testing and an unknown workflow or step is refused before anything is queued**.

### Acceptance Criteria

#### Scenario: Options API lists the workflows and steps on the chosen skills branch
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows, including the `github` row for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and contains `config/bug-fix.yaml` and `config/smoke.yaml` as listed in the contract
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/options?skills_ref=test/ada/fix-reproduce` carrying that `sb_session` cookie
Then the builder responds with HTTP status 200
And the `Content-Type` response header is `application/json`
And the JSON response body's `workflows` value is exactly `[{"name":"bug-fix","steps":["triage","reproduce","root-cause","implement"]},{"name":"smoke","steps":["triage"]}]`

#### Scenario: Run-start page shows the workflow and step choices on the chosen branch
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows, including the `github` row for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and contains `config/bug-fix.yaml` and `config/smoke.yaml` as listed in the contract
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/projects/7/runs/new?skills_ref=test/ada/fix-reproduce` carrying that `sb_session` cookie
Then the builder responds with HTTP status 200
And the `Content-Type` response header is `text/html; charset=utf-8`
And the response body contains the exact text `bug-fix`
And the response body contains the exact text `smoke`
And the response body contains the exact text `triage`
And the response body contains the exact text `reproduce`
And the response body contains the exact text `root-cause`
And the response body contains the exact text `implement`

#### Scenario: The chosen workflow and step are recorded in the run context
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and contains `config/bug-fix.yaml` as listed in the contract
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix","step":"triage"}}`
Then the builder responds with HTTP status 201
And the response body's `context` value is exactly `{"workflow":"bug-fix","step":"triage"}`
And `SELECT context FROM runs WHERE id = 1` equals the JSON value `{"workflow":"bug-fix","step":"triage"}`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: A workflow that does not exist on the chosen branch is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and declares workflows `bug-fix` and `smoke` only
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"release","step":"triage"}}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"workflow_not_found","message":"Workflow 'release' does not exist on skills branch 'test/ada/fix-reproduce'."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A step that does not exist in the chosen workflow is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and workflow `smoke` declares only step `triage`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"smoke","step":"deploy"}}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"step_not_found","message":"Step 'deploy' does not exist in workflow 'smoke'."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A workflow supplied without a step is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix"}}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"step_required","message":"A step is required when a workflow is supplied."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A step supplied without a workflow is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"step":"triage"}}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"workflow_required","message":"A workflow is required when a step is supplied."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A context containing an unknown key is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix","step":"triage","foo":1}}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"context_invalid","message":"The context contains an unknown key 'foo'."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: An omitted context is recorded as an empty object
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 201
And the response body's `context` value is exactly `{}`
And `SELECT context FROM runs WHERE id = 1` equals the JSON value `{}`
And `SELECT count(*) FROM runs` returns `1`

### Covered requirements (traceability)
- FR-147

### Out of scope
Defining or validating the workflow config schema; the `config/` files are supplied with the skills
branch and the platform owns their format. Resolving the default workflow when the author omits the
context, and rendering the chosen context into `BB_CONTEXT` (epic BSB-26). Executing a workflow,
gates or routing (an explicit product non-goal). Branch choice and validation (BSB-24-PENDING-2),
reviewer feedback and upstream handoff (BSB-24-PENDING-4), and model profile and tier choice
(BSB-24-PENDING-5). Accessibility of the workflow and step controls on the run-start page (epic
BSB-38, FR-130 to FR-137 and NFR-012).

### Notes / dependencies
- Depends on BSB-24-PENDING-1 for the run-start route and the `runs` row, on BSB-24-PENDING-2 for the
  skills branch the workflow list is read from, and on epic BSB-23 for the `github` integration used
  to read the branch's `config/` directory.
- The workflows offered are the `workflow` values declared in the selected branch's `config/*.yaml`
  files and the steps are each file's ordered `steps` list. The contract fixes only those two keys;
  the rest of the file is the platform's config schema and is not read by this epic.
- A `context` object may carry only the fields in the contract preamble. `workflow` and `step` must
  be supplied together; a supplied `workflow` without `step` is `step_required`, and a supplied
  `step` without `workflow` is `workflow_required`. Any other key is `context_invalid` with the
  message naming that key.
- Context is optional, as in ADR §5: when it is omitted the run row's `context` is `{}` and the
  default workflow resolution is left to epic BSB-26. This story records only an explicit choice.
- `step_required`, `workflow_required` and `context_invalid` (including an unknown context key) are
  field-stage checks; `workflow_not_found` and `step_not_found` happen after branch validation.
  All of them happen before any `runs` row is written; the scenarios assert
  `SELECT count(*) FROM runs` = `0`.
- `runs.context` is the durable record of the choice; the run-start page and the options API read the
  same `config/` files so the offered values and the accepted values cannot drift.

---

## STORY: BSB-24-PENDING-4

**Summary:** Optionally supply reviewer feedback or an upstream handoff
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **to optionally attach reviewer feedback or an upstream handoff to a run**, so that **I can test a send-back or a BLOCK hand-off without changing the skill**.

### Acceptance Criteria

#### Scenario: Reviewer feedback is recorded on the run
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and declares workflow `bug-fix` as listed in the contract
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix","step":"triage","reviewer_feedback":"Please handle an empty issue title without failing."}}`
Then the builder responds with HTTP status 201
And the response body's `context` value is exactly `{"workflow":"bug-fix","step":"triage","reviewer_feedback":"Please handle an empty issue title without failing."}`
And `SELECT context FROM runs WHERE id = 1` equals the JSON value `{"workflow":"bug-fix","step":"triage","reviewer_feedback":"Please handle an empty issue title without failing."}`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: An upstream handoff is recorded on the run
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and declares workflow `bug-fix` as listed in the contract
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix","step":"triage","upstream_handoff":{"step":"reproduce","result_status":"completed","summary":"Reproduction confirmed on the input branch."}}}`
Then the builder responds with HTTP status 201
And the response body's `context` value is exactly `{"workflow":"bug-fix","step":"triage","upstream_handoff":{"step":"reproduce","result_status":"completed","summary":"Reproduction confirmed on the input branch."}}`
And `SELECT context FROM runs WHERE id = 1` equals the JSON value `{"workflow":"bug-fix","step":"triage","upstream_handoff":{"step":"reproduce","result_status":"completed","summary":"Reproduction confirmed on the input branch."}}`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: Reviewer feedback and an upstream handoff may be supplied together
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and declares workflow `bug-fix` as listed in the contract
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix","step":"triage","reviewer_feedback":"Please handle an empty issue title without failing.","upstream_handoff":{"step":"reproduce","result_status":"completed","summary":"Reproduction confirmed on the input branch."}}}`
Then the builder responds with HTTP status 201
And the response body's `context` value is exactly `{"workflow":"bug-fix","step":"triage","reviewer_feedback":"Please handle an empty issue title without failing.","upstream_handoff":{"step":"reproduce","result_status":"completed","summary":"Reproduction confirmed on the input branch."}}`
And `SELECT context FROM runs WHERE id = 1` equals the JSON value `{"workflow":"bug-fix","step":"triage","reviewer_feedback":"Please handle an empty issue title without failing.","upstream_handoff":{"step":"reproduce","result_status":"completed","summary":"Reproduction confirmed on the input branch."}}`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: Neither optional value is required
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and declares workflow `bug-fix` as listed in the contract
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix","step":"triage"}}`
Then the builder responds with HTTP status 201
And the response body's `context` value is exactly `{"workflow":"bug-fix","step":"triage"}`
And `SELECT jsonb_object_keys(context) FROM runs WHERE id = 1` returns exactly two rows, `workflow` and `step`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: Run-start page offers the optional feedback and handoff fields
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the catalog branch `test/ada/fix-reproduce` exists and declares workflow `bug-fix` as listed in the contract
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/projects/7/runs/new?skills_ref=test/ada/fix-reproduce` carrying that `sb_session` cookie
Then the builder responds with HTTP status 200
And the `Content-Type` response header is `text/html; charset=utf-8`
And the response body contains the exact text `name="reviewer_feedback"`
And the response body contains the exact text `name="upstream_handoff"`
And the `upstream_handoff` field is a text area whose value is parsed as a JSON object when the form is submitted

#### Scenario: Reviewer feedback that is not a string is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix","step":"triage","reviewer_feedback":42}}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"reviewer_feedback_invalid","message":"Reviewer feedback must be a string."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: An upstream handoff that is not an object is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":{"workflow":"bug-fix","step":"triage","upstream_handoff":"reproduce completed"}}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"upstream_handoff_invalid","message":"The upstream handoff must be a JSON object."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A context that is not an object is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high","context":"bug-fix triage"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"context_invalid","message":"The context must be a JSON object."}}`
And `SELECT count(*) FROM runs` returns `0`

### Covered requirements (traceability)
- FR-148

### Out of scope
The internal schema and meaning of `upstream_handoff` and `reviewer_feedback`; the platform step kit
owns them. Rendering these values into `BB_CONTEXT` (epic BSB-26). Gate routing, send-back handling
or BLOCK hand-off behaviour (an explicit product non-goal for this epic). Workflow and step choice
(BSB-24-PENDING-3), branch choice (BSB-24-PENDING-2), and model profile and tier choice
(BSB-24-PENDING-5). Persisting feedback or a handoff outside the run row, or editing either after
the run starts. Accessibility of the feedback and handoff controls on the run-start page (epic
BSB-38, FR-130 to FR-137 and NFR-012).

### Notes / dependencies
- Depends on BSB-24-PENDING-1 for the run-start route and the `runs` row, on BSB-24-PENDING-3 for the
  `context` object that carries these fields, and on epic BSB-23 for the `github` integration used to
  read the skills branch's workflow config.
- `reviewer_feedback` is accepted only as a JSON string and is stored unchanged. An empty string is
  stored as the empty string; the field is optional, so omitting it is the normal case.
- `upstream_handoff` is accepted only as a JSON object and is stored unchanged. Its internal shape
  (`step`, `result_status`, `summary` in the fixture) is the platform step kit's contract, not this
  epic's; the builder does not inspect or rewrite it. The fixture value is the one the step kit's
  `BB_CONTEXT` builder consumes (ADR §2a).
- The two fields are independent and may be supplied together; ADR §5 lists them as alternatives for
  testing a send-back or a BLOCK hand-off, and carrying both tests both paths in one run.
- An omitted `context`, or a context with only `workflow` and `step`, carries neither key. No null
  placeholders are added, so the stored context is exactly the allowed keys the author supplied.
- The page's `upstream_handoff` control is a text area whose value is parsed as a JSON object before
  the start API is called; a value that is not a JSON object surfaces the same
  `upstream_handoff_invalid` 422 as the API scenario above.
- `reviewer_feedback_invalid` and `upstream_handoff_invalid` are field-stage checks, before branch
  validation. Both happen before any `runs` row is written; the scenarios assert
  `SELECT count(*) FROM runs` = `0`.

---

## STORY: BSB-24-PENDING-5

**Summary:** Choose the model profile and model tier
**Epic:** BSB-24 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **the run start to offer the project's model profiles and the tiers each profile maps**, so that **I can choose the model for this run and a profile that cannot map the chosen tier is refused before anything is queued**.

### Acceptance Criteria

#### Scenario: Options API lists the model profiles and their tiers
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows, including the `ai_model` row for project `7`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/options?skills_ref=test/ada/fix-reproduce` carrying that `sb_session` cookie
Then the builder responds with HTTP status 200
And the `Content-Type` response header is `application/json`
And the JSON response body's `model_profiles` value is exactly `[{"id":3,"name":"Anthropic test","tiers":["high","medium"]},{"id":4,"name":"Smoke","tiers":["medium"]}]`

#### Scenario: Run-start page shows the model profiles and their tiers
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows, including the `ai_model` row for project `7`
And the catalog branch `test/ada/fix-reproduce` exists as listed in the contract
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `GET https://builder.skillbuilder.internal/projects/7/runs/new?skills_ref=test/ada/fix-reproduce` carrying that `sb_session` cookie
Then the builder responds with HTTP status 200
And the `Content-Type` response header is `text/html; charset=utf-8`
And the response body contains the exact text `Anthropic test`
And the response body contains the exact text `Smoke`
And the response body contains the exact text `high`
And the response body contains the exact text `medium`

#### Scenario: The chosen model profile and tier are recorded on the run
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":4,"tier":"medium"}`
Then the builder responds with HTTP status 201
And the response body's `model_profile_id` value is exactly `4`
And the response body's `tier` value is exactly `medium`
And `SELECT model_profile_id, tier FROM runs WHERE id = 1` returns exactly `4 | medium`
And `SELECT count(*) FROM runs` returns `1`

#### Scenario: A missing model profile is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"model_profile_required","message":"A model profile is required."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A model profile that is not in the project is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the project's `ai_model` integration contains profiles `3` and `4` only
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":99,"tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"model_profile_not_found","message":"Model profile 99 does not exist in project 7."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A missing model tier is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"tier_required","message":"A model tier is required."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A missing tier is refused before the skills branch is looked up
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And `SELECT count(*) FROM branches WHERE name = 'test/ada/missing'` returns `0` for the catalog repository
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/missing","input_branch":"main","model_profile_id":3}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"tier_required","message":"A model tier is required."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A profile without a mapping for the chosen tier is refused
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the three fixture rows for project `7`
And the project's `ai_model` integration maps profile `3` to tiers `high` and `medium` only
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"low"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"model_tier_not_mapped","message":"Model profile 3 has no model mapping for tier 'low'."}}`
And `SELECT count(*) FROM runs` returns `0`

#### Scenario: A project without an AI-model integration cannot start a run
Given project `7` exists with `owner_id` = `42`
And `project_members` contains row `7 | 42 | owner`
And the `integrations` table contains the `jira` and `github` rows for project `7` but no `ai_model` row
And `SELECT count(*) FROM runs` returns `0`
And Ada has a valid member session with local `users.id` = `42`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs` with `Content-Type: application/json` and body exactly `{"skill":"sdlc-fix-bug-triage","skills_ref":"test/ada/fix-reproduce","input_branch":"main","model_profile_id":3,"tier":"high"}`
Then the builder responds with HTTP status 422
And the `Content-Type` response header is `application/json`
And the response body is exactly `{"error":{"code":"model_profile_not_found","message":"Model profile 3 does not exist in project 7."}}`
And `SELECT count(*) FROM runs` returns `0`

### Covered requirements (traceability)
- FR-149
- FR-150

### Out of scope
Configuring model profiles, their vendor, base URL, tier-to-model mapping or credentials (epic
BSB-23, FR-031, FR-032 and FR-036). Making model calls, recording the model profile or tier at
execution (FR-049 and FR-152, epic BSB-26), and the project's LLM-scan default model (FR-163, epic
BSB-32). Turn and spend caps (epic BSB-27). Branch choice (BSB-24-PENDING-2), workflow and step
choice (BSB-24-PENDING-3), and reviewer feedback and upstream handoff (BSB-24-PENDING-4).
Preselecting the tier from the skill's declared `model:` value in `SKILL.md`; the page offers each
profile's tier keys and the author chooses explicitly. Accessibility of the profile and tier
controls on the run-start page (epic BSB-38, FR-130 to FR-137 and NFR-012).

### Notes / dependencies
- Depends on BSB-24-PENDING-1 for the run-start route and the `runs` row, and on epic BSB-23 for the
  `ai_model` integration (FR-031) and its credential. The `config.profiles` shape in the contract is
  the minimum fixture this epic consumes; BSB-23 owns the full integration schema, so if it names a
  field differently only this fixture is re-pointed.
- The tier vocabulary is not fixed by the PRD: it is the set of keys in the selected profile's
  `tiers` mapping, and the run-start page offers exactly those keys. The fixture uses `high` and
  `medium`, and profile `3` deliberately has no `low` mapping so the epic's stated edge case is
  testable.
- The model profile and the tier are both required, matching the epic's goal that the author
  explicitly choose the model profile and model tier. There is no installation-level or
  project-level fallback: a project with no `ai_model` integration, or a profile id it does not
  own, is refused before a `runs` row is written. ADR §5's default is the skill's declared `model:`
  tier; preselecting it from `SKILL.md` is out of scope (see Out of scope), and the API records the
  explicit `tier` value the author submits.
- The `runs.model_profile_id` and `runs.tier` columns are the durable record of the choice; epic
  BSB-26 records the model profile and tier actually used for the execution (FR-049 and FR-152).
- The selected profile's model mapping values are not exposed by the options API and are not part
  of this epic's contract; the runner resolves them from the profile when the run is prepared.
- `model_profile_required`, `model_profile_invalid` and `tier_required` are field-stage checks;
  `model_profile_not_found` and `model_tier_not_mapped` happen after branch and workflow
  validation. All of them happen before any `runs` row is written; the scenarios assert
  `SELECT count(*) FROM runs` = `0`.
- Making `model_profile_id` and `tier` required changes the shared run-start body
  BSB-22-PENDING-4 uses; see the cross-epic note in the contract preamble.
- Turn and spend caps (epic BSB-27) are separate run-start inputs from the model profile and tier,
  so the options API may later carry cap defaults.
- Depends on epic BSB-23 giving each `ai_model` profile a stable positive integer `id` that is
  never reused within a project; if BSB-23 keys profiles differently, `model_profile_id` and its
  error codes are re-pointed, not only the fixture.

---

*Generated by `sdlc-plan-stories-write`. Coverage: FR-037 and FR-145 to FR-150 all covered. Next
steps: `sdlc-plan-epic-review` reviews the set, then `sdlc-tracker-sync` publishes the approved
stories to Jira.*
