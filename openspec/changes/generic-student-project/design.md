# Technical Design: Selective Adaptation of the Generic Student Project

## Decision summary

`clase_08/proyecto` remains the in-place transformation target and its current 11-file skeleton remains the recovery baseline. The canonical application roots are exactly `clase_08/proyecto/backend`, `clase_08/proyecto/frontend`, and `clase_08/proyecto/landing`. `apps/*` and `services/api` are rejected as unnecessary monorepo layering: this project has three independently containerized applications, not shared workspace packages that justify nested monorepo namespaces.

Implementation MUST preserve those three root folders after recovery reconciliation and extend or selectively revise them in place. It MUST NOT recreate `apps/*` or `services/api`, delete and recreate the target, or copy a restored application wholesale. The current placeholder files under `apps/{landing,web}` and `services/api` are recovery inputs only; the first slice relocates them atomically to the canonical roots, updates Compose build contexts, verifies equivalent health behavior, and removes only the vacated empty wrapper directories.

The restored trees are immutable, read-only inputs:

- `material_desarrollo/backend`
- `material_desarrollo/frontend`
- `material_desarrollo/landing`

Useful infrastructure is evaluated at file, class, or function level as **retained**, **adapted**, **referenced**, or **excluded**. Existing target files are amended in place where practical and may be replaced or removed only when incremental extension is incompatible. These process decisions and the operational read-only rule for `material_desarrollo/**` are recorded exclusively in OpenSpec and Engram, never in product files.

This amendment preserves the approved product and security architecture: separate Astro landing and Vite/React application containers; FastAPI as the only trusted application boundary; PostgreSQL/pgvector with transaction-local tenant context and forced RLS; private MinIO; generic SMTP recovery; opaque server-side sessions; tenant roles; experiments/results/metrics; assets and ingestion; tenant-safe RAG; guarded read-only Text-to-SQL; and no invitations. Container separation comes from `backend/Dockerfile`, `frontend/Dockerfile`, `landing/Dockerfile`, and root `compose.yaml`, not from `apps/*` or `services/*` nesting. Delivery remains stacked-to-main, in dependency order, with a target maximum of 600 changed lines per slice.

## 1. Recovery baseline and non-destructive rule

The current target contains exactly these 11 baseline files:

```text
clase_08/proyecto/
├── .env.example
├── .gitignore
├── Makefile
├── README.md
├── compose.yaml
├── apps/landing/Dockerfile
├── apps/landing/index.html
├── apps/web/Dockerfile
├── apps/web/index.html
├── services/api/Dockerfile
└── services/api/app/main.py
```

They already establish local service names, ports, health checks, private MinIO initialization, Mailpit, named local volumes, placeholder-only browser boundaries, and a backend `/health` contract. Those decisions are useful recovery inputs, not disposable incident output. Their wrapper paths are not architectural commitments: the first slice preserves their bytes and behavior while relocating them to `landing`, `frontend`, and `backend`.

### 1.1 File-by-file recovery treatment

| Existing target file | Treatment | Required continuity |
| --- | --- | --- |
| `.env.example` | Retain and append placeholders incrementally. | Keep values non-secret; add separate migrator/runtime/assistant credentials and provider opt-ins only when their slice needs them. |
| `.gitignore` | Retain and append generated Python, Vite, Astro, test, and local-data exclusions as needed. | Never weaken `.env`, cache, build-output, or local-data exclusions. |
| `Makefile` | Retain existing `config`, `up`, `down`, `reset-local`, and `logs`; add narrow migration/test/check aliases. | Existing commands remain valid or receive a documented compatibility alias. |
| `README.md` | Amend progressively. | Keep only product-facing reset/rollback guidance; correct the obsolete “replaces” wording to “recovers and adapts.” |
| `compose.yaml` | Amend service-by-service; first change only build contexts from `./apps/landing`, `./apps/web`, and `./services/api` to `./landing`, `./frontend`, and `./backend`. | Preserve service names, dependencies, health checks, and public ports; later split database credentials and add migration readiness without recreating the file. |
| `apps/landing/Dockerfile` -> `landing/Dockerfile` | Relocate byte-for-byte in recovery reconciliation; later adapt from static Nginx copy to an Astro multi-stage build. | Preserve port 80 and health behavior. Later replacement rationale: the static copy cannot build Astro sources. |
| `apps/landing/index.html` -> `landing/index.html` | Relocate byte-for-byte and keep as the public placeholder until `landing/src/pages/index.astro` is healthy; then remove it in the landing slice. | Astro owns the route after cutover; retaining a second static entry would be stale and ambiguous. |
| `apps/web/Dockerfile` -> `frontend/Dockerfile` | Relocate byte-for-byte; later adapt from static Nginx copy to a Vite multi-stage build. | Preserve port 80 and health behavior; add SPA fallback explicitly. |
| `apps/web/index.html` -> `frontend/index.html` | Relocate byte-for-byte, then adapt in place into Vite's root HTML entry. | Preserve accessible title/fallback intent while replacing the placeholder body with the Vite mount node. |
| `services/api/Dockerfile` -> `backend/Dockerfile` | Relocate byte-for-byte; later adapt incrementally to install the pruned backend dependency set and run FastAPI. | Preserve Python 3.12 base intent, work directory, port 8000, and health endpoint. |
| `services/api/app/main.py` -> `backend/app/main.py` | Relocate byte-for-byte; later replace the standard-library placeholder with the selectively adapted FastAPI bootstrap. | Preserve `GET /health` response intent; `ThreadingHTTPServer` cannot host FastAPI dependency injection, lifespan, security middleware, or routers. |

