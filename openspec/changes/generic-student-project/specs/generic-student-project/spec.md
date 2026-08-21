# Generic Student Project Specification

## Purpose

`clase_08/proyecto` MUST provide a locally runnable, teachable, multi-tenant application for experiments, knowledge assets, and tenant-safe assistant queries. The MVP MUST preserve the proposal defaults and MUST NOT introduce an invitation lifecycle or production-only capabilities.

## Requirements

### Requirement: Local container operation

The project MUST run locally through Docker Compose with separate public landing and authenticated frontend containers, a backend API, PostgreSQL with pgvector, MinIO, and an SMTP-compatible recovery path. The backend MUST be the only application boundary holding database, object-storage, or provider credentials.

#### Scenario: Start the complete local stack

- GIVEN a developer has copied the documented local environment example
- WHEN the documented Compose startup command is run
- THEN the landing frontend, authenticated frontend, backend, PostgreSQL/pgvector, MinIO, and SMTP-compatible path become healthy or report an actionable configuration failure

#### Scenario: Browser cannot access infrastructure credentials

- GIVEN a browser loads either frontend
- WHEN it performs an application operation
- THEN it communicates through the backend and receives no PostgreSQL, MinIO, or model-provider credentials

### Requirement: Identity and recovery

The system MUST support email/password registration, login, logout, and password recovery. Registration MUST create one tenant and an administrator membership. Recovery responses MUST be generic, tokens MUST be single-use with a default 30-minute lifetime, and request throttling MUST be configurable.

#### Scenario: Register and authenticate

- GIVEN a user submits a valid unused email and password
- WHEN registration completes
- THEN one tenant and an administrator membership are created and the user can log in

#### Scenario: Recovery does not disclose account existence

- GIVEN a recovery request names either an existing or unknown email
- WHEN the request is processed
- THEN the externally visible response has the same generic shape and does not disclose whether an account exists

#### Scenario: Expired or reused recovery token is rejected

- GIVEN a recovery token is expired or has already been consumed
- WHEN it is submitted to set a password
- THEN the password is not changed and the request fails safely

### Requirement: Tenants, memberships, roles, and permissions

Tenant membership MUST be separate from global identity and a user MAY belong to multiple tenants. The backend MUST enforce the default administrator, member, and viewer permissions using trusted authenticated context. Administrators MAY directly create or attach users and memberships. The system MUST NOT implement invitations, invitation tokens, pending invitations, or invitation acceptance.

#### Scenario: Tenant switch selects an authorized membership

- GIVEN a user has memberships in two tenants
- WHEN the user selects the second tenant
- THEN subsequent authorized operations use only the second membership context

#### Scenario: Default role matrix is enforced

- GIVEN an administrator, member, and viewer access the same tenant
- WHEN each attempts administration, mutation, and read operations
- THEN administrators can administer and mutate, members can mutate but not administer, and viewers can read but cannot mutate

#### Scenario: Invitation lifecycle is absent

- GIVEN an administrator creates or attaches a user directly
- WHEN the account is activated through the standard recovery mechanism
- THEN no invitation entity, token, pending state, or acceptance endpoint is created

### Requirement: Trusted tenant context and relational RLS

The backend MUST derive tenant and user identifiers from authenticated server-side state and MUST set transaction-scoped database context. Every tenant-owned relational table, including experiments, results, metrics, documents, ingestion records, chunks, and vector records, MUST enforce PostgreSQL RLS with appropriate `USING` and `WITH CHECK` policies. Application roles MUST NOT have `BYPASSRLS`. Missing, forged, or inconsistent context MUST fail closed.

#### Scenario: Forged tenant identifier cannot widen access

- GIVEN an authenticated user belongs to tenant A
- WHEN the client submits tenant B's identifier in a path, body, header, or query
- THEN reads and writes are evaluated against trusted context and tenant B data is neither returned nor changed

#### Scenario: Cross-tenant relational access is denied

- GIVEN tenant A and tenant B each own relational records
- WHEN a tenant A request attempts to read, insert, update, or delete tenant B records
- THEN the operation is denied or returns no record and tenant B data remains unchanged

#### Scenario: Pool reuse does not leak context

- GIVEN a database connection is returned to a pool after a tenant A transaction
- WHEN the same connection serves a tenant B transaction
- THEN tenant A context is cleared and tenant B can see only tenant B-authorized rows

