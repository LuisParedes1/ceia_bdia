#!/usr/bin/env python3
"""Seed deterministic, tenant-isolated demo data without emitting secrets."""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from minio import Minio  # pyright: ignore[reportMissingImports] -- provided by the API runtime
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "backend"))

from app.core.config import settings  # noqa: E402  # pyright: ignore[reportMissingImports] -- backend path inserted above
from app.core.database import users as users_table  # noqa: E402  # pyright: ignore[reportMissingImports] -- backend path inserted above
from app.documents import FixedEmbeddingProvider  # pyright: ignore[reportMissingImports] -- backend path inserted above
from app.security.password import hash_password  # pyright: ignore[reportMissingImports] -- backend path inserted above

PREFIX = "https://example.test/gentle-ai/demo/"
ROLES = ("admin", "member", "viewer")
TENANTS = (("alpha", "Alpha Research Lab"), ("beta", "Beta Evaluation Lab"))
DASHBOARD_DAYS = 91
EMAIL_VARIABLES = {
    "admin": "ADMIN_EMAIL",
    "member": "MEMBER_EMAIL",
    "viewer": "VIEWER_EMAIL",
}


def load_fixture_credentials() -> tuple[dict[str, str], str]:
    from email_validator import EmailNotValidError, validate_email

    missing = [name for name in (*EMAIL_VARIABLES.values(), "FIXTURE_PASSWORD") if not os.environ.get(name)]
    if missing:
        raise SystemExit("Required fixture environment variables are missing: " + ", ".join(missing))

    emails: dict[str, str] = {}
    invalid: list[str] = []
    for role, name in EMAIL_VARIABLES.items():
        try:
            emails[role] = validate_email(
                os.environ[name].strip(), check_deliverability=False
            ).normalized
        except EmailNotValidError:
            invalid.append(name)
    if invalid:
        raise SystemExit("Invalid fixture email variables: " + ", ".join(invalid))

    duplicate_names = [
        name
        for role, name in EMAIL_VARIABLES.items()
        if list(emails.values()).count(emails[role]) > 1
    ]
    if duplicate_names:
        raise SystemExit("Fixture email variables must be distinct: " + ", ".join(duplicate_names))

    password = os.environ["FIXTURE_PASSWORD"]
    if len(password) < 8:
        raise SystemExit("FIXTURE_PASSWORD must contain at least 8 characters.")
    return emails, password


def fixture_id(value: str) -> UUID:
    return uuid5(NAMESPACE_URL, PREFIX + value)


