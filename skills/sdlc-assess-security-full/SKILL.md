---
name: sdlc-assess-security-full
role: reviewer   # ADR-035: author | reviewer | integration
description: >
  Audit a whole repository for security and quality problems by running pinned open-source
  scanners (secrets, SAST, dependency CVEs, misconfiguration, licences, SBOM), normalising their
  output into one findings.json tagged with severity, CWE and OWASP Top 10 category, and writing a
  reviewable security-audit.md with tool coverage and gaps. Use this as the FIRST step of the
  security audit workflow (sdlc-wf-security-audit), before sdlc-assess-findings-triage. Trigger
  this even when the user just says "security audit", "scan the repo", "run the scanners", "OWASP
  report", or "what vulnerabilities do we have". It reports only: it changes no code, decides
  nothing about what to fix, and writes nothing to Jira.
compatibility: >
  Needs the agent image's security tools layer (gitleaks, opengrep, osv-scanner, trivy at minimum;
  stack tools such as psalm, composer, npm, eslint, bandit, pip-audit, hadolint, syft when present).
  No MCP required. Writes only under docs/security/audit/.
complexity: medium   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-assess-security-full — Audit the Whole Repo

> **Artifact paths:** The audit folder is `docs/security/audit/` (see the Security rows of
> `_SHARED-project-layout.md`). Re-running the audit replaces its files; git keeps the history.
> This skill's own `templates/`, `references/` and `examples/` stay in the skill folder.

> **Cost & context:** The scanners do the reading. Do not read source files to look for
> problems yourself; open a file only to confirm or explain a specific finding. Keep raw tool
> output on disk under `raw/`, and load only the parts you need.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part for a template before you fill it.

**Scanners find; this step records.** This step produces the evidence: what
each tool reported, normalised to one scale. Deciding what to fix, accept or ignore is
`sdlc-assess-findings-triage`'s job, and a person approves it. Read
`references/_SHARED-security-scanners.md` before you start: it lists the tools per stack, the
severity scale, the OWASP mapping and the `findings.json` format.

## Input it expects
- The repository at the run branch tip.
- The security tools on `PATH` (the agent image's security layer). The four core tools are checked
  before you start.
- Optional: the project's own scanner configs (`.gitleaks.toml`, `psalm.xml`, `.eslintrc*`),
  `docs/architecture.md` to explain where a finding sits.

## Output it produces
All under `docs/security/audit/`:
- `findings.json` — every finding, normalised, valid against `templates/findings.schema.json`.
- `security-audit.md` — from `templates/security-audit.md.tmpl`: summary counts, scope, tool
  coverage, OWASP Top 10 coverage, the findings table, and gaps.
- `raw/<tool>.<ext>` — each tool's unmodified output (JSON or SARIF where the tool supports it).
- `sbom.cdx.json` — the CycloneDX SBOM from syft, when syft is available.

## Procedure

### Step 1 — Detect the stacks
From the files present (see the stack table in the shared note): `composer.json` → PHP,
`package.json` → Node.js (React if `react` is a dependency), `pyproject.toml` /
`requirements*.txt` → Python, `Dockerfile` / `compose*.yaml` → Docker, `*.sql` or a migrations
folder → SQL. Record each detected stack and the file that proved it.

### Step 2 — Run the tools
Run every core tool and every tool for a detected stack, writing raw output to `raw/`. Use the
project's config when it exists; never edit or weaken it. If a stack tool is missing, record it as
`not_available` and carry on. Never install a tool during the run. Record each tool's version, and
the vulnerability database date for CVE scanners. For gitleaks, scan both the working tree and the
git history; a secret in history is still a leaked secret. Record history findings with
`tool: "gitleaks-history"` and the commit in `notes`, because their file may no longer exist.

If a tool needs the project's dependencies installed (psalm, phpstan, eslint plugins) and they
are not, run it only if the project's own install command is documented in `AGENTS.md`;
otherwise record it as `failed` with the reason.

### Step 3 — Normalise
Convert every reported issue into one `findings.json` entry: severity on our scale, CWE, OWASP
category (`A01`–`A10`; `LLM01`–`LLM10` for code that calls an LLM), path relative to the repo
root, line, and a fingerprint as the shared note defines it. Merge exact duplicates that two
tools report for the same path, line and CWE into one finding, and name both tools in `notes`.
Do not drop or downgrade anything here, even if it looks like a false positive: that is triage's
call, with a person watching.

### Step 4 — Write the report
Fill `security-audit.md`. The findings table lists every finding ID. The OWASP coverage table
says, for each category, how many findings and which tools covered it, and marks categories no
tool covers (typically A01, A06, A09) as needing review or later DAST. The Gaps section lists
missing or failed tools and what they would have covered.

### Step 5 — Commit
Commit `docs/security/audit/` only. Hand off with the summary counts by severity.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: The audit ran and the report is written, including when it found nothing or
  when some stack tools were missing (those are recorded as gaps).
- **failed_execution**: A core tool ran but crashed or produced unreadable output, so the
  audit cannot be trusted. Name the tool and the error.

## What this skill is NOT
- Not a fixer: it changes no code and no config.
- Not triage: it keeps every finding the tools report, including likely false positives.
- Not DAST or a pentest: it never runs the application or sends traffic anywhere.

## Reference files
- `references/_SHARED-security-scanners.md` — tools per stack, severity scale, OWASP mapping,
  the findings format.
- `templates/security-audit.md.tmpl` — the report.
- `templates/findings.schema.json` — the findings schema.
- `examples/security-audit-example.md` — an audit of a PHP and Node.js repo.
