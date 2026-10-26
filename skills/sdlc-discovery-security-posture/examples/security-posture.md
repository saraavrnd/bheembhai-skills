<!-- Worked example: SDLC-structured security-posture.md for Learn Portal. Readable domain sections
     + severity-ranked findings + machine block. Every line tagged + sourced. -->

---
artifact: security-posture
generated: 2026-10-10
status: draft
confidence_summary: "5 observed, 0 inferred, 0 uncertain"
---

# Security Posture — Learn Portal

## 1. Overview
A single JWT+bcrypt auth scheme applied per-route (not global middleware), all secrets defaulted
for dev, no TLS in the compose stack, and no CI gate. The posture is "walking-skeleton" — enough
to run, not hardened.

## 2. Authentication & Authorization
- One JWT+bcrypt scheme via three per-route guards (`require_role` Bearer, `require_role_cookie`
  HTML, `require_role_json` dual-mode + CSRF). _[observed — source: app/auth/security.py; api-surface.md:597-604]_
- App-level routes (/health, /, /docs, /openapi.json) carry **no** auth dependency.
  _[observed — source: api-surface.md:22-35]_

## 3. Secrets & Configuration
- Every setting has a default so the app boots with no .env; `JWT_SECRET_KEY` defaults in code and
  `SECURE_STORAGE_MASTER_KEY` defaults to `dev-only-insecure-key-change-me` in compose.
  _[observed — source: app/config.py:1-35; docker-compose.yml:26-33]_

## 4. Data Protection
- `PostgresSecureStorage` (ADR-009) encrypts stored secrets using the master key above; tenancy
  scoping is a plain `school_id` String with no FK. _[observed — source: data-model.md:205-226]_

## 5. Transport & Network
- No TLS in the compose stack; all services on plain HTTP/ports. MinIO console and all DB ports
  are host-exposed in dev. _[observed — source: docker-compose.yml:56-108]_

## 6. Input & Attack Surface
- 5 of 24 web POSTs have no CSRF check as written. _[observed — source: api-surface.md:597-604]_
- Raw string SQL via `text()` is a declared pack risk; grep scope for discovery.
  _[inferred — basis: stack.md risk_hints; not confirmed present]_

## 7. Dependency & Supply-Chain
- learn-portal has a `uv.lock`; embedding-service has **no lockfile** (deps pip-pinned in its
  Dockerfile). _[observed — source: embedding-service/dependency-inventory.md (lockfile MISSING)]_

## 8. Findings (severity-ranked)
| ID | Severity | Finding | Confidence | Source |
|----|----------|---------|------------|--------|
| SEC-1 | high | `SECURE_STORAGE_MASTER_KEY` + `JWT_SECRET_KEY` default to insecure dev values | observed | docker-compose.yml:33; app/config.py |
| SEC-2 | high | No TLS anywhere in the stack | observed | docker-compose.yml:56-108 |
| SEC-3 | med | 5/24 web POSTs lack CSRF protection | observed | api-surface.md:597-604 |
| SEC-4 | med | embedding-service has no dependency lockfile | observed | embedding-service/dependency-inventory.md |
| SEC-5 | low | No CI gate — tests never run automatically | observed | test-coverage-map.md:132-135 |

## 9. Evidence Notes
- Tags: observed (cited), inferred (basis stated), uncertain.
- Coverage: full across both services; runtime pen-test out of scope (static review only).

<!-- ── MACHINE BLOCK ── -->
```yaml machine
artifact: security-posture
findings:
  - { id: "SEC-1", claim: "secrets default to insecure dev values", severity: "high", confidence: observed, source: "docker-compose.yml:33" }
  - { id: "SEC-2", claim: "no TLS in the stack", severity: "high", confidence: observed, source: "docker-compose.yml:56-108" }
  - { id: "SEC-3", claim: "5/24 web POSTs lack CSRF", severity: "med", confidence: observed, source: "learn-portal/api-surface.md" }
  - { id: "SEC-4", claim: "embedding-service has no lockfile", severity: "med", confidence: observed, source: "embedding-service/dependency-inventory.md" }
  - { id: "SEC-5", claim: "no CI gate", severity: "low", confidence: observed, source: "learn-portal/test-coverage-map.md:11-14" }
```
