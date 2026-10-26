---
name: sdlc-discovery-security-posture
description: >
  Synthesize the security posture — the auth/authz model, secrets handling, input-validation and known risk areas — from the per-service discovery artifacts, into a system-level security note. Use during Discovery AFTER the per-service skills. Trigger on "security posture", "how does auth work", "where are the security risks". For brownfield this is partly a FINDINGS exercise (what's weak), stated honestly with evidence, not a clean description.
compatibility: >
  Tool-agnostic. Reads the per-service discovery artifacts (and targeted source where needed). No
  MCP required. Output is a system-level discovery artifact under docs/discovery/_system/.
complexity: high   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-security-posture

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the convention is created by sdlc-discovery-init. Use the default layout in `references/_SHARED-project-layout.md`. This is a SYSTEM-LEVEL synthesis skill: it reads the per-service discovery artifacts for every service in `docs/discovery/services.md` and writes to `docs/discovery/_system/`. It reads discovery artifacts and source only — never the canonical project docs, which are discovery OUTPUT. Own `templates/`/`examples/` stay in the skill folder.

Cost & context: Runs at the frontmatter complexity tier. Read the per-service artifacts (already
distilled) as primary input; touch source only to confirm a specific judgment. Don't re-read whole
services — the per-service discovery notes are why they exist.

The "how safe is it, as built" for the system. Unlike greenfield (where security is designed), brownfield security is discovered — and often it's a findings exercise: the auth model as actually enforced, how secrets are actually handled, where validation is actually missing. State weaknesses as evidence-backed findings, never as vague alarm. A wrong security claim is dangerous in both directions (false alarm wastes effort; missed gap causes a breach), so confidence discipline matters most here.

## Input it expects
- Every service's `api-surface.md` (auth per endpoint), `dependency-inventory.md` (vulnerable deps), `stack.md` (pack `risk_hints`).
- Every service's code graph (built by sdlc-discovery-graph with graphify), when present. Query it with
  graphify verbs against that service's store
  (`--graph docs/discovery/<SERVICE>/graphify-out/graph.json`) — do NOT read graph.json directly:
  `affected "<sensitive node>"` returns the dependent impact / blast radius of a crypto/secrets
  loader, `subprocess`/`eval` site, or the external-call module — far stronger than grep for "what
  touches secrets / shells out / calls outbound". `path "<entrypoint>" "<sensitive node>"` confirms
  a specific reach. Cite each returned relation's source reference as `observed`. graphify sees
  static structure only (dynamic dispatch may add paths it can't show), so never assert "nothing
  reaches X" as `observed` on an empty `affected` set alone — that is `inferred`. Absent → grep the
  pack `patterns` as today, `inferred`. See sdlc-discovery-graph's `references/graphify-verbs.md`.
- `docs/discovery/_system/integration-map.md` (external data flows, egress).
- Shared: `references/_SHARED-discovery-contract.md`. Each service's selected pack data is embedded in that service's `stack.md` (`embedded_pack:`) — read it there; the pack files live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/_system/security-posture.md`. From `templates/security-posture.md.tmpl`, presented for review.

## Procedure
Step 1 — Read the per-service api-surfaces, dependency-inventories, and each pack's `risk_hints`.
Step 2 — Auth/authz model: from api-surface auth columns across services, describe how authentication and authorization actually work (mechanism, where enforced). Flag any endpoint recorded as 'no auth declared' — an unauthenticated endpoint is a finding, cited to its source.
Step 3 — Secrets handling: from build-run env (secret-flagged vars) and dependency-inventory, note how secrets are sourced; flag any secret seen in code/committed config (cite it) as a high finding.
Step 4 — Input validation + injection surface: apply each pack's `risk_hints` (raw SQL, mass-assignment, missing validation) — grep to CONFIRM before asserting; a hint is `uncertain` until a real instance is cited.
Step 5 — Vulnerable dependencies: carry forward dependency-inventory risk flags.
Step 6 — Write findings by severity, each with evidence + confidence. No ungrounded alarm; no false reassurance. Present.

## Output format
Write a standard SDLC document: numbered headers/sections from the template (Overview first, Evidence Notes last), with a trailing machine block kept in sync for downstream skills and consolidate. The structure is the template's; the evidence discipline stays INLINE — every factual line is tagged observed|inferred|uncertain and observed lines cite a source.
Per `references/_SHARED-discovery-contract.md`: every claim carries confidence; observed claims cite a source
(a per-service artifact entry or a code line). Synthesis/judgment claims are `inferred` and say what
they were inferred from. See `examples/security-posture.md` (worked example).

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: You found serious vulnerabilities. Findings are this skill's product, not a reason to escalate: rank them and complete.
