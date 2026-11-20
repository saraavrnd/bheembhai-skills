# SK-003: Idea-to-PRD workflow with a framing step and a cross-vendor PRD review

**Status:** Proposed · **Date:** 2026-11-20 · **Deciders:** Saraav

Builds on SK-002 and platform **ADR-035** (cross-vendor author and reviewer routing), **ADR-006**
(a policy is tied to its workflow) and **ADR-027** (sub-workflow fan-out).

## Context

`sdlc-wf-planning` starts at `sdlc-plan-prd-write` and goes straight on to epics and Jira. Two
gaps showed up when the question was "what takes an idea to a PRD?":

1. **Nobody can answer the PRD's questions.** `sdlc-plan-prd-write` says "ask only blocking
   questions". Inside an unattended run there is no one to ask, so the skill either invents the
   answer or escalates and ends the run. The only gate (the governed policy's gate on prd-write)
   comes after the PRD is written, which is the expensive moment to discover the users were
   wrong.
2. **Nothing reviews the PRD.** ADR-035 puts a reviewer on a different model family after every
   author whose output others build on: epic-review after stories-write, code-review after
   code-implement. The PRD, which every later artifact inherits, has only its own verify judge.

## Decision

1. **New workflow `sdlc-wf-planning-prd`** (Idea to PRD):
   `sdlc-plan-idea-frame` → `sdlc-plan-prd-write` → `sdlc-plan-prd-review`, with
   `prd-review: changes_requested → prd-write` (revise mode). It publishes nothing and ends at a
   reviewed PRD.
2. **New skill `sdlc-plan-idea-frame`** (`author`). Writes `idea-brief.md` only: the idea as given,
   problem, users, value hypothesis, assumptions marked `Stated` or `Inferred`, constraints,
   non-goals, and up to about seven `Q-n` questions, each `Blocking` or `Non-blocking` and each
   with a **proposed default**. No requirements (its verify.yaml refuses `FR-`/`FA-` ids).
   `Needs framing` escalates.
3. **New skill `sdlc-plan-prd-review`** (`reviewer`). Writes `prd-review.md` only: idea fidelity
   (`Faithful` / `Drifted`), brief coverage, findings with severity, evidence, question with
   proposed default and proposed change. Blocking findings → `changes_requested`; `Drifted` →
   `escalation_required`. Its `changes_requested` edge names `sdlc-plan-prd-write` as the step it
   reviews (ADR-035 §3), so it runs on the run's reviewer model.
4. **`sdlc-plan-prd-write` gains a brief-aware create mode and a revise mode.** With a brief, it
   does not ask again: it uses gate answers, or adopts the defaults, and records both in §8.
   Revise mode applies `prd-review.md`, never renumbers (splits append new ids), and logs each
   pass in `prd-revisions.md`; verify.yaml checks that log exists when the run came back from
   the review. Standalone use and `sdlc-wf-planning` are unchanged.
5. **Two policies.** `sdlc-policy-planning-prd-governed`: gate on idea-frame
   (`completed`, `escalation_required`, role `any`) where a person answers the brief's questions,
   and on prd-review (`completed`, `changes_requested`, `escalation_required`, role `lead`) for
   review answers and sign-off. `sdlc-policy-planning-prd-fast`: no brief gate (defaults
   adopted), prd-review gated on `completed` and `escalation_required` only. There is no
   autonomous variant: a PRD with no human sign-off is not a useful end state.
6. **Defaults everywhere a person might not answer.** Every brief and review question carries a
   default, so a gate-less step never loops waiting for an answer. Adopted defaults are recorded
   in the PRD (§8, and §9 for review questions) so a person can still see and overturn them.

## Alternatives considered

- **Put idea-frame and prd-review into `sdlc-wf-planning`.** It would make the planning run
  longer before anything reaches Jira, and change a workflow other runs depend on. Keeping
  idea-to-PRD separate lets a team stop at the PRD, iterate on it, and then start
  `sdlc-wf-planning`. See Follow-ups for joining them.
- **No framing step: let prd-write's gate carry the questions.** The gate would come after the
  PRD is written, so a wrong answer costs a full rewrite and a review pass.
- **Market or customer research steps** (competitor profiling, customer interviews). The old
  marketing skills that did this were removed from the SDLC catalog, and research needs web or
  CRM connectors that the planning runs do not have. Left as an optional later step between
  idea-frame and prd-write.

## Where this differs from the conventions, and why

- **Literal paths in verify.yaml.** The platform binds only the `{layout.*}` names it knows
  (ADR-031 §1.5: an unbound name fails the step). The brief, review and revisions logs use the
  literal default paths `docs/product/idea-brief.md`, `prd-review.md` and `prd-revisions.md`,
  which are also added to the default Project Layout table. A project that moves them in
  AGENTS.md will not be followed by the checks until the platform binds them.
- **Roles are `any` and `lead`**, like every other policy in this repo, though ADR-007/008 moved to
  the project role catalog. Changing that belongs with the other policies.

## Follow-ups

1. Platform: bind `{layout.idea_brief}`, `{layout.prd_review}` and `{layout.prd_revisions}`, then
   swap the literal paths.
2. Optionally make `sdlc-wf-planning` v3 start from a reviewed PRD, either by running this
   workflow as a `workflow:` node (ADR-027) or by starting at `sdlc-plan-epics-create` when a
   PRD already exists.
3. Bump `catalog.yaml`'s `version` when this is released.

## Consequences

- An idea can go to a reviewed PRD in one run, with the questions asked before writing rather
  than after.
- Releasing it needs a platform that supports ADR-035 roles (as SK-002 already requires).
- `sdlc-plan-prd-review` refuses to run without `idea-brief.md`, so on-demand PRD review outside
  this workflow needs a brief first.
