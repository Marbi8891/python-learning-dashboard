"""recuperar el tutor

Revision ID: f3c8d1a7b2e9
Revises: e1a2b3c4d5f6
Create Date: 2026-10-29 10:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3c8d1a7b2e9"
down_revision: str | Sequence[str] | None = "e1a2b3c4d5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Vuelve el tutor híbrido: consultas por usuario, día y modalidad (cuotas de la IA)."""
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
