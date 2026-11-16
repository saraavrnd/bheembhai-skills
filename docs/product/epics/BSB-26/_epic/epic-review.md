# Epic Review — BSB-26: Run execution & outcome capture

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3, BSB-26-PENDING-4

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-26/_epic/epic-review.md`.

## Context loaded

- **Target work item.** The prompt names `SkillBuilder-2`. A read-only
  `GET /rest/api/3/issue/SkillBuilder-2` on the configured site
  (`https://saraavrnd.atlassian.net`) returned **HTTP 404** ("Issue does not exist or you do not
  have permission to see it."), matching `PRD.md` §8: `SkillBuilder` is not a project key on the
  site and the product work lives in project **BSB**. The Atlassian MCP tools were not exposed in
  this session, so the configured site was queried read-only through its REST API using the
  credentials already in `.mcp.json`/env. The epic under review is **BSB-26 — Run execution &
  outcome capture**, the epic whose story set the immediately preceding
  `sdlc-plan-stories-write` commit produced and which has no `epic-review.md` yet. It was fetched
  read-only: type Epic, status To Do, labels `FA-7`/`MVP`, no parent, no sub-tasks, no issue
  links. Its description has no separate acceptance-criteria field; its functional scope and
  Definition of Done (`epics.md:780-842`) are the acceptance material used here. No Jira write was
  made.
- **Epic story set.** `docs/product/epics/BSB-26/_epic/stories.md` (382 lines) — the full set, not
  a sample: BSB-26-PENDING-1 "Run a prepared skill in the platform's pinned runtime" (FR-044,
  FR-048, FR-151), PENDING-2 "Watch progress and logs while my skill runs" (FR-045, FR-046),
  PENDING-3 "Get a classified run outcome and output on my run branch" (FR-047), PENDING-4 "See
  the exact model profile and tier the run used" (FR-049, FR-152). `story-map.json` has the same
  four stories and the same eight requirement ids; `epic-map.json` agrees.
- **Product context.** `docs/product/PRD.md` §5 FA-7 (line 56), §6 FR-044…FR-049 (lines 118-123),
  FR-151/FR-152 (lines 225-226), §7 NFR-004 (255), NFR-012 (261), NFR-015…NFR-017 (265-267), §8
  source caveat and branch vocabulary (lines 273-281 and 343-345).
- **Design authority.** `docs/adr/SK-001-skill-builder.md` §2 (116-141), §2a (143-174, the step
  kit, context builder and env contract), §4 (190-211), §5 (213-255, run lifecycle), §6 (256-275,
  results), §9 (345-357, data model). No `docs/architecture.md`, `docs/data-model.md`,
  `docs/api-contracts/` or `docs/ui-conventions.md` is committed yet; as the sibling epic reviews
  record, ADR SK-001 is the design authority this pass can use.
- **Sibling stories read for cross-epic hand-offs.** BSB-24-PENDING-1/-2/-3/-4 (run start,
  context, model profile) and the BSB-24 review; BSB-25-PENDING-1/-2/-3 (bundle, run branch,
  source-control writer) and the BSB-25 review; BSB-22-PENDING-3 (run-start page and shared
  membership check); BSB-23-PENDING-1/-2/-3/-4/-5/-6 and the BSB-23 review Findings 6 and 7; the
  BSB-31 and BSB-32 reviews for their BSB-26 cross-epic notes.
- **Not present.** No `epic-sequence.md`/`.json` for BSB-26; BSB-27, BSB-29, BSB-33, BSB-34 and
  BSB-38 have epic definitions in `epics.md` but no stories yet. Sequencing is not computed here.
- **Upstream open item carried, not restated.** The BSB-25 review escalated the bundle
  content/format question. BSB-26-PENDING-1 treats the bundle as an opaque object addressed by
  `s3_key` and a presigned URL (`stories.md:116-119`), so no BSB-26 story fixes that format and
  this review does not re-open it.
- **Actor/role consistency checked.** All four stories use "a skill author who is a project
  member"; PENDING-2's fixtures use `project_members.role "owner"`. ADR §9 defines
  `project_members.role` as `(owner, member)`, and BSB-22's shared check treats a project member
  as any signed-in user with a `project_members` row. No undefined role or two-role
  contradiction; no finding.

