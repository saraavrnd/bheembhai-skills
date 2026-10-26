---
name: sdlc-discovery-data-model
description: >
  Extract the persistent data model of one service — entities/tables, their columns, keys,
  relationships, and the migrations that define them — into a reviewable sdlc-discovery-data-model note the
  feature-dev agent reads before touching the schema. Use during Discovery AFTER sdlc-discovery-stack-detect
  (reads the selected pack to locate models and migrations). Trigger on "map the data model",
  "what tables exist", "extract the schema", or continuing discovery. LOCATES and RECORDS schema
  with source pointers; it does not judge design, only reports what is persisted, as written.
compatibility: >
  Tool-agnostic. Reads docs/discovery/<SERVICE>/stack.md and the pack it names. No MCP. Output is
  a Markdown sdlc-discovery-data-model note consumed by later discovery and, in delivery, by sdlc-deliver-story-design when a
  feature adds a sdlc-discovery-data-model delta.
complexity: low   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-data-model

Artifact paths: Discovery runs on a freshly-acquired brownfield repo, so the BheemBhai convention usually does NOT exist yet — there is typically no `AGENTS.md` and no `docs/` layout (discovery is what CREATES them). Therefore: use the **default layout** in `references/_SHARED-project-layout.md` and CREATE paths as you write; only if a prior discovery run already wrote an `AGENTS.md` Project Layout table should you prefer it. Discovery artifacts are created under `docs/discovery/` (per-service notes in `docs/discovery/<SERVICE>/`, system synthesis in `docs/discovery/_system/`). This skill reads only SOURCE CODE and its own upstream discovery artifacts — never the canonical project docs (`docs/architecture.md` etc.), which are discovery's OUTPUT, produced by `sdlc-discovery-consolidate` at the end of the phase, not its input. This skill's own `templates/`/`examples/` stay in the skill folder, never under `docs/`.

Cost & context: Runs at the frontmatter complexity tier. Read `stack.md`, the pack's
`locations.models`/`locations.migrations`/`patterns.model` only; grep to locate entities and read
only the matched definitions — never whole trees. The migrations folder is the authoritative
schema source: prefer it over inferring columns from ORM classes.

The "what is persisted" for one service. The data model is usually the most load-bearing,
hardest-to-change part of a system, so a feature lives or dies by understanding it correctly. This
is a review checkpoint: a wrong column or missed relationship misleads every future feature that
touches storage.

## Input it expects
- The checked-out service codebase.
- `docs/discovery/<SERVICE>/stack.md` (its `stack_pack`).
- This service's code graph (built by sdlc-discovery-graph with graphify), when present. Query it with
  graphify verbs against `--graph docs/discovery/<SERVICE>/graphify-out/graph.json` — do NOT read
  graph.json directly: `explain "<model/entity node>"` returns its source, cluster and connected
  relationships (which modules use it); a model with no inbound relations is unused. Cite the
  returned source reference as `observed`. graphify sees static structure only, so "used by nothing"
  rests on absence and is `inferred`. Absent → read model files directly and mark usage claims
  `inferred`. See sdlc-discovery-graph's `references/graphify-verbs.md`.
- Shared: `references/_SHARED-discovery-contract.md`. The selected pack's data (locations, patterns, commands, risk_hints, glossary_hints) is embedded in `stack.md` under `embedded_pack:` — read it there; the pack files themselves live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/<SERVICE>/data-model.md` (resolve via `AGENTS.md`; create folder if absent). From
`templates/data-model.md.tmpl`, presented for review. An index into the schema, not a dump.

## Procedure
Step 1 — Read `stack.md`; take `stack_pack`. `none` → inference mode.
Step 2 — From the pack, load `locations.migrations`, `locations.models`, `patterns.model`.
Step 3 — Prefer migrations as the authoritative schema. Grep/list `locations.migrations`, read the
  create-table / column definitions. Record each table, its columns (name, type, nullable), PK,
  FKs, unique constraints — each with `source` (migration file:line).
Step 4 — Cross-check against ORM models (`locations.models`, `patterns.model`) for relationships
  and names the migrations don't make obvious. Where migrations and models disagree, record BOTH
  and flag `uncertain` — a drift is itself an important finding.
Step 5 — Capture relationships (FKs, join tables) as edges with sources.
Step 6 — Write and present.

## Inference mode (stack_pack: none)
No pack → grep broadly for schema signals (CREATE TABLE, ORM base classes, schema files). Record
`inferred` with the signal cited. State coverage is best-effort in `summary`.

## Output format
Per `references/_SHARED-discovery-contract.md`: entities with columns, each carrying `source`. Relationships
as sourced edges. See `examples/data-model-LEARN-portal.md`.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: The service has no data layer. Write an empty, honest note.
