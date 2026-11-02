# SK-001: Skilltester — a standalone app for running skills in isolation

**Status:** Proposed · **Date:** 2026-11-02 · **Deciders:** Saraav

This is the first decision record of the `bheembhai-skills` repo (prefix `SK-`, so the numbers never
collide with the platform's ADRs). References like "ADR-019" point at the **platform's** ADRs in
`bheembhai-mvp/docs/adr/`. The platform side of this decision (what the platform publishes for
the skilltester to consume) is the platform's **ADR-033**.

**Builds on (platform ADRs):** ADR-010 (pluggable auth, Cognito), ADR-012 (secure storage, Secrets
Manager), ADR-013 §3 (content-addressed skill bundles), ADR-014 (results over object storage),
ADR-019 (phase service, not built yet; not required), ADR-032 (skills catalog repo, `bheembhai-verify`, testbed tiers 3–4),
ADR-033 (shared runtime kit for external runners).

## Context

ADR-032 made `bheembhai-skills` the only place skills are edited, and defined four testbed tiers.
Tiers 1 (static) and 2 (verifier self-test on `examples/`) exist. Neither runs a skill.

Skill authors need to run a skill on its own, against real Jira and GitHub and a real model, in
the same runtime the platform uses, look at what it did, edit it, and run it again, many times.

A first draft put that inside the platform (sandbox projects, draft catalogs,
project skill drafts). It touched too much of the platform and made the process heavy. This
record makes it a **separate system, the skilltester**, that shares only versioned components
with the platform, the same way `bheembhai-verify` is shared today. Being separate gives:

- freedom over test data (its own projects, integrations, branches);
- no way to overwrite catalog or project skills, because it never writes to the platform;
- a platform that stays simple: nothing in its data model, engine or UI changes for testing.

## Decision

### 1. The skilltester lives in `bheembhai-skills`

```
bheembhai-skills/
├── skills/ config/ shared/ tools/      # catalog (unchanged)
├── suites/                             # saved test definitions (§6)
├── fixtures/                           # Jira seed data, sandbox-repo seed content
└── skilltester/
    ├── app/                            # web app: login, projects, runs, results
    ├── runner/                         # drives the agent container (also usable from the CLI)
    ├── kit.txt                         # pinned platform kit version (§2)
    └── docker-compose.yml              # app + database, local or on one host
```

`tools/build.py` packs only `skills/`, `config/` and `catalog.yaml`, so the skilltester never
enters a catalog release. Skill authors edit a skill and run it from the same checkout.

Stack: the same as the platform where possible (Python, FastAPI, server-rendered HTML with the
platform's theme, ADR-001; PostgreSQL or SQLite for a single host). The container runtime is
Docker on the skilltester host, like the platform's `DockerRuntime`.

### 2. Shared with the platform, pinned by version

The skilltester runs exactly what the platform runs because it uses the platform's own parts, at
pinned versions, and records them on every run.

| Component | What it is | How it's pinned | Source |
|---|---|---|---|
| **Agent image** | The container the platform runs for every step: `run_skill.sh` (clone, skill bundle, prompt, Claude Code, commit, push, result upload), in one go | Image **digest** from `kit.json`, pulled from the platform's **ECR** repo | Platform image build |
| **`bheembhai-verify`** | verify.yaml loader, builtin checks, verdict precedence | Via the kit (below) | Platform kit releases (ADR-032 §2a, platform ADR-033 §3) |
| **`bheembhai-stepkit`** (new) | The engine-side code that runs before a container starts (§2a) | Via the kit (below) | Platform kit releases |

**One pin: the platform kit.** The platform releases its exported parts together as a kit
(`kit-vN`, platform ADR-033 §3), each part with its own version, plus a `kit.json` bill of
materials listing the package versions, the agent image digest and the env contract version.
The skilltester pins **one kit version** in `skilltester/kit.txt` and installs and pulls exactly
what `kit.json` lists, a set the platform tested together. (The catalog's own CI keeps pinning
only `bheembhai-verify` in `requirements-verify.txt`, since that version is part of the catalog
contract.)

**Pulling the image from ECR.** The skilltester host has a read-only AWS identity allowed
`ecr:GetAuthorizationToken`, `ecr:BatchGetImage` and `ecr:GetDownloadUrlForLayer` on the agent
image repository only. The runner logs in with the ECR token and pulls by digest. Updating the
image, the verifier or the stepkit is a one-line change to `kit.txt`, in a PR like any other.

### 2a. The step kit

Most of what makes a run faithful already lives inside the agent image: `run_skill.sh` clones the
run branch, installs the skill bundle, renders the prompt, runs Claude Code, commits, pushes and
uploads the result, in one go. ADR-019's phase service is not built yet, so nothing here depends
on it. What lives in the **engine**, outside the image, is the code that prepares, launches and
reads back a step. That is what the skilltester
would otherwise have to copy, and what would drift. The step kit packages it:

- **Context builder:** the engine's `build_step_context`: `allowed_result_statuses`,
  `result_status_meanings`, `gate_follows` / `gate_role`, `reviewer_feedback`, `upstream_handoff`,
  rendered to `BB_CONTEXT`.
- **Env contract:** which variables `run_skill.sh` reads (git coordinates and `RUN_BRANCH`,
  `BB_MODEL` from the tier, vendor key and base URL, `BB_MCP_CONFIG` from the selected MCP
  servers, `BB_SKILL_URL` / `BB_SKILL_SHA256`, run and step ids, `BB_CONTEXT`, the ADR-014
  presigned PUT URLs) and how they are built from a project's integrations.
- **Branch:** create the run branch from a source branch through the GitHub API, as `_init_run`
  does.
- **Launch:** the engine's container launch spec and a launcher that runs it and waits for exit.
- **Outcome:** the reconciler's join of exit status and `bb_step_result.json` into a result
  status, so a run is classified exactly as in the platform.
- **Later, phases:** when ADR-019 ships, a phase client joins the kit and the runner can use it.
  The env contract version says which mode an image supports.
- **Shared auth and secrets helpers:** the `CognitoProvider` token verification (ADR-010) and the
  `SecureStorage` protocol with its Secrets Manager implementation (ADR-012).

The platform's engine is refactored to run on the same package: the code moves out of the engine
into the kit and the engine imports it back from its own folder (a path dependency, as with
`bheembhai-verify`), proven unchanged by golden tests (platform ADR-033 §1a). So it isn't a second
implementation. The step kit and the agent image change
together when the env contract changes, so a stepkit release names the image versions it
supports, and the skilltester refuses a mismatched pair.

### 3. Login with the platform's Cognito User Pool

- The skilltester is a **separate app client** in the platform's existing Cognito User Pool, with
  its own callback URL. Platform users sign in with the same username and password.
- Access needs membership of a Cognito group, e.g. `skilltester-users`, since runs spend tokens.
  The skilltester checks the group claim.
- Tokens are verified with the step kit's `CognitoProvider`. The skilltester keeps its own
  `users` table keyed by the Cognito `sub`. It never reads or writes the platform database.

### 4. Projects and integrations

A **test project** is the skilltester's own record. A logged-in user creates one and configures:

| Integration | Settings | Secret |
|---|---|---|
| Jira | Site URL, project key or template project, MCP server definition (the same Atlassian MCP the platform uses) | API token |
| GitHub | Sandbox code repository, base branch, MCP server definition (GitHub MCP) | Token scoped to the sandbox repo, plus read access to `bheembhai-skills` |
| AI models | One or more model profiles: vendor, base URL, tier → model mapping (as ADR-013 §1) | API key |

**Credentials live in AWS Secrets Manager**, under `skilltester/<project-id>/<integration>`. The
skilltester database stores only the secret reference. At step launch the runner fetches the
values and passes them to the container as env (ADR-019 D2a: injected at start, tmpfs, never
logged or written to disk). The skilltester's IAM role may read and write only the
`skilltester/*` secret path.

Tokens should be test-only: a Jira test site, a sandbox GitHub repo, a test model key. The
skilltester warns when a GitHub integration points at a repository that a platform project also
uses.

Project members: the creator is the owner and can add other skilltester users. Every member
can run tests in the project. Only the owner can change integrations.

### 5. A run: one skill, two branches

A run tests **one skill**. The user picks:

1. **Skills branch:** a branch of `bheembhai-skills` (e.g. `test/saraav/fix-reproduce`). At run
   start it is resolved to a **commit SHA** and the skill is packed with `tools/build.py` into a
   content-addressed bundle, exactly as a release would pack it. The bundle is uploaded to the
   skilltester's own S3 bucket and handed to the container by presigned URL (`BB_SKILL_URL`,
   `BB_SKILL_SHA256`). The same SHA is packed once and reused.
2. **Input branch:** a branch of the project's sandbox code repo holding the state the skill
   starts from (code, plus upstream artifacts such as `bug-triage.md`).
3. **Context (optional):** the workflow and step to take the vocabulary from (default: a workflow
   in the skills branch's `config/` that uses this skill), plus optional `reviewer_feedback` or
   `upstream_handoff`, to test a send-back or a BLOCK hand-off.
4. **Model profile and tier:** the skill's `model:` tier by default, or a fixed cheaper tier for
   smoke runs. Turn and spend caps per run.

The runner then does what the engine does for one step today, using the step kit:

1. **Branch:** create a **new run branch** `skilltest/<run-id>` from the input branch's head
   through the GitHub API, and record that head SHA as the baseline. The input branch is never
   written to, so test data can't be overwritten.
2. **Launch:** build the env (presigned URLs point at the skilltester's own S3 bucket), start the
   pinned agent image with Docker, and follow `progress.json` and `agent.log` while it runs.
   `run_skill.sh` clones the run branch, runs the skill, commits and pushes to it, and uploads
   `bb_step_result.json`.
3. **Outcome:** on exit, classify the result exactly as the engine's reconciler does.
4. **Verify (in the skilltester):** check out the run branch and run the pinned
   `bheembhai-verify` on it, with the baseline SHA for `must_change` and preconditions, and the
   skill's `verify.yaml` from the pinned skills commit. Verification runs outside the agent
   container, so the agent can't edit what grades it. If verification later moves into the image
   (skill-verification design §7), the runner reads its result instead, and the skilltester's
   verifier stays for re-verify.
- **Chaining by hand:** a run's output branch can be the next run's input branch. That's how a
  sequence (triage → reproduce → root cause → implement) is tested one skill at a time, with each
  step's result kept.

**Jira test data.** Before a run, the runner can seed issues from `fixtures/<name>/jira.json`
through the Jira REST API. Fixture files use aliases (`{{bug}}`), replaced with the real keys at
seed time. The runner records the Jira state after the run (for assertions and display) and
cleans up at the end, with a nightly sweep for anything left behind. Open question: a fresh Jira
project per run, or one project with a `skilltest-<run>` label on everything.

### 6. Results

All data is the skilltester's own: database rows plus `s3://<skilltester-bucket>/runs/<run-id>/`
for the bundle, `bb_step_result.json`, logs and the transcript. Langfuse traces, if enabled,
carry `env = skilltest` (or go to a separate Langfuse project).

- **Run page:** skill and skills SHA, input and output branches, agent image digest, stepkit and
  verifier versions; the verdict the agent claimed against the verdict after verification
  (overturned or not); each L0/L1 check (L2 when enabled); the diff (input branch → run branch);
  Jira changes; turns, tokens, cost; trace link.
- **Skill history:** every run of one skill, one row per run, with SHA, input branch, verdict
  and checks, so it's easy to see which edit fixed or broke what.
- **Compare:** two runs side by side, with checks that flipped highlighted.
- **Re-run:** the same inputs with the skills branch's latest SHA (after an edit).
- **Re-verify only:** when only `verify.yaml` changed, grade the existing output branch again with
  the new manifest. No agent, no model tokens. It shows which checks flipped. This is the cheap
  loop for tuning checks.
- **Saved suites** (`suites/*.yaml`): a named set of runs (skill + input branch + context +
  expectations). They can be run from the UI or the CLI (§7), and are the basis for a nightly run.

### 6a. verify.yaml changes

verify.yaml travels in the skill bundle, so a run grades with the branch's version. Builtins come
from the pinned `bheembhai-verify` and are not changed in the skilltester; a builtin change is a
platform verifier release. Before packing, the runner runs `bheembhai-verify lint` and
`selftest` on the skill and refuses to start if they fail, and checks that `catalog.yaml`'s
`requires_verify` accepts the pinned version.

### 7. The CLI

`python -m skilltester.runner run --project <p> --skill <s> --skills-ref <branch> --input <branch>`
runs the same runner without the web app (same pins, same results in the same database or a
local folder). It's for quick loops and for CI: a `run-behaviour` PR label or a nightly suite
run in this repo (ADR-032 tier 3).

### 8. From a tested skill to the platform

Nothing in the skilltester reaches the platform. The path stays ADR-032's:

1. Edit on a branch, test in the skilltester.
2. Open a PR. CI runs tiers 1–2. The PR description links the skilltester runs at its head SHA.
3. Merge, tag, import from the platform's Admin → Catalog.

This applies to project team members too. Anyone with skilltester access can push a branch,
test it and open a PR. A project's own in-platform customizations (ADR-032 §4) are unchanged
and out of scope here.

### 9. Data model (skilltester database)

| Table | Key columns |
|---|---|
| `users` | `id`, `cognito_sub` UNIQUE, `email`, `name` |
| `projects` | `id`, `name`, `owner_id`, `created_at` |
| `project_members` | `project_id`, `user_id`, `role` (owner, member) |
| `integrations` | `id`, `project_id`, `kind` (jira, github, ai_model), `config` JSONB, `secret_ref`, `mcp` JSONB, `verified_at` |
| `skill_bundles` | `skills_commit_sha`, `skill`, `bundle_sha256`, `s3_key` (packed once per SHA) |
| `runs` | `id`, `project_id`, `user_id`, `skill`, `skills_ref`, `skills_commit_sha`, `input_branch`, `run_branch`, `context` JSONB, `model_profile_id`, `tier`, `agent_image_digest`, `stepkit_version`, `verify_version`, `state`, `claimed_verdict`, `final_verdict`, `verification` JSONB, `cost_usd`, `parent_run_id` (re-run or re-verify), `kind` (run, reverify), timestamps |
| `run_jira` | `run_id`, `aliases` JSONB, `state_after` JSONB, `cleaned_at` |
| `suites` | `id`, `project_id`, `name`, `definition` JSONB, `source_path` |

## Explicit non-goals (v1)

- Any change to the platform's data model, engine or UI for testing.
- Writing to the platform catalog or to project skills.
- Changing builtin checks (that is a `bheembhai-verify` release).
- Running workflows with gates and routing. The skilltester runs one skill per run; engine
  behaviour stays ADR-032's tier 4 (local platform deploy).
- Mocked models or fake Jira/GitHub by default. A fault-injecting proxy in front of an MCP is a
  later option for failure cases.

## Consequences

- Skill authors get an edit → run → compare loop in the real runtime, with no risk to the
  platform or its projects.
- The platform's only work is publishing what it already has, as versioned parts: the agent image
  (already in ECR), `bheembhai-verify` (already released), and a new small `bheembhai-stepkit`
  extracted from the engine.
- The skilltester depends on three AWS services: Cognito (login), ECR (image), Secrets Manager
  (tokens), plus its own S3 bucket. Its role needs exactly those permissions.
- A new app to run and maintain, though small, and in the same repo as the skills it tests.
- Real Jira and GitHub cost time and rate limits; seeding and cleanup add up to a minute per run.
- Test data is branches, which are cheap to create and impossible to overwrite, but someone has to
  curate good input branches per skill.

## Rough size (one developer; to be checked against the platform code)

| Phase | What | Size |
|---|---|---|
| S0 | Platform (tracked in platform ADR-033): extract `bheembhai-stepkit` (context builder, env contract, branch, launch, outcome, Cognito and Secrets Manager helpers), `kit-v*` release job with `kit.json`, image ↔ stepkit compatibility | 1–2 weeks |
| S1 | Runner + CLI: ECR pull, bundle packing, branch + launch + outcome via the step kit, verification with `bheembhai-verify`, results to S3 and DB, re-verify | 2 weeks |
| S2 | Web app: Cognito login, projects, integrations with Secrets Manager, run form, run page | 2–3 weeks |
| S3 | Jira seeding and cleanup, skill history, compare, suites, nightly CI run | 2 weeks |
| — | Input branches for the bug-fix chain in the sandbox repo, Jira fixture data | 1 week, alongside |

## Open questions

1. Jira isolation: a fresh project per run, or one shared project with run labels?
2. Should verification stay in the skilltester for good, or move into the agent image later
   (skill-verification design §7)? Either way the runner works; this decides only where the
   result comes from.
3. Where does the skilltester run: a laptop with Docker, one EC2 host, or ECS? (Docker access is
   needed for the runtime.)
4. One stepkit package, or split auth/secrets helpers into their own package?

## Rollout

1. S0 in the platform repo (platform ADR-033); first `kit-v*` release to pin.
2. S1 in `bheembhai-skills/skilltester`; pilot with the CLI on the bug-fix skills.
3. S2 web app; create the Cognito app client and group, the S3 bucket, the IAM role.
4. S3 and a nightly suite run in CI.

## Tests (what pins this)

- The runner refuses an agent image digest and stepkit version that the stepkit says are
  incompatible.
- A run never pushes to its input branch; the output always goes to `skilltest/<run-id>`.
- Packing the same skills commit twice gives the same bundle SHA (shared with ADR-032).
- A user outside the `skilltester-users` group can't sign in.
- Secret values never appear in the database, logs, results or run pages.
- Re-verify calls no model and grades with the new commit's verify.yaml.
- Jira seeding replaces aliases with real keys, and cleanup leaves no issues behind.
- The platform engine and the skilltester build the same `BB_CONTEXT` for the same workflow step
  (both import the step kit).

## References

- ADR-001, ADR-010, ADR-012, ADR-013 §3, ADR-014, ADR-019, ADR-032
- `skill-verification/skill-verification-design.md`
- `skill-verification/discovery-fix/tools/` (`run_examples.py`, `build_fixture.py`)
- Platform ADR-033: shared runtime kit for external runners (the platform half of this decision)
