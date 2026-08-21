# Proposal: Transform `clase_08/proyecto` into a Generic Student Project

## Decision

Transform **exactly `clase_08/proyecto` in place** into a locally runnable, multi-tenant educational application for managing experiments and knowledge assets and for querying tenant-owned information through a RAG and Text-to-SQL assistant.

The restored projects at **`material_desarrollo/backend`**, **`material_desarrollo/frontend`**, and **`material_desarrollo/landing`** are immutable, read-only reuse sources. Their useful infrastructure and patterns may be selectively retained or adapted into the existing target; they must not be modified or copied wholesale. The current target must likewise be evolved incrementally rather than deleted wholesale. This recovery plan supersedes the previous cleanup/replacement incident and explicitly rejects a sibling target.

The product will favor a teachable, complete local workflow over production-scale operations. Provider integrations will remain configurable behind backend-owned interfaces. Tenant isolation is a mandatory acceptance boundary, not a later hardening task.

## Intent

Students need one coherent reference project that connects the course's relational modeling, object storage, vector retrieval, multi-tenancy, access control, and AI-assisted querying practices. Today those lessons are distributed across practices, while `clase_08/proyecto` remains tied to the backed-up DVEM product.

The transformed project should let a student run the stack locally, register, manage a tenant, create and inspect an experiment, ingest supporting assets, and safely ask questions over both documents and curated relational data. The code and documentation should make the security boundaries observable and explainable.

## Target users and core journey

### Primary users

- **Student/developer:** runs and studies the application locally, configures optional model providers, and verifies isolation behavior.
- **Tenant administrator:** manages tenant users, memberships, roles, and all tenant-owned project data.
- **Tenant member:** manages experiments and assets and uses the assistant according to granted permissions.
- **Tenant viewer:** reads permitted tenant data and uses read-only assistant capabilities.

### MVP journey

1. A user registers and verifies access by logging in.
2. Registration creates a new tenant and makes that user its tenant administrator.
3. The administrator may directly create or attach users and assign tenant roles; there is no invitation or pending-invitation lifecycle.
4. An authorized member creates an experiment, records results and metrics, and uploads documents, images, datasets, or artifacts.
5. The backend stores object bytes in MinIO, metadata in PostgreSQL, and tenant-scoped chunks/embeddings in pgvector-backed tables.
6. The user asks the assistant a question. The backend uses tenant-filtered RAG, guarded read-only Text-to-SQL, or both, and returns an answer with source citations and query provenance.
7. Isolation checks demonstrate that another tenant cannot read, retrieve, mutate, download, or query those resources.

## Product scope

### Application boundaries

The local Compose application will expose these explicit boundaries:

- a **public landing frontend container** for product explanation and authentication entry points;
- a separate **authenticated application frontend container** for tenant workflows;
- a **FastAPI-style backend** as the only trusted application boundary;
- **PostgreSQL with pgvector** for identity, tenancy, authorization, domain metadata, metrics, ingestion state, chunks, and vectors;
- **MinIO** for uploaded object bytes;
- an **SMTP-compatible recovery channel**, with a local mail catcher permitted as the default development setup;
- configurable embedding and language-model adapters owned by the backend.

The two frontends may share design conventions or source packages, but they remain independently runnable and deployable containers. Browsers and model providers never receive database or MinIO credentials.

### Restored-source adaptation boundary

Implementation must preserve the existing `clase_08/proyecto` skeleton and selectively classify source elements as **retained**, **adapted**, **referenced**, or **excluded**. A retained or adapted element must have a traceable source path, target path, classification, and rationale; target-file replacement must record why incremental extension was not viable.

Permitted reuse is intentionally bounded:

- from `material_desarrollo/backend`: useful FastAPI bootstrap/configuration, authentication, password recovery, generic email, pagination, migration/repository utilities, and tests;
- from `material_desarrollo/frontend`: the Vite/React/TypeScript and shadcn shell, router/provider/API conventions, forms, tables, and tests;
- from `material_desarrollo/landing`: Astro layout, public-page, SEO, accessibility, and contact patterns.

All retained code must be reviewed for compatibility; all adapted code must be rewritten where needed for the generic domain and mandatory security model. DVEM behavior and artifacts—including secrets, certificates, data, payments, MQTT, devices, maps, tax, invitations, and production migrations or deployment assumptions—must not enter the target. No source tree may be copied wholesale, no target tree may be deleted wholesale, and `material_desarrollo/**` must remain unchanged.

