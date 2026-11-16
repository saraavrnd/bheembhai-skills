# Revisions — BSB-35

## Pass 1 — 2026-11-16 — verifier check `no_template_residue`

**Report applied:** automated verifier rejection of the previous `sdlc-plan-stories-write`
attempt for epic BSB-35 (`builtin:md_no_placeholders`, reason code `placeholder_left`).

**Finding:** the compare-contract paragraph declared the two `flips-unavailable` message
templates inside inline code spans that wrapped across lines 200–201. The placeholder scanner
reads the document line by line, so the wrapped spans left `<id>` outside a recognised code
span and it reported both as unfilled `<...>` template slots. The messages themselves were
complete specifications; only their line wrapping was wrong.

**What changed:**

- `stories.md` — the compare-contract paragraph now keeps each of the two exact-text code spans
  (`Checks not retained for comparison (run <id> evidence was purged).` and `Checks not
  available for comparison (run <id> is not verified).`) on a single line. The rendered text,
  the `evidence_purged`/`run_not_verified` conditions and the run-id selection rule are
  unchanged.
- `stories.md` and `story-map.json` — each story's summary now names the two surfaces it
  covers (the HTML page and the JSON API): *List a skill's accessible runs with commit SHA,
  input branch, verdict and checks on page and API*, *Compare two runs of one skill side by side
  on page and API*, and *Highlight checks that flipped between two compared runs on page and
  API*. The same wording is mirrored between the `**Summary:**` line and `story-map.json`. No
  story key or requirement mapping changed.

**Coverage:** unchanged. FR-104, FR-105 and FR-106 are still each covered by exactly one story
(BSB-35-PENDING-1, -2 and -3 respectively), and `story-map.json` maps every requirement to the
same story as before.

**Still open:** none.
