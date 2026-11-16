# Revisions — BSB-24

## Pass 1 — 2026-11-15 — `epic-review.md` (cross-story gap review)

**Report applied:** `docs/product/epics/BSB-24/_epic/epic-review.md` — verdict CHANGES REQUESTED,
findings 1–8 and open questions 1–4. Target resolution: the run named "SkillBuilder", which is the
product title in `docs/product/PRD.md`, not a Jira issue. The Atlassian project
`bheembhai-skill-builder` contains only the 21 epics BSB-18 to BSB-38; a JQL search for an issue
whose summary contains "SkillBuilder" returned no issues. The Atlassian MCP server was not
connected in this session (`.mcp.json` fails validation: `args` must be an array), so the epic was
resolved to **BSB-24** — the epic the preceding `sdlc-plan-stories-write` run wrote (commit
`d5b31a5`) and whose review requested changes (commit `5aaea4f`) — and its details were fetched
read-only through the Atlassian REST API (summary *Run start & input selection*, type Epic, labels
`FA-6`, `MVP`; description and traceability match the BSB-24 section of `docs/product/epics.md`).
Nothing was written to Jira.

**Applied (findings with no open question, and the answer-independent parts of findings 1 and 4):**

- **Finding 2 (blocking) — one fixed validation order.**
  - `stories.md` contract preamble: the validation order now names four stages with every 422 code
    in its stage. Field stage, in order: `skill_required`, `skills_ref_required`,
    `input_branch_required`, `model_profile_required`, `model_profile_invalid`, `tier_required`,
    `context_invalid`, `step_required` / `workflow_required`, `reviewer_feedback_invalid`,
    `upstream_handoff_invalid`. Integration-and-branch stage: `source_control_not_configured`,
    `skills_branch_not_found`, `input_branch_not_found`. Workflow stage: `workflow_not_found`,
    `step_not_found`. Model stage: `model_profile_not_found`, `model_tier_not_mapped`.
  - `BSB-24-PENDING-2` Notes: states that `source_control_not_configured` comes before both branch
    lookups.
  - `BSB-24-PENDING-3` Notes: `step_required`, `workflow_required` and `context_invalid` are
    field-stage checks; `workflow_not_found` and `step_not_found` happen after branch validation.
  - `BSB-24-PENDING-4` Notes: `reviewer_feedback_invalid` and `upstream_handoff_invalid` are
    field-stage checks.
  - `BSB-24-PENDING-5` Notes: `model_profile_required`, `model_profile_invalid` and `tier_required`
    are field-stage checks; `model_profile_not_found` and `model_tier_not_mapped` happen after
    branch and workflow validation.
  - `BSB-24-PENDING-5`: added scenario *A missing tier is refused before the skills branch is looked
    up* — a request with no `tier` and `skills_ref` = `test/ada/missing` returns 422
    `tier_required`, proving the field stage precedes the branch stage.

- **Finding 6 (advisory) — unknown context keys and top-level fields.**
  - `stories.md` contract preamble: added the error row for a `context` key other than `workflow`,
    `step`, `reviewer_feedback` or `upstream_handoff` → 422 `context_invalid` with message
    `The context contains an unknown key 'foo'.`
  - `stories.md` contract preamble: stated that an unknown top-level field is ignored — neither
    stored nor refused — and that only the declared request fields reach validation and the `runs`
    row. The field stage notes the same rule.
  - `BSB-24-PENDING-3`: added scenario *A context containing an unknown key is refused*.
  - `BSB-24-PENDING-4` Notes: "the run's stored context is exactly what the author supplied"
    reworded to "the stored context is exactly the allowed keys the author supplied".

- **Finding 7 (advisory) — BSB-27 extensions to this route.**
  - `stories.md` contract preamble: "exactly" now means exactly as of this epic, and epic BSB-27
    later adds turn and spend cap request fields and `runs` columns (FR-050, FR-052; SK-001 §9 has
    no cap columns yet) and the FR-054/FR-055 start refusals.
  - `BSB-24-PENDING-1` Notes: the same BSB-27 extension statement.
  - `BSB-24-PENDING-5` Notes: caps and model selection are separate run-start inputs, so the
    options API may later carry cap defaults.

- **Finding 8 (advisory) — stable model-profile identity.**
  - `BSB-24-PENDING-1` and `BSB-24-PENDING-5` Notes: BSB-23 must give each `ai_model` profile a
    stable positive integer `id` that is never reused within a project; if BSB-23 keys profiles
    differently, `model_profile_id` and its error codes are re-pointed, not only the fixture.

