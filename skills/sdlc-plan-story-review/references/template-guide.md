# Template guide — sdlc-plan-story-review

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/story-review.md.tmpl`

### Context loaded

Which architecture/data-model/api-contract/ADR/ui-conventions slices were read, and which
sibling stories were checked for overlap.

### Findings

One entry per real gap that survived references/gap-checklist.md's categories. "None." when
the story is clean.

### Open questions

Numbered. One per product decision the gate reviewer must answer before stories-write
revises. "None." when every finding is a wording fix.

### Proposed changes

What sdlc-plan-stories-write (revise) should change in the story statement, acceptance criteria
(Gherkin) and out of scope, and which finding each change closes. Proposed, not applied.

### Architecture impact

"None." OR a gap that needs something the architecture doesn't support — state that
sdlc-arch-design (amend mode) should run before sdlc-deliver-story-design starts on this story.

### Traceability check

The FR/NFR IDs this story claims still match PRD.md wording: yes/no + notes.
