---
name: sdlc-arch-ui-conventions
role: author   # ADR-035: author | reviewer | integration
description: >
  Propose the thin UI-conventions starter for a GREENFIELD product whose approved architecture
  includes a frontend: component structure, a minimal set of design tokens, the state and
  data-loading pattern, the required UI states, the accessibility bar and responsive breakpoints —
  written to `docs/ui-conventions.md` for approval. Use this right after `sdlc-arch-design` is approved
  and before `sdlc-arch-repo-scaffold`, only when the architecture has a UI. Trigger this even when the
  user just says "set up UI conventions", "propose a design system starter", "how should our
  frontend look and behave", or "write ui-conventions.md". It writes that one file; it does not
  design the system (`sdlc-arch-design`) or scaffold code (`sdlc-arch-repo-scaffold`).
compatibility: >
  Tool-agnostic (Claude Code or Codex). Reads the committed `docs/architecture.md` and
  `docs/tech-stack.md`. Writes only `docs/ui-conventions.md`.
model: sonnet   # tier: standard (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-arch-ui-conventions — Thin UI Conventions Starter (propose → approve)

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table in
> the conventions file of the repo (`AGENTS.md`, or `CLAUDE.md` when the repo has none). The current
> layout places this file at `docs/ui-conventions.md`. This skill's own `templates/` stays inside
> the skill folder.

Section guidance for this skill's templates is in `references/template-guide.md`. Read the part for a template before you fill it.

> **Single responsibility (ADR-035):** this is an `author` skill split out of `sdlc-arch-design`. It
> writes `docs/ui-conventions.md` only.

`docs/ui-conventions.md` is the UI source of truth that `sdlc-deliver-code-implement`'s frontend lens reads,
so UI stories come out consistent instead of ad hoc. Most projects START with no design system, so
this skill PROPOSES a thin, sensible starter for a person to approve at the gate after it.

## Input it expects
- The approved `docs/architecture.md` and `docs/tech-stack.md` from `sdlc-arch-design`.
- The PRD's personas and any UI notes, only as far as they constrain the UI (devices, brand,
  accessibility obligations).

## Output it produces
`docs/ui-conventions.md`, from `templates/ui-conventions.md.tmpl`. Nothing else changes.

## Procedure

### Step 1 — Confirm there is a UI
Read the architecture and tech stack. If there is no frontend (pure backend, CLI, API only), write
nothing and finish with a one-line note that the skill does not apply.

### Step 2 — Fill the starter
Cover the decisions that otherwise get made inconsistently per story:
- **Component framework & structure** — the chosen frontend stack and how components are organized
  (mirroring the source-tree convention).
- **Design tokens (minimal)** — a starting spacing scale, color roles (primary/surface/text/
  error/etc.), and typography, so stories don't each invent their own values.
- **State & data-loading pattern** — where state lives (local vs shared store) and how API data is
  fetched/loaded, so every UI story follows one approach.
- **Required UI states** — loading / error / empty / success must all be handled.
- **Accessibility bar** — semantic HTML, labels, keyboard operability, contrast.
- **Responsive expectations** — the breakpoints to support.

Keep it THIN — a starter that creates baseline consistency, not an exhaustive design system. It is
designed to GROW: `sdlc-deliver-docs-sync` promotes patterns that UI stories establish into this file
over time.

### Step 3 — Hand off
Tell the user the starter is ready for approval and that `sdlc-arch-repo-scaffold` is next.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **completed**: The architecture has no frontend, so there is nothing to write. Say so in one line.

## Reference files
- `templates/ui-conventions.md.tmpl` — the starter's structure.
