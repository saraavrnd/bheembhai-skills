---
name: sdlc-plan-story-review
role: reviewer   # ADR-035: author | reviewer | integration
description: >
  Review a single, already-written user story against the system architecture, data model, API
  contracts and sibling stories, and report its gaps, ambiguity and undecided edge cases. REVIEW
  ONLY: it writes one report, `story-review.md`, with each gap, its evidence, the question a
  person must answer and the proposed change to the story; it never edits `stories.md`, the story
  map or Jira. `sdlc-plan-stories-write` (revise mode) applies the findings and `sdlc-tracker-sync`
  publishes them. Trigger this when the user says "review this story", "drill into this story",
  "find gaps in this story", "grill this story", "is this story ready for dev", "this story feels
  ambiguous", or names a story key with a request to check it. On-demand; run it whenever a story
  (new or old) feels underspecified, before `sdlc-deliver-story-design` picks it up.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads architecture.md / data-model.md / api-contracts /
  ui-conventions.md / ADRs from the committed sdlc-arch-design, plus sibling stories in the same epic.
  Atlassian MCP optional and read-only — used to fetch the Jira story if a key is given. Runs on a
  different model family from the story's author (ADR-035).
model: opus   # tier: strong (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-plan-story-review — Review a Story for Gaps (report only)

> **Artifact paths:** Resolve all project-artifact locations (architecture, data model, PRD,
> epics, stories, ADRs, API contracts, per-story notes, etc.) from the **Project Layout** table
> in the repo's conventions file (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see `_SHARED-project-layout.md`. Do not hardcode paths; the
> current layout places these under `docs/` (e.g. `docs/architecture.md`, `docs/adr/`,
> `docs/api-contracts/`, `docs/product/`). **Per-story artifacts live in that story's own
> folder** `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/` with short, un-suffixed
> filenames (story-design.md, test-plan.md, verification.md, code-review.md, design-sync.md,
> **story-review.md**); epic artifacts in `docs/product/epics/<EPIC_KEY>/_epic/`. Resolve a
> story's files under its folder only. This skill's own `templates/`, `references/`,
> `examples/` stay inside the skill folder and never move under `docs/`.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part for a template before you fill it.

> **Cost & context:** This skill runs at the `model:` tier in its frontmatter.
> To avoid context bloat: load only the slices of artifacts you
> need (not whole files), don't re-read what's already in context, and for any MCP calls request
> minimal fields and batch reads rather than fetching repeatedly. MCP results persist for the
> session — keep them small.

> **Single responsibility (ADR-035):** this is a `reviewer` skill. It judges a story and writes
> only `story-review.md`. It never rewrites the story, never edits `stories.md` or
> `story-map.json`, and never writes to Jira. `sdlc-plan-stories-write` in revise mode applies the
> proposed changes on the author's model family.

A user story reads as complete and is still full of silent assumptions — an actor that isn't
quite defined, a precondition that assumes something another story hasn't built yet, an error
path nobody specified, a value the architecture can't actually support. Those gaps are cheapest
to catch here, on the story itself, before `sdlc-deliver-story-design` commits to an interface built on top of
a guess. This skill runs a **grounded interview**: it doesn't ask generic "any ambiguity?"
questions, it reads the actual architecture/data-model/sibling-stories and asks pointed questions
only where something concrete doesn't line up — and hands each gap, with its question and the
proposed change, to `sdlc-plan-stories-write` (revise) through one report.

## Input it expects
- A user story — by Jira key (fetched via Atlassian MCP) or pasted story text (statement +
  acceptance criteria), typically one produced by `sdlc-plan-stories-write`.
- The committed design: `architecture.md`, `data-model.md`, `api-contracts/`, ADRs, and
  `ui-conventions.md` for frontend/full-stack stories.
- The epic's sibling stories (`stories.md` / `story-map.json`) for overlap and sequencing context.

## Output it produces
One file: `story-review.md` in **this story's folder**,
`docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/story-review.md` (create the folder if it
doesn't exist; resolve `<EPIC_KEY>` via `docs/product/epic-map.json` if you only have the story
key), from `templates/story-review.md.tmpl`. Nothing else changes.

