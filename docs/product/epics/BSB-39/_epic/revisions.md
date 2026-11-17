# Revisions — BSB-39 stories

## Pass 1 — 2026-11-17

**Report applied:** automated verifier rejection of run `aa60baa1-b35f-428f-bbf9-2b2d9cf3ae8e`
(step `sdlc-plan-stories-write`). No separate `epic-review.md` or `story-review.md` was present;
the reviewer feedback supplied the failing checks. No open questions were attached, so every
finding was actionable.

### Finding → change

| Finding | Change |
|---------|--------|
| `story_map` artifact unchanged since precheck | Updated `story-map.json` summaries for stories 2, 4, 5 and 6 to match their retitled, revised scope; requirement traceability is unchanged and still covers all 11 epic requirements. |
| `scenario_executable` — sign-in scenario named no account/subject/credential values and gave only a qualitative "authenticated session" outcome | Story 1 now pins the fixture account (`alice@example.test` / `Alice-Passw0rd!` / `sub-12345`), the exact `POST /sign-in` request, HTTP 302, `Location: /builds` and the `builder_session` cookie attributes, plus exact 401/503 failure statuses and messages. A fixed fixture table at the top of `stories.md` defines every account, subject, display name and group claim used across the set; all other scenarios were tightened to exact status codes, JSON bodies and messages. |
| `unhappy_paths` — BSB-39-PENDING-6 had no invalid-input/permission/empty-state scenario | Story 6 now rejects unsafe platform-database configuration at startup (including a DSN hidden behind a secret reference) with an exact error message, and covers the empty state where the identity provider supplies no display-name claim. |
| `vertical_slices` — BSB-39-PENDING-5 was a persistence-layer story and BSB-39-PENDING-6 a pure architectural constraint | Story 5 is retitled "Keep one authoring identity across sign-ins" and its acceptance criteria now assert the author-visible identity through `GET /api/me` (stable `user_id`, subject, display name and groups across browsers and accounts) rather than row counts alone; the durable `users` row remains only where the uniqueness invariant itself is under test. Story 6 is retitled "Refuse to run with platform database access" and is rewritten around administrator-visible outcomes — process exit status, exact stderr message, and `/healthz` reporting only the builder data source — instead of connection-log, configuration and dependency-list inspections as the end goal. Story 2 keeps its client-observable 302/401 outcomes and now enumerates the concrete guarded routes. |

### Still open

- None. All findings in this pass were applied without needing a gate answer.

### Known input caveat (carried from the PRD, not a finding)

The Jira work item `SkillBuilder-2` could not be retrieved from the configured Atlassian site
(direct fetch returns 404; `SkillBuilder` is not a project key there). This is already recorded in
`docs/product/PRD.md` §8 and `docs/product/epics.md`. The stories remain grounded in the epic
BSB-39 section, `epic-map.json` and the PRD requirement wording.

## Pass 2 — 2026-11-17

**Report applied:** `docs/product/epics/BSB-39/_epic/epic-review.md` (verdict **CHANGES
REQUESTED**, run `aa60baa1-b35f-428f-bbf9-2b2d9cf3ae8e`, step `sdlc-plan-epic-review`). The run
hand-off carried no answers to the report's four open questions, so only the findings that need no
product decision were applied; the decision-bearing findings remain open.

### Finding → change

| Finding | Change |
|---------|--------|
| 5 — membership guard proven on only two routes | **Applied.** `BSB-39-PENDING-3` gains a "Membership guard covers every authoring route" scenario that mirrors `BSB-39-PENDING-2`'s route list (`GET /builds`, `GET /builds/new`, `GET /api/builds`, `POST /api/builds`, `GET /api/me`), asserting HTTP 403 with body exactly `{"error":"membership_required"}` and no build data on each, plus the "routes added by later epics" note. `BSB-39-PENDING-2`'s Notes now state that its route list is the canonical guarded-route set for both the authentication and membership guards. |
| 6 — one-sided dependency notes and unnamed cross-epic owner | **Applied.** `BSB-39-PENDING-1` Notes now name `BSB-39-PENDING-2` and `BSB-39-PENDING-3` as dependents on the session it issues. `BSB-39-PENDING-3` Notes now record its dependency on `BSB-39-PENDING-1`'s sign-in flow and that `BSB-39-PENDING-5` depends on its member gate. `BSB-39-PENDING-4`'s Out of scope now names `BSB-49 (Run guardrails & re-runs)` instead of "the run guardrail epic". `BSB-39-PENDING-2` and `BSB-39-PENDING-5` needed no change (their existing notes were already correct; the reciprocal half is now in the other story). |

### Still open

The following findings each pose a question that no one has answered, so applying them would mean
guessing. They are not applied and must be settled at a gate before the next revision pass.

- **Finding 1 — sign-in mechanism (blocking).** No answer to Open question 1: builder-hosted
  `POST /sign-in` form vs. Cognito hosted-UI authorization-code redirect through `/auth/callback`.
  Stories 1, 2, 3 and 5 still describe the two incompatible mechanisms and are mutually
  unsatisfiable until one is chosen.
- **Finding 2 — `/builds` ownership.** No answer to Open question 2: does BSB-39 own a minimal
  identity-only `/builds` landing page and placeholder routes, or do its stories depend on BSB-40?
  The stories preface still names `/builds` without an owner.
- **Finding 3 — session lifetime and membership freshness.** No answer to Open question 3: token
  claim checked per request (SK-001 §3) vs. a separate ≤1-hour membership-decision cache; and the
  mid-edit expiry behaviour (redirect with return path vs. 401/403). Story 1 still gives the
  session no lifetime/expiry attributes, and Stories 3 and 4 still describe the freshness model
  differently.
- **Finding 4 — page identity and denial contract.** No answer to Open question 4: display name
  only (with `Unknown name` fallback) vs. raw subject/groups on `/builds`, and HTML 403 page vs.
  JSON body for browser-facing denials. Stories 1, 3 and 6 still assert three different identity
  contracts; Stories 3 and 4 still assert different denial bodies. The new Finding 5 scenario
  intentionally mirrors the existing `{"error":"membership_required"}` body for all routes, so it
  will need the same contract decision when Finding 4 is resolved.

### New problems noticed

- None beyond the four open questions above. Coverage is unchanged: all 11 BSB-39 requirements
  remain covered, so `story-map.json` needs no update.

### Known input caveat (re-checked this pass)

`SkillBuilder-2` is still unavailable: a direct Atlassian REST fetch returns HTTP 404 ("Issue does
not exist or you do not have permission to see it") and the site's project list contains BEEM, BSB,
EX, GRAP and LNPRTL with no `SkillBuilder` project. This pass therefore revises the BSB-39 story set
on disk, as the epic review directed.
