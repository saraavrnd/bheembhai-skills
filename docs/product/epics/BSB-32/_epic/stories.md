# Stories — BSB-32 (LLM security scanning)

Epic BSB-32 covers FR-082, FR-083, FR-084, FR-085, FR-086, FR-090, FR-093, FR-139, FR-156 and
FR-163. Decomposed into 7 stories below; coverage of all 10 requirements verified.

The slices follow one model-based security opinion from configuration to evidence: choose the
project's LLM-scan model (PENDING-1), run the scan in a sandbox with only the model key and model
endpoint reachable (PENDING-2), trigger it only after the static scan passes for the same content
(PENDING-3), record a scan that cannot run as unavailable (PENDING-4), show the model and located
findings to the author (PENDING-5), let an author start the full scan from the skill page
(PENDING-6), and prove the advisory result never blocks a run (PENDING-7). Each slice is a
user-visible outcome, not a layer of a scanning service.

> New stories use draft keys `BSB-32-PENDING-N`. `sdlc-tracker-sync` creates each story in Jira,
> parents it to BSB-32, and replaces the draft key with the real key in `story-map.json`.

---

## STORY: BSB-32-PENDING-1

**Title:** Configure the LLM-scan model profile for a test project
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-12, MVP

### Story
As a **project owner**, I want **to choose the AI model profile and tier that the project's LLM security scan uses**, so that **the scan runs with the model I selected and no author can override it per scan**.

### Acceptance Criteria

Scenario: The owner selects the project's LLM-scan model profile
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member"), an "integrations" table holding id 3, project_id 7, kind "ai_model", config {"name": "Default", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-opus-5-5", "medium": "claude-sonnet-5-5", "low": "claude-haiku-5-5"}} and id 4, project_id 7, kind "ai_model", config {"name": "Cheap smoke runs", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-haiku-5-5", "medium": "claude-haiku-5-5", "low": "claude-haiku-5-5"}}, and a "projects" row id 7 with llm_scan_model_profile_id NULL and llm_scan_model_tier NULL
When Ada selects profile "Cheap smoke runs" and tier "low" on the "LLM scan model" control at POST "/projects/7/llm-scan-model" with {"model_profile_id": 4, "tier": "low"}
Then the builder responds with HTTP 200 and a body containing "LLM scan model profile set to Cheap smoke runs (low).", the "projects" row id 7 has llm_scan_model_profile_id 4 and llm_scan_model_tier "low", and GET "/projects/7/settings" renders "LLM scan model: Cheap smoke runs (low)"

Scenario: A non-owner member cannot change the scan model
Given Project Atlas (id 7) whose "project_members" table holds rows for Ada (user 42, role "owner") and Bob (user 43, role "member"), a "projects" row id 7 with llm_scan_model_profile_id 3 and llm_scan_model_tier "medium", and an "integrations" row id 4, project_id 7 and kind "ai_model"
When Bob submits {"model_profile_id": 4, "tier": "low"} on POST "/projects/7/llm-scan-model"
Then the builder responds with HTTP 403 and the message "Only the project owner can change integrations.", and the "projects" row id 7 still has llm_scan_model_profile_id 3 and llm_scan_model_tier "medium"

Scenario: A model profile from another project is refused
Given Project Atlas (id 7) with Ada (user 42) as owner, and an "integrations" row id 9, project_id 8 and kind "ai_model"
When Ada submits {"model_profile_id": 9, "tier": "medium"} on POST "/projects/7/llm-scan-model"
Then the builder responds with HTTP 422 and the message "The selected model profile does not belong to this project.", and the "projects" row id 7 keeps llm_scan_model_profile_id NULL

Scenario: An integration that is not an AI model profile is refused
Given Project Atlas (id 7) with Ada (user 42) as owner, and an "integrations" row id 6, project_id 7 and kind "jira"
When Ada submits {"model_profile_id": 6, "tier": "medium"} on POST "/projects/7/llm-scan-model"
Then the builder responds with HTTP 422 and the message "The selected profile is not an AI model profile.", and the "projects" row id 7 keeps llm_scan_model_profile_id NULL

Scenario: An unknown model tier is refused
Given Project Atlas (id 7) with Ada (user 42) as owner, an "integrations" row id 3, project_id 7 and kind "ai_model", and a "projects" row id 7 with llm_scan_model_profile_id NULL
When Ada submits {"model_profile_id": 3, "tier": "ultra"} on POST "/projects/7/llm-scan-model"
Then the builder responds with HTTP 422 and the message "The LLM scan tier must be high, medium or low.", and the "projects" row id 7 keeps llm_scan_model_profile_id NULL and llm_scan_model_tier NULL

Scenario: The owner clears the scan model
Given Project Atlas (id 7) with Ada (user 42) as owner, and a "projects" row id 7 with llm_scan_model_profile_id 4 and llm_scan_model_tier "low"
When Ada submits {"model_profile_id": null, "tier": null} on POST "/projects/7/llm-scan-model"
Then the builder responds with HTTP 200 and a body containing "LLM scan model profile cleared.", the "projects" row id 7 has llm_scan_model_profile_id NULL and llm_scan_model_tier NULL, and GET "/projects/7/settings" renders "LLM scan model: not configured"

### Covered requirements (traceability)
- FR-163

### Out of scope
Creating, editing or verifying AI model profiles (BSB-23-PENDING-3 and BSB-23-PENDING-4); the
project's run model profile and tier chosen at run start (BSB-24); starting any scan
(BSB-32-PENDING-2 and BSB-32-PENDING-3); installation-level model settings; allowing an author or
a scan request to override the configured scan model; deleting a model profile.

### Notes / dependencies
Depends on BSB-22-PENDING-1 for the "projects" table and BSB-22-PENDING-4 for the project settings
page at GET "/projects/7/settings" and its owner-only guard, and on BSB-23-PENDING-3 for the
`kind "ai_model"` rows and their tier mapping. This story owns the "LLM scan model" control and
the "security scan" section of the settings page, plus one nullable
`projects.llm_scan_model_profile_id` and one nullable `projects.llm_scan_model_tier` column that
the data-model stage must record. Both columns are set together: the profile id must reference a
row in "integrations" with kind "ai_model" and the same project_id, and the tier must be one of
"high", "medium" or "low".

The configured pair is the project's single LLM-scan model. The scan resolves the concrete model
identifier from the selected profile's `models` object at the selected tier (for the example rows,
profile "Default" at "medium" resolves to "claude-sonnet-5-5"). Only the project owner changes the
pair, and the owner guard runs before any field is read, reusing BSB-22-PENDING-4's exact refusal
message. A cleared pair is a valid state: the LLM scan then records the unavailable outcome in
BSB-32-PENDING-4 instead of erroring, and readiness treats that unavailable record as satisfied
(FR-069, BSB-30). No run-start or full-scan request field can override this project setting
(BSB-32-PENDING-6 rejects such a field). FR-163 is satisfied when the full scan resolves this pair;
BSB-32-PENDING-6 exercises that consumption.

