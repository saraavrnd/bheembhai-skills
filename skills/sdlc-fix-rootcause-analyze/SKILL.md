---
name: sdlc-fix-rootcause-analyze
description: >
  Find why a reproduced bug happens and write the fix design: the root cause with file:line
  evidence, the causal chain from that line to the observed symptom, the smallest fix that removes
  the cause (not the symptom), the modules it touches, and its blast radius. Use this as the third
  step of the bug-fix workflow, after sdlc-fix-bug-reproduce has a failing regression test and
  before sdlc-deliver-code-implement. Trigger this even when the user just says "why does LEARN-87
  happen?", "root-cause this", "find the cause", "RCA", or "plan the fix". It writes fix-design.md
  only. It does NOT change code or tests.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Read-only on code: reads the modules under test, git
  log/blame for them, architecture.md, data-model.md and the API contracts. May run the
  regression tests under a debugger or with extra logging, but commits no such change.
model: opus   # tier: strong (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-fix-rootcause-analyze — Explain the Bug, Then Plan the Fix

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table in
> `AGENTS.md` at the repo root. Do not hardcode paths. **Per-bug
> artifacts live in that bug's own folder** `docs/product/bugs/<BUG_KEY>/` (`{layout.bug_dir}`).
> `fix-design.md` is the bug's **design note** (`{layout.design_note}` on a bug run): the shared
> deliver skills read it where a story run reads `story-design.md`.

> **Cost & context:** This skill runs at the strong tier because a wrong root cause wastes every
> later step. Start from the failing test and walk outward; do not read whole modules up front.

The regression test proves the bug exists. This skill answers **why**, and turns the answer into
a design note `sdlc-deliver-code-implement` can build to, exactly as it builds to a story design.
The discipline that matters: fix the **cause**, not the place the symptom shows up. A fix at the
symptom (catch the exception, special-case the input) makes the test green and leaves the bug
alive one call away.

## Input it expects
- `reproduction.md` (symptom signature, minimal failing case) and `test-plan.md` from
  `sdlc-fix-bug-reproduce`; the regression tests are red.
- `bug-triage.md` (expected behaviour, affected area).
- The code, its git history, and the committed design (architecture.md, data-model.md,
  api-contracts/, ADRs).

## Output it produces
- `fix-design.md` in the bug's folder, from `templates/fix-design.md.tmpl`, with a **Scope** of
  `local`, `cross-module` or `architectural`, and a **domain tag** (backend / frontend / full-stack)
  for the implement step's lens.

## Procedure

### Step 1 — Trace from the symptom inward
Run the minimal regression test. Starting from where the signature is produced, walk the call
path backwards (route → service → helper) until you reach the first line whose behaviour differs
from what the expected behaviour needs. That line is the candidate cause. Cite it as
`path:line`. Use `references/root-cause-techniques.md` for tracing, bisecting and the five-whys
check.

### Step 2 — Prove the causal chain
Write the chain as numbered links from the cause to the signature: each link is one fact you
observed (a value, a branch taken), with its `path:line`. If one link is a guess, say so and test
it (temporary log line or debugger, never committed). A chain with an unproven link is a
hypothesis, not a root cause.

### Step 3 — Ask why the cause exists
One level up: was it a wrong assumption, a missing case in the original story's design, a
library behaviour change, a data shape nobody anticipated? Use `git log -L` / `git blame` on the
cause line and note the commit and story that introduced it, if found. This shapes the fix (fix
the assumption, not only the line) and tells docs-sync whether the design docs were wrong too.

### Step 4 — Design the smallest fix at the cause
- Fix where the wrong behaviour originates. If several callers share the faulty helper, fix the
  helper, and list every caller under Blast radius.
- Name target modules, any interface change (usually none), and any data-model delta (usually
  none). A fix that needs a migration or a contract change is not a local fix.
- Check for siblings: the same wrong assumption elsewhere (grep for the pattern). List them;
  fix them in this run only if they are the same cause in the same module, otherwise note them
  for new bugs.
- If existing stored data is already wrong because of the bug, say so under Data-model deltas.
  Repairing it is not part of the code fix.

### Step 5 — Classify the scope
- **local** — one module, no interface or data change.
- **cross-module** — more than one module, still inside the architecture, no contract change.
- **architectural** — needs a contract, ADR, data migration or architecture change. Stop here:
  that is a planned change, not a bug fix.

### Step 6 — Write fix-design.md and hand off
Fill the template. Keep it to about a page. Hand off to `sdlc-deliver-code-implement`, whose job
is to make the regression tests pass by building exactly this fix.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: The correct fix changes an API contract, an ADR or the architecture,
  needs a schema migration, or needs a repair of production data the bug already wrote. Set
  Scope to `architectural`.
- **escalation_required**: The cause is in a third-party dependency and there is no in-repo fix
  or workaround short of an upgrade the architecture has not approved.
- **completed**: Scope is `local` or `cross-module`, including when you found sibling occurrences
  in other modules and listed them for separate bugs.

## Rules
- **No code changes.** Debug logging or breakpoints are fine while investigating; none of it is
  committed.
- **Cause, not symptom.** "Catch the error and return 201" is never a root-cause fix.
- **Evidence for every link.** Each causal link cites `path:line` or a recorded observation.

## Reference files
- `templates/fix-design.md.tmpl` — the fix design (hand-off to sdlc-deliver-code-implement).
- `references/root-cause-techniques.md` — tracing, bisecting, five whys, cause vs symptom.
- `examples/fix-design-LEARN-87.md` — root cause and fix design for LEARN-87.
