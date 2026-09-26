"""preparacion pcap

Revision ID: e6a4c5c96c2a
Revises: c8f7da35ecbb
Create Date: 2026-09-27 00:38:24.854225

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e6a4c5c96c2a"
down_revision: str | Sequence[str] | None = "c8f7da35ecbb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Preparación del PCAP guardada en la cuenta (ADR-0010)."""
    op.create_table(
        "pcap_states",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("pcap_states")
