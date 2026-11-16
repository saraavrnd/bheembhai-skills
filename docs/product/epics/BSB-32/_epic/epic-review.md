# Epic Review — BSB-32: LLM security scanning

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-32-PENDING-1, BSB-32-PENDING-2, BSB-32-PENDING-3, BSB-32-PENDING-4

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-32/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The run context (`BB_CONTEXT`) binds `ITEM.id` to `BSB-32` and records
  the upstream `sdlc-plan-stories-write` commit `e7cefc0`; `story_id` is `SkillBuilder-2`, the
  PRD's parent work item, not a story in this epic. `SkillBuilder-2` has no Jira issue on the
  configured site: a read-only `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue
  does not exist or you do not have permission to see it"). The Atlassian MCP tools were not
  exposed in this session, so the configured site (`https://saraavrnd.atlassian.net`) was queried
  read-only through its REST API (GET only; no Jira writes). **Correction:** the run context and
  the recent `sdlc-plan-stories-write` commits (`e7cefc0`, `0526a3a`) identify this run's epic as
  BSB-32; the review below is of BSB-32's four-story set, not of the non-existent
  `SkillBuilder-2`.
- **The epic.** `GET /rest/api/3/issue/BSB-32` returned HTTP 200: Epic "LLM security scanning",
  status To Do, labels `FA-12`/`MVP`, no parent, no sub-tasks and no issue links. Its description
  matches the BSB-32 section of `epics.md`, including the value sentence "additional, non-gating
  evidence for the author and the catalog reviewer" and the non-goal "per-run overrides of the
  scan model". `epic-map.json` records BSB-32 under FA-12/MVP with FR-082, FR-083, FR-084,
  FR-085, FR-086, FR-090, FR-093, FR-139, FR-156 and FR-163; no NFR is mapped to this epic.
- **All 4 stories in BSB-32**, from `stories.md` and `story-map.json` in one read each —
  BSB-32-PENDING-1 through -4 (the full set, not a sample). `story-map.json` maps the same 10
  requirement IDs, and `stories.md`'s coverage table maps each to at least one acceptance
  criterion. BSB-32 has no prior `epic-review.md`; `revisions.md` records the Pass 1 change from
  seven layer stories to these four vertical slices.
- **`PRD.md`** — §2 target users (including the catalog reviewer, who "does not use the authoring
  interface"), §5 FA-12, §6 the ten FR rows (FR-082 to FR-086, FR-090, FR-093, FR-139, FR-156,
  FR-163), §7 NFR-002/NFR-003/NFR-004/NFR-005/NFR-012 (the request gate, credential privacy,
  static-scan isolation and accessibility), and §8/§9's source note and resolved decisions. §8's
  "LLM-scan model setting" says the default model lives on the test project and the project owner
  configures it; §9's resolved decision says "configured per test project only, not overridable
  per run" and "Only the project owner changes it".
- **`epics.md`** — the BSB-32 section (description, functional scope, implementation guidance,
  DoD, covered requirements, Notes), plus the sections of the epics that consume or supply this
  one: BSB-18 (authoring gate), BSB-21 (build page and head SHA), BSB-22 (test projects,
  membership and the settings page), BSB-23 (AI model profiles and secret storage), BSB-24 (run
  start), BSB-26 (run execution), BSB-29 (verification), BSB-30 (readiness), BSB-31 (static scan
  and the shared `GET /scans/{id}` route), BSB-33 (run report and stable reviewer view), BSB-36
  (catalog submission links), BSB-37 (CLI) and BSB-38 (accessibility, explicitly cross-cutting
  over the scan surfaces).
- **`docs/adr/SK-001-skill-builder.md`** — §4 (test project, owner-only integrations and
  credential storage), §5 (runs and model selection), §6b (the LLM check, the model sentence
  "The author picks the model from the test project's **AI models** profiles (§4); only the
  project owner changes the default", the Security tab "on the skill and run pages ... and which
  model ran the LLM check", and "a timeout is a failed scan") and §9 (the data model, which names
  no `scans` table and gives `projects` only `id, name, owner_id, created_at`).
