# Epic Review — BSB-38: Accessibility conformance

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-38-PENDING-1, BSB-38-PENDING-2, BSB-38-PENDING-3, BSB-38-PENDING-4, BSB-38-PENDING-5, BSB-38-PENDING-6, BSB-38-PENDING-7

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-38/_epic/epic-review.md`.

## Context loaded

- All seven BSB-38 stories from `stories.md` — the full set, not a sample — including the
  thirteen-row audited surface set AS-1 to AS-13, the scope decisions and the epic-level notes.
- `story-map.json` for BSB-38 and the BSB-38 entry in `epic-map.json` (FR-130 through FR-137,
  NFR-012; FA-17; MVP).
- `PRD.md`: FA-17, FR-130 through FR-137, NFR-012, and the sibling requirements the audited
  surfaces exercise — FR-001/003/004 (authoring gate), FR-020/021 (build page), FR-050/052/056
  (turn/spend caps and re-run), FR-070 (four readiness checks), FR-074/075 (re-verification and
  flipped checks), FR-159/160 (retention and purge). Section 8 records that `SkillBuilder-2` is
  the PRD work-item umbrella, not a Jira issue.
- `docs/product/epics.md`: the BSB-38 section, plus BSB-27 (Run guardrails, deadlines & re-runs)
  and BSB-30 (Readiness checks & re-verification), whose controls and fields render on BSB-38's
  audited surfaces.
- `docs/adr/SK-001-skill-builder.md` §1b (the four readiness checks), §4 (projects and
  integrations), §5 (run inputs, turn and spend caps), §6 (results and re-run), §6b (scans), §9
  (data model: `builds`, `integrations`, `runs`).
- Sibling story sets compared against BSB-38's fixtures: BSB-18, BSB-19, BSB-20, BSB-22, BSB-23,
  BSB-24, BSB-25, BSB-26, BSB-31, BSB-32, BSB-33, BSB-34, BSB-36 and BSB-37.
- BSB-21, BSB-27, BSB-29 and BSB-30 have no `_epic/stories.md` or story folder yet (the fan-out
  has not reached them); their requirements in `PRD.md` / `docs/product/epics.md` are the only
  contract available.
- No `docs/architecture.md`, `docs/data-model.md`, `docs/api-contracts/` or
  `docs/ui-conventions.md` exists in this repo; the design context is the ADR plus the PRD and
  epic decomposition. `.github/workflows/ci.yml` exists and has no `accessibility` job yet.
- Jira: `SkillBuilder-2` cannot be fetched (HTTP 404); BSB-38 was read read-only from the
  configured site, and its summary and covered requirements match `epics.md` and `epic-map.json`.

## Findings

### Finding 1 — Cross-epic status vocabulary: credential verification
- **Severity:** Blocking
- **Stories touched:** BSB-38-PENDING-2, BSB-38-PENDING-5, BSB-38-PENDING-7 (through AS-8),
  BSB-23-PENDING-4.
- **Evidence:** The audited surface AS-8 says `GET /projects/7/settings` renders "Source control
  integration 4" `Verified` and "AI model profile Default" `Verified`. BSB-38-PENDING-2's
  "Scan, build and credential statuses" scenario requires each integration's role `status`
  element to have description `"Not verified"` or `"Verified"`; PENDING-5's status-pair scenario
  measures AS-8's `"Verified"` and `"Not verified"`; PENDING-2's visible-label set includes
  `"Verified"`. BSB-23-PENDING-4, which owns the settings page, renders `"Not verified"` when
  `verified_at` is NULL and `"Last verified: 2026-11-16T11:05:00Z"` after a successful verify —
  no BSB-23 scenario renders a bare `"Verified"` value.
- **What is missing/ambiguous/contradictory:** The same credential state has two different
  values in the same shared fixture. BSB-38 asserts an accessible description and a visible text
  label that the owning story never renders, so an implementation that satisfies BSB-23 fails
  BSB-38-PENDING-2/5, and an implementation that adds `"Verified"` silently changes BSB-23's
  rendered page. FR-135 requires the visible text label to carry the state, so this is not only
  an accessible-name concern.
- **Question (if a person must decide):** Is the canonical credential status `"Verified"` /
  `"Not verified"`, or BSB-23's `"Last verified: <timestamp>"` / `"Not verified"`? If the short
  word is wanted, does BSB-23's settings page render it alongside the timestamp?
- **Proposed change:** Same change for BSB-38-PENDING-2, BSB-38-PENDING-5 and the AS-8 row of the
  audited surface set: use BSB-23's vocabulary — description/value `"Not verified"` when
  `verified_at` is NULL and `"Last verified: <timestamp>"` when set — and keep the accessible
  name `"Credential status for <integration name>"`. If the product decision is the short
  `"Verified"` word, BSB-23-PENDING-4 must add it to the rendered settings page in the same
  revise pass, and BSB-38-PENDING-2/5 then assert both the word and the timestamp. Update
  PENDING-7 only through the AS-8 registry row it renders.

### Finding 2 — Cross-epic fixture contradiction: scan row 12 is two different scans
- **Severity:** Blocking
- **Stories touched:** BSB-38-PENDING-2, BSB-38-PENDING-5, BSB-38-PENDING-7 (through AS-12);
  BSB-31-PENDING-2, BSB-31-PENDING-3, BSB-32-PENDING-2, BSB-36-PENDING-2, BSB-36-PENDING-4.
- **Evidence:** BSB-38's AS-12 defines `/scans/12` as a completed static scan with verdict
  `fail` and findings `CRITICAL SS-001 SKILL.md:3` and `HIGH SS-101 scripts/run.sh:14`, owned by
  "BSB-31, BSB-32". BSB-31-PENDING-2 defines scans row 12 exactly that way and asserts only the
  findings table (no score, recommendation or coverage). BSB-32-PENDING-2 defines the full
  security check for the same build 7 as static scan 11 plus **LLM** scan 12: row 12 has
  `stage "llm"`, `verdict NULL`, model `claude-sonnet-5-5` and findings `CRITICAL LLM-001` /
  `HIGH LLM-101`; its report renders "LLM security scan" and BSB-32 states explicitly that the
  LLM report has no `"Verdict:"` line. BSB-36-PENDING-2 embeds static `/scans/11` and LLM
  `/scans/12` in the first submission's pull-request body, while BSB-36-PENDING-4 embeds static
  `/scans/13` and LLM `/scans/14` for the later-head update. BSB-31-PENDING-2 uses scan 13 for
  the `DO_NOT_INSTALL` + incomplete-coverage report and scan 14 for a running scan.
  BSB-38-PENDING-2 requires a role `status` element named `"Recommendation"` with description
  `"INSTALL"` or `"DO_NOT_INSTALL"` for every completed scan; PENDING-5 lists only
  `"Recommendation: INSTALL"`; neither definition of scan 12 supplies a recommendation value.
- **What is missing/ambiguous/contradictory:** For build 7 the same `scans` row id 12 cannot be
  both the static failing report (BSB-31) and the LLM report (BSB-32). The recommendation value
  BSB-38-PENDING-2 asserts for scan 12 is undefined, and PENDING-5 never exercises
  `DO_NOT_INSTALL` at all. Scan ids 13/14 are also allocated differently by BSB-31 (DO_NOT_INSTALL
  static / running) and BSB-36 (static pass / LLM), so any registry that renders several of these
  surfaces from one seeded database is inconsistent. LLM scans have no verdict or recommendation,
  so "every completed scan" in PENDING-2 cannot literally apply to them.
- **Question (if a person must decide):** Which scan rows are static and which are LLM, and what
  recommendation does the audited failing static scan carry? Should LLM scan reports be in the
  status set at all, given that BSB-32's report renders no verdict or recommendation?
- **Proposed change:** Same change for BSB-38-PENDING-2, BSB-38-PENDING-5, BSB-38-PENDING-7 and
  the AS-12 row of the audited surface set, plus alignment in the sibling stories that own the
  fixtures:
  - Write one canonical scan-fixture allocation into the audited surface set (for example:
    static 11 pass/`INSTALL`; LLM 12 completed/advisory; static 13 fail/`DO_NOT_INSTALL` with
    incomplete coverage; static 14 running; static 15 fail/`CRITICAL SS-001` + `HIGH SS-101`; LLM
    16 unavailable; a later-head pair at 17/18). AS-12 then names the static pass, static fail
    and running rows it audits instead of overloading `/scans/12` and `/scans/14`.
  - BSB-31-PENDING-2/3: move its static failing/fixture rows to the agreed ids (its scan 12
    content becomes the canonical static-fail row, and its scan 13/14 uses stay unique).
  - BSB-32-PENDING-2: keep scan 12 as the LLM row and state in the story that its report has no
    verdict or recommendation.
  - BSB-36-PENDING-2/4: renumber its later-head static/LLM pair to ids the other epics do not use,
    or confirm in writing that its pair is not rendered in BSB-38's registry.
  - BSB-38-PENDING-2: restrict the `"Recommendation"` status to completed `stage "static"`
    scans, and state the failing static scan's recommendation (e.g. `"INSTALL"` for the
    CRITICAL-finding case, per BSB-31-PENDING-3, or `"DO_NOT_INSTALL"` if the DO_NOT_INSTALL row
    is the one audited). PENDING-5: add the `DO_NOT_INSTALL` pair if it is meant to be exercised.
    PENDING-7: name the exact scan rows its registry renders.

### Finding 3 — Epic-wide scope boundary: audited set omits written MVP elements on its own surfaces
- **Severity:** Blocking
- **Stories touched:** BSB-38-PENDING-1, BSB-38-PENDING-2, BSB-38-PENDING-5, BSB-38-PENDING-6,
  BSB-38-PENDING-7; BSB-34-PENDING-3, BSB-34-PENDING-4, BSB-36-PENDING-4, BSB-23-PENDING-4,
  BSB-22-PENDING-2.
- **Evidence:** The owning epics already render these MVP elements on audited surfaces:
  - BSB-34-PENDING-3/4: the run report renders a "Run data" status in four states — `"Run data:
    retained until …"`, `"Run data: expired on …"`, `"Run data: expiry pending: …"` and `"Run
    data: purged on … by …"` — plus `"Download agent log"` / `"Download transcript"` links and a
    `"Purge run data"` action for the project owner; the purged/expired states remove the links.
  - BSB-36-PENDING-4: the build page in the later-Ready/open-PR state offers an enabled
    `"Update catalog pull request"` control.
  - BSB-23-PENDING-4: the settings page owns the `"Verify"` control in the integrations section.
  - BSB-22-PENDING-2: the project page supports removing a member (`POST
    /projects/7/members/44/delete`), an interactive action on AS-7.
  AS-11 is owned by "BSB-26, BSB-33" only and its fixture omits the Run data section, downloads
  and purge action. AS-13 has only the Ready and submitted states and omits `"Update catalog pull
  request"`. AS-8 omits `"Verify"`. PENDING-1's focus-indicator control list names only "Sign in",
  "Create build", "Save", "Security check (static only)", "Full security check", "Start run",
  "Submit to catalog", "Open trace" and page links. PENDING-6's primary-action list names only
  the AS-1/4/5/7/8/9/11/13 subset and omits the Verify, Update, Purge, download and
  member-removal actions. PENDING-2's status list omits the Run data status entirely. PENDING-7
  renders each registry row at "its fixture state", so an element absent from the fixture is
  never audited.
