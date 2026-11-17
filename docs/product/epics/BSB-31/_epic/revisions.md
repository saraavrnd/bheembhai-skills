# Revisions — BSB-31 (Static security scanning)

## Pass 1 — 2026-11-17 (epic-review returned changes_requested)

**Report applied:** `docs/product/epics/BSB-31/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step. The hand-off carried no gate
answers to the report's **Open questions** (1–9), so the report's own **Proposed changes** were
applied to the named stories and every choice is recorded under **Choices recorded** below. Each
proposed change names a remedy that is applyable inside `stories.md` without changing the story
set, the requirement IDs, `epic-map.json`, the epic text, the PRD or ADR SK-001. Findings whose
remaining action is outside this epic (BSB-24/BSB-25/BSB-27/BSB-30/BSB-33/BSB-36/BSB-21 and the
PRD wording) are listed under **Still open**.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools were not exposed in this
session (no `mcp__atlassian__*` tool and no MCP server connection), so the configured site was
queried read-only over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 with "Issue does not exist or you do not have permission to see it.", matching
`PRD.md` section 8 and the review's Context loaded; no issue content is assumed from that lookup.
The run's epic `BSB-31` was read read-only from the same site and returned HTTP 200: summary
"Static security scanning", type Epic, status To Do, labels `FA-11`/`MVP`, no parent, no sub-tasks
and no issue links, with a description matching the BSB-31 section of `epics.md` and reiterating
the static-scan scope. That epic is the subject of this pass. No Jira write was attempted.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| 1 — FR-076's "before every run" call has no owner | Blocking | BSB-31-PENDING-1, -2, -4, -6 (cross-epic BSB-24, BSB-25, BSB-27) | **PENDING-1 Notes** now state the run-start flow is BSB-24's and that it invokes the route for the run's project and exact `skills_commit_sha` **after BSB-25 has packed the bundle at that SHA and before the agent container launches**; the packed bundle is the precondition (a missing row is the HTTP 409 AC), the returned `verdict` is the value BSB-27's FR-055 refusal consumes and BSB-30's FR-069 readiness reads, and BSB-24/-25/-27's own stories must name the call and its position. **PENDING-2, PENDING-4 and PENDING-6 Notes** each state they are callers of the same `POST /api/builds/{id}/scans/static` path with the same after-packaging/before-launch order, and add no second entry point. |
| 2 — epic DoD packaging gate owned by no requirement or story | Blocking | BSB-31-PENDING-1, BSB-31-PENDING-3 (cross-epic BSB-25, BSB-30) | **PENDING-1 Notes** now say BSB-31 supplies only the verdict: no FR mapped to BSB-31 assigns a packaging refusal, packaging refusal belongs to the verifier checks FR-071 to FR-073 under BSB-30, FR-055 (BSB-27) refuses the run and FR-069 (BSB-30) reads the verdict for Ready, and the epic DoD sentence must have its owner/requirement fixed in BSB-25/BSB-30 or be removed. **PENDING-1 Out of scope** and **PENDING-3 Notes** are aligned to the same statement; neither story claims a packaging requirement. |
| 3 — verdict function has no consistent owner; PENDING-1/PENDING-3 cycle | Blocking | BSB-31-PENDING-1, -2, -3, -5, -6 | Chosen owner: **PENDING-3**. Its Notes now state the function's input (scanner report plus the bundle's `.skillspector-baseline.yaml`), its output (`verdict`, `verdict_reasons`, the `scan_findings` rows), its callers (PENDING-1, -2, -5, -6, -7) and the direction: at runtime PENDING-1 depends on PENDING-3 for the function while PENDING-3 depends on PENDING-1 only for the record contract and never calls the route/service; neither story may ship a second implementation. **PENDING-1** adds the same dependency and rewords its Out of scope from "pass/fail rules beyond recording" to "the verdict rules themselves … this story asserts that output but defines no rule". **PENDING-2** adds the PENDING-3 dependency for a newly created scan. **PENDING-5** extends its dependency to the rendered `verdict`. **PENDING-6** states each verdict is produced by PENDING-3's function through PENDING-1's service. |
| 4 — reuse identity includes `skills_commit_sha` in PENDING-1 but not PENDING-2; cross-project reuse only in prose | Blocking | BSB-31-PENDING-1, -2, -5 | Chosen key: content-only. **PENDING-1 Notes** now define the identity/reuse key as `skill` + `stage` + `bundle_sha256` + `scanner_version`; `skills_commit_sha` is provenance only and the same bundle bytes at a new SHA reuse the row. **PENDING-2 Notes** state the key is content-only with `skills_commit_sha` and `build_id` as provenance. Two scenarios added to **PENDING-2**: "The same bundle content at a new commit reuses the completed result" and "A request from a different build and project reuses the completed result". **PENDING-5** gains the scenario "A scan reused by a different build and project renders from the same URL". |
| 5 — catalog reviewer cannot open the only scan report route; no epic owns a reviewer view | Blocking | BSB-31-PENDING-5, -7 (cross-epic BSB-18, BSB-33, BSB-36) | **PENDING-5 Notes/Out of scope** now state the authoring route's access rule (BSB-18 signed-in skill-builder check only; a non-member gets HTTP 403), that this gated URL cannot be the FR-111 link the PRD's reviewer can open, and that **no epic currently owns** a stable reviewer-facing scan-report view or its access rule — BSB-33's stable view is the run report and BSB-36 only links the scan reports; the view must be added by BSB-36 (or BSB-33) with an access rule that is not the authoring-interface gate, or the PRD's reviewer assumption corrected. The story adds no second route. **PENDING-7** rewords the actor to a builder team member maintaining the scan and says the catalog reviewer consumes the parity evidence through the catalog pull request, not a builder screen; parity ACs unchanged. |
| 6 — parity test calls an undefined service entry point and creates build-less scans | Advisory | BSB-31-PENDING-1, -7 | **PENDING-1 Notes** now define one direct bundle-fixture service entry point (packed bundle fixture plus pinned scanner version/digest, no build or project) of which the HTTP route is a thin caller, and state `scans.build_id` is nullable/NULL for scans created that way. **PENDING-7** cites that entry point, its input, and the `build_id` NULL rule; the parity AC's Then now asserts `build_id NULL`. |
| 7 — synchronous scan vs NFR-001's 60-second preparation budget | Advisory | BSB-31-PENDING-1, -4 (cross-epic BSB-25, PRD NFR-001/G4) | Chosen boundary: the static scan is a separate synchronous gate with its own fixed 600-second ceiling, **outside** BSB-25's 60-second / 5 MB non-model bundle-preparation budget. **PENDING-1 and PENDING-4 Notes** state the budget, that a cache-miss run start can wait up to ten minutes while a reuse hit adds no scan time, and that NFR-001's "run preparation" wording and BSB-25 must be reconciled to say so. |
| 8 — PENDING-5 has no AC for the failed/timeout state | Advisory | BSB-31-PENDING-4, -5 | **PENDING-5** gains the scenario "A failed scan shows its failure reason instead of an in-progress state": state `failed`, verdict `fail`, NULL score/recommendation and `failure_reason "Scan exceeded the ten-minute limit."` renders "Verdict: FAIL" and "Scan failed: Scan exceeded the ten-minute limit." and not "Scan in progress"/score/recommendation. Its Notes fix the template "Scan failed: " + `failure_reason`, naming both the timeout string and the no-report string from PENDING-1. **PENDING-4 Notes** cross-reference the rendered timeout string. |
| 9 — PENDING-6 adds a control to BSB-21's build page without naming the dependency or access rule | Advisory | BSB-31-PENDING-6 (cross-epic BSB-19, BSB-21) | **PENDING-6 Notes** now depend on BSB-21 for the build page `GET /builds/{id}`, its head SHA and its access rule; the story adds the control to that page and does not own it, and a signed-in `skill-builders` group member can open it. The Dave scenario now states Dave is a current `skill-builders` group member, so the HTTP 200 is tied to BSB-21/BSB-18's rule. The project selector and disabled-state AC are unchanged. |

**Minor attribution alignment (report's Dependency-note sanity check, no finding number).**
PENDING-1 and PENDING-6 now cite BSB-22-PENDING-1 for **defining** the shared
project-membership check and BSB-22-PENDING-3 for its **run-start application**, matching
BSB-22-PENDING-1's Notes. No design or requirement change.

### Choices recorded (no gate answer supplied)

1. **Run-start owner and position (Finding 1 / Open question 1).** BSB-24's run start invokes the
   route, after BSB-25 packs the bundle at the requested SHA and before the agent container
   launches; BSB-27's FR-055 refusal and BSB-30's FR-069 readiness consume that same verdict. This
   is the only order consistent with PENDING-1's packed-bundle precondition. If a person instead
   assigns the invocation to BSB-27's preflight, that preflight must run after BSB-25's packaging;
   BSB-27's "before a bundle or branch is prepared" guidance still needs correction either way.
2. **Packaging gate (Finding 2 / Open question 2).** The packaging gate is **not** owned by
   BSB-31: no mapped FR assigns it and the only packaging-refusal requirements (FR-071 to FR-073)
   belong to BSB-30. BSB-31 supplies the verdict only. Keeping the epic DoD sentence therefore
   requires BSB-25 or BSB-30 to add the requirement and story; otherwise the sentence should be
   removed or narrowed to the run gate. The cross-epic action is recorded below.
3. **Verdict-function ownership (Finding 3 / Open question 3).** PENDING-3 owns the function;
   PENDING-1 calls it and records its output; PENDING-2 calls it for a newly created scan;
   PENDING-5 renders its `verdict`/`verdict_reasons`; PENDING-6 reaches it through PENDING-1's
   service; PENDING-7 uses it in the parity test. Its input/output are fixed in PENDING-3's Notes.
   The apparent cycle is resolved as a runtime direction (PENDING-1 → PENDING-3) plus a
   record-contract dependency (PENDING-3 → PENDING-1), with no second implementation allowed.
4. **Reuse key (Finding 4 / Open question 4).** Content-only: `skill` + `stage` + `bundle_sha256`
   + `scanner_version`; `skills_commit_sha` and `build_id` are provenance. Cross-project and
   cross-build reuse are intended and are now asserted by acceptance criteria in PENDING-2 and
   PENDING-5.
5. **Reviewer-facing scan report (Finding 5 / Open question 5).** BSB-31 does **not** add a
   reviewer-facing route: no FR mapped to BSB-31 covers one, and the report already assigns a
   stable view to BSB-33/BSB-36 as a cross-epic gap. PENDING-5's authoring route keeps its BSB-18
   gate and the Notes now say explicitly that this URL cannot be the reviewer's FR-111 link.
   BSB-36 (or BSB-33) must add the view and its access rule, or PRD section 2's "does not use the
   authoring interface" must change.
6. **Parity seam (Finding 6 / Open question 6).** The scan service exposes a direct
   bundle-fixture entry point with no build/project, and `scans.build_id` is nullable (NULL for a
   direct/parity scan). The HTTP route is a thin caller of the same entry point.
7. **Scan budget vs NFR-001 (Finding 7 / Open question 7).** The scan is outside the 60-second
   non-model bundle-preparation budget and has its own fixed 600-second ceiling; the run start
   waits synchronously. On a cache miss the run start can wait up to ten minutes; the PRD/NFR-001
   and BSB-25 wording must be reconciled to state the boundary.
8. **Failed-state report text (Finding 8 / Open question 8).** `GET /scans/{id}` for state
   `failed` shows "Verdict: FAIL" and "Scan failed: " + the row's `failure_reason`, never "Scan in
   progress" and never a score/recommendation; the timeout and no-report strings are fixed above.
9. **Build-page host (Finding 9 / Open question 9).** The "Security check (static only)" control
   is delivered on BSB-21's `GET /builds/{id}` page under BSB-21's access rule (BSB-18's authoring
   gate); PENDING-6 adds the control and does not own the page.

### Still open (cross-epic follow-ups, not applied in this pass)

These are outside `docs/product/epics/BSB-31/_epic/`; this skill may not edit another epic's
stories or the epic/PRD text.

1. **BSB-24 / BSB-25 / BSB-27 (Finding 1).** Their stories must name the static-scan invocation
   and its position after packaging and before agent launch, and BSB-27's implementation guidance
   must stop placing the precondition "before a bundle or branch is prepared", which the scan's
   packed-bundle input makes impossible. BSB-24 and BSB-27 should consume the returned verdict
   without recomputing it.
2. **BSB-25 / BSB-30 (Finding 2).** Own the packaging gate if the epic DoD keeps it (new FR and
   story/AC), or remove/narrow the BSB-31 epic DoD packaging sentence. No requirement currently
   assigns it.
3. **BSB-36 / BSB-33 and PRD section 2 (Finding 5).** Own a stable reviewer-facing scan-report view
   and its access rule, or correct the PRD's statement that the catalog reviewer does not use the
   authoring interface. FR-111 links the scan reports, but no epic owns a view the reviewer can
   open.
4. **BSB-25, PRD NFR-001/G4 (Finding 7).** Agree that the static scan is a separate synchronous
   gate outside the 60-second non-model bundle-preparation budget, or change NFR-001/BSB-25 to include
   it and define the fallback when a cache-miss scan exceeds 60 seconds.
5. **BSB-21 (Finding 9).** Its future stories must own `GET /builds/{id}`, its head SHA, its
   access rule and the slot where this control is rendered.
6. **Rejection of any recorded choice.** Each choice above names the exact story sections to change
   if a person decides the other branch. No unresolved question blocks building the seven stories
   as revised.

### Coverage re-check

Complete and unchanged. BSB-31 still has 7 stories — PENDING-1 (FR-076, NFR-005), PENDING-2
(FR-077), PENDING-3 (FR-078, FR-079, FR-080, FR-081), PENDING-4 (FR-087, FR-088), PENDING-5
(FR-089, FR-154, FR-155), PENDING-6 (FR-092) and PENDING-7 (FR-091) — covering all 14 requirements
mapped to BSB-31 in `epic-map.json`, with no foreign requirement and no duplicate claim. No story
key, title, requirement mapping or estimate changed. `story-map.json` changed only summary strings
so they match the revised contracts; `requirement_ids` are untouched.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md`, `story-map.json` and this
  `revisions.md`. Nothing outside `docs/product/epics/BSB-31/_epic/` was touched, and no Jira write
  was made (authoring only, per ADR-035).
