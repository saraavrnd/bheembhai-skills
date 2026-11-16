# Epic Review — BSB-28: Jira fixture seeding

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-28-PENDING-1, BSB-28-PENDING-2, BSB-28-PENDING-3, BSB-28-PENDING-4, BSB-28-PENDING-5

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-28/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item
  umbrella rather than a Jira issue. A read-only `GET /rest/api/3/issue/SkillBuilder-2` returned
  HTTP 404 ("Issue does not exist or you do not have permission to see it."), matching
  `PRD.md` §8 and the source note in BSB-28's own `stories.md:30-37`. The Atlassian MCP server is
  configured in `.mcp.json`, but this session exposed no Atlassian MCP tools, so the configured
  site (`https://saraavrnd.atlassian.net`) was queried read-only through its REST API (GET only;
  no Jira writes).
- **The epic this run reviews is BSB-28.** The branch HEAD (`a0c69d8`) is the
  `sdlc-plan-stories-write` step (run `434beb1b-3784-4840-bdc9-e18d2cf14478`) that wrote
  `BSB-28/_epic/stories.md` and `story-map.json`; `config/sdlc-wf-planning-epic.yaml` runs
  `sdlc-plan-epic-review` immediately after that step for the same epic. Jira
  `GET /rest/api/3/issue/BSB-28` returned HTTP 200: Epic "Jira fixture seeding", status To Do,
  labels FA-9/Later, no parent, no sub-tasks and no issue links. BSB-28 has no prior
  `epic-review.md` and no `revisions.md`, so this is the first review pass.
- **All 5 stories in BSB-28**, from `stories.md` and `story-map.json` in one read each:
  BSB-28-PENDING-1 through BSB-28-PENDING-5 (the full set, not a sample). `story-map.json` maps
  FR-058 to FR-062, one requirement per story, and the coverage table at `stories.md:54-66`
  maps the same five requirements to named acceptance criteria.
- **`PRD.md`** — §5 FA-9, §6 FR-058 to FR-062 (`PRD.md:132-136`), §7 NFR-002, NFR-004 and
  NFR-006 (`PRD.md:252-256`), and §8's source note. `epic-map.json` assigns BSB-28 only
  FR-058 to FR-062; no NFR is mapped to this epic.
- **`epics.md`** — the BSB-28 section (`epics.md:1175-1225`): description, functional scope,
  the seven-step implementation guidance, the Definition of Done, the five covered
  requirements and the Notes. Also read for the hand-offs this epic consumes: BSB-22 (projects,
  membership and the settings page), BSB-23 (Jira integrations and the redaction rule), BSB-24
  (run start), BSB-25 (packaging and the `prepared` transition), BSB-26 (execution and terminal
  classification), BSB-27 (deadline; epic only) and BSB-33 (run report and Jira capture).
