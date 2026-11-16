# Epic Review — BSB-23: Integrations, credentials & MCP definitions

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-23-PENDING-1, BSB-23-PENDING-2, BSB-23-PENDING-3, BSB-23-PENDING-4, BSB-23-PENDING-5, BSB-23-PENDING-6

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-23/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** `SkillBuilder-2` has no Jira issue on the configured site: a read-only
  `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not exist or you do not
  have permission to see it"), and the site's project list contains no `SkillBuilder` key
  (`BSB` = `bheembhai-skill-builder` is the only skill-builder project). The Atlassian MCP tools
  were not exposed in this session, so the same site's REST API was queried read-only (GET only;
  no Jira writes). `PRD.md` §8 and `epics.md`'s source note record the same result and ground the
  product in ADR SK-001. The run context (`ITEM`) binds this step to `BSB-23`, and the upstream
  `sdlc-plan-stories-write` artifacts are BSB-23's, so BSB-23 is the epic reviewed.
- **The epic.** `GET /rest/api/3/issue/BSB-23` returned HTTP 200: Epic "Integrations, credentials
  & MCP definitions", status To Do, labels `FA-5`/`MVP`, no parent, no sub-tasks and no issue
  links. Its description (functional scope, implementation guidance, Definition of Done and
  covered requirements) matches the BSB-23 section of `epics.md`; JQL `parent = BSB-23` returns no
  child issues, so the six draft stories are not yet in Jira. `epic-map.json` records BSB-23 under
  FA-5/MVP with FR-029 to FR-036, FR-128, FR-129, NFR-004 and NFR-006.
- **All 6 stories in BSB-23**, from `stories.md` and `story-map.json` in one read each —
  BSB-23-PENDING-1, -2, -3, -4, -5 and -6 (the full set, not a sample).
- **`PRD.md`** — §2 target users (including the test-project owner and the catalog reviewer), §5
  FA-5, §6 the twelve FR rows, §7 NFR-004 and NFR-006, and §8's source note, external
  prerequisites, secrets, test-data and MCP-definition constraints.
- **`epics.md`** — the BSB-23 section (description, functional scope, implementation guidance,
  DoD, covered requirements, Notes), the foreach dependency order, and the sections of the epics
  that consume BSB-23's records: BSB-22 (test projects and the owner-only integration guard),
  BSB-24 (run start), BSB-25 (packaging and run branch), BSB-26 (execution and outcome),
  BSB-28 (Jira fixture seeding), BSB-32 (LLM scan model), BSB-33 (run report) and BSB-36
  (catalog submission).
- **`docs/adr/SK-001-skill-builder.md`** — §1a/§1b (build and Ready), §2/§2a (pinned step kit and the
  env contract, including `BB_MCP_CONFIG` from the selected MCP servers), §3 (Cognito, the
  `skill-builders` group, per-request claim check), §4 (test project, the three integrations, the
  secret path `skill-builder/<project-id>/<integration>`, test-only tokens and the platform-repo
  warning, only the owner changes integrations), §5 (run branches), §6b (scans) and §9 (the
  `users`, `projects`, `project_members` and `integrations` records).
- **`docs/product/epics/BSB-22/_epic/stories.md`** — BSB-22-PENDING-4, which owns
  `GET "/projects/7/settings"`, the "Integrations" section, the "Add integration" link to
  `/projects/7/integrations/new` and the owner-only integration guard, and asserts a denial on
  `POST "/projects/7/integrations"`; and BSB-22-PENDING-2, which defines the shared owner check.
  Also read: `docs/product/epics/BSB-22/_epic/epic-review.md`, whose Finding 2 and Open question 2
  (who owns the guarded `POST /projects/7/integrations` route) are still open and unapplied.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md` are
  not committed; the architecture-design step runs after planning, so ADR SK-001 is the design authority this
  pass can use. No `epic-sequence.md`/`.json` exists for BSB-23; ordering was read only from
  `epics.md`/`epic-map.json` and is not computed here. BSB-23 has no `revisions.md`.
- **Other epic story sets checked:** BSB-18, BSB-19, BSB-20 and BSB-22 have stories on disk. BSB-24,
  BSB-25, BSB-26, BSB-28, BSB-32, BSB-33 and BSB-36 have epic definitions but no stories yet; their
  epic Notes were read to confirm which dependencies are legitimate and written down.

## Findings

