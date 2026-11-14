# PDLC Skill Chain (product-agnostic)

A pipeline of reusable skills that take **any** product idea through the product development
lifecycle using Claude or Codex. Each skill consumes the previous skill's output artifact and
produces the next, so the chain composes into a semi-autonomous build flow. These skills are
generic — the product (Learn Portal, a payments API, anything) is just the input you feed in.

## The chain

```
  idea / domain notes
        │
        ▼
   ┌─────────┐   PRD.md
   │   prd   │ ───────────────►
   └─────────┘
        │
        ▼
 ┌───────────────┐  epics in Jira + epic-map.json
 │ sdlc-plan-epics-create │ ──────────────────────────────►   (via Atlassian MCP)
 └───────────────┘
        │
        ▼
 ┌────────────┐  stories in Jira + story-map.json
 │ sdlc-plan-stories-write │ ─────────────────────────────────►   (via Atlassian MCP)
 └────────────┘
        │
        ▼
 ── greenfield bootstrap (run once) ──────────────────────────
 ┌─────────────┐  approved design: architecture, ADRs, contracts, testing strategy
 │ sdlc-arch-design │ ───────────────────────────────────────────►   (propose → APPROVE)
 └─────────────┘
        │
        ▼
 ┌─────────────────┐  runnable repo skeleton + walking skeleton + TDD harness
 │ sdlc-arch-repo-scaffold│ ─────────────────────────────────────────►
 └─────────────────┘
        │
        ▼
 ── per-story loop (repeat for each story, TDD) ───────────────
 ┌──────────────┐  story-design-<KEY>.md  (the "how", REVIEWED)
 │ sdlc-deliver-story-design │ ──────────────────────────────────────────►   (propose → APPROVE)
 └──────────────┘
        │
        ▼
 ┌──────────────┐  failing tests + test-plan  (TDD red)
 │ sdlc-deliver-tests-write │ ──────────────────────────────────────────►
 └──────────────┘
        │
        ▼
 ┌───────────┐  code on feat/<KEY> branch, tests green  (TDD green)
 │ implement │ ─────────────────────────────────────────────►
 └───────────┘
        │
        ▼
 ┌─────────────┐  verification report: PASS / BLOCK  (honest-green gate)
 │ sdlc-deliver-tests-verify │ ───────────────────────────────────────────►
 └─────────────┘
        │ PASS
        ▼
 ┌─────────────┐  advisory review report + fix list  (standards/security/acceptance/maintainability)
 │ sdlc-deliver-code-review │ ───────────────────────────────────────────►
 └─────────────┘
        │ fixes? ──► implement applies ──► sdlc-deliver-tests-verify re-runs ──┐
        │                                                        │
        │ (none / waived)                                        │
        ▼                                                        │
 ┌───────────┐  sdlc-deliver-docs-sync commits doc/AGENTS.md updates to     │
 │ sdlc-deliver-pr-open │  the branch → GitHub PR (via MCP) + Jira → In     │
 │ +design-  │  Review (via MCP); flags affected open stories    │
 │  sync     │ ◄───────────────────────────────────────────────┘
 └───────────┘
        │
        └──► human review owns merge ──► next story starts at sdlc-deliver-story-design

   ↑ escalation: if a story needs an architecture change, sdlc-deliver-story-design kicks back to
     sdlc-arch-design (AMEND mode) → new ADR → resume. (before code, not at merge)
```

### Roles (ADR-035)
Every skill does one job and carries one `role:` in its SKILL.md frontmatter (`tools/check.py`
enforces it). The role decides which model runs it: the platform runs **author** and
**integration** steps on the run's primary model and **reviewer** steps (and the verify judge) on
a model from a different family, so content is never reviewed by the family that wrote it.

