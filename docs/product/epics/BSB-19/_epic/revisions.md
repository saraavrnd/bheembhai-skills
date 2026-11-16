# Revisions — BSB-19 (Skill build creation & scaffolding)

## Pass 1 — 2026-11-16 (automated verifier feedback)

**Report applied:** the step hand-off feedback for this run of `sdlc-plan-stories-write`. No
`epic-review.md` or `story-review.md` report existed on disk for BSB-19; the failing verifier check
below is applied as a revise pass.

### Findings applied

- **`no_template_residue` — BSB-19-PENDING-1, Notes / dependencies (line 62).** The prose carried
  the placeholder `build/<skill-name>`. Replaced it with the concrete naming rule: the branch name
  is the literal prefix "build/" followed by the skill name, so skill "sdlc-plan-new-skill" gets
  branch "build/sdlc-plan-new-skill". No acceptance criterion, covered requirement, story key or
  story-map entry changed.
- **`no_template_residue`, same check swept across the file — BSB-19-PENDING-3, Notes /
  dependencies.** The `sdlc-<area>-<action>` notation was the file's only other angle-bracket
  placeholder. Rewrote it as prose — a literal "sdlc-" prefix, then an area segment and an action
  segment, all lowercase letters, digits and hyphens, with at least three hyphen-separated
  segments — so no placeholder-shaped token remains. The rule's meaning is unchanged.

### Still open

None.

### Notes for the next review

- **Work item `SkillBuilder-2`.** Re-checked against the configured Atlassian site and it remains
  unavailable: no project named `SkillBuilder` is visible (visible projects: BEEM, BSB, EX, GRAP,
  LNPRTL) and no `SkillBuilder-2` issue exists. This is already recorded in `docs/product/PRD.md`
  section 8 and does not change this epic's scope, which is fixed by `epic-map.json`.
- **Story set unchanged.** Still 3 stories; coverage of all 10 BSB-19 requirements (FR-006,
  FR-007, FR-008, FR-009, FR-010, FR-015, FR-016, FR-017, FR-143, FR-144) is complete.

## Pass 2 — 2026-11-16 (automated verifier feedback, second attempt)

**Report applied:** the step hand-off feedback for this retry of run
`d0e8e526-b74e-42e6-9194-5e0c0f30bc2f`: `artifact 'story_map': artifact did not change since
precheck: docs/product/epics/BSB-19/_epic/story-map.json (reviewer feedback is active)`. No
`epic-review.md` or `story-review.md` report exists on disk for BSB-19, so this is the finding
applied.

### Findings applied

- **`story_map` — BSB-19-PENDING-1 summary.** Replaced "Create a build and cut its branch from the
  head of main" with "Create a build from a skill name and one-line description and cut its branch
  from the current head of main". The old summary omitted FR-006's one-line description and did not
  name the source of the base SHA; the new one does. `requirement_ids` unchanged: FR-006, FR-007.
- **`story_map` — BSB-19-PENDING-2 summary.** Replaced "Scaffold a catalog-shaped skill folder on
  the build branch" with a summary that names the `SKILL.md` frontmatter, the `verify.yaml` stub and
  the standard references, templates and examples folders. The old summary did not show why FR-009,
  FR-143 and FR-144 are covered by this story; the new one does. `requirement_ids` unchanged:
  FR-008, FR-009, FR-010, FR-143, FR-144.
- **`story_map` — BSB-19-PENDING-3 summary.** Replaced "Reject invalid and duplicate skill names
  before creating a build" with "Reject malformed, duplicate-on-main and open-build skill names
  before creating a build", matching the three distinct rejection causes FR-017, FR-015 and FR-016
  that the story's scenarios exercise. `requirement_ids` unchanged: FR-015, FR-016, FR-017.

The summaries are the only change: no story statement, acceptance criterion, requirement ID,
coverage summary, story title or draft key changed, and `stories.md` is the Pass 1 revision
unchanged.

### Coverage re-check

Every requirement mapped to BSB-19 in `epic-map.json` — FR-006, FR-007, FR-008, FR-009, FR-010,
FR-015, FR-016, FR-017, FR-143, FR-144 — still appears in exactly one story's `requirement_ids`,
and no story claims a requirement outside the epic. 3 stories, 10 requirements, no gap.

### Still open

None.

### Notes for the next review

- **Work item `SkillBuilder-2`.** Re-queried the configured Atlassian site (`GET
  /rest/api/3/issue/SkillBuilder-2`) and it still returns HTTP 404 "Issue does not exist or you do
  not have permission to see it." The MCP tools are not exposed in this session, so the read-only
  REST call was used; no Jira write was attempted. This matches `docs/product/PRD.md` section 8 and
  does not change BSB-19's scope.
- **Story set unchanged.** Still 3 stories with the same coverage; only the three `story_map`
  summaries changed in this pass.
