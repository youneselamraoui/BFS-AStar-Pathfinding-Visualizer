import os
from flask import Flask, render_template, send_from_directory
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bfs_astar import run_comparison, generate_grid

app = Flask(__name__, static_folder='static', template_folder='templates')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'static', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def visualize(grid, bfs_res, astar_res, size, idx):
    # Create visualization for BFS and A*
    # We'll produce two images side by side
    fig, axes = plt.subplots(1,2, figsize=(12,6))
    for ax, visited, path, title in [
        (axes[0], bfs_res['visited_order'], bfs_res['path'], 'BFS'),
        (axes[1], astar_res['visited_order'], astar_res['path'], 'A*')
    ]:
        img = np.ones_like(grid, dtype=float)*0.9  # free space light
        img[grid==1] = 0  # walls black
        # visited
        for r,c in visited:
            img[r,c] = 0.6
        # path
        for r,c in path:
            img[r,c] = 1.0
        # start green, goal yellow
        start = (0,0)
        goal = (grid.shape[0]-1, grid.shape[1]-1)
        img[start] = 0.2
        img[goal] = 0.8
        ax.imshow(img, cmap='gray_r', vmin=0, vmax=1)
        ax.set_title(f'{title} - explored {len(visited)}')
        ax.axis('off')
    plt.tight_layout()
    path_img = os.path.join(OUTPUT_DIR, f'grid_{size}_{idx}.png')
    plt.savefig(path_img, dpi=150)
    plt.close()
    return path_img

def ensure_results():
    results_file = os.path.join(OUTPUT_DIR, 'results.json')
    # For simplicity, regenerate each run
    sizes = [20,50,100]
    data = []
    for i, size in enumerate(sizes):
        grid = generate_grid(size, obstacle_ratio=0.2, seed=size)
        start = (0,0)
        goal = (size-1,size-1)
        from bfs_astar import bfs, astar
        bfs_res = bfs(grid, start, goal)
        astar_res = astar(grid, start, goal)
        visualize(grid, bfs_res, astar_res, size, i)
        data.append({
            'size': size,
            'bfs_explored': bfs_res['explored'],
            'astar_explored': astar_res['explored'],
            'bfs_time': round(bfs_res['time'],4),
            'astar_time': round(astar_res['time'],4),
            'bfs_path_len': len(bfs_res['path']),
            'astar_path_len': len(astar_res['path']),
            'image': f'output/grid_{size}_{i}.png'
        })
    return data

@app.route('/')
def index():
    results = ensure_results()
    return render_template('index.html', results=results)

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
