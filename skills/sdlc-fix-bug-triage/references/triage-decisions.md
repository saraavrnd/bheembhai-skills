# Triage decisions

Exactly one decision per bug. The decision is what the rest of the workflow keys off, so it must
be a defensible call, not a hedge.

## Fix
A defect against a documented expectation, with steps another engineer could follow.
- Steps may contain *assumed* details (a payload filled in from the contract, a role guessed from
  the screenshot). That is fine; the reproduce step will confirm or correct them.
- Intermittent bugs are Fix if you can describe the conditions (load, timing, data shape), even if
  you cannot yet force them.

## Duplicate of `<KEY>`
Same symptom **and** same path as an open bug, or one fixed in the last release that has
regressed. Name the key.
- Same symptom, different path (e.g. 415 on upload via API vs via bulk import) is **not** a
  duplicate. Link it and decide Fix.
- If the earlier bug was closed as fixed and the symptom is back, decide **Fix** and note
  "regression of `<KEY>`" under Notes. A regression is a new bug run.

## Not a bug
The behaviour matches what a story, contract or the architecture says.
- Quote the source in Expected vs actual so the reporter can see why.
- If the documented behaviour is clearly wrong for users, it is still Not a bug here: it is a new
  story or a story change. Say so in the reason.

## Needs info
Use when either holds:
- You cannot write steps another engineer could follow, even with assumptions (no route, no
  input, no observable result).
- No document defines the expected behaviour, so "is this wrong?" is a product decision. Say
  which decision is needed and who usually makes it (product owner, designer).

## Borderline cases
| Situation | Decision |
|-----------|----------|
| Report mixes two symptoms | Fix the one with the clearer path; note the other for a separate bug |
| Expected behaviour is defined only by a sibling feature's behaviour | Fix, cite the sibling, mark the expectation *inferred* |
| Third-party outage caused the symptom and nothing in our code is wrong | Not a bug |
| Third-party behaviour changed and our code no longer handles it | Fix |
| Only reproducible in production data you cannot see | Fix if the data shape is described; otherwise Needs info |
