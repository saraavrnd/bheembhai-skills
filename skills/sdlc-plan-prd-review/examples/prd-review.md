# PRD Review — Learn Portal

**Verdict:** CHANGES REQUESTED · **Date:** 2026-06-19 · **Pass:** 1

> Report of the PRD review (ADR-035 `reviewer`). This skill edits nothing else;
> `sdlc-plan-prd-write` (revise mode) applies the proposed changes.

> Illustrative: a first pass over an early draft of `sdlc-plan-prd-write`'s example PRD. The
> requirement wording quoted here is the draft's; the published example already includes the
> fixes.

## Context loaded
- `docs/product/PRD.md` — 8 feature areas, 17 FRs, 4 NFRs.
- `docs/product/idea-brief.md` — Q-1, Q-2 answered at the gate (defaults accepted); Q-3 to Q-5
  defaulted.
- Run input (the idea text).

## Idea fidelity
- **Verdict:** Faithful
- **Reason:** Same users, same problem, and the MVP still tests the value hypothesis.

## Brief coverage
| Brief item | Carried by |
|------------|------------|
| Student | FA-1, FR-001–FR-003 |
| Teacher | FR-004, FR-012 |
| District admin | NFR-003 |
| Value hypothesis | Goals G1, G2 |
| Constraint: COPPA/FERPA | NFR-003 |
| Constraint: local Docker | NFR-005 |
| Constraint: no raw chat logs for teachers | FR-012 |
| Non-goal: no curriculum supplied | §8 assumption |
| Q-1 roster import | FR-014 |
| Q-2 at-risk flags Later | FR-013 (Later) |
| Q-3 diagram interpretation Later | FR-009 (Later) |
| Q-4 35% metric | Goal G1 metric |
| Q-5 upload formats | FR-004 |
| A-3 roster provisioning | Not carried: no requirement handles re-imports |

## Findings

### Finding 1 — Lifecycle completeness
- **Severity:** Blocking
- **Requirements touched:** FR-014
- **Evidence:** FR-014 "System imports a student roster via OneRoster or CSV, skipping bad rows."
  Nothing says what a second import of the same roster does, and student profiles are the core
  entity every other feature area consumes.
- **Question (if a person must decide):** Should re-importing a roster update existing students
  or create new ones? — **Proposed default:** Update by student id; never duplicate.
- **Proposed change:** Split FR-014 into an import requirement, a malformed-row requirement and an
  idempotent re-import requirement.

### Finding 2 — Atomicity and testability
- **Severity:** Blocking
- **Requirements touched:** FR-014
- **Evidence:** "imports … skipping bad rows" bundles import and rejection, with no observable
  result for the rejected rows.
- **Proposed change:** The rejection requirement says malformed rows are rejected, valid rows are
  processed, and each rejection is logged.

### Finding 3 — Non-functional coverage
- **Severity:** Advisory
- **Requirements touched:** NFR section
- **Evidence:** The brief's users include children; the draft has no accessibility NFR.
- **Proposed change:** Add an accessibility NFR: student UI meets WCAG AA and age-appropriate
  reading levels.

## Open questions
- RQ-1: Should re-importing a roster update existing students or create new ones? — Proposed
  default: update by student id; never duplicate.

## Proposed changes
1. FR-014 → "System imports a student roster via OneRoster or CSV."
2. New FR → "System rejects malformed roster rows while processing valid ones, and logs each
   rejection."
3. New FR → "Re-importing the same roster does not create duplicate student profiles."
4. New NFR (Accessibility) → "Student UI meets WCAG AA and age-appropriate reading levels."

## Earlier findings
First pass.
