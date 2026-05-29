"""
Task 15 — TDD tests for app-type heuristic + injectionResistance weight override suggestion.

The audit SKILL reads context signals to classify the app as consumer/internal/mixed,
then suggests injectionResistance weight overrides per spec §3a.

Asserts:
  1. SKILL step 7b exists and documents app-type detection
  2. domain.json source documented (.vibe-prompt/iterate/domain.json)
  3. CLAUDE.md scanning documented
  4. User-input var count heuristic (3+) documented
  5. Consumer classification → injectionResistance weight 0.40 (2×) + 0.15 each for others
  6. Internal classification → injectionResistance weight 0.10 (0.5×) + 0.225 each for others
  7. Mixed classification → default 0.20 each
  8. suggestedWeightOverrides[] fields: dimension, multiplier, appTypeSignal, rationale
  9. Weight values in scoring-dimensions.md match the heuristic table
  10. Override stored at .vibe-prompt/grade/weights.json on acceptance
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"
SCORING_DIMS = SKILLS_DIR / "audit" / "references" / "scoring-dimensions.md"


class TestAppTypeHeuristicInSkill(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.dims = SCORING_DIMS.read_text(encoding="utf-8")
        self.skill_lower = self.skill.lower()

    # ------------------------------------------------------------------ #
    # 1. Step 7b exists with app-type detection                           #
    # ------------------------------------------------------------------ #

    def test_step_7b_app_type_heuristic_exists(self):
        self.assertIn(
            "App-type heuristic",
            self.skill,
            "SKILL must have a '7b. App-type heuristic' step"
        )

    # ------------------------------------------------------------------ #
    # 2. domain.json source documented                                    #
    # ------------------------------------------------------------------ #

    def test_domain_json_source_documented(self):
        has_domain = (
            "domain.json" in self.skill
            or ".vibe-prompt/iterate/domain.json" in self.skill
        )
        self.assertTrue(
            has_domain,
            "App-type heuristic must document reading .vibe-prompt/iterate/domain.json"
        )

    # ------------------------------------------------------------------ #
    # 3. CLAUDE.md scanning documented                                    #
    # ------------------------------------------------------------------ #

    def test_claude_md_scanning_documented(self):
        has_claude_md = (
            "CLAUDE.md" in self.skill
            or "claude.md" in self.skill_lower
        )
        self.assertTrue(
            has_claude_md,
            "App-type heuristic must document reading CLAUDE.md for user-input signals"
        )

    # ------------------------------------------------------------------ #
    # 4. User-input var count heuristic                                   #
    # ------------------------------------------------------------------ #

    def test_user_input_var_count_heuristic_documented(self):
        """3+ user-input vars → consumer signal."""
        has_count = (
            "3+" in self.skill
            or "three" in self.skill_lower
            or "user-input vars" in self.skill_lower
        )
        self.assertTrue(
            has_count,
            "App-type heuristic must document the 3+ user-input-var consumer signal"
        )

    # ------------------------------------------------------------------ #
    # 5. Consumer classification → 0.40                                   #
    # ------------------------------------------------------------------ #

    def test_consumer_weight_040_in_skill(self):
        combined = self.skill + self.dims
        self.assertIn(
            "0.40",
            combined,
            "Consumer app heuristic must document injectionResistance weight 0.40"
        )

    def test_consumer_other_dims_015_in_dims(self):
        self.assertIn(
            "0.15",
            self.dims,
            "Consumer app heuristic must document other-dimension weight 0.15 each"
        )

    # ------------------------------------------------------------------ #
    # 6. Internal classification → 0.10                                   #
    # ------------------------------------------------------------------ #

    def test_internal_weight_010_in_dims(self):
        self.assertIn(
            "0.10",
            self.dims,
            "Internal app heuristic must document injectionResistance weight 0.10"
        )

    def test_internal_other_dims_0225_in_dims(self):
        self.assertIn(
            "0.225",
            self.dims,
            "Internal app heuristic must document other-dimension weight 0.225 each"
        )

    # ------------------------------------------------------------------ #
    # 7. Mixed classification → default 0.20                              #
    # ------------------------------------------------------------------ #

    def test_mixed_default_020_in_dims(self):
        combined = self.skill + self.dims
        has_mixed = (
            "mixed" in combined.lower()
            and "0.20" in combined
        )
        self.assertTrue(
            has_mixed,
            "Mixed app heuristic must document default weight 0.20 for injectionResistance"
        )

    # ------------------------------------------------------------------ #
    # 8. suggestedWeightOverrides fields                                  #
    # ------------------------------------------------------------------ #

    def test_suggested_weight_overrides_field_documented(self):
        combined = self.skill + self.dims
        self.assertIn(
            "suggestedWeightOverrides",
            combined,
            "App-type heuristic output must reference suggestedWeightOverrides"
        )

    def test_app_type_signal_field_documented(self):
        combined = self.skill + self.dims
        self.assertIn(
            "appTypeSignal",
            combined,
            "suggestedWeightOverrides must include appTypeSignal field"
        )

    def test_rationale_field_documented(self):
        combined = self.skill + self.dims
        self.assertIn(
            "rationale",
            combined.lower(),
            "suggestedWeightOverrides must include rationale field"
        )

    def test_multiplier_field_documented(self):
        combined = self.skill + self.dims
        self.assertIn(
            "multiplier",
            combined.lower(),
            "suggestedWeightOverrides must include multiplier field"
        )

    # ------------------------------------------------------------------ #
    # 9. Weight values in scoring-dimensions match heuristic table        #
    # ------------------------------------------------------------------ #

    def test_scoring_dims_consumer_table_row(self):
        """Scoring-dimensions must have consumer row in the app-type table."""
        self.assertIn(
            "consumer",
            self.dims.lower(),
            "scoring-dimensions.md must include consumer app-type row in override table"
        )

    def test_scoring_dims_internal_table_row(self):
        self.assertIn(
            "internal",
            self.dims.lower(),
            "scoring-dimensions.md must include internal app-type row in override table"
        )

    # ------------------------------------------------------------------ #
    # 10. Override write path documented                                  #
    # ------------------------------------------------------------------ #

    def test_weights_json_write_documented(self):
        """Confirmed overrides must write to .vibe-prompt/grade/weights.json."""
        combined = self.skill + self.dims
        self.assertIn(
            "weights.json",
            combined,
            "App-type heuristic must document writing accepted overrides to weights.json"
        )


class TestAppTypeInternalAndMixed(unittest.TestCase):
    """Verify internal and mixed heuristics are properly documented."""

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.dims = SCORING_DIMS.read_text(encoding="utf-8")

    def test_internal_no_user_input_condition(self):
        """Internal classification requires no user-input vars."""
        combined = self.skill + self.dims
        has_condition = (
            "no user-input" in combined.lower()
            or "no user input" in combined.lower()
            or "no-user-input" in combined.lower()
            or "no user" in combined.lower()
        )
        self.assertTrue(
            has_condition,
            "Internal app condition must reference absence of user-input vars or user interaction"
        )

    def test_mixed_signals_conflict_documented(self):
        """Mixed classification should cover conflicting signals."""
        combined = self.skill + self.dims
        has_mixed_condition = (
            "mixed" in combined.lower()
            and ("conflict" in combined.lower() or "unclear" in combined.lower() or "default" in combined.lower())
        )
        self.assertTrue(
            has_mixed_condition,
            "Mixed app classification must document conflicting/unclear signal handling"
        )


if __name__ == "__main__":
    unittest.main()
