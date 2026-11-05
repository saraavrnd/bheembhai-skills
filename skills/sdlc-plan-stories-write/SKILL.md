---
name: sdlc-plan-stories-write
role: author   # ADR-035: author | reviewer | integration
description: >
  Break an EPIC into well-formed USER STORIES, each with testable acceptance criteria, written to
  `stories.md` and `story-map.json` — and, in REVISE mode, apply the proposed changes from a
  review report (`epic-review.md` or a `story-review.md`) plus the answers a person gave at the
  gate. Use this as the THIRD step of the PDLC chain, after `sdlc-plan-epics-create`, and again whenever
  `sdlc-plan-epic-review` / `sdlc-plan-story-review` request changes. Trigger this even when the user just says
  "write the user stories", "break the epic into stories", "create stories with acceptance
  criteria", "apply the review", or names an epic to expand. Authoring only: it never writes to
  Jira — `sdlc-tracker-sync` publishes the approved stories (ADR-035).
compatibility: >
  Tool-agnostic skill body (Claude Code or Codex). Reads the epic from `epics.md` /
  `epic-map.json` (Atlassian MCP optional and read-only, to fetch an existing epic). Writes only
  the epic's `stories.md`, `story-map.json` and `revisions.md`.
model: sonnet   # tier: standard (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-plan-stories-write — Epic to Stories with Acceptance Criteria

> **Artifact paths:** Resolve all project-artifact locations (architecture, data model, PRD,
> epics, stories, ADRs, API contracts, per-story notes, etc.) from the **Project Layout** table
> in the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see `_SHARED-project-layout.md`. Do not hardcode paths; the
> current layout places these under `docs/` (e.g. `docs/architecture.md`, `docs/adr/`,
> `docs/api-contracts/`, `docs/product/`). **Per-story artifacts live in that story's own
> folder** `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/` with short, un-suffixed
> filenames (story-design.md, test-plan.md, verification.md, code-review.md, design-sync.md);
> epic artifacts in `docs/product/epics/<EPIC_KEY>/_epic/`. Resolve a story's files under its
> folder only. This skill's own `templates/`, `references/`,
> `examples/`, and `scripts/` stay inside the skill folder and never move under `docs/`.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part for a template before you fill it.

> **Cost & context:** This skill runs at the `model:` tier in its frontmatter.
> To avoid context bloat: load only the slices of artifacts you
> need (not whole files), don't re-read what's already in context, and for any MCP calls request
> minimal fields and batch reads rather than fetching repeatedly. MCP results persist for the
> session — keep them small.

> **Single responsibility (ADR-035):** this is an `author` skill. It writes story content only.
> It does not create or update Jira issues (that is `sdlc-tracker-sync`, an `integration` step),
> and it does not review its own stories (that is `sdlc-plan-epic-review` / `sdlc-plan-story-review`, run on a
> different model family). New stories get draft keys `<EPIC_KEY>-PENDING-N`; `sdlc-tracker-sync`
> swaps them for the real Jira keys when it publishes.


Third link in the chain. It converts an epic (and the PRD requirements mapped to it) into
INVEST-quality user stories, each with acceptance criteria precise enough that a test can be
written from them directly. These acceptance criteria are the contract that the downstream
`sdlc-deliver-code-implement` and `sdlc-deliver-tests-write` skills build against — so vagueness here costs the most later.

## Modes
- **Create** (default): no `stories.md` exists for this epic yet, or the user asks for a fresh
  decomposition. Steps 1–5.
- **Revise**: the run hands you back from `sdlc-plan-epic-review` or `sdlc-plan-story-review` with
  `changes_requested` (the hand-off names the report), or the user asks to "apply the review".
  Read that report's **Findings**, **Open questions** (with the answers given at the gate) and
  **Proposed changes**, and apply them — Step R. A finding whose question has no answer yet is
  not applied: list it in `revisions.md` as still open.

## Input it expects
- An epic — its section in `epics.md` and its entry in `epic-map.json` (or a Jira epic key the
  agent can read via the Atlassian MCP).
- `epic-map.json` from `sdlc-plan-epics-create` — to know which PRD requirement IDs this epic must
  cover (the source of truth for completeness).
