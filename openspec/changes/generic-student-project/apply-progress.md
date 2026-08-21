# Apply Progress: Generic Student Project

## Reconstructed cumulative ledger after accidental truncation

This artifact was reconstructed after an accidental truncation replaced the historical cumulative ledger with the visual-correction record below. It records completed milestones supported by `tasks.md` and the current target tree; it does not claim dates, commits, PRs, review receipts, or delivery approval. Delivery remains `disabled/unmanaged`.

## Completed foundation and security milestones

### 1. Target-only runnable foundation

- Established the target-owned backend, frontend, landing, and Compose foundation under `clase_08/proyecto/`.
- Reused compatible patterns selectively from `material_desarrollo` without modifying its backend, frontend, or landing source trees.

### 2. PostgreSQL, trusted context, and tenant isolation

- Added PostgreSQL bootstrap roles and the MVP schema for users, tenants, memberships, roles, experiments, results, metrics, documents, chunks, and vectors.
- Added transaction-local verified context, forced RLS, and tenant-isolation and pooled-context probes.
- Task evidence records the intended negative coverage: no `BYPASSRLS`, forged-context denial, pooled-context containment, and two-tenant isolation.

### 3. Identity, recovery, and fixed roles

- Implemented opaque identity sessions with CSRF protection plus registration, login, and logout.
- Added Mailpit-backed account recovery with uniform `202` responses and rate limiting.
- Seeded fixed `admin`, `member`, and `viewer` roles; an administrator creates users without choosing their passwords, and users complete password setup through recovery.
- Task evidence records recovery rate-limit/`202` parity, fixed role and permission seeding, recovery-only member password setup, and authenticated viewer admin denial. The recorded local no-stack proof is 8 pass / 1 skip; isolated Compose HTTP proof is separate.

### 4. One-active-membership session model

- Added migration 05 for one active tenant membership per user.
- Login atomically resolves that tenant into the opaque session; tenant selection was removed.
- Session responses expose the assigned role and at most 20 capabilities; administrators cannot attach an existing user from another tenant.

### 5. React application shell and protected routes

- Added the Vite/React foundation with cookie/CSRF API access, protected routes, and a responsive authenticated shell.
- Implemented auth and user-management screens plus experiment, document, and assistant navigation placeholders for later slices.
- Configured Nginx SPA deep-link fallback.

### 6. Astro public landing

- Added the generic Astro landing foundation using selectively adapted layout, SEO, home, and contact patterns.

### 7. Configurable Compose URLs and ports

- Made Compose host ports configurable for the landing, web, API, PostgreSQL, MinIO, and Mailpit services.

## Error localization correction — ordinary unmanaged

- Localized every identity route detail and recovery response/email in professional Spanish, including invalid credentials, CSRF, membership, role, recovery-token, and cross-workspace cases.
- Added centralized FastAPI handling: `422` returns `{"detail": [{"loc", "type", "msg"}]}` without Pydantic input/context/raw-English leakage; framework/default HTTP errors use trusted status-specific Spanish details while preserving status and headers; unhandled errors are logged server-side and return a safe `500` detail.
- Moved CORS to the outer middleware position so handled inner responses can retain allowed-origin headers where Starlette permits.
- Hardened the frontend API boundary: it never uses `response.statusText`; it has Spanish status fallbacks, normalizes validation issues by location/type, accepts known Spanish backend details, defensively maps legacy English auth details, and preserves the Spanish network failure.
- RED: frontend API contracts failed for all status fallbacks, non-JSON statusText exposure, legacy `invalid credentials`, raw Pydantic English, and missing terminal punctuation. Backend source guard failed for untranslated identity literals; runtime HTTP-boundary RED could not run because the checked-in backend environment lacks `httpx`.
- GREEN: focused frontend API suite passed 15 tests. Backend focused suite passed 10 tests using the checked-in virtual environment. Full backend suite passed 16 tests with 4 configured integration skips; full frontend suite passed 43 tests. Frontend typecheck, lint, and production audit passed.
- `compileall`, Pyright, and frontend build were not run inside that delegated work unit: those validations are parent-owned below. Delivery remains `disabled/unmanaged`.

## Recovered post-foundation UI and identity milestones

This append-only recovery supplements the cumulative reconstruction above from current source, tests, `tasks.md`, and persisted Engram evidence. It does not invent commit, PR, receipt, or delivery state.

