# Revisions — BSB-32 (LLM security scanning)

## Pass 1 — 2026-11-16 (automated verifier feedback)

**Report applied:** the step hand-off feedback for this run of `sdlc-plan-stories-write`. No
`epic-review.md` or `story-review.md` report existed on disk for BSB-32; the failing verifier
check below is applied as a revise pass.

**Work item `SkillBuilder-2`.** The Atlassian MCP tools are not exposed in this session, so the
configured site was queried read-only through its REST API (`GET /rest/api/3/issue/SkillBuilder-2`);
it returned HTTP 404 "Issue does not exist or you do not have permission to see it." This matches
`docs/product/PRD.md` section 8 and no issue content is assumed from the lookup. The epic being
decomposed was read read-only from the same site: `BSB-32` returned HTTP 200, summary "LLM security
scanning", status To Do, labels FA-12/MVP, no parent and no sub-tasks. No Jira write was attempted.

### Finding applied

- **Judge criterion `vertical_slices` — the seven-story set was a mixture of technical layers and
  three user-facing slices.** The old PENDING-2 was sandbox/environment/egress configuration with no
  user-visible surface, PENDING-3 owned "the full security scan service and route" and was the
  backend of the control PENDING-6 already exposed, PENDING-4 persisted unavailable and
  `failure_reason` rows while rendering was deferred to PENDING-5, and PENDING-7 was a proof story
  that added "no run-start behaviour of its own". The seven layers are replaced by four vertical
  journeys, each of which starts at a page the author or owner can open and ends at a page or state
  they can see:

  - **BSB-32-PENDING-1 — "Configure the LLM-scan model profile for a test project."** Retained
    essentially unchanged: the project owner sets the profile and tier on the project settings page
    at GET "/projects/7/settings", and the page renders the selection. Covers FR-163.
  - **BSB-32-PENDING-2 — "Run a full security check from the skill page and read the LLM report."**
    Absorbs the old PENDING-3 (static-before-LLM trigger and the full-scan route), PENDING-5 (the
    author report page with the model, advisory banner and located findings) and PENDING-6 (the
    "Full security check" control, project selector, membership refusal and per-scan override
    refusal), and adds the old PENDING-7's findings-do-not-block path as the journey's payoff. It
    begins at the build page control and ends at GET "/scans/12" and the run's verdict page. Covers
    FR-082, FR-085, FR-086, FR-090, FR-093, FR-156 and FR-163 (consumption).
  - **BSB-32-PENDING-3 — "Scan untrusted skill content without exposing project credentials or
    other services."** Absorbs the old PENDING-2, but is no longer a sandbox-configuration story:
    the journey starts with the author running a full check on a hostile bundle from the build page
    and ends at the rendered report, with the credential-absence, egress-allowlist and
    exact-bundle assertions as acceptance criteria inside that journey. Covers FR-083 and FR-084.
  - **BSB-32-PENDING-4 — "See why the LLM scan could not run and keep working."** Absorbs the old
    PENDING-4 and the old PENDING-7's unavailable and failed paths, and owns the rendering that was
    previously deferred to PENDING-5: each unavailable or failed reason is read on the same author
    report page, and the author then starts and finishes a run whose verdict is unaffected. Covers
    FR-139 and FR-085.
  - Old draft keys BSB-32-PENDING-5, -6 and -7 are removed. They were never published to Jira
    (`sdlc-tracker-sync` had not run), so no real issue key is orphaned. All ten requirement
    mappings are preserved; see the coverage re-check below.

### Coverage re-check

Every requirement mapped to BSB-32 in `epic-map.json` — FR-082, FR-083, FR-084, FR-085, FR-086,
FR-090, FR-093, FR-139, FR-156 and FR-163 — appears in at least one story's `requirement_ids`, and
no story claims a requirement outside the epic. 4 stories, 10 requirements, no gap and no foreign
requirement. FR-163 is configured by PENDING-1 and consumed by PENDING-2; FR-085 is exercised on
both the findings path (PENDING-2) and the unavailable/failed path (PENDING-4). The
`stories.md` coverage table records the acceptance criteria that cover each requirement.

### Still open

None.

### Notes for the next review

- **Story set reduced, coverage unchanged.** 4 vertical stories now replace the previous 7. Every
  story's acceptance criteria remain concrete enough to test directly, and each ends on a rendered
  page or page state rather than only a database row or network observation.
- **Cross-epic dependencies unchanged.** Run start/page and verification are BSB-24, BSB-26 and
  BSB-29; the static scan records and report route are BSB-31; project membership and the settings
  page are BSB-22; the model profile is BSB-23. The stories name these hand-offs in Notes rather
  than claiming their behaviour.