The relocation is a single reviewed placeholder transition: create the three canonical roots, move each file without changing content or mode, update only the three Compose build contexts, verify all health contracts, then remove the empty `apps` and `services` wrappers. If validation fails before commit, abort the whole transition and leave the recovery baseline untouched. Once accepted, rollback restores prior placeholder behavior inside the canonical roots and reverts other slice changes without reviving the rejected wrappers. No intermediate committed state may contain duplicate active roots, broken build contexts, or absent application boundaries.

After reconciliation, new directories and files are added only beneath `backend`, `frontend`, `landing`, or the root infrastructure/documentation paths required by the active slice. `apps/*` and `services/api` MUST NOT return.

## 2. Target architecture and trust boundaries

The existing Compose topology is retained and incrementally completed:

| Boundary | Responsibility | Trusted credentials |
| --- | --- | --- |
| `landing` | Public Astro site, product explanation, SEO, accessible contact flow, links into web authentication. It performs no tenant fetches. | Public web/login/API URLs only. |
| `web` | Vite/React authenticated UI for auth, tenant switching, members, experiments, assets, ingestion, and assistant provenance. | Public API URL only; session is an HttpOnly cookie. |
| `api` | FastAPI transport, application services, authorization, transactions, object access, ingestion, providers, RAG, and SQL guard. | Runtime DB, assistant DB, MinIO, SMTP, recovery, and optional model-provider credentials. |
| `db` | PostgreSQL 16 + pgvector, generic schema, role separation, constraints, RLS, curated views, vectors, and audit. | Bootstrap/migrator credentials remain server-side. |
| `minio` / `minio-init` | Private object bytes and idempotent private bucket creation. | Root bootstrap credentials only in Compose/API/init. |
| `mailpit` | Local SMTP catcher and teaching UI. | No production credentials. |

The API remains the sole trusted application boundary. The browser, restored code, object keys, generated SQL, model output, and client-provided tenant identifiers are all untrusted inputs.

After the placeholder transition, the target source organization evolves directly beneath the three requested application roots:

```text
clase_08/proyecto/
├── backend/                        # FastAPI; only trusted application boundary
│   ├── Dockerfile                  # backend container boundary
│   ├── migrations/                 # fresh generic Alembic baseline and later revisions
│   ├── app/
│   │   ├── api/                    # transport and DTOs
│   │   ├── core/                   # settings, engines, transactions, errors
│   │   ├── domain/                 # framework-independent policy and value types
│   │   ├── services/               # use cases and authorization boundaries
│   │   ├── repositories/           # persistence adapters; no authorization decisions
│   │   ├── security/               # password, session, CSRF, context, permissions, audit
│   │   ├── storage/                # MinIO adapter; no raw-key public methods
│   │   ├── ingestion/              # extraction/chunking/embedding orchestration
│   │   ├── assistant/              # RAG, SQL guard/reader, combined orchestration
│   │   └── providers/              # mail, embedding, and generation adapters
│   └── tests/{unit,integration}/
├── frontend/                       # Vite/React/shadcn; authenticated UI
│   ├── Dockerfile                  # authenticated frontend container boundary
│   ├── src/
│   └── tests/
├── landing/                        # Astro; public-only
│   ├── Dockerfile                  # public landing container boundary
│   ├── src/
│   └── tests/
├── infra/{postgres,minio}/
├── scripts/                         # product runtime/development/security utilities
└── README.md                        # product-facing local usage and architecture
```

Each root owns its dependency manifest, source tree, tests, build configuration, and Dockerfile. Cross-container communication is configured by root `compose.yaml`; no shared-package workspace or path alias may depend on an `apps` or `services` wrapper. Everything under `clase_08/proyecto` must be product runtime, development support, product tests, or product-facing documentation. Adaptation history, recovery bookkeeping, source inventories, and other process traceability belong only in OpenSpec and Engram.

## 3. Selective source-to-target mapping

The paths below are evaluation inputs, not copy instructions. The same-named target roots (`backend`, `frontend`, `landing`) deliberately mirror the restored-source boundaries, reducing target-path rewrites, package working-directory changes, import alias churn, test relocation, and Docker build-context translation. This is selective reuse, not whole-tree copying.

