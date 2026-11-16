# Stories — BSB-36 (Catalog submission)

Epic BSB-36 covers FR-107 to FR-115 and FR-161. It is decomposed into 4 vertical slices below, and
coverage of all ten requirements is verified.

The slices are the end of the authoring loop as an author experiences it: the Submit to catalog
control is offered only for a build that is Ready at its current head and the submission re-checks
that readiness (PENDING-1); submitting opens exactly one catalog pull request in the author's own
source-control identity, with the four readiness checks and the run and scan report links in its
description, and writes nothing directly to the catalog or platform data (PENDING-2); the build
records the pull-request URL and state and moves through open, submitted, merged or abandoned as
the catalog's review flow changes the pull request (PENDING-3); and a save after submission clears
readiness, with the next Ready submission refreshing that same open pull request rather than
opening a second one (PENDING-4).

**Source.** The run hand-off names `SkillBuilder-2`, which is the PRD's work-item umbrella rather
than a Jira issue: a read-only Jira REST `GET /rest/api/3/issue/SkillBuilder-2` returned HTTP 404
"Issue does not exist or you do not have permission to see it.", matching `PRD.md` section 8. The
Atlassian MCP server is configured in `.mcp.json`, but this session exposed no Atlassian MCP tools
(`claude mcp list` reported no usable servers, and the server entries are invalid because `args`
is a string where an array is expected), so the configured site was queried read-only through its
REST API. The
epic being decomposed is BSB-36, read read-only from the same site: summary "Catalog submission",
type Epic, status To Do, labels FA-15/MVP, and a description matching the BSB-36 section of
`epics.md`. No Jira write was attempted.

**Scope decisions (made here because the epic leaves them open, not assumed silently).**
- **Submission control and route.** The build page is BSB-21's `GET "/builds/7"`; this epic adds a
  `Submit to catalog` control with a project selector and the route
  `POST "/api/builds/7/submit"` whose body is `{"project_id": 7}`. The selector lists only the
  projects in which the signed-in user has a `project_members` row with role `owner`. The route
  resolves the author's own source-control identity from the selected project's `github`
  integration (BSB-23-PENDING-2): the token stored at `integrations.secret_ref` is the project
  owner's credential, and the builder holds no separate per-user credential. The PR is therefore
  opened with the submitting owner's identity, and submission is restricted to the owner; a
  non-owner member gets HTTP 403 with `{"error": "Only the project owner can submit to the
  catalog."}`. A signed-in user with no owned project sees the control disabled with "No test
  project available." A non-member of the selected project gets BSB-22-PENDING-3's exact HTTP 403
  "You are not a member of this project."
- **Readiness is re-derived at submission.** The route calls BSB-30's readiness evaluation at
  `builds.head_sha`; all four checks must hold: manifest valid; at least one passing run at that
  SHA; a static scan at that SHA whose verdict is pass; and an LLM scan at that SHA that is
  `completed` or recorded `unavailable`. `builds.ready_sha` is a display hint only; a value equal
  to `head_sha` never skips the evaluation, and the route refuses with HTTP 422 when the fresh
  evaluation reports any check not holding.
- **Evidence selection and links.** The description links the run and the two scan rows the
  readiness evaluation used. When more than one candidate exists at the head SHA, the greatest
  `runs.id` or `scans.id` is used: the passing run, the static scan with verdict `pass`, and the
  LLM scan with state `completed` or `unavailable`. Links are absolute, built from the installation
  setting `BUILDER_PUBLIC_URL` (for example "https://builder.example.com"):
  `<base>/projects/<run.project_id>/runs/<run.id>`, `<base>/scans/<static.id>` and
  `<base>/scans/<llm.id>`. The four readiness check labels are "Manifest valid", "Passing run",
  "Static security check" and "LLM security check"; the LLM line reads `completed` or
  `unavailable`, never "PASS".
- **Catalog target.** Installation setting `CATALOG_REPOSITORY` is the catalog repository in
  owner/name form (for example "saraavrnd/bheembhai-skills"); the pull request is opened from
  `builds.branch` to that repository's `main` branch. The source-control API base is
  "https://api.github.com". These are the external catalog prerequisites named in the epic's
  Notes; no requirement defines a UI for changing them, so they are deployment settings.
- **Build and pull-request state.** `builds.pr_url` exists in ADR SK-001 section 9. This epic adds
  `builds.pr_state` (`open`, `closed`, `merged`) for FR-161, `builds.pr_integration_id` — the
  `integrations.id` whose credential opened the PR, so the state can be re-read later without
  guessing a project — and `builds.pr_head_sha`, the head SHA whose evidence the PR description
  currently describes (set on a first submission and on a refresh, and left unchanged by a save).
  `builds.state` keeps the epic's lifecycle values (`open`, `submitted`, `merged`, `abandoned`).
  An epic adding a `builds` column that the ADR's list omits has precedent: BSB-19 added
  `builds.base_sha`.
