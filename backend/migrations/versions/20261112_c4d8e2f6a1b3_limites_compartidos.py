"""límites de intentos compartidos entre instancias

Revision ID: c4d8e2f6a1b3
Revises: a9c3e5f7b1d2
Create Date: 2026-11-12 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4d8e2f6a1b3"
down_revision: str | Sequence[str] | None = "a9c3e5f7b1d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Tabla nueva y vacía: no toca ningún dato que ya exista."""
    op.create_table(
        "rate_limits",
        sa.Column("scope", sa.String(length=20), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("window_start", sa.BigInteger(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("scope", "key", "window_start"),
    )


def downgrade() -> None:
    op.drop_table("rate_limits")
