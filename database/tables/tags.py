from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.base import Base
from database.tables.association_tables import artist_tag_association


class TagORM(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    artists = relationship(
        "ArtistORM", secondary=artist_tag_association, back_populates="tags"
    )
