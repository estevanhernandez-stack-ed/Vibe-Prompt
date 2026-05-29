"""
Task 17 — TDD tests for skills/remediate/references/confidence-rubric.md.

Asserts the file declares all 5 weighted dimensions, sum-to-1.0 weights,
routing thresholds, and a worked example.
"""

import pathlib
import re
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
RUBRIC = SKILLS_DIR / "remediate" / "references" / "confidence-rubric.md"


class TestRemediateConfidenceRubric(unittest.TestCase):

    def setUp(self):
        self.assertTrue(
            RUBRIC.exists(),
            f"references/confidence-rubric.md must exist at {RUBRIC}",
        )
        self.content = RUBRIC.read_text(encoding="utf-8")
        self.lower = self.content.lower()

    # 5 dimensions
    def test_locate_confidence_declared(self):
        self.assertIn("locate", self.lower)
        self.assertIn("0.30", self.content)

    def test_diff_shape_confidence_declared(self):
        self.assertIn("diff-shape", self.lower)
        self.assertIn("0.25", self.content)

    def test_voice_risk_declared(self):
        self.assertIn("voice", self.lower)
        self.assertIn("0.20", self.content)

    def test_schema_impact_declared(self):
        self.assertIn("schema", self.lower)
        self.assertIn("0.15", self.content)

    def test_version_bump_declared(self):
        self.assertIn("version-bump", self.lower)
        self.assertIn("0.10", self.content)

    def test_weights_sum_to_one(self):
        # 0.30 + 0.25 + 0.20 + 0.15 + 0.10 = 1.00
        self.assertTrue(
            "sum" in self.lower and "1.0" in self.content,
            "Rubric must declare weights sum to 1.0",
        )

    # Routing thresholds
    def test_auto_write_threshold_0_90(self):
        idx = self.content.find("auto-write")
        self.assertGreater(idx, -1)
        # Check window around the term (table row format may have number before or after)
        section = self.content[max(0, idx - 200):idx + 500]
        self.assertIn("0.90", section)

    def test_stage_threshold_0_70(self):
        idx = self.lower.find("stage")
        self.assertGreater(idx, -1)
        # Window around it (number may be in the same table row before "stage")
        section = self.content[max(0, idx - 200):idx + 500]
        self.assertIn("0.70", section)

    def test_inline_only_threshold(self):
        self.assertTrue(
            "inline-only" in self.lower or "inline only" in self.lower,
        )
        # Must reference < 0.70 boundary
        self.assertTrue(
            "< 0.70" in self.content or "<0.70" in self.content,
            "Rubric must declare < 0.70 inline-only boundary",
        )

    # Worked example
    def test_worked_example_present(self):
        self.assertTrue(
            "worked example" in self.lower or "example" in self.lower,
            "Rubric must include a worked example",
        )

    def test_worked_example_category_a_high_confidence(self):
        # Category A composer-fix on F9 with composer.json present → confidence ~0.95
        self.assertTrue(
            "Category A" in self.content or "F9" in self.content,
            "Worked example must show Category A or F9 case",
        )
        # Numbers close to 0.92-0.95 should appear
        has_high_conf = (
            "0.92" in self.content or "0.93" in self.content
            or "0.94" in self.content or "0.95" in self.content
        )
        self.assertTrue(
            has_high_conf,
            "Worked example must show high-confidence result",
        )


if __name__ == "__main__":
    unittest.main()
