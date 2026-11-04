# Template guide — sdlc-deliver-docs-sync

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/AGENTS.md.tmpl`

### What this project is

2-3 sentences.

### Stack

from tech-stack.md: languages, frameworks, stores, key tools + pinned versions

### Module map

mirrors architecture.md; updated as modules gain behavior

### Current endpoints (summary)

updated by sdlc-deliver-docs-sync as stories add endpoints; full shapes in api-contracts/

### Data entities (summary)

updated as stories add/change fields; full model in data-model.md

### Conventions

branch naming, error handling, logging, config, testing approach (TDD)

## `templates/design-sync-note.md.tmpl`

### What this story changed (vs current design)

endpoints / data fields / module behavior / integrations / config

### Reference updates committed to this branch

Only files that actually changed. "none" if no-op.

### Structural-change check

If this story made a structural change that did NOT go through a sdlc-arch-design amendment,
flag it here and recommend pausing to amend sdlc-arch-design + add an ADR. Usually "none".
