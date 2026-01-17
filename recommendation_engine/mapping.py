from recommendation_engine.constants import NodeType, RelationType
from recommendation_engine.relation import Relation

AUTHORIZED_RELATIONS = {
    (NodeType.ALBUM, NodeType.ARTIST): Relation(RelationType.ALBUM_ARTIST),
    (NodeType.TRACK, NodeType.ARTIST): Relation(RelationType.TRACK_ARTIST),
    (NodeType.TRACK, NodeType.ALBUM): Relation(RelationType.TRACK_ALBUM),
    (NodeType.ARTIST, NodeType.ARTIST): Relation(RelationType.ARTIST_ARTIST),
    (NodeType.ARTIST, NodeType.TAG): Relation(RelationType.ARTIST_TAG),
    (NodeType.TAG, NodeType.TAG): Relation(RelationType.TAG_TAG),
}
