# Stories — BSB-36 (Catalog submission)

Source: Jira epic **BSB-36** — *Catalog submission* (feature area FA-15, release MVP, labels
FA-15, MVP; status To Do), fetched read-only from the Atlassian project `bheembhai-skill-builder`
through its REST API; its summary, description, functional scope, goal, stated edge cases and
covered-requirement list are the same as the BSB-36 section of `docs/product/epics.md`. The
requirement IDs mapped to the epic are in `docs/product/epic-map.json`.

Epic BSB-36 covers 10 requirements. They decompose into the 6 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-36`), is epic
**BSB-36**. The Atlassian MCP entry in `.mcp.json` is not usable in this session: its `args` value
is a string where Claude Code requires an array, so no Jira MCP tools were offered and the epic was
fetched read-only through the Atlassian REST API with the same credentials. Nothing was written to
Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-107 | BSB-36-PENDING-1 |
| FR-108 | BSB-36-PENDING-2 |
| FR-109 | BSB-36-PENDING-3 |
| FR-110 | BSB-36-PENDING-3 |
| FR-111 | BSB-36-PENDING-3 |
| FR-112 | BSB-36-PENDING-2 |
| FR-113 | BSB-36-PENDING-4 |
| FR-114 | BSB-36-PENDING-5 |
| FR-115 | BSB-36-PENDING-6 |
| FR-161 | BSB-36-PENDING-4 |

The epic's three stated edge cases are covered explicitly: a pull request closed without merge maps
to `abandoned` (BSB-36-PENDING-4); a save after submission clears readiness but does not close the
pull request (BSB-36-PENDING-5); and a permission failure on the author's identity surfaces without
falling back to a service identity (BSB-36-PENDING-2 and BSB-36-PENDING-6). The epic's non-goals are
respected: there is no catalog import, no merge automation and no platform-project write
(BSB-36-PENDING-6).

## Submission and catalog pull-request contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control, readiness,
verification and scan fixture unless it says otherwise. The member session, the local `users` rows
and the `skill-builders` gate are established by epic BSB-18. The `builds` record shape, build branch,
`head_sha` and the save endpoint are established by epics BSB-19, BSB-20 and BSB-21 (FR-018 to
FR-022, FR-127, FR-162). The bundle and skills-commit resolution are epic BSB-25's. The run's final
verdict and verification record are epics BSB-26 and BSB-29's; the run page is epic BSB-26's route
and epic BSB-33's report. The `build_readiness` aggregate, the Ready rule and its `detail` evidence
ids are epic BSB-30's (FR-069, FR-070). The static scan outcome and report API are epic BSB-31's
(FR-076 to FR-080); the LLM scan outcome and report API are epic BSB-32's (FR-082, FR-139). The
`builds`, `runs` and `skill_bundles` columns follow `docs/adr/SK-001-skill-builder.md` §1a, §5, §8
and §9.

This epic adds two columns to `builds`: `pr_number` and `pr_state` (Decision 2). Both are additive;
no existing column changes meaning. It adds no table.

**`builds` submission columns.**

| Column | Type and value |
|--------|----------------|
| `pr_number` | integer NULL; the catalog pull request's number, `NULL` until a submission succeeds |
| `pr_state` | text NULL; `open`, `merged` or `abandoned`, `NULL` until a submission succeeds |

**Ready at the head SHA.** A build is Ready at its head SHA exactly when
`builds.ready_sha = builds.head_sha` and the `build_readiness` row for `(builds.id, builds.head_sha)`
has `ready` = `true` under epic BSB-30's Ready rule. Submit evaluates readiness for the build's
current `head_sha` through BSB-30's readiness evaluation before it checks the gate, so a stale
`ready_sha` never enables Submit for a head whose checks have not passed. The evaluation may create
or update the `build_readiness` row and may set or clear `builds.ready_sha`, exactly as epic BSB-30's
Ready-SHA write rule specifies.

**Submit API.** `POST https://builder.skillbuilder.internal/api/builds/{build_id}/submit` with
`Content-Type: application/json` and body exactly `{}`. The route is behind epic BSB-18's session and
`skill-builders` gates. It is not a project route: `builds` has no project column, so project
membership is not part of the submit gate. Validation runs in this fixed order:

1. Epic BSB-18's session gate (401 `authentication_required`).
2. Epic BSB-18's `skill-builders` group gate (403 `not_a_member`).
3. Request-body validation (422 `invalid_request`).
4. Build resolution (404 `not_found`).
5. Build state (409 `already_submitted`, `already_merged` or `build_abandoned`).
6. Readiness evaluation for `head_sha` and the Ready gate (409 `not_ready`).
7. Author identity resolution (422 `source_control_identity_missing`).
8. Pull-request creation through the source-control provider.

A successful submit is HTTP 201 with `Content-Type: application/json` and exactly:

```
{"build_id":7,"state":"submitted","pr_url":"https://github.com/saraavrnd/bheembhai-skills/pull/42","pr_number":42,"pr_state":"open","ready_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b"}
```

The keys are exactly `build_id`, `state`, `pr_url`, `pr_number`, `pr_state` and `ready_sha`, in that
order. A successful submit's own `builds` row update sets exactly `state` = `submitted`,
`pr_url` = the provider's `html_url`, `pr_number` = the provider's `number` and `pr_state` = `open`;
it changes no other column. Any readiness write before it is epic BSB-30's evaluation, not part of
this update. Submit creates no commit and no branch.

**Build-page submit and state region.** Epic BSB-20's
`GET https://builder.skillbuilder.internal/builds/{build_id}` page gains one
`<section id="submit-to-catalog">`. It always contains `<div id="build-state">` and
`<div id="pull-request-state">` with the exact text below, and exactly one of the button or the link.

| `builds.state` | `build-state` text | `pull-request-state` text | Control |
|---|---|---|---|
| `open` | `State: Open` | `Pull request: None` | Submit button, disabled unless Ready at the head SHA |
| `submitted` | `State: Submitted` | `Pull request: Open` | Pull-request link |
| `merged` | `State: Merged` | `Pull request: Merged` | Pull-request link |
| `abandoned` | `State: Abandoned` | `Pull request: Abandoned` | Pull-request link |

The control elements are exactly:

- Enabled Submit: `<button id="submit-to-catalog-button" type="submit">Submit to catalog</button>`
- Disabled Submit: `<button id="submit-to-catalog-button" type="submit" disabled>Submit to catalog</button>`
- Pull-request link: `<a id="catalog-pull-request" href="{pr_url}">View pull request</a>`

A page in `submitted`, `merged` or `abandoned` state has no element with id
`submit-to-catalog-button`. A page in `open` state has no element with id `catalog-pull-request`.
The page evaluates the head SHA's readiness on request, exactly as epic BSB-30's readiness section
does.

**Author identity.** Submitting uses the author's own source-control identity: the `builds.created_by`
user's GitHub credential, read at submit time from the external secret store at
`skill-builder/users/{user_id}/github` (Decision 1). It is never stored in the builder database and
never logged. The builder never substitutes an application or service credential when the author's
credential is missing or rejected.

**Pull-request creation.** The builder calls
`POST https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls` with the author's credential in
the header `Authorization: token <author-token>` and a JSON body with exactly the four keys `title`,
`head`, `base` and `body`, in that order:

