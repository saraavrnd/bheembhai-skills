# Epic Review — BSB-24: Run start & input selection

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-24-PENDING-1, BSB-24-PENDING-2, BSB-24-PENDING-3, BSB-24-PENDING-4

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-24/_epic/epic-review.md`.

## Context loaded

- **Target work item.** `SkillBuilder-2` is the PRD's work-item umbrella, not a Jira issue. A
  read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned
  `"Issue does not exist or you do not have permission to see it."`, matching `PRD.md:273-281`
  (no `SkillBuilder-2` issue exists on the configured site). The Atlassian MCP tools were not
  exposed in this session; the read-only REST calls used the credentials already in `.mcp.json`.
  The epic actually under review is **BSB-24 — Run start & input selection** (`epics.md:657-713`),
  whose four stories were just written (HEAD `3779217`, `sdlc-plan-stories-write`) and which has
  no prior `epic-review.md`.
- **Epic story set.** `docs/product/epics/BSB-24/_epic/stories.md` (all four stories, 371 lines)
  and `story-map.json` (four entries, seven requirements).
- **Product context.** `docs/product/PRD.md` §4-§9: FA-6 (`PRD.md:55`), FR-037 (`PRD.md:111`),
  FR-145 to FR-150 (`PRD.md:219-224`), NFR-006 (`PRD.md:256`), and the external prerequisites in
  §8 (`PRD.md:271-290`). `docs/product/epics.md` BSB-24 (`657-713`), BSB-25/26/27
  (`717-910`). `docs/product/epic-map.json` BSB-24 entry (`62-66`).
- **Design source.** `docs/adr/SK-001-skill-builder.md` §1a (catalog repo and branch naming),
  §3 (Cognito / per-request authorization), §4 (projects and integrations; GitHub token scope,
  line 197), §5 (one skill per run, workflows under `config/`, skills branch is a branch of
  `bheembhai-skills`, line 217), §6b (static scan), §9 (data model; `runs` columns, line 355).
  There is no `docs/architecture.md`, `docs/data-model.md`, `docs/api-contracts/` or
  `docs/ui-conventions.md` in this repo yet; the ADRs are the only design source.
- **Sibling story sets compared.** BSB-19 (`BSB-19-PENDING-1` build row and `-PENDING-3` skill
  naming rule), BSB-22 (`-PENDING-1` membership check, `-PENDING-3` run-start page, `-PENDING-4`
  owner-only integration changes), BSB-23 (`-PENDING-2` source-control config, `-PENDING-3` AI
  model profiles, `-PENDING-6` test-purpose confirmation and run-purpose list), BSB-31
  (`-PENDING-1` static-scan route), and BSB-32 (no run-creation overlap).

## Findings

### Finding 1 — PENDING-1 assigns model validation to PENDING-4 while PENDING-4 depends on PENDING-1; the implied edge is a dependency cycle
- **Severity:** Blocking
- **Stories touched:** BSB-24-PENDING-1, BSB-24-PENDING-4
- **Evidence:**
  - PENDING-1 says `model_profile_id` and `tier` are "required, chosen and validated by
    BSB-24-PENDING-4" (`stories.md:97-98`), and its declared validation order ends with "... the
    context fields of BSB-24-PENDING-2 and the model fields of BSB-24-PENDING-4"
    (`stories.md:126-127`).
  - PENDING-1's Out of scope says "choosing and validating the model profile and tier
    (BSB-24-PENDING-4)" is not this story (`stories.md:71-72`).
  - PENDING-1's dependency list names BSB-18, BSB-22-PENDING-1/-3, BSB-19-PENDING-1,
    BSB-23-PENDING-2/-3/-6 — **not** BSB-24-PENDING-4 (`stories.md:80-91`).
  - PENDING-4 says "Depends on BSB-24-PENDING-1 for the POST contract, the run row and the
    'Chosen inputs' summary" (`stories.md:340`).
- **What is missing/ambiguous/contradictory:** The dependency is a cycle. PENDING-1's POST cannot
  reach its own 201 ACs without the model validation PENDING-4 owns (its ACs submit
  `model_profile_id` and `tier` and expect 201, `stories.md:36-38`), so PENDING-1 → PENDING-4.
  PENDING-4 cannot exist without PENDING-1's request contract and run row, so PENDING-4 →
  PENDING-1. `sdlc-plan-epic-sequence` cannot order the pair, and whichever story is delivered
  first must duplicate the other's logic or ship an endpoint that fails its own acceptance
  criteria. PENDING-1's own Out of scope already assigns model validation to PENDING-4, so the
  validation-order sentence is the inconsistent half.
- **Question (if a person must decide):** Does PENDING-1 own only the presence/required check and
  the row write for `model_profile_id`/`tier`, with PENDING-4 appending availability validation
  after it, or does PENDING-4 own the whole model step with PENDING-1 depending on it? (Open
  question 1.)
- **Proposed change:**
  - **BSB-24-PENDING-1:** End the validation order at PENDING-2's context fields
    (`stories.md:126-127`). State that this story requires `model_profile_id` and `tier` as
    request fields and writes them to the run row, and that PENDING-4 appends the
    availability/kind/test-purpose check after this story's checks. Keep the Out of scope
    sentence. Do **not** add PENDING-4 to PENDING-1's dependency list.
  - **BSB-24-PENDING-4:** Keep "Depends on BSB-24-PENDING-1 for the POST contract, the run row
    and the 'Chosen inputs' summary" and add that its model validation runs after PENDING-1's
    checks and does not require PENDING-1 to call it.
  - **BSB-24-PENDING-2 / -3 (minor):** Add a sentence that PENDING-4's model validation also
    applies to their requests, since they submit its required fields.

### Finding 2 — Every sibling AC that asserts a 201 (or a late-chain 422) omits fixtures PENDING-1's validation chain reads first
- **Severity:** Blocking
- **Stories touched:** BSB-24-PENDING-1, BSB-24-PENDING-2, BSB-24-PENDING-3, BSB-24-PENDING-4
- **Evidence:**
  - The inherited chain is membership → source-control integration → build and skill → skills
    branch → input branch → context → model (`stories.md:126-127`). The skills branch must contain
    `skills/<skill>` and the input branch must exist in the sandbox repository
    (`stories.md:110-112`). These reads need a source-control provider stub and a catalog tree.
  - **PENDING-1 scenario 7** (`stories.md:61-63`) expects 201, but its Given has no
    branch-list provider stubs, no catalog tree, and no `ai_model` integration 4 — while the
    submitted body and the existing run row both carry `model_profile_id: 4`.
  - **PENDING-1 scenario 1** (`stories.md:31-33`) expects a usable page but has no `ai_model` row
    or run-purpose list stub; once PENDING-4 lands, the page's model state is "No model profile is
    available..." and Start is disabled (`stories.md:351-353`), which the AC does not
    acknowledge.
  - **PENDING-2 scenarios 2 and 3** (`stories.md:154-161`) expect 201; each supplies only "the
    source-control integration 3 for project 7" (no provider stubs), a catalog tree that names
    only `config/...` (no `skills/bug-fix-resolver/SKILL.md`), and no `ai_model` row. The refusal
    scenarios (`stories.md:164-181`) expect workflow/step-specific 422s, but the earlier
    skills-branch and input-branch checks would fail first with different messages.
  - **PENDING-3 scenarios 1-4** (`stories.md:233-250`) expect 201 with no catalog tree at all, no
    provider stubs and no `ai_model` row; scenario 4 (`stories.md:248`) has a tree that names only
    `config/...`.
  - **PENDING-4 scenario 2** (`stories.md:298-300`) expects 201 with no provider stubs and no
    skill path; scenarios 3-7 (`stories.md:303-325`) expect model-specific 422s, but model is
    validated last, so all earlier checks must pass and their fixtures do not provide what those
    checks read.
  - **Validation source is unstated.** PENDING-4 says a direct request naming a profile "not in
    the list" is refused (`stories.md:342-345`), but PENDING-1 scenario 2 (`stories.md:36-38`) and
    PENDING-4 scenario 2 (`stories.md:298-300`) expect 201 without stubbing
    `GET /api/projects/7/integrations?purpose=run`. An implementer can reasonably validate
    against the list response (then scenario 2 fails) or against the `integrations` row (then it
    passes).
- **What is missing/ambiguous/contradictory:** The sibling ACs are not independently executable.
  Run against the chain they all inherit, several produce a 422 or 502 for a different reason than
  the one asserted; a developer implementing PENDING-2's workflow refusal literally must either
  reorder the checks (contradicting the declared order) or watch the AC fail. The fix is a shared
  fixture block, stated once, plus one decision on where POST model validation reads from.
- **Question (if a person must decide):** Should the stories share one named "standard run-start
  fixture", and does submit-time model validation read the `integrations` row or the
  run-purpose list response? (Open question 2.)
- **Proposed change:** Same change for all four stories: define the standard fixture in
  PENDING-1's Notes and have the sibling ACs reuse it.
  - **Standard fixture:** source-control integration 3 (kind `github`, `config.test_only: true`)
    with provider branch lists for `saraavrnd/bheembhai-skills` and
    `saraavrnd/skill-builder-sandbox`; a catalog tree whose ref contains
    `skills/bug-fix-resolver/SKILL.md`; AI-model integration 4 (`config.test_only: true`).
  - **BSB-24-PENDING-1:** Add the standard fixture to scenario 7 and to scenario 1 (the page is
    meant to be startable); keep scenario 2 as is.
  - **BSB-24-PENDING-2:** Add the provider stubs and the skill path to every AC; keep each
    scenario's workflow/step tree contents on top of the standard fixture.
  - **BSB-24-PENDING-3:** Add the standard fixture to all four ACs.
  - **BSB-24-PENDING-4:** Add the standard fixture to every POST AC and to scenario 1's page
    load; keep the model rows each scenario varies. State that submit-time validation queries the
    `integrations` row (same
    project, kind `ai_model`, `config.test_only` true) and that the list endpoint is for rendering
    only — or, if the list response is authoritative, add the list stub to every POST AC.

### Finding 3 — PENDING-1 uses the project's source-control integration without the test-purpose check NFR-006 and BSB-23-PENDING-6 require
- **Severity:** Blocking
- **Stories touched:** BSB-24-PENDING-1. Cross-epic: BSB-23-PENDING-6, PRD NFR-006.
- **Evidence:**
  - NFR-006: "Runs use only test-purpose Jira, source-control and model credentials."
    (`PRD.md:256`).
  - BSB-23-PENDING-6: "the run-purpose list is the hard filter ... An unconfirmed integration is
    never offered to a run even if it exists in the table."
    (`BSB-23/_epic/stories.md:477-481`).
  - PENDING-1's validation order checks membership, presence of a source-control integration,
    build/skill, skills branch, input branch, context and model — it never checks the
    source-control row's `config.test_only` (`stories.md:126-134`). Its only integration-absence
    scenario covers "no row with kind 'github'" (`stories.md:45-48`); every AC that uses
    integration 3 gives it `test_only: true` (`stories.md:31, 36`).
  - PENDING-1 says it depends on BSB-23-PENDING-6 "for the run-purpose filter"
    (`stories.md:86`), but that endpoint returns AI-model profiles (`BSB-23/_epic/stories.md:450-453`),
    not the source-control row; the source-control row's `test_only` is not filtered by it.
- **What is missing/ambiguous/contradictory:** A project whose `github` integration exists but has
  `config.test_only: false` would still have its repository listed and used to validate the input
  branch. BSB-23-PENDING-6 says that must never happen, and NFR-006 says runs use only
  test-purpose source-control credentials. The page also has no state for this case: the
  "No source-control integration is configured..." message would be false, and Start would be
  enabled against a non-test repository.
- **Question (if a person must decide):** For a source-control integration that exists but is not
  test-purpose, should the page reuse "No source-control integration is configured for this
  project." or show a distinct message such as "A test-purpose source-control integration is
  required to start a run."? (Open question 3.)
- **Proposed change:**
  - **BSB-24-PENDING-1:** Add "the source-control integration's `config.test_only` is true" to the
    validation order before the build/skill check. Add a scenario: the page renders the chosen
    message with Start disabled, POST returns 422 with the same message, no `runs` row is
    created, and the provider receives 0 branch-listing requests. Correct the dependency note:
    BSB-23-PENDING-6 defines the test-purpose rule; the run-purpose list covers model profiles,
    while the source-control row is checked directly.

### Finding 4 — The run-purpose list's read access and the non-owner member run start are unproven
- **Severity:** Advisory
- **Stories touched:** BSB-24-PENDING-1, BSB-24-PENDING-4. Cross-epic: BSB-22-PENDING-3,
  BSB-23-PENDING-6.
- **Evidence:**
  - All four stories' actor is "a skill author who is a project member" (`stories.md:26, 144,
    228, 288`), and the epic's DoD says "A project member can start a run"
    (`epics.md:694-697`); FR-037 says the same (`PRD.md:111`).
  - Every BSB-24 AC that exercises a successful or member action uses Ada with `role "owner"`
    (`stories.md:31-323`); the only other actor is Carol, a non-member. No BSB-24 AC has a
    non-owner member start a run.
  - BSB-22-PENDING-3 proves Bob (role `member`) can open the bare run-start page
    (`BSB-22/_epic/stories.md:161-164`), but not that he can start a run; its POST ACs use Carol
    (non-member) and Ada (owner) (`176-179`).
  - BSB-23-PENDING-6's actor is "a project owner" (`BSB-23/_epic/stories.md:436`) and its GET AC
    uses Ada owner (`451-453`); it states no read-access rule for the run-purpose list.
    BSB-22-PENDING-4's owner guard covers integration *changes*, and the settings page is
    member-readable (`BSB-22/_epic/stories.md:231-234, 265-269`).
- **What is missing/ambiguous/contradictory:** The run-purpose list could be implemented
  owner-only by analogy with integration management, which would make PENDING-4's page fail for a
  non-owner member; or member-readable, which is clearly intended but never tested. The epic's
  central DoD claim is verified only for the owner, and the list's access rule is not written
  down in the story that owns the endpoint.
- **Question (if a person must decide):** Is
  `GET /api/projects/7/integrations?purpose=run` readable by any project member (membership check
  only, not owner-only), and should a non-owner member AC be added? (Open question 4.)
- **Proposed change:**
  - **BSB-24-PENDING-4:** Add a Bob-role-member AC that opens the page and sees the run-purpose
    profiles; state in Notes that the list applies the shared membership check and is not
    owner-only.
  - **BSB-24-PENDING-1:** Add one Bob-role-member 201 AC (or switch one existing 201 AC to Bob)
    so FR-037's "project member" is exercised end to end.
  - **Cross-epic follow-up (not applied here):** BSB-23-PENDING-6 should state the list's read
    access rule and include a member (not only the owner) in its GET AC.

### Finding 5 — The no-build state of `GET /projects/7/runs/new` is asserted by BSB-22 but defined by no BSB-24 story
- **Severity:** Advisory
- **Stories touched:** BSB-24-PENDING-1. Cross-epic: BSB-22-PENDING-3, BSB-21.
- **Evidence:**
  - BSB-22-PENDING-3: Bob opens `GET "/projects/7/runs/new"` with no `build` parameter and no
    build fixture, and receives HTTP 200 rendering the heading and project name
    (`BSB-22/_epic/stories.md:161-164`).
  - BSB-24-PENDING-1 defines only `GET "/projects/7/runs/new?build=7"` (`stories.md:30-33`) and
    says the page is BSB-22-PENDING-3's, that this story fills its choices and summary, and that
    the build page (BSB-21) links here with the build id (`stories.md:100-102`). The only
    "Choose a build to run." text is a POST refusal (`stories.md:128-129`).
- **What is missing/ambiguous/contradictory:** With no build (or an unknown/closed build), which
  selects render, what the "Chosen inputs" summary shows, and whether Start is enabled are all
  undefined. BSB-22-PENDING-3's AC asserts only the heading, so it will pass while the page may
  render an unusable form or crash on a missing skill. This is a cross-epic page contract, not a
  wording nit: BSB-24 adds controls to a page whose no-build state it does not own.
- **Question (if a person must decide):** Should the page require a build and render
  "Choose a build to run." with Start disabled (build page is the only entry), or should it offer
  a build picker? (Open question 5.)
- **Proposed change:**
  - **BSB-24-PENDING-1:** State the no-build/unknown-build state in the Notes and add an AC for
    it; or state that the page is only reachable with a build and arrange for BSB-22-PENDING-3's
    Bob AC to use `?build=7`.
  - **Cross-epic follow-up (not applied here):** Align BSB-22-PENDING-3's Bob AC with whichever
    state is chosen.

### Finding 6 — The skills-branch list is attributed to the source-control integration although the catalog repository is fixed and not stored in the integration
- **Severity:** Advisory
- **Stories touched:** BSB-24-PENDING-1. Cross-epic: BSB-23-PENDING-2, ADR SK-001 §4-§5.
- **Evidence:**
  - PENDING-1: "The skills branch choices are the branches of the catalog repository
    'bheembhai-skills' returned by the project's source-control integration; the input branch
    choices are the branches of that integration's sandbox repository." (`stories.md:106-108`).
  - BSB-23-PENDING-2 stores only the sandbox `repository` and `base_branch` in the `github`
    integration config; one source-control integration exists per project
    (`BSB-23/_epic/stories.md:171-177`).
  - ADR SK-001 §5 says the skills branch is a branch of `bheembhai-skills`
    (`docs/adr/SK-001-skill-builder.md:217`); §4 says the integration token is scoped to the
    sandbox repository plus push access to `build/*` branches of `bheembhai-skills`
    (`docs/adr/SK-001-skill-builder.md:197`).
- **What is missing/ambiguous/contradictory:** The sentence can be read as "the integration
  config supplies the catalog repository", but no such field exists. An implementer could add a
  `catalog_repository` config field or store the catalog repository on the source-control row,
  diverging from BSB-23's schema. The intended reading is: the catalog repository is the fixed
  `bheembhai-skills`, read with the integration's credential.
- **Question (if a person must decide):** Confirm that the catalog repository is the fixed
  `bheembhai-skills` and the integration supplies only the credential, with no new configuration
  field. (Open question 6.)
- **Proposed change:**
  - **BSB-24-PENDING-1:** Reword to "the fixed catalog repository 'bheembhai-skills'
    (ADR SK-001 §5), read with the project's source-control integration credential; the
    integration's `config.repository` remains the sandbox repository." Add that no new config
    field is introduced.

### Finding 7 — AC fixture skill names do not satisfy BSB-19's naming rule and the step-to-skill mapping is unrealistic
- **Severity:** Advisory (lowest priority; does not change behavior)
- **Stories touched:** BSB-24-PENDING-1, BSB-24-PENDING-2, BSB-24-PENDING-3,
  BSB-24-PENDING-4. Cross-epic: BSB-19-PENDING-3, BSB-31 (matching fixtures).
- **Evidence:**
  - The ACs use skill `bug-fix-resolver` (`stories.md:31, 36, 61, 149, ...`), steps
    `sdlc-fix-bug-triage` with skill `bug-fix-resolver` and `sdlc-fix-bug-reproduce` with skill
    `bug-fix-reproducer`, and `release-opener` (`stories.md:149`).
  - BSB-19-PENDING-3's rule: a literal `sdlc-` prefix, then an area segment and an action
    segment, all lowercase letters, digits and hyphens, with at least three hyphen-separated
    segments; the validator is reused by every build create
    (`BSB-19/_epic/stories.md:195-198`). `bug-fix-resolver` and `release-opener` do not satisfy
    it. The catalog has `skills/sdlc-fix-bug-reproduce` and `skills/sdlc-fix-bug-triage`; there
    is no `release-opener`.
  - BSB-31's stories use `bug-fix-resolver` in their fixtures too, so a rename is cross-epic.
- **What is missing/ambiguous/contradictory:** The fixtures seed `builds` rows directly, so no
  test enforces BSB-19's validator; a developer may copy the names into real fixtures or conclude
  the rule does not apply to runs. The step id `sdlc-fix-bug-triage` paired with skill
  `bug-fix-resolver` also models a platform step whose `skill:` does not match its id, which the
  real catalog does not do.
- **Question (if a person must decide):** Should AC fixtures use catalog-valid names
  (`sdlc-fix-bug-reproduce`, `sdlc-fix-bug-triage`, `sdlc-deliver-pr-open`), and should BSB-31's
  matching fixtures be renamed in the same pass? (Open question 7.)
- **Proposed change:** Same change for all four stories — BSB-24-PENDING-1,
  BSB-24-PENDING-2, BSB-24-PENDING-3 and BSB-24-PENDING-4: rename the fixture skill to a valid
  catalog skill (for example `sdlc-fix-bug-reproduce`), the branch to `build/<skill>`, and the
  workflow steps to real catalog skills that match their `skill:` values (for example
  `sdlc-fix-bug-reproduce` and `sdlc-fix-bug-triage`; use `sdlc-deliver-pr-open` for the
  non-matching release step). Cross-epic follow-up (not applied here): BSB-31's fixtures should
  use the same names.

## Open questions

1. **Model-validation ownership (Finding 1).** Does PENDING-1 own only the presence/required
   check and the row write for `model_profile_id`/`tier`, with PENDING-4 appending availability
   validation, or does PENDING-4 own the entire model step with PENDING-1 depending on it? The
   chosen direction must leave one edge, never PENDING-1 ↔ PENDING-4.
2. **Standard fixture and POST validation source (Finding 2).** Should the four stories share one
   named "standard run-start fixture" (source-control integration + provider branch lists +
   catalog tree with the skill path + `ai_model` integration), and does submit-time model
   validation read the `integrations` row or the run-purpose list response?
3. **Non-test source-control integration (Finding 3).** What should the page and POST say when a
   `github` integration exists but `config.test_only` is false — reuse the no-integration message
   or show a distinct test-purpose message? Is the refusal required before the branch-list read?
4. **Run-purpose list access (Finding 4).** Is
   `GET /api/projects/7/integrations?purpose=run` readable by any project member, and should a
   non-owner member AC exercise a full run start?
5. **No-build page state (Finding 5).** Should `GET /projects/7/runs/new` require a build and
   render "Choose a build to run." with Start disabled, or offer a build picker? Whichever is
   chosen, BSB-22-PENDING-3's Bob AC must match it.
6. **Catalog repository (Finding 6).** Confirm that `bheembhai-skills` is the fixed catalog
   repository read with the integration credential, and that no `catalog_repository` config field
   is added to the source-control integration.
7. **Fixture skill names (Finding 7).** Should AC fixtures use catalog-valid `sdlc-...` names,
   and should BSB-31's matching fixtures be renamed in the same pass?

## Proposed changes

Per story, for `sdlc-plan-stories-write` (revise mode). Cross-epic items are recorded, not
applied here.

- **BSB-24-PENDING-1**
  - End the validation order at PENDING-2's context fields; leave model availability to PENDING-4
    (Finding 1).
  - Add the standard run-start fixture to the Notes and to scenarios 1 and 7 (Finding 2).
  - Add the source-control `config.test_only` check and a non-test-integration scenario; correct
    the BSB-23-PENDING-6 dependency note (Finding 3).
  - Add one non-owner member (Bob) 201 AC (Finding 4).
  - State the no-build/unknown-build page state and add an AC, or make the page build-only and
    align BSB-22-PENDING-3 (Finding 5).
  - Reword the catalog-repository sentence and state that no new config field is added
    (Finding 6).
  - Rename fixture skills/branches/steps to catalog-valid names (Finding 7).
- **BSB-24-PENDING-2**
  - Add the standard fixture (provider stubs, skill path, `ai_model` row) to every AC
    (Finding 2).
  - Add a sentence that PENDING-4's model validation applies (Finding 1).
  - Rename fixture skills/steps (Finding 7).
- **BSB-24-PENDING-3**
  - Add the standard fixture to all four ACs (Finding 2).
  - Add a sentence that PENDING-4's model validation applies (Finding 1).
  - Rename fixture skills/steps (Finding 7).
- **BSB-24-PENDING-4**
  - Keep the PENDING-1 dependency; state that model validation runs after PENDING-1's checks
    (Finding 1).
  - Add the standard fixture to every POST AC and state whether POST validation reads the
    `integrations` row or the list response (Finding 2).
  - Add a non-owner member AC and state the list's membership-only read access (Finding 4).
  - Rename fixture skills/steps (Finding 7).
- **Cross-epic follow-ups (not applied here)**
  - BSB-23-PENDING-6: state the run-purpose list's read access rule; include a non-owner member
    in its GET AC (Finding 4).
  - BSB-22-PENDING-3: align its Bob no-build AC with the chosen page contract (Finding 5).
  - BSB-31: rename the matching fixture skill names (Finding 7); update its stale note that
    BSB-24 "does not currently name" the static-scan call — BSB-24-PENDING-1 now does
    (`stories.md:118-120` vs `BSB-31/_epic/stories.md:95-96`).
  - BSB-27: its epic places the static scan "before a bundle or branch is prepared"
    (`epics.md:873-874`), while BSB-24-PENDING-1 places it after BSB-25 resolves the SHA and
    creates the run branch (`stories.md:116-120`). BSB-27 has no stories yet; resolve the
    sequence there (the known BSB-31 review follow-up), not in BSB-24.

## Architecture impact

None. The stories fit ADR SK-001: the `runs` table already has `model_profile_id`, `tier`,
`context`, `skills_ref`, `input_branch`, `run_branch`, `state` and `kind`
(`docs/adr/SK-001-skill-builder.md:355`). PENDING-1 adds `runs.build_id`, which that column list
does not include; PENDING-1 already states that the data-model stage must record the column
(`stories.md:87-88`), so this is a stated data-model follow-up within the existing design.
There is no `docs/data-model.md` or `docs/api-contracts/` yet; when those stages run they must
carry `runs.build_id` and the `POST /projects/7/runs` / `GET /api/projects/7/integrations?purpose=run`
contracts. No escalation is needed.

## Requirement coverage check

| Requirement | Story | Status |
|---|---|---|
| FR-037 — start a run in a test project the author belongs to | BSB-24-PENDING-1 | Covered, but the "project member" (non-owner) path is unexercised (Finding 4). |
| FR-145 — choice of skills branch | BSB-24-PENDING-1 | Covered. |
| FR-146 — choice of input branch | BSB-24-PENDING-1 | Covered. |
| FR-147 — choice of workflow and step context | BSB-24-PENDING-2 | Covered. |
| FR-148 — optional reviewer feedback or upstream handoff | BSB-24-PENDING-3 | Covered. |
| FR-149 — choice of model profile | BSB-24-PENDING-4 | Covered. |
| FR-150 — choice of model tier | BSB-24-PENDING-4 | Covered. |

- No requirement in `epic-map.json:66` is claimed by two stories, and no mapped requirement is
  unclaimed. `story-map.json` matches the "Covered requirements" headers in `stories.md:65-68,
  183-184, 252-253, 327-329` and the epic list in `epics.md:699-706`.
- FA-6's packaging requirements FR-038 to FR-043 belong to BSB-25, and execution/guardrail
  requirements to BSB-26/BSB-27; PENDING-1's Out of scope correctly defers them
  (`stories.md:70-78`). The epic does not drift into packaging or execution.
- NFR-006 is mapped to BSB-23 in the epic map but is consumed here; Finding 3 is the gap.
- Epic DoD (`epics.md:694-697`): non-member refusal is covered (`stories.md:40-43`); selections
  are recorded (`stories.md:36-38, 154-156, 233-245, 298-300`); the input branch is treated as
  read-only (`stories.md:113-114`); "a project member can start a run" is only proven for the
  owner (Finding 4).

## Dependency-note sanity check

- **All referenced keys exist.** Within the epic: BSB-24-PENDING-1/-2/-3/-4. Cross-epic:
  BSB-18, BSB-19-PENDING-1, BSB-22-PENDING-1/-3, BSB-23-PENDING-2/-3/-6, BSB-25, BSB-26,
  BSB-27, BSB-31-PENDING-1, BSB-32, BSB-33, BSB-34, BSB-36, BSB-37. No note points at a
  non-existent story.
- **Reciprocity is mostly good.** BSB-22-PENDING-3 names BSB-24 (`BSB-22/_epic/stories.md:210-211`),
  BSB-23-PENDING-6 names BSB-24 (`BSB-23/_epic/stories.md:468`), and BSB-31-PENDING-1 names
  BSB-24 (`BSB-31/_epic/stories.md:91-96`). BSB-19-PENDING-1 and BSB-23-PENDING-2/-3 are upstream
  suppliers and do not need a reverse note.
- **Finding 1:** PENDING-1's prose implies a dependency on PENDING-4 that its dependency list
  omits; adding it creates PENDING-1 ↔ PENDING-4. The fix is to make the edge one-way.
- **PENDING-2/-3:** neither names PENDING-4, although both submit `model_profile_id`/`tier`
  (PENDING-4's required fields). A one-line note is enough; no ordering edge is needed if
  PENDING-4 only appends validation.
- **Finding 3:** PENDING-1's note "BSB-23-PENDING-6 for the run-purpose filter" conflates the
  AI-model filter with the source-control test-purpose check. Correct the wording.
- **Stale cross-epic note:** BSB-31-PENDING-1 says "BSB-24's epic does not currently name this
  call" (`BSB-31/_epic/stories.md:95-96`); BSB-24-PENDING-1 now names
  `POST /api/builds/7/scans/static` and its position (`stories.md:118-120`). BSB-31's note is
  stale and should be updated on its next revise pass.
- **Cross-epic ordering conflict:** BSB-27's implementation guidance puts the preflight and
  static-scan precondition "before a bundle or branch is prepared" (`epics.md:873-874`);
  BSB-24-PENDING-1 puts the scan after BSB-25 resolves `skills_commit_sha` and creates the run
  branch (`stories.md:116-120`). The scan route takes a resolved SHA and a bundle, so the BSB-24
  order is the implementable one; BSB-27's wording should change when its stories are written.
  This is the same open item recorded in the BSB-31 review; it is not a BSB-24 story defect.
- **Data-model handoff:** PENDING-1's `runs.build_id` note (`stories.md:87-88`) is explicit and
  consistent with ADR SK-001 §9, which does not list the column.
