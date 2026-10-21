"""Dataclasses pour les résultats de recherche."""
from dataclasses import dataclass
from typing import List, Tuple

Pos = Tuple[int, int]

@dataclass
class SearchResult:
    path: List[Pos]
    cost: int
    nodes_expanded: int
    nodes_generated: int
    max_frontier_size: int
    time_ms: float
    visited_order: List[Pos]
