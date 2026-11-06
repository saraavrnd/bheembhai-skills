# Template guide — sdlc-assess-security-rescan

Guidance for filling this skill's templates, section by section. Read the part for a template
before you fill it. Do not copy this guidance into the output.

## `templates/security-rescan.md.tmpl`

### Target findings

One row per finding in the bug's findings table, with the fingerprint copied exactly. Evidence is
the tool's current line of output for that file, or "not reported".

### New findings in the change

Only findings in files the diff changed. Write a single row `none` when there are none. A finding
on an unchanged line is listed with "no — unchanged line, other batch" and does not affect the
verdict.

### Tools run

At least one fenced block per tool, with the exact command and its trimmed output, so a reviewer
can repeat it.

### Manual actions still open

Copy the bug's manual actions (credential rotation, history rewrite). A PASS does not close them;
say so.

### Verdict

Exactly one `**Verdict:**` line. On BLOCK, list each change for `sdlc-deliver-code-implement` with
file and line.