| Role | Does | Writes | Skills |
|------|------|--------|--------|
| `author` | creates, updates or deletes content | content in its own scope | prd-write, epics-create, stories-write, epic-sequence, arch-design, arch-ui-conventions, arch-repo-scaffold, story-design, tests-write, code-implement, docs-sync, fix-bug-triage, fix-bug-reproduce, fix-rootcause-analyze, all 16 discovery skills, adhoc-session |
| `reviewer` | judges another step's output | its own report only | code-review, tests-verify, epic-review, story-review |
| `integration` | carries out an approved decision in Jira / the code host | a short record, tracker keys | story-start, impact-flag, pr-open, tracker-sync |

A reviewer reviews the step its `changes_requested` / `BLOCK` edge routes to; a workflow names any
other independence pair with `independent_of` (tests-write vs code-implement).

### Built now
| Skill | In | Out |
|-------|----|----|
| `sdlc-plan-prd-write` | idea / domain notes / whitepaper | `PRD.md` — numbered, atomic, testable requirements grouped into feature areas |
| `sdlc-plan-epics-create` | `PRD.md` | `epics.md` (opening with the `bheembhai:foreach` block the planning fan-out reads) + `epic-map.json` traceability (draft keys; `sdlc-tracker-sync` publishes) |
| `sdlc-plan-stories-write` | an epic + `epic-map.json`; or a review report (revise mode) | `stories.md` with Gherkin acceptance criteria + `story-map.json` (draft keys; `sdlc-tracker-sync` publishes) |
| `sdlc-arch-design` | PRD + epics (create); escalated story (amend) | **approved** architecture, ADRs, data model, API contracts, tech stack, testing strategy. **Amend mode**: updates the design + adds an ADR when a story needs an architecture change |
| `sdlc-arch-ui-conventions` | approved design with a frontend | thin `ui-conventions.md` starter (split out of `sdlc-arch-design`) |
| `sdlc-arch-repo-scaffold` | approved design | **runnable repo skeleton** with frameworks wired, TDD harness, walking skeleton, CI, Docker |
| `sdlc-deliver-story-design` | a story + committed design | thin, **reviewed** `story-design-<KEY>.md`; escalates to sdlc-arch-design (amend) if the story breaks the architecture |
| `sdlc-deliver-tests-write` | story + approved sdlc-deliver-story-design | **failing tests** (TDD red) + `test-plan-<KEY>.md`, one+ test per acceptance scenario |
| `sdlc-deliver-code-implement` | failing tests + sdlc-deliver-story-design | code on the run's `feat/<KEY>` branch (created by the platform) making tests **green**, no test weakened |
| `sdlc-deliver-tests-verify` | branch + test-plan | **PASS/BLOCK** verification: honest-green gate (coverage, no faked green, no regression) |
| `sdlc-deliver-code-review` | verified branch + standards/NFRs | **advisory** report (standards + security + acceptance + maintainability) by severity + fix list routed to `sdlc-deliver-code-implement`; blocks nothing |
| `sdlc-deliver-docs-sync` | merged story diff + committed design + AGENTS.md | updates **architecture / data-model / contracts / AGENTS.md** on the branch (proportionate; no-op when nothing changed) |
| `sdlc-deliver-impact-flag` | this run's diff + other in-progress stories' designs | Jira comment on each overlapping in-progress story + `impact-flags.md`; never blocks |
| `sdlc-deliver-pr-open` | verified, reviewed and doc-synced story | GitHub/Bitbucket **PR** (via MCP) + Jira story → **In Review** (via MCP); does not merge |
| `sdlc-tracker-sync` | approved epics / stories / sequence / bug-triage action | the matching Jira issues, links and transitions; swaps draft keys for Jira keys (in `epic-map.json` and in `epics.md`'s fan-out block) |

### Bug-fix skills
| Skill | In | Out |
|-------|----|----|
| `sdlc-fix-bug-triage` | a Jira bug | `bug-triage.md`: expected vs actual with a source, steps, severity S1–S4, affected area, one decision and the intended Jira action (`sdlc-tracker-sync` applies it on Fix) |
| `sdlc-fix-bug-reproduce` | `bug-triage.md` (Fix) | regression tests that fail with the reported symptom, guard tests, `reproduction.md`, `test-plan.md` |
| `sdlc-fix-rootcause-analyze` | reproduction + red tests | `fix-design.md`: root cause, causal chain, fix approach, target modules, blast radius, scope |

### Utility skills
| Skill | In | Out |
|-------|----|----|
| `sdlc-plan-epic-review` | an epic's full story set + committed design | **report only**: `epic-review.md` with cross-story gaps, questions and proposed changes; `sdlc-plan-stories-write` (revise) applies them; escalates architecture-conflict gaps to `sdlc-arch-design` |
| `sdlc-plan-story-review` | a written story + committed design | **report only**: `story-review.md` with gaps, questions and proposed changes; `sdlc-plan-stories-write` (revise) applies them; escalates architecture-conflict gaps to `sdlc-arch-design` |

### The two phases
**Bootstrap (run once):** `sdlc-arch-design` → `sdlc-arch-repo-scaffold`. Establishes the stack/architecture
(with your approval) and a repo that builds, lints, tests, and runs in Docker.

**Per-story loop (repeat forever, TDD):** `sdlc-deliver-story-design` → `sdlc-deliver-tests-write` → `sdlc-deliver-code-implement` →
`sdlc-deliver-tests-verify` → `sdlc-deliver-code-review` → `sdlc-deliver-docs-sync` → `sdlc-deliver-impact-flag` → `sdlc-deliver-pr-open`. Two human checkpoints per
story: the sdlc-deliver-story-design review and the PR review.

### Entry point: the story delivery workflow
You don't invoke the loop skills by hand. Under BheemBhai, the **story delivery workflow** runs
them: start it with a story key and the engine walks `sdlc-deliver-story-start` → `sdlc-deliver-story-design` →
`sdlc-deliver-tests-write` → `sdlc-deliver-code-implement` → `sdlc-deliver-tests-verify` → `sdlc-deliver-code-review` → `sdlc-deliver-docs-sync` →
`sdlc-deliver-impact-flag` → `sdlc-deliver-pr-open`. Its `on:` map handles
the loops (the `sdlc-deliver-tests-verify` BLOCK loop, architecture escalation), and its policy gates are the
human checkpoints (sdlc-deliver-story-design approval, code review). The run stops at the open PR; it never
merges. `sdlc-deliver-story-start` runs first: it refuses a story whose prerequisites are not merged and moves
the Jira story to In Progress. Start one run per story; stories in the same wave can run in
parallel.

### Fixing a bug: the bug-fix workflow
A bug is a different work item with the same back half. `sdlc-wf-bug-fix` runs three bug-only
skills, then reuses the story loop's deliver skills unchanged in behaviour:

```
sdlc-fix-bug-triage ──► bug-triage.md         decision: Fix / Duplicate / Not a bug / Needs info
        │ Fix
        ▼
sdlc-tracker-sync ──► Jira bug → In Progress (the action triage recorded)
        ▼
sdlc-fix-bug-reproduce ──► regression tests (red, with the reported symptom) + reproduction.md + test-plan.md
        │
        ▼
sdlc-fix-rootcause-analyze ──► fix-design.md   root cause at path:line, causal chain, fix at the cause, scope
        │ local / cross-module                (architectural → stop: it is a planned change, not a bug fix)
        ▼
sdlc-deliver-code-implement ──► fix on fix/<BUG_KEY>-<slug>, regression tests green
        ▼
sdlc-deliver-tests-verify ──► verification.md (PASS/BLOCK, same honest-green gate)
        ▼
sdlc-deliver-code-review ──► code-review.md (does the fix remove the cause for every caller?)
        ▼
sdlc-deliver-docs-sync ──► design docs corrected if a doc stated the wrong behaviour
        ▼
sdlc-deliver-impact-flag ──► comments on in-progress stories the fix overlaps
        ▼
sdlc-deliver-pr-open ──► PR with Expected behaviour, Root cause, Regression tests; Jira → In Review
```

Why not reuse `sdlc-deliver-tests-write` for the red phase: its scenarios come from a story's
Gherkin acceptance criteria and its good red means "feature missing". A bug's scenarios come from
the triage note and its good red means "fails **with the reported symptom**", which
`sdlc-fix-bug-reproduce` checks against a recorded signature. Bug artifacts live in
`docs/product/bugs/<BUG_KEY>/`; see "Work items" in `_SHARED-project-layout.md` for how the shared
skills find them. Policies: `sdlc-policy-bug-fix-governed` (a human approves the fix design and the
PR) and `sdlc-policy-bug-fix-fast` (no gates, for S3/S4 bugs).

### Ordering stories: `sdlc-plan-epic-sequence`
Before implementing an epic's stories, run **`sdlc-plan-epic-sequence`** to order them by dependency so a
producer (the story that creates an endpoint/table) is built before its consumers. It detects
dependencies from three sources (explicit Jira links > sdlc-deliver-story-design artifacts > requirement/data
model), topologically sorts into **waves** (same-wave stories are independent → parallelizable),
flags cycles, and writes the proposed order plus a machine-readable plan for approval;
`sdlc-tracker-sync` then mirrors the approved edges as Jira "blocks" links. `sdlc-deliver-story-start` reads that plan: it refuses to start a story whose
prerequisites aren't merged. Flow:
`sdlc-plan-stories-write → sdlc-plan-epic-review (→ stories-write revise) → sdlc-plan-epic-sequence → sdlc-tracker-sync → story delivery (wave by wave)`
— the `sdlc-wf-planning` / `sdlc-wf-planning-epic` workflows run exactly this. Running
`sdlc-plan-epic-review` first means `sdlc-plan-epic-sequence` sorts a story set whose cross-story contradictions and
missing dependency notes are already resolved, rather than baking them into the dependency graph.

### Fanning the planning run out per epic: `sdlc-wf-planning`
`sdlc-wf-planning` runs `sdlc-plan-prd-write` → `sdlc-plan-epics-create` → `sdlc-tracker-sync`, then a
`foreach` node launches **one child run of `sdlc-wf-planning-epic` per epic**. The items file is
`docs/product/epics.md`, not `epic-map.json`: an ADR-027 items file must carry exactly one fenced
block whose info string contains `bheembhai:foreach` (and every item a non-empty unique `id`), and
a JSON map cannot. `sdlc-plan-epics-create` writes that block with draft keys; `sdlc-tracker-sync`
swaps both `id` and `epic_key` for the real Jira keys on the step before the fan-out; both skills'
`verify.yaml` enforce the block's presence and completeness. Each child receives one block entry as
its run item (`ITEM.epic_key`, `ITEM.summary`, …), and `ITEM.epic_key` is also what binds the
child's `{epic}` so its artifacts land in `docs/product/epics/<EPIC_KEY>/`.

### Keeping the design current (anti-drift, for parallel teams)
Two distinct paths keep the system design and `AGENTS.md` from going stale as multiple developers
work in parallel:
- **Reactive (before code):** a story that needs an architecture change is caught by
  `sdlc-deliver-story-design`'s escalation rule and routed to `sdlc-arch-design` **amend mode**, which updates the
  design and records a new ADR before implementation proceeds.
- **Housekeeping (at every merge):** `sdlc-deliver-docs-sync` runs as its own step before `sdlc-deliver-pr-open`
  on every story, reconciling the references and `AGENTS.md` with what shipped and committing
  those updates onto the same branch so they merge atomically. It's proportionate (a near no-op
  for most stories). `sdlc-deliver-impact-flag` then runs on **every** story and **flags any in-progress
  stories the change affects** — from the code diff, not the docs — so parallel work re-aligns
  proactively instead of colliding at merge. `AGENTS.md` is treated as a first-class output because every
  future story's agent reads it first.

