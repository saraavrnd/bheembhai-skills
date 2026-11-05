---
name: sdlc-plan-epics-create
role: author   # ADR-035: author | reviewer | integration
description: >
  Decompose a Product Requirements Document (PRD) into well-formed EPICS — written to `epics.md`
  with the traceability map `epic-map.json`. Use this as the SECOND step of the PDLC chain, right
  after the `sdlc-plan-prd-write` skill. Trigger this even when the user just says "break the PRD into
  epics", "decompose the PRD", or "plan the epics". This skill reads a PRD.md and groups its
  requirements into epics along feature-area boundaries. Authoring only: it never writes to
  Jira — `sdlc-tracker-sync` publishes the approved epics (ADR-035).
compatibility: >
  Tool-agnostic skill body (Claude Code or Codex). Reads `PRD.md`; writes only `epics.md` and
  `epic-map.json`. No Jira access needed.
model: sonnet   # tier: standard (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-plan-epics-create — PRD to Epics

> **Artifact paths:** Resolve all project-artifact locations (architecture, data model, PRD,
> epics, stories, ADRs, API contracts, per-story notes, etc.) from the **Project Layout** table
> in the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see `_SHARED-project-layout.md`. Do not hardcode paths; the
> current layout places these under `docs/` (e.g. `docs/architecture.md`, `docs/adr/`,
> `docs/api-contracts/`, `docs/product/`). **Per-story artifacts live in that story's own
> folder** `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/` with short, un-suffixed
> filenames (story-design.md, test-plan.md, verification.md, code-review.md, design-sync.md);
> epic artifacts in `docs/product/epics/<EPIC_KEY>/_epic/`. Resolve a story's files under its
> folder only. This skill's own `templates/`, `references/`,
> `examples/`, and `scripts/` stay inside the skill folder and never move under `docs/`.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part for a template before you fill it.

> **Cost & context:** This skill runs at the `model:` tier in its frontmatter.
> To avoid context bloat: load only the slices of artifacts you
> need (not whole files), don't re-read what's already in context, and for any MCP calls request
> minimal fields and batch reads rather than fetching repeatedly. MCP results persist for the
> session — keep them small.


Second link in the chain. It turns a structured PRD into epics. Epics are the unit of
planning; getting their boundaries right is what makes the later `sdlc-plan-stories-write` step clean.

> **Single responsibility (ADR-035):** this is an `author` skill. It writes epic content only.
> It does not create Jira issues — `sdlc-tracker-sync` (an `integration` step) publishes the
> epics after review, swaps the draft keys `<FA-N>-PENDING` for the real Jira keys in
> `epic-map.json` and `epics.md`, and confirms the target project.

## Input it expects
A `PRD.md` produced by the `sdlc-plan-prd-write` skill (numbered FR/NFR requirements grouped under feature
areas FA-N). If given a free-form PRD, first normalise it into that shape before decomposing.

## Output it produces
1. `epics.md` — the proposed epics with their mapped requirements (the reviewable plan).
2. `epic-map.json` — a machine-readable map of `{epic_key -> [requirement IDs]}` so the next
   skill (`sdlc-plan-stories-write`) knows which requirements each epic must cover. Traceability lives here.
   New epics use draft keys `<FA-N>-PENDING` (e.g. `FA-3-PENDING`); `project_key` is the target
   Jira project if the user named it, else `PENDING`.

## Procedure

### Step 1 — Read and group
- Parse the PRD. Each **feature area (FA-N)** is the default epic boundary.
- Refine boundaries: if a feature area holds 15+ requirements or two clearly separable
  themes, split it into two epics. If two tiny areas are tightly coupled, consider merging.
- Keep MVP and Later requirements together under the same epic but note release on each;
  scope can be filtered later.
- Order the resulting epics to make dependency flow obvious when that helps readability.
  Foundational epics that unblock others should come earlier than dependent epics.
- Run a **lifecycle completeness** pass while grouping:
  - For every capability, ask what prerequisite actors, entities, or states it depends on.
  - For every prerequisite actor or entity, make its lifecycle explicit: created by another
    requirement, supplied externally, or intentionally out of scope.
  - For every persisted core entity or state, confirm which requirement creates it before
    other requirements consume it.
  - If a requirement assumes an existing actor, entity, or state and no requirement creates
    it, either add the missing requirement, split the epic, or document the assumption clearly.

### Step 2 — Write each epic (use `templates/epic.md.tmpl`)
Each epic needs:
- **Summary** — short, outcome-focused ("Curriculum ingestion & retrieval", not "FA-3").
- **Description** — the problem this epic solves, the domain context behind it, the primary
  users/actors, and the value it delivers. Write it so someone who has not read the PRD can
  still understand the feature area.
- **Functional scope** — the concrete capabilities and workflows the epic must deliver,
  including key inputs/outputs, integrations, data touched, and any notable edge cases or
  non-goals.
- **Implementation guidance / dependency order** — the recommended build sequence for the
  stories inside the epic. Call out foundation-first work, prerequisite data models or
  services, integration points, and which pieces should come before others when dependencies
  exist.
- **Goal / definition of done** — when is this epic complete.
- **Covered requirements** — the explicit list of FR/NFR IDs rolled into it (traceability).
- **Release** — MVP or Later (or "mixed", with the MVP subset listed).
- **Labels** — feature-area code + release, for filtering in Jira.

### Step 3 — Write the map and hand off
Write `epics.md` and `epic-map.json` (draft keys). Tell the user: N epics planned, every PRD
requirement lands in exactly one epic, and the next steps are `sdlc-tracker-sync` (publish the
epics to Jira) and then `sdlc-plan-stories-write` for each epic.

## Boundary heuristics (quick reference)
- One feature area → usually one epic.
- An epic should be deliverable in a few sprints; if it's clearly a quarter of work, split.
- Cross-cutting NFRs (security, compliance, accessibility) that touch many areas can become
  their own epic (e.g. "Compliance & data protection") rather than being scattered.
- Every requirement must land in exactly one epic. No orphans, no duplicates — check the map.
- Epic descriptions should be self-contained: if a Jira reader sees only the epic issue, they
  should still understand the feature, the users, the implementation shape, and the order in
  which it should be built.
- If the epic has an internal dependency chain, document the preferred implementation order in
  the epic body rather than leaving it implicit.
- If an epic contains a flow that depends on an actor, entity, or state already existing, make
  that dependency explicit in the epic body and/or split out the prerequisite story instead of
  burying it inside another requirement.

## Reference files
- `templates/epic.md.tmpl` — epic structure.
- `templates/epic-map.schema.json` — the shape of the traceability map.
- `examples/` — epics decomposed from the sample PRD, with the resulting map.
