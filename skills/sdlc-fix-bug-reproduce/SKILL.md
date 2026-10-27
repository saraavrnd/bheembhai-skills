---
name: sdlc-fix-bug-reproduce
description: >
  Reproduce a triaged bug as an automated regression test that FAILS today with the reported
  symptom, plus guard tests for the neighbouring cases that already work. This is the TDD red
  phase for a bug. Use this as the second step of the bug-fix workflow, after sdlc-fix-bug-triage
  decides Fix and before sdlc-fix-rootcause-analyze. Trigger this even when the user just says
  "reproduce LEARN-87", "write a failing test for this bug", "can you make it happen?", or "add a
  regression test". It writes tests, reproduction.md and test-plan.md. It does NOT find the root
  cause and does NOT fix the bug.
compatibility: >
  Tool-agnostic (Claude Code or Codex). Uses the project's test runners from testing-strategy.md
  and the deployed Docker Compose stack for integration and browser reproductions. Reads
  bug-triage.md and the existing test harness.
model: sonnet   # tier: standard (haiku=cheap, sonnet=standard, opus=strong)

---

# sdlc-fix-bug-reproduce — Make the Bug Fail on Demand

> **Artifact paths:** Resolve all project-artifact locations from the **Project Layout** table in
> the repo's conventions file (`AGENTS.md`, or `CLAUDE.md` when the repo has none) — see `_SHARED-project-layout.md`. Do not hardcode paths. **Per-bug
> artifacts live in that bug's own folder** `docs/product/bugs/<BUG_KEY>/` (`{layout.bug_dir}`).
> Tests go in the project's test tree, never in the bug folder.

> **Cost & context:** This skill runs at the `model:` tier in its frontmatter. Load only
> bug-triage.md, the modules named under Affected area, and the existing tests for those modules.

A bug you cannot reproduce is a bug you cannot prove you fixed. This skill turns the triage
steps into a test that fails **now, with the same symptom the reporter saw**. That test is the
executable definition of "fixed" for the rest of the chain: `sdlc-deliver-code-implement` makes
it pass, `sdlc-deliver-tests-verify` makes sure it was not weakened, and it stays in the suite
forever so the bug cannot quietly come back.

> Red for a bug means something different from red for a story. A story test fails because the
> feature is missing. A regression test fails because the feature is **wrong**, and the failure
> output must show the reported symptom. A test that fails for any other reason reproduces a
> different bug.

## Input it expects
- `bug-triage.md` with **Decision: Fix**, expected vs actual, and numbered steps.
- The test harness and conventions from `testing-strategy.md`; the harness is green.

## Output it produces
- **Regression test(s)** that fail now with the reported symptom, placed under the module folder
  that mirrors the source (`tests/<layer>/<module>/`), never flat.
- **Guard test(s)** (optional, recommended) for the closest cases that work today, so the fix
  cannot break them. Guards pass now and must still pass after the fix.
- `reproduction.md` — what was run, the observed symptom with its **signature**, and the red run.
- `test-plan.md` — the scenario → test table the shared deliver skills read.

## Procedure

### Step 1 — Run the triage steps by hand first
Bring up the stack the steps need and follow them literally. Record what you ran and what came
back under Reproduction. If it does not reproduce, vary only the details triage marked
*assumed* (content type, role, data shape) and record each attempt. Fix any assumed detail that
turned out wrong.

### Step 2 — Capture the symptom signature
Pick the shortest string that identifies the symptom in test output: an error message, a status
code with its body, an exception type. Write it on the `**Signature:**` line in backticks. The
platform checks that the regression tests fail with this string in their output, so pick
something the buggy code actually emits, not a paraphrase.

### Step 3 — Shrink to the smallest failing case
Find the lowest layer that still shows the symptom: a unit test of one function beats an
integration test, which beats an e2e test. Keep one test at the layer the user saw (usually
integration, the endpoint) and add a lower-layer test if you found one. Record the minimal input
under Minimal failing case. Do not guess the cause; you are narrowing the input, not reading the
fix.

### Step 4 — Write the tests
- **Regression tests** assert the **expected** behaviour from bug-triage.md, so they fail now and
  will pass once the bug is fixed. Never assert the buggy behaviour.
- **Guard tests** cover the nearest working cases (e.g. the lowercase variant, the other
  formats). They pass now.
- Name test files after the unit under test (mirror the source tree). Put the bug key in each
  regression test's docstring or a comment, so `git grep <BUG_KEY>` finds it.
- Pin exact values: the status code, message and state that triage cites as expected.
- Do not touch production code. If the test cannot be written without a hook in production code,
  stop and say so.

### Step 5 — Run them and confirm the right red
Run the new tests. Every regression test must **fail** (not error) with the signature in its
output; every guard test must **pass**. Paste the run under Red-phase verification. See
`references/regression-red.md` for good vs bad red.

### Step 6 — Write test-plan.md and hand off
Fill `templates/test-plan.md.tmpl`. Each row is one scenario, tagged `regression` or `guard` in
the Type column. Hand off to `sdlc-fix-rootcause-analyze`.

## Rules that keep the red honest
- **Assert the expected behaviour, never the current one.** A test that passes today and fails
  after the fix is backwards.
- **Same symptom, not a nearby one.** If the only failure you can produce has a different error,
  you have found a different bug. Record it under Notes and keep looking for the reported one.
- **No production edits, no skips.** Red phase writes tests and notes only.

## Outcomes

BheemBhai checks this skill's inputs before you start and its output's structure after you
finish (`verify.yaml`), so don't spend effort re-checking those. This section covers only the
calls code can't make: each line gives a situation and the word it gets. What each word means
is injected at run time.

- **escalation_required**: After following the steps and varying every assumed detail, the
  reported symptom does not occur in the run environment (environment-, data- or timing-specific
  and you cannot force it). Record every attempt in reproduction.md.
- **escalation_required**: Running the steps shows the behaviour matches the documented
  expectation, so triage was wrong.
- **completed**: The symptom reproduces only at a lower layer than reported, or only after you
  corrected an assumed detail. Say so in reproduction.md.

## Reference files
- `templates/reproduction.md.tmpl` — the reproduction record (hand-off to root-cause analysis).
- `templates/test-plan.md.tmpl` — the scenario → test table read by the shared deliver skills.
- `references/regression-red.md` — good red vs bad red for a bug; choosing the signature.
- `examples/` — reproduction and test plan for LEARN-87.