“Retain” means the bounded implementation can remain substantially recognizable after import/config review. “Adapt” means reuse the seam or algorithm while rewriting domain, trust, and configuration assumptions. “Reference” means inspect behavior/tests but write a target-owned implementation. “Exclude” means the source must not enter the target.

### 3.1 Backend mapping

| Source | Target | Classification and adaptation contract |
| --- | --- | --- |
| `material_desarrollo/backend/app/main.py` | `clase_08/proyecto/backend/app/main.py` | **Adapt only** FastAPI construction, lifespan shape, CORS/host middleware, router inclusion, docs toggles, and health route. Exclude MQTT startup/subscriptions, refund workers, DVEM model imports, `create_all`, default DVEM admin creation, production hostnames, and DVEM copy. |
| `material_desarrollo/backend/app/core/config.py` | `backend/app/core/config.py` | **Adapt** the Pydantic Settings pattern into a target allow-list. Keep only app/public origins, role-specific DB URLs, MinIO, SMTP, session/recovery, upload, SQL limits, and explicitly opted-in model settings. Do not carry permissive `extra="ignore"` as a way to hide excluded configuration; tests assert forbidden DVEM keys are absent. |
| `material_desarrollo/backend/app/core/db.py` | `backend/app/core/database.py` and `backend/app/core/transactions.py` | **Reference/adapt** sync/async URL and engine patterns. Reject development `metadata.create_all`, session-scoped context, and `system_session`/BYPASSRLS behavior. Add runtime and assistant pools plus one transaction helper that sets `app.user_id` and verified `app.tenant_id` with local `set_config(..., true)`. |
| `material_desarrollo/backend/alembic.ini` and `alembic/env.py` | `backend/alembic.ini` and `backend/migrations/env.py` | **Retain/adapt Alembic infrastructure only**: offline/online modes, `NullPool`, type/default comparison, and target metadata loading. Every import of a DVEM model is excluded. No file under source `alembic/versions/` is reused. |
| `material_desarrollo/backend/app/api/auth/router.py` and `models.py` | `backend/app/api/auth.py` | **Adapt transport validation and request-model patterns** for register/login/logout/session/recovery request/recovery confirm. Exclude verification, social login, invitation, global-user administration, JWT response, and DVEM route semantics. |
| `material_desarrollo/backend/app/api/auth/service.py` and `repository.py` | `backend/app/services/auth.py`, `backend/app/security/{password,sessions,recovery}.py`, and target repositories | **Reference/adapt** password hashing, transaction tests, and generic recovery flow shape. Replace JWT reset/session tokens with opaque hashed session state and one-use keyed-hash recovery tokens. Registration atomically creates user, tenant, membership, roles, permissions, and admin assignment. |
| `material_desarrollo/backend/app/core/email.py` and `email_templates.py` | `backend/app/providers/mail.py` and target templates | **Adapt** SMTP URL-building and multipart-mail patterns behind `MailProvider.send_recovery`. Remove hard-coded recipients/domains, DVEM branding, verification, invitations, WhatsApp, and production credentials. Recovery messages contain the raw token only in the destination URL and never logs/audit. |
| `material_desarrollo/backend/app/services/pagination.py` | `backend/app/services/pagination.py` | **Retain/adapt** bounded page normalization, subquery count, allow-listed ordering, and async execution. Add typed response contracts and ensure the caller's RLS transaction owns the query; pagination never accepts tenant filters as authorization. |
| `material_desarrollo/backend/tests/conftest.py` | `backend/tests/conftest.py` | **Adapt fixture organization** only. Replace SQLite/global-user assumptions with PostgreSQL test transactions, two tenants, three roles, pooled connections, private MinIO, and Mailpit/provider fakes. |
| `material_desarrollo/backend/tests/test_app.py`, `test_auth.py`, `test_pagination_logic.py`, and `tests/core/test_email.py` | `backend/tests/{unit,integration}/**` | **Retain test style; adapt cases** for health, opaque sessions, generic recovery parity, expiry/reuse/races, target URL construction, and RLS-scoped pagination. DVEM assertions are excluded. |
| `material_desarrollo/backend/app/api/{mercadopago,device,environment,location,tax,access,provisioning,reports,settings}`; MQTT modules; DVEM migrations/seeds | no target | **Exclude.** They cannot be imported, copied, or depended upon. |

### 3.2 Authenticated frontend mapping

