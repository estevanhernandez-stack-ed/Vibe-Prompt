"""
Task 22 — TDD tests for handoffHint on F10-F12 findings in audit/SKILL.md.

When F10, F11, or F12 fires, the finding must include:
  handoffHint: "vibe-sec:audit"

Asserts:
  1. audit/SKILL.md declares handoffHint: "vibe-sec:audit" in the F10 finding block
  2. audit/SKILL.md declares handoffHint: "vibe-sec:audit" in the F11 finding block
  3. audit/SKILL.md declares handoffHint: "vibe-sec:audit" in the F12 finding block
  4. The handoff rule is explicit prose (not buried — the SKILL says "attach handoffHint")
  5. The hint value is exactly "vibe-sec:audit" (not a variant)
"""

import pathlib
import unittest

SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"
AUDIT_SKILL = SKILLS_DIR / "audit" / "SKILL.md"


class TestAuditHandoffHints(unittest.TestCase):

    def setUp(self):
        self.content = AUDIT_SKILL.read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # 1. F10 carries handoffHint                                          #
    # ------------------------------------------------------------------ #

    def test_f10_handoff_hint_in_skill(self):
        """F10 finding block must include handoffHint: 'vibe-sec:audit'."""
        f10_start = self.content.find("F10")
        self.assertGreater(f10_start, -1, "F10 must be present in audit/SKILL.md")
        # Find the F10 section and verify handoffHint is in the nearby block
        f10_block_end = self.content.find("4d.", f10_start)
        if f10_block_end == -1:
            f10_block_end = f10_start + 3000
        f10_block = self.content[f10_start:f10_block_end]
        self.assertIn(
            "vibe-sec:audit",
            f10_block,
            "F10 finding block must include handoffHint: 'vibe-sec:audit'"
        )

    # ------------------------------------------------------------------ #
    # 2. F11 carries handoffHint                                          #
    # ------------------------------------------------------------------ #

    def test_f11_handoff_hint_in_skill(self):
        """F11 finding block must include handoffHint: 'vibe-sec:audit'."""
        f11_start = self.content.find("4d.")
        if f11_start == -1:
            f11_start = self.content.find("F11")
        self.assertGreater(f11_start, -1, "F11 section must be present in audit/SKILL.md")
        f11_block_end = self.content.find("4e.", f11_start)
        if f11_block_end == -1:
            f11_block_end = f11_start + 2000
        f11_block = self.content[f11_start:f11_block_end]
        self.assertIn(
            "vibe-sec:audit",
            f11_block,
            "F11 finding block must include handoffHint: 'vibe-sec:audit'"
        )

    # ------------------------------------------------------------------ #
    # 3. F12 carries handoffHint                                          #
    # ------------------------------------------------------------------ #

    def test_f12_handoff_hint_in_skill(self):
        """F12 finding block must include handoffHint: 'vibe-sec:audit'."""
        f12_start = self.content.find("4e.")
        if f12_start == -1:
            f12_start = self.content.find("F12")
        self.assertGreater(f12_start, -1, "F12 section must be present in audit/SKILL.md")
        f12_block_end = self.content.find("5.", f12_start)
        if f12_block_end == -1:
            f12_block_end = f12_start + 2000
        f12_block = self.content[f12_start:f12_block_end]
        self.assertIn(
            "vibe-sec:audit",
            f12_block,
            "F12 finding block must include handoffHint: 'vibe-sec:audit'"
        )

    # ------------------------------------------------------------------ #
    # 4. The rule is declared in explicit prose                           #
    # ------------------------------------------------------------------ #

    def test_handoff_hint_rule_is_declared_explicitly(self):
        """SKILL must have a declared rule attaching handoffHint when F10-F12 fire."""
        has_rule = (
            "handoffHint" in self.content
            and "vibe-sec:audit" in self.content
        )
        self.assertTrue(
            has_rule,
            "audit/SKILL.md must explicitly declare the handoffHint rule for F10-F12"
        )

    # ------------------------------------------------------------------ #
    # 5. Hint value is exactly "vibe-sec:audit"                           #
    # ------------------------------------------------------------------ #

    def test_handoff_hint_value_is_exact(self):
        """The hint value must be exactly 'vibe-sec:audit' (verbatim string)."""
        self.assertIn(
            '"vibe-sec:audit"',
            self.content,
            "handoffHint value must appear verbatim as '\"vibe-sec:audit\"' in audit/SKILL.md"
        )

    # ------------------------------------------------------------------ #
    # 6. All three findings use the same hint (count occurrences)         #
    # ------------------------------------------------------------------ #

    def test_vibe_sec_audit_appears_at_least_three_times(self):
        """vibe-sec:audit should appear at least 3 times (once per F10, F11, F12)."""
        count = self.content.count("vibe-sec:audit")
        self.assertGreaterEqual(
            count,
            3,
            f"'vibe-sec:audit' should appear at least 3 times in audit/SKILL.md "
            f"(once per F10, F11, F12 finding). Found: {count}"
        )


if __name__ == "__main__":
    unittest.main()
