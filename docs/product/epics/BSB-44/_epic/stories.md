# Stories — BSB-44 (Integrations & credentials)

Epic BSB-44 covers FR-029, FR-030, FR-031, FR-032, FR-033, FR-034, FR-035, FR-036, FR-128, FR-129,
NFR-004 and NFR-006. It is decomposed into the 7 stories below; every one of those 12 requirements
is covered by at least one story's acceptance criteria.

**Prerequisite: project, owner guard and settings container (FA-4 / BSB-43).** BSB-43 owns the
test project, `projects.owner_id`, the owner-only guard and its HTTP 403
`{"error":"owner_required"}` response, the project settings page
`GET /projects/{project_id}/settings`, and the integration write route
`PUT /api/projects/{project_id}/integrations/{kind}` with its `(project_id, kind)` row identity,
`integration_id` (`^int_[A-Za-z0-9]{10}$`), non-secret `config` object, and at most one
`integrations` row per `(project_id, kind)` (BSB-43-PENDING-5). Every route in this epic is an
authoring route and inherits FA-1's gate: a request with no valid session gets HTTP 401
`{"error":"authentication_required"}`, and a request whose current `cognito:groups` claim lacks
`skill-builders` gets HTTP 403 `{"error":"membership_required"}` before any integration data is
read or written. The builder database is `postgres://builder-db:5432/skillbuilder`.

**What this epic adds to the FA-4 write route.** BSB-44 keeps BSB-43's route and owner guard and
adds two optional body fields: `credential` (a non-empty string) and `mcp` (an object, Jira and
source-control only). A body without `credential` leaves the row's `secret_ref` unchanged — NULL on
a newly created row, which is BSB-43-PENDING-5's contract — so a configuration-only write remains
valid and verification later reports `credential_missing`. A body with `credential` writes the
value to the external secret store and sets `secret_ref`; the row's `config` never contains the
value.

**Fixture accounts.** The Cognito fixture is BSB-39's:

| Account | Subject | Display name | Current `cognito:groups` | `users` row |
|---------|---------|--------------|--------------------------|-------------|
| `alice@example.test` | `sub-12345` | Alice Author | `["skill-builders"]` | `U_alice` |
| `bob@example.test` | `sub-67890` | Bob Builder | `["skill-builders"]` | `U_bob` |
| `casey@example.test` | `sub-99999` | Casey Newcomer | `["skill-builders"]` | `U_casey` |
| `dana@example.test` | `sub-13579` | Dana Owner | `["skill-builders"]` | `U_dana` |

`U_alice`, `U_bob`, `U_casey` and `U_dana` stand for the actual `users.id` UUID value read from the
database (`SELECT id FROM users WHERE cognito_sub = 'sub-12345'` for `U_alice`, and likewise for the
other subjects); a test substitutes the value. Bob and Casey have no `project_members` row for
either fixture project unless a scenario's `Given` says so.

**Fixture projects.** The fixture builder database contains these `projects` and
`project_members` rows and no others; scenarios add further membership rows only where their
`Given` says so:

| `projects.id` | `name` | `owner_id` | `created_at` | `project_members` |
|---------------|--------|------------|--------------|-------------------|
| `prj_H5mQ2rT8vX` | Research quality | `U_alice` | `2026-11-16T09:00:00+00:00` | `(U_alice, owner)` |
| `prj_K9pL3wN6zB` | Release notes | `U_dana` | `2026-11-16T09:05:00+00:00` | `(U_dana, owner)` |

The `integrations` table contains no row for either project unless a scenario's `Given` says so.

**Integration kinds and non-secret configuration.** `kind` is one of `jira`, `github` and
`ai_model`.

- `jira`: `config` contains `site_url` (an `https` URL with a non-empty host) and exactly one of
  `project_key` or `template_project` (non-empty string after trimming). Both, neither or a missing
  field is HTTP 422 `{"error":"invalid_jira_config"}`; a non-`https` `site_url` is HTTP 422
  `{"error":"invalid_site_url"}`.
- `github`: `config` contains `repository` matching `^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$` and
  `base_branch` (non-empty string after trimming). A malformed repository is HTTP 422
  `{"error":"invalid_repository"}`; a whitespace-only base branch is HTTP 422
  `{"error":"invalid_base_branch"}`.
- `ai_model`: `config` contains `vendor` (non-empty string after trimming), `base_url` (an `https`
  URL with a non-empty host) and `tier_models` (an object with exactly the keys `fast`, `standard`
  and `deep`, each a non-empty string matching `^[A-Za-z0-9._-]+$`). A missing or empty vendor is
  HTTP 422 `{"error":"invalid_vendor"}`; a non-`https` base URL is HTTP 422
  `{"error":"invalid_base_url"}`; an empty or malformed `tier_models` object is HTTP 422
  `{"error":"invalid_tier_mapping"}`; a required tier absent from the object is HTTP 422
  `{"error":"tier_model_missing","tier":"deep"}` where the `tier` value is the missing key.

The three tier labels `fast`, `standard` and `deep` are this epic's fixture vocabulary: SK-001 §4
cites platform ADR-013 §1 for the tier-to-model mapping, and that ADR is not present in this
repository. The behaviour under test is the exact mapping storage and the rejection of an
incomplete mapping; a different platform vocabulary changes the fixture labels, not the story.

**Secret store contract.** Credential values live in the external secret store (AWS Secrets
Manager; fixture endpoint `http://secrets.test:4566`) under the secret id
`skill-builder/{project_id}/{kind}`. The `integrations.secret_ref` column equals that secret id
exactly; no other column or JSON field holds the value. Writing a credential calls
`PutSecretValue` with `SecretString` equal to the submitted value. Verification and run preparation
read the current value through `secret_ref` with `GetSecretValue` at the time of use, so a value
rotated in the secret store is picked up without a builder write. Administering the secret store is
an external prerequisite, not a deliverable.

