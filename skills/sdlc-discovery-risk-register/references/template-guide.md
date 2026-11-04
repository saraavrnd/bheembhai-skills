# Template guide — sdlc-discovery-risk-register

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/risk-register.md.tmpl`

### Top of file

Discovery hand-off (system): risk-register.md -> docs/discovery/_system/risk-register.md
SDLC-standard Risk Register. Readable summary + detailed register on top, machine block at the
bottom. Every risk keeps a confidence tag + source and a severity. A risk may be `inferred`
(a judgment from observed facts) — tag it so; the evidence it rests on stays `observed`.

### 1. Overview

2-4 sentences: the overall risk picture; the few risks that dominate.

### 3. Detailed Register

Highest severity first. Evidence cites the artifact/code that establishes the risk.

## `examples/risk-register.md`

### Top of file

Worked example: SDLC-structured risk-register.md for Learn Portal.
