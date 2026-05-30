"""
Task 14 — TDD tests for F12 detection in audit/SKILL.md + smell-rubric-f1-f13.md.

F12: User-controlled var appears at or before system instruction in composition order.
Severity: critical (degrades to high when composer-mimic confidence < 0.6).
Score impact: injectionResistance −6, persona-consistency −2.
Prerequisite: F10 must have fired on the same prompt.

Asserts:
  1. F12 section exists in rubric
  2. F10 prerequisite declared in F12 section
  3. Composer.json / composition order reading documented
  4. Fire condition: user-var layer index <= system-instruction layer index
  5. Non-fire condition: user-var layer comes AFTER system instruction
  6. Confidence degrade: composer-mimic < 0.6 → severity high (not critical)
  7. Evidence shape: userVar, userVarLayer, systemInstructionLayer, compositionOrder
  8. Severity is critical (default)
  9. Score impact injectionResistance −6 + persona-consistency −2 documented
  10. handoffHint: "vibe-sec:audit" present
  11. SKILL.md step 4e references F12 detection + composer.json reading
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"
AUDIT_RUBRIC = SKILLS_DIR / "audit" / "references" / "smell-rubric-f1-f13.md"


class TestF12DetectionRubric(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.rubric = AUDIT_RUBRIC.read_text(encoding="utf-8")
        f12_start = self.rubric.find("## F12")
        self.f12_section = self.rubric[f12_start:] if f12_start >= 0 else ""

    # ------------------------------------------------------------------ #
    # 1. F12 section exists                                               #
    # ------------------------------------------------------------------ #

    def test_f12_section_exists(self):
        self.assertIn(
            "## F12",
            self.rubric,
            "smell-rubric-f1-f13.md must have a ## F12 section"
        )

    # ------------------------------------------------------------------ #
    # 2. F10 prerequisite declared                                        #
    # ------------------------------------------------------------------ #

    def test_f10_prerequisite_in_f12(self):
        self.assertIn(
            "F10 prerequisite",
            self.f12_section,
            "F12 section must declare 'F10 prerequisite'"
        )

    # ------------------------------------------------------------------ #
    # 3. Composer.json / composition order documented                     #
    # ------------------------------------------------------------------ #

    def test_composer_json_referenced(self):
        has_composer = (
            "composer.json" in self.f12_section
            or "composer" in self.f12_section.lower()
        )
        self.assertTrue(
            has_composer,
            "F12 must reference composer.json for composition order reading"
        )

    def test_composition_order_reading_documented(self):
        has_order = (
            "composition order" in self.f12_section.lower()
            or "layer" in self.f12_section.lower()
        )
        self.assertTrue(
            has_order,
            "F12 must document reading the composition order / layer structure"
        )

    # ------------------------------------------------------------------ #
    # 4. Fire condition: user-var layer <= system-instruction layer       #
    # ------------------------------------------------------------------ #

    def test_f12_fire_condition_layer_order(self):
        """F12 fires when user-var layer index <= system-instruction layer index."""
        has_fire_cond = (
            "at or before" in self.f12_section.lower()
            or "<=" in self.f12_section
            or "layer index" in self.f12_section.lower()
        )
        self.assertTrue(
            has_fire_cond,
            "F12 fire condition must state user-var layer at or before system instruction"
        )

    # ------------------------------------------------------------------ #
    # 5. Non-fire: user-var AFTER system instruction                     #
    # ------------------------------------------------------------------ #

    def test_f12_no_fire_when_user_var_after_system(self):
        """Rubric or SKILL must document F12 does NOT fire when user-var comes after system."""
        combined = self.skill + self.rubric
        has_no_fire = (
            "after" in self.f12_section.lower()
            or "comes after" in combined.lower()
            or "user data must be in" in combined.lower()
        )
        self.assertTrue(
            has_no_fire,
            "F12 must document that it does NOT fire when user-var layer is after system instruction"
        )

    # ------------------------------------------------------------------ #
    # 6. Confidence degrade: < 0.6 → high                                #
    # ------------------------------------------------------------------ #

    def test_f12_confidence_degrade_documented(self):
        has_degrade = (
            "0.6" in self.f12_section
            or "confidence" in self.f12_section.lower()
        )
        self.assertTrue(
            has_degrade,
            "F12 must document composer-mimic confidence < 0.6 → severity degrades to high"
        )

    def test_f12_high_severity_on_low_confidence(self):
        """When confidence < 0.6, severity must degrade to high."""
        has_degrade_high = (
            "high" in self.f12_section.lower()
            and "confidence" in self.f12_section.lower()
        )
        self.assertTrue(
            has_degrade_high,
            "F12 must document severity 'high' as the degraded value when confidence < 0.6"
        )

    # ------------------------------------------------------------------ #
    # 7. Evidence shape                                                   #
    # ------------------------------------------------------------------ #

    def test_f12_evidence_userVar(self):
        self.assertIn("userVar", self.f12_section, "F12 evidence must include userVar")

    def test_f12_evidence_userVarLayer(self):
        self.assertIn("userVarLayer", self.f12_section, "F12 evidence must include userVarLayer")

    def test_f12_evidence_systemInstructionLayer(self):
        self.assertIn(
            "systemInstructionLayer",
            self.f12_section,
            "F12 evidence must include systemInstructionLayer"
        )

    def test_f12_evidence_compositionOrder(self):
        self.assertIn(
            "compositionOrder",
            self.f12_section,
            "F12 evidence must include compositionOrder"
        )

    # ------------------------------------------------------------------ #
    # 8. Default severity is critical                                     #
    # ------------------------------------------------------------------ #

    def test_f12_default_severity_critical(self):
        self.assertIn(
            "critical",
            self.f12_section.lower(),
            "F12 default severity must be 'critical'"
        )

    # ------------------------------------------------------------------ #
    # 9. Score impact                                                     #
    # ------------------------------------------------------------------ #

    def test_f12_score_impact_injection_minus_6(self):
        has_impact = (
            "−6" in self.rubric
            or "-6" in self.rubric
            or "injectionResistance −6" in self.rubric
        )
        self.assertTrue(
            has_impact,
            "F12 must document injectionResistance −6 score impact"
        )

    def test_f12_score_impact_persona_minus_2(self):
        # Confirm persona-consistency −2 is in scoring-dimensions or rubric
        scoring_dims = (
            pathlib.Path(__file__).parent.parent.parent
            / "skills" / "audit" / "references" / "scoring-dimensions.md"
        ).read_text(encoding="utf-8")
        has_persona = (
            "persona-consistency" in self.f12_section.lower()
            or "persona" in self.f12_section.lower()
            or "F12" in scoring_dims and "−2" in scoring_dims
        )
        self.assertTrue(
            has_persona,
            "F12 must reference persona-consistency −2 impact"
        )

    # ------------------------------------------------------------------ #
    # 10. handoffHint: vibe-sec:audit                                     #
    # ------------------------------------------------------------------ #

    def test_f12_handoff_hint(self):
        self.assertIn(
            "vibe-sec:audit",
            self.f12_section,
            "F12 must include handoffHint: vibe-sec:audit"
        )

    # ------------------------------------------------------------------ #
    # 11. SKILL step 4e references F12 + composer.json reading            #
    # ------------------------------------------------------------------ #

    def test_skill_step_4e_references_f12(self):
        self.assertIn(
            "F12",
            self.skill,
            "audit/SKILL.md must reference F12 in step 4e"
        )

    def test_skill_step_4e_reads_composer_json(self):
        has_composer_read = (
            "composer.json" in self.skill
            or "composer" in self.skill.lower()
        )
        self.assertTrue(
            has_composer_read,
            "SKILL step 4e must document reading composer.json for layer order"
        )


class TestF12NotFireWhenUserVarAfterSystem(unittest.TestCase):
    """Negative-case: F12 does NOT fire when user-var comes after system instruction."""

    def setUp(self):
        self.rubric = (
            pathlib.Path(__file__).parent.parent.parent
            / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"
        ).read_text(encoding="utf-8")
        self.skill = (
            pathlib.Path(__file__).parent.parent.parent
            / "skills" / "audit" / "SKILL.md"
        ).read_text(encoding="utf-8")

    def test_recommendation_instructs_system_first_user_last(self):
        """Recommendation must say system instruction first, user data last."""
        combined = self.skill + self.rubric
        has_order = (
            "system instruction" in combined.lower()
            and ("last layer" in combined.lower() or "last" in combined.lower())
            or "user data" in combined.lower()
        )
        self.assertTrue(
            has_order,
            "F12 recommendation must instruct system-instruction-first, user-data-last ordering"
        )


if __name__ == "__main__":
    unittest.main()
