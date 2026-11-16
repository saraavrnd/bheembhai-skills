# Stories — BSB-20 (Skill cloning & edit builds)

Source: Jira epic **BSB-20** — *Skill cloning & edit builds* (feature area FA-2, release MVP,
labels FA-2, MVP), read from the Atlassian project `bheembhai-skill-builder`; its summary,
description and functional scope are the same as the BSB-20 section of `docs/product/epics.md`.
The requirement IDs mapped to the epic are in `docs/product/epic-map.json`.

Epic BSB-20 covers 7 requirements. They decompose into the 3 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item is epic **BSB-20**, fetched read-only from the Atlassian Jira API
(`GET /rest/api/3/issue/BSB-20`), and its seven requirements are the ones decomposed here.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-011 | BSB-20-PENDING-1 |
| FR-012 | BSB-20-PENDING-1 |
| FR-013 | BSB-20-PENDING-1 |
| FR-014 | BSB-20-PENDING-1 |
| FR-124 | BSB-20-PENDING-2 |
| FR-125 | BSB-20-PENDING-3 |
| FR-126 | BSB-20-PENDING-2 |

The clone name-rule rejections in BSB-20-PENDING-1 are the epic's stated edge case ("the clone
target name must pass the same name rules as a new build"). The rules they exercise are FR-015 and
FR-017, owned by epic BSB-19, so they are exercised but not claimed here. FR-016 (a name used by
another open build) is owned by epic BSB-19; SK-001 §1a applies it to create and clone builds but not
to edit builds, where "open build" means the `builds.state` value `open` (SK-001 §9). This epic does
not assert the clone collision until BSB-19's decomposition fixes its response; a `build/<skill>`
branch left by a submitted, merged or abandoned build is Open question 1(b) in `epic-review.md`.

## Build and catalog contract (test fixture constants)

Every scenario below uses these exact values. The catalog repository, its `main` branch and its
`main` head are external prerequisites supplied outside the builder (PRD §8); the builder is
configured with them. The member session and local user are established by epic BSB-18, and every
request below carries that session. Build branch names, build kinds and the `builds` columns follow
`docs/adr/SK-001-skill-builder.md` §1a and §9. No story below writes the catalog's `main` branch:
the only catalog branch written is the build branch, and the catalog changes only when the pull
request opened by epic BSB-36 merges.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`=`a1b2c3d4-0000-0000-0000-000000000001`, `email`=`ada@example.com`, `name`=`Ada Lovelace`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z`. The matching local `users` row has `id` = `42`. |
| Catalog repository | `saraavrnd/bheembhai-skills` |
| Catalog default branch | `main` |
| `main` head used by the clone and edit fixtures | `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` |
| Skills directory | `skills/` |
| Source skill | `sdlc-fix-bug-triage`, folder `skills/sdlc-fix-bug-triage/`, present at the `main` head above |
| Build branch | `build/` followed by the skill name, giving `build/sdlc-fix-bug-recheck` for the clone fixture and `build/sdlc-fix-bug-triage` for the edit fixtures |
| Build kinds | `create`, `clone`, `edit` |
| `builds` columns used here | `id`, `kind`, `skill`, `cloned_from`, `branch`, `created_by`, `head_sha`, `ready_sha`, `pr_url`, `state` |
| `builds` fixture state | rows with ids `1` to `16` exist; no row has `skill` = `sdlc-fix-bug-recheck`, and no row has `skill` = `sdlc-fix-bug-triage` with `state` = `open` |
| Build API | `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` |
| Success status | HTTP 201 with `Content-Type: application/json` |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |

The source skill folder at the `main` head contains exactly these seven files, in the order
`git ls-tree -r --name-only` returns them:

```
skills/sdlc-fix-bug-triage/SKILL.md
skills/sdlc-fix-bug-triage/examples/bug-triage-LEARN-87.md
skills/sdlc-fix-bug-triage/references/severity-rubric.md
skills/sdlc-fix-bug-triage/references/template-guide.md
skills/sdlc-fix-bug-triage/references/triage-decisions.md
skills/sdlc-fix-bug-triage/templates/bug-triage.md.tmpl
skills/sdlc-fix-bug-triage/verify.yaml
```

The build's own skill is carried in the `skill` field for every build kind. The successful clone
request body is exactly:

