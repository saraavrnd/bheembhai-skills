# Template guide — sdlc-arch-design

Guidance for filling this skill's templates, section by section. It used to sit in HTML
comments inside the template and example files; it is kept here, word for word, so those
files hold only visible content. Read the part for a template before you fill it. Do not
copy this guidance into the output.

## `templates/ADR.md.tmpl`

### Context

The forces at play: the requirement(s) driving this, constraints, what we knew at the time.
Reference PRD requirement IDs where relevant.

### Decision

The choice made, stated plainly.

### Alternatives considered

The options we rejected and the one-line reason each lost.

### Consequences

What becomes easier and what becomes harder. Include follow-on work and the conditions
under which we'd revisit this decision.

## `templates/architecture.md.tmpl`

### Overview

The agreed architecture in a few sentences.

### Diagrams

Include whichever diagrams best explain the design. Mermaid preferred.

### Component / container diagram

Show the major building blocks and the primary external integrations.

### Sequence diagram

Show the main request or workflow lifecycle end-to-end.

### State diagram

Show meaningful lifecycle state machines such as run / step / attempt / approval.

### Deployment / topology diagram

Show how the runtime is deployed locally or in the target environment.

### Other diagrams

Add any additional view that makes the design easier to understand.

### Data flow

The main paths through the system (e.g. request lifecycle), step by step and/or as a diagram.

### Cross-cutting concerns

How auth, logging, config, error handling, and (if relevant) privacy/compliance are
handled consistently across components.

### Non-functional design

For each key NFR (NFR-NNN): the concrete mechanism that satisfies it.

### Seams for later

Where the MVP is intentionally simple and how it would evolve (e.g. extract a service,
swap a store) without a rewrite.

### Traceability

Which PRD feature areas / requirement IDs each component covers.

## `templates/tech-design-proposal.md.tmpl`

### 1. System summary

3-5 sentences: what the system is, its major components implied by the feature areas, and
the non-functional drivers (scale, latency, privacy, compliance) that shape the design.

### 2. MVP vs Later (scope the design)

What the design must support at MVP, and what it should only leave room for. Prevents
over-engineering.

### 3.3 Architecture style

monolith / modular monolith / services. For MVP, justify the simplest option that meets
the NFRs, and name the seams where it would split later.

### 3.4 Data stores

primary DB + any specialised store the PRD actually requires.

### 3.5 Key libraries / external services

only those the requirements demand.

### 3.6 Deployment target

honour the user's target (e.g. local Docker first); note the path to extend later.

### 3.7 Testing approach

default: TDD — acceptance criteria become failing tests before implementation. Name the
test runner per layer (unit / integration / e2e).

### 3.8 Repository shape

monorepo vs multi-repo; high-level package/service layout.

### 4. Proposed architecture (overview)

Components and how data flows between them. A simple diagram or component list.

### 5. Proposed data model (sketch)

Main entities and relationships, traceable to PRD requirement IDs.

### 6. Versions (pinned)

verify current stable versions; flag any recent breaking changes.

### 8. Assumptions made

Everything inferred because it wasn't specified.