- **`docs/adr/SK-001-skill-builder.md`** — §5's "Jira test data" paragraph
  (`SK-001:250-254`: `fixtures/<name>/jira.json`, aliases written `{{bug}}`, the post-run state
  and cleanup, the nightly sweep, and the open question "a fresh Jira project per run, or one
  project with a `skilltest-<run>` label") and §9's data model (`SK-001:345-357`), whose
  `run_jira` table lists `run_id`, `aliases`, `state_after` and `cleaned_at` but neither
  `cleaned_count` nor `state_before`/`changes`/`capture_error`, and which has no
  `fixture_sweeps` table.
- **Other story sets checked for the hand-offs this epic depends on:** BSB-22-PENDING-1 and
  BSB-22-PENDING-4 (project/membership row, settings page and owner guard); BSB-23-PENDING-1,
  BSB-23-PENDING-5 and BSB-23-PENDING-6 (Jira integration shape, the shared redaction rule and
  the test-purpose filter); BSB-24-PENDING-1 (run row and the "Jira is not a run-start choice"
  sentence); BSB-25-PENDING-1 and BSB-25-PENDING-3 (the preparation worker, the trigger that
  starts preparation, and the `prepared` transition); BSB-26-PENDING-1 and BSB-26-PENDING-3
  (launch environment and terminal classification); BSB-33-PENDING-1 and BSB-33-PENDING-4 (run
  page frame and the Jira before/after capture).
- **Prior reviews read:** BSB-33's review in full, especially Finding 5 (the `run_jira` column
  split and the missing run-start snapshot) and its Open question 5; BSB-34's review for
  severity/output precedent; the relevant findings of BSB-22, BSB-23, BSB-25 and BSB-26's
  reviews (settings/integrations ownership, the redaction helper's one-sided contract, the
  launch-environment omissions, and the test-purpose admission at launch).
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md`.
  There is therefore no project-wide UI convention for the page PENDING-5 asserts; the review
  relies on the owning stories named below.

## Findings

### Finding 1 — Epic-wide lifecycle trigger ownership: no story owns the pre-launch seeding call, the post-terminal capture/cleanup call, or the ordering that makes them safe

- **Severity:** Blocking
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-3, BSB-28-PENDING-4. Cross-epic:
  BSB-25-PENDING-1/-3, BSB-26-PENDING-1/-3, BSB-27.
- **Evidence:**
  - BSB-28 `stories.md:42-45` states the ordering as a fact: "PENDING-1 runs after a run reaches
    `prepared` and before BSB-26 launches the agent container; BSB-26-PENDING-1's launch contract
    gains the `BB_JIRA_FIXTURES` environment variable in PENDING-2." PENDING-1's first scenario
    is "When the run reaches state 'prepared' and the builder seeds its fixture before
    execution" (`stories.md:82`), and its Notes say "Seeding happens after the run is 'prepared'
    and before BSB-26 launches the container, so a seeding failure never starts execution"
    (`stories.md:137-140`).
  - No story implements that ordering. BSB-25-PENDING-1's Notes say it "owns the trigger that
    starts preparation" and that preparation is resolver → packager → branch preparer, with
    BSB-25-PENDING-3 setting `prepared` only after all three succeed
    (`BSB-25/_epic/stories.md:94-101`); BSB-25-PENDING-3's out-of-scope names "Jira fixture
    seeding (BSB-28)" and ends at `prepared` (`BSB-25/_epic/stories.md:271-279,300-303`).
  - BSB-26-PENDING-1 reacts directly to `prepared`: "When the execution worker processes run 21"
    → "the stub runtime adapter's container-start counter is 1" (`BSB-26/_epic/stories.md:63-64`).
    Its enumerated launch environment is `BB_SKILL_URL`, `BB_SKILL_SHA256`, `RUN_BRANCH`,
    `BB_CONTEXT` and the injected integration values; it does not contain `BB_JIRA_FIXTURES`.
    Its out-of-scope explicitly excludes "Jira fixture seeding (BSB-28)"
    (`BSB-26/_epic/stories.md:92-94`). The launch-environment Notes name the ADR contract and
    never mention fixtures (`BSB-26/_epic/stories.md:104-118`).
  - The post-terminal side has the same hole. BSB-28-PENDING-3 starts "When the run reaches a
    terminal state and the builder records the Jira state for fixture assertions, before cleanup
    runs" (`stories.md:220-221`), and PENDING-4 starts "When run 21 reaches a terminal state and
    the builder cleans up its seeded issues" (`stories.md:277-278`). BSB-26-PENDING-3 "owns the
    classification of the execution, the terminal execution values of `runs.state`"
    (`BSB-26/_epic/stories.md:280-282`) but nowhere calls either step; its out-of-scope names
    Jira fixture seeding only. BSB-27 owns the deadline outcome and has no stories yet.
- **What is missing/ambiguous/contradictory:** There is no state between `prepared` and
  `running`, so a seeding step triggered by `prepared` races the execution worker that is also
  triggered by `prepared`. If the execution worker wins, the container starts before the fixture
  exists, `BB_JIRA_FIXTURES` cannot be in its environment, and PENDING-1's "a seeding failure
  never starts execution" guarantee is false. At the other end, a run can reach a terminal state
  and be picked up for a later step without `state_after` ever being recorded or cleanup ever
  running; the nightly sweep is the only fallback for the issues, and no story defines who
  invokes capture/cleanup at the terminal transition.
- **Question (if a person must decide):** Which story owns the pre-launch seeding call and the
  post-terminal capture → cleanup call, and how is the ordering enforced (a new lifecycle state,
  a synchronous step in the `prepared` setter, or an explicit hand-off in BSB-26-PENDING-1/-3)?
  (also Open question 1)
- **Proposed change:**
  - **BSB-28-PENDING-1:** name the component that invokes seeding and the exact point in the
    lifecycle; add an acceptance criterion that the execution worker does not start a container
    until seeding has completed and that a seeding failure leaves the run `failed_infra` with a
    container-start counter of 0 (the existing failure scenarios assert the counter, but not the
    ordering against the worker).
  - **BSB-28-PENDING-3 and -4:** name the terminal-transition owner in Notes and dependencies
    and add a scenario that a terminal event runs capture and then cleanup once; state whether a
    missed hook is recoverable (for example, the nightly sweep deletes issues but cannot
    reconstruct `state_after`).
  - **Cross-epic (not applied here):** BSB-26-PENDING-1 must accept the `BB_JIRA_FIXTURES`
    hand-off or explicitly delegate the seeding call; BSB-26-PENDING-3 (or BSB-27 when its
    stories are written) must call BSB-28's capture and cleanup after setting the terminal
    state. BSB-25-PENDING-3 is the natural place to call seeding before it sets `prepared`, but
    only if the epic accepts that the run is not "prepared" until seeding succeeds.

### Finding 2 — Cross-epic record ownership: BSB-28-PENDING-3 and BSB-33-PENDING-4 both write `run_jira.state_after`, and they disagree on whether a no-fixture run gets a `run_jira` row

- **Severity:** Blocking
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-3. Cross-epic: BSB-33-PENDING-4.
- **Evidence:**
  - BSB-28 `stories.md:50-52`: "PENDING-3 owns `run_jira.state_after`; BSB-33-PENDING-4 owns the
    report's display-oriented `state_before`, `changes` and `capture_error`, and must read this
    recorded snapshot rather than maintain a second post-run capture."
  - BSB-28-PENDING-3's Notes repeat the claim: "This story owns the write of
    `run_jira.state_after` named by ADR SK-001 section 9" (`stories.md:251-252`); "The capture
    happens once, when the run reaches a terminal state and before PENDING-4 deletes the seeded
    issues" (`stories.md:256-258`). Its first scenario asserts the row's `state_after`
    (`stories.md:220-221`).
  - BSB-33-PENDING-4 asserts the same write: after its terminal capture, "the `run_jira` row for
    run 21 has `state_before` …, `state_after` … and `changes` …"
    (`BSB-33/_epic/stories.md:266-268`). Its Notes say "the builder takes the project snapshot
    when the run starts, takes it again when the run reaches a terminal state, and persists the
    field-level differences as `run_jira.changes`" (`BSB-33/_epic/stories.md:304-306`), and
    "`run_jira.state_after` remains the post-run snapshot ADR SK-001 names"
    (`BSB-33/_epic/stories.md:313`).
  - BSB-33-PENDING-4's out-of-scope disclaims "recording `run_jira.state_after` for fixture
    assertions (FR-060, BSB-28)" (`BSB-33/_epic/stories.md:291-293`) but does not disclaim the
    `state_after` write its own first scenario asserts, so the disclaimer and the acceptance
    criterion contradict each other.
  - Row lifecycle differs. BSB-28-PENDING-3's second scenario requires that for a completed run
    in a Jira-configured project with no seeded fixture, "no 'run_jira' row is created for run
    24" (`stories.md:223-226`). BSB-33-PENDING-4 creates a `run_jira` row for its before/after
    capture. Its no-changes scenario still asserts a row with `state_before` equal to
    `state_after` and `changes []` (`BSB-33/_epic/stories.md:271-273`), and it only says no row
    exists when the project has no Jira integration at all
    (`BSB-33/_epic/stories.md:282-289`). A Jira-configured, no-fixture run therefore gets a row
    under BSB-33's scenarios and no row under BSB-28's.
- **What is missing/ambiguous/contradictory:** The same column has two claimed writers and two
  claimed capture moments. Depending on which story is implemented first, `state_after` is
  either overwritten by a second terminal read (defeating "must read this recorded snapshot") or
  never written for the report's scenario. The `run_jira` row's existence is also a shared
  invariant with opposite requirements. BSB-33's review Finding 5 already recorded the BSB-33
  side and asked for one contract; BSB-28's stories now choose "PENDING-3 owns it" without
  revising BSB-33-PENDING-4, so the contradiction is still in the plan set.
- **Question (if a person must decide):** Which story is the single writer of
  `run_jira.state_after`, and does a run in a Jira-configured project with no fixture get a
  `run_jira` row? (also Open questions 2 and 3)
- **Proposed change:**
  - **BSB-28-PENDING-3:** state the single-writer contract explicitly, including what
    BSB-33-PENDING-4 must read and must not update; add a scenario where BSB-33's report opens
    the run and the stub Jira read counter does not increase (the story has this for later edits,
    but not for a second consumer process). Decide and assert the no-fixture row rule.
  - **Cross-epic (not applied here):** BSB-33-PENDING-4 must either read BSB-28's recorded
    `state_after` and own only `state_before`/`changes`/`capture_error`, or be named as the sole
    writer and BSB-28-PENDING-3 must read it. Whichever is chosen, the same rule must cover the
    no-fixture row.

### Finding 3 — Cross-epic capture boundary: BSB-33's run-start snapshot predates seeding, so seeded issues become "changes" the run appears to have made, and capture-vs-cleanup ordering is undefined

- **Severity:** Blocking
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-3, BSB-28-PENDING-4. Cross-epic:
  BSB-33-PENDING-4.
- **Evidence:**
  - BSB-33-PENDING-4's Notes define attribution as a run window: "the builder takes the project
    snapshot when the run starts, takes it again when the run reaches a terminal state, and
    persists the field-level differences as `run_jira.changes`. The run window is the
    attribution boundary" (`BSB-33/_epic/stories.md:304-311`). Its first scenario's
    `state_before` contains only the pre-existing issue and `changes` includes the newly created
    issue as `"change": "created"` (`BSB-33/_epic/stories.md:266-268`).
  - BSB-28 seeds "after the run is 'prepared' and before BSB-26 launches the container"
    (`stories.md:137-140`), so seeding happens after run preparation but before the agent runs.
    BSB-28-PENDING-3 captures before cleanup (`stories.md:256-258`), and PENDING-4 says cleanup
    "runs after the post-run state is recorded so the snapshot still describes the seeded
    issues" (`stories.md:319-323`).
  - BSB-33-PENDING-4 names BSB-28 only in out-of-scope ("Jira fixture seeding, alias
    substitution, cleanup and the nightly sweep (BSB-28, Later)", `BSB-33/_epic/stories.md:291-293`);
    it never states whether `state_before` is taken before or after seeding, or that cleanup
    must run after its terminal snapshot.
- **What is missing/ambiguous/contradictory:** If BSB-33's `state_before` is taken "when the run
  starts" before seeding, every seeded issue appears in `changes` as a run-created issue, so the
  report attributes the builder's own fixture to the skill. If it is taken after seeding, the
  story's wording must say so and name the seeding step; otherwise two implementers will choose
  opposite orders. The terminal side has the mirror race: if cleanup runs before BSB-33's capture,
  every seeded issue appears as `"deleted"`; if capture runs first, the snapshot is correct. The
  two epics state the correct order in different places but do not share it.
- **Question (if a person must decide):** Is `state_before` taken after seeding and `state_after`
  before cleanup, so seeded issues do not appear as run-created or run-deleted, and which story
  states that ordering as a shared contract? (also Open question 4)
- **Proposed change:**
  - **BSB-28-PENDING-3:** state the full order in Notes — seed → BSB-33's `state_before` (or
    exclude the seeded keys explicitly) → run → `state_after` → cleanup — and name
    BSB-33-PENDING-4 as the other consumer.
  - **BSB-28-PENDING-1:** state that seeding completes before the run window's before-snapshot;
    add the fixture-run variant to PENDING-3's acceptance criteria if the snapshot is BSB-33's.
  - **Cross-epic (not applied here):** BSB-33-PENDING-4 must state the same order and either
    exclude the seeded keys from `changes` or define how they are labelled.

### Finding 4 — Cross-epic integration contract: "the project's configured test Jira project" is undefined for template-project, non-test-only, and multiple Jira integrations

- **Severity:** Blocking
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-3, BSB-28-PENDING-4, BSB-28-PENDING-5.
  Cross-epic: BSB-23-PENDING-1, BSB-23-PENDING-6, BSB-24-PENDING-1.
- **Evidence:**
  - BSB-23-PENDING-1 permits either a `project_key` or a `template_project`: its second scenario
    saves a Jira integration "config containing site_url …, template_project 'BSB' and test_only
    true and … no project_key value" (`BSB-23/_epic/stories.md:35-38`). BSB-28-PENDING-1 says the
    fixture "may not carry a 'project_key' because the integration's 'project_key' is the only
    write target" (`stories.md:135-136`), so a template-project integration has no write target
    and the seeding behavior is undefined.
  - Test-purpose filtering is inconsistent. BSB-28-PENDING-1's scenarios all supply
    `test_only: true` (`stories.md:81` and following) and its Notes say it depends on
    BSB-23-PENDING-1 for "the Jira integration's site URL, project key, test-only flag and opaque
    secret reference" (`stories.md:126-130`), but no scenario or sentence says what happens when
    the flag is false. PENDING-3 and PENDING-4 are silent. PENDING-5 alone filters: "The sweep
    visits every 'integrations' row of kind 'jira' whose config marks it 'test_only': true"
    (`stories.md:391-392`). BSB-23-PENDING-6 owns the run-purpose filter
    `GET /api/projects/7/integrations?purpose=run` (`BSB-23/_epic/stories.md:451-481`), but
    BSB-24-PENDING-1 says "Jira is not a run-start choice: the run inherits the project's Jira
    integration when execution seeds or reads Jira (BSB-26 and BSB-28)"
    (`BSB-24/_epic/stories.md:122-124`), so BSB-28 never calls that filter. NFR-006 requires
    test-purpose credentials.
  - Multiplicity is undefined. BSB-23 rejects a second source-control integration with HTTP 409
    (`BSB-23/_epic/stories.md:150`) and duplicate model-profile names, but defines no uniqueness
    rule for Jira integrations. BSB-28 refers to "the project's configured test Jira project"
    singular (`stories.md:19-23,76`), while PENDING-1 seeds through "an 'integrations' row … kind
    'jira'" (`stories.md:81`) and PENDING-5 sweeps every test-only Jira integration
    (`stories.md:391-392`). With two test-only Jira integrations, the seed target, the capture
    target and the sweep scope can differ.
- **What is missing/ambiguous/contradictory:** The story set needs a single resolution rule for
  "the Jira integration this run uses": how many may exist, whether `project_key` is required,
  whether `test_only: true` is required, and what happens for `template_project` and for a
  non-test integration. Without it, PENDING-1 can fail with a nil `project_key`, seed a
  production project, or seed one project while PENDING-3 captures and PENDING-5 sweeps another.
- **Question (if a person must decide):** What is the resolution rule — exactly one Jira
  integration per project (and BSB-23 rejects a second), or a named selection among several; is
  `project_key` required for seeding; and is `template_project` refused? (also Open question 5)
- **Proposed change:**
  - **BSB-28-PENDING-1:** add the resolution rule and scenarios: no Jira integration (exists),
    `template_project` with no `project_key` (refused with an exact message), `test_only: false`
    (refused or excluded), and more than one eligible integration (refused or a defined
    selection). Use the same rule in PENDING-3 and PENDING-4.
  - **BSB-28-PENDING-5:** state that the sweep uses the same resolved integration, not "every
    test-only Jira integration", unless the multiplicity answer says otherwise.
  - **Cross-epic (not applied here):** BSB-23-PENDING-1 should either reject a second Jira
    integration or name the selection rule; BSB-23-PENDING-6's test-purpose filter should be
    named as the gate BSB-28 uses (or BSB-28 should implement its own explicit refusal).

### Finding 5 — Cross-epic page ownership: PENDING-5's six acceptance criteria assert a `GET /projects/7/integrations` page that no story defines, and cite the settings-page story for it

- **Severity:** Blocking
- **Stories touched:** BSB-28-PENDING-5. Cross-epic: BSB-22-PENDING-4.
- **Evidence:**
  - Every PENDING-5 scenario asserts that `GET "/projects/7/integrations"` renders the last-sweep
    line: `stories.md:348,353,358,363,368,373` (two projects in the failure scenario:
    `/projects/7/integrations` and `/projects/8/integrations`).
  - BSB-22-PENDING-4 owns `GET "/projects/7/settings"`, its "Integrations" section and the
    owner-only integration guard: "This story owns the project settings page at
    GET '/projects/7/settings', its 'Integrations' section and the owner-only
    integration-management guard" (`BSB-22/_epic/stories.md:259-262`). Its first scenario renders
    the section on that page (`BSB-22/_epic/stories.md:228-229`); the only
    `/projects/7/integrations` route it names is the "new" form
    `/projects/7/integrations/new` (`BSB-22/_epic/stories.md:229`).
  - PENDING-5's Notes cite the wrong page: "Depends on … BSB-22-PENDING-4 for the project
    integrations page the last-sweep line is added to" (`stories.md:389-391`). BSB-22-PENDING-4
    defines the settings page, not a `GET /projects/7/integrations` page.
  - PENDING-5's scenarios have no signed-in actor. BSB-22-PENDING-4's guard requires a signed-in
    project member for the settings page and returns HTTP 403 to a non-member
    (`BSB-22/_epic/stories.md:241-245`); a new `/projects/7/integrations` page would need its own
    access rule, which no story states.
- **What is missing/ambiguous/contradictory:** The acceptance criteria cannot pass as written:
  the route they assert has no owner, no template and no access rule. The dependency note points
  at a story that owns a different URL. A builder implementing PENDING-5 would either invent a
  page (and its guard) or silently render the line on the settings page and fail all six ACs.
- **Question (if a person must decide):** Does the last-sweep line belong on
  `GET /projects/7/settings` (the BSB-22-PENDING-4 Integrations section) or on a new
  `GET /projects/7/integrations` page, and if new, which story owns it and what is its access
  rule? (also Open question 6)
- **Proposed change:**
  - **BSB-28-PENDING-5:** change the six assertions to `GET "/projects/7/settings"` and add
    "Ada (user 42, role 'owner')" as the signed-in actor, if the settings page is chosen; or name
    the new page owner and add the route, its template and its membership/owner rule to the
    dependency notes. Correct the BSB-22-PENDING-4 citation either way.
  - **Cross-epic (not applied here):** BSB-22-PENDING-4 should name BSB-28 and the last-sweep line
    in its Integrations section if the settings page is the chosen home, and add a scenario for
    the line's empty/never-swept state.

### Finding 6 — Design-authority drift: the fixture alias syntax is `${alias}` in the stories but `{{bug}}` in ADR SK-001 §5

- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-2.
- **Evidence:**
  - `SK-001:250-254`: "Fixture files use aliases (`{{bug}}`), replaced with the real keys at seed
    time."
  - BSB-28-PENDING-2's Notes: "Alias tokens use the form `${alias}` in any string field of a
    fixture issue" (`stories.md:197-199`); its scenarios use `"Follow-up for ${bug}"` and assert
    that no created field contains `"${"` (`stories.md:162-169`).
  - BSB-28-PENDING-1 defines the fixture format and validation but never names the alias-token
    syntax (`stories.md:133-140`), so the change from the ADR is not recorded as a decision.
- **What is missing/ambiguous/contradictory:** The author-facing fixture format in the design
  authority and the one in the stories differ. A skill author following the ADR writes `{{bug}}`
  and the validator/substituter in these stories does not recognize it. A builder implementing
  the ADR writes `{{}}` and fails the stories' ACs.
- **Question (if a person must decide):** Which notation is the product format: adopt the ADR's
  `{{alias}}` in the stories, or keep `${alias}` and amend SK-001 §5? (also Open question 7)
- **Proposed change:**
  - **BSB-28-PENDING-2:** use the chosen notation consistently in the Notes and every scenario;
    if `${alias}` is retained, say why it deviates.
  - **BSB-28-PENDING-1:** name the alias-token syntax in the fixture-format paragraph and in the
    validation scenario.
  - **Cross-epic (not applied here):** if `${alias}` is retained, `SK-001` §5 needs a one-line
    amend (see Architecture impact).

### Finding 7 — Cross-story cleanup/sweep overlap: both delete the same marker issues, but neither defines delete-of-absent semantics or mutual exclusion

- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-4, BSB-28-PENDING-5.
- **Evidence:**
  - PENDING-4 deletes "exactly the issues in the integration's configured project carrying the
    label 'skilltest-' plus this run's id" at the terminal transition
    (`stories.md:319-323`); PENDING-5 deletes the same selector nightly (`stories.md:391-392`).
    Both can target the same issue.
  - PENDING-4's failure scenario says if any delete fails, the builder "leaves 'cleaned_at' and
    'cleaned_count' NULL" even though one of the two deletes succeeded
    (`stories.md:286-288`). PENDING-5's failure scenario says a failed project's issues "are not
    partially deleted beyond the requests Jira accepted" (`stories.md:400-402`) but does not say
    whether a 404 for an issue already deleted by PENDING-4 is a failure.
  - PENDING-5 decides leftovers from `runs.state` only (`stories.md:396-400`); it never reads
    `run_jira.cleaned_at`. PENDING-4's idempotence is based on `cleaned_at`
    (`stories.md:325-329`). The two idempotence mechanisms do not meet.
- **What is missing/ambiguous/contradictory:** If cleanup and the sweep overlap, one can receive
  a 404 for an issue the other just removed. Treating that as a failure would mark a successful
  cleanup "pending" forever (on the next sweep) or record a spurious sweep error. Treating it as
  success is the likely rule, but no story states it. There is also no statement that a sweep
  should skip markers whose run already has `cleaned_at` set.
- **Question (if a person must decide):** Is a 404 on delete treated as "already removed" success,
  and does the sweep skip runs whose `run_jira.cleaned_at` is set? (also Open question 8)
- **Proposed change:**
  - **BSB-28-PENDING-4:** state that a 404 for an issue already absent is success (not a failed
    delete) and count it as removed or not according to one rule; keep the "any real delete
    failure leaves both NULL" rule.
  - **BSB-28-PENDING-5:** skip markers whose `run_jira.cleaned_at` is non-NULL when a row exists,
    or state why it still deletes them; add the 404-as-success sentence to the failure scenario.
  - **Both:** state that the two paths may run concurrently and that the marker selector is the
    only coordination needed.

### Finding 8 — Epic-wide silent NFR-004/NFR-006: only PENDING-1 names the credential guarantee, and no story names BSB-23-PENDING-5's shared redaction helper

- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-3, BSB-28-PENDING-4, BSB-28-PENDING-5.
  Cross-epic: BSB-23-PENDING-5.
- **Evidence:**
  - PENDING-1's Notes say "The Jira provider is called with the test-purpose credential resolved
    from the secret store at call time; no credential value is persisted or rendered (NFR-004,
    NFR-006)" (`stories.md:130-131`).
  - PENDING-2, PENDING-3, PENDING-4 and PENDING-5 never mention NFR-004, NFR-006 or the redaction
    rule, although all four render Jira-derived text on `GET "/projects/7/runs/…"` or
    `GET "/projects/7/integrations"`: seeded counts and markers (`stories.md:83`), alias maps
    (`stories.md:169`), captured issue summaries/status/assignee/labels (`stories.md:221`),
    cleanup messages (`stories.md:278`) and sweep results/errors (`stories.md:348,368`).
  - BSB-23-PENDING-5 owns "the single redaction rule every builder surface applies"
    (`BSB-23/_epic/stories.md:408-412`); the credential value is replaced with "[REDACTED]" in
    the database, log, run result and interface. BSB-33's review Finding 3 already recorded that
    the helper's contract with BSB-26/BSB-33 is one-sided; BSB-28's stories are another consumer
    that never names it.
- **What is missing/ambiguous/contradictory:** The epic's requirement coverage is formally FR-only,
  but the feature handles a live Jira credential and renders tracker text. Leaving the redaction
  helper unnamed in four stories makes it likely that a new renderer (the "Jira fixture" sections
  and the sweep line) is built without the shared rule, which would violate NFR-004 if any error
  text or captured field ever contains the credential.
- **Question (if a person must decide):** None; this is a wording/ownership fix, not a product
  choice.
- **Proposed change:**
  - **BSB-28-PENDING-2/-3/-4/-5:** name BSB-23-PENDING-5's shared redaction helper in Notes and
    add a rendering assertion that the fixture/sweep sections pass through it, mirroring
    PENDING-1's sentence.
  - **Cross-epic (not applied here):** BSB-23-PENDING-5 should define the helper's input contract
    (text/document plus the run project's resolved credential values) so BSB-28 can call it.

### Finding 9 — Data-model hand-off: `fixture_sweeps` is a new table absent from ADR §9 and, unlike `cleaned_count`, has no "data-model stage must record it" sentence; the full `run_jira` schema remains split across epics

- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-3, BSB-28-PENDING-4, BSB-28-PENDING-5. Cross-epic:
  BSB-33-PENDING-4.
- **Evidence:**
  - BSB-28's header declares "PENDING-4 adds `run_jira.cleaned_count` … and PENDING-5 adds
    `fixture_sweeps` (`id`, `integration_id`, `started_at`, `finished_at`, `deleted_count`,
    `error`)" (`stories.md:16-19`).
  - PENDING-4 carries the hand-off sentence: "the data-model stage must record it"
    (`stories.md:325-326`). PENDING-5 says "Each integration's result is recorded in the new
    `fixture_sweeps` table" (`stories.md:400`) but never tells the data-model stage to create it.
  - ADR §9's `run_jira` row lists only `run_id`, `aliases`, `state_after` and `cleaned_at`
    (`SK-001:357`) and has no `fixture_sweeps` table at all (`SK-001:345-357`). BSB-33-PENDING-4
    adds `state_before`, `changes` and `capture_error` and does carry a hand-off sentence
    (`BSB-33/_epic/stories.md:300-302`).
- **What is missing/ambiguous/contradictory:** The new table has no explicit data-model owner,
  and the `run_jira` schema is declared in three places (ADR §9, BSB-33-PENDING-4 and
  BSB-28-PENDING-3/-4) with no single statement of the full column set or which story owns each
  column. This is the same class of gap BSB-33's review Finding 6 raised for `runs.diff_error`;
  BSB-28 repeats it for `fixture_sweeps`.
- **Question (if a person must decide):** None; this is a hand-off wording fix. The ownership
  question is Open question 2.
- **Proposed change:**
  - **BSB-28-PENDING-5:** add "the data-model stage must create `fixture_sweeps` with these
    columns" to Notes, matching PENDING-4's sentence.
  - **BSB-28-PENDING-3/-4:** add one Notes paragraph declaring the full `run_jira` column set and
    ownership (BSB-28: `aliases`, `state_after`, `cleaned_at`, `cleaned_count`; BSB-33:
    `state_before`, `changes`, `capture_error`, subject to Finding 2), and name the data-model
    stage for all of them.
  - **Cross-epic (not applied here):** ADR SK-001 §9 should be updated when the data-model stage
    lands; no architecture redesign is needed.

### Finding 10 — Cross-epic run-page reciprocity: BSB-28 adds four sections to the run page, but BSB-33-PENDING-1, which owns the page frame, never names BSB-28

- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-2, BSB-28-PENDING-3, BSB-28-PENDING-4.
  Cross-epic: BSB-33-PENDING-1.
- **Evidence:**
  - BSB-28's stories assert new read-only sections on `GET "/projects/7/runs/21"`: "Jira
    fixture: …" and "Run marker: …" (`stories.md:83`), "Aliases: …" (`stories.md:169`), "Jira
    fixture state: …" (`stories.md:221`) and "Jira fixture cleanup: …" (`stories.md:278`).
  - PENDING-1's Notes name the frame owner: "The run report gains a read-only 'Jira fixture'
    section on the page BSB-33-PENDING-1 frames" (`stories.md:144-147`).
  - BSB-33-PENDING-1's out-of-scope lists "the verdict, check, diff, Jira, turn and trace sections
    (BSB-33-PENDING-2 to -5)" and never names BSB-28 or a Jira fixture section
    (`BSB-33/_epic/stories.md:99-110`). Its Notes describe the page as extending BSB-26-PENDING-2's
    run page with a "What ran" section, with no slot for BSB-28.
- **What is missing/ambiguous/contradictory:** The page owner does not acknowledge the sections
  the later epic adds. A BSB-33 implementer can build a page layout that leaves no place for the
  fixture sections, and the BSB-28 ACs then fail on a page whose frame was never designed for
  them. The dependency is one-sided: BSB-28 names BSB-33, but BSB-33 does not name BSB-28.
- **Question (if a person must decide):** None; this is a reciprocity note.
- **Proposed change:**
  - **BSB-28-PENDING-1/-2/-3/-4:** cite the exact section list and anchor (for example, after
    "What ran") rather than only "the page BSB-33-PENDING-1 frames".
  - **Cross-epic (not applied here):** BSB-33-PENDING-1's out-of-scope/Notes should name BSB-28's
    four read-only fixture sections so the frame reserves space for them.

### Finding 11 — Cross-story boundary between PENDING-1 and PENDING-2: PENDING-2 disclaims fixture validation but owns alias validation that must run before PENDING-1 creates anything, and both stories claim the alias-map write

- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-2.
- **Evidence:**
  - PENDING-2's out-of-scope starts "Reading and validating the fixture, creating issues and
    applying the run marker (BSB-28-PENDING-1)" (`stories.md:184-186`), but its third scenario is
    a fixture-validation failure: an undefined alias is refused with zero create requests
    (`stories.md:162-166`), and its Notes say an undefined, forward or circular reference "fails
    validation before any issue is created" (`stories.md:197-199`).
  - PENDING-1's out-of-scope assigns "replacing aliases with created keys and handing the alias
    map to the skill (BSB-28-PENDING-2)" (`stories.md:114-116`), while its first scenario already
    asserts the `run_jira` row's `aliases` map after seeding (`stories.md:83`). PENDING-2's Notes
    say "The alias map is persisted in 'run_jira.aliases'" (`stories.md:199-201`).
- **What is missing/ambiguous/contradictory:** Validation is split across the two stories: the
  behavior is specified in PENDING-2, but PENDING-2 disclaims "validating the fixture", and
  PENDING-1 owns the pre-create validation step. An implementer could create issues in PENDING-1
  and then discover an undefined alias in PENDING-2, violating PENDING-2's own zero-create AC.
  The alias-row write is similarly claimed twice. This is a smaller seam than Findings 1-5, but
  it is the same "two owners, one write" pattern.
- **Question (if a person must decide):** None; assign one validation pass and one alias-map
  writer.
- **Proposed change:**
  - **BSB-28-PENDING-1:** state that its pre-create validation pass includes the alias-reference
    rules (undefined, forward, circular) and that the alias map is written once, after all
    creates succeed.
  - **BSB-28-PENDING-2:** narrow its out-of-scope to "fixture syntax and issue creation
    (PENDING-1); alias resolution is this story's validation rule, executed inside PENDING-1's
    pre-create pass"; remove the duplicate claim to persisting `run_jira.aliases`, or state that
    it owns the write and PENDING-1's scenario only observes it.

### Finding 12 — Epic-wide scope: the "nightly" sweep has no owner for the nightly invocation, and PENDING-5 explicitly defers it

- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-5.
- **Evidence:**
  - The epic's functional scope and DoD claim "Run a nightly sweep that removes seeded issues
    carrying a run marker" (`epics.md:1193,1208-1211`).
  - PENDING-5's out-of-scope includes "defining the scheduler, installation settings or run
    frequency beyond the nightly invocation this story observes" (`stories.md:382-385`), and its
    Notes say "The sweep's nightly trigger is an implementation detail; this story asserts the
    invocation's effect, not the scheduler" (`stories.md:403-404`).
  - Its scenarios only say "When the nightly fixture sweep runs" (`stories.md:347,351,356,361,366,
    371`); no scenario asserts a schedule, a registration, or which component invokes the sweep.
- **What is missing/ambiguous/contradictory:** The requirement is "nightly", but no story makes it
  happen nightly. If an operator must invoke the sweep, FR-062 is not delivered by the product.
  This is the same pattern as Finding 1 at a lower frequency, and the story's own explicit
  deferral makes it an epic-wide scope gap rather than an implementation detail.
- **Question (if a person must decide):** Which component owns the nightly invocation (the
  platform's scheduler/cron, an installation setting, or an external operator), and is a
  registration/trigger story needed? (also Open question 9)
- **Proposed change:**
  - **BSB-28-PENDING-5:** name the scheduler owner and add a scenario that the sweep is registered
    to run nightly for projects with a test Jira integration (or state explicitly that an
    operator runs it, which would require revising FR-062's "nightly" wording). Keep the
    "implementation detail" sentence only if the owner is named elsewhere.

## Open questions

1. **Lifecycle hooks (Finding 1).** Which story owns the pre-launch seeding call and the
   post-terminal capture → cleanup call, and how is the order enforced — a new lifecycle state, a
   synchronous step in BSB-25-PENDING-3's `prepared` setter, or an explicit call in
   BSB-26-PENDING-1/-3? If BSB-26 owns it, does it accept `BB_JIRA_FIXTURES` in the launch
   contract?
2. **`run_jira.state_after` ownership (Findings 2 and 9).** Is BSB-28-PENDING-3 the single writer
   (and BSB-33-PENDING-4 reads the recorded snapshot), or is BSB-33-PENDING-4 the writer for the
   MVP report and BSB-28 reads it later? State the full `run_jira` column set and its owner.
3. **No-fixture row (Finding 2).** For a completed run in a Jira-configured project with no seeded
   fixture, does a `run_jira` row exist for the report's `state_before`/`state_after`, or is
   there no row (as BSB-28-PENDING-3 requires)?
4. **Capture boundary (Finding 3).** Is `state_before` taken after seeding and `state_after`
   before cleanup, so seeded issues are neither "created" nor "deleted" by the run? Does the
   report's `changes` list exclude builder-seeded issues?
5. **Jira integration selection (Finding 4).** Is there exactly one Jira integration per project
   (and BSB-23 rejects a second), or a selection rule among several? Is `project_key` required for
   seeding, and is `template_project` refused? Is `test_only: true` required?
6. **Last-sweep page (Finding 5).** Does the line belong on `GET /projects/7/settings` (the
   BSB-22-PENDING-4 Integrations section) or on a new `GET /projects/7/integrations` page? If new,
   which story owns the route, template and access rule?
7. **Alias syntax (Finding 6).** Adopt the ADR's `{{alias}}` in the stories, or keep `${alias}`
   and amend SK-001 §5?
8. **Cleanup/sweep race (Finding 7).** Is a 404 on delete "already removed" success, and does the
   sweep skip markers whose run has `run_jira.cleaned_at` set?
9. **Nightly scheduler (Finding 12).** Which component registers and invokes the nightly sweep,
   and does FR-062's "nightly" survive if an operator must invoke it?

## Proposed changes

`docs/product/epics/BSB-28/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them). Each bullet says which of the statement, acceptance criteria, out-of-scope and
notes/dependencies change; where it names only Notes/ACs, the story statement and out-of-scope
stay as written because the finding changes the contract, not the role:

- **BSB-28-PENDING-1** — Notes/ACs: name the pre-launch seeding trigger and its ordering against
  the execution worker, and add an AC that no container starts until seeding completes (Finding
  1); define the Jira-integration resolution rule including `template_project`, `test_only` and
  multiple integrations (Finding 4); include alias-reference validation and the single alias-map
  write in the pre-create pass (Finding 11); name BSB-23-PENDING-5's redaction helper (Finding 8).
- **BSB-28-PENDING-2** — Notes/ACs: use the chosen alias notation consistently (Finding 6);
  narrow the out-of-scope/validation boundary with PENDING-1 and drop the duplicate alias-write
  claim (Finding 11); name the redaction helper (Finding 8); reference the pre-launch trigger that
  supplies `BB_JIRA_FIXTURES` (Finding 1).
- **BSB-28-PENDING-3** — Notes/ACs: state the single-writer `run_jira.state_after` contract and
  the no-fixture row rule (Finding 2); state the seed → `state_before` → run → `state_after` →
  cleanup order and the exclusion of seeded keys from `changes` (Finding 3); name the terminal
  trigger owner (Finding 1); declare the full `run_jira` column set and the data-model hand-off
  (Finding 9); name the redaction helper (Finding 8).
- **BSB-28-PENDING-4** — Notes/ACs: state 404-as-already-removed and the sweep interaction
  (Finding 7); name the terminal trigger owner (Finding 1); repeat the full `run_jira` contract
  and keep the `cleaned_count` data-model hand-off (Findings 2 and 9); name the redaction helper
  (Finding 8).
