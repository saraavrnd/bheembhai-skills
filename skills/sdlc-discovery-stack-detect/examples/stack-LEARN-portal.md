<!-- Worked example: stack-detect output for the Learn Portal backend service.
     Written to docs/discovery/learn-portal/stack.md. Confident match. -->
```yaml
artifact: stack
service: learn-portal
generated: 2026-10-01
stack_pack: fastapi

summary: >
  FastAPI (Python 3.12) backend service, detected with high confidence: fastapi in
  pyproject.toml, app/main.py entrypoint, and app/**/router.py routing convention all present.
  The fastapi knowledge pack applies; downstream discovery can use conventional locations
  (routes at **/router.py, SQLAlchemy models at **/models.py, Alembic migrations under
  migrations/versions/).

findings:
  - claim: "Framework is FastAPI"
    confidence: observed
    source: "pyproject.toml"
    note: "dep_present fastapi; also app/main.py present (dep+glob signals)"
  - claim: "FastAPI version >=0.138"
    confidence: observed
    source: "pyproject.toml:dependencies.fastapi"
  - claim: "Language is Python 3.12"
    confidence: observed
    source: "pyproject.toml:requires-python"
  - claim: "ORM is SQLAlchemy 2.0 with Alembic migrations"
    confidence: observed
    source: "pyproject.toml:dependencies.sqlalchemy"
    note: "confirms data-model will be in **/models.py + migrations/versions/"
  - claim: "Selected knowledge pack: fastapi"
    confidence: observed
    source: "references/knowledge-packs/fastapi.yaml"
  - claim: "Server-rendered UI (Jinja2 + Bootstrap), not a separate SPA service"
    confidence: inferred
    basis: "jinja2/bootstrap deps in pyproject.toml; no package.json frontend build present"
    note: "so this is one full-stack service, not a split frontend/backend — relevant to integration-map"

# Embedded copy of the selected fastapi pack — carried here so downstream skills (api-surface,
# data-model, security-posture, build-run, …) need only read this stack.md, never the pack files.
embedded_pack:
  pack: fastapi
  locations:
    routes:      [app/, "**/router.py", "**/routers/"]
    controllers: [app/, "**/router.py"]
    models:      ["**/models.py", app/]
    migrations:  [migrations/versions/, alembic/versions/]
    config:      [app/config.py, app/settings.py, .env]
    tests:       [tests/unit/, tests/integration/, tests/e2e/, tests/]
    env_example: .env.example
    entrypoint:  [app/main.py, main.py]
  patterns:
    route:         '@(app|router)\.(get|post|put|patch|delete)\('
    model:         '(class\s+\w+\(Base\)|Mapped\[|Column\()'
    auth:          '(Depends\(require_role|Depends\(get_current_user|OAuth2|require_role_cookie)'
    external_call: '(httpx|requests\.(get|post)|aiohttp|\.request\()'
  commands:
    install: "uv sync"
    test:    "uv run pytest"
    run:     "uv run uvicorn app.main:app --reload"
    migrate: "uv run alembic upgrade head"
  risk_hints:
    - "endpoint with no Depends(auth) = unauthenticated route"
    - "raw string SQL via text() / execute() = injection surface"
    - "secrets in settings read from env — confirm not defaulted to a real value in code"
    - "missing response_model = unvalidated/over-exposed response shape"
  glossary_hints:
    - "**/models.py"
    - docs/data-model.md
  graph:
    builder: graphify
    dynamic_caveats:
      - "FastAPI Depends() wiring is runtime DI — not a static edge"
      - "APIRouter include_router() can be dynamic/string-driven"
      - "Prefect/Celery flow & task discovery is runtime, not import-visible"
```
