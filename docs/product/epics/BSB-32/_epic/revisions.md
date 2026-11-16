# Revisions — BSB-32 (LLM security scanning)

## Pass 1 — 2026-11-16 (automated verifier feedback)

**Report applied:** the step hand-off feedback for this run of `sdlc-plan-stories-write`. No
`epic-review.md` or `story-review.md` report existed on disk for BSB-32; the failing verifier
check below is applied as a revise pass.

**Work item `SkillBuilder-2`.** The Atlassian MCP tools are not exposed in this session, so the
configured site was queried read-only through its REST API (`GET /rest/api/3/issue/SkillBuilder-2`);
it returned HTTP 404 "Issue does not exist or you do not have permission to see it." This matches
`docs/product/PRD.md` section 8 and no issue content is assumed from the lookup. The epic being
decomposed was read read-only from the same site: `BSB-32` returned HTTP 200, summary "LLM security
scanning", status To Do, labels FA-12/MVP, no parent and no sub-tasks. No Jira write was attempted.

### Finding applied

- **Judge criterion `vertical_slices` — the seven-story set was a mixture of technical layers and
  three user-facing slices.** The old PENDING-2 was sandbox/environment/egress configuration with no
  user-visible surface, PENDING-3 owned "the full security scan service and route" and was the
  backend of the control PENDING-6 already exposed, PENDING-4 persisted unavailable and
  `failure_reason` rows while rendering was deferred to PENDING-5, and PENDING-7 was a proof story
  that added "no run-start behaviour of its own". The seven layers are replaced by four vertical
  journeys, each of which starts at a page the author or owner can open and ends at a page or state
  they can see:

  - **BSB-32-PENDING-1 — "Configure the LLM-scan model profile for a test project."** Retained
    essentially unchanged: the project owner sets the profile and tier on the project settings page
    at GET "/projects/7/settings", and the page renders the selection. Covers FR-163.
  - **BSB-32-PENDING-2 — "Run a full security check from the skill page and read the LLM report."**
    Absorbs the old PENDING-3 (static-before-LLM trigger and the full-scan route), PENDING-5 (the
    author report page with the model, advisory banner and located findings) and PENDING-6 (the
    "Full security check" control, project selector, membership refusal and per-scan override
    refusal), and adds the old PENDING-7's findings-do-not-block path as the journey's payoff. It
    begins at the build page control and ends at GET "/scans/12" and the run's verdict page. Covers
    FR-082, FR-085, FR-086, FR-090, FR-093, FR-156 and FR-163 (consumption).
  - **BSB-32-PENDING-3 — "Scan untrusted skill content without exposing project credentials or
    other services."** Absorbs the old PENDING-2, but is no longer a sandbox-configuration story:
    the journey starts with the author running a full check on a hostile bundle from the build page
    and ends at the rendered report, with the credential-absence, egress-allowlist and
    exact-bundle assertions as acceptance criteria inside that journey. Covers FR-083 and FR-084.
  - **BSB-32-PENDING-4 — "See why the LLM scan could not run and keep working."** Absorbs the old
    PENDING-4 and the old PENDING-7's unavailable and failed paths, and owns the rendering that was
    previously deferred to PENDING-5: each unavailable or failed reason is read on the same author
    report page, and the author then starts and finishes a run whose verdict is unaffected. Covers
    FR-139 and FR-085.
  - Old draft keys BSB-32-PENDING-5, -6 and -7 are removed. They were never published to Jira
    (`sdlc-tracker-sync` had not run), so no real issue key is orphaned. All ten requirement
    mappings are preserved; see the coverage re-check below.

### Coverage re-check

Every requirement mapped to BSB-32 in `epic-map.json` — FR-082, FR-083, FR-084, FR-085, FR-086,
FR-090, FR-093, FR-139, FR-156 and FR-163 — appears in at least one story's `requirement_ids`, and
no story claims a requirement outside the epic. 4 stories, 10 requirements, no gap and no foreign
requirement. FR-163 is configured by PENDING-1 and consumed by PENDING-2; FR-085 is exercised on
both the findings path (PENDING-2) and the unavailable/failed path (PENDING-4). The
`stories.md` coverage table records the acceptance criteria that cover each requirement.

### Still open

None.

### Notes for the next review

- **Story set reduced, coverage unchanged.** 4 vertical stories now replace the previous 7. Every
  story's acceptance criteria remain concrete enough to test directly, and each ends on a rendered
  page or page state rather than only a database row or network observation.
- **Cross-epic dependencies unchanged.** Run start/page and verification are BSB-24, BSB-26 and
  BSB-29; the static scan records and report route are BSB-31; project membership and the settings
  page are BSB-22; the model profile is BSB-23. The stories name these hand-offs in Notes rather
  than claiming their behaviour.
