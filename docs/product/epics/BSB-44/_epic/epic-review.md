# Epic Review — BSB-44: Integrations & credentials

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-17 · **Stories reviewed:** BSB-44-PENDING-1, BSB-44-PENDING-2, BSB-44-PENDING-3, BSB-44-PENDING-4, BSB-44-PENDING-5, BSB-44-PENDING-6, BSB-44-PENDING-7

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-44/_epic/epic-review.md`.

## Context loaded

- **Target work item `SkillBuilder-2` — unavailable.** A read-only Atlassian REST fetch of
  `https://saraavrnd.atlassian.net/rest/api/3/issue/SkillBuilder-2` returns HTTP 404 ("Issue does
  not exist or you do not have permission to see it"); the site's project list contains BEEM, BSB,
  EX, GRAP and LNPRTL and no `SkillBuilder` project, and a site-wide JQL text search returns no
  issue. This matches `docs/product/PRD.md` §8, `docs/product/epics.md` and the input note in this
  epic's `_epic/stories.md`. The Atlassian MCP server configured in `.mcp.json` was not exposed as a
  tool in this session, so the read-only Jira REST API was used. The work item contributes no scope
  here.
- **Epic under review:** `BSB-44` "Integrations & credentials" (Jira `BSB-44`, fetched read-only;
  status To Do; labels FA-5 and MVP; zero issue links, subtasks and comments; description, functional
  scope, edge cases, non-goals, implementation guidance, Definition of Done, covered requirements and
  notes match `_epic/stories.md` and `docs/product/epics.md:500–577`). BSB-44 is the epic whose
  stories were written by the immediately preceding `sdlc-plan-stories-write` run (commit
  `3f77409`), and the only written epic without an `epic-review.md`.
- **Stories:** all 7 in the epic, from `_epic/stories.md` and `_epic/story-map.json` — the full
  set, not a sample. Story keys are the `BSB-44-PENDING-*` placeholders until `sdlc-tracker-sync`
  publishes them; `story-map.json`'s summaries and requirement mappings match `stories.md`.
- **PRD:** `docs/product/PRD.md` §4 scope, §5 FA-5, §6 FR-029–FR-036 and FR-128–FR-129 (the twelve
  requirements `epic-map.json` assigns to BSB-44), §7 NFR-004 and NFR-006, and §8 "Secrets",
  "Test data", "MCP definitions", "Access model" and "External prerequisites".
- **Design input:** there is no `docs/architecture.md`, `docs/data-model.md`,
  `docs/api-contracts/` or `docs/ui-conventions.md` in this repo; the committed design reference is
  `docs/adr/SK-001-skill-builder.md`. Read §3 (the `skill-builders` group claim checked on every
  request; the builder's `users` table keyed by Cognito `sub`; no platform-database access — the
  gate FA-1 / BSB-39 supplies), §4 (the three integrations and their settings; credentials in AWS
  Secrets Manager under `skill-builder/<project-id>/<integration>` with only the reference in the
  builder database; test-only tokens and the source-control overlap warning; members run tests,
  only the owner changes integrations; MCP definitions are non-secret settings), §2a (`BB_MODEL`
  from the tier/vendor/base URL and `BB_MCP_CONFIG` from the selected MCP servers), §6 (run data in
  `s3://<skill-builder-bucket>/runs/<run-id>/`, including `bb_step_result.json`, logs and the
  transcript), and §9 (`integrations` = `id`, `project_id`, `kind`, `config` JSONB, `secret_ref`,
  `mcp` JSONB, `verified_at`; plus `users`, `projects`, `project_members`, `runs`). Platform
  ADR-013 §1, which SK-001 §4 cites for the tier vocabulary, is not in this repository; Story 3
  treats `fast`/`standard`/`deep` as this epic's fixture vocabulary and the mapping shape as the
  contract.
