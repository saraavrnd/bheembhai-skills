# Revisions — BSB-28

## Pass 1 — 2026-11-16 — `epic-review.md` (cross-story gap review)

**Report applied:** `docs/product/epics/BSB-28/_epic/epic-review.md` — verdict CHANGES REQUESTED,
findings 1–11 and open questions 1–3. Target resolution: the run named "SkillBuilder", which is the
product title in `docs/product/PRD.md`, not a Jira issue. No Atlassian (Jira) MCP tool is available
in this session (only the built-in tools are offered, and `.mcp.json` declares the Atlassian
server's `args` as a string rather than an array), so the epic was resolved the way the review
resolved it: **BSB-28** — the epic the preceding `sdlc-plan-stories-write` run wrote (commit
`b505892`) and whose review requested changes (commit `1d47d0a`). Its stories' header records the
read-only Jira fetch and matches the BSB-28 section of `docs/product/epics.md` and the FR-058 to
FR-062 rows of `docs/product/PRD.md`. Nothing was written to Jira.

**Applied (findings with no open question):**

- **Finding 2 (blocking) — cross-story contradiction: alias-mapping and finalizer ownership.**
  - Shared contract, **Seeding lifecycle** and **Alias replacement**: the `run_jira` row with
    `aliases` is written as soon as phase 1 has created every issue; phase 2 then resolves the
    tokens. The rollback removes the row if a later step fails.
  - `BSB-28-PENDING-1`: Out of scope no longer gives "storing the alias mapping" to PENDING-2;
    Notes now say this story writes the `run_jira` row including `aliases` in fixture order.
  - `BSB-28-PENDING-2`: Out of scope and Notes now give the row and its `aliases` mapping to
    PENDING-1; this story owns only phase-2 replacement and alias validation.
  - `BSB-28-PENDING-3`: owns the finalizer hook (capture first, then cleanup). Removed the
    scenario *The state is captured before the issues are cleaned up* and the `DELETE` /
    `cleaned_at` assertions from *An issue deleted during the run is recorded as missing* and *A
    failed read leaves the state unrecorded*. Its acceptance criteria now assert only the capture
    reads, `state_after`, the capture-failure log line and the unchanged `runs.state`.
  - `BSB-28-PENDING-4`: gained *Cleanup runs after the post-run state is captured* and *Cleanup
    runs after a failed state capture*, moved from PENDING-3; *An issue that is already gone counts
    as cleaned* now states the issue was deleted during the run. Notes name PENDING-1 as the
    writer of `aliases` and keep the dependency on PENDING-3.
- **Finding 4 (advisory) — terminal-write edges during seeding and finalization.**
  - Shared contract, **Seeding lifecycle**: seeding re-checks that the run is still `running`
    before inserting `run_jira` and before creating the container; if the terminal write was lost,
    it deletes what it created and writes no state.
  - Shared contract, **Post-run state capture**: the finalizer runs after every terminal write,
    whichever writer made it, and on executor startup for terminal runs whose
    `run_jira.cleaned_at` is `NULL`.
  - `BSB-28-PENDING-1`: added scenario *A run that becomes terminal during seeding rolls the seed
    back*, and the BSB-27 deadline dependency in its Notes.
  - `BSB-28-PENDING-3`: added scenarios *A timed-out run's state is captured* (BSB-27's writer) and
    *A restarted executor finalizes a terminal run left uncleaned* (startup recovery). Notes state
    the trigger covers every writer.
  - `BSB-28-PENDING-4`: Notes reference the same trigger.
  - `BSB-28-PENDING-5`: Notes say it is the last-resort fallback when finalizer recovery also
    fails, so `state_after` may stay `NULL`.
- **Finding 5 (advisory) — `cleaned_at` semantics.**
  - Shared contract, **Cleanup**: replaced "all-or-nothing" with continue-with-the-remaining-keys,
    leave `cleaned_at` `NULL`, and log the failure. `cleaned_at` is set when, after the pass, no
    issue carrying the run's marker remains for any recorded key.
  - `BSB-28-PENDING-4`: added scenario *A deletion failure on the first key still attempts the
    rest*.
  - Shared contract, **Nightly sweep**, and `BSB-28-PENDING-5`: the sweep sets `cleaned_at` only
    when no issue carrying that run's marker remains, including when it had nothing to delete.
    Added scenario *The sweep marks a run cleaned when nothing of its own remains*.
- **Finding 6 (advisory) — sweep/finalizer race.**
  - Shared contract, **Nightly sweep**, `BSB-28-PENDING-3` Notes and `BSB-28-PENDING-4` Notes: the
    finalizer and the sweep serialise on the run's `run_jira` row lock.
  - `BSB-28-PENDING-5`: added scenario *The sweep skips a run whose finalizer is in progress*.
- **Finding 8 (advisory) — alias delimiter follows SK-001.**
  - Shared contract, **Fixture file format**, the fixture JSON block and the `POST` bodies in
    `BSB-28-PENDING-1` now use `{{alias}}` as in SK-001 §5. `BSB-28-PENDING-2`'s unknown-alias
    scenario and no-token assertion use the same form.
  - Open decision 2 (the delimiter) is closed and removed; the remaining open decisions are
    renumbered: template-project integrations is 2, re-runs is 3. References in the Notes and the
    BSB-27 cross-epic note were updated.
- **Finding 9 (advisory) — `failed_seed` outcome text.**
  - Shared contract, **Run state values**: this epic owns the run-page text exactly `The Jira
    fixture could not be seeded.` as an extension of BSB-26's outcome table; BSB-26 needs no revise
    pass.
  - `BSB-28-PENDING-1`: added scenario *A failed seed shows its outcome on the run page*.
    `BSB-28-PENDING-2` Notes reference it.
  - Cross-epic notes BSB-24/25/26 and BSB-38 updated to say this epic adds the row and text and
    that NFR-012 applies to that region.
