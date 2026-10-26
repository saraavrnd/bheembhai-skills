---
name: sdlc-discovery-integration-map
description: >
  Map how the services and external systems connect — who calls whom, over what (HTTP, queue,
  shared DB), and which third-party/external APIs each service talks to — into a system-level
  integration map. Use during Discovery AFTER the per-service skills have run for ALL services
  (it synthesizes across them). Trigger on "map the integrations", "how do services talk", "what
  external systems does this call". Especially critical for multi-service repos, where the most
  important knowledge lives BETWEEN services and no single repo reveals it.
compatibility: >
  Tool-agnostic. Reads every service'"'"'s docs/discovery/<SERVICE>/{api-surface,structure-map,
  dependency-inventory}.md plus targeted source (outbound-call patterns from each pack). No MCP.
  Output is the system integration map consumed by sdlc-discovery-architecture and the feature agent.
complexity: medium   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-integration-map

Artifact paths: Discovery runs on a freshly-acquired brownfield repo; the convention is created by sdlc-discovery-init. Use the default layout in `references/_SHARED-project-layout.md`. This is a SYSTEM-LEVEL synthesis skill: it reads the per-service discovery artifacts (`docs/discovery/<SERVICE>/*.md` for every service in `docs/discovery/services.md`) and writes to `docs/discovery/_system/`. It reads discovery's own artifacts and source code only — never the canonical project docs, which are discovery OUTPUT. Own `templates/`/`examples/` stay in the skill folder.

Cost & context: Runs at the frontmatter complexity tier (standard — this is synthesis, not
extraction). Read the per-service artifacts (already distilled) first; only grep source for each
pack'"'"'s `patterns.external_call` to find outbound calls the per-service maps didn'"'"'t capture. Do not
re-read whole services — the per-service artifacts are your primary input.

The "how it all connects" for the system. In a services architecture the load-bearing knowledge is
often BETWEEN the services — who calls whom, what queues couple them, what external APIs they
depend on — and that truth is in no single repo. This fans in the per-service findings and the
outbound-call evidence into one map. It is a review checkpoint: a wrong edge (a dependency that
isn'"'"'t real, or a missed coupling) misleads every cross-service feature.

## Input it expects
- `docs/discovery/services.md` (the service list).
- For each service: its `api-surface.md` (inbound surface), `structure-map.md`,
  `dependency-inventory.md` (external SDKs hint at integrations), and `stack.md` (for the pack).
- Source, only to grep each pack'"'"'s `patterns.external_call`.
- Shared: `references/_SHARED-discovery-contract.md`. Each service's selected pack data is embedded in that service's `stack.md` (`embedded_pack:`) — read it there; the pack files live only in sdlc-discovery-stack-detect and are not reachable here.

## Output it produces
`docs/discovery/_system/integration-map.md`. From `templates/integration-map.md.tmpl`, presented
for review.

## Procedure
Step 1 — Read `services.md` and each service'"'"'s per-service artifacts.
Step 2 — Inbound surfaces: each service'"'"'s `api-surface.md` is what it EXPOSES. Record as nodes.
Step 3 — Outbound calls: for each service, grep its pack'"'"'s `patterns.external_call` to find where
  it calls OUT. Resolve each target: another internal service (match the URL/host to a known
  service'"'"'s surface) or an external system (a third-party API, by hostname/SDK). Record each as a
  directed edge with its source line.
Step 4 — Couplings beyond HTTP: shared databases (two services pointing at the same DB from their
  build-run env), message queues/brokers (a dependency like redis/rabbitmq/kafka + publish/consume
  calls). Record these as edges with their kind.
Step 5 — External dependencies: third-party APIs each service integrates with (payment, email,
  auth providers, cloud SDKs) from dependency-inventory + call sites.
Step 6 — Flag confidence honestly: an edge inferred from a hostname is `inferred`; one traced to a
  concrete client+URL is `observed`. A suspected-but-unconfirmed coupling is `uncertain`.
Step 7 — Write and present.

## Output format
Write a standard SDLC document: numbered headers/sections from the template (Overview first, Evidence Notes last), with a trailing machine block kept in sync for downstream skills and consolidate. The structure is the template's; the evidence discipline stays INLINE — every factual line is tagged observed|inferred|uncertain and observed lines cite a source.
Per `references/_SHARED-discovery-contract.md`: nodes (services + external systems) and directed edges, each
edge sourced. See `examples/integration-map-LEARN-portal.md`.
