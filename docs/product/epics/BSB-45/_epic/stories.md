# Stories — BSB-45 (Run setup & skill packaging)

Epic BSB-45 covers FR-037, FR-038, FR-039, FR-040, FR-041, FR-042, FR-043, FR-145, FR-146,
FR-147, FR-148, FR-149, FR-150, NFR-001 and NFR-009. It is decomposed into the 6 stories below;
every one of those 15 requirements is covered by at least one story's acceptance criteria.

**Prerequisite: identity, membership and the project record (FA-1 / BSB-39, FA-4 / BSB-43).**
BSB-39 owns sign-in, the builder's `users` table keyed by the Cognito `sub`, the `builder_session`
cookie and the request-time `skill-builders` group check. BSB-43 owns the test project,
`projects.owner_id`, `project_members`, the owner/member distinction and the rule that every
project member (owner or member) may start a run (`can_start_run`, BSB-43-PENDING-4). Every route
in this epic is an authoring route and inherits the FA-1 gate: no valid session is HTTP 401
`{"error":"authentication_required"}`, and a current `cognito:groups` claim without
`skill-builders` is HTTP 403 `{"error":"membership_required"}` before any run data is read or
written. The run-start page link is BSB-43's `data-testid="start-run"` element on the project page,
whose `href` is `/projects/{project_id}/runs/new`. The builder database is
`postgres://builder-db:5432/skillbuilder`.

**Prerequisite: integrations (FA-5 / BSB-44).** BSB-44 owns the project's `github` and `ai_model`
integration rows, their non-secret `config`, their `secret_ref` references and the external secret
store. This epic reads those rows and never writes them. The source-control credential is read
through `skill-builder/{project_id}/github` and the model credential through
`skill-builder/{project_id}/ai_model`, with `GetSecretValue` at the time of use. Administering the
secret store and provisioning the catalog and sandbox repositories are external prerequisites
(PRD §8).

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
unless a scenario's `Given` says so. Erin signed in while still in `skill-builders`, so her `users`
row exists, but her current claim no longer contains the group.

**Fixture projects.** BSB-45 uses the shared BSB-43 fixture database. The rows its scenarios rely on
are:

| `projects.id` | `name` | `owner_id` | `created_at` | `project_members` |
|---------------|--------|------------|--------------|-------------------|
| `prj_H5mQ2rT8vX` | Research quality | `U_alice` | `2026-11-16T09:00:00+00:00` | `(U_alice, owner)` |
| `prj_K9pL3wN6zB` | Release notes | `U_dana` | `2026-11-16T09:05:00+00:00` | `(U_dana, owner)` |

The database also contains BSB-43's `prj_M2vQ8kT4xD` / Erin rows even though no BSB-45 scenario uses
them. Scenarios add further `project_members` rows only where their `Given` says so.

**Fixture integrations.** The `integrations` table contains these two rows for
`prj_H5mQ2rT8vX` and no other row for that project unless a scenario's `Given` says so:

| `kind` | `integration_id` | `config` | `secret_ref` | `verified_at` |
|--------|------------------|----------|--------------|---------------|
| `github` | `int_Gh7kL2pQ9r` | `{"repository":"sandbox-org/skilltest","base_branch":"main"}` | `skill-builder/prj_H5mQ2rT8vX/github` | `2026-11-16T10:00:00+00:00` |
| `ai_model` | `int_Md4xN8sT2v` | `{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}}` | `skill-builder/prj_H5mQ2rT8vX/ai_model` | `2026-11-16T10:05:00+00:00` |

The secret store values are `ghp_aliceSandboxToken0123456789` at
`skill-builder/prj_H5mQ2rT8vX/github` and `sk-ant-alice-model-key` at
`skill-builder/prj_H5mQ2rT8vX/ai_model`. `prj_K9pL3wN6zB` has no integration row unless a scenario's
`Given` says so. Because BSB-44 allows at most one `integrations` row per `(project_id, kind)`, a
project has at most one `ai_model` profile; the run form offers that profile and the run request may
name it or omit it.

**Fixture catalog repository (`bheembhai-skills`).** The repository is BSB-41's fixture. Its
branches used by this epic are:

| Branch | Head SHA | What it contains |
|--------|----------|------------------|
| `main` | `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` | BSB-41's fixture: `skills/sdlc-research-summarise/`, `skills/sdlc-release-notes/`, `skills/sdlc-legacy-notes/` |
| `build/sdlc-research-summarise` | `9b2f4d6a8c0e2f5a7d1b3c6e8f0a2c4d6e8f1a3b` | `skills/sdlc-research-summarise/` copied from `main`, so its `SKILL.md` has `model: sonnet`, plus `config/sdlc-wf-research.yaml` |
| `test/saraav/research` | `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` | `skills/sdlc-research-summarise/` with `SKILL.md` `model: standard`; `config/sdlc-wf-research.yaml`; `config/sdlc-wf-audit.yaml` |
| `test/saraav/large` | `e2b4d6f8a0c2e4b6d8f0a2c4e6b8d0f2a4c6e8b0` | `skills/sdlc-research-summarise/` whose packed bundle is exactly 5,000,000 bytes |

`test/saraav/research`'s `skills/sdlc-research-summarise/` contains `SKILL.md`, `verify.yaml`,
`references/README.md`, `references/corpus.txt` (4,194,304 bytes of the byte `a`), `templates/brief.md`,
`examples/example-brief.md` and `assets/diagram.png` (2,048-byte PNG with a fixed byte pattern), the
same file set as BSB-41's fixture; only the `model:` value differs. The branch also keeps
`skills/sdlc-release-notes/` and `skills/sdlc-legacy-notes/` copied unchanged from `main`, so those
skills can be selected at that commit. Its `config/sdlc-wf-research.yaml`
is:

```yaml
workflow: sdlc-wf-research
version: 1
description: Research brief fixture workflow
start: sdlc-research-summarise
steps:
  - id: sdlc-research-summarise
    skill: sdlc-research-summarise
    model: standard
    label: Summarise the research
    "on":
      completed: DONE
      changes_requested: sdlc-research-summarise
```

Its `config/sdlc-wf-audit.yaml` is:

```yaml
workflow: sdlc-wf-audit
version: 1
description: Audit fixture workflow
start: sdlc-research-audit
steps:
  - id: sdlc-research-audit
    skill: sdlc-research-audit
    model: fast
    label: Audit the research
    "on":
      completed: DONE
```

Only `sdlc-wf-research` has a step whose `skill` is `sdlc-research-summarise`, so it is the default
workflow for that skill. `skills/sdlc-research-audit/` does not exist on the fixture branch; a
scenario that selects the audit workflow for `sdlc-research-summarise` is testing the step/skill
mismatch, not a runnable skill.

**Fixture sandbox repository (`sandbox-org/skilltest`).** This is the repository named by
`prj_H5mQ2rT8vX`'s `github` integration. Its branches are `main` at
`1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b`, `fixtures/bug-142` at
`5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c` and `fixtures/bug-143` at
`c4e2a8b6d0f1e3a5c7b9d1f3a5c7e9b1d3f5a7c9`. The repository's branch protection rejects a push
from the project's source-control credential to `main` and to `fixtures/*`; `skilltest/*` accepts
that credential's pushes. The input-branch content is test code and is not asserted.

**Fixture packer.** `tools/build.py` in the catalog repository packs one skill folder at one commit
into a deterministic archive and appends one line `pack <skills_commit_sha> <skill>` to the file named
by `BB_PACK_LOG` on every invocation. The fixture object store is `s3://builder-test` (endpoint
`http://s3.test:9000`); the fixture GitHub API is `https://api.github.test`.

**Run-start route and request contract.** `POST /api/projects/{project_id}/runs` takes
`Content-Type: application/json`. The body fields are:

- `skill` (required): a skill folder name; the folder `skills/{skill}/` must exist at the resolved
  skills commit.
- `skills_branch` (required): a branch of `bheembhai-skills`.
- `input_branch` (required): a branch of the project's configured sandbox repository; it must not
  start with `skilltest/`.
- `workflow` (optional): a workflow name defined in the resolved skills commit's `config/`; default is
  the workflow whose `start` step's `skill` equals `skill`.
- `step` (optional): a step of `workflow` whose `skill` equals `skill`; default is that step.
- `reviewer_feedback` (optional): a non-empty string.
- `upstream_handoff` (optional): an object with a non-empty string `from_step`, a `status` equal to
  one of `completed`, `BLOCK`, `changes_requested` or `escalation_required`, and an optional string
  `summary`.