- **What is missing/ambiguous/contradictory:** The epic's own boundary claims "every interactive
  control", "every status" and "every primary action" on the audited surfaces (FR-130, FR-131,
  FR-132, FR-135, FR-136, NFR-012), but the fixture set excludes MVP controls and statuses that
  the owning epics already specify on those same pages. The omissions are invisible story by
  story — each BSB-38 story is internally consistent — and only appear when the audited surface
  set is compared with BSB-34/36/23/22's rendered content. Because PENDING-7's registry is
  defined as this exact set, the CI job would pass while these elements remain unaudited.
- **Question (if a person must decide):** Are the BSB-34 run-data status/links/purge action, the
  BSB-36 `"Update catalog pull request"` control, the BSB-23 `"Verify"` control and the BSB-22
  member-removal action in the MVP audited set? If not, which are explicitly deferred and why?
- **Proposed change:** Same change for BSB-38-PENDING-1, PENDING-2, PENDING-5, PENDING-6,
  PENDING-7 and the audited surface set (BSB-34/36/23/22 stories need no change):
  - Extend AS-7 (member-removal action), AS-8 (`"Verify"` control and a verified state rendering
    `"Last verified: …"`), AS-11 (Run data retained/expired/expiry-pending/purged states, both
    download links, the `"Purge run data"` action and its post-purge absence) and AS-13 (a third
    state: later Ready with an open pull request and `"Update catalog pull request"`).
  - PENDING-1: add `"Verify"`, `"Update catalog pull request"`, `"Purge run data"`, `"Download
    agent log"`, `"Download transcript"` and the member-removal control to the focus-indicator
    control list.
  - PENDING-2: add the Run data status states and their accessible names/descriptions to the
    status scenarios, and add the new labels to the visible-text-label set (FR-135).
  - PENDING-5: add the Run data status colour pairs and the new status labels to the pair list.
  - PENDING-6: add the same controls to the primary-action list.
  - PENDING-7: extend the registry so the job renders the added fixture states, and state that a
    new control or state on an existing surface is added to the registry in the same change that
    introduces it.