- `title` = `Skill catalog submission: sdlc-fix-bug-triage`
- `head` = `build/sdlc-fix-bug-triage`
- `base` = `main`
- `body` = the exact description `Description-A` or `Description-B` below.

The source-control stub answers that call with HTTP 201 and:

```
{"number":42,"html_url":"https://github.com/saraavrnd/bheembhai-skills/pull/42","state":"open","merged":false}
```

**Pull-request description.** `Description-A`, used when the four readiness checks are `passed`,
`passed`, `passed` and `complete`, is exactly:

```
## Skill catalog submission: sdlc-fix-bug-triage

Build: https://builder.skillbuilder.internal/builds/7
Head SHA: 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b
Skill folder: skills/sdlc-fix-bug-triage/

### Readiness checks at 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b

- Manifest: Passed
- Run: Passed
- Static scan: Passed
- LLM scan: Complete

### Evidence

- Run report: https://builder.skillbuilder.internal/projects/7/runs/1
- Static scan report: https://builder.skillbuilder.internal/api/scans/12
- LLM scan report: https://builder.skillbuilder.internal/api/llm-scans/51
```

`Description-B`, used when the LLM scan is recorded as `unavailable` and the build is still Ready,
differs from `Description-A` on exactly two lines: `- LLM scan: Unavailable` replaces
`- LLM scan: Complete`, and
`- LLM scan report: https://builder.skillbuilder.internal/api/llm-scans/52` replaces the
`/api/llm-scans/51` line. Every other byte is identical.

Both descriptions derive from the `build_readiness` row for the submitted `head_sha`. The check
lines are epic BSB-30's build-page labels (`Manifest: Passed`, `Run: Passed`, `Static scan: Passed`,
`LLM scan: Complete` or `LLM scan: Unavailable`). The evidence links are the `detail.run_id`,
`detail.static_scan_id` and `detail.llm_scan_id` of that row: the run report is epic BSB-33's run page
`https://builder.skillbuilder.internal/projects/{runs.project_id}/runs/{run_id}`; the static report
is epic BSB-31's `https://builder.skillbuilder.internal/api/scans/{scan_id}`; the LLM report is epic
BSB-32's `https://builder.skillbuilder.internal/api/llm-scans/{llm_scan_id}`. A readiness row that
is `ready`, the three checks that produce those ids have passed or completed, so all three ids are
present; the description builder reads them and never invents a link.

**Build and pull-request state.** `builds.state` moves `open` → `submitted` → `merged` or
`abandoned`. `builds.pr_state` records the provider's view: `open`, `merged` or `abandoned`. The
mapping from the provider's pull-request object is fixed:

| Provider response | `builds.state` | `builds.pr_state` |
|---|---|---|
| `state` = `open` (whatever `merged` is) | `submitted` | `open` |
| `state` = `closed`, `merged` = `true` | `merged` | `merged` |
| `state` = `closed`, `merged` = `false` | `abandoned` | `abandoned` |

A pull request closed without merge therefore maps to `abandoned`, which is the epic's stated edge
case. A build in `merged` or `abandoned` is terminal for submission: it never returns to `open` and
cannot be submitted again.

**State reconciliation.** `GET https://builder.skillbuilder.internal/builds/{build_id}` reconciles a
build whose `builds.state` = `submitted` and `builds.pr_number` is not `NULL` by calling
`GET https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/{pr_number}` with the author's
credential and applying the mapping above before rendering. It makes exactly one such call per page
request while the build is `submitted`; a build in `open`, `merged` or `abandoned` makes none. If the
provider call fails (a non-2xx response, a timeout, or a missing author credential), the recorded
`builds.state` and `builds.pr_state` are left unchanged, the page still returns HTTP 200 and shows
the recorded values, and it contains
`<div id="pull-request-reconcile-error">Pull request state could not be refreshed.</div>`.

**Save after submission.** Epic BSB-21's save endpoint
`PUT https://builder.skillbuilder.internal/api/builds/{build_id}/files/{path}` is unchanged. When a
save succeeds on a build whose `builds.state` = `submitted`, epic BSB-21's rule moves `builds.head_sha`
to the new commit and clears `builds.ready_sha`; this epic adds only the submission-side rule that
`builds.state` stays `submitted`, `builds.pr_state` stays `open`, `builds.pr_url` and
`builds.pr_number` are unchanged, and the builder does not close, merge or otherwise write to the pull
request. The build page then shows Submit disabled because the new head SHA is not Ready.

**No direct writes.** The only write this epic makes to any external system is the single
`POST /repos/saraavrnd/bheembhai-skills/pulls` request above. It makes no direct commit or push to
`main`, no `POST /git/refs`, no contents-API write, no pull-request merge, no pull-request close and
no call to a platform API. A pull request merged outside the builder is recorded by reconciliation,
not performed by the builder. The builder's service credential is never used for any submission
request.

**Fixture constants.**

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z` |
| Current time | `2026-11-15T10:20:00Z` unless a scenario sets a clock |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace`; her token's `cognito:groups` is `["skill-builders"]` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper`; her token's `cognito:groups` is `["skill-builders"]` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing`; his token's `cognito:groups` is `["skill-builders"]` |
| User Mallory | `users.id` = `45`, `cognito_sub` = `d4e5f6a7-0000-0000-0000-000000000004`, `email` = `mallory@example.com`, `name` = `Mallory Trell`; her token's `cognito:groups` is `["catalog-reviewers"]` |
| `users` fixture | exactly four rows, the users above |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42`; id `8` has `name` = `Search smoke`, `owner_id` = `43`; ids `1` to `6`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)`; Alan has no row for project `7` |
| Catalog repository | `saraavrnd/bheembhai-skills` |
| Catalog main branch | `main`, unchanged at `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` throughout |
| Head SHA (`H`) | `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` |
| No-evidence SHA (`H5`) | `3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d`; a valid tree identical to `H`'s, with no `runs` row and no `skill_bundles` row |
| Lint-failure SHA (`H6`) | `7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e`; the tree's `skills/sdlc-fix-bug-triage/verify.yaml` makes the pinned verifier's `lint` exit `1` |
| Saved head (`S`) | the commit the successful save in BSB-36-PENDING-5 creates on `build/sdlc-fix-bug-triage`; the scenario captures it with `git rev-parse origin/build/sdlc-fix-bug-triage`; it is a 40-character lowercase hex SHA different from `H` |
| Build branch | `build/sdlc-fix-bug-triage` in the catalog repository |
| Build-skill bundle | `skill_bundles` (`skills_commit_sha` `H`, `skill` `sdlc-fix-bug-triage`, `bundle_sha256` `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`, `s3_key` `bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz`) |
| Author GitHub credential | user `42`'s credential is read from the external secret store at `skill-builder/users/42/github`; its exact fixture value is `ghp_ada_fixture_token` |
| Service GitHub credential | the builder's application credential has the exact fixture value `ghp_service_fixture_token`; it is never sent on any submission request |
| Source-control API | `https://api.github.com`; the stub records every request's method, path, headers and body |
| Pull-request create response | `{"number":42,"html_url":"https://github.com/saraavrnd/bheembhai-skills/pull/42","state":"open","merged":false}` |
| Pull-request read default | `GET /repos/saraavrnd/bheembhai-skills/pulls/{number}` returns HTTP 200 with body exactly `{"state":"open","merged":false}` unless a scenario overrides it |
| Platform API | `https://platform.bheembhai.internal/api`; the stub records every request and returns HTTP 500 if called |
| Next pull-request number | `42` |