### Sharpening a whole epic before its stories scatter: `sdlc-plan-epic-review`
On-demand, and cheapest run right after `sdlc-plan-stories-write` finishes an epic — before `sdlc-plan-epic-sequence`,
before any per-story `sdlc-plan-story-review`, before `sdlc-deliver-story-design` touches anything. `sdlc-plan-story-review` drills
one story in isolation; some gaps only exist *across* siblings — the same actor/role several
stories assume but that's never actually defined in the data model, a requirement two stories
claim in contradicting ways (or that no story claims at all), a cross-epic dependency a story
quietly assumes but never writes down, a one-sided "depends on me" claim no sibling reciprocates.
`sdlc-plan-epic-review` loads the epic's **full** story set together, checks
`references/gap-checklist.md`'s cross-story categories, and writes one report, `epic-review.md` in
the epic's `_epic/` folder: each gap with its severity, the question a person must answer and the
proposed change for every affected story. It changes nothing else — `sdlc-plan-stories-write` (revise mode)
applies the report on the author's model family, so the same question isn't asked (and answered
differently) once per story. Same escalation posture as
`sdlc-plan-story-review`: a gap that's a real architecture conflict (not a legitimate, already-sequenced
cross-epic dependency) gets flagged to `sdlc-arch-design` rather than resolved here. It does not
compute build order — that's still `sdlc-plan-epic-sequence`'s job.

