# Driving the GitHub, Bitbucket + Atlassian MCPs for PRs

`sdlc-deliver-pr-open` opens the PR and updates Jira through connected MCPs, not via hard-coded API calls.
Tool names vary by MCP version — discover them, don't assume.

**Which code host?** The run attaches one code-versioning connection and exactly one code-host
MCP: GitHub MCP → GitHub flow below; Bitbucket MCP (`@aashari/mcp-server-atlassian-bitbucket`)
→ Bitbucket flow. The Bitbucket MCP speaks only the Bitbucket Cloud REST API — never use it
against a GitHub repo, and vice versa.

## GitHub MCP
### Before creating
- List the available GitHub tools (create PR, push, get repo, list branches).
- Confirm the **repo** (owner/name) and the **base branch** (usually `main`). Don't guess.

### Push the branch
- Ensure the branch is `feat/<STORY_KEY>-<slug>` and commits reference the Jira key.
- Use the MCP's push tool; if none exists, fall back to `git push -u origin <branch>`.

### Open the PR
Provide: repo, head (story branch), base (main), title (`<STORY_KEY>: <title>`), body (the
assembled template), labels (if used). **Capture the returned PR number/URL** — you need it for
the Jira link and the hand-off.
- If the call fails with auth/permission, STOP and report; let the user fix access. Don't
  silently fall back in a way that hides a credentials problem.

## Bitbucket MCP (Bitbucket Cloud)
### Before creating
- The MCP exposes six generic tools: `bb_get`, `bb_post`, `bb_put`, `bb_patch`, `bb_delete`,
  `bb_clone` — every call is a REST path against `api.bitbucket.org/2.0`. There is no dedicated
  "create PR" tool and **no push tool**.
- Confirm the **workspace/repo** slug. `BITBUCKET_DEFAULT_WORKSPACE` scopes calls that omit the
  workspace; otherwise read the slug from the git remote (`bitbucket.org/<workspace>/<repo>.git`).

### Push the branch
- Use `git push -u origin <branch>` (the MCP cannot push). Credentials come from the run env —
  never print the token.

### Open the PR
- `bb_post` `path: /repositories/{workspace}/{repo}/pullrequests` with body:
  `{"title": "<STORY_KEY>: <title>", "description": "<assembled body>",
    "source": {"branch": {"name": "<run branch>"}},
    "destination": {"branch": {"name": "<merge target>"}}}`.
- **Capture the returned `links.html.href` (the PR URL) and `id`** — the Jira link needs it.
- Idempotency: before posting, `bb_get` the open PRs for the branch (`.../pullrequests` with
  `q=source.branch.name="<branch>"` and `state=OPEN`); if one exists, report it instead of
  creating a duplicate.
- If the call fails with 401/403, STOP and report — the token likely lacks the repository
  scopes; don't retry blindly.

## Atlassian (Jira) MCP
### Link the PR to the story
- Add the PR URL as a remote link (preferred) or a comment on the story. Use the PR captured
  above so the link is real.

### Transition the story
- Find the story's available transitions; pick the one meaning "In Review" (the name varies per
  workflow — confirm rather than assuming a fixed string).
- Apply the transition; capture the resulting status to report back.
- If the transition isn't available (workflow doesn't allow it from the current state), report
  the current status and the valid transitions rather than forcing it.

## Sequencing & safety
- Order: push → open PR → capture URL → link Jira → transition Jira. Each step depends on the
  previous; don't transition the issue before the PR exists.
- Idempotency: before opening, check whether a PR for this branch already exists (re-runs
  shouldn't create duplicates). If one exists, update/report it instead.
- Stop-on-failure: a failed PR creation or transition halts the step with a clear error; don't
  proceed to later steps on a broken earlier one.

## Fallbacks (never block the loop)
- No code-host MCP → `git push` + print the PR title/body and compare/creation URL for manual
  creation (on Bitbucket: `https://bitbucket.org/<workspace>/<repo>/pull-requests/new?source=<branch>`).
- No Atlassian MCP → print the PR link and the intended transition for the user to apply.
The branch and PR body are produced regardless of connectivity.

## Boundary
This skill never merges, approves, or closes the PR. Merge is a human decision (or a future
`sdlc-deliver-code-review` skill). It also does not re-run tests — it trusts the PASS from `sdlc-deliver-tests-verify`.

## Token-cost discipline (MCP results persist in context)
Code-host and Atlassian MCP results stay in context for the whole session. Keep them small:
- Request minimal fields; don't pull full issue/PR bodies or diffs you don't need.
- Capture only the IDs/URLs/status you must carry forward; drop the rest of the payload.
- Don't re-fetch the same issue/PR; reuse what's in context.
- Operator: `/compact` between stories; disable MCP servers not needed for the run.
