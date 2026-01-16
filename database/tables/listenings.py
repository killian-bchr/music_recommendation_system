from sqlalchemy import JSON, Column, Float, Integer, String

from database.base import Base


class ListeningORM(Base):
    __tablename__ = "listenings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    played_at = Column(String, unique=True)
    track_id = Column(String)
    track_name = Column(String)
    track_artists = Column(JSON)
    album_id = Column(String)
    album_name = Column(String)
    album_artists = Column(JSON)
    duration = Column(Float)
    popularity = Column(Integer)
    spotify_url = Column(String)
    release_date = Column(String)
    image_url = Column(String)
