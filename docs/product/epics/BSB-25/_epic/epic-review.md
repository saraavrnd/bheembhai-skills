# Epic Review — BSB-25: Skill packaging & run branch preparation

**Verdict:** ESCALATE · **Date:** 2026-11-16 · **Stories reviewed:** BSB-25-PENDING-1, BSB-25-PENDING-2, BSB-25-PENDING-3

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-25/_epic/epic-review.md`.

## Context loaded

- **Target work item.** The prompt names `SkillBuilder-2`. A read-only `GET /rest/api/3/issue/SkillBuilder-2`
  returned **HTTP 404 "Issue does not exist or you do not have permission to see it."**, which matches
  `docs/product/PRD.md` §8: the original `SkillBuilder` project is gone and the work lives in project
  **BSB** (the PRD is the umbrella record). The Atlassian MCP tools were not exposed in this session;
  the configured site (`https://saraavrnd.atlassian.net`) was read through its REST API, read-only,
  using the credentials already in `.mcp.json`/env. The epic under review is **BSB-25 — Skill packaging
  & run branch preparation**, named by the run context (`BB_CONTEXT.ITEM`) and fetched read-only:
  status To Do, labels `FA-6`, `MVP`, no parent, no sub-tasks, no child issues, no links. No Jira write
  was made.
- **Epic story set.** `docs/product/epics/BSB-25/_epic/stories.md` — all three stories (312 lines):
  BSB-25-PENDING-1 "Run the exact skills commit I chose even after the branch moves" (FR-038),
  BSB-25-PENDING-2 "Package the pinned skill commit once and reuse the same bundle" (FR-039, FR-040,
  NFR-009), BSB-25-PENDING-3 "Run against my test branch without ever changing it" (FR-041, FR-042,
  FR-043, NFR-001). `story-map.json` has the same three stories and the same eight requirement ids.
- **Product context.** `docs/product/PRD.md`: §4–5 FA-6 (line 55), §6 FR-038…FR-043 (lines 111–117),
  §7 NFR-001 (line 251) and NFR-009 (line 259), §8 source caveat (lines 273–281). `docs/product/epic-map.json`
  agrees with the story map. `docs/product/epics.md`: BSB-24 (657–713), BSB-25 (717–759), BSB-26 (761+),
  BSB-27, BSB-30 (979–1046), BSB-31 (520–600).
- **Design authority.** `docs/adr/SK-001-skill-builder.md` §1 (line 56), §4 (190–211), §5 (213–255),
  §6b, §9 (345–357); `tools/build.py` (`pack` at lines 82–119). No `docs/architecture.md`,
  `docs/data-model.md`, `docs/api-contracts/`, or `docs/ui-conventions.md` is committed yet — the
  architecture-design step runs after planning, so ADR SK-001 is the design authority this pass can use.
- **Sibling stories read for the cross-epic hand-offs.** BSB-24-PENDING-1 (run start),
  BSB-23-PENDING-2 (source-control integration) and BSB-23-PENDING-6 (test-purpose admission),
  BSB-19-PENDING-3 (skill naming), BSB-31-PENDING-1 (static scan) and BSB-32's `skill_bundles` fixtures;
  the BSB-24 and BSB-31 `epic-review.md` files for the carried cross-epic notes.
- **Not present.** No `epic-sequence.md`/`.json` for BSB-25; BSB-26, BSB-27, BSB-29, BSB-30, BSB-33,
  BSB-34, BSB-36 and BSB-37 have no stories yet. Sequencing is not computed here.

## Findings