**Integration write contract (BSB-44 extension).**
`PUT /api/projects/{project_id}/integrations/{kind}` takes `Content-Type: application/json` with
body `{"config": {...}, "credential": "...", "mcp": {...}}`; `credential` and `mcp` are optional.
The caller must be the project owner (FA-4 guard) and the project must exist (HTTP 404
`{"error":"project_not_found"}`). On success the builder responds with HTTP 200 and a JSON body with
`integration_id` (`^int_[A-Za-z0-9]{10}$`), `project_id`, `kind`, `config` (equal to the submitted
object), `secret_ref` (the secret id or `null`), `credential_set` (`true` exactly when `secret_ref`
is not `null`), `mcp` (the stored object or `null`), `verified_at` (`null` or an ISO-8601 UTC
timestamp), `platform_overlap`, `platform_overlap_projects` (array) and `test_purpose` (boolean or
`null`). The response never contains a credential value and never has a field named `credential`,
`token`, `api_key` or `secret_value`. A second PUT for the same `(project_id, kind)` updates the
existing row and keeps its `integration_id`. A validation failure returns HTTP 422 with the error
names above and changes no row and writes no secret. If the secret store is unreachable or refuses
the write, the builder returns HTTP 503 `{"error":"secret_store_unavailable"}` and changes no row
(on an update, the previous row and secret remain).

**MCP definition validation.** `mcp`, when present for kind `jira` or `github`, must be an object
with a non-empty string `server`, an optional string `command` and an optional `args` array of
strings. Any other shape is HTTP 422 `{"error":"invalid_mcp_definition"}`. Any object key matching
`(?i)token|api[_-]?key|secret|password|credential` whose value is a non-empty string, at any depth,
is HTTP 422 `{"error":"mcp_definition_must_not_contain_credentials"}` and is not stored. `mcp` on
kind `ai_model` is HTTP 422 `{"error":"mcp_not_supported","kind":"ai_model"}`.

**Integration read contract (this epic adds).** `GET /api/projects/{project_id}/integrations` and
`GET /api/projects/{project_id}/integrations/{kind}` are available to a project member and return
the same fields as the write response (without a credential) for each row; list entries are ordered
by `kind` ascending (`ai_model`, `github`, `jira`). A non-member gets HTTP 403
`{"error":"project_membership_required"}`; an unknown kind or an absent row gets HTTP 404
`{"error":"integration_not_found"}`. The settings page renders, inside each
`data-testid="integration-section-{kind}"` container, an element
`data-testid="integration-credential-status-{kind}"` whose text is exactly `Configured` or
`Not configured`, an element `data-testid="integration-verified-at-{kind}"` whose text is exactly
`Last verified: {timestamp}` or `Never verified`, and for `jira` and `github` an element
`data-testid="integration-mcp-{kind}"` whose text is exactly `MCP: {server}` or
`MCP: not configured`. The settings HTML contains no credential value.

**Credential verification contract.** `POST /api/projects/{project_id}/integrations/{kind}/verify`
takes no body and is owner-only. Each probe has a 10-second timeout:

- `jira`: `GET {site_url}/rest/api/3/myself` with header `Authorization: Bearer {credential}`; a 2xx
  response is verified.
- `github`: `GET https://api.github.test/user` with header `Authorization: token {credential}`; a
  2xx response is verified.
- `ai_model`: `GET {base_url}/v1/models` with header `x-api-key: {credential}`; a 2xx response is
  verified.

Success is HTTP 200 with `{"kind": "...", "verified": true, "verified_at": "..."}` and sets
`integrations.verified_at` to that timestamp. A non-2xx response, a refused connection or an
unreadable response is HTTP 422
`{"error":"verification_failed","kind":"...","detail":"..."}` where `detail` is
`jira_authentication_failed` for a 401 or 403 and `endpoint_unreachable` for a refused connection;
`verified_at` is unchanged. No response within 10 seconds is HTTP 504
`{"error":"verification_timeout","kind":"..."}`; `verified_at` is unchanged. A `null` `secret_ref`
is HTTP 422 `{"error":"credential_missing","kind":"..."}` and makes no external call. A non-owner is
HTTP 403 `{"error":"owner_required"}` and makes no external call. An absent integration row is HTTP
404 `{"error":"integration_not_found"}`.

**Repository-overlap and test-purpose contract.** For kind `github` only, the builder reads the
platform repository inventory (an external prerequisite; fixture endpoint
`GET https://platform-inventory.test/repositories` returning
`{"repositories":[{"full_name":"owner/repo","platform_projects":["PRJ-1"]}]}`) on every write and
read, with a 5-second timeout.

- Repository present in the inventory: `platform_overlap` is `"warning"`,
  `platform_overlap_projects` is that entry's `platform_projects` array, and `test_purpose` is
  `false`.
- Inventory read succeeded and the repository is absent: `platform_overlap` is `"none"`,
  `platform_overlap_projects` is `[]`, and `test_purpose` is `true`.
- Inventory unreachable or timed out: `platform_overlap` is `"unknown"`,
  `platform_overlap_projects` is `[]`, and `test_purpose` is `null`.

For kinds `jira` and `ai_model`, `platform_overlap` is `null`, `platform_overlap_projects` is `[]`
and `test_purpose` is `null`. A warning or an unknown inventory never blocks a save or a read. The
settings page shows, only when `platform_overlap` is `"warning"`, an element
`data-testid="integration-overlap-warning-github"` whose text is exactly
`This repository is also used by a platform project: PRJ-1. Runs in this project use non-test state.`
with the platform project keys comma-separated; when the result is `"unknown"` the same element's
text is exactly `Platform repository inventory unavailable - overlap unknown.`; when the result is
`"none"` the element is absent. It also shows an element
`data-testid="integration-test-purpose-github"` whose text is exactly `Test credentials`,
`Not test credentials` or `Test purpose unknown` for `true`, `false` and `null`.

**Redaction contract.** The builder writes one JSON object per line to `stderr` for each request.
Every log record, HTTP error body and stored run artifact passes through a redaction layer that
replaces each credential value known to the project (the current values read through the project's
`secret_ref`s) with the literal `[REDACTED]` before the record is written. Run artifacts are stored
under `s3://builder-test/runs/{run_id}/` (`agent.log`, `progress.json`, `bb_step_result.json` and
the transcript); the redaction layer runs before the object is written. The same rule applies to the
JSONB values recorded in `runs.context` and `runs.verification`. The redaction layer never rewrites
the secret store value.

**Durable systems of record.** Integration state lives in the builder database's `integrations`
table — `id`, `project_id`, `kind`, `config` JSONB, `secret_ref`, `mcp` JSONB, `verified_at`
(SK-001 §9). Credential values live only in the external secret store. The acceptance criteria
assert the `integrations` row, the secret store value at `secret_ref`, and the settings page — not a
mock, cache or in-memory response alone.

