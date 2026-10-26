---
name: sdlc-discovery-structure-map
description: >
  Map where the important code lives in one service — the directory layout and what each key area
  is for (routes, controllers, models, config, tests, entrypoint) — into a reviewable structure
  note the feature-dev agent reads to orient fast. Use during Discovery AFTER sdlc-discovery-stack-detect
  (reads the selected pack'"'"'s locations). Trigger on "map the structure", "where does code live",
  "lay out this service". RECORDS the layout with source pointers; it is an orientation index.
compatibility: >
  Tool-agnostic. Reads docs/discovery/<SERVICE>/stack.md and the pack it names. No MCP. Output is a
  Markdown structure note consumed by the other per-service skills and the feature agent.
complexity: low   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-structure-map

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the BheemBhai convention is created by sdlc-discovery-init, not assumed. Use the default layout in `references/_SHARED-project-layout.md` (prefer an existing `AGENTS.md` Project Layout table only if a prior run wrote one). This skill reads SOURCE CODE and its own upstream discovery artifacts under `docs/discovery/` — never the canonical project docs (`docs/architecture.md` etc.), which are discovery OUTPUT produced by sdlc-discovery-consolidate. This skill's own `templates/`/`examples/` stay in the skill folder, never under `docs/`.

Cost & context: Runs at the frontmatter complexity tier. Read `stack.md` and the pack'"'"'s `locations.*`,
then LIST (not read) those directories to confirm presence and note what'"'"'s there. Do not read source
files — this maps where things are, not what they do.

The "where is everything" for one service. The fastest orientation a feature agent can get: given
the framework, confirm where each conventional area actually is in THIS repo (conventions bend in
real codebases), so later reads go straight to the right place.

## Input it expects
- The checked-out service codebase.
- `docs/discovery/<SERVICE>/stack.md` (its `stack_pack`).
- Shared: `references/_SHARED-discovery-contract.md`. The selected pack's data (locations, patterns, commands, risk_hints, glossary_hints) is embedded in `stack.md` under `embedded_pack:` — read it there; the pack files themselves live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/<SERVICE>/structure-map.md` (create folder if absent). From
`templates/structure-map.md.tmpl`, presented for review.

## Procedure
Step 1 — Read `stack.md`; take `stack_pack`. `none` → infer from top-level dirs.
Step 2 — From the pack, load `locations.*` (routes, controllers, models, migrations, config, tests,
  entrypoint). For each, confirm whether that path actually exists in the repo (try the candidate
  list in order; real repos deviate).
Step 3 — Record each area: its real path (or "not found at conventional location — actual: X"),
  a one-line purpose, each with `source` (the directory). Flag conventional-location misses as
  `inferred` with the actual path you found.
Step 4 — Note any significant non-conventional top-level dirs (a `lib/`, `internal/`, `packages/`)
  worth the feature agent knowing about.
Step 5 — Write and present.

## Output format
Per `references/_SHARED-discovery-contract.md`: an areas table, each with path + purpose + source. See
`examples/structure-map-LEARN-portal.md`.
