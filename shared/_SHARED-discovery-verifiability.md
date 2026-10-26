# Discovery Self-Check — producing a trustworthy artifact

> Optional shared guidance for discovery skills. Not a skill itself.

**The outcome vocabulary (BB_OUTCOME / BB_REVIEW and what `completed` / `BLOCK` /
`changes_requested` / `escalation_required` / `failed_execution` mean) is owned by BheemBhai and
injected into every skill at runtime.** Do not restate what the words mean in a skill — the
orchestrator is the single source of truth, and a skill's own copy would drift from it. A skill's
`## Outcomes` section, where it has one, names only the calls `verify.yaml` cannot make in code. This note covers only the
discovery-specific part the orchestrator does NOT provide: how an *extraction* judges its own output.

## Why discovery needs a self-check

Unlike a delivery skill, a discovery skill has no test suite to run — "did it work?" cannot be
answered by green tests. So the honesty of a discovery artifact rests on the evidence discipline in
`_SHARED-discovery-contract.md`, checked by the skill against its own output before it finishes.

## The self-check (run it before deciding the outcome applies)

1. **Every `observed` claim's `source:` resolves** — the cited file/line exists and says what the
   claim says. A claim whose source doesn't resolve is downgraded to `uncertain` or removed, never
   left as a false `observed`.
2. **Nothing uncited is asserted as fact** — if it can't be cited and can't honestly be labelled
   `inferred`, it is cut.
3. **Coverage is truthful** — `partial: true` and a summary note whenever the codebase was too
   large to cover fully. A partial pass never claims completeness.
4. **Confidence is calibrated** — `observed` only where directly verifiable; `inferred` states what
   it was inferred from; `uncertain` used freely instead of guessing.

If the artifact would be mostly guesswork — a required upstream hand-off is missing/malformed, or
the code can't be read well enough for a trustworthy result — that is a principled stop, not a
success: the skill should NOT emit a confident-looking artifact. (Which runtime outcome word that
maps to is BheemBhai's vocabulary, injected at runtime — the skill just applies it honestly.)

## Focusing the review signal

When the skill reports which artifact a reviewer should look at, aim the attention at the
**low-confidence, high-impact** claims (the `inferred` / `uncertain` entries) — that is where
reverse-engineered knowledge is most likely wrong and where a human-review gate earns its keep.