**`builds` fixture.** Exactly sixteen rows with ids `1` to `16`. Rows other than the four below are
unrelated fixture builds and are never read by these scenarios.

| id | `kind` | `skill` | `branch` | `created_by` | `head_sha` | `ready_sha` | `pr_url` | `pr_number` | `pr_state` | `state` |
|----|--------|---------|----------|--------------|------------|-------------|----------|-------------|------------|---------|
| `7` | `edit` | `sdlc-fix-bug-triage` | `build/sdlc-fix-bug-triage` | `42` | `H` | `H` | `NULL` | `NULL` | `NULL` | `open` |
| `8` | `edit` | `sdlc-fix-bug-recheck` | `build/sdlc-fix-bug-recheck` | `42` | `H` | `H` | `https://github.com/saraavrnd/bheembhai-skills/pull/41` | `41` | `open` | `submitted` |
| `9` | `edit` | `sdlc-fix-bug-review` | `build/sdlc-fix-bug-review` | `42` | `H` | `H` | `https://github.com/saraavrnd/bheembhai-skills/pull/39` | `39` | `merged` | `merged` |
| `10` | `edit` | `sdlc-fix-bug-close` | `build/sdlc-fix-bug-close` | `42` | `H` | `H` | `https://github.com/saraavrnd/bheembhai-skills/pull/38` | `38` | `abandoned` | `abandoned` |

A scenario that needs build `7` not Ready overrides `builds.ready_sha` and the
`build_readiness` row it names; the other columns stay as written.

**`build_readiness` fixture.** Exactly the rows below. A row's `detail` JSONB holds epic BSB-30's
per-check evidence; only the keys the description reads are shown.

| `build_id` | `sha` | `manifest_state` | `run_state` | `static_state` | `llm_state` | `ready` | `detail` |
|------------|-------|------------------|-------------|----------------|-------------|---------|----------|
| `7` | `H` | `passed` | `passed` | `passed` | `complete` | `true` | `{"run_id":1,"static_scan_id":12,"llm_scan_id":51}` |
| `7` | `H6` | `failed` | `not_run` | `not_run` | `not_run` | `false` | `{"manifest":{"lint_exit":1,"lint_stderr":"manifest invalid","check_py_exit":null}}` |

**Runs fixture.** Epic BSB-30's seven-row fixture is unchanged. Run `1` is the qualifying run for
build `7`'s skill at `H`: `project_id` = `7`, `user_id` = `42`, `skill` = `sdlc-fix-bug-triage`,
`kind` = `run`, `skills_commit_sha` = `H`, `state` = `completed`, `final_verdict` = `completed` and
`verification.status` = `passed`. No run exists at `H5` or `H6`.

**Scan fixture.** Static scan `12` is `completed` with builder verdict `passed` for content SHA
`b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`. LLM scan `51` is `complete` for
the same content SHA with model `test-model-medium`; LLM scan `52` is `unavailable` for the same
content SHA with `error` = `llm_model_key_unavailable` and model `test-model-medium`.

**Error bodies.** Every refusal uses the shared body
`{"error":{"code":"code_value","message":"message text"}}`:

| Condition | Status | `code` | `message` exactly |
|-----------|--------|--------|-------------------|
| no session | 401 | `authentication_required` | `Sign in to use the skill builder.` |
| caller is not in `skill-builders` | 403 | `not_a_member` | `You are not a member of the skill-builders group` |
| body is not the empty JSON object | 422 | `invalid_request` | `The request body must be an empty JSON object.` |
| build does not exist | 404 | `not_found` | `Build not found` |
| build is already `submitted` | 409 | `already_submitted` | `Build <id> already has an open catalog pull request.` |
| build is `merged` | 409 | `already_merged` | `Build <id> has already been merged into the catalog.` |
| build is `abandoned` | 409 | `build_abandoned` | `Build <id> has been abandoned.` |
| build is not Ready at its head SHA | 409 | `not_ready` | `Build <id> is not Ready at head SHA <sha>.` |
| the author has no source-control credential | 422 | `source_control_identity_missing` | `No source-control identity is configured for user <user_id>.` |
| the provider rejects the author's credential | 502 | `source_control_identity_failed` | `The author's source-control identity could not open the pull request: <provider-message>` |

In `not_ready`, `<sha>` is the exact 40-character lowercase hex `builds.head_sha` that was evaluated.
In `source_control_identity_failed`, `<provider-message>` is the provider response's `message` value
verbatim.

## Decisions recorded in this decomposition (confirm at review)

1. **Author identity source (FR-108).** FR-108 requires the author's own source-control identity,
   but ADR §4 defines only project-scoped `github` integrations and epic BSB-23 (FA-5) has no
   stories yet. This decomposition treats the author's GitHub credential as a per-user secret in the
   external secret store at `skill-builder/users/{user_id}/github`, read at submit time and never
   stored in the builder database; provisioning it is an external prerequisite like the catalog
   repository and its review flow. If review decides the project `github` integration's token is the
   author identity, only the credential adapter changes; the gate, request contract and no-fallback
   rule do not.
2. **Pull-request columns.** FR-161 says the builder records the pull-request state on the build, but
   the ADR §9 `builds` table names only `pr_url` and `state`. This decomposition adds `pr_number` and
   `pr_state` as additive columns. `builds.state` remains the build state machine; `pr_state` is the
   provider's view. If review prefers one column, the mapping table and page text do not change.
3. **Reconciliation trigger.** The epic says to reconcile state changes from the source-control
   provider but not when. This decomposition reconciles on each build-page read while the build is
   `submitted`, matching epic BSB-30's on-request readiness evaluation. No webhook, scheduler or
   merge automation is added.
4. **Build-page state region.** The epic requires tracking `open`, `submitted`, `merged` and
   `abandoned` but no page region exists for it. This decomposition adds
   `<section id="submit-to-catalog">` with `build-state`, `pull-request-state`, the Submit button and
   the pull-request link to epic BSB-20's page. Epic BSB-21's head-SHA and readiness regions are
   unchanged.
5. **Readiness evaluation on submit.** Submit evaluates the current head SHA through epic BSB-30's
   readiness evaluation before gating, so a `ready_sha` left from an older head can never enable a
   submission. This makes the gate depend on BSB-30's `build_readiness` row and not on the page's last
   render.
6. **Description evidence source.** The description lists the four states and three evidence ids
   from the `build_readiness` row for the submitted head SHA, not from a fresh scan or a search over
   `runs`. This makes the description match exactly what BSB-30 judged Ready.
7. **Link forms.** The run report link is the run page route epic BSB-26 defines and epic BSB-33
   extends; the scan links are epic BSB-31's and epic BSB-32's report APIs. These are the only
   per-evidence URLs the referenced epics define. If review prefers the build-page anchors
   `#static-scan-report` and `#llm-scan-report`, only the URL builder changes.
