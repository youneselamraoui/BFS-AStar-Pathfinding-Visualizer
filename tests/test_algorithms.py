"""
Tests pytest pour bfs_astar.
"""
import numpy as np
from bfs_astar import bfs, astar, generate_grid, manhattan, get_neighbors, reconstruct_path


def test_manhattan():
    assert manhattan((0,0),(3,4)) == 7


def test_get_neighbors_edges():
    grid = np.zeros((3,3), dtype=int)
    neighbors = get_neighbors((1,1), grid)
    assert len(neighbors) == 4
    neighbors_corner = get_neighbors((0,0), grid)
    assert len(neighbors_corner) == 2


def test_reconstruct_path_simple():
    came_from = {(0,1): (0,0), (0,2): (0,1)}
    path = reconstruct_path(came_from, (0,0), (0,2))
    assert path == [(0,0),(0,1),(0,2)]


def test_bfs_empty_grid():
    grid = np.zeros((5,5), dtype=int)
    res = bfs(grid, (0,0), (4,4))
    assert res['path'][0] == (0,0)
    assert res['path'][-1] == (4,4)
    assert res['cost'] == 8
    # vérifie pas de mur traversé
    for r,c in res['path']:
        assert grid[r,c] == 0


def test_astar_empty_grid():
    grid = np.zeros((5,5), dtype=int)
    res = astar(grid, (0,0), (4,4))
    assert res['path'][0] == (0,0)
    assert res['path'][-1] == (4,4)
    assert res['cost'] == 8


def test_start_equals_goal():
    grid = np.zeros((3,3), dtype=int)
    res_bfs = bfs(grid, (1,1), (1,1))
    res_astar = astar(grid, (1,1), (1,1))
    assert res_bfs['cost'] == 0
    assert res_astar['cost'] == 0
    assert res_bfs['path'] == [(1,1)]
    assert res_astar['path'] == [(1,1)]


def test_no_solution():
    grid = np.ones((3,3), dtype=int)
    grid[0,0] = 0
    grid[2,2] = 0
    # mur complète autour
    grid[0,1] = 1
    grid[1,0] = 1
    res_bfs = bfs(grid, (0,0), (2,2))
    res_astar = astar(grid, (0,0), (2,2))
    assert res_bfs['path'] == []
    assert res_bfs['cost'] == -1
    assert res_astar['path'] == []
    assert res_astar['cost'] == -1


def test_corridor():
    grid = np.ones((5,5), dtype=int)
    grid[0,:] = 0
    grid[:,4] = 0
    res_bfs = bfs(grid, (0,0), (0,4))
    res_astar = astar(grid, (0,0), (0,4))
    assert res_bfs['cost'] == 4
    assert res_astar['cost'] == 4


def test_bfs_astar_same_cost_random():
    for seed in range(100):
        grid = generate_grid(10, obstacle_ratio=0.2, seed=seed)
        start = (0,0)
        goal = (9,9)
        res_bfs = bfs(grid, start, goal)
        res_astar = astar(grid, start, goal)
        if res_bfs['path']:
            assert res_bfs['cost'] == res_astar['cost'], f"seed {seed}"


def test_astar_explores_less_or_equal_on_empty():
    grid = np.zeros((50,50), dtype=int)
    res_bfs = bfs(grid, (0,0), (49,49))
    res_astar = astar(grid, (0,0), (49,49))
    assert res_astar['explored'] <= res_bfs['explored']


def test_path_no_wall_and_endpoints():
    grid = generate_grid(20, obstacle_ratio=0.25, seed=42)
    start = (0,0)
    goal = (19,19)
    res_bfs = bfs(grid, start, goal)
    path = res_bfs['path']
    assert path[0] == start
    assert path[-1] == goal
    for r,c in path:
        assert grid[r,c] == 0


def test_generate_grid_guarantees_path():
    grid = generate_grid(15, obstacle_ratio=0.3, seed=7)
    res = bfs(grid, (0,0), (14,14))
    assert res['path'], "generate_grid doit garantir un chemin"
