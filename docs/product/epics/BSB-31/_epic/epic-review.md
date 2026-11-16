# Epic Review — BSB-31: Static security scanning

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-31-PENDING-1, BSB-31-PENDING-2, BSB-31-PENDING-3, BSB-31-PENDING-4, BSB-31-PENDING-5, BSB-31-PENDING-6, BSB-31-PENDING-7

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-31/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The run context (`BB_CONTEXT`) binds `ITEM.id` to `BSB-31` and records
  the upstream `sdlc-plan-stories-write` commit `644e397`; `SkillBuilder-2` is the PRD's parent
  work item, not a story in this epic. `SkillBuilder-2` has no Jira issue on the configured site:
  a read-only `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not exist or
  you do not have permission to see it"). The Atlassian MCP tools were not exposed in this
  session, so the same site's REST API was queried read-only (GET only; no Jira writes).
  `PRD.md` §8 and `epics.md`'s source note record the same result and ground the product in ADR
  SK-001.
- **The epic.** `GET /rest/api/3/issue/BSB-31` returned HTTP 200: Epic "Static security scanning",
  status To Do, labels `FA-11`/`MVP`, no parent, no sub-tasks and no issue links. Its description
  matches the BSB-31 section of `epics.md`. `epic-map.json` records BSB-31 under FA-11/MVP with
  FR-076 to FR-081, FR-087 to FR-089, FR-091, FR-092, FR-154, FR-155 and NFR-005.
- **All 7 stories in BSB-31**, from `stories.md` and `story-map.json` in one read each —
  BSB-31-PENDING-1 through -7 (the full set, not a sample). `story-map.json` maps the same 14
  requirement IDs, each to exactly one story. BSB-31 has no `revisions.md` and no prior
  `epic-review.md`.
- **`PRD.md`** — §2 target users (including the catalog reviewer, who "does not use the authoring
  interface"), §5 FA-11, §6 the fourteen FR rows, §7 NFR-001, NFR-005 and NFR-012, and §8's
  source note, external prerequisites and secrets constraints. G4's 60-second / 5 MB run
  preparation target was read with NFR-001.
- **`epics.md`** — the BSB-31 section (description, functional scope, implementation guidance, DoD,
  covered requirements, Notes), plus the sections of the epics that consume or supply this one:
  BSB-18 (authoring gate), BSB-19/BSB-21 (build and head SHA; BSB-19's Notes say the full build
  page is BSB-21's), BSB-22 (test projects and the shared membership check), BSB-24 (run start),
  BSB-25 (packaging), BSB-26 (execution), BSB-27 (run refusal and preflight), BSB-30 (readiness
  and packaging preflight), BSB-32 (LLM scan), BSB-33 (run report), BSB-36 (catalog submission),
  BSB-37 (CLI) and BSB-38 (accessibility, explicitly cross-cutting over the scan surfaces).
- **`docs/adr/SK-001-skill-builder.md`** — §1b (Ready), §2/§2a (pinned kit and image digest),
  §3 (Cognito and the per-request `skill-builders` gate), §4 (test project, membership and
  credentials), §5 (runs), §6b (security scan, including "static stage runs with no network" and
  "cached by content sha") and §9 (the data model, which names no `scans` or `scan_findings`
  table).
- **Other story sets checked:** BSB-18, BSB-19, BSB-20, BSB-22 and BSB-23 have stories on disk.
  BSB-21, BSB-24, BSB-25, BSB-26, BSB-27, BSB-30, BSB-32, BSB-33, BSB-36, BSB-37 and BSB-38 have
  epic definitions but no stories yet; their epic scope and Notes were read to tell a legitimate
  cross-epic dependency from an unowned one.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md` are
  not committed; the architecture-design step runs after planning, so ADR SK-001 is the design
  authority this pass can use. No `epic-sequence.md`/`.json` exists for BSB-31; no build order is
  computed here.

## Findings

### Finding 1 — FR-076's "before every run" call has no owner, and the consumer-side guidance contradicts the scan's input
- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-2, BSB-31-PENDING-4, BSB-31-PENDING-6.
  Cross-epic: BSB-24, BSB-25, BSB-27.
- **Evidence:**
  - PENDING-1's Notes say "The run-start path is BSB-24's; before it launches the agent container
    it must call this route for the run's project and SHA … BSB-24's epic does not currently name
    this call, so its run-start stories must adopt it for FR-076's 'before every run' to hold"
    (`stories.md:90-98`).
  - PENDING-1's acceptance criteria start from the caller: "Given … the run-start preflight …
    calls POST \"/api/builds/7/scans/static\"" (`stories.md:29-52`). PENDING-2 and PENDING-4 do the
    same (`stories.md:118-141`, `stories.md:256-269`). They prove the route's behaviour once it is
    called; no AC proves that every run start calls it.
  - BSB-24's epic functional scope and Notes (`epics.md:669-713`) cover branch/context/model
    selection and creating a run request for packaging; they never mention a static scan or
    `POST /api/builds/7/scans/static`.
  - BSB-27's implementation guidance says: "Add a preflight that rejects incompatible execution
    components **before a bundle or branch is prepared**, and add the static-scan precondition
    using the scanning epic's verdict function" (`epics.md:869-874`, emphasis added).
  - PENDING-1 cannot scan before a bundle exists: the route reads the `skill_bundles` row for the
    requested SHA and returns HTTP 409 "No packed bundle exists for commit 4f2c9a1." when there is
    none (`stories.md:49-52`, `stories.md:76-79`). BSB-25 owns packaging (`epics.md:730-739`) and
    its Notes say it supplies the pinned bundle to static scanning (`epics.md:771-776`).
  - `PRD.md` FR-076 says "before every run" (`PRD.md:150`); FR-055, owned by BSB-27, refuses the
    run when the static scan did not pass (`PRD.md:129`, `epics.md:896`).
