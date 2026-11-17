# Revisions — BSB-22 (Test projects & membership)

## Pass 1 — 2026-11-17 (epic-review returned changes_requested)

**Report applied:** `docs/product/epics/BSB-22/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step (upstream commit `dcb3fb6`) of run
`42864b5b-aeee-478b-8b7f-56dea592ee04`. The hand-off carried no gate answers: the run context's
`settled_decisions` records `answered: 0`, and the report's **Open questions** 1 and 2 are
therefore unanswered. Per Step R of `sdlc-plan-stories-write`, Findings 1 and 2 were not applied —
they each require a product/architecture decision that this skill has no authority to guess.
Findings 3, 4 and 5 carry no open question and were applied.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools were not exposed in this
session, so the configured site was queried read-only over its REST API (GET only; no Jira write).
`GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 "Issue does not exist or you do not have
permission to see it", matching `PRD.md` section 8 and the review's Context loaded; no issue
content is assumed from that lookup. The run's epic `BSB-22` was read from the same site and
returned HTTP 200: summary "Test projects & membership", type Epic, status To Do, labels
`FA-4`/`MVP`, no parent and no sub-tasks, with a description matching the BSB-22 section of
`epics.md`. That epic is the subject of this pass.

### Findings applied

- **Finding 3 — cross-story guard ownership (Advisory; BSB-22-PENDING-2 and BSB-22-PENDING-4).**
  Applied as proposed:
  - **BSB-22-PENDING-2**, Notes: the claim that the story defines "the shared owner guard every
    project-administration route uses" is narrowed to "the member-management use of one shared
    owner check"; the Notes now state that BSB-22-PENDING-4 owns the integration-management use,
    and that the check is membership first, then `role = "owner"`, parameterised by the
    resource-specific denial message — "Only the project owner can change project members." here
    and "Only the project owner can change integrations." on PENDING-4's integration routes.
  - **BSB-22-PENDING-4**, Notes: the story now uses "that same shared owner check rather than a
    second implementation", owns the integration-management use and its denial message, and the
    two-check-order paragraph is attributed to "the shared owner check". Its two-check order and
    acceptance criteria are unchanged.
  - `story-map.json`: PENDING-2's summary now says "through the shared member-management owner
    check"; PENDING-4's says "through the shared owner check using the integration-management
    message" instead of "the shared owner-only integration guard".
- **Finding 4 — epic-wide scope boundary: how a user reaches the project surfaces (Advisory;
  BSB-22-PENDING-1, -2 and -4).** Applied as proposed:
  - **BSB-22-PENDING-1**, new acceptance scenarios: "The projects list links to the create form"
    (GET `/projects` renders "Your projects" and a "New project" link to `/projects/new`) and "The
    project page shows the owner the member and settings links" (GET `/projects/7` renders an
    "Add member" link to `/projects/7/members/new` and a "Settings" link to
    `/projects/7/settings`). Its Notes now state that, as the host pages, this story owns those
    entry points and that a non-owner member sees neither project-page link.
  - **BSB-22-PENDING-2**, new acceptance scenario: "The owner sees a remove control on each
    non-owner member row" (GET `/projects/7` renders, on Bob's member row, a "Remove" control that
    submits POST `/projects/7/members/43/delete`, and no "Remove" control on Ada's own owner row).
    Its Notes now name the project page as the route to the "Add member" form and the per-row
    "Remove" control.
  - **BSB-22-PENDING-4**, Notes: states that the settings page is reached from the project page via
    the "Settings" link defined by BSB-22-PENDING-1, and that this story does not own that link.
  - `story-map.json`: PENDING-1's summary no longer asserts the untested "members-only ... from the
    author's projects list" behaviour; it now names the create-form link and the owner's
    "Add member"/"Settings" entry points, matching its acceptance criteria.
- **Finding 5 — membership-check reuse lists omit BSB-32 (Advisory; BSB-22-PENDING-1 and
  BSB-22-PENDING-3).** Applied as proposed:
  - **BSB-22-PENDING-1**, Notes: the reuse list now reads "BSB-24, BSB-31, BSB-32, BSB-33 and
    BSB-37 reuse it."
  - **BSB-22-PENDING-3**, Notes: now names "BSB-31's standalone scans, BSB-32's full-scan entry
    point, BSB-33's reports and BSB-37's command line reuse it."

### Still open (no gate answer supplied)

These findings each ask a question only a person or an earlier stage can answer. They were
deliberately not applied, per Step R of the skill.

1. **Finding 1 — cross-epic access rule for the report views (Blocking; BSB-22-PENDING-1 and
   BSB-22-PENDING-3; cross-epic BSB-31, BSB-32, BSB-33, BSB-36).** Should the stable run and scan
   report views linked from a catalog pull request be readable outside the builder authoring gate
   and the project-membership check, as `PRD.md` section 2's catalog reviewer and `epics.md` BSB-33
   step 6 imply? If yes, what authorizes the reviewer (a signed share link, a separate read-only
   access rule, or a public view), and which of BSB-31/BSB-32/BSB-33 owns it? Until answered, the
   two stories keep the unqualified claim that BSB-33's reports reuse the project-membership check
   and that BSB-31's scan surface does too; the only Finding 1-adjacent change applied is Finding
   5's addition of BSB-32.
