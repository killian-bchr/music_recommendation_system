from enum import Enum


class NodeType(str, Enum):
    ALBUM = "album"
    ARTIST = "artist"
    TAG = "tag"
    TRACK = "track"


class RelationType(str, Enum):
    ALBUM_ARTIST = "album_artist"
    TRACK_ARTIST = "track_artist"
    TRACK_ALBUM = "track_album"
    ARTIST_ARTIST = "artist_artist"
    ARTIST_TAG = "artist_tag"
    TAG_TAG = "tag_tag"
