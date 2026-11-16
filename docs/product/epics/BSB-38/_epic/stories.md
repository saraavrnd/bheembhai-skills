# Stories — BSB-38 (Accessibility conformance)

Epic BSB-38 covers FR-130, FR-131, FR-132, FR-133, FR-134, FR-135, FR-136, FR-137 and NFR-012.
It is decomposed into 7 vertical slices below, and coverage of all nine requirements is verified.

The slices are the accessibility work as each author experiences it: a keyboard-only author
operates every control and always sees where focus is (PENDING-1); a screen-reader author reads
every custom status — readiness, run outcome, verdict, scan verdict, build state and credential
verification — by name, role and state, and status is never carried by colour alone (PENDING-2);
every form field exposes its label, instructions and error message (PENDING-3); run progress and
readiness changes are announced as they happen (PENDING-4); a low-vision author reads all text and
status colours at WCAG 2.1 AA contrast in normal and hover/focus states (PENDING-5); every surface
reflows to a 320 CSS-pixel viewport without horizontal scrolling (PENDING-6); and automated
accessibility checks run in continuous verification and block a critical regression (PENDING-7).

This is a cross-cutting epic: it adds no product capability of its own. Each story constrains
surfaces built by other epics, so every scenario names the surface, its route and the fixture state
it audits in the **audited surface set** below. The owning requirement exists in its epic even
where that epic's stories are written later in the fan-out (BSB-21, BSB-29 and BSB-30 have no
stories yet when this file is written in the same fan-out; their requirements FR-020, FR-021,
FR-063 and FR-070 pre-date this epic).

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than a Jira issue: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404
"Issue does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The
Atlassian MCP server is configured in `.mcp.json`, but this session exposed no Atlassian MCP tools
(the tool list contains no Jira/Atlassian tool), so the configured site was queried read-only
through its REST API. The epic being decomposed is BSB-38, read read-only from the same site:
summary "Accessibility conformance", type Epic, status To Do, labels FA-17/MVP, and a description
whose functional scope and covered requirements match the BSB-38 section of `epics.md`. The run
context's epic item is BSB-38 (feature area FA-17, release MVP). No Jira write was attempted.

## Audited surface set (MVP)

Every story below audits these surfaces at the state named here. A scenario that says "the audited
surface set" means exactly these thirteen rows; it does not mean every route the builder could ever
render. The set is also the surface registry the continuous check in PENDING-7 renders. Later
surfaces (skill history and run comparison in BSB-35, saved suites in BSB-37) are not built at MVP;
they join this registry when they ship and inherit the same primitives.

| ID | Surface | Route and fixture state | Owning epic |
|---|---|---|---|
| AS-1 | Sign-in | `GET /sign-in` with no `sb_session` cookie, and `GET "/sign-in?error=sign_in_incomplete"` | BSB-18 |
| AS-2 | Account | `GET /account` for signed-in Ada (local `users` id 42) | BSB-18 |
| AS-3 | Builds list | `GET /builds` for Ada with no builds (empty state) and with build 7 listed | BSB-18 |
| AS-4 | Build form | `GET /builds/new`, `GET /builds/new?mode=clone` and `GET /builds/new?mode=edit` for Ada; the catalog tree contains skill `sdlc-plan-training` | BSB-19, BSB-20 |
| AS-5 | Build page | `GET /builds/7`: build 7 with skill `sdlc-fix-bug-reproduce`, branch `build/sdlc-fix-bug-reproduce`, `head_sha` `4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d`, `ready_sha` NULL, state `open`; readiness `Not ready` with checks `Manifest valid: Passed`, `Passing run: Not run`, `Static security check: Passed`, `LLM security check: Unavailable`; editor showing `SKILL.md`; controls `Save`, `Security check (static only)`, `Full security check` and disabled `Submit to catalog` | BSB-21, BSB-30, BSB-31, BSB-32, BSB-36 |
| AS-6 | Projects list and create form | `GET /projects` for Ada (project 7 listed) and for a member with no project (empty state); `GET /projects/new` | BSB-22 |
| AS-7 | Project page and add-member form | `GET /projects/7` with Ada `owner` and Bob `member`; `GET /projects/7/members/new` | BSB-22 |
| AS-8 | Project settings and add-integration form | `GET /projects/7/settings` with "Jira integration 3" `Not verified`, "Source control integration 4" `Verified` and "AI model profile Default" `Verified`; `GET /projects/7/integrations/new` | BSB-23 |
| AS-9 | Run start | `GET /projects/7/runs/new?build=7` for Ada with all choices populated; and the same route with no source-control integration, rendering "No source-control integration is configured for this project." and disabled `Start run` | BSB-22, BSB-24 |
| AS-10 | Run page, live | `GET /projects/7/runs/21`: run 21 state `running`, progress `{"status": "running", "turns": 3, "max_turns": 12, "last_event": "Wrote bugfix.md"}` and log lines "Cloned run branch skilltest/21." and "Wrote bugfix.md"; and the empty live state with neither `runs/21/progress.json` nor `runs/21/agent.log` | BSB-26 |
| AS-11 | Run page, completed | `GET /projects/7/runs/21`: state `completed`, result_status `completed`, claimed_verdict `completed`, final_verdict `pass`, a verification record with four checks, a diff, Jira changes, turn count 12 and trace link "Open trace"; and the variants final_verdict `fail` with overturned `yes`, and final_verdict NULL with verification NULL | BSB-26, BSB-33 |
| AS-12 | Scan report | `GET /scans/11` (completed, verdict `pass`, score 96, recommendation `INSTALL`, no findings), `GET /scans/12` (completed, verdict `fail`, findings `CRITICAL SS-001 SKILL.md:3` and `HIGH SS-101 scripts/run.sh:14`) and `GET /scans/14` (running) | BSB-31, BSB-32 |
| AS-13 | Build page, submission states | `GET /builds/7` Ready at the head SHA with `Submit to catalog` enabled and project selector `Project Atlas (7)`; and `GET /builds/7` state `submitted` with "Build state: Submitted", pull-request link `#42` and disabled `Submit to catalog` with "This build has already been submitted." | BSB-36 |

## Scope decisions (made here because the epic leaves them open, not assumed silently)

- **Conformance is tested on rendered surfaces, not on a component gallery.** The epic's
  implementation guidance says to establish accessible primitives first. These stories keep the
  value vertical: they require the rendered audited surfaces to conform and leave the primitive
  library as an implementation choice. A separate "build the primitives" story would be a
  technical layer with no user-visible outcome.
