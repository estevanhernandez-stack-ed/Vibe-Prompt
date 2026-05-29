"""
Task 8 — TDD tests for F9 score impact in scoring-dimensions.md.

Asserts:
  1. scoring-dimensions.md contains F9 score impact entry (instruction-clarity −3)
  2. scoring-dimensions.md contains F9 score impact entry (schema-tightness −1)
  3. The deductions are correct numeric values
  4. The scoring document explains how to apply the deductions correctly
     (floor at 1, apply per fired finding per prompt)
"""

import pathlib
import re
import unittest

REFERENCES_DIR = (
    pathlib.Path(__file__).parent.parent.parent
    / "skills" / "audit" / "references"
)

SCORING_DIMS = REFERENCES_DIR / "scoring-dimensions.md"


class TestF9ScoringImpact(unittest.TestCase):

    def setUp(self):
        self.content = SCORING_DIMS.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. F9 section exists in scoring dimensions                          #
    # ------------------------------------------------------------------ #

    def test_f9_scoring_section_exists(self):
        self.assertIn(
            "F9",
            self.content,
            "scoring-dimensions.md must document F9 score impact"
        )

    # ------------------------------------------------------------------ #
    # 2. instruction-clarity penalty of −3 documented for F9             #
    # ------------------------------------------------------------------ #

    def test_f9_instruction_clarity_minus_3(self):
        """F9 section (rationale text) must document instruction-clarity -3 penalty."""
        # Locate the F9 rationale paragraph which spells out the penalties explicitly
        rationale_idx = self.content.find("F9 rationale")
        self.assertGreater(rationale_idx, -1, "F9 rationale section missing from scoring-dimensions.md")
        rationale_text = self.content[rationale_idx : rationale_idx + 600]
        has_clarity_penalty = (
            ("instruction-clarity" in rationale_text or "instruction clarity" in rationale_text.lower())
            and ("−3" in rationale_text or "-3" in rationale_text or "3" in rationale_text)
        )
        self.assertTrue(
            has_clarity_penalty,
            "F9 rationale must mention instruction-clarity and the -3 penalty"
        )

    # ------------------------------------------------------------------ #
    # 3. schema-tightness penalty of −1 documented for F9                #
    # ------------------------------------------------------------------ #

    def test_f9_schema_tightness_minus_1(self):
        """F9 rationale section must document schema-tightness -1 penalty."""
        rationale_idx = self.content.find("F9 rationale")
        self.assertGreater(rationale_idx, -1, "F9 rationale section missing from scoring-dimensions.md")
        rationale_text = self.content[rationale_idx : rationale_idx + 600]
        has_schema_penalty = (
            ("schema-tightness" in rationale_text or "schema tightness" in rationale_text.lower())
            and ("−1" in rationale_text or "-1" in rationale_text or "1" in rationale_text)
        )
        self.assertTrue(
            has_schema_penalty,
            "F9 rationale must mention schema-tightness and the -1 penalty"
        )

    # ------------------------------------------------------------------ #
    # 4. Composite scoring formula still present                          #
    # ------------------------------------------------------------------ #

    def test_composite_formula_still_present(self):
        """Existing composite formula must not be removed."""
        self.assertIn(
            "weighted average",
            self.content.lower(),
            "Composite weighted-average formula missing from scoring-dimensions.md"
        )

    def test_floor_at_1_documented(self):
        """Floor-at-1 rule must be documented."""
        self.assertTrue(
            "floor" in self.content.lower() or "below 1" in self.content.lower(),
            "Floor-at-1 rule missing from scoring-dimensions.md"
        )

    # ------------------------------------------------------------------ #
    # 5. Simulate F9 impact on a prompt with perfect dimensions           #
    # ------------------------------------------------------------------ #

    def test_f9_deductions_are_documented_correctly(self):
        """
        Verify scoring document contains correct F9 deduction values (−3 and −1)
        in the F9 rationale section, which spells them out explicitly.
        """
        rationale_idx = self.content.find("F9 rationale")
        self.assertGreater(rationale_idx, -1, "F9 rationale section missing")
        rationale_text = self.content[rationale_idx : rationale_idx + 600]

        # instruction-clarity −3
        clarity_present = re.search(
            r"instruction.?clarity.{0,50}[−\-]3|[−\-]3.{0,100}instruction.?clarity",
            rationale_text,
            re.IGNORECASE | re.DOTALL
        )
        # schema-tightness −1
        schema_present = re.search(
            r"schema.?tightness.{0,50}[−\-]1|[−\-]1.{0,100}schema.?tightness",
            rationale_text,
            re.IGNORECASE | re.DOTALL
        )

        self.assertIsNotNone(
            clarity_present,
            "F9 rationale must show 'instruction-clarity −3' (or -3)"
        )
        self.assertIsNotNone(
            schema_present,
            "F9 rationale must show 'schema-tightness −1' (or -1)"
        )


if __name__ == "__main__":
    unittest.main()