```
{"kind":"clone","source":"sdlc-fix-bug-triage","skill":"sdlc-fix-bug-recheck"}
```

The successful edit-build request body is exactly:

```
{"kind":"edit","skill":"sdlc-fix-bug-triage"}
```

Epic BSB-19's `create` kind extends the same request contract and names the skill being created
in the same `skill` field.

On a successful clone or edit-build open, `head_sha` is the SHA of the single commit the builder
creates on the build branch. A test reads it with `git rev-parse origin/build/sdlc-fix-bug-recheck`
for the clone and `git rev-parse origin/build/sdlc-fix-bug-triage` for the edit build.

The rejection responses used below are fixed. The two name-rule rows (FR-015 and FR-017) are owned
by epic BSB-19: BSB-20 asserts the same response the create path returns for the same name. The
`skill_not_found` and `file_outside_skill_folder` rows are BSB-20's own. FR-016 (another open
build) has no row here because its scope for clone and edit builds is Open question 1(a) in
`epic-review.md`.

**BSB-19-owned name-rule responses**

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| Clone target name already exists on `main` | 409 | `{"error":{"code":"skill_name_exists","message":"A skill named 'sdlc-fix-bug-triage' already exists on main."}}` |
| Clone target name breaks the catalog name pattern | 422 | `{"error":{"code":"skill_name_invalid","message":"Skill name must follow sdlc-<area>-<action> using lowercase letters, digits and hyphens."}}` |

**BSB-20-owned responses**

| Situation | Status | Exact response body |
|-----------|--------|---------------------|
| The skill name does not exist on the current `main` head — either an edit build's skill or a clone's source | 404 | `{"error":{"code":"skill_not_found","message":"No skill named 'sdlc-fix-bug-recheck' exists on main."}}` |
| A build's save targets a path outside that build's skill folder | 403 | `{"error":{"code":"file_outside_skill_folder","message":"A build can only change files under skills/sdlc-fix-bug-triage/."}}` |

In each `skill_not_found` body the quoted name is the skill name that was requested.

---

## STORY: BSB-20-PENDING-1

**Summary:** Clone an existing catalog skill into a new build under a validated new name
**Epic:** BSB-20 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **to clone an existing catalog skill under a new name**, so that **I can adapt a proven skill without rebuilding it from scratch and without changing the original**.

### Acceptance Criteria

#### Scenario: Clone creates a new build on its own branch
Given the catalog `saraavrnd/bheembhai-skills` `main` head is `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the `builds` table has no row with `skill` = `sdlc-fix-bug-recheck`
And no branch `build/sdlc-fix-bug-recheck` exists on the origin remote
And the author has a valid member session with local `users.id` = `42`
When the author sends `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` and body exactly `{"kind":"clone","source":"sdlc-fix-bug-triage","skill":"sdlc-fix-bug-recheck"}`
Then the builder responds with HTTP status 201
And the `Content-Type` response header is `application/json`
And the JSON response's `id` is `17`, `kind` is `clone`, `skill` is `sdlc-fix-bug-recheck`, `cloned_from` is `sdlc-fix-bug-triage`, `branch` is `build/sdlc-fix-bug-recheck` and `state` is `open`
And the JSON response's `head_sha` equals the value returned by `git rev-parse origin/build/sdlc-fix-bug-recheck`
And `SELECT id, kind, skill, cloned_from, branch, created_by, state FROM builds WHERE id = 17` returns exactly `17 | clone | sdlc-fix-bug-recheck | sdlc-fix-bug-triage | build/sdlc-fix-bug-recheck | 42 | open`
And branch `build/sdlc-fix-bug-recheck` exists on the origin remote
And `GET https://builder.skillbuilder.internal/builds/17` returns HTTP status 200 and its response body contains the exact text `sdlc-fix-bug-recheck` and the exact text `build/sdlc-fix-bug-recheck`
And `git rev-list --count 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b..origin/build/sdlc-fix-bug-recheck` returns `1`
And `git rev-parse origin/build/sdlc-fix-bug-recheck^` equals `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the commit message is exactly `Clone sdlc-fix-bug-triage as sdlc-fix-bug-recheck`

#### Scenario: Clone copies the whole source skill folder
Given branch `build/sdlc-fix-bug-recheck` was created by the clone above
When the test runs `git ls-tree -r --name-only origin/build/sdlc-fix-bug-recheck -- skills/sdlc-fix-bug-recheck`
Then the command returns exactly these seven paths in this order: `skills/sdlc-fix-bug-recheck/SKILL.md`, `skills/sdlc-fix-bug-recheck/examples/bug-triage-LEARN-87.md`, `skills/sdlc-fix-bug-recheck/references/severity-rubric.md`, `skills/sdlc-fix-bug-recheck/references/template-guide.md`, `skills/sdlc-fix-bug-recheck/references/triage-decisions.md`, `skills/sdlc-fix-bug-recheck/templates/bug-triage.md.tmpl`, `skills/sdlc-fix-bug-recheck/verify.yaml`
And for each of the six relative paths `verify.yaml`, `examples/bug-triage-LEARN-87.md`, `references/severity-rubric.md`, `references/template-guide.md`, `references/triage-decisions.md` and `templates/bug-triage.md.tmpl`, the blob id at that relative path under `skills/sdlc-fix-bug-recheck/` on `build/sdlc-fix-bug-recheck` equals the blob id at the same relative path under `skills/sdlc-fix-bug-triage/` at `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `git diff --name-only 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b origin/build/sdlc-fix-bug-recheck` lists only paths beginning `skills/sdlc-fix-bug-recheck/`