### Sharpening a story before design: `sdlc-plan-story-review`
On-demand, not an automatic stage. Whenever a story reads as ambiguous — right after `sdlc-plan-stories-write`
produces it, before `sdlc-deliver-story-design` starts, or on an old backlog story nobody's touched — run
`sdlc-plan-story-review`. It reads `architecture.md`, `data-model.md`, `api-contracts/`, and sibling stories
in the same epic, drills the story with pointed questions grounded in what actually exists (not
generic "any ambiguity?" prompts), and writes `story-review.md` in the story's folder with each gap,
its question and the proposed change. `sdlc-plan-stories-write` (revise mode) applies it. If a gap turns out to
be an architecture conflict rather than story ambiguity, it flags that for `sdlc-arch-design` (amend
mode) instead of resolving it — the same escalation posture `sdlc-deliver-story-design` uses, just one step
earlier and cheaper.

### Possible later additions
Deploy/release skills once stories are merging (e.g. a `release` skill that cuts a versioned
build and brings the Docker stack up), and a periodic dependency/security re-scan skill.

## Cost & model tiers
Each skill declares a `model:` tier in its frontmatter — `cheap`, `standard`, or `strong` —
routing it to the cheapest model that does its job well. High-judgment skills (`sdlc-arch-design`,
`sdlc-deliver-story-design`, `sdlc-deliver-code-review`, `sdlc-plan-prd-write`) are `strong`; mechanical ones (`sdlc-plan-epic-sequence`,
`sdlc-deliver-tests-write`, `sdlc-deliver-tests-verify`, `sdlc-deliver-docs-sync`, `sdlc-deliver-pr-open`, `sdlc-deliver-story-start`) are `cheap`; coding/verification sit at `standard`. The tiers are generic; map them to your actual
models in the project's AI-vendor integration (`model_high` / `model_medium` /
`model_low` — kept out of the skills so model renames don't churn them). Three cost levers are baked in:
1. **Per-skill model tier** — don't pay strong-model rates for traffic-directing.
2. **Read slices, not whole files** — skills load only the sections they act on (this fixes the
   `sdlc-plan-epic-sequence` context blowup that forced 1M-context fallback).
