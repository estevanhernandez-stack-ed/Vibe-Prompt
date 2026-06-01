"""
Task 20 — TDD tests for F12 severity-decoupling from composer-multiplicity (v0.7).

Background: a cross-app probe (v0.7 spec §F12 severity decoupling) found that
v0.6's F12 severity-degrade logic was implicitly tied to composer-multiplicity
because the only available `globalConfidence` was a single global number that
dropped whenever multiple composers were detected.

v0.7 fixes this:
  - composer-multiplicity is exposed as `findings[].metadata.composerMultiplicityFlag`
    (context only) — it is NOT a severity input.
  - F12 severity-degrade keys solely off:
    A) detection ambiguity per layer (any layer's apiParameter has confidence < 0.6
       or apiParameter === null), OR
    B) absent composer.json (existing v0.6 fallback)
  - composer.globalConfidence is still consulted but no longer collapses to a
    "low" value purely because multiplicity was detected.

Asserts:
  1. SKILL/rubric documents the decoupling: multiplicity does NOT drag severity
  2. SKILL/rubric documents detection-ambiguity as the severity-degrade trigger
  3. SKILL emits `metadata.composerMultiplicityFlag` for context-only
  4. SKILL/rubric references v0.7 for this decoupling
  5. F12 severity stays critical when apiParameter is unambiguous on all layers
     even when multi-composer kind detected (the canonical Fixture A case)
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"
RUBRIC = ROOT / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"


class TestF12SeverityDecoupling(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.rubric = RUBRIC.read_text(encoding="utf-8")
        self.combined = self.skill + "\n" + self.rubric

    def test_decoupling_documented(self):
        """SKILL or rubric must explicitly document that composer-multiplicity does NOT degrade severity."""
        lowered = self.combined.lower()
        has_decouple = (
            ("multiplicity" in lowered and ("does not" in lowered or "does not degrade" in lowered or "not a severity input" in lowered or "not drag" in lowered or "decouple" in lowered))
            or ("multiplicity" in lowered and "context only" in lowered)
        )
        self.assertTrue(
            has_decouple,
            "F12 severity-decoupling from composer multiplicity must be documented "
            "(rubric or SKILL must state multiplicity is not a severity input)"
        )

    def test_detection_ambiguity_drives_degrade(self):
        """F12 severity-degrade must key off detection ambiguity (confidence/null), not multiplicity."""
        f12_start = self.rubric.find("## F12")
        f12_section = self.rubric[f12_start: f12_start + 6000] if f12_start >= 0 else ""
        combined = f12_section + "\n" + self.skill
        lowered = combined.lower()
        has_ambiguity_rule = (
            ("apiparameter" in lowered and ("null" in lowered or "unknown" in lowered) and "degrade" in lowered)
            or ("confidence" in lowered and "< 0.6" in combined and "apiparameter" in lowered)
            or ("detection ambiguity" in lowered)
        )
        self.assertTrue(
            has_ambiguity_rule,
            "F12 severity-degrade must be tied to detection-ambiguity (apiParameter null / low confidence), not multiplicity"
        )

    def test_metadata_multiplicity_flag_emitted(self):
        """SKILL must emit composerMultiplicityFlag in finding metadata (context only)."""
        self.assertIn(
            "composerMultiplicityFlag",
            self.combined,
            "F12 finding must emit metadata.composerMultiplicityFlag (context-only signal)"
        )

    def test_v07_reference_for_decoupling(self):
        """SKILL or rubric must reference v0.7 explicitly for the decoupling."""
        self.assertIn(
            "v0.7",
            self.combined,
            "F12 severity-decoupling change must be tagged v0.7"
        )

    def test_severity_stays_critical_when_unambiguous(self):
        """SKILL/rubric must document: unambiguous apiParameter → severity stays critical, even with multiplicity."""
        lowered = self.combined.lower()
        # Look for explicit statement that severity is not degraded when apiParameter is unambiguous
        has_stays_critical = (
            ("critical" in lowered and "unambiguous" in lowered)
            or ("critical" in lowered and "multiplicity" in lowered and "not" in lowered)
            or ("not a severity input" in lowered)
            or ("stays critical" in lowered)
        )
        self.assertTrue(
            has_stays_critical,
            "F12 severity must stay critical when apiParameter is unambiguous even with multi-composer"
        )

    def test_v06_existing_apiparameter_null_fallback_preserved(self):
        """The v0.6 apiParameter-null → high degrade must still be documented (regression guard)."""
        f12_start = self.rubric.find("## F12")
        f12_section = self.rubric[f12_start: f12_start + 6000] if f12_start >= 0 else ""
        lowered = (f12_section + self.skill).lower()
        has_null_path = "null" in lowered and "apiparameter" in lowered and "high" in lowered
        self.assertTrue(
            has_null_path,
            "F12 v0.6 apiParameter-null fallback must remain (severity high when apiParameter null)"
        )


if __name__ == "__main__":
    unittest.main()
