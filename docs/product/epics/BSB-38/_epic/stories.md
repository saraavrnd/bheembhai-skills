# Stories — BSB-38 (Accessibility conformance)

Source: Jira epic **BSB-38** — *Accessibility conformance* (feature area FA-17, release MVP,
labels FA-17 and MVP; status To Do), fetched read-only from the Atlassian project
`bheembhai-skill-builder` through its REST API. Its summary, description, functional scope,
implementation guidance, goal, stated edge cases and covered-requirement list are the same as the
BSB-38 section of `docs/product/epics.md`. The requirement IDs mapped to the epic are in
`docs/product/epic-map.json`; their exact PRD wording is in `docs/product/PRD.md`.

Epic BSB-38 covers 9 requirements. They decompose into the 9 stories below; every requirement is
covered by exactly one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-38`), is epic
**BSB-38**. No Atlassian MCP tools were offered in this session, so the epic was fetched read-only
through the Atlassian REST API with the same credentials. Nothing was written to Jira.

BSB-38 is the cross-cutting presentation bar for surfaces delivered by the other epics. It adds no
product feature: it adds the accessible names, roles, states, live regions, colour tokens,
continuous checks and reflow rules those surfaces must expose. The shared contract below is the
single source for every story's fixtures.

## Coverage summary

| Requirement | Covered by | Release |
|-------------|------------|---------|
| FR-130 | BSB-38-PENDING-1 | MVP |
| FR-131 | BSB-38-PENDING-2 | MVP |
| FR-132 | BSB-38-PENDING-3 | MVP |
| FR-133 | BSB-38-PENDING-4 | MVP |
| FR-134 | BSB-38-PENDING-5 | MVP |
| FR-135 | BSB-38-PENDING-6 | MVP |
| FR-136 | BSB-38-PENDING-7 | MVP |
| FR-137 | BSB-38-PENDING-8 | MVP |
| NFR-012 | BSB-38-PENDING-9 | MVP |

The epic's four named highest-risk surfaces are covered explicitly: status badges by
BSB-38-PENDING-3, -5 and -6; the diff viewer by BSB-38-PENDING-1, -2, -3, -6 and -9; the log
stream by BSB-38-PENDING-1, -2, -3, -5 and -9; and the file editor by BSB-38-PENDING-1, -2, -4
and -9. Dynamic readiness changes use a live region in BSB-38-PENDING-5, not a visual colour
change. The non-goals are respected: no story adds a feature, a route, a field or a workflow; each
story constrains the presentation of a surface another epic's requirement already creates.

## Accessibility conformance contract (test fixture constants)

Every scenario below starts from this fixed deployment, identity, database and browser fixture
unless it says otherwise. User sessions, local `users` rows and the `skill-builders` gate are
established by epic BSB-18. Project `7`, its membership rows and its integrations are established
by epics BSB-22 and BSB-23. Build `7`, its branch, its files and its readiness panel are
established by epics BSB-20, BSB-21 and BSB-30. Runs, their progress and their logs are established
by epics BSB-24 to BSB-29. Scan reports are established by epics BSB-31 and BSB-32. The run report
and diff viewer are established by FR-094 to FR-101 (epic BSB-33). History and compare are
established by epic BSB-35. Catalog submission is established by epic BSB-36.

**Deployment and identity fixture.**

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups` = `["skill-builders"]`, `iss` = `https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud` = `skill-builder-web` and `exp` = `2026-11-15T11:00:00Z` |
| Current time | `2026-11-15T10:00:00Z` unless a scenario sets a clock |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace`; their token's `cognito:groups` is `["skill-builders"]` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper`; their token's `cognito:groups` is `["skill-builders"]` |
| User Alan | `users.id` = `44`, `cognito_sub` = `c3d4e5f6-0000-0000-0000-000000000003`, `email` = `alan@example.com`, `name` = `Alan Turing`; their token's `cognito:groups` is `["skill-builders"]`; they have no `project_members` row for project `7` |
| User Mallory | `users.id` = `45`, `cognito_sub` = `d4e5f6a7-0000-0000-0000-000000000004`, `email` = `mallory@example.com`, `name` = `Mallory Trell`; their token's `cognito:groups` is `["catalog-reviewers"]` |
| `users` fixture | exactly four rows, the users above |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42` and `created_at` = `2026-11-14T09:00:00Z`; ids `1` to `6`, `8`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)`; Alan has no row for project `7` |
| Catalog repository | `saraavrnd/bheembhai-skills`, default branch `main` |
| Build 7 (ready fixture) | `builds` row `id` = `7`, `kind` = `edit`, `skill` = `sdlc-fix-bug-triage`, `cloned_from` = `NULL`, `branch` = `build/sdlc-fix-bug-triage`, `created_by` = `42`, `head_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `ready_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `pr_url` = `NULL`, `pr_number` = `NULL`, `pr_state` = `NULL` and `state` = `open`; its readiness values are `manifest` = `passed`, `run` = `passed`, `static` = `passed`, `llm` = `complete` |
| Build 8 (submitted fixture) | identical to build `7` except `id` = `8`, `state` = `submitted`, `pr_url` = `https://github.com/saraavrnd/bheembhai-skills/pull/41`, `pr_number` = `41` and `pr_state` = `open` |
| Build 9 (not-ready fixture) | `builds` row `id` = `9`, `kind` = `create`, `skill` = `sdlc-fix-bug-triage`, `cloned_from` = `NULL`, `branch` = `build/sdlc-fix-bug-triage-2`, `created_by` = `43`, `head_sha` = `5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b`, `ready_sha` = `NULL`, `pr_url` = `NULL`, `pr_number` = `NULL`, `pr_state` = `NULL` and `state` = `open`; its readiness values are `manifest` = `passed`, `run` = `not_run`, `static` = `not_run`, `llm` = `not_run` |
| Builds 1 to 6 and 10 to 16 | unrelated fixture builds with distinct skills and branches |
| Run 1 | `runs` row `id` = `1`, `project_id` = `7`, `user_id` = `42`, `skill` = `sdlc-fix-bug-triage`, `skills_ref` = `build/sdlc-fix-bug-triage`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `input_branch` = `main`, `run_branch` = `skilltest/1`, `state` = `completed`, `claimed_verdict` = `completed`, `final_verdict` = `completed`, `verification` = `{"status":"passed","checks":[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"passed","message":"required change present"},{"id":"scope","status":"passed","message":"within scope"}]}`, `kind` = `run`, `turn_count` = `12`, `input_tokens` = `12000`, `output_tokens` = `3000`, `cost_usd` = `0.42`, `trace_url` = `https://langfuse.skillbuilder.internal/project/skill-builder/traces/run-1`, `evidence_purged_at` = `NULL`, `created_at` = `2026-11-15T09:00:00Z` |
| Run 2 | identical to run `1` except `id` = `2`, `user_id` = `43`, `skills_commit_sha` = `5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e`, `run_branch` = `skilltest/2`, `input_branch` = `release/2.4`, `claimed_verdict` = `changes_requested`, `final_verdict` = `changes_requested`, `verification` = `{"status":"passed","checks":[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"failed","message":"required change missing"},{"id":"new-check","status":"passed","message":"new rubric satisfied"}]}` and `created_at` = `2026-11-15T11:00:00Z` |
| Run 3 (running fixture) | identical to run `1` except `id` = `3`, `run_branch` = `skilltest/3`, `state` = `running`, `claimed_verdict` = `NULL`, `final_verdict` = `NULL`, `verification` = `NULL` and `created_at` = `2026-11-15T10:30:00Z` |
| Run 7 (failed-start fixture) | identical to run `1` except `id` = `7`, `run_branch` = `NULL`, `state` = `failed_infra`, `claimed_verdict` = `NULL`, `final_verdict` = `NULL`, `verification` = `NULL` and `created_at` = `2026-11-15T07:00:00Z` |
| `runs` fixture | exactly four rows, runs `1`, `2`, `3` and `7`; `SELECT count(*) FROM runs` is `4` |
| Run 1 progress object | `s3://skill-builder-runs/runs/1/progress.json` contains exactly `{"step":"triage","state":"running","message":"Reading issue LEARN-87","percent":40,"updated_at":"2026-11-15T10:01:05Z"}` |
| Run 1 log object | `s3://skill-builder-runs/runs/1/agent.log` contains exactly the three lines `2026-11-15T10:01:01Z INFO starting skill sdlc-fix-bug-triage`, `2026-11-15T10:01:03Z INFO reading issue LEARN-87` and `2026-11-15T10:01:05Z INFO writing bug-triage.md` |
| Run 1 diff | exactly three lines: the added line `+New content`, the removed line `-Old content` and the unchanged line with two leading spaces followed by `Same content` |
| Run 3 progress object | `progress.json` contains exactly `{"step":"triage","state":"running","message":"Reading issue LEARN-87","percent":40,"updated_at":"2026-11-15T10:01:05Z"}` |
| Static scan 12 | `static_scans` row `id` = `12`, `skill` = `sdlc-fix-bug-triage`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `state` = `completed`, `verdict` = `passed`, `score` = `100`, `recommendation` = `INSTALL`, `coverage` = `complete`, `findings` = `[]` |
| LLM scan 51 | `llm_scans` row `id` = `51`, `skill` = `sdlc-fix-bug-triage`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `state` = `complete`, `model` = `test-model-medium`, `error` = `NULL`, `findings` = `[{"severity":"HIGH","rule":"SP-0090","file":"skills/sdlc-fix-bug-triage/templates/report.md","line":4},{"severity":"MEDIUM","rule":"SP-0117","file":"skills/sdlc-fix-bug-triage/references/run.md","line":8}]` |
| Static scan 19 (failed fixture) | `static_scans` row `id` = `19`, `skill` = `sdlc-fix-bug-triage`, `state` = `failed`, `verdict` = `failed`, `score` = `NULL`, `recommendation` = `NULL`, `findings` = `[]`, `error` = `scan_timeout` |
| LLM scan 54 (unavailable fixture) | `llm_scans` row `id` = `54`, `skill` = `sdlc-fix-bug-triage`, `state` = `unavailable`, `model` = `NULL`, `error` = `llm_model_profile_missing`, `findings` = `[]` |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |
| Scan-row seeding | a scenario that exercises a scan result seeds exactly the scan rows it names for that content; no other `static_scans` or `llm_scans` row exists for that content while the scenario runs |
| Browser | Chromium `131.0.6778.33`, driven by Playwright `1.49.0`; `deviceScaleFactor` = `1`; JavaScript enabled; no extensions |
| Desktop viewport | `1280` by `800` CSS pixels |
| Reflow viewport | `320` by `256` CSS pixels |
| Accessibility tree tooling | Playwright assertions `toHaveRole` and `toHaveAccessibleName`; the tree is read with `locator.ariaSnapshot()` |
| Automated checker | `@axe-core/playwright` `4.10.2` with tags `wcag2a`, `wcag2aa`, `wcag21a` and `wcag21aa` |
| Test command | `npx --prefix skill-builder/app playwright test --config skill-builder/app/tests/a11y/playwright.config.ts` |

