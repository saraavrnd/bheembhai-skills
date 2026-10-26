---
name: sdlc-discovery-architecture
description: >
  Synthesize the system architecture — the components, their responsibilities, and how they fit — from the per-service discovery artifacts, into a system-level architecture note. Use during Discovery AFTER the per-service and integration-map skills. Trigger on "describe the architecture", "how is this system structured", "what are the components". JUDGES structure from evidence; every architectural claim traces to per-service findings or code.
compatibility: >
  Tool-agnostic. Reads the per-service discovery artifacts (and targeted source where needed). No
  MCP required. Output is a system-level discovery artifact under docs/discovery/_system/.
complexity: high   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-architecture

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the convention is created by sdlc-discovery-init. Use the default layout in `references/_SHARED-project-layout.md`. This is a SYSTEM-LEVEL synthesis skill: it reads the per-service discovery artifacts for every service in `docs/discovery/services.md` and writes to `docs/discovery/_system/`. It reads discovery artifacts and source only — never the canonical project docs, which are discovery OUTPUT. Own `templates/`/`examples/` stay in the skill folder.

Cost & context: Runs at the frontmatter complexity tier. Read the per-service artifacts (already
distilled) as primary input; touch source only to confirm a specific judgment. Don't re-read whole
services — the per-service discovery notes are why they exist.

The "how it is structured" for the whole system. sdlc-arch-design would decide this for a greenfield project; discovery reverse-engineers it for a brownfield one. It names the real components and their responsibilities and relationships — grounded in the per-service maps, not an idealized picture. Review checkpoint: this becomes the architecture every future feature reasons about, so a wrong structural claim misleads broadly. Distinguish what the code ACTUALLY does (observed) from architectural intent you infer (inferred).

## Input it expects
- `docs/discovery/services.md` and every service's `stack.md`, `structure-map.md`, `api-surface.md`, `data-model.md`.
- Every service's code graph (built by sdlc-discovery-graph with graphify), when present. Query it with
  graphify verbs against that service's store
  (`--graph docs/discovery/<SERVICE>/graphify-out/graph.json`) — do NOT read graph.json directly:
  `query "entry points"/"database access" [--context call]` for the dependency neighborhood,
  `explain "<hub>"` to inspect a load-bearing node (source, cluster, relationships),
  `path "<layerA>" "<layerB>"` to test whether one layer reaches another. At the SYSTEM layer, query
  every service's store and look for cross-service relationships (a monorepo boundary leak). Cite
  each returned relation's source reference as `observed`. graphify returns graph context, not a
  verdict, and sees static structure only: a missing `path` is not proof of no coupling (DI, dynamic
  routing), so coupling claims resting on absence are `inferred`. If no graph was built, fall back
  to reading `structure-map.md` and mark structural claims `inferred`. See sdlc-discovery-graph's
  `references/graphify-verbs.md`.
- `docs/discovery/_system/integration-map.md`.
- Shared: `references/_SHARED-discovery-contract.md`. Each service's selected pack data is embedded in that service's `stack.md` (`embedded_pack:`) — read it there; the pack files live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/_system/architecture.md`. From `templates/architecture.md.tmpl`, presented for review.

## Procedure
Step 1 — Read all per-service artifacts + the integration-map.
Step 2 — Identify components: each service, plus significant internal modules (from structure-maps) and shared datastores/queues (from integration-map). Give each a one-line responsibility grounded in its api-surface + structure.
Step 3 — Describe relationships from the integration-map edges — what depends on what, synchronous vs async.
Step 4 — Name the architectural style ONLY if the evidence supports it (monolith / service-oriented / layered) — and mark it `inferred`, citing the structural evidence. Do NOT assert a pattern (hexagonal, DDD, microservices) the code doesn't clearly show; absence of evidence → say so.
Step 5 — Note cross-cutting concerns visible in the evidence (auth approach, shared config, how services are deployed — from build-run).
Step 6 — Write and present. Keep it a map of the real system, not an idealized target.

## Output format
Write a standard SDLC document: numbered headers/sections from the template (Overview first, Evidence Notes last), with a trailing machine block kept in sync for downstream skills and consolidate. The structure is the template's; the evidence discipline stays INLINE — every factual line is tagged observed|inferred|uncertain and observed lines cite a source.
Write this artifact in Simplified Technical English: apply the rules in `references/ste-rules.md` (bundled in this skill) while you write (short active sentences, one claim each, plain words). This artifact is the evidence layer that `sdlc-discovery-consolidate` turns into the canonical greenfield Software Architecture Document (`docs/architecture.md`, from consolidate's `templates/architecture-SAD.md.tmpl`) — so keep each claim clear and atomic, which makes the STE rewrite at consolidation faithful. Keep the confidence tags and source pointers; STE governs the wording, not the evidence discipline.
Per `references/_SHARED-discovery-contract.md`: every claim carries confidence; observed claims cite a source
(a per-service artifact entry or a code line). Synthesis/judgment claims are `inferred` and say what
they were inferred from. See `examples/architecture.md` (worked example).