### Finding 4 — Cross-epic dependency: BSB-27 and BSB-30 controls absent from the audited set
- **Severity:** Advisory
- **Stories touched:** BSB-38-PENDING-1, BSB-38-PENDING-3, BSB-38-PENDING-6, BSB-38-PENDING-7;
  BSB-27 (FR-050, FR-052, FR-056), BSB-30 (FR-074, FR-075).
- **Evidence:** BSB-27 is MVP and adds turn-cap and spend-cap fields to the run-start form
  (`epics.md` implementation guidance 1: "Add turn and spend caps to the run request with
  validation and explicit units"; ADR SK-001 §5 lists them among run inputs) and a re-run action
  for a prior run (FR-056). BSB-38's AS-9 fixture is owned by BSB-22/BSB-24, and
  BSB-38-PENDING-3's field list names "Skills branch", "Input branch", "Workflow", "Step", "Model
  tier", "Model profile", "Reviewer feedback" and "Upstream handoff" but no turn or spend cap.
  AS-11 and PENDING-6's action list have no re-run action. BSB-30 is MVP and adds re-verification
  (FR-074) and a flipped-check display (FR-075); no audited surface or fixture includes either.
  `stories.md`'s readiness note says only "BSB-21, BSB-29 and BSB-30 have no stories yet", but
  BSB-27 also has no story folder or `_epic/stories.md`.
- **What is missing/ambiguous/contradictory:** MVP fields, controls and statuses from two other
  MVP epics render on the same surfaces BSB-38 audits (run-start AS-9, run report AS-11, build
  page AS-5), but the audited set does not mention them. The file's own list of epics whose
  stories are still unwritten omits BSB-27. When those epics' stories land, the "every" clauses
  in FR-130/131/132/133/135/136 and NFR-012 become false unless the registry is extended — and
  nothing in BSB-38 says who must extend it.
- **Question (if a person must decide):** Do BSB-27's cap fields and re-run action and BSB-30's
  re-verification/flipped-check display join the audited set now (as explicit dependency rows),
  or are they explicitly deferred until those epics' stories are written?
- **Proposed change:** Same change for BSB-38-PENDING-1, PENDING-3, PENDING-6, PENDING-7 and the
  audited surface set:
  - Add the turn-cap and spend-cap fields to AS-9 and to PENDING-3's field list (with their
    labels, units and accessible descriptions), owned by BSB-27.
  - Add the re-run action to AS-11 and to PENDING-1/6's control lists, and add BSB-30's
    re-verification action and flipped-check display to whichever surface BSB-30 places them on
    (build page or run report), with that surface's fixture row.
  - Add those rows to PENDING-7's registry, or add one explicit sentence to the audited surface
    set saying these elements are deferred and must be added in the same change that writes
    BSB-27/BSB-30's stories.
  - Correct the readiness note to name BSB-27 alongside BSB-21, BSB-29 and BSB-30 as epics whose
    stories are written later.

