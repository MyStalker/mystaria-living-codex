"""Validate the whole publish artifact, including links, search and privacy boundaries."""
import argparse,json,re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote

class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.links=[];self.errors=[];self.headings=0;self.lang=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids:self.errors.append('Duplicate id '+a['id'])
            self.ids.add(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='h1':self.headings+=1
        for attr in ('href','src'):
            if attr in a:self.links.append((a[attr],attr))
        if tag=='img' and not a.get('alt'):self.errors.append('Image lacks alt text')
        if tag=='script' and 'src' not in a:self.errors.append('Unexpected inline script')
def validate(root,config):
    root=Path(root);errors=[];warnings=[];pages={};external=set();link_count=0
    for path in root.rglob('*.html'):
        p=Page();p.feed(path.read_text(encoding='utf8'));pages[path.resolve()]=p
        errors.extend(str(path.relative_to(root))+': '+e for e in p.errors)
        if p.headings!=1:errors.append(str(path.relative_to(root))+': expected one h1')
        if p.lang!='en':errors.append(str(path.relative_to(root))+': missing language')
    for path,p in pages.items():
        for href,kind in p.links:
            link_count+=1;u=urlsplit(href)
            if u.scheme:
                if u.scheme not in ('http','https','mailto'):errors.append('Unsafe URL scheme: '+href)
                if u.scheme in ('http','https'):external.add(href.split('#')[0])
                continue
            if href.startswith('//'):errors.append('Protocol-relative URL: '+href);continue
            target=((root/unquote(u.path).lstrip('/')) if u.path.startswith('/') else path.parent/unquote(u.path)) if u.path else path
            if target.is_dir():target=target/'index.html'
            if not target.is_file():errors.append(str(path.relative_to(root))+': missing target '+href);continue
            if u.fragment and target.resolve() in pages and unquote(u.fragment) not in pages[target.resolve()].ids:errors.append(str(path.relative_to(root))+': missing anchor '+href)
    for file in root.rglob('*'):
        if not file.is_file():continue
        rel=file.relative_to(root).as_posix()
        if any(part in ('.git','.cache','source','legacy','campaigns','campaign','node_modules') for part in file.relative_to(root).parts) or rel.startswith(('content/','sources/')):errors.append('Forbidden published path: '+rel)
        if file.suffix.lower() in ('.py','.env','.yml','.yaml','.zip','.bundle','.toml'):errors.append('Implementation/private artifact in output: '+rel)
        if file.suffix in ('.html','.md','.json','.js','.txt'):
            text=file.read_text(encoding='utf8')
            if re.search(config['denyParagraph'],text):errors.append('Private content marker in '+rel)
            if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]+|api\.netlify\.com/build_hooks/[a-f0-9]{15,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----',text):errors.append('Possible credential in '+rel)
    index=json.loads((root/'assets/search-index.json').read_text(encoding='utf8'))
    seen=set()
    for row in index:
        key=(row['url'],row['kind'])
        if key in seen:errors.append('Duplicate search target '+row['url'])
        seen.add(key)
        u=urlsplit(row['url']);target=(root/u.path.lstrip('/')/'index.html').resolve()
        if target not in pages or (u.fragment and unquote(u.fragment) not in pages[target].ids):errors.append('Broken search target '+row['url'])
        if row['status'] not in ('reference','experimental','proposal','historical','revision','incomplete'):errors.append('Unknown status '+row['status'])
    build=json.loads((root/'build.json').read_text(encoding='utf8'))
    for key in ('canon','economy'):
        if not re.fullmatch('[0-9a-f]{40}',build['repositories'][key]['commit']):errors.append('Missing source revision '+key)
    if not (root/'assets/enchanted-city.jpg').is_file():errors.append('Inherited artwork missing')
    return {'htmlPages':len(pages),'checkedLinks':link_count,'searchRecords':len(index),'externalLinks':len(external),'errors':errors,'warnings':warnings}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',nargs='?',default='dist');a=p.parse_args();config=json.loads(Path('content/public-manifest.json').read_text(encoding='utf8'));result=validate(Path(a.directory),config);print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