- **What "programmatic name, role and state" means here.** A custom status is an element with an
  ARIA role, an accessible name identifying the status kind, and the status value in its
  accessible description or value. A native element whose role already carries the state (for
  example `progressbar` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax` and
  `aria-valuetext`) uses that state. The exact role, name and description for each status are
  pinned in PENDING-2's scenarios so a test reads them from the accessibility tree without
  guessing.
- **Focus indicator bar.** WCAG 2.1 AA requires a visible focus indicator (2.4.7) and 3:1
  non-text contrast (1.4.11). This epic fixes the measurable bar: the indicator is at least 2 CSS
  pixels thick and has a contrast ratio of at least 3:1 against the adjacent background in the
  normal theme. Removing an outline without drawing a replacement is a failure.
- **Contrast bar.** Normal text is at least 4.5:1 and large text (at least 24 CSS pixels, or at
  least 18.66 CSS pixels when bold) is at least 3:1 (WCAG 2.1 1.4.3). Status text is normal text:
  it is at least 4.5:1, and a status's non-text cue (dot or border) is at least 3:1 (1.4.11).
  Pairs are measured against the rendered pixel behind the text, not against an assumed
  background.
- **Live-update mechanism.** The server-rendered run page and build page are not otherwise live:
  BSB-26 shows progress on the next request and BSB-36 says its refresh is not a poller. FR-134
  needs a change the assistive technology can observe, so this epic adds two read-only JSON
  projections and a 2-second poll while a value is pending: `GET /projects/7/runs/21/live`
  returning `{"state", "turns", "max_turns", "last_event", "failure_reason"}` and
  `GET /builds/7/live` returning `{"head_sha", "readiness", "checks"}`. They apply the same
  authorization as their page (BSB-22's membership check for the run, BSB-18's gate plus the
  build's access rule for the build), read the same objects and rows, and write nothing. They add
  no product behaviour beyond what FR-045, FR-046 and FR-070 already require.
- **Announcement policy.** Each page has exactly one persistent live region: role `status`, name
  "Live updates", `aria-live="polite"` and `aria-atomic="true"`. Its text is replaced only when
  the underlying values change, one sentence per change. The initial page content is not an
  announcement. Repeated identical polls announce nothing. An unavailable live read is announced
  once as "Live updates unavailable. Retry." and is not repeated.
- **Reflow bar.** At a 320 by 640 CSS-pixel viewport, the document's `scrollWidth` is at most 320
  and no element has horizontal overflow (`scrollWidth` greater than `clientWidth`). Long values
  wrap (`overflow-wrap: anywhere`); the run log and the run report's diff use `white-space:
  pre-wrap` and wrap instead of scrolling sideways. This keeps NFR-012's "without two-dimensional
  scrolling" literal instead of relying on WCAG 1.4.10's exception for content that needs two
  dimensions.
- **Automated check bar.** FR-137's check is a job named `accessibility` in the builder repository's
  `.github/workflows/ci.yml`, run on every `pull_request` and every `push` to `main`. It starts
  the builder against a seeded SQLite fixture database, renders every row of the audited surface
  set in headless Chromium, and runs the pinned axe-core engine with the WCAG 2.1 A and AA rule
  tags. A finding with impact `critical` or `serious` is blocking; `moderate` and `minor` findings
  are recorded in `accessibility-report.json` and do not fail the job. An incomplete run (scanner
  or browser failure) fails closed. These stories do not choose the axe-core version; the
  implementation pins it in the builder repository's tool dependencies and records the version in the
  report.
- **No accessibility certification.** The target is WCAG 2.1 AA on the audited builder surfaces.
  The epic's non-goals stand: surfaces outside the builder, certification claims beyond WCAG 2.1
  AA, and native mobile clients are out of scope.

## Readiness check

- **Actors and state.** Ada, Bob, Carol and the project owner are created by BSB-18 and BSB-22.
  Build 7 is created by BSB-19; project 7 by BSB-22; integrations 3, 4 and 5 by BSB-23; run 21 by
  BSB-24/BSB-26; its verification and verdict by BSB-29; the rendered report and verdict sections
  by BSB-33; scans 11, 12 and 14 by BSB-31/BSB-32; the four readiness checks by BSB-30; the
  submission states by BSB-36. No story below invents
  an actor, entity or state that no requirement creates.
- **Split of prerequisite and usage.** This epic uses surfaces; it creates none of their business
  behaviour. The only routes it introduces are the two read-only live projections above, and their
  prerequisites (the run's progress document and the readiness evaluation) exist in BSB-26 and
  BSB-30.
- **Ambiguities returned upstream: none.** The epic leaves the audited surface breadth, the
  scanner, the focus/contrast numbers and the live mechanism open; those are resolved as scope
  decisions above. It does not leave a prerequisite lifecycle ambiguous.

A requirement is covered by exactly one story:

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-130 — Every interactive control in the builder is operable with a keyboard | BSB-38-PENDING-1 | "Every interactive control on every audited surface is reachable and operable from the keyboard"; "The sign-in, create-build and start-run flows complete with the keyboard alone"; "A disabled action is skipped by Tab and its unavailable state is programmatic"; "The run log and diff regions are keyboard-scrollable" |
| FR-131 — Every interactive control shows a visible focus indicator | BSB-38-PENDING-1 | "Every focused control shows a focus indicator at the measured bar"; "Focus moves in reading order and is never lost or trapped" |
| FR-132 — Every custom status component exposes a programmatic name, role and state | BSB-38-PENDING-2 | "Build readiness and its four checks expose name, role and state"; "Run state, progress and verdicts expose name, role and state"; "Scan, build and credential statuses expose name, role and state"; "An unknown or unavailable status is exposed, never defaulted to a passing state" |
| FR-133 — Every form field exposes its label, instructions and error message | BSB-38-PENDING-3 | "Every field on the create-build form exposes its label, instructions, required state and error"; "Every field on the run-start and integration forms exposes its label, instructions and group"; "The project create and add-member forms expose their labels and errors"; "Submission exposes every error, associates it with its field and focuses the first invalid field"; "A form-level error is exposed as an alert and no field is falsely marked invalid" |
| FR-134 — Run progress and readiness changes are announced to assistive technology | BSB-38-PENDING-4 | "Run state and progress changes are announced once each"; "A failed run is announced with its reason"; "A readiness change is announced on the build page"; "An unavailable live update is announced once and not repeated"; "Announcements never contain credentials and unchanged values announce nothing" |
| FR-135 — Readiness and verdict status are never conveyed by colour alone | BSB-38-PENDING-2 | "Every status carries a visible text label in addition to colour" |
| FR-136 — Text and status colours meet WCAG 2.1 AA contrast in normal and hover or focus states | BSB-38-PENDING-5 | "All normal text meets 4.5:1 and all large text meets 3:1"; "Hover and focus states keep text and the focus indicator at their ratios"; "Every status colour pair meets AA in normal and row-hover states"; "Text over a non-solid background is measured against the rendered pixel"; "A sub-threshold pair is rejected with its measured ratio" |
| FR-137 — Automated accessibility checks run in continuous verification | BSB-38-PENDING-7 | "A clean change passes the accessibility job with zero blocking findings"; "A change that removes a control's accessible name fails the job and names the surface and rule"; "A contrast regression fails the job"; "An incomplete accessibility run fails closed"; "Non-blocking findings are reported without failing the job" |
| NFR-012 — Every builder web surface reflows to a 320 CSS-pixel viewport without two-dimensional scrolling | BSB-38-PENDING-6 | "Every audited surface reflows at 320 by 640 with no horizontal overflow"; "Long values wrap instead of widening the page"; "The run log and diff wrap and remain readable at 320 pixels"; "Every primary action remains visible and reachable at 320 pixels" |

> New stories use draft keys `BSB-38-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-38, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-38-PENDING-1

**Title:** Operate every builder surface with the keyboard and see where focus is
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As an **author who uses only a keyboard**, I want **every control on every audited builder surface to be reachable and operable with the keyboard and to show a visible focus indicator**, so that **I can complete the whole authoring loop — sign in, create and edit a build, start a run, read the report and submit to the catalog — without a mouse**.

### Acceptance Criteria

Scenario: Every interactive control on every audited surface is reachable and operable from the keyboard
Given the thirteen audited surface fixtures AS-1 to AS-13 rendered for Ada or for the unauthenticated visitor as the table names, and a browser in which no pointer is used
When a tester presses Tab repeatedly from the start of each page, then Shift+Tab back to the start, and activates each focused control with its standard key (Enter on a link or button, Space on a button or checkbox, arrow keys on a radio group or select, typing in a text field)
Then on each surface every element that is focusable when the page is used with a pointer is also reachable by Tab, each focused control is the one printed in the page's reading order, each control performs the same action it performs for a pointer, Shift+Tab returns through the same controls in reverse order, and Tab from the last control leaves the page without any control or group trapping focus

Scenario: The sign-in, create-build and start-run flows complete with the keyboard alone
Given AS-1 with no session, AS-4 in create mode for Ada, and AS-9 with all choices populated, and a catalog tree that does not yet contain "sdlc-plan-new-skill"
When the tester presses Tab to "Sign in" on AS-1 and presses Enter, then on AS-4 presses Tab to "Skill name", types "sdlc-plan-new-skill", presses Tab, types "Plan a training session", presses Tab to "Create build" and presses Enter, then on AS-9 presses Tab to "Input branch", selects "test/atlas/bug-42" with the arrow keys, presses Tab to "Start run" and presses Enter
Then the "Sign in" activation sends the browser to the Cognito sign-in URL, the "Create build" activation sends POST "/builds" with skill name "sdlc-plan-new-skill" and description "Plan a training session", the "Start run" activation sends POST "/projects/7/runs" with input_branch "test/atlas/bug-42", and no request requires a pointer action

Scenario: Every focused control shows a focus indicator at the measured bar
Given the audited surface set and the interactive controls "Sign in", "Create build", "Save", "Security check (static only)", "Full security check", "Start run", "Submit to catalog", "Open trace" and every link in the page content
When each control receives keyboard focus in turn
Then each focused control renders a focus indicator that is at least 2 CSS pixels thick and whose colour has a contrast ratio of at least 3:1 against the adjacent background in the normal theme, computed `outline-style` is not `none` and computed `outline-width` is not `0px` unless a replacement indicator with those measurements is drawn, and the indicator is visible while the control is focused and absent after focus moves away

Scenario: Focus moves in reading order and is never lost or trapped
Given AS-5 and AS-13 at `GET /builds/7`, AS-7 at `GET /projects/7`, and AS-12 at `GET /scans/12`
When the tester presses Tab through each page and then presses Shift+Tab from the first control
Then focus visits controls in document reading order (the skip link first where the page has one, then the header, main content and footer), the sequence of Tab stops equals the DOM order of the focusable elements with no stop jumping backwards in the document, Shift+Tab returns through the same stops in reverse order, and Shift+Tab from the first control does not move focus backwards past the page

Scenario: A disabled action is skipped by Tab and its unavailable state is programmatic
Given AS-5 with "Submit to catalog" disabled because build 7 is not Ready, and AS-9 without a source-control integration with "Start run" disabled
When the tester presses Tab through AS-5 and AS-9
Then neither disabled control receives focus by Tab or Shift+Tab, each disabled control exposes `disabled` or `aria-disabled="true"` in the accessibility tree, a programmatic `element.focus()` on the disabled control leaves `document.activeElement` unchanged, and the enabled controls around them ("Security check (static only)" on AS-5) remain focusable and operable

Scenario: The run log and diff regions are keyboard-scrollable
Given AS-11 with a 200-line log and a diff longer than the viewport, and a browser viewport 320 by 640 CSS pixels
When the tester presses Tab until the "Run log" region receives focus, then presses Page Down and Arrow Down, then tabs to the "Code diff" region and presses Page Down
Then each region is focusable with `tabindex="0"`, has the accessible name "Run log" or "Code diff" respectively, scrolls its own content while focus stays on the region, and the first visible line or hunk changes after each Page Down without moving focus to another element

### Covered requirements (traceability)
- FR-130
- FR-131

### Out of scope
The business behaviour of the surfaces being operated (BSB-18 to BSB-37); adding mouse, touch or
pen interactions; audio or voice control; browser and operating-system keyboard shortcut
customisation; screen-reader-specific vendor behaviour; accessibility of surfaces outside the
builder, native mobile clients and WCAG certification claims beyond the audited surfaces; the
automated check that enforces these criteria in continuous verification (BSB-38-PENDING-7).

### Notes / dependencies
This story audits the surfaces its owning epics render and adds only keyboard semantics, tab order
and focus styling. AS-1 to AS-3 depend on BSB-18, AS-4 on BSB-19/BSB-20, AS-5 on BSB-21 with the
Security controls of BSB-31/BSB-32 and the Submit control of BSB-36, AS-6/AS-7 on BSB-22, AS-8 on
BSB-23, AS-9 on BSB-22/BSB-24, AS-10/AS-11 on BSB-26/BSB-33, AS-12 on BSB-31/BSB-32 and AS-13 on
BSB-36. BSB-21 and BSB-30 are written later in the fan-out, but their requirements FR-020, FR-021
and FR-070 already define the build page and readiness content these scenarios use.

No new route or product behaviour is introduced. The implementation is expected to land the
shared control primitives first, per the epic's implementation guidance, so later feature pages
inherit them; the acceptance criteria still test the rendered surfaces because that is the
author-visible value. A control that is unavailable is represented by `disabled` on a native
control, not by removing it from the page, so its state is still programmatic. The log and diff
regions are read-only content and are made focusable only so a keyboard user can scroll them.

---

## STORY: BSB-38-PENDING-2

**Title:** Read every builder status without relying on sight or colour
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As an **author who uses a screen reader or cannot distinguish status colours**, I want **every custom status component to expose its name, role and state and to show its state as text as well as colour**, so that **I can tell whether a build is Ready, a run passed, a scan failed, a submission moved or a credential is verified without seeing the page**.

### Acceptance Criteria

Scenario: Build readiness and its four checks expose name, role and state
Given AS-5 at `GET /builds/7` with head SHA "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and readiness "Not ready" whose checks are "Manifest valid: Passed", "Passing run: Not run", "Static security check: Passed" and "LLM security check: Unavailable"
When the accessibility tree of the page is read
Then the readiness element has role "status", accessible name "Build readiness" and accessible description "Not ready at 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", the four checks are a list with accessible name "Readiness checks" whose four list items have accessible names "Manifest valid: Passed", "Passing run: Not run", "Static security check: Passed" and "LLM security check: Unavailable" in that order, and each list item's state text is also visible on the page

Scenario: Run state, progress and verdicts expose name, role and state
Given AS-10 at `GET /projects/7/runs/21` with state "running", turns 3 of 12 and last event "Wrote bugfix.md", and AS-11 at `GET /projects/7/runs/21` with result_status "completed", claimed_verdict "completed" and final_verdict "pass"
When the accessibility tree of each render is read
Then the running render has a role "status" element named "Run state" with description "running", a role "progressbar" element named "Run turns" with valuemin 0, valuemax 12, valuenow 3 and valuetext "3 of 12 turns", and a role "status" element named "Last event" with description "Wrote bugfix.md"; and the completed render has a role "status" element named "Run outcome" with description "completed", a role "status" element named "Claimed verdict" with description "completed", a role "status" element named "Final verdict" with description "PASS" and a role "status" element named "Overturned" with description "no"

Scenario: Scan, build and credential statuses expose name, role and state
Given AS-12 at `GET /scans/11` (verdict "pass", recommendation "INSTALL"), `GET /scans/12` (verdict "fail") and `GET /scans/14` (running), AS-13 at `GET /builds/7` in state "submitted", and AS-8 at `GET /projects/7/settings` with "Jira integration 3" "Not verified", "Source control integration 4" "Verified" and "AI model profile Default" "Verified"
When the accessibility tree of each render is read
Then each scan has a role "status" element named "Scan verdict" whose description is "PASS", "FAIL" or "In progress" respectively and, for the completed renders, a role "status" element named "Recommendation" with description "INSTALL" or "DO_NOT_INSTALL"; the build has a role "status" element named "Build state" with description "Submitted"; and each integration has a role "status" element named "Credential status for Jira integration 3", "Credential status for source control integration 4" or "Credential status for AI model profile Default" with description "Not verified" or "Verified"

Scenario: Every status carries a visible text label in addition to colour
Given the status components of AS-5, AS-8, AS-10, AS-11, AS-12 and AS-13 in their fixture states
When each status is rendered twice, once normally and once with CSS `filter: grayscale(1)` applied to the whole page
Then in both renders each status component contains a visible, non-empty text label from the set "Ready", "Not ready", "Passed", "Failed", "Not run", "Unavailable", "In progress", "running", "completed", "failed", "PASS", "FAIL", "no", "yes", "Open", "Submitted", "Merged", "Abandoned", "Verified" and "Not verified", the label is not clipped, hidden or transparent, and hiding the status's coloured dot or background removes no information because the label alone still states the status

Scenario: An unknown or unavailable status is exposed, never defaulted to a passing state
Given AS-5 whose LLM security check is recorded "unavailable", AS-12 at `GET /scans/14` whose scan is still "running", and a run whose database state value is "archived" (not a value the app defines)
When the accessibility tree of each render is read
Then the LLM check's accessible name is "LLM security check: Unavailable", the in-progress scan's "Scan verdict" description is "In progress", the unknown run's "Run state" description is "Unknown (archived)", and none of the three renders a description of "Passed", "PASS", "Ready" or an empty string

### Covered requirements (traceability)
- FR-132
- FR-135

### Out of scope
Computing or storing any status (BSB-26, BSB-30, BSB-31, BSB-32, BSB-33 and BSB-36 own the
values); changing the status vocabularies those epics define; adding audible alerts or sounds;
colour-independent encoding beyond a visible text label (for example pattern fills); announcing
changes over time (BSB-38-PENDING-4); contrast ratios (BSB-38-PENDING-5); accessibility of
surfaces outside the builder and WCAG certification claims.

### Notes / dependencies
This story adds roles, accessible names and state descriptions to status components that already
exist; it does not add or change any status value. The components audited come from BSB-21/BSB-30
(build readiness and the four checks), BSB-26/BSB-33 (run state, progress, outcome and verdicts),
BSB-31/BSB-32 (scan verdict and recommendation), BSB-23 (credential verification) and BSB-36
(build state). Those requirements exist even where BSB-21, BSB-29 and BSB-30 have no stories yet in
the fan-out.

The four readiness check labels are exactly the labels BSB-36 already uses: "Manifest valid",
"Passing run", "Static security check" and "LLM security check". The run vocabulary is BSB-26's
(`requested`, `preparing`, `prepared`, `preparation_failed`, `running`, `completed`, `failed`) and
BSB-33's (`Claimed verdict`, `Final verdict` PASS/FAIL/not run, `Overturned` yes/no). The scan
vocabulary is BSB-31's (`Verdict: PASS`/`FAIL`, `Recommendation: INSTALL`/`DO_NOT_INSTALL`,
`Scan in progress`). Nothing here renames a visible label.