8. **HTTP status choices.** Gate failures are 409; a missing author credential is 422; a provider
   rejection of the author's credential is 502. This keeps 403 reserved for epic BSB-18's and epic
   BSB-22's membership decisions and 401 for an absent session.
9. **Save after submission.** FR-114 says a save clears readiness but does not say what happens to
   the build state or the pull request. This decomposition keeps `builds.state` = `submitted`,
   `builds.pr_state` = `open`, `builds.pr_url` and `builds.pr_number` unchanged, and makes no
   provider write; only `head_sha` moves and `ready_sha` clears. This follows the epic's
   review-on-the-same-branch flow and ADR §8's note that a save clears Ready until the checks pass
   again.

## Cross-epic notes

- **BSB-18 (session and group gate).** Every submit request and every build page sits behind BSB-18's
  session and `skill-builders` gates. A non-member never reaches build resolution or readiness.
- **BSB-19, BSB-20 and BSB-21 (build record, branch, head and save).** Submit reads `builds.id`,
  `builds.skill`, `builds.branch`, `builds.created_by`, `builds.head_sha` and `builds.ready_sha` and
  adds only `pr_number`, `pr_state`, `state`, `pr_url` and the page region. Epic BSB-21's save
  endpoint and its head/`ready_sha` rule are consumed, not changed. BSB-21 has no stories yet; its
  decomposition must keep `head_sha` current on every save and clear `ready_sha` on a new commit.
- **BSB-22 (project membership).** Submit is not a project route because a build has no project
  column. This epic adds no project-membership check to submission. The run report linked from the
  description is subject to BSB-22's project membership when a reader opens it.
- **BSB-25 (bundle).** The evidence links resolve the bundle content SHA for `(head_sha, skill)`
  through `skill_bundles`; the description does not pack a bundle again.
- **BSB-26 and BSB-29 (run and verification).** The linked run report route is BSB-26's
  `/projects/{project_id}/runs/{run_id}`; the run is qualifying only under BSB-29's pass predicate,
  which BSB-30's `run_state` already encodes.
- **BSB-30 (readiness).** Submit consumes the `build_readiness` row, the Ready rule and the
  `detail.run_id`, `detail.static_scan_id` and `detail.llm_scan_id` evidence ids. The check labels in
  the description are the same labels as BSB-30's readiness rows.
- **BSB-31 and BSB-32 (scans).** The static link is BSB-31's `/api/scans/{scan_id}` and the LLM link
  is BSB-32's `/api/llm-scans/{llm_scan_id}`. This epic does not start a scan at submit; it links
  the scans BSB-30's Ready decision already consumed.
- **BSB-33 (run report).** The run report link points at BSB-33's run page, which owns the rendered
  report and the evidence a catalog reviewer reads.
- **BSB-34 (retention).** A purged run or scan may make a linked report unavailable; this epic
  records the link and leaves the report's retention behavior to BSB-34.
- **BSB-37 (CLI).** There is no CLI submit command in this epic; the CLI scope is BSB-37's.
- **BSB-38 (accessibility).** The Submit control, state region and pull-request link are new builder
  web surfaces; their WCAG 2.1 AA and 320-pixel reflow checks belong to BSB-38 and add no
  requirement here.

---

## STORY: BSB-36-PENDING-1

**Summary:** Enable Submit to catalog only for a build Ready at its head SHA
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-15, MVP

### Story
As a **skill author**, I want **Submit to catalog to be enabled only when my build is Ready at its current head SHA**, so that **I can never propose a skill whose checks have not passed at the commit that would be merged**.

### Acceptance Criteria

#### Scenario: A Ready build shows an enabled Submit control
Given build `7` is `open` with `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` and `pr_url` = `NULL`
And the `build_readiness` row for `(build_id 7, sha 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b)` has `manifest_state` = `passed`, `run_state` = `passed`, `static_state` = `passed`, `llm_state` = `complete` and `ready` = `true`
And Ada is a current member of the `skill-builders` group
When Ada sends `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the response contains `<div id="build-state">State: Open</div>`
And the response contains `<div id="pull-request-state">Pull request: None</div>`
And the response contains `<button id="submit-to-catalog-button" type="submit">Submit to catalog</button>`
And the response contains no element with id `catalog-pull-request`

#### Scenario: A build that is not Ready shows a disabled Submit control
Given build `7` is `open` with `head_sha` = `7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e` and `ready_sha` = `NULL`
And the `build_readiness` row for `(build_id 7, sha 7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e)` has `manifest_state` = `failed`, `run_state` = `not_run`, `static_state` = `not_run`, `llm_state` = `not_run` and `ready` = `false`
And Ada is a current member of the `skill-builders` group
When Ada sends `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the response contains `<button id="submit-to-catalog-button" type="submit" disabled>Submit to catalog</button>`
And the response contains `<div id="build-state">State: Open</div>`
And the response contains `<div id="pull-request-state">Pull request: None</div>`

#### Scenario: Submit accepts a build Ready at its head SHA
Given build `7` is `open` with `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` and `pr_url` = `NULL`
And the `build_readiness` row for `(build_id 7, sha 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b)` has `ready` = `true` with all four checks in their passing or complete state
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 201 with `Content-Type: application/json`
And the response's `build_id` is `7` and `state` is `submitted`
And the response's `ready_sha` is `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `SELECT ready, evaluated_at FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` returns `true` and a non-NULL `evaluated_at`

#### Scenario: Submit refuses a build with a failed readiness check
Given build `7` is `open` with `head_sha` = `7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e` and `ready_sha` = `NULL`
And the `build_readiness` row for `(build_id 7, sha 7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e)` has `manifest_state` = `failed`, `run_state` = `not_run`, `static_state` = `not_run`, `llm_state` = `not_run` and `ready` = `false`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 409
And the response body is exactly `{"error":{"code":"not_ready","message":"Build 7 is not Ready at head SHA 7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e."}}`
And the source-control stub records zero requests to `POST /repos/saraavrnd/bheembhai-skills/pulls`
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 7` returns `open | NULL | NULL | NULL`

#### Scenario: A head that advanced past the recorded ready SHA does not inherit Ready
Given build `7` is `open` with `head_sha` = `7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e` and `ready_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the `build_readiness` row for `(build_id 7, sha 7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e)` has `manifest_state` = `failed`, `run_state` = `not_run`, `static_state` = `not_run`, `llm_state` = `not_run` and `ready` = `false`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 409
And the response body is exactly `{"error":{"code":"not_ready","message":"Build 7 is not Ready at head SHA 7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e."}}`
And `SELECT ready_sha FROM builds WHERE id = 7` returns `NULL`
And the source-control stub records zero requests to `POST /repos/saraavrnd/bheembhai-skills/pulls`

#### Scenario: A head with no readiness evidence is refused and recorded as not run
Given build `7` is `open` with `head_sha` = `3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d` and `ready_sha` = `NULL`
And the `build_readiness` table has no row for `(build_id 7, sha 3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d)`
And no `runs` row exists with `skill` = `sdlc-fix-bug-triage` and `skills_commit_sha` = `3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d`
And no `skill_bundles` row exists for that SHA and `sdlc-fix-bug-triage`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 409
And the response body is exactly `{"error":{"code":"not_ready","message":"Build 7 is not Ready at head SHA 3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d."}}`
And `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = '3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d'` returns `passed | not_run | not_run | not_run | false`
And the source-control stub records zero requests to `POST /repos/saraavrnd/bheembhai-skills/pulls`

