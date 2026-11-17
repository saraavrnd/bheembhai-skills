# Epic Review — BSB-46: Static security scanning

**Verdict:** ESCALATE · **Date:** 2026-11-17 · **Stories reviewed:** BSB-46-PENDING-1, BSB-46-PENDING-2, BSB-46-PENDING-3, BSB-46-PENDING-4, BSB-46-PENDING-5, BSB-46-PENDING-6, BSB-46-PENDING-7, BSB-46-PENDING-8

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-46/_epic/epic-review.md`.

## Context loaded

- **Requested work item.** `SkillBuilder-2` could not be retrieved. A direct read-only Atlassian
  REST fetch of `https://saraavrnd.atlassian.net/rest/api/3/issue/SkillBuilder-2` returns HTTP 404
  ("Issue does not exist or you do not have permission to see it"); the site's projects are BEEM,
  BSB, EX, GRAP and LNPRTL, with no `SkillBuilder` project. The Atlassian MCP server configured in
  `.mcp.json` is not exposed as a tool in this session, so the same read-only Jira REST API was
  used with the configured credentials. This matches `docs/product/PRD.md` §8 and the input note
  already recorded at `docs/product/epics/BSB-46/_epic/stories.md:308–317`. The placeholder
  contributes no scope.
- **Epic under review.** BSB-46, "Static security scanning" (Jira fetched read-only: type Epic,
  status To Do, labels FA-11 and MVP; its description, functional scope, edge cases, non-goals and
  covered requirements match `docs/product/epics.md:673–757`). It is the only written epic with no
  `_epic/epic-review.md`; its stories were written by the preceding `sdlc-plan-stories-write` step
  (commit `e7d2062`).
- **Stories.** All eight, from `docs/product/epics/BSB-46/_epic/stories.md` and
  `docs/product/epics/BSB-46/_epic/story-map.json`. The epic covers FR-076–FR-081, FR-087–FR-089,
  FR-091, FR-092, FR-154, FR-155 and NFR-005.
- **Requirement and scope sources.** `docs/product/PRD.md` §2 (target users), §4, §5 (FA-11), §6
  (the 14 mapped requirements), §7 (NFR-005 and the inherited NFR-002/NFR-003/NFR-004), §8
  ("External prerequisites", "Secrets", "Test data", "Access model", the retention and
  run-preparation assumption notes); `docs/product/epic-map.json` (BSB-46 and every sibling
  entry); `docs/product/epics.md:673–757` (BSB-46) and the sibling entries at `:760–830` (BSB-47),
  `:912–965` (BSB-49), `:1073–1135` (BSB-51), `:1141–1200` (BSB-52), `:1210–1290` (BSB-53),
  `:1294–1370` (BSB-54), `:1374–1430` (BSB-55).