- **Finding 1 (blocking), answer-independent part.**
  - `BSB-24-PENDING-5` Notes: making `model_profile_id` and `tier` required changes the shared
    run-start body BSB-22-PENDING-4 uses; it points at the preamble's cross-epic note.

- **Finding 4 (blocking), answer-independent parts — the page and options surfaces.**
  - `BSB-24-PENDING-2`: added scenario *Submitting the run-start form creates the run through the
    start API*, which pins the form's resulting `POST /api/projects/7/runs` JSON body and the
    resulting `runs` row.
  - `BSB-24-PENDING-3`: added scenario *Run-start page shows the workflow and step choices on the
    chosen branch* with exact workflow and step text.
  - `BSB-24-PENDING-4`: added scenario *Run-start page offers the optional feedback and handoff
    fields*, including that `upstream_handoff` is a text area parsed as a JSON object.
  - `BSB-24-PENDING-5`: added scenario *Run-start page shows the model profiles and their tiers*,
    and moved `SKILL.md` tier preselection from Notes to Out of scope (the page offers the tier
    keys and the author chooses explicitly).
  - `BSB-24-PENDING-2`, `-3`, `-4` and `-5` Out of scope: each names epic BSB-38 for accessibility
    of those controls (FR-130 to FR-137, NFR-012).

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 1 / Open question 1 (blocking).** Whether BSB-22-PENDING-4 becomes a reusable
  membership guard with BSB-24-PENDING-1 owning every run-start route scenario (option (a)), or
  both stories keep run-start scenarios with BSB-22's bodies re-pointed to BSB-24's contract
  (option (c)). The guard-or-duplicate line in `BSB-24-PENDING-1` Notes, the rewrite of the
  preamble's BSB-22 cross-epic note, and BSB-22-PENDING-4's own revise pass all depend on it, so
  nothing was changed. The preamble's existing cross-epic note still says BSB-22's fixture "must"
  be re-pointed, and that remains true under option (c) only.
- **Finding 3 / Open question 2 (blocking).** Whether run start lists the skill folders present on
  the chosen skills branch and refuses an absent `skill` with 422 `skill_not_found` before any
  `runs` row (option (a)), or BSB-25 owns the refusal (option (b)). No `skills` entry, no
  `skill_not_found` error row or scenario, and no change to PENDING-1's "only checked for presence"
  Notes or PENDING-2's skill-folder Out-of-scope line was made.
- **Finding 4 / Open question 3 (blocking).** Whether the options API and page refuse with a 422
  when the project has no `github` or no `ai_model` integration, or return 200 with empty lists and
  an explanatory message. The page/form scenarios were added, but the project `8` options/page
  scenario and the no-`ai_model` options/page behaviour were not, because either answer needs a
  new error code or a new empty-state contract.
- **Finding 5 / Open question 4 (blocking).** Whether run start resolves the default workflow and
  step when `context` is omitted and stores the resolved values in `runs.context` (and what happens
  when no workflow, or more than one, uses the skill), or BSB-26 takes on default resolution
  through a new requirement. PENDING-3's omitted-context scenario, its Out-of-scope entry and the
  preamble's `context` row are unchanged; PENDING-4's `BB_CONTEXT` note is unchanged.

**Coverage:** unchanged. All 7 requirements mapped to BSB-24 (FR-037 and FR-145 to FR-150) are
still covered by the same five stories, and no story claims a requirement outside the epic.
`story-map.json` is unchanged: no story key, summary or requirement mapping changed.

**Note for the next review (not a finding of this pass):** the reviewer-requested page scenarios
raise BSB-24-PENDING-2, -3 and -5 to nine acceptance scenarios each, above the skill's ~7-scenario
size signal. Splitting along the API/page seam (for example a page-story per surface) is worth
considering once the open questions are answered, but it was not done here because the report
names no such split and revise mode does not add changes of its own.

## Pass 2 — 2026-11-16 — `epic-review.md` (re-dispatched; three of the four open questions now answered by sibling artifacts)

**Report applied:** `docs/product/epics/BSB-24/_epic/epic-review.md` — the same CHANGES REQUESTED
report as Pass 1 (findings 1–8 and open questions 1–4), re-routed here by the
`sdlc-plan-epic-review` step. The run hand-off again carried no gate answers. Unlike Pass 1, three
of the four open questions can now be answered without guessing: BSB-22's revise pass applied the
membership-guard split (Finding 1 / Open question 1), BSB-26's revise pass decided default context
resolution at claim (Finding 5 / Open question 4), and Finding 3 / Open question 2 has an explicit
reviewer recommendation that enforces the epic DoD and needs no new product decision. Those are
applied below. Finding 4 / Open question 3 still has neither an answer nor a recommended option,
so it remains open.

