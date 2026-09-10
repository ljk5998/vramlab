(() => {
  'use strict';
  const themeButton = document.querySelector('.theme-button');
  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    themeButton?.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
    document.dispatchEvent(new CustomEvent('lab-theme', { detail: theme }));
  };
  try { const saved = localStorage.getItem('vramlab-draft-theme'); if (saved === 'light' || saved === 'dark') applyTheme(saved); } catch { /* Private mode does not disable theme switching. */ }
  if (themeButton) {
    themeButton.hidden = false;
    themeButton.addEventListener('click', () => {
      const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      applyTheme(theme);
      try { localStorage.setItem('vramlab-draft-theme', theme); } catch { /* Optional preference only. */ }
    });
  }
  document.querySelectorAll('.post-content table').forEach((table, index) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', table.caption?.textContent || `Report table ${index + 1}, scroll horizontally if needed`);
    table.before(wrapper);
    wrapper.append(table);
  });
  if (navigator.clipboard?.writeText) {
    document.querySelectorAll('.highlight').forEach((block) => {
      const code = block.querySelector('pre code');
      if (!code) return;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'copy-button';
      button.textContent = 'Copy';
      button.setAttribute('aria-label', 'Copy code block');
      button.addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(code.textContent); button.textContent = 'Copied'; }
        catch { button.textContent = 'Select to copy'; }
        window.setTimeout(() => { button.textContent = 'Copy'; }, 2000);
      });
      block.append(button);
    });
  }
  const results = document.getElementById('searchResults');
  const input = document.getElementById('searchInput');
  if (results && input) {
    const status = document.createElement('p');
    status.className = 'search-status';
    status.setAttribute('role', 'status');
    results.before(status);
    const update = () => {
      const count = results.children.length;
      status.textContent = !input.value.trim() ? '' : count ? `${count} matching ${count === 1 ? 'page' : 'pages'}.` : 'No matching pages. Try another term or browse Experiments.';
    };
    new MutationObserver(update).observe(results, { childList: true });
    input.addEventListener('input', () => window.setTimeout(update, 350));
  }
})();