- **What is missing/ambiguous/contradictory:** The gate's producer (BSB-31's route) and its
  refusal (BSB-27's FR-055) exist, but the invocation that connects them is owned by nobody. The
  only written instruction points at BSB-24, whose epic is silent; BSB-27's guidance instead puts
  the static-scan precondition before bundle preparation, which the scan's own input makes
  impossible. One implementer can put the check before packaging (always 409) while another puts
  it after packaging (the intended gate); either way, FR-076's "before every run" is not
  demonstrated.
- **Question (if a person must decide):** Which epic/story invokes
  `POST /api/builds/{id}/scans/static` before every run — BSB-24's run start or BSB-27's
  preflight — and at what point relative to BSB-25's packaging (after the bundle is packed, before
  the agent container launches)? Does FR-055's refusal consume the returned verdict at that same
  point?
- **Proposed change:**
  - **BSB-31-PENDING-1:** Keep the route contract and add an explicit sentence naming the caller
    and the required order: the run-start flow calls this route after BSB-25 packs the bundle at
    the requested SHA and before the agent container launches; the returned `verdict` is the value
    FR-055 refuses on. Name the consumer epic/story IDs once BSB-24/BSB-25/BSB-27 are decomposed.
  - **BSB-31-PENDING-2, -4, -6:** State that each is a caller of the same run-start/POST path (or
    of the same service) and that the call happens after packaging and before agent launch, so no
    story implies the scan can run before a bundle exists.
  - **Cross-epic follow-up (not applied here):** BSB-24, BSB-25 and BSB-27 must name the call and
    its position; reconcile BSB-27's "before a bundle or branch is prepared" wording with the
    scan's dependence on the packed bundle. This report does not compute a build order.

### Finding 2 — The epic's Definition of Done claims a packaging gate that no requirement or story owns
- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-3. Cross-epic: BSB-25, BSB-30.
- **Evidence:**
  - The epic's DoD says "Every run and **every packaged skill** is preceded by a static scan of
    the exact content, and a non-passing verdict blocks the run **and packaging**"
    (`epics.md:555-561`, emphasis added).
  - `epic-map.json` assigns BSB-31 the fourteen requirements listed above; none is a packaging
    gate. The only packaging-refusal requirements are FR-071 to FR-073 (verifier lint, verifier
    self-test, verifier range), and they are mapped to BSB-30, not BSB-31 (`PRD.md:145-147`,
    `epics.md:1032-1034`).
  - PENDING-1's Notes already record the hole: "the epic's Definition of Done says a non-passing
    verdict also blocks packaging, but no FR mapped to BSB-31 covers a packaging gate, BSB-25's
    epic does not name the static verdict, and the requirement list assigns packaging refusal only
    to the verifier checks FR-071 to FR-073" (`stories.md:100-104`). PENDING-3 repeats it
    (`stories.md:237-242`).
  - BSB-25's functional scope and DoD cover bundle preparation and its 60-second budget, not a
    static-scan packaging gate (`epics.md:730-759`). BSB-30's packaging preflight covers verifier
    lint, self-test and range (`epics.md:992-1004`); its FR-069 Ready check includes the static
    scan (`epics.md:994`), but Ready is not packaging.
- **What is missing/ambiguous/contradictory:** The epic promises a second hard gate (packaging)
  that no story claims and no FR assigns. Two implementers can reasonably conclude either that
  PENDING-1/-3 should reject packaging or that BSB-25/BSB-30 should — or that the sentence is
  satisfied by FR-055's run gate. The epic cannot meet its own DoD as written.
- **Question (if a person must decide):** Is a non-passing static verdict required to block
  packaging? If yes, which epic and FR own that gate — add it to BSB-31 (new story/AC and a
  requirement ID) or to BSB-25/BSB-30? If no, should the DoD's packaging sentence be removed or
  narrowed to the run gate (FR-055)?
- **Proposed change:**
  - **BSB-31-PENDING-1, -3:** Align both Notes with the answer. If BSB-31 owns the packaging
    gate, add the AC and the requirement ID; if not, state explicitly that this epic supplies
    only the verdict and that run refusal is FR-055 (BSB-27) and packaging belongs to the named
    other epic.
  - **Cross-epic follow-up (not applied here):** If the gate is assigned outside BSB-31, the
    owning epic's scope/stories must add it and the epic DoD wording must change. A new FR or
    `epic-map.json` change is outside this review's authority and needs a human/earlier-stage
    decision.

### Finding 3 — The one verdict function is owned by PENDING-3, but four sibling stories assert its output and two do not depend on it; the declared PENDING-1/PENDING-3 direction is circular
- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-2, BSB-31-PENDING-3,
  BSB-31-PENDING-5, BSB-31-PENDING-6.