- **Pull-request state refresh.** Opening `GET "/builds/7"` for a build that has a `pr_url` and a
  non-terminal state calls `GET https://api.github.com/repos/<catalog>/pulls/<number>` with the
  recorded integration's token. `state "open"` keeps `pr_state "open"` and build `submitted`;
  `merged` true records `pr_state "merged"` and build `merged`; `state "closed"` with `merged`
  false records `pr_state "closed"` and build `abandoned`. A provider error keeps the recorded
  values and adds the notice "The pull request state could not be refreshed."; no state is guessed
  from a failed call. `merged` and `abandoned` are terminal.
- **A save on a submitted build.** The save-to-commit path is BSB-21's: it creates a commit, moves
  `builds.head_sha` and clears `builds.ready_sha` (BSB-21's FR-022). This epic adds the submitted
  case: `builds.state` stays `submitted` and `pr_url`, `pr_state` and `pr_integration_id` are
  untouched, while Submit becomes disabled until the new head is Ready. When the new head is Ready
  and differs from `pr_head_sha`, the page offers "Update catalog pull request" and the route
  updates the existing open pull request (`PATCH /pulls/<number>`) with the new head's checks and
  links instead of opening a second pull request; if the recorded PR is no longer open, the builder
  first records the observed state and refuses with the terminal message. A submission whose head
  still equals `pr_head_sha` is refused with HTTP 409 "This build is already submitted.", so a
  repeated click cannot create a second pull request or a redundant patch. This keeps one pull
  request per build and the catalog reviewer looking at evidence for the current commit. A second
  pull request is never opened for a build that already has a `pr_url`.
- **Branch after merge or abandonment.** The build branch is neither deleted nor finalised here;
  it stays at its head. BSB-20-PENDING-2 resets `build/skill-name` when a later build finds the
  previous build merged or abandoned, which is where BSB-20's review asked for this to be stated.
- **No direct writes.** The only source-control writes are `POST /repos/<catalog>/pulls` for a
  first submission and `PATCH /repos/<catalog>/pulls/<number>` when refreshing an open PR. The
  builder never merges, never writes contents or git refs, and has no platform client
  (BSB-18-PENDING-2). Merging the PR, administering the catalog review flow and bypassing the
  Ready gate are the epic's explicit non-goals.

**Unresolved cross-epic gap (not claimed by these stories).** The pull-request description links
the author-facing run report at `GET "/projects/7/runs/21"` (BSB-33) and the author-facing scan
reports at `GET "/scans/11"` and `GET "/scans/12"` (BSB-31 and BSB-32): the run report applies
BSB-22's project-membership check and the scan report BSB-18's skill-builders gate. `PRD.md`
section 2 says the catalog reviewer "Consumes the catalog pull request and its linked run and scan
reports; does not use the authoring interface", so a reviewer outside those gates cannot open the
links. BSB-22's review (Finding 1), BSB-31's review (Finding 5) and BSB-33's stories already record
this as an open human decision, and no gate answer exists in this run. These stories satisfy
FR-110 and FR-111 by linking the reports that exist and do not invent a reviewer access rule; the
access decision must be made before the catalog review flow can rely on those links.

A single requirement is covered by exactly one story:

| Requirement | Story | Acceptance criteria that cover it |
|---|---|---|
| FR-107 — Submit to catalog is enabled only when the build is Ready at the head SHA | BSB-36-PENDING-1 | "A Ready build offers Submit to catalog"; "A build that is not Ready disables Submit and says why"; "A Ready recorded for an older head is not trusted after the head moves"; "Submission re-evaluates readiness at the current head and refuses a stale Ready" |
| FR-108 — Submitting opens a catalog pull request using the author's source-control identity | BSB-36-PENDING-2 | "A Ready build opens one catalog pull request with the owner's credential" |
| FR-109 — The pull-request description lists the readiness checks at the head SHA | BSB-36-PENDING-2 | "The description lists the four readiness checks at the head SHA and links the run and scan reports"; "An unavailable LLM scan is listed as unavailable and still linked" |
| FR-110 — The pull-request description links to the run report | BSB-36-PENDING-2 | "The description lists the four readiness checks at the head SHA and links the run and scan reports" |
| FR-111 — The pull-request description links to the scan reports | BSB-36-PENDING-2 | "The description lists the four readiness checks at the head SHA and links the run and scan reports"; "An unavailable LLM scan is listed as unavailable and still linked" |
| FR-112 — The pull-request URL is recorded on the build | BSB-36-PENDING-3 | "A successful submission records the pull-request URL and state and shows them" |
| FR-113 — The build state moves through open, submitted, merged or abandoned | BSB-36-PENDING-3 | "A successful submission records the pull-request URL and state and shows them"; "A merged pull request moves the build to merged"; "A closed pull request moves the build to abandoned"; "A merged or abandoned build cannot be submitted again" |
| FR-114 — A save on a submitted build clears its readiness status | BSB-36-PENDING-4 | "A save on a submitted build creates a commit, clears readiness and leaves the submission intact" |
| FR-115 — The builder never writes directly to the platform catalog, platform projects or project skills | BSB-36-PENDING-2 | "Submission never writes directly to the catalog, platform projects or project skills" |
| FR-161 — The pull-request state is recorded on the build | BSB-36-PENDING-3 | "A successful submission records the pull-request URL and state and shows them"; "A provider outage on refresh keeps the recorded pull-request state" |

> New stories use draft keys `BSB-36-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-36, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-36-PENDING-1

**Title:** See Submit to catalog only for a build Ready at its current head
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-15, MVP

### Story
As a **skill author who owns a test project**, I want **Submit to catalog enabled only when my build is Ready at its current head**, so that **I cannot propose a skill whose evidence belongs to a different commit**.

### Acceptance Criteria

Scenario: A Ready build offers Submit to catalog
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "projects" row id 7 with owner_id 42 and name "Project Atlas", a "builds" row id 7 with skill "sdlc-fix-bug-reproduce", branch "build/sdlc-fix-bug-reproduce", created_by 42, head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "open", pr_url NULL and pr_state NULL, and a readiness evaluation for build 7 at head SHA "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" that reports manifest valid, passing run 21, static scan 11 pass and LLM scan 12 completed
When Ada opens GET "/builds/7"
Then the response is HTTP 200 rendering the "Submit to catalog" control enabled and that control's project selector whose only option is "Project Atlas (7)", the body contains neither "Submit to catalog is available only when the build is Ready at its current head." nor "No test project available.", and the source-control provider's request counter is 0

Scenario: A build that is not Ready disables Submit and says why
Given the same signed-in Ada and her "project_members" and "projects" rows for Project Atlas (id 7), a "builds" row id 7 with head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", ready_sha NULL and state "open", and a readiness evaluation for build 7 at that head SHA that reports manifest valid, passing run missing, static scan 11 fail and LLM scan not run
When Ada opens GET "/builds/7"
Then the response is HTTP 200 rendering the "Submit to catalog" control disabled with the message "Submit to catalog is available only when the build is Ready at its current head.", and the source-control provider's request counter is 0

Scenario: A Ready recorded for an older head is not trusted after the head moves
Given the same signed-in Ada and her "project_members" and "projects" rows for Project Atlas (id 7), a "builds" row id 7 with head_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "open", and a readiness evaluation for build 7 at "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f" that reports manifest valid, passing run missing, static scan not run and LLM scan not run
When Ada opens GET "/builds/7"
Then the response is HTTP 200 rendering the "Submit to catalog" control disabled with the message "Readiness was recorded for 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d; the current head is 8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f.", and the source-control provider's request counter is 0

Scenario: Submission re-evaluates readiness at the current head and refuses a stale Ready
Given the same signed-in Ada and her "project_members" and "projects" rows for Project Atlas (id 7), a "builds" row id 7 with head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "open", pr_url NULL and pr_state NULL, a "scans" row id 15 with build_id 7, stage "llm", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "failed" and failure_reason "The model endpoint timed out.", and a readiness stub whose evaluation for build 7 at that head SHA reports manifest valid, passing run 21, static scan 11 pass and LLM scan 15 failed although builds.ready_sha equals the head
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the response is HTTP 422 with {"error": "Submit to catalog is available only when the build is Ready at its current head."}, the source-control provider receives no request, and the "builds" row id 7 still has state "open", pr_url NULL, pr_state NULL, pr_integration_id NULL and ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d"

Scenario: A user with no owned test project sees Submit disabled
Given a signed-in skill author Bob whose local "users" id is 43, who has a "project_members" row (project_id 7, user_id 43, role "member") for Project Atlas (id 7), and who owns no "projects" row, the "builds" row id 7 and the all-pass readiness evaluation of the first scenario
When Bob opens GET "/builds/7" and then calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the GET response is HTTP 200 rendering the "Submit to catalog" control disabled with the message "No test project available.", the POST response is HTTP 403 with {"error": "Only the project owner can submit to the catalog."}, and the source-control provider's request counter is 0

Scenario: A non-member is refused before ownership is considered
Given a signed-in skill author Carol whose local "users" id is 44, who has no "project_members" row for Project Atlas (id 7), who owns no "projects" row, the "builds" row id 7 and the all-pass readiness evaluation of the first scenario, and a source-control stub whose request counter is 0
When Carol opens GET "/builds/7" and then calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the GET response is HTTP 200 rendering the "Submit to catalog" control disabled with the message "No test project available.", the POST response is HTTP 403 with {"error": "You are not a member of this project."}, and the source-control stub receives no request

### Covered requirements (traceability)
- FR-107

### Out of scope
Opening the pull request and assembling its description (BSB-36-PENDING-2); recording the
pull-request URL and state and the lifecycle transitions (BSB-36-PENDING-3); the save-to-commit
path and its readiness clearing (BSB-21 and BSB-36-PENDING-4); computing readiness or the four
check results (BSB-30); rendering the per-check readiness display (BSB-30); configuring or
verifying a source-control integration (BSB-23); the catalog review flow and merging the pull
request (epic non-goals); the content of the run and scan reports (BSB-31, BSB-32 and BSB-33);
reviewer-facing access to the linked reports (recorded as an unresolved cross-epic gap above);
branch deletion or finalisation (BSB-20-PENDING-2 resets the fixed branch).

### Notes / dependencies
Depends on BSB-18 for the authenticated session and the skill-builders gate, on BSB-21 for the
build page and its access rule, on BSB-22-PENDING-3 for the shared project-membership check and
its exact 403 message "You are not a member of this project.", on BSB-22-PENDING-1 for the
"projects" row and its owner, on BSB-23-PENDING-2 for the project's `github` integration and its
stored credential, and on BSB-30 for the readiness evaluation at `builds.head_sha` and its four
check results. Those requirements exist in those epics even where their stories are written later
in the fan-out. This story only reads readiness and the build; it creates no pull request and
writes no build field.

The control is rendered disabled rather than hidden so the author can see why submission is not
available. `builds.ready_sha` is never sufficient evidence on its own: the route re-runs BSB-30's
evaluation because the epic's implementation guidance says not to trust a cached Ready flag. A
stale row (as in the third scenario) therefore cannot open a pull request, and a row that looks
Ready but whose fresh evaluation fails cannot either. The project selector is the authorization
scope: the selected project's source-control integration supplies the identity for the pull
request, so only a project the user owns is offered. A direct POST is checked in order: the
caller must be a member of the selected project, which yields BSB-22-PENDING-3's exact 403 "You
are not a member of this project.", and then its owner, which yields the 403 "Only the project
owner can submit to the catalog."; the selector can only offer owned projects, but the route
enforces both because a request can bypass the page. The Submit control's enabled state does not
depend on the build's creator; it depends on the signed-in owner and on readiness.

---

## STORY: BSB-36-PENDING-2

**Title:** Submit a Ready build as a catalog pull request with its evidence
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 8 · **Labels:** FA-15, MVP

### Story
As a **skill author who owns a test project**, I want **submitting a Ready build to open one catalog pull request in my own source-control identity, with the readiness checks and the run and scan report links in its description**, so that **a catalog reviewer can judge the change from evidence recorded at that exact commit**.

### Acceptance Criteria

Scenario: A Ready build opens one catalog pull request with the owner's credential
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "projects" row id 7 with owner_id 42, a "builds" row id 7 with skill "sdlc-fix-bug-reproduce", branch "build/sdlc-fix-bug-reproduce", created_by 42, head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "open", an "integrations" row id 3 with project_id 7, kind "github", config {"repository": "saraavrnd/skill-builder-sandbox", "base_branch": "main", "test_only": true} and secret_ref "skill-builder/7/integration-3", a secret store holding "ghp-test-token-7a1d" at path "skill-builder/7/integration-3", the installation settings CATALOG_REPOSITORY "saraavrnd/bheembhai-skills" and BUILDER_PUBLIC_URL "https://builder.example.com", a catalog repository whose "main" branch is at "1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d", a source-control stub that answers POST "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls" with HTTP 201 and a JSON body whose "number" is 42, "html_url" is "https://github.com/saraavrnd/bheembhai-skills/pull/42", "state" is "open", "user.login" is "ada", "head.ref" is "build/sdlc-fix-bug-reproduce" and "base.ref" is "main", and a readiness evaluation for build 7 at head SHA "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" that reports manifest valid, passing run 21, static scan 11 pass and LLM scan 12 completed, with a "runs" row id 21 whose project_id is 7, build_id is 7, skill is "sdlc-fix-bug-reproduce", skills_commit_sha is "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state is "completed", kind is "run" and final_verdict is "pass", a "scans" row id 11 with build_id 7, stage "static", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "completed" and verdict "pass", and a "scans" row id 12 with build_id 7, stage "llm", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "completed"
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the source-control stub receives exactly one request, a POST to "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls" whose Authorization header is "Bearer ghp-test-token-7a1d" and whose JSON body has head "build/sdlc-fix-bug-reproduce", base "main" and title "Catalog submission: sdlc-fix-bug-reproduce", the response is HTTP 201 and its body contains "https://github.com/saraavrnd/bheembhai-skills/pull/42", the "builds" row id 7 records pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open", pr_integration_id 3, pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "submitted", its head_sha and ready_sha are still "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", and the catalog repository's "main" branch is still at "1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d"

Scenario: The description lists the four readiness checks at the head SHA and links the run and scan reports
Given the same signed-in Ada, the same "project_members", "projects", "builds", "integrations", secret-store, installation-setting, catalog-repository and source-control-stub fixtures, and the same all-pass readiness evaluation, "runs" row 21 and "scans" rows 11 and 12 of the first scenario
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the request body's "body" value contains "## Ready checks at 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", "- Manifest valid: PASS", "- Passing run: PASS", "- Static security check: PASS", "- LLM security check: completed", "## Evidence", "- Run report: https://builder.example.com/projects/7/runs/21", "- Static scan report: https://builder.example.com/scans/11" and "- LLM scan report: https://builder.example.com/scans/12", and the description contains exactly one line that starts with "## Ready checks at " and that line is "## Ready checks at 4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d"

Scenario: An unavailable LLM scan is listed as unavailable and still linked
Given the same signed-in Ada and the same "project_members", "projects", "builds", "integrations", secret-store, installation-setting, catalog-repository and source-control-stub fixtures, the same "runs" row 21 and static "scans" row 11, and a "scans" row id 12 with build_id 7, stage "llm", skills_commit_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "unavailable" and failure_reason "No LLM scan model profile is configured for this project.", with a readiness evaluation at the head that reports the LLM check as unavailable and still satisfied
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the source-control stub receives one POST to ".../pulls", the request body's "body" value contains "- LLM security check: unavailable" and "- LLM scan report: https://builder.example.com/scans/12", the body contains no "- LLM security check: PASS", and the response is HTTP 201

Scenario: A non-owner project member cannot submit
Given a signed-in skill author Bob whose local "users" id is 43 and who has a "project_members" row (project_id 7, user_id 43, role "member") for Project Atlas (id 7), the "builds" row id 7 of the first scenario, the readiness evaluation of the first scenario, and a source-control stub whose request counter is 0
When Bob calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the response is HTTP 403 with {"error": "Only the project owner can submit to the catalog."}, the source-control stub receives no request, and the "builds" row id 7 still has state "open", pr_url NULL, pr_state NULL and pr_integration_id NULL

Scenario: A project without a source-control integration cannot submit
Given the same signed-in Ada, the same "project_members", "projects" and "builds" rows, and the readiness evaluation of the first scenario, but no "integrations" row of kind "github" for project 7, and a source-control stub whose request counter is 0
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the response is HTTP 422 with {"error": "The project has no source-control integration."}, the source-control stub receives no request, and the "builds" row id 7 still has state "open", pr_url NULL and pr_state NULL

Scenario: A failed pull-request creation leaves the build open
Given the same signed-in Ada and all the fixtures of the first scenario except that the source-control stub answers the POST to ".../pulls" with HTTP 502 and {"message": "Server Error"}
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the response is HTTP 502 with {"error": "The catalog pull request could not be opened. Retry the submission."}, the "builds" row id 7 still has state "open", pr_url NULL, pr_state NULL, pr_integration_id NULL and ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", the catalog repository's "main" branch is still at "1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d", and no other pull request is recorded

Scenario: Submission never writes directly to the catalog, platform projects or project skills
Given the same signed-in Ada and all the fixtures of the first scenario, a source-control stub that records every request it receives, and a platform API stub that records every request it receives
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the source-control stub's request log contains exactly one request, the POST to "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls", that log contains no PUT, PATCH or DELETE request and no request whose path contains "/contents", "/git/refs", "/merges" or "/pulls/42/merge", the catalog repository's "main" branch still points at "1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d" and its tree is unchanged from commit "1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d", the platform API stub's request counter is 0, and the build's recorded submission fields are pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open", pr_integration_id 3, pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "submitted", with no other build field changed except its updated_at timestamp

### Covered requirements (traceability)
- FR-108
- FR-109
- FR-110
- FR-111
- FR-115

### Out of scope
The Submit control's enabled state and the readiness refusal (BSB-36-PENDING-1, which this story's
route also applies); recording the pull-request URL and state and the merged and abandoned
transitions (BSB-36-PENDING-3); the save-to-commit path and the refresh of an existing pull request
(BSB-21 and BSB-36-PENDING-4); computing readiness and the four check results (BSB-30); rendering
the readiness display (BSB-30); configuring or verifying the source-control integration (BSB-23);
the content and access rules of the run and scan reports (BSB-31, BSB-32 and BSB-33); making the
linked reports readable by a catalog reviewer (recorded as an unresolved cross-epic gap above);
merging the pull request, administering the catalog review workflow and bypassing the Ready gate
(epic non-goals); deleting or finalising the build branch (BSB-20-PENDING-2 resets it for a later
build); multiple pull requests per build (only the first submission is opened here).

### Notes / dependencies
Depends on BSB-18 for the session and the skill-builders gate, on BSB-21 for the build page, on
BSB-22-PENDING-1 for Project Atlas and its owner, on BSB-22-PENDING-3 for the membership check, on
BSB-23-PENDING-2 for the project's `github` integration, its `secret_ref` and its secret, on
BSB-24 for the `runs` row and its `project_id`, on BSB-25 for `runs.skills_commit_sha`, on BSB-29
for `runs.final_verdict`, on BSB-30 for the readiness evaluation, on BSB-31 and BSB-32 for the
static and LLM `scans` rows and their states and verdicts, and on BSB-33 for the run report's
route. Those requirements exist in those epics even where their stories are written later in the
fan-out.

The route is `POST "/api/builds/7/submit"` with `{"project_id": 7}`. It re-runs BSB-30's
evaluation at `builds.head_sha` (PENDING-1), resolves the selected project's `github` integration
and its credential from the secret store, and calls the source-control API at
"https://api.github.com". The PR head is the literal `builds.branch`; the base is the literal
`main` in the configured catalog repository. The returned `html_url` is what is recorded; the
builder does not construct the URL from the repository name. The token is never rendered in a
response, a log line or the description. The PR is attributed by the provider to the user behind
that token — the project owner who configured the integration — which is how FR-108's "author's
own source-control identity" is satisfied without a per-user credential store. The owner-only
refusal is therefore an identity guarantee, not an extra permission layer.

The description is one markdown block: a `## Ready checks at <head SHA>` heading, one line for
each of the four checks in the fixed order manifest, run, static, LLM, then a `## Evidence`
heading and the run, static scan and LLM scan links. The check labels and their PASS/`completed`/
`unavailable` values come from the readiness evaluation; the run and scan ids are the ones that
evaluation used, so the description cannot cite a different commit's evidence. The LLM check is
never rendered as PASS because ADR SK-001 section 1b allows it to be recorded unavailable; its
report link is still included so the reviewer can see why. A provider failure creates nothing and
leaves the build open and retryable; a retry is a first submission, so it sends the same POST
rather than a PATCH.

---

## STORY: BSB-36-PENDING-3

**Title:** Track a submission through open, submitted, merged or abandoned
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-15, MVP

### Story
As a **skill author who owns a test project**, I want **the build to record my pull request's URL and state and to move through Submitted, Merged or Abandoned**, so that **I can see where my catalog change stands without leaving the builder**.

### Acceptance Criteria

Scenario: A successful submission records the pull-request URL and state and shows them
Given a signed-in skill author Ada whose local "users" id is 42 and who has a "project_members" row (project_id 7, user_id 42, role "owner") for Project Atlas (id 7), a "projects" row id 7 with owner_id 42, a "builds" row id 7 with head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "open", pr_url NULL, pr_state NULL, pr_integration_id NULL and pr_head_sha NULL, the source-control integration 3 for project 7 with a stored credential, the all-pass readiness evaluation at the head and its run 21 and scans 11 and 12, and a source-control stub that answers the submission POST with HTTP 201 and {"number": 42, "html_url": "https://github.com/saraavrnd/bheembhai-skills/pull/42", "state": "open"} and answers GET "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 200 and {"number": 42, "html_url": "https://github.com/saraavrnd/bheembhai-skills/pull/42", "state": "open", "merged": false, "merged_at": null}
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the response is HTTP 201 with {"pr_url": "https://github.com/saraavrnd/bheembhai-skills/pull/42", "pr_state": "open", "state": "submitted"}, the "builds" row id 7 has pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open", pr_integration_id 3, pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "submitted", and a following GET "/builds/7" renders "Build state: Submitted", "Pull request: open", a link whose href is "https://github.com/saraavrnd/bheembhai-skills/pull/42" and whose text is "#42", and the "Submit to catalog" control disabled with the message "This build has already been submitted."

Scenario: A merged pull request moves the build to merged
Given a signed-in skill author Ada who owns Project Atlas (id 7), a "builds" row id 7 with head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "submitted", pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open" and pr_integration_id 3, the source-control integration 3 for project 7 with a stored credential, and a source-control stub that answers GET "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 200 and {"number": 42, "html_url": "https://github.com/saraavrnd/bheembhai-skills/pull/42", "state": "closed", "merged": true, "merged_at": "2026-11-17T09:00:00Z"}
When Ada opens GET "/builds/7"
Then the response is HTTP 200 rendering "Build state: Merged", "Pull request: merged", a link whose href is "https://github.com/saraavrnd/bheembhai-skills/pull/42" and whose text is "#42", and no "Submit to catalog" control, the "builds" row id 7 has pr_state "merged" and state "merged", and the source-control stub received exactly one GET to "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with Authorization "Bearer ghp-test-token-7a1d"

Scenario: A closed pull request moves the build to abandoned
Given the same signed-in Ada and the same "builds" row and source-control integration of the previous scenario, and a source-control stub that answers GET "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 200 and {"number": 42, "html_url": "https://github.com/saraavrnd/bheembhai-skills/pull/42", "state": "closed", "merged": false, "merged_at": null}
When Ada opens GET "/builds/7"
Then the response is HTTP 200 rendering "Build state: Abandoned", "Pull request: closed", a link whose href is "https://github.com/saraavrnd/bheembhai-skills/pull/42" and whose text is "#42", and no "Submit to catalog" control, and the "builds" row id 7 has pr_state "closed" and state "abandoned"

Scenario: A provider outage on refresh keeps the recorded pull-request state
Given the same signed-in Ada and the "builds" row id 7 in state "submitted" with pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open" and pr_integration_id 3, and a source-control stub that answers GET "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 502 and {"message": "Server Error"}
When Ada opens GET "/builds/7"
Then the response is HTTP 200 rendering "Build state: Submitted", "Pull request: open", "The pull request state could not be refreshed." and the link whose href is "https://github.com/saraavrnd/bheembhai-skills/pull/42", the body contains no exception text or stack trace, and the "builds" row id 7 still has pr_state "open" and state "submitted"

Scenario: A submitted build cannot be submitted again
Given the same signed-in Ada and the "builds" row id 7 with head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and state "submitted", pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open", pr_integration_id 3 and pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", a readiness evaluation at that head SHA that reports all four checks pass, and a source-control stub whose request counter is 0
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the response is HTTP 409 with {"error": "This build is already submitted."}, the source-control stub receives no request, and the "builds" row id 7 still has pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open" and state "submitted"

Scenario: A merged or abandoned build cannot be submitted again
Given the same signed-in Ada and her "project_members" and "projects" rows for Project Atlas (id 7), a "builds" row id 7 in state "merged" with pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42" and pr_state "merged", a "builds" row id 8 in state "abandoned" with pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/43" and pr_state "closed", a readiness evaluation for both builds at their head SHA "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" that reports all four checks pass, and a source-control stub whose request counter is 0
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7} and then POST "/api/builds/8/submit" with {"project_id": 7}
Then the first response is HTTP 409 with {"error": "This build is merged and cannot be submitted again."}, the second response is HTTP 409 with {"error": "This build is abandoned and cannot be submitted again."}, the source-control stub receives no request, and neither "builds" row changes

