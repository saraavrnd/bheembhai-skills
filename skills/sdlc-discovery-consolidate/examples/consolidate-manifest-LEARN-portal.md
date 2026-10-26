<!-- Worked example: what sdlc-discovery-consolidate produces for Learn Portal, and from what. -->
```yaml
artifact: consolidate-manifest
generated: 2026-10-01
canonical_docs:
  - path: docs/architecture.md
    composed_from: [docs/discovery/_system/architecture.md, docs/discovery/_system/integration-map.md]
    shape: "sdlc-arch-design templates/architecture.md.tmpl"
  - path: docs/tech-stack.md
    composed_from: [docs/discovery/learn-portal/stack.md, docs/discovery/learn-portal/dependency-inventory.md]
  - path: docs/data-model.md
    composed_from: [docs/discovery/learn-portal/data-model.md]
  - path: docs/api-contracts/learn-portal.openapi.yaml
    composed_from: [docs/discovery/learn-portal/api-surface.md]
    note: "api-surface endpoints emitted as OpenAPI paths"
  - path: docs/testing-strategy.md
    composed_from: [docs/discovery/learn-portal/test-coverage-map.md]
    note: "documents what EXISTS + the gaps, not an idealized strategy"
evidence_retained: docs/discovery/      # permanent provenance — never deleted
all_docs_carry: provenance-banner
gate: "human approval required — ratifies reverse-engineered knowledge as project truth"
```
