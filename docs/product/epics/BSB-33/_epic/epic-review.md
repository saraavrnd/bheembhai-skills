# Epic Review — BSB-33: Run report & change evidence

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-33-PENDING-1, BSB-33-PENDING-2, BSB-33-PENDING-3, BSB-33-PENDING-4, BSB-33-PENDING-5

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-33/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item
  umbrella rather than a Jira issue. A read-only `GET /rest/api/3/issue/SkillBuilder-2` returned
  HTTP 404 ("Issue does not exist or you do not have permission to see it."); `SkillBuilder` is
  not a visible project key (the visible projects are BEEM, BSB, EX, GRAP and LNPRTL), and a
  site-wide search returns no such issue. This matches `PRD.md` §8. The Atlassian MCP tools were
  not exposed in this session, so the configured site (`https://saraavrnd.atlassian.net`) was
  queried read-only through its REST API (GET only; no Jira writes).
- **The epic this run reviews is BSB-33.** The branch HEAD (`de95dd9`) is the
  `sdlc-plan-stories-write` step that wrote `BSB-33/_epic/stories.md` and `story-map.json`;
  `config/sdlc-wf-planning-epic.yaml` runs `sdlc-plan-epic-review` immediately after that step
  for the same epic. Jira `GET /rest/api/3/issue/BSB-33` returned HTTP 200: Epic "Run report &
  change evidence", status To Do; `epics.md` records labels FA-13/MVP and the same description.
  BSB-33 has no prior `epic-review.md` and no `revisions.md`, so this is the first review pass.
- **All 5 stories in BSB-33**, from `stories.md` and `story-map.json` in one read each:
  BSB-33-PENDING-1 through BSB-33-PENDING-5 (the full set, not a sample). `story-map.json` maps
  the same 13 requirement IDs as `stories.md`'s coverage table, and every requirement maps to at
  least one acceptance criterion.
