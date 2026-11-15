# Stories — BSB-30 (Readiness checks & re-verification)

Source: Jira epic **BSB-30** — *Readiness checks & re-verification* (feature area FA-10, release
MVP, labels FA-10, MVP), fetched read-only from the Atlassian project `bheembhai-skill-builder`;
its summary, description, functional scope, goal, stated edge cases and covered-requirement list
are the same as the BSB-30 section of `docs/product/epics.md`. The requirement IDs mapped to the
epic are in `docs/product/epic-map.json`.

Epic BSB-30 covers 8 requirements. They decompose into the 8 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-30`), is epic
**BSB-30**. The Atlassian MCP entry in `.mcp.json` is not usable in this session: its `args` value
is a string where Claude Code requires an array, so no Jira MCP tools were offered and the epic was
fetched read-only through the Atlassian REST API with the same credentials. Nothing was written to
Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-068 | BSB-30-PENDING-1 |
| FR-069 | BSB-30-PENDING-2, BSB-30-PENDING-3 |
| FR-070 | BSB-30-PENDING-4 |
| FR-071 | BSB-30-PENDING-5 |
| FR-072 | BSB-30-PENDING-5 |
| FR-073 | BSB-30-PENDING-6 |
| FR-074 | BSB-30-PENDING-7 |
| FR-075 | BSB-30-PENDING-8 |

The epic's two stated edge cases are covered explicitly: a check that has not run never counts as
passing (BSB-30-PENDING-2 and BSB-30-PENDING-3), and a re-verification against a different commit
never updates readiness for the build head (BSB-30-PENDING-3 and BSB-30-PENDING-7).

## Readiness, packaging and re-verification contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control, verifier and
scan-outcome fixture unless it says otherwise. The member session, the local `users` rows and the
`skill-builders` gate are established by epic BSB-18. The project, `projects` rows and
`project_members` rows are established by epic BSB-22. The build, its branch, `head_sha`,
`ready_sha` and the ready-clearing rule on a new commit are established by epic BSB-21 (FR-019,
FR-022); the build-creation shapes are epic BSB-20's. The bundle, skills-commit resolution, run
branch and baseline are epic BSB-25's (FR-038 to FR-043). Terminal run states, `claimed_verdict`
and the verification record are epics BSB-26 and BSB-29's; this epic consumes BSB-29's pass
predicate. The static scan outcome is epic BSB-31's (FR-076 to FR-080) and the LLM scan outcome is
epic BSB-32's (FR-082, FR-139); this epic consumes the outcome each records for a content SHA.
`builds`, `runs` and `skill_bundles` columns follow `docs/adr/SK-001-skill-builder.md` §1a, §5 and
§9; `runs.baseline_sha` and `runs.verify_version` are the values epics BSB-25 and BSB-26 record, as
used by epic BSB-29.

This epic adds two tables to that data model: `build_readiness` and `packaging_refusals` (Open
decision 1). Both are additive; no existing column changes meaning.

**`build_readiness` — the readiness aggregate.**

| Column | Type and value |
|--------|----------------|
| `build_id` | bigint; the `builds.id` |
| `sha` | 40-character lowercase hex commit SHA on the build branch |
| `manifest_state` | `passed` \| `failed` \| `not_run` |
| `run_state` | `passed` \| `failed` \| `not_run` |
| `static_state` | `passed` \| `failed` \| `not_run` |
| `llm_state` | `complete` \| `unavailable` \| `not_run` |
| `ready` | boolean; true only under the Ready rule below |
| `detail` | JSONB; per-check evidence (manifest exits and stderr, qualifying run id, scan ids) |
| `evaluated_at` | timestamptz |

Primary key `(build_id, sha)`. A row is created the first time readiness is evaluated for a
`(build_id, sha)` pair. Every check that has no evidence at that moment is stored as `not_run`;
absence of evidence is never stored as `passed`.

**Ready rule (FR-069).** `ready` is true exactly when `manifest_state` = `passed`, `run_state` =
`passed`, `static_state` = `passed` and `llm_state` is `complete` or `unavailable`. Every other
combination is false; `not_run` and `failed` are never a pass.

**Check inputs.**

- **Manifest.** Tier 1 on a checkout of the build branch at `sha`: the pinned verifier's
  `lint` command on the build's skill folder and `python tools/check.py` at the same checkout.
  `bheembhai-verify lint skills/sdlc-fix-bug-triage --require-all` must exit 0, then
  `python tools/check.py` must exit 0. The verifier distribution is the one
  `skill-builder/kit.json` pins as `bheembhai-verify`, `2.2.0` in the fixture. The result is
  cached per `(build_id, sha)`; a different SHA is checked against its own tree.
  `detail.manifest` holds `lint_exit` (integer or null), `lint_stderr` (string, empty when none),
  `check_py_exit` (integer or null), `check_py_stderr` (string, empty when none) and, only for an
  unreadable tree, `reason` = `manifest_unreadable`. Lint is run first; when it fails
  `check_py_exit` is null and `python tools/check.py` is not run.
- **Run.** At least one `runs` row with `kind` = `run`, `skill` = the build's skill,
  `skills_commit_sha` = `sha`, `final_verdict` = `completed` and `verification->>'status'` =
  `passed` (epic BSB-29's pass predicate). A `kind` = `reverify` row never counts. If no
  `kind` = `run` row exists for the `(skill, sha)`, `run_state` = `not_run`; if rows exist but none
  passes, `run_state` = `failed`. `detail.run_id` is the lowest qualifying run id.
- **Static.** The outcome epic BSB-31 recorded for the bundle content SHA of `(sha, build.skill)`
  — the `skill_bundles.bundle_sha256` of that pair: `passed` or `failed`. No bundle or no recorded
  result is `not_run`. `detail.static_scan_id` names the result.
- **LLM.** The outcome epic BSB-32 recorded for the same content SHA: `complete` or `unavailable`.
  No recorded result is `not_run`; a scan that cannot run is recorded `unavailable` by BSB-32 and
  permits Ready. `detail.llm_scan_id` names the result.

The static and LLM outcomes are consumed through the read interface
`readiness_scan_outcome(content_sha, kind)`, where `kind` is `static` or `llm`; epics BSB-31 and
BSB-32 own the storage behind it, so if they name a different table only that adapter changes
(Open decision 2).

**Ready-SHA write rule.** After evaluating `sha`: if `ready` is true and `builds.head_sha` = `sha`,
the builder sets `builds.ready_sha` = `sha`; if `ready` is false and `builds.head_sha` = `sha`, it
sets `builds.ready_sha` = `NULL`; when `sha` is not the head, the evaluation never changes
`builds.ready_sha`. Epic BSB-21's rule that a new commit clears `ready_sha` on save is unchanged.

**Readiness API.** `GET https://builder.skillbuilder.internal/api/builds/{build_id}/readiness`
evaluates the build's current `head_sha`; `?sha=<40 lowercase hex>` evaluates that SHA instead.
Response HTTP 200 `application/json`:

```
{"build_id":7,"sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","manifest":"passed","run":"passed","static":"passed","llm":"complete","ready":true,"ready_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b"}
```

The keys are exactly `build_id`, `sha`, `manifest`, `run`, `static`, `llm`, `ready`, `ready_sha`.
`ready_sha` is `builds.ready_sha` after the evaluation and is `null` when no SHA is ready. An
unknown build is HTTP 404 with body exactly
`{"error":{"code":"not_found","message":"Build not found"}}`. A request from a signed-in user
without current `skill-builders` membership is rejected by epic BSB-18's gate with HTTP 403 and
body exactly `{"error":{"code":"not_a_member","message":"You are not a member of the skill-builders group"}}`
before any readiness row is read or written.

**Build page (FR-070).** `GET https://builder.skillbuilder.internal/builds/{build_id}` is epic
BSB-20's page. This epic adds one section, `<section id="readiness-checks">`, rendered for the
build's current head SHA. It contains exactly four rows, each a `<div>` with the id and the exact
text:

| Element id | `passed` / `complete` | `failed` | `not_run` | `unavailable` |
|---|---|---|---|---|
| `readiness-manifest` | `Manifest: Passed` | `Manifest: Failed` | `Manifest: Not run` | — |
| `readiness-run` | `Run: Passed` | `Run: Failed` | `Run: Not run` | — |
| `readiness-static` | `Static scan: Passed` | `Static scan: Failed` | `Static scan: Not run` | — |
| `readiness-llm` | `LLM scan: Complete` | — | `LLM scan: Not run` | `LLM scan: Unavailable` |

