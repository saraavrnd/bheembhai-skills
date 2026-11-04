# Template guide — sdlc-discovery-init

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/project-layout.md.tmpl`

### Top of file

Template: the AGENTS.md Project Layout table sdlc-discovery-init seeds at the repo root.
Copy the table into AGENTS.md (create the file if absent). The discovery rows are REQUIRED —
every downstream skill resolves docs/discovery/ paths through them. The delivery rows are the
standard BheemBhai layout later phases use; keep them so the repo is ready for development.
If AGENTS.md already carries a Project Layout table, add only the missing rows.

### Project Layout

The per-story filename set (story-design.md, test-plan.md, verification.md, code-review.md,
design-sync.md) and the per-epic set (story-map.json, epic-sequence.md, epic-review.md)
live INSIDE their folders — see the delivery skills.

## `templates/services.md.tmpl`

### Top of file

Discovery hand-off: the services this repo contains, driving the per-service fan-out.
Written to docs/discovery/services.md. The parent workflow's fan-out node parses the fenced
block below (info string `bheembhai:foreach`, select `$.services[*]`) and starts ONE child
run per entry; each entry's `id` becomes that service's docs/discovery/<id>/ folder.
Keep it valid YAML: unique, filesystem-safe ids.
A SERVICE is a separately deployable/runnable unit (own Dockerfile, own compose `build:`, or
own manifest) — NOT every dir with a manifest. Off-the-shelf infra (compose `image:`-only:
postgres, redis, …) and components that run inside another service are NOT services; mention
them in `summary`, don't list them here. See references/service-boundary-heuristics.md.

## `examples/AGENTS-LEARN-portal.md`

### Top of file

Worked example: the AGENTS.md sdlc-discovery-init writes for Learn Portal (repo had none).

## `examples/services-LEARN-portal.md`

### Top of file

Worked example: polyglot repo (Learn Portal). topology=multi, TWO first-party services.
Note how detection comes from docker-compose.yml + the Dockerfiles, NOT just manifests:
embedding_service has no pyproject.toml of its own yet is a service (own Dockerfile, own
compose build context, own port). ingestion_pipeline is a COMPONENT of the api service
(no Dockerfile/manifest; runs on the shared prefect-worker image against the api codebase),
so it is noted in summary but NOT a fan-out entry. The infra images (postgres, redis, minio,
ollama, langfuse, mailhog) are dependencies, not services. The fence info string is what the
parent workflow's fan-out node looks for.
