# Epic Review — BSB-34: Run usage, trace & data retention

**Verdict:** CHANGES REQUESTED · **Date:** 2026-11-16 · **Stories reviewed:** BSB-34-PENDING-1, BSB-34-PENDING-2, BSB-34-PENDING-3, BSB-34-PENDING-4

> Report of the cross-story gap review (ADR-035 `reviewer`): which stories were loaded together,
> what is wrong when they are compared (not visible from any single story alone), what a person
> must decide, and the change proposed per story. This skill edits nothing else;
> `sdlc-plan-stories-write` (revise mode) applies the proposed changes. Lives at
> `docs/product/epics/BSB-34/_epic/epic-review.md`.

## Context loaded

**Work item and epic.** The user-supplied target is `SkillBuilder-2`. That key is the planning
umbrella named in the run context, not a Jira issue: a read-only `GET /rest/api/3/issue/SkillBuilder-2`
returns HTTP 404. The environment run is `7378be93-47a6-4e65-aa28-f7314cb742ba`; its upstream
`sdlc-plan-stories-write` commit is `66c5150`, and that step wrote BSB-34. A read-only
`GET /rest/api/3/issue/BSB-34` returns HTTP 200: Epic **"Run usage, trace & data retention"**,
status **To Do**, labels **FA-13, MVP**, no parent, no subtasks and no issue links. No Atlassian MCP
tool was exposed in this session, so the documented read-only REST fallback was used; the only
tracker operations were GETs. Nothing was written to Jira. The REST payload's ADF `description` was
not parsed; the epic definition in `docs/product/epics.md` was used instead.

**Stories in the epic (all four read in full).** `docs/product/epics/BSB-34/_epic/stories.md`
(lines 1–399), `story-map.json`, and `revisions.md` (Pass 1 reworked the set into four vertical
slices; no prior `epic-review.md` exists and no `epic-sequence.md` exists yet).

- **BSB-34-PENDING-1** — "See what a run consumed and cost on its report" (FR-159, FR-160,
  NFR-015, NFR-016, NFR-017). Records terminal telemetry and renders it in the report's new
  "Usage and cost" section; declares `runs.token_usage` and `runs.turn_count`, and states that
  `runs.cost_usd` already exists in ADR SK-001 §9.
- **BSB-34-PENDING-2** — "Open a run's trace and see it is marked as a test-environment run"
  (NFR-011). Creates one trace at launch, stores `runs.trace_id`, and renders "Open trace" /
  "Tracing is disabled." / "Trace unavailable."; declares the installation tracing configuration
  `{enabled, environment, url_template}`.
- **BSB-34-PENDING-3** — "See that an old run's logs, transcript and results have expired"
  (NFR-013, NFR-018). Adds the report's "Run data" section (retained / expired / expiry-pending /
  no-data), and the scheduled sweep that deletes every object under `runs/<run-id>/`; keeps the
  `runs` row and `skill_bundles`.
- **BSB-34-PENDING-4** — "Purge a run's data on request and see it recorded on the report"
  (NFR-014). Adds the owner-only `POST /projects/7/runs/21/purge`, its idempotence and failure
  behaviour, and the purged / purge-failed states in the same "Run data" section; declares
  `runs.purged_at`, `runs.purged_by` and `runs.purge_error`.

**Requirements and epic definition.** `docs/product/PRD.md` §5 (FA-13 "Run results & audit
trail"), §6 (FR-159, FR-160), §7 (NFR-011, NFR-013, NFR-014, NFR-015, NFR-016, NFR-017,
NFR-018), §8 (source note: retention/purge framed as builder database plus S3 bucket) and §9 (no
open product questions). `docs/product/epics.md` BSB-34 section (lines 1114–1172) and the
surrounding BSB-33/BSB-38 definitions for the boundary. `story-map.json` maps exactly the nine
requirements above, each to one story.

**Design authority.** `docs/adr/SK-001-skill-builder.md` §6 (Results: `runs/<run-id>/` holds the
bundle, `bb_step_result.json`, logs and transcript; Langfuse traces are env `skilltest`; the run
page lists turns/tokens/cost and the trace link) and §9 (Data model: `runs.cost_usd` exists;
`token_usage`, `turn_count`, `trace_id`, `purged_at`, `purged_by`, `purge_error` do not). The
repository has no `docs/architecture.md`, `docs/data-model.md`, `docs/api-contracts/` or
`docs/ui-conventions.md`; the ADR is the design authority, and these new columns are explicitly
left to the data-model stage by the stories.

