"""Static Living Codex renderer. Stage, validate, then atomically replace dist."""
import argparse,hashlib,html,json,os,re,shutil,sys,tempfile,unicodedata
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote,urlsplit,unquote
from markdown_it import MarkdownIt
from sources import ROOT,CACHE,retrieve,select,git_hash

LABELS={'reference':'Reference · revisions apply','experimental':'Approved experimental rules','proposal':'Unapproved development proposal','historical':'Historical / superseded','revision':'Under major revision','incomplete':'Incomplete reference','development':'Development · approval varies'}
CONFIG=json.loads((ROOT/'content/public-manifest.json').read_text(encoding='utf8'))
ED=json.loads((ROOT/'content/editorial.json').read_text(encoding='utf8'))
def esc(s):return html.escape(str(s),quote=True)
def slug(s):
    s=unicodedata.normalize('NFKD',re.sub(r'[*`\\]','',s)).lower()
    return re.sub(r'-{2,}','-',re.sub(r'[^a-z0-9_-]+','-',s)).strip('-') or 'section'
def route(doc,development=False):return ('/development/' if development or doc['section']=='development' else '/library/')+doc['id']+'/'
def badge(status):return '<span class="badge '+esc(status)+'">'+esc(LABELS[status])+'</span>'
def clean_links(value,doc):
    v=unquote(value);u=urlsplit(v)
    if u.scheme:
        return value if u.scheme in ('https','http','mailto') else '#restricted-reference'
    if v.startswith('#'):return v
    path=v.split('#')[0]
    if re.search(r'(^|/)(campaigns?|reports/experimental/2026|\.git|secrets?)(/|$)',path,re.I):return '#restricted-reference'
    target=next((d for d in CONFIG['documents'] if d['repository']==doc['repository'] and Path(d['path']).name==Path(path).name),None)
    if target:
        if '#' in v:
            fragment=slug(v.split('#',1)[1])
            return ANCHOR_ROUTES.get((target['id'],fragment),route(target))+'#'+fragment
        return route(target)
    if path=='Mystaria_Mana_Emblems_Approved.png':return 'https://raw.githubusercontent.com/MyStalker/mystaria-codex/'+REVISIONS['canon']['commit']+'/'+path
    if '.md' in path:return '#restricted-reference'
    return '#restricted-reference'
def render(text,doc=None):
    # Preserve TeX through Markdown escaping. MathJax enhances this readable fallback.
    protected=[]
    def math(m):
        i=len(protected);tex=m[0];protected.append('<span class="math">'+esc(tex)+'</span>');return 'MYSTARIAMATHPLACEHOLDER'+str(i)+'END'
    text=re.sub(r'(?s)\$\$.+?\$\$|\\\[.+?\\\]|\\\(.+?\\\)',math,text)
    md=MarkdownIt('default',{'html':False,'typographer':False,'breaks':False}).enable('table')
    if doc:
        def link(self,tokens,i,options,env):
            tokens[i].attrSet('href',clean_links(tokens[i].attrGet('href') or '',doc))
            return self.renderToken(tokens,i,options,env)
        def image(self,tokens,i,options,env):
            src=tokens[i].attrGet('src') or ''
            if 'Mystaria_Mana_Emblems_Approved.png' not in src:return '<p class="small">Artwork reference omitted pending public asset review.</p>'
            tokens[i].attrSet('src',clean_links('Mystaria_Mana_Emblems_Approved.png',doc));tokens[i].attrSet('loading','lazy')
            return self.renderToken(tokens,i,options,env)
        md.add_render_rule('link_open',link);md.add_render_rule('image',image)
    body=md.render(text).replace('<table>','<div class="table-scroll" role="region" aria-label="Reference table" tabindex="0"><table>').replace('</table>','</table></div>')
    for i,m in enumerate(protected):body=body.replace('MYSTARIAMATHPLACEHOLDER'+str(i)+'END',m)
    return body
