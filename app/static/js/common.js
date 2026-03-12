(function(){
  const html = document.documentElement;
  const btn = document.getElementById('themeToggle');
  const saved = localStorage.getItem('planner_theme');
  if (saved) html.setAttribute('data-theme', saved);
  if (btn) {
    btn.addEventListener('click', () => {
      const current = html.getAttribute('data-theme') || 'nebula';
      const next = current === 'nebula' ? 'light' : current === 'light' ? 'night' : 'nebula';
      html.setAttribute('data-theme', next);
      localStorage.setItem('planner_theme', next);
    });
  }
})();