#### Scenario: Clone rewrites only the frontmatter name
Given the source `skills/sdlc-fix-bug-triage/SKILL.md` at `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` has line 2 exactly `name: sdlc-fix-bug-triage`
When the clone completes
Then line 2 of `skills/sdlc-fix-bug-recheck/SKILL.md` on `build/sdlc-fix-bug-recheck` is exactly `name: sdlc-fix-bug-recheck`
And deleting line 2 from both `SKILL.md` files produces byte-identical content
And the `role`, `description` and `compatibility` frontmatter values in the copy are byte-identical to the source
And the copied body after the closing `---` line is byte-identical to the source, including its `# sdlc-fix-bug-triage — Decide What the Bug Is` heading

#### Scenario: Clone leaves the source skill unchanged
Given the clone above completed at `main` head `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the source tree object id `git rev-parse 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b:skills/sdlc-fix-bug-triage` was captured before the clone
When the author replaces `skills/sdlc-fix-bug-recheck/references/severity-rubric.md` on `build/sdlc-fix-bug-recheck` with the exact content `# Recheck severity rubric` and commits it
Then `git ls-remote origin refs/heads/main` still returns `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `git rev-parse origin/main:skills/sdlc-fix-bug-triage` equals the source tree object id captured before the clone
And `git rev-parse 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b:skills/sdlc-fix-bug-triage/references/severity-rubric.md` is unchanged
And `git rev-parse origin/build/sdlc-fix-bug-recheck:skills/sdlc-fix-bug-recheck/references/severity-rubric.md` differs from `git rev-parse 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b:skills/sdlc-fix-bug-triage/references/severity-rubric.md`
And `git diff --name-only 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b origin/main` is empty

#### Scenario: Clone refuses a source skill that does not exist on main
Given the catalog `saraavrnd/bheembhai-skills` `main` head is `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `skills/sdlc-fix-bug-recheck/` does not exist at that head
And no branch `build/sdlc-fix-bug-retry` exists on the origin remote
And the `builds` table has no row with `skill` = `sdlc-fix-bug-retry`
And the author has a valid member session with local `users.id` = `42`
When the author sends `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` and body exactly `{"kind":"clone","source":"sdlc-fix-bug-recheck","skill":"sdlc-fix-bug-retry"}`
Then the builder responds with HTTP status 404
And the response body is exactly `{"error":{"code":"skill_not_found","message":"No skill named 'sdlc-fix-bug-recheck' exists on main."}}`
And no branch `build/sdlc-fix-bug-retry` exists on the origin remote
And `SELECT count(*) FROM builds WHERE skill = 'sdlc-fix-bug-retry'` returns `0`