**Surface inventory.** The accessibility bar applies to these 8 MVP builder web surfaces. Every
story that says "every surface" iterates exactly this list, in this order. The Later-release saved
suites and nightly schedule (FR-119 to FR-123, epic BSB-37) are not MVP surfaces and are not in
this inventory; they inherit this bar when they are delivered.

| # | Surface | Route | Regions and controls in scope |
|---|---------|-------|-------------------------------|
| 1 | Builds list | `GET /builds` | The build table, its row links, and the build create/clone/edit form (`#build-form`) |
| 2 | Build page | `GET /builds/7` | `#build-state`, `#readiness-checks` and its four check rows, `#static-scan-report`, `#llm-scan-report`, `#submit-to-catalog`, `#submit-to-catalog-button`, `#catalog-pull-request` |
| 3 | File editor | `GET /builds/7/files` | `#file-path`, `#file-content`, `#save-file` |
| 4 | Run start | `GET /projects/7/runs/new` | The run-start form (`#run-form`) and its controls, including its submit control `#start-run` |
| 5 | Run page | `GET /projects/7/runs/1` | `#run-outcome`, `#run-final-verdict`, `#run-progress`, `#run-log`, `#run-diff`, `#run-evidence`, `#run-trace` |
| 6 | Project settings | `GET /projects/7/settings` | The integrations and settings form (`#settings-form`) and its save control `#save-settings` |
| 7 | Skill history | `GET /skills/sdlc-fix-bug-triage/history` | `#skill-history` and its verdict cells |
| 8 | Run compare | `GET /runs/compare?left=1&right=2` | `#run-comparison`, `#compare-flips`, `#compare-skill` |

Every surface is rendered inside one `main` landmark. A surface's page has exactly one `h1`. The
sign-in page is the platform's hosted Cognito UI and is not a builder surface; it is out of scope.

**Interactive-control selector.** On each surface, the keyboard-reachable controls are the
elements matching exactly:

`a[href], button:not([disabled]), input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])`

inside `main`. A disabled control is not in this set, but its disabled state must still be exposed.
A control is "operable" when its action can be performed with `Enter` or `Space`, or, for a text
input, `select` or `textarea`, by typing. Arrow keys move between options of a `select`, radio group
or tab list.

**Focus indicator.** Every element in the interactive-control selector, when focused by keyboard,
has exactly these computed styles:

| Property | Exact value |
|----------|-------------|
| `outline-width` | `3px` |
| `outline-style` | `solid` |
| `outline-color` | `rgb(11, 87, 208)` (`#0B57D0`) |
| `outline-offset` | `2px` |
| `border-radius` | `2px` |
| `box-shadow` | has no value that is required for the indicator; the indicator survives when `box-shadow` is removed |
| `scroll-margin-block` | `24px` |

The `:focus` rule applies the indicator, not only `:focus-visible`; no surface removes it with
`outline: none` or `outline: 0`. In forced-colours mode the computed `outline-color` is
`Highlight` and the outline width is still `3px`. A focused control is scrolled fully into view
with at least `24px` above and below it, and its outline is not clipped by an ancestor's
`overflow: hidden`.

**Status-component semantics.** Status components keep the exact visible text fixed by the epic
that owns them and add the following role, name and state. When an element's accessible name is
given as "same as its visible text", the element's `aria-label` is exactly that visible text, so
the visible label is contained in the accessible name.

| Component | Role | Accessible name | State exposed |
|-----------|------|-----------------|---------------|
| `#build-state` | `img` | same as its visible text, for example `State: Open` | the state word in the name |
| `#pull-request-state` | `img` | same as its visible text, for example `Pull request: None` | the state word in the name |
| `#readiness-manifest` | `img` | same as its visible text, for example `Manifest: Passed` | the result word in the name |
| `#readiness-run` | `img` | same as its visible text, for example `Run: Passed` | the result word in the name |
| `#readiness-static` | `img` | same as its visible text, for example `Static scan: Passed` | the result word in the name |
| `#readiness-llm` | `img` | same as its visible text, for example `LLM scan: Complete` | the result word in the name |
| `#static-scan-score` | `img` | same as its visible text, for example `Score: 100/100` | the score in the name |
| `#static-scan-recommendation` | `img` | same as its visible text, for example `Recommendation: INSTALL` | the recommendation in the name |
| `#llm-scan-state` | `img` | same as its visible text, for example `LLM scan: Complete` | the state word in the name |
| `#run-outcome` | `img` | same as its visible text, for example `Outcome: completed` | the outcome in the name |
| `#run-final-verdict` | `img` | same as its visible text, for example `Final verdict: completed` | the verdict in the name |
| `#run-1-verdict`, `#run-2-verdict`, `#left-verdict` and `#right-verdict` | `cell` | its own visible text, for example `completed` | the verdict is the cell's text content |
| A verdict cell inside `#run-diff` | `cell` | its own visible text, for example `completed` | the verdict is the cell's text content |
| `#static-scan-error` | `alert` | `Static scan error` | the error text is the content |
| `#llm-scan-error` | `alert` | `LLM scan error` | the error text is the content |
| `#form-errors` | `alert` | `There is a problem` | the error links are the content |
| `#run-progress` | `progressbar` | `Run progress` | `aria-valuemin` = `0`, `aria-valuemax` = `100`, `aria-valuenow` = the percent, and `aria-valuetext` = the same sentence as the visible progress text |
| `#run-log` | `log` | `Run log` | `aria-describedby` names `#run-log-truncation` only when the log is truncated |
| `#run-diff` | `table` | `Diff: main to skilltest/1` | `role="row"` lines with `role="cell"` status cells |
| `#readiness-checks` | `region` | `Readiness checks` | the four check rows are its content |
| `#compare-flips` | `region` | `Checks that flipped` | the flipped-check rows are its content |

Decorative icons beside a status carry `aria-hidden="true"`. A diff line's first cell has
`role="cell"` and an accessible name of exactly `Added`, `Removed` or `Unchanged`; the line's visible
prefix is exactly `+ `, `- ` or two spaces. An unknown status value renders the exact visible text
`Unknown status: ` followed by the raw value, and exposes the same text as its accessible name.

**Form-field contract.** Every form control has a programmatic label, an instruction and, when
invalid, an error. The accessible name is exactly the "Accessible name" column. The accessible
description is the exact help text when the field is valid, and the help text followed by one space
and the exact error text when the field is invalid. Required controls carry the native `required`
attribute and `aria-required="true"`; optional controls carry neither.

| Surface | Field id | Accessible name | Exact help text | Required |
|---------|----------|-----------------|-----------------|----------|
| `/builds` | `#build-kind` | `Build kind` | `Choose create, clone or edit.` | yes |
| `/builds` | `#build-skill` | `Skill name` | `Skill name must follow sdlc-<area>-<action> using lowercase letters, digits and hyphens.` | yes |
| `/builds` | `#build-source` | `Source skill` | `Choose the catalog skill to clone or edit.` | yes when the kind is clone or edit |
| `/builds` | `#build-description` | `Description` | `One line describing what the skill does.` | no |
| `/builds/7/files` | `#file-path` | `File path` | `A file inside the skill folder.` | yes |
| `/builds/7/files` | `#file-content` | `File content` | `The full contents of the selected file.` | yes |
| `/projects/7/runs/new` | `#skill` | `Skill` | `The skill to test.` | yes |
| `/projects/7/runs/new` | `#skills-branch` | `Skills branch` | `A branch of the catalog repository.` | yes |
| `/projects/7/runs/new` | `#input-branch` | `Input branch` | `A branch of the project's sandbox repository.` | yes |
| `/projects/7/runs/new` | `#context` | `Context` | `Context must be a JSON object with optional keys workflow, step, reviewer_feedback and upstream_handoff.` | no |
| `/projects/7/runs/new` | `#model-profile` | `Model profile` | `A model profile configured for this project.` | yes |
| `/projects/7/runs/new` | `#tier` | `Tier` | `A tier mapped by the selected model profile.` | yes |
| `/projects/7/runs/new` | `#reviewer-feedback` | `Reviewer feedback` | `Text passed to the skill as reviewer_feedback.` | no |
| `/projects/7/runs/new` | `#upstream-handoff` | `Upstream handoff` | `A JSON object passed to the skill as upstream_handoff.` | no |
| `/projects/7/settings` | `#project-name` | `Project name` | `Between 1 and 80 characters.` | yes |
| `/projects/7/settings` | `#jira-site-url` | `Jira site URL` | `The base URL of the test Jira site.` | yes |
| `/projects/7/settings` | `#jira-project-key` | `Jira project key` | `The Jira project used for test data.` | yes |
| `/projects/7/settings` | `#jira-mcp` | `Jira MCP server definition` | `The MCP server definition exposed to a run.` | no |
| `/projects/7/settings` | `#github-repo` | `GitHub sandbox repository` | `Owner and repository name, for example saraavrnd/bheembhai-skill-fixtures.` | yes |
| `/projects/7/settings` | `#github-base-branch` | `GitHub base branch` | `The branch runs are created from.` | yes |
| `/projects/7/settings` | `#github-mcp` | `GitHub MCP server definition` | `The MCP server definition exposed to a run.` | no |
| `/projects/7/settings` | `#ai-model-profiles` | `AI model profiles` | `A JSON array of model profiles.` | yes |