### Identity and tenant administration

The MVP includes:

- email/password registration, login, logout, and password recovery;
- generic recovery responses that do not disclose whether an account exists;
- one-use recovery tokens with a default 30-minute lifetime and configurable request throttling;
- tenant membership separate from global user identity, allowing a user to belong to more than one tenant;
- a tenant switcher when a user has multiple memberships;
- direct administrator-managed account/membership creation with no invitation entity, invitation token, or pending invitation state;
- tenant-scoped role assignment and permission enforcement in the backend.

The default role model is intentionally small:

| Role | MVP authority |
| --- | --- |
| Tenant administrator | Manage tenant users and roles; manage all experiments and assets; use the assistant. |
| Member | Create and update experiments and assets; use the assistant; no user administration. |
| Viewer | Read tenant experiments/assets and use read-only assistant functions; no mutation. |

A bootstrap-only platform administrator may be configured for local recovery and diagnostics, but it is not a general cross-tenant product workflow. Tenant creation beyond self-registration is deferred unless needed for bootstrap fixtures.

### Experiments, results, and metrics

The MVP experiment lifecycle is `draft -> running -> completed` or `failed`. Authorized users can create, update, list, and inspect experiments and append immutable run results.

Each result records provenance: experiment, creator, timestamps, status, optional input/output summaries, and linked assets. Metrics use a flexible but queryable shape: a required name, type (`number`, `text`, `boolean`, or `json`), typed value, optional unit, step/iteration, timestamp, and result reference. This supports teaching varied workloads without committing to a domain-specific schema.

Editing historical result payloads and metrics is excluded from the default workflow; corrections are represented by a new result or metric record so provenance remains understandable.

### Assets and ingestion

Tenant-authorized users can upload and inspect:

- documents: PDF, plain text, and Markdown;
- images: PNG and JPEG;
- datasets: CSV and JSON;
- generic artifacts as opaque downloads when their configured MIME type and size are allowed.

The default upload limit is 25 MiB per object and is configurable. The backend validates declared and detected type, creates tenant-owned metadata before storage, and tracks ingestion as `pending`, `processing`, `ready`, or `failed` with a user-visible error summary and retry action.

MVP extraction covers text-native PDF, plain text, Markdown, CSV, and JSON. OCR, archive extraction, malware scanning, rich office formats, automatic data profiling, object version history, retention automation, and destructive lifecycle policies are deferred. Re-ingestion replaces the active derived chunks while retaining ingestion audit metadata; it does not silently change the original object.

### Assistant

The assistant supports three backend-controlled modes: document retrieval, relational analysis, and combined answers. An `auto` request may select one or both paths, but the backend—not the model—authorizes every data operation.

RAG responses include citations to tenant-visible documents/chunks. Relational responses expose the generated read-only query, bounded result metadata, and relevant experiment/result references. Combined responses identify which claims came from documents and which came from relational results. Provider failures produce a clear unavailable/partial result without bypassing authorization or exposing another tenant's data.

Provider contracts are configurable for embeddings and generation. A local OpenAI-compatible endpoint may be used for the teaching path; external providers are opt-in and disabled until explicitly configured. Provider adapters receive only the minimum authorized context. Production provider governance and guarantees are out of scope.

## Mandatory security rules

Security isolation is part of the MVP definition.

1. **Trusted context:** the backend derives tenant and user identifiers from authenticated server-side state and sets transaction-scoped database context. Client payloads, generated SQL, and model output cannot select or mutate trusted context.
2. **RLS everywhere tenant-owned:** every tenant-owned relational table—including documents, chunks, embeddings/vector records, experiments, results, and metrics—uses PostgreSQL RLS with appropriate `USING` and `WITH CHECK` policies. Application roles do not have `BYPASSRLS`.
3. **Connection-pool containment:** trusted context is transaction-local, cleared by transaction completion, and verified not to leak across reused connections.
4. **Guarded Text-to-SQL:** generated queries execute through a distinct least-privilege, read-only role against curated tenant-safe views. Only one parsed `SELECT` statement is accepted. DDL, DML, function/command abuse, unrestricted schemas, secrets, context mutation, and arbitrary SQL are rejected. Statement timeout, row limit, and bounded result size are enforced.
5. **RAG authorization:** tenant filtering and permission checks occur before context reaches the model. Similarity search cannot widen the authorized tenant scope.
6. **MinIO authorization:** buckets are not public. Upload, download, delete, and any short-lived signed URL require backend authorization plus tenant ownership checks. Object keys are opaque and tenant-partitioned; possession of a guessed key is insufficient.
7. **Auditing:** authentication recovery, membership/role changes, ingestion actions, object access grants, and assistant retrieval/query operations record bounded audit metadata without storing secrets or recovery tokens.
8. **Failure behavior:** missing or inconsistent tenant context fails closed. Security-sensitive failures do not fall back to unscoped queries, public objects, or broader model context.

