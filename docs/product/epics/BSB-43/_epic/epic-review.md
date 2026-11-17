# Epic Review — BSB-43: Test projects & membership

**Verdict:** ESCALATE · **Date:** 2026-11-17 · **Stories reviewed:** BSB-43-PENDING-1, BSB-43-PENDING-2, BSB-43-PENDING-3, BSB-43-PENDING-4, BSB-43-PENDING-5

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-43/_epic/epic-review.md`.

## Context loaded

- **Target work item `SkillBuilder-2` — unavailable.** A read-only Atlassian REST fetch of
  `https://saraavrnd.atlassian.net/rest/api/3/issue/SkillBuilder-2` returns HTTP 404 ("Issue does
  not exist or you do not have permission to see it"); the site's project list contains BEEM, BSB,
  EX, GRAP and LNPRTL and no `SkillBuilder` project. This matches `docs/product/PRD.md` §8,
  `docs/product/epics.md` and the input note in this epic's `_epic/stories.md`. The Atlassian MCP
  server configured in `.mcp.json` was not exposed as a tool in this session, so the read-only Jira
  REST API was used. The work item contributes no scope here.
- **Epic under review:** `BSB-43` "Test projects & membership" (Jira `BSB-43`, fetched read-only;
  status To Do; labels FA-4, MVP; no issue links, subtasks or comments; description, functional
  scope, edge cases, non-goals, implementation guidance, Definition of Done, covered requirements
  and notes match `_epic/stories.md`). BSB-43 is the epic whose stories were written by the
  immediately preceding `sdlc-plan-stories-write` run (commit `77052d9`) and the only written epic
  without an `epic-review.md`.
- **Stories:** all 5 in the epic, from `_epic/stories.md` and `_epic/story-map.json` — the full set,
  not a sample. Story keys are the `BSB-43-PENDING-*` placeholders until `sdlc-tracker-sync`
  publishes them; `story-map.json`'s summaries and requirement mappings match `stories.md`.
- **PRD:** `docs/product/PRD.md` §5 FA-4, §6 FR-023–FR-028 (the six requirements `epic-map.json`
  assigns to BSB-43), §7 (no NFR is mapped to FA-4), §4 scope, and §8 "Access model", "External
  prerequisites", "Secrets" and "Authoring surface". The identity/group gate is FA-1 / BSB-39.
- **Design input:** there is no `docs/architecture.md`, `docs/data-model.md`,
  `docs/api-contracts/` or `docs/ui-conventions.md` in this repo; the committed design reference is
  `docs/adr/SK-001-skill-builder.md`. Read §3 (Cognito `skill-builders` group; the builder checks
  the *caller's* `cognito:groups` claim on every request; builder `users` table keyed by `sub`; no
  platform-database access), §4 (a test project is the builder's own record; the creator is owner;
  members can run tests; only the owner changes integrations; credentials live in Secrets Manager),
  and §9 (`users` = `id`, `cognito_sub`, `email`, `name`; `projects.owner_id`;
  `project_members.role` = owner/member; `integrations.kind` = jira/github/ai_model; `runs`).
- **Sibling epics checked:** BSB-39's `stories.md`, `story-map.json` and `revisions.md` (fixture
  accounts and `builder_session`; BSB-39-PENDING-4's caller-claim recheck; its open
  membership-freshness question); BSB-44 (FA-5 — owner-only integration CRUD, secret reference,
  MCP definitions, verification); BSB-45 (FA-6 — run form and run start reusing the membership
  decision); BSB-46/BSB-47 (FA-11/FA-12 — scan starts); BSB-57 (FA-9, Later); and the
  `epic-map.json` entries for all of them. No `epic-sequence.md`/`.json` exists yet, so relative
  build order cannot be confirmed in this pass — that remains `sdlc-plan-epic-sequence`'s job.

## Findings

