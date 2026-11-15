# Revisions — BSB-18

## Pass 1 — 2026-11-15 — verifier check `scenario_executable`

**Report applied:** automated verifier rejection of the previous `sdlc-plan-stories-write` attempt
for epic BSB-18 (judge criterion `scenario_executable`).

**Finding:** the scenario *Expired session is treated as unauthenticated* gave only the path
(`/builds`), the 302 status and the 1-minute expiry. It did not give a concrete sign-in URL, did not
name the session cookie, did not specify the session format, and did not state what the
`Set-Cookie` header must contain when clearing the expired cookie.

**What changed:**

- Added a **Session and identity contract** section at the top of `stories.md` that fixes the
  builder public URL, the Cognito hosted-UI domain and app client id, the exact sign-in redirect
  target (`Location`), the token endpoint, the issuer, the session cookie name (`sb_session`), its
  format (a Cognito ID token JWT with named required claims), its success attribute set, and the
  exact expired-session clearing header.
- `BSB-18-PENDING-1` — *Expired session is treated as unauthenticated* now names the cookie, the
  token format and claims, the exact `exp` and current time, the exact sign-in `Location`, the exact
  clearing `Set-Cookie` header (`Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT`) and a 0-byte
  body. The other three scenarios in this story now assert the same exact `Location` value, exact
  API error body, and 0-byte/no-`Set-Cookie` responses.
- `BSB-18-PENDING-2` — every sign-in scenario now names the callback URL, the token endpoint, the
  exact ID-token claims, the exact `sb_session` cookie attributes on success, the exact redirect
  target, and the exact rejection text plus the `users` row count for rejected identities.
- `BSB-18-PENDING-3` — membership scenarios now carry exact token claims, issuer, audience and
  `exp` values; the one-hour removal bound is split into a valid-token case (HTTP 200 at
  `10:59:59Z`) and an expiry case (HTTP 302 with the exact clearing header at `11:00:00Z`), plus a
  re-authentication rejection case.
- `BSB-18-PENDING-4` — each upsert scenario now states the exact `cognito_sub`, the SQL count it
  must observe, the exact stored `email`/`name` values, and the exact displayed identity text.

**Coverage:** unchanged. All 10 requirements mapped to BSB-18 are still covered by the same four
stories; `story-map.json` is unchanged.

**Still open:** none.

## Pass 2 — 2026-11-15 — verifier checks `gherkin_parses` and story-map artifact change

**Report applied:** automated verifier rejection of the previous `sdlc-plan-stories-write` attempt
for epic BSB-18. Two checks failed:

1. `gherkin_parses` — scenario *Authoring page refuses an unauthenticated visitor* had no Given
   step.
2. artifact `story_map` — `story-map.json` did not change since precheck while reviewer feedback
   was active.

**Root cause of finding 1:** the criterion lines were written as Markdown bullets (`- Given …`,
`- When …`). The acceptance-criteria extractor recognises a step only when the keyword is the
first token on the line, so every bulleted step was invisible: the first scenario (and every
other scenario in the file) parsed with an empty step list. This was a formatting defect, not a
missing behaviour.

**What changed:**

- `stories.md` — all 19 scenarios across the four stories rewritten to canonical Gherkin: the
  `Given`, `And`, `When`, `Then` keywords now start the line instead of being introduced by a
  `- ` bullet. Scenario headings stay `#### Scenario: <title>`. Every scenario now parses with at
  least one Given, one When and one Then; the scenario titles, steps, expected values and
  requirement traceability are otherwise unchanged.
- `story-map.json` — `BSB-18-PENDING-1` summary refined to *Require a signed-in session for every
  authoring page and API request*, naming both surfaces its scenarios cover (FR-001 for the page
  gate, NFR-002 for the API gate). The same wording is mirrored on the story's `**Summary:**` line
  in `stories.md`. No story key or requirement mapping changed.

**Coverage:** unchanged. All 10 requirements mapped to BSB-18 are still covered by the same four
stories, and `story-map.json` still maps each requirement to exactly the same story.

**Still open:** none.