---

## STORY: BSB-32-PENDING-2

**Title:** Run the LLM scan with only the model key and model-endpoint access
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 5 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **the LLM scan to run in an isolated container that receives only the model key and can reach only the model endpoint**, so that **a model-based scan of untrusted skill content cannot touch Jira, source control, the builder database or any other network service**.

### Acceptance Criteria

Scenario: The LLM scan completes and records the model that produced it
Given build 7 for skill "bug-fix-resolver" at head SHA "4f2c9a1", a "skill_bundles" row for "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" and s3_key "bundles/4f2c9a1.tar.gz", a completed "scans" row id 11 with stage "static", state "completed", verdict "pass", skills_commit_sha "4f2c9a1", bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", scanner_version "bheembhai-skillscan 0.4.2" and image_digest "sha256:9c1f0a9d8b7e6f5a", a "projects" row id 3 with llm_scan_model_profile_id 8 and llm_scan_model_tier "high", an "integrations" row id 8 with project_id 3, kind "ai_model", config {"name": "Default", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-opus-5-5", "medium": "claude-sonnet-5-5", "low": "claude-haiku-5-5"}} and secret_ref "skill-builder/3/integration-8", a secret store holding "sk-ant-test-3c9e" at path "skill-builder/3/integration-8", and a stub model endpoint at "https://api.anthropic.com/v1/messages" that returns HTTP 200 with body {"model": "claude-opus-5-5", "findings": [{"severity": "HIGH", "rule": "LLM-101", "file": "SKILL.md", "line": 9}]}
When the LLM scan service runs for build 7 at skills_commit_sha "4f2c9a1"
Then exactly one "scans" row id 12 exists with stage "llm", build_id 7, skill "bug-fix-resolver", skills_commit_sha "4f2c9a1", bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", scanner_version "bheembhai-skillscan 0.4.2", image_digest "sha256:9c1f0a9d8b7e6f5a", model "claude-opus-5-5", model_profile_id 8, state "completed", verdict NULL and failure_reason NULL, exactly one "scan_findings" row exists with scan_id 12, severity "HIGH", rule "LLM-101", file "SKILL.md", line 9 and accepted false, and the stub model endpoint received exactly one POST to "/v1/messages" with header "Authorization: Bearer sk-ant-test-3c9e" and a request body naming model "claude-opus-5-5"

Scenario: The scan container receives only the model key and no other credential
Given the same project 3, build 7 and LLM-scan model profile, a secret store holding "sk-ant-test-3c9e" at "skill-builder/3/integration-8", an "integrations" row id 6 with project_id 3, kind "jira", secret_ref "skill-builder/3/integration-6" and secret value "jira-test-token-9f2c", and an "integrations" row id 7 with project_id 3, kind "github", secret_ref "skill-builder/3/integration-7" and secret value "ghp-test-token-7a1d"
When the LLM scan container starts
Then its environment contains the keys "BB_MODEL_API_KEY", "BB_MODEL_BASE_URL" and "BB_MODEL_ID" and no credential key for Jira, source control, the secret store or the builder database, the bundle is mounted read-only at "/skill", and the "scans" row, the "scan_findings" rows and the stored report document contain none of "jira-test-token-9f2c", "ghp-test-token-7a1d" or "sk-ant-test-3c9e"

