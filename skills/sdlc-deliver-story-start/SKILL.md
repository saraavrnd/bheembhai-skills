---
name: sdlc-deliver-story-start
description: >
  Open a user story for delivery: confirm it is ready to be built, move the Jira story to
  In Progress via the Atlassian MCP, and write a short start note in the story's folder. Use this
  as the FIRST step of the story delivery workflow, before sdlc-deliver-story-design. Trigger this even when
  the user just says "start LEARN-21", "pick up this story", or "begin work on <STORY-KEY>". The
  readiness checks (repo scaffolded, acceptance criteria present, prerequisite stories merged)
  run as code before this skill starts; this skill only records the start and moves Jira. It does
  NOT design, test, or implement anything.
compatibility: >
  Tool-agnostic skill body (Claude Code or Codex). Uses the Atlassian (Jira) MCP to read the
  story and transition it. Reads the epic's epic-sequence.json when one exists. Resolves
  artifact paths from the Project Layout table in the repo's conventions file (`AGENTS.md`, or `CLAUDE.md` when the repo has none).
model: haiku   # tier: cheap (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-deliver-story-start — Open a Story for Delivery

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table in
> the repo's conventions file (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see `_SHARED-project-layout.md`. Do not hardcode paths. **Per-story
> artifacts live in that story's own folder** `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/`;
> epic artifacts in `docs/product/epics/<EPIC_KEY>/_epic/`.

> **Cost & context:** This skill runs at the cheap tier. Request minimal fields from the Jira MCP
> (status, epic link, transitions) and read only the sdlc-plan-epic-sequence entry for this story.

The "picking it up now" moment for one story. It replaces the preconditions and the In Progress
transition that the `story-implement` orchestrator used to perform. Under BheemBhai, the
readiness checks are code (`verify.yaml` preconditions) and run before this skill, so a story
that is not ready never reaches it. What remains is small: make the board reflect reality, and
leave a note the rest of the workflow and the reviewer can read.

## Input it expects
- A story key (the run's story), with acceptance criteria in Jira.
- A scaffolded repo: `AGENTS.md` with the Project Layout table, and `docs/architecture.md`.
- Optionally the epic's `epic-sequence.json` from `sdlc-plan-epic-sequence`.

## Output it produces
- The Jira story transitioned to **In Progress** (or left there if it already was).
- `story-start.md` in the story's folder, from `templates/story-start.md.tmpl`: story key, epic,
  prerequisites with their status, the wave, and the Jira status before and after.

## Procedure

### Step 1 — Resolve the story and its epic
Fetch the story's summary, status and epic link via the Atlassian MCP. Resolve `<EPIC_KEY>` from
the epic link, or from `docs/product/epic-map.json` if Jira has no link. Create the story folder
if it does not exist.

### Step 2 — Read the sequence entry
If `docs/product/epics/<EPIC_KEY>/_epic/epic-sequence.json` exists, read this story's
`depends_on` and `wave`, and the current Jira status of each prerequisite. If no sequence exists
for the epic, record that in the note and recommend running `sdlc-plan-epic-sequence`; do not stop.

### Step 3 — Move Jira to In Progress
Find the project's transition that means "work started" (names vary: "In Progress", "In Dev",
"Start Work") and apply it. If the story is already in that state, leave it. If the Atlassian MCP
is unavailable, record the intended transition in the note.

### Step 4 — Write the start note and commit it
Fill `templates/story-start.md.tmpl`, write it to the story folder, and commit it to the run
branch.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: The story was already In Progress, or the epic has no `epic-sequence.json`.
  Record either in the note and continue.

## What this skill is NOT
- Not a gate on readiness: the preconditions in `verify.yaml` are the gate.
- Not sdlc-deliver-story-design: it records the start; it makes no design decisions.
- Not a branch manager: the run branch is created by the platform at run initialisation.

## Reference files
- `templates/story-start.md.tmpl` — the start note.
