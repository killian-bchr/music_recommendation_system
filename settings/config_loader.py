from typing import Dict, Optional

import yaml

from config import Config
from settings.constants import MarkovStrategy


def validate_type_transition_matrix(T: Dict[str, Dict[str, float]]) -> None:
    for src, targets in T.items():
        s = sum(targets.values())
        if abs(s - 1.0) > 1e-8:
            raise ValueError(f"Transition probabilities for '{src}' sum to {s}, not 1")


def load_markov_type_transition_matrix(
    strategy: Optional[MarkovStrategy] = None,
) -> Dict[str, Dict[str, float]]:
    path = Config.CONFIG_ROOT / "type_transition_probabilities.yaml"

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    markov_cfg = data["markov"]
    strategies = markov_cfg["strategies"]

    if strategy is None:
        strategy = MarkovStrategy(markov_cfg["default_strategy"])

    if strategy.value not in strategies:
        raise ValueError(f"Unknown strategy '{strategy}'")

    matrix = strategies[strategy.value]["type_transition_probabilities"]
    validate_type_transition_matrix(matrix)

    return matrix


def load_random_walk_parameters() -> Dict[str, Dict[str, float]]:
    path = Config.CONFIG_ROOT / "random_walk_parameters.yaml"

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return data["random_walk"]