Scenario: The scan container can reach only the model endpoint
Given profile 8's base URL "https://api.anthropic.com" resolves to the stub model endpoint at "10.0.0.7" on port 443, a dummy HTTP server at "http://10.0.0.5:8080" that records every request it receives, and a public endpoint "https://example.com"
When the LLM scan container starts with an egress allowlist containing only "10.0.0.7" on port 443 and the scanner attempts HTTPS to "https://api.anthropic.com", HTTP to "http://10.0.0.5:8080" and HTTPS to "https://example.com"
Then the request to "https://api.anthropic.com" reaches the stub model endpoint, the requests to "http://10.0.0.5:8080" and "https://example.com" fail before a response is received, the dummy server records 0 requests, and the scan completes with state "completed"

Scenario: The LLM scan reads the exact bundle the static scan passed, not a newer branch head
Given build 7 whose branch has advanced to head SHA "8a7d3e0", a "skill_bundles" row for "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", no "skill_bundles" row for "8a7d3e0", a completed static scan id 11 for skills_commit_sha "4f2c9a1" and bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", and a stub scanner that records the s3_key it was given
When the LLM scan service runs for build 7 at skills_commit_sha "4f2c9a1"
Then the stub scanner records s3_key "bundles/4f2c9a1.tar.gz", the "scans" row id 12 records skills_commit_sha "4f2c9a1" and bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", and the scan does not read or record commit "8a7d3e0"

### Covered requirements (traceability)
- FR-083
- FR-084

### Out of scope
Deciding when the LLM scan is triggered (BSB-32-PENDING-3); recording unavailable, failed or
timed-out outcomes (BSB-32-PENDING-4); rendering the report (BSB-32-PENDING-5); configuring the
project's scan model (BSB-32-PENDING-1); the static scan service, records and verdict
(BSB-31-PENDING-1 to BSB-31-PENDING-3); the LLM scanner's own rule set and prompt policy
(external); model provider administration or key rotation; reusing a prior LLM result.

### Notes / dependencies
Depends on BSB-31-PENDING-1 for the "scans" and "scan_findings" records and the packed bundle at
the requested SHA, and on BSB-32-PENDING-1 for the project's LLM-scan model profile and tier. This
story owns the LLM scan service: it extends "scans" with stage "llm" and the nullable `model` and
`model_profile_id` columns (the data-model stage must record them), runs the pinned scanner image
at the same scanner version and image digest as the static stage, mounts the bundle read-only, and
writes the report to an output mount.

The service resolves the model identifier from the selected profile's `models` object at the
selected tier, fetches the profile's key from the external secret store at container start, and
injects only `BB_MODEL_API_KEY`, `BB_MODEL_BASE_URL` and `BB_MODEL_ID`. It never passes a Jira,
source-control, secret-store or database credential and never writes a credential value to
"scans", "scan_findings", the report document or a log. The LLM stage has network access only to
the resolved model endpoint host and port; every other egress attempt fails. The scanner writes
one report document naming the model it used and the findings; the service records that model on
the "scans" row, never a model the request asked for. A scan has no verdict: `verdict` stays NULL
because the result is advisory, and findings are recorded on "scan_findings" with `accepted`
false (`.skillspector-baseline.yaml` acceptance is static-stage behaviour owned by
BSB-31-PENDING-3). This epic adds no reuse for the LLM stage; each full scan runs it.

---

## STORY: BSB-32-PENDING-3

**Title:** Trigger the LLM scan only after the static scan passes for the same content
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **the LLM scan to start only when the static scan for the exact same content has passed**, so that **model tokens are never spent on content the static gate has already blocked**.

### Acceptance Criteria

Scenario: A passing static scan triggers the LLM scan on the same content
Given build 7 for skill "bug-fix-resolver" at head SHA "4f2c9a1", a "skill_bundles" row for "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" and s3_key "bundles/4f2c9a1.tar.gz", no "scans" row for that bundle, a signed-in project member Ada (user 42) with a "project_members" row for project 3, a stub static scanner that writes the clean report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []}, and a configured LLM-scan model profile whose stub model completes with one finding
When Ada calls POST "/api/builds/7/scans/full" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the static "scans" row id 11 is created with stage "static", state "completed" and verdict "pass", the LLM "scans" row id 12 is created with stage "llm", skills_commit_sha "4f2c9a1" and bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" with started_at not earlier than scan 11's finished_at, the response is HTTP 201 with {"static": {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": false}, "llm": {"scan_id": 12, "state": "completed", "model": "claude-sonnet-5-5", "reused": false}}, and the stub records that the static container started before the LLM container

Scenario: A failing static scan prevents the LLM scan
Given build 7 at head SHA "4f2c9a1" with a packed bundle, a signed-in project member Ada with a "project_members" row for project 3, a stub static scanner that writes the report {"score": 41, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "CRITICAL", "rule": "SS-001", "file": "SKILL.md", "line": 3}]}, a configured LLM-scan model profile, and a stub model endpoint whose request counter is 0
When Ada calls POST "/api/builds/7/scans/full" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the static "scans" row id 11 exists with stage "static", state "completed" and verdict "fail", no "scans" row with stage "llm" exists, the stub model endpoint received 0 requests, and the response is HTTP 200 with {"static": {"scan_id": 11, "state": "completed", "verdict": "fail", "reused": false}, "llm": null, "llm_skipped": "static scan did not pass"}