- **BSB-28-PENDING-5** — ACs/Notes: use `GET "/projects/7/settings"` with a signed-in owner, or
  name the new page owner and access rule (Finding 5); use the same resolved Jira integration as
  PENDING-1/-3/-4 (Finding 4); add the `fixture_sweeps` data-model hand-off (Finding 9); add the
  sweep/cleanup 404 and `cleaned_at` rules (Finding 7); name the nightly scheduler owner (Finding
  12); name the redaction helper (Finding 8).
- **Epic header** — Correct the cross-epic hand-off paragraph (`stories.md:42-52`) to match the
  chosen lifecycle and `run_jira` ownership, and add the `fixture_sweeps` table to the schema
  summary if it remains a BSB-28 deliverable.

Cross-epic follow-ups (not applied here):

- **BSB-26-PENDING-1** — Accept the `BB_JIRA_FIXTURES` environment variable and the pre-launch
  seeding call, or explicitly hand both to the story chosen in Open question 1 (Finding 1).
- **BSB-26-PENDING-3 / BSB-27** — Call BSB-28's terminal capture and cleanup after setting a
  terminal state, or name the story that does (Finding 1).
- **BSB-25-PENDING-3** — If seeding is made part of the `prepared` transition, call it before
  setting `prepared`; otherwise state that `prepared` means seeding is complete (Finding 1).
