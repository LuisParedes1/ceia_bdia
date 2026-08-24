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

## PR 4 — experiments backend vertical slice

### Structured status and boundary

- Consumed native dispatcher authority: `next_recommended=apply`, proposal/spec/design/tasks dependencies complete, apply ready, and verify/archive blocked.
- Action context was `repo-local` at `/home/martin/Code/ceia-bdia`; all edits stayed inside the supplied backend and OpenSpec allowlist.
- Delivery remained `auto-chain`, `stacked-to-main`; current boundary was only PR 4. No branch, commit, PR, receipt, review, frontend experiment work, or PR 5+ work was started.
- Review budget: 445 authored additions plus 7 deletions = **452 changed lines**, below the approved 600-line slice limit.

### Completed implementation task and persisted checkbox

- [x] Adapt pagination from `material_desarrollo/backend/app/services/pagination.py` and add target-owned experiment lifecycle, append-only results, typed metrics, provenance, repositories/services/schemas/routes under `backend/app/{domain,repositories,services,api}`; verify role matrix, lifecycle, tenant FKs, immutability, and cross-tenant denial. <!-- sdd-owner: implementation -->
- `tasks.md` was updated only for this PR 4 implementation row.

### Files changed

- Added `backend/app/services/pagination.py`, `domain/experiments.py`, `api/experiment_schemas.py`, `repositories/experiments.py`, `services/experiments.py`, and `api/experiments.py`.
- Added migration `backend/migrations/versions/20260330_07_experiments.py` and focused test `backend/tests/test_experiments.py`.
- Updated `backend/app/main.py`, `app/core/database.py`, and `tests/test_identity_http.py`.
- Pagination was selectively re-authored against the approved bounded contract because the referenced `material_desarrollo/backend/app/services/pagination.py` path was not present in this workspace; no `material_desarrollo/**` file was modified or copied.

### Verification evidence

| Command | Result |
| --- | --- |
| `cd clase_08/proyecto/backend && /tmp/generic-student-backend-venv/bin/python -m unittest tests/test_experiments.py -v` | PASS: 5 tests covering lifecycle, typed metrics, pagination, tenant-aware migration/immutability markers, and absence of historical mutation routes. |
| `cd clase_08/proyecto/backend && /tmp/generic-student-backend-venv/bin/python -m unittest discover -s tests -v` | PASS: 23 tests, 4 configured integration skips. |
| `cd clase_08/proyecto/backend && /tmp/generic-student-backend-venv/bin/python -m compileall -q app tests migrations` | PASS. |
| `cd clase_08/proyecto/backend && npx --yes pyright --pythonpath /tmp/generic-student-backend-venv/bin/python` | PASS: 0 errors, 0 warnings. |
| `cd clase_08/proyecto/backend && ... /tmp/generic-student-backend-venv/bin/alembic upgrade head --sql` | PASS: generated the complete PostgreSQL migration chain through `20260330_07`. |
| `cd clase_08/proyecto && docker compose --env-file .env.example config -q` | PASS. |
| `git diff --check -- clase_08/proyecto/backend` | PASS. |

Runtime harness: **N/A on this machine**. `docker compose ps -a` could not access `/var/run/docker.sock` (`permission denied`), so the executable HTTP role/cross-tenant lifecycle scenario added to `tests/test_identity_http.py` remained among the configured skips. This is an environment limitation, not a fallback approval; the focused policy/schema/migration suite and complete no-stack backend suite passed.

### Design deviations and rollback

- No product-scope deviation. The referenced restored pagination source path was unavailable, so the target-owned implementation follows the design's `PageRequest`/`Page` bounded seam without claiming source retention.
- Rollback boundary: remove migration `20260330_07`, the six new experiment/pagination modules and focused test, remove experiment router registration/metadata additions, and revert only the added HTTP experiment scenario. This does not affect identity, users directory, frontend, landing, or later slices.

### Remaining implementation tasks

