---
name: sdlc-discovery-stack-detect
description: >
  Detect the tech stack / framework of one service from its code and select the matching
  knowledge pack, writing a thin, reviewable stack note that every downstream discovery skill
  reads. Use this as the FIRST step of the Discovery phase when onboarding a brownfield project,
  before any other discovery skill (sdlc-discovery-api-surface, sdlc-discovery-data-model, …). Trigger this even when the user
  just says "what is this built with", "detect the stack", "start discovery on this service", or
  names a service/repo to onboard. This skill DETECTS and records evidence; it does not analyze
  the API, data model, or architecture (later discovery skills do). It is the keystone — a wrong
  framework verdict poisons every later artifact, so it pauses for review before downstream
  discovery proceeds.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads the service's manifest (composer.json /
  package.json / pyproject.toml) and the bundled knowledge packs in this skill's
  references/knowledge-packs/. No MCP required. Output is a short Markdown stack note that EMBEDS
  the selected pack's locations/patterns/commands so downstream discovery skills need only read
  stack.md — they never read the pack files (each skill sees only its own folder at runtime).
complexity: low   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-stack-detect

Artifact paths: Discovery runs on a freshly-acquired brownfield repo, so the BheemBhai convention usually does NOT exist yet — there is typically no `AGENTS.md` and no `docs/` layout (discovery is what CREATES them). Therefore: use the **default layout** in `references/_SHARED-project-layout.md` and CREATE paths as you write; only if a prior discovery run already wrote an `AGENTS.md` Project Layout table should you prefer it. Discovery artifacts are created under `docs/discovery/` (per-service notes in `docs/discovery/<SERVICE>/`, system synthesis in `docs/discovery/_system/`). This skill reads only SOURCE CODE and its own upstream discovery artifacts — never the canonical project docs (`docs/architecture.md` etc.), which are discovery's OUTPUT, produced by `sdlc-discovery-consolidate` at the end of the phase, not its input. This skill's own `templates/`/`examples/` stay in the skill folder, never under `docs/`.

Cost & context: This skill runs at the complexity tier in its frontmatter.
To avoid context bloat: read the service manifest and the pack
`detect:` blocks only when SELECTING — not whole packs, not whole source files — and locate by
glob/grep before reading any file. Once a pack is selected, read that one pack in full to embed
its locations/patterns/commands/caveats into `stack.md`. Don't re-read what's already in context.

**Why this skill owns the packs.** The knowledge packs live in THIS skill's
`references/knowledge-packs/` and nowhere else. BheemBhai runs each skill in its own container
that sees only that skill's folder, so a shared packs folder or another skill's folder is NOT
reachable at runtime. This skill is the only one that SELECTS a pack, so it is the only one that
needs the pack library — and it passes the selected pack's data forward by embedding it in
`stack.md`, which every downstream skill already reads.

The "what is this" for one service. Discovery reverse-engineers a brownfield codebase into the
knowledge a feature-dev agent needs. This is the first and most load-bearing step: it names the
framework and picks the knowledge pack that every downstream discovery skill uses to know where
things live. It is deliberately narrow and factual, and it is a review checkpoint — a wrong
framework verdict is cheap to correct here and expensive to correct after five more artifacts
were built on it. It pauses for approval before the downstream discovery steps proceed.

This step exists so that downstream discovery (sdlc-discovery-api-surface, sdlc-discovery-data-model, security-posture, …) can
go straight to the conventional location for a known framework (high-confidence, grep-able)
instead of inferring a framework's structure from scratch (slow, expensive, hallucination-prone).
When no framework is recognized, it says so — switching the chain into honest inference mode
rather than guessing.

## Input it expects

- The checked-out service codebase (the current git workspace).
- This skill's bundled references (inside the skill folder):
  - `references/_SHARED-discovery-contract.md` — the evidence discipline every discovery artifact obeys
    (observed / inferred / uncertain; source pointers; terse, machine-read for the feature agent).
  - `references/knowledge-packs/*.yaml` — one pack per known stack (bundled in THIS skill);
    `references/knowledge-packs/SCHEMA.md` describes the format and the `detect:` block.

