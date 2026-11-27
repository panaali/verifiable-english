// Drives the shipped app.js Asimov section in a minimal DOM (no browser needed).
// Input (argv[2], JSON): {page, reruns: [{scenario, facts, result}]}; `result` is VE's
// answer from POST /api/asimov, computed by the Python test. Each re-run ticks the
// checkboxes to `facts`, clicks "Ask VE again" and checks where the card lands.
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

class Node {
  constructor(tag) {
    Object.assign(this, {tagName: tag.toUpperCase(), children: [], parentNode: null, className: '',
                         dataset: {}, attributes: {}, hidden: false, open: false, checked: false,
                         disabled: false, value: '', type: '', focused: false, text: ''});
    this.classList = {
      contains: name => this.className.split(' ').includes(name),
      toggle: (name, on) => { const set = new Set(this.className.split(' ').filter(Boolean));
        if (on === undefined ? !set.has(name) : on) set.add(name); else set.delete(name);
        this.className = [...set].join(' '); },
      add: name => this.classList.toggle(name, true), remove: name => this.classList.toggle(name, false),
    };
  }
  get textContent() { return this.text + this.children.map(c => c.textContent).join(''); }
  set textContent(value) { this.replaceChildren(); this.text = String(value); }
  append(...nodes) {
    for (const node of nodes) {
      if (typeof node === 'string') { const t = new Node('#text'); t.text = node; node = t; }
      if (node.parentNode) node.remove();
      node.parentNode = this; this.children.push(node);
    }
  }
  replaceChildren(...nodes) { for (const c of this.children) c.parentNode = null; this.children = []; this.text = ''; this.append(...nodes); }
  remove() { const p = this.parentNode; if (p) { p.children.splice(p.children.indexOf(this), 1); this.parentNode = null; } }
  replaceWith(node) { const p = this.parentNode; const i = p.children.indexOf(this); node.remove();
    p.children[i] = node; node.parentNode = p; this.parentNode = null; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return this.attributes[name]; }
  addEventListener() {}
  focus() { focused = this; }
  scrollIntoView() {}
  showModal() {} close() {}
  matches(selector) {
    const [tag, ...classes] = selector.split('.');
    return (!tag || this.tagName === tag.toUpperCase()) && classes.every(c => this.classList.contains(c));
  }
  *walk() { for (const c of this.children) { yield c; yield* c.walk(); } }
  querySelectorAll(selector) {
    const parts = selector.split(' ');
    let found = [this];
    for (const part of parts) found = found.flatMap(n => [...n.walk()].filter(m => m.matches(part)));
    return [...new Set(found)];
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

let focused = null;
const elements = {};
const document = {
  getElementById: id => elements[id] || (elements[id] = new Node('div')),
  createElement: tag => new Node(tag),
  querySelectorAll: () => [], addEventListener() {},
  documentElement: new Node('html'),
};
const input = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let answer = null;
const fetch = async (url, options = {}) => {
  if (url === '/api/asimov' && options.method === 'POST') {
    const body = JSON.parse(options.body);
    assert.deepStrictEqual(body, {scenario: answer.scenario, facts: answer.facts});
    return {ok: true, status: 200, json: async () => answer.result};
  }
  return {ok: false, status: 401, json: async () => ({error: {code: 'Unauthorized', message: 'signed out'}})};
};
const context = vm.createContext({
  document, fetch, window: {addEventListener() {}}, localStorage: {getItem: () => null, setItem() {}},
  matchMedia: () => ({matches: false}), setTimeout: () => 0, clearTimeout() {}, console,
  confirm: () => true, prompt: () => null, crypto: {randomUUID: () => '0'},
});
vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 've_webapp', 'static', 'app.js'), 'utf8'), context);

const sections = {approves: 'asimovApproves', rejects: 'asimovRejects', limits: 'asimovLimits'};
const cardsIn = group => document.getElementById(sections[group]).children.filter(n => n.matches('article.asimov-card'));
const allCards = () => Object.keys(sections).flatMap(cardsIn);
const title = card => card.querySelector('h3').textContent;
function lawOf(card) {  // The law heading the card sits under, if its section has headings.
  const siblings = card.parentNode.children;
  for (let i = siblings.indexOf(card); i >= 0; i--) if (siblings[i].matches('h3.asimov-law')) return siblings[i].textContent;
  return null;
}
function checkLayout(scenarios) {
  const cards = allCards();
  assert.strictEqual(cards.length, scenarios.length, 'every scenario has exactly one card');
  for (const s of scenarios) {
    const matching = cards.filter(card => title(card) === s.title && card.querySelector('p').textContent === s.situation);
    assert.strictEqual(matching.length, 1, `one card shows ${s.id} with its current description`);
    const [card] = matching;
    assert.ok(cardsIn(s.group).includes(card), `${s.id} (${s.verdict}) sits under ${s.group}`);
    assert.strictEqual(lawOf(card), s.group === 'limits' ? null : input.page.groups[s.law], `${s.id} law heading`);
    assert.strictEqual(card.querySelector('div.asimov-verdict span.badge').textContent !== 'Unknown', true);
  }
  for (const group of Object.keys(sections)) {  // No law heading is left without cards.
    const nodes = document.getElementById(sections[group]).children;
    nodes.forEach((n, i) => { if (n.matches('h3.asimov-law')) assert.ok(nodes[i + 1] && nodes[i + 1].matches('article.asimov-card'), `empty heading in ${group}`); });
  }
}

(async () => {
  context.renderAsimov(input.page);
  let scenarios = input.page.scenarios.map(s => s);
  checkLayout(scenarios);
  const moved = [];
  for (const rerun of input.reruns) {
    const before = scenarios.find(s => s.id === rerun.scenario);
    const card = allCards().find(c => title(c) === before.title && c.querySelector('p').textContent === before.situation);
    // A pending edit on another card must survive the re-layout.
    const other = allCards().find(c => c !== card && c.querySelector('input'));
    const otherBox = other && other.querySelector('input');
    if (otherBox) otherBox.checked = !otherBox.checked;
    const pending = otherBox && otherBox.checked;
    for (const box of card.querySelectorAll('input')) box.checked = rerun.facts[box.dataset.fact];
    answer = rerun;
    await card.querySelector('details.asimov-edit button').onclick();
    assert.strictEqual(document.getElementById('notice').textContent, '', 'the re-run shows no error');
    scenarios = scenarios.map(s => s.id === rerun.scenario ? rerun.result : s);
    checkLayout(scenarios);
    const fresh = allCards().find(c => title(c) === rerun.result.title && c.querySelector('p').textContent === rerun.result.situation);
    assert.ok(fresh.textContent.includes('VE decided this again just now'), 'fresh card is marked live');
    assert.ok(fresh.querySelector('details.asimov-edit').open, 'fact editor stays open');
    assert.strictEqual(focused, fresh.querySelector('details.asimov-edit button'), 'focus follows the card');
    assert.strictEqual(fresh.querySelector('div.asimov-verdict').textContent,
                       rerun.result.options.find(o => o.id === rerun.result.focus).label +
                       {required: 'Required', permitted: 'Permitted', forbidden: 'Forbidden', 'ruled out': 'Ruled out',
                        'no clear action': 'No clear action'}[rerun.result.verdict]);
    if (otherBox) {
      assert.strictEqual(otherBox.checked, pending, 'another card keeps its unsent edit');
      otherBox.checked = !otherBox.checked;
    }
    if (before.group !== rerun.result.group) moved.push(rerun.scenario);
  }
  process.stdout.write(JSON.stringify({moved}));
})().catch(error => { console.error(error.stack || error); process.exit(1); });