- **BSB-33-PENDING-4** — Choose the single `state_after` writer and the no-fixture row rule
  (Findings 2 and 3); state the run-start/terminal snapshot order relative to seeding and cleanup;
  keep its `state_before`/`changes`/`capture_error` data-model hand-off (Finding 9).
- **BSB-33-PENDING-1** — Name BSB-28's four read-only "Jira fixture" sections in the run page's
  out-of-scope/Notes (Finding 10).
- **BSB-22-PENDING-4** — If the last-sweep line belongs on the settings page, add it to the
  Integrations section and add a scenario for the never-swept state (Finding 5).
- **BSB-23-PENDING-1** — Either reject a second Jira integration or define the selection rule;
  state how a `template_project` integration is treated for seeding (Finding 4).
- **BSB-23-PENDING-5** — Define the shared redaction helper's input contract for BSB-28's fixture
  and sweep renderings (Finding 8; already requested by BSB-23's review Finding 6).
- **BSB-23-PENDING-6** — Name the run-purpose/test-purpose filter as the gate BSB-28 consumes, or
  state that BSB-28 enforces its own `test_only` refusal (Finding 4).
- **ADR SK-001** — Update §5 if `${alias}` is retained and §9 for `cleaned_count`, `fixture_sweeps`
  and the BSB-33 columns when the data-model stage lands (Findings 6 and 9).

## Architecture impact

None. The epic adds no new service, entity, endpoint or integration: seeding, capture, cleanup and
sweeping all use the existing Jira integration and REST API, the existing `runs` row and the
`run_jira` table. The new `run_jira.cleaned_count` column and the `fixture_sweeps` table are the
normal planning-to-design hand-off the later data-model stage records, exactly like the columns
BSB-33-PENDING-4 and BSB-26-PENDING-1 already declare; they are not a conflict with an existing
entity and do not require `sdlc-arch-design` first. The ADR's §5 open question (a fresh Jira
project per run versus one project with a `skilltest-<run>` label) is answered by these stories in
favor of the second option the ADR already lists, so no new design is needed. The only
design-authority drift is the alias notation (`{{bug}}` in SK-001 §5 versus `${alias}` in the
stories); aligning the stories to the ADR needs no design work, and keeping `${alias}` needs only
a one-line ADR §5 amend, not an architecture redesign. The lifecycle and page-ownership questions
above are product/story decisions, not missing architecture.

