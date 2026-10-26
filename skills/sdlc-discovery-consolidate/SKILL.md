---
name: sdlc-discovery-consolidate
description: >
  FINAL step of the Discovery phase. Compose the per-service and system discovery artifacts into
  the canonical project docs that BheemBhai's delivery skills read — docs/architecture.md,
  docs/tech-stack.md, docs/data-model.md, docs/api-contracts/, docs/testing-strategy.md — so that
  after discovery, a brownfield repo looks greenfield to story-design/implement. Use once, after
  every other discovery skill has run. Trigger on "finish discovery", "produce the project docs",
  "consolidate discovery". It CREATES the canonical docs AND finalizes AGENTS.md.
compatibility: >
  Tool-agnostic. Reads docs/discovery/ (all evidence) and reuses the delivery skills' templates
  (sdlc-arch-design's architecture.md.tmpl, ADR.md.tmpl; the project's testing-strategy shape). Writes
  the canonical docs/ artifacts. Output is what delivery consumes.
complexity: high   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-consolidate

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the convention was created by
sdlc-discovery-init. Use the default layout in `references/_SHARED-project-layout.md` to resolve WHERE the canonical
docs go (docs/architecture.md, docs/tech-stack.md, docs/data-model.md, docs/api-contracts/,
docs/testing-strategy.md). This skill READS the discovery evidence under docs/discovery/ and WRITES
the canonical project docs. It reuses the delivery skills' own templates where they exist (e.g.
sdlc-arch-design's `templates/architecture.md.tmpl`, `templates/ADR.md.tmpl`) so the output is shaped
identically to greenfield. Own `templates/`/`examples/` stay in the skill folder.

Cost & context: Runs at the frontmatter complexity tier (strong — these docs drive every future
feature). Read the distilled discovery artifacts, not source. Compose, don't re-discover.

The capstone. The evidence layer (docs/discovery/) is the SOURCE-CITED, CONFIDENCE-TAGGED truth and
stays as the permanent audit trail. This step produces the CANONICAL layer: the greenfield-shaped
docs delivery reads. After this, sdlc-deliver-story-design reads docs/architecture.md and neither knows nor cares
that discovery reverse-engineered it.

## The honesty rule (critical)

The canonical docs are a LOSSY consolidation — they drop per-claim confidence tags and source lines
to match the greenfield shape delivery expects. That means a canonical doc can state as plain prose
what the evidence flagged `uncertain`. To preserve discovery's honesty:
- Every canonical doc Carries a header banner:
  `> ⚠ Reverse-engineered by BheemBhai Discovery from the codebase on <DATE>. This is inferred from
  code, not human-authored design. Per-claim provenance and confidence: see docs/discovery/.`
- Any claim the evidence marked `uncertain` is either OMITTED from the canonical doc or written with
  an explicit hedge — never laundered into confident prose.
- This skill does not INVENT to fill a greenfield template section the evidence can't support; it
  writes "Not determinable from the codebase — see docs/discovery/<...>" for that section.

## Input it expects
- The complete discovery evidence: `docs/discovery/services.md`, every `docs/discovery/<SERVICE>/*.md`,
  and every `docs/discovery/_system/*.md`.
- The delivery skills' templates to match shape (tech-design/prd templates), where present.

## Output it produces (the canonical docs delivery reads)
Resolve each path from the layout table:
1. `docs/architecture.md` — from `_system/architecture.md` + integration-map, written as a full
   greenfield-style **Software Architecture Document** using this skill's
   `templates/architecture-SAD.md.tmpl` (all SDLC sections: Introduction, Goals & Constraints,
   Stakeholders, Context, Significant Requirements, Views [logical/runtime/development/deployment/
   data], Interfaces, Cross-Cutting, Decisions, Quality Realization, Risks, Appendices). It reads
   as a settled greenfield SAD; the provenance banner + Appendix A carry the recovered-from-code
   truth. See `examples/architecture-SAD-LEARN-portal.md`.
2. `docs/tech-stack.md` — from per-service `stack.md` + `dependency-inventory.md`.
3. `docs/data-model.md` — from per-service `data-model.md` (merged across services).
4. `docs/api-contracts/<service>.openapi.yaml` — from per-service `api-surface.md` (emit OpenAPI).
5. `docs/testing-strategy.md` — from per-service `test-coverage-map.md` (what exists + the gaps).
6. `docs/adr/` — OPTIONAL: where discovery inferred a load-bearing decision (e.g. "auth is
   cookie+JWT"), write an ADR marked as reverse-engineered, so the decision is recorded.
7. Finalize `AGENTS.md` — ensure its Project Layout table points at all the above.
Each canonical doc carries the provenance banner.

## Procedure
Step 1 — Read all discovery evidence (services.md, per-service, _system).
Step 2 — For each canonical doc, compose from the corresponding evidence, in the matching delivery
  template's shape (for `docs/architecture.md`, the full SAD template above). Carry forward only
  claims the evidence supports; apply the honesty rule to `uncertain` items.
Step 2a — **Write in Simplified Technical English.** These are technical documents a reader must
  understand with no follow-up questions, so write them in ASD-STE100. Apply the rules in
  `references/ste-rules.md` (bundled in this skill) WHILE you write each section — one meaning per
  word, active voice, simple tenses, one instruction or claim per sentence, short sentences, lists
  for sequences, plain words. Do not write a draft and then rewrite it. Never drop a fact,
  condition, or hedge to shorten a sentence, and never change code, paths, numbers, or quoted text.
Step 2b — **Draw the architecture diagrams.** `docs/architecture.md` must carry the five required
  Mermaid diagrams (System context §4, Component §6.1, Runtime sequence §6.2, Deployment §6.4,
  Data ER §6.5). Build each ONLY from the discovery evidence — the graphify graph, the
  integration-map edges, the data-model — never freehand. Draw observed edges solid and
  inferred/planned edges dashed, and caption each with its source artifact. Follow
  `references/diagram-conventions.md` (format, evidence source, templates, reserved-word caveat).
  Confirm each diagram parses before you present the doc.
Step 3 — Add the provenance banner to each doc.
Step 4 — Write the docs to their layout-table paths (create dirs as needed). Do NOT delete the
  docs/discovery/ evidence — it is the permanent provenance layer.
Step 5 — Present ALL canonical docs together for review. This is the hardest gate in the phase: these
  docs become the trusted basis for every future feature, so they warrant explicit human approval
  before the project is considered onboarded. State clearly that approval here ratifies the
  reverse-engineered knowledge as the project's working truth.

## Output format
Each canonical doc matches its delivery-skill template shape, plus the provenance banner. The
evidence layer is untouched. See `examples/consolidate-manifest-LEARN-portal.md` for the mapping.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: The evidence notes contradict each other in a way only a human can settle, for example two services claimed to own the same data. Record the contradiction; don't pick a side in the canonical docs.
