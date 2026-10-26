<!-- Worked example: dependency-inventory for Learn Portal (fastapi pack). From pyproject + uv.lock. -->
```yaml
artifact: dependency-inventory
service: learn-portal
generated: 2026-10-01
stack_pack: fastapi
summary: >
  uv-managed Python deps with uv.lock present. Core stack current (FastAPI 0.138, SQLAlchemy 2.0.x,
  pydantic). One flag: pgvector must stay >=0.8.2 (older pins carry a known parallel-HNSW CVE per
  the project's tech-stack note) — confirm the resolved version.
manager: { tool: "uv", lockfile: "uv.lock", source: "uv.lock" }
dependencies:
  - { name: "fastapi", version: ">=0.138.0", risk: none, confidence: observed, source: "pyproject.toml" }
  - { name: "sqlalchemy", version: "2.0.x", risk: none, confidence: observed, source: "pyproject.toml" }
  - { name: "pgvector", version: ">=0.8.2", risk: known-cve, confidence: uncertain,
      source: "pyproject.toml", note: "older pins carry a parallel-HNSW buffer-overflow CVE; verify resolved >=0.8.2" }
  - { name: "passlib", version: "latest", risk: none, confidence: observed, source: "pyproject.toml", note: "with the bcrypt extra" }
```
