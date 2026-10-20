"""uso del tutor

Revision ID: d7e2a9c4f1b8
Revises: b4f1c2d3e5a6
Create Date: 2026-10-20 08:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d7e2a9c4f1b8"
down_revision: str | Sequence[str] | None = "b4f1c2d3e5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Consultas al tutor por usuario, día y modalidad: cuotas de la IA avanzada (ADR-0038)."""
    op.create_table(
        "tutor_usage",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("mode", sa.String(length=10), nullable=False),
        sa.Column("requests", sa.Integer(), server_default="0", nullable=False),
        sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "day", "mode"),
    )
    op.create_index("ix_tutor_usage_day_mode", "tutor_usage", ["day", "mode"])


def downgrade() -> None:
    op.drop_index("ix_tutor_usage_day_mode", table_name="tutor_usage")
    op.drop_table("tutor_usage")