### Covered requirements (traceability)
- FR-112
- FR-113
- FR-161

### Out of scope
The first submission's provider request and description assembly (BSB-36-PENDING-2); readiness and
the Submit control's enabled state (BSB-36-PENDING-1 and BSB-30); the save-to-commit path and the
refresh of an existing pull request (BSB-21 and BSB-36-PENDING-4); computing the four readiness
checks (BSB-30); configuring or verifying the source-control integration (BSB-23); the content and
access rules of the run and scan reports (BSB-31, BSB-32 and BSB-33); making the linked reports
readable by a catalog reviewer (recorded as an unresolved cross-epic gap above); merging the pull
request or administering the catalog review flow (epic non-goals); deleting or finalising the
build branch after merge or abandonment (BSB-20-PENDING-2 resets it for a later build); reopening a
merged or abandoned build (both are terminal); a reviewer-facing submission dashboard or
notification (no requirement defines one).

### Notes / dependencies
Depends on BSB-21 for the build page, on BSB-22-PENDING-1 for Project Atlas and its owner, on
BSB-23-PENDING-2 for the `github` integration and its stored credential, on BSB-30 for the
readiness evaluation, and on BSB-36-PENDING-2 for the submission that first records `pr_url`.
Those requirements exist in those epics even where their stories are written later in the
fan-out.

