"""
Task 11 — TDD tests for the 5th dimension (injectionResistance) in scoring-dimensions.md.

Asserts:
  1. Section '## Dimension 5 — injectionResistance' exists
  2. Default weight 0.20 documented
  3. Range 1-10 defined
  4. App-type-aware weight override heuristics present (consumer 2×, internal 0.5×, mixed default)
  5. Backward-compat note for legacy 4-dim weights.json auto-normalization
  6. Weight redistribution from v0.3 (0.25×4) to v0.4 default (0.20×5) documented
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCORING_DIMS = SKILLS_DIR / "audit" / "references" / "scoring-dimensions.md"


class TestFifthDimensionDefinition(unittest.TestCase):

    def setUp(self):
        self.content = SCORING_DIMS.read_text(encoding="utf-8")
        self.content_lower = self.content.lower()

    # ------------------------------------------------------------------ #
    # 1. Section header                                                    #
    # ------------------------------------------------------------------ #

    def test_dimension_5_section_exists(self):
        self.assertIn(
            "injectionResistance",
            self.content,
            "scoring-dimensions.md must have an injectionResistance dimension section"
        )

    def test_dimension_5_header_format(self):
        """Must have a markdown heading for injectionResistance."""
        has_header = (
            "## 5. injectionResistance" in self.content
            or "## Dimension 5" in self.content
            or "## injectionResistance" in self.content
        )
        self.assertTrue(
            has_header,
            "scoring-dimensions.md must have a ## heading for injectionResistance"
        )

    # ------------------------------------------------------------------ #
    # 2. Default weight 0.20                                               #
    # ------------------------------------------------------------------ #

    def test_default_weight_020_present(self):
        self.assertIn(
            "0.20",
            self.content,
            "scoring-dimensions.md must document default weight 0.20 for injectionResistance"
        )

    def test_five_dimensions_sum_to_1(self):
        """Doc must state that 5 × 0.20 = 1.0 or equivalent."""
        has_5dim_sum = (
            "5 × 0.20" in self.content
            or "5 * 0.20" in self.content
            or "0.20 × 5" in self.content
            or ("5 dimensions" in self.content_lower and "0.20" in self.content)
        )
        self.assertTrue(
            has_5dim_sum,
            "scoring-dimensions.md must document that 5 dimensions × 0.20 = 1.0"
        )

    # ------------------------------------------------------------------ #
    # 3. Range 1-10 defined                                                #
    # ------------------------------------------------------------------ #

    def test_range_1_to_10_defined(self):
        """injectionResistance must document 1-10 scoring range."""
        combined_check = (
            "1-10" in self.content
            or "1 to 10" in self.content_lower
            or "score 1" in self.content_lower
        )
        self.assertTrue(
            combined_check,
            "injectionResistance must define 1-10 scoring range"
        )

    # ------------------------------------------------------------------ #
    # 4. App-type-aware heuristics                                         #
    # ------------------------------------------------------------------ #

    def test_consumer_app_heuristic_present(self):
        self.assertIn(
            "consumer",
            self.content_lower,
            "scoring-dimensions.md must document consumer app-type heuristic for weight override"
        )

    def test_internal_app_heuristic_present(self):
        self.assertIn(
            "internal",
            self.content_lower,
            "scoring-dimensions.md must document internal app-type heuristic"
        )

    def test_mixed_app_heuristic_present(self):
        self.assertIn(
            "mixed",
            self.content_lower,
            "scoring-dimensions.md must document mixed app-type heuristic"
        )

    def test_consumer_2x_weight_documented(self):
        """Consumer app → injectionResistance 2× (0.40) documented."""
        has_2x = (
            "2×" in self.content
            or "2x" in self.content_lower
            or "0.40" in self.content
        )
        self.assertTrue(
            has_2x,
            "Consumer app heuristic must document 2× weight (0.40) for injectionResistance"
        )

    def test_internal_half_x_weight_documented(self):
        """Internal app → injectionResistance 0.5× (0.10) documented."""
        has_half = (
            "0.5×" in self.content
            or "0.5x" in self.content_lower
            or "0.10" in self.content
        )
        self.assertTrue(
            has_half,
            "Internal app heuristic must document 0.5× weight (0.10) for injectionResistance"
        )

    # ------------------------------------------------------------------ #
    # 5. Backward-compat note                                              #
    # ------------------------------------------------------------------ #

    def test_legacy_4dim_backward_compat_note(self):
        """Must mention auto-normalization for legacy 4-dim weights.json."""
        has_compat = (
            "auto-normaliz" in self.content_lower
            or "auto normaliz" in self.content_lower
            or "backward compat" in self.content_lower
            or "legacy" in self.content_lower
        )
        self.assertTrue(
            has_compat,
            "scoring-dimensions.md must document backward compat for legacy 4-dim weights.json"
        )

    # ------------------------------------------------------------------ #
    # 6. v0.3 → v0.4 weight redistribution noted                          #
    # ------------------------------------------------------------------ #

    def test_v03_weight_redistribution_noted(self):
        """Must reference the shift from 0.25×4 to 0.20×5."""
        has_redistrib = (
            "0.25" in self.content
            or "v0.3" in self.content
            or "weight redistribution" in self.content_lower
        )
        self.assertTrue(
            has_redistrib,
            "scoring-dimensions.md must note the v0.3→v0.4 weight redistribution (0.25×4 → 0.20×5)"
        )

    # ------------------------------------------------------------------ #
    # 7. F-finding impact table includes F10/F11/F12 + injectionResistance #
    # ------------------------------------------------------------------ #

    def test_f10_impact_row_in_table(self):
        self.assertIn(
            "F10",
            self.content,
            "scoring-dimensions.md must include F10 in the F-finding score impacts table"
        )

    def test_f11_impact_row_in_table(self):
        self.assertIn(
            "F11",
            self.content,
            "scoring-dimensions.md must include F11 in the F-finding score impacts table"
        )

    def test_f12_impact_row_in_table(self):
        self.assertIn(
            "F12",
            self.content,
            "scoring-dimensions.md must include F12 in the F-finding score impacts table"
        )

    def test_injection_resistance_column_in_table(self):
        """The score-impact table must have an injectionResistance column."""
        self.assertIn(
            "injectionResistance",
            self.content,
            "F-finding impact table must include injectionResistance column"
        )


if __name__ == "__main__":
    unittest.main()