Each help text is inside an element whose `id` is the field id followed by `-help`, and each error
is inside an element whose `id` is the field id followed by `-error`. A valid field has
`aria-describedby` naming only its help element. An invalid field has `aria-invalid="true"` and
`aria-describedby` naming its help element then its error element, in that order. A failed submit
renders `<div id="form-errors" role="alert" tabindex="-1">` with an `h2` whose text is exactly
`There is a problem` and one list link per invalid field, each link's text being that field's exact
error text and each `href` being `#` followed by the field id. Focus moves to `#form-errors` on a
failed submit. Correcting the field and resubmitting removes `aria-invalid`, removes the error
element, and leaves `aria-describedby` naming only the help element.

The fixed error texts used below are:

| Field | Condition | Exact error text |
|-------|-----------|------------------|
| `#skill` on the run-start form | empty | `A skill is required.` |
| `#project-name` on project settings | longer than 80 characters | `Project name must be 80 characters or fewer.` |
| `#build-skill` on the builds list | breaks the catalog name pattern | `Skill name must follow sdlc-<area>-<action> using lowercase letters, digits and hyphens.` |

**Live regions.** `#run-announcer` and `#readiness-announcer` are the only elements that announce
progress and readiness. Each is a `div` with `role="status"`, `aria-live="polite"`,
`aria-atomic="true"` and the class `sb-visually-hidden`, and is present in the document before the
first change. Neither is hidden with `display: none`, `visibility: hidden`, the `hidden` attribute
or `aria-hidden="true"`. The class uses exactly:

`.sb-visually-hidden { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }`

The run page refreshes both the progress region and `#run-announcer` from the existing progress API
once per second and applies a change within 2 seconds. The build page refreshes `#readiness-checks`
and `#readiness-announcer` from the existing readiness API once every 5 seconds and applies a change
within 5 seconds. An announcement is written only when the announced value changes; a refresh that
finds the same value performs no DOM mutation inside either announcer.

| Trigger | Exact text written into the announcer |
|---------|----------------------------------------|
| First run progress observed | `Run progress: Running step triage — Reading issue LEARN-87 (40%).` |
| Progress percentage or message changes | `Run progress: Running step triage — Writing bug-triage.md (80%).` |
| Run progress with no progress object | `Run progress: Waiting for the skill to report progress.` |
| Run reaches `completed` | `Run finished: completed.` |
| Run reaches `failed_infra` | `Run failed: The runtime could not be started.` |
| Readiness first rendered not ready | `Readiness: Not ready. Manifest: Passed. Run: Not run. Static scan: Not run. LLM scan: Not run.` |
| Readiness changes to ready | `Readiness changed: Ready. Manifest: Passed. Run: Passed. Static scan: Passed. LLM scan: Complete.` |
| Readiness changes to not ready | `Readiness changed: Not ready. Manifest: Passed. Run: Failed. Static scan: Passed. LLM scan: Complete.` |

**Non-colour status text.** Every status listed below carries its exact text as visible, selectable
content in the rendered page. Colour, a CSS class, an icon, a background or an `aria-label` may
repeat that meaning but never carries it alone. Applying the monochrome stylesheet
`* { color: #000000 !important; background-color: #FFFFFF !important; border-color: #000000 !important; outline-color: #000000 !important; }`
must leave every status readable and mutually distinguishable by its text.

| Status family | Exact visible text values |
|---------------|---------------------------|
| Build state | `State: Open`, `State: Submitted`, `State: Merged`, `State: Abandoned` |
| Pull-request state | `Pull request: None`, `Pull request: Open`, `Pull request: Merged`, `Pull request: Abandoned` |
| Readiness manifest | `Manifest: Passed`, `Manifest: Failed`, `Manifest: Not run` |
| Readiness run | `Run: Passed`, `Run: Failed`, `Run: Not run` |
| Readiness static scan | `Static scan: Passed`, `Static scan: Failed`, `Static scan: Not run` |
| Readiness LLM scan | `LLM scan: Complete`, `LLM scan: Unavailable`, `LLM scan: Not run` |
| Static scan | `Score: 63/100`, `Recommendation: INSTALL`, `Recommendation: DO_NOT_INSTALL`, `Recommendation: REVIEW` |
| Run outcome | `Outcome: completed`, `Outcome: changes_requested`, `Outcome: BLOCK`, `Outcome: escalation_required`, `The runtime could not be started.`, `The runtime exited with a non-zero status without a valid result.`, `The runtime exited without a classifiable result.` |
| Final verdict | `Final verdict: completed`, `Final verdict: changes_requested`, `Final verdict: BLOCK`, `Final verdict: escalation_required`, `Final verdict: failed_execution`, `Final verdict: unverified`, `Final verdict: Not verified` |
| History and compare verdict cells | `completed`, `changes_requested`, `BLOCK`, `escalation_required`, `failed_execution`, `unverified`, `Pending`, `Not verified` |
| Diff line | the status cell text `Added`, `Removed` or `Unchanged`, and the visible prefix `+ `, `- ` or two spaces |
| Log truncation | `[skill-builder] log truncated: showing the last 10485760 bytes of 12582912 bytes; 2097152 earlier bytes discarded.` |
| Unknown status value | `Unknown status: ` followed by the raw value, for example `Unknown status: mystery` |

**Colour tokens and contrast pairs.** The builder's base theme defines these CSS custom properties
on `:root`. Ratios use the WCAG 2.1 relative-luminance formula and are rounded to two decimal
places. Normal text needs at least `4.5:1`; large text (at least `24px`, or at least `18.66px` when
bold) and non-text UI or focus indicators need at least `3:1`.

| Token | Value | Tested pair | Computed ratio | Minimum |
|-------|-------|-------------|----------------|---------|
| `--sb-bg` | `#FFFFFF` | page background | not applicable | not applicable |
| `--sb-text` | `#1F2328` | `--sb-text` on `--sb-bg` | `15.80:1` | `4.5:1` |
| `--sb-text-muted` | `#57606A` | `--sb-text-muted` on `--sb-bg` | `6.39:1` | `4.5:1` |
| `--sb-surface` | `#F3F4F6` | `--sb-text` on `--sb-surface` (hover) | `14.35:1` | `4.5:1` |
| `--sb-surface` | `#F3F4F6` | `--sb-text-muted` on `--sb-surface` | `5.81:1` | `4.5:1` |
| `--sb-link` | `#0B57D0` | `--sb-link` on `--sb-bg` | `6.39:1` | `4.5:1` |
| `--sb-focus-ring` | `#0B57D0` | `--sb-focus-ring` on `--sb-bg` | `6.39:1` | `3:1` |
| `--sb-focus-ring` | `#0B57D0` | `--sb-focus-ring` on `--sb-surface` | `5.80:1` | `3:1` |
| `--sb-button-primary-bg` | `#0B57D0` | `--sb-button-primary-text` on `--sb-button-primary-bg` | `6.39:1` | `4.5:1` |
| `--sb-button-primary-bg` | `#0B57D0` | hover background `#0842A0` with `--sb-button-primary-text` | `9.14:1` | `4.5:1` |
| `--sb-button-primary-text` | `#FFFFFF` | text on primary and primary-hover backgrounds | `6.39:1` and `9.14:1` | `4.5:1` |
| `--sb-status-pass-text` | `#116329` | on `--sb-status-pass-bg` `#E6F4EA` | `6.51:1` | `4.5:1` |
| `--sb-status-fail-text` | `#A40E26` | on `--sb-status-fail-bg` `#FBE9EB` | `6.73:1` | `4.5:1` |
| `--sb-status-warn-text` | `#7A4D00` | on `--sb-status-warn-bg` `#FFF4D6` | `6.63:1` | `4.5:1` |
| `--sb-status-neutral-text` | `#424A53` | on `--sb-status-neutral-bg` `#EAEEF2` | `7.71:1` | `4.5:1` |
| Rejected candidate | `#999999` on `#FFFFFF` | palette validator input | `2.85:1` | fails `4.5:1` |