The recorded state is two values with different vocabularies. `builds.pr_state` is the
source-control provider's state: `open`, `closed` or `merged`. `builds.state` is the build
lifecycle: `open` (created, not submitted), `submitted` (a PR has been opened and is not observed
closed or merged), `merged` (the PR was merged) and `abandoned` (the PR was closed without being
merged). The submission sets `pr_state "open"`, `state "submitted"` and `pr_head_sha` equal to
`head_sha` in the same database transaction that records `pr_url` and `pr_integration_id`; a
partial write is not a valid state. The page renders the two values separately, "Build state:
Submitted" and "Pull request: open", so an author can tell a submitted build from an open build.
A submitted build whose head still equals `pr_head_sha` has already described that commit, so the
route refuses a repeated submission with HTTP 409 "This build is already submitted." and the page
renders the control disabled with that message; a newer head is BSB-36-PENDING-4's refresh path,
not a second submission of the same evidence.

The refresh happens when the build page is opened, using `pr_integration_id` rather than a project
chosen at read time. It is a read-through refresh, not a background poller: no scheduler, webhook
or catalog-side callback exists in this epic. If the integration or its secret has been removed,
the refresh also fails closed and leaves the recorded state with the same notice. The provider
failure is never rendered as "merged" or "abandoned"; only a successful response with `merged`
true or `state "closed"` and `merged` false moves the build. A `merged` or `abandoned` build is
terminal, and both the route and the page refuse further submission or state changes. The build
branch is left at its head — this story does not delete it or finalise it. BSB-20-PENDING-2 resets
`build/skill-name` when a later build finds the previous build merged or abandoned, so the fixed
branch is reusable without this epic deleting it.