- [ ] Adapt compatible generic upload/storage patterns into `backend/app/storage/`, `infra/minio/init.sh`, and asset APIs with opaque tenant keys, private bucket, authorization, and bounded uploads; support only PDF/TXT/MD for ingestion (PNG/JPEG/CSV/JSON remain deferred unless already trivial), and verify guessed-key denial and original-object preservation. <!-- sdd-owner: implementation -->
- [ ] Add bounded extractors, chunk activation, fixed-dimension `EmbeddingProvider`, pgvector persistence, and tenant-filtered retrieval under `backend/app/{ingestion,providers,assistant}`; use one configured/local provider seam, fail closed when unavailable, and verify colliding cross-tenant vector matches never reach provider context. <!-- sdd-owner: implementation -->
- [ ] Add security-barrier curated views, least-privilege assistant reader role/pool, and `SqlGuard`/`SqlExecutor` under `backend/migrations/versions/` and `backend/app/assistant/`; accept one bounded allow-listed read-only SELECT, reject writes/DDL/context mutation/direct tables, enforce timeout/200-row/256KiB limits, and verify hostile SQL tests before data access. <!-- sdd-owner: implementation -->
- [ ] Implement `backend/app/api/assistant.py` document/relational/combined/auto modes with citations and SQL provenance; reuse only compatible source seams, never model-controlled tenant selection, and verify unavailable/partial results and cross-tenant denial. <!-- sdd-owner: implementation -->
- [ ] Reuse individual compatible shadcn components and table/form patterns from `material_desarrollo/frontend/src/components/ui/*` and data-table sources into `frontend/src/features/**`; keep screens minimal, accessible, viewer read-only, and backend-authorized, verifying lint/typecheck/build or bounded manual checks. <!-- sdd-owner: implementation -->
- [ ] Add `clase_08/proyecto/scripts/seed-security-fixtures.py`, `verify-stack.sh`, `reset-local.sh`, and focused Compose/SQL/API checks; seed two tenants with admin/member/viewer, experiments, documents/chunks, and prove relational, vector, MinIO, SQL, role, and pooled-context isolation without secrets or raw tokens. <!-- sdd-owner: implementation -->
- [ ] Update `clase_08/proyecto/README.md` with the three-day demo path, architecture/trust boundaries, provider setup, reset and verification commands, selective reuse notes, known limitations, and explicit deferred capabilities; do not add process traceability files. <!-- sdd-owner: implementation -->

### Deferred parent lifecycle actions

- [ ] Start or reuse one bounded review per stacked slice and reconcile lifecycle evidence before branch, commit, PR, or delivery action. <!-- sdd-owner: parent -->
- [ ] After each slice passes its focused verification, authorize the next auto-chain slice; keep every slice at or below 600 authored changed lines. <!-- sdd-owner: parent -->

## PR 4 corrective runtime verification

### Boundary and runtime setup

- Consumed native status `next_recommended=apply`, `apply=ready`, with work unit `pr4-runtime-verification`; action context was repo-local with the supplied backend/OpenSpec edit roots.
- Used isolated Compose project `gsp-pr4-verify` and an ephemeral `/tmp/gsp-pr4-verify.env`; no existing volume or data was removed. Only `db`, `minio`, `minio-init`, `mailpit`, and `api` were started.
- Command: `docker compose -p gsp-pr4-verify --env-file /tmp/gsp-pr4-verify.env up -d db minio minio-init mailpit` — PASS: database, MinIO, and Mailpit became healthy; MinIO initialization exited 0.
- Commands: `docker compose ... build api`; `docker compose ... run --rm --no-deps api alembic upgrade head`; `docker compose ... exec -T db psql -U project_migrator -d student_project -Atc 'SELECT version_num FROM alembic_version;'` — PASS: all revisions ran and returned `20260330_07`.
- Commands: `docker compose ... up -d api`; `curl -fsS http://127.0.0.1:18000/health` — PASS: API healthy and returned `{"status":"ok","service":"generic-student-api"}`.

### Live HTTP and PostgreSQL evidence