### Finding 5 — Cross-story validation contract: PENDING-3 assumes BSB-19 returns all field errors
- **Severity:** Advisory
- **Stories touched:** BSB-38-PENDING-3, BSB-19-PENDING-1, BSB-24-PENDING-1.
- **Evidence:** BSB-38-PENDING-3's "A form with two invalid fields shows both errors" scenario
  says "When the server returns the two validation errors" and asserts a role `alert` summary
  listing both the skill-name format message and "A one-line description is required.", with
  `aria-invalid="true"` on both fields. BSB-19-PENDING-1's scenarios each submit one invalid
  value and receive one HTTP 422 message; no BSB-19 scenario defines a submit that returns both
  errors together. BSB-24's run-start 422 scenarios likewise return a single form-level message.
- **What is missing/ambiguous/contradictory:** The accessibility story depends on an error
  aggregation behaviour no owning story specifies. An implementer of BSB-19 can reasonably return
  only the first validation error, and then PENDING-3's scenario cannot pass even though the
  accessibility work is correct.
- **Question (if a person must decide):** Should the create-build handler (and the other
  multi-field forms) return every field error in one response, so the form-level alert can list
  them?
- **Proposed change:** Same change for BSB-38-PENDING-3 and BSB-19-PENDING-1 (and BSB-24-PENDING-1
  for its multi-field form): either add an explicit acceptance criterion to BSB-19 (and BSB-24)
  that one submit returns all field errors together with their field associations, or reduce
  BSB-38-PENDING-3's scenario to one field error plus the form-level alert BSB-19 already
  defines. Keep the alert-summary and `aria-invalid` assertions either way.