- `model_profile_id` (optional): the project's `ai_model` `integration_id`; default is that id.
- `tier` (optional): one of `fast`, `standard`, `deep`; default is the skill's `model:` frontmatter
  value when that value is a key of the profile's `tier_models` mapping. There is no default when
  the value is not a tier key (BSB-41's fixture skills use `model: sonnet`).

The caller must be a project member (owner or member). A successful start is synchronous: the
builder prepares the run (resolves the skills commit, packages or reuses the bundle, creates the run
branch, records the baseline) and then responds with HTTP 201 and a JSON body whose fields are
`run_id` matching `^run_[0-9A-Za-z]{10}$`, `project_id`, `skill`, `skills_branch`,
`skills_commit_sha` matching `^[0-9a-f]{40}$`, `input_branch`, `run_branch` equal to
`skilltest/{run_id}`, `baseline_sha` matching `^[0-9a-f]{40}$`, `bundle_sha256` matching
`^[0-9a-f]{64}$`, `workflow`, `step`, `reviewer_feedback`, `upstream_handoff`, `model_profile_id`,
`tier`, `state` equal to `prepared` and `created_at` as an ISO-8601 UTC timestamp. A failure returns
one of the errors below and changes no `runs` row; a content-addressed bundle already written to the
cache may remain.

| Condition | Response |
|-----------|----------|
| No valid session | 401 `{"error":"authentication_required"}` |
| Current claim lacks `skill-builders` | 403 `{"error":"membership_required"}` |
| Project does not exist | 404 `{"error":"project_not_found"}` |
| Caller has no `project_members` row | 403 `{"error":"project_membership_required"}` |
| `skill` missing or blank | 422 `{"error":"skill_required"}` |
| `skills_branch` missing or blank | 422 `{"error":"skills_branch_required"}` |
| `input_branch` missing or blank | 422 `{"error":"input_branch_required"}` |
| Skills branch absent from `bheembhai-skills` | 404 `{"error":"skills_branch_not_found","branch":"{skills_branch}"}` |
| Input branch absent from the sandbox repository | 404 `{"error":"input_branch_not_found","branch":"{input_branch}"}` |
| Input branch starts with `skilltest/` | 422 `{"error":"input_branch_is_run_branch","branch":"{input_branch}"}` |
| No `skills/{skill}/` at the resolved commit | 404 `{"error":"skill_not_found","skill":"{skill}"}` |
| Workflow not defined in the commit's `config/` | 422 `{"error":"workflow_not_found","workflow":"{workflow}"}` |
| Step not in the workflow | 422 `{"error":"step_not_found","workflow":"{workflow}","step":"{step}"}` |
| Step's `skill` is not the selected skill | 422 `{"error":"step_skill_mismatch","step":"{step}","skill":"{skill}"}` |
| `reviewer_feedback` present but not a non-empty string | 422 `{"error":"invalid_reviewer_feedback"}` |
| `upstream_handoff` present but malformed | 422 `{"error":"invalid_upstream_handoff"}` |
| Project has no `ai_model` integration | 422 `{"error":"model_profile_missing"}` |
| `model_profile_id` is not the project's `ai_model` integration | 422 `{"error":"invalid_model_profile","model_profile_id":"{model_profile_id}"}` |
| No `tier` and no valid skill default | 422 `{"error":"tier_required"}` |
| `tier` not a key of `tier_models` | 422 `{"error":"tier_model_missing","tier":"{tier}"}` |
| GitHub API/branch creation unavailable | 503 `{"error":"source_control_unavailable"}` |
| Bundle upload unavailable | 503 `{"error":"bundle_store_unavailable"}` |
| BSB-51's verifier packaging gates reject the skill | 422 `{"error":"packaging_gates_failed"}` |

**Run record contract.** A successful start writes one `runs` row (SK-001 §9) whose `id` is
`run_id`, `project_id` is the route's project, `user_id` is the caller's `users.id`, `skill`,
`skills_ref` is the submitted `skills_branch`, `skills_commit_sha` is the resolved commit,
`input_branch` is the submitted branch, `run_branch` is `skilltest/{run_id}`, `context` is the JSONB
object `{"workflow": "{workflow}", "step": "{step}", "reviewer_feedback": {string or null},
"upstream_handoff": {object or null}}`, `model_profile_id`, `tier`, `state` `prepared`, `kind`
`run`, `parent_run_id` NULL, `baseline_sha` equal to the input branch's head SHA at branch creation,
and the row's timestamps. `agent_image_digest`, `stepkit_version`, `verify_version`,
`claimed_verdict`, `final_verdict`, `verification`, `cost_usd` are FA-7's and are NULL after this
epic. SK-001 §5 requires recording the input head as the run's baseline; §9's `runs` table lists no
explicit baseline column, so this epic records it in `runs.baseline_sha`. If the architecture pins a
different column name, only that name changes.

**Bundle contract.** At run start the builder resolves `skills_branch` to one commit SHA `S` and uses
`S` for every read (skill folder, `config/` workflows, `verify.yaml`). It packs `skills/{skill}/`
at `S` with `tools/build.py` into a content-addressed archive, computes `bundle_sha256` over the
archive bytes, uploads it to `s3://builder-test/bundles/{bundle_sha256}.tar.zst` and inserts one
`skill_bundles` row with `skills_commit_sha` `S`, `skill`, `bundle_sha256` and `s3_key`
`bundles/{bundle_sha256}.tar.zst` (SK-001 §9). The pair `(skills_commit_sha, skill)` is unique.
Packing is deterministic: the same `S` and `skill` always produce byte-identical archives and the
same `bundle_sha256` (NFR-009). Before a run reuses a cached bundle, the builder verifies that the
object exists and its bytes hash to `bundle_sha256`; a missing or mismatched object is re-packed from
`S`. BSB-51 (FA-10B) owns the verifier lint, self-test and `catalog.yaml` `requires_verify` gates; this
epic invokes them before a bundle is accepted.

**Run-branch and baseline contract.** The builder creates `skilltest/{run_id}` through the GitHub API
from the input branch's head and records that head as `baseline_sha` (FR-041, FR-042). The run's
output is committed only to `run_branch`; the project's source-control credential may push to
`skilltest/*` but the sandbox repository's protection rejects it on `main` and `fixtures/*`, so the
input branch cannot be written even outside application code (FR-043).

**Durable systems of record.** The `runs` row (including `skills_commit_sha`, `run_branch`,
`context`, `model_profile_id`, `tier` and `baseline_sha`) and the `skill_bundles` row plus its S3
object are the durable records (SK-001 §9). The two git branches (`skills_branch` in
`bheembhai-skills`, `input_branch` and the new `run_branch` in `sandbox-org/skilltest`) are the git
system of record. The acceptance criteria assert those rows, objects and refs, not a mock, temporary
copy or in-memory response alone.

**Scope boundary with later epics.** FA-3 (BSB-42) owns the build head and branch. FA-4 (BSB-43) owns
the project, membership and the run-start link. FA-5 (BSB-44) owns integration rows, credentials,
model profiles and MCP definitions. FA-7 (BSB-48) owns execution, launching the container, rendering
`BB_CONTEXT`, `BB_MODEL` and `BB_MCP_CONFIG`, and the run's later states and result. FA-8 (BSB-49)
owns guardrails, re-runs and their new runs. FA-9 (BSB-57) owns Jira fixture seeding. FA-10B (BSB-51)
owns the verifier packaging gates invoked here. FA-11/FA-12 (BSB-46/BSB-47) own scans. This epic
stops at a prepared run; no model tokens are spent in preparation.

## Coverage summary

| Story | Requirements covered |
|-------|----------------------|
| BSB-45-PENDING-1 — Start a run with the chosen skill and branches | FR-037, FR-145, FR-146 |
| BSB-45-PENDING-2 — Choose the workflow and step context with optional hand-off | FR-147, FR-148 |
| BSB-45-PENDING-3 — Choose the model profile and tier | FR-149, FR-150 |
| BSB-45-PENDING-4 — Pin the skills commit and package a content-addressed bundle | FR-038, FR-039, NFR-009 |
| BSB-45-PENDING-5 — Reuse an existing bundle for the same skills commit | FR-040 |
| BSB-45-PENDING-6 — Create the run branch, record the baseline and keep the input branch read-only | FR-041, FR-042, FR-043, NFR-001 |

> **Input note.** The run's placeholder work item `SkillBuilder-2` could not be retrieved: the
> configured Atlassian site returns HTTP 404 ("Issue does not exist or you do not have permission
> to see it") for that key, and the site's project list contains BEEM, BSB, EX, GRAP and LNPRTL
> with no `SkillBuilder` project. `claude mcp list` reports the Atlassian entry in `.mcp.json` as
> skipped (`args: expected array, received string`), so no Atlassian MCP tool was exposed in this
> session; the read-only Jira REST API was used instead. The epic `BSB-45` was fetched successfully
> (summary "Run setup & skill packaging", status To Do, labels FA-6 and MVP) and its description,
> functional scope, edge cases, non-goals, implementation guidance, Definition of Done, covered
> requirements and notes match `docs/product/epics.md`. The placeholder work item contributes no
> scope here.

---

## STORY: BSB-45-PENDING-1

**Title:** Start a run with the chosen skill and branches
**Epic:** BSB-45 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-6, MVP

### Story
As a **test-project member**, I want **to start a run by choosing the skill, its skills branch and the input branch**, so that **the skill is tested against the exact code and configuration I intend**.

### Acceptance Criteria
Scenario: The run form offers the documented skill and branch choices
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice opens `GET /projects/prj_H5mQ2rT8vX/runs/new`
Then the builder responds with HTTP 200 and HTML containing an element with `data-testid="run-form"`, a `select` with `data-testid="skills-branch"` whose options have values exactly `build/sdlc-research-summarise`, `main`, `test/saraav/large` and `test/saraav/research`, a `select` with `data-testid="input-branch"` whose options have values exactly `fixtures/bug-142`, `fixtures/bug-143` and `main`, and a `select` with `data-testid="skill"` whose options have values exactly `sdlc-legacy-notes`, `sdlc-release-notes` and `sdlc-research-summarise` (the skills on the initially selected `main` branch)

Scenario: A project member starts a run with an explicit skill and branches
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and Bob has a `builder_session` cookie
When Bob submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 201 and a JSON body whose `run_id` matches `^run_[0-9A-Za-z]{10}$`, whose `project_id` is `prj_H5mQ2rT8vX`, whose `skill` is `sdlc-research-summarise`, whose `skills_branch` is `test/saraav/research`, whose `skills_commit_sha` is `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, whose `input_branch` is `fixtures/bug-142`, whose `run_branch` is `skilltest/{run_id}` and whose `state` is `prepared`; the `runs` table contains exactly one row whose `id` is that `run_id`, whose `project_id` is `prj_H5mQ2rT8vX`, whose `user_id` is `U_bob`, whose `skill` is `sdlc-research-summarise`, whose `skills_ref` is `test/saraav/research`, whose `skills_commit_sha` is `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, whose `input_branch` is `fixtures/bug-142`, whose `run_branch` is `skilltest/{run_id}`, whose `kind` is `run`, whose `parent_run_id` is NULL and whose `state` is `prepared`

Scenario: A non-member cannot start a run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `builder_session` cookie, and the `project_members` table has no row for `prj_H5mQ2rT8vX` and `U_bob`
When Bob submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 403 and body exactly `{"error":"project_membership_required"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: An unknown input branch is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-999","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 404 and body exactly `{"error":"input_branch_not_found","branch":"fixtures/bug-999"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: An unknown skills branch is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/missing","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 404 and body exactly `{"error":"skills_branch_not_found","branch":"test/saraav/missing"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: An input branch named like a run branch is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"skilltest/run_Ab3dE5fG7h","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"input_branch_is_run_branch","branch":"skilltest/run_Ab3dE5fG7h"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: A request with no session is rejected
Given a visitor with no `builder_session` cookie
When the visitor submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 401 and body exactly `{"error":"authentication_required"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

### Covered requirements (traceability)
- FR-037
- FR-145
- FR-146

### Out of scope
The workflow/step and optional hand-off fields beyond accepting and storing them (BSB-45-PENDING-2); model profile and tier selection beyond accepting and storing them (BSB-45-PENDING-3); commit resolution and bundle packaging (BSB-45-PENDING-4 and BSB-45-PENDING-5); run-branch creation and baseline recording (BSB-45-PENDING-6); launching the container, rendering `BB_CONTEXT`, `BB_MODEL` or `BB_MCP_CONFIG`, and execution states (FA-7 / BSB-48); guardrails and re-runs (FA-8 / BSB-49); Jira fixture seeding (FA-9 / BSB-57); scans (FA-11 / FA-12).

### Notes / dependencies
Depends on FA-1 (BSB-39) for the `users` row, the `builder_session` cookie and the request-time `skill-builders` gate; on FA-4 (BSB-43) for `projects`, `project_members`, the member/owner distinction and the `data-testid="start-run"` link whose `href` this page serves; and on FA-5 (BSB-44) for the project's `github` integration that names the sandbox repository and holds the credential used to read branches. The run-start link is BSB-43's; this story owns the page and the start endpoint behind it. The form's branch options are read from `bheembhai-skills` and the project's sandbox repository with the project's source-control credential. The form initially selects `main` in both branch controls and lists the skills present on that commit. Starting a run creates the `runs` row only after preparation succeeds; the later preparation fields are asserted by BSB-45-PENDING-3, -4 and -6. The skills branch may be a `test/` or `build/` branch; this epic does not require it to be a build branch.

---

## STORY: BSB-45-PENDING-2

**Title:** Choose the workflow and step context with optional hand-off
**Epic:** BSB-45 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-6, MVP

### Story
As a **test-project member**, I want **to choose the workflow and step context for a run and optionally supply reviewer feedback or an upstream hand-off**, so that **the skill runs with the vocabulary and send-back inputs I am testing**.

### Acceptance Criteria
Scenario: The run form offers the workflow and step choices
Given the skills branch `test/saraav/research` at commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` and the selected skill `sdlc-research-summarise`
When a member opens `GET /projects/prj_H5mQ2rT8vX/runs/new?skills_branch=test/saraav/research&skill=sdlc-research-summarise`
Then the builder responds with HTTP 200 and HTML containing a `select` with `data-testid="run-workflow"` whose options have values exactly `sdlc-wf-audit` and `sdlc-wf-research`, and a `select` with `data-testid="run-step"` whose options have values exactly `sdlc-research-summarise`

Scenario: An omitted workflow and step default to the workflow that uses the skill
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and the `config/` at `test/saraav/research` commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` contains `sdlc-wf-research.yaml` and `sdlc-wf-audit.yaml`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","tier":"standard"}`
Then the builder responds with HTTP 201 and a JSON body whose `workflow` is `sdlc-wf-research`, whose `step` is `sdlc-research-summarise`, whose `reviewer_feedback` is `null` and whose `upstream_handoff` is `null`, and the `runs` row's `context` equals `{"workflow":"sdlc-wf-research","step":"sdlc-research-summarise","reviewer_feedback":null,"upstream_handoff":null}`

Scenario: An explicit workflow, step, reviewer feedback and upstream hand-off are recorded
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and the `config/` at `test/saraav/research` commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` contains `sdlc-wf-research.yaml`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","reviewer_feedback":"Tighten the summary to 300 words.","upstream_handoff":{"from_step":"sdlc-review","status":"changes_requested","summary":"The summary is too long."},"tier":"standard"}`
Then the builder responds with HTTP 201 and a JSON body whose `workflow` is `sdlc-wf-research`, whose `step` is `sdlc-research-summarise`, whose `reviewer_feedback` is `Tighten the summary to 300 words.` and whose `upstream_handoff` equals `{"from_step":"sdlc-review","status":"changes_requested","summary":"The summary is too long."}`, and the `runs` row's `context` equals `{"workflow":"sdlc-wf-research","step":"sdlc-research-summarise","reviewer_feedback":"Tighten the summary to 300 words.","upstream_handoff":{"from_step":"sdlc-review","status":"changes_requested","summary":"The summary is too long."}}`

Scenario: Malformed reviewer feedback is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","reviewer_feedback":{"text":"too long"},"tier":"standard"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_reviewer_feedback"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: Malformed upstream hand-off is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","upstream_handoff":{"status":"changes_requested"},"tier":"standard"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_upstream_handoff"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: An undefined workflow is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-missing","tier":"standard"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"workflow_not_found","workflow":"sdlc-wf-missing"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: A step that does not use the selected skill is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-audit","tier":"standard"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"step_skill_mismatch","step":"sdlc-research-audit","skill":"sdlc-research-summarise"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

### Covered requirements (traceability)
- FR-147
- FR-148

### Out of scope
Rendering `BB_CONTEXT` and launching the container with the selected context (FA-7 / BSB-48); executing or orchestrating the workflow, gates or routing (FA-7 and the product's non-goals); the skill selection itself (BSB-45-PENDING-1); model profile and tier (BSB-45-PENDING-3); choosing a reviewer or a gated step; validating the hand-off against a real prior run (the hand-off is an input object, not a lookup).

### Notes / dependencies
Depends on BSB-45-PENDING-1 for the run-start route and the resolved `skills_commit_sha`; the workflow files are read from `config/` at that commit, so a branch that moves after resolution cannot change the context (FR-038's pinning rule). The workflow format is the one the skills repository already uses (`config/*.yaml` with `workflow`, `version`, `start` and `steps[].skill`); this story reads `start` and `steps` and does not execute the `on:` routes. The default rule is "the workflow whose `start` step's `skill` equals the selected skill"; `sdlc-wf-audit` is offered but does not use the fixture skill, which is why selecting it is a mismatch rather than a runnable default. `runs.context` stores the selected values only; the step kit expands them into `allowed_result_statuses`, `result_status_meanings`, `gate_follows` and `gate_role` at launch (SK-001 §2a, FA-7). The optional hand-off deliberately has no lookup against a prior run: `upstream_handoff` is supplied as an object to test a send-back or BLOCK hand-off (SK-001 §5).

---

## STORY: BSB-45-PENDING-3

**Title:** Choose the model profile and tier
**Epic:** BSB-45 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-6, MVP

### Story
As a **test-project member**, I want **to choose the model profile and model tier for a run**, so that **the run uses the model endpoint and cost tier I intend**.

### Acceptance Criteria
Scenario: The run form offers the project model profile and the three tiers
Given project `prj_H5mQ2rT8vX` has the `ai_model` integration `int_Md4xN8sT2v` with config `{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}}`
When a member opens `GET /projects/prj_H5mQ2rT8vX/runs/new?skills_branch=test/saraav/research&skill=sdlc-research-summarise`
Then the builder responds with HTTP 200 and HTML containing a `select` with `data-testid="model-profile"` whose options have values exactly `int_Md4xN8sT2v`, and a `select` with `data-testid="model-tier"` whose options have values exactly `deep`, `fast` and `standard`

Scenario: An explicit profile and tier are recorded on the run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and the `ai_model` integration is `int_Md4xN8sT2v` with the tier mapping above
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","model_profile_id":"int_Md4xN8sT2v","tier":"deep"}`
Then the builder responds with HTTP 201 and a JSON body whose `model_profile_id` is `int_Md4xN8sT2v` and whose `tier` is `deep`, and the `runs` row has `model_profile_id` `int_Md4xN8sT2v` and `tier` `deep`

Scenario: Omitted choices default to the project profile and the skill's tier
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, the `ai_model` integration is `int_Md4xN8sT2v` with the tier mapping above, and `skills/sdlc-research-summarise/SKILL.md` at `test/saraav/research` commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` has `model: standard`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise"}`
Then the builder responds with HTTP 201 and a JSON body whose `model_profile_id` is `int_Md4xN8sT2v` and whose `tier` is `standard`, and the `runs` row has `model_profile_id` `int_Md4xN8sT2v` and `tier` `standard`

Scenario: A project with no model profile cannot start a run
Given project `prj_K9pL3wN6zB` is owned by Dana (`U_dana`), Dana has a `builder_session` cookie, and the `integrations` table has no row for `prj_K9pL3wN6zB` with `kind` `ai_model`
When Dana submits `POST /api/projects/prj_K9pL3wN6zB/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"model_profile_missing"}`, and the `runs` table gains no row for `project_id` `prj_K9pL3wN6zB`

Scenario: A model profile that is not the project's is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and Alice has a `builder_session` cookie
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","model_profile_id":"int_Zz9yX8wV7u","tier":"standard"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_model_profile","model_profile_id":"int_Zz9yX8wV7u"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: A tier that is not in the profile mapping is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and the `ai_model` integration is `int_Md4xN8sT2v` with the tier mapping above
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"economy"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"tier_model_missing","tier":"economy"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

Scenario: A skill with no tier default requires an explicit tier
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, the `ai_model` integration is `int_Md4xN8sT2v` with the tier mapping above, and `skills/sdlc-research-summarise/SKILL.md` at `build/sdlc-research-summarise` commit `9b2f4d6a8c0e2f5a7d1b3c6e8f0a2c4d6e8f1a3b` has `model: sonnet`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"build/sdlc-research-summarise","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"tier_required"}`, and the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`

### Covered requirements (traceability)
- FR-149
- FR-150

### Out of scope
Writing, validating or verifying the `ai_model` integration (FA-5 / BSB-44); resolving the chosen tier to `BB_MODEL`, the vendor key, the base URL and the provider credential at launch (FA-7 / BSB-48); scans' own model profile (FA-12 / BSB-47); spend and turn caps (FA-8 / BSB-49); changing the project's tier mapping per run (BSB-44 owns the mapping).

### Notes / dependencies
Depends on BSB-45-PENDING-1 for the run-start route and the resolved skills commit, and on FA-5 (BSB-44) for the project's `ai_model` integration, its `integration_id` and the `tier_models` mapping; the same `tier_model_missing` error name is used as BSB-44's model-profile validation. BSB-44 allows at most one `integrations` row per `(project_id, kind)`, so the project has exactly one model profile: the form offers it, and `runs.model_profile_id` stores its `integration_id` (SK-001 §9). The `model:` frontmatter is used as the default tier only when its value equals a key of `tier_models`; the BSB-41 fixture skills carry `model: sonnet`, which is a model family rather than a tier key, so a run of that branch must supply `tier` explicitly (`tier_required`). Mapping a model family to a tier is the platform ADR-013 §1 vocabulary, which is not present in this repository; if the architecture pins that mapping, only the default rule changes, not the stored `runs.tier` value. The model credential is read through its `skill-builder` secret reference at launch, not at run start; no model tokens are spent in preparation.

---

## STORY: BSB-45-PENDING-4

**Title:** Pin the skills commit and package a content-addressed bundle
**Epic:** BSB-45 · **Release:** MVP · **Estimate:** 8 · **Labels:** FA-6, MVP

### Story
As a **test-project member**, I want **the run to pin my skills branch to a commit and package that exact skill content into a content-addressed bundle**, so that **a run cannot be changed by a later edit to the branch and can be reproduced from its recorded commit**.

### Acceptance Criteria
Scenario: A run pins the skills branch and packs the skill at that commit
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, `test/saraav/research` is at commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, the `skill_bundles` table has no row for that commit and `skill` `sdlc-research-summarise`, and `BB_PACK_LOG` is empty
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 201 and a JSON body whose `skills_commit_sha` is `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` and whose `bundle_sha256` matches `^[0-9a-f]{64}$`; let `B` be that value; the `runs` row has `skills_ref` `test/saraav/research` and `skills_commit_sha` `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`; the `skill_bundles` table contains exactly one row with `skills_commit_sha` `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, `skill` `sdlc-research-summarise`, `bundle_sha256` `B` and `s3_key` `bundles/{B}.tar.zst`; `BB_PACK_LOG` contains exactly one line `pack d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9 sdlc-research-summarise`; the object at `s3://builder-test/bundles/{B}.tar.zst` exists; and the SHA-256 of that object's bytes equals `B`

Scenario: A branch that moves after one run does not change that run's bundle
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, `test/saraav/research` is at commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, and Alice has started run `run_Ab3dE5fG7h` from that branch
When the test advances `test/saraav/research` to a new commit `S2` whose `skills/sdlc-research-summarise/SKILL.md` contains the line `# Research summarise (changed)`, and Alice starts a second run from the same body
Then the first `runs` row's `skills_commit_sha` is still `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, its `skill_bundles` row and S3 object are unchanged, and the second `runs` row's `skills_commit_sha` is `S2` and its `bundle_sha256` differs from the first run's `bundle_sha256`

Scenario: Packing the same commit twice produces an identical bundle
Given the bundle for `test/saraav/research` commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` and skill `sdlc-research-summarise` has been packed once with `bundle_sha256` `B`, and the test deletes that `skill_bundles` row and its S3 object
When Alice starts a run from the same skills branch and skill again
Then the builder responds with HTTP 201 with `bundle_sha256` `B`, the new S3 object's bytes are byte-identical to the first bundle, and the new `skill_bundles` row has `bundle_sha256` `B`

Scenario: A skill that is not present at the resolved commit is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and `skills/sdlc-missing-skill/` does not exist at `test/saraav/research` commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-missing-skill","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 404 and body exactly `{"error":"skill_not_found","skill":"sdlc-missing-skill"}`, the `runs` table gains no row, and `BB_PACK_LOG` is unchanged

Scenario: An unavailable bundle store leaves no run and no bundle row
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and the fixture object store at `http://s3.test:9000` refuses TCP connections
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 503 and body exactly `{"error":"bundle_store_unavailable"}`, the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`, and the `skill_bundles` table gains no row for `test/saraav/research`'s commit and `sdlc-research-summarise`

Scenario: A skill that fails the packaging gates is refused before a bundle is accepted
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and `bheembhai-verify lint` at the resolved skills commit exits 1 for `skills/sdlc-research-summarise`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"packaging_gates_failed"}`, the `runs` table gains no row, the `skill_bundles` table gains no row for that commit and skill, and `BB_PACK_LOG` is unchanged

### Covered requirements (traceability)
- FR-038
- FR-039
- NFR-009

### Out of scope
Reusing a bundle that already exists for the same commit (BSB-45-PENDING-5); creating the run branch and recording the baseline (BSB-45-PENDING-6); rendering `BB_SKILL_URL` and `BB_SKILL_SHA256` at launch (FA-7 / BSB-48); the verifier lint, self-test and `requires_verify` gate logic itself (FA-10B / BSB-51); `tools/build.py`'s release packaging path; very large bundles above 5 MB (NFR-001 covers up to 5 MB only).

### Notes / dependencies
Depends on BSB-45-PENDING-1 for the run-start route and the selected skill and branches, and on FA-10B (BSB-51) for the verifier lint, self-test and `catalog.yaml` `requires_verify` gates this story invokes before accepting a bundle (FR-071 through FR-073; the epic's dependency order). The bundle format and content hash are the catalog packer's (`tools/build.py`); the same skills commit produces the same archive bytes (SK-001 §5, NFR-009). The resolved `S` is passed to the packer once and every later read uses `S`, which is the epic's "skills branch moving between SHA resolution and packaging" edge case. The `skill_bundles` row's `(skills_commit_sha, skill)` uniqueness and `s3_key` contract are BSB-45-PENDING-5's cache key. `bundle_sha256` is returned by this story and becomes `BB_SKILL_SHA256` at launch; the presigned `BB_SKILL_URL` is FA-7's. A failed preparation may leave a content-addressed object in the cache; it never leaves a `runs` row or a `skill_bundles` row for a rejected packaging attempt.

---

## STORY: BSB-45-PENDING-5

**Title:** Reuse an existing bundle for the same skills commit
**Epic:** BSB-45 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-6, MVP

### Story
As a **test-project member**, I want **a run of a commit that was already packaged to reuse that bundle**, so that **repeated runs of the same skill content prepare quickly and use identical bytes**.

### Acceptance Criteria
Scenario: A second run of the same commit reuses the bundle
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, `test/saraav/research` is at commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, a `skill_bundles` row for that commit and `sdlc-research-summarise` has `bundle_sha256` `B`, its S3 object is present and hashes to `B`, and `BB_PACK_LOG` contains one line
When Alice starts a second run from the same skills branch and skill
Then the builder responds with HTTP 201 with `bundle_sha256` `B`, `BB_PACK_LOG` still contains exactly one line, the `skill_bundles` table contains exactly one row for that commit and skill, and the fixture object store contains exactly one object under `s3://builder-test/bundles/`

Scenario: Concurrent runs of one commit share one bundle
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row with `role` `member`, both are signed in, `test/saraav/research` is at commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, and the bundle for that commit and skill is not cached
When Alice and Bob start a run with the same skills branch and skill at the same time
Then both requests respond with HTTP 201 and the same `bundle_sha256`, the `skill_bundles` table contains exactly one row for that commit and skill, the fixture object store contains exactly one object for that bundle, and `BB_PACK_LOG` contains exactly one `pack` line for that commit and skill

Scenario: A different skill at the same commit gets its own bundle
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, `test/saraav/research` is at commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9`, and a bundle for `sdlc-research-summarise` is cached
When Alice starts a run for `sdlc-release-notes` on the same skills branch
Then the builder responds with HTTP 201, the `skill_bundles` table contains one row for `sdlc-research-summarise` and one row for `sdlc-release-notes` with different `s3_key` values, and `BB_PACK_LOG` contains a `pack d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9 sdlc-release-notes` line

Scenario: A cached bundle whose bytes no longer match is re-packed
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, a `skill_bundles` row for `test/saraav/research` commit `d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9` and `sdlc-research-summarise` has `bundle_sha256` `B`, and the test overwrites the object at `s3://builder-test/bundles/{B}.tar.zst` with the bytes `corrupt`
When Alice starts a run from that skills branch and skill
Then the builder responds with HTTP 201 with `bundle_sha256` `B`, `BB_PACK_LOG` gains a `pack d1a3f5b7c9e1a3f5b7d9c1e3a5f7b9d1c3e5a7f9 sdlc-research-summarise` line, the `skill_bundles` row's `bundle_sha256` is still `B` and its `s3_key` is still `bundles/{B}.tar.zst`, and the object at `s3://builder-test/bundles/{B}.tar.zst` has been rewritten so that the SHA-256 of its bytes is `B`

### Covered requirements (traceability)
- FR-040

### Out of scope
The first packaging of a commit and the deterministic bundle format (BSB-45-PENDING-4); creating the run branch and recording the baseline (BSB-45-PENDING-6); evicting old bundles or enforcing a retention period; cross-project bundle sharing; the object store's own durability and lifecycle rules; launching the container with the bundle (FA-7 / BSB-48).

### Notes / dependencies
Depends on BSB-45-PENDING-4 for the packer, the `skill_bundles` row shape and `bundle_sha256`. The cache key is `(skills_commit_sha, skill)`; the S3 key is content-addressed (`bundles/{bundle_sha256}.tar.zst`), so two different commits never overwrite each other's object. Concurrency is resolved by the unique constraint on `(skills_commit_sha, skill)`: one start inserts, a racing start reads the winner's row after its insert conflict. Reuse verifies the object's bytes against `bundle_sha256` before accepting it; a missing object or a hash mismatch falls back to a re-pack rather than failing the run, which is the epic's "cached bundle whose content hash no longer matches" edge case. Reusing a bundle spends no model tokens and does not re-read the skill folder beyond the commit that is already pinned in the `runs` row.

---

## STORY: BSB-45-PENDING-6

**Title:** Create the run branch, record the baseline and keep the input branch read-only
**Epic:** BSB-45 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-6, MVP

### Story
As a **test-project member**, I want **the run to start a separate output branch from the input branch's head and to leave the input branch untouched**, so that **a run can never overwrite the test state it starts from and its output has a recorded baseline**.

### Acceptance Criteria
Scenario: A run creates the output branch from the input head and records the baseline
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and `fixtures/bug-142` is at commit `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 201 and a JSON body whose `run_id` matches `^run_[0-9A-Za-z]{10}$`, whose `run_branch` is `skilltest/{run_id}`, whose `baseline_sha` is `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c` and whose `state` is `prepared`; the sandbox repository's branch named by the response's `run_branch` has head commit `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c`; and the `runs` row for that `run_id` has `input_branch` `fixtures/bug-142`, the same `run_branch` value, `baseline_sha` `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c` and `state` `prepared`

Scenario: The input branch is unchanged after a run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, `fixtures/bug-142` is at commit `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c`, and a run `run_Ab3dE5fG7h` has been prepared from it and has pushed one commit to `skilltest/run_Ab3dE5fG7h`
When the test reads the input branch
Then `git rev-parse fixtures/bug-142` is still `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c`, `git log fixtures/bug-142` has no commit authored by the run, and `git rev-parse skilltest/run_Ab3dE5fG7h` is not `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c`

Scenario: A push to the input branch is refused while a push to the run branch succeeds
Given project `prj_H5mQ2rT8vX` has prepared run `run_Ab3dE5fG7h` with `run_branch` `skilltest/run_Ab3dE5fG7h`, the fixture sandbox repository protects `fixtures/*` against pushes from the project's source-control credential, and `skilltest/*` is unprotected
When the run's runtime pushes a commit to `fixtures/bug-142` and then pushes a commit to `skilltest/run_Ab3dE5fG7h`
Then the push to `fixtures/bug-142` is rejected by the GitHub API with HTTP 403, `git rev-parse fixtures/bug-142` is still `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c`, the push to `skilltest/run_Ab3dE5fG7h` succeeds, and `git rev-parse skilltest/run_Ab3dE5fG7h` differs from `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c`

Scenario: A branch-creation failure leaves no run
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, and the fixture GitHub API at `https://api.github.test` refuses TCP connections
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/research","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 503 and body exactly `{"error":"source_control_unavailable"}`, the `runs` table gains no row for `project_id` `prj_H5mQ2rT8vX`, and no branch matching `skilltest/*` is created in the sandbox repository

Scenario: A 5 MB run prepares within 60 seconds
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Alice has a `builder_session` cookie, the `test/saraav/large` skills branch produces a bundle of exactly 5,000,000 bytes, the bundle is not cached, and the fixtures are healthy
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/runs` with body `{"skill":"sdlc-research-summarise","skills_branch":"test/saraav/large","input_branch":"fixtures/bug-142","workflow":"sdlc-wf-research","step":"sdlc-research-summarise","tier":"standard"}`
Then the builder responds with HTTP 201 and `state` `prepared` no more than 60 seconds after receiving the request, and the run's `baseline_sha` is `5e7a9c1b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c`

### Covered requirements (traceability)
- FR-041
- FR-042
- FR-043
- NFR-001

### Out of scope
Resolving the skills commit and packaging or reusing the bundle (BSB-45-PENDING-4 and BSB-45-PENDING-5); executing the skill and pushing the run's actual output (FA-7 / BSB-48); re-runs and `parent_run_id` (FA-8 / BSB-49); deleting the run branch or its retention; the sandbox repository's branch-protection rules as a product deliverable (provisioning the curated sandbox repository and its protection is an external prerequisite); the verifier's use of the baseline for `must_change` (FA-10 / BSB-50); very large bundles above 5 MB and cold-start host tuning.

### Notes / dependencies
Depends on BSB-45-PENDING-1 for the run-start route and the input-branch validation, on BSB-45-PENDING-4 and BSB-45-PENDING-5 for the bundle that is prepared before the branch is created, and on FA-5 (BSB-44) for the source-control credential used to call the GitHub API. The run branch is `skilltest/{run_id}` (SK-001 §5) and `baseline_sha` is the input head at the moment the branch is created; `runs.baseline_sha` is this epic's explicit baseline record because SK-001 §9's `runs` table lists no baseline column while §5 requires the baseline (see the preface). FR-043 is enforced at the repository permission layer, not only in application code: the sandbox repository's protection rejects the project credential on `main` and `fixtures/*`, and only `skilltest/*` accepts its pushes. Provisioning the curated input branches and their protection is an external prerequisite (PRD §8 "External prerequisites"). NFR-001 is measured on the synchronous start request with a cold bundle cache and no model call; the 5 MB fixture is the requirement's stated upper bound, and a larger bundle is outside that budget.
