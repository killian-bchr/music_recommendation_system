"""add image_url to album and track

Revision ID: b582b1098169
Revises: 5cc80cf11cc2
Create Date: 2026-01-20 23:39:38.695368

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b582b1098169"
down_revision: Union[str, Sequence[str], None] = "5cc80cf11cc2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Upgrade schema."""
    op.add_column("albums", sa.Column("image_url", sa.Text(), nullable=True))
    op.add_column("tracks", sa.Column("image_url", sa.Text(), nullable=True))

    connection = op.get_bind()

    result = connection.execute(text("""
        SELECT DISTINCT a.id, l.image_url
        FROM albums a
        JOIN tracks t ON t.album_id = a.id
        JOIN listenings l ON l.track_id = t.spotify_id
        WHERE l.image_url IS NOT NULL
    """))

    for album_id, image_url in result:
        connection.execute(
            text("UPDATE albums SET image_url = ? WHERE id = ?"), (image_url, album_id)
        )

    result = connection.execute(text("""
        SELECT DISTINCT t.id, l.image_url
        FROM tracks t
        JOIN listenings l ON l.track_id = t.spotify_id
        WHERE l.image_url IS NOT NULL
    """))

    for track_id, image_url in result:
        connection.execute(
            text("UPDATE tracks SET image_url = ? WHERE id = ?"), (image_url, track_id)
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tracks", "image_url")
    op.drop_column("albums", "image_url")