The effective background of an element is its own non-transparent `background-color`, or the first
non-transparent `background-color` found by walking up its ancestors to `html`. Transparent text
colours are not allowed on text or status tokens. The focus indicator is part of the `outline` and
sits on the effective page or surface background because of its `2px` offset.

**Continuous verification job.** The builder's accessibility gate is the GitHub Actions workflow
`.github/workflows/skill-builder-a11y.yml`, job `a11y`, on `ubuntu-latest` with a 20-minute timeout.
It runs on `pull_request` and on `push` to `main` when a changed path matches
`skill-builder/app/**`, `skill-builder/docker-compose.yml` or the workflow file itself. Its steps
are: check out; set up Python `3.12` and Node `20`; `npm ci --prefix skill-builder/app`; start the
app with `docker compose -f skill-builder/docker-compose.yml up -d`; wait until
`GET http://localhost:8000/healthz` returns HTTP 200, polling once per second for at most 60
seconds; seed the fixture with `psql "$DATABASE_URL" -f skill-builder/app/tests/fixtures/a11y-seed.sql`;
run the test command above with the JSON reporter writing `a11y-report.json`; and upload that file
with `actions/upload-artifact@v4` as artifact `skill-builder-a11y-report`, retained 30 days.

The test file `skill-builder/app/tests/a11y/surfaces.spec.ts` visits every route in the surface
inventory with Ada's member session, at both the desktop and reflow viewports. Each route is
asserted to return HTTP 200 before axe runs. Axe runs with the four WCAG tags above and no rule
disabled. A run is a **route check**; the suite must produce exactly 16 route checks (8 routes at
2 viewports). The job fails when any route check has a violation whose `impact` is `critical` or
`serious`, when a route does not return HTTP 200, or when fewer than 16 route checks are produced.
The report is a JSON object with the keys `summary` and `checks`; `summary` is an object with
`routes` = `8`, `viewports` = `2`, `checks` = `16`, `critical` and `serious`; each element of
`checks` has `route`, `viewport`, `status` and `violations`, and each violation has `id`, `impact`,
`help` and `nodes`. The job prints exactly one summary line: on success
`a11y: 16 checks, 0 critical, 0 serious`, and otherwise `a11y: 16 checks, N critical, M serious`.
Each violation also produces an annotation of the form
`::error file=skill-builder/app/templates/builds.html,line=42::button-name (critical) on /builds`,
naming the nearest template file and the rule id, impact and route. A route that does not return
HTTP 200 fails with the exact message `a11y_route_unreachable: ` followed by the route and the
status, for example `a11y_route_unreachable: /builds/7 returned 500`. A short suite fails with the
exact message `a11y_route_count: expected 16 route checks, got 14`.

**Reflow rule.** At the reflow viewport, `window.innerWidth` is exactly `320` and
`document.documentElement.scrollWidth` is less than or equal to `320` on every surface. Vertical
scrolling is allowed; horizontal scrolling, a horizontally scrollable page element, clipped text or
content reachable only by scrolling sideways is not. Long unbroken strings (commit SHAs, URLs,
skill names and JSON values) use `overflow-wrap: anywhere` and, where relevant, `word-break:
break-word`. Log and diff content uses `white-space: pre-wrap` with `overflow-wrap: anywhere`;
`#run-log` and `#run-diff` have `max-height: 12rem` and `overflow-y: auto` at the reflow viewport,
so long content scrolls vertically inside them. Textareas use `wrap="soft"` and never exceed the
viewport width. A table at a viewport of 480 CSS
pixels or less reflows each row into a block and each cell into a block whose visible `::before`
label is `attr(data-label)`, where `data-label` equals that column's header text; no cell text is
removed.

---

## STORY: BSB-38-PENDING-1

**Summary:** Operate every builder control from the keyboard on every surface
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As a **skill author who cannot use a mouse**, I want **every interactive control on every builder surface to be reachable and operable from the keyboard**, so that **I can complete every authoring task without a pointing device**.

### Acceptance Criteria

#### Scenario: Every interactive control on every surface is in the keyboard tab order
Given Ada has a valid member session and every surface fixture in the surface inventory is seeded
And each of the 8 surfaces is opened at the desktop viewport in a fresh browser page
When Ada presses `Tab` repeatedly from the start of the document until focus returns to the first control
Then on each surface the sequence of focused elements contains every element matching the interactive-control selector inside `main`
And the sequence contains no element outside that selector and no element twice
And the first focused element on every surface is the skip link whose text is `Skip to main content`
And the last focused element on every surface is the last element matching the selector in document order

#### Scenario: Every control performs its action with Enter or Space
Given Ada has a valid member session and the surface fixtures are seeded
And each surface is opened at the desktop viewport
When Ada tests each control on a fresh copy of its surface, focusing it and pressing `Enter`, and pressing `Space` when the control is a button or checkbox
Then every link's target is loaded and the link's `href` is the resulting URL
And every button's defined action is performed, for example `#save-file` sends `PUT /api/builds/7/files/SKILL.md`, `#start-run` sends `POST /api/projects/7/runs`, and `#save-settings` sends one `PUT` for each changed integration kind, beginning with `PUT /api/projects/7/integrations/jira`
And every checkbox toggles its checked state and every select changes to the next option with `ArrowDown`
And no control requires a mouse hover, a click or a drag to become visible or enabled

#### Scenario: The file editor is fully keyboard operable
Given Ada has a valid member session and build `7` has the file `SKILL.md` on branch `build/sdlc-fix-bug-triage`
And Ada opens `GET /builds/7/files` at the desktop viewport
When Ada presses `Tab` until `#file-content` has focus
And Ada types `# Skill updated` into `#file-content`
And Ada presses `Tab` until `#save-file` has focus and presses `Enter`
Then the builder receives exactly one request `PUT https://builder.skillbuilder.internal/api/builds/7/files/SKILL.md` whose body is exactly `# Skill updated` and whose `Content-Type` is `text/markdown`
And the response is HTTP 200 with a JSON body whose `path` is `skills/sdlc-fix-bug-triage/SKILL.md`, whose `branch` is `build/sdlc-fix-bug-triage` and whose `commit_sha` is `5f4e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e`
And `document.activeElement` after the save is the element with id `save-file`

#### Scenario: Scrollable log and diff regions are keyboard scrollable and never trap focus
Given Ada has a valid member session and run `1` exists with the run 1 log object and a diff whose first line is the added line `+New content`
And Ada opens `GET /projects/7/runs/1` at the desktop viewport
When Ada presses `Tab` until `#run-log` has focus
Then `#run-log` has `tabindex="0"` and `role="log"`
And pressing `PageDown` scrolls `#run-log` down by one viewport and `document.activeElement` is still `#run-log`
And pressing `Tab` once moves focus to the next element after `#run-log` inside `main`
And pressing `Shift+Tab` once returns focus to `#run-log`
And the same four checks pass with `#run-diff` in place of `#run-log`

#### Scenario: Disabled controls are skipped and expose their disabled state
Given Ada has a valid member session and build `9` is not ready at its head SHA
And Ada opens `GET /builds/9` at the desktop viewport
When Ada presses `Tab` through the page
Then `#submit-to-catalog-button` has the `disabled` attribute and is never `document.activeElement`
And `#submit-to-catalog-button` is matched by `button:disabled` and is not matched by the interactive-control selector
And its accessible name is exactly `Submit to catalog`
And its accessible state includes `disabled=true` in the accessibility tree

### Covered requirements (traceability)
- FR-130

### Out of scope

Screen-reader announcements (BSB-38-PENDING-5); visible focus styling (BSB-38-PENDING-2); form
label and error association (BSB-38-PENDING-4); the platform's hosted Cognito sign-in page;
browser chrome, operating-system keyboard settings and pointing-device input; command-line output;
and any change to what a control does, which the owning epic fixes.

### Notes / dependencies

The 8 surfaces and their regions are fixed in the contract above. The skip link is a new
presentation element this story requires on every surface; it changes no route or action. File
saving is FR-162 (epic BSB-21); run start is FR-037 (epic BSB-24); integration saving is FR-029 to
FR-036 (epic BSB-23); the disabled Submit control is FR-107 (epic BSB-36). BSB-33 has no stories
yet; its run page and diff viewer are FR-094 to FR-101, and this story fixes only their keyboard
behaviour, not their content.

## STORY: BSB-38-PENDING-2

**Summary:** Show a visible focus indicator on every focused control on every surface
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-17, MVP

### Story
As a **keyboard user**, I want **every focused control to show a clearly visible focus indicator**, so that **I can tell which control will act before I press a key**.

### Acceptance Criteria

#### Scenario: Every focused control shows the exact focus ring
Given Ada has a valid member session and every surface fixture in the surface inventory is seeded
And each of the 8 surfaces is opened at the desktop viewport
When Ada focuses each element matching the interactive-control selector by pressing `Tab`, then moves focus away and presses `Shift+Tab` back onto it
Then for every focused element the computed `outline-width` is `3px`
And the computed `outline-style` is `solid`
And the computed `outline-color` is `rgb(11, 87, 208)`
And the computed `outline-offset` is `2px`
And the computed `border-radius` is `2px`
And removing every `box-shadow` declaration from the page does not remove the outline

#### Scenario: Focus rings meet non-text contrast in every state
Given Ada has a valid member session and the builds list, run-start page and build page are open at the desktop viewport
When Ada focuses a control that sits on the page background `#FFFFFF`, then one that sits on a card or table surface `#F3F4F6`
Then the focus ring's contrast against `#FFFFFF` is `6.39:1`
And the focus ring's contrast against `#F3F4F6` is `5.80:1`
And each of those two ratios is at least `3:1`