### Finding 1 — Verification proves the credential is valid, never that the configured target is reachable
- **Severity:** Blocking
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-2, BSB-23-PENDING-3, BSB-23-PENDING-4.
- **Evidence:**
  - PENDING-1 configures a Jira `site_url` plus exactly one of `project_key` or
    `template_project` (`stories.md:31-48`). PENDING-2 configures `repository
    "saraavrnd/skill-builder-sandbox"` and `base_branch "main"` (`stories.md:118-120`).
    PENDING-3 configures a `base_url` and a `models` mapping whose values are model identifiers
    such as `"claude-opus-5-5"` (`stories.md:202-204`).
  - PENDING-4's story says it exists "so that I know a run can reach its Jira, sandbox repository
    or model before I start it" (`stories.md:273`). Its Notes, however, define only three identity
    calls — for `jira`, `GET <site_url>/rest/api/3/myself`; for `github`, `GET
    "https://api.github.com/user"`; for `ai_model`, `GET <base_url>/v1/models` — and "a 2xx
    response is a pass and any other response is a fail" (`stories.md:331-335`). None of those
    calls reads the project key or template project, the repository or base branch, or the tier
    model identifiers that its three sibling stories configured.
  - PENDING-4's model success AC makes the gap concrete: the model stub returns HTTP 200 with body
    `{"data":[]}` and the scenario still passes (`stories.md:288-290`), so a profile whose three
    configured model identifiers do not exist verifies successfully.
  - `epics.md` BSB-23 DoD says "a verified integration is usable by runs"
    (`epics.md:481-486`); `PRD.md` FR-033 says only "The owner verifies an integration's
    credentials" (`PRD.md:107`).
- **What is missing/ambiguous/contradictory:** The four stories disagree about what "verified"
  means. PENDING-1/-2/-3 record a target; PENDING-4 tests only whether the token/key is accepted by
  a provider's identity endpoint. A credential that is valid but has no access to the configured
  Jira project/template project, sandbox repository/base branch or tier models passes verification,
  so the DoD's "usable by runs" and PENDING-4's "so that I know a run can reach ..." are not
  delivered. Two implementers can read FR-033 (credential validity) and the story value (target
  reachability) and build different checks.
- **Question (if a person must decide):** Should verification prove the configured target is
  reachable and usable — the Jira project or template project exists and is accessible, the
  sandbox repository and base branch exist and the token can read/push, and every tier model
  identifier is present at the base URL — or is credential validity alone the intended meeting of
  FR-033? If the latter, PENDING-4's "so that" and the epic DoD must stop promising run
  reachability, and target reachability must move to run start (BSB-24).
