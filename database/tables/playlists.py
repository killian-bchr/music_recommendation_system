from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base
from database.tables.association_tables import playlist_track_association


class PlaylistORM(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_id = Column(String, unique=True)

    tracks = relationship(
        "TrackORM", secondary=playlist_track_association, back_populates="playlists"
    )