Executable checks must cover cross-tenant relational reads/writes, vector retrieval, object access, SQL mutation attempts, forged tenant identifiers, and pooled-context reuse.

## Affected areas

All implementation changes are confined to `clase_08/proyecto`, including its:

- Compose topology, environment examples, health checks, and local run documentation;
- FastAPI-style routes, services, authorization, provider interfaces, and recovery mail integration;
- PostgreSQL schema, migrations, least-privilege roles, RLS policies, curated SQL views, and verification scripts;
- MinIO bucket policy and backend-mediated object workflows;
- landing and authenticated frontend applications, navigation, administration, experiment, asset, ingestion, and assistant screens;
- fixtures and executable security/integration checks.

Practices under `clase_02` through `clase_07` are evidence sources and must remain unchanged. The immutable `material_desarrollo/{backend,frontend,landing}` trees are bounded reuse sources and must remain unchanged. Within the target, excluded DVEM-specific code may be removed only through selective, reviewed edits; wholesale target deletion is forbidden. Existing DVEM data and production migrations are not migrated into the new domain.

## MVP defaults resolving exploration questions

| Question | Reversible MVP default |
| --- | --- |
| Initial tenancy | Self-registration creates one tenant and administrator membership; users may later hold multiple memberships. |
| User onboarding without invitations | Administrators directly create/attach accounts and memberships; password setup uses the standard recovery mechanism, without invitation state. |
| Experiment model | Four terminal-aware states with append-only results and typed flexible metrics plus provenance. |
| Content support | Text-native PDF/TXT/MD, PNG/JPEG, CSV/JSON, and bounded opaque artifacts; 25 MiB default. |
| Ingestion | Backend-managed stateful jobs with visible failure/retry; no separate production queue requirement for the first slice. |
| Model providers | Backend adapters; local OpenAI-compatible configuration supported; external transmission is explicit opt-in. |
| Assistant UX | `auto`, document, relational, and combined modes; citations and SQL/provenance shown; no autonomous writes. |
| Text-to-SQL limits | Curated views, one `SELECT`, configurable timeout, maximum 200 rows, and bounded serialized output. |
| Recovery mail | SMTP interface with a local mail catcher for development; generic response, one-use 30-minute token, throttling. |
| Frontend | Accessible English-first instructional UI using reusable semantic components; branding and localization deferred. |
| Operations | Local Compose, example secrets, health checks, and reset/verification instructions; no production SLA. |

These defaults may be refined in specifications or design only when the security boundary and bounded product outcome remain unchanged.

## Deferred capabilities and non-goals

The first product slice will not include:

- a sibling replacement project, wholesale source copying, wholesale target deletion, modification of `material_desarrollo/**`, or preservation of DVEM-specific behavior;
- migration of DVEM secrets, certificates, data, production migrations, payments, MQTT, devices, maps, tax, or invitation behavior;
- invitation workflows, pending invitations, or invitation acceptance;
- social login, SSO, MFA, fine-grained custom role builders, or enterprise identity lifecycle;
- tenant deletion, merge, billing, quotas, export, legal retention, or automated backup/restore;
- OCR, malware scanning, office/archive extraction, large-file multipart workflows, or production job orchestration;
- model training, experiment scheduling, hyperparameter search, live telemetry, or arbitrary notebook execution;
- arbitrary database access, write-capable assistant tools, autonomous actions, or model-controlled tenant selection;
- production deployment, high availability, autoscaling, SLA monitoring, secrets management platforms, or compliance certification;
- polished branding, localization, advanced analytics dashboards, streaming responses, or long-term conversation memory.

## Delivery boundary

Implementation should use chained, reviewable slices under the selected `auto-chain` strategy and a target budget of 600 changed lines per slice. Each affected slice must preserve the target baseline and record source-to-target adaptation traceability. The proposal does not prescribe exact PRs, but security foundations must precede features that depend on them. A sensible sequence is: reconcile the local skeleton; selectively adapt backend/frontend/landing foundations; identity/tenancy/RLS; experiments; assets/ingestion; assistant; frontends and documentation; then end-to-end isolation and source-preservation evidence.

