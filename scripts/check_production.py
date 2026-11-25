"""Anonymous HTTP smoke test of the real public deployment, not a signed-in session."""
import argparse,concurrent.futures,json,urllib.error,urllib.request
BASE='https://resonant-genie-1ee11c.netlify.app'
PATHS=['/','/sections/world/','/sections/peoples/','/sections/character/','/sections/combat/','/sections/magic/','/sections/economy/','/sections/bestiary/','/sections/development/','/reference/search/','/assets/enchanted-city.jpg','/build.json','/learn/character/','/learn/health/','/learn/training/','/economy/regions/','/economy/mana/','/reference/weapon-enchantments/','/library/warlock/','/content/source/01_World_and_Shimmer.md']
def check(path):
    req=urllib.request.Request(BASE+path,headers={'User-Agent':'Mystaria-Public-Smoke-Test/2'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:status=r.status;body=r.read()
    except urllib.error.HTTPError as e:status=e.code;body=e.read()
    expected=404 if path.startswith('/content/source/') else 200
    if status!=expected:raise AssertionError(path+': expected '+str(expected)+', received '+str(status))
    if path=='/build.json':
        build=json.loads(body);assert build['version']=='2.1.0';assert len(build['repositories']['canon']['commit'])==40
    if path=='/learn/character/':assert b'Training Points' in body and b'playtest' not in body.lower()
    if path=='/learn/health/':assert b'310 natural HP' in body and b'penalties removed' not in body
    if path=='/economy/mana/':assert b'Dreamcatchers' in body and b'nonadjacent' in body and b'Leshy' in body
    return {'path':path,'status':status}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--allow-previous-edition',action='store_true');args=parser.parse_args()
    with urllib.request.urlopen(BASE+'/build.json',timeout=30) as response:published=json.load(response)
    paths=PATHS
    if published['version']!='2.1.0' and args.allow_previous_edition:
        paths=['/','/reference/search/','/assets/enchanted-city.jpg','/content/source/01_World_and_Shimmer.md']
        print('Production is still the previously accepted edition; validating its availability while the new edition is staged.')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,paths))
    print(json.dumps({'anonymousPublicChecks':len(results),'results':results},indent=2))