**Other story sets read for the hand-offs.** BSB-22-PENDING-2 and -3 (shared owner guard and
membership check), BSB-23-PENDING-5 (credential redaction), BSB-25-PENDING-1 and -2 (bundle
retention note), BSB-26-PENDING-1, -2 and -3 (launch path, log tail, terminal result), and
BSB-33-PENDING-1, -3 and -5 (report page, diff section, trace link and its strings). Also read:
BSB-33's `epic-review.md` in full (its Finding 7 / Open question 6 asked BSB-34 to own
`runs.trace_id` and the tracing configuration, which BSB-34-PENDING-2 now answers), and the finding
lists of the BSB-22/23/25/26 reviews.

**Conventions and layout.** No `AGENTS.md` and no `CLAUDE.md` exist at the repo root, so the
default layout in `shared/_SHARED-project-layout.md` resolves this file to
`docs/product/epics/BSB-34/_epic/epic-review.md`. Jira reporting-type issues for ADR-035 are not in
this skill's remit; none was created.

## Findings

### Finding 1 — Cross-story lifecycle: the "Run data" state precedence and the run states that retention and purge act on are split between PENDING-3 and PENDING-4

- **Severity:** Blocking
- **Stories touched:** BSB-34-PENDING-3, BSB-34-PENDING-4 (cross-epic: BSB-26-PENDING-2, BSB-33-PENDING-1)
- **Evidence:** `stories.md:39-41` says PENDING-3 "adds the report's 'Run data' section, which owns the retained/expired/pending status and the artifact download links." PENDING-3's states are retained-until (`stories.md:244,249,254`), expired (`:244`), expiry-pending (`:269`) and no-data (`:259`), with the sweep keyed to `runs.finished_at` (`:294-300`). PENDING-4 adds two more states to that same section — "Run data: purged on …" (`:337,352,362`) and "Run data: purge failed: …" (`:357`) — but its Notes (`:375-396`) never name PENDING-3, never say which status wins when both apply, and its dependency list (`:382-386`) names neither PENDING-3 nor BSB-33-PENDING-1's report route. The combinations are undefined: a run purged and then past its retention date; a failed purge that later crosses retention; a purge requested for a run the sweep already expired. The no-data state (`:259`) has the same shape a purged run presents. Separately, every PENDING-4 scenario uses `state "completed"` (`:335,340,345,350,355`), and its Notes impose no state guard on `POST /projects/7/runs/21/purge`, while BSB-26-PENDING-2 reads `runs/<id>/progress.json` and `agent.log` for the live view (`BSB-26/_epic/stories.md:150-172`); a purge of a prepared or running run would delete the live view's objects mid-execution.
- **What is missing/ambiguous/contradictory:** One lifecycle model for the section and for the two deletion paths. Without it, two implementers produce contradicting renderings (one reports "expired", the other "purged"), the sweep can overwrite the purge audit trail (`purged_at`/`purged_by`) or vice versa, and the purge endpoint can race the execution path. PENDING-4's notes also omit BSB-34-PENDING-3 as the section it is modifying, which a developer implementing only PENDING-4 would not discover.
- **Question (if a person must decide):** Which status wins when a purged or purge-failed run later crosses its retention date, and does the sweep skip runs with a non-null `purged_at`? May an owner purge a prepared or running run, or only a terminal one, and what happens to the live view if the former? (Open question 1.)
- **Proposed change:** In **PENDING-3**, state the precedence once in the "Run data" notes and add acceptance criteria for (a) a purged run past its retention date rendering "purged on …" (the sweep does not delete audit metadata and does not change the purge record), and (b) a purge-failed run past retention rendering "purge failed: …" with the sweep leaving the objects for the retry. In **PENDING-4**, add PENDING-3 as the owner of the section and BSB-33-PENDING-1 as the route, name the precedence, and add the run-state guard (with its response and message if a running run is refused). Same change applied to both stories' notes; the exact precedence values come from the answer to Open question 1. **BSB-33-PENDING-1** needs no change — PENDING-3 already states it adds the section to that report route. **BSB-26-PENDING-2** needs no change if only terminal runs may be purged; if Open question 1 allows purging a running run, it gains a "run data purged" live-view state and the matching scenario.