#### Scenario: The ring is never clipped or covered
Given Ada has a valid member session and run `1` exists with a log long enough to scroll and a diff whose first line is the added line `+New content`
And Ada opens `GET /projects/7/runs/1` at the desktop viewport
When Ada focuses each control inside `#run-log` and `#run-diff`
Then the focused control is scrolled so that its top is at least `24px` below the top of the viewport and its bottom is at least `24px` above the bottom of the viewport
And all four outline edges lie inside the viewport rectangle
And no outline edge intersects the rectangle of any element with `position: sticky` or `position: fixed`
And the same checks pass on `#file-content` and `#save-file` on `GET /builds/7/files`

#### Scenario: Hover and focus combine without losing the ring
Given Ada has a valid member session and the builds list is open at the desktop viewport
When Ada focuses `#build-skill` by pressing `Tab` and then moves the pointer over it
Then the computed `outline-width` is still `3px` and the computed `outline-color` is still `rgb(11, 87, 208)`
And the effective background is `#F3F4F6`
And the computed `color` is `#1F2328` and its contrast against `#F3F4F6` is `14.35:1`
And no `:hover` or `:active` rule sets `outline: none` or `outline: 0` on any control on any surface

#### Scenario: The indicator survives forced-colours mode
Given Ada has a valid member session and the run-start page is open at the desktop viewport with `forced-colors: active` emulated
When Ada focuses each control in the interactive-control selector by pressing `Tab`
Then the computed `outline-width` is still `3px`
And the computed `outline-style` is still `solid`
And the computed `outline-color` is `Highlight`
And no focused control has an effective indicator drawn only with `background-color` or `box-shadow`

### Covered requirements (traceability)
- FR-131

### Out of scope

Keyboard reachability and activation (BSB-38-PENDING-1); announcements (BSB-38-PENDING-5); text
contrast (BSB-38-PENDING-7); focus indicators on the platform's hosted sign-in page; focus
management for browser dialogs; and any focus animation or transition, which is not required.

### Notes / dependencies

The token `--sb-focus-ring` and the exact computed values are fixed in the contract above. FR-131
is a PRD-added requirement (PRD §8), not an ADR-given value. The focus ring is tested on the
surfaces other epics own; this story adds no route, control or action. The run page's diff viewer
is FR-100 (epic BSB-33), which has no stories yet; this story fixes only its focus behaviour.

## STORY: BSB-38-PENDING-3

**Summary:** Expose the name, role and state of every custom status component
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As a **screen-reader user**, I want **every custom status component on every surface to expose its name, role and state**, so that **I learn the same status a sighted user sees instead of hearing an unlabelled graphic or nothing at all**.

### Acceptance Criteria

#### Scenario: Build-page status components expose their roles and names
Given Ada has a valid member session and build `7` is open at the desktop viewport
When Ada opens `GET /builds/7` and reads the accessibility tree
Then `#build-state` has role `img` and accessible name `State: Open`
And `#pull-request-state` has role `img` and accessible name `Pull request: None`
And `#readiness-manifest` has role `img` and accessible name `Manifest: Passed`
And `#readiness-run` has role `img` and accessible name `Run: Passed`
And `#readiness-static` has role `img` and accessible name `Static scan: Passed`
And `#readiness-llm` has role `img` and accessible name `LLM scan: Complete`
And `#readiness-checks` has role `region` and accessible name `Readiness checks`
And `#static-scan-score` has role `img` and accessible name `Score: 100/100`
And `#static-scan-recommendation` has role `img` and accessible name `Recommendation: INSTALL`
And `#llm-scan-state` has role `img` and accessible name `LLM scan: Complete`
And every decorative icon inside those components has `aria-hidden="true"`

#### Scenario: Scan error components expose alert semantics
Given Ada has a valid member session and build `7` has static scan `19` and LLM scan `54`
When Ada opens `GET /builds/7` and reads the accessibility tree
Then `#static-scan-error` has role `alert` and accessible name `Static scan error`
And its text content is exactly `scan_timeout`
And `#llm-scan-error` has role `alert` and accessible name `LLM scan error`
And its text content is exactly `llm_model_profile_missing`

#### Scenario: History and compare verdicts expose the verdict as their name
Given Ada has a valid member session and runs `1` and `2` exist
When Ada opens `GET /skills/sdlc-fix-bug-triage/history` and `GET /runs/compare?left=1&right=2` and reads the accessibility tree
Then `#run-1-verdict` has role `cell` and accessible name `completed`
And `#run-2-verdict` has role `cell` and accessible name `changes_requested`
And `#left-verdict` has role `cell` and accessible name `completed`
And `#right-verdict` has role `cell` and accessible name `changes_requested`
And `#compare-flips` has role `region` and accessible name `Checks that flipped`

#### Scenario: The run page exposes outcome, progress, log and diff semantics
Given Ada has a valid member session and run `1` exists with the run 1 log object and a diff whose first line is the added line `+New content`
And run `1` has `final_verdict` = `completed`
When Ada opens `GET /projects/7/runs/1` and reads the accessibility tree
Then `#run-outcome` has role `img` and accessible name `Outcome: completed`
And `#run-final-verdict` has role `img` and accessible name `Final verdict: completed`
And when Ada opens `GET /projects/7/runs/3` instead, `#run-progress` has role `progressbar`, accessible name `Run progress`, `aria-valuemin` = `0`, `aria-valuemax` = `100`, `aria-valuenow` = `40` and `aria-valuetext` = `Running step triage — Reading issue LEARN-87 (40%)`
And `#run-log` has role `log` and accessible name `Run log`
And `#run-diff` has role `table` and accessible name `Diff: main to skilltest/1`
And the diff's first line has role `row` and its first cell has role `cell` and accessible name `Added`
And the diff's second line has role `row` and its first cell has role `cell` and accessible name `Removed`

#### Scenario: A truncated log exposes its truncation state
Given Ada has a valid member session and run `1` exists with a log of `12582912` bytes and the builder's log capture limit is `10485760` bytes
When the builder stores the truncated log and Ada opens `GET /projects/7/runs/1` and reads the accessibility tree
Then `#run-log` has role `log`, accessible name `Run log` and `aria-describedby="run-log-truncation"`
And `#run-log-truncation` has the exact text `[skill-builder] log truncated: showing the last 10485760 bytes of 12582912 bytes; 2097152 earlier bytes discarded.`
And with the complete three-line log from the fixture, `#run-log` has no `aria-describedby` attribute and no element with id `run-log-truncation` exists

#### Scenario: An unknown status value is exposed instead of rendering an empty component
Given Ada has a valid member session and build `7` has a `builds.state` value of `mystery` outside the four defined values
When Ada opens `GET /builds/7` and reads the accessibility tree
Then `#build-state` has role `img` and accessible name `Unknown status: mystery`
And `#build-state`'s visible text is exactly `Unknown status: mystery`
And the page contains no element with role `img` whose accessible name is empty

### Covered requirements (traceability)
- FR-132

### Out of scope

Visible focus (BSB-38-PENDING-2); form-field semantics (BSB-38-PENDING-4); live announcements
(BSB-38-PENDING-5); colour independence (BSB-38-PENDING-6); the platform's hosted sign-in page;
the content or wording of the statuses, which their owning epics fix; and screen-reader-specific
verbosity settings.

### Notes / dependencies

The exact status text is taken from the epics that render each surface: build state and pull-request
state from BSB-36, readiness labels from BSB-30, scan state and recommendation from BSB-31 and
BSB-32, run outcome from BSB-26, final verdict from BSB-29 and BSB-33, history and compare verdicts
from BSB-35. The ids of the run-page report regions are FR-094 to
FR-101 (epic BSB-33); BSB-33 has no stories yet, so this story fixes only their accessible
semantics. `role="img"` is used for a static status badge; `role="status"` is reserved for the live
announcers in BSB-38-PENDING-5.

## STORY: BSB-38-PENDING-4

**Summary:** Expose every form field's label, instructions and error to assistive technology
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As a **screen-reader user**, I want **every form field to expose its label, instructions and validation error**, so that **I can complete each builder form correctly and fix a rejected field without guessing what went wrong**.

### Acceptance Criteria

#### Scenario: The builds list and file editor fields expose labels and instructions
Given Ada has a valid member session and the builds list and file editor fixtures are seeded
When Ada opens `GET /builds`, sets `#build-kind` to `clone`, and reads the accessibility tree
Then `#build-kind`, `#build-skill`, `#build-source` and `#build-description` each have an accessible name and description exactly matching the form-field contract
And `#build-kind` and `#build-skill` have `required` and `aria-required="true"`
And when Ada sets `#build-kind` to `clone`, `#build-source` has `required` and `aria-required="true"`, and when the kind is set to `create`, `#build-source` has neither
And `#build-description` has neither `required` nor `aria-required`
And each control's `aria-describedby` names only its help element
And when Ada opens `GET /builds/7/files`, `#file-path` and `#file-content` have accessible names `File path` and `File content`, descriptions exactly `A file inside the skill folder.` and `The full contents of the selected file.`, and both are required

#### Scenario: The run-start fields expose labels and instructions
Given Ada has a valid member session and project `7` has its integrations
When Ada opens `GET /projects/7/runs/new` and reads the accessibility tree
Then `#skill`, `#skills-branch`, `#input-branch`, `#context`, `#model-profile`, `#tier`, `#reviewer-feedback` and `#upstream-handoff` each have an accessible name and description exactly matching the form-field contract
And `#skill`, `#skills-branch`, `#input-branch`, `#model-profile` and `#tier` have `required` and `aria-required="true"`
And `#context`, `#reviewer-feedback` and `#upstream-handoff` have neither `required` nor `aria-required`
And the `#context` description is exactly `Context must be a JSON object with optional keys workflow, step, reviewer_feedback and upstream_handoff.`