### Finding 6 — Cross-epic data and authorization contracts in the live projections
- **Severity:** Advisory
- **Stories touched:** BSB-38-PENDING-4, BSB-26-PENDING-2, BSB-30, BSB-34-PENDING-1,
  BSB-21, BSB-18-PENDING-1.
- **Evidence:** PENDING-4's notes say the run projection reads "BSB-26's `runs/21/progress.json`
  and the run row (state, turns, failure reason)". BSB-26's run page reads `progress.json` for
  status/turns/max_turns/last_event and stores failures in `runs.execution_error`; the run row
  has no `turns` column in BSB-26. BSB-34-PENDING-1 adds `runs.turn_count` (recorded from
  `usage.json`). The projection field `failure_reason` matches neither `execution_error` nor any
  other named run column. PENDING-4 also pins the announcement exactly as `"Build 7 is Ready at
  <sha>."` / `"Build 7 is Not ready at <sha>: Passing run is missing."`, but BSB-30 (which owns
  readiness evaluation and is still storyless) defines no reason wording; FR-070 only requires
  the four checks to be shown. Finally, PENDING-4 says the build projection applies "BSB-18's
  gate plus BSB-21's build access rule"; FR-020/021 define only what the build page shows, and no
  story defines a BSB-21 access rule (the authoring gate is FR-001/003/004 in BSB-18).
