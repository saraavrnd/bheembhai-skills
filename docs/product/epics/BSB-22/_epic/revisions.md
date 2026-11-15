# Revisions — BSB-22

## Pass 1 — 2026-11-15 — `epic-review.md` (cross-story gap review)

**Report applied:** `docs/product/epics/BSB-22/_epic/epic-review.md` — verdict CHANGES REQUESTED,
findings 1–8 and open questions 1–5. Target resolution: the run named "SkillBuilder", which is the
product title in `docs/product/PRD.md`, not a Jira issue; the Atlassian project `bheembhai-skill-builder`
contains only the epics BSB-18 to BSB-38. The epic was resolved to **BSB-22** — the epic the
preceding `sdlc-plan-stories-write` run wrote (commit `70c9c1b`) and whose review requested changes
(commit `0580ae0`). The Atlassian MCP server was not connected in this session, so the epic was
fetched read-only through the Atlassian REST API (summary *Test projects & membership*, type Epic,
labels `FA-4`, `MVP`) and cross-checked against the BSB-22 section of `docs/product/epics.md`.
Nothing was written to Jira.

**Applied (findings with no open question):**

- **Finding 5 (advisory) — every run and scan start path applies the membership check.**
  - `BSB-22-PENDING-4` Notes: the BSB-31/BSB-32 reuse bullet now says *every* path that starts a
    run or a scan applies the check — re-runs and output chaining (BSB-27, FR-056 and FR-057),
    scans (BSB-31 and BSB-32, FR-092 and FR-093) and the CLI (BSB-37, FR-116 to FR-118) — and that
    it therefore belongs in the run/scan start service, not only in the HTTP route.
  - `BSB-22-PENDING-3` Notes: "on every run start" changed to "on every run or scan start, on every
    path listed in BSB-22-PENDING-4".

- **Finding 6 (advisory) — the authorization order is complete, including BSB-18's group gate and
  body validation.**
  - `stories.md` contract preamble: the fixed order is now 401 `authentication_required` → 403
    `not_a_member` (BSB-18) → 404 `project_not_found` → 403 `project_membership_required` → 403
    `project_owner_required` where required → 422 request-body validation, with the consequence
    that an unauthorized caller never learns a body-validation error.
  - `BSB-22-PENDING-2`: added scenario *A non-owner member's invalid body is refused by the owner
    check, not body validation* — Grace (member, not owner) sends `{}` and receives 403
    `project_owner_required` with the exact existing body, and `project_members` still has two rows.

- **Finding 7 (advisory) — one stated source of truth for the owner check.**
  - `stories.md` contract preamble: added "The owner check reads the caller's `project_members` row
    whose `role` is `owner`; `projects.owner_id` is the denormalized creator record and must equal
    that row's `user_id`."
  - `BSB-22-PENDING-1` Notes: added the at-most-one-owner invariant and its enforcement
    (partial unique index on `project_members (project_id) WHERE role = 'owner'`, or an equivalent
    invariant for `sdlc-deliver-story-design` to enforce in the project-writing transaction).

- **Finding 8 (advisory) — the PENDING-2 → PENDING-5 dependency is declared on both sides.**
  - `BSB-22-PENDING-5` Notes: added the dependency on BSB-22-PENDING-2 for the `member` role rows
    its non-owner scenario exercises.
  - `BSB-22-PENDING-2` Notes: the forward note now also says BSB-22-PENDING-5 distinguishes these
    rows from the owner.

**Still open — not applied, because the question has no answer in the run hand-off:**

- **Finding 1 / Open question 1 (blocking).** How the membership/owner checks are split from the
  run-start and integration routes they protect: (a) re-scope PENDING-4/PENDING-5 to a reusable
  guard and move the 201/200 success assertions to BSB-24/BSB-23, (b) move the two stories into
  those epics, or (c) keep the stories and accept that BSB-22 closes after BSB-23 and BSB-24. All
  three change the stories' acceptance criteria and cross-epic notes, so nothing was applied.
- **Finding 2 / Open question 2 (blocking).** Whether the project and membership web pages (list,
  create, settings/members view with add and remove) and their read endpoints are new BSB-22
  stories or owned by a named other epic. No story was added and no Out-of-scope owner was named,
  because choosing the epic without the answer would be guessing.
- **Finding 2 / Open question 3 (blocking).** Whether any project owner may see every local
  user's name and email to pick a member, or the picker must take an exact email address. The
  add-member picker therefore remains as described and no privacy rule was invented.
- **Finding 3 / Open question 4 (blocking).** Whether "has a local `users` row" is the accepted
  add-time meaning of "a current skill-builder", with former group members neutralized by BSB-18's
  per-request gate, or add-time rejection must cover former members (which needs a Cognito
  directory read the architecture does not provide). PENDING-2's "Boundary for review" bullet is
  unchanged.
- **Finding 4 / Open question 5 (blocking).** Whether the project's LLM-scan default model is an
  integration setting covered by FR-028/PENDING-5's owner check or a separate setting owned by
  BSB-23/BSB-32. PENDING-5's Out-of-scope entry and Notes are unchanged.

**Coverage:** unchanged. All 6 requirements mapped to BSB-22 (FR-023 to FR-028) are still covered
by the same five stories, and no story claims a requirement outside the epic. `story-map.json` is
unchanged: no story key, summary or requirement mapping changed.

**Note for the next review (not a finding of this pass):** PENDING-2 now has seven acceptance
scenarios (the skill's stated upper bound). If Finding 2's answer adds a member-management page
story, the non-owner-invalid-body scenario could move to that story's route rather than growing
PENDING-2 further.