| Source | Target | Classification and adaptation contract |
| --- | --- | --- |
| `material_desarrollo/frontend/package.json` | `clase_08/proyecto/frontend/package.json` | **Adapt** scripts and the minimal dependency set. Preserve Vite, React, TypeScript, React Router, TanStack Query/Table, react-hook-form, Zod, shadcn/Radix components actually used, Tailwind v4, Sonner, Lucide, Vitest, Testing Library, and ESLint. Prune excluded domain and credential-bearing libraries. |
| `material_desarrollo/frontend/components.json` | `frontend/components.json` | **Retain/adapt** `rsc: false`, Tailwind CSS variables, Lucide, and `@/` aliases. Target `src/styles/index.css` or the chosen existing target CSS path is recorded once and then treated as canonical. Components are reviewed individually; no `components/ui` directory bulk copy. |
| `material_desarrollo/frontend/src/FrontendApp.tsx` | `frontend/src/app/providers.tsx` | **Adapt** QueryClient, RouterProvider, Sonner, and auth-check composition. Remove hostname checks, token refresh/JWT assumptions, global confirm singleton unless required, and DVEM idle policy. Session lookup is cookie-based and tenant changes invalidate all tenant-keyed queries. |
| `material_desarrollo/frontend/src/router/app.router.tsx` | `frontend/src/app/router.tsx` | **Reference/adapt router composition**, not route contents. Routes become auth/recovery and authenticated tenants/members/experiments/assets/assistant. Exclude social callback, invitations, payments, devices, maps, tax, environment, and DVEM admin routes. Backend capability responses drive presentation only. |
| `material_desarrollo/frontend/src/auth/**` excluding social/verification domain behavior | `frontend/src/features/auth/**` | **Adapt** accessible login/register/recovery form and test patterns to opaque-cookie/CSRF contracts. Do not copy JWT decoding, social login, verification, invitation, tax/profile coupling, or DVEM strings. |
| `material_desarrollo/frontend/src/components/ui/*` | `frontend/src/components/ui/*` | **Evaluate individually.** Retain only installed shadcn source components needed by the active slice. Preserve semantic tokens, Radix composition, accessible titles, grouped items, `gap-*`, `cn()`, and `data-icon`; never overwrite local component changes blindly. |
| `material_desarrollo/frontend/src/components/custom/DataTablePagination.tsx`, `DataTableColumnHeader.tsx`, and their tests | `frontend/src/components/data-table/**` | **Adapt** generic TanStack pagination/sorting composition. Remove DVEM labels and ensure server pagination parameters match the backend bounded contract. |
| Existing `useForm` table/form examples and tests under `material_desarrollo/frontend/src/admin/components/settings/**` | `frontend/src/features/**` and colocated `frontend/src/**/*.test.tsx` | **Reference only.** Reuse form/table testing and responsive composition ideas, not environment/tax fields or business components. Target forms use shadcn `FieldGroup` + `Field`, proper invalid state, and accessible dialogs. |
| `material_desarrollo/frontend/src/config/publicUrls.ts` and tests | `frontend/src/lib/public-urls.ts` | **Adapt** trimmed local URL override behavior with no production DVEM fallback. Only landing/web/API public URLs are valid. |
| Map, Leaflet, Google Maps, Mercado Pago, device, tax, invitation, analytics, social auth, DVEM branding and related tests | no target | **Exclude.** Their imports and package dependencies must be absent from target production code. |

### 3.3 Landing mapping

| Source | Target | Classification and adaptation contract |
| --- | --- | --- |
| `material_desarrollo/landing/package.json` | `clase_08/proyecto/landing/package.json` | **Adapt** Astro, sitemap, Tailwind, TypeScript, and Vitest scripts. Remove React integration and map dependencies unless a later approved public component demonstrably requires an island; no such need exists in MVP. |
| `material_desarrollo/landing/src/layouts/BaseLayout.astro` | `landing/src/layouts/BaseLayout.astro` | **Adapt** document structure, canonical/meta/OpenGraph hooks, theme initialization, and accessible slot. Remove hard-coded analytics IDs/scripts, PostHog key, Clarity, Google Analytics, WhatsApp float, DVEM site name/domain/assets, and locale assumptions outside English-first MVP. |
| `material_desarrollo/landing/src/seo/metadata.ts` and `seo/assets.ts` | `landing/src/seo/**` | **Adapt** pure URL, canonical, social metadata, and JSON-LD builders. Configuration comes from public placeholders; organization/application data is generic. Remove DVEM domains, logos, geographic claims, analytics, and generated assets. |
| `material_desarrollo/landing/src/components/HomePage.astro` | `landing/src/pages/index.astro` plus small public components | **Reference/adapt** sectioning, CTA, semantic landmarks, and accessibility. Re-author all copy for the student project and link only to web login/register/recovery. Exclude maps, devices, payments, product telemetry, and DVEM branding. |
| `material_desarrollo/landing/src/components/ContactSection.astro` and `src/contact/contactForm.ts` | `landing/src/components/ContactSection.astro` and `landing/src/contact/contact-form.ts` | **Adapt** bounded fields, honeypot, accessible status, request payload, and mailto fallback. Remove WhatsApp phone/links and old sales semantics. The backend public contact endpoint, if retained, uses the generic `MailProvider` and has no tenant access. |
| `material_desarrollo/landing/tests/{public-urls,seo,contact-form,home-page}.test.ts` | `landing/tests/{public-urls,seo,contact-form,home-page}.test.ts` | **Adapt** pure helper/render assertions. Exclude assertions for analytics keys, maps, devices, DVEM assets, production locales, and generated output. |
| `dist`, `.astro`, generated sitemap/output, maps, analytics, production Traefik/routing, DVEM localization/brand assets | no target | **Exclude.** Generated artifacts are rebuilt from target source and are not adaptation inputs. |

