# Knowledge Pack Schema

A knowledge pack is **flat reference data** (no logic) that makes the generic discovery skills
tech-specific at runtime. One pack per tech stack. `stack-detect` selects the pack; every
downstream skill reads it to know *where things live* and *what they look like*, instead of
rediscovering a framework's conventions from scratch (slow, expensive, hallucination-prone).

This is the model-profile pattern applied to codebase knowledge: add a stack by dropping a new
pack file — **no skill changes**.

Packs live with the PLATFORM (shared across all projects using that tech), not in a per-project
image. Selected by `BB_STACK_PACK` or by `stack-detect`'s output.

## Rule: data only, never logic

If a pack starts containing extraction scripts or conditionals, it has become a mini-skill and
the maintenance problem is back. Keep *how to extract* in the generic skill; keep *where/what*
in the pack. A pack is read, not executed.

## Fields

```yaml
stack: <id>                      # unique key, e.g. laravel, fastapi, nestjs, express

detect:                          # how stack-detect recognizes this stack (any match = candidate;
                                 # score by how many hit). Ordered strongest-signal first.
  - file_exists: <path>          # a file whose presence is near-proof (e.g. artisan, nest-cli.json)
  - dep_present: <name>          # a dependency in the manifest (composer.json/package.json)
  - glob_exists: <pattern>       # a path pattern that, if present, signals this stack

language: <lang>                 # php, javascript, typescript, python
manifest: <file>                 # composer.json, package.json, pyproject.toml — the dep source
version_hint:                    # where the framework version is declared (for stack-detect)
  file: <path>
  key: <json-path-or-pattern>

locations:                       # WHERE things live — the mechanical gold. Lists = try in order.
  routes:        [<paths>]
  controllers:   <path>
  models:        <path>          # ORM entities
  migrations:    <path>
  config:        <path>
  tests:         <path>
  env_example:   <path>          # .env.example etc. — signals config surface
  entrypoint:    <path>          # the app bootstrap

patterns:                        # WHAT things look like — regexes to locate/confirm, not parse
  route:         "<regex>"
  model:         "<regex>"
  auth:          "<regex>"       # how auth/authorization is declared
  external_call: "<regex>"       # how the service calls OUT (for integration-map)

commands:                        # how to build/run/test THIS stack (for build-run skill)
  install: "<cmd>"
  test:    "<cmd>"
  run:     "<cmd>"
  migrate: "<cmd>"

risk_hints:                      # advisory for synthesis skills (security, risk-register)
  - "<a known footgun pattern for this stack>"

glossary_hints:                  # where domain vocabulary tends to live
  - "<path or pattern>"
```

## Graceful absence

If no pack matches, `stack-detect` returns `stack: unknown` and downstream skills run in
inference mode (CONTRACT.md). A missing pack is a *known, handled* state — never a hard failure.

## Validation (packs can be wrong — test them)

A wrong `locations.routes` silently breaks every route extraction for that stack. So each pack
SHOULD be validated against a known reference repo of that stack: run the mechanical skills with
the pack, assert they find the known endpoints/models. Packs are data, but data that can be
wrong, so they get the same test discipline as code.
