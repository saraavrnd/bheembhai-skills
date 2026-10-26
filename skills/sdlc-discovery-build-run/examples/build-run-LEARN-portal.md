<!-- Worked example: build-run for Learn Portal (fastapi pack). Commands from pyproject/compose + pack. -->
```yaml
artifact: build-run
service: learn-portal
generated: 2026-10-01
stack_pack: fastapi
summary: >
  uv-managed FastAPI app. Install with uv sync, run with uvicorn, test with pytest (unit runs
  standalone; integration/e2e need a live Postgres from docker-compose). Requires Postgres, Redis,
  and MinIO per the compose file; env is driven by .env.example.
commands:
  install: { cmd: "uv sync", source: "pyproject.toml (uv) + fastapi pack default", confidence: observed }
  test:    { cmd: "uv run pytest", source: "tests/ layout; e2e needs --base-url", confidence: observed }
  run:     { cmd: "uv run uvicorn app.main:app --reload", source: "fastapi pack + app/main.py entrypoint", confidence: observed }
  migrate: { cmd: "uv run alembic upgrade head", source: "migrations/versions/ present", confidence: observed }
backing_services:
  - { name: postgres, source: "docker-compose.yml", confidence: observed }
  - { name: redis, source: "docker-compose.yml", confidence: observed }
  - { name: minio, source: "docker-compose.yml", confidence: observed }
env_required:
  - { name: DATABASE_URL, secret: false, source: ".env.example", confidence: observed }
  - { name: SECRET_KEY, secret: true, source: ".env.example", confidence: observed }
entrypoint: { path: "app/main.py", confidence: observed, source: "app/main.py" }
```
