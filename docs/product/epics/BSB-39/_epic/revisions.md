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