- **`PRD.md`** — §2 target users (including the catalog reviewer, who "does not use the authoring
  interface"), §5 FA-13, §6 the thirteen FR rows FR-094 to FR-103, FR-140, FR-157 and FR-158,
  §7 NFR-002/NFR-003/NFR-004/NFR-012, §8's source note, and §9's prior-review decisions. No NFR
  is mapped to BSB-33 by `epic-map.json`; NFR-004 is mapped to BSB-23 and NFR-012 to BSB-38.
- **`epics.md`** — the BSB-33 section (description, functional scope, implementation guidance,
  DoD, covered requirements, Notes) and the sections of the epics that supply or consume it:
  BSB-18 (session and authoring gate), BSB-22 (test projects, membership and the shared check),
  BSB-23 (Jira/source-control integrations and the redaction rule), BSB-24 (run start),
  BSB-25 (packaging, run branch and baseline), BSB-26 (execution, run page and outcome),
  BSB-28 (Jira fixture seeding and `run_jira`), BSB-29 (verification and verdicts),
  BSB-30 (readiness), BSB-31/BSB-32 (static and LLM scans and the Security tab),
  BSB-34 (usage, turn count, trace and retention), BSB-35 (history, Later), BSB-36 (catalog
  submission links), BSB-37 (CLI) and BSB-38 (accessibility, cross-cutting).
- **`docs/adr/SK-001-skill-builder.md`** — §4/§5 (test project, run branch and baseline), §6
  (run-page content, the "Security tab on the skill and run pages" sentence, the external trace
  store and the `s3://…/runs/<run-id>/` layout), and §9 (the data model, whose `runs` table lists
  no `build_id`, `baseline_sha`, `result_status`, `turn_count`, `trace_id` or `diff_error`, and
  whose `run_jira` table lists `run_id`, `aliases`, `state_after` and `cleaned_at` but not
  `state_before`, `changes` or `capture_error`).
- **Other story sets checked:** BSB-18 (3 stories), BSB-22 (4), BSB-23 (6), BSB-24 (4), BSB-25
  (3), BSB-26 (4), BSB-31 (7) and BSB-32 (4) have stories on disk and were read for the
  cross-epic hand-offs this epic depends on. BSB-29, BSB-30, BSB-34, BSB-28, BSB-36, BSB-37 and
  BSB-38 have epic definitions but no stories yet; their epic scope and Notes were read to
  distinguish a legitimate forward dependency from an unowned capability.
- **Prior reviews read:** BSB-22's review Finding 1 / Open question 1 (catalog-PR report access),
  BSB-23's review Finding 6 (the redaction helper's contract with BSB-26 and BSB-33), BSB-31's
  review Finding 5 (reviewer-facing scan report) and BSB-32's review Findings 2, 6 and 7 / Open
  question 2 (combined Security tab and reviewer view). These already record parts of Findings 1,
  2 and 3 below from the other epic's side; this review records the BSB-33 side and the exact
  contradiction.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md`
  are not committed; ADR SK-001 is the design authority this pass can use. No
  `epic-sequence.md`/`.json` exists for BSB-33; no build order is computed here.

## Findings

### Finding 1 — Cross-epic scope ownership: the run page's Security tab and the reviewer-facing scan report are assigned to BSB-33 by two sibling stories while BSB-33's own out-of-scope disclaims them

- **Severity:** Blocking
- **Stories touched:** BSB-33-PENDING-1. Cross-epic: BSB-26-PENDING-2, BSB-31-PENDING-5,
  BSB-32 (four stories).
- **Evidence:**
  - BSB-33-PENDING-1, Out of scope: "the security tab and scan reports (BSB-31 and BSB-32)"
    (`stories.md:101-102`).
  - BSB-26-PENDING-2, Out of scope: "the Security tab and scan reports (BSB-31, BSB-32 and
    **BSB-33**)" (`BSB-26/_epic/stories.md:186-187`).
  - BSB-31-PENDING-5, Out of scope: "the LLM scan report, which model ran it and the combined
    security tab (**BSB-32**)" (`BSB-31/_epic/stories.md:339-342`); Notes: "The reviewer-facing
    stable report view and its access rule belong to **BSB-33/BSB-36** … The HTML route and the
    report model are shared with the run page's Security tab (**BSB-26/BSB-33** link the run's
    scan); this story owns the scan-only page, not the run page layout"
    (`BSB-31/_epic/stories.md:352-362`).
  - BSB-32's four stories (`BSB-32-PENDING-1` to `-4`) own the LLM scan, its report at
    `GET /scans/{id}` and the build-page control, but none owns the combined Security tab; BSB-32's
    own review records this as Finding 2 (Blocking) and Open question 2, and Finding 7 records
    that no BSB-32/BSB-36 story owns the reviewer view.
  - ADR SK-001 §6b requires a "**Security tab** on the skill and run pages, next to the verify
    results (§6): score, recommendation, each finding with severity, rule, file and line, and
    which model ran the LLM check" (`SK-001:308-310`).
  - BSB-33's epic functional scope and DoD list no Security tab and no scan-report viewer
    (`epics.md:1047-1089`).
- **What is missing/ambiguous/contradictory:** Three sibling stories name three different owners
  for the same run-page capability. BSB-33 says BSB-31/BSB-32 own it, BSB-26-PENDING-2 includes
  BSB-33 among the owners, BSB-31-PENDING-5 gives the combined tab to BSB-32, and BSB-32's stories
  own neither the combined tab nor a reviewer-facing view. The ADR-required tab therefore has no
  owner, and BSB-33's out-of-scope is a positive claim that contradicts two of its siblings. A
  developer building the BSB-33 run page would omit the tab (or build a second, competing one),
  and the reviewer-facing scan report that BSB-31 hands to BSB-33/BSB-36 has no view.
- **Question (if a person must decide):** Does BSB-33 own the combined Security tab on the run
  page and the reviewer-facing stable scan-report view (which would add a story or acceptance
  criteria to BSB-33), or do BSB-32 and BSB-36 own them (in which case BSB-33-PENDING-1's
  out-of-scope must name the actual owner consistently with BSB-26-PENDING-2 and
  BSB-31-PENDING-5)? If BSB-33 owns the tab, which BSB-31/BSB-32 records does it compose, and is
  the LLM scan shown as advisory evidence per FR-085? (also Open question 1)
- **Proposed change:**
  - **If BSB-33 owns the tab:** add a sixth story (or extend BSB-33-PENDING-2's verdict/check
    section) with acceptance criteria for the Security tab on `GET "/projects/7/runs/21"`,
    composing BSB-31's static score/recommendation/findings with BSB-32's "Model:" line and LLM
    findings, with the advisory banner and the unavailable/failed LLM states. Add the
    reviewer-facing scan-report view and its access rule to the same story or to BSB-36's link
    contract, and add the tab and viewer to the epic's functional scope and DoD.
  - **If BSB-32/BSB-36 own them:** change BSB-33-PENDING-1's Out of scope to "the Security tab
    (BSB-32) and the scan reports and reviewer-facing scan view (BSB-31, BSB-32, BSB-36)" and add
    a Notes sentence recording the hand-off; do not leave the current "BSB-31 and BSB-32" claim
    standing.
  - **Cross-epic (not applied here):** BSB-26-PENDING-2's "BSB-31, BSB-32 and BSB-33" and
    BSB-31-PENDING-5's "BSB-32" / "BSB-33/BSB-36" must be reconciled to the same owner; BSB-32's
    Open question 2 and Finding 7 and BSB-36's functional scope must carry the same answer.

### Finding 2 — Cross-epic actor and access rule: the epic's catalog-reviewer actor and its stable reviewer-readable report have no story, while the only run-report route is gated to project members

- **Severity:** Blocking
- **Stories touched:** BSB-33-PENDING-1, BSB-33-PENDING-2, BSB-33-PENDING-3, BSB-33-PENDING-4,
  BSB-33-PENDING-5. Cross-epic: BSB-22-PENDING-1/-3, BSB-31-PENDING-5, BSB-36.
- **Evidence:**
  - All five stories' Story line names the same actor: "a **skill author who is a project
    member**" (`stories.md:66`, `stories.md:134`, `stories.md:200`, `stories.md:261`,
    `stories.md:327`). No story names a catalog reviewer or a reviewer-facing surface.
  - BSB-33-PENDING-1, "A non-member cannot read a run report": Carol, a signed-in skill author
    with no `project_members` row for Project Atlas, opens `GET "/projects/7/runs/21"` and gets
    HTTP 403 "You are not a member of this project." (`stories.md:80-83`). Its Notes then say
    access remains "the authenticated session plus the project-membership check from BSB-22;
    'without the authoring interface' … does not mean anonymous access (NFR-002 requires a valid
    session), and the separate reviewer-facing access rule is the unresolved cross-epic gap"
    (`stories.md:114-120`).
  - `stories.md`'s header records the gap: the epic's final functional-scope bullet "has no FR
    mapped to BSB-33 and is an open question in BSB-22's review (Open question 1) and BSB-31's
    review (Finding 5)"; "they deliberately do not invent a reviewer access rule"
    (`stories.md:27-33`).
  - The epic itself requires the capability: description "An author, reviewer or debugger needs
    one place that explains what a run did" (`epics.md:1051-1054`); functional scope "Present the
    report as the stable evidence target linked from catalog submission" (`epics.md:1069`);
    implementation guidance step 6 "Expose a stable report view that catalog submission can link
    to and that reviewers can read without the authoring interface" (`epics.md:1082-1083`); DoD
    "The report is the evidence target the catalog pull request links to" (`epics.md:1085-1089`).
  - `PRD.md` §2: the catalog reviewer "Consumes the catalog pull request and its linked run and
    scan reports; **does not use the authoring interface**" (`PRD.md:16`). BSB-36's only claim is
    "Link the run report and the scan reports from the pull-request description"
    (`epics.md:1284-1295`); it defines no view or access rule.
  - BSB-22's review Finding 1 (Blocking) already asks BSB-33 to "state how the stable report is
    accessed outside the authoring interface" (`BSB-22/_epic/epic-review.md:48-95`); BSB-31's
    review Finding 5 (Blocking) records the same for the scan view and hands it to BSB-33/BSB-36.
- **What is missing/ambiguous/contradictory:** The epic's third actor (the catalog reviewer) is
  absent from all five stories, and the epic's own DoD and implementation step 6 cannot be met by
  any of them. The report's only route is the member-gated authoring page, so the BSB-36 link a
  catalog reviewer receives would return HTTP 403. The review report and the stories both record
  the gap, but no story owns it and no mapped FR covers it; a developer building BSB-33 as written
  builds only the author-facing report. A person must decide the access rule (a signed read-only
  share link, a reviewer role/group, or a public view) before the story can be written.
- **Question (if a person must decide):** Do catalog reviewers read a run report outside the
  builder authoring gate and the project-membership check? If yes, what authorizes them (a signed
  read-only share link, a separate reviewer role/group, or a public view), which route renders it,
  and which epic/story owns it? If no (reviewers must be `skill-builders` members or project
  members), is `PRD.md` §2's "does not use the authoring interface" wrong, and must the epic's
  DoD and BSB-36's FR-110 link be narrowed? (also Open question 2)
- **Proposed change:**
  - **BSB-33-PENDING-1:** If the reviewer view is BSB-33's, add acceptance criteria for the stable
    reviewer route and its authorization, and state how it differs from the 403 in "A non-member
    cannot read a run report"; if it is deferred, say so explicitly and name the owner (BSB-36 or
    a later epic), and stop leaving the 403 AC as the only access statement.
  - **BSB-33-PENDING-2, BSB-33-PENDING-3, BSB-33-PENDING-4, BSB-33-PENDING-5:** add the same
    Notes sentence — these sections render inside the stable report view once the reviewer access
    rule is decided; until then they remain on the member-gated authoring page owned by
    BSB-26-PENDING-2 — and add BSB-36 to the cross-epic hand-off list. Same sentence for all five
    stories.
  - **Cross-epic (not applied here):** BSB-36 must point FR-110 at the chosen reviewer-readable
    view, not only at the member-gated URL; BSB-22-PENDING-1/-3 must scope their shared membership
    check to author-facing surfaces; BSB-31-PENDING-5 and BSB-32's review must use the same rule
    for the scan report. Resolve this together with BSB-22's Open question 1 and BSB-31's
    Finding 5.

### Finding 3 — Cross-epic NFR: BSB-23's shared credential-redaction helper is never named or exercised by BSB-33's report or its captured diff and Jira evidence

- **Severity:** Advisory
- **Stories touched:** BSB-33-PENDING-1, BSB-33-PENDING-2, BSB-33-PENDING-3, BSB-33-PENDING-4,
  BSB-33-PENDING-5. Cross-epic: BSB-23-PENDING-5.
- **Evidence:**
  - BSB-23-PENDING-5, Notes: "This story owns the single redaction rule every builder surface
    applies … The run result writer and **the run report are built by BSB-26 and BSB-33**; this
    story owns the shared redaction they call" (`BSB-23/_epic/stories.md:408-415`). Its
    "A run result redacts the credential" scenario asserts the stored run result document and the
    rendered run report contain "[REDACTED]" and not the value
    (`BSB-23/_epic/stories.md:384-387`). It covers FR-032, FR-036 and NFR-004.
  - BSB-23's review Finding 6 (Advisory) records the cross-epic follow-up in terms: "BSB-26's and
    **BSB-33's stories must name the BSB-23 redaction helper and pass it the resolved values**"
    (`BSB-23/_epic/epic-review.md:305-341`).
  - No BSB-33 story names BSB-23-PENDING-5, "redact" or "[REDACTED]". The only related assertion
    is BSB-33-PENDING-1's "the body contains no exception text, stack trace or credential value"
    (`stories.md:73`), with no injected-credential fixture. BSB-33-PENDING-2 renders recorded
    verification messages, PENDING-3 captures `runs/<run-id>/diff.json` (including file patches),
    PENDING-4 captures `run_jira` before/after snapshots and change values, and PENDING-5 renders
    a trace URL — none states a redaction path. NFR-004 says credential values are never written
    to logs, results or the interface; the report and its captured evidence are exactly such
    surfaces.
- **What is missing/ambiguous/contradictory:** The redaction dependency is claimed only on
  BSB-23's side. A BSB-33 implementer reading only this epic can render the diff, Jira snapshots
  and verification messages verbatim, and capture unredacted objects, so BSB-23-PENDING-5's
  report AC cannot pass and NFR-004 is not proven for the report. The helper's input (the run
  project's resolved credential values) is also unstated on the BSB-33 side, so the report has no
  way to know what to redact.
- **Question (if a person must decide):** How does the report obtain the resolved credential
  values and call BSB-23-PENDING-5's helper — at capture time for `runs/<id>/diff.json` and the
  `run_jira` snapshots, at render time, or both — and must the persisted captured objects be
  redacted before storage or only when rendered? (also Open question 3)
- **Proposed change:**
  - **BSB-33-PENDING-1, BSB-33-PENDING-2, BSB-33-PENDING-3, BSB-33-PENDING-4, BSB-33-PENDING-5:**
    add the same Notes sentence — "The report calls BSB-23-PENDING-5's shared redaction with the
    run project's resolved credential values; no credential value is stored or rendered" — and add
    BSB-23-PENDING-5 to the dependency Notes. Same sentence for all five stories.
  - **BSB-33-PENDING-3:** add an acceptance criterion that a credential value present in a changed
    file's patch appears as "[REDACTED]" in `runs/<id>/diff.json` and on the page, and that the
    value is not in the stored object.
  - **BSB-33-PENDING-4:** add an acceptance criterion that a credential value present in a Jira
    issue field appears as "[REDACTED]" in `run_jira.state_before/state_after/changes` and on the
    page, and that the value is not stored.
  - **Cross-epic (not applied here):** BSB-23-PENDING-5's review Finding 6 asks BSB-23 to define
    the helper's input contract; BSB-33 consumes that contract as above.

### Finding 4 — Cross-epic record contract: the `llm.scan` L2 check in PENDING-2 is not defined by BSB-29 (which owns `runs.verification`) and overlaps BSB-32's advisory LLM security scan

- **Severity:** Advisory
- **Stories touched:** BSB-33-PENDING-2. Cross-epic: BSB-29, BSB-32-PENDING-2/-4.
- **Evidence:**
  - BSB-33-PENDING-2, "An upheld claim shows both verdicts and every check result": the
    `runs.verification` fixture contains `{"id": "llm.scan", "level": "L2", "status": "pass",
    "message": "No instruction injection found."}` and the page renders "llm.scan (L2): PASS — No
    instruction injection found." (`stories.md:139-141`).
  - BSB-33-PENDING-2, Notes: the read contract is `verdict`, `overturned` and `checks[]` with
    `id`, `level` ("L0", "L1" or "L2" when enabled), `status` and `message`; "BSB-29 must persist
    that shape; this story renders every entry in array order, including any L2 entry present when
    L2 scanning is enabled, and does not infer a verdict" (`stories.md:176-181`).
  - BSB-29's epic owns `runs.final_verdict` and `runs.verification`. Its functional scope says
    "Persist the check-level results and the component versions that produced them, for
    readiness, the run report and re-verification" (`epics.md:947-948`), but it names no check
    levels, no `llm.scan` entry and no L2 record; its covered requirements are FR-063 to FR-067,
    FR-153, FR-164 and NFR-010 (`epics.md:959-967`).
  - BSB-32 owns the LLM security scan as a separate `scans` record, and its epic defines the
    evidence as "additional, non-gating evidence" and the requirement FR-085 as "The LLM scan
    never blocks a run" (`epics.md:595-598, 640`, `PRD.md:190`). BSB-32's review Finding 2/6 says the
    LLM finding must be allowed to appear as advisory evidence and must not enter the run's
    claimed verdict, final verdict or verification result (`BSB-32/_epic/epic-review.md:124-171`,
    `313-348`).
  - ADR SK-001 §6 says the run page shows "each L0/L1 check (L2 when enabled)"
    (`SK-001:262-267`); it does not place the security scan inside `runs.verification`.
- **What is missing/ambiguous/contradictory:** BSB-33-PENDING-2 defines a check shape and an
  `llm.scan` entry that BSB-29's epic does not state, and the entry looks like BSB-32's LLM
  security scan, which BSB-32 defines as a separate advisory record. If a developer implements
  `llm.scan` as a verification check that can fail, the run's final verdict may be perceived as
  gated by the security scan, contradicting FR-085 and BSB-32's advisory contract; if it is
  BSB-32's scan, it is in the wrong record. If BSB-29 does not persist the shape at all, the
  rendering contract has no producer. No story owns the difference.
- **Question (if a person must decide):** Is the `llm.scan` L2 entry a check produced by the
  shared verification layer (`runs.verification`, owned by BSB-29) or the LLM security scan's
  result (BSB-32's `scans` record, advisory)? If the former, what does it check, and can a fail
  change `runs.final_verdict`? If the latter, why is it in `runs.verification` rather than the
  Security tab, and how is it kept from affecting the verdict? (also Open question 4)
- **Proposed change:**
  - **BSB-33-PENDING-2:** choose one definition in Notes and acceptance criteria. If it is a
    verifier L2 check, name BSB-29 as the definer of `checks[]` (including L2), state whether a
    fail affects the verdict, and use a check id/message that cannot be confused with the security
    scan. If it is BSB-32's scan, remove it from `runs.verification`, show it in the Security tab
    (if BSB-33 owns the tab per Finding 1) or point at the scan report, and add BSB-32 to the
    dependency Notes. In both cases add BSB-29's check-shape contract to the dependency Notes.
  - **Cross-epic (not applied here):** BSB-29's stories must adopt the `verdict`/`overturned`/
    `checks[]` shape and say whether L2 exists; BSB-32 must state that its LLM evidence is not a
    `runs.verification` check and does not affect the verdict.

### Finding 5 — Cross-epic dependency and record ownership: PENDING-4's Jira capture needs a run-start snapshot no BSB-24/BSB-26 story owns, and it extends a `run_jira` table whose other columns belong to the later BSB-28 whose stories do not exist yet

- **Severity:** Advisory
- **Stories touched:** BSB-33-PENDING-4. Cross-epic: BSB-24-PENDING-1, BSB-26-PENDING-1/-3,
  BSB-28.
- **Evidence:**
  - BSB-33-PENDING-4, Notes: "the builder takes the project snapshot when the run starts, takes
    it again when the run reaches a terminal state, and persists the field-level differences as
    `run_jira.changes`. The run window is the attribution boundary" (`stories.md:304-311`). Its
    first scenario's `state_before` is the project state "when the run starts" and `state_after`
    the state "when the run finishes" (`stories.md:266-268`).
  - Its dependency Notes name BSB-22-PENDING-3, BSB-23-PENDING-1 and "BSB-26 for the run reaching
    a terminal state" (`stories.md:297-299`); they do not name BSB-24-PENDING-1 or
    BSB-26-PENDING-1/-3 as the owner of the run-start read. BSB-24-PENDING-1's Notes say "Jira is
    not a run-start choice: the run inherits the project's Jira integration when execution seeds
    or reads Jira (BSB-26 and BSB-28)" (`BSB-24/_epic/stories.md:122-124`), and BSB-26's stories
    contain no `run_jira` snapshot step (the only Jira integration use is the launch environment
    in BSB-26-PENDING-1).
  - PENDING-4, Out of scope: "Jira fixture seeding, alias substitution, cleanup and the nightly
    sweep (**BSB-28, Later**); recording `run_jira.state_after` for fixture assertions (FR-060,
    BSB-28)" (`stories.md:289-293`); Notes: "The data model already names `run_jira` with
    `run_id`, `aliases`, `state_after` and `cleaned_at` (ADR SK-001 section 9); this story adds
    `state_before` JSONB, `changes` JSONB and `capture_error` text, all nullable, and the
    data-model stage must record them" (`stories.md:300-302`).
  - BSB-28 (Later) owns the fixture seeding, alias substitution, post-run state for fixture
    assertions (FR-060) and cleanup (`epics.md:1175-1225`); its stories are not written.
- **What is missing/ambiguous/contradictory:** The run-start snapshot has no owning hook in
  BSB-24 or BSB-26; if no run-start code calls BSB-33's capture, `state_before` cannot exist and
  the first acceptance criterion is unbuildable. The `run_jira` table is split across two epics
  with no named contract: BSB-33 (MVP) adds and reads `state_before`, `state_after`, `changes`
  and `capture_error`, while BSB-28 (Later) owns `aliases`, `cleaned_at` and FR-060's post-run
  state. A BSB-33 implementer can design a table BSB-28 later conflicts with, and BSB-28's
  planner has no MVP column contract to consume.
- **Question (if a person must decide):** Which story performs the run-start Jira project
  snapshot (BSB-24-PENDING-1 at run creation, BSB-26-PENDING-1 at launch, or BSB-33-PENDING-4
  itself as a hook on the run-start path), and which story owns the full `run_jira` schema
  (`aliases`, `state_after`, `state_before`, `changes`, `capture_error`, `cleaned_at`)? If BSB-28
  is Later, which MVP story owns the table's base columns? (also Open question 5)
- **Proposed change:**
  - **BSB-33-PENDING-4:** name the run-start trigger owner in Notes and dependencies
    (BSB-24-PENDING-1 / BSB-26-PENDING-1) and state whether this story adds the hook; add a
    scenario for a run-start snapshot failure (the run still completes and the section shows
    "Jira changes unavailable"), mirroring the existing terminal-capture failure. Name BSB-28 as
    the owner of `aliases` and `cleaned_at` (FR-060) and state that this story owns only
    `state_before`, `state_after`, `changes` and `capture_error` for MVP; add a data-model
    hand-off sentence for the full `run_jira` column set.
  - **Cross-epic (not applied here):** BSB-24-PENDING-1 or BSB-26-PENDING-1 must call the
    run-start snapshot (or explicitly hand it to BSB-33-PENDING-4); BSB-28's stories must adopt
    the same `run_jira` table and column contract.

### Finding 6 — Cross-story data-model hand-off: PENDING-3 adds `runs.diff_error` but, unlike its siblings, never tells the data-model stage to record it

- **Severity:** Advisory
- **Stories touched:** BSB-33-PENDING-3. Cross-story comparison: BSB-33-PENDING-4,
  BSB-25-PENDING-3, BSB-26-PENDING-3.
- **Evidence:**
  - BSB-33-PENDING-3, "A diff that was not captured is shown as unavailable": the `runs` row has
    `diff_error NULL`, and after the failed capture "diff_error 'The run diff could not be
    captured.'" (`stories.md:219-222`); Notes: "The capture failure is recorded in `runs.diff_error`"
    (`stories.md:245-247`).
  - BSB-33-PENDING-4 states the opposite pattern for its own additions: "this story adds
    `state_before` JSONB, `changes` JSONB and `capture_error` text, all nullable, and the
    data-model stage must record them" (`stories.md:300-302`).
  - BSB-25-PENDING-3: "The data-model stage must add `runs.baseline_sha`; ADR SK-001 section 9
    does not list it" (`BSB-25/_epic/stories.md:262-265`). BSB-26-PENDING-3: "both columns are
    added by the data-model stage together with `runs.execution_error`"
    (`BSB-26/_epic/stories.md:279-285`).
  - ADR SK-001 §9's `runs` table lists no `diff_error` (`SK-001:355`).
- **What is missing/ambiguous/contradictory:** `runs.diff_error` is the only persistent column
  BSB-33 adds without the data-model hand-off sentence. A data-model pass reading PENDING-3's
  story will see the column in fixtures and prose but not in the "must record" contract; a pass
  reading only PENDING-4's declaration will omit it. The peer stories (BSB-25-PENDING-3,
  BSB-26-PENDING-3) establish the convention PENDING-3 breaks.
- **Question (if a person must decide):** None — this is a consistency correction, unless
  `diff_error` is meant to live in the captured object rather than on `runs`; if so, state that
  explicitly.
- **Proposed change:**
  - **BSB-33-PENDING-3:** add the sentence "This story adds nullable `runs.diff_error`; ADR SK-001
    §9 does not list it and the data-model stage must record it." Add it to the epic-level
    data-model hand-off list beside PENDING-4's `run_jira` columns. No acceptance-criterion change.

### Finding 7 — Cross-epic dependency note: PENDING-5 assigns `runs.trace_id` and the installation trace URL template to BSB-34, but BSB-34's epic scope claims neither

- **Severity:** Advisory
- **Stories touched:** BSB-33-PENDING-5. Cross-epic: BSB-34.
- **Evidence:**
  - BSB-33-PENDING-5, Notes: "Depends on … BSB-34 for `runs.turn_count` (NFR-017),
    `runs.trace_id` and the installation's tracing configuration (NFR-011; the trace store is
    external). **BSB-34 owns recording those values**" (`stories.md:363-369`); Out of scope:
    "choosing or storing the trace identifier (the trace store and BSB-34)" (`stories.md:356-359`).
  - Its acceptance criteria require the record `runs.trace_id "trace-4f2c9a1b7d3e"` and
    "installation tracing configuration with tracing enabled and trace URL template
    `https://langfuse.test/traces/{trace_id}`" (`stories.md:331-334`), plus the disabled and
    missing-id states (`stories.md:336-349`).
  - BSB-34's epic functional scope records "Record each run's cost", "Record each run's token
    usage", "Record each run's turn count", "When tracing is enabled, identify every run's trace
    as a test-environment run", retention, purge and the three-month default (`epics.md:1125-1136`).
    It does **not** name `runs.trace_id`, a trace URL template, or an installation tracing
    enable/disable setting beyond the test-environment marker. Its covered requirements are
    FR-159, FR-160 and NFR-011/013/014/015/016/017/018 (`epics.md:1155-1166`).
  - ADR SK-001 §9's `runs` table lists no `trace_id` (`SK-001:355`); §6 says "Langfuse traces, if
    enabled, carry `env = skilltest`" but defines no link template (`SK-001:262-267`).