3. **Keep MCP results small** — request minimal Jira/GitHub fields, batch reads, don't re-fetch;
   `/compact` between stories to flush accumulated tool results. (MCP results persist for the whole
   session, which is why the Atlassian server dominated usage.)

## Where artifacts live (single source of truth)
Project artifacts live under `docs/` in the product repo; their canonical paths are declared in
the **Project Layout** table inside `AGENTS.md` at the repo root. Every skill resolves artifact
locations from that table (see `_SHARED-project-layout.md`) instead of hardcoding paths — so when
the layout moves, you change one table, not twelve skills. Current layout:

```
AGENTS.md                      # repo root — orientation + Project Layout table (source of truth)
docs/
├── architecture.md  data-model.md  tech-stack.md  testing-strategy.md
├── CHANGELOG-design.md  product-overview.md
├── adr/                       # ADR-NNN-*.md
├── api-contracts/             # *.openapi.yaml  (interface specs — source of truth)
├── design-history/            # tech-design-proposal.md
└── product/
    ├── PRD.md  epics.md  epic-map.json        # project-level
    └── epics/<EPIC_KEY>/
        ├── _epic/             # stories.md, story-map.json, sdlc-plan-epic-sequence.{md,json}, epic-review.md
        └── stories/<STORY_KEY>/   # story-review.md, story-design.md, test-plan.md, verification.md,
                                    #   code-review.md, design-sync.md  (short names, folder carries key)
```

