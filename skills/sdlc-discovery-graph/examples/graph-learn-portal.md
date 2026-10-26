<!-- Worked example: sdlc-discovery-graph hand-off for the learn-portal service, built with graphify.
     Shows the graph store location + the verb calls downstream skills run against it. -->
```yaml
artifact: graph
service: learn-portal
generated: 2026-10-10
nodes: 69
```

# Service graph — learn-portal

**Built by:** graphify (`GRAPHIFY_OUT=docs/discovery/learn-portal/graphify-out graphify extract app --code-only`) · **generated:** 2026-10-10
**Graph store:** `docs/discovery/learn-portal/graphify-out/graph.json`  ← pass as `--graph` to every verb
**Status:** built

## Scale
- Nodes: 69 · relations: ~111 import/call · languages: python

## Smoke test
`graphify query "entry points" --budget 500 --graph docs/discovery/learn-portal/graphify-out/graph.json`
→ returned the app bootstrap + router registrations with source refs (app/main.py:41-66)

## How downstream skills query this graph
Pass `--graph docs/discovery/learn-portal/graphify-out/graph.json` to:
- `graphify query "database access" --context call` — architecture: how the app reaches Postgres
- `graphify explain "app.auth.models"` — data-model: the most-depended-on model node + its uses
- `graphify path "app.ingestion.router" "app.object_storage.plugins.minio_plugin"` — api-surface: route → object storage
- `graphify affected "app.secure_storage"` — security-posture: blast radius of the secret store

## Evidence note
graphify returns graph context, not a verified answer. Returned relations + source refs are
`observed` (e.g. the api→Postgres call edges). The learn-portal→embedding-service seam has NO path
in the graph — recorded as `inferred`/`uncertain`, never "proven independent", since graphify sees
static structure only (the embed call is unimplemented).
