# Security rescan — ACME-212: SQL injection in the PHP report module

**Date:** 2026-11-08 · **Branch:** `fix/ACME-212-report-sql-injection` · **Commit:** `b71e0d4`

## Target findings
| Finding | Tool / rule | Fingerprint | Status | Evidence |
|---|---|---|---|---|
| F-002 | psalm / TaintedSql | `psalm:TaintedSql:src/Report/SalesReport.php:91ab33f0` | fixed | not reported |
| F-003 | psalm / TaintedSql | `psalm:TaintedSql:src/Report/StockReport.php:0c7de412` | moved | `src/Report/ReportBase.php:88` TaintedSql: `$_GET['sort']` reaches `PDO::query()` through `ReportBase::orderBy()` |

## New findings in the change
| Tool / rule | Location | Severity | New in this change? |
|---|---|---|---|
| none | — | — | — |

## Tools run
```
$ psalm --taint-analysis --output-format=json src/Report/
1 issue: TaintedSql src/Report/ReportBase.php:88
```
```
$ gitleaks dir --no-banner src/Report/ tests/Report/
no leaks found
```
```
$ opengrep scan --config rules/ src/Report/ tests/Report/
0 findings
```

## Manual actions still open
- none

## Verdict
**Verdict:** BLOCK

- `src/Report/ReportBase.php:88` — `orderBy()` still concatenates `$sort` into the query when the
  column is not in the allow-list; it falls back to the raw value instead of the default column.
  Return the default column for any value not in `ALLOWED_SORT_COLUMNS`. StockReport reaches this
  path; SalesReport no longer does because it now passes a constant.