The role "status" is used for value-bearing status components because it is the ARIA role for
advisory status information; the accessible name identifies which status it is and the accessible
description carries the value. A native `progressbar` carries the turn state in its ARIA value
properties. A status value the application does not recognise is exposed as "Unknown" followed by
the unrecognised value, for example "Unknown (archived)", instead of being coerced to a passing
value; this is a display rule, not a new storage rule.

---

## STORY: BSB-38-PENDING-3

**Title:** Fill every builder form with its label, instructions and errors exposed
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As an **author who uses a screen reader**, I want **every field on every builder form to expose its label, instructions, required state and error message**, so that **I can enter the right value the first time and recover from a validation error without guessing which field or message applies to me**.

### Acceptance Criteria

Scenario: Every field on the create-build form exposes its label, instructions, required state and error
Given AS-4 at `GET /builds/new` for Ada, with empty skill name and description, and a catalog tree in which skill "sdlc-plan-training" exists and "sdlc-plan-new-skill" does not
When the accessibility tree is read before any submit, and again after submitting the skill name "plan-new-skill" with the description "Plan a training session"
Then the form has a text field with accessible name "Skill name", `required` or `aria-required="true"`, and description "Use the sdlc prefix followed by an area and an action segment, for example sdlc-plan-new-skill."; a text field with accessible name "One-line description", `required` or `aria-required="true"`, and description "A single line describing what the skill does."; and after the submit the "Skill name" field has `aria-invalid="true"`, its accessible description includes "Skill name must have the sdlc prefix and at least an area and an action segment, for example sdlc-plan-new-skill.", focus is on the "Skill name" field, and correcting the field to "sdlc-plan-new-skill" removes `aria-invalid` and the error from the accessibility tree