- **What is missing/ambiguous/contradictory:** The story pins column names, field names and
  authorization rules that the owning epics do not define. Two implementers could satisfy
  PENDING-4 and BSB-26/30/34 independently and disagree on the durable turn source, the failure
  field, the readiness reason text and the build-page authorization, and the live announcement
  would not match the page it announces.
- **Question (if a person must decide):** Is the durable turn count `runs.turn_count` (BSB-34) or
  a live read of `progress.json`, and what is the canonical readiness reason string and build
  access rule the announcement must mirror?
- **Proposed change:** Same change for BSB-38-PENDING-4, BSB-26-PENDING-2, BSB-30, BSB-34-PENDING-1
  and BSB-18-PENDING-1/BSB-21:
  - Rewrite PENDING-4's note to name exact sources: `runs/21/progress.json` (`status`, `turns`,
    `max_turns`, `last_event`) for live progress; `runs.state` for the run state;
    `runs.execution_error` for the failure reason; and `runs.turn_count` (BSB-34) only for the
    terminal recorded count. Rename the projection field `failure_reason` to match the source, or
    state the mapping.
  - State that the build projection's authorization is BSB-18's FR-001/003/004 gate plus the
    project-membership check BSB-22 defines for the project, and that any additional build-page
    rule must be defined by BSB-21's stories when written; do not cite FR-020/021 as an access
    rule.
  - Replace the fixed readiness reason sentence with the reason text BSB-30 renders, and pin only
    the sentence shape (or add a BSB-30 acceptance criterion/definition of that reason string in
    the same revise wave).
  - Align BSB-26-PENDING-2 and BSB-34-PENDING-1 with the chosen turn/failure fields; no field is
    added by BSB-38.

### Finding 7 — Dependency-note ownership accuracy
- **Severity:** Advisory
- **Stories touched:** BSB-38-PENDING-1, BSB-38-PENDING-2, BSB-38-PENDING-3; BSB-18-PENDING-1,
  BSB-19-PENDING-1, BSB-20-PENDING-2, BSB-25-PENDING-1, BSB-26-PENDING-1.
- **Evidence:** The AS-3 row is owned by BSB-18 and shows the builds list "with build 7 listed",
  but BSB-18-PENDING-1 explicitly puts "build creation, build records and build-list content
  (BSB-19, BSB-21)" out of scope and only defines the empty list. BSB-38-PENDING-3's notes say it
  wires forms "that BSB-19 (create, clone and edit build) ... already own", but BSB-20 owns the
  clone and edit modes at `/builds/new?mode=clone` and `?mode=edit`. BSB-38-PENDING-2's notes say
  "The run vocabulary is BSB-26's (`requested`, `preparing`, `prepared`, `preparation_failed`,
  `running`, `completed`, `failed`)"; BSB-25 defines the first four and BSB-26 adds only
  `running`, `completed` and `failed`.
- **What is missing/ambiguous/contradictory:** The notes point the implementer at the wrong
  sibling for three surfaces. An implementer following AS-3's owner would look in BSB-18 for a
  populated builds list it does not build; following PENDING-3's note would look in BSB-19 for
  clone/edit forms BSB-20 owns; following PENDING-2's note would miss BSB-25 as the source of the
  preparation states. These are documentation accuracy gaps, not behaviour conflicts, because the
  requirements still exist — but they will send the revise/implementation pass to the wrong
  place.
- **Question (if a person must decide):** Should AS-3's ownership be split between the empty
  state (BSB-18) and the populated state (BSB-19/BSB-21), and should the other notes name the
  owning epic precisely?