### Finding 1 — Cross-epic architecture fit: the run bundle's content and format contradict ADR SK-001 §5 and `tools/build.py`
- **Severity:** Blocking
- **Stories touched:** BSB-25-PENDING-2 (primary), BSB-25-PENDING-3; cross-epic BSB-26, BSB-31.
- **Evidence:** BSB-25-PENDING-2 Notes say the bundle is "a tar archive of that skill's own catalog folder
  at the pinned commit and nothing else from the catalog repository" (`stories.md:197-199`), canonicalized
  as "an uncompressed tar stream" stored at `bundles/<skills_commit_sha>/<skill>.tar.gz`
  (`stories.md:201-204`); AC1 says the packer "records exactly the 5 skill-folder paths and nothing from
  `config/`, `tools/` or another skill" (`stories.md:139-142`). ADR SK-001 §5 says "the skill is packed
  with `tools/build.py` into a content-addressed bundle, exactly as a release would pack it"
  (`SK-001:218-219`). What `tools/build.py` packs is the **whole catalog**: `manifest.json`, every file
  under `skills/`, every `config/*.yaml` and `catalog.yaml`, as a **gzipped** tarball written to
  `dist/catalog.tgz` (`tools/build.py:82-119`); ADR §1 confirms `tools/build.py` packs `skills/`,
  `config/` and `catalog.yaml` (`SK-001:56`). The story therefore specifies a per-skill, config-free,
  uncompressed artifact; the ADR and the tool specify a whole-catalog, config-bearing gzip. BSB-26
  executes the bundle and BSB-31 scans it, so both consumers inherit whichever answer is chosen.
- **What is missing/ambiguous/contradictory:** Neither shape is derivable from the other without a
  product/architecture decision: per-skill isolation vs release fidelity; whether `config/*.yaml`
  (model tiers, limits) travels with the skill; whether `manifest.json` is required at execution;
  gzip vs uncompressed bytes for the `bundle_sha256`; and whether `tools/build.py` gains a
  single-skill mode or the builder writes a second packer. The story pass cannot settle this without
  changing the ADR's "exactly as a release would pack it" or the tool.
- **Question (if a person must decide):** Is a run bundle the whole-catalog release artifact described
  in ADR SK-001 §5 and produced by `tools/build.py`, or a new per-skill bundle? If the latter, must
  `tools/build.py` be amended to support it (and is the stored object gzip or raw tar)? Who owns that
  change before BSB-25-PENDING-2 can be built?
- **Proposed change:** Do **not** lock the divergent format into the story. Escalate to
  `sdlc-arch-design` (amend ADR SK-001 §5 and `tools/build.py`, or add a per-skill pack mode) to
  decide the bundle shape, then have `sdlc-plan-stories-write` (revise) restate BSB-25-PENDING-2's
  Notes/AC1 and BSB-25-PENDING-3's NFR-001 context from that decision. BSB-26 and BSB-31 must read the
  same answer.

### Finding 2 — Cross-story: the three-stage preparation pipeline has no short-circuit or orchestration contract
- **Severity:** Blocking
- **Stories touched:** BSB-25-PENDING-1, BSB-25-PENDING-2, BSB-25-PENDING-3.
- **Evidence:** BSB-25-PENDING-1 Notes order the stages resolver → PENDING-2 packager → PENDING-3 branch
  preparer, say "any stage failure sets `preparation_failed`", and say PENDING-3 sets `prepared` only
  after all three succeed (`stories.md:101-107`). But its own failure ACs only cover resolver failures,
  and its exactly-once AC counts resolver calls only (`stories.md:56-71`). BSB-25-PENDING-2's two
  failure ACs assert state, error text, no bundle row and 0 PutObject — they do **not** assert that the
  branch preparer was skipped or that `runs.run_branch`/`runs.baseline_sha` stay NULL
  (`stories.md:163-171`). BSB-25-PENDING-3 AC1 sets `prepared` with no precondition that a bundle row
  exists (`stories.md:229-232`), and PENDING-3's Notes claim "All preparation failures … leave
  `runs.run_branch` and `runs.baseline_sha` NULL, as the failure scenarios assert" (`stories.md:279-282`)
  — a guarantee PENDING-2's failure scenarios do not actually assert. The three stories also never say
  which component owns the sequence and the state transitions; each story's ACs assume the other stages
  behaved.
