"""Regression coverage for the actual player reading path and current-rule presentation."""
import json
from pathlib import Path
import re
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reading import Edition


@unittest.skipUnless((ROOT/'dist/learn/character/index.html').exists(),'Build the player edition first')
class PlayerReading(unittest.TestCase):
    def page(self,path):return (ROOT/'dist'/path/'index.html').read_text(encoding='utf8')

    def test_main_guides_teach_present_rules_without_repository_chronology(self):
        for path in ['learn/character','learn/training','learn/health','economy/regions','economy/mana']:
            text=self.page(path)
            self.assertNotRegex(text,r'(?i)AUTHOR APPROV|November \d|wound.penalt|simulation job|playtest|not yet operative')
        self.assertIn('Training Points',self.page('learn/character'))

    def test_health_examples_and_sleep_override_are_present(self):
        text=self.page('learn/health')
        for term in ['310 natural HP','510 natural HP','317 post-armor damage','including a Guard broken','50% of maximum ordinary HP']:
            self.assertIn(term,text)
        self.assertNotIn('sleep cannot bypass',text)

    def test_mana_depth_and_exact_five_hex_pairs(self):
        text=self.page('economy/mana')
        self.assertEqual(text.count('class="deep-dive"'),6)
        for a,b in [('Red','Green'),('Red','Black'),('Blue','Black'),('Blue','White'),('Green','White')]:
            self.assertRegex(text,r'<td[^>]*>'+a+r'</td>\s*<td[^>]*>'+b+r'</td>')
        self.assertIn('87.5%',text)
        self.assertIn('Immediate successor',text)

    def test_search_covers_teaching_topics_and_no_historical_heading(self):
        rows=json.loads((ROOT/'dist/assets/search-index.json').read_text(encoding='utf8'))
        for query in ['Training Points','Dreamcatchers','Honed','Rosewheat','Guardian','Skillprints']:
            self.assertTrue(any(query.lower() in (r['title']+' '+r['text']).lower() for r in rows),query)
        self.assertTrue(all(not re.search(r'November \d|AUTHOR APPROV',r['title']) for r in rows))
        self.assertTrue(all(r['status']=='reference' for r in rows))

    def test_catalogue_entries_are_independent_and_addressable(self):
        text=self.page('reference/weapon-enchantments')
        self.assertEqual(text.count('class="deep-dive"'),37)
        self.assertRegex(text,r'<details class="deep-dive" id="guardian-[^"]+"')
        self.assertIn('id="catalogue-filter"',text)

    def test_comparison_cells_keep_their_mobile_labels(self):
        text=self.page('economy/regions')
        self.assertIn('class="mobile-cards"',text)
        self.assertIn('data-label="Scarlands"',text)
        self.assertIn('data-label="Canopy Kingdoms"',text)

    def test_optional_content_is_escaped_and_has_distinct_ids(self):
        edition=Edition.__new__(Edition)
        text,_=edition.render('Intro\n\n::: detail One\nFirst\n:::\n\n::: detail Two\n<script>alert(1)</script>\n:::')
        self.assertEqual(text.count('class="deep-dive"'),2)
        self.assertIn('id="one"',text);self.assertIn('id="two"',text)
        self.assertNotIn('<script>',text)

if __name__=='__main__':unittest.main()