Scenario: Every field on the run-start and integration forms exposes its label, instructions and group
Given AS-9 at `GET /projects/7/runs/new?build=7` and AS-8 at `GET /projects/7/integrations/new` for Ada
When the accessibility tree of each form is read
Then the run-start form exposes the fields "Skills branch", "Input branch", "Workflow", "Step", "Model profile", "Model tier", "Reviewer feedback" and "Upstream handoff", each with an accessible name; the "Model tier" select has accessible name "Model tier" and options "high", "medium" and "low", and the "Model profile" select has accessible name "Model profile"; the optional "Workflow", "Step", "Reviewer feedback" and "Upstream handoff" fields expose `aria-required="false"` and their visible labels end with "(optional)", while "Skills branch", "Input branch", "Model profile" and "Model tier" expose `aria-required="true"`; and the integration form exposes "Site URL" with description "The base URL of the Jira site, for example https://example.atlassian.net.", "Project key" and "Template project" with the group description "Provide either a project key or a template project, not both.", and "API token" with description "Stored in the external secret store and never displayed after save.", where the "API token" control has type "password" and neither its value nor any credential value appears in the accessibility tree or page text

Scenario: The project create and add-member forms expose their labels and errors
Given AS-6 at `GET /projects/new` and AS-7 at `GET /projects/7/members/new` for Ada, a blank project name of "   ", and an added email "carol@example.com" for which no builder account exists
When each form is submitted
Then the project form's text field has accessible name "Project name", `aria-required="true"` and description "The name shown to project members.", the add-member form's text field has accessible name "Member email", `aria-required="true"` and description "The email address of an existing skill-builders user.", after each submit its field has `aria-invalid="true"` and its accessible description includes "A project name is required." or "No skill-builders user with email carol@example.com." respectively, focus is on that field, and no other field on the form has `aria-invalid="true"`