## Findings

### Finding 1 — Cross-story / cross-epic: `BB_CONTEXT` is specified as the raw run context, not the step kit's rendered context
- **Severity:** Blocking
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-3. Cross-epic: BSB-24-PENDING-2, BSB-24-PENDING-3.
- **Evidence:**
  - PENDING-1 AC1: "its environment contains … `BB_CONTEXT` whose parsed JSON equals run 21's
    context" (`stories.md:64`). The fixture's `runs.context` has exactly four keys — `workflow`,
    `step`, `reviewer_feedback`, `upstream_handoff` (`stories.md:62`). Its Notes repeat the idea:
    "the `BashH_CONTEXT` built from the run's context" (`stories.md:109`).
  - ADR SK-001 §2a: the step kit's context builder renders `allowed_result_statuses`,
    `result_status_meanings`, `gate_follows`/`gate_role`, `reviewer_feedback` and
    `upstream_handoff` to `BB_CONTEXT` (`SK-001:152-154`).
  - BSB-24-PENDING-2's Notes state the same contract from the producer side: "BSB-26 and the step
    kit build BB_CONTEXT (`allowed_result_statuses`, `result_status_meanings`, `gate_follows`,
    `gate_role`, `reviewer_feedback`, `upstream_handoff`) from them at execution"
    (`BSB-24/_epic/stories.md:210-211`); BSB-24-PENDING-3 says "BSB-26 owns the BB_CONTEXT
    rendering" (`:277`).
  - BSB-24 allows a run with `runs.context` NULL (`BSB-24/_epic/stories.md:158-161`) and several
    default run-start ACs produce `context NULL` (`:38,61`), yet PENDING-1 has no NULL-context
    launch scenario and PENDING-3 accepts the four domain statuses "verbatim" without naming
    `allowed_result_statuses` (`stories.md:287-289`).
- **What is missing/ambiguous/contradictory:** PENDING-1's acceptance test requires a four-key copy
  of `runs.context`, while the design and BSB-24 require the agent to receive the six-field
  step-kit rendering. A developer following the AC would pass a context without
  `allowed_result_statuses`/`result_status_meanings`/`gate_*`; PENDING-3's classifier then has no
  allowed-status set and can accept a status the step does not allow, so the builder and the
  platform disagree. The NULL-context case is worse: it is the default run-start shape, and no
  story says what PENDING-1 sends or what PENDING-3 may accept.
- **Question (if a person must decide):** For a run with `context` non-null, is `BB_CONTEXT` the
  step kit's six-field rendering (not the raw `runs.context`); and for the `context` NULL case
  BSB-24 permits, what does `BB_CONTEXT` carry and which `allowed_result_statuses` govern
  PENDING-3's classification? (also Open question 1)
- **Proposed change:** Same change for BSB-26-PENDING-1 and BSB-26-PENDING-3, with the cross-epic
  contract confirmed by BSB-24-PENDING-2/-3: **PENDING-1** AC1 asserts `BB_CONTEXT` contains the
  run's `reviewer_feedback`/`upstream_handoff` and the step-kit-rendered
  `allowed_result_statuses`, `result_status_meanings`, `gate_follows`/`gate_role` derived from the
  workflow/step, plus a new scenario for a run whose `runs.context` is NULL; its Notes correct
  `BashH_CONTEXT` to `BB_CONTEXT` and say the step kit's `build_step_context` is called.
  **PENDING-3** Notes state that the document's `status` must be one of the run's
  `allowed_result_statuses`, and state the allowed set and outcome when `runs.context` is NULL.

### Finding 2 — Cross-story: `runs.result_status`/`execution_error` are assigned to each other in a cycle
- **Severity:** Blocking
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-3.
- **Evidence:**
  - PENDING-1 Notes: "`runs.result_status` and `runs.execution_error` are added by
    BSB-26-PENDING-3" (`stories.md:122-123`). Yet PENDING-1's own failure ACs already write
    `result_status "failed_infra"` and `execution_error` (`stories.md:74,79`).
  - PENDING-3 Notes: "Depends on BSB-26-PENDING-1 for a run in state 'running', for the adapter
    that reports the container exit, and for the `result_status` and `execution_error` columns"
    (`stories.md:273-274`). It then says "both columns are added by the data-model stage together
    with `runs.execution_error`" (`stories.md:293-294`).