**Target resolution:** the run item is `SkillBuilder`, which is the product title in
`docs/product/PRD.md`, not a Jira issue. The run context's item is epic **BSB-24**, fetched
read-only in this pass through `GET /rest/api/3/issue/BSB-24` (the Atlassian MCP tools were not
exposed in this session): summary *Run start & input selection*, type Epic, status *To Do*, labels
`FA-6` and `MVP`. An epic carries no acceptance-criteria field; its description, functional scope
and covered requirements match the BSB-24 section of `docs/product/epics.md` and
`epic-map.json`. Nothing was written to Jira.

**Previously open questions now answered, and what was applied:**

- **Finding 1 / Open question 1 (blocking) — option (a), already applied by BSB-22.** BSB-22's
  `revisions.md` Pass 3 re-scoped BSB-22-PENDING-4 to the reusable `require_project_member` guard:
  the story now asserts only the guard's admit/refuse decision and its `project_members` read, its
  run-start request body is an explicit placeholder, and its Notes say BSB-24's run-start story
  must cite the guard and carry the 201 and `runs`-row assertions. BSB-24 is therefore aligned to
  that answer, not to a guess:
  - `stories.md` contract preamble: the BSB-22 cross-epic note is rewritten from "BSB-22 must
    re-point its fixture" to "BSB-22-PENDING-4 is the guard this route calls". It records that
    BSB-22 asserts only the guard decision, that BSB-24 owns the route contract, that
    BSB-24-PENDING-1 asserts the 403/404 outcomes at the route, and that BSB-22's placeholder body
    is the only thing re-pointed in BSB-22's revise pass. BSB-22-PENDING-5's separate
    `require_project_owner` guard is named and marked unchanged.
  - `BSB-24-PENDING-1` Notes: the "Shares the route with BSB-22-PENDING-4" bullet now says that
    story delivers the guard, that this story owns the route contract, and that "the 403/404
    decision is BSB-22-PENDING-4's guard; this story asserts it at the route".
  - `BSB-24-PENDING-1` Out of scope: names BSB-22-PENDING-4's `require_project_member` guard.
  - `BSB-24-PENDING-5` Notes: "shared run-start body" changed to "placeholder run-start body", to
    match BSB-22's current fixture status.

- **Finding 3 / Open question 2 (blocking) — option (a), the reviewer's recommended option.**
  Applying it enforces the epic DoD ("an invalid selection is refused before any run is created")
  and SK-001 §5 ("A run tests one skill"), and gives the check an owner: BSB-25's requirements
  (FR-038 to FR-043, NFR-001, NFR-009) never take on a missing-skill refusal and BSB-25 has no
  stories, so the deferral would remain unowned. Applied:
  - Preamble fixture: exactly one skill folder, `sdlc-fix-bug-triage`, exists on every catalog
    branch offered; no other skill folder exists there.
  - Preamble request fields: the `skill` rule now says it must name a skill folder on the selected
    skills branch.
  - Preamble options response: `"skills":["sdlc-fix-bug-triage"]` added, with skill-name ordering
    and the rule that `skills` is `[]` when `skills_ref` is absent or names no branch.
  - Preamble validation order: `skill_not_found` is in the integration-and-branch stage, after
    `skills_branch_not_found` (the branch must resolve before its folders can be read) and before
    `input_branch_not_found`.
  - Preamble error table: the `skill_not_found` 422 row with the message the reviewer specified,
    and the interpolation sentence now includes it.
  - `BSB-24-PENDING-2`: summary and statement now include the skill choice; the page scenario
    asserts `name="skill"` and `value="sdlc-fix-bug-triage"`; the options scenario asserts the
    `skills` value; a new scenario, *A skill that does not exist on the chosen skills branch is
    refused*, asserts the 422 `skill_not_found` body and `runs` count `0`; the "Validating that the
    chosen skill folder exists … (epic BSB-25)" Out-of-scope line is dropped; Notes record the
    `skill_not_found` position and that the options `skills` list and the start check share one
    branch read.
  - `BSB-24-PENDING-1` Notes: the "only checked for presence" bullet now points at
    BSB-24-PENDING-2's `skill_not_found` check.
  - `story-map.json`: the PENDING-2 summary mirrors the revised story summary. Requirement
    mappings are unchanged.

