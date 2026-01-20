from enum import Enum


class Methods(Enum):
    pass


class TrackMethods(Methods):
    TRACK_DETAILS = "track.getInfo"
    SIMILAR_TRACKS = "track.getSimilar"
    TRACK_TAGS = "track.getTopTags"
    SEARCH_TRACK = "track.search"


class ArtistMethods(Methods):
    SIMILAR_ARTISTS = "artist.getSimilar"
    TOP_TRACKS = "artist.getTopTracks"
    TOP_ALBUMS = "artist.getTopAlbums"
    ARTIST_TAGS = "artist.getTags"
    SEARCH_ARTIST = "artist.search"
    ARTIST_DETAILS = "artist.getInfo"


class AlbumMethods(Methods):
    ALBUM_DETAILS = "album.getInfo"
    ALBUM_TAGS = "album.getTopTags"
    SEARCH_ALBUM = "album.search"


class TagMethods(Methods):
    TAG_DETAILS = "tag.getInfo"
    TAG_TOP_ARTISTS = "tag.getTopArtists"
    TAG_TOP_ALBUMS = "tag.getTopAlbums"
    TAG_TOP_TRACKS = "tag.getTopTracks"


class TrendMethods(Methods):
    TREND_TOP_ARTISTS = "chart.getTopArtists"
    TREND_TOP_ALBUMS = "chart.getTopTracks"
    TREND_TOP_TAGS = "chart.getTopTags"


class NodeType(str, Enum):
    ALBUM = "album"
    ARTIST = "artist"
    TAG = "tag"
    TRACK = "track"


class RelationType(str, Enum):
    ALBUM_ALBUM = "album_album"
    ALBUM_ARTIST = "album_artist"
    TRACK_ARTIST = "track_artist"
    TRACK_ALBUM = "track_album"
    ARTIST_ARTIST = "artist_artist"
    ARTIST_TAG = "artist_tag"
    TAG_TAG = "tag_tag"


class NodeColor(str, Enum):
    GREEN = "tab:green"  # noqa: E231
    ORANGE = "tab:orange"  # noqa: E231
    BLUE = "tab:blue"  # noqa: E231
    RED = "tab:red"  # noqa: E231


class MarkovStrategy(str, Enum):
    BALANCED = "balanced"
    EXPLORATION = "exploration"


class RandomWalkStrategy(str, Enum):
    POWER_ITERATION = "power iteration"
    MONTE_CARLO = "monte carlo"
