# Epic Review — BSB-28: Jira fixture seeding

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-15 · **Stories reviewed:** BSB-28-PENDING-1, BSB-28-PENDING-2, BSB-28-PENDING-3, BSB-28-PENDING-4, BSB-28-PENDING-5

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-28/_epic/epic-review.md`.

## Context loaded

- **Target resolution.** The run's target was `SkillBuilder`. That is the product title of
  `docs/product/PRD.md`, not a Jira issue. The `epics.md` handoff and the BSB-28 `stories.md` header
  both record this. No Atlassian (Jira) MCP tool was available in this session, so the epic was
  resolved from disk. BSB-28 is the epic the most recent `sdlc-plan-stories-write` run wrote
  (commit `b505892`), and it has no review yet. Its `stories.md` header says the epic was fetched
  read-only from Jira during decomposition and matches the BSB-28 section of `epics.md`. Nothing was
  read from or written to Jira in this pass.
- **All 5 BSB-28 stories**, from `docs/product/epics/BSB-28/_epic/stories.md` and
  `story-map.json`, the full set:
  - PENDING-1: seed the fixture as run-marked issues (FR-058).
  - PENDING-2: replace aliases with the created keys (FR-059).
  - PENDING-3: record post-run state (FR-060).
  - PENDING-4: end-of-run cleanup (FR-061).
  - PENDING-5: nightly sweep (FR-062).

  Also read the shared "Jira fixture contract" preamble. It covers the fixture constants, fixture
  selection, file format, seeding lifecycle, alias replacement, capture, cleanup, sweep, the Jira
  API contract, run state values, Open decisions 1–4 and the cross-epic notes.
- `docs/product/epic-map.json`: BSB-28 → FR-058 to FR-062, no NFRs. Also read the entries for
  BSB-23 (FR-029 to FR-036, NFR-004, NFR-006), BSB-27 (FR-056, NFR-007, NFR-008), BSB-33 (FR-140),
  BSB-34 (NFR-013, NFR-014) and BSB-37 (FR-122).
- `docs/product/PRD.md`: the FA-9 rows FR-058 to FR-062, FR-029, FR-056, FR-140, NFR-001 to
  NFR-019, and the §8 "Jira fixture marking" paragraph.
- `docs/product/epics.md`: the BSB-28 section (scope, edge cases, non-goals, notes). Also the
  BSB-33 (FA-13, Jira-change capture), BSB-34 (retention/purge) and BSB-37 (nightly scheduler)
  sections.
- `docs/adr/SK-001-skill-builder.md`, the committed design. This repo has no `architecture.md` or
  `data-model.md`. Read:
  - §1 (repo tree `fixtures/`);
  - §4 (integrations: Jira "project key or template project");
  - §5 ("Jira test data": `{{bug}}` aliases, record state "for assertions and display", nightly
    sweep);
  - §9 (`run_jira`, `runs`, `integrations` columns);
  - Open question 1 (Jira isolation);
  - Tests ("cleanup leaves no issues behind").

  Skimmed `SK-002` by keyword; it has nothing on Jira fixtures.
- Sibling epics checked for consumed contracts: BSB-26 `stories.md` (run-state table, terminal-write
  rule, claim contract, run page outcome texts, log contract, executor-restart reconciliation) and
  BSB-24 `stories.md` (sandbox branches such as `fixtures/empty-title`, `jira` integration
  fixture). BSB-23, BSB-27, BSB-29, BSB-33, BSB-34 and BSB-37 have no stories on disk; only their
  `epics.md` sections were read.
- **Left for `sdlc-plan-story-review`.** These are single-story points and are not raised below:
  - PENDING-1: the optional fixture `key` field can only ever fail, because Jira assigns keys.
  - PENDING-4: the `jira cleanup skipped` log prefix is missing from the contract's prefix list.
  - PENDING-5: the outcome of a failed sweep delete is unspecified.

## Findings

### Finding 1 — Epic-wide scope boundary: where a fixture is chosen, and who lets anyone set it, is undecided and unowned
- **Severity:** Blocking
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-2, BSB-28-PENDING-3, BSB-28-PENDING-4,
  BSB-28-PENDING-5 (every story keys off a seeded run, and whether a run is seeded depends on this);
  cross-epic BSB-23, BSB-24, BSB-27.
- **Evidence:**
  - `stories.md` "Fixture selection and enablement" (lines 87–93) pins the fixture as
    `config.fixture` on the project's `jira` integration. It says this is "an explicit decision of
    this decomposition, not a requirement" and lists it as Open decision 1.
  - Cross-epic note on BSB-23 (lines 200–204): "BSB-23 has no stories yet, so its decomposition
    must include `config.fixture`". BSB-23's FRs (FR-029 to FR-036) never mention fixtures, and
    BSB-23 is MVP while this epic is Later.
  - No BSB-28 story has an acceptance criterion that sets or changes `config.fixture`. Every
    PENDING-1 and PENDING-2 scenario starts from a row that already has it.
  - Open decision 4 (lines 193–196): a re-run (FR-056, BSB-27) uses "the project's current
    fixture". NFR-010 says "the same inputs … produce the same verification result".
  - SK-001 §5 lists the fixture beside the per-run inputs ("Before a run, the runner can seed
    issues from `fixtures/<name>/jira.json`"). BSB-24's sandbox fixture offers input branch
    `fixtures/empty-title`, which pairs naturally with fixture `bug-fix-empty-title`. Both point
    towards a per-run (per-input) choice.
- **What is missing/ambiguous/contradictory:**
  - It is open whether seeding happens at all for a run, and which data it seeds.
  - Under the current pin, no epic credibly delivers the means to turn seeding on. BSB-23 has no FR
    for it, and this epic excludes it.
  - Under the current pin, two runs of different skills in one project always get the same Jira
    data.
  - A re-run can silently get a different fixture than its parent.

  No single story shows this; it only appears when the five stories' Givens are set against the
  BSB-23/BSB-24/BSB-27 boundaries.
- **Question:** "Is the Jira fixture chosen per run (a run-start input next to the input branch,
  recorded on the run so re-runs reuse it) or per project (`config.fixture` on the `jira`
  integration)? Whichever it is, which story delivers the way an owner or author sets it: a new
  BSB-28 story, or a named BSB-23/BSB-24 story?"
- **Proposed change:**
  - **PENDING-1:** rewrite "Fixture selection and enablement" and the Givens to the chosen source.
    Add an acceptance criterion, or a new sibling story in this epic, that sets the fixture through
    the chosen route. Do not rely on an unwritten BSB-23 story.
  - **PENDING-1 notes:** name the epic and story that supply the fixture name.
  - **PENDING-2, PENDING-3, PENDING-4, PENDING-5:** no AC change. Their Notes should say they
    apply only to runs seeded under PENDING-1's rule.
  - **Contract, Open decision 4:** if the answer is per run, record the fixture name per run so a
    BSB-27 re-run reuses it (see Architecture impact). If per project, say explicitly that a re-run
    may seed a different fixture, and that NFR-010 does not cover Jira fixture content.
  - Remove Open decisions 1 and 4 once answered.

### Finding 2 — Cross-story contradiction: acceptance criteria assert behaviour the same story's Out of scope gives to a sibling, and the PENDING-3 ↔ PENDING-4 dependency is inverted
- **Severity:** Blocking
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-2, BSB-28-PENDING-3, BSB-28-PENDING-4
- **Evidence:**
  - **PENDING-1 vs PENDING-2.** PENDING-1's first scenario asserts
    `SELECT aliases FROM run_jira WHERE run_id = 1` equals `{"bug":"OLD-101","task":"OLD-102"}`
    (line 243). PENDING-1's Out of scope gives "storing the alias mapping" to PENDING-2 (line 304).
    PENDING-2's Out of scope gives "inserting the `run_jira` row" back to PENDING-1 (line 390).
    PENDING-2's notes depend on PENDING-1 "for the created issue keys and the `run_jira` row"
    (line 396). It is unclear which story writes `run_jira.aliases`.
  - **PENDING-3 vs PENDING-4.** PENDING-3 asserts cleanup results:
    - scenario "The state is captured before the issues are cleaned up" (lines 425–431): a
      `DELETE` order and `cleaned_at` = `2026-11-15T10:05:01Z`;
    - line 440: "cleanup still runs and sets `cleaned_at`";
    - lines 456–457: two `DELETE` requests and `cleaned_at`.

    Yet PENDING-3's Out of scope gives deletion to PENDING-4 (line 465), and its notes
    (lines 471–473) do not depend on PENDING-4. PENDING-4's notes say it depends on PENDING-3
    (line 553). As written, PENDING-3 cannot pass its own ACs until PENDING-4 is built, while the
    notes say the opposite. `sdlc-plan-epic-sequence` would order them wrongly.
  - **Finalizer ownership.** PENDING-3's trigger is "When the executor writes `runs.state`";
    PENDING-4's is "When the Jira finalizer runs". Neither story says it builds the finalizer hook
    itself: the step after the terminal write that runs capture and then cleanup.
  - PENDING-4 reads `run_jira.aliases` but its notes depend only on PENDING-1 and PENDING-3. That
    is consistent only if PENDING-1 writes the mapping, which PENDING-1's Out of scope denies.
- **What is missing/ambiguous/contradictory:** The story boundaries contradict each other. Two
  implementers could both build the alias-mapping write, or neither could. PENDING-3 and PENDING-4
  have a hidden two-way dependency.
- **Question:** none — this is a boundary/wording fix.
- **Proposed change:**
  - **PENDING-1:** owns inserting the `run_jira` row *including* `aliases`, since the mapping is
    known as soon as phase 1 finishes. Remove "and storing the alias mapping" from its Out of scope.
  - **PENDING-2:** owns only the phase-2 token replacement (the `PUT`s) and alias validation.
    Remove "The alias mapping is written in fixture order and is the only place…" from its notes,
    or reword it to say PENDING-1 writes the mapping.
  - **PENDING-3:** owns the finalizer hook (runs once after the terminal write, capture first).
    Its ACs assert only `state_after`, the read requests, and that a capture failure does not stop
    the next finalizer step. Move the scenario "The state is captured before the issues are cleaned
    up" and the `DELETE`/`cleaned_at` assertions in the "deleted during the run" and "failed read"
    scenarios to PENDING-4.
  - **PENDING-4:** gains those moved assertions as "cleanup runs after capture, including when
    capture failed". Its notes keep "depends on PENDING-3" and also name PENDING-1 as the writer of
    `aliases`.

### Finding 3 — Cross-epic scope boundary: nobody consumes `state_after`, and cleanup may delete the seeded issues before BSB-33 records the run's Jira changes
- **Severity:** Blocking
- **Stories touched:** BSB-28-PENDING-3, BSB-28-PENDING-4; cross-epic BSB-33 (FR-140), BSB-29.
- **Evidence:**
  - PENDING-3's Out of scope (lines 466–468): "The fixture assertions themselves and any display of
    the recorded state; the run report, the durable Jira-change record and its display belong to
    epic BSB-33 (FR-140)."
  - The cross-epic note (lines 214–216): "This epic records `run_jira.state_after` for fixture
    assertions only; it does not compute a diff and does not add a run page region."
  - `epics.md` BSB-33: "Capture Jira changes through the run's Jira integration into a durable
    record, then display them". BSB-28's own `epics.md` notes: "fixture seeding is an additional
    source of that data".
  - The contract (lines 118–120) and PENDING-3's notes (lines 474–475): the finalizer runs
    "immediately after the executor writes a terminal `runs.state`, before epic BSB-29 verifies",
    and then deletes the issues (PENDING-4).
  - SK-001 §5: the state after the run is recorded "for assertions and display".
  - No PRD FR assigns *evaluating* fixture assertions to any epic.
- **What is missing/ambiguous/contradictory:**
  - PENDING-3 says BSB-33 owns the fixture assertions, but BSB-33 claims only the Jira-change record
    and its display, and the cross-epic note says BSB-28 owns `state_after` "for fixture assertions
    only". No epic reads `state_after`, and no API, page or verifier exposes it. An author cannot
    use it, so FR-060's "for fixture assertions" has no consumer.
  - BSB-33 (MVP, built first) captures Jira changes "through the run's Jira integration". If that
    capture runs after BSB-28's finalizer, a seeded run's issues are already deleted. The run page
    would then show no changes, or deletions the skill never made.
  - The ordering between the BSB-28 finalizer and BSB-33's capture is not written down in either
    epic.
- **Question:** "For a seeded run, should BSB-33's FR-140 record be built from
  `run_jira.state_after` (making BSB-28 a data source BSB-33 reads), or does BSB-33 capture
  independently? If independently, must BSB-28's cleanup wait until BSB-33's capture has finished?
  And is evaluating assertions against `state_after` deliberately left to no epic (the author reads
  the stored value), or does a story need to expose it?"
- **Proposed change:**
  - **PENDING-3:** correct Out of scope so it no longer attributes fixture assertions to BSB-33.
    State the answer: who reads `state_after`, and whether that is BSB-33's FR-140 record or an
    explicit "no consumer in this PRD".
  - **PENDING-3 and PENDING-4 notes, and the contract's "Post-run state capture" paragraph:** state
    where the finalizer sits relative to BSB-33's Jira-change capture, as well as BSB-29's
    verification.
  - **Contract, BSB-33 cross-epic note:** reword it to match. If BSB-33 must read `state_after`,
    say so as a dependency BSB-33's decomposition has to pick up.

### Finding 4 — Cross-story / cross-epic lifecycle: seeding and the finalizer run between BSB-26's and BSB-27's state writers, and the edges are unassigned
- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-3, BSB-28-PENDING-4, BSB-28-PENDING-5;
  cross-epic BSB-26, BSB-27.
- **Evidence:**
  - The contract (lines 102–109) runs seeding after the claim's compare-and-set, so the run is
    already `running`. PENDING-1's notes depend on BSB-23/24/25/26 but not on BSB-27.
  - BSB-26's terminal-write rule: "Epic BSB-27 writes its terminal state before it stops the
    container."
  - BSB-26 PENDING-1 notes: "After an executor restart, an executor finds its in-flight runs by the
    `bb.run_id` container label." A run that crashes mid-seed has no container.
  - PENDING-3 triggers the finalizer on "the executor writes `runs.state`". PENDING-3's notes and
    the BSB-27 cross-epic note (lines 211–213) say it runs "for every terminal state, including
    BSB-27's", but BSB-27's writer and BSB-26's restart reconciliation are not "the executor's" claim
    path.
- **What is missing/ambiguous/contradictory:**
  - **Deadline fires mid-seed.** If BSB-27's deadline writes `failed_timeout` during a slow seed,
    the finalizer runs with no `run_jira` row yet and does nothing. Seeding then inserts `run_jira`
    and may try to create a container for a terminal run.
  - **Crash between the terminal write and the finalizer.** A run that is terminal with
    `cleaned_at` `NULL` is never finalized again. PENDING-5 removes the issues, but `state_after`
    is never captured.

  Each story assumes another handles these edges.
- **Question:** none — the safe behaviour follows from rules already written.
- **Proposed change:**
  - **PENDING-1:** before inserting `run_jira` and before creating the container, seeding re-checks
    that the run is still `running`. If it is not (it lost the terminal write), it deletes what it
    created and writes no state. Add a BSB-27 deadline dependency to its notes.
  - **PENDING-3:** the finalizer runs after *every* terminal write, whichever writer made it
    (BSB-26 executor, BSB-26 restart reconciliation, BSB-27). Add a recovery rule: on executor
    startup, finalize terminal runs whose `run_jira.cleaned_at` is `NULL`.
  - **PENDING-4:** notes reference the same trigger.
  - **PENDING-5:** notes say it is the fallback when that recovery also fails, so `state_after` may
    then stay `NULL`.

### Finding 5 — Cross-story contradiction: `run_jira.cleaned_at` means different things in PENDING-4 and PENDING-5, and the shared contract's wording contradicts PENDING-4
- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-4, BSB-28-PENDING-5 (and the shared "Cleanup" contract both
  rely on).
- **Evidence:**
  - Contract "Cleanup" (lines 136–141): "Cleanup is all-or-nothing on errors: an unexpected Jira
    error … leaves other issues in place where possible … When every recorded key is deleted or
    already absent, `cleaned_at` is set".
  - PENDING-4's scenario "A deletion failure leaves the record uncleaned" (lines 532–541) deletes
    `OLD-101` and then fails on `OLD-102`. That is not all-or-nothing, and because the failure is on
    the last key it does not decide whether cleanup continues past a failed key.
  - Contract "Nightly sweep" (lines 150–151) and PENDING-5's first scenario: the sweep sets
    `cleaned_at` "when the sweep deletes at least one issue for a run".
- **What is missing/ambiguous/contradictory:**
  - PENDING-4 sets `cleaned_at` only when *every* recorded key is gone. PENDING-5 sets it when *at
    least one* is deleted. So a sweep that deletes one issue and fails on another marks the run
    cleaned.
  - A run whose issues are all already gone (for example, cleanup deleted them and then failed on a
    read) is never marked cleaned, because the sweep deletes nothing for it.
- **Question:** none.
- **Proposed change:**
  - **Contract "Cleanup":** replace "all-or-nothing" with the rule PENDING-4 actually tests. On an
    unexpected error for one key, cleanup continues with the remaining keys, leaves `cleaned_at`
    `NULL` and logs the failure. Add a PENDING-4 scenario where the *first* key fails, to pin it.
  - **PENDING-5 and the contract "Nightly sweep":** use the same meaning. The sweep sets
    `cleaned_at` for a run's `run_jira` row only when, after the sweep, no issue carrying that run's
    marker remains, which includes the case where it had nothing to delete.

### Finding 6 — Cross-story race: the sweep can delete a just-finished run's issues before PENDING-3 captures them
- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-3, BSB-28-PENDING-5
- **Evidence:**
  - Contract "Nightly sweep" (lines 147–149) and PENDING-5's notes (lines 628–630): the sweep skips
    only runs in `queued` or `running`. "Every other value is terminal".
  - Contract "Post-run state capture" (lines 118–128): capture runs after the terminal write, and
    an absent key is recorded as `"missing":true`.
- **What is missing/ambiguous/contradictory:** A run that becomes terminal just before 02:00 UTC is
  fair game for the sweep while its finalizer is still capturing. PENDING-3 would then record
  `"missing":true` for issues the *skill* never deleted. That is a false signal in the very data
  FR-060 exists to produce, and it is only visible with both stories side by side.
- **Question:** none.
- **Proposed change:**
  - **PENDING-5:** also skip a run whose `run_jira` row has `state_after` `NULL` and `cleaned_at`
    `NULL` while its finalizer is in progress. The two serialise on the run, for example by locking
    the `run_jira` row. Add a scenario: a terminal run with an in-progress finalizer is skipped.
  - **PENDING-3 notes:** reference the same serialisation.

### Finding 7 — Epic-wide scope boundary: integration settings that change or have no project key leave seeded issues unreachable
- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-4, BSB-28-PENDING-5; cross-epic BSB-23.
- **Evidence:**
  - Contract "Jira API contract" (line 154): every call uses the integration's *current*
    `config.site_url`. `run_jira` records only keys (SK-001 §9: `run_id`, `aliases`, `state_after`,
    `cleaned_at`).
  - PENDING-4 treats a key the site reports absent as already cleaned (line 135).
  - PENDING-5 searches the integration's *current* `project_key`. Its Out of scope excludes a
    *removed* integration (lines 619–620) but not a *changed* one.
  - Open decision 3 and PENDING-1's Out of scope exclude template-project integrations (FR-029),
    but no story says what happens at run time when such an integration has a fixture set. PENDING-5
    "iterates every project that has a `jira` integration" and searches its `project_key`, which a
    template-project integration does not have.
- **What is missing/ambiguous/contradictory:**
  - If the owner edits `site_url` or `project_key` (BSB-23) between seeding and cleanup, PENDING-4
    gets 404s on the new site and marks the run cleaned. PENDING-5 searches only the new project, so
    the marked issues on the old site/project are orphaned forever. The marker check still protects
    human issues.
  - The template-project case is excluded by every story but handled by none.
- **Question:** "When a project's Jira `site_url` or `project_key` changes while a seeded run has
  not been cleaned, should BSB-23 refuse the change until cleanup finishes, or should each seeded
  run record the site and project it seeded into?"
- **Proposed change:**
  - **PENDING-1:** add a scenario: a template-project `jira` integration (no `project_key`) with a
    fixture set → `failed_seed` with an exact `[skill-builder] jira fixture seed failed: ` line
    (instead of leaving it undefined).
  - **PENDING-4:** do not treat a 404 as cleaned when the recorded key's project prefix differs from
    the integration's current `project_key`. Leave `cleaned_at` `NULL` and log it.
  - **PENDING-5:** skip integrations without a `project_key`. Add "a changed integration" to Out of
    scope, or handle it per the answer.
  - **PENDING-1 notes and the BSB-23 cross-epic note:** state the answer.

### Finding 8 — Cross-story fit with the committed design: the alias token delimiter departs from SK-001 without a reason
- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-2
- **Evidence:**
  - SK-001 §5: "Fixture files use aliases (`{{bug}}`)".
  - Contract "Fixture file format" (lines 97–100) and Open decision 2 pin `@alias@`.
  - PENDING-1's `POST` bodies (lines 240–241) carry the raw `@task@` / `@bug@` tokens, and
    PENDING-2's scenarios parse them.
- **What is missing/ambiguous/contradictory:** Two stories hard-code a token form that differs from
  the design's, and no reason is recorded. Fixture files authored from the ADR would not resolve.
- **Question:** none — follow the committed design unless someone objects.
- **Proposed change:**
  - **PENDING-1 and PENDING-2, contract "Fixture file format", fixture JSON block:** use `{{alias}}`
    as in SK-001 §5. PENDING-1 changes only the raw tokens in its `POST` bodies. PENDING-2 changes
    the tokens in its scenarios and log lines.
  - Close Open decision 2.

### Finding 9 — Cross-epic architecture fit: two BSB-28 stories produce `failed_seed`, but no epic shows it on the run page
- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-2; cross-epic BSB-26, BSB-38.
- **Evidence:**
  - Contract "Run state values" (lines 174–177) and PENDING-1's notes (lines 321–322): BSB-26's
    "state table must gain it in a later revise pass".
  - The BSB-38 note (line 218): "The failure text BSB-26 shows for `failed_seed` is BSB-26's
    surface."
  - BSB-26's `stories.md` lists every sibling-owned terminal value (BSB-27's cap state, BSB-25's
    preparation failure) without `failed_seed`. Its run page "renders the outcome region with
    exactly one of these texts", for four states.
  - BSB-26 is MVP and this epic is Later.
- **What is missing/ambiguous/contradictory:** The claim on BSB-26 is one-sided. An MVP epic is
  asked to render a Later epic's state, and the author-visible outcome text for `failed_seed` is
  owned by nobody. Both PENDING-1 and PENDING-2 produce the state.
- **Question:** none.
- **Proposed change:**
  - **PENDING-1:** owns the `failed_seed` outcome text on the run page as an extension of BSB-26's
    table, for example the exact text `The Jira fixture could not be seeded.`, with a scenario.
  - **PENDING-2:** notes reference it.
  - **Contract "Run state values" and the BSB-26/BSB-38 cross-epic notes:** say that this epic adds
    the row and the text, so BSB-26 needs no revise pass, and that NFR-012 (BSB-38) applies to that
    region.

### Finding 10 — Dependency-note sanity: PENDING-5 depends on an "installation's scheduler" that no epic delivers before it
- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-5 (and the epic boundary).
- **Evidence:**
  - PENDING-5's notes (lines 626–627): "on the installation's scheduler (the epic's dependency note
    names a scheduler for this job)".
  - SK-001 defines no scheduler.
  - The only scheduler in `epics.md` is BSB-37's "nightly scheduler" for saved suites (FR-122, also
    Later).
- **What is missing/ambiguous/contradictory:** The daily 02:00 UTC trigger is assumed and not
  owned. If BSB-37 is built later than BSB-28, or not at all, nothing runs the sweep.
- **Question:** none.
- **Proposed change:** **PENDING-5** delivers its own installation-level daily trigger, with a
  scenario that pins `02:00` UTC. Its notes say BSB-37's suite scheduler may later reuse it, rather
  than depending on an unnamed scheduler.

### Finding 11 — Epic-wide silent NFRs: retention and purge (NFR-013, NFR-014) don't mention `run_jira`
- **Severity:** Advisory
- **Stories touched:** BSB-28-PENDING-1, BSB-28-PENDING-3; cross-epic BSB-34.
- **Evidence:**
  - PENDING-1 writes `run_jira.aliases`. PENDING-3 copies Jira `summary` and `status` values into
    `run_jira.state_after` (lines 120–124).
  - NFR-013/NFR-014 (BSB-34): run "transcripts, logs and results are retained only for a configured
    period … can be purged on request". BSB-34's edge case: "a purge must remove transcripts, logs
    and results together".
  - Neither BSB-28 story mentions retention, and BSB-34 (MVP) cannot know about a Later table.
- **What is missing/ambiguous/contradictory:** `run_jira` is run-result data that would survive a
  BSB-34 purge.
- **Question:** none.
- **Proposed change:** **PENDING-1 and PENDING-3 notes:** say the `run_jira` row is part of the
  run's results under NFR-013/NFR-014 and is removed with the run by BSB-34's retention and purge.
  Add a matching BSB-34 cross-epic note to the contract.

## Open questions

1. *(Finding 1)* Is the Jira fixture chosen per run (a run-start input recorded on the run, reused
   by re-runs) or per project (`config.fixture` on the `jira` integration)? Which story, in this
   epic or a named BSB-23/BSB-24 story, delivers the way to set it?
2. *(Finding 3)* For a seeded run, is BSB-33's FR-140 Jira-change record built from
   `run_jira.state_after`, or captured independently? If independently, must BSB-28's cleanup wait
   for it? And is evaluating fixture assertions against `state_after` deliberately left to no epic?
3. *(Finding 7)* When a project's Jira `site_url` or `project_key` changes while a seeded run is not
   yet cleaned, should BSB-23 refuse the change, or should each seeded run record the site and
   project it seeded into?

## Proposed changes

Proposed for `sdlc-plan-stories-write` (revise mode); nothing has been applied.

- **Shared contract (`stories.md` preamble):**
  - "Fixture selection and enablement" and Open decisions 1/4: rewrite to the answer to Open
    question 1 (F1).
  - "Fixture file format", the fixture JSON block and Open decision 2: switch to `{{alias}}` (F8).
  - "Cleanup": replace "all-or-nothing" with continue-and-leave-`cleaned_at`-`NULL` (F5).
  - "Nightly sweep": `cleaned_at` is set only when no marked issue of that run remains. The sweep
    skips runs whose finalizer is in progress (F5, F6).
  - "Post-run state capture": the finalizer's trigger and recovery (F4); its position relative to
    BSB-33's capture (F3).
  - "Run state values": this epic owns the `failed_seed` run-page text (F9).
  - Cross-epic notes: BSB-23 (F1, F7), BSB-26 and BSB-38 (F9), BSB-27 (F4), BSB-33 (F3), BSB-34
    (F11), BSB-37 (F10).
- **BSB-28-PENDING-1:**
  - Givens and notes follow the fixture source; add the way to set it (F1).
  - Owns writing `run_jira.aliases`; remove "storing the alias mapping" from Out of scope (F2).
  - Re-check `running` before inserting `run_jira` and creating the container, and roll back if the
    terminal write was lost; add the BSB-27 dependency (F4).
  - Add the template-project + fixture → `failed_seed` scenario (F7).
  - `{{alias}}` tokens in the `POST` bodies (F8).
  - Owns the `failed_seed` outcome text, with a scenario (F9).
  - Retention note (F11).
- **BSB-28-PENDING-2:**
  - Scope narrowed to phase-2 replacement and alias validation; notes no longer claim the mapping
    write (F2).
  - `{{alias}}` tokens in scenarios and log lines (F8).
  - Note that it also produces `failed_seed` (F9).
  - Note on the fixture source (F1).
- **BSB-28-PENDING-3:**
  - Owns the finalizer hook. ACs keep only capture assertions; move the cleanup assertions to
    PENDING-4 (F2).
  - The trigger covers every terminal writer, plus startup recovery (F4).
  - Out of scope and notes corrected on fixture assertions and on BSB-33 ordering (F3).
  - Serialise with the sweep (F6).
  - Retention note (F11).
- **BSB-28-PENDING-4:**
  - Gains the moved "capture before cleanup" and "cleanup after a failed capture" scenarios; notes
    name PENDING-1 as the writer of `aliases` (F2).
  - Notes on the finalizer trigger (F4) and the BSB-33 ordering (F3).
  - Add a first-key-fails scenario (F5).
  - Do not treat a 404 as cleaned when the key's project prefix differs from the current
    `project_key` (F7).
- **BSB-28-PENDING-5:**
  - Same `cleaned_at` meaning as PENDING-4 (F5).
  - Skip runs whose finalizer is in progress, with a scenario (F6).
  - Skip integrations without a `project_key`; handle a changed integration per Open question 3
    (F7).
  - Own its daily 02:00 UTC trigger instead of an unnamed scheduler (F10).
  - Notes say it is the last-resort fallback when finalizer recovery fails (F4).

## Architecture impact

None for the stories as written. Every finding is closed by a story or contract change within
SK-001 §5 and §9:
- `integrations.config` and `runs.state` are free-form;
- the `run_jira` columns already exist;
- PRD §8 "Jira fixture marking" already settles SK-001 Open question 1 (one configured project,
  marked issues).

**Conditional:** a "per run, reused by re-runs" answer to Open question 1, or a "record the site and
project per seeded run" answer to Open question 3, needs a column that SK-001 §9 does not list. The
§9 `runs` row has no fixture field, `runs.context` is handed to the agent as `BB_CONTEXT`, and
`run_jira` has no site or project field. If the gate gives either answer, take it back to the design
stage before `sdlc-plan-stories-write` revises. No such change is needed today.

## Requirement coverage check

**Yes, with caveats.** All five FR IDs that `epic-map.json` assigns to BSB-28 are exercised by at
least one story's acceptance criteria:
- FR-058: PENDING-1.
- FR-059: PENDING-2.
- FR-060: PENDING-3.
- FR-061: PENDING-4. The "only issues marked with that run's ID" clause is pinned by its
  unmarked-issue and lost-marker scenarios.
- FR-062: PENDING-5.

No FR is claimed by two stories, and BSB-28 has no NFRs. The FR-058 to FR-062 wording in `PRD.md`
matches the `epics.md` traceability lines exactly, so there is no drift. The epic's three edge cases
and two non-goals are each carried by a named story.

Caveats:
- PENDING-1's ACs assert the alias mapping that its Out of scope gives to PENDING-2 (Finding 2).
- FR-060's purpose clause, "for fixture assertions", has no consumer in any epic (Finding 3).

## Dependency-note sanity check

**No.** Every story key and epic key the notes mention exists (PENDING-1 to PENDING-5, BSB-23 to
BSB-27, BSB-29, BSB-33, BSB-38). These mismatches remain:
- **PENDING-3 ↔ PENDING-4:** PENDING-4's notes say it depends on PENDING-3, but PENDING-3's ACs
  require PENDING-4's cleanup. The direction is inverted (Finding 2).
- **PENDING-1 ↔ PENDING-2:** each assigns the `aliases` write to the other. PENDING-4's notes omit
  whichever story writes it (Finding 2).
- **PENDING-1 → BSB-23:** depends on a `config.fixture` key that BSB-23 has no FR for and has no
  stories to reciprocate (Finding 1).
- **PENDING-1 / contract → BSB-26:** one-sided claim that BSB-26 will add `failed_seed` and its page
  text. BSB-26's stories enumerate sibling terminal states without it (Finding 9).
- **PENDING-1:** silent on BSB-27, whose deadline can end a run mid-seed (Finding 4).
- **PENDING-5 → "the installation's scheduler":** no epic delivers one before BSB-37 (Finding 10).

Build order itself is left to `sdlc-plan-epic-sequence`.

---
*Next: the gate reviewer answers Open questions 1–3. Then `sdlc-plan-stories-write` (revise mode)
applies the proposed changes to `docs/product/epics/BSB-28/_epic/stories.md`, then this review is
re-run. No Jira issue, story file or map was changed by this pass.*
