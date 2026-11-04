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
