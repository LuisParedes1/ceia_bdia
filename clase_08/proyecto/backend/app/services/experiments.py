"""Experiment use cases independent of HTTP/session handling."""

from uuid import UUID

from app.api.experiment_schemas import ExperimentCreate, ExperimentUpdate, ResultCreate
from app.domain.experiments import require_transition
from app.repositories.experiments import ExperimentRepository


class ExperimentService:
    def __init__(self, repository: ExperimentRepository):
        self.repository = repository

    def create(self, tenant: UUID, actor: UUID, payload: ExperimentCreate) -> dict:
        return self.repository.create(tenant, actor, payload.name)

    def update(self, tenant: UUID, experiment_id: UUID, payload: ExperimentUpdate) -> dict | None:
        current = self.repository.get(tenant, experiment_id)
        if not current:
            return None
        if payload.status:
            require_transition(current["status"], payload.status)
        return self.repository.update(tenant, experiment_id, payload.name, payload.status)

    def append_result(self, tenant: UUID, actor: UUID, experiment_id: UUID, payload: ResultCreate) -> dict | None:
        experiment = self.repository.get(tenant, experiment_id)
        if not experiment:
            return None
        if experiment["status"] != "running":
            raise ValueError("results require a running experiment")
        return self.repository.append_result(tenant, actor, experiment_id, payload)
