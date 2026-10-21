import os
from flask import Flask, render_template, send_from_directory
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from src.pathfinding.grid import generate_grid
from src.pathfinding.algorithms import bfs, astar

app = Flask(__name__, static_folder='static', template_folder='templates')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def visualize(grid, bfs_res, astar_res, size, idx):
    # Create visualization for BFS and A* with clear colors
    fig, axes = plt.subplots(1,2, figsize=(12,6))
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
        ax.set_title(f'{title} - exploré {len(visited)}')
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
        bfs_res = bfs(grid, start, goal)
        astar_res = astar(grid, start, goal)
        visualize(grid, bfs_res, astar_res, size, i)
        data.append({
            'size': size,
            'bfs_explored': bfs_res.nodes_expanded,
            'astar_explored': astar_res.nodes_expanded,
            'bfs_time': round(bfs_res.time_ms/1000,4),
            'astar_time': round(astar_res.time_ms/1000,4),
            'bfs_path_len': bfs_res.cost,
            'astar_path_len': astar_res.cost,
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
