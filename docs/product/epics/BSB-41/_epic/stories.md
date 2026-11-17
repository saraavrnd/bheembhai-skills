# Stories — BSB-41 (Cloning & edit builds)

Epic BSB-41 covers FR-011, FR-012, FR-013, FR-014, FR-124, FR-125 and FR-126. It is decomposed
into the 2 stories below; every one of those 7 requirements is covered by at least one story's
acceptance criteria.

**Prerequisite: build creation and name rules (FA-2A).** FA-2A — epic BSB-40 "Build creation &
skill scaffolding" — owns the build entity (owner, name, branch, base SHA, build kind, state),
the branch creation from the recorded head of `main`, and skill-name validation
(FR-006–FR-010, FR-015–FR-017). This epic extends the build-creation endpoint `POST /api/builds`
with `"build_kind":"clone"` and `"build_kind":"edit"`, and the build list `GET /api/builds` used to observe an
accepted or rejected build; `"build_kind":"create"` and the name rules (including
case-insensitive collisions, the on-main and open-build checks, and the `sdlc-` prefix, area
segment and action segment pattern) are FA-2A's and are not restated here. Both stories below
depend on FA-2A for the build entity and for the build branch (`build/` followed by the skill
name) being cut from `main`.

**Durable system of record.** Skill files live in the catalog git repository
`bheembhai-skills`; a build is a `build/` branch named after its skill, cut from `main` (SK-001 §1a), and the
branch plus its commits are the durable record of what the build will submit. The builder's build
list `GET /api/builds` is where an accepted or rejected build is observed. The acceptance criteria
therefore assert git tree, blob and commit state (never a mock or temporary copy) and the build
list, not an in-memory response alone.

**Fixture catalog.** Every scenario starts from a fresh fixture copy of the catalog repository
whose `main` is commit `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and whose `skills/` contains
exactly three skill folders: `sdlc-legacy-notes`, `sdlc-release-notes` and
`sdlc-research-summarise`. The folders `sdlc-research-digest`, `sdlc-release-digest` and
`sdlc-missing-skill` do not exist on `main`.

| Fixture skill | Contents on `main` |
|---------------|--------------------|
| `skills/sdlc-research-summarise/` | `SKILL.md` (below), `verify.yaml`, `references/README.md`, `references/corpus.txt` (4,194,304 bytes of the byte `a`), `templates/brief.md`, `examples/example-brief.md`, `assets/diagram.png` (2,048-byte PNG with a fixed byte pattern) |
| `skills/sdlc-release-notes/` | `SKILL.md` (below), `verify.yaml`, `references/README.md` |
| `skills/sdlc-legacy-notes/` | `SKILL.md` (below), `verify.yaml` |

`main:skills/sdlc-research-summarise/SKILL.md`:

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

`main:skills/sdlc-release-notes/SKILL.md`:

```markdown
---
name: 'sdlc-release-notes'
description: Draft release notes from merged changes.
compatibility: claude-code
model: sonnet
---
# Release notes
```

`main:skills/sdlc-legacy-notes/SKILL.md`:

```markdown
---
description: Legacy notes skill with no name key.
compatibility: claude-code
model: sonnet
---
# Legacy notes
```

**Frontmatter name rewrite rule.** A clone changes exactly one line of the copied `SKILL.md`: the
value of the top-level `name` key becomes the new skill name, keeping that line's quoting style
(double quotes stay double quotes, single quotes stay single quotes) and any trailing `#` comment.
Every other line of `SKILL.md` — including every other frontmatter line and every comment — and
every other file in the folder are copied byte-for-byte from the source blob. Thus cloning
`sdlc-research-summarise` to `sdlc-research-digest` changes
`name: "sdlc-research-summarise"  # catalog skill name` to
`name: "sdlc-research-digest"  # catalog skill name`, and cloning `sdlc-release-notes` to
`sdlc-release-digest` changes `name: 'sdlc-release-notes'` to `name: 'sdlc-release-digest'`.
Because the `SKILL.md` file therefore changes, a cloned `SKILL.md` blob's SHA differs from its
source blob's SHA; blob SHAs are asserted equal only for every other file in the folder.

