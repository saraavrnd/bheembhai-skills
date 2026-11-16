# Epic Review — BSB-35: Skill history & run comparison

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-35-PENDING-1, BSB-35-PENDING-2, BSB-35-PENDING-3

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-35/_epic/epic-review.md`.

## Context loaded

- **Work item and epic.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item
  umbrella rather than a Jira issue. A read-only `GET /rest/api/3/issue/SkillBuilder-2` returned
  HTTP 404 ("Issue does not exist or you do not have permission to see it."), matching
  `PRD.md` §8 and the source note in BSB-35's own `stories.md:19-26`. The Atlassian MCP server is
  configured in `.mcp.json`, but this session exposed no Atlassian MCP tools, so the configured
  site (`https://saraavrnd.atlassian.net`) was queried read-only through its REST API (GET only;
  no Jira writes). The run context's epic item is **BSB-35**; the branch HEAD (`2bc6294`) is the
  `sdlc-plan-stories-write` step (run `200e61fb-322e-4de0-9d6b-8c297624c3de`) that wrote
  `BSB-35/_epic/stories.md` and `story-map.json`, and `config/sdlc-wf-planning-epic.yaml` runs
  `sdlc-plan-epic-review` immediately after that step for the same epic. Jira
  `GET /rest/api/3/issue/BSB-35` returned HTTP 200: Epic **"Skill history & run comparison"**,
  status **To Do**, labels **FA-14, Later**, no parent, no subtasks and no issue links. BSB-35
  has no prior `epic-review.md` and no `revisions.md`, so this is the first review pass.
- **All 3 stories in the epic**, from `stories.md` (lines 1-319) and `story-map.json` in one read
  each: BSB-35-PENDING-1 (FR-104, the history list), BSB-35-PENDING-2 (FR-105, the two-run
  comparison) and BSB-35-PENDING-3 (FR-106, the flipped-check highlight) — the full set, not a
  sample. `story-map.json` maps one requirement per story, and the coverage table at
  `stories.md:54-60` maps the same three requirements to named acceptance criteria.
- **`PRD.md`** — §5 FA-14 (`PRD.md:63`), §6 FR-104 to FR-106 (`PRD.md:178-180`), §7 NFR-002,
  NFR-003 and NFR-012 (`PRD.md:252-253,262`), §8's source note, and the Later release split.
  `epic-map.json` assigns BSB-35 only FR-104, FR-105 and FR-106 — no NFR.
