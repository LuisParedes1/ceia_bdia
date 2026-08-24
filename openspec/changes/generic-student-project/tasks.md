# Three-Day MVP Tasks: Generic Student Project

This replanning supersedes the longer production-oriented sequence. It targets a runnable educational demo in three days, reuses compatible restored patterns selectively, and never modifies `material_desarrollo/{backend,frontend,landing}` or adds process bookkeeping under `clase_08/proyecto`.

## Review Workload Forecast

| Field | Value |
| ------- | ------- |
| Estimated changed lines | 3,600–5,000 total; 300–600 per chained slice |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Day 1: PR 1 → PR 2 → PR 3; Day 2: PR 4 → PR 5; Day 3: PR 6 → PR 7 → PR 8 |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

## Global guardrails

- [x] Keep all implementation under `clase_08/proyecto/backend`, `frontend`, `landing`, and required root infrastructure; preserve canonical roots and selectively adapt source patterns with source/target/classification/rationale recorded in OpenSpec/Engram. <!-- sdd-owner: implementation -->
- [x] Exclude invitations, OAuth/social, OCR, queues/workers, custom roles, streaming, advanced history/dashboards, production deploy/HA/observability, DVEM compatibility, multiple providers, and non-trivial PNG/JPEG/CSV/JSON ingestion; never copy source trees wholesale or modify `material_desarrollo/**`. <!-- sdd-owner: implementation -->

## Day 1 — backend, security, and minimal shell

### PR 1 — Backend runnable foundation (300–500 lines)

Predecessor: completed cleanup and root normalization. Rollback: backend foundation files only. Finish: FastAPI health/config/dependencies starts in Compose.

- [x] Adapt `material_desarrollo/backend/app/main.py`, `core/config.py`, dependency files, and Alembic bootstrap into `clase_08/proyecto/backend/{app/main.py,app/core/config.py,requirements.txt,Dockerfile,alembic.ini,migrations/env.py}`; retain FastAPI/lifespan/health patterns, exclude DVEM/MQTT/payments/certs, and verify `docker compose config` plus backend startup. <!-- sdd-owner: implementation -->

### PR 2 — PostgreSQL, pgvector, RLS, and trusted context (450–600 lines)

Predecessor: PR 1. Rollback: DB migrations/context/scripts. Finish: clean-volume migration and negative isolation probes pass.

- [x] Adapt `material_desarrollo/backend/app/core/db.py` into `backend/app/core/database.py` and `transactions.py`; add fresh generic roles, users/tenants/memberships/roles, experiment/result/metric/document/chunk/vector tables, transaction-local verified context, forced RLS, and `scripts/verify-rls.sql`/pool probes; verify no BYPASSRLS, forged context denial, pooled-context containment, and two-tenant isolation. <!-- sdd-owner: implementation -->

### PR 3 — Identity, recovery, roles, and frontend auth shell (450–600 lines)

Predecessor: PR 2. Rollback: identity routes/security and minimal frontend auth files. Finish: register/login/recovery works through Mailpit and shell protects authenticated routes.

- [x] Adapt source auth/email patterns into `backend/app/api/auth.py`, `tenants.py`, `members.py`, `security/{password,sessions,recovery}.py`, and `providers/mail.py`; implement opaque sessions, CSRF, generic one-use 30-minute recovery, direct admin/member/viewer management without invitations, and verify permission denial. <!-- sdd-owner: implementation -->
- Verification correction evidence: recovery rate limit/202 parity, fixed role and permission seeding, recovery-only member password setup, and authenticated viewer admin denial are recorded in `apply-progress.md`; local no-stack proof is 8 pass / 1 skip, while isolated Compose HTTP proof is separate. <!-- sdd-owner: implementation -->
- [x] MVP tenant membership is one active tenant per user: login atomically resolves that tenant into the opaque session, tenant selection is absent, and existing users attached elsewhere cannot be attached by an admin. Session responses expose the assigned role and at most 20 capabilities. <!-- sdd-owner: implementation -->
- [x] Adapt `material_desarrollo/frontend/{package.json,components.json,src/FrontendApp.tsx,src/router/app.router.tsx,src/auth/**}` into `frontend/src/app/**` and `features/auth/**`; retain Vite/React/shadcn patterns, use cookie/CSRF API access, and verify lint/typecheck/build when available. <!-- sdd-owner: implementation -->

