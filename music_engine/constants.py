class MethodsAPILastFM:
    """Base class for LastFM API method groups."""
    pass


class ArtistMethods(MethodsAPILastFM):
    """Methods related to artist endpoints."""
    TOP_TRACKS = 'artist.getTopTracks'
    TOP_ALBUMS = 'artist.getTopAlbums'
    SIMILAR_ARTISTS = 'artist.getSimilar'
    TAGS = 'artist.getTags'
    INFO = 'artist.getInfo'
    SEARCH = 'artist.search'


class AlbumMethods(MethodsAPILastFM):
    """Methods related to album endpoints."""
    INFO = 'album.getInfo'
    TOP_TAGS = 'album.getTopTags'
    SEARCH = 'album.search'


class TrackMethods(MethodsAPILastFM):
    """Methods related to track endpoints."""
    INFO = 'track.getInfo'
    SIMILAR_TRACKS = 'track.getSimilar'
    TOP_TAGS = 'track.getTopTags'
    SEARCH = 'track.search'


class TrendMethods(MethodsAPILastFM):
    """Methods related to trend endpoints."""
    TOP_ARTISTS = 'chart.getTopArtists'
    TOP_TRACKS = 'chart.getTopTracks'
    TOP_TAGS = 'chart.getTopTags'


class TagsMethods(MethodsAPILastFM):
    """Methods related to tag endpoints."""
    INFO = 'tag.getInfo'
    TOP_ARTISTS = 'tag.getTopArtists'
    TOP_ALBUMS = 'tag.getTopAlbums'
    TOP_TRACKS = 'tag.getTopTracks'
