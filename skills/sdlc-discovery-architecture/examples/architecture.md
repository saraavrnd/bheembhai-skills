<!-- Worked example: the SDLC-structured architecture.md for Learn Portal, built from the real
     per-service discovery artifacts + integration-map. Shows how the machine findings become a
     readable Architecture Overview while every line keeps its confidence tag and source. -->

---
artifact: architecture
generated: 2026-10-10
status: draft
confidence_summary: "12 observed, 2 inferred, 1 uncertain"
---

# Architecture Overview — Learn Portal

## 1. Overview
An early-scaffold, two-container system: **learn-portal** (one FastAPI "modular monolith" — 15
domain modules in a single process, 80 routes of which only 3 domains are implemented and 12 are
empty stubs, serving server-rendered Jinja2 HTML and a JSON API side by side) and
**embedding-service** (a 2-file FastAPI container on :8001 whose `/embed` and `/rerank` raise
`NotImplementedError`). The two first-party services have **zero runtime coupling today** — the
edges that matter (ingestion embed → embedding-service; api → Prefect) are both scaffold.

## 2. Context & Scope
- Scope: both first-party services (learn-portal, embedding-service) and their shared infra. _[observed — source: docs/discovery/services.md:15-25]_
- Synthesized from: the per-service `stack`/`structure-map`/`api-surface`/`data-model`/
  `test-coverage-map` artifacts and `_system/integration-map.md`. _[observed — source: docs/discovery/]_
- Topology: multi — 2 first-party services. _[observed — source: docs/discovery/services.md:15-25]_

## 3. Component Inventory
| Component | Kind | Responsibility | Confidence | Source |
|-----------|------|----------------|------------|--------|
| learn-portal | service | Primary FastAPI process; all 15 domain routers; 80 routes (40 HTML + 38 JSON + /health, /) | observed | docker-compose.yml:11-25; app/main.py:41-66 |
| embedding-service | service | Separately built FastAPI container :8001; only GET /health works | observed | docs/discovery/embedding-service/api-surface.md:20-41 |
| ingestion_pipeline | module (of learn-portal) | Prefect noop stub flow; not a service | observed | docs/discovery/services.md:20-24; ingestion_pipeline/flows.py:1-17 |
| app/auth | module | Identity & user lifecycle; roles admin/teacher/student; 27 routes | observed | structure-map.md:16-21; api-surface.md (auth) |
| app/school_admin | module | Academic structure (years, classes, sections, subjects); 37 routes | observed | structure-map.md:16-21; api-surface.md (school_admin) |
| app/ingestion | module | Chapter content + object storage; 14 routes | observed | structure-map.md:16-21; api-surface.md (ingestion) |
| 12 empty domain modules | module | Registered + include_router'd, 0 routes (AI/learning placeholder) | observed | app/main.py:45-66; stack.md:74-76 |
| Postgres (pgvector:pg17) | datastore | Only database: 14 tables + separate langfuse DB; test DB learn_portal_test | observed | data-model.md (14 entities); docker-compose.yml:56-71 |
| MinIO | datastore | Chapter file object storage (bucket learn-portal-uploads) | observed | minio_plugin.py:29-54; docker-compose.yml:99-108 |
| Redis | datastore (declared) | Cache-tier dep; only /health ping today, not a broker | observed | app/main.py:101-106 |
| Ollama / Langfuse | external (declared) | ai-profile; zero call sites in app/ | uncertain | integration-map.md:48-54 |

## 4. Component Relationships
| From | To | Via | Detail | Confidence | Source |
|------|----|----|--------|------------|--------|
| learn-portal | Postgres | sdk | SQLAlchemy 2.0 over psycopg3; only store | observed | app/db.py:8; app/main.py:123 |
| learn-portal | MinIO | sdk | Chapter file put/get/delete + presigned GET | observed | app/ingestion/router.py:443-448 |
| learn-portal | Redis | sdk | Cache ping, surfaced in /health | observed | app/main.py:101-106 |
| learn-portal | email provider | smtp/sdk/https | Invite/activation/reset tokens; SMTP/SendGrid/Brevo | observed | smtp_plugin.py:34; app/config.py:25-28 |
| learn-portal | embedding-service | http | **PLANNED, NOT WIRED** — embed step unimplemented; 0 grep hits | uncertain | ingestion_pipeline/flows.py:1-5 |
| learn-portal | prefect-server | http | No-op seam — trigger_parse submits no flow run | uncertain | app/ingestion/service.py:143-151 |
| prefect-worker | prefect-server | http | Poll of work pool; the only live service→service edge; repo flow NOT deployed | observed | docker-compose.yml:138-145 |
| langfuse | Postgres | sdk | Separate `langfuse` DB on shared server (compose self-describes as representative) | observed | docker-compose.yml:147-161 |

## 5. Data & Persistence
- Postgres is the single database — 14 tables (13 domain + `_scaffold_sanity_check`), app-generated
  string-UUID PKs, Alembic authoritative (14 revisions, single head), **no indexes declared**.
  _[observed — source: data-model.md:183-226]_
- MinIO holds chapter files; bucket created by one-shot `minio-init` before api starts.
  _[observed — source: docker-compose.yml:99-108]_
- No queue/broker anywhere — grep for lpush/publish/celery/kombu/broker returns 0.
  _[observed — source: integration-map.md:52]_

## 6. Cross-Cutting Concerns
### Authentication & Authorization
- One JWT+bcrypt scheme applied **per-route** via three guards (`require_role` Bearer,
  `require_role_cookie` HTML, `require_role_json` dual-mode + CSRF) — not global middleware;
  app-level routes carry no auth, and 5 of 24 web POSTs have no CSRF check as written.
  _[observed — source: api-surface.md:597-604, 22-35]_