## Requirement coverage check

Yes for assignment; one caveat. `epic-map.json` assigns exactly FR-058, FR-059, FR-060, FR-061 and
FR-062, and each is claimed by exactly one story:

| Requirement | Assigned story | Covered by acceptance criteria? | Notes |
|---|---|---|---|
| FR-058 — seed Jira issues from a fixture into the configured project, marked with the run ID | BSB-28-PENDING-1 | Yes — six scenarios: seed and marker, malformed fixture, fixture-chosen project, no integration, mid-seed rollback, no fixture | The integration-resolution gaps in Finding 4 mean the "configured project" is not uniquely defined for every input. |
| FR-059 — replace fixture aliases with created issue keys | BSB-28-PENDING-2 | Yes — four scenarios: substitution, launch map, undefined alias, two runs | Alias notation and validation ownership: Findings 6 and 11. |
| FR-060 — record the post-run Jira state for fixture assertions | BSB-28-PENDING-3 | Yes — four scenarios: record and show, no fixture, read failure, later edits | The write is also claimed by BSB-33-PENDING-4; coverage exists but the contract contradicts a sibling epic (Finding 2). |
| FR-061 — clean up seeded issues at run end, only those marked with the run ID | BSB-28-PENDING-4 | Yes — six scenarios: completed, failed, partial failure, second cleanup, no fixture, other project | Cleanup trigger and sweep overlap: Findings 1 and 7. |
| FR-062 — nightly sweep removes marked issues | BSB-28-PENDING-5 | Yes — six scenarios: sweep, active run, orphan, lookalike labels, one project failing, second sweep | The asserted page route is unowned (Finding 5) and the nightly trigger is deferred (Finding 12). |