- **`epics.md`** — the BSB-35 section (`epics.md:1229-1267`): description, functional scope, the
  five-step implementation guidance (step 1 is "Build the history query over **completed runs**
  keyed by skill identity, ordered by time", `:1247`), the Definition of Done, the three covered
  requirements and the Notes ("History is scoped to one skill", `:1266`). Also read because the
  stories hand work to it: the BSB-38 accessibility epic (`epics.md:1406-1466`), whose scope is
  "all web surfaces built by the other epics" and whose release is MVP.
- **`docs/adr/SK-001-skill-builder.md`** — §5's two branches and the pinned skills commit
  (`SK-001:213-245`), §6 Results including the skill-history and compare behaviour
  (`SK-001:256-274`), §6a verify.yaml travelling in the bundle (`SK-001:276-282`), and §9's data
  model (`SK-001:345-357`), whose `runs` row carries `project_id`, `skill`, `skills_commit_sha`,
  `input_branch`, `state`, `final_verdict`, `verification` and `kind` but has no `skills` table.
- **Sibling stories this epic reads from:** BSB-22-PENDING-1 (Project Atlas and the membership
  rows) and -PENDING-3 (the shared project-membership check and its exact 403 message,
  `BSB-22/_epic/stories.md:204-212`); BSB-24-PENDING-1 (the `runs` row and `created_at`,
  `BSB-24/_epic/stories.md:38`); BSB-25-PENDING-1 (the resolver that freezes
  `runs.skills_commit_sha`, `BSB-25/_epic/stories.md:54,95`) and -PENDING-2 (the bundle, which
  itself depends on PENDING-1, `BSB-25/_epic/stories.md:188`); BSB-26-PENDING-1 and -PENDING-3
  (`runs.state`, `result_status`, `execution_error`, and the terminal classification);
  BSB-33-PENDING-1 (the run report at `GET "/projects/7/runs/21"` and the "not recorded"
  vocabulary, `BSB-33/_epic/stories.md:71-89,114`) and -PENDING-2 (the `runs.verification` read
  contract and its two unavailable states, `BSB-33/_epic/stories.md:176-190`); BSB-34-PENDING-3
  and -4 (retention and purge leave the `runs` row and its verification columns,
  `BSB-34/_epic/stories.md:304`).
- **Prior reviews read for precedent:** BSB-34's review in full (severity calibration, cross-epic
  producer/consumer findings, fallback-vocabulary findings) and BSB-28's review's context and
  finding structure.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md`.
  There is therefore no project-wide API/UI convention for the two routes PENDING-1 and -2 add;
  the review relies on ADR SK-001 §9 and the owning stories named above.

## Findings

### Finding 1 — Cross-story compare-table identity: PENDING-2 keys a check row by `(id, level)` while PENDING-3 keys a flip by `id` alone

- **Severity:** Blocking
- **Stories touched:** BSB-35-PENDING-2, BSB-35-PENDING-3 (cross-epic: BSB-33-PENDING-2, BSB-29)
- **Evidence:**
  - BSB-35-PENDING-2's Notes say "one row per check id present in either run" and then "The check
    row is **identified by the check `id` plus its `level` in parentheses**; the left and right
    cells hold that run's uppercase status" (`stories.md:234-238`).
  - BSB-35-PENDING-3's Notes say "A flip is defined over check *identity*, which is the check
    `id`" and "**The check `level` is displayed but is not part of identity**, because
    `verify.yaml` check ids are unique within a run" (`stories.md:299-305`).
  - This epic exists to compare two different skills commits: the "Commit" the history and compare
    views show is `runs.skills_commit_sha` (`stories.md:37-39`), and `verify.yaml` travels with the
    bundle, so each run is graded by its own commit's manifest (ADR SK-001 §6a,
    `SK-001:276-282`). The same check id can therefore legitimately appear at a different level in
    the two compared runs — the very case of editing `verify.yaml` and re-running.
  - The uniqueness PENDING-3 relies on is not owned anywhere: BSB-33-PENDING-2 defines `level` per
    check entry but never states that ids are unique in `runs.verification.checks`
    (`BSB-33/_epic/stories.md:176-180`); BSB-29 (which persists the object) has no stories yet
    (`docs/product/epics/BSB-29/` does not exist).
- **What is missing/ambiguous/contradictory:** If check `must_change` is L1 in the left run and L0
  in the right run, PENDING-2's rule renders two rows — `must_change (L1)` with "not present" on
  the right and `must_change (L0)` with "not present" on the left — while PENDING-3's rule says the
  id is present in both runs and is a flip. There is no single row to carry the "Flipped:" marker,
  and the "Checks flipped: N." count can disagree with the rows an implementer rendered. Two
  implementers reading one story each build different tables from the same two runs.
- **Question (if a person must decide):** Is a check whose `id` is the same but whose `level`
  changed between the two runs the same check for flip purposes — and if so, which level is
  displayed and which level does the row label use? Who owns the "check ids are unique within a
  run" guarantee PENDING-3 relies on? (also Open question 1)
- **Proposed change:**
  - **BSB-35-PENDING-2:** make the row identity the check `id` (matching "one row per check id
    present in either run"); display each column's own `level` beside its status so a level change
    is visible without splitting the row; state the behaviour when the two levels differ. Add a
    scenario with the same id at L0 in one run and L1 in the other.
  - **BSB-35-PENDING-3:** apply the same identity rule explicitly (already its intent) and define
    whether a level change is or is not a flip; add that case to the flip rules and to the
    one-sided/unavailable-check scenarios so the count and the markers cannot disagree.
  - **Cross-epic (revise pass, not applied here):** BSB-33-PENDING-2 — as the cited read-contract
    owner — and BSB-29 when it is written must state that check ids are unique within
    `runs.verification.checks`, or define duplicate-id behaviour; PENDING-3 currently cites a
    guarantee no story makes.

### Finding 2 — Epic boundary: all three stories narrow FR-104 to "every run of the skill in the current project, in any state" while the epic's guidance says "completed runs", and no owner covers a cross-project history

- **Severity:** Advisory
- **Stories touched:** BSB-35-PENDING-1, BSB-35-PENDING-2, BSB-35-PENDING-3; the BSB-35 epic boundary
- **Evidence:**
  - The stories' shared scope decision: "Both views are addressed under a project … FR-104's
    'every run of a skill' is therefore every `runs` row of that skill recorded in the project the
    view is opened in. A cross-project history would need a new aggregation and access rule that
    no requirement or epic defines; it is out of scope rather than invented here"
    (`stories.md:29-36`). The same header says "Every `runs` row counts as a run, whatever its
    `state` and whether its `kind` is `run` or `reverify`" (`stories.md:48-52`).
  - The requirement being narrowed is "The skill history lists **every run of a skill** with its
    commit SHA, input branch, verdict and checks." (`PRD.md:178`) — no project, state or kind
    qualifier.
  - The epic's implementation guidance says "Build the history query over **completed runs** keyed
    by skill identity, ordered by time" (`epics.md:1247`), and its Notes say "History is scoped to
    one skill" (`epics.md:1266`) — again no project scope and no "all states".
  - PENDING-1's acceptance criteria enforce the narrowing: a run of the same skill in project 8 is
    not rendered (`stories.md:78-80`), and a failed run with no verification is listed as
    "Verdict: not run" / "Checks: unavailable" (`stories.md:82-85`). PENDING-2's form lists "every
    run in the history" (`stories.md:218-223`), and PENDING-3 compares whatever those two runs
    contain, so the same narrowed set flows through all three stories.
  - No other epic or story owns a cross-project or author-wide history: BSB-22-PENDING-3 makes
    project membership the builder's run-access rule (`BSB-22/_epic/stories.md:204-212`), and
    BSB-33's run report is project-scoped (`BSB-33/_epic/stories.md:114`). The PRD's Later list
    (`PRD.md` §4) does not mention a cross-project history either.
- **What is missing/ambiguous/contradictory:** Two narrowing decisions are made in the story
  header but never presented as answered product decisions. If FR-104 means every run the author
  has across projects, the stories build the wrong scope and the missing aggregation/access rule
  is the real work. If FR-104 means "in the project", the PRD and epic text should say so, because
  an implementer reading only the epic would build a skill-wide history. Separately, the epic
  says "completed runs" while the stories include requested/preparing/running/failed rows; an
  in-flight run appears as "Verdict: not run" with no indication it is still executing.
- **Question (if a person must decide):** Does FR-104 mean every run of the skill across all the
  author's projects — requiring an access rule and a cross-project aggregation — or every run
  recorded in the current project? And should the history include in-flight and re-verification
  rows, or only completed runs as the epic guidance says? (also Open question 2)
- **Proposed change:**
  - **BSB-35-PENDING-1:** state the confirmed answer in the existing "Scope decisions" block
    rather than only as a rationale; add an in-flight-run scenario asserting its exact rendering
    (state, "Verdict: not run", "Checks: unavailable") so "every row" has an observable contract;
    if only completed rows are intended, restrict the query and remove the failed/in-flight cases
    from the ACs.
  - **BSB-35-PENDING-2 and -PENDING-3:** state that the compare form and flip computation operate
    on the same project-scoped, all-state set as the history, so the three stories agree on what
    "a run of this skill" means.
  - **Cross-epic (revise pass, not applied here):** if the project-scoped answer is confirmed,
    qualify FR-104 in the PRD (or record the decision in `epics.md`'s BSB-35 Notes) and correct
    "completed runs" at `epics.md:1247`; if cross-project is intended, add the missing story and
    the access rule.

### Finding 3 — Epic-wide NFR: accessibility is deferred to BSB-38, an MVP epic with no stories that is sequenced before BSB-35's Later surfaces

- **Severity:** Advisory
- **Stories touched:** BSB-35-PENDING-1, BSB-35-PENDING-2, BSB-35-PENDING-3; the BSB-35 epic boundary
- **Evidence:**
  - Every story's "Out of scope" ends by deferring accessibility: "viewport and accessibility
    layout work (BSB-38)" (`stories.md:113`), "accessibility layout work (BSB-38)"
    (`stories.md:208`), "accessibility layout work (BSB-38)" (`stories.md:290`).
  - BSB-38's epic says it "applies to all web surfaces built by the other epics" and requires
    keyboard operability, focus indicators, programmatic names/roles/states, form labels,
    live-region announcements, non-colour-only status, WCAG 2.1 AA contrast and 320-pixel reflow
    (`epics.md:1409-1432`), and its guidance says to establish accessible primitives "before
    feature pages proliferate, so later epics build on conforming components"
    (`epics.md:1435-1436`). Its release is **MVP** (`epics.md:1407`).
  - BSB-35 is release **Later** (`epics.md:1230`) and adds two new surfaces — the history page and
    the compare view (`stories.md:125-131,226-232`). BSB-38 has no story folder yet
    (`docs/product/epics/BSB-38/` does not exist), so no BSB-38 acceptance criterion can named the
    history or compare page.
  - `epic-map.json` assigns BSB-35 no NFR, but NFR-012 (`PRD.md:262`) and FR-130 to FR-136 are
    "every builder web surface" requirements, not scoped to FA-17's epic.
- **What is missing/ambiguous/contradictory:** The stories hand these two Later surfaces to an
  epic that is released earlier and cannot audit pages that do not exist when it closes. If BSB-38
  is delivered in the MVP ahead of BSB-35, nothing in the plan makes the history/compare page
  keyboard-operable, labelled, non-colour-only or reflowing at 320 pixels, and G6/NFR-012's
  "100% of audited builder surfaces" target silently excludes them. If BSB-38 remains open for
  Later surfaces, no story says so and no sequencing records it.
- **Question (if a person must decide):** Does BSB-38 stay open and get sequenced after BSB-35 so
  it can audit these Later surfaces, or does BSB-35 own the accessibility acceptance criteria for
  its own two pages? (also Open question 3)
- **Proposed change:**
  - **BSB-35-PENDING-1, -PENDING-2 and -PENDING-3:** replace the bare "accessibility layout work
    (BSB-38)" with a named contract — either the specific FR-130, FR-131, FR-132, FR-133, FR-135,
    FR-136 and NFR-012 acceptance criteria each page must meet (keyboard order for the two selects
    and Compare button, visible focus, labelled selects and error messages, non-colour-only flip
    status, 320-pixel reflow), or a stated hand-off that BSB-38 is extended/re-run after BSB-35
    with those criteria listed. Do not leave the deferral as an unqualified epic name.
  - **Cross-epic (revise pass, not applied here):** record the chosen ownership and sequence in
    `epics.md`'s BSB-35/BSB-38 Notes; if BSB-35 owns it, add the ACs here and no BSB-38 change is
    needed.

### Finding 4 — Cross-story page contract: PENDING-1 and PENDING-2 disagree on the history page's zero-run state and leave the select order ambiguous

- **Severity:** Advisory
- **Stories touched:** BSB-35-PENDING-1, BSB-35-PENDING-2
- **Evidence:**
  - PENDING-1's empty-history scenario: a skill with no runs returns HTTP 200 rendering
    "History — sdlc-fix-bug-reproduce" and "No runs recorded for sdlc-fix-bug-reproduce."
    (`stories.md:87-90`).
  - PENDING-2's "fewer than two runs" scenario: with exactly one run the same page returns HTTP
    200 rendering the run row, "Two runs are needed to compare." and no Compare form
    (`stories.md:178-181`); its Notes generalise this: "With fewer than two runs the form is not
    rendered and the page says 'Two runs are needed to compare.'" (`stories.md:222-223`).
  - Zero is fewer than two, so an empty history must satisfy both stories; PENDING-1 does not
    forbid the second message and PENDING-2 does not carve out zero, so an implementer can render
    "No runs recorded for sdlc-fix-bug-reproduce." and "Two runs are needed to compare." together
    on the same page.
  - PENDING-2's first scenario enumerates the select options as "Run 21", "Run 22" and "Run 24"
    (`stories.md:166`), while PENDING-1 orders rows newest first (`stories.md:78-80,127-129`) and
    PENDING-2's Notes say the options follow "the page's order" (`stories.md:219-221`). Reading
    the AC literally gives oldest-first options, opposite the page and the note.
- **What is missing/ambiguous/contradictory:** The two stories that co-own the same page do not
  define its state at zero runs, and the compare form's option order is stated in the Notes but
  contradicted by the AC's enumeration. Both are cheap to fix but produce either a duplicated
  message or an order-dependent test.
- **Question (if a person must decide):** None; this is a contract wording fix. Use the natural
  split: zero runs shows PENDING-1's empty state only; exactly one run shows PENDING-2's compare
  message.
- **Proposed change:**
  - **BSB-35-PENDING-1:** add to the empty-history scenario that neither the compare form nor the
    "Two runs are needed to compare." message is rendered.
  - **BSB-35-PENDING-2:** change "fewer than two runs" to "exactly one run" for the compare
    message, add the zero-run case explicitly (no Compare form and no compare message), and say
    in the first scenario that the selects list the runs in the history's page order (newest
    first), not in the order the AC enumerates them.

### Finding 5 — Dependency-note accuracy: all three stories cite BSB-25-PENDING-2 for `runs.skills_commit_sha`, whose owner is BSB-25-PENDING-1, and PENDING-2/-3 omit the "BSB-29 has no stories yet" caveat

- **Severity:** Advisory
- **Stories touched:** BSB-35-PENDING-1, BSB-35-PENDING-2, BSB-35-PENDING-3 (cross-epic:
  BSB-25-PENDING-1, BSB-25-PENDING-2, BSB-29)
- **Evidence:**
  - Each story's Notes list "on BSB-25-PENDING-2 for `runs.skills_commit_sha`"
    (`stories.md:119-120`, `:213-214`, `:295-296`).
  - BSB-25-PENDING-1 owns the field: "This story owns the resolver, the freeze of
    `runs.skills_commit_sha`" (`BSB-25/_epic/stories.md:95`), and its acceptance criterion writes
    the SHA (`:54`). BSB-25-PENDING-2 itself says "Depends on BSB-25-PENDING-1 for
    `runs.skills_commit_sha`" (`:188`). BSB-33-PENDING-1, reading the same field, cites both
    PENDING-1 and PENDING-2 (`BSB-33/_epic/stories.md:109`).
  - PENDING-1 uniquely records that BSB-29's records exist as requirements even though "their
    stories are written later in the fan-out" (`stories.md:121-123`); PENDING-2 and PENDING-3 cite
    BSB-29 for `runs.final_verdict` and `runs.verification` without that caveat
    (`stories.md:214-216`, `:293-297`), and `docs/product/epics/BSB-29/` does not exist.
- **What is missing/ambiguous/contradictory:** The producer citation points at the packager, which
  only reuses the SHA and itself waits on PENDING-1; a sequence or a reader following it treats
  PENDING-2 as the prerequisite and may believe PENDING-2 writes the field. The PENDING-2/-3
  BSB-29 citations read as if that epic's read contract already existed, which the sequence stage
  cannot assume.
- **Question (if a person must decide):** None; the ownership is already stated by BSB-25.
- **Proposed change:**
  - **BSB-35-PENDING-1, -PENDING-2 and -PENDING-3:** cite **BSB-25-PENDING-1** for
    `runs.skills_commit_sha`; keep BSB-25-PENDING-2 only for the `skill_bundles` row if a story
    needs it (these three read only the SHA).
  - **BSB-35-PENDING-2 and -PENDING-3:** copy PENDING-1's one-sentence note that BSB-29 has no
    stories yet and that the records are a cross-epic dependency recorded for the sequence stage.
  - No acceptance-criteria change.

### Finding 6 — Cross-epic read-contract drift: the history and compare collapse BSB-33's two "no checks" states into one "Checks: unavailable"

- **Severity:** Advisory
- **Stories touched:** BSB-35-PENDING-1, BSB-35-PENDING-2, BSB-35-PENDING-3 (cross-epic:
  BSB-33-PENDING-2)
- **Evidence:**
  - PENDING-1: "A NULL `verification`, **or** one without a readable non-empty `checks` array,
    renders the check section as `Checks: unavailable`" (`stories.md:43-47`), and its AC asserts
    "Checks: unavailable" for a run with `verification NULL` (`:82-85`).
  - PENDING-2: when either run lacks readable checks, the comparison falls back to a single
    "Checks" row with "Checks: unavailable" (`stories.md:244-249`); PENDING-3 repeats the same
    fallback for its zero-flip case (`stories.md:306-312`).
  - BSB-33-PENDING-2, the shape owner the BSB-35 header cites (`stories.md:15-17`), distinguishes
    the two states on the same `runs.verification` value: a NULL verification renders **"No check
    results recorded."** (`BSB-33/_epic/stories.md:148-151`) and a present object without a
    readable checks array renders **"Check results unavailable."** (`:153-156,187-190`).
- **What is missing/ambiguous/contradictory:** The same run shows one label in the history/compare
  and a different, more precise one in its run report, and the summary views cannot distinguish
  "verification never ran" from "the verification record is unreadable". PENDING-1's verdict line
  often disambiguates the NULL case ("Verdict: not run"), but a partial record with
  `final_verdict` set and no checks arrays is still flattened.
- **Question (if a person must decide):** None; the read contract already exists in BSB-33.
- **Proposed change:**
  - **BSB-35-PENDING-1, -PENDING-2 and -PENDING-3:** adopt BSB-33-PENDING-2's two labels — "No
    check results recorded." for a NULL verification and "Check results unavailable." for a
    present but unreadable record — in the history row, the compare fallback and the flip
    fallback; update the affected ACs. Alternatively, if the summary really intends one label,
    state that collapse and why in PENDING-1's Notes and have PENDING-2/-3 say they reuse it,
    rather than leaving the two contracts to drift.
  - No change to BSB-33-PENDING-2 — it is the source of the vocabulary.

## Open questions

1. **Compare-table check identity (Finding 1).** Is a check whose `id` is the same but whose
   `level` differs between the two compared runs the same check for flip purposes? If yes, which
   level is displayed in the row label (each column's own level, or one canonical level)? If no,
   how is the pair rendered and is the count still zero? Who owns the "check ids are unique within
   a run" guarantee PENDING-3 relies on — BSB-33-PENDING-2's read contract, BSB-29's persistence,
   or a new statement in these stories? (PENDING-2 `stories.md:234-238`; PENDING-3
   `stories.md:299-305`; BSB-33-PENDING-2 `BSB-33/_epic/stories.md:176-180`; BSB-29 has no
   stories.)
2. **History scope (Finding 2).** Does FR-104's "every run of a skill" mean every run across all
   the author's projects, or every run recorded in the current project? If author-wide, which
   access rule authorizes it and which story owns the aggregation? If project-scoped, should the
   PRD/epic say so? And should the history include in-flight and re-verification rows, or only
   completed runs as `epics.md:1247` says? (`stories.md:29-52,78-85`; `PRD.md:178`;
   `epics.md:1247,1266`; BSB-22-PENDING-3's membership rule `BSB-22/_epic/stories.md:204-212`.)
3. **Accessibility ownership and sequence (Finding 3).** Does BSB-38 stay open and get sequenced
   after BSB-35 so it can audit the Later history and compare surfaces, or does BSB-35 own the
   accessibility acceptance criteria for its own two pages? (`stories.md:113,208,290`;
   `epics.md:1407,1409-1432,1435-1436`; `PRD.md:262`; `docs/product/epics/BSB-38/` absent.)

## Proposed changes

**BSB-35-PENDING-1 (Findings 2, 4, 5, 6).**
- Scope decisions: state the confirmed history scope (project-wide or author-wide) and whether
  in-flight/re-verification rows are included as answered decisions, not only as a rationale; on
  the project-scoped answer, keep the existing ACs and qualify the epic/PRD wording in the
  cross-epic follow-up.
- ACs: add an in-flight-run scenario with its exact rendering (if all states stay); add to the
  empty-history scenario that neither the compare form nor "Two runs are needed to compare." is
  rendered; adopt BSB-33's two "no checks" labels (or record the deliberate collapse).
- Notes: cite BSB-25-PENDING-1 (not -PENDING-2) for `runs.skills_commit_sha`.

**BSB-35-PENDING-2 (Findings 1, 2, 4, 5, 6).**
- Notes: make the check row identity the check `id`; display each column's own level beside its
  status; define the same-id/different-level case; add a matching scenario.
- ACs: first scenario — list the select options in the history's page order (newest first);
  "fewer than two runs" → "exactly one run", plus an explicit zero-run assertion.
- Scope decisions/Notes: state that the form and comparison read the same project-scoped,
  all-state set as the history (per the Open question 2 answer).
- Notes: cite BSB-25-PENDING-1 for `runs.skills_commit_sha`; add PENDING-1's note that BSB-29 has
  no stories yet; adopt the two "no checks" labels (or reuse PENDING-1's stated collapse).

**BSB-35-PENDING-3 (Findings 1, 2, 5, 6).**
- Notes: state explicitly that flip identity is the check `id`; define whether a level change is a
  flip (per the Open question 1 answer) and add that case to the scenarios; name the owner of the
  uniqueness guarantee.
- Notes: state that the compare set is the same project-scoped, all-state history set.
- Notes: cite BSB-25-PENDING-1 for `runs.skills_commit_sha`; add the BSB-29-has-no-stories caveat;
  adopt the two "no checks" labels (or reuse PENDING-1's stated collapse).
- No new route and no new record; the story still only extends PENDING-2's rendering.

**Cross-epic follow-ups for the revise pass (not edits this review makes):**
- **BSB-33-PENDING-2** (and **BSB-29** when written): state that check ids are unique within
  `runs.verification.checks`, or define duplicate-id handling (Finding 1 / Open question 1).
- **`docs/product/PRD.md` FR-104 and `docs/product/epics.md` BSB-35** (`:1247,1266`): qualify the
  history scope per Open question 2 and reconcile "completed runs" with the all-state behaviour
  the stories implement.
- **`docs/product/epics.md` BSB-35/BSB-38 Notes:** record the accessibility ownership and
  sequencing decision from Open question 3.

**Not proposed:** no new entity, column, endpoint, service or external integration; no change to
the history ordering rule, the membership 403 rule, the run-report link, the retention behaviour
(BSB-34 already leaves the `runs` row and its verification columns), or the flip definition beyond
the level-identity clarification.

## Architecture impact

None. Every value the three stories render is already on the `runs` row in ADR SK-001 §9 or in the
`runs.verification` object whose read contract BSB-33-PENDING-2 defines, and the compared run
report route already belongs to BSB-33. The two guarantees this report asks for — check-id
uniqueness within a run and the accessibility obligations of the two new surfaces — are contract
and scope decisions for the story revision, not a need for a new entity, field, endpoint or
external integration. No design change is required before `sdlc-plan-stories-write` can apply the
proposals.

## Requirement coverage check

| Requirement | PRD source | Mapped story | AC evidence | Verdict |
|---|---|---|---|---|
| FR-104 — the skill history lists every run of a skill with its commit SHA, input branch, verdict and checks | `PRD.md:178` | BSB-35-PENDING-1 | "Every run of the skill is listed newest first with its commit, input branch, verdict and checks"; "A failed run with no verification is listed as not run with checks unavailable"; "A skill with no runs shows an empty history"; the non-member 403 scenario (`stories.md:77-100`) | Covered, subject to Finding 2 (scope of "every run") and Finding 6 (checks wording) |
| FR-105 — the compare view shows two runs side by side | `PRD.md:179` | BSB-35-PENDING-2 | "The history page offers a comparison of its two most recent runs"; "Two runs are shown side by side with their commit, input branch, verdict and checks"; the incomplete, same-run, cross-skill, other-project and non-member refusals (`stories.md:163-196`) | Covered, subject to Finding 1 (check-row identity) and Finding 4 (empty/one-run state) |
| FR-106 — the compare view highlights checks that flipped between the two runs | `PRD.md:180` | BSB-35-PENDING-3 | "A pass-to-fail and a fail-to-pass check are highlighted with their direction"; "A check present in only one run is not a flip"; "A run with unavailable checks produces no flips" (`stories.md:266-279`) | Covered, subject to Finding 1 (level identity) and Finding 6 (unavailable wording) |

- `epic-map.json` assigns BSB-35 exactly FR-104, FR-105 and FR-106, and those three IDs still match
  `PRD.md`'s current wording and Release column (`Later`) — no traceability drift after
  decomposition.
- No requirement is claimed by two stories: each of the three stories covers exactly one FR, and
  the coverage table at `stories.md:54-60` cites acceptance criteria that genuinely exercise its
  requirement. PENDING-2's compare form is added to PENDING-1's page but claims no FR-104
  behaviour, and PENDING-3 adds no route or record.
- `epic-map.json` maps no NFR to BSB-35, so there is no epic-assigned NFR to check here; the
  cross-cutting NFR-012/FR-130-to-FR-136 obligation that does apply to these two web surfaces is
  Finding 3. The session and membership NFRs (NFR-002, NFR-003) are handled by the named BSB-18
  dependency and the 403 scenarios in all three stories.

## Dependency-note sanity check

- **Every named prerequisite exists.** The story set names BSB-18 (the session and gate),
  BSB-22-PENDING-1 and -PENDING-3, BSB-24-PENDING-1, BSB-25-PENDING-1 and -PENDING-2,
  BSB-26-PENDING-1 and -PENDING-3, BSB-29, BSB-33-PENDING-2 and BSB-34; all are real epic/story
  entries. BSB-27, BSB-30 and BSB-37 are named only in "Out of scope" and exist as published epics.
- **Accuracy issue.** All three stories cite BSB-25-PENDING-2 for `runs.skills_commit_sha`, but
  BSB-25-PENDING-1 owns the resolver and the freeze, and BSB-25-PENDING-2's own Notes depend on
  PENDING-1 for that field (Finding 5). BSB-33-PENDING-1, reading the same field, cites both.
- **Missing caveat.** BSB-29 has no story folder; PENDING-1 records that its requirements exist as
  a later fan-out, PENDING-2 and -PENDING-3 do not (Finding 5).
- **Reciprocity is otherwise consistent.** PENDING-3's Notes name PENDING-2 as its prerequisite for
  the comparison table and route; PENDING-2's out-of-scope and Notes name PENDING-3 as the owner of
  the flip marker and summary. PENDING-1's out-of-scope names PENDING-2 and -PENDING-3 for the
  compare view, and PENDING-2's Notes say the history rows, ordering and empty state remain
  PENDING-1's. No story claims a sibling depends on it without that sibling agreeing.
- **Cross-epic sequencing is otherwise sound.** BSB-35 is Later and all its data producers
  (BSB-24 to BSB-29, BSB-33, BSB-34) are MVP or earlier, so the reads are legitimate; the only
  sequencing question is BSB-38's MVP accessibility pass preceding BSB-35's Later surfaces
  (Finding 3 / Open question 3). No build order is proposed here — that is
  `sdlc-plan-epic-sequence`'s job.
