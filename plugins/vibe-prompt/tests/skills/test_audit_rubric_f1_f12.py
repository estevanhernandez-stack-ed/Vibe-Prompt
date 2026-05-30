"""
Task 6 — TDD tests for audit rubric rename + F9 addition.

Asserts:
  1. File smell-rubric-f1-f13.md exists
  2. File smell-rubric-f1-f7.md does NOT exist
  3. File contains section ## F9 — Date-handling prompt without temporal grounding
  4. File contains section ## F10 — Prompt accepts user-controlled input without sanitization marker
  5. File contains section ## F11 — Prompt has insufficient defense-in-depth directives
  6. File contains section ## F12 — User-controlled var appears at or before system instruction
"""

import pathlib
import unittest

REFERENCES_DIR = (
    pathlib.Path(__file__).parent.parent.parent
    / "skills" / "audit" / "references"
)

OLD_RUBRIC = REFERENCES_DIR / "smell-rubric-f1-f7.md"
NEW_RUBRIC = REFERENCES_DIR / "smell-rubric-f1-f13.md"


class TestAuditRubricRename(unittest.TestCase):

    def test_new_rubric_exists(self):
        self.assertTrue(
            NEW_RUBRIC.exists(),
            f"Expected {NEW_RUBRIC} to exist — run 'git mv' and extend"
        )

    def test_old_rubric_does_not_exist(self):
        self.assertFalse(
            OLD_RUBRIC.exists(),
            f"Old rubric {OLD_RUBRIC} still exists — remove it with 'git mv'"
        )

    def _load_content(self):
        return NEW_RUBRIC.read_text(encoding="utf-8")

    def test_f9_section_present(self):
        content = self._load_content()
        self.assertIn(
            "## F9 — Date-handling prompt without temporal grounding",
            content,
            "F9 section missing from smell-rubric-f1-f13.md"
        )

    def test_f10_section_present(self):
        content = self._load_content()
        self.assertIn(
            "## F10 — Prompt accepts user-controlled input without sanitization marker",
            content,
            "F10 section missing from smell-rubric-f1-f13.md"
        )

    def test_f11_section_present(self):
        content = self._load_content()
        self.assertIn(
            "## F11 — Prompt has insufficient defense-in-depth directives",
            content,
            "F11 section missing from smell-rubric-f1-f13.md"
        )

    def test_f12_section_present(self):
        content = self._load_content()
        self.assertIn(
            "## F12 — User-controlled var appears at or before system instruction",
            content,
            "F12 section missing from smell-rubric-f1-f13.md"
        )

    def test_f9_has_severity_high(self):
        content = self._load_content()
        # Find the F9 section and check it declares high severity
        idx = content.find("## F9 —")
        self.assertGreater(idx, -1, "F9 section missing")
        # Grab 500 chars after the section header
        excerpt = content[idx : idx + 500]
        self.assertIn("high", excerpt.lower(), "F9 should declare high severity")

    def test_f9_score_impact_instruction_clarity(self):
        content = self._load_content()
        idx = content.find("## F9 —")
        self.assertGreater(idx, -1)
        # Find next section boundary so we stay in F9
        next_section = content.find("## F10", idx)
        f9_section = content[idx:next_section] if next_section > -1 else content[idx:]
        self.assertIn(
            "instruction-clarity",
            f9_section,
            "F9 section should declare instruction-clarity score impact"
        )
        self.assertIn(
            "schema-tightness",
            f9_section,
            "F9 section should declare schema-tightness score impact"
        )

    def test_existing_f1_through_f7_still_present(self):
        """Rename must not drop existing F1-F7 content."""
        content = self._load_content()
        for fid in ["F1 —", "F2 —", "F3 —", "F4 —", "F5 —", "F6 —", "F7 —"]:
            self.assertIn(fid, content, f"Existing finding {fid} missing after rename")


if __name__ == "__main__":
    unittest.main()
