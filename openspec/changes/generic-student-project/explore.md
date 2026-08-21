# Exploration: Generic Student Project (recovered-source correction)

## Executive finding

The authoritative source recovery changes the implementation plan: **`clase_08/proyecto` is the transformation target; `material_desarrollo/backend`, `material_desarrollo/frontend`, and `material_desarrollo/landing` are immutable, read-only reuse sources.** Reuse must be selective. Do not copy the restored projects wholesale, delete the target wholesale, or modify the restored source. The prior cleanup/replacement incident must not be repeated.

The confirmed product remains a local, multi-tenant educational application with separate public landing and authenticated web frontends, FastAPI API, PostgreSQL/pgvector, MinIO, generic SMTP recovery, experiments/results/metrics, documents/ingestion, and tenant-safe RAG plus read-only Text-to-SQL. Invitations, DVEM payments/MQTT/devices/maps/tax/invitations/secrets/certs/production migrations/data are excluded. Delivery remains auto-chain with a 600-line review budget.

## Inputs and inspection boundaries

Inspected `openspec/config.yaml`, current proposal/design/tasks, the target skeleton, and restored source manifests/configuration/patterns. Inspection excludes `node_modules`, `dist`, caches, certificates, `.env` values, generated output, and production data. No implementation source was edited.

The target currently has a generic Compose skeleton, placeholder landing/web/API structure, `.env.example` placeholders, Makefile, health checks, and local PostgreSQL/MinIO/Mailpit wiring. Existing tasks mark the initial cleanup/skeleton slice complete; recovery guidance below supersedes any instruction to destructively clean or wholesale replace it.

## Reuse inventory

Legend: **retain** = use substantially as-is after path/config review; **adapt** = copy only the bounded pattern and rewrite domain/security; **reference** = consult as evidence, do not import; **discard** = never bring into the target.

### Backend (`material_desarrollo/backend`)

| Classification | Inventory and destination | Notes/dependencies |
| --- | --- | --- |
| Retain | FastAPI application bootstrap, Dockerfile/build conventions, requirements discipline, health/config shape -> `clase_08/proyecto/backend/` | Reconcile with target Compose and PostgreSQL/pgvector. Preserve generic startup/config/auth/recovery/email/pagination/test foundations where compatible. |
| Adapt | DB session/repository patterns, Alembic layout, password/session/recovery/mail adapters, generic error and pagination utilities -> `backend/app/{core,repositories,security,providers}` | Must use trusted transaction-local tenant context, non-BYPASSRLS roles, generic SMTP, and target schema. Review every dependency for DVEM assumptions. |
| Adapt | Existing API/test fixtures and auth tests -> `backend/tests/` | Keep test shape and useful cases; rewrite fixtures to two tenants and role matrix; add negative RLS/vector/object/SQL checks. |
| Reference | Backend package/dependency inventory and integration seams | Use to avoid reinventing stable infrastructure, not as permission to copy the application. |
| Discard | Payment/Mercado Pago, MQTT/EMQX, device/telemetry, maps/location, tax, invitation, production integration, certificate and secret material | Also discard DVEM routes, entities, seeds, migrations, names, and production deployment assumptions. |

### Frontend (`material_desarrollo/frontend`)

| Classification | Inventory and destination | Notes/dependencies |
| --- | --- | --- |
| Retain | Vite + React + TypeScript shell, router/provider/auth patterns, API client conventions, shadcn components/config, tables/forms, tests -> `clase_08/proyecto/frontend/` | Existing manifest confirms React, React Router, TanStack Query/Table, Vitest, Tailwind v4, Radix shadcn conventions, Lucide, `@/` alias. Verify components before reuse. |
| Adapt | Auth screens, authenticated shell, pagination/table/form composition, query/cache behavior -> `frontend/src/{app,features,lib}` | Replace DVEM navigation and permissions with tenants/members/experiments/assets/assistant. Backend remains the security boundary; tenant switch invalidates cached queries. Follow shadcn semantic tokens, `FieldGroup`/`Field`, accessible dialog titles, grouped items, `gap-*`, `cn()`, and `data-icon`. |
| Reference | Existing visual/layout and test patterns | Preserve instructional accessibility and stable component composition, not product branding or domain copy. |
| Discard | DVEM branding/routes, payments, maps, device screens, tax/invitation flows, Google/Map credentials, production analytics/tracker configuration | Do not move public runtime credentials into the target. |

### Landing (`material_desarrollo/landing`)

| Classification | Inventory and destination | Notes/dependencies |
| --- | --- | --- |
| Retain | Astro layout, public page structure, SEO/meta/sitemap and contact/content patterns -> `clase_08/proyecto/landing/` | Keep public-only boundary and independent container. |
| Adapt | Auth entry links, copy, environment/public URL handling, Docker/build config -> `landing` | Landing may expose public API/login URLs only; it must not fetch tenant data or contain infrastructure credentials. |
| Reference | SEO/accessibility/contact implementation patterns | Re-author product copy for the generic student application. |
| Discard | DVEM brand/domain, Traefik production routing, map/API keys, generated sitemap/output, analytics and production security headers tied to old deployment | Use local Compose defaults and placeholders only. |