### Requirement: Experiments, results, and metrics

Authorized users MUST be able to create, update, list, and inspect experiments with lifecycle `draft`, `running`, `completed`, or `failed`. Results MUST be append-only and retain provenance. Metrics MUST support name, type (`number`, `text`, `boolean`, or `json`), typed value, optional unit, step/iteration, timestamp, and result reference.

#### Scenario: Record an experiment result and metric

- GIVEN an authorized member owns an experiment
- WHEN the member records a run result and metric
- THEN the records are linked to the experiment, creator, and timestamps and are visible to authorized tenant readers

#### Scenario: Historical result data is not silently edited

- GIVEN an existing result or metric
- WHEN a client requests an in-place historical payload change
- THEN the original provenance remains unchanged and correction requires a new record or is rejected

### Requirement: MinIO assets and ingestion

The system MUST support tenant-owned PDF, plain text, Markdown, PNG, JPEG, CSV, JSON, and bounded opaque artifacts. The default object limit MUST be 25 MiB and configurable. Buckets MUST be private; every upload, download, delete, and signed-URL operation MUST require backend authorization and tenant ownership checks. Ingestion MUST expose `pending`, `processing`, `ready`, and `failed` states, a bounded user-visible error, and retry behavior. Re-ingestion MUST replace active derived chunks without changing the original object or deleting ingestion audit metadata.

#### Scenario: Unauthorized object access is denied

- GIVEN tenant A owns an object and its key is guessed or obtained by tenant B
- WHEN tenant B requests download, deletion, or a signed URL
- THEN the backend denies the operation and MinIO does not expose the object

#### Scenario: Supported asset is ingested

- GIVEN an authorized member uploads a supported object within the configured size limit
- WHEN ingestion completes
- THEN metadata is tenant-owned, the object is stored privately, and extraction produces tenant-scoped derived content or a visible failed state

#### Scenario: Failed ingestion can be retried safely

- GIVEN ingestion enters `failed` with an actionable error
- WHEN an authorized user requests retry
- THEN processing restarts without making the object public or discarding its audit history

### Requirement: Tenant-safe pgvector and RAG

Document chunks and embeddings MUST be tenant-owned relational/vector data protected by RLS. Similarity retrieval MUST apply tenant and permission constraints before context reaches a model. RAG answers MUST cite tenant-visible documents or chunks.

#### Scenario: Cross-tenant vector similarity is denied

- GIVEN matching embeddings exist for tenants A and B
- WHEN a tenant A user performs retrieval
- THEN only tenant A authorized chunks can be returned to generation or citations

#### Scenario: Missing retrieval context fails closed

- GIVEN tenant context or permission checks are absent or inconsistent
- WHEN a RAG request is made
- THEN retrieval and generation do not proceed with unscoped data

### Requirement: Guarded read-only Text-to-SQL

Text-to-SQL MUST execute through a distinct least-privilege read-only database role against curated tenant-safe views. The system MUST accept only one parsed `SELECT`, enforce tenant context, statement timeout, a maximum of 200 rows, and bounded serialized output. It MUST reject DDL, DML, function/command abuse, unrestricted schemas, secrets access, context mutation, arbitrary SQL, and write-capable assistant actions.

#### Scenario: Safe relational question returns bounded provenance

- GIVEN an authorized user asks about tenant-visible experiment data
- WHEN a generated query is a single valid `SELECT` over curated views
- THEN the query executes under the read-only role and the response exposes the generated query, bounded result metadata, and relevant provenance

#### Scenario: Unsafe generated SQL is rejected

- GIVEN generated SQL contains multiple statements, writes, DDL, context mutation, unrestricted tables, or disallowed functions
- WHEN execution is attempted
- THEN it is rejected before data access or mutation

#### Scenario: Resource bounds are enforced

- GIVEN a permitted query exceeds the timeout, row limit, or serialized result bound
- WHEN it executes
- THEN it is terminated or truncated according to the documented contract and no unbounded result is returned

### Requirement: Combined assistant behavior

The assistant MUST support document, relational, combined, and `auto` modes. The backend MUST authorize each operation and MUST NOT permit model output to select tenant context or mutate application data. Combined answers MUST distinguish document citations from relational results. Provider failures MUST yield clear unavailable or partial results without widening access.

#### Scenario: Combined answer identifies sources

