"""Build the player edition into a validated stage; preserve successful output on failure."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from reading import Edition, esc
from sources import ROOT, retrieve
from publication import public_fingerprint, website_fingerprint


def build_indexes(site):
    lessons = site.reading['lessons']
    byid = {x['id']: x for x in lessons}
    config = site.config
    summaries = {
        'character': 'Start with the character guide, then use training and equipment to make your idea playable.',
        'combat': 'Learn your turn, how attacks resolve, and how equipment and defenses work together.',
        'world': 'Meet the societies, landscapes, and conflicts your character will travel through.',
        'peoples': 'Find a race, understand its heritage, and make a person of your own.',
        'magic': 'Begin with a working, then choose the tradition that fits your character.',
        'economy': 'Compare regions and follow food, fuel, labor, and waste through daily life.',
        'bestiary': 'Meet intelligent magical creatures and understand their place in the world.',
        'library': 'Focused guides and comparison sheets, organized by what you want to understand.',
        'development': 'A few details to settle with your GM before play.',
    }
    for key, title in config['sections'].items():
        selected = lessons if key == 'library' else [x for x in lessons if x['section'] == key]
        if key == 'character':
            selected = [byid[i] for i in ['character', 'training', 'races', 'equipment', 'enchantments', 'magic']]
        body = '<p class="lesson-lead">' + esc(summaries[key]) + '</p>' + site.cards(selected)
        if key == 'world':
            body += '<p><a href="/codex/">Read stories from Mystaria</a></p>'
        if key == 'combat':
            body += '<p><a href="/reference/weapon-enchantments/">Browse the full weapon enchantment catalogue</a></p>'
        if key == 'development':
            body = site.render('HP/d20 and Training Points are the game taught by this edition. Before play, agree your table’s starting sheet and training menu.\n\n## Ask your GM about these details\n\n- Five-stat racial starting arrays and incomplete racial packages.\n- Training prices, level-scaled benefits, and purchased-HP caps.\n- Actual weapon, armor, shield, and enchantment profiles where conversion is incomplete.\n- Unfinished magical purchases, exact channel values, and unusual status interactions.\n- Specific economic quotes outside the stated working examples.\n\nResearch candidates and historical rules remain in the source repositories. Their presence there does not make them automatic character options.')[0]
        site.shell('/sections/' + key + '/', title, body, key)
    home = '<p class="lesson-lead">A beautiful world with cruel roots. Learn the game, build your character, and explore Mystaria at your own pace.</p><a class="primary-button start-button" href="/learn/character/">Build your first character</a><h2>Begin your adventure</h2>' + site.cards([byid[i] for i in ['character', 'combat', 'magic', 'regions']]) + '<h2>Understand the world</h2>' + site.cards([byid[i] for i in ['economies', 'mana-economy', 'food']])
    site.shell('/', 'Mystaria: The Living Codex', home, 'world', hero=True)
    search = '<p class="lesson-lead">Find a rule, race, material, crop, discipline, or enchantment. Results take you straight to the relevant explanation.</p><label for="codex-q">Search the Codex</label><input id="codex-q" type="search" placeholder="Training Points, Dreamcatchers, Honed, Rosewheat…" autocomplete="off"><div class="search-filters"><label for="codex-section">Section</label><select id="codex-section"><option value="all">All sections</option>' + ''.join('<option>' + esc(s) + '</option>' for s in config['sections'].values()) + '</select><input type="hidden" id="codex-status" value="current"></div><p id="codex-count" role="status" aria-live="polite">Loading search index.</p><div id="codex-results"></div>'
    site.shell('/reference/search/', 'Search the Codex', search)
    site.shell('/reference/bookmarks/', 'My Bookmarks', '<p>Your saved reading stays in this browser.</p><div id="bookmarks-list"></div>')
    glossary = [('Attribute points', 'Allocated to broad base capabilities.', 'character'), ('SP — Skill Points', 'Buy learned skills, Crafts, and useful options.', 'training'), ('TP — Training Points', 'Buy individual derived-stat improvements.', 'training'), ('HP and Shimmer Reserve', 'Ordinary health and a Hero’s separate reserve.', 'health'), ('AR and AP', 'Armor Rating and the penetration reducing it.', 'equipment'), ('Evasion and Pressure', 'Avoiding attacks and tactical disadvantages.', 'combat'), ('MP and Channel Limit', 'Available energy and how much a working may channel.', 'magic'), ('Leywell and Soul Strain', 'Stored magical fuel and a distinct ongoing enhancement cost.', 'enchantments'), ('Honed / Hulking / Deflection', 'Specialized equipment tradeoffs.', 'equipment'), ('Managmins and Nectar', 'Dietary nutrition and Leshy cultivation resources.', 'food'), ('Dreamcatchers and Leydrains', 'Industrial waste collection and recovery.', 'mana-economy'), ('Hex, Haze, and Hexways', 'Alchemical pollution, ambient smog, and export infrastructure.', 'mana-economy'), ('Avowed and House Scrip', 'Canopy free citizenship and locally controlled currency.', 'society'), ('Celestial Recall', 'The return of a Starspawn and its unassimilated flesh.', 'creatures')]
    raw = 'A quick vocabulary sheet. Follow each term to the guide that explains how it works.\n\n' + '\n\n'.join('## ' + t + '\n\n' + d + ' [Read the guide](' + byid[i]['url'] + ').' for t, d, i in glossary)
    body, _ = site.render(raw)
    site.shell('/reference/glossary/', 'Terms at a glance', body)
    site.index_text('Terms at a glance', body, '/reference/glossary/', 'library')
    sources = '<p>This edition teaches HP/d20 and Training Points as the current game, by the author’s direction. The guides explain present rules; source manuscripts retain detailed history.</p><details class="source-notes"><summary>Edition revisions</summary><table><thead><tr><th>Repository</th><th>Build revision</th></tr></thead><tbody>' + ''.join('<tr><td>' + esc(v['repository']) + '</td><td><a href="https://github.com/' + v['repository'] + '/tree/' + v['commit'] + '">' + v['commit'][:12] + '</a></td></tr>' for v in site.revisions.values()) + '</tbody></table><p><a href="/build.json">Build metadata</a> · <a href="https://github.com/MyStalker/mystaria-living-codex">Website source and maintenance</a></p></details><p><a href="/sections/development/">Details to settle with your GM</a></p>' + site.source_links(list(site.documents))
    site.shell('/reference/sources/', 'Sources and further reading', sources)
    editorial = json.loads((ROOT / 'content/editorial.json').read_text(encoding='utf8'))
    volumes = []
    targets = {'world': 'regions', 'history': 'regions', 'divinity': 'regions', 'peoples': 'races', 'factions': 'society', 'shimmer': 'character', 'sorcery': 'sorcery', 'warlocks': 'manacraft', 'crafts': 'disciplines', 'jesters': 'jestercraft', 'starspawn': 'creatures', 'equipment': 'equipment'}
    for x in editorial['volumes']:
        title = x[1].replace('The Peoples of Mystaria', 'The Races of Mystaria')
        target = byid[targets[x[0]]]['url']
        site.shell('/codex/' + x[0] + '/', title, '<p class="small">A story from Mystaria · illustrative fiction</p><h2>' + esc(x[5]) + '</h2>' + site.render(x[6])[0] + '<p><a href="' + target + '">Explore this subject</a></p>', 'world')
        volumes.append(dict(url='/codex/' + x[0] + '/', title=title, summary=x[2], section='world'))
    site.shell('/codex/', 'Stories from Mystaria', site.cards(volumes), 'world')
    site.alias('/welcome/', '/learn/character/')
    for x in editorial['welcome']:
        site.alias('/welcome/' + x[0] + '/', '/learn/character/')
    site.shell('/codex/secrets/', 'Restricted reference', '<p>This public Codex contains player references.</p>')
    site.shell('/reference/calculators/', 'Classic rules calculators', '<p class="info">These preserved utilities calculate the earlier rules. They do not calculate the HP/Training Points system taught by the current guides.</p>' + (ROOT / 'content/calculators.html').read_text(encoding='utf8'), 'magic')
    source_targets = {}
    for doc in config['documents']:
        if doc.get('readingOnly'):
            continue
        related = next((x for x in lessons if doc['id'] in x['sources']), None)
        source_targets[doc['id']] = related['url'] if related else '/sections/' + doc['section'] + '/'
    source_targets.update({'combat': '/learn/combat/', 'world': '/world/regions/', 'equipment': '/learn/equipment/', 'canopy-economy': '/economy/mana/', 'enchantments': '/reference/weapon-enchantments/', 'sorcery': '/reference/sorcery/', 'warlock': '/reference/manacraft/', 'races': '/world/races/', 'smithcraft': '/reference/anvilcant/', 'leshy': '/economy/food/', 'nymbrin': '/economy/mana/'})
    for docid, target in source_targets.items():
        for prefix in ('library', 'history', 'development'):
            site.alias('/' + prefix + '/' + docid + '/', target)
    aliases = dict(config['aliases'])
    aliases.update(json.loads((ROOT / 'content/legacy-routes.json').read_text(encoding='utf8')))
    for old, target in aliases.items():
        site.alias(old, site.redirects.get(target, target))


def main(offline=False):
    config = json.loads((ROOT / 'content/public-manifest.json').read_text(encoding='utf8'))
    reading = json.loads((ROOT / 'content/reading-manifest.json').read_text(encoding='utf8'))
    revisions = retrieve(config, offline)
    stage = Path(tempfile.mkdtemp(prefix='.stage-', dir=ROOT))
    try:
        shutil.copytree(ROOT / 'assets', stage / 'assets')
        (stage / 'downloads').mkdir()
        site = Edition(config, reading, revisions, stage)
        for lesson in reading['lessons']:
            site.lesson(lesson)
        site.catalogue()
        build_indexes(site)
        for url, text in site.pages.items():
            dest = stage / url.lstrip('/') / 'index.html'
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding='utf8')
        (stage / '_redirects').write_text(''.join(old + ' ' + target + ' 301!\n' for old, target in sorted(site.redirects.items())), encoding='utf8')
        (stage / 'assets/search-index.json').write_text(json.dumps(site.search, ensure_ascii=False, separators=(',', ':')), encoding='utf8')
        provenance = {k: dict(repository=v['repository'], commit=v['commit']) for k, v in revisions.items()}
        build = dict(version='2.1.0', edition='Player guide', rules=reading['rules'], builtAt=datetime.now(timezone.utc).isoformat(), repositories=provenance, pages=len(site.pages), searchRecords=len(site.search), documents=site.report, websiteCommit=os.environ.get('COMMIT_REF') or os.environ.get('GITHUB_SHA') or 'local', readingManifestSha256=hashlib.sha256((ROOT / 'content/reading-manifest.json').read_bytes()).hexdigest())
        (stage / '404.html').write_text(site.pages['/reference/search/'].replace('<h1>Search the Codex</h1>', '<h1>Page not found — search the Codex</h1>'), encoding='utf8')
        (stage / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + config['site']['url'] + '/sitemap.xml\n', encoding='utf8')
        (stage / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + config['site']['url'] + esc(u) + '</loc></url>' for u in site.pages if u not in site.redirects) + '</urlset>', encoding='utf8')
        marker = json.loads((ROOT / 'content/source-revisions.json').read_text(encoding='utf8'))
        build.update(publicationSchema=1, publicationId=marker.get('requestId'),
                     publicContentSha256=public_fingerprint(stage, revisions),
                     websiteInputsSha256=website_fingerprint(ROOT))
        (stage / 'build.json').write_text(json.dumps(build, ensure_ascii=False, indent=2), encoding='utf8')
        from validate import validate
        result = validate(stage, config)
        if result['errors']:
            raise ValueError(json.dumps(result, ensure_ascii=False, indent=2))
        (stage / 'validation.json').write_text(json.dumps(result, indent=2), encoding='utf8')
        destination, backup = ROOT / 'dist', ROOT / '.stage-previous'
        if backup.exists():
            shutil.rmtree(backup)
        if destination.exists():
            destination.rename(backup)
        try:
            stage.rename(destination)
        except BaseException:
            if backup.exists():
                backup.rename(destination)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        print(json.dumps(dict(pages=len(site.pages), searchRecords=len(site.search), sources=provenance, validation=result), indent=2))
    finally:
        if stage.exists() and stage.resolve().is_relative_to(ROOT.resolve()):
            shutil.rmtree(stage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true')
    main(parser.parse_args().offline)