- **What is missing/ambiguous/contradictory:** The dependency note is one-sided. BSB-33-PENDING-5
  assigns BSB-34 a column and a configuration BSB-34's epic does not claim, so a BSB-34 planner
  may build only the test-environment marker, turn count and retention, leaving the trace link
  without a producer. The story's ACs cannot pass unless someone records `trace_id` at execution
  time and defines the installation template. A developer could invent both inside BSB-33, which
  would split the run/trace record across two epics with no owner.
- **Question (if a person must decide):** Does BSB-34 own `runs.trace_id` and the
  installation-level tracing configuration (enabled flag plus URL template), or does
  BSB-33-PENDING-5 own recording the trace identifier on the run and the template setting, with
  the data-model stage recording them? (The trace store itself is external either way.)
  (also Open question 6)
- **Proposed change:**
  - **BSB-33-PENDING-5:** if BSB-34 owns them, keep the dependency but add the exact deliverable
    to Notes ("BSB-34 must record `runs.trace_id` and define the installation tracing enabled
    flag and URL template"); if BSB-34 will not own them, state that this story adds
    `runs.trace_id` and the installation setting and that the data-model stage must record them,
    and move them out of the out-of-scope list.
  - **Cross-epic (not applied here):** BSB-34's epic scope (or its stories, when written) must
    name `runs.trace_id` and the installation trace configuration, or explicitly decline them so
    BSB-33 can own them. ADR SK-001 §9's `runs` table is the place the data-model stage records
    the column.

### Finding 8 — Dependency-note sanity: PENDING-2 cites a non-existent story, BSB-32-PENDING-5, for the run page's "Verdict:" line

- **Severity:** Advisory
- **Stories touched:** BSB-33-PENDING-2. Cross-epic: BSB-32-PENDING-2, BSB-32-PENDING-4.
- **Evidence:**
  - BSB-33-PENDING-2, Notes: "The final-verification verdict is rendered on the 'Verdict:' line
    that **BSB-32-PENDING-5's** acceptance criteria already expect; the agent's claim is on the
    separate 'Claimed verdict:' line" (`stories.md:184-186`).
  - BSB-32's `story-map.json` and `stories.md` contain only BSB-32-PENDING-1, -2, -3 and -4
    (`BSB-32/_epic/story-map.json:1-26`; `BSB-32/_epic/stories.md:20-271`). The run-page
    "Verdict: PASS" expectations are in BSB-32-PENDING-2
    (`BSB-32/_epic/stories.md:131-134`) and BSB-32-PENDING-4
    (`BSB-32/_epic/stories.md:311-314`).
  - BSB-33-PENDING-2's dependency Notes name BSB-22-PENDING-3, BSB-26-PENDING-3 and BSB-29 but
    not BSB-32 or BSB-26-PENDING-2, the owner of the run page shell it extends
    (`stories.md:170-174`).
- **What is missing/ambiguous/contradictory:** The note points at a story that does not exist.
  A BSB-33 implementer looking for the "Verdict:" contract will not find it, and the one-sided
  claim is not matched on BSB-32's side (BSB-32's review Finding 6 records that PENDING-2/-4
  assert the run page without naming BSB-33). The shared-page dependency on BSB-26-PENDING-2 is
  also unstated in this story, unlike PENDING-1.
