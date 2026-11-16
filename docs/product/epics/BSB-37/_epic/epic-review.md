# Epic Review — BSB-37: Command line & saved suites

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-37-PENDING-1, BSB-37-PENDING-2, BSB-37-PENDING-3, BSB-37-PENDING-4, BSB-37-PENDING-5, BSB-37-PENDING-6, BSB-37-PENDING-7

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-37/_epic/epic-review.md`.

## Context loaded

**Epic resolution and Jira.** The run input names `SkillBuilder-2`. That is not a Jira issue: a
read-only `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404 ("Issue does not exist or you do
not have permission to see it."), matching `docs/product/PRD.md` section 8, which identifies
`SkillBuilder-2` as the PRD's work-item umbrella. No Atlassian MCP tool was exposed in this session,
so the configured site was queried read-only through its REST API. The epic under review is BSB-37:
its Jira issue reads summary "Command line & saved suites", type Epic, labels FA-16/mixed, and a
description matching the BSB-37 section of `docs/product/epics.md`; HEAD commit `5939721` is the
`sdlc-plan-stories-write` step that wrote this epic's `stories.md` and `story-map.json`; the
workflow's next step is `sdlc-plan-epic-review` (`config/sdlc-wf-planning-epic.yaml`); and no
`epic-review.md` existed for BSB-37. No Jira write was attempted.

**Story set.** All seven stories were loaded together from
`docs/product/epics/BSB-37/_epic/stories.md` (the file was read in full across contiguous slices),
with the full `docs/product/epics/BSB-37/_epic/story-map.json`:

- BSB-37-PENDING-1 — CLI `run` (FR-116)
- BSB-37-PENDING-2 — CLI static scan (FR-117)
- BSB-37-PENDING-3 — CLI full scan (FR-118)
- BSB-37-PENDING-4 — save a suite (FR-119, FR-120)
- BSB-37-PENDING-5 — run a suite (FR-121)
- BSB-37-PENDING-6 — schedule a suite (FR-122)
- BSB-37-PENDING-7 — record scheduled results (FR-123)

**System context.** Read the PRD's feature-area section and `FR-116`–`FR-123`, plus `NFR-004`,
`NFR-006`, `NFR-012`, `NFR-013` and `NFR-014`; the BSB-37 section and covered requirements in
`docs/product/epics.md`; the BSB-37 entry in `docs/product/epic-map.json`; ADR SK-001 sections 3–7
and 9; and the sibling stories that BSB-37 declares dependencies on: BSB-18, BSB-22, BSB-23,
BSB-24, BSB-25, BSB-31, BSB-32 and BSB-34. Also checked the epic entries for BSB-19, BSB-21,
BSB-26, BSB-27, BSB-29, BSB-30 and BSB-33 far enough to confirm which dependencies are planned
deliverables; BSB-27, BSB-29 and BSB-30 have no stories yet. Read
`shared/_SHARED-project-layout.md` and `config/sdlc-wf-planning-epic.yaml` for paths and the
review hand-off. There is no `AGENTS.md` or `CLAUDE.md` at the repo root, so the shared default
layout applies; the BSB-37 folder and `docs/product` paths used here match that default.

**Missing design artifacts.** There is no `docs/architecture.md`, `docs/data-model.md`,
`docs/api-contracts/` or `docs/ui-conventions.md` in this repo, and no
`docs/product/epics/BSB-37/_epic/epic-sequence.{md,json}`. This matches the BSB-36 review's
finding; context comes from ADR SK-001, the PRD, `epics.md`/`epic-map.json`, and sibling stories.
No modules that only other epics touch were loaded.

## Findings

### Finding 1 — Cross-epic contract fit: the CLI run request contradicts BSB-24's build-required run-start contract
- **Severity:** Blocking
- **Stories touched:** BSB-37-PENDING-1, BSB-37-PENDING-5 (and, across epics, BSB-24-PENDING-1; BSB-27, whose stories are not written yet)
- **Evidence:**
  - `docs/product/epics/BSB-37/_epic/stories.md:34-39` says "A CLI run calls BSB-24's run-start service with the skill name and skills ref instead of a `build_id`. `runs.build_id` is the id of the open build whose skill and branch match ... and NULL when no open build matches. ... the web contract still requires it."
  - `docs/product/epics/BSB-37/_epic/stories.md:173-176` repeats that "`runs.build_id` is resolved ... when no open build matches, the column is NULL" and "the web request still requires it."
  - The `run` command has no `--build` flag (`stories.md:84`, `stories.md:145-148`); its first AC starts a run and expects `build_id 7` to be resolved server-side from the open build (`stories.md:84-85`).
  - `docs/product/epics/BSB-37/_epic/stories.md:515-516` says "The run-start service is BSB-24's, extended for a skill-and-ref request exactly as BSB-37-PENDING-1 uses it."
  - `docs/product/epics/BSB-24/_epic/stories.md:93-100` says "The request fields are `build_id` (required), `skills_branch` (required) ... and `model_profile_id` and `tier` (required) ... and BSB-37 uses the same contract for the command line."
  - `docs/product/epics/BSB-24/_epic/stories.md:116-120` says BSB-27's preflight "calls BSB-31-PENDING-1's static-scan route for the run's project and resolved SHA (for build 7, POST `/api/builds/7/scans/static`)" — there is no stated no-build path.
- **What is missing/ambiguous/contradictory:** BSB-24 defines one run-start contract and says the CLI uses it, but that contract requires a `build_id`; BSB-37 explicitly defines a different request (skill + skills ref, no build id) and relies on a server-side open-build lookup. The same split leaves BSB-27's build-keyed preflight with no build to address for a CLI run whose open build does not exist. `runs.build_id` nullability is asserted only by BSB-37, not by the run-start owner.
- **Question (if a person must decide):** Should BSB-24's run-start service accept a skill-and-ref request with a nullable `runs.build_id` and resolve the build id server-side, or must the CLI require a build and send `build_id`? If the former, how should BSB-27's preflight address the static scan for a run with no build?
- **Proposed change:**
  - **BSB-24-PENDING-1:** Add the CLI request variant explicitly (project, skill, skills_ref, input_branch, context, model profile/tier; no build_id; nullable `runs.build_id` resolved server-side), and make the "BSB-37 uses the same contract" sentence true. Alternatively, remove that sentence and state that the CLI is a separate caller that must supply `build_id`.
  - **BSB-37-PENDING-1:** Align the AC and Notes with the chosen contract. If build-required, add `--build` and delete the no-build resolution paragraph; if skill+ref, cite BSB-24's variant and keep the `NULL` rule.
  - **BSB-37-PENDING-5:** Point the suite's run-start paragraph (`stories.md:515-516`) at the same chosen contract so manual suite entries do not depend on an undefined extension.
  - **BSB-37-PENDING-1 and BSB-27 (future):** Record that a run with no build calls the static-scan service by project + resolved SHA, not `/api/builds/{id}/scans/static`; carry the requirement into BSB-27's stories when they are written.

### Finding 2 — Cross-epic dependency: the CLI scan assumes run-less packaging and an independently callable full-scan service that BSB-25/BSB-32 do not define
- **Severity:** Blocking
- **Stories touched:** BSB-37-PENDING-2, BSB-37-PENDING-3 (and, across epics, BSB-25-PENDING-1, BSB-25-PENDING-2, BSB-32-PENDING-2)
- **Evidence:**
  - `docs/product/epics/BSB-37/_epic/stories.md:243-248` says the static scan "resolves `--skill` and `--skills-ref` to a commit and a `skill_bundles` row through the same BSB-25 path a run uses, then calls BSB-31-PENDING-1's static scan service with the project, skill, commit SHA and bundle and no build id; BSB-31-PENDING-1 must expose that service independently of its build-keyed route."
  - `docs/product/epics/BSB-37/_epic/stories.md:323-326` says the full scan "resolves the skill and ref through BSB-25's packaging path, then calls the same full-scan service BSB-32-PENDING-2 uses with the project, skill, commit SHA and bundle and no build id; BSB-32-PENDING-2 must expose that service independently of its build-keyed route."
  - `docs/product/epics/BSB-25/_epic/stories.md:52-54` says the resolver processes a requested `runs` row and sets `runs.skills_commit_sha` and `runs.state`; `stories.md:95-102` says the worker picks up `runs` rows in state `requested` and runs the resolver, packager and branch preparer; `stories.md:139-141` says the packager processes run 21.
  - `docs/product/epics/BSB-25/_epic/stories.md:85`, `:185` and `:272-273` put "the command-line run (BSB-37)" out of scope but say nothing about a command-line scan or a run-less packaging path. Every BSB-25 acceptance criterion is built on a `runs` row.
  - `docs/product/epics/BSB-32/_epic/stories.md:160-161` says BSB-32-PENDING-2 owns "the full-scan request contract and route POST `/api/builds/7/scans/full`"; `stories.md:168-180` defines the route and its response but does not state a service entry point independent of the build-keyed route.
  - Checked: `docs/product/epics/BSB-31/_epic/stories.md:447-448` calls the static scan service directly with a bundle fixture "so no build or project is needed", so BSB-31's static service is already independently callable. The remaining one-sided contract is `scans.build_id` nullability, asserted only in BSB-37 (`stories.md:40-44`, `:249-250`, `:319-321`); BSB-31's data-model list (`stories.md:82-86`) does not state it.
- **What is missing/ambiguous/contradictory:** The CLI scan stories require "the same BSB-25 path a run uses" while creating no `runs` row, but BSB-25's resolver and packager are specified as run-row state machines. They require an entry point that takes project/skill/skills-ref and returns a commit and a `skill_bundles` row without a run or a run-state transition; no BSB-25 story defines one. Likewise, BSB-37 requires BSB-32-PENDING-2 to expose the full-scan service independently of its route, but BSB-32's story only specifies the route. Without those contracts, FR-117 and FR-118 cannot be implemented as written.
- **Question (if a person must decide):** Should BSB-25 and BSB-32 be revised to expose these service entry points for the CLI, or should the command-line scan stories (FR-117/FR-118) be deferred until those contracts exist?
- **Proposed change:**
  - **BSB-25-PENDING-1 and BSB-25-PENDING-2 (or a small new BSB-25 story):** Add a run-less service contract that resolves a skill/ref to a commit and packs or reuses a content-addressed bundle, returning the commit and bundle without creating or transitioning a `runs` row. Name the exact entry point.
  - **BSB-32-PENDING-2:** State a direct full-scan service entry point independent of `POST /api/builds/{id}/scans/full`, accepting project, skill/commit SHA and bundle; state that the LLM `scans.build_id` is NULL for a no-build caller.
  - **BSB-37-PENDING-2 and BSB-37-PENDING-3:** Name the actual BSB-25 and BSB-32 entry points in Notes, and repeat that `scans.build_id` must be nullable for both static and LLM rows. Note that BSB-31-PENDING-7 already covers the static service's direct call.
  - **If the answer is defer:** Move PENDING-2 and PENDING-3 out of the MVP release and update the epic's release split and traceability, rather than claiming a service that no story provides.

### Finding 3 — Cross-story actor & role consistency: a manual suite run's user is undefined, and `suites.created_by` is called both "creator" and "suite owner"
- **Severity:** Advisory
- **Stories touched:** BSB-37-PENDING-5, BSB-37-PENDING-6, BSB-37-PENDING-7 (and BSB-22's project "owner" role)
- **Evidence:**
  - `docs/product/epics/BSB-37/_epic/stories.md:451-454`: Ada is both `created_by 42` and the runner; `suite_runs.user_id` and both `runs.user_id` values are 42. The story never says whether that is because Ada is the runner or because she created the suite.
  - `docs/product/epics/BSB-37/_epic/stories.md:524-527`: a `suite_runs` row is "failed" when no entry can be attempted, including when the cause is "a non-member suite owner" — a creator-identity rule, but stated for manual runs without an AC.
  - `docs/product/epics/BSB-37/_epic/stories.md:595-597`: the scheduler reads `suites.created_by` and uses that user as `suite_runs.user_id` and each `runs.user_id`; a creator who is no longer a project member makes the execution fail. This is explicit, but only for scheduled runs.
  - `docs/product/epics/BSB-37/_epic/stories.md:635-638`: the scenario title says "creator has left", while the user-visible `failure_reason` and page text say "The suite owner is no longer a project member." The story uses both terms for the same `suites.created_by` value.
  - `docs/product/epics/BSB-22/_epic/stories.md:30` and `:62`: the project page renders "Owner: ..." and `project_members.role` is `(owner, member)`, so "suite owner" is easily confused with the project's owner role.
- **What is missing/ambiguous/contradictory:** For a manual suite run triggered by a project member who is not `suites.created_by`, the story set does not say whether `suite_runs.user_id` and each entry's `runs.user_id` are the signed-in runner or the suite creator. PENDING-5's Notes imply creator identity (a non-member suite owner is a failure cause), while PENDING-6 states creator identity only for scheduled runs. PENDING-7 then calls the creator the "suite owner", a term BSB-22 already uses for a project role.
- **Question (if a person must decide):** For a manual suite run by a project member who is not `suites.created_by`, should `suite_runs.user_id` and each entry's `runs.user_id` be the signed-in runner or the suite creator? Does the "creator is no longer a member" failure apply to manual runs as well as scheduled ones?
- **Proposed change:**
  - **BSB-37-PENDING-5:** State the manual-run rule explicitly in Notes and add an AC where a different project member (e.g. Bob) runs Ada's suite, asserting both user-id fields and whether the creator-membership check fails the run. Keep the rule consistent with PENDING-5's existing "non-member suite owner" failure cause.
  - **BSB-37-PENDING-6:** Keep the scheduled rule (creator identity) and use "suite creator (`suites.created_by`)" consistently.
  - **BSB-37-PENDING-7:** Use the same term and change the exact message to "The suite creator is no longer a project member." (or define "suite owner" explicitly as `suites.created_by` and use it everywhere). Avoid the bare "owner" that BSB-22 uses for a project role.
  - **BSB-37 scope decisions:** State in the "Nightly schedule" or "Result record" decision whether manual and scheduled runs share one identity rule or differ.

### Finding 4 — Cross-story suite fixture contract drift: `context` nullability and the model profile's `test_only`
- **Severity:** Advisory
- **Stories touched:** BSB-37-PENDING-4, BSB-37-PENDING-5, BSB-37-PENDING-6, BSB-37-PENDING-7 (and BSB-24-PENDING-4, BSB-23-PENDING-6)
- **Evidence:**
  - `docs/product/epics/BSB-37/_epic/stories.md:413-416` fixes `suites.definition` as `"context": {"workflow": string or null, "step": string or null, "reviewer_feedback": string or null, "upstream_handoff": string or null}`. The `context` value itself is an object; null is not in the shape.
  - The skip/failure fixtures in PENDING-5 and every fixture in PENDING-6 and PENDING-7 use `"context": null`: `stories.md:462`, `:467`, `:472` (PENDING-5), `:554` (PENDING-6), `:621`, `:626`, `:631`, `:636`, `:641`, `:646` (PENDING-7). PENDING-5's first AC (`stories.md:451-454`) uses object contexts and matches PENDING-4, so the two encodings coexist in the story set. A validator or data-model constraint written from PENDING-4's object-only shape would reject the null fixtures the later scenarios depend on.
  - `docs/product/epics/BSB-37/_epic/stories.md:380-382` refuses a model profile with `test_only false`; `stories.md:151-152` says `--model-profile` names a profile "whose config `test_only` is true"; `docs/product/epics/BSB-24/_epic/stories.md:308-310` refuses a non-test profile with "The selected model profile is not available for runs in this project."
  - PENDING-1's integration 4 has `config {"name": "Default", ..., "test_only": true}` (`stories.md:83`) and PENDING-4's integration 4 has `config {"name": "Default", "test_only": true}` (`stories.md:355`). PENDING-5 (`stories.md:452`), PENDING-6 (`stories.md:554`) and PENDING-7 (`stories.md:621`) say only "'ai_model' integration 4" and omit its config/`test_only`.
- **What is missing/ambiguous/contradictory:** The suite definition's authoritative shape does not admit the null context used by PENDING-5's skip/failure scenarios and every PENDING-6/-7 scenario, and those suite-run fixtures do not establish the test-purpose model profile that run-start validation requires. Implemented literally, PENDING-4's schema and BSB-24's profile validation can reject the data the later ACs assume, so the suite-run scenarios may fail before an entry is requested.
- **Question (if a person must decide):** None — this is an alignment fix. (Confirm only that the intended context encoding is null, matching `runs.context`, rather than an all-null object.)
- **Proposed change:**
  - **BSB-37-PENDING-4:** Change the shape to `"context": object or null` and state that an omitted/empty context is stored as `null` (consistent with `runs.context` in BSB-24-PENDING-1), or require an all-null object and change the later fixtures. Also state that save-time validation accepts the chosen null form.
  - **BSB-37-PENDING-5, BSB-37-PENDING-6, BSB-37-PENDING-7:** Repeat `config {"name": "Default", "test_only": true}` on integration 4 in every suite fixture, or state in each Given that it is the PENDING-4 integration 4 row (test purpose). Align the context fixtures with PENDING-4's chosen shape.

### Finding 5 — Cross-story reachability: main-only suite entries are valid and used at run time, but the suite form cannot select them
- **Severity:** Advisory
- **Stories touched:** BSB-37-PENDING-4, BSB-37-PENDING-5
- **Evidence:**
  - `docs/product/epics/BSB-37/_epic/stories.md:423-425`: "Each entry's skill must exist as an open build's skill or on the catalog `main` ref."
  - `docs/product/epics/BSB-37/_epic/stories.md:428-429`: the form at `GET "/projects/7/suites/new"` "lists only the project's open-build skills and sandbox branches."
  - `docs/product/epics/BSB-37/_epic/stories.md:435-436`: "a skill that exists only on `main` uses `main` and records no build id (see PENDING-5)."
  - `docs/product/epics/BSB-37/_epic/stories.md:512-513`: PENDING-5 resolves an entry "to `main` when the skill exists there" before skipping it.
- **What is missing/ambiguous/contradictory:** A main-only skill is valid at save-time validation and is a supported run-time resolution, but the only UI path to create an entry offers open-build skills only. A member cannot create a main-only entry through the form; only a hand-crafted POST can. The fallback PENDING-5 implements is unreachable through the interface the epic says is the suite surface.
- **Question (if a person must decide):** Should the suite form list catalog `main`-only skills as choices, or should main-only entries be rejected at save and the PENDING-5 `main` fallback removed?
- **Proposed change:**
  - **BSB-37-PENDING-4 (if list):** Include main-only skills in the form's skill choices (label them as no-build/main entries) and keep the save-time `main` clause. If reject: change validation to open-build skills only, remove the `main` clause from `stories.md:423-425` and `:435-436`, and state the refusal message.
  - **BSB-37-PENDING-5 (if reject):** Remove the `main` fallback and the "records no build id" language, and update the skip scenario accordingly. If list: keep the fallback and add a scenario with a main-only skill.

### Finding 6 — Epic boundary: no story owns the project page's saved-suite list or link
- **Severity:** Advisory
- **Stories touched:** BSB-37-PENDING-4, BSB-37-PENDING-5, BSB-37-PENDING-6, BSB-37-PENDING-7 (and BSB-22-PENDING-1's project page)
- **Evidence:**
  - `docs/product/epics/BSB-37/_epic/stories.md:62-65` says "Saving, running and scheduling a saved suite are project-page features in this epic."
  - `docs/product/epics/BSB-37/_epic/stories.md:397` puts "project-level suite lists beyond the project page" out of scope, which leaves a project-page list in scope.
  - PENDING-4's ACs define `POST "/projects/7/suites"`, `GET "/projects/7/suites/new"` and `GET "/projects/7/suites/5"` (`stories.md:354-357`), but no story AC renders a suite list or a suite link on `GET "/projects/7"`.
  - PENDING-5, PENDING-6 and PENDING-7 all start from `GET "/projects/7/suites/5"` or an already-known suite id (`stories.md:453`, `:545`, `:622`); no scenario discovers a suite.
  - `docs/product/epics/BSB-22/_epic/stories.md:30` and `:62` says `GET "/projects/7"` renders the project name, owner and members; it has no suite section.
- **What is missing/ambiguous/contradictory:** The epic calls saving/running/scheduling project-page features, and PENDING-4's out-of-scope wording implies the project page carries a suite list, but no story owns the list or the link from the project page to a suite. A member who does not already know suite id 5 has no stated way to reach it. This is an epic-boundary hole, not a single-story omission: every suite surface is reachable only by a URL constructed from an id.
- **Question (if a person must decide):** Should `GET "/projects/7"` render the project's saved suites with links to their suite pages (and which story owns that AC), or are saved suites intentionally reachable only by direct URL?
- **Proposed change:**
  - **BSB-37-PENDING-4 (or a small new BSB-37 story):** Add an AC for `GET "/projects/7"` (or a project-page section) rendering the project's saved suite names and links to `GET "/projects/7/suites/{id}"`, coordinating with BSB-22-PENDING-1's project page. If the project page itself is BSB-22's, record the cross-epic change there rather than claiming BSB-37 owns the whole page.
  - **If direct URL only:** State that explicitly in the BSB-37 scope decision and remove "project-page features" / "beyond the project page" wording that implies a list.

### Finding 7 — Cross-epic dependency: suite result retention is handed to BSB-34, which explicitly does not delete database metadata
- **Severity:** Advisory
- **Stories touched:** BSB-37-PENDING-7 (and BSB-34-PENDING-3, BSB-34-PENDING-4)
- **Evidence:**
  - `docs/product/epics/BSB-37/_epic/stories.md:656-657` puts "retaining results beyond the run-retention setting (BSB-34)" out of scope; `stories.md:688` says "the general retention and purge rules are BSB-34's."
  - `docs/product/epics/BSB-34/_epic/stories.md:275-279` puts out of scope "deleting the `runs` row, its verification record, its verdicts, its usage values or any other database metadata"; `stories.md:288-303` says the sweep deletes every object under `runs/<run-id>/` and "never deletes the `runs` row or its verdict, verification or usage columns."
  - BSB-34's stories do not mention `suites`, `suite_runs` or `suite_run_entries` anywhere.
- **What is missing/ambiguous/contradictory:** PENDING-7 points suite-result retention at BSB-34, but BSB-34 owns run-artifact retention and explicitly excludes database metadata. `suite_runs` and `suite_run_entries` are database metadata, not run artifacts, so no story currently says whether they expire, are purged, or persist. The dependency is one-sided and points at a scope that will not touch the suite tables.
- **Question (if a person must decide):** Should suite result rows persist like `runs` rows (consistent with BSB-34's "database metadata" exclusion), or should they expire or be purged with the linked runs? If they expire or are purged, what happens to the suite run's counts and entry rows when a linked run's data is purged?
- **Proposed change:**
  - **BSB-37-PENDING-7:** Replace the unsupported "retaining results beyond the run-retention setting (BSB-34)" out-of-scope item with the actual rule. Either state that `suite_runs`/`suite_run_entries` are database metadata and, like `runs` rows, are not removed by BSB-34's artifact sweep (so they persist), or name the story that will delete/expire them.
  - **BSB-34-PENDING-3 and BSB-34-PENDING-4 (if they should expire/purge):** Add suite rows to the sweep/purge contract and define the linked-run behavior; otherwise state explicitly that suite result rows are out of scope, matching the current out-of-scope list.

### Finding 8 — Cross-story CLI gate parity and exact group-denial message
- **Severity:** Advisory
- **Stories touched:** BSB-37-PENDING-1, BSB-37-PENDING-2, BSB-37-PENDING-3 (and BSB-18-PENDING-3)
- **Evidence:**
  - `docs/product/epics/BSB-37/_epic/stories.md:90` covers five refusals: no `SKILL_BUILDER_TOKEN`, unverifiable token, expired token, token outside `skill-builders`, and a valid token with no local `users` row. It also asserts "standard output and standard error contain no part of any token value."
  - `docs/product/epics/BSB-37/_epic/stories.md:127` says the story depends on BSB-18-PENDING-3 for "the exact group-denial message", but `stories.md:90` writes "Access is limited to members of the skill-builders group." with a trailing period.
  - `docs/product/epics/BSB-18/_epic/stories.md:233` and `:238` give the exact message "Access is limited to members of the skill-builders group" with no trailing period.
  - `docs/product/epics/BSB-37/_epic/stories.md:203-206` (PENDING-2) and `:290-293` (PENDING-3) test only three cases: no token, unverifiable token, and a non-member. They omit the expired token, the unprivileged group token and the no-`users`-row case, and neither AC asserts that output contains no token value.
- **What is missing/ambiguous/contradictory:** The three CLI commands are specified as separate commands, but only PENDING-1 pins the full shared gate (including the no-account refusal and token redaction). PENDING-2 and PENDING-3 depend on BSB-18 for the gate but do not state that they use PENDING-1's gate or repeat its cases, so their auth behavior can drift. The "exact" group-denial message in PENDING-1 differs from BSB-18's exact string by a trailing period.
- **Question (if a person must decide):** None — this is an alignment fix, unless the trailing period is intentional, in which case BSB-18 and every other caller need the same change.
- **Proposed change:**
  - **BSB-37-PENDING-1:** Remove the trailing period so the message matches BSB-18-PENDING-3's exact string (or, if the period is intended, change BSB-18-PENDING-3 and all callers consistently).
  - **BSB-37-PENDING-2 and BSB-37-PENDING-3:** State that the `scan` commands use PENDING-1's shared CLI auth gate, and either reference its five scenarios or repeat the missing expired, unprivileged and no-account cases. Add the "no part of any token value in standard output or standard error" assertion to both commands' ACs (NFR-004's cross-cutting guarantee).

## Open questions

1. **Run-start contract (Finding 1).** Should BSB-24's run-start service accept a skill-and-ref request with a nullable `runs.build_id` and resolve the build id server-side, or must the CLI require a build and send `build_id`? If the former, how should BSB-27's preflight address the static scan for a run with no build?
2. **CLI scan service ownership (Finding 2).** Should BSB-25 and BSB-32 be revised to expose the run-less packaging and independent full-scan service entry points, or should FR-117/FR-118 be deferred until those contracts exist?
3. **Manual suite-run identity (Finding 3).** For a manual suite run by a project member who is not `suites.created_by`, should `suite_runs.user_id` and each entry's `runs.user_id` be the signed-in runner or the suite creator? Does the creator-membership failure apply to manual runs as well as scheduled runs?
4. **Main-only suite entries (Finding 5).** Should the suite form list catalog `main`-only skills as choices, or should main-only entries be rejected at save and the PENDING-5 `main` fallback removed?
5. **Project-page suite discovery (Finding 6).** Should `GET "/projects/7"` render the project's saved suites with links, or are saved suites intentionally reachable only by direct URL?
6. **Suite result retention (Finding 7).** Should `suite_runs`/`suite_run_entries` persist like `runs` rows, or expire/be purged with the linked runs? If they expire or are purged, what happens to the suite run's counts and entry rows?

## Proposed changes

Proposed, not applied. Per touched story, keyed to the findings above.

- **BSB-37-PENDING-1** — Finding 1: align the `run` command and `runs.build_id` Notes with the chosen BSB-24 contract; add or remove `--build` accordingly; record the no-build preflight path. Finding 8: remove the trailing period from the group message and pin the shared auth gate.
- **BSB-37-PENDING-2** — Finding 2: name the BSB-25 run-less resolve/pack entry point and confirm the BSB-31 static service call and nullable `scans.build_id`. Finding 8: reference the shared CLI gate, add the missing refusal cases and the no-token-output assertion.
- **BSB-37-PENDING-3** — Finding 2: name the BSB-25 run-less packaging entry point and the BSB-32 independent full-scan service; state the LLM `scans.build_id` NULL rule. Finding 8: same shared-gate and redaction additions.
- **BSB-37-PENDING-4** — Finding 4: allow `context: null` in the definition shape (or require an all-null object) and validate it. Finding 5: either list main-only skills in the form or reject them at save and remove the `main` clause. Finding 6: add the project-page suite list/link AC, or state direct-URL-only in scope.
- **BSB-37-PENDING-5** — Finding 3: state the manual-run identity rule and add a non-creator member scenario; use "suite creator (`suites.created_by`)" consistently. Finding 4: repeat `test_only true` and align context fixtures. Finding 5: keep or remove the `main` fallback to match PENDING-4's decision.
- **BSB-37-PENDING-6** — Finding 3: use "suite creator (`suites.created_by`)" consistently. Finding 4: repeat `test_only true` and align context fixtures.
- **BSB-37-PENDING-7** — Finding 3: use "suite creator (`suites.created_by`)" and change the failure message to "The suite creator is no longer a project member." Finding 4: repeat `test_only true` and align context fixtures. Finding 7: replace the BSB-34 retention hand-off with the actual persistence or purge rule.
- **BSB-24-PENDING-1** — Finding 1: add the CLI skill-and-ref request variant with nullable `runs.build_id`, or remove the "BSB-37 uses the same contract" claim and require `build_id`; make the preflight's no-build path explicit.
- **BSB-25-PENDING-1 and BSB-25-PENDING-2** — Finding 2: add the run-less resolve/pack service contract, returning the commit and bundle without a `runs` row or run-state transition.
- **BSB-32-PENDING-2** — Finding 2: add the independent full-scan service entry point and state the no-build caller's LLM `scans.build_id` is NULL.
- **BSB-34-PENDING-3 and BSB-34-PENDING-4** — Finding 7: if suite result rows should expire or be purged, add them to the sweep/purge contract and define linked-run behavior; otherwise state explicitly that `suite_runs`/`suite_run_entries` are database metadata outside the artifact sweep.
- **BSB-18-PENDING-3** — Finding 8: either keep the no-period exact message and have PENDING-1 match it, or add the period here and in every other caller; do not leave the two strings different.
- **BSB-37 scope decisions (`stories.md:26-65`)** — Findings 3 and 6: state the manual-versus-scheduled suite-run identity rule and the project-page suite surface. Finding 2: if the CLI scan is deferred, update the MVP subset and release split.
- **BSB-27 (future stories)** — Finding 1: carry the no-build/no-build-id preflight requirement into its stories when they are written; BSB-37's "unchanged" claim is not implementable for a NULL-build run until then.
- **Checked, no change required:** BSB-31-PENDING-1 and BSB-31-PENDING-7 already expose and directly call the static scan service without a build or project; BSB-31's data-model note may optionally repeat `scans.build_id` nullability for the CLI caller.

## Architecture impact

None required for these seven stories.

The stories add `runs.build_id`, `suites.created_by`, `suites.schedule_enabled`, `suites.created_at`,
`suite_runs` and `suite_run_entries`, and make `scans.build_id` nullable. All are explicitly handed
to the data-model stage in the stories' Notes; ADR SK-001 section 9 already models `suites` with a
`definition` JSONB and a nullable `source_path`, so the builder-saved suite is within the ADR's
model. The new tables and columns are a normal data-model hand-off, not an architecture conflict
that needs `sdlc-arch-design` (amend).

One scope divergence is worth recording but does not change this verdict: ADR SK-001 sections 6
and 7 say saved suites can be run "from the UI or the CLI", while BSB-37 deliberately adds no
`suite` command and PENDING-5 puts "a command-line `suite` command" out of scope
(`stories.md:486-487`). The PRD's FR-119 to FR-123 do not require a CLI suite command, and the
stories' suite-run service is explicitly the service a later CLI client would call. Treat this as a
product-scope deferral, not an architecture gap in BSB-37; if the ADR's CLI-suite capability is
still promised for this release, assign it to a later epic or add an ADR note rather than amending
the architecture for these stories.

## Requirement coverage check

Each FR mapped to BSB-37 by `docs/product/epic-map.json` is exercised by at least one story's
acceptance criteria, with no duplicate or contradictory claim:

| Requirement | Story | Covered? | Notes |
|---|---|---|---|
| FR-116 — CLI starts a test run without the web interface | BSB-37-PENDING-1 | Yes | CLI `run`, one `runs` row, token gate and exit codes. "Without the web interface" is interpreted as no web interaction to start the run; a first-time user still needs a prior web sign-in to create the local `users` row (PENDING-1's scope decision and its no-account refusal). If the FR is read as "no web interface at all, including provisioning", the story does not satisfy it. |
| FR-117 — CLI runs a static-only security scan without a test run | BSB-37-PENDING-2 | Yes | Asserts no `runs` row, no run branch, one static `scans` row, PASS/FAIL exit codes and refusal exit 2. The run-less BSB-25 packaging dependency is Finding 2. |
| FR-118 — CLI runs a full security scan without a test run | BSB-37-PENDING-3 | Yes | Asserts static then LLM stages, both `scans` rows, no `runs` row, and the exit contract. The run-less BSB-25/BSB-32 service dependency is Finding 2. |
| FR-119 — Author saves a named suite of runs | BSB-37-PENDING-4 | Yes | `suites` row with name, definition and unique project-scoped name; save/refusal ACs. Project-page discovery is Finding 6. |
| FR-120 — Suite entry names skill, input branch, context and expectations | BSB-37-PENDING-4 | Yes, with a wording caveat | The definition has `skill`, `input_branch`, a `context` object and an `expectations` object. The only expectation stored is `final_verdict`; if the PRD's plural "expectations" means more than the final verdict, no story covers that. The context nullability contradiction is Finding 4. |
| FR-121 — Author runs a saved suite | BSB-37-PENDING-5 | Yes | Creates one run per resolvable entry, grades each against its expectation, records matched/mismatched/skipped/failed. Manual-run identity is Finding 3. |
| FR-122 — Saved suite can be scheduled for nightly execution | BSB-37-PENDING-6 | Yes | Toggle plus 02:00 UTC tick, one run per suite per date, idempotency and disabled behavior. |
| FR-123 — Builder records each scheduled run's result | BSB-37-PENDING-7 | Yes | Records date, state, counts and entry outcomes, including skips and failures, across dates. Retention ownership is Finding 7. |

**NFRs.** `epic-map.json` assigns no NFR directly to BSB-37. The cross-cutting NFRs that touch these
stories are covered elsewhere: NFR-004 (credential redaction) and NFR-006 (test-purpose
credentials) are BSB-23's, but the CLI token path is still a BSB-37 concern — PENDING-1 asserts
redaction, and PENDING-2/-3 do not (Finding 8); PENDING-4's profile validation enforces test-purpose
profiles, but the later fixtures omit `test_only` (Finding 4). NFR-012 (accessibility) is BSB-38's
and applies to the new suite pages. NFR-013/NFR-014 (retention/purge) are BSB-34's for run
artifacts; suite result rows are not covered there (Finding 7).

**Traceability.** No drift among `docs/product/PRD.md` (FR-116–FR-123), `docs/product/epics.md`'s
BSB-37 section, `docs/product/epic-map.json` and `story-map.json`: all eight requirements map to
one story each, with PENDING-4 covering both FR-119 and FR-120. No requirement is claimed by two
stories in contradictory ways. The epic's MVP/Later split matches the story releases: PENDING-1/2/3
are MVP; PENDING-4/5/6/7 are Later.

## Dependency-note sanity check

**Yes, with the mismatches below.** Every story key cited in the seven Notes sections exists, or is
an epic whose stories are not written yet (BSB-27, BSB-29, BSB-30); no note points at a
non-existent story key. The following are not reciprocated or are inconsistent with the owning
story:

- **BSB-24-PENDING-1 vs BSB-37-PENDING-1/-5 (Finding 1, Blocking):** BSB-24 says `build_id` is
  required and "BSB-37 uses the same contract"; BSB-37 says the CLI sends skill + skills ref
  instead of `build_id` and resolves `runs.build_id` server-side, nullable. This is a direct
  contract contradiction, not a build-order issue.
- **BSB-24-PENDING-1 vs BSB-27 (Finding 1, Blocking for the CLI run):** BSB-24 describes BSB-27's
  preflight as calling `POST /api/builds/7/scans/static`; a CLI run with no open build has no build
  id to put in that path. BSB-27's stories are not written, so the requirement must be carried
  forward, not assumed "unchanged".
- **BSB-25-PENDING-1/-2 vs BSB-37-PENDING-2/-3 (Finding 2, Blocking):** BSB-25's resolver and
  packager process `runs` rows in `requested`/`preparing`; BSB-37's CLI scans create no `runs` row
  and still claim "the same BSB-25 path a run uses." No BSB-25 story exposes a run-less resolve/pack
  entry point. BSB-25's out-of-scope names only "the command-line run (BSB-37)", not the CLI scan.
- **BSB-32-PENDING-2 vs BSB-37-PENDING-3 (Finding 2, Blocking):** BSB-32-PENDING-2 owns
  `POST /api/builds/7/scans/full` and does not state an independent full-scan service entry point;
  BSB-37 requires one. BSB-37 also requires the LLM `scans.build_id` to be NULL for a no-build
  caller, which BSB-32's AC does not state.
- **BSB-31-PENDING-1/-7 vs BSB-37-PENDING-2 (checked, no service gap):** BSB-31-PENDING-7 calls the
  static scan service directly with a bundle fixture "so no build or project is needed", so the
  static service side of BSB-37's dependency is supported. `scans.build_id` nullability is stated
  only in BSB-37 (`stories.md:40-44`, `:249-250`); BSB-31's data-model list does not repeat it, so
  the data-model stage must take the nullability rule from BSB-37 (or BSB-31 should add it).
- **BSB-34-PENDING-3/-4 vs BSB-37-PENDING-7 (Finding 7, Advisory):** PENDING-7 delegates suite
  result retention to BSB-34; BSB-34 explicitly excludes "any other database metadata" and its
  sweep touches only `runs/<run-id>/` objects. No BSB-34 story mentions the suite tables. The
  dependency is one-sided.
- **BSB-18-PENDING-3 vs BSB-37-PENDING-1 (Finding 8, Advisory):** BSB-18's exact group-denial
  message has no trailing period (`BSB-18/_epic/stories.md:233`, `:238`); PENDING-1 writes the
  same message with a period (`BSB-37/_epic/stories.md:90`) while claiming to use the exact
  message. The three CLI commands also do not all repeat the shared gate's refusal cases.
- **BSB-22-PENDING-1 vs BSB-37's suite surface (Finding 6, Advisory):** BSB-22's `GET "/projects/7"`
  project page renders the project name, owner and members; no BSB-37 story adds a suite list or
  link to that page, although the epic calls suite operations project-page features and PENDING-4's
  out-of-scope wording leaves a project-page list in scope.
- **BSB-23-PENDING-3/-6 and BSB-24-PENDING-4 vs BSB-37-PENDING-5/-6/-7 (Finding 4, Advisory):**
  The model-profile dependency is correctly named, but the later suite fixtures omit the
  `config.test_only` value that those owning stories require for a run-purpose profile. The
  fixtures also use `context: null` against PENDING-4's object-only definition shape.
- **Checked, no mismatch:** BSB-19 and BSB-21 are the open-build/skill-branch owners named by
  PENDING-1/-4/-5; BSB-22-PENDING-1/-3 own the project and shared membership check; BSB-23-PENDING-2
  owns the source-control integration; BSB-24-PENDING-2/-3/-4 own the context and model fields;
  BSB-25/26/27/29 are the run pipeline; BSB-30 (readiness aggregation) has no stories yet, which
  PENDING-1's Notes state as a dependency rather than a claim. No story key is dangling.
