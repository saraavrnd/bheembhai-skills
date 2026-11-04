# Template guide — sdlc-discovery-stack-detect

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/stack.md.tmpl`

### Top of file

Discovery hand-off: tech stack for one service. Written to docs/discovery/<SERVICE>/stack.md
Read by every downstream discovery skill. It carries BOTH the detection findings AND an
embedded copy of the selected knowledge pack's data — because downstream skills cannot read
the pack files (those live only in sdlc-discovery-stack-detect's folder; each skill's container
sees only its own folder). Every finding carries confidence and, when observed, a source.

## `examples/stack-LEARN-portal.md`

### Top of file

Worked example: stack-detect output for the Learn Portal backend service.
Written to docs/discovery/learn-portal/stack.md. Confident match.
