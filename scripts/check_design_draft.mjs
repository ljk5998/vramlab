// Run after building both output directories documented in design/README.md.
// Static checks complement (and do not replace) the recorded browser review.
import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { resolve, join, relative } from 'node:path';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const root = resolve(import.meta.dirname, '..');
const draft = join(root, '.draft-build');
const production = join(root, '.draft-checks', 'production');
const read = (path) => readFileSync(path, 'utf8');
const home = read(join(draft, 'index.html'));
const liveHome = read(join(production, 'index.html'));
const files = (dir) => readdirSync(dir).flatMap((name) => {
  const path = join(dir, name);
  return statSync(path).isDirectory() ? files(path) : [path];
});
const checks = [];
const check = (name, fn) => { fn(); checks.push(name); };
const postPaths = JSON.parse(read(join(production, 'index.json')))
  .map((item) => new URL(item.permalink).pathname)
  .filter((path) => path.startsWith('/posts/') && path !== '/posts/');

check('Seven existing report URLs remain available', () => {
  assert.equal(postPaths.length, 7);
  for (const path of postPaths) assert.ok(existsSync(join(draft, path, 'index.html')), path);
});
check('Existing report code blocks and table contents are unchanged', () => {
  const blocks = (html, tag) => [...html.matchAll(new RegExp(`<${tag}\\b[^>]*>[\\s\\S]*?<\\/${tag}>`, 'g'))]
    .map(([block]) => block.replaceAll('\r\n', '\n'));
  for (const path of postPaths) {
    const before = read(join(production, path, 'index.html'));
    const after = read(join(draft, path, 'index.html'));
    for (const tag of ['pre', 'table']) assert.deepEqual(blocks(after, tag), blocks(before, tag), `${path} ${tag}`);
  }
});
check('Draft identity, opt-in robots policy, and source-based claims', () => {
  assert.match(home, /Small hardware\./);
  assert.match(home, /Deep experiments\./);
  assert.match(home, /noindex, nofollow/);
  assert.match(home, /17 conditions × 3 runs/);
  assert.match(home, /132\.415/);
  assert.match(home, /11,412/);
  assert.match(home, /No published M4 experiments yet/);
  assert.match(read(join(draft, 'robots.txt')), /Disallow: \//);
  assert.doesNotMatch(home, /cloudflareinsights|beacon\.min/);
});
check('Visible feature dates match their machine-readable dates', () => {
  for (const [, iso, display] of home.matchAll(/<time datetime="(\d{4}-\d{2}-\d{2})">([^<]+)<\/time>/g)) {
    const [year, month, day] = iso.split('-');
    const shortMonth = new Date(`${iso}T12:00:00Z`).toLocaleString('en-US', { month: 'short', timeZone: 'UTC' }).toUpperCase();
    assert.ok([`${day} ${shortMonth} ${year}`, `${year}.${month}.${day}`].includes(display), `${iso} versus ${display}`);
  }
});
check('Production promotes the approved design without review-only UI', () => {
  assert.match(liveHome, /Small hardware\./);
  assert.match(liveHome, /Deep experiments\./);
  assert.match(liveHome, /lab\/scene\.js/);
  assert.doesNotMatch(liveHome, /DESIGN STUDY|Design draft|Local preview/);
  assert.match(liveHome, /name="robots" content="index, follow"/);
  assert.match(liveHome, /cloudflareinsights/);
  assert.match(read(join(production, 'robots.txt')), /Sitemap: https:\/\/vramlab\.com\/sitemap\.xml/);
  assert.doesNotMatch(read(join(production, 'robots.txt')), /Disallow:\s*\//);
});
check('Production indexing, canonical links, feeds, and structured data are preserved', () => {
  for (const path of [...postPaths, '/start-here/', '/fixes/', '/compatibility/', '/benchmarks/']) {
    const html = read(join(production, path, 'index.html'));
    assert.match(html, /name="robots" content="index, follow"/, path);
    assert.ok(html.includes(`href="https://vramlab.com${path}"`), `canonical: ${path}`);
    if (postPaths.includes(path)) assert.match(html, /"@type":\s*"BlogPosting"/, path);
    else assert.doesNotMatch(html, /"@type":\s*"BlogPosting"/, path);
  }
  for (const path of ['/search/', '/tags/', '/categories/']) {
    assert.match(read(join(production, path, 'index.html')), /name="robots" content="noindex, follow"/, path);
  }
  const sitemap = read(join(production, 'sitemap.xml'));
  assert.doesNotMatch(sitemap, /localhost|127\.0\.0\.1|\/search\/|\/tags\/|\/categories\//);
  for (const path of postPaths) assert.ok(sitemap.includes(`https://vramlab.com${path}`));
  assert.equal([...read(join(production, 'index.xml')).matchAll(/<item>/g)].length, 7);
  assert.doesNotMatch(liveHome, /"@type":\s*"BlogPosting"/);
});
let references = 0;
check('Local HTML links and script/style/image resources resolve', () => {
  for (const path of files(draft).filter((path) => path.endsWith('.html') && !path.replaceAll('\\', '/').includes('lab/diagrams'))) {
    const relativePath = relative(draft, path).replaceAll('\\', '/');
    const base = new URL(relativePath.replace(/index\.html$/, ''), 'http://127.0.0.1:1313/');
    const html = read(path);
    for (const [, raw] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
      const value = raw.replaceAll('&amp;', '&');
      if (/^(?:data:|mailto:|tel:|javascript:)/.test(value) || value.startsWith('#')) continue;
      const url = new URL(value, base);
      if (url.origin !== base.origin) continue;
      if (url.pathname === '/livereload.js') continue; // Hugo development server only.
      const target = join(draft, decodeURIComponent(url.pathname));
      assert.ok(existsSync(target) || existsSync(join(target, 'index.html')), `${relativePath} -> ${value}`);
      references += 1;
    }
  }
});
check('Three.js is local, pinned, and does not require React', () => {
  const vendor = join(root, 'themes/LabDraft/static/lab/vendor');
  const module = read(join(vendor, 'three.module.min.js'));
  assert.match(module, /three@0\.186\.0/);
  for (const [, importPath] of module.matchAll(/from\s*["'](\.[^"']+)["']/g)) assert.ok(existsSync(join(vendor, importPath)), importPath);
  const custom = read(join(root, 'themes/LabDraft/static/lab/scene.js'));
  assert.doesNotMatch(custom, /from\s+['"]react|react-dom|@react-three/);
  assert.match(custom, /prefers-reduced-motion/);
  assert.match(custom, /webglcontextlost/);
});
check('Archify HTML matches the frozen delivery', () => {
  const path = join(root, 'themes/LabDraft/static/lab/diagrams/dataset-cache.html');
  const hash = createHash('sha256').update(readFileSync(path)).digest('hex');
  assert.equal(hash, '1cb401089c336ce53ef94dc2a2f2dfc670d5989c2f3a107187f7d997594d396d');
});
console.log(JSON.stringify({ status: 'pass', checks: checks.length, localReferences: references, reports: postPaths.length, passed: checks }, null, 2));