---

## STORY: BSB-36-PENDING-4

**Title:** Clear readiness on a save after submission and refresh the same pull request
**Epic:** BSB-36 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-15, MVP

### Story
As a **skill author who owns a test project**, I want **a save on a submitted build to clear its readiness and a later Ready submission to refresh the open pull request instead of opening a second one**, so that **the change I am iterating on is never judged by evidence from an earlier commit and the catalog reviewer sees one current pull request**.

### Acceptance Criteria

Scenario: A save on a submitted build creates a commit, clears readiness and leaves the submission intact
Given a signed-in skill author Ada who owns Project Atlas (id 7), a "builds" row id 7 with head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", ready_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", state "submitted", pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open", pr_integration_id 3 and pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", the source-control integration 3 for project 7 with a stored credential, a source-control stub whose branch "build/sdlc-fix-bug-reproduce" is at "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d" and which accepts a commit that moves it to "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", and which answers GET "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 200 and {"number": 42, "state": "open", "merged": false, "merged_at": null}, and a readiness evaluation for build 7 at "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f" that reports manifest valid, passing run missing, static scan not run and LLM scan not run
When Ada saves an edited "SKILL.md" on build 7 through the save-to-commit path BSB-21 owns
Then the branch "build/sdlc-fix-bug-reproduce" is at "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", the "builds" row id 7 has head_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", ready_sha NULL, state "submitted", pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open", pr_integration_id 3 and pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", and a following GET "/builds/7" renders "Build state: Submitted", "Pull request: open" and the "Submit to catalog" control disabled with the message "Submit to catalog is available only when the build is Ready at its current head.", and the source-control stub receives no POST or PATCH to any "/pulls" path

