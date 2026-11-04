---
name: sdlc-plan-epic-review
role: reviewer   # ADR-035: author | reviewer | integration
description: >
  Review an already-decomposed epic's FULL set of stories together — not one at a time — and
  report the gaps that only show up across siblings: the same actor/role assumed by several
  stories but never actually defined, a requirement claimed by two stories in contradictory
  ways (or claimed by none), a cross-epic dependency a story quietly assumes but never states,
  a scope hole no single story's "out of scope" admits to. REVIEW ONLY: it writes one report,
  `epic-review.md`, with each gap, the stories it touches, the question a person must answer and
  the proposed change; it never edits stories, maps or Jira. `sdlc-plan-stories-write` (revise
  mode) applies the findings and `sdlc-tracker-sync` publishes them. Trigger this when the user
  says "review this epic", "drill into this epic", "find gaps across these stories", "sanity
  check the epic", "is this epic ready for sdlc-deliver-story-design", or "these stories feel
  inconsistent". Runs right after `sdlc-plan-stories-write` finishes an epic (before
  `sdlc-plan-epic-sequence` or any per-story `sdlc-plan-story-review`), or any time later.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads architecture.md / data-model.md / api-contracts /
  ui-conventions.md / ADRs from the committed sdlc-arch-design, the PRD's feature-area requirements,
  and every sibling story in the epic from `stories.md` / `story-map.json`. Read-only: no Jira
  writes, no edits outside its own report. Runs on a different model family from the author of
  the stories (ADR-035).
model: opus   # tier: strong (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-plan-epic-review — Drill a Whole Epic for Cross-Story Gaps

> **Artifact paths:** Resolve all project-artifact locations (architecture, data model, PRD,
> epics, stories, ADRs, API contracts, per-story notes, etc.) from the **Project Layout** table
> in the repo's conventions file (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see `_SHARED-project-layout.md`. Do not hardcode paths; the
> current layout places these under `docs/` (e.g. `docs/architecture.md`, `docs/adr/`,
> `docs/api-contracts/`, `docs/product/`). **Epic-level artifacts live in that epic's own
> `_epic/` folder** `docs/product/epics/<EPIC_KEY>/_epic/` (stories.md, story-map.json,
> sdlc-plan-epic-sequence.{md,json}, **epic-review.md**); per-story artifacts stay in
> `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/`. This skill's own `templates/`,
> `references/`, `examples/` stay inside the skill folder and never move under `docs/`.

> **Cost & context:** This skill runs at the `model:` tier in its frontmatter.
> An epic can hold a dozen-plus stories — batch-read `stories.md`
> and `story-map.json` once rather than fetching per story, load architecture/data-model slices
> only for the modules the epic's stories collectively touch (not whole files, not other
> epics' modules), and for any MCP calls request minimal fields and batch reads. MCP results
> persist for the session — keep them small, this skill's blast radius is already wider than
> `sdlc-plan-story-review`'s.

> **Single responsibility (ADR-035):** this is a `reviewer` skill. It judges the stories
> `sdlc-plan-stories-write` wrote and writes only `epic-review.md`. It never rewrites a story, never
> edits `stories.md`, `story-map.json` or `epic-map.json`, and never writes to Jira. The fix is
> applied by `sdlc-plan-stories-write` in revise mode, which reads this report.

`sdlc-plan-story-review` drills one story at a time — it's precise but blind to the epic around it. Some
gaps only exist in that blind spot: an actor named "admin" that three stories each assume is
defined, when the data model actually has no such role; a requirement two stories both claim to
cover, worded so each would build a different, contradicting interpretation; a story that leans on
a concept another epic owns without ever writing that dependency down. Left uncaught, every
affected story's `sdlc-deliver-story-design` (or a separate `sdlc-plan-story-review` pass) re-discovers the same gap
independently and asks the user the same question N times. This skill runs the drill once, across
the whole epic, and hands every affected story's fix to `sdlc-plan-stories-write` in one report.

## Input it expects
- An epic — by Jira key (fetched via Atlassian MCP) or its existing `stories.md` /
  `story-map.json` pair on disk.
- The committed design: `architecture.md`, `data-model.md`, `api-contracts/`, ADRs, and
  `ui-conventions.md` for feature areas with frontend/full-stack stories.
- The PRD's feature-area section and the FR/NFR IDs `epic-map.json` assigns to this epic.
- Other epics' `epic-map.json` entries and `sdlc-plan-epic-sequence` position, only far enough to tell
  whether something this epic's stories assume is legitimately another epic's deliverable.

## Output it produces
One file: `docs/product/epics/<EPIC_KEY>/_epic/epic-review.md` (from
`templates/epic-review.md.tmpl`). Nothing else changes.

For each real cross-story gap it records:
- **Severity:** `Blocking` (a developer would build the wrong thing, or two stories would
  contradict each other) or `Advisory` (worth fixing, safe to build as written).
