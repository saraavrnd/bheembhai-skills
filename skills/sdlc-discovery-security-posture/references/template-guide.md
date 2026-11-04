# Template guide — sdlc-discovery-security-posture

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/security-posture.md.tmpl`

### Top of file

Discovery hand-off (system): security-posture.md -> docs/discovery/_system/security-posture.md
SDLC-standard Security Posture document. Readable domain sections on top; machine block of
severity-ranked findings at the bottom. Every line keeps a confidence tag + source; security
findings also carry a severity. "None observed." where a control is absent — say so explicitly,
since absence of a control IS a finding.

### 1. Overview

2-4 sentences: the overall posture and the single biggest honest caveat.

### 8. Findings (severity-ranked)

The actionable list. Highest severity first.

## `examples/security-posture.md`

### Top of file

Worked example: SDLC-structured security-posture.md for Learn Portal. Readable domain sections
+ severity-ranked findings + machine block. Every line tagged + sourced.