Scenario: The next Ready submission updates the existing open pull request instead of opening a second one
Given the same signed-in Ada and the same "builds" row after the save, now with head_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", ready_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f" and pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", a readiness evaluation at that head that reports manifest valid, passing run 24, static scan 13 pass and LLM scan 14 completed, a "runs" row id 24 with project_id 7, build_id 7, skills_commit_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", state "completed" and final_verdict "pass", a "scans" row id 13 with build_id 7, stage "static", skills_commit_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", state "completed" and verdict "pass", a "scans" row id 14 with build_id 7, stage "llm", skills_commit_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f" and state "completed", and a source-control stub that answers GET "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 200 and {"number": 42, "state": "open", "merged": false, "merged_at": null} and answers PATCH "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 200 and {"number": 42, "html_url": "https://github.com/saraavrnd/bheembhai-skills/pull/42", "state": "open", "title": "Catalog submission: sdlc-fix-bug-reproduce", "body": "updated"}
When Ada opens GET "/builds/7" and then calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the GET response renders an enabled "Update catalog pull request" control, the source-control stub receives exactly one PATCH to "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" whose Authorization header is "Bearer ghp-test-token-7a1d" and whose JSON body's "body" value contains "## Ready checks at 8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", "- Manifest valid: PASS", "- Passing run: PASS", "- Static security check: PASS", "- LLM security check: completed", "- Run report: https://builder.example.com/projects/7/runs/24", "- Static scan report: https://builder.example.com/scans/13" and "- LLM scan report: https://builder.example.com/scans/14", the stub receives no POST to any "/pulls" path, the response is HTTP 200 with {"pr_url": "https://github.com/saraavrnd/bheembhai-skills/pull/42", "pr_state": "open", "state": "submitted"}, and the "builds" row id 7 has pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open", pr_integration_id 3, pr_head_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f" and state "submitted"

