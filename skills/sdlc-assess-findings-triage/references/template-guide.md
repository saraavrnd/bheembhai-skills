# Template guide — sdlc-assess-findings-triage

Guidance for filling this skill's templates, section by section. Read the part for a template
before you fill it. Do not copy this guidance into the output.

## `templates/fix-plan.md.tmpl`

### Summary

Counts must match `fix-map.json`. The sentence names the batch to fix first.

### Batches

One `### B-NN — title` section per batch in `fix-map.json`, in batch order, whatever the decision.
For a fix-now batch, everything from the findings table to **Done when** is copied into the Jira
bug's description by `sdlc-tracker-sync`, so write it for a developer who has not seen the audit.
For accept and defer batches, keep the table and the decision line; the Accepted and deferred
table carries the reason.

The fingerprint column is what `sdlc-assess-security-rescan` uses to prove a finding is gone.
Copy it exactly from `findings.json`.

### Accepted and deferred

One row per batch whose decision is accept or defer. An accept without a limit on the risk is not
an acceptance; say what contains it.

### False positives

One row per false-positive finding. Duplicates are listed in `fix-map.json` only.

### Not covered by tools

Copy the categories from the audit's Gaps section and add what to check, in a sentence each.

### Jira

The project key comes from the run context. Never guess it.

## `templates/fix-map.schema.json`

`bug_key` is `SEC-PENDING-N` for a fix-now batch until tracker-sync replaces it with the real
key, and `null` for accept and defer. `manual_action` is set for secrets and anything else a
person must do outside the code.