#### Scenario: Clone refuses a target name that already exists on main
Given `skills/sdlc-fix-bug-triage/` exists at `main` head `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And no branch `build/sdlc-fix-bug-triage` exists on the origin remote
And the `builds` table has no row with `skill` = `sdlc-fix-bug-triage`
When the author sends `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` and body exactly `{"kind":"clone","source":"sdlc-fix-bug-triage","skill":"sdlc-fix-bug-triage"}`
Then the builder responds with HTTP status 409
And the response body is exactly `{"error":{"code":"skill_name_exists","message":"A skill named 'sdlc-fix-bug-triage' already exists on main."}}`
And no branch `build/sdlc-fix-bug-triage` exists on the origin remote
And `SELECT count(*) FROM builds WHERE skill = 'sdlc-fix-bug-triage'` returns `0`

#### Scenario: Clone refuses a target name that breaks the catalog name pattern
Given the catalog `main` head is `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the `builds` table has no row with `skill` = `BugTriage`
And no branch `build/BugTriage` exists on the origin remote
When the author sends `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` and body exactly `{"kind":"clone","source":"sdlc-fix-bug-triage","skill":"BugTriage"}`
Then the builder responds with HTTP status 422
And the response body is exactly `{"error":{"code":"skill_name_invalid","message":"Skill name must follow sdlc-<area>-<action> using lowercase letters, digits and hyphens."}}`
And no branch `build/BugTriage` exists on the origin remote
And `SELECT count(*) FROM builds WHERE skill = 'BugTriage'` returns `0`

### Covered requirements (traceability)
- FR-011
- FR-012
- FR-013
- FR-014

### Out of scope
Editing the cloned skill's files after the clone completes (epic BSB-21, FR-127 and FR-162);
creating a build from a new name and scaffolding it (epic BSB-19, FR-006 to FR-010); defining or
changing the catalog name rules themselves — the clone path calls the name validator that create
builds use, and epic BSB-19 owns the shared name validator (FR-015, FR-016 and FR-017); SK-001 §1a
applies FR-016 to clone builds as well as create builds, but the collision response is BSB-19's and
is not defined here; deleting or renaming catalog skills; opening the catalog pull request (epic
BSB-36).

### Notes / dependencies
- Depends on epic BSB-18 for the member session and the local `users.id` = `42`, and on epic BSB-19
  for the `builds` record shape and build-branch creation (FR-006, FR-007) and for the shared name
  validator (FR-015, FR-016 and FR-017). FR-016 is owned by epic BSB-19 (its requirement home in
  `epic-map.json`), which scopes it to create builds; SK-001 §1a also applies it to clone builds
  ("Both refuse a name that already exists on `main` or on another open build"), so this story
  asserts the same response the create path returns once BSB-19 fixes it. No collision scenario is
  written while that response and the stale `build/<skill>` branch rule (Open question 1(b)) are
  undefined. The catalog repository `saraavrnd/bheembhai-skills` and its `main` branch are external
  prerequisites.
- The `POST /api/builds` route and its `create` kind are epic BSB-19's (FR-006); this epic adds the
  `clone` and `edit` kinds to the same request contract.
- The clone is a one-shot copy. `builds.cloned_from` records provenance only; there is no live link,
  so later changes to either skill never propagate to the other.
- Only the frontmatter `name:` line is rewritten. FR-013 scopes the rewrite to the frontmatter, so
  the copied body stays byte-identical to the source, including the source name that appears in its
  heading; no other occurrence of the source name is rewritten.
- The builder never writes the catalog's `main` branch. The clone commit lands only on
  `build/sdlc-fix-bug-recheck`, and the source folder on `main` is read-only to this story.
- The clone source folder is resolved from the current `main` head immediately before the branch
  is created, the same as BSB-20-PENDING-2. A stale listing is never used, so a source renamed or
  deleted on `main` is caught before any branch exists (see the `skill_not_found` scenario).
- The two name-rule rejection responses in the contract table belong to epic BSB-19's name
  validator (FR-015 and FR-017); this story asserts the same responses the create path returns for
  the same name. FR-016's open-build collision rule is owned by BSB-19 and is not asserted here
  because its response is undefined (Open question 1(a)) and a stale non-open build branch raises
  Open question 1(b).
- Saves on a clone build are confined to `skills/sdlc-fix-bug-recheck/` by the same save-path
  rule; the save endpoint and its contract are epic BSB-21's (FR-127 and FR-162).
- The *Clone leaves the source skill unchanged* scenario makes its commit directly with git as the
  test, not through the builder's save endpoint, so it does not depend on BSB-21.

---

## STORY: BSB-20-PENDING-2

