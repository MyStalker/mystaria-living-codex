"""Cloud reconciliation marker. Netlify rebuilds on this repository's Git push."""
import argparse,json,os
from datetime import datetime,timezone
from sources import ROOT,request

def main(force=False):
    config=json.loads((ROOT/'content/public-manifest.json').read_text(encoding='utf8'))
    revisions={}
    for key,spec in config['repositories'].items():
        result=json.loads(request('https://api.github.com/repos/'+spec['name']+'/commits/'+spec['branch'],os.environ.get('GITHUB_TOKEN')))
        revisions[key]=result['sha']
    path=ROOT/'content/source-revisions.json'
    prior=json.loads(path.read_text(encoding='utf8')) if path.exists() else {}
    if prior.get('revisions')==revisions and not force:
        print('Source heads unchanged; no publishing marker needed.');return
    value={'revisions':revisions,'checkedAt':datetime.now(timezone.utc).isoformat()}
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
    print('Updated publishing marker for '+', '.join(k+':'+v[:12] for k,v in revisions.items()))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--force',action='store_true');args=p.parse_args();main(args.force)