### Migrations, tests, and utilities

| Classification | Inventory and destination | Notes/dependencies |
| --- | --- | --- |
| Retain | Migration discipline, SQL verification style, Docker/health-check and local command conventions -> `backend/migrations`, `infra`, `scripts` | Fresh generic baseline is required; do not chain incompatible DVEM history. |
| Adapt | Existing auth/recovery/pagination/unit/integration test helpers and reset/verification utilities | Add executable proof for RLS, pooled context, vector retrieval, MinIO authorization, SQL guard, role matrix, and recovery parity. Tests must prove denial and unchanged victim state. |
| Reference | Course practices `clase_02`–`clase_07`, especially tenant/RLS/pgvector/RAG examples | Evidence source only; those instructional artifacts remain unchanged. |
| Discard | DVEM migrations, seed/production data, generated output, local `.env`, certs, payment/MQTT/device/map utilities, invitation utilities | Never expose or reproduce secret values. |

## Dependency and destination notes

1. **Preserve the target skeleton first.** Reconcile its existing `compose.yaml`, `.env.example`, Makefile, Dockerfiles, health checks, and placeholders rather than recreating them. Only replace a file when its contents are demonstrably incompatible, and record the reason.
2. **Backend foundation precedes tenant routes:** config/startup -> database roles/migrations/context/RLS -> identity/recovery/memberships -> experiments -> assets/ingestion -> pgvector/RAG -> curated views/SQL guard -> frontend feature surfaces -> end-to-end evidence.
3. Restored backend utilities depend on their original package layout and settings; adapt imports/configuration into `backend`, then remove only unused DVEM dependencies. Restored frontend code depends on its Vite alias, Tailwind v4 tokens, Radix/shadcn base, and installed packages; preserve those conventions in `frontend`.
4. Landing can be adapted independently, but its auth URLs must match the web container. Neither frontend may receive DB, MinIO, SMTP, model, or migration credentials.
5. The new migration baseline must own generic identity, tenancy, experiments, assets, ingestion, chunks/embeddings, assistant views, audit, and RLS. Existing DVEM volumes/data are incompatible and are not migrated.
6. Every implementation slice must remain reviewable under 600 changed lines and auto-chain boundaries must not expose an unprotected tenant route.

## Security and secret hazards

- Restored manifests/configuration contain DVEM-specific integrations and may reference credentials, public API keys, certificates, external hosts, or production routing. Do not print, copy, commit, or expose values; inspect names and structure only.
- `.env` files, certificates/keys, generated bundles, caches, and production data are not reuse inputs. `.env.example` may contain placeholders only.
- Browser-visible `PUBLIC_*` values are not secrets by default, but map/provider/analytics values are excluded with the related feature. Backend-only DB roles, MinIO, SMTP, recovery, and model credentials must never enter frontend source or bundles.
- RLS is defense in depth: backend-derived transaction-local user/tenant context, `FORCE ROW LEVEL SECURITY`, no runtime `BYPASSRLS`, tenant filtering for vectors, backend-authorized MinIO, and a separate read-only curated-view SQL role are mandatory.
- Never trust restored route payloads, JWT/header tenant selection, generated SQL, model output, object keys, or client permissions as authorization input.

## Recovery guidance for the current 11-file target skeleton

- Treat the current target as a preserved starting point, not an incident artifact to erase. Do not run the previous full cleanup, delete all target files, or copy an entire restored tree over it.
- Before each slice, snapshot/check the target paths and record only intentional replacements. Keep the existing local Compose service contract where compatible; amend services incrementally for PostgreSQL roles/migrations, MinIO initialization, and SMTP.
- Recover reusable code by file/class/function classification: retain generic infrastructure, adapt imports and domain contracts, reference patterns that need redesign, discard excluded integrations. Source remains read-only.
- Keep the initial skeleton's no-tenant-route invariant until context/RLS/permission evidence exists. If a target file is a placeholder, extend it in place or add the smallest destination module needed by the current dependency slice.
- If rollback is needed, revert only target implementation commits/changes or restore the target pre-slice snapshot; do not mutate restored source or use production/DVEM data. Use explicit project-volume reset commands only for new local volumes.
- Later proposal/spec/design/tasks must be read as product scope and security constraints, but any destructive cleanup language must be interpreted through this recovered-source inventory and corrected to selective reuse.

## Confirmed scope and unresolved decisions

The proposal/design defaults remain authoritative: self-registration creates a tenant/admin, direct administrator account attachment without invitations, append-only experiment results and typed metrics, bounded document formats/ingestion, private MinIO, tenant-safe RAG, curated read-only Text-to-SQL, generic recovery, and local Compose. Open decisions remain provider choice, exact experiment fields, ingestion/OCR/retention boundaries, assistant SQL views/limits, recovery throttling, and landing branding; none may weaken isolation or expand excluded DVEM behavior.

## Next planning implication

Update downstream planning language to say **selective adaptation from immutable restored sources into the existing target skeleton**. Split implementation into small auto-chain slices under 600 changed lines, with recovery/source preservation and negative security evidence explicit in each affected task. No source or target implementation changes are made by this exploration.