### Finding 2 — Cross-epic producer contradiction: PENDING-1 depends on BSB-26-PENDING-1 writing `runs/<run-id>/usage.json`, but BSB-26 assigns usage to BSB-34 and no BSB-26 story mentions the object

- **Severity:** Blocking
- **Stories touched:** BSB-34-PENDING-1 (cross-epic: BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3)
- **Evidence:** `stories.md:126-129` says PENDING-1 "depends on … BSB-26-PENDING-1 for the execution path that writes `runs/<run-id>/usage.json`", and the story's ACs read that object as the source of the recorded values (`:74-100`). But BSB-26-PENDING-1's out-of-scope explicitly excludes "token, cost and turn usage and retention (BSB-34)" (`BSB-26/_epic/stories.md:86-96`) while its Notes say "BSB-34 reads the run's usage" (`:129`); BSB-26-PENDING-2's out-of-scope repeats "the recorded turn count, token usage, cost and retention (BSB-34)" (`:183-190`); BSB-26-PENDING-3's out-of-scope repeats "token usage, cost and retention (BSB-34)" (`:263-272`). Searching the whole BSB-26 story set finds no story that writes, reads or names `runs/<run-id>/usage.json`. The hand-off is therefore one-sided and mutually disclaimed: PENDING-1 says BSB-26 writes it; BSB-26 says BSB-34 owns it.
- **What is missing/ambiguous/contradictory:** The terminal telemetry object has no producer. PENDING-1's ACs pass against a fixture object, so the story is green in tests while a production run has no `usage.json` to read and the columns stay NULL. The answer also decides what the retention sweep in PENDING-3 deletes (`stories.md:302-303` lists `usage.json`).
- **Question (if a person must decide):** Which epic owns emitting `runs/<run-id>/usage.json` — the BSB-26 execution path at terminal state, or BSB-34 from some other source? If BSB-26 owns it, which BSB-26 story carries the AC and how is its out-of-scope corrected? (Open question 2.)
- **Proposed change:** In **PENDING-1**, make the Notes and the AC precondition name the chosen producer explicitly; if BSB-34 is the producer, state the source object and add the writing step (and keep PENDING-3's sweep list consistent). Cross-epic follow-up for the revise pass: **BSB-26-PENDING-1/-2/-3** must either add the `usage.json` write (and its reader contract) or remove the "usage … (BSB-34)" disclaimers and name BSB-34 as the producer; **BSB-34's** epic boundary in `epics.md` must reflect the answer.

### Finding 3 — Cross-epic hand-offs for the trace-creation hook and `runs/<run-id>/transcript.json` are one-sided

- **Severity:** Advisory
- **Stories touched:** BSB-34-PENDING-2, BSB-34-PENDING-3 (cross-epic: BSB-26-PENDING-1, BSB-26-PENDING-2, BSB-26-PENDING-3, BSB-33-PENDING-3)
- **Evidence:** PENDING-2's Notes say "the launch path must call this hook and pass the trace identifier to the runtime adapter as a cross-epic hand-off, because BSB-26-PENDING-1's acceptance criteria do not name tracing" (`stories.md:205-213`). BSB-26-PENDING-1's ACs and Notes (`BSB-26/_epic/stories.md:57-129`) never mention a trace, a trace identifier or a hook. PENDING-3's Notes say "no BSB-26 story currently writes `runs/<run-id>/transcript.json`, so the execution path must write it as a cross-epic hand-off or the transcript has no producer" (`stories.md:311-316`); BSB-26-PENDING-2 writes `progress.json`/`agent.log` and BSB-26-PENDING-3 writes `bb_step_result.json`, but no BSB-26 story writes `transcript.json`. BSB-33-PENDING-3's out-of-scope assigns "storing or rendering the agent's transcript (BSB-26 and BSB-34)" (`BSB-33/_epic/stories.md:228-231`), splitting ownership without naming which does the storing.
- **What is missing/ambiguous/contradictory:** BSB-34's stories explicitly depend on two execution-path behaviours that no executing story owns. PENDING-2's and PENDING-3's ACs pass against fixture traces/objects, so the gap cannot be seen inside BSB-34; a production run would create no trace and no transcript, and PENDING-2's "Open trace" link and PENDING-3's "Download transcript" would never appear.
- **Question (if a person must decide):** Which story outside BSB-34 owns the trace-creation hook and `transcript.json` — a new or existing BSB-26 story, or BSB-34 itself? (Open question 2, with Finding 2's usage object.)
- **Proposed change:** In **PENDING-2** and **PENDING-3**, keep the dependency but name the owning story and the exact contract (hook name/inputs, object key, writer). Cross-epic follow-up for the revise pass: **BSB-26-PENDING-1** adds the trace hook (or names BSB-34 as its owner); **BSB-26-PENDING-2** or **BSB-26-PENDING-3**, whichever the person assigns, adds the `transcript.json` write (PENDING-2 currently writes `progress.json`/`agent.log`, PENDING-3 writes `bb_step_result.json`); **BSB-33-PENDING-3**'s out-of-scope is reconciled to the chosen owner. No other BSB-26 story changes, and there is no BSB-34 AC change unless the answer makes BSB-34 the producer.

### Finding 4 — Cross-epic fallback: the objects PENDING-3 deletes are rendered by BSB-26-PENDING-2 and BSB-33-PENDING-3, whose existing unavailable states misdescribe retention deletion

- **Severity:** Advisory
- **Stories touched:** BSB-34-PENDING-3 (cross-epic: BSB-26-PENDING-2, BSB-33-PENDING-3)
- **Evidence:** PENDING-3's Notes says the log and diff sections BSB-26-PENDING-2 and BSB-33-PENDING-3 own "must degrade to their existing unavailable state when the objects are gone; their reviewers must confirm that fallback" (`stories.md:316-318`). Those existing states are: BSB-26-PENDING-2's "No log output yet." (`BSB-26/_epic/stories.md:157`) and "Logs unavailable; retry." (`:169-172`), with the note "A missing progress or log object is an empty state, not an error, because the agent may not have written it yet" (`:204-207`); and BSB-33-PENDING-3's "Diff unavailable: The run diff could not be captured." (`BSB-33/_epic/stories.md:219-222`, notes `:245-250`). After retention expiry or a purge, the truthful state is "no longer retained/expired/purged", not "the agent has not written it yet" or "the capture failed", and neither story knows BSB-34 deletes the objects.
- **What is missing/ambiguous/contradictory:** The cross-epic fallback contract is delegated to unnamed "reviewers", and the only existing states are misleading after deletion. PENDING-3's own report does show "expired", but a reader of the log or diff section sees a false explanation of why the data is missing.
- **Question (if a person must decide):** None; this is a contract wording change, not a product decision.
- **Proposed change:** In **PENDING-3**, replace "their reviewers must confirm that fallback" with the exact expected state and the authoritative notice ("the 'Run data' section states expired/purged"). Cross-epic follow-up: **BSB-26-PENDING-2** and **BSB-33-PENDING-3** add a distinct "not retained after expiry or purge" / "expired" message, or explicitly defer to the "Run data" section, and their tests cover the deleted-object case.

### Finding 5 — Cross-story access rule: PENDING-2 assumes cross-project access and PENDING-3 has no denial scenario, while the sibling stories assert the membership rule

- **Severity:** Advisory
- **Stories touched:** BSB-34-PENDING-2, BSB-34-PENDING-3 (cross-story: BSB-34-PENDING-1, BSB-34-PENDING-4; cross-epic: BSB-22-PENDING-3, BSB-26-PENDING-2, BSB-33-PENDING-1)
- **Evidence:** PENDING-1 has "A non-member cannot see a run's usage, cost or turns" → HTTP 403 (`stories.md:102-105`). PENDING-2 has the same scenario for the trace → HTTP 403 (`:188-191`). PENDING-4 has a non-owner 403 (`:339-342`) and a cross-project 404 (`:344-347`). But PENDING-2's "Every run carries the installation's test-environment identity" scenario has Ada — whose only `project_members` row is project 7 (`:169`) — open the reports for run 21 (project 7) **and run 31 (project 8)** (`:173-176`), with no project-8 membership stated. PENDING-3's six scenarios (`:241-269`) all sign in Ada for project 7 and contain no non-member or cross-project case, even though it introduces artifact download links (`:244,254`) — a new data-exposure surface. BSB-22-PENDING-3 defines the shared check as a 403 for a signed-in non-member (`BSB-22/_epic/stories.md:64-77,204-212`); BSB-26-PENDING-2 treats another project's run as not disclosed (HTTP 404, `BSB-26/_epic/stories.md:165`); and BSB-33-PENDING-1 enforces the non-member 403 on the report route (`BSB-33/_epic/stories.md:86-89`).
- **What is missing/ambiguous/contradictory:** PENDING-2's fixture contradicts the rule its own other scenario asserts; either the rule has an exception (why can Ada see project 8?) or the fixture is wrong. PENDING-3 adds a download surface without exercising the denial path that protects it, so an implementer can wire downloads without the membership check and the epic-level access rule still passes.
- **Question (if a person must decide):** None; the rule is already stated in the sibling scenarios and BSB-22-PENDING-3. This is a fixture/coverage defect.
- **Proposed change:** In **PENDING-2**, give Ada a `project_members` row for project 8 or use a second signed-in owner for run 31. In **PENDING-3**, add "A non-member cannot download a run's artifacts" (HTTP 403, no object bytes, no link) and "A run from another project is not disclosed" (HTTP 404) scenarios, matching PENDING-1/-2/-4. **PENDING-1** and **PENDING-4** need no change — they already assert the same rule. **BSB-22-PENDING-3**, **BSB-26-PENDING-2** and **BSB-33-PENDING-1** need no change — they are the rule's source and the existing evidence.

### Finding 6 — Dependency-note sanity: PENDING-4 reuses the shared owner guard owned by BSB-22-PENDING-2 but names only BSB-22-PENDING-3

- **Severity:** Advisory
- **Stories touched:** BSB-34-PENDING-4 (cross-epic: BSB-22-PENDING-2, BSB-22-PENDING-3)
- **Evidence:** PENDING-4's dependency list says it depends on "BSB-22-PENDING-3 for the shared project-membership check" (`stories.md:382-384`), and its Notes say it "checks the project-owner role" (`:380-382`) and that a non-owner member is denied (`:388-390`). BSB-22-PENDING-3 only defines the membership check, where the owner passes as a member (`BSB-22/_epic/stories.md:64-77`, `:204-212`). The owner-only guard is defined separately by BSB-22-PENDING-2: "this story defines the shared owner guard every project-administration route uses … a member without that role receives HTTP 403" (`BSB-22/_epic/stories.md:130-135`). No BSB-34 story names BSB-22-PENDING-2.
- **What is missing/ambiguous/contradictory:** PENDING-4's purge authorization is owner-only, but it names only the weaker membership guard. An implementer reading the dependency list can check `project_members` membership and stop, or invent a check against `projects.owner_id`, diverging from the shared guard the other owner-only routes use.
- **Question (if a person must decide):** None; the guard already exists and is named by sibling epics.
- **Proposed change:** In **PENDING-4**, add BSB-22-PENDING-2 to the Notes as the shared owner guard it reuses, and state that a non-owner member gets the 403 while a non-member gets the membership 403 (already asserted). **BSB-22-PENDING-3** needs no change — the membership check stays as the first gate. No AC change.

### Finding 7 — Cross-epic scope hand-off: BSB-25-PENDING-2 outsources bundle retention and purge to BSB-34, which declines it, and PENDING-3 mis-cites the source story

- **Severity:** Advisory
- **Stories touched:** BSB-34-PENDING-3 (cross-epic: BSB-25-PENDING-2)
- **Evidence:** BSB-34's header and PENDING-3 say "BSB-25-PENDING-1's out-of-scope names 'bundle retention and purge (BSB-34)'" (`stories.md:42`, `:307-309`). The phrase is actually in **BSB-25-PENDING-2**'s out-of-scope (`BSB-25/_epic/stories.md:184`), not PENDING-1. Substantively, BSB-34-PENDING-3 asserts that `skill_bundles` survive (`stories.md:261-264`) and says bundles are keyed by `(skill, skills_commit_sha)`, are shared by every run at that commit, are not run-scoped and are not deleted (`:305-309`); its out-of-scope also excludes "deleting content-addressed `skill_bundles` objects" (`:279`). The PRD's NFR-013/NFR-014 and FA-13 cover run transcripts, logs and results, not shared bundles.
- **What is missing/ambiguous/contradictory:** The hand-off is one-sided and mis-cited: BSB-25-PENDING-2 says BSB-34 owns bundle retention/purge, while BSB-34's stories and the PRD scope say it does not. A reader following the citation in BSB-34's own notes is sent to the wrong story; a reader of BSB-25 believes bundles are covered by another epic.
- **Question (if a person must decide):** Does BSB-34 own retention/purge of content-addressed `skill_bundles` objects (as BSB-25-PENDING-2's out-of-scope states), or does BSB-25 keep it? The PRD supports "BSB-34 does not", but the cross-epic scope must be settled by a person. (Open question 3.)
- **Proposed change:** In **PENDING-3** and the epic header, correct the citation to **BSB-25-PENDING-2**. On the answer "BSB-34 does not own bundles" (which the stories already implement), cross-epic follow-up for the revise pass: **BSB-25-PENDING-2** re-scopes or removes the "(BSB-34)" phrase and, if the bundles need retention, adds it to BSB-25. On the opposite answer, add a BSB-34 story or ACs for `skill_bundles` retention/purge and update `epics.md`; PENDING-3's "bundles survive" AC would then change.

## Open questions

1. **Run-data lifecycle precedence and purge eligibility (Finding 1).** Which status does the report show when a run is purged and then crosses its retention date, when a purge fails and the run later crosses retention, and when a purge is requested for a run the sweep already expired? Does the sweep skip a run whose `purged_at` is set? May a project owner purge a run that is still prepared or running, or only a terminal run — and if a running run can be purged, what happens to BSB-26-PENDING-2's live log/progress view and BSB-26-PENDING-3's execution? (PENDING-3 renders expired/expiry-pending at `stories.md:244,249,269`; PENDING-4 renders purged/purge-failed at `:337,352,357` and only uses completed runs at `:335,340,345,350,355`; the live view is `BSB-26/_epic/stories.md:150-172`.)
2. **Execution-path artifact ownership (Findings 2 and 3).** Which epic owns emitting the terminal `runs/<run-id>/usage.json`, calling the trace-creation hook and storing `runs.trace_id`, and writing `runs/<run-id>/transcript.json` — a BSB-26 story or BSB-34? If BSB-26, which story carries each AC and how are its "usage/retention (BSB-34)" disclaimers corrected? If BSB-34, what is the source object for each and which story writes it? (PENDING-1 `stories.md:126-129`; PENDING-2 `:205-213`; PENDING-3 `:311-316`; BSB-26-PENDING-1 out-of-scope `BSB-26/_epic/stories.md:86-94`; BSB-33-PENDING-3 out-of-scope `BSB-33/_epic/stories.md:228-231`.)
3. **Bundle retention and purge ownership (Finding 7).** Does BSB-34 own retention/purge of content-addressed `skill_bundles` objects, as BSB-25-PENDING-2's out-of-scope says, or does BSB-25 keep it? BSB-34's stories currently assert the bundles survive and exclude them from deletion; the PRD covers run artifacts only. (BSB-25-PENDING-2 out-of-scope `BSB-25/_epic/stories.md:178-185`; PENDING-3 `stories.md:261-264,305-309`; PRD §7 NFR-013/NFR-014.)

## Proposed changes

**BSB-34-PENDING-1 (Finding 2).**
- Notes: name the actual producer of `runs/<run-id>/usage.json` (from Open question 2). If BSB-26-PENDING-1 produces it, say so and add the field contract; if BSB-34 produces it, state the source and add the writing step to the ACs.
- Notes: keep the `usage.json` key in PENDING-3's sweep list consistent with the answer.

**BSB-34-PENDING-2 (Findings 3, 5).**
- Scenario 2: give Ada a project-8 `project_members` row, or use a second signed-in project owner for run 31, so the cross-project fixture no longer contradicts the 403 rule.
- Notes: name the story that owns the trace-creation hook and the `runs.trace_id` write (from Open question 2); keep the existing statement that the hook runs before the first model call.

**BSB-34-PENDING-3 (Findings 1, 3, 4, 5, 7).**
- Notes: state the "Run data" status precedence (retained / expired / expiry-pending / purged / purge-failed) and that PENDING-4 adds the last two; define what the sweep does with a run whose `purged_at` is set or whose `purge_error` is set.
- ACs: add a purged run past retention and a purge-failed run past retention, per the answer to Open question 1.
- ACs: add non-member 403 and cross-project 404 scenarios for the "Run data" section and its download links.
- Notes: replace the "their reviewers must confirm that fallback" delegation with the exact expected log/diff state after deletion, and name the owning stories (BSB-26-PENDING-2, BSB-33-PENDING-3).
- Notes: name the owner/producer of `runs/<run-id>/transcript.json` (from Open question 2).
- Notes and epic header line 42: correct the citation from BSB-25-PENDING-1 to BSB-25-PENDING-2, per Finding 7 / Open question 3.

**BSB-34-PENDING-4 (Findings 1, 6).**
- Notes: name BSB-34-PENDING-3 as the owner of the "Run data" section it extends, and BSB-33-PENDING-1 as the report route; add BSB-22-PENDING-2 as the shared owner guard it reuses (BSB-22-PENDING-3 remains the membership check).
- Notes and, if the answer requires it, ACs: state the state precedence with PENDING-3 and the guard on the run's state (may a prepared/running run be purged?), per Open question 1.

**Cross-epic follow-ups for the revise pass (not edits this review makes):**
- **BSB-26-PENDING-1**: add the `usage.json` terminal write and the trace-creation hook, or hand them to BSB-34 explicitly and correct the out-of-scope disclaimers (Findings 2, 3).
- **BSB-26-PENDING-2 / -3**: add the `transcript.json` writer, and add a post-deletion log/progress state distinct from "not written yet"/"retry" (Findings 3, 4).
- **BSB-33-PENDING-3**: add the post-retention/purge diff state and reconcile its "storing the transcript (BSB-26 and BSB-34)" wording with the chosen owner (Findings 3, 4).
- **BSB-25-PENDING-2**: re-scope or remove "bundle retention and purge (BSB-34)" per Open question 3 (Finding 7).
- **`docs/product/epics.md` : BSB-34**: reflect the usage/transcript/trace producer ownership and the bundle boundary from Open questions 2 and 3.

**Not proposed:** no new entities, endpoints or services; no change to the ADR; no change to PENDING-1's "Usage and cost" section beyond the producer wording; no change to PENDING-2's trace environment identity or failure behaviour; no change to PENDING-3's retention arithmetic; no change to PENDING-4's idempotence or failure semantics.

## Architecture impact

None. Every gap in this report is an ownership, state-precedence or dependency-note issue inside the story set; no new entity, endpoint, service or external integration is required. The columns the stories add (`runs.token_usage`, `runs.turn_count`, `runs.trace_id`, `runs.purged_at`, `runs.purged_by`, `runs.purge_error`) and the external trace store are already accounted for by the story notes and ADR SK-001 §6/§9, and the data-model stage records the columns. Findings 2, 3 and 7 need an owner/scope decision, not a design change.

## Requirement coverage check

| Requirement | PRD source | Mapped story | AC evidence | Verdict |
|---|---|---|---|---|
| FR-159 — record token usage, cost and turn count per run | §6 | BSB-34-PENDING-1 | `runs.token_usage`, `runs.cost_usd`, `runs.turn_count` written from the validated telemetry (`stories.md:74-100`) | Covered |
| FR-160 — show usage, cost and turns on the run report | §6 | BSB-34-PENDING-1 | "Usage and cost" section renders the values; non-member 403 (`stories.md:79-105`) | Covered |
| NFR-011 — traces marked with the test-environment identity, openable from the report | §7 | BSB-34-PENDING-2 | trace env "skilltest", `runs.trace_id`, "Open trace" link (`stories.md:169-186`) | Covered |
| NFR-013 — run artifacts retained then expired under the period | §7 | BSB-34-PENDING-3 | retained/expired/expiry-pending; no objects under `runs/21/` after expiry; run row and run metadata remain (`stories.md:241-269`) | Covered |
| NFR-014 — purge run data on request | §7 | BSB-34-PENDING-4 | owner `POST …/purge`, idempotence, failure/retry, `purged_at`/`purged_by`/`purge_error` (`stories.md:334-362`) | Covered |
| NFR-015 — no cost recomputation / record cost accurately | §7 | BSB-34-PENDING-1 | `runs.cost_usd` is the telemetry's cost; no price table (`stories.md:134-140`) | Covered |
| NFR-016 — token totals computed from the four counts | §7 | BSB-34-PENDING-1 | `total_tokens` = sum of four counts; telemetry total not trusted (`stories.md:100,134-140`) | Covered |
| NFR-017 — turn count recorded and displayed | §7 | BSB-34-PENDING-1 | `runs.turn_count`; "Recorded turns: 7" asserted end-to-end (`stories.md:98-105,130-132`) | Covered |
| NFR-018 — retention period configurable, default three months | §7 | BSB-34-PENDING-3 | `retention_months` default 3, minimum 1; 6-month override (`stories.md:246-249,292-300`) | Covered |

**Notes.** All nine requirements covered by this epic are mapped to exactly one story and each is
exercised by at least one acceptance criterion; `story-map.json` and the stories' traceability
blocks agree with `epics.md`. There is no orphan requirement and no requirement claimed by two
stories. FR-159 and FR-160 are the record and display halves of one vertical slice, and PENDING-1
asserts both ends, so the merge does not leave either half deferred. The stories apply NFR-004
(credential redaction) but explicitly leave it to BSB-23-PENDING-5; they do not claim it. The
inherited signed-in/member rule is exercised by PENDING-1, -2 and -4 but not by PENDING-3, which is
Finding 5. No NFR owned by BSB-34 is unexercised.

## Dependency-note sanity check

Every story named in a note exists; no note points to a missing or renamed story. The mismatches
below are the ownership or reciprocity defects reported above. This check confirms the graph, not
the build order (that is `sdlc-plan-epic-sequence`'s job).

| Story | Depends on (as written) | Exists | Reciprocal? | Result |
|---|---|---|---|---|
| PENDING-1 | BSB-26-PENDING-3 for the terminal state | Yes | Yes | OK |
| PENDING-1 | BSB-26-PENDING-1 for the `usage.json` writer | Story yes, hand-off no | **No** — BSB-26-PENDING-1/-3 disclaim usage to BSB-34 | **Finding 2** |
| PENDING-1 | BSB-33-PENDING-1 for the report page | Yes | Yes — its out-of-scope names BSB-34 for usage/cost | OK |
| PENDING-2 | BSB-26-PENDING-1 for launch path/runtime adapter | Yes | **No** — no trace hook named there | **Finding 3** |
| PENDING-2 | BSB-33-PENDING-5 for link/states | Yes | Yes — BSB-33-PENDING-5 names BSB-34 for `trace_id`/config | OK |
| PENDING-3 | BSB-26-PENDING-3 for `finished_at`/terminal state | Yes | Yes | OK |
| PENDING-3 | BSB-26-PENDING-2 for `agent.log`/`progress.json` | Yes | Yes | OK |
| PENDING-3 | BSB-26-PENDING-3 for `bb_step_result.json` | Yes | Yes | OK |
| PENDING-3 | BSB-33-PENDING-3 for `diff.json` | Yes | Partial — retention is deferred to BSB-34, but its fallback wording misstates deletion | **Finding 4** |
| PENDING-3 | "execution path" for `transcript.json` | **No story named** | No | **Finding 3** |
| PENDING-3 | BSB-25-PENDING-1 for the bundle note | Story exists, **citation wrong** — phrase is in PENDING-2 | No | **Finding 7** |
| PENDING-4 | BSB-18 for session/gate | Yes | Yes | OK |
| PENDING-4 | BSB-22-PENDING-3 for the membership check | Yes | Yes | OK |
| PENDING-4 | BSB-22-PENDING-2 for the owner guard | Yes | **Not named** (Finding 6) | **Finding 6** |
| PENDING-4 | BSB-26-PENDING-2/-3 for `agent.log`/`progress.json`/`bb_step_result.json` | Yes | Yes | OK |
| PENDING-4 | BSB-33-PENDING-3 and PENDING-1 for `diff.json`/`usage.json` | Yes | Yes | OK |
| PENDING-4 | BSB-33-PENDING-1 for the report route and PENDING-3 for the section | Yes | **Not named** (Finding 1) | **Finding 1** |

**Cross-story links inside BSB-34.** PENDING-1's out-of-scope names PENDING-2/-3/-4; PENDING-2's
names PENDING-1/-3/-4; PENDING-3's names PENDING-1/-4; PENDING-4's names PENDING-1/-3. The
out-of-scope partition is reciprocal. The only internal gaps are the state-model split (Finding 1),
the missing denial scenarios (Finding 5) and the section-owner omission in PENDING-4 (Finding 1).
