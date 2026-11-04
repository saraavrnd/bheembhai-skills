# Template guide — sdlc-deliver-story-design

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/story-design.md.tmpl`

### Story Design — {{story_key}}: {{story_title}} — the line `**Domain:** {{backend | frontend | full-stack}}`

drives which implement lens + test types

### Target module(s)

Where this lives, per architecture.md. Backend → app/<service> modules; frontend → UI
components; full-stack → both. The domain tag above should match these.

### Interfaces / endpoints

Concrete signatures sdlc-deliver-tests-write will test against. For UI: components + props/state and the
API contract(s) consumed. For backend: endpoints/functions.

### Data-model deltas

New fields/tables/migrations, or "none". Consistent with data-model.md.

### Reuse

Existing functions/components/services this builds on, named.

### Approach

2-5 sentences. Strategy, not full pseudocode.

### Out of scope

Restated from the story to keep this bounded.

### Architecture impact

Usually "none — fits existing architecture". If the story needs something the architecture
doesn't support, describe the gap and recommend escalating to sdlc-arch-design + an ADR.
Do NOT bend the architecture silently here.

### Dependencies discovered (feeds sdlc-plan-epic-sequence)

Firm produces/consumes from this design, for the sequence to self-correct.
"Consumes <endpoint/table/field/module> produced by <STORY_KEY>" → that story must precede this.
Note whether this matches the current (provisional) epic order or changes it. "none" if this
story is self-contained.

### Traceability — the line `**Requirements covered:**`

FR/NFR IDs
