# Epic Order — Learn Portal

**Status:** AWAITING REVIEW · **Date:** 2026-11-21 · **Epics:** 8 · **Waves:** 3

> Proposed order of the epics by dependency. `sdlc-plan-epics-review` reviews it with the epic
> plan; after sign-off, `sdlc-tracker-sync` mirrors every edge as a Jira "A blocks B" link.
> Explicit Jira links are ground truth and never changed.

> Five of the eight edges are **provisional** (inferred from the epics' own notes and from which
> epic creates which entity). They firm up once each epic's stories are written.

## Waves
Epics in the same wave are independent and can be built in parallel.

### Wave 1 (no dependencies)
- LEARN-11 — Curriculum knowledge base (MVP)
- LEARN-15 — SIS integration (MVP)
- LEARN-17 — Deployment & operations (MVP)

### Wave 2 (depends only on Wave 1)
- LEARN-10 — Socratic dialogue engine (MVP) — depends on: LEARN-11
- LEARN-16 — Safety, privacy & compliance (MVP) — depends on: LEARN-15

### Wave 3
- LEARN-12 — Visual & diagram learning (mixed) — depends on: LEARN-10
- LEARN-13 — Answer grounding & accuracy (mixed) — depends on: LEARN-10, LEARN-11
- LEARN-14 — Teacher dashboard (mixed) — depends on: LEARN-10, LEARN-15

## Dependencies
| Epic | Depends on | Source | Confidence | Why |
|------|-----------|--------|------------|-----|
| LEARN-10 | LEARN-11 | epic-body | provisional | the tutor retrieves curriculum content that LEARN-11 indexes |
| LEARN-16 | LEARN-15 | lifecycle | provisional | retention and deletion apply to student records that LEARN-15 imports |
| LEARN-12 | LEARN-10 | prd | firm | FR-007 renders diagrams inside the dialogue that FR-001 creates |
| LEARN-13 | LEARN-10 | prd | firm | FR-010 verifies the tutor's answers |
| LEARN-13 | LEARN-11 | lifecycle | provisional | grounding cites the indexed curriculum sources |
| LEARN-14 | LEARN-10 | prd | firm | FR-012 shows the session history the dialogue engine records |
| LEARN-14 | LEARN-15 | lifecycle | provisional | teachers see the classes and students that LEARN-15 imports |

## Parallel groups
- Wave 1: three teams can start LEARN-11, LEARN-15 and LEARN-17 at once.
- Wave 2: LEARN-10 and LEARN-16 are independent of each other.
- Wave 3: LEARN-12, LEARN-13 and LEARN-14 are independent of each other.
- Story planning for all eight epics can run in parallel now; the waves constrain building only.

## MVP path
All eight epics: LEARN-11, LEARN-15, LEARN-17 → LEARN-10, LEARN-16 → LEARN-12, LEARN-13,
LEARN-14. The three wave-3 epics are `mixed`: only their MVP requirements are on the path.

## Cycles and conflicts
None.

## On approval
- `sdlc-tracker-sync` sets "blocks" links between the epics: LEARN-11 blocks LEARN-10,
  LEARN-15 blocks LEARN-16, LEARN-10 blocks LEARN-12, LEARN-10 blocks LEARN-13, LEARN-11 blocks
  LEARN-13, LEARN-10 blocks LEARN-14, LEARN-15 blocks LEARN-14.
- Each epic's stories can then be planned in its own `sdlc-wf-planning-epic` run, in any order and in parallel.
