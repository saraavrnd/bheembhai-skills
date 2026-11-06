---
name: sdlc-assess-findings-triage
role: author   # ADR-035: author | reviewer | integration
description: >
  Triage a security audit's findings into a fix plan a person can approve: confirm each finding
  as a true positive, false positive or duplicate with evidence from the code, rate how
  exploitable it is, group the true positives into fix batches (one future Jira security bug and
  one fix branch each), and propose fix now, accept or defer for each batch. Writes fix-plan.md and
  fix-map.json with draft bug keys for sdlc-tracker-sync to publish. Use this as the step after
  sdlc-assess-security-full in sdlc-wf-security-audit. Trigger this even when the user just says
  "triage the findings", "which of these are real", "plan the security fixes", or "group the
  vulnerabilities". It changes no code and writes nothing to Jira.
compatibility: >
  Tool-agnostic. Reads docs/security/audit/findings.json, security-audit.md and the raw tool
  output, plus the source lines each finding points at. No MCP required.
complexity: high   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-assess-findings-triage — Decide What Is Real and What to Fix

> **Artifact paths:** The audit folder is `docs/security/audit/` (see the Security rows of
> `_SHARED-project-layout.md`). This skill's own `templates/`, `references/` and `examples/`
> stay in the skill folder.

> **Cost & context:** Read each finding's source location and a few lines around it, not whole
> files. For a dependency finding, read the lockfile entry and search for where the package is
> imported; do not read the package.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part for a template before you fill it.

Scanners over-report. A raw audit of an older codebase can hold hundreds of findings, most of
them noise, and nobody fixes a list like that. This step turns the list into a small number of
fix batches, each sized for one branch and one pull request, with a clear proposal a person can
approve at the gate. The person decides; you propose with evidence. Read
`references/_SHARED-security-scanners.md` for the severity scale and OWASP mapping, and
`references/batching-rules.md` before grouping.

## Input it expects
- `docs/security/audit/findings.json` and `security-audit.md` from `sdlc-assess-security-full`.
- The raw tool output in `docs/security/audit/raw/`.
- The source at the audit commit. Optional: `docs/architecture.md` to judge reachability.
- On a revise pass after the gate: the reviewer's comments on the previous `fix-plan.md`.

## Output it produces
In `docs/security/audit/`:
- `fix-map.json` — valid against `templates/fix-map.schema.json`: a verdict for every finding, and
  the batches with their decision and a draft bug key (`SEC-PENDING-N`) for each fix-now batch.
- `fix-plan.md` — from `templates/fix-plan.md.tmpl`: the reviewable plan. Each fix-now batch
  section is written so `sdlc-tracker-sync` can paste it into the Jira bug unchanged.

## Procedure

### Step 1 — Confirm every finding
For each finding, open its location and decide:
- **true_positive** — the code really does what the rule describes, and the input can reach it.
- **false_positive** — it cannot happen: the input is constant or already validated, the code is
  test-only or dead, the package version is not the one actually installed. Quote the line that
  proves it in `reason`.
- **duplicate** — the same flaw as another finding (same sink, same root cause). Name it in
  `duplicate_of`.

A finding with `confidence: "model-only"` can be confirmed only with a quoted line and a concrete
path from input to the flaw. When unsure, keep it a true positive with low exploitability: a
missed vulnerability costs more than a reviewed false alarm.

### Step 2 — Rate exploitability
For each true positive: **high** (reachable from an unauthenticated request or a public page, or a
live secret), **medium** (reachable after login or with specific data), **low** (needs admin
access, local access, or an unlikely configuration). Severity stays what the tool said;
exploitability is your judgment, and you say why.

### Step 3 — Group into batches
Follow `references/batching-rules.md`: one root cause or one module per batch, at most about five
findings, secrets in a batch of their own, and dependency upgrades grouped by package manager.
Give each batch an ID (`B-01`, …), a title a developer understands, its highest severity and its
OWASP categories.

### Step 4 — Propose a decision per batch
- **fix_now** — every critical, every high with high or medium exploitability, and anything the
  project's own rules require. Give it a draft key `SEC-PENDING-N`.
- **accept** — a real but tolerable risk, with the reason and what limits it (for example "admin
  only, behind VPN"). A person must agree at the gate; the reason is kept as the audit record.
- **defer** — real and worth fixing, but not now; say what it waits for.

### Step 5 — Write the plan
Fill `fix-plan.md` and `fix-map.json` so they agree. For each fix-now batch, write the section the
Jira bug will carry: the findings table (ID, tool / rule, location, fingerprint), why it matters
in this application, the fix direction (not the code), and the acceptance condition: "a re-scan no
longer reports these fingerprints, and a regression test shows the attack is blocked". Secrets get
an extra line: **the credential must be revoked and rotated by a person**; removing it from code
does not make it safe.

Set `project_key` from the run context's Jira integration. If it is not known, write `PENDING`
and say so in the Jira section; the person names it at the gate. Commit both files.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: The plan is written, including when every finding was a false positive or every
  batch is accept or defer. The gate shows it to a person either way.

## What this skill is NOT
- Not a scanner: it never adds a finding the audit did not report, except a duplicate merge.
- Not a fixer: it changes no code; batches are fixed later, one branch each, by
  `sdlc-wf-security-fix`.
- Not a tracker writer: `sdlc-tracker-sync` creates the Jira bugs after the gate.

## Reference files
- `references/_SHARED-security-scanners.md` — severity scale, OWASP mapping, findings format.
- `references/batching-rules.md` — how to group findings into fix batches.
- `templates/fix-plan.md.tmpl` — the reviewable plan.
- `templates/fix-map.schema.json` — the machine plan tracker-sync reads.
- `examples/fix-plan-example.md` — the plan for the audit in `sdlc-assess-security-full`'s example.
