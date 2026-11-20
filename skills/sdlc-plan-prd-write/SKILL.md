---
name: sdlc-plan-prd-write
role: author   # ADR-035: author | reviewer | integration
description: >
  Convert a raw product idea or domain description into a structured, decomposable Product
  Requirements Document (PRD). Use this as the FIRST step of the PDLC chain whenever someone
  has a product idea, concept notes, a whitepaper, or domain details and needs a real PRD.
  Trigger this even when the user just says "write a PRD", "turn this idea into requirements",
  "draft requirements for my product", "I have a product concept", or pastes domain notes and
  asks what to build. The PRD this produces is designed to feed directly into the `sdlc-plan-epics-create`
  skill, so it is structured into numbered, traceable requirements rather than prose.
compatibility: >
  Tool-agnostic (Claude Code or Codex). No external tools required to produce the PRD. The
  output is a single Markdown file that downstream skills (sdlc-plan-epics-create, sdlc-plan-stories-write) consume.
---

# prd — Idea to PRD

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

> **Cost & context:** This skill runs at the model tier its workflow step sets.
> To avoid context bloat: load only the slices of artifacts you
> need (not whole files), don't re-read what's already in context, and for any MCP calls request
> minimal fields and batch reads rather than fetching repeatedly. MCP results persist for the
> session — keep them small.


First link in the PDLC chain. It turns an unstructured product idea into a PRD whose
structure is engineered for decomposition: every requirement is numbered, scoped, and
testable, so `sdlc-plan-epics-create` can split it into epics and `sdlc-plan-stories-write` can derive stories
with acceptance criteria. A pretty prose PRD that can't be decomposed is a failure here.

> This skill is product-agnostic. The product could be a K-12 tutor, a payments API, or a
> warehouse app. Read the input, ask only what's essential, and produce the PRD.

## Modes
- **Create** (default): no review report has been handed to this run. Steps 1–5.
- **Revise**: the run hands you back from `sdlc-plan-prd-review` with `changes_requested` (the
  hand-off names the report), or the user asks to "apply the PRD review". Step R.

## Input it expects
Any of: a one-line idea, a page of concept notes, a domain whitepaper, a transcript, or a
mix. The input may be incomplete — that is normal.

Under `sdlc-wf-planning-prd`, also:
- `idea-brief.md` from `sdlc-plan-idea-frame` (current layout: `docs/product/idea-brief.md`) and
  the answers a person gave to its open questions at the gate, in the run hand-off. When the
  brief exists it is your starting point; the raw input is still the yardstick for fidelity.
- Revise mode only: `prd-review.md` from `sdlc-plan-prd-review` and the gate answers to its open
  questions.

## Output it produces
One file: `PRD.md`, following `templates/PRD.md.tmpl`. It is self-contained and ready for
`sdlc-plan-epics-create`.

Revise mode also writes `prd-revisions.md` next to the PRD (current layout:
`docs/product/prd-revisions.md`): one entry per pass, naming the report applied, each finding →
what changed, and each question → the answer given or the default adopted.

## Procedure
1. **Read the input fully.** Extract the problem, the users, and the core value before
   writing anything.
2. **Identify gaps, then ask only blocking questions.** Do not interrogate. Ask at most a
   few questions, and only for things that would change the PRD's shape (target users,
   must-have vs later, any hard constraints like compliance or platform). If the input is
   rich enough, proceed and state your assumptions inline instead of asking.
   **When an idea brief exists, do not ask again:** the brief's questions are the questions.
   For each `Q-n`, use the answer given at the gate; if none was given, adopt its proposed
   default. Record both in §8 as `Q-n: <answer> (answered at the gate)` or
   `Q-n: <default> (default adopted)`, and carry each brief `A-n` assumption into §8 as well.
   Keep the brief's target users, constraints and non-goals unless an answer changed them.
3. **Draft the PRD** from the template. Rules that make it decomposable:
   - Every functional requirement gets a stable ID: `FR-001`, `FR-002`, …
   - Non-functional requirements get `NFR-001`, … (performance, security, compliance,
     accessibility, scale).
   - Each requirement is **one testable capability**, written so success is checkable.
   - Group requirements under **feature areas** — these become natural epic boundaries.
   - Mark each requirement's release: `MVP` or `Later`. This drives scope decisions
     downstream.
   - Capture measurable **success metrics** (the PRD's definition of "working").
4. **Self-check** against `references/prd-quality-checklist.md`. Fix anything that fails.
   The most common failure is a requirement that bundles three capabilities into one — split
   it.
5. **Write `PRD.md`** to the location given for the PRD in the Project Layout table in `AGENTS.md`
   (current layout: `docs/product/PRD.md`). If no repo/AGENTS.md exists yet — i.e. the PRD is
   being written before `sdlc-arch-repo-scaffold` — write it where the user wants and note that
   `sdlc-arch-repo-scaffold` will place it under `docs/product/`. Tell the user
   it's ready to feed into `sdlc-plan-epics-create`.

### Step R — Revise from a PRD review
1. Read `prd-review.md`'s **Proposed changes** and **Open questions**, and the gate answers.
2. Apply each proposed change to `PRD.md`. For each `RQ-n`, use the gate answer; if none was
   given (a policy with no gate on the review), adopt the proposed default and record it in §8
   as `RQ-n: <default> (default adopted)` and in §9 as still open for a person to confirm.
3. Splitting a requirement keeps the original id on the first part and gives the new parts the
   next free ids at the end of the table, so ids already cited elsewhere stay stable. Never
   renumber.
4. Do not change requirements the report does not name, and do not add findings of your own:
   note anything new you spot in `prd-revisions.md` for the next review pass.
5. Re-run the self-check (Step 4), append the `prd-revisions.md` entry, and hand back: the
   reviewer runs again on the revised PRD.

## What makes a good requirement (the core rule)
A requirement must be **atomic and testable**. Compare:

- Bad (bundled, vague): "The system handles user content and shows useful feedback."
- Good (atomic, testable):
  - `FR-012` The system accepts a user-uploaded document (PDF, DOCX, TXT) up to 25 MB.
  - `FR-013` The system rejects unsupported file types with a clear error message.
  - `FR-014` The system displays processing status while a document is being prepared.

If you can't write a one-sentence acceptance check for a requirement, it isn't atomic yet.

## Handoff
End by telling the user: the PRD is at `<path>`, it contains N feature areas and M
requirements, and the next step is `sdlc-plan-epics-create` to turn feature areas into Jira epics
(under `sdlc-wf-planning-prd`, `sdlc-plan-prd-review` reviews it first).

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: The idea is too thin or self-contradictory to write a PRD without inventing the product's core.
- **completed**: Ordinary gaps in the idea. State them as explicit assumptions, never as given. In revise mode, an unanswered review question is not a reason to stop: adopt its proposed default and record it.

## Reference files
- `templates/PRD.md.tmpl` — the structure to fill in.
- `references/prd-quality-checklist.md` — self-check before finishing.
- `examples/` — a worked PRD generated from a real product input.
