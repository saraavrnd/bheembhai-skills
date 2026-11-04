# Template guide — sdlc-discovery-api-surface

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/api-surface.md.tmpl`

### Top of file

Discovery hand-off: the HTTP/API surface of one service.
Written to docs/discovery/<SERVICE>/api-surface.md. An INDEX into the code, not a re-description.
Every endpoint row carries confidence + a source pointer. Read by security-posture,
integration-map, and (in delivery) by sdlc-deliver-story-design when a feature touches an endpoint.

## `examples/api-surface-LEARN-portal.md`

### Top of file

Worked example: api-surface for the Learn Portal backend (fastapi pack).
Written to docs/discovery/learn-portal/api-surface.md. Sources are the real router lines.
