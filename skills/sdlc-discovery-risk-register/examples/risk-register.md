<!-- Worked example: SDLC-structured risk-register.md for Learn Portal. -->

---
artifact: risk-register
generated: 2026-10-10
status: draft
confidence_summary: "3 observed, 0 inferred, 0 uncertain"
---

# Risk & Tech-Debt Register — Learn Portal

## 1. Overview
The dominant risks are scaffold presented as a stack (the whole AI/ingestion path is stubbed),
insecure-by-default secrets, and no automated quality gate. None is a surprise for an early
scaffold, but all must be closed before the system does real work.

## 2. Risk Summary
| Severity | Count | Themes |
|----------|-------|--------|
| High | 3 | insecure default secrets; no TLS; unimplemented core pipeline |
| Medium | 3 | missing CSRF on some POSTs; no CI; embedding-service unversioned deps |
| Low | 1 | no DB indexes declared |

## 3. Detailed Register
| ID | Risk | Impact | Likelihood | Severity | Confidence | Evidence | Recommendation |
|----|------|--------|------------|----------|------------|----------|----------------|
| R-1 | Secrets default to insecure dev values | Key compromise / forged tokens | high | high | observed | docker-compose.yml:33; app/config.py | Require non-default secrets at boot; fail closed |
| R-2 | No TLS anywhere | Credential/token interception | med | high | inferred | docker-compose.yml:56-108 | Terminate TLS at ingress before any non-dev use |
| R-3 | Ingestion pipeline is a noop stub | Core feature absent | high | high | observed | ingestion_pipeline/flows.py:1-17 | Implement + deploy flow; wire embed→embedding-service |
| R-4 | 5/24 web POSTs lack CSRF | State-changing CSRF | med | med | observed | api-surface.md:597-604 | Apply CSRF guard uniformly |
| R-5 | No CI configuration | Regressions ship unnoticed | high | med | observed | test-coverage-map.md:132-135 | Add CI running the 3 pytest layers |
| R-6 | embedding-service deps unpinned (no lockfile) | Non-reproducible build | med | med | observed | embedding-service/dependency-inventory.md | Add a lockfile/manifest |
| R-7 | No DB indexes declared | Query degradation at scale | low | low | observed | data-model.md:224-226 | Add indexes on FK/scoping columns |

## 4. Evidence Notes
- Tags: observed (the fact is cited), inferred (the risk judgment from observed facts — basis stated), uncertain.
- Coverage: full static review across both services.

<!-- ── MACHINE BLOCK ── -->
```yaml machine
artifact: risk-register
risks:
  - { id: "R-1", risk: "insecure default secrets", impact: "key compromise", likelihood: "high", severity: "high", confidence: observed, source: "docker-compose.yml:33", recommendation: "require non-default secrets at boot" }
  - { id: "R-3", risk: "ingestion pipeline is a noop stub", impact: "core feature absent", likelihood: "high", severity: "high", confidence: observed, source: "ingestion_pipeline/flows.py:1-17", recommendation: "implement + deploy flow" }
  - { id: "R-5", risk: "no CI", impact: "regressions ship", likelihood: "high", severity: "med", confidence: observed, source: "learn-portal/test-coverage-map.md:11-14", recommendation: "add CI running pytest layers" }
```