- **Finding 5 / Open question 4 (blocking) — option (b), decided by BSB-26.** BSB-26's
  `revisions.md` Pass 3 resolved the same question (it calls it BSB-24 Open question 4) by having
  BSB-26-PENDING-1 resolve the default workflow and step at claim from the pinned skills commit,
  and its cross-epic follow-up explicitly asks BSB-24's revise pass to record that decision while
  leaving BSB-24's contract unchanged (`{}` at run start). Applied:
  - Preamble, after the `runs`-row table: at run start `context` records the author's input or
    `{}`; BSB-26-PENDING-1 later resolves the default at claim and writes the resolved values into
    the same column, preserving `reviewer_feedback` and `upstream_handoff`; an unresolvable default
    is BSB-26's `failed_infra`. This epic never stores a resolved context.
  - `BSB-24-PENDING-3` Out of scope names BSB-26-PENDING-1 as the resolver and `BB_CONTEXT`
    renderer. Its Notes name the resolution rule (SK-001 §5.3), the no-workflow / more-than-one
    outcome, and state that at start `runs.context` is the author's input while BSB-33 and BSB-35
    read it after claim, when BSB-26 has resolved it.
  - `BSB-24-PENDING-4` Out of scope names BSB-26-PENDING-1; Notes add that BSB-26's claim-time
    resolution preserves `reviewer_feedback` and `upstream_handoff`, and that before claim this
    story stores exactly the allowed keys the author supplied.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 4 / Open question 3 (blocking).** When a project has no `github` integration or no
  `ai_model` integration, should the options API and run-start page refuse with a 422 (as the start
  route does) or return `200` with empty lists and an explanatory message? The report states no
  recommended option, and the repository has no answer: BSB-24's start-route contract only fixes
  the start route's refusals, and no sibling epic constrains the options/page surface. Either answer
  changes the options response or page contract (including whether a new error code such as
  `model_profiles_not_configured` exists), so nothing was invented. Pass 1's answer-independent page
  and form-submit scenarios remain applied.

**Re-checked, no further edit needed (applied in Pass 1):** Finding 2 (one fixed validation order,
every code in a stage, the PENDING-5 precedence scenario), Finding 6 (unknown context keys and
unknown top-level fields), Finding 7 (BSB-27 extensions to this route) and Finding 8 (stable
model-profile identity), plus the answer-independent parts of Finding 4 already applied. Nothing was
reverted.

**Coverage:** unchanged. All 7 requirements mapped to BSB-24 (FR-037 and FR-145 to FR-150) are
still covered by the same five stories, and no story claims a requirement outside the epic.
`story-map.json` changes only the BSB-24-PENDING-2 summary that mirrors the revised story; no story
key or requirement mapping changed.

**Note for the next review (not a finding of this pass):**
- BSB-24-PENDING-2 now has ten acceptance scenarios, above the skill's ~7-scenario size signal,
  because Finding 3's missing-skill scenario and the skill assertions were added to the branch
  story. A split along the API/page seam is worth considering once Finding 4 is answered.
- Jira's BSB-24 description lists the selected inputs as the skills branch, input branch,
  workflow/step context, optional feedback or handoff, model profile and model tier; it does not
  name `skill` as a selection even though SK-001 §5 says a run tests one skill. Option (a) therefore
  adds the skill choice to the run-start surface as the reviewer recommended. No requirement
  mapping changed.

**Next:** a person must answer Finding 4 / Open question 3 in the run hand-off; then run
`sdlc-plan-stories-write` again to apply it and re-run `sdlc-plan-epic-review`.

## Pass 3 — 2026-11-16 — `epic-review.md` (re-dispatched; no gate answers, so the one remaining open question stays open)

**Report applied:** the same `docs/product/epics/BSB-24/_epic/epic-review.md` — verdict CHANGES
REQUESTED, findings 1–8 and open questions 1–4. The run hand-off again carries no answers:
`settled_decisions` reports `answered: 0`, `eligible: 0`, `shown: 0`, `gate_follows` is false,
`reviewer_feedback` is empty and `upstream_handoff` is null. No open question was answered, so no
conditional proposal was applied and `stories.md` and `story-map.json` are unchanged by this pass.

