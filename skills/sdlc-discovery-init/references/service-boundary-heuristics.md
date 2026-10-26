<!-- Flat reference read by sdlc-discovery-init. Defines what counts as a service boundary, which
     files reveal them, and how to tell a first-party service from an off-the-shelf infra
     dependency. No logic, no tool calls — just the rules the skill applies. -->

# Service-boundary heuristics

## What a service IS

A service is a **separately deployable or separately runnable unit** of the repo — something
that builds into its own image, or runs as its own process with its own entrypoint. It is NOT
"a directory," and it is NOT "anything with a language manifest." A manifest is one signal among
several, not the definition. Many real services (a Dockerfile-only sidecar, a worker that reuses
the main image) carry no manifest of their own, and missing them is the most common way to
under-count.

## Evidence that reveals a service (any ONE can be sufficient)

Score these; the strongest wins. A boundary needs at least one STRONG signal, or two SUPPORTING.

**Strong (own deployable/runnable unit):**
- A **`Dockerfile`** with its own build context (e.g. `embedding_service/Dockerfile`).
- A **compose service with a `build:` stanza** pointing at a local context
  (`build: ./embedding_service` or `build.context`). The compose file is the clearest statement
  in the repo of "what runs as a separate thing."
- A **language manifest** that defines its own app (`pyproject.toml`, `package.json`,
  `composer.json`, `go.mod`, `pom.xml`) at a distinct root.

**Supporting (needs corroboration):**
- A distinct **process entrypoint** declared somewhere that launches it: a `command:` /
  `entrypoint:` in compose, a `Procfile` line, a systemd `*.service`, a documented
  `uvicorn app.main:app` vs a different module.
- Its own exposed **port** in compose.
- Its own **CI job / deploy target** naming it as a separate build.

## What a service is NOT — infra dependencies

Off-the-shelf infrastructure pulled as a prebuilt image is a **dependency, not a first-party
service**. The test is: a compose entry with **`image:` pointing at a public registry and no
local `build:`** is infra. Record these as dependencies in the summary, never as `services:`
fan-out entries. Typical infra: postgres / pgvector, redis, minio, ollama, langfuse, mailhog,
rabbitmq, elasticsearch, prometheus, grafana, nginx, mailpit.

Rule of thumb: **`build:` with a local context → candidate service. `image:` only → infra.**

## What a service is NOT — a component of another service

A directory that runs **inside another service's process or on another service's image** is a
**component** of that service, not a service of its own. Signals that something is a component:
- No Dockerfile and no manifest of its own.
- It is imported by, or executed on, another service's image (e.g. a Prefect `flows.py` that the
  `prefect-worker` runs using the api image and the api codebase; a Celery task module the api
  worker loads; a CLI under the app package).
- It shares the main service's dependency set rather than declaring its own.

Call these out in the `summary` as "component of `<service>`" so the decision is visible and a
reviewer can override — but do NOT emit them as separate `services:` entries.

## Primary files to read for topology (in priority order)

1. **`docker-compose.yml` / `compose.yaml`** (and `docker-compose.*.yml` overrides) — parse
   `services:`, split `build:`-with-local-context (first-party) from `image:`-only (infra).
2. **Dockerfiles anywhere in the tree** — `Dockerfile`, `Dockerfile.*`, `*/Dockerfile`. Each
   distinct build context is a candidate service root.
3. **Monorepo workspace markers** — root `package.json` `workspaces`, `pnpm-workspace.yaml`,
   `lerna.json`, `nx.json`, `turbo.json`, Cargo workspaces, Go `go.work`.
4. **Nested language manifests** — a manifest in a subdirectory distinct from the root.
5. **Process declarations** — `Procfile`, systemd `*.service`, Kubernetes manifests
   (`kind: Deployment`), `supervisord.conf`.

Read these files' structure only — do NOT read application source. Service *analysis* is the job
of the later per-service skills.

## Confidence and ambiguity

- A boundary backed by a Dockerfile/compose-build or its own manifest → `confidence: observed`,
  with the exact marker in `source`.
- A boundary inferred from weaker/mixed signals, or a component/service judgment call → the top
  reading with `confidence: inferred` and a `note:` naming the alternative. **Surface the
  ambiguity; never silently collapse it.** A missed service is expensive to fix after five more
  artifacts were built on the wrong topology; a flagged "inferred" is cheap to correct at the
  review checkpoint.
- If nothing but the root manifest is found and no Dockerfile/compose/workspace markers exist →
  genuinely single service, `confidence: observed`.

## Worked application to a polyglot repo (Learn Portal)

Root has `pyproject.toml` (the FastAPI app), `docker-compose.yml`, and `infra/Dockerfile.api`.
`embedding_service/` has its own `Dockerfile` + `main.py` and a compose entry with
`build: ./embedding_service` on port 8001. `ingestion_pipeline/` has only `flows.py` and runs on
the shared `prefect-worker` (Prefect) using the api image/codebase.

- **learn-portal (api)** — service. Strong: root `pyproject.toml`, `infra/Dockerfile.api`,
  compose `api` with `build: .`. `observed`.
- **embedding_service** — service. Strong: own `Dockerfile`, compose `embedding_service` with
  `build: ./embedding_service`, own port 8001. `observed`.
- **ingestion_pipeline** — **component of learn-portal**, not a service: no Dockerfile, no
  manifest, runs on the shared prefect-worker image against the api codebase. Note it in summary.
- postgres / redis / minio / ollama / langfuse / mailhog — **infra** (`image:` only). Not
  services.

Result: `topology: multi`, **2 services** (`learn-portal`, `embedding_service`). The old
manifest-only rule saw 1, because it equated "service" with "has a manifest" and never read
compose or the Dockerfiles.
