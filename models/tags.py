from dataclasses import dataclass


@dataclass(eq=True)
class Tag:
    name: str
