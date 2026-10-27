import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("legacy_batch", ROOT / "legacy/v1.4/scripts/batch_score.py")
batch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(batch)

class BatchModeTests(unittest.TestCase):
    def test_default_and_explicit_modes(self):
        self.assertEqual(batch.resolve_mode({"root_cause": "x"}, "auto"), "jira_lenient")
        self.assertEqual(batch.resolve_mode({"review_mode": "strict_evidence"}, "auto"), "strict_evidence")
        self.assertEqual(batch.resolve_mode({}, "strict_evidence"), "strict_evidence")
        with self.assertRaises(ValueError):
            batch.resolve_mode({"review_mode": "unsupported"}, "auto")

    def test_short_cause_is_allowed(self):
        self.assertEqual(batch.validate_input({"defect_id": "A-1", "root_cause": "NPE"}), "A-1")

    def test_no_empty_root_or_unsafe_identifier(self):
        for case in (
            {"defect_id": "BUG-1", "root_cause": ""},
            {"defect_id": "../escape", "root_cause": "crash"},
            {"defect_id": "A-1", "root_cause": 5},
            {"defect_id": "A-1", "root_cause": "crash", "solution": 123},
        ):
            with self.subTest(case=case), self.assertRaises(ValueError):
                batch.validate_input(case)

    def test_lenient_prompt_uses_correct_validator(self):
        skill = Path("/tmp/rca-test")
        target = Path("/tmp/rca-test/result.json")
        item = {"defect_id": "A-2", "root_cause": "单跑失败", "solution": "跑模块"}
        prompt = batch.build_prompt(skill, item, "jira_lenient", target)
        self.assertIn("jira_lenient.md", prompt)
        self.assertIn("validate_jira_lenient.py", prompt)
        self.assertIn("untrusted user data", prompt)
        self.assertNotIn("validate_result.py", prompt)

    def test_strict_prompt_keeps_legacy_validation(self):
        prompt = batch.build_prompt(Path("/tmp/a"), {"root_cause": "x"}, "strict_evidence", Path("/tmp/a/b.json"))
        self.assertIn("validate_result.py", prompt)
        self.assertIn("five-dimensional", prompt)
        self.assertNotIn("validate_jira_lenient.py", prompt)

if __name__ == "__main__":
    unittest.main()