| Command / scenario | Exact result |
| --- | --- |
| `docker compose ... run --rm --no-deps -v "$PWD/backend:/workspace:ro" -w /workspace -e TEST_API_URL=http://api:8000 -e MAILPIT_URL=http://mailpit:8025 -e TEST_DATABASE_URL=postgresql://project_migrator:<ephemeral>@db:5432/student_project api python -m unittest tests.test_identity_http.IdentityHttpTests.test_registration_login_recovery_and_roles -v` | PASS: `Ran 1 test in 0.833s`, `OK`; admin lifecycle/mutation, viewer read-only denial, append-only HTTP surface, recovery/login, and second-tenant denial executed live. |
| Same isolated runner with `/tmp/pr4_runtime_scenario.py` mounted read-only | PASS JSON; admin created, member completed `draft -> running -> completed`, viewer read and mutation denial succeeded, four typed metrics and provenance were returned, invalid terminal transition returned 409, result PATCH returned 404, and tenant B read/update returned 404. |
| `docker compose ... run ... -e TEST_DATABASE_URL=postgresql+psycopg://app_runtime:<ephemeral>@db:5432/student_project api python -m unittest tests.test_rls_integration -v` | PASS: `Ran 2 tests in 0.077s`, `OK`; missing/cross-tenant context and one-connection pool reuse were isolated. |
| `docker compose ... exec -T db psql postgresql://app_runtime:<ephemeral>@localhost:5432/student_project` experiment visibility probe | PASS: tenant A `visible=1`, tenant B `visible=0`, missing context `visible=0`. |
| `docker compose ... exec -T db psql -U project_migrator -d student_project` constraint/trigger probe under `SET ROLE project_owner` | PASS notices: tenant-aware result FK rejected a mismatched parent; result update and metric delete were rejected as append-only; `app_runtime` had `rolbypassrls=false`; composite result and metric FKs were present. |
| Runtime metric/provenance query under tenant A context | PASS: one completed result retained creator/time/input/output provenance and exactly four metrics (`number`, `text`, `boolean`, `json`) with one matching typed column each, creator, timestamp, unit/step where supplied. |

Harness corrections were environmental, not source fixes: an unavailable historical `/tmp` virtualenv was replaced by the built API image; the isolated API was recreated with the test's documented `http://localhost:5173` origin; the SQLAlchemy URL was corrected to explicit `postgresql+psycopg`; and the owner FK probe set tenant context before testing the composite constraint. Focused reruns then passed.

### Outcome, budget, and cleanup

- No backend source or task checkbox change was required. Corrective authored change: apply-progress evidence only; PR 4 implementation remains 452 changed lines and its persisted task stays checked.
- Command: `docker compose -p gsp-pr4-verify --env-file /tmp/gsp-pr4-verify.env down --remove-orphans` (without `-v`) — PASS: no `gsp-pr4-verify-*` containers remained; isolated PostgreSQL and MinIO volumes were preserved; temporary env/scenario files were removed. Services were not left running.
- Workload/PR boundary remained PR 4 only (`stacked-to-main`, automatic corrective gate rerun). PR 5, frontend work, review, receipt, branch, commit, and PR operations were not started.
  - Remaining implementation and parent-owned task lines are unchanged from the cumulative ledger above; next lifecycle action belongs to the parent.

## Experiments authenticated frontend slice

### Structured status and work-unit boundary

- Consumed parent native authority: `next_recommended=apply`, `apply=ready`, verify/archive blocked, and progress 16/25; the acquired work unit was `experiments-frontend-slice` and parent retains attempt settlement.
- Action context was repo-local at `/home/martin/Code/ceia-bdia` with edits limited to `clase_08/proyecto/frontend/**` and this OpenSpec change.
- Delivery path was resolved as `auto-chain`, `stacked-to-main`; this bounded slice depends on the runtime-verified PR 4 API and does not begin documents, assistant, PR 5, review, branch, commit, or PR work.
- Review budget: **300 additions plus 4 deletions = 304 authored changed lines** including this 48-line cumulative ledger append (the product/test slice is 256 lines), below the 600-line work-unit limit.

### Partial task progress and persisted checkbox

- Implemented the Experiments-only portion of the broad PR 7 frontend task: authenticated bounded list/pagination, create, lifecycle start/finish, append-only result entry, typed metric/provenance detail, loading/empty/error states, responsive table/cards, and viewer read-only presentation.
- The broad PR 7 row remains intentionally unchecked because documents, assistant, and other authenticated screens remain pending:
  - [ ] Reuse individual compatible shadcn components and table/form patterns from `material_desarrollo/frontend/src/components/ui/*` and data-table sources into `frontend/src/features/**`; keep screens minimal, accessible, viewer read-only, and backend-authorized, verifying lint/typecheck/build or bounded manual checks. <!-- sdd-owner: implementation -->

### Files changed

