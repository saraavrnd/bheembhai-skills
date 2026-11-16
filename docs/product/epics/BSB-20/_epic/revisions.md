# Revisions — BSB-20 (Skill cloning & edit builds)

## Pass 1 — 2026-11-16 (epic-review returned changes_requested)

**Report applied:** `docs/product/epics/BSB-20/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), handed back from the `sdlc-plan-epic-review` step. The hand-off carried no gate
answers to the report's **Open questions** (1–6). Per Step R of `sdlc-plan-stories-write`, a finding
whose question has no answer yet is not applied — guessing a product or architecture decision is
outside this skill's authority. All six findings therefore remain open and no story content changed
in this pass.

**Work item `SkillBuilder-2`.** The Atlassian MCP tools were not exposed in this session, so the
configured site was queried read-only over its REST API. `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 "Issue does not exist or you do not have permission to see it"; this matches
`docs/product/PRD.md` section 8 and no issue content is assumed from the lookup. The run's epic was
read read-only from the same site: `BSB-20` returned HTTP 200 with summary "Skill cloning & edit
builds", type Epic, status To Do, labels `FA-2`/`MVP`, no sub-tasks, and a description matching the
BSB-20 section of `epics.md`. No Jira write was attempted.

### Findings applied

None. Every finding in the report carries a question a person must answer, and the hand-off
supplied no answers. A partial application would still require choosing the unanswered option, so
no finding was applied in part either.

| Finding | Severity | Stories touched | Open question (abridged) | Change applied |
|---|---|---|---|---|
| 1 — catalog-manifest consistency | Blocking | BSB-20-PENDING-1 (cross-epic BSB-19-PENDING-2) | Rewrite `verify.yaml`'s `skill` value on clone, or keep the copied manifest byte-identical and change the catalog check? | None |
| 2 — shared endpoint contract | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-1) | Which story owns the single `GET /builds/new` + `POST /builds` handler, and what is the exact mode carrier, default and per-mode request fields? | None |
| 3 — build-record contract | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-2, BSB-21) | Is `head_sha` the clone commit / `base_sha`, or deliberately NULL until BSB-21's first save? | None |
| 4 — branch lifecycle | Blocking | BSB-20-PENDING-1, BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-1, BSB-19-PENDING-3, BSB-36) | After a build is merged or abandoned, is `build/<skill-name>` reused, deleted first, or uniquely named — and which epic/story owns that lifecycle? | None |
| 5 — FR-125 proof location | Advisory | BSB-20-PENDING-2 (cross-epic BSB-21) | Move FR-125's verification to BSB-21's save story, or keep it in BSB-20-PENDING-2 with an AC asserting the resolved target folder? | None |
| 6 — reciprocal BSB-19 notes | Advisory | BSB-20-PENDING-2 (cross-epic BSB-19-PENDING-1, BSB-19-PENDING-3) | Do BSB-19's stories name the edit flow explicitly, or does BSB-20 own the edit-specific inverted existence check? | None |

### Still open (no gate answer supplied)

1. **Finding 1 — manifest rewrite (Blocking; BSB-20-PENDING-1).** Should the clone rewrite both
   name-bearing manifest fields (`SKILL.md` frontmatter `name` and `verify.yaml` top-level `skill`),
   with the catalog's `python tools/check.py` asserted to exit 0, or is a source-identical
   `verify.yaml` intended and the catalog check changed? The report notes this may also need
   `PRD.md` FR-013 and the BSB-20 epic description clarified if "frontmatter" does not cover
   `verify.yaml`.
2. **Finding 2 — shared handler and mode (Blocking; BSB-20-PENDING-1, BSB-20-PENDING-2).** Should
   BSB-19-PENDING-1 own the single `GET /builds/new` + `POST /builds` handler, with BSB-20 extending
   it for `clone` and `edit`? What is the exact mode carrier (query parameter, form field or path),
   its default value, and the request fields each mode accepts? The report's proposed change names
   the allowed values (`create`, `clone`, `edit`) and the default but not the carrier.
3. **Finding 3 — build head and clone base (Blocking; BSB-20-PENDING-1, BSB-20-PENDING-2).** Should
   the clone record `head_sha` = the clone commit (whose parent is `base_sha`, with the source tree
   read at `base_sha`) and the edit build record `head_sha` = `base_sha`, or is `head_sha`
   deliberately NULL until BSB-21's first save?
4. **Finding 4 — branch lifecycle (Blocking; BSB-20-PENDING-1, BSB-20-PENDING-2).** When a prior
   build for the same skill is merged or abandoned, should the builder reuse the existing
   `build/<skill-name>` branch, delete it first, or give each build a unique branch name? Which
   epic/story owns that lifecycle? The report assigns no owner, so the story notes cannot state the
   rule without this answer.
5. **Finding 5 — FR-125 proof location (Advisory; BSB-20-PENDING-2).** Should FR-125's verification
   move to BSB-21's save story, or stay in BSB-20-PENDING-2 with an AC that asserts the edit build
   resolves the existing `skills/<skill-name>/` target and creates no second folder?
6. **Finding 6 — reciprocal BSB-19 notes (Advisory; BSB-20-PENDING-2).** Should BSB-19-PENDING-1 and
   BSB-19-PENDING-3 name the edit flow explicitly, or does BSB-20 own the edit-specific inverted
   existence check? The report offers two alternatives for how the shared validator carries it (a
   mode parameter, or reuse of only the pattern and collision parts).

### Coverage re-check

Unchanged. BSB-20 still has 2 stories — BSB-20-PENDING-1 (FR-011, FR-012, FR-013, FR-014) and
BSB-20-PENDING-2 (FR-124, FR-125, FR-126) — covering all 7 requirements mapped to BSB-20 in
`epic-map.json`, with no foreign requirement. `stories.md` and `story-map.json` are unchanged; no
story key, title, statement, acceptance criterion or requirement ID changed. The report's proposed
`story-map.json` summary edit belongs to Finding 1 and is not applied while that question is open.

### Notes for the next review

- **Blocking findings 1–4 remain unresolved and need gate answers.** Findings 1 and 4 in particular
  turn on decisions the report itself routes to a person or an earlier stage: the clone-rewrite
  scope versus `tools/check.py` and `PRD.md`/`epics.md` wording (Finding 1), and the
  `build/<skill-name>` branch lifecycle and its owner after a build is merged or abandoned
  (Finding 4). Findings 2, 3, 5 and 6 also name the choice to make but state the answer is not yet
  fixed.
- **Nothing outside this epic's story files was touched.** The report's cross-epic follow-ups
  (BSB-19-PENDING-1/-3 and the BSB-19 epic note, BSB-21's save story, BSB-36's lifecycle scope,
  `PRD.md` FR-013 / BSB-20 epic wording) are not applied here; they belong to those epics' own
  revision passes or a human decision.
- **No Jira write was made.** Authoring only, per ADR-035; publication remains
  `sdlc-tracker-sync`'s job after a clean review.
- **Next pass:** once the gate answers for Findings 1–6 are supplied, apply them to the named
  stories in the shape Step 3 produces, then update `story-map.json` only if coverage changes.
