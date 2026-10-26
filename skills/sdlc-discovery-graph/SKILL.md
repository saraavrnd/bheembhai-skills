---
name: sdlc-discovery-graph
description: >
  Builds the code graph for one service by running graphify (the graphify Claude Code plugin
  installed in the BheemBhai container) over the service source, into a per-service graph store.
  Runs once per service, right after sdlc-discovery-stack-detect. Downstream per-service and synthesis
  skills then query that graph with graphify's four verbs (query, explain, path, affected) to get
  structural knowledge as observed, source-referenced evidence. graphify is multi-language, so this
  one skill works for every stack.
compatibility: >
  Requires the graphify plugin in the step container (Claude Code plugin). Tool-agnostic otherwise.
  Builds into a per-service GRAPHIFY_OUT under docs/discovery/<service>/. No code execution of the
  target repo beyond graphify's own static extraction.
complexity: low   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile
---

# sdlc-discovery-graph

**Artifact paths:** The BheemBhai convention is created by `sdlc-discovery-init`; until `AGENTS.md`
exists, use the default layout (`references/_SHARED-project-layout.md`). This skill builds the graph into the
per-service discovery folder `docs/discovery/<SERVICE>/graphify-out/` and writes a short index
(`graph.md`) beside it. It reads the **service source code**; it does not read the canonical
`docs/` files (those are discovery OUTPUT). This skill's own `references/`, `templates/`,
`examples/` stay in the skill folder.

**Cost & context:** Runs at the frontmatter complexity tier — the work is mechanical (run graphify,
confirm it built, summarize). graphify does the extraction; do NOT read source into context. After
the build, use graphify's verbs for anything you need rather than reading the raw `graph.json`.

## What this skill does

You run **once per service**, immediately after `sdlc-discovery-stack-detect`. Your job: **build the
code graph for this service with graphify**, into a per-service store, and record where it is — so
every downstream skill can query it with graphify's four verbs and cite the results as observed
evidence. You do not interpret the architecture; you build the graph and index it.

graphify is installed as a Claude Code plugin in the container, so its commands are available to
you directly. See `references/graphify-verbs.md` for the build command and the four query verbs.

## Input it expects

- The checked-out service source (the current git workspace, scoped to this service's `root`).
- `docs/discovery/<SERVICE>/stack.md` — for the service language/root (graphify is multi-language,
  so no per-stack extractor selection is needed; `stack.md` still orients scope and sanity checks).
- graphify, available in the container (the plugin). If graphify is unavailable, record that and
  emit an empty graph index with `confidence: uncertain` — downstream skills then degrade to
  reading source directly.

## Output it produces

Two things in `docs/discovery/<SERVICE>/`:
1. **`graphify-out/graph.json`** — the graph store graphify built. Downstream skills pass this as
   `--graph docs/discovery/<SERVICE>/graphify-out/graph.json` to every verb. Produced by graphify;
   never hand-edit.
2. **`graph.md`** — a short human index from `templates/graph.md.tmpl`: what was built, the graph
   path, scale (node/edge counts if graphify reports them), and the fixed note that downstream
   skills query this graph via graphify verbs. This is the hand-off record; the store is the truth.
   Worked example: `examples/graph-learn-portal.md`.

## Procedure

1. **Build the graph with graphify**, scoped to this service and isolated per service:
   ```bash
   GRAPHIFY_OUT=docs/discovery/<SERVICE>/graphify-out graphify extract <SERVICE_ROOT> --code-only
   ```
   Setting a per-service `GRAPHIFY_OUT` is REQUIRED — in the fan-out every service shares the
   checkout, and the default `graphify-out/` would be clobbered across branches.
2. **Confirm it built** — `docs/discovery/<SERVICE>/graphify-out/graph.json` exists and is
   non-trivial. If graphify failed or the graph is empty (unsupported stack, extraction error),
   say so in `graph.md` and lower confidence; do not fabricate.
3. **Smoke-test one verb** so the hand-off is trustworthy — e.g.
   `graphify query "entry points" --budget 500 --graph docs/discovery/<SERVICE>/graphify-out/graph.json`
   and confirm it returns nodes with source references.
4. **Write `graph.md`** — the graph path, scale, and the standard "how to query" note. Keep it an
   INDEX, not a description of the code.

## Hand-off (feeds the downstream discovery skills)

The built graph is the shared evidence base for the rest of the per-service phase and the system
synthesis. Downstream skills do NOT read `graph.json` directly — they call graphify's verbs against
`docs/discovery/<SERVICE>/graphify-out/graph.json`:

- **sdlc-discovery-architecture** — `query "entry points"/"database access"`, `explain "<hub>"`,
  `path "<layerA>" "<layerB>"`; at the system layer, reads every service's graph for cross-service
  structure.
- **sdlc-discovery-api-surface** — `query "request validation"/routing`, `path "<route>" "<repository>"`.
- **sdlc-discovery-data-model** — `explain "<model/entity node>"` to see its source, cluster, and uses.
- **sdlc-discovery-security-posture** — `affected "<secrets/crypto/subprocess node>"` for blast radius /
  reachability.
- **sdlc-discovery-risk-register** — `affected "<fragile module>"` for impact.

Each cites the returned relation's source reference as `observed`; claims that rest on a missing
path or empty `affected` set are `inferred` (graphify sees static structure only). If the graph is
absent, consumers degrade to reading source and mark findings `inferred`. graphify is an amplifier,
never a hard dependency.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: Graphify could not build a graph for this service, and `graph.md` says so and why.