## 4. Adapter seams that preserve useful code as the base

Selective adaptation is organized around stable seams so generic infrastructure can remain while domain behavior changes behind it.

| Seam | Input/output contract | Source reuse boundary |
| --- | --- | --- |
| `Settings` | Explicit validated target settings; secret values are backend-only. | Adapt Pydantic settings shape, but define a fresh allow-list and fail on missing required target values. |
| `ApplicationFactory` | Builds FastAPI with target lifespan, middleware, routers, and `/health`. | Adapt source bootstrap mechanics; excluded workers/routes cannot register themselves. |
| `TenantTransaction` | Authenticates session, begins transaction, sets user context, verifies membership, sets tenant context, checks permission, then exposes repositories. | Adapt engine/session mechanics only. No repository or caller can create this context from a request tenant ID. |
| `SessionStore` | Create, lookup, revoke opaque hashed sessions and session-bound CSRF state. | Reuse hashing/repository patterns, not JWT or local-storage contracts. |
| `RecoveryTokenStore` / `MailProvider` | One-use keyed-hash token lifecycle and `send_recovery(recipient, reset_url)`. | Reuse SMTP/template/URL/test patterns after removing verification/invitation/brand behavior. |
| `PageRequest` / `Page[T]` | Bounded page, per-page, allow-listed sort, items and totals. | Retain pagination algorithm under the caller's already-established RLS transaction. |
| `Repository[T]` | Persistence only; receives an established transaction and never authorizes. | Adapt SQLAlchemy/SQLModel patterns; tenant columns and RLS are mandatory. |
| `AuthorizedAsset` / `ObjectStore` | Storage operations accept only an authorized asset capability, never a raw client key. | Fresh target seam; MinIO SDK is isolated behind it. |
| `TextExtractor`, `Chunker`, `EmbeddingProvider` | Bounded authorized bytes/text to deterministic chunks/vectors. | Fresh target interfaces; source code supplies no trusted tenant context. |
| `SqlGuard` / `SqlExecutor` | One parsed allow-listed SELECT to bounded read-only rows/provenance. | Fresh target security seam; no source query helper bypasses it. |
| `GenerationProvider` | Minimum authorized context to typed generation result. | Fresh target interface; external endpoints require opt-in. |
| `ApiClient` | Cookie credentials, CSRF on mutations, stable error codes, typed payloads. | Adapt source API conventions; remove JWT decode/storage and domain-specific interceptors. |
| `AuthSessionProvider` / `TenantProvider` | Session capabilities and selected authorized membership; tenant switch clears tenant-query cache. | Adapt provider composition, not DVEM stores or route guards. |
| `DataTable` / feature forms | Server-bounded pagination and semantic shadcn form/table composition. | Adapt reusable UI primitives individually; domain columns/actions remain target-owned. |
| `PublicUrl` / SEO / contact helpers | Public-only URLs and pure metadata/payload builders. | Adapt landing pure functions; remove production constants and excluded channels. |

## 5. Dependency pruning and exclusion gates

A dependency is retained only when a target module in the same or immediately following slice uses it. Dependency rationale is maintained in OpenSpec/Engram planning artifacts, not in the product tree.

### Backend

Candidate retained foundation: FastAPI/Starlette, Pydantic Settings, SQLAlchemy/SQLModel, Alembic, asyncpg/psycopg, Argon2/pwdlib, email validation, multipart handling, pytest/pytest-asyncio, HTTPX, and one generic SMTP implementation. Target additions such as `minio`, `pgvector`, a bounded PDF reader, and a PostgreSQL AST parser are added only with their feature slice.

Explicitly remove or prohibit Mercado Pago, `paho-mqtt`, EMQX/MQTT clients, QR/payment libraries used only by DVEM, social-login packages, device/telemetry packages, map/location integrations, tax/invitation modules, production sentry/cloud CLI coupling, certificate loaders, and DVEM migration/seed packages. Generic cryptography libraries may remain only for target password/session/token hashing and must have a target importer.

### Authenticated frontend

Retain only the Vite/React/TypeScript, Router, TanStack Query/Table, React Hook Form/Zod, required shadcn/Radix components, Tailwind v4, Lucide, Sonner, Vitest/Testing Library, and lint dependencies used by target code. Remove JWT decode, Google/Leaflet map packages and types, payment/device/tax/invitation dependencies, production analytics, spreadsheet/PDF export libraries, charting, and unused state libraries. No package survives merely because it existed upstream.

### Landing

