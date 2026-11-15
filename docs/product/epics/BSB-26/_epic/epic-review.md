# Epic Review — BSB-26: Run execution & outcome capture

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-15 · **Stories reviewed:** BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3, BSB-26-PENDING-4

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-26/_epic/epic-review.md`.

## Context loaded

- **Target resolution.** The run's target was `SkillBuilder`. That is the product title of
  `docs/product/PRD.md`, not a Jira issue, as the BSB-26 `stories.md` header also records. The
  Atlassian MCP server was not connected in this session: no Jira tools were offered, and the local
  `.mcp.json` declares `args` as a string rather than an array. The epic was therefore resolved
  from disk. BSB-26 is the epic the most recent `sdlc-plan-stories-write` run wrote (commit
  `7e10c04`), and it has no review yet. Its `stories.md` header says the epic was fetched read-only
  from Jira during decomposition and matches the BSB-26 section of `epics.md`. Nothing was read from
  or written to Jira in this pass.
- **All 4 BSB-26 stories**, from `docs/product/epics/BSB-26/_epic/stories.md` and
  `story-map.json`, the full set:
  - PENDING-1: execute a prepared run in the pinned runtime (FR-044).
  - PENDING-2: progress and logs (FR-045, FR-046).
  - PENDING-3: outcome classification (FR-047).
  - PENDING-4: execution provenance (FR-048, FR-049, FR-151, FR-152).

  Also read the shared "Execution and outcome contract" preamble: fixtures, run-state vocabulary,
  executor claim contract, result rules, page texts, runtime environment, progress, log and error
  contracts, and cross-epic notes.
- `docs/product/epic-map.json`: BSB-26 → FR-044, FR-045, FR-046, FR-047, FR-048, FR-049, FR-151,
  FR-152 (no NFRs). The NFR ownership of every other epic was read to check epic-wide NFRs:
  - BSB-23: NFR-004, NFR-006.
  - BSB-25: NFR-001, NFR-009.
  - BSB-27: NFR-007, NFR-008, NFR-019.
  - BSB-34: NFR-011, NFR-013 to NFR-018.
  - BSB-38: NFR-012.
- `docs/product/PRD.md`: the FA-7 rows FR-044 to FR-049, FR-151 and FR-152; FR-128 and FR-129;
  NFR-001 to NFR-019; the "MCP definitions" and "Installation settings" paragraphs.
- `docs/product/epics.md`: the BSB-26 section (description, scope, edge cases, guidance, DoD).
  Neighbouring sections were read for ownership: BSB-23 (integrations, MCP definitions, NFR-004
  redaction), BSB-24, BSB-25 (preparation and edge cases) and BSB-27 (caps, deadline supervisor,
  refusals).
- `docs/adr/SK-001-skill-builder.md`:
  - §2: the components and the single kit pin.
  - §2a: the step kit (context builder, env contract including git coordinates, `BB_MCP_CONFIG`
    and the ADR-014 presigned PUT URLs, launch, outcome join).
  - §5: run launch and outcome, and the default context.
  - §6: the results layout under `runs/<run-id>/`.
  - §9: the `runs`, `skill_bundles` and `integrations` columns.
  - The v1 non-goals.

  The repo has no separate `architecture.md`, `data-model.md`, `api-contracts/` or
  `ui-conventions.md`, so SK-001 §9 serves as the data model.
- Other epics' stories, only far enough to check cross-epic claims:
  - BSB-24 `stories.md`: the run-start contract, the `runs`-row table and the PENDING-3/PENDING-4
    Notes.
  - BSB-24 `epic-review.md` Finding 5 and `revisions.md`: Open question 4 on the default context
    is still unanswered.
  - BSB-22 `stories.md`: the error table and validation order.
  - Actor names in BSB-18, BSB-20, BSB-22 and BSB-24.

  BSB-23, BSB-25, BSB-27, BSB-29, BSB-33 and BSB-34 have no stories yet. Their scope was checked
  against `epics.md`, `epic-map.json` and the PRD only. No `sdlc-plan-epic-sequence` output exists
  yet.

## Findings

### Finding 1 — Cross-epic scope boundary: the default context and the rendering of reviewer feedback / upstream handoff are handed to BSB-26, and no BSB-26 story takes them
- **Severity:** Blocking
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-3 (and BSB-24-PENDING-3, BSB-24-PENDING-4
  across the epic boundary)
- **Evidence:**
  - BSB-24's `runs`-row contract stores `context` as "the request's context, or `{}` when omitted".
  - BSB-24-PENDING-3 Notes say that when the context is omitted, "the default workflow resolution
    is left to epic BSB-26".
  - BSB-24-PENDING-3 and BSB-24-PENDING-4 Out of scope both name "rendering … into `BB_CONTEXT`
    (epic BSB-26)".
  - BSB-24 `revisions.md` lists Open question 4 (who resolves the default) as still unanswered.
  - BSB-26's fixture only has run `1` with `context` = `{"workflow":"bug-fix","step":"triage"}`.
    PENDING-1 asserts `BB_CONTEXT` only for that context, with `reviewer_feedback` and
    `upstream_handoff` = `null`.
  - PENDING-3's result rules depend on "`allowed_result_statuses`" from "the selected workflow
    step's config on the skills commit" (PENDING-3 Notes). With `context` = `{}`, no step is
    selected, so PENDING-3 has no allowed set to classify against.
  - No BSB-26 story's Out of scope mentions the default or the feedback/handoff rendering.
  - SK-001 §5.3 defines the default as "a workflow in the skills branch's `config/` that uses this
    skill".
- **What is missing:**
  - The most common run start, with the context omitted, has no defined `BB_CONTEXT` in PENDING-1
    and no allowed result set in PENDING-3. Two implementers would choose differently: an empty
    set (every run is `failed_incomplete`), the platform default, or a refusal at claim.
  - FR-148's reviewer feedback and upstream handoff reach the runtime only by implication. No
    scenario shows a non-null value arriving in `BB_CONTEXT`.
- **Question (a person must decide):** This is the same decision as BSB-24 Open question 4, and
  one answer should close both epics:
  - Does run start resolve the default workflow and step and store them in `runs.context`?
  - Or does BSB-26 resolve it at claim time from the pinned skills commit?
  - If BSB-26 resolves it: what happens to a run whose skill is used by no workflow on the
    commit, or by more than one?
  (Also listed under Open questions.)
- **Proposed change:**
  - BSB-26-PENDING-1: add a scenario where the run's `context` carries `reviewer_feedback` and
    `upstream_handoff` (BSB-24-PENDING-4's fixture values). It asserts that `BB_CONTEXT` carries
    them as rendered by `build_step_context`.
  - BSB-26-PENDING-1, if BSB-26 owns the default: add a scenario for `context` = `{}` that names
    the resolved workflow/step in `BB_CONTEXT`, and one per "no workflow / several workflows"
    outcome per the answer.
  - BSB-26-PENDING-1, if run start owns the default: add a Notes line that a claimed run's
    `context` always has `workflow` and `step`.
  - BSB-26-PENDING-3: state in Notes where `allowed_result_statuses` comes from when the author
    omitted the context, matching PENDING-1.
  - BSB-26 preamble, cross-epic notes: replace "BSB-24's workflow fixture" with a note that records
    who resolves the default, citing BSB-24 Open question 4.

### Finding 2 — Epic-wide scope boundary: no story wires the project's source-control and Jira integrations or their MCP definitions into the runtime environment
- **Severity:** Blocking
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-4 (and epic BSB-23's FR-128, FR-129 across
  the epic boundary)
- **Evidence:**
  - PRD "MCP definitions": "A Jira or source-control integration may carry an MCP server definition
    that **the runner passes to the skill**." FR-128 and FR-129 (BSB-23) only *record* the
    definition "that the … integration exposes to a run".
  - SK-001 §2a's env contract includes "git coordinates and `RUN_BRANCH`", the "vendor key and base
    URL" and "`BB_MCP_CONFIG` from the selected MCP servers". §5.2 says `run_skill.sh` "clones the
    run branch … commits and pushes to it".
  - BSB-26 preamble, "Environment handed to the runtime", fixes six variables. The BSB-26 fixture
    contains only the `ai_model` integration, with no `github` or `jira` row (BSB-24's fixture has
    all three).
  - PENDING-1 Notes depend on BSB-23 only "for the `ai_model` integration".
  - PENDING-4 resolves only the model (`BB_MODEL`).
  - No story's Out of scope mentions git coordinates, the sandbox-repo credential, the Jira
    credential or `BB_MCP_CONFIG`.
- **What is missing:** the step that makes the run able to clone and push the run branch and reach
  Jira/GitHub through MCP has no owner in any epic. BSB-23 stores the definitions, and BSB-26 is
  the only epic that launches the container. A PENDING-1 implementation can pass every scenario
  and still start an agent that cannot clone `skilltest/1`.
- **Question:** None. FR-044 ("the same runtime as the platform") and the PRD sentence place the
  pass-through on the runner, so this is a scope wording fix.
- **Proposed change:**
  - BSB-26 preamble: add the project's `github` integration (and the `jira` integration with an
    `mcp` definition) to the fixture, reusing BSB-24's rows `id` `5` and `6`. Extend the
    environment table with the git coordinates for `saraavrnd/bheembhai-skill-fixtures` and
    `BB_MCP_CONFIG` built from the integrations' `mcp` values. State that every credential is
    injected from Secrets Manager by `secret_ref` and never appears in the stored env or the log.
  - BSB-26-PENDING-1: add one scenario asserting the git coordinates and `BB_MCP_CONFIG` on the
    container (values, not credentials). Add a Notes line that BSB-26 renders FR-128/FR-129's
    stored definitions into the env, and depends on BSB-23 for the `github` and `jira`
    integrations as well as `ai_model`.
  - BSB-26-PENDING-4: no AC change. Its Notes should say that only the model is resolved there,
    and that the other integrations' env values are PENDING-1's.

### Finding 3 — Cross-story contradiction: who writes `agent.log`, and how the agent can write `progress.json` and `bb_step_result.json` at all, differs between PENDING-1, PENDING-2 and PENDING-3
- **Severity:** Blocking
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3
- **Evidence:**
  - Who writes `agent.log`:
    - PENDING-2 Notes: "It depends on the agent image's existing `progress.json` and `agent.log`
      outputs, which are part of the platform image contract". This makes the image the writer.
    - Preamble log contract: "its standard output and standard error are captured to
      `s3://…/agent.log`". PENDING-2's truncation scenario: "When **the builder flushes the
      captured log** to `…/agent.log` … the stored log's first line is exactly `[skill-builder]
      log truncated: …`". This makes the builder the writer.
    - PENDING-1's start-failure scenario: "the first line of `…/runs/1/agent.log` is exactly
      `[skill-builder] runtime start failed: …`". Here the builder writes before any image runs.
  - The PUT URLs:
    - SK-001 §2a's env contract hands the agent "the ADR-014 presigned PUT URLs" for its uploads.
    - The PENDING-1 environment table and scenarios name no PUT URL.
    - PENDING-2 reads `progress.json` from `runs/1/`, and PENDING-3 reads `bb_step_result.json`
      from `runs/1/`. Both rely on the agent writing exactly those keys.
- **What is missing/contradictory:**
  - If the image uploads `agent.log` through a presigned PUT, it overwrites the builder's
    truncation marker and start-failure line, and the 10 MiB cap is not the builder's to enforce.
  - If the builder captures container output, the image must not be given a PUT URL for that
    key.
  - Either way, PENDING-1 (which builds the env) never commits to the PUT URLs for the keys that
    PENDING-2 and PENDING-3 read, so the three stories can each pass while the integrated run
    finds no result file.
- **Question (a person must decide):** Is `runs/<id>/agent.log` the builder's own capture of the
  container's stdout/stderr, so the builder is its only writer and enforces the cap and marker? Or
  is it the agent image's own upload? In the second case, how are the truncation marker and the
  start-failure line kept? (Also listed under Open questions.)
- **Proposed change:**
  - BSB-26-PENDING-1: extend the environment table and the first scenario with the presigned PUT
    URLs the step kit's env contract requires. Assert that their paths are exactly
    `/runs/1/progress.json` and `/runs/1/bb_step_result.json` (and `/runs/1/agent.log` only if the
    answer makes the image the writer).
  - BSB-26-PENDING-2: change the Notes line on "the agent image's existing … `agent.log` outputs"
    to match the answer. If the builder captures, the dependency on the image is `progress.json`
    only, and the builder is the sole writer of `agent.log`.
  - BSB-26-PENDING-3: add a Notes line that `bb_step_result.json` is read from the key PENDING-1's
    PUT URL points at.
  - Preamble log contract: name the single writer of `agent.log`.

### Finding 4 — Cross-story / cross-epic state contract: the state vocabulary is declared complete, but sibling epics' terminations collide with PENDING-3's classification
- **Severity:** Blocking
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-3 (and epics BSB-25, BSB-27 across the
  boundary)
- **Evidence:**
  - Preamble: "The values below are the whole state vocabulary for this epic" lists `queued`,
    `running`, `completed`, `failed_infra`, `failed_execution`, `failed_incomplete` and
    `failed_timeout` (BSB-27).
  - Preamble cross-epic notes: "a run it leaves `running` may be terminated as `failed_timeout` by
    BSB-27".
  - PENDING-3's rule: "exits with a non-zero status | missing … | `failed_execution`". A container
    killed by BSB-27's deadline supervisor ("force-terminates", `epics.md` BSB-27 guidance) exits
    non-zero with no result. PENDING-3's reconciler, which is not written as a compare-and-set
    from `running` (unlike PENDING-1's claim), would then write `failed_execution` over
    `failed_timeout`, or be overwritten by it, depending on timing.
  - BSB-27 FR-051 and FR-053: "A run stops when it reaches its turn/spend cap". No state for a
    cap-stopped run appears in the "whole" vocabulary, and PENDING-3 would classify the killed
    container as `failed_execution` or `failed_incomplete`.
  - BSB-25 edge case: "a missing or unreadable input branch must fail before a run branch is
    created". PENDING-1's claim predicate never claims a run with `run_branch IS NULL`, and the
    vocabulary has no preparation-failure state. Such a run stays `queued` with no owner of its
    terminal state, which conflicts with NFR-007 ("every run reaches a terminal state").
- **What is missing/contradictory:** one precedence rule for terminal writes, and the terminal
  states sibling epics need before BSB-26 declares the vocabulary closed.
- **Question (a person must decide):** What `runs.state` does a run stopped at its turn or spend
  cap end in? Is it a BSB-27-owned value such as `failed_cap`, or classified by PENDING-3's rules?
  What state does BSB-25 leave a run whose preparation fails? (Also listed under Open questions.)
- **Proposed change:**
  - Preamble: change "the whole state vocabulary for this epic" to list the answered cap-stop and
    preparation-failure states as owned by BSB-27 and BSB-25 respectively. Add the rule "every
    transition out of `running` is a compare-and-set on `state = 'running'`; the first terminal
    write wins, and BSB-27 writes its terminal state before it stops the container."
  - BSB-26-PENDING-3: add a scenario where run `1` is already `failed_timeout` when its container
    exits with status `137` and no result. The reconciler leaves `state` = `failed_timeout` and
    `claimed_verdict` = `NULL`. Add a Notes line on the compare-and-set.
  - BSB-26-PENDING-1: add a Notes line that a run left `queued` by a failed preparation is BSB-25's
    to terminate and is never claimed here.

### Finding 5 — Cross-story contradiction: the progress and log surfaces are defined only for `running`, but PENDING-1 and PENDING-3 end runs that the same surfaces still serve
- **Severity:** Blocking
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3
- **Evidence:**
  - Preamble progress contract: before the first `progress.json`, the API returns
    `{"run_id":1,"step":null,"state":"running",…}` and the page shows `Waiting for the skill to
    report progress.`. The `state` field is otherwise copied from the agent's `progress.json`.
  - PENDING-1's start-failure scenario ends run `1` as `failed_infra` with no container, so
    `progress.json` never exists. As written, the progress API returns `"state":"running"` for
    that run, and the page shows "Waiting for the skill to report progress." next to `The runtime
    could not be started.`.
  - PENDING-3's terminal runs keep the agent's last `progress.json`, so the API keeps reporting
    `"state":"running"` after `runs.state` = `completed` or `failed_*`.
  - PENDING-1 Notes: the start-failure reason "is durable in … the first line of the stored log".
    PENDING-2 covers the log region only for `state` = `running`, and its Notes keep the ids "for
    runs in `running`". No story says whether the log, and the failure line and truncation marker
    in it, stays readable once the run has ended. BSB-33 (no stories yet) owns only the full
    report.
- **What is contradictory:** the progress API reports a different state than `runs.state` for
  every run that PENDING-1 or PENDING-3 has ended. It is undefined whether the log that carries
  PENDING-1's durable failure reason can be read after the run ends.
- **Question:** None. The fix keeps FR-045/FR-046 as written and removes the contradiction.
- **Proposed change:**
  - Preamble progress contract: the API's `state` is `runs.state`, not the agent's own field. The
    progress region is absent once `runs.state` is terminal, as the outcome region is absent while
    `running`.
  - Preamble log contract: the log API and the `run-log` element keep serving the stored log after
    the run ends, so PENDING-1's failure line and PENDING-2's marker stay visible until BSB-33
    replaces the page.
  - BSB-26-PENDING-2: add a scenario for a `failed_infra` run. The progress API returns
    `"state":"failed_infra"`, the page has no progress region, and the log API returns the
    start-failure line.
  - BSB-26-PENDING-3: add one `Then` to the `completed` scenario: the progress region is absent.
  - BSB-26-PENDING-1: add one `Then` to the start-failure scenario: the page's `run-log` element
    contains the `[skill-builder] runtime start failed: …` line.

### Finding 6 — Cross-story architecture fit: a run whose executor stops is never reconciled
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-3
- **Evidence:**
  - PENDING-1 claim contract: "A run already in `running` … is never claimed again."
  - PENDING-3: "When the executor reconciles the exit" assumes the same executor process is alive
    when the container exits.
  - PENDING-1 already labels every container `bb.run_id`, so the information to recover exists.
- **What is missing:** if an executor process restarts (for example on a deploy) while its run's
  container is still going, nobody reconciles that container's exit. Even a valid uploaded result
  is then lost, and the run sits in `running` until BSB-27's deadline marks it `failed_timeout`.
  It is safe to build as written, but the run gets a wrong terminal state.
- **Question:** None.
- **Proposed change:**
  - BSB-26-PENDING-3: add a scenario where an executor that starts while run `1` is `running` and
    its container (label `bb.run_id` = `1`) has exited with status `0` and a valid
    `bb_step_result.json` reconciles it to `completed`. Apply the same compare-and-set as
    Finding 4.
  - BSB-26-PENDING-1: add a Notes line that executors find their in-flight runs by the `bb.run_id`
    label after a restart.

### Finding 7 — Epic-wide silent NFRs: NFR-004 and NFR-011 bind this epic's capture and launch, and no story names the dependency
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-2 (and epics BSB-23, BSB-34 across the
  boundary)
- **Evidence:**
  - NFR-004, owned by BSB-23: "Credential values never appear in builder logs or run results".
    BSB-23's guidance ends with "redaction tests proving credentials" are kept out.
  - PENDING-2 stores and serves the container's raw stdout/stderr through the log API and the page.
    PENDING-1 writes daemon error text into the same `agent.log`.
  - The preamble says credentials "are not stored or logged" only for the env injection, not for
    what the agent prints.
  - NFR-011, owned by BSB-34: "every run's trace identifies it as a test-environment run".
    SK-001 §6 places this in the trace (`env = skilltest`), which is set at launch (PENDING-1's
    env), yet PENDING-1's Out of scope and Notes do not mention tracing.
- **What is missing:** the two NFRs apply to every run this epic starts and every log it stores,
  but no story either applies them or names BSB-23/BSB-34 as the owner of the mechanism. Each of
  those epics' designers would rediscover the need for a hook here.
- **Question:** None. Ownership already sits with BSB-23 and BSB-34. Only the dependency needs to
  be written down, plus one guard scenario.
- **Proposed change:**
  - BSB-26-PENDING-2: add a Notes line that the captured log passes through BSB-23's NFR-004
    redaction before it is stored or served. Add one scenario: a log line containing the fixture's
    `ai_model` secret value is returned with the value replaced, using BSB-23's mask.
  - BSB-26-PENDING-1: add a Notes line that the launch env carries the step kit's tracing settings
    with the test-environment marker required by NFR-011, which BSB-34 owns. Add tracing to the Out
    of scope list beside "token usage and cost".

### Finding 8 — Epic-wide error contract: the run routes' 404 and path/run project mismatch are not exercised or decided by any story
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3
- **Evidence:**
  - Preamble error table: 404 `run_not_found` ("Run 999 does not exist."), and a 403 defined on
    "the run's `project_id`". The preamble also says "the BSB-22 project-membership decision run[s]
    before these checks". BSB-22's decision is on the *path* project, with 404 `project_not_found`
    first.
  - The run page route is asserted by PENDING-1, PENDING-2 and PENDING-3. Only PENDING-2 has an
    error scenario: the progress API, a non-member, 403.
  - No story asserts `run_not_found`, the run page's 403, or `GET /projects/8/runs/1` (path project
    `8`, run `1` in project `7`).
- **What is missing:** a member of project `8` who is not a member of project `7` would pass
  BSB-22's path check. Whether they then get 403, 404 or the run is left to each route's
  implementer. That is an inconsistency, and possibly a cross-project disclosure, spread across
  three stories' surfaces.
- **Question:** None. The proposal follows the existing "don't disclose" pattern of BSB-22's 404.
- **Proposed change:**
  - Preamble error table: add "the run's `project_id` differs from the path's `project_id` → 404
    `run_not_found`". State that the order is BSB-18 gates → BSB-22 `project_not_found` → BSB-22
    membership on the path project → `run_not_found`.
  - BSB-26-PENDING-2: add scenarios for `GET /api/projects/7/runs/999/progress` (404
    `run_not_found`) and for a path/run project mismatch (404). Add one run-page scenario for a
    non-member (403), since the page route is shared with PENDING-1 and PENDING-3.

### Finding 9 — Dependency-note sanity: PENDING-2 attributes the run bucket to BSB-23, which does not own it
- **Severity:** Advisory
- **Stories touched:** BSB-26-PENDING-2, BSB-26-PENDING-1
- **Evidence:**
  - PENDING-2 Notes: "on epic BSB-23's object-store configuration for the bucket".
  - BSB-23's scope in `epics.md` covers Jira, source-control and model integrations, secrets and MCP
    definitions, with no bucket. BSB-25's Notes treat the bucket as "the external object-storage
    bucket". SK-001 §6 calls it the skill builder's own bucket.
  - PENDING-1 uses the same `skill-builder-runs` bucket (bundle URL, start-failure log line) and
    names no dependency for it.
- **What is wrong:** the note points at an epic that will not deliver the bucket, and the sibling
  story that writes to the bucket first does not name the bucket dependency.
- **Question:** None.
- **Proposed change:** BSB-26-PENDING-2 and BSB-26-PENDING-1 Notes both say the same thing: they
  depend on the installation-provisioned `skill-builder-runs` bucket (SK-001 §6, the same bucket
  BSB-25 writes bundles to). PENDING-2's reference to BSB-23 for the bucket is removed.

## Open questions

1. **Default context (Finding 1; the same decision as BSB-24 Open question 4).** When the author
   omits `context`, does run start resolve the default workflow and step from the chosen skills
   branch and store them in `runs.context`? Or does BSB-26 resolve them at claim from the pinned
   skills commit? Under either answer, what happens when no workflow, or more than one, uses the
   skill: refuse at start, `failed_infra` at claim, or something else? One answer closes both
   epics.
2. **`agent.log` writer (Finding 3).** Is `runs/<id>/agent.log` the builder's capture of the
   container's stdout/stderr, so the builder is its only writer and enforces the 10 MiB cap and
   marker? Or is it an upload by the agent image through a presigned PUT? If the image uploads
   it, how do PENDING-1's start-failure line and PENDING-2's truncation marker survive?
3. **Terminal states owned by sibling epics (Finding 4).** What `runs.state` does a run stopped at
   its turn or spend cap (BSB-27, FR-051, FR-053) end in? What state does BSB-25 give a run whose
   preparation fails (missing input branch, unpackable skill)? Both values must be named before
   the BSB-26 vocabulary is declared complete.

## Proposed changes

- **BSB-26 preamble (shared by all four stories)**
  - Cross-epic notes: record who resolves the default context (Finding 1).
  - Fixture: add the `github` and `jira` integrations. Environment table: add git coordinates,
    `BB_MCP_CONFIG` and the presigned PUT URLs (Findings 2, 3).
  - Log contract: name the single writer of `agent.log` (Finding 3).
  - State vocabulary: list the BSB-25 and BSB-27 terminal states, and add the compare-and-set and
    "first terminal write wins" rule (Finding 4).
  - Progress API: `state` mirrors `runs.state`. The progress region is absent for terminal runs,
    and the log stays readable after the run ends (Finding 5).
  - Error table: add the path/run project mismatch → 404 and the full check order (Finding 8).
- **BSB-26-PENDING-1**
  - Scenarios to add:
    - `BB_CONTEXT` carrying reviewer feedback and upstream handoff, plus the default-context
      scenarios per Open question 1 (Finding 1).
    - Git coordinates and `BB_MCP_CONFIG` on the container (Finding 2).
  - Changes to existing scenarios:
    - The first scenario asserts the presigned PUT URL paths (Finding 3).
    - The start-failure scenario asserts the failure line in `run-log` (Finding 5).
  - Notes:
    - Dependency on BSB-23's `github`/`jira` integrations and FR-128/FR-129 definitions
      (Finding 2).
    - A queued run whose preparation failed is BSB-25's to terminate (Finding 4).
    - Recovery of in-flight runs by the `bb.run_id` label (Finding 6).
    - NFR-011 tracing marker owned by BSB-34, and tracing added to Out of scope (Finding 7).
    - Bucket dependency (Finding 9).
- **BSB-26-PENDING-2**
  - Scenarios to add:
    - A `failed_infra` run's progress and log (Finding 5).
    - Log redaction of a credential value (Finding 7).
    - 404 `run_not_found`, path/run project mismatch, and run-page 403 (Finding 8).
  - Notes:
    - Correct the `agent.log` writer per Open question 2 (Finding 3).
    - Redaction dependency on BSB-23's NFR-004 (Finding 7).
    - Replace the BSB-23 bucket reference with the installation bucket (Finding 9).
- **BSB-26-PENDING-3**
  - Scenarios to add:
    - An already-`failed_timeout` run is not overwritten on exit (Finding 4).
    - An executor restart reconciles an exited container (Finding 6).
  - Changes to existing scenarios: the `completed` scenario asserts the progress region is absent
    (Finding 5).
  - Notes:
    - Where `allowed_result_statuses` comes from for an omitted context (Finding 1).
    - `bb_step_result.json` is read from PENDING-1's PUT URL key (Finding 3).
    - Terminal transitions are compare-and-set from `running` (Finding 4).
- **BSB-26-PENDING-4**
  - Notes only: model resolution is the only env value owned here, and the other integrations'
    env values are PENDING-1's (Finding 2).
- **Across the boundary (not applied by this epic's revise pass, recorded for the owning epics):**
  - BSB-24-PENDING-3 and BSB-24-PENDING-4: per Open question 1.
  - BSB-25 and BSB-27 decompositions: per Open question 3.

## Architecture impact

None. Every finding is closed by a story or contract change inside SK-001 §2a, §5, §6 and §9.
The step kit already defines the env contract (git coordinates, `BB_MCP_CONFIG`, presigned PUT
URLs) and the outcome join. The `runs.state` column is free-form in §9, so the extra terminal
values in Finding 4 need no schema change.

## Requirement coverage check

Yes, with notes.
- FR-044 (PENDING-1), FR-045 and FR-046 (PENDING-2), FR-047 (PENDING-3), and FR-048, FR-049,
  FR-151 and FR-152 (PENDING-4) are each exercised by at least one acceptance scenario.
- No FR is claimed by two stories. The covered-requirement lists match `story-map.json`.
- The `epic-map.json` IDs match the current `PRD.md` and `epics.md` wording for all eight
  requirements.
- PENDING-1 and PENDING-4 both assert the container's `BB_MODEL` and `bb.stepkit` label, and the
  start-failure provenance. Their values agree, and the split is clean: PENDING-1 covers launch,
  PENDING-4 covers persistence.
- Notes:
  - FR-044 is only partly exercised. The env contract that makes it "the same runtime as the
    platform" omits the integration coordinates and MCP definitions (Finding 2) and the PUT URLs
    (Finding 3).
  - FR-047 has no defined allowed set for an omitted context (Finding 1), and can contradict
    BSB-27's `failed_timeout` (Finding 4).
  - FR-045's API reports the agent's state rather than the run's (Finding 5).

## Dependency-note sanity check

Mostly yes. Every in-epic note names a real BSB-26 story. Every cross-epic note names a real epic
(BSB-18, BSB-22, BSB-23, BSB-24, BSB-25, BSB-27, BSB-29, BSB-31 to BSB-35, BSB-37, BSB-38).
- PENDING-2, PENDING-3 and PENDING-4 each depend on PENDING-1 (for a `running` run, or for the
  claim). PENDING-1's Out of scope names PENDING-3 and PENDING-4 for those slices, so the pairs
  agree.
- BSB-24's `runs`-row contract says BSB-26 fills `agent_image_digest`, `stepkit_version`,
  `verify_version` and the verdict columns. PENDING-3 and PENDING-4 do so, and leave
  `final_verdict`/`verification` to BSB-29. The two sides agree.
- BSB-25 has no stories. BSB-26's assumptions about its outputs (`skills_commit_sha`,
  `run_branch`, `skill_bundles`, `queued` until claimed) are written down in the preamble and in
  PENDING-1's Notes.

Mismatches:
- BSB-24 hands default-context resolution and `BB_CONTEXT` rendering to BSB-26, and no BSB-26
  story accepts it (Finding 1).
- PENDING-2 depends on BSB-23 for the bucket, which BSB-23 does not own, and PENDING-1 names no
  bucket dependency (Finding 9).
- PENDING-1 depends on BSB-23 for `ai_model` only, though it needs the `github` and `jira`
  integrations and their MCP definitions (Finding 2).

Build order itself is left to `sdlc-plan-epic-sequence`.
