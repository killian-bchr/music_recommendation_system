from abc import ABC, abstractmethod

from numpy import ndarray


class RandomWalkBase(ABC):
    @abstractmethod
    def run(self) -> ndarray:
        pass