def plain(body):return ' '.join(html.unescape(re.sub('<[^>]+>',' ',body)).split())
PAGES={};SEARCH=[];REPORT=[];SEARCH_KEYS=set();ANCHOR_ROUTES={}
def cards(items):return '<div class="card-grid">'+''.join('<a class="tile" href="'+esc(url)+'"><span class="kicker">'+esc(kicker)+'</span><h3>'+esc(title)+'</h3><p>'+esc(desc)+'</p></a>' for url,title,desc,kicker in items)+'</div>'
def shell(url,title,body,section='library',status='reference',hero=False):
    section_name=CONFIG['sections'].get(section,section)
    nav=[('/','Home'),('/welcome/','Welcome'),('/reference/search/','Search'),('/reference/bookmarks/','Bookmarks'),('/reference/sources/','Sources')]
    top=''.join('<a href="'+u+'"'+(' aria-current="page"' if u==url else '')+'>'+t+'</a>' for u,t in nav)
    sidebar=''.join('<a href="/sections/'+k+'/"'+(' aria-current="page"' if k==section else '')+'>'+esc(v)+'</a>' for k,v in CONFIG['sections'].items())
    sidebar+='<h3>Reading tools</h3><a href="/reference/calculators/">Operative calculators</a><a href="/reference/canon-status/">Canon status</a><a href="/reference/sources/">Sources and build revisions</a>'
    if hero:body='<img class="cover-art" src="/assets/enchanted-city.jpg" alt="The inherited Living Codex illustration: an enchanted fantasy city beneath purple skies">'+body
    h='<div class="eyebrow">'+esc(section_name)+'</div><h1>'+esc(title)+'</h1>'
    doc='<!doctype html><html lang="en" data-page="'+esc(url.lstrip('/')+'index.html')+'" data-title="'+esc(title)+'" data-root="/"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="'+esc(title+' — Mystaria lore and tabletop reference with source revisions and status boundaries.')+'"><meta name="theme-color" content="#251b35"><title>'+esc(title)+' · Mystaria</title><link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/codex.css"><link rel="canonical" href="'+CONFIG['site']['url']+esc(url)+'"><script defer src="/assets/site.js"></script><script defer src="/assets/reader.js"></script></head><body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="header-inner"><a class="brand" href="/"><span class="brand-symbol" aria-hidden="true">✧</span><span>MYSTARIA<small>The Living Codex</small></span></a><button class="theme-toggle" data-theme-toggle aria-label="Toggle light and dark reading theme">☾</button><button class="menu-btn" id="mobile-menu" aria-label="Open menu" aria-expanded="false" aria-controls="global-nav side-nav">Menu</button><nav class="nav-links" id="global-nav" aria-label="Main navigation">'+top+'</nav></div></header><div class="layout"><aside id="side-nav" class="sidebar"><h3>Explore the Codex</h3>'+sidebar+'</aside><main class="main-pane" id="main"><article class="paper"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Mystaria</a><span>›</span><a href="/sections/'+section+'/">'+esc(section_name)+'</a><span>›</span><span>'+esc(title)+'</span></nav>'+h+'<div class="badges">'+badge(status)+'<button class="bookmark-toggle" type="button" data-bookmark-toggle>☆ Save this page</button></div>'+body+'</article></main></div><footer class="footer">Mystaria · The Living Codex 2.0 · <a href="/reference/sources/">Source revisions '+REVISIONS['canon']['commit'][:7]+' / '+REVISIONS['economy']['commit'][:7]+'</a> · <a href="/reference/canon-status/">Canon policy</a></footer><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script></body></html>'
    PAGES[url]=doc
def add_search(title,text,url,section,status,kind='section'):
    content=plain(text)
    key=(title,None if re.match(r'^\w+ \d{1,2}, \d{4}',title) else content,status,kind)
    if key in SEARCH_KEYS:return
    SEARCH_KEYS.add(key)
    SEARCH.append(dict(title=title,text=content,summary=content[:240],url=url,category=CONFIG['sections'].get(section,section),status=status,kind=kind))
