"""Algorithmes BFS et A*."""
import time
import heapq
from collections import deque
from typing import Tuple, List, Dict
import numpy as np
from .metrics import SearchResult
from .heuristics import manhattan
from .grid import get_neighbors

Pos = Tuple[int, int]
Grid = np.ndarray

def reconstruct_path(came_from: Dict[Pos, Pos | None], start: Pos, goal: Pos) -> List[Pos]:
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

def bfs(grid: Grid, start: Pos, goal: Pos) -> SearchResult:
    visited_order: List[Pos] = []
    queue = deque([start])
    came_from: Dict[Pos, Pos | None] = {start: None}
    nodes_generated = 1
    max_frontier = 1
    start_time = time.perf_counter()
    while queue:
        max_frontier = max(max_frontier, len(queue))
        current = queue.popleft()
        visited_order.append(current)
        if current == goal:
            break
        for nb in get_neighbors(current, grid):
            if nb not in came_from:
                came_from[nb] = current
                queue.append(nb)
                nodes_generated += 1
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    path = reconstruct_path(came_from, start, goal) if goal in came_from else []
    cost = len(path) - 1 if path else -1
    nodes_expanded = len(visited_order)
    return SearchResult(
        path=path,
        cost=cost,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier_size=max_frontier,
        time_ms=elapsed_ms,
        visited_order=visited_order
    )

def astar(grid: Grid, start: Pos, goal: Pos) -> SearchResult:
    open_set: List[Tuple[int, int, Pos]] = []
    heapq.heappush(open_set, (manhattan(start, goal), 0, start))
    came_from: Dict[Pos, Pos | None] = {start: None}
    g_score: Dict[Pos, int] = {start: 0}
    closed_set: set[Pos] = set()
    visited_order: List[Pos] = []
    nodes_generated = 1
    max_frontier = 1
    start_time = time.perf_counter()
    while open_set:
        max_frontier = max(max_frontier, len(open_set))
        _, current_g, current = heapq.heappop(open_set)
        if current in closed_set:
            continue
        closed_set.add(current)
        visited_order.append(current)
        if current == goal:
            break
        for nb in get_neighbors(current, grid):
            tentative_g = g_score[current] + 1
            if nb not in g_score or tentative_g < g_score[nb]:
                came_from[nb] = current
                g_score[nb] = tentative_g
                f = tentative_g + manhattan(nb, goal)
                heapq.heappush(open_set, (f, tentative_g, nb))
                if nb not in closed_set:
                    nodes_generated += 1
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    path = reconstruct_path(came_from, start, goal) if goal in came_from else []
    cost = len(path) - 1 if path else -1
    nodes_expanded = len(visited_order)
    return SearchResult(
        path=path,
        cost=cost,
        nodes_expanded=nodes_expanded,
        nodes_generated=nodes_generated,
        max_frontier_size=max_frontier,
        time_ms=elapsed_ms,
        visited_order=visited_order
    )