#### Scenario: The project settings fields expose labels and instructions
Given Ada has a valid member session and project `7` has its integrations
When Ada opens `GET /projects/7/settings` and reads the accessibility tree
Then `#project-name`, `#jira-site-url`, `#jira-project-key`, `#jira-mcp`, `#github-repo`, `#github-base-branch`, `#github-mcp` and `#ai-model-profiles` each have an accessible name and description exactly matching the form-field contract
And the required settings controls are `#project-name`, `#jira-site-url`, `#jira-project-key`, `#github-repo`, `#github-base-branch` and `#ai-model-profiles`, and each has `required` and `aria-required="true"`
And `#jira-mcp` and `#github-mcp` have neither `required` nor `aria-required`

#### Scenario: A validation error is associated with its field and focused error summary
Given Ada has a valid member session and the run-start fixture is seeded
And the `runs` table has exactly four rows: runs `1`, `2`, `3` and `7`
When Ada submits the run-start form with `#skill` empty and every other field valid
Then the response contains `<div id="form-errors" role="alert" tabindex="-1">`
And `#form-errors` contains an `h2` whose text is exactly `There is a problem`
And `#form-errors` contains a link whose text is exactly `A skill is required.` and whose `href` is `#skill`
And `document.activeElement` is `#form-errors`
And `#skill` has `aria-invalid="true"` and `aria-describedby="skill-help skill-error"`
And `#skill-error` has the exact text `A skill is required.`
And the accessible description of `#skill` is exactly `The skill to test. A skill is required.`
And `SELECT count(*) FROM runs` returns `4`

#### Scenario: A corrected field loses its invalid state and error
Given Ada has a valid member session and the run-start form has just been rejected with an empty `#skill`
When Ada selects `sdlc-fix-bug-triage` in `#skill`, sets `#skills-branch` to `build/sdlc-fix-bug-triage`, sets `#input-branch` to `main`, sets `#model-profile` to `3`, sets `#tier` to `high`, leaves `#context` empty and resubmits
Then the builder responds with HTTP 201 and `SELECT count(*) FROM runs` returns `5`
And `SELECT count(*) FROM runs WHERE project_id = 7 AND user_id = 42 AND skill = 'sdlc-fix-bug-triage' AND input_branch = 'main' AND state = 'queued'` returns `1`
And `#skill` has no `aria-invalid` attribute or has `aria-invalid="false"`
And no element with id `skill-error` exists in the rendered form
And `#skill`'s `aria-describedby` is exactly `skill-help`
And no `aria-describedby` on any control names an element that does not exist

#### Scenario: A field that breaks its format rule exposes its exact error
Given Ada has a valid member session and the builds list is open
And the `builds` table has no row with `skill` = `BugTriage`
When Ada submits the build form with `#build-kind` = `create`, `#build-skill` = `BugTriage` and `#build-description` = `A triage skill`
Then the page contains `<div id="form-errors" role="alert" tabindex="-1">` with a link whose text is exactly `Skill name must follow sdlc-<area>-<action> using lowercase letters, digits and hyphens.`
And `#build-skill` has `aria-invalid="true"` and `aria-describedby="build-skill-help build-skill-error"`
And `#build-skill-error` has the exact text `Skill name must follow sdlc-<area>-<action> using lowercase letters, digits and hyphens.`
And `SELECT count(*) FROM builds WHERE skill = 'BugTriage'` returns `0`

### Covered requirements (traceability)
- FR-133

### Out of scope

Keyboard operation (BSB-38-PENDING-1); focus styling (BSB-38-PENDING-2); status semantics
(BSB-38-PENDING-3); announcements (BSB-38-PENDING-5); the platform's hosted sign-in page; native
browser validation bubbles; the validation rules and messages themselves, which the owning epics
fix; and client-side-only validation that duplicates a server rule.

### Notes / dependencies

The field inventory, exact labels, help texts and error texts are fixed in the contract above. The
run-start validation messages are epic BSB-24's; the build name rule is epic BSB-19's; the project
name rule is epic BSB-22's; the file editor fields are
FR-127 and FR-162 (epic BSB-21). BSB-19, BSB-21 and BSB-23 have no stories yet; their forms are
created by FR-006 to FR-017, FR-029 to FR-036 and FR-127. This story adds accessibility attributes
and error association only; it adds no field and changes no validation rule.

## STORY: BSB-38-PENDING-5

**Summary:** Announce run progress and readiness changes to assistive technology
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-17, MVP

### Story
As a **screen-reader user**, I want **run progress and readiness changes to be announced as they happen**, so that **I do not have to poll the page or discover a change only when I navigate back to it**.

### Acceptance Criteria

#### Scenario: The run page announces the first observed progress
Given Ada has a valid member session and run `3` exists with the run 3 progress object
And Ada opens `GET /projects/7/runs/3` at the desktop viewport
When the page's first progress refresh completes
Then `#run-announcer` has `role="status"`, `aria-live="polite"` and `aria-atomic="true"`
And `#run-announcer` has the class `sb-visually-hidden` and is not `display: none`, not `visibility: hidden`, has no `hidden` attribute and has no `aria-hidden="true"`
And `#run-announcer`'s text content is exactly `Run progress: Running step triage — Reading issue LEARN-87 (40%).`
And `#run-progress` has `aria-valuenow` = `40` and `aria-valuetext` = `Running step triage — Reading issue LEARN-87 (40%)`

#### Scenario: A progress change is announced once and an unchanged refresh is silent
Given Ada has a valid member session and run `3` is open with the run 3 progress object
And `#run-announcer`'s text is exactly `Run progress: Running step triage — Reading issue LEARN-87 (40%).`
When `s3://skill-builder-runs/runs/3/progress.json` is replaced with exactly `{"step":"triage","state":"running","message":"Writing bug-triage.md","percent":80,"updated_at":"2026-11-15T10:01:20Z"}`
Then within 2 seconds `#run-announcer`'s text content is exactly `Run progress: Running step triage — Writing bug-triage.md (80%).`
And `#run-progress` has `aria-valuenow` = `80` and `aria-valuetext` = `Running step triage — Writing bug-triage.md (80%)`
And a `MutationObserver` watching `#run-announcer` with `childList`, `characterData` and `subtree` records exactly one mutation batch for that change
And when the same progress object is refreshed five more times, the observer records no further mutations and the text remains exactly `Run progress: Running step triage — Writing bug-triage.md (80%).`

#### Scenario: A run's terminal outcome is announced
Given Ada has a valid member session and run `3` is open with the run 3 progress object
When `SELECT state FROM runs WHERE id = 3` changes to `completed` and the next refresh completes
Then within 2 seconds `#run-announcer`'s text content is exactly `Run finished: completed.`
And when the same fixture is re-run with run `7` in `failed_infra` and `#run-announcer` rendered from that page, the text content is exactly `Run failed: The runtime could not be started.`
And when a running run has no progress object, the text content is exactly `Run progress: Waiting for the skill to report progress.`

#### Scenario: A readiness change is announced within the build page refresh interval
Given Ada has a valid member session and build `9` is open at the desktop viewport
And `GET /api/builds/9/readiness` initially returns `{"build_id":9,"sha":"5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b","manifest":"passed","run":"not_run","static":"not_run","llm":"not_run","ready":false,"ready_sha":null}`
And `#readiness-announcer`'s text is exactly `Readiness: Not ready. Manifest: Passed. Run: Not run. Static scan: Not run. LLM scan: Not run.`
When the readiness API then returns `{"build_id":9,"sha":"5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b","manifest":"passed","run":"passed","static":"passed","llm":"complete","ready":true,"ready_sha":"5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b"}`
Then within 5 seconds `#readiness-announcer`'s text content is exactly `Readiness changed: Ready. Manifest: Passed. Run: Passed. Static scan: Passed. LLM scan: Complete.`
And `#readiness-announcer` has `role="status"`, `aria-live="polite"` and `aria-atomic="true"`
And when the same ready value is refreshed five more times, a `MutationObserver` records no further mutations in `#readiness-announcer`

#### Scenario: A failed progress refresh never announces stale or false progress
Given Ada has a valid member session and run `3` is open with the run 3 progress object
And `#run-announcer`'s text is exactly `Run progress: Running step triage — Reading issue LEARN-87 (40%).`
When the progress API returns HTTP 500 for two consecutive refreshes
Then `#run-announcer`'s text content is unchanged and no announcement text is added
And `#run-progress` still has `aria-valuenow` = `40` and `aria-valuetext` = `Running step triage — Reading issue LEARN-87 (40%)`
And when the API recovers with exactly `{"step":"triage","state":"running","message":"Writing bug-triage.md","percent":80,"updated_at":"2026-11-15T10:01:20Z"}`, the announcer text becomes exactly `Run progress: Running step triage — Writing bug-triage.md (80%).` once
And the page never contains an announcement whose percent is greater than the latest successful progress object's `percent`

### Covered requirements (traceability)
- FR-134

### Out of scope

Keyboard operation (BSB-38-PENDING-1); status roles and names (BSB-38-PENDING-3); form errors
(BSB-38-PENDING-4); colour independence (BSB-38-PENDING-6); the progress, log and readiness APIs
themselves, which epics BSB-26 and BSB-30 own; browser notification or sound; and announcements for
events other than run progress and readiness.

