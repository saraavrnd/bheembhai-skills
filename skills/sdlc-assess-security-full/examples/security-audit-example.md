# Security audit — acme-orders

**Date:** 2026-11-06 · **Commit:** `4f2c9e1` · **Scope:** full repository

## Summary
| Severity | Findings |
|---|---|
| critical | 1 |
| high | 3 |
| medium | 2 |
| low | 1 |
| info | 0 |

The critical finding is an AWS access key committed in git history (F-001). Two of the three
highs are SQL built from request input in the PHP reporting module (F-002, F-003); the third is a
vulnerable `axios` version in the Node.js API (F-004).

## Scope
| Stack | Detected from |
|---|---|
| PHP | `composer.json` |
| Node.js | `api/package.json` |
| React | `web/package.json` (`react` dependency) |
| Docker | `Dockerfile` |
| SQL | `db/migrations/` |

## Tool coverage
| Tool | Version | Status | Vulnerability DB date | Raw output |
|---|---|---|---|---|
| gitleaks | 8.21.2 | ran | n/a | `raw/gitleaks.json` |
| opengrep | 1.6.0 | ran | n/a | `raw/opengrep.sarif` |
| osv-scanner | 2.0.2 | ran | 2026-11-06 | `raw/osv-scanner.json` |
| trivy | 0.58.1 | ran | 2026-11-06 | `raw/trivy.json` |
| psalm | 6.8.0 | ran | n/a | `raw/psalm.sarif` |
| composer audit | 2.8.4 | ran | 2026-11-06 | `raw/composer-audit.json` |
| npm audit | 10.9.0 | ran | 2026-11-06 | `raw/npm-audit.json` |
| eslint | 9.17.0 | ran | n/a | `raw/eslint.json` |
| hadolint | 2.12.0 | ran | n/a | `raw/hadolint.json` |
| sqlfluff | — | not_available | n/a | — |
| syft | 1.18.1 | ran | n/a | `sbom.cdx.json` |

## OWASP Top 10 coverage
| Category | Findings | Covered by | Gap |
|---|---|---|---|
| A01 Broken Access Control | 0 | opengrep (path traversal only) | Route and role checks need manual review or DAST |
| A02 Security Misconfiguration | 2 | trivy, hadolint | — |
| A03 Software Supply Chain Failures | 1 | osv-scanner, npm audit, composer audit | — |
| A04 Cryptographic Failures | 1 | gitleaks, opengrep | — |
| A05 Injection | 2 | psalm, opengrep, eslint | — |
| A06 Insecure Design | 0 | none | Needs design review against the architecture docs |
| A07 Authentication Failures | 0 | opengrep | Session handling needs manual review |
| A08 Software or Data Integrity Failures | 0 | opengrep | — |
| A09 Logging and Alerting Failures | 1 | opengrep | Coverage of security events needs review |
| A10 Mishandling of Exceptional Conditions | 0 | eslint, psalm | — |

## Findings
| ID | Severity | OWASP | CWE | Location | Tool / rule | Title |
|---|---|---|---|---|---|---|
| F-001 | critical | A04 | CWE-798 | `config/legacy.php:12` (commit `9a1b3c0`) | gitleaks-history / aws-access-token | AWS access key in git history |
| F-002 | high | A05 | CWE-89 | `src/Report/SalesReport.php:58` | psalm / TaintedSql | Request input reaches a SQL query |
| F-003 | high | A05 | CWE-89 | `src/Report/StockReport.php:41` | psalm / TaintedSql | Request input reaches a SQL query |
| F-004 | high | A03 | CWE-918 | `api/package-lock.json` | osv-scanner / axios SSRF advisory | axios 1.6.0 vulnerable to SSRF |
| F-005 | medium | A02 | CWE-250 | `Dockerfile:1` | hadolint / DL3002 | Container runs as root |
| F-006 | medium | A02 | CWE-16 | `Dockerfile:9` | trivy / DS026 | No HEALTHCHECK instruction |
| F-007 | low | A09 | CWE-532 | `api/src/auth/login.js:77` | opengrep / log-sensitive-data | Email address written to the log on failed login |

## Gaps and limits
- sqlfluff is not in the image, so SQL migration files were not linted (quality only, no security category).
- No tool checks route-level access control (A01) or design (A06); triage should flag these for review.
- Vulnerability databases dated 2026-11-06.
