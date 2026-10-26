# Discovery Artifact Contract (shared by every discovery skill)

This contract is the single most important rule of the Discovery phase. Every discovery skill
MUST obey it. It is what separates a trustworthy knowledge base from confident fiction.

## The core rule: every claim is evidence-backed or flagged

Discovery artifacts are **reverse-engineered from code**. Fact and inference look identical on
the page unless forced apart. Therefore every statement in a discovery artifact MUST be one of:

- **`observed`** — directly verifiable in the code. Carries a `source:` pointer (`path:line`,
  or `path` for a whole-file fact, or a grep pattern that locates it). The reader (or the
  feature-dev agent) can jump to it and confirm.
- **`inferred`** — a reasonable conclusion drawn from observed facts, but not itself directly
  stated in the code. MUST carry a `basis:` naming what it was inferred *from* (the observed
  facts, files or other artifacts); a `note:` saying the same thing is also accepted, but
  `source:` alone is **not** — `source` is the observed-only pointer.
- **`uncertain`** — a guess, a gap, or a thing that couldn't be confirmed. Flag it loudly; do
  not launder it into a confident statement.

**A discovery artifact that states inference as fact is worse than no artifact** — every future
feature is then built on a claim the code does not support. If you cannot cite it and cannot
honestly label it inferred, leave it out.

## The consumer is the feature-dev agent, not a human reader

Artifacts are machine-read context loaded at the start of every feature. Consequences:

- **Structure over prose.** Fixed sections, predictable keys. The agent locates by section, not
  by reading paragraphs.
- **Every entry is a pointer into the code.** The artifact is an *index*, not a replacement for
  the code. It says "auth lives here" so the agent reads *there*; it does not re-describe the
  code at length.
- **Terse.** It is loaded every run, so length is cost. The expensive detail stays in the code.
  An artifact as long as the code it maps is useless.

## Output format

Each skill emits a Markdown artifact with YAML-structured entries. Every factual entry carries
`confidence` and the provenance that backs it: `source` when observed, `basis` (or `note`) when
inferred. Skeleton:

```yaml
artifact: <artifact-name>        # e.g. stack, api-surface, data-model
service: <service-name>          # which service this covers (polyglot/multi-service)
generated: <date>
stack_pack: <pack-name|none>     # which knowledge pack informed this (none = inference mode)

findings:
  - claim: "<a single, specific statement>"
    confidence: observed|inferred|uncertain
    source: "<path:line | path | grep:pattern>"   # required for observed (never enough for inferred)
    basis: "<the observed facts it was inferred from>"   # required for inferred (note: is accepted instead)
    note: "<optional short context>"
```

The verification checks enforce exactly this: `observed` needs a non-empty `source`, `inferred`
needs a non-empty `basis` or `note`, `uncertain` needs neither. An inferred entry that carries
only `source` **fails** — that is the most common first-draft rejection.

Prose is allowed only as a short `summary:` at the top (2–3 sentences, itself honest about
confidence). Everything load-bearing is a `findings` entry with a source.

## Exploration discipline (large codebases don't fit in context)

A real codebase is too big to read wholesale. Skills MUST explore *targeted*, not exhaustive:

1. Use the knowledge pack (when one exists) to go straight to the conventional location
   (`routes live in routes/api.php`) rather than reading everything.
2. Grep/glob to *locate*, then read only the located files.
3. When fanning out is needed, prefer a read-only search sub-agent over loading every file.
4. If the codebase is too large to cover, say so in `summary` and mark coverage as partial —
   never pretend full coverage from a partial read.

## No knowledge pack = graceful degradation, not failure

If `stack-detect` found no matching pack, downstream skills still run, but:
- `stack_pack: none`, and they operate in **inference mode**: explore-and-infer instead of
  look-in-the-known-place.
- Confidence skews toward `inferred`/`uncertain`. That is correct and honest — not a bug.
