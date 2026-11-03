"""versión de los documentos de progreso

Revision ID: a9c3e5f7b1d2
Revises: e1a2b3c4d5f6
Create Date: 2026-11-02 12:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a9c3e5f7b1d2"
down_revision: str | Sequence[str] | None = "e1a2b3c4d5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = ("pcap_states", "course_states")


def upgrade() -> None:
    """Contador de versión para no pisar lo guardado desde otra pestaña o dispositivo. Columna nueva
    con valor 0 en las filas que ya existen: no cambia ningún dato."""
    for table in TABLES:
        op.add_column(
            table,
            sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("0")),
        )


def downgrade() -> None:
    for table in TABLES:
        op.drop_column(table, "version")