def document(doc):
    source=(CACHE/doc['repository']/doc['path']).read_text(encoding='utf8')
    blocks,removed=select(doc,CONFIG,source)
    groups={'normal':[],'development':[],'history':[]}
    for b in blocks:
        group='history' if b['status']=='historical' else 'development' if b['status'] in ('experimental','proposal') or doc['section']=='development' else 'normal'
        groups[group].append(b)
    REPORT.append(dict(id=doc['id'],repository=doc['repository'],path=doc['path'],selected=len(blocks),counts={k:len(v) for k,v in groups.items()},excludedSections=len(removed)))
    for group,items in groups.items():
        if not items:continue
        url='/history/'+doc['id']+'/' if group=='history' else route(doc,group=='development')
        title=doc['title']+(' — historical passages' if group=='history' else ' — development' if group=='development' and doc['section']!='development' else '')
        statuses={b['status'] for b in items}
        page_status='historical' if group=='history' else (next(iter(statuses)) if len(statuses)==1 and statuses<={'proposal','experimental'} else 'development') if group=='development' else doc['status'] if doc['status']=='revision' else 'reference'
        rev=REVISIONS[doc['repository']];resolved=rev.get('resolvedPaths',{}).get(doc['path'],doc['path'])
        source_url='https://github.com/'+rev['repository']+'/blob/'+rev['commit']+'/'+quote(resolved,safe='/')
        body='<p class="info">'+('These are development references. Approval to experiment does not replace operative rules. Individual proposals and unresolved values retain their stated status.' if group=='development' else 'This reference preserves the source’s qualifications, approvals and unresolved decisions. Later explicit approvals govern earlier conflicting passages. Read the revision notes before using a rule.')+'</p>'
        body+='<p class="source-line"><a href="'+source_url+'">View source at '+rev['commit'][:12]+'</a> · <a href="/downloads/'+doc['id']+'-'+group+'.md" download>Download public Markdown</a></p>'
        related=[]
        if groups['normal'] and group!='normal':related.append((route(doc),'Operative/reference passages','Keep the two systems distinct.','Reference'))
        if groups['development'] and group!='development':related.append((route(doc,True),'Development and experimental passages','Approved experiments and proposals retain their stated boundaries.','Development'))
        if groups['history'] and group!='history':related.append(('/history/'+doc['id']+'/','Historical passages','Superseded headings; excluded from ordinary search.','History'))
        body+=cards(related)
        anchors=Counter();toc=[];parts=[];mdparts=['# '+title,'Source: '+source_url,'Status: '+LABELS[page_status],'> Public excerpt. Omitted/private passages are not included. Later explicit approvals take precedence.']
        for b in items:
            anchor=slug(b['title']);anchors[anchor]+=1
            if anchors[anchor]>1:anchor+='-'+str(anchors[anchor]-1)
            content=render(b['body'],doc)
            if b['level']<=2:toc.append('<a href="#'+anchor+'">'+esc(b['title'])+'</a>')
            tag='h'+str(max(2,min(6,b['level'])))
            parts.append('<section id="'+anchor+'" class="reference-section"><'+tag+'>'+esc(b['title'])+'</'+tag+'>'+badge(b['status'])+content+'</section>')
            mdparts+=['## '+b['title'],b['body']]
            add_search(b['title'],content,url+'#'+anchor,doc['section'],b['status'])
        body+='<details class="page-toc"><summary>On this page ('+str(len(items))+' sections)</summary><nav aria-label="On this page">'+''.join(toc)+'</nav></details>'+''.join(parts)+'<p id="restricted-reference" class="small">Some source links refer to excluded private material, unreviewed documents, or passages outside this public excerpt.</p>'
        shell(url,title,body,doc['section'] if group=='normal' else 'development',page_status)
        add_search(title,title,url,doc['section'],page_status,'entry')
        text='\n\n'.join(mdparts)
        # Download links must follow the same public-content policy as rendered pages.
        text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'['+m[1]+']('+clean_links(m[2],doc)+')',text)
        p=STAGE/'downloads'/str(doc['id']+'-'+group+'.md');p.parent.mkdir(exist_ok=True);p.write_text(text,encoding='utf8')
    if not groups['normal'] and route(doc) not in PAGES and doc['section']!='development':
        shell(route(doc),doc['title'],cards([(route(doc,True),'Read development reference','No operative replacement is claimed.','Development')]),doc['section'],'experimental')
