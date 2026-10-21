(() => {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const openBtn = document.getElementById('sidebar-open');
  const closeBtn = document.getElementById('sidebar-close');
  const toggleBtn = document.getElementById('sidebar-toggle');
  const toggleIcon = document.getElementById('sidebar-toggle-icon');
  const breadcrumb = document.getElementById('breadcrumb-current');
  const links = Array.from(document.querySelectorAll('[data-nav]'));

  const LABELS = {
    implementation: 'Implémentation',
    visualisation: 'Visualisation',
    comparaison: 'Comparaison',
    observation: 'Analyse',
  };
  const SECTIONS = ['implementation', 'visualisation', 'comparaison', 'observation'];

  const COLLAPSE_KEY = 'bfs:sidebar:collapsed';

  function readCollapsed() {
    try {
      return localStorage.getItem(COLLAPSE_KEY) === '1';
    } catch {
      return false;
    }
  }

  function setCollapsed(collapsed) {
    sidebar.classList.toggle('is-collapsed', collapsed);
    toggleIcon.classList.toggle('rotate-180', collapsed);
    if (toggleBtn) toggleBtn.title = collapsed ? 'Déplier' : 'Replier';
    try {
      localStorage.setItem(COLLAPSE_KEY, collapsed ? '1' : '0');
    } catch {
      void 0;
    }
  }

  function openMobile() {
    sidebar.classList.remove('hidden');
    sidebar.classList.add('flex');
    overlay.classList.remove('hidden');
  }

  function closeMobile() {
    if (window.matchMedia('(min-width: 1024px)').matches) return;
    sidebar.classList.add('hidden');
    sidebar.classList.remove('flex');
    overlay.classList.add('hidden');
  }

  function setActive(key) {
    links.forEach((link) => {
      link.classList.toggle('is-active', link.dataset.nav === key);
    });
    if (breadcrumb && LABELS[key]) breadcrumb.textContent = LABELS[key];
  }

  function updateScrollSpy() {
    const offset = window.innerHeight * 0.28;
    let current = SECTIONS[0];
    for (const id of SECTIONS) {
      const el = document.getElementById(id);
      if (!el) continue;
      if (el.getBoundingClientRect().top <= offset) current = id;
    }
    if (window.innerHeight + window.scrollY >= document.body.scrollHeight - 4) {
      current = SECTIONS[SECTIONS.length - 1];
    }
    setActive(current);
  }

  setCollapsed(readCollapsed());

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      setCollapsed(!sidebar.classList.contains('is-collapsed'));
    });
  }
  if (openBtn) openBtn.addEventListener('click', openMobile);
  if (closeBtn) closeBtn.addEventListener('click', closeMobile);
  if (overlay) overlay.addEventListener('click', closeMobile);

  links.forEach((link) => {
    link.addEventListener('click', () => {
      closeMobile();
      const key = link.dataset.nav;
      if (key && LABELS[key]) setActive(key);
    });
  });

  window.addEventListener('resize', () => {
    if (window.matchMedia('(min-width: 1024px)').matches) {
      overlay.classList.add('hidden');
      sidebar.classList.remove('flex');
      sidebar.classList.add('hidden');
    }
  });

  let ticking = false;
  window.addEventListener(
    'scroll',
    () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        updateScrollSpy();
        ticking = false;
      });
    },
    { passive: true }
  );

  updateScrollSpy();
})();
