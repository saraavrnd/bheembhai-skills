# Stories — BSB-42 (Skill editing, build state & readiness tracking)

Epic BSB-42 covers FR-018, FR-019, FR-020, FR-021, FR-022, FR-127 and FR-162. It is decomposed
into the 2 stories below; every one of those 7 requirements is covered by at least one story's
acceptance criteria.

**Prerequisite: build and branch (FA-2A / FA-2B).** BSB-40 "Build creation & skill scaffolding"
owns the build entity (owner, name, branch, base SHA, build kind, state), the branch cut from
`main`, and `POST /api/builds`. BSB-41 "Cloning & edit builds" owns the `edit` build kind that
targets an existing skill folder. This epic extends an existing build on
`build/<skill-name>` with file editing, save-to-commit, head tracking and the build page's
head/readiness surfaces; it does not create a build, a branch or a skill folder. BSB-40 owns the
build entity, `POST /api/builds` and the build list `GET /api/builds`; this epic adds the save
endpoint `PUT /api/builds/{build_id}/files/{path}` and the build-page read model
`GET /api/builds/{build_id}` used by the build page.

**Durable systems of record.** Skill content lives in the catalog git repository
`bheembhai-skills`: the build branch `build/<skill-name>` and its commits are the durable record
of what the author saved. Builder state lives in the builder database
`postgres://builder-db:5432/skillbuilder`; its `builds` row carries `head_sha` and `ready_sha` as
separate columns (SK-001 §9, and SK-001 §1b's rule that a new commit clears Ready). The
acceptance criteria assert the git commit, tree and blob state and the `builds` row — never a
mock, temporary copy or in-memory response alone.

**Fixture catalog and build.** Every scenario starts from a fresh fixture copy of the catalog
repository whose `main` is commit `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and whose `skills/`
contains `sdlc-research-summarise`, `sdlc-release-notes` and `sdlc-legacy-notes`. This is the
fixture BSB-41 defines. The build used by every scenario is:

| `builds` column | Value |
|----------------|-------|
| `id` | `bld_4nT8rW2yLc` |
| `skill` | `sdlc-research-summarise` |
| `kind` | `edit` |
| `cloned_from` | NULL |
| `branch` | `build/sdlc-research-summarise` |
| `created_by` | the `users.id` row for subject `sub-12345` (alice) |
| `head_sha` | `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` |
| `ready_sha` | NULL |
| `pr_url` | NULL |
| `state` | `open` |

`build/sdlc-research-summarise` is an edit build cut from the recorded head of `main`
(BSB-41-PENDING-2), so before any save its head equals `main`:
`git rev-parse build/sdlc-research-summarise` is
`4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`. The signed-in author is `alice@example.test`
(`sub-12345`, group `skill-builders`) carrying the `builder_session` cookie BSB-39 issues; FA-1
owns sign-in and the route guard.

`skills/sdlc-research-summarise/` contains `SKILL.md` (below), `verify.yaml`,
`references/README.md`, `references/corpus.txt` (4,194,304 bytes of the byte `a`),
`templates/brief.md`, `examples/example-brief.md` and `assets/diagram.png` (a fixed 2,048-byte
binary file). `skills/sdlc-release-notes/` and `skills/sdlc-legacy-notes/` each contain
`SKILL.md` and `verify.yaml`.

`main:skills/sdlc-research-summarise/SKILL.md` (followed by exactly one trailing newline):

```markdown
---
# skill metadata (kept verbatim)
name: "sdlc-research-summarise"  # catalog skill name
description: >-
  Summarise research sources into a short, cited brief.
compatibility: claude-code
model: sonnet
---
# Research summarise

## Steps
1. Read every supplied source.
2. Write a brief no longer than 400 words.
```

**Edited SKILL.md fixture.** The block above with the single body line `# Research summarise`
replaced by `# Research summarise (edited)`, everything else byte-identical, followed by exactly
one trailing newline. Scenarios refer to this block as "the Edited SKILL.md".

**Fixture build-head commit `D`.** A commit on `build/sdlc-research-summarise` whose parent is
`4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, whose tree equals that parent's tree except
`skills/sdlc-research-summarise/SKILL.md` is replaced byte-for-byte by the Edited SKILL.md. Its
author and committer are both `Fixture <fixture@example.test>`, its author and committer dates
are both `2026-11-16T10:00:00+00:00`, and its message is exactly `fixture: advance build head`.
Its SHA is read at test time as `D=$(git rev-parse build/sdlc-research-summarise)`; no scenario
asserts a literal SHA for `D`.

**Save contract.** A save is
`PUT /api/builds/{build_id}/files/{path}` where `{path}` is the file's path relative to the
build's skill folder, percent-encoded as one URL path segment (for example
`references%2FREADME.md` decodes to `references/README.md`). The builder resolves the path
against `skills/<build.skill>/` on the build branch `build/<build.skill>`. The request is
`Content-Type: application/json` with:

- `content` — the file content;
- `encoding` — `utf-8` (the default when omitted) or `base64`;
- `base_sha` — the 40-hex head SHA the author loaded before editing.

A save that creates a commit responds HTTP 200 with a JSON body carrying `build_id`, `path`,
`commit_sha` (40 hex), `head_sha` (equal to `commit_sha`) and `changed` (`true`). The commit's
parent is the previous head and its only tree change is
`skills/<build.skill>/<path>`. The same operation updates `builds.head_sha` to the new commit
SHA and clears `builds.ready_sha` to NULL (FR-022). A save whose decoded content is byte-identical to the current blob responds HTTP 200 with
`changed` `false`, `commit_sha` `null` and `head_sha` unchanged, and creates no commit.
Rejections are:

| Situation | Response |
|-----------|----------|
| `base_sha` is not the current head | HTTP 409, a JSON body whose `error` is `stale_head`, `expected_sha` is the submitted `base_sha` and `current_sha` is the current head |
| decoded path escapes the skill folder (any `..` segment or an absolute path) | HTTP 422, a JSON body whose `error` is `invalid_path` and `path` is the decoded path |
| the path does not exist on the build branch | HTTP 404, a JSON body whose `error` is `file_not_found` and `path` is the decoded path |
| the commit cannot be created | HTTP 500 and the exact body `{"error":"commit_failed"}` |

Every rejection leaves the branch ref, `builds.head_sha` and `builds.ready_sha` unchanged.

**Build-page read contract.** `GET /api/builds/{build_id}` (authenticated) responds HTTP 200
with JSON carrying `build_id`, `skill_name`, `branch`, `head_sha`, `ready_sha`, `ready` and
`state`. `ready` is `true` exactly when `ready_sha` is non-null and equals `head_sha`; it is
`false` otherwise. `GET /builds/{build_id}` (authenticated) returns the server-rendered build
page whose HTML contains an element with `data-testid="build-head-sha"` whose text is exactly
`head_sha`, an element with `data-testid="build-readiness"` whose text is exactly `Ready` when
`ready` is true and exactly `Not ready` otherwise, and an element with
`data-testid="build-ready-sha"` whose text is `ready_sha` when non-null and empty when null. The
page therefore shows a Ready status only for the exact head SHA, never for a different SHA.
`ready_sha` is written by FA-10B (BSB-51) when all four readiness checks hold at a SHA; this
epic owns persisting, displaying and clearing it, not computing the checks. Scenarios that need
a Ready build set `builds.ready_sha` directly in the builder database, which is the durable
record FA-10B writes.

## Coverage summary

| Story | Requirements covered |
|-------|----------------------|
| BSB-42-PENDING-1 — Edit and save a file in the build's skill folder | FR-018, FR-019, FR-127, FR-162 |
| BSB-42-PENDING-2 — Show the build head and readiness, and clear readiness when the head moves | FR-020, FR-021, FR-022 |

> **Input note.** The epic was fetched as Jira issue `BSB-42` through the configured Atlassian MCP
> server (summary, description, functional scope, edge cases, implementation guidance, Definition
> of Done and covered requirements). The run's placeholder work item `SkillBuilder-2` does not
> exist on that site: the MCP `jira_get_issue` call rejects the key because it does not match the
> server's `^[A-Z][A-Z0-9_]+-\d+(?:-\d+)*$` pattern, a JQL text search returns no issue, and a
> direct read-only REST fetch returns HTTP 404. This matches `docs/product/PRD.md` §8 and
> `docs/product/epics.md`; the placeholder work item contributes no scope here.

---

## STORY: BSB-42-PENDING-1

**Title:** Edit and save a file in the build's skill folder, committing it and recording the build head
**Epic:** BSB-42 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-3, MVP

### Story
As a **skill author**, I want **to edit and save a file in my build's skill folder**, so that **my change becomes a commit on the build branch and the build's head is the exact content I saved**.

### Acceptance Criteria
Scenario: Save an edited file creates one commit and advances the build head
Given the fixture build `bld_4nT8rW2yLc` on `build/sdlc-research-summarise` at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, whose `skills/sdlc-research-summarise/SKILL.md` is the fixture `SKILL.md`
When the signed-in author alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/SKILL.md` with a JSON body whose `content` is the Edited SKILL.md byte-for-byte, `encoding` is `utf-8`, and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
Then the builder responds with HTTP 200 and a JSON body whose `build_id` is `bld_4nT8rW2yLc`, `path` is `SKILL.md`, `commit_sha` matches `^[0-9a-f]{40}$` and equals `head_sha`, and `changed` is `true`; `git rev-parse build/sdlc-research-summarise` equals that `commit_sha`, `git rev-parse build/sdlc-research-summarise^` equals `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `git show --name-status --format= build/sdlc-research-summarise` lists exactly `M skills/sdlc-research-summarise/SKILL.md`, `git show build/sdlc-research-summarise:skills/sdlc-research-summarise/SKILL.md` is byte-identical to the Edited SKILL.md, and the `builds` row with `id` `bld_4nT8rW2yLc` has `head_sha` equal to that `commit_sha`

Scenario: Save a large binary file stored byte-for-byte
Given the fixture build at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `skills/sdlc-research-summarise/assets/diagram.png` is the fixture 2,048-byte binary file
When alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/assets%2Fdiagram.png` with a JSON body whose `content` is the base64 encoding of the exact 4,194,304 bytes formed by repeating the byte sequence 0x00,0x01,…,0xFF 16,384 times, `encoding` is `base64`, and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
Then the builder responds with HTTP 200, `changed` is `true`, `git cat-file -s build/sdlc-research-summarise:skills/sdlc-research-summarise/assets/diagram.png` is `4194304`, the committed blob's SHA equals `git hash-object --stdin` computed over those exact 4,194,304 bytes, `git show --name-status --format= build/sdlc-research-summarise` lists exactly `M skills/sdlc-research-summarise/assets/diagram.png`, and `builds.head_sha` for `bld_4nT8rW2yLc` equals the response's `commit_sha`

Scenario: Save of unchanged content creates no commit
Given the fixture build at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` whose `SKILL.md` blob is `BLOB=$(git rev-parse build/sdlc-research-summarise:skills/sdlc-research-summarise/SKILL.md)` and `COUNT=$(git rev-list --count build/sdlc-research-summarise)`
When alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/SKILL.md` with a JSON body whose `content` is the fixture `SKILL.md` byte-for-byte, `encoding` is `utf-8`, and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
Then the builder responds with HTTP 200 and a JSON body whose `changed` is `false`, `commit_sha` is `null` and `head_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`; `git rev-list --count build/sdlc-research-summarise` is still `COUNT`, `git rev-parse build/sdlc-research-summarise:skills/sdlc-research-summarise/SKILL.md` is still `BLOB`, and `builds.head_sha` for `bld_4nT8rW2yLc` is still `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`

Scenario: Save to a path outside the skill folder rejected
Given the fixture build at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
When alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/..%2Fsdlc-release-notes%2FSKILL.md` with body `{"content":"# Release notes (edited)","encoding":"utf-8","base_sha":"4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_path","path":"../sdlc-release-notes/SKILL.md"}`, `git rev-parse build/sdlc-research-summarise` is still `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `builds.head_sha` for `bld_4nT8rW2yLc` is still `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, and `git rev-list --count build/sdlc-research-summarise` is unchanged

Scenario: Save to a file absent from the build branch rejected
Given the fixture build at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, where `skills/sdlc-research-summarise/references/missing.md` does not exist
When alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/references%2Fmissing.md` with body `{"content":"# Missing","encoding":"utf-8","base_sha":"4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c"}`
Then the builder responds with HTTP 404 and body exactly `{"error":"file_not_found","path":"references/missing.md"}`, `git rev-parse build/sdlc-research-summarise` is still `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `builds.head_sha` for `bld_4nT8rW2yLc` is still `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, and `git rev-list --count build/sdlc-research-summarise` is unchanged

Scenario: Two saves racing on one file produce one commit and one conflict
Given the fixture build at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, content `A` equal to the Edited SKILL.md, and content `B` equal to the fixture `SKILL.md` with its body line `# Research summarise` replaced by `# Research summarise (race winner B)`
When alice issues `PUT /api/builds/bld_4nT8rW2yLc/files/SKILL.md` twice concurrently, once with a JSON body whose `content` is `A`, `encoding` is `utf-8` and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, and once with a JSON body whose `content` is `B`, `encoding` is `utf-8` and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
Then exactly one request responds with HTTP 200 and `changed` `true`, the other responds with HTTP 409 and a JSON body whose `error` is exactly `stale_head`, `expected_sha` is exactly `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `current_sha` equals the 200 response's `commit_sha`, `git rev-list --count 4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c..build/sdlc-research-summarise` is `1`, `git rev-parse build/sdlc-research-summarise` equals the 200 response's `commit_sha`, the committed `SKILL.md` is byte-identical to exactly one of `A` or `B` and matches the request that received the 200, and `builds.head_sha` for `bld_4nT8rW2yLc` equals that `commit_sha`

Scenario: Commit failure leaves the previous head intact
Given the fixture build at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and the fixture repository's `pre-commit` hook is installed to exit with status `1` without printing a diff
When alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/SKILL.md` with a JSON body whose `content` is the Edited SKILL.md byte-for-byte, `encoding` is `utf-8`, and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
Then the builder responds with HTTP 500 and body exactly `{"error":"commit_failed"}`, `git rev-parse build/sdlc-research-summarise` is still `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `git rev-list --count build/sdlc-research-summarise` is unchanged, `builds.head_sha` for `bld_4nT8rW2yLc` is still `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, and `git show build/sdlc-research-summarise:skills/sdlc-research-summarise/SKILL.md` still has a line equal to `# Research summarise` and no line equal to `# Research summarise (edited)`

### Covered requirements
- FR-018
- FR-019
- FR-127
- FR-162

### Out of scope
Creating builds, build branches or skill folders (FA-2A / BSB-40 and FA-2B / BSB-41); the readiness checks and the Ready computation (FA-10B / BSB-51); the build page (BSB-42-PENDING-2); running, scanning, packaging or submitting a build (later epics); saving from a build whose pull request is already open, beyond the generic commit-clears-readiness rule (FR-114 is BSB-54's); renaming, deleting or merging files; any file-size limit (none is required) and any content validation beyond the declared `utf-8`/`base64` encoding; direct git edits by the author.

### Notes / dependencies
Depends on FA-2A (BSB-40) for the build entity, the `build/` branch cut from `main` and the build list, and on FA-2B (BSB-41) for the `edit` build kind and its existing skill folder; the catalog repository is the external prerequisite that supplies `main` and the skill. This save action is the save that BSB-41-PENDING-2's "An edit changes the existing folder in place" scenario depends on (FR-018): the edit build owns the target path, this story owns writing, committing and recording the head. FA-10B (BSB-51) writes `builds.ready_sha`; BSB-42-PENDING-2 owns clearing it when a save creates a commit. FR-114 (BSB-54) reuses this same save path for a submitted build, so the save must not depend on `state` being `open`. The commit on `build/<skill-name>` is the durable record; the `builds.head_sha` update and the commit must succeed or fail together.

---

## STORY: BSB-42-PENDING-2

**Title:** Show the build's current head SHA and readiness status, and clear readiness when the head moves
**Epic:** BSB-42 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-3, MVP

### Story
As a **skill author**, I want **the build page to show the current head SHA and whether the build is Ready at that exact SHA**, so that **"Ready" never describes code I have already changed**.

### Acceptance Criteria
Scenario: Build page shows the current head SHA
Given the fixture build `bld_4nT8rW2yLc` has `builds.head_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `git rev-parse build/sdlc-research-summarise` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
When alice requests `GET /api/builds/bld_4nT8rW2yLc` and `GET /builds/bld_4nT8rW2yLc` with her `builder_session` cookie
Then `GET /api/builds/bld_4nT8rW2yLc` responds with HTTP 200 and a JSON body whose `build_id` is `bld_4nT8rW2yLc`, `skill_name` is `sdlc-research-summarise`, `branch` is `build/sdlc-research-summarise` and `head_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`; `GET /builds/bld_4nT8rW2yLc` responds with HTTP 200 and its HTML contains an element with `data-testid="build-head-sha"` whose text is exactly `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`

Scenario: Build page shows Ready only when the ready SHA equals the head SHA
Given the fixture build has `builds.head_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and its `builds.ready_sha` is set to `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` (the FA-10B record that all four readiness checks hold at that SHA)
When alice requests `GET /api/builds/bld_4nT8rW2yLc` and `GET /builds/bld_4nT8rW2yLc` with her `builder_session` cookie
Then the API responds with HTTP 200, `head_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `ready_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `ready` `true`, and the page's element with `data-testid="build-readiness"` has text exactly `Ready` and its element with `data-testid="build-ready-sha"` has text exactly `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`

Scenario: Build page shows Not ready when no ready SHA is recorded
Given the fixture build has `builds.head_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `builds.ready_sha` is NULL
When alice requests `GET /api/builds/bld_4nT8rW2yLc` and `GET /builds/bld_4nT8rW2yLc` with her `builder_session` cookie
Then the API responds with HTTP 200, `head_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `ready_sha` `null` and `ready` `false`, and the page's element with `data-testid="build-readiness"` has text exactly `Not ready` and its element with `data-testid="build-ready-sha"` has empty text

Scenario: Build page shows Not ready when the recorded ready SHA is not the head SHA
Given `build/sdlc-research-summarise` head is fixture build-head commit `D`, the `builds` row has `head_sha` equal to `D` and `ready_sha` set to `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` (a readiness record for the previous head)
When alice requests `GET /api/builds/bld_4nT8rW2yLc` and `GET /builds/bld_4nT8rW2yLc` with her `builder_session` cookie
Then the API responds with HTTP 200, `head_sha` equal to `D`, `ready_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `ready` `false`, and the page's element with `data-testid="build-readiness"` has text exactly `Not ready` and its element with `data-testid="build-ready-sha"` has text exactly `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`

Scenario: A save that creates a commit clears the previously recorded ready SHA
Given the fixture build has `builds.head_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `builds.ready_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
When alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/SKILL.md` with a JSON body whose `content` is the Edited SKILL.md byte-for-byte, `encoding` is `utf-8`, and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, and the request succeeds with `commit_sha` `H2`
Then the `builds` row with `id` `bld_4nT8rW2yLc` has `head_sha` equal to `H2` and `ready_sha` `NULL`; `GET /api/builds/bld_4nT8rW2yLc` responds with HTTP 200 and `head_sha` `H2`, `ready_sha` `null` and `ready` `false`; `GET /builds/bld_4nT8rW2yLc` shows text exactly `H2` in its `data-testid="build-head-sha"` element, text exactly `Not ready` in its `data-testid="build-readiness"` element, and empty text in its `data-testid="build-ready-sha"` element; and `git rev-parse build/sdlc-research-summarise` equals `H2`

Scenario: A no-op save does not clear the ready SHA
Given the fixture build has `builds.head_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `builds.ready_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
When alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/SKILL.md` with a JSON body whose `content` is byte-identical to the current `SKILL.md`, `encoding` is `utf-8`, and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
Then the save responds with HTTP 200 and `changed` `false`, the `builds` row still has `head_sha` and `ready_sha` both equal to `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `GET /api/builds/bld_4nT8rW2yLc` returns `ready` `true`, and the page's `data-testid="build-readiness"` element has text exactly `Ready`

Scenario: A failed commit does not clear the ready SHA
Given the fixture build has `builds.head_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `builds.ready_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, and the fixture repository's `pre-commit` hook exits with status `1`
When alice submits `PUT /api/builds/bld_4nT8rW2yLc/files/SKILL.md` with a JSON body whose `content` is the Edited SKILL.md byte-for-byte, `encoding` is `utf-8`, and `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
Then the request responds with HTTP 500 and body exactly `{"error":"commit_failed"}`, the `builds` row still has `head_sha` and `ready_sha` both equal to `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `GET /api/builds/bld_4nT8rW2yLc` returns `ready` `true`, and the page's `data-testid="build-readiness"` element has text exactly `Ready`

### Covered requirements
- FR-020
- FR-021
- FR-022

### Out of scope
Computing or displaying the four individual readiness checks (FR-068–FR-070, owned by FA-10B / BSB-51); the Submit to catalog gate and the submitted-build save rule (FR-107 and FR-114, owned by FA-15 / BSB-54); the save/commit implementation itself except as exercised here (BSB-42-PENDING-1); build state transitions (FR-113); the build list page; formal accessibility criteria (FA-17) — the status is rendered as text, never by colour alone.

### Notes / dependencies
Depends on BSB-42-PENDING-1 for the save action: the same operation that creates a commit must clear `builds.ready_sha` in the same transaction, and this story owns that rule (FR-022) and its page assertions. Depends on FA-10B (BSB-51) for writing `builds.ready_sha` when all four checks hold at a SHA, and on FA-15 (BSB-54) for reading the Ready status and for FR-114's submitted-build variant. The `ready` boolean is derived on read (`ready_sha` equals `head_sha`) and is never stored, so a stale non-null `ready_sha` cannot make the page show Ready. The build-page contract here is the base BSB-51 extends with the four per-check rows; it applies to create, clone and edit builds alike because all three kinds use the same `builds` row and build branch.
