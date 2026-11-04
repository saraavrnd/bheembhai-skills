# Template guide — sdlc-plan-epics-create

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/epic.md.tmpl`

### Description

The problem this epic solves, the domain context, the users/actors, and the value it delivers.
Write this so a Jira reader with no PRD context can still understand why the epic exists.

### Functional scope

The concrete capabilities this epic must deliver. Include the key workflows, inputs/outputs,
integrations, data touched, edge cases, and any non-goals that help the reader understand scope.

### Implementation guidance / dependency order

Recommended build sequence for the stories inside the epic. Call out what should be built
first, what depends on it, and any prerequisite models/services/integrations.

### Goal / Definition of Done

When is this epic complete? What can a user do that they couldn't before?

### Covered requirements (traceability)

Every FR/NFR ID rolled into this epic. These must come from the PRD verbatim.

### MVP subset (if release = mixed)

Which of the above are MVP vs Later.

### Notes

Dependencies on other epics, sequencing hints, rollout notes, risks, or out-of-scope details.
