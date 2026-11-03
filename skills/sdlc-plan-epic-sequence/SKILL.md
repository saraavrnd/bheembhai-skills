---
name: sdlc-plan-epic-sequence
role: author   # ADR-035: author | reviewer | integration
description: >
  Order the user stories of an epic by dependency so foundational stories are built before the
  stories that depend on them: detect dependencies from explicit Jira links, from sdlc-deliver-story-design
  artifacts (what each story produces vs consumes), and from requirement/data-model traceability;
  topologically sort into parallelizable waves; flag cycles; and write the sequence plan
  (`epic-sequence.md` / `.json`) for approval. Use this after `sdlc-plan-stories-write` (stories exist for
  an epic) and before implementing them, and again in REFINE mode when `sdlc-deliver-story-design` emits a
  dependency delta. Trigger this even when the user just says "sequence the stories", "what order
  should we build LEARN-11", "order the epic", "resolve story dependencies", or "which story
  first". Authoring only: it does NOT set Jira links — `sdlc-tracker-sync` mirrors the approved
  edges as "blocks" links (ADR-035) — and it does NOT implement stories.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads the epic's stories + sdlc-deliver-story-design notes + maps from
  docs/ artifacts, and existing Jira links read-only via the Atlassian MCP when connected. Writes
  only `epic-sequence.md` and `epic-sequence.json`. Resolves artifact paths from the Project
  Layout table in the repo's conventions file (`AGENTS.md`, or `CLAUDE.md` when the repo has none).
model: haiku   # tier: cheap (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-plan-epic-sequence — Order an Epic's Stories by Dependency

> **Artifact paths:** Resolve all project-artifact locations (architecture, data model, PRD,
> epics, stories, ADRs, API contracts, per-story notes, etc.) from the **Project Layout** table
> in the repo's conventions file (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see `_SHARED-project-layout.md`. Do not hardcode paths; the
> current layout places these under `docs/` (e.g. `docs/architecture.md`, `docs/adr/`,
> `docs/api-contracts/`, `docs/product/`). **Per-story artifacts live in that story's own
> folder** `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/` with short, un-suffixed
> filenames (story-design.md, test-plan.md, verification.md, code-review.md, design-sync.md);
> epic artifacts in `docs/product/epics/<EPIC_KEY>/_epic/`. Resolve a story's files under its
> folder only. This skill's own `templates/`, `references/`,
> `examples/`, and `scripts/` stay inside the skill folder and never move under `docs/`.

> **Cost & context:** This skill runs at the `model:` tier in its frontmatter.
> To avoid context bloat: load only the slices of artifacts you
> need (not whole files), don't re-read what's already in context, and for any MCP calls request
> minimal fields and batch reads rather than fetching repeatedly. MCP results persist for the
> session — keep them small.


Decides what to build first. Left unsequenced, stories get picked in backlog order and a consumer
(a story that calls an endpoint or reads a table) can land before its producer — unbuildable and
untestable in isolation. This skill builds the dependency graph for an epic, sorts it into waves,
and records the order as a plan (`.md`) and a machine-readable map (`.json`), so `sdlc-deliver-story-start`
refuses a story whose prerequisites are not done.

> Dependency detection from artifacts is inference, not fact. This skill PROPOSES an order; the
> gate after it is where a person approves it.

> **Single responsibility (ADR-035):** this is an `author` skill. It writes the sequence only.
> Jira "blocks" links are set (and platform-created provisional links removed) by
> `sdlc-tracker-sync`, an `integration` step that runs after approval and reads the `.json` this
> skill writes. Existing Jira links are read here, never written.

## Input it expects
- An epic key (e.g. `LEARN-11`) — its stories from `stories.md` / `story-map.json`.
- `docs/product/epics/<EPIC>/_epic/story-map.json` and any `story-design.md` notes in each story's
  folder (`…/stories/<STORY>/story-design.md`) — the richest dependency signal.
- `data-model.md` and the epic's PRD requirements (for requirement-derived dependencies).
- Existing Jira issue links on the stories (explicit signal), read-only via the Atlassian MCP.
- Refine mode only: the dependency delta in a story's `story-design.md` ("Dependencies
  discovered").