**Summary:** Open an existing catalog skill in an edit build cut from the current main head and reject a missing skill
**Epic:** BSB-20 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **to open an existing catalog skill in an edit build cut from the current main branch**, so that **I can change a live skill through the same run, scan, Ready and submit path as a new build**.

### Acceptance Criteria

#### Scenario: Open creates an edit build on a branch cut from main
Given the catalog `saraavrnd/bheembhai-skills` `main` head is `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `skills/sdlc-fix-bug-triage/` exists at that head and contains `SKILL.md` and `verify.yaml`
And no branch `build/sdlc-fix-bug-triage` exists on the origin remote
And the `builds` table has no row with `skill` = `sdlc-fix-bug-triage` and `state` = `open`
And the author has a valid member session with local `users.id` = `42`
When the author sends `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` and body exactly `{"kind":"edit","skill":"sdlc-fix-bug-triage"}`
Then the builder responds with HTTP status 201
And the `Content-Type` response header is `application/json`
And the JSON response's `id` is `17`, `kind` is `edit`, `skill` is `sdlc-fix-bug-triage`, `cloned_from` is `null`, `branch` is `build/sdlc-fix-bug-triage` and `state` is `open`
And the JSON response's `head_sha` equals the value returned by `git rev-parse origin/build/sdlc-fix-bug-triage`
And `SELECT id, kind, skill, cloned_from, branch, created_by, state FROM builds WHERE id = 17` returns exactly `17 | edit | sdlc-fix-bug-triage | NULL | build/sdlc-fix-bug-triage | 42 | open`
And branch `build/sdlc-fix-bug-triage` exists on the origin remote
And `GET https://builder.skillbuilder.internal/builds/17` returns HTTP status 200 and its response body contains the exact text `sdlc-fix-bug-triage` and the exact text `build/sdlc-fix-bug-triage`
And `git rev-list --count 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b..origin/build/sdlc-fix-bug-triage` returns `1`
And `git rev-parse origin/build/sdlc-fix-bug-triage^` equals `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `git rev-parse origin/build/sdlc-fix-bug-triage:skills/sdlc-fix-bug-triage` equals `git rev-parse 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b:skills/sdlc-fix-bug-triage`
And `git diff --name-only 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b origin/build/sdlc-fix-bug-triage` is empty (the edit-open commit changes no files)
And the commit message is exactly `Open edit build for sdlc-fix-bug-triage`

#### Scenario: Edit build is cut from the main head current at request time
Given the author viewed the skill when `main` head was `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `main` advanced to `9b8a7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b` before the request and `skills/sdlc-fix-bug-triage/` still exists at that head
And no branch `build/sdlc-fix-bug-triage` exists on the origin remote
When the author sends `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` and body exactly `{"kind":"edit","skill":"sdlc-fix-bug-triage"}`
Then the builder responds with HTTP status 201
And `git rev-parse origin/build/sdlc-fix-bug-triage^` equals `9b8a7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b`
And `git rev-parse origin/build/sdlc-fix-bug-triage:skills/sdlc-fix-bug-triage` equals `git rev-parse 9b8a7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b:skills/sdlc-fix-bug-triage`
And the JSON response's `head_sha` equals `git rev-parse origin/build/sdlc-fix-bug-triage`

#### Scenario: Edit build for a name that does not exist on main is rejected
Given the catalog `main` head is `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And `skills/sdlc-fix-bug-recheck/` does not exist at that head
And no branch `build/sdlc-fix-bug-recheck` exists on the origin remote
And the `builds` table has no row with `skill` = `sdlc-fix-bug-recheck`
When the author sends `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` and body exactly `{"kind":"edit","skill":"sdlc-fix-bug-recheck"}`
Then the builder responds with HTTP status 404
And the response body is exactly `{"error":{"code":"skill_not_found","message":"No skill named 'sdlc-fix-bug-recheck' exists on main."}}`
And no branch `build/sdlc-fix-bug-recheck` exists on the origin remote
And `SELECT count(*) FROM builds WHERE skill = 'sdlc-fix-bug-recheck'` returns `0`

#### Scenario: Edit build whose skill was deleted from main after selection is rejected
Given the author listed skills when `main` head was `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` and `skills/sdlc-fix-bug-triage/` existed
And `main` advanced to `9b8a7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b` and `skills/sdlc-fix-bug-triage/` does not exist at that head
And no branch `build/sdlc-fix-bug-triage` exists on the origin remote
When the author sends `POST https://builder.skillbuilder.internal/api/builds` with `Content-Type: application/json` and body exactly `{"kind":"edit","skill":"sdlc-fix-bug-triage"}`
Then the builder responds with HTTP status 404
And the response body is exactly `{"error":{"code":"skill_not_found","message":"No skill named 'sdlc-fix-bug-triage' exists on main."}}`
And no branch `build/sdlc-fix-bug-triage` exists on the origin remote
And `SELECT count(*) FROM builds WHERE skill = 'sdlc-fix-bug-triage'` returns `0`

