import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/calibration'))
from test_excerpts import changed_test_names, extract_current_functions


class TestEvidenceExcerpts(unittest.TestCase):
    def test_unchanged_negative_assertion_is_current_evidence(self):
        patch='@@ -3,4 +3,5 @@ func TestSwitch(t *testing.T) {\n assert.False(t, enabled)\n+ enabled = true\n assert.True(t, enabled)\n }\n func TestNeighbor(t *testing.T) {'
        self.assertEqual(changed_test_names(patch),['TestSwitch'])
        source='func TestSwitch(t *testing.T) {\n assert.False(t, enabled)\n enabled = true\n assert.True(t, enabled)\n}\nfunc TestNeighbor(t *testing.T) {}\n'
        result=extract_current_functions(source,changed_test_names(patch))
        self.assertIn('assert.False',result[0]['code'])
        self.assertNotIn('TestNeighbor',result[0]['code'])

    def test_added_test_does_not_select_unchanged_previous_test(self):
        patch='@@ -8,2 +8,7 @@ func TestOld(t *testing.T) {\n }\n+// new regression\n+func TestNew(t *testing.T) {\n+ assert.NoError(t, err)\n+}'
        self.assertEqual(changed_test_names(patch),['TestNew'])

    def test_missing_head_function_is_not_fabricated(self):
        with self.assertRaises(ValueError):extract_current_functions('func TestOther(t *testing.T) {}',['TestMissing'])


if __name__=='__main__':unittest.main()
