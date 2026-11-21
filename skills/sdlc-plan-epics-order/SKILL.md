---
name: sdlc-plan-epics-order
role: author   # ADR-035: author | reviewer | integration
description: >
  Order a project's EPICS by dependency, so the epics that create shared actors, entities, data
  and platform come before the epics that consume them: detect cross-epic dependencies from the
  PRD's requirements, the lifecycle of the entities each epic creates and uses, the dependency
  notes already written in `epics.md`, and existing Jira links; sort the epics into waves that
  can be planned and built in parallel; flag cycles; and write the order (`epic-order.md` /
  `.json`) for review and approval. Use this right after `sdlc-plan-epics-create`, and again
  after a revise pass. Trigger this even when the user says "order the epics", "which epic
  first", "sequence the epics", "epic dependencies", or "what can teams start in parallel".
  Authoring only: it never sets Jira links (`sdlc-tracker-sync` mirrors the approved edges as
  "blocks" links, ADR-035) and it never orders stories (that is `sdlc-plan-epic-sequence`).
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads `epics.md`, `epic-map.json` and `PRD.md`, and
  existing Jira links on published epics read-only via the Atlassian MCP when connected. Writes
  only `epic-order.md` and `epic-order.json`.
---

# sdlc-plan-epics-order — Order the Epics by Dependency

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table
> in the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see
> `_SHARED-project-layout.md`. Current defaults: the epic plan at `docs/product/epics.md` and
> `docs/product/epic-map.json`, the PRD at `docs/product/PRD.md`, and this skill's output at
> `docs/product/epic-order.md` and `docs/product/epic-order.json`. This skill's own
> `templates/`, `references/` and `examples/` stay inside the skill folder.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part
for a template before you fill it.

> **Cost & context:** This skill runs at the model tier its workflow step sets. Read slices, not
> whole files: each epic's **Functional scope**, **Implementation guidance / dependency order**
> and **Covered requirements** from `epics.md`, the requirement table rows from `PRD.md`, and
> the keys from `epic-map.json`. If the Atlassian MCP is connected and the epics already have
> real keys, read their existing links in **one batched, read-only query** (key and links only).

> **Single responsibility (ADR-035):** this is an `author` skill. It writes the epic order only.
> `sdlc-plan-epics-review` judges it on a different model family, and `sdlc-tracker-sync` sets
> the approved "A blocks B" links between epics after the review is signed off.

## Why this step exists
A PRD decomposes into an unknown number of epics. Once each epic is planned on its own (one
`sdlc-wf-planning-epic` run per epic, possibly by different people at the same time), nobody
sees the whole graph again. This step writes that graph down once, while every epic is in view:
which epic must ship before which, which epics are independent, and which waves deliver the MVP.
Story planning can then run for any epic in any order; the order matters for building.

## Input it expects
- `epics.md` and `epic-map.json` from `sdlc-plan-epics-create` (draft `<FA-N>-PENDING` keys on a
  first run; real keys once published).
- `PRD.md`, for requirement wording.
- Existing Jira "blocks" links between published epics, read-only, when the MCP is connected.
- On a revise pass (the run came back from `sdlc-plan-epics-review`): `epics-review.md` — apply
  the findings whose **Target** is `order`, and the answers given at its gate.

## Output it produces
1. `docs/product/epic-order.md` — the waves, each epic's dependencies with source and confidence,
   the parallel groups, the MVP path, and any flagged cycle (from `templates/epic-order.md.tmpl`).
2. `docs/product/epic-order.json` (from `templates/epic-order.schema.json`) — one entry per epic
   in `epic-map.json`: `epic_key`, `wave`, `depends_on`, `edge_sources`. `sdlc-tracker-sync`
   swaps draft keys in it when it publishes the epics, then mirrors every edge as a Jira link.

## Procedure

### Step 1 — Build a produces / consumes profile per epic
For each epic, from its slices: what it **creates** (actors, accounts, entities, stored data,
platform, integrations) and what it **uses** that it does not create. Record only nouns that
appear in the epic's scope or its requirements. Keep the profiles; drop the raw text.

### Step 2 — Find the edges (record source and confidence)
Add an edge A → B ("A before B") when B depends on A. Sources, strongest first:
1. **link** — an existing Jira "blocks" link between the two epics. Ground truth; never dropped.
2. **prd** — a requirement in B names an output that a requirement in A creates.
3. **epic-body** — B's "Implementation guidance / dependency order" names A, or the thing A
   creates.
4. **lifecycle** — B uses an entity, actor or state from Step 1 that only A creates.

`link` and `prd` edges are **firm**; `epic-body` and `lifecycle` edges are **provisional**.
Do not add an edge for "nice to have first" or for shared infrastructure every epic touches
lightly: an edge means B cannot be built or tested without A. See
`references/dependency-signals.md` for what counts.

### Step 3 — Sort into waves; detect cycles
- **Cycle?** If A and B depend on each other (directly or through others), stop and flag it in
  `cycles`: two epics that need each other are usually sliced wrong. Recommend the re-slice (move
  the shared piece into one epic, or into its own epic). Do not drop an edge to hide a cycle.
- **No cycle:** wave 1 holds the epics with no dependencies; wave N holds the epics whose
  dependencies are all in earlier waves. Epics in the same wave are independent.

### Step 4 — Mark the MVP path
List the waves and epics needed to deliver every MVP requirement (an MVP or mixed epic, plus
every epic it depends on, transitively). If an MVP epic depends on a `Later` epic, that is a
conflict: flag it under **Cycles and conflicts** for the reviewer and the gate.

### Step 5 — Write both files and hand off
Write `epic-order.md` and `epic-order.json`, covering **exactly** the epics in `epic-map.json`,
with the same keys. If any edge is provisional, say plainly that the order is provisional until
the epics' stories are written. Report the waves, the parallel groups and the MVP path, and that
`sdlc-plan-epics-review` reviews the plan and the order next.

## Revise pass
When the run comes back from `sdlc-plan-epics-review`, re-read `epics.md` (the epics may have
been split, merged or re-scoped by `sdlc-plan-epics-create`) and apply the review's `order`
findings. Keep firm edges unless the epic they connect is gone. Recompute the waves from scratch.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: The epics depend on each other in a cycle. Don't drop an edge to break it; a person re-slices the epics.

## What this skill is NOT
- Not a story sequencer: the order of stories inside one epic is `sdlc-plan-epic-sequence`'s job,
  in that epic's planning run.
- Not a scheduler: it says what must come first, not who builds what or when.
- Not a tracker writer: `sdlc-tracker-sync` sets the links after approval.

## Reference files
- `templates/epic-order.md.tmpl` — the order document.
- `templates/epic-order.schema.json` — the machine-readable order tracker-sync reads.
- `references/template-guide.md` — section-by-section guidance.
- `references/dependency-signals.md` — what counts as a cross-epic dependency, and what does not.
- `examples/epic-order.md` and `examples/epic-order.json` — the Learn Portal's 8 epics in 3 waves.
