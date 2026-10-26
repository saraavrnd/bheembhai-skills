<!-- Worked example: SDLC-structured conventions.md for Learn Portal. -->

---
artifact: conventions
generated: 2026-10-10
status: draft
confidence_summary: "3 observed, 0 inferred, 0 uncertain"
---

# Coding Conventions — Learn Portal

## 1. Overview
A de-facto (not enforced) set of conventions holds across the 3 implemented domains; the 12 stub
domains carry only an empty `router.py`, so the convention is a working pattern, not a validated
architecture. No linter/formatter config is committed.

## 2. Code Organization
- Per-domain package under `app/<domain>/` with `router.py` (HTTP), concern-split service modules
  and `models.py` beside the domain; no `schemas/`, `crud/`, `repository`, or `app/core`.
  _[observed — source: structure-map.md:15, 36-38]_
- Shared support modules use a loader + `plugins/` shape (provider by config).
  _[observed — source: app/email_service/loader.py; app/object_storage/plugins/]_

## 3. Naming
- Routers named `router.py` per domain; models `models.py`; snake_case modules; routes prefixed by
  domain. _[observed — source: structure-map.md:36-38]_

## 4. Error Handling & Logging
- Standard `logging` module (4 call sites); no centralized exception handler observed.
  _[inferred — basis: graph external_imports (logging); no app-level handler in app/main.py]_

## 5. Testing Conventions
- Three pytest layers under `tests/` (unit / integration / e2e), 69 modules total.
  _[observed — source: test-coverage-map.md:132-135]_

## 6. API / Interface Conventions
- API + form pair per entity (JSON route + server-rendered HTML route); `response_model` used
  inconsistently (missing in places). _[observed — source: api-surface.md]_

## 7. Configuration & Environment
- One pydantic-settings module; every value defaulted; compose overrides connection values.
  _[observed — source: app/config.py:1-35]_

## 8. Evidence Notes
- Tags: observed (holds across cited files), inferred (holds in part — basis stated), uncertain.
- Coverage: conventions validated against the 3 implemented domains; 12 stubs excluded.

<!-- ── MACHINE BLOCK ── -->
```yaml machine
artifact: conventions
conventions:
  - { area: "organization", claim: "per-domain router.py + service + models.py", confidence: observed, source: "learn-portal/structure-map.md:11-17" }
  - { area: "testing", claim: "3 pytest layers under tests/", confidence: observed, source: "learn-portal/test-coverage-map.md:11-14" }
  - { area: "config", claim: "single pydantic-settings module, all defaulted", confidence: observed, source: "app/config.py:1-35" }
```
