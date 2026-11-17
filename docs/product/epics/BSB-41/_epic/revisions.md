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
