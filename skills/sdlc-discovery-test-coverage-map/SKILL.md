---
name: sdlc-discovery-test-coverage-map
description: >
  Map what is tested in one service today — which test files exist, at which layers (unit /
  integration / e2e), what they cover, and how they run — into a reviewable note so a feature
  knows what safety net exists and where there is none. Use during Discovery AFTER
  sdlc-discovery-stack-detect. Trigger on "what's tested", "map test coverage", "which areas have no
  tests". RECORDS the existing tests with sources; it does not run them or judge sufficiency.
compatibility: >
  Tool-agnostic. Reads docs/discovery/<SERVICE>/stack.md and the pack'"'"'s test locations + run
  commands. No MCP. Output feeds sdlc-discovery-risk-register (coverage gaps) and, in delivery,
  sdlc-deliver-tests-write (so new tests match existing conventions).
complexity: low   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-test-coverage-map

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the BheemBhai convention is created by sdlc-discovery-init, not assumed. Use the default layout in `references/_SHARED-project-layout.md` (prefer an existing `AGENTS.md` only if a prior run wrote one). This skill reads SOURCE CODE and its own upstream discovery artifacts under `docs/discovery/` — never the canonical project docs, which are discovery OUTPUT. This skill's own `templates/`/`examples/` stay in the skill folder, never under `docs/`.

Cost & context: Runs at the frontmatter complexity tier. List the test directories (pack
`locations.tests`) and read test file NAMES and the first docstring/describe line to infer what
each covers — do not read full test bodies. Do NOT run the suite (that is sdlc-deliver-tests-verify in delivery).

The "what safety net exists" for one service. A feature that changes code with no tests is far
riskier than one covered by them — so a feature agent needs to know, before it edits, which areas
have tests and which are bare. This is a MAP of existing tests, not a coverage percentage and not a
judgment of adequacy (the risk-register synthesis judges gaps).

## Input it expects
- The checked-out service codebase.
- `docs/discovery/<SERVICE>/stack.md` and `structure-map.md` (for test + source locations).
- Shared: `references/_SHARED-discovery-contract.md`. The selected pack's data (locations, patterns, commands, risk_hints, glossary_hints) is embedded in `stack.md` under `embedded_pack:` — read it there; the pack files themselves live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/<SERVICE>/test-coverage-map.md`. From `templates/test-coverage-map.md.tmpl`,
presented for review.

## Procedure
Step 1 — Read `stack.md`; take `stack_pack`. Load pack `locations.tests` and `commands.test`.
Step 2 — List test files by layer (unit / integration / e2e, per the repo's own split). For each,
  capture its name, the layer, and a one-line "what it covers" inferred from the filename + first
  docstring — each sourced to the file.
Step 3 — Map tests to the areas they exercise (which module/feature), using filename correspondence
  (test_passwords → auth/passwords). Mark these `inferred` (name-based) unless a docstring confirms.
Step 4 — Note how to run each layer (from pack `commands.test` + any layer-specific invocation
  the repo documents) and any layer that needs backing services to run.
Step 5 — Write and present. Do NOT compute a coverage number — absence of a test for an area is
  recorded as "no tests found for <area>", a fact, not a percentage.

## Output format
Per `references/_SHARED-discovery-contract.md`: tests by layer, area mapping, run commands — each sourced.
See `examples/test-coverage-map-LEARN-portal.md`.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: The service has no tests. Name every area as bare.
