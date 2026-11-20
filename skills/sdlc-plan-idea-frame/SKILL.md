---
name: sdlc-plan-idea-frame
role: author   # ADR-035: author | reviewer | integration
description: >
  Frame a raw product idea before anyone writes requirements: restate the idea as given, name the
  problem, the users and the value hypothesis, separate what was stated from what is inferred,
  and list the questions that would change the PRD's shape, each with a proposed default answer.
  Writes one file, `idea-brief.md`. Use this as the FIRST step of `sdlc-wf-planning-prd` (idea to
  PRD), or whenever someone says "here's an idea", "help me shape this concept", "what do we need
  to know before writing a PRD", or pastes rough notes that are not yet ready for requirements.
  It writes no requirements: `sdlc-plan-prd-write` turns the brief, plus the answers a person gives
  at the gate, into the PRD.
compatibility: >
  Tool-agnostic (Claude Code or Codex). No external tools required. Reads the run's input (the
  idea text, notes, transcript or whitepaper) and, when the repo already has them, the PRD and
  AGENTS.md for context. Writes only `idea-brief.md`; no Jira writes.
---

# sdlc-plan-idea-frame — Shape an Idea into a Brief

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table
> in the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see
> `_SHARED-project-layout.md`. The current default places the brief next to the PRD:
> `docs/product/idea-brief.md`. If no repo or AGENTS.md exists yet, write it there anyway; do not
> create AGENTS.md (that is `sdlc-arch-repo-scaffold`'s job). This skill's own `templates/`,
> `references/` and `examples/` stay inside the skill folder and never move under `docs/`.

Section guidance for this skill's template is in `references/template-guide.md`. Read it before
you fill the template.

> **Cost & context:** This skill runs at the model tier its workflow step sets. The input is
> usually short; if it is a long whitepaper or transcript, read it once and quote only the lines
> you rely on.

> **Single responsibility (ADR-035):** this is an `author` skill that writes **one file**. It
> frames the idea and asks; it never writes requirements, feature areas or epics. Under
> BheemBhai an agent cannot stop mid-run to ask a person, so the brief is where the questions
> live: the governed policy's gate on this step is where a person answers them, and the answers
> travel to `sdlc-plan-prd-write` in the run hand-off.

## Why this step exists
`sdlc-plan-prd-write` used to read the idea and "ask only blocking questions". Run unattended,
nobody can answer, so the PRD either invents the product's core or stops. Framing first gives a
person one short, cheap document to correct (wrong users, wrong problem, a hard constraint
nobody wrote down) before the expensive, decomposable PRD is written and reviewed.

## Input it expects
- The idea, in any form: a one-liner, concept notes, a whitepaper, a transcript or a mix
  (`context.query`, plus any files the run attached).
- Optional: an existing `PRD.md` or product overview, when the idea extends a product that
  already exists. Read only the sections that bound the new idea.

## Output it produces
One file: `docs/product/idea-brief.md`, following `templates/idea-brief.md.tmpl`.

## Procedure

### Step 1 — Restate the idea as given
Quote or closely paraphrase the input in **Idea as given**. Nothing added. This is the yardstick
the PRD reviewer later uses to tell a faithful PRD from an invented one.

### Step 2 — Frame it
Fill **Problem**, **Target users**, **Value hypothesis**, **Constraints** and **Non-goals**.
Write the problem without the solution. Keep target users to the types that would change what
gets built. A value hypothesis is one falsifiable sentence: "If <users> can <capability>, then
<measurable change>".

### Step 3 — Separate stated from inferred
Every claim the brief makes that the input did not say goes into **Assumptions** as an `A-n`
row marked `Inferred`, with the reason. Things the input did say may be listed as `Stated` when
the PRD depends on them. Never present an inference as given.

### Step 4 — Ask only shape-changing questions
List questions in **Open questions** as `Q-n` rows. Mark a question `Blocking` only if different
answers would produce a different PRD shape: different target users, a different MVP boundary, a
hard constraint (compliance, platform, data residency, budget, deadline), or a different core
lifecycle (who creates the main entity). Everything else is `Non-blocking`.

**Every question carries a proposed default answer.** If nobody answers at the gate (the fast
policy has no gate on this step), `sdlc-plan-prd-write` adopts the default and records it as an
assumption, so the run never stalls on a question. Cap the list at about seven questions; if
you need more, the idea is too thin (see Outcomes).

### Step 5 — Readiness
In **Readiness**, write one line: `Ready for PRD` (no Blocking questions, or every Blocking
question has a defensible default) or `Needs framing` (see Outcomes). Then stop.

## What this skill is NOT
- Not a PRD. No `FR-`/`NFR-` ids, no feature areas, no release tags.
- Not market or customer research. It frames what was given; it does not go looking for
  competitors or interview data (see SK-003 for why that is a later, optional step).
- Not an editor of anything else: no PRD, no AGENTS.md, no Jira.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: The idea is too thin or self-contradictory to frame without inventing its core (no identifiable user or problem, or two incompatible products described). Readiness says `Needs framing`; the brief lists what is missing.
- **completed**: The brief is written. Blocking questions are fine here: each has a default, and the gate is where a person answers them.

## Reference files
- `templates/idea-brief.md.tmpl` — the structure to fill in.
- `references/template-guide.md` — section-by-section guidance.
- `references/question-guide.md` — what makes a question Blocking, with examples.
- `examples/idea-brief.md` — a worked brief for the Learn Portal idea that `sdlc-plan-prd-write`'s
  example PRD was written from.
