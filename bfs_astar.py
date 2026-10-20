"""
BFS vs A* comparison for grid pathfinding.
Implémentation avec type hints et docstrings en français.
"""

import heapq
import time
from collections import deque
from typing import Tuple, List, Dict, Any

import numpy as np

Pos = Tuple[int, int]
Grid = np.ndarray
Result = Dict[str, Any]


def manhattan(a: Pos, b: Pos) -> int:
    """Retourne la distance de Manhattan entre deux positions."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(pos: Pos, grid: Grid) -> List[Pos]:
    """Renvoie les voisins libres en 4 directions autour de pos."""
    rows, cols = grid.shape
    r, c = pos
    neighbors: List[Pos] = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr, nc] == 0:
            neighbors.append((nr, nc))
    return neighbors


def reconstruct_path(came_from: Dict[Pos, Pos | None], start: Pos, goal: Pos) -> List[Pos]:
    """Reconstitue le chemin depuis start jusqu'à goal."""
    path: List[Pos] = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = came_from.get(cur)
        if cur is None:
            return []
    path.append(start)
    path.reverse()
    return path


def bfs(grid: Grid, start: Pos, goal: Pos) -> Result:
    """Breadth-First Search sur grille. Retourne path, cost, explored, time."""
    visited_order: List[Pos] = []
    queue = deque([start])
    came_from: Dict[Pos, Pos | None] = {start: None}
    explored = 0
    start_time = time.perf_counter()
    while queue:
        current = queue.popleft()
        explored += 1
        visited_order.append(current)
        if current == goal:
            break
        for nb in get_neighbors(current, grid):
            if nb not in came_from:
                came_from[nb] = current
                queue.append(nb)
    elapsed = time.perf_counter() - start_time
    path = reconstruct_path(came_from, start, goal) if goal in came_from else []
    cost = len(path) - 1 if path else -1
    return {
        'path': path,
        'cost': cost,
        'explored': explored,
        'time': elapsed,
        'visited_order': visited_order,
        'nodes_expanded': len(visited_order)
    }


def astar(grid: Grid, start: Pos, goal: Pos) -> Result:
    """A* avec heuristique Manhattan. Utilise un set closed pour O(1)."""
    open_set: List[Tuple[int, int, Pos]] = []
    heapq.heappush(open_set, (manhattan(start, goal), 0, start))
    came_from: Dict[Pos, Pos | None] = {start: None}
    g_score: Dict[Pos, int] = {start: 0}
    closed_set: set[Pos] = set()
    visited_order: List[Pos] = []
    explored = 0
    start_time = time.perf_counter()
    while open_set:
        _, current_g, current = heapq.heappop(open_set)
        if current in closed_set:
            continue
        closed_set.add(current)
        visited_order.append(current)
        explored += 1
        if current == goal:
            break
        for nb in get_neighbors(current, grid):
            tentative_g = g_score[current] + 1
            if nb not in g_score or tentative_g < g_score[nb]:
                came_from[nb] = current
                g_score[nb] = tentative_g
                f = tentative_g + manhattan(nb, goal)
                heapq.heappush(open_set, (f, tentative_g, nb))
    elapsed = time.perf_counter() - start_time
    path = reconstruct_path(came_from, start, goal) if goal in came_from else []
    cost = len(path) - 1 if path else -1
    return {
        'path': path,
        'cost': cost,
        'explored': explored,
        'time': elapsed,
        'visited_order': visited_order,
        'nodes_expanded': len(visited_order)
    }


def generate_grid(size: int, obstacle_ratio: float = 0.2, seed: int | None = None) -> Grid:
    """
    Génère une grille avec obstacles.
    Garantit l'existence d'un chemin entre (0,0) et (size-1,size-1)
    en ré-essayant jusqu'à 50 fois, sinon ValueError.
    """
    start = (0, 0)
    goal = (size - 1, size - 1)
    for attempt in range(50):
        actual_seed = None if seed is None else seed + attempt
        rng = np.random.default_rng(actual_seed)
        # 0 = libre, 1 = mur. obstacle_ratio = probabilité de mur
        grid = rng.random((size, size)) < obstacle_ratio
        grid = grid.astype(int)
        grid[start] = 0
        grid[goal] = 0
        # vérification rapide de l'existence d'un chemin
        res = bfs(grid, start, goal)
        if res['path']:
            return grid
    raise ValueError(f"Impossible de générer une grille {size}x{size} avec un chemin après 50 essais")


def run_comparison(sizes: List[int] = [20, 50, 100], obstacle_ratio: float = 0.2) -> List[Dict[str, Any]]:
    """Exécute BFS et A* sur plusieurs tailles de grille."""
    results: List[Dict[str, Any]] = []
    for size in sizes:
        grid = generate_grid(size, obstacle_ratio, seed=size)
        start = (0, 0)
        goal = (size - 1, size - 1)
        bfs_res = bfs(grid, start, goal)
        astar_res = astar(grid, start, goal)
        results.append({
            'size': size,
            'obstacle_ratio': obstacle_ratio,
            'bfs_explored': bfs_res['explored'],
            'astar_explored': astar_res['explored'],
            'bfs_time': bfs_res['time'],
            'astar_time': astar_res['time'],
            'bfs_path_len': len(bfs_res['path']),
            'astar_path_len': len(astar_res['path']),
            'bfs_cost': bfs_res['cost'],
            'astar_cost': astar_res['cost'],
            'bfs_path': bfs_res['path'],
            'astar_path': astar_res['path'],
            'grid': grid,
            'bfs_visited': bfs_res['visited_order'],
            'astar_visited': astar_res['visited_order'],
            'start': start,
            'goal': goal
        })
    return results