def reference_cards(section):
    out=[]
    for d in CONFIG['documents']:
        u=route(d)
        if d['section']==section and u in PAGES:out.append((u,d['title'],'Source-linked reference, with approvals and open decisions preserved.',LABELS.get(d['status'],LABELS['reference'])))
    if section=='development':
        out=[(u,re.sub('<[^>]+>','',re.search(r'<h1>(.*?)</h1>',p)[1]),'Experimental rules remain separate from operative canon.','Development') for u,p in PAGES.items() if u.startswith('/development/')]
    if section=='character':out=[('/library/world/','Heroes, progression and the Shimmer','Attributes, Skill Points, rewards and their revisions.','Character creation'),('/library/races/','Playable races','Approved identities, exceptions and missing statistics.','Races'),('/library/combat/','Operative combat','Read alongside explicitly separated HP/d20 development.','Rules')]+out
    if section=='bestiary':out=[('/library/world/','Starspawn, Nightfoxes and summoners','Current public creature references; no complete standalone stat database exists.','Bestiary'),('/library/agriculture/','Mossback husbandry','Working creature and food-production benchmarks.','Economy')]
    if section=='library':out=[(route(d),d['title'],'Pinned source, public selection and Markdown download.','Reference') for d in CONFIG['documents'] if route(d) in PAGES]
    return cards(out)