2. **Finding 2 — future mutation-route ownership (Blocking; BSB-22-PENDING-3 and BSB-22-PENDING-4;
   cross-epic BSB-23, BSB-24).** Should BSB-22 own minimal guarded `POST /projects/7/runs` and
   `POST /projects/7/integrations` routes that BSB-24 and BSB-23 extend, or should the two denial
   ACs move to BSB-24/BSB-23 while BSB-22 tests the guard only on its own GET pages? If BSB-22 owns
   them, what is each route's request contract and guard order? The answer decides who builds the
   route skeletons and what `epics.md`'s BSB-23/BSB-24 stories must adopt. PENDING-3's
   "run creation and input selection are not part of this story" sentence and its
   `POST /projects/7/runs` denial AC, and PENDING-4's "representative guarded route" wording, are
   unchanged pending the answer.

### Coverage re-check

Unchanged and complete. BSB-22 still has 4 stories — BSB-22-PENDING-1 (FR-023, FR-024), -2
(FR-025, FR-026), -3 (FR-027) and -4 (FR-028) — covering all six requirements mapped to BSB-22 in
`epic-map.json`, with no foreign requirement and no duplicate claim. No story key, title, story
statement, estimate, requirement ID or `requirement_ids` entry changed; `story-map.json` changed
only the PENDING-1, PENDING-2 and PENDING-4 summary strings.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md`, `story-map.json` and this
  `revisions.md`. Nothing outside `docs/product/epics/BSB-22/_epic/` was touched; no Jira write was
  made (authoring only, per ADR-035).
- **Scenario counts:** BSB-22-PENDING-1 now has 5 Gherkin scenarios (two added), PENDING-2 has 8
  (one added), PENDING-3 has 5 and PENDING-4 has 4 (both unchanged). No scenario was removed and no
  existing assertion was weakened.
- **The two Blocking findings still need gate answers.** The remaining actions for Finding 1 are
  cross-epic (BSB-31/BSB-32/BSB-33 report access and BSB-36's link contract); for Finding 2 they
  decide BSB-23/BSB-24's route contracts. Neither can be resolved inside BSB-22's stories without
  that decision.
- **Next pass:** once the gate answers for Open questions 1 and 2 are supplied, apply them to the
  named stories in the shape Step 3 produces, then update `story-map.json` only if coverage changes.

## Pass 2 — 2026-11-17 (re-run of the revise step; still no gate answers)

**Report applied:** the same `docs/product/epics/BSB-22/_epic/epic-review.md` report (verdict
CHANGES REQUESTED, 2026-11-16) whose commit is `dcb3fb6`, with the prior revise pass at `e11dad2`
as the step's own upstream commit. This is visit 3 of `sdlc-plan-stories-write` in run
`42864b5b-aeee-478b-8b7f-56dea592ee04` (the step was re-entered after the revise pass returned
`changes_requested`). The run context's `settled_decisions` still records `answered: 0`, so no
answer to **Open question 1** or **Open question 2** was supplied.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools are not exposed in this
session, so the configured site was queried read-only over its REST API (GET only; no Jira
write). `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 "Issue does not exist or you do
not have permission to see it", matching `PRD.md` section 8 and the prior passes; no issue
content is assumed from that lookup. The run's epic `BSB-22` returned HTTP 200: summary "Test
projects & membership", type Epic, status To Do, labels `FA-4`/`MVP`, no parent and no
sub-tasks. The run context (`ITEM`) binds this step to `BSB-22`.

### Findings re-checked (no new change made)

- **Findings 3, 4 and 5 (Advisory)** remain applied exactly as recorded in Pass 1: PENDING-2 and
  PENDING-4 share one owner check with two documented uses/messages; PENDING-1 renders the
  "New project" link and the owner-only "Add member"/"Settings" links; PENDING-2 asserts the
  per-row "Remove" control and names the project-page route; PENDING-4 states the settings page
  is reached via PENDING-1's link; and the BSB-32 reuse addition is present in PENDING-1 and
  PENDING-3. A comparison against the report's Proposed changes found nothing further to apply.
- **Findings 1 and 2 (Blocking)** remain deliberately unapplied. Each carries an unanswered
  question (Open questions 1 and 2) that this skill has no authority to guess. The affected
  sentences are unchanged: PENDING-1's and PENDING-3's unqualified BSB-31/BSB-33 reuse claims,
  and PENDING-3's `POST /projects/7/runs` / PENDING-4's `POST /projects/7/integrations` denial
  ACs and route-ownership wording.

### Outcome of this pass

No story, acceptance criterion, note, estimate, key or requirement mapping changed this pass;
only this entry was appended. Coverage remains complete: 4 stories cover all six requirements
mapped to BSB-22 (FR-023 to FR-028), with no foreign requirement. The two Blocking findings
still require the gate answers recorded under **Still open** above. Nothing outside
`docs/product/epics/BSB-22/_epic/` was touched, and no Jira write was made (authoring only, per
ADR-035).
