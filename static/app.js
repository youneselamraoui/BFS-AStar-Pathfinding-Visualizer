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
        ctx.fillStyle = isWall ? '#000' : '#fff';
        ctx.fillRect(c*cw, r*ch, cw, ch);
        // grille fine
        ctx.strokeStyle = '#e5e7eb';
        ctx.strokeRect(c*cw, r*ch, cw, ch);
      }
    }
    // visites
    ctx.fillStyle = '#add8e6';
    for(const [r,c] of visited){
      ctx.fillRect(c*cw+1, r*ch+1, cw-2, ch-2);
    }
    // chemin
    ctx.fillStyle = '#ff0000';
    for(const [r,c] of path){
      ctx.fillRect(c*cw+1, r*ch+1, cw-2, ch-2);
    }
    // start / goal
    ctx.fillStyle = '#00cc00';
    ctx.fillRect(start[1]*cw+1, start[0]*ch+1, cw-2, ch-2);
    ctx.fillStyle = '#ffff00';
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
    if(!res){
      c.nodes.textContent = '0';
      c.time.textContent = '—';
      c.len.textContent = '—';
      c.state.textContent = 'idle';
      return;
    }
    const visitedSoFar = Math.min(step, res.visited_order.length);
    c.nodes.textContent = String(visitedSoFar);
    c.time.textContent = res.time_ms.toFixed(3)+' ms';
    c.len.textContent = res.found ? String(res.cost) : '—';
    c.state.textContent = step >= res.visited_order.length ? (res.found ? 'terminé' : 'aucun chemin') : 'en cours';
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
      state.bfsResult = null;
      state.astarResult = null;
      state.bfsStep = 0;
      state.astarStep = 0;
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
      const res = await apiRun(algo);
      if(algo==='bfs'){
        state.bfsResult = {...res, found: res.found};
        state.bfsStep = 0;
        state.bfsPlaying = true;
        updateCounters('bfs', state.bfsResult, 0);
        animate('bfs');
      }else{
        state.astarResult = {...res, found: res.found};
        state.astarStep = 0;
        state.astarPlaying = true;
        updateCounters('astar', state.astarResult, 0);
        animate('astar');
      }
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
      const [bfsRes, astarRes] = await Promise.all([apiRun('bfs'), apiRun('astar')]);
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

  // Init
  function init(){
    densityInput.addEventListener('input', ()=> densityVal.textContent = densityInput.value+'%');
    speedInput.addEventListener('input', ()=> speedVal.textContent = speedInput.value);
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
    btnPauseBFS.onclick = ()=> { state.bfsPlaying = !state.bfsPlaying; btnPauseBFS.textContent = state.bfsPlaying ? 'Pause' : 'Reprendre'; };
    btnPauseAStar.onclick = ()=> { state.astarPlaying = !state.astarPlaying; btnPauseAStar.textContent = state.astarPlaying ? 'Pause' : 'Reprendre'; };

    modeWall.onclick = ()=> state.mode='wall';
    modeStart.onclick = ()=> state.mode='start';
    modeGoal.onclick = ()=> state.mode='goal';

    [canvasBFS, canvasAStar].forEach(cnv => {
      cnv.width = 600;
      cnv.height = 600;
      cnv.addEventListener('click', (e)=> handleCanvasClick(cnv, e));
      let dragging = false;
      cnv.addEventListener('mousedown', ()=> dragging=true);
      window.addEventListener('mouseup', ()=> dragging=false);
      cnv.addEventListener('mousemove', (e)=> { if(dragging) handleCanvasClick(cnv, e); });
    });

    // génération initiale
    generate();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