- **Proposed change:**
  - **BSB-23-PENDING-4:** Add the chosen target checks to the provider paths and acceptance
    criteria (or, if credential-only is chosen, reword the story value and Notes so target
    reachability is explicitly BSB-24's check). For Jira, read the stored `project_key` or
    `template_project`; for source control, read the stored `repository` and `base_branch` (and
    check push/read permission); for a model profile, read the stored `models` mapping and verify
    every identifier appears in `/v1/models`.
  - **BSB-23-PENDING-1, -2, -3:** State in each Notes that verification exercises exactly the
    target fields that story stores, so the record and the check cannot drift apart.
  - Same change for all four stories: one agreed meaning of "verified" across the three kinds.

### Finding 2 — The test-purpose attestation is enforced on create but not on edit
- **Severity:** Blocking
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-4, BSB-23-PENDING-5, BSB-23-PENDING-6.
- **Evidence:**
  - `story-map.json` PENDING-6's summary says: "Test-purpose attestation required on **every
    integration save**, recorded as test_only in config with unconfirmed **saves** refused, and
    unconfirmed integrations excluded from the run-purpose integration list that run start
    consumes."
  - `stories.md` PENDING-6 narrows that to creates: "Every integration **create** carries a
    test-purpose confirmation" (`stories.md:472`) and "This story owns the test-purpose
    confirmation field on every integration **create**" (`stories.md:469-470`). Its three ACs cover
    create and the run-purpose filter only; its Out of scope does not exclude edits.
  - PENDING-1 describes the edit path without mentioning `test_only`: "a blank API token keeps the
    stored secret_ref and its secret, and changing the site URL, target or credential clears
    verified_at" (`stories.md:98-101`).
  - PENDING-4's edit AC (`stories.md:307-310`) and PENDING-5's edit AC (`stories.md:388-391`) both
    submit a blank token and assert no `test_only` behaviour. PENDING-5's Notes say "a non-blank
    token replaces the secret-store value at the same path and clears verified_at"
    (`stories.md:420-422`) — again no `test_only` and no confirmation.
  - PENDING-6's run-purpose AC selects only rows whose `config.test_only` is true
    (`stories.md:450-453`). `PRD.md` NFR-006 requires "Runs use only test-purpose Jira,
    source-control and model credentials" (`PRD.md:256`), and the epic's functional scope repeats
    "Ensure runs use only test-purpose Jira, source-control and model credentials"
    (`epics.md:463`).
- **What is missing/ambiguous/contradictory:** An owner can create a confirmed test-only
  integration, then edit it with a non-blank production token. PENDING-5's contract replaces the
  secret in place and clears `verified_at`, but `config.test_only` remains `true`, so PENDING-6's
  run-purpose list still returns the integration and a run uses the production credential. The
  story-map summary already states the intended rule ("every integration save"); the story body
  and ACs implement only half of it.
- **Question (if a person must decide):** Must the test-purpose confirmation be re-supplied on
  every edit, or only on an edit that changes the credential? Should an unconfirmed
  credential-changing edit be refused with HTTP 422 "Runs require test-purpose credentials.", or
  should it clear `test_only` so the run-purpose list excludes the integration until it is
  re-confirmed?
- **Proposed change:**
  - **BSB-23-PENDING-6:** Restore the summary's rule in the story body ("every integration create
    and every edit that changes the credential", or every edit, per the answer), add an AC for the
    edit case (422 without the confirmation; no secret or row change), and state how `test_only` is
    set on a confirmed edit.
  - **BSB-23-PENDING-5:** Add the confirmation and the `test_only` assertion to its edit AC and
    Notes; if the chosen policy clears `test_only` on a credential change, state it.
  - **BSB-23-PENDING-4:** Add the confirmation to its edit AC and Notes.
  - **BSB-23-PENDING-1:** Its edit-contract sentence must state the same rule; it currently defines
    only the secret-preservation and `verified_at` effects.
  - Same change for all four stories: one attestation rule spanning create and edit.

### Finding 3 — The shared create route and the create form page have no single owner
- **Severity:** Blocking
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-2, BSB-23-PENDING-3, BSB-23-PENDING-6.
  Cross-epic: BSB-22-PENDING-4.
- **Evidence:**
  - PENDING-1: "This story fills that section and **owns the Jira create route POST
    "/projects/7/integrations"**" (`stories.md:80-82`).
  - PENDING-2: "This story **owns the source-control create path through POST
    "/projects/7/integrations"**" (`stories.md:168-169`).
  - PENDING-3: "This story **owns the AI model create path through POST
    "/projects/7/integrations"**" (`stories.md:244-246`).
  - PENDING-6: "This story owns the test-purpose confirmation field on every integration create
    and the GET "/api/projects/7/integrations?purpose=run" contract" (`stories.md:469-470`).
  - BSB-22-PENDING-4 asserts a denial on the same route: "When Bob submits a Jira integration
    configuration ... on POST "/projects/7/integrations" Then the builder responds with HTTP 403"
    (`BSB-22/_epic/stories.md:236-239`), and its Notes say "POST "/projects/7/integrations" is the
    representative guarded route used by this story's acceptance criteria"
    (`BSB-22/_epic/stories.md:260-263`). `BSB-22/_epic/epic-review.md` Finding 2 and Open question 2
    already ask who owns that route; the question is open and unapplied.
  - BSB-22-PENDING-4's settings page renders "the link "Add integration" whose target is
    "/projects/7/integrations/new"" (`BSB-22/_epic/stories.md:226-229`) and its Notes assign "The
    integration form, its configuration fields, the opaque secret reference and the verification
    step" to BSB-23 (`BSB-22/_epic/stories.md:260-263`). No BSB-23 story defines
    `GET "/projects/7/integrations/new"`; PENDING-1's Notes only reproduce the link as
    BSB-22-PENDING-4's (`stories.md:78-80`).
- **What is missing/ambiguous/contradictory:** Four stories claim or assert the same
  `POST /projects/7/integrations` route, and no story owns its skeleton, kind dispatch or
  validation order (owner guard → test-purpose confirmation → MCP credential validation → kind
  branch). Three implementers can build three handlers, or one can build a Jira-only handler while
  PENDING-2/-3 assume it dispatches. Separately, the create form page that BSB-22-PENDING-4 links
  to and explicitly hands to BSB-23 is owned by nobody: no BSB-23 AC or Notes define it, so the
  "Add integration" link has no destination.
- **Question (if a person must decide):** Should BSB-23-PENDING-1 own the shared
  `POST /projects/7/integrations` route skeleton and the `GET /projects/7/integrations/new` form,
  with the owner guard and test-purpose/MCP validation in one documented order, and PENDING-2/-3
  owning only the `github` and `ai_model` kind branches and field sets? Does that answer BSB-22's
  Open question 2, or does BSB-22-PENDING-4 keep a minimal guarded route that BSB-23 extends?
- **Proposed change:**
  - **BSB-23-PENDING-1:** Add Notes and ACs owning the shared create route and the create form
    page: the route performs the owner guard, the test-purpose confirmation, the MCP
    credential check and kind dispatch in that order; the form renders the kind choice and the
    Jira field set. Keep the Jira-specific validation and row creation.
  - **BSB-23-PENDING-2:** State it extends PENDING-1's shared route with the `github` branch
    (validation, uniqueness and row creation) and its field set on PENDING-1's form, not a second
    route or page.
  - **BSB-23-PENDING-3:** Same for the `ai_model` branch and field set.
  - **BSB-23-PENDING-6:** State the confirmation is a shared pre-dispatch step called by
    PENDING-1's route, not a separate route.
  - **Cross-epic (not applied here):** BSB-22-PENDING-4's route assertion must adopt the answer to
    BSB-22 Open question 2; if BSB-22 keeps the minimal guarded route, PENDING-1 calls it and does
    not create a second skeleton.

### Finding 4 — The Jira edit route is exercised by two stories but owned by none
- **Severity:** Blocking
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-2, BSB-23-PENDING-4, BSB-23-PENDING-5.
- **Evidence:**
  - PENDING-1's Notes describe the edit behaviour but claim only the create route: "Editing an
    existing Jira integration is POST "/projects/7/integrations/3": a blank API token keeps the
    stored secret_ref and its secret, and changing the site URL, target or credential clears
    verified_at so a stale verification never applies to different settings (**BSB-23-PENDING-4
    and BSB-23-PENDING-5 exercise the edit path**)" (`stories.md:97-103`). Its ownership sentence
    is "owns the Jira create route" (`stories.md:80-82`).
  - PENDING-4 owns "POST "/projects/7/integrations/3/verify" and the "Verify" control"
    (`stories.md:325-327`), not the edit route; its AC "Changing the verification target clears the
    last verification time" submits site URL and project key "on POST
    "/projects/7/integrations/3"" and expects "Jira integration 3 updated."
    (`stories.md:307-310`).
  - PENDING-5 owns "the single redaction rule" (`stories.md:405-410`), not the edit route; its AC
    "Editing an integration preserves the stored secret" also submits on
    `POST "/projects/7/integrations/3"` and expects "Jira integration 3 updated."
    (`stories.md:388-391`).
  - PENDING-2 contains no sentence about editing the source-control integration and no Out of
    scope exclusion for it; PENDING-3 explicitly excludes "editing or deleting a profile"
    (`stories.md:239-240, 262`).
  - The edit contract covers the secret and `verified_at` only. Neither PENDING-1, PENDING-4 nor
    PENDING-5 says whether an edit that omits the MCP definition preserves the stored
    `integrations.mcp`, although FR-128 requires the Jira MCP definition to be recorded
    (`PRD.md:202`) and PENDING-1's create AC stores it (`stories.md:32-33`).
- **What is missing/ambiguous/contradictory:** Two acceptance criteria cannot pass unless someone
  builds `POST /projects/7/integrations/3`, but no story claims ownership of it. An implementer of
  PENDING-4 or PENDING-5 can build a throwaway handler or treat the edit as a full replace that
  wipes `integrations.mcp` and leaves the run without the Jira MCP definition. The source-control
  edit boundary is neither owned nor excluded, so the epic's boundary is uneven.
- **Question (if a person must decide):** Is editing an existing integration in scope for BSB-23?
  If yes, which story owns the Jira edit route and the source-control edit route, and does an edit
  that omits the MCP definition preserve the stored `integrations.mcp`? If no, what replaces the
  two edit ACs as the way to test `verified_at` clearing and secret preservation — a fixture-level
  update, or a different route — and which Out of scope says so?
- **Proposed change:**
  - **BSB-23-PENDING-1:** State that it owns `POST "/projects/7/integrations/3"` (the Jira edit) in
    addition to the create route, and write the full contract: a blank token preserves
    `secret_ref`, the stored secret and `integrations.mcp`; a non-blank token replaces the secret
    and clears `verified_at`; a site URL/target change clears `verified_at`; an edit that changes
    none keeps it; the confirmation rule from Finding 2 applies.
  - **BSB-23-PENDING-2:** Either own the analogous source-control edit branch with the same rules
    (including recomputing the overlap warning), or state in Out of scope that editing the
    source-control integration is not in this epic.
  - **BSB-23-PENDING-4:** Change "exercise the edit path" to "exercise PENDING-1's edit route";
    keep ownership of the verify route and control.
  - **BSB-23-PENDING-5:** Same for its edit AC; keep ownership of the redaction rule.
  - Same change for all four stories: one owner and one edit contract, including MCP preservation.

### Finding 5 — The run-purpose integration list contract is underspecified for BSB-24
- **Severity:** Advisory
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-2, BSB-23-PENDING-3, BSB-23-PENDING-4,
  BSB-23-PENDING-6. Cross-epic: BSB-24.
- **Evidence:**
  - PENDING-6 owns `GET "/api/projects/7/integrations?purpose=run"` (`stories.md:469-470`). Its
    only AC returns `{"integrations":[{"id":4,"kind":"ai_model","name":"Default"}]}` from two
    `ai_model` rows (`stories.md:450-453`). No AC returns a `jira` or `github` row, and neither of
    those configs has a `name` field (PENDING-1 and PENDING-2 store `site_url`,
    `project_key`/`template_project`, `repository` and `base_branch`).
  - PENDING-6's Notes say "Depends on ... on BSB-24 for the run-start choices that consume the
    run-purpose list" (`stories.md:466-470`). The endpoint does not need BSB-24; BSB-24 is the
    consumer of the endpoint PENDING-6 supplies.
  - BSB-24's Notes say "Depends on the test-project membership check, the source-control and model
    integrations, and the externally supplied sandbox branches and platform workflow definitions"
    (`epics.md:709-713`), and its functional scope says "Validate the selections against the
    project's configured integrations and the sandbox repository" (`epics.md:677-678`). Neither
    its Notes nor its implementation guidance names the `purpose=run` list, `test_only`, or
    `verified_at`.
  - PENDING-6's AC is run by Ada (the owner); there is no non-member or non-owner case. BSB-24's
    run start is member-accessible (BSB-22-PENDING-3), so the list's caller can be a member.
  - The epic DoD says "a verified integration is usable by runs" (`epics.md:481-486`), but
    PENDING-6's filter is `config.test_only is true` only (`stories.md:477-481`); a row with
    `verified_at NULL` is still returned. PENDING-4 creates every integration with
    `verified_at NULL` (`stories.md:33, 120, 204`).
- **What is missing/ambiguous/contradictory:** The one interface between this epic and run start
  has no agreed item shape for Jira and source-control rows, no stated access rule, and no answer
  on whether verification gates selection. BSB-24 cannot implement against it without guessing,
  and the dependency note points in the wrong direction.
- **Question (if a person must decide):** (a) Does `purpose=run` return all three kinds, and what
  fields does each item carry (for example `{id, kind, name?}` plus `site_url`/`repository`)?
  (b) May any project member call it, matching run start, or only the owner? (c) Is `verified_at`
  a selection criterion (only verified integrations are offered), or is verification advisory?
  (d) Is BSB-24 the consumer rather than a prerequisite?
- **Proposed change:**
  - **BSB-23-PENDING-6:** Define the item shape for `jira`, `github` and `ai_model`; state the
    project-membership access rule; state the `verified_at` rule; add an AC that returns a `jira`
    or `github` row and an AC for the member/owner boundary; correct the dependency sentence to
    "BSB-24 consumes this endpoint" and list it as a supplied contract, not a prerequisite.
  - **BSB-23-PENDING-1, -2, -3:** State in their Notes which stored fields the run-purpose item
    exposes for their kind, so PENDING-6's contract matches the records they create.
  - **BSB-23-PENDING-4:** State whether `verified_at NULL` means "not offered to runs" or
    "offered with a not-verified marker"; PENDING-6 needs that decision.
  - **Cross-epic (not applied here):** BSB-24's stories must read the `purpose=run` list, apply the
    same membership guard, and name the test-purpose/verified filter they rely on.

### Finding 6 — The redaction helper's contract with BSB-26 and BSB-33 is one-sided and incomplete
- **Severity:** Advisory
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-4, BSB-23-PENDING-5. Cross-epic:
  BSB-26, BSB-33.
- **Evidence:**
  - PENDING-5's Notes: "The run result writer and the run report are built by BSB-26 and BSB-33;
    this story owns the shared redaction they call, and its run-result scenario exercises that
    writer against a persisted result fixture. Redaction replaces any occurrence of the resolved
    credential value with the literal text "[REDACTED]"" (`stories.md:412-422`).
  - BSB-26's epic Notes (`epics.md:735-745`) do not mention BSB-23 or a redaction helper; its
    implementation step 2 says "Stream progress and logs ... without storing credential values"
    (`epics.md:727-730`), which covers live logs, not the persisted result document. BSB-33's
    Notes (`epics.md:1103-1111`) do not mention redaction or BSB-23 at all.
  - PENDING-5's log AC requires the captured log to contain
    `"secret_ref=skill-builder/7/integration-3"` (`stories.md:378-381`). PENDING-1's save path and
    PENDING-4's verify path say only that no response, page or log echoes the credential value
    (`stories.md:84-92, 339`); neither story requires or owns the positive `secret_ref=` log line
    the redaction AC asserts.
  - The helper's input is unstated. PENDING-5 says redaction replaces "the resolved credential
    value", but the run record stores only `secret_ref` (ADR SK-001 §9), so the result writer
    must be handed the resolved values (or resolve them itself) — neither is specified.
- **What is missing/ambiguous/contradictory:** The cross-epic dependency is claimed only on
  BSB-23's side, and the helper's input contract and the positive log assertion have no owner. A
  BSB-26 implementer reading only its own epic can build a result writer that never calls the
  helper; PENDING-5's ACs then fail, or pass only against the fixture without proving the real
  writer is wired.
- **Question (if a person must decide):** How does the result writer obtain the resolved credential
  values at write time — does the runner pass the values (or the project's secret refs) to the
  helper, or does the helper resolve them itself? And which story owns the `secret_ref=` log line
  the redaction AC asserts?
- **Proposed change:**
  - **BSB-23-PENDING-5:** Define the helper contract: input is the text/document plus the resolved
    credential values for the run's project integrations; output is the text with every occurrence
    of a value replaced by `"[REDACTED]"`, while `secret_ref` is never redacted. State that
    BSB-26's result writer and BSB-33's report call it with those values, and add the positive
    log-line sentence or move that assertion to the story that owns the log.
  - **BSB-23-PENDING-1 and BSB-23-PENDING-4:** State which one owns the save/verify log line that
    records `secret_ref` and never the value; the other references it.
  - **Cross-epic (not applied here):** BSB-26's and BSB-33's stories must name the BSB-23 redaction
    helper and pass it the resolved values.

### Finding 7 — MCP definitions are recorded but no story or epic owns delivering them to a run
- **Severity:** Advisory
- **Stories touched:** BSB-23-PENDING-1, BSB-23-PENDING-2. Cross-epic: BSB-24, BSB-25, BSB-26.
- **Evidence:**
  - PENDING-1's Notes: "The MCP definition is non-secret configuration stored in
    "integrations.mcp" and is passed to a run as configuration, never as a credential"
    (`stories.md:84-92`).
  - PENDING-2 stores "the submitted MCP definition in mcp" (`stories.md:118-120`) but its Notes do
    not say how it reaches a run.
  - `epics.md` BSB-23 DoD: "MCP server definitions are stored as non-secret configuration and are
    available to a run" (`epics.md:485-486`). ADR SK-001 §2a lists `BB_MCP_CONFIG` from the
    selected MCP servers in the env contract (`SK-001:152-160`).
  - BSB-24's functional scope and implementation guidance (`epics.md:667-694`) and its Notes
    (`epics.md:709-713`) never mention MCP. BSB-25's and BSB-26's Notes (`epics.md:771-777,
    735-745`) do not mention MCP either.
- **What is missing/ambiguous/contradictory:** The epic promises MCP availability to a run, but the
  delivery crosses into the run epics and no dependency is written on the consuming side. A
  BSB-24/BSB-25/BSB-26 implementer reading only those epics would not build the
  `integrations.mcp` → `BB_MCP_CONFIG` path, leaving FR-128/FR-129's "exposes to a run" half
  delivered.
- **Question (if a person must decide):** Which run epic owns building `BB_MCP_CONFIG` from
  `integrations.mcp` — BSB-24 (when it selects the integrations/MCP servers) or BSB-25/BSB-26
  (when it builds the container env)? Should PENDING-1 and PENDING-2 name that owner in their
  Notes?
- **Proposed change:**
  - **BSB-23-PENDING-1 and BSB-23-PENDING-2:** In Notes, name the consumer and the contract: "The
    `integrations.mcp` value is non-secret; [the chosen run epic] selects it and builds
    `BB_MCP_CONFIG`. This epic records it only." Use whichever owner the answer names.
  - **Cross-epic (not applied here):** BSB-24, BSB-25 and BSB-26 must read `integrations.mcp` and
    build `BB_MCP_CONFIG`; their Notes should say so.

## Open questions

1. **Verification depth (Finding 1).** Should verification prove the configured target is
   reachable — Jira project/template project, sandbox repository/base branch and push permission,
   every tier model identifier — or is credential validity alone enough? If credential-only, which
   text (PENDING-4's story value and the epic DoD) changes so run reachability is not promised?
2. **Edit scope and ownership (Finding 4).** Is editing an existing integration in scope? Which
   story owns the Jira edit route and the source-control edit route, and does an edit that omits
   the MCP definition preserve `integrations.mcp`? If editing is out of scope, what replaces the
   two edit ACs?
3. **Test-purpose re-attestation (Finding 2).** Is the confirmation required on every edit, or
   only on a credential-changing edit? Should an unconfirmed edit be refused, or should it clear
   `test_only` and be excluded from the run-purpose list until re-confirmed?
4. **Create route and form ownership (Finding 3).** Does PENDING-1 own the shared
   `POST /projects/7/integrations` route and the `GET /projects/7/integrations/new` form, with
   PENDING-2/-3 owning kind branches and field sets? Does that answer BSB-22's Open question 2, or
   does BSB-22-PENDING-4 keep a minimal guarded route?
5. **Run-purpose list contract (Finding 5).** What item fields does it return for Jira and
   source-control, may any project member call it, and is `verified_at` a selection criterion or
   an advisory marker?
6. **Redaction helper input (Finding 6).** How does the result writer obtain the resolved
   credential values at write time, and which story owns the `secret_ref=` log line?
7. **MCP delivery owner (Finding 7).** Which run epic builds `BB_MCP_CONFIG` from
   `integrations.mcp` — BSB-24, BSB-25 or BSB-26?

## Proposed changes

`docs/product/epics/BSB-23/_epic/stories.md` (proposed only; `sdlc-plan-stories-write` applies
them):

- **BSB-23-PENDING-1** — Notes/ACs: own the shared `POST /projects/7/integrations` route and the
  `GET /projects/7/integrations/new` form (Findings 3); own the Jira edit route
  `POST /projects/7/integrations/3` with the full secret/`verified_at`/`mcp` contract (Finding 4);
  state the test-purpose rule on edit (Finding 2); name the target fields verification reads
  (Finding 1); name the consumer that builds `BB_MCP_CONFIG` (Finding 7). Keep the Jira-specific
  validation, MCP credential rule and row creation.
- **BSB-23-PENDING-2** — Notes/ACs: extend PENDING-1's shared route and form as the `github` branch
  and field set, not a second route (Finding 3); own the source-control edit branch or state it
  is out of scope (Finding 4); state the target fields verification reads (Finding 1); name the
  `BB_MCP_CONFIG` consumer for the source-control MCP definition (Finding 7).
- **BSB-23-PENDING-3** — Notes/ACs: extend PENDING-1's shared route and form as the `ai_model`
  branch and field set (Finding 3); state the target fields verification reads (Finding 1); state
  which stored model fields the run-purpose list exposes (Finding 5).
- **BSB-23-PENDING-4** — Notes/ACs: add the chosen target checks or narrow the story value
  (Finding 1); add the test-purpose confirmation to the edit AC and Notes (Finding 2); reference
  PENDING-1's edit route instead of only "exercising" it (Finding 4); state whether
  `verified_at NULL` is offered to runs (Finding 5); own the `secret_ref=` log line or defer it to
  PENDING-1 (Finding 6).
- **BSB-23-PENDING-5** — Notes/ACs: add the test-purpose confirmation to the edit AC and Notes
  (Finding 2); reference PENDING-1's edit route (Finding 4); define the redaction helper's input
  and output contract and its BSB-26/BSB-33 consumers (Finding 6).
- **BSB-23-PENDING-6** — Notes/ACs: restore "every integration save" in the body and add the edit
  case (Finding 2); state the confirmation is a shared pre-dispatch step on PENDING-1's route
  (Finding 3); define the run-purpose item shape for all three kinds, the access rule, the
  `verified_at` rule and the corrected dependency direction (Finding 5).
- **`story-map.json`** — No requirement ID or story-set change. PENDING-6's summary already says
  "every integration save"; after the revision, the story body and ACs must match it. No other
  summary needs a change.

Cross-epic follow-ups (not applied in this pass; they need their own epic revisions or a human
decision):

- **BSB-22** — Answer Open question 2 and align BSB-22-PENDING-4's `POST
  /projects/7/integrations` assertion with the route owner chosen here; keep its guard contract
  and the `/projects/7/integrations/new` link.
- **BSB-24** — Read the `GET /api/projects/7/integrations?purpose=run` contract, apply the
  project-membership guard, and name the test-purpose/verified filter it relies on; name the MCP
  selection it hands to the run env and `BB_MCP_CONFIG`.
- **BSB-25 / BSB-26** — Build `BB_MCP_CONFIG` from `integrations.mcp` (or state where it is
  built) and call BSB-23's redaction helper with the resolved credential values.
- **BSB-33** — Call BSB-23's redaction helper when rendering the run report and name the
  dependency.

No change is proposed to `epic-map.json`, the requirement IDs, the story set, `sdlc-tracker-sync`
or Jira.

## Architecture impact

None. Every finding is a story-boundary, shared-contract, access-rule or dependency-note issue.
The records and rules the stories rely on already exist in ADR SK-001: §9's `integrations` table
(`id`, `project_id`, `kind`, `config`, `secret_ref`, `mcp`, `verified_at`), §4's secret path
`skill-builder/<project-id>/<integration>` and owner rule, and §2a's `BB_MCP_CONFIG` env contract.
Finding 1's target checks use provider endpoints, not new stored fields; Finding 5's run-purpose
list is a query over `integrations.config`; Finding 4's edit route writes the same `integrations`
row. No new entity, field, endpoint or integration is required beyond what the stories already
define, and no design-stage change is needed before `sdlc-plan-stories-write` (revise) applies
this report.

## Requirement coverage check

Yes for all twelve requirements, with traceability caveats that the findings above must close; no
requirement is claimed by two stories in contradictory ways, and no FR/NFR wording drift was found
between `epic-map.json` and the current `PRD.md`.

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-029 | BSB-23-PENDING-1 | "The owner saves a Jira integration with a project key" (HTTP 201, `kind "jira"`, `project_key "BSB"`, `test_only true`, `secret_ref`) and "A template project can stand in for a project key"; rejects both/neither target, non-https and blank token. |
| FR-030 | BSB-23-PENDING-2 | "The owner saves a source-control integration for a sandbox repository" (HTTP 201, `kind "github"`, `repository`, `base_branch`, `test_only true`); rejects malformed repository, blank base branch and a second integration. |
| FR-031 | BSB-23-PENDING-3 | "The owner saves an AI model profile" (HTTP 201, `vendor`, `base_url`, `models`, `test_only true`); rejects a missing/unknown tier, non-https base URL and duplicate name. |
| FR-032 | BSB-23-PENDING-5 | "Saving an integration stores only a secret reference": a search of every text column of every builder table finds zero occurrences of the token; the row holds only `secret_ref`. |
| FR-033 | BSB-23-PENDING-4 | "A Jira integration verifies successfully and records the time", "A source-control integration verifies successfully", "An AI model profile verifies successfully" (one provider call, HTTP 200, timestamp). **Caveat:** the checks prove credential validity, not target reachability (Finding 1). |
| FR-034 | BSB-23-PENDING-4 | The same success scenarios stamp `verified_at` and render `Last verified: ...`; "A rejected credential is reported and the previous verification time is kept"; "Changing the verification target clears the last verification time". |
| FR-035 | BSB-23-PENDING-2 | "A repository used by a platform project is saved with a warning" (HTTP 201 plus the exact warning; settings page renders it); "An unavailable platform inventory is reported and does not block the save". |
| FR-036 | BSB-23-PENDING-5 | "The settings page masks the credential": renders `"Credential: stored in secret manager"` and zero occurrences of the token. |
| FR-128 | BSB-23-PENDING-1 | The create AC stores "the submitted MCP definition in mcp" and the create/duplicate/MCP-credential rejections exercise the non-secret rule. **Caveat:** no AC exercises "exposes to a run" (Finding 7). |
| FR-129 | BSB-23-PENDING-2 | The create AC stores "the submitted MCP definition in mcp" and the credential-bearing MCP rejection exercises the non-secret rule. **Caveat:** no AC exercises "exposes to a run" (Finding 7). |
| NFR-004 | BSB-23-PENDING-5 | "The application log redacts the credential" (log contains `secret_ref=...`, zero occurrences of the value) and "A run result redacts the credential" (stored document and rendered report contain `"[REDACTED]"`). |
| NFR-006 | BSB-23-PENDING-6 | "A create without the test-purpose confirmation is rejected" (HTTP 422, no row/secret) and "An unconfirmed integration is excluded from run selection" (`purpose=run` returns only `test_only true`). **Caveat:** creates only; an edit can introduce a new credential without re-attestation (Finding 2). |

Traceability notes: the epic-map/PRD rows for all twelve requirements match the Jira BSB-23
description and `epics.md`. `story-map.json`'s PENDING-6 summary says "every integration save"
while `stories.md` says "create" — the mismatch is Finding 2, not a requirement change. FR-128 and
FR-129 are recorded but their "available to a run" half has no exercising story (Finding 7).

## Dependency-note sanity check

Mostly consistent; five cross-story/cross-epic mismatches (Findings 2, 4, 5, 6 and 7) and one
open cross-epic route question (Finding 3).

- **Reciprocated and real within the epic:** PENDING-2/-3/-4/-5/-6 each say they depend on
  PENDING-1, and PENDING-1's Out of scope names all of them. PENDING-4/-5/-6 name PENDING-2/-3,
  and those stories' Out of scope name PENDING-4/-5/-6. PENDING-6's dependency on the three kinds
  is reciprocated by PENDING-1/-2/-3's Out of scope. No draft key is dangling.
- **Reciprocated cross-epic:** PENDING-1 to PENDING-6 name BSB-22-PENDING-4 for the settings page
  and owner guard, and BSB-22-PENDING-4's Notes say BSB-23 must call that guard. PENDING-2 names
  BSB-25/BSB-36's source-control dependency, and BSB-25 and BSB-36's Notes reciprocate.
  PENDING-3 names BSB-32 for the LLM-scan model, and BSB-32's Notes reciprocate. PENDING-1 names
  BSB-28 for Jira fixture seeding, and BSB-28's Notes reciprocate.
- **One-sided — Finding 5:** PENDING-6 says it depends on BSB-24 for the run-start choices that
  consume the run-purpose list, but BSB-24 is the consumer, not a prerequisite; BSB-24's Notes do
  not name the `purpose=run` list, `test_only` or `verified_at`.
- **One-sided — Finding 6:** PENDING-5 says BSB-26 and BSB-33 call its shared redaction, but
  neither epic's Notes mention BSB-23 or a redaction helper. PENDING-5's log AC also asserts a
  positive `secret_ref=` line that no sibling story owns emitting.
- **One-sided — Finding 7:** PENDING-1 says the MCP definition "is passed to a run", and
  PENDING-2 stores one, but BSB-24, BSB-25 and BSB-26 never mention MCP or `BB_MCP_CONFIG`.
- **Unowned — Finding 4:** PENDING-4 and PENDING-5 exercise `POST
  /projects/7/integrations/3`, and PENDING-1 describes it, but no story's Notes says it owns that
  route; PENDING-2 neither owns nor excludes a source-control edit.
- **Open cross-epic — Finding 3:** BSB-22-PENDING-4 asserts on `POST
  /projects/7/integrations` and claims the owner-only integration guard, while PENDING-1/-2/-3
  each claim the create path on the same route; BSB-22's own epic-review Open question 2 is still
  open. `epics.md` orders BSB-22 before BSB-23, but this report does not compute a build order.
- **Ordering not computed:** no `epic-sequence.md`/`.json` exists for BSB-23; sequencing remains
  `sdlc-plan-epic-sequence`'s job. This pass only records the dependency gaps.

---

*On approval: `docs/product/epics/BSB-23/_epic/stories.md` is updated in place for
BSB-23-PENDING-1 through -6 (and the PENDING-6 summary/body alignment in `story-map.json`). No
Jira keys exist yet for these draft stories, and no Jira write is made in this pass. Next:
`sdlc-plan-stories-write` (revise), then `sdlc-plan-epic-sequence` and the per-story review for
single-story concerns this epic-level pass deliberately did not raise.*