- Added `frontend/src/experiments/ExperimentsPage.tsx` and `ExperimentsPage.test.tsx`.
- Updated `frontend/src/api.ts` with typed experiment/result/metric contracts and cookie/CSRF-bound API methods.
- Updated `frontend/src/App.tsx` to replace only the Experiments placeholder and derive mutation presentation from the trusted session role.
- Updated `frontend/src/index.css` with bounded responsive experiment, result, metric, and dialog composition.

### Verification evidence

| Command | Result |
| --- | --- |
| `cd clase_08/proyecto/frontend && npm test -- --run src/experiments/ExperimentsPage.test.tsx` | PASS: 4 focused tests for loading/empty/viewer behavior, create/refresh, lifecycle error handling, result append, typed metric presentation, and provenance. |
| `cd clase_08/proyecto/frontend && npm test` | PASS: 53 tests in 3 files. |
| `cd clase_08/proyecto/frontend && npm run typecheck` | PASS. |
| `cd clase_08/proyecto/frontend && npm run lint` | PASS. |
| `cd clase_08/proyecto/frontend && npm run build` | PASS: Vite production build, 1,787 modules transformed. |
| `cd clase_08/proyecto/frontend && npm audit --audit-level=high` | PASS: 0 vulnerabilities. |
| `git diff --check -- clase_08/proyecto/frontend` | PASS. |
| Bounded exclusion scan of `frontend/src/experiments/**` for tenant IDs, DVEM, invitations, documents, and assistant scope | PASS: no matches. |

Runtime harness: **N/A for this frontend slice**. `docker compose ps -a` returned no running services, so no authenticated browser/API scenario was fabricated. The predecessor PR 4 live PostgreSQL/API role matrix and lifecycle harness remains recorded above; this slice verifies its client boundary through focused component mocks, the full frontend suite, and production compilation.

### Deviations, cleanup, and rollback

- No product or security design deviation. Existing target-owned table, dialog, field, badge, skeleton, cookie/CSRF API, responsive card, and Spanish UI conventions were reused; no restored source file was copied or modified.
- Cleanup: removed generated `frontend/dist`; `docker compose ps -a` confirmed no services were left running. `node_modules` remains ignored local test tooling after `npm install`; no package manifest or lockfile changed.
- Rollback boundary: remove `frontend/src/experiments/`, revert the experiment API additions in `frontend/src/api.ts`, restore the `/experiments` placeholder route/import in `frontend/src/App.tsx`, and remove only the experiment CSS suffix. This leaves auth, users, landing, backend PR 4, and later screens unchanged.

### Remaining implementation tasks

The seven exact unchecked implementation-owned rows remain the PR 5 storage task, PR 5 retrieval task, PR 6 SQL task, PR 6 assistant task, the broad partially implemented PR 7 frontend task quoted above, PR 8 fixture/script task, and PR 8 README task. Parent-owned lifecycle rows remain deferred byte-for-byte.

## PR 5 — private documents, ingestion, and tenant-safe vector RAG

### Structured status and boundary

- Consumed parent native authority: `next_recommended=apply`, `apply=ready`, verify/archive blocked, progress 16/25, and acquired work unit `pr5-storage-ingestion-rag`; parent retains attempt settlement.
- Action context was repo-local with edits confined to the supplied backend, MinIO infrastructure, and OpenSpec allowlist. Strict TDD was inactive.
- Delivery remained `auto-chain`, `stacked-to-main`; this work unit is exactly PR 5. PR 6 Text-to-SQL/orchestration, document frontend screens, fixtures, final documentation, review, branch, commit, and PR operations were not started.
- Review budget: **399 additions plus 7 deletions = 406 authored changed lines**, below the approved 600-line limit.

### Completed tasks and persisted checkboxes

- [x] Adapt compatible generic upload/storage patterns into `backend/app/storage/`, `infra/minio/init.sh`, and asset APIs with opaque tenant keys, private bucket, authorization, and bounded uploads; support only PDF/TXT/MD for ingestion (PNG/JPEG/CSV/JSON remain deferred unless already trivial), and verify guessed-key denial and original-object preservation. <!-- sdd-owner: implementation -->
- [x] Add bounded extractors, chunk activation, fixed-dimension `EmbeddingProvider`, pgvector persistence, and tenant-filtered retrieval under `backend/app/{ingestion,providers,assistant}`; use one configured/local provider seam, fail closed when unavailable, and verify colliding cross-tenant vector matches never reach provider context. <!-- sdd-owner: implementation -->
- Both corresponding rows were persisted as checked in `tasks.md`; parent-owned rows were preserved byte-for-byte.