- **Evidence:**
  - PENDING-1's Out of scope excludes "the pass/fail rules beyond recording what the scanner
    reports (BSB-31-PENDING-3)" (`stories.md:58-65`), yet its ACs assert `verdict: "pass"` for the
    clean report (`stories.md:29-32`, `stories.md:39-42`) and `verdict: "fail"` for the no-report
    failure (`stories.md:44-47`). Its Notes say it owns "the static scan service … and the
    synchronous `POST /api/builds/7/scans/static` route that every other caller uses" and that "a
    caller always receives a verdict" (`stories.md:73-75`), without naming PENDING-3 as a
    dependency.
  - PENDING-3's Notes say "This story owns the one verdict function every caller uses; no caller
    recomputes the verdict from a report" and "Depends on BSB-31-PENDING-1 for the scan record and
    BSB-31-PENDING-2 for when a result is computed or reused" (`stories.md:223-235`).
  - PENDING-2's Notes list only PENDING-1 (`stories.md:153-159`), but its ACs assert verdict
    `pass` for a newly created scan after changed content (`stories.md:123-126`), after a scanner
    version change (`stories.md:128-131`) and after replacing a failed row (`stories.md:133-136`)
    — all of which require PENDING-3's verdict function.
  - PENDING-5's Notes depend on PENDING-3 for `verdict_reasons` only (`stories.md:344-350`), but
    its ACs assert the page text "Verdict: PASS"/"Verdict: FAIL" (`stories.md:307-320`).
  - PENDING-6's Notes name BSB-18, BSB-22 and BSB-25 and say the route/service is PENDING-1's
    (`stories.md:411-428`), but its ACs assert `verdict: "pass"` for each successful scan
    (`stories.md:376-399`), which transitively needs PENDING-3.
  - PENDING-7 already declares the dependency on PENDING-3 for the verdict function
    (`stories.md:475-484`), showing the intended direction — the other callers do not.
- **What is missing/ambiguous/contradictory:** There are two plausible readings. PENDING-1 owns
  the service and computes a verdict (making PENDING-3's "one verdict function" claim false and
  duplicating the rules); or PENDING-3 owns the function (making PENDING-1's ACs, PENDING-2's
  new-scan ACs and PENDING-6's ACs dependent on PENDING-3, which none of those three declares).
  PENDING-3 depends on PENDING-1 and PENDING-2, while PENDING-1 and PENDING-2's new-scan paths
  depend on PENDING-3 — a dependency cycle that the per-story notes never acknowledge. The
  function's interface (scanner report plus the scanned bundle's `.skillspector-baseline.yaml`
  in; `state`, `verdict`, `verdict_reasons` and `scan_findings` out) is also never stated, so
  each caller could shape it differently.
- **Question (if a person must decide):** Does PENDING-1 own the verdict function (with PENDING-3
  owning only the rule definition and its tests), or does PENDING-3 own it (with PENDING-1
  recording only the scanner report/state and leaving `verdict` to PENDING-3)? What is the
  function's exact input and output, and which story may assert a verdict before PENDING-3 is
  built?
- **Proposed change:**
  - **BSB-31-PENDING-1:** Choose one owner. If PENDING-3 owns the function, add "Depends on
    BSB-31-PENDING-3 for the verdict function" and remove the Out-of-scope sentence that disclaims
    the rules while asserting verdicts; if PENDING-1 owns it, reword PENDING-3's ownership claim
    and state the shared function in PENDING-1. State the function's input/output in one sentence.
  - **BSB-31-PENDING-2:** Add "Depends on BSB-31-PENDING-3 for the verdict function on a newly
    created scan" and keep the reused-row ACs as row copies.
  - **BSB-31-PENDING-3:** State that PENDING-1, PENDING-2, PENDING-5, PENDING-6 and PENDING-7 call
    its function, and give the function's input (report plus the bundle's
    `.skillspector-baseline.yaml`) and output (`state`, `verdict`, `verdict_reasons`,
    `scan_findings`); resolve the PENDING-1/PENDING-3 direction explicitly.
  - **BSB-31-PENDING-5:** Extend its PENDING-3 dependency from `verdict_reasons` to the `verdict`
    the page renders.
  - **BSB-31-PENDING-6:** Add the PENDING-3 dependency (or state it inherits it through PENDING-1's
    route); its ACs assert a verdict and must not appear independent of the function.
  - Same change for all five stories: one verdict function, one caller contract, one dependency
    direction.

### Finding 4 — The scan's reuse identity includes `skills_commit_sha` in PENDING-1 but excludes it in PENDING-2, and cross-project reuse is asserted only in prose
- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-2, BSB-31-PENDING-5.
- **Evidence:**
  - PENDING-1's Notes say "The scan record is content-addressed by `skill`, `skills_commit_sha`,
    `bundle_sha256`, `stage` and `scanner_version`" (`stories.md:78-81`).
  - PENDING-2's Notes say "This story owns the reuse key: a scan is reused only when `stage` is
    \"static\", `bundle_sha256`, `skill` and `scanner_version` all match … and the existing row's
    state is \"completed\"" (`stories.md:154-159`). `skills_commit_sha` is absent.
  - PENDING-2's Notes also say "Because a scan row carries no `project_id`, a completed result is
    reusable by any project whose run uses the same content and scanner version"
    (`stories.md:161-165`). PENDING-5 repeats that "a completed result reused by another build
    (BSB-31-PENDING-2) renders from the same URL" (`stories.md:353-355`).
  - PENDING-2's ACs cover an unchanged bundle, changed bundle content, a changed scanner version,
    a failed row and a completed failing row (`stories.md:118-141`). None has the same
    `bundle_sha256` at a different `skills_commit_sha`, and none reuses across a different build
    or project.
  - `PRD.md` FR-077 says a completed result is reused "when the content is unchanged"
    (`PRD.md:151`); ADR SK-001 §6b says the static check is "Cached by content sha"
    (`SK-001:300`).
- **What is missing/ambiguous/contradictory:** If `skills_commit_sha` is part of the identity, the
  same bytes committed twice (same `bundle_sha256`, different commit) are scanned twice, which
  contradicts PENDING-2's content-key Notes and FR-077's "content is unchanged". If it is not
  part of the identity, PENDING-1's sentence is wrong. The cross-project/cross-build reuse that
  both PENDING-2 and PENDING-5 rely on has no acceptance criterion, so a developer can add
  `project_id` or `build_id` scoping and still pass every AC.
