# Epic Review — BSB-24: Run start & input selection

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-15 · **Stories reviewed:** BSB-24-PENDING-1, BSB-24-PENDING-2, BSB-24-PENDING-3, BSB-24-PENDING-4, BSB-24-PENDING-5

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-24/_epic/epic-review.md`.

## Context loaded

- **Target resolution.** The run's target was `SkillBuilder`. That is the product title of
  `docs/product/PRD.md`, not a Jira issue, as the BSB-24 `stories.md` header also records. The
  Atlassian MCP server was not connected in this session (no Jira tools were available), so the
  epic was resolved from disk. BSB-24 is the epic the most recent `sdlc-plan-stories-write` run wrote
  (commit `d5b31a5`), and it has no review yet. Its `stories.md` header says the epic was fetched
  read-only from Jira during decomposition and matches the BSB-24 section of `epics.md`. Nothing was
  read from or written to Jira in this pass.
- **All 5 BSB-24 stories**, from `docs/product/epics/BSB-24/_epic/stories.md` and
  `story-map.json`, the full set: PENDING-1 (start a run as a project member, FR-037), PENDING-2
  (skills and input branch, FR-145, FR-146), PENDING-3 (workflow and step, FR-147), PENDING-4
  (reviewer feedback / upstream handoff, FR-148) and PENDING-5 (model profile and tier, FR-149,
  FR-150). Also read the shared "Run-start contract" preamble: fixtures, `runs`-row contract,
  request-field table, options response, validation order, error table, and the cross-epic note on
  BSB-22's run-start fixture.
- `docs/product/epic-map.json`: BSB-24 → FR-037, FR-145, FR-146, FR-147, FR-148, FR-149, FR-150.
  Neighbouring entries read for ownership: BSB-22 (FR-023 to FR-028), BSB-23 (FR-029 to FR-036,
  FR-128, FR-129, NFR-004, NFR-006), BSB-25 (FR-038 to FR-043, NFR-001, NFR-009), BSB-26 (FR-044 to
  FR-049, FR-151, FR-152), BSB-27 (FR-050 to FR-057, NFR-007, NFR-008, NFR-019), BSB-38 (FR-130 to
  FR-137, NFR-012).
- `docs/product/PRD.md`: the FA-6 rows FR-037 to FR-043 and FR-145 to FR-150; neighbouring rows
  FR-029 to FR-036, FR-044 to FR-057, FR-130 to FR-137, FR-151, FR-152, FR-163; NFR-001 to NFR-019.
- `docs/product/epics.md`: the BSB-24 section (description, functional scope, edge cases,
  implementation guidance, Goal/DoD).
- `docs/adr/SK-001-skill-builder.md`: §3 (Cognito login and group gate), §4 (projects and
  integrations, GitHub token scope), §5 (a run: skills branch, input branch, optional context and
  its default, model profile and tier, turn and spend caps), §9 (`integrations`, `runs`,
  `skill_bundles` columns), and the v1 non-goals. The repo has no separate `architecture.md`,
  `data-model.md`, `api-contracts/` or `ui-conventions.md`; SK-001 §9 is the data model.
- Other epics' stories, only far enough to check cross-epic claims: BSB-22 `stories.md` (contract
  preamble and BSB-22-PENDING-4), BSB-22 `epic-review.md` and `revisions.md` (Open question 1 is
  still open), and BSB-18 `stories.md` (the gate scenarios and the authentication middleware note).
  BSB-23, BSB-25, BSB-26 and BSB-27 have no stories yet, so their scope was checked against
  `epic-map.json` and PRD wording only. No `sdlc-plan-epic-sequence` output exists yet.

## Findings

### Finding 1 — Cross-epic requirement duplication: BSB-24-PENDING-1 and BSB-22-PENDING-4 assert the same route with contradicting success bodies, while BSB-22's open question on who owns it is unanswered
- **Severity:** Blocking
- **Stories touched:** BSB-24-PENDING-1, BSB-24-PENDING-5, BSB-22-PENDING-4
- **Evidence:**
  - BSB-22-PENDING-4 (FR-027) has two 201 scenarios on `POST /api/projects/7/runs` with body
    exactly `{"skill":…,"skills_ref":…,"input_branch":"main"}` and a fixture where project `7` has
    only a `jira` integration.
  - BSB-24-PENDING-5 makes `model_profile_id` and `tier` required (422 `model_profile_required`,
    422 `tier_required`), and BSB-24-PENDING-2 refuses a project with no `github` integration (422
    `source_control_not_configured`). Under BSB-24's contract, both BSB-22-PENDING-4 success
    scenarios return 422, not 201.
  - BSB-24-PENDING-1 repeats BSB-22-PENDING-4's other scenarios: "A non-member cannot start a run"
    (403 `project_membership_required`) and "A run start against a missing project is refused"
    (404 `project_not_found`), with the same bodies, under FR-037 instead of FR-027.
  - BSB-24's contract preamble ("Cross-epic note — BSB-22's run-start fixture") sees the
    contradiction and says BSB-22-PENDING-4 "must" be re-pointed, but "This epic does not edit
    BSB-22's files". BSB-22's `revisions.md` lists Finding 1 / Open question 1 (how the membership
    check is split from the run-start route: (a) guard, (b) move, (c) keep both) as still open.
- **What is contradictory:** the same route is asserted by two epics with incompatible success
  bodies. The same 403/404 behaviour is owned twice, under two FRs. BSB-24's stories assume
  answer (c) to BSB-22's open question, but that question has not been answered. Until one
  answer applies to both epics, either BSB-22-PENDING-4 fails against BSB-24's implementation or
  BSB-24's validation contract must be weakened.
- **Question (a person must decide):** Answer BSB-22 Open question 1 once, for both epics. Should
  BSB-22-PENDING-4 become a reusable membership guard, so BSB-24-PENDING-1 owns every scenario on
  the run-start route and cites the guard (BSB-22 option (a), recommended)? Or should both stories
  keep run-start scenarios, with BSB-22-PENDING-4's bodies and fixture re-pointed to BSB-24's
  contract (option (c))?
- **Proposed change:**
  - If (a): BSB-24-PENDING-1 keeps its non-member and missing-project scenarios and adds a Notes
    line: "the 403/404 decision is BSB-22-PENDING-4's guard; this story asserts it at the route".
    BSB-24's cross-epic note changes from "BSB-22 must re-point its fixture" to "BSB-22-PENDING-4
    is the guard this route calls". BSB-22-PENDING-4 (BSB-22 revise pass) loses its 201
    scenarios, as BSB-22 option (a) describes.
  - If (c): no BSB-24 story change. BSB-22-PENDING-4 (BSB-22 revise pass) uses the `github` and
    `ai_model` fixture rows and adds `"model_profile_id":3,"tier":"high"` to its Ada and Grace
    bodies, as BSB-24's cross-epic note already describes. BSB-24-PENDING-1's Notes record that
    its 403/404 scenarios intentionally duplicate BSB-22-PENDING-4's.
  - Either way, BSB-24-PENDING-5 Notes add: "making `model_profile_id` and `tier` required changes
    the shared run-start body BSB-22-PENDING-4 uses; see the cross-epic note".

### Finding 2 — Cross-story contradiction: the "fixed" validation order in the preamble disagrees with PENDING-3's and PENDING-5's Notes
- **Severity:** Blocking
- **Stories touched:** BSB-24-PENDING-1 (owns the preamble), BSB-24-PENDING-2, BSB-24-PENDING-3,
  BSB-24-PENDING-4, BSB-24-PENDING-5
- **Evidence:**
  - Preamble, **Validation order**: "…then the request's required fields and types (`skill`,
    `skills_ref`, `input_branch`, `model_profile_id`, `tier`, then `context`), then the project's
    source-control integration and branch existence, then workflow/step existence, then model
    profile existence and tier mapping…". This puts `model_profile_required`,
    `model_profile_invalid` and `tier_required` **before** branch validation.
  - BSB-24-PENDING-5 Notes: "The 422 responses happen after branch and workflow validation". That
    covers all of PENDING-5's 422 scenarios, including `model_profile_required` and
    `tier_required`, so it puts them **after** branch validation.
  - BSB-24-PENDING-3 Notes: "The 422 responses happen after branch validation". That covers its
    `step_required` and `workflow_required` scenarios. Pairing could be a "type" check in the
    field stage, or it could come after branches; the preamble does not say which.
  - BSB-24-PENDING-4's `reviewer_feedback_invalid` and `upstream_handoff_invalid` are not placed
    in the order at all ("the request's required fields and types … then `context`" does not
    name them).
  - No scenario in any story sends two faults at once, so nothing pins which error wins.
- **What is contradictory:** take a request with a missing `tier` and a non-existent
  `skills_ref`. The preamble returns `tier_required`; PENDING-5's Notes return
  `skills_branch_not_found`. The validation is "defined in one place" (epic implementation
  guidance), but three stories describe that place differently. Two implementers would build
  different precedence.
- **Question (if a person must decide):** None; the preamble is the explicit, "fixed" statement.
  The fix is to make the Notes agree with it and to place every error code in it.
- **Proposed change:**
  - Preamble (all stories inherit it): list every 422 code in its stage. Field stage, in order:
    `skill_required`, `skills_ref_required`, `input_branch_required`, `model_profile_required`,
    `model_profile_invalid`, `tier_required`, `context_invalid`, `step_required` /
    `workflow_required`, `reviewer_feedback_invalid`, `upstream_handoff_invalid`. Integration and
    branch stage: `source_control_not_configured`, `skills_branch_not_found`,
    `input_branch_not_found`. Workflow stage: `workflow_not_found`, `step_not_found`. Model stage:
    `model_profile_not_found`, `model_tier_not_mapped`.
  - BSB-24-PENDING-3 Notes: "`step_required` and `workflow_required` are field-stage checks;
    `workflow_not_found` and `step_not_found` happen after branch validation."
  - BSB-24-PENDING-4 Notes: "`reviewer_feedback_invalid` and `upstream_handoff_invalid` are
    field-stage checks, before branch validation."
  - BSB-24-PENDING-5 Notes: "`model_profile_required`, `model_profile_invalid` and `tier_required`
    are field-stage checks; `model_profile_not_found` and `model_tier_not_mapped` happen after
    branch and workflow validation." Also add one precedence scenario, for example a missing
    `tier` with `skills_ref` = `test/ada/missing` → 422 `tier_required`.
  - BSB-24-PENDING-2 Notes: state that `source_control_not_configured` comes before both branch
    lookups, which the project `8` scenario already implies.

### Finding 3 — Epic-wide scope boundary: the `skill` itself is neither offered nor checked against the chosen skills branch, and the deferral to BSB-25 has no owning requirement
- **Severity:** Blocking
- **Stories touched:** BSB-24-PENDING-1, BSB-24-PENDING-2, BSB-24-PENDING-3 (and epic BSB-25's
  boundary)
- **Evidence:**
  - BSB-24-PENDING-1 Notes: "`skill` is only checked for presence here. Whether that skill folder
    exists on the chosen skills branch is resolved by epic BSB-25 when it packs the branch."
  - BSB-24-PENDING-2 Out of scope: "Validating that the chosen skill folder exists on the chosen
    branch (epic BSB-25)."
  - BSB-24-PENDING-3 validates `context.workflow` and `context.step` against the same branch at
    start (`workflow_not_found`, `step_not_found`) through the same GitHub read. The workflow on
    the branch is checked; the skill being tested is not.
  - The options response (preamble) has `skills_branches`, `input_branches`, `workflows` and
    `model_profiles`, but no list of skills. The run-start page scenario (PENDING-2) shows no
    skill choice. No story offers a skill to choose.
  - BSB-25's requirements (FR-038 to FR-043) cover SHA resolution, packaging, bundle reuse, the
    run branch and the baseline. None of them says a run is refused or failed when the skill is
    missing, or which `runs.state` it ends in.
  - Epic Goal / DoD: "A non-member or an invalid selection is refused before any run is created."
    A typo in `skill` creates a `queued` `runs` row (PENDING-1's contract).
- **What is missing:** the skill is the one input every run needs (SK-001 §5: "A run tests one
  skill"). It is the only run-start input that is neither offered (as FR-145 to FR-150 require
  for every other input) nor validated before the run row is written. The story that defers the
  check names an epic whose requirements never take it on.
- **Question (a person must decide):** Should run start (a) list the skill folders present on the
  chosen skills branch in the options API and page, and refuse a `skill` that is absent from that
  branch with a 422 before any `runs` row (recommended: same read as PENDING-3 and matches the
  epic DoD), or (b) keep presence-only and make BSB-25 own the refusal, adding an explicit failed
  state and requirement there?
- **Proposed change:**
  - If (a): BSB-24-PENDING-2 (it already reads the chosen branch and owns branch validation) adds
    `skills` to the options response and the page. It also adds a scenario such as
    `"skill":"sdlc-missing"` → 422 `skill_not_found` with the message `Skill 'sdlc-missing' does
    not exist on skills branch 'test/ada/fix-reproduce'.` and `runs` count `0`, and drops the
    "Validating that the chosen skill folder exists … (epic BSB-25)" Out-of-scope line.
    BSB-24-PENDING-1 Notes: replace the "only checked for presence" bullet with a pointer to
    PENDING-2. Preamble: add the code to the error table and to the branch stage of the
    validation order (Finding 2).
  - If (b): BSB-24-PENDING-1 and BSB-24-PENDING-2 keep their text but name the BSB-25 requirement
    or story that refuses a missing skill and the `runs.state` it ends in. Also record that this is
    an accepted exception to the epic DoD's "refused before any run is created".

### Finding 4 — Epic-wide scope boundary: no story owns the run-start page's controls beyond the branch lists, or the options API's behaviour when an integration is missing
- **Severity:** Blocking
- **Stories touched:** BSB-24-PENDING-2, BSB-24-PENDING-3, BSB-24-PENDING-4, BSB-24-PENDING-5
- **Evidence:**
  - The only page scenario in the epic is BSB-24-PENDING-2's "Run-start page shows the branch
    choices" (`GET /projects/7/runs/new` contains branch names). No scenario in any story shows a
    workflow/step control, a reviewer-feedback or upstream-handoff field, a profile/tier picker,
    or the page submitting to `POST …/runs`.
  - Notes that assume the page has more: PENDING-3 ("the run-start page and the options API read
    the same `config/` files") and PENDING-5 ("the run-start page offers exactly those keys", "the
    run-start page may preselect from `SKILL.md`").
  - FR-147, FR-149 and FR-150 say a run start "offers the author a choice". FR-148 says it "lets
    the author optionally supply" feedback or a handoff. Epic implementation guidance: "Build the
    run-start surface and then the API". BSB-37 (CLI) is out of scope for the epic, so the page is
    the only human surface. FR-148 in particular has no surface at all; `context.upstream_handoff`
    is a JSON object with no way for a person to enter it.
  - BSB-24-PENDING-2's scenario "A project without a source-control integration cannot offer or
    start a run" checks only the start route. What `GET …/runs/options` and the page return for
    project `8` (no `github`), or for a project with no `ai_model` row (PENDING-5's last scenario),
    is not stated anywhere. Three stories read the options API and each covers only its own slice.
- **What is missing:** each story owns its API slice, but the page and the options API's error
  behaviour fall between stories. PENDING-3, PENDING-4 and PENDING-5 implementers could each assume
  PENDING-2 builds "the page", while PENDING-2's AC builds only the branch lists.
- **Question (a person must decide):** When the project has no `github` or no `ai_model`
  integration, should the options API and page refuse with the same 422 the start route uses
  (`source_control_not_configured`, and a new `model_profiles_not_configured` or equivalent),
  or return `200` with empty lists and an explanatory message on the page?
- **Proposed change:**
  - BSB-24-PENDING-2: owns the page shell and the form's submit. Add a scenario where submitting
    the page's form produces the PENDING-1 `POST` body, and a scenario for project `8` on the
    options API and page, per the answer above.
  - BSB-24-PENDING-3: add a page scenario. The response for `skills_ref=test/ada/fix-reproduce`
    contains `bug-fix`, `smoke` and the step names.
  - BSB-24-PENDING-4: add a page scenario showing an optional reviewer-feedback text field and an
    optional upstream-handoff field, stating how the handoff object is entered (for example a JSON
    text area validated as an object, which matches `upstream_handoff_invalid`).
  - BSB-24-PENDING-5: add a page scenario showing profiles `Anthropic test` and `Smoke` with their
    tiers. Turn "may preselect from `SKILL.md`" into either an AC with an exact preselected value
    or an Out-of-scope line. Add the no-`ai_model` options/page behaviour per the answer above.
  - Each story's Out of scope names BSB-38 for accessibility of these controls (FR-130 to FR-137,
    NFR-012), as that epic constrains surfaces delivered here.

### Finding 5 — Cross-epic dependency: the default context when the author omits it is handed to BSB-26, whose requirements do not include it
- **Severity:** Blocking
- **Stories touched:** BSB-24-PENDING-3, BSB-24-PENDING-4 (and epic BSB-26's boundary)
- **Evidence:**
  - BSB-24-PENDING-3 Out of scope: "Resolving the default workflow when the author omits the
    context, and rendering the chosen context into `BB_CONTEXT` (epic BSB-26)". Its Notes say:
    "when it is omitted the run row's `context` is `{}` and the default workflow resolution is left
    to epic BSB-26."
  - BSB-24-PENDING-4 Out of scope: "Rendering these values into `BB_CONTEXT` (epic BSB-26)."
  - SK-001 §5.3 defines the default: "a workflow in the skills branch's `config/` that uses this
    skill". BSB-26's requirements (FR-044 to FR-049, FR-151, FR-152) cover execution, progress,
    logs, outcome classification, component versions, and the model profile and tier used. None
    covers default-context resolution. Rendering `BB_CONTEXT` is credibly part of FR-044 ("the same
    runtime as the platform"); choosing the default workflow is not.
  - Epic description: "a run is explicit about every input before anything executes, so results
    are reproducible and comparable." Storing `{}` and choosing a workflow later means
    `runs.context` does not record the context that was actually used.
  - The options API lists every workflow on the branch (PENDING-3), not the ones that "use this
    skill", so the page cannot show the default either.
- **What is missing:** an owner for the default. As written, nobody chooses it at start, and BSB-26
  has no requirement that says it will.
- **Question (a person must decide):** When the author omits `context`, should run start resolve
  the default (a workflow on the chosen branch whose steps use `skill`, plus the step that uses
  it) and store the resolved values in `runs.context` (recommended, matches the epic's
  reproducibility goal)? Or should `{}` be stored, with BSB-26 explicitly taking on resolution
  through a new requirement? And what happens when no workflow, or more than one, uses the skill?
- **Proposed change:**
  - If resolved at start: BSB-24-PENDING-3 replaces the "omitted context is recorded as an empty
    object" scenario with one where the stored `context` equals the resolved
    `{"workflow":…,"step":…}`. It adds scenarios for "no workflow uses the skill" and "more than
    one does" per the answer, and removes default resolution from its Out of scope. The preamble's
    `context` row ("when omitted the stored context is `{}`") changes to match.
    BSB-24-PENDING-4's Notes line "An omitted `context` … carries neither key" stays true for the
    two optional keys.
  - If left to BSB-26: BSB-24-PENDING-3 and BSB-24-PENDING-4 Notes name the BSB-26 requirement or
    story that resolves the default and renders `BB_CONTEXT`. They also state that `runs.context`
    records the author's input, not the resolved context, so BSB-33/BSB-35 comparisons know which
    one they show.

### Finding 6 — Cross-story consistency: unknown `context` keys and unknown top-level fields have no stated handling, and two stories' Notes point in different directions
- **Severity:** Advisory
- **Stories touched:** BSB-24-PENDING-3, BSB-24-PENDING-4 (preamble owned by BSB-24-PENDING-1)
- **Evidence:**
  - BSB-24-PENDING-3 Notes: "A `context` object may carry only the fields in the contract
    preamble." But the error table has no code for an extra key.
  - BSB-24-PENDING-4 Notes: "the run's stored context is exactly what the author supplied", which
    reads as store-whatever-arrives.
  - The request-field table lists the top-level fields but never says what an unlisted field
    (for example `turn_cap`, see Finding 7) does.
- **What is ambiguous:** whether `{"context":{"workflow":"bug-fix","step":"triage","foo":1}}` is
  refused (with which code) or stored. It is safe to build either way, but each implementer will
  pick one.
- **Question (if a person must decide):** None; recommended default below.
- **Proposed change:**
  - Preamble: add an error row "`context` contains a key other than `workflow`, `step`,
    `reviewer_feedback`, `upstream_handoff`" → 422 `context_invalid` with message
    `The context contains an unknown key 'foo'.`. Also state that unknown top-level fields are
    refused the same way (or ignored, if preferred), in the field stage of the order (Finding 2).
  - BSB-24-PENDING-3: add the unknown-key scenario.
  - BSB-24-PENDING-4 Notes: reword to "the stored context is exactly the allowed keys the author
    supplied".

### Finding 7 — Cross-epic architecture fit: BSB-27 must extend the run-start contract this epic declares closed (caps, start refusals), and SK-001 §9 has no cap columns
- **Severity:** Advisory
- **Stories touched:** BSB-24-PENDING-1 (preamble), BSB-24-PENDING-5 (and epic BSB-27's boundary)
- **Evidence:**
  - FR-050 / FR-052 (BSB-27): "The author sets a turn cap / spend cap for a run". SK-001 §5.4 lists
    "Turn and spend caps per run" among the inputs the user picks at run start. FR-054 / FR-055
    (BSB-27): the builder "refuses to start a run" when components are incompatible or the static
    scan did not pass. These are start-route refusals.
  - BSB-24 preamble: "This epic owns the full contract of that route", "**Validation order** on
    the start API is fixed … and only then the `runs` row", "The `runs` row … is exactly these
    columns", and the options response "is exactly …".
  - BSB-24-PENDING-1 and BSB-24-PENDING-5 Out of scope correctly name BSB-27 for caps and the
    static-scan refusal. But neither Notes section says BSB-27 will add request fields, `runs`
    columns, options entries and validation stages to this route.
  - SK-001 §9's `runs` table has no turn-cap or spend-cap column. That is for BSB-27 to add (it
    owns FR-050 and FR-052); it does not block this epic.
- **What is missing:** the dependency is stated only as "out of scope". A BSB-27 implementer would
  find a contract that says it is fixed and exact. The missing cap columns could be overlooked
  because no BSB-24 note mentions them.
- **Question (if a person must decide):** None.
- **Proposed change:**
  - BSB-24-PENDING-1 Notes: "Epic BSB-27 extends this route: turn and spend cap request fields and
    `runs` columns (FR-050, FR-052; SK-001 §9 has no cap columns yet), and the FR-054/FR-055
    refusals as stages before the `runs` row. 'Exactly' in this contract means exactly as of this
    epic."
  - BSB-24-PENDING-5 Notes: one line that caps (BSB-27) and model selection are separate inputs, so
    the options API may later carry cap defaults.

### Finding 8 — Cross-epic architecture fit: `runs.model_profile_id` points at an integer id inside BSB-23's `ai_model` config JSON, whose identity and stability BSB-23 has not committed to
- **Severity:** Advisory
- **Stories touched:** BSB-24-PENDING-1, BSB-24-PENDING-5 (and epics BSB-23 and BSB-26)
- **Evidence:**
  - Preamble fixture: `ai_model` `config` = `{"profiles":[{"id":3,…},{"id":4,…}]}`. The request's
    `model_profile_id` "must be the `id` of a profile in the project's `ai_model` integration", and
    `runs.model_profile_id` stores it.
  - SK-001 §9 has `runs.model_profile_id` but no model-profile table. Profiles live inside
    `integrations.config` JSONB, and BSB-23 (FR-031) owns how they are keyed. BSB-23 has no stories
    yet.
  - BSB-24-PENDING-1 and BSB-24-PENDING-5 Notes: "if BSB-23 names a field differently only this
    fixture is re-pointed — the validation decisions … do not change". That holds for a renamed
    field, but not if BSB-23 keys profiles by name or re-numbers them when the owner edits the
    integration. In that case, stored `runs.model_profile_id` values would point at a different
    profile or none. BSB-26 (FR-049) and BSB-35 (run comparison) read this value later.
- **What is missing:** the stated dependency on BSB-23 covers field names, not the fact that
  BSB-24 relies on a stable integer profile id.
- **Question (if a person must decide):** None for this epic. The decision is BSB-23's, and this
  dependency should be written down so BSB-23's decomposition sees it.
- **Proposed change:** BSB-24-PENDING-1 and BSB-24-PENDING-5 Notes: "Depends on BSB-23 giving each
  `ai_model` profile a stable positive integer `id` that is never reused within a project; if
  BSB-23 keys profiles differently, `model_profile_id` and its error codes are re-pointed, not
  only the fixture."

## Open questions

1. **(Finding 1)** Answer BSB-22 Open question 1 for both epics. Is BSB-22-PENDING-4 a reusable
   membership guard, with BSB-24-PENDING-1 owning every run-start route scenario (option (a),
   recommended)? Or do both stories keep run-start scenarios, with BSB-22's bodies re-pointed to
   BSB-24's contract (option (c))?
2. **(Finding 3)** Should run start offer the skills present on the chosen skills branch and
   refuse an absent `skill` with a 422 before any `runs` row (recommended)? Or does BSB-25 own the
   refusal, as an explicit exception to the epic DoD?
3. **(Finding 4)** When a project has no `github` or no `ai_model` integration, should the options
   API and run-start page refuse with a 422 (as the start route does), or return 200 with empty
   lists and a message?
4. **(Finding 5)** When `context` is omitted, should run start resolve the default workflow and
   step (a workflow on the branch that uses `skill`) and store it in `runs.context` (recommended)?
   Or does BSB-26 take on default resolution through a new requirement? In either case, what
   happens when no workflow, or more than one, uses the skill?

## Proposed changes

`docs/product/epics/BSB-24/_epic/stories.md`. These are for `sdlc-plan-stories-write` (revise) to
apply after the open questions are answered. Nothing here has been applied.

- **Contract preamble** (inherited by all five stories):
  - Place every 422 code in a named stage of the validation order (Finding 2).
  - Add the unknown-key error row and the top-level unknown-field rule (Finding 6).
  - Add `skill_not_found` and `skills` in the options response if Q2 is answered (a) (Finding 3).
  - Update the `context` row if Q4 resolves the default at start (Finding 5).
  - Rewrite the BSB-22 cross-epic note per Q1 (Finding 1).
  - State that "exactly" means as of this epic, with BSB-27 extensions expected (Finding 7).
- **BSB-24-PENDING-1:**
  - Notes: the guard-or-duplicate line per Q1 (Finding 1).
  - Notes: replace "only checked for presence" per Q2 (Finding 3).
  - Notes: the BSB-27 extension line (Finding 7) and the stable profile-id dependency on BSB-23
    (Finding 8).
- **BSB-24-PENDING-2:**
  - AC: a form-submit scenario and the project `8` options/page scenario per Q3 (Finding 4).
  - AC: if Q2 is (a), the `skills` option and the `skill_not_found` scenario (Finding 3).
  - Out of scope: drop the skill-folder line if Q2 is (a) (Finding 3).
  - Notes: `source_control_not_configured` precedes both branch lookups (Finding 2).
- **BSB-24-PENDING-3:**
  - AC: a page scenario for workflows and steps (Finding 4).
  - AC: the unknown-context-key scenario (Finding 6).
  - AC: the default-context scenarios per Q4 (Finding 5).
  - Notes: the field-stage vs post-branch placement of its codes (Finding 2).
  - Out of scope and Notes: name the default's owner per Q4 (Finding 5).
- **BSB-24-PENDING-4:**
  - AC: a page scenario for the feedback and handoff fields, stating how the handoff object is
    entered (Finding 4).
  - Notes: its two codes are field-stage (Finding 2).
  - Notes: reword "exactly what the author supplied" (Finding 6).
  - Notes: name the `BB_CONTEXT` owner per Q4 (Finding 5).
- **BSB-24-PENDING-5:**
  - AC: a page scenario for profiles and tiers; turn the `SKILL.md` preselection into an AC or an
    Out-of-scope line; add the no-`ai_model` options/page behaviour per Q3 (Finding 4).
  - AC: a precedence scenario, e.g. missing `tier` with a non-existent branch → `tier_required`
    (Finding 2).
  - Notes: correct "The 422 responses happen after branch and workflow validation" (Finding 2).
  - Notes: the shared-body consequence for BSB-22-PENDING-4 (Finding 1), the caps line
    (Finding 7), and the stable profile-id dependency (Finding 8).
- **Outside this epic (for the owning epic's revise pass, not BSB-24's):**
  - BSB-22-PENDING-4 per Q1 (Finding 1).
  - BSB-25 per Q2 (b), if chosen (Finding 3).
  - BSB-26 per Q4, if it takes on default resolution (Finding 5).

## Architecture impact

None. Every finding is resolved by a story change or a scope decision inside SK-001 §4, §5 and §9.
The only data-model addition noticed is the turn-cap and spend-cap storage on `runs` (Finding 7).
That belongs to BSB-27, which owns FR-050 and FR-052, so it is recorded as a cross-epic note, not
as a design change for this epic. The stable profile identity in Finding 8 is BSB-23's decision
within the existing `integrations.config` JSONB.

## Requirement coverage check

Yes, with notes.
- FR-037 (PENDING-1), FR-145 and FR-146 (PENDING-2), FR-147 (PENDING-3), FR-148 (PENDING-4), and
  FR-149 and FR-150 (PENDING-5) are each exercised by at least one acceptance scenario.
- No FR is claimed by two BSB-24 stories, and the covered-requirement lists match `story-map.json`.
- The `epic-map.json` IDs match the current `PRD.md` wording for all seven requirements.
- Notes:
  - FR-037's 403/404 behaviour is asserted again by BSB-22-PENDING-4 under FR-027, and the two
    epics' success bodies contradict each other (Finding 1).
  - FR-147 to FR-150 are exercised through the options API only, and FR-148 has no human surface
    (Finding 4).
  - The epic DoD's "invalid selection refused before any run is created" does not hold for the
    `skill` input (Finding 3).
  - FR-147's default context has no owner (Finding 5).

## Dependency-note sanity check

Mostly yes. Every in-epic note names a real BSB-24 story. Every cross-epic note names a real epic
(BSB-18, BSB-22, BSB-23, BSB-25, BSB-26, BSB-27, BSB-31 to BSB-35, BSB-37).
- PENDING-2, PENDING-3, PENDING-4 and PENDING-5 each depend on PENDING-1 for the route and `runs`
  row. PENDING-1 makes no contradicting forward claim.
- PENDING-3 depends on PENDING-2, and PENDING-4 on PENDING-3. Both are consistent with their
  scenarios.
- BSB-24-PENDING-1's "Shares the route with BSB-22-PENDING-4" matches BSB-22-PENDING-4's "Cannot be
  accepted before epic BSB-24's run-start story". The link is two-way, but the content of the
  shared fixture contradicts (Finding 1).
- PENDING-5's Notes rely on PENDING-2's and PENDING-3's validation running first, but they
  misstate the order (Finding 2).

Mismatches:
- The skill-existence deferral names BSB-25, but no BSB-25 requirement takes it on (Finding 3).
- The default-context deferral names BSB-26, but no BSB-26 requirement takes it on (Finding 5).
- The stable-profile-id dependency on BSB-23 is not written down (Finding 8).

Build order itself is left to `sdlc-plan-epic-sequence`.