## Day 2 — experiments, storage, ingestion, and RAG

### PR 4 — Experiments, results, and typed metrics (350–550 lines)

Predecessor: PR 3. Rollback: experiment domain/routes/tests. Finish: member mutation and viewer read-only behavior are executable.

- [x] Adapt pagination from `material_desarrollo/backend/app/services/pagination.py` and add target-owned experiment lifecycle, append-only results, typed metrics, provenance, repositories/services/schemas/routes under `backend/app/{domain,repositories,services,api}`; verify role matrix, lifecycle, tenant FKs, immutability, and cross-tenant denial. <!-- sdd-owner: implementation -->

### PR 5 — MinIO plus PDF/TXT/MD ingestion and vector RAG (500–600 lines)

Predecessor: PR 4. Rollback: storage/ingestion/vector/assistant retrieval files and local volumes. Finish: authorized document upload, extraction, embedding, retrieval, and citation work for the demo.

- [x] Adapt compatible generic upload/storage patterns into `backend/app/storage/`, `infra/minio/init.sh`, and asset APIs with opaque tenant keys, private bucket, authorization, and bounded uploads; support only PDF/TXT/MD for ingestion (PNG/JPEG/CSV/JSON remain deferred unless already trivial), and verify guessed-key denial and original-object preservation. <!-- sdd-owner: implementation -->
- [x] Add bounded extractors, chunk activation, fixed-dimension `EmbeddingProvider`, pgvector persistence, and tenant-filtered retrieval under `backend/app/{ingestion,providers,assistant}`; use one configured/local provider seam, fail closed when unavailable, and verify colliding cross-tenant vector matches never reach provider context. <!-- sdd-owner: implementation -->

## Day 3 — assistant, screens, fixtures, and proof

### PR 6 — Guarded read-only Text-to-SQL and assistant orchestration (500–600 lines)

Predecessor: PR 5. Rollback: assistant SQL/orchestration files and migration revision. Finish: document/relational/combined assistant responses are bounded and authorized.

- [ ] Add security-barrier curated views, least-privilege assistant reader role/pool, and `SqlGuard`/`SqlExecutor` under `backend/migrations/versions/` and `backend/app/assistant/`; accept one bounded allow-listed read-only SELECT, reject writes/DDL/context mutation/direct tables, enforce timeout/200-row/256KiB limits, and verify hostile SQL tests before data access. <!-- sdd-owner: implementation -->
- [ ] Implement `backend/app/api/assistant.py` document/relational/combined/auto modes with citations and SQL provenance; reuse only compatible source seams, never model-controlled tenant selection, and verify unavailable/partial results and cross-tenant denial. <!-- sdd-owner: implementation -->

### PR 7 — Minimal authenticated screens and generic Astro landing (450–600 lines)

Predecessor: PR 6. Rollback: frontend feature and landing files. Finish: demo screens cover auth, tenant/members, experiments, documents, assistant, and public landing.

- [ ] Reuse individual compatible shadcn components and table/form patterns from `material_desarrollo/frontend/src/components/ui/*` and data-table sources into `frontend/src/features/**`; keep screens minimal, accessible, viewer read-only, and backend-authorized, verifying lint/typecheck/build or bounded manual checks. <!-- sdd-owner: implementation -->
- [x] Adapt Astro layout/SEO/home/contact patterns from `material_desarrollo/landing/{package.json,src/layouts,src/seo,src/components}` into `landing/`; remove analytics/maps/WhatsApp/DVEM copy, keep public-only links, switch Docker build only after Astro build passes, then remove obsolete `landing/index.html` with rationale. <!-- sdd-owner: implementation -->
- [x] Correct the public/auth presentation with evidence-based experiment, document, assistant, RAG, and read-only Text-to-SQL language; add persisted system-aware light/dark themes and accessible toggles without claiming deferred capabilities are implemented. <!-- sdd-owner: implementation -->