No NFR is assigned to BSB-28 by `epic-map.json`. NFR-004 and NFR-006 still apply because the epic
handles a live test Jira credential; only PENDING-1 names them, and no story names BSB-23-PENDING-5's
shared redaction helper (Finding 8). No requirement is duplicated across two stories, but FR-060's
`state_after` write is duplicated across two epics (Finding 2).

## Dependency-note sanity check

Yes for existence, no for reciprocity. Every named story key exists on disk: BSB-18,
BSB-22-PENDING-1, BSB-22-PENDING-4, BSB-23-PENDING-1, BSB-24-PENDING-1, BSB-25-PENDING-1,
BSB-26, BSB-26-PENDING-1, BSB-33-PENDING-1 and BSB-33-PENDING-4. BSB-27 is an epic with no story
folder yet; the dependency on "BSB-27's deadline" is a legitimate forward dependency, but it must
be rechecked when BSB-27 is decomposed because no story yet promises the terminal-state guarantee
PENDING-5 relies on.

Mismatches:

- **PENDING-1's "BSB-26 for the pre-launch state"** (`stories.md:130`) is vague and is not
  reciprocated: BSB-26-PENDING-1 excludes seeding (`BSB-26/_epic/stories.md:93`) and its launch
  env has no `BB_JIRA_FIXTURES` (Finding 1).
