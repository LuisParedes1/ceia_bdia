# pyright: reportMissingImports=false

import os
import unittest
from uuid import uuid4

from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv("TEST_DATABASE_URL", "")


@unittest.skipUnless(DATABASE_URL, "set TEST_DATABASE_URL to run PostgreSQL RLS probes")
class RlsIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(DATABASE_URL, pool_size=1, max_overflow=0)
        cls.user_a, cls.user_b, cls.tenant_a, cls.tenant_b = uuid4(), uuid4(), uuid4(), uuid4()
        with cls.engine.begin() as connection:
            for user_id in (cls.user_a, cls.user_b):
                connection.execute(
                    text("INSERT INTO users (id, email, password_hash) VALUES (:id, :email, 'x')"),
                    {"id": user_id, "email": f"fixture-{user_id}@example.test"},
                )
            for user_id, tenant_id, name in ((cls.user_a, cls.tenant_a, "tenant-a"), (cls.user_b, cls.tenant_b, "tenant-b")):
                cls._context(connection, user_id, tenant_id)
                connection.execute(text("INSERT INTO tenants (id, name) VALUES (:id, :name)"), {"id": tenant_id, "name": name})
                connection.execute(text("INSERT INTO memberships (tenant_id, user_id) VALUES (:tenant, :user)"), {"tenant": tenant_id, "user": user_id})

    @staticmethod
    def _context(connection, user_id, tenant_id) -> None:
        connection.execute(text("SELECT set_config('app.user_id', :value, true)"), {"value": str(user_id)})
        connection.execute(text("SELECT set_config('app.tenant_id', :value, true)"), {"value": str(tenant_id)})

    def test_missing_and_cross_tenant_context_leave_victim_unchanged(self) -> None:
        with self.engine.connect() as connection:
            with connection.begin():
                self.assertEqual(connection.execute(text("SELECT count(*) FROM tenants")).scalar_one(), 0)
            with connection.begin():
                self._context(connection, self.user_a, self.tenant_a)
                self.assertEqual(connection.execute(text("SELECT count(*) FROM tenants")).scalar_one(), 1)
                self.assertEqual(connection.execute(text("SELECT count(*) FROM tenants WHERE id = :id"), {"id": self.tenant_b}).scalar_one(), 0)
                with self.assertRaises(Exception):
                    connection.execute(
                        text("INSERT INTO tenants (id, name) VALUES (:id, :name)"),
                        {"id": uuid4(), "name": "forged"},
                    )
        with self.engine.begin() as connection:
            self._context(connection, self.user_b, self.tenant_b)
            self.assertEqual(
                connection.execute(text("SELECT name FROM tenants WHERE id = :id"), {"id": self.tenant_b}).scalar_one(),
                "tenant-b",
            )

    def test_experiment_status_history_is_tenant_isolated_and_append_only(self) -> None:
        experiment_id, transition_id = uuid4(), uuid4()
        with self.engine.begin() as connection:
            self._context(connection, self.user_a, self.tenant_a)
            connection.execute(
                text("INSERT INTO experiments (id, tenant_id, creator_id, name, status) VALUES (:id, :tenant, :actor, 'history', 'running')"),
                {"id": experiment_id, "tenant": self.tenant_a, "actor": self.user_a},
            )
            connection.execute(
                text("INSERT INTO experiment_status_transitions (id, tenant_id, experiment_id, previous_status, next_status, actor_id) VALUES (:id, :tenant, :experiment, 'draft', 'running', :actor)"),
                {"id": transition_id, "tenant": self.tenant_a, "experiment": experiment_id, "actor": self.user_a},
            )
        with self.engine.begin() as connection:
            self._context(connection, self.user_b, self.tenant_b)
            self.assertEqual(
                connection.execute(text("SELECT count(*) FROM experiment_status_transitions WHERE id=:id"), {"id": transition_id}).scalar_one(),
                0,
            )
        with self.assertRaises(Exception):
            with self.engine.begin() as connection:
                self._context(connection, self.user_a, self.tenant_a)
                connection.execute(
                    text("UPDATE experiment_status_transitions SET reason=:reason WHERE id=:id"),
                    {"id": transition_id, "reason": "rewritten"},
                )

    def test_archived_experiment_metadata_remains_tenant_isolated(self) -> None:
        experiment_id = uuid4()
        with self.engine.begin() as connection:
            self._context(connection, self.user_a, self.tenant_a)
            connection.execute(text("INSERT INTO experiments (id,tenant_id,creator_id,name,status,archived_at,archived_by) VALUES (:id,:tenant,:actor,'archived','completed',now(),:actor)"), {"id": experiment_id, "tenant": self.tenant_a, "actor": self.user_a})
        with self.engine.begin() as connection:
            self._context(connection, self.user_b, self.tenant_b)
            self.assertEqual(connection.execute(text("SELECT count(*) FROM experiments WHERE id=:id AND archived_at IS NOT NULL"), {"id": experiment_id}).scalar_one(), 0)
        with self.assertRaises(Exception):
            with self.engine.begin() as connection:
                self._context(connection, self.user_a, self.tenant_a)
                connection.execute(text("UPDATE experiments SET status='failed' WHERE id=:id"), {"id": experiment_id})

    def test_audit_definer_is_the_only_append_path_and_global_count_bypasses_force_rls(self) -> None:
        resource = f"recovery-{uuid4().hex}"
        with self.assertRaises(Exception):
            with self.engine.begin() as connection:
                self._context(connection, self.user_a, self.tenant_a)
                connection.execute(text("INSERT INTO audit_events (id,actor_id,tenant_id,action,outcome,metadata) VALUES (:id,:actor,:tenant,'auth.login','success','{}'::jsonb)"), {"id": uuid4(), "actor": self.user_a, "tenant": self.tenant_a})
        for statement in ("UPDATE audit_events SET outcome='failed' WHERE false", "DELETE FROM audit_events WHERE false", "UPDATE ingestion_runs SET status='failed' WHERE false", "DELETE FROM ingestion_runs WHERE false"):
            with self.subTest(statement=statement), self.assertRaises(Exception):
                with self.engine.begin() as connection:
                    self._context(connection, self.user_a, self.tenant_a)
                    connection.execute(text(statement))
        with self.engine.begin() as connection:
            self._context(connection, self.user_a, self.tenant_a)
            event_id = connection.execute(text("SELECT append_audit_event(:actor,:tenant,'auth.login','success','session',CAST(:metadata AS jsonb))"), {"actor": self.user_a, "tenant": self.tenant_a, "metadata": "{}"}).scalar_one()
            self.assertIsNotNone(event_id)
            self.assertEqual(connection.execute(text("SELECT count(*) FROM audit_events WHERE id=:id"), {"id": event_id}).scalar_one(), 0)
            self.assertEqual(connection.execute(text("SELECT recovery_request_count(:resource)"), {"resource": resource}).scalar_one(), 0)
            connection.execute(text("SELECT append_audit_event(NULL,NULL,'auth.recovery.request','success',:resource,CAST(:metadata AS jsonb))"), {"resource": resource, "metadata": "{}"})
            self.assertEqual(connection.execute(text("SELECT recovery_request_count(:resource)"), {"resource": resource}).scalar_one(), 1)
        for action, outcome, metadata in (("unknown.action", "success", "{}"), ("auth.login", "accepted", "{}"), ("auth.login", "success", '{"token":"secret"}')):
            with self.subTest(action=action, outcome=outcome, metadata=metadata), self.assertRaises(Exception):
                with self.engine.begin() as connection:
                    self._context(connection, self.user_a, self.tenant_a)
                    connection.execute(text("SELECT append_audit_event(:actor,:tenant,:action,:outcome,'resource',CAST(:metadata AS jsonb))"), {"actor": self.user_a, "tenant": self.tenant_a, "action": action, "outcome": outcome, "metadata": metadata})

    def test_audit_definer_rejects_forged_request_context_and_global_events(self) -> None:
        calls = (
            (self.user_b, self.tenant_a, "auth.login", "success"),
            (self.user_a, self.tenant_b, "auth.login", "success"),
            (None, None, "auth.login", "success"),
        )
        for actor, tenant, action, outcome in calls:
            with self.subTest(actor=actor, tenant=tenant, action=action), self.assertRaises(Exception):
                with self.engine.begin() as connection:
                    self._context(connection, self.user_a, self.tenant_a)
                    connection.execute(
                        text("SELECT append_audit_event(:actor,:tenant,:action,:outcome,'resource','{}'::jsonb)"),
                        {"actor": actor, "tenant": tenant, "action": action, "outcome": outcome},
                    )
        with self.engine.begin() as connection:
            self._context(connection, self.user_a, self.tenant_a)
            self.assertIsNotNone(connection.execute(
                text("SELECT append_audit_event(:actor,:tenant,'auth.login','success','resource','{}'::jsonb)"),
                {"actor": self.user_a, "tenant": self.tenant_a},
            ).scalar_one())
            self.assertIsNotNone(connection.execute(
                text("SELECT append_audit_event(NULL,NULL,'auth.recovery.request','rate_limited','resource','{}'::jsonb)")
            ).scalar_one())

    def test_pooled_connection_does_not_retain_context(self) -> None:
        with self.engine.begin() as connection:
            self._context(connection, self.user_a, self.tenant_a)
            self.assertEqual(connection.execute(text("SELECT count(*) FROM tenants")).scalar_one(), 1)
        with self.engine.begin() as connection:
            self.assertEqual(connection.execute(text("SELECT count(*) FROM tenants")).scalar_one(), 0)


if __name__ == "__main__":
    unittest.main()
