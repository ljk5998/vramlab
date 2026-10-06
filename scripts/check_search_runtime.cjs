#!/usr/bin/env node
/* Execute the built search bundle and its real pinned Fuse engine.
 * A small DOM double checks states and event handlers; this does not render a
 * page or replace browser/viewport/accessibility QA. No requests leave the VM.
 * Usage: node scripts/check_search_runtime.cjs BUILD [RESULT.json]
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const build = path.resolve(process.argv[2] || 'public');
const searchHtml = fs.readFileSync(path.join(build, 'search/index.html'), 'utf8');
const bundleUrl = searchHtml.match(/src=["']?([^"'\s>]*\/lab\/search\.[^"'\s>]+\.js)/)?.[1];
assert(bundleUrl, 'Built fingerprinted search bundle is missing');
const bundle = fs.readFileSync(path.join(build, new URL(bundleUrl, 'https://vramlab.com').pathname), 'utf8');
const index = JSON.parse(fs.readFileSync(path.join(build, 'index.json'), 'utf8'));
const passed = [];

class Element {
  constructor(tag, owner) {
    this.tagName = tag;
    this.owner = owner;
    this.children = [];
    this.parentElement = null;
    this.dataset = {};
    this.attributes = {};
    this.listeners = {};
    this.className = '';
    this.textContent = '';
    this.value = '';
    this.disabled = false;
    this.hidden = false;
    this.classList = {
      add: (name) => { this.className = [...new Set([...this.className.split(' ').filter(Boolean), name])].join(' '); },
      remove: (name) => { this.className = this.className.split(' ').filter((x) => x !== name).join(' '); },
    };
  }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  addEventListener(name, fn) { (this.listeners[name] ||= []).push(fn); }
  dispatch(name, extra = {}) {
    const event = { target: this, preventDefault() { this.prevented = true; }, ...extra };
    for (const fn of this.listeners[name] || []) fn(event);
    return event;
  }
  append(...nodes) {
    for (const node of nodes) {
      if (node.tagName === '#fragment') { this.append(...node.children); continue; }
      node.parentElement = this;
      this.children.push(node);
    }
  }
  replaceChildren(...nodes) { this.children = []; this.append(...nodes); }
  matches(selector) { return selector.startsWith('.') && this.className.split(' ').includes(selector.slice(1)); }
  querySelectorAll(selector) {
    return this.children.flatMap((child) => [...(child.matches(selector) ? [child] : []), ...child.querySelectorAll(selector)]);
  }
  contains(node) { return node === this || this.children.some((child) => child.contains(node)); }
  focus() { this.owner.activeElement = this; }
  click() { this.clicked = true; this.dispatch('click'); }
}

const settle = async () => { for (let n = 0; n < 16; n++) await Promise.resolve(); };
function environment(outcome = 'success') {
  const document = { activeElement: null, readyState: 'complete', listeners: {} };
  const nodes = Object.fromEntries(['searchbox', 'searchInput', 'searchResults', 'searchStatus', 'searchRetry'].map((id) => [id, new Element(id, document)]));
  const box = nodes.searchbox;
  box.dataset.indexUrl = '/index.json';
  box.append(nodes.searchInput, nodes.searchResults, nodes.searchStatus, nodes.searchRetry);
  document.getElementById = (id) => nodes[id] || null;
  document.createElement = (tag) => new Element(tag, document);
  document.createDocumentFragment = () => new Element('#fragment', document);
  document.addEventListener = (name, fn) => { (document.listeners[name] ||= []).push(fn); };
  document.key = (key) => {
    const event = { key, preventDefault() { this.prevented = true; } };
    for (const fn of document.listeners.keydown || []) fn(event);
    return event;
  };
  const timers = new Map();
  let counter = 0;
  const window = {
    location: { href: 'https://vramlab.com/search/', origin: 'https://vramlab.com' },
    setTimeout: (fn, delay) => { const id = ++counter; timers.set(id, { fn, delay }); return id; },
    clearTimeout: (id) => { timers.delete(id); },
  };
  let mode = outcome;
  const requests = [];
  const warnings = [];
  const fetch = async (url, options) => {
    requests.push(url);
    assert.equal(url, '/index.json', 'Unexpected request from search');
    if (mode === 'network') throw new TypeError('Simulated network failure');
    if (mode === 'timeout') return new Promise((resolve, reject) => {
      options.signal.addEventListener('abort', () => { const error = new Error('Simulated abort'); error.name = 'AbortError'; reject(error); });
    });
    return {
      ok: mode !== 'http', status: mode === 'http' ? 503 : 200,
      json: async () => {
        if (mode === 'json') throw new SyntaxError('Simulated invalid JSON');
        if (mode === 'shape') return [{ title: 'Broken', permalink: 'javascript:alert(1)', summary: '', content: '' }];
        if (mode === 'cross-origin') return [{ title: 'Unexpected host', permalink: 'https://example.invalid/', summary: '', content: '' }];
        return index;
      },
    };
  };
  const context = vm.createContext({ document, window, fetch, URL, AbortController,
    console: { warn: (...values) => warnings.push(values) }, setTimeout: window.setTimeout, clearTimeout: window.clearTimeout });
  vm.runInContext(bundle, context, { timeout: 2000, filename: 'built-search.js' });
  return { nodes, document, requests, warnings,
    mode: (value) => { mode = value; },
    state: () => box.dataset.searchState,
    runTimers: (delay) => { for (const [id, timer] of [...timers]) if (timer.delay === delay) { timers.delete(id); timer.fn(); } },
  };
}

async function main() {
  const env = environment();
  assert.equal(env.state(), 'loading');
  assert.equal(env.nodes.searchInput.disabled, true);
  await settle();
  assert.equal(env.state(), 'ready');
  assert.equal(env.nodes.searchInput.disabled, false);
  assert.equal(env.nodes.searchRetry.hidden, true);
  passed.push('loading -> ready from the generated production index');

  env.nodes.searchInput.value = '0xc03a001a';
  env.nodes.searchInput.dispatch('input');
  env.runTimers(150);
  assert.equal(env.state(), 'results');
  let links = env.nodes.searchResults.querySelectorAll('.entry-link');
  assert(links.some((link) => new URL(link.href).pathname === '/posts/wsl-resize-error-0xc03a001a/'));
  assert(links.every((link) => link.attributes['aria-label']?.trim()));
  passed.push('real Fuse finds the resize error report and gives links accessible labels');

  env.nodes.searchInput.focus();
  assert.equal(env.document.key('ArrowDown').prevented, true);
  assert.equal(env.document.activeElement, links[0]);
  env.document.key('ArrowUp');
  assert.equal(env.document.activeElement, env.nodes.searchInput);
  env.document.key('ArrowDown');
  env.document.key('ArrowRight');
  assert.equal(links[0].clicked, true);
  env.document.key('Escape');
  assert.equal(env.state(), 'empty');
  assert.equal(env.nodes.searchInput.value, '');
  assert.equal(env.nodes.searchResults.children.length, 0);
  passed.push('arrow handlers, result activation and Escape clear/focus contract');

  env.nodes.searchInput.value = 'zzzxqvzzzxqvzzzxqv';
  env.nodes.searchInput.dispatch('input');
  env.runTimers(150);
  assert.equal(env.state(), 'no-results');
  assert.equal(env.nodes.searchRetry.hidden, true);
  env.nodes.searchInput.value = '';
  env.nodes.searchInput.dispatch('search');
  assert.equal(env.state(), 'empty');
  passed.push('no matching pages is distinct from failure and native clear resets it');

  for (const mode of ['http', 'network', 'json', 'shape', 'cross-origin', 'timeout']) {
    const failed = environment(mode);
    if (mode === 'timeout') failed.runTimers(10000);
    await settle();
    assert.equal(failed.state(), 'error', `${mode} must show an error`);
    assert.equal(failed.nodes.searchInput.disabled, true);
    assert.equal(failed.nodes.searchRetry.hidden, false);
    assert.equal(failed.nodes.searchResults.children.length, 0);
    assert.match(failed.nodes.searchStatus.textContent, /Start here.*All reports/);
    failed.nodes.searchRetry.focus();
    failed.document.key('Escape');
    assert.equal(failed.state(), 'error', 'Clear must not disguise an unloaded index');
    failed.mode('success');
    failed.nodes.searchRetry.dispatch('click');
    await settle();
    assert.equal(failed.state(), 'ready');
    assert.equal(failed.document.activeElement, failed.nodes.searchInput);
    assert.equal(failed.requests.length, 2);
    passed.push(`${mode}: explicit error, clear keeps error, retry recovers`);
  }
}

main().then(() => {
  const result = { status: 'PASS', checks: passed.length, cases: passed,
    scope: 'Actual built JS/Fuse, generated index, controlled requests and DOM double; no browser rendering, native keyboard, viewport or accessibility claim.' };
  if (process.argv[3]) fs.writeFileSync(process.argv[3], JSON.stringify(result, null, 2) + '\n');
  console.log(`PASS: ${passed.length} search runtime cases.`);
}).catch((error) => {
  const result = { status: 'FAIL', error: error.message, completed: passed,
    scope: 'JS/Fuse runtime with controlled requests and a DOM double.' };
  if (process.argv[3]) fs.writeFileSync(process.argv[3], JSON.stringify(result, null, 2) + '\n');
  console.error(`FAIL: ${error.message}`);
  process.exitCode = 1;
});
