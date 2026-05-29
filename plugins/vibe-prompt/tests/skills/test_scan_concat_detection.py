r"""
Task 7 — TDD tests for string-concat var detection in scan/SKILL.md.

Pattern: `'... ' + userVar + ' ...'`
Capture: name, source: 'concat', declaredAt.

Asserts:
  1. inline-prompt-detection.md declares the concat pattern
  2. source value 'concat' is documented
  3. The pattern shows a `+ var +` chain example
  4. The detection is scoped to prompt-shaped concat chains (false-positive guard)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
SCAN_SKILL = SKILLS_DIR / "scan" / "SKILL.md"
INLINE_PROMPT_REF = SKILLS_DIR / "scan" / "references" / "inline-prompt-detection.md"


class TestScanConcatDetection(unittest.TestCase):

    def setUp(self):
        self.skill = SCAN_SKILL.read_text(encoding="utf-8")
        self.ref = INLINE_PROMPT_REF.read_text(encoding="utf-8")
        self.combined = self.skill + "\n" + self.ref

    def test_concat_source_value_declared(self):
        self.assertIn(
            "concat",
            self.ref,
            "inline-prompt-detection.md must declare source value 'concat'",
        )

    def test_concat_pattern_example_present(self):
        """Example must show a `+ var +` style chain."""
        # Strip backticks/code formatting and check for + var + pattern
        has_chain = (
            "+ userMessage +" in self.ref
            or "' + " in self.ref
            or "+ user" in self.ref
        )
        self.assertTrue(
            has_chain,
            "inline-prompt-detection.md must show a `+ var +` example",
        )

    def test_concat_scoped_to_prompts(self):
        """Detection must be scoped to prompt-shaped content (false-positive guard)."""
        # The reference must note the scope constraint
        ref_lower = self.ref.lower()
        has_scope = (
            "prompt" in ref_lower
            and ("conservative" in ref_lower or "scope" in ref_lower or "false-positive" in ref_lower)
        )
        self.assertTrue(
            has_scope,
            "concat detection must document scope/false-positive guard",
        )

    def test_skill_workflow_mentions_concat_pattern(self):
        """SKILL.md workflow must mention concat as one of the captured patterns."""
        self.assertIn(
            "concat",
            self.skill,
            "scan/SKILL.md workflow must reference concat detection",
        )


if __name__ == "__main__":
    unittest.main()