#### Scenario: Submit refuses a caller outside the skill-builders group
Given build `7` is `open` and Ready at its head SHA
And Mallory's `cognito:groups` claim is `["catalog-reviewers"]`
When Mallory sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}` carrying her `sb_session` cookie
Then the response is HTTP 403
And the response body is exactly `{"error":{"code":"not_a_member","message":"You are not a member of the skill-builders group"}}`
And the source-control stub records zero requests

### Covered requirements (traceability)
- FR-107

### Out of scope
Opening the pull request, recording its URL and recording its number (BSB-36-PENDING-2); composing
the pull-request description (BSB-36-PENDING-3); tracking later pull-request state changes
(BSB-36-PENDING-4); clearing readiness on a later save (BSB-36-PENDING-5); computing the four
readiness states or re-running a check (epic BSB-30); moving the build head or creating a save commit
(epic BSB-21); the direct-write prohibitions (BSB-36-PENDING-6).

### Notes / dependencies
- Depends on epic BSB-18 for the session and group gates, epic BSB-20 and epic BSB-21 for the
  `builds` row, head and `ready_sha` rule, and epic BSB-30 for `build_readiness`, the Ready rule and
  the `detail` evidence ids.
- The gate is evaluated on the build's current `head_sha`, not on `builds.ready_sha` alone. A build
  whose head advanced after Ready is refused until the new head is evaluated and passes.
- The evaluation is epic BSB-30's; this story does not change its states, its Ready rule or its
  Ready-SHA write rule. It only refuses a submission when the evaluated row is not `ready`.
- Prerequisite for BSB-36-PENDING-2 and BSB-36-PENDING-3.
- `build_readiness` has no row until readiness is evaluated; the no-evidence scenario is the first
  evaluation for that head and therefore creates the row with every check `not_run`.

---

## STORY: BSB-36-PENDING-2

**Summary:** Open a catalog pull request under the author's own source-control identity and record it on the build
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-15, MVP

### Story
As a **skill author**, I want **submitting a Ready build to open a catalog pull request as me and record its URL and number on the build**, so that **the proposal is attributable to the person who made it and the builder can show and track that pull request**.

### Acceptance Criteria

#### Scenario: Submit opens one pull request with the author's credential and records it
Given build `7` is `open` with `skill` = `sdlc-fix-bug-triage`, `branch` = `build/sdlc-fix-bug-triage`, `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `pr_url` = `NULL`, `pr_number` = `NULL` and `pr_state` = `NULL`
And the `build_readiness` row for `(build_id 7, sha 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b)` has `ready` = `true`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
And the source-control stub answers `POST /repos/saraavrnd/bheembhai-skills/pulls` with HTTP 201 and `{"number":42,"html_url":"https://github.com/saraavrnd/bheembhai-skills/pull/42","state":"open","merged":false}`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 201 with `Content-Type: application/json`
And the response body is exactly `{"build_id":7,"state":"submitted","pr_url":"https://github.com/saraavrnd/bheembhai-skills/pull/42","pr_number":42,"pr_state":"open","ready_sha":"4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b"}`
And the source-control stub records exactly one request to `POST /repos/saraavrnd/bheembhai-skills/pulls`
And that request's `Authorization` header is exactly `token ghp_ada_fixture_token`
And that request's JSON body has exactly the keys `title`, `head`, `base` and `body`
And that request's `title` is exactly `Skill catalog submission: sdlc-fix-bug-triage`
And that request's `head` is exactly `build/sdlc-fix-bug-triage`
And that request's `base` is exactly `main`
And that request's `body` is exactly `Description-A`
And no request recorded by the source-control stub carries the header value `token ghp_service_fixture_token`
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 7` returns `submitted | https://github.com/saraavrnd/bheembhai-skills/pull/42 | 42 | open`
And `git rev-parse origin/build/sdlc-fix-bug-triage` is still `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `git ls-remote origin refs/heads/main` is still `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`

#### Scenario: A rejected author credential surfaces and never falls back to the service identity
Given build `7` is `open` and Ready at `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
And the source-control stub answers `POST /repos/saraavrnd/bheembhai-skills/pulls` with HTTP 403 and body exactly `{"message":"Resource not accessible by integration"}`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 502
And the response body is exactly `{"error":{"code":"source_control_identity_failed","message":"The author's source-control identity could not open the pull request: Resource not accessible by integration"}}`
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 7` returns `open | NULL | NULL | NULL`
And the source-control stub records exactly one request to `POST /repos/saraavrnd/bheembhai-skills/pulls`
And that request's `Authorization` header is exactly `token ghp_ada_fixture_token`
And the source-control stub records zero requests whose `Authorization` header is `token ghp_service_fixture_token`

#### Scenario: A missing author credential refuses before any provider call
Given build `7` is `open` and Ready at `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the external secret store has no secret at `skill-builder/users/42/github`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 422
And the response body is exactly `{"error":{"code":"source_control_identity_missing","message":"No source-control identity is configured for user 42."}}`
And the source-control stub records zero requests
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 7` returns `open | NULL | NULL | NULL`

#### Scenario: A submitted build cannot open a second pull request
Given build `8` is `submitted` with `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/41`, `pr_number` = `41` and `pr_state` = `open`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/8/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 409
And the response body is exactly `{"error":{"code":"already_submitted","message":"Build 8 already has an open catalog pull request."}}`
And the source-control stub records zero requests to `POST /repos/saraavrnd/bheembhai-skills/pulls`
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 8` returns `submitted | https://github.com/saraavrnd/bheembhai-skills/pull/41 | 41 | open`

### Covered requirements (traceability)
- FR-108
- FR-112

### Out of scope
Deciding whether the build is Ready (BSB-36-PENDING-1); the exact contents of the pull-request
description (BSB-36-PENDING-3); tracking the pull request after creation (BSB-36-PENDING-4);
clearing readiness when a submitted build is saved (BSB-36-PENDING-5); the no-direct-write audit
(BSB-36-PENDING-6); configuring, storing or rotating the author's GitHub credential (external
prerequisite and epic BSB-23, FA-5); creating or pushing the build branch (epic BSB-19 and epic
BSB-21).

### Notes / dependencies
- Depends on BSB-36-PENDING-1 for the Ready gate and on epic BSB-19, BSB-20 and BSB-21 for the build
  branch and head. The catalog repository `saraavrnd/bheembhai-skills` and its `main` branch are
  external prerequisites.
- The author credential is read from `skill-builder/users/42/github` at request time. It is never
  copied into the builder database, a log line or a response body. A missing or rejected credential
  fails the submission; the builder never retries with its own application credential.
- Submit creates no commit: the pull request is opened from the build branch's existing head, so
  `git rev-parse origin/build/sdlc-fix-bug-triage` and `main` are unchanged.
- The two columns `pr_number` and `pr_state` are this epic's additive columns (Decision 2).
- Prerequisite for BSB-36-PENDING-3, which asserts the `body` field of this same request, and for
  BSB-36-PENDING-4, which tracks the recorded pull request.

---