- **Other story sets checked:** BSB-18, BSB-19, BSB-20, BSB-22, BSB-23 and BSB-31 have stories on
  disk and were read for the cross-epic handoffs this epic depends on. BSB-21, BSB-24, BSB-25,
  BSB-26, BSB-27, BSB-29, BSB-30, BSB-33, BSB-36, BSB-37 and BSB-38 have epic definitions but no
  stories yet; their epic scope and Notes were read to distinguish a legitimate cross-epic
  dependency from an unowned capability. BSB-31's own review (`BSB-31/_epic/epic-review.md`) was
  read because its Finding 5 (reviewer-facing scan report) and its scan-route ownership directly
  bound this epic.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md`
  are not committed; ADR SK-001 is the design authority this pass can use. No
  `epic-sequence.md`/`.json` exists for BSB-32; no build order is computed here.

## Findings

### Finding 1 — Cross-epic model-selection contract: the stories make the project owner pick one fixed profile/tier and forbid per-scan choice, while ADR SK-001 §6b says the author picks the model

- **Severity:** Blocking
- **Stories touched:** BSB-32-PENDING-1, BSB-32-PENDING-2
- **Evidence:**
  - BSB-32-PENDING-1, Story: "As a **project owner**, I want **to choose the AI model profile and
    tier that the project's LLM security scan uses**, so that **the scan runs with the model I
    selected and no author can override it per scan**" (`stories.md:26`).
  - BSB-32-PENDING-1, Notes: "The configured pair is the project's single LLM-scan model. ...
    Only the project owner changes the pair, and the owner guard runs before any field is read,
    reusing BSB-22-PENDING-4's exact refusal message. ... No run-start or full-scan request field
    can override this project setting (BSB-32-PENDING-2 rejects such a field)" (`stories.md:79-86`).
  - BSB-32-PENDING-2, "A per-scan model override is refused": a request carrying `model`,
    `model_profile_id` and `tier` must return HTTP 422 with "The LLM scan model is configured on
    the test project and cannot be overridden per scan." (`stories.md:121-124`).
  - `docs/adr/SK-001-skill-builder.md` §6b, LLM check: "The author picks the model from the test
    project's **AI models** profiles (§4); only the project owner changes the default, and the
    key comes from Secrets Manager like any other run" (`SK-001:303-307`).
  - `PRD.md` §8: "The LLM security scan's **default model** lives on the test project, not on the
    installation and not on the run; the project owner configures it (FR-163)" (`PRD.md:362`).
    §9: "configured per test project only, not overridable per run (FR-163). Only the project
    owner changes it" (`PRD.md:324-325`, `PRD.md:372`). `epics.md` BSB-32 non-goals: "per-run
    overrides of the scan model" (`epics.md:613-614`); implementation step 2: "do not accept a
    per-run model override" (`epics.md:619`).
  - FR-163: "A full security scan uses the LLM-scan model profile configured for the scan's test
    project" (`PRD.md:237`).
- **What is missing/ambiguous/contradictory:** The stories resolve an ambiguity in the stricter
  direction and make the owner, not the author, the selector. The ADR's "The author picks the
  model" sentence is the only place that grants the author a choice, and the PRD only forbids
  overrides "per run", not "per scan" (a full scan can run without a run). The stories therefore
  add two product decisions the requirement text does not state: (a) the author has no per-scan
  choice at all, and (b) the owner chooses the tier as well as the profile. A developer reading
  the ADR could build author-selectable profile/tier with an owner-configured default, while a
  developer reading the stories would reject the same request with 422. The tier question is
  separate from the profile question: FR-163 names a "model profile", while the stories require a
  profile **and** a tier, which is how BSB-23's `models: {high, medium, low}` map resolves to a
  concrete model.
- **Question (if a person must decide):** Is the LLM scan's model one fixed, owner-configured
  (profile, tier) pair per test project — the stories' reading — or may the author choose a
  profile and tier per scan from the project's AI model profiles, with the owner configuring only
  the default, as ADR SK-001 §6b says? If the former, is the owner required to choose a tier, or
  does the system apply a default tier? (also Open question 1)
- **Proposed change:**
  - If the owner-only fixed pair is confirmed: keep BSB-32-PENDING-1 and BSB-32-PENDING-2's 422
    AC as written, and add one sentence to PENDING-1's Notes that ADR SK-001 §6b's "The author
    picks the model" wording is superseded by the PRD's project-level setting and needs a one-line
    amendment (cross-epic, not applied here). State explicitly whether the owner picks the tier
    or a default tier applies; FR-163 alone names only a profile.
  - If author per-scan choice is intended: change PENDING-1 to "the owner configures the
    project's default profile and tier" and keep the default-resolution ACs; change PENDING-2 to
    accept an optional `model_profile_id` and `tier` on the full-scan request, require them to
    resolve within the scan project's `kind "ai_model"` rows, and replace the 422 refusal AC with
    validation ACs (foreign profile, non-AI-model profile, unknown tier). Do not leave both the
    owner-setting and the per-scan field as unstated alternatives.
  - Same change for both stories: one actor, one granularity, one refusal/validation contract.

### Finding 2 — Cross-epic scope boundary: BSB-31 hands the combined Security tab to BSB-32, but no BSB-32 story owns it and the ADR requires it on the skill and run pages

- **Severity:** Blocking
- **Stories touched:** BSB-32-PENDING-2 (potentially PENDING-1 and PENDING-4). Cross-epic:
  BSB-31-PENDING-5, BSB-26, BSB-33.
- **Evidence:**
  - BSB-31-PENDING-5, Out of scope: "the LLM scan report, which model ran it and **the combined
    security tab (BSB-32)**" (`BSB-31/_epic/stories.md:337-342`).
  - BSB-31-PENDING-5, Notes: "The HTML route and the report model are shared with the run page's
    Security tab (BSB-26/BSB-33 link the run's scan); this story owns the scan-only page, not the
    run page layout" (`BSB-31/_epic/stories.md:360-362`).
  - `docs/adr/SK-001-skill-builder.md` §6b: "**Security tab** on the skill and run pages, next to
    the verify results (§6): score, recommendation, each finding with severity, rule, file and
    line, and which model ran the LLM check" (`SK-001:308-310`).
  - BSB-32-PENDING-2 owns the "Full security check" control on `GET /builds/7` and the LLM
    report's rendering on `GET /scans/{id}`; BSB-32-PENDING-1 owns the "security scan" section of
    `GET /projects/7/settings`; BSB-32-PENDING-3/-4 own the sandbox and the unavailable/failed
    states. None of the four stories mentions a Security tab or claims to compose the static and
    LLM results on the skill/build or run page (`stories.md:63-87`, `145-164`, `236-267`,
    `320-355`).
  - BSB-33's functional scope is the run report (verdicts, checks, diff, Jira changes, turn
    count, trace link) and does not list a Security tab or the scan's model
    (`epics.md:1047-1110`). BSB-26's functional scope is progress/logs/outcome capture, not the
    report page (`epics.md:780-841`). So the "BSB-26/BSB-33" handoff in BSB-31-PENDING-5 does
    not name an owning story either.
- **What is missing/ambiguous/contradictory:** The ADR requires a Security tab on the skill and
  run pages that shows the LLM model and findings. BSB-31's story explicitly assigns the
  "combined security tab" to BSB-32, but BSB-32's four stories stop at the scan-only
  `GET /scans/{id}` page and the build-page control; no acceptance criterion renders a tab that
  composes the static score/recommendation/findings (BSB-31) with the LLM model/findings
  (BSB-32). A developer following BSB-32 would not build it, and neither BSB-26 nor BSB-33's epic
  scope admits it. The capability falls in the handoff between the two scan epics.
- **Question (if a person must decide):** Does BSB-32 own the combined Security tab (adding an
  acceptance criterion or a fifth story for the skill/build and run pages), or does BSB-33 (or
  BSB-26) own the tab, in which case BSB-31-PENDING-5's out-of-scope must name that owner and
  BSB-32's stories must state the handoff? (also Open question 2)
- **Proposed change:**
  - **BSB-32-PENDING-2:** Add either (a) an acceptance criterion for the combined Security tab on
    the build/skill page and the run page — it renders the static verdict/score/recommendation
    and findings from BSB-31's records plus "Model: <model>" and the LLM findings from the
    `stage "llm"` row, with the advisory banner — or (b) a Notes sentence that the tab is
    BSB-33/BSB-26's and that BSB-32 supplies only the LLM model and findings; do not leave it
    unmentioned.
  - **BSB-32-PENDING-4:** If the tab renders unavailable/failed LLM states, add the corresponding
    tab-state assertion; otherwise state that the tab is out of this story's scope.
  - **Cross-epic (not applied here):** BSB-31-PENDING-5's out-of-scope must point at the chosen
    owner; BSB-33 (and/or BSB-26) must add the tab to its functional scope if that is the answer;
    ADR SK-001 §6b's Security tab sentence is the requirement both epics must satisfy.

### Finding 3 — Cross-epic data-model contradiction: PENDING-3's fixtures store Jira and source-control secret values on `integrations` rows, while BSB-23 and the ADR keep them only in the external secret store

- **Severity:** Advisory
- **Stories touched:** BSB-32-PENDING-3. Cross-epic: BSB-23-PENDING-1, BSB-23-PENDING-2.
- **Evidence:**
  - BSB-32-PENDING-3, "A full check of untrusted content completes and shows its finding": "...
    an 'integrations' row id 6 with project_id 3, kind 'jira' and **secret value
    'jira-test-token-9f2c'**, an 'integrations' row id 7 with project_id 3, kind 'github' and
    **secret value 'ghp-test-token-7a1d'** ..." (`stories.md:207-210`).
  - BSB-32-PENDING-3, "The scan container holds no credential other than the model key": "secrets
    'sk-ant-test-3c9e' at 'skill-builder/3/integration-8', 'jira-test-token-9f2c' **for the Jira
    integration** and 'ghp-test-token-7a1d' **for the source-control integration** ..."
    (`stories.md:217-220`).
  - BSB-23-PENDING-1, Notes: "The credential value lives only in the external secret store, at
    path 'skill-builder/7/integration-3'; ... the 'integrations.secret_ref' column holds only that
    path" (`BSB-23/_epic/stories.md:85-88`). Its AC asserts the row has `secret_ref` and the
    store holds the value, and neither response contains the value
    (`BSB-23/_epic/stories.md:31-33`).
  - BSB-23-PENDING-2, AC: the source-control row has `secret_ref
    "skill-builder/7/integration-3"`, "the secret store holds 'ghp-test-token-7a1d' at path
    'skill-builder/7/integration-3'", and neither response contains it
    (`BSB-23/_epic/stories.md:120`).
  - ADR SK-001 §4/§6b: integration credentials come from the external secret store, not from the
    `integrations` row.
- **What is missing/ambiguous/contradictory:** The fixture describes a schema in which
  `integrations` rows carry secret values, which BSB-23's stories and the ADR explicitly deny.
  A developer building the fixture literally would either invent a `secret` column (contradicting
  BSB-23 and the architecture) or silently use `secret_ref` and make the Given false. The
  credential-absence assertions in AC 3 are the epic's FR-083/FR-084 proof; they must be aimed at
  the real storage location (`secret_ref` plus the secret store), not at an `integrations`
  column that does not exist. PENDING-3's Notes also do not name BSB-23-PENDING-1/-2, the stories
  that own the `secret_ref`/secret-store contract it relies on.
- **Question (if a person must decide):** None — this is a data-model correction. The intended
  shape is BSB-23's `secret_ref` plus an external secret-store entry.
- **Proposed change:**
  - **BSB-32-PENDING-3:** Change the Given to `"integrations"` row id 6 with `project_id 3`,
    `kind "jira"` and `secret_ref "skill-builder/3/integration-6"`, and id 7 with `project_id 3`,
    `kind "github"` and `secret_ref "skill-builder/3/integration-7"`; add the corresponding
    `"jira-test-token-9f2c"` and `"ghp-test-token-7a1d"` entries to the secret store at those
    paths. Keep the credential-absence assertions unchanged. Add BSB-23-PENDING-1 and
    BSB-23-PENDING-2 to the dependency Notes for the `secret_ref`/secret-store contract.

### Finding 4 — Cross-story ownership: three stories each claim to extend `scans`, and the LLM-stage record shape (including nullable `verdict`) has no single owner

- **Severity:** Advisory
- **Stories touched:** BSB-32-PENDING-2, BSB-32-PENDING-3, BSB-32-PENDING-4. Cross-epic:
  BSB-31-PENDING-1.
- **Evidence:**
  - BSB-32-PENDING-2, Notes: "The LLM scan record **extends 'scans' with stage 'llm' and the
    nullable `model` and `model_profile_id` columns** (the data-model stage must record them)"
    (`stories.md:182-184`); "An LLM scan has no verdict (`verdict` stays NULL) because the result
    is advisory" (`stories.md:185-187`).
  - BSB-32-PENDING-3, Notes: "This story **owns the LLM scan service's sandbox contract: it
    extends 'scans' with stage 'llm' and the nullable `model` and `model_profile_id` columns**
    (the data-model stage must record them)" (`stories.md:248-252`).
  - BSB-32-PENDING-4, Notes: "It **extends 'scans' so that state 'unavailable' is valid for stage
    'llm'**; the data-model stage must record that enumeration **alongside the model columns**"
    (`stories.md:335-336`).
  - BSB-31-PENDING-1, Notes: this story "owns the static scan service, the `scans` and
    `scan_findings` records" and lists the `scans` columns, including `stage`, `state` and
    `verdict`, without saying that `verdict` is nullable or that `stage`/`state` accept the LLM
    values (`BSB-31/_epic/stories.md:73-88`).
- **What is missing/ambiguous/contradictory:** Two stories (PENDING-2 and PENDING-3) both say they
  extend `scans` with the same `stage "llm"`, `model` and `model_profile_id` columns, and a third
  (PENDING-4) extends the same table with the `state "unavailable"` value and says it does so
  "alongside the model columns". No story owns the `scans` migration as a whole, so two
  implementers can write overlapping migrations (or each assume the other added the columns).
  The base schema in BSB-31-PENDING-1 does not declare `verdict` nullable, although PENDING-2 and
  PENDING-4 both require a NULL verdict for LLM scans; a `verdict NOT NULL` implementation of
  BSB-31's schema would make the LLM insert impossible. The same gap exists for the stage/state
  enumerations.
- **Question (if a person must decide):** None if the ownership is assigned as proposed; the
  schema shape is already agreed. (If the team wants one migration per epic stage, say so in the
  Notes; no product choice is involved.)
- **Proposed change:**
  - **BSB-32-PENDING-2:** Make this story the owner of the LLM scan record extension: `stage`
    accepts `"llm"`; `model` and `model_profile_id` are nullable; `verdict` is nullable for
    `stage "llm"`. State that PENDING-3 and PENDING-4 consume this record shape rather than
    redefine it.
  - **BSB-32-PENDING-3:** Remove the "extends 'scans' ..." ownership sentence; say it depends on
    PENDING-2's LLM record shape and owns only the sandbox/service contract.
  - **BSB-32-PENDING-4:** Keep the `state "unavailable"` enumeration ownership, but say it is an
    addition to PENDING-2's record shape, not a second table extension; state the exact allowed
    states for `stage "llm"` (`completed`, `unavailable`, `failed`) and that `verdict` stays NULL
    in all three.
  - **Cross-epic (not applied here):** BSB-31-PENDING-1's `scans` schema should record that
    `verdict` is nullable overall and that `stage`/`state` are enumerated values, so the static
    and LLM stages share one contract.

### Finding 5 — Cross-epic guard reuse: PENDING-1 applies BSB-22-PENDING-4's integration-management guard and its exact "change integrations" message to a non-integration route

- **Severity:** Advisory
- **Stories touched:** BSB-32-PENDING-1. Cross-epic: BSB-22-PENDING-2, BSB-22-PENDING-4.
- **Evidence:**
  - BSB-32-PENDING-1, "A non-owner member cannot change the scan model": Bob submits
    `{"model_profile_id": 4, "tier": "low"}` on `POST "/projects/7/llm-scan-model"` and the
    builder responds with HTTP 403 and the message "Only the project owner can change
    integrations." (`stories.md:35-38`).
  - BSB-32-PENDING-1, Notes: it depends on BSB-22-PENDING-4 "for the project settings page at
    `GET "/projects/7/settings"` and its owner-only guard"; "the owner guard runs before any field
    is read, reusing BSB-22-PENDING-4's exact refusal message" (`stories.md:70-72`, `82-83`); it
    also owns "the 'security scan' section of the settings page" (`stories.md:72-74`).
  - BSB-22-PENDING-4, Notes: "This story owns the project settings page at
    `GET "/projects/7/settings"`, its 'Integrations' section and the **owner-only
    integration-management guard**. ... BSB-23 must call this guard on **every integration change
    route**, and `POST /projects/7/integrations` is the representative guarded route used by this
    story's acceptance criteria" (`BSB-22/_epic/stories.md:258-263`).
  - BSB-22-PENDING-2, Notes: it "defines the shared owner guard every project-administration
    route uses", with the message "Only the project owner can change project members"; BSB-23's
    integration routes apply "the same owner-only rule, with the message 'Only the project owner
    can change integrations'" (`BSB-22/_epic/stories.md:131-136`).
  - BSB-22's own review (`BSB-22/_epic/epic-review.md` Finding 3 and Open question 2) records that
    the ownership of the shared owner guard versus the integration-management guard is unresolved
    and that the integration-route contract is still an open question.
- **What is missing/ambiguous/contradictory:** `POST /projects/7/llm-scan-model` is a
  project-administration route, but it is not an integration change: it selects a model profile
  for the LLM scan. PENDING-1 reuses BSB-22-PENDING-4's integration-specific guard and message
  anyway, and BSB-22-PENDING-4's Notes do not name this route (or BSB-32's new "security scan"
  settings section) in its scope. The dependency is one-sided: BSB-32-PENDING-1 depends on
  BSB-22-PENDING-4, but BSB-22-PENDING-4 does not say its guard is exposed to BSB-32's route. A
  BSB-22 implementer can reasonably build a guard bound to the integration controller and never
  make it reusable here, or a reviewer can reasonably object that the 403 message is false — the
  owner is not changing an integration. BSB-22's own review already flags that guard ownership is
  ambiguous, so BSB-32 is inheriting an unresolved contract.
- **Question (if a person must decide):** Is the LLM-scan model setting treated as an
  "integration change" for the purposes of BSB-22-PENDING-4's guard (and therefore uses its exact
  message), or should it use BSB-22-PENDING-2's shared owner guard with a scan-specific message
  such as "Only the project owner can change the LLM scan model."? (also Open question 3)
- **Proposed change:**
  - **BSB-32-PENDING-1:** Choose one of the two guards explicitly in Notes. If the shared owner
    guard is used, change the 403 message to a scan-specific one and state that the guard runs
    before any field is read, independent of the integrations controller. If the
    integration-management guard is used, state why the model setting is an integration change
    and keep the exact message. Add a sentence that the "security scan" section is added to
    BSB-22-PENDING-4's settings page rather than a second settings page.
  - **Cross-epic (not applied here):** BSB-22-PENDING-4's Notes should either name
    `POST /projects/7/llm-scan-model` and the BSB-32 "security scan" section in its guard/page
    scope, or state that a separate shared owner guard (from BSB-22-PENDING-2) is the one BSB-32
    calls. Reconcile with BSB-22's Open question 2.

### Finding 6 — Cross-epic dependency note: PENDING-2 and PENDING-4 assert the run report page without naming BSB-33, and PENDING-2's "no LLM-001" assertion is broader than the verdict sections

- **Severity:** Advisory
- **Stories touched:** BSB-32-PENDING-2, BSB-32-PENDING-4. Cross-epic: BSB-33, BSB-26.
- **Evidence:**
  - BSB-32-PENDING-2, "A finding in the LLM report does not block starting or finishing a run":
    after the run finishes, `GET "/projects/3/runs/21"` renders "Verdict: PASS" and **no
    "LLM-001"** (`stories.md:131-134`).
  - BSB-32-PENDING-2, Out of scope: "starting, executing and verifying a run (BSB-24, BSB-26 and
    BSB-29)" (`stories.md:149-150`); its Notes name BSB-21, BSB-22, BSB-31 and BSB-32, but not
    BSB-33 (`stories.md:153-164`).
  - BSB-32-PENDING-4, "A failed LLM scan does not block a run": `GET "/projects/3/runs/23"`
    renders "Verdict: PASS" and the failure reason does not appear in the run's claimed verdict,
    final verdict or verification result (`stories.md:311-314`); its Out of scope also names only
    BSB-24, BSB-26 and BSB-29 (`stories.md:323-324`).
  - `epics.md` BSB-33 "Run report & change evidence" owns the run report and its stable view
    (`epics.md:1047-1110`); BSB-31-PENDING-5 says "the run page's Security tab (BSB-26/BSB-33 link
    the run's scan)" (`BSB-31/_epic/stories.md:360-362`).
- **What is missing/ambiguous/contradictory:** Both stories exercise a page whose owner
  (BSB-33, with BSB-26 for the run page layout) is not in their dependency notes or out-of-scope
  lists. The dependency is legitimate and sequenced, but it is silent, which is exactly the
  cross-epic note gap category 5 asks for. The assertion itself is also broader than the
  requirement: "no 'LLM-001'" on the whole run page would forbid a Security tab that correctly
  shows the LLM finding as advisory evidence (Finding 2 / ADR §6b). The intended assertion is
  that the finding does not enter the run's claimed verdict, final verdict or verification
  result — which the same AC already states separately.
- **Question (if a person must decide):** None for the dependency note; the owner is BSB-33 for
  the run report (and BSB-26 for the run page layout). If the run page is meant to render the
  Security tab (Finding 2), the "no LLM-001" assertion must be scoped to the verdict sections,
  not the whole page.
- **Proposed change:**
  - **BSB-32-PENDING-2 and BSB-32-PENDING-4:** Add BSB-33 (and BSB-26 for the run page layout) to
    the dependency Notes and Out of scope. Scope the assertion to "the run's verdict, verification
    result and final verdict" and replace the whole-page "no 'LLM-001'" assertion with "the
    verdict/verification sections do not contain 'LLM-001'"; if Finding 2 puts the Security tab on
    the run page, the finding must be allowed to appear there as advisory evidence.

### Finding 7 — Cross-epic scope boundary: the epic's value names the catalog reviewer, but no story states how the reviewer reads the LLM report; the handoff is only in the epic summary

- **Severity:** Advisory
- **Stories touched:** BSB-32-PENDING-2, BSB-32-PENDING-4. Cross-epic: BSB-31-PENDING-5, BSB-33,
  BSB-36.
- **Evidence:**
  - BSB-32's epic description: "The value is additional, non-gating evidence for **the author and
    the catalog reviewer** without letting a second security opinion stall delivery"
    (`epics.md:598-599`; Jira BSB-32 description matches).
  - BSB-32-PENDING-2 and BSB-32-PENDING-4 render the LLM report on `GET "/scans/{id}"`, which
    BSB-32-PENDING-4 says is "gated by BSB-18's signed-in skill-builder check only,
    content-addressed, and applying no project-membership check" (`stories.md:346-349`). BSB-18 is
    the authoring gate (`epics.md:132-158`), not a reviewer-facing access rule.
  - BSB-31-PENDING-5, Notes: "It does not apply the project-membership check, because the same
    scan report is evidence linked from a catalog pull request (BSB-36, FR-111) and the PRD's
    catalog reviewer does not use the authoring interface. **The reviewer-facing stable report
    view and its access rule belong to BSB-33/BSB-36**; this story supplies the report content
    and adds no project-membership gate to it" (`BSB-31/_epic/stories.md:352-359`). BSB-31's own
    review Finding 5 is the same open question and is still Blocking there.
  - BSB-36's functional scope only "Link[s] the run report and the scan reports from the
    pull-request description" (`epics.md:1284-1295`); it defines no scan-report viewer. BSB-33's
    stable view is the **run** report (`epics.md:1082-1083`), not a scan-report viewer.
  - `stories.md`'s trailing paragraph says "the reviewer-facing scan-report view (FR-111) ...
    remain[s] other epics' handoffs and are not claimed here" (`stories.md:374-379`), but no
    story's Notes or Out of scope repeats it.
- **What is missing/ambiguous/contradictory:** The epic promises the LLM evidence to the catalog
  reviewer, but the only report route is behind the authoring gate. The reviewer-facing view is
  named as another epic's handoff at the bottom of `stories.md`, yet neither BSB-33 nor BSB-36
  owns a scan-report viewer, and BSB-32's stories do not say that their LLM report content
  (model line, findings, unavailable/failed states) is what that future viewer must render. A
  BSB-32 implementer can build the authoring route correctly and still leave the reviewer with no
  way to see the model or the LLM findings. This is the same hole BSB-31's review left open; it
  is not duplicated here as a Blocking finding because the author-facing behavior is safe to
  build, but the epic's stated audience is not served by any story.
- **Question (if a person must decide):** Does BSB-32 need to state the reviewer-view handoff in
  its stories (and is the LLM report's model/findings content part of the stable view BSB-33/
  BSB-36 must expose), or is the epic-level summary sufficient and the reviewer view entirely
  BSB-33/BSB-36's deliverable? (also Open question 4)
- **Proposed change:**
  - **BSB-32-PENDING-2 and BSB-32-PENDING-4:** Add a Notes sentence mirroring BSB-31-PENDING-5:
    the `GET /scans/{id}` page is the authoring report; the reviewer-facing stable scan report
    and its access rule are BSB-33/BSB-36's; BSB-32 supplies the LLM model, findings and
    unavailable/failed content, and adds no second reviewer route. Add BSB-33/BSB-36 to the
    cross-epic handoff list.
  - **Cross-epic (not applied here):** BSB-33/BSB-36 must add the scan-report viewer and its
    access rule, or PRD §2's catalog-reviewer statement must be corrected. This should be
    resolved together with BSB-31's Finding 5.

### Finding 8 — Cross-story LLM reuse wording: PENDING-2 says no LLM stage is reused, while PENDING-4 only says unavailable/failed scans are never reused

- **Severity:** Advisory
- **Stories touched:** BSB-32-PENDING-2, BSB-32-PENDING-4
- **Evidence:**
  - BSB-32-PENDING-2, Notes: "**This epic adds no reuse for the LLM stage; each full scan runs
    it.**" (`stories.md:187`); its AC 1 reports `"reused": false` for the LLM result
    (`stories.md:102-104`), and its Out of scope lists "reusing a prior LLM result"
    (`stories.md:150-151`).
  - BSB-32-PENDING-4, Notes: "**An unavailable or failed scan is never reused**, so a later full
    scan re-attempts it" (`stories.md:344`); its Out of scope lists "reusing a prior LLM result"
    (`stories.md:326`).
  - BSB-31-PENDING-2 owns the reuse key and limits reuse to `stage "static"`
    (`BSB-31/_epic/stories.md:153-165`), which is consistent with PENDING-2's no-LLM-reuse rule.
- **What is missing/ambiguous/contradictory:** PENDING-2's rule is absolute: the LLM stage is
  never reused, including a completed scan. PENDING-4's narrower sentence ("unavailable or
  failed") implies that a completed LLM scan might be reused, because it does not say what
  happens to a completed one. The two stories do not have conflicting acceptance criteria, but
  their prose leaves an implementer free to read PENDING-4 as authorizing completed-result reuse.
  Because a completed LLM scan re-run costs a model call, this is worth one sentence even though
  the ACs do not contradict.
- **Question (if a person must decide):** None — the epic's intended rule is PENDING-2's "no LLM
  reuse"; PENDING-4 needs to say so consistently.
- **Proposed change:**
  - **BSB-32-PENDING-4:** Change "An unavailable or failed scan is never reused" to "No LLM scan
    is reused; a later full scan re-runs the LLM stage, including when a prior LLM scan
    completed." Keep the failed/unavailable emphasis if useful, but do not imply completed reuse.
  - **BSB-32-PENDING-2:** Keep the absolute no-reuse rule; add a cross-reference to PENDING-4's
    sentence so the two stories cannot drift.

## Open questions

1. **LLM-scan model granularity (Finding 1).** Is the scan model one fixed, owner-configured
   (profile, tier) pair per test project — the stories' reading — or may the author choose a
   profile and tier per scan from the project's AI model profiles, with the owner configuring only
   the default, as ADR SK-001 §6b says? If the former, does the owner choose the tier or does a
   default tier apply? If the latter, the 422 refusal in BSB-32-PENDING-2 changes to a validation
   contract.
2. **Combined Security tab ownership (Finding 2).** Does BSB-32 add an acceptance criterion or a
   fifth story for the ADR's Security tab on the skill/build and run pages (composing BSB-31's
   static result with BSB-32's LLM model and findings), or does BSB-33/BSB-26 own the tab? If the
   latter, BSB-31-PENDING-5's out-of-scope and BSB-32's Notes must name that owner.
3. **Owner guard for the scan-model setting (Finding 5).** Is `POST /projects/7/llm-scan-model`
   an "integration change" for BSB-22-PENDING-4's guard (keeping the "Only the project owner can
   change integrations." message), or does it use BSB-22-PENDING-2's shared owner guard with a
   scan-specific message? The answer decides which guard BSB-22 must expose and which message
   BSB-32 tests.
4. **Reviewer-facing LLM report (Finding 7).** Does BSB-32 need to state the reviewer-view
   handoff in its stories — and is the LLM report's model/findings content part of the stable
   view BSB-33/BSB-36 must expose — or is the epic-level summary sufficient and the viewer
   entirely BSB-33/BSB-36's deliverable? This should be resolved with BSB-31's Finding 5.

## Proposed changes

`docs/product/epics/BSB-32/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-32-PENDING-1** — Story/ACs/Notes: resolve the model granularity and actor (Finding 1);
  choose and name the owner guard and refusal message, and state that the "security scan"
  section is added to BSB-22-PENDING-4's settings page (Finding 5); keep the nullable
  `projects.llm_scan_model_profile_id`/`llm_scan_model_tier` columns and the cleared-pair
  unavailable path as written.
