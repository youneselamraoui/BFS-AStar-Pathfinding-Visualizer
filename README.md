# TD Ethique IA - Comparaison BFS vs A*

## Contexte
Comparaison d'un algorithme exact BFS et heuristique A* sur problème de recherche de chemin dans une grille.

## Structure du projet
- `bfs_astar.py` : implémentation BFS et A* avec compteurs
- `app.py` : Flask serving page avec Tailwind
- `templates/index.html` : frontend style inspiré de Management_Demande (Tailwind, cards, tableau)
- `static/output/` : images générées
- `Dockerfile` + `docker-compose.yml`

## Lancement
```bash
docker compose up --build
```
Accès http://localhost:5000

## Résultats attendus
Tableau comparatif : nœuds explorés, temps d'exécution, longueur chemin.
Visualisation côte à côte BFS / A*.

## Réponses théoriques
**Pourquoi A* est plus efficace ?**
Il oriente la recherche vers le but via f(n)=g(n)+h(n), donc explore moins de nœuds que BFS qui étend en largeur uniforme.

**Rôle de la fonction heuristique ?**
Estime le coût restant. Si admissible, A* reste optimal. Plus elle est précise, plus la recherche est rapide. h=0 → Dijkstra.

**Quand BFS reste préférable ?**
Pas d'heuristique fiable, graphe petit/ coûts unitaires, besoin de garantie simple sans dépendre de h, plusieurs buts inconnus.

## Note
Impossible de lire `C:\Users\youne\Downloads\TD2.pdf` : ce modèle ne supporte pas l'entrée PDF.
