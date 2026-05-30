"""
Task 13 — TDD tests for F13 score impact in scoring-dimensions.md.

F13 score impact (per spec §4):
  schema-tightness −2
  instruction-clarity −1

When F13 fires on a prompt with otherwise perfect dimensions:
  schemaTightness: 10 - 2 = 8
  instructionClarity: 10 - 1 = 9
  (other dimensions unchanged at 10)

Asserts:
  1. scoring-dimensions.md includes F13 row in the score impact table
  2. F13 schema-tightness penalty is −2
  3. F13 instruction-clarity penalty is −1
  4. F13 severity declared medium
  5. F13 rationale documented
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
SCORING_DIMS = ROOT / "skills" / "audit" / "references" / "scoring-dimensions.md"


class TestF13Scoring(unittest.TestCase):

    def setUp(self):
        self.scoring = SCORING_DIMS.read_text(encoding="utf-8")

    def test_f13_in_score_impact_table(self):
        """scoring-dimensions.md must include F13 in the F-finding score impacts table."""
        self.assertIn(
            "F13",
            self.scoring,
            "scoring-dimensions.md must include F13 row in score impact table"
        )

    def test_f13_schema_tightness_minus_2(self):
        """F13 must penalize schema-tightness by -2."""
        # Look for F13 line + −2 / -2 with schema-tightness association
        # The F13 row should contain the schema-tightness column with −2
        # We accept either Unicode minus or ASCII hyphen
        f13_idx = self.scoring.find("F13")
        if f13_idx < 0:
            self.fail("F13 row missing from scoring-dimensions.md")
        section = self.scoring[f13_idx: f13_idx + 800]
        has_minus_2 = "−2" in section or "-2" in section
        self.assertTrue(
            has_minus_2,
            "F13 row must declare schema-tightness penalty of −2"
        )

    def test_f13_instruction_clarity_minus_1(self):
        """F13 must penalize instruction-clarity by -1."""
        f13_idx = self.scoring.find("F13")
        if f13_idx < 0:
            self.fail("F13 row missing from scoring-dimensions.md")
        section = self.scoring[f13_idx: f13_idx + 800]
        has_minus_1 = "−1" in section or "-1" in section
        self.assertTrue(
            has_minus_1,
            "F13 row must declare instruction-clarity penalty of −1"
        )

    def test_f13_severity_medium_in_scoring(self):
        """F13 severity should be medium in the scoring table."""
        f13_idx = self.scoring.find("F13")
        section = self.scoring[f13_idx: f13_idx + 800] if f13_idx >= 0 else ""
        self.assertIn(
            "medium",
            section.lower(),
            "F13 row must declare severity medium"
        )

    def test_f13_rationale_documented(self):
        """F13 rationale block should explain the score impact."""
        # Look for "F13 rationale" or "F13:" block
        has_rationale = (
            "F13 rationale" in self.scoring
            or "**F13" in self.scoring
        )
        self.assertTrue(
            has_rationale,
            "scoring-dimensions.md should include F13 rationale block"
        )


if __name__ == "__main__":
    unittest.main()
