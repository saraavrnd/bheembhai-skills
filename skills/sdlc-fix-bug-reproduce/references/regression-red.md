# Regression red — what a valid failing bug test looks like

## Good red
- The test reaches its assertion and fails, and the failure output contains the symptom
  signature (the error message, status code or exception the reporter saw).
- Example: `assert 415 == 201` with `{"error": "Unsupported file type"}` in the captured body.

## Bad red (fix the test, not the code)
- **Errors instead of fails:** ImportError, fixture error, syntax error, runner cannot find the
  test. The test never reached the behaviour.
- **Wrong symptom:** it fails, but with a different message or status. You are reproducing a
  different bug, or your setup is wrong (missing auth, wrong course id, empty DB).
- **Asserts the bug:** it passes today because it asserts the current broken output. Flip it to
  assert the expected behaviour.

## A regression test that passes immediately
Either the bug is already fixed on this branch (check recent commits, then report), the steps
lost an essential detail (go back to the *assumed* items in triage), or the test is too weak.
Do not hand off a green regression test.

## Choosing the signature
- Shortest string that is unique to the symptom: `Unsupported file type` beats `415`, because
  many things return 415.
- Copy it from the buggy code's actual output, not from the report's paraphrase.
- For exceptions, use the type and the stable part of the message: `KeyError: 'mime_type'`.
- For UI bugs, the visible text or the missing element's accessible name.

## Guard tests
Guards pin the behaviour next to the bug so a fix cannot over-correct. Good guards for
"uppercase .PDF rejected": lowercase `.pdf` still accepted, `.exe` still rejected, `.PdF`
accepted. They pass today and must pass after the fix. Keep them few (one to three).

## Layers
Prefer the lowest layer that shows the symptom, but keep one test at the layer the user saw. A
unit test alone can pass while the endpoint still fails (for example, the route never calls the
fixed function).
