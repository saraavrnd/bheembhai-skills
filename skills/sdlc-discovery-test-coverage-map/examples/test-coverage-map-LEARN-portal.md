<!-- Worked example: test-coverage-map for Learn Portal (fastapi pack). From the tests/ tree. -->
```yaml
artifact: test-coverage-map
service: learn-portal
generated: 2026-10-01
stack_pack: fastapi
summary: >
  Three layers present (unit / integration / e2e). Unit runs standalone; integration + e2e need a
  live Postgres (and the app running, for e2e Playwright). auth/passwords and the health path are
  covered; school_admin has unit + integration. Coverage is per-feature, not blanket.
layers:
  unit:        { run: "uv run pytest tests/unit", needs_services: false, source: "tests/unit/" }
  integration: { run: "uv run pytest tests/integration", needs_services: true, source: "tests/integration/" }
  e2e:         { run: "uv run pytest tests/e2e --base-url http://localhost:8000", needs_services: true, source: "tests/e2e/" }
tests:
  - { file: "tests/unit/test_passwords.py", layer: unit, covers: "bcrypt hash/verify (NFR-004)", confidence: observed, source: "tests/unit/test_passwords.py" }
  - { file: "tests/unit/test_health.py", layer: unit, covers: "health payload shape", confidence: observed, source: "tests/unit/test_health.py" }
  - { file: "tests/integration/test_password_persistence.py", layer: integration, covers: "bcrypt hash round-trips through Postgres", confidence: observed, source: "tests/integration/test_password_persistence.py" }
  - { file: "tests/integration/test_health_api.py", layer: integration, covers: "API round trip via httpx", confidence: observed, source: "tests/integration/test_health_api.py" }
  - { file: "tests/e2e/test_health_page.py", layer: e2e, covers: "browser loads page, reads DOM status", confidence: observed, source: "tests/e2e/test_health_page.py" }
area_coverage:
  - { area: "auth/passwords", tested: true, by: ["test_passwords.py", "test_password_persistence.py"], confidence: observed, source: "tests/" }
  - { area: "health/main", tested: true, by: ["test_health.py", "test_health_api.py", "test_health_page.py"], confidence: observed, source: "tests/" }
  - { area: "school_admin", tested: true, by: ["tests/unit/school_admin", "tests/integration/school_admin"], confidence: observed, source: "tests/" }
```
