from typing import List

from numpy import ndarray

from recommendation_engine.markov.initial_distribution import InitialDistributionBuilder
from recommendation_engine.markov.node_index import NodeIndex
from recommendation_engine.markov.random_walk.base import RandomWalkBase
from recommendation_engine.markov.random_walk.monte_carlo import MonteCarloRW
from recommendation_engine.markov.random_walk.power_iteration import PowerIterationRW
from settings.constants import RandomWalkStrategy


class RandomWalkFactory:
    @staticmethod
    def create(
        method: RandomWalkStrategy,
        P: ndarray,
        index: NodeIndex,
        seeds: List[str],
        **kwargs,
    ) -> RandomWalkBase:
        if method == RandomWalkStrategy.POWER_ITERATION:
            pi0 = InitialDistributionBuilder(seeds, index).build()
            return PowerIterationRW(P, pi0)

        if method == RandomWalkStrategy.MONTE_CARLO:
            return MonteCarloRW(P, index, seeds, kwargs.get("steps", 1000))

        raise ValueError(f"Unknown method {method}")
