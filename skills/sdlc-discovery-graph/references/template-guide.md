# Template guide — sdlc-discovery-graph

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/graph.md.tmpl`

### Top of file

Human index for the service graph graphify built. Written to docs/discovery/<SERVICE>/graph.md.
An INDEX + hand-off record, not a description of the code. The real artifact is the graphify
store at graphify-out/graph.json; downstream skills query it via graphify verbs.

### Scale

From graphify's build output if it reports counts; otherwise "see store".

### Smoke test

The one verb call run to confirm the graph answers queries.

## `examples/graph-learn-portal.md`

### Top of file

Worked example: sdlc-discovery-graph hand-off for the learn-portal service, built with graphify.
Shows the graph store location + the verb calls downstream skills run against it.
