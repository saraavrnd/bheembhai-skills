# Batching rules — sdlc-assess-findings-triage

A batch becomes one Jira security bug, one `sdlc-wf-security-fix` run, one branch and one pull
request. Size it so a reviewer can read the PR in one sitting.

1. **One root cause or one module per batch.** Two SQL injections in the same reporting module
   that share a query helper are one batch. The same rule firing in unrelated modules is two.
2. **At most about five findings.** Split a larger group by module.
3. **Secrets alone.** Each leaked credential is its own batch, because it needs a person to
   revoke and rotate it, and its fix (remove from code, load from config) is separate from any
   other change. A secret in git history also needs a decision on rewriting history, which is a
   person's call; propose it, never assume it.
4. **Dependency upgrades by package manager.** All `composer` upgrades in one batch, all `npm`
   upgrades for one `package.json` in another. Note any major-version jump: it is a code change,
   not only a version bump, and may deserve its own batch.
5. **Configuration and container hardening together.** Dockerfile and compose findings for one
   image form one batch.
6. **Never mix severities across very different risks** just to fill a batch: a critical injection
   should not wait behind a low-severity lint finding in the same PR.
7. **Order batches** by highest severity, then exploitability, so `B-01` is what to fix first.
