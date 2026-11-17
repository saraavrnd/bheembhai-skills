# Epic Review — BSB-23: Integrations, credentials & MCP definitions

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-17 · **Stories reviewed:** BSB-23-PENDING-1, BSB-23-PENDING-2, BSB-23-PENDING-3, BSB-23-PENDING-4, BSB-23-PENDING-5, BSB-23-PENDING-6

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-23/_epic/epic-review.md`. This pass follows the Pass 1 revision in
> `revisions.md` (2026-11-17), which applied the previous report's seven findings; each of those is
> re-checked below against the revised story text, and only the residual cross-epic contradictions
> are reported.

## Context loaded

- Work item: the run binds the epic to `BSB-23` (`BB_CONTEXT.ITEM`); `SkillBuilder-2` is the PRD
  umbrella, and `GET /rest/api/3/issue/SkillBuilder-2` returns HTTP 404 ("Issue does not exist or you
  do not have permission to see it"), matching `PRD.md` section 8. The Atlassian MCP tools were not
  exposed in this session, so the configured site was queried read-only over REST (GET only); the
  `BSB-23` epic itself was read and matches the `epics.md` section. No Jira write was made.
- All six BSB-23 stories from `docs/product/epics/BSB-23/_epic/stories.md` (full set, not a sample)
  and `story-map.json`.
- `docs/product/epics/BSB-23/_epic/revisions.md` — Pass 1, which applied the prior report.
- `docs/product/PRD.md` — FA-5 (line 54), FR-029 through FR-036 (lines 103-110), FR-128 and
  FR-129 (lines 202-203), NFR-004 (line 254), NFR-006 (line 256).
- `docs/product/epics.md` — the BSB-23 section (lines 439-507), including the Goal / Definition of
  Done at lines 481-486 ("a verified integration is usable by runs"; "MCP server definitions are
  stored as non-secret configuration and are available to a run").
- `docs/adr/SK-001-skill-builder.md` — §2a environment contract (`BB_MCP_CONFIG` built from the
  selected MCP servers), §4 credentials (lines 200-204: injected at start, tmpfs, "never logged or
  written to disk"), §6 results (lines 256-260: `runs/<run-id>/` holds the bundle,
  `bb_step_result.json`, logs and transcript), and §9 data model (`integrations` columns;
  `runs` has `model_profile_id`/`tier` but no Jira or source-control integration id).
- `docs/product/epic-map.json` — the twelve requirements mapped to BSB-23: FR-029, FR-030, FR-031,
  FR-032, FR-033, FR-034, FR-035, FR-036, FR-128, FR-129, NFR-004, NFR-006.
- Cross-epic contracts read side by side: `BSB-22/_epic/stories.md` (PENDING-4 guard),
  `BSB-24/_epic/stories.md` (PENDING-1 run request, PENDING-4 model profile),
  `BSB-25/_epic/stories.md` (PENDING-3 bundle/output-branch writer),
  `BSB-26/_epic/stories.md` (PENDING-1 launch env, PENDING-2 live log, PENDING-3 execution
  classification), and `BSB-33/_epic/stories.md` (PENDING-1 run report). No BSB-23
  `epic-sequence.md` exists yet.
- No ADR-035 write outside this report; no story, map or Jira issue was edited.

## Findings

### Finding 1 — Cross-epic run-request contract: a "selected Jira/source-control integration id" that BSB-24 does not record
- **Severity:** Blocking
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-2, BSB-23-PENDING-5; cross-epic
  BSB-24-PENDING-1, BSB-26-PENDING-2.
- **Evidence:**
  - `stories.md:111-113` (PENDING-1): "BSB-24 records the selected Jira integration id in the run
    request, and BSB-26 builds `BB_MCP_CONFIG` from this row's `integrations.mcp` value when it
    launches the run container".
  - `stories.md:220-222` (PENDING-2): "BSB-24 records the selected source-control integration id in
    the run request, and BSB-26 builds `BB_MCP_CONFIG` from this row's `integrations.mcp` value".
  - `stories.md:488` (PENDING-5): "run 11 in project 7 whose selected Jira integration is 3";
    `stories.md:522-524`: the helper's input is "the text or document to redact, the project id and
    the run's selected integration ids".
  - `docs/product/epics/BSB-24/_epic/stories.md:93-98` lists the request fields exhaustively —
    `build_id`, `skills_branch`, `input_branch`, `workflow`, `step`, `reviewer_feedback`,
    `upstream_handoff`, `model_profile_id`, `tier` — with no Jira or source-control integration id;
    `:122-124` says "Jira is not a run-start choice: the run inherits the project's Jira integration
    when execution seeds or reads Jira (BSB-26 and BSB-28), so a missing Jira integration is not a
    run-start refusal."
  - `stories.md:123-126` and `:216-218` establish that a project has at most one Jira integration
    and at most one source-control integration; `ADR SK-001` §9 gives `runs` `model_profile_id` and
    `tier` but no Jira/github integration id.
  - `docs/product/epics/BSB-26/_epic/stories.md:209-211` says the builder "knows the run's injected
    values from its secret references", but the run record holds no such references; they can only
    be derived from the project id (plus `model_profile_id`).
- **What is missing/ambiguous/contradictory:** the run has no integration selection to record. The
  only selected integration is the AI model profile (`runs.model_profile_id`); the Jira and
  source-control integrations are determined by `runs.project_id` because each is one-per-project.
  BSB-23 twice asserts a run-request field that BSB-24's contract and acceptance criteria do not
  have, and that `ADR SK-001` §9 does not model. A BSB-24 implementer following its own story will
  not add it; a BSB-26 implementer cannot read it. PENDING-5's helper input is therefore not
  suppliable from the run record as written.
- **Question (if a person must decide):** Should the run continue to record no Jira/source-control
  integration id and resolve them from `project_id` at launch/render (recommended, and what BSB-24
  and `ADR SK-001` §9 already describe), or should BSB-24 add an explicit recorded id, which is a
  data-model change? (Also listed under Open questions.)
- **Proposed change:**
  - **PENDING-1** — replace `stories.md:111-113` with: "The run is not asked to choose a Jira
    integration: a project has at most one, and BSB-26 resolves it from the run's project id when it
    launches the run container and builds `BB_MCP_CONFIG` from that row's `integrations.mcp` value.
    This epic records the definition only."
  - **PENDING-2** — apply the same wording to source control at `stories.md:220-222`: "…resolves it
    from the run's project id…".
  - **PENDING-5** — change the helper input at `stories.md:522-524` to "the text or document to
    redact, the project id and the run's `model_profile_id` (when set)"; the helper resolves the
    project's single Jira and single source-control integrations by project id and the selected
    model profile by id. Change the scenario's given at `stories.md:488` to "run 11 in project 7,
    which has Jira integration 3". Do not assert a run field that does not exist.
  - **Cross-epic note:** no BSB-24 or BSB-26 change is required; their text is the reference. With
    this wording, BSB-26-PENDING-2's "secret references" are derivable from the project id and need
    not be stored on the run.

### Finding 2 — Cross-epic result path: BSB-23 redacts a "run result document" that BSB-26 says the builder never writes
- **Severity:** Blocking
- **Stories touched:** BSB-23-PENDING-5; cross-epic BSB-26-PENDING-1, BSB-26-PENDING-3.
- **Evidence:**
  - `stories.md:488-490` (PENDING-5): "a run result document for run 11 whose command environment
    records the variable `JIRA_API_TOKEN` with the value … When the builder's result writer writes
    the document to prefix `runs/11/` in the builder's run bucket through the shared redaction
    helper … Then the stored document contains `[REDACTED]`…".
  - `stories.md:520-521`: "The run result writer and the run report are built by BSB-26 and BSB-33";
    `stories.md:528-529`: "BSB-26 calls the helper before persisting the run result document".
  - `docs/product/epics/BSB-26/_epic/stories.md:276-278`: "The result document is the agent image's
    `runs/21/bb_step_result.json` (ADR SK-001 sections 5 and 6); the builder reads it and never
    rewrites it." Its acceptance criteria (`:230`, `:235`, `:240`, `:245`) have the agent container
    upload `bb_step_result.json`; the builder only reads it. BSB-26's Notes name BSB-23-PENDING-5
    for the integrations and secret references (`:101`) and say no secret value is written
    (`:113-114`), but define no result writer and no `BB_MCP_CONFIG`.
  - `docs/adr/SK-001-skill-builder.md:256-260` — `runs/<run-id>/` holds the bundle,
    `bb_step_result.json`, logs and transcript; §4 (`:200-204`) requires credentials to be injected
    into the container and never logged or written to disk. No builder-side persist step for the
    result document exists.
- **What is missing/ambiguous/contradictory:** BSB-23's scenario requires the builder to write the
  run result document through the helper and asserts the **stored** document is redacted. BSB-26
  states the agent writes that object and the builder never rewrites it. The two stories cannot both
  be implemented: there is no builder "result writer" to call the helper. A credential in an
  agent-uploaded object cannot be scrubbed at write time by a builder that does not write it; the
  helper can only redact text the builder renders or returns. This also makes PENDING-5's NFR-004
  run-result leg unimplementable as written, even though the rest of the redaction contract is
  sound.
- **Question (if a person must decide):** Does NFR-004's "run results" require the agent-uploaded
  object itself to be scrubbed in storage — which needs a new builder read/scan/rewrite path not in
  `ADR SK-001` — or does it require only that credential values never appear in what the builder
  displays or returns (render-time redaction, with the agent's stored document read unchanged)?
  (Recommended: render-time; §4 already forbids the value being written by the stepkit.)
- **Proposed change:**
  - **PENDING-5** — replace the scenario's When/Then at `stories.md:489-490` with: "When the run
    report renders the agent's `runs/11/` result document through the shared redaction helper Then
    the rendered report contains `[REDACTED]` in place of the value, no builder-written record or
    log contains the value, and the agent's stored document is read unchanged (BSB-26-PENDING-3)."
  - **PENDING-5 Notes** — delete "The run result writer and the run report are built by BSB-26 and
    BSB-33; this story owns the shared redaction helper they call, and its run-result scenario
    exercises that writer against a persisted result fixture" (`:520-522`) and "BSB-26 calls the
    helper before persisting the run result document" (`:528-529`). Replace with: "BSB-26 reads the
    agent's result document and calls the helper whenever it renders or returns any part of it; the
    builder never rewrites the stored object. The helper is a render-time filter over
    builder-controlled output, and `ADR SK-001` §4's injection rule remains the primary reason the
    value is never written."
  - **Do not** add a builder result writer to BSB-23; if the answer to the question is "scrub in
    storage", that is an architecture change (see **Architecture impact**), not a story wording fix.

### Finding 3 — Dependency-note sanity (cross-epic): `BB_MCP_CONFIG` has a named builder in BSB-23 but no consumer story in BSB-25/BSB-26
- **Severity:** Advisory
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-2; cross-epic BSB-25-PENDING-3,
  BSB-26-PENDING-1.
- **Evidence:** BSB-23-PENDING-1 (`stories.md:111-113`) and BSB-23-PENDING-2 (`:220-222`) say BSB-26
  builds `BB_MCP_CONFIG` from the row's `integrations.mcp` value. `BSB-26/_epic/stories.md` never
  mentions `BB_MCP_CONFIG` or MCP outside the boilerplate note at `:38`; its launch-env scenario
  (`:62-79`) lists the bundle URL/hash, run branch, `BB_CONTEXT` and model env only. `BSB-25`'s
  PENDING-3 only presigns the bundle and passes `BB_SKILL_URL`/`BB_SKILL_SHA256`. `ADR SK-001` §2a
  defines `BB_MCP_CONFIG` from the selected MCP servers, and `epics.md:485-486` makes "available to
  a run" part of the BSB-23 DoD.
- **What is missing/ambiguous/contradictory:** BSB-23's half of the contract is now stated (and
  Finding 1 fixes how the integration is resolved), but the consumer epic's own Notes and acceptance
  criteria are silent. A developer building BSB-26 from its stories would launch the container
  without `BB_MCP_CONFIG`, so the Jira/github MCP definitions recorded here would never reach a run
  and no test would fail. The gap is one-sided in the direction of the consumer, not a defect in
  BSB-23's wording.
- **Proposed change:** no BSB-23 story change beyond Finding 1. Cross-epic follow-up for
  `sdlc-plan-stories-write` on BSB-26: PENDING-1's launch-env scenario and Notes must build
  `BB_MCP_CONFIG` from the project's Jira and source-control `integrations.mcp` values (where each
  exists), and its Out of scope must not leave the env var unowned. BSB-25-PENDING-3 should not be
  widened to own it. Record this as a still-open cross-epic follow-up, not a blocking BSB-23 change.

### Finding 4 — Dependency-note sanity (cross-epic): the shared redaction rule is claimed for BSB-26/BSB-33 but neither story names it
- **Severity:** Advisory
- **Stories touched:** BSB-23-PENDING-5; cross-epic BSB-26-PENDING-2, BSB-33-PENDING-1.
- **Evidence:** BSB-23-PENDING-5 says BSB-26 calls the helper before persisting (Finding 2 changes
  this to render-time) and "BSB-33 renders only stored, already-redacted content and calls the same
  helper with the same inputs" (`stories.md:528-531`). BSB-26-PENDING-2 defines its own rule instead:
  "The builder knows the run's injected values from its secret references and replaces any
  occurrence in the rendered progress or log with `[REDACTED]`" (`BSB-26/_epic/stories.md:209-211`).
  BSB-26-PENDING-3 and BSB-33-PENDING-1 never mention the helper; BSB-33-PENDING-1's only related
  assertion is that the body contains no credential value (`BSB-33/_epic/stories.md:73`).
- **What is missing/ambiguous/contradictory:** same outcome, two implementations. BSB-26's live-view
  redaction and BSB-33's report rendering can drift from BSB-23-PENDING-5's helper (different
  replacement token, different surfaces, one resolving from project integrations and the other from
  "the run's secret references"). Neither consumer's Notes name the shared rule, so a later change
  to the helper would not reach them. Safe to build as written only because both happen to assert
  the same `[REDACTED]` outcome; the dependency is not durable.
- **Proposed change:** no blocking BSB-23 change. Cross-epic follow-up: BSB-26-PENDING-2's Notes and
  BSB-33-PENDING-1's Notes should name BSB-23-PENDING-5 as the single redaction rule and its
  `[REDACTED]` token, and BSB-26 should say how it resolves the project's Jira/github secrets and
  the run's model profile (Finding 1's derivation) rather than "the run's secret references". If the
  consumer epics will not be revised, BSB-23-PENDING-5 should state the requirement as an output
  contract ("every builder surface renders `[REDACTED]`") and stop claiming callers it cannot bind.

## Open questions

1. **Finding 1:** Should the run record no Jira/source-control integration id and resolve them from
   `project_id` (recommended — matches BSB-24-PENDING-1 and `ADR SK-001` §9), or should BSB-24 add
   an explicit id, which changes the `runs` data model?
2. **Finding 2:** Does NFR-004 require the agent-uploaded `bb_step_result.json` to be scrubbed in
   storage (needs a builder read/scan/rewrite path; architecture amend), or only that the builder
   never displays/returns a credential value (render-time redaction, agent object read unchanged)?
   Recommended: the latter.

## Proposed changes

`docs/product/epics/BSB-23/_epic/stories.md`:
- **PENDING-1** — Notes `:111-113`: replace "BSB-24 records the selected Jira integration id in the
  run request" with "the run is not asked to choose a Jira integration; a project has at most one
  and BSB-26 resolves it from the run's project id".
- **PENDING-2** — Notes `:220-222`: same change for source control.
- **PENDING-5** — helper input `:522-524`: project id plus `runs.model_profile_id` (when set), not
  "the run's selected integration ids"; scenario `:488` given: project 7's Jira integration 3, not a
  run-selected id; scenario `:489-490` and Notes `:520-529`: redact at render time, assert the agent's
  stored document is read unchanged, and remove the builder "result writer"/"before persisting"
  wording.
- **PENDING-3, PENDING-4, PENDING-6** — unchanged; no contradiction found.
- Cross-epic follow-ups (not applied by this epic's revise pass): BSB-26-PENDING-1 `BB_MCP_CONFIG`
  and BSB-26/-33's naming of the shared redaction rule (Findings 3 and 4).

## Architecture impact

None for the proposed changes. Both Blocking findings are contradictions between BSB-23's story text
and contracts that already exist (BSB-24's run request, BSB-26's result handling, `ADR SK-001` §4/§6)
and are closable by rewording BSB-23; no new entity, column, endpoint or component is proposed.

One open-question branch would be an architecture conflict: if Finding 2 is answered "scrub the
agent-uploaded object in storage", closing it needs a builder-side read/scan/rewrite path that
`ADR SK-001` does not define, and `sdlc-arch-design` (amend) must be invoked rather than a story
change. The recommended render-time direction needs no architecture change. Finding 3's
`BB_MCP_CONFIG` work is a legitimate cross-epic deliverable already named in `ADR SK-001` §2a, not
an architecture gap.

## Requirement coverage check

The twelve IDs mapped in `epic-map.json` are all still exercised by at least one acceptance criterion:

- **PENDING-1** — FR-029 (site URL plus project key or template project; create and form scenarios)
  and FR-128 (the MCP definition is stored non-secret, and a definition containing a credential is
  rejected). **PENDING-2** — FR-030 (repository plus base branch), FR-129 (github MCP definition),
  FR-035 (shared-platform-repository warning, including the inventory-unavailable path).
- **PENDING-3** — FR-031 (vendor, base URL, high/medium/low mapping; duplicate-name 409).
- **PENDING-4** — FR-033 (verification per provider) and FR-034 (`verified_at` stamping/clearing).
- **PENDING-5** — FR-032 (no credential in any builder record), FR-036 (no credential in the
  interface), NFR-004 (logs and run results). The NFR-004 run-result leg is the subject of Finding 2:
  as written it asserts a stored-document rewrite that no story owns, so the coverage is claimed but
  not soundly exercised until the scenario is reworded to the rendered report.
- **PENDING-6** — NFR-006 (test-purpose confirmation on every create/edit and the run-purpose
  filter/exclusion).

No requirement is claimed twice with contradicting slices: FR-032/FR-036 split records vs
interface; FR-033/FR-034 split verification vs last-verified stamping; FR-029/FR-128 and
FR-030/FR-129 split configuration vs MCP definition. FR-028 (owner-only changes) is asserted by
BSB-23's routes but is owned by BSB-22-PENDING-4's guard, so its absence from BSB-23's traceability
list is correct. FR-128/FR-129's "exposes to a run" clause is recorded here but only delivered by
BSB-26; that is Finding 3, not a missing BSB-23 mapping. PRD wording for all twelve IDs still
matches `epic-map.json`; no traceability drift from PRD edits was found.

## Dependency-note sanity check

- Every in-epic reference resolves to a real story: PENDING-1 to PENDING-6 all exist, and the
  out-of-scope cross-references among PENDING-1 through PENDING-6 are reciprocal.
- **BSB-22-PENDING-4** — BSB-23-PENDING-1 depends on its settings page and guard, and BSB-22's Notes
  now state that BSB-23 calls the guard on `POST /projects/7/integrations`. Reconciled.
- **BSB-24-PENDING-1** — BSB-23 asserts BSB-24 records selected Jira/github integration ids;
  BSB-24 says the run inherits the project's Jira integration, lists no such request field, and
  `ADR SK-001` §9 has no such column. Contradictory and one-sided — Finding 1.
- **BSB-26-PENDING-1/-3** — BSB-23 names BSB-26 as the `BB_MCP_CONFIG` builder and as calling the
  redaction helper "before persisting" the result document; BSB-26 never mentions `BB_MCP_CONFIG`
  and says the builder reads the agent's `bb_step_result.json` and never rewrites it. One-sided —
  Findings 2 and 3.
- **BSB-33-PENDING-1** — BSB-23 says BSB-33 calls the same helper; BSB-33 never names it and only
  asserts the rendered body has no credential value. One-sided — Finding 4.
- **BSB-25-PENDING-3** — no BSB-23 dependency is claimed on it, and it owns only the bundle/output
  branch writer; no conflict.
- No dependency note points at a non-existent story key. Build order was not computed here; that is
  `sdlc-plan-epic-sequence`'s job.
