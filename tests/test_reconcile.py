import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import reconcile

class ReconciliationFailureRecovery(unittest.TestCase):
    def run_case(self,deployed,force=False):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'content').mkdir()
            cfg={'site':{'url':'https://public.example'},'repositories':{'canon':{'name':'owner/canon','branch':'main'},'economy':{'name':'owner/economy','branch':'main'}}}
            (root/'content/public-manifest.json').write_text(json.dumps(cfg),encoding='utf8')
            marker=root/'content/source-revisions.json';original={'revisions':{'canon':'a'*40,'economy':'b'*40},'checkedAt':'old'}
            marker.write_text(json.dumps(original),encoding='utf8')
            def request(url,token=None):
                if '/repos/owner/canon/' in url:return json.dumps({'sha':'a'*40}).encode()
                if '/repos/owner/economy/' in url:return json.dumps({'sha':'b'*40}).encode()
                self.assertIsNone(token)
                return json.dumps({'repositories':{k:{'commit':v} for k,v in deployed.items()}}).encode()
            with patch.object(reconcile,'ROOT',root),patch.object(reconcile,'request',request):reconcile.main(force)
            return json.loads(marker.read_text(encoding='utf8')),original
    def test_current_production_does_not_rebuild(self):
        actual,old=self.run_case({'canon':'a'*40,'economy':'b'*40});self.assertEqual(actual,old)
    def test_failed_previous_marker_build_is_retried(self):
        actual,old=self.run_case({'canon':'c'*40,'economy':'b'*40});self.assertNotEqual(actual['checkedAt'],old['checkedAt']);self.assertEqual(actual['revisions'],old['revisions'])
    def test_forced_safe_rebuild_is_supported(self):
        actual,old=self.run_case({'canon':'a'*40,'economy':'b'*40},True);self.assertNotEqual(actual['checkedAt'],old['checkedAt'])