## Pass 2 — 2026-11-17 (epic review)

**Report applied:** `docs/product/epics/BSB-32/_epic/epic-review.md` (verdict CHANGES REQUESTED,
2026-11-16). The run was routed here by `sdlc-plan-epic-review` with status `changes_requested`.

**Work item `SkillBuilder-2`.** The Atlassian MCP tools are not exposed in this session, so the
configured site was queried read-only through its REST API. `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 ("Issue does not exist or you do not have permission to see it"), matching PRD
§9 and Pass 1; no issue content was assumed from that lookup. `GET /rest/api/3/issue/BSB-32`
returned HTTP 200 (summary "LLM security scanning", status To Do, labels FA-12/MVP, no parent,
sub-tasks or issue links), matching the BSB-32 section of `epics.md`. No Jira write was attempted.

**Gate answers:** none. The run hand-off records `settled_decisions.counts.answered = 0` and
`gate_follows = false`, so none of the review's four open questions has an answer.

### Findings applied

- **Finding 3 (Advisory) — `integrations` fixtures carried secret values.** BSB-32-PENDING-3: the
  Jira and source-control fixtures now carry `secret_ref "skill-builder/3/integration-6"` and
  `"skill-builder/3/integration-7"` instead of secret values, with "jira-test-token-9f2c" and
  "ghp-test-token-7a1d" held in the secret store at those paths. The credential-absence assertions
  are unchanged. BSB-23-PENDING-1 and BSB-23-PENDING-2 were added to the dependency Notes for the
  `secret_ref`/secret-store contract.
- **Finding 4 (Advisory) — overlapping `scans` extensions.** BSB-32-PENDING-2 is now the single
  owner of the LLM scan record shape (`stage "llm"`, nullable `model` and `model_profile_id`,
  nullable `verdict` for `stage "llm"`) and states that PENDING-3 and PENDING-4 consume it.
  BSB-32-PENDING-3 no longer claims the extension and depends on PENDING-2's shape. BSB-32-PENDING-4
  owns only the `state "unavailable"` addition and states the allowed states (`completed`,
  `unavailable`, `failed`) with `verdict` NULL in all three.
- **Finding 6 (Advisory) — silent run-report dependency and over-broad assertion.**
  BSB-32-PENDING-2 and BSB-32-PENDING-4 now name BSB-33 (run report page) and BSB-26 (run page
  layout) in Notes and Out of scope. The whole-page "no LLM-001" assertion is scoped to the run's
  verdict, verification result and final verdict sections, so an advisory Security tab could still
  show the finding.
- **Finding 8 (Advisory) — inconsistent LLM reuse wording.** BSB-32-PENDING-4 now says "No LLM scan
  is reused; a later full scan re-runs the LLM stage, including when a prior LLM scan completed."
  BSB-32-PENDING-2 keeps the absolute rule and cross-references PENDING-4.

### Still open (not applied — no answer at the gate)

These findings carry an open question and were **not** applied; applying them would require
guessing:

- **Finding 1 (Blocking) — LLM-scan model granularity.** Open question 1: is the scan model one
  fixed, owner-configured `(profile, tier)` pair per test project, or may the author choose a
  profile and tier per scan with the owner configuring only the default (ADR SK-001 §6b vs PRD §8/
  §9 and FR-163)? BSB-32-PENDING-1 and BSB-32-PENDING-2 are unchanged.
- **Finding 2 (Blocking) — combined Security tab ownership.** Open question 2: does BSB-32 add the
  combined Security tab acceptance criterion or a fifth story, or does BSB-33/BSB-26 own the tab?
  BSB-32-PENDING-2 and BSB-32-PENDING-4 are unchanged.
- **Finding 5 (Advisory) — owner guard for the scan-model route.** Open question 3: is
  `POST /projects/7/llm-scan-model` an "integration change" for BSB-22-PENDING-4's guard (keeping
  its exact message), or does it use BSB-22-PENDING-2's shared owner guard with a scan-specific
  message? BSB-32-PENDING-1 is unchanged.
- **Finding 7 (Advisory) — reviewer-facing LLM report.** Open question 4: must BSB-32 state the
  reviewer-view handoff in its stories, or is the epic-level summary sufficient and the viewer
  entirely BSB-33/BSB-36's deliverable? BSB-32-PENDING-2 and BSB-32-PENDING-4 are unchanged.

### Coverage re-check

Unchanged. All 10 requirements mapped to BSB-32 by `epic-map.json` remain covered by at least one
acceptance criterion, and no story claims a requirement outside the epic. No `story-map.json`
change was needed: no story key or requirement mapping changed, and the summaries remain accurate.

### Notes for the next review

- Four advisory corrections were applied; the two Blocking findings and two Advisory findings
  depend on answers that were not supplied at the gate.
- Finding 1 needs a product/architecture decision (PRD §8/§9 vs ADR SK-001 §6b) before
  BSB-32-PENDING-1/-2 can be rewritten. Finding 2 needs an ownership decision across
  BSB-31/BSB-32/BSB-33/BSB-26.
- The report's cross-epic follow-ups (BSB-31-PENDING-5, BSB-22-PENDING-4, BSB-31-PENDING-1,
  BSB-33/BSB-36 and ADR SK-001 §6b) are outside this skill's write scope and were not touched.

## Pass 3 — 2026-11-17 (automated verifier feedback: unchanged story map)

**Report applied:** the verification feedback for the preceding attempt of this step
(`sdlc-plan-stories-write`, verdict `changes_requested`, `feedback_active: true`). Its one failing
check was `story_map`: `docs/product/epics/BSB-32/_epic/story-map.json` had not changed since
precheck even though the revise pass had changed story content. No new review report and no gate
answers were supplied, so the four findings that carry open questions remain open (see below).

**Work item `SkillBuilder-2`.** The Atlassian MCP tools are not exposed in this session; the
configured site was queried read-only through its REST API. `GET /rest/api/3/issue/SkillBuilder-2`
still returns HTTP 404 ("Issue does not exist or you do not have permission to see it"), matching
PRD §8/§9 and Passes 1–2, and no issue content is assumed. `GET /rest/api/3/issue/BSB-32` still
returns HTTP 200 (Epic "LLM security scanning", status To Do, labels FA-12/MVP). No Jira write was
attempted.

### Changes made

- **`story-map.json` — summaries resynchronised with the revised stories** (the failing check).
  No story key or requirement mapping changed; the four summaries now state the scope the stories
  carry after Pass 2:
  - PENDING-1: names the existing settings page and the cleared-pair → unavailable outcome.
  - PENDING-2: records that it owns the LLM `scans` record shape and the absolute no-LLM-reuse
    rule (Finding 4, Finding 8).
  - PENDING-3: records that it consumes PENDING-2's record shape and that its fixtures use
    `secret_ref` paths backed by the secret store, not secret values (Finding 3, Finding 4).
  - PENDING-4: records the `state "unavailable"` addition and the `completed`/`unavailable`/
    `failed` enumeration with NULL verdict, and the no-reuse rule (Finding 4, Finding 8).
- **`stories.md` — two decision-free corrections from the report.**
  - BSB-32-PENDING-1 Notes now state that the "security scan" section is added to
    BSB-22-PENDING-4's existing settings page rather than a second settings page (the
    ownership-independent half of Finding 5; the guard/message choice is still open).
  - BSB-32-PENDING-4's dependency list now names BSB-18-PENDING-1 for the signed-in report-page
    gate, matching the prose (the minor formatting fix recorded in the report's
    dependency-note sanity check; no product decision involved).

### Coverage re-check

Unchanged. All 10 requirements mapped to BSB-32 by `epic-map.json` — FR-082, FR-083, FR-084,
FR-085, FR-086, FR-090, FR-093, FR-139, FR-156 and FR-163 — remain covered by at least one story,
and no story claims a requirement outside the epic. 4 stories, 10 requirements, no gap and no
foreign requirement. `stories.md`'s coverage table and `story-map.json` agree.

### Still open (not applied — no answer at the gate)

- **Finding 1 (Blocking) — LLM-scan model granularity.** Open question 1 has no answer. The
  owner-only fixed `(profile, tier)` pair in PENDING-1/PENDING-2 is unchanged; the ADR SK-001 §6b
  reconciliation is not written into the stories until the decision is made.
- **Finding 2 (Blocking) — combined Security tab ownership.** Open question 2 has no answer. No
  tab acceptance criterion or ownership handoff sentence was added.
- **Finding 5 (Advisory) — owner guard for the scan-model route.** Open question 3 has no answer;
  only the page-ownership half was clarified.
- **Finding 7 (Advisory) — reviewer-facing LLM report.** Open question 4 has no answer; the
  reviewer-view handoff remains only in the closing paragraph of `stories.md`.

### Notes for the next review

- The story map is now a faithful trace of the revised stories; the check that failed was the
  map staying stale, not a coverage change.
- The two Blocking findings need answers at the gate (or an earlier stage's decision) before
  PENDING-1/-2 can be rewritten; applying either branch now would guess.
- Cross-epic follow-ups from the report remain outside this skill's write scope and were not
  touched.