Scenario: Submission exposes every error, associates it with its field and focuses the first invalid field
Given AS-4 at `GET /builds/new` with the skill name "plan-new-skill" and a description of three spaces, and Ada submitting the form
When the server returns the two validation errors
Then a role "alert" summary named "There are 2 problems with this form." lists "Skill name must have the sdlc prefix and at least an area and an action segment, for example sdlc-plan-new-skill." followed by "A one-line description is required."; each message is programmatically associated with its own field, each field has `aria-invalid="true"`, focus is on "Skill name" as the first invalid field in reading order, and the summary is the first element after the page heading

Scenario: A form-level error is exposed as an alert and no field is falsely marked invalid
Given AS-9 at `GET /projects/7/runs/new?build=7` for a project with no source-control integration, rendering "No source-control integration is configured for this project." and disabled "Start run", and a direct POST "/projects/7/runs" that returns HTTP 422 with "A source-control integration is required to start a run."
When the error render of the page is read
Then the message is in a role "alert" region named "Run cannot start", the region is associated with the run-start form, no field on the form has `aria-invalid="true"`, and focus is on the alert region

### Covered requirements (traceability)
- FR-133

### Out of scope
The validation rules and their wording (BSB-19, BSB-23, BSB-24); form layout, field order and
business behaviour; client-side validation as a substitute for the server's rules; password
managers and autocomplete policy; adding new fields or new forms; the credential-storage guarantee
itself (BSB-23); accessibility of surfaces outside the builder and WCAG certification claims.

### Notes / dependencies
This story wires labels, descriptions, group names and error associations onto forms that BSB-19
(create, clone and edit build), BSB-22 (project and add-member), BSB-23 (integration) and BSB-24
(run start) already own. It changes no validation rule and adds no field; the error messages it
asserts are the messages those stories already define. Where a story writes its own error wording, this
story uses it unchanged.

Every field's instruction is programmatically associated (for example with `aria-describedby`) and
is also visible, so a screen-reader user hears it and a sighted user reads it. Required state is
exposed on the control rather than inferred from an asterisk. An error is associated only with the
field it belongs to; a form-level failure that belongs to no field is an alert, not a false field
error. The "API token" value is never rendered, so the accessibility tree cannot expose it; the
description tells the author it is stored externally. The project and add-member forms follow the
same rules as the create-build form even though they have one field each.

---

## STORY: BSB-38-PENDING-4

