# Revisions — BSB-18 (Access, identity & the authoring gate)

## Pass 1 — 2026-11-16 (automated verifier feedback)

**Report applied:** the step hand-off feedback for `sdlc-plan-stories-write` on run
`2e351540-8ae0-4117-90a3-bef1c4e28bd3`. No `epic-review.md` or `story-review.md` report existed on
disk; the findings below are the verifier's failing checks, applied as a revise pass.

### Findings applied

- **`scenario_executable` — BSB-18-PENDING-1, "Invalid credentials are rejected".** The scenario
  fixed the username and the final UI message but left the wrong-password value, the
  "ada@example.com" account's valid password, the sign-in page URL and the Cognito error to assert
  unspecified. Rewrote the scenario to pin the account ("ada@example.com", valid password
  "Correct-Horse-Battery-1"), the submitted incorrect password ("wrong-password-123"), the sign-in
  page ("/sign-in"), and Cognito's exact failure (HTTP 400, error code "NotAuthorizedException").
  The remaining assertions are the builder's HTTP 200, the exact message "Sign-in failed. Check your
  username and password.", no session cookie, and no "users" row.
- **Sibling sign-in scenarios in BSB-18-PENDING-1.** Tightened the member and non-member scenarios
  to the same fixture (concrete usernames and passwords, the "/sign-in" route) so they satisfy the
  same execability bar, and split the former two-condition callback scenario into
  "Callback without a code parameter is rejected" and "Callback with an unverifiable token is
  rejected" — one behaviour each.
- **`story_map` artifact.** Updated the BSB-18-PENDING-1 summary to match its revised title,
  "Sign in with platform credentials and reject invalid sign-ins". Requirement coverage is
  unchanged: all 11 epic requirements remain covered by the same five stories.

### Still open

None.
