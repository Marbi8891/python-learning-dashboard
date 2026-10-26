"""quitar el tutor

Revision ID: e1a2b3c4d5f6
Revises: d7e2a9c4f1b8
Create Date: 2026-10-26 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e1a2b3c4d5f6"
down_revision: str | Sequence[str] | None = "d7e2a9c4f1b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """El tutor se ha quitado del proyecto, así que su tabla ya no hace falta."""
    op.drop_index("ix_tutor_usage_day_mode", table_name="tutor_usage")
    op.drop_table("tutor_usage")


def downgrade() -> None:
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