**Fixture change commit `C`.** Scenarios that need `main` to move create exactly one commit `C`
on top of `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and read its SHA at test time as
`C=$(git rev-parse main)`; no scenario asserts a literal SHA for `C`. `C` has parent
`4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, its tree equals that commit's tree except that
`skills/sdlc-research-summarise/SKILL.md` is replaced byte-for-byte by the block below followed by
exactly one trailing newline. Its author and committer are both
`Fixture <fixture@example.test>`, its author and committer dates are both
`2026-11-16T09:00:00+00:00`, and its message is exactly `fixture: change research summarise`.

```markdown
---
name: "sdlc-research-summarise"
description: >-
  Summarise research sources into a short, cited brief.
compatibility: claude-code
model: sonnet
---
# Research summarise (changed on main)
```

**Build-creation contract used by these stories.** The author is a signed-in current member of
the `skill-builders` group (FA-1 owns sign-in and the guard). Build creation is
`POST /api/builds` with `Content-Type: application/json`; a successful clone or edit responds
HTTP 201 with a JSON body carrying `build_id` (matching `^bld_[0-9A-Za-z]{10}$`), `build_kind`,
`skill_name`, `skill_path`, `branch`, `base_sha` and `head_sha`. A clone body also carries
`source_skill`. Rejections carry no `Set-Cookie` change and no build entry.

## Coverage summary

| Story | Requirements covered |
|-------|----------------------|
| BSB-41-PENDING-1 — Clone a catalog skill under a new name | FR-011, FR-012, FR-013, FR-014 |
| BSB-41-PENDING-2 — Open an existing catalog skill in an edit build | FR-124, FR-125, FR-126 |

> **Input note.** The epic was fetched as Jira issue `BSB-41` from the configured Atlassian site
> (summary, description, functional scope, edge cases, implementation guidance, Definition of
> Done and covered requirements). The run's placeholder work item `SkillBuilder-2` does not exist
> on that site, as recorded in `docs/product/PRD.md` §8, so it contributes no scope here.

---

## STORY: BSB-41-PENDING-1

**Title:** Clone a catalog skill under a new name, copying every file and rewriting only the frontmatter name
**Epic:** BSB-41 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **to clone an existing catalog skill under a new name**, so that **I can start from a working skill without altering the catalog's original**.

### Acceptance Criteria
Scenario: Clone an existing catalog skill
Given the fixture catalog at `main` commit `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and a signed-in skill author with no open build named `sdlc-research-digest`
When the author submits `{"build_kind":"clone","source_skill":"sdlc-research-summarise","name":"sdlc-research-digest","description":"Digest research sources for a weekly brief"}` to `POST /api/builds`
Then the builder responds with HTTP 201 and a JSON body whose `build_kind` is `clone`, `skill_name` is `sdlc-research-digest`, `source_skill` is `sdlc-research-summarise`, `skill_path` is `skills/sdlc-research-digest`, `branch` is `build/sdlc-research-digest`, `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `build_id` matches `^bld_[0-9A-Za-z]{10}$`, and `git rev-parse build/sdlc-research-digest` equals the response's `head_sha`, that value matches `^[0-9a-f]{40}$`, and `git rev-parse build/sdlc-research-digest^` equals `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`

Scenario: Whole skill folder copied, with only the SKILL.md name line rewritten
Given the clone build `build/sdlc-research-digest` created from `sdlc-research-summarise`
When `git ls-tree -r --name-only build/sdlc-research-digest skills/sdlc-research-digest/` is compared with `git ls-tree -r --name-only main skills/sdlc-research-summarise/` after stripping the `skills/sdlc-research-digest/` and `skills/sdlc-research-summarise/` prefixes
Then both list exactly the 7 relative paths `SKILL.md`, `assets/diagram.png`, `examples/example-brief.md`, `references/README.md`, `references/corpus.txt`, `templates/brief.md` and `verify.yaml`; for each of the 6 relative paths other than `SKILL.md` the cloned blob's SHA equals the source blob's SHA, so the 4,194,304-byte `references/corpus.txt` and the binary `assets/diagram.png` are copied without truncation or re-encoding; and for `SKILL.md` the clone's blob differs from the source blob in exactly one line, the frontmatter `name:` line, whose value is `sdlc-research-digest` (so the cloned `SKILL.md` blob's SHA is not equal to the source `SKILL.md` blob's SHA)

