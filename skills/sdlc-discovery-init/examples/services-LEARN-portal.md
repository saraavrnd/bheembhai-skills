<!-- Worked example: polyglot repo (Learn Portal). topology=multi, TWO first-party services.
     Note how detection comes from docker-compose.yml + the Dockerfiles, NOT just manifests:
     embedding_service has no pyproject.toml of its own yet is a service (own Dockerfile, own
     compose build context, own port). ingestion_pipeline is a COMPONENT of the api service
     (no Dockerfile/manifest; runs on the shared prefect-worker image against the api codebase),
     so it is noted in summary but NOT a fan-out entry. The infra images (postgres, redis, minio,
     ollama, langfuse, mailhog) are dependencies, not services. The fence info string is what the
     parent workflow's fan-out node looks for. -->
```yaml bheembhai:foreach
artifact: services
repo: learn-portal
generated: 2026-10-10
topology: multi
summary: >
  Two first-party services, detected from docker-compose.yml and the Dockerfiles (not from
  manifests alone): the FastAPI web app (api, root pyproject.toml + infra/Dockerfile.api, compose
  `api` build: .) and embedding_service (own Dockerfile, compose `embedding_service`
  build: ./embedding_service, port 8001 — no manifest of its own but a separately built/deployed
  container). ingestion_pipeline/ is a COMPONENT of the api service (Prefect flows.py with no
  Dockerfile/manifest, run by the shared prefect-worker on the api image/codebase), not a separate
  service. postgres/redis/minio/ollama/langfuse/mailhog are off-the-shelf infra (compose
  image-only), not services. The per-service discovery chain runs twice.
services:
  - id: learn-portal
    root: "."
    manifest: "pyproject.toml"
    confidence: observed
    source: "pyproject.toml (root); docker-compose.yml service `api` build context `.`; infra/Dockerfile.api"
  - id: embedding-service
    root: "embedding_service"
    manifest: "none"
    confidence: observed
    source: "embedding_service/Dockerfile; docker-compose.yml service `embedding_service` build: ./embedding_service, port 8001"
```