- **Question (if a person must decide):** None — the owner exists and the citation is a typo.
- **Proposed change:**
  - **BSB-33-PENDING-2:** replace "BSB-32-PENDING-5" with "BSB-32-PENDING-2 and
    BSB-32-PENDING-4"; add BSB-32 and BSB-26-PENDING-2 to the dependency Notes. Keep the
    claimed/final verdict distinction as written.
  - **Cross-epic (not applied here):** BSB-32's review Finding 6 already asks BSB-32-PENDING-2
    and -4 to name BSB-33; the corrected reference closes the BSB-33 side.

## Open questions

1. **Security tab and reviewer-facing scan report (Finding 1).** Does BSB-33 own the combined
   Security tab on the run page and the reviewer-facing stable scan-report view (adding a story or
   acceptance criteria), or do BSB-32/BSB-36 own them? If BSB-33 owns the tab, which BSB-31/BSB-32
   records does it compose, and is the LLM scan advisory per FR-085?
2. **Catalog-reviewer access rule for the run report (Finding 2).** Do catalog reviewers read a
   run report outside the builder authoring gate and the project-membership check? If yes, what
   authorizes them (signed read-only share link, reviewer role/group, or public view), which route
   renders it, and which epic owns it? If no, is `PRD.md` §2's "does not use the authoring
   interface" wrong, and must the epic DoD and BSB-36's FR-110 link be narrowed? Resolve together
   with BSB-22's Open question 1 and BSB-31's Finding 5.
