"""estado de cursos

Revision ID: 5b1d2f8c9a31
Revises: e6a4c5c96c2a
Create Date: 2026-09-27 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5b1d2f8c9a31"
down_revision: str | Sequence[str] | None = "e6a4c5c96c2a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Estado de los cursos de DAW de la app Android guardado en la cuenta (ADR-0018)."""
    op.create_table(
        "course_states",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course", sa.String(length=20), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "course"),
    )


def downgrade() -> None:
    op.drop_table("course_states")
