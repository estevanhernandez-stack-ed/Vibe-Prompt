r"""
Task 10 — TDD tests for var-origin Signal 1 (naming heuristic).

Asserts:
  1. scan/references/var-origin-detection.md exists
  2. User-keyword regex documented (matches dreamText, userMessage, etc.)
  3. System-keyword regex documented (matches knowledgeContext, etc.)
  4. Confidence ≥0.85 for clear-match cases declared
  5. Confidence ≤0.50 for no-signal cases declared (e.g., `prompt`)
  6. Conflict (both lists match) → fall through to Signal 2 documented
  7. Result writes to inventory `templatedVars[].origin` + `originConfidence`
  8. scan/SKILL.md references var-origin-detection.md in workflow
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCAN_SKILL = SKILLS_DIR / "scan" / "SKILL.md"
VAR_ORIGIN_REF = SKILLS_DIR / "scan" / "references" / "var-origin-detection.md"


class TestVarOriginSignal1Documentation(unittest.TestCase):

    def setUp(self):
        self.skill = SCAN_SKILL.read_text(encoding="utf-8")
        self.ref = (
            VAR_ORIGIN_REF.read_text(encoding="utf-8")
            if VAR_ORIGIN_REF.exists()
            else ""
        )

    def test_var_origin_reference_exists(self):
        self.assertTrue(
            VAR_ORIGIN_REF.exists(),
            "scan/references/var-origin-detection.md must exist",
        )

    def test_signal_1_documented(self):
        self.assertIn(
            "Signal 1",
            self.ref,
            "var-origin-detection.md must declare Signal 1",
        )

    def test_user_keyword_regex_documented(self):
        """User-keyword regex must list user-controlled var name patterns."""
        # Per spec §3 Signal 1: user|input|message|query|text|content|bio|description|question|dream|note|comment|review|feedback|reply|chat
        ref_lower = self.ref.lower()
        user_keys = ["user", "input", "message", "query", "dream", "bio"]
        missing = [k for k in user_keys if k not in ref_lower]
        self.assertEqual(
            missing,
            [],
            f"User-keyword list must include: {missing} (spec §3 Signal 1)",
        )

    def test_system_keyword_regex_documented(self):
        """System-keyword regex must list system-injected var name patterns."""
        # Per spec §3 Signal 1: knowledge|context|system|service|injected|cached|preloaded|fetched|loaded|enriched|computed
        ref_lower = self.ref.lower()
        sys_keys = ["knowledge", "context", "system", "service", "injected", "fetched"]
        missing = [k for k in sys_keys if k not in ref_lower]
        self.assertEqual(
            missing,
            [],
            f"System-keyword list must include: {missing} (spec §3 Signal 1)",
        )

    def test_high_confidence_for_clear_match_declared(self):
        """Clear match (only one list hits) → confidence ≥0.85."""
        # Look for 0.85 or higher reference
        has_high = (
            "0.85" in self.ref
            or "0.9" in self.ref
            or "high confidence" in self.ref.lower()
        )
        self.assertTrue(
            has_high,
            "Confidence ≥0.85 for clear naming-match must be declared",
        )

    def test_low_confidence_for_no_signal_declared(self):
        """No signal (e.g., `prompt`) → confidence ≤0.50."""
        # Look for 0.5 or lower
        has_low = (
            "0.5" in self.ref
            or "0.4" in self.ref
            or "0.50" in self.ref
            or "low confidence" in self.ref.lower()
        )
        self.assertTrue(
            has_low,
            "Confidence ≤0.50 for no-signal cases must be declared",
        )

    def test_conflict_falls_through_to_signal_2(self):
        """Both lists match (e.g., 'userContext') → defer to Signal 2."""
        ref_lower = self.ref.lower()
        has_fallthrough = (
            ("conflict" in ref_lower or "both" in ref_lower or "ambiguous" in ref_lower)
            and "signal 2" in ref_lower
        )
        self.assertTrue(
            has_fallthrough,
            "Conflict (both lists match) must fall through to Signal 2",
        )

    def test_writes_to_inventory_origin_field(self):
        """Output writes to inventory templatedVars[].origin + originConfidence."""
        has_origin = (
            "origin" in self.ref
            and ("templatedVars" in self.ref or "inventory" in self.ref.lower())
        )
        self.assertTrue(
            has_origin,
            "Reference must declare output writes to templatedVars[].origin",
        )

    def test_skill_references_var_origin_detection(self):
        self.assertIn(
            "var-origin-detection",
            self.skill,
            "scan/SKILL.md must reference var-origin-detection.md",
        )

    def test_classification_enum_documented(self):
        """The origin enum: user-controlled | system-injected | unknown."""
        for value in ("user-controlled", "system-injected", "unknown"):
            self.assertIn(
                value,
                self.ref,
                f"var-origin-detection.md must document origin enum value '{value}'",
            )


if __name__ == "__main__":
    unittest.main()
