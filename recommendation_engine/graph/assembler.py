from collections import defaultdict
from itertools import combinations
from typing import List

from database.db_env import DBEnv
from database.session import get_session
from helpers.db_helpers import DBHelpers
from recommendation_engine.constants import NodeType
from recommendation_engine.graph.builder import GraphBuilder


class GraphAssembler(GraphBuilder):
    def __init__(self, env: DBEnv = DBEnv.EXP, auto_load: bool = True):
        super().__init__()
        self.env = env
        self.tracks = []
        self.artists = []
        self.tags = []
        self.albums = []
        if auto_load:
            self.load_data()

    def load_data(self) -> None:
        with get_session(self.env) as session:
            self.tracks = DBHelpers.fetch_all_tracks(session)
            self.artists = DBHelpers.fetch_all_artists(session)
            self.tags = DBHelpers.fetch_all_tags(session)
            self.albums = DBHelpers.fetch_all_albums(session)

    def add_nodes(self, items: List, node_type: NodeType) -> None:
        for item in items:
            node = self.build_node(node_type, item.id)
            self.add_node(node)

    def assemble_nodes(self) -> None:
        self.add_nodes(self.tracks, NodeType.TRACK)
        self.add_nodes(self.artists, NodeType.ARTIST)
        self.add_nodes(self.albums, NodeType.ALBUM)
        self.add_nodes(self.tags, NodeType.TAG)

    def add_album_edges(self) -> None:
        artist_to_albums = defaultdict(list)

        for album in self.albums:
            for artist in album.artists:
                artist_to_albums[artist.id].append(album.id)

                edge = self.build_edge(
                    nodes=(
                        self.build_node(NodeType.ALBUM, album.id),
                        self.build_node(NodeType.ARTIST, artist.id),
                    ),
                )
                self.add_edge(edge)

        for _, album_ids in artist_to_albums.items():
            for i, j in combinations(album_ids, 2):
                edge = self.build_edge(
                    nodes=(
                        self.build_node(NodeType.ALBUM, i),
                        self.build_node(NodeType.ALBUM, j),
                    ),
                )
                self.add_edge(edge)

    def add_track_edges(self) -> None:
        for track in self.tracks:
            for artist in track.artists:
                edge = self.build_edge(
                    node=(
                        self.build_node(NodeType.TRACK, track.id),
                        self.build_node(NodeType.ARTIST, artist.id),
                    ),
                )
                self.add_edge(edge)

            edge = self.build_edge(
                nodes=(
                    self.build_node(NodeType.TRACK, track.id),
                    self.build_node(NodeType.ALBUM, track.album.id),
                ),
            )
            self.add_edge(edge)

    def add_artist_edges(self) -> None:
        for artist in self.artists:
            for similar_artist in artist.similar_artists:
                edge = self.build_edge(
                    nodes=(
                        self.build_node(NodeType.ARTIST, artist.id),
                        self.build_node(NodeType.ARTIST, similar_artist.id),
                    ),
                )
                self.add_edge(edge)

            for tag in artist.tags:
                edge = self.build_edge(
                    nodes=(
                        self.build_node(NodeType.ARTIST, artist.id),
                        self.build_node(NodeType.TAG, tag.id),
                    ),
                )
                self.add_edge(edge)

    def add_tag_edges(self) -> None:
        artists_to_tags = defaultdict(list)

        for tag in self.tags:
            for artist in tag.artists:
                artists_to_tags[artist.id].append(tag.id)

        for _, tag_ids in artists_to_tags.items():
            for i, j in combinations(tag_ids, 2):
                edge = self.build_edge(
                    nodes=(
                        self.build_node(NodeType.TAG, i),
                        self.build_node(NodeType.TAG, j),
                    ),
                )
                self.add_edge(edge)

    def assemble_edges(self) -> None:
        self.add_album_edges()
        self.add_track_edges()
        self.add_artist_edges()
        self.add_tag_edges()

    def assemble_graph(self) -> None:
        self.assemble_nodes()
        self.assemble_edges()
