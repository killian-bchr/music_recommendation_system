from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database.base import Base
from database.tables.association_tables import track_artist_association, playlist_track_association


class TrackORM(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_id = Column(String, unique=True)
    name = Column(String)
    duration = Column(Float)
    popularity = Column(Integer)
    spotify_url = Column(String)
    listeners = Column(Integer, nullable=True)
    playcount = Column(Integer, nullable=True)

    album_id = Column(Integer, ForeignKey("albums.id"))
    album = relationship("AlbumORM", back_populates="tracks")

    artists = relationship("ArtistORM", secondary=track_artist_association, backref="tracks")

    playlists = relationship(
        "PlaylistORM",
        secondary=playlist_track_association,
        back_populates="tracks"
    )
