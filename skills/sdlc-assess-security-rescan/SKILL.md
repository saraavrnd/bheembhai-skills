---
name: sdlc-assess-security-rescan
role: reviewer   # ADR-035: author | reviewer | integration
description: >
  Prove a security fix worked: re-run the scanners that reported a security bug's findings on the
  fix branch, confirm every finding's fingerprint is gone, and check that the change itself
  introduces no new critical or high finding. Writes a PASS/BLOCK security-rescan.md in the bug's
  folder; BLOCK routes back to sdlc-deliver-code-implement. Use this in sdlc-wf-security-fix after
  sdlc-deliver-tests-verify passes and before sdlc-deliver-code-review. Trigger this even when the
  user just says "rescan", "is the vulnerability gone", "confirm the security fix", or "check the
  fix with the scanners". It changes no code.
compatibility: >
  Needs the agent image's security tools layer (the tools named in the bug's findings table, plus
  gitleaks and opengrep for the new-findings check). Reads the bug from the run context. Writes
  only the bug folder's security-rescan.md.
model: haiku   # tier: cheap (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-assess-security-rescan — Prove the Finding Is Gone

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table in
> the repo's conventions file (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see
> `_SHARED-project-layout.md`. The work item is a security bug, so its folder is
> `docs/product/bugs/<BUG_KEY>/` (`{layout.bug_dir}`).

> **Cost & context:** Run only the tools named in the bug's findings table, scoped to the files
> they point at, plus the two new-findings tools on the changed files. Do not re-run the whole
> audit.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part for a template before you fill it.

Tests passing shows the code works; it does not show the vulnerability is gone. A fix can block
the one payload in the regression test and leave the flaw open by another path. The scanner that
found the problem is the independent check: if it still reports the same fingerprint, the fix is
not done. Read `references/_SHARED-security-scanners.md` for the fingerprint rule and the
severity scale.

## Input it expects
- The bug (`context.bug`): its description carries the batch's findings table with tool, rule,
  location and fingerprint, written by `sdlc-assess-findings-triage` and published by
  `sdlc-tracker-sync`.
- `verification.md` in the bug folder with verdict PASS (from `sdlc-deliver-tests-verify`).
- The fix branch and its diff against the branch point.

## Output it produces
- `security-rescan.md` in the bug folder, from `templates/security-rescan.md.tmpl`, ending in
  `**Verdict:** PASS` or `**Verdict:** BLOCK`.

## Procedure

### Step 1 — Read the target findings
Take the findings table from the bug description. If the bug has no findings table with
fingerprints, it was not created by the audit; stop (see Outcomes).

### Step 2 — Re-run the reporting tools
For each tool in the table, run it on the files the findings point at (for a dependency finding,
on the lockfile), with the same config the audit used. Compute fingerprints the same way. Mark
each target finding:
- **fixed** — the tool no longer reports that fingerprint, and no finding with the same rule now
  appears elsewhere in the same file.
- **still present** — the same fingerprint is reported.
- **moved** — the fingerprint changed but the same rule fires on the same function or a line the
  change touched. A moved finding is not fixed.

For a secret, "fixed" means it is gone from the working tree; the history and the rotation are
manual actions the bug records, and the report repeats them.

### Step 3 — Check the change for new findings
Run `gitleaks` and `opengrep` (and the stack's SAST tool) on the files the diff changed. Any
critical or high finding in a changed line that the audit did not report is a new finding.
Findings in unchanged lines belong to other batches and are listed only as a note.

### Step 4 — Decide
**PASS** when every target finding is fixed and the change adds no new critical or high finding.
Otherwise **BLOCK**, and list what `sdlc-deliver-code-implement` must change, with file and line.
Commit the report.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: Your verdict is PASS.
- **BLOCK**: Your verdict is BLOCK: a target finding is still present or moved, or the change
  adds a new critical or high finding.
- **failed_execution**: The bug carries no findings table with fingerprints, so there is
  nothing to re-scan against. A person links it to the audit or runs the plain bug-fix workflow.

## What this skill is NOT
- Not a fixer: it reports what is still wrong; `sdlc-deliver-code-implement` fixes it.
- Not the full audit: it checks one batch and the change, nothing else.
- Not code review: style and design belong to `sdlc-deliver-code-review`, which runs next.

## Reference files
- `references/_SHARED-security-scanners.md` — fingerprints, severity scale, tool commands.
- `templates/security-rescan.md.tmpl` — the report.
- `examples/security-rescan-example.md` — a BLOCK on a moved SQL injection finding.
