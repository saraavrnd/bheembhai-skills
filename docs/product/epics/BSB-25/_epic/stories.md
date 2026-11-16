# Stories — BSB-25 (Skill packaging & run branch preparation)

Epic BSB-25 covers FR-038, FR-039, FR-040, FR-041, FR-042, FR-043, NFR-001 and NFR-009.
Decomposed into 3 vertical slices below; coverage of all 8 requirements verified.

The three slices follow one run's preparation from the author's chosen branches to an immutable,
reproducible, isolated input. The author first gets the exact skills commit they chose pinned on the
run (PENDING-1), then gets the skill content at that commit packaged once and reused for the same
commit (PENDING-2), and finally gets a run branch of their own cut from the input branch's head with
that head recorded as the baseline and the input branch left untouched (PENDING-3). Every slice ends
in durable state on the run (`runs.skills_commit_sha`, a `skill_bundles` row, `runs.run_branch` and
`runs.baseline_sha`) that scanning, execution, verification and the run report consume.

The run is created in state `requested` by BSB-24. This epic's run-preparation step moves it through
`preparing` to `prepared`, or to `preparation_failed` with a concrete `preparation_error`.

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-038 — resolve the skills branch to a commit SHA at run start | BSB-25-PENDING-1 | "The run's skills branch is resolved and frozen at a commit"; "A requested run is picked up for preparation exactly once"; "A re-resolution keeps the already-frozen commit" |
| FR-039 — package the skill at that commit into a content-addressed bundle | BSB-25-PENDING-2 | "The first preparation of a commit packs and stores one bundle" |
| FR-040 — reuse an existing bundle for the same skills commit | BSB-25-PENDING-2 | "Re-preparing the same commit reuses the stored bundle"; "A different skill at the same commit gets its own bundle" |
| FR-041 — create the run branch from the input branch head | BSB-25-PENDING-3 | "The run branch is created from the input head and the baseline is recorded" |
| FR-042 — record the input branch head as the run baseline | BSB-25-PENDING-3 | "The run branch is created from the input head and the baseline is recorded"; "A branch that moves after the baseline is read does not change the run's start point" |
| FR-043 — a run never writes to its input branch | BSB-25-PENDING-3 | "A write aimed at the input branch is refused" |
| NFR-001 — non-model run preparation within 60 seconds for a 5 MB bundle | BSB-25-PENDING-3 | "A 5 MB skill bundle is prepared within 60 seconds" |
| NFR-009 — the same skills commit produces an identical bundle twice | BSB-25-PENDING-2 | "The same commit packs to identical bytes twice" |

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than an epic: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 "Issue
does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The Atlassian
MCP tools were not exposed in this session, so the configured site was queried read-only through its
REST API. The epic being decomposed is BSB-25, read read-only from the same site: summary "Skill
packaging & run branch preparation", status To Do, labels FA-6/MVP, no parent and no sub-tasks. No
Jira write was attempted and no issue content is assumed from the lookup.

