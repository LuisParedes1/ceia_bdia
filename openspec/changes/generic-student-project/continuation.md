# Cross-computer continuation: Generic Student Project

## Goal

Continue the three-day generic student-project MVP from its documented OpenSpec state without treating local runtime state as portable.

## Start here

Run `gentle-ai sdd-status generic-student-project --cwd <repo> --json --instructions`. Reconcile the reported active SDD attempt exactly through its native instructions before a new runtime apply. Do not persist, recover, or reuse any opaque token.

## Resume from another computer

After transferring the complete working tree, open a terminal in the repository and start Pi:

```bash
cd /path/to/ceia-bdia
pi
```

Inside Pi, run:

```text
/sdd-continue generic-student-project
```

If the meta-command is unavailable, send this exact request instead:

```text
Resume the OpenSpec change `generic-student-project`. Read `openspec/changes/generic-student-project/continuation.md`, run `gentle-ai sdd-status generic-student-project --cwd <repo> --json --instructions`, reconcile any active SDD attempt only through the returned native instructions, and continue with the next ready apply work unit. Do not verify or archive while tasks remain incomplete.
```

The orchestrator must route from native status, not infer progress from chat history. The expected next implementation is PR 4: the experiments backend vertical slice, followed by the real Experiments frontend using the DVEM table/form pattern.

## Artifacts

- `proposal.md`, `spec.md`, `design.md`, `tasks.md`, and `apply-progress.md` are complete artifacts.
- `verify-report.md` is still missing.
- Before this checkpoint, task progress was 23 total, 11 completed, and 12 pending; native status recommended `apply` and blocked verify/archive.

## Completed

- Day 1: foundation, PostgreSQL/pgvector/FORCE RLS, identity/recovery/fixed roles, one active membership, and frontend auth shell.
- Extra corrections: themes; Spanish copy, errors, and email; blur-local validation; password confirmation and visibility; logout confirmation; `tenant_name`; and the query-token reset-password route with manual fallback.
- DVEM users directory: migration `20260330_06`; admin-only paginated `GET /api/members`; tenant/RLS isolation; responsive directory; search, filter, sort, pagination, details, and create dialogs.
- Day 3 partial: landing, auth, and users UI are complete.

## Pending

- Day 2: experiments/results/typed metrics/provenance; private MinIO document APIs; PDF/TXT/MD ingestion; chunks, embeddings, and tenant-safe RAG.
- Day 3: guarded Text-to-SQL, assistant orchestration, real experiment/document/assistant screens, fixtures, scripts, documentation, and final proof.

## Next work order

1. Reconcile native status and its active attempt.
2. PR 4: experiments backend vertical slice.
3. Real Experiments frontend using the DVEM table/form pattern.
4. PR 5: documents, MinIO, ingestion, and RAG.
5. PR 6: Text-to-SQL and assistant.
6. PR 7: remaining screens.
7. PR 8: fixtures, scripts, docs, and final verification.

## Environment bootstrap

On the new machine, recreate local configuration and data. If `.env` is absent, copy `.env.example` to `.env`, configure it locally, then run:

```bash
docker compose up -d db minio minio-init mailpit
# Wait until the required services are healthy.
docker compose run --rm api alembic upgrade head
docker compose up --build -d
docker compose ps -a
```

## Validation commands

Run focused validation appropriate to the slice. Integration validation may need a configured environment.

```bash
# Backend
python -m unittest discover
python -m compileall app
pyright

# Frontend
npm test
npm run typecheck
npm run lint
npm run build
npm audit

# Landing
npm test
npm run check
npm run build
npm audit

# Current stack health
docker compose ps -a
```

## Portable vs ephemeral

Portable: OpenSpec artifacts and source files that are copied or transferred through Git. Ephemeral: `.env`, Docker volumes, migrated database data, local users, and service runtime state. At handoff, local services were healthy, Alembic was `20260330_06 (head)`, and 11 local users existed; recreate these on the new machine.

## Constraints

Keep implementation under the canonical target roots, preserve `material_desarrollo/**` as immutable, and do not implement excluded scope. Receipt-driven development is disabled/unmanaged.

## Git transfer warning

`clase_08/proyecto/` and `openspec/changes/generic-student-project/` are untracked. No commits, branches, or PRs exist. Nothing transfers through Git until the user explicitly commits and pushes it, or copies/synchronizes the working tree.