## Output it produces

Two things:

1. One short file: `stack.md`, written to this service's discovery folder,
   `docs/discovery/<SERVICE>/stack.md` (create the folder if it doesn't exist; resolve the
   discovery root and `<SERVICE>` via `AGENTS.md`). From `templates/stack.md.tmpl`, presented for
   approval before downstream discovery continues. It is intentionally small.
2. The selected knowledge-pack id (its `stack_pack` value) AND the **embedded pack data** — the
   chosen pack's `locations`, `patterns`, `commands`, `risk_hints`, `glossary_hints`, and graph
   `dynamic_caveats`, copied into `stack.md` under an `embedded_pack:` block. This is the whole
   point of the hand-off: downstream skills read `stack.md` and get everything they need from the
   pack WITHOUT opening the pack files (which they cannot reach — they live only here). If
   `stack_pack: none`, there is no embedded pack and downstream skills run in inference mode. Same
   mechanism by which `sdlc-deliver-code-implement` reads `story-design.md`.

## Procedure

Step 1 — Locate and read the manifest
Find `composer.json` (PHP), `package.json` (Node), or `pyproject.toml`/`requirements.txt`
(Python). The manifest is the strongest, cheapest signal. Read only it.

Step 2 — Score each knowledge pack's `detect:` block
Walk `references/knowledge-packs/*.yaml`. For each: a `file_exists` near-proof (e.g. `artisan`,
`nest-cli.json`) weighs highest; a `dep_present` in the manifest is strong; a `glob_exists` is
supporting. The best-scoring pack wins.

Step 3 — Extract the framework version
Use the winning pack's `version_hint` to read the version from the manifest. Record it `observed`
with the manifest as source.

Step 4 — Decide the verdict, honestly (per `references/_SHARED-discovery-contract.md`)
- Confident — one pack clearly wins → `stack: <id>`, `confidence: observed`.
- Ambiguous — close scores or only weak signals → top candidate, `confidence: inferred`, with the
  alternatives in `note`.
- No match / framework-less → no pack scores → `stack: unknown`, `stack_pack: none`,
  `confidence: uncertain`. A valid, important outcome: it switches downstream discovery into
  inference mode. NEVER invent a framework you cannot evidence — a false "it's Laravel" is far
  worse than an honest "unrecognized".

Step 5 — Polyglot note
If the service mixes stacks (a PHP backend with a Node build toolchain), name the primary
application framework as `stack` and list the secondary toolchain in `note`.

Step 6 — Embed the selected pack into the hand-off
Read the WINNING pack in full and copy its `locations`, `patterns`, `commands`, `risk_hints`,
`glossary_hints`, and `graph.dynamic_caveats` into an `embedded_pack:` block in `stack.md`. This is
mandatory: downstream skills cannot read the pack files (they are bundled only in this skill, and
each skill's container sees only its own folder), so whatever a downstream skill needs from the
pack must be present here. Do NOT embed the `detect:` block (selection is done) — only the fields
downstream skills consume. If `stack_pack: none`, write `embedded_pack: none` and nothing more.

Step 7 — Write and present
Write `stack.md` to `docs/discovery/<SERVICE>/stack.md` per the contract and template, and present
it for approval. Emit the `stack_pack` value clearly; if `none`, say so loudly in `summary` so the
reviewer and downstream skills know discovery is in inference mode.

## Output format

Follow `references/_SHARED-discovery-contract.md`: YAML-structured `findings`, every entry carrying
`confidence` and its provenance (`source` when observed, `basis` when inferred) — PLUS the `embedded_pack:` block
carrying the selected pack's data for downstream skills. See `examples/stack-LEARN-portal.md` for a
worked example and `templates/stack.md.tmpl` for the shape.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: Nothing matches (`stack: unknown`, `stack_pack: none`, `confidence: uncertain`). This switches downstream skills to inference mode and is never an escalation or a failure.
