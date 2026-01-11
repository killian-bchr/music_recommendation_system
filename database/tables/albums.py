from sqlalchemy import Column, Integer, String

from database.base import Base


class AlbumORM(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_id = Column(String, unique=True)
    name = Column(String)
    release_date = Column(String)
