"""Typed experiment HTTP contracts."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

ExperimentStatus = Literal["draft", "running", "completed", "failed"]
MetricType = Literal["number", "text", "boolean", "json"]


class ExperimentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ExperimentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    status: ExperimentStatus | None = None


class MetricCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: MetricType
    value: Any
    unit: str | None = Field(default=None, max_length=40)
    step: int | None = Field(default=None, ge=0)
    timestamp: datetime | None = None

    @model_validator(mode="after")
    def typed_value(self):
        valid = {
            "number": isinstance(self.value, (int, float)) and not isinstance(self.value, bool),
            "text": isinstance(self.value, str),
            "boolean": isinstance(self.value, bool),
            "json": isinstance(self.value, (dict, list)),
        }
        if not valid[self.type]:
            raise ValueError("metric value does not match type")
        return self


class ResultCreate(BaseModel):
    status: Literal["completed", "failed"]
    input_summary: str | None = Field(default=None, max_length=4000)
    output_summary: str | None = Field(default=None, max_length=4000)
    metrics: list[MetricCreate] = Field(default_factory=list, max_length=100)


class ExperimentPath(BaseModel):
    experiment_id: UUID
