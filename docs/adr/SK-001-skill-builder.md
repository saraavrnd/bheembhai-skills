# SK-001: Skill builder — create, test, scan and ready platform skills

**Status:** Proposed · **Date:** 2026-11-02 · **Deciders:** Saraav

This is the first decision record of the `bheembhai-skills` repo (prefix `SK-`, so the numbers never
collide with the platform's ADRs). References like "ADR-019" point at the **platform's** ADRs in
`bheembhai-mvp/docs/adr/`. The platform side of this decision (what the platform publishes for
the skill builder to consume) is the platform's **ADR-033**.

**Builds on (platform ADRs):** ADR-010 (pluggable auth, Cognito), ADR-012 (secure storage, Secrets
Manager), ADR-013 §3 (content-addressed skill bundles), ADR-014 (results over object storage),
ADR-019 (phase service, not built yet; not required), ADR-032 (skills catalog repo, `bheembhai-verify`, testbed tiers 3–4),
ADR-033 (shared runtime kit for external runners), ADR-034 (skill security scanning).

## Context

`bheembhai-skills` holds **platform skills only**. A project gets skills only through the
platform catalog (catalog import, ADR-032); it never pulls from this repo directly. Platform and
project admins can still create and edit skills inside the platform, and those edits go through
the platform's draft → scan → review flow (platform ADR-034). This record covers the other path:
authoring a platform skill in this repo.

ADR-032 made `bheembhai-skills` the only place skills are edited, and defined four testbed tiers.
Tiers 1 (static) and 2 (verifier self-test on `examples/`) exist. Neither runs a skill.

Skill authors need to run a skill on its own, against real Jira and GitHub and a real model, in
the same runtime the platform uses, look at what it did, edit it, and run it again, many times.

A first draft put that inside the platform (sandbox projects, draft catalogs,
project skill drafts). It touched too much of the platform and made the process heavy. This
record makes it a **separate system, the skill builder** (module `bheembhai-skill-builder`), that
shares only versioned components with the platform, the same way `bheembhai-verify` is shared
today. It takes a skill from nothing to Ready: create it (or clone an existing one), run it,
security-check it, and hand it to the catalog as a PR. Being separate gives:

- freedom over test data (its own projects, integrations, branches);
- no way to overwrite catalog or project skills, because it never writes to the platform;
- a platform that stays simple: nothing in its data model, engine or UI changes for testing.

## Decision

### 1. The skill builder lives in `bheembhai-skills`

```
bheembhai-skills/
├── skills/ config/ shared/ tools/      # catalog (unchanged)
├── suites/                             # saved test definitions (§6)
├── fixtures/                           # Jira seed data, sandbox-repo seed content
└── skill-builder/
    ├── app/                            # web app: login, projects, runs, results
    ├── runner/                         # drives the agent container (also usable from the CLI)
    ├── kit.txt                         # pinned platform kit version (§2)
    └── docker-compose.yml              # app + database, local or on one host
```

`tools/build.py` packs only `skills/`, `config/` and `catalog.yaml`, so the skill builder never
enters a catalog release. Skill authors edit a skill and run it from the same checkout.

Stack: the same as the platform where possible (Python, FastAPI, server-rendered HTML with the
platform's theme, ADR-001; PostgreSQL or SQLite for a single host). The container runtime is
Docker on the skill builder host, like the platform's `DockerRuntime`.

### 1a. Create and clone

A **build** is one skill being authored. It lives on its own branch of `bheembhai-skills`,
`build/<skill-name>`, cut from `main`. The skill builder starts one in two ways:

- **Create:** the user gives a name and a one-line description. The skill builder writes the
  default structure to `skills/<skill-name>/`:

  ```
  skills/<skill-name>/
  ├── SKILL.md        # frontmatter (name, description, compatibility, model tier) + body sections
  ├── verify.yaml     # v2 manifest stub: claims, no checks yet (§6a)
  ├── references/     # empty, with a README saying what goes here
  ├── templates/
  └── examples/
  ```

  The scaffold comes from `skill-builder/scaffold/`, kept in step with the current verify.yaml
  version, so a new skill passes tier 1 as soon as it's created (with "no checks" as a warning).

- **Clone:** the user picks an existing catalog skill and gives a **new name**. The skill builder
  copies the whole folder to `skills/<new-name>/` and rewrites `name:` in the frontmatter. The
  result is a new skill with no link back to the original; the original is never changed. To
  change an existing skill itself, the user edits it on a branch (§8), not through Clone.

Names must be unique in the catalog and follow `sdlc-<area>-<action>`. Both refuse a name that
already exists on `main` or on another open build.

There is **no versioning inside the skill builder**. A build is a branch; each save is a commit;
runs and scans are recorded against the commit SHA. Versions exist only once the skill is in the
catalog: the catalog release tag, then the platform's own revision numbers after import
(ADR-034 §9). An enhancement is a new build (a clone, or an edit branch), not a version of the
old one.

### 1b. Ready

A build is **Ready** at a commit SHA when all of these hold at that SHA:

| Check | Where it comes from |
|---|---|
| Manifest valid | Tier 1: `bheembhai-verify` on the skill's `verify.yaml`, and `tools/check.py` |
| Passing run | At least one run (§5) whose final verdict, after verification, is pass |
| Static security check | Not `DO_NOT_INSTALL` (§6b) |
| LLM security check | Completed, or recorded as unavailable; findings shown, never blocking (§6b) |

Any new commit clears Ready; the checks re-run on the new SHA (runs on the old SHA stay visible
in the history). The build page shows the four checks and a **Submit to catalog** button,
enabled only when all four hold. It opens the PR described in §8.

Ready here means "ready to propose". It is not the platform's Ready: the skill becomes usable in
projects only after the PR merges, a release is tagged, and the platform imports it, where the
platform scans it again (ADR-034 §6) and its root `verify.yaml` sets `is_ready_to_use`.

### 2. Shared with the platform, pinned by version

The skill builder runs exactly what the platform runs because it uses the platform's own parts, at
pinned versions, and records them on every run.

| Component | What it is | How it's pinned | Source |
|---|---|---|---|
| **Agent image** | The container the platform runs for every step: `run_skill.sh` (clone, skill bundle, prompt, Claude Code, commit, push, result upload), in one go | Image **digest** from `kit.json`, pulled from the platform's **ECR** repo | Platform image build |
| **Scanner image** | The platform's scanner container (ADR-034 §4, §7): `bheembhai-skillscan` and SkillSpector on a slim Python base. It reads one skill bundle and writes one report | Image **digest** from `kit.json`, pulled from the platform's **ECR** repo. Never a tag such as `:latest` | Platform image build |
| **`bheembhai-verify`** | verify.yaml loader, builtin checks, verdict precedence | Via the kit (below) | Platform kit releases (ADR-032 §2a, platform ADR-033 §3) |
| **`bheembhai-stepkit`** (new) | The engine-side code that runs before a container starts (§2a) | Via the kit (below) | Platform kit releases |

**One pin: the platform kit.** The platform releases its exported parts together as a kit
(`kit-vN`, platform ADR-033 §3), each part with its own version, plus a `kit.json` bill of
materials listing the package versions, the agent image digest and the env contract version.
The skill builder pins **one kit version** in `skill-builder/kit.txt` and installs and pulls exactly
what `kit.json` lists, a set the platform tested together. (The catalog's own CI keeps pinning
only `bheembhai-verify` in `requirements-verify.txt`, since that version is part of the catalog
contract.)

**Pulling the image from ECR.** The skill builder host has a read-only AWS identity allowed
`ecr:GetAuthorizationToken`, `ecr:BatchGetImage` and `ecr:GetDownloadUrlForLayer` on the agent
and scanner image repositories only. The runner logs in with the ECR token and pulls both by
digest. A digest, not `:latest`, is what makes the verdict here match the platform's: a moving tag
would let the two scan with different SkillSpector versions. Updating an image, the verifier or
the stepkit is a one-line change to `kit.txt`, in a PR like any other.

### 2a. The step kit

Most of what makes a run faithful already lives inside the agent image: `run_skill.sh` clones the
run branch, installs the skill bundle, renders the prompt, runs Claude Code, commits, pushes and
uploads the result, in one go. ADR-019's phase service is not built yet, so nothing here depends
on it. What lives in the **engine**, outside the image, is the code that prepares, launches and
reads back a step. That is what the skill builder
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
supports, and the skill builder refuses a mismatched pair.

### 3. Login with the platform's Cognito User Pool

- The skill builder is a **separate app client** in the platform's existing Cognito User Pool, with
  its own callback URL. Platform users sign in with the same username and password.
- Access needs membership of a **dedicated Cognito group, `skill-builders`**. Only its members can
  create, clone, run, scan and submit skills: they write to the catalog repo and spend tokens.
  Platform users outside the group can't sign in. The skill builder checks the `cognito:groups`
  claim on every request, not only at login, so removing someone from the group takes effect
  when their token expires (one hour at most).
- Group membership is managed in Cognito by a platform admin. The skill builder has no user
  admin screen of its own.
- Tokens are verified with the step kit's `CognitoProvider`. The skill builder keeps its own
  `users` table keyed by the Cognito `sub`. It never reads or writes the platform database.

### 4. Projects and integrations

A **test project** is the skill builder's own record. A logged-in user creates one and configures:

| Integration | Settings | Secret |
|---|---|---|
| Jira | Site URL, project key or template project, MCP server definition (the same Atlassian MCP the platform uses) | API token |
| GitHub | Sandbox code repository, base branch, MCP server definition (GitHub MCP) | Token scoped to the sandbox repo, plus push access to `build/*` branches of `bheembhai-skills` and PR creation (§1a, §8) |
| AI models | One or more model profiles: vendor, base URL, tier → model mapping (as ADR-013 §1) | API key |

**Credentials live in AWS Secrets Manager**, under `skill-builder/<project-id>/<integration>`. The
skill builder database stores only the secret reference. At step launch the runner fetches the
values and passes them to the container as env (ADR-019 D2a: injected at start, tmpfs, never
logged or written to disk). The skill builder's IAM role may read and write only the
`skill-builder/*` secret path.

Tokens should be test-only: a Jira test site, a sandbox GitHub repo, a test model key. The
skill builder warns when a GitHub integration points at a repository that a platform project also
uses.

Project members: the creator is the owner and can add other skill builder users. Every member
can run tests in the project. Only the owner can change integrations.

### 5. A run: one skill, two branches

A run tests **one skill**. The user picks:

1. **Skills branch:** a branch of `bheembhai-skills` (e.g. `test/saraav/fix-reproduce`). At run
   start it is resolved to a **commit SHA** and the skill is packed with `tools/build.py` into a
   content-addressed bundle, exactly as a release would pack it. The bundle is uploaded to the
   skill builder's own S3 bucket and handed to the container by presigned URL (`BB_SKILL_URL`,
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
2. **Launch:** build the env (presigned URLs point at the skill builder's own S3 bucket), start the
   pinned agent image with Docker, and follow `progress.json` and `agent.log` while it runs.
   `run_skill.sh` clones the run branch, runs the skill, commits and pushes to it, and uploads
   `bb_step_result.json`.
3. **Outcome:** on exit, classify the result exactly as the engine's reconciler does.
4. **Verify (in the skill builder):** check out the run branch and run the pinned
   `bheembhai-verify` on it, with the baseline SHA for `must_change` and preconditions, and the
   skill's `verify.yaml` from the pinned skills commit. Verification runs outside the agent
   container, so the agent can't edit what grades it. If verification later moves into the image
   (skill-verification design §7), the runner reads its result instead, and the skill builder's
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

All data is the skill builder's own: database rows plus `s3://<skill-builder-bucket>/runs/<run-id>/`
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
from the pinned `bheembhai-verify` and are not changed in the skill builder; a builtin change is a
platform verifier release. Before packing, the runner runs `bheembhai-verify lint` and
`selftest` on the skill and refuses to start if they fail, and checks that `catalog.yaml`'s
`requires_verify` accepts the pinned version.

### 6b. Security scan (platform ADR-034)

A test run hands the skill real Jira, GitHub and model credentials, so the skill builder scans a
skill before it runs it, with the same two SkillSpector stages and the same pinned
`bheembhai-skillscan` package the platform uses (ADR-034 §7). A skill gets the same verdict here,
in this repo's CI and in the platform.

- **Runs in the scanner image, never in the app process.** The scanner parses untrusted skill
  content, so the runner starts a short-lived scanner container (the kit's digest, §2) for each
  stage, as the platform's Engine does. The bundle is mounted read-only and the report is written
  to an output mount. The static stage runs with no network. The LLM stage gets the model key as
  env only and network access only to the model endpoint. Each container has a 10-minute limit,
  and a timeout is a failed scan. The scanner's MCP server mode is never used.
- **No scan on save**, as in the platform (ADR-034 §2). Scans run when the author asks for them
  and before every run.
- **Static check** before every run on the exact bundle the run will use, and from a **Security
  check** button on the skill page. Cached by content sha. `DO_NOT_INSTALL`, a CRITICAL finding or
  incomplete coverage refuses the run, with the findings shown. Accepted findings cannot clear a
  block (ADR-034 §7). There is no override: fix the skill and save.
- **LLM check** is queued by the **Security check** button only after the static check passes for
  that content sha; a run never waits for it. The author picks the model from the test project's
  **AI models** profiles (§4); only the project owner changes the default, and the key comes from
  Secrets Manager like any other run. The LLM check never refuses a run. Its findings are shown for
  the author to act on; there is no human-review step here.
- **Security tab** on the skill and run pages, next to the verify results (§6): score,
  recommendation, each finding with severity, rule, file and line, and which model ran the LLM
  check.
- **CLI:** `python -m skill_builder.runner scan --project <p> --skill <s> --skills-ref <branch>`
  runs both stages without a test run; `--static-only` skips the model. Both start the same scanner
  container as the app, so the host needs Docker.
- **Not a gate for the platform.** The skill builder never writes to the platform (§8). Its scan is
  advice for the author; this repo's CI and the platform scan again.

This repo's CI (`ci.yml`) also runs the static check on every PR, in the same scanner image (pulled
by the digest in `skill-builder/kit.txt`), with
SARIF uploaded so findings show on the PR. It skips the LLM check, because the platform runs both
stages at import (ADR-034 §6). Accepted findings live in `.skillspector-baseline.yaml`, each with a
reason, and need a CODEOWNERS review.

### 7. The CLI

`python -m skill_builder.runner run --project <p> --skill <s> --skills-ref <branch> --input <branch>`
runs the same runner without the web app (same pins, same results in the same database or a
local folder). It's for quick loops and for CI: a `run-behaviour` PR label or a nightly suite
run in this repo (ADR-032 tier 3).

### 8. From a Ready build to the platform

Nothing in the skill builder writes to the platform. The path stays ADR-032's:

1. **Submit to catalog** (§1b) opens a PR from `build/<skill-name>` to `main`. The PR description
   lists the Ready checks at the head SHA with links to the run and the scan reports. The PR is
   opened with the user's own GitHub identity, so the author is the person, not the app.
2. CI runs tiers 1–2 and the static security check. CODEOWNERS review it.
3. Merge, tag a catalog release, import from the platform's Admin → Catalog. The platform scans
   the imported skill again before it can be used (ADR-034 §6).

Changing an existing catalog skill (a fix, not a new skill) follows the same path from an edit
branch: open the skill on a branch in the skill builder, run, scan, Ready, Submit. Review
comments on the PR are fixed on the same branch, which clears Ready until the checks pass again.

### 9. Data model (skill builder database)

| Table | Key columns |
|---|---|
| `users` | `id`, `cognito_sub` UNIQUE, `email`, `name` |
| `builds` | `id`, `skill`, `kind` (create, clone, edit), `cloned_from` (skill name, clone only), `branch`, `created_by`, `head_sha`, `ready_sha` (NULL until the §1b checks hold), `pr_url`, `state` (open, submitted, merged, abandoned), timestamps |
| `projects` | `id`, `name`, `owner_id`, `created_at` |
| `project_members` | `project_id`, `user_id`, `role` (owner, member) |
| `integrations` | `id`, `project_id`, `kind` (jira, github, ai_model), `config` JSONB, `secret_ref`, `mcp` JSONB, `verified_at` |
| `skill_bundles` | `skills_commit_sha`, `skill`, `bundle_sha256`, `s3_key` (packed once per SHA) |
| `runs` | `id`, `project_id`, `user_id`, `skill`, `skills_ref`, `skills_commit_sha`, `input_branch`, `run_branch`, `context` JSONB, `model_profile_id`, `tier`, `agent_image_digest`, `stepkit_version`, `verify_version`, `state`, `claimed_verdict`, `final_verdict`, `verification` JSONB, `cost_usd`, `parent_run_id` (re-run or re-verify), `kind` (run, reverify), timestamps |
| `run_jira` | `run_id`, `aliases` JSONB, `state_after` JSONB, `cleaned_at` |
| `suites` | `id`, `project_id`, `name`, `definition` JSONB, `source_path` |

## Explicit non-goals (v1)

- Versioning inside the skill builder. A build is a branch; versions start at the catalog release.
- Skills that live only in a project. Projects get skills from the platform catalog; their own
  in-platform edits are the platform's flow (ADR-034).
- Any change to the platform's data model, engine or UI for testing.
- Writing to the platform catalog or to project skills.
- Changing builtin checks (that is a `bheembhai-verify` release).
- Running workflows with gates and routing. The skill builder runs one skill per run; engine
  behaviour stays ADR-032's tier 4 (local platform deploy).
- Mocked models or fake Jira/GitHub by default. A fault-injecting proxy in front of an MCP is a
  later option for failure cases.

## Consequences

- Skill authors get an edit → run → compare loop in the real runtime, with no risk to the
  platform or its projects.
- The platform's only work is publishing what it already has, as versioned parts: the agent image
  (already in ECR), `bheembhai-verify` (already released), and a new small `bheembhai-stepkit`
  extracted from the engine.
- The skill builder depends on three AWS services: Cognito (login), ECR (image), Secrets Manager
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
| S2 | Web app: Cognito login with the `skill-builders` group, Create (scaffold) and Clone, build page with the Ready checks and Submit to catalog, projects, integrations with Secrets Manager, run form, run page | 3–4 weeks |
| S3 | Jira seeding and cleanup, skill history, compare, suites, nightly CI run | 2 weeks |
| — | Input branches for the bug-fix chain in the sandbox repo, Jira fixture data | 1 week, alongside |

## Open questions

1. Jira isolation: a fresh project per run, or one shared project with run labels?
2. Should verification stay in the skill builder for good, or move into the agent image later
   (skill-verification design §7)? Either way the runner works; this decides only where the
   result comes from.
3. Where does the skill builder run: a laptop with Docker, one EC2 host, or ECS? (Docker access is
   needed for the runtime.)
4. One stepkit package, or split auth/secrets helpers into their own package?

## Rollout

1. S0 in the platform repo (platform ADR-033); first `kit-v*` release to pin.
2. S1 in `bheembhai-skills/skill-builder`; pilot with the CLI on the bug-fix skills.
3. S2 web app with Create, Clone, Ready and Submit to catalog; create the Cognito app client and
   the `skill-builders` group, the S3 bucket, the IAM role.
4. S3 and a nightly suite run in CI.

## Tests (what pins this)

- The runner refuses an agent image digest and stepkit version that the stepkit says are
  incompatible.
- A run never pushes to its input branch; the output always goes to `skilltest/<run-id>`.
- Packing the same skills commit twice gives the same bundle SHA (shared with ADR-032).
- A user outside the `skill-builders` group can't sign in, and a token without the group claim
  is refused on every endpoint.
- Create writes the default structure, and the new skill passes tier 1 with no edits.
- Clone writes a new folder under the new name with `name:` rewritten, and leaves the source
  skill's files unchanged.
- Create and Clone refuse a name that exists on `main` or on another open build.
- A new commit on a build clears `ready_sha`; Submit to catalog stays disabled until all four
  §1b checks pass at the head SHA.
- Secret values never appear in the database, logs, results or run pages.
- Re-verify calls no model and grades with the new commit's verify.yaml.
- Jira seeding replaces aliases with real keys, and cleanup leaves no issues behind.
- A skill whose static check is `DO_NOT_INSTALL` never starts a run; the LLM check is never called
  for it.
- The runner refuses a scanner or agent image given by tag instead of digest.
- A static scan container has no network.
- The skill builder and the platform give the same scan verdict for the same bundle (both pin
  `bheembhai-skillscan`).
- The platform engine and the skill builder build the same `BB_CONTEXT` for the same workflow step
  (both import the step kit).

## References

- ADR-001, ADR-010, ADR-012, ADR-013 §3, ADR-014, ADR-019, ADR-032
- `skill-verification/skill-verification-design.md`
- `skill-verification/discovery-fix/tools/` (`run_examples.py`, `build_fixture.py`)
- Platform ADR-033: shared runtime kit for external runners (the platform half of this decision)
- Platform ADR-034: skill security scanning and approved revisions (§6b)
