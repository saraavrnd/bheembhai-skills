---
name: sdlc-fix-bug-triage
description: >
  Triage a reported bug before anyone tries to fix it: restate the report as expected vs actual
  behaviour with concrete reproduction steps, assign a severity from the rubric, name the affected
  module, and decide whether it is a real bug to fix, a duplicate, works-as-designed, or missing
  information. On a Fix decision, move the Jira bug to In Progress. Use this as the FIRST step of
  the bug-fix workflow, before sdlc-fix-bug-reproduce. Trigger this even when the user just says
  "triage LEARN-87", "look at this bug", "is this a real bug?", or "pick up bug <KEY>". It writes
  bug-triage.md only. It does NOT reproduce the bug in code, find the root cause, or fix anything.
compatibility: >
  Tool-agnostic skill body (Claude Code or Codex). Uses the Atlassian (Jira) MCP to read the bug
  and transition it. Reads architecture.md, the stories/contracts that define the expected
  behaviour, and recent bugs in the same component. Resolves artifact paths from the Project
  Layout table in AGENTS.md.
model: haiku   # tier: cheap (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-fix-bug-triage — Decide What the Bug Is

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table in
> `AGENTS.md` at the repo root. Do not hardcode paths. **Per-bug
> artifacts live in that bug's own folder** `docs/product/bugs/<BUG_KEY>/` (`{layout.bug_dir}`),
> with short filenames: bug-triage.md, reproduction.md, test-plan.md, fix-design.md,
> verification.md, code-review.md, design-sync.md.

> **Cost & context:** This skill runs at the cheap tier. Request minimal fields from the Jira MCP
> (summary, description, environment, priority, components, linked issues, status, transitions).
> Read only the slices of architecture.md and the story/contract that define the behaviour in
> question.

A bug report is written by someone who saw a symptom, not by someone who knows the code. Triage
turns that report into a hand-off the rest of the bug-fix chain can act on without re-reading
Jira: what should happen, what happens instead, how to make it happen, how bad it is, and where
in the system it lives. It also makes the one call that saves the most effort: **is this worth
fixing as a bug at all?**

## Input it expects
- A bug key (the run's work item), with a summary and description in Jira (`context.bug`).
- `AGENTS.md` with the Project Layout table, and `docs/architecture.md`.
- Where they exist: the story whose acceptance criteria cover this behaviour, the API contract,
  `docs/ui-conventions.md` for UI bugs.

## Output it produces
- `bug-triage.md` in the bug's folder, from `templates/bug-triage.md.tmpl`.
- On a **Fix** decision: the Jira bug transitioned to **In Progress** (or left there), with
  severity and component set if the project uses those fields.
- On any other decision: a Jira comment with the decision and its reason. The bug is not moved.

## Procedure

### Step 1 — Read the report, nothing else yet
Fetch the bug's summary, description, environment, attachments list, priority, components and
linked issues. Create the bug folder if it does not exist. Note what the reporter actually
observed (error text, status code, screenshot description) separately from what they guess the
cause is. Reporter guesses go under Notes, never into Expected vs actual.

### Step 2 — Pin the expected behaviour to a source
Find the document that says what *should* happen, in this order: a story's acceptance criteria
(`story-map.json` → story folder), an API contract in `docs/api-contracts/`, `docs/ui-conventions.md`,
`docs/architecture.md`, the PRD. Quote it and cite the path. If no document defines the behaviour,
the bug may be a missing requirement, not a defect (see `references/triage-decisions.md`).

### Step 3 — Write reproduction steps someone else could follow
Numbered, concrete steps: starting state (user role, data present), the exact action (endpoint +
payload, or UI path + input), and the observable result. Fill gaps from the report's attachments
and the contract; mark each filled-in detail as *assumed*. Do not run anything yet; executing the
steps is `sdlc-fix-bug-reproduce`'s job.

### Step 4 — Locate the affected area
Name the module(s) the symptom passes through, using architecture.md and the code layout (route →
service → store). This is a pointer for the next steps, not a root cause. One or two modules is
normal; if you list more than three, you are guessing.

### Step 5 — Assign severity
Use `references/severity-rubric.md`. Severity is impact × reach, not how annoyed the reporter
sounds. Record one line of justification.

### Step 6 — Decide
Pick exactly one decision and record it on the `**Decision:**` line:
- **Fix** — a real defect against a documented expectation, with enough to reproduce.
- **Duplicate of `<KEY>`** — an open or recently fixed bug describes the same symptom and path.
- **Not a bug** — the behaviour matches the documented expectation.
- **Needs info** — you cannot write steps another engineer could follow, or no document defines
  the expected behaviour and someone has to decide it.

See `references/triage-decisions.md` for the borderline cases.

### Step 7 — Update Jira and commit the note
On Fix, apply the project's "work started" transition (names vary: "In Progress", "In Dev"). On
any other decision, add a comment with the decision and its reason, and leave the status alone.
If the Atlassian MCP is unavailable, record the intended action under Jira. Commit the note.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: Your decision is Duplicate, Not a bug, or Needs info. A person
  closes, links or clarifies the bug; the fix chain does not run.
- **completed**: Your decision is Fix, including when the steps contain assumed details or the
  severity is low.

## What this skill is NOT
- Not reproduction: it writes steps, it does not execute them or write tests.
- Not root-cause analysis: "affected area" is where to look, not why it breaks.
- Not a fix: it changes no code.

## Reference files
- `templates/bug-triage.md.tmpl` — the triage note (the hand-off to sdlc-fix-bug-reproduce).
- `references/severity-rubric.md` — S1–S4 with examples.
- `references/triage-decisions.md` — Fix vs Duplicate vs Not a bug vs Needs info, borderline cases.
- `examples/bug-triage-LEARN-87.md` — a triaged Learn Portal bug.
