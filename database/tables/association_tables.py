from sqlalchemy import Column, ForeignKey, Table
from database.base import Base

track_artist_association = Table(
    "track_artist",
    Base.metadata,
    Column("track_id", ForeignKey("tracks.id"), primary_key=True),
    Column("artist_id", ForeignKey("artists.id"), primary_key=True)
)

artist_tag_association = Table(
    "artist_tag",
    Base.metadata,
    Column("artist_id", ForeignKey("artists.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)

similar_artist_association = Table(
    "similar_artist",
    Base.metadata,
    Column("artist_id", ForeignKey("artists.id"), primary_key=True),
    Column("similar_id", ForeignKey("artists.id"), primary_key=True)
)

playlist_track_association = Table(
    "playlist_track",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlists.id"), primary_key=True),
    Column("track_id", ForeignKey("tracks.id"), primary_key=True)
)

artist_album_association = Table(
    "artist_album_association",
    Base.metadata,
    Column("artist_id", ForeignKey("artists.id"), primary_key=True),
    Column("album_id", ForeignKey("albums.id"), primary_key=True),
)