- **Design input.** No `architecture.md`, `data-model.md`, `api-contracts/` or `ui-conventions.md`
  exists in this repository (there is no project-level `AGENTS.md`/`CLAUDE.md` either). The
  committed design reference is `docs/adr/SK-001-skill-builder.md`: §2/§2a (the kit, scanner image
  digest, step kit), §5 (a run's two branches and bundle), §6b (the security scan contract) and §9
  (the data model). `docs/adr/SK-002-single-responsibility-skills.md` was skimmed for the reviewer
  role boundary; it adds nothing to this epic.
- **Sibling stories used for cross-epic comparison.** BSB-39 (`users`, `builder_session`, the
  `skill-builders` gate, fixture accounts), BSB-41 (catalog fixture `main`, build branches,
  read-from-checkout wording), BSB-43 (`projects`, `project_members`, owner/member, fixture
  accounts), BSB-45 (the catalog fixture branch table, `POST /api/projects/{id}/runs`, the bundle,
  NFR-001, and the fixture branch options). BSB-44 is the integration/secret owner. BSB-40 and
  BSB-47–BSB-58 have no stories yet; their epic entries were used as the contract.
- **Not loaded.** No `epic-sequence.md`/`.json` exists anywhere under `docs/product/epics/`, so
  relative epic build order could not be checked. No Jira issue links or sub-tasks exist for
  BSB-46. The previous BSB-45 review (`docs/product/epics/BSB-45/_epic/epic-review.md`) was used
  for its already-recorded architecture finding (`runs.baseline_sha`).

## Findings

### Finding 1 — Cross-epic architecture fit: the scan record model is absent from SK-001 §9
- **Severity:** Blocking
- **Stories touched:** BSB-46-PENDING-1, -2, -3, -4, -5, -6, -7, -8 (every story asserts or reads
  the record); cross-epic BSB-47 (LLM stage), BSB-49 (FR-055 gate), BSB-51 (Ready evaluation),
  BSB-54 (report links), BSB-55 (CLI scan).
- **Evidence:**
  - `docs/adr/SK-001-skill-builder.md:345–357` (§9 data model) lists `users`, `builds`, `projects`,
    `project_members`, `integrations`, `skill_bundles`, `runs`, `run_jira` and `suites`. There is
    no scan table, no scan-report storage and no scan column on `runs`.
  - `docs/adr/SK-001-skill-builder.md:284–317` (§6b) requires the builder to scan before every run,
    cache by content sha, write a report with score/recommendation/findings and show it in a
    Security tab — but says only "cached by content sha", with no entity, key or storage.
  - `docs/product/epics/BSB-46/_epic/stories.md:181–213` invents a 22-column `static_scans` table,
    a partial unique index on (`project_id`, `content_sha256`, `scanner_version`,
    `scanner_image_digest`) and a new `runs.static_scan_id` column. `:383` acknowledges the
    position: "`static_scan_id` is the one new `runs` column (SK-001 §9 lists none)".
  - Every AC asserts the invented shape: `:346` (P1's full `static_scans` row plus
    `runs.static_scan_id`), `:399–424` (P2's reuse and concurrency), `:449–464` (P3),
    `:489–504` (P4), `:530–560` (P5), `:585–597` (P6), `:622–652` (P7), `:677–692` (P8).
  - BSB-47's epic entry (`docs/product/epics.md:760–830`) needs the LLM stage's report and model
    field; BSB-49/BSB-51/BSB-54/BSB-55 consume the classifier or the report. Only BSB-46's stories
    name a storage shape, and they name a static-only one.
- **What is missing/ambiguous/contradictory:** The durable scan record is design the architecture
  has not made. The stories choose a table name, 22 columns, a uniqueness rule and a `runs`
  foreign key. BSB-47 will need the same record for the LLM stage, and the chosen
  `static_scans`/`GET /api/scans/{scan_id}` shape is stage-specific. Two implementations (FA-8's
  preflight and FA-11's own gate) can read different schemas, and BSB-47 can duplicate the entity.
  This is the same class of gap BSB-45 already recorded for `runs.baseline_sha`
  (`docs/product/epics/BSB-45/_epic/epic-review.md:166–195`, `:365–375`); BSB-46 adds a second
  unratified `runs` column and a whole new table on top of the same pending amendment.
- **Question (if a person must decide):** Should `sdlc-arch-design` (amend) add one scan record
  model — either a `static_scans` table plus `runs.static_scan_id`, or a shared `scans` table with
  a stage (`static`/`llm`) discriminator and the run link — and what are its key, nullability,
  report storage and uniqueness rule? (also listed under Open questions)
- **Proposed change:** `sdlc-arch-design` (amend) first; `sdlc-plan-stories-write` then updates the
  preface and every affected AC to the pinned table/column names. No behavior change is expected
  beyond the schema and the report-route split with BSB-47. This finding is under **Architecture
  impact**, not a story-wording fix.

### Finding 2 — Cross-epic NFR conflict: the scan sits inside run preparation, which BSB-45 bounds at 60 seconds
- **Severity:** Blocking
- **Stories touched:** BSB-46-PENDING-1 and BSB-46-PENDING-4; cross-epic BSB-45-PENDING-6 and the
  PRD's NFR-001.
- **Evidence:**
  - `docs/product/PRD.md:254` (NFR-001): "Non-model run preparation completes within 60 seconds for
    a skill bundle of up to 5 MB."
  - `docs/product/epics/BSB-45/_epic/stories.md:553–556` (P6's NFR-001 AC): the run-start request
    must respond HTTP 201 with `state` `prepared` "no more than 60 seconds after receiving the
    request"; `:562` maps NFR-001 to that story. `:568` says NFR-001 is measured "on the
    synchronous start request with a cold bundle cache and no model call".
  - `docs/product/epics/BSB-46/_epic/stories.md:230–244`: the run-start order is FA-1 gate → project
    and membership → BSB-45 request validation → packaging and bundle resolution → **static scan**
    → branch creation → run insert. P1's 201 responses (`:346`) are returned only after the scan
    completes.
  - `docs/product/epics/BSB-46/_epic/stories.md:491–494` (P4): a run-triggered scan whose scanner
    finishes at fixture-clock 599,999 ms still responds HTTP 201 with the run created; `:293–298`
    sets the scanner deadline at 600,000 ms. A timed-out or crashed run-triggered scan is a 503.
  - BSB-45 places scans outside its scope and says FA-11/FA-12 own them
    (`docs/product/epics/BSB-45/_epic/stories.md:236`, `:313`) — it never says the start path
    now waits for one.
- **What is missing/ambiguous/contradictory:** NFR-001 and BSB-45's P6 can be read as binding the
  whole synchronous `POST /runs` path, which now includes a static scan with a 10-minute ceiling.
  The two stories cannot both be satisfied for the P4 slow-pass case. Nothing states whether scan
  time is inside the 60-second budget, and no story states an interaction between BSB-45's run
  deadline prep bound and the scanner's 600,000 ms deadline from SK-001 §6b.
- **Question (if a person must decide):** Is the static scan part of NFR-001's "run preparation" —
  in which case the run-triggered scan must fit the 60-second budget and P4's 599,999 ms
  run-start AC is wrong — or is scan time excluded, in which case NFR-001 (and BSB-45-PENDING-6)
  must say "run preparation excluding the security scan" and the run-start request may take up to
  the scan deadline? (also listed under Open questions)
- **Proposed change:** Choose one reading. If the scan counts: add a run-path scan deadline that
  fits the remaining 60-second budget, remove or re-point P4's slow-pass-at-599,999 ms
  run-triggered AC, and state the bound in P1 and the preface. If it does not count: amend
  NFR-001's wording and `docs/product/epics/BSB-45/_epic/stories.md:553–556`, `:568` to exclude
  the scan and record the start path's worst case (up to 600 seconds) in the BSB-46 preface.

### Finding 3 — Cross-epic fixture ownership: BSB-46 adds eleven branches to BSB-45's fixture repository and invalidates BSB-45's exact branch list
- **Severity:** Blocking
- **Stories touched:** the BSB-46 preface and BSB-46-PENDING-1, -2, -3, -4, -5, -6, -7, -8
  (every story that names a static fixture branch); cross-epic BSB-45-PENDING-1 and BSB-41.
- **Evidence:**
  - `docs/product/epics/BSB-46/_epic/stories.md:61–91`: "The repository is BSB-41's and BSB-45's
    fixture." Its branch table (`:68–84`) adds `test/saraav/static-clean`, `static-dni`,
    `static-critical`, `static-partial`, `static-accepted`, `static-accepted-pass`,
    `static-accepted-partial`, `static-mixed`, `static-timeout`, `static-crash` and
    `static-slow-pass` — eleven branches that BSB-45's fixture does not define.
  - `docs/product/epics/BSB-45/_epic/stories.md:69–81` defines the same repository with exactly
    four branches used by its epic (`main`, `build/sdlc-research-summarise`,
    `test/saraav/research`, `test/saraav/large`) and does not mention the static branches.
  - `docs/product/epics/BSB-45/_epic/stories.md:275` asserts the run form's `skills-branch`
    select has options "exactly `build/sdlc-research-summarise`, `main`, `test/saraav/large` and
    `test/saraav/research`"; `:316` says those options are read from `bheembhai-skills`. Every
    BSB-46 static branch contains `skills/sdlc-research-summarise/`, so it would appear in that
    select.
  - BSB-46's P7 page assertion is deliberately non-exact ("include `main` and
    `test/saraav/static-clean`", `:627`), so the page test tolerates extra branches; BSB-45's test
    does not.
- **What is missing/ambiguous/contradictory:** The fixture repository is a single shared artifact,
  but no epic owns its full branch set. If the static branches live in the same fixture snapshot,
  BSB-45-PENDING-1's exact-options AC fails; if BSB-46 uses a separate snapshot, the statement
  that it is "BSB-41's and BSB-45's fixture" is false and the shared-fixture test seam is
  undefined. This is a cross-epic test-contract conflict, not a wording nit.
- **Question (if a person must decide):** Are the eleven static branches added to the shared
  `bheembhai-skills` fixture owned by BSB-41/BSB-45 (which then updates its fixture table and the
  exact `skills-branch` options in BSB-45-PENDING-1), or does BSB-46 define a distinct fixture
  snapshot with its own branch list? (also listed under Open questions)
- **Proposed change:** Pick one and record it. If shared: BSB-46's preface names BSB-45/BSB-41 as
  the fixture owner that delivers the static branches, and BSB-45-PENDING-1's exact options list
  and fixture table are updated. If separate: BSB-46 states its own snapshot identity and the
  BSB-45 AC stays untouched. Do not leave both exact assertions in force against one repository.

### Finding 4 — Cross-epic access: the member-only scan report is the report FR-111 asks a catalog reviewer to read
- **Severity:** Advisory
- **Stories touched:** BSB-46-PENDING-5 and BSB-46-PENDING-7; cross-epic BSB-54.
- **Evidence:**
  - `docs/product/epics/BSB-46/_epic/stories.md:273–291` (report contract) and `:547–550` (P5's
    non-member AC) make `GET /api/scans/{scan_id}` and `GET /scans/{scan_id}` return HTTP 403 to
    anyone who is not a member of the scan's `project_id`; `:634–637` repeats the rule for the
    skill page.
  - `docs/product/PRD.md:19` defines the Catalog reviewer as consuming "the catalog pull request
    and its linked run and scan reports; does not use the authoring interface".
  - `docs/product/PRD.md:188` (FR-111) requires the pull-request description to link the scan
    reports; BSB-54's epic entry repeats it (`docs/product/epics.md:1304`, `:1316`, `:1343`,
    `:1359`).
- **What is missing/ambiguous/contradictory:** A catalog reviewer who is not a member of the test
  project cannot open the report link BSB-54 is required to put in the PR description. The stories
  never state whether the reviewer has a builder login, is added to the project, or is expected to
  see a published/signed report; BSB-46's AC explicitly forbids every non-member.
- **Question (if a person must decide):** How does a catalog reviewer consume the scan report
  linked from the catalog PR — a read-only published/signed report URL, a builder account with
  read access, or a copy of the evidence in the PR itself? (also listed under Open questions)
- **Proposed change:** Decide the access path. If the member-only rule stands, BSB-46-PENDING-5/7
  keep it and BSB-54 must link something a reviewer can open (record that in both); if reviewers
  must read the report, add the read-only access rule/route to P5 (and P7) and coordinate the link
  with BSB-54.

### Finding 5 — Epic-wide scope boundary: two edge cases listed by the epic have no owning AC
- **Severity:** Advisory
- **Stories touched:** the BSB-46 preface/error table, BSB-46-PENDING-1, BSB-46-PENDING-2 and
  BSB-46-PENDING-7.
- **Evidence:**
  - `docs/product/epics.md:706–708` lists the epic's edge cases, including "scanner image
    unavailable" and "a scan started from the skill page while an identical run-triggered scan is
    in flight".
  - BSB-46's error table (`docs/product/epics/BSB-46/_epic/stories.md:239–244`) has
    `static_scan_blocked` (422), `static_scan_failed` for timeout/scanner_error (503),
    `scanner_image_not_pinned` for a tagged image (503) and `bundle_store_unavailable` (503), but
    no row for a pinned image that cannot be pulled or a scanner image that is otherwise
    unavailable. No story AC creates a `static_scans` row for that condition, so it is unclear
    whether it is `scanner_error`, a new error, or a no-row failure.
  - P2's concurrency AC (`:421–424`) exercises two *run* triggers for the same content; the
    cross-entry-point case (skill-page trigger joining a running run-triggered scan) has a
    contract rule (`:207–211`, `:256–260`) but no AC.
- **What is missing/ambiguous/contradictory:** One epic-listed edge case has no contract at all and
  the other has a rule but no exercise. A developer implementing the preface can choose different
  statuses/rows for image-pull failure, and the cross-entry-point join can regress without a test.
- **Question (if a person must decide):** When the pinned scanner image cannot be pulled or is
  unavailable, is the result HTTP 503 `{"error":"static_scan_failed","reason":"scanner_error"}`
  with a `failed` `static_scans` row, a new `scanner_unavailable` error, or no row at all? (also
  listed under Open questions)
- **Proposed change:** Add the chosen image-unavailable row to the preface error table and a P1
  (run path) plus P7 (skill-page path) AC; add one P2 or P7 AC where a run-triggered scan is
  running and the skill-page trigger joins it (`reused` true, one `BB_SCAN_LOG` line, one row).

### Finding 6 — Epic boundary: no epic owns retention or eviction of scan rows and reports
- **Severity:** Advisory
- **Stories touched:** BSB-46-PENDING-2; cross-epic BSB-52.
- **Evidence:**
  - `docs/product/epics/BSB-46/_epic/stories.md:430` puts "cross-project reuse and eviction of old
    scan rows" out of scope for P2, without naming an owning epic or story.
  - `docs/product/epics.md:1141–1200` (BSB-52) scopes retention/purge to "run transcripts, logs
    and results" (NFR-013/NFR-014), depends on FA-5/FA-6/FA-7, and never names scans or FA-11.
  - `docs/product/PRD.md:266–267` (NFR-013/NFR-014) uses the same "run transcripts, logs and
    results" wording. BSB-46 stores `static_scans.report` (the full scanner JSON, `:204`) and
    retains completed scan rows for reuse, but defines no eviction; no story states who deletes
    them or whether they are purged with a run.
- **What is missing/ambiguous/contradictory:** The epic creates durable scan data and explicitly
  defers its eviction, but no epic in the plan claims scan retention/purge. Either BSB-52's scope
  silently excludes it (a hole nobody owns) or BSB-52 must extend to it; the current mapping says
  neither.
- **Question (if a person must decide):** Does BSB-52's retention/purge apply to `static_scans`
  rows and their stored `report` (adding FA-11 as a dependency and scan data to its scope), or is
  scan-record retention out of the MVP and stated as such? (also listed under Open questions)
- **Proposed change:** Name the owner in P2's Out of scope and, if it is BSB-52, record the
  dependency on both sides (BSB-52's epic scope and BSB-46 P2's Notes). If out of MVP, say so
  explicitly instead of leaving "eviction" unassigned.

### Finding 7 — Cross-story dependency notes are one-sided or incomplete
- **Severity:** Advisory
- **Stories touched:** BSB-46-PENDING-4, -5, -6, -7, -8.
- **Evidence:**
  - P4's AC at `:501–504` starts a **skill-page** scan (P7's entry point), but P4's Notes at
    `:513–514` name only P1 and P2, and P7's Out of scope at `:657–658` never mentions P4.
  - P5's AC at `:542–545` uses a **failed** scan, which is P4's state machine (`:489–504`), but P5's
    Notes at `:570–571` name only P1 and P2, and P4's Out of scope at `:510–511` never mentions
    P5's report.
  - P6's Notes at `:605–606` depend on P5 for the report fields, but P5's Out of scope at
    `:567–568` never mentions P6, so one side of the dependency is silent.
  - P8's Notes at `:700–701` depend on P7 for the second entry point, but P7's Out of scope at
    `:657–658` never mentions P8.
- **What is missing/ambiguous/contradictory:** Nothing contradictory; four dependency notes are
  incomplete on the implementing side. A developer reading only P4/P5/P7 can build without
  noticing the other story's behavior and test seam.
- **Question (if a person must decide):** None.
- **Proposed change:** Add the reciprocal dependency sentences: P4 → P7 (skill-page scan used by
  the timeout AC), P5 → P4 (failed-scan state used by the report AC), P5's Out of scope → P6
  (platform-parity consumer), P7's Out of scope → P8 (network-isolation consumer).

### Finding 8 — Cross-story actor consistency: PENDING-8 uses a PRD role that is external to the product
- **Severity:** Advisory
- **Stories touched:** BSB-46-PENDING-8, against BSB-46-PENDING-1 through -7.
- **Evidence:**
  - `docs/product/epics/BSB-46/_epic/stories.md:671`: "As a **platform administrator**, I want
    **every static scan to run in a container with no network access**…".
  - P1–P7 use "skill author" (`:340`, `:393`, `:443`, `:483`, `:524`, `:581`, `:616`) or
    "test-project member"; the P8 ACs are all exercised as Alice, a skill author/project owner
    (`:675–692`).
  - `docs/product/PRD.md:20` defines Platform administrator as "External to this product; manages
    group membership and the catalog import". The PRD does not define an in-product
    administrator role the scan operator could be.
- **What is missing/ambiguous/contradictory:** The epic's actor set is inconsistent: one story
  attributes a system security property to a role the PRD says never uses the product. The ACs
  are unchanged (Alice runs the scan), so this is a persona/wording defect, not a behavior gap.
- **Question (if a person must decide):** None.
- **Proposed change:** Change P8's story actor to "skill author" (or "the builder operator") and
  keep the ACs; if the platform administrator is intended, add one sentence explaining why an
  external role owns this property. No acceptance-criteria change.

## Open questions

1. **Scan record model (Finding 1).** `sdlc-arch-design` must pin the scan entity, its key,
   nullability, report storage and uniqueness rule, and the run link (`static_scans` +
   `runs.static_scan_id` vs a shared `scans` table with a stage column). BSB-47, BSB-49, BSB-51,
   BSB-54 and BSB-55 all consume it.
2. **NFR-001 boundary (Finding 2).** Does the 60-second non-model run-preparation budget include
   the static scan? If yes, the run path needs a scan deadline inside that budget and P4's
   599,999 ms run-start AC changes. If no, NFR-001 and BSB-45-PENDING-6 must say "excluding the
   security scan" and the start path's worst case is the 600-second scanner deadline.
3. **Fixture ownership (Finding 3).** Are the eleven `test/saraav/static-*` branches part of the
   shared `bheembhai-skills` fixture owned by BSB-41/BSB-45 (whose exact branch-option AC then
   changes), or a separate BSB-46 fixture snapshot?
4. **Catalog-reviewer access (Finding 4).** How does the catalog reviewer open the scan report
   linked from the catalog PR, given P5/P7's non-member 403 — a published/signed report, a
   read-only builder account, or evidence copied into the PR?
5. **Unavailable scanner image (Finding 5).** What status/error and what `static_scans` row does a
   pinned scanner image that cannot be pulled produce?
6. **Scan retention (Finding 6).** Does BSB-52's retention/purge cover `static_scans` rows and
   their stored `report`, or is scan-record retention out of MVP?

## Proposed changes

### BSB-46 preface / shared contract (`stories.md:1–332`)
- Mark the `static_scans` table and `runs.static_scan_id` as pending the `sdlc-arch-design`
  amendment, not as story-invented design; record the chosen scan model once it exists
  (Finding 1).
- Record the NFR-001 position: whether scan time is inside run preparation, and the run-path scan
  deadline (Finding 2).
- Name the fixture owner for the eleven static branches and whether they live in BSB-45's shared
  fixture or a separate snapshot (Finding 3).
- Add the unavailable-scanner-image error/row rule to the error table, and the retention owner for
  scan rows (Findings 5, 6).

### BSB-46-PENDING-1 — Block a run whose static scan does not pass
- Apply the NFR-001 decision (run-path scan deadline or a preface note that the scan is excluded
  from the 60-second budget) (Finding 2).
- Add the unavailable-scanner-image AC and error row (Finding 5).
- No change to the pass classifier or the existing run-gate scenarios.

### BSB-46-PENDING-2 — Reuse a completed static scan for unchanged content
- State the owner of scan-row eviction/retention in Out of scope (Finding 6).
- Add the cross-entry-point join AC (skill page joining a running run-triggered scan) here or in
  P7 (Finding 5).
- No change to the reuse key or the failed-scan-not-reused rule.

### BSB-46-PENDING-3 — Keep an accepted finding from clearing a static-scan block
- No change.

### BSB-46-PENDING-4 — Time out a static scan after ten minutes and record it as failed
- Reconcile the 599,999 ms run-triggered AC with the NFR-001 decision (Finding 2).
- Add the P7 dependency sentence for the skill-page timeout scenario (Finding 7).

### BSB-46-PENDING-5 — Show the scan score, recommendation and findings in the report
- Add the P4 dependency sentence for the failed-scan report AC (Finding 7).
- Record the catalog-reviewer access decision (Finding 4).
- Add P6 to Out of scope / Notes as a consumer of the report fields (Finding 7).

### BSB-46-PENDING-6 — Match the platform's verdict for the same content and scanner version
- No change beyond the scan-model names from the architecture amendment (Finding 1).

### BSB-46-PENDING-7 — Start a static-only scan from the skill page without a run
- Add the unavailable-scanner-image AC for the skill-page path (Finding 5).
- Add the cross-entry-point concurrency AC if not placed in P2 (Finding 5).
- Add P8 to Out of scope as the consumer of the second entry point (Finding 7).
- Record the reviewer-access rule if the decision changes the page's membership rule
  (Finding 4).

### BSB-46-PENDING-8 — Run the static scan with no network access
- Change the story actor to "skill author" or "the builder operator" (Finding 8).

### Mapping files
- `story-map.json`: no requirement assignment changes; the gaps are cross-cutting, not missing
  requirements.
- `docs/product/epic-map.json`: no change unless the architecture amend changes the scan model,
  which does not alter requirement IDs.

### Cross-epic changes needed (outside this epic's revise pass)
- **BSB-45-PENDING-1 / -6**: fixture table and exact `skills-branch` options (Finding 3);
  NFR-001 wording/AC and the "excluding the security scan" position (Finding 2).
- **BSB-52**: retention/purge scope and FA-11 dependency if it owns scan rows (Finding 6).
- **BSB-54**: scan-report link access for the catalog reviewer (Finding 4).
- **BSB-47**: use the same scan record model and disambiguate the `GET /api/scans/{scan_id}` stage
  (Finding 1).
- **`sdlc-arch-design` (amend)**: the scan record model and `runs` linkage (Finding 1).

## Architecture impact

**Needs `sdlc-arch-design` (amend): one item, plus a note.**

1. **The scan record model (Finding 1).** SK-001 §6b requires a cached, report-bearing scan
   before every run (`docs/adr/SK-001-skill-builder.md:284–317`), but §9's data model
   (`:345–357`) has no scan table and no scan column on `runs`. BSB-46 invents `static_scans` (22
   columns, a partial unique index) and `runs.static_scan_id` (`docs/product/epics/BSB-46/_epic/
   stories.md:181–213`; acknowledged at `:383`). BSB-47 will need the LLM stage's record, and
   BSB-49/BSB-51/BSB-54/BSB-55 consume the result. The data model must define the entity, keys,
   nullability, report storage and run link (or state the shared-`scans` alternative). Until then
   every BSB-46 AC asserts an unratified schema. This is the reason the verdict is ESCALATE.
   It should be settled in the same amendment as BSB-45's `runs.baseline_sha`
   (`docs/product/epics/BSB-45/_epic/epic-review.md:166–195`, `:365–375`), which is still open.

**Not architecture conflicts, but cross-epic contract changes owned elsewhere:**
- The NFR-001 boundary (Finding 2) is a requirement/AC conflict between PRD NFR-001 and BSB-45's
  P6 and BSB-46's start path; it is a wording/scope decision, not a new entity or endpoint.
- The fixture branch set (Finding 3) is a test-fixture ownership gap, not a data-model change.
- The catalog-reviewer access path (Finding 4) is an access-model decision that P5/P7 and BSB-54
  can record; it does not need a new architecture entity unless the decision introduces one.
- The unavailable-image and retention gaps (Findings 5, 6) are error/scope rules, not new design.

The other entities the stories use — `users`, `projects`, `project_members`, `skill_bundles`,
`runs` — all exist in SK-001 §9, and the fixture accounts/projects match BSB-39/BSB-43.

## Requirement coverage check

| Requirement | Story | Covered? | Note |
|-------------|-------|----------|------|
| FR-076 | P1 | Yes | Static scan on the exact bundle before every run; P1's clean/blocked ACs assert the scan row and the 201/422 outcomes. |
| FR-077 | P2 | Yes | Reuse keyed by (`project_id`, `content_sha256`, `scanner_version`, `scanner_image_digest`); completed failing scans reuse and still block. |
| FR-078 | P1 | Yes | `DO_NOT_INSTALL` → `verdict_do_not_install` and 422. |
| FR-079 | P1 | Yes | Critical finding → `critical_finding`, including a PASS verdict. |
| FR-080 | P1 | Yes | `files_scanned != files_total` → `incomplete_coverage`. |
| FR-081 | P3 | Yes | Accepted findings remain visible but never change `passes`/`reasons`. |
| FR-087 | P4 | Yes | 600,000 ms deadline, measured from `started_at`; slow-pass boundary AC. |
| FR-088 | P4 | Yes | Timeout and scanner error both `state` `failed` with `failure_reason`; report shows failure. |
| FR-089 | P5 | Yes | Score stored verbatim and rendered (`scan-score`). |
| FR-091 | P6 | Yes | Six-case platform-oracle comparison plus version/digest mismatch refusals. |
| FR-092 | P7 | Yes | Project-member skill-page trigger with no run, no branch and no model request. |
| FR-154 | P5 | Yes | Recommendation stored verbatim and rendered (`scan-recommendation`). |
| FR-155 | P5 | Yes | Findings carry severity, rule, file and line in both JSON and HTML. |
| NFR-005 | P8 | Yes | `network=none`, probe results recorded, both entry points, read-only bundle. |

- The requirement lists in `docs/product/PRD.md`, `docs/product/epic-map.json`,
  `docs/product/epics.md:673–757`, `story-map.json` and `stories.md` agree for all 14 mapped
  requirements; there is no wording drift and no duplicate assignment that redefines a concept.
- No requirement assigned to BSB-46 is unexercised, and no story claims a requirement outside the
  epic's map.
- **Cross-epic requirement note:** NFR-001 is BSB-45's mapped requirement, not BSB-46's, but
  BSB-46's run-start insertion changes the path BSB-45 measures. That is Finding 2, not a
  BSB-46 coverage failure. FR-111 (BSB-54) likewise consumes BSB-46's scan report; the access
  question is Finding 4.

## Dependency-note sanity check

- **Within the epic, all referenced story keys exist.** P2 → P1; P3 → P1; P4 → P1, P2; P5 → P1,
  P2; P6 → P1, P5; P7 → P1, P2; P8 → P1, P7. The declared edges are consistent with the Out of
  scope lists for P1/P2/P3, but four reciprocal notes are missing (Finding 7): P4's use of P7's
  skill-page entry point, P5's use of P4's failed state, P6's dependency on P5 and P8's dependency
  on P7 are not reflected on the providing story's side.
- **Cross-epic keys all exist.** BSB-39, BSB-43, BSB-45, BSB-47, BSB-49, BSB-51, BSB-52/53,
  BSB-54 and BSB-55 are real epic keys in `docs/product/epics.md` and `docs/product/epic-map.json`;
  no story key or epic key is dangling.
- **Cross-epic reciprocity is mostly present.** BSB-47's, BSB-49's, BSB-51's, BSB-54's and
  BSB-55's epic entries all name FA-11 as a dependency. BSB-52's entry does not, which is the
  retention gap in Finding 6. BSB-53 (the run page) does not name FA-11 and does not list the
  scan report in its scope.
- **No ordering is proposed.** No `epic-sequence.md`/`.json` exists, so this report makes no
  build-order or wave claim; that remains `sdlc-plan-epic-sequence`'s job.