Scenario: A reused static pass still triggers the LLM scan for that content
Given build 7 at head SHA "4f2c9a1", a completed static "scans" row id 11 for skills_commit_sha "4f2c9a1" and bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" with state "completed" and verdict "pass", a stub static scanner whose container-start counter is 0, and a configured LLM-scan model profile whose stub model completes
When Ada calls POST "/api/builds/7/scans/full" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the static result is {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": true}, the static container-start counter remains 0, a new LLM "scans" row id 12 exists for skills_commit_sha "4f2c9a1" and bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", and the response is HTTP 201 with both result objects

Scenario: A request with no packed bundle runs neither stage
Given build 7 at head SHA "4f2c9a1" with no "skill_bundles" row for "4f2c9a1", a signed-in project member Ada with a "project_members" row for project 3, and a stub model endpoint whose request counter is 0
When Ada calls POST "/api/builds/7/scans/full" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 409 with {"error": "No packed bundle exists for commit 4f2c9a1."}, no "scans" row of either stage is created, and the stub model endpoint received 0 requests

### Covered requirements (traceability)
- FR-082

### Out of scope
Running the LLM container and its isolation (BSB-32-PENDING-2); unavailable and timeout outcomes
(BSB-32-PENDING-4); the skill-page control that calls this route (BSB-32-PENDING-6); the static
route, scan record and verdict (BSB-31-PENDING-1 to BSB-31-PENDING-3); static result reuse
(BSB-31-PENDING-2); starting a run (BSB-24); the command-line full scan (BSB-37); reusing a prior
LLM result; any per-scan model override.

### Notes / dependencies
Depends on BSB-31-PENDING-1 for the static route and the packed bundle, BSB-31-PENDING-2 for
static reuse, BSB-31-PENDING-3 for the static verdict, BSB-22-PENDING-1 for the shared
project-membership check, and BSB-32-PENDING-2 for the LLM scan service. This story owns the full
scan service and its route POST "/api/builds/7/scans/full". The route applies the project
membership check before any bundle lookup, scan or model call; a signed-in user without a
"project_members" row receives HTTP 403 and the message "You are not a member of this project."
and learns nothing about the bundle or a prior scan.

The route runs the static stage first through BSB-31's synchronous route or the same service, and
only a static `verdict` of "pass" for the requested `skills_commit_sha` and its `bundle_sha256`
starts the LLM stage for that same skills commit and bundle. A static verdict of "fail" is a
normal result, not an error: the response reports it and `llm` is null with
`llm_skipped: "static scan did not pass"`, and no model token is spent. The response returns HTTP
201 when a new scan row is created and the body carries the static result object (the same shape
BSB-31-PENDING-1 returns) and the LLM result object `{scan_id, state, model, reused}`. A request
field that tries to choose a model, model profile or tier is rejected by BSB-32-PENDING-6 before
this route runs. The run-start path calls only the static route (BSB-32-PENDING-7); the full scan
is started from the skill page (BSB-32-PENDING-6) or the command line (BSB-37).

---

## STORY: BSB-32-PENDING-4

**Title:** Record an LLM scan that cannot run as unavailable
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **an LLM scan that cannot run to be recorded as unavailable with a reason**, so that **a missing model configuration, a rejected key or a provider failure is visible evidence rather than a silent gap or an error page**.

### Acceptance Criteria

Scenario: No LLM-scan model profile is configured
Given build 7 at head SHA "4f2c9a1" with a packed bundle, a completed static "scans" row id 11 with stage "static", state "completed" and verdict "pass" for bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", a "projects" row id 3 with llm_scan_model_profile_id NULL and llm_scan_model_tier NULL, a signed-in project member, and a stub model endpoint whose request counter is 0
When the full scan runs for skills_commit_sha "4f2c9a1"
Then the LLM "scans" row id 12 exists with stage "llm", skills_commit_sha "4f2c9a1", bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", state "unavailable", model NULL, model_profile_id NULL and failure_reason "No LLM scan model profile is configured for this project.", no "scan_findings" row is written, the stub model endpoint received 0 requests, and the response is HTTP 201 with {"static": {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": false}, "llm": {"scan_id": 12, "state": "unavailable", "model": null, "reused": false}}

Scenario: The configured model profile has no model key
Given build 7 with a static pass, a "projects" row id 3 with llm_scan_model_profile_id 8 and llm_scan_model_tier "high", an "integrations" row id 8 with project_id 3, kind "ai_model" and secret_ref "skill-builder/3/integration-8", a secret store with no secret at path "skill-builder/3/integration-8", and a stub model endpoint whose request counter is 0
When the full scan runs for skills_commit_sha "4f2c9a1"
Then the LLM "scans" row id 12 has state "unavailable", model NULL, model_profile_id 8 and failure_reason "The configured model profile has no model key.", no "scan_findings" row is written, the stub model endpoint received 0 requests, and the full-scan response carries the same static pass and an unavailable LLM result

Scenario: The model provider rejects the configured key
Given build 7 with a static pass, a configured LLM-scan model profile whose secret is "sk-ant-test-invalid", and a stub model endpoint that returns HTTP 401 with body {"error": {"type": "authentication_error"}}
When the full scan runs for skills_commit_sha "4f2c9a1"
Then the LLM "scans" row id 12 has state "unavailable", model NULL and failure_reason "The model provider rejected the configured model key.", no "scan_findings" row is written, and the full-scan response is HTTP 201 with the LLM result state "unavailable" rather than an error page

