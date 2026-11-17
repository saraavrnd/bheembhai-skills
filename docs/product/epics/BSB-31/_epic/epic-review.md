# Epic Review — BSB-31: Static security scanning

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-17 · **Stories reviewed:** BSB-31-PENDING-1, BSB-31-PENDING-2, BSB-31-PENDING-3, BSB-31-PENDING-4, BSB-31-PENDING-5, BSB-31-PENDING-6

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-31/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The run context binds the target to epic `BSB-31`; `SkillBuilder-2` is
  the PRD's parent work item, not a story in this epic. `SkillBuilder-2` has no retrievable Jira
  issue: a read-only `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not
  exist or you do not have permission to see it"). The Atlassian MCP server is configured in
  `.mcp.json`, but no `mcp__atlassian__*` tools were exposed in this session, so the same site was
  queried read-only over REST (GET only; no Jira writes). `PRD.md` §8 (`:273-278`) and
  `epics.md`'s source note (`:110-119`) record the same result and designate the committed
  decomposition as the source. This review therefore judges the committed epic artifacts, not a
  Jira description.
- **Stories.** Read all six stories in `stories.md` and every entry in `story-map.json` in one
  pass: BSB-31-PENDING-1 (scan the exact run bundle before the run), -2 (reuse a completed result),
  -3 (fail with a specific reason and match the platform verdict), -4 (ten-minute timeout), -5
  (show the static scan report), -6 (standalone static-only scan). No PENDING-7 remains in either
  artifact; the coverage table at `stories.md:566-584` maps all fourteen requirements.
- **Requirements.** `epic-map.json` BSB-31 entry: FR-076, FR-077, FR-078, FR-079, FR-080, FR-081,
  FR-087, FR-088, FR-089, FR-091, FR-092, FR-154, FR-155, NFR-005. Read `PRD.md` §2 (target users,
  including the catalog reviewer at `:16`), the FA-11 requirements (`:150-166`, `:228-229`), FR-111
  (`:185`) and the NFR table (`:251`, `:255`). Read the BSB-31 epic section in `epics.md`
  (`:511-587`), including the functional scope, implementation guidance and the Goal / Definition
  of Done (`:555-561`).
- **Design / data.** Read `docs/adr/SK-001-skill-builder.md` §6b (security scan, `:284-315`) and
  §9 (data model, `:345-361`). No `architecture.md`, `data-model.md` or `api-contracts/` exists in
  `docs/` at this revision (the tree holds `docs/adr/`, `docs/product/` and `docs/skill-chain.md`),
  so the ADR is the design input;
  PENDING-1 already states that the data-model stage must record the new `scans` and
  `scan_findings` structures. Read `story-map.json`, `epic-map.json` and the BSB-31 section of
  `epics.md`.
- **Sibling epics checked for legitimate cross-epic dependencies.** `BSB-24` (run start; stories
  decomposed), `BSB-25` (packaging / `skill_bundles`; stories decomposed), `BSB-26` (run progress
  and page; stories decomposed), `BSB-32` (LLM scan; stories decomposed), `BSB-33` (run report;
  stories decomposed), `BSB-36` (catalog submission; stories decomposed), `BSB-37` (CLI; stories
  decomposed), `BSB-22` (project membership; stories decomposed), `BSB-38` (acceptance fixtures;
  stories decomposed). `BSB-21`, `BSB-27` and `BSB-30` have no `stories.md` yet, so only their
  epic sections in `epics.md` were read. Also read the existing `revisions.md` (Passes 1-3) and
  the previous `epic-review.md` to distinguish already-applied findings from current ones.
- **Prior pass.** The previous report (dated 2026-11-16, seven stories) was superseded by Passes
  1-3 of `sdlc-plan-stories-write`. This pass re-checks the revised six-story set against sibling
  epics that have since been decomposed; it does not repeat findings the revision demonstrably
  closed (the parity entry point, the PENDING-1/PENDING-3 direction, the failed-state report
  text, and the build-page host note are now consistent).

## Findings

### Finding 1 — Cross-epic dependency and caller contradiction: the every-run static scan is attributed to BSB-24's run start, while BSB-24 and BSB-25 assign it to BSB-27's preflight

- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-2, BSB-31-PENDING-4, BSB-31-PENDING-6.
  Cross-epic: BSB-24-PENDING-1, BSB-25-PENDING-1, BSB-25-PENDING-2, BSB-27 (epic; no stories yet).
- **Evidence:**
  - BSB-31-PENDING-1, Notes: "the run-start flow is BSB-24's, and it invokes this route for the
    run's project and the exact `skills_commit_sha` after BSB-25 has packed the bundle at that SHA
    and before the agent container launches" (`stories.md:118-120`); "BSB-24's, BSB-25's and
    BSB-27's own stories must name this call and its position when those epics are decomposed"
    (`stories.md:123-124`).
  - BSB-31-PENDING-2 repeats "BSB-24's run-start flow calls it after BSB-25 has packed the bundle"
    (`stories.md:219-221`); BSB-31-PENDING-4 repeats it verbatim (`stories.md:384-386`);
    BSB-31-PENDING-6 says "BSB-24's run-start preflight calls the same route" (`stories.md:557-558`).
  - BSB-24-PENDING-1 says the opposite: "Run start does not resolve or package the skill, create
    the run branch, scan or execute. … BSB-27's preflight calls BSB-31-PENDING-1's static-scan
    route for the run's project and resolved SHA … before BSB-26 launches the agent container, and
    BSB-27 refuses a run whose static verdict is not pass (FR-055)"
    (`BSB-24/_epic/stories.md:116-121`).
  - BSB-25-PENDING-1 agrees: "The static scan runs after this preparation because BSB-31-PENDING-1's
    route reads the `skill_bundles` row for the resolved SHA; BSB-27 owns the refusal when the
    verdict is not pass" (`BSB-25/_epic/stories.md:117-120`); BSB-25-PENDING-2 says "BSB-27's
    preflight, static scan and execution run after this story has set `prepared`"
    (`BSB-25/_epic/stories.md:304`).
  - BSB-27 has no `stories.md` yet. Its epic guidance still places the preflight "before a bundle
    or branch is prepared" (`epics.md:869-874`), which BSB-25-PENDING-1 already records as
    superseded by the packed-bundle input (`BSB-25/_epic/stories.md:117-119`). BSB-27 is the epic
    that owns FR-055's refusal.
- **What is missing/ambiguous/contradictory:** BSB-31's four run-start stories all name BSB-24's
  run start as the invoker, but BSB-24's own decomposed story explicitly says run start does not
  scan and assigns the call to BSB-27's preflight; BSB-25's stories agree with BSB-24. An
  implementer wiring the route per BSB-31 would put the call in BSB-24's request-creation flow,
  contradicting BSB-24-PENDING-1's scope. An implementer wiring BSB-27 would find BSB-31's note
  naming BSB-24. The statement that BSB-24/-25/-27 "must name this call … when those epics are
  decomposed" is stale for BSB-24 and BSB-25: both are decomposed, and both name BSB-27's
  preflight. The result is that FR-076's "before every run" invocation has no story-level owner
  that all three epics agree on.
- **Question (if a person must decide):** Which flow/story invokes
  `POST /api/builds/{id}/scans/static` before every run — BSB-24's run start or BSB-27's
  preflight — and does it run after BSB-25 sets the run's bundle prepared and before BSB-26
  launches the agent container? If the answer is BSB-24, BSB-24-PENDING-1's explicit "does not …
  scan" must be revised too; if the answer is BSB-27, BSB-31's four notes and BSB-27's epic
  "before a bundle or branch is prepared" wording must be corrected. (Also Open question 1.)
- **Proposed change:**
  - **BSB-31-PENDING-1:** Replace "the run-start flow is BSB-24's, and it invokes this route" with
    "BSB-27's preflight invokes this route for the run's project and the exact
    `skills_commit_sha` after BSB-25 has set the run prepared / packed the bundle at that SHA and
    before BSB-26 launches the agent container." State that BSB-24's run start only records the
    request and does not scan. Delete the stale "when those epics are decomposed" sentence and
    instead say BSB-27's stories must name the call when that epic is decomposed.
  - **BSB-31-PENDING-2:** Replace "BSB-24's run-start flow calls it" with "BSB-27's preflight
    calls it" and keep the after-packaging/before-launch order.
  - **BSB-31-PENDING-4:** Same replacement and order; keep the synchronous-wait rationale.
  - **BSB-31-PENDING-6:** Replace "BSB-24's run-start preflight calls the same route" with
    "BSB-27's preflight calls the same route."
  - **Cross-epic follow-up (not applied here):** BSB-27, when decomposed, must name the
    invocation and its position after packaging; BSB-24 and BSB-25 already state the correct
    order, but BSB-27's epic "before a bundle or branch is prepared" wording still needs
    correction. This report does not compute a build order.

### Finding 2 — Epic boundary: the Definition of Done promises a static scan before packaging and a packaging block that no requirement or story owns, and the ordering is impossible as written

- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-3. Cross-epic: BSB-25, BSB-30, the
  BSB-31 epic's Goal / Definition of Done in `epics.md`.
- **Evidence:**
  - The epic's Goal / Definition of Done: "Every run **and every packaged skill** is preceded by a
    static scan of the exact content, and a non-passing verdict blocks the run **and packaging**"
    (`epics.md:555-561`). Implementation guidance step 7: "Expose the verdict to run preflight and
    packaging; both must consume the same function" (`epics.md:553`).
  - `epic-map.json` assigns BSB-31 fourteen requirements; none is a packaging gate. The only
    packaging-refusal requirements are FR-071 to FR-073 (verifier lint, verifier self-test,
    verifier range) (`PRD.md:145-147`), mapped to BSB-30 (`epics.md:1032-1034`), not BSB-31.
  - BSB-31-PENDING-1 says the opposite of the DoD's ordering: "The packed bundle is a
    precondition: there is no scan before packaging, and a missing `skill_bundles` row is the HTTP
    409 above" (`stories.md:120-121`). Its Notes record the unowned gate: "no FR mapped to BSB-31
    assigns a packaging refusal, and BSB-25's and BSB-30's epics name no static-scan packaging
    gate … packaging refusal belongs to the verifier checks FR-071 to FR-073 under BSB-30"
    (`stories.md:135-141`). BSB-31-PENDING-3 repeats the hole (`stories.md:327-332`).
  - BSB-25's functional scope and DoD cover bundle preparation and the 60-second budget, not a
    static-scan packaging gate (`epics.md:730-759`). BSB-30's packaging preflight covers verifier
    lint, self-test and range (`epics.md:992-1004`); its FR-069 Ready check includes the static
    scan, but Ready is not packaging. BSB-30 has no stories yet.
- **What is missing/ambiguous/contradictory:** The epic promises a second hard gate (packaging)
  that no story claims and no FR assigns, and it says every packaged skill is *preceded* by a
  static scan even though the scan reads the packed `skill_bundles` row — so packaging must
  happen first. The stories' note that "packaging refusal belongs to the verifier checks FR-071 to
  FR-073" blurs the issue: those are verifier refusals, not a static-verdict refusal. The epic
  cannot meet its own DoD as written, and the requirement map cannot tell a packaging implementer
  whether to add the gate or omit it.
- **Question (if a person must decide):** Is a non-passing static verdict required to block
  packaging? If yes, which epic and FR own that gate — BSB-25, BSB-30, or a new BSB-31 story/AC
  and requirement — and at what point relative to the bundle being packed? If no, should the
  DoD's packaging sentence be removed or narrowed to the run gate (FR-055)? (Also Open question 2.)
- **Proposed change:**
  - **BSB-31-PENDING-1:** Keep the verdict-only boundary, but replace "packaging refusal belongs
    to the verifier checks FR-071 to FR-073" with "the only packaging refusals are FR-071 to
    FR-073 (verifier lint, self-test and range); none is a static-verdict refusal." State the
    resolved owner/FR once the question is answered.
  - **BSB-31-PENDING-3:** Align the same sentence with PENDING-1's answer; do not claim a static
    packaging gate here if no FR or story owns it.
  - **Cross-epic follow-up (not applied here):** If the gate is assigned outside BSB-31, BSB-25 or
    BSB-30 must add it (with a requirement) and the epic DoD wording must change. If it is
    assigned to BSB-31, this epic needs a new acceptance criterion and a mapped requirement. A new
    FR or `epic-map.json` change needs a human/earlier-stage decision; this review does not make
    it.

### Finding 3 — Cross-epic data contract: the static scan's bundle identity disagrees with BSB-25's `(skill, skills_commit_sha)` key and `s3_key` layout

- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-1. Cross-epic: BSB-25-PENDING-1, BSB-25-PENDING-2.
- **Evidence:**
  - BSB-31-PENDING-1: "The route accepts `project_id` and `skills_commit_sha`; it reads the
    `skill_bundles` row for that SHA and scans that bundle" (`stories.md:80-81`). Its 409 is
    "No packed bundle exists for commit 4f2c9a1." (`stories.md:52-55`). Its fixtures use
    `s3_key "bundles/4f2c9a1.tar.gz"` (`stories.md:33`, `:35`, `:40`).
  - BSB-25-PENDING-2: "The reuse key is `(skill, skills_commit_sha)`: the same commit packaged for
    a different skill is a different bundle" (`BSB-25/_epic/stories.md:207-208`); "BSB-31-PENDING-1
    reads the `skill_bundles` row by `(skill, skills_commit_sha)` and hands the `bundle_sha256`
    and `s3_key` to the scanner, so a scan always reads the exact bundle the run will use"
    (`BSB-25/_epic/stories.md:210-212`). Its `s3_key` format is `bundles/<skills_commit_sha>/<skill>.tar.gz`
    (`BSB-25/_epic/stories.md:202-204`), and its acceptance criteria prove two skills at the same
    commit SHA produce two distinct rows and bundles (`BSB-25/_epic/stories.md:153-156`).
- **What is missing/ambiguous/contradictory:** BSB-25 tells BSB-31 to read the row by
  `(skill, skills_commit_sha)` and gives the per-skill `s3_key` layout; BSB-31 says it reads "the
  row for that SHA" and fixtures a SHA-only `s3_key`. When two skills are packed at the same
  commit, a SHA-only lookup can select the wrong skill's row (or be ambiguous), and the fixture
  asserts an object path the packer never writes. The route is build-scoped
  (`/api/builds/7/scans/static`), so `skill` is resolvable from build 7; the story simply does not
  say so. This is separate from PENDING-2's content-only reuse key
  (`skill + stage + bundle_sha256 + scanner_version`), which is correct.
- **Question (if a person must decide):** Does the route resolve `skill` from the build and read
  the `skill_bundles` row by `(skill, skills_commit_sha)`, with the 409 naming both the skill and
  the commit? (The scan must not pick a bundle by SHA alone.) (Also Open question 3.)
- **Proposed change:**
  - **BSB-31-PENDING-1:** State that the route resolves `skill` from the build and reads the
    `skill_bundles` row by `(skill, skills_commit_sha)`; update the 409 to name both (for example,
    "No packed bundle exists for skill bug-fix-resolver at commit 4f2c9a1."); align every fixture
    `s3_key` with BSB-25's `bundles/<skills_commit_sha>/<skill>.tar.gz` layout. Keep the
    direct-entry-point fixture rule (a caller that supplies the row/fixture still owns the
    identity).
  - **Cross-epic follow-up:** BSB-25 already states the correct key and layout; no change is
    proposed there, but the BSB-25 story should remain the authority for the `skill_bundles`
    contract.

### Finding 4 — Cross-epic scope and actor: the catalog reviewer cannot open the only scan report route, and no epic owns a reviewer-readable view

- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-5. Cross-epic: BSB-36-PENDING-2, BSB-33, `PRD.md` §2 and
  FR-111.
- **Evidence:**
  - BSB-31-PENDING-5: the report route "is part of the authoring interface and is gated by
    BSB-18's signed-in skill-builder check only (a signed-in author outside the `skill-builders`
    group receives HTTP 403). … A catalog reviewer named in PRD section 2 does not use the
    authoring interface, so this gated URL cannot itself be the report link FR-111 asks the
    catalog pull request to carry. No epic currently owns a stable reviewer-facing scan-report
    view or its access rule: BSB-33's stable view is the run report and BSB-36 only links the scan
    reports" (`stories.md:470-480`).
  - `PRD.md` §2 defines the catalog reviewer as one who "Consumes the catalog pull request and its
    linked run and scan reports; does not use the authoring interface" (`PRD.md:16`); FR-111
    requires the pull-request description to link the scan reports (`PRD.md:185`).
  - BSB-36-PENDING-2 links `<base>/scans/<static.id>` and `<base>/scans/<llm.id>` (`BSB-36/_epic/stories.md:51-52`)
    and records the unresolved gap: "a reviewer outside those gates cannot open the links … the
    access decision must be made before the catalog review flow can rely on those links"
    (`BSB-36/_epic/stories.md:96-105`).
  - BSB-33 lists "the security tab and scan reports (BSB-31 and BSB-32)" out of scope and records
    the reviewer-facing stable report view as unresolved (`BSB-33/_epic/stories.md:101-103`).
- **What is missing/ambiguous/contradictory:** The only scan report route BSB-31 builds is
  authoring-gated, while BSB-36's catalog pull request links that same URL for a reviewer who is
  defined as not using the authoring interface. No epic currently owns a reviewer-readable view or
  its access rule. Two stories therefore point at the same URL with incompatible access
  assumptions. BSB-31-PENDING-5 correctly supplies no second route, but the deliverable remains
  unowned; this is a genuine cross-story/cross-epic scope hole, not a wording nit.
- **Question (if a person must decide):** Do catalog reviewers read the linked run and scan
  reports? If yes, which epic owns the stable reviewer-facing view and what authorizes a reviewer
  (a signed read-only share link, a reviewer role/group, or a public view)? If no, should PRD §2's
  reviewer definition and FR-111's "linked scan reports" wording be corrected? (Also Open
  question 4.)
- **Proposed change:**
  - **BSB-31-PENDING-5:** Keep the authoring route and its BSB-18 gate exactly as written; keep
    the statement that this story adds no second route. Update the note to name the resolved owner
    and the route the reviewer will use once the question is answered. Do not add a
    reviewer-facing route to BSB-31 unless the epic is explicitly assigned that deliverable.
  - **Cross-epic follow-up (not applied here):** BSB-36 (or BSB-33, if it extends its stable run
    report) must add the reviewer view and its access rule; BSB-36-PENDING-2's `/scans/<id>`
    links must then point at that view. If the answer is "reviewers do not read the reports,"
    `PRD.md` §2 and FR-111 must be corrected. This is the same open decision recorded in BSB-36's
    and BSB-33's reviews.

### Finding 5 — Cross-epic scope boundary: the combined Security tab is handed to BSB-32, which does not claim it, and BSB-26/BSB-33 also disclaim it

- **Severity:** Blocking
- **Stories touched:** BSB-31-PENDING-5. Cross-epic: BSB-32-PENDING-2, BSB-26, BSB-33, ADR
  SK-001 §6b.
- **Evidence:**
  - BSB-31-PENDING-5's Out of scope assigns "the LLM scan report, which model ran it and **the
    combined security tab (BSB-32)**" (`stories.md:451-452`). Its Notes say the route and report
    model are "shared with the run page's Security tab (BSB-26/BSB-33 link the run's scan); this
    story owns the scan-only page, not the run page layout" (`stories.md:482-484`).
  - ADR SK-001 §6b requires a "**Security tab** on the skill and run pages, next to the verify
    results (§6): score, recommendation, each finding with severity, rule, file and line, and
    which model ran the LLM check" (`docs/adr/SK-001-skill-builder.md:308-310`).
  - BSB-32-PENDING-2's Out of scope does not mention or claim the combined tab
    (`BSB-32/_epic/stories.md:145-151`); its Notes own the "Full security check" control,
    `POST /api/builds/7/scans/full`, and the LLM report's rendering on `GET /scans/{id}`, not a
    Security tab (`BSB-32/_epic/stories.md:159-164`).
  - BSB-33 lists "the security tab and scan reports (BSB-31 and BSB-32)" out of scope
    (`BSB-33/_epic/stories.md:101`); BSB-26 lists "the Security tab and scan reports (BSB-31,
    BSB-32 and BSB-33)" out of scope (`BSB-26/_epic/stories.md:187`).
- **What is missing/ambiguous/contradictory:** BSB-31's story explicitly assigns the combined
  Security tab to BSB-32, but no BSB-32 story claims it, and BSB-26 and BSB-33 both disclaim it.
  The ADR requires the tab on the skill and run pages. A developer following BSB-32 would build
  the full-scan control and the LLM report page, not the combined tab; a developer following
  BSB-26/BSB-33 would treat it as another epic's. The capability falls in the handoff between the
  two scan epics.
- **Question (if a person must decide):** Does BSB-32 own the combined Security tab (adding an
  acceptance criterion or a story for the skill/build and run pages), or do BSB-26/BSB-33 own it
  when they compose the page? If BSB-31 supplies only the static report model and link, which
  epic owns the tab layout and the LLM model line? (Also Open question 5.)
- **Proposed change:**
  - **BSB-31-PENDING-5:** Correct the Out of scope pointer: do not state that BSB-32 owns the
    combined tab unless BSB-32 adds it. State that this story supplies the static report model,
    the scan-only page and the link BSB-26/BSB-33 can compose, and name the actual owner of the
    combined tab once decided. Repeat the same owner in the Notes.
  - **Cross-epic follow-up (not applied here):** BSB-32-PENDING-2 (or BSB-26/BSB-33) must add the
    combined-tab acceptance criterion; ADR SK-001 §6b is the requirement. This is the same
    handoff BSB-32's review flags as its Finding 2.

### Finding 6 — Epic-wide NFR: NFR-001's 60-second preparation budget and the synchronous 600-second static scan define "run preparation" differently

- **Severity:** Advisory
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-4. Cross-epic: BSB-25, `PRD.md`
  NFR-001 and goal G4.
- **Evidence:**
  - NFR-001: "Non-model run preparation completes within 60 seconds for a skill bundle of up to
    5 MB" (`PRD.md:251`); goal G4 repeats the 60-second target (`PRD.md:31-32`).
  - BSB-31-PENDING-1: "the run-start preflight waits synchronously for the verdict, so a cache-miss
    run start can wait up to ten minutes; a reuse hit … adds no scan time. The scan is a separate
    synchronous gate, not part of BSB-25's 60-second / 5 MB non-model bundle-preparation budget
    (NFR-001); NFR-001's 'run preparation' wording and BSB-25 must be reconciled to say so
    (cross-epic follow-up)" (`stories.md:129-133`). BSB-31-PENDING-4 repeats the boundary
    (`stories.md:387-390`).
  - BSB-25-PENDING-2 measures NFR-001 "on the end-to-end non-model preparation — resolver, packer
    and branch preparer — for a skill folder of 5,000,000 bytes. No model call is part of
    preparation … BSB-27's preflight, static scan and execution run after this story has set
    `prepared`" (`BSB-25/_epic/stories.md:300-304`).
- **What is missing/ambiguous/contradictory:** The PRD's NFR-001 says "non-model run preparation"
  completes in 60 seconds; the stories define preparation narrowly (resolver/packer/branch
  preparer) and put the synchronous static scan, which can wait ten minutes, outside it. The
  intended design is clear and recorded as a follow-up, but the PRD text has not been reconciled,
  so a reviewer can read NFR-001 as violated on every cache-miss run start. This is an
  epic-wide NFR boundary, not a single acceptance criterion.
- **Question (if a person must decide):** Does NFR-001's 60-second budget include the synchronous
  static-scan wait? If yes, the gating model needs a different design (for example an asynchronous
  scan or a separate run-start budget) or NFR-001 must change; if no, the PRD must say that "run
  preparation" excludes the static-scan gate and BSB-25's measurement is the authoritative one.
  (Also Open question 6.)
- **Proposed change:**
  - **BSB-31-PENDING-1:** Keep the boundary note, but describe it as a proposed interpretation
    requiring PRD/NFR-001 reconciliation rather than as settled; state the answer explicitly.
  - **BSB-31-PENDING-4:** Same; keep the 600-second ceiling and the cache-miss wait explicit.
  - **Cross-epic follow-up (not applied here):** `PRD.md` NFR-001/G4 and BSB-25's measurement must
    agree on whether the scan is inside or outside the 60-second budget. No story change can
    settle a PRD wording question.

### Finding 7 — Cross-epic service contract: BSB-37's declared service call does not match PENDING-1's direct entry point

- **Severity:** Advisory
- **Stories touched:** BSB-31-PENDING-1. Cross-epic: BSB-37-PENDING-2.
- **Evidence:**
  - BSB-31-PENDING-1 defines "one direct entry point that takes a packed bundle fixture (its bytes
    or `skill_bundles` row) plus the pinned scanner version and image digest, with no build or
    project, and returns the same scan result the route returns" (`stories.md:83-86`); a scan
    created through it has `build_id` NULL (`stories.md:87-89`).
  - BSB-37-PENDING-2 says the command "calls BSB-31-PENDING-1's static scan service **with the
    project**, skill, commit SHA and bundle and no build id; BSB-31-PENDING-1 must expose that
    service independently of its build-keyed route" (`BSB-37/_epic/stories.md:243-247`); it also
    says the row carries no `project_id` and "the project is the authorization scope only"
    (`BSB-37/_epic/stories.md:248-250`).
- **What is missing/ambiguous/contradictory:** BSB-31 says the direct entry point has "no build or
  project"; BSB-37 says the CLI calls it "with the project." Both agree the scan row has no
  `project_id`, so the likely intent is that the CLI resolves and authorizes the project before
  calling the service, but the service signature is left ambiguous. A developer implementing the
  entry point could add a `project_id` parameter BSB-31 says does not exist, or omit one BSB-37's
  caller expects.
- **Question (if a person must decide):** Does the direct scan entry point accept a `project_id`
  (for example for authorization/audit), or does the caller resolve and authorize the project
  before passing only the bundle fixture, scanner version and image digest? (Also Open question 7.)
- **Proposed change:**
  - **BSB-31-PENDING-1:** State the exact entry-point inputs and outputs, including whether
    `project_id`, `skill` and `skills_commit_sha` are parameters or derived from the fixture;
    name BSB-37-PENDING-2 alongside BSB-31-PENDING-3 as a consumer. If the project is not a
    parameter, say explicitly that the caller authorizes it before calling.
  - **Cross-epic follow-up:** BSB-37-PENDING-2's "with the project" wording should then say the
    CLI resolves/authorizes the project and passes the bundle/provenance, not a service
    `project_id`.

### Finding 8 — Cross-story state contract: PENDING-5 renders `state "running"`, but PENDING-1 never defines the state enum or when the row is created

- **Severity:** Advisory
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-4, BSB-31-PENDING-5. Cross-epic: BSB-38
  (its acceptance fixtures assume the same running state).
- **Evidence:**
  - BSB-31-PENDING-5's AC: "Given a `scans` row id 14 for build 7 with state `running` and score
    NULL, recommendation NULL and verdict NULL … Then the response is HTTP 200 and the page
    contains 'Scan in progress'" (`stories.md:424-427`).
  - BSB-31-PENDING-1 owns the record and its fields (`stories.md:97-103`) but says only that "a
    scan request returns only after the scan reaches `completed` or `failed`"
    (`stories.md:78-79`); its acceptance criteria assert `completed` and `failed`, never
    `running`. BSB-31-PENDING-4 says a scan that has not reached `completed` by 600 seconds is
    recorded `failed` (`stories.md:378-379`), implying an in-flight state without naming it.
  - BSB-38's acceptance fixtures also include `GET /scans/14` in a running state
    (`BSB-38/_epic/stories.md:54`).
- **What is missing/ambiguous/contradictory:** PENDING-5's in-progress page depends on a persisted
  `scans` row with `state "running"`, but PENDING-1, the record owner, never enumerates the state
  values or says when the row is inserted. A developer could insert the row only at completion and
  PENDING-5's running AC would be unreachable; another could use a different value or omit
  `started_at`. The state lifecycle is a shared record contract, not a single-story detail.
- **Question (if a person must decide):** Is `state "running"` a persisted state, and is the
  `scans` row inserted as `running` (with `started_at`) before the scanner container starts,
  transitioning to `completed` or `failed`? If not, how is PENDING-5's in-progress page reached?
  (Also Open question 8.)
- **Proposed change:**
  - **BSB-31-PENDING-1:** Enumerate the `state` values (`running`, `completed`, `failed`) and
    state that the row is inserted as `running` with `started_at` before the scanner starts, then
    transitioned to `completed` or `failed`; state which story owns each transition.
  - **BSB-31-PENDING-4:** Reference the same enum when recording the timeout as `failed`.
  - **BSB-31-PENDING-5:** Reference PENDING-1's enum for the `running` and `failed` states rather
    than relying on an undefined fixture value.

### Finding 9 — Cross-story requirement non-duplication: the story-map's PENDING-1 summary claims content reuse that PENDING-1 assigns to PENDING-2

- **Severity:** Advisory
- **Stories touched:** BSB-31-PENDING-1, BSB-31-PENDING-2; `story-map.json`.
- **Evidence:**
  - `story-map.json`'s PENDING-1 summary says the story runs the scan "… recording the scanner
    version and image digest, **reusing by content**, and executing the scanner container with no
    network access …" (`story-map.json`, PENDING-1 `summary`).
  - The story body assigns reuse to PENDING-2: "reusing an earlier result (BSB-31-PENDING-2)"
    (`stories.md:67`), and "The scan record's identity/reuse key is `skill` + `stage` +
    `bundle_sha256` + `scanner_version` (BSB-31-PENDING-2 owns reuse)" (`stories.md:91-92`).
  - PENDING-1's mapped requirements are FR-076 and NFR-005; FR-077 (reuse) is PENDING-2's
    (`story-map.json`; `stories.md:568-569`).
- **What is missing/ambiguous/contradictory:** The story-map summary is the text used for the Jira
  story summary. It claims "reusing by content" for PENDING-1 while the story body and the
  requirement map assign reuse to PENDING-2. This is a non-duplication/traceability defect, not a
  functional contradiction: the body is clear, but the published summary would tell a reader that
  PENDING-1 owns FR-077.
- **Question:** None; this is a wording fix.
- **Proposed change:**
  - **`story-map.json` (PENDING-1):** Remove "reusing by content" from the summary, or phrase it
    as "exposing the route/service through which BSB-31-PENDING-2 reuses." Keep PENDING-2 as the
    reuse owner.
  - **BSB-31-PENDING-1 / BSB-31-PENDING-2:** No story-body change; the body already states the
    ownership correctly.

## Open questions

1. **Run-start caller (Finding 1).** Which flow/story invokes
   `POST /api/builds/{id}/scans/static` before every run — BSB-24's run start or BSB-27's
   preflight — and does it run after BSB-25 sets the bundle prepared and before BSB-26 launches
   the agent container? If BSB-24, its "does not scan" statement must change; if BSB-27, BSB-31's
   four notes and BSB-27's epic ordering wording must change.
2. **Packaging gate (Finding 2).** Is a non-passing static verdict required to block packaging? If
   yes, which epic/FR owns the gate (BSB-25, BSB-30, or a new BSB-31 story/AC and requirement) and
   at what point relative to the packed bundle? If no, should the DoD's packaging sentence be
   removed or narrowed to the run gate?
3. **Bundle identity (Finding 3).** Does the static-scan route resolve `skill` from the build and
   read the `skill_bundles` row by `(skill, skills_commit_sha)`, with the 409 naming both? The scan
   must not select a bundle by SHA alone.
4. **Reviewer access (Finding 4).** Do catalog reviewers read the linked run and scan reports? If
   yes, which epic owns the stable reviewer-facing view and what authorizes a reviewer? If no, do
   PRD §2 and FR-111 need correction?
5. **Combined Security tab (Finding 5).** Does BSB-32 own the combined Security tab, or do
   BSB-26/BSB-33 own it when they compose the skill/run page? Which epic supplies the LLM model
   line and the tab layout?
6. **NFR-001 boundary (Finding 6).** Does NFR-001's 60-second non-model preparation budget include
   the synchronous static-scan wait? If yes, the gating model or the NFR must change; if no, the
   PRD must say preparation excludes the static-scan gate.
7. **Direct entry point (Finding 7).** Does the direct scan entry point accept a `project_id`, or
   does the caller resolve and authorize the project before passing only the bundle fixture,
   scanner version and image digest?
8. **Running state (Finding 8).** Is `state "running"` persisted, and is the `scans` row inserted
   as `running` with `started_at` before the scanner container starts, transitioning to
   `completed` or `failed`? If not, how is PENDING-5's in-progress page reached?

Finding 9 is a story-map wording fix and needs no product answer.

## Proposed changes

### BSB-31-PENDING-1 — closes Findings 1, 2, 3, 6, 7 and 8

- **Finding 1:** Name BSB-27's preflight as the run-start invariant caller; state that BSB-24's
  run start does not scan; delete the stale "when those epics are decomposed" sentence.
- **Finding 2:** Keep the verdict-only boundary; correct the note to say the only existing
  packaging refusals are FR-071 to FR-073 (verifier), not a static-verdict gate; name the resolved
  owner once Open question 2 is answered.
- **Finding 3:** Resolve `skill` from the build; read `skill_bundles` by
  `(skill, skills_commit_sha)`; update the 409 message; align fixture `s3_key` values with BSB-25's
  `bundles/<skills_commit_sha>/<skill>.tar.gz` layout.
- **Finding 6:** State the proposed NFR-001 boundary explicitly and mark it as requiring PRD/BSB-25
  reconciliation.
- **Finding 7:** Specify the direct entry point's exact inputs/outputs and whether `project_id`,
  `skill` and `skills_commit_sha` are parameters or derived; name BSB-37-PENDING-2 as a consumer.
- **Finding 8:** Enumerate `state` values and the insert-as-`running`/transition lifecycle.

### BSB-31-PENDING-2 — closes Finding 1

- Replace "BSB-24's run-start flow calls it" (`stories.md:219-221`) with "BSB-27's preflight calls
  it after BSB-25 has packed the bundle at the requested SHA and before the agent container
  launches." Add no other change; the reuse key and content-only identity remain correct.

### BSB-31-PENDING-3 — closes Finding 2

- Align the packaging-boundary note (`stories.md:327-332`) with PENDING-1's answer: BSB-31 supplies
  only the verdict; the existing packaging refusals are FR-071 to FR-073 (verifier), and any
  static-verdict packaging gate must be assigned with a requirement before this story claims it.
- If Open question 2 answers that BSB-31 owns a packaging gate, add the corresponding acceptance
  criterion here and in PENDING-1, plus a mapped requirement (a change requiring a human/earlier
  decision).

### BSB-31-PENDING-4 — closes Findings 1, 6 and 8

- **Finding 1:** Replace "BSB-24's run-start flow calls it" (`stories.md:384-386`) with "BSB-27's
  preflight calls it" and keep the after-packaging/before-launch order.
- **Finding 6:** Reference the resolved NFR-001 boundary rather than presenting the exclusion as
  settled.
- **Finding 8:** Reference PENDING-1's `state` enum when recording the timeout as `failed`.

### BSB-31-PENDING-5 — closes Findings 4, 5 and 8

- **Finding 4:** Keep the authoring route and its BSB-18 gate; keep "this story adds no second
  route"; update the note to name the resolved owner and route for the reviewer view, or the
  corrected PRD assumption.
- **Finding 5:** Correct the Out of scope pointer that says the combined Security tab is BSB-32's;
  name the actual owner once Open question 5 is answered, and state that this story supplies only
  the static report model, the scan-only page and the link the page owner composes.
- **Finding 8:** Reference PENDING-1's state enum for the `running` and `failed` report states.

### BSB-31-PENDING-6 — closes Finding 1

- Replace "BSB-24's run-start preflight calls the same route" (`stories.md:557-558`) with
  "BSB-27's preflight calls the same route," keeping the same after-packaging/before-launch order
  and the membership check.

### `docs/product/epics/BSB-31/_epic/story-map.json` — closes Finding 9

- Remove "reusing by content" from PENDING-1's `summary`, or rephrase it so reuse is explicitly
  PENDING-2's. Do not change PENDING-1's `requirement_ids`.

### Cross-epic follow-ups (not applied here)

- **Finding 1:** BSB-27, when decomposed, must name the static-scan invocation and its position
  after packaging; BSB-27's epic "before a bundle or branch is prepared" wording needs correction.
  BSB-24 and BSB-25 already state the correct order.
- **Finding 2:** BSB-25 or BSB-30 must own the packaging gate (with a requirement) or the BSB-31
  epic DoD sentence must be removed/narrowed. This needs a human/earlier-stage decision.
- **Finding 4:** BSB-36 (or BSB-33) must add the stable reviewer-facing scan-report view and its
  access rule, or PRD §2/FR-111 must be corrected. BSB-36-PENDING-2's `/scans/<id>` links depend
  on that decision.
- **Finding 5:** BSB-32-PENDING-2 (or BSB-26/BSB-33) must add the combined Security tab
  acceptance criterion; ADR SK-001 §6b is the requirement.
- **Finding 6:** `PRD.md` NFR-001/G4 and BSB-25's measurement must agree on whether the static
  scan is inside the 60-second budget.
- **Finding 7:** BSB-37-PENDING-2's "with the project" wording should match the entry-point
  contract chosen in Open question 7.

## Architecture impact

None.

## Requirement coverage check

Every FR/NFR `epic-map.json` assigns to BSB-31 is exercised by at least one story's acceptance
criteria, with no contradicting claims:

| Requirement | Exercising story | Acceptance criterion / note |
|---|---|---|
| FR-076 | BSB-31-PENDING-1 | "Unscanned content is scanned before the run-start preflight returns a verdict"; "The scan reads the requested commit's bundle, not a newer branch head." Conditional on Finding 1: the story proves the route's behavior once called; the every-run caller must be named consistently. |
| FR-077 | BSB-31-PENDING-2 | Unchanged bundle/scanner reuse; changed content; changed scanner version; same bundle at a new commit; cross-build/project reuse. |
| FR-078 | BSB-31-PENDING-3 | "A DO_NOT_INSTALL recommendation fails even with no critical finding." |
| FR-079 | BSB-31-PENDING-3 | "Any critical finding fails even with a non-blocking recommendation." |
| FR-080 | BSB-31-PENDING-3 | "Incomplete coverage fails even with no blocking recommendation and no critical finding." |
| FR-081 | BSB-31-PENDING-3 | "An accepted critical finding cannot clear the block." |
| FR-087 | BSB-31-PENDING-4 | "A scan still running at ten minutes is terminated and recorded as failed"; "The ten-minute boundary terminates a scan that has not finished." |
| FR-088 | BSB-31-PENDING-4 | Same two scenarios: state "failed", verdict "fail", the fixed failure reason. |
| FR-089 | BSB-31-PENDING-5 | "A completed passing scan shows its score, recommendation and coverage"; the failed and reused states. Authoring report only; reviewer access is Finding 4 and is not an FR-089/154/155 claim. |
| FR-091 | BSB-31-PENDING-3 | "The verdict matches the platform's for the same content and pinned scanner version." |
| FR-092 | BSB-31-PENDING-6 | Project-member start with no run; non-owner member; non-member refusal; no project membership. |
| FR-154 | BSB-31-PENDING-5 | "A completed passing scan shows its score, recommendation and coverage." |
| FR-155 | BSB-31-PENDING-5 | "Every finding is shown with severity, rule, file and line." |
| NFR-005 | BSB-31-PENDING-1 | "The static scanner container has no network access." |

All fourteen requirements mapped to BSB-31 are covered; no story claims a requirement outside this
epic. Finding 9 is a story-map summary wording defect, not a missing or duplicated acceptance
criterion.

## Dependency-note sanity check

Every "Depends on X" / "prerequisite for Y" note refers to a real story or a named epic, and the
in-epic directions are reciprocated. Cross-epic mismatches are called out explicitly:

- **PENDING-1 ↔ PENDING-3:** reciprocal and consistent — PENDING-1 applies PENDING-3's rules and
  records the output; PENDING-3 depends on PENDING-1 only for the record contract. No cycle remains.
- **PENDING-2 → PENDING-1 / PENDING-3:** both exist; PENDING-1 names PENDING-2 as the reuse owner.
- **PENDING-4 → PENDING-1 / PENDING-3:** both exist; PENDING-1 names PENDING-1/-4 as the
  failed/timeout state owners.
- **PENDING-5 → PENDING-1 / PENDING-3 / PENDING-4:** all exist; PENDING-1 names PENDING-5 as the
  report route owner.
- **PENDING-6 → PENDING-1 / PENDING-3 / BSB-22-PENDING-1/-3 / BSB-21 / BSB-25:** all named stories
  exist or the referenced epic is named (BSB-21 has no stories yet); the membership-check
  dependency matches BSB-22-PENDING-1's and -3's notes.
- **Cross-epic mismatch (Finding 1):** BSB-31-PENDING-1/-2/-4/-6 say BSB-24's run start invokes the
  route; BSB-24-PENDING-1 says run start does not scan and BSB-27's preflight invokes it; BSB-25
  agrees with BSB-24. The dependency is one-sided and contradictory. BSB-27's epic guidance still
  says "before a bundle or branch is prepared," which BSB-25 records as superseded.
- **Cross-epic mismatch (Finding 3):** BSB-25-PENDING-2 says BSB-31-PENDING-1 reads the
  `skill_bundles` row by `(skill, skills_commit_sha)`; BSB-31-PENDING-1 says it reads by SHA alone.
  The two contracts do not match.
- **Cross-epic mismatch (Finding 4):** BSB-36-PENDING-2 depends on BSB-31-PENDING-5's `GET /scans/{id}`
  for the catalog pull-request link, while PENDING-5 says that route is authoring-gated and cannot
  serve the reviewer.
- **Cross-epic mismatch (Finding 5):** BSB-31-PENDING-5 says BSB-32 owns the combined Security tab;
  BSB-32's stories do not claim it, and BSB-26/BSB-33 disclaim it.
- **Cross-epic mismatch (Finding 7):** BSB-37-PENDING-2 depends on BSB-31-PENDING-1's direct scan
  service "with the project"; PENDING-1 defines the entry point as "no build or project." The row
  has no `project_id` in both stories, so the mismatch is in the service signature/wording.
- **Epic references without stories:** BSB-21, BSB-27 and BSB-30 have no `stories.md` yet. Their
  epic-level references (build page, FR-055 refusal, FR-069 readiness / FR-071-073 packaging) are
  correctly named as epics, not as missing story keys; they cannot be checked for story-level
  reciprocity until decomposition. This check does not compute build order.