- **What is missing/ambiguous/contradictory:** Each story says the other supplies the columns.
  PENDING-1 cannot satisfy its failure ACs without a column it assigns to PENDING-3; PENDING-3
  cannot start without a column it says PENDING-1 supplies. `sdlc-plan-epic-sequence` reading
  these notes would record a cycle, and whichever story is built first lacks the schema it
  asserts.
- **Proposed change:** Apply the same wiring statement to both: **PENDING-1 and PENDING-3** Notes
  say the data-model stage adds `runs.result_status`, `runs.claimed_verdict` and
  `runs.execution_error` once for this epic; PENDING-1 is the first consumer (pre-launch failures)
  and PENDING-3 consumes them for classification. PENDING-3's dependency list drops the columns
  from its PENDING-1 dependency and points at the data-model stage. No product decision; no open
  question.

### Finding 3 — Cross-epic: BSB-27's deadline/cap stop and PENDING-3's classifier can both write the terminal outcome
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-3. Cross-epic: BSB-27.
- **Evidence:**
  - PENDING-3 classifies every container exit: a non-zero exit is `failed_execution`
    (`stories.md:241-242`), and its Notes only say "`failed_timeout` is BSB-27's deadline outcome
    and is not produced here" (`stories.md:289`).
  - BSB-27's epic guidance says "Enforce caps from the execution telemetry path and stop the run
    with a recorded reason when a cap is reached" and adds "a watchdog that marks overdue runs
    failed and reaches a terminal state even if the runtime is unresponsive"
    (`epics.md:871-873`). NFR-008 says an over-deadline run is recorded as failed (`PRD.md:258`).
- **What is missing/ambiguous/contradictory:** A cap-stopped or deadline-killed container exits
  non-zero, which PENDING-3's rule turns into `failed_execution`; if BSB-27's watchdog has already
  recorded `failed_timeout` or a cap reason, PENDING-3 overwrites it, and if the watchdog fires
  while the worker still runs, the two epics race on the same terminal columns. Neither story says
  who owns the final write.
- **Question (if a person must decide):** When BSB-27 stops a run for a cap or the deadline, does
  BSB-27's recorded terminal reason win over PENDING-3's exit classification, and must the
  classifier skip any run BSB-27 has already terminated? (also Open question 2)
- **Proposed change:** **PENDING-3** Notes state the classifier runs only while no BSB-27 terminal
  reason is recorded, that BSB-27's `failed_timeout`/cap reason is authoritative, and add a
  scenario where a run already marked `failed` with `failed_timeout` is not overwritten.
  Cross-epic follow-up: BSB-27's decomposition must record the same precedence.

### Finding 4 — Cross-epic: the test-purpose admission is assumed silently at launch
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-4. Cross-epic: BSB-24-PENDING-1, BSB-23-PENDING-6, NFR-006.
- **Evidence:**
  - PENDING-1 AC1 injects the secret values of integrations 3 (github), 5 (ai_model) and 6 (jira)
    into the container (`stories.md:62-64`); every fixture carries `test_only: true`, but no
    BSB-26 AC asserts that a non-test-purpose integration is refused. Its Notes depend on
    BSB-23-PENDING-2/-3/-5 for the integrations and their secret references
    (`stories.md:99-102`), never on the test-purpose rule.
  - PENDING-4 injects the AI-model vendor key at launch (`stories.md:356-359`), likewise without
    naming the admission rule.
  - NFR-006 says "Runs use only test-purpose Jira, source-control and model credentials"
    (`PRD.md:256`); BSB-23-PENDING-6 owns the run-purpose rule; the BSB-24 review's Finding 3
    (Blocking) requires BSB-24-PENDING-1 to check `config.test_only` at run start
    (`BSB-24/_epic/epic-review.md:137-177`). The BSB-25 review's Finding 7 raised the same missing
    note for preparation.
- **What is missing/ambiguous/contradictory:** Execution is the last gate before a credential is
  read from Secrets Manager and injected. If BSB-24's Finding 3 is not applied, BSB-26 reads and
  injects a production credential while its Notes stay silent about the dependency, so the
  assumption has no owner in this epic.