### PR 8 — Two-tenant fixtures, e2e proof, and demo docs (400–600 lines)

Predecessor: PR 7. Rollback: fixtures/scripts/docs only. Finish: one command demonstrates the complete two-tenant journey and isolation.

- [ ] Add `clase_08/proyecto/scripts/seed-security-fixtures.py`, `verify-stack.sh`, `reset-local.sh`, and focused Compose/SQL/API checks; seed two tenants with admin/member/viewer, experiments, documents/chunks, and prove relational, vector, MinIO, SQL, role, and pooled-context isolation without secrets or raw tokens. <!-- sdd-owner: implementation -->
- [ ] Update `clase_08/proyecto/README.md` with the three-day demo path, architecture/trust boundaries, provider setup, reset and verification commands, selective reuse notes, known limitations, and explicit deferred capabilities; do not add process traceability files. <!-- sdd-owner: implementation -->

## Parent lifecycle actions

- [ ] Start or reuse one bounded review per stacked slice and reconcile lifecycle evidence before branch, commit, PR, or delivery action. <!-- sdd-owner: parent -->
- [ ] After each slice passes its focused verification, authorize the next auto-chain slice; keep every slice at or below 600 authored changed lines. <!-- sdd-owner: parent -->

## Frontend confirmation and password UX correction — ordinary unmanaged

- [x] Add target-owned Radix AlertDialog primitives, controlled reusable `ConfirmDialog` and `PasswordInput`; use the dialog for authenticated sign-out and use visible/hidden password inputs with frontend-only confirmation validation in registration and recovery confirmation. API calls retain their existing payload arity. <!-- sdd-owner: implementation -->

## Identity email validation and workspace-name correction — ordinary unmanaged

- [x] Validate every identity/member email payload with Pydantic `EmailStr` backed by pinned `email-validator`; retain normalized lowercase query/insert use, reject malformed payloads before route side effects, and preserve recovery's uniform `202` for syntactically valid unknown addresses. Return trusted session `tenant_name` alongside tenant ID, role, and capabilities; render the workspace name (not its UUID) and normalize FastAPI structured email validation errors into useful Spanish copy. <!-- sdd-owner: implementation -->

## Auth field-local validation — ordinary unmanaged

- [x] Validate every auth mode locally after first blur and on subsequent changes; render stable, accessible field-local errors, keep transport errors form-level, focus the first invalid submit control, and preserve existing auth payloads, redirects, theme, dialog, and password-visibility behavior. <!-- sdd-owner: implementation -->

## Exhaustive identity error localization — ordinary unmanaged

- [x] Localize all identity/recovery user-facing errors and recovery email copy; centralize backend 404/405/422/500 safe Spanish responses; normalize frontend status, validation, legacy, non-JSON, and network failures without exposing server English or Pydantic internals. <!-- sdd-owner: implementation -->

## Recovery-link route correction — ordinary unmanaged

- [x] Support `/reset-password?token=...` as the recovery-email route, autofill the opaque token from the query string, and retain the manual `/recovery/confirm` token-entry fallback. <!-- sdd-owner: implementation -->

## DVEM users-directory selective adaptation — ordinary unmanaged

- [x] Add Alembic revision `20260330_06`, an admin-only paginated tenant/RLS-safe `GET /api/members` endpoint, and the responsive DVEM-derived users directory with search, filters, sort, pagination, details, and create dialogs. <!-- sdd-owner: implementation -->

## Cross-computer continuation checkpoint

1. Run native status and reconcile its reported active attempt through native instructions before any new runtime apply; do not persist or reuse an opaque token.
2. PR 4: implement the experiments backend vertical slice.
3. Implement the real Experiments frontend using the DVEM table/form pattern.
4. PR 5: implement documents, MinIO, ingestion, and tenant-safe RAG.
5. PR 6: implement guarded Text-to-SQL and assistant orchestration.
6. PR 7: implement the remaining authenticated screens.
7. PR 8: add fixtures, scripts, documentation, and final verification.
