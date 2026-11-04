# Template guide — sdlc-discovery-integration-map

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/integration-map.md.tmpl`

### Top of file

Discovery hand-off (system): integration-map.md -> docs/discovery/_system/integration-map.md
SDLC-standard Integration / Interface document: readable sections on top, machine block
(nodes/edges/external_dependencies) at the bottom for downstream skills. Every factual line
keeps a confidence tag and, when observed, a source. "None observed." where a section is empty.

### 1. Overview

2-4 sentences: the shape of the system and its key couplings.

### 2. System Context

The boundary: first-party services vs external systems vs datastores.

### 4. Interfaces & Integrations

Directed edges. Planned-but-unwired seams go here as confidence: uncertain, labelled PLANNED.

## `examples/integration-map-LEARN-portal.md`

### Top of file

Worked example: SDLC-structured integration-map.md for Learn Portal. Readable sections +
machine block; every line tagged + sourced. This is the per-service synthesis the
architecture skill reads.
