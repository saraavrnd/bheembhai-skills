# Epics Review — Learn Portal

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-21 · **Pass:** 1

> Report of the epic plan review (ADR-035 `reviewer`). This skill edits nothing else;
> `sdlc-plan-epics-create` (revise mode) applies `epics` findings and `sdlc-plan-epics-order`
> applies `order` findings.

## Context loaded
- `PRD.md`: 8 feature areas, 18 FRs, 5 NFRs.
- `epics.md` / `epic-map.json`: 8 epics, draft keys shown here as LEARN-10 to LEARN-17.
- `epic-order.md` / `.json`: 3 waves, 7 edges, 4 provisional.

## PRD fit
- **Verdict:** Fits
- **Reason:** Every finding can be fixed in the epics or the order; no requirement contradicts another.

## Findings

### Finding 1 — Lifecycle across epics
- **Target:** epics
- **Severity:** Blocking
- **Epics touched:** LEARN-10, LEARN-15
- **Requirements touched:** FR-001, FR-014
- **Evidence:** LEARN-10's scope says "a signed-in student starts a dialogue"; LEARN-15 imports
  rosters but its scope says "accounts are provisioned by the school's identity provider". No
  epic owns student sign-in.
- **Question (if a person must decide):** Who creates the student's sign-in: the portal, or the
  school's identity provider through SSO? — **Proposed default:** SSO through the school's
  identity provider, owned by LEARN-15.
- **Proposed change:** Add "student and teacher sign-in through SSO" to LEARN-15's functional
  scope, and name it in LEARN-10's dependencies.

### Finding 2 — Edges and waves
- **Target:** order
- **Severity:** Blocking
- **Epics touched:** LEARN-10, LEARN-15
- **Requirements touched:** FR-001
- **Evidence:** With Finding 1 applied, LEARN-10 uses the sign-in that LEARN-15 creates, but the
  order has no LEARN-15 → LEARN-10 edge.
- **Proposed change:** Add the edge LEARN-15 → LEARN-10 (source `lifecycle`). LEARN-10 stays in wave 2.

### Finding 3 — Boundaries and size
- **Target:** epics
- **Severity:** Advisory
- **Epics touched:** LEARN-17
- **Requirements touched:** NFR-005
- **Evidence:** LEARN-17 holds one NFR and no user-facing scope.
- **Proposed change:** Keep it, but say in its Goal which environments must exist before wave 1
  epics can be demonstrated.

## Open questions
- Q-1: Who creates the student's sign-in? — Proposed default: SSO through the school's identity provider, owned by LEARN-15.

## Proposed changes
- `sdlc-plan-epics-create`: add SSO sign-in to LEARN-15's scope and LEARN-10's dependencies (Finding 1); sharpen LEARN-17's Goal (Finding 3).
- `sdlc-plan-epics-order`: add LEARN-15 → LEARN-10 (Finding 2).

## Earlier findings
First pass.
