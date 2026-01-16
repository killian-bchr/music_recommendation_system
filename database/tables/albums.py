from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base
from database.tables.association_tables import artist_album_association


class AlbumORM(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_id = Column(String, unique=True)
    name = Column(String)
    release_date = Column(String)

    tracks = relationship("TrackORM", back_populates="album")

    artists = relationship(
        "ArtistORM", secondary=artist_album_association, back_populates="albums"
    )
