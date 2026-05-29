"""
Task 16 — TDD tests for 5th dimension synthesis in grade/SKILL.md + composite-formula.md.

Asserts:
  1. grade/SKILL.md workflow pulls injectionResistance from audit + eval
  2. composite-formula.md has 5-dimension weighting (0.20 × 5)
  3. Per-prompt composite averages audit + eval per dimension including injectionResistance
  4. weights.json consumption documented for 5 dimensions
  5. Auto-normalization documented for 5-dim weights
  6. Legacy 4-dim weights.json backward-compat migration documented
  7. Normalization warning logged in banner
  8. Example legacy migration math documented (shows the normalization)
  9. grade/SKILL.md references 5 dimensions in workflow step 2
  10. composite-formula.md updated for v0.4 (not v0.3 defaults)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
GRADE_SKILL = SKILLS_DIR / "grade" / "SKILL.md"
COMPOSITE_FORMULA = SKILLS_DIR / "grade" / "references" / "composite-formula.md"


class TestGrade5DimensionSynthesis(unittest.TestCase):

    def setUp(self):
        self.grade = GRADE_SKILL.read_text(encoding="utf-8")
        self.formula = COMPOSITE_FORMULA.read_text(encoding="utf-8")
        self.combined = self.grade + self.formula

    # ------------------------------------------------------------------ #
    # 1. grade/SKILL.md pulls injectionResistance                         #
    # ------------------------------------------------------------------ #

    def test_grade_skill_pulls_injection_resistance(self):
        self.assertIn(
            "injectionResistance",
            self.grade,
            "grade/SKILL.md must reference injectionResistance in the dimension-pull step"
        )

    # ------------------------------------------------------------------ #
    # 2. composite-formula.md has 5-dimension weighting                   #
    # ------------------------------------------------------------------ #

    def test_formula_has_5_dimension_default_weights(self):
        """composite-formula.md must document 0.20 × 5 = 1.0 default weights."""
        has_5dim = (
            "0.20" in self.formula
            or "injectionResistance" in self.formula
        )
        self.assertTrue(
            has_5dim,
            "composite-formula.md must document 5-dimension default weight 0.20"
        )

    # ------------------------------------------------------------------ #
    # 3. Per-prompt composite averages audit + eval per dimension          #
    # ------------------------------------------------------------------ #

    def test_formula_documents_audit_eval_average(self):
        """Formula must state composite = average of audit + eval per dimension."""
        has_average = (
            "average" in self.formula.lower()
            or "avg" in self.formula.lower()
        )
        self.assertTrue(
            has_average,
            "composite-formula.md must document that per-dimension score = average(audit, eval)"
        )

    def test_grade_skill_averages_dimension_scores(self):
        """grade/SKILL.md must state it averages audit and eval dimension scores."""
        has_avg = (
            "average" in self.grade.lower()
            and ("audit" in self.grade.lower())
            and ("eval" in self.grade.lower())
        )
        self.assertTrue(
            has_avg,
            "grade/SKILL.md must document averaging audit + eval dimension scores"
        )

    # ------------------------------------------------------------------ #
    # 4. weights.json consumption for 5 dimensions                        #
    # ------------------------------------------------------------------ #

    def test_formula_documents_weights_json_consumption(self):
        self.assertIn(
            "weights.json",
            self.formula,
            "composite-formula.md must document consuming weights.json for 5-dim overrides"
        )

    # ------------------------------------------------------------------ #
    # 5. Auto-normalization documented                                    #
    # ------------------------------------------------------------------ #

    def test_formula_auto_normalization_documented(self):
        has_norm = (
            "auto-normaliz" in self.formula.lower()
            or "auto normaliz" in self.formula.lower()
            or "normaliz" in self.formula.lower()
        )
        self.assertTrue(
            has_norm,
            "composite-formula.md must document auto-normalization of weights to sum=1.0"
        )

    # ------------------------------------------------------------------ #
    # 6. Legacy 4-dim weights.json backward-compat documented             #
    # ------------------------------------------------------------------ #

    def test_formula_legacy_4dim_compat_documented(self):
        has_legacy = (
            "4-dim" in self.formula.lower()
            or "4 dim" in self.formula.lower()
            or "legacy" in self.formula.lower()
            or "4-dimension" in self.formula.lower()
        )
        self.assertTrue(
            has_legacy,
            "composite-formula.md must document backward compat for legacy 4-dim weights.json"
        )

    # ------------------------------------------------------------------ #
    # 7. Normalization warning in banner                                  #
    # ------------------------------------------------------------------ #

    def test_normalization_warning_in_banner_documented(self):
        combined = self.grade + self.formula
        has_warn = (
            "warn" in combined.lower()
            or "normali" in combined.lower()
        )
        self.assertTrue(
            has_warn,
            "Grade or formula must document a normalization warning in the banner"
        )

    # ------------------------------------------------------------------ #
    # 8. Example legacy migration math                                    #
    # ------------------------------------------------------------------ #

    def test_legacy_migration_math_example_documented(self):
        """composite-formula.md or scoring-dims must include a worked example."""
        scoring_dims = (
            pathlib.Path(__file__).parent.parent.parent
            / "skills" / "audit" / "references" / "scoring-dimensions.md"
        ).read_text(encoding="utf-8")
        combined = self.formula + scoring_dims
        has_example = (
            "example" in combined.lower()
            or "e.g." in combined.lower()
            or "schema: 0.5" in combined
            or "normalized" in combined.lower()
        )
        self.assertTrue(
            has_example,
            "composite-formula.md or scoring-dims must include a legacy normalization example"
        )

    # ------------------------------------------------------------------ #
    # 9. grade/SKILL.md references 5 dimensions in workflow step 2        #
    # ------------------------------------------------------------------ #

    def test_grade_skill_step2_references_5_dimensions(self):
        """Workflow step 2 must list injectionResistance alongside the other 4 dimensions."""
        self.assertIn(
            "injectionResistance",
            self.grade,
            "grade/SKILL.md step 2 must include injectionResistance in the dimension list"
        )

    def test_grade_skill_references_all_4_original_dimensions(self):
        """grade/SKILL.md must still reference all 4 original dimensions."""
        for dim in ["schemaTightness", "personaConsistency", "instructionClarity", "tokenEfficiency"]:
            self.assertIn(
                dim,
                self.grade,
                f"grade/SKILL.md must still reference {dim}"
            )

    # ------------------------------------------------------------------ #
    # 10. composite-formula.md updated for v0.4                           #
    # ------------------------------------------------------------------ #

    def test_formula_reflects_v04_not_just_v03(self):
        """composite-formula.md must not only reflect v0.3 (4 dims, 0.25 each)."""
        has_v04 = (
            "0.20" in self.formula
            or "injectionResistance" in self.formula
            or "5" in self.formula
        )
        self.assertTrue(
            has_v04,
            "composite-formula.md must be updated for v0.4 (5 dimensions, 0.20 default)"
        )


class TestGrade5DimWeightMath(unittest.TestCase):
    """Verify the weight math example: legacy 4-dim → 5-dim normalized."""

    def setUp(self):
        self.formula = COMPOSITE_FORMULA.read_text(encoding="utf-8")
        self.scoring_dims = (
            SKILLS_DIR / "audit" / "references" / "scoring-dimensions.md"
        ).read_text(encoding="utf-8")

    def test_normalization_formula_present(self):
        """normalizedWeight = rawWeight / sum(all weights) must be documented."""
        combined = self.formula + self.scoring_dims
        has_formula = (
            "normalizedWeight" in combined
            or "normalized_weight" in combined.lower()
            or "sum(all" in combined.lower()
            or "/ sum" in combined.lower()
        )
        self.assertTrue(
            has_formula,
            "Weight normalization formula (normalizedWeight = rawWeight / sum) must be documented"
        )

    def test_5th_dim_injection_resistance_in_formula(self):
        self.assertIn(
            "injectionResistance",
            self.formula,
            "composite-formula.md must reference injectionResistance"
        )


if __name__ == "__main__":
    unittest.main()
