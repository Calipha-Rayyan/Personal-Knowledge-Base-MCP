"""add document status, error_message, created_at, updated_at

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-30

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("status", sa.String(20), nullable=False, server_default="indexed"),
    )
    op.add_column("documents", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column(
        "documents",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "documents",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Backfill created_at/updated_at from the existing uploaded_at column
    # for any rows that already exist, so nothing shows NULL timestamps.
    op.execute(
        "UPDATE documents SET created_at = uploaded_at, updated_at = uploaded_at "
        "WHERE created_at IS NULL"
    )


def downgrade() -> None:
    op.drop_column("documents", "updated_at")
    op.drop_column("documents", "created_at")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "status")