Scenario: The model provider reports budget exhaustion
Given build 7 with a static pass, a configured LLM-scan model profile, and a stub model endpoint that returns HTTP 402 with body {"error": {"type": "budget_exhausted"}}
When the full scan runs for skills_commit_sha "4f2c9a1"
Then the LLM "scans" row id 12 has state "unavailable", model NULL and failure_reason "The model provider reported that its budget is exhausted.", and no "scan_findings" row is written

Scenario: The LLM scanner exits before writing a report
Given build 7 with a static pass, a configured LLM-scan model profile, and the LLM scanner container exits with code 137 before writing a report
When the full scan runs for skills_commit_sha "4f2c9a1"
Then the LLM "scans" row id 12 has state "unavailable", model NULL and failure_reason "LLM scanner exited with code 137 before writing a report.", and no "scan_findings" row is written

Scenario: The LLM scan exceeds the ten-minute limit
Given build 7 with a static pass, a configured LLM-scan model profile, a stub scanner that starts at "2026-11-16T10:00:00Z", writes no report and never responds, a fake clock, and no override of the ten-minute limit
When the clock reaches "2026-11-16T10:10:01Z" with the LLM scan still running
Then the scanner container is killed, the LLM "scans" row id 12 has state "failed", model NULL and failure_reason "LLM scan exceeded the ten-minute limit.", no "scan_findings" row is written, and the full-scan response is HTTP 201 with the LLM result state "failed"

### Covered requirements (traceability)
- FR-139

### Out of scope
Running the LLM scan's successful path and its isolation (BSB-32-PENDING-2); deciding when to
trigger the scan (BSB-32-PENDING-3); rendering unavailable and failed states (BSB-32-PENDING-5);
configuring the project's scan model (BSB-32-PENDING-1); static scan failures (BSB-31); provider
administration, key rotation, retry policy and model budget administration; automatic retries;
reusing a prior LLM result; aggregating readiness (BSB-30).

### Notes / dependencies
Depends on BSB-31-PENDING-1 for the "scans" and "scan_findings" records and the static pass,
BSB-32-PENDING-1 for the project's LLM-scan model profile and tier, and BSB-32-PENDING-2 for the
LLM scan service and its container. This story owns the LLM stage's non-completed outcomes and
their exact `failure_reason` strings. It extends "scans" so that state "unavailable" is valid for
stage "llm"; the data-model stage must record that enumeration alongside the model columns.

State "unavailable" is a first-class outcome, not an error: no model result exists, so `model`
stays NULL, no "scan_findings" row is written, and the full scan still returns a normal composite
response. It covers missing configuration, a missing key, a rejected key, a provider failure and
provider-reported budget exhaustion. State "failed" is reserved for the LLM scanner container
exceeding its fixed ten-minute (600-second) limit, mirroring the static stage's timeout rule; the
limit cannot be overridden per project, scan or request. An unavailable or failed scan is never
reused, so a later full scan re-attempts it. Readiness (FR-069, BSB-30) treats state "completed"
or "unavailable" as satisfied and state "failed" as not satisfied; this story persists the states
that check reads, and BSB-30's own stories own the aggregation.

---

## STORY: BSB-32-PENDING-5

**Title:** Show the LLM scan's model and located findings to the author
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **the LLM scan report to show which model ran the scan and every finding's severity, rule, file and line**, so that **I can judge and act on the model-based evidence even though it never blocks my run**.

### Acceptance Criteria

Scenario: A completed LLM scan shows its model and every located finding
Given a completed "scans" row id 12 with stage "llm", build_id 7, state "completed", model "claude-opus-5-5", model_profile_id 8, verdict NULL, report {"model": "claude-opus-5-5", "findings": [{"severity": "CRITICAL", "rule": "LLM-001", "file": "SKILL.md", "line": 3}, {"severity": "HIGH", "rule": "LLM-101", "file": "scripts/run.sh", "line": 14}]}, two matching "scan_findings" rows with accepted false, and a signed-in skill author
When the author opens GET "/scans/12"
Then the response is HTTP 200 and the page contains the heading "LLM security scan", the text "Model: claude-opus-5-5", the text "Advisory: this scan never blocks a run.", and a findings table listing "CRITICAL LLM-001 SKILL.md:3" followed by "HIGH LLM-101 scripts/run.sh:14"

Scenario: A clean completed LLM scan shows no findings and no static verdict
Given a completed "scans" row id 13 with stage "llm", state "completed", model "claude-haiku-5-5" and verdict NULL, and no "scan_findings" rows
When the author opens GET "/scans/13"
Then the response is HTTP 200 and the page contains "Model: claude-haiku-5-5" and "No findings.", and does not contain "Verdict: PASS" or "Verdict: FAIL"

Scenario: An unavailable LLM scan shows its reason
Given a "scans" row id 14 with stage "llm", state "unavailable", model NULL, verdict NULL and failure_reason "No LLM scan model profile is configured for this project."
When the author opens GET "/scans/14"
Then the response is HTTP 200 and the page contains "LLM scan unavailable", "Model: not run" and "No LLM scan model profile is configured for this project.", and does not contain "Scan in progress" or "No findings."

Scenario: A failed LLM scan shows the timeout reason
Given a "scans" row id 15 with stage "llm", state "failed", model NULL, verdict NULL and failure_reason "LLM scan exceeded the ten-minute limit."
When the author opens GET "/scans/15"
Then the response is HTTP 200 and the page contains "LLM scan failed", "Model: not run" and "LLM scan exceeded the ten-minute limit.", and does not contain "Scan in progress"

