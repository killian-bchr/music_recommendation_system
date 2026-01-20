import numpy as np
from numpy import ndarray

from recommendation_engine.markov.random_walk.base import RandomWalkBase


class PowerIterationRW(RandomWalkBase):
    def __init__(
        self,
        P: ndarray,
        pi0: ndarray,
        alpha: float = 0.15,
        tol: float = 1e-6,
        max_iter: int = 1000,
    ):
        self.P = P
        self.pi0 = pi0
        self.alpha = alpha
        self.tol = tol
        self.max_iter = max_iter

    def run(self) -> ndarray:
        pi = self.pi0.copy()

        for _ in range(self.max_iter):
            pi_next = self.alpha * self.pi0 + (1 - self.alpha) * pi @ self.P
            if np.linalg.norm(pi_next - pi, ord=1) < self.tol:
                break
            pi = pi_next

        return pi
