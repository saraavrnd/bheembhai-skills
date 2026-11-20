# Template guide — sdlc-plan-idea-frame

Guidance for filling `templates/idea-brief.md.tmpl`, section by section. Read the part for a
section before you fill it. Do not copy this guidance into the output.

## `templates/idea-brief.md.tmpl`

### 1. Idea as given

The input, quoted or closely paraphrased. Nothing added, nothing improved. For a long input,
quote the lines that define the product and summarise the rest in one sentence each.

### 2. Problem

2–4 sentences: who has the pain, what the pain is, why it matters now. No solution, no feature
names.

### 3. Target users

Only the user types whose needs would change what gets built. "Everyone" is not a user type.

### 4. Value hypothesis

One falsifiable sentence. The measurable change becomes a success-metric candidate in the PRD.

### 5. Assumptions

One row per claim the PRD will rely on. `Basis` is `Stated` (the input says it) or `Inferred`
(you concluded it). Every `Inferred` row says why. If an assumption is risky enough that a wrong
guess changes the PRD's shape, it belongs in Open questions instead.

### 6. Constraints

Hard limits the input names or implies: platform, compliance regime, budget, deadline, data
residency, integrations that must be used. Mark inferred ones "(inferred)".

### 7. Non-goals

What this product will deliberately not do, so the PRD's out-of-scope list starts from something.

### 8. Open questions

`Q-n` rows. `Kind` is `Blocking` or `Non-blocking` (see `references/question-guide.md`). Every row
has a proposed default that `sdlc-plan-prd-write` can adopt if no answer is given. About seven
questions at most.

### 9. Readiness

Exactly one of `Ready for PRD` or `Needs framing`, optionally followed by one sentence of reason.