Scenario: The report route uses the authoring gate and no project-membership check
Given a completed "scans" row id 12 with stage "llm" and a signed-in skill-builders user Carol (user 44) with no "project_members" row for project 3
When Carol opens GET "/scans/12"
Then the response is HTTP 200 and the page renders the same LLM report as for a project member, because the report route applies BSB-18's signed-in skill-builder check only

### Covered requirements (traceability)
- FR-086
- FR-090
- FR-156

### Out of scope
The static scan report's score, recommendation, coverage and verdict (BSB-31-PENDING-5); computing
any verdict (BSB-31-PENDING-3); running the scan or deciding its outcome (BSB-32-PENDING-2 to
BSB-32-PENDING-4); the combined Security tab on the run page (BSB-33/BSB-26); a reviewer-facing
stable scan-report view and its access rule (BSB-33/BSB-36, recorded as a cross-epic gap); SARIF or
other export formats; filtering, sorting or editing findings; accepting an LLM finding.

### Notes / dependencies
Depends on BSB-31-PENDING-5 for the authoring report route GET "/scans/{id}", its field mapping and
its access rule, and on BSB-32-PENDING-2 for the "scans" row, the stored report and the
"scan_findings" rows, and on BSB-32-PENDING-4 for the unavailable and failed states. This story
extends that route to stage "llm": it renders the heading "LLM security scan", a model line built
from `scans.model`, the advisory banner, and one row per finding with severity, rule, file and
line in descending severity. Because an LLM scan is advisory, `verdict` is NULL and the page
renders no "Verdict:" line; the clean state renders "No findings.", the unavailable state renders
"LLM scan unavailable" and "Model: not run" with its `failure_reason`, and the failed state renders
"LLM scan failed" and "Model: not run" with its `failure_reason`. It does not fall back to "Scan in
progress" for a terminal state.

The access rule is inherited unchanged from BSB-31-PENDING-5: the route is part of the authoring
interface and is gated by BSB-18's signed-in skill-builder check only, is content-addressed and is
not scoped to the build or project that first requested the scan, and applies no
project-membership check. The report contains no credential value. The catalog reviewer consumes
the same evidence through the catalog pull request's scan-report links (FR-111, BSB-36); neither
BSB-33 nor BSB-36 currently owns a stable reviewer-facing scan-report view or its access rule, the
same cross-epic gap BSB-31 records, so this story does not claim one. The page's accessibility
conformance is BSB-38's cross-cutting pass.

---

## STORY: BSB-32-PENDING-6

**Title:** Start a full security scan from the skill page without a run
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 3 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **to start a full static-then-LLM security scan from the skill page for a test project I belong to without creating a run**, so that **I can see both security views for the current content before spending a run on it**.

### Acceptance Criteria

Scenario: A project member starts a full scan and no run is created
Given a signed-in skill author Ada (users id 42) with a "project_members" row for test project 3 with role "member", build 7 at head SHA "4f2c9a1" with a "skill_bundles" row for "4f2c9a1" with bundle_sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", an empty "scans" table, an empty "runs" table, a "projects" row id 3 with llm_scan_model_profile_id 8 and llm_scan_model_tier "medium", a stub static scanner that writes the clean report {"score": 96, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": []}, and a stub model endpoint that completes with one finding
When Ada submits the "Full security check" control on GET "/builds/7" selecting project 3, which calls POST "/api/builds/7/scans/full" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 201 with {"static": {"scan_id": 11, "state": "completed", "verdict": "pass", "reused": false}, "llm": {"scan_id": 12, "state": "completed", "model": "claude-sonnet-5-5", "reused": false}}, exactly one "scans" row exists with stage "static" and verdict "pass", exactly one "scans" row exists with stage "llm", state "completed" and model "claude-sonnet-5-5", the "runs" table still contains 0 rows, and the page renders "Static scan: PASS", "LLM scan: completed" and "Model: claude-sonnet-5-5"

Scenario: The full scan uses the project's configured model profile and tier
Given a signed-in project member Ada with a "project_members" row for project 3, build 7 at head SHA "4f2c9a1" with a packed bundle, a stub static scanner that writes a clean passing report, a "projects" row id 3 with llm_scan_model_profile_id 9 and llm_scan_model_tier "medium", an "integrations" row id 9 with project_id 3, kind "ai_model" and config {"name": "Cheap smoke runs", "vendor": "anthropic", "base_url": "https://api.anthropic.com", "models": {"high": "claude-haiku-5-5", "medium": "claude-haiku-5-5", "low": "claude-haiku-5-5"}}, and a stub model endpoint that completes
When Ada starts the full scan from GET "/builds/7" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the LLM "scans" row has model_profile_id 9 and model "claude-haiku-5-5", and the stub model endpoint received a request naming model "claude-haiku-5-5"

Scenario: A per-scan model override is refused
Given a signed-in project member Ada with a "project_members" row for project 3, build 7 at head SHA "4f2c9a1" with a packed bundle, and a stub static scanner whose container-start counter is 0
When Ada calls POST "/api/builds/7/scans/full" with {"project_id": 3, "skills_commit_sha": "4f2c9a1", "model": "claude-opus-5-5", "model_profile_id": 9, "tier": "high"}
Then the response is HTTP 422 with {"error": "The LLM scan model is configured on the test project and cannot be overridden per scan."}, no "scans" row is created, and the stub static scanner's container-start counter remains 0

