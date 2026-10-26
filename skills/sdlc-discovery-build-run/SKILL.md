---
name: sdlc-discovery-build-run
description: >
  Extract how to build, run, and test one service locally — the commands, required services,
  environment variables, and entrypoint — into a reviewable sdlc-discovery-build-run note the feature-dev agent
  reads so it can actually run the project. Use during Discovery AFTER sdlc-discovery-stack-detect (reads the
  pack for the stack's standard commands). Trigger on "how do I run this", "what's the build/test
  command", "get this running locally", or continuing discovery. RECORDS what is configured, with
  source pointers; it does not fix broken setups.
compatibility: >
  Tool-agnostic. Reads docs/discovery/<SERVICE>/stack.md and the pack it names, plus the service's
  own manifest/compose/env files. No MCP. Output is a Markdown sdlc-discovery-build-run note — the first thing a
  feature agent needs, since architecture docs don't help if the project won't start.
complexity: low   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-build-run

Artifact paths: Discovery runs on a freshly-acquired brownfield repo, so the BheemBhai convention usually does NOT exist yet — there is typically no `AGENTS.md` and no `docs/` layout (discovery is what CREATES them). Therefore: use the **default layout** in `references/_SHARED-project-layout.md` and CREATE paths as you write; only if a prior discovery run already wrote an `AGENTS.md` Project Layout table should you prefer it. Discovery artifacts are created under `docs/discovery/` (per-service notes in `docs/discovery/<SERVICE>/`, system synthesis in `docs/discovery/_system/`). This skill reads only SOURCE CODE and its own upstream discovery artifacts — never the canonical project docs (`docs/architecture.md` etc.), which are discovery's OUTPUT, produced by `sdlc-discovery-consolidate` at the end of the phase, not its input. This skill's own `templates/`/`examples/` stay in the skill folder, never under `docs/`.

Cost & context: Runs at the frontmatter complexity tier. Read `stack.md`, the pack's `commands` and
`locations.env_example`/`entrypoint`, plus the service's manifest scripts, a compose file if
present, and `.env.example`. Do not read source code — this is about the run surface, not the app.

The "how to run it" for one service. Architecture docs are useless if a feature agent can't start
the project. This captures the real commands (preferring the project's own scripts over the pack's
generic defaults), the backing services it needs, and the env it expects. Review checkpoint: a
wrong run command or missed required service blocks every future feature at the first step.

## Input it expects
- The checked-out service codebase.
- The run context's `ITEM` — the ONE service this child run owns. `ITEM.id` IS the
  `<SERVICE>` below and `ITEM.root` its path. Sibling services are other child runs on the
  same branch: never read their artifacts as your input and never write under
  `docs/discovery/<OTHER>/` — a child that writes its siblings' paths collides with their
  commits (live 2026-10-17: one build-run child wrote all eight services' notes and the
  push-rebase conflicted on every retry).
- `docs/discovery/<SERVICE>/stack.md` (its `stack_pack`).
- Shared: `references/_SHARED-discovery-contract.md`. The selected pack's data (locations, patterns, commands, risk_hints, glossary_hints) is embedded in `stack.md` under `embedded_pack:` — read it there; the pack files themselves live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/<SERVICE>/build-run.md` (resolve via `AGENTS.md`), where `<SERVICE>` is
`ITEM.id` — this service ONLY; never another service's `build-run.md`. From
`templates/build-run.md.tmpl`, presented for review.

## Procedure
Step 1 — Read `stack.md`; take `stack_pack`. `none` → infer from manifest/compose only.
Step 2 — From the pack, load `commands` (install/test/run/migrate) as the stack defaults.
Step 3 — OVERRIDE defaults with the project's own: manifest scripts (package.json "scripts",
  composer "scripts", pyproject tool configs), a Makefile, a justfile. The project's own command
  wins over the pack default — record which you used and its source.
Step 4 — Backing services: read a docker-compose.yml / compose.yaml if present; list the services
  (db, cache, queue, object store) the app needs to run, each with source.
Step 5 — Environment: read `.env.example` (pack `locations.env_example`); list the required vars
  (names only, never values) and flag any that look secret.
Step 6 — Entrypoint: record the app entrypoint (pack `locations.entrypoint`), confirmed present.
Step 7 — Write and present.

## Output format
Per `references/_SHARED-discovery-contract.md`. Commands, backing services, and env vars — each sourced. See
`examples/build-run-LEARN-portal.md`.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: The service lacks a command (for example, no tests). Record it as absent; don't invent one.
