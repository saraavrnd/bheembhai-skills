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
When the author submits a clone of "sdlc-plan-training" under the new name "sdlc-plan-workshop" on the clone form at "/builds/new"
Then the builder responds with HTTP 201 and a body containing "Build 1 cloned from sdlc-plan-training to sdlc-plan-workshop on branch build/sdlc-plan-workshop from base commit 4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3.", and exactly one "builds" row exists with skill "sdlc-plan-workshop", kind "clone", cloned_from "sdlc-plan-training", created_by 42, branch "build/sdlc-plan-workshop", base_sha "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", state "open" and ready_sha NULL, and the catalog repository has a branch "build/sdlc-plan-workshop" whose "skills/sdlc-plan-workshop/" tree holds exactly those five files at the same relative paths and no other file

Scenario: Every copied file except SKILL.md is byte-identical to its source
Given the clone of "sdlc-plan-training" to "sdlc-plan-workshop" completed on branch "build/sdlc-plan-workshop" from base commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"
When the file trees under "skills/sdlc-plan-training/" at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" and under "skills/sdlc-plan-workshop/" at the clone commit are compared
Then "verify.yaml", "references/README.md", "templates/run.md" and "examples/seed.json" are byte-identical to their source files, and "SKILL.md" is the only copied file whose bytes differ

Scenario: Copied SKILL.md frontmatter carries the new skill name and nothing else changes
Given the clone of "sdlc-plan-training" to "sdlc-plan-workshop" whose source "SKILL.md" frontmatter has name "sdlc-plan-training", description "Plan a training session", role "author" and model "medium", and whose body is the text "Use this skill to plan a training session."
When "skills/sdlc-plan-workshop/SKILL.md" at the clone commit is parsed
Then its frontmatter has name "sdlc-plan-workshop", its description is "Plan a training session", its role is "author" and its model is "medium", and its body is byte-identical to the source body, so the frontmatter name value is the only difference from the source file

Scenario: Cloning leaves the source skill and main unchanged
Given the clone of "sdlc-plan-training" to "sdlc-plan-workshop" completed on branch "build/sdlc-plan-workshop" from base commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"
When the catalog repository is queried after the clone
Then "main" still points at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" and has no path "skills/sdlc-plan-workshop/", and on branch "build/sdlc-plan-workshop" the set of files under "skills/sdlc-plan-training/" is identical to that commit and each of those files is byte-identical to it

Scenario: Clone rejects a source skill that does not exist on main
Given a signed-in skill author and a catalog "main" branch with no skill folder "skills/sdlc-plan-missing"
When the author submits a clone of "sdlc-plan-missing" under the new name "sdlc-plan-workshop" on the clone form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Source skill sdlc-plan-missing does not exist on main.", and creates no "builds" row and no branch "build/sdlc-plan-workshop"

Scenario: Clone rejects a new name that already exists on main
Given a signed-in skill author and a catalog "main" branch whose head contains the skill folder "skills/sdlc-plan-workshop/SKILL.md"
When the author submits a clone of "sdlc-plan-training" under the new name "sdlc-plan-workshop" on the clone form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-workshop already exists on main.", and creates no "builds" row and no branch "build/sdlc-plan-workshop"

Scenario: Clone rejects a new name that another open build already uses
Given a signed-in skill author and a "builds" row with id 12, skill "sdlc-plan-workshop" and state "open"
When the author submits a clone of "sdlc-plan-training" under the new name "sdlc-plan-workshop" on the clone form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-workshop is already used by an open build.", and the "builds" table still contains exactly one row with skill "sdlc-plan-workshop" and no branch "build/sdlc-plan-workshop" is created

### Covered requirements (traceability)
- FR-011
- FR-012
- FR-013
- FR-014

### Out of scope
Creating a fresh build and its scaffold (BSB-19-PENDING-1 and BSB-19-PENDING-2); opening an edit
build (BSB-20-PENDING-2); editing the cloned skill's files after creation (BSB-21); running,
scanning, readiness and catalog submission (later epics); renaming or deleting the source skill or
the clone; preserving the source repository's git history (the clone copies content, not history);
skill versioning.

### Notes / dependencies
Depends on BSB-19-PENDING-1 for the build record, the branch name rule and base_sha, and on
BSB-19-PENDING-3 for the shared skill-name validator and open-build collision check, which this
story reuses unchanged; the name checks apply to the new name only, because the source name
necessarily exists on main. Depends on BSB-18 for the signed-in skill author and the local "users"
row that "builds.created_by" references, and on the external catalog repository "bheembhai-skills"
and its "main" branch (PRD section 8; ADR SK-001 section 1a). The build is the durable system of
record: a row in the builder's own "builds" table with kind "clone" and cloned_from set to the
source skill name, plus a real branch in the catalog repository, not a placeholder. The copy is a
whole-folder copy at identical relative paths; SKILL.md is the only file rewritten, and only its
frontmatter name value changes, so the rest of that file and every other file stays byte-identical.
The clone has no runtime link back to the source beyond the cloned_from column. The clone form is
served at GET "/builds/new" with mode clone and POST "/builds" creates the build; submission and
merge are out of this epic.