### Notes / dependencies

The run progress object, log object and their exact sentences are epic BSB-26's. The readiness API
and its values are epic BSB-30's. This story adds two live regions and their text; the refresh
mechanism reads the existing APIs and adds no route or data. Visually hidden is required because a
`display: none` region is not announced. The announcement text is asserted exactly so no wording is
left to implementation.

## STORY: BSB-38-PENDING-6

**Summary:** Convey readiness, verdict and diff status without relying on colour
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-17, MVP

### Story
As a **colour-blind user**, I want **every readiness, verdict, scan and diff status to carry text and a non-colour cue**, so that **I can tell every status apart in any colour perception, in monochrome and in a printed or high-contrast view**.

### Acceptance Criteria

#### Scenario: Readiness and build statuses remain distinct in monochrome
Given Ada has a valid member session and a build page fixture has readiness values `manifest` = `passed`, `run` = `failed`, `static` = `passed` and `llm` = `unavailable`
When Ada opens `GET /builds/7`, applies the monochrome stylesheet from the contract and reads the visible text
Then the visible text of `#readiness-manifest` is exactly `Manifest: Passed`
And the visible text of `#readiness-run` is exactly `Run: Failed`
And the visible text of `#readiness-static` is exactly `Static scan: Passed`
And the visible text of `#readiness-llm` is exactly `LLM scan: Unavailable`
And `#build-state`'s visible text is exactly `State: Open`
And `#pull-request-state`'s visible text is exactly `Pull request: None`
And every pair of those six status texts is different

#### Scenario: Verdicts remain distinct in monochrome
Given Ada has a valid member session and runs `1` and `2` exist with `final_verdict` = `completed` and `changes_requested`
When Ada opens `GET /skills/sdlc-fix-bug-triage/history` and `GET /runs/compare?left=1&right=2` with the monochrome stylesheet applied
Then the visible text of `#run-1-verdict` is exactly `completed`
And the visible text of `#run-2-verdict` is exactly `changes_requested`
And the visible text of `#left-verdict` is exactly `completed`
And the visible text of `#right-verdict` is exactly `changes_requested`
And no verdict cell's visible text is empty
And no verdict cell sets its text with a pseudo-element alone

#### Scenario: Diff line status is carried by a prefix and a status label
Given Ada has a valid member session and run `1` has a diff whose first line is the added line `+New content`, whose second line is the removed line `-Old content` and whose third line is the unchanged line ` Same content`
When Ada opens `GET /projects/7/runs/1` with the monochrome stylesheet applied and reads the diff
Then the first line's visible text begins with the exact prefix `+ `
And its first cell's visible text is exactly `Added`
And the second line's visible text begins with the exact prefix `- `
And its first cell's visible text is exactly `Removed`
And the third line's visible text begins with two spaces
And its first cell's visible text is exactly `Unchanged`
And the three status labels `Added`, `Removed` and `Unchanged` are pairwise different
And no diff line distinguishes added from removed using background colour alone

#### Scenario: Scan and log statuses carry text, and an unknown value is named
Given Ada has a valid member session and build `7` has static scan `12` and LLM scan `51`
And run `1` exists with a log of `12582912` bytes
When Ada opens `GET /builds/7` and `GET /projects/7/runs/1` with the monochrome stylesheet applied
Then the visible text of `#static-scan-score` is exactly `Score: 100/100`
And the visible text of `#static-scan-recommendation` is exactly `Recommendation: INSTALL`
And the visible text of `#llm-scan-state` is exactly `LLM scan: Complete`
And `#run-log`'s visible text begins with the exact log truncation marker from the contract
And when `builds.state` is `mystery`, the visible text of `#build-state` is exactly `Unknown status: mystery`
And no status in this scenario is rendered as an empty element, a colour swatch or an icon without its text

### Covered requirements (traceability)
- FR-135

### Out of scope

Contrast ratios (BSB-38-PENDING-7); programmatic roles and names (BSB-38-PENDING-3); announcements
(BSB-38-PENDING-5); the platform's hosted sign-in page; colour-vision simulation of a specific
deficiency, since the monochrome check is stricter; and choosing which redundant colour to use.

### Notes / dependencies

The exact visible text values are fixed in the contract and are the text the owning epics already
render: readiness from BSB-30, scans from BSB-31 and BSB-32, verdicts from BSB-29 and BSB-35,
build and pull-request state from BSB-36, and the log truncation marker from
BSB-26. This story does not require a particular icon or glyph; text is the non-colour channel. The
diff viewer is FR-100 (epic BSB-33), which has no stories yet.

## STORY: BSB-38-PENDING-7

**Summary:** Meet WCAG 2.1 AA contrast for text and status colours in normal, hover and focus states
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-17, MVP

### Story
As a **low-vision user**, I want **text and status colours to meet WCAG 2.1 AA contrast in normal, hover and focus states**, so that **I can read every label, value and control state without relying on magnification or a high-contrast override**.

### Acceptance Criteria

#### Scenario: Every normal-state text pair meets its contrast minimum
Given Ada has a valid member session and each of the 8 surfaces is open at the desktop viewport
When the palette validator computes the WCAG 2.1 contrast ratio for every token pair in the contract's normal-state table
Then `--sb-text` on `--sb-bg` is `15.80:1` and at least `4.5:1`
And `--sb-text-muted` on `--sb-bg` is `6.39:1` and at least `4.5:1`
And `--sb-link` on `--sb-bg` is `6.39:1` and at least `4.5:1`
And `--sb-button-primary-text` on `--sb-button-primary-bg` is `6.39:1` and at least `4.5:1`
And no visible text element on any surface has an effective foreground and background pair below `4.5:1` when its computed font size is below `24px` and its computed font weight is below `700`
And no visible text element with a computed font size of at least `24px`, or at least `18.66px` at weight `700` or heavier, has a pair below `3:1`

#### Scenario: Every hover-state pair meets its contrast minimum
Given Ada has a valid member session and the builds list, run-start page and file editor are open at the desktop viewport
When Ada hovers every control in the interactive-control selector on those surfaces
Then each hovered control that has no filled-button rule has effective background `--sb-surface` `#F3F4F6`
And `--sb-text` on `--sb-surface` is `14.35:1` and at least `4.5:1`
And `--sb-text-muted` on `--sb-surface` is `5.81:1` and at least `4.5:1`
And a primary button's hover background `#0842A0` with `--sb-button-primary-text` `#FFFFFF` is `9.14:1` and at least `4.5:1`
And no `:hover` rule changes a text or background pair below its minimum

#### Scenario: Every focus-state pair and focus ring meets its minimum
Given Ada has a valid member session and each of the 8 surfaces is open at the desktop viewport
When Ada focuses every control in the interactive-control selector by pressing `Tab`
Then every focused control's focus ring is drawn entirely outside the control, in the `2px` `outline-offset` gap, on the effective background of the surface that contains the control
And no focused control's focus ring overlaps the control's own fill
And `--sb-focus-ring` `#0B57D0` on `--sb-bg` `#FFFFFF` is `6.39:1` and on `--sb-surface` `#F3F4F6` is `5.80:1`, each at least `3:1`

#### Scenario: Every status badge pair meets its contrast minimum
Given the palette validator reads the status token pairs from the contract's status rows
When the palette validator computes each status token pair
Then `--sb-status-pass-text` on `--sb-status-pass-bg` is `6.51:1`
And `--sb-status-fail-text` on `--sb-status-fail-bg` is `6.73:1`
And `--sb-status-warn-text` on `--sb-status-warn-bg` is `6.63:1`
And `--sb-status-neutral-text` on `--sb-status-neutral-bg` is `7.71:1`
And every one of those ratios is at least `4.5:1`
And no status text colour is set with an alpha channel or inherited from a parent whose effective background differs from the badge background

#### Scenario: A token below the minimum is rejected with its measured ratio
Given the palette validator is run over a candidate token set that adds `#999999` as a normal-text colour on `#FFFFFF`
When the validator computes that pair
Then the computed ratio is exactly `2.85:1`
And the validator exits non-zero with the exact message `Contrast 2.85:1 is below the 4.5:1 minimum for normal text (#999999 on #FFFFFF).`
And the validator does not silently round the value up to `3:1` or treat the pair as large text
And no surface renders normal text using `#999999` on `#FFFFFF` after the rejection

### Covered requirements (traceability)
- FR-136

### Out of scope

Colour-blind distinction without text (BSB-38-PENDING-6); focus-ring geometry (BSB-38-PENDING-2);
automated axe contrast checks (BSB-38-PENDING-8); the platform's hosted sign-in page; disabled
controls and logos, which WCAG 2.1 AA exempts; user-supplied colours; and print stylesheets.

### Notes / dependencies

The token names, values, thresholds and computed ratios are fixed in the contract above. FR-136 is
a PRD-added requirement (PRD §8); the ADR gives no colour values, so this decomposition pins a
compliant palette. The palette validator is a unit test in the builder app's test suite; the
automated axe gate in BSB-38-PENDING-8 catches rendered contrast regressions that a token test
cannot. The effective-background walk is defined so a test never guesses through transparency.

## STORY: BSB-38-PENDING-8

**Summary:** Run automated accessibility checks on every builder change in continuous verification
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As a **skill author**, I want **automated accessibility checks to run on every builder change**, so that **an accessibility regression is caught before merge instead of after a release**.

### Acceptance Criteria

