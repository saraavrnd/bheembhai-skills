---
name: sdlc-discovery-dependency-inventory
description: >
  Inventory one service'"'"'s third-party dependencies from its manifest and lockfile — names,
  versions, and flags for outdated or known-vulnerable packages — into a reviewable note the
  feature-dev agent and security synthesis read. Use during Discovery AFTER sdlc-discovery-stack-detect.
  Trigger on "list dependencies", "what libraries does this use", "any outdated/vulnerable deps".
  RECORDS what is declared, with sources; flags risk signals without deep CVE research.
compatibility: >
  Tool-agnostic. Reads the service manifest + lockfile (composer.json/.lock, package.json/lock,
  pyproject/uv.lock). Optional web lookup for latest-version/known-CVE signal if available. Output
  feeds sdlc-discovery-security-posture and sdlc-discovery-risk-register.
complexity: low   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-dependency-inventory

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the BheemBhai convention is created by sdlc-discovery-init, not assumed. Use the default layout in `references/_SHARED-project-layout.md` (prefer an existing `AGENTS.md` only if a prior run wrote one). This skill reads SOURCE CODE and its own upstream discovery artifacts under `docs/discovery/` — never the canonical project docs, which are discovery OUTPUT. This skill's own `templates/`/`examples/` stay in the skill folder, never under `docs/`.

Cost & context: Runs at the frontmatter complexity tier. Read ONLY the manifest and lockfile — not
source. Keep the list to direct/top-level dependencies plus any transitive dep that carries a known
risk flag; do not enumerate the entire transitive tree.

The "what it depends on" for one service. Dependencies are both capability and risk surface — an
outdated or vulnerable library is where features break and breaches happen. This records the
declared set and flags the obvious risk signals (clearly old pins, packages with well-known CVEs);
deep per-CVE research is out of scope (that is a security exercise, not discovery extraction).

## Input it expects
- The service manifest + lockfile.
- `docs/discovery/<SERVICE>/stack.md` (for the manifest location from the pack).
- Shared: `references/_SHARED-discovery-contract.md`. The selected pack's data (locations, patterns, commands, risk_hints, glossary_hints) is embedded in `stack.md` under `embedded_pack:` — read it there; the pack files themselves live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/<SERVICE>/dependency-inventory.md`. From `templates/dependency-inventory.md.tmpl`,
presented for review.

## Procedure
Step 1 — Locate the manifest (pack `manifest`) and its lockfile. Read both.
Step 2 — List direct dependencies: name + pinned/resolved version, each sourced to the manifest line.
Step 3 — Flag risk signals you can see WITHOUT research: a version pinned far below current major;
  a package with a famously-known CVE class; an unmaintained/deprecated package. Mark these
  `uncertain` unless confirmed, and say what the signal was. If a version/CVE lookup tool is
  available, use it to upgrade a flag from `uncertain` to `observed` with the source.
Step 4 — Note the dependency manager and lockfile presence (a missing lockfile is itself a finding).
Step 5 — Write and present.

## Output format
Per `references/_SHARED-discovery-contract.md`: a deps table with version + risk flag + source. See
`examples/dependency-inventory-LEARN-portal.md`.