- **Question (if a person must decide):** Is the scan identity/reuse key `skill` + `stage` +
  `bundle_sha256` + `scanner_version` (content-only), with `skills_commit_sha` recorded as
  provenance, or does `skills_commit_sha` also scope reuse? If content-only, should PENDING-2 add
  an AC for the same bundle at a new commit and for reuse by a different build/project, and should
  PENDING-5 add the matching render AC?
- **Proposed change:**
  - **BSB-31-PENDING-1:** Reword the identity sentence to match PENDING-2: content identity is
    `skill` + `stage` + `bundle_sha256` + `scanner_version`; `skills_commit_sha` is recorded on
    the row for traceability but does not by itself force a new scan. If the answer is the
    opposite, correct PENDING-2 instead.
  - **BSB-31-PENDING-2:** Keep the same key wording and add ACs for (a) the same `bundle_sha256`
    at a different `skills_commit_sha` and (b) a request from a different build/project reusing
    the completed row, if cross-project reuse is intended.
  - **BSB-31-PENDING-5:** Add an AC (or state in Notes) that a scan reused by a different build
    renders from the same `GET /scans/{id}` URL; this is currently prose only.
  - Same change for all three stories: one reuse key and a test for the content-only case.

### Finding 5 — The catalog reviewer named as the scan's audience cannot open the only scan report route, and no epic owns a reviewer-facing view
- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-5, BSB-31-PENDING-7. Cross-epic: BSB-18, BSB-33, BSB-36.
- **Evidence:**
  - PENDING-5's Notes say "the report route is part of the authoring interface and is gated by
    BSB-18's signed-in skill-builder check only" and "It does not apply the project-membership
    check, because the same scan report is evidence linked from a catalog pull request (BSB-36,
    FR-111) and the PRD's catalog reviewer does not use the authoring interface. The
    reviewer-facing stable report view and its access rule belong to BSB-33/BSB-36"
    (`stories.md:351-362`). Its Out of scope repeats the handoff (`stories.md:341`).
  - `PRD.md` §2 defines the catalog reviewer as someone who "Consumes the catalog pull request and
    its linked run and scan reports; does not use the authoring interface" (`PRD.md:16`). FR-111
    requires the pull-request description to link the scan reports (`PRD.md:185`).
  - BSB-18's authoring gate requires a current `skill-builders` group member on every authoring
    page and API; a signed-in non-member receives HTTP 403 (`BSB-18/_epic/stories.md:176-212`).
    PENDING-5's route applies that gate, so a reviewer outside the group cannot open the link.
  - BSB-36's functional scope only says "Link the run report and the scan reports from the
    pull-request description" (`epics.md:1284-1295`); it defines no scan-report view or access
    rule. BSB-33's "stable report view that catalog submission can link to and that reviewers can
    read without the authoring interface" (`epics.md:1082-1083`) is the **run** report; BSB-33's
    covered requirements are FR-094 to FR-103, FR-140, FR-157 and FR-158, with no scan-report
    requirement (`epics.md:1091-1104`).
  - PENDING-7's story actor is "a **catalog reviewer**" (`stories.md:441`), but its ACs are
    build-time parity tests (`stories.md:445-463`); the reviewer performs no action and has no
    builder surface.
- **What is missing/ambiguous/contradictory:** PENDING-5 correctly identifies that the reviewer
  cannot use the authoring interface, then gates the only scan report behind the authoring
  interface anyway. The handoff names BSB-33/BSB-36, but neither epic owns a scan-report viewer:
  BSB-33's stable view is the run report, and BSB-36 only links the scan reports. The result is
  an FR-111 link that the named audience cannot open, and a reviewer actor in PENDING-7 with no
  usable interface. This is a scope hole at the epic boundary, not a single-story wording issue.
- **Question (if a person must decide):** Should the scan report have a stable reviewer-facing
  view readable without the authoring interface, and which epic owns it — BSB-36 (with its PR
  links) or a new story in BSB-31? If the catalog reviewer is expected to be a `skill-builders`
  member, PRD §2's "does not use the authoring interface" must change; if not, PENDING-5's
  authoring route cannot be the linked evidence and PENDING-7's reviewer actor has no surface.
- **Proposed change:**
  - **BSB-31-PENDING-5:** State the authoring route's access rule and hand off a stable
    reviewer-facing scan-report view *with its access rule* to a named epic; do not assert that
    BSB-33/BSB-36 already own it. If BSB-31 must supply it, add the route/AC and name the access
    rule (for example, a stable read-only URL whose access is not the authoring gate).
  - **BSB-31-PENDING-7:** Reword the story value/actor to the builder team (the parity test is
    build-time) or state that the catalog reviewer consumes the parity evidence through the
    catalog pull request, not through a builder screen. Keep the parity ACs unchanged.
  - **Cross-epic follow-up (not applied here):** BSB-36 (and BSB-33 if it owns the stable view)
    must add the scan-report viewer and its access rule, or the PRD's reviewer assumption must be
    corrected. Same change for PENDING-5 and PENDING-7: one reviewer-facing scan-report contract.

