import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / 'calibration/evidence_v1_4/snapshots.json'


@unittest.skipUnless(SNAPSHOTS.exists(), 'Optional public snapshot dataset not present')
class SnapshotIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(SNAPSHOTS.read_text(encoding='utf-8'))

    def test_exact_sample_coverage(self):
        original = json.loads((ROOT/'calibration/50_real_github_cases.json').read_text(encoding='utf-8'))
        self.assertEqual(len(self.cases), 50)
        self.assertEqual(len({c['case_id'] for c in self.cases}), 50)
        self.assertEqual({c['case_id'] for c in self.cases}, {c['case_id'] for c in original})

    def test_fixed_sha_and_file_coverage(self):
        for c in self.cases:
            with self.subTest(case=c['case_id']):
                head = c['snapshot']['head_sha']; base = c['snapshot']['base_sha']
                self.assertRegex(head, r'^[0-9a-f]{40}$')
                self.assertRegex(base, r'^[0-9a-f]{40}$')
                self.assertIn(base+'...'+head, c['compare_url'])
                self.assertEqual(len(c['files']), c['snapshot']['changed_files'])
                self.assertEqual(len({f['filename'] for f in c['files']}), len(c['files']))
                for f in c['files']:
                    expected_sha = c['merge_base_sha'] if f['status'] == 'removed' else head
                    self.assertIn(expected_sha, f['blob_url'])
                    if f['additions'] + f['deletions']:
                        self.assertTrue(f['patch'], f['filename'])
                        lines = f['patch'].splitlines()
                        self.assertEqual(sum(x.startswith('+') for x in lines), f['additions'], f['filename'])
                        self.assertEqual(sum(x.startswith('-') for x in lines), f['deletions'], f['filename'])

    def test_ci_evidence_targets_same_head(self):
        for c in self.cases:
            with self.subTest(case=c['case_id']):
                head = c['snapshot']['head_sha']
                for item in c['checks'] + c['workflows'] + c['jobs']:
                    self.assertEqual(item['head_sha'], head)
                self.assertEqual(len(c['checks']), c['check_runs_total'])
                self.assertFalse(c['log_attempt']['available'])
                self.assertIn('410', c['log_attempt']['error'])


if __name__ == '__main__':
    unittest.main()
