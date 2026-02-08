"""init pasto entries

Revision ID: 0001_init
Revises: 
Create Date: 2026-02-08 00:00:01

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = "20260208_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pasto_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("uuid", sa.Uuid(as_uuid=True), nullable=False, unique=True),
        sa.Column("lot_number", sa.String(length=100), nullable=False),
        sa.Column("entry_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exit_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("device_id", sa.String(length=128), nullable=True),
        sa.Column("updated_seq", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.create_index("ix_pasto_entries_uuid", "pasto_entries", ["uuid"], unique=True)
    op.create_index("ix_pasto_entries_device_id", "pasto_entries", ["device_id"])
    op.create_index("ix_pasto_entries_updated_seq", "pasto_entries", ["updated_seq"])
    op.create_index("ix_pasto_entries_deleted_at", "pasto_entries", ["deleted_at"])

    op.create_table(
        "pasto_entry_photos",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("uuid", sa.Uuid(as_uuid=True), nullable=False, unique=True),
        sa.Column(
            "entry_uuid",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("pasto_entries.uuid"),
            nullable=False,
        ),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("size", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_pasto_entry_photos_entry_uuid", "pasto_entry_photos", ["entry_uuid"]
    )


def downgrade() -> None:
    op.drop_index("ix_pasto_entry_photos_entry_uuid", table_name="pasto_entry_photos")
    op.drop_table("pasto_entry_photos")
    op.drop_index("ix_pasto_entries_deleted_at", table_name="pasto_entries")
    op.drop_index("ix_pasto_entries_updated_seq", table_name="pasto_entries")
    op.drop_index("ix_pasto_entries_device_id", table_name="pasto_entries")
    op.drop_table("pasto_entries")
