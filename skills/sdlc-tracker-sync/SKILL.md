---
name: sdlc-tracker-sync
role: integration   # ADR-035: author | reviewer | integration
description: >
  Publish approved planning and bug-triage artifacts to the tracker (Jira) through the Atlassian
  MCP: create or update the epics in `epic-map.json`, the stories in an epic's `story-map.json`
  (parented to the epic), the approved "blocks" links in `epic-sequence.json`, and the tracker
  action a bug's `bug-triage.md` records. Swaps draft `-PENDING` keys for the real Jira keys and
  changes nothing else. Use this as its own step right after an authoring step whose output was
  approved — after `sdlc-plan-epics-create`, after `sdlc-plan-stories-write` / `sdlc-plan-epic-sequence`, after
  `sdlc-fix-bug-triage` decides Fix. Trigger this even when the user just says "publish to Jira", "sync
  the stories to Jira", "create the epics in Jira", "set the blocks links", or "move the bug to In
  Progress". It decides nothing: every action comes from an artifact a person already approved.
compatibility: >
  Requires the Atlassian (Jira) MCP. Reads the planning artifacts and `bug-triage.md`; writes only
  tracker keys back into `epic-map.json`, `epics.md`, `story-map.json` and `stories.md`.
model: haiku   # tier: cheap (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-tracker-sync — Publish Approved Artifacts to Jira

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table in
> the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none). Epic-level
> artifacts live in `docs/product/epics/<EPIC_KEY>/_epic/`; bug artifacts in
> `docs/product/bugs/<BUG_KEY>/`.

> **Cost & context:** cheap tier. Batch reads, minimal fields (key, status, links), one write at a
> time — see `references/atlassian-mcp-usage.md`.

> **Single responsibility (ADR-035):** this is an `integration` skill — the only one that writes
> planning and triage results to Jira. It carries out decisions already written down and approved
> by authoring skills; it never writes or rewrites content, never reviews it, and never adds a
> story, link or transition that an artifact does not name.

## Input it expects
Whichever of these the run has (the scopes below are applied in this order, each only when its
artifact exists and has something unpublished):
1. **Epics** — `epic-map.json` + `epics.md` from `sdlc-plan-epics-create`.
2. **Stories** — the epic's `story-map.json` + `stories.md` from `sdlc-plan-stories-write`.
3. **Links** — the epic's `epic-sequence.json` from `sdlc-plan-epic-sequence`, including any
   `retired_edges`. Approval is the gate after that step; this skill runs only after it.
4. **Bug** — on a bug run, `bug-triage.md`'s **Jira** section with `Applied: no`.

## Output it produces
- Jira issues created or updated, links set, transitions applied — exactly what the artifacts say.
- Draft keys swapped for real ones: `<FA-N>-PENDING` in `epic-map.json` / `epics.md`,
  `<EPIC>-PENDING-N` in `story-map.json` / `stories.md`. No other line of those files changes.
- A hand-off reply: a table of every tracker action (scope, key, action, result).

## Procedure

### Step 1 — Confirm the target
Find the Jira tools, the project key (`epic-map.json`'s `project_key`; if it is `PENDING`, stop with
`failed_execution` — the project must be named at the gate, never guessed) and the issue type names.

### Step 2 — Epics
For each epic with a `-PENDING` key: search by summary first (re-runs must not duplicate); create
it if absent (type Epic, summary, description from its `epics.md` section, labels); swap the
draft key for the returned key in `epic-map.json` and in `epics.md`. For an epic that already has
a real key, update its summary/description only if `epics.md` differs.

### Step 3 — Stories
For each story with a `-PENDING-N` key: search first; create it (type Story, summary, description
with the statement + Gherkin acceptance criteria + out of scope, labels, story points if known),
parent it to the epic, and swap the key in `story-map.json` and `stories.md`. For stories with a
real key whose section in `stories.md` changed (a revise pass), update the description /
acceptance-criteria field. Never delete a story.

### Step 4 — Links
For each `depends_on` edge A → B, set "A blocks B" if it does not already exist, with the marker
comment from `references/atlassian-mcp-usage.md`. For each `retired_edges` entry, remove the link
only if it carries that marker; a human-set link is left alone and reported.

### Step 5 — Bug
On a bug run where `bug-triage.md` says `Applied: no`: apply the intended action — on Fix, the
project's "work started" transition plus severity/component if those fields exist; otherwise the
comment. Do not edit `bug-triage.md`; report the result in the hand-off.

### Step 6 — Hand off
Reply with the action table. Anything that failed is listed with the error; do not retry blindly.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **failed_execution**: The Atlassian MCP is not connected, the project key is unknown, or a write was refused (auth, permission, field). Name what was and was not published.
- **completed**: Nothing was unpublished (a re-run). Say so; that is a valid result.

## What this skill is NOT
- Not an author: it never writes story, epic or triage content, and never "fixes" an artifact it
  disagrees with — it publishes what was approved or fails.
- Not a reviewer: it does not judge the stories or the order.
- Not a deleter: it removes only platform-created links for retired edges, never an issue.

## Reference files
- `references/atlassian-mcp-usage.md` — driving the MCP: discovery, epics, stories, links,
  transitions, safety rules, token discipline.
