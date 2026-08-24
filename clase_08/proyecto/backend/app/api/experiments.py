"""Tenant-owned experiment, result, and metric routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Query, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.auth import _csrf, _session, _tenant_context, db_session
from app.api.experiment_schemas import ExperimentCreate, ExperimentUpdate, ResultCreate
from app.repositories.experiments import ExperimentRepository
from app.services.experiments import ExperimentService
from app.services.pagination import PageRequest

router = APIRouter(prefix="/api/experiments", tags=["experiments"])


def _trusted(db: Session, state: dict, roles: set[str]) -> UUID:
    db.commit()
    return _tenant_context(db, state, roles)


def _set_context(db: Session, state: dict, tenant: UUID) -> None:
    db.execute(text("SELECT set_config('app.user_id', :user, true), set_config('app.tenant_id', :tenant, true)"), {"user": str(state["user_id"]), "tenant": str(tenant)})


def _mutation(request: Request, db: Session, state: dict, csrf_header: str | None, csrf_cookie: str | None) -> UUID:
    _csrf(db, state, request, csrf_header, csrf_cookie)
    return _trusted(db, state, {"admin", "member"})


@router.get("")
def list_experiments(page: int = Query(1), per_page: int = Query(20), session_token: Annotated[str | None, Cookie()] = None, db: Session = Depends(db_session)) -> dict:
    try:
        paging = PageRequest(page, per_page)
    except ValueError as exc:
        raise HTTPException(422, "Los datos de paginación no son válidos.") from exc
    state = _session(db, session_token)
    tenant = _trusted(db, state, {"admin", "member", "viewer"})
    with db.begin():
        _set_context(db, state, tenant)
        result = ExperimentRepository(db).list(tenant, paging)
    return {"items": result.items, "total": result.total, "page": result.page, "per_page": result.per_page, "pages": result.pages}


@router.get("/{experiment_id}")
def get_experiment(experiment_id: UUID, session_token: Annotated[str | None, Cookie()] = None, db: Session = Depends(db_session)) -> dict:
    state = _session(db, session_token); tenant = _trusted(db, state, {"admin", "member", "viewer"})
    with db.begin():
        _set_context(db, state, tenant); item = ExperimentRepository(db).get(tenant, experiment_id)
    if not item: raise HTTPException(404, "No se encontró el experimento.")
    return item


@router.post("", status_code=status.HTTP_201_CREATED)
def create_experiment(payload: ExperimentCreate, request: Request, session_token: Annotated[str | None, Cookie()] = None, csrf_token: Annotated[str | None, Cookie()] = None, x_csrf_token: Annotated[str | None, Header()] = None, db: Session = Depends(db_session)) -> dict:
    state = _session(db, session_token); tenant = _mutation(request, db, state, x_csrf_token, csrf_token)
    with db.begin():
        _set_context(db, state, tenant); return ExperimentService(ExperimentRepository(db)).create(tenant, state["user_id"], payload)


@router.patch("/{experiment_id}")
def update_experiment(experiment_id: UUID, payload: ExperimentUpdate, request: Request, session_token: Annotated[str | None, Cookie()] = None, csrf_token: Annotated[str | None, Cookie()] = None, x_csrf_token: Annotated[str | None, Header()] = None, db: Session = Depends(db_session)) -> dict:
    state = _session(db, session_token); tenant = _mutation(request, db, state, x_csrf_token, csrf_token)
    try:
        with db.begin():
            _set_context(db, state, tenant); item = ExperimentService(ExperimentRepository(db)).update(tenant, experiment_id, payload)
    except ValueError as exc:
        raise HTTPException(409, "La transición de estado no es válida.") from exc
    if not item: raise HTTPException(404, "No se encontró el experimento.")
    return item


@router.post("/{experiment_id}/results", status_code=status.HTTP_201_CREATED)
def append_result(experiment_id: UUID, payload: ResultCreate, request: Request, session_token: Annotated[str | None, Cookie()] = None, csrf_token: Annotated[str | None, Cookie()] = None, x_csrf_token: Annotated[str | None, Header()] = None, db: Session = Depends(db_session)) -> dict:
    state = _session(db, session_token); tenant = _mutation(request, db, state, x_csrf_token, csrf_token)
    try:
        with db.begin():
            _set_context(db, state, tenant); item = ExperimentService(ExperimentRepository(db)).append_result(tenant, state["user_id"], experiment_id, payload)
    except ValueError as exc:
        raise HTTPException(409, "El experimento debe estar en ejecución.") from exc
    if not item: raise HTTPException(404, "No se encontró el experimento.")
    return item
