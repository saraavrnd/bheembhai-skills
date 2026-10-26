# Root-cause techniques

Use the cheapest technique that produces evidence. Stop when every link in the causal chain is
observed, not inferred.

## 1. Trace backwards from the signature
1. Find where the signature string or exception is produced (`git grep "<signature>"`).
2. Set a breakpoint or a temporary log line there; run the minimal regression test.
3. Note the inputs that reached that point. Walk one caller up and repeat.
4. Stop at the first line whose output is wrong **given correct inputs**. Everything below it is
   a consequence; everything above it is innocent.

## 2. Compare a passing and a failing input
The guard tests are a gift: run the failing case and the nearest passing case side by side and
diff the values at each step. The first divergence is the cause or very close to it.

## 3. Bisect when it used to work
If triage or the history says the behaviour worked before, `git bisect run <regression test>`
between a known-good tag and HEAD finds the introducing commit. Record it under "How it got in".

## 4. Five whys (one level is usually enough)
Ask "why does this line do that?" until the answer is a decision, not a line of code. Example:
- Why 415? `is_allowed_type` returned False.
- Why False? It compares the extension with `ALLOWED = {".pdf", ".docx", ".txt"}` as is.
- Why as is? The LEARN-21 design assumed lowercase names; no test covered case.
The fix goes at the second answer (normalise case); the third answer goes under "How it got in"
and tells docs-sync nothing in the design docs needs changing.

## Cause vs symptom: quick test
| Proposed fix | Cause or symptom? |
|--------------|-------------------|
| Lower-case the extension inside the allowlist check | Cause |
| Catch the 415 in the route and retry with a lower-cased name | Symptom |
| Special-case `".PDF"` in the allowlist | Symptom (and fixture special-casing) |
| Wrap the call in try/except and log | Symptom |

A fix is at the cause when, after it, **no caller** can reach the wrong behaviour, not only the
caller in the test.

## Scope classification
| Needs | Scope |
|-------|-------|
| Change inside one module, same interface | local |
| Change in a shared helper plus its callers, same interfaces | cross-module |
| Changed API contract, new/changed table or column, new dependency, ADR change | architectural |
| Repair of data already stored wrongly | architectural (escalate; repair is its own change) |

## Things that are not evidence
- "This code looks suspicious."
- A stack trace line without the values that reached it.
- The reporter's guess.
