<!-- Worked example: SDLC-structured glossary.md for Learn Portal. -->

---
artifact: glossary
generated: 2026-10-10
status: draft
confidence_summary: "2 observed, 1 inferred, 0 uncertain"
---

# Domain Glossary — Learn Portal

## 1. Overview
Vocabulary drawn from the 3 implemented domains (auth, school_admin, ingestion) and the data model;
the 12 stub domains contribute names only, not meanings.

## 2. Domain Terms
| Term | Definition | Confidence | Source |
|------|------------|------------|--------|
| School (singleton) | The single tenant per deployment; one row enforced via `school.singleton` | observed | data-model.md:205 |
| Academic Year / Class / Section | The academic-structure hierarchy under school_admin | observed | structure-map.md (school_admin); api-surface.md |
| Chapter | A unit of uploaded content with ordered files, parsed and previewable | observed | app/ingestion/router.py |
| Secure Storage | App-encrypted secret store backed by Postgres (ADR-009) | observed | data-model.md:205-226 |
| Ingestion flow | The planned parse→markdown→chunk→embed→index pipeline (currently a noop stub) | inferred | ingestion_pipeline/flows.py:1-5 (docstring) |

## 3. Abbreviations & Acronyms
| Abbrev. | Expansion | Confidence | Source |
|---------|-----------|------------|--------|
| JWT | JSON Web Token (auth scheme) | observed | app/auth/security.py |
| CSRF | Cross-Site Request Forgery (double-submit guard) | observed | api-surface.md:597-604 |
| SIS | Student Information System (sis_integration — stub) | inferred | app/main.py (module name; no implementation) |

## 4. Evidence Notes
- Tags: observed (term named in cited code/artifact), inferred (meaning read from usage — basis stated), uncertain.
- Coverage: implemented domains only; stub-domain terms are names without definitions.

<!-- ── MACHINE BLOCK ── -->
```yaml machine
artifact: glossary
terms:
  - { term: "School (singleton)", definition: "single tenant per deployment", kind: "term", confidence: observed, source: "learn-portal/data-model.md" }
  - { term: "Chapter", definition: "unit of uploaded content, parsed + previewable", kind: "term", confidence: observed, source: "app/ingestion/router.py" }
  - { term: "SIS", definition: "Student Information System (stub)", kind: "abbreviation", confidence: inferred, basis: "the expansion is never written in code; read from usage in app/main.py" }
```