- **Proposed change:** Same change for BSB-38-PENDING-1, PENDING-2, PENDING-3 and the audited
  surface set: mark AS-3's empty state BSB-18 and its "build 7 listed" state BSB-19/BSB-21 (or
  move the populated state to a separate row owned by BSB-21); in PENDING-3's notes, attribute
  create to BSB-19 and clone/edit to BSB-20; in PENDING-2's notes, attribute `requested`,
  `preparing`, `prepared` and `preparation_failed` to BSB-25 and `running`, `completed` and
  `failed` to BSB-26.

## Open questions

1. **Credential status wording (Finding 1):** Is the canonical status `"Verified"` /
   `"Not verified"`, or BSB-23's `"Last verified: <timestamp>"` / `"Not verified"`? If the short
   word is wanted, does BSB-23 render it too?
2. **Scan fixture allocation (Finding 2):** Which scan rows are static and which are LLM, and
   what recommendation does the audited failing static scan carry? Should LLM scan reports, which
   have no verdict or recommendation, be in the status set at all?
3. **Audited-set breadth for written MVP surfaces (Finding 3):** Are the BSB-34 run-data
   status/links/purge action, the BSB-36 `"Update catalog pull request"` control, the BSB-23
   `"Verify"` control and the BSB-22 member-removal action in the MVP audited set? If not, which
   are explicitly deferred?
4. **Audited-set breadth for unwritten MVP epics (Finding 4):** Do BSB-27's turn/spend caps and
   re-run action and BSB-30's re-verification/flipped-check display join the registry now, or are
   they explicitly deferred until those stories are written?
5. **Multi-field error aggregation (Finding 5):** Must the create-build (and other multi-field)
   handlers return all field errors in one response?

## Proposed changes

`stories.md` — audited surface set and epic-level notes:
- AS-3: split the empty state (BSB-18) from the populated state (BSB-19/BSB-21).
- AS-7: add the member-removal action from BSB-22.
- AS-8: add the `"Verify"` control and a verified state rendering `"Last verified: <timestamp>"`;
  align the credential status wording with BSB-23.
- AS-9: add BSB-27's turn-cap and spend-cap fields.
- AS-11: add the BSB-34 Run data states, download links and `"Purge run data"` action; add the
  BSB-27 re-run action and, if placed on the run report, BSB-30's re-verification and
  flipped-check display.
- AS-12: use a single canonical static/LLM scan allocation; name the audited static pass, static
  fail and running rows explicitly and state the failing scan's recommendation.
- AS-13: add the later-Ready/open-PR state with `"Update catalog pull request"`.
- Readiness note: name BSB-27 alongside BSB-21, BSB-29 and BSB-30 as still-unwritten epics; note
  that a new control or state on an existing surface joins the registry in the same change that
  introduces it, or state the deferral explicitly.

`BSB-38-PENDING-1`: extend the focus-indicator control list with `"Verify"`, `"Update catalog
pull request"`, `"Purge run data"`, `"Download agent log"`, `"Download transcript"`, the
member-removal control and, once BSB-27 exists, `"Re-run"`; split AS-3's ownership note.

`BSB-38-PENDING-2`: use BSB-23's credential status vocabulary; restrict `"Recommendation"` to
completed static scans; add the BSB-34 Run data status states and labels; attribute the run
vocabulary to BSB-25/BSB-26 correctly.

`BSB-38-PENDING-3`: add the turn-cap and spend-cap fields; either add BSB-19's multi-error
aggregation contract or reduce the two-error scenario; attribute create to BSB-19 and clone/edit
to BSB-20.

`BSB-38-PENDING-4`: name the exact run/progress columns and the build-page authorization rule;
replace the fixed readiness reason text with BSB-30's rendered reason (or add that reason to
BSB-30).

`BSB-38-PENDING-5`: add the Run data status colour pairs and both recommendation pairs
(`INSTALL`/`DO_NOT_INSTALL`); align the credential pair with Finding 1.

`BSB-38-PENDING-6`: add the Verify, Update, Purge, download and member-removal actions to the
primary-action list; add the cap fields' labels to the long-value/reflow surface.

