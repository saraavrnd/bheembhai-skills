---
name: sdlc-deliver-impact-flag
role: integration   # ADR-035: author | reviewer | integration
description: >
  Warn the owners of other in-progress stories that this story's change overlaps their design:
  list the Jira stories In Progress / In Review (not this one), find those whose `story-design.md`
  names a file, module, endpoint or data entity this run's diff touched, post a "design changed by
  <KEY>, re-check your design" comment on each, and record them in `impact-flags.md`. A
  notification only — it never blocks the run and never edits another story. Use this on every
  story and bug run, after `sdlc-deliver-docs-sync` and before `sdlc-deliver-pr-open`. Trigger this even when
  the user just says "who does this change affect", "flag overlapping stories", or "notify the
  other developers".
compatibility: >
  Requires the Atlassian (Jira) MCP to list stories and add comments. Reads this run's diff and
  the other stories' `story-design.md` notes. Writes only `impact-flags.md` in this work item's
  folder.
model: haiku   # tier: cheap (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-deliver-impact-flag — Flag Overlapping In-Progress Stories

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table in
> the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none). Per-story
> artifacts live in `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/`; bug artifacts in
> `docs/product/bugs/<BUG_KEY>/`.

> **Single responsibility (ADR-035):** this is an `integration` skill, split out of
> `sdlc-deliver-docs-sync`. It reports overlaps to the people who need to know; it does not change any
> doc, design, code or other story. Run on every story and bug run: the overlap signal is the
> code diff, not the docs, so it matters even when docs-sync changed nothing.

The multi-developer safeguard. People design their stories against the code and docs as they were
when they started. When this story changes a shared helper, a column, a default or an endpoint
that another in-flight story's design relies on, that developer should hear about it now, not as a
merge conflict or a broken test later.

## Input it expects
- This run's diff against its base (files and the modules, endpoints and entities they define).
- The other stories In Progress / In Review in the Jira project (key, status, epic) — one batched,
  minimal-fields query via the Atlassian MCP.
- Each of those stories' `story-design.md` (sections "Modules touched", "Interfaces / endpoints",
  "Data-model deltas", "Reuse") — slices, not whole files.

## Output it produces
- `impact-flags.md` in this work item's folder, from `templates/impact-flags.md.tmpl`: the stories
  checked, and each overlap with its evidence.
- One Jira comment on each overlapping story.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part for a template before you fill it.

## Procedure

### Step 1 — Pre-filter with no judgement (cheap, always)
List the other stories In Progress / In Review. Collect the paths, modules, endpoints and entity
names in this run's diff, and the ones each candidate's `story-design.md` names. Keep only the
stories whose set intersects this diff's. **No intersection → write `impact-flags.md` with
"No overlaps" and finish** — that is the common case.

### Step 2 — Confirm each candidate
For each remaining story, confirm the overlap is real: this diff changes the behaviour, signature,
schema or contract of something that story's design names (not just a shared file with an
unrelated edit). Each confirmed flag must cite this diff's `path:line` or the entity/endpoint, and
the line in the other story's design that relies on it. **No evidence → no flag.**

### Step 3 — Notify
On each confirmed story, add one Jira comment: "Design changed by <THIS_KEY>: <what changed, e.g.
`material` table gained `checksum`>. Please re-check your story design before (or while)
implementing." Do not comment twice on a re-run: check for an existing comment from this key first.

### Step 4 — Record and commit
Write `impact-flags.md` (stories checked, flags with evidence, comments posted) and commit it.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: No overlaps, or the overlaps were flagged. A flag never blocks the run.
- **failed_execution**: The Atlassian MCP is not connected, so the in-progress stories cannot be listed.

## What this skill is NOT
- Not a gate: it never blocks or routes the run.
- Not an editor: it never changes another story, its design, or any doc.
- Not docs-sync: keeping the design docs current is `sdlc-deliver-docs-sync`.

## Reference files
- `templates/impact-flags.md.tmpl` — the record of what was checked and flagged.
- `examples/impact-flags-LEARN-21.md` — LEARN-21's material upload flags LEARN-22.