**Scope boundary with later epics.** FA-4 (BSB-43) owns the project, owner guard and settings
container. FA-6 (BSB-45) owns run setup and model-profile selection; FA-7 (BSB-48) owns run
execution and writes run outputs through the redaction layer this epic defines; FA-9 (BSB-57) owns
Jira fixture seeding; FA-11/FA-12 (BSB-46/BSB-47) own scans and use the project's model profile;
FA-15 (BSB-54) owns source-control identity for submission. Administering the secret store,
provisioning Jira, GitHub and model endpoints, and supplying the platform repository inventory are
external prerequisites, not deliverables (PRD §8).

## Coverage summary

| Story | Requirements covered |
|-------|----------------------|
| BSB-44-PENDING-1 — Configure a Jira integration with a credential reference | FR-029, FR-032 |
| BSB-44-PENDING-2 — Configure a source-control integration with a sandbox repository | FR-030 |
| BSB-44-PENDING-3 — Configure a model profile with a tier-to-model mapping | FR-031 |
| BSB-44-PENDING-4 — Verify credentials and record when they were last verified | FR-033, FR-034 |
| BSB-44-PENDING-5 — Warn when a repository is also used by a platform project | FR-035, NFR-006 |
| BSB-44-PENDING-6 — Keep credentials out of records, interface, logs and run results | FR-032, FR-036, NFR-004 |
| BSB-44-PENDING-7 — Record MCP server definitions for Jira and source-control | FR-128, FR-129 |