Scenario: Frontmatter name rewritten and everything else preserved
Given the fixture sources `sdlc-research-summarise` (comments, a double-quoted name and a block scalar) and `sdlc-release-notes` (a single-quoted name and no comments)
When the author clones `sdlc-research-summarise` to `sdlc-research-digest` and `sdlc-release-notes` to `sdlc-release-digest` through `POST /api/builds` with bodies `{"build_kind":"clone","source_skill":"sdlc-research-summarise","name":"sdlc-research-digest","description":"Digest research sources for a weekly brief"}` and `{"build_kind":"clone","source_skill":"sdlc-release-notes","name":"sdlc-release-digest","description":"Draft release notes for the weekly release"}`
Then each cloned `SKILL.md` parses to `name` equal to its new skill name, each source's other frontmatter values (`description`, `compatibility`, `model`) and body after the closing `---` are byte-identical in the clone, the `# skill metadata (kept verbatim)` and `# catalog skill name` comments survive in the `sdlc-research-digest` clone, and the `name:` line is the only differing line in each pair — in the `sdlc-research-digest` clone `name: "sdlc-research-summarise"  # catalog skill name` is replaced by `name: "sdlc-research-digest"  # catalog skill name`, and in the `sdlc-release-digest` clone `name: 'sdlc-release-notes'` is replaced by `name: 'sdlc-release-digest'`

Scenario: Source skill left unchanged
Given the source tree SHA is captured as `git rev-parse main:skills/sdlc-research-summarise` before the clone
When the clone build `build/sdlc-research-digest` completes and `git diff --name-status main..build/sdlc-research-digest` is inspected
Then `git rev-parse main:skills/sdlc-research-summarise` still equals the captured SHA, every line of the diff starts with `A` and names a path under `skills/sdlc-research-digest/`, no diff line names `skills/sdlc-research-summarise/`, `git rev-parse main` still equals `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, and `git status --porcelain` on the fixture working tree is empty

Scenario: Clone copies the recorded base commit rather than the checkout working tree
Given a fresh fixture copy whose `main` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and whose working tree carries exactly one uncommitted edit replacing the line `# Research summarise` in `skills/sdlc-research-summarise/SKILL.md` with `# Research summarise (uncommitted local edit)`, so `git status --porcelain` is exactly ` M skills/sdlc-research-summarise/SKILL.md`
When the author submits `{"build_kind":"clone","source_skill":"sdlc-research-summarise","name":"sdlc-research-digest","description":"Digest research sources for a weekly brief"}` to `POST /api/builds`
Then the builder responds with HTTP 201 and `base_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, and `git show build/sdlc-research-digest:skills/sdlc-research-digest/SKILL.md` parses to `name` equal to `sdlc-research-digest`, has frontmatter values `description`, `compatibility` and `model` equal to those in `git show 4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c:skills/sdlc-research-summarise/SKILL.md`, and has a body after the closing `---` that is byte-identical to the body of that same `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` blob, so it contains the exact line `# Research summarise` and no line with the text `uncommitted local edit`

