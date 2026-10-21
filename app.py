import os
from flask import Flask, render_template, send_from_directory, request, jsonify
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from statistics import median
from src.pathfinding.grid import generate_grid
from src.pathfinding.algorithms import bfs, astar
from src.pathfinding.heuristics import manhattan, euclidean, chebyshev, zero

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 1_000_000
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.errorhandler(400)
def handle_400(e):
    return jsonify(error='Requête invalide'), 400

@app.errorhandler(404)
def handle_404(e):
    return jsonify(error='Ressource non trouvée'), 404

@app.errorhandler(405)
def handle_405(e):
    return jsonify(error='Méthode non autorisée'), 405

@app.errorhandler(413)
def handle_413(e):
    return jsonify(error='Payload trop volumineux'), 413

@app.errorhandler(500)
def handle_500(e):
    return jsonify(error='Erreur interne du serveur'), 500

def visualize(grid, bfs_res, astar_res, size, idx):
    # Create visualization for BFS and A* with clear colors
    fig, axes = plt.subplots(1,2, figsize=(14,7))
    cmap = ListedColormap(['white', 'black', '#add8e6', '#ff0000', '#00cc00', '#ffff00'])
    start = (0,0)
    goal = (grid.shape[0]-1, grid.shape[1]-1)
    for ax, visited, path, title in [
        (axes[0], bfs_res.visited_order, bfs_res.path, 'BFS'),
        (axes[1], astar_res.visited_order, astar_res.path, 'A*')
    ]:
        img_cat = np.where(grid == 1, 1, 0)
        for r,c in visited:
            if (r,c) not in [start, goal]:
                img_cat[r,c] = 2
        for r,c in path:
            img_cat[r,c] = 3
        img_cat[start] = 4
        img_cat[goal] = 5
        ax.imshow(img_cat, cmap=cmap, vmin=0, vmax=5, interpolation='nearest')
        ax.set_title(f'{title} : {len(visited)} nœuds explorés', fontsize=14)
        ax.axis('off')
    plt.tight_layout()
    path_img = os.path.join(OUTPUT_DIR, f'grid_{size}_{idx}.png')
    plt.savefig(path_img, dpi=150)
    plt.close()
    return path_img

def build_results():
    sizes = [20,50,100]
    data = []
    for i, size in enumerate(sizes):
        grid = generate_grid(size, obstacle_ratio=0.2, seed=size)
        start = (0,0)
        goal = (size-1,size-1)
        # 10 runs for median time
        bfs_runs = [bfs(grid, start, goal) for _ in range(10)]
        astar_runs = [astar(grid, start, goal) for _ in range(10)]
        bfs_res = bfs_runs[0]
        astar_res = astar_runs[0]
        visualize(grid, bfs_res, astar_res, size, i)
        bfs_time_ms = round(median(r.time_ms for r in bfs_runs), 3)
        astar_time_ms = round(median(r.time_ms for r in astar_runs), 3)
        reduction = 0.0
        if bfs_res.nodes_expanded > 0:
            reduction = round((1 - astar_res.nodes_expanded / bfs_res.nodes_expanded) * 100, 1)
        if astar_res.nodes_expanded < bfs_res.nodes_expanded:
            if astar_time_ms >= bfs_time_ms:
                observation = f"Sur {size}x{size}, A* explore {astar_res.nodes_expanded} nœuds contre {bfs_res.nodes_expanded} pour BFS, soit une réduction de {reduction}%, mais le temps médian est {astar_time_ms} ms contre {bfs_time_ms} ms : le coût du tas O(log n) compense le gain sur cette taille."
            else:
                observation = f"Sur {size}x{size}, A* explore {astar_res.nodes_expanded} nœuds contre {bfs_res.nodes_expanded} pour BFS, soit une réduction de {reduction}%, et est aussi plus rapide en temps {astar_time_ms} ms contre {bfs_time_ms} ms."
        else:
            observation = f"Sur {size}x{size}, A* n’apporte pas de gain en nombre de nœuds explorés."
        data.append({
            'size': size,
            'bfs_explored': bfs_res.nodes_expanded,
            'astar_explored': astar_res.nodes_expanded,
            'bfs_time': bfs_time_ms,
            'astar_time': astar_time_ms,
            'bfs_path_len': bfs_res.cost,
            'astar_path_len': astar_res.cost,
            'reduction': reduction,
            'observation': observation,
            'image': f'output/grid_{size}_{i}.png'
        })
    return data

CACHED_RESULTS = build_results()

@app.route('/')
def index():
    results = CACHED_RESULTS
    return render_template('index.html', results=results)

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/health', methods=['GET'])
def health():
    return jsonify(status='ok')

