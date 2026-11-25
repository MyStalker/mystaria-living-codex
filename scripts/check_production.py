"""Anonymous HTTP smoke test of the real public deployment, not a signed-in session."""
import concurrent.futures,json,urllib.error,urllib.request
BASE='https://resonant-genie-1ee11c.netlify.app'
PATHS=['/','/sections/world/','/sections/peoples/','/sections/character/','/sections/combat/','/sections/magic/','/sections/economy/','/sections/bestiary/','/sections/development/','/reference/search/','/assets/enchanted-city.jpg','/build.json','/library/warlock/','/content/source/01_World_and_Shimmer.md']
def check(path):
    req=urllib.request.Request(BASE+path,headers={'User-Agent':'Mystaria-Public-Smoke-Test/2'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:status=r.status;body=r.read()
    except urllib.error.HTTPError as e:status=e.code;body=e.read()
    expected=404 if path.startswith('/content/source/') else 200
    if status!=expected:raise AssertionError(path+': expected '+str(expected)+', received '+str(status))
    if path=='/build.json':
        build=json.loads(body);assert build['version']=='2.0.0';assert len(build['repositories']['canon']['commit'])==40
    if path=='/library/warlock/':assert b'<math ' in body and b'mathjax@' not in body
    return {'path':path,'status':status}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,PATHS))
    print(json.dumps({'anonymousPublicChecks':len(results),'results':results},indent=2))
