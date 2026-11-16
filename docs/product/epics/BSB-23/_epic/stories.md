# Stories — BSB-23 (Integrations, credentials & MCP definitions)

Epic BSB-23 covers FR-029, FR-030, FR-031, FR-032, FR-033, FR-034, FR-035, FR-036, FR-128,
FR-129, NFR-004 and NFR-006. Decomposed into 6 stories below; coverage of all 12 requirements
verified.

The slices are journeys through one project's integration settings: declare each of the three
integrations a run needs (Jira, source control and AI model), verify the credential behind each,
keep the credential value out of every builder surface, and require the credentials to be
test-purpose. Each is a user-visible outcome for a project owner, not a layer of an integration
API. All of them extend the integrations section of the project settings page that
BSB-22-PENDING-4 owns at GET "/projects/7/settings", and every change route calls that story's
owner-only guard.

> New stories use draft keys `BSB-23-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-23, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-23-PENDING-1

**Title:** Configure the project's Jira integration
**Epic:** BSB-23 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **project owner**, I want **to configure the project's Jira site, its target project or template project and its MCP definition**, so that **runs and Jira fixture seeding reach the right test Jira without the project ever holding the API token**.

### Acceptance Criteria

Scenario: The owner saves a Jira integration with a project key
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member"), an empty "integrations" table whose id sequence's next value is 3, a builder clock reading "2026-11-16T10:30:00Z", and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", project key "BSB", API token "jira-test-token-9f2c", the atlassian MCP definition with command "uvx", args ["mcp-atlassian"] and env JIRA_URL "https://saraavrnd.atlassian.net" and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201 and a body containing "Jira integration 3 saved.", exactly one "integrations" row exists with id 3, project_id 7, kind "jira", config containing site_url "https://saraavrnd.atlassian.net", project_key "BSB" and test_only true, secret_ref "skill-builder/7/integration-3", the submitted MCP definition in mcp and verified_at NULL, the secret store holds "jira-test-token-9f2c" at path "skill-builder/7/integration-3", GET "/projects/7/settings" renders "Jira integration 3", "https://saraavrnd.atlassian.net" and "Not verified", and neither the POST response nor the settings page contains "jira-test-token-9f2c"

Scenario: A template project can stand in for a project key
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table whose id sequence's next value is 3, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", template project "BSB", API token "jira-test-token-9f2c", no project key, and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201 and a body containing "Jira integration 3 saved.", the "integrations" row with id 3 has config containing site_url "https://saraavrnd.atlassian.net", template_project "BSB" and test_only true and has no project_key value, secret_ref "skill-builder/7/integration-3" and verified_at NULL, GET "/projects/7/settings" renders "Template project BSB" and "Not verified", and neither response contains "jira-test-token-9f2c"

Scenario: A Jira target with both a project key and a template project is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", project key "BSB", template project "TRAIN", API token "jira-test-token-9f2c" and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "Provide either a project key or a template project, not both.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: A Jira target with neither a project key nor a template project is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", no project key, no template project, API token "jira-test-token-9f2c" and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "A Jira project key or template project is required.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: A non-https site URL is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "http://saraavrnd.atlassian.net", project key "BSB", API token "jira-test-token-9f2c" and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "The Jira site URL must be an https URL.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: A blank API token is rejected on create
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", project key "BSB", an API token of "   " and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "An API token is required.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: An MCP definition containing a credential is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", project key "BSB", API token "jira-test-token-9f2c", the jira MCP definition whose env sets JIRA_API_TOKEN to "jira-test-token-9f2c" and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "MCP definitions must not contain credentials.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

### Covered requirements (traceability)
- FR-029
- FR-128

### Out of scope
The source-control integration (BSB-23-PENDING-2); AI model profiles (BSB-23-PENDING-3);
credential verification and the last-verified time (BSB-23-PENDING-4); the record-wide, log and
run-result redaction guarantee (BSB-23-PENDING-5); the test-purpose enforcement rule
(BSB-23-PENDING-6); Jira fixture seeding and cleanup (BSB-28); secret-store administration and
credential rotation policy; deleting an integration; connecting to Jira during the save (the save
is a configuration write, not a live call).

### Notes / dependencies
Depends on BSB-22-PENDING-4 for the project settings page at GET "/projects/7/settings", the
"Integrations" section, the "Add integration" link to "/projects/7/integrations/new" and the
owner-only integration guard. This story fills that section and owns the Jira create route
POST "/projects/7/integrations"; the guard runs before any field is read, so a non-owner or a
non-member is refused with the messages BSB-22-PENDING-4 defines and no row or secret is written.

The durable system of record is one row in the builder's own "integrations" table from ADR SK-001
section 9: project_id 7, kind "jira", config JSONB, secret_ref, mcp JSONB and verified_at. The
credential value lives only in the external secret store, at path "skill-builder/7/integration-3";
the final path segment is the integrations row id, which stays unique when a project has more than
one integration, and the "integrations.secret_ref" column holds only that path. The MCP definition
is non-secret configuration stored in "integrations.mcp" and is passed to a run as configuration,
never as a credential: any object key at any depth whose lowercased name contains "token",
"password", "secret", "authorization" or "apikey" is treated as a credential and the whole
definition is rejected.

A project has at most one Jira integration and at most one source-control integration; a second
create for the same kind is refused with HTTP 409 and the message "A Jira integration is already
configured for this project.", or the source-control wording that BSB-23-PENDING-2 exercises. AI
model profiles are the exception and may be several per project (BSB-23-PENDING-3). Editing an
existing Jira integration is POST "/projects/7/integrations/3": a blank API token keeps the
stored secret_ref and its secret, and changing the site URL, target or credential clears
verified_at so a stale verification never applies to different settings (BSB-23-PENDING-4 and
BSB-23-PENDING-5 exercise the edit path). A create leaves the integration unverified;
verified_at is NULL until BSB-23-PENDING-4's verification succeeds, and the settings page shows
"Not verified".

---

## STORY: BSB-23-PENDING-2

**Title:** Configure the project's source-control integration and warn on a shared repository
**Epic:** BSB-23 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-5, MVP

### Story
As a **project owner**, I want **to point the project at a sandbox repository and base branch and be warned when that repository is also used by a platform project**, so that **runs work against test data and I see the production-data risk before it is used**.

### Acceptance Criteria

Scenario: The owner saves a source-control integration for a sandbox repository
Given Project Atlas (id 7) with Ada (user 42) as owner and Bob (user 43) as member, an empty "integrations" table whose id sequence's next value is 3, a builder clock reading "2026-11-16T10:40:00Z", a platform repository inventory that lists only "saraavrnd/bheembhai-platform" as used by platform project "beembhai", and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "github", repository "saraavrnd/skill-builder-sandbox", base branch "main", token "ghp-test-token-7a1d", the github MCP definition with command "npx" and args ["-y", "@modelcontextprotocol/server-github"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201 and a body containing "Source-control integration 3 saved.", exactly one "integrations" row exists with id 3, project_id 7, kind "github", config containing repository "saraavrnd/skill-builder-sandbox", base_branch "main" and test_only true, secret_ref "skill-builder/7/integration-3", the submitted MCP definition in mcp and verified_at NULL, the secret store holds "ghp-test-token-7a1d" at path "skill-builder/7/integration-3", GET "/projects/7/settings" renders "Source control integration 3", "saraavrnd/skill-builder-sandbox", "Base branch: main" and "Not verified" and does not render "No integrations configured yet." or "also used by platform project", and neither response contains "ghp-test-token-7a1d"

Scenario: A repository used by a platform project is saved with a warning
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table whose id sequence's next value is 3, a platform repository inventory that lists "saraavrnd/bheembhai-platform" as used by platform project "beembhai", and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "github", repository "saraavrnd/bheembhai-platform", base branch "main", token "ghp-test-token-7a1d", the github MCP definition with command "npx" and args ["-y", "@modelcontextprotocol/server-github"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201, the body contains "Source-control integration 3 saved." and "Warning: saraavrnd/bheembhai-platform is also used by platform project beembhai. Runs may touch production data.", exactly one "integrations" row exists with id 3 and kind "github", and GET "/projects/7/settings" renders the same warning

Scenario: An unavailable platform inventory is reported and does not block the save
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table whose id sequence's next value is 3, a platform repository inventory whose request returns HTTP 503, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "github", repository "saraavrnd/skill-builder-sandbox", base branch "main", token "ghp-test-token-7a1d", the github MCP definition with command "npx" and args ["-y", "@modelcontextprotocol/server-github"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201 and a body containing "Source-control integration 3 saved." and "Platform repository inventory unavailable; the shared-repository check could not be performed.", exactly one "integrations" row exists with id 3 and kind "github", and GET "/projects/7/settings" renders that inventory notice

Scenario: A repository that is not in owner/name form is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "github", repository "skill-builder-sandbox", base branch "main", token "ghp-test-token-7a1d", the github MCP definition with command "npx" and args ["-y", "@modelcontextprotocol/server-github"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "The sandbox repository must be in owner/name form.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: A blank base branch is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "github", repository "saraavrnd/skill-builder-sandbox", a base branch of "   ", token "ghp-test-token-7a1d", the github MCP definition with command "npx" and args ["-y", "@modelcontextprotocol/server-github"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "A base branch is required.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: An MCP definition containing a credential is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "github", repository "saraavrnd/skill-builder-sandbox", base branch "main", token "ghp-test-token-7a1d", the github MCP definition whose env sets GITHUB_TOKEN to "ghp-test-token-7a1d" and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "MCP definitions must not contain credentials.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: A second source-control integration is rejected
Given Project Atlas (id 7) with Ada as owner, an existing "integrations" row with id 3, project_id 7 and kind "github", and a secret store with no secret at path "skill-builder/7/integration-4"
When Ada submits kind "github", repository "saraavrnd/another-sandbox", base branch "main", token "ghp-test-token-8b2e", the github MCP definition with command "npx" and args ["-y", "@modelcontextprotocol/server-github"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 409 and the message "A source-control integration is already configured for this project.", exactly one "integrations" row of kind "github" exists for project 7, and the secret store holds no secret at path "skill-builder/7/integration-4"

### Covered requirements (traceability)
- FR-030
- FR-129
- FR-035

### Out of scope
The Jira integration (BSB-23-PENDING-1); AI model profiles (BSB-23-PENDING-3); credential
verification and the last-verified time (BSB-23-PENDING-4); the record-wide, log and run-result
redaction guarantee (BSB-23-PENDING-5); the test-purpose enforcement rule (BSB-23-PENDING-6);
creating, curating or deleting sandbox branches; configuring the platform repository inventory;
blocking a save because of the overlap warning; secret-store administration and credential
rotation; deleting an integration.

### Notes / dependencies
Depends on BSB-22-PENDING-4 for the settings page and the owner-only integration guard, and on
BSB-23-PENDING-1 for the integration record shape, the secret-store path convention and the
non-secret MCP validation rule. This story owns the source-control create path through
POST "/projects/7/integrations"; the guard runs before any field is read.

The row is one "integrations" record from ADR SK-001 section 9: project_id 7, kind "github",
config JSONB, secret_ref "skill-builder/7/integration-3", mcp JSONB and verified_at NULL. The
config holds the sandbox repository in owner/name form and the base branch; the token lives only
in the external secret store. The ADR calls this kind "github"; the interface labels it "Source
control". One source-control integration exists per project, so a second create is refused with
HTTP 409 and the message "A source-control integration is already configured for this project."
The Jira kind has the same one-per-project rule (BSB-23-PENDING-1).

The overlap warning is a non-blocking check against the platform repository inventory, an external
prerequisite from PRD section 8. The builder reads the inventory on save and again when it renders
the settings page; a repository the inventory reports as used by a platform project is still
stored, and the interface shows "Warning: saraavrnd/bheembhai-platform is also used by platform
project beembhai. Runs may touch production data." with the repository and platform project names
substituted. When the inventory cannot be read, the save still succeeds and the page shows
"Platform repository inventory unavailable; the shared-repository check could not be performed."
so an unavailable check is never mistaken for a clean result. The inventory and its entries are
supplied outside this product; this story does not build or administer the platform inventory.

---

## STORY: BSB-23-PENDING-3

**Title:** Configure an AI model profile with a tier-to-model mapping
**Epic:** BSB-23 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **project owner**, I want **to configure AI model profiles with a vendor, base URL and a complete high, medium and low tier-to-model mapping**, so that **run start and the LLM scan can resolve each model tier to the model I chose**.

### Acceptance Criteria

Scenario: The owner saves an AI model profile
Given Project Atlas (id 7) with Ada (user 42) as owner and Bob (user 43) as member, an empty "integrations" table whose id sequence's next value is 3, a builder clock reading "2026-11-16T10:50:00Z", and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "ai_model", profile name "Default", vendor "anthropic", base URL "https://api.anthropic.com", the tier mapping {"high":"claude-opus-5-5","medium":"claude-sonnet-5-5","low":"claude-haiku-5-5"} and API key "sk-ant-test-3c9e" with the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201 and a body containing "Model profile 3 saved.", exactly one "integrations" row exists with id 3, project_id 7, kind "ai_model", config containing name "Default", vendor "anthropic", base_url "https://api.anthropic.com", the submitted tier mapping in models and test_only true, secret_ref "skill-builder/7/integration-3" and verified_at NULL, the secret store holds "sk-ant-test-3c9e" at path "skill-builder/7/integration-3", GET "/projects/7/settings" renders "AI model profile Default", "anthropic", "https://api.anthropic.com", "high: claude-opus-5-5", "medium: claude-sonnet-5-5", "low: claude-haiku-5-5" and "Not verified", and neither response contains "sk-ant-test-3c9e"

Scenario: A second profile is added and both are listed
Given Project Atlas (id 7) with Ada as owner, an "integrations" table holding one row with id 3, project_id 7, kind "ai_model" and config name "Default", an id sequence whose next value is 4, and a secret store with no secret at path "skill-builder/7/integration-4"
When Ada submits kind "ai_model", profile name "Cheap smoke runs", vendor "anthropic", base URL "https://api.anthropic.com", the tier mapping {"high":"claude-haiku-5-5","medium":"claude-haiku-5-5","low":"claude-haiku-5-5"} and API key "sk-ant-test-4d0f" with the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201 and a body containing "Model profile 4 saved.", exactly two "integrations" rows of kind "ai_model" exist for project 7 with names "Default" and "Cheap smoke runs", the second row has secret_ref "skill-builder/7/integration-4", and GET "/projects/7/settings" renders both "Default" and "Cheap smoke runs"

Scenario: A tier mapping missing a tier is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "ai_model", profile name "Default", vendor "anthropic", base URL "https://api.anthropic.com", the tier mapping {"high":"claude-opus-5-5","low":"claude-haiku-5-5"} and API key "sk-ant-test-3c9e" with the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "The tier mapping must include high, medium and low.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: An unknown tier is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "ai_model", profile name "Default", vendor "anthropic", base URL "https://api.anthropic.com", the tier mapping {"high":"claude-opus-5-5","medium":"claude-sonnet-5-5","low":"claude-haiku-5-5","ultra":"claude-opus-5-5"} and API key "sk-ant-test-3c9e" with the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "Unknown model tier 'ultra'; expected high, medium or low.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: A non-https base URL is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "ai_model", profile name "Default", vendor "anthropic", base URL "http://api.anthropic.com", the tier mapping {"high":"claude-opus-5-5","medium":"claude-sonnet-5-5","low":"claude-haiku-5-5"} and API key "sk-ant-test-3c9e" with the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "The base URL must be an https URL.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: A duplicate profile name is rejected
Given Project Atlas (id 7) with Ada as owner, an "integrations" table holding one row with id 3, project_id 7, kind "ai_model" and config name "Default", and a secret store with no secret at path "skill-builder/7/integration-4"
When Ada submits kind "ai_model", profile name "Default", vendor "anthropic", base URL "https://api.anthropic.com", the tier mapping {"high":"claude-opus-5-5","medium":"claude-sonnet-5-5","low":"claude-haiku-5-5"} and API key "sk-ant-test-4d0f" with the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 409 and the message "A model profile named Default already exists in this project.", exactly one "integrations" row of kind "ai_model" exists for project 7, and the secret store holds no secret at path "skill-builder/7/integration-4"

### Covered requirements (traceability)
- FR-031

### Out of scope
The Jira and source-control integrations (BSB-23-PENDING-1 and BSB-23-PENDING-2); credential
verification and the last-verified time (BSB-23-PENDING-4); the record-wide, log and run-result
redaction guarantee (BSB-23-PENDING-5); the test-purpose enforcement rule (BSB-23-PENDING-6);
starting a run or choosing a profile or tier at run start (BSB-24); the LLM security scan and its
project-level default model (BSB-32); editing or deleting a profile; pricing or vendor
administration.

### Notes / dependencies
Depends on BSB-22-PENDING-4 for the settings page and the owner-only integration guard, and on
BSB-23-PENDING-1 for the integration record shape and the secret-store path convention. This story
owns the AI model create path through POST "/projects/7/integrations"; the guard runs before any
field is read.

Each profile is one "integrations" row from ADR SK-001 section 9 with kind "ai_model": id 3,
project_id 7, config JSONB, secret_ref "skill-builder/7/integration-3", mcp NULL (a model profile
carries no MCP definition) and verified_at NULL. The config holds the author-facing name, the
vendor, the base URL and the models object whose keys are exactly "high", "medium" and "low" and
whose values are model identifiers. Those tier keys are the tiers the workflow configuration and
the agent image resolve through BB_MODEL, so a run can pick a model tier without a code change.
A project may have several model profiles, unlike the single Jira and source-control
integrations; the profile name must be unique within the project. The row id is the
model_profile_id that a later run records (BSB-24). The API key lives only in the external secret
store and is never stored in the row.

The base URL must be https, is stored without a trailing slash and carries no API-version suffix,
so verification and the agent image append their own "/v1" path. The vendor is a non-empty
free-form identifier. A create leaves the profile unverified; verified_at is NULL until
BSB-23-PENDING-4's verification succeeds. Editing or deleting a profile is not part of this story,
and a profile is not offered at run start until BSB-24 reads it.

---

## STORY: BSB-23-PENDING-4

**Title:** Verify an integration's credentials and record the last verification time
**Epic:** BSB-23 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **project owner**, I want **to verify each integration's credentials and see when each was last verified**, so that **I know a run can reach its Jira, sandbox repository or model before I start it, and a stale check is never mistaken for a current one**.

### Acceptance Criteria

Scenario: A Jira integration verifies successfully and records the time
Given Project Atlas (id 7) with Ada (user 42) as owner, an "integrations" row with id 3, project_id 7, kind "jira", config site_url "https://saraavrnd.atlassian.net", secret_ref "skill-builder/7/integration-3" and verified_at NULL, a secret store holding "jira-test-token-9f2c" at path "skill-builder/7/integration-3", a Jira stub that returns HTTP 200 with body {"accountId":"ada"} only for GET "https://saraavrnd.atlassian.net/rest/api/3/myself" carrying the header "Authorization: Bearer jira-test-token-9f2c", and the builder clock reading "2026-11-16T11:00:00Z"
When Ada submits POST "/projects/7/integrations/3/verify"
Then the Jira stub receives exactly one such request, the builder responds with HTTP 200 and a body containing "Jira integration 3 verified at 2026-11-16T11:00:00Z.", the row's verified_at is "2026-11-16T11:00:00Z", GET "/projects/7/settings" renders "Last verified: 2026-11-16T11:00:00Z", and neither response contains "jira-test-token-9f2c"

Scenario: A source-control integration verifies successfully
Given Project Atlas (id 7) with Ada as owner, an "integrations" row with id 3, project_id 7, kind "github", config repository "saraavrnd/skill-builder-sandbox" and base_branch "main", secret_ref "skill-builder/7/integration-3" and verified_at NULL, a secret store holding "ghp-test-token-7a1d" at path "skill-builder/7/integration-3", a source-control stub that returns HTTP 200 with body {"login":"ada"} only for GET "https://api.github.com/user" carrying the header "Authorization: Bearer ghp-test-token-7a1d", and the builder clock reading "2026-11-16T11:05:00Z"
When Ada submits POST "/projects/7/integrations/3/verify"
Then the source-control stub receives exactly one such request, the builder responds with HTTP 200 and a body containing "Source-control integration 3 verified at 2026-11-16T11:05:00Z.", the row's verified_at is "2026-11-16T11:05:00Z", GET "/projects/7/settings" renders "Last verified: 2026-11-16T11:05:00Z", and neither response contains "ghp-test-token-7a1d"

Scenario: An AI model profile verifies successfully
Given Project Atlas (id 7) with Ada as owner, an "integrations" row with id 3, project_id 7, kind "ai_model", config name "Default", vendor "anthropic" and base_url "https://api.anthropic.com", secret_ref "skill-builder/7/integration-3" and verified_at NULL, a secret store holding "sk-ant-test-3c9e" at path "skill-builder/7/integration-3", a model stub that returns HTTP 200 with body {"data":[]} only for GET "https://api.anthropic.com/v1/models" carrying the header "Authorization: Bearer sk-ant-test-3c9e", and the builder clock reading "2026-11-16T11:10:00Z"
When Ada submits POST "/projects/7/integrations/3/verify"
Then the model stub receives exactly one such request, the builder responds with HTTP 200 and a body containing "Model profile 3 verified at 2026-11-16T11:10:00Z.", the row's verified_at is "2026-11-16T11:10:00Z", GET "/projects/7/settings" renders "Last verified: 2026-11-16T11:10:00Z", and neither response contains "sk-ant-test-3c9e"

Scenario: A rejected credential is reported and the previous verification time is kept
Given Project Atlas (id 7) with Ada as owner, an "integrations" row with id 3, project_id 7, kind "jira", config site_url "https://saraavrnd.atlassian.net", secret_ref "skill-builder/7/integration-3" and verified_at "2026-11-10T09:00:00Z", a secret store holding "jira-test-token-9f2c" at path "skill-builder/7/integration-3", and a Jira stub that returns HTTP 401 with body {"errorMessages":["Unauthorized"]} for GET "https://saraavrnd.atlassian.net/rest/api/3/myself" carrying the header "Authorization: Bearer jira-test-token-9f2c"
When Ada submits POST "/projects/7/integrations/3/verify"
Then the builder responds with HTTP 422 and the message "Jira verification failed: the API token was rejected (HTTP 401).", the row's verified_at remains "2026-11-10T09:00:00Z", GET "/projects/7/settings" still renders "Last verified: 2026-11-10T09:00:00Z", and neither response contains "jira-test-token-9f2c"

Scenario: A missing secret is reported without calling the provider
Given Project Atlas (id 7) with Ada as owner, an "integrations" row with id 3, project_id 7, kind "jira", config site_url "https://saraavrnd.atlassian.net", secret_ref "skill-builder/7/integration-3" and verified_at NULL, a secret store with no secret at path "skill-builder/7/integration-3", and a Jira stub that records every request it receives
When Ada submits POST "/projects/7/integrations/3/verify"
Then the builder responds with HTTP 422 and the message "The integration has no credential to verify.", the Jira stub receives zero requests, the row's verified_at remains NULL, and GET "/projects/7/settings" renders "Not verified"

Scenario: A non-owner member cannot verify an integration
Given Project Atlas (id 7) with Ada (user 42) as owner and Bob (user 43) as member, an "integrations" row with id 3, project_id 7, kind "jira", config site_url "https://saraavrnd.atlassian.net", secret_ref "skill-builder/7/integration-3" and verified_at NULL, a secret store holding "jira-test-token-9f2c" at path "skill-builder/7/integration-3", and a Jira stub that records every request it receives
When Bob submits POST "/projects/7/integrations/3/verify"
Then the builder responds with HTTP 403 and the message "Only the project owner can change integrations.", the Jira stub receives zero requests, the row's verified_at remains NULL, and GET "/projects/7/settings" renders "Not verified"

Scenario: Changing the verification target clears the last verification time
Given Project Atlas (id 7) with Ada as owner, an "integrations" row with id 3, project_id 7, kind "jira", config site_url "https://saraavrnd.atlassian.net", project_key "BSB", secret_ref "skill-builder/7/integration-3" and verified_at "2026-11-10T09:00:00Z", and a secret store holding "jira-test-token-9f2c" at path "skill-builder/7/integration-3"
When Ada submits site URL "https://other.atlassian.net" and project key "BSB" with a blank API token on POST "/projects/7/integrations/3"
Then the builder responds with HTTP 200 and a body containing "Jira integration 3 updated.", the row's config site_url is "https://other.atlassian.net", the row's verified_at is NULL, GET "/projects/7/settings" renders "Not verified", the row's secret_ref is still "skill-builder/7/integration-3", the secret store still holds "jira-test-token-9f2c" at that path, and neither response contains "jira-test-token-9f2c"

### Covered requirements (traceability)
- FR-033
- FR-034

### Out of scope
Creating the Jira, source-control or model integrations (BSB-23-PENDING-1 to BSB-23-PENDING-3);
the record-wide, log and run-result redaction guarantee (BSB-23-PENDING-5); the test-purpose
enforcement rule (BSB-23-PENDING-6); secret-store administration and credential rotation policy;
automatic re-verification or scheduling; changing a credential's value in the secret store;
starting a run.

### Notes / dependencies
Depends on BSB-23-PENDING-1, BSB-23-PENDING-2 and BSB-23-PENDING-3 for the integration records and
their secret references, and on BSB-22-PENDING-4 for the owner-only integration guard. This story
owns POST "/projects/7/integrations/3/verify" and the "Verify" control in the integrations section
of GET "/projects/7/settings".

Verification resolves the secret from the external secret store at the integration's secret_ref at
call time and never reads a credential from the request or the database. There is one provider
path per kind: for "jira", GET the configured site URL plus "/rest/api/3/myself"; for "github",
GET "https://api.github.com/user"; for "ai_model", GET the configured base URL plus "/v1/models".
Each call carries the resolved credential as "Authorization: Bearer" with the value; a 2xx
response is a pass and any other response is a fail. The result message names the provider and the
HTTP status on failure, as in "Jira verification failed: the API token was rejected (HTTP 401)."
and "Source-control verification failed: the token was rejected (HTTP 401)." and "Model
verification failed: the API key was rejected (HTTP 401)."; a provider that does not answer within
10 seconds is a fail with the same wording and "the provider did not respond within 10 seconds"
in place of the status text. No response, page or log echoes the credential value.

The "integrations.verified_at" column from ADR SK-001 section 9 records the last successful
verification: a pass stamps the builder clock, and a fail, a missing secret or a refused request
leaves the previous value untouched, so a stale success is never displayed as current. Editing an
integration through POST "/projects/7/integrations/3" that changes the site URL, target or
credential clears verified_at to NULL; an edit that changes none of them keeps it. The settings page renders
"Last verified:" and the stored timestamp for a verified integration and "Not verified" when
verified_at is NULL. Verification is an owner action, so the guard's message "Only the project
owner can change integrations." applies; a non-owner or non-member is refused before the provider
is called.

---

## STORY: BSB-23-PENDING-5

**Title:** Keep credential values out of builder records, logs, run results and the interface
**Epic:** BSB-23 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-5, MVP

### Story
As a **project owner**, I want **the builder to keep only an opaque secret reference and redact the credential value everywhere**, so that **sharing a project, reading its logs or inspecting a run result never exposes the test credentials**.

### Acceptance Criteria

Scenario: Saving an integration stores only a secret reference
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table whose id sequence's next value is 3, a secret store with no secret at path "skill-builder/7/integration-3", and the builder's own "users", "builds", "projects", "project_members", "integrations", "skill_bundles", "runs", "run_jira" and "suites" tables
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", project key "BSB", API token "jira-test-token-9f2c", the atlassian MCP definition with command "uvx" and args ["mcp-atlassian"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201, the "integrations" row with id 3 has secret_ref "skill-builder/7/integration-3", the secret store holds "jira-test-token-9f2c" at that path, and a search of every text column of every row in those tables finds zero occurrences of "jira-test-token-9f2c"

Scenario: The settings page masks the credential
Given Project Atlas (id 7) with Ada as owner, an "integrations" row with id 3, project_id 7, kind "jira", config site_url "https://saraavrnd.atlassian.net", secret_ref "skill-builder/7/integration-3" and verified_at NULL, and a secret store holding "jira-test-token-9f2c" at path "skill-builder/7/integration-3"
When Ada opens GET "/projects/7/settings"
Then the builder responds with HTTP 200, the page renders "Credential: stored in secret manager" for integration 3, and the response body contains zero occurrences of "jira-test-token-9f2c"

Scenario: A rejected save does not echo the credential
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, a secret store with no secret at path "skill-builder/7/integration-3", and a captured builder application log
When Ada submits kind "jira", site URL "http://saraavrnd.atlassian.net", project key "BSB", API token "jira-test-token-9f2c", the atlassian MCP definition with command "uvx" and args ["mcp-atlassian"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "The Jira site URL must be an https URL.", no "integrations" row is created for project 7, and neither the response body nor the captured log contains "jira-test-token-9f2c"

Scenario: The application log redacts the credential
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table whose id sequence's next value is 3, a secret store with no secret at path "skill-builder/7/integration-3", a Jira stub that returns HTTP 200 for GET "https://saraavrnd.atlassian.net/rest/api/3/myself" carrying the header "Authorization: Bearer jira-test-token-9f2c", and a captured builder application log
When Ada saves a Jira integration with API token "jira-test-token-9f2c" and then verifies it successfully
Then the captured log contains "secret_ref=skill-builder/7/integration-3" and a search of the entire captured log finds zero occurrences of "jira-test-token-9f2c"

Scenario: A run result redacts the credential
Given Project Atlas (id 7) and a run result document for run 11 in project 7 whose command environment records the variable JIRA_API_TOKEN with the value "jira-test-token-9f2c"
When the builder's result writer writes the document to prefix "runs/11/" in the builder's run bucket and the run report renders it
Then the stored document contains "[REDACTED]" in place of the value, the rendered run report contains "[REDACTED]" in place of the value, and neither contains "jira-test-token-9f2c"

Scenario: Editing an integration preserves the stored secret
Given Project Atlas (id 7) with Ada as owner, an "integrations" row with id 3, project_id 7, kind "jira", config site_url "https://saraavrnd.atlassian.net" and project_key "BSB", secret_ref "skill-builder/7/integration-3" and verified_at "2026-11-16T11:00:00Z", and a secret store holding "jira-test-token-9f2c" at path "skill-builder/7/integration-3"
When Ada submits the unchanged site URL "https://saraavrnd.atlassian.net" and project key "BSB" with a blank API token on POST "/projects/7/integrations/3"
Then the builder responds with HTTP 200 and a body containing "Jira integration 3 updated.", the row's secret_ref is still "skill-builder/7/integration-3", the secret store still holds "jira-test-token-9f2c" at that path, the row's verified_at is still "2026-11-16T11:00:00Z", and the response body contains zero occurrences of "jira-test-token-9f2c"

### Covered requirements (traceability)
- FR-032
- FR-036
- NFR-004

### Out of scope
Creating the Jira, source-control or model integrations (BSB-23-PENDING-1 to BSB-23-PENDING-3);
verification paths and last-verified rules (BSB-23-PENDING-4); the test-purpose enforcement rule
(BSB-23-PENDING-6); secret-store administration; credential rotation policy; the run's own
command, transcript and object-storage layout (BSB-26); the run report's content (BSB-33);
encryption at rest; access control to the secret store.

### Notes / dependencies
Depends on BSB-23-PENDING-1 for the integration record and its create path, on BSB-23-PENDING-4
for the verification path that resolves the secret, and on BSB-22-PENDING-4 for the settings page
and the owner guard. This story owns the single redaction rule every builder surface applies:
the credential value is written only to the external secret store, and the builder stores, logs,
renders and reports the secret_ref instead of the value.

The "integrations" row from ADR SK-001 section 9 keeps secret_ref "skill-builder/7/integration-3"
and never the value; the redaction covers the database, the application log, the run result
document and the interface. The run result writer and the run report are built by BSB-26 and
BSB-33; this story owns the shared redaction they call, and its run-result scenario exercises that
writer against a persisted result fixture. Redaction replaces any occurrence of the resolved
credential value with the literal text "[REDACTED]"; it applies to the value, not to the
secret_ref, so an operator can still find the secret by path. The settings page shows
"Credential: stored in secret manager" for every integration and never an input or text node
holding the value. A blank token on edit leaves the stored secret, secret_ref and verified_at
unchanged; a non-blank token replaces the secret-store value at the same path and clears
verified_at so a check made with the old credential is not shown as current.

Secret-store administration, credential rotation and access control to the store are outside this
product, as PRD section 8 states. No credential value is written to an S3 object, a log line, a
database column or an HTML response by any path in this story.

---

## STORY: BSB-23-PENDING-6

**Title:** Require test-purpose credentials on every integration
**Epic:** BSB-23 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-5, MVP

### Story
As a **project owner**, I want **the builder to require a test-purpose confirmation for every integration create and exclude unconfirmed integrations from run selection**, so that **a run cannot be configured with production credentials**.

### Acceptance Criteria

Scenario: A create without the test-purpose confirmation is rejected
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", project key "BSB", API token "jira-test-token-9f2c" and the atlassian MCP definition with command "uvx" and args ["mcp-atlassian"] with no test-purpose confirmation on POST "/projects/7/integrations"
Then the builder responds with HTTP 422 and the message "Runs require test-purpose credentials.", no "integrations" row is created for project 7, and the secret store holds no secret at path "skill-builder/7/integration-3"

Scenario: A confirmed create records the test-purpose attestation
Given Project Atlas (id 7) with Ada as owner, an empty "integrations" table whose id sequence's next value is 3, and a secret store with no secret at path "skill-builder/7/integration-3"
When Ada submits kind "jira", site URL "https://saraavrnd.atlassian.net", project key "BSB", API token "jira-test-token-9f2c", the atlassian MCP definition with command "uvx" and args ["mcp-atlassian"] and the test-purpose confirmation checked on POST "/projects/7/integrations"
Then the builder responds with HTTP 201, the "integrations" row with id 3 has config test_only true, and GET "/projects/7/settings" renders "Test-purpose credentials: confirmed" for integration 3

Scenario: An unconfirmed integration is excluded from run selection
Given Project Atlas (id 7) with Ada as owner, an "integrations" table holding rows with id 3, project_id 7, kind "ai_model", config containing name "Production profile" and test_only false, and id 4, project_id 7, kind "ai_model", config containing name "Default" and test_only true
When Ada requests GET "/api/projects/7/integrations?purpose=run"
Then the builder responds with HTTP 200 and the JSON body {"integrations":[{"id":4,"kind":"ai_model","name":"Default"}]}

### Covered requirements (traceability)
- NFR-006

### Out of scope
Creating the Jira, source-control or model integrations (BSB-23-PENDING-1 to BSB-23-PENDING-3);
verification paths and last-verified rules (BSB-23-PENDING-4); the redaction guarantee
(BSB-23-PENDING-5); the run-start form, its model profile and tier choices and the run record
(BSB-24); defining what a test-purpose Jira site, sandbox repository or model key is; detecting or
marking a credential as production by inspecting its value; secret-store administration and
credential rotation.

### Notes / dependencies
Depends on BSB-23-PENDING-1, BSB-23-PENDING-2 and BSB-23-PENDING-3 for the three integration kinds,
on BSB-22-PENDING-4 for the settings page and owner guard, and on BSB-24 for the run-start choices
that consume the run-purpose list. This story owns the test-purpose confirmation field on every
integration create and the GET "/api/projects/7/integrations?purpose=run" contract.

Every integration create carries a test-purpose confirmation. A create without it, or with it
unchecked, is refused with HTTP 422 and the message "Runs require test-purpose credentials."
before any row or secret is written. A confirmed create records test_only true inside the row's
config JSONB from ADR SK-001 section 9, and the settings page renders "Test-purpose credentials:
confirmed" for that integration. The builder cannot inspect a credential's value to decide whether
it is test-purpose, so the confirmation is the owner's attestation and the run-purpose list is the
hard filter: GET "/api/projects/7/integrations?purpose=run" returns only integrations whose config
test_only is true, and BSB-24 reads that list when it offers model profiles and validates the
project's integrations. An unconfirmed integration is never offered to a run even if it exists in
the table. This attests purpose and filters selection; it does not replace the source-control
overlap warning (BSB-23-PENDING-2), which still appears for a confirmed integration that points at
a repository a platform project also uses.
