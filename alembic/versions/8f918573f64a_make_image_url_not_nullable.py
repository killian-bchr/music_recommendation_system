"""make image_url not nullable

Revision ID: 8f918573f64a
Revises: b582b1098169
Create Date: 2026-01-21 00:04:50.614163

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f918573f64a"
down_revision: Union[str, Sequence[str], None] = "b582b1098169"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("tracks") as batch_op:
        batch_op.alter_column(
            "image_url",
            existing_type=sa.String(),
            nullable=False,
        )

    with op.batch_alter_table("albums") as batch_op:
        batch_op.alter_column(
            "image_url",
            existing_type=sa.String(),
            nullable=False,
        )


def downgrade():
    with op.batch_alter_table("tracks") as batch_op:
        batch_op.alter_column(
            "image_url",
            existing_type=sa.String(),
            nullable=True,
        )

    with op.batch_alter_table("albums") as batch_op:
        batch_op.alter_column(
            "image_url",
            existing_type=sa.String(),
            nullable=True,
        )