- **Scenario counts:** PENDING-1 has 5 (unchanged); PENDING-2 now has 7 (two added — same content
  at a new commit, different build/project); PENDING-3 has 6 (unchanged); PENDING-4 has 3
  (unchanged); PENDING-5 now has 7 (two added — failed state, cross-build/project reuse render);
  PENDING-6 has 5 (unchanged); PENDING-7 has 4 (unchanged). No scenario was removed and no existing
  assertion was weakened.
- **Blocking findings 1–5 are addressed in the stories** by naming one run-start position, one
  verdict-function owner and contract, one content-only reuse key, one failed-state text, and by
  correcting the reviewer-facing handoff. Their remaining actions are the cross-epic follow-ups
  above; none blocks building BSB-31's seven stories as revised.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set with the current story text.
  If it returns changes_requested, the next revise pass applies the new report the same way.

## Pass 2 — 2026-11-17 (automated verifier rejected Pass 1)

**Report applied:** the verification report on Pass 1's artifacts, check `no_template_residue`
(`builtin:md_no_placeholders`), verdict `changes_requested` — `stories.md` line 445 contained the
angle-bracketed placeholder text `<failure_reason>` in BSB-31-PENDING-5's Notes. No epic-review
finding and no gate answer changed in this pass; the story set, the requirement mapping and every
acceptance criterion are exactly as Pass 1 left them.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools are still not exposed in
this session (no `mcp__atlassian__*` tool and no MCP server connection), so the configured site was
re-queried read-only over its REST API (GET only; no Jira write).
`GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 "Issue does not exist or you do not have
permission to see it.", matching `PRD.md` section 8 and the Pass 1 note; no issue content is
assumed from that lookup. `GET /rest/api/3/issue/BSB-31` returned HTTP 200: summary "Static
security scanning", type Epic, status To Do, labels `FA-11`/`MVP`, description matching the BSB-31
section of `epics.md`. BSB-31 remains the epic this pass revises. No Jira write was attempted.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| `no_template_residue` — a `<slot>`-style placeholder remained in the PENDING-5 Notes | Blocking (verifier) | BSB-31-PENDING-5 | Rewrote the failed-state sentence so the failure text is described in prose and a template string rather than an angle-bracketed slot: the page shows "Verdict: FAIL" and the template "Scan failed: " followed by the row's `failure_reason`, never "Scan in progress" and never a score or recommendation. The concrete timeout text (BSB-31-PENDING-4) and no-report text (BSB-31-PENDING-1) are unchanged. |

### Still open

Unchanged from Pass 1. The cross-epic follow-ups listed under Pass 1's "Still open" are outside
`docs/product/epics/BSB-31/_epic/` and were not touched in this pass. No epic-review finding is
newly open, and no recorded choice from Pass 1 was reopened.

### Coverage re-check

Complete and unchanged. BSB-31 still has 7 stories covering all 14 requirements mapped to it in
`epic-map.json`; no story key, title, requirement ID or estimate changed. Only `stories.md`'s
PENDING-5 Notes prose changed, so `story-map.json` needs no update.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md` and this `revisions.md`. Nothing outside
  `docs/product/epics/BSB-31/_epic/` was touched, and no Jira write was made (ADR-035).