- **What is missing/ambiguous/contradictory:** A pack failure could still create the run branch and
  record a baseline (or a branch failure could leave a bundle row and still reach `prepared`); no AC
  stops the pipeline at the first failing stage; PENDING-3's "prepared only after all three" is prose,
  not a tested hand-off. With BSB-26 consuming `prepared`, the missing short-circuit is externally
  visible.
- **Question (if a person must decide):** Which component owns the resolver → packager → branch-preparer
  sequence and the `preparing`/`prepared`/`preparation_failed` transitions, and is the contract
  "stop at the first failure, never run a later stage"?
- **Proposed change:** For **BSB-25-PENDING-1**, state in Notes that the run worker owns the ordered
  three-stage sequence and stops at the first failure, and add to AC2 counters proving the packager and
  branch preparer ran exactly once on success. For **BSB-25-PENDING-2**, add to both failure ACs: the
  branch preparer is not called, no branch is created, and `runs.run_branch`/`runs.baseline_sha` are
  NULL. For **BSB-25-PENDING-3**, add a failure AC (or extend AC1) that the story refuses to prepare —
  leaves `run_branch` NULL, state unchanged — when no bundle row exists or the run is
  `preparation_failed`, so `prepared` cannot be reached without the earlier stages.

### Finding 3 — Cross-epic: the static-scan packaging gate is both unowned and ordered opposite to BSB-31's DoD
- **Severity:** Blocking
- **Stories touched:** BSB-25-PENDING-1, BSB-25-PENDING-2; cross-epic BSB-31-PENDING-1 and BSB-30.
- **Evidence:** BSB-31's epic DoD says "Every run and every packaged skill is preceded by a static scan
  of the exact content, and a non-passing verdict blocks the run and packaging" (`epics.md:556-557`).
  BSB-25-PENDING-1 Notes instead put the scan **after** preparation — i.e. after PENDING-2 has produced
  the bundle — because BSB-31-PENDING-1 reads the `skill_bundles` row (`stories.md:117-119`), and
  PENDING-1 lists BSB-31 as out of scope for this epic (`stories.md:177-196` region). BSB-31's review
  already records the packaging half of this gap as Finding 2 (Blocking) and asks BSB-25/BSB-30 to
  settle it (`docs/product/epics/BSB-31/_epic/epic-review.md`). BSB-30 owns the packaging preflight
  FR-071…FR-073 (`epics.md:979-1046`) but has no stories, and BSB-25-PENDING-2 only notes the preflight
  dependency (`stories.md:194`).
- **What is missing/ambiguous/contradictory:** "Preceded by a static scan" and "scan runs after
  preparation" cannot both be true; no BSB-25 story says whether a non-pass verdict blocks packaging
  (and nothing to do if it does, because the scan needs the bundle), and no story names the owner of
  the gate. Building PENDING-2 as written makes packaging ungated, silently contradicting BSB-31's DoD.
- **Question (if a person must decide):** Does a non-passing static scan block packaging for a run, and
  if so where does that check sit given that the scan consumes the `skill_bundles` row? Who owns the
  gate — BSB-25, BSB-30 or BSB-31 — and if packaging is deliberately not gated, is BSB-31's DoD the
  sentence that changes?
- **Proposed change:** Record the answer in BSB-25-PENDING-1/PENDING-2 Notes. If packaging is gated,
  add the gate and its owner to PENDING-1's sequence and a PENDING-2 refusal/ordering AC; if it is not,
  delete/narrow BSB-31's DoD sentence and state that packaging is not gated. Do not leave both
  statements standing. Cross-epic follow-up: BSB-30 and BSB-31 must adopt the same answer.

### Finding 4 — Cross-story: NFR-001's 60-second boundary does not say whether the static scan is inside it
- **Severity:** Advisory
- **Stories touched:** BSB-25-PENDING-3 (NFR-001 AC), with BSB-25-PENDING-1 and BSB-25-PENDING-2 owning
  the measured stages; cross-epic BSB-31-PENDING-1/-4.
