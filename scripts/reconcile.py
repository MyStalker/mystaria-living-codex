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
    # Compare with the actual deployed source revisions. A marker alone cannot prove
    # its resulting build succeeded; stale production must be retried on later runs.
    try:
        published=json.loads(request(config['site']['url']+'/build.json'))
        deployed={k:v['commit'] for k,v in published.get('repositories',{}).items()}
    except Exception as exc:
        deployed={}
        print('Could not verify production provenance ('+type(exc).__name__+'); requesting a validated rebuild.')
    if deployed==revisions and not force:
        print('Production already reflects current source heads; no rebuild needed.');return
    path=ROOT/'content/source-revisions.json'
    value={'revisions':revisions,'checkedAt':datetime.now(timezone.utc).isoformat()}
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8')
    print('Updated publishing marker for '+', '.join(k+':'+v[:12] for k,v in revisions.items()))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--force',action='store_true');args=p.parse_args();main(args.force)
