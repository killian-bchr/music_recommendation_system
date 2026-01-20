from typing import List

from numpy import ndarray

from recommendation_engine.markov.initial_distribution import InitialDistributionBuilder
from recommendation_engine.markov.node_index import NodeIndex
from recommendation_engine.markov.random_walk.base import RandomWalkBase
from recommendation_engine.markov.random_walk.monte_carlo import MonteCarloRW
from recommendation_engine.markov.random_walk.power_iteration import PowerIterationRW
from settings.config_loader import load_random_walk_parameters
from settings.constants import RandomWalkStrategy

RW_CONFIG = load_random_walk_parameters()


class RandomWalkFactory:
    @staticmethod
    def create(
        method: RandomWalkStrategy,
        P: ndarray,
        index: NodeIndex,
        seeds: List[str],
    ) -> RandomWalkBase:
        if method == RandomWalkStrategy.POWER_ITERATION:
            cfg = RW_CONFIG[RandomWalkStrategy.POWER_ITERATION]
            pi0 = InitialDistributionBuilder(seeds, index).build()

            return PowerIterationRW(
                P=P,
                pi0=pi0,
                alpha=cfg["alpha"],
                tol=cfg["tol"],
                max_iter=cfg["max_iter"],
            )

        if method == RandomWalkStrategy.MONTE_CARLO:
            cfg = RW_CONFIG[RandomWalkStrategy.MONTE_CARLO]

            return MonteCarloRW(
                P=P,
                index=index,
                seed_nodes=seeds,
                steps=cfg["steps"],
            )

        raise ValueError(f"Unknown method {method}")
