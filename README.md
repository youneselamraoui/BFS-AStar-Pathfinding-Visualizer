# BFS vs A* – TD Éthique IA

Comparaison interactive d’une recherche exacte en largeur **BFS** et d’une recherche heuristique **A*** sur un problème de cheminement dans une grille. Interface avec sidebar repliable, cartes, tableau comparatif, charts Chart.js et thème Tailwind v4.

## Structure du projet

```
BFS-AStar-Pathfinding-Visualizer/
├─ backend/
│  ├─ app.py                # API Flask + rendu template
│  ├─ src/pathfinding/      # BFS, A*, heuristiques, grille, métriques
│  ├─ tests/                # tests pytest
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ src/
│  │  ├─ static/            # CSS, JS, images, output
│  │  └─ templates/         # index.html
│  ├─ tailwind/             # input.css, thème OKLCH
│  ├─ package.json
│  └─ ...
├─ docker-compose.yml
├─ .gitignore
└─ README.md
```

### Backend
* Flask expose `/`, `/api/grid`, `/api/run`, `/health`
* Génération de grille avec densité et seed reproductible
* Exécution BFS et A* avec comptage nœuds, temps médian, longueur chemin
* Visualisations Matplotlib sauvegardées dans `frontend/src/static/output/`

### Frontend
* Tailwind v4 avec variables CSS personnalisées
* Sidebar repliable persistante, navigation par ancres, breadcrumb
* 4 stat cards : Grille, Heuristique, Nœuds BFS, Nœuds A*
* Section Implémentation : taille, densité, seed, heuristique, vitesse animation
* Section Visualisation : deux canvas côte à côte, modes Mur/Départ/Arrivée, pause
* Section Comparaison : tableau historique, benchmark rapide, export CSV, charts nœuds/temps
* Thème : `bg-background`, `text-muted-foreground`, `rounded-2xl`, `border-border`, palette succès/warning

## Prérequis

* Docker + Docker Compose **ou**
* Python 3.11+, Node 18+, pip, npm

## Démarrage rapide – Docker

```bash
cd BFS-AStar-Pathfinding-Visualizer

docker compose up --build
```
Accès : http://localhost:5000

Le build copie `backend/` et `frontend/`, monte `frontend/src/static` et `frontend/src/templates` pour le développement.

## Démarrage local sans Docker

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python app.py
```
API sur http://localhost:5000

### Frontend – build Tailwind
```bash
cd frontend
npm install
npm run build   # génère frontend/src/static/css/app.css
```
Le serveur Flask sert déjà les fichiers statiques depuis `frontend/src/static`.

### Tests
```bash
cd backend
pytest -q
```
45 tests passent : routes, API grid/run, UI éléments.

## Utilisation

1. **Implémentation** : régler taille, densité, seed, heuristique `manhattan/euclidean/chebyshev/zero`, vitesse.
2. **Générer** une grille, modifier mur/départ/arrivée par clic/glisser.
3. **Lancer BFS / A* / Comparer** : animation de l’exploration, compteurs nœuds/temps/longueur.
4. **Tableau comparatif** : historique des runs, réduction % A* vs BFS, export CSV.
5. **Benchmark rapide** : 20/50/100, 10 runs médianes, mise à jour des charts.

## Concepts clés

* **BFS** : exploration en largeur uniforme, optimal sur coûts unitaires, file O(1).
* **A*** : f(n)=g(n)+h(n), explore moins de nœuds avec heuristique admissible.
* **Heuristique** :
  * manhattan → grille Manhattan
  * euclidean → distance euclidienne
  * chebyshev → diagonales autorisées
  * zero → Dijkstra
* Quand BFS reste préférable : absence d’heuristique fiable, petit graphe, besoin de simplicité.

## Développement

* Modifier le thème : `frontend/tailwind/input.css`
* Modifier l’UI : `frontend/src/templates/index.html`, `frontend/src/static/app.js`, `frontend/src/static/ui.js`
* Ajouter tests : `backend/tests/`

## .gitignore

Python, venv, `__pycache__`, `.pytest_cache`, `node_modules/`, `dist/`, `.vscode/`, `static/output/*.png`, etc.

## Licence

Projet académique TD Éthique IA.
