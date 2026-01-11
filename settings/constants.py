from enum import Enum


class Methods(Enum):
    pass


class TrackMethods(Methods):
    TRACK_DETAILS = 'track.getInfo'
    SIMILAR_TRACKS = 'track.getSimilar'
    TRACK_TAGS = 'track.getTopTags'
    SEARCH_TRACK = 'track.search'


class ArtistMethods(Methods):
    SIMILAR_ARTISTS = 'artist.getSimilar'
    TOP_TRACKS = 'artist.getTopTracks'
    TOP_ALBUMS = 'artist.getTopAlbums'
    ARTIST_TAGS = 'artist.getTags'
    SEARCH_ARTIST = 'artist.search'
    ARTIST_DETAILS = 'artist.getInfo'


class AlbumMethods(Methods):
    ALBUM_DETAILS = 'album.getInfo'
    ALBUM_TAGS = 'album.getTopTags'
    SEARCH_ALBUM = 'album.search'


class TagMethods(Methods):
    TAG_DETAILS = 'tag.getInfo'
    TAG_TOP_ARTISTS = 'tag.getTopArtists'
    TAG_TOP_ALBUMS = 'tag.getTopAlbums'
    TAG_TOP_TRACKS = 'tag.getTopTracks'


class TrendMethods(Methods):
    TREND_TOP_ARTISTS = 'chart.getTopArtists'
    TREND_TOP_ALBUMS = 'chart.getTopTracks'
    TREND_TOP_TAGS = 'chart.getTopTags'