3. **Credential-redaction input and timing (Finding 3).** How does the report obtain the run
   project's resolved credential values and call BSB-23-PENDING-5's helper — at capture time for
   `runs/<id>/diff.json` and the `run_jira` snapshots, at render time, or both — and must the
   persisted captured objects be redacted before storage or only when rendered?
4. **The `llm.scan` L2 record (Finding 4).** Is `llm.scan` a shared-verification L2 check
   (`runs.verification`, BSB-29) or BSB-32's advisory LLM security scan (`scans`)? If a
   verification check, can a fail change `runs.final_verdict`? If BSB-32's scan, why is it in
   `runs.verification` rather than the Security tab / scan report?
5. **Run-start Jira snapshot and `run_jira` schema owner (Finding 5).** Which story takes the
   run-start project snapshot (BSB-24-PENDING-1, BSB-26-PENDING-1, or BSB-33-PENDING-4), and which
   story owns the full `run_jira` schema, including the `aliases`/`cleaned_at` columns that BSB-28
   (Later) uses?
6. **Trace-id and template ownership (Finding 7).** Does BSB-34 own `runs.trace_id` and the
   installation tracing enabled flag and URL template, or does BSB-33-PENDING-5 own them? The
   trace store is external either way.

## Proposed changes

`docs/product/epics/BSB-33/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-33-PENDING-1** — Out of scope/Notes: name the actual Security tab and reviewer-facing
  scan-report owner and reconcile with BSB-26-PENDING-2 and BSB-31-PENDING-5 (Finding 1); state
  the reviewer access rule or the explicit deferral, and how the reviewer route differs from the
  403 AC (Finding 2); name BSB-23-PENDING-5's redaction helper and add a render-time redaction AC
  (Finding 3).
- **BSB-33-PENDING-2** — Notes/ACs: add the reviewer-view/access sentence and BSB-36 hand-off
  (Finding 2); name BSB-23-PENDING-5's redaction (Finding 3); resolve the `llm.scan` L2 record and
  its verdict effect (Finding 4); replace `BSB-32-PENDING-5` with BSB-32-PENDING-2/-4 and add
  BSB-32 and BSB-26-PENDING-2 to the dependencies (Finding 8).
- **BSB-33-PENDING-3** — Notes/ACs: add the reviewer-view/access sentence (Finding 2); name the
  redaction helper and add a diff-patch redaction AC and stored-object assertion (Finding 3);
  declare nullable `runs.diff_error` to the data-model stage (Finding 6).
- **BSB-33-PENDING-4** — Notes/ACs: add the reviewer-view/access sentence (Finding 2); name the
  redaction helper and add a `run_jira` field redaction AC (Finding 3); name the run-start
  snapshot owner, add the snapshot-failure scenario, and state the full `run_jira` column
  ownership with BSB-28 (Finding 5).
- **BSB-33-PENDING-5** — Notes/ACs: add the reviewer-view/access sentence (Finding 2); name the
  redaction helper (Finding 3); settle whether `runs.trace_id` and the installation tracing
  configuration are BSB-34's or this story's, and add the data-model hand-off (Finding 7).

Cross-epic follow-ups (not applied here):

- **BSB-26-PENDING-2** — Reconcile its "BSB-31, BSB-32 and BSB-33" Security tab ownership with the
  owner chosen in Finding 1 / Open question 1.
- **BSB-31-PENDING-5** — Reconcile "the combined security tab (BSB-32)" and "the reviewer-facing
  stable report view … BSB-33/BSB-36" with the owner chosen in Findings 1-2.
- **BSB-32** — Its review's Open question 2 / Finding 2 (combined Security tab) and Finding 7
  (reviewer view) must land on the same owner; PENDING-2/-4 should name BSB-33 for the run page
  (Finding 8), and the LLM scan must remain advisory and outside `runs.verification` (Finding 4).
- **BSB-36** — Point FR-110 at the reviewer-readable run report, not only the member-gated
  authoring URL, once Open question 2 is answered (Finding 2).
- **BSB-34** — Name `runs.trace_id` and the installation tracing enabled flag and URL template in
  its scope, or explicitly decline them so BSB-33 can own them (Finding 7).
- **BSB-28** — Adopt the same `run_jira` table and column contract, including the MVP
  `state_before`/`changes`/`capture_error` columns and the Later `aliases`/`cleaned_at` columns
  (Finding 5).
- **BSB-24-PENDING-1 / BSB-26-PENDING-1** — Call the run-start Jira project snapshot, or hand that
  hook explicitly to BSB-33-PENDING-4 (Finding 5).
- **BSB-29** — Adopt/define the `verdict`/`overturned`/`checks[]` shape and say whether L2 exists;
  reconcile with BSB-32's advisory scan (Finding 4).
- **BSB-23-PENDING-5** — Define the redaction helper's input contract (text/document plus the
  run project's resolved credential values) that BSB-33 consumes (Finding 3; already requested by
  BSB-23's review Finding 6).
- **BSB-22-PENDING-1/-3** — Scope the shared membership check to author-facing surfaces once Open
  question 2 is answered (Finding 2; already requested by BSB-22's review Finding 1).

## Architecture impact

None. The epic's cumulative behavior adds nullable record fields the ADR's §9 tables do not name —
`run_jira.state_before`, `run_jira.changes`, `run_jira.capture_error` (declared by PENDING-4),
`runs.diff_error` (PENDING-3, currently undeclared) and BSB-34's `runs.turn_count`/`runs.trace_id`
— but these are the normal planning-to-design hand-off the later data-model stage records, not a
conflict with an existing entity, a new service or a new integration. The Security tab, the
reviewer access rule and the `run_jira` column split are ownership/product decisions, not new
design. No new design is required before the stories can be revised.

## Requirement coverage check

All thirteen requirements mapped to BSB-33 by `epic-map.json` are exercised by at least one
acceptance criterion, each is claimed by exactly one story, and no story claims a requirement
outside the epic. `epic-map.json`, `epics.md` and `PRD.md` agree on the current wording of every
mapped requirement; no drift was found.

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-094 — the run page shows the skill that ran | BSB-33-PENDING-1 | "A completed run's report shows what ran"; "A run that failed before component versions were recorded shows not recorded". |
| FR-095 — the run page shows the input branch | BSB-33-PENDING-1 | Same two scenarios (`Input branch:` line). |
| FR-096 — the run page shows the output branch | BSB-33-PENDING-1 | Same two scenarios (`Output branch:` / "not recorded"). |
| FR-097 — the run page shows the component versions used | BSB-33-PENDING-1 | Same two scenarios (agent image, step kit, verifier / "not recorded"). |
| FR-098 — the run page shows the verdict the agent claimed | BSB-33-PENDING-2 | "An upheld claim shows both verdicts and every check result"; "An overturned claim shows both verdicts"; "A run whose verification has not run shows no final verdict". |
| FR-099 — the run page shows each check result | BSB-33-PENDING-2 | "An upheld claim shows both verdicts and every check result"; "An overturned claim shows both verdicts"; "A partial verification record shows checks unavailable". **Caveat:** the `llm.scan` L2 entry is Finding 4. |
| FR-100 — the run page shows the diff from the input branch to the run branch | BSB-33-PENDING-3 | "The captured diff is shown from the baseline to the output head"; "A run that changed nothing shows an empty diff"; "The shown diff is pinned to the head captured at run completion"; "A diff that was not captured is shown as unavailable". |
| FR-101 — the run page shows the Jira changes the run made | BSB-33-PENDING-4 | "The Jira changes the run made are recorded and shown"; "A run with no Jira changes shows an empty state"; "A Jira change capture that fails is shown as unavailable"; "A project with no Jira integration shows the section as not recorded". |
| FR-102 — the run page shows the run's turn count | BSB-33-PENDING-5 | "The recorded turn count and trace link are shown"; "Tracing disabled shows no trace link"; "A missing trace identifier shows trace unavailable"; "A run that recorded no turns shows not recorded". |
| FR-103 — the run page links to the run's trace when tracing is enabled | BSB-33-PENDING-5 | "The recorded turn count and trace link are shown"; "Tracing disabled shows no trace link"; "A missing trace identifier shows trace unavailable". **Caveat:** the trace-id/template owner is Finding 7. |
| FR-140 — the builder records the Jira changes a run makes | BSB-33-PENDING-4 | "The Jira changes the run made are recorded and shown"; "A run with no Jira changes shows an empty state"; "A Jira change capture that fails is shown as unavailable". |
| FR-157 — the run page shows the skills commit SHA | BSB-33-PENDING-1 | "A completed run's report shows what ran"; "A run that failed before component versions were recorded shows not recorded". |
| FR-158 — the run page shows the final verdict after verification | BSB-33-PENDING-2 | "An upheld claim shows both verdicts and every check result"; "An overturned claim shows both verdicts"; "A run whose verification has not run shows no final verdict"; "A partial verification record shows checks unavailable". |

No NFR is mapped to BSB-33 in `epic-map.json`. NFR-002/NFR-003 (the signed-in gate and the
one-hour removal rule) are inherited from BSB-18 and exercised through BSB-33-PENDING-1's 403/404
scenarios; NFR-004 (credential values) is mapped to BSB-23 and is the subject of Finding 3;
NFR-012 (accessibility) is cross-cutting and owned by BSB-38, as the BSB-20/BSB-22/BSB-26/BSB-31/
BSB-32 reviews already record, so no epic-wide silent NFR is left unaddressed. FR-159/FR-160
(token usage and cost) are FA-13 but mapped to BSB-34, and every BSB-33 story's out-of-scope names
BSB-34 for them.

## Dependency-note sanity check

Every "Depends on" story key in BSB-33's stories names a real story in the named epic, with one
exception: BSB-33-PENDING-2 cites BSB-32-PENDING-5, which does not exist (Finding 8). The rest are
consistent or are the findings above; no note asks this review to compute a build order.

| Story | Dependency as written | Check |
|---|---|---|
| BSB-33-PENDING-1 | BSB-18 (session and authoring gate) | Exists; BSB-18-PENDING-1/-2/-3 own the gate. |
| BSB-33-PENDING-1 | BSB-22-PENDING-1, BSB-22-PENDING-3 | Exist; PENDING-1 owns `projects`/`project_members`, PENDING-3 owns the shared membership check and names BSB-33's reports in its reuse list. |
| BSB-33-PENDING-1 | BSB-24-PENDING-1 | Exists; owns `runs.build_id`, the accepted run and `runs.input_branch`. |
| BSB-33-PENDING-1 | BSB-25-PENDING-1, -2, -3 | Exist; -1 owns `runs.skills_commit_sha`, -2 owns `skill_bundles`, -3 owns `runs.run_branch`/`runs.baseline_sha`. |
| BSB-33-PENDING-1 | BSB-26-PENDING-1 | Exists; owns `runs.agent_image_digest`/`stepkit_version`/`verify_version` and the run-page route it extends with BSB-26-PENDING-2. |
| BSB-33-PENDING-2 | BSB-22-PENDING-3 | Exists; shared membership check. |
| BSB-33-PENDING-2 | BSB-26-PENDING-3 | Exists; owns `runs.claimed_verdict` and the execution outcome. |
| BSB-33-PENDING-2 | BSB-29 | Epic exists with no stories yet; its scope owns `runs.final_verdict`/`runs.verification`, but it does not state the `checks[]` shape or an L2 entry (Finding 4). |
| BSB-33-PENDING-2 | **BSB-32-PENDING-5 (not a real story)** | BSB-32 has PENDING-1 to -4 only; the intended stories are BSB-32-PENDING-2/-4 (Finding 8). BSB-26-PENDING-2 (the run page shell) is also not named. |
| BSB-33-PENDING-3 | BSB-22-PENDING-3 | Exists; shared membership check. |
| BSB-33-PENDING-3 | BSB-23-PENDING-2 | Exists; owns the source-control integration and sandbox repository. |
| BSB-33-PENDING-3 | BSB-25-PENDING-3, BSB-26-PENDING-3 | Exist; baseline/run branch and the terminal output branch. |
| BSB-33-PENDING-3 | **BSB-23-PENDING-5 (not named)** | The shared redaction helper BSB-33 must call; its own review records the one-sided claim (Finding 3). `runs.diff_error` is not declared to the data-model stage (Finding 6). |
| BSB-33-PENDING-4 | BSB-22-PENDING-3, BSB-23-PENDING-1 | Exist; membership check and the Jira integration/`secret_ref`. |
| BSB-33-PENDING-4 | BSB-26 (terminal state) | Exists; BSB-26-PENDING-3 owns the terminal state. The **run-start** snapshot is not named or owned by a BSB-24/BSB-26 story (Finding 5). |
| BSB-33-PENDING-4 | **BSB-28 (not named in dependencies)** | BSB-28 is the Later epic that owns `run_jira.aliases`/`cleaned_at` and FR-060; the column split is unstated (Finding 5). |
| BSB-33-PENDING-4 | **BSB-23-PENDING-5 (not named)** | Redaction of the Jira snapshots/changes is unstated (Finding 3). |
| BSB-33-PENDING-5 | BSB-22-PENDING-3, BSB-26 | Exist; membership check and the terminal run. |
| BSB-33-PENDING-5 | BSB-34 | Epic exists with no stories yet; its scope records turn count but not `runs.trace_id` or the trace URL template (Finding 7). |

Reciprocity spot-check: BSB-25-PENDING-3's Notes say "what BSB-33's diff uses" and its out-of-scope
names BSB-33; BSB-26-PENDING-2's out-of-scope names the run report's verdict/component/diff/Jira
sections as BSB-33's and its Notes say BSB-33 adds the report sections to the same page;
BSB-26-PENDING-3's out-of-scope names BSB-33's diff/Jira/check sections and its Notes say BSB-33
uses the baseline and run branch. Those are reciprocal. The one-sided claims are BSB-23-PENDING-5
(Finding 3), BSB-31-PENDING-5 and BSB-32 (Finding 1), BSB-34 (Finding 7) and BSB-28 (Finding 5).