**Title:** Hear run progress and readiness changes as they happen
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As an **author who uses a screen reader**, I want **run progress and build readiness changes to be announced automatically as they happen**, so that **I know when a run advances or a build becomes Ready without refreshing the page and re-reading it**.

### Acceptance Criteria

Scenario: Run state and progress changes are announced once each
Given AS-10 at `GET /projects/7/runs/21` for Ada, with the page's live region reading "Run 21 is running. Turns: 3 of 12. Last event: Wrote bugfix.md.", and the live projection `GET /projects/7/runs/21/live` then answering first `{"state": "running", "turns": 4, "max_turns": 12, "last_event": "Pushing skilltest/21", "failure_reason": null}` and then `{"state": "completed", "turns": 4, "max_turns": 12, "last_event": "Pushed skilltest/21.", "failure_reason": null}`
When the page polls the live projection every 2 seconds while the run is not terminal
Then the page contains exactly one live region with role "status", accessible name "Live updates", `aria-live="polite"` and `aria-atomic="true"`; after the first poll its text is exactly "Run 21 is running. Turns: 4 of 12. Last event: Pushing skilltest/21."; after the second poll its text is exactly "Run 21 completed."; and each change replaces the previous text once with no duplicate announcement for the same values

Scenario: A failed run is announced with its reason
Given AS-10 with the live region reading "Run 21 is running. Turns: 7 of 12. Last event: Running the verifier.", and the live projection then answering `{"state": "failed", "turns": 7, "max_turns": 12, "last_event": "Running the verifier.", "failure_reason": "The agent process exited with code 2."}`
When the page polls once, and then polls again with the identical response
Then after the first poll the live region's text is exactly "Run 21 failed: The agent process exited with code 2.", and after the second identical poll the region's text is still exactly that and no new announcement is produced

Scenario: A readiness change is announced on the build page
Given AS-5 at `GET /builds/7` for Ada with the live region reading "Build 7 is Not ready at 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d: Passing run is missing.", and the live projection `GET /builds/7/live` then answering `{"head_sha": "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", "readiness": "not_ready", "checks": {"manifest": "Passed", "passing_run": "Not run", "static_scan": "Passed", "llm_scan": "Unavailable"}}` and then `{"head_sha": "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", "readiness": "ready", "checks": {"manifest": "Passed", "passing_run": "Passed", "static_scan": "Passed", "llm_scan": "Unavailable"}}`
When the page polls the live projection every 2 seconds while readiness is pending
Then after the first poll the live region's text is exactly "Build 7 is Not ready at 8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f: Passing run is missing.", after the second poll it is exactly "Build 7 is Ready at 8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f.", and each change is announced once

Scenario: An unavailable live update is announced once and not repeated
Given AS-10 at `GET /projects/7/runs/21` with the live region reading "Run 21 is running. Turns: 3 of 12. Last event: Wrote bugfix.md.", and the live projection then answering HTTP 503 "Service Unavailable" on two consecutive polls
When the page polls twice
Then after the first failed poll the live region's text is exactly "Live updates unavailable. Retry.", after the second failed poll the text is still exactly that and no second announcement is produced, and the page keeps rendering the last known state, turns and last event rather than an empty state

Scenario: Announcements never contain credentials and unchanged values announce nothing
Given AS-10 for run 21 whose progress and log contain the injected values "sk-ant-test-3c9e" and "ghp-test-token-7a1d" and whose projection renders them as "[REDACTED]", and a page load whose live region reads "Run 21 is running. Turns: 3 of 12. Last event: Calling the model."
When the page loads, then polls three times with a projection whose values are byte-identical to the loaded state
Then none of the live region's texts contains "sk-ant-test-3c9e", "ghp-test-token-7a1d" or "[REDACTED]", and the live region's text is byte-identical after each of the three polls so no announcement is produced

### Covered requirements (traceability)
- FR-134

### Out of scope
Computing progress, readiness or terminal states (BSB-26 and BSB-30); how the agent writes
progress or logs; the portal's notification centre; email, SMS or chat notifications; sounds or
haptics; announcing changes on surfaces other than the run page and the build page; changing the
polling interval per user; announcements for surfaces outside the builder and WCAG certification
claims.

### Notes / dependencies
This story adds the two read-only live projections `GET /projects/7/runs/21/live` and
`GET /builds/7/live` and one persistent live region per page. The run projection reads BSB-26's
`runs/21/progress.json` and the run row (state, turns, failure reason); the build projection reads
BSB-30's readiness evaluation and the build's head SHA. Neither projection writes, and both apply
their page's authorization: BSB-22's project-membership check for the run and BSB-18's gate plus
BSB-21's build access rule for the build. They add no new product behaviour beyond FR-045, FR-046
and FR-070.

The 2-second poll runs only while the state is pending (a run not in a terminal state, or a
readiness not yet decided); it stops on a terminal value and on page unload. A poll that returns
the same values produces no DOM change and therefore no announcement. The initial server-rendered
content is present but is not an announcement, because assistive technology announces changes to
an existing live region, not the content of a freshly loaded document. If the projection cannot be
read, the page keeps its last known values and announces the unavailable sentence once, so a
transient failure neither blanks the page nor repeats every 2 seconds. Credential redaction is
BSB-23's rule and BSB-26-PENDING-2's run-view rule; this story applies it to the live text and adds
no new storage.

The exact sentence forms, shown with the fixtures above, are: "Run 21 is running. Turns: 4 of 12.
Last event: Pushing skilltest/21.", "Run 21 completed.", "Run 21 failed: The agent process exited
with code 2.", "Build 7 is Ready at 8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f.", "Build 7 is Not
ready at 8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f: Passing run is missing." and "Live updates
unavailable. Retry." A value change of any of state, turns, last event, failure reason or readiness
produces one new sentence; a change of no value produces none.

---

## STORY: BSB-38-PENDING-5

**Title:** Read all builder text and status colours at WCAG 2.1 AA contrast
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As a **low-vision author**, I want **all builder text and status colours to meet WCAG 2.1 AA contrast in normal and hover or focus states**, so that **I can read every label, value and status without straining or relying on a colour difference I cannot see**.

### Acceptance Criteria