The previous destructive cleanup direction is superseded. No code is implemented by this proposal.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Cross-tenant exposure through missed filters or vectors | RLS is mandatory defense-in-depth; trusted transaction context and attack-oriented checks cover relational and vector paths. |
| Generated SQL escapes intended access | Separate role, curated views, parser/allow-list validation, single-statement rule, and resource limits; fail closed. |
| MinIO bypasses database isolation | Private buckets and backend authorization for every object operation or signed URL. |
| Connection pooling reuses tenant context | Transaction-local context and explicit pool-reuse verification. |
| Scope becomes production-platform work | Preserve the local teaching journey; keep operational, compliance, and advanced lifecycle work deferred. |
| Provider choice couples or blocks local use | Stable backend adapter contracts, explicit provider configuration, and graceful unavailable behavior. |
| Flexible metrics become unqueryable | Keep typed columns for common values and reserve JSON for structured exceptions, all with provenance. |
| Selective reuse accidentally imports DVEM behavior, secrets, or production assumptions | Classify reuse at file/class/function level; prohibit excluded integrations and sensitive artifacts; review dependencies and configuration before adaptation. |
| Recovery work repeats the cleanup incident or overwrites useful target/source material | Keep restored sources immutable, preserve the target skeleton, prohibit wholesale copy/deletion, snapshot each slice, and require source-to-target traceability with replacement rationale. |

## Rollback and recovery

Because this is an incremental in-place transformation with no DVEM data migration, rollback is repository- and environment-based:

- snapshot affected target paths before each slice and revert only the corresponding implementation commits or changes inside `clase_08/proyecto`;
- stop the local Compose stack and remove only the new project volumes when schema/object reset is required;
- never mutate the restored `material_desarrollo/**` sources during rollback and never restore DVEM secrets, certificates, production data, or production migrations into the target;
- keep migration boundaries, adaptation records, and seed/reset commands explicit so each development slice can be reconstructed.

The current target skeleton is the recovery baseline. No forward compatibility with existing DVEM database volumes or object data is promised.

## Success criteria

The proposal is successful when the implemented MVP demonstrates all of the following locally:

- one documented Compose workflow starts the landing frontend, authenticated frontend, backend, PostgreSQL/pgvector, MinIO, and SMTP-compatible development path;
- a new user can register, log in, recover a password, receive a tenant administrator role, and manage users without invitations;
- role checks permit and deny administration, mutation, and viewing according to the default matrix;
- an authorized user can complete the experiment/result/metric journey and inspect provenance;
- supported assets can be uploaded, authorized, ingested, retried after failure, retrieved, and cited;
- the assistant can produce tenant-scoped document, relational, and combined answers using configured provider adapters;
- Text-to-SQL accepts bounded read-only queries over curated views and rejects writes, DDL, unsafe statements, context manipulation, and oversized/slow execution;
- cross-tenant reads, writes, vector retrieval, object access, forged context, and pooled-context leakage are denied by executable checks;
- no invitation lifecycle or DVEM-specific behavior, secrets, certificates, data, payments, MQTT, devices, maps, tax, or production migrations remain in the primary application flow or target configuration;
- `material_desarrollo/{backend,frontend,landing}` remain unchanged, the target was not deleted or replaced wholesale, and every retained/adapted component has reviewable source path, target path, classification, and rationale;
- preservation evidence identifies the pre-slice target baseline and explains every intentional target-file replacement;
- documentation explains the architecture, security assumptions, local provider configuration, reset path, selective-reuse traceability, and known non-production limitations.

## Proposal question round

Automatic mode requires reversible defaults rather than blocking product questions. The following questions remain appropriate for stakeholder review before later production-oriented expansion:

1. Should users ultimately join existing tenants through an administrator-only direct action, a verified domain policy, or a future invitation flow?
2. Which experiment fields and metric types deserve first-class domain columns after real student projects reveal common patterns?
3. Which sensitive-data classes, if any, may be sent to external model providers under a future governance policy?
4. Which production ingestion safeguards—malware scanning, OCR, retention, or background queues—should be prioritized first?

For this proposal, the defaults in the table above apply. A later question round may revise deferred capabilities but must not weaken tenant isolation, backend-owned context, read-only Text-to-SQL, or backend-authorized object access.
