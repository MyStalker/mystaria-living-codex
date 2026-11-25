import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from sources import split_sections,select,classify,git_hash

class PublicPolicy(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/'content/public-manifest.json').read_text(encoding='utf8'))
        self.doc={'id':'fixture','path':'fixture.md','repository':'canon','include':['.*'],'exclude':[],'status':'reference'}
    def test_fenced_heading_is_not_content_boundary(self):
        b=split_sections('# Public\nText\n```\n# example\n```\n## Next\nSecond')
        self.assertEqual([x['title'] for x in b],['Introduction','Public','Next'])
    def test_private_subtree_and_download_material_are_excluded(self):
        blocks,_=select(self.doc,self.config,'# Public\nReadable\n## GM-only\nPRIVATE_SENTINEL\n### Nested\nPRIVATE_NESTED\n## Public again\nVisible')
        text=' '.join(b['body'] for b in blocks)
        self.assertNotIn('PRIVATE_',text);self.assertIn('Visible',text)
    def test_explicit_experiment_is_not_operative(self):
        b={'title':'AUTHOR-APPROVED HP/d20 EXPERIMENTAL foundation','parents':[],'body':'Approved for experiments.'}
        self.assertEqual(classify(b,self.doc),'experimental')
    def test_unapproved_proposal_keeps_its_status(self):
        b={'title':'Unapproved proposal','parents':['HP/d20 research'],'body':'Candidate'}
        self.assertEqual(classify(b,self.doc),'proposal')
    def test_proposal_ancestry_and_specific_approval(self):
        b={'title':'Candidate tables','parents':['HP/d20 conversion (PROPOSAL)'],'body':'Candidate'}
        self.assertEqual(classify(b,self.doc),'proposal')
        b['title']='AUTHOR-APPROVED working replacement'
        self.assertEqual(classify(b,self.doc),'experimental')
    def test_public_urls_are_unique_and_campaigns_not_included(self):
        ids=[d['id'] for d in self.config['documents']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertFalse(any('campaign' in d['path'] for d in self.config['documents']))

class PublishingIntegration(unittest.TestCase):
    @unittest.skipUnless((ROOT/'.cache/revisions.json').exists(),'Run a source build before integration tests')
    def test_synthetic_change_builds_and_failed_refresh_preserves_output(self):
        with tempfile.TemporaryDirectory(prefix='codex-fixture-') as temp:
            root=Path(temp)
            for name in ('scripts','content','assets','.cache'):shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__'))
            config=json.loads((root/'content/public-manifest.json').read_text(encoding='utf8'))
            config['documents'].append({'id':'synthetic-publishing-test','repository':'canon','path':'synthetic-public-fixture.md','title':'Synthetic publishing fixture — not canon','section':'development','status':'proposal','include':['.*'],'exclude':[]})
            (root/'content/public-manifest.json').write_text(json.dumps(config),encoding='utf8')
            reading=json.loads((root/'content/reading-manifest.json').read_text(encoding='utf8'))
            reading['lessons'].append(dict(id='synthetic-publishing-test',document='synthetic-publishing-test',url='/development/synthetic-publishing-test/',title='Synthetic publishing fixture - not canon',section='development',summary='Explicit isolated test only.',sources=['synthetic-publishing-test'],status='proposal'))
            (root/'content/reading-manifest.json').write_text(json.dumps(reading),encoding='utf8')
            fixture=b'# Synthetic fixture\n\nSYNTHETIC_PUBLIC_CHANGE_2026\n\n## GM-only\n\nPRIVATE_FIXTURE_SENTINEL\n'
            source=root/'.cache/canon/synthetic-public-fixture.md';source.write_bytes(fixture)
            revisions=json.loads((root/'.cache/revisions.json').read_text(encoding='utf8'))
            revisions['canon']['tree']['tree'].append({'path':'synthetic-public-fixture.md','type':'blob','mode':'100644','sha':git_hash(fixture)})
            (root/'.cache/revisions.json').write_text(json.dumps(revisions),encoding='utf8')
            result=subprocess.run([sys.executable,'scripts/build.py','--offline'],cwd=root,capture_output=True,text=True,encoding='utf8')
            self.assertEqual(result.returncode,0,result.stderr[-5000:])
            page=(root/'dist/development/synthetic-publishing-test/index.html').read_text(encoding='utf8')
            self.assertIn('SYNTHETIC_PUBLIC_CHANGE_2026',page);self.assertNotIn('PRIVATE_FIXTURE_SENTINEL',page)
            index=json.loads((root/'dist/assets/search-index.json').read_text(encoding='utf8'))
            fixture_rows=[x for x in index if 'synthetic-publishing-test' in x['url']]
            self.assertTrue(fixture_rows);self.assertTrue(all(x['status']=='proposal' for x in fixture_rows))
            before=hashlib.sha256((root/'dist/build.json').read_bytes()).hexdigest()
            source.write_text('Corrupted source transfer',encoding='utf8')
            failed=subprocess.run([sys.executable,'scripts/build.py','--offline'],cwd=root,capture_output=True,text=True,encoding='utf8')
            self.assertNotEqual(failed.returncode,0)
            self.assertEqual(before,hashlib.sha256((root/'dist/build.json').read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()
