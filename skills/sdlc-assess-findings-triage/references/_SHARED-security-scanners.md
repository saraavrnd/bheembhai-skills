# Shared Convention — Security Scanners and the Findings Format

> Referenced by the security skills (`sdlc-assess-security-full`, `sdlc-assess-findings-triage`,
> `sdlc-assess-security-rescan`). It is NOT a skill itself. Edit it in `shared/` only, then run
> `python tools/build.py sync`.

## The rule: scanners find, the agent triages
Every finding starts as output from a pinned open-source scanner. The agent runs the tools,
normalises their output, removes duplicates and false positives, explains each finding and
proposes the fix. A problem the agent notices while reading code, with no tool behind it, is
recorded with `tool: "review"` and `confidence: "model-only"`. It is reported, but it never
counts toward a blocking decision on its own.

## Where the tools come from
The tools are baked into the agent image's security layer (platform ADR-018 D4). Never install
a scanner during a run (`pip install`, `npm i -g`, `curl | sh`): an unpinned tool fetched at run
time is itself a supply-chain risk, and its results are not reproducible. A tool that is not on
`PATH` is recorded as `not_available` in the coverage table, and the categories it would cover
are marked as gaps.

## Tool set by stack

**Core (every repo; the run fails without these):** `gitleaks`, `opengrep`, `osv-scanner`, `trivy`.

| Stack (detected from) | Tools | Covers |
|---|---|---|
| Every repo | `gitleaks dir` (working tree), `gitleaks git` (history, full audit only; record as tool `gitleaks-history`) | Secrets |
| Every repo | `opengrep scan --config <bundled rules>` | SAST, all languages |
| Every repo | `osv-scanner scan source -r .` | Known CVEs in lockfiles |
| Every repo | `trivy fs --scanners vuln,misconfig,secret,license .` | CVEs, config, licences |
| Every repo | `syft dir:. -o cyclonedx-json` (full audit only) | SBOM |
| PHP (`composer.json`) | `composer audit --format=json`, `psalm --taint-analysis`, `phpstan analyse` | CVEs, injection data flow, types |
| Node.js (`package.json`) | `npm audit --json`, `eslint` with `eslint-plugin-security` | CVEs, JS security patterns |
| React (`react` in `package.json`) | `eslint` with `eslint-plugin-react`, `eslint-plugin-jsx-a11y`; retire.js for vendored libraries | XSS sinks, vendored library CVEs |
| Python (`pyproject.toml`, `requirements*.txt`) | `bandit -r`, `pip-audit`, `ruff check` | Python security, CVEs |
| Docker (`Dockerfile`, `compose*.yaml`) | `hadolint`, `trivy config` | Image and compose hardening |
| MySQL / SQL files (`*.sql`, migrations) | `sqlfluff lint --dialect mysql` | SQL file quality |

Use the project's own config when it exists (an `.eslintrc`, `psalm.xml`, `.gitleaks.toml`).
Never weaken a project config to reduce findings.

## Licence rules for the tools themselves
Do not use the Semgrep Registry community rules (their licence forbids use in a competing
commercial product); use Opengrep's own rules. Do not use CodeQL on customer code (it is free
only for open-source code).

## Severity
Map every tool's severity onto one scale:

| Ours | Tool values |
|---|---|
| `critical` | CVSS ≥ 9.0, `CRITICAL`, a verified live secret |
| `high` | CVSS 7.0–8.9, `HIGH`, `ERROR`, any unverified secret |
| `medium` | CVSS 4.0–6.9, `MEDIUM`, `WARNING` |
| `low` | CVSS < 4.0, `LOW`, `INFO` with a security CWE |
| `info` | Everything else (style, notes) |

## OWASP category
Tag every finding with its OWASP Top 10:2025 category (`A01`–`A10`) from its CWE, and, for code
that calls an LLM, its OWASP Top 10 for LLM Applications 2025 category (`LLM01`–`LLM10`) where one
applies. When a tool gives no CWE, choose from the rule's description and say so in `notes`.

The CWEs below are common examples to guide the choice, not OWASP's full mapping.

| Category | Typical CWEs |
|---|---|
| A01 Broken Access Control | 22, 23, 35, 200, 201, 284, 285, 352, 639, 862, 863, 918 |
| A02 Security Misconfiguration | 16, 611, 942, 1004, 614 |
| A03 Software Supply Chain Failures | 1104, 937, 1035, 494 |
| A04 Cryptographic Failures | 261, 296, 310, 319, 321, 326, 327, 328, 330, 798 |
| A05 Injection | 20, 74, 77, 78, 79, 89, 90, 94, 917, 1336 |
| A06 Insecure Design | 209, 256, 501, 522, 656 |
| A07 Authentication Failures | 255, 259, 287, 288, 297, 384, 521, 613, 620, 640 |
| A08 Software or Data Integrity Failures | 345, 353, 426, 502, 565, 784, 829, 830 |
| A09 Logging and Alerting Failures | 117, 223, 532, 778 |
| A10 Mishandling of Exceptional Conditions | 248, 252, 390, 391, 396, 397, 755 |

## The findings format (`findings.json`)
One file, one object, validated against `templates/findings.schema.json` in the skill that
writes it:

```json
{
  "generated_at": "2026-11-06T09:00:00Z",
  "commit": "<sha scanned>",
  "scope": "full",
  "tools": [
    {"name": "gitleaks", "version": "8.21.2", "status": "ran", "db_date": null}
  ],
  "findings": [
    {
      "id": "F-001",
      "fingerprint": "<tool>:<rule_id>:<path>:<sha1 of the normalised matched line>",
      "tool": "psalm",
      "rule_id": "TaintedSql",
      "severity": "high",
      "cwe": "CWE-89",
      "owasp": "A05",
      "owasp_llm": null,
      "path": "src/Controller/ReportController.php",
      "line": 42,
      "title": "User input reaches a SQL query",
      "message": "<the tool's message, trimmed>",
      "confidence": "tool",
      "notes": ""
    }
  ]
}
```

- `id`: `F-NNN`, numbered in order of severity, then path. Stable within one audit only.
- `fingerprint`: stable across runs and line shifts. It is how a later scan recognises the same
  finding (fixed, still present, or accepted).
- `status` of a tool: `ran`, `not_available`, `failed`, or `not_applicable` (stack not present).
- `db_date`: the vulnerability database date for CVE scanners, so reports say how fresh they are.
- Raw tool output is kept next to it under `raw/<tool>.<ext>` as evidence.
