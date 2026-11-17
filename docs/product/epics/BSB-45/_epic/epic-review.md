# Epic Review — BSB-45: Run setup & skill packaging

**Verdict:** ESCALATE · **Date:** 2026-11-17 · **Stories reviewed:** BSB-45-PENDING-1, BSB-45-PENDING-2, BSB-45-PENDING-3, BSB-45-PENDING-4, BSB-45-PENDING-5, BSB-45-PENDING-6

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-45/_epic/epic-review.md`.

## Context loaded

- **Requested work item.** `SkillBuilder-2` could not be retrieved. The read-only Jira REST API
  returns HTTP 404 ("Issue does not exist or you do not have permission to see it"); the site's
  projects are BEEM, BSB, EX, GRAP and LNPRTL, with no `SkillBuilder` project. The Atlassian MCP
  server configured in `.mcp.json` was not exposed as a tool in this session (`claude mcp list`
  reports it skipped), so no Atlassian MCP call was possible. This matches the input note already
  recorded at `docs/product/epics/BSB-45/_epic/stories.md:250–260`, and `docs/product/PRD.md` §8.
  The placeholder contributes no scope; the review covers the epic whose stories were written in
  this run.
- **Epic under review.** BSB-45, "Run setup & skill packaging" (Jira fetched read-only: status To Do,
  labels FA-6 and MVP; description matches `docs/product/epics.md:584–669`). Its stories were written
  by the preceding `sdlc-plan-stories-write` step (commit `c9d0baf`), and it was the only written
  epic with no `_epic/epic-review.md` before this review. The other candidate was BSB-44, which
  already has a review; its findings are used here only as cross-epic input.
- **Stories.** All six, from `docs/product/epics/BSB-45/_epic/stories.md` and
  `docs/product/epics/BSB-45/_epic/story-map.json`. The epic covers FR-037–FR-043, FR-145–FR-150,
  NFR-001 and NFR-009.
- **Requirement and scope sources.** `docs/product/PRD.md` §4, §5 (FA-6), §6 (all 15 requirements),
  §7 (NFR-001, NFR-004, NFR-006, NFR-009 in addition to the inherited NFR-002/NFR-003), §8
  ("External prerequisites", "Secrets", "One skill per run", "Test data");
  `docs/product/epics.md:584–669` (BSB-45), `:882` (BSB-48), `:1001–1043` (BSB-50),
  `:1070–1135` (BSB-51); `docs/product/epic-map.json` (`BSB-45` and `BSB-44` entries).
- **Design input.** No `architecture.md`, `data-model.md`, `api-contracts.md` or `ui-conventions.md`
  exists in this repository (no project-level `AGENTS.md`/`CLAUDE.md` either). The committed design
  reference is `docs/adr/SK-001-skill-builder.md`: §1 (the builder lives in `bheembhai-skills`;
  `tools/build.py` packs the catalog), §1a (builds on `build/<skill>`), §4 (integrations and
  credentials), §5 (run preparation, branches, baseline), §9 (data model: `skill_bundles`, `runs`).
  The current `tools/build.py` in this repository was read as the packer's actual interface.
- **Sibling epics checked for the shared contract.** BSB-39 (accounts, gate, fixture database),
  BSB-41 (catalog fixture, `main`, build branches), BSB-42 (build head and edit commits), BSB-43
  (projects, membership, `can_start_run`, the start-run link), BSB-44 (integrations, secret refs,
  `test_purpose`, redaction; its epic review), BSB-48/BSB-50/BSB-51 epic entries. BSB-48, BSB-50
  and BSB-51 have no stories yet; BSB-48 and BSB-50 consume FA-6's baseline, and BSB-51's packaging
  gates are called by BSB-45-PENDING-4.
- **Not loaded.** No `docs/product/epic-sequence.md` or `.json` exists, so relative epic build order
  could not be checked. No Jira issue links or sub-tasks exist for BSB-45.

## Findings

### Finding 1 — Cross-story contract hole: no defined behavior when the project has no `github` integration
- **Severity:** Blocking
- **Stories touched:** BSB-45-PENDING-1 (form/branch listing), BSB-45-PENDING-3 (the
  `prj_K9pL3wN6zB` scenario), BSB-45-PENDING-6 (branch creation); cross-epic BSB-44.
- **Evidence:**
  - `stories.md:19–25` says this epic reads BSB-44's `github` and `ai_model` rows and the
    `skill-builder/{project_id}/github` credential, but never says what happens when the `github`
    row is absent.
  - `stories.md:59–67`: only `prj_H5mQ2rT8vX` has the two integration rows; `prj_K9pL3wN6zB` "has no
    integration row unless a scenario's `Given` says so."
  - `stories.md:169–191`: the start error table has `source_control_unavailable` (503) for "GitHub
    API/branch creation unavailable", but no error for a missing source-control integration.
  - `stories.md:272–275`: the form's input-branch select is populated from the project's sandbox
    repository using that project's source-control credential. With no `github` row there is no
    repository and no credential, so the form cannot render as specified.
  - `stories.md:400–403`: the no-model-profile scenario uses `prj_K9pL3wN6zB`, whose `Given` removes
    only the `ai_model` row. Per `stories.md:64` it has no `github` row either, so the expected
    `model_profile_missing` depends on an unstated validation precedence between the missing model
    profile and the missing source-control integration.
  - BSB-43 creates a project and its membership rows only (`docs/product/epics/BSB-43/_epic/stories.md:33–47`)
    and always shows the Start run link to a member (`:282`, `:287`), so "member opens the run form
    on a project with no integrations" is a normal path, not an exotic edge.
- **What is missing/ambiguous/contradictory:** There is no defined response for `GET
  /projects/{id}/runs/new` or `POST /api/projects/{id}/runs` when the project has no `github`
  integration, no stated validation order, and no error name/status for the condition. Two
  implementations can legitimately return different errors, and the P3 scenario as written cannot
  pass without one.
- **Question (if a person must decide):** What should the run form and the start route do when the
  project has no `github` integration — a new 422 (for example
  `{"error":"source_control_integration_missing"}`), the existing 503 `source_control_unavailable`,
  or a form-level disabled state with a link to project settings? And which check runs first when
  both `github` and `ai_model` are missing? (also listed under Open questions)
- **Proposed change:** Add the chosen error and status to the start contract, a precedence sentence
  (for example: session → group → project → membership → `github` integration → `ai_model`
  integration → request fields), a P1 form AC for a project with no `github` integration, and a P6
  start AC. Fix P3's scenario so `prj_K9pL3wN6zB` has the `github` row (`int_Gh7kL2pQ9r`) and only
  the model profile is missing, or change its expected error to the chosen missing-integration
  error.

### Finding 2 — Cross-story contract hole: the default workflow/step cannot resolve on `main` and diverges from SK-001 §5
- **Severity:** Blocking
- **Stories touched:** BSB-45-PENDING-1 (the form defaults to `main`), BSB-45-PENDING-2 (the
  default rule and its notes); conflict with `docs/adr/SK-001-skill-builder.md` §5.
- **Evidence:**
  - `stories.md:144–146`: `workflow` is optional and defaults to "the workflow whose `start` step's
    `skill` equals `skill`"; `step` defaults to that step.
  - `stories.md:169–191`: the only workflow error is `workflow_not_found` for a supplied workflow
    that is not defined. There is no error for "no workflow exists" and no statement that
    `workflow`/`step` may be null.
  - `stories.md:74–77`: `main` contains only the three skill folders; `config/sdlc-wf-*.yaml`
    appears only on `build/...` and `test/...`. `main` therefore has no workflow for any fixture
    skill.
  - `stories.md:272–275` and `:316`: the form initially selects `main` in both branch controls and
    lists the three skills on that commit. Selecting a skill on `main` and submitting with omitted
    `workflow` has no defined result.
  - The only form/default ACs (`stories.md:330–337`) run on `test/saraav/research`, where `config/`
    happens to exist.
  - `docs/adr/SK-001-skill-builder.md:216–218` defines the default as "a workflow in the skills
    branch's `config/` that uses this skill", not specifically the workflow whose `start` step uses
    it. The P2 Notes (`stories.md:372`) repeat the narrower start-step rule.
- **What is missing/ambiguous/contradictory:** (a) No outcome when the resolved commit has no
  matching workflow — exactly the form's initial `main` state. (b) The story's rule silently excludes
  a workflow that uses the skill at a non-start step, which SK-001 §5 allows. (c) No statement
  whether `workflow`/`step` may be null in `runs.context`, so the "optional" fields are not actually
  optional on a commit without `config/`.
- **Question (if a person must decide):** When no workflow matches, does an omitted `workflow`
  return a new 422 (for example `workflow_required`), or is the run allowed with a null
  workflow/step? Should the default follow SK-001 §5 (any workflow that uses the skill) or the
  story's start-step-only rule? (also listed under Open questions)
- **Proposed change:** Align the default with SK-001 §5, or record why the epic narrows it. Add a
  `workflow_required` (or explicitly null-context) rule to the contract and to P2. Add a P1 or P2
  form/start AC for `main` (no `config/`), including whether the form disables Start and what
  message it shows. Update the P1 Notes, P2 Notes and the preface contract together.

### Finding 3 — Epic-level traceability: NFR-006 test-purpose enforcement is unowned
- **Severity:** Blocking
- **Stories touched:** BSB-45-PENDING-1 (reads the project's integrations), BSB-45-PENDING-6 (uses
  the source-control credential); cross-epic BSB-44 (its Finding 1 and Open question 1).
- **Evidence:**
  - `docs/product/PRD.md:259` (NFR-006): "Runs use only test-purpose Jira, source-control and model
    credentials."
  - `stories.md:19–25` says this epic reads both integration rows and their credentials. No BSB-45
    story checks a `test_purpose` property, and no story or Notes line states a dependency on
    BSB-44's warning rather than enforcement.
  - `docs/product/epic-map.json`: BSB-45's `requirement_ids` omit NFR-006; BSB-44 carries it. The
    BSB-45 coverage summary (`stories.md:3–5`, `:239–248`) likewise omits it.
  - `docs/product/epics/BSB-44/_epic/stories.md:459` puts "Refusing, blocking or gating a save or a
    run on an overlap" out of scope, while `:462` says "FA-6 (BSB-45) may consume `test_purpose`
    when preparing a run but does not change this contract." BSB-45 never mentions
    `test_purpose`. BSB-44's review
    (`docs/product/epics/BSB-44/_epic/epic-review.md:58–107`, Open question `:297–302`) records
    that no epic owns enforcement and that, if enforcement is intended, BSB-45 must carry NFR-006
    and add the run gate.
  - `docs/product/PRD.md:353` ("Test data") says test-purpose credentials are used and that a
    source-control integration pointing at a platform project "triggers a warning" — a warning-only
    reading of the same requirement.
- **What is missing/ambiguous/contradictory:** Two readings of NFR-006 remain open: externally
  assured plus a warning (BSB-44's behavior), or enforced at run start (a BSB-45 gate). BSB-45 —
  the epic that actually starts runs and reads the credentials — takes neither position, and the
  requirement mapping says BSB-44 covers it. The same holds for the NFR-004 hand-off from BSB-44's
  Finding 2: BSB-45 reads credentials at request time but never says its logs and error bodies go
  through BSB-44's redaction layer.
- **Question (if a person must decide):** Does a run with a `github` (or `ai_model`) integration
  whose `test_purpose` is false (or unknown) get refused at start, and with what error? Or is
  PRD §8's "Test data" paragraph the intended reading, making BSB-44's warning the only behavior
  and NFR-006 externally assured? This is the same question as BSB-44's Open question 1, now asked
  from the enforcing side. (also listed under Open questions)
- **Proposed change:** If enforcement: add NFR-006 to BSB-45's scope and traceability (P1's
  requirement list, the coverage summary, `story-map.json`, and — via the planning pass — the
  epic map), add a P1 AC for false/unknown `test_purpose` with the chosen error, and reference
  BSB-44's read model. If warning-only: add a preface sentence that test-purpose selection is an
  external prerequisite, that BSB-45 does not gate on it, and that BSB-44's warning is the only
  behavior; do not claim enforcement. Either way, add a sentence that run-preparation logs and
  error bodies go through BSB-44's redaction layer and never contain the credential value (NFR-004).

### Finding 4 — Cross-story architecture fit: `runs.baseline_sha` is required by SK-001 §5 but absent from §9
- **Severity:** Blocking
- **Stories touched:** BSB-45-PENDING-6 (defines and asserts it); cross-epic BSB-48 and BSB-50
  (consume it).
- **Evidence:**
  - `docs/adr/SK-001-skill-builder.md:232–233`: "create a new run branch … and record that head SHA
    as the baseline."
  - `docs/adr/SK-001-skill-builder.md:354–355`: the `runs` table columns include `skills_ref`,
    `skills_commit_sha`, `input_branch`, `run_branch`, `context`, `model_profile_id`, `tier`,
    `state`, … but no `baseline`/`baseline_sha`.
  - `stories.md:200–204` acknowledges the omission and invents the storage: "§9's `runs` table lists
    no explicit baseline column, so this epic records it in `runs.baseline_sha`. If the architecture
    pins a different column name, only that name changes."
  - `stories.md:537` asserts `baseline_sha` on the response and the `runs` row; P6's Notes
    (`stories.md:568`) repeat the assumption.
  - `docs/product/epics.md:882` (BSB-48) depends on FA-6's "prepared bundle, run branch, baseline";
    `docs/product/epics.md:1001`, `:1013`, `:1043` (BSB-50) pass the baseline to the verifier
    (FR-064).
- **What is missing/ambiguous/contradictory:** The design requires a baseline but gives it no
  storage. The stories choose a column name, which is inventing design at the story stage. This is
  not a story-wording fix: the data model must say whether the baseline is a new `runs` column (and
  its exact name/type/nullability) or is carried in `runs.context` and derived. BSB-48 and BSB-50
  will read this field, so the name is cross-epic.
- **Question (if a person must decide):** Should `baseline_sha` be a new `runs` column, and if so is
  that the final name? Or is the baseline stored in `runs.context` (or not stored, derived from the
  input branch at read time)? (also listed under Open questions)
- **Proposed change:** `sdlc-arch-design` (amend) adds the baseline field to the data model and
  SK-001 §9 with its type and nullability (or states the `context` storage explicitly). Then
  `sdlc-plan-stories-write` updates the preface, P6 and any `runs`-row assertions to the chosen
  name. No behavior change is expected beyond the field name.

### Finding 5 — Cross-story dependency reciprocity: `can_start_run` reuse is one-sided (Advisory)
- **Severity:** Advisory
- **Stories touched:** BSB-45-PENDING-1; cross-epic BSB-43-PENDING-4.
- **Evidence:** BSB-43-PENDING-4's Notes (`docs/product/epics/BSB-43/_epic/stories.md:316`) say
  "BSB-45 must call the same project-membership decision this story defines … rather than
  re-implementing the check." BSB-45's preface (`stories.md:7–18`) names `can_start_run` in the
  prerequisite list, but P1's Notes (`stories.md:316`) say only that the story depends on FA-4
  for the member/owner distinction; they do not repeat the reuse obligation. P1's ACs pin the
  behavior (member 201, non-member 403), so there is no test gap — only an implementation-risk gap.
- **What is missing/ambiguous/contradictory:** Nothing contradictory; the dependency note is
  incomplete on the side that implements the check.
- **Question (if a person must decide):** None.
- **Proposed change:** Add one sentence to P1's Notes (and the preface) that the membership decision
  is BSB-43's `can_start_run` and must be called, not re-implemented.

### Finding 6 — Cross-epic requirement coverage: FR-149's "choice of model profile" is a one-option select (Advisory)
- **Severity:** Advisory
- **Stories touched:** BSB-45-PENDING-3; cross-epic BSB-44.
- **Evidence:** `docs/product/PRD.md:226` (FR-149) speaks of choosing "the model profile". BSB-44
  permits at most one `integrations` row per `(project_id, kind)` (`stories.md:65–67`; BSB-44's
  data model), so P3's form AC (`stories.md:386–388`) asserts a model-profile select with exactly
  one option (`int_Md4xN8sT2v`). P3's Notes (`stories.md:428`) explain the rule.
- **What is missing/ambiguous/contradictory:** FR-149 is satisfied only in the degenerate sense of
  confirming the one profile; there is no "choice". If the requirement intends multiple profiles
  per project, BSB-44's uniqueness rule — not this story — is what must change. The epic should
  record the intended reading so the apparent gap is not rediscovered later.
- **Question (if a person must decide):** Is one model profile per project intended, with FR-149
  satisfied by confirming it and choosing a tier? Or are multiple profiles required? (also listed
  under Open questions)
- **Proposed change:** State the intended reading in P3's Notes and the preface; if multiple
  profiles are required, raise it against BSB-44's data model rather than changing P3 alone.

### Finding 7 — Fixture drift on `build/sdlc-research-summarise` (Advisory)
- **Severity:** Advisory
- **Stories touched:** BSB-45-PENDING-3 and the epic preface's fixture table; cross-epic BSB-41 and
  BSB-42.
- **Evidence:** `stories.md:69` says "The repository is BSB-41's fixture", but `stories.md:75` gives
  `build/sdlc-research-summarise` a fixed head `9b2f4d6a8c0e2f5a7d1b3c6e8f0a2c4d6e8f1a3b` and adds
  `config/sdlc-wf-research.yaml`. BSB-41 defines that branch as starting from `main` at
  `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`
  (`docs/product/epics/BSB-41/_epic/stories.md:26`, `:204–206`), and BSB-42 advances it only through
  `SKILL.md` edits to a dynamic commit `D` (`docs/product/epics/BSB-42/_epic/stories.md:155–182`,
  `:228`). Neither sibling defines a config-adding commit or the fixed SHA `9b2f…`.
- **What is missing/ambiguous/contradictory:** If BSB-41/BSB-42 and BSB-45 run against the same
  fixture snapshot, their `git rev-parse` assertions can disagree: BSB-42 expects the build head to
  be `4f2a…` or the commit its own edit produced, while BSB-45 expects `9b2f…`. The fixture owner
  for the extra commit is unstated.
- **Question (if a person must decide):** Is BSB-45 using a distinct fixture snapshot whose
  `build/sdlc-research-summarise` includes `config/`, or should it use BSB-41/42's head and move the
  test workflows to the `test/` branches only?
- **Proposed change:** Either define the config-adding commit in BSB-41/BSB-42's shared fixture and
  reference it from BSB-45, or state explicitly that BSB-45's fixture snapshot is a later,
  separate copy and give the commit that adds `config/`.

### Finding 8 — Shared-tool contract: a per-skill pack mode of `tools/build.py` is assumed, not owned (Advisory)
- **Severity:** Advisory
- **Stories touched:** BSB-45-PENDING-4 (packaging), the preface bundle contract; cross-epic BSB-51
  (release packaging uses the same tool).
- **Evidence:** `stories.md:206–211` requires packing `skills/{skill}/` at commit `S` "with
  `tools/build.py`". The current `tools/build.py` exposes only `sync` and `pack --version`
  (`tools/build.py:1–7`, `:121–133`); `pack()` always archives the whole catalog into
  `dist/catalog.tgz` (`tools/build.py:82–117`). There is no per-skill-at-a-commit mode and no
  `BB_PACK_LOG` hook. P4's Out of scope (`stories.md:477`) excludes "`tools/build.py`'s release
  packaging path" but not the per-skill mode, and no story owns adding it.
- **What is missing/ambiguous/contradictory:** The bundle contract depends on a tool capability that
  does not exist in the committed repository. The per-skill mode could be a new CLI/library entry
  point in the catalog tool, a wrapper in the builder, or a documented subset of `pack()`; the epic
  does not choose, so P4 can be implemented without touching the tool and fail the "same tool as
  release" intent.
- **Question (if a person must decide):** Which layer owns per-skill packing — a new
  `tools/build.py` mode used by both the builder and the release path, or a builder-side wrapper
  around `content_sha256`/`pack()`? And is `BB_PACK_LOG` a fixture-only hook?
- **Proposed change:** Pin the packer interface (for example a `pack --skill <name> --git-sha <S>`
  mode that produces `bundles/{sha}.tar.zst`, or a documented library function), state that P4 owns
  the catalog-tool change (and BSB-51 consumes it), and mark `BB_PACK_LOG` as a fixture-only logging
  hook rather than a product requirement.

### Finding 9 — Failure atomicity after the run branch is created is undefined (Advisory)
- **Severity:** Advisory
- **Stories touched:** BSB-45-PENDING-6; the preface failure contract.
- **Evidence:** `stories.md:163–164` says a failure "changes no `runs` row; a content-addressed
  bundle already written to the cache may remain" — enumerating the bundle as the only permitted
  residue. P6 creates `skilltest/{run_id}` (`stories.md:533–537`) and then the `runs` row. P6's
  failure AC covers branch-creation failure (`stories.md:548–551`) but not a failure after the
  branch exists (for example the `runs` insert failing). P6's Out of scope (`stories.md:565`) puts
  deleting the run branch and retention outside this epic.
- **What is missing/ambiguous/contradictory:** If the branch is created and a later preparation step
  fails, the branch remains with no run. The preface's residue list omits the branch, so it is
  unclear whether this is allowed or must be cleaned up. Two implementations can differ, and a
  leftover `skilltest/*` branch is observable by later runs (the input-branch rejection rule).
- **Question (if a person must decide):** On a failure after `skilltest/{run_id}` is created, is the
  branch deleted before the error response, or left in place? If left, is that acceptable residue
  like the cached bundle?
- **Proposed change:** Add one sentence to the preface and a P6 AC stating the chosen behavior:
  either the builder deletes the just-created run branch on any later failure (and the response is
  the error), or the branch may remain and the preface lists it as permitted residue. If cleanup is
  deliberately out of scope, say so explicitly rather than leaving the silence.

## Open questions

1. **No `github` integration (Finding 1).** What do the run form and `POST /api/projects/{id}/runs`
   return when the project has no `github` integration, and which integration check runs first when
   both `github` and `ai_model` are missing? A new 422, the existing 503, or a disabled form?
2. **Default workflow (Finding 2).** When the resolved commit has no workflow whose start step uses
   the selected skill (the form's initial `main` state), is the run refused (`workflow_required`) or
   allowed with a null workflow/step? And is the default SK-001 §5's "any workflow that uses the
   skill", or the story's start-step-only rule?
3. **NFR-006 (Finding 3).** Does BSB-45 refuse a run when the project's source-control or model
   integration is not test-purpose, and with what error? Or is PRD §8's "Test data" warning the
   intended, warning-only behavior? This repeats BSB-44's Open question 1 from the enforcement side.
4. **Baseline storage (Finding 4).** `sdlc-arch-design` must pin whether the baseline is a new
   `runs` column (name/type/nullability) or lives in `runs.context`; BSB-48 and BSB-50 depend on the
   answer.
5. **FR-149 (Finding 6).** Is one model profile per project intended (FR-149 satisfied by confirming
   it and choosing a tier), or are multiple profiles required — which would change BSB-44's data
   model, not just P3?

## Proposed changes

### BSB-45 preface / shared contract (`stories.md:133–215`)
- Add the chosen no-`github`-integration error/status and the validation precedence (Finding 1).
- Align the default workflow rule with SK-001 §5 or record the narrowing; add the no-workflow rule
  (Finding 2).
- Add the NFR-006 position and the NFR-004 redaction hand-off, or state that both remain BSB-44's
  and are external prerequisites (Finding 3).
- Mark the baseline field as pending the architecture amendment (Finding 4), not as a story-invented
  column.
- Correct or explicitly separate the `build/sdlc-research-summarise` fixture (Finding 7).
- Pin the per-skill packer interface and mark `BB_PACK_LOG` fixture-only (Finding 8).
- State the post-branch-creation failure behavior (Finding 9).

### BSB-45-PENDING-1 — Start a run with the chosen skill and branches
- Add a form AC for a project with no `github` integration and the chosen behavior (Finding 1).
- Add the missing-integration error and precedence to the start contract (Finding 1).
- Add the `main`-with-no-`config/` form/start behavior (Finding 2).
- Add the `can_start_run` reuse sentence to Notes (Finding 5).
- If NFR-006 enforcement is chosen, add the `test_purpose` gate and AC, and add NFR-006 to the
  story's requirement list and coverage summary (Finding 3).

### BSB-45-PENDING-2 — Choose the workflow and step context with optional hand-off
- Apply the default-rule change: SK-001 §5 wording, the `workflow_required`/null-context rule, and
  the `main` case (Finding 2).
- Update Notes at `stories.md:372` to match.

### BSB-45-PENDING-3 — Choose the model profile and tier
- Fix the `prj_K9pL3wN6zB` Given so the project has the `github` row and only the model profile is
  missing, or change its expected error (Finding 1).
- Record the FR-149 one-profile reading in Notes (Finding 6).

### BSB-45-PENDING-4 — Pin the skills commit and package a content-addressed bundle
- Pin the per-skill packer interface and state that this story owns the catalog-tool change; mark
  `BB_PACK_LOG` fixture-only (Finding 8).

### BSB-45-PENDING-5 — Reuse an existing bundle for the same skills commit
- No change.

### BSB-45-PENDING-6 — Create the run branch, record the baseline and keep the input branch read-only
- Use the architecture-pinned baseline name/storage (Finding 4).
- Add the no-`github`-integration start AC (Finding 1).
- Add the post-branch-creation failure AC (Finding 9).
- If NFR-006 enforcement is chosen, add the gate/error AC (Finding 3).

### Mapping files
- `story-map.json`: add NFR-006 to P1 only if enforcement is chosen.
- `docs/product/epic-map.json`: add NFR-006 to BSB-45's `requirement_ids` only if enforcement is
  chosen; that is a planning-pass change, not an authoring change.
- No other story-map assignment changes are proposed.

## Architecture impact

**Needs `sdlc-arch-design` (amend): one item.**

1. **`runs.baseline_sha` (Finding 4).** SK-001 §5 requires recording the input head as the baseline
   (`docs/adr/SK-001-skill-builder.md:232–233`), but §9's `runs` table has no baseline column
   (`:354–355`). BSB-45-PENDING-6 invents `runs.baseline_sha`, and BSB-48 (`docs/product/epics.md:882`)
   and BSB-50 (`:1001`, `:1013`, `:1043`) consume the value. The data model — or SK-001 §9 — must
   add the field (or state that the baseline lives in `runs.context` and how it is read). Until then
   the stories' field name is an unratified assumption. This is the reason the verdict is ESCALATE:
   it is not a story change the revise pass can settle.

**Not architecture conflicts, but cross-epic contract changes owned elsewhere:**
- The default-workflow rule (Finding 2) is a story-vs-ADR wording difference. It can be fixed in the
  story (narrow the rule and say why) or by amending SK-001 §5; the former needs no architecture
  change.
- FR-149 (Finding 6) becomes an architecture/data-model change only if multiple model profiles are
  required; then it is BSB-44's `(project_id, kind)` uniqueness rule that changes, not BSB-45's
  tables.
- The per-skill pack mode (Finding 8) is a tool interface gap, not a data-model conflict; once the
  interface is pinned it is a P4/BSB-51 change.
- The other findings use only entities SK-001 §9 already defines: `users`, `projects`,
  `project_members`, `integrations`, `skill_bundles`, `runs`. `skill_bundles`
  `(skills_commit_sha, skill)` uniqueness and the `runs.context` fields match §9 as written.

## Requirement coverage check

| Requirement | Story | Covered? | Note |
|-------------|-------|----------|------|
| FR-037 | P1 | Yes | Member starts a run (201, `runs` row); non-member 403; no session 401. BSB-43 owns the membership decision (Finding 5). |
| FR-038 | P4 (asserted in P1) | Yes | Pins `skills_commit_sha`; branch-move AC at P4. |
| FR-039 | P4 | Yes | `bundle_sha256`, `skill_bundles` row and S3 object. |
| FR-040 | P5 | Yes | Reuse, concurrency and corrupt-cache ACs. |
| FR-041 | P6 (asserted in P1) | Yes | `skilltest/{run_id}` created from the input head. |
| FR-042 | P6 | Yes, behaviorally | Baseline is recorded and asserted; its storage is Finding 4 (architecture). |
| FR-043 | P6 | Yes | Input branch unchanged; push refused by the fixture protection. |
| FR-145 | P1 | Yes | Skills-branch options in the form. |
| FR-146 | P1 | Yes | Input-branch options in the form. |
| FR-147 | P2 | Yes, with a hole | Workflow/step choices, default and mismatch ACs; the no-default/`main` case is Finding 2. |
| FR-148 | P2 | Yes | Both `reviewer_feedback` and `upstream_handoff` are accepted, recorded and validated. The PRD's "or" wording is exercised as "and"; this is a single-story wording question, not raised as an epic finding. |
| FR-149 | P3 | Yes, degenerate | The profile select has one option (Finding 6). |
| FR-150 | P3 | Yes | Tier select, skill default, `tier_required` and `tier_model_missing`. |
| NFR-001 | P6 | Yes | 5 MB bundle within 60 seconds, measured on the start request. |
| NFR-009 | P4 | Yes | Repeated packing yields byte-identical bundles. |
| NFR-006 | — | **No** | Not in BSB-45's mapped requirements; enforcement ownership unresolved (Finding 3). |
| NFR-004 | — (inherited) | Not stated | The redaction hand-off from BSB-44 is not repeated; expected to be inherited from BSB-44's layer (Finding 3 sub-point). |

- The requirement lists in the PRD (`docs/product/PRD.md:114–120`, `:222–227`, `:254`, `:262`),
  `story-map.json` and `docs/product/epic-map.json` agree for the 15 mapped requirements; there is
  no wording drift between the epic map, the story map and the PRD.
- No requirement is duplicated with a contradictory definition across stories: FR-038 is owned by
  P4 and merely asserted in P1; FR-041/FR-042 are owned by P6 and merely asserted in P1.
- The FR-037/FR-027 boundary is explicit: BSB-43 owns the project-membership decision; BSB-45 owns
  the run start. The only gap on that boundary is the one-sided note in Finding 5.
- NFR-006 is the sole mapped-requirement gap. It is a genuine cross-epic traceability gap, not a
  missing story: PRD §8's test-data paragraph may make it externally assured, but nothing in BSB-45
  says so.

## Dependency-note sanity check

- **Within the epic, reciprocal.** P2/P3/P4/P5/P6 each name P1 as their dependency; P1's Out of
  scope names all five downstream stories. P5 names P4 and P4's Out of scope names P5; P6 names P4
  and P5 and their Out of scope names P6. No cycle, no dangling story key.
- **Cross-epic, mostly reciprocal.** P1 names BSB-39/BSB-43/BSB-44; BSB-44's epic entry names
  FA-6/BSB-45, and BSB-43-PENDING-4 names BSB-45 (the `can_start_run` reuse — incomplete on the
  BSB-45 side, Finding 5). P4 names BSB-51 for FR-071–FR-073; BSB-51's epic entry names FA-6 as a
  dependency (the packaging path), so the interface is mutual even though BSB-51 has no stories yet.
- **Downstream consumers.** BSB-48 and BSB-50 depend on FA-6's "prepared bundle, run branch,
  baseline" (`docs/product/epics.md:882`, `:1001–1043`) and have no stories yet. Their dependency is
  recorded on their side; the baseline field they will read is the subject of Finding 4.
- **No missing or nonexistent keys.** Every cross-epic key named by these stories exists in
  `docs/product/epics.md` (BSB-39, -41, -42, -43, -44, -48, -50, -51, -57). BSB-49, BSB-47 and the
  FA-8/FA-11/FA-12 references are epic-level names, not story keys.
- **Order.** No `epic-sequence.md`/`.json` exists, so relative build order cannot be confirmed. The
  stories assume FA-1/FA-4/FA-5 are built before FA-6 and that FA-10B (BSB-51) is callable at run
  time; that is consistent with `docs/product/epics.md`, but it is an ordering assumption, not a
  checked sequence.