> **Input note.** The run's placeholder work item `SkillBuilder-2` could not be retrieved: the
> configured Atlassian site returns HTTP 404 ("Issue does not exist or you do not have permission
> to see it") for that key, and the site's project list contains BEEM, BSB, EX, GRAP and LNPRTL
> with no `SkillBuilder` project. The Atlassian MCP server configured in `.mcp.json` was not
> exposed as a tool in this session, so the read-only Jira REST API was used. The epic `BSB-44`
> was fetched successfully (summary "Integrations & credentials", status To Do, labels FA-5 and
> MVP, no issue links and no subtasks) and matches `docs/product/epics.md` and `epic-map.json`.
> The placeholder work item contributes no scope here.

---

## STORY: BSB-44-PENDING-1

**Title:** Configure a Jira integration with a credential reference
**Epic:** BSB-44 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **test-project owner**, I want **to configure my project's Jira integration with a test site and project**, so that **runs in this project can reach the test Jira instance**.

### Acceptance Criteria
Scenario: The owner configures a Jira integration with a project key
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`, the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/jira`, and Alice is signed in with a `builder_session` cookie
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"},"credential":"ATATT-alice-jira-token"}`
Then the builder responds with HTTP 200 and a JSON body whose `integration_id` matches `^int_[A-Za-z0-9]{10}$`, whose `project_id` is `prj_H5mQ2rT8vX`, whose `kind` is `jira`, whose `config` equals `{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"}`, whose `secret_ref` is `skill-builder/prj_H5mQ2rT8vX/jira`, whose `credential_set` is `true`, whose `mcp` is `null`, whose `verified_at` is `null`, whose `platform_overlap` is `null` and whose `test_purpose` is `null`; the `integrations` table contains exactly one row for `prj_H5mQ2rT8vX` and `kind` `jira`, with that `integration_id`, that `config`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira`, `mcp` NULL and `verified_at` NULL; the secret store returns `SecretString` exactly `ATATT-alice-jira-token` for secret id `skill-builder/prj_H5mQ2rT8vX/jira`; and no column of that `integrations` row contains the substring `ATATT-alice-jira-token`

Scenario: The owner configures a Jira integration with a template project
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","template_project":"TP_MOBILE"},"credential":"ATATT-alice-jira-token"}`
Then the builder responds with HTTP 200 and a JSON body whose `kind` is `jira`, whose `config` equals `{"site_url":"https://alice-test.atlassian.net","template_project":"TP_MOBILE"}`, whose `secret_ref` is `skill-builder/prj_H5mQ2rT8vX/jira` and whose `credential_set` is `true`; the `integrations` row for `prj_H5mQ2rT8vX` and `kind` `jira` stores that `config` exactly, has no `project_key` key in its `config`, and its `secret_ref` is `skill-builder/prj_H5mQ2rT8vX/jira`

Scenario: A Jira config with both a project key and a template project is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/jira`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"TEST","template_project":"TP_MOBILE"},"credential":"ATATT-alice-jira-token"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_jira_config"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/jira`

Scenario: A Jira config with neither a project key nor a template project is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net"},"credential":"ATATT-alice-jira-token"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_jira_config"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/jira`

Scenario: A non-HTTPS Jira site URL is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"http://alice-test.atlassian.net","project_key":"TEST"},"credential":"ATATT-alice-jira-token"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_site_url"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/jira`

Scenario: A non-owner cannot configure the Jira integration
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`
When Bob submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://bob-test.atlassian.net","project_key":"BOB"},"credential":"ATATT-bob-jira-token"}`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/jira`

Scenario: An unreachable secret store leaves no partial integration
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the fixture secret store at `http://secrets.test:4566` refuses TCP connections
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"},"credential":"ATATT-alice-jira-token"}`
Then the builder responds with HTTP 503 and body exactly `{"error":"secret_store_unavailable"}` and the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`

### Covered requirements (traceability)
- FR-029
- FR-032

### Out of scope
Verifying the Jira credential and recording `verified_at` (BSB-44-PENDING-4); MCP server definitions (BSB-44-PENDING-7); credential display and log/result redaction beyond the write response (BSB-44-PENDING-6); the source-control and model integrations (BSB-44-PENDING-2 and BSB-44-PENDING-3); provisioning or administering the Jira test site; seeding Jira fixtures (FA-9 / BSB-57).

### Notes / dependencies
Depends on FA-4 (BSB-43) for the project, `projects.owner_id`, the owner-only guard and the settings container, and on BSB-43-PENDING-5 for the `PUT /api/projects/{project_id}/integrations/{kind}` route, its `(project_id, kind)` identity and its `integration_id` contract. The secret store is an external prerequisite (SK-001 §4): the value lives at `skill-builder/{project_id}/{kind}` and the row stores only `secret_ref`. This story establishes the `credential` extension of the write route that BSB-44-PENDING-2, -3, -6 and -7 reuse. `config` is non-secret by contract; the `template_project` value is consumed by FA-9's Jira fixture seeding, and the site URL and project key are consumed by FA-6's run preparation.

---

## STORY: BSB-44-PENDING-2

**Title:** Configure a source-control integration with a sandbox repository
**Epic:** BSB-44 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **test-project owner**, I want **to configure my project's source-control integration with a sandbox repository and base branch**, so that **runs have a test repository and a starting point**.

### Acceptance Criteria
Scenario: The owner configures a source-control integration with a credential
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `github`, the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/github`, and the platform repository inventory at `https://platform-inventory.test/repositories` returns `{"repositories":[{"full_name":"platform-org/shared-repo","platform_projects":["PRJ-1"]}]}`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org/skilltest","base_branch":"main"},"credential":"ghp_aliceSandboxToken0123456789"}`
Then the builder responds with HTTP 200 and a JSON body whose `integration_id` matches `^int_[A-Za-z0-9]{10}$`, whose `project_id` is `prj_H5mQ2rT8vX`, whose `kind` is `github`, whose `config` equals `{"repository":"sandbox-org/skilltest","base_branch":"main"}`, whose `secret_ref` is `skill-builder/prj_H5mQ2rT8vX/github`, whose `credential_set` is `true`, whose `mcp` is `null`, whose `verified_at` is `null`, whose `platform_overlap` is `"none"`, whose `platform_overlap_projects` is `[]` and whose `test_purpose` is `true`; the `integrations` table contains exactly one row for `prj_H5mQ2rT8vX` and `kind` `github`, with that `config`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/github`, `mcp` NULL and `verified_at` NULL; the secret store returns `SecretString` exactly `ghp_aliceSandboxToken0123456789` for secret id `skill-builder/prj_H5mQ2rT8vX/github`; and no column of that `integrations` row contains the substring `ghp_aliceSandboxToken0123456789`

Scenario: A configuration-only save leaves the secret reference unset
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `github`, and the platform repository inventory at `https://platform-inventory.test/repositories` returns `{"repositories":[]}`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org/skilltest","base_branch":"main"}}`
Then the builder responds with HTTP 200 and a JSON body whose `kind` is `github`, whose `secret_ref` is `null`, whose `credential_set` is `false`, whose `mcp` is `null`, whose `platform_overlap` is `"none"` and whose `test_purpose` is `true`; the `integrations` row for `prj_H5mQ2rT8vX` and `kind` `github` has `secret_ref` NULL; and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/github`

Scenario: A malformed repository name is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `github`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org","base_branch":"main"},"credential":"ghp_aliceSandboxToken0123456789"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_repository"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `github`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/github`

Scenario: A whitespace-only base branch is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `github`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org/skilltest","base_branch":"   "},"credential":"ghp_aliceSandboxToken0123456789"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_base_branch"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `github`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/github`

Scenario: A non-owner cannot configure the source-control integration
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `github`
When Bob submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org/bob-test","base_branch":"main"},"credential":"ghp_bobSandboxToken"}`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `github`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/github`

Scenario: Saving source control leaves the Jira integration untouched
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `integration_id` `int_Jira000001`, `config` `{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `verified_at` `2026-11-16T10:00:00+00:00`, the secret store value for that secret id is `ATATT-alice-jira-token`, and the platform repository inventory at `https://platform-inventory.test/repositories` returns `{"repositories":[]}`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org/skilltest","base_branch":"main"},"credential":"ghp_aliceSandboxToken0123456789"}`
Then the builder responds with HTTP 200 for the `github` integration, the `jira` row's `integration_id`, `config`, `secret_ref` and `verified_at` are unchanged, and the secret store value for secret id `skill-builder/prj_H5mQ2rT8vX/jira` is still `ATATT-alice-jira-token`

### Covered requirements (traceability)
- FR-030

### Out of scope
The repository-overlap warning beyond the `platform_overlap`/`test_purpose` values asserted here (BSB-44-PENDING-5 owns the warning surface); MCP server definitions (BSB-44-PENDING-7); verification (BSB-44-PENDING-4); credential display and log/result redaction (BSB-44-PENDING-6); provisioning the sandbox repository; the token's push access to `build/*` branches and pull-request creation (consumed by FA-2 and FA-15); the Jira and model integrations (BSB-44-PENDING-1 and BSB-44-PENDING-3).

### Notes / dependencies
Depends on FA-4 (BSB-43) for the project, owner guard and settings container, and on BSB-44-PENDING-1 for the `credential` extension of the write route and the secret-store contract. The source-control repository and token are external prerequisites (SK-001 §4): the fixture repository is `sandbox-org/skilltest`, the token is stored only at `skill-builder/{project_id}/github`, and the repository's base branch is the run's input branch (FA-6 / BSB-45). The `platform_overlap` values in this story come from the contract BSB-44-PENDING-5 owns; this story asserts them only so a source-control save has a complete response. The token's push and pull-request permissions are consumed by FA-2 (build branches) and FA-15 (catalog submission), not exercised here.

---

## STORY: BSB-44-PENDING-3

**Title:** Configure a model profile with a tier-to-model mapping
**Epic:** BSB-44 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **test-project owner**, I want **to configure my project's AI model profile with a vendor, a base URL and a tier-to-model mapping**, so that **runs use a model endpoint and mapping that I control**.

### Acceptance Criteria
Scenario: The owner configures a model profile
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/ai_model`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/ai_model` with body `{"config":{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}},"credential":"sk-ant-alice-model-key"}`
Then the builder responds with HTTP 200 and a JSON body whose `integration_id` matches `^int_[A-Za-z0-9]{10}$`, whose `project_id` is `prj_H5mQ2rT8vX`, whose `kind` is `ai_model`, whose `config` equals `{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}}`, whose `secret_ref` is `skill-builder/prj_H5mQ2rT8vX/ai_model`, whose `credential_set` is `true`, whose `mcp` is `null`, whose `verified_at` is `null`, whose `platform_overlap` is `null`, whose `platform_overlap_projects` is `[]` and whose `test_purpose` is `null`; the `integrations` table contains exactly one row for `prj_H5mQ2rT8vX` and `kind` `ai_model`, with that `config`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/ai_model`, `mcp` NULL and `verified_at` NULL; the secret store returns `SecretString` exactly `sk-ant-alice-model-key` for secret id `skill-builder/prj_H5mQ2rT8vX/ai_model`; and no column of that `integrations` row contains the substring `sk-ant-alice-model-key`

Scenario: A mapping missing a required tier is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/ai_model` with body `{"config":{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5"}},"credential":"sk-ant-alice-model-key"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"tier_model_missing","tier":"deep"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/ai_model`

Scenario: An empty tier-to-model mapping is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/ai_model` with body `{"config":{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{}},"credential":"sk-ant-alice-model-key"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_tier_mapping"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/ai_model`

Scenario: A non-HTTPS model base URL is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/ai_model` with body `{"config":{"vendor":"anthropic","base_url":"http://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}},"credential":"sk-ant-alice-model-key"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_base_url"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/ai_model`

Scenario: A missing vendor is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/ai_model` with body `{"config":{"base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}},"credential":"sk-ant-alice-model-key"}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_vendor"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/ai_model`

Scenario: A non-owner cannot configure the model profile
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`
When Bob submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/ai_model` with body `{"config":{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}},"credential":"sk-ant-bob-model-key"}`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `ai_model`, and the secret store has no value for secret id `skill-builder/prj_H5mQ2rT8vX/ai_model`

### Covered requirements (traceability)
- FR-031

### Out of scope
Verifying the model credential (BSB-44-PENDING-4); MCP server definitions, which a model profile does not have (BSB-44-PENDING-7); credential display and log/result redaction (BSB-44-PENDING-6); choosing a tier per run and recording the tier on a run (FA-6 / BSB-45 and FA-7 / BSB-48); provisioning or administering model endpoints; the Jira and source-control integrations (BSB-44-PENDING-1 and BSB-44-PENDING-2).

### Notes / dependencies
Depends on FA-4 (BSB-43) for the project, owner guard and settings container, and on BSB-44-PENDING-1 for the `credential` extension of the write route and the secret-store contract. The model endpoint and API key are external prerequisites (SK-001 §4). FA-6 (BSB-45) reads the profile's `tier_models` mapping to build `BB_MODEL` from the run's tier, vendor key and base URL (SK-001 §2a), and FA-12 (BSB-47) uses the project's profile for the LLM security scan. The tier labels `fast`, `standard` and `deep` are this epic's fixture vocabulary because SK-001 §4 defers the vocabulary to platform ADR-013 §1, which is not in this repository; a different platform vocabulary changes the fixture labels, not the validation behaviour or the stored mapping shape.

---

## STORY: BSB-44-PENDING-4

**Title:** Verify credentials and record when they were last verified
**Epic:** BSB-44 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **test-project owner**, I want **to verify an integration's stored credentials and see when they were last verified**, so that **I know a run will not fail on a bad credential**.

### Acceptance Criteria
Scenario: A Jira integration verifies using the current stored credential
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `integration_id` `int_Jira000001`, `config` `{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `verified_at` NULL, and the secret store value at that secret id is `ATATT-alice-jira-token-rotated` (rotated after the row was saved from `ATATT-alice-jira-token`), and the fixture Jira site returns HTTP 200 `{"accountId":"alice"}` for `GET https://alice-test.atlassian.net/rest/api/3/myself` only when the `Authorization` header is exactly `Bearer ATATT-alice-jira-token-rotated`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/integrations/jira/verify`
Then the builder responds with HTTP 200 and a JSON body whose `kind` is `jira`, whose `verified` is `true` and whose `verified_at` is an ISO-8601 UTC timestamp within 5 seconds of the test's start; the `integrations` row's `verified_at` equals that response value; the fixture Jira site recorded exactly one request to `/rest/api/3/myself` with `Authorization` `Bearer ATATT-alice-jira-token-rotated`; and the row's `integration_id`, `config` and `secret_ref` are unchanged

Scenario: A source-control integration verifies with its stored token
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `github`, `config` `{"repository":"sandbox-org/skilltest","base_branch":"main"}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/github` and `verified_at` NULL, the secret store value at that secret id is `ghp_aliceSandboxToken0123456789`, and the fixture GitHub API at `https://api.github.test` returns HTTP 200 `{"login":"alice"}` for `GET /user` only when the `Authorization` header is exactly `token ghp_aliceSandboxToken0123456789`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/integrations/github/verify`
Then the builder responds with HTTP 200 and a JSON body whose `kind` is `github`, whose `verified` is `true` and whose `verified_at` is an ISO-8601 UTC timestamp within 5 seconds of the test's start; the `integrations` row's `verified_at` equals that response value; and the fixture GitHub API recorded exactly one request to `/user` with `Authorization` `token ghp_aliceSandboxToken0123456789`

Scenario: A model profile verifies against its stored API key
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `ai_model`, `config` `{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/ai_model` and `verified_at` NULL, the secret store value at that secret id is `sk-ant-alice-model-key`, and the fixture model endpoint returns HTTP 200 `{"data":[]}` for `GET https://models.example.test/v1/models` only when the `x-api-key` header is exactly `sk-ant-alice-model-key`
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/integrations/ai_model/verify`
Then the builder responds with HTTP 200 and a JSON body whose `kind` is `ai_model`, whose `verified` is `true` and whose `verified_at` is an ISO-8601 UTC timestamp within 5 seconds of the test's start; the `integrations` row's `verified_at` equals that response value; and the fixture model endpoint recorded exactly one request to `/v1/models` with `x-api-key` `sk-ant-alice-model-key`

Scenario: A refused verification keeps the previous verified timestamp
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `verified_at` `2026-11-16T10:00:00+00:00`, the secret store value at that secret id is `ATATT-alice-jira-token`, and the fixture Jira site returns HTTP 401 with body `{"errorMessages":["Unauthorized"]}` for the probe
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/integrations/jira/verify`
Then the builder responds with HTTP 422 and body exactly `{"error":"verification_failed","kind":"jira","detail":"jira_authentication_failed"}` and the `integrations` row's `verified_at` is still `2026-11-16T10:00:00+00:00`

Scenario: A timed-out verification keeps the previous verified timestamp
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `verified_at` `2026-11-16T10:00:00+00:00`, the secret store value at that secret id is `ATATT-alice-jira-token`, and the fixture Jira site accepts the connection and sends no response for 30 seconds
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/integrations/jira/verify`
Then the builder responds within 11 seconds of the request with HTTP 504 and body exactly `{"error":"verification_timeout","kind":"jira"}` and the `integrations` row's `verified_at` is still `2026-11-16T10:00:00+00:00`

Scenario: Verification without a stored credential is refused
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `secret_ref` NULL and `verified_at` NULL, and the fixture Jira site records zero requests
When Alice submits `POST /api/projects/prj_H5mQ2rT8vX/integrations/jira/verify`
Then the builder responds with HTTP 422 and body exactly `{"error":"credential_missing","kind":"jira"}`, the fixture Jira site recorded zero requests, and the `integrations` row's `verified_at` is NULL

Scenario: A non-owner cannot verify an integration
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `verified_at` `2026-11-16T10:00:00+00:00`, and the fixture Jira site records zero requests
When Bob submits `POST /api/projects/prj_H5mQ2rT8vX/integrations/jira/verify`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, the fixture Jira site recorded zero requests, and the `integrations` row's `verified_at` is still `2026-11-16T10:00:00+00:00`

### Covered requirements (traceability)
- FR-033
- FR-034

### Out of scope
Configuring or saving an integration and writing its credential (BSB-44-PENDING-1, -2 and -3); credential display and log/result redaction (BSB-44-PENDING-6); deciding whether a run may start on a failed verification or blocking a run (FA-6 / BSB-45); automatic, scheduled or background verification; provisioning the external Jira, GitHub and model endpoints; administering the secret store.

### Notes / dependencies
Depends on BSB-44-PENDING-1 for the Jira integration, BSB-44-PENDING-2 for the source-control integration, BSB-44-PENDING-3 for the model profile, and FA-4 (BSB-43) for the owner guard. The verification endpoint is owner-only because only the owner changes integrations (FA-4 / FR-028) and the check reads the stored credential. Each probe reads the value through `secret_ref` with `GetSecretValue` at verification time, so a credential rotated in the secret store is used without a builder write (the epic's rotation edge case). `verified_at` is the durable record of the last successful verification (SK-001 §9); a failed, refused or timed-out verification never clears it. The external endpoints and the secret store are supplied outside this product (PRD §8). FA-6 (BSB-45) may surface the timestamp but does not own it.

---

## STORY: BSB-44-PENDING-5

**Title:** Warn when a repository is also used by a platform project
**Epic:** BSB-44 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **test-project owner**, I want **a warning when my source-control integration points at a repository that a platform project also uses**, so that **I do not run tests against non-test state**.

### Acceptance Criteria
Scenario: An overlapping repository produces a warning without blocking the save
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `github`, and the platform repository inventory at `https://platform-inventory.test/repositories` returns `{"repositories":[{"full_name":"platform-org/shared-repo","platform_projects":["PRJ-1"]}]}`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"platform-org/shared-repo","base_branch":"main"},"credential":"ghp_aliceSandboxToken0123456789"}`
Then the builder responds with HTTP 200 and a JSON body whose `platform_overlap` is `"warning"`, whose `platform_overlap_projects` is `["PRJ-1"]` and whose `test_purpose` is `false`; the `integrations` table contains one row for `prj_H5mQ2rT8vX` with `kind` `github` and that `config`; a follow-up `GET /api/projects/prj_H5mQ2rT8vX/integrations/github` by Bob returns HTTP 200 with the same `platform_overlap`, `platform_overlap_projects` and `test_purpose`; and `GET /projects/prj_H5mQ2rT8vX/settings` by Alice contains an element `data-testid="integration-overlap-warning-github"` whose text is exactly `This repository is also used by a platform project: PRJ-1. Runs in this project use non-test state.` and an element `data-testid="integration-test-purpose-github"` whose text is exactly `Not test credentials`

Scenario: A non-overlapping repository produces no warning
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `github`, and the platform repository inventory at `https://platform-inventory.test/repositories` returns `{"repositories":[{"full_name":"platform-org/shared-repo","platform_projects":["PRJ-1"]}]}`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org/skilltest","base_branch":"main"},"credential":"ghp_aliceSandboxToken0123456789"}`
Then the builder responds with HTTP 200 and a JSON body whose `platform_overlap` is `"none"`, whose `platform_overlap_projects` is `[]` and whose `test_purpose` is `true`; the `integrations` table contains one row for `prj_H5mQ2rT8vX` with `kind` `github`; and `GET /projects/prj_H5mQ2rT8vX/settings` by Alice has no element with `data-testid="integration-overlap-warning-github"` and contains an element `data-testid="integration-test-purpose-github"` whose text is exactly `Test credentials`

Scenario: An unavailable inventory degrades to unknown, not none
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `github`, and the platform repository inventory at `https://platform-inventory.test/repositories` refuses TCP connections
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org/skilltest","base_branch":"main"},"credential":"ghp_aliceSandboxToken0123456789"}`
Then the builder responds with HTTP 200 and a JSON body whose `platform_overlap` is `"unknown"`, whose `platform_overlap_projects` is `[]` and whose `test_purpose` is `null`; the `integrations` table contains one row for `prj_H5mQ2rT8vX` with `kind` `github`; and `GET /projects/prj_H5mQ2rT8vX/settings` by Alice contains an element `data-testid="integration-overlap-warning-github"` whose text is exactly `Platform repository inventory unavailable - overlap unknown.` and an element `data-testid="integration-test-purpose-github"` whose text is exactly `Test purpose unknown`

Scenario: Jira and model integrations carry no repository overlap signal
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira` or `kind` `ai_model`, and the platform repository inventory at `https://platform-inventory.test/repositories` returns `{"repositories":[{"full_name":"platform-org/shared-repo","platform_projects":["PRJ-1"]}]}`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"},"credential":"ATATT-alice-jira-token"}` and then submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/ai_model` with body `{"config":{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}},"credential":"sk-ant-alice-model-key"}`
Then each response is HTTP 200 with `platform_overlap` `null`, `platform_overlap_projects` `[]` and `test_purpose` `null`, and `GET /projects/prj_H5mQ2rT8vX/settings` by Alice has no element with `data-testid="integration-overlap-warning-jira"` and no element with `data-testid="integration-overlap-warning-ai_model"`

### Covered requirements (traceability)
- FR-035
- NFR-006

### Out of scope
Refusing, blocking or gating a save or a run on an overlap; cleaning, migrating or deleting the overlapping repository; administering the platform repository inventory; verifying credentials (BSB-44-PENDING-4); assessing the test purpose of Jira or model credentials beyond the `null` read-model value; provisioning the external inventory service.

### Notes / dependencies
Depends on BSB-44-PENDING-2 for the source-control integration, BSB-44-PENDING-1 and BSB-44-PENDING-3 for the Jira and model integrations, and FA-4 (BSB-43) for the owner guard and settings page. The platform repository inventory is an external prerequisite (PRD §8); SK-001 §4 defines the warning, and PRD §8 "Test data" ties NFR-006 to it: the builder cannot inspect whether a Jira or model credential is test-purpose, and the only committed test-purpose signal is the source-control repository overlap. The `test_purpose` read-model field is this epic's representation of that signal: `true` (no overlap), `false` (overlap) or `null` (inventory unknown). A warning never blocks a save; FA-6 (BSB-45) may consume `test_purpose` when preparing a run but does not change this contract.

---

## STORY: BSB-44-PENDING-6

**Title:** Keep credentials out of records, interface, logs and run results
**Epic:** BSB-44 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-5, MVP

### Story
As a **test-project owner**, I want **my integration credentials to stay out of the builder's records, interface, logs and run results**, so that **a teammate or report reader cannot obtain a credential and use my test systems**.

### Acceptance Criteria
Scenario: The integration API and settings page never return a credential value
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, the `integrations` table contains rows for `prj_H5mQ2rT8vX` with kinds `jira`, `github` and `ai_model`, their `secret_ref`s are `skill-builder/prj_H5mQ2rT8vX/jira`, `skill-builder/prj_H5mQ2rT8vX/github` and `skill-builder/prj_H5mQ2rT8vX/ai_model`, and the secret store values at those secret ids are `ATATT-secret-leak-probe`, `ghp_secretLeakProbe` and `sk-ant-secret-leak-probe`
When Alice requests `GET /api/projects/prj_H5mQ2rT8vX/integrations` and each `GET /api/projects/prj_H5mQ2rT8vX/integrations/{kind}`, Bob requests the same, and Alice requests `GET /projects/prj_H5mQ2rT8vX/settings`
Then every request returns HTTP 200; every JSON item has `credential_set` `true` for its kind and contains none of the three values; no JSON object has a key named `credential`, `token`, `api_key` or `secret_value`; the settings HTML contains none of the three values and contains elements `data-testid="integration-credential-status-jira"`, `data-testid="integration-credential-status-github"` and `data-testid="integration-credential-status-ai_model"` each with text exactly `Configured`

Scenario: The builder database never stores a credential value
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the Jira, source-control and model integrations are saved with credentials `ATATT-secret-leak-probe`, `ghp_secretLeakProbe` and `sk-ant-secret-leak-probe` through the integration write route
When every text and JSONB column of every table in the `skillbuilder` database is queried for the three values
Then none of the three values appears; the `integrations` rows have `secret_ref` exactly `skill-builder/prj_H5mQ2rT8vX/jira`, `skill-builder/prj_H5mQ2rT8vX/github` and `skill-builder/prj_H5mQ2rT8vX/ai_model`; and no table has a column named `credential`, `credential_value`, `token`, `api_key` or `secret_value`

Scenario: Builder logs redact the submitted credential value
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the builder's structured logs are the JSON lines it writes to `stderr` during the request
When Alice saves the Jira integration with credential `ATATT-secret-leak-probe` and the request completes
Then every captured `stderr` JSON line for the request contains no substring `ATATT-secret-leak-probe`, and the line whose `event` is `integration_write` has `project_id` `prj_H5mQ2rT8vX`, `kind` `jira`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `credential` `[REDACTED]`

Scenario: An upstream error that echoes the credential is redacted
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table has no row for `prj_H5mQ2rT8vX` with `kind` `jira`, and the fixture secret store returns the error message `AccessDeniedException: value ATATT-secret-leak-probe is not permitted` when the builder writes that value
When Alice saves the Jira integration with credential `ATATT-secret-leak-probe`
Then the builder responds with HTTP 503 and body exactly `{"error":"secret_store_unavailable"}`; every captured `stderr` JSON line for the request contains no substring `ATATT-secret-leak-probe` and contains `[REDACTED]`; and the `integrations` table contains no row for `prj_H5mQ2rT8vX` with `kind` `jira`

Scenario: Stored run artifacts and run JSONB fields are redacted
Given run `run_8Qm3Rt5Vw` belongs to project `prj_H5mQ2rT8vX`, the project's Jira credential value is `ATATT-secret-leak-probe`, and the builder receives the run artifacts `agent.log` and `bb_step_result.json` whose contents each contain `ATATT-secret-leak-probe`, plus a `runs.context` value `{"jira_note":"token ATATT-secret-leak-probe"}` and a `runs.verification` value `{"detail":"used ATATT-secret-leak-probe"}`
When the builder stores those artifacts under `s3://builder-test/runs/run_8Qm3Rt5Vw/` and records the `runs` row
Then each stored object contains `[REDACTED]` and does not contain `ATATT-secret-leak-probe`, and the `runs` row's `context` and `verification` JSONB values contain `[REDACTED]` and do not contain `ATATT-secret-leak-probe`

Scenario: A non-member cannot read integration settings
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Casey (`U_casey`) is a current skill-builder with no `project_members` row for it, and the project's Jira credential value is `ATATT-secret-leak-probe`
When Casey requests `GET /api/projects/prj_H5mQ2rT8vX/integrations` and `GET /projects/prj_H5mQ2rT8vX/settings`
Then the API responds with HTTP 403 and body exactly `{"error":"project_membership_required"}`, the page responds with HTTP 403 with a body containing `You are not a member of this test project`, and neither response contains `ATATT-secret-leak-probe`

### Covered requirements (traceability)
- FR-032
- FR-036
- NFR-004

### Out of scope
Transport security between the builder and the secret store; secret rotation policy and secret-store administration; run execution itself (FA-7 / BSB-48); audit-trail and retention rules for run reports (FA-13 / BSB-52); preventing the external secret store from retaining previous secret versions (service behaviour outside the builder); encryption-at-rest configuration of the builder database.

### Notes / dependencies
Depends on BSB-44-PENDING-1, BSB-44-PENDING-2 and BSB-44-PENDING-3 for the saved integrations and their `secret_ref` values, BSB-44-PENDING-4 for the verification path whose errors are redacted, and FA-4 (BSB-43) for the project-membership read rule. The redaction contract is the durable privacy guarantee for FR-032, FR-036 and NFR-004 (SK-001 §4 and §6): the builder's own records, interface, `stderr` JSON logs, error bodies and run artifacts never carry a credential value. The `runs` row and the artifact paths `s3://builder-test/runs/{run_id}/` are FA-7 (BSB-48) fixtures supplied to this story; FA-7 writes run outputs through the redaction layer this epic defines, and this story does not create or execute a run. The secret store value itself is never rewritten by the redaction layer.

---

## STORY: BSB-44-PENDING-7

**Title:** Record MCP server definitions for Jira and source-control
**Epic:** BSB-44 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **test-project owner**, I want **to record the MCP server definition that my Jira and source-control integrations expose to runs**, so that **runs can use the same MCP servers the platform uses without putting a secret in the definition**.

### Acceptance Criteria
Scenario: The owner records the Jira integration's MCP server definition
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `integration_id` `int_Jira000001`, `config` `{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira`, `mcp` NULL and `verified_at` NULL
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"},"credential":"ATATT-alice-jira-token","mcp":{"server":"atlassian","command":"npx","args":["-y","mcp-atlassian"]}}`
Then the builder responds with HTTP 200 and a JSON body whose `kind` is `jira`, whose `integration_id` is `int_Jira000001` and whose `mcp` equals `{"server":"atlassian","command":"npx","args":["-y","mcp-atlassian"]}`; the `integrations` row's `mcp` JSONB equals that object; a follow-up `GET /api/projects/prj_H5mQ2rT8vX/integrations/jira` returns HTTP 200 with that `mcp` object; and `GET /projects/prj_H5mQ2rT8vX/settings` by Alice contains an element `data-testid="integration-mcp-jira"` whose text is exactly `MCP: atlassian`

Scenario: The owner records the source-control integration's MCP server definition
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `github`, `config` `{"repository":"sandbox-org/skilltest","base_branch":"main"}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/github` and `mcp` NULL, and the platform repository inventory at `https://platform-inventory.test/repositories` returns `{"repositories":[]}`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/github` with body `{"config":{"repository":"sandbox-org/skilltest","base_branch":"main"},"credential":"ghp_aliceSandboxToken0123456789","mcp":{"server":"github","command":"npx","args":["-y","@modelcontextprotocol/server-github"]}}`
Then the builder responds with HTTP 200 and a JSON body whose `kind` is `github` and whose `mcp` equals `{"server":"github","command":"npx","args":["-y","@modelcontextprotocol/server-github"]}`; the `integrations` row's `mcp` JSONB equals that object; and `GET /projects/prj_H5mQ2rT8vX/settings` by Alice contains an element `data-testid="integration-mcp-github"` whose text is exactly `MCP: github`

Scenario: A malformed MCP definition is rejected without changing the stored definition
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `integration_id` `int_Jira000001`, `config` `{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `mcp` `{"server":"atlassian","command":"npx","args":["-y","mcp-atlassian"]}`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"},"credential":"ATATT-alice-jira-token","mcp":{"server":"atlassian","args":"not-an-array"}}`
Then the builder responds with HTTP 422 and body exactly `{"error":"invalid_mcp_definition"}`, the row's `mcp` is still `{"server":"atlassian","command":"npx","args":["-y","mcp-atlassian"]}`, and the row's `config` and `secret_ref` are unchanged

Scenario: An MCP definition that contains a credential is rejected
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `integration_id` `int_Jira000001`, `config` `{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `mcp` NULL, and the secret store value at that secret id is `ATATT-alice-jira-token`
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"},"credential":"ATATT-alice-jira-token","mcp":{"server":"atlassian","env":{"JIRA_TOKEN":"ATATT-mcp-secret"}}}`
Then the builder responds with HTTP 422 and body exactly `{"error":"mcp_definition_must_not_contain_credentials"}`, the row's `mcp` is still NULL, the secret store value at `skill-builder/prj_H5mQ2rT8vX/jira` is still `ATATT-alice-jira-token`, and no column of the row contains the substring `ATATT-mcp-secret`

Scenario: A model profile cannot carry an MCP definition
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`) and the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `ai_model`, `integration_id` `int_Model00001`, `config` `{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/ai_model` and `mcp` NULL
When Alice submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/ai_model` with body `{"config":{"vendor":"anthropic","base_url":"https://models.example.test","tier_models":{"fast":"claude-haiku-5-5","standard":"claude-sonnet-5-5","deep":"claude-opus-5-5"}},"credential":"sk-ant-alice-model-key","mcp":{"server":"atlassian"}}`
Then the builder responds with HTTP 422 and body exactly `{"error":"mcp_not_supported","kind":"ai_model"}`, the row's `mcp` is still NULL, and the row's `config` and `secret_ref` are unchanged

Scenario: A non-owner cannot record an MCP definition
Given project `prj_H5mQ2rT8vX` is owned by Alice (`U_alice`), Bob (`U_bob`) has a `project_members` row for it with `role` `member`, and the `integrations` table contains a row for `prj_H5mQ2rT8vX` with `kind` `jira`, `integration_id` `int_Jira000001`, `config` `{"site_url":"https://alice-test.atlassian.net","project_key":"TEST"}`, `secret_ref` `skill-builder/prj_H5mQ2rT8vX/jira` and `mcp` NULL
When Bob submits `PUT /api/projects/prj_H5mQ2rT8vX/integrations/jira` with body `{"config":{"site_url":"https://bob-test.atlassian.net","project_key":"BOB"},"credential":"ATATT-bob-jira-token","mcp":{"server":"atlassian","command":"npx","args":["-y","mcp-atlassian"]}}`
Then the builder responds with HTTP 403 and body exactly `{"error":"owner_required"}`, the row's `mcp` is still NULL, and the row's `config` and `secret_ref` are unchanged

### Covered requirements (traceability)
- FR-128
- FR-129

### Out of scope
Executing or connecting to an MCP server; passing the definition to a run and rendering `BB_MCP_CONFIG` (FA-6 / BSB-45); the platform's Atlassian and GitHub MCP servers themselves; any credential value inside an MCP definition (forbidden by this story); MCP definitions on a model profile; verifying the credential (BSB-44-PENDING-4).

### Notes / dependencies
Depends on BSB-44-PENDING-1 and BSB-44-PENDING-2 for the Jira and source-control integrations, BSB-44-PENDING-3 for the model profile that must reject `mcp`, and FA-4 (BSB-43) for the owner guard. The MCP server definition is non-secret configuration stored in `integrations.mcp` JSONB (SK-001 §9) and is never a credential (PRD §8 "MCP definitions"). The Jira definition is the Atlassian MCP the platform uses and the source-control definition is the GitHub MCP (SK-001 §4). FA-6 (BSB-45) reads the stored definition to build `BB_MCP_CONFIG` for a run (SK-001 §2a); this story records it and does not execute it.
