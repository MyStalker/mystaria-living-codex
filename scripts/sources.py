"""Pinned public GitHub ingestion. Credentials, manuscripts and cache never enter dist."""
import hashlib,io,json,os,re,urllib.request,zipfile
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache'
def git_hash(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def request(url,token=None):
    headers={'User-Agent':'Mystaria-Living-Codex/2','Accept':'application/vnd.github+json'}
    if token and url.startswith('https://api.github.com/'):
        headers['Authorization']='Bearer '+token
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=90) as r:
        data=r.read(40_000_001)
    if len(data)>40_000_000:raise ValueError('Source response exceeds safe size limit')
    return data
def normalize_cache(revisions):
    # Connector text transfers may add a final newline. Accept only exact Git blob matches.
    for key,rev in revisions.items():
        for entry in rev['tree']['tree']:
            p=CACHE/key/entry['path']
            if entry['type']!='blob' or not p.is_file():continue
            b=p.read_bytes()
            if git_hash(b)==entry['sha']:continue
            candidates=[b[:-1],b.replace(b'\r\n',b'\n'),b.replace(b'\r\n',b'\n')[:-1]]
            exact=next((v for v in candidates if git_hash(v)==entry['sha']),None)
            if exact is None:raise ValueError('Cache integrity mismatch: '+entry['path'])
            p.write_bytes(exact)
def retrieve(config,offline=False):
    CACHE.mkdir(exist_ok=True)
    if offline:
        revisions=json.loads((CACHE/'revisions.json').read_text(encoding='utf8'))
        normalize_cache(revisions)
        return revisions
    token=os.environ.get('GH_READ_TOKEN') or os.environ.get('GITHUB_TOKEN')
    revisions={}
    for key,spec in config['repositories'].items():
        base='https://api.github.com/repos/'+spec['name']
        commit=json.loads(request(base+'/commits/'+spec['branch'],token))['sha']
        tree=json.loads(request(base+'/git/trees/'+commit+'?recursive=1',token))
        if tree.get('truncated'):raise ValueError('Truncated upstream tree')
        revisions[key]={'repository':spec['name'],'commit':commit,'tree':tree}
        wanted={d['path'] for d in config['documents'] if d['repository']==key}
        wanted.update(['00_Mystaria_Canon_Index.md','10_Canon_Changelog.md','AGENTS.md','11_Visual_Style_Guide.md'] if key=='canon' else ['00_Economy_Index.md','10_Economic_Changelog.md'])
        archive=zipfile.ZipFile(io.BytesIO(request('https://codeload.github.com/'+spec['name']+'/zip/'+commit)))
        files={str(PurePosixPath(n).relative_to(PurePosixPath(n).parts[0])):n for n in archive.namelist() if not n.endswith('/')}
        for path in wanted:
            found=path if path in files else None
            if not found:
                candidates=[n for n in files if PurePosixPath(n).name==PurePosixPath(path).name]
                if len(candidates)==1:found=candidates[0]
            if not found:raise ValueError('Reviewed source was removed or renamed: '+path+'; update manifest paths while retaining document id')
            if re.search(r'(^|/)(campaigns?|\.git|secrets?)(/|$)',found,re.I):raise ValueError('Private source path refused')
            raw=archive.read(files[found])
            entry=next((e for e in tree['tree'] if e['path']==found),None)
            if not entry or entry['type']!='blob' or entry.get('mode')=='120000' or git_hash(raw)!=entry['sha']:raise ValueError('Upstream integrity check failed: '+found)
            dest=CACHE/key/path
            if not dest.resolve().is_relative_to((CACHE/key).resolve()):raise ValueError('Unsafe cache path')
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            if found!=path:revisions[key].setdefault('resolvedPaths',{})[path]=found
    (CACHE/'revisions.json').write_text(json.dumps(revisions),encoding='utf8')
    return revisions

def split_sections(text):
    """Heading-aware blocks, ignoring fenced code; each body is emitted exactly once."""
    blocks=[];current={'title':'Introduction','level':0,'body':'','parents':[]};stack=[];fence=None
    for line in text.splitlines(keepends=True):
        fm=re.match(r'^\s*(`{3,}|~{3,})',line)
        if fm:
            if fence is None:fence=fm[1][0]
            elif fm[1][0]==fence:fence=None
        m=re.match(r'^(#{1,6})\s+(.+?)\s*#*\s*$',line) if fence is None else None
        if m:
            blocks.append(current)
            level=len(m[1]);title=m[2]
            while stack and stack[-1][0]>=level:stack.pop()
            current={'title':title,'level':level,'body':'','parents':[s[1] for s in stack]}
            stack.append((level,title))
        else:current['body']+=line
    blocks.append(current)
    return blocks

EXPERIMENT=re.compile(r'(?i)(HP[ /-]*d?20|HP.PROTOTYPE|replacement.prototype|replacement.*attribute|replacement.*equipment|replacement melee|Hulking working|END Barbarian|Deflection.*handling|Deflection armor|Upgrade [234]|NOT YET OPERATIVE|REPLACEMENT-PROTOTYPE|HP conversion|structural breach 25%|PROTOTYPE.*SHIMMER|SHIMMER.*PROTOTYPE)')
def classify(block,doc):
    title=block['title'];family=' '.join(block['parents']+[title]);intro=block['body'][:700]
    if re.search(r'(?i)(HISTORICAL|SUPERSEDED|legacy|earlier.*retained)',title):return 'historical'
    if doc['status']=='proposal':return 'proposal'
    for heading in reversed(block['parents']+[title]):
        if re.search(r'(?i)(PROPOSED ONLY|NOT CANON YET|UNAPPROVED|\bPROPOSAL\b|NOT YET APPROVED|DESIGN IDEA FOR LATER)',heading):return 'proposal'
        if re.search(r'(?i)(AUTHOR.APPROVED|APPROVED working|APPROVED EXPERIMENTAL)',heading) and (EXPERIMENT.search(family) or doc['status']=='experimental'):return 'experimental'
    if doc['status']=='experimental' or EXPERIMENT.search(family):return 'experimental'
    if doc['status']=='revision':return 'revision'
    if re.search(r'(?i)(DRAFT|OPEN QUESTIONS|UNRESOLVED|verification tasks)',title):return 'incomplete'
    # Mixed manuscripts cannot be algorithmically promoted to operative canon.
    return 'reference'
def select(doc,config,text):
    selected=[];removed=[]
    for block in split_sections(text):
        headings=block['parents']+[block['title']]
        if not any(re.search(p,h,re.I) for p in doc['include'] for h in headings):continue
        if any(re.search(config['denyHeading'],h) or any(re.search(p,h,re.I) for p in doc['exclude']) for h in headings):
            removed.append(block['title']);continue
        # Paragraph-level suppression also handles a public section containing a private aside.
        paragraphs=re.split(r'\n\s*\n',block['body'])
        public=[p for p in paragraphs if not re.search(config['denyParagraph'],p)]
        body='\n\n'.join(public).strip()
        if not body and block['level']==0:continue
        selected.append({**block,'body':body,'status':classify(block,doc)})
    if not selected:raise ValueError('No reviewed public content selected for '+doc['id'])
    return selected,removed