> New stories use draft keys `BSB-25-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-25, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-25-PENDING-1

**Title:** Run the exact skills commit I chose even after the branch moves
**Epic:** BSB-25 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **the builder to resolve my run's skills branch to an exact commit and freeze that commit on the run**, so that **the run tests the skill content I chose and a later push to the branch cannot change what executes**.

### Acceptance Criteria

Scenario: The run's skills branch is resolved and frozen at a commit
Given a requested "runs" row id 21 with project_id 7, user_id 42, build_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha NULL, input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, context NULL, model_profile_id 4, tier "medium", state "requested", kind "run" and preparation_error NULL, an "integrations" row id 3 with project_id 7, kind "github", config {"repository": "saraavrnd/skill-builder-sandbox", "base_branch": "main", "test_only": true} and secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at path "skill-builder/7/integration-3", a stub source-control provider in which repository "saraavrnd/bheembhai-skills" has branch "build/sdlc-fix-bug-reproduce" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", a builder clock reading "2026-11-16T11:00:00Z", and a stub skill packer whose pack counter is 0
When the run-preparation resolver processes run 21
Then the resolver returns {"skills_commit_sha": "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", "skills_ref": "build/sdlc-fix-bug-reproduce", "state": "preparing"}, the "runs" row id 21 has skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "preparing", the stub source-control provider received exactly one branch-resolution request for repository "saraavrnd/bheembhai-skills" and branch "build/sdlc-fix-bug-reproduce" authenticated with "ghp-test-token-7a1d", the resolver sent no request to repository "saraavrnd/skill-builder-sandbox", and the stub skill packer's pack counter remains 0

Scenario: A requested run is picked up for preparation exactly once
Given two "runs" rows id 21 and 22, each with project_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha NULL, input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, state "requested" and preparation_error NULL, the source-control integration 3 for project 7 with secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at that path, a stub source-control provider in which repository "saraavrnd/bheembhai-skills" has branch "build/sdlc-fix-bug-reproduce" at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", and a run-preparation worker that picks up "runs" rows in state "requested" and whose resolution counter is 0
When the run-preparation worker runs twice
Then the first pass hands run 21 and run 22 to the resolver once each, each "runs" row has state "preparing" and skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", the worker's resolution counter is 2, and the second pass hands no run to the resolver and leaves the counter at 2

Scenario: A re-resolution keeps the already-frozen commit
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", state "preparing" and preparation_error NULL, repository "saraavrnd/bheembhai-skills" now having branch "build/sdlc-fix-bug-reproduce" at commit "8a7d3e0f5c2b9a4e1d6f8c3b7a5e2d9f4c1b6a8e", and a stub source-control provider whose branch-resolution counter is 0
When the run-preparation resolver processes run 21 again
Then the resolver returns {"skills_commit_sha": "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", "skills_ref": "build/sdlc-fix-bug-reproduce", "state": "preparing"}, the "runs" row id 21 still has skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", and the stub source-control provider's branch-resolution counter remains 0

Scenario: A skills branch that no longer exists fails preparation
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha NULL, input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, state "requested" and preparation_error NULL, the source-control integration 3 for project 7 with secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at that path, and a stub source-control provider in which repository "saraavrnd/bheembhai-skills" has no branch "build/sdlc-fix-bug-reproduce"
When the run-preparation resolver processes run 21
Then the "runs" row id 21 has state "preparation_failed", preparation_error "The selected skills branch was not found in the catalog repository.", skills_commit_sha NULL and run_branch NULL, no "skill_bundles" row exists, and the stub source-control provider received 0 branch-creation and 0 commit requests

Scenario: A provider that cannot be read fails preparation without pinning a guess
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha NULL, input_branch "test/atlas/bug-42", state "requested" and preparation_error NULL, the source-control integration 3 for project 7 with secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at that path, and a stub source-control provider that returns HTTP 503 "Service Unavailable" for the branch-resolution request
When the run-preparation resolver processes run 21
Then the "runs" row id 21 has state "preparation_failed", preparation_error "The skills branch could not be resolved.", skills_commit_sha NULL and run_branch NULL, no "skill_bundles" row exists, and the resolver returns {"state": "preparation_failed", "error": "The skills branch could not be resolved."}

### Covered requirements (traceability)
- FR-038

### Out of scope
The run request itself — membership, branch choices, context and model validation, and creating the
`requested` run row (BSB-24); packing the skill at the pinned commit and reusing a bundle
(BSB-25-PENDING-2); creating the run branch and recording the baseline (BSB-25-PENDING-3); the
packaging preflight (BSB-30); the static security scan and the run refusal when it does not pass
(BSB-31 and BSB-27); resolving the skills branch again on a re-run (BSB-27); executing the skill
(BSB-26); verification (BSB-29); the run report (BSB-33); the command-line run (BSB-37).

### Notes / dependencies
Depends on BSB-24-PENDING-1 for run 21 in state "requested", its `skills` value, `skills_ref` and
`input_branch`, and the request validation that produced them; on BSB-23-PENDING-2 for the
test-purpose `github` integration row, its sandbox `config.repository`, `config.base_branch` and
`secret_ref`; on BSB-19-PENDING-3 for the catalog-valid skill name "sdlc-fix-bug-reproduce"; and on
BSB-18 for the author identity recorded as `runs.user_id`. Preparation is a background step acting
on an already-authorized run, so it adds no membership check of its own.

This story owns the resolver, the freeze of `runs.skills_commit_sha`, the trigger that starts
preparation, and the preparation lifecycle values that the other two stories reuse. BSB-24's
`POST /projects/{id}/runs` returns immediately and does no preparation; this story owns the
background worker that picks up runs in state `requested`, so every new run — including BSB-27's
re-run row — is prepared without another epic having to trigger it. The worker claims a run by
changing its state from `requested` to `preparing`, so a second pass does not prepare the same run
again. The run-preparation step runs the resolver, then BSB-25-PENDING-2's packager, then
BSB-25-PENDING-3's branch preparer. The resolver
sets `preparing`; any stage failure sets `preparation_failed` and stores the exact message in
`runs.preparation_error`; BSB-25-PENDING-3 sets `prepared` only after all three stages succeed.
`preparation_failed` is terminal for this epic and a later attempt is a new run (BSB-27's re-run),
not a retry of the same row. The data-model stage must add `runs.preparation_error` and record these
state values; `runs.skills_commit_sha` already exists in ADR SK-001 section 9. BSB-26 and BSB-27
extend the state set for execution and terminal outcomes without renaming these values.

The catalog repository is the fixed `saraavrnd/bheembhai-skills` (ADR SK-001 section 5), read with
the project's source-control integration credential; the integration's `config.repository` remains
the sandbox repository and no new `catalog_repository` config field is introduced. Once set,
`runs.skills_commit_sha` is never overwritten: the packager, branch preparer, scanner, executor and
verifier all read it, so a branch that moves after resolution cannot change what the run uses. A
provider that fails is not retried by guessing a SHA; the run is failed with the message above.

The static scan runs after this preparation because BSB-31-PENDING-1's route reads the
`skill_bundles` row for the resolved SHA; BSB-27 owns the refusal when the verdict is not pass. This
ordering supersedes BSB-27's epic wording that puts its preflight "before a bundle or branch is
prepared" — the same cross-epic note recorded in the BSB-24 and BSB-31 reviews. BSB-30's packaging
preflight (FR-071 to FR-073) must run before BSB-25-PENDING-2 produces a bundle; those requirements
belong to BSB-30, which has no stories yet, so this is a recorded cross-epic dependency rather than
a requirement claimed here. BSB-26 executes only a run in state `prepared`; BSB-33's run report
displays the pinned SHA; BSB-37's command line uses the same preparation step.

---

## STORY: BSB-25-PENDING-2

**Title:** Package the pinned skill commit once and reuse the same bundle
**Epic:** BSB-25 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **the builder to package the skill at my run's pinned commit into a content-addressed bundle and reuse that bundle when the same commit is packaged again**, so that **repeated runs start quickly and always execute byte-identical skill content**.

### Acceptance Criteria

Scenario: The first preparation of a commit packs and stores one bundle
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", state "preparing" and preparation_error NULL, an empty "skill_bundles" table, a builder object store whose PutObject counter is 0 and which holds no object at "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", a catalog repository checkout of commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" whose skill folder "skills/sdlc-fix-bug-reproduce/" contains exactly "SKILL.md", "verify.yaml", "references/example.md", "templates/output.md.tmpl" and "examples/sample.md", a deterministic skill packer that produces archive bytes with SHA-256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", and a builder clock reading "2026-11-16T11:00:10Z"
When the run packager processes run 21
Then the packager returns {"bundle_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", "s3_key": "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", "reused": false}, exactly one "skill_bundles" row exists with skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", skill "sdlc-fix-bug-reproduce", bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08" and s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", the object store received exactly one PutObject to that key with those archive bytes, the "runs" row id 21 still has state "preparing", and the packer recorded exactly the 5 skill-folder file paths above (nothing from "config/", "tools/" or another skill)

Scenario: Re-preparing the same commit reuses the stored bundle
Given a "runs" row id 22 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "preparing" and preparation_error NULL, a "skill_bundles" row for skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and skill "sdlc-fix-bug-reproduce" with bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08" and s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", the object store containing that object, a stub skill packer whose pack counter is 0, and an object store whose PutObject counter is 0
When the run packager processes run 22
Then the packager returns {"bundle_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", "s3_key": "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz", "reused": true}, the "skill_bundles" table still contains exactly one row, the stub skill packer's pack counter remains 0, the object store's PutObject counter remains 0, and run 22's state remains "preparing"

Scenario: A different commit is packaged into its own bundle
Given a "runs" row id 23 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "5e7a1c9d3b8f2a6e4d0c7b5a9f1e3d8c6b2a4f70", state "preparing" and preparation_error NULL, the existing "skill_bundles" row for skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and skill "sdlc-fix-bug-reproduce", a catalog repository checkout of commit "5e7a1c9d3b8f2a6e4d0c7b5a9f1e3d8c6b2a4f70" for the same skill folder, a deterministic skill packer that produces archive bytes with SHA-256 "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae" for that checkout and whose pack counter is 0, and no object at "bundles/5e7a1c9d3b8f2a6e4d0c7b5a9f1e3d8c6b2a4f70/sdlc-fix-bug-reproduce.tar.gz"
When the run packager processes run 23
Then a second "skill_bundles" row exists with skills_commit_sha "5e7a1c9d3b8f2a6e4d0c7b5a9f1e3d8c6b2a4f70", skill "sdlc-fix-bug-reproduce", bundle_sha256 "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae" and s3_key "bundles/5e7a1c9d3b8f2a6e4d0c7b5a9f1e3d8c6b2a4f70/sdlc-fix-bug-reproduce.tar.gz", the row for "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" is unchanged, and the deterministic skill packer's pack counter is 1

Scenario: A different skill at the same commit gets its own bundle
Given a "runs" row id 24 with project_id 7, build_id 8, skill "sdlc-fix-bug-triage", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "preparing" and preparation_error NULL, a "skill_bundles" row for skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and skill "sdlc-fix-bug-reproduce" with bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", a catalog repository checkout of that commit whose skill folder "skills/sdlc-fix-bug-triage/" contains "SKILL.md" and "verify.yaml", a deterministic skill packer that produces archive bytes with SHA-256 "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9" for that folder and whose pack counter is 0
When the run packager processes run 24
Then a new "skill_bundles" row exists with skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", skill "sdlc-fix-bug-triage", bundle_sha256 "fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9" and s3_key "bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-triage.tar.gz", the row for "sdlc-fix-bug-reproduce" is unchanged, and the deterministic skill packer's pack counter is 1

Scenario: The same commit packs to identical bytes twice
Given the catalog repository checkout of commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" for skill "sdlc-fix-bug-reproduce" is packaged twice in separate builder runs, with the "skill_bundles" table and the bundle object empty at the start of each run, and a deterministic skill packer that canonicalizes the archive
When the run packager processes commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" for skill "sdlc-fix-bug-reproduce" in each run
Then each pack returns bundle_sha256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", the two archive byte streams are identical byte for byte, and each archive lists its entries in the same order with identical paths, modes, sizes and a modification time of "1970-01-01T00:00:00Z"

Scenario: A pack failure leaves no bundle row
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "preparing" and preparation_error NULL, an empty "skill_bundles" table, an object store whose PutObject counter is 0, and a stub skill packer that exits with status 1 after writing no archive
When the run packager processes run 21
Then the "runs" row id 21 has state "preparation_failed" and preparation_error "The skill bundle could not be packed.", no "skill_bundles" row exists, the object store received 0 PutObject requests, and the packager returns {"state": "preparation_failed", "error": "The skill bundle could not be packed."}

Scenario: An object-store failure leaves no bundle row
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "preparing" and preparation_error NULL, an empty "skill_bundles" table, a deterministic skill packer that produces archive bytes with SHA-256 "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", and an object store that returns HTTP 503 for the PutObject request
When the run packager processes run 21
Then the "runs" row id 21 has state "preparation_failed" and preparation_error "The skill bundle could not be stored.", no "skill_bundles" row exists, and the packager returns {"state": "preparation_failed", "error": "The skill bundle could not be stored."}

### Covered requirements (traceability)
- FR-039
- FR-040
- NFR-009

### Out of scope
Resolving the skills branch to a commit and failing when it cannot be resolved (BSB-25-PENDING-1);
creating the run branch, recording the baseline and enforcing input-branch isolation
(BSB-25-PENDING-3); the packaging preflight for verifier lint, verifier self-test and the catalog
verifier range (BSB-30); the static scan of the bundle and its verdict (BSB-31); refusing a run on a
non-passing scan (BSB-27); presigning the bundle URL, passing `BB_SKILL_URL` and `BB_SKILL_SHA256`,
and executing the skill (BSB-26); verification (BSB-29); bundle retention and purge (BSB-34);
catalog submission packaging (BSB-36); the command-line run (BSB-37).

### Notes / dependencies
Depends on BSB-25-PENDING-1 for `runs.skills_commit_sha` and the `preparing` state; on BSB-19's
scaffold and naming rule for the skill folder, its `SKILL.md` and its `verify.yaml`; and on
BSB-23-PENDING-2 for the test-purpose `github` integration credential used to read the catalog
repository at the pinned commit. It depends on BSB-30 for the packaging preflight: the packer must
call that preflight's verifier lint, self-test and required-verifier-range checks before producing a
bundle and surface its refusal unchanged. FR-071 to FR-073 are BSB-30's requirements, not this
story's, and BSB-30 has no stories yet, so this is recorded as a cross-epic dependency for the
sequence stage.

The bundle is a tar archive of the skill's own catalog folder at the pinned commit — for run 21,
`skills/sdlc-fix-bug-reproduce/` with `SKILL.md`, `verify.yaml` and its `references/`, `templates/`
and `examples/` folders — and nothing else from the catalog repository. The packer canonicalizes it
so the same commit always produces the same bytes: entries in lexicographic path order, regular-file
mode 0644, directory mode 0755, uid/gid 0, modification time 0, and an uncompressed tar stream.
`bundle_sha256` is the SHA-256 of those archive bytes and `s3_key` is `bundles/` followed by the
skills commit SHA, a slash and the skill name with `.tar.gz`, for example
`bundles/4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d/sdlc-fix-bug-reproduce.tar.gz`, in the builder's
own object-storage bucket. The row is
written only after the object is stored, so a pack or upload failure leaves neither a row nor a
half-written bundle that a later run could reuse. The reuse key is `(skill, skills_commit_sha)`:
the same commit packaged for a different skill is a different bundle.

BSB-31-PENDING-1 reads the `skill_bundles` row by `(skill, skills_commit_sha)` and hands the
`bundle_sha256` and `s3_key` to the scanner, so a scan always reads the exact bundle the run will
use. BSB-26 presigns the stored object and passes `BB_SKILL_URL` and `BB_SKILL_SHA256` to the
container. BSB-27's re-run re-resolves the skills branch and packs the new commit; it never reuses a
bundle for a different commit. The data model already names `skill_bundles` (ADR SK-001 section 9);
this story does not add a column.

---

## STORY: BSB-25-PENDING-3

**Title:** Run against my test branch without ever changing it
**Epic:** BSB-25 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-6, MVP

### Story
As a **skill author who is a project member**, I want **the builder to create the run's own output branch from my input branch's head, record that head as the baseline, and refuse any write to the input branch**, so that **the skill's changes land only on a branch I can inspect and my test data is never overwritten**.

### Acceptance Criteria

Scenario: The run branch is created from the input head and the baseline is recorded
Given a "runs" row id 21 with project_id 7, user_id 42, build_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, state "preparing" and preparation_error NULL, the source-control integration 3 with project_id 7, kind "github", config {"repository": "saraavrnd/skill-builder-sandbox", "base_branch": "main", "test_only": true} and secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at that path, a stub source-control provider in which repository "saraavrnd/skill-builder-sandbox" has branch "test/atlas/bug-42" at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" and has no ref "refs/heads/skilltest/21", and a builder clock reading "2026-11-16T11:00:20Z"
When the run-branch preparer processes run 21
Then the stub source-control provider received exactly one branch-creation request for repository "saraavrnd/skill-builder-sandbox" and ref "refs/heads/skilltest/21" at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" authenticated with "ghp-test-token-7a1d", the "runs" row id 21 has run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", state "prepared" and preparation_error NULL, the stub source-control provider received 0 ref-update and 0 commit requests targeting "refs/heads/test/atlas/bug-42", and the preparer returns {"run_branch": "skilltest/21", "baseline_sha": "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", "state": "prepared"}

Scenario: A branch that moves after the baseline is read does not change the run's start point
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, state "preparing" and preparation_error NULL, the source-control integration 3 for project 7 with secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at that path, and a stub source-control provider in which branch "test/atlas/bug-42" is at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" when the preparer resolves it and at commit "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1" before the branch-creation request is made
When the run-branch preparer processes run 21
Then the branch-creation request names commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", the "runs" row id 21 has baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" and run_branch "skilltest/21", and the provider recorded no branch-creation request at commit "c4a8e0f1b3d6a2c5e7f9b1d4a6c8e0f2b5d7a9c1"

Scenario: An input branch that no longer exists fails preparation
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, state "preparing" and preparation_error NULL, the source-control integration 3 for project 7 with secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at that path, and a stub source-control provider in which repository "saraavrnd/skill-builder-sandbox" has no branch "test/atlas/bug-42"
When the run-branch preparer processes run 21
Then the "runs" row id 21 has state "preparation_failed", preparation_error "The selected input branch was not found in the sandbox repository.", run_branch NULL and baseline_sha NULL, the stub source-control provider received 0 branch-creation requests, and no ref "refs/heads/skilltest/21" exists

Scenario: A run branch that cannot be created fails preparation without touching the input branch
Given a "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, state "preparing" and preparation_error NULL, the source-control integration 3 for project 7 with secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at that path, a stub source-control provider in which branch "test/atlas/bug-42" is at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" and that returns HTTP 503 "Service Unavailable" for the branch-creation request, and a provider counter for ref updates and commits targeting "refs/heads/test/atlas/bug-42" that is 0
When the run-branch preparer processes run 21
Then the "runs" row id 21 has state "preparation_failed", preparation_error "The run branch could not be created.", run_branch NULL and baseline_sha NULL, the provider's ref-update and commit counters for "refs/heads/test/atlas/bug-42" remain 0, and branch "test/atlas/bug-42" still points at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e"

Scenario: A write aimed at the input branch is refused
Given a prepared "runs" row id 21 with project_id 7, skill "sdlc-fix-bug-reproduce", input_branch "test/atlas/bug-42", run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", state "prepared" and preparation_error NULL, and a stub source-control provider that records every ref-update and commit request and whose ref "refs/heads/test/atlas/bug-42" points at "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e"
When the run's source-control writer is asked to commit a file change "bugfix.md" with message "Apply the reproduced fix" to ref "refs/heads/test/atlas/bug-42", and then is asked to commit the same change with the same message to ref "refs/heads/skilltest/21"
Then the first write is refused with the message "A run cannot write to its input branch.", the provider records 0 ref-update and 0 commit requests for "refs/heads/test/atlas/bug-42", the provider's ref "refs/heads/test/atlas/bug-42" still points at "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", and the second write is accepted and recorded once for "refs/heads/skilltest/21"

Scenario: A 5 MB skill bundle is prepared within 60 seconds
Given a "runs" row id 21 with project_id 7, user_id 42, build_id 7, skill "sdlc-fix-bug-reproduce", skills_ref "build/sdlc-fix-bug-reproduce", skills_commit_sha NULL, input_branch "test/atlas/bug-42", run_branch NULL, baseline_sha NULL, state "requested" and preparation_error NULL, an empty "skill_bundles" table, a catalog repository checkout of commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" whose skill folder "skills/sdlc-fix-bug-reproduce/" totals 5,000,000 bytes, the source-control integration 3 for project 7 with secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at that path, a stub source-control provider in which branch "build/sdlc-fix-bug-reproduce" is at commit "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", branch "test/atlas/bug-42" is at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e" and ref "refs/heads/skilltest/21" does not exist, a deterministic skill packer that takes 35 seconds for that folder, an object store whose PutObject takes 20 seconds, the builder's branch-resolution and branch-creation steps taking 4 seconds in total, a builder clock reading "2026-11-16T11:00:00Z" when preparation starts, and a model-endpoint stub whose request counter is 0
When the builder prepares run 21 end to end with the resolver, the packager and the branch preparer
Then the "runs" row id 21 has skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", run_branch "skilltest/21", baseline_sha "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", state "prepared" and preparation_error NULL, a "skill_bundles" row exists for skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and skill "sdlc-fix-bug-reproduce", the provider's ref "refs/heads/skilltest/21" exists at commit "9b2e7c4a1d6f0b3e8c5a2f9d4b7e1c6a3f8d0b5e", the builder clock reads "2026-11-16T11:00:59Z" when preparation completes, and the model-endpoint stub received 0 requests

### Covered requirements (traceability)
- FR-041
- FR-042
- FR-043
- NFR-001

### Out of scope
Resolving the skills branch and freezing `runs.skills_commit_sha` (BSB-25-PENDING-1); packing
the bundle and reusing it (BSB-25-PENDING-2); the packaging preflight (BSB-30); the static scan
(BSB-31) and the run refusal when it does not pass (BSB-27); executing the skill, producing commits
on the output branch and the run page's progress and logs (BSB-26); verification with the baseline
and the final verdict (BSB-29); the input-to-output diff and the rest of the run report (BSB-33);
re-running and chaining a prior output branch as a later input (BSB-27); Jira fixture seeding
(BSB-28); deleting or garbage-collecting run branches (not assigned by the PRD); the command-line
run (BSB-37).

### Notes / dependencies
Depends on BSB-25-PENDING-1 for `runs.skills_commit_sha`; on BSB-25-PENDING-2 for the
`skill_bundles` row at that SHA; on BSB-24-PENDING-1 for `runs.input_branch` and the accepted run;
and on BSB-23-PENDING-2 for the test-purpose `github` integration whose sandbox `config.repository`
is the repository that holds the input branch. The output branch and the baseline are created with
that integration credential. Preparation is a background step acting on an already-authorized run,
so it adds no membership check of its own.

This story owns `runs.run_branch`, `runs.baseline_sha` and the isolation rule. `run_branch` is
`skilltest/` followed by the run id — for run 21, `skilltest/21` (ADR SK-001 section 5) — created
through the source-control provider from the input branch's head; `baseline_sha` is that head SHA. The data-model stage must add
`runs.baseline_sha`; ADR SK-001 section 9 does not list it. The baseline is what BSB-29 passes to
the shared verification layer for `must_change` and precondition checks, and what BSB-33's diff
uses. The input branch is read-only: the run's source-control writer refuses any write whose target
ref equals `runs.input_branch` with "A run cannot write to its input branch.", and every run-time
write target is `runs.run_branch`. BSB-26 must use that writer for every commit it makes; BSB-27's
chaining uses a prior run's `run_branch` as a later run's `input_branch` and still creates a new
output branch and a new baseline.

The preparer resolves the input head once, records it, and creates the run branch at that recorded
SHA, so an input branch that moves between the read and the branch-creation call cannot change the
run's start point. A `preparation_failed` run is not retried in place: it is terminal for this epic
and a later attempt is a new run (BSB-27's re-run), so the preparer does not have to adopt a
pre-existing `refs/heads/skilltest/21` left by a failed attempt. All preparation failures store their
exact message in `runs.preparation_error` and leave `runs.run_branch` and `runs.baseline_sha` NULL, as
the failure scenarios assert.

NFR-001 is measured on the end-to-end non-model preparation — resolver, packer and branch preparer —
for a skill folder of 5,000,000 bytes. No model call is part of preparation; the model-endpoint stub
must record 0 requests. BSB-27's preflight, static scan and execution run after this story has set
`prepared`; BSB-37's command line uses the same preparation step.

---

*Generated by `sdlc-plan-stories-write`. Coverage: FR-038, FR-039, FR-040, FR-041, FR-042, FR-043,
NFR-001 and NFR-009 all covered. Next steps: `sdlc-plan-epic-review` reviews the set on a different
model family; then `sdlc-plan-epic-sequence` orders the stories and `sdlc-tracker-sync` publishes
them to Jira.*