- Optionally the original `PRD.md` for requirement wording.
- Revise mode only: the review report (`_epic/epic-review.md` or the story's `story-review.md`)
  and the gate answers in the run hand-off.

## Output it produces
1. `docs/product/epics/<EPIC_KEY>/_epic/stories.md` — the reviewable set of stories with acceptance criteria.
2. `docs/product/epics/<EPIC_KEY>/_epic/story-map.json` — `{story_key -> [requirement IDs]}`, extending traceability
   from epic → story → requirement. Every requirement mapped to this epic must be covered by
   at least one story. New stories use draft keys `<EPIC_KEY>-PENDING-N`; existing keys are kept.
3. Revise mode only: `docs/product/epics/<EPIC_KEY>/_epic/revisions.md` — one entry per pass: which
   report was applied, each finding → what changed in which story, and any finding left open.

## Procedure

### Step 1 — Gather the epic's requirements
From `epic-map.json`, get the FR/NFR IDs this epic covers. Pull their exact wording from the
PRD. These define what the stories must collectively satisfy.

Before slicing, run a **story-readiness** check:
- If a story would assume an actor/entity/state exists, verify another requirement or story
  creates it first.
- If the epic leaves a prerequisite lifecycle ambiguous, stop and send that ambiguity back to
  `sdlc-plan-epics-create` or `sdlc-plan-prd-write` rather than hiding it inside a story.
- If the epic mixes prerequisite creation and usage in one requirement, split them into separate
  stories unless the combined slice is still a single testable user-visible outcome.

### Step 2 — Slice into stories
- Each story is **one coherent slice of user-visible value** — vertical, not a technical layer.
  ("As a teacher I can upload a course PDF and see it accepted" — not "build the upload
  endpoint".)
- A single requirement may need one story or several; several small requirements may combine
  into one story. Optimise for INVEST (Independent, Negotiable, Valuable, Estimable, Small,
  Testable), with **Small and Testable** mattering most for the AI build chain.
- Split a story if it has more than ~5-7 acceptance criteria or covers two user goals.

### Step 3 — Write each story (use `templates/story.md.tmpl`)
Each story needs:
- **Title** — short, action-oriented.
- **Story statement** — "As a <role>, I want <capability>, so that <benefit>."
- **Acceptance criteria** — in **Gherkin** (Given/When/Then), one scenario per distinct
  behaviour, including the unhappy paths (invalid input, permission denied, empty state).
  Each scenario must be a concrete pass/fail check.
  For stories that create or change persistent platform state, phrase the criteria against the
  durable system of record the architecture names, not against a temporary shim or mockable
  placeholder. The downstream design and tests should be able to prove the real row/state exists.
- **Covered requirements** — the FR/NFR IDs this story satisfies (traceability).
- **Out of scope** — what this story explicitly does NOT do (prevents scope creep into tests).
- **Notes / dependencies** — sequencing, data needs, design links.
- **Estimate** — story points if known.

### Step 4 — Verify coverage
Cross-check the stories against the epic's requirement IDs. Every requirement must be covered
by at least one story's acceptance criteria. If any requirement is uncovered, add or extend a
story. Record the coverage summary at the top of `stories.md`.

### Step 5 — Hand off
Tell the user: N stories written for <EPIC_KEY> (draft keys where new), coverage of requirements
is complete (or flag gaps), and the next steps: `sdlc-plan-epic-review` reviews the set, then
`sdlc-tracker-sync` publishes the approved stories to Jira.

### Step R — Revise from a review report
1. Read the report's **Proposed changes** and the gate answers; apply each one to the named
   story's statement, acceptance criteria, out of scope or notes in `stories.md`, in the same
   shape Step 3 produces. One answer that affects several stories changes all of them.
2. If coverage changed, update `story-map.json` (and keep Step 4's coverage summary true).
3. Do not touch stories the report does not name, and do not add findings of your own — a new
   problem you notice goes into `revisions.md` as a note for the next review.
4. Write the `revisions.md` entry (report applied, finding → change, still-open findings).
5. Hand back: the reviewer runs again on the revised set.

## Writing acceptance criteria that drive tests (the core rule)
Each Given/When/Then must be executable as a test with no further interpretation.

- Weak: "Then the upload works correctly."
- Strong:
  - Given a signed-in teacher, When they upload a 10 MB PDF, Then the file is accepted and its
    status shows "processing" within 2 seconds.
  - Given a signed-in teacher, When they upload a 40 MB file, Then it is rejected with the
    message "File exceeds 25 MB limit" and nothing is stored.

If a criterion can't be turned into a test without guessing, rewrite it.

If a story would require a missing prerequisite actor, entity, or state that no story in the
epic creates, do not paper over it with an assumption; flag the gap and route it back to
epic/PRD review.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **changes_requested**: Revise mode, and a finding's question has no answer yet, so the story cannot be fixed without guessing. Name the open finding in `revisions.md`.
- **escalation_required**: A scenario assumes an actor, entity or state that no story or requirement creates, and you cannot record it as a gap within this epic.

## Reference files
- `templates/story.md.tmpl` — story + acceptance-criteria structure.
- `references/acceptance-criteria-guide.md` — Gherkin patterns and the testability bar.
- `examples/` — stories with acceptance criteria derived from a sample epic.
