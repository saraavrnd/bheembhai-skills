# Security fix plan — acme-orders

**Date:** 2026-11-06 · **Audit commit:** `4f2c9e1` · **Audit report:** `docs/security/audit/security-audit.md`

## Summary
| | Count |
|---|---|
| Findings in the audit | 7 |
| True positives | 6 |
| False positives | 1 |
| Duplicates | 0 |
| Batches to fix now | 4 |
| Batches accepted | 1 |
| Batches deferred | 0 |

Fix B-01 first: the AWS key in git history is valid until it is revoked, whatever happens to the
code.

## Batches

### B-01 — Leaked AWS access key in git history
**Decision:** fix_now · **Severity:** critical · **OWASP:** A04 · **Draft bug:** SEC-PENDING-1

| Finding | Tool / rule | Location | Exploitability | Fingerprint |
|---|---|---|---|---|
| F-001 | gitleaks-history / aws-access-token | `config/legacy.php:12` (commit `9a1b3c0`) | high | `gitleaks-history:aws-access-token:config/legacy.php:5e1d0c2a` |

**Why it matters:** anyone with read access to the repository, now or in any old clone, can use
the key against the AWS account until it is revoked.

**Fix direction:** load the key from the environment through the existing config loader, and add a
`.gitleaks.toml` allow-list only for test fixtures.

**Manual action:** revoke and rotate the key in AWS IAM; decide whether to rewrite git history.

**Done when:** a re-scan no longer reports these fingerprints, and a regression test shows the attack is blocked.

### B-02 — SQL injection in the PHP report module
**Decision:** fix_now · **Severity:** high · **OWASP:** A05 · **Draft bug:** SEC-PENDING-2

| Finding | Tool / rule | Location | Exploitability | Fingerprint |
|---|---|---|---|---|
| F-002 | psalm / TaintedSql | `src/Report/SalesReport.php:58` | medium | `psalm:TaintedSql:src/Report/SalesReport.php:91ab33f0` |
| F-003 | psalm / TaintedSql | `src/Report/StockReport.php:41` | medium | `psalm:TaintedSql:src/Report/StockReport.php:0c7de412` |

**Why it matters:** a logged-in user can change the `sort` query parameter to read any table,
including other customers' orders.

**Fix direction:** both reports build `ORDER BY` from `$_GET['sort']` through
`ReportBase::query()`. Bind values with prepared statements and map `sort` through an allow-list
of column names in `ReportBase`.

**Manual action:** none

**Done when:** a re-scan no longer reports these fingerprints, and a regression test shows the attack is blocked.

### B-03 — Vulnerable axios in the Node.js API
**Decision:** fix_now · **Severity:** high · **OWASP:** A03 · **Draft bug:** SEC-PENDING-3

| Finding | Tool / rule | Location | Exploitability | Fingerprint |
|---|---|---|---|---|
| F-004 | osv-scanner / axios SSRF advisory | `api/package-lock.json` | medium | `osv-scanner:axios-ssrf:api/package-lock.json:axios@1.6.0` |

**Why it matters:** the API passes a user-supplied webhook URL to axios, so the SSRF flaw is
reachable after login.

**Fix direction:** upgrade axios to the first fixed minor version; no API changes expected.

**Manual action:** none

**Done when:** a re-scan no longer reports these fingerprints, and a regression test shows the attack is blocked.

### B-04 — Container hardening
**Decision:** accept · **Severity:** medium · **OWASP:** A02 · **Draft bug:** none

| Finding | Tool / rule | Location | Exploitability | Fingerprint |
|---|---|---|---|---|
| F-005 | hadolint / DL3002 | `Dockerfile:1` | low | `hadolint:DL3002:Dockerfile:3b9f1e77` |

### B-05 — Email address in the failed-login log
**Decision:** fix_now · **Severity:** low · **OWASP:** A09 · **Draft bug:** SEC-PENDING-4

| Finding | Tool / rule | Location | Exploitability | Fingerprint |
|---|---|---|---|---|
| F-007 | opengrep / log-sensitive-data | `api/src/auth/login.js:77` | low | `opengrep:log-sensitive-data:api/src/auth/login.js:aa04c9d1` |

**Why it matters:** the log goes to a shared logging service, so personal data leaves the
application's own store.

**Fix direction:** log the user ID hash instead of the email address.

**Manual action:** none

**Done when:** a re-scan no longer reports these fingerprints, and a regression test shows the attack is blocked.

## Accepted and deferred
| Batch | Decision | Reason | Limits on the risk / waits for |
|---|---|---|---|
| B-04 | accept | The image is replaced by the hardened base image planned in the Kubernetes move | Runs only on the internal network today; revisit when ADR-036 lands |

## False positives
| Finding | Reason (with the line that proves it) |
|---|---|
| F-006 | The health check is defined where the image runs: `deploy/compose.prod.yaml:22` sets `healthcheck:` for this service, so the missing Dockerfile instruction has no effect. |

## Not covered by tools
- A01 Broken Access Control: check that every `/admin/*` route calls `requireRole('admin')`.
- A06 Insecure Design: review the webhook feature's trust model (who can register a URL).

## Jira
- Project key: ACME
- To create: 4 bugs, type Bug, label `security`, one per fix-now batch above.
- Applied: no — sdlc-tracker-sync creates them after the gate (ADR-035)