Scenario: A failed update leaves the open pull request and recorded state unchanged
Given the same signed-in Ada and the same "builds" row after the save with head_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", ready_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f" and pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d", the same all-pass readiness evaluation, "runs" row 24 and "scans" rows 13 and 14, and a source-control stub that answers GET "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 200 and {"number": 42, "state": "open", "merged": false, "merged_at": null} and answers PATCH "https://api.github.com/repos/saraavrnd/bheembhai-skills/pulls/42" with HTTP 502 and {"message": "Server Error"}
When Ada calls POST "/api/builds/7/submit" with {"project_id": 7}
Then the response is HTTP 502 with {"error": "The catalog pull request could not be updated. Retry the submission."}, the source-control stub records no change to pull request 42's title or body, the stub receives no POST to any "/pulls" path, and the "builds" row id 7 still has head_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", ready_sha "8a7d3e0f2b6c4d1e9a8b7c6d5e4f3a2b1c0d9e8f", state "submitted", pr_url "https://github.com/saraavrnd/bheembhai-skills/pull/42", pr_state "open", pr_integration_id 3 and pr_head_sha "4f2c9a1b7d3e5a608f2c4e9b1a7d3e5f6c8b0a2d"

### Covered requirements (traceability)
- FR-114

### Out of scope
The first submission and its description (BSB-36-PENDING-2); the pull-request state refresh and the
merged and abandoned transitions (BSB-36-PENDING-3); the save-to-commit implementation, commit
message, diff and save failure semantics (BSB-21); readiness computation and the four check results
(BSB-30); configuring or verifying the source-control integration (BSB-23); the content and access
rules of the run and scan reports (BSB-31, BSB-32 and BSB-33); making the linked reports readable by
a catalog reviewer (recorded as an unresolved cross-epic gap above); opening a second pull request
for the same build; merging the pull request or administering the catalog review flow (epic
non-goals); editing a build whose state is merged or abandoned (both terminal); deleting the build
branch or the pull request; branch reset for a later build (BSB-20-PENDING-2).