- **BSB-32-PENDING-2** — Story/ACs/Notes: if author per-scan choice is confirmed, replace the 422
  refusal with the validation contract; otherwise keep it and state the ADR reconciliation
  (Finding 1). Own the LLM `scans` record extension, including nullable `verdict` (Finding 4).
  Add the Security tab AC or its explicit handoff (Finding 2); add BSB-33/BSB-26 to the
  dependency notes and scope the "no LLM-001" assertion to the verdict/verification sections
  (Finding 6); add the reviewer-view handoff sentence (Finding 7); keep the no-LLM-reuse rule
  and cross-reference PENDING-4 (Finding 8).
- **BSB-32-PENDING-3** — ACs/Notes: replace the `integrations` "secret value" fixtures with
  `secret_ref` paths and secret-store entries, and add BSB-23-PENDING-1/-2 to the dependencies
  (Finding 3); stop claiming the `scans` extension and depend on PENDING-2's record shape
  (Finding 4).
- **BSB-32-PENDING-4** — Notes/ACs: reference PENDING-2's LLM record shape and keep only the
  `state "unavailable"` enumeration (Finding 4); add BSB-33/BSB-26 to the dependencies and scope
  the run-page assertion (Finding 6); add the reviewer-view handoff sentence (Finding 7); change
  the reuse sentence to "No LLM scan is reused" (Finding 8). If the Security tab renders
  unavailable/failed LLM states, add that tab-state assertion (Finding 2).

