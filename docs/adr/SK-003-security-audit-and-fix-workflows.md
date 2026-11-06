# SK-003: Security audit and fix workflows

**Status:** Proposed · **Date:** 2026-11-06 · **Deciders:** Saraav

**Discussion:** "Open-source quality and security testing as BheemBhai skills" (project doc),
6 November thread. Part of preparing BheemBhai and its customers' code for security review before
on-premises deployment.

## Context

Customers' security teams will ask for evidence: what was scanned, with which tools, what was
found, what was fixed, and which risks were accepted and by whom. The catalog has a security
*synthesis* skill (`sdlc-discovery-security-posture`) and a security area in code review, but both
rely on the model reading code. Nothing runs real scanners, and there is no way to work through an
existing codebase's security debt without mixing it into feature stories.

Decisions from the discussion:
- First stacks: PHP, Node.js, React, MySQL (both first customers); Python and Docker when
  BheemBhai itself is the target.
- Security fixes get a dedicated workflow, on their own branches, separate from feature work.
- The scan inside story delivery starts advisory (a later PR); DAST waits; SonarQube is parked.
- Findings are reported against the OWASP Top 10 and, for LLM features, the OWASP Top 10 for LLM
  Applications.

## Decision

1. **Scanners find, the agent triages.** Every finding starts as output from a pinned open-source
   scanner (`gitleaks`, `opengrep`, `osv-scanner`, `trivy` as the core; stack tools per
   `shared/_SHARED-security-scanners.md`). A model-only observation is labelled as such and is
   never the sole basis for a decision. Tools come from the agent image; skills never install
   them at run time.
2. **Three new skills.**

   | Skill | Role | Writes |
   |---|---|---|
   | `sdlc-assess-security-full` | reviewer | `docs/security/audit/` only: `findings.json`, `security-audit.md`, `raw/`, SBOM |
   | `sdlc-assess-findings-triage` | author | `docs/security/audit/fix-plan.md`, `fix-map.json` |
   | `sdlc-assess-security-rescan` | reviewer | the bug folder's `security-rescan.md` |

3. **Two workflows, not one with fan-out.** `sdlc-wf-security-audit` (scan → triage → gate →
   tracker-sync files one Jira Bug labelled `security` per fix-now batch) and
   `sdlc-wf-security-fix` (work item: bug; the bug-fix chain plus a rescan step after
   tests-verify). Fan-out children share the parent's branch (platform ADR-027), but each batch
   needs its own branch and PR, so each security bug is a separate run.
4. **Fingerprints carry the finding across runs.** The audit fingerprints each finding; triage
   copies the fingerprints into the fix plan; tracker-sync pastes that section into the Jira bug;
   the rescan re-runs the same tool and proves the fingerprint is gone. The rescan can therefore
   work even before the audit branch is merged.
5. **A person approves every accepted risk.** Triage proposes fix now / accept / defer per batch;
   the governed policy gates the plan for a lead. Secrets always carry a manual action: revoke
   and rotate.
6. **Existing skills changed minimally.** `sdlc-tracker-sync` gains a "security batches" scope
   (create the Bugs, swap `SEC-PENDING-N` keys). `sdlc-fix-bug-triage`'s decision guide gains a
   section for security bugs. Everything else in the fix chain is reused unchanged.
7. **OWASP as the classification.** Every finding carries an OWASP Top 10:2025 category (and an
   LLM Top 10 category where it applies), and the audit report has a coverage row for each of the
   ten categories, including the ones no tool covers.

## Consequences

- **Platform dependency:** the agent image needs a security tools layer (platform ADR-018 D4)
  with pinned versions and fresh vulnerability databases. Until it exists, both scanning skills
  fail their tool precondition with `env_infra`, which is the intended behaviour.
- **Branch names** for security fixes are the platform's bug branches (`fix/<KEY>-<slug>`), not a
  separate `security/` prefix; the `security` label on the Jira bug distinguishes them.
- **The audit's files** stay on the audit run's branch until someone merges it. Merging keeps the
  accepted-risk record on main, which the advisory story scan (next PR) will use as its baseline.
- **Not yet verified against tier 2.** `bheembhai-verify lint` needs the private platform release;
  CI runs it. The new verify files use only builtins and argument shapes already used in this
  catalog.
- **Later:** the advisory diff scan in story delivery (`sdlc-deliver-security-scan`), DAST against
  BheemBhai itself, SonarQube as an optional connection, and live LLM red-teaming.