## STORY: BSB-36-PENDING-3

**Summary:** Put the head-SHA readiness checks and the run and scan report links in the pull-request description
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-15, MVP

### Story
As a **catalog reviewer**, I want **the pull-request description to list the readiness checks at the submitted head SHA and link the run and scan reports**, so that **I can judge the proposal from recorded evidence without leaving the review or re-running anything myself**.

### Acceptance Criteria

#### Scenario: The description lists the four readiness checks and the three evidence links
Given build `7` is `open` and Ready at `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` with `skill` = `sdlc-fix-bug-triage`
And the `build_readiness` row for `(build_id 7, sha 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b)` has `manifest_state` = `passed`, `run_state` = `passed`, `static_state` = `passed`, `llm_state` = `complete`, `ready` = `true` and `detail` = `{"run_id":1,"static_scan_id":12,"llm_scan_id":51}`
And run `1` belongs to project `7`
And static scan `12` is `completed` with builder verdict `passed` for the build's bundle content SHA
And LLM scan `51` is `complete` for the same content SHA
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 201
And the source-control stub records exactly one request to `POST /repos/saraavrnd/bheembhai-skills/pulls`
And that request's `body` is exactly `Description-A`
And that request's `body` contains the exact line `- Manifest: Passed`
And that request's `body` contains the exact line `- Run: Passed`
And that request's `body` contains the exact line `- Static scan: Passed`
And that request's `body` contains the exact line `- LLM scan: Complete`
And that request's `body` contains the exact line `- Run report: https://builder.skillbuilder.internal/projects/7/runs/1`
And that request's `body` contains the exact line `- Static scan report: https://builder.skillbuilder.internal/api/scans/12`
And that request's `body` contains the exact line `- LLM scan report: https://builder.skillbuilder.internal/api/llm-scans/51`

#### Scenario: An unavailable LLM scan is listed as unavailable and still links its report
Given build `7` is `open` and Ready at `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` with `skill` = `sdlc-fix-bug-triage`
And the `build_readiness` row for `(build_id 7, sha 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b)` has `manifest_state` = `passed`, `run_state` = `passed`, `static_state` = `passed`, `llm_state` = `unavailable`, `ready` = `true` and `detail` = `{"run_id":1,"static_scan_id":12,"llm_scan_id":52}`
And run `1` belongs to project `7`
And the LLM scan outcome for the bundle content SHA `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a` is `unavailable`, recorded by `llm_scans` row `52` with `error` = `llm_model_key_unavailable`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 201
And the source-control stub records exactly one request to `POST /repos/saraavrnd/bheembhai-skills/pulls`
And that request's `body` is exactly `Description-B`
And that request's `body` contains the exact line `- LLM scan: Unavailable`
And that request's `body` contains the exact line `- LLM scan report: https://builder.skillbuilder.internal/api/llm-scans/52`
And that request's `body` contains no line beginning `- LLM scan: Complete`

### Covered requirements (traceability)
- FR-109
- FR-110
- FR-111

### Out of scope
The Ready gate that decides whether a description is composed at all (BSB-36-PENDING-1); the
provider request, credential and recorded URL and number (BSB-36-PENDING-2); later pull-request
state tracking (BSB-36-PENDING-4); starting, changing or re-running a scan (epic BSB-31 and epic
BSB-32); rendering the run report or the scan reports themselves (epic BSB-33 and the report APIs);
retention or redaction of linked evidence (epic BSB-34).

### Notes / dependencies
- Depends on BSB-36-PENDING-2 for the pull-request request whose `body` this story fixes, and on epic
  BSB-30 for the `build_readiness` row and its `detail.run_id`, `detail.static_scan_id` and
  `detail.llm_scan_id`.
- The description is built entirely from the readiness row for the submitted `head_sha`; it makes no
  new scan, run or provider call. This keeps the claim in the pull request identical to the evidence
  BSB-30 judged Ready.
- The run report link uses the qualifying run's `project_id` from `runs`; the scan links use the
  report ids in `detail`. The exact `Description-A` and `Description-B` blocks are in the contract
  above.
- An `unavailable` LLM scan is a permitted Ready state under epic BSB-30, so it must still produce a
  submittable description; it is listed as `Unavailable`, never hidden or converted to `Complete`.

---

## STORY: BSB-36-PENDING-4

**Summary:** Track the pull request and build through open, submitted, merged and abandoned
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-15, MVP

### Story
As a **skill author**, I want **the build to record my pull request's state and show whether it is open, merged or abandoned**, so that **I can tell what happened to my submission without opening GitHub or guessing from the branch**.

### Acceptance Criteria

#### Scenario: Submit records the pull request as open and the page shows the submitted state
Given build `7` is `open` and Ready at `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
And the source-control stub answers `POST /repos/saraavrnd/bheembhai-skills/pulls` with HTTP 201 and `{"number":42,"html_url":"https://github.com/saraavrnd/bheembhai-skills/pull/42","state":"open","merged":false}`
And the source-control stub answers `GET /repos/saraavrnd/bheembhai-skills/pulls/42` with HTTP 200 and `{"state":"open","merged":false}`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
And Ada then sends `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the submit response is HTTP 201 and its `state` is `submitted` and its `pr_state` is `open`
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 7` returns `submitted | https://github.com/saraavrnd/bheembhai-skills/pull/42 | 42 | open`
And the page response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the page response contains `<div id="build-state">State: Submitted</div>`
And the page response contains `<div id="pull-request-state">Pull request: Open</div>`
And the page response contains `<a id="catalog-pull-request" href="https://github.com/saraavrnd/bheembhai-skills/pull/42">View pull request</a>`
And the page response contains no element with id `submit-to-catalog-button`

#### Scenario: A merged pull request moves the build to merged
Given build `8` is `submitted` with `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/41`, `pr_number` = `41` and `pr_state` = `open`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
And the source-control stub answers `GET /repos/saraavrnd/bheembhai-skills/pulls/41` with HTTP 200 and `{"state":"closed","merged":true}`
When Ada sends `GET https://builder.skillbuilder.internal/builds/8` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 8` returns `merged | https://github.com/saraavrnd/bheembhai-skills/pull/41 | 41 | merged`
And the response contains `<div id="build-state">State: Merged</div>`
And the response contains `<div id="pull-request-state">Pull request: Merged</div>`
And the response contains `<a id="catalog-pull-request" href="https://github.com/saraavrnd/bheembhai-skills/pull/41">View pull request</a>`
And the response contains no element with id `submit-to-catalog-button`

#### Scenario: A pull request closed without merge moves the build to abandoned
Given build `8` is `submitted` with `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/41`, `pr_number` = `41` and `pr_state` = `open`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
And the source-control stub answers `GET /repos/saraavrnd/bheembhai-skills/pulls/41` with HTTP 200 and `{"state":"closed","merged":false}`
When Ada sends `GET https://builder.skillbuilder.internal/builds/8` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 8` returns `abandoned | https://github.com/saraavrnd/bheembhai-skills/pull/41 | 41 | abandoned`
And the response contains `<div id="build-state">State: Abandoned</div>`
And the response contains `<div id="pull-request-state">Pull request: Abandoned</div>`
And the response contains `<a id="catalog-pull-request" href="https://github.com/saraavrnd/bheembhai-skills/pull/41">View pull request</a>`