- **Sibling epics checked:** BSB-43's `stories.md` (the integration write route, owner guard,
  `(project_id, kind)` identity, settings container and membership read rule), BSB-39's
  `stories.md` (fixture accounts and the request-time gate), BSB-41/BSB-42 (no integration surface),
  and the `epic-map.json` entries for BSB-45 (FA-6 run setup), BSB-46/BSB-47 (scans), BSB-48 (FA-7
  run execution), BSB-52 (FA-13 retention), BSB-54 (FA-15 submission) and BSB-57 (FA-9, Later).
  No `epic-sequence.md`/`.json` exists, so relative build order cannot be confirmed in this pass —
  that remains `sdlc-plan-epic-sequence`'s job.

## Findings

### Finding 1 — Requirement coverage / epic boundary: NFR-006 is claimed, but only a warning is built and no epic owns enforcement

- **Severity:** Blocking
- **Stories touched:** BSB-44-PENDING-5 (primary), BSB-44-PENDING-1, -2 and -3 (the three
  credential-accepting stories, which add no test-purpose gate); cross-epic FA-6 / BSB-45.
- **Evidence:**
  - `stories.md:3–5` and `:198` map NFR-006 to BSB-44 and to Story 5; `:456` lists NFR-006 under
    Story 5's covered requirements.
  - `stories.md:152–156` — for kinds `jira` and `ai_model`, `platform_overlap` is `null` and
    `test_purpose` is `null`: there is no test-purpose signal for two of the three credential types.
  - `stories.md:459` — Story 5's Out of scope explicitly excludes "Refusing, blocking or gating a
    save or a run on an overlap" and "assessing the test purpose of Jira or model credentials
    beyond the `null` read-model value".
  - `stories.md:462` — "A warning never blocks a save; FA-6 (BSB-45) may consume `test_purpose`
    when preparing a run but does not change this contract."
  - `docs/product/epics.md:530` and `:575` — the epic's functional scope and covered requirements
    say "Ensure runs use only test-purpose Jira, source-control and model credentials (NFR-006)",
    while the Definition of Done at `:556–560` only requires "an overlapping source-control
    repository produces a warning".
  - `docs/product/epic-map.json:45` assigns NFR-006 to BSB-44 only; BSB-45's `requirement_ids` do
    not include it, so no other epic owns enforcement.
  - `docs/product/PRD.md:259` is NFR-006; `:353` ("Test data") says the credentials used for runs
    are test-purpose and that a source-control overlap "triggers a warning", which is the narrower
    reading Story 5 implements.
- **What is missing/ambiguous/contradictory:** The epic's own scope says "ensure runs use only
  test-purpose ... credentials", but the only story mapped to NFR-006 builds a non-blocking warning
  and returns `null` for Jira and model credentials. No story and no named epic enforces the
  requirement, and BSB-45's traceability does not carry NFR-006. A developer building BSB-44 and a
  developer building FA-6 can each assume the other enforces it, and the epic will still report
  NFR-006 as covered. The PRD's §8 "Test data" paragraph supports a warning-only reading, but the
  epic's scope and the coverage table claim more; a person must choose which one is authoritative.
- **Question (if a person must decide):** Does NFR-006 require the builder to refuse a run whose
  source-control `test_purpose` is `false` (and what should `unknown` do), in which case FA-6 /
  BSB-45 must carry NFR-006 and Story 5 must record that dependency — or is the PRD §8 "Test data"
  assumption the intended reading, making FR-035's warning the builder's only behaviour and
  NFR-006 an externally assured property? (Also listed under Open questions.)
- **Proposed change:**
  - **If enforcement is intended:** Story 5's Notes/dependencies must say FA-6 (BSB-45) must refuse
    a run when `test_purpose` is `false` and state the rule for `unknown`; the epic preface's
    "Scope boundary with later epics" must add NFR-006 to BSB-45's obligations; and the BSB-44
    coverage summary/`epic-map.json` traceability should mark NFR-006 as jointly owned (BSB-44
    supplies the signal, BSB-45 enforces it). BSB-45's planning pass must add NFR-006 to its
    `requirement_ids`. Stories 1–3 need no behaviour change beyond supplying the read model.
  - **If warning-only is intended:** restate `docs/product/epics.md:530` and the coverage summary so
    NFR-006 is not claimed as enforced by BSB-44; say in the preface that the test-purpose property
    is an external prerequisite (PRD §8) and FR-035's warning is the builder's only behaviour.
    Story 5's Notes already say this, but its "covered requirements" line and the epic scope must
    not overclaim. No story AC change; Story 5's Out of scope stays as written.
  - Either way, Story 5's Out of scope must match the chosen option and its Notes must name the
    owner of any enforcement.

