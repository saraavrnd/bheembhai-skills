# Epic Review — BSB-36: Catalog submission

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-36-PENDING-1, BSB-36-PENDING-2, BSB-36-PENDING-3, BSB-36-PENDING-4

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-36/_epic/epic-review.md`.

## Context loaded

- **Work item and epic.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item
  umbrella rather than a Jira issue. A read-only `GET /rest/api/3/issue/SkillBuilder-2` returned
  HTTP 404 ("Issue does not exist or you do not have permission to see it."), matching
  `PRD.md:4,273-277` and the source note in BSB-36's own `stories.md:16-25`. No Atlassian MCP tool
  was exposed to this reviewer session (the session's tool set contains none), so the configured
  site (`https://saraavrnd.atlassian.net`) was queried read-only through its REST API (GET only;
  no Jira writes). The run context's epic item is **BSB-36**; the branch HEAD (`d64c83f`) is the
  `sdlc-plan-stories-write` step (run `1a45cd21-9fc5-46ec-94d2-ea793cde7a04`) that wrote
  `BSB-36/_epic/stories.md` and `story-map.json`, and `config/sdlc-wf-planning-epic.yaml:20-31`
  runs `sdlc-plan-epic-review` immediately after that step for the same epic. Jira
  `GET /rest/api/3/issue/BSB-36` returned HTTP 200: Epic **"Catalog submission"**, status
  **To Do**, labels **FA-15, MVP**, no parent, no subtasks. BSB-36 has no prior `epic-review.md`
  and no `revisions.md`, so this is the first review pass.
- **All 4 stories in the epic**, from `stories.md` (lines 1-453) and `story-map.json` in one read
  each: BSB-36-PENDING-1 (FR-107, the Submit control and the submission-time readiness refusal),
  BSB-36-PENDING-2 (FR-108 to FR-111 and FR-115, the pull request and its evidence),
  BSB-36-PENDING-3 (FR-112, FR-113 and FR-161, the recorded URL/state and the lifecycle) and
  BSB-36-PENDING-4 (FR-114, save-after-submission and refresh of the same pull request) — the
  full set, not a sample. The coverage table at `stories.md:107-120` maps the same ten
  requirements one-to-one to named acceptance criteria.
- **`PRD.md`** — §2's catalog-reviewer definition (`PRD.md:16`), §5 FA-15 (`PRD.md:64`), §6
  FR-107 to FR-115 and FR-161 (`PRD.md:181-189,235`), §7 NFR-004 and NFR-006 (`PRD.md:254,256`),
  §8's source note and release-split caveat. `epic-map.json` assigns BSB-36 exactly FR-107 to
  FR-115 and FR-161, with no NFR.
