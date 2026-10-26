<!-- Flat reference: how discovery skills build and query the code graph with the graphify CLI
     (installed as a Claude Code plugin in the BheemBhai container). No logic — the contract and the
     four query verbs, with how each maps to a discovery need. Confirm flags against
     https://docs.graphify.com/reference/overview for the installed graphify version
     (`graphify --version`); the forms below are the stable shape, not every flag. -->

# graphify — build & query reference

graphify is a code-graph tool available in the step container as a Claude Code plugin. It BUILDS a
graph from source and ANSWERS queries over it with four verbs. Discovery uses it instead of a
hand-written extractor: graphify is multi-language, so the same commands work for every stack.

## Build (sdlc-discovery-graph does this, once per service)

```bash
# scope to the service root; code-only keeps it to source structure
GRAPHIFY_OUT=docs/discovery/<SERVICE>/graphify-out graphify extract <SERVICE_ROOT> --code-only
```

- Output: `<GRAPHIFY_OUT>/graph.json` (default `graphify-out/graph.json` when GRAPHIFY_OUT is unset).
- **Per-service GRAPHIFY_OUT is mandatory in the fan-out.** Each service's child run shares the
  checkout; writing every service's graph to the default `graphify-out/` would clobber. Set
  `GRAPHIFY_OUT` to the service's own discovery folder so branches never collide (the graphify docs
  give this same guidance for worktrees).
- Every later query in that service points at this graph with `--graph <GRAPHIFY_OUT>/graph.json`.

## The four query verbs (downstream skills call these)

All return **graph context** — nodes, relations, provenance, and source references. graphify's own
caveat: *"the response is graph context, not an independently verified natural-language answer."*
That maps onto the discovery evidence contract exactly — treat a returned relation as `observed`
and cite its source ref; never treat the verb's output as a verdict.

### 1. `query` — retrieve a neighborhood around a question
```bash
graphify query "<question>" [--budget <tokens>] [--dfs] [--context call] --graph <path>
```
- Input: a natural-language question or keywords. `--budget` (default 2000) caps output size;
  `--context call` filters to call edges; `--dfs` for depth-first.
- Returns: a compact neighborhood (nodes + relations + provenance + source refs).
- Discovery use: broad "get context around X" — `"entry points"`, `"request validation"`,
  `"database access"`. Used by architecture, api-surface, conventions.

### 2. `explain` — inspect one node
```bash
graphify explain "<node>" --graph <path>
```
- Input: a single node label or id (take the precise id from a `query` result when names collide).
- Returns: that node's source file, the community/cluster it belongs to, and its connected
  relationships.
- Discovery use: inspect one concept precisely — a model/entity (data-model), a hub (architecture).

### 3. `path` — shortest relationship path between two concepts
```bash
graphify path "<source>" "<target>" [--directed|--undirected] --graph <path>
```
- Input: two node labels/ids/keywords. `--directed` (default) respects edge direction;
  `--undirected` ignores it.
- Returns: the shortest path, each relationship carrying its evidence.
- Caveat (graphify's): a source-level path does not prove a runtime input executes it; NO path does
  not prove independence (relations may be missing/unresolved). Tag accordingly.
- Discovery use: route→repository (api-surface), does layer A reach layer B (architecture),
  service→datastore (integration-map).

### 4. `affected` — reverse traversal: nodes impacted by a node
```bash
graphify affected "<node>" --graph <path>
```
- Input: a single node label/id. (Per `graphify --help`, the form is `affected "X"`; no relation/
  depth flags are documented — the whole dependent set is returned.)
- Returns: by **reverse traversal**, the nodes **impacted by** `<node>` — i.e. its dependents,
  everything downstream that would be affected if it changed. This is "who depends on X" / X's
  blast radius, not "what X reaches" (for a directional reach from A to B, use `path`).
- Discovery use: the dependents of a sensitive node — what touches the secrets/crypto/subprocess
  module (security-posture), the blast radius of a fragile module (risk-register).

## MCP equivalents (if graphify is reached as MCP rather than CLI)
`explain` ≈ `get_node` then `get_neighbors`; `path` ≈ `shortest_path` (accepts `max_hops`). Same
semantics; the CLI forms above are the default integration.

## Evidence discipline (unchanged contract)
- A returned relation with a source ref → `observed`, cite the ref.
- A `path` result, or "no path", or an `affected` set → still static-analysis context: dynamic
  wiring (DI, dynamic dispatch, string routing) may not be represented. Claims resting on absence
  are `inferred`, never `observed`.
- If `graphify extract` produced no graph for the stack, or a verb returns empty → degrade to
  reading source directly and mark findings `inferred`. graphify is an amplifier, not a hard dep.