- **Question (if a person must decide):** Is the test-purpose admission guaranteed at run start by
  BSB-24-PENDING-1/BSB-23-PENDING-6, or must the execution launch re-check each integration's
  `config.test_only` before reading its secret? (also Open question 3)
- **Proposed change:** **PENDING-1 and PENDING-4** Notes add: "Depends on BSB-24-PENDING-1 and
  BSB-23-PENDING-6 admitting only a test-purpose integration; execution does not re-check
  `config.test_only`." If the answer is that execution must check, add a refusal scenario to
  PENDING-1 before any secret is read. Cross-epic follow-up: BSB-24's Finding 3 must be applied.

### Finding 5 — Cross-epic: `integrations.mcp` → `BB_MCP_CONFIG` has no owner, and PENDING-1 does not pass it
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-1. Cross-epic: BSB-23-PENDING-1, BSB-23-PENDING-2, BSB-24, BSB-25.
- **Evidence:**
  - ADR SK-001 §2a lists `BB_MCP_CONFIG` "from the selected MCP servers" in the env contract
    (`SK-001:157`). PRD FR-128/FR-129 require the MCP definition "that the Jira [source-control]
    integration exposes to a run" (`PRD.md:202-203`).
  - BSB-23-PENDING-1/-2 store the submitted definition in `integrations.mcp`
    (`BSB-23/_epic/stories.md:33,120`); the BSB-23 review's Finding 7 records that no run epic
    owns delivering it and asks which of BSB-24/25/26 builds `BB_MCP_CONFIG`
    (`BSB-23/_epic/epic-review.md:342-374`).
  - PENDING-1's launch environment enumerates `BB_SKILL_URL`, `BB_SKILL_SHA256`, `RUN_BRANCH`,
    `BB_CONTEXT` and the injected secrets (`stories.md:64`); `BB_MCP_CONFIG` is absent, and its
    integration fixtures carry no `mcp` value (`stories.md:62`).
- **What is missing/ambiguous/contradictory:** BSB-23 promises the definition is available to a
  run; BSB-26 builds the container environment and is the natural delivery point, but neither the
  story nor the epic notes mention it. A BSB-26 implementer reading only this epic would never
  build the path, leaving FR-128/FR-129 half delivered.