- **`epics.md`** — the BSB-36 section (`epics.md:1270-1340`): description, functional scope, the
  seven-step implementation guidance (step 1 "Re-check readiness at the current head SHA … do not
  trust a cached Ready flag", step 7 "Add guards and tests proving there is no direct write path"),
  the Definition of Done, the ten covered requirements and the non-goals ("merging the pull
  request, administering the catalog review workflow, and bypassing the Ready gate"). Also read
  the epics this epic hands work to or depends on: BSB-21 build state and readiness invalidation
  (`epics.md:329-385`), BSB-22 projects and membership (`:386-438`), BSB-23 integrations and
  credentials (`:439-510`), BSB-30 readiness (`:979-1046`), BSB-31 static scans (`:511-587`),
  BSB-32 LLM scans (`:588-656`) and BSB-33 run report (`:1047-1113`).
- **`docs/adr/SK-001-skill-builder.md`** — §1a/§1b (build branches and Ready, `SK-001:63-115`),
  §3 (the `skill-builders` gate, `:176-189`), §4 (the GitHub integration credential: "Token
  scoped to the sandbox repo, plus push access to `build/*` branches of `bheembhai-skills` and PR
  creation", `:190-211`), §5 (a build is a branch of `bheembhai-skills`, `:213-255`), §6b
  (security scan, `:284-322`), §8 ("The PR is opened with the user's own GitHub identity, so the
  author is the person, not the app", `:330-343`) and §9's data model (`:345-357`), whose
  `builds` row names `pr_url` and `state` but not the three columns this epic adds.
- **Sibling stories this epic reads from or hands to:** BSB-20-PENDING-2 (the fixed branch reset
  and the branch-deletion hand-off, `BSB-20/_epic/stories.md:162-204`); BSB-22-PENDING-1 (Project
  Atlas, `projects.owner_id`, and the `project_members` role `owner`/`member` rows,
  `BSB-22/_epic/stories.md:27-69`) and -PENDING-3 (the shared membership check and its exact 403
  "You are not a member of this project.", `:204-212`); BSB-23-PENDING-2 (the `github`
  integration, its `config`, `secret_ref` and secret, `BSB-23/_epic/stories.md:107-189`) and
  -PENDING-4 (credential verification, `:266-...`, the `github` case at `:282-285`); BSB-31's
  scan-report route and its authoring-gate-only access rule (`BSB-31/_epic/stories.md:340-362`);
  BSB-32-PENDING-2 (the LLM report rendered through the same `GET /scans/{id}`,
  `BSB-32/_epic/stories.md:104,158-161`); BSB-33-PENDING-1 (the run report route and its
  project-membership 403, `BSB-33/_epic/stories.md:80-120`).
- **Prior reviews read for precedent:** BSB-22's review Finding 1 (Blocking: the reports linked
  from a catalog PR and their access rule), BSB-31's review Finding 5 (Blocking: the catalog
  reviewer cannot open the scan report) and BSB-33's review Findings 1-2 (Blocking: the
  reviewer-facing report view and its access rule have no owner). BSB-34's and BSB-35's reviews
  supplied the severity calibration and report structure.
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md`.
  There is therefore no project-wide API or UI convention for the routes and page controls this
  epic adds; the review relies on ADR SK-001 and the owning stories named above.

## Findings

### Finding 1 — Cross-epic scope & actor: the catalog reviewer cannot open either report the pull-request description links, and no epic owns a reviewer-readable view

- **Severity:** Blocking
- **Stories touched:** BSB-36-PENDING-2 (primary, FR-110/FR-111); BSB-36-PENDING-1, -3 and -4
  repeat the deferral in their Out-of-scope sections. Cross-epic: BSB-22-PENDING-3,
  BSB-31-PENDING-5, BSB-32-PENDING-2, BSB-33-PENDING-1.
- **Evidence:**
  - `stories.md:96-105` records the gap and explicitly declines to close it: "the run report
    applies BSB-22's project-membership check and the scan report BSB-18's skill-builders gate.
    `PRD.md` section 2 says the catalog reviewer 'Consumes the catalog pull request and its linked
    run and scan reports; does not use the authoring interface', so a reviewer outside those gates
    cannot open the links. … These stories satisfy FR-110 and FR-111 by linking the reports that
    exist and do not invent a reviewer access rule; the access decision must be made before the
    catalog review flow can rely on those links."
  - BSB-36-PENDING-2's Out of scope repeats it: "making the linked reports readable by a catalog
    reviewer (recorded as an unresolved cross-epic gap above)" (`stories.md:263-264`); the same
    line appears in PENDING-3 (`:352-353`) and PENDING-4 (`:425-426`).
  - The two link targets are gated exactly as the stories say. BSB-33-PENDING-1's "A non-member
    cannot read a run report" returns HTTP 403 "You are not a member of this project." for
    `GET "/projects/7/runs/21"` (`BSB-33/_epic/stories.md:80-89`), and its Notes confirm the
    access is "the authenticated session plus the project-membership check from BSB-22"
    (`:114-120`). BSB-31-PENDING-5 states its scan route "is gated by BSB-18's signed-in
    skill-builder check only" and hands "the reviewer-facing stable report view and its access
    rule" to BSB-33/BSB-36 (`BSB-31/_epic/stories.md:350-362`); BSB-32-PENDING-2 reuses that
    route (`:104,158-161`). `PRD.md:16` defines the catalog reviewer as not using the authoring
    interface at all.
  - The gap is already Blocking in the sibling reviews, and each one hands it here: BSB-22's
    review Finding 1, BSB-31's review Finding 5 (its cross-epic follow-up asks "BSB-36 / BSB-33 —
    Own the stable reviewer-facing scan-report view and its access rule, or the PRD's reviewer
    assumption is corrected") and BSB-33's review Finding 2. BSB-36 now records the same gap and
    assigns it to nobody, so the pointer has come full circle.
- **What is missing/ambiguous/contradictory:** BSB-36 is the epic whose FR-110/FR-111 links the
  catalog reviewer is given, but it declares the linked reports' readability out of scope and
  leaves the access rule unresolved. The result is an epic whose own value statement
  ("a catalog reviewer can judge the change from evidence recorded at that exact commit",
  `stories.md:211`) cannot be achieved by the named audience: the run link 403s for a non-member
  and the scan link 403s for a non-`skill-builders` user. A person must decide whether a reviewer
  view exists, where it lives and what authorizes it.
- **Question (if a person must decide):** Do catalog reviewers read the linked run report and
  scan reports without the authoring gate and the project-membership check? If yes, which epic
  and story own that view (BSB-36 with its PR links, BSB-33, BSB-31/32, or a new story), what
  route renders it, and what authorizes a reviewer (a signed read-only share link, a separate
  reviewer role/group, or a public view)? If no — reviewers must be project members or
  `skill-builders` members — then PRD §2's "does not use the authoring interface" is wrong and
  FR-110/FR-111 must be narrowed, and BSB-36's story value must be corrected. (also Open
  question 1)
- **Proposed change:**
  - **BSB-36-PENDING-2:** point the two description links at the answer's route, and state the
    access rule for each link (or, if the answer narrows the requirement, reword the "so that"
    clause to the reader who can actually open it). Add the chosen owner to Notes/dependencies.
  - **BSB-36-PENDING-1, -3, -4:** replace the repeated "recorded as an unresolved cross-epic gap
    above" with the resolved owner and rule, or with the explicit narrowing; do not leave the
    wording "unresolved" after the gate answers.
  - **Cross-epic (revise pass, not applied here):** whichever epic owns the view must add the
    route and authorization ACs, and BSB-22-PENDING-3's shared membership check must be scoped to
    author-facing surfaces. If the answer is narrowing, `PRD.md` §2 and FR-110/FR-111 change.
    Resolve this together with BSB-22's Open question 1, BSB-31's Finding 5 and BSB-33's
    Finding 2.

### Finding 2 — Cross-story & cross-epic actor/identity: "the author" is the submitting project owner, not `builds.created_by`, and nothing guarantees the stored integration token is that owner's personal source-control identity (FR-108)

- **Severity:** Blocking
- **Stories touched:** BSB-36-PENDING-1, BSB-36-PENDING-2, BSB-36-PENDING-3,
  BSB-36-PENDING-4. Cross-epic: BSB-23-PENDING-2, BSB-23-PENDING-4.
- **Evidence:**
  - BSB-36-PENDING-1's Notes make submission independent of the build's creator: "The Submit
    control's enabled state does not depend on the build's creator; it depends on the signed-in
    owner and on readiness" (`stories.md:200-201`). Its only scenario fixtures have
    `created_by 42` equal to the owner's `user_id` (`:138`, `:216`, `:313`), so the
    creator-differs case is never exercised.
  - BSB-36-PENDING-2 resolves FR-108 to the project's stored integration credential: "the token
    stored at `integrations.secret_ref` is the project owner's credential, and the builder holds
    no separate per-user credential. The PR is therefore opened with the submitting owner's
    identity, and submission is restricted to the owner" (`stories.md:32-38`); "The PR is
    attributed by the provider to the user behind that token — the project owner who configured
    the integration — which is how FR-108's 'author's own source-control identity' is satisfied
    without a per-user credential store" (`:284-288`).
  - ADR SK-001 §8 requires the stronger guarantee: "The PR is opened with the user's own GitHub
    identity, so the author is the person, not the app" (`SK-001:334-336`). §4 says the
    credential is a token "scoped to the sandbox repo, plus push access to `build/*` branches of
    `bheembhai-skills` and PR creation" (`SK-001:197`) — a scope, not an identity.
  - BSB-23 never guarantees the token is the configuring owner's personal credential.
    BSB-23-PENDING-2 accepts an arbitrary token value and stores it (`BSB-23/_epic/stories.md:
    118-120`); its Notes say only that "the token lives only in the external secret store"
    (`:171-177`). BSB-23-PENDING-4's `github` verification calls `GET "https://api.github.com/user"`
    and asserts only a 2xx pass (`BSB-23/_epic/stories.md:282-285`); it never compares the
    returned `login` to the project owner, so a bot/app/shared token passes verification.
- **What is missing/ambiguous/contradictory:** Two different people are called "the author": the
  build's `created_by` (the user story says "I want submitting a Ready build to open one catalog
  pull request in my own source-control identity", `stories.md:211`) and the project owner who
  happens to submit. PENDING-1 deliberately permits a non-creator owner to submit, while PENDING-2
  asserts the PR will carry "the author's" identity from an unverified token. If a member creates
  build 7 and the owner submits it, the PR is opened in the owner's identity; if the owner
  configured a bot token, the PR is opened by the app. Either outcome can contradict FR-108 and
  ADR §8, and no story says which one is intended.
- **Question (if a person must decide):** Is "the author" whose identity FR-108 requires the
  build's `created_by` or the project owner who submits? If the two differ, may the owner submit
  the build, and whose identity must the PR carry? Must the `github` integration credential be the
  configuring owner's personal source-control identity (with BSB-23 rejecting or flagging a
  bot/app token), or is "whatever identity the token carries" acceptable — in which case ADR §8's
  "the author is the person, not the app" needs correcting? (also Open question 2)
- **Proposed change:**
  - **BSB-36-PENDING-1:** state the author/creator rule explicitly. Either add a scenario where
    `builds.created_by` is a member and the project owner submits (and say the PR uses the owner's
    identity), or restrict submission to a caller who is both the owner and the build's creator
    and add the refusal.
  - **BSB-36-PENDING-2:** turn "the token … is the project owner's credential" into a stated
    precondition owned by BSB-23 (for example, "the integration credential is the configuring
    owner's personal source-control identity, enforced by BSB-23-PENDING-4"), or narrow FR-108's
    claim. Add the `created_by`-differs scenario and name the BSB-23 guarantee in
    Notes/dependencies.
  - **BSB-36-PENDING-3 and -4:** no behavioural change beyond the author rule; their Notes should
    use the same wording for who the submission speaks for.
  - **Cross-epic (revise pass, not applied here):** BSB-23-PENDING-2/-4 must state whose
    credential the `github` integration holds and verify the token's identity (compare `GET
    /user`'s `login` with the configuring owner) or explicitly allow shared/bot credentials and
    correct ADR §8.

### Finding 3 — Cross-story UI contract: three stories define the Submit/Update control's rendered state, PENDING-1 says "disabled rather than hidden" while PENDING-3 hides it for terminal builds, and PENDING-3 disclaims the enabled state its own ACs define

- **Severity:** Blocking
- **Stories touched:** BSB-36-PENDING-1, BSB-36-PENDING-3, BSB-36-PENDING-4.
- **Evidence:**
  - BSB-36-PENDING-1's Notes: "The control is rendered disabled rather than hidden so the author
    can see why submission is not available" (`stories.md:190-191`); its enabled-state rule is
    "it depends on the signed-in owner and on readiness" (`:200-201`).
  - BSB-36-PENDING-3's first scenario renders the Submit control **disabled** after submission
    with "This build has already been submitted." (`stories.md:315`), but its merged and
    abandoned scenarios assert "no 'Submit to catalog' control" (`:320`, `:325`) — hidden, not
    disabled, contradicting PENDING-1's stated epic-wide rendering principle.
  - PENDING-3's Out of scope nevertheless claims the control's state is not its concern:
    "readiness and the Submit control's enabled state (BSB-36-PENDING-1 and BSB-30)"
    (`stories.md:348-349`).
  - PENDING-4 adds a third control: after a save it asserts the **Submit** control disabled with
    the readiness message (`stories.md:405`), and once the new head is Ready it asserts an
    enabled **"Update catalog pull request"** control (`:410`) without saying whether the Submit
    control is also rendered, hidden or replaced.
  - No story defines the control for an owned project with no `github` integration: BSB-36-
    PENDING-1's enabled rule considers only ownership and readiness, so the page can offer an
    enabled control whose POST is guaranteed to fail with HTTP 422 "The project has no
    source-control integration." (`stories.md:235-238`), while PENDING-2's Out of scope says the
    control's enabled state is PENDING-1's (`:258-259`).
- **What is missing/ambiguous/contradictory:** There is no single control-state rule. For a
  submitted build whose new head is Ready, PENDING-1's rule would enable Submit and PENDING-3's
  rule disables it (already submitted), while PENDING-4 offers Update; for merged/abandoned,
  PENDING-1 says disabled and PENDING-3 says hidden; for an owned project without an integration,
  no story says. Two implementers building the three stories separately can produce three
  different pages from the same build row.
- **Question (if a person must decide):** Which control, in which state, does the build page show
  for each combination — not submitted (Ready / not Ready), submitted at `pr_head_sha` (Ready),
  submitted with a new head (not Ready / Ready), merged, abandoned — and who owns that rule?
  Should terminal builds hide the control (PENDING-3) or show it disabled with a reason
  (PENDING-1's principle)? Should an owned project with no source-control integration disable
  Submit, or is the HTTP 422 on submit the only guard? (also Open question 3)
- **Proposed change:** Make one control-state rule the epic's contract — recommended: put the
  full table in BSB-36-PENDING-1's Notes (it owns the control) and have PENDING-3 and PENDING-4
  reference it — and delete the claim in PENDING-3's Out of scope that PENDING-1 owns a narrower
  rule. Add acceptance criteria for (a) a submitted build with a Ready new head (Update enabled,
  Submit not enabled), (b) merged/abandoned (the chosen hide-or-disable behaviour, consistently),
  and (c) an owned project with no `github` integration (disabled with a message, or explicitly
  "POST is the only guard"). Apply the same wording in PENDING-3 and PENDING-4's Notes.

### Finding 4 — Cross-story ownership: PENDING-2's acceptance criteria record the pull-request fields its own Out of scope assigns to PENDING-3, and PENDING-3 re-runs the same submission

- **Severity:** Advisory
- **Stories touched:** BSB-36-PENDING-2, BSB-36-PENDING-3 (PENDING-4 consumes `pr_head_sha`).
- **Evidence:**
  - PENDING-2's first scenario asserts the `builds` row records `pr_url`, `pr_state "open"`,
    `pr_integration_id 3`, `pr_head_sha` and `state "submitted"` (`stories.md:218`), and its
    no-write scenario repeats the same fields (`:248`).
  - PENDING-2's Out of scope says the opposite: "recording the pull-request URL and state and the
    merged and abandoned transitions (BSB-36-PENDING-3)" (`stories.md:259-260`).
  - PENDING-3's first scenario re-runs the same submission POST and asserts the same recorded
    fields (`stories.md:315`); its Notes claim the write: "The submission sets `pr_state 'open'`,
    `state 'submitted'` and `pr_head_sha` equal to `head_sha` in the same database transaction
    that records `pr_url` and `pr_integration_id`" (`:370-372`). FR-112/FR-113/FR-161 are mapped
    to PENDING-3 (`:116-120`).
- **What is missing/ambiguous/contradictory:** Two stories both own the atomic first-submission
  write and PENDING-2's Out of scope denies the very behaviour its AC asserts. The values agree,
  so the epic can be built as written, but a revise pass that touches one story can silently
  leave the other claiming the same FR and transaction.
- **Proposed change:** Pick one owner — recommended: PENDING-2 owns the submission POST and its
  atomic write (it calls the provider and must not record a half-state), and PENDING-3 owns the
  refresh and the later lifecycle transitions, observing rather than re-owning the first-
  submission fields. Remove the contradictory Out-of-scope sentence from the story that does not
  own it, and add a one-line ownership sentence to both Notes. Keep FR-112/FR-113/FR-161 mapped
  to PENDING-3; the AC overlap is a test dependency, not a second requirement claim.

### Finding 5 — Cross-story requirement coverage: FR-115's "never writes directly" is proved only on the POST path, while PENDING-4 adds a PATCH path with no equivalent guard and PENDING-2's wording reads as a ban on that PATCH

- **Severity:** Advisory
- **Stories touched:** BSB-36-PENDING-2, BSB-36-PENDING-4.
- **Evidence:**
  - PENDING-2's no-write scenario asserts the source-control request log "contains exactly one
    request, the POST … that log contains no PUT, PATCH or DELETE request and no request whose
    path contains `/contents`, `/git/refs`, `/merges` or `/pulls/42/merge`", and the platform
    stub's counter is 0 (`stories.md:248`). FR-115 is mapped only to PENDING-2 (`:119`).
  - PENDING-2's own scope decision says there are two source-control writes: "`POST
    /repos/<catalog>/pulls` for a first submission and `PATCH /repos/<catalog>/pulls/<number>`
    when refreshing an open PR" (`stories.md:90-94`).
  - PENDING-4's second scenario requires exactly one `PATCH` to `.../pulls/42` and its Notes say
    the patch replaces the description (`stories.md:410,441-445`). PENDING-4 has no request-log
    assertion that the PATCH touches only the description and no contents, git refs or merge
    endpoints, and no platform-stub counter assertion at all.
- **What is missing/ambiguous/contradictory:** FR-115 is an epic-wide "never" guarantee, but it is
  exercised on one of the two write paths. Read across stories, PENDING-2's "no PATCH" assertion
  appears to forbid the operation PENDING-4 requires; read within PENDING-2 it is correctly
  scoped to the first submission. The second write path — the one that can most plausibly be
  implemented with a careless contents write — carries no equivalent proof.
- **Proposed change:** Keep PENDING-2's assertion scoped to its first-submission scenario and say
  in its Notes that the later refresh PATCH is a separate, allowed description-only write. Add to
  PENDING-4 an acceptance criterion mirroring PENDING-2's: the request log contains exactly one
  PATCH to the recorded pull-request path and no PUT/DELETE, no `/contents`, `/git/refs`,
  `/merges` or `/pulls/42/merge` request, the catalog `main` and tree are unchanged, and the
  platform stub receives no request. Add one sentence to both Notes that the guarantee covers
  both write paths.

### Finding 6 — Epic boundary: a save or edit on a merged or abandoned build is declared out of scope, but no story owns refusing it, so the "terminal" claim is incomplete

- **Severity:** Advisory
- **Stories touched:** BSB-36-PENDING-3, BSB-36-PENDING-4. Cross-epic: BSB-21 (the save-to-commit
  path).
- **Evidence:** PENDING-3's Notes say "A `merged` or `abandoned` build is terminal, and both the
  route and the page refuse further submission or state changes" (`stories.md:384-386`).
  PENDING-4's Out of scope says "editing a build whose state is merged or abandoned (both
  terminal)" is out of scope (`:427-429`), while its Notes hand the save path to BSB-21 ("The
  save-to-commit path is BSB-21's … those behaviours already exist in BSB-21's FR-022",
  `:431-435`). BSB-21's epic owns FR-022 and the save flow (`epics.md:329-385`) but has no stories
  yet (`docs/product/epics/BSB-21/` does not exist), so no written acceptance criterion says its
  save route refuses a terminal build. A save is a head move, not a "state change" in
  PENDING-3's wording, so terminality does not obviously cover it.
- **What is missing/ambiguous/contradictory:** A merged or abandoned build could accept a new
  save, move `head_sha`, clear `ready_sha` and leave the terminal state pointing at a pull request
  that never sees the new commit. The refusal is disclaimed by BSB-36-PENDING-4 and unowned by any
  written BSB-21 story.
- **Question (if a person must decide):** Should a merged or abandoned build be editable/saveable
  at all? If not, which story owns the refusal — a BSB-36 story or BSB-21's save route — and what
  is the message? If it may be edited, what does a new head on a terminal build mean for its
  recorded pull request and "terminal" label? (also Open question 4)
- **Proposed change:** PENDING-3 and PENDING-4's Notes state that BSB-21's save path must refuse a
  save on a `merged` or `abandoned` build (naming the message and status), and the cross-epic
  follow-up adds that AC to BSB-21 when its stories are written. If saves are allowed, remove
  "terminal" from PENDING-3 and define the new-head consequence.

### Finding 7 — Epic-boundary ownership loop: BSB-20 assigns branch deletion/finalisation after merge or abandonment to BSB-36, while BSB-36 leaves the branch in place and assigns the reset to BSB-20-PENDING-2

- **Severity:** Advisory
- **Stories touched:** the BSB-36 boundary (BSB-36-PENDING-3, BSB-36-PENDING-4); cross-epic
  BSB-20-PENDING-2.
- **Evidence:** BSB-36's stories say "The build branch is neither deleted nor finalised here; it
  stays at its head. BSB-20-PENDING-2 resets `build/skill-name` when a later build finds the
  previous build merged or abandoned" (`stories.md:87-89`), repeated in PENDING-3's Notes
  (`:386-388`). BSB-20-PENDING-2 says the opposite owner: its Out of scope lists "deleting or
  finalising `build/<skill-name>` after a build is merged or abandoned (BSB-36) — the reset of
  that fixed branch when a new build starts is in scope" (`BSB-20/_epic/stories.md:167-168`), and
  its Notes repeat "deleting or finalising the branch on merge or abandonment belongs to BSB-36"
  (`:202-204`). Each epic points the capability at the other; neither deletes or finalises it, and
  no PRD or epic requirement asks for deletion.
- **What is missing/ambiguous/contradictory:** The reset behaviour is reciprocal and consistent,
  but the delete/finalise capability is a scope hole with two disclaimers. A reader of either epic
  cannot tell whether it is required and unbuilt or intentionally dropped.
- **Question (if a person must decide):** Is deleting or finalising the branch after merge or
  abandonment required for this release? If not, can BSB-20's Out of scope stop assigning it to
  BSB-36 and can BSB-36 state explicitly that leaving the branch at its head is intentional?
  (also Open question 5)
- **Proposed change:** BSB-36-PENDING-3 and -4 Notes state plainly that the branch is
  intentionally left at its head after merge or abandonment, that no deletion or finalisation is
  in this epic's scope, and that the next-build reset is BSB-20-PENDING-2's. Cross-epic follow-up:
  BSB-20-PENDING-2's Out of scope should name the real owner or drop the BSB-36 assignment. This
  is a documentation/ownership fix; it does not compute build order.

### Finding 8 — Epic-wide silent NFR: credential redaction is stated in PENDING-2 only, while PENDING-3 and PENDING-4 resolve and send the same token

- **Severity:** Advisory
- **Stories touched:** BSB-36-PENDING-2, BSB-36-PENDING-3, BSB-36-PENDING-4.
- **Evidence:** PENDING-2's Notes establish the rule for its own route: "The token is never
  rendered in a response, a log line or the description" (`stories.md:284-286`). PENDING-3
  resolves `pr_integration_id`'s credential for the refresh (`:379-384`) and its ACs assert the
  `Authorization: Bearer ghp-test-token-7a1d` header (`:320`) and "the body contains no exception
  text or stack trace" on outage (`:330`), but never that the response, page or log contains no
  credential. PENDING-4 resolves the same credential for its `PATCH` (`:408,441-445`) and its
  failure scenario asserts the error body but not the absence of the token (`:413-415`).
  `PRD.md:254` (NFR-004) and `:256` (NFR-006) ground the rule; BSB-23-PENDING-5 owns a
  "record-wide, log and run-result redaction guarantee" (`BSB-23/_epic/stories.md:158-163`), but
  BSB-36 never names it.
- **What is missing/ambiguous/contradictory:** The epic's most credential-sensitive route is
  PENDING-2, but two more stories repeat the same secret resolution without the redaction
  assertion. A per-story implementer of PENDING-3 or -4 has no instruction not to echo the token
  in an error page, a log line or a response body, and the shared BSB-23 helper is unnamed.
- **Proposed change:** Add the same sentence and, where an AC exists, the same assertion to
  PENDING-3 and PENDING-4: "No response body, page, log line or record contains the integration
  credential." If BSB-23-PENDING-5 supplies the shared redaction path, name it in both stories'
  Notes/dependencies. Same change for both.

### Finding 9 — Dependency-note sanity: PENDING-2 names PENDING-1 as the owner of the readiness refusal its route applies but omits it from Notes/dependencies; PENDING-4 omits the `runs` producers its AC cites

- **Severity:** Advisory
- **Stories touched:** BSB-36-PENDING-2, BSB-36-PENDING-4.
- **Evidence:** PENDING-2's Out of scope says "The Submit control's enabled state and the
  readiness refusal (BSB-36-PENDING-1, which this story's route also applies)"
  (`stories.md:258-259`), but its Notes/dependencies list BSB-18, BSB-21, BSB-22-PENDING-1 and -3,
  BSB-23-PENDING-2, BSB-24, BSB-25, BSB-29, BSB-30, BSB-31, BSB-32 and BSB-33 — not
  BSB-36-PENDING-1 (`:270-277`). PENDING-4's second scenario cites a `"runs"` row 24 with
  `skills_commit_sha` and `final_verdict` and `"scans"` rows 13 and 14 (`:408`); its Notes list
  BSB-21, BSB-22-PENDING-1, BSB-23-PENDING-2, BSB-30, BSB-31, BSB-32, BSB-33 and
  BSB-36-PENDING-2/-3, but not BSB-24/BSB-25/BSB-29 — the epics PENDING-2 names for the same
  `runs` fields (`:431-439`).
- **What is missing/ambiguous/contradictory:** PENDING-2's route depends on PENDING-1 for its
  readiness and ownership refusals, yet a reader of PENDING-2's Notes can assume PENDING-1 need
  not exist first. PENDING-4's fixture fields have no named producer, unlike PENDING-2's.
- **Proposed change:** Add "Depends on BSB-36-PENDING-1 for the readiness and ownership refusals
  this route applies" to PENDING-2's Notes/dependencies. Add BSB-24, BSB-25 and BSB-29 (or "the
  same `runs`/`scans` records and fields BSB-36-PENDING-2 depends on") to PENDING-4's
  Notes/dependencies. This is a documentation fix only; build order remains
  `sdlc-plan-epic-sequence`'s concern.

## Open questions

1. **Reviewer access (Finding 1).** Do catalog reviewers read the linked run and scan reports
   outside the authoring/project-membership gates? If yes, which epic/story owns the view, which
   route renders it, and what authorizes a reviewer? If no, must PRD §2's "does not use the
   authoring interface" and FR-110/FR-111 be narrowed?
2. **Author identity (Finding 2).** Is "the author" whose identity FR-108 requires the build's
   `created_by` or the project owner who submits? May an owner submit a build a member created,
   and whose identity must the PR carry? Must the `github` integration credential be the
   configuring owner's personal source-control identity, with BSB-23 verifying or rejecting a
   bot/app token — or is the identity behind any configured token acceptable?
3. **Build-page control states (Finding 3).** What control and state does the page show for each
   combination of build state, head vs `pr_head_sha`, readiness and project integration, and who
   owns that rule? Terminal builds: hidden or disabled? Owned project without an integration:
   disable Submit or rely on the HTTP 422?
4. **Terminal build saves (Finding 6).** May a merged or abandoned build be edited/saved? If not,
   which story owns the refusal? If yes, what does a new head mean for the recorded pull request?
5. **Branch deletion/finalisation (Finding 7).** Is deleting or finalising the build branch after
   merge/abandonment required in this release, or is "left at its head, reset by the next build"
   the intended end state?

## Proposed changes

`docs/product/epics/BSB-36/_epic/stories.md` (proposed, not applied):

- **BSB-36-PENDING-1** — Own the complete Submit/Update control-state rule (including submitted,
  terminal and no-integration cases), or reference the epic-level table; reconcile
  "disabled rather than hidden" with PENDING-3's hidden terminal control. State the
  author/`created_by` rule and add the creator-differs scenario or the creator-only refusal
  (Findings 2, 3).
- **BSB-36-PENDING-2** — Point FR-110/FR-111 links at the answer to Open question 1 or narrow the
  story value; state the credential-identity precondition and add the creator-differs scenario
  (Findings 1, 2). Resolve the recording ownership with PENDING-3: either own the atomic
  first-submission write and drop the contrary Out-of-scope line, or stop asserting the build
  fields (Finding 4). Scope the no-write assertion to the first-submission POST and note the
  allowed later PATCH (Finding 5). Add BSB-36-PENDING-1 to Notes/dependencies (Finding 9).
- **BSB-36-PENDING-3** — Stop claiming the Submit control's enabled state is entirely PENDING-1's;
  reference the control-state rule. Add the credential-redaction sentence/AC (Finding 8). State
  the terminal-build save rule and the intentional no-deletion branch policy (Findings 6, 7).
- **BSB-36-PENDING-4** — Add the description-only PATCH request-log/AC mirroring PENDING-2's
  no-write proof (Finding 5). Add the credential-redaction sentence/AC (Finding 8). State the
  terminal-build save rule and the intentional no-deletion branch policy (Findings 6, 7). Add
  BSB-24/25/29 (or the records they produce) to Notes/dependencies (Finding 9).
- **Coverage table** — The FR-107 to FR-115/FR-161 mapping stays one requirement per story; the
  PENDING-2/PENDING-3 recording overlap is a test dependency, not a second claim (Finding 4).

Cross-epic (revise pass / the owning epics, not applied here):

- **BSB-22-PENDING-3, BSB-31-PENDING-5, BSB-32-PENDING-2, BSB-33-PENDING-1** — Resolve the
  reviewer-readable view and its access rule with BSB-36's Open question 1; scope the shared
  membership check to author-facing surfaces if the answer requires it (Finding 1).
- **BSB-23-PENDING-2 and -4** — State whose credential the `github` integration holds and verify
  the token's identity against the configuring owner, or explicitly allow shared/bot credentials
  and correct ADR §8 (Finding 2).
- **BSB-21 (when its stories are written)** — Add the refusal of saves on a `merged` or
  `abandoned` build (Finding 6).
- **BSB-20-PENDING-2** — Stop assigning branch deletion/finalisation to BSB-36, or name the real
  owner (Finding 7).

No change is proposed to `epic-map.json`, the requirement IDs, `story-map.json`,
`sdlc-tracker-sync` or Jira. This report changes no story, map or tracker record.

## Architecture impact

None. Finding 1 is an access-rule/product-ownership decision, as BSB-33's review already
concluded, not a new entity, service or integration; Finding 2 is a contract clarification between
BSB-23 and BSB-36 (whose credential the integration stores), not a new design; Findings 3-9 are
story-boundary, UI-state, coverage and dependency-note issues. The epic's new `builds` columns
(`pr_state`, `pr_integration_id`, `pr_head_sha`) and the two installation settings
(`CATALOG_REPOSITORY`, `BUILDER_PUBLIC_URL`) are the normal planning-to-design hand-off the later
design stage records, like BSB-19's `builds.base_sha`; ADR SK-001 §9 already names `pr_url` and the
`open/submitted/merged/abandoned` build state, and nothing in SK-001's entities, endpoints or
integrations conflicts with the epic. No `sdlc-arch-design` (amend) run is required before
`sdlc-plan-stories-write` (revise) applies this report.

## Requirement coverage check

All ten requirements mapped to BSB-36 by `epic-map.json` — FR-107 to FR-115 and FR-161 — are
exercised by at least one acceptance criterion, each is claimed by exactly one story, and no story
claims a requirement outside the epic. `epic-map.json`, `epics.md` and `PRD.md` agree on the
current wording of every mapped requirement; no drift was found. Two coverage caveats are the
findings above: FR-108's identity guarantee is unproven (Finding 2) and FR-115's "never" is
exercised on only one of the two source-control write paths (Finding 5); neither removes a
requirement from the epic.

| Requirement | Exercising story | Acceptance criteria | Caveat |
|---|---|---|---|
| FR-107 — Submit enabled only when Ready at the head SHA | BSB-36-PENDING-1 | "A Ready build offers Submit to catalog"; "A build that is not Ready disables Submit and says why"; "A Ready recorded for an older head is not trusted after the head moves"; "Submission re-evaluates readiness at the current head and refuses a stale Ready" | Control-state rule open (Finding 3) |
| FR-108 — PR opens using the author's own source-control identity | BSB-36-PENDING-2 | "A Ready build opens one catalog pull request with the owner's credential" | Identity/author contract open (Finding 2) |
| FR-109 — Description lists the readiness checks at the head SHA | BSB-36-PENDING-2 | "The description lists the four readiness checks at the head SHA and links the run and scan reports"; "An unavailable LLM scan is listed as unavailable and still linked" | — |
| FR-110 — Description links the run report | BSB-36-PENDING-2 | "The description lists the four readiness checks at the head SHA and links the run and scan reports" | Link target 403s for a reviewer (Finding 1) |
| FR-111 — Description links the scan reports | BSB-36-PENDING-2 | Same scenario; "An unavailable LLM scan is listed as unavailable and still linked" | Link target 403s for a reviewer (Finding 1) |
| FR-112 — PR URL recorded on the build | BSB-36-PENDING-3 | "A successful submission records the pull-request URL and state and shows them" | Recording ownership duplicated with PENDING-2 (Finding 4) |
| FR-113 — Build state moves through open, submitted, merged or abandoned | BSB-36-PENDING-3 | "A successful submission records the pull-request URL and state and shows them"; "A merged pull request moves the build to merged"; "A closed pull request moves the build to abandoned"; "A merged or abandoned build cannot be submitted again" | Terminal save unowned (Finding 6) |
| FR-114 — A save on a submitted build clears readiness | BSB-36-PENDING-4 | "A save on a submitted build creates a commit, clears readiness and leaves the submission intact" | — |
| FR-115 — The builder never writes directly to the catalog, platform projects or project skills | BSB-36-PENDING-2 | "Submission never writes directly to the catalog, platform projects or project skills" | PATCH path unproven (Finding 5) |
| FR-161 — PR state recorded on the build | BSB-36-PENDING-3 | "A successful submission records the pull-request URL and state and shows them"; "A provider outage on refresh keeps the recorded pull-request state" | Recording ownership duplicated with PENDING-2 (Finding 4) |

No NFR is assigned to BSB-36 in `epic-map.json`. The PRD's cross-cutting NFR-004 (credentials
never in logs or results) and NFR-006 (test-purpose credentials) are handled at the integration
epic; Finding 8 asks BSB-36's two other token-bearing stories to restate the redaction rule.

## Dependency-note sanity check

Every "Depends on X" / "produced by Y" note in the four stories refers to a real epic or story
key: BSB-18, BSB-20-PENDING-2, BSB-21, BSB-22-PENDING-1 and -3, BSB-23-PENDING-2, BSB-24,
BSB-25, BSB-29, BSB-30, BSB-31, BSB-32, BSB-33 and BSB-36-PENDING-1/-2/-3 all exist in
`epic-map.json` and, where stories are written, in their epic's `stories.md`. No note cites a
non-existent story key.

Mismatches found: (a) PENDING-2's Out of scope names BSB-36-PENDING-1 as the owner of the
readiness refusal its route applies, but its Notes omit PENDING-1 (Finding 9); (b) PENDING-4's
ACs cite `runs` fields whose producers (BSB-24/BSB-25/BSB-29) PENDING-2 names but PENDING-4 does
not (Finding 9); (c) the BSB-20-PENDING-2 ↔ BSB-36 branch-deletion note is reciprocal but assigns
the same capability to neither epic (Finding 7). BSB-31-PENDING-5 and BSB-33-PENDING-1 name
BSB-36 for the reviewer-facing view and BSB-36 names them for the link targets — reciprocal, and
the subject of Finding 1. Build order itself is left to `sdlc-plan-epic-sequence`; this pass only
records the documentation mismatches.