Retain Astro, sitemap, Tailwind, TypeScript, and Vitest. Remove Google Maps, React integration when no island remains, analytics/tracker packages or inline scripts, production routing integrations, WhatsApp-specific helpers, and generated-output dependencies.

### Repository-wide exclusion checks

Each affected slice runs bounded searches over product package manifests, imports, routes, environment key names, migrations, and user-visible flow names for: `dvem`, Mercado Pago/payment, MQTT/EMQX, devices/telemetry, maps/location providers, tax, invitations, certificates/keys, production data/seeds, analytics trackers, and production migration identifiers. A match must be removed unless it is necessary product-facing documentation. Secret values are never printed. Excluded source files are not copied into temporary target locations.

## 6. Persistence and security architecture (unchanged)

### 6.1 Identity, tenancy, and sessions

Global users are separate from tenant memberships. Registration atomically creates a user, tenant, membership, seeded `admin`/`member`/`viewer` roles and permissions, and the administrator assignment. Administrators directly attach an existing user or create a `password_setup_required` user whose setup uses standard recovery. There is no invitation table, token, state, route, or UI.

Authentication uses a random opaque session cookie backed by a hashed database token. Mutations require origin validation and a session-bound CSRF token. `X-Tenant-ID` is only a selection hint. The backend authenticates the session, sets transaction-local `app.user_id`, verifies active membership, and only then sets transaction-local `app.tenant_id`. Missing or inconsistent context matches no tenant rows.

### 6.2 Generic schema and RLS

The fresh generic schema includes users, sessions, recovery state, tenants, memberships, roles/permissions, experiments, append-only results, typed append-only metrics, assets, ingestion runs, chunks, embeddings, conversations/messages, assistant runs/citations, and bounded append-only audit events.

Every tenant-owned relational/vector row has non-null `tenant_id`, tenant-aware constraints, RLS `USING` and `WITH CHECK`, and `FORCE ROW LEVEL SECURITY`. Runtime roles do not have `BYPASSRLS`. Child relationships use tenant-aware foreign keys where practical. Results/metrics/audit additionally revoke mutation and use triggers. RLS isolates rows; backend permission checks authorize actions. Both must pass.

Database roles remain separated:

- `project_owner`: non-login owner, never used by requests;
- `project_migrator`: controlled local migrations only;
- `app_runtime`: minimum application CRUD, no schema creation or role switching;
- `assistant_view_owner`: owns curated security-barrier views and remains subject to forced RLS;
- `assistant_reader`: separate pool, SELECT only on curated views;
- optional test-only `security_probe`: hostile least-privilege checks.

### 6.3 Experiments, assets, and ingestion

Experiments follow `draft -> running -> completed` or `failed`. Results and typed number/text/boolean/JSON metrics are append-only and retain creator/time provenance.

Assets use opaque backend-generated keys and one private MinIO bucket. Upload, download, delete, and short-lived GET-only presign require an `AuthorizedAsset` created after RLS visibility and permission checks. The default upload hard limit is configurable at 25 MiB.

Ingestion runs are append-only with pending/processing/ready/failed states. Text-native PDF/TXT/MD/CSV/JSON extraction is supported; PNG/JPEG and opaque artifacts remain downloadable without OCR. Re-ingestion creates new chunks/embeddings and activates them atomically only after success, preserving the object and audit history.

### 6.4 RAG, Text-to-SQL, and providers

RAG executes under trusted tenant context and `assistant:read`, with RLS plus explicit authorized-resource filtering before any chunks reach a provider. Citations are built from server-authorized records; a cross-tenant best vector match cannot reach context or output.

Text-to-SQL uses a PostgreSQL AST parser and accepts exactly one `SELECT` or `WITH ... SELECT` over schema-qualified, allow-listed security-barrier views for experiments, results, metrics, assets, and ingestion status. It rejects direct/system/unqualified relations, DDL/DML, data-changing CTEs, context mutation, locks, commands, unsafe functions, and multiple statements. The separate `assistant_reader` transaction is read-only, receives backend-set tenant context, defaults to a two-second timeout, wraps results with `LIMIT 201`, returns at most 200 rows and 256 KiB, and records bounded provenance. There is no privileged or unvalidated fallback.

Assistant modes remain document, relational, combined, and auto. Auto chooses only from a fixed tool enum; the backend authorizes every tool. Combined partial results use only independently successful authorized paths. External embedding/generation endpoints are disabled until explicitly opted in and receive minimum authorized context.

Recovery requests always return the same generic 202 shape. Tokens are random, stored only as keyed hashes, one-use, default 30 minutes, throttled by normalized-email fingerprint and source, and invalidate prior tokens/sessions on confirmation. Audit excludes passwords, cookies, tokens, credentials, raw objects, vectors, and full prompts.

## 7. Fresh generic migrations while reusing Alembic patterns

The target reuses Alembic infrastructure and migration discipline, not DVEM history or data.

