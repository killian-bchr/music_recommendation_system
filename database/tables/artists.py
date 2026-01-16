from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base
from database.tables.association_tables import (
    artist_album_association,
    artist_tag_association,
    similar_artist_association,
)


class ArtistORM(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_id = Column(String, unique=True)
    name = Column(String)

    tags = relationship(
        "TagORM", secondary=artist_tag_association, back_populates="artists"
    )

    albums = relationship(
        "AlbumORM", secondary=artist_album_association, back_populates="artists"
    )

    similar_artists = relationship(
        "ArtistORM",
        secondary=similar_artist_association,
        primaryjoin=id == similar_artist_association.c.artist_id,
        secondaryjoin=id == similar_artist_association.c.similar_id,
        backref="similar_to",
    )