All four rows are present on every build page, including before any check has run. The page
evaluates the head SHA's readiness on request. Epic BSB-21's overall readiness status and head-SHA
display (FR-020, FR-021) are consumed, not changed.

**Packaging preflight (FR-071 to FR-073).** Epic BSB-25 resolves the run's skills branch to
`skills_commit_sha` and then prepares its bundle. This epic adds a preflight as the first step of
that preparation, before `tools/build.py` packs anything, before the run branch is created and
before any container starts. The checks run in this order, and the first failure wins:

1. `bheembhai-verify lint skills/<run.skill> --require-all` — exit 0 passes.
2. `bheembhai-verify selftest skills/<run.skill> --require-all` — exit 0 passes.
3. The verifier range: `catalog.yaml`'s `requires_verify` must be a valid PEP 440 version
   specifier and must accept the selected verifier version, read from `skill-builder/kit.json`'s
   `bheembhai-verify` value.

A failed preflight creates one `packaging_refusals` row and leaves the run to epic BSB-25's
preparation-failure handling (its `runs.state` value is BSB-25's and is not named here). It creates
no `skill_bundles` row, no object at
`s3://skill-builder-runs/bundles/<skills_commit_sha>/<skill>.tar.gz`, no branch in the catalog
repository and no container.

`packaging_refusals` columns: `id`, `run_id`, `skill`, `skills_commit_sha`, `check` (`lint` \|
`selftest` \| `verifier_range`), `code`, `message`, `created_at`. One row per refused run.

| `check` | `code` | `message` exactly |
|---|---|---|
| `lint` | `verifier_lint_failed` | `Verifier lint failed: ` followed by the verifier's stderr verbatim |
| `selftest` | `verifier_selftest_failed` | `Verifier self-test failed: ` followed by the verifier's stderr verbatim |
| `verifier_range` | `verifier_version_out_of_range` | `Verifier version <version> is outside the catalog's required range <range>` |
| `verifier_range` | `verifier_range_invalid` | `Catalog requires_verify value '<value>' is not a valid version range` |

**Re-verification (FR-074, FR-075).**
`POST https://builder.skillbuilder.internal/api/projects/{project_id}/runs/{run_id}/reverify` with
`Content-Type: application/json` and body `{}` or
`{"skills_commit_sha":"<40 lowercase hex>"}`. The target run must be a `kind` = `run` row with a
recorded verification. With no `skills_commit_sha`, the builder resolves the target run's
`skills_ref` to its current head; with the field, it uses that commit. It packs or reuses that
commit's bundle, requires the bundle's `verify.yaml` SHA-256 to differ from the target run's
`verification.manifest_sha256`, and runs the shared verification layer at the target run's
`verify_version` against the target run's `run_branch` head and `baseline_sha`.

It creates one new `runs` row with `kind` = `reverify`, `parent_run_id` = the target run's `id`,
the target run's `run_branch`, `input_branch`, `skills_ref`, `context` and `claimed_verdict`, the
new `skills_commit_sha`, the target's `baseline_sha` and `verify_version`, `state` = `queued`,
`model_profile_id` and `tier` `NULL`, `agent_image_digest` and `stepkit_version` `NULL`,
`cost_usd` `0`, and `final_verdict` and `verification` `NULL`. The re-verify path is the only
writer of this row: it runs the shared layer, then in one update writes `state` = `completed`,
`final_verdict`, `verification` and `verification.comparison`. A shared-layer failure takes the
same path: that one update writes `state` = `completed`, `verification.status` = `failed` and the
non-passing `final_verdict` epic BSB-29's verification-failure rule assigns, so the row never stays
`queued` after the attempt. A `kind` = `reverify` row is never `completed` with `final_verdict`
still `NULL`, so epic BSB-29's claim predicate, which claims only terminal runs with
`final_verdict` `NULL`, never claims it (Cross-epic notes). The target run is never changed, and
neither is `build_readiness` nor `builds.ready_sha`.

The response is HTTP 201 `application/json` with exactly:

```
{"id":9,"project_id":7,"user_id":42,"skill":"sdlc-fix-bug-triage","skills_ref":"build/sdlc-fix-bug-triage","skills_commit_sha":"5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e","input_branch":"main","run_branch":"skilltest/1","state":"queued","kind":"reverify","parent_run_id":1,"created_at":"2026-11-15T10:10:00Z"}
```

No agent container is started (no container labelled `bb.run_id` = the new row's id) and no model
endpoint is called; the new row's `cost_usd` is `0` and the G5 target of zero model tokens holds.

Refusals use the shared error body `{"error":{"code":"code_value","message":"message text"}}`:

| Condition | Status | `code` | `message` exactly |
|---|---|---|---|
| caller is not a member of the project | 403 | `project_membership_required` | `You are not a member of this project.` |
| run not found in the project | 404 | `run_not_found` | `Run <id> does not exist.` |
| target run is a `kind` = `reverify` row | 409 | `not_a_run` | `Run <id> is not a run` |
| target run has no `final_verdict` or no `verification` | 409 | `run_not_verified` | `The run has no recorded verification to re-verify against` |
| selected verifier version differs from the target's `verify_version` | 409 | `verify_version_changed` | `The selected verifier version <selected> differs from the run's verified version <recorded>` |
| the new manifest's SHA-256 equals the target's `verification.manifest_sha256` | 409 | `manifest_unchanged` | `The verify.yaml at <sha> is unchanged from the verified manifest` |

**Flipped-check comparison (FR-075).** After the re-verification verifies, the builder compares the
target run's `verification.checks` with the re-verification run's `verification.checks`, keyed by
each check's `id`. For every id in either list whose `status` differs, it records one entry
`{"check":"<id>","from":"<target status>","to":"<re-verify status>"}`; a side with no check of that
id is `"absent"`. Entries are sorted by `check` ascending in Unicode code-point order. The
comparison is stored at `runs.verification->'comparison'` on the re-verification row as
`{"base_run_id":1,"flipped":[...]}`.

`GET https://builder.skillbuilder.internal/api/projects/{project_id}/runs/{run_id}/comparison`
returns HTTP 200 `application/json` with exactly
`{"run_id":9,"base_run_id":1,"flipped":[...]}`. A non-reverify run returns 409 `not_a_reverify`
with message `Run <id> is not a re-verification`; a re-verification whose `verification` is still
`NULL` returns 409 `verification_pending` with message
`The re-verification has not been verified yet`; a non-member gets 403 and an unknown run 404 as
above. The re-verification run page contains `<section id="reverify-flips">` and one line per
flipped check with the exact text `<check>: <from> → <to>`; with no flips it contains the exact
text `No checks flipped`.

**Fixture constants.**

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z` |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing` |
| User Mallory | `users.id` = `45`, `cognito_sub` = `d4e5f6a7-0000-0000-0000-000000000004`, `email` = `mallory@example.com`, `name` = `Mallory Trell`; her token's `cognito:groups` is `["catalog-reviewers"]` |
| `users` fixture | exactly four rows, the users above |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42` and `created_at` = `2026-11-14T09:00:00Z`; ids `1` to `6`, `8`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)`; Alan has no row for project `7` |
| Catalog repository | `saraavrnd/bheembhai-skills`, default branch `main` |
| Build fixture | exactly 16 `builds` rows, ids `1` to `16`; build `7` is `kind` = `edit`, `skill` = `sdlc-fix-bug-triage`, `cloned_from` = `NULL`, `branch` = `build/sdlc-fix-bug-triage`, `created_by` = `42`, `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `NULL`, `pr_url` = `NULL` and `state` = `open`; ids `1` to `6` and `8` to `16` are unrelated fixture builds |
| Build branch | `build/sdlc-fix-bug-triage` in the catalog repository; its history contains the SHAs below |
| Head SHA (`H`) | `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`; the tree has a valid `skills/sdlc-fix-bug-triage/verify.yaml` with SHA-256 `c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0` |
| Changed-manifest SHA (`H2`) | `5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e`; the tree differs from `H` only in `skills/sdlc-fix-bug-triage/verify.yaml`, whose SHA-256 is `e1d2c3b4a5f60718293a4b5c6d7e8f901a2b3c4d5e6f708192a3b4c5d6e7f809` |
| No-evidence SHA (`H5`) | `3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d`; a valid tree identical to `H`'s, with no `runs` row and no `skill_bundles` row |
| Lint-failure SHA (`H6`) | `7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e`; the tree's `skills/sdlc-fix-bug-triage/verify.yaml` makes the pinned verifier's `lint` exit `1` |
| Check.py-failure SHA (`H7`) | `8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f`; `lint` exits `0`, and the tree's `skills/sdlc-fix-bug-triage/SKILL.md` frontmatter has `name: sdlc-fix-bug-other`, so `python tools/check.py` exits `1` |
| Unreadable-tree SHA (`H8`) | `9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a`; the tree has no `skills/sdlc-fix-bug-triage/` folder |
| Non-passing-run SHA (`H9`) | `0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b`; a valid tree identical to `H`'s; its only run is run `6` |
| Reverify-only SHA (`H4`) | `2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c`; a valid tree identical to `H`'s; its only run is the `reverify` row run `4` |
| `catalog.yaml` at `H`, `H2`, `H5`, `H6`, `H7`, `H9` and `H4` | contains `requires_verify: ">=2.1,<3"` |
| `skill-builder/kit.txt` | contains exactly `kit-v8` |
| `skill-builder/kit.json` | `{"kit":"kit-v8","env_contract_version":"4","bheembhai-stepkit":"0.5.0","bheembhai-verify":"2.2.0","agent_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-agent@sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13"}` |
| Verifier stub | the pinned `bheembhai-verify` distribution is a fixture stub whose `lint` and `selftest` exit codes and stderr are set by the scenario; a passing invocation exits `0` with empty stderr and it counts its invocations |
| `skill_bundles` rows | `(H, sdlc-fix-bug-triage)` with `bundle_sha256` = `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` and `s3_key` = `bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz`; `(H2, sdlc-fix-bug-triage)` with `bundle_sha256` = `c8f4d2b0a6e3f9c5b7d1a2e4f6c8b0d2e4f6a8c0b2d4e6f8a0c2e4b6d8f2a4c6` and `s3_key` = `bundles/5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e/sdlc-fix-bug-triage.tar.gz`; `(H9, sdlc-fix-bug-triage)` with `bundle_sha256` = `d0e4c2a8b6f3c1e9a7d5b2f0c4e6a8d0b2f4c6e8a0d2b4f6c8e0a2b4d6f8c0e2` and `s3_key` = `bundles/0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b/sdlc-fix-bug-triage.tar.gz` |
| Scan outcome default (`H`, `H2`, `H9`) | static `passed`, LLM `complete` for the bundle content SHA; a scenario overrides one outcome where it says so |
| `runs` fixture | exactly seven rows, the rows below |
| Next `runs.id` | `9` (the re-verification row created by BSB-30-PENDING-7) |
| Current time | `2026-11-15T10:10:00Z` |
| Source-control stub | records every request; creating branch `skilltest/<id>` is a `POST /repos/saraavrnd/bheembhai-skills/git/refs` with body `{"ref":"refs/heads/skilltest/<id>","sha":"<input head>"}` |
| Container stub | records every container start and its labels, including `bb.run_id` |
| Model stub | the `ai_model` integration's base URL `https://api.anthropic.test` records every request |
| S3 stub | records every object put; bundle keys are `bundles/<skills_commit_sha>/<skill>.tar.gz` |

**Run fixtures.** Every row also has `project_id` = `7`, `user_id` = `42`, `skill` =
`sdlc-fix-bug-triage`, `input_branch` = `main`, `context` = `{}`, `model_profile_id` = `3`,
`tier` = `high`, `agent_image_digest` = NULL, `stepkit_version` = NULL and `verify_version` =
`2.2.0` unless the row says otherwise; `created_at` follows the id and the current time is
`2026-11-15T10:10:00Z`. The target run branch `skilltest/1` has head SHA
`6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e`; the fixture baseline SHA is
`9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09`. In the packaging scenarios
(BSB-30-PENDING-5 and BSB-30-PENDING-6) `builds.head_sha` and the catalog branch
`build/sdlc-fix-bug-triage` are at `H5`, so epic BSB-25 resolves run `8`'s `skills_ref` to `H5`;
every other scenario uses the fixture table as written.

| Run | `kind` | `skills_ref` | `skills_commit_sha` | `run_branch` | `baseline_sha` | `state` | `claimed_verdict` | `final_verdict` | `verification` | Purpose |
|-----|--------|--------------|--------------------|--------------|----------------|---------|-------------------|-----------------|----------------|---------|
| `1` | `run` | `build/sdlc-fix-bug-triage` | `H` | `skilltest/1` | `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09` | `completed` | `completed` | `completed` | `{"status":"passed","final":"completed","overridden":false,"reason":"ok","manifest_sha256":"c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0","checks":[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"failed","message":"required change missing"}],"inputs":{"run_branch_sha":"6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e","baseline_sha":"9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09","bundle_sha256":"b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a","verify_version":"2.2.0","self_verdict":"completed"}}` | the passing run at the head; the re-verification target |
| `2` | `run` | `build/sdlc-fix-bug-triage` | `H2` | `skilltest/2` | `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09` | `completed` | `changes_requested` | `changes_requested` | `{"status":"failed","final":"changes_requested","overridden":false,"reason":"checks_failed","manifest_sha256":"e1d2c3b4a5f60718293a4b5c6d7e8f901a2b3c4d5e6f708192a3b4c5d6e7f809","checks":[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"failed","message":"required change missing"}]}` | a verified non-passing run at the changed-manifest SHA |
| `3` | `run` | `build/sdlc-fix-bug-triage` | `H` | `skilltest/3` | `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09` | `completed` | `NULL` | `NULL` | `NULL` | a terminal run with no verification |
| `4` | `reverify` | `build/sdlc-fix-bug-triage` | `H4` | `skilltest/1` | `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09` | `completed` | `completed` | `completed` | `{"status":"passed","final":"completed","overridden":false,"reason":"ok","checks":[]}` | a passing re-verification row with no `kind` = `run` sibling |
| `5` | `run` | `build/sdlc-fix-bug-triage` | `H2` | `skilltest/5` | `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09` | `completed` | `completed` | `completed` | `{"status":"passed","final":"completed","overridden":false,"reason":"ok","manifest_sha256":"e1d2c3b4a5f60718293a4b5c6d7e8f901a2b3c4d5e6f708192a3b4c5d6e7f809","checks":[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"passed","message":"required change present"}]}` | a passing run at `H2` |
| `6` | `run` | `build/sdlc-fix-bug-triage` | `H9` | `skilltest/6` | `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09` | `completed` | `changes_requested` | `changes_requested` | `{"status":"failed","final":"changes_requested","overridden":false,"reason":"checks_failed","checks":[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"failed","message":"required change missing"}]}` | the only run at `H9`, and it does not pass |
| `8` | `run` | `build/sdlc-fix-bug-triage` | `NULL` (resolved by BSB-25) | `NULL` | `NULL` | `queued` | `NULL` | `NULL` | `NULL` | the packaging fixture run; BSB-25 resolves it to the SHA the scenario names |

## Decisions recorded in this decomposition (confirm at review)

1. **Readiness storage.** The epic says to "define the readiness aggregate keyed by build and SHA"
   but the ADR's §9 data model has no readiness table. This decomposition adds `build_readiness`
   (and `packaging_refusals`, below) as additive tables. A JSONB column on `builds` would need one
   row per SHA and cannot hold `not_run` independently; if review prefers a different store, the
   states, Ready rule and API do not change.
2. **Scan-outcome interface.** Epics BSB-31 and BSB-32 own the static and LLM scan records; neither
   has stories yet, and ADR §9 has no scan table. This epic consumes their outcome through
   `readiness_scan_outcome(content_sha, kind)` keyed by the bundle content SHA. Their
   decompositions must record an outcome for that content SHA and must record an LLM scan that
   cannot run as `unavailable`. If they name the storage differently, only this adapter changes.
3. **`ready_sha` writers.** Epic BSB-21 clears `ready_sha` when a save moves the head; this epic
   sets or clears it when it evaluates the head. Both only write `ready_sha`; no other writer is
   introduced.
4. **Manifest-check commands.** The ADR names `bheembhai-verify` and `tools/check.py` but not their
   flags. This decomposition pins `bheembhai-verify lint skills/<skill> --require-all` and
   `bheembhai-verify selftest skills/<skill> --require-all`. The verifier is an external pinned
   distribution; if its CLI differs, only the adapter changes.
5. **Packaging preflight order and wording.** The epic names the three refusals but not their order
   or messages. This decomposition pins lint, then self-test, then the catalog range, with the
   first failure winning, and the messages in the contract table. A run refused for lint is not
   also refused for an out-of-range verifier.
6. **Refusal record.** `packaging_refusals` is this epic's record of why a preparation stopped. The
   run's terminal preparation-failure `state` remains epic BSB-25's and is not named here (it is
   still open in epic BSB-26's review). Epic BSB-33 may render the message; this epic does not add
   a page region for it.
7. **Re-verification row.** A re-verification has no runtime, so its row is created `queued`, then
   set `completed` with `final_verdict` and `verification` in one update. It copies the target
   run's `claimed_verdict` so the verifier is asked the same question, and it records no model
   profile, tier, agent image or stepkit version and a cost of `0`. This keeps epic BSB-29's claim
   predicate from claiming it and keeps the G5 zero-token target testable. The `kind` value
   `reverify` is the ADR's §5/§9 value.
8. **Comparison identity.** FR-075 does not define "flipped". This decomposition compares the
   verifier's per-check `id` and `status`, lists a check present on only one side as `absent`, and
   sorts by check id ascending. Timing and message changes are not flips.
9. **LLM readiness state.** FR-069 says "complete or recorded as unavailable"; this decomposition
   treats only those two values as permitting Ready. Epic BSB-32 records a scan that cannot run as
   `unavailable` (FR-139); a `failed` readiness value does not exist.
10. **Build-page surface.** This epic adds only the four-check panel (`readiness-checks`). Epic
    BSB-21's overall readiness status and head-SHA display (FR-020, FR-021) are consumed unchanged.

## Cross-epic notes

- **BSB-21 (build head and ready SHA).** Epic BSB-21 owns `builds.head_sha`, `builds.ready_sha` and
  the rule that a save clears `ready_sha`. It has no stories yet. Its decomposition must keep the
  head and ready SHA as independent values, must clear `ready_sha` in the same transaction as a
  successful save, and should have its FR-021 readiness display read `builds.ready_sha`, which this
  epic writes under the Ready-SHA rule.
- **BSB-25 (packaging).** This epic's preflight runs after BSB-25 resolves the skills branch and
  before BSB-25 packs the bundle, creates the run branch or starts a container. BSB-25's
  decomposition must call the preflight at that point, record the resolved `skills_commit_sha` on
  the refusal, and own the preparation-failure state the run is left in. A passing preflight
  changes nothing in BSB-25's packaging path.
- **BSB-26 and BSB-29 (run states and verification).** This epic reads BSB-29's pass predicate and
  never changes a run's state for readiness. A `kind` = `reverify` row is created `queued` and is
  written `completed`, `final_verdict` and `verification` in one update by the re-verify path; it is
  therefore never a terminal run with `final_verdict` `NULL`, so BSB-29's claim predicate does not
  claim it. BSB-29's stories already state that a re-verify is a separate `reverify` run and out of
  its scope; no change to its scenarios is required, but its decomposition should not add a
  `kind`-agnostic claim that would pick up a `reverify` row in the `queued` window.
- **BSB-31 (static scan).** This epic consumes the static outcome for the bundle content SHA and
  treats any non-passing result (its `DO_NOT_INSTALL`, critical-finding, incomplete-coverage and
  accepted-finding cases) as `failed`. BSB-31's decomposition must make that outcome readable for a
  content SHA and must not reuse a result across different content hashes.
- **BSB-32 (LLM scan).** This epic consumes `complete` or `unavailable` for the bundle content SHA.
  BSB-32's decomposition must record a scan that cannot run (no profile, model unavailable) as
  `unavailable`, not absent, so readiness can proceed; `not_run` is reserved for a scan never
  requested.
- **BSB-33 (run report).** Epic BSB-33 owns the run page and the run report. This epic adds only the
  `<section id="reverify-flips">` region to a re-verification run page and records the comparison
  on the run row; BSB-33's other run-page regions and its verdict display are unchanged.
- **BSB-36 (catalog submission).** Submit is enabled from `builds.ready_sha` (FR-107). The Ready
  rule and the Ready-SHA write rule above make that value mean "all four checks held at that SHA".
  BSB-36 need not recompute readiness.
- **BSB-38 (accessibility).** The new four-check panel and the flipped-check region are builder web
  surfaces; their WCAG 2.1 AA and 320-pixel reflow checks belong to epic BSB-38 and add no
  requirement here.

---

## STORY: BSB-30-PENDING-1

**Summary:** Check a build's manifest validity at a commit SHA
**Epic:** BSB-30 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **the builder to check my build's manifest at a specific commit SHA**, so that **I know whether that exact commit's `verify.yaml` and catalog structure are valid before I rely on it for readiness**.

### Acceptance Criteria

#### Scenario: A valid manifest at a commit SHA is recorded as passed
Given build `7` exists with branch `build/sdlc-fix-bug-triage` and the fixture tree at `H5` has a valid `skills/sdlc-fix-bug-triage/verify.yaml`
And the pinned verifier's `lint skills/sdlc-fix-bug-triage --require-all` exits `0` with empty stderr
And `python tools/check.py` at `H5` exits `0` with empty stderr
When Ada sends `GET https://builder.skillbuilder.internal/api/builds/7/readiness?sha=3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d` carrying the `sb_session` cookie
Then the response is HTTP 200 with body exactly `{"build_id":7,"sha":"3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d","manifest":"passed","run":"not_run","static":"not_run","llm":"not_run","ready":false,"ready_sha":null}`
And `SELECT manifest_state, detail->'manifest'->>'lint_exit', detail->'manifest'->>'check_py_exit' FROM build_readiness WHERE build_id = 7 AND sha = '3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d'` returns exactly `passed | 0 | 0`

#### Scenario: A verify.yaml that fails lint is recorded as a manifest failure
Given the fixture tree at `H6` has `skills/sdlc-fix-bug-triage/verify.yaml` that makes the pinned verifier's `lint` exit `1` and write exactly `skills/sdlc-fix-bug-triage/verify.yaml: claims.0.id: required property missing` to stderr
When Ada sends `GET https://builder.skillbuilder.internal/api/builds/7/readiness?sha=7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e` carrying the `sb_session` cookie
Then the response body has `manifest` exactly `failed`, `ready` exactly `false` and `ready_sha` exactly `null`
And `SELECT manifest_state, detail->'manifest'->>'lint_exit', detail->'manifest'->>'lint_stderr' FROM build_readiness WHERE build_id = 7 AND sha = '7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e'` returns exactly `failed | 1 | skills/sdlc-fix-bug-triage/verify.yaml: claims.0.id: required property missing`
And `SELECT detail->'manifest'->>'check_py_exit' IS NULL FROM build_readiness WHERE build_id = 7 AND sha = '7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e'` returns exactly `true`
And `python tools/check.py` is not run for that SHA

#### Scenario: A tools/check.py failure is recorded as a manifest failure
Given the fixture tree at `H7` passes the verifier's `lint`
And `python tools/check.py` at `H7` exits `1` and writes exactly `skills/sdlc-fix-bug-triage: SKILL.md name 'sdlc-fix-bug-other' does not match folder` to stderr
When Ada sends `GET https://builder.skillbuilder.internal/api/builds/7/readiness?sha=8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f` carrying the `sb_session` cookie
Then `SELECT manifest_state, detail->'manifest'->>'lint_exit', detail->'manifest'->>'check_py_exit', detail->'manifest'->>'check_py_stderr' FROM build_readiness WHERE build_id = 7 AND sha = '8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f'` returns exactly `failed | 0 | 1 | skills/sdlc-fix-bug-triage: SKILL.md name 'sdlc-fix-bug-other' does not match folder`
And the response body has `manifest` exactly `failed` and `ready` exactly `false`

#### Scenario: A commit without the skill folder is a manifest failure, not a pass
Given the fixture tree at `H8` has no `skills/sdlc-fix-bug-triage/` folder
When Ada sends `GET https://builder.skillbuilder.internal/api/builds/7/readiness?sha=9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a` carrying the `sb_session` cookie
Then `SELECT manifest_state, detail->'manifest'->>'reason', detail->'manifest'->>'lint_exit', detail->'manifest'->>'check_py_exit' FROM build_readiness WHERE build_id = 7 AND sha = '9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a'` returns exactly `failed | manifest_unreadable | NULL | NULL`
And the response body has `manifest` exactly `failed` and `ready` exactly `false`

#### Scenario: A manifest result is cached per build and SHA
Given the fixture verifier records each `lint` invocation
And the trees at `H` and `H2` both pass the verifier's `lint` and `python tools/check.py`
When Ada requests `GET /api/builds/7/readiness?sha=4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` twice and then `GET /api/builds/7/readiness?sha=5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e` once, each carrying the `sb_session` cookie
Then the fixture verifier records exactly `2` `lint` invocations
And `SELECT count(*) FROM build_readiness WHERE build_id = 7` returns exactly `2`
And both rows have `manifest_state` exactly `passed`

### Covered requirements (traceability)
- FR-068

### Out of scope
Deciding whether a structurally valid manifest's checks are the right checks (the external verifier's builtin checks). Running the verifier's checks against an already-built bundle (epic BSB-25). Changing `verify.yaml` (epic BSB-21's save path). Deciding Ready from the other three checks (BSB-30-PENDING-2). Rendering the checks on the build page (BSB-30-PENDING-4).

### Notes / dependencies
- Depends on epic BSB-21 for the build row, branch and head SHA, on epic BSB-20 for the build page
  and branch, on epic BSB-25 for the bundle content SHA the readiness run/static/llm inputs use,
  and on the external pinned `bheembhai-verify` distribution and the repository's `tools/check.py`.
- Tier 1 is the same two commands the catalog's own save gate runs. The check is read-only: it
  checks out the build branch at the SHA and writes no commit.
- The manifest result is cached because it is a pure function of the tree at that SHA; a fix to a
  manifest is a new save, which is a new SHA (epic BSB-21, FR-018/FR-019). The readiness API still
  re-derives the run, static and LLM states on every request because their evidence arrives after
  the first evaluation.
- The verifier distribution is pinned by `skill-builder/kit.json`; the manifest check does not
  consult `kit.txt` directly.

---

## STORY: BSB-30-PENDING-2

**Summary:** Mark a build Ready only when all four checks permit it
**Epic:** BSB-30 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **the builder to mark my build Ready at a SHA only when its manifest is valid, a run passes, the static scan passes and the LLM scan is complete or unavailable**, so that **Ready means the whole set of checks held, not just the one check I happened to look at**.

### Acceptance Criteria

#### Scenario: A build is Ready when all four checks permit it
Given the fixture checks at `H` are manifest `passed`, run `1` satisfying the pass predicate, static `passed` and LLM `complete`
When Ada sends `GET https://builder.skillbuilder.internal/api/builds/7/readiness` carrying the `sb_session` cookie
Then the response is HTTP 200 with body exactly `{"build_id":7,"sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b","manifest":"passed","run":"passed","static":"passed","llm":"complete","ready":true,"ready_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b"}`
And `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` returns exactly `passed | passed | passed | complete | true`
And `SELECT ready_sha FROM builds WHERE id = 7` returns exactly `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`

#### Scenario: A failed manifest check blocks Ready
Given the fixture tree at `H6` fails the manifest check
When readiness is evaluated for build `7` at `7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e`
Then `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e'` returns exactly `failed | not_run | not_run | not_run | false`
And the response body has `ready` exactly `false` and `ready_sha` exactly `null`

#### Scenario: A verified non-passing run does not make the build Ready
Given the fixture checks at `H9` are manifest `passed`, static `passed` and LLM `complete`
And run `6` at `H9` has `final_verdict` = `changes_requested` and `verification->>'status'` = `failed`
When readiness is evaluated for build `7` at `0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b`
Then `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b'` returns exactly `passed | failed | passed | complete | false`
And the response body has `run` exactly `failed` and `ready` exactly `false`

#### Scenario: A check that has not run is never a pass
Given the fixture has no `runs` row, no bundle and no scan outcome for `H5`
And the manifest check at `H5` passes
When readiness is evaluated for build `7` at `3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d`
Then `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d'` returns exactly `passed | not_run | not_run | not_run | false`
And the response body has `run` exactly `not_run`, `static` exactly `not_run`, `llm` exactly `not_run` and `ready` exactly `false`

#### Scenario: A failed static scan blocks Ready
Given the fixture checks at `H` are manifest `passed`, run `passed` and LLM `complete`
And the static scan outcome for the bundle content SHA `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` is `failed`
When readiness is evaluated for build `7` at the head
Then `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` returns exactly `passed | passed | failed | complete | false`
And the response body has `static` exactly `failed` and `ready` exactly `false`

#### Scenario: A missing LLM scan blocks Ready
Given the fixture checks at `H` are manifest `passed`, run `passed` and static `passed`
And no LLM scan outcome is recorded for the bundle content SHA `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
When readiness is evaluated for build `7` at the head
Then `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` returns exactly `passed | passed | passed | not_run | false`
And the response body has `llm` exactly `not_run` and `ready` exactly `false`

#### Scenario: An unavailable LLM scan still permits Ready
Given the fixture checks at `H` are manifest `passed`, run `passed` and static `passed`
And the LLM scan outcome for the bundle content SHA `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` is `unavailable`
When Ada sends `GET https://builder.skillbuilder.internal/api/builds/7/readiness` carrying the `sb_session` cookie
Then `SELECT llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` returns exactly `unavailable | true`
And the response body has `llm` exactly `unavailable`, `ready` exactly `true` and `ready_sha` exactly `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`

### Covered requirements (traceability)
- FR-069

### Out of scope
Defining or changing the verifier's builtin checks, the static scanner's verdict rules (epic BSB-31) or the LLM scan's findings (epic BSB-32). Producing the run, its verification, the bundle or the scans. Deciding what a scan's score or findings mean. Marking a build Ready at a SHA that is not its head (BSB-30-PENDING-3). Rendering the panel (BSB-30-PENDING-4). Submission to the catalog (epic BSB-36).

### Notes / dependencies
- Depends on BSB-30-PENDING-1 for the manifest state, on epic BSB-29 for the pass predicate, on
  epics BSB-31 and BSB-32 for the scan outcomes, and on epic BSB-25 for the bundle content SHA.
- The run check is about the build's skill and the exact `skills_commit_sha`; a run of another
  skill or another commit is never evidence for this SHA.
- A verified `BLOCK` or `changes_requested` run is a legitimate outcome but not a pass; only
  `final_verdict` = `completed` with `verification.status` = `passed` counts.
- Any evaluation writes the explicit states even when nothing has run; a later arrival of a run or
  scan is picked up by the next evaluation of the same SHA.

---

## STORY: BSB-30-PENDING-3

**Summary:** Keep Ready bound to the build's current head SHA
**Epic:** BSB-30 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **readiness to apply only to my build's current head SHA**, so that **an older passing commit or a passing re-verification can never make the current head look Ready**.

### Acceptance Criteria

#### Scenario: A new head with a non-passing run is not Ready and clears the recorded ready SHA
Given build `7` was Ready at `H`, so `builds.ready_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And a save by epic BSB-21 moves `builds.head_sha` to `H2` and clears `builds.ready_sha` to `NULL`
And `H2`'s manifest check passes, its static outcome and LLM outcome permit Ready, and run `2` at `H2` is verified as `changes_requested`
And run `5` does not exist in this scenario
When Ada sends `GET https://builder.skillbuilder.internal/api/builds/7/readiness` carrying the `sb_session` cookie
Then the response body has `sha` exactly `5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e`, `ready` exactly `false` and `ready_sha` exactly `null`
And `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e'` returns exactly `passed | failed | passed | complete | false`
And `SELECT ready_sha FROM builds WHERE id = 7` returns exactly `NULL`
And `SELECT ready FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` returns exactly `true`

#### Scenario: The head becomes Ready when its last missing check passes
Given the state of the previous scenario, with `builds.head_sha` = `H2` and `builds.ready_sha` = `NULL`
And run `5`'s passing verification at `H2` is recorded
When readiness is evaluated for build `7` at `H2`
Then `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e'` returns exactly `passed | passed | passed | complete | true`
And `SELECT ready_sha FROM builds WHERE id = 7` returns exactly `5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e`
And `SELECT ready FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` still returns exactly `true`

#### Scenario: Evaluating an older Ready SHA does not set the ready SHA for the head
Given `builds.head_sha` = `H2` and `builds.ready_sha` = `NULL`
And every check at `H` permits Ready
When Ada sends `GET https://builder.skillbuilder.internal/api/builds/7/readiness?sha=4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` carrying the `sb_session` cookie
Then the response body has `sha` exactly `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready` exactly `true` and `ready_sha` exactly `null`
And `SELECT ready_sha FROM builds WHERE id = 7` returns exactly `NULL`
And `SELECT ready FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` returns exactly `true`

#### Scenario: A passing re-verification is not a passing run
Given `H4` has run `4` with `kind` = `reverify`, `final_verdict` = `completed` and `verification->>'status'` = `passed`
And `H4` has no `kind` = `run` row and no bundle
And the manifest check at `H4` passes
When readiness is evaluated for build `7` at `2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c`
Then `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c'` returns exactly `passed | not_run | not_run | not_run | false`
And the response body has `run` exactly `not_run`, `ready` exactly `false` and `ready_sha` exactly `null`

### Covered requirements (traceability)
- FR-069

### Out of scope
Committing, saving or moving the head (epic BSB-21). Producing the runs or their verification (epics BSB-26 and BSB-29). Performing a re-verification (BSB-30-PENDING-7). Displaying readiness (BSB-30-PENDING-4).

### Notes / dependencies
- Depends on BSB-30-PENDING-2 for the aggregate rule and on epic BSB-21 for the head and
  `ready_sha` lifecycle. This story only adds the binding: readiness is a property of a
  `(build, SHA)` pair, and only the head pair may set `builds.ready_sha`.
- `build_readiness` keeps the row for an older SHA (`ready` = `true` there); that row is history,
  not a claim about the current head.
- A re-verification is a `kind` = `reverify` row and never satisfies the run check
  (BSB-30-PENDING-7). The run check considers only `kind` = `run` rows.
- The head can become Ready without a new save only when the missing evidence arrives for the same
  head SHA (for example a run completes or a scan finishes); no evidence is ever borrowed from
  another SHA.

---

## STORY: BSB-30-PENDING-4

**Summary:** Show all four readiness checks on the build page
**Epic:** BSB-30 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **the build page to show each of the four readiness checks with its state**, so that **I can see exactly which check is blocking Ready instead of guessing**.

### Acceptance Criteria

#### Scenario: All four checks are shown for a Ready head
Given build `7`'s head `H` has manifest `passed`, run `passed`, static `passed` and LLM `complete`
When Ada sends `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the body contains exactly `<section id="readiness-checks">`
And the body contains exactly `Manifest: Passed`, `Run: Passed`, `Static scan: Passed` and `LLM scan: Complete`
And the body contains exactly the ids `readiness-manifest`, `readiness-run`, `readiness-static` and `readiness-llm`

#### Scenario: Checks that have not run are shown as Not run
Given build `7`'s head is at a SHA whose manifest passes and which has no run, no bundle and no scan outcome
When the author opens the build page
Then the body contains exactly `Manifest: Passed`, `Run: Not run`, `Static scan: Not run` and `LLM scan: Not run`
And all four readiness element ids are present

#### Scenario: A failed check is shown as Failed
Given build `7`'s head `H` has manifest `passed`, run `passed`, static `failed` and LLM `complete`
When the author opens the build page
Then the body contains exactly `Manifest: Passed`, `Run: Passed`, `Static scan: Failed` and `LLM scan: Complete`

#### Scenario: An unavailable LLM scan is shown as Unavailable
Given build `7`'s head `H` has manifest `passed`, run `passed`, static `passed` and LLM `unavailable`
When the author opens the build page
Then the body contains exactly `Manifest: Passed`, `Run: Passed`, `Static scan: Passed` and `LLM scan: Unavailable`

#### Scenario: A signed-in non-member sees no readiness data
Given Mallory is signed in with a valid token whose `cognito:groups` is `["catalog-reviewers"]`
When Mallory sends `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the response is HTTP 403
And the body does not contain `readiness-checks`
And no `build_readiness` row is created for build `7`

#### Scenario: An unknown build shows no readiness panel
Given build `999` does not exist
When Ada sends `GET https://builder.skillbuilder.internal/builds/999` carrying the `sb_session` cookie
Then the response is HTTP 404
And the body does not contain `readiness-checks`

### Covered requirements (traceability)
- FR-070

### Out of scope
The build page's overall readiness status, head SHA and other regions (epic BSB-21). Defining the
check states (BSB-30-PENDING-1 and BSB-30-PENDING-2). The scan reports and their findings (epics
BSB-31 and BSB-32). Accessibility conformance of the panel (epic BSB-38). The flipped-check region
of a re-verification (BSB-30-PENDING-8).

### Notes / dependencies
- Depends on BSB-30-PENDING-2 for the four states and on epic BSB-20 for the build page route and
  session handling.
- The panel renders the head SHA's states. It does not offer a SHA selector and does not render an
  older SHA's readiness; the API's `?sha=` form exists for tests and for the re-verify path.
- The four rows are always present, so the page shows a `not_run` row instead of omitting a check
  that has no evidence. This is the visible form of "absence never reads as a pass".
- Epic BSB-21's readiness status (FR-021) remains the page's overall badge; this story adds only
  the four-check panel.

---

## STORY: BSB-30-PENDING-5

**Summary:** Refuse packaging when the verifier lint or self-test fails
**Epic:** BSB-30 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **the builder to refuse to package a skill whose `verify.yaml` fails the verifier's lint or self-test**, so that **a broken manifest never reaches a run and I am told exactly what failed**.

### Acceptance Criteria

#### Scenario: A failing lint check refuses packaging and records why
Given packaging run `8` resolves `build/sdlc-fix-bug-triage` to `H5`
And the pinned verifier's `lint skills/sdlc-fix-bug-triage --require-all` exits `1` and writes exactly `skills/sdlc-fix-bug-triage/verify.yaml: claims.0.id: required property missing` to stderr
When the runner prepares run `8`
Then `SELECT run_id, skill, skills_commit_sha, check, code, message FROM packaging_refusals WHERE run_id = 8` returns exactly `8 | sdlc-fix-bug-triage | 3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d | lint | verifier_lint_failed | Verifier lint failed: skills/sdlc-fix-bug-triage/verify.yaml: claims.0.id: required property missing`
And `SELECT count(*) FROM skill_bundles WHERE skills_commit_sha = '3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d' AND skill = 'sdlc-fix-bug-triage'` returns exactly `0`
And the S3 stub has no object at `bundles/3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d/sdlc-fix-bug-triage.tar.gz`
And the source-control stub received no request to create `skilltest/8`
And the container stub recorded no container labelled `bb.run_id` = `8`
And the pinned verifier's `selftest` was not invoked

#### Scenario: A failing self-test refuses packaging after lint passes
Given packaging run `8` resolves `build/sdlc-fix-bug-triage` to `H5`
And the pinned verifier's `lint` exits `0` with empty stderr
And the pinned verifier's `selftest skills/sdlc-fix-bug-triage --require-all` exits `1` and writes exactly `selftest: builtin check 'gherkin_valid' did not run` to stderr
When the runner prepares run `8`
Then `SELECT check, code, message FROM packaging_refusals WHERE run_id = 8` returns exactly `selftest | verifier_selftest_failed | Verifier self-test failed: selftest: builtin check 'gherkin_valid' did not run`
And no bundle, branch or container is created for run `8`

#### Scenario: A lint failure takes precedence when both checks fail
Given packaging run `8` resolves to `H5`
And the pinned verifier's `lint` exits `1` with stderr exactly `skills/sdlc-fix-bug-triage/verify.yaml: claims.0.id: required property missing`
And the pinned verifier's `selftest` would exit `1` if invoked
When the runner prepares run `8`
Then `SELECT count(*) FROM packaging_refusals WHERE run_id = 8` returns exactly `1`
And `SELECT check, code FROM packaging_refusals WHERE run_id = 8` returns exactly `lint | verifier_lint_failed`
And the pinned verifier's `selftest` was not invoked
And the verifier-range check was not performed

#### Scenario: Packaging proceeds when lint and self-test pass
Given packaging run `8` resolves `build/sdlc-fix-bug-triage` to `H5`
And the pinned verifier's `lint` and `selftest` both exit `0` with empty stderr
And `catalog.yaml` at `H5` has `requires_verify` = `>=2.1,<3` and `kit.json` has `bheembhai-verify` = `2.2.0`
When the runner prepares run `8`
Then `SELECT count(*) FROM packaging_refusals WHERE run_id = 8` returns exactly `0`
And epic BSB-25's packaging proceeds: exactly one `skill_bundles` row exists for `H5` and `sdlc-fix-bug-triage`
And the source-control stub received the `POST /repos/saraavrnd/bheembhai-skills/git/refs` request creating `skilltest/8`

### Covered requirements (traceability)
- FR-071
- FR-072

### Out of scope
Changing the verifier's builtin checks or the `verify.yaml` format (the external pinned verifier).
Packing the bundle, creating the run branch or choosing the preparation-failure state (epic
BSB-25). The catalog verifier range check (BSB-30-PENDING-6). Displaying the refusal (epic
BSB-33). Retrying a refused preparation or re-running the run (epic BSB-27).

### Notes / dependencies
- Depends on epic BSB-25 for the preparation step, the resolved `skills_commit_sha`, the bundle
  and the run branch, and on the pinned `bheembhai-verify` distribution for `lint` and `selftest`.
- The preflight is the first step of preparation, so the run has no bundle and no branch when it
  fails. `packaging_refusals` records the resolved SHA even though the run's own preparation state
  is epic BSB-25's.
- The verifier is an external distribution; the fixture stub's exit codes and stderr make the
  failure deterministic. `lint` is run before `selftest`, so a lint failure does not invoke
  `selftest`.
- A refused run is not retried by this preflight; a new attempt is a new run or epic BSB-25's
  business.

---

## STORY: BSB-30-PENDING-6

**Summary:** Refuse packaging when the required verifier range excludes the selected version
**Epic:** BSB-30 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **the builder to refuse to package a skill when the catalog's required verifier range does not accept the pinned verifier version**, so that **I cannot produce a skill the catalog's own gate would reject**.

### Acceptance Criteria

#### Scenario: A verifier below the required range refuses packaging
Given packaging run `8` resolves `build/sdlc-fix-bug-triage` to `H5`
And the pinned verifier's `lint` and `selftest` both exit `0`
And `catalog.yaml` at `H5` has `requires_verify` = `>=2.1,<3`
And `kit.json` at `H5` has `bheembhai-verify` = `2.0.3`
When the runner prepares run `8`
Then `SELECT check, code, message FROM packaging_refusals WHERE run_id = 8` returns exactly `verifier_range | verifier_version_out_of_range | Verifier version 2.0.3 is outside the catalog's required range >=2.1,<3`
And no bundle, branch or container is created for run `8`

#### Scenario: A verifier above the required range refuses packaging
Given packaging run `8` resolves `build/sdlc-fix-bug-triage` to `H5`
And the pinned verifier's `lint` and `selftest` both exit `0`
And `catalog.yaml` at `H5` has `requires_verify` = `>=2.1,<3`
And `kit.json` at `H5` has `bheembhai-verify` = `3.0.0`
When the runner prepares run `8`
Then `SELECT check, code, message FROM packaging_refusals WHERE run_id = 8` returns exactly `verifier_range | verifier_version_out_of_range | Verifier version 3.0.0 is outside the catalog's required range >=2.1,<3`
And no bundle, branch or container is created for run `8`

#### Scenario: An invalid required range refuses packaging
Given packaging run `8` resolves `build/sdlc-fix-bug-triage` to `H5`
And the pinned verifier's `lint` and `selftest` both exit `0`
And `catalog.yaml` at `H5` has `requires_verify` = `two-one`
When the runner prepares run `8`
Then `SELECT check, code, message FROM packaging_refusals WHERE run_id = 8` returns exactly `verifier_range | verifier_range_invalid | Catalog requires_verify value 'two-one' is not a valid version range`
And no bundle, branch or container is created for run `8`

#### Scenario: A verifier inside the required range permits packaging
Given packaging run `8` resolves `build/sdlc-fix-bug-triage` to `H5`
And the pinned verifier's `lint` and `selftest` both exit `0`
And `catalog.yaml` at `H5` has `requires_verify` = `>=2.1,<3`
And `kit.json` at `H5` has `bheembhai-verify` = `2.2.0`
When the runner prepares run `8`
Then `SELECT count(*) FROM packaging_refusals WHERE run_id = 8` returns exactly `0`
And epic BSB-25's packaging proceeds: exactly one `skill_bundles` row exists for `H5` and `sdlc-fix-bug-triage`

#### Scenario: A lint failure is reported before an out-of-range verifier
Given packaging run `8` resolves `build/sdlc-fix-bug-triage` to `H5`
And the pinned verifier's `lint` exits `1` with stderr exactly `skills/sdlc-fix-bug-triage/verify.yaml: claims.0.id: required property missing`
And `catalog.yaml` at `H5` has `requires_verify` = `>=2.1,<3` and `kit.json` has `bheembhai-verify` = `2.0.3`
When the runner prepares run `8`
Then `SELECT count(*) FROM packaging_refusals WHERE run_id = 8` returns exactly `1`
And `SELECT check, code FROM packaging_refusals WHERE run_id = 8` returns exactly `lint | verifier_lint_failed`
And no `verifier_range` refusal is recorded

### Covered requirements (traceability)
- FR-073

### Out of scope
Choosing or updating the kit and its verifier version (the installation's `kit.txt` and `kit.json`).
Defining the catalog's required range (the catalog's own `catalog.yaml`). Changing, installing or
publishing the verifier (the external pinned distribution). Packing the bundle, creating the run
branch or choosing the preparation-failure state (epic BSB-25). The lint and self-test gates
(BSB-30-PENDING-5).

### Notes / dependencies
- Depends on BSB-30-PENDING-5 for the preflight point and order, on epic BSB-25 for preparation,
  and on the catalog's `catalog.yaml` and the installation's `kit.json` at the resolved SHA.
- The selected verifier version is the one `kit.json` reports for `bheembhai-verify`, the same
  value the shared layer is installed from. A range with no upper bound is valid; the fixture uses
  `>=2.1,<3` so both bounds are observable.
- The range is parsed as a PEP 440 specifier set. An unparsable or missing range is not treated as
  permission to package: it is a refusal, because compatibility cannot be established.
- A successful range check does not change the bundle; it only allows epic BSB-25 to proceed.

---

## STORY: BSB-30-PENDING-7

**Summary:** Re-verify an output branch with a changed verify.yaml without an agent or model
**Epic:** BSB-30 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **to re-grade an existing run's output branch with a changed `verify.yaml` without running the agent or a model**, so that **I can tune checks cheaply and see their effect on the same output**.

### Acceptance Criteria

#### Scenario: Re-verifying creates a re-verification run for the existing output branch
Given run `1` is a verified run at `H` with `claimed_verdict` = `completed` and `verification.manifest_sha256` = `c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0`
And the head of `build/sdlc-fix-bug-triage` is `H2`, whose `verify.yaml` SHA-256 is `e1d2c3b4a5f60718293a4b5c6d7e8f901a2b3c4d5e6f708192a3b4c5d6e7f809`
And the selected verifier version is `2.2.0`
And Ada is the owner of project `7`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/1/reverify` with `Content-Type: application/json` and body `{}` carrying the `sb_session` cookie
Then the response is HTTP 201 with body exactly `{"id":9,"project_id":7,"user_id":42,"skill":"sdlc-fix-bug-triage","skills_ref":"build/sdlc-fix-bug-triage","skills_commit_sha":"5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e","input_branch":"main","run_branch":"skilltest/1","state":"queued","kind":"reverify","parent_run_id":1,"created_at":"2026-11-15T10:10:00Z"}`
And `SELECT project_id, user_id, skill, skills_ref, skills_commit_sha, input_branch, run_branch, baseline_sha, verify_version, kind, parent_run_id, state, claimed_verdict, final_verdict, verification, model_profile_id, tier, agent_image_digest, stepkit_version, cost_usd FROM runs WHERE id = 9` returns exactly `7 | 42 | sdlc-fix-bug-triage | build/sdlc-fix-bug-triage | 5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e | main | skilltest/1 | 9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09 | 2.2.0 | reverify | 1 | queued | completed | NULL | NULL | NULL | NULL | NULL | NULL | 0`

#### Scenario: The re-verification grades the changed manifest with no agent and no model
Given the state after the previous scenario, with run `9` created
When the re-verification completes
Then within 2 seconds `SELECT state, final_verdict, verification->>'status', verification->>'manifest_sha256' FROM runs WHERE id = 9` returns exactly `completed | completed | passed | e1d2c3b4a5f60718293a4b5c6d7e8f901a2b3c4d5e6f708192a3b4c5d6e7f809`
And `SELECT verification->'inputs'->>'run_branch_sha', verification->'inputs'->>'baseline_sha', verification->'inputs'->>'bundle_sha256', verification->'inputs'->>'verify_version', verification->'inputs'->>'self_verdict' FROM runs WHERE id = 9` returns exactly `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e | 9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09 | c8f4d2b0a6e3f9c5b7d1a2e4f6c8b0d2e4f6a8c0b2d4e6f8a0c2e4b6d8f2a4c6 | 2.2.0 | completed`
And the container stub recorded no container labelled `bb.run_id` = `9`
And the model stub recorded `0` requests
And `SELECT cost_usd FROM runs WHERE id = 9` returns exactly `0`
And `SELECT state, final_verdict, verification->>'manifest_sha256' FROM runs WHERE id = 1` still returns exactly `completed | completed | c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0`
And `SELECT ready_sha FROM builds WHERE id = 7` is unchanged by the re-verification, and any `build_readiness` row for `H2` that existed before it is unchanged

#### Scenario: A non-member cannot re-verify a run
Given Alan is signed in but has no `project_members` row for project `7`
When Alan sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/1/reverify` with body `{}` carrying the `sb_session` cookie
Then the response is HTTP 403 with body exactly `{"error":{"code":"project_membership_required","message":"You are not a member of this project."}}`
And `SELECT count(*) FROM runs WHERE id = 9` returns exactly `0`

#### Scenario: An unknown run is not re-verified
Given run `999` does not exist
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/999/reverify` with body `{}` carrying the `sb_session` cookie
Then the response is HTTP 404 with body exactly `{"error":{"code":"run_not_found","message":"Run 999 does not exist."}}`

#### Scenario: A re-verification cannot itself be re-verified
Given run `4` is a `kind` = `reverify` row with `final_verdict` = `completed` and a recorded `verification`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/4/reverify` with body `{}` carrying the `sb_session` cookie
Then the response is HTTP 409 with body exactly `{"error":{"code":"not_a_run","message":"Run 4 is not a run"}}`
And `SELECT count(*) FROM runs WHERE id = 9` returns exactly `0`

#### Scenario: An unverified run cannot be re-verified
Given run `3` has `final_verdict` = `NULL` and `verification` = `NULL`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/3/reverify` with body `{}` carrying the `sb_session` cookie
Then the response is HTTP 409 with body exactly `{"error":{"code":"run_not_verified","message":"The run has no recorded verification to re-verify against"}}`
And `SELECT count(*) FROM runs WHERE id = 9` returns exactly `0`

#### Scenario: A different verifier version is refused
Given run `1` has `verify_version` = `2.2.0`
And `kit.json` has `bheembhai-verify` = `2.3.0`
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/1/reverify` with body `{}` carrying the `sb_session` cookie
Then the response is HTTP 409 with body exactly `{"error":{"code":"verify_version_changed","message":"The selected verifier version 2.3.0 differs from the run's verified version 2.2.0"}}`
And `SELECT count(*) FROM runs WHERE id = 9` returns exactly `0`

#### Scenario: An unchanged verify.yaml is refused
Given run `1`'s `verification.manifest_sha256` is `c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0`
And the `verify.yaml` at `H` has that same SHA-256
When Ada sends `POST https://builder.skillbuilder.internal/api/projects/7/runs/1/reverify` with `Content-Type: application/json` and body `{"skills_commit_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b"}` carrying the `sb_session` cookie
Then the response is HTTP 409 with body exactly `{"error":{"code":"manifest_unchanged","message":"The verify.yaml at 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b is unchanged from the verified manifest"}}`
And `SELECT count(*) FROM runs WHERE id = 9` returns exactly `0`

### Covered requirements (traceability)
- FR-074

### Out of scope
Re-running the agent or a model (epic BSB-27's re-run and the whole run-execution path). Changing
the target run, its verification or its output branch. Changing readiness for the build head
(BSB-30-PENDING-3). Deciding which checks should flip (the external verifier's checks).
Rendering the comparison (BSB-30-PENDING-8). Packing a bundle from scratch (epic BSB-25) or
changing the verifier version.

### Notes / dependencies
- Depends on epic BSB-29 for the verification record and the shared layer, on epic BSB-25 for the
  bundle and branch resolution, on epic BSB-23 for the project membership check, and on the
  external pinned verifier distribution.
- The new row's `claimed_verdict` is a copy of the target run's, so the verifier is asked the same
  question and the `self`/`final`/`overridden` comparison is meaningful. It is not a new agent
  claim.
- The row is created `queued` and is written `completed` with `final_verdict`, `verification` and
  the comparison in one update, so epic BSB-29's claim predicate never sees a terminal unverified
  row (Cross-epic notes).
- The new manifest must differ from the verified one; re-verifying an unchanged manifest is
  refused because the requirement is a re-verification with a changed `verify.yaml`, and the
  result would be identical.
- The target run's `verify_version` is reused, so a kit whose verifier version has moved is refused
  rather than silently grading with a different verifier. This matches epic BSB-29's rule that a
  run verified under one verifier version is not re-verified under another.

---

## STORY: BSB-30-PENDING-8

**Summary:** Show which verifier checks flipped after a re-verification
**Epic:** BSB-30 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **a re-verification to show which verifier checks changed and in which direction**, so that **I can see the effect of a `verify.yaml` edit on the same output without comparing two reports by hand**.

### Acceptance Criteria

#### Scenario: A check that flips from failed to passed is shown
Given run `1` has verification checks exactly `[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"failed","message":"required change missing"}]`
And run `9` is a completed re-verification of run `1` with verification checks exactly `[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"passed","message":"required change present"}]`
When Ada sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/9/comparison` carrying the `sb_session` cookie
Then the response is HTTP 200 with body exactly `{"run_id":9,"base_run_id":1,"flipped":[{"check":"must-change","from":"failed","to":"passed"}]}`
And `SELECT verification->'comparison' FROM runs WHERE id = 9` returns exactly `{"base_run_id":1,"flipped":[{"check":"must-change","from":"failed","to":"passed"}]}`
And `GET https://builder.skillbuilder.internal/projects/7/runs/9` contains exactly `<section id="reverify-flips">` and the exact text `must-change: failed → passed`

#### Scenario: Multiple flips are listed in ascending check-id order
Given run `1` has verification checks exactly `[{"id":"artifact-contract","status":"passed"},{"id":"must-change","status":"failed"}]`
And run `9` has verification checks exactly `[{"id":"artifact-contract","status":"failed"},{"id":"must-change","status":"passed"}]`
When the comparison for run `9` is read
Then `SELECT verification->'comparison'->'flipped' FROM runs WHERE id = 9` returns exactly `[{"check":"artifact-contract","from":"passed","to":"failed"},{"check":"must-change","from":"failed","to":"passed"}]`
And the response body's `flipped` array is exactly that array in that order

#### Scenario: A check present on only one side is listed as absent
Given run `1` has verification checks exactly `[{"id":"artifact-contract","status":"passed"},{"id":"scope","status":"passed"}]`
And run `9` has verification checks exactly `[{"id":"artifact-contract","status":"passed"},{"id":"new-check","status":"passed"}]`
When the comparison for run `9` is read
Then `SELECT verification->'comparison'->'flipped' FROM runs WHERE id = 9` returns exactly `[{"check":"new-check","from":"absent","to":"passed"},{"check":"scope","from":"passed","to":"absent"}]`

#### Scenario: A re-verification with no changed checks reports an empty list
Given run `1` and run `9` have verification checks with the same ids and statuses
When the comparison for run `9` is read
Then the response body is exactly `{"run_id":9,"base_run_id":1,"flipped":[]}`
And `GET https://builder.skillbuilder.internal/projects/7/runs/9` contains exactly `<section id="reverify-flips">` and the exact text `No checks flipped`

#### Scenario: A run that is not a re-verification has no comparison
Given run `1` has `kind` = `run`
When Ada sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/1/comparison` carrying the `sb_session` cookie
Then the response is HTTP 409 with body exactly `{"error":{"code":"not_a_reverify","message":"Run 1 is not a re-verification"}}`

#### Scenario: A re-verification that is not yet verified has no comparison
Given run `9` has `kind` = `reverify` and `verification` = `NULL`
When Ada sends `GET https://builder.skillbuilder.internal/api/projects/7/runs/9/comparison` carrying the `sb_session` cookie
Then the response is HTTP 409 with body exactly `{"error":{"code":"verification_pending","message":"The re-verification has not been verified yet"}}`

### Covered requirements (traceability)
- FR-075

### Out of scope
Deciding what a check means or changing the verifier's checks (the external pinned verifier).
Rendering the full run report or the verdict (epic BSB-33). Comparing two independent runs, which
is epic BSB-35. Changing the target or re-verification run's verification record. Re-verifying
(BSB-30-PENDING-7).

### Notes / dependencies
- Depends on BSB-30-PENDING-7 for the re-verification run and its verification, and on epic
  BSB-29 for the verification block's `checks` array and their `id` and `status` values.
- A flip is a change in a check's `status`, keyed by the check's `id`. A changed `message`, a
  duration, or a timing field is not a flip. A check that appears or disappears is listed with
  `absent` on the missing side (Open decision 8).
- The comparison is stored on the re-verification run so the result is durable after the page is
  closed; the page and API read the stored value rather than recomputing it.
- Epic BSB-33 owns the rest of the run page; this story adds only the `reverify-flips` section.

---

*Generated by `sdlc-plan-stories-write`. Coverage: FR-068, FR-069, FR-070, FR-071, FR-072, FR-073,
FR-074 and FR-075 all covered. Next steps: `sdlc-plan-epic-review` reviews this set;
`sdlc-tracker-sync` publishes the approved stories to Jira.*