Scenario: A signed-in author who is not a project member is refused
Given a signed-in skill author Carol (users id 44) with no "project_members" row for project 3, build 7 at head SHA "4f2c9a1" with a packed bundle, a stub static scanner whose container-start counter is 0, and a stub model endpoint whose request counter is 0
When Carol calls POST "/api/builds/7/scans/full" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"}
Then the response is HTTP 403 with {"error": "You are not a member of this project."}, no "scans" row is created, the stub static scanner's container-start counter remains 0, and the stub model endpoint received 0 requests

Scenario: An author with no project membership sees the control disabled
Given a signed-in skill author Dave (users id 45) with no "project_members" rows, and build 7 at head SHA "4f2c9a1" with a packed bundle
When Dave opens GET "/builds/7"
Then the response is HTTP 200 and the "Full security check" control is disabled with the message "No test project available.", and a direct POST "/api/builds/7/scans/full" with {"project_id": 3, "skills_commit_sha": "4f2c9a1"} returns HTTP 403 with {"error": "You are not a member of this project."} and creates no "scans" row

Scenario: A failing static scan is shown and the LLM stage does not run
Given a signed-in project member Ada with a "project_members" row for project 3, build 7 at head SHA "4f2c9a1" with a packed bundle, a stub static scanner that writes the report {"score": 41, "recommendation": "INSTALL", "coverage": {"complete": true, "files_scanned": 12, "files_total": 12}, "findings": [{"severity": "CRITICAL", "rule": "SS-001", "file": "SKILL.md", "line": 3}]}, and a stub model endpoint whose request counter is 0
When Ada submits the "Full security check" control on GET "/builds/7" selecting project 3
Then the response is HTTP 200 with {"static": {"scan_id": 11, "state": "completed", "verdict": "fail", "reused": false}, "llm": null, "llm_skipped": "static scan did not pass"}, no "scans" row with stage "llm" exists, the stub model endpoint received 0 requests, and the page renders "Static scan: FAIL" and "LLM scan: not run (static scan did not pass)"

### Covered requirements (traceability)
- FR-093
- FR-163

### Out of scope
Running and isolating the LLM container (BSB-32-PENDING-2); the full-scan service, ordering and
response contract (BSB-32-PENDING-3); unavailable and timeout outcomes (BSB-32-PENDING-4);
report rendering (BSB-32-PENDING-5); configuring the project's scan model (BSB-32-PENDING-1); the
static-only control and its project selector (BSB-31-PENDING-6); the full build page and its
access rule (BSB-21); starting a run (BSB-24); the command-line full scan (BSB-37); adding,
removing or listing project members (BSB-22); choosing a model per project member per scan.

### Notes / dependencies
Depends on BSB-21 for the build page GET "/builds/{id}", its head SHA and its access rule, on
BSB-31-PENDING-6 for the static-only control, the project selector pattern and BSB-22's shared
project-membership check, on BSB-22-PENDING-1 for the "project_members" rows and the exact 403
message "You are not a member of this project.", and on BSB-32-PENDING-1 and BSB-32-PENDING-3 for
the configured scan model and the full-scan route. This story owns the "Full security check"
control and the author-facing request contract; it adds the control to BSB-21's build page rather
than owning that page, and it keeps the static-only control as BSB-31-PENDING-6's separate action.

The control carries a project selector listing only the test projects in which the signed-in
author has a current `project_members` row; an author with no membership sees the control disabled
with "No test project available." rather than a selector. The request carries only `project_id`
and `skills_commit_sha`; the route rejects any `model`, `model_profile_id` or `tier` field with
HTTP 422 and the message "The LLM scan model is configured on the test project and cannot be
overridden per scan." before any scan starts, so FR-163's project-level model cannot be bypassed.
The route applies the project-membership check before the bundle lookup, the scan or any model
call. A full scan creates no `runs` row, run branch or run report, and a static failure is shown
as a result rather than an error page. The page's accessibility conformance is BSB-38's
cross-cutting pass.

---

## STORY: BSB-32-PENDING-7

**Title:** Prove a failing or unavailable LLM scan never blocks a run
**Epic:** BSB-32 · **Release:** MVP · **Estimate:** 2 · **Labels:** FA-12, MVP

### Story
As a **skill author**, I want **a failing, unavailable or missing LLM scan to leave my run's start and final verdict unaffected**, so that **a second security opinion can never stall delivery**.

### Acceptance Criteria

Scenario: A completed LLM scan with a critical finding does not change the run's verdict
Given two builds 7 and 8 at head SHA "4f2c9a1" that each have a completed static "scans" row with verdict "pass" for skills_commit_sha "4f2c9a1", build 7 has a completed LLM "scans" row id 12 with stage "llm" and one "CRITICAL" finding with rule "LLM-001", build 8 has no LLM "scans" row, an agent stub completes for both, and the shared verification stub returns final verdict "pass" for both
When the run-start preflight starts a run for build 7 and a run for build 8 and both runs finish
Then both run-start preflights return HTTP 201, both "runs" rows reach a terminal state with final_verdict "pass" from the verification layer, and build 7's run record does not reference the LLM finding in its claimed verdict, final verdict or verification result

