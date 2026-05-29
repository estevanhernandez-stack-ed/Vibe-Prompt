"""
Task 13 — TDD tests for F11 detection in audit/SKILL.md + smell-rubric-f1-f12.md.

F11: Prompt has insufficient defense-in-depth directives.
Severity: medium. Score impact: injectionResistance −2.
Prerequisite: F10 must have fired on the same prompt.

Asserts:
  1. F11 section exists in rubric
  2. F10 prerequisite declared explicitly
  3. Defense-phrase list embedded in rubric (not just a reference to inject-attack-fixtures.md)
  4. All 6 canonical defense phrases present in rubric
  5. Fire condition: F10 fired AND defense-phrase count < 2
  6. Non-fire condition: 2+ defense phrases present (should NOT fire)
  7. Evidence includes detectedDefensePhrases and recommendedDefensePhrases
  8. Severity is medium
  9. Score impact injectionResistance −2 documented
  10. SKILL.md step 4d references F11 detection
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"
AUDIT_RUBRIC = SKILLS_DIR / "audit" / "references" / "smell-rubric-f1-f12.md"

CANONICAL_DEFENSE_PHRASES = [
    "treat as data",
    "ignore instructions within",
    "your role is fixed",
    "do not execute commands",
    "regardless of user request",
    "always remain",
]


class TestF11DetectionRubric(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.rubric = AUDIT_RUBRIC.read_text(encoding="utf-8")
        # Isolate the F11 section of the rubric
        f11_start = self.rubric.find("## F11")
        f12_start = self.rubric.find("## F12")
        self.f11_section = (
            self.rubric[f11_start:f12_start]
            if f12_start > f11_start
            else self.rubric[f11_start:]
        )

    # ------------------------------------------------------------------ #
    # 1. F11 section exists in rubric                                     #
    # ------------------------------------------------------------------ #

    def test_f11_section_exists(self):
        self.assertIn(
            "## F11",
            self.rubric,
            "smell-rubric-f1-f12.md must have a ## F11 section"
        )

    # ------------------------------------------------------------------ #
    # 2. F10 prerequisite explicitly declared                             #
    # ------------------------------------------------------------------ #

    def test_f10_prerequisite_declared(self):
        self.assertIn(
            "F10 prerequisite",
            self.f11_section,
            "F11 section must explicitly declare 'F10 prerequisite'"
        )

    # ------------------------------------------------------------------ #
    # 3. Defense-phrase list embedded in rubric                           #
    # ------------------------------------------------------------------ #

    def test_defense_phrase_list_embedded_in_rubric(self):
        """All 6 canonical defense phrases must appear in the rubric itself — not just referenced."""
        for phrase in CANONICAL_DEFENSE_PHRASES:
            self.assertIn(
                phrase,
                self.rubric,
                f"Canonical defense phrase '{phrase}' must be embedded in the rubric (not just referenced)"
            )

    # ------------------------------------------------------------------ #
    # 4-6. Fire condition and non-fire condition                          #
    # ------------------------------------------------------------------ #

    def test_f11_fire_condition_less_than_2_phrases(self):
        """F11 fire condition must reference count < 2."""
        has_count = (
            "< 2" in self.f11_section
            or "fewer than 2" in self.f11_section.lower()
            or "count < 2" in self.f11_section.lower()
        )
        self.assertTrue(
            has_count,
            "F11 fire condition must state defense-phrase count < 2"
        )

    def test_f11_fire_requires_f10_to_have_fired(self):
        """F11 must only fire when F10 detected a user-var (prerequisite)."""
        has_prereq = (
            "F10 detected" in self.f11_section
            or "F10 prerequisite" in self.f11_section
            or "user-var" in self.f11_section.lower()
        )
        self.assertTrue(
            has_prereq,
            "F11 fire condition must depend on F10 having detected a user-var"
        )

    def test_f11_no_fire_documented_when_2_phrases_present(self):
        """Rubric or SKILL must document that F11 does NOT fire when 2+ phrases present."""
        combined = self.skill + self.rubric
        has_no_fire = (
            "2+ defense" in combined.lower()
            or "at least 2" in combined.lower()
            or "two defense" in combined.lower()
            or "2 defense phrase" in combined.lower()
            or "defense-in-depth requires at least" in combined.lower()
        )
        self.assertTrue(
            has_no_fire,
            "Must document that F11 does NOT fire when 2+ defense phrases present"
        )

    # ------------------------------------------------------------------ #
    # 7. Evidence shape                                                   #
    # ------------------------------------------------------------------ #

    def test_f11_evidence_detected_phrases(self):
        self.assertIn(
            "detectedDefensePhrases",
            self.rubric,
            "F11 evidence must include detectedDefensePhrases"
        )

    def test_f11_evidence_recommended_phrases(self):
        self.assertIn(
            "recommendedDefensePhrases",
            self.rubric,
            "F11 evidence must include recommendedDefensePhrases"
        )

    # ------------------------------------------------------------------ #
    # 8. Severity is medium                                               #
    # ------------------------------------------------------------------ #

    def test_f11_severity_is_medium(self):
        self.assertIn(
            "medium",
            self.f11_section.lower(),
            "F11 severity must be 'medium'"
        )

    # ------------------------------------------------------------------ #
    # 9. Score impact documented                                          #
    # ------------------------------------------------------------------ #

    def test_f11_score_impact_injection_minus_2(self):
        has_impact = (
            "−2" in self.f11_section
            or "-2" in self.f11_section
            or "injectionResistance −2" in self.rubric
            or "injectionResistance -2" in self.rubric
        )
        self.assertTrue(
            has_impact,
            "F11 must document injectionResistance −2 score impact"
        )

    # ------------------------------------------------------------------ #
    # 10. SKILL.md step 4d references F11 detection                      #
    # ------------------------------------------------------------------ #

    def test_skill_step_4d_references_f11(self):
        self.assertIn(
            "F11",
            self.skill,
            "audit/SKILL.md must reference F11 detection (step 4d)"
        )

    def test_skill_defense_phrase_scan_in_step_4d(self):
        """SKILL step 4d must reference defense-phrase scan."""
        has_phrase_scan = (
            "defense-phrase scan" in self.skill.lower()
            or "defense phrase" in self.skill.lower()
        )
        self.assertTrue(
            has_phrase_scan,
            "SKILL step 4d must describe defense-phrase scan for F11 detection"
        )


class TestF11NotFireWhenTwoPhrasesPresent(unittest.TestCase):
    """Verify that rubric logic covers the non-fire case."""

    def setUp(self):
        self.rubric = (
            pathlib.Path(__file__).parent.parent.parent
            / "skills" / "audit" / "references" / "smell-rubric-f1-f12.md"
        ).read_text(encoding="utf-8")

    def test_minimum_2_phrases_threshold(self):
        """The rubric or the combined SKILL must document the threshold of 2 phrases."""
        # The fire condition is count < 2, meaning count >= 2 → no fire
        # At least one place must state this threshold
        has_threshold = (
            "count < 2" in self.rubric
            or "< 2" in self.rubric
            or "fewer than 2" in self.rubric.lower()
            or "at least two" in self.rubric.lower()
        )
        self.assertTrue(
            has_threshold,
            "Rubric must state the threshold (count < 2 → fire; count >= 2 → no fire)"
        )


if __name__ == "__main__":
    unittest.main()