@app.route('/api/grid', methods=['POST'])
def api_grid():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='corps JSON manquant ou invalide'), 400
    size = data.get('size')
    density = data.get('density')
    seed = data.get('seed')
    # Validation
    if type(size) is not int or not (5 <= size <= 150):
        return jsonify(error='size doit être un entier entre 5 et 150'), 400
    if type(density) not in (int, float):
        return jsonify(error='density doit être un nombre'), 400
    import math
    if math.isnan(density) or math.isinf(density) or not (0 <= density <= 0.35):
        return jsonify(error='density doit être entre 0 et 0.35'), 400
    if seed is not None and type(seed) is not int:
        return jsonify(error='seed doit être un entier ou null'), 400
    try:
        grid = generate_grid(size, obstacle_ratio=float(density), seed=seed)
    except ValueError:
        return jsonify(error='impossible de générer une grille avec un chemin'), 400
    return jsonify({
        'grid': grid.tolist(),
        'start': [0, 0],
        'goal': [size-1, size-1],
        'seed': seed
    })

HEURISTICS = {
    'manhattan': manhattan,
    'euclidean': euclidean,
    'chebyshev': chebyshev,
    'zero': zero
}

def validate_grid_payload(data):
    errors = []
    # check required keys
    required = ['grid','start','goal','algo','heuristic','runs']
    for k in required:
        if k not in data:
            errors.append(f'clé manquante : {k}')
            return errors
    grid = data.get('grid')
    start = data.get('start')
    goal = data.get('goal')
    algo = data.get('algo')
    heuristic = data.get('heuristic')
    runs = data.get('runs')
    # grid validation
    if not isinstance(grid, list) or len(grid) == 0:
        errors.append('grid invalide')
        return errors
    n = len(grid)
    if n > 150:
        errors.append('grid taille > 150')
        return errors
    for i,row in enumerate(grid):
        if not isinstance(row, list) or len(row) != n:
            errors.append('grid doit être carrée')
            return errors
        for v in row:
            if type(v) is not int or v not in (0,1):
                errors.append('grid ne contient que 0 et 1')
                return errors
    # start/goal
    if not (isinstance(start, list) and len(start)==2) or not (isinstance(goal, list) and len(goal)==2):
        errors.append('start et goal doivent être [r,c]')
        return errors
    try:
        sr, sc = start[0], start[1]
        gr, gc = goal[0], goal[1]
        if type(sr) is not int or type(sc) is not int or type(gr) is not int or type(gc) is not int:
            raise ValueError
        if sr < 0 or sc < 0 or gr < 0 or gc < 0 or sr >= n or sc >= n or gr >= n or gc >= n:
            errors.append('start ou goal hors grille ou index négatif')
            return errors
    except Exception:
        errors.append('start et goal doivent être entiers')
        return errors
    if grid[sr][sc] != 0 or grid[gr][gc] != 0:
        errors.append('start et goal doivent être sur cases libres')
        return errors
    # algo
    if algo not in ('bfs','astar'):
        errors.append('algo doit être bfs ou astar')
        return errors
    # heuristic
    if heuristic not in HEURISTICS:
        errors.append('heuristic inconnue')
        return errors
    # runs
    if type(runs) is not int or not (1 <= runs <= 30):
        errors.append('runs doit être un entier entre 1 et 30')
        return errors
    return errors

@app.route('/api/run', methods=['POST'])
def api_run():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error='corps JSON manquant ou invalide'), 400
    errors = validate_grid_payload(data)
    if errors:
        return jsonify(error='; '.join(errors)), 400
    grid_list = data['grid']
    grid_np = np.array(grid_list, dtype=int)
    start = (data['start'][0], data['start'][1])
    goal = (data['goal'][0], data['goal'][1])
    algo = data['algo']
    heuristic_name = data['heuristic']
    runs = data['runs']
    heuristic_fn = HEURISTICS[heuristic_name]
    results = []
    for _ in range(runs):
        if algo == 'bfs':
            res = bfs(grid_np, start, goal)
        else:
            res = astar(grid_np, start, goal, heuristic=heuristic_fn)
        results.append(res)
    first = results[0]
    found = first.path and len(first.path) > 0 and first.cost >= 0
    path = [list(p) for p in first.path] if found else []
    visited = [list(p) for p in first.visited_order]
    cost = int(first.cost) if found else None
    time_ms = float(round(median(r.time_ms for r in results), 3))
    return jsonify({
        'found': bool(found),
        'path': path,
        'visited_order': visited,
        'cost': cost,
        'nodes_expanded': int(first.nodes_expanded),
        'nodes_generated': int(first.nodes_generated),
        'max_frontier_size': int(first.max_frontier_size),
        'time_ms': time_ms
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