### Finding 6 — PENDING-7's parity test calls a service entry point that PENDING-1 never defines, and creates scan records with no build
- **Severity:** Advisory
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-7.
- **Evidence:**
  - PENDING-7's Notes say "The parity test calls the same scan and verdict service the HTTP route
    calls, directly with a bundle fixture, so it needs no build or project"
    (`stories.md:475-484`). Its AC says the test runs "the static scan service on each fixture
    bundle through the same scan and verdict path as POST \"/api/builds/7/scans/static\", called
    directly with the bundle fixture so no build or project is needed" and that "every resulting
    scan record carries scanner_version … and image_digest" (`stories.md:445-448`).
  - PENDING-1 owns the scan service and the HTTP route, but defines only the route's inputs —
    `project_id` and `skills_commit_sha` — and its lookup of the `skill_bundles` row
    (`stories.md:73-81`). It never defines a callable bundle-in service entry point.
  - PENDING-1's `scans` schema lists `build_id` (`stories.md:82-88`) without saying it is
    nullable, and every PENDING-1 AC uses build 7 (`stories.md:29-52`). PENDING-7 creates scans
    with no build at all.
- **What is missing/ambiguous/contradictory:** PENDING-7 assumes a test seam that PENDING-1 does
  not specify. An implementer can build PENDING-1's service as route-only, leaving PENDING-7 no
  way to call it, or make `build_id` NOT NULL, leaving PENDING-7 unable to create its fixture
  scans. The parity test is the epic's only evidence for FR-091, so this seam is part of the
  contract, not an optional refactor.
- **Question (if a person must decide):** Does the scan service expose a bundle-fixture entry
  point for the parity test, and is `scans.build_id` nullable for scans created without a build?
  If not, how does PENDING-7 run without a build or project?
- **Proposed change:**
  - **BSB-31-PENDING-1:** Define the service function (bundle fixture plus scanner
    version/digest in; scan result out) that the HTTP route and PENDING-7 both call, and state
    that `scans.build_id` is NULL for a direct/parity scan with no build.
  - **BSB-31-PENDING-7:** Cite that entry point and the nullable `build_id` instead of assuming
    them; keep the parity assertions unchanged.
  - Same change for both stories: one service contract and one nullability rule.

### Finding 7 — The synchronous static scan can occupy run start for up to ten minutes while NFR-001 promises 60-second non-model run preparation
- **Severity:** Advisory
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-4. Cross-epic: BSB-25 and the PRD's
  NFR-001/G4.
- **Evidence:**
  - PENDING-1 makes the call synchronous inside the run-start preflight: "A scan request returns
    only after the scan reaches `completed` or `failed`, so a caller always receives a verdict",
    and the run-start path "before it launches the agent container … must call this route"
    (`stories.md:73-75`, `stories.md:90-96`). Its AC has the preflight call the route and assert
    the scan result in the same response (`stories.md:29-32`).
  - PENDING-4 allows the scan to run for up to 600 seconds and fixes that limit with no override
    (`stories.md:256-269`, `stories.md:282-289`).
  - `PRD.md` NFR-001 says "Non-model run preparation completes within 60 seconds for a skill
    bundle of up to 5 MB" (`PRD.md:251`); G4 repeats the 60-second / 5 MB target as a 95%
    metric (`PRD.md:32`). `epic-map.json` assigns NFR-001 to BSB-25, whose functional scope and
    DoD repeat the 60-second budget (`epics.md:737`, `epics.md:754-759`).
- **What is missing/ambiguous/contradictory:** The static scan is non-model work that the run
  start waits for, but no story says whether it counts against NFR-001's 60-second preparation
  budget. On a cache miss, PENDING-1/PENDING-4 allow run start to block for up to ten minutes,
  while BSB-25's acceptance target says non-model preparation completes within 60 seconds. The
  cache in PENDING-2 makes the common path fast but does not resolve the first scan of new
  content.
- **Question (if a person must decide):** Is the synchronous static scan part of "non-model run
  preparation" for NFR-001/G4? If yes, what happens on a cache-miss scan that exceeds 60 seconds
  (fail the run start, queue the scan, run it asynchronously)? If no, what is the scan's own time
  budget, and should NFR-001 or BSB-25 state that the scan is outside the 60-second budget?
- **Proposed change:**
  - **BSB-31-PENDING-1 and -4:** State the scan's time budget and its relationship to NFR-001
    (included with a 60-second fallback behaviour, or excluded with its own stated budget). Keep
    the fixed ten-minute ceiling but make the run-start expectation explicit.
  - **Cross-epic follow-up (not applied here):** BSB-25 and the PRD's NFR-001 wording must agree
    with the chosen boundary. Same change for PENDING-1/PENDING-4: one scan-budget statement.

### Finding 8 — PENDING-5 has no acceptance criterion for the failed/timeout scan state that PENDING-4 creates
- **Severity:** Advisory
- **Stories touched:** BSB-31-PENDING-4, BSB-31-PENDING-5.
- **Evidence:**
  - PENDING-4 creates `scans` rows with state `failed`, verdict `fail`, `score` NULL,
    `recommendation` NULL and `failure_reason` "Scan exceeded the ten-minute limit."
    (`stories.md:256-269`). PENDING-1 creates the same shape for a scanner that writes no report,
    with `failure_reason` "Scanner exited with code 137 before writing a report."
    (`stories.md:44-47`).
  - PENDING-5's Notes say "BSB-31-PENDING-4 supplies the failed/timeout state this page must
    render" (`stories.md:344-350`).
  - PENDING-5's ACs cover a completed passing scan, a completed failing scan, a scan still
    `running`, and an unknown id (`stories.md:307-330`). There is no AC for state `failed`.
- **What is missing/ambiguous/contradictory:** The only non-completed state the page is tested
  against is `running`, whose expected text is "Scan in progress" with no score. A developer can
  implement "any non-completed row shows Scan in progress", and a timed-out or no-report scan
  will then be reported as in progress forever, with its `failure_reason` never shown. The Notes
  promise the failed state is rendered, but no AC holds it.