- GIVEN a user asks a question requiring a document and experiment result
- WHEN combined processing succeeds
- THEN the answer identifies which claims came from cited documents and which came from relational results and query provenance

#### Scenario: Provider failure preserves security

- GIVEN an embedding or language-model provider is unavailable
- WHEN an assistant request is processed
- THEN the system reports an unavailable or partial result and does not fall back to unscoped retrieval, public objects, or autonomous writes

### Requirement: Frontend boundary and instructional UX

The project MUST provide separate public landing and authenticated application frontends. The landing frontend MUST expose product explanation and authentication entry points only; authenticated tenant workflows MUST require backend authentication and authorization. The MVP UI MUST be accessible, English-first, and use reusable semantic components. Branding, localization, streaming, and polished analytics are out of scope.

#### Scenario: Public boundary blocks tenant data

- GIVEN an unauthenticated visitor uses the landing frontend
- WHEN the visitor requests tenant experiments, assets, or assistant data
- THEN the request is redirected to authentication or denied and no tenant data is rendered

#### Scenario: Authenticated boundary reflects permissions

- GIVEN a viewer signs into the authenticated frontend
- WHEN the viewer opens tenant workflows
- THEN read-only controls are available while administration and mutation controls are unavailable and backend checks remain authoritative

### Requirement: Audit and failure behavior

The system MUST record bounded audit metadata for authentication recovery, membership and role changes, ingestion actions, object access grants, and assistant retrieval/query operations. Audit records MUST NOT contain secrets or recovery tokens. Security-sensitive errors, missing context, authorization failures, and inconsistent state MUST fail closed with actionable but non-sensitive diagnostics.

#### Scenario: Sensitive operation is auditable without secrets

- GIVEN a role change, object access, recovery request, ingestion action, or assistant query occurs
- WHEN the operation is recorded
- THEN the audit entry identifies actor, tenant, action, outcome, and bounded resource metadata without passwords, credentials, or recovery tokens

#### Scenario: Security failure does not degrade to broader access

- GIVEN authorization, tenant context, storage metadata, or provider state is missing or inconsistent
- WHEN the system cannot safely complete an operation
- THEN it denies or returns a partial/unavailable result and never falls back to an unscoped query, public object, or broader model context

### Requirement: Source and target integrity

The implementation MUST preserve `material_desarrollo/backend`, `material_desarrollo/frontend`, and `material_desarrollo/landing` unchanged. The implementation MUST evolve `clase_08/proyecto` incrementally and MUST NOT delete or replace the target wholesale.

#### Scenario: Source trees and target baseline are preserved

- GIVEN an implementation slice adapts restored source material
- WHEN the slice is reviewed
- THEN all three restored trees remain unchanged and the existing target baseline is extended or selectively revised rather than deleted and recreated wholesale

### Requirement: Reuse traceability and replacement rationale

Every retained or adapted component MUST record its source path, target path, classification, and rationale. Replacing an existing target file MUST record why incremental extension was incompatible.

#### Scenario: Adaptation records are reviewable

- GIVEN a backend, frontend, landing, utility, or test component is retained or adapted
- WHEN the implementation is accepted
- THEN a record identifies source path, target path, classification, rationale, and any target-file replacement incompatibility

### Requirement: Excluded material never enters the target

The target MUST NOT contain or depend on secrets, certificates, production data, payments, MQTT, devices, maps, tax, invitations, or production migrations and deployment assumptions. Invitation behavior MUST remain absent.

#### Scenario: Excluded artifacts are rejected

- GIVEN a candidate source component, configuration, migration, fixture, or generated artifact belongs to an excluded category
- WHEN reuse is classified
- THEN it is excluded and no such content or integration enters the target

### Requirement: Compatible foundation reuse is evaluated

Implementation MUST evaluate and selectively retain or adapt compatible FastAPI bootstrap, authentication, recovery, email, pagination, and test patterns; Vite/React/shadcn shell, forms, tables, and test patterns; and Astro layout, SEO, and contact patterns. Evaluation MUST preserve product behavior, backend security, RLS, MinIO authorization, tenant-safe RAG, guarded Text-to-SQL, and the no-invitations scope.

#### Scenario: Compatible foundations are assessed

- GIVEN a restored foundation pattern is relevant to a target slice
- WHEN the slice is planned and implemented
- THEN compatibility is evaluated and the pattern is retained or adapted where compatible, or exclusion is recorded with rationale, without weakening product or security requirements
