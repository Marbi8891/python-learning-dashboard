"""actividad de la cuenta

Revision ID: 7c3e9a1d4b20
Revises: 5b1d2f8c9a31
Create Date: 2026-09-30 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7c3e9a1d4b20"
down_revision: str | Sequence[str] | None = "5b1d2f8c9a31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Actividad de seguridad visible para el usuario en «Mi cuenta» (ADR-0025)."""
    op.create_table(
        "account_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("device", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_account_events_user_id", "account_events", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_account_events_user_id", table_name="account_events")
    op.drop_table("account_events")
