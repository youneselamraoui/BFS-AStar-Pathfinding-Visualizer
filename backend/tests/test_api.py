import pytest
import numpy as np
from src.pathfinding.grid import generate_grid
from src.pathfinding.algorithms import bfs, astar

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json() == {'status': 'ok'}

def test_api_grid_valid(client):
    r = client.post('/api/grid', json={'size': 20, 'density': 0.2, 'seed': 42})
    assert r.status_code == 200
    data = r.get_json()
    assert 'grid' in data
    assert data['start'] == [0,0]
    assert data['goal'] == [19,19]
    assert len(data['grid']) == 20

def test_api_grid_density_invalid(client):
    r = client.post('/api/grid', json={'size': 20, 'density': 0.9, 'seed': 1})
    assert r.status_code == 400
    assert 'error' in r.get_json()

def test_api_grid_size_invalid(client):
    r = client.post('/api/grid', json={'size': 200, 'density': 0.1, 'seed': 1})
    assert r.status_code == 400

def test_api_run_bfs_valid(client):
    grid = [[0]*5 for _ in range(5)]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [4,4],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 3
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 200
    data = r.get_json()
    assert data['found'] is True
    assert data['cost'] == 8
    assert isinstance(data['time_ms'], float)

def test_api_run_astar_valid(client):
    grid = [[0]*5 for _ in range(5)]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [4,4],
        'algo': 'astar',
        'heuristic': 'manhattan',
        'runs': 2
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 200
    data = r.get_json()
    assert data['found'] is True
    assert data['cost'] == 8

def test_api_run_bfs_astar_same_cost(client):
    for i in range(20):
        grid = generate_grid(15, obstacle_ratio=0.2, seed=i)
        payload = {
            'grid': grid.tolist(),
            'start': [0,0],
            'goal': [14,14],
            'algo': 'bfs',
            'heuristic': 'manhattan',
            'runs': 1
        }
        r_bfs = client.post('/api/run', json=payload)
        payload['algo'] = 'astar'
        r_astar = client.post('/api/run', json=payload)
        assert r_bfs.status_code == 200
        assert r_astar.status_code == 200
        d_bfs = r_bfs.get_json()
        d_astar = r_astar.get_json()
        if d_bfs['found']:
            assert d_astar['found']
            assert d_bfs['cost'] == d_astar['cost']
        else:
            assert not d_astar['found']

def test_api_run_no_solution(client):
    grid = [[0]*3 for _ in range(3)]
    # wall row
    grid[1] = [1,1,1]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [2,2],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 200
    data = r.get_json()
    assert data['found'] is False
    assert data['cost'] is None
    assert data['path'] == []

def test_api_run_start_on_wall(client):
    grid = [[0,1],[0,0]]
    payload = {
        'grid': grid,
        'start': [0,1],
        'goal': [1,1],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400
    assert 'error' in r.get_json()

def test_api_run_algo_unknown(client):
    grid = [[0]]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [0,0],
        'algo': 'dijkstra',
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

def test_api_run_grid_too_large(client):
    grid = [[0]*200 for _ in range(200)]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [199,199],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

def test_api_run_start_negative(client):
    grid = [[0,0],[0,0]]
    payload = {
        'grid': grid,
        'start': [-1,-1],
        'goal': [1,1],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

def test_api_run_body_non_json(client):
    r = client.post('/api/run', data='not json', content_type='text/plain')
    assert r.status_code == 400

def test_api_run_missing_algo(client):
    grid = [[0]]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [0,0],
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

def test_api_run_grid_value_2(client):
    grid = [[0,2],[0,0]]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [1,1],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

def test_api_run_grid_true_value(client):
    grid = [[0, True],[0,0]]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [1,1],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

def test_api_run_grid_unequal_rows(client):
    grid = [[0,0],[0]]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [1,0],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 1
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

def test_api_grid_density_nan(client):
    import math
    r = client.post('/api/grid', json={'size': 20, 'density': float('nan'), 'seed': 1})
    assert r.status_code == 400

def test_api_run_runs_zero(client):
    grid = [[0]]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [0,0],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 0
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

def test_api_run_runs_too_high(client):
    grid = [[0]]
    payload = {
        'grid': grid,
        'start': [0,0],
        'goal': [0,0],
        'algo': 'bfs',
        'heuristic': 'manhattan',
        'runs': 31
    }
    r = client.post('/api/run', json=payload)
    assert r.status_code == 400

@pytest.mark.parametrize('heuristic', ['manhattan','euclidean','chebyshev','zero'])
def test_api_astar_heuristic_optimality(client, heuristic):
    for i in range(50):
        grid = generate_grid(15, obstacle_ratio=0.2, seed=i)
        payload_bfs = {
            'grid': grid.tolist(),
            'start': [0,0],
            'goal': [14,14],
            'algo': 'bfs',
            'heuristic': 'manhattan',
            'runs': 1
        }
        payload_astar = {
            'grid': grid.tolist(),
            'start': [0,0],
            'goal': [14,14],
            'algo': 'astar',
            'heuristic': heuristic,
            'runs': 1
        }
        r_bfs = client.post('/api/run', json=payload_bfs)
        r_astar = client.post('/api/run', json=payload_astar)
        assert r_bfs.status_code == 200
        assert r_astar.status_code == 200
        d_bfs = r_bfs.get_json()
        d_astar = r_astar.get_json()
        if d_bfs['found']:
            assert d_astar['found']
            assert d_bfs['cost'] == d_astar['cost']
        else:
            assert not d_astar['found']

def test_api_astar_zero_explores_at_least_manhattan(client):
    size = 30
    grid = [[0]*size for _ in range(size)]
    payload_man = {
        'grid': grid,
        'start': [0,0],
        'goal': [size-1,size-1],
        'algo': 'astar',
        'heuristic': 'manhattan',
        'runs': 1
    }
    payload_zero = {
        'grid': grid,
        'start': [0,0],
        'goal': [size-1,size-1],
        'algo': 'astar',
        'heuristic': 'zero',
        'runs': 1
    }
    r_man = client.post('/api/run', json=payload_man)
    r_zero = client.post('/api/run', json=payload_zero)
    assert r_man.status_code == 200
    assert r_zero.status_code == 200
    d_man = r_man.get_json()
    d_zero = r_zero.get_json()
    assert d_zero['nodes_expanded'] >= d_man['nodes_expanded']

def test_api_grid_density_too_high(client):
    r = client.post('/api/grid', json={'size':100,'density':0.5,'seed':1})
    assert r.status_code == 400
    assert 'error' in r.get_json()

def test_api_grid_max_density_has_path(client):
    from src.pathfinding.algorithms import bfs
    import numpy as np
    r = client.post('/api/grid', json={'size':100,'density':0.35,'seed':1})
    assert r.status_code == 200
    data = r.get_json()
    grid = np.array(data['grid'])
    start = tuple(data['start'])
    goal = tuple(data['goal'])
    res = bfs(grid, start, goal)
    assert res.path, 'un chemin doit exister'

def test_api_grid_density_zero(client):
    r = client.post('/api/grid', json={'size':20,'density':0,'seed':1})
    assert r.status_code == 200
    data = r.get_json()
    grid = data['grid']
    assert all(all(cell==0 for cell in row) for row in grid)