Cross-epic follow-ups (not applied here):

- **BSB-31-PENDING-5** — Point the "combined security tab" out-of-scope at the chosen owner
  (BSB-32, or BSB-33/BSB-26), and keep the reviewer-facing view handoff consistent with BSB-32's
  Finding 7.
- **BSB-22-PENDING-4** — Either name `POST /projects/7/llm-scan-model` and BSB-32's "security
  scan" settings section in the guard/page scope, or state that BSB-32 calls a separate shared
  owner guard from BSB-22-PENDING-2 (Finding 5). Reconcile with BSB-22's Open question 2.
- **BSB-31-PENDING-1** — Record that `scans.verdict` is nullable overall and that `stage`/`state`
  are enumerated values shared with the LLM stage (Finding 4).
- **BSB-33 / BSB-36** — Add the reviewer-facing scan-report viewer and its access rule, or
  correct PRD §2's catalog-reviewer statement (Finding 7; same as BSB-31's Finding 5).
- **ADR SK-001 §6b** — If the owner-only fixed pair is confirmed, reconcile "The author picks the
  model from the test project's **AI models** profiles" with the project-level setting (Finding 1).
  The Security tab sentence also needs the owner chosen in Finding 2.

## Architecture impact

No new architecture design is required to build the epic as the stories describe. The cumulative
behavior needs the two `projects.llm_scan_model_*` columns and the `scans` stage/model/state
extension; those are declared by the stories and must be recorded by the later data-model stage,
as BSB-31-PENDING-1 does for the base `scans` table. ADR SK-001 §9 names none of them, but that is
the same normal planning-to-design handoff BSB-31 already records, not a conflict with an existing
entity.

