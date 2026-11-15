# Stories — BSB-29 (Run verification & verdicts)

Source: Jira epic **BSB-29** — *Run verification & verdicts* (feature area FA-10, release MVP,
labels FA-10, MVP), fetched read-only from the Atlassian project `bheembhai-skill-builder`; its
summary, description, functional scope, goal and stated edge cases are the same as the BSB-29
section of `docs/product/epics.md`. The requirement IDs mapped to the epic are in
`docs/product/epic-map.json`.

Epic BSB-29 covers 8 requirements. They decompose into the 4 stories below; every requirement is
covered by at least one story and no story claims a requirement outside this epic.

The run labelled the target `SkillBuilder`, which is the product title in `docs/product/PRD.md`,
not a Jira issue. The Atlassian project `bheembhai-skill-builder` contains only the epic issues
BSB-18 to BSB-38; this run's item, from the workflow context (`ITEM.id` = `BSB-29`), is epic
**BSB-29**. The Atlassian MCP entry in `.mcp.json` is not usable in this session: its `args` value
is a string where Claude Code requires an array, so the server is skipped as invalid. The epic was
therefore fetched read-only through the Atlassian REST API with the same credentials. Nothing was
written to Jira.

## Coverage summary

| Requirement | Covered by |
|-------------|------------|
| FR-063 | BSB-29-PENDING-1 |
| FR-064 | BSB-29-PENDING-1 |
| FR-065 | BSB-29-PENDING-2 |
| FR-066 | BSB-29-PENDING-2, BSB-29-PENDING-3 |
| FR-067 | BSB-29-PENDING-2 |
| FR-153 | BSB-29-PENDING-1 |
| FR-164 | BSB-29-PENDING-2, BSB-29-PENDING-3 |
| NFR-010 | BSB-29-PENDING-4 |

The epic's three stated edge cases are covered explicitly: a verifier that cannot run
(BSB-29-PENDING-3), a verifier that returns no verdict (BSB-29-PENDING-3) and a verifier that
returns a verdict for the wrong baseline (BSB-29-PENDING-3). Each is recorded as a verification
failure, never as a pass.

## Verification contract (test fixture constants)

Every scenario below starts from this fixed deployment, database, source-control and object-store
fixture unless it says otherwise. The member session, the local `users` rows and the
`skill-builders` gate are established by epic BSB-18. The project, `projects` rows and
`project_members` rows are established by epic BSB-22. The integrations are established by epic
BSB-23. The prepared runs — the `runs` rows with `skills_commit_sha`, `run_branch` and the
`skill_bundles` row — are the output of epic BSB-25 (FR-038 to FR-043); the terminal states and
`claimed_verdict` are the output of epics BSB-26 and BSB-27. This epic consumes them. The `runs`
and `skill_bundles` columns follow `docs/adr/SK-001-skill-builder.md` §5 and §9.