- **Evidence:** NFR-001 says "Non-model run preparation completes within 60 seconds for a skill bundle
  of up to 5 MB" (`PRD.md:251`). PENDING-3 AC6 measures a 5,000,000-byte bundle with packer 35 s +
  PutObject 20 s + resolution/creation 4 s, clock 11:00:00Z → 11:00:59Z (`stories.md:254-257`), and
  PENDING-3 Notes define the measurement as "resolver, packer and branch preparer" and put the static
  scan after `prepared` (`stories.md:302-305`). BSB-31-PENDING-1's synchronous scan can run up to 600 s
  (`BSB-31/_epic/stories.md`, PENDING-1 ACs), and BSB-31's review Finding 7 (Advisory) records the same
  tension and asks BSB-25 to agree the budget.
- **What is missing/ambiguous/contradictory:** The PRD says "non-model run preparation"; a static scan
  is non-model work. PENDING-3's enumeration silently defines the scan out of the 60 s budget, but the
  PRD does not, and BSB-31's synchronous scan still sits on the run's critical path. A reader can
  legitimately conclude the combined path violates NFR-001 at 5 MB.
- **Question (if a person must decide):** Is the static scan part of "non-model run preparation" for
  NFR-001, or is it a separate post-`prepared` stage with its own budget? Does the 60 s cover only the
  resolver, packer and branch preparer?