Two design-document reconciliations are recorded here rather than as story changes:

1. **ADR SK-001 §6b's model sentence.** "The author picks the model from the test project's **AI
   models** profiles (§4); only the project owner changes the default" conflicts with the stories'
   owner-only fixed pair. The PRD §8/§9 and FR-163 support the project-level reading, so if the
   owner-only answer is confirmed the ADR sentence needs a one-line amendment (a
   `sdlc-arch-design` amend); if the author-selectable answer is confirmed, the stories change
   instead. No new design is needed either way.
2. **The ADR's Security tab.** "**Security tab** on the skill and run pages ... and which model
   ran the LLM check" has no owning story after BSB-31 hands the combined tab to BSB-32. This is
   an ownership/scope assignment, not a new design: either BSB-32 adds the tab or BSB-33/BSB-26
   does.

Both are ownership/wording gaps the next planning pass can resolve; neither requires inventing a
data model, endpoint or integration that the architecture does not already imply.

## Requirement coverage check

All ten requirements mapped to BSB-32 by `epic-map.json` are exercised by at least one acceptance
criterion, and no story claims a requirement outside the epic. The only caveat is the
model-selection semantics of FR-163 (Finding 1); it does not remove the requirement from the epic.

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-082 — LLM scan only after the static pass | BSB-32-PENDING-2 | "A failing static scan stops the LLM stage and the page says why"; **also** BSB-32-PENDING-3's "The scan reads the exact bundle the static scan passed, not a newer branch head" for the current-content half. |
| FR-083 — no credential other than the model key | BSB-32-PENDING-3 | "The scan container holds no credential other than the model key". |
| FR-084 — reach only the model endpoint | BSB-32-PENDING-3 | "The scan container can reach only the model endpoint". |
| FR-085 — never blocks a run | BSB-32-PENDING-2; BSB-32-PENDING-4 | "A finding in the LLM report does not block starting or finishing a run"; "No LLM-scan model profile is configured"; "A failed LLM scan does not block a run". The two paths are distinct and consistent. |
| FR-086 — findings shown to the author | BSB-32-PENDING-2 | "A project member starts a full security check and reads the LLM report"; "A clean LLM scan shows the model and an empty findings state". |
| FR-090 — report shows which model ran | BSB-32-PENDING-2 | "A project member starts a full security check and reads the LLM report"; "The full check uses the project's configured model profile and tier"; "A clean LLM scan shows the model and an empty findings state". |
| FR-093 — full scan from the skill page without a run | BSB-32-PENDING-2 | "A project member starts a full security check and reads the LLM report"; "An author with no project to scan cannot start a full check". The build page is the "skill page" used by BSB-31-PENDING-6 as well. |
| FR-139 — record an LLM scan that cannot run as unavailable | BSB-32-PENDING-4 | All six unavailable/failed scenarios: no profile, missing key, rejected key, budget exhaustion, scanner exit 137, ten-minute timeout (the last records `state "failed"`, correctly distinct from unavailable). |
| FR-156 — findings list severity, rule, file and line | BSB-32-PENDING-2 | "A project member starts a full security check and reads the LLM report"; "A clean LLM scan shows the model and an empty findings state". |
| FR-163 — full scan uses the project's configured LLM-scan model profile | BSB-32-PENDING-1; BSB-32-PENDING-2 | "The owner selects the project's LLM-scan model profile"; "The full check uses the project's configured model profile and tier"; "A per-scan model override is refused". **Caveat:** the owner-only granularity and the tier's actor are the Finding 1 decision. |