- **Stories touched**, with the evidence (story key + the sentence or AC that shows the gap).
- **Question** a person must answer, when the fix is a product decision, not a wording fix.
- **Proposed change** per touched story — what `sdlc-plan-stories-write` (revise) should change in the
  statement, acceptance criteria, out of scope or notes. Proposed, not applied.

Plus a requirement-coverage check, a dependency-note sanity check, and an **Architecture
impact** section for a gap that needs `sdlc-arch-design` (amend) rather than a story change.

## Procedure

### Step 1 — Resolve the epic and load its full story set
Get the epic (Jira key via MCP, minimal fields: summary, description, goal, child-story links —
or resolve from disk). Load `stories.md` and `story-map.json` for this epic in one read each —
every story in the epic, not a sample. This full set is the whole point: gaps here are defined by
comparing stories against each other, not against one story's own text.

### Step 2 — Load only the system context the epic collectively touches
Read the PRD's feature-area section and the exact FR/NFR IDs `epic-map.json` maps to this epic.
Read `architecture.md` / `data-model.md` slices for every module the epic's stories reference
(union across stories, still slices — not whole files, and not modules only some *other* epic
touches). Read `api-contracts/` sections implied by any story. Skim ADRs by keyword. Check
`epic-sequence.md`/`.json` and other epics' `epic-map.json` entries only far enough to tell
whether something a story assumes is legitimately another epic's planned deliverable and how
that epic is sequenced relative to this one.

### Step 3 — Run the epic-level drill checklist
Work through `references/gap-checklist.md`'s categories, each scoped to what's only visible
*across* stories: actor/role/entity consistency, requirement coverage completeness and
non-duplication, epic-wide scope boundary, cross-story (and cross-epic) architecture fit,
dependency-note sanity, epic-wide silent NFRs, and epic-level traceability. Explicitly skip
anything that is a single-story concern with no cross-story angle (one vague adjective in one
AC, one missing unhappy path with no sibling implication) — that stays `sdlc-plan-story-review`'s job; do
not duplicate it here. Only gaps that involve two or more stories, or the epic's own boundary,
earn a question.

### Step 4 — Turn each gap into a finding
Each real cross-cutting gap becomes one finding: its severity, the stories it touches with the
evidence, one specific answerable question when a person must decide, and the proposed change per
story. Order by impact — an undefined actor used by half the epic's stories, or a silently-assumed
cross-epic dependency, outranks a wording nitpick. If a gap is a genuine architecture conflict
(not a legitimate, already-sequenced cross-epic dependency — see the checklist's category 4),
record it under **Architecture impact**, not as a story change.

### Step 5 — Write the report and stop
Write `epic-review.md` from `templates/epic-review.md.tmpl` and finish. Do not edit any story,
map or Jira issue, even when the fix looks obvious: the proposed change is the hand-off to
`sdlc-plan-stories-write` (revise mode), which applies it on the author's model family and is then
reviewed again.

> Anti-stall note: read the inputs and write the report in the same turn. Don't narrate that
> you're "about to check the architecture" and stop there.

## What this skill is NOT
- Not a replacement for `sdlc-plan-story-review` — that skill still does the deep single-story drill
  (vague thresholds, one story's missing unhappy path). This only catches what requires
  comparing stories to each other or to the epic's own boundary.
- Not `sdlc-plan-epic-sequence` — that skill computes build ORDER (topological waves, Jira "blocks"
  links). This skill only flags a dependency note that's missing, contradictory, or points at a
  story that doesn't exist; it never computes or writes the order itself.
- Not an editor — it never rewrites stories, maps or Jira; `sdlc-plan-stories-write` (revise) applies
  its proposed changes and `sdlc-tracker-sync` publishes them.
- Not authority to change architecture — a real architecture-conflict gap gets flagged to
  `sdlc-arch-design`, never quietly resolved by inventing a design inside this interview.
- Runs as a step of `sdlc-wf-planning-epic` right after `sdlc-plan-stories-write`, and can also be run on
  demand any time an epic's stories feel like they're talking past each other.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: A gap is an architecture conflict: closing it needs `sdlc-arch-design` (amend), not a story change.
- **changes_requested**: At least one `Blocking` finding, or an open question a person must answer. `sdlc-plan-stories-write` (revise) applies the report.
- **completed**: No `Blocking` findings (advisory ones may remain). The epic is ready for `sdlc-plan-epic-sequence`.

## Reference files
- `references/gap-checklist.md` — the epic-scoped drill checklist by category, with what a real
  (vs. nitpick, vs. already-`sdlc-plan-story-review`'s-job) gap looks like in each.
- `templates/epic-review.md.tmpl` — the review-log artifact structure.
- `examples/epic-review-BEEM-3.md` — an illustrative worked pass over this repo's own `BEEM-3`
  epic (Project access, identity & run ownership).
