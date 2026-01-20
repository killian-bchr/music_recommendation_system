from typing import List, Tuple

from database.db_env import DBEnv
from database.session import get_session
from helpers import DBHelpers
from recommendation_engine.graph import GraphAssembler
from recommendation_engine.markov import MarkovKernel, RandomWalkFactory
from settings.constants import MarkovStrategy, NodeType, RandomWalkStrategy


class MarkovRecommender:
    def __init__(
        self,
        markov_strategy: MarkovStrategy = MarkovStrategy.BALANCED,
        walk_strategy: RandomWalkStrategy = RandomWalkStrategy.POWER_ITERATION,
        n_last_listenings: int = 3,
        env: DBEnv = DBEnv.EXP,
    ):
        self.env = env
        self.markov_strategy = markov_strategy
        self.walk_strategy = walk_strategy
        self.n_last_listenings = n_last_listenings

        self.graph_assembler = GraphAssembler(self.env)
        self.graph_assembler.assemble_graph()
        self.G = self.graph_assembler.G

        self.kernel = MarkovKernel(self.G, self.markov_strategy)
        self.P = self.kernel.build_kernel()
        self.index = self.kernel.index

    def get_seed_nodes(self) -> List[str]:
        with get_session(self.env) as session:
            listenings = DBHelpers.fetch_last_tracks_listened(
                session,
                n_listenings=self.n_last_listenings,
            )

        seed_nodes = [
            self.graph_assembler.build_node(NodeType.TRACK, listening.id)
            for listening in listenings
        ]

        return [seed.name for seed in seed_nodes]

    def compute_scores(self) -> Tuple[List[str], List[Tuple[str, float]]]:
        seed_nodes = self.get_seed_nodes()

        rw = RandomWalkFactory.create(
            self.walk_strategy,
            self.P,
            self.index,
            seed_nodes,
        )

        scores = rw.run()
        return seed_nodes, scores

    def get_track_id_from_node(self, node_name: str) -> int:
        return int(node_name.split(":")[1])

    def recommend(self, top_k: int = 10) -> List[int]:
        seed_nodes, scores = self.compute_scores()

        recommendations = []

        for i, score in enumerate(scores):
            node = self.index.idx_to_node[i]

            if node in seed_nodes:
                continue

            if self.G.nodes[node]["type"] != NodeType.TRACK.value:
                continue

            recommendations.append((node, score))

        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        return [self.get_track_id_from_node(x[0]) for x in sorted_recommendations]