def main(offline=False):
    global REVISIONS,STAGE
    REVISIONS=retrieve(CONFIG,offline)
    for d in CONFIG['documents']:
        selected,_=select(d,CONFIG,(CACHE/d['repository']/d['path']).read_text(encoding='utf8'))
        for b in selected:
            target='/history/'+d['id']+'/' if b['status']=='historical' else route(d,b['status'] in ('experimental','proposal'))
            ANCHOR_ROUTES.setdefault((d['id'],slug(b['title'])),target)
    stage_path=Path(tempfile.mkdtemp(prefix='.stage-',dir=ROOT));STAGE=stage_path
    try:
        shutil.copytree(ROOT/'assets',STAGE/'assets')
        for doc in CONFIG['documents']:document(doc)
        for key,title in CONFIG['sections'].items():shell('/sections/'+key+'/',title,reference_cards(key),key)
        home='<p class="lead">A beautiful world with cruel roots. Explore Mystaria’s peoples, strange magic, living kingdoms and tabletop rules.</p><p>The Living Codex brings reviewed public references together from Mystaria’s canon and economy repositories. Each build records its exact sources. Experimental rules have their own reading room.</p>'+cards([('/sections/'+k+'/',v,{'economy':'From Rosewheat and Emberbeans to clockwork, leywells and the cost of magical waste.','development':'The HP/d20 replacement, training research and provisional economic models.','peoples':'Races, language, dress and the societies that shape them.','world':'The Scarlands, Imperium, Canopy Kingdoms and ancient waterways.'}.get(k,'Explore source-linked rules, stories and reference material.'),'Explore') for k,v in CONFIG['sections'].items()])
        shell('/','Mystaria: The Living Codex',home,'world',hero=True)
        shell('/reference/search/','Search the Codex','<label for="codex-q">Find a mechanic, race, material, crop or discipline</label><input id="codex-q" type="search" placeholder="Rosewheat, Dreamcatchers, Honed, Wakecraft…" autocomplete="off"><div class="search-filters"><label for="codex-section">Section</label><select id="codex-section"><option value="all">All sections</option>'+''.join('<option>'+esc(s)+'</option>' for s in CONFIG['sections'].values())+'</select><label for="codex-status">Status</label><select id="codex-status"><option value="current">Public references</option><option value="all">Include development and history</option>'+''.join('<option value="'+s+'">'+esc(l)+'</option>' for s,l in LABELS.items())+'</select></div><p id="codex-count" role="status" aria-live="polite">Loading search index…</p><div id="codex-results"></div>')
        shell('/reference/bookmarks/','My Bookmarks','<p>Your reading shelf stays in this browser. Existing Living Codex bookmarks retain their addresses through compatibility pages.</p><div id="bookmarks-list"></div>')
        policy='## Reading canon responsibly\n\nAuthority: the author’s latest explicit approval; latest approved subject-specific reference; Canon Changelog; compatible older material. The Combat Lab is a research tool, never an independent canon authority.\n\nThe operative wound engine remains distinct from the approved HP/d20 experimental replacement. Approval of an experiment does not make every candidate number operative.\n\nSource manuscripts accumulate corrections. This public edition labels them as references with revisions rather than certifying every paragraph as current. Proposals, explicitly experimental replacements, and historical headings are separated. Qualifications within sections remain binding.\n\nSorcery and Jestercraft remain under major revision. Missing costs, prerequisites, racial statistics, economic prices and other unresolved decisions are not filled in.\n\nPrivate campaign records, hidden revelations and internal research artifacts are excluded from generated pages, downloads and search. Reveal controls are not used as a security boundary. New source documents require public-manifest review.\n\nArtwork and the inherited illustration are preserved. Narrative vignettes are illustrative fiction and establish no additional canon.'
        shell('/reference/canon-status/','Canon status and reading policy',render(policy))
        revisions={k:{'repository':v['repository'],'commit':v['commit']} for k,v in REVISIONS.items()}
        body='<p>These are the exact repository revisions used for this static build. Visitors do not need to query GitHub to read or search the Codex.</p><table><thead><tr><th>Source</th><th>Commit</th></tr></thead><tbody>'+''.join('<tr><td>'+esc(v['repository'])+'</td><td><a href="https://github.com/'+v['repository']+'/tree/'+v['commit']+'">'+v['commit']+'</a></td></tr>' for v in revisions.values())+'</tbody></table><p><a href="/build.json">Machine-readable build provenance</a> · <a href="https://github.com/MyStalker/mystaria-living-codex">Website source and maintenance</a></p>'+reference_cards('library')
        shell('/reference/sources/','Reference library and build revisions',body)
        shell('/welcome/','Welcome to Mystaria',cards([('/welcome/'+x[0]+'/',x[1],x[2],'Introduction') for x in ED['welcome']]),'world')
        for x in ED['welcome']:
            prose=x[3]
            # Introduction is inherited editorial material; obsolete dice-free language is removed.
            prose=re.sub(r'[^.!?\n]*dice.free[^.!?\n]*[.!?]?', '',prose,flags=re.I)
            shell('/welcome/'+x[0]+'/',x[1],'<p class="info">Inherited introduction. For numerical rules and recent revisions, use the linked public references.</p>'+render(prose)+cards([('/sections/character/','Create a character','Latest source-linked foundations.','Reference')]),'world')
        volume_map={'world':'world','history':'world','divinity':'world','peoples':'races','factions':'canopy-economy','shimmer':'world','sorcery':'sorcery','warlocks':'warlock','crafts':'crafts','jesters':'jestercraft','starspawn':'world','equipment':'equipment'}
        for x in ED['volumes']:
            title=x[1].replace('The Peoples of Mystaria','The Races of Mystaria')
            target='/library/'+volume_map[x[0]]+'/'
            body='<div class="story"><p class="eyebrow">A story from Mystaria · illustrative fiction</p><h2>'+esc(x[5])+'</h2>'+render(x[6])+'<p class="small">Preserved from the original website. The named character and scene do not establish canon.</p></div>'+cards([(target,'Read the updated reference','Latest public content and revision boundaries.','Reference')])
            shell('/codex/'+x[0]+'/',title,body,'world')
        shell('/codex/','The Codex',cards([('/codex/'+x[0]+'/',x[1].replace('Peoples','Races'),x[2],'Volume') for x in ED['volumes']]),'library')
        # A retired public GM URL must not continue serving its former hidden contents.
        shell('/codex/secrets/','Restricted reference','<p>GM-only and hidden source material is excluded from this public edition.</p>')
        calculators()
        for old,target in CONFIG['aliases'].items():
            if old not in PAGES:shell(old,'This reference has moved',cards([(target,'Open current reference','Stable compatibility link for an earlier Codex address.','Reference')]))
        # Stable compatibility for every prior generated page, without copying old content.
        for old,target in json.loads((ROOT/'content/legacy-routes.json').read_text(encoding='utf8')).items():
            if old not in PAGES:shell(old,'Reference library',cards([(target,'Read the updated reference','This older address remains available for bookmarks.','Reference')]))
        # Source fragments can point to deliberately excluded passages or old heading spellings.
        # Keep the useful document link, without generating a dead or private fragment.
        fragment_fallbacks=0
        for url,doc in list(PAGES.items()):
            def repair(m):
                nonlocal fragment_fallbacks
                href=html.unescape(m[1]);u=urlsplit(href)
                target=u.path or url
                if not u.scheme and u.fragment and target in PAGES and 'id="'+esc(unquote(u.fragment))+'"' not in PAGES[target]:
                    fragment_fallbacks+=1
                    return 'href="'+esc(target)+'" title="Source heading is outside this public excerpt or has changed; open the document reference"'
                return m[0]
            PAGES[url]=re.sub(r'href="([^"]+)"',repair,doc)
        for url,doc in PAGES.items():
            p=STAGE/url.lstrip('/')/'index.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(doc,encoding='utf8')
        (STAGE/'assets/search-index.json').write_text(json.dumps(SEARCH,ensure_ascii=False,separators=(',',':')),encoding='utf8')
        build={'version':'2.0.0','builtAt':datetime.now(timezone.utc).isoformat(),'repositories':revisions,'manifestSha256':hashlib.sha256((ROOT/'content/public-manifest.json').read_bytes()).hexdigest(),'pages':len(PAGES),'searchRecords':len(SEARCH),'documents':REPORT,'fragmentFallbacks':fragment_fallbacks,'websiteCommit':os.environ.get('COMMIT_REF') or os.environ.get('GITHUB_SHA') or 'local'}
        (STAGE/'build.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf8')
        (STAGE/'404.html').write_text(PAGES['/reference/search/'].replace('<h1>Search the Codex</h1>','<h1>Page not found — search the Codex</h1>'),encoding='utf8')
        (STAGE/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+CONFIG['site']['url']+'/sitemap.xml\n',encoding='utf8')
        (STAGE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+CONFIG['site']['url']+esc(u)+'</loc></url>' for u in PAGES if not u.startswith('/history/'))+'</urlset>',encoding='utf8')
        from validate import validate
        result=validate(STAGE,CONFIG)
        if result['errors']:raise ValueError(json.dumps(result,ensure_ascii=False,indent=2))
        (STAGE/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
        destination=ROOT/'dist';backup=ROOT/'.stage-previous'
        if backup.exists():shutil.rmtree(backup)
        if destination.exists():destination.rename(backup)
        try:STAGE.rename(destination)
        except BaseException:
            if backup.exists():backup.rename(destination)
            raise
        if backup.exists():shutil.rmtree(backup)
        print(json.dumps({'pages':len(PAGES),'searchRecords':len(SEARCH),'sources':revisions,'validation':result},indent=2))
    finally:
        if stage_path.exists() and stage_path.resolve().is_relative_to(ROOT.resolve()):shutil.rmtree(stage_path)
def calculators():
    # Preserve the tested browser utilities, with an explicit operative-system boundary.
    source=(ROOT/'content/calculators.html').read_text(encoding='utf8')
    shell('/reference/calculators/','Operative rules calculators','<p class="info">These inherited arithmetic aids belong to the operative rules. Do not use them as HP/d20 experimental calculators. Unresolved source limits still apply.</p>'+source,'magic')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--offline',action='store_true');args=p.parse_args();main(args.offline)
