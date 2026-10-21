"""Gestion des grilles et voisins."""
from typing import Tuple, List
import numpy as np

Pos = Tuple[int, int]
Grid = np.ndarray

def get_neighbors(pos: Pos, grid: Grid) -> List[Pos]:
    """Renvoie les voisins libres en 4 directions."""
    rows, cols = grid.shape
    r, c = pos
    neighbors: List[Pos] = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr, nc] == 0:
            neighbors.append((nr, nc))
    return neighbors

def generate_grid(size: int, obstacle_ratio: float = 0.2, seed: int | None = None) -> Grid:
    """Génère une grille avec garantie de chemin."""
    from .algorithms import bfs
    start = (0, 0)
    goal = (size - 1, size - 1)
    for attempt in range(50):
        actual_seed = None if seed is None else seed + attempt
        rng = np.random.default_rng(actual_seed)
        grid = rng.random((size, size)) < obstacle_ratio
        grid = grid.astype(int)
        grid[start] = 0
        grid[goal] = 0
        res = bfs(grid, start, goal)
        if res.path:
            return grid
    raise ValueError(f"Impossible de générer une grille {size}x{size} avec un chemin après 50 essais")