---

## STORY: BSB-20-PENDING-2

**Title:** Open an existing catalog skill in an edit build
**Epic:** BSB-20 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-2, MVP

### Story
As a **skill author**, I want **to open an existing catalog skill in an edit build on its own branch**, so that **I can improve the catalog skill in place without creating a duplicate entry or touching main directly**.

### Acceptance Criteria

Scenario: Edit build is opened on a branch cut from the head of main
Given a signed-in skill author whose local "users" id is 42, an empty "builds" table, a catalog repository whose "main" head is commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", and an existing skill folder "skills/sdlc-plan-training/" on "main"
When the author submits an edit build for "sdlc-plan-training" on the edit form at "/builds/new"
Then the builder responds with HTTP 201 and a body containing "Build 1 opened for edits to sdlc-plan-training on branch build/sdlc-plan-training from base commit 4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3.", and exactly one "builds" row exists with skill "sdlc-plan-training", kind "edit", cloned_from NULL, created_by 42, branch "build/sdlc-plan-training", base_sha "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", state "open" and ready_sha NULL, and the catalog repository has a branch "build/sdlc-plan-training" pointing at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3"

Scenario: Edit build reuses the existing skill folder and creates no second one
Given an edit build with id 1 for skill "sdlc-plan-training" on branch "build/sdlc-plan-training" created from base commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", and "main" at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3" contains the single skill folder "skills/sdlc-plan-training/"
When the skill folder list under "skills/" on branch "build/sdlc-plan-training" is read at its head
Then "git ls-tree -d --name-only skills/" returns exactly the same list of folder names as at commit "4f1c2ab7d9e8f6a5b4c3d2e1f0a9b8c7d6e5f4a3", and no path "skills/sdlc-plan-training-copy/" or "skills/sdlc-plan-training-2/" exists on the branch

Scenario: Edit build rejects a skill name that does not exist on main
Given a signed-in skill author and a catalog "main" branch with no skill folder "skills/sdlc-plan-missing"
When the author submits an edit build for "sdlc-plan-missing" on the edit form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-missing does not exist on main.", and creates no "builds" row and no branch "build/sdlc-plan-missing"

Scenario: Edit build rejects a skill that another open build already uses
Given a signed-in skill author and a "builds" row with id 12, skill "sdlc-plan-training" and state "open"
When the author submits an edit build for "sdlc-plan-training" on the edit form at "/builds/new"
Then the builder responds with HTTP 422 and the message "Skill sdlc-plan-training is already used by an open build.", and the "builds" table still contains exactly one row with skill "sdlc-plan-training" and no second branch "build/sdlc-plan-training" is created

Scenario: Edit build rejects a submission with no skill selected
Given a signed-in skill author and a "builds" table with no edit build
When the author submits the edit form at "/builds/new" with no skill selected
Then the builder responds with HTTP 422 and the message "A skill name is required.", and creates no "builds" row and no branch

### Covered requirements (traceability)
- FR-124
- FR-125
- FR-126

### Out of scope
Editing file content after the build exists (BSB-21, FR-127); creating a fresh or cloned build
(BSB-19 and BSB-20-PENDING-1); submitting the branch or merging it into the catalog; renaming,
deleting or recovering a skill or build; readiness tracking, runs and scans (BSB-21 onward).

### Notes / dependencies
Depends on BSB-19-PENDING-1 for the build record, the branch name rule and base_sha, and on
BSB-19-PENDING-3 for the shared skill-name validator and open-build collision check. In edit mode
the existence check is inverted: the name must exist on main (FR-126), so the create and clone rule
that a name already on main is rejected does not apply; the open-build collision check does apply,
so a skill already used by another open build is rejected. Depends on BSB-18 for the signed-in
skill author and the local "users" row that "builds.created_by" references, and on the external
catalog repository "bheembhai-skills" and its "main" branch (PRD section 8; ADR SK-001 section 1a).
The build is the durable system of record: a row in the builder's own "builds" table with kind
"edit" and cloned_from NULL, plus a branch in the catalog repository cut from main with no commit
of its own. The branch holds exactly one folder for this skill, the existing skill folder under
"skills/", so the save flow delivered in BSB-21 (FR-127) commits to that existing folder and never
to a second one. The edit form is served at GET "/builds/new" with mode edit and POST "/builds"
creates the build. Main is never written by the edit build; the change reaches the catalog only
through the submission epic's pull request.
