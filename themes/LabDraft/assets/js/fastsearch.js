import * as params from '@params';

// LabDraft owns the search states. Fuse itself remains a pinned PaperMod asset.
const searchBox = document.getElementById('searchbox');
const input = document.getElementById('searchInput');
const resultsList = document.getElementById('searchResults');
const status = document.getElementById('searchStatus');
const retry = document.getElementById('searchRetry');

let fuse = null;
let searchTimer;

const setState = (state, message) => {
  searchBox.dataset.searchState = state;
  searchBox.setAttribute('aria-busy', String(state === 'loading'));
  status.textContent = message;
  retry.hidden = state !== 'error';
};

const fuseOptions = () => {
  const options = params.fuseOpts || {};
  return {
    isCaseSensitive: options.iscasesensitive ?? false,
    includeScore: options.includescore ?? false,
    includeMatches: options.includematches ?? false,
    minMatchCharLength: options.minmatchcharlength ?? 1,
    shouldSort: options.shouldsort ?? true,
    findAllMatches: options.findallmatches ?? false,
    keys: options.keys ?? ['title', 'permalink', 'summary', 'content'],
    location: options.location ?? 0,
    threshold: options.threshold ?? 0.4,
    distance: options.distance ?? 100,
    ignoreLocation: options.ignorelocation ?? true,
  };
};

const clearResults = () => resultsList.replaceChildren();

const renderResults = (matches) => {
  const fragment = document.createDocumentFragment();
  for (const { item } of matches) {
    const row = document.createElement('li');
    const title = document.createElement('span');
    title.textContent = item.title;
    const arrow = document.createElement('span');
    arrow.className = 'row-arrow';
    arrow.textContent = '↗';
    arrow.setAttribute('aria-hidden', 'true');
    const link = document.createElement('a');
    link.className = 'entry-link';
    link.href = item.permalink;
    link.setAttribute('aria-label', item.title);
    row.append(title, arrow, link);
    fragment.append(row);
  }
  resultsList.replaceChildren(fragment);
};

const performSearch = () => {
  if (!fuse) return; // Loading and failure keep their own status.
  const query = input.value.trim();
  if (!query) {
    clearResults();
    setState('empty', 'Enter a command, error, or component name.');
    return;
  }
  const limit = params.fuseOpts?.limit;
  const matches = Number.isInteger(limit) && limit > 0
    ? fuse.search(query, { limit }) : fuse.search(query);
  renderResults(matches);
  setState(matches.length ? 'results' : 'no-results', matches.length
    ? `${matches.length} matching ${matches.length === 1 ? 'page' : 'pages'}.`
    : 'No matching pages. Try another term, Start here, or All reports.');
};

const validIndex = (data) => Array.isArray(data) && data.length > 0 && data.every((item) => {
  if (!item || typeof item !== 'object' || Array.isArray(item)) return false;
  if (!['title', 'permalink', 'summary', 'content'].every((key) => typeof item[key] === 'string')) return false;
  if (!item.title.trim() || !item.permalink.trim()) return false;
  try {
    const url = new URL(item.permalink, window.location.href);
    return ['http:', 'https:'].includes(url.protocol) && url.origin === window.location.origin;
  } catch { return false; }
});

const initSearch = async (focusAfterLoad = false) => {
  if (!searchBox || !input || !resultsList || !status || !retry) return;
  window.clearTimeout(searchTimer);
  fuse = null;
  clearResults();
  input.disabled = true;
  setState('loading', 'Loading the search index…');
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(searchBox.dataset.indexUrl, { signal: controller.signal });
    if (!response.ok) throw new Error(`Search index returned HTTP ${response.status}`);
    const data = await response.json();
    if (!validIndex(data)) throw new Error('Invalid search index');
    fuse = new Fuse(data, fuseOptions());
    input.disabled = false;
    setState('ready', 'Search is ready. Enter a command, error, or component name.');
    if (input.value.trim()) performSearch();
    if (focusAfterLoad) input.focus();
  } catch (error) {
    setState('error', 'Search could not load. Use Start here or All reports below, or retry.');
    console.warn('VRAM Lab search is unavailable:', error.name);
  } finally {
    window.clearTimeout(timeout);
  }
};

const resetSearch = () => {
  window.clearTimeout(searchTimer);
  input.value = '';
  if (fuse) performSearch();
  else clearResults();
  if (!input.disabled) input.focus();
  else if (!retry.hidden) retry.focus();
};

const focusResult = (link) => {
  resultsList.querySelectorAll('.focus').forEach((row) => row.classList.remove('focus'));
  if (!link) return;
  link.focus();
  link.parentElement.classList.add('focus');
};

input?.addEventListener('input', () => {
  window.clearTimeout(searchTimer);
  if (!input.value.trim()) performSearch();
  else searchTimer = window.setTimeout(performSearch, 150);
});
input?.addEventListener('search', () => { if (!input.value) resetSearch(); });
retry?.addEventListener('click', () => initSearch(true));
resultsList?.addEventListener('focusin', (event) => {
  resultsList.querySelectorAll('.focus').forEach((row) => row.classList.remove('focus'));
  if (event.target.matches('.entry-link')) event.target.parentElement.classList.add('focus');
});
resultsList?.addEventListener('focusout', (event) => {
  if (event.target.matches('.entry-link')) event.target.parentElement.classList.remove('focus');
});

document.addEventListener('keydown', (event) => {
  const active = document.activeElement;
  if (!searchBox?.contains(active)) return;
  if (event.key === 'Escape') {
    event.preventDefault();
    resetSearch();
    return;
  }
  const links = Array.from(resultsList.querySelectorAll('.entry-link'));
  if (!links.length) return;
  const index = links.indexOf(active);
  if (event.key === 'ArrowDown' && (active === input || index >= 0)) {
    event.preventDefault();
    focusResult(active === input ? links[0] : links[Math.min(index + 1, links.length - 1)]);
  } else if (event.key === 'ArrowUp' && index >= 0) {
    event.preventDefault();
    if (index === 0) { input.focus(); }
    else focusResult(links[index - 1]);
  } else if (event.key === 'ArrowRight' && index >= 0) {
    event.preventDefault();
    active.click();
  }
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initSearch(), { once: true });
} else {
  initSearch();
}