**Per-story folders (scales to hundreds of stories):** every artifact for one story lives in its
own folder `docs/product/epics/<EPIC_KEY>/stories/<STORY_KEY>/` with short, un-suffixed filenames.
A story's files are resolved under its folder only; epic-level files sit in the epic's `_epic/`
folder; project-level files (PRD, epics, epic-map) stay at `docs/product/`. Use `epic-map.json` to
find a story's epic from its key.

`sdlc-arch-repo-scaffold` creates this tree and the `AGENTS.md` table; `sdlc-deliver-docs-sync` keeps the table
honest at each merge. **Skill-internal files** (`templates/`, `references/`, `examples/`,
`scripts/` inside each skill) are tooling — they stay in the skill folder wherever the agent
loads skills from and are never placed under `docs/`.

## Why it holds together: the traceability thread
Requirement IDs flow through every step:

```
PRD requirement (FR-006)
  → epic-map.json   : LEARN-11 covers FR-006
    → story-map.json: LEARN-23 covers FR-006
      → (later) tests and code reference LEARN-23 / FR-006
```

So at any point you can answer "is requirement X built and tested?" by following the IDs.
`sdlc-plan-epics-create` enforces that every requirement maps to exactly one epic; `sdlc-plan-stories-write`
enforces that every epic requirement is covered by at least one story.

## Jira via Atlassian MCP
Authoring and reviewer skills never write to Jira (ADR-035). The integration skills do:
`sdlc-tracker-sync` creates and updates epics and stories, sets "blocks" links and applies a bug's
triage action; `sdlc-deliver-story-start` and `sdlc-deliver-pr-open` move a story's status; `sdlc-deliver-impact-flag`
comments on overlapping stories. All go through the **connected Atlassian MCP**, not a REST script —
see `skills/sdlc-tracker-sync/references/atlassian-mcp-usage.md`.

## How to run it
Install where your agent reads skills (e.g. `.claude/skills/`), then drive the chain in order:

1. "Here are my product notes — **write a PRD**."  → `sdlc-plan-prd-write` produces `PRD.md`.
2. "**Decompose the PRD into epics** in project LEARN."  → `sdlc-plan-epics-create` writes the epics; `sdlc-tracker-sync` publishes them.
3. "**Break LEARN-11 into stories**."  → `sdlc-plan-stories-write` writes stories with acceptance criteria; `sdlc-tracker-sync` publishes them.

## Reporting the outcome (BheemBhai pipeline)

Run standalone, you read a skill's artifacts yourself. Run **under BheemBhai**, a runner wraps
every invocation and owns the control-plane result — so **a skill never writes the result JSON,
and a skill author never needs its schema.**

- The runner (`agent/run_skill.sh`) composes the prompt: it invokes the skill and appends the
  outcome contract. The exact template is in `docs/architecture.md` (§Context passing between
  steps).