- **Proposed change:** For **BSB-25-PENDING-3**, state the boundary explicitly in Notes ("NFR-001 covers
  the resolver, packer and branch preparer only; the static scan runs after `prepared` under BSB-31's
  budget") and make AC6's clock start/end name those stages. For **BSB-25-PENDING-1** and
  **BSB-25-PENDING-2**, add the same one-line boundary to their NFR notes so all three stories agree.
  Cross-epic follow-up: BSB-31 aligns PENDING-1/-4 to the same boundary; if the scan is inside the
  budget, NFR-001's 60 s must be raised in the PRD instead.

### Finding 5 — Epic boundary: the bundle identity the consumers look up does not match what PENDING-2 produces
- **Severity:** Advisory
- **Stories touched:** BSB-25-PENDING-2; epic output contract consumed by BSB-31-PENDING-1 and BSB-32.
- **Evidence:** BSB-25-PENDING-2 keys the row and reuse by `(skill, skills_commit_sha)`
  (`stories.md:203-210`), stores at `bundles/<skills_commit_sha>/<skill>.tar.gz`, and AC4 deliberately
  creates **two rows at one commit** for two skills (`stories.md:153-156`). Its Notes claim
  "BSB-31-PENDING-1 reads the `skill_bundles` row by `(skill, skills_commit_sha)`" (`stories.md:210`).
  BSB-31-PENDING-1's route takes only `{"project_id", "skills_commit_sha"}` and its Notes say it
  "reads the `skill_bundles` row for that SHA" (`BSB-31/_epic/stories.md:76`), with fixtures that use
  a SHA-only row and `s3_key "bundles/4f2c9a1.tar.gz"` (`BSB-31/_epic/stories.md:30-37`). BSB-32 uses
  the same SHA-only fixture (`BSB-32/_epic/stories.md:102,228`).
- **What is missing/ambiguous/contradictory:** PENDING-2's own model requires `skill` in the lookup,
  but the consumer stories it cites look up by commit only and use a different key shape. With two
  skills at one commit, the commit-only lookup is ambiguous; nothing in BSB-25 says which bundle a
  scan/execution targets. The key-shape difference is harmless if consumers read `s3_key` from the row,
  but the lookup identity is not.
- **Proposed change:** Correct **BSB-25-PENDING-2**'s Notes to say the consumer must resolve the build's
  `skill` and read by `(skill, skills_commit_sha)`, and note that the object key is an implementation
  detail read from the row. Cross-epic follow-up (not applied here): BSB-31-PENDING-1 and BSB-32 must
  add `skill` to the lookup and align their `s3_key` fixtures; this is an alignment, not a product
  decision, so no question blocks it.

### Finding 6 — Epic boundary: the isolation rule protects only `input_branch`; writes to `main` are unowned
- **Severity:** Advisory
- **Stories touched:** BSB-25-PENDING-3; epic non-goal; cross-epic BSB-26 (the writer's consumer).
- **Evidence:** The epic non-goal says the epic does not write "to the input branch or `main`"
  (`epics.md:739`), and ADR SK-001's test list says "A run never pushes to its input branch; the output
  always goes to `skilltest/<run-id>`" (`SK-001:418`). BSB-25-PENDING-3's Notes define the writer as
  refusing "any write whose target ref equals `runs.input_branch`" and routing every run-time write to
  `runs.run_branch` (`stories.md:288-290`), but AC5 tests only a write to the input branch
  (`stories.md:249-252`); no AC refuses `refs/heads/main`.
- **What is missing/ambiguous/contradictory:** "Never write `main`" is asserted at epic level but is
  not a rule in the story that owns the writer. A writer that only compares against `input_branch`
  would allow a `main` push; BSB-26 inherits that writer.
- **Question (if a person must decide):** Is the rule "refuse any target other than
  `runs.run_branch`" (deny-by-default) or only "refuse `runs.input_branch`"? If `main` must be
  protected, is that a separate check or a consequence of the first rule?
- **Proposed change:** For **BSB-25-PENDING-3**, state the deny-by-default rule in Notes ("the only
  accepted target is `runs.run_branch`; every other ref, including `main`, is refused") and add an AC
  that a write to `refs/heads/main` is rejected with the same error. Cross-epic follow-up: BSB-26 must
  use that writer and add its own `main`-refusal case.

### Finding 7 — Cross-epic dependency assumed but undischarged: the source-control credential's test-purpose check
- **Severity:** Advisory
- **Stories touched:** BSB-25-PENDING-1, BSB-25-PENDING-2; cross-epic BSB-24-PENDING-1, BSB-23-PENDING-6.
- **Evidence:** PENDING-1 and PENDING-2 read the source-control integration and its secret to resolve and
  pack (`stories.md:88-93,188-191,208-211`), and both call it the "test-purpose" integration. But neither
  story's ACs assert that a non-test-purpose integration is refused; they assume run start admitted one.
  BSB-24-PENDING-1's review records that the test-purpose admission check is unowned as Finding 3
  (Blocking) (`BSB-24/_epic/epic-review.md`), and BSB-23-PENDING-6 owns the run-purpose list
  (NFR-006). The assumption therefore currently has no owner.
- **What is missing/ambiguous/contradictory:** If BSB-24's Finding 3 is not applied, preparation will
  read a credential belonging to a non-test repository. BSB-25's Notes mention "test-purpose" but do not
  name the upstream check they rely on, so the dependency is silent in the form the checklist requires.
- **Question (if a person must decide):** Is the test-purpose admission guaranteed at run start (BSB-24 /
  BSB-23-PENDING-6), or must preparation re-check `config.test_only` before reading the credential?
- **Proposed change:** For **BSB-25-PENDING-1** and **BSB-25-PENDING-2**, add to Notes: "Depends on
  BSB-24-PENDING-1 / BSB-23-PENDING-6 admitting only a test-purpose integration; preparation does not
  re-check it." If the answer is that preparation must check, add a refusal AC to both stories. Cross-epic
  follow-up: BSB-24's Finding 3 must be applied; BSB-25 cannot discharge it.

## Open questions

1. **Bundle shape (Finding 1).** Whole-catalog release artifact per ADR SK-001 §5 and `tools/build.py`,
   or a new per-skill bundle? If per-skill, does `tools/build.py` gain a mode, and is the stored object
   gzip or raw tar? Needs `sdlc-arch-design` (amend).
2. **Pipeline ownership (Finding 2).** Which component owns resolver → packager → branch preparer and
   the state transitions, and is the contract "stop at the first failure"?
3. **Packaging gate (Finding 3).** Does a non-passing static scan block packaging, who owns the gate,
   and if packaging is not gated, does BSB-31's DoD change?
4. **NFR-001 boundary (Finding 4).** Is the static scan inside the 60-second non-model preparation
   budget, or a separate post-`prepared` stage?
5. **Isolation scope (Finding 6).** Deny-by-default (`runs.run_branch` only) or only refuse
   `runs.input_branch`; is `main` protected by the writer?
6. **Test-purpose admission (Finding 7).** Guaranteed at run start by BSB-24/BSB-23-PENDING-6, or
   re-checked by preparation?

## Proposed changes

These are proposals only — nothing in `stories.md`, the story map, the PRD, the ADR or Jira was
changed by this review.

- **BSB-25-PENDING-1**
  - Notes: name the run worker as owner of the ordered three-stage sequence; state "stop at the first
    failure — a later stage never runs after an earlier one fails"; state the static-scan ordering
    decision from Finding 3 and the NFR-001 boundary from Finding 4; add the test-purpose dependency
    line from Finding 7.
  - AC2: add packager-called-once and branch-preparer-called-once counters.
  - If Finding 3 says packaging is gated: add the gate, its owner, and the resulting ordering/refusal.
- **BSB-25-PENDING-2**
  - Restate the bundle content/format from the Finding 1 architecture decision (or hold the story
    until that decision lands).
  - Failure ACs (AC6, AC7): add "the branch preparer is not called", "no branch is created",
    "`runs.run_branch` and `runs.baseline_sha` are NULL".
  - Notes: correct the BSB-31 lookup to `(skill, skills_commit_sha)` and say the object key is read
    from the row (Finding 5); add the test-purpose dependency line from Finding 7; state the NFR-001
    boundary from Finding 4.
  - If Finding 3 says packaging is gated: add the gate/ordering and the corresponding AC.
- **BSB-25-PENDING-3**
  - Notes: state the NFR-001 boundary explicitly and name the measured stages in AC6 (Finding 4);
    state the deny-by-default isolation rule (Finding 6).
  - AC1 (or a new failure AC): refuse to prepare when no bundle row exists or the run is
    `preparation_failed`, so `prepared` cannot be reached without the earlier stages (Finding 2).
  - AC5: add a write to `refs/heads/main` that is refused (Finding 6).
- **Cross-epic follow-ups (recorded here, not applied)**
  - `sdlc-arch-design` (amend): decide the bundle content/format and update ADR SK-001 §5 and/or
    `tools/build.py` (Finding 1).
  - BSB-30 / BSB-31: agree the packaging gate and the scan-ordering answer (Finding 3); align
    BSB-31-PENDING-1/-4 to the NFR-001 boundary (Finding 4).
  - BSB-31-PENDING-1 / BSB-32: resolve the build's `skill` and read `skill_bundles` by
    `(skill, skills_commit_sha)`; align fixture `s3_key` values (Finding 5).
  - BSB-26: use PENDING-3's writer and add a `main`-refusal case (Finding 6).
  - BSB-24-PENDING-1 / BSB-23-PENDING-6: discharge the test-purpose admission check (Finding 7).

## Architecture impact

**Architecture conflict — escalated, not story-fixable.** Finding 1 conflicts with ADR SK-001 §5
("packed with `tools/build.py` … exactly as a release would pack it") and with the actual
`tools/build.py` behavior (whole-catalog `skills/` + `config/` + `catalog.yaml`, gzipped
`dist/catalog.tgz`) versus BSB-25-PENDING-2's per-skill, config-free, uncompressed tar. Resolving it
requires `sdlc-arch-design` to **amend** ADR SK-001 §5 and/or extend `tools/build.py` before the story
pass can restate the bundle contract. BSB-26 (execution) and BSB-31 (scan) consume the same answer.
No other architecture change is implied by the remaining findings.

## Requirement coverage check

- **FR-038** — BSB-25-PENDING-1: AC1 resolve+freeze, AC2 exactly-once pickup, AC3 re-resolution keeps
  the frozen commit, AC4 missing skills branch fails, AC5 provider 503 fails. Covered.
- **FR-039** — BSB-25-PENDING-2 AC1 (per-skill bundle), AC4 (second skill gets its own bundle).
  Covered.
- **FR-040** — BSB-25-PENDING-2 AC2 (same key reuses the stored object, 0 PutObject), AC4 (different
  skill at the same commit builds its own). Covered.
- **FR-041** — BSB-25-PENDING-3 AC1/AC2 (run branch from the input head, baseline recorded).
  Covered.
- **FR-042** — BSB-25-PENDING-3 AC1/AC2 (baseline = input head). Covered.
- **FR-043** — BSB-25-PENDING-3 AC5 (input-branch write refused; run-branch write accepted). Covered.
- **NFR-001** — BSB-25-PENDING-3 AC6 (5 MB, 59 s, no model call). Covered, but the scan boundary is
  Finding 4.
- **NFR-009** — BSB-25-PENDING-2 AC5 (two runs of the same packed commit produce identical archive
  bytes). Covered.
- **No requirement is claimed by two stories.** The map and PRD ids agree; no PRD text drift was found
  in FR-038…FR-043, NFR-001 or NFR-009. NFR-004 and NFR-006 belong to BSB-23; there is no UI in this
  epic, so NFR-012 is not applicable. NFR-001's AC necessarily spans all three stages but is mapped
  once, to PENDING-3, which is correct.

## Dependency-note sanity check

- **All referenced keys exist.** Within the epic: BSB-25-PENDING-1/-2/-3. Cross-epic:
  BSB-18, BSB-19-PENDING-3, BSB-23-PENDING-2/-6, BSB-24-PENDING-1, BSB-26, BSB-27, BSB-29,
  BSB-30, BSB-31-PENDING-1, BSB-33, BSB-34, BSB-36, BSB-37. No note points at a non-existent story.
  References to epics with no stories yet (BSB-26, BSB-27, BSB-29, BSB-30, BSB-33, BSB-34, BSB-36,
  BSB-37) are recording cross-epic dependencies for the sequence stage, not dangling story keys.
- **Reciprocity is good where it is required.** BSB-24-PENDING-1 names BSB-25 for `skills_commit_sha`
  and the run branch, and BSB-31-PENDING-1 names BSB-25 for the bundle row. BSB-19-PENDING-3 and
  BSB-23-PENDING-2/-6 are upstream suppliers and do not need a reverse note.
- **Ordering reconciliation is recorded.** PENDING-1's "static scan after preparation" note is the
  same reconciliation the BSB-24 review records (BSB-27's "before a bundle or branch is prepared"
  wording is the outlier); PENDING-2's packaging note must still be reconciled with BSB-31's DoD —
  that is Finding 3, not a missing key.
- **Finding 5** is the one inaccurate dependency claim: PENDING-2 says BSB-31-PENDING-1 reads by
  `(skill, skills_commit_sha)`, but that story and BSB-32 read by commit only. Correct PENDING-2's
  wording and align the consumers.
- **Carry-forwards, not BSB-25 defects.** BSB-24-PENDING-1's fixtures still use `bug-fix-resolver`,
  which BSB-19-PENDING-3's naming rule rejects (BSB-24 review Finding 7); BSB-24's review Finding 3
  leaves the test-purpose check unowned (BSB-25 Finding 7). BSB-25's own fixture names
  (`sdlc-fix-bug-reproduce`, `sdlc-fix-bug-triage`) satisfy BSB-19-PENDING-3's rule.
- **No build order is computed here.** With no epic-sequence files for BSB-25 and BSB-30 having no
  stories, ordering belongs to `sdlc-plan-epic-sequence` after the Blocking findings are applied.
