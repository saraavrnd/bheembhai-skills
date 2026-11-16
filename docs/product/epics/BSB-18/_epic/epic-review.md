# Epic Review — BSB-18: Access, identity & the authoring gate

**Verdict:** CLEAN · **Date:** 2026-11-16 · **Stories reviewed:** BSB-18-PENDING-1, BSB-18-PENDING-2, BSB-18-PENDING-3

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-18/_epic/epic-review.md`.

## Context loaded

- **Work item / source.** The requested item `SkillBuilder-2` has no Jira issue on the configured
  site. The Atlassian MCP tools are not exposed in this session, so the site was queried read-only
  over its REST API (GET only; no Jira write). `GET /rest/api/3/issue/SkillBuilder-2` returned
  HTTP 404 ("Issue does not exist or you do not have permission to see it"), matching `PRD.md` §8;
  the visible projects are BEEM, BSB, EX, GRAP and LNPRTL — there is no `SkillBuilder` project.
  The run context resolves this step to epic `BSB-18`; it was read read-only from the same site
  (`GET /rest/api/3/issue/BSB-18` → HTTP 200, summary "Access, identity & the authoring gate",
  status To Do, labels `FA-1`/`MVP`, type Epic), matching `epics.md` and `epic-map.json`.
- **All 3 stories in the epic**, from `stories.md` and `story-map.json` in one read each —
  BSB-18-PENDING-1, BSB-18-PENDING-2, BSB-18-PENDING-3 (the full set, not a sample).
  `story-map.json` maps exactly these three keys with the same requirement IDs.
- **`epic-map.json`** — BSB-18 maps FR-001, FR-002, FR-003, FR-004, FR-005, FR-138, FR-141,
  FR-142, FR-165, NFR-002 and NFR-003. `epics.md`'s BSB-18 section matches (description, functional
  scope, implementation guidance, DoD, covered requirements).
- **`PRD.md`** — §5 FA-1, the §6 rows for the eleven mapped FRs, the §7 rows for NFR-002 and
  NFR-003, and §8's source, assumptions and stale-traceability wording.
- **`docs/adr/SK-001-skill-builder.md`** — the only committed design authority: §1a (builds and
  branches, for the BSB-19/BSB-21 hand-off), §3 (separate Cognito app client, externally managed
  `skill-builders` group, per-request `cognito:groups` check, no admin screen), §7 (CLI, for the
  BSB-37 hand-off), §2a (`CognitoProvider` verification) and §9 (the builder's own `users` table
  with `cognito_sub` UNIQUE).
- **Sibling epics checked for legitimate cross-epic dependencies** — BSB-19, BSB-20, BSB-22,
  BSB-23, BSB-24, BSB-25, BSB-26, BSB-31 and BSB-32 `stories.md` were read far enough to confirm
  the hand-off: BSB-19/20/22/24/25/26/31/32 each state a dependency on BSB-18 for the signed-in
  skill author, the local `users` row and/or the per-request group gate. No sibling story claims a
  BSB-18 surface or contradicts its session, error or denial contract. `epics.md`'s BSB-21 and
  BSB-37 sections were checked as the named downstream owners (build page; command line).
- **Not present:** `architecture.md`, `data-model.md`, `api-contracts/` and `ui-conventions.md` are
  not committed in this repo; the PDLC design stage runs after planning, so ADR SK-001 is the
  design context this pass can use. No `epic-sequence.md`/`.json` exists for BSB-18; ordering was
  not computed here.
- **Prior review state — verified applied.** The previous `epic-review.md` (CHANGES REQUESTED,
  four findings) was re-checked line by line against the current text rather than assumed complete:
  the callback hand-off (`users` upsert, required `sub`/`email`, missing-`sub` refusal), the
  rendered-200 `/sign-in` page and its three-value error contract, the anonymous-versus-expired
  session distinction, and `/account`'s inclusion in the protected-surface inventory are all
  present in the stories and summaries reviewed here. No story key, title, estimate, scenario
  count or requirement mapping changed in that revise pass.

## Findings

No cross-story gaps remain in the current story set. Every category of
`references/gap-checklist.md` was run across all three stories and the epic boundary:

- **Actor & role consistency.** All three stories use the single persona "skill author"; the
  external `skill-builders` Cognito group is the only access concept and maps cleanly to ADR
  SK-001 §3. There is no builder administrator role in any story, matching ADR SK-001 §3 and §9.
- **Requirement coverage / non-duplication.** All eleven epic requirement IDs are claimed exactly
  once and exercised by acceptance criteria; the apparent overlap between PENDING-1's sign-in
  rejection (FR-138) and PENDING-3's per-request denial (FR-003/FR-004/NFR-003) is a deliberate
  split using one consistent 403 message.
- **Epic-wide scope boundary.** The union of the three stories' out-of-scope sections leaves no
  capability the mapped FR/NFR text implies unowned; build-list content, CLI authentication and
  group administration are explicitly assigned to BSB-19/BSB-21/BSB-37 or declared external.
- **Architecture fit.** The pages, routes and `users` record the stories need are covered by ADR
  SK-001 §3 and §9; the only new internal state (the server-side session record) is an
  implementation detail for the later data-model artifact, not a missing entity/field/endpoint.
- **Dependency-note sanity.** Notes are reciprocal and refer to real keys (see the dedicated
  section below).
- **Epic-wide silent NFRs.** The only NFRs mapped to BSB-18 are NFR-002 and NFR-003, both
  addressed per request by PENDING-3; accessibility is mapped to BSB-38, not this epic.
- **Traceability.** The eleven IDs and their PRD wording still match `epic-map.json`; no drift was
  found (one stale PRD sentence is noted informationally under the coverage check below).

Prior findings, recorded here so the reviewer can see they were settled rather than dropped:

| Prior finding | Severity | State in current text |
|---|---|---|
| Callback hand-off: `users` upsert, required `sub`/`email`, missing-`sub` refusal | Blocking | Applied — PENDING-1 Notes and successful-sign-in Given/When; PENDING-2 Notes and "Sign-in without a subject claim is refused" |
| `GET /sign-in` is a rendered HTTP 200 page, not a redirect to Cognito | Blocking | Applied — PENDING-1 Notes; PENDING-3 "Public sign-in page is not gated by the middleware" |
| Expired, unrefreshable session distinct from an anonymous request | Blocking | Applied — PENDING-1 Notes (state retained, `session_expired`) and PENDING-3 Notes (`session_expired` vs `session_required`) |
| `/account` in the protected-surface inventory | Advisory | Applied — PENDING-2 Notes (gated by PENDING-3's middleware) and PENDING-3 Notes (named protected surface) |

## Open questions

None. Every prior finding was a contract, hand-off or inventory fix that followed from the
stories' own acceptance criteria and ADR SK-001; the earlier route-ownership, middleware-ownership
and sign-in-flow questions were settled by the Pass 4 re-slice recorded in `_epic/revisions.md`,
and this pass found nothing that reopens them.

## Proposed changes

None. No change is proposed to `stories.md`, `story-map.json`, `epic-map.json`, the PRD,
`epics.md` or Jira. The epic is ready for `sdlc-plan-epic-sequence`.

## Architecture impact

None. The epic's cumulative behaviour is covered by the committed design authority, ADR SK-001: a
separate Cognito app client and the externally managed `skill-builders` group with a per-request
`cognito:groups` check (§3), the builder's own `users` table keyed by `cognito_sub` UNIQUE (§9),
and `CognitoProvider` token verification (§2a). The stories introduce no entity, field, endpoint or
integration that the ADR lacks; the server-side session record PENDING-1 introduces is internal
state for the later data-model artifact, not a design-stage dependency. No design-stage pass is
needed before sequencing.

## Requirement coverage check

Complete and non-duplicated. Every requirement `epic-map.json` assigns to BSB-18 is exercised by
at least one story's acceptance criteria, and no FR/NFR is claimed by two stories in contradictory
ways:

| Requirement | Exercising story | Acceptance criteria that exercises it |
|---|---|---|
| FR-001 | BSB-18-PENDING-3 | "Visitor without a session is sent to sign in" / "API request without a session is rejected" |
| FR-002 | BSB-18-PENDING-1 | "Current group member signs in and opens the builds page" (Cognito hosted sign-in with the platform credentials) / "Incorrect password does not create a builder session" |
| FR-003 | BSB-18-PENDING-3 | "Current member opens the builds page" / "Removed member is denied within one hour" |
| FR-004 | BSB-18-PENDING-3 | "Removed member is denied within one hour" (the `cognito:groups` claim is re-read at 11:15 after the 11:00 refresh) |
| FR-005 | BSB-18-PENDING-2 | "First sign-in creates my builder account and shows it on my account page" |
| FR-138 | BSB-18-PENDING-1 | "Non-member sign-in is refused" (403, no `sb_session` cookie, no `users` row) |
| FR-141 | BSB-18-PENDING-3 | "Removed member is denied within one hour" |
| FR-142 | BSB-18-PENDING-2 | "Signing in again shows the same account" |
| FR-165 | BSB-18-PENDING-2 | All three isolation scenarios (no connection, no client/credential, startup refusal) |
| NFR-002 | BSB-18-PENDING-3 | "Visitor without a session…" / "API request without a session…" / "Expired session is sent back to sign in" |
| NFR-003 | BSB-18-PENDING-3 | "Removed member is denied within one hour" / "Removed member's API request is denied", with no builder data returned |

All 3 stories' `requirement_ids` and `story-map.json` agree with this table; no story claims a
requirement outside the epic. The scenarios exercise the behaviours rather than only listing the
IDs under "Covered requirements".

Informational, no story change: `PRD.md` §8 still says FR-165 "will be mapped on the next epics
pass" although `epic-map.json` already maps it to BSB-18 and PENDING-2 covers it. That is a stale
sentence in the PRD, outside this skill's write scope; it produces no gap in the stories.

## Dependency-note sanity check

Consistent; no one-sided, missing or dangling dependency notes remain.

- **Reciprocated in-epic notes.** PENDING-1 defines the `sb_session` session contract "that
  BSB-18-PENDING-2 and BSB-18-PENDING-3 consume" and names its callback as invoking PENDING-2's
  `users` upsert. PENDING-2 "Depends on BSB-18-PENDING-1 for the verified token and the session
  contract" and states it supplies that upsert and missing-`sub` refusal. PENDING-3 "Depends on
  BSB-18-PENDING-1 for the signed-in session contract and for the minimal `/builds` page and GET
  `/api/builds`", and PENDING-1 reciprocates by naming `/sign-in` and `/auth/callback` as public
  routes exempt from PENDING-3's middleware.
- **`/account` dependency is two-sided.** PENDING-2's Notes say `GET /account` is gated by
  PENDING-3's per-request middleware; PENDING-3's Notes name `/account` among the representative
  protected surfaces it gates. Neither side claims a dependency the other denies.
- **Real keys only.** All referenced story keys exist in `story-map.json`; no note points at a
  non-existent story. PENDING-2's only named in-epic dependency is PENDING-1; PENDING-3's is
  PENDING-1.
- **Cross-epic notes written down.** PENDING-1 names BSB-19 and BSB-21 as the owners that replace
  the minimal `/builds` page and `GET /api/builds` content; PENDING-3 names BSB-37 as the
  command-line owner that must authenticate against this same gate, with CLI authentication in its
  Out of scope. In return, BSB-19, BSB-20, BSB-22, BSB-24, BSB-25, BSB-26, BSB-31 and BSB-32 each
  state their dependency on BSB-18's signed-in author, local `users` row and/or per-request gate.
  BSB-21 and BSB-37 are planned epics without decomposed stories yet, which is a normal cross-epic
  dependency, not a dangling key.
- **No cycles.** PENDING-1 is the only prerequisite either sibling names, and PENDING-1 names no
  in-epic prerequisite; PENDING-2 and PENDING-3 are siblings of it. Build order itself is left to
  `sdlc-plan-epic-sequence` and is not computed here.

---
*No approval action is required for this pass: the report proposes no story or map change. Next:
`sdlc-plan-epic-sequence` for BSB-18, then the per-story review for any single-story concern this
epic-level pass deliberately did not raise.*
