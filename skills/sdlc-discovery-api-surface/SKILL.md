---
name: sdlc-discovery-api-surface
description: >
  Extract the HTTP/API surface of one service — every endpoint with its method, path, auth
  requirement, and handler location — into a reviewable sdlc-discovery-api-surface note the feature-dev agent
  reads to know what interfaces exist before changing them. Use this during Discovery of a
  brownfield service, AFTER sdlc-discovery-stack-detect (it reads the selected knowledge pack to know where
  routes live). Trigger when the user says "map the API", "what endpoints does this expose",
  "extract the routes", or continues discovery past stack detection. This skill LOCATES and
  RECORDS endpoints with source pointers; it does not judge security (security-posture) or map
  cross-service calls (integration-map). Every entry is evidence-backed or flagged.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads this service's docs/discovery/<SERVICE>/stack.md
  (from sdlc-discovery-stack-detect) and the knowledge pack it names. No MCP required. Output is a Markdown
  sdlc-discovery-api-surface note consumed by later discovery (security-posture, integration-map) and, in
  delivery, by sdlc-deliver-story-design when a feature touches an existing endpoint.
complexity: low   # BheemBhai maps complexity (low/medium/high) -> model via the project model profile

---

# sdlc-discovery-api-surface

Artifact paths: Discovery runs on a freshly-acquired brownfield repo, so the BheemBhai convention usually does NOT exist yet — there is typically no `AGENTS.md` and no `docs/` layout (discovery is what CREATES them). Therefore: use the **default layout** in `references/_SHARED-project-layout.md` and CREATE paths as you write; only if a prior discovery run already wrote an `AGENTS.md` Project Layout table should you prefer it. Discovery artifacts are created under `docs/discovery/` (per-service notes in `docs/discovery/<SERVICE>/`, system synthesis in `docs/discovery/_system/`). This skill reads only SOURCE CODE and its own upstream discovery artifacts — never the canonical project docs (`docs/architecture.md` etc.), which are discovery's OUTPUT, produced by `sdlc-discovery-consolidate` at the end of the phase, not its input. This skill's own `templates/`/`examples/` stay in the skill folder, never under `docs/`.

Cost & context: This skill runs at the complexity tier in its frontmatter. To avoid context bloat:
read `stack.md` and the named pack's `locations.routes`/`patterns.route`/`patterns.auth` only, then
grep those locations to LOCATE routes and read only the matched route definitions — never whole
source trees. Don't re-read what's already in context.

The "what interfaces exist" for one service. sdlc-discovery-stack-detect decided the framework and selected the
knowledge pack; this uses that pack to go straight to where routes live and records every endpoint
as a pointer into the code. It is a review checkpoint: the feature-dev agent will trust this map to
know what it can call and what it must not break, so a wrong or missing endpoint misleads every
future feature that touches the API.

This step exists so that a feature changing an endpoint starts from the real, current signature —
not a guessed one. It is pure extraction: it does not decide whether an endpoint's auth is
*correct* (that is security-posture) — only what the auth *is*, as written.

## Input it expects