### Notes / dependencies
Depends on BSB-21 for the save-to-commit path, the new commit, the moved `builds.head_sha` and the
cleared `builds.ready_sha`; those behaviours already exist in BSB-21's FR-022, and FR-114 is the
submitted-build consequence: readiness clears while the submitted state and the pull-request fields
stay. This story adds no second save path and changes no file content itself. It depends on
BSB-22-PENDING-1 for Project Atlas and its owner, on BSB-23-PENDING-2 for the `github` integration
and its credential, on BSB-30 for the readiness evaluation at the new head, on BSB-31 and BSB-32 for
the new static and LLM `scans` rows, on BSB-33 for the run report route, and on BSB-36-PENDING-2
and -PENDING-3 for the first submission and the recorded pull-request state.

The update is a `PATCH` to the pull request the build already records, not a second `POST`: the
epic's value is one reviewable change, and a second pull request from the same branch to the same
base is rejected by the provider anyway. The patch replaces the description with the new head's
checks and evidence; the title, head and base are unchanged. `builds.pr_head_sha` is the guard:
the route updates only when `head_sha` differs from it, and records the new head in the same
transaction as the successful patch; a submission whose head still equals `pr_head_sha` is the
already-submitted refusal that BSB-36-PENDING-3 owns, not a patch. If the recorded pull request is
no longer open when the new submission starts, the builder refreshes its state first (PENDING-3)
and refuses with the terminal message rather than patching a closed or merged pull request. A
failed patch leaves the recorded state and the pull request's existing description untouched, and
a retry sends the same PATCH. The build keeps `pr_url`, `pr_state`, `pr_head_sha` and
`pr_integration_id` across the save, so the author does not have to re-select the project to
update the submission.