Scenario: A main move affects neither an existing clone build nor the base of the next clone
Given the clone build `build/sdlc-research-digest` was created from `main` at `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, with `HEAD_SHA=$(git rev-parse build/sdlc-research-digest)` and `CLONE_BLOB=$(git rev-parse build/sdlc-research-digest:skills/sdlc-research-digest/SKILL.md)` captured
When the test applies fixture change commit `C` to `main`, verifies `C=$(git rev-parse main)`, and submits `{"build_kind":"clone","source_skill":"sdlc-research-summarise","name":"sdlc-research-brief","description":"Summarise research sources into a short brief"}` to `POST /api/builds`
Then `git rev-parse build/sdlc-research-digest` still equals `HEAD_SHA`, `git rev-parse build/sdlc-research-digest:skills/sdlc-research-digest/SKILL.md` still equals `CLONE_BLOB` and that blob contains the exact line `# Research summarise` and no line with the text `changed on main`, `git diff --name-status main..build/sdlc-research-digest` has exactly one line starting with `M`, that line is `M skills/sdlc-research-summarise/SKILL.md`, and every line starting with `A` names a path under `skills/sdlc-research-digest/`, `GET /api/builds` still reports `base_sha` `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` for it, and the new build responds HTTP 201 with `base_sha` equal to `C`, `git rev-parse build/sdlc-research-brief^` equal to `C`, and `git show build/sdlc-research-brief:skills/sdlc-research-brief/SKILL.md` equal to `git show C:skills/sdlc-research-summarise/SKILL.md` with its single frontmatter line `name: "sdlc-research-summarise"` replaced by `name: "sdlc-research-brief"` (so the cloned `SKILL.md` blob's SHA at `skills/sdlc-research-brief/SKILL.md` is not equal to the source blob's SHA at `C:skills/sdlc-research-summarise/SKILL.md`)

Scenario: Clone of a source skill missing from main rejected
Given `main` contains no directory `skills/sdlc-does-not-exist/`
When the author submits `{"build_kind":"clone","source_skill":"sdlc-does-not-exist","name":"sdlc-research-digest","description":"Digest research sources for a weekly brief"}` to `POST /api/builds`
Then the builder responds with HTTP 404 and body exactly `{"error":"source_skill_not_found","skill_name":"sdlc-does-not-exist"}`, `git branch --list build/sdlc-research-digest` is empty, and `GET /api/builds` lists no build whose `branch` is `build/sdlc-research-digest`

Scenario: Clone of a source without a frontmatter name rejected
Given `main:skills/sdlc-legacy-notes/SKILL.md` has frontmatter with `description`, `compatibility` and `model` but no `name` key, and its tree SHA is captured as `git rev-parse main:skills/sdlc-legacy-notes`
When the author submits `{"build_kind":"clone","source_skill":"sdlc-legacy-notes","name":"sdlc-legacy-digest","description":"Digest legacy notes"}` to `POST /api/builds`
Then the builder responds with HTTP 422 and body exactly `{"error":"source_frontmatter_invalid","detail":"missing name"}`, `git branch --list build/sdlc-legacy-digest` is empty, `GET /api/builds` lists no build whose `branch` is `build/sdlc-legacy-digest`, and `git rev-parse main:skills/sdlc-legacy-notes` still equals the captured SHA

### Covered requirements
- FR-011
- FR-012
- FR-013
- FR-014

### Out of scope
Build creation from a new name and its scaffold (FA-2A / BSB-40); clone-name validation, on-main and open-build collision rules, and the `sdlc-` prefix, area segment and action segment pattern (FR-015–FR-017, owned by FA-2A); editing, running, scanning or submitting the cloned build (later epics); writing to the platform catalog or opening a pull request (FA-15 / BSB-54); changes to `main` itself.

### Notes / dependencies
Depends on FA-2A (BSB-40) for the build entity, the `build/` branch cut from `main`, and name validation. The catalog repository is the external prerequisite that supplies `main` and the source skills; the builder reads it from the checkout shared with the catalog (SK-001 §1a, §8). The clone build is the entry point FA-3 (BSB-42) tracks, FA-6 (BSB-45) packages and FA-15 (BSB-54) submits, so later epics rely on `build_kind` being `clone` and on the build branch containing only the new skill folder. The concurrent main-move scenario pins the clone to the recorded `base_sha`; the same rule is used by FA-2A's create branch. An open edit build of the same source is unaffected by a clone (BSB-41-PENDING-2).

---

## STORY: BSB-41-PENDING-2

**Title:** Open an existing catalog skill in an edit build
**Epic:** BSB-41 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **to open an existing catalog skill in an edit build**, so that **I can improve that catalog skill through the same build, run and submit path instead of creating a duplicate**.

