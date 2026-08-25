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
            connection.execute(
                text("""INSERT INTO experiments (id,tenant_id,creator_id,name,status,archived_at,archived_by)
                    VALUES (:id,:tenant,:actor,'archived','completed',now(),:actor)"""),
                {"id": experiment_id, "tenant": self.tenant_a, "actor": self.user_a},
            )
        with self.engine.begin() as connection:
            self._context(connection, self.user_b, self.tenant_b)
            self.assertEqual(
                connection.execute(text("SELECT count(*) FROM experiments WHERE id=:id AND archived_at IS NOT NULL"), {"id": experiment_id}).scalar_one(),
                0,
            )
        with self.assertRaises(Exception):
            with self.engine.begin() as connection:
                self._context(connection, self.user_a, self.tenant_a)
                connection.execute(text("UPDATE experiments SET status='failed' WHERE id=:id"), {"id": experiment_id})

    def test_pooled_connection_does_not_retain_context(self) -> None:
        with self.engine.begin() as connection:
            self._context(connection, self.user_a, self.tenant_a)
            self.assertEqual(connection.execute(text("SELECT count(*) FROM tenants")).scalar_one(), 1)
        with self.engine.begin() as connection:
            self.assertEqual(connection.execute(text("SELECT count(*) FROM tenants")).scalar_one(), 0)


if __name__ == "__main__":
    unittest.main()