- **Question (if a person must decide):** What should `GET /scans/{id}` show for a scan with state
  `failed`, verdict `fail`, score/recommendation NULL and a `failure_reason` (timeout or no
  report)? Which exact text is shown, and is the `failure_reason` displayed?
- **Proposed change:**
  - **BSB-31-PENDING-5:** Add a failed-state AC asserting the page shows "Verdict: FAIL" and the
    agreed failure text (including the `failure_reason`) and does not show "Scan in progress";
    state the exact strings in the Notes.
  - **BSB-31-PENDING-4:** Cross-reference the same `failure_reason` string and state that PENDING-5
    renders it, so the two stories share one value.
  - Same change for both stories: one failed-state text contract.

### Finding 9 — PENDING-6 adds a control to BSB-21's build page without naming the dependency or the page's access rule
- **Severity:** Advisory
- **Stories touched:** BSB-31-PENDING-6. Cross-epic: BSB-19, BSB-21.
- **Evidence:**
  - PENDING-6 places the "Security check (static only)" control on `GET "/builds/7"`
    (`stories.md:376-394`) and calls it "the skill page" (`stories.md:414-416`). Its Notes list
    BSB-18, BSB-22, BSB-25, BSB-32, BSB-23/BSB-24 and BSB-37, but not BSB-21 (`stories.md:411-428`).
  - BSB-19's Notes say "the full build page with head and readiness is BSB-21's"
    (`BSB-19/_epic/stories.md:61`). BSB-21's epic owns the build page's head SHA and readiness
    status (`epics.md:341-350`); BSB-21 has no stories yet.
  - PENDING-6's AC has Dave — who has no `project_members` rows — open `GET "/builds/7"` and
    receive HTTP 200 (`stories.md:391-394`), but no story in this epic defines who may open a
    build page; that access rule belongs to BSB-21/BSB-18.
- **What is missing/ambiguous/contradictory:** PENDING-6 adds a control to a page this epic does
  not own and whose access rule is not yet defined. The dependency is silent, so an implementer
  can build a second build page in this story (duplicating BSB-21) or place the control on a page
  that does not yet exist. The AC's HTTP 200 for Dave also assumes an access rule no story states.
- **Question (if a person must decide):** Is the "Security check (static only)" control delivered
  on BSB-21's build page `GET /builds/{id}`, and should PENDING-6 depend on BSB-21 (FR-020) for
  the page and its access rule?
- **Proposed change:**
  - **BSB-31-PENDING-6:** Add "Depends on BSB-21 for the build page `GET /builds/{id}`, its head
    SHA and its access rule" to the Notes, and state that this story adds the control to that
    page rather than owning the page. Keep the control's project selector and the disabled-state
    AC.
  - **Cross-epic follow-up (not applied here):** BSB-21's stories must render the control. Same
    change for PENDING-6 and BSB-21: one host page.

## Open questions

1. **Run-start invocation (Finding 1).** Which epic/story invokes
   `POST /api/builds/{id}/scans/static` before every run — BSB-24's run start or BSB-27's
   preflight — and at what point relative to BSB-25's packaging? Does FR-055's refusal consume
   the verdict there?
2. **Packaging gate (Finding 2).** Does a non-passing static verdict block packaging, and if so
   which epic/FR owns it — BSB-31 (new story/AC and requirement ID), BSB-25 or BSB-30? If not,
   does the epic DoD drop the packaging sentence?
3. **Verdict function ownership (Finding 3).** Does PENDING-1 own the verdict function (with
   PENDING-3 owning the rules/tests), or does PENDING-3 own it (with PENDING-1 recording only the
   report/state)? What is its input/output, and how is the PENDING-1/PENDING-3 cycle resolved?
4. **Reuse key (Finding 4).** Is the scan reuse key content-only (`skill` + `stage` +
   `bundle_sha256` + `scanner_version`), with `skills_commit_sha` as provenance, or does the
   commit SHA also scope reuse? Is cross-project/cross-build reuse intended, and should PENDING-2
   and PENDING-5 test it?
5. **Reviewer-facing scan report (Finding 5).** Which epic owns a stable scan-report view that
   the catalog reviewer can read without the authoring interface, and what is its access rule —
   or is the reviewer also a `skill-builders` member (which would contradict PRD §2)?
6. **Parity test seam (Finding 6).** Does the scan service expose a bundle-fixture entry point,
   and is `scans.build_id` nullable for a scan with no build?
7. **Scan time budget vs NFR-001 (Finding 7).** Is the synchronous static scan part of the
   60-second non-model run-preparation budget? If yes, what happens when a cache-miss scan
   exceeds it? If no, what is the scan's own budget?
8. **Failed-state report text (Finding 8).** What exact text does `GET /scans/{id}` show for a
   failed (timeout or no-report) scan, and is its `failure_reason` displayed?
9. **Build-page host (Finding 9).** Is the static-only control delivered on BSB-21's
   `GET /builds/{id}` page, and should PENDING-6 depend on BSB-21 for that page and its access
   rule?

## Proposed changes