## Pass 3 — 2026-11-15 — `epic-review.md` (cross-story gap review)

**Report applied:** `docs/product/epics/BSB-18/_epic/epic-review.md` — verdict CHANGES REQUESTED,
findings 1–7 and open questions 1–2. Target resolution: the run named "SkillBuilder", which is the
product title in `docs/product/PRD.md`, not a Jira issue. Jira project BSB has no issue titled
`SkillBuilder` (it contains only the epics BSB-18 through BSB-38), so the epic was resolved to
BSB-18 — the only epic with a decomposed story set and the one this review covers.

**Applied (findings with no open question):**

- **Finding 1 (blocking) — the "valid session" check now has one owner: BSB-18-PENDING-1.**
  - Summary refined to *Require a valid signed-in session for every authoring page and API
    request* in `stories.md` and mirrored in `story-map.json`.
  - Added scenarios: an unverifiable signature → page 302 + the clearing `Set-Cookie` + a 0-byte
    body; a token issued to another app client (`aud`=`platform-web`) of the same User Pool → the
    same 302 behaviour; a token from a different `iss` → the same 302 behaviour; an expired
    session on `GET /api/builds` → 401 with the exact `authentication_required` JSON body, the
    clearing cookie, and none of `Alpha`/`Beta`/`Gamma`.
  - Added a Notes bullet defining validity (signature against the User Pool key, `iss`, `aud`,
    `exp`, required claims) and the page/API response for every failure.
  - Out of scope narrowed from "a request that does carry a session" to "a request that carries a
    *valid* session".
  - BSB-18-PENDING-3 Notes changed to state that token validity is enforced by
    BSB-18-PENDING-1's gate and that this story adds only the `cognito:groups` check.
- **Finding 4 (advisory) — local-user resolution exposed once.**
  - BSB-18-PENDING-4: added two scenarios — a valid member token whose `sub` has no `users` row is
    rejected on a page (302 + clearing header) and by the API (401 `authentication_required` +
    clearing header), with no row created in either case — plus a Notes bullet that the gate
    exposes the local `users.id`, resolved by `cognito_sub`, to every admitted request.
  - BSB-18-PENDING-1 and BSB-18-PENDING-3 Notes cross-reference that resolution and its position
    after the session and membership checks.
- **Finding 5 (advisory) — actor term.** BSB-18-PENDING-3's actor changed from "platform owner" to
  the PRD §2 role "platform administrator".
- **Finding 6 (advisory) — gate exemption.** BSB-18-PENDING-1 Notes now state that
  `/auth/callback` is the only route exempt from the session gate and that any further
  unauthenticated route must be added explicitly; BSB-18-PENDING-2 Notes cross-reference the
  exemption. No duplicate callback scenario was added: BSB-18-PENDING-2's failed hosted-UI
  sign-in scenario already pins the callback's 401 response.
- **Finding 7 (advisory) — membership is per requesting user.** BSB-18-PENDING-4 Notes state that
  a `users` row proves past admission, not current membership; BSB-18-PENDING-3 carries the
  matching pointer.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 2 / Open question 1 (blocking).** Whether the builder enforces FR-141's one-hour bound
  itself (rejecting a session whose `iat` is 3600 s or more before the current time) or relies on
  the platform configuring `skill-builder-web` ID-token validity ≤ 60 minutes as an external
  prerequisite. Both branches change the shared contract and every token fixture, so applying
  either without the answer would be guessing. The contract table and BSB-18-PENDING-3's FR-141
  note are unchanged.
- **Finding 3 / Open question 2 (blocking).** Whether BSB-18 owns authentication for non-browser
  clients (a bearer ID token on the API gate) or BSB-37 owns CLI identity and membership. The
  branches differ materially (new/extended scenarios vs. an out-of-scope pointer), so this is left
  unapplied. No story was added.

**Coverage:** unchanged. All 10 requirements mapped to BSB-18 are still covered by the same four
stories, and `story-map.json` still maps each requirement to exactly the same story. Only the
BSB-18-PENDING-1 summary text changed in that file.

**Still open:** Open questions 1 and 2 above.