- The agent must end its final reply with a verdict line:
  `BB_OUTCOME: <one of the allowed statuses>`. Allowed statuses are **step-specific** — the
  workflow's `on:` map decides which ones route — and are injected into the step's context
  (`allowed_result_statuses` + `result_status_meanings`), along with the skill's other inputs.
  The domain verdicts are `completed`, `BLOCK`, `changes_requested`, `escalation_required`;
  choose the one that honestly describes the execution, from the injected list only.
- Some skills have an `## Outcomes` section. It holds only the calls `verify.yaml` cannot make
  in code: judgement escalations (sdlc-deliver-story-design needs a new service), edge cases that are valid
  completions (an unrecognized stack), and the verdict that is the skill's own job (sdlc-deliver-tests-verify's
  PASS/BLOCK). Inputs (preconditions, run before the agent) and output structure (checks, run
  after) stay in `verify.yaml` only. The section never redefines a word or names a routing target.
- Optionally, before it, one line per file a human should review:
  `BB_REVIEW: <path> | <short reason>` — these become the reviewer's default file list in the UI.
- The runner parses those lines and writes `bb_step_result.json` itself (verdict, summary,
  files, commit, cost). **Do not create or modify any file to report the outcome** — the reply
  lines are the only thing read. Skills' own hand-off artifacts (`result.json`, report `.md`s)
  stay skill-owned; that is why the control-plane file carries a distinct name.
- If the step dies before a verdict — crash, deadline, missing result — the runner/engine
  classify it (`failed_execution` / `failed_infra` / `failed_timeout` / `failed_incomplete`) and
  retry where appropriate. An absent `BB_OUTCOME` line degrades to `completed`.
- **Ad-hoc interactive sessions** (ADR-016) are the exception: no contract lines — the final
  reply is shown to the user verbatim.

Details: `docs/architecture.md` §Context passing between steps; ADR-005 (execution artifacts);
ADR-014 (results over object storage). The runner itself is `agent/run_skill.sh`.

## Worked example (Learn Portal)
Each skill ships a real example produced from the Learn Portal whitepaper:
- `prd/examples/PRD.md` — 8 feature areas, 18 FRs, 5 NFRs.
- `prd-decompose/examples/epics.md` + `epic-map.json` — 8 epics, verified 1:1 coverage of all 23 requirements.
- `user-story/examples/stories-LEARN-11.md` + `story-map-LEARN-11.json` — epic LEARN-11 expanded into 3 stories with Gherkin criteria.

## Conventions
Tool-agnostic (Claude Code + Codex), Jira via Atlassian MCP, artifact-driven hand-offs,
ID-based traceability end to end. Skills are product-agnostic and reusable across projects.

**Test layout** mirrors the source tree so tests stay maintainable at scale: test-type at the top
(`tests/unit|integration|e2e/`), module sub-folders under each (`tests/unit/<module>/test_*.py`),
mapping `app/<module>/x.py` → `tests/unit/<module>/test_x.py`. `sdlc-arch-repo-scaffold` establishes it;
`sdlc-deliver-tests-write` places each story's tests under the right module folder (never flat). Tests track
code structure, not ticket structure — the per-story `test-plan.md` links tests back to the story.

**Backend vs UI stories** are handled by domain tagging, not separate skills. `sdlc-deliver-story-design` tags
each story **backend / frontend / full-stack**. `sdlc-deliver-code-implement` then loads the matching domain lens —
`references/backend.md` (contracts, validation, persistence, security) and/or
`references/frontend.md` (which reads `docs/ui-conventions.md` for component structure, design
tokens, state pattern, required loading/error/empty/success states, and accessibility). The
project's UI knowledge lives in `docs/ui-conventions.md` — a thin starter `sdlc-arch-design` proposes
(since most projects begin with no design system) that `sdlc-deliver-docs-sync` grows by promoting patterns UI
stories establish. `sdlc-deliver-tests-write` writes API/integration tests for backend, component/e2e for UI.
One `sdlc-deliver-code-implement` skill, domain-aware via lenses + a project UI-context artifact.
