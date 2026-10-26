---
name: sdlc-discovery-risk-register
description: >
  Compile the risk and tech-debt register — fragile areas, missing test coverage, outdated/vulnerable deps, TODO/FIXME hotspots, and deviations — from the per-service and synthesis artifacts, so features know where to tread carefully. Use during Discovery near the end (it aggregates other findings). Trigger on "risks", "tech debt", "where are the landmines". AGGREGATES evidence-backed concerns; it does not invent risks.
compatibility: >
  Tool-agnostic. Reads the per-service discovery artifacts (and targeted source where needed). No
  MCP required. Output is a system-level discovery artifact under docs/discovery/_system/.
complexity: medium   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-risk-register

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the convention is created by sdlc-discovery-init. Use the default layout in `references/_SHARED-project-layout.md`. This is a SYSTEM-LEVEL synthesis skill: it reads the per-service discovery artifacts for every service in `docs/discovery/services.md` and writes to `docs/discovery/_system/`. It reads discovery artifacts and source only — never the canonical project docs, which are discovery OUTPUT. Own `templates/`/`examples/` stay in the skill folder.

Cost & context: Runs at the frontmatter complexity tier. Read the per-service artifacts (already
distilled) as primary input; touch source only to confirm a specific judgment. Don't re-read whole
services — the per-service discovery notes are why they exist.

The "where not to tread, or tread carefully" for the system. It aggregates risk signals the other skills surfaced — bare test areas (coverage-map), risky deps (dependency-inventory), security findings (security-posture), convention inconsistencies — plus a light pass for TODO/FIXME/HACK markers. Each risk is a real, cited concern with a severity, so a feature agent knows the landmines before stepping on them. No speculative risk without evidence.

## Input it expects
- All per-service artifacts, especially `test-coverage-map.md` and `dependency-inventory.md`.
- `docs/discovery/_system/security-posture.md` and `conventions.md`.
- A light grep for TODO/FIXME/HACK/XXX markers across source.
- Shared: `references/_SHARED-discovery-contract.md`. Each service's selected pack data is embedded in that service's `stack.md` (`embedded_pack:`) — read it there; the pack files live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/_system/risk-register.md`. From `templates/risk-register.md.tmpl`, presented for review.

## Procedure
Step 1 — Gather already-surfaced findings: coverage gaps (test-coverage-map 'no tests found'), risky deps (dependency-inventory flags), security findings (security-posture), convention inconsistencies.
Step 2 — Light debt scan: grep source for TODO/FIXME/HACK/XXX; cluster by area; cite representative instances (don't list every one).
Step 3 — Fragility signals from structure/size where visible (a god-file, a module with no tests AND high fan-in) — mark `inferred`, cite the signal.
Step 4 — Rate each risk severity (high/med/low) by impact × likelihood, with a one-line rationale. Every entry carries a source; a risk you can't evidence doesn't go in.
Step 5 — Write ordered by severity. Present.

## Output format
Write a standard SDLC document: numbered headers/sections from the template (Overview first, Evidence Notes last), with a trailing machine block kept in sync for downstream skills and consolidate. The structure is the template's; the evidence discipline stays INLINE — every factual line is tagged observed|inferred|uncertain and observed lines cite a source.
Per `references/_SHARED-discovery-contract.md`: every claim carries confidence; observed claims cite a source
(a per-service artifact entry or a code line). Synthesis/judgment claims are `inferred` and say what
they were inferred from. See `examples/risk-register.md` (worked example).
