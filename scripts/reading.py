"""Player-facing rendering and explicitly selected, live public source tables."""
from collections import Counter
import html
import json
import re
import unicodedata
from urllib.parse import quote
from markdown_it import MarkdownIt
from math_render import protect as protect_math
from sources import ROOT, CACHE, select


def esc(value):
    return html.escape(str(value), quote=True)


def slug(value):
    text = unicodedata.normalize('NFKD', re.sub(r'[*`\\]', '', value)).lower()
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9_-]+', '-', text)).strip('-') or 'section'


def plain(value):
    return ' '.join(html.unescape(re.sub('<[^>]+>', ' ', value)).split())


class Edition:
    def __init__(self, config, reading, revisions, stage):
        self.config, self.reading, self.revisions, self.stage = config, reading, revisions, stage
        self.pages, self.search, self.redirects = {}, [], {}
        self.documents = {d['id']: d for d in config['documents']}
        self.blocks, self.report = {}, []
        for doc in config['documents']:
            selected, removed = select(doc, config, (CACHE / doc['repository'] / doc['path']).read_text(encoding='utf8'))
            self.blocks[doc['id']] = selected
            self.report.append(dict(id=doc['id'], repository=doc['repository'], path=doc['path'], selected=len(selected), excludedSections=len(removed)))

    def block(self, docid, pattern):
        found = [b for b in self.blocks[docid] if re.search(pattern, b['title'], re.I)]
        if len(found) != 1:
            raise ValueError(f'Expected one current public source block: {docid} / {pattern}; got {len(found)}')
        return found[0]['body']

    @staticmethod
    def tables(text):
        return re.findall(r'(?m)^\|.*\n\|[- :|]+\n(?:\|.*(?:\n|$))+', text)

    def table(self, name):
        selectors = {
            'health-curve': ('combat', r'HP/d20 replacement attribute scaling'),
            'enchantment-modes': ('equipment', r'Blank, Mixed and Full enchantment modes'),
            'sorcery-costs': ('sorcery', r'^II\. Skill Point ledger'),
            'sorcery-red': ('sorcery', r'^Red —'),
            'sorcery-green': ('sorcery', r'^Green —'),
            'sorcery-white': ('sorcery', r'^White —'),
        }
        if name == 'sleep-recovery':
            text = self.block('combat', r'ADDITIVE-HP PROTOTYPE: armor, carrying tradeoffs, and sleep healing')
            m = re.search(r'Ordinary characters recover \*\*(\d+)%\*\*.*?or \*\*(\d+)%\*\*.*?Heroes recover \*\*(\d+)%\*\*.*?or \*\*(\d+)%\*\*', text, re.S)
            if not m:
                raise ValueError('Sleep recovery data changed shape; review the health lesson')
            a, b, c, d = m.groups()
            return f'| Character | Qualifying sleep | Sleep with medical attention |\n|---|---:|---:|\n| Ordinary | {a}% of maximum ordinary HP | {b}% |\n| Hero | {c}% of maximum ordinary HP | {d}% |'
        if name == 'sorcery-blue':
            return 'The complete approved Blue name list is not currently available. Ask your GM for the specific available Incantation and alteration before purchasing it.'
        if name == 'sorcery-black':
            groups = []
            for b in self.blocks['sorcery']:
                if b['level'] == 4 and any('Black —' in p for p in b['parents']):
                    tables = self.tables(b['body'])
                    if tables:
                        groups.append('::: detail ' + b['title'] + '\n' + '\n\n'.join(tables) + '\n:::')
            if len(groups) != 5:
                raise ValueError('Expected the five approved Black Sorcery groups')
            return '\n\n'.join(groups)
        docid, pattern = selectors[name]
        tables = self.tables(self.block(docid, pattern))
        if not tables:
            raise ValueError('Missing live source table: ' + name)
        table = tables[0]
        if name == 'enchantment-modes':
            # Later slot-based scaling governs actual effect values; the older table's
            # Quality-derived one-tier phrase is not the current catalogue rule.
            table = re.sub(r'(?m)^\| \*\*Full\*\*.*$', '| **Full** | **No stat enhancement** from this mode | Stronger magical effect; use the named Full values |', table)
        if name == 'health-curve':
            table = '\n'.join('| ' + ' | '.join(line.strip('| ').split('|')[:2]) + ' |' for line in table.strip().splitlines())
            table = table.replace('Effective attribute band', 'Effective END band')
        if name.startswith('sorcery-') and name != 'sorcery-costs':
            # Base identity columns only; recovery/approval notes belong in the repository.
            table = '\n'.join('| ' + ' | '.join(line.strip('| ').split('|')[:2]) + ' |' for line in table.strip().splitlines())
        return table

    def expand(self, text):
        return re.sub(r'\{\{table:([a-z-]+)\}\}', lambda m: self.table(m[1]), text)

    def render(self, text):
        text, equations = protect_math(text)
        md = MarkdownIt('default', {'html': False}).enable('table')
        ids, toc, details = Counter(), [], []
        def anchor(title):
            base = slug(title)
            ids[base] += 1
            return base + (('-' + str(ids[base] - 1)) if ids[base] > 1 else '')
        def heading(renderer, tokens, i, options, env):
            title = tokens[i + 1].content
            key = anchor(title)
            tokens[i].attrSet('id', key)
            if tokens[i].tag == 'h2':
                toc.append((key, plain(md.renderInline(title))))
            return renderer.renderToken(tokens, i, options, env)
        md.add_render_rule('heading_open', heading)
        def detail(match):
            key = anchor(match[1])
            details.append('<details class="deep-dive" id="' + key + '"><summary>' + esc(match[1]) + '</summary><div class="detail-content">' + md.render(match[2]) + '</div></details>')
            return '\n\nCODEXDETAIL' + str(len(details) - 1) + 'END\n\n'
        text = re.sub(r'(?ms)^::: detail ([^\n]+)\n(.*?)^:::[ \t]*$', detail, text)
        if re.search(r'^:::', text, re.M):
            raise ValueError('Unbalanced optional detail block')
        body = md.render(text)
        for i, value in enumerate(details):
            body = body.replace('<p>CODEXDETAIL' + str(i) + 'END</p>', value)
        for i, value in enumerate(equations):
            body = body.replace('MYSTARIAMATHPLACEHOLDER' + str(i) + 'END', value)
        def table_layout(match):
            content = match[1]
            headers = [plain(x) for x in re.findall(r'<th(?:\s[^>]*)?>(.*?)</th>', content, re.S)]
            def row_layout(row):
                column = 0
                def cell(cell_match):
                    nonlocal column
                    label = headers[column] if column < len(headers) else ''
                    column += 1
                    return '<td' + cell_match[1] + ' role="cell" data-label="' + esc(label) + '">'
                return '<tr role="row">' + re.sub(r'<td([^>]*)>', cell, row[1]) + '</tr>'
            content = re.sub(r'<tr>(.*?)</tr>', row_layout, content, flags=re.S)
            content = re.sub(r'<th(?=[\s>])', '<th scope="col" role="columnheader"', content)
            style = ' class="mobile-cards"' if len(headers) > 2 else ''
            return '<div class="table-scroll" role="region" aria-label="Reference table" tabindex="0"><table role="table"' + style + '>' + content + '</table></div>'
        body = re.sub(r'<table>(.*?)</table>', table_layout, body, flags=re.S)
        body = body.replace('<p>', '<p class="lesson-lead">', 1)
        return body, toc

    def cards(self, lessons):
        return '<div class="card-grid">' + ''.join('<a class="tile" href="' + esc(x['url']) + '"><span class="kicker">' + esc(self.config['sections'].get(x['section'], 'Guide')) + '</span><h3>' + esc(x['title']) + '</h3><p>' + esc(x['summary']) + '</p></a>' for x in lessons) + '</div>'

    def shell(self, url, title, body, section='library', canonical=None, hero=False):
        name = self.config['sections'].get(section, 'Reference')
        nav = ''.join('<a href="' + u + '"' + (' aria-current="page"' if u == url else '') + '>' + label + '</a>' for u, label in [('/', 'Home'), ('/learn/character/', 'Start here'), ('/reference/search/', 'Search'), ('/reference/bookmarks/', 'Bookmarks')])
        side = '<a class="start-link" href="/learn/character/">Build a character</a>' + ''.join('<a href="/sections/' + k + '/"' + (' aria-current="page"' if k == section else '') + '>' + esc(v) + '</a>' for k, v in self.config['sections'].items())
        art = '<img class="cover-art" src="/assets/enchanted-city.jpg" alt="An enchanted fantasy city beneath Mystaria’s purple skies">' if hero else ''
        self.pages[url] = f'''<!doctype html><html lang="en" data-page="{esc(url.lstrip('/')+'index.html')}" data-title="{esc(title)}" data-root="/"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(title + ': a player’s guide to Mystaria.')}"><meta name="theme-color" content="#251b35"><title>{esc(title)} · Mystaria</title><link rel="canonical" href="{self.config['site']['url']}{esc(canonical or url)}"><link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/codex.css"><script defer src="/assets/site.js"></script><script defer src="/assets/reader.js"></script></head><body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="header-inner"><a class="brand" href="/"><span class="brand-symbol" aria-hidden="true">✧</span><span>MYSTARIA<small>The Living Codex</small></span></a><button class="theme-toggle" data-theme-toggle aria-label="Toggle light and dark reading theme">☾</button><button class="menu-btn" id="mobile-menu" aria-label="Open menu" aria-expanded="false" aria-controls="global-nav side-nav">Menu</button><nav class="nav-links" id="global-nav" aria-label="Main navigation">{nav}</nav></div></header><div class="layout"><aside class="sidebar" id="side-nav"><h3>Explore the Codex</h3>{side}<h3>Reading tools</h3><a href="/reference/glossary/">Terms at a glance</a><a href="/reference/sources/">Sources and further reading</a></aside><main class="main-pane" id="main"><article class="paper"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Mystaria</a><span>›</span><a href="/sections/{section}/">{esc(name)}</a><span>›</span><span>{esc(title)}</span></nav><div class="eyebrow">{esc(name)}</div><h1>{esc(title)}</h1><div class="reading-actions"><button class="bookmark-toggle" type="button" data-bookmark-toggle>☆ Save this page</button><button class="print-page" type="button">Print this guide</button></div>{art}{body}</article></main></div><footer class="footer">Mystaria · The Living Codex · <a href="/reference/sources/">Sources and edition</a></footer></body></html>'''

    def index_text(self, title, body, url, section, status='reference'):
        def row(title, text, url, kind):
            return dict(title=plain(title), text=plain(text), summary=plain(text)[:220], url=url, category=self.config['sections'].get(section, section), status=status, kind=kind)
        self.search.append(row(title, body, url, 'entry'))
        for part in re.split(r'(?=<h2\b|<details class="deep-dive")', body):
            m = re.match(r'(?:<h2 id="([^"]+)">(.+?)</h2>|<details class="deep-dive" id="([^"]+)"><summary>(.+?)</summary>)', part, re.S)
            if m:
                key, heading = (m[1], m[2]) if m[1] else (m[3], m[4])
                self.search.append(row(heading, part, url + '#' + key, 'section'))

    def source_links(self, ids):
        links = []
        for docid in ids:
            doc = self.documents[docid]
            rev = self.revisions[doc['repository']]
            path = rev.get('resolvedPaths', {}).get(doc['path'], doc['path'])
            url = 'https://github.com/' + rev['repository'] + '/blob/' + rev['commit'] + '/' + quote(path, safe='/')
            links.append('<li><a href="' + url + '">' + esc(doc['title']) + '</a></li>')
        return '<details class="source-notes"><summary>Sources and further reading</summary><p>Detailed manuscripts and revision history are maintained on GitHub.</p><ul>' + ''.join(links) + '</ul></details>'

    def lesson(self, x):
        blocks = self.blocks[x['document']]
        raw = self.expand('\n\n'.join(('#' * b['level'] + ' ' + b['title'] + '\n\n' if b['level'] > 1 else '') + b['body'] for b in blocks))
        body, toc = self.render(raw)
        if toc:
            contents = '<details class="lesson-toc"><summary>In this guide</summary><nav aria-label="On this page">' + ''.join('<a href="#' + key + '">' + label + '</a>' for key, label in toc) + '</nav></details>'
            split = body.find('</p>') + 4
            body = body[:split] + contents + body[split:]
        status = x.get('status', 'reference')
        self.index_text(x['title'], body, x['url'], x['section'], status)
        if status != 'reference':
            labels = {'proposal': 'Unapproved proposal: this is not a player option.', 'experimental': 'Optional experiment: use only with your GM’s explicit selection.'}
            body = '<p class="info">' + esc(labels.get(status, 'Optional development reference.')) + '</p>' + body
        self.shell(x['url'], x['title'], body + self.source_links(x['sources']) + '<p class="guide-download"><a href="/downloads/guide-' + x['id'] + '.md" download>Download this guide as Markdown</a></p>', x['section'])
        (self.stage / 'downloads' / ('guide-' + x['id'] + '.md')).write_text('# ' + x['title'] + '\n\n' + raw, encoding='utf8')

    def catalogue(self):
        raw = 'Choose an effect for the actions you actually use. Each entry lists eligibility, trigger, strength, limits, and counterplay. Use the named Mixed or Full values and actual legally occupied slots.\n\nHP-system conversion and some installation MP/color assignments remain incomplete; confirm the actual item with your GM. [How enchantments work](/learn/enchantments/) explains modes and powering.\n\n'
        items = [b for b in self.blocks['enchantments'] if b['level'] == 3]
        items = [b for b in items if b['status'] == 'reference']
        if not items:
            raise ValueError('No approved public enchantment entries selected')
        raw += '\n\n'.join('::: detail ' + b['title'] + '\n' + b['body'] + '\n:::' for b in items)
        body, _ = self.render(raw)
        body = '<label class="catalogue-label" for="catalogue-filter">Find an enchantment by name, trigger, or weapon</label><input type="search" id="catalogue-filter" placeholder="Try Backstab, shield, reach…"><p id="catalogue-count" role="status" aria-live="polite">' + str(len(items)) + ' enchantments</p>' + body
        self.index_text('Weapon enchantment catalogue', body, '/reference/weapon-enchantments/', 'combat')
        self.shell('/reference/weapon-enchantments/', 'Weapon enchantment catalogue', body + self.source_links(['enchantments']), 'combat')

    def alias(self, old, target):
        if old in self.pages or old == target:
            return
        self.redirects[old] = target
        self.shell(old, 'Continue reading the Codex', '<p>This address now leads to a focused player guide.</p><p><a class="primary-button" href="' + esc(target) + '">Open the guide</a></p>', canonical=target)