### Finding 2 — Redaction contract: the epic-wide redaction set excludes the credential submitted in the current request, which Story 6 requires to be redacted

- **Severity:** Blocking
- **Stories touched:** BSB-44-PENDING-6 (primary), BSB-44-PENDING-1, -2, -3, -7 (every story whose
  write request carries a `credential` and is logged); BSB-44-PENDING-4 (verification error bodies).
- **Evidence:**
  - `stories.md:167–170` — "Every log record, HTTP error body and stored run artifact passes
    through a redaction layer that replaces each credential value known to the project (the current
    values read through the project's `secret_ref`s) with the literal `[REDACTED]` before the
    record is written."
  - `stories.md:21–24` — a body with `credential` writes the value to the secret store and sets
    `secret_ref`; `stories.md:96–99` — a validation failure "changes no row and writes no secret".
  - `stories.md:485–488` — Story 6's "Builder logs redact the submitted credential value" saves a
    **new** Jira credential and requires every captured `stderr` line to contain no
    `ATATT-secret-leak-probe`, and the `integration_write` line to carry `credential`
    `[REDACTED]`.
  - `stories.md:490–493` — Story 6's "An upstream error that echoes the credential is redacted":
    the fixture secret store refuses the write and returns `AccessDeniedException: value
    ATATT-secret-leak-probe is not permitted`, and the builder must answer HTTP 503 while every
    `stderr` line contains `[REDACTED]` and no `ATATT-secret-leak-probe`.
- **What is missing/ambiguous/contradictory:** On a first write the `secret_ref` exists only after
  the secret store accepts the value; on the upstream-error and validation-failure paths it is
  never set. The submitted value is therefore outside the contract's stated redaction set ("the
  current values read through the project's `secret_ref`s"), yet Story 6 requires exactly that value
  to be redacted. An implementer following the preface literally leaks the credential in the
  `integration_write` line and in the upstream-error log — the two scenarios Story 6 exists to
  prevent — violating NFR-004 and `stories.md:514`.
- **Question (if a person must decide):** None; this is a contract correction.
- **Proposed change:** Extend the redaction contract to add every credential value present in the
  current request (the `credential` body field, and any value the builder attempts to write to the
  secret store) to the redaction set for the lifetime of the request, before any log record or
  error body is emitted — in addition to values read through `secret_ref`. Apply the sentence to
  the preface, Story 6's Notes, and Stories 1–4 and 7's Notes (all emit request logs or error
  bodies). Story 6's two existing scenarios then match the contract; optionally add a rejected
  first-write case to Story 6. No AC change is required in Stories 1–4 and 7.

### Finding 3 — `verified_at` after a credential or configuration change is undefined across the write and verification stories

- **Severity:** Blocking
- **Stories touched:** BSB-44-PENDING-1, -2, -3 and -7 (writes), BSB-44-PENDING-4
  (verification and the timestamp's meaning).
- **Evidence:**
  - `stories.md:85–99` — the write contract returns `verified_at` and says a second PUT updates
    the existing row, but never says what a successful write does to `verified_at` when `config` or
    the stored credential changes.
  - `stories.md:223–225` — Story 1 asserts `verified_at` is `null` on a newly created row.
  - `stories.md:378–381` — Story 4 sets `verified_at` on a successful verification; `:393–396` a
    refused verification keeps the previous value; `:421` — "a failed, refused or timed-out
    verification never clears it".
  - `stories.md:527–530` — Story 7 updates an existing Jira row (with a `credential` and an `mcp`
    object) and asserts nothing about `verified_at`.
  - `stories.md:303–306` — Story 2 only proves that saving a **different** kind leaves the Jira
    row's `verified_at` unchanged.
- **What is missing/ambiguous/contradictory:** No rule says whether a successful save that changes
  the Jira site/project, the GitHub repository/base branch, the model base URL, or the credential
  itself resets `verified_at` to NULL. Preserving it lets the settings page show "Last verified:
  2026-11-16" for a credential replaced on 2026-11-17; resetting it shows "Never verified" after
  an unrelated config edit even when the credential is unchanged. Two implementers can choose
  differently, and FR-034's "when an integration's credentials were last verified" is ambiguous
  for the current row.
- **Question (if a person must decide):** Does changing `config` or writing a new credential reset
  `verified_at` to NULL (with an unchanged save preserving it), or is `verified_at` a historical
  "last successful verification ever" that survives changes? If it resets, does every config change
  count or only the fields the verification probe uses (Jira `site_url`; GitHub repository/base
  branch; model `base_url`/vendor)? (Also listed under Open questions.)
- **Proposed change:** Add one rule to the epic's write contract and apply it consistently in
  Stories 1, 2, 3, 4 and 7. Example: "A successful write that changes the stored credential or any
  config field the verification probe uses sets `verified_at` to NULL; a write that changes neither
  preserves it." Add an AC to Story 1/2/3 (or a scenario in Story 4) for re-saving after a
  verification, and a sentence in Story 4's Notes that the timestamp describes the current
  config + credential. If the historical reading is chosen instead, state it in the same contract
  and make the settings-page text (`Last verified: …`) unambiguous.

### Finding 4 — Optional `mcp` on an update: absent means "preserve" or "clear" is not stated

- **Severity:** Advisory
- **Stories touched:** BSB-44-PENDING-1, -2, -3 (config-only saves), BSB-44-PENDING-7 (the stored
  MCP definition).
- **Evidence:**
  - `stories.md:19–24` — the write route "adds two optional body fields: `credential` ... and
    `mcp`"; "A body without `credential` leaves the row's `secret_ref` unchanged" — there is no
    corresponding rule for `mcp`.
  - `stories.md:87` — "`credential` and `mcp` are optional"; `:92–95` — the response `mcp` is "the
    stored object or `null`" and a second PUT updates the existing row.
  - `stories.md:225`, `:281`, `:331` — Stories 1–3 omit `mcp` and assert `mcp` `null` only on
    **creation**; `stories.md:529–530` and `:534–535` — Story 7 records a non-null `mcp`.
- **What is missing/ambiguous/contradictory:** If an owner later saves the Jira config or a new
  credential with a body that omits `mcp`, does the MCP definition recorded by Story 7 survive? A
  partial-update implementation preserves it; a full-replacement implementation silently drops it.
  The credential rule explicitly preserves `secret_ref`, which makes the silence for `mcp`
  conspicuous. No story exercises a successful update that omits `mcp` after a definition exists,
  so the two readings cannot be distinguished from the ACs.
- **Question (if a person must decide):** None if the preserve rule is chosen; if clearing must be
  supported, the explicit clear form is a contract decision.
- **Proposed change:** State in the write contract: "An absent `mcp` leaves the stored `mcp`
  unchanged (as an absent `credential` leaves `secret_ref` unchanged); send `\"mcp\": null` to clear
  a definition." Add one AC (Story 7 or Story 1) that a config + credential save without `mcp`
  preserves a previously stored MCP definition, and the same sentence to Stories 1–3 and 7's
  Notes. If clearing is not supported, say so explicitly instead of leaving it undefined.

### Finding 5 — Stories 2 and 5 each name the other as the dependency for the same overlap read model

- **Severity:** Advisory
- **Stories touched:** BSB-44-PENDING-2, BSB-44-PENDING-5.
- **Evidence:**
  - `stories.md:315` — Story 2: "The `platform_overlap` values in this story come from the contract
    BSB-44-PENDING-5 owns; this story asserts them only so a source-control save has a complete
    response."
  - `stories.md:462` — Story 5: "Depends on BSB-44-PENDING-2 for the source-control integration..."
  - `stories.md:434–437` — Story 5's first scenario saves the GitHub integration through Story 2's
    write route and asserts the overlap warning.
  - `stories.md:142–165` — the overlap/read-model contract itself lives in the epic preface, not in
    a single story.
- **What is missing/ambiguous/contradictory:** Each story treats the other as the owner or
  prerequisite of the `platform_overlap`/`test_purpose` read model while both change the same write
  route. `sdlc-plan-epic-sequence` will see a cycle (Story 2 needs Story 5's contract; Story 5 needs
  Story 2's route) unless the split is written down. This is a dependency-note gap, not an order
  computation.
- **Question (if a person must decide):** None; the reviewer can propose the split.
- **Proposed change:** Assign the split explicitly. Preferred: Story 2 implements the inventory
  read and the `platform_overlap`/`platform_overlap_projects`/`test_purpose` read model for a
  GitHub save (its ACs already need `none`/`true`), and Story 5 adds the `warning`/`unknown` cases
  and the settings-page warning; then Story 5's dependency on Story 2 is one-sided and Story 2 no
  longer depends on Story 5. Alternative: make Story 5 the owner of the read model and have Story 2
  depend on Story 5 for it, while Story 5 does not depend on Story 2 beyond the row/route. Update
  both Notes sections and the preface's ownership sentence; do not compute a build order here.

### Finding 6 — Fixture set drifts from BSB-39/BSB-43: Dana's display name, the "no others" project list, and the missing Erin fixture

- **Severity:** Advisory
- **Stories touched:** the epic preface (all seven stories); no story behaviour changes.
- **Evidence:**
  - `stories.md:27–34` — "**Fixture accounts.** The Cognito fixture is BSB-39's:" lists
    `dana@example.test | sub-13579 | Dana Owner | ["skill-builders"] | U_dana` at `:34`.
  - `docs/product/epics/BSB-39/_epic/stories.md:16` — Dana (`sub-13579`) has *(no `name` claim)*;
    `docs/product/epics/BSB-43/_epic/stories.md:22` repeats the same.
  - `stories.md:41–50` — "The fixture builder database contains these `projects` and
    `project_members` rows and no others", listing only `prj_H5mQ2rT8vX` and `prj_K9pL3wN6zB`;
    `stories.md:38` says Bob and Casey have no row "for either fixture project".
  - `docs/product/epics/BSB-43/_epic/stories.md:23` and `:40` — the shared fixture also contains
    Erin (`sub-11111`, `[]`, `U_erin`) and `prj_M2vQ8kT4xD` (owner `U_erin`).
  - BSB-44's scenarios use Alice, Bob and Casey only; Dana and Erin are not used (Dana appears
    only in the fixture rows `stories.md:34` and `:48`).
- **What is missing/ambiguous/contradictory:** BSB-44 claims BSB-39's fixture but changes Dana's
  display name and asserts a database with no Erin project, contradicting the shared fixture that
  BSB-43 extends. A test setup that takes "and no others" literally would omit
  `prj_M2vQ8kT4xD` and break BSB-43's fixture; the unused Dana row and her project add noise and
  an unneeded cross-epic mismatch.
- **Question (if a person must decide):** None; this is a fixture-definition correction.
- **Proposed change:** State that BSB-44 uses a subset of the shared BSB-39 + BSB-43 fixture: keep
  Alice, Bob and Casey (remove Dana, or if she is kept, match BSB-39's no-name claim), and say the
  database also contains BSB-43's `prj_M2vQ8kT4xD`/Erin rows even though no BSB-44 scenario uses
  them. Replace "and no others" with "in addition to BSB-43's rows, these are the rows BSB-44's
  scenarios rely on." No story AC change.

### Finding 7 — `config` accepts and stores credential-looking keys while `mcp` rejects them

- **Severity:** Advisory
- **Stories touched:** BSB-44-PENDING-1, -2, -3 (write validation), BSB-44-PENDING-6 (the
  never-store guarantee).
- **Evidence:**
  - `stories.md:55–69` — each kind's `config` is validated for its documented keys
    (`site_url`/`project_key`/`template_project`; `repository`/`base_branch`;
    `vendor`/`base_url`/`tier_models`), but no rule rejects additional keys.
  - `stories.md:101–106` — `mcp` rejects "any object key matching
    `(?i)token|api[_-]?key|secret|password|credential` whose value is a non-empty string, at any
    depth" with HTTP 422 — the same store, same risk, stricter rule.
  - `stories.md:223–225` — Story 1 stores `config` exactly as submitted in the `integrations` row
    and returns it in the response.
  - `stories.md:480–483` — Story 6 asserts no credential value is stored in any table and that no
    table has a column named `credential`, `credential_value`, `token`, `api_key` or
    `secret_value`; a nested `config` key is not a column, so this assertion does not catch it.
  - `docs/product/PRD.md:109` (FR-032) and `:113` (FR-036).
- **What is missing/ambiguous/contradictory:** An owner can submit
  `{"config":{"site_url":"…","project_key":"TEST","api_token":"ATATT-…"}}`; Stories 1–3 accept it
  (there is no unknown-key or credential-key rule for `config`), store it in `config` JSONB and
  return it, while Story 6 promises no credential value is ever stored or displayed. The redaction
  layer also knows only values from `secret_ref`s (see Finding 2), so this value is not scrubbed.
  The `mcp` rule shows the intended defence but is scoped only to `mcp`.
- **Question (if a person must decide):** None if the documented-key-only rule is chosen.
- **Proposed change:** Apply the same credential-key scan to `config` at any depth (with a clear
  error name), or state that `config` rejects unknown keys and list the exact allowed key set per
  kind so a credential-looking extra key is a 422. Add the rule to the epic preface and Stories
  1–3's Notes; optionally extend Story 6's DB-scan scenario with a credential-looking key inside
  `config`.

## Open questions

1. **NFR-006 enforcement vs warning-only (Finding 1).** Does the builder have to refuse a run when
   the source-control `test_purpose` is `false` — and what should `unknown` do — with FA-6 / BSB-45
   carrying NFR-006 and Story 5 recording that dependency? Or is the PRD §8 "Test data" assumption
   the intended reading, so FR-035's non-blocking warning is the builder's only behaviour and
   NFR-006 is externally assured? This decides whether the epic's "ensure" scope and coverage claim
   change, and whether BSB-45's traceability gains NFR-006.
2. **`verified_at` after a change (Finding 3).** Does a successful save that changes the stored
   credential or a probe-relevant config field reset `verified_at` to NULL (and an unchanged save
   preserve it), or is the timestamp a historical "last successful verification ever"? If it
   resets, which config fields count per kind?

## Proposed changes

Per touched story, for `sdlc-plan-stories-write` (revise mode). All changes are proposed, not
applied.

- **`_epic/stories.md` (preface):** apply the answers to Open questions 1 and 2; extend the
  redaction contract to include the credential submitted in the current request (Finding 2); state
  the absent-`mcp` preserve/clear rule (Finding 4); correct the fixture subset against BSB-39 and
  BSB-43 (Finding 6); add the `config` credential-looking-key/unknown-key rule (Finding 7); and
  make the Story 2/Story 5 ownership split explicit (Finding 5). If Open question 1 chooses
  enforcement, add NFR-006 to the "Scope boundary with later epics" paragraph and to Story 5's
  Notes; if it chooses warning-only, restate the NFR-006 coverage sentence and do not claim
  enforcement.
- **BSB-44-PENDING-1:** add the Finding 2 sentence to Notes (request-time credential redaction);
  the Finding 3 `verified_at` rule to the write contract and one AC/Notes line; the Finding 4
  absent-`mcp` sentence to Notes; and the Finding 7 `config` rule to the validation scenarios.
  No behaviour change for Finding 1.
- **BSB-44-PENDING-2:** same Finding 2, 3, 4 and 7 changes as Story 1. For Finding 5, if the
  preferred split is chosen, keep the inventory read and the `none`/`true` read model here and add
  a Notes sentence that Story 5 owns only the `warning`/`unknown` cases and the settings surface;
  drop the claim that the values "come from" Story 5's contract.
- **BSB-44-PENDING-3:** same Finding 2, 3, 4 and 7 changes as Story 1 (its `config` includes the
  model profile and `tier_models`). No Finding 5 change.
- **BSB-44-PENDING-4:** add the Finding 3 sentence and AC for the post-verification save, and the
  Finding 2 sentence that verification error bodies are redacted under the extended set. No
  Finding 1/4/5/6/7 behaviour change.
- **BSB-44-PENDING-5:** apply the answer to Open question 1 to the covered-requirement line, Out of
  scope and Notes (Finding 1); apply the Finding 5 ownership split; keep the warning/unknown
  scenarios otherwise unchanged. No Finding 2/3/4/6/7 behaviour change.
- **BSB-44-PENDING-6:** rewrite the Notes' restatement of the redaction contract to match Finding 2,
  and optionally extend the DB-scan scenario to a credential-looking key inside `config`
  (Finding 7). Its existing submitted-value and upstream-error scenarios remain the proof for
  Finding 2.
- **BSB-44-PENDING-7:** add the Finding 4 AC and Notes sentence that a config/credential save
  without `mcp` preserves a stored definition; add the Finding 3 `verified_at` rule to the
  post-update scenario; add the Finding 7 `config` rule to Notes. No Finding 1/5/6 change.
- **`_epic/story-map.json`:** no summary or requirement-mapping change in BSB-44. NFR-006 stays
  mapped to Story 5 as the signal. If Open question 1 chooses enforcement, the cross-epic
  traceability change belongs to BSB-45's planning pass (`epic-map.json` adding NFR-006 to
  BSB-45), not to this file.

## Architecture impact

None. The epic uses only the SK-001 §9 entities and fields (`integrations.id`, `project_id`,
`kind`, `config`, `secret_ref`, `mcp`, `verified_at`) and computes `credential_set`,
`platform_overlap`, `platform_overlap_projects` and `test_purpose`; the secret store, repository
inventory and external endpoints are PRD §8 external prerequisites. The one missing design
reference is platform ADR-013 §1's tier vocabulary: `stories.md:71–74` and `:365` scope
`fast`/`standard`/`deep` to this epic's fixture vocabulary and make the mapping shape the
contract, so no `sdlc-arch-design` amendment is required unless the platform tier names must be
pinned. Findings 1–7 are story/contract changes or a product decision, not architecture conflicts.

## Requirement coverage check

All twelve requirements assigned to BSB-44 are exercised by at least one acceptance criterion; no
requirement is duplicated with a contradictory definition, and no requirement-wording drift was
found. NFR-006 is only partially enforceable — see Finding 1.

| Requirement | Story | Exercising acceptance criteria |
|---|---|---|
| FR-029 | BSB-44-PENDING-1 | Jira save with a project key and with a template project; both/neither rejected; non-HTTPS `site_url` rejected; non-owner refused; secret-store failure changes no row |
| FR-030 | BSB-44-PENDING-2 | GitHub save with a repository/base branch; config-only save leaves `secret_ref` null; malformed repository and blank base branch rejected; non-owner refused; Jira row untouched |
| FR-031 | BSB-44-PENDING-3 | Model profile save with vendor/base URL/`tier_models`; missing tier, empty mapping, non-HTTPS base URL and missing vendor rejected; non-owner refused |
| FR-032 | BSB-44-PENDING-1, BSB-44-PENDING-6 | Story 1: no column of the created row contains the credential; Story 6: every text/JSONB column and every table is scanned, and no credential column exists. Distinct slices, no contradiction; the `config` path is the gap in Finding 7 |
| FR-033 | BSB-44-PENDING-4 | Jira, GitHub and model verification probes read the stored credential and set `verified_at`; non-owner, missing credential, failure and timeout paths |
| FR-034 | BSB-44-PENDING-4 | Successful verification records `verified_at`; failure, refused and timeout keep the previous value; the `verified_at` invalidation rule is Finding 3 |
| FR-035 | BSB-44-PENDING-5 | Overlap warning without blocking; no warning when absent; inventory unavailable degrades to `unknown`; Jira/model carry no overlap signal |
| FR-036 | BSB-44-PENDING-6 | Integration API and settings page return no credential value and no `credential`/`token`/`api_key`/`secret_value` key; non-member is refused |
| FR-128 | BSB-44-PENDING-7 | Jira MCP definition stored in `integrations.mcp`, returned by the read API and shown on the settings page; malformed and credential-bearing definitions rejected |
| FR-129 | BSB-44-PENDING-7 | GitHub MCP definition stored, returned and shown; non-owner refused |
| NFR-004 | BSB-44-PENDING-6 | `stderr` JSON lines, HTTP error bodies and stored run artifacts redacted; the submitted-value/upstream-error gap is Finding 2 |
| NFR-006 | BSB-44-PENDING-5 | **Partial** — only the source-control overlap signal; Jira/model are `null` and no run is gated. See Finding 1 and Open question 1 |

Notes:
- **FR-032** is claimed by Stories 1 and 6 in genuinely distinct slices (the write path's row
  versus the DB/log/artifact-wide guarantee); they do not redefine a status, error or threshold.
  Finding 7 shows the `config` path is not covered by the never-store rule.
- **NFR-004** is exercised by Story 6 and restated at the epic level in the preface; the redaction
  set itself is Finding 2.
- **NFR-006** is the only requirement whose coverage is not fully realisable from the story set;
  Finding 1 asks whether that is intentional (PRD §8) or an enforcement hole.
- No requirement-wording drift: FR-029–FR-036, FR-128–FR-129 and NFR-004/NFR-006 match
  `PRD.md:106–113`, `:205–206`, `:257–259`; `epic-map.json:45` matches the Jira epic's covered
  requirements and `story-map.json`.
- No NFR other than NFR-004 and NFR-006 is mapped to BSB-44. The authoring gate (NFR-002/NFR-003)
  belongs to BSB-39 and is inherited at the epic preface (`stories.md:13–17`).

## Dependency-note sanity check

Mostly correct; two observations need attention (Findings 1 and 5). Mismatches and notes:

- **Within the epic — reciprocal and correct:** Story 1's Notes say it establishes the `credential`
  extension reused by Stories 2, 3, 6 and 7; each of those names Story 1. Story 4 names Stories
  1–3 and is named in their Out of scope. Story 6 names Stories 1–4, and Story 4's Out of scope
  names Story 6 for redaction. Story 7 names Stories 1–3, and Story 1's Notes names Story 7 as a
  reuser.
- **Story 2 ↔ Story 5:** each names the other as the owner/prerequisite of the overlap read model —
  see Finding 5. This is the only within-epic dependency cycle; the contract itself is in the
  preface, so the split is a wording fix, not a missing capability.
- **Cross-epic keys all exist:** Stories 1–3, 5 and 7 name BSB-43 for the project/owner guard/
  settings container; BSB-43-PENDING-5's Notes reciprocate. Story 1 names FA-9 (BSB-57, Later) for
  `template_project` consumption and FA-6 (BSB-45) for run preparation; Story 2 names FA-2 (BSB-40/
  BSB-41) and FA-15 (BSB-54); Story 3 names FA-6 (BSB-45) and FA-12 (BSB-47); Story 4 names FA-6
  only as a possible surfacer; Story 5 names FA-6 (BSB-45); Story 6 names FA-7 (BSB-48) and FA-13
  (BSB-52); Story 7 names FA-6 (BSB-45). All keys exist in `epic-map.json`; no dependency note
  names a nonexistent story or epic.
- **BSB-45 / BSB-46 / BSB-47 / BSB-48 / BSB-52 / BSB-54 / BSB-57 have no stories yet**, so
  reciprocity cannot be checked. The dependencies are recorded on the depending side, which is the
  expected direction. If Open question 1 chooses enforcement, BSB-45's planning pass must carry
  NFR-006 and the run-gate rule; `epic-map.json` currently does not.
- **BSB-39 does not name BSB-44**, but the gate dependency is BSB-44's dependence on FA-1's
  request-time check, which BSB-39-PENDING-4 defines; no change is required in this epic.
- **BSB-57 is Later**; Story 1's `template_project` value is stored now and consumed when FA-9 is
  planned. That is a legitimate Later-release split, not a hole.
- No `epic-sequence.md`/`.json` exists yet, so sequencing position cannot be checked here; build
  order itself is `sdlc-plan-epic-sequence`'s job. Finding 5 must be resolved before that step can
  avoid a cycle.
