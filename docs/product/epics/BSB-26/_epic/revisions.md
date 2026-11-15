# Revisions — BSB-26

## Pass 1 — 2026-11-15 — `epic-review.md` (cross-story gap review)

**Report applied:** `docs/product/epics/BSB-26/_epic/epic-review.md` — verdict CHANGES REQUESTED,
findings 1–9 and open questions 1–3. Target resolution: the run named "SkillBuilder", which is the
product title in `docs/product/PRD.md`, not a Jira issue. The Atlassian project
`bheembhai-skill-builder` contains only the 21 epics BSB-18 to BSB-38, and a JQL search for an
issue whose summary contains "SkillBuilder" returned no issues. The Atlassian MCP server was not
connected in this session, so **BSB-26** — the epic the preceding `sdlc-plan-stories-write` run
wrote (commit `7e10c04`) and whose review requested changes (commit `c25ba32`) — was fetched
read-only through the Atlassian REST API: summary *Run execution & outcome capture*, type Epic,
labels `FA-7` and `MVP`, status *To Do*; its description, functional scope and covered
requirements match the BSB-26 section of `docs/product/epics.md`. Nothing was written to Jira.

**Applied (findings with no open question, and the answer-independent parts of findings 1, 3 and 4):**

- **Finding 1 (blocking) — the reviewer-feedback and upstream-handoff rendering.**
  - `stories.md` fixture table: added **run `3`**, prepared like run `1` but with
    `context` = `{"workflow":"bug-fix","step":"triage","reviewer_feedback":"Please handle an empty
    issue title without failing.","upstream_handoff":{"step":"reproduce","result_status":"completed",
    "summary":"Reproduction confirmed on the input branch."}}` — the values BSB-24-PENDING-4 uses.
  - `BSB-26-PENDING-1`: added scenario *Reviewer feedback and upstream handoff reach the runtime
    context*, asserting that `BB_CONTEXT`'s `reviewer_feedback` and `upstream_handoff` are exactly
    those values as rendered by `build_step_context`.
  - `stories.md` cross-epic notes: the BSB-24 bullet now records that default workflow/step
    resolution for an omitted `context` is still open (BSB-24 Open question 4, this epic's Open
    question 1) and that no scenario below asserts a `BB_CONTEXT` or `allowed_result_statuses`
    value for an omitted context.
  - `BSB-26-PENDING-3` Notes: states that which workflow step supplies `allowed_result_statuses`
    for an omitted context is still open, and that no scenario classifies an omitted-context run.
