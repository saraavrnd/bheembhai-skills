# Template guide — sdlc-plan-epic-review

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/epic-review.md.tmpl`

### Context loaded

Every story in the epic (list them), which architecture/data-model/api-contract/ADR/
ui-conventions slices were read, and which other epics were checked for legitimate
cross-epic dependencies.

### Findings

One entry per real cross-story gap that survived references/gap-checklist.md's categories.
Name every story key each gap touches. Single-story concerns are sdlc-plan-story-review's job.

### Open questions

Numbered. One per product decision the gate reviewer must answer before stories-write
revises. "None." when every finding is a wording fix.

### Proposed changes

Per touched story: what sdlc-plan-stories-write (revise) should change — statement, acceptance
criteria, out of scope, notes/dependencies — and which finding it closes. Proposed, not applied.

### Architecture impact

"None." OR a gap that needs something the architecture doesn't support and isn't credibly any
epic's planned deliverable — state that sdlc-arch-design (amend mode) should run first.

### Requirement coverage check

Every FR/NFR epic-map.json assigns to this epic is exercised by at least one story's
acceptance criteria, with no contradicting claims: yes/no + notes.

### Dependency-note sanity check

Every "Depends on X" / "prerequisite for Y" note refers to a real story and is reciprocated:
yes/no + mismatches. Not a build-order computation — that's sdlc-plan-epic-sequence.
