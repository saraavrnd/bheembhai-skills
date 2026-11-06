# Template guide — sdlc-assess-security-full

Guidance for filling this skill's templates, section by section. Read the part for a template
before you fill it. Do not copy this guidance into the output.

## `templates/security-audit.md.tmpl`

### Summary

The counts must equal the counts in `findings.json`. The sentences name the worst problems by
finding ID and where they cluster (a module, a dependency, the git history). No advice on what
to fix first; that is triage.

### Scope

One row per detected stack, with the file that proved it.

### Tool coverage

One row per tool the shared note lists for a detected stack, plus the four core tools, even when
the tool was not available. `not_applicable` is only for a tool whose stack is absent.

### OWASP Top 10 coverage

All ten rows, always. "Covered by" names the tools whose rules map to that category. "Gap" says
what no tool here can see, for example "access control rules need manual review or DAST".

### Findings

Every finding ID from `findings.json`, ordered by severity then path. Keep titles short; the
detail lives in `findings.json` and `raw/`.

### Gaps and limits

Missing or failed tools and the categories they would have covered; anything the scan could not
reach (generated code, vendored binaries); the vulnerability database dates.

## `templates/findings.schema.json`

The machine-readable contract. `sdlc-assess-findings-triage` reads it, and the verifier validates
it. Use `null` for an unknown CWE, OWASP category or line, never an empty string.
