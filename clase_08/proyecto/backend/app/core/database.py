"""Target-owned SQLAlchemy metadata for the tenant-safe MVP foundation."""

# pyright: reportMissingImports=false

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, MetaData, String, Table, Text, UniqueConstraint, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

runtime_engine = create_engine(settings.runtime_database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=runtime_engine, expire_on_commit=False)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("email", String(320), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
tenants = Table(
    "tenants", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String(120), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
memberships = Table(
    "memberships", metadata,
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("active", Boolean, nullable=False, server_default="true"),
)
Index("memberships_one_active_user", memberships.c.user_id, unique=True, postgresql_where=memberships.c.active)
roles = Table(
    "roles", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False),
    Column("name", String(32), nullable=False),
    UniqueConstraint("tenant_id", "name"),
)
permissions = Table(
    "permissions", metadata,
    Column("code", String(64), primary_key=True),
)
role_permissions = Table(
    "role_permissions", metadata,
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column("permission_code", String(64), ForeignKey("permissions.code"), primary_key=True),
)
experiments = Table(
    "experiments", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False),
    Column("creator_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("name", String(200), nullable=False), Column("status", String(16), nullable=False),
)
results = Table(
    "results", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False),
    Column("experiment_id", UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False),
    Column("creator_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("status", String(16), nullable=False), Column("summary", Text),
)
metrics = Table(
    "metrics", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False),
    Column("result_id", UUID(as_uuid=True), ForeignKey("results.id"), nullable=False),
    Column("name", String(120), nullable=False), Column("value_type", String(16), nullable=False),
    Column("number_value", Integer), Column("text_value", Text), Column("boolean_value", Boolean), Column("json_value", JSONB),
)
documents = Table(
    "documents", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False),
    Column("created_by", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("name", String(255), nullable=False), Column("object_key", String(255), nullable=False),
    Column("ingestion_status", String(16), nullable=False),
)
chunks = Table(
    "chunks", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False),
    Column("document_id", UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False),
    Column("content", Text, nullable=False), Column("ordinal", Integer, nullable=False),
)
embeddings = Table(
    "embeddings", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False),
    Column("chunk_id", UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=False),
    Column("embedding", JSONB, nullable=False),
)
sessions = Table("sessions", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False), Column("token_hash", String(64), nullable=False, unique=True), Column("csrf_hash", String(64), nullable=False), Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id")), Column("expires_at", DateTime(timezone=True), nullable=False), Column("revoked_at", DateTime(timezone=True)))
recovery_tokens = Table("recovery_tokens", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False), Column("token_hash", String(64), nullable=False, unique=True), Column("expires_at", DateTime(timezone=True), nullable=False), Column("used_at", DateTime(timezone=True)))
membership_roles = Table("membership_roles", metadata, Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True), Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True), Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False))
audit_events = Table("audit_events", metadata, Column("id", UUID(as_uuid=True), primary_key=True), Column("actor_id", UUID(as_uuid=True), ForeignKey("users.id")), Column("tenant_id", UUID(as_uuid=True), ForeignKey("tenants.id")), Column("action", String(64), nullable=False), Column("outcome", String(16), nullable=False), Column("resource", String(120)), Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()))