#### Scenario: A clean change passes with a complete report
Given a pull request changes `skill-builder/app/templates/builds.html`
And every surface fixture is seeded and every route in the surface inventory returns HTTP 200
When the `.github/workflows/skill-builder-a11y.yml` job `a11y` runs
Then all 8 routes are visited at the desktop and reflow viewports, producing exactly 16 route checks
And axe runs with tags `wcag2a`, `wcag2aa`, `wcag21a` and `wcag21aa` and with no rule disabled
And the job exits with status `0`
And the job's stdout contains exactly one summary line `a11y: 16 checks, 0 critical, 0 serious`
And `a11y-report.json` has `summary` exactly `{"routes":8,"viewports":2,"checks":16,"critical":0,"serious":0}`
And every element of `checks` has `status` = `200` and `violations` = `[]`
And the artifact `skill-builder-a11y-report` is uploaded and contains `a11y-report.json`

#### Scenario: A missing accessible name fails the job with the route and rule
Given a pull request adds `<button id="mystery"></button>` to `skill-builder/app/templates/builds.html`
And every fixture and route is otherwise unchanged
When the `a11y` job runs
Then axe reports violation id `button-name` with impact `critical` on route `/builds` at viewport `1280x800`
And the job exits with status `1`
And the job prints the annotation `::error file=skill-builder/app/templates/builds.html,line=42::button-name (critical) on /builds`
And the summary line is exactly `a11y: 16 checks, 1 critical, 0 serious`
And the report's `/builds` entry at viewport `1280x800` has a violation whose `id` is `button-name`, whose `impact` is `critical` and whose `nodes[0].target` contains `#mystery`

#### Scenario: An unreachable route fails instead of being skipped
Given the `/builds/7` route returns HTTP 500 for Ada's valid member session
And every other route and fixture is unchanged
When the `a11y` job runs
Then the job exits with status `1`
And the job prints the exact message `a11y_route_unreachable: /builds/7 returned 500`
And the report's entry for `/builds/7` has `status` = `500` and no result is recorded as a pass for that route
And the job does not report `a11y: 16 checks, 0 critical, 0 serious`

#### Scenario: A short suite fails instead of passing vacuously
Given the route list in `surfaces.spec.ts` omits `/runs/compare`
And every route it does list returns HTTP 200
When the `a11y` job runs
Then the job exits with status `1`
And the job prints the exact message `a11y_route_count: expected 16 route checks, got 14`
And the report contains exactly 18 elements in `checks`
And the job does not upload a report whose `summary.checks` is greater than the number of elements in `checks`

#### Scenario: The check runs continuously on the builder paths only
Given a pull request changes only `docs/product/PRD.md`
When the workflow trigger is evaluated
Then the `a11y` job is not scheduled
And given a pull request changes `skill-builder/app/templates/run.html`, the `a11y` job is scheduled
And given a push to `main` changes `skill-builder/app/services/runs.py`, the `a11y` job is scheduled
And given a pull request changes only `skills/sdlc-fix-bug-triage/SKILL.md`, the `a11y` job is not scheduled

### Covered requirements (traceability)
- FR-137

### Out of scope

Fixing the violations the check reports, which the owning surface's epic or this epic's other
stories do; unit contrast-token validation (BSB-38-PENDING-7); manual assistive-technology testing;
the `skills/` catalog CI, which builds skills rather than the builder app; the platform's hosted
sign-in page; and load, performance or security scanning.

### Notes / dependencies

The workflow path, job name, tool versions, route list, thresholds, exact messages and report shape
are fixed in the contract above. The builder app lives at `skill-builder/app` per ADR SK-001 §1. The
`a11y` job is separate from the catalog's `.github/workflows/ci.yml`, which runs tier 1 and tier 2
on the skills tree and never builds the builder app. FR-137 is a PRD-added requirement (PRD §8).
The exact `a11y_route_unreachable` and `a11y_route_count` messages make a silent or partial run a
failure, not a pass.

## STORY: BSB-38-PENDING-9

**Summary:** Reflow every builder surface to 320 CSS pixels without two-dimensional scrolling
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As a **low-vision user who reads at high zoom or on a narrow screen**, I want **every builder surface to reflow to a 320 CSS-pixel viewport without two-dimensional scrolling**, so that **I can read and operate the page by scrolling in one direction only**.

### Acceptance Criteria

#### Scenario: Every surface fits the reflow viewport with no horizontal scrolling
Given Ada has a valid member session and every surface fixture in the surface inventory is seeded
And every route returns HTTP 200
When each of the 8 surfaces is opened at the reflow viewport of `320` by `256` CSS pixels
Then `window.innerWidth` is exactly `320`
And `document.documentElement.scrollWidth` is less than or equal to `320`
And `document.documentElement.scrollWidth` is less than or equal to `document.documentElement.clientWidth`
And no element with a visible box has a `getBoundingClientRect().right` value greater than `320`
And no element has computed `overflow-x` equal to `auto` or `scroll` while its `scrollWidth` is greater than its `clientWidth`, except a textarea that wraps its own content
And Ada can reach the last piece of content by scrolling vertically only

#### Scenario: Long unbroken strings wrap instead of widening the page
Given Ada has a valid member session and build `7` has head SHA `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`
And run `1` links to the 120-character trace URL `https://langfuse.skillbuilder.internal/project/skill-builder/traces/run-1`
When Ada opens `GET /builds/7`, `GET /skills/sdlc-fix-bug-triage/history` and `GET /projects/7/runs/1` at the reflow viewport
Then each page's `document.documentElement.scrollWidth` is less than or equal to `320`
And the 40-character SHA is wrapped within its cell on the build page and on the history page
And the 120-character trace URL is wrapped within its link
And the SHA and the trace URL are each still fully present in their page's text content

#### Scenario: The log stream and diff viewer wrap and scroll vertically only
Given Ada has a valid member session and run `1` exists with a log whose first line is the ASCII character `a` repeated 400 times and a diff whose first line is the added line `+New content` and whose second line is the removed line `-Old content`
When Ada opens `GET /projects/7/runs/1` at the reflow viewport
Then `#run-log` has computed `white-space` = `pre-wrap` and computed `overflow-wrap` = `anywhere`
And `#run-diff` has computed `white-space` = `pre-wrap` and computed `overflow-wrap` = `anywhere`
And `#run-log`'s `scrollWidth` is less than or equal to its `clientWidth`
And `#run-diff`'s `scrollWidth` is less than or equal to its `clientWidth`
And `#run-log`'s `scrollHeight` is greater than its `clientHeight`
And the full 400-character log line is present in `#run-log`'s text content
And no element inside `#run-log` or `#run-diff` has a `getBoundingClientRect().right` value greater than `320`

#### Scenario: Data tables reflow to labelled blocks at the narrow width
Given Ada has a valid member session and the history, compare, readiness and scan fixtures are seeded
And the `data-label` value of every table cell equals its column's header text
When Ada opens `GET /skills/sdlc-fix-bug-triage/history`, `GET /runs/compare?left=1&right=2` and `GET /builds/7` at the reflow viewport
Then each table's rows have computed `display` = `block` at a viewport width of `480` CSS pixels or less
And each cell has computed `display` = `block`
And each cell's `::before` pseudo-element content includes its `data-label` value
And each surface's `document.documentElement.scrollWidth` is less than or equal to `320`
And the text of every cell in the desktop rendering is still present at the reflow rendering
And no table cell's text is clipped by `overflow: hidden` or an ellipsis whose full value is unavailable

#### Scenario: The file editor fits and an empty history page does not overflow
Given Ada has a valid member session and the file `SKILL.md` in build `7` contains a line that is the ASCII character `y` repeated 300 times
And the skill `sdlc-fix-bug-missing` has no runs
When Ada opens `GET /builds/7/files` and `GET /skills/sdlc-fix-bug-missing/history` at the reflow viewport
Then on the file editor, `#file-content`'s `scrollWidth` is less than or equal to its `clientWidth`, `#file-content`'s `getBoundingClientRect().right` is less than or equal to `320`, `#save-file` is visible and focusable, and the page's `document.documentElement.scrollWidth` is less than or equal to `320`
And the textarea has `wrap="soft"` and the full 300-character line remains in its value
And on the empty history page, the visible text is exactly `No runs for this skill.` and `document.documentElement.scrollWidth` is less than or equal to `320`
And no page in this scenario has a horizontal scrollbar

### Covered requirements (traceability)
- NFR-012

### Out of scope

Reflow below `320` CSS pixels; text-only zoom at `200%` beyond the reflow viewport; WCAG 1.4.4
resize-text testing beyond the token sizes in BSB-38-PENDING-7; content that is inherently
two-dimensional by nature, which this epic does not exempt because NFR-012 states no exception;
the platform's hosted sign-in page; and print or PDF layouts.

### Notes / dependencies

The reflow viewport, measurement, wrapping and table rules are fixed in the contract above. NFR-012
is a PRD-added requirement (PRD §8) and the `320` CSS-pixel value is a PRD-added value, not an
ADR-given one. The surfaces are the same 8 as every other story: the builds list and create form
(FR-006 to FR-017), build page, file editor (FR-127 and FR-162), run start (FR-037), run page and
diff viewer (FR-094 to FR-101), project settings (FR-029 to FR-036), and history and compare
(FR-104 to FR-106). The Later-release suites and nightly schedule (FR-119 to FR-123) are excluded
from the MVP inventory and inherit this rule when delivered. BSB-19, BSB-21, BSB-23 and BSB-33 have
no stories yet; this story fixes only their reflow behaviour, not their content.
