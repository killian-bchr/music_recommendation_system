from models import Relation
from settings.constants import NodeColor, NodeType, RelationType

AUTHORIZED_RELATIONS = {
    (NodeType.ALBUM, NodeType.ALBUM): Relation(RelationType.ALBUM_ALBUM),
    (NodeType.ALBUM, NodeType.ARTIST): Relation(RelationType.ALBUM_ARTIST),
    (NodeType.TRACK, NodeType.ARTIST): Relation(RelationType.TRACK_ARTIST),
    (NodeType.TRACK, NodeType.ALBUM): Relation(RelationType.TRACK_ALBUM),
    (NodeType.ARTIST, NodeType.ARTIST): Relation(RelationType.ARTIST_ARTIST),
    (NodeType.ARTIST, NodeType.TAG): Relation(RelationType.ARTIST_TAG),
    (NodeType.TAG, NodeType.TAG): Relation(RelationType.TAG_TAG),
}

NODE_COLORS = {
    NodeType.ALBUM.value: NodeColor.GREEN.value,
    NodeType.ARTIST.value: NodeColor.ORANGE.value,
    NodeType.TRACK.value: NodeColor.BLUE.value,
    NodeType.TAG.value: NodeColor.RED.value,
}

NODE_SIZES = {
    NodeType.ALBUM.value: 80,
    NodeType.ARTIST.value: 80,
    NodeType.TRACK.value: 80,
    NodeType.TAG.value: 80,
}