1. Extend the existing Compose and `.env.example` with distinct bootstrap/migrator/runtime/assistant credentials; do not mount or rename restored DVEM volumes.
2. Adapt `alembic.ini` and `env.py` patterns into `backend`, loading only target metadata and a migrator URL. Preserve offline/online support, `NullPool`, and type/default comparison.
3. Create a fresh generic baseline revision owned by this project. It enables pgvector, revokes public schema creation, creates roles/schemas/tables/constraints, forces RLS, creates policies/helpers/triggers, seeds only the permission catalog, and creates curated assistant views/grants.
4. Never import, copy, stamp, squash, or chain `material_desarrollo/backend/alembic/versions/*`. Existing DVEM PostgreSQL and MinIO volumes/data are incompatible and are not migrated.
5. After the baseline, each feature slice adds a normal forward Alembic revision only for its target-owned change. Downgrade is allowed only while no irreversible local user data exists; otherwise local teaching recovery is reset/reseed.
6. Verify migration from an empty named project volume, runtime inability to migrate, no `BYPASSRLS`, missing-context denial, and fresh rebuild. Any process note that SQL/RLS ideas were referenced from course/source material belongs only in OpenSpec/Engram.

## 8. Product-tree and process-traceability boundary

`clase_08/proyecto` contains only:

- product runtime code and configuration;
- development tooling required to build, run, reset, migrate, lint, or test the product;
- product and security tests;
- product-facing documentation for local use, architecture, security assumptions, provider setup, reset, and non-production limitations.

Process traceability is exclusive to OpenSpec and Engram. The product tree MUST NOT contain adaptation directories, adaptation documents, source inventories, source checksums, source-digest tooling, source-integrity commands, or per-slice process records. The operational rule remains that `material_desarrollo/**` is read-only, but that rule is enforced through implementation discipline and recorded only in OpenSpec/Engram. Product tests and scripts verify product behavior and security, not the provenance or digest of the restored sources.

## 9. Incremental migration sequence and stacked slices

Each item is one or more stacked-to-main slices of at most 600 changed lines. Split by coherent invariant, never by arbitrary file count. Each slice starts from its predecessor and leaves existing services runnable or intentionally gated.

1. **Recovery reconciliation and root normalization:** correct README destructive wording only where needed for product-facing accuracy. Atomically relocate the six application placeholders from `apps/{landing,web}` and `services/api` to `landing`, `frontend`, and `backend`; update only Compose build contexts; verify unchanged behavior and all health contracts; remove only the vacated empty wrappers. Failed pre-commit validation aborts the transaction; after acceptance, all recovery stays within the canonical roots.
2. **Backend bootstrap adaptation:** adapt the product dependency manifest, `backend/Dockerfile`, Settings, application factory, and `/health`. Replace `backend/app/main.py` only because the standard-library placeholder cannot host the required FastAPI contracts. Do not add tenant routes.
3. **Database and Alembic foundation:** incrementally amend Compose/env; adapt Alembic infrastructure; add fresh generic roles/baseline/context helpers, forced RLS, and negative SQL fixtures. Runtime cannot migrate or bypass RLS.
4. **Identity/security foundation:** adapt password/auth test patterns into opaque sessions, CSRF, recovery, generic SMTP, users/tenants/memberships/roles. Registration is atomic; no invitations. Expose routes only with role/context evidence.
5. **Pagination and experiment domain:** adapt bounded pagination, then add experiment lifecycle, append-only results, typed metrics, provenance, role tests, and RLS denial.
6. **Private assets and ingestion:** add `AuthorizedAsset`/MinIO seam, 25 MiB stream limits, ingestion attempts, supported extractors, retry, and object-isolation evidence.
7. **pgvector and RAG:** add fresh vector schema/index, provider adapters, chunk activation, tenant-filtered retrieval, best-match contamination tests, and citations from authorized rows.
8. **Curated views and guarded Text-to-SQL:** add assistant roles/pool, security-barrier views, AST guard, bounded execution/provenance, hostile SQL tests, then combined/auto orchestration.
9. **Authenticated frontend foundation:** adapt `frontend` Vite package/config, `components.json`, providers, typed cookie/CSRF client, router, auth/recovery, and tenant switch. Preserve `frontend/index.html` as the Vite entry; adapt `frontend/Dockerfile` only after the build passes.
10. **Authenticated feature surfaces:** adapt shadcn components individually and generic table/form patterns for members, experiments, assets/ingestion, and assistant citations/SQL provenance. Viewer UI is read-only, but backend authorization remains authoritative.
11. **Astro landing:** add Astro sources beside `landing/index.html`, adapt layout/SEO/contact tests without analytics/maps/brand, switch `landing/Dockerfile` after the build passes, then remove the obsolete static placeholder.
12. **End-to-end closeout:** complete Compose health, Mailpit recovery, role, RLS, pool, vector, object, SQL-guard, frontend boundary, exclusion, and dependency evidence; finalize product-facing instructional documentation.