- **Finding 2 (blocking) — the project's source-control and Jira integrations and their MCP
  definitions in the runtime environment.**
  - `stories.md` fixture table: added the `github` integration row (`id` `6`, config
    `{"repo":"saraavrnd/bheembhai-skill-fixtures","base_branch":"main"}`, `secret_ref`
    `skill-builder/7/github`, `mcp` `null`) and the `jira` integration row (`id` `5`, config
    `{"site_url":"https://old.atlassian.net","project_key":"OLD"}`, `secret_ref`
    `skill-builder/7/jira`, `mcp` =
    `{"servers":[{"name":"jira","transport":"stdio","command":"mcp-atlassian","args":["--jira-url","https://old.atlassian.net"]}]}`),
    reusing BSB-24's rows `5` and `6`. Added an integration-credentials row naming the `ai_model`
    secret value used by Finding 7 and stating that every credential is injected by `secret_ref`
    and never appears in the stored environment or the log.
  - `stories.md` environment table: added `BB_REPO_URL`
    (`https://github.com/saraavrnd/bheembhai-skill-fixtures.git`), `BB_BASE_BRANCH` (`main`) and
    `BB_MCP_CONFIG` (the `jira` integration's `mcp` value), plus a paragraph that they are built
    from the `github`/`jira` integrations and that no credential value appears in the stored
    environment or the log (NFR-004, epic BSB-23).
  - `BSB-26-PENDING-1`: added scenario *The runtime receives the project's git coordinates and MCP
    configuration*, asserting the two coordinates and the exact `BB_MCP_CONFIG` JSON value, and
    that no environment value equals the `ai_model` secret.
  - `BSB-26-PENDING-1` Notes: the dependency now names BSB-23's `ai_model`, `github` and `jira`
    integrations and FR-128/FR-129's stored MCP definitions, and states that this story renders
    them into the environment and injects credentials by reference.
  - `BSB-26-PENDING-4` Notes: added the boundary that only the model is resolved there; the other
    integrations' environment values are PENDING-1's.
- **Finding 3 (blocking), answer-independent part — the presigned PUT URLs and the result key.**
  - `stories.md` environment table: added `BB_PROGRESS_PUT_URL` and `BB_RESULT_PUT_URL`, with paths
    exactly `/runs/1/progress.json` and `/runs/1/bb_step_result.json`.
  - `BSB-26-PENDING-1` first scenario: asserts both PUT URL paths.
  - `BSB-26-PENDING-3` Notes: `bb_step_result.json` is read from the object at the key PENDING-1's
    `BB_RESULT_PUT_URL` points at.
  - `stories.md` log contract and `BSB-26-PENDING-2` Notes: record that which process writes
    `agent.log` is still open (Open question 2); the `/runs/1/agent.log` PUT URL was therefore not
    asserted and no single writer was named.
- **Finding 4 (blocking), answer-independent part — one terminal-write rule.**
  - `stories.md`: the state-vocabulary paragraph now lists the BSB-27 cap-stop terminal state and
    the BSB-25 preparation-failure state as sibling-owned values whose exact names are still open
    (Open question 3), so they are not declared absent and not invented.
  - `stories.md`: added the **Terminal-write rule** — every transition out of `running` is one
    compare-and-set on `state = 'running'`, the first terminal write wins, and BSB-27 writes its
    terminal state before it stops the container.
  - `BSB-26-PENDING-3`: added scenario *A run already terminated at its deadline is not
    overwritten* — run `1` is `failed_timeout`, its container exits `137` with no result, and the
    run stays `failed_timeout | NULL | NULL`. Notes gained the compare-and-set bullet, and the
    `failed_timeout` bullet now says the story only proves such a run is not overwritten.
  - `BSB-26-PENDING-1` Notes: a run left `queued` by a failed preparation is BSB-25's to terminate
    and is never claimed here.
- **Finding 5 (blocking) — progress and log surfaces for terminated runs.**
  - `stories.md` progress contract: the progress region is the element with id `run-progress`; the
    API's and page's `state` is `runs.state`, never the agent's own field; once the run is terminal
    the region is absent and the API keeps returning the last read values with `state` following
    `runs.state` (including the `failed_infra` example).
  - `stories.md` log contract: the log API and `run-log` element keep serving the stored log after
    the run ends.
  - `BSB-26-PENDING-2`: added scenario *A run that failed to start keeps its log and reports no
    progress*, asserting the `failed_infra` page text, the absent `run-progress` element, the
    progress body with `"state":"failed_infra"`, and the start-failure line from both the log API
    and `run-log`.
  - `BSB-26-PENDING-3`: the `completed` scenario now asserts the page has no `run-progress`
    element.
  - `BSB-26-PENDING-1`: the start-failure scenario now asserts the `run-log` element contains the
    `[skill-builder] runtime start failed: …` line.
- **Finding 6 (advisory) — executor-restart reconciliation.**
  - `BSB-26-PENDING-3`: added scenario *A restarted executor reconciles a container that already
    exited* — an executor with no in-memory record finds the container by the `bb.run_id` label,
    reads the valid result, and moves the run to `completed | completed | NULL`.
  - `BSB-26-PENDING-3` Notes: the restart bullet and the same compare-and-set.
  - `BSB-26-PENDING-1` Notes: executors find in-flight runs by the `bb.run_id` label after a
    restart.
- **Finding 7 (advisory) — NFR-004 redaction and NFR-011 tracing.**
  - `stories.md` log contract: every occurrence of a known credential value is replaced with
    exactly `[REDACTED]` before the log is stored or served.
  - `BSB-26-PENDING-2`: added scenario *A credential value in the log is redacted before it is
    stored*, using the fixture's `ai_model` secret `sk-ant-test-5f2c8e1d`; asserts the stored
    object, the log API lines and the page.
  - `BSB-26-PENDING-2` Notes: the redaction dependency on BSB-23's NFR-004 mechanism.
  - `BSB-26-PENDING-1` Notes: the launch environment carries the step kit's tracing settings with
    the NFR-011 test-environment marker, owned by BSB-34; Out of scope now names tracing beside
    token usage and cost.
- **Finding 8 (advisory) — the run routes' 404 and path/run project mismatch.**
  - `stories.md` error table: added the fixed check order (BSB-18 gates → BSB-22
    `project_not_found` → BSB-22 membership on the path project → `run_not_found`) and the row
    "the run's `project_id` differs from the path's `project_id`" → 404 `run_not_found`.
  - `BSB-26-PENDING-2`: added scenarios for `GET /api/projects/7/runs/999/progress` (404
    `run_not_found`), a path/run mismatch (`GET /api/projects/8/runs/1/progress` by a member of
    project `8`, 404 `run_not_found`), and the run page by a non-member (403
    `project_membership_required`). Notes record the ordering.
- **Finding 9 (advisory) — the bucket dependency.**
  - `BSB-26-PENDING-1` and `BSB-26-PENDING-2` Notes now name the installation-provisioned
    `skill-builder-runs` bucket (SK-001 §6, the bucket BSB-25 writes bundles to). PENDING-2's
    reference to BSB-23 for the bucket is removed.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 1 / Open question 1 (blocking).** Who resolves the default workflow and step when
  `context` is omitted — run start (storing them in `runs.context`) or BSB-26 at claim — and what
  happens when no workflow, or more than one, uses the skill. The `context` = `{}` scenario, the
  "run start owns the default" and "BSB-26 owns the default" Notes lines, the PENDING-3 sentence
  naming the source of `allowed_result_statuses` for an omitted context, and the preamble's
  commitment to an owner were not written. The preamble and PENDING-3 record the question as open
  instead.
- **Finding 3 / Open question 2 (blocking).** Whether `runs/<id>/agent.log` is the builder's
  capture of the container's stdout/stderr or an upload by the image. Naming a single writer in the
  log contract and PENDING-2's Notes, and asserting a PUT URL for `/runs/1/agent.log`, were not
  done; both places record the question as open.
- **Finding 4 / Open question 3 (blocking).** The `runs.state` value for a run stopped at its turn
  or spend cap (BSB-27, FR-051 and FR-053) and for a run whose preparation fails (BSB-25). The
  values were not named; the state-vocabulary paragraph records the ownership and the open names,
  and no scenario asserts either value.

**Across the boundary (not applied by this epic's revise pass, recorded for the owning epics):**
BSB-24-PENDING-3 and BSB-24-PENDING-4 per Open question 1; the BSB-25 and BSB-27 decompositions per
Open question 3. The report's own "Across the boundary" section carries the same list.

**Coverage:** unchanged. All 8 requirements mapped to BSB-26 (FR-044 to FR-049, FR-151 and FR-152)
are still covered by the same four stories, and no story claims a requirement outside the epic.
`story-map.json` is unchanged: no story key, summary or requirement mapping changed.

**Note for the next review (not a finding of this pass):** the added scenarios take
`BSB-26-PENDING-2` to eleven acceptance scenarios and `BSB-26-PENDING-3` to eight, above the
skill's ~7-scenario size signal. A split along the live-surfaces / error-surfaces seam is worth
considering once the open questions are answered; it was not done here because the report names no
such split. The `jira` `mcp` definition shape, the `[REDACTED]` mask, the `BB_REPO_URL` /
`BB_BASE_BRANCH` / PUT URL variable names and the `ai_model` secret fixture are contract constants
this pass pinned because no BSB-23 or step-kit story fixes them yet; reconcile them with BSB-23's
schema when that epic decomposes.
