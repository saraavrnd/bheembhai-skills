# Revisions — BSB-23 (Integrations, credentials & MCP definitions)

## Pass 1 — 2026-11-17 (epic-review returned changes_requested)

**Report applied:** `docs/product/epics/BSB-23/_epic/epic-review.md`, verdict CHANGES REQUESTED
(2026-11-16), authored by the `sdlc-plan-epic-review` step of run
`693d7422-18b0-42f9-b7e9-9d4ef928a836` (commit `59b758c`). The hand-off carried no gate answers, so
the report's **Open questions** were answered inside this epic by applying the report's own
**Proposed changes** and recording every choice under **Choices recorded** below. No finding was
left unapplied: each proposed change either states the remedy directly or names a recommended
direction that is applyable within `stories.md` without changing the epic, the PRD, ADR SK-001 or
the story set. Where the report offered two branches, the chosen branch is recorded so a person can
override it in a later pass.

**Work item `SkillBuilder-2` / epic lookup.** The Atlassian MCP tools were not exposed in this
session (no `mcp__atlassian__*` tool and no MCP server connection), so the configured site was
queried read-only over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2`
returned HTTP 404 with `"Issue does not exist or you do not have permission to see it."`, matching
`PRD.md` section 8 and the review's Context loaded; no issue content is assumed from that lookup.
The run's epic `BSB-23` was read read-only from the same site and returned HTTP 200: summary
"Integrations, credentials & MCP definitions", type Epic, status To Do, labels `FA-5`/`MVP`, no
parent, no sub-tasks and no issue links, with a description matching the BSB-23 section of
`epics.md`. That epic is the subject of this pass.

### Findings applied

| Finding | Severity | Stories touched | Change applied |
|---|---|---|---|
| 1 — verification proves credential validity, not target reachability | Blocking | BSB-23-PENDING-1, -2, -3, -4 | PENDING-4 now defines one agreed meaning of "verified": the credential is accepted **and** the stored target is usable. The Jira path calls `/rest/api/3/myself` then `/rest/api/3/project/<stored project_key or template_project>`; the source-control path calls `/user`, `/repos/<stored repository>` (asserting `permissions.push` is true) then `/repos/<repository>/branches/<stored base_branch>`; the model path calls `/v1/models` and requires every identifier in the stored `models` mapping to appear in `data[].id`. The three success scenarios now stub and assert those calls; three new unhappy-path scenarios cover an inaccessible Jira project, a token without push access, and a missing model identifier. PENDING-1/-2/-3 each state the exact stored target fields verification reads. |
| 2 — test-purpose attestation enforced on create but not on edit | Blocking | BSB-23-PENDING-1, -4, -5, -6 | PENDING-6 now owns "every integration save — every create and every edit": an unconfirmed save is refused with HTTP 422 "Runs require test-purpose credentials." before any row or secret change, a confirmed create records `config.test_only true`, and a confirmed edit keeps it true. A new scenario rejects a non-blank-token edit with no confirmation and asserts the row, the secret and `verified_at` are unchanged. PENDING-1's edit contract, PENDING-4's target-change scenario and PENDING-5's edit scenario and Notes all require the confirmation and assert `test_only true`. |
| 3 — shared create route and create form have no single owner | Blocking | BSB-23-PENDING-1, -2, -3, -6 | PENDING-1 now owns the shared `POST /projects/7/integrations` route skeleton with one documented order — owner check, test-purpose confirmation, non-secret MCP validation, kind dispatch — and the `GET /projects/7/integrations/new` form (new happy-path and non-owner scenarios). PENDING-2 and PENDING-3 add the `github` and `ai_model` kind branches and field sets to that route and form, not a second route or page. PENDING-6 states the confirmation is a shared pre-dispatch step called by PENDING-1's create and edit routes, not a separate route. |
| 4 — Jira edit route exercised by two stories but owned by none | Blocking | BSB-23-PENDING-1, -2, -4, -5 | PENDING-1 now owns the Jira edit route `POST /projects/7/integrations/3` with the full contract: a blank token preserves `secret_ref` and the secret; a non-blank token replaces the secret and clears `verified_at`; a site URL or target change clears `verified_at`; an unchanged edit keeps it; an omitted MCP definition preserves `integrations.mcp`; a submitted one replaces it after the non-secret rule; every edit needs the confirmation. PENDING-4 and PENDING-5 reference PENDING-1's edit route, and PENDING-5's edit scenario now also asserts the MCP definition and `test_only` survive. PENDING-2 states source-control editing is out of scope for this epic. |
| 5 — run-purpose list contract underspecified for BSB-24 | Advisory | BSB-23-PENDING-1, -2, -3, -4, -6 | PENDING-6 now defines the item shape for all three kinds (`jira`: id, kind, site_url, project_key or template_project, verified_at; `github`: id, kind, repository, base_branch, verified_at; `ai_model`: id, kind, name, verified_at), states the list is in id order, open to any project member, and returns `verified_at` as an advisory marker rather than a selection filter. The exclusion scenario remains, a new scenario returns all three kinds with their target fields, and new scenarios cover member access (200) and non-member denial (403). PENDING-1/-2/-3 state the fields their kind exposes; PENDING-4 states `verified_at NULL` is still offered to runs. The dependency sentence now says BSB-24 consumes the endpoint as a supplied contract, not a prerequisite. |
| 6 — redaction helper contract one-sided and incomplete | Advisory | BSB-23-PENDING-1, -4, -5 | PENDING-5 now defines the helper's input — the text or document, the project id and the run's selected integration ids — and output — the same text with every occurrence of each resolved value replaced by `"[REDACTED]"`, never redacting `secret_ref`. The helper resolves credentials from the secret store at call time, so no value is stored or passed through a durable record. BSB-26 calls it before persisting; BSB-33 calls it for any text it renders that did not pass through the writer. PENDING-1 owns the save-path `secret_ref=` log line and PENDING-4 owns the verify-path line, and PENDING-5's log scenario exercises both. |
| 7 — MCP definitions recorded but no story owns delivering them to a run | Advisory | BSB-23-PENDING-1, -2 | PENDING-1 and PENDING-2 now name the consumer and the side of the boundary: BSB-24 records the selected integration id in the run request, and BSB-26 builds `BB_MCP_CONFIG` from the row's `integrations.mcp` value when it launches the run container; this epic records the definition only. |

### Choices recorded (no gate answer supplied)

1. **Verification depth (Finding 1 / Open question 1).** Target reachability was chosen over
   credential-only validity. The epic DoD says "a verified integration is usable by runs"
   (`epics.md` BSB-23), and this skill may not rewrite the epic or the PRD to withdraw that
   promise; adding the target checks keeps the stories aligned with the DoD and with PENDING-4's
   "so that" clause. If a person chooses credential-only verification, revert the target calls in
   PENDING-4's three success scenarios and the three target-failure scenarios, reword PENDING-4's
   story value, and move target reachability to BSB-24 — and change the epic DoD separately, which
   is outside this skill's authority.
2. **Edit scope and ownership (Finding 4 / Open question 2).** Editing a Jira integration is in
   scope and owned by BSB-23-PENDING-1. Editing a source-control integration is explicitly out of
   scope for this epic (stated in PENDING-2's Notes and Out of scope), matching PENDING-3's
   existing exclusion for model profiles. The chosen split gives every kind a stated boundary
   without adding a second edit route to the epic.
3. **Test-purpose re-attestation (Finding 2 / Open question 3).** The confirmation is required on
   every save — every create and every edit — not only credential-changing edits, matching
   `story-map.json`'s existing "every integration save" wording. An unconfirmed edit is refused
   with HTTP 422 "Runs require test-purpose credentials." and changes neither the row nor the
   secret store; `test_only` is never cleared by an edit. If a person prefers re-attestation only
   on credential-changing edits, narrow PENDING-6's new edit scenario and PENDING-1's contract
   accordingly and add the credential-change predicate.
4. **Create route and form ownership (Finding 3 / Open question 4).** BSB-23-PENDING-1 owns the
   shared `POST /projects/7/integrations` route and the `GET /projects/7/integrations/new` form;
   PENDING-2/-3 own kind branches and field sets; PENDING-6's confirmation is a pre-dispatch step.
   The cross-epic half — BSB-22-PENDING-4's own assertion on that route and BSB-22's Open
   question 2 — is not applied here (see **Still open**).
5. **Run-purpose list contract (Finding 5 / Open question 5).** The list returns all three kinds
   with the target fields named above, is readable by any project member, and treats `verified_at`
   as an advisory marker (unverified rows are returned with `null`). If verification should gate
   selection, add the `verified_at IS NOT NULL` condition to PENDING-6's filter and update the
   list scenario, PENDING-4's Notes and BSB-24.
6. **Redaction helper input (Finding 6 / Open question 6).** The helper resolves the selected
   credentials from the secret store itself, given the project id and the run's selected
   integration ids, rather than receiving resolved values from its caller. This lets both BSB-26's
   writer and BSB-33's report call it without storing or forwarding a credential value. The
   save-path `secret_ref=` log line belongs to PENDING-1 and the verify-path line to PENDING-4;
   PENDING-5 owns the redaction rule they apply.
7. **MCP delivery owner (Finding 7 / Open question 7).** BSB-26 builds `BB_MCP_CONFIG` from
   `integrations.mcp` when it launches the run container; BSB-24 records the selected integration
   ids in the run request. BSB-24, BSB-25 and BSB-26 do not need a BSB-23 revision for this, but
   their own story passes must read this contract (see **Still open**).

### Still open (cross-epic follow-ups, not applied in this pass)

These are outside `docs/product/epics/BSB-23/_epic/`; this skill may not edit another epic's
stories or the epic/PRD text.

1. **BSB-22 — route ownership.** BSB-22's Open question 2 remains unanswered and
   BSB-22-PENDING-4 still asserts a denial on `POST /projects/7/integrations`, which
   BSB-23-PENDING-1 now owns. BSB-22's next revision must align that scenario: either it calls
   BSB-23-PENDING-1's route and keeps only the guard assertion, or BSB-22 keeps a minimal guarded
   route that PENDING-1 extends. Its "Add integration" link and `/projects/7/integrations/new`
   contract are unchanged.
2. **BSB-24 — run-purpose consumer.** Its stories must read
   `GET /api/projects/7/integrations?purpose=run`, apply the same project-membership check, name
   the `test_only` filter they rely on, record the selected Jira and source-control integration ids
   in the run request, and not treat `verified_at` as a gate.
3. **BSB-25 / BSB-26 — MCP env.** BSB-26 must build `BB_MCP_CONFIG` from the selected
   integrations' `integrations.mcp` values at container launch (BSB-25 only pins the bundle,
   output branch and baseline); its Notes should say so.
4. **BSB-26 / BSB-33 — redaction helper.** BSB-26's result writer must call the BSB-23 redaction
   helper before persisting a result document, and BSB-33 must call it for any text it renders
   that did not pass through the writer; both epics' Notes should name the dependency.
5. **Rejection of any recorded choice.** Choices 1-7 above each name the exact story sections to
   change if a person decides the other branch. No unresolved question blocks building the six
   stories as revised.

### Coverage re-check

Unchanged and complete. BSB-23 still has 6 stories covering all 12 requirements mapped to it in
`epic-map.json` — PENDING-1 (FR-029, FR-128), PENDING-2 (FR-030, FR-129, FR-035), PENDING-3
(FR-031), PENDING-4 (FR-033, FR-034), PENDING-5 (FR-032, FR-036, NFR-004) and PENDING-6
(NFR-006) — with no foreign requirement and no duplicate claim. No story key, title, story
statement, estimate or requirement mapping changed. `story-map.json` changed only the summary
strings for PENDING-1, PENDING-2, PENDING-3, PENDING-4 and PENDING-5 so they match their revised
contracts; PENDING-6's summary already said "every integration save" and was left unchanged.

### Notes for the next review

- **Only this epic's story files changed:** `stories.md`, `story-map.json` and this
  `revisions.md`. Nothing outside `docs/product/epics/BSB-23/_epic/` was touched, and no Jira
  write was made (authoring only, per ADR-035).
- **Scenario counts:** PENDING-1 now has 9 (two added: create form and non-owner form denial);
  PENDING-2 has 7 (unchanged); PENDING-3 has 6 (unchanged); PENDING-4 has 10 (three added for the
  target-reachability failures); PENDING-5 has 6 (unchanged); PENDING-6 has 7 (three added: edit
  re-attestation, every-kind item shape and non-member denial; the original exclusion scenario is
  kept and the member-access case is its own scenario). No scenario was removed and no existing
  assertion was weakened.
- **Story size:** PENDING-4 and PENDING-1 exceed the skill's ~5-7 scenario guideline because the
  review fixes the story set and requires the target checks and route ownership to be asserted in
  these stories. Splitting them would change the story set and `story-map.json`, which the report
  explicitly does not propose; a later epic-level pass may split them if it prefers.
- **Next pass:** `sdlc-plan-epic-review` re-runs on the revised set. If it returns
  changes_requested, the next revise pass applies the new report the same way.
