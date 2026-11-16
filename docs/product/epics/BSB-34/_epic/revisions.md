# Revisions — BSB-34 (Run usage, trace & data retention)

## Pass 1 — 2026-11-16 — automated verification feedback (run 7378be93-47a6-4e65-aa28-f7314cb742ba)

**Report applied.** The automated verifier rejected the previous `stories.md` on the
`vertical_slices` judge criterion: "Not every story is a user-visible vertical slice. PENDING-2
(run report rendering) and PENDING-5 (owner-triggered purge) are user-facing, but PENDING-1 is
persistence-only … PENDING-3 only asserts an external trace-store trace and the runs.trace_id
column, while PENDING-4 only asserts a background retention sweep deletes object-store keys; both
are technical/integration or job layers rather than story-level user-visible outcomes."

**Finding → change.**

- *PENDING-1 is persistence-only; its visible display is deferred to PENDING-2.* → Old PENDING-1
  (record usage, cost and turn count) and old PENDING-2 (render them on the report) are merged into
  new **BSB-34-PENDING-1 "See what a run consumed and cost on its report"** (FR-159, FR-160,
  NFR-015, NFR-016, NFR-017). Every scenario now starts with the run finishing and ends with Ada
  reading the values on GET "/projects/7/runs/21"; the recorded row is asserted as the durable
  backing of that visible outcome. No display is deferred, and the separate display story is gone.
- *PENDING-3 only asserts an external trace-store trace and the `runs.trace_id` column.* → New
  **BSB-34-PENDING-2 "Open a run's trace and see it is marked as a test-environment run"** makes the
  compliance reviewer's view of the opened trace the outcome, and brings the report's "Open trace"
  link and its "Tracing is disabled." / "Trace unavailable." states into this story's acceptance
  criteria instead of deferring them to BSB-33. `runs.trace_id` is asserted only as the backing of
  the link that opens.
- *PENDING-4 only asserts a background retention sweep deletes object-store keys.* → New
  **BSB-34-PENDING-3 "See that an old run's logs, transcript and results have expired"** adds the
  report's "Run data" section (retained-until date, expired notice, expiry-pending notice and
  artifact download links) as the user-visible outcome (NFR-013, NFR-018). The sweep is asserted
  only behind what Ada sees; the object-store state is the durable check that the notice is true.
- *PENDING-5 is user-facing.* → Kept and extended as **BSB-34-PENDING-4 "Purge a run's data on
  request and see it recorded on the report"** (NFR-014): the owner's request now also asserts the
  report's purged and purge-failed states and the absence of the action for a non-owner.

**Coverage.** All 9 epic requirements are still covered, each by exactly one story: FR-159,
FR-160, NFR-015, NFR-016 and NFR-017 (PENDING-1); NFR-011 (PENDING-2); NFR-013 and NFR-018
(PENDING-3); NFR-014 (PENDING-4). No requirement was added, dropped or claimed by a story outside
this epic.

**Keys.** Draft keys are renumbered from `-1` to `-5` to `-1` to `-4`: old `-1` and `-2` merged
into new `-1`; old `-3` became new `-2`; old `-4` became new `-3`; old `-5` became new `-4`. No
story was published to Jira (authoring only, ADR-035), so there is no tracker key to reconcile.

**Still open.** No verifier finding remains unapplied. The following are cross-epic hand-offs
carried in the stories' notes and are not open questions for this epic: `runs/<run-id>/usage.json`
has no named producer in BSB-26's stories; `runs/<run-id>/transcript.json` has no producer in any
BSB-26 story; BSB-26-PENDING-2's log tail and BSB-33-PENDING-3's diff section must degrade to their
existing unavailable state once BSB-34 deletes the objects; and BSB-25-PENDING-1's out-of-scope note
"bundle retention and purge (BSB-34)" needs reconciling because content-addressed `skill_bundles`
objects are not run-scoped and are not deleted by this epic.