Scenario: All normal text meets 4.5:1 and all large text meets 3:1
Given every surface in the audited surface set rendered at its fixture state in the normal theme and a viewport of 1280 by 800 CSS pixels
When every visible text run on each surface is measured against the background pixels rendered directly behind it
Then every text run in a font smaller than 24 CSS pixels, or smaller than 18.66 CSS pixels when bold, has a contrast ratio of at least 4.5:1; every text run at or above those sizes has a ratio of at least 3:1; the only excluded text is text inside an inactive control (the disabled "Submit to catalog" and "Start run" controls); and the audit report lists every measured pair with its selector, foreground colour, background colour and ratio

Scenario: Hover and focus states keep text and the focus indicator at their ratios
Given the controls "Sign in" on AS-1, "Create build" on AS-4, "Save", "Security check (static only)", "Full security check" and "Submit to catalog" on AS-13, "Start run" on AS-9 and "Open trace" on AS-11
When each control is hovered with the pointer, then focused with the keyboard
Then in both states the control's visible label has a contrast ratio of at least 4.5:1 against the control's rendered background, and the focus indicator has a ratio of at least 3:1 against the adjacent background; when a hover or focus background token would take the label below 4.5:1, the rendered state uses the next darker token and the measured ratio is recorded, never left below the bar

Scenario: Every status colour pair meets AA in normal and row-hover states
Given the status components of AS-5 and AS-13 ("Ready" and "Not ready"), AS-8 ("Verified" and "Not verified"), AS-10 ("running"), AS-11 ("PASS", "FAIL", "completed" and "Overturned: no"), AS-12 ("PASS", "FAIL", "In progress" and "Recommendation: INSTALL") and AS-13 ("Open", "Submitted", "Merged" and "Abandoned")
When each status is measured in its normal state and again while its containing row is hovered
Then each status text has a contrast ratio of at least 4.5:1 against the status background in both states, and the status's dot, border or other non-text cue has at least 3:1 against the adjacent background in both states

Scenario: Text over a non-solid background is measured against the rendered pixel
Given AS-5 at `GET /builds/7` with the selected row painting `rgba(0, 0, 0, 0.06)` behind its status text, and a contrast fixture that renders the "Not ready" label #767676 over the background `linear-gradient(90deg, #ffffff, #d9d9d9)`
When the lightest and darkest pixels directly behind each text run are measured
Then on the real surfaces each text run's worst-case ratio is at least 4.5:1 for normal text and 3:1 for large text, or the run is rendered on an opaque theme background token whose measured ratio meets the bar; and the synthetic fixture is reported as failing at "3.22:1" against the #d9d9d9 end even though it would measure "4.54:1" against #ffffff, proving the audit uses the worst-case pixel

Scenario: A sub-threshold pair is rejected with its measured ratio
Given a fixture page in the audited surface registry whose "Not ready" status label is changed from its theme token to the pair #808080 on #FFFFFF
When the contrast audit for the audited surface set runs
Then the audit reports a failure for that surface with the rule `color-contrast` (WCAG 2.1 1.4.3 Contrast (Minimum)), the selector of the label and the measured ratio "3.95:1", the surface is marked failing in `accessibility-report.json`, and the `accessibility` job of BSB-38-PENDING-7 exits non-zero

### Covered requirements (traceability)
- FR-136

### Out of scope
Changing the platform theme's brand colours beyond the tokens the builder controls; dark mode,
high-contrast mode beyond the normal theme, forced-colours mode and colour-blindness simulation;
non-text contrast for controls other than the focus indicator and status cues (that belongs to
BSB-38-PENDING-1 and WCAG 1.4.11); images, charts and the catalog report viewed outside the
builder; WCAG 2.1 AAA contrast; accessibility of surfaces outside the builder and certification
claims.

### Notes / dependencies
This story owns the contrast tokens of the builder's rendered surfaces and the measured bars in the
scope decisions. It depends on BSB-38-PENDING-2 for the status components whose pairs it measures
and on BSB-38-PENDING-1 for the focus indicator it measures in the focused state. The surfaces are
the same audited set the other stories use; no route is added and no business behaviour changes.

Normal and large text follow WCAG 2.1 1.4.3. Status text is treated as normal text even when it is
bold, because status wording is short and load-bearing; a large-text exemption is available only
where the rendered font size genuinely meets the large-text definition. Non-solid backgrounds are
measured at both extremes because a gradient can pass under one pixel and fail under another. The
sub-threshold scenario is a guardrail: the fixture is never shipped, it proves the audit reports
the measured ratio rather than a pass/fail guess, and it is the same contrast rule the continuous
check in BSB-38-PENDING-7 blocks on. #808080 on #FFFFFF is 3.95:1 and is therefore below 4.5:1 for
normal text.

---

## STORY: BSB-38-PENDING-6

**Title:** Use every builder surface at 320 CSS pixels without horizontal scrolling
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-17, MVP

### Story
As an **author on a narrow screen or at high zoom**, I want **every audited builder surface to reflow to a 320 CSS-pixel viewport with no horizontal scrolling**, so that **I can read and operate the whole page by scrolling in one direction instead of panning sideways**.

### Acceptance Criteria

Scenario: Every audited surface reflows at 320 by 640 with no horizontal overflow
Given every surface in the audited surface set rendered at a viewport of 320 by 640 CSS pixels
When each surface is measured after its content has loaded
Then `document.scrollingElement.scrollWidth` is at most 320 on every surface, every element's `scrollWidth` is at most its `clientWidth` (no element scrolls horizontally), the main content occupies one column whose width is at most 320 minus the page's horizontal padding, and every text run and control is reachable by vertical scrolling alone

Scenario: Long values wrap instead of widening the page
Given AS-5 with head SHA "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", branch "build/sdlc-fix-bug-reproduce" and path "skills/sdlc-fix-bug-reproduce/SKILL.md", AS-11 with one log line of 200 characters and one diff line containing a 120-character file path, and AS-12 with the finding row "HIGH SS-101 scripts/run.sh:14"
When each is rendered at 320 by 640 CSS pixels
Then each long value wraps inside its container using `overflow-wrap: anywhere` or an equivalent computed style, no element's right edge extends past x=320, no text is truncated with an ellipsis or hidden, and every character of each long value is present in the rendered text

Scenario: The run log and diff wrap and remain readable at 320 pixels
Given AS-11 with a 200-line log and a diff longer than one viewport, rendered at 320 by 640 CSS pixels
When the log and diff regions are measured
Then the "Run log" and "Code diff" regions compute `white-space: pre-wrap`, neither region has `scrollWidth` greater than its `clientWidth`, every source line is present in the DOM and fully readable across its wrapped segments, and the page itself has no horizontal overflow