**Target resolution:** the run item is `SkillBuilder`, the product title in `docs/product/PRD.md`,
not a Jira issue; a read-only JQL search for a summary containing "SkillBuilder" returned no issues
across the accessible projects. The run context's `ITEM` is epic **BSB-24** (*Run start & input
selection*, FA-6, MVP). The Atlassian MCP tools were not exposed in this session, so the epic was
fetched **read-only** through `GET /rest/api/3/issue/BSB-24`: type Epic, status To Do, labels
`FA-6` and `MVP`, summary *Run start & input selection*, no acceptance-criteria field; its
description, functional scope and covered-requirements list match the BSB-24 section of
`docs/product/epics.md`. Nothing was written to Jira.

**Re-checked in the current `stories.md`; nothing new to apply:**

- **Finding 1 (option (a), applied in Pass 2)** still matches `BSB-22-PENDING-4` as revised:
  BSB-22's `revisions.md` Passes 3 and 4 keep that story as the reusable `require_project_member`
  guard, with the run-start route contract owned here. BSB-24-PENDING-1's guard bullet and the
  preamble's cross-epic note agree.
- **Finding 2 (applied in Pass 1)** — the four-stage validation order, every code in its stage and
  the PENDING-5 precedence scenario are present in the preamble and in PENDING-2, -3, -4 and -5's
  Notes.
- **Finding 3 (option (a), applied in Pass 2)** — the `skills` options entry, the `skill_not_found`
  error row, the branch-stage position and PENDING-2's missing-skill scenario are present.
- **Finding 4 (answer-independent parts, applied in Passes 1–2)** — PENDING-2's form-submit and
  branch/skill page scenarios, PENDING-3's workflow/step page scenario, PENDING-4's feedback and
  handoff page scenario, PENDING-5's profile/tier page scenario, the `SKILL.md` preselection moved
  to Out of scope, and the BSB-38 accessibility pointers are present.
- **Finding 5 (option (b), applied in Pass 2)** still matches `BSB-26-PENDING-1`: BSB-26's
  `revisions.md` Pass 3 resolves the default workflow and step at claim and its story records the
  unresolvable-default `failed_infra` path. BSB-24 stores the author's input or `{}`.
- **Findings 6, 7 and 8 (applied in Pass 1)** — the unknown-context-key row and scenario, the
  unknown-top-level-field rule, the BSB-27 extension note and the stable profile-id dependency
  remain present.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 4 / Open question 3 (blocking).** When a project has no `github` integration or no
  `ai_model` integration, should the options API and run-start page refuse with a 422 (as the start
  route does) or return `200` with empty lists and an explanatory message? The report names no
  recommended option, the hand-off supplies no answer, and no repository artifact settles it:
  BSB-23 (which owns the integration schemas) has no stories, and the sibling revisions address
  different questions. Either answer changes the options response or page contract (including
  whether a new error code such as `model_profiles_not_configured` exists), so the project `8`
  options/page scenario and the no-`ai_model` page behaviour remain unapplied.

**Notes for the next review (not findings of this pass):**

- Jira BSB-24's implementation guidance says workflow and step choices are populated "from the
  platform's workflow definitions", while BSB-24-PENDING-3 and SK-001 §5.3 read them from the
  chosen skills branch's `config/`. The PRD treats the published epic set as a downstream
  traceability view generated from an earlier revision, so the ADR and the stories were left as
  they are; the next review should confirm the `config/` source is authoritative.
- Jira BSB-24's non-goals include "automatically choosing defaults that the author cannot see or
  override". BSB-26-PENDING-1's claim-time default resolution (Finding 5, option (b)) is automatic;
  the next review should confirm that the post-claim visibility in the run report satisfies that
  non-goal. Nothing was changed, because the report names no such finding.
- BSB-22's `revisions.md` Pass 4 records that BSB-24's run form needs the caller's projects and
  that the project-list read endpoint is part of BSB-22's unanswered Open question 2. BSB-24's
  stories name no project picker or project-list endpoint; this is not a finding of this report,
  so it is recorded here only.
- Size signal carried from Pass 2: `BSB-24-PENDING-2` has ten acceptance scenarios, above the
  skill's ~7-scenario signal. A split along the API/page seam is worth considering once Finding 4
  is answered.

**Coverage:** unchanged. All 7 requirements mapped to BSB-24 (FR-037 and FR-145 to FR-150) are
still covered by the same five stories, and no story claims a requirement outside the epic.
`story-map.json` is unchanged.

**Next:** a person must answer Finding 4 / Open question 3 in the run hand-off; then run
`sdlc-plan-stories-write` again to apply it and re-run `sdlc-plan-epic-review`.
