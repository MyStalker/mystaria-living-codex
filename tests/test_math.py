import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from math_render import protect

class StaticMath(unittest.TestCase):
    def test_fraction_is_native_static_mathml(self):
        text,items=protect(r'Before \[\frac{a}{b}\] after')
        self.assertIn('PLACEHOLDER',text);self.assertEqual(len(items),1)
        self.assertIn('<math',items[0]);self.assertIn('<mfrac>',items[0])
        self.assertIn('display="block"',items[0])
    def test_code_samples_remain_literal(self):
        source='```tex\n\\[x^2\\]\n```\n`\\(a\\)`'
        text,items=protect(source)
        self.assertEqual(text,source);self.assertEqual(items,[])