### Finding 1 — Cross-epic architecture fit: Story 2 requires an arbitrary target user's *current* `cognito:groups`, which no committed design or FA-1 story provides

- **Severity:** Blocking
- **Stories touched:** BSB-43-PENDING-2 (with the epic preface and FA-1 / BSB-39 as the assumed
  provider).
- **Evidence:**
  - `stories.md:199–202` — Story 2's scenario "A target who is not a current skill-builder is
    refused": `Given project prj_H5mQ2rT8vX is owned by Alice (U_alice) and Erin (U_erin) has a
    users row but her current cognito:groups claim is [] … Then the builder responds with HTTP 422
    and body exactly {"error":"not_a_skill_builder"}`.
  - `stories.md:216` — Story 2's Notes assert the mechanism: "The target's current claim is read
    from the identity provider at add time (the Cognito user directory is an external prerequisite,
    as in BSB-39)". BSB-39 provides no such directory read.
  - `docs/product/epics/BSB-39/_epic/stories.md:203–205` — BSB-39-PENDING-4 only "re-reads the
    identity-provider claim" for the *signed-in caller* whose request is being authorized, and
    `:162–164` record that as the caller's membership decision; there is no lookup of an arbitrary
    `users.id`'s current group.
  - `docs/adr/SK-001-skill-builder.md:180–188` — §3 defines the identity mechanism as checking the
    `cognito:groups` claim on every request (of the caller) and a `users` table keyed by the Cognito
    `sub`; `:349` — §9's `users` columns are `id`, `cognito_sub`, `email`, `name`, with no group
    column. Nothing in §3/§9 describes a Cognito admin/directory read for another user, or the
    permission it would need.
  - `docs/product/epics/BSB-39/_epic/revisions.md:56–60` — BSB-39's own epic review left the
    membership-freshness model open (Finding 3), so even the caller-claim mechanism Story 2 builds
    on is not yet settled.
- **What is missing/ambiguous/contradictory:** The epic's cumulative behavior as written needs a
  capability that is not in the committed design and is not a planned deliverable of any epic: a
  way to obtain a *target* user's current group membership. The `users` table is the only durable
  identity record and does not store groups; the builder only sees the caller's token claim. A
  developer implementing Story 2 exactly as written cannot satisfy the `not_a_skill_builder` case
  without inventing an identity-provider integration (a Cognito admin/directory call plus its IAM
  permission, or a local membership projection with a freshness rule). Read alone, Story 2 looks
  complete because its Notes claim the lookup is "as in BSB-39"; only comparing it with BSB-39 and
  §3/§9 shows that assumption is unsupported.
- **Question (if a person must decide):** Should the owner's add-member validation read the target's
  *current* `cognito:groups` claim (which requires a new identity-provider directory capability and
  its permissions), or is "another skill-builder user" satisfied by an existing `users` row — created
  only by a successful sign-in that already required the group — with FA-1's per-request gate
  denying a removed user? If the former, what is the authoritative source and permission for that
  lookup, and who owns it?
- **Proposed change:**
  - **If the current-claim refusal is kept:** BSB-43-PENDING-2's Notes must stop saying the lookup
    is "as in BSB-39" and instead record the real dependency: "The target's current group claim
    comes from the identity provider's user directory, which FA-1 (BSB-39) does not yet expose and
    SK-001 §3 does not describe; that capability (source, permission, freshness) must be settled in
    design before implementation." Add the same sentence to the epic preface's fixture/gate
    paragraph, and route the capability to `sdlc-arch-design` (amend) for BSB-39/FA-1. Do not
    implement the lookup by inventing a data model inside this epic.
  - **If the refusal is dropped:** replace Story 2's 422 `not_a_skill_builder` scenario with a
    target rule this epic can implement from the committed model: the target must have a `users`
    row (a prior successful sign-in); no row → HTTP 404 `{"error":"user_not_found"}`. Rely on FA-1's
    per-request gate to deny a removed user's requests. Update Story 2's Notes and the preface's
    "Membership write contract" and edge-case sentence ("adding a user who has never successfully
    signed in is refused; a user removed from the group is denied at request time by FA-1's gate").
  - **Either way:** keep Story 2's owner-only and idempotency scenarios unchanged; the
    422/404 contract in the preface must match the chosen option. Stories 1, 3, 4 and 5 need no
    behavior change for this finding.

### Finding 2 — Cross-epic fixture provenance: Erin is presented as BSB-39's fixture account but is not in BSB-39's fixture table

- **Severity:** Advisory
- **Stories touched:** BSB-43-PENDING-1, BSB-43-PENDING-2, BSB-43-PENDING-4 (plus the epic preface).
- **Evidence:**
  - `stories.md:15–30` — the preface says "**Fixture accounts.** The Cognito fixture is BSB-39's:"
    and then lists five rows, including `erin@example.test | sub-11111 | Erin Ex-member | [] |
    U_erin` (`:23`), and explains that "Erin signed in while still in the skill-builders group, so
    her `users` row exists" (`:27–30`).
  - `docs/product/epics/BSB-39/_epic/stories.md:7–16` — BSB-39's fixture table defines Alice, Bob,
    Mallory, Casey and Dana; there is no Erin, no `sub-11111`, and no account with a pre-existing
    `users` row and an empty group claim.
  - Erin is load-bearing in three of the five stories: Story 1's "A non-skill-builder cannot create
    a project" (`stories.md:148–151`), Story 2's "A target who is not a current skill-builder is
    refused" (`:199–202`), and Story 4's "An owner who lost skill-builders membership is denied by
    the authoring gate" (`:304–307`).
- **What is missing/ambiguous/contradictory:** The fixture's provenance is wrong and the account is
  under-specified. A test author who follows the preface to BSB-39's fixture set will not find Erin,
  her credentials, or the story of how her `users` row and a `builder_session` were created while
  she was still a member. The three scenarios above therefore cannot be set up from the stated
  fixture as written, and different implementers could seed Erin differently (different subject or
  session handling), producing inconsistent non-member tests across stories.
- **Question (if a person must decide):** Should Erin be added to BSB-39's fixture table (a
  cross-epic fixture change for the BSB-39 pass), or is Erin an additional fixture account owned by
  this epic, with her pre-seeded `users` row and the way her session was issued defined here?
- **Proposed change:**
  - **Preferred, BSB-43-local:** rewrite `stories.md:15` from "The Cognito fixture is BSB-39's:" to
    "The Cognito fixture extends BSB-39's with one account defined here," and state Erin's complete
    setup: subject `sub-11111`, groups `[]`, a pre-seeded `users` row `U_erin`, and that the test
    issues her a `builder_session` as if it were issued while she was a member (the case
    BSB-39-PENDING-3 already covers as "a token issued while `cognito:groups` contained
    `skill-builders` and whose current claim is `[]`"). If a real sign-in is required, define her
    credentials too.
  - **Alternative:** add Erin to BSB-39's fixture table in `BSB-39/_epic/stories.md` (cross-epic)
    with the same values, and keep BSB-43's preface pointing at BSB-39.
  - **Same fixture definition for all three listed stories:** Stories 1, 2 and 4 keep their current
    scenarios; they must consume the corrected Erin definition. Stories 3 and 5 do not use Erin and
    need no change.

## Open questions

1. **Target current-claim validation (Finding 1).** Does the owner's add-member check read the
   target's *current* `cognito:groups` (requiring a new identity-provider directory capability,
   source, permission and freshness rule owned by FA-1/BSB-39), or is an existing `users` row
   sufficient, with FA-1's per-request gate handling removal? This decides whether the 422
   `not_a_skill_builder` contract stays and whether an architecture decision is needed.
2. **Erin's fixture ownership (Finding 2).** Is Erin part of BSB-39's fixture set (and BSB-39's
   stories must be amended), or an additional BSB-43 fixture whose pre-seeded `users` row and
   session issuance are defined in this epic's preface?

## Proposed changes

Per touched story, for `sdlc-plan-stories-write` (revise mode). All changes are proposed, not
applied.

- **BSB-43-PENDING-2:** apply the answer to Open question 1. If the current-claim refusal is kept,
  replace the "as in BSB-39" sentence in Notes/dependencies with the explicit identity-provider
  directory dependency and hand the capability to `sdlc-arch-design` (amend) via FA-1/BSB-39. If it
  is dropped, replace the 422 `not_a_skill_builder` scenario with the "target must have a `users`
  row; no row → 404 `user_not_found`" rule and update Notes/dependencies accordingly. Keep the
  owner-only, non-member, idempotency and unknown-user scenarios otherwise unchanged.
- **BSB-43-PENDING-1, BSB-43-PENDING-4:** no behavior change. Both use Erin (non-skill-builder
  create; owner-lost-group denial); they must consume the corrected Erin fixture definition from
  Finding 2. If Open question 1 changes what "skill-builder user" means, restate the same definition
  in their Notes so they do not drift from Story 2.
- **BSB-43-PENDING-3, BSB-43-PENDING-5:** no change from this report. Their owner-only,
  last-owner, in-flight-run, settings-page and integration-guard scenarios are internally consistent
  and consistent with Stories 1, 2 and 4.
- **`_epic/stories.md` (preface):** fix the fixture provenance and Erin definition (Finding 2);
  align the "Membership write contract" and the edge-case sentence with the answer to Open question
  1 (Finding 1).
- **`_epic/story-map.json`:** no change — the FR-023–FR-028 mapping and story summaries are
  unaffected.

## Architecture impact

One gap is an **architecture conflict**, not a story-wording fix: BSB-43-PENDING-2's
`not_a_skill_builder` refusal needs an arbitrary target user's current group membership, and the
committed design provides only the caller's per-request `cognito:groups` claim
(`SK-001-skill-builder.md` §3) and a `users` table with no group column (§9). No epic's planned
stories provide a user-directory lookup, and BSB-39's own membership-freshness model is still open.
Closing this by keeping the refusal requires `sdlc-arch-design` (amend) to define the source,
permission and freshness of the target-claim lookup (a Cognito admin/directory read, a local
membership projection, or similar) and, if needed, amend the identity data model. If the product
instead scopes FR-025 to "an existing `users` row" and lets FA-1's gate handle removal, the gap
closes as a story change and no architecture work is needed — but that is a product decision about
the epic's stated edge case, so it is recorded here for the gate rather than assumed. Finding 2
(fixture provenance) needs only a documentation change.

## Requirement coverage check

All six requirements assigned to BSB-43 are exercised by at least one acceptance criterion; no
requirement is duplicated or redefined across stories.

| Requirement | Story | Exercising acceptance criteria |
|---|---|---|
| FR-023 | BSB-43-PENDING-1 | "Create a project records the creator as its owner" (`POST /api/projects` 201 + `projects` row); "Unauthenticated create is rejected"; "A non-skill-builder cannot create a project"; "An empty project name is rejected" |
| FR-024 | BSB-43-PENDING-1 | The same create scenario asserts `owner_id = U_alice`, exactly one `project_members` row with `role` `owner`, and `role` `owner` in `GET /api/projects` |
| FR-025 | BSB-43-PENDING-2 | "The owner adds a current skill-builder as a member" (201, row `role` `member`); idempotent re-add; non-owner/non-member refusal; non-skill-builder target (see Finding 1 for the mechanism); unknown user |
| FR-026 | BSB-43-PENDING-3 | "The owner removes a member" (204, row deleted, project unaffected, Bob's list excludes it); non-owner/non-member refusal; last-owner 409; non-member target 404; in-flight-run scenario |
| FR-027 | BSB-43-PENDING-4 | Member and owner `GET /api/projects/{id}` return `can_start_run: true` and the page renders `data-testid="start-run"` → `/projects/{id}/runs/new`; non-member, other-project owner, removed member and group-lost owner are denied |
| FR-028 | BSB-43-PENDING-5 | Owner `PUT /api/projects/{id}/integrations/jira` returns 200 and writes one row with the submitted non-secret config; non-owner, non-member and other-project owner are denied `owner_required`; the settings page shows the edit affordance only to the owner |

Notes:
- **FR-027 is exercised as the membership decision, not as an actual run start.** The story's own
  Out of scope (`stories.md:313`) and Notes (`:316`) explicitly defer the run-start submit endpoint
  to FA-6 / BSB-45 and require BSB-45 (and FA-11/FA-12 for scans) to call the same decision. That is
  a legitimate, written, cross-epic split — not a coverage hole — but it means the epic's DoD
  sentence "membership authorizes starting a run" is satisfied by the decision helper and the Start
  run affordance, with the actual start proven later in BSB-45. No story change is proposed for this.
- No NFR is assigned to BSB-43 by `epic-map.json`. NFR-002/NFR-003 belong to BSB-39, and the epic
  preface (`stories.md:7–13`) states that every route in this epic inherits the 401/403 authoring
  gate, so they are addressed once at the epic level. NFR-012 / FA-17 accessibility belongs to
  BSB-56; NFR-004/NFR-006 credential handling belongs to BSB-44, and Story 5 explicitly defers
  credentials to it.
- No requirement-wording drift was found: FR-023–FR-028 match the current `PRD.md` §6 text, and
  `epic-map.json`'s `requirement_ids` match the Jira epic's "Covered requirements" and
  `stories.md`'s coverage summary.

## Dependency-note sanity check

Mostly correct; one cross-epic dependency is asserted against a capability that does not exist
(Finding 1). Mismatches and observations:

- **Within the epic — reciprocal and correct:** Story 1's Notes say `projects.owner_id` is used by
  every later story's owner check and the project list is the read surface later stories use;
  Stories 2, 3, 4 and 5 each name BSB-43-PENDING-1. Story 2's Notes say the inserted row is the
  durable membership record used by BSB-43-PENDING-3 and -4; both name Story 2. Story 3's Notes say
  new starts after removal are denied by Story 4's decision; Story 4's removed-member scenario
  matches. Story 5 names Story 1 and the `projects.owner_id` owner record.
- **BSB-43-PENDING-2 → BSB-39 (FA-1):** the target-current-claim dependency is **not** satisfied by
  the named provider — see Finding 1. The caller-side gate dependencies in Stories 3, 4 and 5 on
  `BSB-39-PENDING-4` are correct (that story exists and covers the request-time recheck); only the
  *target* lookup is unsupported.
- **Cross-epic owners named:** Story 5 names FA-5 / BSB-44 for integration contents, secret
  reference, MCP, verification and display, and BSB-44's epic maps exactly those requirements; Story
  4 names FA-6 / BSB-45 for the run form and start; Story 3 names FA-7 / BSB-48 and FA-8 / BSB-49 for
  run execution and terminal states. All keys exist in `epic-map.json`. Story 4's Notes refer to
  FA-11 / FA-12 by feature-area code only (the epics are BSB-46 and BSB-47); this is unambiguous but
  adding the keys would match the rest of the set. No dependency note names a story key that does
  not exist.
- **BSB-39-PENDING-4's Notes do not reciprocate** BSB-43's dependence, but the dependency is
  recorded on the depending side and BSB-39 predates BSB-43; no change is required in this epic.
- **Fixture dependency:** the Erin account is a fact BSB-39's fixture set does not supply — see
  Finding 2.
- No `epic-sequence.md`/`.json` exists yet, so sequencing position cannot be checked here; build
  order itself is `sdlc-plan-epic-sequence`'s job.
