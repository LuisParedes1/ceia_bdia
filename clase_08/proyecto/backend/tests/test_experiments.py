"""Focused experiment policy, schema, pagination, and migration checks."""

import unittest
from pathlib import Path
from typing import cast
from unittest.mock import patch

_ENVIRONMENT = {
    "RUNTIME_DATABASE_URL": "postgresql+psycopg://runtime:password@db/student_project",
    "MIGRATOR_DATABASE_URL": "postgresql+psycopg://migrator:password@db/student_project",
    "ASSISTANT_DATABASE_URL": "postgresql+psycopg://assistant:password@db/student_project",
    "MINIO_ACCESS_KEY": "local-user", "MINIO_SECRET_KEY": "local-password",
    "SMTP_FROM": "noreply@example.test", "SESSION_SECRET": "test-session-secret",
    "RECOVERY_TOKEN_SECRET": "test-recovery-secret",
}


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.environment = patch.dict("os.environ", _ENVIRONMENT, clear=False); cls.environment.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.environment.stop()

    def test_lifecycle_allows_only_forward_terminal_transitions(self) -> None:
        from app.domain.experiments import require_transition
        for current, target in (("draft", "running"), ("running", "completed"), ("running", "failed")):
            require_transition(current, target)
        for current, target in (("draft", "completed"), ("completed", "running"), ("failed", "running")):
            with self.assertRaises(ValueError): require_transition(current, target)

    def test_metrics_require_the_declared_value_type(self) -> None:
        from pydantic import ValidationError
        from app.api.experiment_schemas import MetricCreate, MetricType
        for kind, value in (("number", 1.5), ("text", "ok"), ("boolean", True), ("json", {"fold": 1})):
            self.assertEqual(MetricCreate(name="score", type=cast(MetricType, kind), value=value).value, value)
        with self.assertRaises(ValidationError): MetricCreate(name="score", type="number", value=True)

    def test_pagination_is_bounded(self) -> None:
        from app.services.pagination import Page, PageRequest
        self.assertEqual(PageRequest(2, 20).offset, 20)
        self.assertEqual(Page([], 21, 1, 20).pages, 2)
        for values in ((0, 20), (1, 200)):
            with self.assertRaises(ValueError): PageRequest(*values)

    def test_migration_enforces_tenant_fks_and_append_only_history(self) -> None:
        source = Path("migrations/versions/20260330_07_experiments.py").read_text()
        for invariant in ("results_tenant_experiment_fk", "metrics_tenant_result_fk", "metrics_typed_value_check", "results_append_only", "metrics_append_only", "REVOKE UPDATE, DELETE"):
            self.assertIn(invariant, source)
        self.assertIn('down_revision = "20260330_06"', source)

    def test_experiment_routes_expose_no_historical_mutation(self) -> None:
        from app.main import app
        methods = {(getattr(route, "path", ""), method) for route in app.routes for method in getattr(route, "methods", set())}
        self.assertIn(("/api/experiments", "GET"), methods)
        self.assertIn(("/api/experiments/{experiment_id}/results", "POST"), methods)
        self.assertNotIn(("/api/experiments/{experiment_id}/results/{result_id}", "PATCH"), methods)

    def test_experiment_query_helpers_validate_and_escape_literal_search(self) -> None:
        from pydantic import ValidationError

        from app.api.experiments import ExperimentListQuery
        from app.repositories.experiments import escape_like

        query = ExperimentListQuery(
            page=2,
            per_page=20,
            search="  100%_ready\\  ",
            status="running",
            sort="result_count:desc",
        )
        self.assertEqual(query.search, "100%_ready\\")
        self.assertEqual(query.status, "running")
        self.assertEqual(query.sort, "result_count:desc")
        self.assertEqual(escape_like(query.search), r"100\%\_ready\\")
        invalid_payloads: tuple[dict[str, object], ...] = (
            {"status": "unknown"},
            {"status": ""},
            {"sort": "name:drop"},
        )
        for payload in invalid_payloads:
            with self.assertRaises(ValidationError):
                ExperimentListQuery.model_validate(cast(object, payload))


if __name__ == "__main__":
    unittest.main()
