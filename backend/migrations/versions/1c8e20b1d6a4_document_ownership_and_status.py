"""add document ownership and processing status

Revision ID: 1c8e20b1d6a4
Revises: 0921f114f64e
"""

from alembic import op
import sqlalchemy as sa

revision = "1c8e20b1d6a4"
down_revision = "0921f114f64e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("processing_status", sa.String(length=30), server_default="completed", nullable=False))
    op.create_foreign_key("fk_documents_user_id_users", "documents", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_processing_status", "documents", ["processing_status"])


def downgrade() -> None:
    op.drop_index("ix_documents_processing_status", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_constraint("fk_documents_user_id_users", "documents", type_="foreignkey")
    op.drop_column("documents", "processing_status")
    op.drop_column("documents", "user_id")
