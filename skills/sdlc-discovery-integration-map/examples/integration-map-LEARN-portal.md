<!-- Worked example: SDLC-structured integration-map.md for Learn Portal. Readable sections +
     machine block; every line tagged + sourced. This is the per-service synthesis the
     architecture skill reads. -->

---
artifact: integration-map
generated: 2026-10-10
status: draft
confidence_summary: "8 observed, 0 inferred, 1 uncertain"
---

# Integration & Interface Map — Learn Portal

## 1. Overview
Two first-party FastAPI services with **no runtime coupling today**. learn-portal talks
synchronously to Postgres, MinIO, Redis and an email provider; the only live service→service edge
in the deployment is prefect-worker → prefect-server. The embed and Prefect seams are scaffold.

## 2. System Context
- First-party services: learn-portal, embedding-service. _[observed — source: docs/discovery/services.md:15-25]_
- External systems / infra: Postgres, MinIO, Redis, email provider (SMTP/SendGrid/Brevo), Ollama, Langfuse, Prefect. _[observed — source: docker-compose.yml:56-161]_

## 3. Nodes (Inventory)
| Node | Kind | Role | Confidence | Source |
|------|------|------|------------|--------|
| learn-portal | service | FastAPI app, all domains | observed | docker-compose.yml:11-25 |
| embedding-service | service | :8001, stubbed | observed | embedding-service/api-surface.md:20-41 |
| postgres | datastore | only DB (+ langfuse DB) | observed | docker-compose.yml:56-71 |
| minio | datastore | chapter files | observed | docker-compose.yml:99-108 |
| redis | datastore | cache (ping only) | observed | app/main.py:101-106 |
| prefect-server | external-api | flow orchestration | observed | docker-compose.yml:129-136 |
| prefect-worker | service | work-pool poller on the api image | observed | docker-compose.yml:138-145 |

## 4. Interfaces & Integrations
| From | To | Via | Interface / Detail | Confidence | Source |
|------|----|----|--------------------|------------|--------|
| learn-portal | postgres | sdk | SQLAlchemy 2.0 / psycopg3 | observed | app/db.py:8 |
| learn-portal | minio | sdk | put/get/delete + presigned GET | observed | app/ingestion/router.py:443-448 |
| learn-portal | redis | sdk | /health cache ping | observed | app/main.py:101-106 |
| learn-portal | email provider | smtp/sdk/https | invite/activation/reset tokens | observed | smtp_plugin.py:34 |
| learn-portal | embedding-service | http | PLANNED, NOT WIRED (embed step unimplemented) | uncertain | ingestion_pipeline/flows.py:1-5 |
| learn-portal | prefect-server | http | no-op seam (no flow submitted) | uncertain | app/ingestion/service.py:143-151 |
| prefect-worker | prefect-server | http | work-pool poll — only live svc→svc edge | observed | docker-compose.yml:138-145 |

## 5. External Dependencies
| Service | External System | Purpose | Confidence | Source |
|---------|-----------------|---------|------------|--------|
| learn-portal | SendGrid / Brevo / SMTP | transactional email | observed | app/email_service/plugins/ |
| learn-portal | Ollama | LLM provider (ai profile) | uncertain | docker-compose.yml:119-127 (0 call sites) |
| learn-portal | Langfuse | LLM observability (ai profile) | uncertain | docker-compose.yml:147-161 (0 call sites) |

## 6. Evidence Notes
- Tags: observed (cited), inferred (basis stated), uncertain (declared-only / not wired).
- Coverage: full across the deployment; ai-profile usage is declared-only.

<!-- ── MACHINE BLOCK ── -->
```yaml machine
artifact: integration-map
nodes:
  - { id: "learn-portal", kind: "service", confidence: observed, source: "docker-compose.yml:11-25" }
  - { id: "embedding-service", kind: "service", confidence: observed, source: "embedding-service/api-surface.md:20-41" }
  - { id: "postgres", kind: "datastore", confidence: observed, source: "docker-compose.yml:56-71" }
  - { id: "prefect-server", kind: "external-api", confidence: observed, source: "docker-compose.yml:129-136" }
  - { id: "prefect-worker", kind: "service", confidence: observed, source: "docker-compose.yml:138-145" }
edges:
  - { from: "learn-portal", to: "postgres", via: "sdk", detail: "SQLAlchemy/psycopg3", confidence: observed, source: "app/db.py:8" }
  - { from: "learn-portal", to: "embedding-service", via: "http", detail: "PLANNED embed step", confidence: uncertain, source: "ingestion_pipeline/flows.py:1-5" }
  - { from: "prefect-worker", to: "prefect-server", via: "http", detail: "work-pool poll", confidence: observed, source: "docker-compose.yml:138-145" }
external_dependencies:
  - { service: "learn-portal", system: "SendGrid/Brevo/SMTP", purpose: "transactional email", confidence: observed, source: "app/email_service/plugins/" }
```