- **Placeholder sweep:** `stories.md` now has no template-brace, `TODO`, `TBD`, `FIXME`, `XXX` or
  angle-bracketed slot token anywhere. Scenario counts are unchanged.
- **Next pass:** the verifier re-runs on the corrected set; `sdlc-plan-epic-review` and
  `sdlc-tracker-sync` follow as before.

## Pass 3 — 2026-11-17 (automated verifier rejected Pass 2: vertical slices and unchanged story map)

**Report applied:** the verification report on Pass 2's artifacts, verdict `changes_requested`,
with two failing checks: `story_map` "artifact did not change since precheck", and judge criterion
`vertical_slices` — `BSB-31-PENDING-7` was an internal parity-test/verification slice rather than a
user-visible product capability (its Notes said it owned the parity test and its AC was that the
test reports "4 of 4 bundles match"), and `BSB-31-PENDING-3` was framed as owning one verdict
function, a technical-layer description. No epic-review finding and no gate answer changed in this
pass.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP server is configured in `.mcp.json`,
but this session again exposed no `mcp__atlassian__*` tool, so the configured site was queried
read-only over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 "Issue does not exist or you do not have permission to see it.", matching the
PRD section 8 note and Passes 1–2; no issue content is assumed from that lookup. `SkillBuilder-2` is
the PRD's work-item umbrella; the epic decomposed here is `BSB-31`. `GET
/rest/api/3/issue/BSB-31` returned HTTP 200: summary "Static security scanning", type Epic, status
To Do, labels `FA-11`/`MVP`, and a description whose scope includes the platform-parity requirement.
No Jira write was attempted.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| `vertical_slices` — PENDING-7 is an internal parity test, not a user-visible slice | Blocking (verifier) | BSB-31-PENDING-3, BSB-31-PENDING-7 | **PENDING-7 was removed as a story.** Its requirement FR-091 is now an acceptance criterion of the verdict slice, **BSB-31-PENDING-3**: a new scenario, "The verdict matches the platform's for the same content and pinned scanner version", asserts the verdict the author receives for each of four baseline bundles equals that bundle's recorded `platform_verdict`, with the pinned `scanner_version` and `image_digest` on every scan row. PENDING-3's Story statement now names this user-visible outcome, and its Notes consume the platform baseline as an external prerequisite (no internal test story owns it). PENDING-1's direct bundle-fixture entry point (with `build_id` NULL) remains and is cited by that scenario. |
| `vertical_slices` — PENDING-3 described as owning one verdict function | Blocking (verifier) | BSB-31-PENDING-3, BSB-31-PENDING-1, BSB-31-PENDING-4, BSB-31-PENDING-6 | **PENDING-3 is reframed as an author-visible outcome:** its title is now "Fail a static scan with a specific reason when its content is unsafe or incompletely scanned", its Story statement is author-first, and each acceptance criterion now asserts the scan response `verdict` the author receives in addition to the durable `scans`/`scan_findings` rows. The Notes no longer say the story "owns the one verdict function"; they say it **defines the pass/fail rules the scan applies**, applied once, with no caller re-deriving them. The same wording fix removed "verdict function" from PENDING-1's Out of scope, PENDING-1's dependency paragraph, PENDING-4's Notes and PENDING-6's Notes. |
| `story_map` — artifact did not change since precheck | Blocking (verifier) | `story-map.json` | The map now has **6 stories** (PENDING-7 removed), FR-091 moved from PENDING-7 to PENDING-3, and the PENDING-1 and PENDING-3 summaries rewritten to match the revised contracts. Every requirement ID and key that remains is unchanged. |

### Coverage re-check

Complete. BSB-31 now has 6 stories covering all 14 requirements mapped to it in `epic-map.json`:
PENDING-1 (FR-076, NFR-005), PENDING-2 (FR-077), PENDING-3 (FR-078, FR-079, FR-080, FR-081,
FR-091), PENDING-4 (FR-087, FR-088), PENDING-5 (FR-089, FR-154, FR-155) and PENDING-6 (FR-092).
No foreign requirement is claimed. The coverage summary in `stories.md` maps FR-091 to PENDING-3's
new parity scenario. PENDING-3's estimate changed from 3 to 5 to reflect the added parity outcome;
no other estimate changed.

### Still open (cross-epic follow-ups, not applied in this pass)

Unchanged from Pass 1 and still outside `docs/product/epics/BSB-31/_epic/`: BSB-24/BSB-25/BSB-27
must name the static-scan invocation and its position; BSB-25/BSB-30 must own or drop the packaging
gate in the epic DoD; BSB-36/BSB-33 must own a reviewer-facing scan-report view (or PRD section 2
corrected); BSB-25 and PRD NFR-001/G4 must reconcile the 60-second budget with the scan's own
600-second ceiling; BSB-21 must own the build page, its head SHA and access rule; BSB-37's and
BSB-31's existing review reports still name the removed PENDING-7 as historical text and are not
edited here because another epic's artifacts and the review report are outside this skill's write
scope.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md`, `story-map.json` and this `revisions.md`.
  Nothing outside `docs/product/epics/BSB-31/_epic/` was touched, and no Jira write was made
  (ADR-035).
- **Scenario counts:** PENDING-1 5 (unchanged); PENDING-2 7 (unchanged); PENDING-3 7 (the six
  existing rules scenarios now also assert the returned verdict, plus the new parity scenario);
  PENDING-4 3 (unchanged); PENDING-5 7 (unchanged); PENDING-6 5 (unchanged). Every story now opens
  with an author-visible outcome and has at least one unhappy-path or refusal scenario where one
  plausibly exists.
- **Placeholder sweep:** `stories.md` has no template-brace, `TODO`, `TBD`, `FIXME`, `XXX` or
  angle-bracketed slot token.
- **Next pass:** the verifier re-runs on the revised set; `sdlc-plan-epic-review` and
  `sdlc-tracker-sync` follow as before.