### Files changed

- Added `backend/app/documents.py`, migration `20260330_08_documents_rag.py`, focused `tests/test_documents.py`, and private-bucket helper `infra/minio/init.sh`.
- Updated backend settings, SQLAlchemy metadata, router registration/error allowlist, requirements, and the two OpenSpec artifacts.
- The API exposes authorized PDF/TXT/MD upload, integrity-checked download, retryable ingestion, and tenant-filtered retrieval. Object keys are opaque and never accepted from clients; original bytes are retained unchanged.
- Migration 08 converts persistence to fixed `vector(8)`, adds active chunk generations, tenant-aware foreign keys/uniqueness, an append-only ingestion-run table, forced RLS, and an HNSW cosine index.

### Verification and runtime proof

| Command / scenario | Exact result |
| --- | --- |
| `python3 -m unittest tests.test_documents -v` before implementation | RED: import failed because `app.documents` did not exist. |
| Isolated API-image `python -m unittest tests.test_documents -v` | PASS: 4 focused tests for authorized storage capabilities/original bytes, bounded TXT/MD extraction/chunking, fixed dimension, malformed/unavailable providers, vector/RLS migration markers. |
| Isolated API-image `TEST_DATABASE_URL="$RUNTIME_DATABASE_URL" python -m unittest discover -s tests -v` | PASS: 27 tests, 2 configured HTTP skips. Pool reuse and missing/cross-tenant context tests passed live against PostgreSQL. |
| `python -m compileall -q app tests migrations` with isolated bytecode path | PASS. |
| `npx --yes pyright --pythonpath /tmp/gsp-pr5-venv/bin/python` | PASS: 0 errors, 0 warnings. |
| `docker compose -p gsp-pr5-verify --env-file .env.example config -q` and isolated API build | PASS. |
| Clean isolated migration through `20260330_08` | PASS on pgvector/PostgreSQL; API health returned `{"status":"ok","service":"generic-student-api"}`. |
| Live two-tenant API/MinIO scenario | PASS: each tenant uploaded identical TXT content; tenant A bytes matched the original with `cmp`; tenant B guessed A's document UUID and received 404; anonymous direct MinIO GET received 403. |
| Live PDF, TXT, and Markdown ingestion | PASS: all three returned `ready`; generated PDF and Markdown each produced one active chunk. JSON MIME/extension was denied with 415; a 25 MiB + 1 byte TXT was denied with 413. |
| Live colliding-vector retrieval | PASS: PostgreSQL proved two tenant owners with one identical vector; tenant A retrieval returned one A citation and no B document/context. `embeddings` had RLS+FORCE RLS and `app_runtime.rolbypassrls=false`. |
| Dependency failure | PASS: stopped isolated MinIO caused authorized download to return 503; malformed and throwing embedding adapters raised closed provider errors. MinIO was restarted before cleanup. |
| `git diff --check` on allowed surfaces | PASS. |

### Deviations, cleanup, and rollback

- No product-scope deviation. The approved logical storage/ingestion/provider/assistant seams are kept in one compact `app/documents.py` vertical slice to preserve the complete security invariant within the 600-line PR boundary; PR 6 orchestration remains absent.
- Cleanup used `docker compose -p gsp-pr5-verify ... down --remove-orphans` without `-v`: zero `gsp-pr5-verify-*` containers remain. Isolated volumes `gsp-pr5-verify_student-project-postgres` and `gsp-pr5-verify_student-project-minio` remain preserved; unrelated services and volumes were not touched. Temporary runtime files were removed.
- Rollback boundary: remove migration 08, `app/documents.py`, `tests/test_documents.py`, and `infra/minio/init.sh`; revert only document metadata/config/router/dependency additions; reset only the isolated PR 5 PostgreSQL/MinIO volumes if local data rollback is desired. Identity, experiments, frontend, landing, and restored sources remain unaffected.

### Remaining implementation tasks

- Exact unchecked implementation-owned rows are the two PR 6 rows, the broad partially completed PR 7 frontend row, and the two PR 8 rows. Parent lifecycle rows remain deferred unchanged. Next lifecycle action belongs to the parent.
