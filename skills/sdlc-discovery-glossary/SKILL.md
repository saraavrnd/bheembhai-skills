---
name: sdlc-discovery-glossary
description: >
  Extract the domain vocabulary — the business nouns and terms the code uses — from entity/model names and the per-service artifacts, so a feature agent understands the domain language. Use during Discovery after data-model. Trigger on "domain glossary", "what do these terms mean", "domain vocabulary". RECORDS terms with where they appear; definitions are inferred from usage, flagged as such.
compatibility: >
  Tool-agnostic. Reads the per-service discovery artifacts (and targeted source where needed). No
  MCP required. Output is a system-level discovery artifact under docs/discovery/_system/.
complexity: medium   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-glossary

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the convention is created by sdlc-discovery-init. Use the default layout in `references/_SHARED-project-layout.md`. This is a SYSTEM-LEVEL synthesis skill: it reads the per-service discovery artifacts for every service in `docs/discovery/services.md` and writes to `docs/discovery/_system/`. It reads discovery artifacts and source only — never the canonical project docs, which are discovery OUTPUT. Own `templates/`/`examples/` stay in the skill folder.

Cost & context: Runs at the frontmatter complexity tier. Read the per-service artifacts (already
distilled) as primary input; touch source only to confirm a specific judgment. Don't re-read whole
services — the per-service discovery notes are why they exist.

The "what the words mean" for the system. The biggest comprehension barrier in an unfamiliar codebase is its domain vocabulary — the business nouns encoded as entities, routes, and modules. This gathers those terms and an inferred definition from how they're used, so a feature agent speaks the codebase's language. Definitions are `inferred` from usage (code rarely defines its terms) — cite where each term lives.

## Input it expects
- Every service's `data-model.md` (entities = domain nouns) and `structure-map.md` (module names).
- `api-surface.md` (route nouns).
- Shared: `references/_SHARED-discovery-contract.md`. Each service's selected pack data is embedded in that service's `stack.md` (`embedded_pack:`) — read it there; the pack files live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/_system/glossary.md`. From `templates/glossary.md.tmpl`, presented for review.

## Procedure
Step 1 — Collect candidate terms: entity/table names (data-model), module/feature names (structure-map), route path nouns (api-surface).
Step 2 — For each term, infer a short definition from how it's used — its columns/relationships (for entities), its endpoints (for features). Mark `inferred`, cite the source where it appears.
Step 3 — Note relationships between terms where the data-model shows them (a Student belongs to a School).
Step 4 — Keep it terse — a term, a one-line meaning, where it lives. Not an essay. Present.

## Output format
Write a standard SDLC document: numbered headers/sections from the template (Overview first, Evidence Notes last), with a trailing machine block kept in sync for downstream skills and consolidate. The structure is the template's; the evidence discipline stays INLINE — every factual line is tagged observed|inferred|uncertain and observed lines cite a source.
Per `references/_SHARED-discovery-contract.md`: every claim carries confidence; observed claims cite a source
(a per-service artifact entry or a code line). Synthesis/judgment claims are `inferred` and say what
they were inferred from. See `examples/glossary.md` (worked example).