#### Scenario: A failed provider read keeps the recorded state and shows a refresh notice
Given build `8` is `submitted` with `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/41`, `pr_number` = `41` and `pr_state` = `open`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
And the source-control stub answers `GET /repos/saraavrnd/bheembhai-skills/pulls/41` with HTTP 500
When Ada sends `GET https://builder.skillbuilder.internal/builds/8` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 8` returns `submitted | https://github.com/saraavrnd/bheembhai-skills/pull/41 | 41 | open`
And the response contains `<div id="build-state">State: Submitted</div>`
And the response contains `<div id="pull-request-state">Pull request: Open</div>`
And the response contains `<div id="pull-request-reconcile-error">Pull request state could not be refreshed.</div>`

#### Scenario: A merged build cannot be submitted again
Given build `9` is `merged` with `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/39`, `pr_number` = `39` and `pr_state` = `merged`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/9/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 409
And the response body is exactly `{"error":{"code":"already_merged","message":"Build 9 has already been merged into the catalog."}}`
And the source-control stub records zero requests to `POST /repos/saraavrnd/bheembhai-skills/pulls`
And `SELECT state, pr_state FROM builds WHERE id = 9` returns `merged | merged`

#### Scenario: An abandoned build cannot be submitted again
Given build `10` is `abandoned` with `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/38`, `pr_number` = `38` and `pr_state` = `abandoned`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/10/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 409
And the response body is exactly `{"error":{"code":"build_abandoned","message":"Build 10 has been abandoned."}}`
And the source-control stub records zero requests to `POST /repos/saraavrnd/bheembhai-skills/pulls`
And `SELECT state, pr_state FROM builds WHERE id = 10` returns `abandoned | abandoned`

#### Scenario: A terminal build does not reconcile its pull request again
Given build `9` is `merged` with `pr_number` = `39` and `pr_state` = `merged`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
When Ada sends `GET https://builder.skillbuilder.internal/builds/9` twice carrying the `sb_session` cookie
Then both responses are HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the source-control stub records zero requests to `GET /repos/saraavrnd/bheembhai-skills/pulls/39`
And `SELECT state, pr_state FROM builds WHERE id = 9` returns `merged | merged`

### Covered requirements (traceability)
- FR-113
- FR-161

### Out of scope
Opening the pull request or deciding whether it may be opened (BSB-36-PENDING-1 and
BSB-36-PENDING-2); the pull-request description (BSB-36-PENDING-3); clearing readiness when a
submitted build is saved (BSB-36-PENDING-5); the no-direct-write audit (BSB-36-PENDING-6); merging,
closing or re-opening a pull request from the builder; watching the provider by webhook, scheduler or
push notification; any notification or email about the state change.

### Notes / dependencies
- Depends on BSB-36-PENDING-2 for the submit that creates `pr_url`, `pr_number` and the initial
  `pr_state` = `open`, and on epic BSB-20 for the build page. The two columns `pr_number` and
  `pr_state` are this epic's additive columns (Decision 2).
- Reconciliation runs on the build-page read for a `submitted` build and applies the fixed provider
  mapping in the contract. A `closed` pull request with `merged` = `false` is `abandoned`, which is
  the epic's explicit edge case. A provider failure never erases a recorded state.
- `submitted` and `open` are different fields on purpose: `builds.state` is the build's state machine
  and `builds.pr_state` is the provider's view. The page shows both.
- A terminal build (`merged` or `abandoned`) is never reconciled and never returns to `open`; this
  story adds no resubmission path and no merge automation.
- Prerequisite for BSB-36-PENDING-5, whose scenarios start from a `submitted` build, and for
  BSB-36-PENDING-6, which audits the reconciliation read.

---

## STORY: BSB-36-PENDING-5

**Summary:** Clear readiness when a submitted build is saved without closing its pull request
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-15, MVP

### Story
As a **skill author**, I want **a save on my submitted build to clear its Ready state while leaving the pull request open**, so that **I can fix review comments on the same branch and cannot re-submit or appear Ready until the new commit has passed the checks again**.

### Acceptance Criteria

#### Scenario: A save on a submitted build clears readiness and keeps the pull request open
Given build `7` is `submitted` with `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/42`, `pr_number` = `42` and `pr_state` = `open`
And the `build_readiness` row for `(build_id 7, sha 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b)` has `ready` = `true`
And the request body is the exact source `skills/sdlc-fix-bug-triage/SKILL.md` at `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` with the exact line `SUBMIT-FIXTURE` appended after the source file's final newline followed by a single newline
When Ada sends `PUT https://builder.skillbuilder.internal/api/builds/7/files/SKILL.md` with `Content-Type: text/markdown` and that body
Then the response is HTTP 200
And `git rev-parse origin/build/sdlc-fix-bug-triage` returns a 40-character lowercase hex SHA different from `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, and that SHA is `S`
And `SELECT head_sha, ready_sha, state, pr_url, pr_number, pr_state FROM builds WHERE id = 7` returns `S | NULL | submitted | https://github.com/saraavrnd/bheembhai-skills/pull/42 | 42 | open`
And the source-control stub records zero requests with method `PATCH` or `DELETE` to a path beginning `/repos/saraavrnd/bheembhai-skills/pulls/42`
And the source-control stub records zero requests to `PUT /repos/saraavrnd/bheembhai-skills/pulls/42/merge`
And `git ls-remote origin refs/heads/main` is still `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`

#### Scenario: The build page after the save shows Submit disabled and the pull request still open
Given the save in the previous scenario completed and the saved head is `S`, captured with `git rev-parse origin/build/sdlc-fix-bug-triage`
And the tree at `S` is `H`'s tree with only `skills/sdlc-fix-bug-triage/SKILL.md` changed, so its manifest check passes
And `builds.state` is still `submitted`, `builds.pr_state` is still `open` and `builds.ready_sha` is `NULL`
And no `build_readiness` row exists for `(build_id 7, sha S)`
And the source-control stub answers `GET /repos/saraavrnd/bheembhai-skills/pulls/42` with HTTP 200 and `{"state":"open","merged":false}`
When Ada sends `GET https://builder.skillbuilder.internal/builds/7` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And the response contains `<button id="submit-to-catalog-button" type="submit" disabled>Submit to catalog</button>`
And the response contains `<div id="build-state">State: Submitted</div>`
And the response contains `<div id="pull-request-state">Pull request: Open</div>`
And the response contains `<a id="catalog-pull-request" href="https://github.com/saraavrnd/bheembhai-skills/pull/42">View pull request</a>`
And the readiness section contains the exact text `Manifest: Passed`, `Run: Not run`, `Static scan: Not run` and `LLM scan: Not run`
And `SELECT manifest_state, run_state, static_state, llm_state, ready FROM build_readiness WHERE build_id = 7 AND sha = (SELECT head_sha FROM builds WHERE id = 7)` returns `passed | not_run | not_run | not_run | false`