### Covered requirements (traceability)
- FR-124
- FR-126

### Out of scope
Editing or saving files after the edit build is opened (epic BSB-21, FR-018, FR-019, FR-127 and
FR-162); creating new skills or cloning an existing one (story BSB-20-PENDING-1 and epic BSB-19);
detecting a skill deleted after the edit build has been opened — the build keeps its own branch, and
later saves are epic BSB-21's concern; opening the catalog pull request (epic BSB-36).

### Notes / dependencies
- Depends on epic BSB-18 for the member session and the local `users.id` = `42`, on epic BSB-19 for
  the `builds` record shape and build-branch creation (FR-006, FR-007), and on the external catalog
  repository `saraavrnd/bheembhai-skills`. The `POST /api/builds` route and its `create` kind are
  epic BSB-19's (FR-006); this story adds the `edit` kind to the same request contract.
- The edit build resolves the skill folder from the current `main` head immediately before creating
  the branch. A stale listing is never used, so a folder renamed or deleted on `main` is caught
  before any branch exists.
- The branch parent is the `main` head used for that resolution, and `builds.head_sha` is the single
  edit-open commit created on top of it. The skill folder on the branch has the same tree object id
  as the folder at the resolved `main` head.
- The edit-open commit is empty: it changes no path relative to the resolved `main` head, so
  `git diff --name-only` between them is empty until the first save.
- The target folder recorded at open (`skills/sdlc-fix-bug-triage/`) is the folder the save-path
  confinement rule uses; the save endpoint and its contract are epic BSB-21's (FR-127 and FR-162).
- Prerequisite for BSB-20-PENDING-3.
- FR-016 is owned by epic BSB-19 and SK-001 §1a applies it to create and clone builds, not to the
  `edit` kind; this epic therefore defines no edit-kind concurrency rule. A
  `build/sdlc-fix-bug-triage` branch left behind by a submitted, merged or abandoned build is Open
  question 1(b) in `epic-review.md`; this story adds no separate concurrency rule. The fixtures
  start with no open `build/sdlc-fix-bug-triage` branch.

---

## STORY: BSB-20-PENDING-3

**Summary:** Keep an edit build's saves in the existing skill folder
**Epic:** BSB-20 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **every save in an edit build to change the existing skill folder**, so that **my catalog pull request updates the skill in place instead of adding a duplicate folder**.

### Acceptance Criteria

#### Scenario: Saving an edited file commits into the existing skill folder
Given an edit build with `id` = `17` in state `open` exists on branch `build/sdlc-fix-bug-triage` cut from `main` head `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the edit build was opened by BSB-20-PENDING-2, whose open commit changes no files
And no save has been made on that branch, so `git diff --name-only 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b origin/build/sdlc-fix-bug-triage` is empty
And the author has a valid member session with local `users.id` = `42`
And the request body is the exact source `skills/sdlc-fix-bug-triage/SKILL.md` at `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` with the exact line `EDIT-BUILD-FIXTURE` appended after the source file's final newline followed by a single newline
When the author sends `PUT https://builder.skillbuilder.internal/api/builds/17/files/SKILL.md` with `Content-Type: text/markdown` and that body
Then the builder responds with HTTP status 200
And the JSON response's `path` is `skills/sdlc-fix-bug-triage/SKILL.md`, its `branch` is `build/sdlc-fix-bug-triage` and its `commit_sha` equals `git rev-parse origin/build/sdlc-fix-bug-triage`
And `git diff --name-only 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b origin/build/sdlc-fix-bug-triage` returns exactly `skills/sdlc-fix-bug-triage/SKILL.md`
And the final line of `git show origin/build/sdlc-fix-bug-triage:skills/sdlc-fix-bug-triage/SKILL.md` is exactly `EDIT-BUILD-FIXTURE`
And `git ls-tree --name-only origin/build/sdlc-fix-bug-triage skills/` equals `git ls-tree --name-only 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b skills/`
And no path under `skills/` on `build/sdlc-fix-bug-triage` differs from `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` except paths under `skills/sdlc-fix-bug-triage/`

