"""
Task 10 — TDD tests for F12 API-parameter-aware detection (v0.6).

v0.5 F12 fired on layer-order alone. v0.6 reads each layer's `apiParameter`
field first and treats apiParameter separation as structurally safe:

  - user-var layer at apiParameter "contents" (or "messages") AND
    system-instruction layer at apiParameter "systemInstruction"
    → F12 does NOT fire (structurally segregated by the API)

  - Both layers at the SAME apiParameter (e.g., both interpolated into
    one `systemInstruction:` string) → F12 fires per v0.5 layer-order rule.

  - Either layer's apiParameter === null → F12 degrades to v0.5 layer-order
    fallback with severity "high" (not "critical").

The audit finding includes an `apiParameterContext` evidence object with the
separation analysis: { userVarApiParameter, systemInstructionApiParameter,
separationVerified }.

Asserts:
  1. audit/SKILL.md F12 step references apiParameter check first
  2. SKILL documents: contents + systemInstruction → F12 does NOT fire
  3. SKILL documents: same apiParameter → fall through to v0.5 layer-order rule
  4. SKILL documents: null apiParameter → confidence-degraded high severity
  5. SKILL emits apiParameterContext in F12 evidence
  6. Rubric F12 section references apiParameter-aware behavior
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
SKILLS_DIR = ROOT / "skills"
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"
# Phase 3 renames this file; tolerate either name during build.
AUDIT_RUBRIC_F12 = SKILLS_DIR / "audit" / "references" / "smell-rubric-f1-f12.md"
AUDIT_RUBRIC_F13 = SKILLS_DIR / "audit" / "references" / "smell-rubric-f1-f13.md"


def load_rubric():
    if AUDIT_RUBRIC_F13.exists():
        return AUDIT_RUBRIC_F13.read_text(encoding="utf-8")
    return AUDIT_RUBRIC_F12.read_text(encoding="utf-8")


class TestF12ApiParameterAwareDetection(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.rubric = load_rubric()

    def test_skill_f12_references_apiparameter(self):
        """audit/SKILL.md F12 detection step must reference apiParameter."""
        # F12 step is workflow step 4e; ensure apiParameter appears in context.
        # Find F12 section in SKILL
        f12_start = self.skill.find("4e.")
        f12_section = self.skill[f12_start: f12_start + 3000] if f12_start >= 0 else self.skill
        self.assertIn(
            "apiParameter",
            f12_section,
            "audit/SKILL.md F12 step (4e) must reference apiParameter"
        )

    def test_skill_documents_structural_separation_no_fire(self):
        """SKILL must document: user-var contents + system-instruction systemInstruction → F12 does NOT fire."""
        combined = self.skill + self.rubric
        # Look for explicit "structurally segregated" / "structurally safe" / "does NOT fire"
        has_separation = (
            ("structurally" in combined.lower() and ("segregated" in combined.lower() or "safe" in combined.lower()))
            or ("does not fire" in combined.lower() and "apiParameter" in combined)
        )
        self.assertTrue(
            has_separation,
            "SKILL or rubric must document structural-separation no-fire rule"
        )

    def test_skill_documents_same_apiparameter_fallthrough(self):
        """SKILL must document same apiParameter → v0.5 layer-order rule applies."""
        combined = self.skill + self.rubric
        has_same = (
            "same apiParameter" in combined
            or "same `apiParameter`" in combined
            or ("same" in combined.lower() and "fall" in combined.lower() and "layer" in combined.lower())
        )
        self.assertTrue(
            has_same,
            "SKILL must document same-apiParameter fall-through to v0.5 layer-order rule"
        )

    def test_skill_documents_null_apiparameter_degrade(self):
        """SKILL must document apiParameter === null → severity degrades to high."""
        combined = self.skill + self.rubric
        has_null_degrade = (
            ("null" in combined.lower() and "apiParameter" in combined)
            and ("high" in combined.lower() or "degrade" in combined.lower())
        )
        self.assertTrue(
            has_null_degrade,
            "SKILL must document null apiParameter → high severity degrade"
        )

    def test_skill_emits_api_parameter_context(self):
        """F12 finding evidence must include apiParameterContext field."""
        self.assertIn(
            "apiParameterContext",
            self.skill,
            "audit/SKILL.md F12 step must emit apiParameterContext evidence"
        )

    def test_rubric_f12_references_apiparameter(self):
        """The F12 rubric section must reference apiParameter-aware detection (v0.6)."""
        f12_start = self.rubric.find("## F12")
        f12_section = self.rubric[f12_start: f12_start + 5000] if f12_start >= 0 else ""
        self.assertIn(
            "apiParameter",
            f12_section,
            "F12 rubric section must reference apiParameter detection"
        )

    def test_skill_f12_check_order_apiparameter_first(self):
        """SKILL must check apiParameter BEFORE falling back to layer order."""
        # Look for explicit ordering language
        combined = self.skill + self.rubric
        has_order = (
            "first" in combined.lower() and "apiParameter" in combined
        ) or (
            "before" in combined.lower() and "layer" in combined.lower() and "apiParameter" in combined
        )
        self.assertTrue(
            has_order,
            "SKILL must check apiParameter first before falling back to v0.5 layer-order rule"
        )


if __name__ == "__main__":
    unittest.main()