- The checked-out service codebase (current git workspace).
- `docs/discovery/<SERVICE>/stack.md` from sdlc-discovery-stack-detect — specifically its `stack_pack` value.
- This service's code graph (built by sdlc-discovery-graph with graphify), when present. Query it with
  graphify verbs against `--graph docs/discovery/<SERVICE>/graphify-out/graph.json` — do NOT read
  graph.json directly: `query "request validation"/routing` for the handler neighborhood, and
  `path "<route-handler>" "<repository>"` to trace an endpoint through to what it reaches. Cite each
  returned relation's source reference as `observed`. graphify sees static structure only (dynamic
  routing / DI may not appear), so reach claims resting on a missing path are `inferred`. Absent →
  extract from source as today and mark reach claims `inferred`. See sdlc-discovery-graph's
  `references/graphify-verbs.md`.
  - If `stack_pack` names a pack → use the embedded pack data in `stack.md` (see "Knowledge pack
    access" below) and extract from known locations.
  - If `stack_pack: none` → run in INFERENCE MODE (below).
- Discovery-phase shared tooling:
  - `references/_SHARED-discovery-contract.md` — the evidence discipline (observed/inferred/uncertain,
    source pointers, terse machine-read output).

## Knowledge pack access

The selected knowledge pack's data is **embedded in `stack.md`** under `embedded_pack:` — read it
from there. `sdlc-discovery-stack-detect` is the only skill that carries the pack files (they live in
its `references/knowledge-packs/`), and because BheemBhai runs each skill in a container that sees
only its own folder, those pack files are NOT reachable here. So take `locations` (where
routes/controllers live) and `patterns` (route/auth regexes) from `stack.md`'s `embedded_pack`
block. This skill does NOT re-detect the stack — it trusts sdlc-discovery-stack-detect's verdict. If
`stack.md` has `embedded_pack: none`, run in INFERENCE MODE.

## Output it produces

One short file: `api-surface.md`, written to `docs/discovery/<SERVICE>/api-surface.md` (resolve via
`AGENTS.md`; create the folder if absent). From `templates/api-surface.md.tmpl`, presented for
review before discovery continues. It is an index into the code, not a re-description of it.

## Procedure

Step 1 — Read the upstream hand-off
Read `docs/discovery/<SERVICE>/stack.md`. Take its `stack_pack`. If `none` → go to Inference Mode.

Step 2 — Load the pack's routing knowledge
From the named pack, read `locations.routes`, `locations.controllers`, `patterns.route`,
`patterns.auth`. These tell you WHERE routes are declared and WHAT they look like.

Step 3 — Locate, then read
Grep the `patterns.route` regex within `locations.routes` (and controllers) to LOCATE every route
declaration. Read only the matched definitions and their immediate handler signature — not whole
files. For each route capture: HTTP method, path, handler symbol, and the file:line.

Step 4 — Determine auth per endpoint (as written, not as judged)
For each endpoint, look for the pack's `patterns.auth` on or near the route (middleware, guard,
dependency, decorator). Record what you find: the auth mechanism as declared, or "none found"
(flag "none found" clearly — an endpoint with no auth is a finding the reviewer needs, but say
`observed: no auth declared at <source>`, not an interpretation of whether that is wrong).

Step 5 — Record request/response shape when cheaply visible
If the framework declares a response/DTO/serializer inline (e.g. FastAPI `response_model`, a
NestJS DTO, a Laravel resource), note it with its source. Do NOT deep-trace types across the
codebase — that is beyond this map's scope; note "shape not inline-declared" and move on.

Step 6 — Write and present
Write `api-surface.md` per the contract and template. Present for review.

## Inference mode (stack_pack: none)

No pack means no known route location. Fall back to: grep broadly for common route signatures
across likely source dirs, read what matches, and record findings with `confidence: inferred`,
each saying what signal it was inferred from. State in `summary` that coverage is best-effort and
may be incomplete. Never present inferred endpoints as a complete, authoritative list.

## Output format

Follow `references/_SHARED-discovery-contract.md`. The core is an endpoints table where every row carries
a `source`. Example (see `examples/api-surface-LEARN-portal.md`):

```yaml
artifact: api-surface
service: <SERVICE>
generated: <DATE>
stack_pack: <pack|none>
summary: ><2-3 sentences; note coverage and any inference.>
endpoints:
  - method: GET
    path: /api/v1/academic-years
    handler: "list_academic_years"
    auth: "require_role(admin, teacher)"
    confidence: observed
    source: "app/school_admin/router.py:45"
    response_shape: "list[AcademicYearOut]"
coverage:
  routes_found: <n>
  locations_searched: ["<from pack locations.routes>"]
  partial: false
```

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: Dynamic routes you cannot read are listed as `uncertain` and coverage is marked `partial: true`.
