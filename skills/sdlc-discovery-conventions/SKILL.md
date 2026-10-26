---
name: sdlc-discovery-conventions
description: >
  Extract the implicit house style and patterns of the codebase — naming, error handling, how this team structures and writes code — from the per-service artifacts and sampled source, so new features MATCH existing patterns rather than clash. Use during Discovery AFTER structure-map. Trigger on "coding conventions", "house style", "how does this team write code". RECORDS observed patterns with examples; conventions are inferred-from-repetition, flagged as such.
compatibility: >
  Tool-agnostic. Reads the per-service discovery artifacts (and targeted source where needed). No
  MCP required. Output is a system-level discovery artifact under docs/discovery/_system/.
complexity: medium   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-conventions

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the convention is created by sdlc-discovery-init. Use the default layout in `references/_SHARED-project-layout.md`. This is a SYSTEM-LEVEL synthesis skill: it reads the per-service discovery artifacts for every service in `docs/discovery/services.md` and writes to `docs/discovery/_system/`. It reads discovery artifacts and source only — never the canonical project docs, which are discovery OUTPUT. Own `templates/`/`examples/` stay in the skill folder.

Cost & context: Runs at the frontmatter complexity tier. Read the per-service artifacts (already
distilled) as primary input; touch source only to confirm a specific judgment. Don't re-read whole
services — the per-service discovery notes are why they exist.

The "how this team does things" for the codebase. A feature must match existing patterns or it clashes — and in brownfield these rules are UNWRITTEN. This infers them from repetition in the real code: naming, error-handling style, response shaping, test structure. Conventions are inherently `inferred` (a pattern seen 5 times is a convention; seen once is not) — say how many instances support each, and cite examples.

## Input it expects
- Every service's `structure-map.md` (where to sample) and `api-surface.md` (route/handler style).
- Sampled source — a few representative files per area, not the whole tree.
- Shared: `references/_SHARED-discovery-contract.md`. Each service's selected pack data is embedded in that service's `stack.md` (`embedded_pack:`) — read it there; the pack files live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/_system/conventions.md`. From `templates/conventions.md.tmpl`, presented for review.

## Procedure
Step 1 — From structure-maps, pick a few representative files per area (a couple of routers, models, tests).
Step 2 — Infer naming conventions (files, classes, functions, routes) from repetition — record the pattern + how many instances support it + an example source.
Step 3 — Error-handling style: how errors/exceptions are raised and surfaced (typed exceptions? HTTP error shape?) — cite examples.
Step 4 — Response/serialization style, config access style, logging style — each as an observed-pattern with example + instance count.
Step 5 — Test conventions: structure, naming, fixtures (from test-coverage-map + samples).
Step 6 — Mark each convention's strength: strong (consistent across the sample), weak (mixed — note the inconsistency, itself useful). Present. Every convention is `inferred`; the evidence is the instance list.

## Output format
Write a standard SDLC document: numbered headers/sections from the template (Overview first, Evidence Notes last), with a trailing machine block kept in sync for downstream skills and consolidate. The structure is the template's; the evidence discipline stays INLINE — every factual line is tagged observed|inferred|uncertain and observed lines cite a source.
Per `references/_SHARED-discovery-contract.md`: every claim carries confidence; observed claims cite a source
(a per-service artifact entry or a code line). Synthesis/judgment claims are `inferred` and say what
they were inferred from. See `examples/conventions.md` (worked example).