- **PENDING-1/-3/-4's terminal dependency on "BSB-26 / BSB-27"** is one-sided: BSB-26-PENDING-3
  owns the terminal values but does not name BSB-28's capture or cleanup (Finding 1).
- **PENDING-3's "PENDING-3 owns `run_jira.state_after`; BSB-33-PENDING-4 … must read this recorded
  snapshot"** is contradicted by BSB-33-PENDING-4's own AC and Notes, which write `state_after`
  (Finding 2).
- **PENDING-5's "BSB-22-PENDING-4 for the project integrations page"** points at the settings
  page, while every PENDING-5 AC asserts `GET /projects/7/integrations`, which no story owns
  (Finding 5).
- **PENDING-1's "the page BSB-33-PENDING-1 frames"** (`stories.md:144-147`) is not reciprocated:
  BSB-33-PENDING-1's out-of-scope never names BSB-28 (Finding 10).
- **PENDING-1's "BB_JIRA_FIXTURES in BSB-26-PENDING-1's launch contract"** is not reciprocated:
  BSB-26-PENDING-1's enumerated environment has no such variable (Finding 1).
- **PENDING-1's "test-only flag" dependency on BSB-23-PENDING-1** is named but not used: no
  scenario or rule says what a false flag does (Finding 4).

Reciprocal notes that are sound: BSB-23-PENDING-1's out-of-scope names "Jira fixture seeding and
cleanup (BSB-28)", BSB-24-PENDING-1's Notes name BSB-28 for the inherited Jira integration,
BSB-25-PENDING-3's out-of-scope names BSB-28, and BSB-33-PENDING-4's out-of-scope names BSB-28's
seeding/aliases/cleanup/sweep (the last is partial because its AC still writes `state_after`).
No circular dependency was found. Build order itself is `sdlc-plan-epic-sequence`'s job and is not
computed here.