`BSB-38-PENDING-7`: extend the registry and fixture states with the elements above; state the
same-change registry rule for new controls/states and the exact scan rows it renders.

Sibling stories for alignment in their own revise passes:
- `BSB-23-PENDING-4`: if `"Verified"` is chosen, render it alongside `"Last verified: <ts>"`.
- `BSB-31-PENDING-2`/`BSB-31-PENDING-3`, `BSB-32-PENDING-2`, `BSB-36-PENDING-2`/`BSB-36-PENDING-4`:
  align scan ids with the canonical allocation and state that LLM reports have no
  verdict/recommendation.
- `BSB-19-PENDING-1`, `BSB-24-PENDING-1`: add the all-field-errors contract if Finding 5's
  scenario stays.
- `BSB-26-PENDING-2`, `BSB-34-PENDING-1`, `BSB-30`: align the turn/failure field names and define
  the readiness reason text if Finding 6's pinned sentence stays.

## Architecture impact

None. Every finding is resolvable by fixture data, story wording or a scope note. The two
read-only live projections in PENDING-4 reuse data the sibling epics already define and add no
entity, field or endpoint. No design-stage change is needed for this epic.

## Requirement coverage check

`epic-map.json` assigns FR-130 through FR-137 and NFR-012 to BSB-38 (MVP, FA-17).
`story-map.json` and the stories' traceability tables map each requirement to exactly one story:
FR-130/FR-131 → PENDING-1; FR-132/FR-135 → PENDING-2; FR-133 → PENDING-3; FR-134 → PENDING-4;
FR-136 → PENDING-5; NFR-012 → PENDING-6; FR-137 → PENDING-7. No requirement is claimed twice and
none is unclaimed, and each has at least one scenario that exercises it. The PRD wording matches
the epic-map and the stories; no drift was found, and `PRD.md` §8 records the `SkillBuilder-2`
naming exception.

The coverage is real but only as wide as the audited surface fixture states: Finding 3 omits
written MVP controls and statuses on AS-7/AS-8/AS-11/AS-13, and Finding 4 omits BSB-27/BSB-30
elements on AS-9/AS-11/AS-5, so the "every" clauses in FR-130, FR-131, FR-132, FR-133, FR-135 and
FR-136 and NFR-012 are incomplete until those rows are extended. Findings 1 and 2 additionally
assert status values the owning stories do not define. After those changes, each requirement's
coverage claim is supported by the fixtures it names.

## Dependency-note sanity check

- All `BSB-38-PENDING-1` through `BSB-38-PENDING-7` keys exist in `story-map.json`; no dependency
  note points at a non-existent story key.
- Intra-epic references are reciprocal: PENDING-5 depends on PENDING-2 and PENDING-1; PENDING-2
  puts announcements in PENDING-4 and contrast in PENDING-5; PENDING-1 puts the automated check in
  PENDING-7; PENDING-4 and PENDING-6 defer to PENDING-2/1. No contradiction was found in those
  directions.
- Cross-epic references resolve to real epics with defined requirements, but BSB-21, BSB-27,
  BSB-29 and BSB-30 have no detailed stories yet. `stories.md` names BSB-21, BSB-29 and BSB-30 and
  omits BSB-27 (Finding 4).
- Ownership notes are wrong in three places: AS-3's populated state is attributed to BSB-18, the
  clone/edit forms to BSB-19, and the preparation states to BSB-26 (Finding 7). BSB-34 is not
  referenced anywhere in BSB-38 despite sharing AS-11's page, and BSB-36's later-Ready control and
  BSB-23's `"Verify"` control are absent from the audited set (Finding 3).
- PENDING-7's dependency on `.github/workflows/ci.yml` is valid: the file exists and has no
  `accessibility` job, so the story adds one. Build order itself is left to
  `sdlc-plan-epic-sequence`; this pass only records the missing and inaccurate notes.
