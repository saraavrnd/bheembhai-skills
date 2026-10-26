# Discovery Phase — Onboarding a Brownfield Repo into BheemBhai

Discovery reverse-engineers a repo that has only source code into the knowledge base BheemBhai's
delivery skills expect — so that afterward, story-design/implement run on it exactly as on a
greenfield project. Discovery is the bridge from "raw repo" to "BheemBhai-shaped repo".

## The two layers
1. **Evidence** (`docs/discovery/`) — per-service + system artifacts, every claim source-cited and
   confidence-tagged (observed/inferred/uncertain). The permanent, auditable provenance. Governed
   by `_SHARED-discovery-contract.md`.
2. **Canonical** (`docs/architecture.md`, `docs/tech-stack.md`, `docs/data-model.md`,
   `docs/api-contracts/`, `docs/testing-strategy.md`) — composed from the evidence by
   `sdlc-discovery-consolidate`, in the greenfield shape delivery reads. Carries a provenance banner;
   the evidence layer is never deleted.

## The skills (14), in workflow order
- `sdlc-discovery-init` — detect services, bootstrap AGENTS.md + docs/discovery/ (nothing exists yet).
- PER-SERVICE (fan-out, cheap/haiku, pack-driven extraction, one pass per service):
  `sdlc-discovery-stack-detect` (keystone — selects the knowledge pack) → `sdlc-discovery-structure-map` →
  `sdlc-discovery-dependency-inventory` → `sdlc-discovery-api-surface` → `sdlc-discovery-data-model` →
  `sdlc-discovery-build-run` → `sdlc-discovery-test-coverage-map`.
- SYSTEM synthesis (fan-in, sonnet/opus, judgment, reads all services):
  `sdlc-discovery-integration-map` → `sdlc-discovery-architecture` → `sdlc-discovery-security-posture` →
  `sdlc-discovery-conventions` → `sdlc-discovery-risk-register` → `sdlc-discovery-glossary`.
- `sdlc-discovery-consolidate` (capstone, opus) — compose the canonical docs; hardest review gate.

## Generic skills + knowledge packs
Skills are tech-agnostic; per-stack specifics live in knowledge packs (flat data, no logic). The
pack files are bundled inside `sdlc-discovery-stack-detect` (`references/knowledge-packs/*.yaml`) —
NOT in a shared folder, because BheemBhai runs each skill in a container that sees only its own
folder. `sdlc-discovery-stack-detect` is the only skill that reads them: it selects the matching pack
and **embeds that pack's data into `stack.md`** (`embedded_pack:`). Every downstream skill reads
the pack data from `stack.md`, never from the pack files. Add a stack = add a pack file to
`sdlc-discovery-stack-detect`, no other skill change.
Shipped packs: laravel, nestjs, express, fastapi. No pack matched → inference mode (honest,
lower-confidence), never a wrong guess.

## Workflow & policy
`config/workflow-discovery.yaml` stitches the skills (per-service fan-out → system fan-in →
consolidate). `config/policy-discovery-governed.yaml` gates the parent's high-stakes checkpoints
(init topology, architecture, security, and the consolidate capstone) for human review; the stack
verdict is gated by the per-service chain's own policy (`discovery-service-governed`) — discovery
gates HARDER than delivery, because reverse-engineered knowledge that is wrong silently misleads
every future feature.

## Complexity tiers (cost)
Every skill declares a COMPLEXITY tier, not a model: LOW (mechanical extraction), MEDIUM
(cross-service synthesis), HIGH (architecture, security, consolidate — high-stakes judgment).
BheemBhai maps tier -> model per project via the project model profile, so the same skills run on
whatever models a given deployment/project assigns to low/medium/high. Most of discovery is LOW
(cheap) with a thin MEDIUM/HIGH layer on top.

## Verifiability
There is no test suite for an extraction, so each skill runs a SELF-CHECK against the evidence
contract before finishing (every observed claim's source resolves; nothing uncited is asserted as
fact; coverage and confidence are truthful) — see `_SHARED-discovery-verifiability.md`. The outcome
vocabulary (BB_OUTCOME / BB_REVIEW and what completed / BLOCK / escalation_required mean) is OWNED
by BheemBhai and injected at runtime — skills do not restate it. A skill's `## Outcomes`
section, where it has one, names only the calls `verify.yaml` cannot make in code. The review signal (BB_REVIEW) is
aimed at the low-confidence, high-impact claims, so the human gate lands where the reverse-
engineering is most likely wrong.
