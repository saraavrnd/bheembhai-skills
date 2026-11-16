# Stories — BSB-20 (Skill cloning & edit builds)

Epic BSB-20 covers FR-011, FR-012, FR-013, FR-014, FR-124, FR-125 and FR-126. Decomposed into 2
stories below; coverage of all 7 requirements verified.

> New stories use draft keys `BSB-20-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-20, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-20-PENDING-1

**Title:** Clone a catalog skill into a new skill under a new name
**Epic:** BSB-20 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **to clone an existing catalog skill under a new name**, so that **I can adapt a proven skill as an independent skill without copying its files by hand or changing the original**.

### Acceptance Criteria

Scenario: Clone creates a build and copies the whole skill folder
Given a signed-in skill author whose local "users" id is 42, an empty "builds" table, a catalog repository whose "main" head is commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", and a source skill folder "skills/sdlc-plan-training/" on "main" that contains "SKILL.md", "verify.yaml", "references/README.md", "templates/run.md" and "examples/seed.json"
When the author submits a clone of "sdlc-plan-training" under the new name "sdlc-plan-workshop" on the clone form at "/builds/new?mode=clone"
Then the builder responds with HTTP 201 and a body containing "Build 1 cloned from sdlc-plan-training to sdlc-plan-workshop on branch build/sdlc-plan-workshop from base commit 4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3.", and exactly one "builds" row exists with skill "sdlc-plan-workshop", kind "clone", cloned_from "sdlc-plan-training", created_by 42, branch "build/sdlc-plan-workshop", base_sha "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", head_sha equal to the SHA of the clone commit at the head of branch "build/sdlc-plan-workshop", state "open" and ready_sha NULL, and the catalog repository has a branch "build/sdlc-plan-workshop" whose head commit has parent "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" and whose "skills/sdlc-plan-workshop/" tree holds exactly those five files at the same relative paths and no other file, each copied from the source tree at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"

Scenario: Every copied file except SKILL.md and verify.yaml is byte-identical to its source
Given the clone of "sdlc-plan-training" to "sdlc-plan-workshop" completed on branch "build/sdlc-plan-workshop" from base commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"
When the file trees under "skills/sdlc-plan-training/" at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" and under "skills/sdlc-plan-workshop/" at the clone commit are compared
Then "references/README.md", "templates/run.md" and "examples/seed.json" are byte-identical to their source files, "verify.yaml" has skill "sdlc-plan-workshop" and every other byte identical to its source, and "SKILL.md" and "verify.yaml" are the only copied files whose bytes differ from their source

Scenario: Copied SKILL.md frontmatter carries the new skill name and nothing else changes
Given the clone of "sdlc-plan-training" to "sdlc-plan-workshop" whose source "SKILL.md" frontmatter has name "sdlc-plan-training", description "Plan a training session", role "author" and model "medium", and whose body is the text "Use this skill to plan a training session."
When "skills/sdlc-plan-workshop/SKILL.md" at the clone commit is parsed
Then its frontmatter has name "sdlc-plan-workshop", its description is "Plan a training session", its role is "author" and its model is "medium", and its body is byte-identical to the source body, so the frontmatter name value is the only difference from the source file

Scenario: Clone passes the catalog's static manifest checks
Given the clone of "sdlc-plan-training" to "sdlc-plan-workshop" completed on branch "build/sdlc-plan-workshop" in the catalog repository
When "python tools/check.py" runs at the root of the catalog repository checked out on branch "build/sdlc-plan-workshop" and the pinned "bheembhai-verify lint" runs on "skills/sdlc-plan-workshop/"
Then "python tools/check.py" exits with code 0 with no output line naming "skills/sdlc-plan-workshop", and "bheembhai-verify lint" exits with code 0 with no error line naming "skills/sdlc-plan-workshop"

Scenario: Cloning leaves the source skill and main unchanged
Given the clone of "sdlc-plan-training" to "sdlc-plan-workshop" completed on branch "build/sdlc-plan-workshop" from base commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"
When the catalog repository is queried after the clone
Then "main" still points at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" and has no path "skills/sdlc-plan-workshop/", and on branch "build/sdlc-plan-workshop" the set of files under "skills/sdlc-plan-training/" is identical to that commit and each of those files is byte-identical to it

Scenario: Clone rejects a source skill that does not exist on main
Given a signed-in skill author and a catalog "main" branch with no skill folder "skills/sdlc-plan-missing"
When the author submits a clone of "sdlc-plan-missing" under the new name "sdlc-plan-workshop" on the clone form at "/builds/new?mode=clone"
Then the builder responds with HTTP 422 and the message "Source skill sdlc-plan-missing does not exist on main.", and creates no "builds" row and no branch "build/sdlc-plan-workshop"

Scenario: Clone rejects a new name that already exists on main
Given a signed-in skill author and a catalog "main" branch whose head contains the skill folder "skills/sdlc-plan-workshop/SKILL.md"
When the author submits a clone of "sdlc-plan-training" under the new name "sdlc-plan-workshop" on the clone form at "/builds/new?mode=clone"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-workshop already exists on main.", and creates no "builds" row and no branch "build/sdlc-plan-workshop"

Scenario: Clone rejects a new name that another open build already uses
Given a signed-in skill author and a "builds" row with id 12, skill "sdlc-plan-workshop" and state "open"
When the author submits a clone of "sdlc-plan-training" under the new name "sdlc-plan-workshop" on the clone form at "/builds/new?mode=clone"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-workshop is already used by an open build.", and the "builds" table still contains exactly one row with skill "sdlc-plan-workshop" and no branch "build/sdlc-plan-workshop" is created

### Covered requirements (traceability)
- FR-011
- FR-012
- FR-013
- FR-014

### Out of scope
Creating a fresh build and its scaffold (BSB-19-PENDING-1 and BSB-19-PENDING-2); BSB-19-PENDING-1
owns the base create route and create mode of the single `GET /builds/new` + `POST /builds`
handler, and this story adds the clone mode to that same handler and creates no second handler at
that route; opening an edit build (BSB-20-PENDING-2); editing the cloned skill's files after
creation (BSB-21); running, scanning, readiness and catalog submission (later epics); deleting or
reusing `build/<skill-name>` after a build is merged or abandoned (BSB-36); renaming or deleting
the source skill or the clone; preserving the source repository's git history (the clone copies
content, not history); skill versioning.

### Notes / dependencies
Depends on BSB-19-PENDING-1 for the build record, the branch name rule, base_sha and the single
shared create-build handler, and on BSB-19-PENDING-3 for the shared skill-name validator and
open-build collision check, which this story reuses unchanged; the name checks apply to the new
name only, because the source name necessarily exists on main. Depends on BSB-18 for the signed-in
skill author and the local "users" row that "builds.created_by" references, and on the external
catalog repository "bheembhai-skills" and its "main" branch (PRD section 8; ADR SK-001 section 1a).

The build is the durable system of record: a row in the builder's own "builds" table with kind
"clone" and cloned_from set to the source skill name, plus a real branch in the catalog repository,
not a placeholder. The copy is a whole-folder copy at identical relative paths. SKILL.md and
verify.yaml's `skill` value are the only files rewritten: SKILL.md's frontmatter `name` and
verify.yaml's top-level `skill` both become "sdlc-plan-workshop", and every other byte of both
files and every other copied file stays byte-identical, so both `python tools/check.py` and the
pinned `bheembhai-verify lint` exit 0 on the clone. The clone has no runtime link back to the
source beyond the cloned_from column.

The clone form extends BSB-19-PENDING-1's single `GET /builds/new` + `POST /builds` handler and
adds no second handler at that route: BSB-19-PENDING-1 owns the base create route and its `create`
mode, and this story owns the `clone`-mode dispatch on that same handler. The build mode is
carried as the `mode` query parameter on `GET /builds/new` and a hidden `mode` form field on the
`POST /builds` body; allowed values are
`create` (the default when the parameter is absent), `clone` and `edit`, matching `builds.kind`.
In `clone` mode the request fields are the source skill name and the new skill name.

The copy commit sets `builds.head_sha`; `base_sha` stays fixed at the commit the branch was cut
from, the copy reads the source tree at `base_sha` rather than a moving `main` ref, and the clone
commit's parent is `base_sha`. The branch name is fixed at `build/<skill-name>`. When a prior build
for the same skill was merged or abandoned, a new build resets that branch to the new `base_sha`
and creates no second branch; deleting or finalising the branch on merge or abandonment belongs to
BSB-36 (submission and build lifecycle), not this epic. Submission and merge are out of this epic.

---

## STORY: BSB-20-PENDING-2

**Title:** Open an existing catalog skill in an edit build
**Epic:** BSB-20 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **to open an existing catalog skill in an edit build on its own branch**, so that **I can improve the catalog skill in place without creating a duplicate entry or touching main directly**.

### Acceptance Criteria

Scenario: Edit build is opened on a branch cut from the head of main
Given a signed-in skill author whose local "users" id is 42, an empty "builds" table, a catalog repository whose "main" head is commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", and an existing skill folder "skills/sdlc-plan-training/" on "main"
When the author submits an edit build for "sdlc-plan-training" on the edit form at "/builds/new?mode=edit"
Then the builder responds with HTTP 201 and a body containing "Build 1 opened for edits to sdlc-plan-training on branch build/sdlc-plan-training from base commit 4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3.", and exactly one "builds" row exists with skill "sdlc-plan-training", kind "edit", cloned_from NULL, created_by 42, branch "build/sdlc-plan-training", base_sha "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", head_sha "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", state "open" and ready_sha NULL, and the catalog repository has a branch "build/sdlc-plan-training" pointing at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"

Scenario: Edit build resolves to the existing skill folder and creates no second one
Given an edit build with id 1 for skill "sdlc-plan-training" on branch "build/sdlc-plan-training" created from base commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", and "main" at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" contains exactly one skill folder "skills/sdlc-plan-training/"
When the edit build resolves its target skill folder at the head of branch "build/sdlc-plan-training"
Then the resolved target is "skills/sdlc-plan-training/", "git ls-tree -d --name-only skills/" returns exactly "sdlc-plan-training" and no other name, and no path "skills/sdlc-plan-training-copy/" or "skills/sdlc-plan-training-2/" exists on the branch

Scenario: Edit build rejects a skill name that does not exist on main
Given a signed-in skill author and a catalog "main" branch with no skill folder "skills/sdlc-plan-missing"
When the author submits an edit build for "sdlc-plan-missing" on the edit form at "/builds/new?mode=edit"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-missing does not exist on main.", and creates no "builds" row and no branch "build/sdlc-plan-missing"

Scenario: Edit build rejects a skill that another open build already uses
Given a signed-in skill author and a "builds" row with id 12, skill "sdlc-plan-training" and state "open"
When the author submits an edit build for "sdlc-plan-training" on the edit form at "/builds/new?mode=edit"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-training is already used by an open build.", and the "builds" table still contains exactly one row with skill "sdlc-plan-training" and no second branch "build/sdlc-plan-training" is created

Scenario: Edit build rejects a submission with no skill selected
Given a signed-in skill author and a "builds" table with no edit build
When the author submits the edit form at "/builds/new?mode=edit" with no skill selected
Then the builder responds with HTTP 422 and the message "A skill name is required.", and creates no "builds" row and no branch

### Covered requirements (traceability)
- FR-124
- FR-125
- FR-126

### Out of scope
Editing file content after the build exists (BSB-21, FR-127); creating a fresh or cloned build
(BSB-19 and BSB-20-PENDING-1); BSB-19-PENDING-1 owns the base create route and create mode of the
single `GET /builds/new` + `POST /builds` handler, and this story adds the edit mode to that same
handler and creates no second handler at that route; submitting the branch or merging it into the
catalog; deleting or reusing `build/<skill-name>` after a build is merged or abandoned (BSB-36);
renaming, deleting or recovering a skill or build; readiness tracking, runs and scans (BSB-21
onward).

### Notes / dependencies
Depends on BSB-19-PENDING-1 for the build record, the branch name rule, base_sha and the single
shared `GET /builds/new` + `POST /builds` handler, and on BSB-19-PENDING-3 for the shared
skill-name validator and open-build collision check. BSB-19-PENDING-1 owns the base create route
and its `create` mode, and BSB-19-PENDING-3 owns the skill-name pattern validator and open-build
collision check for both the clone flow and this edit flow; this story owns the `edit`-mode
dispatch on the same handler and the inverted existence rule.
In edit mode the existence check is inverted: the name must exist on main (FR-126), so the create
and clone rule that a name already on main is rejected does not apply; the open-build collision
check does apply, so a skill already used by another open build is rejected. Because of that
inversion, the shared validator takes a `mode` parameter (`create`/`clone` versus `edit`) that
selects the existence rule, while the pattern and open-build collision parts are reused unchanged.
Depends on BSB-18 for the signed-in skill author and the local "users" row that "builds.created_by"
references, and on the external catalog repository "bheembhai-skills" and its "main" branch (PRD
section 8; ADR SK-001 section 1a).

The build is the durable system of record: a row in the builder's own "builds" table with kind
"edit" and cloned_from NULL, plus a branch in the catalog repository cut from main. The branch has
no commit of its own, so `builds.head_sha` starts equal to `base_sha`, and BSB-21's first save
moves it. The edit build resolves its target to the existing `skills/<skill-name>/` folder and
creates no second folder; the save flow delivered in BSB-21 (FR-127) must therefore commit only to
that existing folder, and BSB-21's save acceptance criteria must assert exactly that (the FR-125
proof). Main is never written by the edit build; the change reaches the catalog only through the
submission epic's pull request.

The edit form extends BSB-19-PENDING-1's single `GET /builds/new` + `POST /builds` handler and
adds no second handler at that route. The build mode is carried as the `mode` query parameter on
`GET /builds/new` and a hidden `mode` form field on the `POST /builds` body; allowed values are
`create` (the default when the parameter is absent), `clone` and `edit`, matching `builds.kind`.
In `edit` mode the request field is the existing skill name only. The branch name is fixed at
`build/<skill-name>`. When a prior build for the same skill was merged or abandoned, a new build
resets that branch to the new `base_sha` and creates no second branch; deleting or finalising the
branch on merge or abandonment belongs to BSB-36 (submission and build lifecycle), not this epic.
