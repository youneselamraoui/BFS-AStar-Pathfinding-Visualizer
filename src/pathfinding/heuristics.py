"""Heuristiques pour la recherche de chemin."""
from typing import Tuple

Pos = Tuple[int, int]

def manhattan(a: Pos, b: Pos) -> int:
    """Distance de Manhattan entre deux positions."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
