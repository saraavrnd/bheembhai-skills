# Template guide — sdlc-discovery-dependency-inventory

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/dependency-inventory.md.tmpl`

### Top of file

Discovery hand-off: third-party dependencies of one service.
docs/discovery/<SERVICE>/dependency-inventory.md. Direct deps + risk-flagged transitives.

## `examples/dependency-inventory-LEARN-portal.md`

### Top of file

Worked example: dependency-inventory for Learn Portal (fastapi pack). From pyproject + uv.lock.
