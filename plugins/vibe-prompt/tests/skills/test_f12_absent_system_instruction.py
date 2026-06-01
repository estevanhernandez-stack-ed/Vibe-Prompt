"""
Task 23 — TDD tests for F12 absent-system-instruction sub-case (v0.7).

Background: WeSeeYou cross-app probe surfaced the badge-icon-generator
pattern — a composer with a user-var layer in `contents` but NO
system-instruction layer at all. v0.6 F12 detection couldn't reason about
this (there's no system-instruction layer to find), so it skipped the
prompt entirely, missing the real risk: when ONLY a user-var layer exists,
there is no structural separation possible — anything the user sends IS
the entire input to the model.

v0.7 treats absent-system-instruction as a sub-case of F12:
  - Severity: high (degraded — no system instruction means no structural
    separation possible)
  - Evidence emits `apiParameterContext.absentSystemInstructionLayer: true`
    for clarity (signals to consumers that this is the degenerate composition)

Asserts:
  1. SKILL.md F12 step documents the absent-system-instruction sub-case
  2. SKILL.md says severity stays high in this sub-case
  3. SKILL.md emits `apiParameterContext.absentSystemInstructionLayer: true`
  4. rubric F12 section documents the sub-case
  5. v0.7 referenced for this addition
"""

import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent.parent
AUDIT_SKILL = ROOT / "skills" / "audit" / "SKILL.md"
RUBRIC = ROOT / "skills" / "audit" / "references" / "smell-rubric-f1-f13.md"


class TestF12AbsentSystemInstruction(unittest.TestCase):

    def setUp(self):
        self.skill = AUDIT_SKILL.read_text(encoding="utf-8")
        self.rubric = RUBRIC.read_text(encoding="utf-8")
        self.combined = self.skill + "\n" + self.rubric

    def test_absent_system_instruction_documented(self):
        """SKILL or rubric must document the absent-system-instruction sub-case."""
        lowered = self.combined.lower()
        has_subcase = (
            "absent" in lowered
            and "system" in lowered
            and "instruction" in lowered
            and ("layer" in lowered or "subcase" in lowered or "sub-case" in lowered)
        )
        self.assertTrue(
            has_subcase,
            "F12 absent-system-instruction sub-case must be documented"
        )

    def test_severity_high_in_subcase(self):
        """Severity in the absent-system-instruction sub-case must be high (degraded)."""
        # The rubric/SKILL must declare severity high explicitly for this sub-case
        lowered = self.combined.lower()
        # Look for clustered language: absent + system + instruction + high
        nearby_window = 800
        idx = lowered.find("absent")
        while idx >= 0:
            window = lowered[idx: idx + nearby_window]
            if ("system" in window) and ("instruction" in window) and ("high" in window):
                return  # pass
            idx = lowered.find("absent", idx + 1)
        self.fail("F12 absent-system-instruction sub-case must declare severity high")

    def test_emits_absent_layer_flag(self):
        """SKILL must emit absentSystemInstructionLayer: true in apiParameterContext."""
        self.assertIn(
            "absentSystemInstructionLayer",
            self.combined,
            "F12 finding must emit apiParameterContext.absentSystemInstructionLayer when applicable"
        )

    def test_v07_referenced(self):
        """SKILL/rubric must reference v0.7 for this addition."""
        self.assertIn(
            "v0.7",
            self.combined,
            "F12 absent-system-instruction sub-case must be tagged v0.7"
        )

    def test_subcase_describes_no_separation(self):
        """SKILL or rubric must explain that NO structural separation is possible without system-instruction layer."""
        lowered = self.combined.lower()
        has_explanation = (
            ("no structural separation" in lowered)
            or ("no separation" in lowered and "absent" in lowered)
            or ("only one layer" in lowered)
            or ("only user" in lowered and "layer" in lowered)
        )
        self.assertTrue(
            has_explanation,
            "F12 absent-system-instruction must explain the no-separation-possible structural reality"
        )


if __name__ == "__main__":
    unittest.main()
