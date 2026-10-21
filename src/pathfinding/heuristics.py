"""Heuristiques pour la recherche de chemin."""
from typing import Tuple
import math

Pos = Tuple[int, int]

def manhattan(a: Pos, b: Pos) -> int:
    """Distance de Manhattan entre deux positions."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclidean(a: Pos, b: Pos) -> float:
    """Distance euclidienne entre deux positions."""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def chebyshev(a: Pos, b: Pos) -> int:
    """Distance de Chebyshev entre deux positions."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

def zero(a: Pos, b: Pos) -> int:
    """Heuristique nulle."""
    return 0
