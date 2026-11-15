"""simulacros del PCAP verificados por el servidor

Revision ID: d5e9f1a3b7c2
Revises: 8a2f6c4d9b10
Create Date: 2026-11-15 06:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5e9f1a3b7c2"
down_revision: str | Sequence[str] | None = "8a2f6c4d9b10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Tabla nueva y vacía: no toca ningún dato que ya exista."""
    op.create_table(
        "verified_exams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exam_code", sa.String(length=20), nullable=False),
        sa.Column("question_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=10), server_default="open", nullable=False),
        sa.Column("answers", sa.JSON(), nullable=True),
        sa.Column("correct", sa.Integer(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_verified_exams_user_started", "verified_exams", ["user_id", "started_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_verified_exams_user_started", table_name="verified_exams")
    op.drop_table("verified_exams")
