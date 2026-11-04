# Template guide — sdlc-discovery-build-run

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/build-run.md.tmpl`

### Top of file

Discovery hand-off: how to build/run/test one service. docs/discovery/<SERVICE>/build-run.md.
Project's own scripts win over pack defaults. Env var NAMES only, never values.
A pack default with no project script is confidence: inferred with a `basis:` naming the
pack and the missing project script — never observed.

## `examples/build-run-LEARN-portal.md`

### Top of file

Worked example: build-run for Learn Portal (fastapi pack). Commands from pyproject/compose + pack.