### Configuration
- One pydantic-settings module; every setting defaulted (boots with no .env); compose overrides
  every connection value; `.env.example` is narrower than what `config.py` reads (JWT_SECRET_KEY,
  OBJECT_STORAGE_BUCKET, INGESTION_MAX_UPLOAD_MB, APP_BASE_URL absent).
  _[observed — source: app/config.py:1-35; build-run.md]_
### Data / Tenancy
- Per-deployment single tenancy (`school.singleton`); `school_id` is a plain String, no FK.
  _[observed — source: data-model.md:205-226]_
### Health & Observability
- Each service exposes GET /health (api reports db/cache/object_storage/secure_storage); beyond
  that, tracing is not wired (Langfuse declared, 0 call sites).
  _[observed — source: app/main.py:126-138]_
### Quality Gates
- 3 pytest layers (29 unit / 35 integration / 5 e2e) but **no CI config**, so none runs
  automatically; embedding-service has zero tests.
  _[observed — source: test-coverage-map.md:132-135]_

## 7. Deployment & Runtime
- docker-compose-first, two profiles: default (api + postgres + redis + minio + one-shot
  migrate/minio-init) and opt-in `ai` (embedding_service, ollama, prefect, langfuse, mailhog). The
  api image bakes migrations + alembic.ini; dev uses a read-only ./app mount + --reload.
  _[observed — source: docker-compose.yml:1-40; build-run.md:13-37]_
- Startup ordering (default): api waits on one-shot `migrate` and `minio-init` completing + redis
  started. _[observed — source: docker-compose.yml:34-54]_

## 8. Architecture Style
- learn-portal is a single-process **modular monolith** — one app assembling all 15 per-domain
  routers, one settings module, one ORM/session, server-rendered UI in-process; no per-domain
  process boundary, no separate SPA/API deployment.
  _[inferred — basis: structure-map.md:11-21, 36-38; app/main.py:1,41-66 (also the entrypoint's own
  "modular monolith" comment, which is not proof)]_
- At system level: **two independently built FastAPI containers with no runtime coupling** — not
  microservices/event-driven; asserting a richer topology would over-read scaffold intent.
  _[inferred — basis: services.md:15-25; integration-map.md:51-53]_
- The one concrete code pattern: a **loader + plugins/** shape in the shared support modules
  (email_service, object_storage, secure_storage) — provider selected by config.
  _[observed — source: app/email_service/loader.py; app/object_storage/plugins/minio_plugin.py]_

## 9. Gaps & Known Limitations
- The ingestion pipeline (parse → markdown → chunk → embed → index) exists only as a Prefect noop
  stub; no step implemented; embed's callee has no caller; flow not deployed to the worker.
  _[observed — source: ingestion_pipeline/flows.py:1-17; docker-compose.yml:138-145]_
- embedding-service is never exercised — opt-in, no tests, no config, no persistence, no manifest.
  _[observed — source: embedding-service/build-run.md:10-20; dependency-inventory.md (lockfile MISSING)]_
- The `ai` profile is declared but not operational end-to-end (worker runs no repo flow; Ollama
  needs a manual model pull; Langfuse block is representative-only).
  _[observed — source: docker-compose.yml:126-161; integration-map.md:43,54]_

## 10. Evidence Notes
- Tags: `observed` = cited to a per-service artifact or code `path:line`; `inferred` = synthesis,
  basis stated; `uncertain` = declared-only / not verifiable from code (the two scaffold seams,
  Ollama/Langfuse usage).
- Coverage: full across both first-party services; ai-profile runtime behavior is declared-only.

<!-- ── MACHINE BLOCK ── -->
```yaml machine
artifact: architecture
components:
  - { id: "learn-portal", kind: "service", confidence: observed, source: "docker-compose.yml:11-25" }
  - { id: "embedding-service", kind: "service", confidence: observed, source: "embedding-service/api-surface.md:20-41" }
  - { id: "postgres", kind: "datastore", confidence: observed, source: "learn-portal/data-model.md; docker-compose.yml:56-71" }
  - { id: "minio", kind: "datastore", confidence: observed, source: "docker-compose.yml:99-108" }
  - { id: "redis", kind: "datastore", confidence: observed, source: "app/main.py:101-106" }
  - { id: "prefect-server", kind: "external", confidence: observed, source: "docker-compose.yml:129-136" }
  - { id: "prefect-worker", kind: "external", confidence: observed, source: "docker-compose.yml:138-145" }
edges:
  - { from: "learn-portal", to: "postgres", via: "sdk", confidence: observed, source: "app/db.py:8" }
  - { from: "learn-portal", to: "minio", via: "sdk", confidence: observed, source: "app/ingestion/router.py:443-448" }
  - { from: "learn-portal", to: "embedding-service", via: "http", confidence: uncertain, source: "ingestion_pipeline/flows.py:1-5" }
  - { from: "prefect-worker", to: "prefect-server", via: "http", confidence: observed, source: "docker-compose.yml:138-145" }
style:
  - { claim: "modular monolith (learn-portal)", confidence: inferred, basis: "structure-map.md:11-21; app/main.py:41-66" }
  - { claim: "two uncoupled containers, not microservices", confidence: inferred, basis: "integration-map.md:51-53" }
gaps:
  - { claim: "ingestion pipeline is a noop stub", confidence: observed, source: "ingestion_pipeline/flows.py:1-17" }
  - { claim: "embedding-service never exercised", confidence: observed, source: "embedding-service/build-run.md:10-20" }
```