- **Question (if a person must decide):** Which run epic builds `BB_MCP_CONFIG` from
  `integrations.mcp` — BSB-26-PENDING-1 when it builds the launch environment, or BSB-24 when it
  selects integrations? (Carries BSB-23's open question 7; also Open question 4)
- **Proposed change:** If BSB-26 owns it, **PENDING-1** Notes say it reads the project's
  Jira/source-control `integrations.mcp` values and passes them as `BB_MCP_CONFIG` in the launch
  environment, adds an AC for a run whose Jira integration has an MCP definition, and adds the
  dependency on BSB-23-PENDING-1/-2. If BSB-24 selects the servers, PENDING-1 names BSB-24 and
  the run record field the selection uses. Cross-epic follow-up: BSB-23-PENDING-1/-2 and the
  chosen run epic must name the same owner.

### Finding 6 — Cross-story: the run detail page's route/shell and membership check are unowned
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-2, BSB-26-PENDING-3, BSB-26-PENDING-4. Cross-epic: BSB-22-PENDING-3, BSB-33.
- **Evidence:**
  - PENDING-2's Notes say "This story owns only the live progress and log view"
    (`stories.md:195-197`), yet its ACs render the page heading and "Status: running" for
    `GET /projects/7/runs/21` (`stories.md:145-147`).
  - PENDING-3's ACs assert `GET "/projects/7/runs/21"` renders "Outcome: …"
    (`stories.md:232,237,242,247`); PENDING-4's assert the same page renders the model fields
    (`stories.md:330-336`).
  - PENDING-3's Notes name PENDING-1, BSB-25-PENDING-3 and BSB-24-PENDING-1 but never PENDING-2 or
    BSB-22 for the page (`stories.md:272-276`); PENDING-4 names BSB-22 only "for the run page's
    membership check" (`stories.md:351-353`).
  - BSB-22-PENDING-3 owns only `GET /projects/7/runs/new` (`BSB-22/_epic/stories.md:151-213`), and
    PENDING-2 says BSB-33 "adds the report sections to this same page"
    (`stories.md:196-197`). No story says who creates `GET /projects/{projectId}/runs/{runId}` or
    applies the membership check to it.
- **What is missing/ambiguous/contradictory:** Three stories assert sections on a route no story
  owns. PENDING-3 and PENDING-4 could each build their own page, or both assume a shell that is
  never built; the membership/404 behavior PENDING-2 tests may not apply to PENDING-3's and
  PENDING-4's assertions.
- **Question (if a person must decide):** Which story creates the run detail page route and shell
  (`GET /projects/{projectId}/runs/{runId}`) and applies BSB-22's membership check before any
  progress/log read — BSB-26-PENDING-2, or BSB-22/BSB-33? (also Open question 5)
- **Proposed change:** **PENDING-2** Notes state it owns the route, the page shell and the BSB-22
  membership check that runs before any artifact read, and that PENDING-3/-4 add sections to it.
  **PENDING-3 and PENDING-4** Notes add the dependency on PENDING-2 for the page (and PENDING-3 on
  BSB-22 for the membership check). If BSB-33/BSB-22 owns the shell instead, all three stories
  name that story and PENDING-2 does not claim the route.

### Finding 7 — Cross-epic traceability: FR-065's claimed-verdict recording is implemented in PENDING-3 but assigned to BSB-29
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-3. Cross-epic: BSB-29, `epic-map.json`.
- **Evidence:**
  - `epic-map.json` assigns FR-065 "The builder records the verdict the agent claimed" to
    **BSB-29** (`epic-map.json:94`; `PRD.md:140`).
  - BSB-26's own Definition of Done says to "persist both the status and the agent's claimed
    verdict for verification to compare" (`epics.md:814-815`), and PENDING-3's ACs record
    `runs.claimed_verdict` in the success, BLOCK, non-zero-exit and missing-document scenarios
    (`stories.md:232,237,242,247`).
  - PENDING-3's traceability claims only FR-047 (`stories.md:256-257`), and its Notes say
    "whether the claimed verdict survives verification is BSB-29's job" but never that BSB-29
    inherits an already-recorded claim (`stories.md:290-291`).
- **What is missing/ambiguous/contradictory:** The same behavior is promised by two epics on
  opposite sides of the map: BSB-26 builds the recording, BSB-29 is credited with it. When BSB-29
  is decomposed, its stories can re-record the claim or add a second writer, and the traceability
  view says BSB-26 did not deliver it.
- **Question (if a person must decide):** Does BSB-26-PENDING-3 own recording `runs.claimed_verdict`
  (FR-065), with BSB-29 only reading it and deciding whether verification overturned it — and
  should `epic-map.json`'s FR-065 attribution move to BSB-26? (also Open question 6)
- **Proposed change:** **PENDING-3** Notes state that recording the claimed verdict is the FR-065
  behavior, that `runs.claimed_verdict` is written here, and that BSB-29 consumes it and must not
  re-record it. Cross-epic follow-up: when BSB-29 is decomposed, treat FR-065's recording as
  supplied by BSB-26; reconcile the `epic-map.json` attribution (not edited by this review).

### Finding 8 — Cross-epic: the BSB-23 redaction helper is never named by BSB-26's result/log path
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3. Cross-epic: BSB-23-PENDING-5.
- **Evidence:**
  - BSB-23-PENDING-5 owns "the single redaction rule every builder surface applies" and says its
    redaction "covers the database, the application log, the run result document and the
    interface"; it states "The run result writer and the run report are built by BSB-26 and
    BSB-33" (`BSB-23/_epic/stories.md:408-415`). The BSB-23 review's Finding 6 records the
    cross-epic note: "BSB-26's and BSB-33's stories must name the BSB-23 redaction helper and pass
    it the resolved values" (`BSB-23/_epic/epic-review.md:305-341`).
  - No BSB-26 story names BSB-23-PENDING-5 or the helper. PENDING-1 AC1 asserts only that the
    builder database and the builder's own log lack the values (`stories.md:64`); PENDING-2's
    redaction AC asserts the rendered page contains `[REDACTED]` (`stories.md:174-179`); PENDING-3
    reads `runs/21/bb_step_result.json` and "never rewrites it" without any redaction rule
    (`stories.md:276-278`).
- **What is missing/ambiguous/contradictory:** NFR-004 says credential values never appear in
  builder logs or run results. The persisted `runs/<id>/agent.log` and `bb_step_result.json` are
  run results; PENDING-2 only proves render-time redaction, and PENDING-3 never applies the shared
  helper. The cross-epic dependency is claimed on BSB-23's side only, so a BSB-26 implementer can
  build a path that never calls it.
- **Question (if a person must decide):** How does the BSB-26 result/log path obtain the resolved
  credential values and call BSB-23-PENDING-5's helper — and must the persisted `agent.log` and
  `bb_step_result.json` be redacted, or is redaction at render time sufficient for NFR-004? (also
  Open question 7)
- **Proposed change:** **PENDING-1, PENDING-2 and PENDING-3** Notes name BSB-23-PENDING-5's shared
  redaction as the rule they call, with the resolved values handed in. **PENDING-2** adds an AC
  that the stored log object read for the view is redacted (or states explicitly that redaction is
  render-time only and why that satisfies NFR-004). **PENDING-3** states the result document is
  passed through the same helper before anything derived from it is stored or shown.

### Finding 9 — Cross-story: PENDING-1's launch environment omits the ADR-014 presigned PUT URLs that PENDING-2 and PENDING-3 depend on
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3.
- **Evidence:**
  - ADR SK-001 §2a says the env contract includes "run and step ids, `BB_CONTEXT`, the ADR-014
    presigned PUT URLs" (`SK-001:156-159`).
  - PENDING-1's Notes say the adapter "passes the environment contract ADR SK-001 section 2a names
    — the bundle URL and hash, the run branch, `BB_CONTEXT`, and the run's model environment"
    (`stories.md:107-109`), omitting the presigned PUT URLs and the run/step ids; AC1's environment
    list matches that omission (`stories.md:64`).
  - PENDING-2 depends on "the adapter that writes the agent's `progress.json` and `agent.log` to
    `runs/21/` in the builder's object store" (`stories.md:192-195`); PENDING-3's scenarios
    require the agent to have uploaded `runs/21/bb_step_result.json` (`stories.md:230-252`).
    Neither story says where the upload URL comes from.
- **What is missing/ambiguous/contradictory:** Two stories assert agent-written objects in the
  builder's bucket, but the story that launches the agent never provides the write URLs. A
  developer building PENDING-1 to its AC would not wire them; PENDING-2 and PENDING-3's stubs
  would then mask the missing production path.
- **Question (if a person must decide):** Does PENDING-1 presign and pass the result/progress/log
  upload URLs (and the run/step ids) in the launch environment, and are those the same entries
  PENDING-2 and PENDING-3 rely on? (also Open question 8)
- **Proposed change:** **PENDING-1** AC1 and Notes add the ADR-014 presigned PUT URL(s) and the
  run/step ids to the asserted environment. **PENDING-2 and PENDING-3** Notes name the same env
  entries as their upload path, so all three stories describe one contract. No new design is
  implied — the entries are already in ADR SK-001 §2a.

## Open questions

1. **BB_CONTEXT shape (Finding 1).** Is `BB_CONTEXT` the step kit's six-field rendering rather
   than the raw `runs.context`, and what are the `allowed_result_statuses` for a run whose
   `context` is NULL?
2. **Deadline/cap ownership (Finding 3).** When BSB-27 stops a run for a cap or the deadline, does
   its recorded terminal reason win over PENDING-3's exit classification?
3. **Test-purpose admission (Finding 4).** Guaranteed at run start by BSB-24/BSB-23-PENDING-6, or
   re-checked by execution before a secret is read?
4. **MCP delivery owner (Finding 5).** Which run epic builds `BB_MCP_CONFIG` from
   `integrations.mcp`?
5. **Run detail page owner (Finding 6).** Which story creates
   `GET /projects/{projectId}/runs/{runId}` and applies the membership check?
6. **FR-065 attribution (Finding 7).** Does BSB-26 record the claimed verdict and BSB-29 only read
   it; does the epic map change?
7. **Redaction scope (Finding 8).** Must the persisted `agent.log` and `bb_step_result.json` be
   redacted, and who hands the helper the resolved values?
8. **Launch upload URLs (Finding 9).** Does PENDING-1 presign and pass the ADR-014 upload URLs and
   run/step ids that PENDING-2/PENDING-3 rely on?

## Proposed changes

Proposed only — nothing in `stories.md`, the story map, the PRD, the ADR or Jira was changed by
this review.

- **BSB-26-PENDING-1**
  - AC1: assert the six-field `BB_CONTEXT` (Finding 1); add the ADR-014 presigned PUT URL(s) and
    run/step ids (Finding 9); add a `runs.context` NULL launch scenario (Finding 1).
  - Notes: correct `BashH_CONTEXT` to `BB_CONTEXT` and name the step kit's `build_step_context`
    (Finding 1); say the data-model stage adds
    `runs.result_status`/`runs.claimed_verdict`/`runs.execution_error` and this story is the
    pre-launch consumer (Finding 2); add the test-purpose dependency (Finding 4); add the
    `integrations.mcp` → `BB_MCP_CONFIG` rule or its owner (Finding 5); name BSB-23-PENDING-5's
    redaction helper (Finding 8).
- **BSB-26-PENDING-2**
  - Notes: state that it owns the run detail route/shell and the BSB-22 membership check that
    precedes any read (Finding 6); name the upload env entries from PENDING-1 (Finding 9); name
    BSB-23-PENDING-5's helper (Finding 8).
  - AC redaction scenario: assert the stored log object is redacted, or state the render-time
    boundary explicitly (Finding 8).
- **BSB-26-PENDING-3**
  - ACs/Notes: require the document's `status` to be in `allowed_result_statuses` and define the
    NULL-context set (Finding 1); move the column ownership to the data-model stage (Finding 2);
    state that BSB-27's terminal reason wins and add an AC that a `failed_timeout` run is not
    overwritten (Finding 3); name the page dependency on PENDING-2/BSB-22 (Finding 6); state that
    recording `claimed_verdict` is FR-065 and BSB-29 consumes it (Finding 7); name the redaction
    helper (Finding 8) and the upload entry (Finding 9).
- **BSB-26-PENDING-4**
  - Notes: add the test-purpose dependency (Finding 4); add the page dependency on
    PENDING-2/BSB-22 (Finding 6).
- **Cross-epic follow-ups (recorded here, not applied)**
  - BSB-24-PENDING-2/-3: confirm the six-field `BB_CONTEXT` contract and the NULL-context answer
    (Finding 1).
  - BSB-27: record the terminal-state precedence between its watchdog/cap stop and the execution
    classifier (Finding 3).
  - BSB-24-PENDING-1 / BSB-23-PENDING-6: discharge the test-purpose admission; BSB-24's review
    Finding 3 must be applied (Finding 4).
  - BSB-23-PENDING-1/-2 and whichever run epic owns MCP delivery: name the same `BB_MCP_CONFIG`
    owner (Finding 5).
  - BSB-22-PENDING-3 / BSB-33: agree who owns the run detail page shell (Finding 6).
  - BSB-29: treat FR-065's recording as supplied by BSB-26; reconcile `epic-map.json`
    (Finding 7).
  - BSB-23-PENDING-5: define the helper's input and confirm the persisted result/log are in scope
    (Finding 8).

## Architecture impact

None. Every finding above is a story-contract fix against a design element that already exists
(ADR SK-001 §2a's env contract and context builder, §9's data model, PRD NFR-004/NFR-006); none
requires the design to change.

## Requirement coverage check

| Requirement | Story | Acceptance criteria that exercise it |
|---|---|---|
| FR-044 | BSB-26-PENDING-1 | AC1: the pinned runtime adapter starts one container for run 21 with the kit's image digest, step kit and env contract version. |
| FR-045 | BSB-26-PENDING-2 | AC1/AC2: progress `turns` and `last_event` rendered and refreshed. |
| FR-046 | BSB-26-PENDING-2 | AC1/AC2/AC6: log tail rendered, refreshed, and shown unavailable on a read failure. |
| FR-047 | BSB-26-PENDING-3 | AC1–AC5: completed/BLOCK, failed_execution, failed_incomplete, failed_infra; AC6 output-branch-only. |
| FR-048 | BSB-26-PENDING-1 | AC1: `agent_image_digest`, `stepkit_version` and `verify_version` recorded at launch; AC4 tag refused. |
| FR-049 | BSB-26-PENDING-4 | AC1: `model_profile_id`, `tier` and `model` recorded; AC3 not rewritten after a profile edit. |
| FR-151 | BSB-26-PENDING-1 | AC1: `verify_version` recorded at launch. |
| FR-152 | BSB-26-PENDING-4 | AC1/AC2: tier recorded and mapped to the concrete model. |

- **Coverage: yes for all eight.** `story-map.json` and `epic-map.json` agree on every ID; no
  requirement is missing, and no ID is claimed by two stories with different meanings.
- **FR-048 and FR-151** are both exercised by PENDING-1 — FR-151 is the verifier-specific slice of
  FR-048, not a contradictory second claim. **FR-049 and FR-152** are both exercised by PENDING-4
  for the same reason.
- **Traceability notes.** FR-065 is not assigned to BSB-26 but is implemented by PENDING-3
  (Finding 7). NFR-004 is mapped to BSB-23 and is exercised here by PENDING-1's DB/log assertion
  and PENDING-2's render redaction, with the persisted-result gap in Finding 8. NFR-012
  (accessibility) is BSB-38's cross-cutting requirement, as the BSB-22/BSB-31/BSB-32 reviews
  record, so it is not a silent epic-wide NFR here. NFR-015–NFR-017 (cost, tokens, turns) are
  BSB-34's; PENDING-2's "Turns" is explicitly the agent's live progress counter, not the recorded
  turn count, so there is no duplicate claim.

## Dependency-note sanity check

- **All referenced keys exist.** Within the epic: BSB-26-PENDING-1/-2/-3/-4. Cross-epic: BSB-18,
  BSB-22, BSB-22-PENDING-3, BSB-23-PENDING-2/-3/-4/-5, BSB-24-PENDING-1/-4,
  BSB-25-PENDING-1/-2/-3, BSB-27, BSB-28, BSB-29, BSB-31, BSB-32, BSB-33, BSB-34, BSB-37. No
  note points at a non-existent story. References to BSB-27/BSB-29/BSB-33/BSB-34 (epic
  definitions, no stories yet) are downstream dependencies, not dangling keys.
- **Reciprocated:** BSB-24-PENDING-4 → PENDING-4 (`runs.model_profile_id`/`tier`, `BB_MODEL`) is
  matched by PENDING-4's dependency on BSB-24-PENDING-4. BSB-25-PENDING-2/-3 →
  PENDING-1/PENDING-3 (bundle URL and hash, source-control writer) are matched by PENDING-1 and
  PENDING-3. BSB-25-PENDING-3's deny-by-default writer rule is applied by PENDING-3 AC6, as the
  BSB-25 review's Finding 6 follow-up asked.
- **Broken or one-sided:**
  - PENDING-1 ↔ PENDING-3 on the `result_status`/`execution_error` columns is circular
    (Finding 2).
  - PENDING-3 and PENDING-4 assert the run detail page but name neither PENDING-2 nor BSB-22 for
    it (Finding 6).
  - BSB-24-PENDING-2/-3's "BSB-26 owns the BB_CONTEXT rendering" is not matched by PENDING-1's
    stated shape (Finding 1).
  - BSB-23-PENDING-5's claim that BSB-26's result writer calls its redaction helper has no
    counterpart in BSB-26 (Finding 8).
  - BSB-23-PENDING-1/-2 → run delivery of `integrations.mcp` has no owner in any run epic
    (Finding 5).
- **Carry-forwards, not BSB-26 defects:** BSB-25's escalated bundle-shape question is correctly
  referenced and insulated by PENDING-1's opaque-bundle handling; BSB-24's Finding 3 and BSB-23's
  Findings 6–7 are the upstream halves of Findings 4, 8 and 5 and must land on their own epics'
  passes.