No foreign requirement is claimed. NFR-004 (credential values never in logs/results) is
exercised by BSB-32-PENDING-3's "never writes a credential value to 'scans', 'scan_findings', the
report document or a log"; NFR-002/NFR-003 are inherited from BSB-18's per-request gate, which
BSB-32-PENDING-4 names for the report route and BSB-32-PENDING-2 inherits through BSB-21's build
page. No NFR is mapped to BSB-32 in `epic-map.json`.

## Dependency-note sanity check

Every "Depends on" story key in BSB-32's stories exists in the named epic, and the cross-epic
hand-offs that matter are mostly reciprocal. The exceptions are the findings above; the rest are
consistent.

| Story | Dependency as written | Check |
|---|---|---|
| BSB-32-PENDING-1 | BSB-22-PENDING-1 (projects table) | Exists; BSB-22-PENDING-1 owns `projects`/`project_members` (`BSB-22/_epic/stories.md:54-59`). |
| BSB-32-PENDING-1 | BSB-22-PENDING-4 (settings page, owner guard) | Exists; **one-sided** — BSB-22-PENDING-4's guard is scoped to integration change routes and does not name this route or the "security scan" section (Finding 5). |
| BSB-32-PENDING-1 | BSB-23-PENDING-3 (`kind "ai_model"` rows, tier mapping) | Exists; BSB-23-PENDING-3's Out of scope names the "project-level default model (BSB-32)" (`BSB-23/_epic/stories.md:239`). Reciprocal. |
| BSB-32-PENDING-1 | BSB-30 (readiness treats unavailable as satisfied) | BSB-30 is an epic with no stories yet; its functional scope and DoD say the same (`epics.md:992-1026`). Legitimate. |
| BSB-32-PENDING-2 | BSB-21 (build page, head SHA, access rule) | BSB-21 is an epic with no stories yet; it owns the build page (`epics.md:329-382`). BSB-31-PENDING-6 depends on the same page. Legitimate. |
| BSB-32-PENDING-2 | BSB-22-PENDING-1/-3 (membership rows and shared check) | Exist; BSB-22's review Finding 5 already proposes adding BSB-32 to its reuse lists (`BSB-22/_epic/epic-review.md:220-244`). The BSB-32 side is written; the BSB-22 side is a known cross-epic follow-up. |
| BSB-32-PENDING-2 | BSB-31-PENDING-1/-2/-3/-5 | Exist. BSB-31-PENDING-1 names "BSB-32's full security scan calls this static stage first" (`BSB-31/_epic/stories.md:94`); PENDING-5's out-of-scope names the LLM report (Finding 2); PENDING-6's out-of-scope names the full scan. Reciprocal. |
| BSB-32-PENDING-2 | BSB-32-PENDING-1 | Exists; PENDING-1's Notes say PENDING-2 rejects the per-scan field and exercises FR-163. Reciprocal. |
| BSB-32-PENDING-3 | BSB-31-PENDING-1/-5 | Exist; the base `scans`/`scan_findings` records and the report route. PENDING-5's static mapping is extended by PENDING-2 (Finding 4). |
| BSB-32-PENDING-3 | BSB-32-PENDING-1/-2 | Exist; profile/tier and the full-scan control/render. Reciprocal. |
| BSB-32-PENDING-3 | **BSB-23-PENDING-1/-2 (not named)** | The `secret_ref`/secret-store fixture is BSB-23's contract; the story should name them (Finding 3). |
| BSB-32-PENDING-4 | BSB-31-PENDING-1/-5 | Exist; base records and report route. |
| BSB-32-PENDING-4 | BSB-32-PENDING-1/-2 | Exist; profile/tier and the full-scan control/successful rendering. |
| BSB-32-PENDING-4 | BSB-30 (readiness) | BSB-30 epic exists, no stories; its scope says readiness requires the LLM scan complete or unavailable (`epics.md:992-1026`). Legitimate. |
| BSB-32-PENDING-4 | BSB-18 (report-page gate, in prose) | BSB-18 exists as an epic with no stories; the gate is the authoring gate (`epics.md:132-158`). It is named in the Notes prose but not in the "Depends on" list; a minor formatting fix, not a separate finding. |
| BSB-32-PENDING-2 / -4 | **BSB-33 / BSB-26 (run report page, not named)** | The run-page assertions exercise BSB-33's report (BSB-26 owns the layout); the dependency is silent (Finding 6). |
| BSB-32-PENDING-2 / -4 | **BSB-33 / BSB-36 (reviewer-facing scan report, not named)** | The epic summary records the handoff, but no story does; BSB-31-PENDING-5 hands the reviewer view to the same epics (Finding 7). |

No dependency note points at a non-existent story. No note asks this review to compute a build
order; the ordering itself is `sdlc-plan-epic-sequence`'s job.
