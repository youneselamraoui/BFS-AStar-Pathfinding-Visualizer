/* app.js - Application dynamique BFS vs A*
   Commentaires en français
*/
(() => {
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

  // État
  let state = {
    size: 30,
    grid: [],
    start: [0,0],
    goal: [29,29],
    heuristic: 'manhattan',
    animationSpeed: 50,
    mode: 'wall', // wall, start, goal
    bfsResult: null,
    astarResult: null,
    bfsStep: 0,
    astarStep: 0,
    bfsPlaying: false,
    astarPlaying: false,
    bfsAnimId: null,
    astarAnimId: null,
    history: [],
    chartNodes: null,
    chartTime: null,
    seed: null,
    comparisonSeq: 0,
  };

  // Références DOM
  const errorBanner = $('#error-banner');
  const showError = (msg) => {
    errorBanner.textContent = msg;
    errorBanner.classList.remove('hidden');
  };
  const hideError = () => errorBanner.classList.add('hidden');

  const sizeInput = $('#size-input');
  const densityInput = $('#density-input');
  const densityVal = $('#density-val');
  const seedInput = $('#seed-input');
  const heuristicSelect = $('#heuristic-select');
  const speedInput = $('#speed-input');
  const speedVal = $('#speed-val');

  const btnGen = $('#btn-generate');
  const btnRandom = $('#btn-random');
  const btnBFS = $('#btn-bfs');
  const btnAStar = $('#btn-astar');
  const btnCompare = $('#btn-compare');
  const btnReset = $('#btn-reset');
  const btnPauseBFS = $('#btn-pause-bfs');
  const btnPauseAStar = $('#btn-pause-astar');
  const modeWall = $('#mode-wall');
  const modeStart = $('#mode-start');
  const modeGoal = $('#mode-goal');
  const modeButtons = { wall: modeWall, start: modeStart, goal: modeGoal };
  const btnBenchmark = $('#btn-benchmark');
  const btnClearHistory = $('#btn-clear-history');
  const btnExportCSV = $('#btn-export-csv');
  const progressBar = $('#progress-bar');
  const progressFill = $('#progress-fill');
  const perfBody = $('#perf-body');
  const observationDiv = $('#observation');

  const canvasBFS = $('#canvas-bfs');
  const canvasAStar = $('#canvas-astar');
  const ctxBFS = canvasBFS.getContext('2d');
  const ctxAStar = canvasAStar.getContext('2d');

  const counters = {
    bfs: {
      nodes: $('#bfs-nodes'),
      time: $('#bfs-time'),
      len: $('#bfs-len'),
      state: $('#bfs-state')
    },
    astar: {
      nodes: $('#astar-nodes'),
      time: $('#astar-time'),
      len: $('#astar-len'),
      state: $('#astar-state')
    }
  };

  const statGrid = $('#stat-grid');
  const statGridNote = $('#stat-grid-note');
  const statHeuristic = $('#stat-heuristic');
  const statBfsNodes = $('#stat-bfs-nodes');
  const statAstarNodes = $('#stat-astar-nodes');

  // Utilitaires
  const disableButtons = (on) => {
    [btnGen, btnBFS, btnAStar, btnCompare, btnReset].forEach(b => b.disabled = on);
  };

  const toInt = (v, d=0) => {
    const n = Math.trunc(Number(v));
    return Number.isFinite(n) ? n : d;
  };

  const randomSeed = () => Math.floor(Math.random()*1000000);

  // Dessin
  function drawGrid(ctx, grid, start, goal, visited=[], path=[]) {
    const size = state.size;
    const cw = ctx.canvas.width / size;
    const ch = ctx.canvas.height / size;
    ctx.clearRect(0,0,ctx.canvas.width,ctx.canvas.height);
    for(let r=0;r<size;r++){
      for(let c=0;c<size;c++){
        const isWall = grid[r][c]===1;
        // fond
        ctx.fillStyle = isWall ? '#223047' : '#ffffff';
        ctx.fillRect(c*cw, r*ch, cw, ch);
        // grille fine
        ctx.strokeStyle = '#e8edf5';
        ctx.strokeRect(c*cw, r*ch, cw, ch);
      }
    }
    // visites
    ctx.fillStyle = '#dbeafe';
    for(const [r,c] of visited){
      ctx.fillRect(c*cw+1, r*ch+1, cw-2, ch-2);
    }
    // chemin
    ctx.fillStyle = '#2f6fd0';
    for(const [r,c] of path){
      ctx.fillRect(c*cw+1, r*ch+1, cw-2, ch-2);
    }
    // start / goal
    ctx.fillStyle = '#2f9e63';
    ctx.fillRect(start[1]*cw+1, start[0]*ch+1, cw-2, ch-2);
    ctx.fillStyle = '#c98a1e';
    ctx.fillRect(goal[1]*cw+1, goal[0]*ch+1, cw-2, ch-2);
  }

  function redraw() {
    drawGrid(ctxBFS, state.grid, state.start, state.goal,
      state.bfsResult ? state.bfsResult.visited_order.slice(0, state.bfsStep) : [],
      state.bfsResult ? state.bfsResult.path : []);
    drawGrid(ctxAStar, state.grid, state.start, state.goal,
      state.astarResult ? state.astarResult.visited_order.slice(0, state.astarStep) : [],
      state.astarResult ? state.astarResult.path : []);
  }

  function updateCounters(algo, res, step){
    const c = counters[algo];
    const statNode = algo === 'bfs' ? statBfsNodes : statAstarNodes;
    if(!res){
      c.nodes.textContent = '0';
      c.time.textContent = '—';
      c.len.textContent = '—';
      c.state.textContent = 'idle';
      if(statNode) statNode.textContent = '0';
      return;
    }
    const visitedSoFar = Math.min(step, res.visited_order.length);
    c.nodes.textContent = String(visitedSoFar);
    c.time.textContent = res.time_ms.toFixed(3)+' ms';
    c.len.textContent = res.found ? String(res.cost) : '—';
    c.state.textContent = step >= res.visited_order.length ? (res.found ? 'terminé' : 'aucun chemin') : 'en cours';
    if(statNode) statNode.textContent = String(res.nodes_expanded);
  }

  // Animation
  function animate(algo){
    const isBFS = algo==='bfs';
    const res = isBFS ? state.bfsResult : state.astarResult;
    if(!res) return;
    const stepKey = isBFS ? 'bfsStep' : 'astarStep';
    const playingKey = isBFS ? 'bfsPlaying' : 'astarPlaying';
    if(!state[playingKey]) return;
    state[stepKey] = Math.min(state[stepKey]+1, res.visited_order.length);
    redraw();
    updateCounters(algo, res, state[stepKey]);
    if(state[stepKey] >= res.visited_order.length){
      state[playingKey]=false;
      return;
    }
    const delay = Math.max(1, 200 - state.animationSpeed*3);
    setTimeout(()=>animate(algo), delay);
  }

  // API
  async function apiGrid(size, density, seed){
    const body = {size: toInt(size), density: Number(density), seed: seed===null||seed==='' ? null : toInt(seed)};
    const r = await fetch('/api/grid', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    if(!r.ok){
      const j = await r.json().catch(()=>({error:'Erreur inconnue'}));
      throw new Error(j.error || 'Erreur API grid');
    }
    return r.json();
  }

  async function apiRun(algo){
    const body = {
      grid: state.grid,
      start: state.start,
      goal: state.goal,
      algo,
      heuristic: state.heuristic,
      runs: 1
    };
    const r = await fetch('/api/run', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    if(!r.ok){
      const j = await r.json().catch(()=>({error:'Erreur inconnue'}));
      throw new Error(j.error || 'Erreur API run');
    }
    return r.json();
  }

  // Actions
  async function generate(){
    hideError();
    disableButtons(true);
    try{
      const size = toInt(sizeInput.value,30);
      const densityPct = Number(densityInput.value);
      const density = densityPct/100;
      const seedVal = seedInput.value.trim()==='' ? null : toInt(seedInput.value);
      const data = await apiGrid(size, density, seedVal);
      state.size = size;
      state.grid = data.grid;
      state.start = [0,0];
      state.goal = [data.goal[0], data.goal[1]];
      state.seed = data.seed !== undefined ? data.seed : seedVal;
      state.bfsResult = null;
      state.astarResult = null;
      state.bfsStep = 0;
      state.astarStep = 0;
      if(statGrid) statGrid.textContent = `${size} × ${size}`;
      if(statGridNote) statGridNote.textContent = `${densityPct}% de murs · seed ${state.seed ?? 'aléatoire'}`;
      if(statHeuristic) statHeuristic.textContent = state.heuristic.charAt(0).toUpperCase()+state.heuristic.slice(1);
      updateCounters('bfs', null, 0);
      updateCounters('astar', null, 0);
      redraw();
    }catch(e){
      showError(e.message);
    }finally{
      disableButtons(false);
    }
  }

  async function runAlgo(algo){
    hideError();
    disableButtons(true);
    try{
      const heuristic = state.heuristic;
      const seed = state.seed;
      const pairId = ++state.comparisonSeq;
      const res = await apiRun(algo);
      const density = Number(densityInput.value)/100;
      if(algo==='bfs'){
        state.bfsResult = {...res, found: res.found};
        state.bfsStep = 0;
        state.bfsPlaying = true;
        updateCounters('bfs', state.bfsResult, 0);
        animate('bfs');
        addPerfEntry({size: state.size, density, algo:'bfs', heuristic, seed, pairId, nodes: res.nodes_expanded, time: res.time_ms, length: res.found? res.cost : -1});
      }else{
        state.astarResult = {...res, found: res.found};
        state.astarStep = 0;
        state.astarPlaying = true;
        updateCounters('astar', state.astarResult, 0);
        animate('astar');
        // réduction vs dernier BFS même config
        let reduction = null;
        const lastBFS = state.history.find(h=>h.algo==='bfs' && h.size===state.size && Math.abs(h.density-density)<1e-9);
        if(lastBFS && lastBFS.nodes>0) reduction = (1 - res.nodes_expanded/lastBFS.nodes)*100;
        addPerfEntry({size: state.size, density, algo:'astar', heuristic, seed, pairId, nodes: res.nodes_expanded, time: res.time_ms, length: res.found? res.cost : -1, reduction});
      }
      updateCharts();
    }catch(e){
      showError(e.message);
    }finally{
      disableButtons(false);
    }
  }

  async function compare(){
    hideError();
    disableButtons(true);
    try{
      const heuristic = state.heuristic;
      const seed = state.seed;
      const [bfsRes, astarRes] = await Promise.all([apiRun('bfs'), apiRun('astar')]);
      const density = Number(densityInput.value)/100;
      const pairId = ++state.comparisonSeq;
      state.bfsResult = {...bfsRes};
      state.astarResult = {...astarRes};
      state.bfsStep = 0;
      state.astarStep = 0;
      state.bfsPlaying = true;
      state.astarPlaying = true;
      updateCounters('bfs', state.bfsResult, 0);
      updateCounters('astar', state.astarResult, 0);
      animate('bfs');
      animate('astar');
      addPerfEntry({size: state.size, density, algo:'bfs', heuristic, seed, pairId, nodes: bfsRes.nodes_expanded, time: bfsRes.time_ms, length: bfsRes.found? bfsRes.cost : -1});
      const reduction = bfsRes.nodes_expanded>0 ? (1 - astarRes.nodes_expanded/bfsRes.nodes_expanded)*100 : null;
      addPerfEntry({size: state.size, density, algo:'astar', heuristic, seed, pairId, nodes: astarRes.nodes_expanded, time: astarRes.time_ms, length: astarRes.found? astarRes.cost : -1, reduction});
      updateCharts();
    }catch(e){
      showError(e.message);
    }finally{
      disableButtons(false);
    }
  }

  function reset(){
    state.bfsResult = null;
    state.astarResult = null;
    state.bfsStep = 0;
    state.astarStep = 0;
    state.bfsPlaying = false;
    state.astarPlaying = false;
    redraw();
    updateCounters('bfs', null, 0);
    updateCounters('astar', null, 0);
  }

  function addPerfEntry({size, density, algo, heuristic, nodes, time, length, reduction=null, seed=null, pairId=null}){
    state.history.unshift({size, density, algo, heuristic, nodes, time, length, reduction, seed, pairId});
    if(state.history.length>40) state.history.pop();
    updatePerfTable();
    updateObservation();
  }

  function updatePerfTable(){
    if(!perfBody) return;
    if(state.history.length===0){
      perfBody.innerHTML = '<tr><td colspan="9" class="px-4 py-8 text-center text-muted-foreground">Aucune donnée</td></tr>';
      return;
    }
    perfBody.innerHTML = '';
    state.history.forEach(e=>{
      const tr = document.createElement('tr');
      tr.className = 'border-b border-border last:border-0 hover:bg-muted/50';
      const seed = e.seed !== undefined && e.seed !== null ? e.seed : '—';
      const algoBadge = e.algo === 'astar'
        ? '<span class="inline-flex rounded-md bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">A*</span>'
        : '<span class="inline-flex rounded-md bg-accent px-2 py-0.5 text-[11px] font-semibold text-accent-foreground">BFS</span>';
      const reduction = e.reduction !== null
        ? `<span class="inline-flex rounded-md bg-success-soft px-2 py-0.5 text-[11px] font-semibold text-success">${e.reduction.toFixed(1).replace('.', ',')} %</span>`
        : '<span class="text-muted-foreground">—</span>';
      tr.innerHTML = `<td class="px-4 py-3 font-medium">${e.size}x${e.size}</td>
      <td class="px-4 py-3 text-muted-foreground">${(e.density*100).toFixed(0)}%</td>
      <td class="px-4 py-3 text-muted-foreground">${seed}</td>
      <td class="px-4 py-3">${algoBadge}</td>
      <td class="px-4 py-3 text-muted-foreground">${e.algo === 'astar' ? e.heuristic : '—'}</td>
      <td class="px-4 py-3 text-center font-semibold tabular-nums">${e.nodes}</td>
      <td class="px-4 py-3 text-center tabular-nums">${e.time.toFixed(3)}</td>
      <td class="px-4 py-3 text-center font-semibold tabular-nums">${e.length}</td>
      <td class="px-4 py-3 text-center">${reduction}</td>`;
      perfBody.appendChild(tr);
    });
  }

  function lastComparison(){
    const groups = new Map();
    state.history.forEach(e=>{
      if(e.pairId===null || e.pairId===undefined) return;
      if(!groups.has(e.pairId)) groups.set(e.pairId, {});
      const g = groups.get(e.pairId);
      if(!g[e.algo]) g[e.algo] = e;
    });
    for(const g of groups.values()){
      if(g.bfs && g.astar) return g;
    }
    return null;
  }

  function updateObservation(){
    if(!observationDiv) return;
    const pair = lastComparison();
    if(!pair){
      observationDiv.textContent = '';
      return;
    }
    const bfs = pair.bfs;
    const astar = pair.astar;
    const bfsFound = bfs.length >= 0;
    const astarFound = astar.length >= 0;
    let txt = '';
    if(bfsFound && astarFound){
      if(bfs.length !== astar.length){
        txt = "Les longueurs de chemin diffèrent : l'heuristique n'est pas admissible ou la recherche n'est pas optimale.";
      }else if(astar.nodes < bfs.nodes && !(astar.time < bfs.time)){
        txt = "A* explore moins de nœuds que BFS mais n'est pas plus rapide en temps : le coût du tas O(log n) compense le gain par rapport à la file O(1) de BFS sur cette taille.";
      }else if(astar.nodes < bfs.nodes && astar.time < bfs.time){
        txt = "A* explore moins de nœuds et est plus rapide : l'heuristique oriente efficacement la recherche.";
      }else{
        txt = "Les deux algorithmes trouvent un chemin optimal de même longueur.";
      }
    }else{
      txt = "Aucun chemin trouvé pour l'un des algorithmes.";
    }
    observationDiv.textContent = txt;
  }

  function exportCSV(){
    const header = ['Grille','Densité','Seed','Algo','Heuristique','Nœuds explorés','Temps (ms)','Longueur du chemin','Réduction %'];
    const rows = state.history.map(e=>[`${e.size}x${e.size}`, e.density, e.seed??'', e.algo==='astar'?'A*':e.algo, e.algo==='astar'?e.heuristic:'—', e.nodes, e.time, e.length, e.reduction??'']);
    const csv = [header, ...rows].map(r=>r.join(',')).join('\n');
    const blob = new Blob(['\uFEFF'+csv], {type:'text/csv;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const d = new Date();
    const pad = n => String(n).padStart(2,'0');
    a.href = url;
    a.download = `bfs_astar_${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function clearHistory(){
    state.history = [];
    updatePerfTable();
    if(state.chartNodes) state.chartNodes.destroy();
    if(state.chartTime) state.chartTime.destroy();
    state.chartNodes = null;
    state.chartTime = null;
  }

  function initCharts(){
    if(typeof Chart === 'undefined'){
      $('#chart-nodes-msg').textContent = 'Graphiques indisponibles';
      $('#chart-time-msg').textContent = 'Graphiques indisponibles';
      return;
    }
    const ctxN = $('#chart-nodes');
    const ctxT = $('#chart-time');
    Chart.defaults.font.family = '"Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif';
    Chart.defaults.color = '#7c879b';
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: { usePointStyle: true, pointStyle: 'circle', boxWidth: 8, boxHeight: 8, font: { size: 11, weight: '600' } }
        },
        tooltip: {
          backgroundColor: '#ffffff',
          titleColor: '#1c2635',
          bodyColor: '#4a566a',
          borderColor: '#e3e8f0',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 10,
          displayColors: false
        }
      },
      scales: {
        x: {
          grid: { display: false },
          border: { display: false },
          ticks: { font: { size: 10 }, color: '#7c879b', maxRotation: 0, autoSkip: true }
        },
        y: {
          beginAtZero: true,
          grid: { color: '#e8edf5' },
          border: { display: false },
          ticks: { font: { size: 10 }, color: '#7c879b' }
        }
      }
    };
    const datasets = [
      { label: 'BFS', data: [], backgroundColor: '#2f6fd0', borderRadius: 6, maxBarThickness: 24 },
      { label: 'A*', data: [], backgroundColor: '#2f9e63', borderRadius: 6, maxBarThickness: 24 }
    ];
    state.chartNodes = new Chart(ctxN, { type: 'bar', data: { labels: [], datasets }, options: baseOptions });
    state.chartTime = new Chart(ctxT, { type: 'bar', data: { labels: [], datasets: datasets.map(d => ({ ...d })) }, options: baseOptions });
  }

  function updateCharts(){
    if(typeof Chart === 'undefined') return;
    // une paire de barres par comparaison (groupée par pairId)
    const groups = new Map();
    state.history.forEach(e=>{
      if(e.pairId===null || e.pairId===undefined) return;
      if(!groups.has(e.pairId)) groups.set(e.pairId, {});
      const g = groups.get(e.pairId);
      if(!g[e.algo]) g[e.algo] = e;
    });
    const pairs = [];
    for(const g of groups.values()){
      if(g.bfs && g.astar) pairs.push(g);
    }
    // 20 comparaisons maximum, les plus récentes, remises dans l'ordre chronologique
    const selected = pairs.slice(0, 20).reverse();
    const labels = [];
    const nodesBFS = [];
    const nodesA = [];
    const timeBFS = [];
    const timeA = [];
    selected.forEach(g=>{
      const seedTxt = g.bfs.seed !== null && g.bfs.seed !== undefined ? g.bfs.seed : '—';
      labels.push(`${g.bfs.size}×${g.bfs.size} · ${Math.round(g.bfs.density*100)}% · ${seedTxt}`);
      nodesBFS.push(g.bfs.nodes);
      nodesA.push(g.astar.nodes);
      timeBFS.push(g.bfs.time);
      timeA.push(g.astar.time);
    });
    if(state.chartNodes){
      state.chartNodes.data.labels = labels;
      state.chartNodes.data.datasets[0].data = nodesBFS;
      state.chartNodes.data.datasets[1].data = nodesA;
      state.chartNodes.update();
    }
    if(state.chartTime){
      state.chartTime.data.labels = labels;
      state.chartTime.data.datasets[0].data = timeBFS;
      state.chartTime.data.datasets[1].data = timeA;
      state.chartTime.update();
    }
  }

  // Interactions canvas
  function canvasToCell(canvas, ev){
    const rect = canvas.getBoundingClientRect();
    const x = ev.clientX - rect.left;
    const y = ev.clientY - rect.top;
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const cx = Math.floor(x * scaleX / canvas.width * state.size);
    const cy = Math.floor(y * scaleY / canvas.height * state.size);
    return [Math.max(0,Math.min(state.size-1,cy)), Math.max(0,Math.min(state.size-1,cx))];
  }

  function handleCanvasClick(canvas, ev){
    const [r,c] = canvasToCell(canvas, ev);
    if(state.mode==='wall'){
      if((r===state.start[0] && c===state.start[1]) || (r===state.goal[0] && c===state.goal[1])) return;
      state.grid[r][c] = state.grid[r][c]===1 ? 0 : 1;
      reset();
      redraw();
    }else if(state.mode==='start'){
      if(state.grid[r][c]===1) return;
      state.start = [r,c];
      redraw();
    }else if(state.mode==='goal'){
      if(state.grid[r][c]===1) return;
      state.goal = [r,c];
      redraw();
    }
  }

  async function benchmark(){
    hideError();
    disableButtons(true);
    progressBar.classList.remove('hidden');
    const sizes = [20,50,100];
    const density = Number(densityInput.value)/100;
    const seed = seedInput.value.trim()==='' ? null : toInt(seedInput.value);
    const heuristic = state.heuristic;
    try{
      for(let i=0;i<sizes.length;i++){
        const size = sizes[i];
        progressFill.style.width = ((i)/sizes.length*100)+'%';
        const gridData = await apiGrid(size, density, seed);
        state.size = size;
        state.grid = gridData.grid;
        state.start = [0,0];
        state.goal = gridData.goal;
        // runs=10
        const body = {grid: state.grid, start: state.start, goal: state.goal, algo:'bfs', heuristic, runs:10};
        const rBFS = await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
        if(!rBFS.ok) throw new Error((await rBFS.json()).error||'Erreur BFS');
        const bfsRes = await rBFS.json();
        const bodyA = {...body, algo:'astar'};
        const rA = await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(bodyA)});
        if(!rA.ok) throw new Error((await rA.json()).error||'Erreur A*');
        const astarRes = await rA.json();
        const pairId = ++state.comparisonSeq;
        addPerfEntry({size, density, algo:'bfs', heuristic, seed, pairId, nodes:bfsRes.nodes_expanded, time:bfsRes.time_ms, length:bfsRes.found?bfsRes.cost:-1});
        const reduction = bfsRes.nodes_expanded>0 ? (1 - astarRes.nodes_expanded/bfsRes.nodes_expanded)*100 : null;
        addPerfEntry({size, density, algo:'astar', heuristic, seed, pairId, nodes:astarRes.nodes_expanded, time:astarRes.time_ms, length:astarRes.found?astarRes.cost:-1, reduction});
        progressFill.style.width = ((i+1)/sizes.length*100)+'%';
      }
      updateCharts();
    }catch(e){
      showError(e.message);
    }finally{
      disableButtons(false);
      progressBar.classList.add('hidden');
      progressFill.style.width='0%';
    }
  }

  function setMode(mode){
    state.mode = mode;
    Object.entries(modeButtons).forEach(([key, btn])=>{
      if(btn) btn.classList.toggle('is-active', key === mode);
    });
  }

  function setPauseLabel(btn, playing){
    const label = btn.querySelector('[data-label]');
    if(label) label.textContent = playing ? 'Pause' : 'Reprendre';
  }

  // Init
  function init(){
    densityInput.addEventListener('input', ()=> densityVal.textContent = densityInput.value+'%');
    speedInput.addEventListener('input', ()=> speedVal.textContent = speedInput.value);
    heuristicSelect.addEventListener('change', ()=>{
      state.heuristic = heuristicSelect.value;
      if(statHeuristic) statHeuristic.textContent = state.heuristic.charAt(0).toUpperCase()+state.heuristic.slice(1);
    });
    sizeInput.value = 30;
    densityInput.value = 20;
    densityVal.textContent = '20%';
    speedInput.value = 50;
    speedVal.textContent = '50';
    seedInput.value = '42';
    state.animationSpeed = 50;

    btnRandom.onclick = ()=> { seedInput.value = String(randomSeed()); };
    btnGen.onclick = generate;
    btnBFS.onclick = ()=> runAlgo('bfs');
    btnAStar.onclick = ()=> runAlgo('astar');
    btnCompare.onclick = compare;
    btnReset.onclick = reset;
    btnPauseBFS.onclick = ()=> { state.bfsPlaying = !state.bfsPlaying; setPauseLabel(btnPauseBFS, state.bfsPlaying); };
    btnPauseAStar.onclick = ()=> { state.astarPlaying = !state.astarPlaying; setPauseLabel(btnPauseAStar, state.astarPlaying); };
    if(btnBenchmark) btnBenchmark.onclick = benchmark;
    if(btnClearHistory) btnClearHistory.onclick = clearHistory;
    if(btnExportCSV) btnExportCSV.onclick = exportCSV;

    modeWall.onclick = ()=> setMode('wall');
    modeStart.onclick = ()=> setMode('start');
    modeGoal.onclick = ()=> setMode('goal');
    setMode('wall');

    [canvasBFS, canvasAStar].forEach(cnv => {
      cnv.width = 600;
      cnv.height = 600;
      cnv.addEventListener('click', (e)=> handleCanvasClick(cnv, e));
      let dragging = false;
      cnv.addEventListener('mousedown', ()=> dragging=true);
      window.addEventListener('mouseup', ()=> dragging=false);
      cnv.addEventListener('mousemove', (e)=> { if(dragging) handleCanvasClick(cnv, e); });
    });

    initCharts();
    // génération initiale
    generate();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