For each real gap it records the **severity** (`Blocking`: tests or code would be built on a
guess; `Advisory`: worth tightening, safe to build), the **evidence** (the AC or sentence, and the
doc section it conflicts with), the **question** a person must answer when it is a product
decision, and the **proposed change** to the story statement, acceptance criteria or out of
scope. An architecture conflict goes under **Architecture impact**, recommending
`sdlc-arch-design` (amend mode) before `sdlc-deliver-story-design`.

## Procedure

### Step 1 — Resolve the story and its neighborhood
Get the story (Jira key via MCP, minimal fields: summary, description, acceptance-criteria field,
status, parent epic — or the pasted text). If only the story key is known, resolve its epic via
`epic-map.json`. Locate the story's entry in the epic's `stories.md` and its per-story folder
(create the folder if this is the first artifact for it). Load the epic's `story-map.json` and
the other stories in `stories.md` for later overlap checks — one batch read, not one fetch per
sibling.

### Step 2 — Load only the system context this story touches
Read `architecture.md` and `data-model.md` for the module(s)/entities the story's language
implies. Read `api-contracts/` if the story implies an existing or new endpoint. Read
`ui-conventions.md` if the story reads as frontend or full-stack. Skim relevant ADRs by keyword
rather than the whole `adr/` folder. Read slices, not whole files.

### Step 3 — Run the drill checklist
Work through `references/gap-checklist.md`'s categories against this specific story: actor/
precondition clarity, acceptance-criteria completeness (happy path only?), concreteness of
outcomes (vague thresholds/messages), architecture/data-model fit, silent NFRs, traceability to
FR/NFR IDs, overlap with sibling stories, and whether "out of scope" actually bounds the story.
Discard anything the story already answers unambiguously — only real gaps make it to Step 4.
Rank what remains by how much it would mislead `sdlc-deliver-tests-write` if left unresolved.

### Step 4 — Turn each gap into a finding
Each real gap becomes one finding: severity, evidence, one specific answerable question when a
person must decide (never "anything else unclear?"), and the proposed change, written in the shape
`sdlc-plan-stories-write` produces (Gherkin for acceptance criteria). If a gap is an architecture
conflict (the story needs an entity/endpoint/integration that doesn't exist and isn't already
someone else's in-flight work), record it under **Architecture impact** — an answer cannot invent
architecture.

### Step 5 — Write the report and stop
Write `story-review.md` from `templates/story-review.md.tmpl` and finish. Do not edit the story,
`stories.md`, `story-map.json` or Jira, even when the fix looks obvious: the proposed change is the
hand-off to `sdlc-plan-stories-write` (revise mode). A clean story ("no findings") is a valid,
useful outcome.

> Anti-stall note: read the inputs and write the report in the same turn. Don't narrate that
> you're "about to check the architecture" and stop there.

## What this skill is NOT
- Not an editor — it never rewrites the story or writes to Jira; `sdlc-plan-stories-write` (revise)
  applies its proposed changes and `sdlc-tracker-sync` publishes them.
- Not the "how" — it doesn't decide interfaces, endpoints, or data-model deltas; that's
  `sdlc-deliver-story-design`. This only sharpens the "what" the story is asking for.
- Not authority to change architecture — a real architecture-conflict gap gets flagged to
  `sdlc-arch-design`, never quietly resolved by inventing a design inside this interview.
- Not a duplicate of `sdlc-deliver-story-design`'s escalation check — that one verifies fit once the how is
  decided; this one catches ambiguity earlier and cheaper, before design work starts.
- Not automatic — this is an on-demand utility skill, not a numbered stage every story must pass
  through. Reach for it when a story feels underspecified: right after `sdlc-plan-stories-write`, before
  `sdlc-deliver-story-design`, or on an older backlog story nobody's touched.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: A gap is an architecture conflict: closing it needs `sdlc-arch-design` (amend), not a story change.
- **changes_requested**: At least one `Blocking` finding, or an open question a person must answer. `sdlc-plan-stories-write` (revise) applies the report.
- **completed**: No `Blocking` findings (advisory ones may remain). The story is ready for `sdlc-deliver-story-design`.

## Reference files
- `references/gap-checklist.md` — the full drill checklist by category, with what a real (vs.
  nitpick) gap looks like in each.
- `templates/story-review.md.tmpl` — the review-log artifact structure.
- `examples/story-review-LEARN-21.md` — a worked pass over `sdlc-plan-stories-write`'s LEARN-21 example.
