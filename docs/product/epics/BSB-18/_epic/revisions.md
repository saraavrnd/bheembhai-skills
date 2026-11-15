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