- **Finding 10 (advisory) — the nightly trigger is owned here.**
  - Shared contract, **Nightly sweep**: this epic owns the daily `02:00` UTC trigger; BSB-37's
    suite scheduler may later reuse it.
  - `BSB-28-PENDING-5`: added scenario *The sweep is scheduled daily at 02:00 UTC*. Notes no
    longer depend on an unnamed "installation's scheduler".
- **Finding 11 (advisory) — `run_jira` under retention and purge.**
  - `BSB-28-PENDING-1` and `BSB-28-PENDING-3` Notes: the `run_jira` row and `state_after` are part
    of the run's results under NFR-013 and NFR-014 and are removed with the run by BSB-34's
    retention and purge.
  - Cross-epic notes: added the BSB-34 bullet recording the dependency.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 1 / Open question 1 (blocking).** Whether the Jira fixture is chosen per run (a
  run-start input recorded on the run, reused by re-runs) or per project (`config.fixture` on the
  `jira` integration), and which story in this epic or a named BSB-23/BSB-24 story delivers the
  way to set it. The "Fixture selection and enablement" paragraph, the Givens of all five stories,
  the cross-epic BSB-23 note and the re-run decision therefore still pin `config.fixture` as an
  explicit, unreviewed decision. The report's conditional architecture impact is still live: a
  per-run answer needs a new column in the SK-001 §9 design before it can be written here.
- **Finding 3 / Open question 2 (blocking).** Whether BSB-33's FR-140 Jira-change record is built
  from `run_jira.state_after` or captured independently, whether BSB-28's cleanup must wait for
  that capture, and whether evaluating fixture assertions against `state_after` is deliberately
  left to no epic. `BSB-28-PENDING-3`'s Out of scope still says the fixture assertions and display
  belong to BSB-33, and the contract and PENDING-3/PENDING-4 Notes still place the finalizer only
  relative to BSB-29's verification, not BSB-33's capture.
- **Finding 7 / Open question 3 (advisory).** Whether BSB-23 must refuse a `site_url` or
  `project_key` change while a seeded run is uncleaned, or whether each seeded run must record the
  site and project it seeded into. The template-project `failed_seed` scenario, the changed-prefix
  404 rule, the sweep's `project_key` guard and the changed-integration Out of scope were not
  written. A "record the site and project per run" answer is the report's other conditional
  architecture impact: `run_jira` has no such columns in SK-001 §9.

**Coverage:** unchanged. All five requirements mapped to BSB-28 (FR-058 to FR-062) are still
covered by the same five stories, and no story claims a requirement outside the epic.
`story-map.json` is unchanged: no story key, summary or requirement mapping changed.

**Note for the next review (not a finding of this pass):** applying Finding 2's move and Finding
5's new scenario takes `BSB-28-PENDING-4` to nine acceptance scenarios, and `BSB-28-PENDING-5` to
eight, above the skill's ~7-scenario size signal. A split along the capture-boundary /
cleanup-surface seam (PENDING-4) and the scheduled-job / recovery seam (PENDING-5) is worth
considering once the open questions are answered; it was not done here because the report names no
such split. The new fixture-file token form `{{alias}}` follows SK-001 §5; the optional fixture
`key` field remains as the report left it for `sdlc-plan-story-review`.

## Pass 2 — 2026-11-16 — verifier re-check of the Pass 1 revision

**Why this pass ran.** The automated verifier rejected the Pass 1 attempt without re-reviewing the
content: `no_template_residue` (`builtin:md_no_placeholders`) reported five unfilled placeholder
matches in `stories.md`, and `story_map` was rejected because it had not changed while reviewer
feedback was active. Both were addressed here; no review finding was re-opened and no requirement
mapping changed.

**Placeholder check — the alias token notation.** The five matches were the literal double-brace
alias token that Finding 8 introduced to follow SK-001 §5, not unfilled template fields. The token
form is still required by the contract, so only the way it is written in the reviewable criterion
text changed:
- The **Fixture file format** paragraph now defines the form in words and names it the
  **double-brace alias token**; the later prose uses that name instead of spelling the braces.
- `BSB-28-PENDING-1`'s two `POST` body criteria keep the exact body but write the unresolved token
  as the equivalent JSON unicode escape sequences for `{` and `}`, with a clause saying they
  decode to the raw fixture text. A test compares the parsed JSON, so the assertion is unchanged.
- `BSB-28-PENDING-2`'s no-token assertion and its unknown-alias Given use the same wording; the
  unknown-alias Given now spells out the description's text without the literal braces.
- The fixture-file JSON block above the contract still shows the literal token form, because that
  block is the fixture file's exact content.

**`story-map.json` — summaries aligned to the reviewed scopes.** Finding 2 moved alias validation
to PENDING-2, made PENDING-3 own the finalizer, and made PENDING-4 clean up after capture. The
story summaries (in `stories.md` and `story-map.json`) now say so:
- PENDING-2: "Resolve fixture alias tokens to the created keys and reject an invalid fixture".
- PENDING-3: "Capture the seeded issues' post-run Jira state when any terminal write ends the run".
- PENDING-4: "Clean up a run's seeded Jira issues after the post-run state is captured".

`story_key` and `requirement_ids` are unchanged; coverage is still FR-058 → PENDING-1, FR-059 →
PENDING-2, FR-060 → PENDING-3, FR-061 → PENDING-4, FR-062 → PENDING-5.

**Still open:** Findings 1/Open question 1, 3/Open question 2 and 7/Open question 3 remain
unapplied for the reasons recorded under Pass 1 — the run hand-off still carries no gate answers.