def seed() -> None:
    alpha_emails, password = load_fixture_credentials()
    objects: list[tuple[str, bytes]] = []
    engine = create_engine(settings.migrator_database_url)
    embedder = FixedEmbeddingProvider(384)
    with engine.connect() as connection:
        for slug, tenant_name in TENANTS:
            tenant_id = fixture_id(f"tenant/{slug}")
            users = {role: fixture_id(f"tenant/{slug}/user/{role}") for role in ROLES}
            roles = {role: fixture_id(f"tenant/{slug}/role/{role}") for role in ROLES}
            experiment_id = fixture_id(f"tenant/{slug}/experiment")
            result_id = fixture_id(f"tenant/{slug}/result")
            document_id = fixture_id(f"tenant/{slug}/document")
            chunk_id = fixture_id(f"tenant/{slug}/chunk")
            content = f"{tenant_name} private retrieval fixture. Dataset policy: {slug}-only."
            data = content.encode()
            object_key = f"{tenant_id.hex}/demo-security-fixture.txt"
            objects.append((object_key, data))
            tenant_emails = alpha_emails if slug == "alpha" else {
                role: f"demo-beta-{role}@example.test" for role in ROLES
            }

            with connection.begin():
                connection.execute(text("SET ROLE project_owner"))
                connection.execute(text("SELECT set_config('app.user_id', :value, true)"), {"value": str(users["admin"])})
                connection.execute(text("SELECT set_config('app.tenant_id', :value, true)"), {"value": str(tenant_id)})
                for role, user_id in users.items():
                    user_insert = pg_insert(users_table).values(
                        id=user_id,
                        email=tenant_emails[role],
                        password_hash=hash_password(password),
                    )
                    connection.execute(
                        user_insert.on_conflict_do_update(
                            index_elements=[users_table.c.id],
                            set_={
                                "email": user_insert.excluded.email,
                                "password_hash": user_insert.excluded.password_hash,
                            },
                        )
                    )
                connection.execute(text("INSERT INTO tenants(id,name) VALUES (:id,:name) ON CONFLICT DO NOTHING"), {"id": tenant_id, "name": tenant_name})
                connection.execute(text("INSERT INTO permissions(code) VALUES ('members:manage') ON CONFLICT DO NOTHING"))
                for role, user_id in users.items():
                    connection.execute(text("INSERT INTO memberships(tenant_id,user_id) VALUES (:tenant,:user) ON CONFLICT DO NOTHING"), {"tenant": tenant_id, "user": user_id})
                    connection.execute(text("INSERT INTO roles(id,tenant_id,name) VALUES (:id,:tenant,:name) ON CONFLICT DO NOTHING"), {"id": roles[role], "tenant": tenant_id, "name": role})
                    connection.execute(text("INSERT INTO membership_roles(tenant_id,user_id,role_id) VALUES (:tenant,:user,:role) ON CONFLICT DO NOTHING"), {"tenant": tenant_id, "user": user_id, "role": roles[role]})
                connection.execute(text("INSERT INTO role_permissions(tenant_id,role_id,permission_code) VALUES (:tenant,:role,'members:manage') ON CONFLICT DO NOTHING"), {"tenant": tenant_id, "role": roles["admin"]})
                connection.execute(text("INSERT INTO experiments(id,tenant_id,creator_id,name,status) VALUES (:id,:tenant,:user,:name,'completed') ON CONFLICT DO NOTHING"), {"id": experiment_id, "tenant": tenant_id, "user": users["admin"], "name": f"{tenant_name} baseline"})
                for day in range(DASHBOARD_DAYS):
                    created_at = datetime.now(UTC) - timedelta(days=day)
                    dashboard_experiment = fixture_id(f"tenant/{slug}/dashboard/experiment/{day}")
                    dashboard_result = fixture_id(f"tenant/{slug}/dashboard/result/{day}")
                    dashboard_metric = fixture_id(f"tenant/{slug}/dashboard/metric/{day}")
                    experiment_status = ("completed", "running", "failed", "draft")[day % 4]
                    connection.execute(text("""INSERT INTO experiments(id,tenant_id,creator_id,name,status,created_at,updated_at)
                        VALUES (:id,:tenant,:user,:name,:status,:created,:created) ON CONFLICT DO NOTHING"""), {"id": dashboard_experiment, "tenant": tenant_id, "user": users["admin"], "name": f"{tenant_name} dashboard {day + 1:03d}", "status": experiment_status, "created": created_at})
                    if experiment_status != "draft":
                        result_status = "failed" if experiment_status == "failed" else "completed"
                        connection.execute(text("""INSERT INTO results(id,tenant_id,experiment_id,creator_id,status,input_summary,output_summary,created_at)
                            VALUES (:id,:tenant,:experiment,:user,:status,'dashboard input','dashboard output',:created) ON CONFLICT DO NOTHING"""), {"id": dashboard_result, "tenant": tenant_id, "experiment": dashboard_experiment, "user": users["member"], "status": result_status, "created": created_at})
                        connection.execute(text("""INSERT INTO metrics(id,tenant_id,result_id,creator_id,name,value_type,number_value,step,recorded_at)
                            VALUES (:id,:tenant,:result,:user,'dashboard_score','number',:value,:step,:created) ON CONFLICT DO NOTHING"""), {"id": dashboard_metric, "tenant": tenant_id, "result": dashboard_result, "user": users["member"], "value": round(0.5 + day / 200, 3), "step": day, "created": created_at})
                connection.execute(text("INSERT INTO results(id,tenant_id,experiment_id,creator_id,status,input_summary,output_summary) VALUES (:id,:tenant,:experiment,:user,'completed','deterministic input','deterministic output') ON CONFLICT DO NOTHING"), {"id": result_id, "tenant": tenant_id, "experiment": experiment_id, "user": users["member"]})
                metric_values = (
                    ("number", {"number": 0.91}), ("text", {"text_value": "accepted"}),
                    ("boolean", {"boolean": True}), ("json", {"json_value": '{"fold": 1}'}),
                )
                for index, (kind, value) in enumerate(metric_values):
                    params = {"id": fixture_id(f"tenant/{slug}/metric/{kind}"), "tenant": tenant_id, "result": result_id,
                              "user": users["member"], "name": f"fixture_{kind}", "kind": kind,
                              "number": None, "text_value": None, "boolean": None, "json_value": None} | value
                    connection.execute(text("""INSERT INTO metrics(id,tenant_id,result_id,creator_id,name,value_type,number_value,text_value,boolean_value,json_value,step)
                        VALUES (:id,:tenant,:result,:user,:name,:kind,:number,:text_value,:boolean,CAST(:json_value AS jsonb),:step) ON CONFLICT DO NOTHING"""), params | {"step": index})
                connection.execute(text("""INSERT INTO documents(id,tenant_id,created_by,name,object_key,ingestion_status,content_type,size_bytes,sha256)
                    VALUES (:id,:tenant,:user,'demo-security-fixture.txt',:key,'ready','text/plain',:size,:digest) ON CONFLICT DO NOTHING"""),
                    {"id": document_id, "tenant": tenant_id, "user": users["member"], "key": object_key, "size": len(data), "digest": sha256(data).hexdigest()})
                connection.execute(text("INSERT INTO chunks(id,tenant_id,document_id,content,ordinal,active) VALUES (:id,:tenant,:document,:content,0,true) ON CONFLICT DO NOTHING"), {"id": chunk_id, "tenant": tenant_id, "document": document_id, "content": content})
                connection.execute(text("INSERT INTO embeddings(id,tenant_id,chunk_id,embedding) VALUES (:id,:tenant,:chunk,CAST(:embedding AS vector)) ON CONFLICT DO NOTHING"), {"id": fixture_id(f"tenant/{slug}/embedding"), "tenant": tenant_id, "chunk": chunk_id, "embedding": str(embedder.embed(content, "passage"))})

    client = Minio(settings.minio_endpoint, settings.minio_access_key, settings.minio_secret_key, secure=False)
    for object_key, data in objects:
        client.put_object(settings.minio_bucket, object_key, BytesIO(data), len(data), content_type="text/plain")
    print("Seeded 2 tenants, 6 identities, and isolated relational/vector/object fixtures.")


if __name__ == "__main__":
    seed()