Scenario: Every primary action remains visible and reachable at 320 pixels
Given every surface in the audited surface set at 320 by 640 CSS pixels
When each surface is scrolled from top to bottom and each action is tabbed to
Then the controls "Sign in" on AS-1, "Create build" on AS-4, "Save", "Security check (static only)", "Full security check" and "Submit to catalog" on AS-5, the add-member form's submit control on AS-7, "Add integration" on AS-8, "Start run" on AS-9, "Open trace" on AS-11 and "Submit to catalog" on AS-13 each have a bounding rectangle whose left edge is at or after x=0 and whose right edge is at or before x=320, each is reachable without horizontal scrolling, and no action is hidden, clipped or moved off-screen

### Covered requirements (traceability)
- NFR-012

### Out of scope
Viewport widths below 320 CSS pixels; print styles; native mobile clients; desktop-only
administration of surfaces outside the builder; changing information architecture or removing
content at narrow widths; horizontal scrolling inside individual components as a substitute for
reflow (this story requires wrapping instead); accessibility of surfaces outside the builder and
certification claims.

### Notes / dependencies
This story changes layout styles only; it adds no route, field or action and removes no content.
The audited surfaces are the same thirteen rows the other stories use, and their owning epics keep
their behaviour. The 320 CSS-pixel value comes from NFR-012; 640 is the height used for the
measurement viewport and is not a requirement.

NFR-012 says "without two-dimensional scrolling", so this story does not use WCAG 1.4.10's
exception for content that needs two dimensions: the run log and the diff wrap (`white-space:
pre-wrap`) rather than scrolling sideways, and no element in the page is allowed horizontal
overflow. Long unbroken values such as a commit SHA, a branch name or a path must wrap; a table
that cannot fit is restacked into one column rather than given a horizontal scrollbar. The
"primary action" list keeps the end-to-end authoring loop operable at the narrow width; controls
that are conditionally absent (for example "Submit to catalog" on a submitted build) are checked
in their present state only.

---

## STORY: BSB-38-PENDING-7

**Title:** Block accessibility regressions in continuous verification
**Epic:** BSB-38 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-17, MVP

### Story
As a **skill author**, I want **every proposed change to the builder to be checked automatically for accessibility on every pull request and push to main, with a critical or serious finding blocking the merge**, so that **an inaccessible surface is caught by the pipeline instead of by me when I use the builder**.

### Acceptance Criteria

Scenario: A clean change passes the accessibility job with zero blocking findings
Given a pull request against `main` that changes only `README.md`, and the builder repository's `.github/workflows/ci.yml` with a job named "accessibility" that runs on `pull_request` and on `push` to `main`
When the `accessibility` job runs on that pull request and on the merging commit
Then each run exits 0, uploads `accessibility-report.json` that lists every row of the audited surface set, records the pinned axe-core version, and reports zero findings of impact "critical" or "serious", and the pull request's "accessibility" check is green

Scenario: A change that removes a control's accessible name fails the job and names the surface and rule
Given a pull request that changes the build-page template so the "Security check (static only)" control becomes `<button id="security-check-static"></button>` with no text and no `aria-label`, and makes no other change
When the `accessibility` job runs
Then the job exits 1, the pull request's "accessibility" check is red and blocks merge, and `accessibility-report.json` contains one blocking finding with rule "button-name", impact "critical", surface "/builds/7", selector "button#security-check-static" and the rendered fixture URL of AS-5

Scenario: A contrast regression fails the job
Given a pull request that changes the "Not ready" status label to the pair #808080 on #FFFFFF while every other token is unchanged
When the `accessibility` job runs
Then the job exits 1, `accessibility-report.json` contains a blocking finding with rule "color-contrast", impact "serious", surface "/builds/7" and measured ratio "3.95:1", and the pull request's "accessibility" check is red

Scenario: An incomplete accessibility run fails closed
Given a pull request whose accessibility job starts, and a headless Chromium that fails to launch with the error "Browser launch failed: sandbox unavailable."
When the `accessibility` job runs
Then the job exits 1, the "accessibility" check is red, the job log contains "Accessibility check did not complete.", no `accessibility-report.json` marked passing is uploaded, and the job never reports success with zero surfaces or zero findings

Scenario: Non-blocking findings are reported without failing the job
Given a pull request that introduces a single finding of impact "moderate" (rule "landmark-unique") on the projects page and no finding of impact "critical" or "serious"
When the `accessibility` job runs
Then the job exits 0, the pull request's "accessibility" check is green, and `accessibility-report.json` contains the moderate finding with its surface "/projects", rule "landmark-unique" and impact "moderate" so it is visible for follow-up rather than silently dropped

### Covered requirements (traceability)
- FR-137

### Out of scope
Fixing the findings the job reports (the owning surface's story fixes them); choosing or upgrading
the scanner beyond the pinned version; visual-regression screenshots, unit tests or manual
accessibility audits; a merge-queue or branch-protection policy outside the builder repository's workflow
file; enforcing accessibility on repositories other than this one; WCAG certification claims and
accessibility of surfaces outside the builder.

### Notes / dependencies
This story adds one job to the existing `.github/workflows/ci.yml` and a seeded fixture database
that the job starts for the audited surfaces. The fixture data is the same state the audited
surface set names in this file; the job renders each surface in headless Chromium and runs the
pinned axe-core engine with the WCAG 2.1 A and AA rule tags. It writes
`accessibility-report.json`, uploads it as a workflow artifact, and exits non-zero on any finding
of impact "critical" or "serious" or on an incomplete run. The job is required for merge through
the builder repository's branch protection; this story states the required check's name and outcome, not
the builder repository's administration screens.

The gate is deliberately narrower than every possible axe rule: critical and serious findings
block, moderate and minor findings are recorded. That matches the epic's "fail the pipeline on
critical findings" and the PRD's G6 metric of zero critical findings, while still failing on the
serious contrast rule FR-136 depends on. An incomplete run is not a pass: if the browser, the
scanner or the fixture database cannot start, the job fails with "Accessibility check did not
complete." so a broken pipeline can never be mistaken for a clean audit. The audit registry is the
audited surface set in this file, so adding a Later surface (BSB-35 or BSB-37) means adding its row
to the registry in the same change; an unlisted surface is not audited, which is why the registry
is part of this epic's contract.