## Output it produces
1. `docs/product/epics/<EPIC>/_epic/epic-sequence.md` — the proposed order: dependency list per story, the
   waves, parallelizable groups, any cycles flagged, and the rationale.
2. A machine-readable `docs/product/epics/<EPIC>/_epic/epic-sequence.json` (`{story -> {depends_on:[], wave:N}}`)
   that `sdlc-deliver-story-start` reads to refuse a story whose prerequisites are not merged, that a
   person reads to pick the next eligible story, and that `sdlc-tracker-sync` mirrors as Jira
   "blocks" links. Edges that a refine pass retires go in `retired_edges` so tracker-sync can
   remove the provisional links it created earlier (never a human-set one).

## The ordering paradox, and how this is resolved
The richest dependency signal is the per-story `sdlc-deliver-story-design` notes (what each story produces vs
consumes) — but those are written in the story delivery workflow, which runs *after* sequencing. So on
first run, design notes mostly don't exist yet. This skill therefore works in two modes:

- **Provisional (first run, before designs):** sequence on the COARSE signals that DO exist —
  explicit Jira links, requirement/data-model traceability, and the stories' acceptance-criteria
  text. Label the result **provisional**: it's a good starting order, not a final one.
- **Refined (re-run, as designs land):** when `sdlc-deliver-story-design` notes appear (each story designed
  just before it's built), re-run to fold in their precise produces/consumes. The sequence sharpens
  over the life of the epic. Crucially, sequencing never *requires* sdlc-deliver-story-design — it *benefits*
  from it when available. Dependency flows the right way: design refines sequence.

So you run `sdlc-plan-epic-sequence` once up front (provisional), start building the earliest stories, and
the order self-corrects for the *remaining* stories as their designs reveal real dependencies.

## Dependency detection — sources by availability
Combine whatever exists; precision rises as more becomes available.

### Always available (used for the provisional first run)
1. **Explicit Jira links** (most reliable) — "blocks"/"is blocked by" the team set. Ground truth;
   never overridden.
2. **Requirement / data-model derived** — from `epic-map`/`story-map` requirement IDs and
   `data-model.md`: foundational entities before features that use them; a prerequisite requirement
   before the one that builds on it.
3. **Acceptance-criteria text** — a well-written story already hints at produces/consumes. "Given
   an uploaded document, when processing runs…" → the *uploaded document* is a consume edge pointing
   at the upload story. Parse the Gherkin for nouns/actions that reference another story's output.

### Available later (used on re-runs to refine)
4. **Artifact-derived (sdlc-deliver-story-design notes)** — the precise produces/consumes profile. When a story's
   design note exists, it OVERRIDES the coarse guess for that story's edges. This is the feedback
   that sharpens the provisional order.

## Procedure

### Step 1 — Gather whatever signals exist (minimal reads — this skill's main cost risk)
This skill reads across the whole epic, so it is the most likely to bloat context. Read **slices,
not whole files**:
- Read the epic's stories from `stories.md` / `story-map.json`; if the Atlassian MCP is
  connected, read their existing links in **one batched, read-only query** requesting **minimal
  fields only** — key, status, and issue links. Do NOT pull full descriptions/changelogs.
- For dependency signal, read only the **produces/consumes lines** from each existing
  `sdlc-deliver-story-design` note (the "Interfaces / endpoints", "Data-model deltas", and "Dependencies
  discovered" sections) — not the entire note.
- From `data-model.md`, read only the **entity/table names and key fields**, not the full schema.
- From the story-map, read the requirement IDs only.
Build a compact produces/consumes profile per story from these slices. Don't re-read anything
already in context. If the epic is large, process stories in batches and keep only the profiles,
discarding raw payloads once the profile is extracted.

### Step 2 — Build the dependency graph (record provenance + confidence)
Create a directed edge A → B ("A before B") whenever B depends on A, merging all sources. For each
edge record its source (`link` / `artifact` / `requirement` / `acceptance-text`) AND a confidence:
- **firm** — from an explicit Jira link or a sdlc-deliver-story-design artifact,
- **provisional** — inferred from requirements/data-model/acceptance-text only.
This lets the plan show which edges are solid and which are best-guesses pending design.

### Step 3 — Topologically sort into waves; detect cycles
- **Cycle?** If A↔B (directly or transitively), STOP and flag it: a cycle usually means the
  stories are sliced wrong (two halves of one capability) — recommend re-splitting back in
  `sdlc-plan-stories-write`, or breaking the cycle by moving a shared piece into its own story. Do not invent
  an arbitrary order to hide a cycle.
- **No cycle:** assign waves. Wave 1 = stories with no dependencies; wave 2 = stories depending
  only on wave 1; and so on. Within a wave, stories are independent and can be built **in
  parallel** (useful for multiple developers).

### Step 4 — Write the proposed order; mark it provisional
Write `docs/product/epics/<EPIC>/_epic/epic-sequence.md`: the waves, each story's dependencies with source AND confidence,
the parallelizable groups, flagged cycles/conflicts, and — if any edges are provisional — a clear
note that the order is **provisional and will be refined as sdlc-deliver-story-design notes land**. Write
the machine-readable `docs/product/epics/<EPIC>/_epic/epic-sequence.json` (with per-edge confidence).
The gate after this step is the approval — `sdlc-tracker-sync` runs only after it; a person who adjusts
the order sends the step back and you update both files.

### Step 5 — Hand off
Report the order, the waves/parallel groups, and which edges are firm vs provisional. Tell the
user which stories are eligible to start now (wave 1), that `sdlc-tracker-sync` will mirror the approved
edges as Jira "blocks" links, that `sdlc-deliver-story-start` will refuse any story whose prerequisites are
not merged, and that the sequence will refine as each story's design is produced (see feedback
below). Note any cycle/conflict needing a human decision.

## Feedback from sdlc-deliver-story-design (the refinement loop)
`sdlc-deliver-story-design` (in the story delivery workflow) produces each story's precise produces/consumes just
before that story is built. When it does, it emits a small **dependency-delta** (see
`sdlc-deliver-story-design`'s output) — the firm edges it discovered. On receiving a delta, `sdlc-plan-epic-sequence`
re-runs in refine mode for the epic:
1. Replace that story's **provisional** edges with the **firm** ones from its design.
2. Recompute waves for the **remaining (not-yet-merged) stories** only — never reorder or disturb
   stories already built/merged.
3. If a newly-firm dependency contradicts the current order (e.g. a story you were about to build
   actually depends on one not yet done), surface it: update the plan and the `.json` (add the
   firm edge; move the contradicted provisional one to `retired_edges` with a reason), and tell the
   user the remaining order changed and why. `sdlc-tracker-sync` adjusts the Jira links.
4. If the delta only confirms existing edges, it's a no-op — no churn.
This is how the provisional first order self-corrects with real data, resolving the ordering
paradox: sequencing starts without designs and sharpens as designs arrive, with dependency flowing
the correct direction (design → sequence).

## Re-running (stories change over time)
Re-run when stories are added/removed/re-designed, or on a sdlc-deliver-story-design dependency-delta (above).
The skill reconciles against current state: add new edges, flag edges that no longer hold for the
user to confirm before retiring them, never retire a human-set (`source: link`) edge, and never
reorder already-merged stories. Idempotent — re-running with no new information changes nothing.

## Boundaries
- Proposes the order; does NOT set Jira links (`sdlc-tracker-sync`) and does NOT implement (the story
  delivery workflow).
- Does not decide unilaterally — the gate after it approves the order before tracker-sync runs.
- Does not override human-set dependency links.
- Coarse for un-designed stories; sharpens as sdlc-deliver-story-design notes appear.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: The dependencies form a cycle. Don't drop an edge to break it; a cycle needs a human to re-slice the stories.

## Reference files
- `references/dependency-detection.md` — the three sources, produces/consumes extraction, cycles.
- `templates/epic-sequence.md.tmpl` — the proposed-order plan doc.
- `templates/epic-sequence.schema.json` — the machine-readable order that sdlc-deliver-story-start reads.
- `examples/` — a worked sequence for epic LEARN-11 (3 stories, 2 waves).
