# Stories — BSB-19 (Skill build creation & scaffolding)

Epic BSB-19 covers FR-006, FR-007, FR-008, FR-009, FR-010, FR-015, FR-016, FR-017, FR-143 and
FR-144. Decomposed into 3 stories below; coverage of all 10 requirements verified.

> New stories use draft keys `BSB-19-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-19, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-19-PENDING-1

**Title:** Create a build and cut its branch from the head of main
**Epic:** BSB-19 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **to create a build from a skill name and a one-line description**, so that **I get a dedicated branch cut from main to author the skill on without touching main**.

### Acceptance Criteria

Scenario: Build is created and its branch is cut from the current head of main
Given a signed-in skill author whose local "users" id is 42, an empty "builds" table, and a catalog repository whose "main" head is commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"
When the author submits the skill name "sdlc-plan-new-skill" and the one-line description "Plan a training session" on the create build form at "/builds/new"
Then the builder responds with HTTP 201 and a body containing "Build 1 created on branch build/sdlc-plan-new-skill from base commit 4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3.", and exactly one "builds" row exists with skill "sdlc-plan-new-skill", kind "create", created_by 42, branch "build/sdlc-plan-new-skill", base_sha "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", state "open" and ready_sha NULL, and the catalog repository has a branch "build/sdlc-plan-new-skill"

Scenario: Build branch follows the latest head of main
Given a signed-in skill author whose local "users" id is 42, the catalog repository's "main" head was commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" when an earlier build was created, and "main" has since advanced to commit "8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b"
When the author submits the skill name "sdlc-train-session-plan" and the one-line description "Plan a training session" on the create build form at "/builds/new"
Then the new "builds" row has base_sha "8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b" and the branch "build/sdlc-train-session-plan" was created from commit "8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c5b", not from the earlier build's base commit

Scenario: Blank description is rejected
Given a signed-in skill author and a "builds" table with no row for "sdlc-plan-new-skill"
When the author submits the skill name "sdlc-plan-new-skill" with a description of "   " on the create build form at "/builds/new"
Then the builder responds with HTTP 422 and the message "A one-line description is required.", and creates no "builds" row and no branch "build/sdlc-plan-new-skill"

Scenario: Multi-line description is rejected
Given a signed-in skill author and a "builds" table with no row for "sdlc-plan-new-skill"
When the author submits the skill name "sdlc-plan-new-skill" with a description whose text is "Plan a training session" followed by a line break and the text "and review it", on the create build form at "/builds/new"
Then the builder responds with HTTP 422 and the message "The description must be a single line.", and creates no "builds" row and no branch "build/sdlc-plan-new-skill"

### Covered requirements (traceability)
- FR-006
- FR-007

### Out of scope
Skill-name validation and duplicate-name rejection (BSB-19-PENDING-3); the scaffold content
(BSB-19-PENDING-2); cloning (BSB-20); editing, saving and build-head tracking after creation
(BSB-21); readiness, runs, scans and catalog submission (BSB-21 onward); changing or deleting a
build; build state transitions other than the initial "open".

### Notes / dependencies
Depends on the access epic BSB-18 for the signed-in skill author and the local "users" row that
"builds.created_by" references, and on the external catalog repository "bheembhai-skills" and its
"main" branch (PRD section 8 external prerequisites; ADR SK-001 section 1a). The build is the
durable system of record: a row in the builder's own "builds" table (ADR SK-001 section 9) plus a
real branch in the catalog repository, not a placeholder. The epic requires the base SHA to be
recorded on the build, so "builds" carries a "base_sha" column alongside the ADR's key columns;
"base_sha" stays fixed at the resolved head of "main" while "head_sha" tracks the branch head and
moves with the scaffold commit in BSB-19-PENDING-2 and with later saves in BSB-21. The create form
is served at GET "/builds/new" and POST "/builds" returns the confirmation body; these routes are
owned by this epic, and the full build page with head and readiness is BSB-21's. The branch name is
the literal prefix "build/" followed by the skill name, so skill "sdlc-plan-new-skill" gets branch
"build/sdlc-plan-new-skill"; project membership (BSB-22) plays no part in creating a build.

---

## STORY: BSB-19-PENDING-2

**Title:** Scaffold a catalog-shaped skill folder on the build branch
**Epic:** BSB-19 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **a new build to start with a catalog-shaped skill folder**, so that **I can edit and verify a valid skill without hand-assembling its structure**.

### Acceptance Criteria

Scenario: Scaffold is committed on the build branch and nothing else changes
Given build 1 exists for skill "sdlc-plan-new-skill" on branch "build/sdlc-plan-new-skill" with base_sha "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"
When the create flow completes its scaffold step
Then the branch head is a new commit whose parent is "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", the commit changes only paths under "skills/sdlc-plan-new-skill/", "builds.head_sha" for build 1 equals that new commit SHA and "builds.base_sha" is unchanged, and "catalog.yaml" and every other skill folder on the branch are identical to commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"

Scenario: SKILL.md carries the skill's frontmatter
Given the scaffold commit for skill "sdlc-plan-new-skill" with the submitted description "Plan a training session"
When "skills/sdlc-plan-new-skill/SKILL.md" is parsed
Then its YAML frontmatter has name "sdlc-plan-new-skill", description "Plan a training session", role "author", and non-empty values for the "compatibility" and "model" keys

Scenario: verify.yaml is a valid manifest stub with no checks
Given the scaffold commit for skill "sdlc-plan-new-skill"
When "skills/sdlc-plan-new-skill/verify.yaml" is parsed and "bheembhai-verify lint" runs on the folder
Then the file is valid YAML, its skill value is "sdlc-plan-new-skill", it declares no checks, and "bheembhai-verify lint" exits 0

Scenario: Standard folders exist in the scaffold
Given the scaffold commit for skill "sdlc-plan-new-skill"
When the skill folder tree is read at the branch head
Then the folder contains "references/README.md", "templates/.gitkeep" and "examples/.gitkeep" as tracked files, so the "references", "templates" and "examples" folders exist on the branch

Scenario: Unedited scaffold passes the catalog's static manifest checks
Given a clean checkout of branch "build/sdlc-plan-new-skill" at the scaffold commit for skill "sdlc-plan-new-skill", with no manual edit
When the catalog's static checks "python tools/check.py" and the tier-1 "bheembhai-verify" run on it
Then "python tools/check.py" exits 0 and reports no errors, and tier-1 verification returns verdict "pass" with "no checks" reported only as a warning

Scenario: Re-running the scaffold makes no new commit
Given build 1's branch "build/sdlc-plan-new-skill" is at commit "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678", which already contains the complete scaffold for skill "sdlc-plan-new-skill"
When the create flow retries its scaffold step for build 1
Then no new commit is created, the branch head remains "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678", and the tracked file list under "skills/sdlc-plan-new-skill/" is unchanged

Scenario: Scaffold commit failure leaves no partial skill folder
Given build 1 exists for skill "sdlc-plan-new-skill" on branch "build/sdlc-plan-new-skill" with base_sha "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", and the catalog source-control API returns HTTP 500 for the scaffold commit
When the create flow runs its scaffold step
Then the builder responds with HTTP 502 and the message "The skill scaffold could not be committed. Retry the build.", the branch "build/sdlc-plan-new-skill" stays at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" with no new commit, and "builds.head_sha" for build 1 remains "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"

### Covered requirements (traceability)
- FR-008
- FR-009
- FR-010
- FR-143
- FR-144

### Out of scope
The create form, build record and branch creation (BSB-19-PENDING-1); the actual verify.yaml checks a
mature skill needs; SKILL.md body sections beyond the default scaffold; filling references,
templates or examples with content; editing the scaffold after creation (BSB-21); running the
skill or scanning it.

### Notes / dependencies
Depends on BSB-19-PENDING-1 for the build row, its base_sha and the branch. The scaffold template is
`skill-builder/scaffold/`, kept in step with the catalog's current verify.yaml version (ADR SK-001
section 1a), so the generated folder matches the catalog's shape at creation time. The scaffold
carries `role: author` because the catalog's static check requires every skill frontmatter to
declare one of author, reviewer or integration (ADR-035; `tools/check.py`); a newly authored skill
is an author skill. Tier-1 passing with a "no checks" warning is the expected state for a fresh
scaffold (ADR SK-001 section 1a), not a defect. The scaffold writer is idempotent: re-running it
against a branch whose skill folder already holds the scaffold makes no new commit and leaves the
target tree unchanged. The catalog repository and both checkers are external prerequisites (PRD
section 8).

---

## STORY: BSB-19-PENDING-3

**Title:** Reject invalid and duplicate skill names before creating a build
**Epic:** BSB-19 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **the builder to refuse a name that is malformed, already on main or already used by an open build**, so that **I get a clear reason instead of a colliding branch or a duplicate skill in the catalog**.

### Acceptance Criteria

Scenario: Name without the sdlc prefix is rejected
Given a signed-in skill author and a catalog "main" branch that has no skill folder "skills/plan-new-skill"
When the author submits the skill name "plan-new-skill" with a one-line description on the create build form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill name must have the sdlc prefix and at least an area and an action segment, for example sdlc-plan-new-skill.", and creates no "builds" row and no branch for that name

Scenario: Name missing the action segment is rejected
Given a signed-in skill author and a catalog "main" branch that has no skill folder "skills/sdlc-plan"
When the author submits the skill name "sdlc-plan" with a one-line description on the create build form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill name must have the sdlc prefix and at least an area and an action segment, for example sdlc-plan-new-skill.", and creates no "builds" row and no branch for that name

Scenario: Name with uppercase or underscore characters is rejected
Given a signed-in skill author and a catalog "main" branch that has no skill folder "skills/sdlc-Plan_new-Skill"
When the author submits the skill name "sdlc-Plan_new-Skill" with a one-line description on the create build form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill name must have the sdlc prefix and at least an area and an action segment, for example sdlc-plan-new-skill.", and creates no "builds" row and no branch for that name

Scenario: Name that already exists on main is rejected
Given a signed-in skill author and a catalog "main" branch whose head contains the skill folder "skills/sdlc-plan-new-skill/SKILL.md"
When the author submits the skill name "sdlc-plan-new-skill" with the one-line description "Plan a training session" on the create build form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-new-skill already exists on main.", and creates no "builds" row and no branch "build/sdlc-plan-new-skill"

Scenario: Name used by another open build is rejected
Given a signed-in skill author and a "builds" row with id 12, skill "sdlc-plan-new-skill" and state "open"
When the author submits the skill name "sdlc-plan-new-skill" with the one-line description "Plan a training session" on the create build form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-new-skill is already used by an open build.", and the "builds" table still contains exactly one row with skill "sdlc-plan-new-skill" and no second branch "build/sdlc-plan-new-skill" is created

Scenario: A free valid name is accepted
Given a signed-in skill author, a catalog "main" branch with no skill folder "skills/sdlc-train-session-plan", and no open build for that name
When the author submits the skill name "sdlc-train-session-plan" with the one-line description "Plan a training session" on the create build form at "/builds/new"
Then the builder responds with HTTP 201 and creates a "builds" row with skill "sdlc-train-session-plan" and state "open"

### Covered requirements (traceability)
- FR-015
- FR-016
- FR-017

### Out of scope
Renaming a skill or a build after creation; case-insensitive aliasing or slug normalisation beyond
rejecting non-lowercase names; clone-build creation (BSB-20), which must reuse this same validator
and collision check; deleting or recovering an abandoned build; catalog-level name governance
outside this check.

### Notes / dependencies
Depends on BSB-19-PENDING-1 for the create flow and the "builds" table, and on the catalog
repository's "main" branch for the on-main check. "Another open build" means a "builds" row whose
"state" is "open" (ADR SK-001 section 9); this epic creates only the "open" state, other states are
owned by BSB-21 and BSB-36. Both checks run before any branch is created, so a rejected request
leaves no "builds" row and no branch in the catalog repository. The name pattern follows
ADR SK-001 section 1a: a literal "sdlc-" prefix, then an area segment and an action segment, all
lowercase letters, digits and hyphens, with at least three hyphen-separated segments. The validator
and collision check are reused unchanged by the clone flow in BSB-20 (FR-015 covers create or
clone).
