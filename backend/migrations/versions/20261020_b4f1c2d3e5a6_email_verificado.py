"""email verificado

Revision ID: b4f1c2d3e5a6
Revises: 7c3e9a1d4b20
Create Date: 2026-10-20 03:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b4f1c2d3e5a6"
down_revision: str | Sequence[str] | None = "7c3e9a1d4b20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cuándo se probó que el email es del usuario (Google o recuperación). Columna nueva y
    vacía: no cambia ningún dato existente."""
    op.add_column(
        "users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "email_verified_at")
