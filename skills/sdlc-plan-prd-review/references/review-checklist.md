# PRD review checklist

Each category says what a real finding looks like, and what is not one. `verify.yaml` already
checks numbering, sections, release tags, declared feature areas, a numeric metric and a
security NFR on the PRD; do not repeat those.

## 1. Atomicity and testability
- **Finding:** a requirement hides a second capability behind "and", "or", "including", "such
  as"; or no one-sentence pass/fail check could be written for it ("intuitive", "fast",
  "robust").
- **Not a finding:** a requirement that is long but still one capability.
- **Proposed change:** the split, with the new requirements' wording.

## 2. Brief coverage
- **Finding:** a target user, constraint or answered question from the brief that no requirement,
  NFR, scope line or assumption carries; or a gate answer the PRD contradicts.
- **Severity:** Blocking when it is a user, a hard constraint or an answered Blocking question.

## 3. Lifecycle completeness
- **Finding:** a requirement uses an actor, entity or state (an account, a class, an uploaded
  file, an approved order) that no requirement creates and that is not marked external or out of
  scope.
- **Proposed change:** the missing creating requirement, or the assumption line that makes it
  external.

## 4. Scope and MVP boundary
- **Finding:** an MVP requirement that the value hypothesis does not need; a Later requirement
  that an MVP requirement depends on; an out-of-scope line that an in-scope requirement
  contradicts.

## 5. Non-functional coverage
- **Finding:** a constraint in the brief (compliance regime, minors, accessibility, data
  residency, platform) with no matching NFR; an NFR with no measurable threshold.

## 6. Success metrics
- **Finding:** a metric that does not measure the value hypothesis, or that no MVP requirement
  could move.

## 7. Decomposability
- **Finding:** a feature area too large to be one epic (roughly 15+ requirements) or two areas
  that only make sense together; a requirement in the wrong area so that its epic would depend
  on another epic for no reason.
- **Severity:** usually Advisory.

## 8. What, not how
- **Finding:** a requirement that names a technology, library, schema or UI layout where a
  capability would do. Name the capability; never propose the technology.

## Severity rule of thumb
Blocking when `sdlc-plan-epics-create` would produce a wrong or untestable epic from the PRD as
written. Everything else is Advisory.
