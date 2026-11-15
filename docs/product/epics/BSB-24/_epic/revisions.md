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
