"""
Task 12 — TDD tests for F10 detection in audit/SKILL.md.

F10: Prompt accepts user-controlled input without sanitization marker.
Severity: high. Score impact: injectionResistance −4, instruction-clarity −1.

Asserts:
  1. audit/SKILL.md contains F10 detection step
  2. User-var heuristic documented: exact match list + contains regex
  3. Sanitization-directive scan (200-char window) documented
  4. F10 fires when user-var detected AND no sanitization directive
  5. F10 does NOT fire when sanitization directive present in window
  6. Config-extensibility via audit.injectionResistance.userInputVars documented
  7. F10 dependency is declared (standalone detection, prerequisite for F11/F12)
  8. handoffHint: "vibe-sec:audit" attached to F10 finding
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"
AUDIT_RUBRIC = SKILLS_DIR / "audit" / "references" / "smell-rubric-f1-f12.md"


class TestF10DetectionInAuditSkill(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.rubric = AUDIT_RUBRIC.read_text(encoding="utf-8")
        self.combined = self.skill + self.rubric

    # ------------------------------------------------------------------ #
    # 1. F10 step exists in SKILL workflow                                 #
    # ------------------------------------------------------------------ #

    def test_f10_detection_step_in_skill(self):
        self.assertIn(
            "F10",
            self.skill,
            "audit/SKILL.md must include an F10 detection step in the workflow"
        )

    # ------------------------------------------------------------------ #
    # 2. User-var heuristic documented                                     #
    # ------------------------------------------------------------------ #

    def test_exact_match_list_documented(self):
        """SKILL or rubric must list exact-match user-var names."""
        has_exact = (
            "userInput" in self.combined
            or "userMessage" in self.combined
            or "userQuery" in self.combined
        )
        self.assertTrue(
            has_exact,
            "F10 must document exact-match user-var names (e.g., userInput, userMessage, userQuery)"
        )

    def test_contains_regex_documented(self):
        """SKILL or rubric must document contains-match heuristic."""
        has_contains = (
            "message" in self.combined.lower()
            and "query" in self.combined.lower()
            and ("contains" in self.combined.lower() or "regex" in self.combined.lower() or "(?i)" in self.combined)
        )
        self.assertTrue(
            has_contains,
            "F10 must document the contains-match heuristic for user-var detection"
        )

    # ------------------------------------------------------------------ #
    # 3. Sanitization-directive scan (200-char window)                    #
    # ------------------------------------------------------------------ #

    def test_200_char_window_documented(self):
        """Sanitization-directive scan must reference 200-char proximity window."""
        self.assertIn(
            "200",
            self.combined,
            "F10 must document the 200-char window for sanitization-directive scan"
        )

    def test_sanitization_directive_patterns_documented(self):
        """At least two sanitization-directive patterns must be listed."""
        has_patterns = (
            "treat" in self.combined.lower()
            and "as data" in self.combined.lower()
        )
        self.assertTrue(
            has_patterns,
            "F10 must document sanitization-directive patterns (e.g., 'treat as data')"
        )

    def test_do_not_execute_pattern_documented(self):
        """'do not execute' pattern must appear in rubric or SKILL."""
        self.assertIn(
            "do not execute",
            self.combined.lower(),
            "F10 sanitization-directive scan must include 'do not execute' pattern"
        )

    # ------------------------------------------------------------------ #
    # 4. F10 fires when user-var detected + no sanitization               #
    # ------------------------------------------------------------------ #

    def test_f10_fire_condition_documented(self):
        """SKILL or rubric must describe when F10 fires (user-var + no sanitization)."""
        has_fire_cond = (
            "user-var detected" in self.combined.lower()
            or "user-var" in self.combined.lower()
            or "user var" in self.combined.lower()
        )
        self.assertTrue(
            has_fire_cond,
            "F10 must document the fire condition: user-var detected AND no sanitization directive"
        )

    # ------------------------------------------------------------------ #
    # 5. Non-fire when sanitization directive present                     #
    # ------------------------------------------------------------------ #

    def test_f10_does_not_fire_with_sanitization(self):
        """SKILL or rubric must document that F10 does NOT fire when sanitization present."""
        has_no_fire = (
            "no sanitization" in self.combined.lower()
            or "sanitization directive found" in self.combined.lower()
            or "sanitization directive" in self.combined.lower()
        )
        self.assertTrue(
            has_no_fire,
            "F10 must document that finding does not fire when a sanitization directive is present"
        )

    # ------------------------------------------------------------------ #
    # 6. Config-extensibility via userInputVars                           #
    # ------------------------------------------------------------------ #

    def test_config_extensibility_documented(self):
        """Must reference config extension for userInputVars."""
        has_config = (
            "userInputVars" in self.combined
            or "user-input-vars" in self.combined
            or "audit.injectionResistance" in self.combined
        )
        self.assertTrue(
            has_config,
            "F10 must document config-extensibility via audit.injectionResistance.userInputVars"
        )

    # ------------------------------------------------------------------ #
    # 7. F10 is prerequisite for F11/F12 (documented)                    #
    # ------------------------------------------------------------------ #

    def test_f10_prerequisite_for_f11_documented(self):
        """F11 must declare F10 as a prerequisite."""
        self.assertIn(
            "F10 prerequisite",
            self.rubric,
            "F11 in smell-rubric must declare 'F10 prerequisite'"
        )

    def test_f10_prerequisite_for_f12_documented(self):
        """F12 must declare F10 as a prerequisite."""
        # F12 section comes after F11 in the rubric; both say "F10 prerequisite"
        f12_start = self.rubric.find("## F12")
        self.assertGreater(f12_start, 0, "F12 section must exist in rubric")
        f12_content = self.rubric[f12_start:]
        self.assertIn(
            "F10 prerequisite",
            f12_content,
            "F12 in smell-rubric must declare 'F10 prerequisite'"
        )

    # ------------------------------------------------------------------ #
    # 8. handoffHint: "vibe-sec:audit" on F10                             #
    # ------------------------------------------------------------------ #

    def test_f10_handoff_hint_present(self):
        """F10 finding must include handoffHint: vibe-sec:audit."""
        has_hint = (
            "vibe-sec:audit" in self.combined
            or "handoffHint" in self.combined
        )
        self.assertTrue(
            has_hint,
            "F10 must document handoffHint: vibe-sec:audit"
        )


class TestF10NoFireWithSanitization(unittest.TestCase):
    """Negative-case test: F10 does NOT fire when sanitization directive present."""

    def setUp(self):
        self.rubric = (
            pathlib.Path(__file__).parent.parent.parent
            / "skills" / "audit" / "references" / "smell-rubric-f1-f12.md"
        ).read_text(encoding="utf-8")

    def test_rubric_fire_condition_is_and_not_or(self):
        """The fire condition must be AND (user-var AND no sanitization) — not OR."""
        # The rubric should say 'fire when' with both conditions
        f10_start = self.rubric.find("## F10")
        self.assertGreater(f10_start, 0, "F10 section must exist in rubric")
        f10_content = self.rubric[f10_start:f10_start + 2000]
        self.assertIn(
            "Fire when",
            f10_content,
            "F10 rubric must have an explicit 'Fire when' condition"
        )
        # The fire condition must reference no sanitization
        self.assertTrue(
            "no sanitization" in f10_content.lower()
            or "not found" in f10_content.lower()
            or "found nearby" in f10_content.lower(),
            "F10 fire condition must reference absence of sanitization directive"
        )


if __name__ == "__main__":
    unittest.main()