- Corrected post-registration session races so stale anonymous refreshes cannot overwrite a newly authenticated session.
- Added persistent accessible themes to the landing and authenticated frontend, and verified runtime theme interaction.
- Added configurable host ports and cross-service public URLs; documented the clean-start and migration workflow in Spanish.
- Added a reusable accessible confirmation dialog integrated into sign-out, plus independent password visibility controls and frontend-only password confirmation.
- Added robust email validation and trusted `tenant_name` session presentation instead of exposing the tenant UUID.
- Added field-local auth validation: first blur reveals the error directly below its control, touched fields revalidate on change, and invalid submission focuses the first field.
- Added `/reset-password?token=...` as the Mailpit recovery-link route; the opaque token is consumed from the query string and the manual `/recovery/confirm` fallback remains available.

## Parent validation of localization correction

- Parent verification passed: backend 16 tests with 4 configured integration skips, compileall, and Pyright with zero diagnostics; frontend 47 tests, typecheck, lint, production build, and audit with zero vulnerabilities.
- API and web images were rebuilt and are healthy. Runtime probes confirmed Spanish+CORS responses for nonexistent login (`401`), invalid email (`422`), framework missing route (`404`), and login preflight (`200`); no persistent user was created.

## DVEM users-directory selective adaptation

- Added Alembic revision `20260330_06` and an admin-only, tenant-context-bound `GET /api/members` contract with pagination, email search, allowlisted role/status filters, deterministic sorting, and FORCE-RLS tenant isolation.
- Adapted DVEM's users page, toolbar, responsive table/cards, badges, loading/empty/error states, details dialog, and pagination into the target. Domain-only identity fields, invitations, OAuth, clients, exports, edit/delete, and tenant selection remain excluded.
- Preserved direct member creation as an accessible capability-gated dialog; creation refreshes the directory and explains recovery-based password setup.
- Backend focused tests passed, Pyright reported zero diagnostics, HTTP identity/list tests passed, and dedicated pooled-context RLS probes passed. Frontend passed 49 tests, typecheck, lint, production build, and audit with zero vulnerabilities.
- API/web images are healthy at Alembic `20260330_06 (head)` and the served bundle contains the users-directory states and actions. Delivery remains `disabled/unmanaged`.

## Cross-computer continuation checkpoint

### State and evidence

- Native status for `generic-student-project` reports the OpenSpec artifact store; proposal, spec, design, tasks, and apply progress are complete, while the verify report is missing. Before this update, task progress was 23 total, 11 completed, and 12 pending; `apply` was ready, verify/archive were blocked, and the next recommendation was `apply`.
- Native status also reports an active SDD attempt. The next machine must run `gentle-ai sdd-status generic-student-project --cwd <repo> --json --instructions` and reconcile the reported active attempt using native instructions before a new runtime apply. No opaque token or attempt counters are persisted here.
- Completed evidence: Day 1 foundation/security/auth shell; themes and Spanish localization; blur-local auth validation; password confirmation/visibility; logout confirmation; `tenant_name`; and `/reset-password?token=...` with manual recovery fallback.
- DVEM users-directory evidence: migration `20260330_06`; admin-only paginated `GET /api/members`; tenant/RLS isolation; responsive table/cards; search/filter/sort/pagination; details/create dialogs.
- Last known validation: backend focused/unit tests, HTTP identity/list tests, and two pooled-context RLS tests passed; Pyright had zero diagnostics. Frontend had 49 passing tests plus typecheck, lint, build, and audit with zero vulnerabilities. Landing had 6 passing tests plus Astro check, build, and audit. API/web images were healthy.
- Local runtime state is non-portable: all services were healthy, Alembic was `20260330_06 (head)`, and 11 local users existed. A new machine must recreate `.env`, volumes, migrations, and data.

### Next work order

1. Reconcile native status and its active attempt through native instructions.
2. PR 4: experiments backend vertical slice.
3. Real Experiments frontend using the DVEM table/form pattern.
4. PR 5: documents, MinIO, ingestion, and tenant-safe RAG.
5. PR 6: Text-to-SQL and assistant orchestration.
6. PR 7: remaining screens.
7. PR 8: fixtures, scripts, documentation, and final verification.

### Transfer constraint

`clase_08/proyecto/` and `openspec/changes/generic-student-project/` are untracked. No commits, branches, or PRs exist. These files will not transfer through Git unless the user explicitly commits/pushes them or copies/synchronizes the working tree. Delivery remains `disabled/unmanaged`.