#### Scenario: A rejected save leaves the submitted build and its pull request unchanged
Given build `7` is `submitted` with `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/42`, `pr_number` = `42` and `pr_state` = `open`
And the `build_readiness` row for `(build_id 7, sha 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b)` has `ready` = `true`
When Ada sends the raw, unnormalised `PUT` path `https://builder.skillbuilder.internal/api/builds/7/files/../sdlc-fix-bug-other/SKILL.md` with `Content-Type: text/markdown` and body exactly `# Other skill`
Then the response is HTTP 403
And the response body is exactly `{"error":{"code":"file_outside_skill_folder","message":"A build can only change files under skills/sdlc-fix-bug-triage/."}}`
And `git rev-parse origin/build/sdlc-fix-bug-triage` is still `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `SELECT head_sha, ready_sha, state, pr_url, pr_number, pr_state FROM builds WHERE id = 7` returns `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b | 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b | submitted | https://github.com/saraavrnd/bheembhai-skills/pull/42 | 42 | open`
And `SELECT ready FROM build_readiness WHERE build_id = 7 AND sha = '4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b'` returns `true`
And the source-control stub records zero requests with method `PATCH` or `DELETE` to a path beginning `/repos/saraavrnd/bheembhai-skills/pulls/42`

### Covered requirements (traceability)
- FR-114

### Out of scope
The save endpoint, its path confinement and its commit creation (epic BSB-21, FR-127 and FR-162);
composing the pull-request description (BSB-36-PENDING-3); opening a second pull request or
re-submitting after the save (BSB-36-PENDING-2 and BSB-36-PENDING-4); re-running the four checks or
re-evaluating readiness after the new commit (epic BSB-30); closing, merging or commenting on the
pull request (not done by the builder); pushing to `main` (never done).

### Notes / dependencies
- Depends on BSB-36-PENDING-2 for the submitted build and its recorded pull request, on epic BSB-21
  for the save endpoint and its `head_sha`/`ready_sha` rule, and on epic BSB-30 for the readiness
  states the page renders after the save.
- FR-114 is distinct from epic BSB-21's FR-022: FR-022 clears `ready_sha` on any new commit, while
  this story fixes what happens to a *submitted* build — it stays `submitted`, its pull request stays
  open and unmodified, and the new head is `not_run` until the checks run again.
- The builder never closes the pull request on a save. The new commit lands on the same build branch,
  which is the pull request's head branch, so the pull request updates naturally without a provider
  write.
- A rejected save is epic BSB-20's `file_outside_skill_folder` contract; this story asserts only that
  the rejected save changes nothing about readiness, the build state or the pull request.

---

## STORY: BSB-36-PENDING-6

**Summary:** Never write directly to the catalog or the platform outside the catalog pull request
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-15, MVP

### Story
As a **platform administrator**, I want **the builder's only outward write to be the author's catalog pull request and never a direct catalog, platform-project or project-skill write**, so that **every catalog change still goes through review and the builder cannot bypass the platform's controls**.

### Acceptance Criteria

#### Scenario: Submit writes the pull request and nothing else
Given build `7` is `open` and Ready at `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
And the source-control stub answers `POST /repos/saraavrnd/bheembhai-skills/pulls` with HTTP 201 and `{"number":42,"html_url":"https://github.com/saraavrnd/bheembhai-skills/pull/42","state":"open","merged":false}`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 201
And the source-control stub records exactly one request whose method is not `GET`, and it is `POST /repos/saraavrnd/bheembhai-skills/pulls`
And the source-control stub records zero requests with method `PUT`, `PATCH` or `DELETE` to any path beginning `/repos/saraavrnd/bheembhai-skills/`
And the source-control stub records zero requests to `POST /repos/saraavrnd/bheembhai-skills/git/refs`
And the source-control stub records zero requests to `PUT /repos/saraavrnd/bheembhai-skills/pulls/42/merge`
And `git ls-remote origin refs/heads/main` is still `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `git rev-parse origin/build/sdlc-fix-bug-triage` is still `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the platform API stub records zero requests

#### Scenario: A pull request merged outside the builder is recorded without a merge write
Given build `8` is `submitted` with `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/41`, `pr_number` = `41` and `pr_state` = `open`
And Ada has a source-control credential at `skill-builder/users/42/github` with value `ghp_ada_fixture_token`
And the source-control stub answers `GET /repos/saraavrnd/bheembhai-skills/pulls/41` with HTTP 200 and `{"state":"closed","merged":true}`
When Ada sends `GET https://builder.skillbuilder.internal/builds/8` carrying the `sb_session` cookie
Then the response is HTTP 200 with `Content-Type: text/html; charset=utf-8`
And `SELECT state, pr_state FROM builds WHERE id = 8` returns `merged | merged`
And the source-control stub records exactly one request to `GET /repos/saraavrnd/bheembhai-skills/pulls/41`
And the source-control stub records zero requests to `PUT /repos/saraavrnd/bheembhai-skills/pulls/41/merge`
And the source-control stub records zero requests with method `PUT`, `PATCH` or `DELETE` to any path beginning `/repos/saraavrnd/bheembhai-skills/`
And the platform API stub records zero requests
And `git ls-remote origin refs/heads/main` is still `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`

#### Scenario: A missing author credential produces no write at all, including no service-identity write
Given build `7` is `open` and Ready at `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the external secret store has no secret at `skill-builder/users/42/github`
And the builder's application credential is present with the value `ghp_service_fixture_token`
When Ada sends `POST https://builder.skillbuilder.internal/api/builds/7/submit` with `Content-Type: application/json` and body exactly `{}`
Then the response is HTTP 422
And the response body is exactly `{"error":{"code":"source_control_identity_missing","message":"No source-control identity is configured for user 42."}}`
And the source-control stub records zero requests of any method
And the platform API stub records zero requests
And `SELECT state, pr_url, pr_number, pr_state FROM builds WHERE id = 7` returns `open | NULL | NULL | NULL`

### Covered requirements (traceability)
- FR-115

### Out of scope
Opening the pull request and recording its URL and number (BSB-36-PENDING-2); the pull-request
description (BSB-36-PENDING-3); tracking an already-opened pull request (BSB-36-PENDING-4); the
readiness-clearing rule on a save (BSB-36-PENDING-5); creating or pushing the build branch (epic
BSB-19 and epic BSB-21); catalog import, release tagging, merge automation and platform-project or
project-skill writes (out of scope for the product); the platform's own scan and import behavior
(external).

### Notes / dependencies
- Depends on BSB-36-PENDING-2 for the one allowed provider write and on BSB-36-PENDING-4 for the
  reconciliation read. The platform API stub at `https://platform.bheembhai.internal/api` records
  every request; this story asserts it is never called.
- The allowed write set is exactly one endpoint: `POST /repos/saraavrnd/bheembhai-skills/pulls`.
  Every other source-control call the builder makes for submission is a `GET`.
- The builder never merges, closes or re-opens a pull request, never commits or pushes to `main`, and
  never uses its own service credential as a fallback for the author's. This is the epic's
  identity-only creation rule and its no-direct-write rule in one testable slice.
- The create request itself is the author's pull request, not a direct catalog write: it proposes a
  change from the build branch and changes no catalog content until a reviewer merges it.

---

*Generated by `sdlc-plan-stories-write`. Coverage: all 10 requirements mapped to BSB-36 are covered
by these 6 stories. Next step: `sdlc-plan-epic-review` reviews this set, then `sdlc-tracker-sync`
publishes the approved stories to Jira.*
