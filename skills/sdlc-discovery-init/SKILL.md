---
name: sdlc-discovery-init
description: >
  FIRST step of the Discovery phase. Bootstraps the BheemBhai convention onto a freshly-acquired
  brownfield repo that has none of it: detects the service topology (single service vs. multiple),
  creates the docs/discovery/ working area, and writes a minimal AGENTS.md Project Layout table so
  that downstream discovery skills (and later the delivery skills) have a layout to resolve paths
  from. Use this once, at the very start of onboarding a repo, before any other discovery skill.
  Trigger on "onboard this repo", "start discovery", "acquire knowledge for this codebase", or the
  beginning of the discovery workflow. It CREATES structure only; it does not analyze code.
compatibility: >
  Tool-agnostic. Reads the raw repo: top-level layout, orchestration files (docker-compose,
  Dockerfiles), monorepo markers, and nested manifests. No MCP. Writes AGENTS.md (if absent) and
  the docs/discovery/ skeleton. Output seeds every later step.
model: low   # default tier (high/medium/low); the workflow step's model: overrides it

---

# sdlc-discovery-init

Artifact paths: Discovery runs on a freshly-acquired brownfield repo, so the BheemBhai convention
usually does NOT exist yet. THIS skill is the one that creates it. Seed the layout from this
skill's `templates/project-layout.md.tmpl`. If an `AGENTS.md` with a Project Layout table already
exists (a re-run, or a repo already onboarded), do NOT overwrite it — read it and confirm the
discovery rows are present, adding only what's missing. This skill's own `templates/`/`examples/` stay in the
skill folder, never under `docs/`.

Cost & context: Runs at the frontmatter model tier. Read the repo's TOP-LEVEL structure, the
**orchestration files** (`docker-compose.yml`/`compose.yaml` and any Dockerfiles), monorepo
markers (root package.json "workspaces", pnpm-workspace.yaml, lerna.json, nx.json, go.work), and
any nested manifests. Read these files' STRUCTURE only — do NOT read application source. Service
*analysis* is the job of the later per-service skills.

The "set the stage" step. A brownfield repo has only code — no `AGENTS.md`, no `docs/` convention,
none of the structure the rest of BheemBhai assumes. Discovery is the bridge that turns a raw repo
into a BheemBhai-shaped one, and this is its first act: establish where discovery will write, and
how many services it must cover. Everything downstream resolves paths from what this writes.

## Input it expects
- The raw checked-out repo (code only; no BheemBhai convention assumed).
- `references/service-boundary-heuristics.md` — **read this first.** Defines what counts as a
  service (a separately deployable/runnable unit, not merely "a dir with a manifest"), which
  files reveal boundaries, and how to tell a first-party service from an infra dependency or a
  component of another service.
- `templates/project-layout.md.tmpl` — the default layout to seed from.

## Output it produces
Two things:
1. `AGENTS.md` at the repo root (created if absent) containing the **Project Layout** table seeded
   from the default layout, INCLUDING the discovery rows (docs/discovery/ root, per-service folder,
   system folder). This is what makes downstream path-resolution work — and what later lets the
   delivery skills treat this repo as a normal BheemBhai project.
2. The `docs/discovery/` skeleton and a `services.md` manifest listing the detected **first-party
   services only** — one entry per service with a filesystem-safe `id`, its `root`, its `manifest`
   (or `none` for a Dockerfile-only service), and `confidence` + `source` (plus a `note` when the
   call is inferred). Infra dependencies and components of another service are described in
   `summary`, not listed as entries. The parent workflow's fan-out node reads this file (the
   `bheembhai:foreach` block, `$.services[*]`), so the entry ids become the `docs/discovery/<id>/`
   folders and the child runs — one child run per service. From `templates/services.md.tmpl`.

## Procedure
Step 1 — Detect topology. Apply `references/service-boundary-heuristics.md`. A service is a
  **separately deployable/runnable unit**, NOT "any directory with a manifest" — detecting only
  manifest-bearing dirs is the classic under-count (it misses Dockerfile-only sidecars and
  workers that reuse the main image). Read topology sources in priority order:
  1. **`docker-compose.yml` / `compose.yaml`** (+ overrides) — parse `services:`. A compose entry
     with a **`build:`** stanza on a local context is a first-party service; an **`image:`-only**
     entry (postgres, redis, minio, ollama, langfuse, mailhog, …) is an **infra dependency**, not
     a service — never emit those as `services:`.
  2. **Dockerfiles** anywhere (`Dockerfile`, `Dockerfile.*`, `*/Dockerfile`) — each distinct build
     context is a candidate service root.
  3. **Monorepo markers** — root `package.json` `workspaces`, `pnpm-workspace.yaml`, `lerna.json`,
     `nx.json`, `turbo.json`, `go.work`.
  4. **Nested manifests** — a manifest in a subdir distinct from the root.
  5. **Process declarations** — `Procfile`, systemd `*.service`, k8s `kind: Deployment`.
  A directory that runs **inside another service's process or on another service's image** (no
  Dockerfile, no manifest of its own — e.g. a Prefect `flows.py` run by the shared worker on the
  api image) is a **component of that service**, not a service; note it in `summary`, do not emit
  it as a `services:` entry. `topology: single` ONLY when the sole signal is one root manifest
  with no compose-build / Dockerfile / workspace markers.
  Record each detected service with a short, filesystem-safe `<SERVICE>` id (dir name, sanitized),
  its `root`, its `manifest` (or `none` for a Dockerfile-only service), and a `confidence` +
  `source`. Where the service/component or service-count call is a judgment, mark `inferred` with
  a `note` — surface it at the Step 4 checkpoint, never collapse it silently.
Step 2 — Write/confirm AGENTS.md. If absent, create it with the Project Layout table from
  `templates/project-layout.md.tmpl` (including discovery rows). If present, read it and add any
  missing discovery rows only — never clobber an existing layout.
Step 3 — Create docs/discovery/ and write services.md in the `bheembhai:foreach` shape: one
  entry per service with a filesystem-safe `id`, its `root`, and its `manifest`.
Step 4 — Present services.md + the AGENTS.md layout for review. This is a checkpoint: the detected
  service list drives the entire fan-out, so a wrong topology (missed a service, split one wrongly)
  is cheapest to correct here.

## Output format
`services.md` per `templates/services.md.tmpl`: a YAML `bheembhai:foreach` block (header comment,
then the `services:` list) — the fan-out node parses exactly this. AGENTS.md uses the standard
Project Layout table from `templates/project-layout.md.tmpl`. See `examples/services-LEARN-portal.md`.

## Hand-off
The `services.md` service list is the fan-out input: the parent workflow's `foreach` node reads it
from the run branch and starts ONE child run per entry (sdlc-discovery-stack-detect → … → per service),
passing the entry to each child as `ITEM` in its run context. The AGENTS.md layout gives every
downstream skill its write paths. If only one service: the chain runs once with that service.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: Services you are unsure of stay in `services.md`, marked `inferred` or `uncertain`. Never invent a service you cannot evidence.