#### Scenario: Saving a new file creates it inside the existing skill folder
Given an edit build with `id` = `17` in state `open` exists on branch `build/sdlc-fix-bug-triage` cut from `main` head `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And the edit build was opened by BSB-20-PENDING-2, whose open commit changes no files
And no save has been made on that branch, so `git diff --name-only 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b origin/build/sdlc-fix-bug-triage` is empty
And the author has a valid member session with local `users.id` = `42`
And no file `skills/sdlc-fix-bug-triage/references/recheck-rubric.md` exists on that branch
When the author sends `PUT https://builder.skillbuilder.internal/api/builds/17/files/references/recheck-rubric.md` with `Content-Type: text/markdown` and a body of exactly 17 bytes: the ASCII text `# Recheck rubric` followed by a single newline
Then the builder responds with HTTP status 200
And the JSON response's `path` is `skills/sdlc-fix-bug-triage/references/recheck-rubric.md`
And `git diff --name-only 4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b origin/build/sdlc-fix-bug-triage` returns exactly `skills/sdlc-fix-bug-triage/references/recheck-rubric.md`
And `git show origin/build/sdlc-fix-bug-triage:skills/sdlc-fix-bug-triage/references/recheck-rubric.md` is exactly the byte string `# Recheck rubric` followed by a single newline
And `git ls-tree -r --name-only origin/build/sdlc-fix-bug-triage -- skills/sdlc-fix-bug-recheck` returns no paths

#### Scenario: A save cannot create or change a second skill folder
Given an edit build with `id` = `17` in state `open` exists on branch `build/sdlc-fix-bug-triage`
And the branch head is captured as `git rev-parse origin/build/sdlc-fix-bug-triage`
And the author has a valid member session with local `users.id` = `42`
When the author sends the raw, unnormalised `PUT` path `https://builder.skillbuilder.internal/api/builds/17/files/../sdlc-fix-bug-recheck/SKILL.md` with `Content-Type: text/markdown` and body exactly `# Hijacked skill`
Then the builder responds with HTTP status 403
And the response body is exactly `{"error":{"code":"file_outside_skill_folder","message":"A build can only change files under skills/sdlc-fix-bug-triage/."}}`
And `git rev-parse origin/build/sdlc-fix-bug-triage` still equals the captured branch head
And `git ls-tree -r --name-only origin/build/sdlc-fix-bug-triage -- skills/sdlc-fix-bug-recheck` returns no paths

### Covered requirements (traceability)
- FR-125

### Out of scope
The editor interface, the save-to-commit mechanics, recording the build head and clearing readiness
(epic BSB-21, FR-018 to FR-022, FR-127 and FR-162) — this story fixes the edit build's target
folder, not how a save is implemented; opening the edit build (story BSB-20-PENDING-2) and
creating or cloning builds (story BSB-20-PENDING-1 and epic BSB-19); renaming, moving or deleting a
skill folder; opening the catalog pull request (epic BSB-36).

### Notes / dependencies
- Cannot be accepted before BSB-21's save story (FR-162) is delivered; BSB-21 owns the
  `PUT /api/builds/{id}/files/{path}` contract.
- Depends on BSB-20-PENDING-2 for the edit build and its recorded target folder, and on epic BSB-18
  for the member session and local `users.id` = `42`.
- Depends on epic BSB-21 for the save endpoint (FR-127 and FR-162). The `PUT` request and `200`
  response in the scenarios are the minimal path contract this story needs; BSB-21's save service
  writes to the target folder this story fixes, and owns head recording and readiness invalidation.
- The target folder is fixed when the edit build is opened (story BSB-20-PENDING-2) from the
  resolved `main` head. A save never changes the target: every path it writes resolves inside
  `skills/sdlc-fix-bug-triage/`.
- A path that resolves outside the target folder — including a `..` segment — is refused before a
  commit is created, so the branch head and the set of skill folders on the branch stay unchanged.
- `git diff --name-only` between the `main` head and the build branch is the evidence that the edit
  build changed the existing skill folder and did not create a second one.
