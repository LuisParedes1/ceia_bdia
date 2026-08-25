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

    def update(self, tenant: UUID, actor: UUID, experiment_id: UUID, payload: ExperimentUpdate) -> dict | None:
        current = self.repository.get(tenant, experiment_id)
        if not current:
            return None
        if payload.status:
            require_transition(current["status"], payload.status)
            if payload.reason is not None and payload.status == current["status"]:
                raise ValueError("reason requires a status change")
        item = self.repository.update(tenant, experiment_id, payload.name, payload.status)
        if item and payload.status and payload.status != current["status"]:
            self.repository.append_status_transition(
                tenant,
                experiment_id,
                current["status"],
                payload.status,
                actor,
                payload.reason,
            )
        return item

    def append_result(self, tenant: UUID, actor: UUID, experiment_id: UUID, payload: ResultCreate) -> dict | None:
        experiment = self.repository.get(tenant, experiment_id)
        if not experiment:
            return None
        if experiment["status"] != "running":
            raise ValueError("results require a running experiment")

        result = self.repository.append_result(tenant, actor, experiment_id, payload)
        if payload.terminal_status is None:
            return result

        require_transition(experiment["status"], payload.terminal_status)
        updated_experiment = self.repository.update(tenant, experiment_id, None, payload.terminal_status)
        if not updated_experiment:
            raise ValueError("experiment disappeared during result closure")
        self.repository.append_status_transition(
            tenant,
            experiment_id,
            experiment["status"],
            payload.terminal_status,
            actor,
            payload.transition_reason,
        )
        return {**result, "experiment": updated_experiment}
