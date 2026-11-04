# Template guide — sdlc-deliver-code-review

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/code-review-report.md.tmpl`

### Severity summary — the line `**Advisory note:**`

e.g. "Recommend fixing the 1 High before PR; Mediums optional."

### Tools run

linter, formatter, dependency/secret/static scanners — with key output cited as evidence

### Fix list for `sdlc-deliver-code-implement` (ordered by severity)

Concrete, actionable changes. NOT applied here — handed to sdlc-deliver-code-implement.