### Acceptance Criteria
Scenario: Open an existing catalog skill in an edit build
Given the fixture catalog at `main` commit `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and a signed-in skill author with no open build for `sdlc-research-summarise`
When the author submits `{"build_kind":"edit","skill_name":"sdlc-research-summarise","description":"Tighten the summary"}` to `POST /api/builds`
Then the builder responds with HTTP 201 and a JSON body whose `build_kind` is `edit`, `skill_name` is `sdlc-research-summarise`, `skill_path` is `skills/sdlc-research-summarise`, `branch` is `build/sdlc-research-summarise`, `base_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `head_sha` is `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and `build_id` matches `^bld_[0-9A-Za-z]{10}$`, and `git rev-parse build/sdlc-research-summarise` equals `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`

Scenario: Edit build targets the existing skill folder, not a second folder
Given the edit build `build/sdlc-research-summarise` created from `main`
When `git ls-tree -d --name-only build/sdlc-research-summarise skills/` is compared with `git ls-tree -d --name-only main skills/`
Then both list exactly `skills/sdlc-legacy-notes`, `skills/sdlc-release-notes` and `skills/sdlc-research-summarise`, the edit branch contains no `skills/sdlc-research-summarise-edit` or any other added skill folder, and the build's `skill_path` in `GET /api/builds` is `skills/sdlc-research-summarise`

Scenario: An edit changes the existing folder in place
Given the edit build `build/sdlc-research-summarise` exists at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c` and the author edits `SKILL.md` on that build, replacing the line `# Research summarise` with `# Research summarise (tightened)`
When the author saves the change through the build's save action and that save creates a commit on `build/sdlc-research-summarise`
Then the build head advances by exactly one commit and `git show --name-status --format= build/sdlc-research-summarise` lists exactly `M skills/sdlc-research-summarise/SKILL.md`, `git diff --name-status main..build/sdlc-research-summarise` contains no line starting with `A` under `skills/`, and `git ls-tree -d --name-only build/sdlc-research-summarise skills/` still lists exactly the same three skill folders as `main`

Scenario: Edit build for a skill absent from main rejected
Given `main` contains no directory `skills/sdlc-missing-skill/`
When the author submits `{"build_kind":"edit","skill_name":"sdlc-missing-skill","description":"Fix the missing skill"}` to `POST /api/builds`
Then the builder responds with HTTP 404 and body exactly `{"error":"skill_not_found_on_main","skill_name":"sdlc-missing-skill"}`, `git branch --list build/sdlc-missing-skill` is empty, `GET /api/builds` lists no build whose `branch` is `build/sdlc-missing-skill`, and `git rev-parse main` still equals `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`

Scenario: A concurrent clone of the same skill leaves the edit build untouched
Given the edit build `build/sdlc-research-summarise` is open at head `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
When the author submits `{"build_kind":"clone","source_skill":"sdlc-research-summarise","name":"sdlc-research-digest","description":"Digest research sources for a weekly brief"}` to `POST /api/builds`
Then the edit build's branch head is still `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, `git diff --name-status build/sdlc-research-summarise..build/sdlc-research-digest` contains only lines starting with `A` under `skills/sdlc-research-digest/`, and `GET /api/builds` returns both builds with distinct `branch` values `build/sdlc-research-summarise` and `build/sdlc-research-digest`

### Covered requirements
- FR-124
- FR-125
- FR-126

### Out of scope
Build creation from a new name and its scaffold (FA-2A / BSB-40); clone-name validation, the open-build collision rule and the `sdlc-` prefix, area segment and action segment pattern (FR-015–FR-017, owned by FA-2A); the file-editing and save implementation (FR-018–FR-022, owned by FA-3 / BSB-42); running, scanning or submitting the edit build (later epics); merging the build branch or writing to the platform catalog (FA-15 / BSB-54); changing the skill's name, which an edit build cannot do.

### Notes / dependencies
Depends on FA-2A (BSB-40) for the build entity and branch creation, and on FA-3 (BSB-42) only for the save action that produces the commit in "An edit changes the existing folder in place" (FR-018); this epic owns the edit build's target path, not the save implementation. The catalog repository is the external prerequisite that supplies `main` and the skill being edited. An edit build resolves the skill from the recorded head of `main`, so a later commit to `main` does not change an already-open edit build. FA-6 (BSB-45) packages and FA-15 (BSB-54) submits both build kinds, so `build_kind` must be `edit` and `skill_path` must be the existing folder rather than a new one.