| Item | Exact value |
|------|-------------|
| Builder base URL | `https://builder.skillbuilder.internal` |
| Session cookie | `sb_session`, holding a Cognito ID token JWT with claims `sub`, `email`, `name`, `cognito:groups`=`["skill-builders"]`, `iss`=`https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_SBExample`, `aud`=`skill-builder-web` and `exp`=`2026-11-15T11:00:00Z` |
| User Ada | `users.id` = `42`, `cognito_sub` = `a1b2c3d4-0000-0000-0000-000000000001`, `email` = `ada@example.com`, `name` = `Ada Lovelace` |
| User Grace | `users.id` = `43`, `cognito_sub` = `b2c3d4e5-0000-0000-0000-000000000002`, `email` = `grace@example.com`, `name` = `Grace Hopper` |
| `projects` fixture | exactly ten rows with ids `1` to `10`; id `7` has `name` = `Payment regression`, `owner_id` = `42`, `created_at` = `2026-11-14T09:00:00Z`; ids `1` to `6`, `8`, `9` and `10` are unrelated fixture projects |
| `project_members` fixture | exactly three rows: `(project_id 7, user_id 42, role owner)`, `(project_id 7, user_id 43, role member)` and `(project_id 8, user_id 43, role owner)`; Alan has no row for project `7` |
| `skills_commit_sha` | `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b` for every run below |
| `baseline_sha` | `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09` for every run below |
| `input_branch` | `main` for every run below |
| `skill` | `sdlc-fix-bug-triage` for every run below |
| `skill_bundles` row | `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `skill` = `sdlc-fix-bug-triage`, `bundle_sha256` = `b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`, `s3_key` = `bundles/4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b/sdlc-fix-bug-triage.tar.gz` |
| `verify.yaml` at the skills commit | the file `skills/sdlc-fix-bug-triage/verify.yaml` inside the bundle; its SHA-256 is `c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0` |
| Modified `verify.yaml` on run `1`'s branch | the agent committed a changed `skills/sdlc-fix-bug-triage/verify.yaml` to `skilltest/1`; its SHA-256 is `e1d2c3b4a5f60718293a4b5c6d7e8f901a2b3c4d5e6f708192a3b4c5d6e7f809` |
| Object-store bucket | `skill-builder-runs` |
| Current `skill-builder/kit.txt` | exactly `kit-v8` |
| `kit.json` for `kit-v8` | `{"kit":"kit-v8","env_contract_version":"4","bheembhai-stepkit":"0.5.0","bheembhai-verify":"2.2.0","agent_image":"123456789012.dkr.ecr.eu-west-1.amazonaws.com/bheembhai-agent@sha256:8f1e3a5c7b9d2f4e6a8c0b1d3f5e7a9c2b4d6f8e0a1c3b5d7f9e2a4c6b8d0f13"}` |
| Verification worker | a builder process polling every 1 second |
| Verification container | separate from the agent container; labelled `bb.verify_run_id` = the run id and never labelled `bb.run_id` |
| Verifier distribution | the pinned shared verification layer at the run's `runs.verify_version`; it exposes the `verify.py precheck` and `verify.py verify` commands |
| Verification block | the shared layer's JSON block: `schema`, `skill`, `status`, `self`, `final`, `reason`, `overridden`, `manifest_present`, `manifest_sha256`, `snapshot`, `checks`, `errors` |
| Verification inputs | the builder records `{"run_branch_sha": "<40 hex>", "baseline_sha": "<40 hex>", "bundle_sha256": "<64 hex>", "verify_version": "<x.y.z>", "self_verdict": "<verdict>"}` |
| Success status | HTTP 200 with `Content-Type: text/html; charset=utf-8` for the run page; HTTP 200 with `Content-Type: application/json` for builder APIs |
| Error body shape | `{"error":{"code":"code_value","message":"message text"}}` |
| Current time | `2026-11-15T10:10:00Z`, after every run below is terminal |

**Run fixtures.** Every row also has `project_id` = `7`, `user_id` = `42`, `input_branch` = `main`,
`final_verdict` = `NULL` and `verification` = `NULL` before the scenario starts. `created_at`
follows the run id: run `1` is `2026-11-15T10:00:00Z`, run `2` is one second later, and so on.

| Run | `runs.state` | `runs.claimed_verdict` | `runs.verify_version` | `run_branch` | run-branch head SHA | Purpose |
|-----|--------------|------------------------|-----------------------|--------------|---------------------|---------|
| `1` | `completed` | `completed` | `2.1.2` | `skilltest/1` | `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e` | main verified run; its branch carries the modified `verify.yaml` |
| `2` | `completed` | `completed` | `2.2.0` | `skilltest/2` | `7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f` | a run pinned to a different verifier version |
| `3` | `completed` | `BLOCK` | `2.1.2` | `skilltest/3` | `8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a` | an honest BLOCK claim |
| `4` | `failed_execution` | `NULL` | `2.1.2` | `skilltest/4` | `9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b` | runtime exited without a claim |
| `5` | `failed_infra` | `NULL` | `2.1.2` | `skilltest/5` | `0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c` | runtime never started |
| `6` | `running` | `NULL` | `2.1.2` | `skilltest/6` | `1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d` | not terminal |
| `7` | `completed` | `changes_requested` | `2.1.2` | `skilltest/7` | `2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e` | a non-completed claim |
| `8` | `failed_timeout` | `NULL` | `2.1.2` | `skilltest/8` | `3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f` | runtime started, then the deadline stopped it |
| `9` | `completed` | `completed` | `2.1.2` | `skilltest/9` | `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e` | determinism twin of run `1`: same tree, baseline, manifest and verifier version |

Run `9`'s branch points at the same commit as run `1`'s branch; the two runs therefore have the
same run-branch head SHA while remaining separate `runs` rows.

**Which runs are verified.** A verification worker claims a run only when all of these hold:

- `runs.state` is a terminal state reached after a runtime started: `completed`,
  `failed_execution`, `failed_incomplete`, `failed_timeout`, or epic BSB-27's turn/spend-cap
  terminal state (its exact name is owned by BSB-27 and is added to this set by its stories).
- `runs.final_verdict IS NULL` and `runs.verification IS NULL`.
- No other worker holds the run's advisory lock: `pg_try_advisory_lock(runs.id)` succeeds.

`failed_infra` (run `5`), epic BSB-25's preparation-failure state and epic BSB-28's `failed_seed`
are terminal before a runtime starts; they are never claimed and their `final_verdict` stays
`NULL`. A run in `queued` or `running` is never claimed.

**Verification adapter contract.** For a claimed run the worker performs these steps in order,
all outside the agent container:

1. Resolve the current head SHA of `run_branch` and record it as `verification.inputs.run_branch_sha`.
2. Check out `runs.baseline_sha` at `/var/lib/skill-builder/verify/<run id>/baseline` and the
   run-branch head at `/var/lib/skill-builder/verify/<run id>/run`.
3. Download the bundle named by `skill_bundles.s3_key` for `runs.skills_commit_sha` to
   `/var/lib/skill-builder/verify/<run id>/bundle.tar.gz` and verify its SHA-256 equals
   `skill_bundles.bundle_sha256` (`b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`).
4. Run the pinned shared layer at `runs.verify_version`:
   `verify.py precheck --repo /var/lib/skill-builder/verify/1/baseline --bundle /var/lib/skill-builder/verify/1/bundle.tar.gz --skill sdlc-fix-bug-triage --skill-sha b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a --out precheck.json`
   then
   `verify.py verify --repo /var/lib/skill-builder/verify/1/run --bundle /var/lib/skill-builder/verify/1/bundle.tar.gz --skill sdlc-fix-bug-triage --skill-sha b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a --self-verdict <self> --baseline precheck.json --out verify.json`.
   The run id in those paths is the claimed run's id.
5. The shared layer reads `verify.yaml` from `bundle.tar.gz`, never from either checkout. It
   records the manifest's SHA-256 as `verification.manifest_sha256` and the baseline checkout's
   `HEAD` as `verification.snapshot.head_sha`.
6. The verifier distribution is the one pinned at `runs.verify_version`; `kit.txt` at verification
   time is not consulted.
7. `<self>` is `runs.claimed_verdict` when it is not `NULL`, otherwise the exact string
   `failed_execution`. The value actually passed is recorded as
   `verification.inputs.self_verdict`.

**Stored verification record.** `runs.verification` holds the shared layer's block verbatim, plus
an `inputs` object with the five values above. `runs.final_verdict` is written in the same update.

| Shared layer result | `runs.final_verdict` | `runs.verification` |
|---------------------|----------------------|---------------------|
| `status` is `passed` or `failed` and `final` is one of `completed`, `BLOCK`, `changes_requested`, `escalation_required`, `failed_execution` | `final`, verbatim | the block, verbatim, plus `inputs` |
| `status` is `unverified` | `unverified` | the block, verbatim, plus `inputs` |
| the process writes no readable output file, exits non-zero, or exceeds the verifier timeout | `unverified` | a block with `status` = `unverified`, `reason` = `verifier_crashed`, `self` = `<self>`, `final` = `<self>`, `overridden` = `false`, `errors` = the process error, plus `inputs` |
| the output has no string `status` or no string `final` | `unverified` | a block with `status` = `unverified`, `reason` = `no_verdict`, `received` = the output, plus `inputs` |
| `final` is not one of the five verdicts above | `unverified` | a block with `status` = `unverified`, `reason` = `invalid_verdict`, `received` = the output, plus `inputs` |
| `snapshot.head_sha` is not exactly `runs.baseline_sha` | `unverified` | a block with `status` = `unverified`, `reason` = `baseline_mismatch`, `received` = the output, plus `inputs` |

**Pass predicate.** A run passes verification only when
`runs.final_verdict = 'completed'` **and** `runs.verification->>'status' = 'passed'`.
`final_verdict` = `unverified` is never a pass; `NULL` is never a pass. Epic BSB-30's Ready check
and epic BSB-33's run report consume this predicate.

**Decisions recorded in this decomposition (confirm at review).**

1. The shared layer is fail-open: when it cannot grade, its block carries `status` = `unverified`
   and `final` = the self verdict. Recording that `final` literally would let a failed verification
   read as a pass, which the epic forbids. This decomposition therefore records
   `runs.final_verdict` = `unverified` in that case and keeps the block in `runs.verification`.
2. `runs.baseline_sha` is the value epic BSB-25 records under FR-042. BSB-25 has no stories yet;
   this epic consumes the value and the adapter reads it from the run record. If BSB-25 stores it
   under a different name, only the adapter's read changes.
3. `runs.verify_version` is written by epic BSB-26-PENDING-4 from the kit pin at claim time. The
   builder must be able to run the shared layer at that version; if the pinned distribution ships
   only the manifest package, the verification executor is an external prerequisite to confirm
   with architecture.
4. When epic BSB-28 is present, its Jira finalizer runs before verification (BSB-28's stories
   require it). The verification claim predicate then also requires the run's finalizer to be
   complete: `run_jira.cleaned_at IS NOT NULL`, or no `run_jira` row for the run. In the MVP,
   where BSB-28 is absent, this condition is vacuous.

## Cross-epic notes

- **BSB-25.** Supplies `skills_commit_sha`, the `skill_bundles` row and the baseline SHA. This epic
  never packs a bundle or creates a branch.
- **BSB-26.** Writes every terminal state except `failed_timeout`, records `claimed_verdict` and
  `verify_version`, and deliberately leaves `final_verdict` and `verification` `NULL` for this
  epic. The terminal-write rule (first writer wins) is unchanged; verification is a read after it.
- **BSB-27.** Owns `failed_timeout` and the turn/spend-cap terminal state. Its terminal states are
  runtime-terminal and are verified here; verification never changes a run's state.
- **BSB-28.** Later release. Its finalizer runs after the terminal write and before verification;
  its `failed_seed` state is pre-runtime and is never verified. This epic does not read or write
  `run_jira`.
- **BSB-30.** Readiness consumes the pass predicate above. A run counts as passing only with
  `final_verdict` = `completed` and `verification.status` = `passed`.
- **BSB-33.** Displays the final verdict on the run page (FR-158) and owns the full run report;
  this epic only records the values.
- **BSB-34.** Owns retention and purge; `runs.verification` is run-result data and must be covered
  by its purge.
- **BSB-35.** Compares verdicts across runs; it reads `final_verdict` and `verification`.
- **BSB-18, BSB-22 and BSB-23.** Every builder route is behind BSB-18's session and
  `skill-builders` gate and BSB-22's project-membership check; the source-control and object-store
  access this epic uses comes from BSB-23's integrations and the installation's bucket.

---

## STORY: BSB-29-PENDING-1

**Summary:** Grade a terminated run with the pinned shared verifier
**Epic:** BSB-29 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **every run that exited its runtime to be graded by the same pinned shared verification layer the platform uses, with the run's own baseline and the skills-commit manifest**, so that **the verdict is independent of the agent and comparable with a platform run**.

### Acceptance Criteria

#### Scenario: A completed run is verified after its agent container exits
Given run `1` exists with `state` = `completed`, `claimed_verdict` = `completed` and the contract's `baseline_sha`, `run_branch` and `verify_version`
And the `skill_bundles` row and bundle object exist as in the contract
And the verification worker is running with a 1-second poll
When the worker's next poll happens at `2026-11-15T10:10:01Z`
Then within 2 seconds the verification container labelled `bb.verify_run_id` = `1` is started
And no container labelled `bb.run_id` = `1` is running when that verification container starts
And that verification container has no `bb.run_id` label
And within 2 seconds of the verifier exiting `SELECT final_verdict, verification->>'status', verification->>'reason' FROM runs WHERE id = 1` returns exactly `completed | passed | ok`

#### Scenario: The verifier receives the run's baseline SHA
Given run `1` exists as in the contract
And the shared layer returns a passing block whose `snapshot.head_sha` is exactly `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09`
When verification completes
Then `SELECT verification->'inputs'->>'baseline_sha', verification->'snapshot'->>'head_sha' FROM runs WHERE id = 1` returns exactly `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09 | 9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09`
And the checkout at `/var/lib/skill-builder/verify/1/baseline` has `HEAD` exactly `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09`

#### Scenario: The verifier receives the verify.yaml from the skills commit, not the run branch
Given run `1` exists as in the contract
And the run branch `skilltest/1` contains the modified `skills/sdlc-fix-bug-triage/verify.yaml` with SHA-256 `e1d2c3b4a5f60718293a4b5c6d7e8f901a2b3c4d5e6f708192a3b4c5d6e7f809`
When verification completes
Then `SELECT verification->>'manifest_sha256', verification->'inputs'->>'bundle_sha256' FROM runs WHERE id = 1` returns exactly `c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0 | b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a`
And the verifier's manifest path is inside `/var/lib/skill-builder/verify/1/bundle.tar.gz`
And the verifier never reads `skills/sdlc-fix-bug-triage/verify.yaml` from `/var/lib/skill-builder/verify/1/run`

#### Scenario: The verifier uses the run's recorded verify_version, not the current kit pin
Given the contract's `kit.txt` contains `kit-v8` and its `kit.json` reports `bheembhai-verify` = `2.2.0`
And run `1` exists with `verify_version` = `2.1.2`
When verification completes
Then `SELECT verification->'inputs'->>'verify_version' FROM runs WHERE id = 1` returns exactly `2.1.2`
And the verification container's verifier distribution reports version exactly `2.1.2`

#### Scenario: A run whose runtime never started is not verified
Given run `5` exists with `state` = `failed_infra`
And run `6` exists with `state` = `running`
And the verification worker is running with a 1-second poll
When the worker performs three poll passes
Then `SELECT final_verdict, verification FROM runs WHERE id = 5` returns exactly `NULL | NULL`
And `SELECT final_verdict, verification FROM runs WHERE id = 6` returns exactly `NULL | NULL`
And no verification container labelled `bb.verify_run_id` = `5` or `bb.verify_run_id` = `6` is started

#### Scenario: A run stopped by the deadline is still verified
Given run `8` exists with `state` = `failed_timeout` and `claimed_verdict` = `NULL`
And the shared layer returns a block with `status` = `passed`, `final` = `failed_execution` and `reason` = `ok`
When the worker's next poll happens
Then within 2 seconds `SELECT final_verdict, verification->'inputs'->>'self_verdict', verification->>'status' FROM runs WHERE id = 8` returns exactly `failed_execution | failed_execution | passed`
And `SELECT claimed_verdict FROM runs WHERE id = 8` still returns `NULL`

### Covered requirements (traceability)
- FR-063
- FR-064
- FR-153

### Out of scope
Writing the terminal `runs.state`, the `claimed_verdict` or the `verify_version` (epic BSB-26, FR-047 and FR-151). Creating the run branch, resolving the skills commit and recording the baseline (epic BSB-25, FR-038 to FR-043). Choosing the verifier's builtin checks or changing them (external `bheembhai-verify` release). Deciding the run outcome (epic BSB-26). Turn and spend caps, the deadline and re-runs (epic BSB-27). Displaying the verdict on the run page or in a report (epic BSB-33, FR-158). Readiness aggregation (epic BSB-30). Retention and purge of the verification record (epic BSB-34).

### Notes / dependencies
- Depends on epic BSB-25 for `skills_commit_sha`, the `skill_bundles` row and the baseline SHA; on
  epic BSB-26 for the terminal state, `claimed_verdict` and `verify_version`; on epic BSB-27 for
  `failed_timeout`; and on the external shared verification layer pinned by `verify_version`.
- The worker never changes `runs.state`. A run remains `completed`, `failed_execution`,
  `failed_incomplete` or `failed_timeout` after verification; only `final_verdict` and
  `verification` change.
- The precheck phase is run at the baseline commit so the shared layer's `must_change` and
  artifact contract compare the run branch against the state the run started from. A precheck
  abort is recorded as a verification failure by BSB-29-PENDING-3.
- The verification container is started after the agent container has exited and has read access
  to a fresh checkout and the bundle, not to the agent's working container. The agent may change
  the run branch (that is the run's output); it cannot change the bundle or the verifier.
- A run verified under one verifier version is never re-verified under another. Epic BSB-30's
  re-verify path is a separate `reverify` run and is out of scope here.

---

## STORY: BSB-29-PENDING-2

**Summary:** Record claimed, final and overturned verdicts
**Epic:** BSB-29 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **the verdict the agent claimed, the final verdict the shared layer produced, and whether verification overturned the claim all recorded on the run**, so that **I can see exactly what the agent claimed and what an independent check decided**.

### Acceptance Criteria

#### Scenario: A verified pass records the claimed, final and overturn values
Given run `1` exists with `claimed_verdict` = `completed`
And the shared layer returns a block with `status` = `passed`, `self` = `completed`, `final` = `completed`, `reason` = `ok` and `overridden` = `false`
When verification completes
Then `SELECT final_verdict, claimed_verdict, verification->>'self', verification->>'final', verification->>'overridden' FROM runs WHERE id = 1` returns exactly `completed | completed | completed | completed | false`

#### Scenario: A verification failure overturns a completed claim
Given run `1` exists with `claimed_verdict` = `completed`
And the shared layer returns a block with `status` = `failed`, `self` = `completed`, `final` = `changes_requested`, `reason` = `checks_failed` and `overridden` = `true`
When verification completes
Then `SELECT final_verdict, claimed_verdict, verification->>'overridden' FROM runs WHERE id = 1` returns exactly `changes_requested | completed | true`
And `SELECT verification->>'reason' FROM runs WHERE id = 1` returns exactly `checks_failed`

#### Scenario: An honest BLOCK claim survives verification
Given run `3` exists with `claimed_verdict` = `BLOCK`
And the shared layer returns a block with `status` = `passed`, `self` = `BLOCK`, `final` = `BLOCK`, `reason` = `self_verdict` and `overridden` = `false`
When verification completes
Then `SELECT final_verdict, claimed_verdict, verification->>'overridden' FROM runs WHERE id = 3` returns exactly `BLOCK | BLOCK | false`

#### Scenario: A run with no claimed verdict is verified without inventing a claim
Given run `4` exists with `state` = `failed_execution` and `claimed_verdict` = `NULL`
And the shared layer receives `self_verdict` = `failed_execution`
And the shared layer returns a block with `status` = `passed`, `self` = `failed_execution`, `final` = `failed_execution`, `reason` = `ok` and `overridden` = `false`
When verification completes
Then `SELECT final_verdict, claimed_verdict, verification->'inputs'->>'self_verdict', verification->>'overridden' FROM runs WHERE id = 4` returns exactly `failed_execution | NULL | failed_execution | false`

#### Scenario: A non-completed claim is recorded as claimed and as final without being softened
Given run `7` exists with `claimed_verdict` = `changes_requested`
And the shared layer returns a block with `status` = `passed`, `self` = `changes_requested`, `final` = `changes_requested`, `reason` = `ok` and `overridden` = `false`
When verification completes
Then `SELECT final_verdict, claimed_verdict, verification->>'overridden' FROM runs WHERE id = 7` returns exactly `changes_requested | changes_requested | false`

#### Scenario: Two verification workers verify a run exactly once
Given run `1` exists as in the contract
And two verification workers `A` and `B` are running with a 1-second poll
When both workers perform their next poll at the same moment
Then exactly one verification container labelled `bb.verify_run_id` = `1` is started
And exactly one verifier process runs against run `1`
And `SELECT count(*) FROM runs WHERE id = 1 AND final_verdict IS NOT NULL AND verification IS NOT NULL` returns `1`
And the losing worker starts no verification container for run `1`

### Covered requirements (traceability)
- FR-065
- FR-066
- FR-067
- FR-164

### Out of scope
Running the shared layer, assembling its inputs and choosing its verifier version (BSB-29-PENDING-1). Recording a verification failure or an invalid result (BSB-29-PENDING-3). Recomputing the claimed verdict or reading `bb_step_result.json` (epic BSB-26, FR-047). Deciding whether the verifier's checks should have passed (external `bheembhai-verify` release). Showing the verdicts on the run page (epic BSB-33, FR-158). Readiness decisions (epic BSB-30). Comparing verdicts across runs (epic BSB-35).

### Notes / dependencies
- Depends on BSB-29-PENDING-1 for the verification run and its inputs, and on epic BSB-26 for
  `runs.claimed_verdict`. The claimed verdict is read, never recomputed or overwritten.
- `verification.overridden` is the shared layer's overturn flag: it is `true` when the final
  verdict differs from the verdict passed as `self`. For a run whose `claimed_verdict` is `NULL`,
  the self verdict is `failed_execution`, so a final verdict of `failed_execution` is not an
  overturn.
- `runs.final_verdict` is exactly the shared layer's `final` when its `status` is `passed` or
  `failed`. The builder does not substitute, round or infer a verdict; FR-164 is a verbatim copy.
- `final_verdict` and `verification` are written in one update. A run never has one without the
  other after a completed verification attempt.
- The pass predicate is `final_verdict` = `completed` and `verification.status` = `passed`. A
  verified `BLOCK` or `changes_requested` is a real, non-overturned verdict, not a failure to
  record.
- The two workers claim with `pg_try_advisory_lock(runs.id)` held for the verification; the lock
  is released when the worker exits. Epic BSB-33's run page reads the row after the update.

---

## STORY: BSB-29-PENDING-3

**Summary:** Record verification failures as non-passing verdicts
**Epic:** BSB-29 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **a verifier that cannot run, returns no verdict or grades the wrong baseline to be recorded as a verification failure**, so that **a broken or mismatched verifier is never mistaken for a passing run**.

### Acceptance Criteria

#### Scenario: A verifier that cannot run is recorded as a verification failure
Given run `1` exists as in the contract
And the verifier process exits with status `1` and writes no output file
When verification completes
Then `SELECT final_verdict, verification->>'status', verification->>'reason' FROM runs WHERE id = 1` returns exactly `unverified | unverified | verifier_crashed`
And `runs.verification->'errors'` contains the exact text `verifier process exited with status 1`
And the pass predicate for run `1` is false

#### Scenario: A verifier that returns no verdict is recorded as a verification failure
Given run `1` exists as in the contract
And the verifier writes the exact JSON `{"schema":2,"skill":"sdlc-fix-bug-triage","status":"passed","self":"completed","checks":[],"errors":[]}` with no `final` key
When verification completes
Then `SELECT final_verdict, verification->>'status', verification->>'reason' FROM runs WHERE id = 1` returns exactly `unverified | unverified | no_verdict`
And `runs.verification->'received'` equals that exact JSON object

#### Scenario: A verdict for the wrong baseline is recorded as a verification failure
Given run `1` exists as in the contract
And the verifier returns a block whose `snapshot.head_sha` is exactly `ffffffffffffffffffffffffffffffffffffffff`
When verification completes
Then `SELECT final_verdict, verification->>'status', verification->>'reason' FROM runs WHERE id = 1` returns exactly `unverified | unverified | baseline_mismatch`
And `SELECT verification->'received'->'snapshot'->>'head_sha' FROM runs WHERE id = 1` returns exactly `ffffffffffffffffffffffffffffffffffffffff`
And the pass predicate for run `1` is false

#### Scenario: An unknown verdict token is recorded as a verification failure
Given run `1` exists as in the contract
And the verifier returns a block with `status` = `passed` and `final` = `pass`
When verification completes
Then `SELECT final_verdict, verification->>'status', verification->>'reason' FROM runs WHERE id = 1` returns exactly `unverified | unverified | invalid_verdict`
And `SELECT verification->'received'->>'final' FROM runs WHERE id = 1` returns exactly `pass`

#### Scenario: A shared layer that reports unverified is recorded as unverified
Given run `1` exists as in the contract
And the verifier returns a block with `status` = `unverified`, `reason` = `no_manifest`, `self` = `completed` and `final` = `completed`
When verification completes
Then `SELECT final_verdict, verification->>'status', verification->>'reason' FROM runs WHERE id = 1` returns exactly `unverified | unverified | no_manifest`
And the pass predicate for run `1` is false

#### Scenario: A recorded verification failure is not retried automatically
Given run `1` has a recorded block with `status` = `unverified` and `reason` = `verifier_crashed`
And `runs.final_verdict` = `unverified`
When the verification worker performs three poll passes
Then no verification container labelled `bb.verify_run_id` = `1` is started
And `SELECT final_verdict, verification->>'reason' FROM runs WHERE id = 1` still returns exactly `unverified | verifier_crashed`

#### Scenario: A worker that crashes mid-verification is retried by another worker
Given run `1` exists as in the contract and its `final_verdict` and `verification` are `NULL`
And verification worker `A` acquires run `1`'s advisory lock and exits before writing any row
When verification worker `B` performs its next poll
Then within 2 seconds worker `B` starts one verification container labelled `bb.verify_run_id` = `1`
And worker `B` writes exactly one `final_verdict` and one `verification` block for run `1`
And `SELECT count(*) FROM runs WHERE id = 1 AND verification IS NOT NULL` returns `1`

### Covered requirements (traceability)
- FR-066
- FR-164

### Out of scope
The happy-path verification run and its inputs (BSB-29-PENDING-1). Recording a valid claimed, final or overturned verdict (BSB-29-PENDING-2). Fixing or retrying the shared layer's own checks (external `bheembhai-verify` release). Changing `runs.state` to a failure state when verification fails; the run's execution state is unchanged. Alerting an author about a verification failure (epic BSB-33's run report). Readiness decisions (epic BSB-30).

### Notes / dependencies
- Depends on BSB-29-PENDING-1 for the verification run and on BSB-29-PENDING-2 for the
  `final_verdict` and `verification` write.
- The shared layer exits `0` on every infrastructure failure and records `unverified`; the builder
  therefore never uses the exit code alone. It inspects `status`, `final` and `snapshot.head_sha`
  in the written block, and treats a missing or unreadable block as `verifier_crashed`.
- The exact reason codes are `verifier_crashed`, `no_verdict`, `invalid_verdict` and
  `baseline_mismatch`. A reason reported by the shared layer, such as `no_manifest`, `no_baseline`,
  `manifest_changed`, `bundle_changed`, `checks_unverified` or `artifacts_unverified`, is stored
  verbatim instead.
- `unverified` is not a run state. The run keeps the execution state BSB-26 or BSB-27 gave it.
  `final_verdict` = `unverified` is the durable record that verification did not produce a
  trustworthy verdict, and the pass predicate rejects it.
- A recorded `unverified` is final for that attempt: the worker claims only rows whose
  `verification` is still `NULL`. A crash before the write leaves `NULL`, so the advisory lock
  releases and another worker retries. An author who wants a new verdict starts a new run
  (epic BSB-27) or uses epic BSB-30's re-verify path, which is out of scope here.
- The received block is preserved under `verification.received` for invalid results so the evidence
  of what the verifier returned is not lost. It is not a substitute for the normalized
  `status`/`reason` fields.

---

## STORY: BSB-29-PENDING-4

**Summary:** Reproduce the same verification result for identical inputs
**Epic:** BSB-29 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-10, MVP

### Story
As a **skill author**, I want **the verification record to capture every input and component version, and identical inputs and verifier versions to produce the same verdict**, so that **I can explain and trust a verdict instead of treating it as a one-off**.

### Acceptance Criteria

#### Scenario: Two runs with identical inputs and verifier version get identical results
Given run `1` and run `9` both exist with `baseline_sha` = `9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09`, run-branch head `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e`, `skills_commit_sha` = `4f3c2b1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b`, `verify_version` = `2.1.2` and `claimed_verdict` = `completed`
And the shared layer returns a block with `status` = `passed`, `final` = `completed`, `overridden` = `false`, `manifest_sha256` = `c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0` and checks `[{"id":"artifact-contract","status":"passed","message":"no change required"},{"id":"must-change","status":"passed","message":"changed files within the contract"}]` for both runs
When both verifications complete
Then both rows return `final_verdict` = `completed` and `verification->>'status'` = `passed`
And for both rows `verification->'inputs'->>'run_branch_sha', verification->'inputs'->>'baseline_sha', verification->'inputs'->>'bundle_sha256', verification->'inputs'->>'verify_version'` returns exactly `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e | 9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09 | b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a | 2.1.2`
And the two rows' `verification->'checks'` are equal when compared on each check's `id`, `status` and `message`
And timing fields such as a check's duration are excluded from that comparison

#### Scenario: The verification record names every input needed to reproduce it
Given run `1` exists as in the contract and verification completes
When the row is read
Then `verification->'inputs'` contains exactly the keys `run_branch_sha`, `baseline_sha`, `bundle_sha256`, `verify_version` and `self_verdict`
And `SELECT verification->'inputs'->>'run_branch_sha', verification->'inputs'->>'baseline_sha', verification->'inputs'->>'bundle_sha256', verification->'inputs'->>'verify_version', verification->'inputs'->>'self_verdict' FROM runs WHERE id = 1` returns exactly `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e | 9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09 | b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a | 2.1.2 | completed`
And `SELECT verification->>'manifest_sha256' FROM runs WHERE id = 1` returns exactly `c2f0a1b3d5e7f9a2c4e6b8d0f1a3c5e7b9d2f4a6c8e0b1d3f5a7c9e2b4d6f8a0`

#### Scenario: A different run-branch commit is recorded as a different input
Given run `2` exists with run-branch head `7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f` and `verify_version` = `2.2.0`
When verification completes
Then `SELECT verification->'inputs'->>'run_branch_sha', verification->'inputs'->>'verify_version' FROM runs WHERE id = 2` returns exactly `7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f | 2.2.0`
And the row's `verification->'inputs'` differs from run `1`'s in `run_branch_sha` and `verify_version`

#### Scenario: A different verifier version is recorded and is not silently compared with another version
Given run `1` records `verify_version` = `2.1.2` and run `2` records `verify_version` = `2.2.0`
And both runs have the same `baseline_sha` and `skills_commit_sha`
When both verifications complete
Then run `1`'s `verification->'inputs'->>'verify_version'` is exactly `2.1.2`
And run `2`'s `verification->'inputs'->>'verify_version'` is exactly `2.2.0`
And the two rows are not reported as reproductions of one another because their recorded verifier versions differ

#### Scenario: A verification failure still records every input
Given run `1` exists as in the contract
And the verifier process exits with status `1` and writes no output file
When verification completes
Then `SELECT final_verdict, verification->>'status', verification->>'reason' FROM runs WHERE id = 1` returns exactly `unverified | unverified | verifier_crashed`
And `verification->'inputs'` still contains exactly the keys `run_branch_sha`, `baseline_sha`, `bundle_sha256`, `verify_version` and `self_verdict`
And `SELECT verification->'inputs'->>'run_branch_sha', verification->'inputs'->>'baseline_sha', verification->'inputs'->>'bundle_sha256', verification->'inputs'->>'verify_version', verification->'inputs'->>'self_verdict' FROM runs WHERE id = 1` returns exactly `6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e | 9a8c7e6d5b4f3a2c1e0d9b8a7c6f5e4d3c2b1a09 | b7e3c1a9f5d2e8b4a6c0f1d3e5b7a9c2d4f6e8b0a1c3e5d7f9b2a4c6e8d0f13a | 2.1.2 | completed`

### Covered requirements (traceability)
- NFR-010

### Out of scope
Defining the shared layer's checks or making the verifier itself deterministic (external `bheembhai-verify` release). Re-verifying an existing output branch with a changed `verify.yaml` (epic BSB-30, FR-074). Comparing two runs side by side in the UI (epic BSB-35). Retaining or purging the verification record (epic BSB-34). Recording agent image, stepkit or scanner versions (epic BSB-26; scanner epics BSB-31 and BSB-32).

### Notes / dependencies
- Depends on BSB-29-PENDING-1 for the verification run and on BSB-29-PENDING-2 for the stored
  record. It changes no transcript, log or result content; it makes the verification result
  explainable.
- NFR-010 is scoped to the inputs the shared layer actually reads: the run-branch content (its head
  commit SHA is the recorded proxy), the baseline SHA, the `verify.yaml` from the skills commit,
  and the verifier version. Two runs with the same recorded `inputs` and the same verifier
  version must produce the same `status`, `final`, `overridden` and per-check `status`/`message`.
- Timing, duration and log-tail fields are not part of the deterministic result; they may differ
  between two invocations of the same inputs.
- The `verify.yaml` digest is the shared layer's `manifest_sha256`, read from the bundle, not the
  digest of any file in the run-branch checkout. A changed `verify.yaml` on the run branch is a
  changed run-branch input and is recorded through `run_branch_sha`, not through the manifest
  digest.
- `verification.inputs` is builder-added metadata stored beside the shared layer's block; it is not
  a change to the shared layer's result format.

---
*Generated by `sdlc-plan-stories-write`. Coverage: FR-063, FR-064, FR-065, FR-066, FR-067,
FR-153, FR-164 and NFR-010 all covered. Next steps: `sdlc-plan-epic-review` reviews this set;
`sdlc-tracker-sync` publishes the approved stories to Jira.*