No tenant-owned HTTP route is introduced before trusted transaction context, RLS, and permission evidence exist. No assistant route is introduced before its data path has negative isolation evidence. Landing and web links share one public URL configuration contract.

## 10. Verification contract

Executable product evidence remains required despite the lack of a pre-existing project-wide runner:

- `backend/tests/{unit,integration}/**` for health, settings allow-list, opaque sessions, CSRF, generic recovery parity/expiry/reuse/races, roles, pagination, append-only records, ingestion retry, and provider unavailable/partial results;
- direct PostgreSQL checks for cross-tenant read/write denial, missing/forged context, unchanged victim state, forced RLS, role grants, and pooled-context reuse;
- vector tests where the best semantic match belongs to another tenant and never reaches provider context/citations;
- MinIO tests for anonymous denial and guessed asset/key download/delete/presign denial;
- SQL guard tests for multiple statements, DML/DDL, data-changing CTEs, context mutation, system/direct/unqualified relations, unsafe functions, timeout, row, and byte bounds;
- `frontend/src/**/*.test.tsx` and `frontend/tests/**` for public/auth boundaries, viewer controls, cookie/CSRF use, tenant-cache invalidation, semantic shadcn forms/tables, and distinguishable citations versus SQL provenance;
- `landing/tests/**` plus the landing build for canonical metadata, public-only links, contact bounds/honeypot/fallback, accessibility, and absence of tenant requests/analytics/map credentials;
- dependency and product-content scans for every excluded DVEM category;
- final `docker compose config`, clean-volume migration/startup, health checks, and an end-to-end two-tenant journey.

Security scripts exit non-zero on unexpected visibility, mutation, provider-context contamination, public object access, or context leakage. They print compact status only and never print secrets, raw recovery tokens, object bytes, or full prompts.

## 11. Rollout, rollback, and risk control

Delivery uses stacked-to-main slices with a 600 changed-line target. Security foundations precede dependent routes, and an invariant is not split so an intermediate branch exposes an unprotected operation.

Rollback is target-only:

- if root-normalization validation fails before commit, abort the entire move/context transaction and leave the current target untouched;
- after root normalization is accepted, restore prior product behavior only within `backend`, `frontend`, and `landing`; never revive `apps/*` or `services/api` as an operational layout;
- for later slices, revert the affected stacked slice under the canonical roots;
- do not modify the three restored source roots during implementation or rollback;
- for schema/object reset, stop Compose and remove only the named generic-project local volumes after explicit confirmation;
- never restore DVEM secrets, certificates, data, migrations, or integrations into the target;
- no generic-to-DVEM data downgrade or compatibility path exists.

| Risk | Control |
| --- | --- |
| Another destructive recovery | Atomic root normalization, one writer per slice, health validation, and no wholesale target operation. |
| Restored source mutation | Treat all `material_desarrollo/**` paths as read-only; keep this operational rule only in OpenSpec/Engram. |
| Process artifacts pollute the student project | Restrict `clase_08/proyecto` to product runtime, development, tests, and product-facing documentation. |
| DVEM dependency or behavior leaks in | Path-level evaluation, dependency importer evidence, forbidden-category scans, and explicit exclusion gates. |
| Useful infrastructure is needlessly rewritten | Source-to-target mapping and adapter seams require compatibility evaluation before exclusion or replacement. |
| Source auth/DB patterns weaken isolation | Opaque target sessions, transaction-local verified tenant context, forced RLS, no bypass/session context, and negative pool tests. |
| Frontend reuse becomes a security boundary | Backend capabilities are presentation hints only; every operation is re-authorized. |
| RAG, SQL, or MinIO crosses tenant boundaries | RLS, least privilege, authorized capabilities, curated views/AST guard, and hostile executable evidence. |
| Slice budget fragments an invariant | Split only at gated dependency seams; do not expose routes until the whole boundary and negative test fit a branch. |

## 12. Task rewrite constraints

Downstream tasks MUST describe **selective adaptation into the preserved skeleton**, not cleanup or replacement. Every task that uses restored material must name in OpenSpec/Engram:

1. exact source path(s) to evaluate;
2. exact target path(s) to retain/add/adapt;
3. classification and adapter seam;
4. excluded behavior and dependencies;
5. executable product acceptance evidence;
6. stacked predecessor, rollback, and estimated changed lines at or below 600.

Tasks MUST NOT create process-traceability files in `clase_08/proyecto`. They MUST NOT contain “delete the target,” “remove current source tree,” “copy backend/frontend/landing,” “replace project,” or equivalent destructive instructions. Except for the explicitly bounded recovery-input side of the first relocation task, no target, test, migration, build, or configuration path may use `apps/*` or `services/api`. Every implementation target remains under `backend`, `frontend`, or `landing`, with container wiring in root `compose.yaml`. The first rewritten task starts from the current 11-file skeleton and normalizes the placeholder paths atomically; it does not replay the prior cleanup slice.