`docs/product/epics/BSB-31/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-31-PENDING-1** — Notes/ACs: name the run-start caller and its position after packaging
  and before agent launch (Finding 1); choose the verdict-function owner and declare the
  dependency or re-scope it (Finding 3); make the reuse identity content-only (or correct the
  sibling) (Finding 4); define the service entry point and nullable `build_id` (Finding 6); state
  the scan's time budget against NFR-001 (Finding 7); align the packaging-gate note with the
  decision (Finding 2).
- **BSB-31-PENDING-2** — Notes/ACs: state that it is a caller of the same run-start path (Finding
  1); add the PENDING-3 verdict dependency (Finding 3); keep the reuse-key wording consistent
  with PENDING-1 and add ACs for the same bundle at a new commit and for cross-build/project
  reuse if intended (Finding 4).
- **BSB-31-PENDING-3** — Notes/ACs: state the verdict function's input/output and its callers
  (PENDING-1, -2, -5, -6, -7), and resolve the PENDING-1/PENDING-3 direction (Finding 3); align
  the packaging-gate note with the decision (Finding 2).
- **BSB-31-PENDING-4** — Notes/ACs: state it is a caller of the same run-start path (Finding 1);
  state the scan's time budget against NFR-001 (Finding 7); cross-reference the failed-state
  `failure_reason` that PENDING-5 renders (Finding 8).
- **BSB-31-PENDING-5** — Notes/ACs: extend the PENDING-3 dependency to the rendered `verdict`
  (Finding 3); add the failed-state AC and exact text (Finding 8); add the cross-build reuse
  render AC if cross-project reuse is intended (Finding 4); correct the reviewer-facing
  scan-report handoff and access rule (Finding 5).
- **BSB-31-PENDING-6** — Notes/ACs: state it is a caller of the same run-start path (Finding 1);
  add the PENDING-3 dependency or say it inherits it through PENDING-1's route (Finding 3); add
  the BSB-21 build-page dependency and the page's access rule (Finding 9).
- **BSB-31-PENDING-7** — Notes/ACs: cite PENDING-1's service entry point and nullable `build_id`
  (Finding 6); reword the catalog-reviewer actor/value so it does not imply a reviewer interface
  (Finding 5).
- **`story-map.json`** — No requirement ID or story-set change. If Finding 4 changes the reuse
  key wording, PENDING-1/-2's summaries must match the chosen key; PENDING-2's summary already
  says "stage, content bundle and scanner version" and needs no change.

Cross-epic follow-ups (not applied in this pass; they need their own epic revisions or a human
decision):

- **BSB-24 / BSB-25 / BSB-27** — Name the static-scan invocation and its position after packaging
  and before agent launch; reconcile BSB-27's "before a bundle or branch is prepared" wording
  (Finding 1).
- **BSB-25 / BSB-30** — Own the packaging gate if the DoD keeps it, or remove the packaging
  sentence from BSB-31's DoD if the answer is no (Finding 2).
- **BSB-36 / BSB-33** — Own the stable reviewer-facing scan-report view and its access rule, or
  correct the PRD's reviewer assumption (Finding 5).
- **BSB-25 (and the PRD's NFR-001/G4)** — Agree the scan's budget boundary (Finding 7).
- **BSB-21** — Render the "Security check (static only)" control on the build page and state its
  access rule (Finding 9).
- **BSB-22** — Minor attribution alignment: PENDING-1 and PENDING-6 cite BSB-22-PENDING-3 for the
  shared project-membership check, while BSB-22-PENDING-1's Notes say that story *defines* the
  check and PENDING-3 *exercises* it on the run-start path. Cite PENDING-1 for the definition and
  PENDING-3 for the run-start application (no design or requirement change).

No change is proposed to `epic-map.json`, the requirement IDs, the story set, `sdlc-tracker-sync`
or Jira.

## Architecture impact

None. Every finding is a story-boundary, shared-contract, access-rule, performance-budget or
dependency-note issue. The only new persisted structures are the `scans` and `scan_findings`
records that PENDING-1 declares (`stories.md:82-88`); ADR SK-001 §9 names no scan table, and
PENDING-1 already says the later design stage must record them. No existing entity, field,
endpoint or integration in ADR SK-001 conflicts with the epic, and no new design decision is
required before `sdlc-plan-stories-write` (revise) applies this report.

## Requirement coverage check

All fourteen requirements mapped to BSB-31 are exercised by at least one acceptance criterion, and
no requirement is claimed by two stories in contradictory ways. The caveats below are the
findings above; none removes a requirement from the epic.

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-076 | BSB-31-PENDING-1 | "Unscanned content is scanned before the run-start preflight returns a verdict"; "The scan reads the requested commit's bundle, not a newer branch head". **Caveat:** both start from "the run-start preflight calls", so the every-run caller is unowned (Finding 1). |
| FR-077 | BSB-31-PENDING-2 | "An unchanged bundle and scanner version reuse the completed result"; "Changed bundle content starts a new scan"; "A different scanner version starts a new scan"; "A completed failing result is reused and stays failing". **Caveat:** the key omits `skills_commit_sha` here but includes it in PENDING-1, and no AC covers the same bundle at a new commit (Finding 4). |
| FR-078 | BSB-31-PENDING-3 | "A DO_NOT_INSTALL recommendation fails even with no critical finding". |
| FR-079 | BSB-31-PENDING-3 | "Any critical finding fails even with a non-blocking recommendation". |
| FR-080 | BSB-31-PENDING-3 | "Incomplete coverage fails even with no blocking recommendation and no critical finding". |
| FR-081 | BSB-31-PENDING-3 | "An accepted critical finding cannot clear the block"; "An accepted non-critical finding does not itself fail a clean scan". |
| FR-087 | BSB-31-PENDING-4 | "A scan still running at ten minutes is terminated and recorded as failed"; "The ten-minute boundary terminates a scan that has not finished". |
| FR-088 | BSB-31-PENDING-4 | The two timeout scenarios assert state "failed", verdict "fail" and `failure_reason` "Scan exceeded the ten-minute limit.". |
| FR-089 | BSB-31-PENDING-5 | "A completed passing scan shows its score, recommendation and coverage" ("Static scan score: 96"). |
| FR-091 | BSB-31-PENDING-7 | "The builder's verdict matches the platform's on a fixed corpus"; "A scanner version mismatch is reported rather than compared"; "A bundle with no platform baseline fails the parity test". **Caveat:** the test calls a service entry point and creates build-less scans that PENDING-1 does not define (Finding 6). |
| FR-092 | BSB-31-PENDING-6 | "A project member starts a static-only scan and no run is created"; "A non-owner member can start the scan"; "A signed-in author who is not a project member is refused"; "An author with no project membership has no project to scan for". **Caveat:** the control's build-page host and access rule are BSB-21's and are not named (Finding 9). |
| FR-154 | BSB-31-PENDING-5 | "A completed passing scan shows its score, recommendation and coverage" ("Recommendation: INSTALL"). |
| FR-155 | BSB-31-PENDING-5 | "Every finding is shown with severity, rule, file and line" (severity-descending table). |
| NFR-005 | BSB-31-PENDING-1 | "The static scanner container has no network access" (Docker network mode "none", dummy server receives 0 requests). |

Traceability notes: `epic-map.json` and `PRD.md` agree on all fourteen IDs and their wording;
`story-map.json` maps each ID to exactly the story above, with no duplicate or missing claim. No
FR/NFR wording drift was found between `epic-map.json`, `epics.md` and the current `PRD.md`. NFR-012
(accessibility) is a cross-cutting requirement explicitly owned by BSB-38, whose Notes name the
scan surfaces, so it is not a silent epic-wide NFR here. NFR-001 is BSB-25's requirement; the
static scan's relationship to it is Finding 7.

## Dependency-note sanity check

Mostly consistent within the epic; the cross-story/cross-epic mismatches are Findings 1, 3, 4, 5,
7 and 9, plus one minor attribution note.

- **Reciprocated within the epic:** PENDING-2/-3/-4/-5/-6's Out of scope name PENDING-1 and the
  siblings they exclude; PENDING-1's Out of scope names PENDING-2, -3 and -5; PENDING-2's Out of
  scope names PENDING-3 and -4; PENDING-3's Out of scope names PENDING-4 and -5; PENDING-4's Out
  of scope names PENDING-3 and -5; PENDING-5's Out of scope names PENDING-1, -3 and -4; PENDING-6's
  Out of scope names PENDING-1 and -5. All seven draft keys exist; no dependency note points at a
  non-existent story.
- **Missing verdict dependencies — Finding 3:** PENDING-1, PENDING-2 and PENDING-6 assert
  verdicts but do not declare PENDING-3; PENDING-5 declares PENDING-3 only for
  `verdict_reasons`, not `verdict`. PENDING-3's own dependency on PENDING-1/PENDING-2 while those
  stories depend on its verdict function is a cycle, not a real order.
- **Contradictory reuse identity — Finding 4:** PENDING-1's "content-addressed by … `skills_commit_sha`
  …" and PENDING-2's "reused only when `stage`, `bundle_sha256`, `skill` and `scanner_version`
  match" cannot both be the key.
- **One-sided cross-epic — Finding 1:** PENDING-1 says BSB-24 must call the route, but BSB-24's
  epic scope and Notes do not mention the scan; BSB-27's guidance instead places the precondition
  before bundle preparation, which PENDING-1's packed-bundle requirement makes impossible.
  PENDING-1's Notes are the only place the gap is written down.
- **Reciprocated cross-epic:** BSB-25's Notes say it supplies the bundle to static scanning
  (`epics.md:771-776`); BSB-27's Notes say it depends on the static verdict (`epics.md:903-904`);
  BSB-30's Notes say it depends on static scan state (`epics.md:1038-1043`); BSB-32's Notes say it
  depends on the static verdict (`epics.md:648-653`); BSB-37's Notes say it depends on the static
  scan service (`epics.md:1397-1402`); BSB-22-PENDING-1/PENDING-3 say BSB-31 reuses the shared
  membership check (`BSB-22/_epic/stories.md:64-68`, `:211`). PENDING-5's BSB-33/BSB-36 handoff
  is the exception: BSB-36 links the scan reports but owns no viewer (Finding 5).
- **Packaging gate — Finding 2:** BSB-25's scope and BSB-30's scope both omit a static-scan
  packaging gate, while BSB-31's DoD claims one. No epic's Notes reciprocate that claim.
- **Build-page dependency — Finding 9:** PENDING-6 uses `GET /builds/7` but does not name
  BSB-21, which BSB-19's Notes say owns the full build page; BSB-21 has no stories yet.
- **Minor attribution (no finding):** PENDING-1 and PENDING-6 cite BSB-22-PENDING-3 as the shared
  project-membership check's owner; BSB-22-PENDING-1's Notes say that story defines it and
  PENDING-3 exercises it. Cite PENDING-1 for the definition and PENDING-3 for the run-start
  application.
- **Ordering not computed:** no `epic-sequence.md`/`.json` exists for BSB-31; sequencing remains
  `sdlc-plan-epic-sequence`'s job. This pass records the dependency gaps and does not propose a
  wave or build order.

---

*On approval: `docs/product/epics/BSB-31/_epic/stories.md` is updated in place for
BSB-31-PENDING-1 through -7 (and the PENDING-1/-2 summary alignment in `story-map.json` only if
Finding 4 changes the reuse-key wording). No Jira keys exist yet for these draft stories, and no
Jira write is made in this pass. Next: `sdlc-plan-stories-write` (revise), then
`sdlc-plan-epic-sequence` and the per-story review for single-story concerns this epic-level pass
deliberately did not raise.*