Scenario: An unavailable LLM scan does not block a run
Given build 7 at head SHA "4f2c9a1" with a completed static "scans" row with verdict "pass", an LLM "scans" row id 12 with stage "llm", state "unavailable" and failure_reason "No LLM scan model profile is configured for this project.", an agent stub that completes, and the shared verification stub returns final verdict "pass"
When the run-start preflight starts a run for build 7 and the run finishes
Then the run-start preflight returns HTTP 201, the "runs" row reaches a terminal state, and the final_verdict recorded is "pass" with the LLM unavailable reason absent from the run's verdict and verification result

Scenario: A failed LLM scan does not block a run
Given build 7 at head SHA "4f2c9a1" with a completed static "scans" row with verdict "pass", an LLM "scans" row id 12 with stage "llm", state "failed" and failure_reason "LLM scan exceeded the ten-minute limit.", an agent stub that completes, and the shared verification stub returns final verdict "pass"
When the run-start preflight starts a run for build 7 and the run finishes
Then the run-start preflight returns HTTP 201, the "runs" row reaches a terminal state, and the final_verdict recorded is "pass" with the LLM failure reason absent from the run's verdict and verification result

Scenario: Run start never triggers or waits for the LLM scan
Given build 7 at head SHA "4f2c9a1" with a packed bundle, a stub static scanner that writes a clean passing report, a configured LLM-scan model profile, and a stub model endpoint whose request counter is 0
When the run-start preflight for project 3 runs for build 7 at "4f2c9a1"
Then the preflight calls POST "/api/builds/7/scans/static" and does not call POST "/api/builds/7/scans/full", the stub model endpoint received 0 requests, and no "scans" row with stage "llm" is created by the run start

### Covered requirements (traceability)
- FR-085

### Out of scope
Implementing run start, packaging, execution or verification (BSB-24, BSB-25, BSB-26 and
BSB-29); the static scan gate and run refusal (BSB-31 and BSB-27); the LLM scan's own outcomes
(BSB-32-PENDING-2 to BSB-32-PENDING-4); aggregating the four readiness checks (BSB-30); changing
the run's own model profile or tier; forcing an LLM scan before every run; making a run wait for
the LLM stage; letting an LLM finding override a static block.

### Notes / dependencies
Depends on BSB-24 for run start, BSB-26 for execution and the terminal run state, BSB-29 for the
shared verification layer's final verdict, BSB-27 for the static gate, and BSB-31-PENDING-1 for
the static route. This story owns the non-gating proof and the contract that run start reads only
the static scan: it adds no run-start behaviour of its own and does not change BSB-24's request or
BSB-26's outcome rules. A completed LLM scan's findings, an unavailable record and a failed record
are all advisory; none appears in the run's claimed verdict, final verdict or verification result,
and none changes the run's ability to start or finish.

The only place an LLM scan state is consulted is readiness (FR-069, BSB-30), which treats state
"completed" or "unavailable" as satisfied and state "failed" as not satisfied; that aggregation is
BSB-30's, and this epic supplies the persisted states it reads. The LLM scan is triggered by the
full scan from the skill page (BSB-32-PENDING-6) or the command line (BSB-37), never by run start;
the run-start path calls only the static route (BSB-31-PENDING-1). No run gate, packaging rule or
catalog-submission rule may depend on LLM findings, as the epic's Notes require.

---

**Story coverage summary**

| Requirement | Exercising story | Acceptance criteria that covers it |
|---|---|---|
| FR-082 | BSB-32-PENDING-3 | "A passing static scan triggers the LLM scan on the same content"; "A failing static scan prevents the LLM scan"; "A reused static pass still triggers the LLM scan for that content" |
| FR-083 | BSB-32-PENDING-2 | "The scan container receives only the model key and no other credential" |
| FR-084 | BSB-32-PENDING-2 | "The scan container can reach only the model endpoint" |
| FR-085 | BSB-32-PENDING-7 | "A completed LLM scan with a critical finding does not change the run's verdict"; "An unavailable LLM scan does not block a run"; "A failed LLM scan does not block a run" |
| FR-086 | BSB-32-PENDING-5 | "A completed LLM scan shows its model and every located finding" |
| FR-090 | BSB-32-PENDING-5 | "A completed LLM scan shows its model and every located finding"; "A clean completed LLM scan shows no findings and no static verdict" |
| FR-093 | BSB-32-PENDING-6 | "A project member starts a full scan and no run is created"; "A signed-in author who is not a project member is refused"; "An author with no project membership sees the control disabled" |
| FR-139 | BSB-32-PENDING-4 | "No LLM-scan model profile is configured"; "The configured model profile has no model key"; "The model provider rejects the configured key"; "The model provider reports budget exhaustion"; "The LLM scanner exits before writing a report" |
| FR-156 | BSB-32-PENDING-5 | "A completed LLM scan shows its model and every located finding" |
| FR-163 | BSB-32-PENDING-1; BSB-32-PENDING-6 | "The owner selects the project's LLM-scan model profile"; "The full scan uses the project's configured model profile and tier" |

All 10 requirements mapped to BSB-32 by `epic-map.json` are covered; no story claims a requirement
outside this epic. FR-163 is configured by BSB-32-PENDING-1 and consumed by BSB-32-PENDING-6; the
two claims are consistent. Readiness aggregation (FR-069) and the reviewer-facing scan-report view
(FR-111) remain other epics' handoffs and are not claimed here.
