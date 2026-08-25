"""Experiment persistence under an already established tenant transaction."""

from datetime import UTC, datetime
import json
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.experiment_schemas import ResultCreate
from app.services.pagination import Page

if TYPE_CHECKING:
    from app.api.experiments import ExperimentListQuery


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class ExperimentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, tenant: UUID, actor: UUID, name: str) -> dict:
        row = self.db.execute(text("INSERT INTO experiments (id,tenant_id,creator_id,name,status) VALUES (:id,:tenant,:actor,:name,'draft') RETURNING *"), {"id": uuid4(), "tenant": tenant, "actor": actor, "name": name}).mappings().one()
        return dict(row)

    def get(self, tenant: UUID, experiment_id: UUID) -> dict | None:
        row = self.db.execute(text("SELECT * FROM experiments WHERE tenant_id=:tenant AND id=:id"), {"tenant": tenant, "id": experiment_id}).mappings().first()
        if not row:
            return None
        item = dict(row)
        item["results"] = [dict(result) for result in self.db.execute(text("SELECT * FROM results WHERE tenant_id=:tenant AND experiment_id=:id ORDER BY created_at,id"), {"tenant": tenant, "id": experiment_id}).mappings()]
        for result in item["results"]:
            result["metrics"] = [dict(metric) for metric in self.db.execute(text("SELECT * FROM metrics WHERE tenant_id=:tenant AND result_id=:result ORDER BY recorded_at,id"), {"tenant": tenant, "result": result["id"]}).mappings()]
        return item

    def list(self, tenant: UUID, query: "ExperimentListQuery") -> Page[dict]:
        values = {
            "tenant": tenant,
            "search": escape_like(query.search),
            "status": query.status,
            "sort_created_at_asc": query.sort == "created_at:asc",
            "sort_created_at_desc": query.sort == "created_at:desc",
            "sort_name_asc": query.sort == "name:asc",
            "sort_name_desc": query.sort == "name:desc",
            "sort_result_count_desc": query.sort == "result_count:desc",
            "limit": query.per_page,
            "offset": (query.page - 1) * query.per_page,
        }
        total = self.db.execute(text("""SELECT count(*) FROM experiments e
            WHERE e.tenant_id=:tenant
              AND (CAST(:status AS varchar) IS NULL OR e.status=CAST(:status AS varchar))
              AND (:search='' OR e.name ILIKE ('%' || :search || '%') ESCAPE '\\')"""), values).scalar_one()
        rows = self.db.execute(text("""SELECT e.*, count(r.id) AS result_count
            FROM experiments e
            LEFT JOIN results r ON r.tenant_id=e.tenant_id AND r.experiment_id=e.id
            WHERE e.tenant_id=:tenant
              AND (CAST(:status AS varchar) IS NULL OR e.status=CAST(:status AS varchar))
              AND (:search='' OR e.name ILIKE ('%' || :search || '%') ESCAPE '\\')
            GROUP BY e.id
            ORDER BY
              CASE WHEN :sort_created_at_asc THEN e.created_at END ASC,
              CASE WHEN :sort_created_at_desc THEN e.created_at END DESC,
              CASE WHEN :sort_name_asc THEN e.name END ASC,
              CASE WHEN :sort_name_desc THEN e.name END DESC,
              CASE WHEN :sort_result_count_desc THEN count(r.id) END DESC,
              e.id DESC
            LIMIT :limit OFFSET :offset"""), values).mappings()
        return Page([dict(row) for row in rows], total, query.page, query.per_page)

    def update(self, tenant: UUID, experiment_id: UUID, name: str | None, status: str | None) -> dict | None:
        row = self.db.execute(text("UPDATE experiments SET name=COALESCE(:name,name),status=COALESCE(:status,status),updated_at=now() WHERE tenant_id=:tenant AND id=:id RETURNING *"), {"name": name, "status": status, "tenant": tenant, "id": experiment_id}).mappings().first()
        return dict(row) if row else None

    def append_result(self, tenant: UUID, actor: UUID, experiment_id: UUID, payload: ResultCreate) -> dict:
        result_id = uuid4()
        result = self.db.execute(text("INSERT INTO results (id,tenant_id,experiment_id,creator_id,status,input_summary,output_summary) VALUES (:id,:tenant,:experiment,:actor,:status,:input,:output) RETURNING *"), {"id": result_id, "tenant": tenant, "experiment": experiment_id, "actor": actor, "status": payload.status, "input": payload.input_summary, "output": payload.output_summary}).mappings().one()
        metrics = []
        for metric in payload.metrics:
            values: dict[str, object] = {"number": None, "text": None, "boolean": None, "json": None}
            values[metric.type] = json.dumps(metric.value) if metric.type == "json" else metric.value
            row = self.db.execute(text("INSERT INTO metrics (id,tenant_id,result_id,creator_id,name,value_type,number_value,text_value,boolean_value,json_value,unit,step,recorded_at) VALUES (:id,:tenant,:result,:actor,:name,:type,:number,:text,:boolean,CAST(:json AS jsonb),:unit,:step,:at) RETURNING *"), {"id": uuid4(), "tenant": tenant, "result": result_id, "actor": actor, "name": metric.name, "type": metric.type, "unit": metric.unit, "step": metric.step, "at": metric.timestamp or datetime.now(UTC), **values}).mappings().one()
            metrics.append(dict(row))
        return {**dict(result), "metrics": metrics}
