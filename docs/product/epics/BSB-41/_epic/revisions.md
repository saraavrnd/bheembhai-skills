# Revisions — BSB-41 stories

## Pass 1 — 2026-11-17

**Report applied:** automated verifier rejection of the previous `sdlc-plan-stories-write` attempt
for BSB-41. No `epic-review.md` or `story-review.md` was present and the hand-off carried no open
questions, so the one reported failing check was actionable in full.

### Finding → change

| Finding | Change |
|---------|--------|
| `scenario_executable` — the "Clone pinned to the base commit when main moves" scenario named target commit `9b3c5e7a1d2f4b6c8e0a2c4e6f8a0b2c4d6e8f0a` without defining its tree, content, author/committer identity, timestamps or message, so the exact commit could not be materialized from the fixture | Removed the literal `9b3c5e7a…` commit and every reference to it. Added a **fixture change commit `C`** definition to the fixture preamble: parent `4f2a9c1d0b6e8f3a2c5d7e9f1b3a5c7d9e1f2a4c`, tree equal to that commit's tree except `skills/sdlc-research-summarise/SKILL.md` replaced by an exact quoted markdown block, author and committer `Fixture <fixture@example.test>`, both dates `2026-11-16T09:00:00+00:00`, message exactly `fixture: change research summarise`. Its SHA is read at test time as `C=$(git rev-parse main)`; no scenario asserts a literal SHA for it. |
| `scenario_executable` — the required interleaving ("resolves `main` when the clone starts" and the push lands "before the copy completes") had no specified synchronization point, hook or observable event, so the test would be a race and could silently pass a buggy implementation | Removed the mid-copy interleaving rather than inventing an implementation hook. The edge case "the source skill changes while a clone is prepared" is now covered by two deterministic scenarios in `BSB-41-PENDING-1`: **"Clone copies the recorded base commit rather than the checkout working tree"** (the working tree carries one exact uncommitted edit; the clone must copy the committed blob at `base_sha`, verified by comparing the frontmatter values and post-frontmatter body against that blob) and **"A main move affects neither an existing clone build nor the base of the next clone"** (clone, then apply commit `C` to `main`, then clone again: the first build's head and blob stay unchanged while the second clone's `base_sha` is `C` and its copied blob equals the blob at `C`). Both are ordered sequentially at the git level, so no timing window is required. |
| `scenario_executable` — the scenario's `When` gave no clone request body or endpoint (only inferable from another scenario) | The replacement `When` gives the full endpoint `POST /api/builds` and the exact JSON body. The same gap in `BSB-41-PENDING-2`'s "A concurrent clone of the same skill leaves the edit build untouched" scenario was tightened to the same exact body and endpoint. |

### Still open

- None. The reported finding was applied without needing a gate answer.

### New problems noticed

- None. Requirement coverage is unchanged (FR-011, FR-012, FR-013, FR-014, FR-124, FR-125,
  FR-126 all still covered), so `story-map.json` needs no update.

### Known input caveat (re-checked this pass)

The Jira work item `SkillBuilder-2` is still unavailable: a direct Atlassian REST fetch of
`https://saraavrnd.atlassian.net/rest/api/3/issue/SkillBuilder-2` returns HTTP 404 ("Issue does
not exist or you do not have permission to see it"). The Atlassian MCP server configured in
`.mcp.json` was not exposed as a tool in this session, so the read-only REST endpoint was used.
This is already recorded in `docs/product/PRD.md` §8 and `docs/product/epics.md`; the stories
remain grounded in the BSB-41 epic section, `epic-map.json` and the PRD requirement wording.

## Pass 2 — 2026-11-17

**Report applied:** the automated verifier rejection of Pass 1. The hand-off named two failing
checks: the `scenario_executable` judge criterion on `BSB-41-PENDING-1`, and an artifact check that
`story-map.json` had not changed since precheck. No `epic-review.md` or `story-review.md` was
present and the hand-off carried no open questions, so both checks were actionable in full.

### Finding → change

| Finding | Change |
|---------|--------|
| `scenario_executable` — in `BSB-41-PENDING-1`, the final assertion of "A main move affects neither an existing clone build nor the base of the next clone" required the new clone's `skills/sdlc-research-brief/SKILL.md` blob SHA to equal the source `C:skills/sdlc-research-summarise/SKILL.md` blob SHA, which cannot hold once the frontmatter `name:` is rewritten. The "Whole skill folder copied byte-for-byte" scenario repeated the conflict by requiring every cloned blob's SHA, including `SKILL.md`'s, to equal the source blob's SHA. | Added a **Frontmatter name rewrite rule** to the fixture preamble: a clone changes exactly one line of `SKILL.md` — the value of the top-level `name` key, preserving quoting style and any trailing comment — and copies every other line and file byte-for-byte. The rewrite rule states that a cloned `SKILL.md` blob's SHA therefore differs from its source's, and that blob SHAs are asserted equal only for the other files. Renamed and rewrote "Whole skill folder copied, with only the SKILL.md name line rewritten": the 6 non-`SKILL.md` files must have equal blob SHAs, while `SKILL.md` must differ in exactly the `name:` line. Replaced the contradictory final assertion in the main-move scenario with the exact expected transformation: the clone's `SKILL.md` equals the source blob at `C` with `name: "sdlc-research-summarise"` replaced by `name: "sdlc-research-brief"`, and the cloned blob's SHA is explicitly not equal to the source blob's SHA. Pinned the exact rewritten lines in "Frontmatter name rewritten and everything else preserved". |
| Artifact `story_map` did not change since precheck, while the reviewer feedback was active | `story-map.json`'s `BSB-41-PENDING-1` summary was updated to describe the revised story precisely — it now states the copy-every-file/rewrite-only-the-name behaviour — and the matching `**Title:**` line in `stories.md` was aligned with that summary. Story 2 and the requirement mappings are unchanged; requirement coverage and story keys are unchanged. |

### Still open

- None. Both reported findings were applied without needing a gate answer.

### New problems noticed

- None. Requirement coverage is unchanged (FR-011, FR-012, FR-013, FR-014, FR-124, FR-125 and
  FR-126 are all still covered by at least one story), so `story-map.json`'s `requirement_ids`
  arrays are unchanged.

### Known input caveat (re-checked this pass)

The Atlassian MCP server configured in `.mcp.json` was reached over stdio in this pass. A
`jira_get_issue` call for `SkillBuilder-2` is rejected by the MCP server's issue-key schema
(`^[A-Z][A-Z0-9_]+-\d+(?:-\d+)*$`), and a `jira_search` JQL text search for `SkillBuilder-2`
returns zero issues; `BSB-41` was fetched successfully and is the epic used here. This supersedes
Pass 1's note that the MCP server was not reachable, and matches the 404 recorded in
`docs/product/PRD.md` §8 and `docs/product/epics.md`.
