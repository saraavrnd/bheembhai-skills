<!-- Worked example: structure-map for Learn Portal (fastapi pack). Follows FastAPI conventions. -->
```yaml
artifact: structure-map
service: learn-portal
generated: 2026-10-01
stack_pack: fastapi
summary: >
  Follows FastAPI conventions closely: app/ holds the application, each feature a sub-package
  (app/auth, app/school_admin) with its own router.py + models.py; migrations under
  migrations/versions; tests split unit/integration/e2e. No surprising top-level dirs.
areas:
  - { area: routes,     path: "app/*/router.py",        purpose: "per-feature routers", confidence: observed, source: "app/" }
  - { area: models,     path: "app/*/models.py",        purpose: "SQLAlchemy models per feature", confidence: observed, source: "app/" }
  - { area: config,     path: "app/config.py",          purpose: "settings, read from .env", confidence: observed, source: "app/" }
  - { area: migrations, path: "migrations/versions/",   purpose: "Alembic schema history", confidence: observed, source: "migrations/" }
  - { area: tests,      path: "tests/",                purpose: "layered test suites (unit, integration, e2e)", confidence: observed, source: "tests/" }
  - { area: entrypoint, path: "app/main.py",            purpose: "FastAPI app + health", confidence: observed, source: "app/main.py" }
non_conventional: []
```
