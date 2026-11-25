(() => {
  'use strict';
  const normalize = value => String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

  function revealFragment() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;
    if (target.matches('details')) target.open = true;
    for (let parent = target.parentElement; parent; parent = parent.parentElement) {
      if (parent.matches('details')) parent.open = true;
    }
    requestAnimationFrame(() => target.scrollIntoView({block: 'start'}));
  }
  revealFragment();
  window.addEventListener('hashchange', revealFragment);

  let printState = [];
  window.addEventListener('beforeprint', () => {
    printState = Array.from(document.querySelectorAll('details.deep-dive'), d => [d, d.open]);
    printState.forEach(([d]) => { d.open = true; });
  });
  window.addEventListener('afterprint', () => printState.forEach(([d, open]) => { d.open = open; }));
  document.querySelectorAll('.print-page').forEach(button => button.addEventListener('click', () => window.print()));

  const filter = document.getElementById('catalogue-filter');
  if (filter) {
    const entries = Array.from(document.querySelectorAll('details.deep-dive'));
    filter.addEventListener('input', () => {
      const tokens = normalize(filter.value).trim().split(/\s+/).filter(Boolean);
      let visible = 0;
      for (const entry of entries) {
        entry.hidden = !tokens.every(t => normalize(entry.textContent).includes(t));
        if (!entry.hidden) visible++;
      }
      document.getElementById('catalogue-count').textContent = visible + (visible === 1 ? ' enchantment' : ' enchantments');
    });
  }

  const q = document.getElementById('codex-q');
  if (!q) return;
  const section = document.getElementById('codex-section');
  const count = document.getElementById('codex-count');
  const results = document.getElementById('codex-results');
  const synonyms = {stats: ['stats', 'attributes'], armour: ['armour', 'armor'], health: ['health', 'hp'], race: ['race', 'races'], training: ['training', 'tp']};
  let data = [];
  function search() {
    const tokens = normalize(q.value).trim().split(/\s+/).filter(Boolean);
    const groups = tokens.map(t => synonyms[t] || [t]);
    const scope = document.getElementById('codex-status');
    const found = data.filter(x => (scope.value === 'all' || x.status === 'reference') && (section.value === 'all' || x.category === section.value)).map(x => {
      const title = normalize(x.title), text = normalize(x.text);
      let score = x.kind === 'entry' ? 1 : 0;
      for (const group of groups) {
        if (group.some(t => title.includes(t))) score += 20;
        else if (group.some(t => text.includes(t))) score += 2;
        else return null;
      }
      return {...x, score};
    }).filter(Boolean).filter(x => tokens.length || x.kind === 'entry').sort((a, b) => b.score - a.score || a.title.localeCompare(b.title));
    const shown = found.slice(0, 40);
    count.textContent = found.length + ' results' + (found.length > 40 ? ' · first 40 shown' : '');
    results.replaceChildren();
    if (!shown.length) {
      const empty = document.createElement('p');
      empty.textContent = 'No matching guide. Try a shorter term or another section.';
      results.append(empty);
    }
    for (const x of shown) {
      const box = document.createElement('div'); box.className = 'search-result';
      const link = document.createElement('a'); link.href = x.url; link.textContent = x.title;
      const category = document.createElement('small'); category.textContent = x.category;
      const summary = document.createElement('p');
      const first = tokens[0] || '';
      const pos = first ? Math.max(0, normalize(x.text).indexOf(first)) : 0;
      summary.textContent = (pos > 55 ? '…' : '') + x.text.slice(Math.max(0, pos - 55), pos + 210) + (x.text.length > pos + 210 ? '…' : '');
      box.append(link, category, summary); results.append(box);
    }
  }
  const initial = new URLSearchParams(location.search);
  q.value = initial.get('q') || '';
  fetch('/assets/search-index.json').then(r => {
    if (!r.ok) throw Error('index');
    return r.json();
  }).then(index => { data = index; search(); }).catch(() => {
    count.textContent = 'Search is temporarily unavailable. Use Explore the Codex to browse the guides.';
  });
  let debounce;
  q.addEventListener('input', () => { clearTimeout(debounce); debounce = setTimeout(search, 90); });
  section.addEventListener('change', search);
})();
